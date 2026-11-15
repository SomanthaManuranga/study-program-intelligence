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


def test_a_unit_needs_offers_at_two_institutions():
    d = pd.DataFrame({"assigned_type": [0, 0, 0, 1, 1, -1], "level": ["bachelor", "bachelor", "master", "master", "master", "master"],
                      "institution": ["a", "b", "a", "c", "c", "d"], "title": list("uvwxyz")})
    u = U.units_of(d)
    assert [(r.type, str(r.level)) for r in u.itertuples()] == [(0, "bachelor")]       # 0/master and 1/master have one institution


def test_units_are_merged_only_if_each_centroid_lies_inside_the_other_radius():
    unit = lambda *v: np.array(v, float) / np.linalg.norm(v)
    cent = np.vstack([unit(1, 0, 0), unit(1, 0.1, 0), unit(1, 0.5, 0), unit(0, 0, 1)])
    radius = np.array([0.02, 0.02, 0.2, 0.02])                  # 0 and 1 are mutual; 2 reaches 0 and 1 but they do not reach 2
    units = pd.DataFrame({"type": [0, 1, 2, 3, 0, 1], "level": pd.Categorical(["bachelor"] * 4 + ["master"] * 2, U.LEVELS, ordered=True)})
    assert list(U.merged_groups(units, cent, radius)) == [0, 0, 2, 3, 0, 0]


def test_teacher_share_uses_title_degree_and_labels():
    pattern = RULES["screen"]["teacher_training"]["pattern"]
    a = pd.DataFrame({"title": ["Mathematik Lehramt an Gymnasien", "Informatik", "Sport", "Physik"], "degree": ["Master"] * 4,
                      "subjects": ["Mathematik", "Informatik", "Lehramt an Grundschulen (grundständig)", "Sonderpädagogik"]})
    assert U.teacher_share(a, pattern) == 0.75


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
    noise = pd.Series(100 + rng.normal(0, 10, 20), index=years)
    assert not U.backtest(noise, 2024, rule)["validated"]                             # no trend: drift does not beat naive
    short = U.backtest(rising[rising.index >= 2014], 2024, rule)
    assert short["years"] == 11 and not short["validated"] and np.isnan(short["drift"])   # fewer than 12 years: not backtested
    assert not U.backtest(rising[rising.index <= 2023], 2024, rule)["validated"]      # does not end in the last data year


def test_youden_cut_and_quotient():
    cut, auc = U.youden(np.array([0.9, 0.8, 0.7]), np.array([0.75, 0.5, 0.4]))
    assert cut == 0.7 and auc == pytest.approx(8 / 9)                              # cuts 0.7 and 0.8 tie: the lower cut is taken
    assert U.quotient(0, 20, 0.12, 5) == pytest.approx((5 * 0.12 / 25) / 0.12)        # no Bavarian offer among 20: well below 1
    assert U.quotient(0, 0, 0.12, 5) == pytest.approx(1.0)                            # no offers at all: shrunk to 1


@needs(*RUN)
def test_every_unit_is_tested_and_the_lists_follow_from_the_screens():
    r = json.loads((INTERIM / "funnel2_step3.json").read_text(encoding="utf-8"))
    s = pd.read_csv(INTERIM / "funnel2_screen.csv")
    d = pd.read_csv(INTERIM / "funnel2_offer_types.csv", low_memory=False)
    a = d[d["assigned_type"] >= 0].groupby(["assigned_type", "level"])["institution"].nunique()
    want = {(int(c), lv) for (c, lv), n in a.items() if n >= 2}
    assert set(zip(s["type"], s["level"])) == want and len(s) == len(want) == r["units"]
    assert r["units"] == json.loads((INTERIM / "funnel2_step2.json").read_text(encoding="utf-8"))["units"]
    sc = RULES["screen"]
    assert (s["drop: teacher training"] == (s["teacher share"] >= sc["teacher_training"]["drop_if_at_least"])).all()
    assert (s["drop: trend"] == ((s["trend %/yr"] < sc["trend"]["drop_if_below"]) & s["trend validated"])).all()
    assert (s["trend validated"] == ((s["MASE drift"] < s["MASE naive"]) & (s["MASE drift"] < 1))).all()
    assert not s.loc[s["backtest years"] < 12, "trend validated"].any()
    assert (s["drop: outside EMI"] == (s["outside EMI"] & r["calibration"]["screen_drops"])).all()
    clear = (s["emi score"] - r["calibration"]["bar"]).abs() > 1e-4               # the bar is stored with 4 decimals
    assert (s.loc[clear, "outside EMI"] == (s.loc[clear, "emi score"] < r["calibration"]["bar"])).all()
    assert r["calibration"]["screen_drops"] == (r["calibration"]["auc"] >= sc["emi_domain"]["if_auc_below"]["auc"])
    dropped = s["at OTH (own or group)"] | s["drop: teacher training"] | s["drop: trend"] | s["drop: outside EMI"]
    assert (s["primary"] == ~dropped).all() and (s["stress"] == ~s["at OTH (own or group)"]).all()
    for name, col in (("funnel2_candidates.csv", "primary"), ("funnel2_candidates_stress.csv", "stress")):
        lst = pd.read_csv(INTERIM / name)
        assert list(zip(lst["type"], lst["level"])) == list(zip(s.loc[s[col], "type"], s.loc[s[col], "level"]))
        h = hashlib.sha256("\n".join(f"{t}:{lv}" for t, lv in zip(lst["type"], lst["level"])).encode()).hexdigest()[:16]
        assert h == r["hashes"][col]
    assert r["stamp"]["clean"] is True
    for name, h in r["files"].items():
        assert hashlib.sha256((INTERIM / name).read_bytes()).hexdigest()[:16] == h, name


@needs(*RUN)
def test_at_oth_and_competition_are_recomputed_from_the_vectors():
    s = pd.read_csv(INTERIM / "funnel2_screen.csv")
    d = pd.read_csv(INTERIM / "funnel2_offer_types.csv", low_memory=False)
    t = pd.read_csv(INTERIM / "funnel2_types.csv")
    emb = np.load(INTERIM / "funnel2_embeddings.npy").astype(np.float64)
    cent = np.load(INTERIM / "funnel2_centroids.npy").astype(np.float64)
    dist = 1 - emb @ cent.T
    oth, far = d["is_oth"].to_numpy(bool), (d["study_form"] == "Fernstudium").to_numpy()
    south = d["state"].isin(["Bayern", "Baden-Württemberg"]).to_numpy()
    by_level = {lv: (d["level"] == lv).to_numpy() for lv in U.LEVELS}
    p = {lv: ((d["state"] == "Bayern").to_numpy() & ~oth & ~far & m).sum() / (~oth & ~far & m).sum() for lv, m in by_level.items()}
    at_oth = {}
    for r in s.itertuples():
        c, m = r.type, by_level[r.level]
        at_oth[(c, r.level)] = bool((oth & m & (dist[:, c] <= t.at[c, "median distance"])).any())
        sim = ~oth & ~far & m & ((d["assigned_type"].to_numpy() == c) | (dist[:, c] <= t.at[c, "radius_90"]))
        n_by, n_s, n_150 = int((sim & (d["state"] == "Bayern").to_numpy()).sum()), int((sim & south).sum()), int((sim & (d["km_amberg"] <= 150).to_numpy()).sum())
        row = s.loc[r.Index]
        assert row["similar offers"] == int(sim.sum())
        assert (row["similar in Bavaria"], row["similar in the south"], row["similar within 150 km"]) == (n_by, n_s, n_150)
        elsewhere = int(sim.sum()) - n_s >= 1
        assert row["exists elsewhere"] == elsewhere and row["absent flag"] == (elsewhere and n_by == 0) and row["gap flag"] == (elsewhere and n_150 == 0 and n_s == 0)
        if sim.sum() >= 5:
            assert row["bavarian quotient"] == pytest.approx(((n_by + 5 * p[r.level]) / (sim.sum() + 5)) / p[r.level])
        else:
            assert np.isnan(row["bavarian quotient"])
        assert row["drop: at OTH"] == at_oth[(c, r.level)]
    groups = s[s["drop: at OTH"]].groupby("level")["group"].agg(set).to_dict()
    want = [own or g in groups.get(lv, set()) for own, g, lv in zip(s["drop: at OTH"], s["group"], s["level"])]
    assert list(s["at OTH (own or group)"]) == want
    radius, cd = t["radius_90"].to_numpy(), 1 - cent @ cent.T
    for lv, part in s.groupby("level"):                         # two units of one level in one group must be linked through mutual pairs
        for g, grp in part.groupby("group"):
            ts = grp["type"].to_numpy()
            if len(ts) > 1:
                link = (cd[np.ix_(ts, ts)] <= radius[ts][:, None]) & (cd[np.ix_(ts, ts)] <= radius[ts][None, :])
                assert (link.sum(axis=1) > 1).all() and g == ts.min()
