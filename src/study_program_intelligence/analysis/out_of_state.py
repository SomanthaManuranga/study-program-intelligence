"""Students from outside Bavaria at OTH and the two cyber anchor universities (data-sufficiency audit, G4).

Run from the repository root:

    python -m study_program_intelligence.analysis.out_of_state

The capture model uses Bavarian school leavers only. This measures how many German students of OTH, TH Ingolstadt and
TH Deggendorf gained their school-leaving certificate outside Bavaria, so the size of that gap is known.
Data (cached): LfStat "Studierende an den Hochschulen in Bayern" WS 2024/25, Tabelle 4 (German students by state of
the certificate; per university only for a selection that includes OTH but not THI or TH Deggendorf) and Tabelle 5
(students of all nationalities with a Bavarian certificate, every state HAW); Destatis 21311-0002 (students by
university campus and nationality, WS 2024/25).
Exact share (OTH, all HAWs): Tabelle 4. Approximate share (OTH, THI, TH Deggendorf): 1 - Tabelle 5 / German students.
Tabelle 5 also counts foreigners with a Bavarian certificate, so the approximation is slightly too low; OTH, where both
exist, shows by how much.
Outputs: reports/out_of_state.md, data/interim/out_of_state.csv.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import pypdf

from study_program_intelligence.analysis.capture import TABLE5, table5
from study_program_intelligence.transform.pdf_numbers import split, tokens

REPO_ROOT = Path(__file__).resolve().parents[3]
DESTATIS = REPO_ROOT / "data" / "raw" / "destatis" / "21311-0002_HS.csv"
REPORT = REPO_ROOT / "reports" / "out_of_state.md"
OUT = REPO_ROOT / "data" / "interim" / "out_of_state.csv"
STATES = ["Bayern", "Baden-Württemberg", "Berlin", "Brandenburg", "Bremen", "Hamburg", "Hessen", "Mecklenburg-Vorpommern",
          "Niedersachsen", "Nordrhein-Westfalen", "Rheinland-Pfalz", "Saarland", "Sachsen", "Sachsen-Anhalt",
          "Schleswig-Holstein", "Thüringen", "Ausland"]
ROWS = {"OTH Amberg-Weiden": "OTH Amberg-Weiden", "Fachhochschulen zusammen": "all HAWs in Bavaria"}
DESTATIS_NAMES = {"OTH Amberg-Weiden": "Ostbayerische TH Amberg-Weiden", "TH Ingolstadt": "Technische H Ingolstadt",
                  "TH Deggendorf": "TH Deggendorf"}


def table4() -> pd.DataFrame:
    """German students by state of the school-leaving certificate (first page: total + 5 states; facing page: 12)."""
    pages = [p.extract_text() or "" for p in pypdf.PdfReader(TABLE5).pages]
    out = {}
    for i, t in enumerate(pages):
        if "Tabelle 4." not in t and "Tabelle 4." not in pages[min(i + 1, len(pages) - 1)]:
            continue
        for name, label in ROWS.items():
            m = re.search(rf"^(\d+)\s+{re.escape(name)} \.+\s*(.+)$", t, re.M)
            if not m or label in out:
                continue
            row = m.group(1)
            line = next((l for l in pages[i + 1].splitlines() if re.search(rf"\s{row}\s*$", l)), None)
            if line is None:
                continue
            left, right = tokens(m.group(2).replace("–", "-")), tokens(line.replace("–", "-"))[:-1]
            hits = [a + b for a in split(left, 6, lambda v: True) for b in split(right, 12, lambda v: True)
                    if a[0] == sum(a[1:]) + sum(b)]
            if len(hits) != 1:
                raise ValueError(f"Tabelle 4 {name}: {len(hits)} consistent splits")
            out[label] = dict(zip(["total", *STATES], hits[0]))
        if len(out) == len(ROWS):
            break
    return pd.DataFrame(out).T


def german_students() -> pd.Series:
    d = pd.read_csv(DESTATIS, sep=";", dtype=str)
    d = d[(d["time"].str[:4] == "2024") & (d["2_variable_attribute_code"] == "NATD") & d["3_variable_attribute_code"].isna()]
    d["v"] = pd.to_numeric(d["value"], errors="coerce")
    return pd.Series({k: d[d["4_variable_attribute_label"].str.startswith(v, na=False)]["v"].sum() for k, v in DESTATIS_NAMES.items()})


def main() -> None:
    t4, t5, ger = table4(), table5(), german_students()
    exact = pd.DataFrame({"German students": t4["total"], "certificate outside Bavaria": t4["total"] - t4["Bayern"],
                          "share outside Bavaria %": (100 * (t4["total"] - t4["Bayern"]) / t4["total"]).round(1),
                          "of which Sachsen + Thüringen": t4["Sachsen"] + t4["Thüringen"],
                          "of which Baden-Württemberg": t4["Baden-Württemberg"], "of which abroad": t4["Ausland"]})
    approx = pd.DataFrame({"German students (Destatis)": ger, "Bavarian certificate, all nationalities (Tabelle 5)": t5.loc[ger.index, "total"]})
    approx["approx. share outside Bavaria %"] = (100 * (1 - approx.iloc[:, 1] / approx.iloc[:, 0])).round(1)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.concat([exact.assign(method="exact (Tabelle 4)"), approx.assign(method="approx. (Tabelle 5 / Destatis)")]).to_csv(OUT)
    md = lambda df: "\n".join(["| | " + " | ".join(df.columns) + " |", "|" + "---|" * (len(df.columns) + 1)]
                              + [f"| {i} | " + " | ".join(f"{v:,.0f}" if isinstance(v, (int, float)) and abs(v) >= 100
                                                        else str(v) for v in r) + " |" for i, r in df.iterrows()])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# Students from outside Bavaria (generated)", "",
        "LfStat WS 2024/25 Tabelle 4 (exact, German students) and Tabelle 5 with Destatis 21311-0002 (approximate).", "",
        "## Exact: German students by state of the school-leaving certificate", "", md(exact), "",
        "## Approximate: OTH and the two cyber anchor universities", "", md(approx), "",
        "Tabelle 5 also counts foreigners with a Bavarian certificate, so the approximate share is slightly too low "
        "(OTH: compare with the exact value above).", ""]), encoding="utf-8")
    print(exact.to_string()); print(); print(approx.to_string())
    print(f"\nWritten: {REPORT.relative_to(REPO_ROOT)}, {OUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
