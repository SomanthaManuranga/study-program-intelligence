"""Google Trends: relative search interest in study-related terms.

Run from the repository root:

    python -m study_program_intelligence.analysis.trends [file ...]

Default input: every data/raw/trends/trends_*.csv (hand-downloaded from
trends.google.com, "Interest over time", monthly). Writes reports/trends.md.

Method notes
- Trends values are relative (0-100, peak of the whole download = 100), so only
  terms inside the same download are comparable. The first term is the anchor;
  every other term is reported as a share of the anchor.
- Google changed its data collection on 2022-01-01 (note shown on the site).
  Levels before and after that date are not compared; trends are measured
  inside each regime (2015-2021, 2022-today).
- Years are compared on January-October only, so the current year is not
  biased by missing months.
- "<1" is read as 0.5. Small terms (values below ~10) are coarse because Google
  rounds to integers; the share of zero months is reported as a quality flag.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[3]
TRENDS = REPO_ROOT / "data" / "raw" / "trends"
REPORT = REPO_ROOT / "reports" / "trends.md"
BREAK = pd.Timestamp("2022-01-01")
START = pd.Timestamp("2015-01-01")


def load(path: Path) -> pd.DataFrame:
    """Read a Trends CSV; return monthly rows with one column per term."""
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    header = next(i for i, line in enumerate(lines) if line.startswith(("Month,", "Week,")))
    if lines[header].startswith("Week,"):
        raise ValueError(f"{path.name}: weekly data; download with a range over 5 years")
    d = pd.read_csv(path, skiprows=header, encoding="utf-8-sig")
    d.columns = ["month"] + [c.split(":")[0].strip() for c in d.columns[1:]]
    d["month"] = pd.to_datetime(d["month"])
    for c in d.columns[1:]:
        d[c] = pd.to_numeric(d[c].astype(str).str.replace("<1", "0.5"), errors="coerce")
    return d[d["month"] >= START].reset_index(drop=True)


def yearly(d: pd.DataFrame) -> pd.DataFrame:
    jo = d[d["month"].dt.month <= 10]
    y = jo.groupby(jo["month"].dt.year)[list(d.columns[1:])].mean()
    y.index.name = "year"
    return y


def _slope(d: pd.DataFrame, col: str, lo: pd.Timestamp, hi: pd.Timestamp | None) -> float:
    s = d[(d["month"] >= lo) & ((d["month"] < hi) if hi is not None else True)]
    t = (s["month"] - s["month"].min()).dt.days / 365.25
    return float(np.polyfit(t, s[col], 1)[0])


def summary(d: pd.DataFrame) -> pd.DataFrame:
    anchor = d.columns[1]
    rows = []
    for c in d.columns[1:]:
        pre = d[d["month"] < BREAK][c].mean()
        post = d[d["month"] >= BREAK][c].mean()
        rows.append({
            "term": c,
            "mean 2015-21": round(pre, 2),
            "mean 2022-": round(post, 2),
            "share of anchor 2022- (%)": round(post / d[d["month"] >= BREAK][anchor].mean() * 100, 1),
            "slope 2022- (points/yr)": round(_slope(d, c, BREAK, None), 2),
            "zero months (%)": round((d[c] == 0).mean() * 100),
        })
    return pd.DataFrame(rows)


def _md(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(out)


def report(files: list[Path]) -> str:
    parts = ["# Google Trends: search interest (generated)", ""]
    for f in files:
        d = load(f)
        anchor = d.columns[1]
        y = yearly(d).round(2)
        for c in d.columns[2:]:
            y[f"{c} / {anchor} (%)"] = (y[c] / y[anchor] * 100).round(1)
        parts += [f"## {f.name}", "", f"Anchor: {anchor}. Months: {d['month'].min():%Y-%m} to {d['month'].max():%Y-%m}.", "",
                  "### Summary", "", _md(summary(d)), "",
                  "### Yearly means (January-October)", "", _md(y.reset_index()), ""]
    return "\n".join(parts)


def main(argv: list[str]) -> None:
    files = [Path(a) for a in argv] or sorted(TRENDS.glob("trends_*.csv"))
    if not files:
        sys.exit(f"No trends_*.csv in {TRENDS}")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report(files), encoding="utf-8")
    print(f"Written: {REPORT.relative_to(REPO_ROOT)} ({len(files)} file(s))")


if __name__ == "__main__":
    main(sys.argv[1:])