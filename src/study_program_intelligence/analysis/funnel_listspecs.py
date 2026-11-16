"""Funnel step 8b: the list-changing specs (configs/funnel.yaml: stress_tests.list_changing_one_at_a_time, list_changing_scope)

Run from the repository root, from committed code on a clean tree, after analysis.funnel_rank:

    python -m study_program_intelligence.analysis.funnel_listspecs

Each spec changes one rule of Steps 3 to 7a and is run up to the pre-gate ranking; reported is how many of the 20
first candidates of the base gate order (those that can take a slot, i.e. not below the minimum cohort) stay in the
first 20. Specs that need Steps 2 or 5 to run again (boilerplate scan, clustering, keyword rules) are not run here.
The former strict feasibility rule is applied to the gate candidates. The base spec must reproduce the published
primary list and gate order exactly.
Outputs: data/interim/funnel2_listspecs.csv, funnel2_step8b.json; reports/funnel2/step8b_listspecs.md.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import yaml

from .funnel_capture import CAPTURE
from .funnel_common import INTERIM, REPO_ROOT, REPORTS, config, md_table, run_stamp
from .funnel_demand import DEMAND
from .funnel_feasibility import GATE_REFS, TAUGHT
from .funnel_shortlist import LABOUR, ORDER, WEIGHTS, scores
from .funnel_types import sha
from .funnel_units import CALIBRATION, LEVELS, QUOTIENT_FROM, SCREEN, STEP3, load_step2

OUT, STEP8B = INTERIM / "funnel2_listspecs.csv", INTERIM / "funnel2_step8b.json"
TOP = 20
FORMER = REPO_ROOT / "configs" / "feasibility.yaml"


def at_oth(d: pd.DataFrame, t: pd.DataFrame, emb: np.ndarray, cent: np.ndarray, units: pd.DataFrame, variant: str) -> pd.Series:
    """screen.at_oth and its stress readings, per unit: an OTH offer of the unit's level (any form) assigned to the
    type or within its median distance (base); within radius_90 or assigned; a fitted member of the type; within the
    median distance only (as first written)."""
    oth = d[d["is_oth"].astype(bool)]
    dist = 1 - emb[oth.index] @ cent.T
    out = []
    for u in units.itertuples():
        same = (oth["level"] == u.level).to_numpy()
        assigned = same & (oth["assigned_type"] == u.type).to_numpy()
        near_med = same & (dist[:, u.type] <= t.at[u.type, "median distance"])
        if variant == "base":
            hit = assigned | near_med
        elif variant == "within radius_90":
            hit = assigned | (same & (dist[:, u.type] <= t.at[u.type, "radius_90"]))
        elif variant == "any fitted member":
            hit = same & (oth["type"] == u.type).to_numpy()
        else:
            hit = near_med
        out.append(bool(hit.any()))
    return pd.Series(out, index=units.index)


def connected_groups(units: pd.DataFrame, cent: np.ndarray, radius: np.ndarray) -> np.ndarray:
    """definitions.merged_candidates as first written: connected components of the pairs within each other's radius_90."""
    from scipy.sparse.csgraph import connected_components
    dist = 1 - cent @ cent.T
    group = units["type"].to_numpy().copy()
    for lv in LEVELS:
        idx = np.where(units["level"] == lv)[0]
        tt = units["type"].to_numpy()[idx]
        ratio = dist[np.ix_(tt, tt)] / np.minimum(radius[tt][:, None], radius[tt][None, :])
        _, lab = connected_components(ratio <= 1.0, directed=False)
        group[idx] = pd.Series(tt).groupby(lab).transform("min").to_numpy()
    return group


def run_spec(s: pd.DataFrame, ctx: dict, spec: dict) -> pd.DataFrame:
    """The gate order (one representative per group and level, by pre-gate score) of one spec."""
    sc = ctx["screen"]
    drop_oth = s["drop: at OTH"] if spec.get("at_oth", "base") == "base" else ctx["at_oth"][spec["at_oth"]]
    tt_line = spec.get("teacher_training_share", sc["teacher_training"]["drop_if_at_least"])
    trend_line = spec.get("trend_threshold", sc["trend"]["drop_if_below"])
    drop_trend = (s["trend %/yr"] < trend_line) & s["trend validated"] if trend_line != "none" else pd.Series(False, index=s.index)
    keep = ~drop_oth & ~(s["teacher share"] >= tt_line) & ~drop_trend & ~s["drop: outside EMI"]
    if "supply_cut" in spec:
        keep &= s["similar within 100 km"] <= spec["supply_cut"]                     # version 2: at most k similar offers within 100 km
    p = s[keep].copy()
    if spec.get("merging") == "none":
        p["group"] = p["type"]
        for c in ("similar within 150 km", "similar offers", "bavarian quotient", "similar in Bavaria"):
            p[f"group: {c}"] = p[c]
    elif spec.get("merging") == "connected":
        g = connected_groups(s[["type", "level"]], ctx["cent"], ctx["radius"])
        p["group"] = pd.Series(g, index=s.index)[p.index]
        for c in ("similar within 150 km", "similar offers", "similar in Bavaria"):                  # the union is at least the largest unit count
            p[f"group: {c}"] = p.groupby(["group", "level"])[f"group: {c}"].transform("max")
    sim150 = p["group: similar within 150 km"].to_numpy(float)
    if spec.get("similarity_radius") == "percentile 75":
        sim150 = p["similar within 150 km (radius 75)"].to_numpy(float)
    elif spec.get("similarity_radius") == "percentile 95":
        sim150 = p["similar within 150 km (radius 95)"].to_numpy(float)
    quotient = p["group: bavarian quotient"].to_numpy(float)
    if "quotient_pseudo_offers" in spec or spec.get("merging") == "connected":
        k = spec.get("quotient_pseudo_offers", 5)
        bp = ctx["bavaria_share"]
        quotient = np.array([((nb + k * bp[lv]) / (nd + k)) / bp[lv] for nb, nd, lv in zip(p["group: similar in Bavaria"], p["group: similar offers"], p["level"])])
    idx = pd.MultiIndex.from_frame(p[["type", "level"]])
    dm, cp, lb = ctx["demand"], ctx["capture"], ctx["labour"]
    u = pd.DataFrame({"trend": dm["trend German BY %/yr"].reindex(idx).to_numpy(), "trend validated": p["trend validated"].to_numpy(bool),
                      "net_new": cp["net-new central"].reindex(idx).to_numpy(),
                      "ads": np.where(lb["labour input"].reindex(idx).to_numpy() == "ok", lb["ads within 100 km (median keyword)"].reindex(idx).to_numpy(), np.nan),
                      "similar_150": sim150, "quotient": quotient, "quotient used": (p["group: similar offers"] >= QUOTIENT_FROM).to_numpy(),
                      "kept": cp["kept in the region (central)"].reindex(idx).to_numpy(), "emi score": p["emi score"].to_numpy(float)})
    v = scores(u, ctx["vf"], ctx["weights"], ctx["bar"], ctx["top"])
    out = pd.concat([p[["type", "level", "group"]].reset_index(drop=True), v[["pre-gate score"]].reset_index(drop=True)], axis=1)
    out["gross central"] = cp["gross central"].reindex(idx).to_numpy()
    out = out.sort_values(["pre-gate score", "type", "level"], ascending=[False, True, True], kind="mergesort")
    members = out.groupby(["group", "level"])["type"].agg(lambda x: set(x))
    rep = out.drop_duplicates(["group", "level"], keep="first").reset_index(drop=True)
    rep["members"] = [members[(g, lv)] for g, lv in zip(rep["group"], rep["level"])]
    cohort = spec.get("min_cohort", 20)
    rep["can take a slot"] = True if cohort == "none" else rep["gross central"] >= cohort
    from .funnel_feasibility import not_candidates
    from .funnel_types import TYPES
    tm = pd.read_csv(TYPES).set_index("type")["members"]
    o = rep.assign(**{"gate order": np.arange(1, len(rep) + 1), "members": rep["type"].map(tm)})
    nc = not_candidates(o[["gate order", "type", "level", "members"]])
    rep["mixed, not a candidate"] = [(int(t), lv) in nc and not nc[(int(t), lv)].startswith("mixed type: needs") for t, lv in zip(rep["type"], rep["level"])]
    return rep


def former_rule(refs: pd.DataFrame) -> pd.DataFrame:
    """configs/feasibility.yaml F1-F4 on the marked references (stress spec feasibility: former strict rule)."""
    r = yaml.safe_load(FORMER.read_text(encoding="utf-8"))["rule"]
    rows = []
    for x in refs.itertuples():
        taught = TAUGHT[x.level]
        new = (refs.at[x.Index, "N ECTS"] + refs.at[x.Index, "T ECTS"] + refs.at[x.Index, "X ECTS"]) / taught
        f = {"F1 covered >= 0.80": x.overlap >= r["F1_min_covered_share"], "F2 new <= 0.20 and caps": new <= r["F2_max_new_share"] and refs.at[x.Index, "T ECTS"] <= r["F2_max_T_ects"][x.level]
             and refs.at[x.Index, "N ECTS"] <= r["F2_max_N_ects"][x.level], "F3 labs": refs.at[x.Index, "share lab"] == 0,
             "F4 one programme <= 0.50": refs.at[x.Index, "largest share from one programme"] <= r["F4_max_share_from_one_programme"]}
        rows.append({"ref": x.ref, "type": x.type, "level": x.level, "overlap": x.overlap, "new share": new, **f, "passes": all(f.values())})
    return pd.DataFrame(rows)


def main() -> None:
    stamp, rules = run_stamp(), config()
    d, t, emb, cent = load_step2()
    s = pd.read_csv(SCREEN, float_precision="round_trip")
    step3 = json.loads(STEP3.read_text(encoding="utf-8"))
    cal = pd.read_csv(CALIBRATION, float_precision="round_trip")
    aw = yaml.safe_load((REPO_ROOT / "configs" / "analysis.yaml").read_text(encoding="utf-8"))["weights"]
    ctx = {"screen": rules["screen"], "vf": rules["ranking"]["value_functions"], "weights": aw, "bar": float(step3["calibration"]["bar"]),
           "top": float(cal.loc[cal["emi"].astype(bool), "score"].quantile(0.9)), "cent": cent, "radius": t["radius_90"].to_numpy(),
           "demand": pd.read_csv(DEMAND, float_precision="round_trip").set_index(["type", "level"]),
           "capture": pd.read_csv(CAPTURE, float_precision="round_trip").set_index(["type", "level"]),
           "labour": pd.read_csv(LABOUR).set_index(["type", "level"]),
           "bavaria_share": {lv: float(step3["bavaria_share_of_offers"][lv]) for lv in LEVELS}}
    units = s[["type", "level"]]
    t = t.set_index("type")
    ctx["at_oth"] = {v: at_oth(d, t, emb, cent, units, v) for v in ("base", "within radius_90", "any fitted member", "median distance only")}
    if not (ctx["at_oth"]["base"] == s["drop: at OTH"]).all():
        raise SystemExit("the at-OTH screen is not reproduced")
    base = run_spec(s, ctx, {})
    published = pd.read_csv(ORDER)
    if list(zip(base["type"], base["level"])) != list(zip(published["type"], published["level"])):
        raise SystemExit("the base spec does not reproduce the published gate order")
    top_base = base[base["can take a slot"]].head(TOP)
    specs = [("trend_threshold", -5), ("trend_threshold", "none"), ("min_cohort", 15), ("min_cohort", "none"), ("supply_cut", 3), ("supply_cut", 5),
             ("similarity_radius", "percentile 75"), ("similarity_radius", "percentile 95"), ("at_oth", "within radius_90"), ("at_oth", "any fitted member"),
             ("at_oth", "median distance only"), ("teacher_training_share", 0.3), ("teacher_training_share", 0.7), ("quotient_pseudo_offers", 2),
             ("quotient_pseudo_offers", 10), ("merging", "none"), ("merging", "connected")]
    gate = pd.read_csv(INTERIM / "funnel2_gate.csv")
    gate_c = list(zip(gate["type"], gate["level"]))
    rows = []
    for k, v in specs:
        o = run_spec(s, ctx, {k: v})
        top = o[o["can take a slot"]].head(TOP)
        in_top = lambda ty, lv: any(ty in m and lv == l for m, l in zip(top["members"], top["level"]))
        bach = o[o["can take a slot"] & ~o["mixed, not a candidate"] & (o["level"] == "bachelor")].reset_index(drop=True)
        pos = [i + 1 for i, m in enumerate(bach["members"]) if 312 in m]
        firsts = {lv: (lambda x: f"{int(x.iloc[0]['type'])}" if len(x) else "-")(top[top["level"] == lv]) for lv in LEVELS}
        rows.append({"spec": k, "value": str(v), "units on the list": int(len(o.explode("members"))), "candidates": len(o),
                     "gate candidates (6) still in the top 20": sum(in_top(ty, lv) for ty, lv in gate_c),
                     "base top-20 candidates still in the top 20": sum(in_top(ty, lv) for ty, lv in zip(top_base["type"], top_base["level"])),
                     "position of 312 bachelor among bachelors that can take a slot": pos[0] if pos else None,
                     "first bachelor (type)": firsts["bachelor"], "first master (type)": firsts["master"],
                     "note": {"similarity_radius": "changes the offers half of differentiation only (unit count at that radius against the group count at p90); "
                                                  "similar-offer counts, quotient and capture competitors are not recomputed",
                              "merging": "connected groups chain most units; the group count is the largest unit count" if v == "connected" else ""}.get(k, "")})
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    fr = former_rule(pd.read_csv(GATE_REFS))
    res = {"stamp": stamp, "specs run": len(out), "base top 20": [f"{a} {b}" for a, b in zip(top_base["type"], top_base["level"])],
           "not run (need Steps 2 or 5 again)": ["boilerplate_scan_from 10", "clustering: the former rule's setting", "labour_keywords: top 5, generic line 2 % and 10 %, phrases in one title"],
           "not run (needs Step 3 again with one radius for all types)": ["similarity_radius: one common radius"],
           "former strict feasibility rule": fr.round(3).to_dict("records"),
           "inputs": {f.name: sha(f) for f in (SCREEN, DEMAND, CAPTURE, LABOUR, GATE_REFS, ORDER)}, "files": {OUT.name: sha(OUT)}}
    STEP8B.write_text(json.dumps(res, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "step8b_listspecs.md").write_text("\n".join(["# Funnel step 8b: list-changing specs (generated)", "", f"Code commit {stamp['commit']}, run on {stamp['date']}.", "",
                                                           md_table(out), "", "## Former strict feasibility rule", "", md_table(fr.round(3))]) + "\n", encoding="utf-8")
    print(out.to_string())
    print(fr.round(3).to_string())


if __name__ == "__main__":
    main()
