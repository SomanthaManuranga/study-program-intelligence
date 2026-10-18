"""A written verdict for every theme group with the two funnel filters (data-sufficiency audit, G5).

Run from the repository root:

    python -m study_program_intelligence.analysis.theme_verdicts

The original screening (Step 36, docs/evidence_funnel.md) gave verdicts for 9 theme groups; 5 further themes in
analysis/themes.py and the sub-themes data science, health/medical informatics and energy informatics had none. This
applies the same two filters to all of them, with thresholds written out here (they were not written as numbers
before) and checked against the original decisions:
  1 demand trend: drop if the feeder subjects' first-years fell by more than 3 % a year in BOTH Germany (2019-2025)
    and Bavaria (2019-2024). A small base (fewer than 500 first-years in Germany 2025) goes to the watch list.
  2 supply gap (per level): pass if at most 3 titled offers within 100 km of OTH AND none at OTH.
Feeder trends are shown for all first-years (the filter) and for German first-years (information only; audit G1).
Supply: title keyword rules (themes.py; sub-themes below), BA Studiensuche catalogue (data/processed/programmes.csv).
Outputs: reports/theme_verdicts.md, data/interim/theme_verdicts.csv.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from study_program_intelligence.analysis.themes import THEMES

REPO_ROOT = Path(__file__).resolve().parents[3]
DESTATIS = REPO_ROOT / "data" / "raw" / "destatis"
PROGRAMMES = REPO_ROOT / "data" / "processed" / "programmes.csv"
REPORT = REPO_ROOT / "reports" / "theme_verdicts.md"
OUT = REPO_ROOT / "data" / "interim" / "theme_verdicts.csv"
FALL_LIMIT, SMALL_BASE, THIN_100KM = -3.0, 500, 3
SUBTHEMES = {
    "data_science": r"data science|data analytics|data engineering|big data|datenwissenschaft",
    "health_informatics": r"medizininformatik|medizinische informatik|gesundheitsinformatik|health informatics|medical informatics|digital health",
    "energy_informatics": r"energieinformatik|energy informatics|smart grid",
}
FEEDERS = {  # Destatis 21311 subject codes behind each theme
    "ai_data": ["SF079", "SF312"], "data_science": ["SF312", "SF079"],
    "cybersecurity": ["SF079", "SF123", "SF200"], "embedded_iot": ["SF123", "SF200"], "robotics": ["SF380", "SF123"],
    "automation_i40": ["SF380", "SF048"], "energy_emobility": ["SF310", "SF316", "SF211"], "energy_informatics": ["SF310", "SF079"],
    "microelectronics": ["SF157"], "medtech_health": ["SF247", "SF215", "SF232"], "health_informatics": ["SF247"],
    "games_xr": ["SF121", "SF305", "SF287"], "media_tech": ["SF305", "SF121"], "software_eng": ["SF079"],
    "quantum": ["SF128"], "aerospace": ["SF057"], "sustainability": ["SF457", "SF458"], "mobility_vehicle": ["SF235", "SF089"],
}
ORIGINAL = {  # verdicts of the original funnel (docs/evidence_funnel.md), per theme and level
    ("ai_data", "BA"): "drop (supply)", ("ai_data", "MA"): "drop (supply)",
    ("cybersecurity", "BA"): "candidate", ("cybersecurity", "MA"): "candidate",
    ("embedded_iot", "BA"): "not carried", ("embedded_iot", "MA"): "candidate",
    ("robotics", "BA"): "candidate", ("robotics", "MA"): "not carried",
    ("automation_i40", "BA"): "drop (at OTH)", ("automation_i40", "MA"): "drop (at OTH)",
    ("energy_emobility", "BA"): "drop (at OTH)", ("energy_emobility", "MA"): "drop (at OTH)",
    ("medtech_health", "BA"): "drop (at OTH)", ("medtech_health", "MA"): "drop (at OTH)",
    ("microelectronics", "BA"): "watch list", ("microelectronics", "MA"): "watch list",
    ("games_xr", "BA"): "drop (demand)", ("games_xr", "MA"): "drop (demand)",
    ("media_tech", "BA"): "drop (demand)", ("media_tech", "MA"): "drop (demand)",
}


NOTES = {  # candidates by the written rule that the original funnel did not carry: what the next stage would face
    ("embedded_iot", "BA"): "kill rule 1 likely: embedded systems are core content of OTH's E&IT and Industrie-4.0-Informatik "
                            "bachelors; only 5 titled bachelors in Germany (no established market)",
    ("robotics", "MA"): "kill rule 1 likely: robotics and ML for robotics are taught in OTH's KI programmes and the IT und "
                        "Automation master; the bachelor variant was carried instead",
    ("software_eng", "BA"): "kill rule 1 likely: software engineering is the core of OTH's informatics bachelors "
                            "(Industrie-4.0-Informatik, Medieninformatik); no Destatis subject of its own (feeder = Informatik)",
    ("software_eng", "MA"): "kill rule 1 likely, as for the bachelor",
    ("quantum", "BA"): "outside EMI's subjects (feeder = Physik, falling in Germany); 2 titled bachelors in Germany",
    ("quantum", "MA"): "outside EMI's subjects (feeder = Physik); research-led master, no EMI staff base",
    ("aerospace", "BA"): "outside EMI's subjects (feeder = Luft- und Raumfahrttechnik, a mechanical-engineering field)",
    ("aerospace", "MA"): "outside EMI's subjects, as for the bachelor",
    ("health_informatics", "BA"): "small base: 600 first-years in Germany 2025 and German first-years -5.3 %/yr; overlap with "
                                  "OTH's Medizintechnik (bachelor, master) and Medical Engineering not tested; would score low on demand",
    ("health_informatics", "MA"): "as for the bachelor; 14 titled masters in Germany",
    ("energy_informatics", "BA"): "no titled programme in Germany: no market evidence; feeder trend is Informatik's",
    ("energy_informatics", "MA"): "no titled programme in Germany: no market evidence",
}


def _first_years(file: str) -> pd.DataFrame:
    d = pd.read_csv(DESTATIS / file, sep=";", dtype=str)
    d = d[d["3_variable_attribute_code"].isna()].copy()
    d["year"] = d["time"].str[:4].astype(int)
    d["nat"] = d["2_variable_attribute_code"].fillna("all")
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d.rename(columns={"4_variable_attribute_code": "sf"})[["year", "sf", "nat", "value"]]


def _cagr(s: pd.Series, a: int, z: int) -> float:
    return round(((s[z] / s[a]) ** (1 / (z - a)) - 1) * 100, 1) if s.get(a, 0) > 0 and s.get(z, 0) > 0 else np.nan


def trends() -> pd.DataFrame:
    de, by = _first_years("21311-0012_DE.csv"), _first_years("21311-0015_BY.csv")
    rows = []
    for theme, codes in FEEDERS.items():
        s = lambda d, nat: d[d["sf"].isin(codes) & (d["nat"] == nat)].groupby("year")["value"].sum()
        rows.append({"theme": theme, "feeder first-years DE 2025": int(s(de, "all").get(2025, 0)),
                     "DE %/yr 2019-25": _cagr(s(de, "all"), 2019, 2025), "BY %/yr 2019-24": _cagr(s(by, "all"), 2019, 2024),
                     "German only DE %/yr": _cagr(s(de, "NATD"), 2019, 2025), "German only BY %/yr": _cagr(s(by, "NATD"), 2019, 2024)})
    return pd.DataFrame(rows).set_index("theme")


def supply() -> pd.DataFrame:
    p = pd.read_csv(PROGRAMMES, dtype={"programme_id": str})
    p = p[p["degree"].isin(["Bachelor/Bakkalaureus", "Master"])].copy()
    p["level"] = p["study_type_id"].map({0: "BA", 1: "MA"})
    title = p["title"].str.lower()
    rows = []
    for theme, pattern in {**THEMES, **SUBTHEMES}.items():
        hit = title.str.contains(pattern, regex=True)
        for level in ("BA", "MA"):
            s = p[hit & (p["level"] == level)]
            rows.append({"theme": theme, "level": level, "Germany": len(s), "<=100 km": int((s["km_oth"] <= 100).sum()),
                         "<=150 km": int((s["km_oth"] <= 150).sum()), "at OTH": int(s["is_oth"].sum())})
    return pd.DataFrame(rows)


def verdicts() -> pd.DataFrame:
    t, s = trends(), supply()
    d = s.join(t, on="theme")
    fell = (d["DE %/yr 2019-25"] < FALL_LIMIT) & (d["BY %/yr 2019-24"] < FALL_LIMIT)
    small = d["feeder first-years DE 2025"] < SMALL_BASE
    thin = (d["<=100 km"] <= THIN_100KM) & (d["at OTH"] == 0)
    d["filter 1 (trend)"] = np.where(fell, "fail", np.where(small, "watch list", "pass"))
    d["filter 2 (supply gap)"] = np.where(d["at OTH"] > 0, "fail (at OTH)", np.where(thin, "pass", "fail (crowded)"))
    d["verdict"] = np.select([fell, small, d["at OTH"] > 0, ~thin],
                             ["drop (demand)", "watch list", "drop (at OTH)", "drop (supply)"], "candidate")
    d["original verdict"] = [ORIGINAL.get((a, b), "not screened") for a, b in zip(d["theme"], d["level"])]
    d["agrees"] = [("new" if o == "not screened" else "yes" if v == o else
                    "yes (dropped by the other filter)" if v.startswith("drop") and o.startswith("drop") else "no")
                   for v, o in zip(d["verdict"], d["original verdict"])]
    d["next stage (title-level judgement, not tested)"] = [NOTES.get((a, b), "") if v == "candidate" and o != "candidate" else ""
                                                          for a, b, v, o in zip(d["theme"], d["level"], d["verdict"], d["original verdict"])]
    return d


def main() -> None:
    d = verdicts()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUT, index=False)
    cols = ["theme", "level", "Germany", "<=100 km", "at OTH", "feeder first-years DE 2025", "DE %/yr 2019-25", "BY %/yr 2019-24",
            "German only DE %/yr", "German only BY %/yr", "filter 1 (trend)", "filter 2 (supply gap)", "verdict",
            "original verdict", "agrees", "next stage (title-level judgement, not tested)"]
    fmt = lambda v: "" if isinstance(v, float) and np.isnan(v) else (f"{v:,}" if isinstance(v, (int, np.integer)) else str(v))
    md = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)] + \
         ["| " + " | ".join(fmt(r[c]) for c in cols) + " |" for _, r in d.iterrows()]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# Verdict for every theme group (generated)", "",
        f"Filter 1: drop if feeder first-years fell by more than {-FALL_LIMIT:.0f} % a year in both Germany (2019-25) and "
        f"Bavaria (2019-24); fewer than {SMALL_BASE} feeder first-years in Germany 2025 = watch list. Filter 2: pass if at most "
        f"{THIN_100KM} titled offers within 100 km of OTH and none at OTH. German-only trends are information only.", "",
        *md, "",
        "Counts: " + ", ".join(f"{k} {v}" for k, v in d["verdict"].value_counts().items()) + ".", ""]), encoding="utf-8")
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 30)
    print(d[cols].to_string(index=False))
    print(f"\nWritten: {REPORT.relative_to(REPO_ROOT)}, {OUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
