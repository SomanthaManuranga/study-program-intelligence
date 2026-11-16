"""Funnel step 7a: the order in which candidates are tried at the feasibility gate (configs/funnel.yaml: shortlist,
ranking.value_functions; criteria in docs/criteria_funnel_step7.md)

Run from the repository root, from committed code on a clean tree, after analysis.funnel_capture:

    python -m study_program_intelligence.analysis.funnel_shortlist

Every unit of the primary list gets the pre-gate score: the ranking's central weighted score with fit replaced by the
fit proxy and feasibility left out, weights renormalised. A merged candidate (group x level) is represented by its unit
with the highest score. The list is the order of the gate; nothing is edited by hand.
Outputs: data/interim/funnel2_shortlist.csv (every primary unit), funnel2_gate_order.csv (one row per candidate),
funnel2_step7a.json; reports/funnel2/step7a_shortlist.md.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import yaml

from .funnel_capture import CAPTURE
from .funnel_common import INTERIM, REPO_ROOT, REPORTS, config, md_table, run_stamp
from .funnel_demand import DEMAND
from .funnel_types import sha
from .funnel_units import CALIBRATION, QUOTIENT_FROM, SCREEN, STEP3

LABOUR = INTERIM / "funnel2_labour.csv"
COHERENCE = REPO_ROOT / "docs" / "funnel_type_coherence.csv"
SHORTLIST, ORDER, STEP7A = INTERIM / "funnel2_shortlist.csv", INTERIM / "funnel2_gate_order.csv", INTERIM / "funnel2_step7a.json"
WEIGHTS = {"demand": "student_demand", "labour": "labour_relevance", "fit": "institutional_fit", "differentiation": "differentiation", "regional": "regional_contribution"}
TRIED_MAX = 20                                # shortlist.gate_list


def value(x, anchors: dict, log: bool = False) -> np.ndarray:
    """A value function of the rule: piecewise linear between its anchors on the 1-5 scale, clipped; a missing input
    has the value 1 (ranking.inputs.missing). With log the line is straight on the logarithm of the input."""
    x = np.asarray(x, float)
    xs = np.array(sorted(float(k) for k in anchors))
    ys = np.array([float(anchors[k]) for k in sorted(anchors, key=float)])
    f = (lambda v: np.log(np.maximum(v, 1e-9))) if log else (lambda v: v)
    out = np.interp(f(x), f(xs), ys)
    return np.where(np.isfinite(x), out, 1.0)


def scores(u: pd.DataFrame, vf: dict, weights: dict, bar: float, top: float) -> pd.DataFrame:
    """The 1-5 values of every criterion and the pre-gate score of every unit (columns of u are the inputs)."""
    v = pd.DataFrame(index=u.index)
    trend = value(u["trend"], vf["trend_pct_per_year"])
    v["trend value"] = np.where(u["trend validated"].to_numpy(bool), trend, np.minimum(trend, 3.0))      # ranking.inputs.trend: capped at 3 if not validated
    v["net-new value"] = value(u["net_new"], vf["net_new"])
    v["demand"] = (v["trend value"] + v["net-new value"]) / 2
    v["labour"] = value(u["ads"], vf["labour_ads_within_100km_log"], log=True)
    v["offers half"] = value(u["similar_150"], vf["differentiation_similar_offers_within_150km"])
    v["quotient half"] = np.where(u["quotient used"].to_numpy(bool), value(u["quotient"], vf["differentiation_bavarian_quotient"]), np.nan)
    v["differentiation"] = np.where(u["quotient used"].to_numpy(bool), (v["offers half"] + v["quotient half"]) / 2, v["offers half"])
    v["regional"] = value(u["kept"], vf["regional_share_of_net_new_kept_in_region"])
    v["fit"] = value(u["emi score"], {bar: 1, top: 5})                                                    # shortlist.fit_proxy
    total = sum(weights[w] for w in WEIGHTS.values())
    v["pre-gate score"] = sum(v[k] * weights[w] for k, w in WEIGHTS.items()) / total
    return v


def main() -> None:
    stamp, rules = run_stamp(), config()
    vf = rules["ranking"]["value_functions"]
    weights = yaml.safe_load((REPO_ROOT / "configs" / "analysis.yaml").read_text(encoding="utf-8"))["weights"]
    step3 = json.loads(STEP3.read_text(encoding="utf-8"))
    s = pd.read_csv(SCREEN, float_precision="round_trip")
    key = ["type", "level"]
    dm = pd.read_csv(DEMAND, float_precision="round_trip").set_index(key)
    cp = pd.read_csv(CAPTURE, float_precision="round_trip").set_index(key)
    lb = pd.read_csv(LABOUR).set_index(key)
    cal = pd.read_csv(CALIBRATION, float_precision="round_trip")
    bar, top = float(step3["calibration"]["bar"]), float(cal.loc[cal["emi"].astype(bool), "score"].quantile(0.9))
    p = s[s["primary"]].reset_index(drop=True)
    idx = pd.MultiIndex.from_frame(p[key])
    u = pd.DataFrame({"trend": dm["trend German BY %/yr"].reindex(idx).to_numpy(), "trend validated": p["trend validated"].to_numpy(bool),
                      "net_new": cp["net-new central"].reindex(idx).to_numpy(),
                      "ads": np.where(lb["labour input"].reindex(idx).to_numpy() == "ok", lb["ads within 100 km (median keyword)"].reindex(idx).to_numpy(), np.nan),
                      "similar_150": p["group: similar within 150 km"].to_numpy(float), "quotient": p["group: bavarian quotient"].to_numpy(float),
                      "quotient used": (p["group: similar offers"] >= QUOTIENT_FROM).to_numpy(),
                      "kept": cp["kept in the region (central)"].reindex(idx).to_numpy(), "emi score": p["emi score"].to_numpy(float)})
    v = scores(u, vf, weights, bar, top)
    coh = pd.read_csv(COHERENCE).set_index("type")["mixed"].astype(bool)
    flags = cp.reindex(idx)
    out = pd.concat([p[key + ["kind", "group", "group size", "group types", "central titles", "institutions", "popularity tier"]], u.drop(columns=["emi score"]), p[["emi score"]], v], axis=1)
    out["type is mixed (Step 3 reading)"] = coh.reindex(p["type"]).fillna(False).to_numpy()
    out["below the minimum cohort"] = flags["below the minimum cohort"].to_numpy(bool)
    out["thin anchor"] = flags["fewer than 2 Bavarian offers in the pool"].to_numpy(bool)
    out["gross central"] = flags["gross central"].to_numpy()
    out = out.sort_values(["pre-gate score", "type", "level"], ascending=[False, True, True], kind="mergesort").reset_index(drop=True)      # ties: lower type, bachelor before master
    out["rank of the unit"] = np.arange(1, len(out) + 1)
    rep = out.drop_duplicates(["group", "level"], keep="first").reset_index(drop=True)                    # the representative: the group's best unit
    variants = out.groupby(["group", "level"])["type"].agg(lambda x: "; ".join(str(t) for t in x.iloc[1:]))
    rep["variants (other types of the candidate)"] = [variants[(g, lv)] for g, lv in zip(rep["group"], rep["level"])]
    rep.insert(0, "gate order", np.arange(1, len(rep) + 1))
    out.to_csv(SHORTLIST, index=False)
    rep.to_csv(ORDER, index=False)
    first = rep.head(TRIED_MAX)
    res = {"stamp": stamp, "units": len(out), "candidates": len(rep), "weights": {k: weights[w] for k, w in WEIGHTS.items()}, "fit_proxy": {"bar": bar, "value 5 at": top},
           "score_quartiles": [round(float(x), 3) for x in rep["pre-gate score"].quantile([0.25, 0.5, 0.75])], "highest": round(float(rep["pre-gate score"].max()), 3),
           "first_20": {"bachelor": int((first["level"] == "bachelor").sum()), "master": int((first["level"] == "master").sum()), "mixed types": int(first["type is mixed (Step 3 reading)"].sum()),
                        "below the minimum cohort": int(first["below the minimum cohort"].sum()), "thin anchor": int(first["thin anchor"].sum()),
                        "trend not validated": int((~first["trend validated"]).sum()), "score of the 20th": round(float(first["pre-gate score"].iloc[-1]), 3)},
           "units_with_a_missing_input": {c: int(u[c].isna().sum()) for c in ("trend", "net_new", "ads", "kept")},
           "inputs": {f.name: sha(f) for f in (SCREEN, DEMAND, CAPTURE, LABOUR, CALIBRATION, COHERENCE)}, "files": {f.name: sha(f) for f in (SHORTLIST, ORDER)}}
    STEP7A.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    show = ["gate order", "type", "level", "central titles", "pre-gate score", "demand", "labour", "fit", "differentiation", "regional", "net_new", "ads", "type is mixed (Step 3 reading)", "below the minimum cohort", "thin anchor"]
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "step7a_shortlist.md").write_text("\n".join([
        "# Funnel step 7a: the order of the gate (generated)", "",
        f"Code commit {stamp['commit']}, run on {stamp['date']}, tracked files clean: {stamp['clean']}.", "",
        f"- {len(out)} units, {len(rep)} candidates. Weights (feasibility left out, renormalised): {res['weights']}. Fit proxy: 1 at {bar:.4f}, 5 at {top:.4f}.",
        f"- First 20: {res['first_20']}.", "",
        "## The first 40 candidates", "", md_table(rep.head(40).assign(**{"central titles": rep["central titles"].head(40).str.slice(0, 60)})[show].round(2))]) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
