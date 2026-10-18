"""Demand by nationality: German vs foreign first-years and graduates (data-sufficiency audit, G1).

Run from the repository root:

    python -m study_program_intelligence.analysis.demand_split

Data (all cached, no download): Destatis 21311-0012 (Germany) / 21311-0015 (Bavaria) first-years (1st university
semester, winter semesters) and 21321-0003 / 21321-0006 passed exams, by nationality (German / foreign) and subject;
LfStat "Studierende an den Hochschulen in Bayern" WS 2024/25, Tabelle 3.2 (study area Informatik by university type
and nationality). Series as in the base evidence: cyber proxy = Informatik + Ingenieurinformatik/Technische Informatik
+ Computer- und Kommunikationstechniken (forecast.py); master pipeline = Informatik graduates (Step 49); robotics feeders
= Mechatronik + Ingenieurinformatik/Technische Informatik (Step 49 score sheet). "Foreign" = foreign nationality
(includes foreigners with a German school-leaving certificate). Degree level is not available at subject level.
Outputs: data/interim/demand_split.csv, reports/demand_split.md.
"""

from __future__ import annotations

import itertools
import re
from pathlib import Path

import pandas as pd
import pypdf

from study_program_intelligence.analysis.first_look import SUBJECTS
from study_program_intelligence.transform.pdf_numbers import split, tokens

REPO_ROOT = Path(__file__).resolve().parents[3]
DESTATIS = REPO_ROOT / "data" / "raw" / "destatis"
LFSTAT = REPO_ROOT / "data" / "raw" / "regional" / "by_studierende_ws2024.pdf"
OUT = REPO_ROOT / "data" / "interim" / "demand_split.csv"
REPORT = REPO_ROOT / "reports" / "demand_split.md"
SERIES = {  # name: (kind, subject codes)
    "Informatik": ("first-years", ["SF079"]),
    "cyber proxy": ("first-years", ["SF079", "SF123", "SF200"]),
    "robotics feeders": ("first-years", ["SF380", "SF123"]),
    "Informatik graduates": ("graduates", ["SF079"]),
}
NAT = {"NATD": "German", "NATA": "foreign"}


def _attr(d: pd.DataFrame, label: str) -> str:
    c = next(c for c in d.columns if c.endswith("variable_label") and (d[c] == label).any())
    return c.replace("variable_label", "variable_attribute_code")


def load() -> pd.DataFrame:
    """Long table: region, kind, subject code, year, nationality (German / foreign), value."""
    rows = []
    for kind, files in (("first-years", (("DE", "21311-0012_DE.csv"), ("BY", "21311-0015_BY.csv"))),
                        ("graduates", (("DE", "21321-0003_DE.csv"), ("BY", "21321-0006_BY.csv")))):
        for region, f in files:
            d = pd.read_csv(DESTATIS / f, sep=";", dtype=str)
            nat, ges, sf = _attr(d, "Nationalität"), _attr(d, "Geschlecht"), _attr(d, "Studienfach")
            d = d[d[nat].isin(NAT)]
            if kind == "first-years":
                d = d[d[ges].isna()]                                   # both sexes
            else:
                d = d[d[_attr(d, "Prüfungsergebnis")] == "PRUEFBESTJ"]  # passed exams; sexes are summed below
            rows.append(pd.DataFrame({"region": region, "kind": kind, "code": d[sf], "year": d["time"].str[:4].astype(int),
                                      "nationality": d[nat].map(NAT), "value": pd.to_numeric(d["value"], errors="coerce")}))
    return pd.concat(rows).groupby(["region", "kind", "code", "year", "nationality"], as_index=False)["value"].sum()


def cagr(a: float, b: float, years: int) -> float:
    return ((b / a) ** (1 / years) - 1) * 100 if a > 0 else float("nan")


def series_table(long: pd.DataFrame) -> pd.DataFrame:
    out = []
    for name, (kind, codes) in SERIES.items():
        y0, y1 = (2019, 2025) if kind == "graduates" else (2019, 2024)   # windows as in the base evidence
        for region in ("DE", "BY"):
            d = long[(long["kind"] == kind) & (long["region"] == region) & long["code"].isin(codes)]
            p = d.pivot_table(index="year", columns="nationality", values="value", aggfunc="sum")
            p["all"] = p["German"] + p["foreign"]
            g = p.loc[y1] - p.loc[y0]
            out.append({"series": name, "region": region, "window": f"{y0}-{y1}",
                        "German start": int(p.at[y0, "German"]), "foreign start": int(p.at[y0, "foreign"]),
                        "German end": int(p.at[y1, "German"]), "foreign end": int(p.at[y1, "foreign"]),
                        "all %/yr": round(cagr(p.at[y0, "all"], p.at[y1, "all"], y1 - y0), 1),
                        "German %/yr": round(cagr(p.at[y0, "German"], p.at[y1, "German"], y1 - y0), 1),
                        "foreign %/yr": round(cagr(p.at[y0, "foreign"], p.at[y1, "foreign"], y1 - y0), 1),
                        "foreign part of change %": int(round(100 * g["foreign"] / g["all"])) if g["all"] > 0 else "n/a (fell)",
                        "foreign share start %": int(round(100 * p.at[y0, "foreign"] / p.at[y0, "all"])),
                        "foreign share end %": int(round(100 * p.at[y1, "foreign"] / p.at[y1, "all"])),
                        "foreign share 2025 %": int(round(100 * p.at[2025, "foreign"] / p.at[2025, "all"]))})
    return pd.DataFrame(out)


def subjects_table(long: pd.DataFrame) -> pd.DataFrame:
    """All EMI-related subjects (first_look.SUBJECTS): growth 2019-2024, all vs German first-years."""
    out = []
    d = long[long["kind"] == "first-years"]
    for region in ("DE", "BY"):
        for code, name in SUBJECTS.items():
            p = d[(d["region"] == region) & (d["code"] == code)].pivot_table(index="year", columns="nationality", values="value", aggfunc="sum")
            if not {2019, 2024} <= set(p.index) or p.loc[[2019, 2024]].sum().sum() == 0:
                continue
            p["all"] = p.sum(axis=1)
            out.append({"region": region, "subject": name, "all 2024": int(p.at[2024, "all"]), "German 2024": int(p.at[2024, "German"]),
                        "all %/yr": round(cagr(p.at[2019, "all"], p.at[2024, "all"], 5), 1),
                        "German %/yr": round(cagr(p.at[2019, "German"], p.at[2024, "German"], 5), 1)})
    return pd.DataFrame(out).sort_values(["region", "all 2024"], ascending=[True, False])


def university_type() -> pd.DataFrame:
    """LfStat Tabelle 3.2: study area Informatik, German / foreign students and first-years by university type.
    The names page carries the combined row (i, w for total, 1st university semester, 1st subject semester); the
    facing page carries German and foreign (12 numbers) on the line that ends with the same row number. The split
    is fixed by the table's own arithmetic: German + foreign = combined, women <= all."""
    pages = [p.extract_text() or "" for p in pypdf.PdfReader(LFSTAT).pages]
    out = []
    for i, t in enumerate(pages):
        if "Tabelle 3.2" not in t:
            continue
        m = re.search(r"^(\d+) Informatik \.+\s*(.+)$", t, re.M)
        if not m:
            continue
        row, kind = m.group(1), ("universities of applied sciences" if "Fachhochschulen" in t else "universities")
        line = next(l for l in pages[i + 1].splitlines() if re.search(rf"\s{row}\s*$", l))
        ok = lambda v: all(v[k + 1] <= v[k] for k in range(0, len(v), 2))
        combined = split(tokens(m.group(2)), 6, ok)
        parts = split(tokens(line)[:-1], 12, ok)
        hits = [(c, p) for c, p in itertools.product(combined, parts) if all(p[k] + p[k + 6] == c[k] for k in range(6))]
        if len(hits) != 1:
            raise ValueError(f"Tabelle 3.2 row {row}: {len(hits)} consistent splits")
        c, p = hits[0]
        out.append({"university type": kind, "German 1st univ. sem.": p[2], "foreign 1st univ. sem.": p[8],
                    "foreign share 1st univ. sem. %": round(100 * p[8] / c[2]),
                    "German 1st subject sem.": p[4], "foreign 1st subject sem.": p[10],
                    "foreign share 1st subject sem. %": round(100 * p[10] / c[4])})
    return pd.DataFrame(out)


def _md(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    fmt = lambda v: "" if v is None or (isinstance(v, float) and pd.isna(v)) else (f"{v:,}" if isinstance(v, int) else str(v))
    return "\n".join(["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
                     + ["| " + " | ".join(fmt(v) for v in r) + " |" for r in df.itertuples(index=False)])


def main() -> None:
    long = load()
    ser, sub, uni = series_table(long), subjects_table(long), university_type()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    long.to_csv(OUT, index=False)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# Demand by nationality (generated)", "",
        "Destatis 21311-0012/-0015 (first-years, 1st university semester, winter semesters) and 21321-0003/-0006 "
        "(passed exams), German vs foreign nationality. Windows as in the base evidence: first-years 2019-2024 "
        "(2025 = Bavarian G9 gap year), graduates 2019-2025.", "",
        "## Series behind the demand trend scores", "", _md(ser), "",
        "## EMI-related subjects, first-years 2019-2024", "", _md(sub), "",
        "## Study area Informatik by university type, Bavaria WS 2024/25 (LfStat Tabelle 3.2)", "", _md(uni), ""]),
        encoding="utf-8")
    pd.set_option("display.width", 250)
    print(ser.to_string(index=False)); print(); print(uni.to_string(index=False))
    print(f"\nWritten: {OUT.relative_to(REPO_ROOT)}, {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
