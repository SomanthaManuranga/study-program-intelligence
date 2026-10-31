"""Pre-registered demand thresholds (docs/criteria_capture_cost_demand.md, E5): committed before any 1 Nov data, numeric,
applied mechanically."""

import datetime as dt
import json
import subprocess
from pathlib import Path

import pandas as pd
import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
FIRST = dt.date(2026, 11, 1)


def first_commit_time(path: str) -> dt.datetime | None:
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%cI", "--", path], cwd=REPO, capture_output=True,
                         text=True).stdout.split()
    return dt.datetime.fromisoformat(out[-1]) if out else None


def test_thresholds_committed_before_any_1_nov_data():
    t = first_commit_time("configs/demand_thresholds.yaml")
    assert t is not None, "configs/demand_thresholds.yaml is not committed"
    assert t.date() < FIRST
    # no job-ad data from 1 Nov on may predate the commit: raw folders are named by snapshot date
    raw = REPO / "data" / "raw" / "jobsuche"
    for d in (raw.iterdir() if raw.exists() else []):
        if d.is_dir() and d.name >= FIRST.isoformat():
            assert dt.datetime.fromtimestamp(d.stat().st_mtime, tz=t.tzinfo) > t, d.name
    snaps = json.loads((REPO / "docs" / "jobsuche_snapshots.json").read_text(encoding="utf-8"))
    assert all(s["date"] >= FIRST.isoformat() or s["keyword_id"] not in {"virtual_reality", "servicerobotik"} for s in snaps)


def test_every_threshold_is_numeric():
    cfg = yaml.safe_load((REPO / "configs" / "demand_thresholds.yaml").read_text(encoding="utf-8"))
    nums = [cfg["robotics_vs_arvr"]["job_ads"]["neutral_max_ratio"], cfg["robotics_vs_arvr"]["trends"]["neutral_max_diff_pp_per_year"],
            cfg["robotics_vs_min_cohort"]["job_ads"]["favours_min"], cfg["robotics_vs_min_cohort"]["job_ads"]["against_max"],
            cfg["robotics_vs_min_cohort"]["trends"]["favours_min_pp_per_year"],
            cfg["robotics_vs_min_cohort"]["trends"]["against_max_pp_per_year"], cfg["downgrade"]["one_against_and_central_below"]]
    assert all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in nums)
    assert cfg["robotics_vs_min_cohort"]["job_ads"]["against_max"] < cfg["robotics_vs_min_cohort"]["job_ads"]["favours_min"]
    keys = {k["id"] for k in yaml.safe_load((REPO / "configs" / "jobsuche.yaml").read_text(encoding="utf-8"))["keywords"]}
    assert set(cfg["groups"]["robotics"]) | set(cfg["groups"]["arvr"]) <= keys


def _synthetic(robotik, servicerobotik, vr, ar, cg, robotik_shares, vr_shares, vc_shares):
    snap = pd.DataFrame([{"keyword_id": k, "region_id": "amberg_100km", "total": v} for k, v in
                         (("robotik", robotik), ("servicerobotik", servicerobotik), ("virtual_reality", vr),
                          ("augmented_reality", ar), ("computergrafik", cg))])
    months = pd.date_range("2022-01-01", "2026-10-01", freq="MS")
    year = lambda shares: [shares[m.year - 2022] for m in months]
    trends = pd.DataFrame({"Informatik Studium": 100.0, "Robotik Studium": year(robotik_shares),
                           "Virtual Reality Studium": year(vr_shares), "Visual Computing Studium": year(vc_shares)}, index=months)
    return snap, trends


def test_rules_applied_as_written():
    from study_program_intelligence.analysis.demand_thresholds import evaluate
    flat = [3.0] * 5
    # robotics 160 vs AR/VR 150: ratio 1.067 <= 1.10 -> neutral; 160 >= 150 -> favours the minimum-cohort level
    snap, tr = _synthetic(160, 20, 150, 90, 40, flat, flat, flat)
    r = evaluate(snap, tr, central_gross=28.7)
    assert r["job ads: robotics vs AR/VR"] == "neutral" and r["job ads: robotics vs minimum cohort"] == "favours"
    assert r["Trends: robotics vs AR/VR"] == "neutral" and r["Trends: robotics vs minimum cohort"] == "neutral"
    assert not r["downgrade robotics to not recommended"]
    # robotics 60 (<= 74: against), falling Robotik share (-0.2 pp/yr: against) -> downgrade by rule 1
    snap, tr = _synthetic(60, 5, 200, 90, 40, [3.4, 3.2, 3.0, 2.8, 2.6], [1.0, 1.2, 1.4, 1.6, 1.8], flat)
    r = evaluate(snap, tr, central_gross=28.7)
    assert r["job ads: robotics vs AR/VR"] == "arvr" and r["Trends: robotics vs AR/VR"] == "arvr"
    assert r["job ads: robotics vs minimum cohort"] == "against" and r["Trends: robotics vs minimum cohort"] == "against"
    assert r["downgrade robotics to not recommended"]
    # one signal against, central steady state 19.9 < 20 -> downgrade by rule 2; with 20.0 -> no downgrade
    snap, tr = _synthetic(60, 5, 50, 40, 30, flat, flat, flat)
    assert evaluate(snap, tr, central_gross=19.9)["downgrade robotics to not recommended"]
    assert not evaluate(snap, tr, central_gross=20.0)["downgrade robotics to not recommended"]


def test_incomplete_snapshot_is_skipped():
    from study_program_intelligence.analysis import demand_thresholds as D
    cfg = D.config()
    region = cfg["robotics_vs_arvr"]["job_ads"]["region"]
    keys = [k for g in cfg["groups"].values() for k in g]
    full = pd.DataFrame({"keyword_id": keys, "region_id": region, "total": 1})
    assert D.complete(full, cfg) and not D.complete(full.iloc[1:], cfg)
    nulled = full.assign(total=[None] + [1] * (len(keys) - 1))   # a null total counts as incomplete, not as zero
    assert not D.complete(nulled, cfg)
