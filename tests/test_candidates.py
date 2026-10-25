"""Equal-evidence step: parsing, nationality split, competitor counts, score rules, ranking reproducibility (E5)."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
INTERIM = REPO / "data" / "interim"
needs = lambda *files: pytest.mark.skipif(not all((REPO / f).exists() for f in files), reason="no generated data")
HAND = ("labour_relevance", "institutional_fit", "feasibility", "differentiation")


def load(p: str):
    return yaml.safe_load((REPO / p).read_text(encoding="utf-8"))


# ---------------- parsing ----------------

@needs("data/raw/references/ref_geodata_hm.pdf", "data/raw/anchors/hske_ba_robotik.pdf")
def test_reference_handbooks_parse_completely():
    from study_program_intelligence.transform.modules import REFERENCES, parse
    expected = {"hske_ba_rob": 50, "thd_ba_em": 34, "fhdo_ba_eedm": 40, "hsc_ba_vc": 65, "hm_ba_gds": 31}
    for hb in REFERENCES:
        hb.strict_ects = True
        rows, check = parse(hb)
        assert check["toc"] == expected[hb.programme_id] == check["found"], hb.programme_id
        assert not check["missing"], hb.programme_id
        no_ects = [r["title"] for r in rows if not r["ects"]]
        assert len(no_ects) <= 4, (hb.programme_id, no_ects)   # Kempten 4 (week 2); the others none


# ---------------- nationality split ----------------

@needs("data/interim/candidate_demand.csv")
def test_nationality_split_adds_up():
    d = pd.read_csv(INTERIM / "candidate_demand.csv")
    for end in ("start", "end"):
        assert (d[f"German {end}"] + d[f"foreign {end}"] == d[f"all {end}"]).all()


@needs("data/raw/destatis/21311-0015_BY.csv")
def test_robotics_series_reproduces_the_baseline_split():
    from study_program_intelligence.analysis import candidates as C
    from study_program_intelligence.analysis.demand_split import load as destatis, series_table
    long = destatis()
    cfg = C.config()
    rows = C.demand("robotics_b", cfg["candidates"]["robotics_b"], long, cfg["trend_rule"])
    base = series_table(long).set_index(["series", "region"])
    for r in rows:
        b = base.loc[("robotics feeders", r["region"])]
        assert (r["German start"], r["foreign end"], r["all %/yr"]) == (b["German start"], b["foreign end"], b["all %/yr"])


# ---------------- trend rule ----------------

def test_trend_rule_reproduces_the_six_baseline_scores():
    from study_program_intelligence.analysis.candidates import trend_score
    rule = load("configs/candidates.yaml")["trend_rule"]
    baseline = {5.9: 4, -0.6: 2, 10.2: 4, 1.9: 3, -3.3: 1, 7.2: 4}   # all-nationality and German-only Bavaria series
    for growth, score in baseline.items():
        assert trend_score(growth, rule)["central"] == score, growth
    sheet = load("configs/scores.yaml")
    assert sheet["options"]["cyber_bsc"]["student_demand"]["trend"]["central"] == trend_score(5.9, rule)["central"]
    assert sheet["sensitivity"]["trend_german"]["robotics_bsc"]["central"] == trend_score(-3.3, rule)["central"]


@needs("data/interim/candidate_demand.csv")
def test_candidate_trend_scores_follow_the_rule():
    from study_program_intelligence.analysis.candidates import trend_score
    rule = load("configs/candidates.yaml")["trend_rule"]
    sheet = load("configs/scores_candidates.yaml")
    d = pd.read_csv(INTERIM / "candidate_demand.csv")
    for _, r in d[d["region"] == "BY"].iterrows():
        t = sheet["options"][r["candidate"]]["student_demand"]["trend"]
        assert {k: t[k] for k in ("low", "central", "high")} == trend_score(r["all %/yr"], rule), r["candidate"]
        assert sheet["sensitivity"]["trend_german"][r["candidate"]] == trend_score(r["German %/yr"], rule), r["candidate"]


# ---------------- competition ----------------

@needs("data/processed/programmes_full.csv", "data/interim/candidate_competition.csv")
def test_competitor_counts_reproduce_the_catalogue():
    """Independent recount from the raw catalogue (plain loops, no shared helper)."""
    import re
    p = pd.read_csv(REPO / "data" / "processed" / "programmes_full.csv")
    comp = pd.read_csv(INTERIM / "candidate_competition.csv").set_index("candidate")
    for key, c in load("configs/candidates.yaml")["candidates"].items():
        theme, excl = re.compile(c["theme"], re.I), re.compile(c["exclude"], re.I) if c.get("exclude") else None
        inst_de, inst_by, inst_150 = set(), set(), set()
        for r in p.itertuples():
            if r.is_oth or r.study_form != "Vollzeitstudium" or not r.degree.startswith(c["level"]):
                continue
            if not theme.search(r.title) or (excl and excl.search(r.title)):
                continue
            inst_de.add(r.institution)
            if r.state == "Bayern":
                inst_by.add(r.institution)
            if r.km_oth <= 150:
                inst_150.add(r.institution)
        got = comp.loc[key]
        assert (len(inst_de), len(inst_by), len(inst_150)) == (got["dedicated institutions DE"], got["dedicated institutions BY"],
                                                               got["dedicated institutions <=150 km"]), key


@needs("data/interim/candidate_competition.csv")
def test_differentiation_rule():
    """0 -> 5, 1-2 -> 4, 3-5 -> 3, more -> 1; minus 1 for a dedicated one within 80 km, OTH's own dedicated programme,
    or the same profile nearby (hand: ot_master, Deggendorf OT)."""
    comp = pd.read_csv(INTERIM / "candidate_competition.csv").set_index("candidate")
    sheet = load("configs/scores_candidates.yaml")["options"]
    same_profile_nearby = {"ot_master"}
    oth_dedicated = {"geodata"}
    for key, r in comp.iterrows():
        n = r["dedicated institutions <=150 km"]
        s = 5 if n == 0 else 4 if n <= 2 else 3 if n <= 5 else 1
        s -= int(r["dedicated institutions <=80 km"] > 0 or key in oth_dedicated or key in same_profile_nearby)
        assert sheet[key]["differentiation"]["central"] == s, key


# ---------------- feasibility and fit ----------------

def _fit(cov: float, new: float) -> int:
    c = 5 if cov >= 70 else 4 if cov >= 50 else 3 if cov >= 30 else 2 if cov >= 20 else 1
    st = 5 if new <= 10 else 4 if new <= 25 else 3 if new <= 40 else 2
    return min(c, st)


@needs("data/interim/feasibility_handcheck_candidates.csv")
def test_fit_scores_follow_the_hand_check():
    t = pd.read_csv(INTERIM / "feasibility_handcheck_candidates.csv")
    key = {"Autonomous mobile systems B.Eng.": "autonomous", "AR/VR & visual computing B.Sc.": "arvr",
           "Energy data management B.Sc.": "energydata", "Geo-data & geovisualisation B.Sc.": "geodata"}
    sheet = load("configs/scores_candidates.yaml")["options"]
    for option, g in t.groupby("option"):
        tot = g["ects"].sum()
        e12 = 100 * g.loc[g["verdict"].isin(["E1", "E2"]), "ects"].sum() / tot
        e1 = 100 * g.loc[g["verdict"] == "E1", "ects"].sum() / tot
        new = g.loc[g["verdict"].isin(["T", "N"]), "ects"].sum()
        f = sheet[key[option]]["institutional_fit"]
        assert (f["low"], f["central"]) == (_fit(e1, new), _fit(e12, new)), option
    # robotics path B (week-2 hand check): E1+E2 91.2 %, E1 56.9 %, T+N 12
    f = sheet["robotics_b"]["institutional_fit"]
    assert (f["low"], f["central"]) == (_fit(56.9, 12), _fit(91.2, 12))


def test_gate_and_feasibility_scores_agree():
    sheet = load("configs/scores_candidates.yaml")["options"]
    for key, s in sheet.items():
        assert (s["gate"]["result"] == "pass") == (s["feasibility"]["central"] > 1), key
        for crit in HAND:
            e = s[crit]
            assert 1 <= e["low"] <= e["central"] <= e["high"] <= 5, (key, crit)
            if e["strength"] == "weak":
                assert e["central"] - e["low"] == pytest.approx(e["high"] - e["central"]), (key, crit)


# ---------------- ranking ----------------

@needs("data/interim/candidate_scenarios.csv", "data/interim/ranking_candidates_summary.csv")
def test_candidate_ranking_reproduces_with_the_fixed_seed():
    from study_program_intelligence.analysis import ranking as R
    cfg, sc, cap = R.load(sheet_path=R.CAND_SCORES, scen_path=R.CAND_SCEN)
    a = R.simulate(cfg, sc, cap, cfg["weights"])
    b = R.simulate(cfg, sc, cap, cfg["weights"])
    assert np.array_equal(a.to_numpy(), b.to_numpy())
    assert set(a.columns) == {k for k, v in sc.items() if v["gate"]["result"] == "pass"}
    stored = pd.read_csv(INTERIM / "ranking_candidates_summary.csv")
    stored = stored[stored["scenario"] == "base"].set_index("option")["P(rank 1)"]
    now = R.summarise(a).set_index("option")["P(rank 1)"]
    for o in now.index:
        assert now[o] == pytest.approx(stored[o]), o
