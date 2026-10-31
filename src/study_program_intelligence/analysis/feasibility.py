"""Feasibility with EMI's existing resources: rule F1-F4 for the current options (re-scope, week 2).

Run from the repository root (after transform.modules --set emi2026 and --set references):

    python -m study_program_intelligence.analysis.feasibility

Rule: configs/feasibility.yaml (pre-registered). Labs: configs/emi_labs.yaml.
Method (the Step 41 method, unchanged):
- module texts cleaned as in analysis/module_gaps.py (title + content/learning outcomes), multilingual-e5-base embeddings,
  centred per handbook; a reference module is covered (E1/E2) if its best EMI match >= the threshold;
- the threshold is recalibrated with the Step 41 procedure on this module set (best-match Youden on the topic reference
  set), as configs/feasibility.yaml requires when the EMI module set grows;
- bachelor references are compared with EMI bachelor modules, master references with EMI bachelor and master modules;
- coverage is ECTS-weighted over the reference's taught modules (frame modules - thesis, practical phase, dual-study
  items, placeholder electives - left out), as in Step 41; missing ECTS = 5.
Reference curricula: cyber bachelor = TH Ingolstadt, TH Deggendorf, THWS (full-time; FAU is part-time and left out);
cyber master = TH Ingolstadt, TH Deggendorf, HDBW; robotics bachelor = Hochschule Kempten Robotik. Equal-evidence
candidates (configs/reference_documents.yaml): autonomous systems = TH Deggendorf EM-B, AR/VR & visual computing =
Hochschule Coburg Visual Computing, energy data = FH Dortmund, geo-data = Hochschule München Geodata Science. The
thresholds are calibrated on the week-2 reference programmes only (CALIBRATION), so adding references does not move
the week-2 results; "core" coverage leaves the listed electives out (a degree needs only some of them).
F2 is checked on the uncovered share scaled to OTH's taught ECTS (bachelor 165, master 60). F3: modules whose practical
part needs a capability no EMI lab has (configs/emi_labs.yaml "missing"). F4: covered ECTS attributed to the OTH
programme of each best match; the largest share must not exceed 50 %.
The matches are automatic; every match counted as covered for a SHORTLISTED candidate is confirmed by hand later.
The hand-check tables below the automatic ones show the PROPOSED verdicts (configs/feasibility_handcheck.yaml); the
report ends with the DECIDED gates (Soma's verdicts, configs/handcheck_sheet.yaml, via report/handcheck_sheet.py),
so this report and docs/evidence_tie_break.md cannot disagree after a rerun.
Outputs: data/interim/feasibility_modules.csv, reports/feasibility.md.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from study_program_intelligence.analysis.module_gaps import (OT, centre, category, clean, embed, tfidf_matrix, topics,
                                                            youden)

REPO_ROOT = Path(__file__).resolve().parents[3]
RULE = REPO_ROOT / "configs" / "feasibility.yaml"
BASE_MODULES = REPO_ROOT / "data" / "interim" / "modules.csv"
EMI_2026 = REPO_ROOT / "data" / "interim" / "modules_emi_2026.csv"
REFS = REPO_ROOT / "data" / "interim" / "modules_references.csv"
OUT = REPO_ROOT / "data" / "interim" / "feasibility_modules.csv"
REPORT = REPO_ROOT / "reports" / "feasibility.md"
HANDCHECK = REPO_ROOT / "configs" / "feasibility_handcheck.yaml"

OPTIONS = {  # option -> (level, reference programmes)
    "Cybersecurity B.Sc.": ("BA", ["thi_ba_csi", "deg_ba_cy", "thws_ba_is"]),
    "Cyber/OT M.Sc.": ("MA", ["thi_ma_cse", "deg_ma_cy", "hdbw_ma_cs"]),
    "Robotics + AI B.Sc.": ("BA", ["hske_ba_rob"]),
    "Autonomous mobile systems B.Eng.": ("BA", ["thd_ba_em"]),
    "AR/VR & visual computing B.Sc.": ("BA", ["hsc_ba_vc"]),
    "Energy data management B.Sc.": ("BA", ["fhdo_ba_eedm"]),
    "Geo-data & geovisualisation B.Sc.": ("BA", ["hm_ba_gds"]),
}
CALIBRATION = ["thi_ba_csi", "deg_ba_cy", "thws_ba_is", "thi_ma_cse", "deg_ma_cy", "hdbw_ma_cs", "hske_ba_rob"]   # week 2
EXTRA_FRAME = re.compile(r"^RO\s?(5[12]\d?|8\d+)\b|praktische tätigkeit|duale praxis", re.I)   # Kempten practical/dual items
REF_FRAME = re.compile(r"betriebliche praxis|praxisergänzende|industriepraktikum|praxisbegleitende|bachelorseminar|"
                       r"wahlmodul fwp", re.I)   # practical-phase items and placeholders of the equal-evidence references
ELECTIVE_TYPE = re.compile(r"Art des Moduls ECTS.{0,200}?Wahlpflichtfach", re.S)   # FH Dortmund header table
ELECTIVE = re.compile(r"wahl|elective|schwerpunkt|vertiefung", re.I)
NEEDS = {  # capability -> pattern in a module's title or text
    "security_lab": re.compile(r"penetration|pentest|forensi|incident response|security operations|\bsoc\b|hacking|cyber ?range|"
                               r"red team|blue team|malware.?analy", re.I),
    "industrial_robots": re.compile(r"industrieroboter|industrial robot|kollaborative robot|collaborative robot|cobot|roboterzelle|"
                                    r"robot(er)?zelle|robot cell", re.I),
    "battery_lab": re.compile(r"batterietechnolog|batteriezell|battery cell|ladesäule|ladestation|wasserstofftechnolog|"
                              r"brennstoffzell", re.I),
}
OTH_DRAFT = {"taught": 165, "reused_or_adapted": 110, "new_by_new_staff": 45, "teaching_assignments": 10}   # docs/evidence_benchmarks.md


def load() -> pd.DataFrame:
    base = pd.read_csv(BASE_MODULES)
    refs = pd.concat([base[base["programme_id"].isin(sum((v[1] for v in OPTIONS.values()), []))], pd.read_csv(REFS)])
    refs["side"] = "reference"
    refs = refs.drop_duplicates(["programme_id", "title", "section", "page"])   # exact repeats only (FH Dortmund has two modules with one title)
    two_groups = refs.duplicated(["programme_id", "title"], keep="first") & refs["section"].fillna("").str.contains(ELECTIVE)
    refs = refs[~two_groups]
    emi = pd.read_csv(EMI_2026).drop_duplicates(["source_file", "title", "page"])     # shared II/MI modules counted once
    emi["side"] = "emi"
    d = pd.concat([refs, emi], ignore_index=True)
    d["clean"] = [clean(t if isinstance(t, str) else "", ti) for t, ti in zip(d["text"], d["title"])]
    d["category"] = [category(ti, c) for ti, c in zip(d["title"], d["clean"])]
    d.loc[d["title"].str.contains(EXTRA_FRAME), "category"] = "frame"
    d.loc[(d["side"] == "reference") & d["title"].str.contains(REF_FRAME), "category"] = "frame"
    d["security"] = d["category"] == "security"
    d["ot"] = (d["clean"].map(lambda c: len(OT.findall(c))) >= 3) | d["title"].str.contains(OT)
    d["ects_used"] = pd.to_numeric(d["ects"], errors="coerce").fillna(5.0)
    d["elective"] = (d["section"].fillna("").str.contains(ELECTIVE) | d["title"].str.contains(r"(?i)wahlpflicht")
                     | d["text"].fillna("").str[:600].str.contains(ELECTIVE_TYPE))
    text = d["title"].fillna("") + " " + d["clean"]
    for cap, pat in NEEDS.items():
        d[f"needs_{cap}"] = text.str.contains(pat)
    return d


def calibrate(d: pd.DataFrame, s: np.ndarray) -> tuple[float, float, float, float, int, int]:
    """Step 41 procedure: per reference module with a topic, best score among same-topic EMI modules (positive) vs
    among other-topic EMI modules (negative); Youden's J."""
    tp = d["title"].map(topics)
    ps, ns = [], []
    for i in d.index[(d["side"] == "reference") & (d["category"] != "frame") & d["programme_id"].isin(CALIBRATION)]:
        if not tp[i]:
            continue
        cand = candidates(d, d.at[i, "level"])
        same = [j for j in cand if tp[j] and tp[i] & tp[j]]
        other = [j for j in cand if tp[j] and not tp[i] & tp[j]]
        if same:
            ps.append(s[i, same].max())
        if other:
            ns.append(s[i, other].max())
    return (*youden(np.array(ps), np.array(ns)), len(ps), len(ns))


def candidates(d: pd.DataFrame, level: str) -> np.ndarray:
    m = (d["side"] == "emi") & (d["category"] != "frame")
    if level == "BA":
        m &= d["level"] == "BA"
    return d.index[m].to_numpy()


def assess(d: pd.DataFrame, s: np.ndarray, tau: float, rule: dict, s_tf: np.ndarray, tau_tf: float
           ) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, mods = [], []
    for option, (level, pids) in OPTIONS.items():
        unit = "bachelor" if level == "BA" else "master"
        taught = rule["unit"][unit]["taught_ects"]
        cand = candidates(d, level)
        for pid in pids:
            p = d[(d["programme_id"] == pid) & (d["category"] != "frame")]
            best = {i: cand[int(np.argmax(s[i, cand]))] for i in p.index}
            p = p.assign(score=[float(s[i, best[i]]) for i in p.index], match=[d.at[best[i], "title"] for i in p.index],
                         match_programme=[d.at[best[i], "programme_id"] for i in p.index])
            p["covered"] = p["score"] >= tau
            core = p[~p["elective"]]
            p["tfidf_covered"] = [float(s_tf[i, cand].max()) >= tau_tf for i in p.index]
            top3 = {i: cand[np.argsort(-s[i, cand])[:3]] for i in p.index}
            p["top3"] = ["; ".join(f"{d.at[j, 'title'][:45]} ({d.at[j, 'programme_id'].replace('oth26_', '')}, {s[i, j]:.3f})" for j in top3[i])
                         for i in p.index]
            tot = p["ects_used"].sum()
            cov = p.loc[p["covered"], "ects_used"].sum() / tot
            new_ects = (1 - cov) * taught
            by_prog = p[p["covered"]].groupby("match_programme")["ects_used"].sum() / tot
            lab_need = {cap: core.loc[core[f"needs_{cap}"], "ects_used"].sum() / tot for cap in NEEDS}
            sec = p[p["security"]]
            f2_max = rule["rule"]["F2_max_T_ects"][unit] + rule["rule"]["F2_max_N_ects"][unit]
            rows.append({
                "option": option, "reference": pid, "taught ECTS listed": tot,
                "F1 covered %": round(100 * cov, 1), "F1 pass (>= 80 %)": cov >= rule["rule"]["F1_min_covered_share"],
                "core covered % (electives left out)": round(100 * core.loc[core["covered"], "ects_used"].sum()
                                                             / max(core["ects_used"].sum(), 1), 1),
                "cross-check TF-IDF covered %": round(100 * p.loc[p["tfidf_covered"], "ects_used"].sum() / tot, 1),
                f"new ECTS at OTH size ({taught})": round(new_ects, 1),
                f"F2 pass (new <= {f2_max} ECTS and <= 20 %)": new_ects <= f2_max and (1 - cov) <= rule["rule"]["F2_max_new_share"],
                "F3 core ECTS needing a missing lab %": round(100 * sum(lab_need.values()), 1),
                "F3 pass": sum(lab_need.values()) == 0,
                "F4 largest share from one OTH programme %": round(100 * (by_prog.max() if len(by_prog) else 0), 1),
                "F4 programme": by_prog.idxmax() if len(by_prog) else "-",
                "F4 pass (<= 50 %)": (by_prog.max() if len(by_prog) else 0) <= rule["rule"]["F4_max_share_from_one_programme"],
                "security ECTS % of reference": round(100 * sec["ects_used"].sum() / tot, 1),
                "security covered %": round(100 * sec.loc[sec["covered"], "ects_used"].sum() / max(sec["ects_used"].sum(), 1), 1),
                "sensitivity: F1 >= 70 %": cov >= rule["sensitivity"]["F1_min_covered_share"],
            })
            mods.append(p.assign(option=option)[["option", "programme_id", "title", "section", "ects_used", "category", "elective",
                                                 *[f"needs_{c}" for c in NEEDS], "score", "covered", "match",
                                                 "match_programme", "tfidf_covered", "top3"]])
    return pd.DataFrame(rows), pd.concat(mods)


def reduced_variants(d: pd.DataFrame) -> pd.DataFrame:
    """What EMI could offer from existing modules alone: security and OT supply."""
    emi = d[(d["side"] == "emi") & (d["category"] != "frame")].copy()
    emi["key"] = emi["title"].str.replace(r"^\[[^\]]*\]\s*", "", regex=True).str.lower().str.strip()
    emi = emi.drop_duplicates("key")                     # a module shared by several handbooks counts once
    ba, all_ = emi[emi["level"] == "BA"], emi
    by_prog = lambda m: "; ".join(f"{k} {v:g}" for k, v in m.groupby("programme_id")["ects_used"].sum().sort_values(ascending=False).items())
    sec_ba = ba[ba["security"]]
    ot_sec = all_[all_["security"] | all_["ot"]]
    return pd.DataFrame([
        {"variant": "reduced cyber bachelor", "existing EMI modules": "security modules at bachelor level",
         "modules": len(sec_ba), "ECTS": sec_ba["ects_used"].sum(), "by programme": by_prog(sec_ba),
         "titles": "; ".join(sec_ba["title"].str.replace(r"^\[[^\]]*\]\s*", "", regex=True))},
        {"variant": "reduced OT-security master", "existing EMI modules": "security or OT modules, bachelor and master",
         "modules": len(ot_sec), "ECTS": ot_sec["ects_used"].sum(), "by programme": by_prog(ot_sec),
         "titles": "; ".join(ot_sec["title"].str.replace(r"^\[[^\]]*\]\s*", "", regex=True))},
    ])


def robotics_paths(mods: pd.DataFrame, rule: dict) -> pd.DataFrame:
    """F1-F4 after the hand check (configs/feasibility_handcheck.yaml) for the two Kempten paths. Core modules plus one
    specialisation; electives are left out (they are all E1 or dropped, so they could only raise coverage)."""
    hc = yaml.safe_load(HANDCHECK.read_text(encoding="utf-8"))["robotics_bsc"]
    auto = mods[mods["programme_id"] == "hske_ba_rob"].set_index("title")
    lim_t, lim_n = rule["rule"]["F2_max_T_ects"]["bachelor"], rule["rule"]["F2_max_N_ects"]["bachelor"]
    rows = []
    for path in ("A", "B"):
        sel = {k: v for k, v in hc["modules"].items() if not v.get("elective") and v.get("path", path) == path}
        ects = {k: float(auto.at[k, "ects_used"]) for k in sel}
        tot = sum(ects.values())
        by = lambda verdict: sum(e for k, e in ects.items() if sel[k]["verdict"] == verdict)
        e12, tn, nn = by("E1") + by("E2"), by("T"), by("N")
        prog = {}
        for k, v in sel.items():
            if v["verdict"] in ("E1", "E2"):
                pr = auto.at[k, "match_programme"].replace("oth26_ba_iki", "oth26_ba_ki")   # KI and KI International = one family
                prog[pr] = prog.get(pr, 0) + ects[k]
        top = max(prog, key=prog.get)
        missing_lab = [k for k, v in sel.items() if str(v.get("lab", "")).startswith("missing")]
        rows.append({"path": {"A": "A: Industrielle Robotik", "B": "B: Geriatronik (assistive / service)"}[path],
                     "taught ECTS (core + specialisation)": tot,
                     "F1 E1+E2 %": round(100 * e12 / tot, 1), "F1 pass": e12 / tot >= rule["rule"]["F1_min_covered_share"],
                     "E1 only %": round(100 * by("E1") / tot, 1), "T ECTS": tn, "N ECTS": nn, "F2 pass": tn <= lim_t and nn <= lim_n and (tn + nn) / tot <= rule["rule"]["F2_max_new_share"],
                     "modules needing a missing lab": "; ".join(missing_lab) or "-", "F3 pass": not missing_lab,
                     "F4 largest share %": round(100 * prog[top] / tot, 1), "F4 programme": top.replace("oth26_", ""),
                     "F4 pass": prog[top] / tot <= rule["rule"]["F4_max_share_from_one_programme"],
                     "status": hc["status"]})
    return pd.DataFrame(rows)


HANDCHECKED = {"autonomous_bsc": "Autonomous mobile systems B.Eng.", "arvr_bsc": "AR/VR & visual computing B.Sc.",
               "energydata_bsc": "Energy data management B.Sc.", "geodata_bsc": "Geo-data & geovisualisation B.Sc."}
FAMILY = {"oth26_ba_iki": "oth26_ba_ki"}   # KI and KI International = one family (as for robotics)


def candidates_handchecked(d: pd.DataFrame, mods: pd.DataFrame, rule: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """F1-F4 after the hand check for the equal-evidence candidates (configs/feasibility_handcheck.yaml), on the
    reference's core modules (electives left out, as for robotics). Electives: the ECTS a student must still choose
    (total minus core and frame modules) against the electives the automatic match covers."""
    hc = yaml.safe_load(HANDCHECK.read_text(encoding="utf-8"))
    lim_t, lim_n = rule["rule"]["F2_max_T_ects"]["bachelor"], rule["rule"]["F2_max_N_ects"]["bachelor"]
    total = rule["unit"]["bachelor"]["total_ects"]
    rows, details = [], []
    for key, option in HANDCHECKED.items():
        c = hc[key]
        pid = c["programme_id"]
        auto = mods[mods["programme_id"] == pid]
        seen: dict[str, int] = {}
        recs = []
        for r in auto.itertuples():
            seen[r.title] = seen.get(r.title, 0) + 1
            k = r.title if seen[r.title] == 1 else f"{r.title} #{seen[r.title]}"
            v = c["modules"].get(k)
            if v is None or v.get("elective") or r.elective or v.get("path", c.get("path")) != c.get("path"):
                continue   # electives, and modules of another specialisation (e.g. Deggendorf EM when the candidate is FR)
            recs.append({"option": option, "module": k, "ects": float(v.get("ects", r.ects_used)), "verdict": v["verdict"],
                         "prog": FAMILY.get(v.get("prog", ""), v.get("prog", "")), "emi": v.get("emi", ""),
                         "lab": str(v.get("lab", "")), "automatic": "covered" if r.covered else "not covered",
                         "tfidf": "covered" if r.tfidf_covered else "not covered", "note": v.get("note", "")})
        t = pd.DataFrame(recs)
        tot = t["ects"].sum()
        by = lambda verdicts: t.loc[t["verdict"].isin(verdicts), "ects"].sum()
        e12, tn, nn = by(["E1", "E2"]), by(["T"]), by(["N"])
        prog = t[t["verdict"].isin(["E1", "E2"])].groupby("prog")["ects"].sum()
        missing_lab = t.loc[t["lab"].str.startswith("missing"), "module"].tolist()
        frame = d.loc[(d["programme_id"] == pid) & (d["category"] == "frame"), "ects_used"].sum()
        el = auto[auto["elective"]]
        need = max(total - tot - frame, 0)
        rows.append({"candidate": option, "reference": pid, "core taught ECTS": tot,
                     "F1 E1+E2 %": round(100 * e12 / tot, 1), "F1 pass": e12 / tot >= rule["rule"]["F1_min_covered_share"],
                     "E1 only %": round(100 * by(["E1"]) / tot, 1), "T ECTS": tn, "N ECTS": nn,
                     "F2 pass": tn <= lim_t and nn <= lim_n and (tn + nn) / tot <= rule["rule"]["F2_max_new_share"],
                     "modules needing a missing lab": "; ".join(missing_lab) or "-", "F3 pass": not missing_lab,
                     "F4 largest share %": round(100 * prog.max() / tot, 1), "F4 programme": prog.idxmax().replace("oth26_", ""),
                     "F4 pass": prog.max() / tot <= rule["rule"]["F4_max_share_from_one_programme"],
                     "electives to choose (ECTS)": need,
                     "electives covered (automatic, ECTS)": el.loc[el["covered"], "ects_used"].sum(),
                     "sensitivity: F1 >= 70 % and N <= 20": e12 / tot >= rule["sensitivity"]["F1_min_covered_share"]
                     and tn <= lim_t and nn <= rule["sensitivity"]["F2_max_N_ects"]["bachelor"] and not missing_lab
                     and prog.max() / tot <= rule["rule"]["F4_max_share_from_one_programme"],
                     "status": c["status"]})
        details.append(t)
    return pd.DataFrame(rows), pd.concat(details, ignore_index=True)


def ot_master(rule: dict) -> pd.DataFrame:
    """The reduced OT-security master as a design from existing master modules (configs/feasibility_handcheck.yaml):
    F1 = 100 % by construction; F4 strict (shared modules count for IA) and lenient (shared modules count elsewhere)."""
    c = yaml.safe_load(HANDCHECK.read_text(encoding="utf-8"))["ot_master"]
    m = pd.DataFrame([{"module": k, **v} for k, v in c["modules"].items()])
    tot = m["ects"].sum()
    strict = m.assign(home=m["owners"].map(lambda o: "oth26_ma_ia" if "oth26_ma_ia" in o else o[0]))
    lenient = m.assign(home=m["owners"].map(lambda o: next((x for x in o if x != "oth26_ma_ia"), o[0])))
    share = lambda x: x.groupby("home")["ects"].sum().sort_values(ascending=False) / tot
    s, l = share(strict), share(lenient)
    lim = rule["rule"]["F4_max_share_from_one_programme"]
    return pd.DataFrame([{"candidate": "Reduced OT-security master", "taught ECTS": tot,
                          "security ECTS": m.loc[m["part"] == "security", "ects"].sum(),
                          "OT ECTS": m.loc[m["part"] == "ot", "ects"].sum(),
                          "project ECTS": m.loc[m["part"] == "project", "ects"].sum(),
                          "F1 %": 100.0, "F2 new ECTS": 0, "F3": "no lab beyond IA's (automation, networks)",
                          "F4 strict %": round(100 * s.iloc[0], 1), "F4 strict programme": s.index[0].replace("oth26_", ""),
                          "F4 lenient %": round(100 * l.iloc[0], 1), "F4 lenient programme": l.index[0].replace("oth26_", ""),
                          "F4 pass (strict)": s.iloc[0] <= lim, "F4 pass (lenient)": l.iloc[0] <= lim,
                          "status": c["status"]}])


def _md(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    fmt = lambda v: ("yes" if v else "no") if isinstance(v, (bool, np.bool_)) else str(v).replace("|", "/")
    return "\n".join(["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
                     + ["| " + " | ".join(fmt(v) for v in r) + " |" for r in df.itertuples(index=False)])


def main() -> None:
    rule = yaml.safe_load(RULE.read_text(encoding="utf-8"))
    d = load()
    emb = centre(embed(d["clean"].tolist()), d["source_file"])
    s = emb @ emb.T
    tau, tpr, fpr, auc, npos, nneg = calibrate(d, s)
    tf = tfidf_matrix(d["clean"].tolist(), fit_on=((d["side"] == "emi") | d["programme_id"].isin(CALIBRATION)).tolist())
    s_tf = (tf @ tf.T).toarray()
    tau_tf = calibrate(d, s_tf)[0]
    res, mods = assess(d, s, tau, rule, s_tf, tau_tf)
    gaps = mods[(mods["programme_id"] == "hske_ba_rob") & ~mods["covered"]][["title", "ects_used", "elective", "score", "top3"]]
    paths = robotics_paths(mods, rule)
    red = reduced_variants(d)
    cand, cand_mods = candidates_handchecked(d, mods, rule)
    otm = ot_master(rule)
    cand_mods.to_csv(OUT.with_name("feasibility_handcheck_candidates.csv"), index=False)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    mods.to_csv(OUT, index=False)
    # decided gates (Soma's verdicts, configs/handcheck_sheet.yaml): computed AFTER the interim CSVs are written,
    # because the verdict tables read them; reuses the code that writes the gate table in docs/evidence_tie_break.md
    from study_program_intelligence.report import handcheck_sheet as H
    decided = H.all_gates(*H.config())
    draft = OTH_DRAFT
    draft_rows = pd.DataFrame([{"curriculum": "OTH draft cyber bachelor (Step 45)", "taught ECTS": draft["taught"],
                                "reused or adapted EMI modules": draft["reused_or_adapted"],
                                "F1 covered %": round(100 * draft["reused_or_adapted"] / draft["taught"], 1),
                                "new ECTS by NEW staff": draft["new_by_new_staff"], "teaching assignments": draft["teaching_assignments"],
                                "verdict": "fails F1 (below 80 %), F2 (new content needs new professorships) and F3 (new security lab)"}])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# Feasibility with existing resources: the current options (generated)", "",
        f"Rule: configs/feasibility.yaml (pre-registered). e5 threshold recalibrated on this module set (Step 41 procedure): "
        f"{tau:.3f} (TPR {tpr:.2f}, FPR {fpr:.2f}, AUC {auc:.3f}; {npos} positive / {nneg} negative reference modules); "
        f"Step 41 threshold 0.295.", "",
        "## The OTH draft curriculum (cyber bachelor)", "", _md(draft_rows), "",
        "## Reference curricula against the current EMI modules", "", _md(res), "",
        f"TF-IDF cross-check threshold (same procedure): {tau_tf:.3f}.", "",
        "## Robotics: modules the automatic match leaves uncovered (for the hand check)", "", _md(gaps), "",
        "## Robotics: proposed week-2 verdicts by path (configs/feasibility_handcheck.yaml; "
        "path B superseded by Soma's decisions, see the decided gates below)", "", _md(paths), "",
        "## Reduced variants: what EMI's existing modules could carry (shared modules counted once)", "", _md(red), "",
        "## Equal-evidence candidates: proposed verdicts (configs/feasibility_handcheck.yaml; "
        "AR/VR superseded by Soma's decisions, see the decided gates below)", "", _md(cand), "",
        "## Reduced OT-security master: design from existing master modules", "", _md(otm), "",
        "Matches are automatic (e5). For a shortlisted candidate every match counted as covered is confirmed by hand.", "",
        "## Decided gates after Soma's hand check (configs/handcheck_sheet.yaml; strict rule = the decision)", "",
        _md(decided), "",
        "These rows match the gate table in docs/evidence_tie_break.md (written by report/handcheck_sheet.py). "
        "ot_master's lenient row uses the most favourable attribution of shared modules (58.3 % from the KI master); "
        "it fails F4 under either attribution.", ""]),
        encoding="utf-8")
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(f"threshold {tau:.3f} (AUC {auc:.3f}, {npos}/{nneg})")
    print(res.to_string(index=False)); print(); print(red.drop(columns=["titles"]).to_string(index=False))
    print(); print(paths.to_string(index=False))
    print(); print(cand.to_string(index=False)); print(); print(otm.to_string(index=False))
    print(f"\nWritten: {OUT.relative_to(REPO_ROOT)}, {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
