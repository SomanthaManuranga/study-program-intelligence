"""Capture model: expected first-years for an OTH Cyber Security B.Sc. (Step 47).

Run from the repository root:

    python -m study_program_intelligence.analysis.capture

1. Distance decay, calibrated on real flows: Bayerisches Landesamt für Statistik, "Studierende an den Hochschulen in
   Bayern" WS 2024/25, Tabelle 5 (students of each state HAW by Regierungsbezirk where the entrance qualification was
   obtained). Doubly-constrained gravity model T_bj = a_b O_b b_j D_j d_bj^-beta,
   balanced by iterative proportional fitting; beta chosen on a grid by the lowest SRMSE of the 7 x 17 flows.
   Distances: population-weighted Bezirk centres (Destatis GV-ISys) to the campus (median of the institution's
   programme offers, data/processed/programmes.csv).
2. Cyber demand per Bavarian county = school leavers with a university entrance qualification 2023/24 (Step 42)
   x cyber-proxy first-year rate (Bavaria 2024: cyber-proxy first-years / qualified school leavers, Step 46)
   x dedicated-cyber share s (low: Bavarian supply share of dedicated cyber bachelors among informatics-type
   bachelor offers; high: search-interest share "Cyber Security Studium" / "Informatik Studium" 2026, Step 37).
3. Huff split of each county's cyber demand among the full-time dedicated cyber bachelors reachable in Bavaria
   (OTH new; TH Ingolstadt, TH Deggendorf, THWS, HNU Neu-Ulm), equal attractiveness, d^-beta.
4. Checks: implied intake of the competitors vs public figures (THI capacity 25); home-region share of OTH.
Outputs: reports/capture.md
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import numpy as np
import pandas as pd
import pypdf

from ..transform.pdf_numbers import split, tokens
from .catchment import counties, haversine, municipalities

REPO_ROOT = Path(__file__).resolve().parents[3]
REPORT = REPO_ROOT / "reports" / "capture.md"
TABLE5 = REPO_ROOT / "data" / "raw" / "regional" / "by_studierende_ws2024.pdf"
LEAVERS = REPO_ROOT / "data" / "interim" / "school_leavers_by.csv"
PROGRAMMES = REPO_ROOT / "data" / "processed" / "programmes.csv"
BEZIRKE = ["Oberbayern", "Niederbayern", "Oberpfalz", "Oberfranken", "Mittelfranken", "Unterfranken", "Schwaben"]
CYBER_PROXY_FIRSTYEARS_BY_2024 = 4936   # Step 46 (Destatis 21311-0015)
TRENDS_SHARE = 0.126                     # Step 37: "Cyber Security Studium" / "Informatik Studium", 2026
THI_CAPACITY = 25                        # THI module handbook Cybersicherheit (Stand 24.10.2025): "Kapazität 25 Studierende pro Studienjahr"
RAMP = (0.6, 0.8, 1.0)                   # assumption: share of steady-state intake in years 1-3
# campus name patterns in programmes.csv (institution column)
CAMPUS = {
    "OTH Amberg-Weiden": "Amberg-Weiden", "HaW Ansbach": "Ansbach", "TH Aschaffenburg": "Aschaffenburg",
    "TH Augsburg": "Technische Hochschule Augsburg", "HaW Coburg": "Hochschule Coburg", "TH Deggendorf": "Deggendorf",
    "HaW Hof": "Hochschule Hof", "TH Ingolstadt": "Technische Hochschule Ingolstadt", "HaW Kempten": "Kempten",
    "HaW Landshut": "Landshut", "HaW München": "Hochschule München", "HaW Neu-Ulm": "Neu-Ulm",
    "TH Nürnberg": "Technische Hochschule Nürnberg", "OTH Regensburg": "Ostbayerische Technische Hochschule Regensburg",
    "TH Rosenheim": "Rosenheim", "HaW Weihenstephan-Triesdorf": "Weihenstephan", "TH Würzburg-Schweinfurt (THWS)": "Würzburg-Schweinfurt",
}
CYBER_SITES = {  # full-time dedicated cyber bachelors in Bavaria (Step 38) + the new OTH programme; campus coordinates
    "OTH (new)": [(49.4425, 11.8558), (49.6761, 12.1603)],
    "TH Ingolstadt": [(48.7656, 11.4233)],
    "TH Deggendorf": [(48.8422, 12.9600)],
    "THWS Würzburg": [(49.7913, 9.9534)],
    "HNU Neu-Ulm": [(48.3888, 10.0099)],
}


def table5() -> pd.DataFrame:
    logging.disable(logging.WARNING)
    r = pypdf.PdfReader(TABLE5)
    rows = []
    for p in r.pages:
        t = p.extract_text(extraction_mode="layout") or ""
        if "Tabelle 5." not in t:
            continue
        for line in t.splitlines():
            m = re.match(r"^\s*(.+?)\s*\.{2,}\s*([LBKP])\s+([\d\s–\-]+)$", line)
            if m and m.group(1).strip() in CAMPUS:
                o = split(tokens(m.group(3).replace("–", "-")), 8, lambda g: g[0] == sum(g[1:]), max_cuts=1)
                rows.append({"haw": m.group(1).strip(), **dict(zip(["total", *BEZIRKE], o[0]))})
    d = pd.DataFrame(rows).set_index("haw")
    if len(d) != len(CAMPUS):
        raise ValueError(f"Tabelle 5: found {len(d)} of {len(CAMPUS)} HAWs")
    return d


def campus_coords() -> pd.DataFrame:
    p = pd.read_csv(PROGRAMMES)
    out = {}
    for haw, pat in CAMPUS.items():
        m = p[p["institution"].str.contains(pat, regex=False, na=False) & (p["state"] == "Bayern")]
        out[haw] = (m["lat"].median(), m["lon"].median())
    d = pd.DataFrame(out, index=["lat", "lon"]).T
    if d.isna().any(axis=None):  # not in the programme catalogue (e.g. HaW Ansbach): centre of its kreisfreie Stadt
        geo = counties().set_index("county")
        fallback = {"HaW Ansbach": "09561"}
        for haw in d.index[d.isna().any(axis=1)]:
            d.loc[haw] = geo.loc[fallback[haw], ["lat", "lon"]].values
    return d


def bezirk_centres() -> pd.DataFrame:
    g = municipalities()
    g = g[g["land"] == "09"].assign(rb=lambda x: x["rb"].astype(int))
    w = g.assign(wl=g["lat"] * g["pop"], wo=g["lon"] * g["pop"]).groupby("rb")[["wl", "wo", "pop"]].sum()
    return pd.DataFrame({"lat": w["wl"] / w["pop"], "lon": w["wo"] / w["pop"]}).set_index(pd.Index(BEZIRKE))


def gravity(flows: np.ndarray, dist: np.ndarray, beta: float, iters: int = 200) -> np.ndarray:
    """Doubly-constrained gravity model (rows: origins, cols: HAWs), balanced to the observed margins."""
    f = np.maximum(dist, 5.0) ** (-beta)
    o, d = flows.sum(axis=1), flows.sum(axis=0)
    a, b = np.ones(len(o)), np.ones(len(d))
    for _ in range(iters):
        a = 1.0 / (f @ (b * d))
        b = 1.0 / ((a * o) @ f)
    return (a * o)[:, None] * (b * d)[None, :] * f


def calibrate() -> tuple[float, pd.DataFrame, dict]:
    t5 = table5()
    cc, bc = campus_coords(), bezirk_centres()
    flows = t5[BEZIRKE].T.values.astype(float)  # 7 x 17
    dist = np.array([[haversine(bc.at[b, "lat"], bc.at[b, "lon"], cc.at[h, "lat"], cc.at[h, "lon"]) for h in t5.index] for b in BEZIRKE])
    grid = np.round(np.arange(0.0, 4.01, 0.05), 2)
    srmse = []
    for beta in grid:
        pred = gravity(flows, dist, beta)
        srmse.append(np.sqrt(((pred - flows) ** 2).mean()) / flows.mean())
    k = int(np.argmin(srmse))
    best = float(grid[k])
    pred = gravity(flows, dist, best)
    r2 = 1 - ((pred - flows) ** 2).sum() / ((flows - flows.mean()) ** 2).sum()
    near = [g for g, s in zip(grid, srmse) if s <= 1.1 * srmse[k]]
    home = {}
    for j, h in enumerate(t5.index):
        hb = BEZIRKE[int(np.argmin(dist[:, j]))]
        i = BEZIRKE.index(hb)
        home[h] = (hb, flows[i, j] / flows[:, j].sum(), pred[i, j] / pred[:, j].sum())
    fit = pd.DataFrame([{"HAW": h, "home Bezirk": v[0], "actual home share %": round(v[1] * 100, 1), "model home share %": round(v[2] * 100, 1)}
                        for h, v in home.items()])
    return best, fit, {"srmse": srmse[k], "r2": r2, "beta_range": (min(near), max(near)), "curve": dict(zip(grid, srmse))}


def supply_share() -> float:
    """Dedicated cyber bachelors among informatics-type bachelor offers in Bavaria (programme catalogue, title rules)."""
    from .themes import THEMES
    p = pd.read_csv(PROGRAMMES)
    p = p[(p["state"] == "Bayern") & (p["degree"] == "Bachelor/Bakkalaureus")]
    it = p["title"].str.contains(r"informati|computer|software|cyber|it-sicherheit|informationssicherheit|data science|künstliche intelligenz", case=False, regex=True)
    cyber = p["title"].str.lower().str.contains(THEMES["cybersecurity"], regex=True)
    return float((cyber & it).sum() / it.sum())


def secondary_sites() -> dict[str, list[tuple[float, float]]]:
    """Bavarian bachelors with a security focus area but no dedicated cyber title (Step 38), one site per institution."""
    from .theme_check import _focus
    from .themes import THEMES
    p = pd.read_csv(PROGRAMMES)
    p = p[(p["state"] == "Bayern") & (p["degree"] == "Bachelor/Bakkalaureus")]
    f = _focus(p["content"].fillna("")).str.lower()
    sec = p[f.str.contains(THEMES["cybersecurity"]) & ~f.str.contains("security printing")
            & ~p["title"].str.lower().str.contains(THEMES["cybersecurity"])]
    g = sec.groupby("institution")[["lat", "lon"]].median()
    return {f"(focus) {i}": [(r.lat, r.lon)] for i, r in g.iterrows()}


def capture(beta: float, s_cyber: float, rate: float, pool: pd.DataFrame, w_sec: float = 0.0) -> pd.Series:
    """Expected first-years per site from all Bavarian counties. Dedicated cyber sites have weight 1, secondary
    (security focus area in a general programme) weight w_sec."""
    sites = {**{k: (v, 1.0) for k, v in CYBER_SITES.items()}, **({k: (v, w_sec) for k, v in secondary_sites().items()} if w_sec else {})}
    out = pd.Series(0.0, index=list(sites))
    for c in pool.itertuples():
        demand = c.hzb * rate * s_cyber
        w = {s: a * max(min(haversine(c.lat, c.lon, la, lo) for la, lo in locs), 5.0) ** (-beta) for s, (locs, a) in sites.items()}
        tot = sum(w.values())
        for s in out.index:
            out[s] += demand * w[s] / tot
    return out


def _md(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    fmt = lambda v: (f"{v:,.0f}" if abs(v) >= 100 else f"{v:.1f}") if isinstance(v, (float, np.floating)) else str(v)
    out += ["| " + " | ".join(fmt(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(out)


DEG_ANECDOTE = 60      # one student review on studycheck.de ("aus etwa 60 Studienanfängern ..."): weak upper cross-check
MIN_COHORT = 20        # ASSUMPTION (no Bavarian rule found): minimum viable first-year cohort; THI plans with 25


def main() -> None:
    import itertools
    beta, fit, info = calibrate()
    lv = pd.read_csv(LEAVERS, dtype={"key": str})
    lv = lv[(lv["year"] == lv["year"].max()) & (lv["key"].str.len() == 5)]
    pool = lv.merge(counties(), left_on="key", right_on="county")[["key", "county_name", "hzb_total", "lat", "lon"]].rename(columns={"hzb_total": "hzb"})
    bav_hzb = int(lv["hzb_total"].sum())
    rate = CYBER_PROXY_FIRSTYEARS_BY_2024 / bav_hzb
    s_low, s_high = supply_share(), TRENDS_SHARE
    s_mid = (s_low + s_high) / 2
    b_lo, b_hi = info["beta_range"]
    # (a) uncalibrated demand model (absolute scale from s): fails the THI check, kept for transparency
    raw = {k: capture(bb, ss, rate, pool) for k, (ss, bb) in {"low": (s_low, b_hi), "central": (s_mid, beta), "high": (s_high, b_lo)}.items()}
    raw_tab = pd.DataFrame(raw).round(1).reset_index().rename(columns={"index": "site"})
    # (b) relative capture over beta x secondary-competitor weight, anchored on real intakes
    rows = []
    for bb, w in itertools.product((b_lo, beta, b_hi), (0.0, 0.5, 1.0)):
        r = capture(bb, 1.0, 1.0, pool, w)
        rows.append({"beta": bb, "w_sec": w, "OTH/THI": r["OTH (new)"] / r["TH Ingolstadt"], "OTH/DEG": r["OTH (new)"] / r["TH Deggendorf"]})
    rel = pd.DataFrame(rows)
    rel["OTH (THI = 25)"] = THI_CAPACITY * rel["OTH/THI"]
    rel[f"OTH (DEG = {DEG_ANECDOTE})"] = DEG_ANECDOTE * rel["OTH/DEG"]
    low = float(rel["OTH (THI = 25)"].median())
    high = float(rel[f"OTH (DEG = {DEG_ANECDOTE})"].median())
    central = float(np.sqrt(low * high))
    steady = {"low": low, "central": central, "high": high}
    ramp = pd.DataFrame([{"intake year": f"year {i + 1}", **{k: round(v * r) for k, v in steady.items()}} for i, r in enumerate(RAMP)])
    ramp.loc[len(ramp)] = ["steady state", *[round(v) for v in steady.values()]]
    viab = pd.DataFrame([{"scenario": k, "steady state": round(v), "year 1": round(v * RAMP[0]),
                          f"meets assumed minimum {MIN_COHORT} (steady)": "yes" if v >= MIN_COHORT else "no",
                          f"meets {MIN_COHORT} in year 1": "yes" if v * RAMP[0] >= MIN_COHORT else "no"} for k, v in steady.items()])
    curve = pd.DataFrame({"beta": list(info["curve"]), "SRMSE": [round(v, 3) for v in info["curve"].values()]})
    curve = curve[curve["beta"].isin(np.round(np.arange(0, 4.01, 0.5), 2))]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# Capture model: OTH Cyber Security B.Sc. (generated)", "",
        f"Gravity calibration on Tabelle 5 (WS 2024/25, 7 Bezirke x 17 state HAWs): best beta {beta:.2f} "
        f"(SRMSE {info['srmse']:.3f}, R2 {info['r2']:.3f}; beta within 10 % of the best SRMSE: {b_lo:.2f}-{b_hi:.2f}).", "",
        "## Fit: home-region share per HAW", "", _md(fit), "", "## SRMSE by beta", "", _md(curve), "",
        "## (a) Uncalibrated demand model (absolute scale) - fails the check", "",
        f"Inputs: qualified school leavers in Bavaria 2023/24 {bav_hzb:,}; cyber-proxy first-year rate {rate:.3f}; "
        f"dedicated-cyber share s low {s_low:.3f} (supply share), high {s_high:.3f} (search interest), central {s_mid:.3f}.", "",
        _md(raw_tab), "", f"THI implied {raw_tab.loc[raw_tab.site == 'TH Ingolstadt', 'low'].iloc[0]:.0f}-"
        f"{raw_tab.loc[raw_tab.site == 'TH Ingolstadt', 'high'].iloc[0]:.0f} vs planned capacity {THI_CAPACITY}: the absolute scale is not credible.", "",
        "## (b) Relative capture, anchored on real intakes", "", _md(rel.round(2)), "",
        "## Scenarios (steady state and ramp-up; ramp-up 60/80/100 % is an assumption)", "",
        f"low = THI-anchored median, high = DEG-anchored median, central = geometric mean of the two (a choice).", "",
        _md(ramp), "", "## Minimum viable cohort (assumption)", "", _md(viab), ""]), encoding="utf-8")
    print(f"beta {beta} range {info['beta_range']} SRMSE {info['srmse']:.3f} R2 {info['r2']:.3f}")
    print(rel.round(2).to_string(index=False)); print(ramp.to_string(index=False)); print(viab.to_string(index=False))


if __name__ == "__main__":
    main()
