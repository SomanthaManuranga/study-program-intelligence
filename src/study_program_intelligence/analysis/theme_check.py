"""Hand-labelled check of the title keyword rules (analysis/themes.py).

Run from the repository root:

    python -m study_program_intelligence.analysis.theme_check sample [--force]

Writes data/interim/theme_labels.xlsx for labelling by hand. Universe: bachelor and
master offers in data/processed/programmes.csv, tagged by title match as in
analysis/first_look.py (supply counts).

Groups (decision log 2026-10-17)
- all_cyber: every programme whose title matches the cybersecurity rule (census,
  so the competitor count becomes exact).
- sample_robotics (10), sample_ai_data (10), sample_embedded_iot (5): random
  samples of title matches, for precision.
- miss_check (15, 5 per theme): programmes whose title matches none of
  cybersecurity/robotics/ai_data but whose content text matches one of them,
  to find specialised programmes the title rules miss.
Fixed seed (SEED) so the sheet can be rebuilt identically.

Label column is_theme_programme: y = a specialised programme of the theme in
column "theme" (main focus, or a named track/specialisation in the title);
n = not; ? = unsure.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd

from .themes import THEMES

REPO_ROOT = Path(__file__).resolve().parents[3]
PROGRAMMES = REPO_ROOT / "data" / "processed" / "programmes.csv"
SHEET = REPO_ROOT / "data" / "interim" / "theme_labels.xlsx"
SEED = 20261017
SAMPLES = {"robotics": 10, "ai_data": 10, "embedded_iot": 5}
MISS_THEMES = ("cybersecurity", "robotics", "ai_data")
MISS_PER_THEME = 5
COLUMNS = ["row_id", "group", "theme", "matched", "level", "title", "institution", "city",
           "km_oth", "content", "programme_id", "is_theme_programme", "note"]


def programmes() -> pd.DataFrame:
    p = pd.read_csv(PROGRAMMES, dtype={"programme_id": str})
    p = p[p["degree"].isin(["Bachelor/Bakkalaureus", "Master"])].copy()
    p["level"] = p["study_type_id"].map({0: "BA", 1: "MA"})
    p["content"] = p["content"].fillna("")
    return p.sort_values("programme_id").reset_index(drop=True)


def _match(text: str, theme: str) -> str:
    m = re.search(THEMES[theme], text.lower())
    return m.group(0) if m else ""


def _rows(d: pd.DataFrame, group: str, theme: str, field: str) -> pd.DataFrame:
    d = d.copy()
    d["group"], d["theme"] = group, theme
    d["matched"] = d[field].map(lambda s: _match(s, theme))
    return d


def build(p: pd.DataFrame) -> pd.DataFrame:
    title, content = p["title"].str.lower(), p["content"].str.lower()
    hit = {t: title.str.contains(THEMES[t], regex=True) for t in THEMES}
    parts = [_rows(p[hit["cybersecurity"]], "all_cyber", "cybersecurity", "title")]
    for theme, n in SAMPLES.items():
        parts.append(_rows(p[hit[theme]].sample(n, random_state=SEED), f"sample_{theme}", theme, "title"))
    no_title = ~pd.concat([hit[t] for t in MISS_THEMES], axis=1).any(axis=1)
    taken: set[str] = set()
    for theme in MISS_THEMES:
        pool = p[no_title & content.str.contains(THEMES[theme], regex=True) & ~p["programme_id"].isin(taken)]
        s = pool.sample(MISS_PER_THEME, random_state=SEED)
        taken.update(s["programme_id"])
        parts.append(_rows(s, "miss_check", theme, "content"))
    out = pd.concat(parts, ignore_index=True)
    out["row_id"] = range(1, len(out) + 1)
    out["km_oth"] = out["km_oth"].round(0)
    out["is_theme_programme"], out["note"] = "", ""
    return out[COLUMNS]


INSTRUCTIONS = [
    "Fill column is_theme_programme on sheet 'labels' for every row: y, n or ?. Do not change other columns.",
    "Question for every row: is this a SPECIALISED programme of the theme in column 'theme'?",
    "y = the theme is the main focus, or a named track/specialisation in the title (e.g. 'Informatik - Cyber Security').",
    "n = the theme is only one topic among many, or the keyword means something else (e.g. 'Food Security').",
    "? = cannot decide from title and content; write why in 'note'. Open the programme page only if needed.",
    "Groups: all_cyber = every title match for cybersecurity (exact competitor count).",
    "sample_* = random title matches (precision). miss_check = title does NOT match, content does: y means the rule missed it.",
    "Column 'matched' shows the keyword that triggered the row (in the title, or in the content for miss_check).",
    "Content is the short Studiensuche teaser (max ~400 characters), not the full description.",
    "Save as .xlsx under the same name. Tell Claude when done; scoring: theme_check score (next part of Step 38).",
]


def write(df: pd.DataFrame, path: Path) -> None:
    from openpyxl.styles import Alignment, Font
    from openpyxl.worksheet.datavalidation import DataValidation

    path.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        df.to_excel(xw, sheet_name="labels", index=False)
        pd.DataFrame({"instructions": INSTRUCTIONS}).to_excel(xw, sheet_name="instructions", index=False)
        ws = xw.sheets["labels"]
        widths = {"A": 7, "B": 18, "C": 15, "D": 18, "E": 6, "F": 50, "G": 35, "H": 15, "I": 8,
                  "J": 70, "K": 12, "L": 18, "M": 35}
        for col, w in widths.items():
            ws.column_dimensions[col].width = w
        for cell in ws[1]:
            cell.font = Font(bold=True)
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical="top")
        ws.freeze_panes = "B2"
        ws.auto_filter.ref = ws.dimensions
        dv = DataValidation(type="list", formula1='"y,n,?"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"L2:L{len(df) + 1}")
        xw.sheets["instructions"].column_dimensions["A"].width = 130


def main(argv: list[str]) -> None:
    if not argv or argv[0] != "sample":
        sys.exit("Usage: python -m study_program_intelligence.analysis.theme_check sample [--force]")
    if SHEET.exists() and "--force" not in argv:
        sys.exit(f"{SHEET.relative_to(REPO_ROOT)} exists (may hold labels); use --force to overwrite")
    df = build(programmes())
    write(df, SHEET)
    print(f"Written: {SHEET.relative_to(REPO_ROOT)} ({len(df)} rows)")
    print(df.groupby(["group", "theme"]).size().to_string())


if __name__ == "__main__":
    main(sys.argv[1:])
