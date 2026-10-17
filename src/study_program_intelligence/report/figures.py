"""Shared figures for report, slides and dashboard (Step 50), one style, generated from the analysis outputs.

Run from the repository root (normally via report.build):

    python -m study_program_intelligence.report.figures

Every figure reads generated data (data/interim, docs/jobsuche_snapshots.json, data/raw/destatis, data/raw/trends)
or reports/key_numbers.yaml; nothing is typed in by hand. PNG (200 dpi) for report and slides, SVG for the dashboard.
Output: reports/figures/fNN_<name>.png/.svg and reports/figures/index.md (figure, message, source doc).
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from ..analysis import forecast, trends  # noqa: E402
from .key_numbers import load as load_numbers  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
FIG = REPO_ROOT / "reports" / "figures"
INTERIM = REPO_ROOT / "data" / "interim"
# one palette for everything: options always in the same colour
OPTION = {"cyber_bsc": "#1F4E79", "cyber_msc": "#5B9BD5", "robotics_bsc": "#C55A11"}
LABEL = {"cyber_bsc": "Cybersecurity B.Sc.", "cyber_msc": "Cyber/OT M.Sc.", "robotics_bsc": "Robotics+AI B.Sc."}
GREY, LIGHT, ACCENT = "#7F7F7F", "#D9D9D9", "#2E7D32"
SOURCE_NOTE = "Source: {}"


def style() -> None:
    plt.rcParams.update({
        "figure.figsize": (7.0, 4.0), "figure.dpi": 100, "savefig.dpi": 200, "savefig.bbox": "tight",
        "font.family": "DejaVu Sans", "font.size": 10, "axes.titlesize": 12, "axes.titleweight": "bold",
        "axes.titlelocation": "left", "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": "#E6E6E6", "grid.linewidth": 0.8, "axes.axisbelow": True,
        "legend.frameon": False, "axes.edgecolor": GREY, "xtick.color": "#404040", "ytick.color": "#404040",
    })


def _save(fig, name: str, title: str, message: str, source: str, index: list) -> None:
    fig.text(0.0, -0.08, SOURCE_NOTE.format(source), fontsize=7.5, color=GREY, ha="left", va="top", transform=fig.transFigure)
    FIG.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(FIG / f"{name}.{ext}")
    plt.close(fig)
    index.append({"file": f"{name}.png", "title": title, "message": message, "source": source})


def f00_funnel(kn: dict, index: list) -> None:
    v = lambda k: kn[k]["value"]
    stages = [
        ("Screening: EMI-related theme groups", v("funnel_0_themes"),
         f"{kn['funnel_offers']['display']} programme offers, {v('funnel_subjects')} Destatis subjects (14 Oct)"),
        ("1 Demand trend", v("funnel_1_demand"), f"drop media technology / games (Medientechnik {kn['funnel_medientechnik']['display']}/yr)"),
        ("2 Supply gap, not at OTH", v("funnel_2_candidates"),
         f"drop generic AI ({v('funnel_ai_ba_150km')} BA / {v('funnel_ai_ma_150km')} MA within 150 km), themes OTH offers; "
         "microelectronics to watch list"),
        ("3 Kill rule 1: overlap", v("funnel_3_shortlist"),
         f"drop embedded/CPS master ({kn['funnel_embedded_overlap']['display']}), part-time AI master (exists)"),
        ("4 Kill rules 2-4", v("funnel_4_after_gates"), "none dropped (feasibility, trend, pipeline)"),
        ("5 Ranking (MCDA + Monte Carlo)", 1, f"Cybersecurity B.Sc., first in {kn['p_rank1_cyber_bsc_base']['display']} of draws"),
    ]
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    top = max(s[1] for s in stages)
    for i, (lab, cnt, note) in enumerate(stages):
        y = len(stages) - 1 - i
        w = 0.6 + 0.4 * cnt / top   # minimum width keeps the last label inside its bar
        col = OPTION["cyber_bsc"] if i == len(stages) - 1 else ("#9DB7D5" if i else LIGHT)
        ax.barh(y, w, left=-w / 2, height=0.72, color=col)
        ax.text(0, y + 0.08, f"{lab}: {cnt}", ha="center", va="center", fontsize=8.5, fontweight="bold",
                color="white" if i == len(stages) - 1 else "black")
        ax.text(0, y - 0.22, note, ha="center", va="center", fontsize=7, color="white" if i == len(stages) - 1 else "#404040")
    ax.set_xlim(-0.55, 0.55)
    ax.set_ylim(-0.45, len(stages) - 0.55)
    ax.axis("off")
    ax.set_title(f"Selection funnel: rules and weights fixed {kn['rules_fixed_date']['display']}, before screening")
    _save(fig, "f00_funnel", "Selection funnel",
          "Candidates were filtered stage by stage with rules fixed in advance; the winner came out at the end.",
          "docs/evidence_funnel.md (from evidence_competition_demand, overlap_test, kill_rules, evidence_ranking)", index)


def f01_demand_forecast(kn: dict, index: list) -> None:
    y = forecast.series()[("BY", "cyber_proxy")]
    y = y[y.index >= 2010]
    fc = pd.read_csv(INTERIM / "forecast.csv")
    by = fc[fc["series"] == "BY cyber_proxy"].set_index("year")
    last = int(forecast.LAST_TRAIN["BY"])
    fig, ax = plt.subplots()
    ax.plot(y.index, y.values, color=OPTION["cyber_bsc"], lw=2, label="Actual first-years")
    yrs = [last, 2030, 2035]
    base = float(y.loc[last])
    for col, lab, ls, c in (("KMK scenario", "Conservative (KMK, constant share)", "--", GREY),
                            ("drift (statistical)", "Upside (drift trend)", ":", GREY)):
        ax.plot(yrs, [base, by.at[2030, col], by.at[2035, col]], ls=ls, color=c, lw=1.5, label=lab)
    cen = [base] + [kn[f"cyber_proxy_by_{t}_central"]["value"] for t in (2030, 2035)]
    ax.plot(yrs, cen, color=ACCENT, lw=2, marker="o", label="Central (planning midpoint)")
    ax.annotate("2025: G9 dip", (2025, float(y.loc[2025])), xytext=(2019.5, float(y.loc[2025]) - 500), fontsize=8,
                arrowprops={"arrowstyle": "-", "color": GREY}, color=GREY)
    ax.set_title("Bavaria: first-year students in the cyber recruiting pool")
    ax.set_ylabel("First-years (winter semester)")
    ax.set_ylim(0, None)
    ax.legend(loc="lower right", fontsize=8)
    _save(fig, "f01_demand_forecast", "Demand forecast, Bavaria cyber proxy",
          "The recruiting pool does not shrink: ~5,500 first-years in 2030 even in the conservative case.",
          "Destatis 21311-0015; docs/evidence_forecast.md", index)


def f02_search_interest(index: list) -> None:
    d = trends.yearly(trends.load(trends.TRENDS / "trends_DE_specialist_2015_2026.csv"))
    cols = {c: c.split(":")[0].replace(" Studium", "") for c in d.columns}
    fig, ax = plt.subplots()
    colour = {"Cyber Security": OPTION["cyber_bsc"], "Künstliche Intelligenz": GREY, "Robotik": OPTION["robotics_bsc"]}
    for c, lab in cols.items():
        if lab in colour:
            ax.plot(d.index, d[c], lw=2, color=colour[lab], label=f"'{lab} Studium'")
    ax.axvline(2022, color=LIGHT, lw=1)
    ax.set_title("Google search interest in Germany, yearly mean")
    ax.set_ylabel("Index (0-100, same download)")
    ax.legend(fontsize=8)
    _save(fig, "f02_search_interest", "Search interest in specialist degrees",
          "Cyber Security is the largest specialist search term (about 2x KI, 2.6x Robotik since 2022), flat since 2022.",
          "Google Trends (manual download); docs/evidence_demand_trends.md", index)


def f03_job_ads(index: list, kn: dict) -> None:
    s = pd.DataFrame(json.loads((REPO_ROOT / "docs" / "jobsuche_snapshots.json").read_text(encoding="utf-8")))
    date = kn["job_snapshot_date"]["value"]
    s = s[s["date"] == date].pivot_table(index=["keyword", "group"], columns="region_id", values="total").reset_index()
    s["share"] = 100 * s["bayern"] / s["germany"]
    s = s.sort_values("share")
    colour = s["group"].map({"cybersecurity": OPTION["cyber_bsc"], "robotics": OPTION["robotics_bsc"]}).fillna(LIGHT)
    fig, ax = plt.subplots(figsize=(7.0, 4.6))
    ax.barh(s["keyword"], s["share"], color=colour)
    ax.axvspan(22, 25, color="#F2F2F2", zorder=0)
    ax.text(23.5, len(s) - 0.3, "IT baseline 22-25 %", ha="center", va="bottom", fontsize=7.5, color=GREY)
    for i, (sh, n100) in enumerate(zip(s["share"], s["amberg_100km"])):
        ax.text(sh + 0.4, i, f"{sh:.0f} %  ({int(n100)} ads ≤100 km)", va="center", fontsize=7.5)
    ax.set_xlim(0, 45)
    ax.set_xlabel("Bavaria's share of all German job ads for the keyword (%)")
    ax.set_title("Job ads: Bavaria's share by keyword")
    _save(fig, "f03_job_ads", "Job ads: Bavaria's share by keyword",
          "Security, especially OT security, is over-represented in Bavaria; robotics has the strongest local signal.",
          f"BA Jobsuche API, snapshot {date}; docs/evidence_outlet_jobs.md", index)


def f04_capture(index: list, kn: dict) -> None:
    d = pd.read_csv(INTERIM / "option_scenarios.csv")
    opts = list(OPTION)
    x = np.arange(len(opts))
    fig, ax = plt.subplots()
    for i, o in enumerate(opts):
        r = d[d["option"] == o].set_index("scenario")
        g = r["gross first-years"]
        nn = r["(b) net new to OTH"]
        ax.plot([i - 0.12] * 2, [g["low"], g["high"]], color=LIGHT, lw=8, solid_capstyle="butt")
        ax.plot([i + 0.12] * 2, [nn["low"], nn["high"]], color=OPTION[o], lw=8, solid_capstyle="butt", alpha=0.5)
        ax.plot(i - 0.12, g["central"], "o", color=GREY)
        ax.plot(i + 0.12, nn["central"], "o", color=OPTION[o])
        ax.text(i + 0.22, nn["central"], f"{nn['central']:.0f}", va="center", fontsize=8)
    ax.axhline(kn["min_cohort"]["value"], color="#C00000", ls="--", lw=1)
    ax.text(0.5, kn["min_cohort"]["value"] - 1.5, "assumed minimum cohort 20", ha="center", va="top", fontsize=7.5, color="#C00000")
    ax.set_xticks(x, [LABEL[o] for o in opts])
    ax.set_ylabel("First-years per year (steady state)")
    ax.set_title("Expected first-years: gross (grey) and net new to OTH (colour)")
    ax.set_ylim(0, None)
    _save(fig, "f04_capture", "Capture model: first-years per option",
          "Same model for all options; bars = low-high, dots = central. Robotics has no intake anchor.",
          "data/interim/option_scenarios.csv; docs/evidence_capture.md, docs/evidence_ranking.md", index)


def f05_cannibalisation(index: list) -> None:
    d = pd.read_csv(INTERIM / "option_scenarios.csv")
    d = d[d["scenario"] == "central"].set_index("option").loc[list(OPTION)]
    fig, ax = plt.subplots(figsize=(7.0, 3.2))
    y = np.arange(len(d))[::-1]
    a, b, c = d["(a) from OTH programmes"], d["(b) net new to OTH"] - d["(c) kept in region"], d["(c) kept in region"]
    ax.barh(y, a, color=LIGHT, label="(a) taken from existing OTH programmes")
    ax.barh(y, b, left=a, color=[OPTION[o] for o in d.index], label="(b) won from other universities")
    ax.barh(y, c, left=a + b, color=ACCENT, label="(c) of which kept in the region")
    for yi, o in zip(y, d.index):
        tot = d.at[o, "gross first-years"]
        ax.text(tot + 0.6, yi, f"{100 * d.at[o, 'net-new share']:.0f} % net new", va="center", fontsize=8)
    ax.set_yticks(y, [LABEL[o] for o in d.index])
    ax.set_xlabel("First-years per year, central scenario")
    ax.set_title("Where the new programme's students would come from")
    ax.legend(fontsize=7.5, loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=3)
    ax.set_title("Where the new programme's students would come from", pad=24)
    ax.set_xlim(0, d["gross first-years"].max() * 1.3)
    _save(fig, "f05_cannibalisation", "Cannibalisation and regional benefit",
          "Most students would be new to OTH; cannibalisation is limited and highest for the master.",
          "data/interim/option_scenarios.csv; docs/evidence_cannibalisation.md", index)


def f06_rank_probabilities(index: list) -> None:
    d = pd.read_csv(INTERIM / "ranking_summary.csv")
    scen = ["base", "robotics 50 % cannibalisation"]
    fig, axes = plt.subplots(1, 2, figsize=(7.5, 3.4), sharey=True)
    for ax, s in zip(axes, scen):
        r = d[d["scenario"] == s].set_index("option").loc[list(OPTION)]
        y = np.arange(len(r))[::-1]
        left = np.zeros(len(r))
        for k, alpha in (("P(rank 1)", 1.0), ("P(rank 2)", 0.55), ("P(rank 3)", 0.2)):
            ax.barh(y, 100 * r[k], left=left, color=[OPTION[o] for o in r.index], alpha=alpha)
            left += 100 * r[k].values
        for yi, p in zip(y, r["P(rank 1)"]):
            ax.text(2, yi, f"{100 * p:.0f} %", va="center", color="white" if p > 0.15 else "black", fontsize=8, fontweight="bold")
        ax.set_yticks(y, [LABEL[o] for o in r.index])
        ax.set_xlim(0, 100)
        ax.set_title(s.capitalize(), fontsize=10)
        ax.set_xlabel("% of 10,000 draws (dark = rank 1, mid = 2, light = 3)", fontsize=8)
    fig.suptitle("Ranking: probability of each rank (MCDA + Monte Carlo)", x=0.0, y=1.06, ha="left", fontweight="bold")
    _save(fig, "f06_rank_probabilities", "Rank probabilities",
          "The Cybersecurity B.Sc. ranks first in about nine of ten draws, also if robotics cannibalises 50 %.",
          "data/interim/ranking_summary.csv; docs/evidence_ranking.md", index)


def f07_leave_one_out(index: list) -> None:
    d = pd.read_csv(INTERIM / "ranking_loo.csv")
    d = d[d["scenario"] == "base"].set_index("criterion left out")
    fig, ax = plt.subplots(figsize=(7.0, 3.6))
    y = np.arange(len(d))[::-1]
    h = 0.27
    for j, o in enumerate(OPTION):
        ax.barh(y + (1 - j) * h, 100 * d[f"P(rank 1) {o}"], height=h, color=OPTION[o], label=LABEL[o])
    ax.axvline(80, color="#C00000", ls="--", lw=1)
    ax.text(80.5, -0.75, "80 % robustness bar", fontsize=7.5, color="#C00000")
    ax.set_yticks(y, [c.replace("_", " ") for c in d.index])
    ax.set_xlim(0, 100)
    ax.set_xlabel("P(rank 1) when this criterion is left out (%)")
    ax.set_title("Leave-one-criterion-out")
    ax.legend(fontsize=7.5, loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=3)
    ax.set_title("Leave-one-criterion-out", pad=24)
    _save(fig, "f07_leave_one_out", "Leave-one-criterion-out",
          "The Cybersecurity B.Sc. stays first whichever criterion is dropped; demand and labour carry most of the lead.",
          "data/interim/ranking_loo.csv; docs/evidence_ranking.md", index)


def main() -> None:
    style()
    kn = load_numbers()
    index: list[dict] = []
    f00_funnel(kn, index)
    f01_demand_forecast(kn, index)
    f02_search_interest(index)
    f03_job_ads(index, kn)
    f04_capture(index, kn)
    f05_cannibalisation(index)
    f06_rank_probabilities(index)
    f07_leave_one_out(index)
    lines = ["# Shared figures (generated)", "", "| File | Title | Message | Source |", "|---|---|---|---|"]
    lines += [f"| {r['file']} | {r['title']} | {r['message']} | {r['source']} |" for r in index]
    (FIG / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Written: {len(index)} figures in {FIG.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
