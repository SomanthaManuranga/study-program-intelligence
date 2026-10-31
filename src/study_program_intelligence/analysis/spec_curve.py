"""Specification-curve (multiverse) analysis of the capture/viability model and the Monte Carlo ranking.

Run from the repository root:

    python -m study_program_intelligence.analysis.spec_curve

Method (docs/criteria_deep_analysis.md): the pre-registered pipeline makes a small number of defensible analysis
choices (anchors, central rule, ramp-up, cannibalisation variant, minimum cohort, distance decay, focus weight,
pool-trend treatment). A specification curve recomputes the outcome under EVERY combination of the reasonable
alternatives a critic could propose, so the conclusion can be stated as "holds in X % of reasonable specifications"
instead of resting on one path (Simonsohn, Simmons and Nelson's specification-curve idea, applied descriptively -
no inference test, the specs are not independent).

The Huff machinery is the pre-registered Step 47/48 code (analysis/capture.py, analysis/cannibalisation.py,
analysis/options.py), fed from the generated tables (data/interim/counties_geo.csv, school_leavers_by.csv,
demand_split.csv) instead of data/raw, so it runs on any machine with the repository data. A REPRODUCTION GATE
asserts that the pre-registered central specification reproduces the committed results exactly (cyber 21 / 39 / 75
gross and 15.3 / 32.0 / 64.4 net new; robotics path B 14.9 / 28.7 / 55.3) before any variant is trusted.

Assumptions and limits, stated: the spec grid is OUR list of reasonable alternatives (grid in SPECS below); the
curve summarises sensitivity, it does not test significance; the master option is not re-run (its origin table needs
data/raw) and keeps its pre-registered scenarios in the ranking family; specs share data, so they are correlated.

Outputs: data/interim/spec_curve_capture.csv, data/interim/spec_curve_ranking.csv, reports/spec_curve.md.
"""

from __future__ import annotations

import itertools
from pathlib import Path

import numpy as np
import pandas as pd

from .capture import THI_CAPACITY, DEG_ANECDOTE, capture
from .cannibalisation import split as cannib_split
from . import options as O
from . import ranking as R

REPO_ROOT = Path(__file__).resolve().parents[3]
INTERIM = REPO_ROOT / "data" / "interim"
OUT_CAP = INTERIM / "spec_curve_capture.csv"
OUT_RANK = INTERIM / "spec_curve_ranking.csv"
REPORT = REPO_ROOT / "reports" / "spec_curve.md"
BETAS, W_ANCHOR, W_SPLIT = (1.3, 1.6, 1.95), (0.0, 0.5, 1.0), (0.5, 1.0)
PROJECT_YEARS = 6   # 2024 pool -> steady state 2030 (configs/first_years.yaml assumptions)


# ---------------- harness: the Step 47/48 inputs from the generated tables ----------------

def load_geo() -> pd.DataFrame:
    g = pd.read_csv(INTERIM / "counties_geo.csv", dtype={"county": str, "land": str})
    for c in ("own_pool", "own_pool_with_regensburg"):
        if g[c].dtype != bool:
            g[c] = g[c].astype(str) == "True"
    return g


def load_pool(geo: pd.DataFrame) -> pd.DataFrame:
    lv = pd.read_csv(INTERIM / "school_leavers_by.csv", dtype={"key": str})
    lv = lv[(lv["year"] == lv["year"].max()) & (lv["key"].str.len() == 5)]
    m = lv.merge(geo, left_on="key", right_on="county")
    return pd.DataFrame({"key": m["key"], "hzb": m["hzb_total"].astype(float), "lat": m["lat"], "lon": m["lon"]})


def options_pool(geo: pd.DataFrame, pool: pd.DataFrame) -> pd.DataFrame:
    own = set(geo.loc[geo["own_pool"], "county"])
    return pd.DataFrame({"mass": pool["hzb"], "lat": pool["lat"], "lon": pool["lon"], "own": pool["key"].isin(own)})


def cyber_ratios(pool: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for beta, w in itertools.product(BETAS, W_ANCHOR):
        r = capture(beta, 1.0, 1.0, pool, w)
        rows.append({"beta": beta, "w": w, "r_thi": r["OTH (new)"] / r["TH Ingolstadt"],
                     "r_deg": r["OTH (new)"] / r["TH Deggendorf"]})
    return pd.DataFrame(rows)


def cyber_shares(pool: pd.DataFrame, geo: pd.DataFrame) -> pd.DataFrame:
    rows = [{"beta": b, "w": w, **cannib_split(b, w, pool, geo)} for b, w in itertools.product(BETAS, W_SPLIT)]
    return pd.DataFrame(rows)


def robotics_runs(geo: pd.DataFrame, pool: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    sites, new_locs = O.option_sites("robotics_bsc")
    opool = options_pool(geo, pool)
    rel = pd.DataFrame([{"beta": b, "w": w,
                         "ratio": (lambda x: x["demand"][O.NEW] / x["demand"][O.anchor_site("robotics_bsc", sites)])(
                             O.run("robotics_bsc", b, w, sites, new_locs, opool, geo))}
                        for b, w in itertools.product(BETAS, W_ANCHOR)])
    shares = pd.DataFrame([{"beta": b, "w": w, **{k: O.run("robotics_bsc", b, w, sites, new_locs, opool, geo)[k] for k in "abc"}}
                           for b, w in itertools.product(BETAS, W_SPLIT)])
    return rel, shares


def pool_growth(codes: list[str], window: tuple[int, int]) -> dict:
    """German/foreign mix in the window's last year and CAGR per group (Bavaria), from the generated split table."""
    ds = pd.read_csv(INTERIM / "demand_split.csv")
    d = ds[(ds["kind"] == "first-years") & (ds["region"] == "BY") & ds["code"].isin(codes)]
    p = d.pivot_table(index="year", columns="nationality", values="value", aggfunc="sum")
    y0, y1 = window
    tot = p.loc[y1].sum()
    g = lambda a, b: (b / a) ** (1 / (y1 - y0)) - 1
    return {"share_de": p.loc[y1, "German"] / tot, "share_f": p.loc[y1, "foreign"] / tot,
            "g_de": g(p.loc[y0, "German"], p.loc[y1, "German"]), "g_f": g(p.loc[y0, "foreign"], p.loc[y1, "foreign"])}


def projection_factor(growth: dict, mode: str) -> float:
    """Factor on the base-year gross for the pool trend carried to 2030: 'base-year' = 1, 'projected' = both groups
    at their 2019-24 CAGR, 'projected, foreign held flat' = German projected, foreign kept at the base level."""
    de = growth["share_de"] * ((1 + growth["g_de"]) ** PROJECT_YEARS if mode.startswith("projected") else 1.0)
    fo = growth["share_f"] * ((1 + growth["g_f"]) ** PROJECT_YEARS if mode == "projected" else 1.0)
    return float(de + fo)


# ---------------- reproduction gate (criteria D2) ----------------

def reproduction_gate(ratios: pd.DataFrame, shares: pd.DataFrame, rob_rel: pd.DataFrame) -> dict:
    low = float((THI_CAPACITY * ratios["r_thi"]).median())
    high = float((DEG_ANECDOTE * ratios["r_deg"]).median())
    central = float(np.sqrt(low * high))
    stored = pd.read_csv(INTERIM / "capture_scenarios.csv").set_index("scenario")
    worst = shares.loc[shares["a"].idxmax()]
    base = shares[(shares["beta"] == 1.6) & (shares["w"] == 0.5)].iloc[0]
    best = shares.loc[shares["a"].idxmin()]
    near = lambda a, b: abs(float(a) - float(b)) <= 0.051
    checks = {
        "cyber gross low/central/high = 21/39/75": [round(low), round(central), round(high)] == [21, 39, 75],
        "cyber net new low = 15.3": near(round(low) * worst["b"], stored.at["low", "(b) net new to OTH"]),
        "cyber net new central = 32.0": near(round(central) * base["b"], stored.at["central", "(b) net new to OTH"]),
        "cyber net new high = 64.4": near(round(high) * best["b"], stored.at["high", "(b) net new to OTH"]),
    }
    r = rob_rel["ratio"]
    rob = pd.read_csv(INTERIM / "option_scenarios.csv")
    rob = rob[rob["option"] == "robotics_bsc"].set_index("scenario")
    lo, hi = 20 * r.min(), 60 * r.max()
    checks["robotics gross low/central/high = 14.9/28.7/55.3"] = (
        near(lo, rob.at["low", "gross first-years"]) and near(np.sqrt(lo * hi), rob.at["central", "gross first-years"])
        and near(hi, rob.at["high", "gross first-years"]))
    return checks


# ---------------- specification family 1: capture and viability ----------------

def capture_specs(ratios: pd.DataFrame, shares: pd.DataFrame, rob_rel: pd.DataFrame, rob_shares: pd.DataFrame) -> pd.DataFrame:
    growth_cyber = pool_growth(["SF079", "SF123", "SF200"], (2019, 2024))
    growth_rob = pool_growth(["SF380", "SF123"], (2019, 2024))
    worst, base, best = (shares.loc[shares["a"].idxmax()], shares[(shares["beta"] == 1.6) & (shares["w"] == 0.5)].iloc[0],
                         shares.loc[shares["a"].idxmin()])
    rw, rb, rbe = (rob_shares.loc[rob_shares["a"].idxmax()], rob_shares[(rob_shares["beta"] == 1.6) & (rob_shares["w"] == 0.5)].iloc[0],
                   rob_shares.loc[rob_shares["a"].idxmin()])
    rows = []
    grid = {
        "cyber": dict(anchor_low=[("THI capacity 25", 25.0), ("THI fills below capacity (20)", 20.0)],
                      anchor_high=[("Deggendorf anecdote 60", 60.0), ("anecdote overstated (45)", 45.0)],
                      ratio=[("median of 9 variants*", None)] + [(f"variant beta {b} w {w}", (b, w)) for b, w in
                                                                 itertools.product(BETAS, W_ANCHOR)],
                      growth=growth_cyber),
        "robotics_b": dict(anchor_low=[("assumed comparator low 20", 20.0), ("pessimistic low 15", 15.0)],
                           anchor_high=[("assumed comparator high 60", 60.0), ("THI Robotik indexed capacity 40", 40.0)],
                           ratio=[("min/max envelope*", None)] + [(f"variant beta {b} w {w}", (b, w)) for b, w in
                                                                  itertools.product(BETAS, W_ANCHOR)],
                           growth=growth_rob),
    }
    for cand, g in grid.items():
        rat = ratios if cand == "cyber" else rob_rel
        sh = (worst, base, best) if cand == "cyber" else (rw, rb, rbe)
        for (al_name, al), (ah_name, ah), (r_name, r_sel), central_rule, ramp1, cannib, min_c, proj in itertools.product(
                g["anchor_low"], g["anchor_high"], g["ratio"],
                ("geometric*", "arithmetic"), (0.6, 0.5), ("model*", "flat 50 %"), (15, 20, 25),
                ("base-year*", "projected", "projected, foreign held flat")):
            if cand == "cyber":
                if r_sel is None:
                    lo, hi = float((al * rat["r_thi"]).median()), float((ah * rat["r_deg"]).median())
                else:
                    v = rat[(rat["beta"] == r_sel[0]) & (rat["w"] == r_sel[1])].iloc[0]
                    lo, hi = al * v["r_thi"], ah * v["r_deg"]
            else:
                if r_sel is None:
                    lo, hi = al * rat["ratio"].min(), ah * rat["ratio"].max()
                else:
                    v = rat[(rat["beta"] == r_sel[0]) & (rat["w"] == r_sel[1])].iloc[0]["ratio"]
                    lo, hi = al * v, ah * v
            central = float(np.sqrt(lo * hi)) if central_rule.startswith("geometric") else (lo + hi) / 2
            f = projection_factor(g["growth"], proj.rstrip("*"))
            central_p = central * f
            b_share = {"model*": sh[1]["b"], "flat 50 %": 0.5}[cannib]
            anchors_pre = (al == 25.0 and ah == 60.0) if cand == "cyber" else (al == 20.0 and ah == 60.0)
            rows.append({"candidate": cand, "anchor low": al_name, "anchor high": ah_name, "ratio": r_name,
                         "central rule": central_rule, "ramp year 1": ramp1, "cannibalisation": cannib,
                         "min cohort": min_c, "pool trend": proj,
                         "gross low": round(lo * f, 1), "gross central": round(central_p, 1), "gross high": round(hi * f, 1),
                         "net new central": round(central_p * b_share, 1),
                         "viable central (steady)": central_p >= min_c,
                         "viable central (year 1)": central_p * ramp1 >= min_c,
                         "viable low (steady)": lo * f >= min_c,
                         "pre-registered": anchors_pre and r_name.endswith("*") and central_rule.endswith("*")
                                            and ramp1 == 0.6 and cannib == "model*" and min_c == 20
                                            and proj == "base-year*"})
    return pd.DataFrame(rows)


def variance_decomposition(df: pd.DataFrame, outcome: str, dims: list[str]) -> pd.DataFrame:
    total = float(np.var(df[outcome]))
    rows = []
    for d in dims:
        between = df.groupby(d)[outcome].mean().reindex(df[d]).to_numpy()
        rows.append({"dimension": d, "share of variance %": round(100 * float(np.var(between)) / total, 1) if total else 0.0})
    return pd.DataFrame(rows).sort_values("share of variance %", ascending=False)


# ---------------- specification family 2: Monte Carlo ranking ----------------

def ranking_specs() -> pd.DataFrame:
    rows = []
    for trend, skew, common, rob50, seed, conc in itertools.product(
            ("base", "German-only"), ("symmetric*", "skewed 2/3/5"), ("common*", "independent"),
            ("model*", "50 %"), (42, 7, 2026, 31101), (25, 50, 100)):
        cfg, sc, cap = R.load(robotics_cannib_50=(rob50 == "50 %"), robotics_skew=(skew != "symmetric*"),
                              german_trend=(trend == "German-only"))
        cfg = {**cfg, "monte_carlo": {**cfg["monte_carlo"], "seed": seed, "dirichlet_concentration": conc}}
        s = R.summarise(R.simulate(cfg, sc, cap, cfg["weights"], common=(common == "common*"))).set_index("option")
        p1 = s["P(rank 1)"]
        rows.append({"trend scores": trend, "robotics range": skew, "capture draws": common,
                     "robotics cannibalisation": rob50, "seed": seed, "concentration": conc,
                     "P1 cyber": round(float(p1["cyber_bsc"]), 4), "P1 master": round(float(p1["cyber_msc"]), 4),
                     "P1 robotics": round(float(p1["robotics_bsc"]), 4),
                     "cyber first": bool(p1["cyber_bsc"] == p1.max()),
                     "pre-registered": trend == "base" and skew.endswith("*") and common.endswith("*")
                                        and rob50.endswith("*") and seed == 42 and conc == 50})
    return pd.DataFrame(rows)


def weight_sweep() -> pd.DataFrame:
    cfg, sc, cap = R.load()
    rows = []
    for crit in cfg["weights"]:
        for scale in (0.5, 0.75, 1.0, 1.25, 1.5):
            w = dict(cfg["weights"])
            w[crit] = w[crit] * scale
            tot = sum(w.values())
            w = {k: v / tot for k, v in w.items()}
            s = R.summarise(R.simulate(cfg, sc, cap, w)).set_index("option")
            rows.append({"criterion": crit, "weight scale": scale, "effective weight": round(w[crit], 3),
                         "P1 cyber": round(float(s.at["cyber_bsc", "P(rank 1)"]), 4)})
    return pd.DataFrame(rows)


def _md(df: pd.DataFrame) -> str:
    fmt = lambda v: ("yes" if v else "no") if isinstance(v, (bool, np.bool_)) else str(v)
    return "\n".join(["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
                     + ["| " + " | ".join(fmt(v) for v in r) + " |" for r in df.itertuples(index=False)])


def main() -> None:
    geo = load_geo()
    pool = load_pool(geo)
    ratios, shares = cyber_ratios(pool), cyber_shares(pool, geo)
    rob_rel, rob_shares = robotics_runs(geo, pool)
    gate = reproduction_gate(ratios, shares, rob_rel)
    if not all(gate.values()):
        raise SystemExit(f"reproduction gate failed: {gate}")
    cap = capture_specs(ratios, shares, rob_rel, rob_shares)
    rank = ranking_specs()
    sweep = weight_sweep()
    OUT_CAP.parent.mkdir(parents=True, exist_ok=True)
    cap.to_csv(OUT_CAP, index=False)
    rank.to_csv(OUT_RANK, index=False)

    dims = ["anchor low", "anchor high", "ratio", "central rule", "cannibalisation", "pool trend"]
    summ = []
    for cand, d in cap.groupby("candidate"):
        pre = d[d["pre-registered"]]
        summ.append({
            "candidate": cand, "specifications": len(d),
            "central gross: median (IQR)": f"{d['gross central'].median():.1f} ({d['gross central'].quantile(.25):.1f}-{d['gross central'].quantile(.75):.1f})",
            "central gross: min-max": f"{d['gross central'].min():.1f}-{d['gross central'].max():.1f}",
            "% viable central (steady, vs own min cohort)": round(100 * d["viable central (steady)"].mean(), 1),
            "% viable central at min cohort 20": round(100 * d.loc[d["min cohort"] == 20, "viable central (steady)"].mean(), 1),
            "% viable low (steady) at 20": round(100 * d.loc[d["min cohort"] == 20, "viable low (steady)"].mean(), 1),
            "pre-registered spec central": ", ".join(f"{v:.1f}" for v in pre["gross central"]) or "-"})
    rk_pre = rank[rank["pre-registered"]]
    rank_summary = pd.DataFrame([{
        "specifications": len(rank),
        "P1 cyber: median": f"{rank['P1 cyber'].median():.3f}",
        "P1 cyber: min-max": f"{rank['P1 cyber'].min():.3f}-{rank['P1 cyber'].max():.3f}",
        "% specs with cyber first": round(100 * rank["cyber first"].mean(), 1),
        "pre-registered spec": f"{float(rk_pre['P1 cyber'].iloc[0]):.3f}" if len(rk_pre) else "-",
        "seed spread at pre-registered settings": f"{rank[(rank['trend scores'] == 'base') & (rank['robotics range'] == 'symmetric*') & (rank['capture draws'] == 'common*') & (rank['robotics cannibalisation'] == 'model*') & (rank['concentration'] == 50)]['P1 cyber'].min():.3f}-"
                                                   f"{rank[(rank['trend scores'] == 'base') & (rank['robotics range'] == 'symmetric*') & (rank['capture draws'] == 'common*') & (rank['robotics cannibalisation'] == 'model*') & (rank['concentration'] == 50)]['P1 cyber'].max():.3f}"}])

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# Specification curve: capture/viability and ranking (generated)", "",
        "Pre-registered machinery rerun from the generated tables; the asterisked level of every dimension is the",
        "pre-registered choice. Reproduction gate (criteria D2): " + "; ".join(f"{k}: PASS" for k in gate), "",
        "## Capture and viability specifications", "", _md(pd.DataFrame(summ)), "",
        "Variance decomposition of the central gross (share of spec variance per dimension; shares need not sum to",
        "100 % because dimensions interact):", "",
        "### cyber", "", _md(variance_decomposition(cap[cap["candidate"] == "cyber"], "gross central", dims)), "",
        "### robotics path B", "", _md(variance_decomposition(cap[cap["candidate"] == "robotics_b"], "gross central", dims)), "",
        "## Ranking specifications (10,000 draws each)", "", _md(rank_summary), "",
        "Weight sweep (one criterion scaled, weights renormalised, pre-registered everything else):", "",
        _md(sweep.pivot(index="criterion", columns="weight scale", values="P1 cyber").reset_index()), "",
        "Reading: see docs/evidence_deep_analysis.md.", ""]), encoding="utf-8")
    pd.set_option("display.width", 250)
    print(pd.DataFrame(summ).to_string(index=False))
    print(rank_summary.to_string(index=False))
    print(f"Written: {OUT_CAP.relative_to(REPO_ROOT)}, {OUT_RANK.relative_to(REPO_ROOT)}, {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
