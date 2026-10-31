"""Deep-analysis layer (docs/criteria_deep_analysis.md): reproduction gate, module math, output invariants."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
INTERIM = REPO / "data" / "interim"
needs = lambda *files: pytest.mark.skipif(not all((REPO / f).exists() for f in files), reason="no generated data")


# ---------------- D2: the rerun harness reproduces the pre-registered results ----------------

@needs("data/interim/counties_geo.csv", "data/interim/school_leavers_by.csv", "data/interim/capture_scenarios.csv",
       "data/interim/option_scenarios.csv", "data/processed/programmes.csv")
def test_reproduction_gate_passes():
    from study_program_intelligence.analysis import spec_curve as S
    geo = S.load_geo()
    pool = S.load_pool(geo)
    gate = S.reproduction_gate(S.cyber_ratios(pool), S.cyber_shares(pool, geo), S.robotics_runs(geo, pool)[0])
    assert all(gate.values()), gate


@needs("data/interim/spec_curve_capture.csv", "data/interim/spec_curve_ranking.csv")
def test_spec_curve_outputs():
    cap = pd.read_csv(INTERIM / "spec_curve_capture.csv")
    pre = cap[cap["pre-registered"]]
    assert set(pre["candidate"]) == {"cyber", "robotics_b"} and len(pre) == 2
    assert float(pre.loc[pre["candidate"] == "cyber", "gross central"].iloc[0]) == pytest.approx(39.2, abs=0.1)
    assert float(pre.loc[pre["candidate"] == "robotics_b", "gross central"].iloc[0]) == pytest.approx(28.7, abs=0.1)
    assert (cap.groupby("candidate").size() == 2880).all()
    rank = pd.read_csv(INTERIM / "spec_curve_ranking.csv")
    assert len(rank) == 192 and rank["cyber first"].all()
    pre_rank = rank[rank["pre-registered"]]
    assert len(pre_rank) == 1 and float(pre_rank["P1 cyber"].iloc[0]) == pytest.approx(0.917, abs=0.001)


# ---------------- intake model math ----------------

def test_gamma_fit_moments():
    from study_program_intelligence.analysis.intake_model import fit_gamma
    shape, rate, m, v = fit_gamma([25, 42, 44, 60])
    assert m == pytest.approx(42.75) and v == pytest.approx(np.var([25, 42, 44, 60], ddof=1))
    assert shape / rate == pytest.approx(m)                      # Gamma mean
    assert shape / rate ** 2 == pytest.approx(v - m)             # between-programme variance = excess over Poisson
    shape2, rate2, m2, _ = fit_gamma([30, 30, 30, 30])           # under-dispersed sample hits the heterogeneity floor
    assert shape2 / rate2 == pytest.approx(m2) and shape2 / rate2 ** 2 == pytest.approx(0.05 * m2)


def test_intake_predictive_brackets():
    from study_program_intelligence.analysis.intake_model import COMPARABLE, R_ENVELOPE, predictive
    lam, oth, _ = predictive(list(COMPARABLE.values()), np.random.default_rng(1))
    assert lam.min() > 0
    assert (oth / lam).min() >= R_ENVELOPE[0] - 1e-9 and (oth / lam).max() <= R_ENVELOPE[1] + 1e-9
    q = np.quantile(oth, [0.1, 0.5, 0.9])
    assert q[0] < q[1] < q[2]


@needs("data/interim/intake_model.csv")
def test_intake_model_output_consistent_with_preregistered_range():
    t = pd.read_csv(INTERIM / "intake_model.csv")
    oth = t[t["quantity"].str.startswith("OTH intake")].iloc[0]
    assert 21 <= oth["q50"] <= 75                                # the median sits inside the pre-registered range
    assert oth["q05"] < oth["q50"] < oth["q95"]


# ---------------- capture benchmark math ----------------

def test_nearest_site_pools_toy():
    from study_program_intelligence.analysis.capture_benchmark import nearest_site_pools
    pool = pd.DataFrame({"lat": [49.0, 50.0], "lon": [11.0, 12.0], "hzb": [100.0, 200.0]})
    pools = nearest_site_pools(pool, {"A": [(49.0, 11.0)], "B": [(50.0, 12.0)]})
    assert pools == {"A": 100.0, "B": 200.0}


@needs("data/interim/capture_benchmark.csv")
def test_benchmark_shares_arithmetic():
    t = pd.read_csv(INTERIM / "capture_benchmark.csv")
    s = t[t["table"] == "shares"].dropna(subset=["intake"])
    recomputed = (100 * s["intake"] / s["pool"]).round(2)
    assert np.allclose(recomputed, s["implied share %"], atol=0.011)
    own = s[s["pool basis"] == "own pool"]["pool"].iloc[0]
    assert own == 5501                                           # docs/evidence_catchment.md own pool


# ---------------- similarity profile invariants ----------------

@needs("data/interim/cannibalisation_similarity.csv")
def test_similarity_profile_invariants():
    t = pd.read_csv(INTERIM / "cannibalisation_similarity.csv")
    for _, d in t.groupby("candidate"):
        assert d["substitution profile %"].sum() == pytest.approx(100, abs=0.3)
        assert d["centred cosine"].between(-1, 1).all()
        assert (d["raw cosine"] > 0.9).all()                     # documented e5 compression


# ---------------- demand corridor ----------------

@needs("data/interim/demand_corridor.csv", "data/interim/demand_split.csv")
def test_demand_corridor_cyber_uses_validated_model():
    t = pd.read_csv(INTERIM / "demand_corridor.csv").set_index("candidate")
    assert t.at["cyber", "German 2030: model"].startswith("drift (MASE 0.92")
    assert t.at["robotics_b", "German 2030: model"].startswith("naive")
    for cand in t.index:
        lo, hi = (float(x) for x in t.at[cand, "first-years 2030 corridor (central)"].split("-"))
        assert lo <= hi
    assert float(t.at["cyber", "first-years 2030, conservative point"]) >= 39   # validated German path lifts the central


# ---------------- data-quality gate ----------------

@needs("data/interim/counties_geo.csv", "data/interim/demand_split.csv", "data/interim/capture_scenarios.csv",
       "data/processed/programmes_full.csv", "data/interim/pool_backtest.csv")
def test_data_quality_gate_clean():
    from study_program_intelligence.analysis import data_quality as Q
    Q.CHECKS.clear()
    assert Q.main() == 0
