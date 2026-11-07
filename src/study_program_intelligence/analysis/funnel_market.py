"""Funnel steps 4-6: are students coming, are there jobs nearby, how many would be new to OTH? (configs/funnel.yaml)

Run from the repository root, after analysis.funnel_screen:

    python -m study_program_intelligence.analysis.funnel_market labour     # job-ad counts, about 30 minutes
    python -m study_program_intelligence.analysis.funnel_market score      # demand, capture, pre-gate score

Candidates come only from the frozen list. Keywords come from each type's terms by script. Capture reuses the Huff
model of analysis/options.py with the type's offers as competitors; the level comes from Destatis first-years per offer.
Outputs: data/interim/funnel_market.csv, funnel_labour.csv, funnel_anchor_check.csv; reports/funnel/step4_6_market.md.
"""

from __future__ import annotations

import json
import re
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from study_program_intelligence.ingest import jobsuche as J

from .capture import RAMP
from .catchment import counties
from .demand_split import load as load_destatis
from .forecast import backtest
from .funnel_discovery import _md
from .funnel_screen import own_mase, pool_series, pool_weights, slope_pct
from .funnel_subject_map import clean_label
from .options import AMBERG, NEW, OTH, WEIDEN, origins, run

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG = REPO_ROOT / "configs" / "funnel.yaml"
ANALYSIS = REPO_ROOT / "configs" / "analysis.yaml"
SUBJECT_MAP = REPO_ROOT / "configs" / "funnel_subject_map.csv"
INTERIM = REPO_ROOT / "data" / "interim"
RAW = REPO_ROOT / "data" / "raw" / "jobsuche"
LABOUR = INTERIM / "funnel_labour.csv"
OUT = INTERIM / "funnel_market.csv"
CHECK = INTERIM / "funnel_anchor_check.csv"
REPORT = REPO_ROOT / "reports" / "funnel" / "step4_6_market.md"
STOP = set("lehramt studium studiengang fach fächer schulen sekundarstufe grundschulen wissenschaft wissenschaften management "
           "angewandte international international business".split())
TEACHER = re.compile(r"lehramt|schulen|staatsexamen|grundschul|sekundarstufe|sonderpäd", re.I)
BETA, W = 1.6, {"low": 1.0, "central": 0.5, "high": 0.25}   # low = most taken from OTH
# published intakes for the validation of the anchor (configs/intake_benchmark_documents.yaml, evidence_capture.md)
PUBLISHED = {"THI Cybersicherheit (capacity)": 25, "TH Deggendorf Cyber Security (one student review)": 60,
             "Saarland Cybersicherheit WS 2024/25": 44, "Saarland Cybersicherheit WS 2025/26": 42,
             "Ruhr-Universität Bochum IT-Sicherheit 2024": 156}


def config() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def candidates() -> pd.DataFrame:
    c = pd.read_csv(INTERIM / "funnel_candidates.csv")
    offers = pd.read_csv(INTERIM / "funnel_offers.csv", low_memory=False)
    share = (offers[offers["assigned_type"] >= 0].assign(t=lambda d: (d["title"].fillna("") + " " + d["subjects"].fillna("")).str.contains(TEACHER))
             .groupby(["assigned_type", "level"])["t"].mean())
    c["teacher share"] = [share.get((r.type, r.level), 0.0) for r in c.itertuples()]
    return c


def keywords(c: pd.DataFrame) -> pd.DataFrame:
    terms = pd.read_csv(INTERIM / "funnel_types.csv").set_index("type")["terms"]
    rows = []
    for r in c[["type", "level"]].drop_duplicates().itertuples():
        out = []
        for term in str(terms.get(r.type, "")).split("; "):
            w = term.split()
            if not term or term.lower() in STOP or (len(w) == 2 and w[0] == w[1]) or (len(w) == 1 and w[0] in STOP):
                continue
            if not any(term in o or o in term for o in out):
                out.append(term)
        rows.append({"type": r.type, "level": r.level, "keywords": "; ".join(out[:5])})
    return pd.DataFrame(rows)


def labour() -> None:
    cfg = yaml.safe_load(J.CONFIG.read_text(encoding="utf-8"))
    c = candidates()
    c = c[c["teacher share"] < 0.5]
    kw = keywords(c)
    terms = sorted({t for s in kw["keywords"] for t in s.split("; ") if t})
    wanted = [(t, "amberg_100km") for t in terms]
    first = {s.split("; ")[0] for s in kw["keywords"] if s}
    wanted += [(t, g) for t in sorted(first) for g in ("germany", "bayern")]
    regions = {r["id"]: r for r in cfg["regions"]}
    folder = RAW / f"funnel_{date.today().isoformat()}"
    folder.mkdir(parents=True, exist_ok=True)
    done = pd.read_csv(LABOUR).to_dict("records") if LABOUR.exists() else []
    seen = {(d["keyword"], d["region"]) for d in done if d.get("total") == d.get("total")}
    print(f"{len(wanted)} counts, {len(seen)} already done", flush=True)
    for t, g in wanted:
        if (t, g) in seen:
            continue
        reg = regions[g]
        params = {"was": t, "wo": reg.get("wo"), "umkreis": reg.get("umkreis"), "size": 1, "page": 1}
        try:
            res = J._get(cfg["endpoint"], params)
            res.raise_for_status()
            payload = res.json()
            total = J._total(payload)
            if total is None:
                raise RuntimeError("no total field")
            (folder / f"{abs(hash((t, g))) % 10**10}.json").write_text(json.dumps({"keyword": t, "region": g, "total": total}), encoding="utf-8")
            done.append({"keyword": t, "region": g, "total": total, "date": date.today().isoformat()})
        except Exception as e:
            print("ERROR", t, g, e, flush=True)
        time.sleep(J.DELAY_SECONDS)
        if len(done) % 50 == 0:
            pd.DataFrame(done).to_csv(LABOUR, index=False)
    pd.DataFrame(done).to_csv(LABOUR, index=False)
    kw.to_csv(INTERIM / "funnel_keywords.csv", index=False)
    print(f"{len(done)} counts written to {LABOUR}", flush=True)


def per_offer_anchor(offers: pd.DataFrame, smap: pd.Series, long: pd.DataFrame) -> dict:
    """Per Destatis code and level: the German pool of the last year per offer, offers counted fractionally."""
    o = offers[offers["subjects"].notna()].copy()
    rows = []
    for r in o[["level", "state", "subjects"]].itertuples():
        labels = [clean_label(x) for x in r.subjects.split("; ")]
        for x in labels:
            if x in smap.index:
                rows.append((r.level, r.state == "Bayern", smap[x], 1 / len(labels)))
    f = pd.DataFrame(rows, columns=["level", "by", "code", "w"])
    out = {}
    for level, kind, year, factor in (("bachelor", "first-years", 2024, 1.0), ("master", "graduates", 2025, 0.5)):
        for region, mask in (("BY", f["by"]), ("DE", pd.Series(True, index=f.index))):
            n = f[(f["level"] == level) & mask].groupby("code")["w"].sum()
            d = long[(long["kind"] == kind) & (long["region"] == region) & (long["nationality"] == "German") & (long["year"] == year)]
            pool = d.groupby("code")["value"].sum() * factor
            out[(level, region)] = (pool / n).replace([np.inf], np.nan).dropna()
    return out


def anchor_of(weights: dict, table: dict, level: str) -> tuple[float, bool]:
    by, de = table[(level, "BY")], table[(level, "DE")]
    val, flag = 0.0, False
    for code, w in weights.items():
        if code in by.index:
            val += w * by[code]
        elif code in de.index:
            val += w * de[code]
            flag = True
    return float(val), flag


def value(x: float, lo: float, hi: float, log: bool = False) -> float:
    if x != x:
        return float("nan")
    if log:
        x, lo, hi = np.log(max(x, 1)), np.log(lo), np.log(hi)
    return float(np.clip(1 + 4 * (x - lo) / (hi - lo), 1, 5))


def score() -> None:
    cfg = config()
    c = candidates()
    weights = yaml.safe_load(ANALYSIS.read_text(encoding="utf-8"))
    w = next(v for k, v in weights.items() if isinstance(v, dict) and "demand" in v)
    offers = pd.read_csv(INTERIM / "funnel_offers.csv", low_memory=False)
    smap = pd.read_csv(SUBJECT_MAP).set_index("label")["code"]
    long = load_destatis()
    table = per_offer_anchor(offers, smap, long)
    geo = counties()
    pools = {"bachelor": origins("robotics_bsc"), "master": origins("cyber_msc")}
    lab = pd.read_csv(LABOUR) if LABOUR.exists() else pd.DataFrame(columns=["keyword", "region", "total"])
    kw = keywords(c).set_index(["type", "level"])["keywords"]
    latest = lab.sort_values("date").drop_duplicates(["keyword", "region"], keep="last").set_index(["keyword", "region"])["total"] if len(lab) else pd.Series(dtype=float)
    total_by = long[(long["region"] == "BY") & (long["nationality"] == "German")]
    rows = []
    for r in c.itertuples():
        a = offers[(offers["assigned_type"] == r.type) & (offers["level"] == r.level)]
        comp = a[~a["is_oth"] & ~a["distance_only"]]
        sites = {f"{x.institution} ({x.city})": ([(x.lat, x.lon)], "d") for x in comp.dropna(subset=["lat", "lon"]).drop_duplicates(["institution", "city"]).itertuples()}
        by_sites = {f"{x.institution} ({x.city})" for x in comp[comp["state"] == "Bayern"].itertuples()}
        sites[OTH] = ([AMBERG], "w")
        new_locs = [AMBERG, WEIDEN] if r.level == "bachelor" else [AMBERG]
        res = {k: run("funnel", BETA, wv, sites, new_locs, pools[r.level], geo) for k, wv in W.items()}
        cen = res["central"]
        mean_by = float(np.mean([cen["demand"][s] for s in by_sites])) if by_sites else float("nan")
        scale = float(cen["demand"][NEW] / mean_by) if by_sites else 1.0
        wts = pool_weights(a, smap)
        anc, flag = anchor_of(wts, table, r.level)
        kind = "first-years" if r.level == "bachelor" else "graduates"
        last = 2024 if kind == "first-years" else 2025
        y_de = pool_series(wts, long, kind, "BY", "German")
        y_fo = pool_series(wts, long, kind, "BY", "foreign")
        total = total_by[total_by["kind"] == kind].groupby("year")["value"].sum()
        terms = [t for t in str(kw.get((r.type, r.level), "")).split("; ") if t]
        ads = max((latest.get((t, "amberg_100km"), np.nan) for t in terms), default=np.nan) if len(latest) else np.nan
        de_slope, fo_slope = slope_pct(y_de), slope_pct(y_fo)
        rows.append({"type": r.type, "level": r.level, "kind": r.kind, "central titles": c.loc[r.Index, "central titles"],
                     "offers": r.offers, "within 100 km": c.loc[r.Index, "within 100 km"], "within 150 km": c.loc[r.Index, "within 150 km"],
                     "teacher share": round(c.loc[r.Index, "teacher share"], 2),
                     "emi score": c.loc[r.Index, "emi score"], "method-dependent": c.loc[r.Index, "method-dependent"],
                     "pool": c.loc[r.Index, "pool"], "German %/yr": round(de_slope, 2), "foreign %/yr": round(fo_slope, 2),
                     "German pool last": round(float(y_de.get(last, np.nan)), 0), "foreign pool last": round(float(y_fo.get(last, np.nan)), 0),
                     "own MASE": round(own_mase(y_de, total, last), 2), "anchor per offer": round(anc, 1), "anchor from Germany": flag,
                     "Bavarian sites": len(by_sites), "Huff scale": round(scale, 3),
                     "share from OTH low": round(res["low"]["a"], 3), "share from OTH central": round(cen["a"], 3),
                     "share from OTH high": round(res["high"]["a"], 3), "kept in region share": round(cen["c"], 3),
                     "keywords": "; ".join(terms), "ads within 100 km": ads})
    m = pd.DataFrame(rows)

    # validation of the level against the published intakes, on the types holding those programmes
    cyber = m[m["central titles"].str.contains("Cyber", na=False) & (m["level"] == "bachelor")]
    base = float(cyber["anchor per offer"].median()) if len(cyber) else float("nan")
    chk = pd.DataFrame([{"programme": k, "published": v, "anchor": base, "log error": round(abs(np.log(v / base)), 3)} for k, v in PUBLISHED.items()])
    med = float(chk["log error"].median())
    shrink = float(np.median([v / base for v in PUBLISHED.values()])) if med > np.log(1.5) else 1.0
    chk.to_csv(CHECK, index=False)

    rng = cfg["capture"]["range"]
    m["gross central"] = (m["anchor per offer"] * m["Huff scale"] * shrink).round(1)
    m["gross low"] = (m["gross central"] * rng["low"]).round(1)
    m["gross high"] = (m["gross central"] * rng["high"]).round(1)
    m["net new central"] = (m["gross central"] * (1 - m["share from OTH central"])).round(1)
    m["net new low"] = (m["gross low"] * (1 - m["share from OTH low"])).round(1)
    m["net new high"] = (m["gross high"] * (1 - m["share from OTH high"])).round(1)
    m["year 1 central"] = (m["gross central"] * RAMP[0]).round(1)
    mc = cfg["capture"]["min_cohort"]["value"]
    m["excluded (teacher training)"] = m["teacher share"] >= 0.5
    m["meets min cohort"] = m["gross central"] >= mc

    # pre-gate score (shortlist rule): fit replaced by the EMI score, feasibility left out, weights renormalised
    emi_top = float(pd.read_csv(INTERIM / "funnel_emi_calibration.csv").query("emi")["score"].quantile(0.9))
    bar = float(cfg_bar())
    m["v trend"] = m["German %/yr"].map(lambda x: value(x, -3, 3))
    m["v net new"] = m["net new central"].map(lambda x: value(x, 10, 40))
    m["v demand"] = (m["v trend"].fillna(3) + m["v net new"]) / 2
    m["v labour"] = m["ads within 100 km"].map(lambda x: value(x, 10, 150, log=True))
    m["v fit proxy"] = m["emi score"].map(lambda x: value(x, bar, emi_top))
    m["v differentiation"] = m["within 150 km"].map(lambda x: value(x, 10, 0))
    m["v regional"] = m["kept in region share"].map(lambda x: value(x, 0.0, 0.4))
    parts = {"v demand": w["demand"], "v labour": w["labour"], "v fit proxy": w["fit"], "v differentiation": w["differentiation"], "v regional": w["regional"]}
    tot = sum(parts.values())
    m["pre-gate score"] = sum(m[k].fillna(1) * v for k, v in parts.items()) / tot
    m = m.sort_values(["pre-gate score"], ascending=False)
    m.to_csv(OUT, index=False)
    ok = m[~m["excluded (teacher training)"] & m["meets min cohort"]]
    show = ["type", "level", "central titles", "offers", "within 100 km", "German %/yr", "own MASE", "gross low", "gross central", "gross high", "share from OTH central", "net new central", "ads within 100 km", "pre-gate score"]
    REPORT.write_text("\n".join([
        "# Funnel steps 4-6: demand, jobs, capture (generated)", "",
        f"Candidates {len(m)}; teacher training excluded {int(m['excluded (teacher training)'].sum())}; below the minimum cohort of {mc}: {int((~m['meets min cohort'] & ~m['excluded (teacher training)']).sum())}; ranked {len(ok)}.",
        f"Anchor check on the cyber types: anchor {base:.1f} first-years per offer; median absolute log error {med:.3f} (limit {np.log(1.5):.3f}); shrink factor applied {shrink:.2f}.", "",
        _md(chk), "", "## Ranked candidates, by pre-gate score", "", _md(ok[show].round(2).head(60))]) + "\n", encoding="utf-8")
    print(f"candidates {len(m)}, teacher {int(m['excluded (teacher training)'].sum())}, ranked {len(ok)}; anchor {base:.1f}, log err {med:.3f}, shrink {shrink:.2f}. Written: {REPORT}")


def cfg_bar() -> float:
    txt = (REPO_ROOT / "reports" / "funnel" / "step3_screen.md").read_text(encoding="utf-8")
    return float(re.search(r"bar (\d\.\d+)", txt).group(1))


if __name__ == "__main__":
    {"labour": labour, "score": score}[sys.argv[1]]()
