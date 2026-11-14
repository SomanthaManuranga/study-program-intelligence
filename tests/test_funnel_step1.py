"""Funnel step 1 (data inventory): rules file, timetable parser, protection of internal data, threshold."""

import json
import re
import subprocess
from pathlib import Path

import pandas as pd
import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
INTERIM = REPO / "data" / "interim"
INTERNAL = REPO / "data" / "raw" / "oth_internal"
needs = lambda *files: pytest.mark.skipif(not all((REPO / f).exists() for f in files), reason="no generated data")


def rules() -> dict:
    return yaml.safe_load((REPO / "configs" / "funnel.yaml").read_text(encoding="utf-8"))


def test_rules_file_parses_and_keeps_the_supervisors_band():
    r = rules()
    g = r["feasibility_gate"]
    assert g["band"] == {"min": 0.40, "max": 0.80}
    assert g["one_programme"]["max"] == g["band"]["max"]
    w = r["capture"]["w_substitute"]
    assert w["pessimistic"] > w["central"] > w["optimistic"]            # pessimistic = most students taken from OTH
    assert r["capture"]["min_cohort"]["value"] == 20


def test_no_origin_tag_ended_up_inside_a_rule_value():
    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                yield from walk(v)
        elif isinstance(x, list):
            for v in x:
                yield from walk(v)
        elif isinstance(x, str):
            yield x
    assert not [v for v in walk(rules()) if re.search(r"\[[SLCJKN]\]", v)]


def test_timetable_cell_is_read_from_positions():
    from study_program_intelligence.transform import timetables as T
    f = lambda x, y, t, size=6.4: {"x": x, "y": y, "size": size, "text": t}
    frags = [f(163.4, 499.9, "Mo", 11.8), f(306.7, 499.9, "Di", 11.8),
             f(160.0, 435.6, "AB1_VL"), f(162.0, 425.5, "Muster"), f(160.6, 415.5, "EMI013"),                    # Monday: code, lecturer, room
             f(300.0, 435.6, "PK 2"), f(301.0, 425.5, "Beispiel-Name"), f(296.0, 415.5, "online,EMI102"), f(298.0, 405.4, "nach Absprache"),
             f(76.3, 397.7, "2", 11.8)]
    cells, orphans = T.grid_cells(frags, {"AB1_VL", "PK 2"})
    assert not orphans
    assert cells[0] == {"code": "AB1_VL", "lecturer": "Muster", "room": "EMI013", "note": "", "day": "Mo", "y": 435.6}
    assert (cells[1]["lecturer"], cells[1]["room"], cells[1]["note"], cells[1]["day"]) == ("Beispiel-Name", "online,EMI102", "nach Absprache", "Di")


def test_subject_list_keeps_codes_with_a_space():
    from study_program_intelligence.transform import timetables as T
    f = lambda x, y, t: {"x": x, "y": y, "size": 9.0, "text": t}
    frags = [f(56.2, 496.6, "Name"), f(97.9, 496.6, "Langname"), f(56.2, 484.3, "PK 2"), f(97.9, 484.3, "Programmieren 2"), f(751.7, 36.5, "Seite 2 / 80")]
    assert T.subject_list(frags) == {"PK 2": "Programmieren 2"}


@needs("data/interim/timetable_subjects.csv", "data/interim/timetable_report.json")
def test_timetables_are_complete_and_carry_no_names():
    t = pd.read_csv(INTERIM / "timetable_subjects.csv")
    rep = json.loads((INTERIM / "timetable_report.json").read_text(encoding="utf-8"))
    assert sum(f["pages"] for f in rep["files"]) == 160 and all(f["cell_texts_in_no_cell"] == 0 for f in rep["files"])
    assert t["subject"].notna().all()                                              # every code is in its group's subject list
    grid = t[t["in_grid"]]
    assert grid["lecturer"].notna().all() and grid["lecturer"].str.fullmatch(r"L\d{3}").all()
    labels = INTERNAL / "lecturer_labels.csv"
    if labels.exists():
        names = set(pd.read_csv(labels)["name"])
        text = (INTERIM / "timetable_subjects.csv").read_text(encoding="utf-8")
        assert not [n for n in names if re.search(rf"(?<![A-Za-zÄÖÜäöüß]){re.escape(n)}(?![A-Za-zÄÖÜäöüß])", text) and n not in set(t["subject"].str.split().explode())]


def test_offer_list_does_not_depend_on_the_file_order(monkeypatch):
    """Of several variants the full-time one is kept, then the lowest programme id (rule universe.dedupe)."""
    import pandas as pd
    from study_program_intelligence.analysis import funnel_common as C
    rows = [("1", "Vollzeitstudium"), ("2", "Vollzeitstudium"), ("3", "Teilzeitstudium")]
    frame = lambda order: pd.DataFrame([{"programme_id": i, "institution": "H", "title": "T", "degree": "Master", "country": "Deutschland",
                                         "study_form": f, "content": f"variant {i}"} for i, f in order])
    kept = set()
    for order in (rows, rows[::-1], [rows[1], rows[2], rows[0]]):
        monkeypatch.setattr(pd, "read_csv", lambda *a, _o=order, **k: frame(_o))
        kept.add(C.universe()["programme_id"].iloc[0])
    assert kept == {"1"}


def test_internal_files_are_not_tracked():
    tracked = subprocess.run(["git", "-C", str(REPO), "ls-files", "data"], capture_output=True, text=True).stdout
    assert "oth_internal" not in tracked and "timetable" not in tracked


@needs("data/interim/funnel2_inventory.json")
def test_inventory_covers_the_laender_and_fixes_the_threshold():
    inv = json.loads((INTERIM / "funnel2_inventory.json").read_text(encoding="utf-8"))
    assert inv["stamp"]["clean"] is True
    assert all(v["covers_2019_2024"] and v["own_land_only"] for v in inv["laender"].values()) and len(inv["laender"]) == 15
    assert inv["catalogue"]["subject_labels_not_in_map"] == 0
    assert inv["timetables"]["names_in_table"] == 0
    thr = inv["threshold"]
    assert thr["earlier_report_value"] is None or abs(thr["value"] - thr["earlier_report_value"]) < 0.0005
    assert rules()["feasibility_gate"]["covered_threshold"] == thr["value"]
