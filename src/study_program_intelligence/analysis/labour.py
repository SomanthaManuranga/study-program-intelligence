"""IT occupations in Bavaria (Claim D: outlet), Step 43.

Run from the repository root:

    python -m study_program_intelligence.analysis.labour

Source (configs/labour_documents.yaml): Bayerisches Landesamt für Statistik, Statistische Berichte A VI 5 - Teil 1
"Sozialversicherungspflichtig Beschäftigte in Bayern", 30.06.2019 and 30.06.2023 (BA employment statistics),
Tabelle 10: employees at place of residence by occupation (KldB 2010) and qualification; main group 43
"Informatik-, Informations- und Kommunikationstechnologieberufe".

Limitations (decision log, Step 43): no county breakdown. Tabelle 9 (ICT sector J by county) is split over facing
pages and could not be parsed reliably (two attempts, both timed out); the BA occupation-by-county tables are only
behind download forms that robots.txt disallows (/SiteGlobals/) and are skipped by decision.
Output: reports/labour.md
"""

from __future__ import annotations

import logging
import re
from pathlib import Path

import pandas as pd
import pypdf

from ..transform.pdf_numbers import split, tokens

REPO_ROOT = Path(__file__).resolve().parents[3]
RAW = REPO_ROOT / "data" / "raw" / "labour"
REPORT = REPO_ROOT / "reports" / "labour.md"
YEARS = (2019, 2023)


def row43(year: int) -> dict:
    logging.disable(logging.WARNING)
    r = pypdf.PdfReader(RAW / f"by_svb_{year}.pdf")
    for p in r.pages:
        if "beruflicher Gliederung" not in (p.extract_text() or ""):
            continue
        t = p.extract_text(extraction_mode="layout") or ""
        m = re.search(r"^\s*43\s+Informatik.*?\.{3,}\s*([\d\s]+)$", t, re.M)
        if m:  # columns: total, with vocational qualification (together, recognised vocational, academic), last column
            opts = split(tokens(m.group(1)), 5, lambda g: g[1] == g[2] + g[3] and g[0] >= g[1], max_cuts=1)
            total, _, voc, acad, _ = opts[0]
            return {"date": f"30.06.{year}", "IT occupations (KldB 43)": total, "with vocational degree": voc,
                    "with academic degree": acad, "academic share %": round(acad / total * 100, 1)}
    raise ValueError(f"{year}: row 43 not found")


def main() -> None:
    occ = pd.DataFrame([row43(y) for y in YEARS])
    chg = {"date": "change %", **{c: round((occ.at[1, c] / occ.at[0, c] - 1) * 100, 1) for c in occ.columns[1:4]}, "academic share %": ""}
    occ = pd.concat([occ, pd.DataFrame([chg])], ignore_index=True)
    lines = ["| " + " | ".join(occ.columns) + " |", "|" + "---|" * len(occ.columns)]
    fmt = lambda v: f"{int(v):,}" if isinstance(v, (int, float)) and float(v).is_integer() else str(v)
    lines += ["| " + " | ".join(fmt(v) for v in r) + " |" for r in occ.itertuples(index=False)]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(["# IT occupations in Bavaria (generated)", "",
                                 "Source: Statistische Berichte A VI 5 - Teil 1, Tabelle 10 (place of residence).", "", *lines, ""]),
                      encoding="utf-8")
    print(occ.to_string(index=False))
    print(f"Written: {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
