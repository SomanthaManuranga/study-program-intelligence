"""Catchment of OTH Amberg-Weiden: school leavers with a university entrance qualification by county (Step 42).

Run from the repository root:

    python -m study_program_intelligence.analysis.catchment geo      # county centres, distances, nearest campus
    python -m study_program_intelligence.analysis.catchment run      # catchment sizes, overlap, trend, forecast
                                                                     # (needs transform.school_leavers first)

Method (decision log 2026-10-17)
- County centres: population-weighted mean of the municipality centre coordinates in the Destatis
  municipality directory (GV-ISys, 30.06.2026; population 31.12.2024). Straight-line (haversine) distances.
- OTH distance = nearer of the Amberg and Weiden campuses. Competitor locations = where their dedicated
  cybersecurity programmes are taught: TH Deggendorf (Deggendorf; its Cham campus is noted, not used),
  TH Ingolstadt, and the Nuremberg/Erlangen hub (nearer of FAU Erlangen and TH Nürnberg).
- "OTH's own pool": counties closer to OTH than to every competitor. Sensitivity: OTH Regensburg added as a
  competitor (51 km away; cybersecurity focus areas in Informatik/Wirtschaftsinformatik).
- School leavers (transform/school_leavers.py): Gymnasium Abitur (allgemeine Hochschulreife from general schools),
  FOS/BOS (Fachhochschulreife + Hochschulreife from vocational schools), combined (+ general-school
  Fachhochschulreife until 2021/22). Bavarian counties only (counts by school location; non-Bavarian counties
  within 150 km are listed, not counted).
- Forecast: 2023/24 catchment values x KMK Dok. 251 index for Bavaria (same category; KMK year 2025 = leavers of
  2024/25, the G9 gap year). Sensitivity: the catchment's own 2014-2024 growth gap to Bavaria continued.
Outputs: data/interim/counties_geo.csv, reports/catchment.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
GV = REPO_ROOT / "data" / "raw" / "regional" / "destatis_gv_auszug_2026q2.xlsx"
GEO = REPO_ROOT / "data" / "interim" / "counties_geo.csv"
LEAVERS = REPO_ROOT / "data" / "interim" / "school_leavers_by.csv"
KMK = REPO_ROOT / "data" / "raw" / "documents" / "kmk_dok251_landeswerte.xlsx"
REPORT = REPO_ROOT / "reports" / "catchment.md"
BANDS = (50, 100, 150)
METRICS = {"abitur_gym": "Gymnasium Abitur", "fos_bos": "FOS/BOS (FHR + HR)", "hzb_total": "All with university entrance qualification"}

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


def _md(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(f"{v:,.0f}" if isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, bool)
                             and float(v).is_integer() else str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(out)


def kmk_index() -> pd.DataFrame:
    """KMK Dok. 251 Bavaria: leavers by category, indexed later to the 2023/24 actuals."""
    x = pd.ExcelFile(KMK)
    out = {}
    for sh in ("A_ABS_AHR", "A_BBS_FHR", "A_BBS_HSR"):
        d = pd.read_excel(x, sheet_name=sh, header=None)
        h = d.index[d.iloc[:, 0].astype(str).str.strip() == "Jahr"][0]
        body = d.iloc[h + 1:].copy()
        body.columns = d.iloc[h].astype(str).str.strip()
        body = body[pd.to_numeric(body["Jahr"], errors="coerce").between(2000, 2100)]
        out[sh] = pd.Series(pd.to_numeric(body["BY"], errors="coerce").values, index=body["Jahr"].astype(int).values)
    k = pd.DataFrame(out).dropna()
    return pd.DataFrame({"abitur_gym": k["A_ABS_AHR"], "fos_bos": k["A_BBS_FHR"] + k["A_BBS_HSR"]})


def run() -> str:
    geo = counties()
    lv = pd.read_csv(LEAVERS, dtype={"key": str})
    cty = lv[lv["key"].str.len() == 5].merge(geo, left_on="key", right_on="county", how="left")
    bav = lv[lv["key"] == "09"].set_index("year")
    last, first, mid = cty["year"].max(), cty["year"].min(), 2018
    sets = {f"<= {b} km": cty["km_OTH"] <= b for b in BANDS}
    sets["Own pool (closer to OTH than to DEG, IN, N/ER)"] = cty["own_pool"]
    sets["Own pool, OTH Regensburg also a competitor"] = cty["own_pool_with_regensburg"]

    def total(mask, year, m="hzb_total"):
        return int(cty.loc[mask & (cty["year"] == year), m].sum())

    rows = []
    for name, mask in sets.items():
        rec = {"catchment": name, "counties": int(cty.loc[mask & (cty["year"] == last), "key"].nunique())}
        for m, lab in METRICS.items():
            rec[f"{lab} {last - 1}/{str(last)[2:]}"] = total(mask, last, m)
        a, z = total(mask, first), total(mask, last)
        rec[f"all: change {first - 1}/{str(first)[2:]}-{last - 1}/{str(last)[2:]} %"] = round((z / a - 1) * 100, 1)
        rec["share of Bavaria %"] = round(z / bav.at[last, "hzb_total"] * 100, 1)
        rows.append(rec)
    size = pd.DataFrame(rows)

    # overlap: OTH's <=100 km catchment, share closer to OTH than to each competitor
    c100 = cty["km_OTH"] <= 100
    ov = []
    for comp in [*COMPETITORS, "OTH Regensburg"]:
        closer = cty["km_OTH"] < cty[f"km_{comp}"]
        ov.append({"competitor": comp, "HZB in OTH <=100 km": total(c100, last),
                   "of which closer to OTH": total(c100 & closer, last),
                   "share closer to OTH %": round(total(c100 & closer, last) / total(c100, last) * 100, 1)})
    allc = cty["own_pool"]
    ov.append({"competitor": "all three (DEG, IN, N/ER)", "HZB in OTH <=100 km": total(c100, last),
               "of which closer to OTH": total(c100 & allc, last),
               "share closer to OTH %": round(total(c100 & allc, last) / total(c100, last) * 100, 1)})
    overlap = pd.DataFrame(ov)

    # each site's own pool (nearest of OTH and the three competitors; Bavaria), for comparison
    sites = ["OTH", *COMPETITORS]
    near = cty[[f"km_{s}" for s in sites]].idxmin(axis=1).str.removeprefix("km_")
    pools = pd.DataFrame([{"site": s, "counties": int(cty.loc[(near == s) & (cty["year"] == last), "key"].nunique()),
                           **{f"{lab}": int(cty.loc[(near == s) & (cty["year"] == last), m].sum()) for m, lab in METRICS.items()},
                           f"all: change since {first - 1}/{str(first)[2:]} %":
                               round((cty.loc[(near == s) & (cty["year"] == last), "hzb_total"].sum()
                                      / cty.loc[(near == s) & (cty["year"] == first), "hzb_total"].sum() - 1) * 100, 1)}
                          for s in sites])

    # time series
    years = sorted(cty["year"].unique())
    ts = pd.DataFrame({"school year": [f"{y - 1}/{str(y)[2:]}" for y in years]})
    own = cty["own_pool"]
    for m, lab in METRICS.items():
        ts[f"own pool: {lab}"] = [total(own, y, m) for y in years]
    ts["<= 100 km: all"] = [total(c100, y) for y in years]
    ts["Bavaria: all"] = [int(bav.at[y, "hzb_total"]) for y in years]
    ts["own pool / Bavaria %"] = (ts["own pool: All with university entrance qualification"] / ts["Bavaria: all"] * 100).round(2)

    # forecast
    k = kmk_index()
    base_bav = {m: bav.at[last, m] for m in ("abitur_gym", "fos_bos")}
    fc = []
    for y in (2025, 2026, 2028, 2030, 2035):
        rec = {"leaving year": f"{y - 1}/{str(y)[2:]}"}
        for nm, mask in (("own pool", own), ("<= 100 km", c100)):
            v = sum(total(mask, last, m) * k.at[y, m] / base_bav[m] for m in ("abitur_gym", "fos_bos"))
            rec[f"{nm}: Abitur + FOS/BOS"] = round(v)
        rec["Bavaria (KMK): Abitur + FOS/BOS"] = round(k.at[y, "abitur_gym"] + k.at[y, "fos_bos"])
        fc.append(rec)
    fc = pd.DataFrame(fc)
    own_cagr = (total(own, last) / total(own, first)) ** (1 / (last - first)) - 1
    bav_cagr = (bav.at[last, "hzb_total"] / bav.at[first, "hzb_total"]) ** (1 / (last - first)) - 1
    gap = own_cagr - bav_cagr
    fc["own pool, sensitivity (own trend gap continued)"] = [round(r * (1 + gap) ** (int(s[:4]) + 1 - last))
                                                              for r, s in zip(fc["own pool: Abitur + FOS/BOS"], fc["leaving year"])]

    # school location vs residence: kreisfreie Stadt and nearest Landkreis in different sets
    cities = geo[(geo["land"] == "09") & geo["county"].str[3].isin(["6"])]
    flags = []
    for c in cities.itertuples():
        lk = geo[(geo["land"] == "09") & (geo["county"].str[3] == "7")].assign(
            d=lambda x: haversine(x["lat"], x["lon"], c.lat, c.lon)).nsmallest(1, "d").iloc[0]
        if bool(c.own_pool) != bool(lk["own_pool"]):
            flags.append(f"{c.county_name} (pool: {c.own_pool}) / Landkreis {lk['county_name']} (pool: {lk['own_pool']})")
    non_by = geo[(geo["land"] != "09") & (geo["km_OTH"] <= 150)]

    return "\n".join([
        "# Catchment of OTH Amberg-Weiden (generated)", "",
        f"School leavers by Bavarian county and school location, {first - 1}/{str(first)[2:]} to {last - 1}/{str(last)[2:]} "
        "(2018/19 missing: edition not in the archive). Source: Statistische Berichte B I/II 1 j, Tabelle 5.", "",
        "## Catchment size", "", _md(size), "",
        "## Overlap: OTH's <= 100 km catchment closer to OTH than to each competitor", "", _md(overlap), "",
        "## Pools if each student chose the nearest of OTH, TH Deggendorf, TH Ingolstadt, Nuremberg/Erlangen", "", _md(pools), "",
        "## Time series", "", _md(ts), "",
        f"## Forecast (KMK Dok. 251 index for Bavaria applied; own-pool trend gap {gap * 100:+.2f} %-points/yr for the sensitivity)", "",
        _md(fc), "",
        "## Notes", "",
        f"- City/Landkreis pairs split across the own-pool boundary (school location effect): {'; '.join(flags) or 'none'}.",
        f"- Not counted (outside Bavaria, within 150 km): {len(non_by)} counties, population {int(non_by['pop'].sum()):,} "
        f"({', '.join(non_by.sort_values('km_OTH')['county_name'].head(8))}, ...).", ""])


def main(argv: list[str]) -> None:
    if argv[:1] == ["run"]:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(run(), encoding="utf-8")
        print(f"Written: {REPORT.relative_to(REPO_ROOT)}")
        return
    if argv[:1] != ["geo"]:
        sys.exit("Usage: python -m study_program_intelligence.analysis.catchment geo | run")
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
