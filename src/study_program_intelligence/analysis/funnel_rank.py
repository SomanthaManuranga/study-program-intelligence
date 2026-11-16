"""Funnel step 8a: ranking, stress tests and the decision (configs/funnel.yaml: ranking, stress_tests, decision;
criteria in docs/criteria_funnel_step8.md)

Run from the repository root, from committed code on a clean tree, after analysis.funnel_feasibility:

    python -m study_program_intelligence.analysis.funnel_rank

The candidates are the six of the Step 7 gate. decision.first is taken among the existing-resources passers,
decision.second among the band passers. Every criterion has a low, central and high input from the earlier steps;
the value functions turn them into 1-5 values; the weights are those of configs/analysis.yaml.
Outputs: data/interim/funnel2_rank_inputs.csv, funnel2_rank.csv, funnel2_factorial.csv, funnel2_step8.json;
reports/funnel2/step8_decision.md.
"""

from __future__ import annotations

import itertools
import json

import numpy as np
import pandas as pd
import yaml

from .funnel_capture import CAPTURE
from .funnel_common import INTERIM, REPO_ROOT, REPORTS, config, md_table, run_stamp
from .funnel_demand import DEMAND, tables
from .funnel_feasibility import GATE, GATE_REFS, STEP7, TAUGHT
from .funnel_shortlist import value
from .funnel_types import OFFER_TYPES, sha
from .funnel_units import QUOTIENT_FROM, SCREEN, SERIES, SUBJECT_MAP, pool_series, pool_weights, slope_pct

LABOUR_FILE = INTERIM / "funnel2_labour.csv"
INPUTS, RANK, FACTORIAL, STEP8 = INTERIM / "funnel2_rank_inputs.csv", INTERIM / "funnel2_rank.csv", INTERIM / "funnel2_factorial.csv", INTERIM / "funnel2_step8.json"
CRITERIA = {"demand": "student_demand", "labour": "labour_relevance", "fit": "institutional_fit", "feasibility": "feasibility",
            "differentiation": "differentiation", "regional": "regional_contribution"}
DRAWS, SEED, CONCENTRATION = 10_000, 42, 50                     # ranking.sampling
WIDEN = 1.0                                                     # one value point (ranking.inputs.trend, differentiation)
SINGLE_WIDEN = 0.10                                             # feasibility_gate.references.one_only
PROMETHEE_P = 4.0                                               # ranking.cross_check: preference threshold, the full scale
BARS = {"rank_1": 0.5, "beats_runner_up": 0.8, "win_share": 0.5}   # decision.rule.two_or_more
ONE_PASSER = 15.0                                               # decision.rule.one
COHORT = 20.0                                                   # capture.min_cohort


def widened(anchors: dict, log: bool = False) -> dict:
    """stress value_anchors: the anchor interval widened by a quarter of its length, half at each end (on the log scale
    for a log value function); inner anchors stay."""
    keys = sorted(float(k) for k in anchors)
    f, g = (np.log, np.exp) if log else ((lambda x: x), (lambda x: x))
    lo, hi = f(max(keys[0], 1e-9) if log else keys[0]), f(keys[-1])
    d = (hi - lo) / 8
    new = {float(k): anchors[k] for k in anchors}
    v_lo, v_hi = new.pop(keys[0]), new.pop(keys[-1])
    new[float(g(lo - d))] = v_lo
    new[float(g(hi + d))] = v_hi
    return new


def trend_windows(type_: int, level: str, d: pd.DataFrame, smap: dict, tab: dict) -> tuple[float, float, float]:
    """ranking.inputs.trend: the window slope (central) and the smallest and largest of the slopes over the window
    started one year earlier, the window itself and the window started one year later (German first-years or
    graduates of the pool in Bavaria)."""
    kind, y0, y1, _ = SERIES[level]
    w = pool_weights(d[(d["assigned_type"] == type_) & (d["level"] == level)], smap)
    y = pool_series(tab[("BY", "German")].loc[kind], w)
    s = [slope_pct(y, a, y1) for a in (y0 - 1, y0, y0 + 1)]
    ok = [x for x in s if np.isfinite(x)]
    return (min(ok), s[1], max(ok)) if ok else (np.nan, np.nan, np.nan)


def inputs(rules: dict) -> pd.DataFrame:
    """One row per gate candidate with the low / central / high of every input and the flags that decide widenings."""
    g, refs = pd.read_csv(GATE), pd.read_csv(GATE_REFS)
    cp = pd.read_csv(CAPTURE, float_precision="round_trip").set_index(["type", "level"])
    dm = pd.read_csv(DEMAND, float_precision="round_trip").set_index(["type", "level"])
    lb = pd.read_csv(LABOUR_FILE).set_index(["type", "level"])
    sc = pd.read_csv(SCREEN, float_precision="round_trip").set_index(["type", "level"])
    d = pd.read_csv(OFFER_TYPES, low_memory=False, dtype={"programme_id": str})
    smap = pd.read_csv(SUBJECT_MAP).set_index("label")["code"].to_dict()
    tab = tables()
    rows = []
    for r in g.itertuples():
        key = (int(r.type), r.level)
        rr = refs[(refs["type"] == r.type) & (refs["level"] == r.level)].sort_values("ref")
        t_lo, t_c, t_hi = trend_windows(*key, d, smap, tab)
        ok = lb.at[key, "labour input"] == "ok"
        q_used = bool(sc.at[key, "group: similar offers"] >= QUOTIENT_FROM)
        rows.append({
            "type": key[0], "level": key[1], "verdict": r.verdict, "central titles": g.at[r.Index, "central titles"],
            "trend low": t_lo, "trend central": t_c, "trend high": t_hi, "trend validated": bool(dm.at[key, "trend validated"]),
            "trend in Step 4": float(dm.at[key, "trend German BY %/yr"]),
            "net-new low": float(cp.at[key, "net-new low"]), "net-new central": float(cp.at[key, "net-new central"]), "net-new high": float(cp.at[key, "net-new high"]),
            "gross central": float(cp.at[key, "gross central"]), "foreign share": float(cp.at[key, "foreign share of the pool"]),
            "projection factor": float(dm.at[key, [c for c in dm.columns if c.startswith("German 2030 BY")][0]] / dm.at[key, f"German {SERIES[key[1]][3]} BY"]),
            "labour low": float(lb.at[key, "ads within 100 km (smallest keyword)"]) if ok else np.nan, "labour central": float(lb.at[key, "ads within 100 km (median keyword)"]) if ok else np.nan,
            "labour high": float(lb.at[key, "ads within 100 km (largest keyword)"]) if ok else np.nan,
            "fit low": float(rr["overlap"].min()) - (SINGLE_WIDEN if len(rr) == 1 else 0.0), "fit central": float(rr["overlap"].mean()),
            "fit high": float(rr["overlap"].max()) + (SINGLE_WIDEN if len(rr) == 1 else 0.0),
            "feasibility low": float(rr["share of new ECTS in N"].min()), "feasibility central": float(rr["share of new ECTS in N"].mean()), "feasibility high": float(rr["share of new ECTS in N"].max()),
            "offers 75": float(sc.at[key, "similar within 150 km (radius 75)"]), "offers 90": float(sc.at[key, "group: similar within 150 km"]), "offers 95": float(sc.at[key, "similar within 150 km (radius 95)"]),
            "quotient": float(sc.at[key, "group: bavarian quotient"]) if q_used else np.nan, "quotient used": q_used,
            "tier 2 shown": bool(sc.at[key, "popularity tier"] <= 2), "trend elsewhere": float(sc.at[key, "trend elsewhere %/yr"]) if "trend elsewhere %/yr" in sc.columns else np.nan,
            "regional low": float(cp.at[key, "kept in the region (pessimistic)"]), "regional central": float(cp.at[key, "kept in the region (central)"]), "regional high": float(cp.at[key, "kept in the region (optimistic)"]),
            "references": len(rr), "ref names": "; ".join(rr["ref"]),
            "overlaps": "; ".join(f"{x:.3f}" for x in rr["overlap"]), "one-programme shares": "; ".join(f"{x:.3f}" for x in rr["largest share from one programme"]),
            "lab shares": "; ".join(f"{x:.3f}" for x in rr["share lab"]), "X ECTS": "; ".join(f"{x:.3f}" for x in rr["X ECTS"]), "N ECTS": "; ".join(f"{x:.3f}" for x in rr["N ECTS"]),
            "new teaching ECTS": float(g.at[r.Index, "new teaching ECTS (mean)"]),
            "professor-equivalents": float(g.at[r.Index, "professor-equivalents (mean)"]),
        })
    out = pd.DataFrame(rows)
    out["missing inputs"] = ["; ".join(c for c in ("trend central", "net-new central", "labour central", "fit central", "feasibility central", "regional central") if not np.isfinite(r[c])) for _, r in out.iterrows()]
    return out


def values(c: pd.Series, vf: dict, spec: dict) -> dict[str, float]:
    """The central 1-5 value of every criterion of one candidate under a spec (stress factors)."""
    anchors = (lambda a, log=False: widened(a, log)) if spec["value_anchors"] == "widened" else (lambda a, log=False: a)
    v = lambda x, a, log=False: float(value([x], anchors(a, log), log=log)[0])
    trend = v(c["trend central"], vf["trend_pct_per_year"])
    if not c["trend validated"] and spec["widenings"] == "as written":
        trend = min(trend, 3.0)
    nn = c["net-new central"] * spec["net-new factor"](c)
    out = {"demand": (trend + v(nn, vf["net_new"])) / 2,
           "labour": v(c[f"labour {'central' if spec['labour_measure'] == 'median keyword' else 'high'}"], vf["labour_ads_within_100km_log"], True),
           "fit": (5.0 if c["fit central"] >= 0.40 else 1.0) if spec["fit_value"] == "flat" else v(c["fit central"], vf["fit_overlap"]),
           "feasibility": v(c["feasibility central"], vf["feasibility_share_of_new_ects_in_N"]),
           "regional": v(c["regional central"], vf["regional_share_of_net_new_kept_in_region"])}
    offers = v(c["offers 90"], {20: 1, 0: 5} if spec["differentiation"] == "anchor 20" else vf["differentiation_similar_offers_within_150km"])
    if c["quotient used"] and spec["differentiation"] != "quotient half left out":
        out["differentiation"] = (offers + v(c["quotient"], vf["differentiation_bavarian_quotient"])) / 2
    else:
        out["differentiation"] = offers
    return out


def score(vals: dict, weights: dict, feasibility: bool = True) -> float:
    use = {k: w for k, w in weights.items() if feasibility or k != "feasibility"}
    return sum(vals[k] * w for k, w in use.items()) / sum(use.values())


def passes(c: pd.Series, spec: dict) -> tuple[bool, bool]:
    """(band passer, existing-resources passer) of one candidate under a spec (feasibility_gate.verdict and the stress
    factors overlap_band, overlap_reading, one_programme_max, references, existing_resources_N_cap, min_cohort)."""
    split = lambda col: [float(x) for x in str(c[col]).split("; ")]
    ov, one, lab, x, n = split("overlaps"), split("one-programme shares"), split("lab shares"), split("X ECTS"), split("N ECTS")
    idx = [0] if spec["references"] == "primary only" else list(range(len(ov)))
    lo, hi = spec["overlap_band"]
    one_max = np.inf if spec["one_programme_max"] == "none" else float(spec["one_programme_max"])
    ok = []
    for i in idx:
        if spec["overlap_reading"] == "lower end overall, upper end on one programme":
            ok.append(ov[i] >= lo and one[i] <= min(hi, one_max) and lab[i] == 0)
        else:
            ok.append(lo <= ov[i] <= hi and one[i] <= one_max and lab[i] == 0)
    gross = c["gross central"] * (spec["master_transition"] / 0.5 if c["level"] == "master" else 1.0)
    band = all(ok) and gross >= spec["min_cohort"]
    cap = spec["N_cap"][c["level"]]
    existing = band and all(x[i] <= 1e-9 for i in idx) and all(n[i] <= cap + 1e-9 for i in idx)
    return band, existing


BASE = {"min_cohort": 20, "pool_trend": "unprojected", "master_transition": 0.5, "overlap_band": (0.40, 0.80),
        "overlap_reading": "lower end overall, upper end on one programme", "one_programme_max": 0.80,
        "N_cap": {"bachelor": np.inf, "master": np.inf}, "references": "both inside", "fit_value": "rising", "feasibility_value": "included",
        "differentiation": "both halves anchor 10", "labour_measure": "median keyword", "value_anchors": "as written", "widenings": "as written"}
FACTORS = {  # stress_tests.downstream_factorial; the factors marked False cannot change a set or a central score and are counted by multiplicity
    "min_cohort": ([20, 25], True), "gross_band": ([(0.33, 3.0), (0.5, 2.0)], False), "pool_trend": (["unprojected", "projected", "foreign added flat"], True),
    "master_transition": ([0.5, 0.3, 0.7], True), "dirichlet_concentration": ([10, 50, 200], False), "overlap_band": ([(0.40, 0.80), (0.50, 0.80), (0.30, 0.90)], True),
    "overlap_reading": (["lower end overall, upper end on one programme", "both ends on all EMI modules"], True), "one_programme_max": ([0.80, 0.50, "none"], True),
    "matching_threshold": ([0.463, 0.285], False), "N_cap": ([{"bachelor": np.inf, "master": np.inf}, {"bachelor": 20.0, "master": 10.0}, {"bachelor": 10.0, "master": 5.0}], True),
    "references": (["both inside", "primary only"], True), "fit_value": (["rising", "flat"], True), "feasibility_value": (["included", "left out"], True),
    "differentiation": (["both halves anchor 10", "anchor 20", "quotient half left out"], True), "labour_measure": (["median keyword", "largest keyword"], True),
    "value_anchors": (["as written", "widened"], True), "widenings": (["as written", "none"], True), "tier_2_slope": ([0, -1], False),
    "decision_bars": (["as written", "lowered by 0.1"], False), "one_passer_net_new": ([15, 10], False)}


def net_new_factor(spec: dict):
    def f(c: pd.Series) -> float:
        k = {"unprojected": 1.0, "projected": c["projection factor"], "foreign added flat": 1 / (1 - c["foreign share"])}[spec["pool_trend"]]
        return k * (spec["master_transition"] / 0.5 if c["level"] == "master" else 1.0)
    return f


def montecarlo(cands: pd.DataFrame, vf: dict, weights: dict, concentration: float = CONCENTRATION, widen: bool = True, draws: int = DRAWS, seed: int = SEED) -> tuple[pd.DataFrame, np.ndarray]:
    """ranking.sampling: P(rank 1) and the rank probabilities of every candidate in the set."""
    rng = np.random.default_rng(seed)
    keys = list(CRITERIA)
    base = np.array([weights[k] for k in keys]) / sum(weights.values())
    W = rng.dirichlet(concentration * base, size=draws)
    n = len(cands)
    tri = lambda lo, c, hi, size, log=False: (np.exp(rng.triangular(np.log(lo + 1), np.log(c + 1), np.log(hi + 1), size)) - 1) if log else (rng.triangular(lo, c, hi, size) if hi > lo else np.full(size, c))
    S = np.zeros((draws, n))
    for j, (_, c) in enumerate(cands.iterrows()):
        def draw(name, log=False):
            lo, ce, hi = c[f"{name} low"], c[f"{name} central"], c[f"{name} high"]
            if not np.isfinite(ce):
                return None
            lo, hi = min(lo, ce), max(hi, ce)
            return tri(lo, ce, hi, draws, log) if hi > lo else np.full(draws, ce)
        vv = {}
        t = draw("trend")
        trend = value(t, vf["trend_pct_per_year"]) if t is not None else np.ones(draws)
        if not c["trend validated"] and widen:
            trend = np.minimum(trend, 3.0) + rng.uniform(-WIDEN, WIDEN, draws)
        nn = draw("net-new", log=True)
        vv["demand"] = (np.clip(trend, 1, 5) + value(nn, vf["net_new"])) / 2
        lab = draw("labour", log=True)
        vv["labour"] = value(lab, vf["labour_ads_within_100km_log"], log=True) if lab is not None else np.ones(draws)
        vv["fit"] = value(draw("fit"), vf["fit_overlap"])
        vv["feasibility"] = value(draw("feasibility"), vf["feasibility_share_of_new_ects_in_N"])
        reg = draw("regional")
        vv["regional"] = value(reg, vf["regional_share_of_net_new_kept_in_region"]) if reg is not None else np.ones(draws)
        lo, ce, hi = sorted([c["offers 75"], c["offers 95"]])[0], c["offers 90"], sorted([c["offers 75"], c["offers 95"]])[1]
        lo, hi = min(lo, ce), max(hi, ce)
        offers = value(rng.triangular(lo, ce, hi, draws) if hi > lo else np.full(draws, ce), vf["differentiation_similar_offers_within_150km"])
        if c["quotient used"]:
            q = value(np.full(draws, c["quotient"]), vf["differentiation_bavarian_quotient"])
            if not c["tier 2 shown"] and widen:
                q = np.clip(q + rng.uniform(-WIDEN, WIDEN, draws), 1, 5)
            vv["differentiation"] = (offers + q) / 2
        else:
            vv["differentiation"] = offers
        S[:, j] = sum(np.clip(vv[k], 1, 5) * W[:, i] for i, k in enumerate(keys))
    order = np.argsort(-S, axis=1, kind="stable")
    rank = np.empty_like(order)
    rank[np.arange(draws)[:, None], order] = np.arange(n)[None, :]
    out = pd.DataFrame({"type": cands["type"].to_numpy(), "level": cands["level"].to_numpy(), "P(rank 1)": (rank == 0).mean(axis=0)})
    return out, S


def promethee(V: pd.DataFrame, weights: dict) -> pd.Series:
    """ranking.cross_check: PROMETHEE II net flow on the central 1-5 values, linear preference, indifference 0, preference 4."""
    w = pd.Series({k: weights[k] for k in V.columns}) / sum(weights[k] for k in V.columns)
    n = len(V)
    phi = pd.Series(0.0, index=V.index)
    for a in V.index:
        for b in V.index:
            if a != b:
                pref = lambda x, y: float((np.clip((V.loc[x] - V.loc[y]) / PROMETHEE_P, 0, 1) * w).sum())
                phi[a] += (pref(a, b) - pref(b, a)) / (n - 1)
    return phi


def decide(cands: pd.DataFrame, central: pd.Series, mc: pd.DataFrame | None, S: np.ndarray | None, win_share: float | None, phi: pd.Series | None, bars: dict, one_bar: float) -> dict:
    """decision.rule for one set."""
    if len(cands) == 0:
        return {"outcome": "no candidate passes"}
    if len(cands) == 1:
        c = cands.iloc[0]
        nn = float(c["net-new central"])
        return {"outcome": "recommend" if nn >= one_bar else "shortlist", "candidate": [int(c["type"]), c["level"]], "net-new central": nn, "bar": one_bar}
    order = central.sort_values(ascending=False, kind="stable").index
    top, second = order[0], order[1]
    p1 = float(mc.set_index(["type", "level"]).loc[top, "P(rank 1)"])
    i, j = list(central.index).index(top), list(central.index).index(second)
    beats = float((S[:, i] > S[:, j]).mean())
    prom_top = phi.idxmax()
    res = {"candidate": [int(top[0]), top[1]], "runner-up": [int(second[0]), second[1]], "P(rank 1)": p1, "P(beats the runner-up)": beats, "win share": win_share,
           "PROMETHEE rank 1": [int(prom_top[0]), prom_top[1]]}
    if prom_top != top:
        res["outcome"] = "shortlist (PROMETHEE disagrees on rank 1)"
    elif p1 >= bars["rank_1"] and beats >= bars["beats_runner_up"] and (win_share or 0) >= bars["win_share"]:
        res["outcome"] = "recommend"
    else:
        res["outcome"] = "shortlist"
    return res


def main() -> None:
    stamp, rules = run_stamp(), config()
    step7 = json.loads(STEP7.read_text(encoding="utf-8"))
    for f in (GATE, GATE_REFS):
        if step7["files"][f.name] != sha(f):
            raise SystemExit(f"{f.name} is not the file Step 7 wrote")
    vf = rules["ranking"]["value_functions"]
    aw = yaml.safe_load((REPO_ROOT / "configs" / "analysis.yaml").read_text(encoding="utf-8"))["weights"]
    weights = {k: float(aw[v]) for k, v in CRITERIA.items()}
    cands = inputs(rules)
    cands.to_csv(INPUTS, index=False)
    idx = pd.MultiIndex.from_frame(cands[["type", "level"]])
    cands.index = idx

    # the factorial: sets and winners under every combination of the factors that can change them
    live = [k for k, (lv, used) in FACTORS.items() if used]
    mult = int(np.prod([len(lv) for k, (lv, used) in FACTORS.items() if not used]))
    total = int(np.prod([len(lv) for lv, _ in FACTORS.values()]))
    counts = {s: {} for s in ("first", "second")}
    regret = {s: {c: [0, 0.0] for c in idx} for s in ("first", "second")}
    by_factor = []
    for combo in itertools.product(*[FACTORS[k][0] for k in live]):
        spec = dict(zip(live, combo))
        spec["net-new factor"] = net_new_factor(spec)
        flags = {c: passes(cands.loc[c], spec) for c in idx}
        sc_ = {c: score(values(cands.loc[c], vf, spec), weights, spec["feasibility_value"] == "included") for c in idx}
        for s, k in (("first", 1), ("second", 0)):
            members = [c for c in idx if flags[c][k]]
            win = max(members, key=lambda c: (sc_[c], -c[0], c[1] == "bachelor")) if members else None
            counts[s][win] = counts[s].get(win, 0) + mult
            for c in members:
                regret[s][c][0] += mult
                regret[s][c][1] += mult * (sc_[win] - sc_[c])
            by_factor.append({"set": s, **{k: str(v) for k, v in spec.items() if k != "net-new factor"}, "winner": "none" if win is None else f"{win[0]} {win[1]}", "count": mult})
    fac = pd.DataFrame(by_factor)
    fac.to_csv(FACTORIAL, index=False)
    assert all(sum(v.values()) == total for v in counts.values())

    # base spec: sets, central scores, Monte Carlo, PROMETHEE, decision
    base = dict(BASE, **{"net-new factor": net_new_factor(BASE)})
    rows, results = [], {}
    for s, k in (("first", 1), ("second", 0)):
        members = cands[[passes(cands.loc[c], base)[k] for c in idx]]
        V = pd.DataFrame({c: values(members.loc[c], vf, base) for c in members.index}).T if len(members) else pd.DataFrame()
        central = pd.Series({c: score(V.loc[c].to_dict(), weights) for c in members.index}, dtype=float)
        base_win = central.idxmax() if len(central) else None
        ws = counts[s].get(base_win, 0) / total if base_win is not None else None
        mc, S, phi, variants = None, None, None, {}
        if len(members) >= 2:
            mc, S = montecarlo(members, vf, weights)
            phi = promethee(V[list(CRITERIA)], weights)
            for conc in (10, 200):
                variants[f"P(rank 1), concentration {conc}"] = montecarlo(members, vf, weights, concentration=conc)[0].set_index(["type", "level"])["P(rank 1)"].to_dict()
            variants["P(rank 1), no widening"] = montecarlo(members, vf, weights, widen=False)[0].set_index(["type", "level"])["P(rank 1)"].to_dict()
        res = {bars: decide(members, central, mc, S, ws, phi, b, one)
               for bars, b, one in (("as written", BARS, ONE_PASSER), ("bars lowered by 0.1", {k: v - 0.1 for k, v in BARS.items()}, ONE_PASSER),
                                    ("one-passer bar 10", BARS, 10.0))}
        results[s] = {"members": [f"{c[0]} {c[1]}" for c in members.index], "win share": ws, "decision": res, "variants": {k: {f"{a[0]} {a[1]}": v for a, v in d.items()} for k, d in variants.items()},
                      "winners over the factorial": {("none" if w is None else f"{w[0]} {w[1]}"): n / total for w, n in counts[s].items()},
                      "regret": {f"{c[0]} {c[1]}": {"share of specs in the set": r[0] / total, "mean score gap to the winner": r[1] / r[0] if r[0] else None} for c, r in regret[s].items() if r[0]}}
        for c in members.index:
            rows.append({"set": s, "type": c[0], "level": c[1], "central score": central[c], **{f"value {k}": V.loc[c, k] for k in CRITERIA},
                         "P(rank 1)": float(mc.set_index(["type", "level"]).loc[c, "P(rank 1)"]) if mc is not None else 1.0,
                         "PROMETHEE net flow": float(phi[c]) if phi is not None else np.nan,
                         "specs won (share of the factorial)": counts[s].get(c, 0) / total})
    rank = pd.DataFrame(rows)
    rank.to_csv(RANK, index=False)

    # which missing number would change the winner of decision.second; what would empty decision.first
    gaps = {}
    sec = rank[rank["set"] == "second"].sort_values("central score", ascending=False)
    if len(sec) >= 2:
        top, run = sec.iloc[0], sec.iloc[1]
        diff = top["central score"] - run["central score"]
        gaps = {k: {"value points the runner-up needs on this criterion alone": diff / (weights[k] / sum(weights.values()))} for k in CRITERIA}
    first_fac = fac[fac["set"] == "first"]
    empty_first = {k: first_fac.groupby(k).apply(lambda x: float(x.loc[x["winner"] == "none", "count"].sum() / x["count"].sum())).to_dict() for k in live}
    res = {"stamp": stamp, "step7_commit": step7["stamp"]["commit"], "candidates": len(cands), "factorial": {"specs": total, "evaluated": total // mult, "multiplicity": mult},
           "weights": weights, "sets": results, "runner-up gaps (decision.second)": gaps, "share of specs with no existing-resources passer, by factor level": empty_first,
           "inputs": {f.name: sha(f) for f in (GATE, GATE_REFS, CAPTURE, DEMAND, LABOUR_FILE, SCREEN)}, "files": {f.name: sha(f) for f in (INPUTS, RANK, FACTORIAL)}}
    STEP8.write_text(json.dumps(res, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "step8_decision.md").write_text("\n".join([
        "# Funnel step 8a: ranking and decision (generated)", "", f"Code commit {stamp['commit']}, run on {stamp['date']}, tracked files clean: {stamp['clean']}.", "",
        "## Decision", "", "```", json.dumps({s: r["decision"] for s, r in results.items()}, indent=1, default=str), "```", "",
        "## Candidates in the sets", "", md_table(rank.round(3)), "",
        "## Inputs", "", md_table(cands.drop(columns=["central titles"]).reset_index(drop=True).round(3))]) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=1, ensure_ascii=False, default=str), flush=True)


if __name__ == "__main__":
    main()
