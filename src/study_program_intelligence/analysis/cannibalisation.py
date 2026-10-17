"""Cannibalisation: where would the first-years of an OTH Cyber Security B.Sc. come from? (Step 48)

Run from the repository root:

    python -m study_program_intelligence.analysis.cannibalisation

Model: the Step 47 Huff model (Bavarian counties, qualified school leavers, distance decay beta calibrated on the
Bavarian student flows) run twice: baseline (dedicated cyber bachelors THI, TH Deggendorf, THWS, HNU at weight 1;
general bachelors with a security focus area, incl. OTH's Industrie-4.0-Informatik / Medieninformatik, at weight w)
and with the new OTH programme added at weight 1. Under Huff, a new alternative draws from every existing alternative
in proportion to its baseline share, so the new programme's students from county c split into
  (a) taken from OTH's existing programmes (cannibalisation),
  (b) won from other universities (net new to OTH), of which
  (c) students from OTH's own pool (Step 42) whose baseline choice lay outside that region (regional benefit).
The model has a fixed demand (no students who would not have studied otherwise) and covers only programmes with
security in the title or focus areas; students who would otherwise take a general OTH programme without a security
focus are not counted in (a) (limitation). Shares are applied to the Step 47 low/central/high gross intakes.
Outputs: data/interim/capture_scenarios.csv (for Step 49), reports/cannibalisation.md.
"""

from __future__ import annotations

import itertools
from pathlib import Path

import numpy as np
import pandas as pd

from .capture import CYBER_SITES, LEAVERS, haversine, secondary_sites
from .catchment import counties

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT = REPO_ROOT / "data" / "interim" / "capture_scenarios.csv"
REPORT = REPO_ROOT / "reports" / "cannibalisation.md"
GROSS = {"low": 21, "central": 39, "high": 75}   # Step 47 steady-state first-years (docs/evidence_capture.md)
BETAS = (1.3, 1.6, 1.95)                          # Step 47 calibration: best 1.6, 10 % band 1.3-1.95
WEIGHTS = (0.5, 1.0)                              # weight of security-focus programmes (w = 0 would hide OTH's own)
OTH_EXISTING = "(focus) Ostbayerische Technische Hochschule Amberg-Weiden"
NEW = "OTH (new)"


def site_county(lat: float, lon: float, geo: pd.DataFrame) -> str:
    return geo.iloc[int(np.argmin(haversine(geo["lat"].values, geo["lon"].values, lat, lon)))]["county"]


def split(beta: float, w: float, pool: pd.DataFrame, geo: pd.DataFrame) -> dict:
    sites = {**{k: (v, 1.0) for k, v in CYBER_SITES.items() if k != NEW}, **{k: (v, w) for k, v in secondary_sites().items()}}
    own = set(geo.loc[geo["own_pool"], "county"])
    in_region = {s: site_county(*locs[0], geo) in own for s, (locs, _) in sites.items()}
    new_locs = CYBER_SITES[NEW]
    tot = {"new": 0.0, "a": 0.0, "b": 0.0, "c": 0.0}
    for c in pool.itertuples():
        base = {s: a * max(min(haversine(c.lat, c.lon, la, lo) for la, lo in locs), 5.0) ** (-beta) for s, (locs, a) in sites.items()}
        new_w = max(min(haversine(c.lat, c.lon, la, lo) for la, lo in new_locs), 5.0) ** (-beta)
        p_new = new_w / (new_w + sum(base.values()))
        n = c.hzb * p_new
        bsum = sum(base.values())
        for s, v in base.items():
            take = n * v / bsum
            if s == OTH_EXISTING:
                tot["a"] += take
            else:
                tot["b"] += take
                if c.key in own and not in_region[s]:
                    tot["c"] += take
        tot["new"] += n
    return {k: v / tot["new"] for k, v in tot.items() if k != "new"}


def _md(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(f"{v:.2f}" if isinstance(v, float) else str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(out)


def main() -> None:
    lv = pd.read_csv(LEAVERS, dtype={"key": str})
    lv = lv[(lv["year"] == lv["year"].max()) & (lv["key"].str.len() == 5)]
    geo = counties()
    pool = lv.merge(geo, left_on="key", right_on="county")[["key", "hzb_total", "lat", "lon"]].rename(columns={"hzb_total": "hzb"})
    rows = [{"beta": b, "w_sec": w, **split(b, w, pool, geo)} for b, w in itertools.product(BETAS, WEIGHTS)]
    sh = pd.DataFrame(rows).rename(columns={"a": "share (a) from OTH", "b": "share (b) other universities", "c": "share (c) kept in region"})
    # carry forward: low gross with the highest cannibalisation, high gross with the lowest, central with the base case
    worst = sh.loc[sh["share (a) from OTH"].idxmax()]
    best = sh.loc[sh["share (a) from OTH"].idxmin()]
    base = sh[(sh["beta"] == 1.6) & (sh["w_sec"] == 0.5)].iloc[0]
    sc = []
    for name, r in (("low", worst), ("central", base), ("high", best)):
        g = GROSS[name]
        sc.append({"scenario": name, "gross first-years": g, "(a) from OTH programmes": round(g * r["share (a) from OTH"], 1),
                   "(b) net new to OTH": round(g * r["share (b) other universities"], 1), "(c) kept in region": round(g * r["share (c) kept in region"], 1),
                   "net-new share": round(r["share (b) other universities"], 3), "beta": r["beta"], "w_sec": r["w_sec"]})
    sc = pd.DataFrame(sc)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    sc.to_csv(OUT, index=False)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(["# Cannibalisation: origin of the OTH Cyber B.Sc. first-years (generated)", "",
                                 "## Shares by model variant", "", _md(sh), "",
                                 "## Scenarios carried forward (data/interim/capture_scenarios.csv)", "", _md(sc), ""]), encoding="utf-8")
    print(sh.round(3).to_string(index=False)); print(sc.to_string(index=False))


if __name__ == "__main__":
    main()
