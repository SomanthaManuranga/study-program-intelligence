"""Key numbers vs. evidence docs, and the report build's number rules (needs the generated data)."""

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(not (REPO / "data" / "interim" / "ranking_loo.csv").exists(),
                                reason="run the pipeline first")


def test_every_key_number_is_found_in_its_source_doc():
    from study_program_intelligence.report.key_numbers import collect
    n = collect()
    missing = [k for k, v in n.items.items() if not v["in_source_doc"]]
    assert not missing, missing
    assert len(n.items) > 150


def test_report_has_no_unknown_placeholders_or_typed_numbers():
    from study_program_intelligence.report.draft import build
    _, problems, stats = build()
    assert not [p for p in problems if not p.startswith("missing")], problems
    assert not stats["missing"], stats["missing"]
    lo, hi = stats["target_pages"]
    assert lo <= stats["pages_main_est"] <= hi + 2


def test_typed_number_check_catches_numbers():
    from study_program_intelligence.report.draft import typed_numbers
    allowed = [r"\b(19|20)\d{2}\b", r"\b\d+ km\b"]
    assert typed_numbers("In 2024 about 39 students, 31 % of them, 1,234 in total, ratio 0.5.", allowed) == \
        ["39", "31 %", "1,234", "0.5"]
    assert typed_numbers("{{cyber_bsc_gross_central}} students within 150 km in 2026 [@destatis2026students].", allowed) == []


def test_defence_qa_source_has_no_typed_numbers():
    """docs/defence/qa.md follows the report's number rules (checked without rewriting the committed output)."""
    import re
    import yaml
    from study_program_intelligence.report.draft import PLACEHOLDER, SRC, typed_numbers
    from study_program_intelligence.report.key_numbers import load
    raw = re.sub(r"<!--.*?-->", " ", (REPO / "docs" / "defence" / "qa.md").read_text(encoding="utf-8"), flags=re.S)
    allowed = yaml.safe_load((SRC / "report.yaml").read_text(encoding="utf-8"))["allowed_numbers"]
    assert typed_numbers(raw, allowed) == []
    kn = load()
    assert all(k.removeprefix("val:") in kn for k in PLACEHOLDER.findall(raw))
    assert len(re.findall(r"^### Q\d+", raw, flags=re.M)) == 25
