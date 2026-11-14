"""Funnel step 2: programme types (configs/funnel.yaml: text, similarity, discovery; docs/criteria_funnel_step2.md)."""

import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from study_program_intelligence.analysis import funnel_types as T

REPO = Path(__file__).resolve().parents[1]
INTERIM = REPO / "data" / "interim"
needs = lambda *files: pytest.mark.skipif(not all((REPO / f).exists() for f in files), reason="no generated data")
RUN = ("data/interim/funnel2_step2.json", "data/interim/funnel2_types.csv", "data/interim/funnel2_offer_types.csv", "data/interim/funnel2_grid.csv")


def test_title_loses_degree_words_only():
    assert T.clean_title("Betriebswirtschaft und Sozialmanagement Bachelor of Arts (B.A.)") == "Betriebswirtschaft und Sozialmanagement"
    assert T.clean_title("Mathematik Master of Education M.Ed. Sekundarstufe I und Europalehramt") == "Mathematik Sekundarstufe I und Europalehramt"
    assert T.clean_title("Altorientalistik Kombibachelor Hauptfach") == "Altorientalistik Hauptfach"
    assert T.clean_title("Sport Lehramt an Gymnasien (Master)") == "Sport Lehramt an Gymnasien"      # other bracket text stays
    assert T.clean_title("Disaster Management Master of Science") == "Disaster Management"         # "Disaster" is no degree word
    assert T.clean_title("Master of Finance Master of Science") == "Finance"                       # the name itself is a degree
    assert T.clean_title("Wirtschaftsrecht LL.M.") == "Wirtschaftsrecht"


def test_focus_items_follow_the_text_rule():
    assert T.focus_items("Inhalte bitte bei der Hochschule erfragen Anmerkung der Hochschule: : Doppel-Hauptfach") == []
    assert T.focus_items("Schwerpunkte: : Recht, Technik Anmerkung der Hochschule: : Bewerbung nur zum Winter, Robotik") == ["Recht", "Technik"]
    assert T.focus_items("Studieninhalte sind bitte bei der Hochschule zu erfragen. Schwerpunkte: : Medizinische Chemie") == ["Medizinische Chemie"]
    assert T.focus_items("Schwerpunkte: : Methods (Biology, Physics), KI, Zellbiologie Anmerkung der Hoc…:") == ["Methods (Biology, Physics)", "KI", "Zellbiologie"]
    assert T.focus_items("Schwerpunkte: : Recht, INHALTE BITTE BEI DER HOCHSCHULE ERFRAGEN") == ["Recht"]
    assert T.focus_items("Das Studium vermittelt Grundlagen der Informatik.") == []            # free text is not a focus item
    assert T.focus_items("Schwerpunkte: : Recht, Wahlpflichtbereich", drop=("wahlpflichtbereich",)) == ["Recht"]
    assert T.focus_items("Schwerpunkte: : Anmerkungen zur Literatur, Recht") == ["Anmerkungen zur Literatur", "Recht"]


def test_offer_text_has_no_dropped_phrase_and_no_level_marker():
    title, items, labels = T.offer_parts("Informatik Bachelor of Science", "Schwerpunkte: : KI Anmerkung der Hochschule: : x",
                                         "Informatik (grundständig); Künstliche Intelligenz (grundständig)")
    text = T.offer_text(title, items, labels)
    assert text == "Informatik. KI. Informatik, Künstliche Intelligenz"
    assert T.unclean([text], list(T.dropped_phrases())) == []
    assert T.unclean(["Recht (Grundständig)", "Inhalte bitte bei der HOCHSCHULE erfragen", "Recht"], T.dropped_phrases()) == [0, 1]


def test_check_finds_a_boilerplate_item_but_not_a_longer_item():
    d = pd.DataFrame({"text": ["A. Wahlpflichtbereich", "B. Wahlpflichtbereich Informatik", ""],
                      "focus_text": ["Wahlpflichtbereich", "Wahlpflichtbereich Informatik", ""]})
    c = T.check_clean(d, ("wahlpflichtbereich",))
    assert c["texts_with_a_boilerplate_item"] == 1 and c["longer_items_containing_a_boilerplate_string"] == 2 and c["empty_texts"] == 1


def test_best_jaccard_and_selection_rule():
    a = np.array([0, 0, 0, 1, 1, -1])
    b = np.array([5, 5, 7, 7, 7, 7])
    j = T.best_jaccard(a, b)
    assert j[0] == pytest.approx(2 / 3) and j[1] == pytest.approx(2 / 4)
    grid = pd.DataFrame([
        {"min_cluster_size": 10, "method": "eom", "clusters": 9, "stable clusters": 5, "share in stable": 0.60, "noise": 0.55, "largest cluster share": 0.05},
        {"min_cluster_size": 15, "method": "eom", "clusters": 9, "stable clusters": 5, "share in stable": 0.58, "noise": 0.30, "largest cluster share": 0.20},
        {"min_cluster_size": 20, "method": "eom", "clusters": 9, "stable clusters": 4, "share in stable": 0.40, "noise": 0.30, "largest cluster share": 0.05},
        {"min_cluster_size": 30, "method": "leaf", "clusters": 9, "stable clusters": 6, "share in stable": 0.40, "noise": 0.30, "largest cluster share": 0.05}])
    pick = T.select(grid)                                   # too much noise, too large a cluster, then the tie goes to more stable clusters
    assert (pick["min_cluster_size"], pick["method"]) == (30, "leaf")


def test_radius_of_a_rare_type_is_never_below_the_stable_median():
    own = {0: np.linspace(0, 0.10, 11), 1: np.linspace(0, 0.20, 11), 2: np.array([0.01, 0.02]), 3: np.array([0.05, 0.40])}
    r = T.radii(own, stable={0, 1})
    assert r[0] == pytest.approx(0.09) and r[1] == pytest.approx(0.18)
    assert r[2] == pytest.approx(0.135) and r[3] == pytest.approx(0.40)       # the median of 0.09 and 0.18; its own largest distance


def test_rare_path_needs_two_institutions_and_respects_the_size_limit():
    e = np.array([[1, 0, 0], [1, 0.01, 0], [0, 1, 0], [0, 1, 0.01], [0, 0, 1], [0, 0.01, 1], [0.01, 0, 1]], float)
    e /= np.linalg.norm(e, axis=1, keepdims=True)
    inst = np.array(["a", "b", "c", "c", "d", "e", "f"])
    out = T.rare_path(e, inst, np.ones(7, bool), cutoff=0.05, max_size=2, min_inst=2)
    assert out[0] == out[1] >= 0 and (out[2:] == -1).all()   # one institution only; three offers are more than max_size


def test_all_18_old_lists_are_tested_and_the_stoplist_holds_no_subject_word():
    assert len(T.old_lists()) == 18
    s = yaml.safe_load((REPO / "configs" / "funnel_title_stoplist.yaml").read_text(encoding="utf-8"))
    words = s["degree_words"] + s["catalogue_words"]
    assert len(words) == len(set(words)) and all(w == T.normalise(w) for w in words)
    assert not {"informatik", "management", "engineering", "englisch", "deutsch", "mathematik"} & set(words)


def test_rule_files_are_tracked():
    tracked = subprocess.run(["git", "ls-files", "configs"], cwd=REPO, capture_output=True, text=True).stdout.split()
    assert "configs/funnel_title_stoplist.yaml" in tracked
    if (INTERIM / "funnel2_embeddings.npy").exists():
        assert "configs/funnel_boilerplate.yaml" in tracked


@needs("data/interim/funnel2_offers.csv", "configs/funnel_boilerplate.yaml")
def test_embedded_texts_are_clean():
    d = pd.read_csv(INTERIM / "funnel2_offers.csv", low_memory=False)
    c = T.check_clean(d, tuple(T.boilerplate()))
    assert c["texts_with_a_dropped_phrase"] == 0 and c["texts_with_a_boilerplate_item"] == 0 and c["empty_texts"] == 0
    assert len(d) == len(np.load(INTERIM / "funnel2_embeddings.npy"))
    assert not d.duplicated(["institution", "title", "degree"]).any()


@needs(*RUN)
def test_selected_setting_is_the_one_the_rule_gives():
    r = json.loads((INTERIM / "funnel2_step2.json").read_text(encoding="utf-8"))
    grid = pd.read_csv(INTERIM / "funnel2_grid.csv")
    rules = yaml.safe_load((REPO / "configs" / "funnel.yaml").read_text(encoding="utf-8"))["discovery"]
    assert len(grid) == len(rules["hdbscan_grid"]["min_cluster_size"]) * len(rules["hdbscan_grid"]["method"]) == 10
    pick = T.select(grid)
    assert (int(pick["min_cluster_size"]), pick["method"]) == (r["selected"]["min_cluster_size"], r["selected"]["method"])
    assert r["stamp"]["clean"] is True and r["old_lists"] == 18


@needs(*RUN)
def test_types_are_built_as_the_rules_say():
    r = json.loads((INTERIM / "funnel2_step2.json").read_text(encoding="utf-8"))
    t = pd.read_csv(INTERIM / "funnel2_types.csv")
    d = pd.read_csv(INTERIM / "funnel2_offer_types.csv", low_memory=False)
    stable, rare = t[t["kind"] == "stable"], t[t["kind"] == "rare"]
    assert list(t["type"]) == list(range(len(t))) and len(stable) == r["stable_types"] and len(rare) == r["rare_types"]
    assert (stable["stability"] >= 0.75).all()
    assert (rare["member institutions"] >= 2).all() and (rare["members"] < r["selected"]["min_cluster_size"]).all()
    assert (rare["radius_90"] >= stable["radius_90"].median() - 1e-4).all() and (rare["radius_90"] >= rare["largest distance"] - 1e-4).all()
    assert d.loc[d["type"] >= 0, "full_time"].all()                                   # only full-time offers are fitted members
    assert (d.loc[d["type"] >= 0, "assigned_type"] == d.loc[d["type"] >= 0, "type"]).all()
    later = d[d["assigned_only"]]
    radius = t.set_index("type")["radius_90"]
    assert (later["assigned_type"] == later["nearest_type"]).all()
    assert (later["dist_to_assigned"] <= later["assigned_type"].map(radius) + 1e-4).all()
    out = d[d["assigned_type"] < 0]
    assert (out["dist_to_nearest"] > out["nearest_type"].map(radius) - 1e-4).all()
    assert t["members"].sum() == (d["type"] >= 0).sum() and t["assigned offers"].sum() == (d["assigned_type"] >= 0).sum()
    cent = np.load(INTERIM / "funnel2_centroids.npy")
    assert cent.shape[0] == len(t) and np.allclose(np.linalg.norm(cent, axis=1), 1, atol=1e-4)
