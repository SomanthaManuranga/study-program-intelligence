"""Timetable parser: pure helpers always; the parse itself only when the (git-ignored) PDFs are present."""

import csv

import pytest

from study_program_intelligence.transform import timetable as T


def test_label_is_neutral_and_distinct_from_prof_labels():
    assert T.label(0) == "T01" and T.label(97) == "T98"


def test_split_name_and_kind():
    assert T.split_name("Elektrotechnik 1 (Vorlesung)") == ("Elektrotechnik 1", "lecture")
    assert T.split_name("Elektrotechnik (Praktikum)") == ("Elektrotechnik", "lab")
    assert T.split_name("Audioproduktion (Grundlagen)") == ("Audioproduktion (Grundlagen)", "")
    assert T.kind_from_code("MFI1_Ue_Z") == "exercise" and T.kind_from_code("GDI") == ""


def test_room_pattern():
    for ok in ("EMI214", "MBUTE10", "DC107", "EMI104,EMI311", "online,EMI108"):
        assert T.ROOM.match(ok), ok
    for bad in ("Deutsch A2.2", "Industrie 4.0 Projekt", "EMI3", "nach Absprache"):
        assert not T.ROOM.match(bad), bad


def test_programme_of():
    assert T.programme_of("EI 3") == "EI" and T.programme_of("IK6") == "IK"
    assert T.programme_of("GI 4 - LM") == "GI-LM" and T.programme_of("MAI_BC") == "MAI BC"


@pytest.mark.skipif(not list(T.IN_DIR.glob("*.pdf")), reason="timetable PDFs are a manual, git-ignored input")
def test_parse_meets_criteria():
    assert T.main() == 0
    rows = list(csv.DictReader((T.OUT_DIR / "timetable_sessions.csv").open(encoding="utf-8")))
    names = {r["name"] for r in csv.DictReader((T.OUT_DIR / "timetable_lecturer_key.csv").open(encoding="utf-8"))}
    assert len(rows) > 900
    assert all(r["module"] for r in rows)                                    # T2
    assert sum(1 for r in rows if r["lecturer_label"]) / len(rows) >= 0.95   # T3
    for f in ("timetable_sessions.csv", "timetable_modules.csv", "timetable_capability.csv", "timetable_rooms.csv"):
        text = (T.OUT_DIR / f).read_text(encoding="utf-8")
        cells = {c.strip() for line in text.splitlines() for c in line.replace(";", ",").split(",")}
        assert not (names & cells), f                                        # T5: no lecturer name as a cell value
