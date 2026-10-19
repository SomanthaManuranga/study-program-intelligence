"""Recombination candidates: coherent clusters of existing EMI modules (re-scope, week 2).

Run from the repository root (after transform.modules --set emi2026):

    python -m study_program_intelligence.analysis.recombination

Method (docs/rescope_plan.md (c)(i), fixed before running):
- EMI modules of the current handbooks (data/interim/modules_emi_2026.csv), frame modules left out (thesis, practical
  phase, placeholder electives), a module shared by several handbooks counted once (by title);
- the same e5 embeddings as Step 41 / the feasibility check, centred per handbook;
- agglomerative clustering (cosine distance, average linkage); the number of clusters chosen by the best silhouette
  between 8 and 30 (deterministic, no seed needed);
- a cluster is described by its module titles, its ECTS and the EMI programmes it draws on;
- a candidate PROFILE is a cluster, or two clusters whose centroids are each other's nearest neighbours, with at least
  60 specialist ECTS (bachelor) and drawing on at least two EMI programmes with at most 50 % of its ECTS from any one
  (rule F4 at module level). Cluster labels are proposed by Claude and reviewed by Soma.
Outputs: data/interim/recombination_clusters.csv, reports/recombination.md.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from study_program_intelligence.analysis.module_gaps import category, centre, clean, embed

REPO_ROOT = Path(__file__).resolve().parents[3]
EMI_2026 = REPO_ROOT / "data" / "interim" / "modules_emi_2026.csv"
OUT = REPO_ROOT / "data" / "interim" / "recombination_clusters.csv"
REPORT = REPO_ROOT / "reports" / "recombination.md"
K_RANGE = range(8, 31)
MIN_ECTS, MAX_SHARE, MIN_PROGRAMMES = 60, 0.50, 2
FAMILY = {"oth26_ba_iki": "oth26_ba_ki"}     # KI and KI International: one programme family for the source-share rule


def load() -> pd.DataFrame:
    d = pd.read_csv(EMI_2026)
    d["clean"] = [clean(t if isinstance(t, str) else "", ti) for t, ti in zip(d["text"], d["title"])]
    d["category"] = [category(ti, c) for ti, c in zip(d["title"], d["clean"])]
    d = d[d["category"] != "frame"].copy()
    d["key"] = d["title"].str.replace(r"^\[[^\]]*\]\s*", "", regex=True).str.lower().str.strip()
    d["family"] = d["programme_id"].replace(FAMILY)
    d["ects_used"] = pd.to_numeric(d["ects"], errors="coerce").fillna(5.0).clip(upper=10)   # 10+ = project blocks
    emb = centre(embed(d["clean"].tolist()), d["source_file"])
    d["row"] = range(len(d))
    keep = d.drop_duplicates("key")
    return keep.reset_index(drop=True), emb[keep["row"].to_numpy()]


def cluster(emb: np.ndarray) -> tuple[np.ndarray, int, pd.DataFrame]:
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.metrics import silhouette_score
    scores = []
    for k in K_RANGE:
        lab = AgglomerativeClustering(n_clusters=k, metric="cosine", linkage="average").fit_predict(emb)
        scores.append({"k": k, "silhouette": silhouette_score(emb, lab, metric="cosine")})
    sc = pd.DataFrame(scores)
    k = int(sc.loc[sc["silhouette"].idxmax(), "k"])
    return AgglomerativeClustering(n_clusters=k, metric="cosine", linkage="average").fit_predict(emb), k, sc


def describe(d: pd.DataFrame, emb: np.ndarray, labels: np.ndarray) -> pd.DataFrame:
    rows = []
    for c in sorted(set(labels)):
        g = d[labels == c]
        share = g.groupby("family")["ects_used"].sum() / g["ects_used"].sum()
        cen = emb[labels == c].mean(axis=0)
        near = g.iloc[np.argsort(-(emb[labels == c] @ cen))[:6]]
        rows.append({"cluster": int(c), "modules": len(g), "ECTS": g["ects_used"].sum(), "programmes": g["family"].nunique(),
                     "largest source": f"{share.idxmax().replace('oth26_', '')} {100 * share.max():.0f} %",
                     "largest share": share.max(), "security modules": int((g["category"] == "security").sum()),
                     "most central titles": "; ".join(re.sub(r"^\[[^\]]*\]\s*", "", t)[:40] for t in near["title"])})
    return pd.DataFrame(rows).sort_values("ECTS", ascending=False)


def profiles(d: pd.DataFrame, emb: np.ndarray, labels: np.ndarray, desc: pd.DataFrame) -> pd.DataFrame:
    cents = {c: emb[labels == c].mean(axis=0) for c in set(labels)}
    cents = {c: v / np.linalg.norm(v) for c, v in cents.items()}
    ids = sorted(cents)
    sim = np.array([[cents[a] @ cents[b] if a != b else -1 for b in ids] for a in ids])
    nn = {ids[i]: ids[int(np.argmax(sim[i]))] for i in range(len(ids))}
    cands = [(c,) for c in ids] + sorted({tuple(sorted((a, b))) for a, b in nn.items() if nn[b] == a})
    rows = []
    for cs in cands:
        g = d[np.isin(labels, cs)]
        ects = g["ects_used"].sum()
        share = g.groupby("family")["ects_used"].sum() / ects
        ok = ects >= MIN_ECTS and share.max() <= MAX_SHARE and g["family"].nunique() >= MIN_PROGRAMMES
        rows.append({"clusters": "+".join(str(c) for c in cs), "modules": len(g), "ECTS": ects, "programmes": g["family"].nunique(),
                     "largest source": f"{share.idxmax().replace('oth26_', '')} {100 * share.max():.0f} %",
                     "passes size and source rule": ok,
                     "titles": "; ".join(re.sub(r"^\[[^\]]*\]\s*", "", t)[:35] for t in g["title"])})
    return pd.DataFrame(rows).sort_values(["passes size and source rule", "ECTS"], ascending=False)


def _md(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    fmt = lambda v: ("yes" if v else "no") if isinstance(v, (bool, np.bool_)) else (f"{v:.3f}" if isinstance(v, float) and v < 1 else str(v))
    return "\n".join(["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
                     + ["| " + " | ".join(fmt(v).replace("|", "/") for v in r) + " |" for r in df.itertuples(index=False)])


def main() -> None:
    d, emb = load()
    labels, k, sc = cluster(emb)
    d["cluster"] = labels
    desc = describe(d, emb, labels)
    prof = profiles(d, emb, labels, desc)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    d[["programme_id", "level", "title", "ects_used", "category", "cluster"]].to_csv(OUT, index=False)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# Recombination: clusters of existing EMI modules (generated)", "",
        f"{len(d)} distinct EMI modules (frame modules left out). Number of clusters by silhouette (8-30): k = {k} "
        f"(silhouette {sc['silhouette'].max():.3f}).", "",
        "## Clusters", "", _md(desc.drop(columns=["largest share"])), "",
        f"## Candidate profiles (cluster or mutual-nearest pair; rule: >= {MIN_ECTS} ECTS, >= {MIN_PROGRAMMES} programmes, "
        f"<= {int(100 * MAX_SHARE)} % from one)", "", _md(prof), "",
        "## Silhouette by k", "", _md(sc), ""]), encoding="utf-8")
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 120)
    print(f"k = {k}"); print(desc.drop(columns=["largest share"]).to_string(index=False)); print()
    print(prof.drop(columns=["titles"]).to_string(index=False))
    print(f"\nWritten: {OUT.relative_to(REPO_ROOT)}, {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
