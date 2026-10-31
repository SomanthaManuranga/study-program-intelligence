"""Required-capture-share benchmark and competition accessibility per candidate (deep-analysis layer).

Run from the repository root:

    python -m study_program_intelligence.analysis.capture_benchmark

Two arguments the capture model implies but never states as numbers:
1. REQUIRED SHARE: how large a slice of its own catchment OTH would need for a minimum cohort (20) and for the
   pre-registered central intake - and how that compares with the share comparable programmes demonstrably achieve
   of THEIR equivalent pools (TH Deggendorf ~60 of a nearest-site pool of about 5,600; THI capacity 25 of an
   inflated nearest-site pool, both from docs/evidence_catchment.md logic, recomputed here from the generated
   tables). A programme that needs 0.4-0.7 % of its pool, where a peer achieves about 1 %, is a modest ask.
2. ACCESSIBILITY: a Hansen-style index per candidate - distance-weighted qualified school leavers (demand access,
   d^-1.6, the calibrated decay) against distance-weighted competitor sites (competition pressure, dedicated = 1,
   focus = 0.5) - summarised as demand access per unit of competition, OTH relative to the candidate's nearest
   dedicated competitor site. It quantifies "thin supply near OTH" beyond raw counts.

Assumptions, stated: straight-line distances, 5 km floor as in the capture model; beta fixed at the calibrated 1.6;
focus weight 0.5 (the pre-registered middle); leavers of 2023/24 by school location; Bavarian counties only (as in
Step 42). Limitations: nearest-site pools ignore programme choice (THI's pool is inflated by Munich, said in
docs/evidence_catchment.md); the index is descriptive, not a market-share forecast.

Outputs: data/interim/capture_benchmark.csv, reports/capture_benchmark.md.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .candidates import config as cand_config, matches, offers
from .capture import CYBER_SITES, haversine, secondary_sites
from .spec_curve import load_geo, load_pool

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT = REPO_ROOT / "data" / "interim" / "capture_benchmark.csv"
REPORT = REPO_ROOT / "reports" / "capture_benchmark.md"
BETA, W_FOCUS, MIN_COHORT = 1.6, 0.5, 20
CENTRAL = {"cyber": 39.0, "robotics_b": 28.7, "arvr": 58.5}   # pre-registered central gross (generated tables)
ANCHOR_SITES = {"THI Cybersicherheit": ("TH Ingolstadt", 25.0), "TH Deggendorf Cyber Security": ("TH Deggendorf", 60.0)}


OTH_CAMPUSES = ((49.4425, 11.8558), (49.6761, 12.1603))   # Amberg, Weiden: distance = nearer campus, as in Step 42


def dist_oth(pool: pd.DataFrame) -> np.ndarray:
    return np.minimum.reduce([haversine(pool["lat"].to_numpy(), pool["lon"].to_numpy(), la, lo)
                              for la, lo in OTH_CAMPUSES])


def access(pool: pd.DataFrame, lat: float | None = None, lon: float | None = None) -> float:
    d = dist_oth(pool) if lat is None else haversine(pool["lat"].to_numpy(), pool["lon"].to_numpy(), lat, lon)
    return float((pool["hzb"].to_numpy() * np.maximum(d, 5.0) ** -BETA).sum())


def nearest_site_pools(pool: pd.DataFrame, sites: dict[str, list[tuple[float, float]]]) -> dict[str, float]:
    """Leavers per site if every student chose the nearest site; a site's distance is its nearest campus."""
    names = list(sites)
    d = np.stack([np.minimum.reduce([haversine(pool["lat"].to_numpy(), pool["lon"].to_numpy(), la, lo)
                                     for la, lo in locs]) for locs in sites.values()])
    nearest = np.argmin(d, axis=0)
    return {names[k]: float(pool.loc[nearest == k, "hzb"].sum()) for k in range(len(names))}


def candidate_sites(key: str) -> tuple[list[tuple[str, float, float, float]], tuple[str, float, float] | None]:
    """(sites with weight: dedicated 1, focus W_FOCUS; non-OTH), and the nearest dedicated site."""
    cfg = cand_config()["candidates"]
    if key == "cyber":
        ded = [(k, la, lo, 1.0) for k, locs in CYBER_SITES.items() if k != "OTH (new)" for la, lo in locs[:1]]
        ded += [(k, la, lo, W_FOCUS) for k, locs in secondary_sites().items() for la, lo in locs[:1]
                if "Amberg-Weiden" not in k]   # Bavarian security-focus bachelors; OTH's own are cannibalisation, not competition
        nearest = min(((k, la, lo) for k, la, lo, w in ded if w == 1.0),
                      key=lambda s: haversine(s[1], s[2], 49.4425, 11.8558))
        return ded, nearest
    c = cfg[key]
    p = offers(c)
    title, focus = matches(p, c)
    ded = p[title & ~p["is_oth"]].dropna(subset=["lat", "lon"])
    foc = p[focus & ~p["is_oth"]].dropna(subset=["lat", "lon"])
    sites = [(f"{r.institution} ({r.city})", r.lat, r.lon, 1.0)
             for r in ded.groupby(["institution", "city"], as_index=False)[["lat", "lon"]].median().itertuples()]
    sites += [(f"(focus) {r.institution} ({r.city})", r.lat, r.lon, W_FOCUS)
              for r in foc.groupby(["institution", "city"], as_index=False)[["lat", "lon"]].median().itertuples()]
    near = ded.sort_values("km_oth").iloc[0] if len(ded) else None
    nearest = (f"{near.institution} ({near.city})", float(near.lat), float(near.lon)) if near is not None else None
    return sites, nearest


def competition_pressure(sites: list[tuple[str, float, float, float]], lat: float, lon: float) -> float:
    if not sites:
        return 0.0
    return float(sum(w * max(haversine(la, lo, lat, lon), 5.0) ** -BETA for _, la, lo, w in sites))


def main() -> None:
    geo = load_geo()
    pool = load_pool(geo)
    own_pool = float(pool.loc[pool["key"].isin(set(geo.loc[geo["own_pool"], "county"])), "hzb"].sum())
    oth = OTH_CAMPUSES[0]   # reference point for competition pressure (Amberg, the main campus)
    pool100 = float(pool.loc[dist_oth(pool) <= 100, "hzb"].sum())

    # 1. required vs demonstrated shares (cyber sites)
    pools = nearest_site_pools(pool, dict(CYBER_SITES))
    share_rows = [{"programme": "OTH candidate (minimum cohort)", "intake": MIN_COHORT, "pool basis": "own pool",
                   "pool": round(own_pool), "implied share %": round(100 * MIN_COHORT / own_pool, 2)},
                  {"programme": "OTH candidate (cyber central 39)", "intake": 39, "pool basis": "own pool",
                   "pool": round(own_pool), "implied share %": round(100 * 39 / own_pool, 2)},
                  {"programme": "OTH candidate (cyber central 39)", "intake": 39, "pool basis": "<= 100 km",
                   "pool": round(pool100), "implied share %": round(100 * 39 / pool100, 2)}]
    for label, (site, intake) in ANCHOR_SITES.items():
        share_rows.append({"programme": label, "intake": intake, "pool basis": "nearest-site pool (of the 5 sites)",
                           "pool": round(pools[site]), "implied share %": round(100 * intake / pools[site], 2)})
    shares = pd.DataFrame(share_rows)

    # 2. accessibility per candidate
    acc_rows = []
    demand_oth = access(pool)   # nearer OTH campus per county
    for key in ("cyber", "robotics_b", "arvr", "autonomous", "energydata", "geodata"):
        sites, nearest = candidate_sites(key)
        press_oth = competition_pressure(sites, *oth)
        row = {"candidate": key, "dedicated sites": sum(1 for s in sites if s[3] == 1.0),
               "focus sites": sum(1 for s in sites if s[3] < 1.0),
               "demand access at OTH": round(demand_oth, 1),
               "competition pressure at OTH": round(press_oth, 3),
               "demand per unit competition": round(demand_oth / press_oth, 0) if press_oth else float("inf")}
        if nearest is not None:
            name, la, lo = nearest
            row["nearest dedicated"] = f"{name} ({haversine(la, lo, *oth):.0f} km)"
            press_there = competition_pressure([s for s in sites if (s[1], s[2]) != (la, lo)], la, lo)
            demand_there = access(pool, la, lo)
            ratio = (demand_oth / press_oth) / (demand_there / press_there) if press_oth and press_there else float("nan")
            row["OTH advantage vs that site"] = round(ratio, 2)
        acc_rows.append(row)
    acc = pd.DataFrame(acc_rows)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.concat([shares.assign(table="shares"), acc.assign(table="accessibility")], ignore_index=True).to_csv(OUT, index=False)
    md = lambda df: "\n".join(["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
                              + ["| " + " | ".join("" if (isinstance(v, float) and np.isnan(v)) else str(v) for v in r) + " |"
                                 for r in df.itertuples(index=False)])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# Required capture share and competition accessibility (generated)", "",
        "Method, assumptions and limitations: module docstring (analysis/capture_benchmark.py).", "",
        "## Required vs demonstrated shares (qualified school leavers 2023/24, Bavaria)", "", md(shares), "",
        "Reading: the minimum cohort needs about "
        f"{shares.loc[0, 'implied share %']} % of OTH's own pool and the central cyber case about "
        f"{shares.loc[1, 'implied share %']} % ({shares.loc[2, 'implied share %']} % of the 100-km pool), while the"
        " Deggendorf anchor corresponds to about "
        f"{shares.loc[4, 'implied share %']} % of its equivalent nearest-site pool: the asked-for share is modest"
        " against a demonstrated peer value. THI's nearest-site pool is inflated by Munich falling to it"
        " (docs/evidence_catchment.md), so its share understates reality.", "",
        "## Accessibility per candidate (demand access d^-1.6 vs distance-weighted competitor sites)", "", md(acc), "",
        "Reading: a higher 'demand per unit competition' means more reachable school leavers per reachable competitor;",
        "'OTH advantage vs that site' > 1 means OTH's ratio beats the same index computed at the nearest dedicated",
        "competitor's own location (its competition excludes itself). Descriptive indices, not forecasts.", ""]),
        encoding="utf-8")
    pd.set_option("display.width", 250)
    print(shares.to_string(index=False)); print(); print(acc.to_string(index=False))
    print(f"Written: {OUT.relative_to(REPO_ROOT)}, {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
