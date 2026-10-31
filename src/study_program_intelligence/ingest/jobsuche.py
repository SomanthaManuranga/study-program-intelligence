"""Count open job ads by keyword and region from the BA Jobsuche (Bundesagentur fuer Arbeit).

Run from the repository root:

    python -m study_program_intelligence.ingest.jobsuche probe
    python -m study_program_intelligence.ingest.jobsuche snapshot

API (documented by the bundesAPI project, github.com/bundesAPI/jobsuche-api):
    base   https://rest.arbeitsagentur.de/jobboerse/jobsuche-service
    header X-API-Key: jobboerse-jobsuche
    search /pc/v4/jobs (or v4/app, v6, see probe) ?was=<keyword>&wo=<place>&umkreis=<km>&angebotsart=1

Only the total number of matching ads is used (counts, no personal data). Each snapshot is a
point in time: running it again on another day adds a new row, which builds a small time series. A missing total
field counts as an ERROR (never as a silent null), and a rerun on the same day replaces the stored day only when it
has at least as many counts, so a partial rerun cannot overwrite a complete snapshot.
Output: data/raw/jobsuche/<date>/<query>.json  first result page (local, not committed)
        docs/jobsuche_snapshots.json             counts per date, keyword and region (committed)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests
import yaml

from .documents import allowed_by_robots, load_env, user_agent

BASE = "https://rest.arbeitsagentur.de/jobboerse/jobsuche-service"
API_KEY = "jobboerse-jobsuche"  # public client id used by the BA job board
REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG = REPO_ROOT / "configs" / "jobsuche.yaml"
RAW = REPO_ROOT / "data" / "raw" / "jobsuche"
SNAPSHOTS = REPO_ROOT / "docs" / "jobsuche_snapshots.json"
DELAY_SECONDS = 2
TIMEOUT_SECONDS = 60
TOTAL_KEYS = ("maxErgebnisse", "totalElements", "anzahl", "total", "numberOfResults")


def _get(path: str, params: dict) -> requests.Response:
    query = "&".join(f"{k}={quote(str(v))}" for k, v in params.items() if v not in (None, ""))
    url = f"{BASE}{path}?{query}"
    agent = user_agent()
    if not allowed_by_robots(url, agent):
        raise RuntimeError(f"robots.txt disallows {url}")
    return requests.get(url, headers={"X-API-Key": API_KEY, "User-Agent": agent, "Accept": "application/json"},
                        timeout=TIMEOUT_SECONDS)


def _total(payload) -> int | None:
    if isinstance(payload, dict):
        for k in TOTAL_KEYS:
            if isinstance(payload.get(k), int):
                return payload[k]
        for v in payload.values():          # e.g. nested {"page": {"totalElements": n}}
            t = _total(v) if isinstance(v, dict) else None
            if t is not None:
                return t
    return None


def probe() -> None:
    for path in ("/pc/v4/jobs", "/pc/v4/app/jobs", "/pc/v6/jobs"):
        try:
            resp = _get(path, {"was": "Cyber Security", "angebotsart": 1, "page": 1, "size": 1})
            info = resp.text[:120].replace("\n", " ")
            if resp.status_code == 200:
                payload = resp.json()
                keys = list(payload.keys()) if isinstance(payload, dict) else type(payload).__name__
                info = f"total={_total(payload)} keys={keys}"
            print(f"{resp.status_code}  {path:<18} {info}")
        except requests.RequestException as exc:
            print(f"ERR  {path:<18} {exc}")
        time.sleep(DELAY_SECONDS)


def snapshot() -> int:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    path, regions, keywords = cfg["endpoint"], cfg["regions"], cfg["keywords"]
    today = date.today().isoformat()
    folder = RAW / today
    folder.mkdir(parents=True, exist_ok=True)

    history = json.loads(SNAPSHOTS.read_text(encoding="utf-8")) if SNAPSHOTS.exists() else []
    rows, errors = [], 0
    for kw in keywords:
        for reg in regions:
            params = {"was": kw["was"], "wo": reg.get("wo"), "umkreis": reg.get("umkreis"),
                      "angebotsart": 1, "page": 1, "size": 1}
            qid = f"{kw['id']}__{reg['id']}"
            try:
                resp = _get(path, params)
                if resp.status_code != 200:
                    raise RuntimeError(f"HTTP {resp.status_code} {resp.text[:120]}")
                payload = resp.json()
                (folder / f"{qid}.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
                total = _total(payload)
                if total is None:   # a count of 0 is valid; a reply without a total field is an error, never a null row
                    raise RuntimeError("no total field in the reply "
                                       f"({list(payload)[:8] if isinstance(payload, dict) else type(payload).__name__})")
                rows.append({"date": today, "keyword_id": kw["id"], "keyword": kw["was"], "group": kw.get("group"),
                             "region_id": reg["id"], "total": total})
                print(f"{kw['id']:<22} {reg['id']:<14} {total}")
            except (RuntimeError, requests.RequestException, ValueError) as exc:
                errors += 1
                print(f"{kw['id']:<22} {reg['id']:<14} ERROR {exc}")
            time.sleep(DELAY_SECONDS)

    stored = [r for r in history if r["date"] == today]
    if len(rows) < len(stored):   # a partial rerun must not overwrite a more complete snapshot of the same day
        print(f"\n{len(rows)} counts for {today}, but {len(stored)} are already stored: keeping the stored snapshot. "
              "Fix the errors above and run again.")
        return 1
    history = [r for r in history if r["date"] != today] + rows   # one snapshot per day
    SNAPSHOTS.write_text(json.dumps(history, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n{len(rows)} counts for {today}. Written: docs/jobsuche_snapshots.json")
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BA Jobsuche counts")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("probe", help="find the working endpoint version")
    sub.add_parser("snapshot", help="count ads for the keywords and regions in configs/jobsuche.yaml")
    args = parser.parse_args(argv)
    load_env(REPO_ROOT / ".env")
    if args.command == "probe":
        probe()
        return 0
    return snapshot()


if __name__ == "__main__":
    sys.exit(main())
