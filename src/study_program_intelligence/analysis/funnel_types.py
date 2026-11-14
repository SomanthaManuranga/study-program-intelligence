"""Funnel step 2: programme types found from all offers, with no topic list (configs/funnel.yaml: universe, text,
similarity, discovery; criteria in docs/criteria_funnel_step2.md).

Run from the repository root, each command from committed code on a clean tree:

    python -m study_program_intelligence.analysis.funnel_types scan     # focus-item strings found in many offers
    (decide which of them name no subject matter, write and commit configs/funnel_boilerplate.yaml)
    python -m study_program_intelligence.analysis.funnel_types embed    # cleaned offer texts and their vectors
    python -m study_program_intelligence.analysis.funnel_types run      # grid, stability, types, checks

No type is judged, scored or dropped here, and nothing about OTH or EMI is used.
Outputs: data/interim/funnel2_scan.csv, funnel2_offers.csv, funnel2_embeddings.npy, funnel2_embed.json, funnel2_grid.csv,
funnel2_types.csv, funnel2_offer_types.csv, funnel2_centroids.npy, funnel2_step2.json (commit and file hashes of
all outputs); reports/funnel2/step2_scan.md, step2_scan_decisions.md, step2_types.md, step2_sample.md.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from functools import lru_cache

import numpy as np
import pandas as pd
import yaml

from .funnel_common import INTERIM, REPO_ROOT, REPORTS, config, md_table, run_stamp, universe

BOILERPLATE = REPO_ROOT / "configs" / "funnel_boilerplate.yaml"
FIELDS = REPO_ROOT / "data" / "processed" / "programme_fields_full.csv"
SCAN = INTERIM / "funnel2_scan.csv"
OFFERS = INTERIM / "funnel2_offers.csv"
EMB = INTERIM / "funnel2_embeddings.npy"
EMBED_META = INTERIM / "funnel2_embed.json"
GRID = INTERIM / "funnel2_grid.csv"
TYPES = INTERIM / "funnel2_types.csv"
OFFER_TYPES = INTERIM / "funnel2_offer_types.csv"
CENTROIDS = INTERIM / "funnel2_centroids.npy"
RESULT = INTERIM / "funnel2_step2.json"
MODEL = "intfloat/multilingual-e5-base"

NOTE = "Anmerkung der Hochschule"
FOCUS_MARK = "Schwerpunkte: :"
STANDARD_DEGREE = r"(?:Science|Arts|Engineering|Education|Laws|Music|Fine\s+Arts|Musical\s+Arts|Business\s+Administration)"
STANDARD = re.compile(rf"\b(?:Bachelor|Master)\s+of\s+{STANDARD_DEGREE}\b(?:\s+in\b)?", re.I)
ABBREVS = re.compile(r"(?<![\w.])(?:(?:B|M)\.\s?(?:Sc|A|Eng|Ed|Mus|F\.?A)\.?|L\.?L\.?\s?(?:B|M)\.?|E?MBA|M\.B\.A\.?|[BM]Sc)(?![\w])", re.I)
UPPER_ABBREVS = re.compile(r"(?<![\w.-])(?:BA|MA|BBA|LLM|LLB|MEng|BEng)(?![\w-])")     # as written only: "ma" and "ba" are no degrees
DEGREE_TOKEN = re.compile(r"[\w-]*(?:bachelor|master)[\w-]*(?:\s+(?:of|in)\b)?", re.I)
ORGANISATION_PARTS = {"ein", "zwei", "fach", "faecher", "hauptfaecher", "doppel", "doppelfach", "mono", "kombi", "q"}
DEGREE_BRACKET = re.compile(r"\((?:\s*(?:\x00|&|/|,|;|-|\.|und|and|eng\.?))*\s*\)", re.I)       # what is left of "(MBA & Eng.)" or "(B.A.)"
LEVEL_MARKER = re.compile(r"\s*\((?:grundständig|weiterführend)[^)]*\)", re.I)          # also "(grundständig außer Staatsexamen)"
STOPWORDS = sorted(set("""und der die das des den dem für fur von mit im in an am auf zu zur zum sowie oder als bei nach aus ein eine einer
    of and the for on with to studiengang studium hochschule universität fachhochschule university""".split()))
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
    """The same phrases as patterns that also match the text as written (umlauts, any case, any spacing)."""
    alt = lambda p: re.escape(p).replace("ae", "(?:ae|ä)").replace("oe", "(?:oe|ö)").replace("ue", "(?:ue|ü)").replace("ss", "(?:ss|ß)").replace(r"\ ", r"\s+")
    return tuple(re.compile(alt(p), re.I) for p in dropped_phrases())


def boilerplate() -> list[str]:
    """The strings of configs/funnel_boilerplate.yaml; the file must be committed and unchanged."""
    rel = BOILERPLATE.relative_to(REPO_ROOT).as_posix()
    git = lambda *a: subprocess.run(["git", *a], cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip()
    if not BOILERPLATE.exists() or not git("ls-files", rel) or git("status", "--porcelain", rel):
        raise SystemExit(f"{rel} is missing or not committed: run the scan, write the list and commit it first")
    return [normalise(p) for p in yaml.safe_load(BOILERPLATE.read_text(encoding="utf-8"))["dropped"]]


def cut_note(text: str) -> str:
    """Everything from the university's note on is dropped. The catalogue cuts long contents; a content that ends in
    "…:" was cut inside the note's heading ("Anmerkung der Hoc…:", "Anm…:"), and that piece of the heading goes too."""
    i = text.lower().find(NOTE.lower())
    if i >= 0:
        return text[:i]
    m = re.search(r"…\s*:\s*$", text)
    if not m:
        return text
    head = text[:m.start()].rstrip()
    low = head.lower()
    for k in range(len(NOTE), 0, -1):
        p = NOTE[:k].lower().rstrip()
        if low.endswith(p) and (len(low) == len(p) or low[-len(p) - 1].isspace()):
            return head[:len(head) - len(p)]
    return head


def split_items(text: str) -> list[str]:
    """Split at commas and semicolons that are not inside brackets."""
    out, depth, cur = [], 0, []
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch in ",;" and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


def focus_items(content, drop: tuple[str, ...] = ()) -> list[str]:
    """The Schwerpunkte items of an offer (rule text.fields). The note is cut first, so a "Schwerpunkte:" inside a note is
    no heading. Text before the heading and the phrases of text.dropped are left out; an item whose normalised form is
    in `drop` (the boilerplate list) is left out. A last item cut by the catalogue stays as it is."""
    if not isinstance(content, str):
        return []
    t = cut_note(content)
    i = t.find(FOCUS_MARK)
    if i < 0:
        return []
    t = t[i + len(FOCUS_MARK):]
    for p in dropped_patterns():
        t = p.sub(" ", t)
    items = [re.sub(r"\s+", " ", x).strip(" …\xa0").rstrip(" ;:.-").lstrip(" ;:-") for x in split_items(t)]
    return [x for x in items if re.search(r"\w", x) and normalise(x) not in drop]


MARK = "\x00"     # stands where a degree word was removed, until the title is tidied


def _degree_token(m: re.Match) -> str:
    """Of a token such as "Zwei-Fach-Bachelor" or "Arp-Schnitger-Master" only the parts that name no degree stay."""
    word = m.group(0).split()[0]
    keep = [p for p in word.split("-") if p and not re.search("bachelor|master", p, re.I) and normalise(p) not in ORGANISATION_PARTS and not p.isdigit()]
    return f" {'-'.join(keep)} {MARK} "


def _tidy(t: str) -> str:
    """Brackets emptied by the removal go. A piece that only repeats the start of an earlier piece goes too, but only
    across a removed degree word ("<name> Master of <name>"); a word repeated inside the name stays."""
    t = DEGREE_BRACKET.sub(" ", t)
    kept: list[str] = []
    for piece in t.split(MARK):
        piece = re.sub(r"\s+", " ", piece).strip()
        words = piece.lower().strip(" -,;/&:").split()
        if not words or any(k.lower().strip(" -,;/&:").split()[:len(words)] == words for k in kept):
            continue
        kept.append(piece)
    t = re.sub(r"\(\s+", "(", re.sub(r"\s+\)", ")", " ".join(kept)))
    t = re.sub(r"\(\s*\)", " ", t)
    t = re.sub(r"\s+", " ", t).strip(" -,;/&:")
    return re.sub(r"^(?:in|of)\s+|\s+(?:in|of)$", "", t, flags=re.I).strip(" -,;/&:")


def clean_title(title: str) -> str:
    """The title without degree words (rule text.fields). Standard degrees ("Master of Science", "B.A.", "MBA") go as a
    whole. Of any other "Master of <name>" only the words Master and of go, because the name is the subject
    ("Master of Landscape Architecture"). If nothing but a standard degree is there, its name is the title ("Laws")."""
    t = LEVEL_MARKER.sub(" ", str(title)).replace(MARK, " ")
    mark = f" {MARK} "
    strip = lambda x: _tidy(DEGREE_TOKEN.sub(_degree_token, UPPER_ABBREVS.sub(mark, ABBREVS.sub(mark, x))))
    out = strip(STANDARD.sub(mark, t))
    if re.search(r"[^\W\d_]{2}", re.sub(r"\([^)]*\)", " ", out)):
        return out
    return strip(t)


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


def sha(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


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
    (REPORTS / "step2_scan_decisions.md").write_text("\n".join([
        "# Funnel step 2: focus-item strings found in many offers, with the decision (generated)", "",
        f"Code commit {stamp['commit']}, run on {stamp['date']}. Scan: reports/funnel2/step2_scan.md. Dropped: the strings of "
        "configs/funnel_boilerplate.yaml (they name no subject matter), where they are a whole focus item.", "",
        md_table(scan_t)]) + "\n", encoding="utf-8")
    meta = {"stamp": stamp, "offers": len(d), "full_time": int(d["full_time"].sum()), "distinct_texts": len(texts),
            "with_focus_items": int(d["has_focus"].sum()), "without_focus_items": int((~d["has_focus"]).sum()),
            "full_time_without_focus_items": int((~d["has_focus"] & d["full_time"]).sum()),
            "texts_longer_than_the_encoder_reads": int(too_long), "boilerplate_strings": len(drop),
            "offers_with_a_boilerplate_item_dropped": int((d["boilerplate_items_dropped"] > 0).sum()),
            "offers_left_without_focus_items_by_the_boilerplate_list": int(((d["boilerplate_items_dropped"] > 0) & ~d["has_focus"]).sum()), "check": chk,
            "files": {OFFERS.name: sha(OFFERS), EMB.name: sha(EMB)}}
    EMBED_META.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
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
    """Mean best-match Jaccard of each reference cluster over the refits (Hennig 2007). Each refit clusters an 80 %
    subsample of the offers again, on the UMAP coordinates of the seeds in turn; a cluster is compared on the offers of
    the subsample only. UMAP itself is fitted once per seed on all offers, not on the subsample."""
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
                         "share in stable": float(np.isin(ref, good).mean()), "noise": float((ref < 0).mean()),
                         "largest cluster share": float(sizes.max() / n) if len(sizes) else 0.0})
            runs[(mcs, method)] = (ref, st)
            print({k: round(v, 4) if isinstance(v, float) else v for k, v in rows[-1].items()}, flush=True)
    return pd.DataFrame(rows), runs


def select(grid: pd.DataFrame) -> pd.Series:
    """Rule discovery.selection: the highest share of offers in stable clusters among the settings with noise <= 0.50 and
    largest cluster <= 0.10 of the offers; a tie goes to more stable clusters. Noise and largest cluster are those of the
    clustering as fitted, before unstable clusters are treated as noise. Remaining ties: the first setting of the grid."""
    ok = grid[(grid["noise"] <= NOISE_MAX) & (grid["largest cluster share"] <= LARGEST_MAX) & (grid["stable clusters"] > 0)]
    if ok.empty:
        raise SystemExit("no setting meets the pre-registered limits: stop and report")
    return ok.sort_values(["share in stable", "stable clusters"], ascending=False, kind="stable").iloc[0]


def within_distances(emb: np.ndarray, labels: np.ndarray) -> dict[int, np.ndarray]:
    """For every type, the cosine distances of all pairs of its members."""
    out = {}
    for c in np.unique(labels[labels >= 0]):
        m = np.where(labels == c)[0]
        out[int(c)] = (1 - emb[m] @ emb[m].T)[np.triu_indices(len(m), 1)]
    return out


def rare_cutoff(emb: np.ndarray, labels: np.ndarray) -> tuple[float, float]:
    """Rule discovery.rare_path.distance_cutoff: the median of all within-type pairwise cosine distances of the stable
    types, every pair once. Second value, for information: the median of the types' own medians."""
    w = within_distances(emb, labels)
    return float(np.median(np.concatenate(list(w.values())))), float(np.median([np.median(v) for v in w.values()]))


def rare_path(emb: np.ndarray, institution: np.ndarray, noise: np.ndarray, cutoff: float, max_size: int, min_inst: int) -> np.ndarray:
    """Groups among the offers left without a stable type: average linkage, cut at the distance cutoff, at least
    min_inst institutions, at most max_size offers (rule discovery.rare_path). A larger group is not cut further."""
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


def centroids_and_assignment(emb: np.ndarray, lab: np.ndarray, n_stable: int) -> dict:
    """Rules similarity.centroid, radius_90, rare_types and universe.assign_afterwards. lab: type of every offer (-1 none),
    types numbered 0..n-1 with the stable ones first. No refit: an offer without a type goes to the type with the nearest
    centroid if it lies inside that type's radius_90."""
    ids = np.unique(lab[lab >= 0])
    cent = np.vstack([emb[lab == c].mean(axis=0) for c in ids])
    cent /= np.linalg.norm(cent, axis=1, keepdims=True)
    dist = 1 - emb @ cent.T
    own = {int(c): dist[lab == c, c] for c in ids}
    stable = set(range(n_stable))
    r = {p: radii(own, stable, p) for p in (75, 90, 95)}
    radius = np.array([r[90][int(c)] for c in ids])
    near = dist.argmin(axis=1)
    near_d = dist[np.arange(len(emb)), near]
    assigned = np.where(lab >= 0, lab, np.where(near_d <= radius[near], near, -1))
    return {"centroids": cent, "dist": dist, "own": own, "radii": r, "nearest": near, "nearest_dist": near_d, "assigned": assigned}


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
        out[int(c)] = terms[row.indices[np.argsort(-score, kind="stable")[:top]]].tolist()
    return out


def tfidf_crosscheck(texts: pd.Series, lab: np.ndarray, n_stable: int) -> tuple[dict[int, float], dict[int, float]]:
    """Rule discovery.crosscheck for the stable types: k-means on TF-IDF with k = the number of stable types. First
    result (the rule's flag): k-means on all fitted texts, also those the grouping left without a stable type. Second
    result (for information): k-means only on the texts inside a stable type."""
    from sklearn.cluster import KMeans
    from sklearn.feature_extraction.text import TfidfVectorizer
    k = max(n_stable, 2)
    vec = lambda t: TfidfVectorizer(lowercase=True, stop_words=STOPWORDS, min_df=2, sublinear_tf=True).fit_transform(t)
    stable = np.where(lab < n_stable, lab, -1)
    hard = best_jaccard(stable, KMeans(n_clusters=k, random_state=42, n_init=3).fit_predict(vec(texts)))
    inside = stable >= 0
    easy = best_jaccard(stable[inside], KMeans(n_clusters=k, random_state=42, n_init=3).fit_predict(vec(texts[inside])))
    return hard, easy


def old_lists() -> dict[str, str]:
    from .theme_verdicts import SUBTHEMES
    from .themes import THEMES
    return {**THEMES, **SUBTHEMES}


def recovery(title: pd.Series, labels: np.ndarray, subset: np.ndarray) -> pd.DataFrame:
    """Rule discovery.validation.old_lists on the offers of `subset`: an old list is the offers whose title matches its
    pattern; for each list the type with the highest Jaccard. Offers of the list that are in no type count against it.
    A list without any matching offer cannot be tested."""
    rows = []
    for name, pat in old_lists().items():
        hit = title.str.contains(pat, case=False, regex=True, na=False).to_numpy() & subset
        if not hit.any():
            rows.append({"old list": name, "offers": 0, "best Jaccard": np.nan, "type": -1, "recovered": "not testable: no title matches", "share in any type": np.nan})
            continue
        inter = pd.Series(labels[hit & (labels >= 0)]).value_counts()
        sizes = pd.Series(labels[subset & (labels >= 0)]).value_counts()
        jac = (inter / (hit.sum() + sizes.reindex(inter.index) - inter)).sort_values(ascending=False, kind="stable")
        j = float(jac.iloc[0]) if len(jac) else 0.0
        rows.append({"old list": name, "offers": int(hit.sum()), "best Jaccard": round(j, 3), "type": int(jac.index[0]) if len(jac) else -1,
                     "recovered": "yes" if j >= RECOVERED else "no", "share in any type": round(float((labels[hit] >= 0).mean()), 3)})
    return pd.DataFrame(rows)


def mix(d: pd.DataFrame, by: str) -> pd.DataFrame:
    """Rule text.report. Full-time offers: where the fit put them (noise = left without a stable type). All offers:
    whether they have a type after the assignment."""
    f = d[d["full_time"]]
    g = f.groupby(by, dropna=False).agg(**{"full-time offers": ("type", "size"), "in a stable type": ("kind", lambda k: (k == "stable").mean()),
                                           "noise (no stable type)": ("kind", lambda k: (k != "stable").mean()), "in a rare type": ("kind", lambda k: (k == "rare").mean()),
                                           "assigned afterwards": ("assigned_only", "mean"), "without any type": ("assigned_type", lambda a: (a < 0).mean())})
    a = d.groupby(by, dropna=False).agg(**{"all offers": ("type", "size"), "all: with a type": ("assigned_type", lambda a: (a >= 0).mean())})
    return g.join(a).round(3).reset_index()


def sample_for_review(d: pd.DataFrame) -> str:
    """Criterion G9: 30 types and 10 member titles each, drawn with one generator (seed 42) from all types. A second
    sample of 30 stable types (seed 43) is added, because rare types are small groups of near-identical titles."""
    lines = ["# Funnel step 2: samples of types for the reader's check (generated)", "",
             f"Question per type: are at least 8 of 10 titles (or 80 % of those shown) the same kind of programme?", ""]
    for name, seed, pool in (("Sample A (criterion G9): all types", SAMPLE_SEED, d["type"] >= 0), ("Sample B (additional): stable types only", SAMPLE_SEED + 1, d["kind"] == "stable")):
        rng = np.random.default_rng(seed)
        ids = np.sort(d.loc[pool, "type"].unique())
        pick = np.sort(rng.choice(ids, min(SAMPLE_TYPES, len(ids)), replace=False))
        lines += [f"## {name}", "", f"{len(pick)} types drawn with numpy default_rng({seed}); for each, {SAMPLE_TITLES} member titles drawn with the same generator (all members if fewer).", ""]
        for c in pick:
            m = d[d["type"] == c]
            take = m.iloc[np.sort(rng.choice(len(m), min(SAMPLE_TITLES, len(m)), replace=False))]
            lines += [f"### Type {int(c)} ({m['kind'].iloc[0]}, {len(m)} members)", ""] + [f"- {t} ({i})" for t, i in zip(take["title"], take["institution"])] + [""]
    return "\n".join(lines) + "\n"


def run(setting: tuple[int, str] | None = None) -> None:
    """Without an argument: the grid and the setting the rule selects (the result of the step). With a setting
    (min_cluster_size, method) the selection rule is bypassed: a diagnostic, never the result; its files carry the
    setting in their names and the result files are not touched."""
    import umap
    from sklearn.metrics import adjusted_rand_score
    stamp, rules = run_stamp(), config()
    cfg = rules["discovery"]
    tag = f"_diag_{setting[0]}_{setting[1]}" if setting else ""
    out = lambda path: path.with_name(path.stem + tag + path.suffix)
    if setting:
        cfg = {**cfg, "hdbscan_grid": {**cfg["hdbscan_grid"], "min_cluster_size": [int(setting[0])], "method": [setting[1]]}}
    meta = json.loads(EMBED_META.read_text(encoding="utf-8"))
    if meta["files"] != {OFFERS.name: sha(OFFERS), EMB.name: sha(EMB)}:
        raise SystemExit("the offer texts or the vectors are not the ones the embedding step wrote: run embed again")
    d = pd.read_csv(OFFERS, low_memory=False, dtype={"programme_id": str})
    emb = np.load(EMB).astype(np.float64)
    if len(d) != len(emb) or d["institution"].isna().any():
        raise SystemExit("offers and vectors do not match, or an offer has no institution")
    fit = np.where(d["full_time"])[0]
    u = cfg["umap"]
    coords = [umap.UMAP(n_neighbors=u["n_neighbors"], n_components=u["n_components"], metric=u["metric"], min_dist=u["min_dist"],
                        random_state=s).fit_transform(emb[fit]) for s in u["seeds"]]
    print("umap done", flush=True)
    grid, runs = grid_search(coords, cfg)
    grid.to_csv(out(GRID), index=False)
    pick = select(grid)
    mcs = int(pick["min_cluster_size"])
    print("selected", mcs, pick["method"], flush=True)
    ref, st = runs[(mcs, pick["method"])]
    good = sorted(c for c, s in st.items() if s >= cfg["stable_jaccard"])
    remap = {c: i for i, c in enumerate(good)}
    lab = np.full(len(d), -1)
    lab[fit] = [remap.get(int(r), -1) for r in ref]
    n_stable = len(remap)
    cut, cut_alt = rare_cutoff(emb, lab)
    ft = d["full_time"].to_numpy()
    inst = d["institution"].to_numpy()
    rare = rare_path(emb, inst, (lab < 0) & ft, cut, mcs - 1, cfg["rare_path"]["min_institutions"])
    rare_alt = rare_path(emb, inst, (lab < 0) & ft, cut_alt, mcs - 1, cfg["rare_path"]["min_institutions"])
    lab[rare >= 0] = rare[rare >= 0] + n_stable
    ids = np.unique(lab[lab >= 0])
    g = centroids_and_assignment(emb, lab, n_stable)
    dist, own, assigned, near, near_d = g["dist"], g["own"], g["assigned"], g["nearest"], g["nearest_dist"]
    d["type"] = lab
    d["kind"] = np.where(lab < 0, "none", np.where(lab < n_stable, "stable", "rare"))
    d["assigned_type"] = assigned
    d["assigned_only"] = (lab < 0) & (assigned >= 0)
    d["dist_to_assigned"] = np.where(assigned >= 0, dist[np.arange(len(d)), np.maximum(assigned, 0)], np.nan)
    d["nearest_type"] = near
    d["dist_to_nearest"] = near_d
    terms = ctfidf_terms(d["text"], lab)
    tf_hard, tf_easy = tfidf_crosscheck(d["text"].iloc[fit].reset_index(drop=True), lab[fit], n_stable)
    inv = {v: k for k, v in remap.items()}
    flag = cfg["rare_path"]["evidence_flag"].split('"')[1]
    rows = []
    for c in ids:
        c = int(c)
        mi = np.where(lab == c)[0]
        m, a = d.iloc[mi], d[assigned == c]
        central = [t for t in d["clean_title"].iloc[mi[np.argsort(dist[mi, c], kind="stable")]].drop_duplicates().tolist() if isinstance(t, str) and t][:5]
        n_inst = {lv: int(a.loc[a["level"] == lv, "institution"].nunique()) for lv in ("bachelor", "master")}
        is_stable = c < n_stable
        rows.append({"type": c, "kind": "stable" if is_stable else "rare", "label": ", ".join(terms[c][:4]), "central titles": "; ".join(central),
                     "members": len(m), "member institutions": int(m["institution"].nunique()), "assigned offers": len(a),
                     "bachelor": int((a["level"] == "bachelor").sum()), "master": int((a["level"] == "master").sum()),
                     "bachelor institutions": n_inst["bachelor"], "master institutions": n_inst["master"],
                     "units": int(n_inst["bachelor"] >= 2) + int(n_inst["master"] >= 2),
                     "stability": round(st[inv[c]], 3) if is_stable else np.nan,
                     "median distance": float(np.median(own[c])), "largest distance": float(np.max(own[c])),
                     "radius_75": g["radii"][75][c], "radius_90": g["radii"][90][c], "radius_95": g["radii"][95][c],
                     "share with focus": round(float(m["has_focus"].mean()), 3),
                     "share HAW": round(float(m["institution_type"].str.startswith("Fachhochschule").mean()), 3),
                     "tfidf best Jaccard": round(tf_hard[c], 3) if is_stable else np.nan,
                     "tfidf best Jaccard (typed offers only)": round(tf_easy[c], 3) if is_stable else np.nan,
                     "method-dependent": ("yes" if tf_hard[c] < METHOD_DEPENDENT else "no") if is_stable else "not tested",
                     "evidence flag": "" if is_stable else flag, "terms": "; ".join(terms[c])})
    types = pd.DataFrame(rows)
    f = pd.read_csv(FIELDS, dtype={"programme_id": str}).drop_duplicates("programme_id").set_index("programme_id")["field_key"]
    fk = d["programme_id"].map(f)
    both = (lab >= 0) & fk.notna().to_numpy()
    ari = float(adjusted_rand_score(fk[both].astype(str), lab[both]))
    rec_fit = recovery(d["title"], lab, ft)
    rec_all = recovery(d["title"], assigned, np.ones(len(d), bool))
    rec = rec_fit.merge(rec_all, on="old list", suffixes=(" (fitted, full-time)", " (all assigned)"))
    d.to_csv(out(OFFER_TYPES), index=False)
    types.to_csv(out(TYPES), index=False)
    np.save(out(CENTROIDS), g["centroids"].astype(np.float32))
    stable_t = types[types["kind"] == "stable"]
    limits = (grid["noise"] <= NOISE_MAX) & (grid["largest cluster share"] <= LARGEST_MAX) & (grid["stable clusters"] > 0)
    n_rare = int(len(ids) - n_stable)
    res = {"stamp": stamp, "diagnostic_setting": list(setting) if setting else None, "embed_commit": meta["stamp"]["commit"], "offers": len(d), "full_time": int(ft.sum()),
           "umap_seeds": u["seeds"], "refits_per_setting": cfg["bootstrap"]["refits"], "subsample": cfg["bootstrap"]["subsample"], "settings": len(grid),
           "selected": {"min_cluster_size": mcs, "method": pick["method"], "clusters": int(pick["clusters"]), "stable_clusters": int(pick["stable clusters"]),
                        "share_in_stable": round(float(pick["share in stable"]), 4), "noise": round(float(pick["noise"]), 4),
                        "largest_cluster_share": round(float(pick["largest cluster share"]), 4)},
           "settings_within_limits": int(limits.sum()), "stable_types": n_stable, "rare_types": n_rare, "rare_cutoff": round(cut, 4),
           "rare_cutoff_median_of_type_medians": round(cut_alt, 4), "rare_types_with_that_cutoff": int(len(np.unique(rare_alt[rare_alt >= 0]))),
           "median_radius_90_stable": round(float(stable_t["radius_90"].median()), 4),
           "full_time_in_stable": int(((lab >= 0) & (lab < n_stable)).sum()), "full_time_in_rare": int((lab >= n_stable).sum()),
           "full_time_without_type": int(((lab < 0) & ft).sum()), "assigned_afterwards": int(d["assigned_only"].sum()),
           "assigned_afterwards_full_time": int((d["assigned_only"] & d["full_time"]).sum()), "offers_without_any_type": int((assigned < 0).sum()),
           "units": int(types["units"].sum()), "types_with_a_unit": int((types["units"] > 0).sum()),
           "largest_type_members": int(types["members"].max()), "median_stable_members": float(stable_t["members"].median()),
           "ari_study_fields": round(ari, 3), "offers_in_ari": int(both.sum()), "tfidf_k": int(max(n_stable, 2)),
           "method_dependent_stable": int((stable_t["method-dependent"] == "yes").sum()),
           "method_dependent_stable_typed_offers_only": int((stable_t["tfidf best Jaccard (typed offers only)"] < METHOD_DEPENDENT).sum()),
           "old_lists": len(rec),
           "old_lists_tested_fitted": int((~rec_fit["recovered"].str.startswith("not testable")).sum()), "old_lists_recovered_fitted": int((rec_fit["recovered"] == "yes").sum()),
           "old_lists_tested_assigned": int((~rec_all["recovered"].str.startswith("not testable")).sum()), "old_lists_recovered_assigned": int((rec_all["recovered"] == "yes").sum()),
           "files": {p.name: sha(p) for p in (OFFERS, EMB, out(GRID), out(TYPES), out(OFFER_TYPES), out(CENTROIDS))}}
    out(RESULT).write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORTS.mkdir(parents=True, exist_ok=True)
    show = types.drop(columns=["terms", "radius_75", "radius_95", "largest distance"]).round(4)
    (REPORTS / f"step2_types{tag}.md").write_text("\n".join([
        "# Funnel step 2: programme types (generated)" + (f" - DIAGNOSTIC, setting {setting} forced, not the rule's choice" if setting else ""), "",
        f"Code commit {stamp['commit']} (texts and vectors: {res['embed_commit']}), run on {stamp['date']}, tracked files clean: {stamp['clean']}.", "",
        f"- Offers: {len(d)}; full-time offers used for the fit: {int(ft.sum())}.",
        f"- Grid: {len(grid)} settings, UMAP seeds {u['seeds']}, {res['refits_per_setting']} refits per setting on {res['subsample']:.0%} subsamples (the seeds in turn).",
        f"- Selected setting: min_cluster_size {mcs}, method {pick['method']} ({res['settings_within_limits']} of {len(grid)} settings are within the limits).",
        f"- Types: {n_stable} stable, {n_rare} rare (flag: {flag}). Rare-path cutoff {cut:.4f} (median of all within-type pairs); "
        f"with the median of the types' medians ({cut_alt:.4f}) there would be {res['rare_types_with_that_cutoff']} rare types.",
        f"- Full-time offers: {res['full_time_in_stable']} in a stable type, {res['full_time_in_rare']} in a rare type, {res['full_time_without_type']} left without a type by the fit.",
        f"- Assigned afterwards (inside the radius of the nearest type): {res['assigned_afterwards']} offers; without any type after that: {res['offers_without_any_type']}.",
        f"- Units (type x level with offers at 2 or more institutions): {res['units']}.",
        f"- Agreement with the catalogue's study fields (ARI; fitted members, first-listed field): {ari:.3f}.",
        f"- TF-IDF cross-check (k-means, k = {res['tfidf_k']}, stable types only): method-dependent {res['method_dependent_stable']} of {n_stable} "
        f"when k-means also has to place the offers without a stable type; {res['method_dependent_stable_typed_offers_only']} of {n_stable} on the typed offers only. Rare types are not tested.",
        f"- Old topic lists (title patterns): {res['old_lists']} lists; on the fitted full-time offers {res['old_lists_tested_fitted']} tested and "
        f"{res['old_lists_recovered_fitted']} recovered (Jaccard >= {RECOVERED}); on all assigned offers {res['old_lists_tested_assigned']} tested and {res['old_lists_recovered_assigned']} recovered.", "",
        "## Grid", "", md_table(grid.round(4)), "", "## Mix by focus items present", "", md_table(mix(d, "has_focus")), "",
        "## Mix by institution type", "", md_table(mix(d, "institution_type")), "",
        "## The old topic lists (counts only)", "", md_table(rec), "", "## Types", "", md_table(show)]) + "\n", encoding="utf-8")
    (REPORTS / f"step2_sample{tag}.md").write_text(sample_for_review(d), encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "run" and len(sys.argv) == 4:
        run((int(sys.argv[2]), sys.argv[3]))
    else:
        {"scan": scan, "embed": embed, "run": run}[sys.argv[1]]()
