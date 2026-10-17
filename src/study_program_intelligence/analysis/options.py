"""Capture + cannibalisation for all three shortlisted options with one model (Step 49, against evidence asymmetry).

Run from the repository root:

    python -m study_program_intelligence.analysis.options

The Step 47/48 model, applied unchanged to each option:
  Huff split with distance decay d^-beta (beta 1.3 / 1.6 / 1.95 from the Step 47 calibration on Bavarian flows);
  dedicated programmes at weight 1, general programmes with the theme as a focus area at weight w, OTH's own related
  programmes as one site at weight w; relative capture OTH / anchor site x the anchor's public intake figure;
  cannibalisation split (a) from OTH, (b) net new to OTH, (c) kept in region (part of b) by running with and without
  the new programme.
Option-specific inputs:
  cyber_bsc     Step 47/48 (sites and anchors as there); recomputed here only as a reproduction check.
  robotics_bsc  dedicated: Bavarian bachelors with robotics in the title (catalogue, theme rule, precision 90 %);
                focus: Bavarian bachelors with robotics in the focus areas; OTH: KI B.Sc. (Smart Robotics), E&IT
                (Robotik focus) and Mechatronik und digitale Automation. Origins: Bavarian counties (school leavers).
                Anchor: none verified (see ANCHORS); assumed comparator intake 20-60, range taken over all variants.
  cyber_msc     dedicated: the hand-checked cyber masters within 150 km (Step 38; UniBw excluded: officers only;
                MBA Defence excluded); focus: Bavarian masters with a security focus area; OTH: AI for Industrial
                Applications and IT und Automation. Origins: Bavarian state HAWs weighted by their students with a
                Bavarian entrance qualification (Tabelle 5, WS 2024/25), because a master recruits bachelor
                graduates, not school leavers. Anchor: THI Cloud Applications und Security Engineering, capacity 30.
Outputs: data/interim/option_scenarios.csv (low/central/high gross, (a), (b), (c) per option, for the Monte Carlo),
reports/options.md.
"""

from __future__ import annotations

import itertools
from pathlib import Path

import numpy as np
import pandas as pd

from .capture import CYBER_SITES, LEAVERS, PROGRAMMES, campus_coords, haversine, secondary_sites, table5
from .catchment import counties
from .theme_check import _focus
from .themes import THEMES

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT = REPO_ROOT / "data" / "interim" / "option_scenarios.csv"
STEP48 = REPO_ROOT / "data" / "interim" / "capture_scenarios.csv"
REPORT = REPO_ROOT / "reports" / "options.md"
BETAS = (1.3, 1.6, 1.95)
W_ANCHOR = (0.0, 0.5, 1.0)     # Step 47 relative-capture variants
W_SPLIT = (0.5, 1.0)           # Step 48 cannibalisation variants
AMBERG, WEIDEN = (49.4425, 11.8558), (49.6761, 12.1603)
NEW = "OTH (new)"
OTH = "OTH (existing related programmes)"
BA_SPREAD = 75 / 21            # cyber B.Sc. high / low (Step 47), used to widen where a second anchor is missing
ANCHORS = {
    "cyber_bsc": "THI Cybersicherheit capacity 25 (low) and TH Deggendorf ~60 (anecdote, high); Step 47",
    "robotics_bsc": ("none verified: THI Robotik's 2023 module handbook is indexed by search engines with 'Kapazität 40'"
                     " but its host no longer resolves and the current www.thi.de path returns 404; Kempten's handbook"
                     " (downloaded) and TH Augsburg KI und Robotik (404) give no figure. Assumed comparator intake"
                     " 20-60 (the span of the cyber anchors), range taken over all model variants (min / max)"),
    "cyber_msc": ("THI Cloud Applications und Security Engineering 'Kapazität 30 Studierende pro Studienjahr' (module"
                  " handbook, Step 39 cache, Stand 2023) as low; no second anchor: high = low x the cyber B.Sc."
                  " high/low spread (75/21) (assumption)"),
}


def _catalogue(level: str) -> pd.DataFrame:
    p = pd.read_csv(PROGRAMMES)
    return p[(p["state"] == "Bayern") & p["degree"].str.startswith(level)]


def _sites(df: pd.DataFrame, prefix: str = "") -> dict:
    """One site per institution and city (campus), coordinates from the catalogue."""
    g = df[~df["is_oth"]].groupby(["institution", "city"])[["lat", "lon"]].median()
    return {f"{prefix}{i} ({c})": [(r.lat, r.lon)] for (i, c), r in g.iterrows()}


def option_sites(option: str) -> tuple[dict, dict]:
    """Returns (sites {name: (locations, weight factor 'd' = dedicated or 'w' = focus/OTH)}, new-programme locations)."""
    if option == "cyber_bsc":
        sites = {k: (v, "d") for k, v in CYBER_SITES.items() if k != NEW}
        sites.update({k: (v, "w") for k, v in secondary_sites().items()})
        return sites, CYBER_SITES[NEW]
    if option == "robotics_bsc":
        p = _catalogue("Bachelor")
        title = p["title"].str.lower().str.contains(THEMES["robotics"])
        focus = _focus(p["content"].fillna("")).str.lower().str.contains(THEMES["robotics"]) & ~title
        sites = {k: (v, "d") for k, v in _sites(p[title]).items()}
        sites.update({k: (v, "w") for k, v in _sites(p[focus], "(focus) ").items()})
        sites[OTH] = ([AMBERG], "w")      # KI B.Sc., E&IT, Mechatronik und digitale Automation: all in Amberg
        return sites, [AMBERG, WEIDEN]
    if option == "cyber_msc":
        p = _catalogue("Master")
        dedicated = {"Technische Hochschule Ingolstadt": "TH Ingolstadt", "Technische Hochschule Deggendorf": "TH Deggendorf",
                     "Hochschule der Bayerischen Wirtschaft": "HDBW München"}
        sites = {}
        for pat, name in dedicated.items():
            m = p[p["institution"].str.contains(pat, regex=False) & p["title"].str.lower().str.contains(THEMES["cybersecurity"])
                  & ~p["title"].str.contains("MBA")]
            sites[name] = ([(m["lat"].median(), m["lon"].median())], "d")
        sites["Hochschule Aalen"] = ([(48.8350, 10.0922)], "d")   # Baden-Württemberg, 145 km (catalogue coordinates)
        title = p["title"].str.lower().str.contains(THEMES["cybersecurity"])
        f = _focus(p["content"].fillna("")).str.lower()
        focus = f.str.contains(THEMES["cybersecurity"]) & ~f.str.contains("security printing") & ~title
        sites.update({k: (v, "w") for k, v in _sites(p[focus], "(focus) ").items()})
        sites[OTH] = ([AMBERG], "w")      # AI for Industrial Applications, IT und Automation: Amberg
        return sites, [AMBERG]
    raise ValueError(option)


def origins(option: str) -> pd.DataFrame:
    """Origin masses with coordinates and an own-region flag (OTH's own pool, Step 42)."""
    geo = counties()
    own = set(geo.loc[geo["own_pool"], "county"])
    if option == "cyber_msc":
        t5, cc = table5(), campus_coords()
        d = pd.DataFrame({"mass": t5["total"].astype(float), "lat": cc["lat"], "lon": cc["lon"]})
        near = [geo.iloc[int(np.argmin(haversine(geo["lat"].values, geo["lon"].values, r.lat, r.lon)))]["county"] for r in d.itertuples()]
        return d.assign(own=[c in own for c in near]).reset_index(drop=True)
    lv = pd.read_csv(LEAVERS, dtype={"key": str})
    lv = lv[(lv["year"] == lv["year"].max()) & (lv["key"].str.len() == 5)]
    d = lv.merge(geo, left_on="key", right_on="county")
    return pd.DataFrame({"mass": d["hzb_total"].astype(float), "lat": d["lat"], "lon": d["lon"], "own": d["county"].isin(own)})


def _attr(o, locs, beta: float) -> float:
    return max(min(haversine(o.lat, o.lon, la, lo) for la, lo in locs), 5.0) ** (-beta)


def run(option: str, beta: float, w: float, sites: dict, new_locs: list, pool: pd.DataFrame, geo: pd.DataFrame) -> dict:
    """Expected demand per site with the new programme, and the (a)/(b)/(c) split of the new programme's students."""
    weight = {"d": 1.0, "w": w}
    own = set(geo.loc[geo["own_pool"], "county"])
    in_region = {}
    for s, (locs, _) in sites.items():
        la, lo = locs[0]
        in_region[s] = geo.iloc[int(np.argmin(haversine(geo["lat"].values, geo["lon"].values, la, lo)))]["county"] in own
    with_new = pd.Series(0.0, index=[*sites, NEW])
    tot = {"a": 0.0, "b": 0.0, "c": 0.0}
    for o in pool.itertuples():
        base = {s: weight[k] * _attr(o, locs, beta) for s, (locs, k) in sites.items()}
        nv = _attr(o, new_locs, beta)
        bsum = sum(base.values())
        all_sum = bsum + nv
        for s, v in base.items():
            with_new[s] += o.mass * v / all_sum
        n = o.mass * nv / all_sum
        with_new[NEW] += n
        for s, v in base.items():
            take = n * v / bsum if bsum else 0.0
            if s == OTH or s.endswith("Ostbayerische Technische Hochschule Amberg-Weiden"):
                tot["a"] += take
            else:
                tot["b"] += take
                if o.own and not in_region[s]:
                    tot["c"] += take
    return {"demand": with_new, **{k: v / with_new[NEW] for k, v in tot.items()}}


def anchor_site(option: str, sites: dict) -> str:
    return next(s for s in sites if s.startswith("TH Ingolstadt") or s.startswith("Technische Hochschule Ingolstadt"))


def option_tables(option: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    geo = counties()
    sites, new_locs = option_sites(option)
    pool = origins(option)
    a = anchor_site(option, sites)
    rel = []
    for b, w in itertools.product(BETAS, W_ANCHOR):
        r = run(option, b, w, sites, new_locs, pool, geo)
        rel.append({"beta": b, "w": w, "OTH / anchor": r["demand"][NEW] / r["demand"][a]})
    shares = []
    for b, w in itertools.product(BETAS, W_SPLIT):
        r = run(option, b, w, sites, new_locs, pool, geo)
        shares.append({"beta": b, "w": w, "a": r["a"], "b": r["b"], "c": r["c"]})
    return pd.DataFrame(rel), pd.DataFrame(shares)


def gross_range(option: str, rel: pd.DataFrame) -> dict:
    r = rel["OTH / anchor"]
    if option == "cyber_bsc":
        s = pd.read_csv(STEP48).set_index("scenario")["gross first-years"]
        return {k: float(s[k]) for k in ("low", "central", "high")}
    if option == "robotics_bsc":
        low, high = 20 * r.min(), 60 * r.max()
    else:  # cyber_msc
        low = 30 * r.median()
        high = low * BA_SPREAD
    return {"low": low, "central": float(np.sqrt(low * high)), "high": high}


def scenarios(option: str, gross: dict, shares: pd.DataFrame) -> list[dict]:
    worst, best = shares.loc[shares["a"].idxmax()], shares.loc[shares["a"].idxmin()]
    base = shares[(shares["beta"] == 1.6) & (shares["w"] == 0.5)].iloc[0]
    out = []
    for name, r in (("low", worst), ("central", base), ("high", best)):
        g = gross[name]
        out.append({"option": option, "scenario": name, "gross first-years": round(g, 1), "(a) from OTH programmes": round(g * r["a"], 1),
                    "(b) net new to OTH": round(g * r["b"], 1), "(c) kept in region": round(g * r["c"], 1),
                    "net-new share": round(r["b"], 3), "beta": r["beta"], "w": r["w"]})
    return out


def _md(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(f"{v:.2f}" if isinstance(v, float) else str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(out)


def main() -> None:
    lines = ["# Capture + cannibalisation for all three options (generated)", ""]
    rows = []
    for option in ("cyber_bsc", "robotics_bsc", "cyber_msc"):
        sites, _ = option_sites(option)
        rel, shares = option_tables(option)
        gross = gross_range(option, rel)
        sc = scenarios(option, gross, shares)
        rows += sc
        lines += [f"## {option}", "", f"Anchor: {ANCHORS[option]}", "",
                  "Sites: " + "; ".join(f"{s} [{'dedicated' if k == 'd' else 'w'}]" for s, (_, k) in sites.items()), "",
                  "Relative capture (OTH new / TH Ingolstadt site):", "", _md(rel), "",
                  "Cannibalisation shares:", "", _md(shares), "", "Scenarios:", "", _md(pd.DataFrame(sc)), ""]
        print(f"\n== {option}: OTH/anchor {rel['OTH / anchor'].min():.2f}-{rel['OTH / anchor'].max():.2f} (median {rel['OTH / anchor'].median():.2f})")
        print(shares.round(3).to_string(index=False))
        print(pd.DataFrame(sc).to_string(index=False))
    out = pd.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWritten: {OUT.relative_to(REPO_ROOT)}, {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
