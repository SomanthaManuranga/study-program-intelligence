"""Funnel step 7: references, blind rows, marks and the gate (configs/funnel.yaml: feasibility_gate; docs/criteria_funnel_step7.md)."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from study_program_intelligence.analysis import funnel_feasibility as F

REPO = Path(__file__).resolve().parents[1]
INTERIM = REPO / "data" / "interim"
needs = lambda *files: pytest.mark.skipif(not all((REPO / f).exists() for f in files), reason="no generated data")


def test_constants_follow_the_rule():
    g = F.config()["feasibility_gate"]
    assert g["band"] == {"min": 0.40, "max": 0.80} and g["one_programme"]["max"] == 0.80
    assert "165 (bachelor) / 60 (master)" in g["references"]["scaling"] and F.TAUGHT == {"bachelor": 165.0, "master": 60.0}
    assert "10 (bachelor) or 5 (master)" in g["hand_check"]["computed_T_and_X"] and F.T_CAP == {"bachelor": 10.0, "master": 5.0}
    assert "0.10" in g["references"]["one_only"] and F.SINGLE_WIDEN == 0.10
    assert "10 rows per eligible candidate" in g["hand_check"]["sample_check"] and F.DRAWN == 10 and F.MAY_DIFFER == 1
    assert "with the 5 EMI modules most similar" in g["hand_check"]["rows"] and "up to 5 more" in g["hand_check"]["rows"] and "3,000 characters" in g["hand_check"]["rows"]
    assert (F.NEAREST, F.TITLE_EXTRA, F.SUBJECTS, F.EMI_TEXT) == (5, 5, 3, 3000) and "third reader" in g["hand_check"]["final_verdict"]
    assert "6 are eligible" in F.config()["shortlist"]["gate_list"] and F.GATE_RULE == (6, 3, 20)


def test_completeness_counts_only_the_required_electives():
    m = pd.DataFrame({"ects": [100, 15, 30, 40], "kind": ["compulsory", "thesis", "elective", "elective"]})
    assert F.complete(m, {"programme_ects": 180, "elective_ects_required": 30}, 0.8) == (True, pytest.approx(145 / 180))
    assert F.complete(m, {"programme_ects": 210, "elective_ects_required": 30}, 0.8)[0] is False                  # 145 / 210 = 0.69
    assert F.complete(m.assign(ects=[100, 15, np.nan, 40]), {"programme_ects": 180, "elective_ects_required": 30}, 0.8)[0] is False


def test_elective_fill_and_its_bounds():
    g = pd.DataFrame({"kind": ["compulsory"] * 3 + ["elective"] * 4, "ects": [50.0, 50.0, 40.0, 10.0, 10.0, 10.0, 10.0]})
    flag = pd.Series([True, False, True, True, False, False, False])
    f = F.fill_figures(g, flag, 165.0)                         # 140 compulsory; 25 of 40 elective ECTS fill the gap
    assert f["counted"] == 165 and f["fill"] == 25
    assert f["share"] == pytest.approx((90 + 25 * 10 / 40) / 165)
    assert f["best"] == pytest.approx((90 + 10) / 165) and f["worst"] == pytest.approx((90 + 0) / 165)
    assert F.fill_figures(g.assign(kind="compulsory"), flag, 60.0)["counted"] == 180                               # no fill if compulsory ECTS exceed the target


def test_nearest_shows_each_title_once_and_only_allowed_modules():
    sim = np.array([0.9, 0.85, 0.8, 0.7, 0.6])
    titles = np.array(["a", "a", "b", "c", "d"])
    assert F.nearest(sim, titles, np.ones(5, bool), 3) == [0, 2, 3]
    assert F.nearest(sim, titles, np.array([False, True, False, True, True]), 3) == [1, 3, 4]
    words = [frozenset({"software"}), frozenset({"software"}), frozenset({"netze"}), frozenset(), frozenset({"software", "engineering"})]
    assert F.title_matches("Software Engineering", sim, titles, words, np.ones(5, bool), [0]) == [4]          # copy of module 0 (same title) not repeated


def test_copies_of_one_module_are_one_title():
    assert F.same_module("[ CNW ]    Computernetzwerke") == F.same_module("Computernetzwerke") == "computernetzwerke"
    assert F.same_module("[ MA2 ]    Mathematik 2 (Diskrete Mathematik)") == "mathematik 2"


def test_title_words_cross_english_and_german():
    assert F.title_words("Theoretical Computer Science") & F.title_words("Theoretische Informatik")
    assert F.title_words("Datenbanksysteme") == F.title_words("Databases")
    assert F.title_words("[ CNW ]    Computernetzwerke") & F.title_words("Computer Networks")


def test_which_may_name_two_modules():
    assert F.which_numbers("3+5") == [3, 5] and F.which_numbers("2") == [2] and F.which_numbers("2.0") == [2] and F.which_numbers("") == [] and F.which_numbers(np.nan) == []


def test_near_band_marks_whole_candidates():
    key = pd.DataFrame({"row": ["R1", "R2", "R3", "R4"], "ref": ["1_bachelor_a"] * 2 + ["2_bachelor_a"] * 2, "type": [1, 1, 2, 2], "level": ["bachelor"] * 4,
                        "kind": ["compulsory"] * 4, "ects": [70.0, 95.0, 20.0, 145.0], "order": [0, 1, 0, 1]})
    first = pd.DataFrame({"verdict": ["E2", "N", "E1", "new"]}, index=["R1", "R2", "R3", "R4"])
    assert F.near_band(key, first, {"band": {"min": 0.4, "max": 0.8}}) == {(1, "bachelor"): [0.424]}          # 70/165 near 0.40; 20/165 = 0.12 is not


def test_timetable_subject_without_its_form():
    assert F.subject_name("Informatik 1 (Vorlesung)") == "Informatik 1"
    assert F.subject_name("Elektrotechnik 2 (Praktikum)") == "Elektrotechnik 2"
    assert F.subject_name("Datenbanken") == "Datenbanken"


def test_drawn_rows_are_reproducible_and_per_candidate():
    key = pd.DataFrame({"row": [f"R{i:04d}" for i in range(30)], "ref": ["1_bachelor_a"] * 15 + ["1_bachelor_b"] * 10 + ["2_master_a"] * 5,
                        "order": list(range(15)) + list(range(10)) + list(range(5)), "type": [1] * 25 + [2] * 5, "level": ["bachelor"] * 25 + ["master"] * 5})
    d = F.drawn_rows(key)
    assert len(d[(1, "bachelor")]) == 10 and len(set(d[(1, "bachelor")])) == 10 and sorted(d[(2, "master")]) == [f"R{i:04d}" for i in range(25, 30)]
    assert d == F.drawn_rows(key.sample(frac=1, random_state=3))                                                    # the file order does not matter


def test_the_walk_stops_and_skips_as_the_rule_says(tmp_path, monkeypatch):
    monkeypatch.setattr(F, "TABLES", tmp_path)
    order = pd.DataFrame({"gate order": range(1, 9), "type": [10, 11, 12, 13, 14, 15, 16, 17], "level": ["bachelor"] * 5 + ["master"] * 3})
    for i in range(1, 8):
        (tmp_path / f"tries_{i}.json").write_text("[]", encoding="utf-8")
    metas = {f"{t}_{lv}_a": {"type": t, "level": lv, "complete": t != 11} for t, lv in zip(order["type"], order["level"])}
    w = F.walk(order, metas, {(13, "bachelor"): "mixed type, all 2 titles read"}, (6, 3, 20))
    assert list(w["status"]) == ["eligible", "tried, not eligible", "eligible", "not a candidate", "eligible", "eligible", "eligible", "not yet tried"]
    w = F.walk(order, metas, {}, (6, 3, 2))                                                                         # stop at 2 tried
    assert list(w["status"]) == ["eligible", "tried, not eligible"]
    order2 = pd.DataFrame({"gate order": range(1, 6), "type": [10, 12, 14, 15, 16], "level": ["bachelor"] * 5})
    w = F.walk(order2, metas, {}, (6, 3, 20))
    assert list(w["status"])[:5] == ["eligible", "eligible", "eligible", "skipped", "skipped"]                    # a 4th eligible bachelor is not looked for


@needs("data/interim/funnel2_rows.json", "data/interim/funnel2_rows_key.csv")
def test_rows_are_blind():
    sheet = json.loads((INTERIM / "funnel2_rows.json").read_text(encoding="utf-8"))
    key = pd.read_csv(INTERIM / "funnel2_rows_key.csv")
    assert len(sheet["rows"]) == len(key) and [r["row"] for r in sheet["rows"]] == list(key["row"])
    import re
    text = " ".join(r["module"] + " " + r["description"] for r in sheet["rows"])      # the reference's own texts; EMI's are OTH's by design
    metas = {f.stem: json.loads(f.read_text(encoding="utf-8")) for f in (INTERIM / "funnel2_refs").glob("*_[ab].json")}
    for t in F.blind_terms(metas):
        assert not re.search(rf"(?<![\wäöüß]){re.escape(t)}(?![\wäöüß])", text, flags=re.I), t
    assert not re.search(rf"\b({'|'.join(F.ACRONYMS)})\b(?=[\s.,;:)-]|$)", text)
    assert not re.search(r"\b[BM]-[A-Z]{2,4}-\d{1,3}\b", text) and F.redact("B-CY-19 Software Engineering", []) == "Software Engineering"
    assert not any(re.search(rf"(?<![\wäöüß]){re.escape(x)}(?![\wäöüß])", text) for x in F.LAENDER)
    assert F.redact("BM3A-II-1 FEM (KIB) in Schleswig-Holstein", []) == "FEM in [region]"
    assert F.redact("an der HTWK Leipzig und der OTH Regensburg; other Tübbingen", ["Leipzig", "Regensburg"]) == "an der [university] [university] und der [university] [university]; other Tübbingen"
    for r in sheet["rows"]:
        assert set(r) == {"row", "module", "credit points", "level of the programme", "description", "EMI modules", "timetable subjects"}
        assert 5 <= len(r["EMI modules"]) <= 10 and len(r["timetable subjects"]) == 3 and len({F.same_module(e["title"]) for e in r["EMI modules"]}) == len(r["EMI modules"]) and not any("similar" in k for e in r["EMI modules"] for k in e)
    tt = pd.read_csv(INTERIM / "timetable_subjects.csv")
    assert tt["lecturer"].dropna().astype(str).str.fullmatch(r"L\d{3}|.{0,3}").all()          # the timetable holds labels only, and no label is shown
    assert not re.search(r"\bL\d{3}\b", json.dumps(sheet, ensure_ascii=False))
    emi = [e["description"] for r in sheet["rows"] for e in r["EMI modules"]]
    assert not any(re.search(r"Prof\.|Dr\.", x) for x in emi)                                              # no person
    assert np.mean([bool(re.search(r"Modulverantwortlich|Module Convenor", x)) for x in emi]) < 0.05      # form headers only where a handbook's layout leaves them
    assert np.median([len(x) for x in emi]) > 800                                                            # the content is shown, not the header


def test_emi_text_is_content_without_persons():
    raw = ("Basics Zuordnung zum Curriculum Modul-ID GBI 5 Modulverantwortliche Module Convenor Prof. Dr. Erika Muster Voraussetzungen keine "
           "Lernziele/Qualifikationen des Moduls Learning Outcomes Die Studierenden kennen Netze, betreut von Prof. Dr. Erika Muster. " + "Sie bauen Netze auf. " * 12 + "Literatur Buch A")
    t = F.emi_text(raw, "Rechnernetze")
    assert t.startswith("Lernziele") and "Sie bauen" in t and "Muster" not in t and "Prof" not in t and "Modulverantwortliche" not in t and "Buch A" not in t


@needs("data/interim/funnel2_rows_final.csv", "data/interim/funnel2_gate_references.csv", "data/interim/funnel2_gate.csv", "data/interim/funnel2_step7.json")
def test_overlap_and_verdicts_recomputed_from_the_marks():
    k = pd.read_csv(INTERIM / "funnel2_rows_final.csv", keep_default_na=False, na_values=[""])
    refs = pd.read_csv(INTERIM / "funnel2_gate_references.csv")
    gate = pd.read_csv(INTERIM / "funnel2_gate.csv")
    m1, m2 = pd.read_csv(REPO / "docs" / "funnel_module_marks_1.csv", keep_default_na=False).set_index("row"), pd.read_csv(REPO / "docs" / "funnel_module_marks_2.csv", keep_default_na=False).set_index("row")
    cov = lambda v: v in ("E1", "E2")
    m3 = pd.read_csv(REPO / "docs" / "funnel_module_marks_3.csv", keep_default_na=False).set_index("row") if (REPO / "docs" / "funnel_module_marks_3.csv").exists() else pd.DataFrame()
    for r in k.itertuples():                                                    # the final verdict of every row, written out
        first = m1.at[r.row, "verdict"]
        if r.row not in m2.index or cov(first) == cov(m2.at[r.row, "verdict"]):
            assert r.final == first
        else:
            assert r.final == m3.at[r.row, "verdict"]
    for ref in refs.itertuples():
        g = k[k["ref"] == ref.ref]
        taught = 165.0 if ref.level == "bachelor" else 60.0
        comp, elec = g[g["kind"] == "compulsory"], g[g["kind"] == "elective"]
        fill = min(max(taught - comp["ects"].sum(), 0), elec["ects"].sum())
        c = comp.loc[comp["final"].isin(["E1", "E2"]), "ects"].sum() + (fill * elec.loc[elec["final"].isin(["E1", "E2"]), "ects"].sum() / elec["ects"].sum() if len(elec) else 0)
        assert ref.overlap == pytest.approx(c / (comp["ects"].sum() + fill))
    for c in gate.itertuples():
        rr = refs[(refs["type"] == c.type) & (refs["level"] == c.level)]
        ok = (rr["overlap"] >= 0.40) & (rr["largest share from one programme"] <= 0.80) & (rr["share lab"] == 0)
        want = ("existing-resources passer" if (rr["X ECTS"] <= 1e-9).all() else "band passer") if ok.all() else ("reference-dependent" if ok.sum() == 1 else "fail")
        assert c.verdict == want and c.references == len(rr)
