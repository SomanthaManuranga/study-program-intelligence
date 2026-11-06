"""Funnel step 3: which programme types are open to OTH and within EMI's field? (configs/funnel.yaml, screen and freeze)

Run from the repository root, after analysis.funnel_discovery:

    python -m study_program_intelligence.analysis.funnel_screen

Every type x level gets the same four tests: not already at OTH, room near OTH, pool not shrinking on a validated trend,
within EMI's field. Every result is kept with its reason (attrition table). Two lists are frozen and hashed: primary
(all screens) and stress (only the at-OTH screen).
Outputs: data/interim/funnel_screen.csv, funnel_candidates.csv, funnel_candidates_stress.csv, funnel_emi_calibration.csv,
reports/funnel/step3_screen.md.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import roc_auc_score, roc_curve

from .demand_split import load as load_destatis
from .forecast import backtest
from .funnel_discovery import _md, focus_items
from .funnel_subject_map import clean_label
from .module_gaps import embed as embed_chunks

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG = REPO_ROOT / "configs" / "funnel.yaml"
SUBJECT_MAP = REPO_ROOT / "configs" / "funnel_subject_map.csv"
PORTFOLIO = REPO_ROOT / "configs" / "oth_portfolio.yaml"
CATALOGUE = REPO_ROOT / "data" / "processed" / "programmes_full.csv"
INTERIM = REPO_ROOT / "data" / "interim"
MODULES = INTERIM / "modules_emi_2026.csv"
REPORT = REPO_ROOT / "reports" / "funnel" / "step3_screen.md"
MODEL = "intfloat/multilingual-e5-base"
WINDOW = (2019, 2024)
# handbook set per EMI programme name, for leaving a programme's own modules out of its calibration score
HANDBOOK_PREFIX = {"digital design": "ba_dd", "elektro und informationstechnik": "ba_ei", "geoinformatik": "ba_gi", "industrie 4 0 informatik": "ba_ii",
                   "kuenstliche intelligenz": "ki", "medieninformatik": "ba_mi", "medientechnik und medienproduktion": "ma_mp",
                   "medienproduktion und medientechnik": "ba_mt", "applied research": "ma_mapr", "educational technology": "ma_edu",
                   "it und automation": "ma_ia", "artificial intelligence": "ma_mai"}


def norm(s: str) -> str:
    s = str(s).lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def emi_flag(offers: pd.DataFrame) -> pd.Series:
    names = [norm(p["name"]) for p in yaml.safe_load(PORTFOLIO.read_text(encoding="utf-8"))["programmes"]]
    return offers["is_oth"] & offers["title"].map(lambda t: any(n in norm(t) for n in names))


def own_modules_mask(title: str, modules: pd.DataFrame) -> np.ndarray:
    """True for modules from the offer's own handbook (left out of its calibration score)."""
    t = norm(title)
    for name, key in HANDBOOK_PREFIX.items():
        if name in t:
            return modules["programme_id"].str.contains(key, regex=False).values
    return np.zeros(len(modules), dtype=bool)


def encode_items(items: list[str]) -> dict[str, np.ndarray]:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL)
    uniq = sorted(set(items))
    v = model.encode([f"query: {t}" for t in uniq], normalize_embeddings=True, batch_size=64, show_progress_bar=False)
    return dict(zip(uniq, v))


def offer_items(offers: pd.DataFrame, content: pd.Series) -> pd.Series:
    title = offers["title"].map(lambda t: re.sub(r"\s+(Bachelor|Master)\b.*$", "", str(t)).strip())
    return pd.Series([[t, *focus_items(content.get(pid))] for t, pid in zip(title, offers["programme_id"])], index=offers.index)


def emi_scores(offers: pd.DataFrame, items: pd.Series, vec: dict, mods: pd.DataFrame, mod_emb: np.ndarray, leave_out: bool) -> pd.Series:
    out = {}
    for i, r in offers.iterrows():
        if not items[i]:
            continue
        m = np.vstack([vec[x] for x in items[i]])
        use = ~own_modules_mask(r["title"], mods) if leave_out else np.ones(len(mods), dtype=bool)
        out[i] = float((m @ mod_emb[use].T).max(axis=1).mean())
    return pd.Series(out)


def pool_weights(offers: pd.DataFrame, smap: pd.Series) -> dict[str, float]:
    """Fractional weights of Destatis codes over a type's offers at one level."""
    w: dict[str, float] = {}
    for s in offers["subjects"].dropna():
        labels = [clean_label(x) for x in s.split("; ")]
        for x in labels:
            if x in smap.index:
                w[smap[x]] = w.get(smap[x], 0.0) + 1 / len(labels)
    tot = sum(w.values())
    return {k: v / tot for k, v in w.items()} if tot else {}


def pool_series(weights: dict, long: pd.DataFrame, kind: str, region: str, nat: str) -> pd.Series:
    d = long[(long["kind"] == kind) & (long["region"] == region) & (long["nationality"] == nat) & long["code"].isin(weights)]
    p = d.pivot_table(index="year", columns="code", values="value", aggfunc="sum").fillna(0.0)
    return sum(p[c] * w for c, w in weights.items() if c in p.columns) if len(p) else pd.Series(dtype=float)


def slope_pct(y: pd.Series, window=WINDOW) -> float:
    s = y[(y.index >= window[0]) & (y.index <= window[1])]
    s = s[s > 0]
    return float(100 * (np.exp(np.polyfit(s.index.astype(float), np.log(s.values), 1)[0]) - 1)) if len(s) >= 4 else float("nan")


def own_mase(y: pd.Series, total: pd.Series, last: int) -> float:
    y = y[y > 0]
    if len(y) < 12 or y.index.min() > 2008:
        return float("nan")
    bt = backtest(y, total, last)
    return float(bt[bt["model"] != "share (actual total)"].groupby("model")["ase"].mean().min())


def main() -> None:
    cfg = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
    sc = cfg["screen"]
    offers = pd.read_csv(INTERIM / "funnel_offers.csv", low_memory=False, dtype={"programme_id": str})
    types = pd.read_csv(INTERIM / "funnel_types.csv").rename(columns=lambda c: c.replace(" ", "_").replace("-", "_"))
    content = pd.read_csv(CATALOGUE, low_memory=False, dtype={"programme_id": str}).set_index("programme_id")["content"]
    content = content[~content.index.duplicated()]
    smap = pd.read_csv(SUBJECT_MAP).set_index("label")["code"]
    long = load_destatis()
    mods = pd.read_csv(MODULES, low_memory=False)
    mod_emb = embed_chunks(mods["text"].fillna(mods["title"]).astype(str).tolist())

    items = offer_items(offers, content)
    used = offers["assigned_type"] >= 0
    vec = encode_items([x for lst in items[used | offers["is_oth"]] for x in lst])

    # calibration of the EMI-domain score on OTH's own offers
    oth_ft = offers[offers["is_oth"] & offers["full_time"]].copy()
    oth_ft["emi"] = emi_flag(oth_ft)
    cal = emi_scores(oth_ft, items, vec, mods, mod_emb, leave_out=True)
    oth_ft["score"] = cal
    auc = roc_auc_score(oth_ft["emi"], oth_ft["score"])
    fpr, tpr, thr = roc_curve(oth_ft["emi"], oth_ft["score"])
    bar = float(thr[np.argmax(tpr - fpr)])
    use_emi_drop = auc >= sc["emi_domain"]["if_auc_below"]["auc"]
    oth_ft[["title", "degree", "emi", "score"]].sort_values("score", ascending=False).to_csv(INTERIM / "funnel_emi_calibration.csv", index=False)

    all_scores = emi_scores(offers[used], items, vec, mods, mod_emb, leave_out=False)
    offers["emi_score"] = all_scores
    oth_all = offers[offers["is_oth"]]
    total_by = long[(long["region"] == "BY") & (long["nationality"] == "German")]
    rows = []
    for t in types.itertuples():
        for level in ("bachelor", "master"):
            a = offers[(offers["assigned_type"] == t.type) & (offers["level"] == level)]
            if a.empty:
                continue
            comp = a[~a["is_oth"] & ~a["distance_only"]]
            near_oth = oth_all[(oth_all["type_nearest_any"] == t.type) & (oth_all["level"] == level)]
            close = near_oth[near_oth["dist_nearest_any"] <= t.median_distance]
            within100, within150 = int((comp["km_oth"] <= 100).sum()), int((comp["km_oth"] <= 150).sum())
            kind = "first-years" if level == "bachelor" else "graduates"
            w = pool_weights(a, smap)
            y = pool_series(w, long, kind, "BY", "German")
            sl = slope_pct(y)
            total = total_by[total_by["kind"] == kind].groupby("year")["value"].sum()
            shrinking = bool(sl < sc["trend"]["drop_if_below"]) if sl == sl else False
            mase = own_mase(y, total, 2024 if kind == "first-years" else 2025) if shrinking else float("nan")
            trend_drop = shrinking and mase == mase and mase < 1
            fo = a[a["has_focus"]]["emi_score"].dropna()
            emi = float(fo.mean()) if len(fo) else float(a["emi_score"].mean())
            emi_low = bool(emi < bar) if emi == emi else True
            reasons = []
            if len(close):
                reasons.append(f"at OTH: {close['title'].iloc[0]}")
            if within100 > sc["supply_gap"]["max_offers_within_100km"]:
                reasons.append(f"supply: {within100} offers within 100 km")
            if trend_drop:
                reasons.append(f"trend: German pool {sl:.1f} %/yr, validated (MASE {mase:.2f})")
            if emi_low and use_emi_drop:
                reasons.append(f"outside EMI: score {emi:.3f} below bar {bar:.3f}")
            rows.append({"type": t.type, "level": level, "kind": t.kind, "label": t.label, "central titles": t.central_titles,
                         "offers": len(a), "within 100 km": within100, "within 150 km": within150,
                         "OTH offers nearest": "; ".join(near_oth["title"].head(4)), "OTH offer close": bool(len(close)),
                         "pool": "; ".join(f"{k}:{v:.2f}" for k, v in sorted(w.items(), key=lambda kv: -kv[1])[:4]),
                         "German pool %/yr": round(sl, 2) if sl == sl else np.nan, "pool MASE": round(mase, 2) if mase == mase else np.nan,
                         "emi score": round(emi, 4) if emi == emi else np.nan, "emi low": emi_low,
                         "method-dependent": bool(t.method_dependent),
                         "passes": not reasons, "drop reasons": " | ".join(reasons) or "-"})
    s = pd.DataFrame(rows)
    s.to_csv(INTERIM / "funnel_screen.csv", index=False)
    primary = s[s["passes"]].sort_values(["level", "type"])
    stress = s[~s["OTH offer close"]].sort_values(["level", "type"])
    primary.to_csv(INTERIM / "funnel_candidates.csv", index=False)
    stress.to_csv(INTERIM / "funnel_candidates_stress.csv", index=False)
    h = {n: hashlib.sha256("\n".join(f"{r.type}:{r.level}" for r in d.itertuples()).encode()).hexdigest()[:16] for n, d in (("primary", primary), ("stress", stress))}
    REPORT.write_text("\n".join([
        "# Funnel step 3: screen and frozen candidate list (generated)", "",
        f"Calibration of the EMI-domain score: AUC {auc:.3f} on {int(oth_ft['emi'].sum())} EMI and {int((~oth_ft['emi']).sum())} other OTH full-time offers; bar {bar:.3f}; "
        f"{'the screen drops' if use_emi_drop else 'AUC below 0.8: the screen only flags'}.",
        f"Type x level tested: {len(s)}. Primary list: {len(primary)} (hash {h['primary']}). Stress list: {len(stress)} (hash {h['stress']}).", "",
        "## Attrition", "", f"- at OTH: {s['OTH offer close'].sum()}", f"- more than {sc['supply_gap']['max_offers_within_100km']} offers within 100 km: {s['drop reasons'].str.contains('supply:').sum()}",
        f"- validated falling trend: {s['drop reasons'].str.contains('trend:').sum()}", f"- outside EMI's field: {s['drop reasons'].str.contains('outside EMI').sum()}", "",
        "## Primary candidates", "", _md(primary[["type", "level", "kind", "label", "central titles", "offers", "within 100 km", "within 150 km", "German pool %/yr", "emi score", "method-dependent"]]), "",
        "## Every type x level with its reason", "", _md(s[["type", "level", "label", "offers", "within 100 km", "German pool %/yr", "pool MASE", "emi score", "passes", "drop reasons"]])]) + "\n", encoding="utf-8")
    print(f"AUC {auc:.3f}, bar {bar:.3f}; tested {len(s)}, primary {len(primary)} ({h['primary']}), stress {len(stress)} ({h['stress']}). Written: {REPORT}")


if __name__ == "__main__":
    main()
