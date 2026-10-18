"""Dashboard checks (Step 52): every page runs without an exception, every metric shows exactly the value of its key
number, and the ranking explorer reproduces the report's first-place shares with the chosen weights.

    python -m pytest tests/test_dashboard.py -q

Needs the generated files (reports/key_numbers.yaml, reports/figures, data/interim); skipped if they are missing.
"""

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
APP = REPO / "app"
VIEWS = ["overview", "demand", "capture", "fit", "outlet", "cannibalisation", "ranking", "sources"]

pytestmark = pytest.mark.skipif(not (REPO / "reports" / "key_numbers.yaml").exists(), reason="run report.build first")
sys.path.insert(0, str(APP))


def run(view: str):
    from streamlit.testing.v1 import AppTest
    at = AppTest.from_file(str(APP / "views" / f"{view}.py"), default_timeout=180)
    at.run()
    return at


@pytest.fixture(scope="module")
def kn():
    from study_program_intelligence.report.key_numbers import load
    return load()


@pytest.fixture(scope="module")
def pages():
    return {v: run(v) for v in VIEWS}


@pytest.mark.parametrize("view", VIEWS)
def test_page_runs(pages, view):
    assert not pages[view].exception, [e.value for e in pages[view].exception]


def test_metrics_equal_key_numbers(pages, kn):
    checked = []
    for view, at in pages.items():
        for m in at.metric:
            key, bare = re.search(r"\(key: (\w+)(, bare)?\)", m.proto.help).groups()
            expected = str(kn[key]["value"]) if bare else kn[key]["display"]
            assert m.value == expected, (view, key, m.value, expected)
            checked.append(key)
    assert len(checked) >= 10, checked


def test_ranking_explorer_reproduces_report(pages, kn):
    df = next(d.value for d in pages["ranking"].dataframe if "First place" in d.value.columns)
    first = dict(zip(df["Option"], df["First place"]))
    assert first["Cybersecurity B.Sc."] == kn["p_rank1_cyber_bsc_base"]["display"]
    assert first["Cyber/OT M.Sc."] == kn["p_rank1_cyber_msc_base"]["display"]
    assert first["Robotics + AI B.Sc."] == kn["p_rank1_robotics_bsc_base"]["display"]


def test_explorer_zero_weight_equals_leave_one_out(kn):
    """Setting a weight to 0 in the explorer must give the report's leave-one-out result, and Reset must restore it."""
    at = run("ranking")
    next(s for s in at.slider if s.label == "student demand").set_value(0.0).run()
    df = next(d.value for d in at.dataframe if "First place" in d.value.columns)
    assert dict(zip(df["Option"], df["First place"]))["Cybersecurity B.Sc."] == kn["loo_min_cyber_bsc"]["display"]
    at.button[0].click().run()
    df = next(d.value for d in at.dataframe if "First place" in d.value.columns)
    assert dict(zip(df["Option"], df["First place"]))["Cybersecurity B.Sc."] == kn["p_rank1_cyber_bsc_base"]["display"]
