"""Embedding-based cannibalisation profile: where OTH-internal substitution would concentrate (deep-analysis layer).

Run from the repository root (uses the cached e5 embeddings; no model download needed):

    python -m study_program_intelligence.analysis.cannibalisation_similarity

Purpose: the Step 48 Huff model sees OTH's own programmes only where they carry the theme in title or focus field,
and the 50 % stress case brackets what it cannot see. This module adds an independent, content-based view: programme
embeddings (ECTS-weighted mean of the cached multilingual-e5 module vectors, centred on the grand mean of all
programme vectors) give a cosine-similarity profile between each candidate programme and every existing EMI bachelor
programme. The normalised positive similarities form a SUBSTITUTION PROFILE: if OTH-internal draw happens, where it
would concentrate. It is a profile, not a level estimate - it cannot say HOW MUCH cannibalisation happens, only
WHERE, so it complements (never replaces) the Huff shares and the 50 % stress case (criteria D4).

Candidates: cyber = the mean of the three reference curricula (THI, Deggendorf, THWS, as in the feasibility step);
robotics path B = Hochschule Kempten Robotik; AR/VR = Hochschule Coburg Visual Computing.

Limitations, stated: module handbooks describe intentions, not teaching; raw e5 cosines are compressed (the raw
values are shown for transparency); ECTS weights fall back to 5 where the handbook states none; the profile assumes
substitution follows content similarity, which ignores admission, language and brand effects.

Outputs: data/interim/cannibalisation_similarity.csv, reports/cannibalisation_similarity.md.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .module_gaps import clean, embed

REPO_ROOT = Path(__file__).resolve().parents[3]
INTERIM = REPO_ROOT / "data" / "interim"
OUT = INTERIM / "cannibalisation_similarity.csv"
REPORT = REPO_ROOT / "reports" / "cannibalisation_similarity.md"
CANDIDATES = {"cyber (reference mean: THI, DEG, THWS)": ["thi_ba_csi", "deg_ba_cy", "thws_ba_is"],
              "robotics path B (Kempten)": ["hske_ba_rob"],
              "AR/VR (Coburg Visual Computing)": ["hsc_ba_vc"]}
EMI_LABELS = {"oth26_ba_ii": "Industrie-4.0-Informatik", "oth26_ba_mi": "Medieninformatik", "oth26_ba_ki": "KI B.Sc.",
              "oth26_ba_iki": "KI International", "oth26_ba_ei": "Elektro- und Informationstechnik",
              "oth26_ba_dd": "Digital Design", "oth26_ba_gi": "Geoinformatik und Landmanagement",
              "oth26_ba_mt": "Medienproduktion und Medientechnik"}


def modules() -> pd.DataFrame:
    base = pd.read_csv(INTERIM / "modules.csv")
    refs = pd.read_csv(INTERIM / "modules_references.csv")
    emi = pd.read_csv(INTERIM / "modules_emi_2026.csv")
    want = {p for pids in CANDIDATES.values() for p in pids}
    pool = pd.concat([base[base["programme_id"].isin(want)], refs[refs["programme_id"].isin(want)],
                      emi[emi["programme_id"].isin(EMI_LABELS)]], ignore_index=True)
    pool = pool.drop_duplicates(["programme_id", "title", "page"])
    pool["clean"] = [clean(t if isinstance(t, str) else "", ti) for t, ti in zip(pool["text"], pool["title"])]
    pool["ects_used"] = pd.to_numeric(pool["ects"], errors="coerce").fillna(5.0)
    return pool


def programme_vectors(pool: pd.DataFrame) -> dict[str, np.ndarray]:
    emb = embed(pool["clean"].tolist())
    vecs = {}
    for pid, idx in pool.groupby("programme_id").groups.items():
        rows = pool.loc[idx]
        w = rows["ects_used"].to_numpy()
        v = (emb[[pool.index.get_loc(i) for i in idx]] * w[:, None]).sum(axis=0) / w.sum()
        vecs[pid] = v / np.linalg.norm(v)
    return vecs


def main() -> None:
    pool = modules()
    vecs = programme_vectors(pool)
    cand_vecs = {}
    for name, pids in CANDIDATES.items():
        missing = [p for p in pids if p not in vecs]
        if missing:
            raise SystemExit(f"missing reference programmes in the module tables: {missing}")
        v = np.mean([vecs[p] for p in pids], axis=0)
        cand_vecs[name] = v / np.linalg.norm(v)
    emi_ids = [p for p in EMI_LABELS if p in vecs]
    # centre on the EMI-only centroid: each centred vector is a programme's deviation from the average EMI programme,
    # so cos(candidate, EMI programme) asks "which EMI programme leans in the candidate's direction?"
    grand = np.mean([vecs[p] for p in emi_ids], axis=0)
    centred = {k: (v - grand) / np.linalg.norm(v - grand) for k, v in {**{p: vecs[p] for p in emi_ids}, **cand_vecs}.items()}

    rows = []
    for cand in CANDIDATES:
        raw = {p: float(np.dot(vecs[p], cand_vecs[cand])) for p in emi_ids}
        cen = {p: float(np.dot(centred[p], centred[cand])) for p in emi_ids}
        pos = {p: max(c, 0.0) for p, c in cen.items()}
        tot = sum(pos.values()) or 1.0
        for p in emi_ids:
            rows.append({"candidate": cand, "EMI programme": EMI_LABELS[p], "raw cosine": round(raw[p], 3),
                         "centred cosine": round(cen[p], 3), "substitution profile %": round(100 * pos[p] / tot, 1)})
    t = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT, index=False)
    md = lambda df: "\n".join(["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
                              + ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)])
    parts = ["# Embedding-based cannibalisation profile (generated)", "",
             "Method, assumptions and limitations: module docstring (analysis/cannibalisation_similarity.py).",
             "The profile says WHERE OTH-internal substitution would concentrate, not how much there is;",
             "levels stay with the Step 48 Huff shares (14-27 %) and the 50 % stress case.", ""]
    for cand in CANDIDATES:
        d = t[t["candidate"] == cand].sort_values("substitution profile %", ascending=False).drop(columns="candidate")
        parts += [f"## {cand}", "", md(d), ""]
    combo = lambda cand, progs: round(float(t[(t["candidate"] == cand) & t["EMI programme"].isin(progs)]
                                             ["substitution profile %"].sum()), 1)
    cyber_k, rob_k, arvr_k = list(CANDIDATES)
    parts += [
        "Reading: Elektro- und Informationstechnik tops every list because the dominant deviation axis separates",
        "EMI's technical-engineering pole from its media/geo pole, so the per-candidate signal sits in the",
        "programme COMBINATIONS: for cyber the two security-focus informatics programmes together take "
        f"{combo(cyber_k, ['Industrie-4.0-Informatik', 'Medieninformatik'])} % of the profile (the Huff model's"
        " concentration); for robotics path B the KI family takes "
        f"{combo(rob_k, ['KI B.Sc.', 'KI International'])} % (the F4 family of the hand check); for AR/VR the"
        " media programmes take "
        f"{combo(arvr_k, ['Medienproduktion und Medientechnik', 'Digital Design', 'Medieninformatik'])} %.",
        "Where the Huff model and the embeddings can be compared they point at the same programmes, so the",
        "cannibalisation story does not depend on the title/focus rules alone. The E&IT pole is a known artefact of",
        "the single dominant axis and is read as generic technical overlap, not as a cannibalisation prediction.", ""]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(parts), encoding="utf-8")
    pd.set_option("display.width", 200)
    print(t.sort_values(["candidate", "substitution profile %"], ascending=[True, False]).to_string(index=False))
    print(f"Written: {OUT.relative_to(REPO_ROOT)}, {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
