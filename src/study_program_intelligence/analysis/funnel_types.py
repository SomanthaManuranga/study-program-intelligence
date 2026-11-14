"""Funnel step 2: programme types found from all offers, with no topic list (configs/funnel.yaml: universe, text,
similarity, discovery; criteria in docs/criteria_funnel_step2.md).

Run from the repository root, each command from committed code on a clean tree:

    python -m study_program_intelligence.analysis.funnel_types scan     # focus-item strings found in many offers
    (decide which of them name no subject matter, write and commit configs/funnel_boilerplate.yaml)
    python -m study_program_intelligence.analysis.funnel_types embed    # cleaned offer texts and their vectors
    python -m study_program_intelligence.analysis.funnel_types run      # grid, stability, types, checks

No type is judged, scored or dropped here, and nothing about OTH or EMI is used.
Outputs: data/interim/funnel2_scan.csv, funnel2_offers.csv, funnel2_embeddings.npy, funnel2_grid.csv,
funnel2_types.csv, funnel2_offer_types.csv, funnel2_centroids.npy, funnel2_step2.json;
reports/funnel2/step2_scan.md, step2_types.md, step2_sample.md.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from functools import lru_cache

import numpy as np
import pandas as pd
import yaml

from .funnel_common import INTERIM, REPO_ROOT, REPORTS, config, md_table, run_stamp, universe

BOILERPLATE = REPO_ROOT / "configs" / "funnel_boilerplate.yaml"
STOPLIST = REPO_ROOT / "configs" / "funnel_title_stoplist.yaml"
FIELDS = REPO_ROOT / "data" / "processed" / "programme_fields_full.csv"
SCAN = INTERIM / "funnel2_scan.csv"
OFFERS = INTERIM / "funnel2_offers.csv"
EMB = INTERIM / "funnel2_embeddings.npy"
GRID = INTERIM / "funnel2_grid.csv"
TYPES = INTERIM / "funnel2_types.csv"
OFFER_TYPES = INTERIM / "funnel2_offer_types.csv"
CENTROIDS = INTERIM / "funnel2_centroids.npy"
RESULT = INTERIM / "funnel2_step2.json"
MODEL = "intfloat/multilingual-e5-base"

NOTE = "Anmerkung der Hochschule"
FOCUS_MARK = re.compile(r"Schwerpunkte\s*:\s*:?")
OF_DEGREE = r"(?:Fine\s+Arts|Business\s+Administration|Public\s+(?:Health|Administration|Policy|Management)|[A-Z][\w.-]*)"
ABBREV = r"(?:B|M)\.\s?(?:Sc|A|Eng|Ed|Mus|F\.?A)\.?|L\.?L\.?\s?(?:B|M)\.?|E?MBA|M\.B\.A\.?|[BM]Sc"
DEGREE_WORDS = re.compile(rf"\b(?:Bachelor|Master)\s+of\s+{OF_DEGREE}|(?<![\w.])(?:{ABBREV})(?![\w])|[\w-]*(?:bachelor|master)[\w-]*", re.I)
LEVEL_MARKER = re.compile(r"\s*\((?:grundständig|weiterführend)[^)]*\)", re.I)   # also "(grundständig außer Staatsexamen)"
STOPWORDS = sorted(set("""und der die das des den dem für fur von mit im in an am auf zu zur zum sowie oder als bei nach aus ein eine einer
    of and the for on with to studiengang studium science arts engineering hochschule universität fachhochschule university""".split()))
NOISE_MAX, LARGEST_MAX = 0.50, 0.10      # discovery.selection
RECOVERED, METHOD_DEPENDENT = 0.5, 0.3   # discovery.validation.old_lists, discovery.crosscheck
SAMPLE_TYPES, SAMPLE_TITLES, SAMPLE_SEED = 30, 10, 42   # criterion G9


def normalise(s: str) -> str:
    """Rule text.normalise: lower case, umlauts and sharp s written out, spaces collapsed."""
    s = str(s).lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return re.sub(r"\s+", " ", s).strip()


@lru_cache(maxsize=1)
def dropped_phrases() -> tuple[str, ...]:
    """The phrases of the rule text.dropped, normalised (the first entry of the rule is a description around a quoted phrase)."""
    out = []
    for p in config()["text"]["dropped"]:
        m = re.match(r'^"(.*)" and everything after it$', p)
        out.append(normalise(m.group(1) if m else p))
    return tuple(out)


@lru_cache(maxsize=1)
def dropped_patterns() -> tuple[re.Pattern, ...]:
    """The same phrases as patterns that also match the text as written (umlauts, any case)."""
    alt = lambda p: re.escape(p).replace("ae", "(?:ae|ä)").replace("oe", "(?:oe|ö)").replace("ue", "(?:ue|ü)").replace("ss", "(?:ss|ß)")
    return tuple(re.compile(alt(p), re.I) for p in dropped_phrases())


def boilerplate() -> list[str]:
    if not BOILERPLATE.exists():
        raise SystemExit(f"{BOILERPLATE.relative_to(REPO_ROOT)} is missing: run the scan, write the list and commit it first")
    return [normalise(p) for p in yaml.safe_load(BOILERPLATE.read_text(encoding="utf-8"))["dropped"]]


def cut_note(text: str) -> str:
    """Everything from the university's note on is dropped. The catalogue cuts long contents, so the note's heading can
    itself be cut ("Anmerkung der Hoc…:"); such a tail is dropped too."""
    i = text.lower().find(NOTE.lower())
    if i >= 0:
        return text[:i]
    m = re.search(r"Anmerkung([^,]{0,20})$", text)
    if m and (" " + normalise(NOTE.split(" ", 1)[1])).startswith(re.sub(r"[…:.\s\xa0]+$", "", m.group(1).lower())):
        return text[:m.start()]
    return text


def split_items(text: str) -> list[str]:
    """Split at commas that are not inside brackets."""
    out, depth, cur = [], 0, []
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == "," and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


def focus_items(content, drop: tuple[str, ...] = ()) -> list[str]:
    """The Schwerpunkte items of an offer (rule text.fields). Text before the heading, the note and the phrases of
    text.dropped are left out; an item whose normalised form is in `drop` (the boilerplate list) is left out."""
    if not isinstance(content, str):
        return []
    m = FOCUS_MARK.search(content)
    if not m:
        return []
    t = cut_note(content[m.end():])
    for p in dropped_patterns():
        t = p.sub(" ", t)
    items = [re.sub(r"\s+", " ", x).strip(" …\xa0;:.-") for x in split_items(t)]
    return [x for x in items if len(x) >= 2 and normalise(x) not in drop]


def clean_title(title: str) -> str:
    """The title without degree words (rule text.fields). The catalogue writes "<name> <degree>"; where the name itself
    is a degree ("Master of Finance Master of Science"), only the last degree and the words Bachelor, Master, of go."""
    tidy = lambda x: re.sub(r"\s+", " ", re.sub(r"\(\s*[.,/;-]*\s*\)", " ", x)).strip(" -,;/")
    t = LEVEL_MARKER.sub(" ", str(title))
    out = tidy(DEGREE_WORDS.sub(" ", t))
    if out:
        return out
    last = list(DEGREE_WORDS.finditer(t))[-1]
    name = re.sub(rf"\b(?:bachelor|master|of)\b|(?<![\w.])(?:{ABBREV})(?![\w])", " ", t[:last.start()] + t[last.end():], flags=re.I)
    return tidy(name)


def clean_label(label: str) -> str:
    return LEVEL_MARKER.sub("", str(label)).strip()


def offer_parts(title, content, subjects, drop: tuple[str, ...] = ()) -> tuple[str, list[str], list[str]]:
    """Rule text.fields: the title without degree words, the focus items, the subject labels without the level marker."""
    labels = [clean_label(x) for x in subjects.split("; ")] if isinstance(subjects, str) else []
    return clean_title(title), focus_items(content, drop), labels


def offer_text(title: str, items: list[str], labels: list[str]) -> str:
    return ". ".join(x for x in [title, ", ".join(items), ", ".join(labels)] if x)


def unclean(texts, phrases) -> list[int]:
    """Rule text.check: positions of the texts that still contain one of the phrases after normalising. A level marker is
    also found in its longer forms ("(grundständig außer Staatsexamen)"): a phrase in brackets is looked for without
    its closing bracket."""
    phrases = [p[:-1] if p.startswith("(") and p.endswith(")") else p for p in phrases]
    return [i for i, t in enumerate(texts) if any(p in normalise(t) for p in phrases)]


# ---------------------------------------------------------------------------------------------------------- scan

def item_counts(d: pd.DataFrame) -> pd.DataFrame:
    """Number of offers in which each focus-item string occurs (normalised, each offer once), most frequent first."""
    c, example = Counter(), {}
    for content in d["content"]:
        seen = set()
        for x in focus_items(content):
            n = normalise(x)
            if n not in seen:
                seen.add(n)
                c[n] += 1
                example.setdefault(n, x)
    out = pd.DataFrame([{"item": k, "offers": v, "as written": example[k]} for k, v in c.items()])
    return out.sort_values(["offers", "item"], ascending=[False, True]).reset_index(drop=True)


def scan() -> None:
    stamp, cfg = run_stamp(), config()
    line = int(re.search(r"in (\d+) or more offers", cfg["text"]["boilerplate_scan"]).group(1))
    stress = min(cfg["stress_tests"]["list_changing_one_at_a_time"]["boilerplate_scan_from"])
    d = universe()
    counts = item_counts(d)
    listed = counts[counts["offers"] >= stress].copy()
    listed["line"] = np.where(listed["offers"] >= line, f"{line} or more", f"{stress} to {line - 1} (stress)")
    listed.to_csv(SCAN, index=False)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "step2_scan.md").write_text("\n".join([
        "# Funnel step 2: focus-item strings found in many offers (generated)", "",
        f"Code commit {stamp['commit']}, run on {stamp['date']}, tracked files clean: {stamp['clean']}. {len(d)} offers, "
        f"{int((d['content'].map(lambda c: len(focus_items(c))) > 0).sum())} with focus items, {len(counts)} distinct item strings; "
        f"{int((counts['offers'] >= line).sum())} occur in {line} or more offers, {int((counts['offers'] >= stress).sum())} in {stress} or more.", "",
        md_table(listed)]) + "\n", encoding="utf-8")
    print(f"{len(counts)} distinct items; {int((counts['offers'] >= line).sum())} in >= {line} offers, {len(listed)} in >= {stress}. Written: {SCAN.name}")


# --------------------------------------------------------------------------------------------------------- embed

SEP = " | "     # between the focus items in the column focus_text


def build_offers(drop: tuple[str, ...]) -> pd.DataFrame:
    d = universe()
    parts = [offer_parts(t, c, x, drop) for t, c, x in zip(d["title"], d["content"], d["subjects"])]
    d["clean_title"] = [p[0] for p in parts]
    d["focus_text"] = [SEP.join(p[1]) for p in parts]
    d["focus_items"] = [len(p[1]) for p in parts]
    d["has_focus"] = d["focus_items"] > 0
    d["boilerplate_items_dropped"] = [len(focus_items(c)) - len(p[1]) for c, p in zip(d["content"], parts)]
    d["text"] = [offer_text(*p) for p in parts]
    return d.drop(columns=["content"])


def check_clean(d: pd.DataFrame, drop: tuple[str, ...]) -> dict:
    """Rule text.check on the texts as they will be embedded: no phrase of text.dropped anywhere in a text, no focus item
    that is a boilerplate string, no empty text. A boilerplate string inside a longer item is content and is counted."""
    items = [[normalise(x) for x in t.split(SEP)] if isinstance(t, str) and t else [] for t in d["focus_text"]]
    return {"texts_with_a_dropped_phrase": len(unclean(d["text"], dropped_phrases())),
            "texts_with_a_boilerplate_item": sum(any(x in drop for x in it) for it in items),
            "empty_texts": int((d["text"].fillna("") == "").sum()),
            "longer_items_containing_a_boilerplate_string": sum(any(b in x for b in drop) for it in items for x in it)}


def embed() -> None:
    stamp = run_stamp()
    drop = tuple(boilerplate())
    d = build_offers(drop)
    chk = check_clean(d, drop)
    if chk["texts_with_a_dropped_phrase"] or chk["texts_with_a_boilerplate_item"] or chk["empty_texts"]:
        raise SystemExit(f"stop (rule text.check): {chk}")
    from sentence_transformers import SentenceTransformer
    texts = sorted(d["text"].unique(), key=len)
    model = SentenceTransformer(MODEL)
    too_long = sum(len(ids) > model.max_seq_length for ids in model.tokenizer([f"query: {t}" for t in texts])["input_ids"])
    v = model.encode([f"query: {t}" for t in texts], normalize_embeddings=True, batch_size=64, show_progress_bar=False)
    pos = {t: i for i, t in enumerate(texts)}
    np.save(EMB, v[[pos[t] for t in d["text"]]].astype(np.float32))
    d.to_csv(OFFERS, index=False)
    scan_t = pd.read_csv(SCAN)
    scan_t["decision"] = np.where(scan_t["item"].isin(drop), "dropped", "kept")
    (REPORTS / "step2_scan.md").write_text("\n".join([
        "# Funnel step 2: focus-item strings found in many offers, with the decision (generated)", "",
        f"Code commit {stamp['commit']}, run on {stamp['date']}. Dropped: the strings of configs/funnel_boilerplate.yaml (they name no subject matter).", "",
        md_table(scan_t)]) + "\n", encoding="utf-8")
    meta = {"stamp": stamp, "offers": len(d), "full_time": int(d["full_time"].sum()), "distinct_texts": len(texts),
            "with_focus_items": int(d["has_focus"].sum()), "without_focus_items": int((~d["has_focus"]).sum()),
            "full_time_without_focus_items": int((~d["has_focus"] & d["full_time"]).sum()),
            "texts_longer_than_the_encoder_reads": int(too_long), "boilerplate_strings": len(drop),
            "offers_with_a_boilerplate_item_dropped": int((d["boilerplate_items_dropped"] > 0).sum()),
            "offers_left_without_focus_items_by_the_boilerplate_list": int(((d["boilerplate_items_dropped"] > 0) & ~d["has_focus"]).sum()), "check": chk}
    (INTERIM / "funnel2_embed.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


# ----------------------------------------------------------------------------------------------------------- run

def fit_hdbscan(x: np.ndarray, mcs: int, method: str, ms: int) -> np.ndarray:
    from sklearn.cluster import HDBSCAN
    return HDBSCAN(min_cluster_size=mcs, min_samples=ms, cluster_selection_method=method, copy=True).fit_predict(x)


def best_jaccard(a: np.ndarray, b: np.ndarray) -> dict[int, float]:
    """For every group of a (labels >= 0): the highest Jaccard with any group of b. Both label arrays cover the same items."""
    ia, ib = np.unique(a[a >= 0]), np.unique(b[b >= 0])
    if not len(ia):
        return {}
    if not len(ib):
        return {int(c): 0.0 for c in ia}
    pa, pb = {c: i for i, c in enumerate(ia)}, {c: i for i, c in enumerate(ib)}
    both = (a >= 0) & (b >= 0)
    m = np.zeros((len(ia), len(ib)))
    np.add.at(m, ([pa[c] for c in a[both]], [pb[c] for c in b[both]]), 1)
    na = np.array([(a == c).sum() for c in ia])[:, None]
    nb = np.array([(b == c).sum() for c in ib])[None, :]
    j = m / (na + nb - m)
    return {int(c): float(j[pa[c]].max()) for c in ia}


def stability(ref: np.ndarray, coords: list[np.ndarray], mcs: int, method: str, ms: int, boot: dict) -> dict[int, float]:
    """Mean best-match Jaccard of each reference cluster over the refits (Hennig 2007): 80 % subsamples, the UMAP seeds in
    turn. A cluster is compared on the offers of the subsample only."""
    rng = np.random.default_rng(boot["seed"])
    n, ids = len(ref), [int(c) for c in np.unique(ref) if c >= 0]
    scores = {c: [] for c in ids}
    for i in range(boot["refits"]):
        take = rng.choice(n, int(boot["subsample"] * n), replace=False)
        lab = fit_hdbscan(coords[i % len(coords)][take], mcs, method, ms)
        for c, j in best_jaccard(ref[take], lab).items():
            scores[c].append(j)
    return {c: float(np.mean(v)) if v else 0.0 for c, v in scores.items()}


def grid_search(coords: list[np.ndarray], cfg: dict) -> tuple[pd.DataFrame, dict]:
    g, boot, stable = cfg["hdbscan_grid"], cfg["bootstrap"], cfg["stable_jaccard"]
    rows, runs, n = [], {}, len(coords[0])
    for mcs in g["min_cluster_size"]:
        for method in g["method"]:
            ref = fit_hdbscan(coords[0], mcs, method, g["min_samples"])
            st = stability(ref, coords, mcs, method, g["min_samples"], boot)
            good = [c for c, s in st.items() if s >= stable]
            sizes = pd.Series(ref[ref >= 0]).value_counts()
            rows.append({"min_cluster_size": mcs, "method": method, "clusters": len(st), "stable clusters": len(good),
                         "share in stable": round(float(np.isin(ref, good).mean()), 4), "noise": round(float((ref < 0).mean()), 4),
                         "largest cluster share": round(float(sizes.max() / n), 4) if len(sizes) else 0.0})
            runs[(mcs, method)] = (ref, st)
            print(rows[-1], flush=True)
    return pd.DataFrame(rows), runs


def select(grid: pd.DataFrame) -> pd.Series:
    """Rule discovery.selection: the highest share of offers in stable clusters among the settings with noise <= 0.50 and
    largest cluster <= 0.10 of the offers; a tie goes to more stable clusters. Noise and largest cluster are those of the
    clustering as fitted, before unstable clusters are treated as noise. Remaining ties: the first setting of the grid."""
    ok = grid[(grid["noise"] <= NOISE_MAX) & (grid["largest cluster share"] <= LARGEST_MAX) & (grid["stable clusters"] > 0)]
    if ok.empty:
        raise SystemExit("no setting meets the pre-registered limits: stop and report")
    return ok.sort_values(["share in stable", "stable clusters"], ascending=False, kind="stable").iloc[0]


def within_cutoff(emb: np.ndarray, labels: np.ndarray, rng: np.random.Generator) -> float:
    """Median pairwise cosine distance inside the stable types; at most 60 members per type, so that large types do not
    decide the value alone."""
    vals = []
    for c in np.unique(labels[labels >= 0]):
        m = np.where(labels == c)[0]
        m = rng.choice(m, min(60, len(m)), replace=False)
        s = 1 - emb[m] @ emb[m].T
        vals.append(s[np.triu_indices(len(m), 1)])
    return float(np.median(np.concatenate(vals)))


def rare_path(emb: np.ndarray, institution: np.ndarray, noise: np.ndarray, cutoff: float, max_size: int, min_inst: int) -> np.ndarray:
    """Groups among the offers left without a stable type: average linkage, cut at the distance cutoff, at least
    min_inst institutions, at most max_size offers (rule discovery.rare_path)."""
    from sklearn.cluster import AgglomerativeClustering
    out = np.full(len(emb), -1)
    idx = np.where(noise)[0]
    if len(idx) < 2:
        return out
    lab = AgglomerativeClustering(n_clusters=None, metric="cosine", linkage="average", distance_threshold=cutoff).fit_predict(emb[idx])
    next_id = 0
    for c in np.unique(lab):
        m = idx[lab == c]
        if 2 <= len(m) <= max_size and len(set(institution[m])) >= min_inst:
            out[m] = next_id
            next_id += 1
    return out


def radii(dist_own: dict[int, np.ndarray], stable: set[int], pct: float = 90) -> dict[int, float]:
    """Rules similarity.radius_90 and similarity.rare_types. dist_own: for each type, its fitted members' distances to its
    centroid. A rare type takes the larger of its largest member distance and the median radius of the stable types."""
    r = {c: float(np.percentile(v, pct)) for c, v in dist_own.items() if c in stable}
    med = float(np.median(list(r.values()))) if r else 0.0
    r.update({c: max(float(np.max(v)), med) for c, v in dist_own.items() if c not in stable})
    return r


def ctfidf_terms(texts: pd.Series, labels: np.ndarray, top: int = 8) -> dict[int, list[str]]:
    from sklearn.feature_extraction.text import CountVectorizer
    ids = [c for c in np.unique(labels) if c >= 0]
    docs = [" ".join(texts[labels == c]) for c in ids]
    cv = CountVectorizer(ngram_range=(1, 2), min_df=1, lowercase=True, stop_words=STOPWORDS, token_pattern=r"(?u)\b[^\W\d_][\w-]{2,}\b", dtype=np.float32)
    m = cv.fit_transform(docs).tocsr()
    df = np.asarray(m.sum(axis=0)).ravel()
    idf = np.log(1 + m.sum(axis=1).mean() / np.maximum(df, 1))
    terms = np.array(cv.get_feature_names_out())
    out = {}
    for i, c in enumerate(ids):
        row = m.getrow(i)
        score = row.data / max(row.sum(), 1) * idf[row.indices]
        out[int(c)] = terms[row.indices[np.argsort(-score)[:top]]].tolist()
    return out


def old_lists() -> dict[str, str]:
    from .theme_verdicts import SUBTHEMES
    from .themes import THEMES
    return {**THEMES, **SUBTHEMES}


def recovery(title: pd.Series, labels: np.ndarray, subset: np.ndarray) -> pd.DataFrame:
    """Rule discovery.validation.old_lists on the offers of `subset`: for each old list (title pattern) the type with the
    highest Jaccard. A list without any matching offer cannot be tested."""
    rows = []
    for name, pat in old_lists().items():
        hit = title.str.contains(pat, case=False, regex=True, na=False).to_numpy() & subset
        if not hit.any():
            rows.append({"old list": name, "offers": 0, "best Jaccard": np.nan, "type": -1, "recovered": "not testable: no offer matches", "share in any type": np.nan})
            continue
        j = best_jaccard(np.where(hit, 0, -1), np.where(subset, labels, -1))[0]
        inter = pd.Series(labels[hit & (labels >= 0)]).value_counts()
        sizes = pd.Series(labels[subset & (labels >= 0)]).value_counts()
        jac = (inter / (hit.sum() + sizes.reindex(inter.index) - inter)).sort_values(ascending=False, kind="stable")
        rows.append({"old list": name, "offers": int(hit.sum()), "best Jaccard": round(j, 3), "type": int(jac.index[0]) if len(jac) else -1,
                     "recovered": "yes" if j >= RECOVERED else "no", "share in any type": round(float((labels[hit] >= 0).mean()), 3)})
    return pd.DataFrame(rows)


def mix(d: pd.DataFrame, by: str) -> pd.DataFrame:
    f = d[d["full_time"]]
    g = f.groupby(by).agg(offers=("type", "size"), in_stable=("kind", lambda k: (k == "stable").mean()), in_rare=("kind", lambda k: (k == "rare").mean()),
                          no_type=("kind", lambda k: (k == "none").mean()), assigned_later=("assigned_only", "mean")).reset_index()
    for c in ("in_stable", "in_rare", "no_type", "assigned_later"):
        g[c] = g[c].round(3)
    return g.rename(columns={"in_stable": "in a stable type", "in_rare": "in a rare type", "no_type": "left without a type by the fit",
                             "assigned_later": "assigned afterwards"})


def sample_for_review(d: pd.DataFrame) -> str:
    """Criterion G9: 30 types and 10 member titles each, drawn with one generator (seed 42)."""
    rng = np.random.default_rng(SAMPLE_SEED)
    ids = np.sort(d.loc[d["type"] >= 0, "type"].unique())
    pick = np.sort(rng.choice(ids, min(SAMPLE_TYPES, len(ids)), replace=False))
    lines = ["# Funnel step 2: sample of types for the reader's check (generated)", "",
             f"{len(pick)} types drawn with numpy default_rng({SAMPLE_SEED}); for each, {SAMPLE_TITLES} member titles drawn with the same generator "
             "(all members if fewer). Question per type: are at least 8 of 10 titles (or 80 %) the same kind of programme?", ""]
    for c in pick:
        m = d[d["type"] == c]
        take = m.iloc[np.sort(rng.choice(len(m), min(SAMPLE_TITLES, len(m)), replace=False))]
        lines += [f"## Type {int(c)} ({m['kind'].iloc[0]}, {len(m)} members)", ""] + [f"- {t} ({i})" for t, i in zip(take["title"], take["institution"])] + [""]
    return "\n".join(lines) + "\n"


def run() -> None:
    import umap
    from sklearn.cluster import MiniBatchKMeans
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics import adjusted_rand_score
    stamp, rules = run_stamp(), config()
    cfg = rules["discovery"]
    d = pd.read_csv(OFFERS, low_memory=False, dtype={"programme_id": str})
    emb = np.load(EMB).astype(np.float64)
    fit = np.where(d["full_time"])[0]
    u = cfg["umap"]
    coords = [umap.UMAP(n_neighbors=u["n_neighbors"], n_components=u["n_components"], metric=u["metric"], min_dist=u["min_dist"],
                        random_state=s).fit_transform(emb[fit]) for s in u["seeds"]]
    print("umap done", flush=True)
    grid, runs = grid_search(coords, cfg)
    grid.to_csv(GRID, index=False)
    pick = select(grid)
    mcs = int(pick["min_cluster_size"])
    print("selected", pick.to_dict(), flush=True)
    ref, st = runs[(mcs, pick["method"])]
    good = sorted(c for c, s in st.items() if s >= cfg["stable_jaccard"])
    remap = {c: i for i, c in enumerate(good)}
    lab = np.full(len(d), -1)
    lab[fit] = [remap.get(int(r), -1) for r in ref]
    n_stable = len(remap)
    cut = within_cutoff(emb, lab, np.random.default_rng(cfg["bootstrap"]["seed"]))
    noise = (lab < 0) & d["full_time"].to_numpy()
    rare = rare_path(emb, d["institution"].to_numpy(), noise, cut, mcs - 1, cfg["rare_path"]["min_institutions"])
    lab[rare >= 0] = rare[rare >= 0] + n_stable
    ids = np.unique(lab[lab >= 0])
    cent = np.vstack([emb[lab == c].mean(axis=0) for c in ids])
    cent /= np.linalg.norm(cent, axis=1, keepdims=True)
    dist = 1 - emb @ cent.T                                   # type ids are 0..n-1, so the column is the type
    own = {int(c): dist[lab == c, c] for c in ids}
    stable_set = set(range(n_stable))
    r90, r75, r95 = radii(own, stable_set, 90), radii(own, stable_set, 75), radii(own, stable_set, 95)
    radius = np.array([r90[int(c)] for c in ids])
    near = dist.argmin(axis=1)
    near_d = dist[np.arange(len(d)), near]
    assigned = np.where(lab >= 0, lab, np.where(near_d <= radius[near], near, -1))
    d["type"] = lab
    d["kind"] = np.where(lab < 0, "none", np.where(lab < n_stable, "stable", "rare"))
    d["assigned_type"] = assigned
    d["assigned_only"] = (lab < 0) & (assigned >= 0)
    d["dist_to_assigned"] = np.where(assigned >= 0, np.round(dist[np.arange(len(d)), np.maximum(assigned, 0)], 4), np.nan)
    d["nearest_type"] = near
    d["dist_to_nearest"] = np.round(near_d, 4)
    terms = ctfidf_terms(d["text"], lab)
    # cross-check: TF-IDF k-means with the same number of groups as there are stable types, on the full-time offers
    tf = TfidfVectorizer(lowercase=True, stop_words=STOPWORDS, min_df=2, sublinear_tf=True).fit_transform(d["text"].iloc[fit])
    km = MiniBatchKMeans(n_clusters=max(n_stable, 2), random_state=42, n_init=3).fit_predict(tf)
    tf_best = best_jaccard(lab[fit], km)
    inv = {v: k for k, v in remap.items()}
    rows = []
    for c in ids:
        c = int(c)
        m, a = d[lab == c], d[assigned == c]
        order = np.argsort(dist[:, c])
        central = [t for t in d["title"].iloc[order[:40]].map(clean_title).drop_duplicates().tolist() if t][:5]
        inst = {lv: int(a.loc[a["level"] == lv, "institution"].nunique()) for lv in ("bachelor", "master")}
        rows.append({"type": c, "kind": "stable" if c < n_stable else "rare", "label": ", ".join(terms[c][:4]), "central titles": "; ".join(central),
                     "members": len(m), "member institutions": int(m["institution"].nunique()), "assigned offers": len(a),
                     "bachelor": int((a["level"] == "bachelor").sum()), "master": int((a["level"] == "master").sum()),
                     "bachelor institutions": inst["bachelor"], "master institutions": inst["master"],
                     "units": int(inst["bachelor"] >= 2) + int(inst["master"] >= 2),
                     "stability": round(st[inv[c]], 3) if c < n_stable else np.nan,
                     "median distance": round(float(np.median(own[c])), 4), "largest distance": round(float(np.max(own[c])), 4),
                     "radius_75": round(r75[c], 4), "radius_90": round(r90[c], 4), "radius_95": round(r95[c], 4),
                     "share with focus": round(float(m["has_focus"].mean()), 3),
                     "share HAW": round(float(m["institution_type"].str.startswith("Fachhochschule").mean()), 3),
                     "tfidf best Jaccard": round(tf_best[c], 3), "method-dependent": bool(tf_best[c] < METHOD_DEPENDENT),
                     "evidence flag": "" if c < n_stable else cfg["rare_path"]["evidence_flag"].split('"')[1], "terms": "; ".join(terms[c])})
    types = pd.DataFrame(rows)
    f = pd.read_csv(FIELDS, dtype={"programme_id": str}).drop_duplicates("programme_id").set_index("programme_id")["field_key"]
    fk = d["programme_id"].map(f)
    both = (lab >= 0) & fk.notna().to_numpy()
    ari = float(adjusted_rand_score(fk[both].astype(str), lab[both]))
    ft = d["full_time"].to_numpy()
    rec_fit = recovery(d["title"], lab, ft)
    rec_all = recovery(d["title"], assigned, np.ones(len(d), bool))
    rec = rec_fit.merge(rec_all, on="old list", suffixes=(" (fitted, full-time)", " (all assigned)"))
    d.to_csv(OFFER_TYPES, index=False)
    types.to_csv(TYPES, index=False)
    np.save(CENTROIDS, cent.astype(np.float32))
    stable_t, rare_t = types[types["kind"] == "stable"], types[types["kind"] == "rare"]
    res = {"stamp": stamp, "offers": len(d), "full_time": int(ft.sum()),
           "selected": {"min_cluster_size": mcs, "method": pick["method"], "clusters": int(pick["clusters"]), "stable_clusters": int(pick["stable clusters"]),
                        "share_in_stable": float(pick["share in stable"]), "noise": float(pick["noise"]), "largest_cluster_share": float(pick["largest cluster share"])},
           "settings_within_limits": int(((grid["noise"] <= NOISE_MAX) & (grid["largest cluster share"] <= LARGEST_MAX) & (grid["stable clusters"] > 0)).sum()),
           "stable_types": n_stable, "rare_types": int(len(ids) - n_stable), "rare_cutoff": round(cut, 4), "median_radius_90_stable": round(float(stable_t["radius_90"].median()), 4),
           "full_time_in_stable": int(((lab >= 0) & (lab < n_stable) & ft).sum()), "full_time_in_rare": int(((lab >= n_stable) & ft).sum()),
           "full_time_without_type": int(((lab < 0) & ft).sum()), "assigned_afterwards": int(d["assigned_only"].sum()),
           "assigned_afterwards_full_time": int((d["assigned_only"] & d["full_time"]).sum()), "offers_without_any_type": int((assigned < 0).sum()),
           "units": int(types["units"].sum()), "types_with_a_unit": int((types["units"] > 0).sum()),
           "largest_type_members": int(types["members"].max()), "median_stable_members": float(stable_t["members"].median()),
           "ari_study_fields": round(ari, 3), "offers_in_ari": int(both.sum()), "tfidf_k": int(max(n_stable, 2)),
           "method_dependent_stable": int(stable_t["method-dependent"].sum()), "method_dependent_rare": int(rare_t["method-dependent"].sum()),
           "old_lists": len(rec), "old_lists_recovered_fitted": int((rec_fit["recovered"] == "yes").sum()), "old_lists_recovered_assigned": int((rec_all["recovered"] == "yes").sum()),
           "old_lists_not_testable": int(rec_fit["recovered"].str.startswith("not testable").sum())}
    RESULT.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORTS.mkdir(parents=True, exist_ok=True)
    show = types.drop(columns=["terms", "radius_75", "radius_95", "largest distance", "evidence flag"])
    (REPORTS / "step2_types.md").write_text("\n".join([
        "# Funnel step 2: programme types (generated)", "",
        f"Code commit {stamp['commit']}, run on {stamp['date']}, tracked files clean: {stamp['clean']}.", "",
        f"- Offers: {len(d)}; full-time offers used for the fit: {int(ft.sum())}.",
        f"- Selected setting: min_cluster_size {mcs}, method {pick['method']} ({res['settings_within_limits']} of {len(grid)} settings are within the limits).",
        f"- Types: {n_stable} stable, {res['rare_types']} rare (flag: {cfg['rare_path']['evidence_flag']}).",
        f"- Full-time offers: {res['full_time_in_stable']} in a stable type, {res['full_time_in_rare']} in a rare type, {res['full_time_without_type']} left without a type by the fit.",
        f"- Assigned afterwards (inside the radius of the nearest type): {res['assigned_afterwards']} offers; without any type after that: {res['offers_without_any_type']}.",
        f"- Units (type x level with offers at 2 or more institutions): {res['units']}.",
        f"- Agreement with the catalogue's study fields (ARI, offers in a type): {ari:.3f}.",
        f"- TF-IDF cross-check (k-means, k = {res['tfidf_k']}): method-dependent {res['method_dependent_stable']} of {n_stable} stable types and {res['method_dependent_rare']} of {res['rare_types']} rare types.",
        f"- Old topic lists: {res['old_lists']} tested; recovered (Jaccard >= {RECOVERED}) {res['old_lists_recovered_fitted']} on the fitted full-time offers, "
        f"{res['old_lists_recovered_assigned']} on all assigned offers; not testable {res['old_lists_not_testable']}.", "",
        "## Grid", "", md_table(grid), "", "## Mix of the full-time offers, by focus items present", "", md_table(mix(d, "has_focus")), "",
        "## Mix of the full-time offers, by institution type", "", md_table(mix(d, "institution_type")), "",
        "## The old topic lists (counts only)", "", md_table(rec), "", "## Types", "", md_table(show)]) + "\n", encoding="utf-8")
    (REPORTS / "step2_sample.md").write_text(sample_for_review(d), encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    {"scan": scan, "embed": embed, "run": run}[sys.argv[1]]()
