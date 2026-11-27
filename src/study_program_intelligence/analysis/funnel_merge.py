"""Rules version 4, R1: one candidate per programme title (configs/funnel.yaml: version_4.title_merge,
version_4.new_to_oth_scenarios; criteria and exact readings in docs/criteria_funnel_v4_merge.md)

Run from the repository root, each command from committed code on a clean tree, after Steps 3 to 6 of version 3:

    python -m study_program_intelligence.analysis.funnel_merge keywords   # keywords of every merged candidate (deviation 1)
    (commit docs/funnel4_keywords.csv)
    python -m study_program_intelligence.analysis.funnel_merge fetch      # job-ad counts of keywords never counted
    python -m study_program_intelligence.analysis.funnel_merge run        # measures and both gate orders

Units of one level whose types share the same normalised main title become one candidate, together with their
complete-linkage partners (one hop). Every measure of the pre-gate score is computed again on the merged candidate:
pool, trend, competition, job ads, EMI-field score, first-years and students new to OTH. The result is the new gate
order. Nothing is edited by hand.
Job ads (version_4.deviations, first entry): a merged candidate's keywords come from the version-3 keyword rule applied
to the fitted members of all its types; the union of its types' keywords (the rule as written) is kept as a
sensitivity order.
Outputs: docs/funnel4_keywords.csv; data/interim/funnel4_job_counts.csv; data/interim/funnel4_units.csv (unit ->
candidate), funnel4_candidates.csv (one row per candidate with its measures), funnel4_gate_order.csv (primary),
funnel4_gate_order_as_written.csv, funnel4_merge.json; reports/funnel2/v4_merge.md.
"""

from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter

import numpy as np
import pandas as pd
import yaml

from .catchment import counties, haversine
from .funnel_capture import CAPTURE, HIGH, LOW, NEW_SITE, ORIGINS, TRANSITION, anchor_of, huff, pool_tables, sites_of
from .funnel_common import INTERIM, REPO_ROOT, REPORTS, config, md_table, run_stamp
from . import funnel_labour as labour
from .funnel_labour import COUNTS, KEYWORDS
from .funnel_shortlist import COHERENCE, LABOUR, ORDER as ORDER_V3, scores
from .funnel_types import OFFER_TYPES, clean_title, sha
from .funnel_units import (CALIBRATION, ITEM_INDEX, ITEM_VEC, LAND, LEVELS, MODULE_VEC, QUOTIENT_FROM, SCREEN, SERIES, SOUTH, STEP3, SUBJECT_MAP,
                           backtest, destatis_bavaria, destatis_laender, emi_offer_scores, gap_numbers, load_step2, module_titles, offer_items,
                           pool_series, pool_weights, slope_pct, subject_titles)
from .options import origins

UNITS4, CANDIDATES4, ORDER4, MERGE4 = (INTERIM / "funnel4_units.csv", INTERIM / "funnel4_candidates.csv", INTERIM / "funnel4_gate_order.csv",
                                       INTERIM / "funnel4_merge.json")
ORDER4_AS_WRITTEN = INTERIM / "funnel4_gate_order_as_written.csv"
KEYWORDS4, COUNTS4 = REPO_ROOT / "docs" / "funnel4_keywords.csv", INTERIM / "funnel4_job_counts.csv"
FIRST = 20                     # version_4.gate_breadth: the first 20 positions
CONTROL = "informatik"         # version_4.deviations, second entry: the Informatik bachelor is checked as a control


# ------------------------------------------------------------------------------------------------ normalisation

def normaliser(rule: dict):
    """version_4.title_merge.normalise as a function of a raw offer title."""
    translate = sorted(rule["translate"].items(), key=lambda kv: (-len(kv[0]), kv[0]))
    remove = set(rule["remove"])

    def norm(title: str) -> str:
        t = re.sub(r"\([^)]*\)|\[[^\]]*\]", " ", clean_title(title)).lower()      # round and square brackets
        for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
            t = t.replace(a, b)
        t = re.sub(r"elektro-\s*und\b", "elektrotechnik und", t)
        t = " " + " ".join(re.sub(r"[^a-z0-9 ]", " ", t).split()) + " "
        for a, b in translate:
            t = t.replace(f" {a} ", f" {b} ")
            t = t.replace(f" {a} ", f" {b} ")       # a phrase can follow itself ("informatik computer science computer science")
        return " ".join(sorted({w for w in t.split() if w not in remove}))
    return norm


def main_titles(d: pd.DataFrame, norm) -> pd.Series:
    """version_4.title_merge.main_title: per (type, level), the most frequent normalised title of its assigned offers of
    that level; ties by the alphabetically first."""
    a = d[d["assigned_type"] >= 0].assign(nt=lambda x: x["title"].map(norm))
    return a.groupby(["assigned_type", "level"])["nt"].agg(lambda x: sorted(Counter(x).items(), key=lambda kv: (-kv[1], kv[0]))[0][0])


# --------------------------------------------------------------------------------------------------- candidates

def candidates(units: pd.DataFrame) -> pd.DataFrame:
    """units: type, level, group (version 3 complete-linkage group), main, at_oth. Returns the units with "candidate"
    (lowest type number of the candidate), "how" and "dropped whole". Readings E1-E5 of docs/criteria_funnel_v4_merge.md."""
    out = units.copy()
    out["candidate"], out["how"], out["dropped whole"] = -1, "", False
    for lv in LEVELS:
        m = out["level"] == lv
        x = out[m]
        size = x.groupby("main")["type"].transform("size")
        matched = size >= 2                                                            # E1
        titles_at_oth = set(x.loc[matched & x["at_oth"], "main"])
        cand = pd.Series(-1, index=x.index)
        how = pd.Series("", index=x.index)
        for title, part in x[matched].groupby("main"):
            cand[part.index] = int(part["type"].min())
            how[part.index] = "title"
        for g, part in x.groupby("group"):
            free = part[~matched[part.index]]
            if free.empty:
                continue
            titles = set(x.loc[part.index[matched[part.index]], "main"])
            if len(titles) == 1 and not titles & titles_at_oth:                                                   # E2: one hop to one title group
                t = next(iter(titles))
                cand[free.index] = int(x.loc[matched & (x["main"] == t), "type"].min())
                how[free.index] = "partner"
                continue
            cand[free.index] = int(free["type"].min())                                                            # own candidate
            how[free.index] = ("version-3 group" if not titles else                                              # no title group in the version-3 group
                               "partner of two or more title groups" if len(titles) > 1 else                    # E3
                               "partner of a title group dropped at OTH")                                       # E5
        cand = cand.groupby(cand).transform(lambda g: int(x.loc[g.index, "type"].min()))      # E7: the lowest type number of all its units
        out.loc[x.index, "candidate"] = cand
        out.loc[x.index, "how"] = how
        out.loc[x.index, "dropped whole"] = matched & x["main"].isin(titles_at_oth)
    return out


# ------------------------------------------------------------------------------------------------- units, keywords

def build_units(d: pd.DataFrame, s: pd.DataFrame, v4: dict) -> pd.DataFrame:
    mt = main_titles(d, normaliser(v4["title_merge"]))
    u = s[["type", "level", "group", "primary", "drop: at OTH", "central titles"]].rename(columns={"drop: at OTH": "at_oth"})
    u["main"] = [mt[(c, lv)] for c, lv in zip(u["type"], u["level"])]
    u = candidates(u)
    assert (u["candidate"] >= 0).all() and len(u) == len(s)                             # M1
    mixed = pd.read_csv(COHERENCE).set_index("type")["mixed"].astype(bool)
    u["mixed type"] = u["type"].map(mixed).fillna(False).astype(bool)                   # version_4.deviations, third entry: leaves singly
    return u


def alive(u: pd.DataFrame) -> pd.DataFrame:
    """The units that count for their candidate: on the primary list, not dropped with a title group, not mixed."""
    return u[u["primary"] & ~u["dropped whole"] & ~u["mixed type"]]


def alive_parts(u: pd.DataFrame) -> dict:
    """(candidate, level) -> sorted surviving types, for the candidates on the list."""
    return {(int(c), str(lv)): sorted(int(x) for x in g["type"]) for (c, lv), g in alive(u).groupby(["candidate", "level"])}


def committed(path) -> bool:
    import subprocess
    rel = str(path.relative_to(REPO_ROOT))
    clean = not subprocess.run(["git", "status", "--porcelain", "--", rel], cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip()
    return clean and bool(subprocess.run(["git", "ls-files", rel], cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip())


def merged_keywords(d: pd.DataFrame, parts: dict) -> pd.DataFrame:
    """version_4.deviations, first entry: labour.keywords on the fitted members of all types of a candidate (members
    ordered by their distance to their type's centre, as version 3), with version 3's stop list and generic list."""
    _, info = labour.build_keywords(d)
    drop = labour.stoplist() | set(info["generic by the 5 % rule"])
    rows = []
    for (cid, lv), types in sorted(parts.items(), key=lambda kv: (kv[0][0], LEVELS.index(kv[0][1]))):
        m = d[d["type"].isin(types)].sort_values("dist_to_assigned", kind="stable")
        kws, how = labour.keywords_of(m["clean_title"].tolist(), m["clean_title"].iloc[0], drop)
        counts = dict(labour.ranked_phrases(m["clean_title"].tolist(), drop))
        for rank, k in enumerate(kws, 1):
            rows.append({"candidate": cid, "level": lv, "types": "; ".join(map(str, types)), "rank": rank, "keyword": k,
                         "member titles with it": counts.get(k, 1), "members": len(m), "from": how})
        if not kws:
            rows.append({"candidate": cid, "level": lv, "types": "; ".join(map(str, types)), "rank": 0, "keyword": "", "member titles with it": 0, "members": len(m), "from": "no keyword left"})
    return pd.DataFrame(rows)


def keywords() -> None:
    stamp, v4 = run_stamp(), config()["version_4"]
    d, _, _, _ = load_step2()
    k = merged_keywords(d, alive_parts(build_units(d, pd.read_csv(SCREEN, float_precision="round_trip"), v4)))
    k.to_csv(KEYWORDS4, index=False, lineterminator="\n")
    have = set(pd.read_csv(COUNTS, keep_default_na=False)["keyword"])
    real = k[k["rank"] > 0]
    print(json.dumps({"commit": stamp["commit"], "candidates": int(k.groupby(["candidate", "level"]).ngroups), "keyword rows": len(real),
                      "distinct keywords": int(real["keyword"].nunique()), "never counted": sorted(set(real["keyword"]) - have)}, indent=1, ensure_ascii=False))


def fetch() -> None:
    """Keywords of docs/funnel4_keywords.csv that were never counted: one request per keyword and region of
    labour.regions (ingest/jobsuche.py: robots.txt, User-Agent, 2 s), the reply's place checked as in Step 5."""
    from ..ingest.jobsuche import DELAY_SECONDS, _get, _total
    import hashlib
    from datetime import date
    stamp = run_stamp()
    if not committed(KEYWORDS4):
        raise SystemExit("docs/funnel4_keywords.csv must be committed before the first request")
    endpoint = yaml.safe_load((REPO_ROOT / "configs" / "jobsuche.yaml").read_text(encoding="utf-8"))["endpoint"]
    k = pd.read_csv(KEYWORDS4, keep_default_na=False)
    have = set(pd.read_csv(COUNTS, keep_default_na=False)["keyword"])
    old = pd.read_csv(COUNTS4, keep_default_na=False) if COUNTS4.exists() else pd.DataFrame(columns=["date", "keyword", "region", "total", "keywords_file", "commit"])
    today = date.today().isoformat()
    done = set(zip(old["keyword"], old["region"]))
    todo = [(w, r) for w in sorted(set(k.loc[k["rank"] > 0, "keyword"]) - have) for r in labour.REGIONS if (w, r) not in done]
    folder = labour.RAW / today
    folder.mkdir(parents=True, exist_ok=True)
    rows, errors = [], 0
    print(f"{len(todo)} requests", flush=True)
    for w, r in todo:
        try:
            resp = _get(endpoint, {"was": w, **labour.REGIONS[r], "angebotsart": 1, "page": 1, "size": 1})
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}")
            payload = resp.json()
            total = _total(payload)
            if total is None:
                raise RuntimeError("no total in the reply")
            if r == "amberg_100km":
                place = (payload.get("woOutput") or {}).get("koordinaten") or [{}]
                if abs(place[0].get("lat", 0) - labour.AMBERG[0]) > 0.05 or abs(place[0].get("lon", 0) - labour.AMBERG[1]) > 0.05:
                    raise RuntimeError(f"the reply is not centred on Amberg in der Oberpfalz: {payload.get('woOutput')}")
            (folder / f"{hashlib.sha256((w + '|' + r).encode()).hexdigest()[:16]}.json").write_text(json.dumps({"keyword": w, "region": r, "reply": payload}, ensure_ascii=False), encoding="utf-8")
            rows.append({"date": today, "keyword": w, "region": r, "total": int(total), "keywords_file": sha(KEYWORDS4), "commit": stamp["commit"]})
            print(f"{w!r} {r}: {total}", flush=True)
        except Exception as exc:
            errors += 1
            print(f"ERROR {w!r} {r}: {exc}", flush=True)
        time.sleep(DELAY_SECONDS)
    pd.concat([old, pd.DataFrame(rows)], ignore_index=True).to_csv(COUNTS4, index=False)
    print(f"{len(rows)} counts stored, {errors} errors", flush=True)


# ------------------------------------------------------------------------------------------------------------ run

def main() -> None:
    stamp, rules = run_stamp(), config()
    v4 = rules["version_4"]
    step3 = json.loads(STEP3.read_text(encoding="utf-8"))
    if step3["files"][SCREEN.name] != sha(SCREEN):
        raise SystemExit("the screen table is not the one Step 3 wrote")
    d, t, emb, cent = load_step2()
    s = pd.read_csv(SCREEN, float_precision="round_trip")
    cap3 = pd.read_csv(CAPTURE, float_precision="round_trip").set_index(["type", "level"])
    u = build_units(d, s, v4)
    u.to_csv(UNITS4, index=False)
    k4 = pd.read_csv(KEYWORDS4, keep_default_na=False)
    if not committed(KEYWORDS4) or set(zip(k4["candidate"], k4["level"])) != set(alive_parts(u).keys()):
        raise SystemExit("docs/funnel4_keywords.csv is not committed or does not belong to these candidates: run keywords and commit")

    # shared inputs (as Steps 3 to 6)
    smap = pd.read_csv(SUBJECT_MAP).set_index("label")["code"].to_dict()
    by, laender = destatis_bavaria(), destatis_laender()
    radius = t["radius_90"].to_numpy()
    dist = 1 - emb @ cent.T
    assigned, level = d["assigned_type"].to_numpy(), d["level"].to_numpy()
    oth, distance = d["is_oth"].to_numpy(bool), d["distance_only"].to_numpy(bool)
    land = d["state"].map(LAND).fillna("").to_numpy()
    km = d["km_amberg"].to_numpy()
    key = pd.factorize(d["institution"].astype(str) + "\x1f" + d["clean_title"].astype(str))[0]
    supply, far_supply = ~oth & ~distance, ~oth & distance
    p_by = {lv: float(((land == "BY") & (level == lv)).sum() / (level == lv).sum()) for lv in LEVELS}
    item_pos = {x: i for i, x in enumerate(pd.read_csv(ITEM_INDEX, keep_default_na=False)["item"])}
    titles = module_titles()
    score_all, _ = emi_offer_scores(offer_items(d), item_pos, np.load(ITEM_VEC).astype(np.float64), np.load(MODULE_VEC).astype(np.float64)[subject_titles(titles)])
    kw = pd.read_csv(KEYWORDS, keep_default_na=False)
    counts = pd.read_csv(COUNTS, keep_default_na=False)
    if not (counts["keywords_file"] == sha(KEYWORDS)).all():
        raise SystemExit("some counts were fetched for another keyword file")
    latest = counts.sort_values("date").drop_duplicates(["keyword", "region"], keep="last").pivot(index="keyword", columns="region", values="total")
    day = counts.sort_values("date").drop_duplicates(["keyword", "region"], keep="last").groupby("keyword")["date"].agg(lambda x: "; ".join(sorted(set(x))))
    if COUNTS4.exists():                                                                  # keywords never counted before (deviation 1)
        c4 = pd.read_csv(COUNTS4, keep_default_na=False)
        if not (c4["keywords_file"] == sha(KEYWORDS4)).all():
            raise SystemExit("some counts of funnel4_job_counts.csv were fetched for another keyword file")
        new = c4.sort_values("date").drop_duplicates(["keyword", "region"], keep="last")
        new = new[~new["keyword"].isin(latest.index)]
        latest = pd.concat([latest, new.pivot(index="keyword", columns="region", values="total")])
        day = pd.concat([day, new.groupby("keyword")["date"].agg(lambda x: "; ".join(sorted(set(x))))])
    from .demand_split import load
    table = pool_tables(d, smap, load(), TRANSITION)
    pools = {lv: origins(o) for lv, o in ORIGINS.items()}
    w_sub, cohort = rules["capture"]["w_substitute"], rules["capture"]["min_cohort"]["value"]
    geo = counties()

    def region_flag(la, lo, bavarian):
        if not len(la):
            return np.zeros(0, bool)
        near = haversine(np.asarray(la)[:, None], np.asarray(lo)[:, None], geo["lat"].to_numpy()[None, :], geo["lon"].to_numpy()[None, :]).argmin(axis=1)
        return geo["own_pool"].to_numpy()[near] & bavarian

    coh = pd.read_csv(COHERENCE).set_index("type")["mixed"].astype(bool)
    shares = [x for x in v4["new_to_oth_scenarios"]["shares_from_oth"] if not isinstance(x, str)]
    rows = []
    for (cid, lv), part in alive(u).groupby(["candidate", "level"]):
        types = sorted(int(c) for c in part["type"])
        at_level = level == lv
        name = part.loc[part["how"] == "title", "main"].iloc[0] if (part["how"] == "title").any() else str(t.at[types[0], "central titles"])   # E7, from its surviving units
        in_types = np.isin(assigned, types) & at_level
        a = d[in_types]
        kind, y0, y1, last = SERIES[lv]
        w = pool_weights(a, smap)
        y = pool_series(by.loc[kind], w)
        slope, bt = slope_pct(y, y0, y1), backtest(y, last, rules["demand"])
        inside = at_level & (np.isin(assigned, types) | (dist[:, types] <= radius[types][None, :]).any(axis=1))
        sim, far = supply & inside, far_supply & inside
        g = gap_numbers(sim, far, land, km, p_by[lv], key)
        other = sorted(set(land[sim & ~np.isin(land, SOUTH)]) - {""})
        slope_else = slope_pct(pool_series(laender.loc[other].groupby("year").sum(), w), 2019, 2024) if other else float("nan")
        emi_mask = in_types & ~oth if (in_types & ~oth).any() else in_types
        emi = float(score_all[emi_mask].mean())
        kws = list(dict.fromkeys(kw.loc[kw["type"].isin(types) & (kw["rank"] > 0), "keyword"]))           # the rule as written: union
        got = [k for k in kws if k in latest.index and latest.loc[k].notna().all()]
        ads_as_written = float(np.median([float(latest.at[k, "amberg_100km"]) for k in got])) if got and len(got) == len(kws) else np.nan
        kws4 = k4.loc[(k4["candidate"] == cid) & (k4["level"] == lv) & (k4["rank"] > 0)].sort_values("rank")["keyword"].tolist()   # deviation 1
        got4 = [k for k in kws4 if k in latest.index and latest.loc[k].notna().all()]
        ads = float(np.median([float(latest.at[k, "amberg_100km"]) for k in got4])) if got4 and len(got4) == len(kws4) else np.nan
        # capture (Step 6 on the merged pool and sites)
        comp = sites_of(d, sim)
        own = oth & in_types
        own_how = "assigned to its types"
        if not own.any():
            cand_oth = np.where(oth & at_level)[0]
            own = np.zeros(len(d), bool)
            own[cand_oth[np.argmin(dist[np.ix_(cand_oth, types)].min(axis=1))]] = True
            own_how = "nearest OTH offer of the level to any of its centroids"
        osite = sites_of(d, own)
        lat, lon = np.r_[comp["lat"], osite["lat"]], np.r_[comp["lon"], osite["lon"]]
        is_oth = np.r_[np.zeros(len(comp), bool), np.ones(len(osite), bool)]
        reg = region_flag(lat, lon, np.r_[(comp["state"] == "Bayern").to_numpy(), np.ones(len(osite), bool)])
        res = {k: huff(pools[lv], lat, lon, np.where(is_oth, wv, 1.0), is_oth, reg, NEW_SITE[lv]) for k, wv in w_sub.items()}
        bav = (comp["state"] == "Bayern").to_numpy()
        scale = res["central"]["new"] / float(res["central"]["sites"][:len(comp)][bav].mean()) if bav.any() else 1.0
        an = anchor_of(w, table, lv)
        gross = an["anchor"] * scale
        net = gross * (1 - res["central"]["a"])
        row = {"candidate": int(cid), "level": lv, "name": name, "types": "; ".join(str(c) for c in types), "units": len(types),
               "how": "; ".join(sorted(set(part["how"]))), "assigned offers": len(a), "institutions": int(a["institution"].nunique()),
               "central titles": str(t.at[types[0], "central titles"]),
               "pool": "; ".join(f"{k}:{v:.2f}" for k, v in sorted(w.items(), key=lambda kv: (-kv[1], kv[0]))[:4]),
               "trend": slope, "trend validated": bool(bt["validated"]), "MASE naive": bt["naive"], "MASE drift": bt["drift"],
               "similar offers": g["similar offers"], "similar in Bavaria": g["similar in Bavaria"], "similar within 100 km": g["similar within 100 km"],
               "similar_150": g["similar within 150 km"], "quotient": g["bavarian quotient"], "quotient used": bool(g["similar offers"] >= QUOTIENT_FROM),
               "popularity tier": 2 if (g["exists elsewhere"] and slope_else >= 0) else 3, "trend elsewhere %/yr": slope_else,
               "emi score": emi, "keywords": "; ".join(kws4), "keywords with counts": len(got4), "ads": ads, "counted on": "; ".join(sorted({day[k] for k in got4})),
               "keywords (as written)": "; ".join(kws), "ads (as written)": ads_as_written, "control": bool(lv == "bachelor" and name == CONTROL),
               "competitor sites": len(comp), "Bavarian competitor sites": int(bav.sum()), "OTH offers used": "; ".join(d.loc[own, "title"].head(3)), "OTH offers from": own_how,
               "OTH offer within a type's radius": bool((dist[np.ix_(np.where(own)[0], types)] <= radius[types][None, :]).any()),
               "anchor": an["anchor"], "anchor from Germany-wide values": an["germany"], "Bavarian offers of the pool (weighted)": an["offers"],
               "thin anchor": bool(an["offers"] < 2.0), "scale": scale, "one Bavarian comparator": bool(bav.sum() == 1),
               "share from OTH (central)": res["central"]["a"], "share from OTH (pessimistic)": res["pessimistic"]["a"], "share from OTH (optimistic)": res["optimistic"]["a"],
               "gross low": gross * LOW, "gross central": gross, "gross high": gross * HIGH,
               "net_new": net, "net-new low": gross * LOW * (1 - res["pessimistic"]["a"]), "net-new high": gross * HIGH * (1 - res["optimistic"]["a"]),
               **{f"net-new at {x:.0%} from OTH": gross * (1 - x) for x in shares},
               "break-even share from OTH": max(0.0, 1 - 15 / gross) if gross > 0 else np.nan,
               "net-new below 15 even with none from OTH": bool(gross < 15),
               "kept": res["central"]["c"], "below the minimum cohort": bool(gross < cohort),
               "mixed": bool(any(coh.get(c, False) for c in types)), "mixed types": "; ".join(str(c) for c in types if coh.get(c, False)),
               "mixed types left out": "; ".join(str(int(x)) for x in u.loc[(u["candidate"] == cid) & (u["level"] == lv) & u["primary"] & u["mixed type"], "type"])}
        if len(types) == 1:                                                              # M3: one unit -> the version-3 values
            c3, s3 = cap3.loc[(types[0], lv)], s[(s["type"] == types[0]) & (s["level"] == lv)].iloc[0]
            for mine, theirs in ((slope, s3["trend %/yr"]), (emi, s3["emi score"]), (g["similar within 150 km"], s3["similar within 150 km"]),
                                 (an["anchor"], c3["anchor"]), (scale, c3["scale"]), (gross, c3["gross central"]), (net, c3["net-new central"])):
                assert (np.isnan(mine) and np.isnan(theirs)) or np.isclose(mine, theirs, rtol=1e-9, atol=1e-12), (types, lv, mine, theirs)
            assert bool(bt["validated"]) == bool(s3["trend validated"])
        rows.append(row)
    c = pd.DataFrame(rows)

    weights = yaml.safe_load((REPO_ROOT / "configs" / "analysis.yaml").read_text(encoding="utf-8"))["weights"]
    cal = pd.read_csv(CALIBRATION, float_precision="round_trip")
    bar, top = float(step3["calibration"]["bar"]), float(cal.loc[cal["emi"].astype(bool), "score"].quantile(0.9))
    vf = rules["ranking"]["value_functions"]
    written = scores(c.assign(ads=c["ads (as written)"]), vf, weights, bar, top)
    c["pre-gate score (as written)"] = written["pre-gate score"]
    c = pd.concat([c, scores(c, vf, weights, bar, top)], axis=1)
    c["level order"] = c["level"].map({lv: i for i, lv in enumerate(LEVELS)})

    def ranked(col: str) -> pd.DataFrame:
        o = c.sort_values([col, "candidate", "level order"], ascending=[False, True, True], kind="mergesort").drop(columns="level order").reset_index(drop=True)
        o.insert(0, "gate order", np.arange(1, len(o) + 1))
        return o
    order, as_written = ranked("pre-gate score"), ranked("pre-gate score (as written)")
    order["gate order (as written)"] = order.set_index(["candidate", "level"]).index.map(as_written.set_index(["candidate", "level"])["gate order"])
    c = c.drop(columns="level order")
    c.to_csv(CANDIDATES4, index=False)
    order.to_csv(ORDER4, index=False)
    as_written.to_csv(ORDER4_AS_WRITTEN, index=False)

    # version 3 against version 4 (M5): the first 20 of version 3 and where their units are now
    o3 = pd.read_csv(ORDER_V3)
    where = u.set_index(["type", "level"])["candidate"]
    pos = order.set_index(["candidate", "level"])["gate order"]
    cmp = []
    for r in o3.head(FIRST).to_dict("records"):
        cid, lv = int(where[(int(r["type"]), r["level"])]), r["level"]
        on = (cid, lv) in pos.index
        cmp.append({"version 3 order": int(r["gate order"]), "type": int(r["type"]), "level": lv, "central titles": str(r["central titles"])[:60],
                    "version 4 candidate": cid, "version 4 order": int(pos[(cid, lv)]) if on else None,
                    "version 4 name": order.loc[(order["candidate"] == cid) & (order["level"] == lv), "name"].iloc[0] if on else "not on the list"})
    cmp = pd.DataFrame(cmp)

    conflicts = u[u["how"].isin(["partner of two or more title groups", "partner of a title group dropped at OTH"])]
    sizes = u.groupby(["candidate", "level"]).size()
    first = order.head(FIRST)
    res = {"stamp": stamp, "step3_commit": step3["stamp"]["commit"], "units": len(u), "candidates_all_units": int(len(sizes)),
           "candidates_on_the_list": len(order), "largest_candidate": {"units": int(sizes.max()), "candidate": int(sizes.idxmax()[0]), "level": str(sizes.idxmax()[1])},
           "units_by_how": {k: int(n) for k, n in u["how"].value_counts().items()},
           "title_groups_dropped_whole_at_oth": sorted({f"{r.main} ({r.level})" for r in u[u["dropped whole"]].itertuples()}),
           "units_dropped_with_a_title_group": int(u["dropped whole"].sum()),
           "partners_of_two_or_more_title_groups_or_of_a_dropped_one": [f"{int(r.type)} {r.level} ({r.how})" for r in conflicts.itertuples()],
           "first_20": {"bachelor": int((first["level"] == "bachelor").sum()), "master": int((first["level"] == "master").sum()),
                        "mixed": int(first["mixed"].sum()), "below the minimum cohort": int(first["below the minimum cohort"].sum()), "thin anchor": int(first["thin anchor"].sum())},
           "candidates_with_a_missing_input": {k: int(c[k].isna().sum()) for k in ("trend", "net_new", "ads", "ads (as written)", "kept")},
           "control": {"candidate": "Informatik bachelor", "gate order": int(order.loc[order["control"], "gate order"].iloc[0]),
                       "gate order (as written)": int(order.loc[order["control"], "gate order (as written)"].iloc[0]),
                       "ads": float(order.loc[order["control"], "ads"].iloc[0]), "keywords": str(order.loc[order["control"], "keywords"].iloc[0])},
           "first_20_as_written_not_in_first_20": [f"{r.name[:40]} ({r.level})" for r in as_written.head(FIRST).itertuples()
                                                    if (r.candidate, r.level) not in set(zip(order.head(FIRST)["candidate"], order.head(FIRST)["level"]))],
           "first_20_not_in_first_20_as_written": [f"{r.name[:40]} ({r.level})" for r in order.head(FIRST).itertuples()
                                                    if (r.candidate, r.level) not in set(zip(as_written.head(FIRST)["candidate"], as_written.head(FIRST)["level"]))],
           "fit_proxy": {"bar": bar, "value 5 at": top},
           "inputs": {f.name: sha(f) for f in [SCREEN, CAPTURE, LABOUR, KEYWORDS, COUNTS, KEYWORDS4, CALIBRATION, COHERENCE, OFFER_TYPES, ORDER_V3] + ([COUNTS4] if COUNTS4.exists() else [])},
           "files": {f.name: sha(f) for f in (UNITS4, CANDIDATES4, ORDER4, ORDER4_AS_WRITTEN)}}
    MERGE4.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    show = ["gate order", "gate order (as written)", "candidate", "level", "name", "types", "pre-gate score", "demand", "labour", "fit", "differentiation", "regional",
            "net_new", "gross central", "break-even share from OTH", "ads", "similar_150", "mixed", "below the minimum cohort", "thin anchor"]
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "v4_merge.md").write_text("\n".join([
        "# Rules version 4, R1: one candidate per programme title (generated)", "",
        f"Code commit {stamp['commit']} (screen: {res['step3_commit']}), run on {stamp['date']}, tracked files clean: {stamp['clean']}.", "",
        f"- {len(u)} units in {res['candidates_all_units']} candidates; {len(order)} candidates on the list; how units joined: {res['units_by_how']}.",
        f"- Title groups dropped whole because a unit with that title is at OTH: {res['title_groups_dropped_whole_at_oth']}.",
        f"- First 20: {res['first_20']}.",
        f"- Job ads by the version-3 keyword rule on the merged titles (deviation 1); the order with the union of keywords (as written) is the sensitivity column. "
        f"In the first 20 as written but not now: {res['first_20_as_written_not_in_first_20']}; now but not as written: {res['first_20_not_in_first_20_as_written']}.",
        f"- Control (deviation 2): {res['control']}.", "",
        "## Version 3's first 20 and where they are now", "", md_table(cmp), "",
        "## The first 40 candidates", "", md_table(order.head(40).assign(name=order["name"].head(40).str.slice(0, 50))[show].round(2))]) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    {"keywords": keywords, "fetch": fetch, "run": main}[sys.argv[1] if len(sys.argv) > 1 else "run"]()
