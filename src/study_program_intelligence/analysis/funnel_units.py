"""Funnel step 3: which units stay, and how much competition do they have? (configs/funnel.yaml: definitions,
pool_mapping, screen, freeze; criteria in docs/criteria_funnel_step3.md)

Run from the repository root, each command from committed code on a clean tree, after analysis.funnel_types:

    python -m study_program_intelligence.analysis.funnel_units items    # vectors of every title, focus item and EMI module title
    python -m study_program_intelligence.analysis.funnel_units labels   # the 300 units a reader marks for the EMI-field bar
    python -m study_program_intelligence.analysis.funnel_units run      # screens, competition, regional gap, frozen lists
    python -m study_program_intelligence.analysis.funnel_units sheet    # the 100 offers of the validity check, for Soma

A unit is a type x level with assigned offers at 2 or more institutions. Every unit gets the same four screens (already
at OTH, teacher training, falling validated trend, outside EMI's field); competition and the regional gap are measured
and never used as a cut. Nothing is added or removed by hand.
Outputs: data/interim/funnel2_item_vectors.npy, funnel2_item_index.csv, funnel2_module_title_vectors.npy, funnel2_items.json,
funnel2_screen.csv, funnel2_candidates.csv, funnel2_candidates_stress.csv, funnel2_emi_calibration.csv, funnel2_step3.json,
funnel2_similarity_key.csv; reports/funnel2/step3_screen.md, step3_coherence_sample.md, step3_emi_label_sample.md;
docs/funnel_similarity_check.csv (the sheet).
"""

from __future__ import annotations

import hashlib
import json
import re
import sys

import numpy as np
import pandas as pd
import yaml

from .funnel_common import INTERIM, REPO_ROOT, REPORTS, config, md_table, run_stamp
from .funnel_subject_map import clean_label as map_label     # the label form the subject map was built with
from .funnel_types import CENTROIDS, EMB, OFFER_TYPES, RESULT, SEP, TYPES, clean_label, normalise, sha

SUBJECT_MAP = REPO_ROOT / "configs" / "funnel_subject_map.csv"
PORTFOLIO = REPO_ROOT / "configs" / "oth_portfolio.yaml"
EMI_LABELS = REPO_ROOT / "docs" / "funnel_emi_labels.csv"
DESTATIS = REPO_ROOT / "data" / "raw" / "destatis"
MODULES = INTERIM / "modules_emi_2026.csv"
ITEM_VEC, ITEM_INDEX, MODULE_VEC = INTERIM / "funnel2_item_vectors.npy", INTERIM / "funnel2_item_index.csv", INTERIM / "funnel2_module_title_vectors.npy"
ITEMS_META = INTERIM / "funnel2_items.json"
SCREEN, PRIMARY, STRESS = INTERIM / "funnel2_screen.csv", INTERIM / "funnel2_candidates.csv", INTERIM / "funnel2_candidates_stress.csv"
CALIBRATION, STEP3 = INTERIM / "funnel2_emi_calibration.csv", INTERIM / "funnel2_step3.json"
KEY, SHEET = INTERIM / "funnel2_similarity_key.csv", REPO_ROOT / "docs" / "funnel_similarity_check.csv"
MODEL = "intfloat/multilingual-e5-base"
LEVELS = ("bachelor", "master")
SERIES = {"bachelor": ("first-years", 2019, 2024, 2024), "master": ("graduates", 2019, 2025, 2025)}   # screen.trend: kind, window, last backtest year
LAND = {"Schleswig-Holstein": "SH", "Hamburg": "HH", "Niedersachsen": "NI", "Bremen": "HB", "Nordrhein-Westfalen": "NW", "Hessen": "HE",
        "Rheinland-Pfalz": "RP", "Baden-Württemberg": "BW", "Bayern": "BY", "Saarland": "SL", "Berlin": "BE", "Brandenburg": "BB",
        "Mecklenburg-Vorpommern": "MV", "Sachsen": "SN", "Sachsen-Anhalt": "ST", "Thüringen": "TH"}
SOUTH = ("BY", "BW")            # screen.regional_gap.south
PSEUDO = 5.0                    # screen.regional_gap.bavarian_quotient
QUOTIENT_FROM = 5               # screen.regional_gap.quotient_from
KEEP = 0.95                     # screen.emi_domain.bar
LABEL_UNITS, LABEL_TITLES = 300, 8


def plain(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", normalise(s)).strip()


def unit_rows(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v, axis=1, keepdims=True)


def file_hash(paths) -> str:
    h = hashlib.sha256()
    for p in sorted(paths):
        h.update(p.read_bytes())
    return h.hexdigest()[:16]


# ------------------------------------------------------------------------------------------------------- items

def offer_items(d: pd.DataFrame) -> list[list[str]]:
    """Per offer: its cleaned title and its focus items (rule screen.emi_domain.offer_score)."""
    return [[t, *(f.split(SEP) if isinstance(f, str) and f else [])] for t, f in zip(d["clean_title"], d["focus_text"])]


def module_titles() -> list[str]:
    return sorted(set(pd.read_csv(MODULES, low_memory=False)["title"].dropna().astype(str)))


def items() -> None:
    stamp = run_stamp()
    d = pd.read_csv(OFFER_TYPES, low_memory=False, dtype={"programme_id": str})
    uniq = sorted({x for lst in offer_items(d) for x in lst if isinstance(x, str) and x})
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL)
    enc = lambda texts: model.encode([f"query: {t}" for t in texts], normalize_embeddings=True, batch_size=128, show_progress_bar=False).astype(np.float32)
    np.save(ITEM_VEC, enc(uniq))
    pd.DataFrame({"item": uniq}).to_csv(ITEM_INDEX, index=False)
    np.save(MODULE_VEC, enc(module_titles()))
    ITEMS_META.write_text(json.dumps({"stamp": stamp, "items": len(uniq), "module_titles": len(module_titles()), "offer_types": sha(OFFER_TYPES), "modules": sha(MODULES),
                                      "files": {p.name: sha(p) for p in (ITEM_VEC, ITEM_INDEX, MODULE_VEC)}}, indent=2) + "\n", encoding="utf-8")
    print(f"{len(uniq)} distinct titles and focus items and {len(module_titles())} EMI module titles encoded.")


# ------------------------------------------------------------------------------------------------- definitions

def units_of(d: pd.DataFrame) -> pd.DataFrame:
    """Rule definitions.unit: a type x level with assigned offers of that level at 2 or more institutions."""
    a = d[d["assigned_type"] >= 0]
    u = a.groupby(["assigned_type", "level"]).agg(offers=("title", "size"), institutions=("institution", "nunique")).reset_index()
    u = u[u["institutions"] >= 2].rename(columns={"assigned_type": "type"})
    u["level"] = pd.Categorical(u["level"], LEVELS, ordered=True)
    return u.sort_values(["type", "level"]).reset_index(drop=True)


def merged_groups(units: pd.DataFrame, cent: np.ndarray, radius: np.ndarray) -> np.ndarray:
    """Rule definitions.merged_candidates: units of one level form a group if every pair of them has centroids inside
    each other's radius_90. Complete-linkage grouping on the centroid distance divided by the smaller of the two radii,
    cut at 1 (the closest pair merges first). Returns, for every unit, the lowest type number of its group."""
    from sklearn.cluster import AgglomerativeClustering
    dist = 1 - cent @ cent.T
    group = units["type"].to_numpy().copy()
    for lv in LEVELS:
        idx = np.where(units["level"] == lv)[0]
        t = units["type"].to_numpy()[idx]
        if len(t) < 2:
            continue
        ratio = dist[np.ix_(t, t)] / np.minimum(radius[t][:, None], radius[t][None, :])
        np.fill_diagonal(ratio, 0.0)
        lab = AgglomerativeClustering(n_clusters=None, metric="precomputed", linkage="complete", distance_threshold=np.nextafter(1.0, 2.0)).fit_predict(ratio)
        group[idx] = pd.Series(t).groupby(lab).transform("min").to_numpy()
    return group


# ------------------------------------------------------------------------------------------------------ screens

def teacher_share(a: pd.DataFrame, pattern: str) -> float:
    """Rule screen.teacher_training.share: share of the offers whose normalised title, degree or subject labels match.
    The labels are taken without the level marker ("grundständig außer Staatsexamen" is no state examination)."""
    labels = a["subjects"].fillna("").map(lambda s: "; ".join(clean_label(x) for x in s.split("; ")))
    text = (a["title"].fillna("") + " " + a["degree"].fillna("") + " " + labels).map(normalise)
    return float(text.map(lambda x: bool(re.search(pattern, x))).mean())


def pool_weights(a: pd.DataFrame, smap: dict[str, str]) -> dict[str, float]:
    """Rule pool_mapping.weights: fractional per offer over its labels; the mean over the offers."""
    w: dict[str, float] = {}
    for s in a["subjects"]:
        labels = [map_label(x) for x in str(s).split("; ")]
        for x in labels:
            w[smap[x]] = w.get(smap[x], 0.0) + 1 / len(labels)
    return {k: v / len(a) for k, v in w.items()}


def slope_pct(y: pd.Series, first: int, last: int) -> float:
    """Log-linear slope in % a year over the window; needs a positive value in every year of the window."""
    s = y.reindex(range(first, last + 1))
    if s.isna().any() or (s <= 0).any():
        return float("nan")
    return float(100 * (np.exp(np.polyfit(s.index.to_numpy(float), np.log(s.to_numpy(float)), 1)[0]) - 1))


def backtest(y: pd.Series, last: int, rule: dict) -> dict:
    """Rule demand.backtest and demand.validated: rolling origins from origins_from, horizons 1 to 5, MASE of the naive and
    the drift model (scaled by the mean absolute yearly change of the training years, pooled over origins and horizons).
    The series is the longest run of consecutive years with a positive value ending in `last`; with fewer than
    min_series years it is not backtested and not validated."""
    y = y[(y.index <= last) & (y > 0)].dropna().sort_index()
    if y.empty or y.index[-1] != last:
        return {"years": 0, "naive": np.nan, "drift": np.nan, "validated": False}
    gaps = np.where(np.diff(y.index) != 1)[0]
    y = y.iloc[gaps[-1] + 1:] if len(gaps) else y
    n_min = int(re.match(r"(\d+)", str(rule["min_series"])).group(1))
    if len(y) < n_min:
        return {"years": len(y), "naive": np.nan, "drift": np.nan, "validated": False}
    err = {"naive": [], "drift": []}
    for origin in range(max(rule["backtest"]["origins_from"], int(y.index[0]) + 2), last):
        train = y[y.index <= origin]
        scale = train.diff().abs().mean()
        if not scale > 0:
            continue
        step = (train.iloc[-1] - train.iloc[0]) / (len(train) - 1)
        for h in rule["backtest"]["horizons"]:
            if origin + h > last:
                break
            actual = y.loc[origin + h]
            err["naive"].append(abs(train.iloc[-1] - actual) / scale)
            err["drift"].append(abs(train.iloc[-1] + step * h - actual) / scale)
    if not err["naive"]:
        return {"years": len(y), "naive": np.nan, "drift": np.nan, "validated": False}
    naive, drift = float(np.mean(err["naive"])), float(np.mean(err["drift"]))
    return {"years": len(y), "naive": naive, "drift": drift, "validated": bool(drift < naive and drift < 1)}


def destatis_bavaria() -> pd.DataFrame:
    """German first-years and graduates in Bavaria by subject and year, index (kind, year), columns subject codes."""
    from .demand_split import load
    long = load()
    return long[(long["region"] == "BY") & (long["nationality"] == "German")].pivot_table(index=["kind", "year"], columns="code", values="value", aggfunc="sum")


def destatis_laender() -> pd.DataFrame:
    """German first-years by Land, subject and year (tables 21311-0015 by Land), index (land, year), columns codes."""
    rows = []
    for land in LAND.values():
        t = pd.read_csv(DESTATIS / f"21311-0015_{land}.csv", sep=";", dtype=str)
        col = lambda label: next(c for c in t.columns if c.endswith("variable_label") and (t[c] == label).any()).replace("variable_label", "variable_attribute_code")
        t = t[(t[col("Nationalität")] == "NATD") & t[col("Geschlecht")].isna()]
        rows.append(pd.DataFrame({"land": land, "code": t[col("Studienfach")], "year": t["time"].str[:4].astype(int), "value": pd.to_numeric(t["value"], errors="coerce")}))
    return pd.concat(rows).pivot_table(index=["land", "year"], columns="code", values="value", aggfunc="sum")


def pool_series(table: pd.DataFrame, w: dict[str, float]) -> pd.Series:
    """Weighted sum over the pool's subjects; a subject without a value in a year counts as 0 for that year."""
    cols = [c for c in w if c in table.columns]
    return (table[cols].fillna(0.0) * pd.Series({c: w[c] for c in cols})).sum(axis=1) if cols else pd.Series(0.0, index=table.index)


def emi_positive(titles: pd.Series) -> pd.Series:
    names = [plain(p["name"]) for p in yaml.safe_load(PORTFOLIO.read_text(encoding="utf-8"))["programmes"]]
    return titles.map(lambda t: any(n in plain(t) for n in names))


def auc(pos: np.ndarray, neg: np.ndarray) -> float:
    return float(np.mean([(p > neg).mean() + 0.5 * (p == neg).mean() for p in pos]))


def youden(pos: np.ndarray, neg: np.ndarray) -> float:
    """Cut with the largest true-positive rate minus false-positive rate (score >= cut counts as positive); of equal cuts
    the lowest."""
    cuts = np.unique(np.concatenate([pos, neg]))
    return float(cuts[int(np.argmax([(pos >= c).mean() - (neg >= c).mean() for c in cuts]))])


def keep_bar(pos: np.ndarray, keep: float = KEEP) -> float:
    """Rule screen.emi_domain.bar: the highest score that keeps at least `keep` of the marked field units."""
    s = np.sort(pos)
    return float(s[len(s) - int(np.ceil(keep * len(s)))])


def emi_offer_scores(item_lists: list[list[str]], item_pos: dict[str, int], item_vec: np.ndarray, module_vec: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Rule screen.emi_domain.offer_score: per offer the mean, over its title and focus items, of the highest cosine to
    the title of any EMI module; all vectors centred on the mean vector of all titles and focus items. Second result:
    the same for the title alone."""
    mean = item_vec.mean(axis=0)
    best = (unit_rows(item_vec - mean) @ unit_rows(module_vec - mean).T).max(axis=1)
    return (np.array([float(np.mean([best[item_pos[x]] for x in lst])) for lst in item_lists]),
            np.array([float(best[item_pos[lst[0]]]) for lst in item_lists]))


def quotient(n_by: int, n_de: int, p: float, pseudo: float = PSEUDO) -> float:
    """Rule screen.regional_gap.bavarian_quotient: a location quotient shrunk towards 1 when offers are few."""
    return ((n_by + pseudo * p) / (n_de + pseudo)) / p


def gap_numbers(sim: np.ndarray, far: np.ndarray, land: np.ndarray, km: np.ndarray, p: float) -> dict:
    """Counts and flags of one set of similar offers (rules screen.competition.report and screen.regional_gap)."""
    south, by = np.isin(land, SOUTH), land == "BY"
    n = {"similar offers": int(sim.sum()), "similar in Bavaria": int((sim & by).sum()), "similar in the south": int((sim & south).sum()),
         "similar within 50 km": int((sim & (km <= 50)).sum()), "similar within 100 km": int((sim & (km <= 100)).sum()),
         "similar within 150 km": int((sim & (km <= 150)).sum()), "similar distance-learning offers (not counted)": int(far.sum())}
    elsewhere = n["similar offers"] - n["similar in the south"] >= 1
    n.update({"exists elsewhere": bool(elsewhere), "absent flag": bool(elsewhere and n["similar in Bavaria"] == 0),
              "gap flag": bool(elsewhere and n["similar within 150 km"] == 0 and n["similar in the south"] == 0),
              "bavarian quotient": quotient(n["similar in Bavaria"], n["similar offers"], p) if n["similar offers"] >= QUOTIENT_FROM else np.nan})
    return n


# ------------------------------------------------------------------------------------------------------- labels

def label_sample(d: pd.DataFrame, units: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Rule screen.emi_domain.calibration: 300 units drawn with numpy default_rng(42) from all units in type order (bachelor
    before master), each shown with up to 8 titles of its assigned offers drawn with the same generator."""
    rng = np.random.default_rng(42)
    pick = np.sort(rng.choice(len(units), LABEL_UNITS, replace=False))
    lines, rows = [f"# {LABEL_UNITS} groups of study programmes", ""], []
    for n, k in enumerate(pick, 1):
        c, lv = int(units.at[k, "type"]), str(units.at[k, "level"])
        a = d[(d["assigned_type"] == c) & (d["level"] == lv)]
        take = a.iloc[np.sort(rng.choice(len(a), min(LABEL_TITLES, len(a)), replace=False))]
        lines += [f"### Group {n} ({lv}, {len(a)} offers)", ""] + [f"- {t}" for t in take["title"]] + [""]
        rows.append({"group": n, "type": c, "level": lv})
    return pd.DataFrame(rows), "\n".join(lines) + "\n"


def labels() -> None:
    """Writes the sample the reader marks. The marks themselves are in docs/funnel_emi_labels.csv."""
    run_stamp()
    d = pd.read_csv(OFFER_TYPES, low_memory=False, dtype={"programme_id": str})
    key, text = label_sample(d, units_of(d))
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "step3_emi_label_sample.md").write_text(text, encoding="utf-8")
    if EMI_LABELS.exists():
        lab = pd.read_csv(EMI_LABELS, keep_default_na=False)
        same = list(zip(lab["group"], lab["type"], lab["level"])) == list(zip(key["group"], key["type"], key["level"]))
        print("the marks in docs/funnel_emi_labels.csv belong to this sample:", same)
    print(f"{len(key)} units written to reports/funnel2/step3_emi_label_sample.md")


# ---------------------------------------------------------------------------------------------------------- run

def load_step2() -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    r = json.loads(RESULT.read_text(encoding="utf-8"))
    for p in (OFFER_TYPES, TYPES, EMB, CENTROIDS):
        if r["files"][p.name] != sha(p):
            raise SystemExit(f"{p.name} is not the file Step 2 wrote")
    d = pd.read_csv(OFFER_TYPES, low_memory=False, dtype={"programme_id": str})
    return d, pd.read_csv(TYPES), np.load(EMB).astype(np.float64), np.load(CENTROIDS).astype(np.float64)


def run() -> None:
    stamp, rules = run_stamp(), config()
    sc = rules["screen"]
    d, t, emb, cent = load_step2()
    meta = json.loads(ITEMS_META.read_text(encoding="utf-8"))
    if meta["offer_types"] != sha(OFFER_TYPES) or meta["modules"] != sha(MODULES) or meta["files"] != {p.name: sha(p) for p in (ITEM_VEC, ITEM_INDEX, MODULE_VEC)}:
        raise SystemExit("the item vectors do not belong to the current offers or modules: run items again")
    item_pos = {x: i for i, x in enumerate(pd.read_csv(ITEM_INDEX, keep_default_na=False)["item"])}
    radius, median = t["radius_90"].to_numpy(), t["median distance"].to_numpy()
    r75, r95 = t["radius_75"].to_numpy(), t["radius_95"].to_numpy()
    dist = 1 - emb @ cent.T
    assigned, level = d["assigned_type"].to_numpy(), d["level"].to_numpy()
    oth, distance = d["is_oth"].to_numpy(bool), d["distance_only"].to_numpy(bool)
    land = d["state"].map(LAND).fillna("").to_numpy()        # an offer without a Land or coordinates counts for Germany only
    km = d["km_amberg"].to_numpy()                           # a missing distance is within no distance
    first = ~d.duplicated(["institution", "clean_title", "level"]).to_numpy()      # competition.unit_counted: institution and cleaned title once
    supply = ~oth & ~distance & first                                              # universe.counted_as_supply
    far_supply = ~oth & distance & first

    units = units_of(d)
    units["group"] = merged_groups(units, cent, radius)

    # EMI-field score (screen.emi_domain)
    score_all, score_title = emi_offer_scores(offer_items(d), item_pos, np.load(ITEM_VEC).astype(np.float64), np.load(MODULE_VEC).astype(np.float64))
    has_focus = d["has_focus"].to_numpy(bool)

    def unit_score(c: int, lv: str) -> tuple[float, str]:
        a = (assigned == c) & (level == lv)
        a = a & ~oth if (a & ~oth).any() else a
        fo = a & has_focus
        return (float(score_all[fo].mean()), "offers with focus items") if fo.any() else (float(score_title[a].mean()), "titles only")

    smap = pd.read_csv(SUBJECT_MAP).set_index("label")["code"].to_dict()
    by, laender = destatis_bavaria(), destatis_laender()
    pattern, tt_line, trend_line = sc["teacher_training"]["pattern"], sc["teacher_training"]["drop_if_at_least"], sc["trend"]["drop_if_below"]
    p_by = {lv: float(((land == "BY") & (level == lv)).sum() / (level == lv).sum()) for lv in LEVELS}      # Bavaria's share of all offers of the level
    similar_of: dict[tuple[int, str], np.ndarray] = {}
    far_of: dict[tuple[int, str], np.ndarray] = {}
    rows = []
    for u in units.itertuples():
        c, lv = int(u.type), str(u.level)
        at_level = level == lv
        a = d[(assigned == c) & at_level]
        oth_near = np.where(oth & at_level & (dist[:, c] <= median[c]))[0]
        kind, y0, y1, last = SERIES[lv]
        w = pool_weights(a, smap)
        y = pool_series(by.loc[kind], w)
        slope, bt = slope_pct(y, y0, y1), backtest(y, last, rules["demand"])
        emi, emi_from = unit_score(c, lv)
        inside = at_level & ((assigned == c) | (dist[:, c] <= radius[c]))
        sim, far = supply & inside, far_supply & inside
        similar_of[(c, lv)], far_of[(c, lv)] = sim, far
        other_laender = sorted(set(land[sim & ~np.isin(land, SOUTH)]) - {""})
        slope_else = slope_pct(pool_series(laender.loc[other_laender].groupby("year").sum(), w), 2019, 2024) if other_laender else float("nan")
        g = gap_numbers(sim, far, land, km, p_by[lv])
        rows.append({"type": c, "level": lv, "kind": t.at[c, "kind"], "group": int(u.group), "central titles": t.at[c, "central titles"],
                     "assigned offers": len(a), "institutions": int(u.institutions),
                     "OTH offer within the median distance": "; ".join(d["title"].to_numpy()[oth_near][:3]), "drop: at OTH": bool(len(oth_near)),
                     "OTH offers assigned": "; ".join(d.loc[(assigned == c) & at_level & oth, "title"].head(3)),
                     "teacher share": teacher_share(a, pattern),
                     "pool": "; ".join(f"{k}:{v:.2f}" for k, v in sorted(w.items(), key=lambda kv: (-kv[1], kv[0]))[:4]), "pool subjects": len(w), "pool weight sum": sum(w.values()),
                     "trend %/yr": slope, "backtest years": bt["years"], "MASE naive": bt["naive"], "MASE drift": bt["drift"], "trend validated": bt["validated"],
                     "emi score": emi, "emi score from": emi_from, **g,
                     "similar within 150 km (radius 75)": int((supply & at_level & ((assigned == c) | (dist[:, c] <= r75[c])) & (km <= 150)).sum()),
                     "similar within 150 km (radius 95)": int((supply & at_level & ((assigned == c) | (dist[:, c] <= r95[c])) & (km <= 150)).sum()),
                     "Laender elsewhere with a similar offer": len(other_laender), "trend elsewhere %/yr": slope_else,
                     "popularity tier": 2 if (g["exists elsewhere"] and slope_else >= 0) else 3,
                     "method-dependent": t.at[c, "method-dependent"], "evidence flag": t.at[c, "evidence flag"] if isinstance(t.at[c, "evidence flag"], str) else ""})
    s = pd.DataFrame(rows)

    # bar of the EMI-field screen from the marked units
    lab = pd.read_csv(EMI_LABELS, keep_default_na=False).merge(s[["type", "level", "emi score"]], on=["type", "level"], how="left")
    key, _ = label_sample(d, units)
    if list(zip(lab["group"], lab["type"], lab["level"])) != list(zip(key["group"], key["type"], key["level"])) or lab["emi score"].isna().any():
        raise SystemExit("docs/funnel_emi_labels.csv does not belong to the units of this Step 2 result")
    pos, neg = lab.loc[lab["label"].isin(["yes", "partly"]), "emi score"].to_numpy(), lab.loc[lab["label"] == "no", "emi score"].to_numpy()
    bar, emi_auc = keep_bar(pos), auc(pos, neg)
    emi_drops = emi_auc >= sc["emi_domain"]["if_auc_below"]["auc"]
    cal = d[oth].copy()
    cal["emi"], cal["score"] = emi_positive(cal["title"]), score_all[oth]
    cal[["title", "degree", "city", "study_form", "emi", "score"]].sort_values("score", ascending=False).to_csv(CALIBRATION, index=False)

    s["drop: teacher training"] = s["teacher share"] >= tt_line
    s["drop: trend"] = (s["trend %/yr"] < trend_line) & s["trend validated"]
    s["outside EMI"] = s["emi score"] < bar
    s["drop: outside EMI"] = s["outside EMI"] & emi_drops
    at_oth_groups = s.loc[s["drop: at OTH"]].groupby("level")["group"].agg(set).to_dict()
    s["drop: at OTH via merged group"] = [(not own) and g in at_oth_groups.get(lv, set()) for own, g, lv in zip(s["drop: at OTH"], s["group"], s["level"])]
    s["at OTH (own or group)"] = s["drop: at OTH"] | s["drop: at OTH via merged group"]
    extra: dict[int, dict] = {}
    for (lv, g), part in s.groupby(["level", "group"]):                        # the merged group: union of its units' similar offers
        union = np.any([similar_of[(int(c), lv)] for c in part["type"]], axis=0)
        far_union = np.any([far_of[(int(c), lv)] for c in part["type"]], axis=0)
        numbers = {"group size": len(part), "group types": "; ".join(str(int(c)) for c in part["type"]),
                   **{f"group: {k}": v for k, v in gap_numbers(union, far_union, land, km, p_by[lv]).items()}}
        extra.update({i: numbers for i in part.index})
    s = s.join(pd.DataFrame.from_dict(extra, orient="index"))
    reasons = {"at OTH (own or group)": "already at OTH", "drop: teacher training": "teacher training", "drop: trend": "falling validated trend", "drop: outside EMI": "outside EMI's field"}
    s["reasons"] = [" | ".join(v for k, v in reasons.items() if r[k]) or "-" for r in s.to_dict("records")]
    s["primary"] = s["reasons"] == "-"
    s["stress"] = ~s["at OTH (own or group)"]
    s.to_csv(SCREEN, index=False)
    lists = {"primary": s[s["primary"]], "stress": s[s["stress"]]}
    lists["primary"].to_csv(PRIMARY, index=False)
    lists["stress"].to_csv(STRESS, index=False)
    hashes = {k: hashlib.sha256("\n".join(f"{r.type}:{r.level}" for r in v.itertuples()).encode()).hexdigest()[:16] for k, v in lists.items()}

    # titles for the coherence reading: every type with a unit on the primary list (screen.type_coherence)
    lines = ["# Funnel step 3: types to read for coherence (generated)", "",
             "Question per type: are at least 80 % of the titles shown the same kind of programme (same subject, same kind of qualification)?", ""]
    for c in sorted(lists["primary"]["type"].unique()):
        m = d[d["type"] == c]
        take = m.iloc[np.sort(np.random.default_rng(42).choice(len(m), min(10, len(m)), replace=False))]
        lines += [f"### Type {int(c)}", ""] + [f"- {x}" for x in take["title"]] + [""]
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "step3_coherence_sample.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    count = lambda col, sub=s: int(sub[col].sum())
    tally = lambda col: {str(k): int(v) for k, v in col.value_counts().items()}
    prim, sizes = lists["primary"], s.groupby(["level", "group"]).size()
    oth_pos, oth_neg = cal.loc[cal["emi"], "score"].to_numpy(), cal.loc[~cal["emi"], "score"].to_numpy()
    res = {"stamp": stamp, "step2_commit": json.loads(RESULT.read_text(encoding="utf-8"))["stamp"]["commit"], "units": len(s), "types_with_a_unit": int(s["type"].nunique()),
           "units_by_level": tally(s["level"]), "merged_groups_with_more_than_one_unit": int((sizes > 1).sum()), "units_in_such_groups": int(sizes[sizes > 1].sum()),
           "largest_merged_group": int(sizes.max()),
           "calibration": {"marked_units": len(lab), "field_units": int(len(pos)), "outside_units": int(len(neg)), "auc": round(emi_auc, 3), "bar": bar, "screen_drops": bool(emi_drops),
                           "field_units_kept": int((pos >= bar).sum()), "outside_units_kept": int((neg >= bar).sum()), "youden_cut": youden(pos, neg),
                           "auc_on_oth_offers": round(auc(oth_pos, oth_neg), 3), "oth_emi_offers": int(len(oth_pos)), "other_oth_offers": int(len(oth_neg)),
                           "p90_of_emi_offers": float(np.percentile(oth_pos, 90))},
           "dropped": {"at OTH (own offer)": count("drop: at OTH"), "at OTH (via merged group)": count("drop: at OTH via merged group"),
                       "teacher training": count("drop: teacher training"), "falling validated trend": count("drop: trend"), "outside EMI's field": count("drop: outside EMI")},
           "dropped_for_one_reason_only": {v: int((s["reasons"] == v).sum()) for v in reasons.values()},
           "units_with_a_validated_trend": count("trend validated"), "units_without_a_trend_value": int(s["trend %/yr"].isna().sum()),
           "units_not_backtested": int((s["backtest years"] < 12).sum()),
           "primary": len(prim), "primary_types": int(prim["type"].nunique()), "primary_candidates": int(prim.groupby(["level", "group"]).ngroups),
           "primary_by_level": tally(prim["level"]), "primary_by_kind": tally(prim["kind"]), "stress": len(lists["stress"]), "hashes": hashes,
           "primary_flags": {"absent in Bavaria": count("absent flag", prim), "gap (none within 150 km and none in the south)": count("gap flag", prim),
                             "no similar offer within 150 km": int((prim["similar within 150 km"] == 0).sum()), "popularity tier 2": int((prim["popularity tier"] == 2).sum()),
                             "method-dependent stable type": int((prim["method-dependent"] == "yes").sum()), "not stability-tested": int((prim["evidence flag"] != "").sum())},
           "offers_without_a_land": int((land == "").sum()), "offers_without_a_distance": int(np.isnan(km).sum()),
           "offers_counted_once_by_cleaned_title": int((~first).sum()), "bavaria_share_of_offers": {k: round(v, 4) for k, v in p_by.items()},
           "competition": "not validated yet (screen.competition.validity_check)",
           "inputs": {MODULES.name: sha(MODULES), EMI_LABELS.name: sha(EMI_LABELS), SUBJECT_MAP.name: sha(SUBJECT_MAP), "destatis tables": file_hash(DESTATIS.glob("213*.csv")),
                      ITEM_INDEX.name: sha(ITEM_INDEX), MODULE_VEC.name: sha(MODULE_VEC)},
           "files": {p.name: sha(p) for p in (OFFER_TYPES, TYPES, EMB, CENTROIDS, ITEM_VEC, SCREEN, PRIMARY, STRESS, CALIBRATION)}}
    STEP3.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    show = ["type", "level", "kind", "group", "central titles", "assigned offers", "trend %/yr", "emi score", "similar offers", "similar in Bavaria",
            "similar within 150 km", "absent flag", "gap flag", "bavarian quotient", "popularity tier", "evidence flag"]
    full = ["type", "level", "central titles", "assigned offers", "teacher share", "trend %/yr", "trend validated", "emi score", "similar within 150 km", "reasons"]
    cut = lambda x: x.assign(**{"central titles": x["central titles"].str.slice(0, 90)}).round(3)
    c = res["calibration"]
    (REPORTS / "step3_screen.md").write_text("\n".join([
        "# Funnel step 3: screen, competition and frozen lists (generated)", "",
        f"Code commit {stamp['commit']} (types: {res['step2_commit']}), run on {stamp['date']}, tracked files clean: {stamp['clean']}.", "",
        f"- Units tested: {len(s)} ({res['units_by_level']}) from {res['types_with_a_unit']} types; merged groups with more than one unit: "
        f"{res['merged_groups_with_more_than_one_unit']} holding {res['units_in_such_groups']} units (largest {res['largest_merged_group']}).",
        f"- EMI-field score on the {c['marked_units']} marked units: AUC {c['auc']:.3f} ({c['field_units']} field units against {c['outside_units']} others); bar {bar:.4f} "
        f"keeps {c['field_units_kept']} of {c['field_units']} field units and {c['outside_units_kept']} of {c['outside_units']} others; "
        f"{'the screen drops' if emi_drops else 'AUC below 0.8: the screen only flags'}. AUC on OTH's own offers ({c['oth_emi_offers']} EMI against {c['other_oth_offers']} others): {c['auc_on_oth_offers']:.3f}.",
        f"- Dropped (a unit can have several reasons): {res['dropped']}; for one reason only: {res['dropped_for_one_reason_only']}.",
        f"- Primary list: {len(prim)} units of {res['primary_types']} types in {res['primary_candidates']} candidates (hash {hashes['primary']}); stress list: {len(lists['stress'])} units (hash {hashes['stress']}).",
        f"- On the primary list: {res['primary_flags']}.",
        "- Competition counts are similar offers by content (assigned offers of the type plus offers inside its radius, each institution and cleaned title once, without OTH "
        "and without distance learning); they are not validated until the check of 100 offers is marked.", "",
        "## Primary list", "", md_table(cut(prim[show])), "", "## Every unit with its reasons", "", md_table(cut(s[full]))]) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False), flush=True)


# -------------------------------------------------------------------------------------------------------- sheet

def sheet() -> None:
    """Rule screen.competition.validity_check: 10 units of the primary list with at least 5 similar offers inside the
    radius; for each the 5 farthest similar offers inside the radius and the 5 nearest supply offers of that level outside
    it; shuffled, without the side. The unit is described by the 5 titles nearest its centroid; an offer with one of
    these titles is not shown."""
    stamp = run_stamp()
    if SHEET.exists() and pd.read_csv(SHEET, keep_default_na=False).iloc[:, -1].astype(str).str.strip().ne("").any():
        raise SystemExit(f"{SHEET.name} already holds marks: it is not written again")
    d, t, emb, cent = load_step2()
    res = json.loads(STEP3.read_text(encoding="utf-8"))
    prim = pd.read_csv(PRIMARY)
    if sha(PRIMARY) != res["files"][PRIMARY.name]:
        raise SystemExit("the primary list is not the one the run wrote")
    prim["level"] = pd.Categorical(prim["level"], LEVELS, ordered=True)
    prim = prim.sort_values(["type", "level"]).reset_index(drop=True)
    dist = 1 - emb @ cent.T
    first = ~d.duplicated(["institution", "clean_title", "level"]).to_numpy()
    supply = (~d["is_oth"] & ~d["distance_only"]).to_numpy(bool) & first
    title = d["clean_title"].to_numpy()
    parts = {}
    for k in range(len(prim)):
        c, lv = int(prim.at[k, "type"]), str(prim.at[k, "level"])
        members = np.where(d["type"].to_numpy() == c)[0]
        shown = list(dict.fromkeys(title[members[np.argsort(dist[members, c], kind="stable")]]))[:5]
        pool = supply & (d["level"] == lv).to_numpy() & ~np.isin(title, shown)
        inside = np.where(pool & (dist[:, c] <= t.at[c, "radius_90"]))[0]
        outside = np.where(pool & (dist[:, c] > t.at[c, "radius_90"]))[0]
        parts[k] = (shown, inside[np.argsort(-dist[inside, c], kind="stable")[:5]], outside[np.argsort(dist[outside, c], kind="stable")[:5]])
    rng = np.random.default_rng(42)
    usable = [k for k in range(len(prim)) if len(parts[k][1]) == 5 and len(parts[k][2]) == 5]
    pick = np.sort(rng.choice(usable, 10, replace=False))
    rows = []
    for k in pick:
        c, lv = int(prim.at[k, "type"]), str(prim.at[k, "level"])
        shown, far, near = parts[k]
        for side, idx in (("inside", far), ("outside", near)):
            rows += [{"type": c, "level": lv, "the kind of programme (5 typical titles)": "; ".join(shown), "offer": d.at[i, "title"],
                      "institution": d.at[i, "institution"], "side": side, "distance": float(dist[i, c]), "radius": float(t.at[c, "radius_90"])} for i in idx]
    key = pd.DataFrame(rows).iloc[rng.permutation(len(rows))].reset_index(drop=True)
    key.insert(0, "row", range(1, len(key) + 1))
    key.to_csv(KEY, index=False)
    out = key[["row", "level", "the kind of programme (5 typical titles)", "offer", "institution"]].copy()
    out["same kind of programme? (yes/no)"] = ""
    out.to_csv(SHEET, index=False, encoding="utf-8-sig")
    print(f"{len(out)} offers of {len(pick)} units ({len(usable)} of {len(prim)} units can be drawn) written to {SHEET.relative_to(REPO_ROOT)} (commit {stamp['commit']}, list {res['hashes']['primary']})")


if __name__ == "__main__":
    {"items": items, "labels": labels, "run": run, "sheet": sheet}[sys.argv[1]]()
