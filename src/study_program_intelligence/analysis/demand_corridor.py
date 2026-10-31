"""Demand corridors to 2030 per candidate pool, from the rolling-origin backtest errors (deep-analysis layer).

Run from the repository root:

    python -m study_program_intelligence.analysis.demand_corridor

Purpose: the three-level answer projects steady-state first-years with each pool's 2019-24 growth carried to 2030.
The backtests (reports/first_years.md) say how much such projections can be trusted: the German cyber pool is the
only one where a trend model beats the naive scale (drift MASE 0.92); the German robotics pool is best served by the
naive level (MASE 1.30), and the foreign pools are far from forecastable (cyber best 4.22). This module turns that
into honest CORRIDORS instead of points:

- German component: the best backtested model's point forecast for 2030 with an empirical 80 % band from that
  model's own rolling-origin relative errors (largest tested horizon, scaled by sqrt(6/5) for the 6-year step, the
  convention of analysis/forecast.py).
- Foreign component: no validated model, so a SCENARIO band - lower bound the 2024 level held flat, upper bound the
  2019-24 growth compounded to 2030 (the three-level table's projection).
- First-years corridor: the pre-registered central gross, scaled by the pool corridor relative to the 2024 pool.

Assumptions and limits, stated: the corridor inherits the capture model's base-year anchoring (intake moves
proportionally with the pool); the error bands come from 12 overlapping origins, so they are indicative; the foreign
band is a scenario range, not a confidence interval; graduates (master pipeline) use window 2019-2025 and a 5-year
step to 2030.

Outputs: data/interim/demand_corridor.csv, reports/demand_corridor.md.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .forecast import MODELS, backtest

REPO_ROOT = Path(__file__).resolve().parents[3]
INTERIM = REPO_ROOT / "data" / "interim"
OUT = INTERIM / "demand_corridor.csv"
REPORT = REPO_ROOT / "reports" / "demand_corridor.md"
TARGET = 2030
POOLS = {   # candidate: (kind, codes, window, pre-registered central gross at base year)
    "cyber": ("first-years", ["SF079", "SF123", "SF200"], (2019, 2024), 39.0),
    "robotics_b": ("first-years", ["SF380", "SF123"], (2019, 2024), 28.7),
    "arvr": ("first-years", ["SF121"], (2019, 2024), 58.5),
    "ot_master": ("graduates", ["SF079"], (2019, 2025), 42.9),
}


def series(kind: str, codes: list[str], nat: str) -> tuple[pd.Series, pd.Series]:
    ds = pd.read_csv(INTERIM / "demand_split.csv")
    d = ds[(ds["kind"] == kind) & (ds["region"] == "BY") & (ds["nationality"] == nat)]
    y = d[d["code"].isin(codes)].groupby("year")["value"].sum()
    total = d.groupby("year")["value"].sum()
    return y, total


def german_corridor(kind: str, codes: list[str], last: int) -> dict:
    y, total = series(kind, codes, "German")
    bt = backtest(y, total, last)
    m = bt[bt["model"].isin(["naive", "drift", "ets"])].groupby("model")["ase"].mean()
    best = str(m.idxmin())
    h = TARGET - last
    point = float(MODELS[best](y[y.index <= last], h)[-1])
    rel = bt[(bt["model"] == best) & (bt["h"] == bt["h"].max())]["rel_error"]
    scale = np.sqrt(h / bt["h"].max())
    q10, q90 = float(np.quantile(rel, 0.1)) * scale, float(np.quantile(rel, 0.9)) * scale
    return {"base": float(y.loc[last]), "model": best, "mase": round(float(m.min()), 2),
            "point": point, "lo": point / (1 + q90), "hi": point / (1 + q10)}


def foreign_scenario(kind: str, codes: list[str], window: tuple[int, int]) -> dict:
    y, _ = series(kind, codes, "foreign")
    y0, y1 = window
    g = (y.loc[y1] / y.loc[y0]) ** (1 / (y1 - y0)) - 1
    return {"base": float(y.loc[y1]), "flat": float(y.loc[y1]), "cagr": float(y.loc[y1] * (1 + g) ** (TARGET - y1)),
            "g": 100 * g}


def main() -> None:
    rows = []
    for cand, (kind, codes, window, gross) in POOLS.items():
        last = window[1]
        de = german_corridor(kind, codes, last)
        fo = foreign_scenario(kind, codes, window)
        pool_base = de["base"] + fo["base"]
        lo, hi = de["lo"] + fo["flat"], de["hi"] + fo["cagr"]
        point = de["point"] + fo["flat"]   # conservative point: validated German path, foreign held flat
        rows.append({"candidate": cand, "pool": f"{kind} {'+'.join(codes)}",
                     "pool 2024/25 (German + foreign)": f"{de['base']:.0f} + {fo['base']:.0f}",
                     "German 2030: model": f"{de['model']} (MASE {de['mase']})",
                     "German 2030: point (80 % bias-corrected band)": f"{de['point']:.0f} ({de['lo']:.0f}-{de['hi']:.0f})",
                     "foreign 2030: scenario band": f"{fo['flat']:.0f}-{fo['cagr']:.0f} (+{fo['g']:.1f} %/yr compounded)",
                     "pool 2030 corridor": f"{lo:.0f}-{hi:.0f}",
                     "central gross at base year": gross,
                     "first-years 2030 corridor (central)": f"{gross * lo / pool_base:.1f}-{gross * hi / pool_base:.1f}",
                     "first-years 2030, conservative point": round(gross * point / pool_base, 1)})
    t = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT, index=False)
    md = "\n".join(["| " + " | ".join(map(str, t.columns)) + " |", "|" + "---|" * len(t.columns)]
                   + ["| " + " | ".join(str(v) for v in r) + " |" for r in t.itertuples(index=False)])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# Demand corridors to 2030 (generated)", "",
        "Method, assumptions and limitations: module docstring (analysis/demand_corridor.py). The corridor's lower",
        "bound combines the German band's low end with the foreign pool held flat; the upper bound combines the",
        "German high end with the compounded foreign growth (the three-level table's projection). The conservative",
        "point uses the validated German path and holds the foreign pool flat. The German bands are bias-corrected",
        "from the model's own backtest errors (the convention of docs/evidence_forecast.md), so a band can sit",
        "beside its point where the model historically over- or under-shot.", "",
        md, "",
        "Reading: the corridors replace single projected points. For cyber the conservative point already exceeds",
        "the base-year central (the validated German drift rises), so the argument does not need the unvalidated",
        "foreign compounding; for robotics path B the corridor stays near the base-year level, which supports",
        "treating its pool trend as an assumption rather than a forecast.", ""]), encoding="utf-8")
    pd.set_option("display.width", 250)
    print(t.to_string(index=False))
    print(f"Written: {OUT.relative_to(REPO_ROOT)}, {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
