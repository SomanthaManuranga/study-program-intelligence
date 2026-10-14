"""Fetch tables and table lists from the Destatis GENESIS-Online REST API.

Run from the repository root (token in .env as GENESIS_TOKEN):

    python -m study_program_intelligence.ingest.genesis catalogue "21311*"
    python -m study_program_intelligence.ingest.genesis catalogue "21321*"
    python -m study_program_intelligence.ingest.genesis tables
    python -m study_program_intelligence.ingest.genesis tables --only 21311-0015 --force

API facts (GENESIS Webservice documentation v5.1, June 2026):
- base URL https://genesis.destatis.de/genesisWS/rest/2020/
- POST only; credentials in the HTTP headers "username" and "password";
  an API token goes in "username" with an empty password.
- token logins cannot start background jobs (job=true).

This script never prints or stores the token. GENESIS echoes the token in a
"Username" field of some replies, so that field is removed before anything
is printed or saved.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml

from .documents import load_env

BASE_URL = "https://genesis.destatis.de/genesisWS/rest/2020/"
REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG = REPO_ROOT / "configs" / "genesis_tables.yaml"
OUT_DIR = REPO_ROOT / "data" / "raw" / "destatis"
MANIFEST = REPO_ROOT / "docs" / "genesis_manifest.json"
TIMEOUT_SECONDS = 600
DELAY_SECONDS = 2


class GenesisError(RuntimeError):
    pass


def _headers() -> dict[str, str]:
    load_env(REPO_ROOT / ".env")
    token = os.environ.get("GENESIS_TOKEN", "").strip()
    if not token:
        raise GenesisError("GENESIS_TOKEN missing in .env")
    return {
        "username": token,
        "password": "",
        "Content-Type": "application/x-www-form-urlencoded",
    }


def _scrub(obj):
    """Remove fields that may contain credentials before printing or saving."""
    if isinstance(obj, dict):
        return {k: _scrub(v) for k, v in obj.items() if k.lower() not in {"username", "password"}}
    if isinstance(obj, list):
        return [_scrub(v) for v in obj]
    return obj


def _post(method: str, data: dict) -> requests.Response:
    resp = requests.post(BASE_URL + method, headers=_headers(), data=data, timeout=TIMEOUT_SECONDS)
    if resp.status_code != 200:
        raise GenesisError(f"{method}: HTTP {resp.status_code}")
    return resp


def _status_message(resp: requests.Response) -> str | None:
    """Return the GENESIS status text if the reply is a JSON status instead of data."""
    if "json" not in resp.headers.get("Content-Type", "") and not resp.content[:1] == b"{":
        return None
    try:
        payload = _scrub(resp.json())
    except ValueError:
        return None
    status = payload.get("Status") if isinstance(payload, dict) else None
    if isinstance(status, dict):
        return f"{status.get('Code')}: {status.get('Content')}"
    return json.dumps(payload, ensure_ascii=False)[:500]


# ---------------------------------------------------------------- catalogue

def catalogue(selection: str) -> list[dict]:
    resp = _post(
        "catalogue/tables",
        {"selection": selection, "area": "all", "pagelength": "2500", "language": "de"},
    )
    payload = _scrub(resp.json())
    items = payload.get("List") or []
    if not items:
        raise GenesisError(f"no tables found: {_status_message(resp)}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    safe = selection.replace("*", "x")
    (OUT_DIR / f"catalogue_{safe}.json").write_text(
        json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    for it in items:
        print(f"{it.get('Code', ''):<12} | {it.get('Time', ''):<40} | {it.get('Content', '')}")
    print(f"\n{len(items)} tables. Saved to data/raw/destatis/catalogue_{safe}.json")
    return items


# ---------------------------------------------------------------- tables

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _extract(content: bytes) -> bytes:
    """GENESIS may return a zip archive; return the CSV bytes either way."""
    if content[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            return zf.read(names[0])
    return content


def _too_large(message: str) -> bool:
    return message.startswith("98:") or "zu gross" in message or "too large" in message.lower()


def _fetch_range(name: str, params: dict, start: int, end: int, log: list) -> list[bytes]:
    """Fetch years start..end; halve the range whenever GENESIS says it is too large."""
    request = {"name": name, "area": "all", "format": "ffcsv", "compress": "false", "language": "de",
               "startyear": str(start), "endyear": str(end)}
    request.update({k: str(v) for k, v in params.items()})
    resp = _post("data/tablefile", request)
    message = _status_message(resp)
    if message is None:
        log.append({"years": f"{start}-{end}", "status": "ok"})
        print(f"      {name} {start}-{end}: ok")
        time.sleep(DELAY_SECONDS)
        return [_extract(resp.content)]
    if _too_large(message) and start < end:
        mid = (start + end) // 2
        print(f"      {name} {start}-{end}: too large, splitting")
        time.sleep(DELAY_SECONDS)
        return _fetch_range(name, params, start, mid, log) + _fetch_range(name, params, mid + 1, end, log)
    log.append({"years": f"{start}-{end}", "status": "error", "error": message})
    raise GenesisError(f"{start}-{end}: {message}")


def _merge(parts: list[bytes]) -> bytes:
    """Concatenate flat CSV parts, keeping one header and dropping duplicate lines."""
    header, seen, lines = None, set(), []
    for part in parts:
        text = part.decode("utf-8-sig")
        rows = text.splitlines()
        if not rows:
            continue
        if header is None:
            header = rows[0]
        for row in rows[1:]:
            if row and row not in seen:
                seen.add(row)
                lines.append(row)
    return ("\n".join([header or ""] + lines) + "\n").encode("utf-8")


def _periods(data: bytes) -> list[str]:
    rows = data.decode("utf-8").splitlines()
    if len(rows) < 2:
        return []
    idx = rows[0].split(";").index("time")
    return sorted({r.split(";")[idx] for r in rows[1:] if r})


def fetch_table(spec: dict, force: bool) -> dict:
    name = spec["name"]
    tid = spec.get("id", name)
    dest = OUT_DIR / f"{tid}.csv"
    params = spec.get("params") or {}
    start, end = int(spec.get("startyear", 2005)), int(spec.get("endyear", datetime.now().year))
    record = {"id": tid, "name": name, "file": dest.relative_to(REPO_ROOT).as_posix(),
              "format": "ffcsv", "params": params, "years_requested": f"{start}-{end}"}

    if dest.exists() and not force:
        data = dest.read_bytes()
        record.update(status="cached", bytes=len(data), sha256=_sha256(data))
        return record

    log: list = []
    try:
        parts = _fetch_range(name, params, start, end, log)
    except GenesisError as exc:
        record.update(status="error", error=str(exc), requests=log)
        return record

    data = _merge(parts)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    periods = _periods(data)
    record.update(
        status="downloaded",
        retrieved_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        bytes=len(data),
        rows=data.count(b"\n") - 1,
        periods=len(periods),
        first_period=periods[0] if periods else None,
        last_period=periods[-1] if periods else None,
        requests=log,
        sha256=_sha256(data),
    )
    return record


def tables(only: list[str] | None, force: bool) -> int:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["tables"]
    if only:
        cfg = [t for t in cfg if t.get("id", t["name"]) in set(only)]

    previous = {}
    if MANIFEST.exists():
        previous = {r.get("id", r.get("name")): r for r in json.loads(MANIFEST.read_text(encoding="utf-8"))}

    results = []
    for t in cfg:
        tid = t.get("id", t["name"])
        print(f"{tid} ...")
        try:
            rec = fetch_table(t, force)
        except (GenesisError, requests.RequestException) as exc:
            rec = {"id": tid, "name": t["name"], "status": "error", "error": str(exc)}
        if rec["status"] == "cached" and tid in previous:
            rec = {**previous[tid], "status": "cached"}
        rec["title"] = t.get("title")
        results.append(rec)
        size = f"{rec['bytes'] / 1024:,.0f} KB" if rec.get("bytes") else ""
        span = f"{rec.get('first_period')} to {rec.get('last_period')} ({rec.get('periods')} periods)" if rec.get("periods") else ""
        print(f"[{rec['status']:>10}] {tid:<16} {size:>10}  {span} {rec.get('error', '')}")

    all_ids = {t.get("id", t["name"]) for t in yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["tables"]}
    kept = {k: v for k, v in previous.items() if k in all_ids}  # drop entries no longer configured
    merged = {**kept, **{r["id"]: r for r in results}}
    MANIFEST.write_text(json.dumps(list(merged.values()), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\nManifest written to docs/genesis_manifest.json")
    return 1 if any(r["status"] == "error" for r in results) else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Destatis GENESIS-Online client")
    sub = parser.add_subparsers(dest="command", required=True)
    c = sub.add_parser("catalogue", help="list tables matching a code pattern, e.g. 21311*")
    c.add_argument("selection")
    t = sub.add_parser("tables", help="download the tables in configs/genesis_tables.yaml")
    t.add_argument("--only", nargs="*", default=None)
    t.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.command == "catalogue":
            catalogue(args.selection)
            return 0
        return tables(args.only, args.force)
    except (GenesisError, requests.RequestException) as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
