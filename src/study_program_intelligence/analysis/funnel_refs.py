"""Funnel step 7b: the reference curricula (configs/funnel.yaml: feasibility_gate.references)

Run from the repository root:

    python -m study_program_intelligence.analysis.funnel_refs tries          # which offers are tried, in which order
    python -m study_program_intelligence.analysis.funnel_refs fetch <id> <url>   # one document, robots.txt checked
    python -m study_program_intelligence.analysis.funnel_refs text <id>      # the text of a fetched PDF, page by page
    python -m study_program_intelligence.analysis.funnel_refs check          # completeness of the module tables

tries: for the first 20 candidates of the gate order, the unit's assigned full-time offers at universities of applied
sciences other than OTH, nearest the type's centroid first (universities only if there is no such offer).
fetch: every request goes through ingest.documents (robots.txt, User-Agent, delay); `manifest` writes all requests
to docs/funnel_refs_manifest.json. A blocked or missing document is recorded, never worked around.
check: a reference is complete if its module table lists at least 80 % of the programme's ECTS, thesis included.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .funnel_common import INTERIM, REPO_ROOT
from .funnel_shortlist import ORDER, TRIED_MAX
from .funnel_units import load_step2

TRIES = INTERIM / "funnel2_reference_tries.csv"
RAW = REPO_ROOT / "data" / "raw" / "funnel2_refs"
TEXT = INTERIM / "funnel2_refs_text"
TABLES = INTERIM / "funnel2_refs"
MANIFEST = REPO_ROOT / "docs" / "funnel_refs_manifest.json"
HAW = "Fachhochschule/Hochschule für angewandte Wissenschaften"
PER_REFERENCE, COMPLETE = 5, 0.8              # feasibility_gate.references: tries per reference, complete
LEFT_OUT = ("thesis", "internship", "practical semester")       # module_kinds
KINDS = ("compulsory", "elective") + LEFT_OUT


def tries() -> None:
    d, t, emb, cent = load_step2()
    g = pd.read_csv(ORDER, float_precision="round_trip").head(TRIED_MAX)
    rows = []
    for _, r in g.iterrows():
        a = d[(d["assigned_type"] == r["type"]) & (d["level"] == r["level"]) & d["full_time"].astype(bool) & ~d["is_oth"].astype(bool)].copy()
        a["distance to the centroid"] = 1 - emb[a.index] @ cent[int(r["type"])]
        haw = a[a["institution_type"] == HAW]
        use, pool = (haw, "universities of applied sciences") if len(haw) else (a, "universities only (no offer at a university of applied sciences)")
        use = use.sort_values(["distance to the centroid", "programme_id"], kind="mergesort").drop_duplicates(["institution", "clean_title"])
        for k, (_, o) in enumerate(use.iterrows(), 1):
            rows.append({"gate order": int(r["gate order"]), "type": int(r["type"]), "level": r["level"], "try": k, "institution": o["institution"], "city": o["city"], "title": o["title"],
                         "programme_id": o["programme_id"], "distance to the centroid": o["distance to the centroid"], "offers from": pool})
    out = pd.DataFrame(rows)
    out.to_csv(TRIES, index=False)
    print(out.groupby(["gate order", "type", "level"]).agg(offers=("try", "size"), institutions=("institution", "nunique")).to_string())


def fetch(doc_id: str, url: str) -> None:
    from ..ingest.documents import allowed_by_robots, delay_for, load_env, sha256, user_agent
    import requests
    load_env(REPO_ROOT / ".env")
    agent = user_agent()
    RAW.mkdir(parents=True, exist_ok=True)
    rec = {"id": doc_id, "url": url, "asked_utc": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    if not allowed_by_robots(url, agent):
        rec["status"] = "skipped_robots"
    else:
        time.sleep(delay_for(url, agent))
        try:
            resp = requests.get(url, headers={"User-Agent": agent}, timeout=60)
            if resp.status_code != 200:
                rec.update(status="error", error=f"HTTP {resp.status_code}")
            else:
                pdf = resp.content[:5] == b"%PDF-"
                dest = RAW / f"{doc_id}{'.pdf' if pdf else '.html'}"
                dest.write_bytes(resp.content)
                rec.update(status="downloaded", file=dest.relative_to(REPO_ROOT).as_posix(), bytes=len(resp.content), sha256=sha256(dest), content_type=resp.headers.get("Content-Type"))
        except requests.RequestException as exc:
            rec.update(status="error", error=type(exc).__name__)
    (RAW / "log").mkdir(exist_ok=True)                 # one file per request: several collectors may run at once
    (RAW / "log" / f"{rec['asked_utc'].replace(':', '')}_{doc_id}.json").write_text(json.dumps(rec, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(rec, ensure_ascii=False))


def manifest() -> None:
    """All requests of the collectors, in time order, as the committed manifest."""
    old = [r for r in (json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else [])]
    new = [json.loads(f.read_text(encoding="utf-8")) for f in sorted((RAW / "log").glob("*.json"))]
    seen = {(r["id"], r["asked_utc"]) for r in new}
    log = sorted([r for r in old if (r["id"], r["asked_utc"]) not in seen] + new, key=lambda r: (r["asked_utc"], r["id"]))
    MANIFEST.write_text(json.dumps(log, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(len(log), "requests;", pd.Series([r["status"] for r in log]).value_counts().to_dict())


def text(doc_id: str) -> None:
    from pypdf import PdfReader
    TEXT.mkdir(parents=True, exist_ok=True)
    pages = PdfReader(str(RAW / f"{doc_id}.pdf")).pages
    out = TEXT / f"{doc_id}.txt"
    out.write_text("\n".join(f"\n===== page {i} =====\n{p.extract_text() or ''}" for i, p in enumerate(pages, 1)), encoding="utf-8")
    print(out, len(pages), "pages")


def table_check(m: pd.DataFrame, total_ects: float) -> dict:
    """Rule references.complete and module_kinds for one module table (columns module, ects, kind, content, page)."""
    bad = sorted(set(m["kind"]) - set(KINDS))
    ects = pd.to_numeric(m["ects"], errors="coerce")
    listed = float(ects.sum())
    counted = m[~m["kind"].isin(LEFT_OUT)]
    return {"modules": len(m), "listed ECTS": listed, "programme ECTS": total_ects, "share listed": listed / total_ects, "complete": bool(listed / total_ects >= COMPLETE and not bad and ects.notna().all()),
            "counted modules": len(counted), "counted ECTS": float(pd.to_numeric(counted["ects"], errors="coerce").sum()), "compulsory ECTS": float(ects[m["kind"] == "compulsory"].sum()),
            "elective ECTS": float(ects[m["kind"] == "elective"].sum()), "unknown kinds": bad, "modules without ECTS": int(ects.isna().sum()),
            "modules with under 100 characters of content": int((counted["content"].fillna("").str.len() < 100).sum())}


def check() -> None:
    src = json.loads((TABLES / "sources.json").read_text(encoding="utf-8"))
    rows = []
    for ref, s in sorted(src.items()):
        f = TABLES / f"{ref}.csv"
        if f.exists():
            rows.append({"reference": ref, **table_check(pd.read_csv(f), float(s["programme_ects"]))})
    print(pd.DataFrame(rows).to_string())


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"tries": tries, "fetch": lambda: fetch(sys.argv[2], sys.argv[3]), "text": lambda: text(sys.argv[2]), "check": check, "manifest": manifest}[cmd]()
