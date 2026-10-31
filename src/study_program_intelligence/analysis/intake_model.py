"""Gamma-Poisson shrinkage model over the published comparable intakes (deep-analysis layer).

Run from the repository root:

    python -m study_program_intelligence.analysis.intake_model

Purpose: the pre-registered intake range (21 / 39 / 75) anchors on two point values (THI capacity 25, Deggendorf
anecdote ~60). This module formalises the same evidence as a small shrinkage model, so the range can ALSO be stated
as a predictive distribution instead of min/anchor/max: a structured sensitivity, not a replacement (criteria D4).

Model: published intakes of German-taught dedicated cyber bachelors y_i are treated as draws of programme-level
intake rates lambda_i ~ Gamma(alpha, beta) with y_i | lambda_i ~ Poisson(lambda_i). Method-of-moments fit: the
between-programme variance is the observed variance minus the Poisson part; a new comparable programme's intake rate
follows the fitted Gamma (its prior predictive). OTH's intake = r x lambda_new, with r drawn uniformly from the
pre-registered relative-capture envelope (the 9 calibrated variants: OTH/THI 0.65-0.86 to OTH/Deggendorf 1.20-1.28,
docs/evidence_capture.md), because the sample sites span THI-like and Deggendorf-like roles.

Data (docs/evidence_capture.md, configs/intake_benchmark_documents.yaml): THI 25 (planned capacity, admission-free),
Saarland Cybersicherheit 42 and 44 (two winter semesters), TH Deggendorf ~60 (one student review). Sensitivity: with
Ruhr-Universitaet Bochum 156 (research university, different scale) to show why it is excluded.

Limitations, stated: n = 4; a capacity is not an intake; one value is an anecdote; publishers may be a selected
(proud) sample; the Gamma form is a convenience. The pre-registered range stays the decision input.

Outputs: data/interim/intake_model.csv, reports/intake_model.md.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT = REPO_ROOT / "data" / "interim" / "intake_model.csv"
REPORT = REPO_ROOT / "reports" / "intake_model.md"
COMPARABLE = {"THI Cybersicherheit (capacity)": 25, "Saarland Cybersicherheit WS 2024/25": 44,
              "Saarland Cybersicherheit WS 2025/26": 42, "TH Deggendorf Cyber Security (anecdote)": 60}
BOCHUM = {"Ruhr-Universitaet Bochum IT-Sicherheit (2024)": 156}
R_ENVELOPE = (0.65, 1.28)   # pre-registered relative-capture variants, docs/evidence_capture.md
DRAWS, SEED = 200_000, 20261031
PRE_REGISTERED = (21, 39, 75)
QUANTS = (0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95)


def fit_gamma(values: list[float]) -> tuple[float, float, float, float]:
    """Method of moments for lambda ~ Gamma(shape, rate) under Poisson sampling: Var(y) = m + Var(lambda)."""
    y = np.asarray(values, dtype=float)
    m, v = float(y.mean()), float(y.var(ddof=1))
    var_lambda = max(v - m, m * 0.05)   # floor: keep a minimal heterogeneity if the sample looks under-dispersed
    rate = m / var_lambda
    shape = m * rate
    return shape, rate, m, v


def predictive(values: list[float], rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, tuple]:
    shape, rate, m, v = fit_gamma(values)
    lam = rng.gamma(shape, 1 / rate, size=DRAWS)
    r = rng.uniform(*R_ENVELOPE, size=DRAWS)
    return lam, r * lam, (shape, rate, m, v)


def qrow(name: str, x: np.ndarray) -> dict:
    return {"quantity": name, **{f"q{int(q * 100):02d}": round(float(np.quantile(x, q)), 1) for q in QUANTS},
            "mean": round(float(x.mean()), 1)}


def main() -> None:
    rng = np.random.default_rng(SEED)
    lam, oth, (shape, rate, m, v) = predictive(list(COMPARABLE.values()), rng)
    lam_b, oth_b, (shape_b, rate_b, m_b, v_b) = predictive(list(COMPARABLE.values()) + list(BOCHUM.values()),
                                                           np.random.default_rng(SEED))
    rows = [qrow("comparable-programme intake (HAW-comparable sample, n=4)", lam),
            qrow("OTH intake = r x lambda (r in the pre-registered envelope)", oth),
            qrow("sensitivity: sample incl. Bochum 156 (research-university scale)", lam_b),
            qrow("sensitivity: OTH mapped, incl. Bochum", oth_b)]
    t = pd.DataFrame(rows)
    lo, ce, hi = PRE_REGISTERED
    inside = float(((oth >= lo) & (oth <= hi)).mean())
    below_min = float((oth < 20).mean())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    t.assign(**{"draws": DRAWS, "seed": SEED}).to_csv(OUT, index=False)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# Intake shrinkage model: published comparable intakes (generated)", "",
        f"Sample (German-taught dedicated cyber bachelors): {', '.join(f'{k} = {v}' for k, v in COMPARABLE.items())}.",
        f"Gamma fit by method of moments: shape {shape:.2f}, rate {rate:.3f} (mean {m:.1f}, sample variance {v:.1f});",
        f"with Bochum: shape {shape_b:.2f}, rate {rate_b:.3f} (mean {m_b:.1f}, variance {v_b:.1f}).",
        f"OTH mapping: intake = r x lambda, r ~ Uniform{R_ENVELOPE} from the pre-registered relative-capture variants.",
        f"{DRAWS:,} draws, seed {SEED}.", "",
        "| " + " | ".join(t.columns) + " |", "|" + "---|" * len(t.columns),
        *("| " + " | ".join(str(x) for x in r) + " |" for r in t.itertuples(index=False)), "",
        f"Reading: the structured estimate brackets the pre-registered range {PRE_REGISTERED}:",
        f"{100 * inside:.0f} % of the OTH predictive mass lies inside it, {100 * below_min:.0f} % falls below the",
        "assumed minimum cohort of 20, and the central quartiles sit around the pre-registered central value, so the",
        "anchored 21 / 39 / 75 is consistent with a shrinkage reading of the same public evidence. It is not an",
        "independent check: THI 25 and Deggendorf ~60 are the anchors themselves, and the two Saarland values are one",
        "research-university programme in two years. The Bochum sensitivity shifts the right tail up, which is why the",
        "research-university value stays a plausibility check, not part of the sample (docs/evidence_capture.md).", "",
        "Limitations: n = 4; a capacity is not an intake; one value is an anecdote; publishing universities may be a",
        "selected sample; the Gamma form is a convenience. The pre-registered range remains the decision input.", ""]),
        encoding="utf-8")
    print(t.to_string(index=False))
    print(f"inside pre-registered range: {100 * inside:.1f} %, below minimum cohort: {100 * below_min:.1f} %")
    print(f"Written: {OUT.relative_to(REPO_ROOT)}, {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
