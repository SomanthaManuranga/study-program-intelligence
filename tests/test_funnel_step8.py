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


def mc_cands():
    row = lambda t, nn: {"type": t, "level": "bachelor", "trend low": 1.0, "trend central": 2.0, "trend high": 3.0, "trend validated": True,
                         "net-new low": nn / 3, "net-new central": nn, "net-new high": nn * 3, "labour low": 50.0, "labour central": 100.0, "labour high": 200.0,
                         "fit low": 0.5, "fit central": 0.6, "fit high": 0.7, "feasibility low": 0.8, "feasibility central": 0.9, "feasibility high": 1.0,
                         "offers 75": 2.0, "offers 90": 3.0, "offers 95": 4.0, "quotient": np.nan, "quotient used": False, "tier 2 shown": False,
                         "regional low": 0.1, "regional central": 0.2, "regional high": 0.3}
    return pd.DataFrame([row(1, 30.0), row(2, 15.0)])


def test_montecarlo_is_reproducible_and_uses_the_full_offers_range():
    w = {"demand": .3, "labour": .2, "fit": .2, "feasibility": .15, "differentiation": .1, "regional": .05}
    a, Sa = R.montecarlo(mc_cands(), VF, w, draws=2000)
    b, Sb = R.montecarlo(mc_cands(), VF, w, draws=2000)
    assert np.array_equal(Sa, Sb) and a["P(rank 1)"].sum() == pytest.approx(1.0)
    assert 0.6 < a.loc[0, "P(rank 1)"] < 1.0                                                                      # twice the new students, but wide ranges
    assert R.OFFERS_FULL_RANGE                                                                                    # second_failure: the offers half on 1-5


def test_two_candidates_decision_and_ties():
    c = mc_cands().assign(**{"new teaching ECTS": 50.0, "professor-equivalents": 1.1, "X ECTS": "0.000", "N ECTS": "40.000", "references": 1, "fit central": 0.6})
    c.index = pd.MultiIndex.from_frame(c[["type", "level"]])
    central = pd.Series([3.0, 3.0], index=c.index)                                                               # a tie: the lower type number first
    S = np.tile([1.0, 0.0], (10, 1))
    mc = pd.DataFrame({"type": [1, 2], "level": ["bachelor"] * 2, "P(rank 1)": [1.0, 0.0]})
    d = R.decide(c, central, mc, S, 0.6, pd.Series([0.1, -0.1], index=c.index), R.BARS, 15)
    assert d["candidate"] == [1, "bachelor"] and d["outcome"] == "recommend" and d["professor-equivalents"] == 1.1
    assert R.decide(c, central, mc, S, 0.4, pd.Series([0.1, -0.1], index=c.index), R.BARS, 15)["outcome"] == "shortlist"          # win share below 0.5
    assert R.decide(c, central, mc, S, 0.6, pd.Series([-0.1, 0.1], index=c.index), R.BARS, 15)["outcome"].startswith("shortlist (PROMETHEE")


def test_one_programme_reading():
    b = dict(R.BASE)
    assert R.passes(cand(**{"one-programme shares": "0.85; 0.3"}), dict(b, one_programme_max="none")) == (True, True)       # no limit means no limit
    assert R.passes(cand(**{"one-programme shares": "0.85; 0.3"}), b) == (False, False)


@needs("data/interim/funnel2_rank_inputs.csv", "data/interim/funnel2_gate_references.csv", "data/interim/funnel2_labour.csv", "data/interim/funnel2_capture.csv")
def test_every_input_comes_from_its_file():
    inp = pd.read_csv(INTERIM / "funnel2_rank_inputs.csv").set_index(["type", "level"])
    refs = pd.read_csv(INTERIM / "funnel2_gate_references.csv")
    lb = pd.read_csv(INTERIM / "funnel2_labour.csv").set_index(["type", "level"])
    cp = pd.read_csv(INTERIM / "funnel2_capture.csv", float_precision="round_trip").set_index(["type", "level"])
    sc = pd.read_csv(INTERIM / "funnel2_screen.csv", float_precision="round_trip").set_index(["type", "level"])
    for key, c in inp.iterrows():
        rr = refs[(refs["type"] == key[0]) & (refs["level"] == key[1])]
        assert c["labour central"] == lb.at[key, "ads within 100 km (median keyword)"] and c["labour low"] == lb.at[key, "ads within 100 km (smallest keyword)"]
        assert c["labour high"] == lb.at[key, "ads within 100 km (largest keyword)"]
        w = 0.10 if len(rr) == 1 else 0.0
        assert c["fit central"] == pytest.approx(rr["overlap"].mean()) and c["fit low"] == pytest.approx(rr["overlap"].min() - w) and c["fit high"] == pytest.approx(rr["overlap"].max() + w)
        assert c["feasibility central"] == pytest.approx(rr["share of new ECTS in N"].mean())
        assert c["offers 90"] == sc.at[key, "group: similar within 150 km"] and c["offers 75"] == sc.at[key, "similar within 150 km (radius 75)"]
        assert (c["quotient used"] == (sc.at[key, "group: similar offers"] >= 5)) and (not c["quotient used"] or c["quotient"] == pytest.approx(sc.at[key, "group: bavarian quotient"]))
        assert c["regional central"] == pytest.approx(cp.at[key, "kept in the region (central)"]) and c["regional low"] == pytest.approx(cp.at[key, "kept in the region (pessimistic)"])
        assert c["gross central"] == pytest.approx(cp.at[key, "gross central"])


def test_cache_keys_cover_every_factor_a_score_or_gate_reads():
    c = cand(**{"trend central": 2.0, "trend validated": True, "net-new central": 20.0, "labour central": 100.0, "labour high": 300.0, "fit central": 0.525,
                "feasibility central": 0.5, "feasibility shares": "0.9; 0.1", "regional central": 0.2, "offers 90": 3.0, "quotient": np.nan, "quotient used": False,
                "projection factor": 1.0, "foreign share": 0.4})
    base = dict(R.BASE, **{"net-new factor": R.net_new_factor(R.BASE)})
    for f, levels in R.FACTORS.items():
        if not levels[1]:
            continue
        for lv in levels[0]:
            spec = dict(base, **{f: lv})
            spec["net-new factor"] = R.net_new_factor(spec)
            if R.values(c, VF, spec) != R.values(c, VF, base):
                assert f in R.VALUE_KEYS, f
            if R.passes(c, spec) != R.passes(c, base):
                assert f in R.GATE_KEYS, f
    assert R.values(c, VF, dict(base, references="primary only"))["feasibility"] != R.values(c, VF, base)["feasibility"]


def test_listspecs_supply_cut_and_connected_groups():
    from study_program_intelligence.analysis import funnel_listspecs as L
    cent = np.array([[1.0, 0.0], [0.995, 0.0998749], [0.98, 0.198997]])
    cent = cent / np.linalg.norm(cent, axis=1, keepdims=True)
    units = pd.DataFrame({"type": [0, 1, 2], "level": ["bachelor"] * 3})
    g = L.connected_groups(units, cent, np.array([0.006, 0.006, 0.006]))
    assert list(g) == [0, 0, 0]                                                                                   # 0-1 and 1-2 within reach: one chain
    assert "<= spec[\"supply_cut\"]" in open(L.__file__, encoding="utf-8").read()                                # version 2 kept at most k offers
