"""Funnel step 3: which units stay, and how much competition do they have? (configs/funnel.yaml: definitions,
pool_mapping, screen, freeze; criteria in docs/criteria_funnel_step3.md)

Run from the repository root, each command from committed code on a clean tree, after analysis.funnel_types:

    python -m study_program_intelligence.analysis.funnel_units items    # vectors of every title and focus item
    python -m study_program_intelligence.analysis.funnel_units run      # screens, competition, regional gap, frozen lists
    python -m study_program_intelligence.analysis.funnel_units sheet    # the 100 offers of the validity check, for Soma

A unit is a type x level with assigned offers at 2 or more institutions. Every unit gets the same four screens (already
at OTH, teacher training, falling validated trend, outside EMI's field); competition and the regional gap are measured
and never used as a cut. Nothing is added or removed by hand.
Outputs: data/interim/funnel2_item_vectors.npy, funnel2_item_index.csv, funnel2_screen.csv, funnel2_candidates.csv,
funnel2_candidates_stress.csv, funnel2_emi_calibration.csv, funnel2_step3.json, funnel2_similarity_key.csv;
reports/funnel2/step3_screen.md, step3_coherence_sample.md; docs/funnel_similarity_check.csv (the sheet).
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
from .funnel_types import CENTROIDS, EMB, OFFER_TYPES, RESULT, SEP, TYPES, normalise, sha

SUBJECT_MAP = REPO_ROOT / "configs" / "funnel_subject_map.csv"
PORTFOLIO = REPO_ROOT / "configs" / "oth_portfolio.yaml"
DESTATIS = REPO_ROOT / "data" / "raw" / "destatis"
MODULES = INTERIM / "modules_emi_2026.csv"
ITEM_VEC, ITEM_INDEX = INTERIM / "funnel2_item_vectors.npy", INTERIM / "funnel2_item_index.csv"
SCREEN, PRIMARY, STRESS = INTERIM / "funnel2_screen.csv", INTERIM / "funnel2_candidates.csv", INTERIM / "funnel2_candidates_stress.csv"
CALIBRATION, STEP3 = INTERIM / "funnel2_emi_calibration.csv", INTERIM / "funnel2_step3.json"
KEY, SHEET = INTERIM / "funnel2_similarity_key.csv", REPO_ROOT / "docs" / "funnel_similarity_check.csv"
MODEL = "intfloat/multilingual-e5-base"
LEVELS = ("bachelor", "master")
SERIES = {"bachelor": ("first-years", 2019, 2024), "master": ("graduates", 2019, 2025)}    # screen.trend: kind, window
LAND = {"Schleswig-Holstein": "SH", "Hamburg": "HH", "Niedersachsen": "NI", "Bremen": "HB", "Nordrhein-Westfalen": "NW", "Hessen": "HE",
        "Rheinland-Pfalz": "RP", "Baden-Württemberg": "BW", "Bayern": "BY", "Saarland": "SL", "Berlin": "BE", "Brandenburg": "BB",
        "Mecklenburg-Vorpommern": "MV", "Sachsen": "SN", "Sachsen-Anhalt": "ST", "Thüringen": "TH"}
# handbook set of each EMI programme, to leave a programme's own modules out of its calibration score (screen.emi_domain)
HANDBOOK = {"digital design": "ba_dd", "elektro und informationstechnik": "ba_ei", "geoinformatik": "ba_gi", "industrie 4 0 informatik": "ba_ii",
            "kuenstliche intelligenz": "ki", "medieninformatik": "ba_mi", "medientechnik und medienproduktion": "ma_mp",
            "medienproduktion und medientechnik": "ba_mt", "applied research": "ma_mapr", "educational technology": "ma_edu",
            "it und automation": "ma_ia", "artificial intelligence": "ma_mai"}


def plain(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", normalise(s)).strip()


# ------------------------------------------------------------------------------------------------------- items

def offer_items(d: pd.DataFrame) -> list[list[str]]:
    """Per offer: its cleaned title and its focus items (rule screen.emi_domain.offer_score)."""
    return [[t, *(f.split(SEP) if isinstance(f, str) and f else [])] for t, f in zip(d["clean_title"], d["focus_text"])]


def items() -> None:
    stamp = run_stamp()
    d = pd.read_csv(OFFER_TYPES, low_memory=False, dtype={"programme_id": str})
    uniq = sorted({x for lst in offer_items(d) for x in lst if isinstance(x, str) and x})
    from sentence_transformers import SentenceTransformer
    v = SentenceTransformer(MODEL).encode([f"query: {t}" for t in uniq], normalize_embeddings=True, batch_size=128, show_progress_bar=False)
    np.save(ITEM_VEC, v.astype(np.float32))
    pd.DataFrame({"item": uniq}).to_csv(ITEM_INDEX, index=False)
    (INTERIM / "funnel2_items.json").write_text(json.dumps({"stamp": stamp, "items": len(uniq), "offer_types": sha(OFFER_TYPES),
                                                           "files": {ITEM_VEC.name: sha(ITEM_VEC), ITEM_INDEX.name: sha(ITEM_INDEX)}}, indent=2) + "\n", encoding="utf-8")
    print(f"{len(uniq)} distinct titles and focus items encoded. Written: {ITEM_VEC.name}")


# ------------------------------------------------------------------------------------------------- definitions

def units_of(d: pd.DataFrame) -> pd.DataFrame:
    """Rule definitions.unit: a type x level with assigned offers of that level at 2 or more institutions."""
    a = d[d["assigned_type"] >= 0]
    u = a.groupby(["assigned_type", "level"]).agg(offers=("title", "size"), institutions=("institution", "nunique")).reset_index()
    u = u[u["institutions"] >= 2].rename(columns={"assigned_type": "type"})
    u["level"] = pd.Categorical(u["level"], LEVELS, ordered=True)
    return u.sort_values(["type", "level"]).reset_index(drop=True)


def merged_groups(units: pd.DataFrame, cent: np.ndarray, radius: np.ndarray) -> np.ndarray:
    """Rule definitions.merged_candidates: units of one level whose centroids each lie inside the other's radius_90 form
    one group (connected groups). Returns, for every unit, the lowest type number of its group."""
    dist = 1 - cent @ cent.T
    group = units["type"].to_numpy().copy()
    for lv in LEVELS:
        idx = np.where(units["level"] == lv)[0]
        t = units["type"].to_numpy()[idx]
        link = (dist[np.ix_(t, t)] <= radius[t][:, None]) & (dist[np.ix_(t, t)] <= radius[t][None, :])
        parent = list(range(len(t)))

        def find(i: int) -> int:
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i
        for i, j in zip(*np.where(np.triu(link, 1))):
            a, b = find(i), find(j)
            if a != b:
                parent[max(a, b)] = min(a, b)
        group[idx] = [t[find(i)] for i in range(len(t))]
    return group


# ------------------------------------------------------------------------------------------------------ screens

def teacher_share(a: pd.DataFrame, pattern: str) -> float:
    """Rule screen.teacher_training.share: share of the offers whose normalised title, degree or subject labels match."""
    text = (a["title"].fillna("") + " " + a["degree"].fillna("") + " " + a["subjects"].fillna("")).map(normalise)
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
    the drift model (scaled by the mean absolute yearly change of the training years). The series is the longest run of
    consecutive years ending in `last`; with fewer than min_series years it is not backtested and not validated."""
    y = y[y.index <= last].dropna().sort_index()
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
    """Weighted sum over the pool's subjects; a subject missing in a year counts as 0."""
    cols = [c for c in w if c in table.columns]
    return (table[cols].fillna(0.0) * pd.Series({c: w[c] for c in cols})).sum(axis=1) if cols else pd.Series(0.0, index=table.index)


def emi_positive(titles: pd.Series) -> pd.Series:
    names = [plain(p["name"]) for p in yaml.safe_load(PORTFOLIO.read_text(encoding="utf-8"))["programmes"]]
    return titles.map(lambda t: any(n in plain(t) for n in names))


def own_modules(title: str, modules: pd.DataFrame) -> np.ndarray:
    t = plain(title)
    for name, key in HANDBOOK.items():
        if name in t:
            return modules["programme_id"].str.contains(key, regex=False).to_numpy()
    return np.zeros(len(modules), bool)


def youden(pos: np.ndarray, neg: np.ndarray) -> tuple[float, float]:
    """Cut with the largest true-positive rate minus false-positive rate (score >= cut counts as positive), and the AUC."""
    cuts = np.unique(np.concatenate([pos, neg]))
    j = [(pos >= c).mean() - (neg >= c).mean() for c in cuts]
    auc = float(np.mean([(p > neg).mean() + 0.5 * (p == neg).mean() for p in pos]))
    return float(cuts[int(np.argmax(j))]), auc


def quotient(n_by: int, n_de: int, p: float, pseudo: float) -> float:
    """Rule screen.regional_gap.bavarian_quotient: a location quotient shrunk towards 1 when offers are few."""
    return ((n_by + pseudo * p) / (n_de + pseudo)) / p


# ---------------------------------------------------------------------------------------------------------- run

def load_step2() -> tuple[pd.DataFrame, pd.DataFrame, np.ndarray, np.ndarray]:
    r = json.loads(RESULT.read_text(encoding="utf-8"))
    for p in (OFFER_TYPES, TYPES, EMB, CENTROIDS):
        if r["files"][p.name] != sha(p):
            raise SystemExit(f"{p.name} is not the file Step 2 wrote")
    d = pd.read_csv(OFFER_TYPES, low_memory=False, dtype={"programme_id": str})
    return d, pd.read_csv(TYPES), np.load(EMB).astype(np.float64), np.load(CENTROIDS).astype(np.float64)


def run() -> None:
    from .module_gaps import embed as embed_modules
    stamp, rules = run_stamp(), config()
    sc = rules["screen"]
    d, t, emb, cent = load_step2()
    meta = json.loads((INTERIM / "funnel2_items.json").read_text(encoding="utf-8"))
    if meta["offer_types"] != sha(OFFER_TYPES) or meta["files"] != {ITEM_VEC.name: sha(ITEM_VEC), ITEM_INDEX.name: sha(ITEM_INDEX)}:
        raise SystemExit("the item vectors do not belong to the current offers: run items again")
    item_pos = {x: i for i, x in enumerate(pd.read_csv(ITEM_INDEX, keep_default_na=False)["item"])}
    item_vec = np.load(ITEM_VEC).astype(np.float64)
    radius, median = t["radius_90"].to_numpy(), t["median distance"].to_numpy()
    r75, r95 = t["radius_75"].to_numpy(), t["radius_95"].to_numpy()
    dist = 1 - emb @ cent.T
    assigned, level = d["assigned_type"].to_numpy(), d["level"].to_numpy()
    oth = d["is_oth"].to_numpy(bool)
    supply = ~oth & ~d["distance_only"].to_numpy(bool)                         # universe.counted_as_supply
    land = d["state"].map(LAND).fillna("").to_numpy()       # an offer without a Land or coordinates counts for Germany only
    km = d["km_amberg"].to_numpy()                          # a missing distance is within no distance
    south = np.isin(land, [LAND[x] for x in ("Bayern", "Baden-Württemberg")])
    bavaria = land == "BY"

    units = units_of(d)
    units["group"] = merged_groups(units, cent, radius)

    # EMI-field score of every offer: mean over its title and focus items of the highest cosine to any EMI module
    mods = pd.read_csv(MODULES, low_memory=False)
    mod_vec = embed_modules(mods["text"].fillna(mods["title"]).astype(str).tolist())
    item_lists = offer_items(d)
    best = item_vec @ mod_vec.T
    best_all = best.max(axis=1)
    score_all = np.array([float(np.mean([best_all[item_pos[x]] for x in lst])) for lst in item_lists])
    score_title = np.array([float(best_all[item_pos[lst[0]]]) for lst in item_lists])
    cal = d[oth & d["full_time"].to_numpy(bool)].copy()
    cal["emi"] = emi_positive(cal["title"])
    cal["score"] = [float(np.mean([best[item_pos[x]][~own_modules(title, mods)].max() for x in item_lists[i]])) if e else score_all[i]
                    for i, title, e in zip(cal.index, cal["title"], cal["emi"])]
    pos, neg = cal.loc[cal["emi"], "score"].to_numpy(), cal.loc[~cal["emi"], "score"].to_numpy()
    bar, auc = youden(pos, neg)
    emi_drops = auc >= sc["emi_domain"]["if_auc_below"]["auc"]
    cal[["title", "degree", "city", "emi", "score"]].sort_values("score", ascending=False).to_csv(CALIBRATION, index=False)

    smap = pd.read_csv(SUBJECT_MAP).set_index("label")["code"].to_dict()
    by, laender = destatis_bavaria(), destatis_laender()
    pattern, tt_line = sc["teacher_training"]["pattern"], sc["teacher_training"]["drop_if_at_least"]
    trend_line, pseudo = sc["trend"]["drop_if_below"], 5.0
    p_by = {lv: float((bavaria & supply & (level == lv)).sum() / (supply & (level == lv)).sum()) for lv in LEVELS}
    similar_of: dict[tuple[int, str], np.ndarray] = {}
    rows = []
    for u in units.itertuples():
        c, lv = int(u.type), str(u.level)
        at_level = level == lv
        a = d[(assigned == c) & at_level]
        oth_near = np.where(oth & at_level & (dist[:, c] <= median[c]))[0]
        oth_assigned = d[(assigned == c) & at_level & oth]
        kind, y0, y1 = SERIES[lv]
        w = pool_weights(a, smap)
        y = pool_series(by.loc[kind], w)
        slope = slope_pct(y, y0, y1)
        bt = backtest(y, y1, rules["demand"])
        fo = a["has_focus"].to_numpy(bool)
        emi = float(score_all[a.index[fo]].mean()) if fo.any() else float(score_title[a.index].mean())
        sim = supply & at_level & ((assigned == c) | (dist[:, c] <= radius[c]))
        similar_of[(c, lv)] = sim
        n = {"de": int(sim.sum()), "by": int((sim & bavaria).sum()), "south": int((sim & south).sum()),
             "50": int((sim & (km <= 50)).sum()), "100": int((sim & (km <= 100)).sum()), "150": int((sim & (km <= 150)).sum())}
        other_laender = sorted(set(land[sim & ~south]) - {""})
        y_else = pool_series(laender.loc[other_laender].groupby("year").sum(), w) if other_laender else pd.Series(dtype=float)
        slope_else = slope_pct(y_else, 2019, 2024) if other_laender else float("nan")
        elsewhere = n["de"] - n["south"] >= 1
        rows.append({"type": c, "level": lv, "kind": t.at[c, "kind"], "group": int(u.group), "central titles": t.at[c, "central titles"],
                     "assigned offers": len(a), "institutions": int(u.institutions),
                     "OTH offer within the median distance": "; ".join(d["title"].to_numpy()[oth_near][:3]), "drop: at OTH": bool(len(oth_near)),
                     "OTH offers assigned": "; ".join(oth_assigned["title"].head(3)),
                     "teacher share": round(teacher_share(a, pattern), 3),
                     "pool": "; ".join(f"{k}:{v:.2f}" for k, v in sorted(w.items(), key=lambda kv: (-kv[1], kv[0]))[:4]), "pool subjects": len(w),
                     "trend %/yr": slope, "backtest years": bt["years"], "MASE naive": bt["naive"], "MASE drift": bt["drift"], "trend validated": bt["validated"],
                     "emi score": emi, "emi score from": "offers with focus items" if fo.any() else "titles only",
                     "similar offers": n["de"], "similar in Bavaria": n["by"], "similar in the south": n["south"],
                     "similar within 50 km": n["50"], "similar within 100 km": n["100"], "similar within 150 km": n["150"],
                     "similar within 150 km (radius 75)": int((supply & at_level & ((assigned == c) | (dist[:, c] <= r75[c])) & (km <= 150)).sum()),
                     "similar within 150 km (radius 95)": int((supply & at_level & ((assigned == c) | (dist[:, c] <= r95[c])) & (km <= 150)).sum()),
                     "exists elsewhere": bool(elsewhere), "absent flag": bool(elsewhere and n["by"] == 0), "gap flag": bool(elsewhere and n["150"] == 0 and n["south"] == 0),
                     "bavarian quotient": quotient(n["by"], n["de"], p_by[lv], pseudo) if n["de"] >= 5 else np.nan,
                     "Laender elsewhere with a similar offer": len(other_laender), "trend elsewhere %/yr": slope_else,
                     "popularity tier": 2 if (elsewhere and slope_else >= 0) else 3,
                     "method-dependent": t.at[c, "method-dependent"], "evidence flag": t.at[c, "evidence flag"] if isinstance(t.at[c, "evidence flag"], str) else ""})
    s = pd.DataFrame(rows)
    s["drop: teacher training"] = s["teacher share"] >= tt_line
    s["drop: trend"] = (s["trend %/yr"] < trend_line) & s["trend validated"]
    s["outside EMI"] = s["emi score"] < bar
    s["drop: outside EMI"] = s["outside EMI"] & emi_drops
    at_oth_groups = s.loc[s["drop: at OTH"]].groupby("level")["group"].agg(set).to_dict()
    s["drop: at OTH via merged group"] = [(not own) and g in at_oth_groups.get(lv, set()) for own, g, lv in zip(s["drop: at OTH"], s["group"], s["level"])]
    s["at OTH (own or group)"] = s["drop: at OTH"] | s["drop: at OTH via merged group"]
    for (lv, g), part in s.groupby(["level", "group"]):                        # competition of the merged group: union over its units
        union = np.any([similar_of[(int(c), lv)] for c in part["type"]], axis=0)
        s.loc[part.index, "group size"] = len(part)
        s.loc[part.index, "group: similar offers"] = int(union.sum())
        s.loc[part.index, "group: similar within 150 km"] = int((union & (km <= 150)).sum())
    reasons = {"at OTH (own or group)": "already at OTH", "drop: teacher training": "teacher training", "drop: trend": "falling validated trend", "drop: outside EMI": "outside EMI's field"}
    s["reasons"] = [" | ".join(v for k, v in reasons.items() if r[k]) or "-" for r in s.to_dict("records")]
    s["primary"] = s["reasons"] == "-"
    s["stress"] = ~s["at OTH (own or group)"]
    s.to_csv(SCREEN, index=False)
    lists = {"primary": s[s["primary"]], "stress": s[s["stress"]]}
    lists["primary"].to_csv(PRIMARY, index=False)
    lists["stress"].to_csv(STRESS, index=False)
    hashes = {k: hashlib.sha256("\n".join(f"{r.type}:{r.level}" for r in v.itertuples()).encode()).hexdigest()[:16] for k, v in lists.items()}

    # sample for the coherence reading: every type with a unit on the primary list (screen.type_coherence)
    lines = ["# Funnel step 3: types to read for coherence (generated)", "",
             "Question per type: are at least 80 % of the titles shown the same kind of programme (same subject, same kind of qualification)?", ""]
    for c in sorted(lists["primary"]["type"].unique()):
        m = d[d["type"] == c]
        take = m.iloc[np.sort(np.random.default_rng(42).choice(len(m), min(10, len(m)), replace=False))]
        lines += [f"### Type {int(c)} ({len(m)} members)", ""] + [f"- {x} ({i})" for x, i in zip(take["title"], take["institution"])] + [""]
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "step3_coherence_sample.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    count = lambda col, sub=s: int(sub[col].sum())
    tally = lambda col: {str(k): int(v) for k, v in col.value_counts().items()}
    prim = lists["primary"]
    res = {"stamp": stamp, "step2_commit": json.loads(RESULT.read_text(encoding="utf-8"))["stamp"]["commit"], "units": len(s), "types_with_a_unit": int(s["type"].nunique()),
           "units_by_level": tally(s["level"]), "merged_groups_with_more_than_one_unit": int((s.groupby(["level", "group"]).size() > 1).sum()),
           "largest_merged_group": int(s.groupby(["level", "group"]).size().max()),
           "calibration": {"positives": int(len(pos)), "negatives": int(len(neg)), "auc": round(auc, 3), "bar": round(bar, 4), "screen_drops": bool(emi_drops),
                           "p90_of_emi_offers": round(float(np.percentile(pos, 90)), 4)},
           "dropped": {"at OTH (own offer)": count("drop: at OTH"), "at OTH (via merged group)": count("drop: at OTH via merged group"),
                       "teacher training": count("drop: teacher training"), "falling validated trend": count("drop: trend"), "outside EMI's field": count("drop: outside EMI")},
           "flagged_outside_emi": count("outside EMI"), "units_with_a_validated_trend": count("trend validated"), "units_without_a_trend_value": int(s["trend %/yr"].isna().sum()),
           "primary": len(prim), "primary_types": int(prim["type"].nunique()), "primary_by_level": tally(prim["level"]),
           "primary_by_kind": tally(prim["kind"]), "stress": len(lists["stress"]), "hashes": hashes,
           "primary_flags": {"absent in Bavaria": count("absent flag", prim), "gap (none within 150 km and none in the south)": count("gap flag", prim),
                             "no similar offer within 150 km": int((prim["similar within 150 km"] == 0).sum()), "popularity tier 2": int((prim["popularity tier"] == 2).sum())},
           "offers_without_a_land": int((land == "").sum()), "offers_without_a_distance": int(np.isnan(km).sum()),
           "bavaria_share_of_offers": {k: round(v, 4) for k, v in p_by.items()}, "competition": "not validated yet (screen.competition.validity_check)",
           "files": {p.name: sha(p) for p in (OFFER_TYPES, TYPES, EMB, CENTROIDS, ITEM_VEC, SCREEN, PRIMARY, STRESS, CALIBRATION)}}
    STEP3.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    show = ["type", "level", "kind", "central titles", "assigned offers", "trend %/yr", "emi score", "similar offers", "similar in Bavaria",
            "similar within 150 km", "absent flag", "gap flag", "bavarian quotient", "popularity tier", "evidence flag"]
    full = ["type", "level", "central titles", "assigned offers", "teacher share", "trend %/yr", "trend validated", "emi score", "similar within 150 km", "reasons"]
    cut = lambda x: x.assign(**{"central titles": x["central titles"].str.slice(0, 90)}).round(3)
    (REPORTS / "step3_screen.md").write_text("\n".join([
        "# Funnel step 3: screen, competition and frozen lists (generated)", "",
        f"Code commit {stamp['commit']} (types: {res['step2_commit']}), run on {stamp['date']}, tracked files clean: {stamp['clean']}.", "",
        f"- Units tested: {len(s)} ({res['units_by_level']}) from {res['types_with_a_unit']} types; merged groups with more than one unit: "
        f"{res['merged_groups_with_more_than_one_unit']} (largest {res['largest_merged_group']}).",
        f"- EMI-field calibration: {len(pos)} EMI offers against {len(neg)} other OTH full-time offers, AUC {auc:.3f}, bar {bar:.4f}; "
        f"{'the screen drops' if emi_drops else 'AUC below 0.8: the screen only flags'}.",
        f"- Dropped (a unit can have several reasons): {res['dropped']}.",
        f"- Primary list: {len(prim)} units of {res['primary_types']} types (hash {hashes['primary']}); stress list: {len(lists['stress'])} units (hash {hashes['stress']}).",
        f"- On the primary list: {res['primary_flags']}.",
        "- Competition counts are similar offers by content (assigned offers of the type plus offers inside its radius, without OTH and without distance learning); "
        "they are not validated until the check of 100 offers is marked.", "",
        "## Primary list", "", md_table(cut(prim[show])), "", "## Every unit with its reasons", "", md_table(cut(s[full]))]) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False), flush=True)


# -------------------------------------------------------------------------------------------------------- sheet

def sheet() -> None:
    """Rule screen.competition.validity_check: 10 units of the primary list, for each the 5 farthest similar offers inside
    the radius and the 5 nearest offers of that level outside it; shuffled, without the side."""
    stamp = run_stamp()
    d, t, emb, cent = load_step2()
    prim = pd.read_csv(PRIMARY)
    prim["level"] = pd.Categorical(prim["level"], LEVELS, ordered=True)
    prim = prim.sort_values(["type", "level"]).reset_index(drop=True)
    rng = np.random.default_rng(42)
    pick = np.sort(rng.choice(len(prim), 10, replace=False))
    dist = 1 - emb @ cent.T
    supply = (~d["is_oth"] & ~d["distance_only"]).to_numpy(bool)
    rows = []
    for k in pick:
        c, lv = int(prim.at[k, "type"]), str(prim.at[k, "level"])
        pool = supply & (d["level"] == lv).to_numpy()
        inside = np.where(pool & (dist[:, c] <= t.at[c, "radius_90"]))[0]
        outside = np.where(pool & (dist[:, c] > t.at[c, "radius_90"]) & (d["assigned_type"] != c).to_numpy())[0]
        far = inside[np.argsort(-dist[inside, c], kind="stable")[:5]]
        near = outside[np.argsort(dist[outside, c], kind="stable")[:5]]
        for side, idx in (("inside", far), ("outside", near)):
            rows += [{"type": c, "level": lv, "the type (titles closest to its centre)": t.at[c, "central titles"], "offer": d.at[i, "title"],
                      "institution": d.at[i, "institution"], "side": side, "distance": float(dist[i, c]), "radius": float(t.at[c, "radius_90"])} for i in idx]
    key = pd.DataFrame(rows).iloc[rng.permutation(len(rows))].reset_index(drop=True)
    key.insert(0, "row", range(1, len(key) + 1))
    key.to_csv(KEY, index=False)
    out = key[["row", "level", "the type (titles closest to its centre)", "offer", "institution"]].copy()
    out["same kind of programme? (yes/no)"] = ""
    out.to_csv(SHEET, index=False, encoding="utf-8-sig")
    print(f"{len(out)} offers of {len(pick)} units written to {SHEET.relative_to(REPO_ROOT)} (commit {stamp['commit']}); key: {KEY.name}")


if __name__ == "__main__":
    {"items": items, "run": run, "sheet": sheet}[sys.argv[1]]()
