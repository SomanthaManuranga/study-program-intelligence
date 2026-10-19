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
cyber master = TH Ingolstadt, TH Deggendorf, HDBW; robotics bachelor = Hochschule Kempten Robotik.
F2 is checked on the uncovered share scaled to OTH's taught ECTS (bachelor 165, master 60). F3: modules whose practical
part needs a capability no EMI lab has (configs/emi_labs.yaml "missing"). F4: covered ECTS attributed to the OTH
programme of each best match; the largest share must not exceed 50 %.
The matches are automatic; every match counted as covered for a SHORTLISTED candidate is confirmed by hand later.
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
}
EXTRA_FRAME = re.compile(r"^RO\s?(5[12]\d?|8\d+)\b|praktische tätigkeit|duale praxis", re.I)   # Kempten practical/dual items
ELECTIVE = re.compile(r"wahl|elective|schwerpunkt|vertiefung", re.I)
NEEDS = {  # capability -> pattern in a module's title or text
    "security_lab": re.compile(r"penetration|pentest|forensi|incident response|security operations|\bsoc\b|hacking|cyber ?range|"
                               r"red team|blue team|malware.?analy", re.I),
    "industrial_robots": re.compile(r"industrieroboter|industrial robot|kollaborative robot|collaborative robot|cobot|roboterzelle|"
                                    r"robot(er)?zelle|robot cell", re.I),
}
OTH_DRAFT = {"taught": 165, "reused_or_adapted": 110, "new_by_new_staff": 45, "teaching_assignments": 10}   # docs/evidence_benchmarks.md


def load() -> pd.DataFrame:
    base = pd.read_csv(BASE_MODULES)
    refs = pd.concat([base[base["programme_id"].isin(sum((v[1] for v in OPTIONS.values()), []))], pd.read_csv(REFS)])
    refs["side"] = "reference"
    emi = pd.read_csv(EMI_2026).drop_duplicates(["source_file", "title", "page"])     # shared II/MI modules counted once
    emi["side"] = "emi"
    d = pd.concat([refs, emi], ignore_index=True)
    d["clean"] = [clean(t if isinstance(t, str) else "", ti) for t, ti in zip(d["text"], d["title"])]
    d["category"] = [category(ti, c) for ti, c in zip(d["title"], d["clean"])]
    d.loc[d["title"].str.contains(EXTRA_FRAME), "category"] = "frame"
    d["security"] = d["category"] == "security"
    d["ot"] = (d["clean"].map(lambda c: len(OT.findall(c))) >= 3) | d["title"].str.contains(OT)
    d["ects_used"] = pd.to_numeric(d["ects"], errors="coerce").fillna(5.0)
    d["elective"] = d["section"].fillna("").str.contains(ELECTIVE) | d["title"].str.contains(r"(?i)wahlpflicht")
    text = d["title"].fillna("") + " " + d["clean"]
    for cap, pat in NEEDS.items():
        d[f"needs_{cap}"] = text.str.contains(pat)
    return d


def calibrate(d: pd.DataFrame, s: np.ndarray) -> tuple[float, float, float, float, int, int]:
    """Step 41 procedure: per reference module with a topic, best score among same-topic EMI modules (positive) vs
    among other-topic EMI modules (negative); Youden's J."""
    tp = d["title"].map(topics)
    ps, ns = [], []
    for i in d.index[(d["side"] == "reference") & (d["category"] != "frame")]:
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
            p["tfidf_covered"] = [float(s_tf[i, cand].max()) >= tau_tf for i in p.index]
            top3 = {i: cand[np.argsort(-s[i, cand])[:3]] for i in p.index}
            p["top3"] = ["; ".join(f"{d.at[j, 'title'][:45]} ({d.at[j, 'programme_id'].replace('oth26_', '')}, {s[i, j]:.3f})" for j in top3[i])
                         for i in p.index]
            tot = p["ects_used"].sum()
            cov = p.loc[p["covered"], "ects_used"].sum() / tot
            new_ects = (1 - cov) * taught
            by_prog = p[p["covered"]].groupby("match_programme")["ects_used"].sum() / tot
            core = p[~p["elective"]]
            lab_need = {cap: core.loc[core[f"needs_{cap}"], "ects_used"].sum() / tot for cap in NEEDS}
            sec = p[p["security"]]
            f2_max = rule["rule"]["F2_max_T_ects"][unit] + rule["rule"]["F2_max_N_ects"][unit]
            rows.append({
                "option": option, "reference": pid, "taught ECTS listed": tot,
                "F1 covered %": round(100 * cov, 1), "F1 pass (>= 80 %)": cov >= rule["rule"]["F1_min_covered_share"],
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
                                                 "needs_security_lab", "needs_industrial_robots", "score", "covered", "match",
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
                     "T ECTS": tn, "N ECTS": nn, "F2 pass": tn <= lim_t and nn <= lim_n and (tn + nn) / tot <= rule["rule"]["F2_max_new_share"],
                     "modules needing a missing lab": "; ".join(missing_lab) or "-", "F3 pass": not missing_lab,
                     "F4 largest share %": round(100 * prog[top] / tot, 1), "F4 programme": top.replace("oth26_", ""),
                     "F4 pass": prog[top] / tot <= rule["rule"]["F4_max_share_from_one_programme"],
                     "status": hc["status"]})
    return pd.DataFrame(rows)


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
    tf = tfidf_matrix(d["clean"].tolist())
    s_tf = (tf @ tf.T).toarray()
    tau_tf = calibrate(d, s_tf)[0]
    res, mods = assess(d, s, tau, rule, s_tf, tau_tf)
    gaps = mods[(mods["programme_id"] == "hske_ba_rob") & ~mods["covered"]][["title", "ects_used", "elective", "score", "top3"]]
    paths = robotics_paths(mods, rule)
    red = reduced_variants(d)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    mods.to_csv(OUT, index=False)
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
        "## Robotics after the hand check (configs/feasibility_handcheck.yaml)", "", _md(paths), "",
        "## Reduced variants: what EMI's existing modules could carry (shared modules counted once)", "", _md(red), "",
        "Matches are automatic (e5). For a shortlisted candidate every match counted as covered is confirmed by hand.", ""]),
        encoding="utf-8")
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(f"threshold {tau:.3f} (AUC {auc:.3f}, {npos}/{nneg})")
    print(res.to_string(index=False)); print(); print(red.drop(columns=["titles"]).to_string(index=False))
    print(); print(paths.to_string(index=False))
    print(f"\nWritten: {OUT.relative_to(REPO_ROOT)}, {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
