"""Equal evidence for the confirmed candidates: demand, competition, capture and cannibalisation (re-scope, week 3).

Run from the repository root (after transform.programmes --set full and analysis.options):

    python -m study_program_intelligence.analysis.candidates

Inputs: configs/candidates.yaml (themes, subject codes, capture rule, trend rule), the full catalogue
(data/processed/programmes_full.csv), the cached Destatis tables (analysis/demand_split.py), the Step 47/48 model
(analysis/options.py).
- Demand: Destatis first-years (graduates for the master) for the candidate's subject codes, German and foreign
  separately, Germany and Bavaria; trend score by the rule in configs/candidates.yaml.
- Competition: full-time offers at the candidate's level whose title matches the theme (dedicated) or whose focus
  field does (focus); Germany, Bavaria, within 150 km and 80 km of OTH (km_oth); OTH's own matches are listed apart.
- Capture: the Step 47/48 model unchanged. Sites = Bavarian offers of the level (any study form, as in options.py),
  dedicated at weight 1, focus at w, OTH's existing related programmes as one Amberg site at w (at 1 if an OTH
  programme's title matches the theme: then OTH already offers the type). No candidate has a public intake figure for
  a comparator, so the robotics logic applies: assumed comparator intake 20-60 at the nearest dedicated site, range
  over all model variants. Without any dedicated site in Bavaria there is no comparator: gross range 10-60 (the
  assumed range, widened downwards because nothing supports even 20). Without any competitor site at all (only OTH's
  own programmes) the Huff split is degenerate (everything from OTH); the shares are then the span of the other
  candidates' model runs (lowest, median, highest net-new share).
Outputs: data/interim/candidate_scenarios.csv, data/interim/candidate_competition.csv, data/interim/candidate_demand.csv,
reports/candidates.md, reports/figures/competitors_<candidate>.png.
"""

from __future__ import annotations

import itertools
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from .catchment import counties
from .demand_split import cagr, load as load_destatis
from .options import AMBERG, BETAS, OTH, W_ANCHOR, W_SPLIT, WEIDEN, NEW, origins, run, scenarios
from .options import OUT as OPTION_SCENARIOS
from .theme_check import _focus

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG = REPO_ROOT / "configs" / "candidates.yaml"
PROGS = REPO_ROOT / "data" / "processed" / "programmes_full.csv"
OUT = REPO_ROOT / "data" / "interim" / "candidate_scenarios.csv"
COMP = REPO_ROOT / "data" / "interim" / "candidate_competition.csv"
DEMAND = REPO_ROOT / "data" / "interim" / "candidate_demand.csv"
REPORT = REPO_ROOT / "reports" / "candidates.md"
FIG = REPO_ROOT / "reports" / "figures"
ASSUMED = (20, 60)          # comparator intake without an anchor (robotics logic, options.py)
NO_COMPARATOR = (10, 60)    # no dedicated site in Bavaria


def config() -> dict:
    return yaml.safe_load(CONFIG.read_text(encoding="utf-8"))


def matches(p: pd.DataFrame, c: dict) -> tuple[pd.Series, pd.Series]:
    """(dedicated, focus) masks: theme in the title, or in the focus field only; exclusions apply to both."""
    title = p["title"].str.contains(c["theme"], case=False, regex=True)
    focus = _focus(p["content"].fillna("")).str.contains(c["theme"], case=False, regex=True) & ~title
    if c.get("exclude"):
        bad = p["title"].str.contains(c["exclude"], case=False, regex=True)
        title, focus = title & ~bad, focus & ~bad
    return title, focus


def offers(c: dict) -> pd.DataFrame:
    p = pd.read_csv(PROGS)
    return p[p["degree"].str.startswith(c["level"]) & (p["study_form"] == "Vollzeitstudium")].copy()


def competition(key: str, c: dict) -> tuple[dict, pd.DataFrame]:
    p = offers(c)
    title, focus = matches(p, c)
    ded = p[title & ~p["is_oth"]]
    near = lambda d, km: d[d["km_oth"] <= km]
    row = {"candidate": key, "level": c["level"],
           "dedicated institutions DE": ded["institution"].nunique(), "dedicated offers DE": len(ded),
           "dedicated institutions BY": ded.loc[ded["state"] == "Bayern", "institution"].nunique(),
           "dedicated institutions <=150 km": near(ded, 150)["institution"].nunique(),
           "dedicated institutions <=80 km": near(ded, 80)["institution"].nunique(),
           "focus offers DE": int((focus & ~p["is_oth"]).sum()),
           "focus offers <=150 km": int((focus & ~p["is_oth"] & (p["km_oth"] <= 150)).sum()),
           "OTH own matches": "; ".join(p.loc[(title | focus) & p["is_oth"], "title"]) or "-",
           "nearest dedicated": "; ".join(f"{r.institution} {r.km_oth:.0f} km"
                                          for r in ded.sort_values("km_oth").drop_duplicates("institution").head(4).itertuples()) or "-"}
    hits = p[(title | focus) & (p["km_oth"] <= 150)].assign(candidate=key, kind=np.where(title[(title | focus) & (p["km_oth"] <= 150)], "dedicated", "focus"))
    return row, hits[["candidate", "kind", "title", "institution", "city", "km_oth", "is_oth"]].sort_values(["kind", "km_oth"])


def competitor_map(key: str, c: dict) -> Path:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    p = offers(c)
    title, focus = matches(p, c)
    fig, ax = plt.subplots(figsize=(5, 6))
    ax.scatter(p.loc[focus & ~p["is_oth"], "lon"], p.loc[focus & ~p["is_oth"], "lat"], s=12, c="#9aa5b1", label="focus")
    ax.scatter(p.loc[title & ~p["is_oth"], "lon"], p.loc[title & ~p["is_oth"], "lat"], s=28, c="#c0392b", label="dedicated")
    ax.scatter([AMBERG[1]], [AMBERG[0]], s=120, marker="*", c="#1f4e79", label="OTH Amberg")
    t = np.linspace(0, 2 * np.pi, 200)
    ax.plot(AMBERG[1] + 150 / (111.3 * np.cos(np.radians(AMBERG[0]))) * np.cos(t), AMBERG[0] + 150 / 111.3 * np.sin(t),
            c="#1f4e79", lw=0.8, ls="--", label="150 km")
    ax.set_xlim(5.5, 15.5); ax.set_ylim(47.2, 55.2)
    ax.set_title(f"{c['label']}: full-time {c['level'].lower()} offers", fontsize=9)
    ax.legend(fontsize=7, loc="upper left"); ax.set_xticks([]); ax.set_yticks([])
    FIG.mkdir(parents=True, exist_ok=True)
    out = FIG / f"competitors_{key}.png"
    fig.savefig(out, dpi=130, bbox_inches="tight"); plt.close(fig)
    return out


def trend_score(growth: float, rule: dict) -> dict:
    central = next((s for cut, s in zip(rule["cuts"], rule["scores"]) if growth >= cut), rule["scores"][-1])
    return {"low": max(1, central - 1), "central": central, "high": min(5, central + 1)}


def demand(key: str, c: dict, long: pd.DataFrame, rule: dict) -> list[dict]:
    kind, codes = c["subjects"]["kind"], c["subjects"]["codes"]
    y0, y1 = (2019, 2025) if kind == "graduates" else (2019, 2024)
    rows = []
    for region in ("DE", "BY"):
        d = long[(long["kind"] == kind) & (long["region"] == region) & long["code"].isin(codes)]
        p = d.pivot_table(index="year", columns="nationality", values="value", aggfunc="sum")
        p["all"] = p["German"] + p["foreign"]
        g = {k: round(cagr(p.at[y0, k], p.at[y1, k], y1 - y0), 1) for k in ("all", "German", "foreign")}
        rows.append({"candidate": key, "series": f"{kind} {'+'.join(codes)}", "region": region, "window": f"{y0}-{y1}",
                     "all start": int(p.at[y0, "all"]), "all end": int(p.at[y1, "all"]),
                     "German start": int(p.at[y0, "German"]), "German end": int(p.at[y1, "German"]),
                     "foreign start": int(p.at[y0, "foreign"]), "foreign end": int(p.at[y1, "foreign"]),
                     "all %/yr": g["all"], "German %/yr": g["German"], "foreign %/yr": g["foreign"],
                     "foreign share end %": int(round(100 * p.at[y1, "foreign"] / p.at[y1, "all"]))})
    by = rows[1]
    rows[1]["trend score (all)"] = trend_score(by["all %/yr"], rule)["central"]
    rows[1]["trend score (German only)"] = trend_score(by["German %/yr"], rule)["central"]
    return rows


def candidate_sites(c: dict) -> tuple[dict, list, str]:
    """Sites as in options.option_sites (Bavaria, level, any study form) and the comparator (nearest dedicated site)."""
    p = pd.read_csv(PROGS)
    p = p[(p["state"] == "Bayern") & p["degree"].str.startswith(c["level"])]
    title, focus = matches(p, c)
    site = lambda df, prefix="": {f"{prefix}{i} ({ci})": [(r.lat, r.lon)]
                                  for (i, ci), r in df[~df["is_oth"]].groupby(["institution", "city"])[["lat", "lon"]].median().iterrows()}
    sites = {k: (v, "d") for k, v in site(p[title]).items()}
    sites.update({k: (v, "w") for k, v in site(p[focus], "(focus) ").items()})
    sites[OTH] = ([AMBERG], "d" if (title & p["is_oth"]).any() else "w")
    ded = p[title & ~p["is_oth"]]
    anchor = ""
    if len(ded):
        r = ded.sort_values("km_oth").iloc[0]
        anchor = f"{r.institution} ({r.city})"
    return sites, [AMBERG, WEIDEN], anchor


def capture(key: str, c: dict) -> tuple[list[dict], str]:
    if c["capture"] != "own":   # same competitor set as a baseline option: reuse its rows
        s = pd.read_csv(OPTION_SCENARIOS)
        rows = s[s["option"] == c["capture"]].assign(option=key).to_dict("records")
        return rows, f"model of the baseline option {c['capture']} (same competitor set), reused unchanged"
    geo = counties()
    sites, new_locs, anchor = candidate_sites(c)
    if len(sites) == 1:     # only OTH's own site: no split possible, filled in main() from the other candidates
        return [], "no competitor site in Bavaria (dedicated or focus): the Huff split is degenerate"
    pool = origins("bachelor" if c["level"] == "Bachelor" else "cyber_msc")
    shares = pd.DataFrame([{"beta": b, "w": w, **{k: run(key, b, w, sites, new_locs, pool, geo)[k] for k in "abc"}}
                           for b, w in itertools.product(BETAS, W_SPLIT)])
    if anchor:
        rel = [run(key, b, w, sites, new_locs, pool, geo) for b, w in itertools.product(BETAS, W_ANCHOR)]
        r = pd.Series([x["demand"][NEW] / x["demand"][anchor] for x in rel])
        low, high = ASSUMED[0] * r.min(), ASSUMED[1] * r.max()
        note = (f"no public intake figure: assumed comparator intake {ASSUMED[0]}-{ASSUMED[1]} at {anchor}; "
                f"OTH new / comparator {r.min():.2f}-{r.max():.2f}")
    else:
        low, high = NO_COMPARATOR
        note = f"no dedicated programme in Bavaria, so no comparator: gross {NO_COMPARATOR[0]}-{NO_COMPARATOR[1]} (assumption, widened)"
    gross = {"low": low, "central": float(np.sqrt(low * high)), "high": high}
    return scenarios(key, gross, shares), note


def _md(df: pd.DataFrame) -> str:
    cols = [str(x) for x in df.columns]
    fmt = lambda v: f"{v:.2f}" if isinstance(v, float) else str(v).replace("|", "/")
    return "\n".join(["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
                     + ["| " + " | ".join(fmt(v) for v in r) + " |" for r in df.itertuples(index=False)])


def main() -> None:
    cfg = config()
    long = load_destatis()
    comp, hits, dem, scen, notes = [], [], [], [], {}
    for key, c in cfg["candidates"].items():
        row, h = competition(key, c)
        comp.append(row); hits.append(h)
        competitor_map(key, c)
        dem += demand(key, c, long, cfg["trend_rule"])
        rows, notes[key] = capture(key, c)
        scen += rows
    own = pd.DataFrame(scen)
    own = own[own["option"].isin([k for k, c in cfg["candidates"].items() if c["capture"] == "own"])]
    for key, c in cfg["candidates"].items():
        if c["capture"] == "own" and key not in set(own["option"]):
            low, high = NO_COMPARATOR
            g = {"low": low, "central": float(np.sqrt(low * high)), "high": high}
            span = {"low": own["net-new share"].min(), "central": own["net-new share"].median(), "high": own["net-new share"].max()}
            kept = (own["(c) kept in region"] / own["gross first-years"])
            kept = {"low": kept.min(), "central": kept.median(), "high": kept.max()}
            for name in ("low", "central", "high"):
                scen.append({"option": key, "scenario": name, "gross first-years": round(g[name], 1),
                             "(a) from OTH programmes": round(g[name] * (1 - span[name]), 1),
                             "(b) net new to OTH": round(g[name] * span[name], 1), "(c) kept in region": round(g[name] * kept[name], 1),
                             "net-new share": round(span[name], 3), "beta": "", "w": ""})
            notes[key] += (f"; gross {low}-{high} (assumption, widened); shares = span of the other candidates' runs "
                           f"(net-new {span['low']:.2f}-{span['high']:.2f})")
    comp, hits, dem, scen = pd.DataFrame(comp), pd.concat(hits), pd.DataFrame(dem), pd.DataFrame(scen)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    scen.to_csv(OUT, index=False); comp.to_csv(COMP, index=False); dem.to_csv(DEMAND, index=False)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# Equal evidence for the candidates (generated)", "",
        "Config: configs/candidates.yaml. Full-time offers, full catalogue (Germany). Maps: reports/figures/competitors_*.png.", "",
        "## Demand: first-years (master: graduates) by nationality", "", _md(dem.fillna("")), "",
        "## Competition", "", _md(comp), "",
        "## Capture and cannibalisation (Step 47/48 model)", "",
        *[f"- {k}: {v}" for k, v in notes.items()], "", _md(scen), "",
        "## Every hit within 150 km (for the hand check of the themes)", "", _md(hits), ""]), encoding="utf-8")
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 60)
    print(dem.to_string(index=False)); print(); print(comp.drop(columns=["nearest dedicated"]).to_string(index=False))
    print(); print(scen.to_string(index=False)); print(); print("\n".join(f"{k}: {v}" for k, v in notes.items()))
    print(f"\nWritten: {OUT.relative_to(REPO_ROOT)}, {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
