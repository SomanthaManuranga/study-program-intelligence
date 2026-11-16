"""Funnel step 8a: ranking, stress tests, decision (configs/funnel.yaml: ranking, stress_tests, decision; docs/criteria_funnel_step8.md)."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from study_program_intelligence.analysis import funnel_rank as R

REPO = Path(__file__).resolve().parents[1]
INTERIM = REPO / "data" / "interim"
needs = lambda *files: pytest.mark.skipif(not all((REPO / f).exists() for f in files), reason="no generated data")
VF = R.config()["ranking"]["value_functions"]


def test_constants_follow_the_rules():
    r = R.config()
    assert "Dirichlet with concentration 50, 10,000 draws, seed 42" in r["ranking"]["sampling"] and (R.CONCENTRATION, R.DRAWS, R.SEED) == (50, 10_000, 42)
    assert "P(rank 1) >= 0.5, P(beats the runner-up) >= 0.8 and win share >= 0.5" in r["decision"]["rule"]["two_or_more"] and R.BARS == {"rank_1": 0.5, "beats_runner_up": 0.8, "win_share": 0.5}
    assert "at least 15" in r["decision"]["rule"]["one"] and R.ONE_PASSER == 15
    f = r["stress_tests"]["downstream_factorial"]
    assert set(f) == {k for k in R.FACTORS} - {"N_cap"} | {"existing_resources_N_cap"}
    assert all(len(f["existing_resources_N_cap" if k == "N_cap" else k]) == len(v[0]) for k, v in R.FACTORS.items())


def test_widened_anchors_keep_the_inner_point():
    assert R.widened({-3: 1, 0: 3, 3: 5}) == {0.0: 3, -3.75: 1, 3.75: 5}
    w = R.widened({10: 1, 150: 5}, log=True)
    lo, hi = sorted(w)
    assert np.log(150) - np.log(hi) == pytest.approx(-(np.log(150) - np.log(10)) / 8) and np.log(lo) == pytest.approx(np.log(10) - (np.log(150) - np.log(10)) / 8)


def cand(**kw):
    base = {"type": 1, "level": "bachelor", "overlaps": "0.6; 0.45", "one-programme shares": "0.3; 0.3", "lab shares": "0.000; 0.000", "X ECTS": "0.000; 0.000",
            "N ECTS": "30.000; 15.000", "gross central": 30.0}
    base.update(kw)
    return pd.Series(base)


def test_gate_under_specs():
    b = dict(R.BASE)
    assert R.passes(cand(), b) == (True, True)
    assert R.passes(cand(**{"X ECTS": "0.000; 5.000"}), b) == (True, False)                                       # outside teaching: band only
    assert R.passes(cand(), dict(b, overlap_band=(0.5, 0.8))) == (False, False)
    assert R.passes(cand(), dict(b, overlap_band=(0.5, 0.8), references="primary only")) == (True, True)
    assert R.passes(cand(), dict(b, N_cap={"bachelor": 20.0, "master": 10.0})) == (True, False)
    assert R.passes(cand(**{"one-programme shares": "0.6; 0.3"}), dict(b, one_programme_max=0.5)) == (False, False)
    assert R.passes(cand(**{"overlaps": "0.85; 0.6"}), dict(b, overlap_reading="both ends on all EMI modules")) == (False, False)
    assert R.passes(cand(**{"overlaps": "0.85; 0.6"}), b) == (True, True)                                         # the upper end applies to one programme
    assert R.passes(cand(**{"gross central": 22.0}), dict(b, min_cohort=25)) == (False, False)
    assert R.passes(cand(**{"lab shares": "0.000; 0.010"}), b) == (False, False)


def test_promethee_and_score():
    w = {"demand": .3, "labour": .2, "fit": .2, "feasibility": .15, "differentiation": .1, "regional": .05}
    V = pd.DataFrame({"demand": [5, 1], "labour": [3, 3], "fit": [3, 3], "feasibility": [3, 3], "differentiation": [1, 5], "regional": [3, 3]}, index=["a", "b"])
    phi = R.promethee(V, w)
    assert phi["a"] == pytest.approx(0.3 - 0.1) and phi["b"] == pytest.approx(-0.2)                               # (5-1)/4 = full preference
    assert R.score(V.loc["a"].to_dict(), w) == pytest.approx(5 * .3 + 3 * .2 + 3 * .2 + 3 * .15 + 1 * .1 + 3 * .05)
    assert R.score(V.loc["a"].to_dict(), w, feasibility=False) == pytest.approx((5 * .3 + 3 * .2 + 3 * .2 + 1 * .1 + 3 * .05) / .85)


def test_one_candidate_rule():
    c = pd.DataFrame([{"type": 1, "level": "bachelor", "net-new central": 26.5}])
    assert R.decide(c, pd.Series([3.0]), None, None, None, None, R.BARS, 15)["outcome"] == "recommend"
    assert R.decide(c.assign(**{"net-new central": 12.0}), pd.Series([3.0]), None, None, None, None, R.BARS, 15)["outcome"] == "shortlist"
    assert R.decide(c.iloc[:0], pd.Series(dtype=float), None, None, None, None, R.BARS, 15)["outcome"] == "no candidate passes"


@needs("data/interim/funnel2_rank_inputs.csv", "data/interim/funnel2_rank.csv", "data/interim/funnel2_step8.json", "data/interim/funnel2_gate.csv")
def test_outputs_follow_the_rules():
    inp = pd.read_csv(INTERIM / "funnel2_rank_inputs.csv")
    rk = pd.read_csv(INTERIM / "funnel2_rank.csv")
    g = pd.read_csv(INTERIM / "funnel2_gate.csv")
    r = json.loads((INTERIM / "funnel2_step8.json").read_text(encoding="utf-8"))
    assert r["stamp"]["clean"] and len(inp) == len(g)
    first = {f"{t} {l}" for t, l in zip(g.loc[g["verdict"] == "existing-resources passer", "type"], g.loc[g["verdict"] == "existing-resources passer", "level"])}
    second = {f"{t} {l}" for t, l, v in zip(g["type"], g["level"], g["verdict"]) if v in ("existing-resources passer", "band passer")}
    assert set(r["sets"]["first"]["members"]) == first and set(r["sets"]["second"]["members"]) == second
    assert r["factorial"]["specs"] == int(np.prod([len(v[0]) for v in R.FACTORS.values()]))
    for s in ("first", "second"):
        assert sum(r["sets"][s]["winners over the factorial"].values()) == pytest.approx(1.0)
    cp = pd.read_csv(INTERIM / "funnel2_capture.csv").set_index(["type", "level"])
    for c in inp.itertuples():
        assert inp.at[c.Index, "net-new central"] == pytest.approx(cp.at[(c.type, c.level), "net-new central"])
        assert inp.at[c.Index, "trend low"] <= inp.at[c.Index, "trend central"] <= inp.at[c.Index, "trend high"]
        assert inp.at[c.Index, "trend central"] == pytest.approx(pd.read_csv(INTERIM / "funnel2_demand.csv").set_index(["type", "level"]).at[(c.type, c.level), "trend German BY %/yr"])
    w = r["weights"]
    for x in rk.itertuples():
        vals = {k: rk.at[x.Index, f"value {k}"] for k in w}
        assert rk.at[x.Index, "central score"] == pytest.approx(sum(vals[k] * w[k] for k in w) / sum(w.values()))
