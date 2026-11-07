"""Funnel step 7: can EMI teach it with what it has? Automatic F1-F4 down the ranked list (configs/funnel.yaml, shortlist).

Run from the repository root, after the reference curricula are in data/interim/funnel_refs/:

    python -m study_program_intelligence.analysis.funnel_gate

The rule is configs/feasibility.yaml, unchanged. A reference module counts as covered if its best EMI match reaches the
calibrated e5 threshold of analysis/feasibility.py (embeddings centred per handbook, as there). Everything uncovered is
new teaching, scaled to OTH's taught ECTS. Labs (F3) and every match counted as covered are decided in the hand check.
The result is the list for Soma's hand check, with one row per module.
Outputs: data/interim/funnel_gate.csv, funnel_gate_modules.csv; reports/funnel/step7_gate.md.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from .funnel_discovery import _md
from .module_gaps import embed as embed_chunks

REPO_ROOT = Path(__file__).resolve().parents[3]
INTERIM = REPO_ROOT / "data" / "interim"
REFS = INTERIM / "funnel_refs"
RULE = REPO_ROOT / "configs" / "feasibility.yaml"
FUNNEL = REPO_ROOT / "configs" / "funnel.yaml"
REPORT = REPO_ROOT / "reports" / "funnel" / "step7_gate.md"
FAMILY = {"ba_iki": "KI family", "ba_ki": "KI family", "ma_mki": "KI family"}   # one programme family for F4, as in the hand check


def threshold() -> float:
    return float(re.search(r"recalibrated on this module set \(Step 41 procedure\): (\d\.\d+)", (REPO_ROOT / "reports" / "feasibility.md").read_text(encoding="utf-8")).group(1))


def centred(v: np.ndarray) -> np.ndarray:
    c = v - v.mean(axis=0)
    return c / np.maximum(np.linalg.norm(c, axis=1, keepdims=True), 1e-9)


def emi_modules() -> tuple[pd.DataFrame, np.ndarray]:
    m = pd.read_csv(INTERIM / "modules_emi_2026.csv", low_memory=False)
    v = embed_chunks((m["title"].fillna("") + " " + m["text"].fillna("")).tolist())
    e = np.zeros_like(v)
    for pid, idx in m.groupby("programme_id").indices.items():
        e[idx] = centred(v[idx])
    return m, e


def assess(key: tuple[int, str], ref: pd.DataFrame, emi: pd.DataFrame, e: np.ndarray, tau: float, rule: dict, caps: dict) -> tuple[dict, pd.DataFrame]:
    typ, level = key
    ref = ref.copy()
    ref["ects"] = pd.to_numeric(ref["ects"], errors="coerce").fillna(5.0)
    ref = ref[ref["kind"].isin(["taught", "elective"])].reset_index(drop=True)
    v = centred(embed_chunks((ref["module"].fillna("") + " " + ref["content"].fillna("")).tolist()))
    use = emi["level"].eq("BA").values if level == "bachelor" else np.ones(len(emi), dtype=bool)
    sim = v @ e[use].T
    best = sim.argmax(axis=1)
    sub = emi[use].reset_index(drop=True)
    ref["best EMI module"] = sub["title"].iloc[best].values
    ref["EMI programme"] = sub["programme_id"].iloc[best].str.replace("oth26_", "").values
    ref["similarity"] = np.round(sim.max(axis=1), 3)
    ref["covered"] = ref["similarity"] >= tau
    core = ref[ref["kind"] == "taught"]
    taught = float(core["ects"].sum())
    unit = rule["unit"]["bachelor" if level == "bachelor" else "master"]["taught_ects"]
    covered = float(core.loc[core["covered"], "ects"].sum())
    f1 = covered / taught if taught else float("nan")
    new_scaled = (taught - covered) * unit / taught if taught else float("nan")
    fam = core[core["covered"]].assign(f=lambda d: d["EMI programme"].map(lambda p: FAMILY.get(p, p))).groupby("f")["ects"].sum()
    f4 = float(fam.max() / taught) if len(fam) and taught else 0.0
    t_cap = rule["rule"]["F2_max_T_ects"]["bachelor" if level == "bachelor" else "master"]
    out = {"type": typ, "level": level, "taught ECTS": taught, "F1 %": round(100 * f1, 1), "new ECTS scaled": round(new_scaled, 1),
           "new share %": round(100 * new_scaled / unit, 1), "F4 %": round(100 * f4, 1), "F4 programme": fam.idxmax() if len(fam) else "-",
           "F1 pass": f1 >= rule["rule"]["F1_min_covered_share"], "F4 pass": f4 <= rule["rule"]["F4_max_share_from_one_programme"]}
    for n in caps["bachelor" if level == "bachelor" else "master"]:
        out[f"F2 pass, N cap {n}"] = bool(new_scaled <= t_cap + n and new_scaled / unit <= rule["rule"]["F2_max_new_share"])
    default = caps["bachelor" if level == "bachelor" else "master"][0]
    out["automatic pass"] = bool(out["F1 pass"] and out["F4 pass"] and out[f"F2 pass, N cap {default}"])
    return out, ref.assign(type=typ, level=level)


def main() -> None:
    rule = yaml.safe_load(RULE.read_text(encoding="utf-8"))
    cfg = yaml.safe_load(FUNNEL.read_text(encoding="utf-8"))
    caps = cfg["feasibility_gate"]["caps_for_N_ects"]
    tau = threshold()
    emi, e = emi_modules()
    gl = pd.read_csv(INTERIM / "funnel_gate_list.csv")
    sources = []
    for f in REFS.glob("sources_*.yaml"):
        sources += yaml.safe_load(f.read_text(encoding="utf-8")) or []
    src = {(s["type"], s["level"]): s for s in sources}
    rows, mods = [], []
    for r in gl.itertuples():
        f = REFS / f"{r.type}_{r.level}.csv"
        s = src.get((r.type, r.level), {})
        base = {"rank": r.rank, "programme": s.get("programme"), "institution": s.get("institution"), "central titles": gl.loc[r.Index, "central titles"]}
        if not f.exists():
            rows.append({**base, "type": r.type, "level": r.level, "automatic pass": False, "problem": "no reference curriculum: manual download"})
            continue
        out, m = assess((r.type, r.level), pd.read_csv(f), emi, e, tau, rule, caps)
        rows.append({**base, **out, "problem": s.get("note", "")})
        mods.append(m)
    t = pd.DataFrame(rows).sort_values("rank")
    t.to_csv(INTERIM / "funnel_gate.csv", index=False)
    if mods:
        pd.concat(mods).to_csv(INTERIM / "funnel_gate_modules.csv", index=False)
    REPORT.write_text("\n".join(["# Funnel step 7: automatic gate (generated)", "", f"e5 threshold {tau}. Scaled to {rule['unit']['bachelor']['taught_ects']} / {rule['unit']['master']['taught_ects']} taught ECTS.", "",
                                 _md(t.drop(columns=["central titles"]))]) + "\n", encoding="utf-8")
    print(t[["rank", "type", "level", "programme", "F1 %", "new ECTS scaled", "F4 %", "F4 programme", "automatic pass"]].to_string())


if __name__ == "__main__":
    main()
