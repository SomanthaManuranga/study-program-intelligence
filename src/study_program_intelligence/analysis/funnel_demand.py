"""Funnel step 4: are students coming? (configs/funnel.yaml: demand, pool_mapping; criteria in docs/criteria_funnel_step4.md)

Run from the repository root, from committed code on a clean tree, after analysis.funnel_units run:

    python -m study_program_intelligence.analysis.funnel_demand

For every unit of Step 3 (both lists): the German first-years (master: graduates) of its subject pool in Bavaria and
in Germany, the slope 2019-2024 (2019-2025), the backtests of the pool, a projection to 2030 with one model for all
pools, and foreign students as a corridor. The numbers are those of the subject pool, not of the programme type. No
unit is removed here.
Outputs: data/interim/funnel2_demand.csv, funnel2_pools.csv, funnel2_step4.json; reports/funnel2/step4_demand.md.
"""

from __future__ import annotations

import json
import warnings

import numpy as np
import pandas as pd

from .forecast import f_drift, f_ets, f_naive
from .funnel_common import INTERIM, REPORTS, config, md_table, run_stamp
from .funnel_types import OFFER_TYPES, sha
from .funnel_units import DESTATIS, LEVELS, SCREEN, SERIES, STEP3, SUBJECT_MAP, backtest, file_hash, pool_series, pool_weights, slope_pct

DEMAND, POOLS, STEP4 = INTERIM / "funnel2_demand.csv", INTERIM / "funnel2_pools.csv", INTERIM / "funnel2_step4.json"
MODELS = {"naive": f_naive, "drift": f_drift, "ets": f_ets}
MIN_TRAIN = 5          # training years every model needs for the comparison of the three models


def tables() -> dict[tuple[str, str], pd.DataFrame]:
    """Destatis by region (BY, DE) and nationality (German, foreign): index (kind, year), columns subject codes."""
    from .demand_split import load
    long = load()
    return {(r, n): long[(long["region"] == r) & (long["nationality"] == n)].pivot_table(index=["kind", "year"], columns="code", values="value", aggfunc="sum")
            for r in ("BY", "DE") for n in ("German", "foreign")}


def run_of_years(y: pd.Series, last: int) -> pd.Series:
    """The longest run of consecutive years with a positive value that ends in `last` (empty if the last year is missing)."""
    y = y[(y.index <= last) & (y > 0)].dropna().sort_index()
    if y.empty or y.index[-1] != last:
        return y.iloc[:0]
    gaps = np.where(np.diff(y.index) != 1)[0]
    return y.iloc[gaps[-1] + 1:] if len(gaps) else y


def compare_models(y: pd.Series, last: int, rule: dict) -> dict[str, float]:
    """Rule demand.backtest for the model choice: per model the MASE averaged over the horizons 1 to 5 (each horizon the
    mean over the rolling origins from origins_from). Every model sees the same origins; an origin needs MIN_TRAIN
    training years. Empty if the pool has fewer than min_series years."""
    y = run_of_years(y, last)
    if len(y) < int(str(rule["min_series"]).split()[0]):
        return {}
    err = {m: {h: [] for h in rule["backtest"]["horizons"]} for m in MODELS}
    for origin in range(max(rule["backtest"]["origins_from"], int(y.index[0]) + MIN_TRAIN - 1), last):
        train = y[y.index <= origin]
        scale = train.diff().abs().mean()
        h_max = min(max(rule["backtest"]["horizons"]), last - origin)
        if not scale > 0 or h_max < 1:
            continue
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pred = {m: np.asarray(f(train, h_max), float) for m, f in MODELS.items()}
        for h in range(1, h_max + 1):
            for m in MODELS:
                err[m][h].append(abs(pred[m][h - 1] - y.loc[origin + h]) / scale)
    if not any(err["naive"].values()):
        return {}
    return {m: float(np.mean([np.mean(v) for v in e.values() if v])) for m, e in err.items()}


def project(y: pd.Series, last: int, year: int, model: str) -> float:
    """The chosen model fitted on the pool's run of years up to `last` and projected to `year` (not below 0)."""
    y = run_of_years(y, last)
    if len(y) < 3:
        return float("nan")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return float(max(0.0, np.asarray(MODELS[model](y, year - last), float)[-1]))


def corridor(last_value: float, slope: float, years: int) -> tuple[float, float]:
    """Rule demand.foreign: from flat to compounded growth at the window's slope; the lower and the higher of the two."""
    if not np.isfinite(last_value):
        return float("nan"), float("nan")
    grown = last_value * (1 + slope / 100) ** years if np.isfinite(slope) else last_value
    return float(min(last_value, grown)), float(max(last_value, grown))


def main() -> None:
    stamp, rules = run_stamp(), config()
    rule, year = rules["demand"], int(rules["demand"]["horizon_year"])
    step3 = json.loads(STEP3.read_text(encoding="utf-8"))
    if step3["files"][SCREEN.name] != sha(SCREEN) or step3["files"][OFFER_TYPES.name] != sha(OFFER_TYPES):
        raise SystemExit("the screen table or the offer table is not the one Step 3 wrote")
    s = pd.read_csv(SCREEN, float_precision="round_trip")
    d = pd.read_csv(OFFER_TYPES, low_memory=False, dtype={"programme_id": str})
    smap = pd.read_csv(SUBJECT_MAP).set_index("label")["code"].to_dict()
    tab = tables()
    rows, pool_of, pools = [], {}, {}
    for r in s.itertuples():
        kind, y0, y1, last = SERIES[r.level]
        a = d[(d["assigned_type"] == r.type) & (d["level"] == r.level)]
        w = pool_weights(a, smap)
        key = (kind, tuple(sorted((k, round(v, 6)) for k, v in w.items())))
        series = {k: pool_series(t.loc[kind], w) for k, t in tab.items()}
        if key not in pools:
            pools[key] = {"pool id": len(pools), "kind": kind, "subjects": len(w), "pool": "; ".join(f"{k}:{v:.2f}" for k, v in sorted(w.items(), key=lambda kv: (-kv[1], kv[0]))[:4]),
                          **{f"MASE {m}": v for m, v in compare_models(series[("BY", "German")], last, rule).items()}}
        pool_of[r.Index] = pools[key]["pool id"]
        by, bt = series[("BY", "German")], backtest(series[("BY", "German")], last, rule)
        foreign = series[("BY", "foreign")]
        slopes = {f"trend {n} {reg} %/yr": slope_pct(series[(reg, n)], y0, y1) for reg in ("BY", "DE") for n in ("German", "foreign")}
        value = lambda x, yr: float(x.get(yr, np.nan))
        rows.append({"type": r.type, "level": r.level, "kind": r.kind, "central titles": s.at[r.Index, "central titles"],
                     "primary": bool(r.primary), "stress": bool(r.stress), "pool id": pools[key]["pool id"], "pool": pools[key]["pool"], "series": kind,
                     f"German {last} BY": value(by, last), f"German {last} DE": value(series[("DE", "German")], last), **slopes,
                     "backtest years": bt["years"], "MASE naive": bt["naive"], "MASE drift": bt["drift"], "trend validated": bt["validated"],
                     "foreign last BY": value(foreign, last), "foreign share last BY": value(foreign, last) / (value(foreign, last) + value(by, last)) if value(by, last) + value(foreign, last) > 0 else np.nan,
                     "window": f"{y0}-{y1}", "last year": last})
    out = pd.DataFrame(rows)
    pool_table = pd.DataFrame(pools.values())
    pool_table["units"] = pool_table["pool id"].map(pd.Series(pool_of).value_counts()).fillna(0).astype(int)
    tested = pool_table.dropna(subset=["MASE naive"])
    averages = {m: float(tested[f"MASE {m}"].mean()) for m in MODELS}
    model = min(averages, key=lambda m: (averages[m], list(MODELS).index(m)))
    proj, low, high = [], [], []
    for r in out.itertuples():
        kind, y0, y1, last = SERIES[r.level]
        a = d[(d["assigned_type"] == r.type) & (d["level"] == r.level)]
        w = pool_weights(a, smap)
        proj.append(project(pool_series(tab[("BY", "German")].loc[kind], w), last, year, model))
        lo, hi = corridor(out.at[r.Index, "foreign last BY"], out.at[r.Index, "trend foreign BY %/yr"], year - last)
        low.append(lo)
        high.append(hi)
    out[f"German {year} BY ({model})"], out[f"foreign {year} BY low"], out[f"foreign {year} BY high"] = proj, low, high
    out["units sharing the pool"] = out["pool id"].map(out["pool id"].value_counts())
    out.to_csv(DEMAND, index=False)
    pool_table.to_csv(POOLS, index=False)

    prim = out[out["primary"]]
    slope = prim["trend German BY %/yr"]
    bands = {"growing (0 or more)": int((slope >= 0).sum()), "falling slowly (0 to -3)": int(((slope < 0) & (slope >= -3)).sum()),
             "falling fast (below -3)": int((slope < -3).sum()), "no slope (a year without students)": int(slope.isna().sum())}
    res = {"stamp": stamp, "step3_commit": step3["stamp"]["commit"], "units": len(out), "primary": int(out["primary"].sum()), "stress": int(out["stress"].sum()),
           "distinct_pools": len(pool_table), "pools_backtested": len(tested), "pools_not_backtested": int(len(pool_table) - len(tested)),
           "average_MASE": {m: round(v, 3) for m, v in averages.items()}, "model_for_the_projection": model, "horizon_year": year,
           "pools_validated": int(((tested["MASE drift"] < tested["MASE naive"]) & (tested["MASE drift"] < 1)).sum()),
           "units_validated": int(out["trend validated"].sum()), "primary_validated": int(prim["trend validated"].sum()),
           "primary_by_trend_in_bavaria": bands,
           "primary_by_trend_in_germany": {"growing (0 or more)": int((prim["trend German DE %/yr"] >= 0).sum()), "falling": int((prim["trend German DE %/yr"] < 0).sum()),
                                           "no slope": int(prim["trend German DE %/yr"].isna().sum())},
           "primary_median_trend": {"German BY": round(float(slope.median()), 2), "German DE": round(float(prim["trend German DE %/yr"].median()), 2),
                                    "foreign BY": round(float(prim["trend foreign BY %/yr"].median()), 2), "foreign DE": round(float(prim["trend foreign DE %/yr"].median()), 2)},
           "primary_units_alone_in_their_pool": int((prim["units sharing the pool"] == 1).sum()),
           "primary_median_foreign_share": round(float(prim["foreign share last BY"].median()), 3),
           "inputs": {SCREEN.name: sha(SCREEN), OFFER_TYPES.name: sha(OFFER_TYPES), SUBJECT_MAP.name: sha(SUBJECT_MAP), "destatis tables": file_hash(DESTATIS.glob("213*.csv"))},
           "files": {p.name: sha(p) for p in (DEMAND, POOLS)}}
    STEP4.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    show = ["type", "level", "central titles", "pool", "units sharing the pool", "German 2024 BY", "German 2025 BY", "trend German BY %/yr", "trend German DE %/yr",
            "trend foreign BY %/yr", "trend validated", f"German {year} BY ({model})", "foreign share last BY"]
    head = prim.sort_values("trend German BY %/yr", ascending=False)
    cut = lambda x: x.assign(**{"central titles": x["central titles"].str.slice(0, 70)})[[c for c in show if c in x.columns]].round(2)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "step4_demand.md").write_text("\n".join([
        "# Funnel step 4: student trend of every unit's subject pool (generated)", "",
        f"Code commit {stamp['commit']} (screen: {res['step3_commit']}), run on {stamp['date']}, tracked files clean: {stamp['clean']}.", "",
        f"- Units: {len(out)} (primary list {res['primary']}, stress list {res['stress']}); distinct pools: {res['distinct_pools']}, backtested {res['pools_backtested']}.",
        f"- Average MASE over the backtested pools and the horizons 1 to 5: {res['average_MASE']}; model for the projection to {year}: {model}.",
        f"- Validated trends (drift beats naive and MASE below 1): {res['pools_validated']} pools, {res['units_validated']} units, {res['primary_validated']} on the primary list.",
        f"- Primary list, German trend in Bavaria: {bands}; in Germany: {res['primary_by_trend_in_germany']}; medians: {res['primary_median_trend']}.",
        "- The numbers are those of the subject pool (Destatis subjects weighted by the unit's offers), not of the programme type.", "",
        "## Primary list, by German trend in Bavaria", "", md_table(cut(head)), "", "## Pools", "", md_table(pool_table.round(3))]) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
