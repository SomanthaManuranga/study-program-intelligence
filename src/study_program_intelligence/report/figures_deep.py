"""Figures for the deep-analysis layer: specification curves and the intake predictive distribution.

Run from the repository root (after analysis.spec_curve and analysis.intake_model):

    python -m study_program_intelligence.report.figures_deep

Follows the house figure conventions (report/figures.py): one palette with fixed option colours, recessive grid,
source note under each figure. Single-hue panels with direct text labels, so identity never rests on colour alone
(the palette validator needs Node.js, which this machine lacks - the same mitigation as in Step 52).
Outputs: reports/figures/f09_spec_curve.png/.svg, reports/figures/f10_intake_model.png/.svg.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
INTERIM = REPO_ROOT / "data" / "interim"
FIG = REPO_ROOT / "reports" / "figures"
OPTION = {"cyber": "#1F4E79", "robotics_b": "#C55A11"}
GREY, LIGHT, INK = "#7F7F7F", "#D9D9D9", "#262626"


def style() -> None:
    plt.rcParams.update({
        "figure.dpi": 130, "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
        "axes.grid": True, "grid.color": "#E6E6E6", "grid.linewidth": 0.8, "axes.axisbelow": True,
        "legend.frameon": False, "axes.edgecolor": GREY, "xtick.color": "#404040", "ytick.color": "#404040",
        "axes.spines.top": False, "axes.spines.right": False, "text.color": INK, "axes.labelcolor": INK})


def save(fig: plt.Figure, name: str, source: str) -> None:
    fig.text(0.0, -0.06, f"Source: {source}", fontsize=7.5, color=GREY, ha="left", va="top", transform=fig.transFigure)
    FIG.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(FIG / f"{name}.{ext}", bbox_inches="tight")
    plt.close(fig)


def spec_panel(ax: plt.Axes, d: pd.DataFrame, colour: str, title: str) -> None:
    y = np.sort(d["gross central"].to_numpy())
    ax.plot(np.arange(1, len(y) + 1), y, color=colour, lw=2)
    ax.axhline(20, color=GREY, lw=1, ls="--")
    ax.text(len(y) * 0.02, 20, " assumed minimum cohort 20", fontsize=7.5, color=GREY, va="bottom", ha="left")
    pre = d.loc[d["pre-registered"], "gross central"]
    if len(pre):
        v = float(pre.iloc[0])
        x = int(np.searchsorted(y, v)) + 1
        ax.plot([x], [v], marker="o", ms=8, color=colour, mfc="white", mew=2)
        ax.annotate(f"pre-registered spec: {v:.1f}", (x, v), textcoords="offset points", xytext=(8, -14),
                    fontsize=8, color=INK)
    share = 100 * (d.loc[d["min cohort"] == 20, "gross central"] >= 20).mean()
    ax.set_title(f"{title}\ncentral estimate >= 20 in {share:.0f} % of specifications", loc="left")
    ax.set_xlabel("specification rank (sorted by outcome)")


def fig_spec_curve() -> None:
    cap = pd.read_csv(INTERIM / "spec_curve_capture.csv")
    rank = pd.read_csv(INTERIM / "spec_curve_ranking.csv")
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.4))
    spec_panel(axes[0], cap[cap["candidate"] == "cyber"], OPTION["cyber"], "Cybersecurity B.Sc. (level c)")
    spec_panel(axes[1], cap[cap["candidate"] == "robotics_b"], OPTION["robotics_b"], "Robotics + AI path B (level b)")
    axes[0].set_ylabel("central steady-state gross first-years")
    ylim = (0, max(axes[0].get_ylim()[1], axes[1].get_ylim()[1]))
    axes[0].set_ylim(*ylim)
    axes[1].set_ylim(*ylim)
    y = np.sort(rank["P1 cyber"].to_numpy())
    ax = axes[2]
    ax.plot(np.arange(1, len(y) + 1), y, color=OPTION["cyber"], lw=2)
    pre = rank.loc[rank["pre-registered"], "P1 cyber"]
    if len(pre):
        v = float(pre.iloc[0])
        x = int(np.searchsorted(y, v)) + 1
        ax.plot([x], [v], marker="o", ms=8, color=OPTION["cyber"], mfc="white", mew=2)
        ax.annotate(f"pre-registered: {v:.3f}", (x, v), textcoords="offset points", xytext=(-86, 6), fontsize=8, color=INK)
    ax.set_ylim(0, 1)
    ax.set_title(f"Baseline ranking: P(cyber first)\nfirst in {100 * rank['cyber first'].mean():.0f} % of specifications",
                 loc="left")
    ax.set_xlabel("specification rank (sorted)")
    fig.tight_layout()
    save(fig, "f09_spec_curve",
         "data/interim/spec_curve_capture.csv, spec_curve_ranking.csv (analysis/spec_curve.py); pre-registered machinery rerun under all reasonable specification variants")


def fig_intake_model() -> None:
    t = pd.read_csv(INTERIM / "intake_model.csv")
    oth = t[t["quantity"].str.startswith("OTH intake")].iloc[0]
    rng = np.random.default_rng(int(oth["seed"]))
    # reproduce the predictive draws for the density outline (same seed and model as analysis/intake_model.py)
    from study_program_intelligence.analysis.intake_model import COMPARABLE, predictive
    _, draws, _ = predictive(list(COMPARABLE.values()), rng)
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.hist(draws, bins=np.arange(0, 120, 2.5), density=True, color=OPTION["cyber"], alpha=0.35, edgecolor="white")
    for v, lab, dy in ((21, "pre-registered low 21", 0), (39, "central 39", 12), (75, "high 75", 0)):
        ax.axvline(v, color=GREY, lw=1.2)
        ax.text(v + 1, ax.get_ylim()[1] * 0.92 - dy * 0.0005, lab, fontsize=8, color=INK, rotation=90, va="top")
    ax.axvline(20, color=GREY, lw=1, ls="--")
    ax.text(19, ax.get_ylim()[1] * 0.5, "assumed minimum cohort 20 ", fontsize=7.5, color=GREY, rotation=90, va="center", ha="right")
    q = {k: float(oth[k]) for k in ("q05", "q50", "q95")}
    ax.set_title("Shrinkage model of published comparable intakes, mapped to OTH\n"
                 f"predictive q05 {q['q05']:.0f} / median {q['q50']:.0f} / q95 {q['q95']:.0f}; "
                 "92.5 % of the mass inside the pre-registered range", loc="left")
    ax.set_xlabel("first-years per year")
    ax.set_ylabel("predictive density")
    save(fig, "f10_intake_model",
         "data/interim/intake_model.csv (analysis/intake_model.py); sample: THI 25, Saarland 44/42, Deggendorf ~60")


def main() -> None:
    style()
    fig_spec_curve()
    fig_intake_model()
    print(f"Written: {FIG / 'f09_spec_curve.png'}, {FIG / 'f10_intake_model.png'} (+ .svg)")


if __name__ == "__main__":
    main()
