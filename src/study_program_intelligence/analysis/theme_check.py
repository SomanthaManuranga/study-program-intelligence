"""Hand-labelled check of the title keyword rules (analysis/themes.py).

Run from the repository root:

    python -m study_program_intelligence.analysis.theme_check sample [--force]
    python -m study_program_intelligence.analysis.theme_check score

sample writes data/interim/theme_labels.xlsx for labelling by hand. score reads the
labels (data/interim/theme_labels_EN.xlsx, joined on row_id) and writes
reports/theme_check.md: precision, miss check, distinct dedicated cybersecurity
programmes, and secondary competitors (focus areas). Universe: bachelor and
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

Secondary competitors: general programmes (title does not match the theme) whose
"Schwerpunkte" list in the Studiensuche content names the theme. Variants of one
programme (same institution, level and title apart from study-form words) count once.
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

LABELS = REPO_ROOT / "data" / "interim" / "theme_labels_EN.xlsx"
REPORT = REPO_ROOT / "reports" / "theme_check.md"
NEAR_KM = 150
# Offers that are one programme (programme_id groups); first id is kept.
DUPLICATES = [
    ("123198697", "123198698"),  # HS Niederrhein Cyber Security Management B.Sc., Teilzeit / Vollzeit
    ("123198699", "173090189"),  # HS Niederrhein Cyber Security Management M.Sc., Teilzeit / Vollzeit
    ("102600135", "124684153"),  # IT-Sicherheit (Online-Studiengang) B.Sc., shared: TH Brandenburg / Ostfalia
]
# Theme words in focus areas that mean something else.
FOCUS_EXCLUDE = {"cybersecurity": r"security printing"}
AI_ONLY = r"künstliche intelligenz|artificial intelligence|\bki\b|\bai\b|machine learning|maschinelles lernen|deep learning"
FORM_WORDS = (r"\b(in teilzeit|teilzeit|vollzeit|dual(e|es)?|berufsbegleitend|ausbildungsintegrierend|"
              r"praxisintegrierend|kooperativ|variante|online-studiengang|online|fernstudium|im praxisverbund)\b")


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


def labelled(p: pd.DataFrame) -> pd.DataFrame:
    """Sheet rows (with programme_id) plus the reviewed labels, joined on row_id."""
    rows = pd.read_excel(SHEET, sheet_name="labels", dtype={"programme_id": str}).drop(columns=["is_theme_programme", "note"])
    lab = pd.read_excel(LABELS, sheet_name="labels")[["row_id", "title", "is_theme_programme", "note"]]
    d = rows.merge(lab, on="row_id", suffixes=("", "_labels"), validate="one_to_one")
    if len(d) != len(rows) or not (d["title"] == d["title_labels"]).all():
        sys.exit(f"{LABELS.name} does not match {SHEET.name} on row_id/title")
    if not d["is_theme_programme"].isin(["y", "n", "?"]).all():
        sys.exit("is_theme_programme must be y, n or ? in every row")
    return d.drop(columns=["title_labels", "km_oth"]).merge(p[["programme_id", "state", "km_oth"]], on="programme_id")


def _wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return float("nan"), float("nan")
    q = k / n
    c = (q + z * z / (2 * n)) / (1 + z * z / n)
    h = z * ((q * (1 - q) + z * z / (4 * n)) / n) ** 0.5 / (1 + z * z / n)
    return c - h, c + h


def precision(d: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (group, theme), g in d[d["group"] != "miss_check"].groupby(["group", "theme"]):
        k, n = int((g["is_theme_programme"] == "y").sum()), int(g["is_theme_programme"].isin(["y", "n"]).sum())
        lo, hi = _wilson(k, n)
        rows.append({"theme": theme, "group": group, "labelled": n, "y": k, "precision %": round(k / n * 100, 1),
                     "95 % CI (Wilson)": f"{lo * 100:.0f}-{hi * 100:.0f} %",
                     "false matches (row_id)": ", ".join(str(r) for r in g.loc[g["is_theme_programme"] == "n", "row_id"]) or "-"})
    for theme, g in d[d["group"] == "miss_check"].groupby("theme"):
        rows.append({"theme": theme, "group": "miss_check", "labelled": len(g), "y": int((g["is_theme_programme"] == "y").sum()),
                     "precision %": "", "95 % CI (Wilson)": "", "false matches (row_id)": "y = missed by the title rule"})
    return pd.DataFrame(rows)


def _regions(d: pd.DataFrame) -> dict[str, int]:
    return {"Germany": len(d), "Bavaria": int((d["state"] == "Bayern").sum()),
            f"<={NEAR_KM} km": int((d["km_oth"] <= NEAR_KM).sum())}


def dedicated_cyber(d: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    c = d[(d["group"] == "all_cyber") & (d["is_theme_programme"] == "y")]
    drop = {pid for group in DUPLICATES for pid in group[1:]}
    distinct = c[~c["programme_id"].isin(drop)]
    rows = [{"level": lv, "offers (title match)": int((d[d["group"] == "all_cyber"]["level"] == lv).sum()),
             "false matches": int(((d["group"] == "all_cyber") & (d["is_theme_programme"] == "n") & (d["level"] == lv)).sum()),
             "duplicates merged": int((c["programme_id"].isin(drop) & (c["level"] == lv)).sum()),
             **_regions(distinct[distinct["level"] == lv])} for lv in ("BA", "MA")]
    t = pd.DataFrame(rows)
    t.loc[len(t)] = ["total"] + t.iloc[:, 1:].sum().tolist()
    near = distinct[distinct["km_oth"] <= NEAR_KM].sort_values("km_oth")[["level", "title", "institution", "km_oth"]]
    return t, near.assign(km_oth=near["km_oth"].round(0).astype(int))


def _focus(content: pd.Series) -> pd.Series:
    sp = content.str.extract(r"Schwerpunkte:\s*:\s*(.*?)(?:Anmerkung der Hochschule:|$)", flags=re.S)[0]
    return sp.fillna("").str.strip()


def _norm_title(t: str) -> str:
    t = re.sub(r"\s+(bachelor|master)\b.*$", "", t.lower())
    t = re.sub(FORM_WORDS, " ", t)
    t = re.sub(r"\([^a-zäöüß]*\)", " ", t)  # brackets left empty by the line above
    return re.sub(r"[^a-z0-9äöüß]+", " ", t).strip()


def secondary(p: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """General programmes whose focus areas name the theme (title does not match it)."""
    p = p.assign(focus=_focus(p["content"]), key=p["title"].map(_norm_title))
    title, focus = p["title"].str.lower(), p["focus"].str.lower()
    themes = {"cybersecurity": THEMES["cybersecurity"], "robotics": THEMES["robotics"],
              "ai_data": THEMES["ai_data"], "ai only (KI/AI/ML)": AI_ONLY}
    rows, near = [], []
    for name, pattern in themes.items():
        base = name if name in THEMES else "ai_data"
        hit = ~title.str.contains(THEMES[base], regex=True) & focus.str.contains(pattern, regex=True)
        if base in FOCUS_EXCLUDE:
            hit &= ~focus.str.contains(FOCUS_EXCLUDE[base], regex=True)
        s = p[hit].sort_values("km_oth").drop_duplicates(["institution", "level", "key"])
        for lv in ("BA", "MA"):
            x = s[s["level"] == lv]
            rows.append({"theme": name, "level": lv, "offers": int((p[hit]["level"] == lv).sum()), **_regions(x),
                         "of which OTH": int(x["is_oth"].sum())})
        if name in ("cybersecurity", "robotics"):
            n = s[s["km_oth"] <= NEAR_KM]
            near.append(n.assign(theme=name, km_oth=n["km_oth"].round(0).astype(int))[["theme", "level", "title", "institution", "km_oth"]])
    return pd.DataFrame(rows), pd.concat(near, ignore_index=True)


def score() -> str:
    p = programmes()
    d = labelled(p)
    t, near = dedicated_cyber(d)
    s, s_near = secondary(p)
    return "\n".join([
        "# Theme rules: hand-labelled check (generated)", "",
        f"Labels: {LABELS.relative_to(REPO_ROOT)} (proposed by Claude, reviewed by the team), joined on row_id "
        f"with {SHEET.relative_to(REPO_ROOT)}. Labels: " + ", ".join(f"{k} {v}" for k, v in d["is_theme_programme"].value_counts().items()) + ".", "",
        "## Precision of the title rules and miss check", "", _md(precision(d)), "",
        "## Distinct dedicated cybersecurity programmes", "",
        f"False matches removed; duplicates merged: {len(DUPLICATES)} groups (see DUPLICATES in analysis/theme_check.py).", "",
        _md(t), "", f"### Within {NEAR_KM} km of OTH", "", _md(near), "",
        "## Secondary competitors: general programmes with the theme as a focus area (Schwerpunkt)", "",
        "Variants (same institution, level, title apart from study-form words) counted once; 'offers' is before merging.", "",
        _md(s), "", f"### Within {NEAR_KM} km of OTH (cybersecurity, robotics)", "", _md(s_near), ""])


def _md(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(out)


def main(argv: list[str]) -> None:
    if argv[:1] == ["score"]:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(score(), encoding="utf-8")
        print(f"Written: {REPORT.relative_to(REPO_ROOT)}")
        return
    if not argv or argv[0] != "sample":
        sys.exit("Usage: python -m study_program_intelligence.analysis.theme_check sample [--force] | score")
    if SHEET.exists() and "--force" not in argv:
        sys.exit(f"{SHEET.relative_to(REPO_ROOT)} exists (may hold labels); use --force to overwrite")
    df = build(programmes())
    write(df, SHEET)
    print(f"Written: {SHEET.relative_to(REPO_ROOT)} ({len(df)} rows)")
    print(df.groupby(["group", "theme"]).size().to_string())


if __name__ == "__main__":
    main(sys.argv[1:])
