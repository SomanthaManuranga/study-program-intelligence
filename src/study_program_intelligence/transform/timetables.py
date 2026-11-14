"""EMI timetables (internal, provided by the supervisor) -> one table of who teaches which subject, without names.

Run from the repository root, with the two PDFs in data/raw/oth_internal/ (git-ignored):

    python -m study_program_intelligence.transform.timetables

The PDFs hold one weekly grid per semester group and, on the next page, that group's list of subject codes with long
names. Every grid cell is a stack of small text lines: subject code, lecturer, room, sometimes notes below.
The cell is rebuilt from the positions of the text fragments: for each subject code, the lines directly below it.
A subject that is listed for a group but has no weekly slot (block courses, dates by arrangement) is kept as a row
without lecturer (in_grid = False).

Internal data rule (configs/funnel.yaml, feasibility_gate.internal_data): lecturers appear only as neutral labels
(L001, ...). The label order comes from a random salt; salt and name-to-label table stay in data/raw/oth_internal/. The
output table has no names.
Outputs: data/interim/timetable_subjects.csv (one row per grid cell and group), data/interim/timetable_report.json;
with the argument "spotcheck": data/raw/oth_internal/timetable_spotcheck.md (internal, with names, for a check by eye).
Limits: the grid gives no ECTS and no hours; the length of a block is not read; a session shared by several groups
appears once per group; long room lists are cut off in the PDF; two lecturers with one surname would share a label.
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
import sys
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE = REPO_ROOT / "data" / "raw" / "oth_internal"
LABELS = SOURCE / "lecturer_labels.csv"
SALT = SOURCE / "label_salt.txt"
SPOTCHECK = SOURCE / "timetable_spotcheck.md"
OUT = REPO_ROOT / "data" / "interim" / "timetable_subjects.csv"
REPORT = REPO_ROOT / "data" / "interim" / "timetable_report.json"

CELL_SIZE = (6.0, 7.0)          # font size of the text inside grid cells
HEADING_SIZE = 17.0             # the group name is the only text this large
LINE = 10.1                     # distance between the lines of one cell
ROOM = re.compile(r"(online|[A-Z]{2,6}\d{1,3}[A-Za-z]?)(,.*)?")      # one or more rooms; long lists are cut off in the PDF
FULL_ROOM = re.compile(r"online|[A-Z]{2,6}\d{2,3}[A-Za-z]?")
SURNAME = re.compile(r"[A-ZÄÖÜ][a-zäöüß]+(-[A-ZÄÖÜ][a-zäöüß]+)?")
DAYS = ("Mo", "Di", "Mi", "Do", "Fr")


def fragments(page) -> list[dict]:
    out: list[dict] = []

    def visit(text, cm, tm, font, size):
        t = text.strip()
        if t:
            out.append({"x": float(tm[4]), "y": float(tm[5]), "size": float(size), "text": t})

    page.extract_text(visitor_text=visit)
    return out


def centre(f: dict) -> float:
    """Estimated horizontal centre of a fragment (text in a cell is centred; x is its left edge)."""
    return f["x"] + 0.25 * f["size"] * len(f["text"])


def subject_list(frags: list[dict]) -> dict[str, str]:
    """Code -> long name, from the two columns under the headers "Name" and "Langname" (a code may contain a space)."""
    head = next(f for f in frags if f["text"] == "Langname")
    name_x = next(f["x"] for f in frags if f["text"] == "Name" and abs(f["y"] - head["y"]) < 1)
    below = [f for f in frags if f["y"] < head["y"] - 1 and not f["text"].startswith("Seite")]
    codes = {round(f["y"], 1): f["text"] for f in below if abs(f["x"] - name_x) < 2}
    longs = {round(f["y"], 1): f["text"] for f in below if abs(f["x"] - head["x"]) < 2}
    return {code: longs.get(y, "") for y, code in codes.items()}


def grid_cells(frags: list[dict], codes: set[str]) -> tuple[list[dict], list[str]]:
    """One dict per grid cell. Returns the cells and the cell-sized texts that belong to no cell."""
    small = [f for f in frags if CELL_SIZE[0] <= f["size"] <= CELL_SIZE[1]]
    days = {f["text"]: centre(f) for f in frags if f["text"] in DAYS and f["size"] > 10}
    used: set[int] = set()
    cells = []
    for i, f in enumerate(small):
        if f["text"] not in codes:
            continue
        used.add(i)
        below = []
        for step in (1, 2, 3, 4):
            cand = [(abs(centre(g) - centre(f)), j) for j, g in enumerate(small)
                    if j not in used and abs(g["y"] - (f["y"] - step * LINE)) < 2.0 and abs(centre(g) - centre(f)) < 30 and g["text"] not in codes]
            if cand:
                j = min(cand)[1]
                used.add(j)
                below.append(small[j]["text"])
        lecturer = below[0] if below and SURNAME.fullmatch(below[0]) and not ROOM.fullmatch(below[0]) else ""   # first line under the code
        rest = below[1:] if lecturer else below
        room = next((b for b in rest if ROOM.fullmatch(b)), "")
        note = "; ".join(b for b in rest if b != room)
        day = min(days, key=lambda d: abs(days[d] - centre(f))) if days else ""
        cells.append({"code": f["text"], "lecturer": lecturer, "room": room, "note": note, "day": day, "y": round(f["y"], 1)})
    orphans = [g["text"] for j, g in enumerate(small) if j not in used]
    return cells, orphans


def parse(path: Path) -> tuple[pd.DataFrame, dict]:
    reader = PdfReader(path)
    rows, orphans, groups = [], [], []
    no_slot = 0
    semester, printed = "", ""
    pending: tuple[str, int, list[dict]] | None = None          # a grid page waits for the subject list on the next page
    for n, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        frags = fragments(page)
        m = re.search(r"Stundenplan\s+(Wintersemester|Sommersemester)\s+(\d{4}(?:/\d{2})?)", text)
        if m:
            semester = ("WS " if m.group(1).startswith("Winter") else "SS ") + m.group(2)
        if not printed:
            pm = re.search(r"\b(\d{1,2}\.\d{1,2}\.\d{4})\s+\d{1,2}:\d{2}\b", text)
            printed = pm.group(1) if pm else ""
        heading = next((f["text"] for f in frags if f["size"] >= HEADING_SIZE), "")
        if any(f["text"] == "Langname" for f in frags):
            subjects = subject_list(frags)
            if pending is None or pending[0] != heading:
                raise ValueError(f"{path.name} page {n}: subject list of '{heading}' has no grid page before it")
            cells, orph = grid_cells(pending[2], set(subjects))
            orphans += orph
            groups.append(heading)
            for c in cells:
                rows.append({"semester": semester, "group": heading, "page": pending[1], **c, "subject": subjects[c["code"]], "in_grid": True})
            for code in subjects:
                if code not in {c["code"] for c in cells}:
                    no_slot += 1
                    rows.append({"semester": semester, "group": heading, "page": pending[1], "code": code, "lecturer": "", "room": "", "note": "",
                                 "day": "", "y": float("nan"), "subject": subjects[code], "in_grid": False})
            pending = None
        else:
            if pending is not None:
                raise ValueError(f"{path.name} page {n}: grid page of '{pending[0]}' has no subject list after it")
            pending = (heading, n, frags)
    if pending is not None:
        raise ValueError(f"{path.name}: last grid page has no subject list")
    d = pd.DataFrame(rows)
    grid = d[d["in_grid"]]
    sessions = grid.drop_duplicates(["day", "y", "code", "lecturer", "room"])
    report = {"file": path.name, "plan_printed": printed, "pages": len(reader.pages), "semester": semester, "groups": len(groups), "grid_cells": len(grid),
              "distinct_sessions": len(sessions), "room_lists_cut_off": int(grid["room"].map(lambda r: bool(r) and not FULL_ROOM.fullmatch(r.split(",")[-1].strip())).sum()),
              "listed_subjects_without_a_slot": no_slot, "cell_texts_in_no_cell": len(orphans),
              "grid_cells_without_lecturer": int((grid["lecturer"] == "").sum()), "grid_cells_without_room": int((grid["room"] == "").sum())}
    return d, report


def label_lecturers(d: pd.DataFrame) -> pd.DataFrame:
    """Replaces names by labels. The mapping is kept (and extended, never renumbered) in the protected folder."""
    known = pd.read_csv(LABELS) if LABELS.exists() else pd.DataFrame(columns=["name", "label"])
    mapping = dict(zip(known["name"], known["label"]))
    if not SALT.exists():
        SALT.write_text(secrets.token_hex(16), encoding="utf-8")
    salt = SALT.read_text(encoding="utf-8").strip()
    new = {x for x in d["lecturer"] if x} - set(mapping)
    for name in sorted(new, key=lambda x: hashlib.sha256((salt + x).encode("utf-8")).hexdigest()):     # order from a secret salt, not from the name
        mapping[name] = f"L{len(mapping) + 1:03d}"
    pd.DataFrame(sorted(mapping.items(), key=lambda kv: kv[1]), columns=["name", "label"]).to_csv(LABELS, index=False)
    out = d.copy()
    out["lecturer"] = out["lecturer"].map(lambda x: mapping.get(x, ""))
    return out


def spotcheck(pages=(("WS 2026/27", 1), ("WS 2026/27", 3), ("SS 2026", 1), ("SS 2026", 3))) -> None:
    """Internal sheet with names for a check by eye against the PDF pages; written only into the protected folder."""
    t = pd.read_csv(OUT)
    lab = pd.read_csv(LABELS)
    back = dict(zip(lab["label"], lab["name"]))
    lines = ["# Timetable spot check (INTERNAL: contains names, stays in this git-ignored folder)", "",
             "Open the PDF page named in each heading and compare cell by cell (days left to right, top to bottom inside a day).", ""]
    for sem, page in pages:
        p = t[(t["semester"] == sem) & (t["page"] == page) & t["in_grid"]].copy()
        p["d"] = p["day"].map({d: i for i, d in enumerate(DAYS)})
        p = p.sort_values(["d", "y"], ascending=[True, False]).fillna("")
        group = p["group"].iloc[0]
        lines += [f"## {sem}, PDF page {page}: group {group}, {len(p)} cells", "",
                  "| Day | Subject code | Subject (from the list on the next page) | Lecturer in the PDF | Label in our table | Room | Note |", "|---|---|---|---|---|---|---|"]
        lines += [f"| {r.day} | {r.code} | {r.subject} | {back[r.lecturer]} | {r.lecturer} | {r.room} | {r.note} |" for r in p.itertuples()]
        lines.append("")
    SPOTCHECK.write_text("\n".join(lines), encoding="utf-8")
    print(f"Written (internal): {SPOTCHECK.relative_to(REPO_ROOT)}")


def main() -> None:
    from study_program_intelligence.analysis.funnel_common import run_stamp
    stamp = run_stamp()
    pdfs = sorted(SOURCE.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No timetable PDFs in {SOURCE.relative_to(REPO_ROOT)} (internal files; copy them there by hand).")
    tables, reports = [], []
    for p in pdfs:
        t, r = parse(p)
        tables.append(t)
        reports.append(r)
    d = label_lecturers(pd.concat(tables, ignore_index=True))
    d = d[["semester", "group", "page", "day", "code", "subject", "lecturer", "room", "note", "in_grid", "y"]]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(OUT, index=False)
    summary = {"stamp": stamp, "files": reports, "rows": len(d), "semesters": sorted(d["semester"].unique()), "groups": int(d.groupby("semester")["group"].nunique().sum()),
               "distinct_subject_names": int(d["subject"].nunique()), "lecturers": int(d.loc[d["lecturer"] != "", "lecturer"].nunique())}
    REPORT.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    spotcheck() if sys.argv[1:] == ["spotcheck"] else main()
