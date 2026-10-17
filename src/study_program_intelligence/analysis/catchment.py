"""Catchment of OTH Amberg-Weiden: school leavers with a university entrance qualification by county (Step 42).

Run from the repository root:

    python -m study_program_intelligence.analysis.catchment geo      # county centres, distances, nearest campus

Method (decision log 2026-10-17)
- County centres: population-weighted mean of the municipality centre coordinates in the Destatis
  municipality directory (GV-ISys, 30.06.2026; population 31.12.2024). Straight-line (haversine) distances.
- OTH distance = nearer of the Amberg and Weiden campuses. Competitor locations = where their dedicated
  cybersecurity programmes are taught: TH Deggendorf (Deggendorf; its Cham campus is noted, not used),
  TH Ingolstadt, and the Nuremberg/Erlangen hub (nearer of FAU Erlangen and TH Nürnberg).
- "OTH's own pool": counties closer to OTH than to every competitor. Sensitivity: OTH Regensburg added as a
  competitor (51 km away; cybersecurity focus areas in Informatik/Wirtschaftsinformatik).
Outputs: data/interim/counties_geo.csv.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
GV = REPO_ROOT / "data" / "raw" / "regional" / "destatis_gv_auszug_2026q2.xlsx"
GEO = REPO_ROOT / "data" / "interim" / "counties_geo.csv"
BANDS = (50, 100, 150)

# Campus coordinates (median of the programme offers per location, data/processed/programmes.csv).
CAMPUS = {
    "OTH Amberg": (49.4425, 11.8558),
    "OTH Weiden": (49.6761, 12.1603),
    "TH Deggendorf": (48.8422, 12.9600),
    "TH Ingolstadt": (48.7656, 11.4233),
    "FAU Erlangen": (49.5950, 11.0050),
    "TH Nürnberg": (49.4508, 11.0753),
    "OTH Regensburg": (49.0178, 12.0975),
}
SITES = {  # site -> campuses (distance = nearest campus)
    "OTH": ["OTH Amberg", "OTH Weiden"],
    "TH Deggendorf": ["TH Deggendorf"],
    "TH Ingolstadt": ["TH Ingolstadt"],
    "FAU/TH Nürnberg": ["FAU Erlangen", "TH Nürnberg"],
    "OTH Regensburg": ["OTH Regensburg"],
}
COMPETITORS = ["TH Deggendorf", "TH Ingolstadt", "FAU/TH Nürnberg"]


def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 6371.0 * 2 * np.arcsin(np.sqrt(a))


def municipalities() -> pd.DataFrame:
    raw = pd.read_excel(GV, sheet_name=1, header=None, dtype=str, skiprows=6)
    raw = raw.iloc[:, [0, 2, 3, 4, 5, 6, 7, 9, 14, 15]]
    raw.columns = ["satzart", "land", "rb", "kreis", "vb", "gem", "name", "pop", "lon", "lat"]
    names = raw[raw["satzart"] == "40"].assign(county=lambda d: d["land"] + d["rb"] + d["kreis"])[["county", "name"]]
    g = raw[raw["satzart"] == "60"].copy()
    g["county"] = g["land"] + g["rb"] + g["kreis"]
    for c in ("pop",):
        g[c] = pd.to_numeric(g[c], errors="coerce")
    for c in ("lon", "lat"):
        g[c] = pd.to_numeric(g[c].str.replace(",", ".", regex=False), errors="coerce")
    g = g.dropna(subset=["pop", "lon", "lat"])
    return g.merge(names.rename(columns={"name": "county_name"}), on="county", how="left")


def counties() -> pd.DataFrame:
    g = municipalities()
    w = g.assign(wlat=g["lat"] * g["pop"], wlon=g["lon"] * g["pop"])
    c = w.groupby(["county", "county_name", "land"], as_index=False)[["pop", "wlat", "wlon"]].sum()
    c["lat"], c["lon"] = c["wlat"] / c["pop"], c["wlon"] / c["pop"]
    c = c.drop(columns=["wlat", "wlon"])
    for site, campuses in SITES.items():
        c[f"km_{site}"] = np.min([haversine(c["lat"], c["lon"], *CAMPUS[k]) for k in campuses], axis=0)
    comp = c[[f"km_{s}" for s in COMPETITORS]]
    c["nearest_competitor"] = comp.idxmin(axis=1).str.removeprefix("km_")
    c["km_nearest_competitor"] = comp.min(axis=1)
    c["own_pool"] = c["km_OTH"] < c["km_nearest_competitor"]
    c["own_pool_with_regensburg"] = c["own_pool"] & (c["km_OTH"] < c["km_OTH Regensburg"])
    c["band"] = pd.cut(c["km_OTH"], [0, *BANDS, np.inf], labels=[f"<={b} km" for b in BANDS] + [">150 km"], include_lowest=True)
    return c


def main(argv: list[str]) -> None:
    if argv[:1] != ["geo"]:
        sys.exit("Usage: python -m study_program_intelligence.analysis.catchment geo")
    c = counties()
    GEO.parent.mkdir(parents=True, exist_ok=True)
    c.to_csv(GEO, index=False)
    near = c[c["km_OTH"] <= 150]
    print(f"Counties: {len(c)} in Germany; within 150 km of OTH: {len(near)} "
          f"({int((near['land'] == '09').sum())} Bavarian, {int((near['land'] != '09').sum())} other Länder)")
    print(near.groupby("band", observed=True).agg(counties=("county", "size"), population=("pop", "sum")).to_string())
    print("Own pool (closer to OTH than to Deggendorf/Ingolstadt/Nuremberg hub):",
          int(near["own_pool"].sum()), "counties;", "with OTH Regensburg as competitor:", int(near["own_pool_with_regensburg"].sum()))
    print(f"Written: {GEO.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
