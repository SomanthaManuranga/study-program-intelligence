"""Funnel step 5: keywords and job ads (configs/funnel.yaml: labour; docs/criteria_funnel_step5.md)."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from study_program_intelligence.analysis import funnel_labour as L

REPO = Path(__file__).resolve().parents[1]
INTERIM = REPO / "data" / "interim"
needs = lambda *files: pytest.mark.skipif(not all((REPO / f).exists() for f in files), reason="no generated data")


def test_titles_are_split_as_the_rule_says():
    assert L.title_parts("Elektro- und Informationstechnik (dual)") == ["elektro-", "informationstechnik"]      # hyphens stay
    assert L.title_parts("Data Science & Artificial Intelligence / KI, Robotik + Automation") == ["data science", "artificial intelligence", "ki", "robotik", "automation"]
    assert L.title_parts("Industrie-4.0-Informatik") == ["industrie-4.0-informatik"]            # hyphens stay
    assert L.title_parts("Sound and Music Production") == ["sound", "music production"]
    assert L.title_parts("2 [X]") == []


def test_keywords_are_the_three_most_shared_phrases_or_the_nearest_title():
    titles = ["Robotik und Automation", "Robotik", "Automation und Robotik", "Mechatronik und Robotik", "Mechatronik dual", "Informatik und Technik"]
    drop = {"dual", "informatik"}
    assert L.ranked_phrases(titles, drop)[:2] == [("robotik", 4), ("automation", 2)]
    assert L.keywords_of(titles, titles[0], drop) == (["robotik", "automation"], "phrases in 2 or more titles")     # "mechatronik" is in one title only as a part
    assert L.keywords_of(["Bionik und Sensorik", "Lasertechnik"], "Bionik und Sensorik", drop) == (["bionik", "sensorik"], "parts of the member nearest the centroid")
    assert L.keywords_of(["Informatik", "Informatik dual"], "Informatik", drop) == ([], "parts of the member nearest the centroid")
    assert L.ranked_phrases(["Künstliche Intelligenz", "Kuenstliche Intelligenz", "Künstliche Intelligenz"], set()) == [("künstliche intelligenz", 3)]


@needs("docs/funnel_keywords.csv", "data/interim/funnel2_offer_types.csv")
def test_the_keyword_file_is_what_the_rule_gives():
    d = pd.read_csv(INTERIM / "funnel2_offer_types.csv", low_memory=False)
    k = pd.read_csv(REPO / "docs" / "funnel_keywords.csv", keep_default_na=False)
    built, info = L.build_keywords(d)
    assert built.astype(str).reset_index(drop=True).equals(k.astype(str).reset_index(drop=True))
    assert k["type"].nunique() == (d["type"] >= 0).groupby(d["type"]).any().sum() - 0 if False else k["type"].nunique() == d.loc[d["type"] >= 0, "type"].nunique()
    stop = L.stoplist() | set(info["generic by the 5 % rule"])
    real = k[k["rank"] > 0]
    assert not real["keyword"].map(L.normalise).isin(stop).any() and (real.groupby("type").size() <= 3).all()
    for c in real["type"].drop_duplicates().sample(40, random_state=0):                        # the rule again, written out
        titles = d.loc[d["type"] == c, "clean_title"]
        n = {}
        for t in titles:
            for p in {L.normalise(x) for x in L.title_parts(t)} - stop:
                n[p] = n.get(p, 0) + 1
        twice = sorted([p for p, v in n.items() if v >= 2], key=lambda p: (-n[p], p))[:3]
        mine = [L.normalise(x) for x in real.loc[real["type"] == c, "keyword"]]
        if twice:
            assert sorted(mine, key=lambda p: (-n[p], p)) == mine and {n[p] for p in mine} == {n[p] for p in twice}


@needs("data/interim/funnel2_labour.csv", "data/interim/funnel2_job_counts.csv", "data/interim/funnel2_step5.json", "docs/funnel_keywords.csv")
def test_the_measure_is_the_median_keyword_count_within_100_km():
    out = pd.read_csv(INTERIM / "funnel2_labour.csv", keep_default_na=False, na_values=[""])
    c = pd.read_csv(INTERIM / "funnel2_job_counts.csv", keep_default_na=False)
    k = pd.read_csv(REPO / "docs" / "funnel_keywords.csv", keep_default_na=False)
    r = json.loads((INTERIM / "funnel2_step5.json").read_text(encoding="utf-8"))
    latest = c.sort_values("date").drop_duplicates(["keyword", "region"], keep="last").set_index(["keyword", "region"])["total"]
    assert len(out) == r["units"] == 1285 and (c["total"] >= 0).all()
    assert L.REGIONS["amberg_100km"]["wo"] == "Amberg, Oberpfalz"
    raw = sorted((REPO / "data" / "raw" / "jobsuche_funnel").glob("*/*.json"))                 # every stored radius reply is centred on the right Amberg
    for f in raw[::25]:
        j = json.loads(f.read_text(encoding="utf-8"))
        if j["region"] == "amberg_100km":
            assert abs(j["reply"]["woOutput"]["koordinaten"][0]["lat"] - 49.4537) < 0.05, f.name
    for row in out[out["labour input"] == "ok"].sample(60, random_state=0).itertuples():
        kws = k.loc[(k["type"] == row.type) & (k["rank"] > 0), "keyword"]
        near = [latest[(x, "amberg_100km")] for x in kws]
        assert out.at[row.Index, "ads within 100 km (median keyword)"] == pytest.approx(np.median(near))
        assert out.at[row.Index, "ads within 100 km (largest keyword)"] == max(near)
        assert out.at[row.Index, "ads in Germany (sum of keywords)"] == sum(latest[(x, "germany")] for x in kws)
    prim = out[out["primary"]]
    need = set(k.loc[k["type"].isin(prim["type"]) & (k["rank"] > 0), "keyword"])
    have = {kw for kw, reg in latest.index if all((kw, x) in latest.index for x in L.REGIONS)}
    assert (prim["labour input"] == "ok").sum() == sum(1 for t in prim["type"] if set(k.loc[(k["type"] == t) & (k["rank"] > 0), "keyword"]) <= have and (k.loc[k["type"] == t, "rank"] > 0).any())
    assert len(need - have) == 0 or r["primary"]["missing"]
