"""Funnel step 2: programme types (configs/funnel.yaml: text, similarity, discovery; docs/criteria_funnel_step2.md).

The tests on generated files recompute the result from the vectors and the offer table; they are skipped where the
git-ignored data is missing (for example on the test server)."""

import hashlib
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
RUN = ("data/interim/funnel2_step2.json", "data/interim/funnel2_types.csv", "data/interim/funnel2_offer_types.csv", "data/interim/funnel2_grid.csv",
       "data/interim/funnel2_embeddings.npy", "data/interim/funnel2_centroids.npy")
RULES = yaml.safe_load((REPO / "configs" / "funnel.yaml").read_text(encoding="utf-8"))


def test_the_four_dropped_phrases_are_read_from_the_rules():
    assert T.dropped_phrases() == ("anmerkung der hochschule", "inhalte bitte bei der hochschule erfragen", "(grundstaendig)", "(weiterfuehrend)")


@pytest.mark.parametrize("raw, clean", [
    ("Betriebswirtschaft und Sozialmanagement Bachelor of Arts (B.A.)", "Betriebswirtschaft und Sozialmanagement"),
    ("Mathematik Master of Education M.Ed. Sekundarstufe I und Europalehramt", "Mathematik Sekundarstufe I und Europalehramt"),
    ("Altorientalistik Kombibachelor Hauptfach", "Altorientalistik Hauptfach"),
    ("Philosophie Zwei-Fach-Bachelor", "Philosophie"),
    ("Sport Lehramt an Gymnasien (Master)", "Sport Lehramt an Gymnasien"),                       # other bracket text stays
    ("Disaster Management Master of Science", "Disaster Management"),                            # "Disaster" is no degree word
    ("Wirtschaftsrecht LL.M.", "Wirtschaftsrecht"),
    ("BA Film / Regie Bachelor", "Film / Regie"),
    ("Wirtschaftsingenieurwesen (MBA & Eng.) Master", "Wirtschaftsingenieurwesen"),
    ("Master of Finance Master of Science", "Finance"),                                          # the name itself is a degree
    ("Bachelor of Laws Bachelor", "Laws"),
    ("International Master of Landscape Architecture Master of Engineering", "International Landscape Architecture"),   # subject words stay
    ("Master of Media Research Master", "Media Research"),
    ("Master of Mergers & Acquisitions Master of Laws", "Mergers & Acquisitions"),
    ("Peace and Security Studies Master of Peace and Security Studies", "Peace and Security Studies"),                 # the name is not doubled
    ("Master in Management Master of Science in Management", "Management"),
    ("Arp-Schnitger-Master Orgel Master of Music", "Arp-Schnitger Orgel"),
    ("Informatik Bachelor of Science (grundständig)", "Informatik"),
    ("Informatik - Technische Informatik Bachelor", "Informatik - Technische Informatik"),                              # a word repeated inside the name stays
    ("Psychologie mit Schwerpunkt Forensische Psychologie Master", "Psychologie mit Schwerpunkt Forensische Psychologie"),
    ("Compliance Master of Laws Compliance", "Compliance"),
    ("Bachelor of Music: Hauptfach Klavier", "Hauptfach Klavier"),
])
def test_title_loses_degree_words_only(raw, clean):
    assert T.clean_title(raw) == clean


def test_focus_items_follow_the_text_rule():
    f = T.focus_items
    assert f("Inhalte bitte bei der Hochschule erfragen Anmerkung der Hochschule: : Doppel-Hauptfach") == []
    assert f("Schwerpunkte: : Recht, Technik Anmerkung der Hochschule: : Bewerbung nur zum Winter, Robotik") == ["Recht", "Technik"]
    assert f("Studieninhalte sind bitte bei der Hochschule zu erfragen. Schwerpunkte: : Medizinische Chemie") == ["Medizinische Chemie"]
    assert f("Schwerpunkte: : Methods (Biology, Physics), KI, Zellbiologie Anmerkung der Hoc…:") == ["Methods (Biology, Physics)", "KI", "Zellbiologie"]
    assert f("Schwerpunkte: : KI, Robotik und Systeme Anmerku…:") == ["KI", "Robotik und Systeme"]          # the heading cut inside the word
    assert f("Schwerpunkte: : KI, Data Science A…:") == ["KI", "Data Science"]
    assert f("Schwerpunkte: : KI, Systeme …:") == ["KI", "Systeme"]
    assert f("Schwerpunkte: : Recht, INHALTE BITTE BEI DER  HOCHSCHULE ERFRAGEN") == ["Recht"]
    assert f("Das Studium vermittelt Grundlagen der Informatik.") == []                                     # free text is not a focus item
    assert f('Inhalte bitte bei der Hochschule erfragen Anmerkung der Hochschule: : Schwerpunkte: "Islam und Medien"') == []   # no heading: it is in the note
    assert f("Schwerpunkte: : Recht, Wahlpflichtbereich", drop=("wahlpflichtbereich",)) == ["Recht"]
    assert f("Schwerpunkte: : Anmerkungen zur Literatur, Recht") == ["Anmerkungen zur Literatur", "Recht"]
    assert f("Schwerpunkte: : Recht; Technik, C, R, .NET, Wirtschaftsinfor…") == ["Recht", "Technik", "C", "R", ".NET", "Wirtschaftsinfor"]


def test_offer_text_has_no_dropped_phrase_and_no_level_marker():
    title, items, labels = T.offer_parts("Informatik Bachelor of Science", "Schwerpunkte: : KI Anmerkung der Hochschule: : x",
                                         "Informatik (grundständig); Lehramt an Gymnasien (grundständig außer Staatsexamen)")
    text = T.offer_text(title, items, labels)
    assert text == "Informatik. KI. Informatik, Lehramt an Gymnasien"
    assert T.unclean([text], T.dropped_phrases()) == []
    assert T.unclean(["Recht (Grundständig)", "Inhalte bitte bei der HOCHSCHULE erfragen", "Recht", "Jura (grundständig außer Staatsexamen)"], T.dropped_phrases()) == [0, 1, 3]
    assert T.clean_label("Informatik (weiterführend)") == "Informatik" and T.clean_label("Rechtswissenschaft (Staatsexamen)") == "Rechtswissenschaft (Staatsexamen)"


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
        {"min_cluster_size": 30, "method": "leaf", "clusters": 9, "stable clusters": 6, "share in stable": 0.40, "noise": 0.30, "largest cluster share": 0.05},
        {"min_cluster_size": 50, "method": "eom", "clusters": 9, "stable clusters": 9, "share in stable": 0.39996, "noise": 0.30, "largest cluster share": 0.05}])
    pick = T.select_former(grid)          # too much noise; too large a cluster; a tie goes to more stable clusters; 0.39996 is not a tie
    assert (pick["min_cluster_size"], pick["method"]) == (30, "leaf")
    pick = T.select(grid)                 # the smallest size inside the limits: 10 has too much noise, 15 too large a cluster
    assert (pick["min_cluster_size"], pick["method"]) == (20, "eom")
    both = pd.concat([grid, grid.iloc[[2]].assign(method="leaf", **{"share in stable": 0.45})], ignore_index=True)
    pick = T.select(both)                 # between the two methods of the smallest size, the higher share in stable clusters
    assert (pick["min_cluster_size"], pick["method"]) == (20, "leaf")


def test_rare_cutoff_is_the_median_of_all_within_type_pairs():
    e = np.array([[1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], float)
    lab = np.array([0, 0, 0, 1, 1, -1])           # type 0: three identical offers (3 pairs at 0); type 1: one pair at distance 1
    pooled, of_medians = T.rare_cutoff(e, lab)
    assert pooled == pytest.approx(0.0) and of_medians == pytest.approx(0.5)      # pairs 0, 0, 0, 1; type medians 0 and 1


def test_radius_of_a_rare_type_is_never_below_the_stable_median():
    own = {0: np.linspace(0, 0.10, 11), 1: np.linspace(0, 0.20, 11), 2: np.array([0.01, 0.02]), 3: np.array([0.05, 0.40])}
    r = T.radii(own, stable={0, 1})
    assert r[0] == pytest.approx(0.09) and r[1] == pytest.approx(0.18)
    assert r[2] == pytest.approx(0.135) and r[3] == pytest.approx(0.40)       # the median of 0.09 and 0.18; its own largest distance
    r = T.radii(own, stable={0, 1}, mid=frozenset({3}))
    assert r[3] == pytest.approx(0.05 + 0.9 * 0.35) and r[2] == pytest.approx(0.135)   # a mid-sized type takes its own percentile


def test_offers_are_assigned_afterwards_only_inside_the_radius_and_nothing_is_refitted():
    unit = lambda *v: np.array(v, float) / np.linalg.norm(v)
    e = np.vstack([unit(1, 0, 0), unit(1, 0.2, 0), unit(1, -0.2, 0),          # type 0 (stable)
                   unit(0, 1, 0), unit(0, 1, 0.1),                            # type 1 (rare)
                   unit(1, 0.05, 0), unit(1, 1, 0), unit(0, 0, 1)])           # near type 0; between the two; far from both
    lab = np.array([0, 0, 0, 1, 1, -1, -1, -1])
    g = T.centroids_and_assignment(e, lab, n_stable=1)
    assert list(g["assigned"]) == [0, 0, 0, 1, 1, 0, -1, -1]
    assert np.allclose(g["centroids"][0], unit(1, 0, 0)) and np.allclose(np.linalg.norm(g["centroids"], axis=1), 1)   # from the fitted members only
    assert g["radii"][90][1] == pytest.approx(max(g["own"][1].max(), g["radii"][90][0]))


def test_rare_path_needs_two_institutions_and_respects_the_size_limit():
    e = np.array([[1, 0, 0], [1, 0.01, 0], [0, 1, 0], [0, 1, 0.01], [0, 0, 1], [0, 0.01, 1], [0.01, 0, 1]], float)
    e /= np.linalg.norm(e, axis=1, keepdims=True)
    inst = np.array(["a", "b", "c", "c", "d", "e", "f"])
    rare, mid, info = T.rare_path(e, inst, np.ones(7, bool), cutoff=0.05, max_size=2, min_inst=2)
    assert rare[0] == rare[1] >= 0 and (rare[2:] == -1).all()                  # two offers of two institutions: a rare type
    assert mid[4] == mid[5] == mid[6] >= 0 and (mid[:4] == -1).all()           # three offers are more than max_size: kept as a mid-sized type
    assert info["groups_at_one_institution"] == 1 and info["offers_in_groups_at_one_institution"] == 2 and info["left_over_offers"] == 7


def test_old_list_recovery_counts_offers_outside_any_type_against_the_list():
    title = pd.Series(["Robotik", "Robotik und KI", "Robotics", "Chemie", "Robotik dual", "Physik"])
    lab = np.array([0, 0, 0, 0, -1, 1])
    r = T.recovery(title, lab, np.ones(6, bool)).set_index("old list")
    assert r.loc["robotics", "offers"] == 4 and r.loc["robotics", "type"] == 0
    assert r.loc["robotics", "best Jaccard"] == pytest.approx(3 / 5) and r.loc["robotics", "recovered"] == "yes"     # 3 shared; 4 in the list, 4 in the type
    assert r.loc["quantum", "recovered"].startswith("not testable") and len(r) == 18


def test_stoplist_holds_no_subject_word_and_rule_files_are_tracked():
    s = yaml.safe_load((REPO / "configs" / "funnel_title_stoplist.yaml").read_text(encoding="utf-8"))
    words = s["degree_words"] + s["catalogue_words"]
    assert len(words) == len(set(words)) and all(w == T.normalise(w) for w in words)
    assert not {"informatik", "management", "engineering", "englisch", "deutsch", "mathematik"} & set(words)
    tracked = subprocess.run(["git", "ls-files", "configs"], cwd=REPO, capture_output=True, text=True).stdout.split()
    assert "configs/funnel_title_stoplist.yaml" in tracked
    if (INTERIM / "funnel2_embeddings.npy").exists():
        assert "configs/funnel_boilerplate.yaml" in tracked


@needs("data/interim/funnel2_offers.csv", "data/interim/funnel2_embed.json", "configs/funnel_boilerplate.yaml")
def test_embedded_texts_are_clean():
    d = pd.read_csv(INTERIM / "funnel2_offers.csv", low_memory=False)
    drop = tuple(T.normalise(p) for p in yaml.safe_load((REPO / "configs" / "funnel_boilerplate.yaml").read_text(encoding="utf-8"))["dropped"])
    c = T.check_clean(d, drop)
    assert c["texts_with_a_dropped_phrase"] == 0 and c["texts_with_a_boilerplate_item"] == 0 and c["empty_texts"] == 0
    low = d["text"].map(T.normalise)
    assert not low.str.contains("grundstaendig ausser|anmerkung der hochschule|bitte bei der hochschule erfragen", regex=True).any()
    assert len(d) == len(np.load(INTERIM / "funnel2_embeddings.npy")) and not d.duplicated(["institution", "title", "degree"]).any()
    meta = json.loads((INTERIM / "funnel2_embed.json").read_text(encoding="utf-8"))
    assert meta["stamp"]["clean"] is True and meta["check"]["texts_with_a_dropped_phrase"] == 0


@needs(*RUN)
def test_grid_is_complete_and_the_selected_setting_is_the_one_the_rule_gives():
    r = json.loads((INTERIM / "funnel2_step2.json").read_text(encoding="utf-8"))
    grid = pd.read_csv(INTERIM / "funnel2_grid.csv")
    cfg = RULES["discovery"]
    want = {(m, k) for m in cfg["hdbscan_grid"]["min_cluster_size"] for k in cfg["hdbscan_grid"]["method"]}
    assert set(zip(grid["min_cluster_size"], grid["method"])) == want and len(grid) == len(want) == 10
    assert r["umap_seeds"] == cfg["umap"]["seeds"] and r["refits_per_setting"] == cfg["bootstrap"]["refits"] == 10
    ok = [row for row in grid.to_dict("records") if row["noise"] <= 0.50 and row["largest cluster share"] <= 0.10 and row["stable clusters"] > 0]
    best = lambda rows: max(rows, key=lambda row: (row["share in stable"], row["stable clusters"]))    # the rules, written out again without the code's functions
    finest = best([row for row in ok if row["min_cluster_size"] == min(x["min_cluster_size"] for x in ok)])
    assert (finest["min_cluster_size"], finest["method"]) == (r["selected"]["min_cluster_size"], r["selected"]["method"])
    assert [best(ok)["min_cluster_size"], best(ok)["method"]] == r["former_rule_setting"]
    assert r["stable_types"] == finest["stable clusters"] and r["full_time_in_stable"] == round(finest["share in stable"] * r["full_time"])
    assert r["diagnostic_setting"] is None
    assert r["old_lists"] == 18 and r["old_lists_tested_fitted"] <= 18


@needs(*RUN)
def test_outputs_belong_together_and_carry_the_commit():
    r = json.loads((INTERIM / "funnel2_step2.json").read_text(encoding="utf-8"))
    meta = json.loads((INTERIM / "funnel2_embed.json").read_text(encoding="utf-8"))
    assert r["stamp"]["clean"] is True and r["embed_commit"] == meta["stamp"]["commit"]
    for name, h in r["files"].items():
        assert hashlib.sha256((INTERIM / name).read_bytes()).hexdigest()[:16] == h, name
    assert f"Code commit {r['stamp']['commit']}" in (REPO / "reports" / "funnel2" / "step2_types.md").read_text(encoding="utf-8")
    assert (REPO / "reports" / "funnel2" / "step2_sample.md").exists()


@needs(*RUN)
def test_types_are_built_as_the_rules_say():
    """Centroids, radii and the assignment are computed again here from the vectors and the type of every offer."""
    r = json.loads((INTERIM / "funnel2_step2.json").read_text(encoding="utf-8"))
    t = pd.read_csv(INTERIM / "funnel2_types.csv")
    d = pd.read_csv(INTERIM / "funnel2_offer_types.csv", low_memory=False)
    emb = np.load(INTERIM / "funnel2_embeddings.npy").astype(np.float64)
    lab = d["type"].to_numpy()
    stable, mid, rare = t[t["kind"] == "stable"], t[t["kind"] == "mid-sized"], t[t["kind"] == "rare"]
    n = len(t)
    assert list(t["type"]) == list(range(n)) and (len(stable), len(mid), len(rare)) == (r["stable_types"], r["mid_sized_types"], r["rare_types"])
    assert len(stable) + len(mid) + len(rare) == n and list(t["kind"]) == ["stable"] * len(stable) + ["mid-sized"] * len(mid) + ["rare"] * len(rare)
    assert (stable["stability"] >= RULES["discovery"]["stable_jaccard"]).all()
    assert (mid["evidence flag"] == "mid-sized, not stability-tested").all() and (rare["evidence flag"] == "rare, not stability-tested").all()
    assert d.loc[lab >= 0, "full_time"].all()                                           # only full-time offers are fitted members
    members = d[lab >= 0].groupby("type").agg(n=("type", "size"), inst=("institution", "nunique"))
    assert (members["n"].to_numpy() == t["members"].to_numpy()).all()
    assert (members.loc[list(rare["type"]) + list(mid["type"]), "inst"] >= RULES["discovery"]["rare_path"]["min_institutions"]).all()
    assert (members.loc[rare["type"], "n"] < r["selected"]["min_cluster_size"]).all() and (members.loc[mid["type"], "n"] >= r["selected"]["min_cluster_size"]).all()
    cent = np.vstack([emb[lab == c].mean(axis=0) for c in range(n)])
    cent /= np.linalg.norm(cent, axis=1, keepdims=True)
    assert np.allclose(cent, np.load(INTERIM / "funnel2_centroids.npy"), atol=1e-5)
    dist = 1 - emb @ cent.T
    r90 = np.array([np.percentile(dist[lab == c, c], 90) for c in range(len(stable))])
    assert np.allclose(r90, stable["radius_90"], atol=1e-6)
    mid_r = np.array([np.percentile(dist[lab == c, c], 90) for c in mid["type"]])
    rare_r = np.array([max(dist[lab == c, c].max(), np.median(r90)) for c in rare["type"]])
    assert np.allclose(mid_r, mid["radius_90"], atol=1e-6) and np.allclose(rare_r, rare["radius_90"], atol=1e-6)
    radius = np.concatenate([r90, mid_r, rare_r])
    near = dist.argmin(axis=1)
    near_d = dist[np.arange(len(d)), near]
    want = np.where(lab >= 0, lab, np.where(near_d <= radius[near], near, -1))
    assert (want == d["assigned_type"].to_numpy()).all()
    assert int((want < 0).sum()) == r["offers_without_any_type"] and int(((lab < 0) & (want >= 0)).sum()) == r["assigned_afterwards"]
    counts = pd.Series(want[want >= 0]).value_counts().reindex(range(n), fill_value=0)
    assert (counts.to_numpy() == t["assigned offers"].to_numpy()).all()
    units = sum(int(d[(want == c) & (d["level"] == lv)]["institution"].nunique() >= 2) for c in range(n) for lv in ("bachelor", "master"))
    assert units == r["units"] == int(t["units"].sum())


@needs(*RUN)
def test_no_left_over_group_of_two_institutions_is_dropped():
    """Criterion R4: the left-over offers are grouped again here; every group with offers of 2 or more institutions is a type."""
    from sklearn.cluster import AgglomerativeClustering
    r = json.loads((INTERIM / "funnel2_step2.json").read_text(encoding="utf-8"))
    d = pd.read_csv(INTERIM / "funnel2_offer_types.csv", low_memory=False)
    emb = np.load(INTERIM / "funnel2_embeddings.npy").astype(np.float64)
    stable = np.where(d["kind"] == "stable", d["type"], -1)
    pairs = []
    for c in np.unique(stable[stable >= 0]):
        m = np.where(stable == c)[0]
        pairs.append((1 - emb[m] @ emb[m].T)[np.triu_indices(len(m), 1)])
    cut = float(np.median(np.concatenate(pairs)))
    assert round(cut, 4) == r["rare_cutoff"]
    idx = np.where(d["full_time"] & (d["kind"] != "stable"))[0]
    assert len(idx) == r["left_over"]["left_over_offers"]
    grp = AgglomerativeClustering(n_clusters=None, metric="cosine", linkage="average", distance_threshold=cut).fit_predict(emb[idx])
    typ, inst, kind = d["type"].to_numpy()[idx], d["institution"].to_numpy()[idx], d["kind"].to_numpy()[idx]
    size = r["selected"]["min_cluster_size"]
    kept = dropped = 0
    for g in np.unique(grp):
        m = grp == g
        if m.sum() >= 2 and len(set(inst[m])) >= 2:
            assert len(set(typ[m])) == 1 and typ[m][0] >= 0, "a group of two institutions has no type of its own"
            assert set(kind[m]) == ({"rare"} if m.sum() < size else {"mid-sized"})
            kept += 1
        else:
            assert (typ[m] == -1).all()
            dropped += int(m.sum() >= 2)
    assert kept == r["rare_types"] + r["mid_sized_types"] and dropped == r["left_over"]["groups_at_one_institution"]


@needs("data/interim/funnel2_offers.csv", "data/interim/funnel2_embed.json", "data/processed/programmes_full.csv", "configs/funnel_boilerplate.yaml")
def test_stored_texts_are_those_the_current_code_builds():
    """Criterion R5: all offer texts are built again from the catalogue."""
    stored = pd.read_csv(INTERIM / "funnel2_offers.csv", low_memory=False)
    drop = tuple(T.normalise(p) for p in yaml.safe_load((REPO / "configs" / "funnel_boilerplate.yaml").read_text(encoding="utf-8"))["dropped"])
    built = T.build_offers(drop)
    assert len(built) == len(stored) and (built["programme_id"].astype(str).to_numpy() == stored["programme_id"].astype(str).to_numpy()).all()
    assert (built["text"].to_numpy() == stored["text"].to_numpy()).all()
    assert int((~built["has_focus"]).sum()) == json.loads((INTERIM / "funnel2_embed.json").read_text(encoding="utf-8"))["without_focus_items"]

