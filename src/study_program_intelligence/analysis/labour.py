"""Regional labour market for IT occupations (Claim D: outlet), Step 43.

Run from the repository root:

    python -m study_program_intelligence.analysis.labour employment

Sources (configs/labour_documents.yaml): Bayerisches Landesamt für Statistik, Statistische Berichte A VI 5 - Teil 1
"Sozialversicherungspflichtig Beschäftigte in Bayern", 30.06.2019 and 30.06.2023 (BA employment statistics).
- Tabelle 9: employees at place of WORK by county and economic section; section J "Information und Kommunikation"
  is the regional proxy for the ICT sector. The table is split over facing pages (left: key, name, total, A, B-F;
  right: services G-U and its sections). Rows are matched by order and checked: services = sum of its sections,
  total = A + (B-F) + services, counties sum to their Regierungsbezirk.
- Tabelle 10: employees at place of RESIDENCE in Bavaria by occupation (KldB 2010) and qualification; occupation
  main group 43 "Informatik-, Informations- und Kommunikationstechnologieberufe" (no county breakdown available).
Occupation x county data exist only at the BA statistics portal, whose download forms (/SiteGlobals/) are
disallowed for robots: listed in docs/manual_downloads.md.
Outputs: data/interim/ict_sector_by_county.csv, reports/labour.md.
"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path

import pandas as pd
import pypdf

from ..transform.pdf_numbers import split, tokens
from .catchment import counties

REPO_ROOT = Path(__file__).resolve().parents[3]
RAW = REPO_ROOT / "data" / "raw" / "labour"
OUT = REPO_ROOT / "data" / "interim" / "ict_sector_by_county.csv"
REPORT = REPO_ROOT / "reports" / "labour.md"
YEARS = (2019, 2023)
RIGHT = ["services", "G-I", "J", "K", "L", "M-N", "O-Q", "R-U"]


def _pages(r: pypdf.PdfReader) -> list[tuple[int, int]]:
    """(left, right) page pairs of Tabelle 9: left has sections A/B-F, right has G-I/J."""
    out = []
    for i in range(len(r.pages) - 1):
        a = r.pages[i].extract_text() or ""
        b = r.pages[i + 1].extract_text() or ""
        if "Regionale Gliederung" in a and "(B-F)" in a and "(J)" in b and "Wirtschaftsabschnitten" in a + b:
            out.append((i, i + 1))
    return out


def table9(year: int) -> pd.DataFrame:
    logging.disable(logging.WARNING)
    r = pypdf.PdfReader(RAW / f"by_svb_{year}.pdf")
    rows = []
    for li, ri in _pages(r):
        left = (r.pages[li].extract_text(extraction_mode="layout") or "").splitlines()
        right = (r.pages[ri].extract_text(extraction_mode="layout") or "").splitlines()
        keys = []
        for line in left:
            m = re.match(r"^\s*(\d{1,3})?\s*([^\d|]+?)\s*\.*\s*\bi\b\s+([\d\s\-]+)$", line)
            if m and re.search(r"\d", m.group(3)):
                keys.append((m.group(1) or "", m.group(2).strip(" .…"), m.group(3)))
        nums = [l for l in right if l.strip() and re.fullmatch(r"[\d\s\-]+", l.strip())]
        i_rows = nums[0::2]  # right page alternates i (insgesamt) and w (weiblich) rows
        if len(i_rows) != len(keys):
            raise ValueError(f"{year} p{li + 1}/{ri + 1}: {len(keys)} left rows vs {len(i_rows)} right rows")
        for (key, name, lnum), rline in zip(keys, i_rows):
            t = tokens(rline)
            if key and t and t[-1] == key:
                t = t[:-1]  # trailing region key on the right page
            opts_r = split(t, len(RIGHT), lambda g: g[0] == sum(g[1:]))
            # left: total, A, B-F, B-E, C, F with B-F = B-E + F and C <= B-E <= total
            opts_l = split(tokens(lnum), 6, lambda g: g[2] == g[3] + g[5] and g[4] <= g[3] <= g[0])
            pick = [(lft, rt) for rt in opts_r for lft in opts_l if lft[0] == lft[1] + lft[2] + rt[0] and lft[2] == lft[3] + lft[5]]
            if not pick:
                raise ValueError(f"{year}: cannot split row {name!r}")
            lft, rt = pick[0]
            rows.append({"key": key, "name": name, "total": lft[0], "A": lft[1], "B-F": lft[2], **dict(zip(RIGHT, rt))})
    d = pd.DataFrame(rows)
    d["year"] = year
    return d


def assign_keys(d: pd.DataFrame) -> pd.DataFrame:
    """County keys: '09' + 3 digits; Bezirk rows: single digit; check counties sum to their Bezirk."""
    d = d.copy()
    d["county"] = d["key"].map(lambda k: f"09{k}" if len(k) == 3 else (f"09{k}" if len(k) == 1 else "09"))
    cty, bez = d[d["key"].str.len() == 3], d[d["key"].str.len() == 1]
    for b in bez.itertuples():
        s = cty[cty["key"].str[0] == b.key][["total", "J"]].sum()
        if not (s["total"] == b.total and s["J"] == b.J):
            raise ValueError(f"{b.year}: counties do not sum to Bezirk {b.key}")
    return d


def table10_row43(year: int) -> dict:
    logging.disable(logging.WARNING)
    r = pypdf.PdfReader(RAW / f"by_svb_{year}.pdf")
    for p in r.pages:
        t = p.extract_text(extraction_mode="layout") or ""
        if "beruflicher Gliederung" in t and "Ausbildungsabschl" in t:
            m = re.search(r"^\s*43\s+Informatik.*?\.{3,}\s*([\d\s]+)$", t, re.M)
            if m:
                opts = split(tokens(m.group(1)), 5, lambda g: g[1] == g[2] + g[3] and g[0] >= g[1])
                total, qual, voc, acad, other = opts[0]
                return {"year": year, "IT occupations (KldB 43)": total, "with vocational degree": voc,
                        "with academic degree": acad}
    raise ValueError(f"{year}: row 43 not found")


def _md(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(f"{v:,}" if isinstance(v, int) else str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(out)


def employment() -> str:
    geo = counties()
    d = pd.concat([assign_keys(table9(y)) for y in YEARS], ignore_index=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUT, index=False)
    c = d[d["key"].str.len() == 3].merge(geo, on="county", how="left")
    groups = {"Own pool (Step 42)": c["own_pool"], "<= 50 km": c["km_OTH"] <= 50, "<= 100 km": c["km_OTH"] <= 100,
              "Bavaria": pd.Series(True, index=c.index)}
    rows = []
    for name, mask in groups.items():
        a = c[mask & (c["year"] == YEARS[0])][["total", "J"]].sum()
        z = c[mask & (c["year"] == YEARS[1])][["total", "J"]].sum()
        rows.append({"area (place of work)": name, f"ICT sector (J) {YEARS[0]}": int(a["J"]), f"ICT sector (J) {YEARS[1]}": int(z["J"]),
                     "change %": round((z["J"] / a["J"] - 1) * 100, 1), f"all employees change %": round((z["total"] / a["total"] - 1) * 100, 1),
                     f"J share of employment {YEARS[1]} %": round(z["J"] / z["total"] * 100, 2)})
    reg = pd.DataFrame(rows)
    top = c[(c["year"] == YEARS[1]) & (c["km_OTH"] <= 100)].sort_values("J", ascending=False)
    top = top.assign(share=(top["J"] / top["total"] * 100).round(1))[["county_name", "km_OTH", "J", "share"]].head(10)
    top["km_OTH"] = top["km_OTH"].round(0).astype(int)
    occ = pd.DataFrame([table10_row43(y) for y in YEARS])
    occ.loc[len(occ)] = ["change %", *[round((occ.iloc[1, k] / occ.iloc[0, k] - 1) * 100, 1) for k in range(1, 4)]]
    return "\n".join([
        "# Regional labour market: ICT sector and IT occupations (generated)", "",
        "Source: Statistische Berichte A VI 5 - Teil 1 (30.06.2019, 30.06.2023), Tabellen 9 and 10. "
        "Counties checked against their Regierungsbezirk.", "",
        "## ICT sector (WZ section J) employment by area", "", _md(reg), "",
        f"## Counties within 100 km with most ICT-sector jobs ({YEARS[1]})", "",
        _md(top.rename(columns={"county_name": "county", "km_OTH": "km to OTH", "J": "ICT sector jobs", "share": "share of employment %"})), "",
        "## IT occupations (KldB 2010 main group 43), Bavaria, place of residence", "", _md(occ), ""])


def main(argv: list[str]) -> None:
    if argv[:1] != ["employment"]:
        sys.exit("Usage: python -m study_program_intelligence.analysis.labour employment")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(employment(), encoding="utf-8")
    print(f"Written: {REPORT.relative_to(REPO_ROOT)}, {OUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1:])
