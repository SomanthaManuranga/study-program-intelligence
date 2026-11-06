"""Funnel step 2: programme types discovered from all offers, with no topic list (configs/funnel.yaml, discovery).

Run from the repository root:

    python -m study_program_intelligence.analysis.funnel_discovery embed
    python -m study_program_intelligence.analysis.funnel_discovery run

embed: builds the offer texts (title, focus items, subject labels; no notes, no degree words) and their e5 embeddings.
run: UMAP + HDBSCAN grid, bootstrap stability, selection by the pre-registered rule, rare path, assignment of other
forms, labels (c-TF-IDF), TF-IDF cross-check, and only then the recovery of the 18 old topic lists.
Outputs: data/interim/funnel_offers.csv, funnel_types.csv, funnel_grid.csv; reports/funnel/step2_types.md.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.cluster import HDBSCAN, AgglomerativeClustering, MiniBatchKMeans
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import adjusted_rand_score

from .funnel_subject_map import clean_label

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG = REPO_ROOT / "configs" / "funnel.yaml"
CATALOGUE = REPO_ROOT / "data" / "processed" / "programmes_full.csv"
FIELDS = REPO_ROOT / "data" / "processed" / "programme_fields_full.csv"
INTERIM = REPO_ROOT / "data" / "interim"
EMB = INTERIM / "funnel_embeddings.npy"
OFFERS = INTERIM / "funnel_offers.csv"
TYPES = INTERIM / "funnel_types.csv"
GRID = INTERIM / "funnel_grid.csv"
REPORT = REPO_ROOT / "reports" / "funnel" / "step2_types.md"
MODEL = "intfloat/multilingual-e5-base"

DEGREE_WORDS = re.compile(r"\b(Bachelor|Master)(\s+of\s+[A-Z][\w.-]*(\s+(in|and)\s+[A-Z][\w.-]*)?)?\b|\b(B|M)\.\s?(Sc|A|Eng|Ed|Mus|F\.?A|BA|LL\.?)\.?", re.I)
STOPWORDS = set("""und der die das des den dem für fur von mit im in an am auf zu zur zum sowie oder als bei nach aus ein eine einer
    of and the for in on with to studiengang studium bachelor master science arts engineering schwerpunkte grundständig
    weiterführend hochschule universität fachhochschule university""".split())


def config() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def focus_items(content) -> list[str]:
    if not isinstance(content, str) or "Schwerpunkte" not in content:
        return []
    t = content.split("Schwerpunkte: :", 1)[-1].split("Anmerkung der Hochschule", 1)[0]
    return [x.strip() for x in t.split(",") if len(x.strip()) > 2]


def clean_title(t: str) -> str:
    return re.sub(r"\s+", " ", DEGREE_WORDS.sub(" ", str(t))).strip(" -,;")


def offer_text(r) -> str:
    subj = [clean_label(s) for s in r.subjects.split("; ")] if isinstance(r.subjects, str) else []
    return ". ".join(x for x in [clean_title(r.title), ", ".join(focus_items(r.content)), ", ".join(subj)] if x)


def load_offers() -> pd.DataFrame:
    """Bachelor and master offers in Germany, one row per institution, title and degree (full-time preferred)."""
    d = pd.read_csv(CATALOGUE, low_memory=False, dtype={"programme_id": str})
    u = config()["universe"]["fit_on"]
    d = d[d["degree"].isin(u["degrees"]) & (d["country"] == u["country"])].copy()
    d["full_time"] = d["study_form"] == u["study_form"]
    d["distance_only"] = d["study_form"] == "Fernstudium"
    d = d.sort_values("full_time", ascending=False).drop_duplicates(["institution", "title", "degree"]).reset_index(drop=True)
    d["level"] = d["degree"].map({"Bachelor/Bakkalaureus": "bachelor", "Master": "master"})
    d["text"] = [offer_text(r) for r in d.itertuples()]
    d["has_focus"] = d["content"].map(lambda c: bool(focus_items(c)))
    return d


def embed() -> None:
    from sentence_transformers import SentenceTransformer
    d = load_offers()
    texts = d["text"].unique().tolist()
    model = SentenceTransformer(MODEL)
    v = model.encode([f"query: {t}" for t in texts], normalize_embeddings=True, batch_size=32, show_progress_bar=False)
    idx = {t: i for i, t in enumerate(texts)}
    np.save(EMB, v[[idx[t] for t in d["text"]]])
    d.drop(columns=["content"]).to_csv(OFFERS, index=False)
    print(f"{len(d)} offers ({d['full_time'].sum()} full-time), {len(texts)} distinct texts, focus items in {d['has_focus'].mean():.0%}. Written: {EMB}")


def fit_hdbscan(x: np.ndarray, mcs: int, method: str, ms: int) -> np.ndarray:
    return HDBSCAN(min_cluster_size=mcs, min_samples=ms, cluster_selection_method=method, copy=True).fit_predict(x)


def stability(ref: np.ndarray, coords: list[np.ndarray], mcs: int, method: str, ms: int, boot: dict) -> dict[int, float]:
    """Mean best-match Jaccard of each reference cluster over the refits (Hennig 2007); subsampled offers, other UMAP seeds."""
    rng = np.random.default_rng(boot["seed"])
    n, ids = len(ref), [c for c in np.unique(ref) if c >= 0]
    scores = {c: [] for c in ids}
    for i in range(boot["refits"]):
        take = rng.choice(n, int(boot["subsample"] * n), replace=False)
        lab = fit_hdbscan(coords[i % len(coords)][take], mcs, method, ms)
        members = {c: set(take[lab == c]) for c in np.unique(lab) if c >= 0}
        in_sample = set(take)
        for c in ids:
            a = set(np.where(ref == c)[0]) & in_sample
            if not a:
                continue
            scores[c].append(max((len(a & b) / len(a | b) for b in members.values()), default=0.0))
    return {c: float(np.mean(v)) if v else 0.0 for c, v in scores.items()}


def grid_search(x_coords: list[np.ndarray], cfg: dict) -> tuple[pd.DataFrame, dict]:
    g, boot, stable = cfg["hdbscan_grid"], cfg["bootstrap"], cfg["stable_jaccard"]
    rows, runs = [], {}
    n = len(x_coords[0])
    for mcs in g["min_cluster_size"]:
        for method in g["method"]:
            ref = fit_hdbscan(x_coords[0], mcs, method, g["min_samples"])
            st = stability(ref, x_coords, mcs, method, g["min_samples"], boot)
            good = [c for c, s in st.items() if s >= stable]
            sizes = pd.Series(ref[ref >= 0]).value_counts()
            rows.append({"min_cluster_size": mcs, "method": method, "clusters": len(st), "stable clusters": len(good),
                         "share in stable": round(float(np.isin(ref, good).mean()), 4), "noise": round(float((ref < 0).mean()), 4),
                         "largest cluster share": round(float(sizes.max() / n), 4) if len(sizes) else 0.0})
            runs[(mcs, method)] = (ref, st)
            print(rows[-1], flush=True)
    return pd.DataFrame(rows), runs


def select(grid: pd.DataFrame) -> pd.Series:
    ok = grid[(grid["noise"] <= 0.50) & (grid["largest cluster share"] <= 0.10) & (grid["stable clusters"] > 0)]
    if ok.empty:
        raise SystemExit("no setting meets the pre-registered limits: stop and report")
    return ok.sort_values(["share in stable", "stable clusters"], ascending=False).iloc[0]


def rare_path(emb: np.ndarray, d: pd.DataFrame, noise: np.ndarray, cutoff: float, max_size: int) -> np.ndarray:
    """Groups of offers among the noise, with at least two institutions (scope 8)."""
    out = np.full(len(d), -1)
    idx = np.where(noise)[0]
    if len(idx) < 2:
        return out
    lab = AgglomerativeClustering(n_clusters=None, metric="cosine", linkage="average", distance_threshold=cutoff).fit_predict(emb[idx])
    next_id = 0
    for c in np.unique(lab):
        m = idx[lab == c]
        if 2 <= len(m) <= max_size and d.iloc[m]["institution"].nunique() >= 2:
            out[m] = next_id
            next_id += 1
    return out


def within_cutoff(emb: np.ndarray, labels: np.ndarray, rng: np.random.Generator) -> float:
    vals = []
    for c in np.unique(labels[labels >= 0]):
        m = np.where(labels == c)[0]
        m = rng.choice(m, min(60, len(m)), replace=False)
        s = 1 - emb[m] @ emb[m].T
        vals.append(s[np.triu_indices(len(m), 1)])
    return float(np.median(np.concatenate(vals)))


def ctfidf_terms(texts: pd.Series, labels: np.ndarray, top: int = 8) -> dict[int, list[str]]:
    ids = [c for c in np.unique(labels) if c >= 0]
    docs = [" ".join(texts[labels == c]) for c in ids]
    cv = CountVectorizer(ngram_range=(1, 2), min_df=2, lowercase=True, stop_words=list(STOPWORDS), token_pattern=r"(?u)\b[^\W\d_][\w-]{2,}\b")
    m = cv.fit_transform(docs).astype(float).toarray()
    tf = m / np.maximum(m.sum(axis=1, keepdims=True), 1)
    idf = np.log(1 + m.sum(axis=1).mean() / np.maximum(m.sum(axis=0), 1))
    terms = np.array(cv.get_feature_names_out())
    return {c: terms[np.argsort(-(tf[i] * idf))[:top]].tolist() for i, c in enumerate(ids)}


def old_topic_recovery(d: pd.DataFrame, labels: np.ndarray) -> pd.DataFrame:
    """Used once, after the types are fixed: how many of the old hand-written lists does the data find on its own?"""
    from .themes import THEMES
    rows = []
    for name, pat in THEMES.items():
        a = set(np.where(d["title"].str.contains(pat, case=False, regex=True, na=False))[0])
        best, best_c = 0.0, -1
        for c in np.unique(labels[labels >= 0]):
            b = set(np.where(labels == c)[0])
            j = len(a & b) / len(a | b) if a | b else 0.0
            if j > best:
                best, best_c = j, c
        rows.append({"old topic": name, "offers": len(a), "best Jaccard": round(best, 3), "type": int(best_c), "recovered": best >= 0.5})
    return pd.DataFrame(rows)


def _md(df: pd.DataFrame) -> str:
    return "\n".join(["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
                     + ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)])


def run() -> None:
    import umap
    cfg = config()["discovery"]
    d = pd.read_csv(OFFERS, low_memory=False, dtype={"programme_id": str})
    emb = np.load(EMB)
    fit = np.where(d["full_time"])[0]
    u = cfg["umap"]
    coords = [umap.UMAP(n_neighbors=u["n_neighbors"], n_components=u["n_components"], metric=u["metric"], min_dist=u["min_dist"],
                        random_state=s).fit_transform(emb[fit]) for s in u["seeds"]]
    print("umap done", flush=True)
    grid, runs = grid_search(coords, cfg)
    grid.to_csv(GRID, index=False)
    pick = select(grid)
    print("selected", pick.to_dict(), flush=True)
    ref, st = runs[(int(pick["min_cluster_size"]), pick["method"])]
    good = {c for c, s in st.items() if s >= cfg["stable_jaccard"]}
    lab = np.full(len(d), -1)
    remap = {c: i for i, c in enumerate(sorted(good))}
    for pos, r in zip(fit, ref):
        if r in remap:
            lab[pos] = remap[r]
    n_stable = len(remap)
    rng = np.random.default_rng(cfg["bootstrap"]["seed"])
    cut = within_cutoff(emb, lab, rng)
    noise = (lab < 0) & d["full_time"].values
    rare = rare_path(emb, d, noise, cut, int(pick["min_cluster_size"]) - 1)
    lab[rare >= 0] = rare[rare >= 0] + n_stable
    # types and their member distance
    ids = np.unique(lab[lab >= 0])
    cent = np.vstack([emb[lab == c].mean(axis=0) for c in ids])
    cent /= np.linalg.norm(cent, axis=1, keepdims=True)
    dist = 1 - emb @ cent.T
    pos = {c: i for i, c in enumerate(ids)}
    p90 = np.array([np.quantile(dist[lab == c, pos[c]], 0.9) for c in ids])
    med = np.array([np.median(dist[lab == c, pos[c]]) for c in ids])
    near = dist.argmin(axis=1)
    near_ok = dist[np.arange(len(d)), near] <= p90[near]
    d["type"] = lab
    d["member"] = lab >= 0
    d["assigned_type"] = np.where(lab >= 0, lab, np.where(near_ok, ids[near], -1))
    d["dist_to_type"] = np.round(dist[np.arange(len(d)), [pos[t] if t >= 0 else 0 for t in d["assigned_type"]]], 4)
    d["type_nearest_any"] = ids[near]
    d["dist_nearest_any"] = np.round(dist[np.arange(len(d)), near], 4)
    terms = ctfidf_terms(d["text"], lab)
    rows = []
    for c in ids:
        m = lab == c
        order = np.argsort(dist[:, pos[c]])
        central = [t for t in d["title"].iloc[order[:40]].map(clean_title).drop_duplicates().tolist() if t][:5]
        a = d[d["assigned_type"] == c]
        rows.append({"type": int(c), "kind": "stable" if c < n_stable else "rare", "label": ", ".join(terms[c][:4]), "terms": "; ".join(terms[c]),
                     "central titles": "; ".join(central), "members": int(m.sum()), "assigned offers": len(a),
                     "bachelor": int((a["level"] == "bachelor").sum()), "master": int((a["level"] == "master").sum()),
                     "stability": round(st[[k for k, v in remap.items() if v == c][0]], 3) if c < n_stable else np.nan,
                     "median distance": round(float(med[pos[c]]), 4), "p90 distance": round(float(p90[pos[c]]), 4),
                     "share with focus": round(float(d.loc[m, "has_focus"].mean()), 3),
                     "share HAW": round(float(d.loc[m, "institution_type"].str.startswith("Fachhochschule").mean()), 3)})
    types = pd.DataFrame(rows)
    # cross-checks
    tf = TfidfVectorizer(lowercase=True, stop_words=list(STOPWORDS), min_df=2, sublinear_tf=True).fit_transform(d["text"].iloc[fit])
    km = MiniBatchKMeans(n_clusters=max(n_stable, 2), random_state=42, n_init=3).fit_predict(tf)
    tf_best = []
    for c in ids:
        a = set(np.where(lab[fit] == c)[0])
        tf_best.append(max((len(a & set(np.where(km == k)[0])) / len(a | set(np.where(km == k)[0])) for k in np.unique(km)), default=0.0))
    types["tfidf best Jaccard"] = np.round(tf_best, 3)
    types["method-dependent"] = types["tfidf best Jaccard"] < 0.3
    f = pd.read_csv(FIELDS, dtype={"programme_id": str}).drop_duplicates("programme_id").set_index("programme_id")["field_key"]
    fk = d["programme_id"].map(f)
    both = (lab >= 0) & fk.notna().values
    ari = adjusted_rand_score(fk[both].astype(str), lab[both])
    rec = old_topic_recovery(d, lab)
    d.to_csv(OFFERS, index=False)
    types.to_csv(TYPES, index=False)
    mix = d[d["full_time"]].assign(in_type=lambda x: x["type"] >= 0).groupby("has_focus")["in_type"].mean().round(3).to_dict()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# Funnel step 2: programme types (generated)", "", f"Offers: {len(d)}, full-time used for fitting: {len(fit)}.",
        f"Selected: min_cluster_size {int(pick['min_cluster_size'])}, method {pick['method']}; stable types {n_stable}, rare types {len(ids) - n_stable}.",
        f"Offers in stable types {float(pick['share in stable']):.1%}, noise before the rare path {float(pick['noise']):.1%}.",
        f"Share of full-time offers in a type, by focus items present: {mix}. ARI against catalogue study fields: {ari:.3f}.", "",
        "## Grid", "", _md(grid), "", "## Recovery of the old 18 topic lists (unsealed after the types were fixed)", "", _md(rec), "",
        "## Types", "", _md(types.drop(columns=["terms"]))]) + "\n", encoding="utf-8")
    print(f"types {len(types)} (stable {n_stable}), ARI {ari:.3f}, recovered {int(rec['recovered'].sum())} of {len(rec)}. Written: {REPORT}", flush=True)


if __name__ == "__main__":
    {"embed": embed, "run": run}[sys.argv[1]]()
