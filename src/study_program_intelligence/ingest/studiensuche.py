"""Harvest programme listings from the Bundesagentur fuer Arbeit study search
(Studiensuche), which publishes Hochschulkompass data.

Run from the repository root:

    python -m study_program_intelligence.ingest.studiensuche fields
    python -m study_program_intelligence.ingest.studiensuche harvest
    python -m study_program_intelligence.ingest.studiensuche harvest --only informatik --force

API (documented by the bundesAPI project, github.com/bundesAPI/studiensuche-api):
    base   https://rest.arbeitsagentur.de/infosysbub/studisu/pc/v1/
    header X-API-Key: infosysbub-studisu
    search studienangebote?sfe=<field ids>&pg=<page>&...

Pass 1 (this script) saves every reply unchanged under data/raw/studiensuche/.
Pass 2 (transform) parses them into a programme table. Keeping the raw replies
means the parser can be fixed later without calling the API again.

Safeguards (see docs/decision_log.md): programme data only, a delay between
requests, caching, robots.txt check, contact address in the User-Agent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests
import yaml

from .documents import allowed_by_robots, load_env, user_agent

BASE_URL = "https://rest.arbeitsagentur.de/infosysbub/studisu/pc/v1/"
API_KEY = "infosysbub-studisu"  # public client id used by the BA website
REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG = REPO_ROOT / "configs" / "studiensuche.yaml"
OUT_DIR = REPO_ROOT / "data" / "raw" / "studiensuche"
MANIFEST = REPO_ROOT / "docs" / "studiensuche_manifest.json"
DELAY_SECONDS = 2
TIMEOUT_SECONDS = 60
MAX_PAGES = 400


def _get(endpoint: str, params: dict) -> dict:
    url = BASE_URL + endpoint
    agent = user_agent()
    if not allowed_by_robots(url, agent):
        raise RuntimeError(f"robots.txt disallows {url}")
    query = "&".join(f"{k}={quote(str(v), safe=';')}" for k, v in params.items())
    resp = requests.get(
        f"{url}?{query}" if query else url,
        headers={"X-API-Key": API_KEY, "User-Agent": agent, "Accept": "application/json"},
        timeout=TIMEOUT_SECONDS,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"{endpoint} {params}: HTTP {resp.status_code} {resp.text[:200]}")
    return resp.json()


def _items(payload) -> list:
    """Find the list of result objects without assuming the exact schema."""
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("items", "studienangebote", "ergebnisse", "results", "content"):
            if isinstance(payload.get(key), list):
                return payload[key]
        lists = [v for v in payload.values() if isinstance(v, list) and v and isinstance(v[0], dict)]
        if lists:
            return max(lists, key=len)
    return []


def fields() -> None:
    payload = _get("studienfelder", {})
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "studienfelder.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    def walk(node, depth=0):
        if isinstance(node, dict):
            name = node.get("name") or node.get("bezeichnung") or node.get("label")
            ident = node.get("dkzIds") or node.get("dkzId") or node.get("id") or node.get("key")
            if name:
                print(f"{'  ' * depth}{name}  [{ident}]")
            for v in node.values():
                if isinstance(v, (list, dict)):
                    walk(v, depth + (1 if name else 0))
        elif isinstance(node, list):
            for v in node:
                walk(v, depth)

    walk(payload)
    print("\nSaved to data/raw/studiensuche/studienfelder.json")



PROBES = [
    ("search word only", {"sw": "Informatik"}),
    ("field, both ids", {"sfe": "94116;93995"}),
    ("field, first id", {"sfe": "94116"}),
    ("field, second id", {"sfe": "93995"}),
    ("field + Bundesweit", {"sfe": "94116;93995", "uk": "Bundesweit"}),
    ("field + st=0", {"sfe": "94116;93995", "st": 0}),
    ("field + st=1", {"sfe": "94116;93995", "st": 1}),
    ("field + st=2", {"sfe": "94116;93995", "st": 2}),
]


def probe() -> None:
    """Try parameter variants and report which ones the API accepts."""
    agent = user_agent()
    for label, params in PROBES:
        for encode in (False, True):
            query = "&".join(f"{k}={quote(str(v), safe='' if encode else ';')}" for k, v in {**params, "pg": 1}.items())
            try:
                resp = requests.get(
                    f"{BASE_URL}studienangebote?{query}",
                    headers={"X-API-Key": API_KEY, "User-Agent": agent, "Accept": "application/json"},
                    timeout=TIMEOUT_SECONDS,
                )
                info = ""
                if resp.status_code == 200:
                    payload = resp.json()
                    keys = list(payload.keys()) if isinstance(payload, dict) else type(payload).__name__
                    info = f"items={len(_items(payload))} keys={keys}"
                else:
                    info = resp.text[:120].replace("\n", " ")
                print(f"{resp.status_code}  {label:<22} {'%3B' if encode else ';  '}  {info}")
            except requests.RequestException as exc:
                print(f"ERR  {label:<22} {exc}")
            time.sleep(DELAY_SECONDS)
            if ";" not in query and "%3B" not in query:
                break  # no semicolon: encoding makes no difference


def harvest_query(q: dict, force: bool) -> dict:
    qid = q["id"]
    folder = OUT_DIR / qid
    params = {k: v for k, v in q.get("params", {}).items()}
    record = {"id": qid, "params": params, "folder": folder.relative_to(REPO_ROOT).as_posix()}

    if folder.exists() and any(folder.glob("page_*.json")) and not force:
        pages = sorted(folder.glob("page_*.json"))
        n = sum(len(_items(json.loads(p.read_text(encoding="utf-8")))) for p in pages)
        record.update(status="cached", pages=len(pages), items=n)
        return record

    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("page_*.json"):
        old.unlink()

    total, previous_hash, page = 0, None, 1
    while page <= MAX_PAGES:
        payload = _get("studienangebote", {**params, "pg": page})
        items = _items(payload)
        digest = hashlib.sha256(json.dumps(items, sort_keys=True).encode()).hexdigest()
        if not items or digest == previous_hash:
            break
        (folder / f"page_{page:03d}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        total += len(items)
        print(f"      {qid} page {page}: {len(items)} items (total {total})")
        if page == 1:
            keys = list(payload.keys()) if isinstance(payload, dict) else type(payload).__name__
            print(f"      reply keys: {keys}")
        previous_hash, page = digest, page + 1
        time.sleep(DELAY_SECONDS)

    record.update(
        status="downloaded",
        retrieved_utc=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        pages=page - 1,
        items=total,
    )
    return record


def harvest(only: list[str] | None, force: bool) -> int:
    queries = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["queries"]
    if only:
        queries = [q for q in queries if q["id"] in set(only)]
    previous = {}
    if MANIFEST.exists():
        previous = {r["id"]: r for r in json.loads(MANIFEST.read_text(encoding="utf-8"))}

    results = []
    for q in queries:
        print(f"{q['id']} ...")
        try:
            rec = harvest_query(q, force)
        except (RuntimeError, requests.RequestException, ValueError) as exc:
            rec = {"id": q["id"], "status": "error", "error": str(exc)}
        if rec["status"] == "cached" and q["id"] in previous:
            rec["retrieved_utc"] = previous[q["id"]].get("retrieved_utc")
        rec["label"] = q.get("label")
        results.append(rec)
        print(f"[{rec['status']:>10}] {q['id']:<28} pages={rec.get('pages')} items={rec.get('items')} {rec.get('error', '')}")

    merged = {**previous, **{r["id"]: r for r in results}}
    MANIFEST.write_text(json.dumps(list(merged.values()), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\nManifest written to docs/studiensuche_manifest.json")
    return 1 if any(r["status"] == "error" for r in results) else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BA Studiensuche harvester")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("fields", help="list study field groups and their ids")
    sub.add_parser("probe", help="test which search parameters the API accepts")
    h = sub.add_parser("harvest", help="download the queries in configs/studiensuche.yaml")
    h.add_argument("--only", nargs="*", default=None)
    h.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    load_env(REPO_ROOT / ".env")
    try:
        if args.command == "fields":
            fields()
            return 0
        if args.command == "probe":
            probe()
            return 0
        return harvest(args.only, args.force)
    except (RuntimeError, requests.RequestException, ValueError) as exc:
        print(f"Error: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
