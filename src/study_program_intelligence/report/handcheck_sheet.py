"""Hand-check sheet for the adapted-module (E2) verdicts of the two candidates that pass the gate, and F1-F4 after
Soma's decisions.

Run from the repository root (after analysis.feasibility):

    python -m study_program_intelligence.report.handcheck_sheet

Inputs: configs/handcheck_sheet.yaml (EMI module behind each E2 verdict, Soma's decisions), configs/feasibility_handcheck.yaml,
configs/feasibility.yaml, data/interim/modules_references.csv, data/interim/modules_emi_2026.csv,
data/interim/feasibility_modules.csv (robotics), data/interim/feasibility_handcheck_candidates.csv (AR/VR).
A rejected E2 module becomes what `if_rejected` says (T or N) and no longer counts for F4. F3 is not changed by the
decisions (it depends on labs, not on the verdict).
Output: docs/handcheck_sheet.md (committed: it is the sheet Soma answers on).
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SHEET = REPO_ROOT / "configs" / "handcheck_sheet.yaml"
HANDCHECK = REPO_ROOT / "configs" / "feasibility_handcheck.yaml"
RULE = REPO_ROOT / "configs" / "feasibility.yaml"
INTERIM = REPO_ROOT / "data" / "interim"
OUT = REPO_ROOT / "docs" / "handcheck_sheet.md"
FAMILY = {"oth26_ba_iki": "oth26_ba_ki"}


def strip_code(title: str) -> str:
    return re.sub(r"^\[[^\]]*\]\s*", "", str(title)).strip()


PROF = re.compile(r"Prof\.?(?:\s*(?:Dr\.?|Dr\.-Ing\.|-Ing\.))*\s+[A-ZÄÖÜ][\w.-]*(?:\s+[A-ZÄÖÜ][\w-]+)?")


OUTCOMES = [re.compile(x) for x in (r"Lernziele:", r"Lernziele\s*/\s*Qualifikation", r"Qualifikationsziele", r"Lernergebnisse",
                                     r"Learning Outcomes")]   # in this order: Kempten's "Learning Outcomes, Contents" heading precedes its prerequisites


def short(text, n: int = 300) -> str:
    """First n characters of the content part (after the form fields), professors' names masked (project rule)."""
    from study_program_intelligence.transform.modules import content_excerpt
    t = re.sub(r"\s+", " ", str(text if isinstance(text, str) else "")).strip()
    m = next((x for x in (o.search(t) for o in OUTCOMES) if x), None)   # outcome headings first: "Inhalte" can sit in the prerequisites
    excerpt = t[m.start():m.start() + n] if m else content_excerpt(t, n)
    return PROF.sub("Prof. [name]", excerpt).replace("|", "/")


def config() -> tuple[dict, dict, dict]:
    load = lambda p: yaml.safe_load(p.read_text(encoding="utf-8"))
    return load(SHEET), load(HANDCHECK), load(RULE)


def sheet_rows(cfg: dict, hc: dict) -> pd.DataFrame:
    refs = pd.read_csv(INTERIM / "modules_references.csv")
    emi = pd.read_csv(INTERIM / "modules_emi_2026.csv")
    emi["plain"] = emi["title"].map(strip_code)
    rows = []
    for cand, c in cfg["candidates"].items():
        for mod, m in c["modules"].items():
            v = hc[c["hand_check"]]["modules"][mod]
            r = refs[(refs["programme_id"] == c["reference"]) & (refs["title"] == mod)].iloc[0]
            pid, title = m["emi"]
            e = emi[(emi["programme_id"] == pid) & (emi["plain"] == title)].iloc[0]
            rows.append({"candidate": cand, "candidate module": mod, "EMI module": f"{title} ({pid.replace('oth26_', '')})",
                         "ECTS (candidate / EMI)": f"{float(r['ects']) if pd.notna(r['ects']) else 5:g} / "
                                                   f"{float(e['ects']):g}" if pd.notna(e["ects"]) else "-",
                         "candidate text (first 300 characters of the content part)": short(r["text"]),
                         "EMI text (first 300 characters of the content part)": short(e["text"]),
                         "where": f"{Path(r['source_file']).name} p. {r['page']}; {Path(e['source_file']).name} p. {e['page']}",
                         "proposed verdict": f"E2: {v.get('emi', '')}" + (f" ({m['note']})" if m.get("note") else ""),
                         "if rejected": m["if_rejected"],
                         "decision": cfg.get("decisions", {}).get(f"{cand}|{mod}", "")})
    return pd.DataFrame(rows)


def verdict_table(cand: str, cfg: dict, hc: dict) -> pd.DataFrame:
    """module, ECTS, verdict, programme (for F4) of the candidate's core path, with Soma's decisions applied."""
    if cand == "robotics_b":
        auto = pd.read_csv(INTERIM / "feasibility_modules.csv")
        auto = auto[auto["programme_id"] == "hske_ba_rob"].set_index("title")
        mods = hc["robotics_bsc"]["modules"]
        t = pd.DataFrame([{"module": k, "ects": float(auto.at[k, "ects_used"]), "verdict": v["verdict"],
                           "prog": FAMILY.get(auto.at[k, "match_programme"], auto.at[k, "match_programme"])}
                          for k, v in mods.items() if not v.get("elective") and v.get("path", "B") == "B"])
    else:
        t = pd.read_csv(INTERIM / "feasibility_handcheck_candidates.csv")
        t = t[t["option"] == "AR/VR & visual computing B.Sc."].rename(columns={})[["module", "ects", "verdict", "prog"]].copy()
    for mod, m in cfg["candidates"][cand]["modules"].items():
        if cfg.get("decisions", {}).get(f"{cand}|{mod}") == "reject":
            t.loc[t["module"] == mod, ["verdict", "prog"]] = [m["if_rejected"], None]
    return t


def f1_f4(t: pd.DataFrame, rule: dict) -> dict:
    tot = t["ects"].sum()
    e12 = t.loc[t["verdict"].isin(["E1", "E2"]), "ects"].sum()
    tn, nn = t.loc[t["verdict"] == "T", "ects"].sum(), t.loc[t["verdict"] == "N", "ects"].sum()
    prog = t[t["verdict"].isin(["E1", "E2"])].groupby("prog")["ects"].sum()
    r = rule["rule"]
    return {"taught ECTS": tot, "F1 %": round(100 * e12 / tot, 1), "F1 pass": e12 / tot >= r["F1_min_covered_share"],
            "T": tn, "N": nn, "F2 pass": tn <= r["F2_max_T_ects"]["bachelor"] and nn <= r["F2_max_N_ects"]["bachelor"]
            and (tn + nn) / tot <= r["F2_max_new_share"],
            "F4 %": round(100 * prog.max() / tot, 1), "F4 programme": prog.idxmax().replace("oth26_", ""),
            "F4 pass": prog.max() / tot <= r["F4_max_share_from_one_programme"]}


def _md(df: pd.DataFrame) -> str:
    fmt = lambda v: ("yes" if v else "no") if isinstance(v, bool) else str(v)
    return "\n".join(["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
                     + ["| " + " | ".join(fmt(v) for v in r) + " |" for r in df.itertuples(index=False)])


def main() -> None:
    cfg, hc, rule = config()
    rows = sheet_rows(cfg, hc)
    decided = bool(cfg.get("decisions"))
    lines = ["# Hand check: adapted-module (E2) verdicts behind the two gate passes", "",
             "Generated by `python -m study_program_intelligence.report.handcheck_sheet` from `configs/handcheck_sheet.yaml`. "
             "Texts start at the module's contents or learning outcomes (the form fields before it are skipped); "
             "professors' names are masked. For each row: is the EMI module, adapted by at most a third, a fair stand-in for the candidate module? "
             "Write `confirm` or `reject` per row (or tell Claude); a rejected module becomes the type in \"if rejected\" "
             "(T = teaching assignment, N = new module by an existing professor).", ""]
    for cand, label in (("arvr", "AR/VR & visual computing B.Sc. (reference: Hochschule Coburg Visual Computing)"),
                        ("robotics_b", "Robotics + AI B.Sc., path B (reference: Hochschule Kempten Robotik, Geriatronik)")):
        r = rows[rows["candidate"] == cand].drop(columns=["candidate"])
        t = verdict_table(cand, {**cfg, "decisions": {}}, hc)
        now = f1_f4(t, rule)
        all_t = t.copy()
        for mod, m in cfg["candidates"][cand]["modules"].items():
            all_t.loc[all_t["module"] == mod, ["verdict", "prog"]] = [m["if_rejected"], None]
        worst = f1_f4(all_t, rule)
        lines += [f"## {label}", "", _md(r), "",
                  f"Now (all E2 confirmed): F1 {now['F1 %']} %, T {now['T']:g}, N {now['N']:g}, F4 {now['F4 %']} % "
                  f"({now['F4 programme']}). If every E2 is rejected: F1 {worst['F1 %']} %, T {worst['T']:g}, N {worst['N']:g}.", ""]
        if decided:
            lines += ["After Soma's decisions:", "", _md(pd.DataFrame([f1_f4(verdict_table(cand, cfg, hc), rule)])), ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Written: {OUT.relative_to(REPO_ROOT)} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
