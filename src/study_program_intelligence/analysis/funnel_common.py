"""Shared helpers of the funnel rerun (configs/funnel.yaml, version 3).

run_stamp() enforces the rule conformance.code_first: a step's code is committed before it runs, its outputs carry the
commit hash, and a working tree with uncommitted changes to tracked files stops the run.
"""

from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG = REPO_ROOT / "configs" / "funnel.yaml"
INTERIM = REPO_ROOT / "data" / "interim"
REPORTS = REPO_ROOT / "reports" / "funnel2"


def config() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(REPO_ROOT), *args], capture_output=True, text=True, check=True).stdout.strip()


def run_stamp(allow_dirty: bool = False) -> dict:
    """Commit hash and date of this run. Raises if tracked files have uncommitted changes (untracked files are ignored)."""
    dirty = _git("status", "--porcelain", "--untracked-files=no")
    if dirty and not allow_dirty:
        raise RuntimeError("Working tree has uncommitted changes to tracked files; commit the code before running a funnel step:\n" + dirty)
    return {"commit": _git("rev-parse", "--short", "HEAD"), "date": date.today().isoformat(), "clean": not dirty}


def universe():
    """Bachelor and master offers in Germany, one row per institution, title and degree (configs/funnel.yaml, universe).

    Of several variants the full-time one is kept; among equal variants the one with the lowest programme id, so that the
    result does not depend on the order of the file. Adds full_time, distance_only and level.
    """
    import pandas as pd
    u = config()["universe"]["fit_on"]
    d = pd.read_csv(REPO_ROOT / "data" / "processed" / "programmes_full.csv", low_memory=False, dtype={"programme_id": str})
    d = d[d["degree"].isin(u["degrees"]) & (d["country"] == u["country"])].copy()
    d["full_time"] = d["study_form"] == u["study_form"]
    d["distance_only"] = d["study_form"] == "Fernstudium"
    d["_id"] = pd.to_numeric(d["programme_id"], errors="coerce")
    d = d.sort_values(["full_time", "_id"], ascending=[False, True], kind="stable").drop_duplicates(["institution", "title", "degree"])
    d["level"] = d["degree"].map(dict(zip(u["degrees"], ("bachelor", "master"))))
    return d.drop(columns="_id").reset_index(drop=True)


def md_table(df) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(map(str, cols)) + " |", "|" + "---|" * len(cols)]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join("" if v != v else str(v).replace("|", "/") for v in row) + " |")
    return "\n".join(lines)
