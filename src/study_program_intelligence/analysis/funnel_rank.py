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
OFFERS_FULL_RANGE = True       # screen.competition.validity_check.second_failure: the check of "similar" failed twice, so the offers half of the
                               # differentiation value takes the range 1 to 5 (triangular, mode at its central value); the p75/p95 counts are reported
PROMETHEE_P = 4.0                                               # ranking.cross_check: preference threshold, the full scale
BARS = {"rank_1": 0.5, "beats_runner_up": 0.8, "win_share": 0.5}   # decision.rule.two_or_more
ONE_PASSER = 15.0                                               # decision.rule.one


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


def unit_inputs(key: tuple[int, str], rr: pd.DataFrame, src: dict) -> dict:
    """The low / central / high of every input of one unit (type, level), with the gate figures of the references rr."""
    cp, dm, lb, sc = src["capture"], src["demand"], src["labour"], src["screen"]
    t_lo, t_c, t_hi = trend_windows(*key, src["offers"], src["smap"], src["tables"])
    ok = lb.at[key, "labour input"] == "ok"
    q_used = bool(sc.at[key, "group: similar offers"] >= QUOTIENT_FROM)
    elsewhere = float(sc.at[key, "trend elsewhere %/yr"]) if "trend elsewhere %/yr" in sc.columns else np.nan
    return {
        "type": key[0], "level": key[1], "central titles": sc.at[key, "central titles"],
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
        "trend elsewhere": elsewhere, "tier 2 shown": bool(np.isfinite(elsewhere) and elsewhere >= 0),            # screen.regional_gap.popularity_evidence.tier_2
        "regional low": float(cp.at[key, "kept in the region (pessimistic)"]), "regional central": float(cp.at[key, "kept in the region (central)"]), "regional high": float(cp.at[key, "kept in the region (optimistic)"]),
        "references": len(rr), "ref names": "; ".join(rr["ref"]),
        "overlaps": "; ".join(f"{x:.3f}" for x in rr["overlap"]),
        "overlaps without two-module covers": "; ".join(f"{x:.3f}" for x in rr["overlap without two-module covers (sensitivity)"]),
        "overlaps with covered-but-unsure rows not covered": "; ".join(f"{x:.3f}" for x in rr["overlap with covered-but-unsure rows not covered (sensitivity)"]),
        "feasibility shares": "; ".join(f"{x:.3f}" for x in rr["share of new ECTS in N"]),
        "one-programme shares": "; ".join(f"{x:.3f}" for x in rr["largest share from one programme"]),
        "lab shares": "; ".join(f"{x:.3f}" for x in rr["share lab"]), "X ECTS": "; ".join(f"{x:.3f}" for x in rr["X ECTS"]), "N ECTS": "; ".join(f"{x:.3f}" for x in rr["N ECTS"]), "T ECTS": "; ".join(f"{x:.3f}" for x in rr["T ECTS"]),
        "new teaching ECTS": float(rr["new teaching ECTS (scaled)"].mean()), "professor-equivalents": float(rr["professor-equivalents"].mean()),
    }


def sources() -> dict:
    return {"capture": pd.read_csv(CAPTURE, float_precision="round_trip").set_index(["type", "level"]),
            "demand": pd.read_csv(DEMAND, float_precision="round_trip").set_index(["type", "level"]),
            "labour": pd.read_csv(LABOUR_FILE).set_index(["type", "level"]), "screen": pd.read_csv(SCREEN, float_precision="round_trip").set_index(["type", "level"]),
            "offers": pd.read_csv(OFFER_TYPES, low_memory=False, dtype={"programme_id": str}), "smap": pd.read_csv(SUBJECT_MAP).set_index("label")["code"].to_dict(),
            "tables": tables()}


def inputs(rules: dict, src: dict | None = None) -> pd.DataFrame:
    """One row per gate candidate with the low / central / high of every input and the flags that decide widenings."""
    g, refs = pd.read_csv(GATE), pd.read_csv(GATE_REFS)
    src = src or sources()
    rows = []
    for r in g.itertuples():
        rr = refs[(refs["type"] == r.type) & (refs["level"] == r.level)].sort_values("ref")
        rows.append({**unit_inputs((int(r.type), r.level), rr, src), "verdict": r.verdict})
    out = pd.DataFrame(rows)
    out["missing inputs"] = ["; ".join(c for c in ("trend central", "net-new central", "labour central", "fit central", "feasibility central", "regional central") if not np.isfinite(r[c])) for _, r in out.iterrows()]
    return out


def values(c: pd.Series, vf: dict, spec: dict) -> dict[str, float]:
    """The central 1-5 value of every criterion of one candidate under a spec (stress factors). A missing input has the
    value 1 (ranking.inputs.missing). Under "references: primary only" fit and feasibility come from the primary
    reference (reference a)."""
    anchors = (lambda a, log=False: widened(a, log)) if spec["value_anchors"] == "widened" else (lambda a, log=False: a)
    v = lambda x, a, log=False: float(value([x], anchors(a, log), log=log)[0])
    trend = v(c["trend central"], vf["trend_pct_per_year"])
    if np.isfinite(c["trend central"]) and not c["trend validated"] and spec["widenings"] == "as written":
        trend = min(trend, 3.0)
    nn = c["net-new central"] * spec["net-new factor"](c)
    first = lambda col: float(str(c[col]).split("; ")[0])
    fit = first("overlaps") if spec["references"] == "primary only" else c["fit central"]
    feas = first("feasibility shares") if spec["references"] == "primary only" else c["feasibility central"]
    out = {"demand": (trend + v(nn, vf["net_new"])) / 2,
           "labour": v(c[f"labour {'central' if spec['labour_measure'] == 'median keyword' else 'high'}"], vf["labour_ads_within_100km_log"], True),
           "fit": ((5.0 if fit >= 0.40 else 1.0) if np.isfinite(fit) else 1.0) if spec["fit_value"] == "flat" else v(fit, vf["fit_overlap"]),
           "feasibility": v(feas, vf["feasibility_share_of_new_ects_in_N"]),
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
    ov, one, lab, x, n = split(spec.get("overlap column", "overlaps")), split("one-programme shares"), split("lab shares"), split("X ECTS"), split("N ECTS")
    idx = [0] if spec["references"] == "primary only" else list(range(len(ov)))
    lo, hi = spec["overlap_band"]
    one_max = np.inf if spec["one_programme_max"] == "none" else float(spec["one_programme_max"])
    ok = []
    for i in idx:
        if spec["overlap_reading"] == "lower end overall, upper end on one programme":
            ok.append(ov[i] >= lo and one[i] <= one_max and lab[i] == 0)                 # band_reading: the upper end applies to one programme
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


# the factors a cached value or gate result depends on (every factor values() or passes() reads)
VALUE_KEYS = ("pool_trend", "master_transition", "fit_value", "differentiation", "labour_measure", "value_anchors", "widenings", "references")
GATE_KEYS = ("min_cohort", "master_transition", "overlap_band", "overlap_reading", "one_programme_max", "N_cap", "references")


def net_new_factor(spec: dict):
    def f(c: pd.Series) -> float:
        k = {"unprojected": 1.0, "projected": c["projection factor"], "foreign added flat": 1 / (1 - c["foreign share"])}[spec["pool_trend"]]
        return k * (spec["master_transition"] / 0.5 if c["level"] == "master" else 1.0)
    return f


def montecarlo(cands: pd.DataFrame, vf: dict, weights: dict, concentration: float = CONCENTRATION, widen: bool = True, draws: int = DRAWS, seed: int = SEED,
               offers: str = "triangular", tier_slope: float = 0.0) -> tuple[pd.DataFrame, np.ndarray]:
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
        if t is not None and not c["trend validated"] and widen:
            trend = np.minimum(trend, 3.0) + rng.uniform(-WIDEN, WIDEN, draws)
        nn = draw("net-new", log=True)
        vv["demand"] = (np.clip(trend, 1, 5) + value(nn, vf["net_new"])) / 2
        lab = draw("labour", log=True)
        vv["labour"] = value(lab, vf["labour_ads_within_100km_log"], log=True) if lab is not None else np.ones(draws)
        fit, feas = draw("fit"), draw("feasibility")
        vv["fit"] = value(fit, vf["fit_overlap"]) if fit is not None else np.ones(draws)
        vv["feasibility"] = value(feas, vf["feasibility_share_of_new_ects_in_N"]) if feas is not None else np.ones(draws)
        reg = draw("regional")
        vv["regional"] = value(reg, vf["regional_share_of_net_new_kept_in_region"]) if reg is not None else np.ones(draws)
        mode = float(value([c["offers 90"]], vf["differentiation_similar_offers_within_150km"])[0])
        if not OFFERS_FULL_RANGE:
            offers_v = value(np.full(draws, c["offers 90"]), vf["differentiation_similar_offers_within_150km"])
        else:
            offers_v = rng.triangular(1.0, mode, 5.0, draws) if offers == "triangular" else rng.uniform(1.0, 5.0, draws)
        if c["quotient used"]:
            q = value(np.full(draws, c["quotient"]), vf["differentiation_bavarian_quotient"])
            tier2 = np.isfinite(c.get("trend elsewhere", np.nan)) and c["trend elsewhere"] >= tier_slope
            if not tier2 and widen:
                q = np.clip(q + rng.uniform(-WIDEN, WIDEN, draws), 1, 5)
            vv["differentiation"] = (offers_v + q) / 2
        else:
            vv["differentiation"] = offers_v
        S[:, j] = sum(np.clip(vv[k], 1, 5) * W[:, i] for i, k in enumerate(keys))
    tie_order = np.lexsort((np.array([c != "bachelor" for c in cands["level"]]), cands["type"].to_numpy()))      # definitions.ties
    S_t = S[:, tie_order]
    order = tie_order[np.argsort(-S_t, axis=1, kind="stable")]
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


def decide(cands: pd.DataFrame, central: pd.Series, mc: pd.DataFrame | None, S: np.ndarray | None, win_share: float | None, phi: pd.Series | None, bars: dict, one_bar: float,
           closest: dict | None = None) -> dict:
    """decision.rule for one set."""
    if len(cands) == 0:
        return {"outcome": "no candidate passes", **({"closest": closest} if closest else {})}
    if len(cands) == 1:
        c = cands.iloc[0]
        nn = float(c["net-new central"])
        out = {"outcome": "recommend" if nn >= one_bar else "shortlist", "candidate": [int(c["type"]), c["level"]], "net-new central": nn, "bar": one_bar}
        for k in ("new teaching ECTS", "professor-equivalents", "X ECTS", "N ECTS", "T ECTS", "references", "fit central"):
            if k in c.index:
                out[k] = c[k] if isinstance(c[k], str) else float(c[k])
        return out
    tie = lambda c, x: (-x, c[0], c[1] != "bachelor")
    order = sorted(central.index, key=lambda c: tie(c, central[c]))
    top, second = order[0], order[1]
    p1 = float(mc.set_index(["type", "level"]).loc[top, "P(rank 1)"])
    i, j = list(central.index).index(top), list(central.index).index(second)
    beats = float((S[:, i] > S[:, j]).mean())
    prom_top = sorted(phi.index, key=lambda c: tie(c, phi[c]))[0]
    res = {"candidate": [int(top[0]), top[1]], "runner-up": [int(second[0]), second[1]], "P(rank 1)": p1, "P(beats the runner-up)": beats, "win share": win_share,
           "PROMETHEE rank 1": [int(prom_top[0]), prom_top[1]]}
    for k in ("new teaching ECTS", "professor-equivalents", "X ECTS", "N ECTS", "T ECTS", "references", "fit central"):
        if k in cands.columns:
            x = cands.loc[top, k]
            res[k] = x if isinstance(x, str) else float(x)
    if prom_top != top:
        res["outcome"] = "shortlist (PROMETHEE disagrees on rank 1)"
    elif p1 >= bars["rank_1"] and beats >= bars["beats_runner_up"] and (win_share or 0) >= bars["win_share"]:
        res["outcome"] = "recommend"
    else:
        res["outcome"] = "shortlist"
    return res


INFORMATIK_TYPES = (13, 242)    # the two large plain "Informatik" types of Step 2 (242 the largest), for the stated sensitivity of the recommendation


def sentences(res: dict, cands: pd.DataFrame) -> list[str]:
    """The decision sentences of decision.first and decision.second, generated from the stored figures. N = new modules by
    current lecturers, T = teaching assignments within the rule's cap, X = teaching beyond what existing staff can take."""
    out = []
    f = lambda x: " and ".join(f"{float(v):.1f}" for v in str(x).split("; "))
    d1 = res["sets"]["first"]["decision"]["as written"]
    if d1["outcome"] == "recommend":
        out.append(f"- decision.first: recommend type {d1['candidate'][0]} {d1['candidate'][1]} (a general computer science / Informatik bachelor; "
                   f"titles: {cands.loc[tuple(d1['candidate']), 'central titles'][:60]}); {d1['net-new central']:.1f} first-years new to OTH a year (central); "
                   f"new teaching {d1['new teaching ECTS']:.1f} ECTS: {f(d1['N ECTS'])} ECTS new modules by current lecturers (N) and {f(d1['T ECTS'])} ECTS by a teaching "
                   f"assignment (T), none beyond that (X {f(d1['X ECTS'])}); about {d1['professor-equivalents']:.2f} professor-equivalents; no new lab. "
                   f"It is the only existing-resources passer; it rests on {int(d1['references'])} handbook(s) and wins {res['sets']['first']['win share']:.0%} of the stress grid "
                   f"(the rest has no passer at all).")
    elif d1["outcome"] == "no candidate passes":
        out.append(f"- decision.first: no candidate passes with existing resources; closest: {d1.get('closest', '-')}.")
    else:
        out.append(f"- decision.first: {d1['outcome']}.")
    d2 = res["sets"]["second"]["decision"]["as written"]
    if "candidate" in d2:
        out.append(f"- decision.second (for information, outside the scope): first among the band passers is type {d2['candidate'][0]} {d2['candidate'][1]} "
                   f"(P(rank 1) {d2.get('P(rank 1)', 1):.2f}, win share {res['sets']['second']['win share']:.0%}); "
                   + "; ".join(f"type {c} needs {f(cands.loc[(int(c.split()[0]), c.split()[1]), 'T ECTS'])} ECTS by teaching assignments (T) and "
                               f"{f(cands.loc[(int(c.split()[0]), c.split()[1]), 'X ECTS'])} ECTS beyond what existing staff can take (X), "
                               f"{cands.loc[(int(c.split()[0]), c.split()[1]), 'professor-equivalents']:.2f} professor-equivalents: outside the scope, needs new expertise"
                               for c in res["sets"]["second"]["members"] if any(float(x) > 1e-9 for x in str(cands.loc[(int(c.split()[0]), c.split()[1]), "X ECTS"]).split("; "))) + ".")
    return out


def main() -> None:
    stamp, rules = run_stamp(), config()
    step7 = json.loads(STEP7.read_text(encoding="utf-8"))
    for f in (GATE, GATE_REFS):
        if step7["files"][f.name] != sha(f):
            raise SystemExit(f"{f.name} is not the file Step 7 wrote")
    vf = rules["ranking"]["value_functions"]
    aw = yaml.safe_load((REPO_ROOT / "configs" / "analysis.yaml").read_text(encoding="utf-8"))["weights"]
    weights = {k: float(aw[v]) for k, v in CRITERIA.items()}
    src = sources()
    cands = inputs(rules, src)
    cands.to_csv(INPUTS, index=False)
    idx = pd.MultiIndex.from_frame(cands[["type", "level"]])
    cands.index = idx

    # the factorial: sets and winners under every combination of the factors that can change them
    live = [k for k, (lv, used) in FACTORS.items() if used]
    mult = int(np.prod([len(lv) for k, (lv, used) in FACTORS.items() if not used]))
    total = int(np.prod([len(lv) for lv, _ in FACTORS.values()]))
    counts = {s: {} for s in ("first", "second")}
    regret = {s: {c: [0, 0.0] for c in idx} for s in ("first", "second")}
    hkey = lambda spec, keys: tuple(str(spec[k]) for k in keys)
    vcache, gcache, by_factor = {}, {}, {}
    for combo in itertools.product(*[FACTORS[k][0] for k in live]):
        spec = dict(zip(live, combo))
        vk, gk = hkey(spec, VALUE_KEYS), hkey(spec, GATE_KEYS)
        if vk not in vcache:
            spec["net-new factor"] = net_new_factor(spec)
            vcache[vk] = {c: values(cands.loc[c], vf, spec) for c in idx}
        if gk not in gcache:
            gcache[gk] = {c: passes(cands.loc[c], spec) for c in idx}
        flags, vals = gcache[gk], vcache[vk]
        feas = spec["feasibility_value"] == "included"
        sc_ = {c: score(vals[c], weights, feas) for c in idx}
        for s, k in (("first", 1), ("second", 0)):
            members = [c for c in idx if flags[c][k]]
            win = max(members, key=lambda c: (sc_[c], -c[0], c[1] == "bachelor")) if members else None   # definitions.ties
            counts[s][win] = counts[s].get(win, 0) + mult
            for c in members:
                regret[s][c][0] += mult
                regret[s][c][1] += mult * (sc_[win] - sc_[c])
            w_name = "none" if win is None else f"{win[0]} {win[1]}"
            for f in live:
                kk = (s, f, str(spec[f]), w_name)
                by_factor[kk] = by_factor.get(kk, 0) + mult
    fac = pd.DataFrame([{"set": s, "factor": f, "level": lv, "winner": w, "count": n} for (s, f, lv, w), n in by_factor.items()])
    fac.to_csv(FACTORIAL, index=False)
    assert all(sum(v.values()) == total for v in counts.values())

    # base spec: sets, central scores, Monte Carlo, PROMETHEE, decision
    base = dict(BASE, **{"net-new factor": net_new_factor(BASE)})
    rows, results = [], {}
    for s, k in (("first", 1), ("second", 0)):
        members = cands[[passes(cands.loc[c], base)[k] for c in idx]]
        members = members.reset_index(drop=True).set_index(pd.MultiIndex.from_frame(members[["type", "level"]])) if len(members) else members
        V = pd.DataFrame({c: values(members.loc[c], vf, base) for c in members.index}).T if len(members) else pd.DataFrame()
        central = pd.Series({c: score(V.loc[c].to_dict(), weights) for c in members.index}, dtype=float)
        base_win = sorted(central.index, key=lambda c: (-central[c], c[0], c[1] != "bachelor"))[0] if len(central) else None
        ws = counts[s].get(base_win, 0) / total if base_win is not None else None
        mc, S, phi, variants, decisions_alt = None, None, None, {}, {}
        if len(members) >= 2:
            mc, S = montecarlo(members, vf, weights)
            phi = promethee(V[list(CRITERIA)], weights)
            for conc in (10, 200):
                variants[f"P(rank 1), concentration {conc}"] = montecarlo(members, vf, weights, concentration=conc)[0].set_index(["type", "level"])["P(rank 1)"].to_dict()
            variants["P(rank 1), no widening"] = montecarlo(members, vf, weights, widen=False)[0].set_index(["type", "level"])["P(rank 1)"].to_dict()
            for label, kw in (("concentration 10", {"concentration": 10}), ("offers half uniform on 1-5", {"offers": "uniform"}), ("tier-2 slope -1", {"tier_slope": -1.0})):
                m_, S_ = montecarlo(members, vf, weights, **kw)
                d_ = decide(members, central, m_, S_, ws, phi, BARS, ONE_PASSER)
                decisions_alt[label] = {"P(rank 1) of the top": d_.get("P(rank 1)"), "P(beats the runner-up)": d_.get("P(beats the runner-up)"), "outcome": d_["outcome"]}
        near = cands.assign(o=cands["fit central"]).sort_values("o", ascending=False).iloc[0]
        gate = pd.read_csv(GATE).set_index(["type", "level"])
        closest = {"candidate": f"{int(near['type'])} {near['level']}", "verdict": near["verdict"], "mean overlap": float(near["fit central"]), "X ECTS": near["X ECTS"], "N ECTS": near["N ECTS"],
                   "lacks": (str(gate.at[(int(near["type"]), near["level"]), "why"]) if isinstance(gate.at[(int(near["type"]), near["level"]), "why"], str) else "")
                            + ("; teaching beyond what existing staff can take (X ECTS)" if any(float(x) > 1e-9 for x in str(near["X ECTS"]).split("; ")) else "")}
        res = {bars: decide(members, central, mc, S, ws, phi, b, one, closest)
               for bars, b, one in (("as written", BARS, ONE_PASSER), ("bars lowered by 0.1", {k: v - 0.1 for k, v in BARS.items()}, ONE_PASSER),
                                    ("one-passer bar 10", BARS, 10.0))}
        if s == "second":                                # decision.second is reported for information, never as a recommendation
            for r_ in res.values():
                r_["outcome"] = {"recommend": "first among the band passers (for information, never a recommendation)"}.get(r_["outcome"], r_["outcome"] + " (for information)")
        results[s] = {"members": [f"{c[0]} {c[1]}" for c in members.index], "win share": ws, "decision": res, "decision under other readings": decisions_alt, "variants": {k: {f"{a[0]} {a[1]}": v for a, v in d.items()} for k, d in variants.items()},
                      "winners over the factorial": {("none" if w is None else f"{w[0]} {w[1]}"): n / total for w, n in counts[s].items()},
                      "regret": {f"{c[0]} {c[1]}": {"share of specs in the set": r[0] / total, "mean score gap to the winner": r[1] / r[0] if r[0] else None} for c, r in regret[s].items() if r[0]}}
        for c in members.index:
            rows.append({"set": s, "type": c[0], "level": c[1], "central score": central[c], **{f"value {k}": V.loc[c, k] for k in CRITERIA},
                         "P(rank 1)": float(mc.set_index(["type", "level"]).loc[c, "P(rank 1)"]) if mc is not None else 1.0,
                         "PROMETHEE net flow": float(phi[c]) if phi is not None else np.nan,
                         "specs won (share of the factorial)": counts[s].get(c, 0) / total})
    rank = pd.DataFrame(rows)
    rank.to_csv(RANK, index=False)
    step7_sens = {}
    for name, col in (("without two-module covers", "overlaps without two-module covers"), ("covered-but-unsure rows not covered", "overlaps with covered-but-unsure rows not covered")):
        spec = dict(base, **{"overlap column": col})
        m = cands[[passes(cands.loc[c], spec)[1] for c in idx]]
        closest = cands.assign(o=[float(np.mean([float(x) for x in str(v).split("; ")])) for v in cands[col]]).sort_values("o", ascending=False).iloc[0]
        step7_sens[name] = {"existing-resources passers": [f"{c[0]} {c[1]}" for c in m.index],
                            "decision.first": decide(m, pd.Series(0.0, index=m.index), None, None, None, None, BARS, ONE_PASSER)["outcome"],
                            "closest (mean overlap)": f"{int(closest['type'])} {closest['level']}: {closest['o']:.3f}"}

    # which missing number would change the winner of decision.second; what would empty decision.first
    gaps = {}
    sec = rank[rank["set"] == "second"].assign(b=lambda x: x["level"] != "bachelor").sort_values(["central score", "type", "b"], ascending=[False, True, True])
    if len(sec) >= 2:
        top, run = sec.iloc[0], sec.iloc[1]
        diff = top["central score"] - run["central score"]
        gaps = {}
        for k in CRITERIA:
            need = diff / (weights[k] / sum(weights.values()))
            room = 5.0 - float(run[f"value {k}"])
            gaps[k] = {"value points the runner-up needs on this criterion alone": need, "room it has": room, "can flip alone": bool(need <= room)}
    # the recommended unit as the plain Informatik type: the gate result of the recommended candidate with the
    # competition, demand, labour and regional inputs of the largest Informatik type of the same level (stated sensitivity)
    informatik = {}
    if results["first"]["members"]:
        t1, lv1 = results["first"]["members"][0].split(" ")
        t1 = int(t1)
        refs = pd.read_csv(GATE_REFS)
        rr = refs[(refs["type"] == t1) & (refs["level"] == lv1)].sort_values("ref")
        for alt_type in INFORMATIK_TYPES:
            alt = pd.Series({**unit_inputs((alt_type, lv1), rr, src), "verdict": "existing-resources passer"})
            alt_in = passes(alt, base)
            others = cands[[passes(cands.loc[c], base)[0] and c != (t1, lv1) for c in idx]]
            group = pd.concat([pd.DataFrame([alt]), others.reset_index(drop=True)], ignore_index=True)
            group.index = pd.MultiIndex.from_frame(group[["type", "level"]])
            Vg = pd.DataFrame({c: values(group.loc[c], vf, base) for c in group.index}).T
            cg = pd.Series({c: score(Vg.loc[c].to_dict(), weights) for c in group.index}, dtype=float)
            mg, Sg = montecarlo(group, vf, weights)
            dg = decide(group, cg, mg, Sg, None, promethee(Vg[list(CRITERIA)], weights), BARS, ONE_PASSER) if len(group) >= 2 else {}
            informatik[f"{alt_type} {lv1}"] = {
                "net-new central": alt["net-new central"], "gross central": alt["gross central"], "similar offers within 150 km": alt["offers 90"],
                "kept in the region": alt["regional central"], "labour (median keyword)": alt["labour central"], "labour (largest keyword)": alt["labour high"],
                "labour artefact": bool(alt["labour central"] < 10 <= alt["labour high"]),
                "existing-resources passer at min cohort 20": bool(alt_in[1]), "at min cohort 25": bool(passes(alt, dict(base, min_cohort=25))[1]),
                "decision.first": decide(pd.DataFrame([alt]) if alt_in[1] else pd.DataFrame(), pd.Series([0.0]), None, None, None, None, BARS, ONE_PASSER)["outcome"],
                "central score": float(cg[(alt_type, lv1)]), "central scores of the other band passers": {f"{c[0]} {c[1]}": float(cg[c]) for c in group.index if c != (alt_type, lv1)},
                "decision.second: first (for information)": dg.get("candidate"), "decision.second: P(rank 1) of the first": dg.get("P(rank 1)")}
    first_fac = fac[fac["set"] == "first"]
    empty_first = {f: {lv: float(g.loc[g["winner"] == "none", "count"].sum() / g["count"].sum()) for lv, g in ff.groupby("level")} for f, ff in first_fac.groupby("factor")}
    res = {"stamp": stamp, "step7_commit": step7["stamp"]["commit"], "candidates": len(cands), "factorial": {"specs": total, "evaluated": total // mult, "multiplicity": mult},
           "weights": weights, "sets": results, "decision.first under the Step 7 sensitivities": step7_sens, "recommended unit as plain Informatik": informatik, "runner-up gaps (decision.second)": gaps, "share of specs with no existing-resources passer, by factor level": empty_first,
           "competition counts": "not validated (Step 3: the check of similar failed twice); the offers half of differentiation takes the range 1 to 5 in the Monte Carlo",
           "inputs": {f.name: sha(f) for f in (GATE, GATE_REFS, CAPTURE, DEMAND, LABOUR_FILE, SCREEN)}, "files": {f.name: sha(f) for f in (INPUTS, RANK, FACTORIAL)}}
    res["sentences"] = sentences(res, cands)
    STEP8.write_text(json.dumps(res, indent=2, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "step8_decision.md").write_text("\n".join([
        "# Funnel step 8a: ranking and decision (generated)", "", f"Code commit {stamp['commit']}, run on {stamp['date']}, tracked files clean: {stamp['clean']}.", "",
        "## Decision", "", *res["sentences"], "", "```", json.dumps({s: r["decision"] for s, r in results.items()}, indent=1, default=str), "```", "",
        "## Candidates in the sets", "", md_table(rank.round(3)), "",
        "## Inputs", "", md_table(cands.drop(columns=["central titles"]).reset_index(drop=True).round(3))]) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=1, ensure_ascii=False, default=str), flush=True)


if __name__ == "__main__":
    main()
