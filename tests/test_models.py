"""Model building blocks: distances, gravity model, forecasts, score mappings, Monte Carlo reproducibility."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from study_program_intelligence.analysis import forecast, ranking
from study_program_intelligence.analysis.capture import gravity
from study_program_intelligence.analysis.catchment import haversine

REPO = Path(__file__).resolve().parents[1]
AMBERG, WEIDEN = (49.4425, 11.8558), (49.6761, 12.1603)


def test_haversine_amberg_weiden():
    d = haversine(*AMBERG, *WEIDEN)
    assert 30 < d < 40                      # about 34 km straight line
    assert haversine(*WEIDEN, *AMBERG) == pytest.approx(d)
    assert haversine(*AMBERG, *AMBERG) == pytest.approx(0)


def test_gravity_model_keeps_both_margins():
    rng = np.random.default_rng(1)
    flows = rng.integers(10, 500, size=(4, 5)).astype(float)
    dist = rng.uniform(10, 200, size=(4, 5))
    pred = gravity(flows, dist, beta=1.6)
    assert pred.sum(axis=1) == pytest.approx(flows.sum(axis=1), rel=1e-6)
    assert pred.sum(axis=0) == pytest.approx(flows.sum(axis=0), rel=1e-6)


def test_gravity_decay_prefers_near_destinations():
    flows = np.array([[100.0, 100.0], [100.0, 100.0]])
    dist = np.array([[10.0, 100.0], [100.0, 10.0]])
    pred = gravity(flows, dist, beta=1.6)
    assert pred[0, 0] > pred[0, 1] and pred[1, 1] > pred[1, 0]


def test_drift_and_naive_forecasts_on_a_linear_series():
    y = pd.Series([5.0 + 2 * t for t in range(10)], index=range(2010, 2020))
    assert forecast.f_drift(y, 3) == pytest.approx([25.0, 27.0, 29.0])
    assert forecast.f_naive(y, 3) == pytest.approx([23.0, 23.0, 23.0])


def test_triangular_quantiles():
    u = np.array([0.0, 0.5, 1.0])
    q = ranking.tri_ppf(u, 1.5, 3.0, 4.5)
    assert q[0] == pytest.approx(1.5) and q[1] == pytest.approx(3.0) and q[2] == pytest.approx(4.5)
    assert ranking.tri_ppf(u, 3, 3, 3) == pytest.approx([3, 3, 3])


def test_score_mappings_anchor_points():
    assert ranking.capture_score(np.array([10.0, 80.0, 5.0, 500.0])) == pytest.approx([1, 5, 1, 5])
    assert ranking.regional_score(np.array([1.0, 16.0, 0.2])) == pytest.approx([1, 5, 1])


@pytest.mark.skipif(not (REPO / "data" / "interim" / "option_scenarios.csv").exists(), reason="run analysis.options first")
def test_monte_carlo_is_reproducible():
    cfg, sc, cap = ranking.load()
    a = ranking.summarise(ranking.simulate(cfg, sc, cap, cfg["weights"]))
    b = ranking.summarise(ranking.simulate(cfg, sc, cap, cfg["weights"]))
    pd.testing.assert_frame_equal(a, b)
    assert a["P(rank 1)"].sum() == pytest.approx(1.0)
