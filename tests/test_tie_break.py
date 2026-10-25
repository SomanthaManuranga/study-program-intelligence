"""Hand-check sheet and demand tie-break (docs/criteria_tie_break.md, E5)."""

import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
INTERIM = REPO / "data" / "interim"
needs = lambda *files: pytest.mark.skipif(not all((REPO / f).exists() for f in files), reason="no generated data")


# ---------------- hand-check sheet ----------------

@needs("data/interim/modules_references.csv", "data/interim/modules_emi_2026.csv", "data/interim/feasibility_handcheck_candidates.csv")
def test_sheet_covers_every_e2_verdict_and_resolves_every_emi_module():
    from study_program_intelligence.report import handcheck_sheet as H
    cfg, hc, _ = H.config()
    rows = H.sheet_rows(cfg, hc)                       # raises if a reference or EMI module does not resolve
    e2 = {("robotics_b", k) for k, v in hc["robotics_bsc"]["modules"].items()
          if v["verdict"] == "E2" and not v.get("elective") and v.get("path", "B") == "B"}
    e2 |= {("arvr", k) for k, v in hc["arvr_bsc"]["modules"].items() if v["verdict"] == "E2" and not v.get("elective")}
    assert set(zip(rows["candidate"], rows["candidate module"])) == e2
    assert not rows.filter(like="text").apply(lambda c: c.str.contains(r"Prof\. [A-Z][a-z]")).any().any()   # names masked


@needs("data/interim/feasibility_modules.csv", "data/interim/feasibility_handcheck_candidates.csv")
def test_recompute_reproduces_the_gate_and_applies_rejections():
    from study_program_intelligence.report import handcheck_sheet as H
    cfg, hc, rule = H.config()
    none = {**cfg, "decisions": {}}
    r = H.f1_f4(H.verdict_table("robotics_b", none, hc), rule)
    a = H.f1_f4(H.verdict_table("arvr", none, hc), rule)
    assert (r["F1 %"], r["T"], r["N"], r["F4 %"]) == (91.2, 7, 5, 25.5)
    assert (a["F1 %"], a["T"], a["N"], a["F4 %"]) == (91.7, 0, 10, 32.2)
    rej = H.f1_f4(H.verdict_table("arvr", {**cfg, "decisions": {"arvr|Bildverarbeitung 2": "reject"}}, hc), rule)
    assert rej["N"] == 15 and not rej["F2 pass"]       # one rejected module taught as N breaks the N cap


# ---------------- demand tie-break ----------------

@needs("data/interim/tie_break.csv", "data/interim/candidate_demand.csv")
def test_tie_break_series_match_the_candidate_demand_table():
    t = pd.read_csv(INTERIM / "tie_break.csv", dtype={"value": str})
    d = pd.read_csv(INTERIM / "candidate_demand.csv").set_index(["candidate", "region"])
    for c, ser in (("arvr", "Medieninformatik"), ("robotics_b", "Mechatronik + Technische Informatik")):
        for reg in ("BY", "DE"):
            v = lambda grp, m: t[(t["candidate"] == c) & (t["series"] == ser) & (t["region"] == reg) & (t["group"] == grp)
                                 & (t["metric"] == m)]["value"].iloc[0]
            assert int(v("all", "2019")) == d.loc[(c, reg), "all start"] and int(v("all", "2024")) == d.loc[(c, reg), "all end"]
            assert float(v("German", "%/yr 2019-24")) == d.loc[(c, reg), "German %/yr"]
            assert int(v("German", "2024")) + int(v("foreign", "2024")) == int(v("all", "2024"))


@needs("data/interim/tie_break.csv", "data/interim/candidate_competition.csv")
def test_tie_break_competitors_match_the_competition_table():
    t = pd.read_csv(INTERIM / "tie_break.csv", dtype={"value": str})
    comp = pd.read_csv(INTERIM / "candidate_competition.csv").set_index("candidate")
    for c in ("arvr", "robotics_b"):
        v = lambda m: int(t[(t["candidate"] == c) & (t["metric"] == m)]["value"].iloc[0])
        assert v("dedicated institutions within 150 km") == comp.at[c, "dedicated institutions <=150 km"]
        assert v("dedicated institutions Germany") == comp.at[c, "dedicated institutions DE"]


@needs("data/interim/tie_break.csv")
def test_job_ads_come_from_the_latest_snapshot_and_missing_keywords_say_why():
    t = pd.read_csv(INTERIM / "tie_break.csv", dtype={"value": str})
    s = pd.DataFrame(json.loads((REPO / "docs" / "jobsuche_snapshots.json").read_text(encoding="utf-8")))
    rob = s[(s["keyword_id"] == "robotik") & (s["date"] == s["date"].max()) & (s["region_id"] == "germany")]["total"].iloc[0]
    got = t[(t["series"] == "robotik") & (t["region"] == "germany")]["value"].iloc[0]
    assert int(got) == rob
    missing = t[(t["signal"] == "job ads") & (t["candidate"] == "arvr")]["value"]
    assert missing.str.startswith("no data").all()


def test_new_keywords_are_in_the_snapshot_config():
    kw = {k["id"] for k in yaml.safe_load((REPO / "configs" / "jobsuche.yaml").read_text(encoding="utf-8"))["keywords"]}
    assert {"virtual_reality", "augmented_reality", "computergrafik", "servicerobotik", "robotik"} <= kw


@needs("data/interim/modules_references.csv", "data/interim/modules_emi_2026.csv")
def test_sheet_excerpts_start_at_a_learning_outcome_heading():
    from study_program_intelligence.report import handcheck_sheet as H
    cfg, hc, _ = H.config()
    rows = H.sheet_rows(cfg, hc)
    heading = r"^(Lernziele|Qualifikationsziele|Lernergebnisse|Learning Outcomes)"
    for col in [c for c in rows.columns if "text" in c]:
        assert rows[col].str.contains(heading).all(), col


@needs("data/interim/tie_break.csv")
def test_proxy_fit_and_per_competitor_rows():
    t = pd.read_csv(INTERIM / "tie_break.csv", dtype={"value": str})
    v = lambda c, m: t[(t["candidate"] == c) & (t["metric"] == m)]["value"].iloc[0]
    assert v("arvr", "dedicated offers whose catalogue subject is the proxy subject") == "0"
    for c in ("arvr", "robotics_b"):
        german = int(t[(t["candidate"] == c) & (t["region"] == "BY") & (t["group"] == "German") & (t["metric"] == "2024")]["value"].iloc[0])
        assert int(v(c, "2024 per dedicated Bavarian institution")) == round(german / int(v(c, "dedicated institutions Bavaria")))
