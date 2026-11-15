"""Funnel step 4: student trend (configs/funnel.yaml: demand; docs/criteria_funnel_step4.md). The tests on generated
files recompute from the Destatis tables; they are skipped where the git-ignored data is missing."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from study_program_intelligence.analysis import funnel_demand as D

REPO = Path(__file__).resolve().parents[1]
INTERIM = REPO / "data" / "interim"
RULE = yaml.safe_load((REPO / "configs" / "funnel.yaml").read_text(encoding="utf-8"))["demand"]
needs = lambda *files: pytest.mark.skipif(not all((INTERIM / f).exists() for f in files), reason="no generated data")
years = range(2005, 2025)


def test_run_of_years_ends_in_the_last_year_and_stops_at_a_gap():
    y = pd.Series([5.0] * 20, index=years)
    y[2012] = 0.0
    assert list(D.run_of_years(y, 2024).index) == list(range(2013, 2025))
    assert D.run_of_years(y[y.index <= 2023], 2024).empty


def test_model_comparison_follows_the_rule():
    line = pd.Series([100.0 + 10 * i for i in range(20)], index=years)
    m = D.compare_models(line, 2024, RULE)
    assert m["drift"] == pytest.approx(0.0, abs=1e-9) and m["naive"] == pytest.approx(3.0)       # horizons 1 to 5 of a straight line: mean of 1..5
    assert set(m) == {"naive", "drift", "ets"}
    assert D.compare_models(line[line.index >= 2014], 2024, RULE) == {}                           # 11 years: not backtested


def test_projection_and_corridor():
    line = pd.Series([100.0 + 10 * i for i in range(20)], index=years)
    assert D.project(line, 2024, 2030, "naive") == pytest.approx(290.0)
    assert D.project(line, 2024, 2030, "drift") == pytest.approx(350.0)
    assert D.project(pd.Series([100.0 - 30 * i for i in range(4)], index=range(2021, 2025)), 2024, 2030, "drift") == 0.0     # never below 0
    assert D.corridor(100.0, 5.0, 6) == pytest.approx((100.0, 100.0 * 1.05 ** 6))
    assert D.corridor(100.0, -5.0, 6) == pytest.approx((100.0 * 0.95 ** 6, 100.0))
    assert all(np.isnan(x) for x in D.corridor(100.0, float("nan"), 6))                   # no slope: no corridor


@needs("funnel2_demand.csv", "funnel2_pools.csv", "funnel2_step4.json", "funnel2_screen.csv", "funnel2_offer_types.csv")
def test_every_unit_has_its_numbers_and_they_agree_with_step_3():
    r = json.loads((INTERIM / "funnel2_step4.json").read_text(encoding="utf-8"))
    out = pd.read_csv(INTERIM / "funnel2_demand.csv", float_precision="round_trip")
    s = pd.read_csv(INTERIM / "funnel2_screen.csv", float_precision="round_trip")
    pools = pd.read_csv(INTERIM / "funnel2_pools.csv")
    assert list(zip(out["type"], out["level"])) == list(zip(s["type"], s["level"])) and len(out) == r["units"] == 1285
    assert (out["primary"] == s["primary"]).all() and (out["stress"] == s["stress"]).all()
    assert np.allclose(out["trend German BY %/yr"], s["trend %/yr"], equal_nan=True) and (out["trend validated"] == s["trend validated"]).all()
    tested = pools.dropna(subset=["model comparison MASE naive"])
    averages = {m: tested[f"model comparison MASE {m}"].mean() for m in ("naive", "drift", "ets")}
    assert (out["trend validated"] == ((out["MASE drift"] < out["MASE naive"]) & (out["MASE drift"] < 1))).all()
    assert r["units_validated"] == int(out["trend validated"].sum()) and r["pools_validated"] == out.loc[out["trend validated"], "pool id"].nunique()
    assert min(averages, key=averages.get) == r["model_for_the_projection"] and len(pools) == r["distinct_pools"] and pools["units"].sum() == len(out)
    low, high, last = out["foreign 2030 BY low"], out["foreign 2030 BY high"], out["foreign last BY"]
    assert ((low <= last + 1e-9) & (last <= high + 1e-9))[low.notna()].all()                    # the corridor contains the flat value
    assert (low.isna() == out["trend foreign BY %/yr"].isna()).all()
    from study_program_intelligence.analysis.demand_split import load               # the slopes again, from the long Destatis table
    long = load()
    smap = pd.read_csv(REPO / "configs" / "funnel_subject_map.csv").set_index("label")["code"].to_dict()
    d = pd.read_csv(INTERIM / "funnel2_offer_types.csv", low_memory=False)
    for row in out.sample(40, random_state=0).itertuples():
        a = d[(d["assigned_type"] == row.type) & (d["level"] == row.level)]
        w = {}
        for sub in a["subjects"]:
            labels = [x.replace(" (grundständig)", "").replace(" (weiterführend)", "") for x in str(sub).split("; ")]
            for x in labels:
                w[smap[x]] = w.get(smap[x], 0) + 1 / len(labels) / len(a)
        kind, first, end = ("first-years", 2019, 2024) if row.level == "bachelor" else ("graduates", 2019, 2025)
        for region, nat, col in (("BY", "German", "trend German BY %/yr"), ("DE", "German", "trend German DE %/yr"), ("BY", "foreign", "trend foreign BY %/yr"), ("DE", "foreign", "trend foreign DE %/yr")):
            part = long[(long["region"] == region) & (long["nationality"] == nat) & (long["kind"] == kind) & long["year"].between(first, end) & long["code"].isin(w)]
            y = part.assign(v=part["value"].fillna(0) * part["code"].map(w)).groupby("year")["v"].sum().reindex(range(first, end + 1), fill_value=0.0)
            want = 100 * (np.exp(np.polyfit(y.index.to_numpy(float), np.log(y.to_numpy(float)), 1)[0]) - 1) if (y > 0).all() else float("nan")
            got = out.at[row.Index, col]
            assert (np.isnan(want) and np.isnan(got)) or got == pytest.approx(want, abs=1e-6), (row.type, row.level, col)
