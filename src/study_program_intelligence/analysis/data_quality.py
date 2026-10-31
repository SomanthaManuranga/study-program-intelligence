"""Data-quality gate for the tables the analyses consume (deep-analysis layer, docs/criteria_deep_analysis.md D7).

Run from the repository root:

    python -m study_program_intelligence.analysis.data_quality

Checks schema, ranges, completeness and cross-table arithmetic of the interim/processed tables. Every check is listed
in the report with its result; the module exits 1 if any check fails, so the pipeline stops on silent data damage.
Method: plain assertions on pandas frames (no sampling); the thresholds are structural facts (column sets, key
uniqueness, sums that the parsers already guaranteed once), not analysis choices.
Output: reports/data_quality.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
INTERIM = REPO_ROOT / "data" / "interim"
PROCESSED = REPO_ROOT / "data" / "processed"
REPORT = REPO_ROOT / "reports" / "data_quality.md"

CHECKS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    CHECKS.append((name, bool(ok), detail))


def counties() -> pd.DataFrame:
    g = pd.read_csv(INTERIM / "counties_geo.csv", dtype={"county": str, "land": str})
    check("counties: one row per county key", g["county"].is_unique, f"{len(g)} rows")
    check("counties: ~400 German counties", 380 <= len(g) <= 420, str(len(g)))
    check("counties: 96 Bavarian counties", int((g["land"] == "09").sum()) == 96, str(int((g["land"] == "09").sum())))
    check("counties: coordinates inside Germany", bool(g["lat"].between(47, 55.3).all() and g["lon"].between(5.5, 15.5).all()))
    check("counties: population positive", bool((g["pop"] > 0).all()))
    by_own = int((g["own_pool"] & (g["land"] == "09")).sum())
    check("counties: Bavarian own pool has 14 counties (docs/evidence_catchment.md)", by_own == 14,
          f"{by_own} Bavarian of {int(g['own_pool'].sum())} German counties where OTH is the nearest of the four sites")
    return g


def leavers(geo: pd.DataFrame) -> pd.DataFrame:
    lv = pd.read_csv(INTERIM / "school_leavers_by.csv", dtype={"key": str})
    years = sorted(lv["year"].unique())
    check("leavers: report years 2014-2024 without 2019", years == [2014, 2015, 2016, 2017, 2018, 2020, 2021, 2022, 2023, 2024], str(years))
    ok_sum = True
    for y, d in lv.groupby("year"):
        bav = d[d["key"] == "09"]["hzb_total"].iloc[0]
        cty = d[d["key"].str.len() == 5]["hzb_total"].sum()
        ok_sum &= int(bav) == int(cty)
    check("leavers: county totals sum to Bavaria in every year", ok_sum)
    check("leavers: every county key exists in the geo table",
          set(lv.loc[lv["key"].str.len() == 5, "key"]) <= set(geo["county"]))
    check("leavers: hzb_total = Abitur + FOS/BOS + general-school FHR",
          bool((lv["hzb_total"] == lv["abitur_gym"] + lv["fos_bos"] + lv["gen_fhr"]).all()))
    return lv


def demand_split() -> None:
    ds = pd.read_csv(INTERIM / "demand_split.csv")
    check("demand split: exactly the two nationalities", set(ds["nationality"]) == {"German", "foreign"})
    check("demand split: values non-negative", bool((ds["value"].fillna(0) >= 0).all()))
    p = ds[(ds["kind"] == "first-years") & (ds["region"] == "BY") & ds["code"].isin(["SF079", "SF123", "SF200"])
           & (ds["year"] == 2024)]["value"].sum()
    check("demand split: Bavarian cyber proxy 2024 equals the forecast anchor (4,936)", int(p) == 4936, str(int(p)))
    pairs = ds.pivot_table(index=["region", "kind", "code", "year"], columns="nationality", values="value", aggfunc="size")
    check("demand split: German/foreign pair complete per series-year", bool(pairs.notna().all(axis=None)))


def scenarios() -> None:
    cap = pd.read_csv(INTERIM / "capture_scenarios.csv")
    check("capture scenarios: low/central/high present", set(cap["scenario"]) == {"low", "central", "high"})
    close = (cap["(a) from OTH programmes"] + cap["(b) net new to OTH"] - cap["gross first-years"]).abs() <= 0.11
    check("capture scenarios: (a) + (b) = gross", bool(close.all()))
    opt = pd.read_csv(INTERIM / "option_scenarios.csv")
    check("option scenarios: three options complete",
          set(opt["option"]) == {"cyber_bsc", "robotics_bsc", "cyber_msc"} and len(opt) == 9)
    cand = pd.read_csv(INTERIM / "candidate_scenarios.csv")
    check("candidate scenarios: six candidates complete", cand["option"].nunique() == 6 and len(cand) == 18)
    check("candidate scenarios: net-new share in [0, 1]", bool(cand["net-new share"].between(0, 1).all()))


def catalogues() -> None:
    p = pd.read_csv(PROCESSED / "programmes.csv")
    check("catalogue (baseline): unique offer ids", p["programme_id"].is_unique, f"{len(p)} offers")
    check("catalogue (baseline): coordinates complete", bool(p[["lat", "lon"]].notna().all(axis=None)))
    f = pd.read_csv(PROCESSED / "programmes_full.csv")
    check("catalogue (full): unique offer ids", f["programme_id"].is_unique, f"{len(f)} offers")
    miss = int(f["km_oth"].isna().sum())
    check("catalogue (full): distances non-negative where coordinates exist", bool((f["km_oth"].dropna() >= 0).all()),
          f"{miss} offers without coordinates ({100 * miss / len(f):.1f} %)")
    check("catalogue (full): is_oth marks OTH offers", bool(f.loc[f["is_oth"], "institution"].str.contains("Amberg-Weiden").all()))


def generated() -> None:
    bt = pd.read_csv(INTERIM / "pool_backtest.csv")
    check("pool backtest: German and foreign rows for all four candidates",
          len(bt) == 8 and set(bt["group"]) == {"German", "foreign"})
    fy = pd.read_csv(INTERIM / "candidate_first_years.csv")
    check("first-years: German + international = gross", bool(((fy["German"] + fy["international"] - fy["gross"]).abs() <= 0.11).all()))


def main() -> int:
    geo = counties()
    leavers(geo)
    demand_split()
    scenarios()
    catalogues()
    generated()
    failed = [c for c in CHECKS if not c[1]]
    lines = ["# Data-quality gate (generated)", "",
             "Structural checks on the tables the analyses consume (docs/criteria_deep_analysis.md, D7).", "",
             "| check | result | detail |", "|---|---|---|"]
    lines += [f"| {n} | {'PASS' if ok else 'FAIL'} | {d} |" for n, ok, d in CHECKS]
    lines += ["", f"{len(CHECKS) - len(failed)} of {len(CHECKS)} checks pass." + (" FAILURES ABOVE." if failed else "")]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    for n, ok, d in CHECKS:
        print(("PASS " if ok else "FAIL "), n, ("- " + d if d else ""))
    print(f"Written: {REPORT.relative_to(REPO_ROOT)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
