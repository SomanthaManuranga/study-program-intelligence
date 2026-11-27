"""Rules version 4, R1 (docs/criteria_funnel_v4_merge.md, M7): the title normalisation and the partner readings."""

import pandas as pd
import pytest

from study_program_intelligence.analysis.funnel_common import config
from study_program_intelligence.analysis.funnel_merge import candidates, normaliser


@pytest.fixture(scope="module")
def norm():
    return normaliser(config()["version_4"]["title_merge"])


@pytest.mark.parametrize("title, expected", [
    ("Informatik", "informatik"),
    ("Computer Science", "informatik"),
    ("Informatik / Computer Science", "informatik"),
    ("International Computer Science", "informatik"),
    ("Angewandte Informatik", "informatik"),
    ("Informatik (dual)", "informatik"),
    ("Informatik - dual", "informatik"),
    ("Allgemeine Informatik", "informatik"),
    ("Elektro- und Informationstechnik", "elektrotechnik informationstechnik"),
    ("Electrical Engineering and Information Technology", "elektrotechnik informationstechnik"),
    ("Business Informatics", "wirtschaftsinformatik"),
    ("Bioinformatics", "bioinformatics"),
    ("Data Science", "data science"),
    ("Cyber Security", "it sicherheit"),
    ("IT-Sicherheit", "it sicherheit"),
    ("Medieninformatik", "medieninformatik"),
])
def test_normalise(norm, title, expected):
    assert norm(title) == expected


def frame(rows):
    return pd.DataFrame(rows, columns=["type", "level", "group", "main", "at_oth"])


def test_title_group_and_one_partner():
    u = candidates(frame([(1, "bachelor", 1, "informatik", False), (2, "bachelor", 1, "technische informatik", False),
                          (3, "bachelor", 3, "informatik", False), (4, "bachelor", 4, "physik", False)]))
    c = dict(zip(u["type"], u["candidate"]))
    assert c[1] == c[3] == c[2] == 1                          # 1 and 3 by title, 2 as the partner of 1 (E2)
    assert c[4] == 4
    assert set(u.loc[u["type"] == 2, "how"]) == {"partner"}


def test_partner_of_two_title_groups_joins_none():
    u = candidates(frame([(1, "bachelor", 1, "informatik", False), (5, "bachelor", 5, "informatik", False),
                          (2, "bachelor", 1, "data science", False), (6, "bachelor", 6, "data science", False),
                          (3, "bachelor", 1, "statistik", False)]))
    c = dict(zip(u["type"], u["candidate"]))
    assert c[1] == c[5] == 1 and c[2] == c[6] == 2            # each title-matched unit stays with its title (E4)
    assert c[3] == 3                                          # partner of two title groups: own candidate (E3)


def test_title_group_at_oth_drops_whole_and_frees_partners():
    u = candidates(frame([(1, "bachelor", 1, "elektrotechnik", True), (2, "bachelor", 2, "elektrotechnik", False),
                          (3, "bachelor", 2, "energietechnik plus", False)]))
    assert u.set_index("type")["dropped whole"].to_dict() == {1: True, 2: True, 3: False}
    assert u.set_index("type").at[3, "candidate"] == 3        # E5
    assert u.set_index("type").at[3, "how"] == "partner of a title group dropped at OTH"


def test_levels_apart_and_every_unit_once():
    u = candidates(frame([(1, "bachelor", 1, "informatik", False), (2, "master", 2, "informatik", False), (3, "bachelor", 3, "x", False)]))
    assert (u["candidate"] >= 0).all() and len(u) == 3
    assert u.set_index("type").at[2, "candidate"] == 2        # a title shared across levels is no match
