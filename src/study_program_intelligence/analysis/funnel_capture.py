"""Funnel step 6: how many first-years, and how many of them new to OTH? (configs/funnel.yaml: capture; criteria in
docs/criteria_funnel_step6.md)

Run from the repository root, from committed code on a clean tree, after analysis.funnel_demand:

    python -m study_program_intelligence.analysis.funnel_capture

For every unit of Step 3 (both lists): a Huff model with the unit's similar-offer sites as competitors, OTH's own
offers of the type as sites with the weight w, and the new programme in Amberg and Weiden (master: Amberg). The level
comes from an anchor (students of the unit's subject pool in Bavaria per Bavarian offer) times a scale from the
model. No unit is removed; the minimum cohort is a flag.
Outputs: data/interim/funnel2_capture.csv, funnel2_step6.json; reports/funnel2/step6_capture.md.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .catchment import counties, haversine
from .funnel_common import INTERIM, REPORTS, config, md_table, run_stamp
from .funnel_demand import DEMAND
from .funnel_types import OFFER_TYPES, sha
from .funnel_units import SCREEN, STEP3, SUBJECT_MAP, load_step2, map_label, pool_weights
from .options import AMBERG, BETAS, WEIDEN, origins

CAPTURE, STEP6 = INTERIM / "funnel2_capture.csv", INTERIM / "funnel2_step6.json"
BETA = BETAS[1]                               # the central distance decay of analysis/options.py
LOW, HIGH, TRANSITION = 0.33, 3.0, 0.5       # capture.gross low and high; capture.anchor.master transition
NEW_SITE = {"bachelor": [AMBERG, WEIDEN], "master": [AMBERG]}          # capture.new_site
ORIGINS = {"bachelor": "cyber_bsc", "master": "cyber_msc"}             # capture.origins: the two origin sets of analysis/options.py
ANCHOR = {"bachelor": ("first-years", 2024, 1.0), "master": ("graduates", 2025, None)}   # capture.anchor; the master factor is the transition
# capture.level_check: published first-year numbers already collected in the baseline (institution, title part, number, note)
PUBLISHED = [("Ingolstadt", "Cybersicherheit", 25, "capacity in the module handbook"), ("Deggendorf", "Cyber Security", 60, "one student review"),
             ("Bochum", "IT-Sicherheit", 156, "research university"), ("Saarland", "Cybersicherheit", 42, "research university"),
             ("Saarland", "Cybersecurity", 3, "research university, English-taught")]


def huff(pool: pd.DataFrame, lat: np.ndarray, lon: np.ndarray, weight: np.ndarray, is_oth: np.ndarray, in_region: np.ndarray,
         new_locs: list[tuple[float, float]], beta: float = BETA) -> dict:
    """The Huff model of analysis/options.py in matrix form. pool: origins with mass, lat, lon, own. Sites: coordinates, a
    weight (1 for a competitor, w for an existing OTH offer), an OTH flag and a flag "in OTH's own region". Attraction is
    weight x max(distance, 5 km)^-beta; the new programme has the weight 1 at its nearest location. Returns the new
    programme's demand, the demand of every site, and the shares of the new programme's students that come from OTH
    sites (a), from other sites (b), and from other sites outside the region for origins in OTH's own pool (c)."""
    mass, own = pool["mass"].to_numpy(float), pool["own"].to_numpy(bool)
    dist = lambda la, lo: np.maximum(haversine(pool["lat"].to_numpy()[:, None], pool["lon"].to_numpy()[:, None], np.atleast_1d(la)[None, :], np.atleast_1d(lo)[None, :]), 5.0)
    new = dist([p[0] for p in new_locs], [p[1] for p in new_locs]).min(axis=1) ** (-beta)
    base = dist(lat, lon) ** (-beta) * weight[None, :] if len(lat) else np.zeros((len(pool), 0))
    bsum = base.sum(axis=1)
    n = mass * new / (bsum + new)
    take = np.divide(n[:, None] * base, bsum[:, None], out=np.zeros_like(base), where=bsum[:, None] > 0)
    total = float(n.sum())
    return {"new": total, "sites": (mass[:, None] * base / (bsum + new)[:, None]).sum(axis=0),
            "a": float(take[:, is_oth].sum() / total), "b": float(take[:, ~is_oth].sum() / total),
            "c": float((take * (own[:, None] & ~in_region[None, :] & ~is_oth[None, :])).sum() / total)}


def per_offer(d: pd.DataFrame, smap: dict, long: pd.DataFrame, transition: float) -> dict:
    """Rule capture.anchor: per level and region (BY, DE) the German students of a subject in the anchor year per offer of
    that subject, offers of all forms counted fractionally over their labels; for a master the graduates times the
    transition."""
    rows = [(lv, st == "Bayern", smap[map_label(x)], 1 / len(sub.split("; "))) for lv, st, sub in zip(d["level"], d["state"], d["subjects"].astype(str)) for x in sub.split("; ")]
    f = pd.DataFrame(rows, columns=["level", "by", "code", "w"])
    out = {}
    for level, (kind, year, factor) in ANCHOR.items():
        for region, mask in (("BY", f["by"]), ("DE", pd.Series(True, index=f.index))):
            offers = f[(f["level"] == level) & mask].groupby("code")["w"].sum()
            students = long[(long["kind"] == kind) & (long["region"] == region) & (long["nationality"] == "German") & (long["year"] == year)].groupby("code")["value"].sum()
            out[(level, region)] = (students * (transition if factor is None else factor) / offers).replace([np.inf, -np.inf], np.nan).dropna()
    return out


def anchor_of(w: dict[str, float], table: dict, level: str) -> tuple[float, float]:
    """The unit's anchor: the per-offer value of its pool's subjects, weighted. A subject without a Bavarian offer takes
    the Germany-wide value; the second result is the pool weight that did so (capture.anchor.no_bavarian_offer_in_pool)."""
    by, de = table[(level, "BY")], table[(level, "DE")]
    value = sum(v * (by[c] if c in by.index else de.get(c, 0.0)) for c, v in w.items())
    return float(value), float(sum(v for c, v in w.items() if c not in by.index))


def sites_of(d: pd.DataFrame, mask: np.ndarray) -> pd.DataFrame:
    """One site per institution and city, at the median coordinates of its offers; offers without coordinates have no site."""
    g = d[mask & d["lat"].notna().to_numpy()]
    return g.groupby(["institution", "city"], as_index=False).agg(lat=("lat", "median"), lon=("lon", "median"), state=("state", "first"))


def main() -> None:
    from .demand_split import load
    stamp, rules = run_stamp(), config()
    rule = rules["capture"]
    step3 = json.loads(STEP3.read_text(encoding="utf-8"))
    if step3["files"][SCREEN.name] != sha(SCREEN):
        raise SystemExit("the screen table is not the one Step 3 wrote")
    d, t, emb, cent = load_step2()
    s = pd.read_csv(SCREEN, float_precision="round_trip")
    demand = pd.read_csv(DEMAND, float_precision="round_trip").set_index(["type", "level"])
    smap = pd.read_csv(SUBJECT_MAP).set_index("label")["code"].to_dict()
    w_sub, cohort = rule["w_substitute"], rule["min_cohort"]["value"]
    transition = TRANSITION
    table = per_offer(d, smap, load(), transition)
    all_geo = counties()
    def region_flag(la, lo, bavarian):                                 # a Bavarian site whose nearest county is in OTH's own pool
        if not len(la):
            return np.zeros(0, bool)
        near = haversine(np.asarray(la)[:, None], np.asarray(lo)[:, None], all_geo["lat"].to_numpy()[None, :], all_geo["lon"].to_numpy()[None, :]).argmin(axis=1)
        return all_geo["own_pool"].to_numpy()[near] & bavarian
    pools = {lv: origins(o) for lv, o in ORIGINS.items()}
    dist = 1 - emb @ cent.T
    assigned, level = d["assigned_type"].to_numpy(), d["level"].to_numpy()
    oth, distance = d["is_oth"].to_numpy(bool), d["distance_only"].to_numpy(bool)
    radius = t["radius_90"].to_numpy()
    rows = []
    for r in s.itertuples():
        c, lv = int(r.type), r.level
        at_level = level == lv
        similar = ~oth & ~distance & at_level & ((assigned == c) | (dist[:, c] <= radius[c]))       # similarity.similar_offer
        comp = sites_of(d, similar)
        own_offers = oth & at_level & (assigned == c)
        how = "assigned to the type"
        if not own_offers.any():                                        # capture.oth_sites: else the OTH offer of the level nearest the centroid
            cand = np.where(oth & at_level)[0]
            own_offers = np.zeros(len(d), bool)
            own_offers[cand[np.argmin(dist[cand, c])]] = True
            how = "nearest OTH offer of the level"
        osite = sites_of(d, own_offers)
        lat, lon = np.r_[comp["lat"], osite["lat"]], np.r_[comp["lon"], osite["lon"]]
        is_oth = np.r_[np.zeros(len(comp), bool), np.ones(len(osite), bool)]
        reg = region_flag(lat, lon, np.r_[(comp["state"] == "Bayern").to_numpy(), np.ones(len(osite), bool)])
        res = {k: huff(pools[lv], lat, lon, np.where(is_oth, w, 1.0), is_oth, reg, NEW_SITE[lv]) for k, w in w_sub.items()}
        bav = (comp["state"] == "Bayern").to_numpy()
        mean_bav = float(res["central"]["sites"][:len(comp)][bav].mean()) if bav.any() else np.nan
        scale = res["central"]["new"] / mean_bav if bav.any() else 1.0                                  # capture.scale
        a = d[(assigned == c) & at_level]
        anchor, de_weight = anchor_of(pool_weights(a, smap), table, lv)
        gross = {"central": anchor * scale, "low": anchor * scale * LOW, "high": anchor * scale * HIGH}
        net = {"central": gross["central"] * (1 - res["central"]["a"]), "low": gross["low"] * (1 - res["pessimistic"]["a"]), "high": gross["high"] * (1 - res["optimistic"]["a"])}
        fs = demand.at[(c, lv), "foreign share last BY"]
        rows.append({"type": c, "level": lv, "kind": r.kind, "primary": bool(r.primary), "stress": bool(r.stress), "central titles": s.at[r.Index, "central titles"],
                     "competitor sites": len(comp), "Bavarian competitor sites": int(bav.sum()), "OTH sites": len(osite), "OTH offers used": "; ".join(d.loc[own_offers, "title"].head(3)),
                     "OTH offers from": how, "anchor": anchor, "pool weight on Germany-wide values": de_weight,
                     "scale": scale, "scale flag": "" if bav.any() else "no Bavarian comparator",
                     "share from OTH (pessimistic)": res["pessimistic"]["a"], "share from OTH (central)": res["central"]["a"], "share from OTH (optimistic)": res["optimistic"]["a"],
                     "gross low": gross["low"], "gross central": gross["central"], "gross high": gross["high"],
                     "net-new low": net["low"], "net-new central": net["central"], "net-new high": net["high"],
                     "kept in the region (pessimistic)": res["pessimistic"]["c"], "kept in the region (central)": res["central"]["c"], "kept in the region (optimistic)": res["optimistic"]["c"],
                     "foreign share of the pool": fs, "international on top, up to": gross["central"] * fs / (1 - fs) if np.isfinite(fs) and fs < 1 else np.nan,
                     "below the minimum cohort": bool(gross["central"] < cohort)})
    out = pd.DataFrame(rows)
    out.to_csv(CAPTURE, index=False)

    # level check (reported only): the anchor against the few published first-year numbers
    check = []
    for inst, title, number, note in PUBLISHED:
        hit = d[d["institution"].str.contains(inst, regex=False) & d["title"].str.contains(title, regex=False) & (d["level"] == "bachelor") & (d["assigned_type"] >= 0)]
        hit = hit.drop_duplicates("assigned_type")
        if hit.empty:
            check.append({"published": f"{inst}: {title}", "number": number, "note": note, "unit": "no offer found in a type", "anchor": np.nan, "gross central": np.nan})
        for h in hit.itertuples():
            u = out[(out["type"] == h.assigned_type) & (out["level"] == "bachelor")]
            if len(u):
                check.append({"published": f"{inst}: {h.title}", "number": number, "note": note, "unit": f"{h.assigned_type} bachelor", "anchor": float(u["anchor"].iloc[0]), "gross central": float(u["gross central"].iloc[0])})
    check = pd.DataFrame(check)
    err = np.abs(np.log(check["anchor"] / check["number"])).dropna()

    prim = out[out["primary"]]
    q = lambda col: [round(float(x), 1) for x in prim[col].quantile([0.25, 0.5, 0.75])]
    res = {"stamp": stamp, "step3_commit": step3["stamp"]["commit"], "units": len(out), "primary": len(prim), "stress": int(out["stress"].sum()),
           "beta": BETA, "w_substitute": w_sub, "gross_band": [LOW, HIGH], "master_transition": transition, "minimum_cohort": cohort,
           "origins": {lv: {"origins": len(p), "mass": float(p["mass"].sum())} for lv, p in pools.items()},
           "primary_quartiles": {"anchor": q("anchor"), "scale": q("scale"), "gross central": q("gross central"), "net-new central": q("net-new central"),
                                 "share from OTH (central)": [round(float(x), 3) for x in prim["share from OTH (central)"].quantile([0.25, 0.5, 0.75])]},
           "primary_below_the_minimum_cohort": int(prim["below the minimum cohort"].sum()), "primary_at_or_above": int((~prim["below the minimum cohort"]).sum()),
           "primary_without_a_bavarian_comparator": int((prim["scale flag"] != "").sum()), "primary_without_any_competitor_site": int((prim["competitor sites"] == 0).sum()),
           "primary_with_germany_wide_anchor_parts": int((prim["pool weight on Germany-wide values"] > 0).sum()),
           "primary_oth_offers_from": {str(k): int(v) for k, v in prim["OTH offers from"].value_counts().items()},
           "primary_net_new_central_10_or_more": int((prim["net-new central"] >= 10).sum()), "primary_net_new_central_40_or_more": int((prim["net-new central"] >= 40).sum()),
           "level_check": {"rows": len(check), "rows_with_a_unit": int(len(err)), "median_absolute_log_error": round(float(err.median()), 3) if len(err) else None,
                           "as_a_factor": round(float(np.exp(err.median())), 2) if len(err) else None},
           "inputs": {SCREEN.name: sha(SCREEN), OFFER_TYPES.name: sha(OFFER_TYPES), DEMAND.name: sha(DEMAND), SUBJECT_MAP.name: sha(SUBJECT_MAP)},
           "files": {CAPTURE.name: sha(CAPTURE)}}
    STEP6.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    show = ["type", "level", "central titles", "competitor sites", "Bavarian competitor sites", "OTH offers used", "anchor", "scale", "gross central", "share from OTH (central)",
            "net-new low", "net-new central", "net-new high", "below the minimum cohort", "scale flag"]
    cut = lambda x: x.assign(**{"central titles": x["central titles"].str.slice(0, 55), "OTH offers used": x["OTH offers used"].str.slice(0, 45)})[show].round(2)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "step6_capture.md").write_text("\n".join([
        "# Funnel step 6: first-years and students new to OTH (generated)", "",
        f"Code commit {stamp['commit']} (screen: {res['step3_commit']}), run on {stamp['date']}, tracked files clean: {stamp['clean']}.", "",
        f"- Units: {len(out)} (primary {len(prim)}, stress {res['stress']}); distance decay {BETA}; w {w_sub}; gross band x0.33 to x3.0.",
        f"- Primary list, quartiles (25 %, median, 75 %): {res['primary_quartiles']}.",
        f"- Primary list: {res['primary_below_the_minimum_cohort']} units below the minimum cohort of {cohort} (central gross), {res['primary_at_or_above']} at or above; "
        f"{res['primary_without_a_bavarian_comparator']} without a Bavarian comparator (scale 1.0).",
        f"- Level check (reported only, no correction): {res['level_check']}.", "",
        "## Level check", "", md_table(check.round(1)), "",
        "## Primary list, by net-new first-years (central)", "", md_table(cut(prim.sort_values("net-new central", ascending=False)))]) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
