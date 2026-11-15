"""Funnel step 3: screen, competition, frozen lists (configs/funnel.yaml: definitions, pool_mapping, screen, freeze;
docs/criteria_funnel_step3.md). The tests on generated files recompute the result from the Step 2 files; they are
skipped where the git-ignored data is missing."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from study_program_intelligence.analysis import funnel_units as U

REPO = Path(__file__).resolve().parents[1]
INTERIM = REPO / "data" / "interim"
RULES = yaml.safe_load((REPO / "configs" / "funnel.yaml").read_text(encoding="utf-8"))
needs = lambda *files: pytest.mark.skipif(not all((INTERIM / f).exists() for f in files), reason="no generated data")
RUN = ("funnel2_screen.csv", "funnel2_candidates.csv", "funnel2_candidates_stress.csv", "funnel2_step3.json", "funnel2_offer_types.csv",
       "funnel2_types.csv", "funnel2_embeddings.npy", "funnel2_centroids.npy")
unit = lambda *v: np.array(v, float) / np.linalg.norm(v)


def test_a_unit_needs_offers_at_two_institutions():
    d = pd.DataFrame({"assigned_type": [0, 0, 0, 1, 1, -1], "level": ["bachelor", "bachelor", "master", "master", "master", "master"],
                      "institution": ["a", "b", "a", "c", "c", "d"], "title": list("uvwxyz")})
    u = U.units_of(d)
    assert [(r.type, str(r.level)) for r in u.itertuples()] == [(0, "bachelor")]       # 0/master and 1/master have one institution


def test_units_are_merged_only_if_every_pair_is_mutual_and_never_through_a_chain():
    cent = np.vstack([unit(1, 0, 0), unit(1, 0.1, 0), unit(1, 0.5, 0), unit(0, 0, 1)])
    radius = np.array([0.02, 0.02, 0.2, 0.02])                  # 0 and 1 are mutual; 2 reaches 0 and 1 but they do not reach 2
    units = pd.DataFrame({"type": [0, 1, 2, 3, 0, 1], "level": pd.Categorical(["bachelor"] * 4 + ["master"] * 2, U.LEVELS, ordered=True)})
    assert list(U.merged_groups(units, cent, radius)) == [0, 0, 2, 3, 0, 0]
    chain = np.vstack([unit(1, 0, 0), unit(1, 0.25, 0), unit(1, 0.55, 0)])      # 0-1 and 1-2 are close, 0-2 is not
    units = pd.DataFrame({"type": [0, 1, 2], "level": pd.Categorical(["bachelor"] * 3, U.LEVELS, ordered=True)})
    d = 1 - chain @ chain.T
    r = np.full(3, 0.045)
    assert d[0, 1] < 0.045 and d[1, 2] < 0.045 and d[0, 2] > 0.045
    assert list(U.merged_groups(units, chain, r)) == [0, 0, 2]                  # the closest pair merges; the third stays alone


def test_teacher_share_uses_title_degree_and_labels_without_the_level_marker():
    pattern = RULES["screen"]["teacher_training"]["pattern"]
    a = pd.DataFrame({"title": ["Mathematik Lehramt an Gymnasien", "Informatik", "Sport", "Physik", "Pharmazie"], "degree": ["Master"] * 5,
                      "subjects": ["Mathematik", "Informatik", "Lehramt an Grundschulen (grundständig)", "Sonderpädagogik", "Pharmazie (grundständig außer Staatsexamen)"]})
    assert U.teacher_share(a, pattern) == 0.6                                   # "außer Staatsexamen" is no state examination


def test_pool_weights_are_fractional_and_sum_to_one():
    a = pd.DataFrame({"subjects": ["Informatik (grundständig); Robotik (grundständig)", "Informatik (grundständig)"]})
    w = U.pool_weights(a, {"Informatik": "SF079", "Robotik": "SF380"})
    assert w == {"SF079": 0.75, "SF380": 0.25}


def test_slope_and_backtest_follow_the_demand_rule():
    rule = RULES["demand"]
    years = range(2005, 2025)
    rising = pd.Series([100 * 1.05 ** i for i in range(20)], index=years)
    assert U.slope_pct(rising, 2019, 2024) == pytest.approx(5.0)
    assert np.isnan(U.slope_pct(rising.drop(2021), 2019, 2024))                      # a year of the window is missing
    bt = U.backtest(pd.Series([100.0 + 10 * i for i in range(20)], index=years), 2024, rule)
    assert bt["validated"] and bt["drift"] == pytest.approx(0.0) and bt["naive"] > 1    # a straight line: drift is exact
    rng = np.random.default_rng(0)
    assert not U.backtest(pd.Series(100 + rng.normal(0, 10, 20), index=years), 2024, rule)["validated"]   # no trend: drift does not beat naive
    short = U.backtest(rising[rising.index >= 2014], 2024, rule)
    assert short["years"] == 11 and not short["validated"] and np.isnan(short["drift"])   # fewer than 12 years: not backtested
    assert not U.backtest(rising[rising.index <= 2023], 2024, rule)["validated"]      # does not end in the last year
    holes = rising.copy()
    holes[2015] = 0.0                                                                 # a zero year breaks the run: 9 years are left
    assert U.backtest(holes, 2024, rule)["years"] == 9


def test_bar_auc_and_quotient():
    pos = np.arange(1, 21) / 20
    assert U.keep_bar(pos) == 0.1                             # 19 of 20 field units are at or above 0.1: at least 95 % kept
    assert (pos >= U.keep_bar(pos)).mean() >= 0.95 and (pos >= 0.15).mean() < 0.95
    assert U.auc(np.array([0.9, 0.8, 0.7]), np.array([0.75, 0.5, 0.4])) == pytest.approx(8 / 9)
    assert U.youden(np.array([0.9, 0.8, 0.75]), np.array([0.7, 0.5, 0.4])) == 0.75
    assert U.quotient(0, 20, 0.12) == pytest.approx((5 * 0.12 / 25) / 0.12)           # no Bavarian offer among 20: well below 1
    assert U.quotient(0, 0, 0.12) == pytest.approx(1.0)                               # no offers at all: shrunk to 1


def test_emi_score_is_the_centred_cosine_to_module_titles():
    item_vec = np.vstack([unit(1, 0, 0), unit(0, 1, 0), unit(0, 0, 1), unit(1, 1, 0)])
    module_vec = np.vstack([unit(1, 0.1, 0)])
    all_items, title_only = U.emi_offer_scores([["a", "b"], ["c"]], {"a": 0, "b": 1, "c": 2, "x": 3}, item_vec, module_vec)
    mean = item_vec.mean(axis=0)
    cos = lambda x, y: float((x - mean) @ (y - mean) / np.linalg.norm(x - mean) / np.linalg.norm(y - mean))
    assert all_items[0] == pytest.approx((cos(item_vec[0], module_vec[0]) + cos(item_vec[1], module_vec[0])) / 2)
    assert title_only[0] == pytest.approx(cos(item_vec[0], module_vec[0])) and all_items[1] == title_only[1]


def test_gap_numbers_count_an_institution_and_title_once():
    land = np.array(["BY", "BW", "NW", "NW", "", "HH"])
    km = np.array([40.0, 140.0, 400.0, 400.0, np.nan, 500.0])
    key = np.array([0, 1, 2, 2, 3, 4])                        # rows 2 and 3: the same institution and cleaned title
    none = np.zeros(6, bool)
    n = U.gap_numbers(np.array([False, False, True, True, True, True]), none, land, km, 0.125, key)
    assert (n["similar offers"], n["similar in Bavaria"], n["similar in the south"], n["similar within 150 km"]) == (3, 0, 0, 0)
    assert n["exists elsewhere"] and n["absent flag"] and n["gap flag"] and np.isnan(n["bavarian quotient"])     # fewer than 5 similar offers: no quotient
    n = U.gap_numbers(np.ones(6, bool), none, land, km, 0.125, key)
    assert n["similar offers"] == 5 and not n["absent flag"] and not n["gap flag"]
    assert n["bavarian quotient"] == pytest.approx(((1 + 5 * 0.125) / 10) / 0.125)


def test_module_titles_that_name_no_subject_are_left_out():
    keep = U.subject_titles(["Change History", "Bachelorarbeit", "Master thesis", "Praxisphase mit Seminar", "Fachspezifisches Wahlpflichtmodul 2",
                             "Regelungstechnik", "Projektarbeit Robotik 2", "Mathematik 1", "Physikalisches Praktikum und Messtechnik"])
    assert list(keep) == [False, False, False, False, False, True, True, True, True]


@needs(*RUN)
def test_every_unit_is_tested_and_the_lists_follow_from_the_screens():
    r = json.loads((INTERIM / "funnel2_step3.json").read_text(encoding="utf-8"))
    s = pd.read_csv(INTERIM / "funnel2_screen.csv", float_precision="round_trip")
    d = pd.read_csv(INTERIM / "funnel2_offer_types.csv", low_memory=False)
    a = d[d["assigned_type"] >= 0].groupby(["assigned_type", "level"])["institution"].nunique()
    want = {(int(c), lv) for (c, lv), n in a.items() if n >= 2}
    assert set(zip(s["type"], s["level"])) == want and len(s) == len(want) == r["units"]
    assert r["units"] == json.loads((INTERIM / "funnel2_step2.json").read_text(encoding="utf-8"))["units"]
    sc, cal = RULES["screen"], r["calibration"]
    assert np.allclose(s["pool weight sum"], 1.0)
    assert (s["drop: teacher training"] == (s["teacher share"] >= sc["teacher_training"]["drop_if_at_least"])).all()
    assert (s["drop: trend"] == ((s["trend %/yr"] < sc["trend"]["drop_if_below"]) & s["trend validated"])).all()
    assert (s["trend validated"] == ((s["MASE drift"] < s["MASE naive"]) & (s["MASE drift"] < 1))).all()
    assert not s.loc[s["backtest years"] < 12, "trend validated"].any()
    assert (s["outside EMI"] == (s["emi score"] < cal["bar"])).all() and (s["drop: outside EMI"] == (s["outside EMI"] & cal["screen_drops"])).all()
    assert cal["screen_drops"] == (cal["auc"] >= sc["emi_domain"]["if_auc_below"]["auc"])
    dropped = s["drop: at OTH"] | s["drop: teacher training"] | s["drop: trend"] | s["drop: outside EMI"]
    assert (s["primary"] == ~dropped).all() and (s["stress"] == ~s["drop: at OTH"]).all()
    for name, col in (("funnel2_candidates.csv", "primary"), ("funnel2_candidates_stress.csv", "stress")):
        lst = pd.read_csv(INTERIM / name)
        assert list(zip(lst["type"], lst["level"])) == list(zip(s.loc[s[col], "type"], s.loc[s[col], "level"]))
        h = hashlib.sha256("\n".join(f"{t}:{lv}" for t, lv in zip(lst["type"], lst["level"])).encode()).hexdigest()[:16]
        assert h == r["hashes"][col]
    for name, h in r["files"].items():
        assert hashlib.sha256((INTERIM / name).read_bytes()).hexdigest()[:16] == h, name
    teach = lambda x: bool(__import__("re").search(sc["teacher_training"]["pattern"], U.normalise(x)))     # the teacher share, again from the offers
    for row in s.sample(60, random_state=0).itertuples():
        o = d[(d["assigned_type"] == row.type) & (d["level"] == row.level)]
        text = o["title"].fillna("") + " " + o["degree"].fillna("") + " " + o["subjects"].fillna("").str.replace(r"\s*\((?:grundständig|weiterführend)[^)]*\)", "", regex=True)
        assert text.map(teach).mean() == pytest.approx(s.at[row.Index, "teacher share"])


@needs(*RUN, "funnel2_item_vectors.npy", "funnel2_item_index.csv", "funnel2_module_title_vectors.npy", "modules_emi_2026.csv")
def test_the_emi_score_is_recomputed_and_separates_the_marked_units():
    """Criterion S18: the unit scores are computed again from the vectors; bar and AUC from the marks."""
    r = json.loads((INTERIM / "funnel2_step3.json").read_text(encoding="utf-8"))["calibration"]
    s = pd.read_csv(INTERIM / "funnel2_screen.csv", float_precision="round_trip")
    d = pd.read_csv(INTERIM / "funnel2_offer_types.csv", low_memory=False)
    vec = np.load(INTERIM / "funnel2_item_vectors.npy").astype(np.float64)
    pos_of = {x: i for i, x in enumerate(pd.read_csv(INTERIM / "funnel2_item_index.csv", keep_default_na=False)["item"])}
    titles = sorted(set(pd.read_csv(INTERIM / "modules_emi_2026.csv", low_memory=False)["title"].dropna().astype(str)))
    mod = np.load(INTERIM / "funnel2_module_title_vectors.npy").astype(np.float64)[U.subject_titles(titles)]
    assert (len(titles), len(mod)) == (r["module_titles"], r["module_titles_naming_a_subject"])
    mean = vec.mean(axis=0)
    norm = lambda v: v / np.linalg.norm(v, axis=1, keepdims=True)
    best = (norm(vec - mean) @ norm(mod - mean).T).max(axis=1)
    for row in s.sample(80, random_state=1).itertuples():
        o = d[(d["assigned_type"] == row.type) & (d["level"] == row.level)]
        o = o[~o["is_oth"]] if (~o["is_oth"]).any() else o
        per_offer = [np.mean([best[pos_of[x]] for x in [t, *(f.split(" | ") if isinstance(f, str) and f else [])]]) for t, f in zip(o["clean_title"], o["focus_text"])]
        assert np.mean(per_offer) == pytest.approx(s.at[row.Index, "emi score"])
    lab = pd.read_csv(REPO / "docs" / "funnel_emi_labels.csv", keep_default_na=False).merge(s[["type", "level", "emi score"]], on=["type", "level"])
    assert len(lab) == 300 == r["marked_units"]
    pos, neg = lab.loc[lab["label"] != "no", "emi score"].to_numpy(), lab.loc[lab["label"] == "no", "emi score"].to_numpy()
    wins = np.mean([(p > neg).mean() + 0.5 * (p == neg).mean() for p in pos])
    assert round(float(wins), 3) == r["auc"] >= 0.8
    assert (pos >= r["bar"]).mean() >= 0.95 and r["bar"] in pos and (pos > r["bar"]).mean() < 0.95     # the highest bar that keeps 95 %
    assert (int((pos >= r["bar"]).sum()), int((neg >= r["bar"]).sum())) == (r["field_units_kept"], r["outside_units_kept"])


@needs(*RUN)
def test_at_oth_groups_and_competition_are_recomputed_from_the_vectors():
    r = json.loads((INTERIM / "funnel2_step3.json").read_text(encoding="utf-8"))
    s = pd.read_csv(INTERIM / "funnel2_screen.csv", float_precision="round_trip")
    d = pd.read_csv(INTERIM / "funnel2_offer_types.csv", low_memory=False)
    t = pd.read_csv(INTERIM / "funnel2_types.csv")
    emb = np.load(INTERIM / "funnel2_embeddings.npy").astype(np.float64)
    cent = np.load(INTERIM / "funnel2_centroids.npy").astype(np.float64)
    dist = 1 - emb @ cent.T
    oth, far = d["is_oth"].to_numpy(bool), (d["study_form"] == "Fernstudium").to_numpy()
    assigned = d["assigned_type"].to_numpy()
    by, south = (d["state"] == "Bayern").to_numpy(), d["state"].isin(["Bayern", "Baden-Württemberg"]).to_numpy()
    km150 = (d["km_amberg"] <= 150).to_numpy()
    at_level = {lv: (d["level"] == lv).to_numpy() for lv in U.LEVELS}
    p = {lv: (by & m).sum() / m.sum() for lv, m in at_level.items()}
    once = lambda mask: len(d.loc[mask, ["institution", "clean_title"]].drop_duplicates())     # each institution and cleaned title once, inside the set
    sims, triggering = {}, set()
    for i, r_ in s.iterrows():
        c, lv, m = r_["type"], r_["level"], at_level[r_["level"]]
        inside = m & ((assigned == c) | (dist[:, c] <= t.at[c, "radius_90"]))
        sim = sims[(c, lv)] = ~oth & ~far & inside
        n, n_by, n_s, n_150 = once(sim), once(sim & by), once(sim & south), once(sim & km150)
        assert (r_["similar offers"], r_["similar in Bavaria"], r_["similar in the south"], r_["similar within 150 km"]) == (n, n_by, n_s, n_150)
        assert r_["similar distance-learning offers (not counted)"] == once(~oth & far & inside)
        elsewhere = n - n_s >= 1
        assert r_["exists elsewhere"] == elsewhere and r_["absent flag"] == (elsewhere and n_by == 0) and r_["gap flag"] == (elsewhere and n_150 == 0 and n_s == 0)
        assert np.isnan(r_["bavarian quotient"]) if n < 5 else r_["bavarian quotient"] == pytest.approx(((n_by + 5 * p[lv]) / (n + 5)) / p[lv])
        hit = oth & m & ((assigned == c) | (dist[:, c] <= t.at[c, "median distance"]))             # criterion S20
        assert r_["drop: at OTH"] == bool(hit.any())
        triggering |= set(np.where(hit)[0])
    units = set(zip(s["type"], s["level"]))
    must = [i for i in np.where(oth)[0] if (assigned[i], d.at[i, "level"]) in units]
    assert set(must) <= triggering and len(triggering) == r["oth_offers_that_drop_a_unit"]
    radius, cd = t["radius_90"].to_numpy(), 1 - cent @ cent.T
    for (lv, g), grp in s.groupby(["level", "group"]):          # criterion S17: every pair in a group is mutual; the union is counted
        ts = grp["type"].to_numpy()
        assert g == ts.min() and (grp["group size"] == len(ts)).all()
        assert (cd[np.ix_(ts, ts)] <= np.minimum(radius[ts][:, None], radius[ts][None, :]) + 1e-12).all()
        union = np.any([sims[(c, lv)] for c in ts], axis=0)
        assert (grp["group: similar offers"] == once(union)).all() and (grp["group: similar within 150 km"] == once(union & km150)).all()
