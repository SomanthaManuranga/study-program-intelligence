"""MCDA + Monte Carlo ranking of the three shortlisted options (Step 49).

Run from the repository root:

    python -m study_program_intelligence.analysis.ranking

Inputs: configs/analysis.yaml (weights, Monte Carlo settings), configs/scores.yaml (score sheet, reviewed by Soma),
data/interim/option_scenarios.csv (capture + cannibalisation per option, analysis/options.py).
Per draw (10,000, seed 42):
  - weights ~ Dirichlet(concentration x base weights);
  - ONE common uniform u sets every option's capture-model quantile (net new first-years and (c) kept in region),
    because the anchor uncertainty is shared model error and should not flip the ranking at random;
  - hand scores and trend scores ~ triangular(low, central, high), independent per option and criterion;
  - student_demand = 0.5 x capture score + 0.5 x trend score; capture score = 1 + 4 ln(n/10)/ln 8 (clipped 1-5);
    regional_contribution = 1 + 4 ln(max(c,1))/ln 16 (clipped 1-5);
  - feasibility gate: an option whose central feasibility rating is 1 is excluded (kill rule 2).
Scenarios: base, and robotics with 50 % cannibalisation (Huff/IIA understates substitution with OTH's KI B.Sc.).
Sensitivity: leave-one-criterion-out (weights renormalised), independent capture draws (no common factor), the
earlier skewed robotics fit/feasibility range 2 / 3 / 5, and demand trend scores from German first-years / graduates
only (scores.yaml sensitivity.trend_german, all three options).
Outputs: reports/ranking.md, data/interim/ranking_summary.csv, data/interim/ranking_loo.csv.

Equal-evidence candidates (`--candidates`): the same model on configs/scores_candidates.yaml and
data/interim/candidate_scenarios.csv (analysis/candidates.py). Candidates that fail the F1-F4 gate carry feasibility 1
and drop out as above. Scenarios: base; German-only trends; lenient feasibility gate; 50 % cannibalisation for the
candidates with a same-campus near-twin; AR/VR capture replaced by robotics' rows; AR/VR differentiation one step lower
(neighbouring countries); all AR/VR counter-arguments at once; independent capture draws; leave-one-criterion-out.
Outputs: reports/ranking_candidates.md, data/interim/ranking_candidates_summary.csv, data/interim/ranking_candidates_loo.csv.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
ANALYSIS = REPO_ROOT / "configs" / "analysis.yaml"
SCORES = REPO_ROOT / "configs" / "scores.yaml"
SCEN = REPO_ROOT / "data" / "interim" / "option_scenarios.csv"
REPORT = REPO_ROOT / "reports" / "ranking.md"
SUMMARY = REPO_ROOT / "data" / "interim" / "ranking_summary.csv"
LOO = REPO_ROOT / "data" / "interim" / "ranking_loo.csv"
CAND_SCORES = REPO_ROOT / "configs" / "scores_candidates.yaml"
CAND_SCEN = REPO_ROOT / "data" / "interim" / "candidate_scenarios.csv"
CAND_REPORT = REPO_ROOT / "reports" / "ranking_candidates.md"
CAND_SUMMARY = REPO_ROOT / "data" / "interim" / "ranking_candidates_summary.csv"
CAND_LOO = REPO_ROOT / "data" / "interim" / "ranking_candidates_loo.csv"
LEVELS = ("low", "central", "high")
HAND = ("labour_relevance", "institutional_fit", "feasibility", "differentiation")


def capture_score(n):
    return np.clip(1 + 4 * np.log(np.maximum(n, 1e-9) / 10) / np.log(8), 1, 5)


def regional_score(c):
    return np.clip(1 + 4 * np.log(np.maximum(c, 1.0)) / np.log(16), 1, 5)


def tri_ppf(u, lo, mode, hi):
    """Inverse CDF of the triangular distribution (vectorised in u)."""
    if hi == lo:
        return np.full_like(u, lo, dtype=float)
    f = (mode - lo) / (hi - lo)
    return np.where(u < f, lo + np.sqrt(u * (hi - lo) * (mode - lo)), hi - np.sqrt((1 - u) * (hi - lo) * (hi - mode)))


def load(robotics_cannib_50: bool = False, robotics_skew: bool = False, german_trend: bool = False,
         sheet_path: Path = SCORES, scen_path: Path = SCEN, cannib_50: tuple = ("robotics_bsc",)) -> tuple[dict, dict, dict]:
    cfg = yaml.safe_load(ANALYSIS.read_text(encoding="utf-8"))
    sheet = yaml.safe_load(sheet_path.read_text(encoding="utf-8"))
    sc = sheet["options"]
    if german_trend:  # sensitivity: trend anchor applied to German first-years / graduates only (all options)
        for o, t in sheet["sensitivity"]["trend_german"].items():
            sc[o]["student_demand"]["trend"].update(t)
    if robotics_skew:  # sensitivity: the earlier skewed 2 / 3 / 5 for robotics fit and feasibility (mean 3.33)
        for k in ("institutional_fit", "feasibility"):
            sc["robotics_bsc"][k].update(low=2, central=3, high=5)
    model = pd.read_csv(scen_path)
    cap = {}
    for o in sc:
        d = model[model["option"] == o].set_index("scenario")
        n = [float(d.at[k, "(b) net new to OTH"]) for k in LEVELS]
        c = [float(d.at[k, "(c) kept in region"]) for k in LEVELS]
        if robotics_cannib_50 and o in cannib_50:
            share = [float(d.at[k, "net-new share"]) for k in LEVELS]
            n = [0.5 * float(d.at[k, "gross first-years"]) for k in LEVELS]
            c = [ci * 0.5 / s for ci, s in zip(c, share)]
        cap[o] = {"n": n, "c": c}
    return cfg, sc, cap


def simulate(cfg: dict, sc: dict, cap: dict, weights: dict, common: bool = True) -> pd.DataFrame:
    mc = cfg["monte_carlo"]
    rng = np.random.default_rng(mc["seed"])
    draws = mc["draws"]
    crit = list(weights)
    base = np.array([weights[k] for k in crit])
    w = rng.dirichlet(mc["dirichlet_concentration"] * base, size=draws)
    options = [o for o in sc if sc[o]["feasibility"]["central"] > 1]          # feasibility gate (kill rule 2)
    u_common = rng.random(draws)
    total = {}
    for o in options:
        s = sc[o]
        u = u_common if common else rng.random(draws)
        n = tri_ppf(u, *cap[o]["n"])
        c = tri_ppf(u, *cap[o]["c"])
        t = s["student_demand"]["trend"]
        vals = {"student_demand": 0.5 * capture_score(n) + 0.5 * tri_ppf(rng.random(draws), t["low"], t["central"], t["high"]),
                "regional_contribution": regional_score(c)}
        for k in HAND:
            vals[k] = tri_ppf(rng.random(draws), s[k]["low"], s[k]["central"], s[k]["high"])
        total[o] = sum(w[:, i] * vals[k] for i, k in enumerate(crit))
    return pd.DataFrame(total)


def summarise(tot: pd.DataFrame) -> pd.DataFrame:
    ranks = tot.rank(axis=1, ascending=False, method="first")
    rows = []
    for o in tot.columns:
        rows.append({"option": o, "P(rank 1)": (ranks[o] == 1).mean(), "P(rank 2)": (ranks[o] == 2).mean(),
                     "P(rank 3)": (ranks[o] == 3).mean(), "median score": tot[o].median(),
                     "80 % range": f"{tot[o].quantile(0.1):.2f}-{tot[o].quantile(0.9):.2f}"})
    return pd.DataFrame(rows).sort_values("P(rank 1)", ascending=False)


def deterministic(cfg: dict, sc: dict, cap: dict) -> pd.DataFrame:
    w = cfg["weights"]
    rows = []
    for o, s in sc.items():
        v = {"student_demand": 0.5 * float(capture_score(cap[o]["n"][1])) + 0.5 * s["student_demand"]["trend"]["central"],
             "regional_contribution": float(regional_score(cap[o]["c"][1])), **{k: s[k]["central"] for k in HAND}}
        rows.append({"option": o, **{k: round(v[k], 2) for k in w}, "weighted total": round(sum(w[k] * v[k] for k in w), 2)})
    return pd.DataFrame(rows).sort_values("weighted total", ascending=False)


def leave_one_out(cfg: dict, sc: dict, cap: dict) -> pd.DataFrame:
    rows = []
    for drop in cfg["weights"]:
        w = {k: v for k, v in cfg["weights"].items() if k != drop}
        tot_w = sum(w.values())
        w = {k: v / tot_w for k, v in w.items()}
        s = summarise(simulate(cfg, sc, cap, w)).set_index("option")
        rows.append({"criterion left out": drop, **{f"P(rank 1) {o}": round(s.at[o, "P(rank 1)"], 3) for o in s.index},
                     "winner": s["P(rank 1)"].idxmax()})
    return pd.DataFrame(rows)


def strength_matrix(sc: dict) -> pd.DataFrame:
    rows = []
    for o, s in sc.items():
        rows.append({"option": o, "demand: model": s["student_demand"]["capture"]["strength"],
                     "demand: trend": s["student_demand"]["trend"]["strength"],
                     **{k: s[k]["strength"] for k in HAND}, "regional_contribution": s["regional_contribution"]["strength"]})
    return pd.DataFrame(rows)


def _md(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(f"{v:.3f}" if isinstance(v, float) else str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(out)


def main_candidates() -> None:
    kw = {"sheet_path": CAND_SCORES, "scen_path": CAND_SCEN}
    sheet = yaml.safe_load(CAND_SCORES.read_text(encoding="utf-8"))
    sens = sheet["sensitivity"]
    cfg, sc, cap = load(**kw)
    runs = {"base": (cfg, sc, cap)}
    runs["German-only trends"] = load(german_trend=True, **kw)
    c, s_, k = load(**kw)
    for o in s_:   # lenient gate: the candidates that would pass under the lenient rule keep their scores
        if o not in sens["lenient_gate"]["pass"]:
            s_[o]["feasibility"].update(low=1, central=1, high=1)
    runs["lenient feasibility gate"] = (c, s_, k)
    runs["50 % cannibalisation (robotics_b, arvr)"] = load(robotics_cannib_50=True, cannib_50=tuple(sens["cannibalisation_50"]), **kw)
    c, s_, k = load(**kw)
    k["arvr"] = k["robotics_b"]
    runs["AR/VR capture = robotics rows"] = (c, s_, k)
    c, s_, k = load(**kw)
    s_["arvr"]["differentiation"].update(low=2, central=3, high=3)
    runs["AR/VR differentiation one step lower"] = (c, s_, k)
    c, s_, k = load(german_trend=True, robotics_cannib_50=True, cannib_50=("arvr",), **kw)
    k["arvr"] = {"n": [0.5 * x for x in k["robotics_b"]["n"]], "c": k["robotics_b"]["c"]}
    s_["arvr"]["differentiation"].update(low=2, central=3, high=3)
    runs["AR/VR: all counter-arguments at once"] = (c, s_, k)
    res = {name: summarise(simulate(*r, r[0]["weights"])) for name, r in runs.items()}
    res["independent capture draws"] = summarise(simulate(cfg, sc, cap, cfg["weights"], common=False))
    det = deterministic(cfg, {o: v for o, v in sc.items() if v["feasibility"]["central"] > 1}, cap)
    det_all = deterministic(cfg, sc, cap)
    loo = leave_one_out(cfg, sc, cap)
    gate = {o: sc[o]["gate"]["result"] + ": " + sc[o]["gate"]["evidence"] for o in sc}
    out = pd.concat([r.assign(scenario=name) for name, r in res.items()])
    CAND_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(CAND_SUMMARY, index=False)
    loo.to_csv(CAND_LOO, index=False)
    lines = ["# Ranking of the equal-evidence candidates (generated)", "",
             f"Score sheet configs/scores_candidates.yaml; capture data/interim/candidate_scenarios.csv. Draws "
             f"{cfg['monte_carlo']['draws']}, Dirichlet concentration {cfg['monte_carlo']['dirichlet_concentration']}, "
             f"seed {cfg['monte_carlo']['seed']}.", "", "## Gate F1-F4", "",
             *[f"- {o}: {g}" for o, g in gate.items()], "",
             "## Central scores of all candidates (gate ignored, for comparison only)", "", _md(det_all), "",
             "## Central scores of the candidates that pass the gate", "", _md(det), ""]
    for name, r in res.items():
        lines += [f"## {name}", "", _md(r), ""]
    lines += ["## Leave-one-criterion-out (base)", "", _md(loo), "", "## Evidence strength", "", _md(strength_matrix(sc)), ""]
    CAND_REPORT.write_text("\n".join(lines), encoding="utf-8")
    pd.set_option("display.width", 250)
    print(det_all.to_string(index=False))
    for name, r in res.items():
        print(f"\n== {name}\n{r.to_string(index=False)}")
    print(f"\n== LOO\n{loo.to_string(index=False)}")
    print(f"\nWritten: {CAND_REPORT.relative_to(REPO_ROOT)}, {CAND_SUMMARY.relative_to(REPO_ROOT)}")


def main() -> None:
    import sys
    if "--candidates" in sys.argv[1:]:
        return main_candidates()
    cfg, sc, cap = load()
    base = summarise(simulate(cfg, sc, cap, cfg["weights"]))
    indep = summarise(simulate(cfg, sc, cap, cfg["weights"], common=False))
    cfg50, sc50, cap50 = load(robotics_cannib_50=True)
    rob50 = summarise(simulate(cfg50, sc50, cap50, cfg50["weights"]))
    cfgs, scs, caps = load(robotics_skew=True)
    skew = summarise(simulate(cfgs, scs, caps, cfgs["weights"]))
    cfgg, scg, capg = load(german_trend=True)
    german = summarise(simulate(cfgg, scg, capg, cfgg["weights"]))
    detg, loog = deterministic(cfgg, scg, capg), leave_one_out(cfgg, scg, capg)
    det, det50 = deterministic(cfg, sc, cap), deterministic(cfg50, sc50, cap50)
    loo, loo50 = leave_one_out(cfg, sc, cap), leave_one_out(cfg50, sc50, cap50)
    gate = [o for o in sc if sc[o]["feasibility"]["central"] <= 1]
    mat = strength_matrix(sc)
    out = pd.concat([base.assign(scenario="base"), rob50.assign(scenario="robotics 50 % cannibalisation"),
                     indep.assign(scenario="base, independent capture draws"),
                     skew.assign(scenario="base, robotics fit/feasibility 2/3/5"),
                     german.assign(scenario="base, trend scores from German first-years only")])
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(SUMMARY, index=False)
    pd.concat([loo.assign(scenario="base"), loo50.assign(scenario="robotics 50 % cannibalisation"),
               loog.assign(scenario="base, trend scores from German first-years only")]).to_csv(LOO, index=False)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# MCDA + Monte Carlo ranking (generated)", "",
        f"Draws {cfg['monte_carlo']['draws']}, Dirichlet concentration {cfg['monte_carlo']['dirichlet_concentration']}, "
        f"seed {cfg['monte_carlo']['seed']}. Feasibility gate excluded: {gate or 'none'}.", "",
        "## Central scores, base weights (no uncertainty)", "", _md(det), "",
        "## Base case", "", _md(base), "",
        "## Robotics with 50 % cannibalisation", "", "Central scores:", "", _md(det50), "", _md(rob50), "",
        "## Sensitivity: independent capture draws (no common factor)", "", _md(indep), "",
        "## Sensitivity: robotics fit and feasibility 2 / 3 / 5 (skewed, earlier draft)", "", _md(skew), "",
        "## Sensitivity: demand trend scores from German first-years / graduates only (all options)", "",
        "Central scores:", "", _md(detg), "", _md(german), "", "Leave-one-criterion-out:", "", _md(loog), "",
        "## Leave-one-criterion-out (base)", "", _md(loo), "",
        "## Leave-one-criterion-out (robotics 50 %)", "", _md(loo50), "",
        "## Evidence strength", "", _md(mat), ""]), encoding="utf-8")
    pd.set_option("display.width", 250)
    for name, df in (("central", det), ("base", base), ("central rob50", det50), ("rob50", rob50), ("independent", indep), ("skew 2/3/5", skew), ("German trend", german), ("central German", detg),
                     ("LOO base", loo), ("LOO rob50", loo50), ("strength", mat)):
        print(f"\n== {name}\n{df.to_string(index=False)}")
    print(f"\nWritten: {REPORT.relative_to(REPO_ROOT)}, {SUMMARY.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
