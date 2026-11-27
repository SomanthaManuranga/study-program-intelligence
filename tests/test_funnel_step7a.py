"""Funnel step 7a: the order of the gate (configs/funnel.yaml: shortlist; docs/criteria_funnel_step7.md)."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from study_program_intelligence.analysis import funnel_shortlist as S

REPO = Path(__file__).resolve().parents[1]
INTERIM = REPO / "data" / "interim"
needs = lambda *files: pytest.mark.skipif(not all((REPO / f).exists() for f in files), reason="no generated data")
VF = S.config()["ranking"]["value_functions"]


def test_value_functions_are_those_of_the_rule():
    assert list(S.value([-5, -3, 0, 1.5, 3, 9, np.nan], VF["trend_pct_per_year"])) == pytest.approx([1, 1, 3, 4, 5, 5, 1])
    assert list(S.value([0, 10, 25, 40, 100], VF["net_new"])) == pytest.approx([1, 1, 3, 5, 5])
    assert list(S.value([0, 10, 150, 5000], VF["labour_ads_within_100km_log"], log=True)) == pytest.approx([1, 1, 5, 5])
    assert float(S.value([np.sqrt(1500)], VF["labour_ads_within_100km_log"], log=True)[0]) == pytest.approx(3.0)      # the middle on the logarithm
    assert list(S.value([0, 5, 10, 30], VF["differentiation_similar_offers_within_150km"])) == pytest.approx([5, 3, 1, 1])
    assert list(S.value([0, 0.5, 1, 2], VF["differentiation_bavarian_quotient"])) == pytest.approx([5, 3, 1, 1])
    assert list(S.value([0, 0.2, 0.4, 0.9], VF["regional_share_of_net_new_kept_in_region"])) == pytest.approx([1, 3, 5, 5])


def test_score_is_the_weighted_mean_without_feasibility():
    w = {"student_demand": 0.30, "labour_relevance": 0.20, "institutional_fit": 0.20, "feasibility": 0.15, "differentiation": 0.10, "regional_contribution": 0.05}
    u = pd.DataFrame({"trend": [3.0, 3.0], "trend validated": [True, False], "net_new": [40.0, 40.0], "ads": [150.0, 150.0], "similar_150": [0.0, 0.0],
                      "quotient": [1.0, 1.0], "quotient used": [True, False], "kept": [0.4, 0.4], "emi score": [0.9, 0.5]})
    v = S.scores(u, VF, w, 0.5, 0.9)
    assert v.loc[0, "demand"] == 5 and v.loc[1, "demand"] == 4                       # a trend that is not validated counts 3 at most
    assert v.loc[0, "differentiation"] == 3 and v.loc[1, "differentiation"] == 5     # the offers half alone if the quotient is not used
    assert v.loc[0, "fit"] == 5 and v.loc[1, "fit"] == 1
    assert v.loc[0, "pre-gate score"] == pytest.approx((5 * 0.30 + 5 * 0.20 + 5 * 0.20 + 3 * 0.10 + 5 * 0.05) / 0.85)


@needs("data/interim/funnel2_shortlist.csv", "data/interim/funnel2_gate_order.csv", "data/interim/funnel2_step7a.json", "data/interim/funnel2_screen.csv")
def test_the_order_is_one_representative_per_candidate_by_score():
    o = pd.read_csv(INTERIM / "funnel2_shortlist.csv", float_precision="round_trip")
    g = pd.read_csv(INTERIM / "funnel2_gate_order.csv", float_precision="round_trip")
    s = pd.read_csv(INTERIM / "funnel2_screen.csv", float_precision="round_trip")
    r = json.loads((INTERIM / "funnel2_step7a.json").read_text(encoding="utf-8"))
    p = s[s["primary"]]
    assert len(o) == len(p) == 365 and len(g) == p.groupby(["group", "level"]).ngroups == r["candidates"] and r["stamp"]["clean"]
    assert (g["pre-gate score"].diff().dropna() <= 1e-12).all() and list(g["gate order"]) == list(range(1, len(g) + 1))
    best = o.groupby(["group", "level"])["pre-gate score"].max()
    assert np.allclose(g["pre-gate score"], [best[(a, b)] for a, b in zip(g["group"], g["level"])])
    w = r["weights"]
    assert o["pre-gate score"].to_numpy() == pytest.approx(sum(o[k] * v for k, v in w.items()).to_numpy() / sum(w.values()))
    assert o[["demand", "labour", "fit", "differentiation", "regional"]].stack().between(1, 5).all()
    m = o.merge(p[["type", "level", "emi score", "group: similar within 150 km"]], on=["type", "level"], suffixes=("", " (screen)"))
    assert np.allclose(m["emi score"], m["emi score (screen)"]) and np.allclose(m["similar_150"], m["group: similar within 150 km"])
    assert np.allclose(m["fit"], S.value(m["emi score"], {r["fit_proxy"]["bar"]: 1, r["fit_proxy"]["value 5 at"]: 5}))
