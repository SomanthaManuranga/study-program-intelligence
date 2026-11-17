"""Cross-check helpers (pure functions; no data needed)."""

from study_program_intelligence.crosscheck.common import base_subject, destatis_match, subjects_of
from study_program_intelligence.crosscheck.steps import topics_of


def test_subjects():
    assert base_subject("Informatik (grundständig)") == "Informatik"
    assert subjects_of("Informatik (weiterführend); Datenwissenschaft, Data Science (weiterführend)") == \
        ["Informatik", "Datenwissenschaft, Data Science"]


def test_destatis_match():
    labels = ["Informatik", "Elektrotechnik/Elektronik", "Rechtswissenschaft", "Mechatronik"]
    assert destatis_match("IT-Sicherheit", labels) == ("Informatik", "manual")
    assert destatis_match("Informatik", labels) == ("Informatik", "exact")
    assert destatis_match("Archivwissenschaft", labels)[0] is None      # the v1 false match must not come back


def test_topics():
    t = topics_of("Schwerpunkte: : IT-Sicherheit, Kryptographie, Software Engineering Anmerkung der Hochschule: x")
    assert t == ["it-sicherheit", "kryptographie", "software engineering"]
    assert topics_of("Inhalte bitte bei der Hochschule erfragen") == []
