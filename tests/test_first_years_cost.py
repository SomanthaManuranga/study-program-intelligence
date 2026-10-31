"""First-years through the shared code path and cost in professor-equivalents (docs/criteria_capture_cost_demand.md)."""

from pathlib import Path

import pandas as pd
import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
INTERIM = REPO / "data" / "interim"
needs = lambda *files: pytest.mark.skipif(not all((REPO / f).exists() for f in files), reason="no generated data")


# ---------------- E1: cyber unchanged through the shared path ----------------

@needs("data/interim/capture_scenarios.csv", "data/interim/option_scenarios.csv")
def test_cyber_step_47_48_numbers_are_unchanged():
    s = pd.read_csv(INTERIM / "capture_scenarios.csv").set_index("scenario")
    assert list(s.loc[["low", "central", "high"], "gross first-years"]) == [21, 39, 75]
    assert list(s.loc[["low", "central", "high"], "(b) net new to OTH"]) == [15.3, 32.0, 64.4]
    o = pd.read_csv(INTERIM / "option_scenarios.csv")
    o = o[o["option"] == "cyber_bsc"].set_index("scenario")
    assert list(o.loc[["low", "central", "high"], "gross first-years"]) == [21, 39, 75]
    assert list(o.loc[["low", "central", "high"], "(b) net new to OTH"]) == [15.3, 32.0, 64.4]


@needs("data/interim/capture_scenarios.csv", "data/raw/destatis/21311-0015_BY.csv")
def test_shared_layer_keeps_the_cyber_model_values():
    from study_program_intelligence.analysis import first_years as F
    from study_program_intelligence.analysis.capture import RAMP
    from study_program_intelligence.analysis.demand_split import load
    cfg = F.config()
    rows = pd.DataFrame(F.first_years("cyber_bsc", cfg["candidates"]["cyber_bsc"], load(), cfg["first_intake_year"]))
    steady = rows[rows["phase"] == "steady state"].set_index("scenario")["gross (model, base year)"]
    year1 = rows[rows["phase"] == "year 1"].set_index("scenario")["gross (model, base year)"]
    assert list(steady.loc[["low", "central", "high"]]) == [21, 39, 75]
    assert list(year1.loc[["low", "central", "high"]]) == [round(g * RAMP[0], 1) for g in (21, 39, 75)]


# ---------------- E2: robotics path B ----------------

@needs("data/interim/candidate_scenarios.csv", "data/raw/destatis/21311-0015_BY.csv")
def test_robotics_first_years_are_complete_and_the_german_trend_is_an_input():
    from study_program_intelligence.analysis import first_years as F
    from study_program_intelligence.analysis.demand_split import load
    cfg, long = F.config(), load()
    c = cfg["candidates"]["robotics_b"]
    rows = pd.DataFrame(F.first_years("robotics_b", c, long, cfg["first_intake_year"]))
    assert set(zip(rows["scenario"], rows["phase"])) == {(s, p) for s in ("low", "central", "high") for p in ("year 1", "steady state")}
    assert ((rows["German"] + rows["international"] - rows["gross"]).abs() <= 0.11).all()
    pl = F.pool(c, long)
    assert round(pl["German %/yr"], 1) == -3.3
    # the trend feeds the projection: German first-years in steady state = model gross x German share x (1 - 3.3 %)^6
    cen = rows[(rows["scenario"] == "central") & (rows["phase"] == "steady state")].iloc[0]
    gross0 = F.scenarios("robotics_b", c).loc["central", "gross"]
    expected = gross0 * pl["German share"] * (1 + pl["German %/yr"] / 100) ** (cfg["first_intake_year"] + 2 - pl["base year"])
    assert cen["German"] == round(expected, 1)
    flat = {**pl, "German %/yr": 0.0}
    assert F.project(gross0, flat, 2030)[0] > F.project(gross0, pl, 2030)[0]


# ---------------- E4: professor-equivalents from config ----------------

def test_regulation_quote_is_in_config_and_cached_source():
    cfg = yaml.safe_load((REPO / "configs" / "cost.yaml").read_text(encoding="utf-8"))
    assert cfg["teaching_load_sws_per_semester"] == 18 and cfg["regulation"]["source"] == "AVBayHIG § 4 Abs. 1 Nr. 1"
    f = REPO / cfg["regulation"]["file"]
    if f.exists():
        import html
        import re
        text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", f.read_text(encoding="utf-8", errors="ignore"))))
        assert cfg["regulation"]["quote"] in text


@needs("data/interim/candidate_first_years.csv", "data/interim/feasibility_modules.csv")
def test_professor_equivalents_recomputed_from_config():
    from study_program_intelligence.analysis import cost as C
    cfg = yaml.safe_load((REPO / "configs" / "cost.yaml").read_text(encoding="utf-8"))
    year = cfg["teaching_load_sws_per_semester"] * cfg["semesters_per_year"]          # 36 SWS-semesters
    t = C.table(cfg).set_index("level")
    by_hand = {"(a)": 5 * cfg["sws_per_ects"] / year,                                  # 15 - 10 ECTS above the cap
               "(b)": (15 + 8.25) * cfg["sws_per_ects"] / year,                         # N 15 + T 8.25
               "(c)": 10 * cfg["sws_per_ects"] / year + 2 + 1}                          # T 10 + 2 professorships + lab engineer
    for prefix, v in by_hand.items():
        row = t[t.index.str.startswith(prefix)].iloc[0]
        assert row["professor-equivalents, total"] == round(v, 3), prefix
    cy = t[t.index.str.startswith("(c)")].iloc[0]
    assert cy["professor-equivalents, all new teaching (no positions)"] == round((45 + 10) * cfg["sws_per_ects"] / year, 3)
    k = 165 / 137                                                                       # OTH taught ECTS / reference base
    scaled = {"(a)": (15 * k - 10) * cfg["sws_per_ects"] / year, "(b)": (15 + 8.25) * k * cfg["sws_per_ects"] / year}
    for prefix, v in scaled.items():
        assert t[t.index.str.startswith(prefix)].iloc[0]["all new teaching scaled to 165 taught ECTS"] == round(v, 3), prefix
    fy = pd.read_csv(INTERIM / "candidate_first_years.csv")
    rc = fy[(fy["candidate"] == "robotics_b") & (fy["scenario"] == "central") & (fy["phase"] == "steady state")]["gross"].iloc[0]
    assert t[t.index.str.startswith("(b)")].iloc[0]["professor-equivalents per first-year, central"] == round(by_hand["(b)"] / rc, 3)
