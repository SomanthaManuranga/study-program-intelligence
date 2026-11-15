"""Funnel step 6: first-years and students new to OTH (configs/funnel.yaml: capture; docs/criteria_funnel_step6.md)."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from study_program_intelligence.analysis import funnel_capture as C
from study_program_intelligence.analysis.catchment import haversine

REPO = Path(__file__).resolve().parents[1]
INTERIM = REPO / "data" / "interim"
needs = lambda *files: pytest.mark.skipif(not all((REPO / f).exists() for f in files), reason="no generated data")
POOL = pd.DataFrame({"mass": [100.0, 300.0], "lat": [49.44, 48.14], "lon": [11.86, 11.58], "own": [True, False]})
ARR = lambda *x: np.array(x, dtype=float)


def test_the_model_follows_the_rule_file():
    r = C.config()["capture"]
    assert r["w_substitute"] == {"pessimistic": 1.0, "central": 0.5, "optimistic": 0.25} and r["min_cohort"]["value"] == 20
    assert f"x {C.LOW}" in r["gross"]["low"] and f"x {C.HIGH}" in r["gross"]["high"] and f"transition {C.TRANSITION}" in r["anchor"]["master"]
    assert C.NEW_SITE == {"bachelor": [C.AMBERG, C.WEIDEN], "master": [C.AMBERG]} and C.BETA == 1.6
    assert "(2024)" in r["anchor"]["bachelor"] and "(2025)" in r["anchor"]["master"] and C.ANCHOR["bachelor"][1] == 2024 and C.ANCHOR["master"][1] == 2025


def test_huff_shares_sum_to_one_and_demand_is_conserved():
    lat, lon = ARR(49.02, 48.14, 49.44), ARR(12.10, 11.58, 11.86)             # Regensburg, Munich, an OTH offer in Amberg
    is_oth, reg = np.array([False, False, True]), np.array([True, False, True])
    r = C.huff(POOL, lat, lon, ARR(1, 1, 0.5), is_oth, reg, [C.AMBERG, C.WEIDEN])
    assert r["a"] + r["b"] == pytest.approx(1.0) and 0 < r["c"] < r["b"]
    assert r["new"] + r["sites"].sum() == pytest.approx(POOL["mass"].sum())    # every origin's shares sum to 1
    d = lambda la, lo: np.maximum(haversine(POOL["lat"].to_numpy(), POOL["lon"].to_numpy(), la, lo), 5.0)      # the same by hand
    new = np.minimum(d(*C.AMBERG), d(*C.WEIDEN)) ** -1.6
    base = np.c_[d(49.02, 12.10) ** -1.6, d(48.14, 11.58) ** -1.6, 0.5 * d(49.44, 11.86) ** -1.6]
    n = POOL["mass"].to_numpy() * new / (base.sum(axis=1) + new)
    assert r["new"] == pytest.approx(n.sum())
    assert r["a"] == pytest.approx((n * base[:, 2] / base.sum(axis=1)).sum() / n.sum())
    assert r["c"] == pytest.approx((n * base[:, 1] / base.sum(axis=1))[0] / n.sum())      # own-pool origin, site outside the region


def test_a_stronger_oth_offer_gives_a_larger_share_from_oth_and_no_site_gives_everything():
    lat, lon, is_oth, reg = ARR(49.02, 49.44), ARR(12.10, 11.86), np.array([False, True]), np.array([True, True])
    a = [C.huff(POOL, lat, lon, ARR(1, w), is_oth, reg, [C.AMBERG])["a"] for w in (1.0, 0.5, 0.25)]
    assert a[0] > a[1] > a[2] > 0
    alone = C.huff(POOL, ARR(), ARR(), ARR(), np.zeros(0, bool), np.zeros(0, bool), [C.AMBERG])
    assert alone["new"] == pytest.approx(400.0) and alone["a"] == alone["b"] == alone["c"] == 0


def test_anchor_per_offer_and_germany_wide_fallback():
    d = pd.DataFrame({"level": ["bachelor"] * 3 + ["master"], "state": ["Bayern", "Bayern", "Hessen", "Bayern"],
                      "subjects": ["Informatik", "Informatik; Mathematik", "Physik", "Informatik"]})
    smap = {"Informatik": "A", "Mathematik": "B", "Physik": "P"}
    long = pd.DataFrame([("first-years", "BY", "A", 2024, "German", 300.0), ("first-years", "BY", "B", 2024, "German", 50.0), ("first-years", "BY", "A", 2024, "foreign", 999.0),
                         ("first-years", "DE", "A", 2024, "German", 900.0), ("first-years", "DE", "P", 2024, "German", 80.0), ("first-years", "BY", "A", 2023, "German", 1.0),
                         ("graduates", "BY", "A", 2025, "German", 40.0)], columns=["kind", "region", "code", "year", "nationality", "value"])
    import study_program_intelligence.analysis.funnel_capture as m
    old, m.map_label = m.map_label, lambda x: x
    try:
        t = C.per_offer(d, smap, long, 0.5)
    finally:
        m.map_label = old
    assert t[("bachelor", "BY")]["A"] == pytest.approx(300 / 1.5) and t[("bachelor", "BY")]["B"] == pytest.approx(50 / 0.5)
    assert t[("bachelor", "DE")]["P"] == pytest.approx(80.0) and t[("master", "BY")]["A"] == pytest.approx(40 * 0.5 / 1)
    assert C.anchor_of({"A": 0.5, "P": 0.5}, t, "bachelor") == (pytest.approx(0.5 * 200 + 0.5 * 80), pytest.approx(0.5))
    assert C.anchor_of({"A": 1.0}, t, "bachelor") == (pytest.approx(200.0), 0.0)


@needs("data/interim/funnel2_capture.csv", "data/interim/funnel2_step6.json", "data/interim/funnel2_screen.csv", "data/interim/funnel2_demand.csv")
def test_the_table_has_every_unit_and_the_arithmetic_of_the_rule():
    o = pd.read_csv(INTERIM / "funnel2_capture.csv", float_precision="round_trip", keep_default_na=False, na_values=[""])
    s = pd.read_csv(INTERIM / "funnel2_screen.csv", float_precision="round_trip")
    dm = pd.read_csv(INTERIM / "funnel2_demand.csv", float_precision="round_trip")
    r = json.loads((INTERIM / "funnel2_step6.json").read_text(encoding="utf-8"))
    assert len(o) == len(s) == r["units"] == 1285 and r["stamp"]["clean"]
    assert (o[["type", "level"]].to_numpy() == s[["type", "level"]].to_numpy()).all() and (o["primary"] == s["primary"]).all() and (o["stress"] == s["stress"]).all()
    assert o["primary"].sum() == 365 and o["stress"].sum() == 1241
    assert np.allclose(o["gross central"], o["anchor"] * o["scale"]) and np.allclose(o["gross low"], o["gross central"] * 0.33) and np.allclose(o["gross high"], o["gross central"] * 3.0)
    assert np.allclose(o["net-new central"], o["gross central"] * (1 - o["share from OTH (central)"]))
    assert np.allclose(o["net-new low"], o["gross low"] * (1 - o["share from OTH (pessimistic)"])) and np.allclose(o["net-new high"], o["gross high"] * (1 - o["share from OTH (optimistic)"]))
    assert (o["net-new low"] <= o["net-new central"] + 1e-9).all() and (o["net-new central"] <= o["net-new high"] + 1e-9).all()
    # a larger w takes more from OTH; between 1.0 and 0.5 the share can turn where OTH's site is the new site (the new programme's origins shift)
    assert (o["share from OTH (pessimistic)"] >= o["share from OTH (optimistic)"] - 1e-12).all() and (o["share from OTH (central)"] >= o["share from OTH (optimistic)"] - 1e-12).all()
    assert (o.loc[o["primary"], "share from OTH (pessimistic)"] >= o.loc[o["primary"], "share from OTH (central)"]).all()
    assert o["share from OTH (optimistic)"].between(0, 1).all() and (o["OTH sites"] >= 1).all() and (o["anchor"] >= 0).all()
    flagged = o["scale flag"].fillna("") == "no Bavarian comparator"
    assert (flagged == (o["Bavarian competitor sites"] == 0)).all() and (o.loc[flagged, "scale"] == 1.0).all()
    assert (o["below the minimum cohort"] == (o["gross central"] < 20)).all() and r["primary_below_the_minimum_cohort"] + r["primary_at_or_above"] == 365
    fs = dm.set_index(["type", "level"])["foreign share last BY"].reindex(pd.MultiIndex.from_frame(o[["type", "level"]])).to_numpy()       # on top, never inside
    ok = np.isfinite(fs) & (fs < 1)
    assert np.allclose(o["international on top, up to"].to_numpy()[ok], (o["gross central"].to_numpy() * fs / (1 - fs))[ok])


@needs("data/interim/funnel2_capture.csv", "data/interim/funnel2_offer_types.csv", "data/interim/funnel2_step2.json", "data/interim/funnel2_screen.csv")
def test_sites_anchor_and_scale_recomputed_for_a_sample():
    from study_program_intelligence.analysis.demand_split import load
    from study_program_intelligence.analysis.funnel_units import SUBJECT_MAP, load_step2, pool_weights
    o = pd.read_csv(INTERIM / "funnel2_capture.csv", float_precision="round_trip", keep_default_na=False, na_values=[""])
    d, t, emb, cent = load_step2()
    smap = pd.read_csv(SUBJECT_MAP).set_index("label")["code"].to_dict()
    table = C.per_offer(d, smap, load(), C.TRANSITION)
    pools = {lv: C.origins(x) for lv, x in C.ORIGINS.items()}
    for row in o[o["primary"]].sample(25, random_state=0).itertuples():
        c, lv = row.type, row.level
        dist = 1 - emb @ cent[c]
        sim = d[~d["is_oth"].astype(bool) & ~d["distance_only"].astype(bool) & (d["level"] == lv) & ((d["assigned_type"] == c) | (dist <= t["radius_90"][c])) & d["lat"].notna()]
        sites = sim.drop_duplicates(["institution", "city"])
        assert o.at[row.Index, "competitor sites"] == len(sites) and o.at[row.Index, "Bavarian competitor sites"] == (sites["state"] == "Bayern").sum()
        a = d[(d["assigned_type"] == c) & (d["level"] == lv)]
        anchor, de = C.anchor_of(pool_weights(a, smap), table, lv)
        assert o.at[row.Index, "anchor"] == pytest.approx(anchor) and o.at[row.Index, "pool weight on Germany-wide values"] == pytest.approx(de)
        own = d[d["is_oth"].astype(bool) & (d["level"] == lv) & (d["assigned_type"] == c)]
        if own.empty:
            cand = d[d["is_oth"].astype(bool) & (d["level"] == lv)]
            own = cand.loc[[cand.index[np.argmin(dist[cand.index])]]]
        own = own.drop_duplicates(["institution", "city"])
        g = sim.groupby(["institution", "city"], as_index=False).agg(lat=("lat", "median"), lon=("lon", "median"), state=("state", "first"))
        lat, lon = np.r_[g["lat"], own["lat"]], np.r_[g["lon"], own["lon"]]
        is_oth = np.r_[np.zeros(len(g), bool), np.ones(len(own), bool)]
        res = C.huff(pools[lv], lat, lon, np.where(is_oth, 0.5, 1.0), is_oth, np.zeros(len(lat), bool), C.NEW_SITE[lv])
        bav = (g["state"] == "Bayern").to_numpy()
        assert o.at[row.Index, "scale"] == pytest.approx(res["new"] / res["sites"][:len(g)][bav].mean() if bav.any() else 1.0)
        assert o.at[row.Index, "share from OTH (central)"] == pytest.approx(res["a"])
