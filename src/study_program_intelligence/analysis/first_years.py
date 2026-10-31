"""First-years per candidate through one shared code path, with the German / international split and the pool trend.

Run from the repository root (after analysis.cannibalisation and analysis.candidates):

    python -m study_program_intelligence.analysis.first_years

Inputs: configs/first_years.yaml. Gross steady-state intakes (low / central / high) and the origin shares (a) from OTH
programmes, (b) net new, (c) kept in region come unchanged from the Step 47/48 model (cyber: capture_scenarios.csv;
candidates: candidate_scenarios.csv). For every candidate the same steps follow:
1. German / international split: the German and foreign shares of the candidate's Bavarian subject pool in the last
   year of its window (Destatis, analysis/demand_split.py).
2. Trend: each group's yearly growth over the window (German and foreign apart) projects the gross intake from the
   window's last year to the first intake year and to steady state (year 3); for robotics path B the German pool
   falls by 3.3 % a year, which therefore lowers its German first-years.
3. Ramp-up 60 / 80 / 100 % (analysis/capture.py RAMP); year 1 = 60 % of the projected first-intake value.
4. Comparison with the assumed minimum cohort of 20 (analysis/capture.py MIN_COHORT).
Plus a rolling-origin backtest (analysis/forecast.py) of each pool's German AND foreign series, scored by MASE; the
foreign rows test the compounded foreign growth that the projection carries forward (e.g. cyber +12.8 %/yr), which
the original run left unvalidated (31 Oct review).
Outputs: data/interim/candidate_first_years.csv, data/interim/pool_backtest.csv, reports/first_years.md.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from .capture import MIN_COHORT, RAMP
from .demand_split import cagr, load as load_destatis
from .forecast import MAX_H, backtest

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG = REPO_ROOT / "configs" / "first_years.yaml"
INTERIM = REPO_ROOT / "data" / "interim"
OUT = INTERIM / "candidate_first_years.csv"
BACKTEST = INTERIM / "pool_backtest.csv"
REPORT = REPO_ROOT / "reports" / "first_years.md"
LEVELS = ("low", "central", "high")


def config() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def scenarios(key: str, c: dict) -> pd.DataFrame:
    """Gross steady-state intake and origin shares per scenario, as the Step 47/48 model produced them."""
    if c["scenarios"] == "capture_scenarios":
        s = pd.read_csv(INTERIM / "capture_scenarios.csv")
    else:
        s = pd.read_csv(INTERIM / "candidate_scenarios.csv")
        s = s[s["option"] == key].drop_duplicates("scenario")
    s = s.set_index("scenario").loc[list(LEVELS)]
    g = s["gross first-years"]
    return pd.DataFrame({"gross": g, "share a": s["(a) from OTH programmes"] / g, "share b": s["(b) net new to OTH"] / g,
                         "share c": s["(c) kept in region"] / g})


def pool(c: dict, long: pd.DataFrame) -> dict:
    """German / foreign mix in the window's last year and each group's yearly growth over the window (Bavaria)."""
    p, (y0, y1) = c["pool"], c["pool"]["window"]
    d = long[(long["kind"] == p["kind"]) & (long["region"] == "BY") & long["code"].isin(p["codes"])]
    t = d.pivot_table(index="year", columns="nationality", values="value", aggfunc="sum")
    tot = t.loc[y1, "German"] + t.loc[y1, "foreign"]
    return {"base year": y1, "German share": t.loc[y1, "German"] / tot, "foreign share": t.loc[y1, "foreign"] / tot,
            "German %/yr": cagr(t.loc[y0, "German"], t.loc[y1, "German"], y1 - y0),
            "foreign %/yr": cagr(t.loc[y0, "foreign"], t.loc[y1, "foreign"], y1 - y0)}


def project(gross: float, pl: dict, year: int) -> tuple[float, float]:
    """German and international first-years in `year` from a gross intake at the pool's base-year level."""
    n = year - pl["base year"]
    return (gross * pl["German share"] * (1 + pl["German %/yr"] / 100) ** n,
            gross * pl["foreign share"] * (1 + pl["foreign %/yr"] / 100) ** n)


def first_years(key: str, c: dict, long: pd.DataFrame, first_year: int) -> list[dict]:
    sc, pl = scenarios(key, c), pool(c, long)
    rows = []
    for level in LEVELS:
        r = sc.loc[level]
        for phase, year, ramp in (("year 1", first_year, RAMP[0]), ("steady state", first_year + len(RAMP) - 1, RAMP[-1])):
            de, intl = project(r["gross"], pl, year)
            de, intl = de * ramp, intl * ramp
            gross = de + intl
            rows.append({"candidate": key, "scenario": level, "phase": phase, "intake year": year,
                         "gross (model, base year)": round(r["gross"] * ramp, 1), "gross": round(gross, 1),
                         "German": round(de, 1), "international": round(intl, 1),
                         "net new to OTH": round(gross * r["share b"], 1), "from OTH programmes": round(gross * r["share a"], 1),
                         "kept in region": round(gross * r["share c"], 1),
                         f"meets minimum {MIN_COHORT}": bool(gross >= MIN_COHORT)})
    return rows


def pool_inputs(cfg: dict, long: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([{"candidate": k, "pool": "+".join(c["pool"]["codes"]) + f" ({c['pool']['kind']})",
                          **{kk: (round(v, 3) if isinstance(v, float) else v) for kk, v in pool(c, long).items()}}
                         for k, c in cfg["candidates"].items()])


def pool_backtest(cfg: dict, long: pd.DataFrame) -> pd.DataFrame:
    """Rolling-origin backtest (analysis/forecast.py) of each pool's German and foreign series in Bavaria; MASE per
    model. The foreign rows test the compounded foreign growth the projection carries to 2030, which the original
    run left unvalidated (31 Oct review)."""
    rows = []
    for key, c in cfg["candidates"].items():
        p, last = c["pool"], c["pool"]["window"][1]
        for nat in ("German", "foreign"):
            d = long[(long["kind"] == p["kind"]) & (long["region"] == "BY") & (long["nationality"] == nat)]
            y = d[d["code"].isin(p["codes"])].groupby("year")["value"].sum()
            total = d.groupby("year")["value"].sum()
            bt = backtest(y, total, last)
            m = bt.groupby("model")["ase"].mean()
            stat = m.drop(index="share (actual total)")
            rows.append({"candidate": key, "group": nat, "series": f"BY {nat} {p['kind']} " + "+".join(p["codes"]),
                         "origins": f"{bt['origin'].min()}-{bt['origin'].max()}", "horizons": f"1-{MAX_H}",
                         **{f"MASE {k}": round(v, 2) for k, v in m.items()}, "best statistical model": stat.idxmin(),
                         "best MASE": round(stat.min(), 2), "beats naive scale (MASE < 1)": bool(stat.min() < 1)})
    return pd.DataFrame(rows)


def _md(df: pd.DataFrame) -> str:
    fmt = lambda v: ("yes" if v else "no") if isinstance(v, bool) else str(v)
    return "\n".join(["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
                     + ["| " + " | ".join(fmt(v) for v in r) + " |" for r in df.itertuples(index=False)])


def main() -> None:
    cfg, long = config(), load_destatis()
    fy = pd.DataFrame(sum((first_years(k, c, long, cfg["first_intake_year"]) for k, c in cfg["candidates"].items()), []))
    pin, bt = pool_inputs(cfg, long), pool_backtest(cfg, long)
    fy.to_csv(OUT, index=False)
    bt.to_csv(BACKTEST, index=False)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(["# First-years per candidate (generated)", "", "Config: configs/first_years.yaml.", "",
                                 "## Pool inputs (Bavaria)", "", _md(pin), "", "## First-years", "", _md(fy), "",
                                 "## Rolling-origin backtest of the pool series (German and foreign)", "",
                                 "The foreign rows test the compounded foreign growth the projection carries to 2030.", "",
                                 _md(bt), ""]), encoding="utf-8")
    pd.set_option("display.width", 250)
    print(pin.to_string(index=False)); print(); print(fy.to_string(index=False)); print(); print(bt.to_string(index=False))


if __name__ == "__main__":
    main()
