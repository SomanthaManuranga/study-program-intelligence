"""Demand forecast: first-year students for Informatik and a cyber proxy, Germany and Bavaria (Step 46).

Run from the repository root:

    python -m study_program_intelligence.analysis.forecast

Data: Destatis GENESIS 21311-0012 (Germany) and 21311-0015 (Bavaria), first-year students (1. Hochschulsemester,
winter semesters), 2005-2025. Destatis has no cybersecurity subject; cyber programmes are classified under
Informatik, so the cyber proxy = Informatik (SF079) + Ingenieurinformatik/Technische Informatik (SF123) +
Computer- und Kommunikationstechniken (SF200). 2025 is the Bavarian G9 transition year (it also lowers the German
total), so both series are trained to 2024; 2025 is shown as the actual dip.

Models: naive (last value), drift (mean change), ETS (additive damped trend, statsmodels), and a KMK-share model
(subject share of all first-years x total). Rolling-origin backtests from 2012, horizons 1-5, scored by MASE (mean
absolute error / in-sample mean absolute one-step change). The KMK projection did not exist at past origins, so the
share model is backtested with the ACTUAL total ("share stability"; conditional, not a fair rival). Forecasts: the
statistical model with the lowest mean MASE, and the KMK scenario (share x KMK Dok. 1 table 5.1 index of first-years
by state of study). 80 % intervals from the empirical relative backtest errors per horizon (beyond 5: scaled sqrt(h/5)).
Outputs: data/interim/forecast.csv, reports/forecast.md.
"""

from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
DESTATIS = REPO_ROOT / "data" / "raw" / "destatis"
KMK = REPO_ROOT / "data" / "raw" / "documents" / "kmk_studienanfaenger_2024_2035_tables.xlsx"
OUT = REPO_ROOT / "data" / "interim" / "forecast.csv"
REPORT = REPO_ROOT / "reports" / "forecast.md"
SUBJECTS = {"informatik": ["SF079"], "cyber_proxy": ["SF079", "SF123", "SF200"]}
FIRST_ORIGIN, MAX_H, TARGETS = 2012, 5, (2030, 2035)
LAST_TRAIN = {"DE": 2024, "BY": 2024}  # 2025 = Bavarian G9 transition (also in the German total): not used for training


def series() -> dict[tuple[str, str], pd.Series]:
    out = {}
    for region, f in (("DE", "21311-0012_DE.csv"), ("BY", "21311-0015_BY.csv")):
        d = pd.read_csv(DESTATIS / f, sep=";", dtype=str)
        d = d[d["2_variable_attribute_code"].isna() & d["3_variable_attribute_code"].isna()].copy()  # all nationalities, both sexes
        d["year"] = d["time"].str[:4].astype(int)
        d["value"] = pd.to_numeric(d["value"], errors="coerce")
        for name, codes in SUBJECTS.items():
            out[(region, name)] = d[d["4_variable_attribute_code"].isin(codes)].groupby("year")["value"].sum()
        out[(region, "all")] = d.groupby("year")["value"].sum()
    return out


def kmk_index() -> pd.DataFrame:
    """KMK Dok. 1, table 5.1: first-years by state of study (state-run HEIs, study year); columns D and BY."""
    d = pd.read_excel(KMK, sheet_name="5.1", header=None)
    h = next(i for i in range(15) if {"D", "BY"} <= set(d.iloc[i].astype(str).str.strip()))
    body = d.iloc[h + 1:].copy()
    body.columns = d.iloc[h].astype(str).str.strip()
    body = body[pd.to_numeric(body.iloc[:, 0], errors="coerce").between(2000, 2100)]
    k = pd.DataFrame({"DE": pd.to_numeric(body["D"], errors="coerce").values, "BY": pd.to_numeric(body["BY"], errors="coerce").values},
                     index=body.iloc[:, 0].astype(int).values)
    return k.dropna()


def f_naive(y: pd.Series, h: int) -> np.ndarray:
    return np.repeat(y.iloc[-1], h)


def f_drift(y: pd.Series, h: int) -> np.ndarray:
    step = (y.iloc[-1] - y.iloc[0]) / (len(y) - 1)
    return y.iloc[-1] + step * np.arange(1, h + 1)


def f_ets(y: pd.Series, h: int) -> np.ndarray:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m = ExponentialSmoothing(y.values.astype(float), trend="add", damped_trend=True, initialization_method="estimated").fit()
    return m.forecast(h)


MODELS = {"naive": f_naive, "drift": f_drift, "ets": f_ets}


def backtest(y: pd.Series, total: pd.Series, last: int) -> pd.DataFrame:
    rows = []
    y = y[y.index <= last]
    for origin in range(FIRST_ORIGIN, last):
        train = y[y.index <= origin]
        scale = train.diff().abs().mean()
        h_max = min(MAX_H, last - origin)
        preds = {name: f(train, h_max) for name, f in MODELS.items()}
        share = (train / total[total.index <= origin]).iloc[-3:].mean()
        preds["share (actual total)"] = share * total.loc[origin + 1:origin + h_max].values
        for name, p in preds.items():
            for h in range(1, h_max + 1):
                actual = y.loc[origin + h]
                rows.append({"model": name, "origin": origin, "h": h, "error": p[h - 1] - actual,
                             "rel_error": (p[h - 1] - actual) / actual, "ase": abs(p[h - 1] - actual) / scale})
    return pd.DataFrame(rows)


def interval(rel: pd.DataFrame, h: int, point: float) -> tuple[float, float]:
    """80 % band for the actual value: rel_error = (forecast - actual) / actual, so actual = forecast / (1 + rel_error);
    10 % / 90 % quantiles at horizon h (beyond MAX_H: errors scaled by sqrt(h / MAX_H))."""
    r = rel[rel["h"] == min(h, MAX_H)]["rel_error"]
    f = np.sqrt(h / MAX_H) if h > MAX_H else 1.0
    q10, q90 = np.quantile(r, 0.1) * f, np.quantile(r, 0.9) * f
    return point / (1 + q90), point / (1 + q10)


def _md(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    fmt = lambda v: f"{v:,.0f}" if isinstance(v, (float, np.floating)) and abs(v) >= 100 else (f"{v:.2f}" if isinstance(v, (float, np.floating)) else str(v))
    out += ["| " + " | ".join(fmt(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(out)


def main() -> None:
    s = series()
    k = kmk_index()
    bt_rows, fc_rows, sel_rows = [], [], []
    for region in ("DE", "BY"):
        last = LAST_TRAIN[region]
        total = s[(region, "all")]
        for name in SUBJECTS:
            y = s[(region, name)]
            bt = backtest(y, total, last)
            m = bt.groupby(["model", "h"])["ase"].mean().unstack("h")
            m["mean MASE (h=1-5)"] = m.mean(axis=1)
            for model, r in m.iterrows():
                bt_rows.append({"series": f"{region} {name}", "model": model, **{f"h={h}": r[h] for h in range(1, MAX_H + 1)},
                                "mean": r["mean MASE (h=1-5)"]})
            stat = m.drop(index="share (actual total)")
            best = stat["mean MASE (h=1-5)"].idxmin()
            sel_rows.append({"series": f"{region} {name}", "best statistical model": best,
                             "mean MASE": stat.at[best, "mean MASE (h=1-5)"], "naive MASE": stat.at["naive", "mean MASE (h=1-5)"],
                             "share stability MASE": m.at["share (actual total)", "mean MASE (h=1-5)"]})
            train = y[y.index <= last]
            horizon = max(TARGETS) - last
            pt = MODELS[best](train, horizon)
            share = (train / total[total.index <= last]).iloc[-3:].mean()
            base_k = k.at[last, region]
            rel_best = bt[bt["model"] == best]
            for t in TARGETS:
                h = t - last
                lo, hi = interval(rel_best, h, pt[h - 1])
                kmk_val = share * total.loc[last] * k.at[t, region] / base_k
                fc_rows.append({"series": f"{region} {name}", "year": t, "last actual": f"{int(train.iloc[-1]):,} ({last})",
                                f"{best} (statistical)": pt[h - 1], "80 % low": lo, "80 % high": hi,
                                "KMK scenario": kmk_val, "KMK index vs last": k.at[t, region] / base_k})
    bt_df, sel, fc = pd.DataFrame(bt_rows), pd.DataFrame(sel_rows), pd.DataFrame(fc_rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fc.to_csv(OUT, index=False)
    hist = pd.DataFrame({f"{r} {n}": s[(r, n)] for r in ("DE", "BY") for n in (*SUBJECTS, "all")})
    hist = hist[hist.index >= 2015].reset_index().rename(columns={"index": "year"})
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# Demand forecast: first-year students (generated)", "",
        "Destatis 21311-0012/-0015, winter semesters. Cyber proxy = Informatik + Technische Informatik + Computer- und "
        "Kommunikationstechniken. Both regions trained to 2024 (2025 = Bavarian G9 transition).", "",
        "## History (2015-2025)", "", _md(hist.set_index("year").astype(float).round(0).reset_index().astype({"year": str})), "",
        "## Backtests: MASE by model and horizon (rolling origin from 2012)", "",
        "MASE < 1: better than the in-sample naive one-step error. 'share (actual total)' uses the actual total and is a "
        "conditional check of share stability, not a fair rival.", "", _md(bt_df), "",
        "## Model choice", "", _md(sel), "",
        "## Forecasts", "", _md(fc), ""]), encoding="utf-8")
    print(sel.to_string(index=False)); print(fc.round(2).to_string(index=False))
    print(f"Written: {OUT.relative_to(REPO_ROOT)}, {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
