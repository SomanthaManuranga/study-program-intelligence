"""Data-sufficiency items: nationality split adds up, written theme rules reproduce the funnel, German-only sensitivity."""

from pathlib import Path

import pandas as pd
import pytest
import yaml

from study_program_intelligence.analysis import demand_split, ranking, theme_verdicts

REPO = Path(__file__).resolve().parents[1]
needs_data = pytest.mark.skipif(not (REPO / "data" / "raw" / "destatis" / "21311-0015_BY.csv").exists(), reason="no cached data")


@needs_data
def test_german_plus_foreign_equals_all_first_years():
    """German + foreign first-years from the split equal the all-nationality series used by the forecast."""
    long = demand_split.load()
    by = long[(long["region"] == "BY") & (long["kind"] == "first-years") & long["code"].isin(["SF079", "SF123", "SF200"])]
    split = by.groupby("year")["value"].sum()
    total = pd.read_csv(REPO / "data" / "raw" / "destatis" / "21311-0015_BY.csv", sep=";", dtype=str)
    total = total[total["2_variable_attribute_code"].isna() & total["3_variable_attribute_code"].isna()
                  & total["4_variable_attribute_code"].isin(["SF079", "SF123", "SF200"])]
    total = total.assign(year=total["time"].str[:4].astype(int), v=pd.to_numeric(total["value"], errors="coerce")).groupby("year")["v"].sum()
    assert split.loc[2019] == total.loc[2019] and split.loc[2024] == total.loc[2024] == 4936


@needs_data
def test_university_type_split_is_consistent():
    """LfStat Tabelle 3.2: the parser only accepts splits where German + foreign = combined."""
    ut = demand_split.university_type().set_index("university type")
    assert set(ut.index) == {"universities", "universities of applied sciences"}
    assert (ut["foreign share 1st univ. sem. %"].between(20, 60)).all()


@needs_data
def test_written_theme_rules_reproduce_the_funnel_for_the_original_candidates():
    d = theme_verdicts.verdicts().set_index(["theme", "level"])
    assert d.at[("cybersecurity", "BA"), "verdict"] == "candidate"
    assert d.at[("cybersecurity", "MA"), "verdict"] == "candidate"
    assert d.at[("robotics", "BA"), "verdict"] == "candidate"
    assert d.at[("embedded_iot", "MA"), "verdict"] == "candidate"
    assert d.at[("microelectronics", "MA"), "verdict"] == "watch list"
    assert d.at[("media_tech", "BA"), "verdict"].startswith("drop")
    assert d.at[("ai_data", "BA"), "verdict"].startswith("drop")
    original = d[d["original verdict"] != "not screened"]
    assert (original["agrees"] != "no").sum() >= len(original) - 2


def test_german_only_trend_scores_cover_all_options_and_stay_on_scale():
    sheet = yaml.safe_load((REPO / "configs" / "scores.yaml").read_text(encoding="utf-8"))
    tg = sheet["sensitivity"]["trend_german"]
    assert set(tg) == set(sheet["options"])                       # fairness: every option gets the same treatment
    for o, t in tg.items():
        assert 1 <= t["low"] <= t["central"] <= t["high"] <= 5
        base = sheet["options"][o]["student_demand"]["trend"]
        assert t["high"] - t["low"] <= base["high"] - base["low"]  # widths kept (or clipped at the floor)


@needs_data
def test_german_trend_sensitivity_changes_only_trend_scores():
    _, sc_base, _ = ranking.load()
    _, sc_g, _ = ranking.load(german_trend=True)
    for o in sc_base:
        for k in ranking.HAND:
            assert sc_base[o][k] == sc_g[o][k]
    assert sc_g["cyber_bsc"]["student_demand"]["trend"]["central"] == 3
