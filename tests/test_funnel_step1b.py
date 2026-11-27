"""Funnel step 1b: the matching threshold is calibrated on EMI's own handbooks only (docs/criteria_funnel_step1b.md)."""

import inspect
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
INTERIM = REPO / "data" / "interim"
needs = lambda *files: pytest.mark.skipif(not all((REPO / f).exists() for f in files), reason="no generated data")


def test_pairs_follow_the_written_procedure():
    from study_program_intelligence.analysis import funnel_modules as M
    bases = ["zero", "alpha", "bravo", "carol", "delta", "echo"]
    long = lambda seed: " ".join(bases[seed] + chr(97 + k % 26) + chr(97 + k // 26) for k in range(40))      # 40 words no other text has
    d = pd.DataFrame([
        {"title": "Datenbanken", "text": long(1), "source_file": "a.pdf", "programme_id": "A"},            # 0: anchor, partner 1
        {"title": "Datenbanken (Vorlesung)", "text": long(2), "source_file": "b.pdf", "programme_id": "B"},  # 1: same title after normalising
        {"title": "Datenbanken", "text": long(1), "source_file": "c.pdf", "programme_id": "C"},            # 2: copy of 0, independent of 1
        {"title": "Regelungstechnik", "text": long(3), "source_file": "b.pdf", "programme_id": "B"},       # 3: other topic
        {"title": "Datenbanken 2", "text": long(4), "source_file": "c.pdf", "programme_id": "C"},          # 4: shares a content word
        {"title": "Datenbanken", "text": long(5), "source_file": "a.pdf", "programme_id": "A"},            # 5: same handbook as 0
    ])
    s = np.full((6, 6), 0.1)
    s[0, 1] = s[1, 0] = 0.8
    s[0, 3] = s[3, 0] = 0.3
    s[0, 4] = s[4, 0] = 0.9          # must not count as a negative: the title shares "datenbanken"
    values, counts = M.pair_values(d, s)
    assert counts["copies_left_out"] == 1                      # 0-2 is a copy; 0-5 is the same handbook and is no pair at all
    row = values.set_index("module").loc[0]
    assert row["positive"] == 0.8 and row["negative"] == 0.3
    assert 3 not in set(values["module"])                      # a module without a same-title partner is no anchor


def test_generic_titles_get_no_negative_value():
    from study_program_intelligence.analysis import funnel_modules as M
    assert M.content_words("Grundlagen und Praktikum 2") == frozenset()
    assert M.content_words("Einführung in die Regelungstechnik (Übung)") == frozenset({"regelungstechnik"})


def test_calibration_reads_only_the_emi_handbooks():
    from study_program_intelligence.analysis import funnel_modules as M
    src = inspect.getsource(M)
    assert M.EMI_MODULES.name == "modules_emi_2026.csv"
    assert src.count("read_csv(") == 1 and "modules_references" not in src and "CALIBRATION" not in src and "funnel_refs" not in src


@needs("data/interim/funnel2_threshold.json")
def test_threshold_in_the_rules_is_the_neutral_one():
    r = json.loads((INTERIM / "funnel2_threshold.json").read_text(encoding="utf-8"))
    rules = yaml.safe_load((REPO / "configs" / "funnel.yaml").read_text(encoding="utf-8"))
    assert r["stamp"]["clean"] is True and r["source"].endswith("modules_emi_2026.csv")
    assert r["positives"] >= 30 and r["negatives"] >= 30
    assert rules["feasibility_gate"]["covered_threshold"] == r["value"]
    assert r["former_value"] in rules["stress_tests"]["downstream_factorial"]["matching_threshold"]
