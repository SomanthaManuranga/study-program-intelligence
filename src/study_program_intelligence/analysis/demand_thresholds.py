"""Apply the pre-registered demand thresholds (configs/demand_thresholds.yaml) to the 1 Nov job ads and the Trends download.

Run from the repository root once both inputs exist:

    python -m study_program_intelligence.analysis.demand_thresholds

Every rule is in the config; this module only applies it. Job ads: docs/jobsuche_snapshots.json (first complete
snapshot on or after 2026-11-01). Trends: data/raw/trends/tiebreak_DE_anchored.csv (Google Trends export).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG = REPO_ROOT / "configs" / "demand_thresholds.yaml"
SNAPSHOTS = REPO_ROOT / "docs" / "jobsuche_snapshots.json"
TRENDS = REPO_ROOT / "data" / "raw" / "trends" / "tiebreak_DE_anchored.csv"
FIRST_DATE = "2026-11-01"


def config() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def group_count(snap: pd.DataFrame, keys: list[str], region: str) -> int:
    """Largest single keyword count of a group in a region (not the sum)."""
    d = snap[snap["keyword_id"].isin(keys) & (snap["region_id"] == region)]
    if set(d["keyword_id"]) != set(keys):
        raise ValueError(f"snapshot lacks keywords {set(keys) - set(d['keyword_id'])} for {region}")
    return int(d["total"].max())


def complete(snap: pd.DataFrame, cfg: dict | None = None) -> bool:
    """True if the snapshot has every keyword of both groups in every region the thresholds use."""
    cfg = cfg or config()
    regions = {cfg[k]["job_ads"]["region"] for k in ("robotics_vs_arvr", "robotics_vs_min_cohort")}
    try:
        for keys in cfg["groups"].values():
            for region in regions:
                group_count(snap, keys, region)
    except ValueError:
        return False
    return True


def slope(yearly: pd.Series) -> float:
    """OLS slope of yearly values (index = year), percentage points per year."""
    return float(np.polyfit(yearly.index.astype(float), yearly.values.astype(float), 1)[0])


def yearly_shares(trends: pd.DataFrame, term: str, anchor: str) -> pd.Series:
    """Monthly share term / anchor x 100, mean of January-October per year, 2022-2026. trends: index = month (datetime)."""
    t = trends[(trends.index.year >= 2022) & (trends.index.year <= 2026) & (trends.index.month <= 10)]
    share = 100 * t[term] / t[anchor]
    return share.groupby(share.index.year).mean()


def job_ads_vs(r: int, a: int, max_ratio: float) -> str:
    if max(r, a) <= max_ratio * min(r, a):
        return "neutral"
    return "robotics" if r > a else "arvr"


def trends_vs(s_r: float, s_a: float, max_diff: float) -> str:
    if abs(s_r - s_a) < max_diff:
        return "neutral"
    return "robotics" if s_r > s_a else "arvr"


def band(value: float, favours_min: float, against_max: float) -> str:
    return "favours" if value >= favours_min else "against" if value <= against_max else "neutral"


def downgrade(job_band: str, trends_band: str, central_gross: float, cfg: dict) -> bool:
    d = cfg["downgrade"]
    against = [job_band, trends_band].count("against")
    return (d["both_against"] and against == 2) or (against >= 1 and central_gross < d["one_against_and_central_below"])


def evaluate(snap: pd.DataFrame, trends: pd.DataFrame, central_gross: float, cfg: dict | None = None) -> dict:
    cfg = cfg or config()
    g, t = cfg["groups"], cfg["trends_terms"]
    a, b = cfg["robotics_vs_arvr"], cfg["robotics_vs_min_cohort"]
    r = group_count(snap, g["robotics"], a["job_ads"]["region"])
    ar = group_count(snap, g["arvr"], a["job_ads"]["region"])
    s_r = slope(yearly_shares(trends, t["robotics"][0], t["anchor"]))
    s_a = max(slope(yearly_shares(trends, term, t["anchor"])) for term in t["arvr"])
    job_min = band(group_count(snap, g["robotics"], b["job_ads"]["region"]), b["job_ads"]["favours_min"], b["job_ads"]["against_max"])
    tr_min = band(s_r, b["trends"]["favours_min_pp_per_year"], b["trends"]["against_max_pp_per_year"])
    return {"robotics job ads": r, "AR/VR job ads": ar, "robotics slope": round(s_r, 3), "AR/VR best slope": round(s_a, 3),
            "job ads: robotics vs AR/VR": job_ads_vs(r, ar, a["job_ads"]["neutral_max_ratio"]),
            "Trends: robotics vs AR/VR": trends_vs(s_r, s_a, a["trends"]["neutral_max_diff_pp_per_year"]),
            "job ads: robotics vs minimum cohort": job_min, "Trends: robotics vs minimum cohort": tr_min,
            "downgrade robotics to not recommended": downgrade(job_min, tr_min, central_gross, cfg)}


def load_trends(path: Path = TRENDS) -> pd.DataFrame:
    """Google Trends 'Interest over time' CSV: one header block, then 'Month,<term>: (Germany),...'. '<1' counts as 0.5."""
    raw = pd.read_csv(path, skiprows=1)
    raw.columns = ["month"] + [c.split(":")[0].strip() for c in raw.columns[1:]]
    raw["month"] = pd.to_datetime(raw["month"])
    return raw.set_index("month").replace("<1", 0.5).astype(float)


def main() -> None:
    snaps = pd.DataFrame(json.loads(SNAPSHOTS.read_text(encoding="utf-8")))
    later = [d for d in sorted(snaps["date"].unique()) if d >= FIRST_DATE and complete(snaps[snaps["date"] == d])]
    if not later or not TRENDS.exists():
        raise SystemExit("complete 1 Nov (or later) snapshot or Trends download missing: nothing to evaluate yet")
    snap = snaps[snaps["date"] == later[0]]
    central = pd.read_csv(REPO_ROOT / "data" / "interim" / "candidate_first_years.csv").query(
        "candidate == 'robotics_b' and scenario == 'central' and phase == 'steady state'")["gross (model, base year)"].iloc[0]
    for k, v in evaluate(snap, load_trends(), float(central)).items():
        print(f"{k}: {v}")


if __name__ == "__main__":
    main()
