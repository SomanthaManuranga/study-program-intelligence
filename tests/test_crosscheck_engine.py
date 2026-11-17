"""Engine tests: rules change results, every removal has a reason, runs are reproducible. Skipped without data/."""

import copy

import pytest

from study_program_intelligence.crosscheck import engine as E

pytestmark = pytest.mark.skipif(not E.INPUTS[0].exists(), reason="needs the local data folder")


@pytest.fixture(scope="module")
def prep():
    return E.prepare()


def test_agreed_rules_have_no_changes():
    assert E.rules_differ(E.agreed_rules()) == []


def test_every_removed_kind_has_a_reason(prep):
    r = E.run(prep, E.agreed_rules())
    removed = set(r["kinds"].loc[~r["kinds"].eligible, "kind"])
    assert removed <= set(r["drop_log"].kind)
    assert r["drop_log"].reason.str.len().min() > 20


def test_same_rules_same_result(prep):
    a, b = E.run(prep, E.agreed_rules()), E.run(prep, E.agreed_rules())
    assert a["ranking"].score.tolist() == b["ranking"].score.tolist()


def test_dropping_relabel_risk_removes_flagged_kinds(prep):
    rules = copy.deepcopy(E.agreed_rules())
    rules["step2_relabel"]["relabel_risk_action"] = "drop"
    r = E.run(prep, rules)
    assert not (r["ranking"].relabel_risk).any()
    assert r["changed"] == ["step2_relabel.relabel_risk_action: flag -> drop"]
