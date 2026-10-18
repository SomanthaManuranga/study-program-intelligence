"""Configuration and report-source integrity (no generated data needed)."""

import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
CONFIGS = sorted((REPO / "configs").glob("*.yaml"))
HAND = ("labour_relevance", "institutional_fit", "feasibility", "differentiation")


def load(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", CONFIGS, ids=lambda p: p.name)
def test_every_config_parses(path):
    assert load(path) is not None


def test_source_register_ids_unique_and_complete():
    src = load(REPO / "configs" / "sources.yaml")["sources"]
    ids = [s["id"] for s in src]
    assert len(ids) == len(set(ids))
    for s in src:
        assert s.get("owner") and (s.get("url") or s.get("table")), s["id"]


def test_weights_sum_to_one():
    cfg = load(REPO / "configs" / "analysis.yaml")
    assert sum(cfg["weights"].values()) == pytest.approx(1.0)
    assert cfg["monte_carlo"]["draws"] > 0 and cfg["monte_carlo"]["dirichlet_concentration"] > 0


def test_score_ranges_valid_and_weak_evidence_symmetric():
    sc = load(REPO / "configs" / "scores.yaml")["options"]
    for opt, s in sc.items():
        for crit in HAND:
            e = s[crit]
            assert 1 <= e["low"] <= e["central"] <= e["high"] <= 5, (opt, crit)
            if e["strength"] == "weak":   # kill_rules.md: weak evidence widens the range symmetrically
                assert e["central"] - e["low"] == pytest.approx(e["high"] - e["central"]), (opt, crit)
        assert s["feasibility"]["central"] > 1, f"{opt}: feasibility gate (kill rule 2)"


def test_report_sections_exist_and_citations_resolve():
    cfg = load(REPO / "docs" / "report" / "report.yaml")
    refs = {r["id"] for r in load(REPO / "docs" / "report" / cfg["citations"]["bibliography"])["references"]}
    for name in cfg["sections"] + cfg.get("appendix", []):
        text = (REPO / "docs" / "report" / name).read_text(encoding="utf-8")
        for key in re.findall(r"@([\w-]+)", re.sub(r"`[^`]*`", "", text)):
            assert key in refs, f"{name}: unknown citation @{key}"
