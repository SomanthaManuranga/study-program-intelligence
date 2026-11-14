"""Funnel step 1: is the data there and current? (configs/funnel.yaml; data table in docs/funnel_preregistration.md)

Run from the repository root, after the Destatis tables by Land are downloaded and the timetables are parsed:

    python -m study_program_intelligence.ingest.genesis tables --only 21311-0015_SH 21311-0015_HH ...   (see configs/genesis_tables.yaml)
    python -m study_program_intelligence.transform.timetables
    python -m study_program_intelligence.analysis.funnel_inventory

Every source a rule needs is listed with its place, size, period, retrieval date and gaps. No programme type is
computed and nothing is scored. The matching threshold of the feasibility gate is recomputed with the Step 41
procedure (analysis/feasibility.py, calibrate) so that its value can be written into configs/funnel.yaml.
Outputs: data/interim/funnel2_inventory.json (all numbers), reports/funnel2/step1_inventory.md.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
import yaml

from .funnel_common import INTERIM, REPO_ROOT, REPORTS, md_table, run_stamp, universe
from .funnel_subject_map import clean_label

RAW = REPO_ROOT / "data" / "raw"
FIELDS = REPO_ROOT / "data" / "processed" / "programme_fields_full.csv"
OUT = INTERIM / "funnel2_inventory.json"
REPORT = REPORTS / "step1_inventory.md"
LAENDER = {"SH": "01", "HH": "02", "NI": "03", "HB": "04", "NW": "05", "HE": "06", "RP": "07", "BW": "08", "SL": "10", "BE": "11",
           "BB": "12", "MV": "13", "SN": "14", "ST": "15", "TH": "16"}          # Bavaria (09) is 21311-0015_BY
PHRASE = "inhalte bitte bei der hochschule erfragen"
NOTE = "anmerkung der hochschule"


def manifest(name: str) -> list[dict]:
    p = REPO_ROOT / "docs" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def dates(records: list[dict]) -> str:
    d = sorted(r["retrieved_utc"][:10] for r in records if r.get("retrieved_utc"))
    return "-" if not d else d[0] if d[0] == d[-1] else f"{d[0]} to {d[-1]}"


def left_after_drops(content: str) -> str:
    """What is left of an offer's content once the two dropped parts of the rule text.dropped are removed."""
    c = str(content).lower()
    c = c.split(NOTE, 1)[0]
    return re.sub(r"[\s:;,.\-]+", " ", c.replace(PHRASE, " ")).strip()


def catalogue() -> dict:
    raw = pd.read_csv(REPO_ROOT / "data" / "processed" / "programmes_full.csv", low_memory=False, dtype={"programme_id": str}, usecols=lambda c: c != "content")
    ded = universe()
    content = ded["content"].fillna("")
    low = content.str.lower()
    has_phrase = low.str.contains(PHRASE, regex=False)
    labels = {clean_label(x) for s in ded["subjects"].dropna() for x in s.split("; ")}
    smap = set(pd.read_csv(REPO_ROOT / "configs" / "funnel_subject_map.csv")["label"])
    fields = pd.read_csv(FIELDS, usecols=["field_key"])
    return {"rows": len(raw), "unique_ids": int(raw["programme_id"].nunique()),
            "bachelor_master_germany": int((raw["degree"].isin(["Bachelor/Bakkalaureus", "Master"]) & (raw["country"] == "Deutschland")).sum()),
            "after_dedupe": len(ded), "full_time_after_dedupe": int(ded["full_time"].sum()),
            "bachelor_after_dedupe": int((ded["level"] == "bachelor").sum()), "master_after_dedupe": int((ded["level"] == "master").sum()),
            "institutions": int(ded["institution"].nunique()), "offers_without_a_land": int((~ded["state"].isin(ded["state"].value_counts().index[:16])).sum()),
            "share_with_focus_items": round(float(content.str.contains("Schwerpunkte").mean()), 3),
            "offers_with_the_phrase": int(has_phrase.sum()),
            "offers_with_only_the_phrase": int((low.str.strip().str.strip(".") == PHRASE).sum()),
            "offers_empty_after_drops": int((content.map(left_after_drops) == "").sum()),
            "share_with_subject_labels": round(float(ded["subjects"].notna().mean()), 3), "share_with_coordinates": round(float(ded["lat"].notna().mean()), 3),
            "institution_types": ded["institution_type"].value_counts().to_dict(), "oth_offers": int(ded["is_oth"].sum()),
            "subject_labels": len(labels), "subject_labels_not_in_map": len(labels - smap),
            "language_column": next((c for c in raw.columns if re.search(r"sprach|language", c, re.I)), None),
            "study_field_rows": len(fields), "study_fields": int(fields["field_key"].nunique()),
            "retrieved": dates(manifest("studiensuche_full_manifest.json"))}


def destatis() -> list[dict]:
    recs = {r["id"]: r for r in manifest("genesis_manifest.json")}
    rows = []
    for f in sorted((RAW / "destatis").glob("*.csv")):
        d = pd.read_csv(f, sep=";", dtype=str, usecols=lambda c: c == "time" or c.endswith("attribute_code") or c.endswith("variable_code"))
        sf = next((c for c in d.columns if c.endswith("attribute_code") and d[c].astype(str).str.startswith("SF").any()), None)
        land = sorted(set(d.loc[d["1_variable_code"] == "DLAND", "1_variable_attribute_code"])) if "1_variable_code" in d.columns else []
        years = d["time"].str[:4].astype(int)
        r = recs.get(f.stem, {})
        rows.append({"table": f.stem, "rows": len(d), "first_year": int(years.min()), "last_year": int(years.max()), "land_codes": ",".join(land),
                     "subjects": int(d[sf].nunique()) if sf else 0, "retrieved": (r.get("retrieved_utc") or "-")[:10], "status": r.get("status", "not in manifest")})
    return rows


def laender(tables: list[dict]) -> dict:
    """Each of the 15 files must exist, hold only its own Land and cover 2019-2024."""
    have = {t["table"]: t for t in tables}
    out = {}
    for land, code in LAENDER.items():
        t = have.get(f"21311-0015_{land}")
        out[land] = {"file": bool(t), "own_land_only": bool(t and t["land_codes"] == code),
                     "covers_2019_2024": bool(t and t["first_year"] <= 2019 and t["last_year"] >= 2024), "subjects": t["subjects"] if t else 0}
    return out


def emi_modules() -> dict:
    m = pd.read_csv(INTERIM / "modules_emi_2026.csv", low_memory=False)
    port = yaml.safe_load((REPO_ROOT / "configs" / "oth_portfolio.yaml").read_text(encoding="utf-8"))["programmes"]
    hb = manifest("oth_handbooks_manifest.json")
    return {"modules": len(m), "distinct_titles": int(m["title"].nunique()), "handbook_sets": int(m["programme_id"].nunique()), "by_level": m["level"].value_counts().to_dict(),
            "ects_missing": int(pd.to_numeric(m["ects"], errors="coerce").isna().sum()), "text_missing": int((m["text"].fillna("").str.len() < 50).sum()),
            "portfolio_programmes": len(port), "handbook_documents": len(hb), "retrieved": dates(hb),
            "labs_listed": len(yaml.safe_load((REPO_ROOT / "configs" / "emi_labs.yaml").read_text(encoding="utf-8"))["labs"])}


def norm_title(t: str) -> str:
    t = re.sub(r"\(.*?\)", " ", str(t).lower())
    t = t.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def timetables() -> dict:
    rep = json.loads((INTERIM / "timetable_report.json").read_text(encoding="utf-8"))
    t = pd.read_csv(INTERIM / "timetable_subjects.csv")
    m = pd.read_csv(INTERIM / "modules_emi_2026.csv", low_memory=False)
    subj_exact, subj_norm = set(t["subject"].dropna()), {norm_title(s) for s in t["subject"].dropna()}
    titles = m["title"].dropna()
    distinct = pd.Series(sorted(set(titles)))
    grid = t[t["in_grid"]]
    return {**{k: rep[k] for k in ("rows", "semesters", "groups", "distinct_subject_names", "lecturers")}, "files": rep["files"], "stamp": rep.get("stamp"),
            "grid_cells": len(grid), "grid_cells_with_lecturer": int(grid["lecturer"].notna().sum()),
            "distinct_sessions": int(sum(f["distinct_sessions"] for f in rep["files"])), "listed_without_slot": int((~t["in_grid"]).sum()),
            "room_lists_cut_off": int(sum(f["room_lists_cut_off"] for f in rep["files"])),
            "subjects_per_lecturer_median": float(grid.groupby("lecturer")["subject"].nunique().median()),
            "emi_module_rows": len(titles), "emi_module_rows_found_exact": int(titles.isin(subj_exact).sum()),
            "emi_module_rows_found_normalised": int(titles.map(norm_title).isin(subj_norm).sum()),
            "emi_distinct_titles": len(distinct), "emi_distinct_titles_found_normalised": int(distinct.map(norm_title).isin(subj_norm).sum()),
            "names_in_table": int(t["lecturer"].dropna().map(lambda x: not re.fullmatch(r"L\d{3}", str(x))).sum())}


def threshold() -> dict:
    """The encoder threshold of the Step 41 procedure on the EMI module set, as analysis/feasibility.py computes it."""
    from .feasibility import CALIBRATION, calibrate, centre, embed, load
    d = load()
    emb = centre(embed(d["clean"].tolist()), d["source_file"])
    tau, tpr, fpr, auc, npos, nneg = calibrate(d, emb @ emb.T)
    rep = REPO_ROOT / "reports" / "feasibility.md"
    m = re.search(r"recalibrated on this module set \(Step 41 procedure\): (\d\.\d+)", rep.read_text(encoding="utf-8")) if rep.exists() else None
    return {"value": round(float(tau), 3), "tpr": round(float(tpr), 2), "fpr": round(float(fpr), 2), "auc": round(float(auc), 3),
            "positives": int(npos), "negatives": int(nneg), "earlier_report_value": float(m.group(1)) if m else None,
            "calibration_reference_programmes": sorted(CALIBRATION)}


def others() -> dict:
    from .capture import table5
    from .theme_verdicts import SUBTHEMES
    from .themes import THEMES
    lv = pd.read_csv(INTERIM / "school_leavers_by.csv", dtype={"key": str})
    counties = lv[lv["key"].str.len() == 5]
    snaps = pd.DataFrame(json.loads((REPO_ROOT / "docs" / "jobsuche_snapshots.json").read_text(encoding="utf-8")))
    t5 = table5()
    intake = manifest("intake_benchmark_manifest.json")
    hub = Path.home() / ".cache" / "huggingface" / "hub" / "models--intfloat--multilingual-e5-base"
    return {"school_leavers": {"years": f"{int(lv['year'].min())}-{int(lv['year'].max())}", "missing_years": sorted(set(range(int(lv["year"].min()), int(lv["year"].max()) + 1)) - set(lv["year"])),
                               "counties_last_year": int(counties[counties["year"] == counties["year"].max()]["key"].nunique()), "retrieved": dates(manifest("regional_manifest.json"))},
            "master_origins": {"campuses": len(t5), "students": int(t5["total"].sum())},
            "job_snapshots": {d: int(n) for d, n in snaps.groupby("date").size().items()},
            "job_keywords_by_date": {d: int(n) for d, n in snaps.groupby("date")["keyword_id"].nunique().items()},
            "job_null_totals_latest": int(snaps[snaps["date"] == snaps["date"].max()]["total"].isna().sum()),
            "published_intake": {"documents": len(intake), "universities": sorted({r["owner"] for r in intake}), "versions": [r["version"] for r in intake],
                                 "retrieved": dates(intake)},
            "old_topic_lists": len(THEMES) + len(SUBTHEMES),
            "reference_files_from_run_1": sum(1 for p in (INTERIM / "funnel_refs").rglob("*") if p.is_file()) if (INTERIM / "funnel_refs").exists() else 0,
            "encoder_cached": hub.exists(),
            "rule_files_for_step_2": {f: (REPO_ROOT / "configs" / f).exists() for f in ("funnel_boilerplate.yaml", "funnel_title_stoplist.yaml")}}


def main() -> None:
    stamp = run_stamp()
    cat, des, emi, tt, thr, oth = catalogue(), destatis(), emi_modules(), timetables(), threshold(), others()
    land = laender(des)
    inv = {"stamp": stamp, "catalogue": cat, "destatis": des, "laender": land, "emi": emi, "timetables": tt, "threshold": thr, "other": oth}
    OUT.write_text(json.dumps(inv, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")

    by = {t["table"]: t for t in des}
    span = lambda ids: "; ".join(f"{i}: {by[i]['first_year']}-{by[i]['last_year']}" for i in ids if i in by)
    ok_l = [k for k, v in land.items() if v["covers_2019_2024"] and v["own_land_only"]]
    pi = oth["published_intake"]
    plans = ", ".join(f"{f['semester']} printed {f['plan_printed']}" for f in tt["files"])
    rows = [   # one row per line of the data table in docs/funnel_preregistration.md, in its order
        ("Study catalogue: all bachelor and master offers", "2, 3", "data/processed/programmes_full.csv",
         f"{cat['rows']:,} offers; {cat['after_dedupe']:,} bachelor and master offers in Germany after merging variants, {cat['full_time_after_dedupe']:,} of them full-time",
         "snapshot", cat["retrieved"],
         f"focus items in {cat['share_with_focus_items']:.0%} of offers; {cat['offers_with_the_phrase']:,} offers carry the boilerplate phrase and "
         f"{cat['offers_empty_after_drops']:,} have no content left once the phrase and the university's note are dropped; {cat['study_fields']} study fields; "
         f"{cat['subject_labels']} subject labels, {cat['subject_labels_not_in_map']} without a Destatis code"),
        ("EMI modules and OTH offers", "3, 7", "data/interim/modules_emi_2026.csv; configs/emi_labs.yaml",
         f"{emi['modules']} module rows ({emi['distinct_titles']} distinct titles) from {emi['handbook_sets']} handbook sets; {cat['oth_offers']} OTH offers in the catalogue; {emi['labs_listed']} labs listed",
         "handbooks valid from winter 2026/27", emi["retrieved"],
         f"{emi['ects_missing']} modules without ECTS; {emi['portfolio_programmes'] - emi['handbook_sets']} of {emi['portfolio_programmes']} EMI programmes without a handbook set"),
        ("First-years and graduates by subject, Bavaria and Germany", "3, 4, 6", "data/raw/destatis/",
         span(["21311-0012_DE", "21311-0015_BY", "21321-0003_DE", "21321-0006_BY"]), "yearly", by.get("21311-0015_BY", {}).get("retrieved", "-"), "-"),
        ("First-years by subject, other Laender", "3", "data/raw/destatis/21311-0015_<Land>.csv",
         f"{len(ok_l)} of {len(land)} Laender: own Land only and 2019-2024 covered", "yearly", max((by[f'21311-0015_{k}']['retrieved'] for k in land if f'21311-0015_{k}' in by), default="-"),
         "missing: " + (", ".join(k for k in land if k not in ok_l) or "none")),
        ("Job ads", "5", "docs/jobsuche_snapshots.json",
         "; ".join(f"{d}: {n} counts for {oth['job_keywords_by_date'][d]} keywords" for d, n in oth["job_snapshots"].items()), "day counts", max(oth["job_snapshots"]),
         "old keywords only; the new keywords are counted in Step 5 on one day, without history"),
        ("Language of instruction per offer", "5", "data/processed/programmes_full.csv", "no such field" if not cat["language_column"] else cat["language_column"], "-", "-",
         "rule labour.english cannot pair German and English keywords; stated limit"),
        ("School leavers by county (bachelor origins)", "6", "data/interim/school_leavers_by.csv",
         f"{oth['school_leavers']['counties_last_year']} counties in the last year", oth["school_leavers"]["years"], oth["school_leavers"]["retrieved"],
         "missing years: " + (", ".join(map(str, oth["school_leavers"]["missing_years"])) or "none")),
        ("Students by campus (master origins)", "6", "data/raw/regional/by_studierende_ws2024.pdf",
         f"{oth['master_origins']['campuses']} campuses, {oth['master_origins']['students']:,} students", "winter 2024/25", oth["school_leavers"]["retrieved"], "-"),
        ("Published first-year numbers of single programmes (level check)", "6", "data/raw/intake_benchmark/",
         f"{pi['documents']} documents from {len(pi['universities'])} universities; with the two baseline anchors, one row per programme gives 4 rows", ", ".join(pi["versions"]), pi["retrieved"],
         "one subject only; reported as a check, no correction"),
        ("Reference handbooks of other universities", "7", "data/interim/funnel_refs/", f"{oth['reference_files_from_run_1']} files left from run 1 (counted, not opened)",
         "-", "not recorded here", "collected again in Step 7 for the new candidates"),
        ("EMI timetables (internal)", "7", "data/raw/oth_internal/ (not in the repository)",
         f"{tt['groups']} group plans, {tt['grid_cells']:,} timetable entries ({tt['distinct_sessions']} distinct sessions), {tt['distinct_subject_names']} subject names, {tt['lecturers']} lecturers (labels only)",
         ", ".join(tt["semesters"]), f"provided by the supervisor in Nov 2026; plans: {plans}", "no ECTS, no hours, no student numbers"),
        ("Published first-year numbers of similar programmes outside the south", "7", "-", "not collected yet", "-", "-",
         "looked for after the gate list is fixed, for the gate candidates only (popularity tier 1)"),
    ]
    table = pd.DataFrame(rows, columns=["Source", "Steps", "Where", "Size", "Period", "Retrieved", "Gaps and notes"])
    lines = ["# Funnel step 1: data inventory (generated)", "",
             f"Code commit {stamp['commit']}, run on {stamp['date']}, tracked files clean: {stamp['clean']}. Timetable table from commit {(tt.get('stamp') or {}).get('commit')}.", "",
             md_table(table), "",
             "## Destatis tables", "", md_table(pd.DataFrame(des)), "",
             "## Timetable files", "", md_table(pd.DataFrame(tt["files"])), "",
             f"Timetable subjects against EMI handbook modules, by title: {tt['emi_module_rows_found_normalised']} of {tt['emi_module_rows']} module rows after normalising the titles "
             f"({tt['emi_module_rows_found_exact']} letter for letter); {tt['emi_distinct_titles_found_normalised']} of {tt['emi_distinct_titles']} distinct titles. A first look only; "
             f"Step 7 matches by content. Names left in the table: {tt['names_in_table']}. Room lists cut off in the PDF: {tt['room_lists_cut_off']}.", "",
             "## Matching threshold for Step 7", "",
             f"calibrate() gives {thr['value']} (true-positive rate {thr['tpr']}, false-positive rate {thr['fpr']}, AUC {thr['auc']}; {thr['positives']} positive and "
             f"{thr['negatives']} negative reference modules from {len(thr['calibration_reference_programmes'])} reference programmes of the baseline). "
             f"Value in the earlier feasibility report: {thr['earlier_report_value']}.", "",
             "## Other checks", "",
             f"- Old topic lists available for the Step 2 validation: {oth['old_topic_lists']}.",
             f"- Encoder in the local cache: {oth['encoder_cached']}.",
             f"- Rule files Step 2 has to write first: {oth['rule_files_for_step_2']}.",
             f"- Latest job-ad snapshot: {oth['job_null_totals_latest']} null totals."]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[:3]))
    print(table[["Source", "Size", "Gaps and notes"]].to_string(index=False))
    print(f"\nthreshold {thr['value']} (earlier report {thr['earlier_report_value']}); Laender complete {len(ok_l)}/{len(land)}. Written: {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
