"""First look: demand (GENESIS first-year students) and supply (programme catalogue).

Run from the repository root after the ingest and transform steps:

    python -m study_program_intelligence.analysis.first_look

Writes reports/first_look.md (tables only; interpretation lives in docs/evidence_*.md).

Notes
- GENESIS first-year students = 1st university semester, winter semesters only.
- Bavaria 2025 is the G9 transition year (half a cohort of school leavers), so Bavarian
  trends end in 2024.
- Supply counts use title keyword rules (analysis/themes.py): a programme counts as
  specialised in a theme only if its title matches.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .themes import THEMES

REPO_ROOT = Path(__file__).resolve().parents[3]
DESTATIS = REPO_ROOT / "data" / "raw" / "destatis"
PROCESSED = REPO_ROOT / "data" / "processed"
REPORT = REPO_ROOT / "reports" / "first_look.md"

SUBJECTS = {  # Destatis Studienfach codes relevant to EMI
    "SF079": "Informatik", "SF277": "Wirtschaftsinformatik", "SF048": "Elektrotechnik/Elektronik",
    "SF380": "Mechatronik", "SF123": "Ingenieurinformatik/Technische Informatik", "SF121": "Medieninformatik",
    "SF222": "Kommunikations- und Informationstechnik", "SF200": "Computer- und Kommunikationstechniken",
    "SF305": "Medientechnik", "SF310": "Regenerative Energien", "SF247": "Medizinische Informatik",
    "SF286": "Mikrosystemtechnik", "SF287": "Neue Medien", "SF157": "Mikroelektronik",
}


def _entrants(file: str) -> pd.DataFrame:
    d = pd.read_csv(DESTATIS / file, sep=";", dtype=str)
    d = d[d["2_variable_attribute_code"].isna() & d["3_variable_attribute_code"].isna()].copy()  # all nationalities, both sexes
    d["year"] = d["time"].str[:4].astype(int)
    d["value"] = pd.to_numeric(d["value"], errors="coerce")  # "-" = none/unknown -> NaN
    return d.rename(columns={"4_variable_attribute_code": "sf"})[["year", "sf", "value"]]


def _cagr(s: pd.Series, a: int, z: int) -> float:
    if a in s and z in s and s[a] and s[z] and s[a] > 0:
        return round(((s[z] / s[a]) ** (1 / (z - a)) - 1) * 100, 1)
    return np.nan


def demand_table() -> pd.DataFrame:
    de, by = _entrants("21311-0012_DE.csv"), _entrants("21311-0015_BY.csv")
    tot_de, tot_by = de.groupby("year")["value"].sum(), by.groupby("year")["value"].sum()
    rows = [{"code": "ALL", "subject": "All subjects",
             "DE 2015": tot_de[2015], "DE 2019": tot_de[2019], "DE 2025": tot_de[2025],
             "DE CAGR 2019-25 %": _cagr(tot_de, 2019, 2025), "DE share 2025 %": 100.0,
             "BY 2019": tot_by[2019], "BY 2024": tot_by[2024], "BY CAGR 2019-24 %": _cagr(tot_by, 2019, 2024)}]
    for code, name in SUBJECTS.items():
        s = de[de.sf == code].set_index("year")["value"]
        b = by[by.sf == code].set_index("year")["value"]
        rows.append({"code": code, "subject": name,
                     "DE 2015": s.get(2015), "DE 2019": s.get(2019), "DE 2025": s.get(2025),
                     "DE CAGR 2019-25 %": _cagr(s, 2019, 2025),
                     "DE share 2025 %": round(s.get(2025, np.nan) / tot_de[2025] * 100, 2),
                     "BY 2019": b.get(2019), "BY 2024": b.get(2024), "BY CAGR 2019-24 %": _cagr(b, 2019, 2024)})
    return pd.DataFrame(rows)


def supply_table() -> pd.DataFrame:
    p = pd.read_csv(PROCESSED / "programmes.csv", dtype={"programme_id": str})
    p = p[p["degree"].isin(["Bachelor/Bakkalaureus", "Master"])].copy()
    p["level"] = p["study_type_id"].map({0: "BA", 1: "MA"})
    title = p["title"].str.lower()
    rows = []
    for theme, pattern in THEMES.items():
        hit = title.str.contains(pattern, regex=True)
        for level in ("BA", "MA"):
            s = p[hit & (p["level"] == level)]
            near = s[s["km_oth"] <= 150].sort_values("km_oth").drop_duplicates("institution")
            rows.append({"theme": theme, "level": level, "Germany": len(s),
                         "Bavaria": int((s["state"] == "Bayern").sum()),
                         "<=100 km": int((s["km_oth"] <= 100).sum()), "<=150 km": int((s["km_oth"] <= 150).sum()),
                         "HAW %": round((s["institution_type_id"] == 106).mean() * 100) if len(s) else 0,
                         "dual %": round(s["is_dual"].mean() * 100) if len(s) else 0,
                         "OTH offers": int(s["is_oth"].sum()),
                         "nearest competitors": "; ".join(f"{r.institution} ({r.km_oth:.0f} km)"
                                                          for r in near[~near["is_oth"]].head(3).itertuples()) or "none <=150 km"})
    return pd.DataFrame(rows)


def _md(df: pd.DataFrame) -> str:
    """Markdown table without extra dependencies."""
    def fmt(v):
        if isinstance(v, float):
            return "" if np.isnan(v) else (f"{v:,.0f}" if v.is_integer() and abs(v) >= 100 else f"{v:,.1f}")
        return str(v)
    head = "| " + " | ".join(df.columns) + " |\n| " + " | ".join("---" for _ in df.columns) + " |\n"
    return head + "\n".join("| " + " | ".join(fmt(v) for v in row) + " |" for row in df.itertuples(index=False))


def main() -> int:
    demand, supply = demand_table(), supply_table()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "# First look: demand and supply tables\n\n"
        "Generated by `python -m study_program_intelligence.analysis.first_look`.\n\n"
        "## Demand: first-year students (1st university semester, winter semesters)\n\n"
        + _md(demand) +
        "\n\n## Supply: specialised programmes by theme (title match)\n\n"
        + _md(supply) + "\n",
        encoding="utf-8",
    )
    print(demand.to_string(index=False))
    print()
    print(supply.drop(columns=["nearest competitors"]).to_string(index=False))
    print(f"\nWritten: {REPORT.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
