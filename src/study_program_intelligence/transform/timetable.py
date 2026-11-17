"""EMI timetables (Untis export, one PDF per semester) -> sessions, modules, staff capability, rooms.

Run from the repository root:

    python -m study_program_intelligence.transform.timetable

Input: the timetable PDFs provided by the supervisor, in data/raw/oth_internal/ (git-ignored). Each semester
group has two pages: a week grid (cells of module code / lecturer / room) and a legend ("Fächer": code -> name).

Privacy: lecturer names never leave data/. Every output uses neutral labels (T01, T02, ...); the only
file with names is data/interim/timetable_lecturer_key.csv. Criteria: docs/criteria_timetable.md.
"""

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
IN_DIR = REPO_ROOT / "data" / "raw" / "oth_internal"   # shared with transform/timetables.py (soma/funnel)
OUT_DIR = REPO_ROOT / "data" / "interim"
REPORT = REPO_ROOT / "reports" / "timetable.md"

DAYS = ("Mo", "Di", "Mi", "Do", "Fr", "Sa")
LINE_STEP = 10.0          # distance between the lines of one cell (points)
ROOM = re.compile(r"^(?:[A-ZÄÖÜ]{2,5}\d{2,3}[a-z]?|online|Audimax)(?:\s*,\s*(?:[A-ZÄÖÜ]{2,5}\d{2,3}[a-z]?|online|Audimax))*$")   # EMI214, MBUTE10, DC107; several rooms comma-separated
KIND = (
    ("Vorlesung", "lecture"), ("Übung", "exercise"), ("Zusatzübung", "exercise"), ("Praktikum", "lab"),
    ("Seminar", "seminar"), ("Projekt", "project"), ("Tutorium", "tutorial"),
)
KIND_SUFFIX = {"VL": "lecture", "Ue": "exercise", "UE": "exercise", "Pr": "lab", "PR": "lab", "Sem": "seminar",
               "Tut": "tutorial", "Z": "exercise"}


def label(n: int) -> str:
    """0 -> 'T01'. 'T' labels are timetable lecturers (professors and external lecturers alike); they are NOT the
    'Prof. A-N' labels of docs/evidence_fit_staff.md."""
    return f"T{n + 1:02d}"


def split_name(long_name: str) -> tuple[str, str]:
    """'Elektrotechnik 1 (Vorlesung)' -> ('Elektrotechnik 1', 'lecture')."""
    kind = ""
    m = re.search(r"\(([^)]*)\)\s*$", long_name)
    if m:
        for word, k in KIND:
            if word.lower() in m.group(1).lower():
                kind = k
        if kind:
            long_name = long_name[: m.start()].strip()
    return long_name.strip(), kind


def kind_from_code(code: str) -> str:
    for part in reversed(code.split("_")[1:]):
        if part in KIND_SUFFIX:
            return KIND_SUFFIX[part]
    return ""


def page_lines(words: list[dict], tol: float = 2.5) -> list[list[dict]]:
    """Words grouped into text lines by their top coordinate."""
    lines: list[list[dict]] = []
    for w in sorted(words, key=lambda w: (w["top"], w["x0"])):
        if lines and abs(lines[-1][0]["top"] - w["top"]) <= tol:
            lines[-1].append(w)
        else:
            lines.append([w])
    return [sorted(line, key=lambda w: w["x0"]) for line in lines]


def parse_legend(words: list[dict]) -> dict[str, str]:
    """Legend page -> {code: long name}."""
    legend: dict[str, str] = {}
    started = False
    for line in page_lines(words):
        texts = [w["text"] for w in line]
        if texts[:2] == ["Name", "Langname"]:
            started = True
            continue
        if not started or texts[0] == "Seite":
            continue
        if len(texts) >= 2:
            legend[texts[0]] = " ".join(texts[1:])
        else:
            legend.setdefault(texts[0], "")
    return legend


def parse_grid(words: list[dict], legend: dict[str, str]) -> list[dict]:
    """Grid page -> one row per cell: code, lecturer, room, day, start time, extra text."""
    day_x = {w["text"]: (w["x0"] + w["x1"]) / 2 for w in words if w["text"] in DAYS and w["top"] < 100}
    days = sorted(day_x.items(), key=lambda kv: kv[1])
    slots = sorted(
        ((w["top"], w["text"]) for w in words if re.fullmatch(r"\d{1,2}:\d{2}-\d{1,2}:\d{2}", w["text"])),
    )
    body = [w for w in words if w["top"] > 100 and w["x0"] > 105 and not w["text"].startswith("Seite")]

    def centre(w: dict) -> float:
        return (w["x0"] + w["x1"]) / 2

    def below(code: dict, k: int) -> list[dict]:
        """Words on the k-th line under a code, in the same column."""
        y = code["top"] + k * LINE_STEP
        half = max(30.0, (code["x1"] - code["x0"]) / 2 + 14)
        return sorted(
            (w for w in body if abs(w["top"] - y) <= 3 and abs(centre(w) - centre(code)) <= half and w is not code),
            key=lambda w: w["x0"],
        )

    codes = [w for w in body if w["text"] in legend]
    rows = []
    for c in codes:
        lecturer, room, extra = "", "", []
        for k in (1, 2, 3, 4):
            ws = [w for w in below(c, k) if w["text"] not in legend]
            if not ws:
                if k > 2:
                    break
                continue
            text = " ".join(w["text"] for w in ws)
            if k == 1 and not ROOM.match(text) and not re.search(r"\d|Absprache|Vereinbarung", text):
                lecturer = text
            elif not room and ROOM.match(text):
                room = text
            elif not room and "," in text and any(ROOM.match(p.strip()) for p in text.split(",")):
                # room list cut off by the cell width ("EMI305,EMI306,EMI3"): keep the complete room numbers
                parts = [p.strip() for p in text.split(",")]
                room = ",".join(p for p in parts if ROOM.match(p))
                extra.append("room list cut off in the PDF: " + ",".join(p for p in parts if not ROOM.match(p)))
            else:
                extra.append(text)
        day = min(days, key=lambda kv: abs(kv[1] - centre(c)))[0] if days else ""
        if days and centre(c) > days[-1][1] + 75:
            day = days[-1][0]
        start = ""
        if slots:
            # a cell belongs to the slot whose label is closest to the cell's middle line
            start = min(slots, key=lambda s: abs(s[0] - (c["top"] + LINE_STEP)))[1].split("-")[0]
        note = re.sub(r"\b(?:for\s+)?Prof\.?\s+\S+", "[lecturer]", "; ".join(extra))   # no names in notes
        rows.append({"code": c["text"], "lecturer": lecturer, "room": room, "day": day, "start": start, "note": note})
    return rows


def parse_pdf(path: Path) -> tuple[str, list[dict], dict]:
    """One timetable PDF -> (semester, sessions, stats)."""
    import pdfplumber

    sessions: list[dict] = []
    stats = {"grid_pages": 0, "groups": 0, "codes_unknown": 0}
    semester = ""
    with pdfplumber.open(path) as pdf:
        pages = []
        for page in pdf.pages:
            words = page.extract_words(keep_blank_chars=False, use_text_flow=False)
            text = " ".join(w["text"] for w in words[:14])
            if not semester:
                m = re.search(r"(Wintersemester|Sommersemester)\s+(\d{4}(?:/\d{2})?)", text)
                if m:
                    semester = ("WS " if m.group(1).startswith("W") else "SS ") + m.group(2)
            head = [w for w in words if 52 < w["top"] < 66]
            group = " ".join(w["text"] for w in sorted(head, key=lambda w: w["x0"]))
            is_legend = any(w["text"] == "Langname" for w in words)
            pages.append((group, is_legend, words))
        legends: dict[str, dict[str, str]] = defaultdict(dict)
        for group, is_legend, words in pages:
            if is_legend:
                legends[group].update(parse_legend(words))
        for group, is_legend, words in pages:
            if is_legend:
                continue
            stats["grid_pages"] += 1
            legend = legends.get(group, {})
            if legend:
                stats["groups"] += 1
            for row in parse_grid(words, legend):
                name, kind = split_name(legend.get(row["code"], ""))
                sessions.append({"semester": semester, "group": group, **row, "module": name,
                                 "kind": kind or kind_from_code(row["code"]) or "course"})
    return semester, sessions, stats


def programme_of(group: str) -> str:
    """'EI 3' -> 'EI', 'GI 4 - LM' -> 'GI-LM', 'IK6' -> 'IK', 'MAI_BC' -> 'MAI BC'."""
    g = group.replace("_", " ").strip()
    m = re.fullmatch(r"([A-Za-z]+)\s*(\d+)?(?:\s*-\s*([A-Za-z]+))?(?:\s+([A-Za-z]+))?", g)
    if not m:
        return g
    parts = [m.group(1)] + [p for p in (m.group(3), m.group(4)) if p]
    return "-".join(parts) if m.group(3) else " ".join(parts)


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    pdfs = sorted(IN_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No timetable PDFs in {IN_DIR.relative_to(REPO_ROOT).as_posix()} (manual input from the supervisor).")
        return 1
    sessions: list[dict] = []
    summary = []
    for pdf in pdfs:
        semester, rows, stats = parse_pdf(pdf)
        sessions += rows
        summary.append((semester, stats, len(rows)))

    # neutral labels, ordered by teaching volume (most sessions first), stable across reruns of the same input
    volume: dict[str, int] = defaultdict(int)
    for s in sessions:
        for name in filter(None, (n.strip() for n in re.split(r"[,/]", s["lecturer"]))):
            volume[name] += 1
    order = sorted(volume, key=lambda n: (-volume[n], n))
    key = {name: label(i) for i, name in enumerate(order)}
    for s in sessions:
        names = [n.strip() for n in re.split(r"[,/]", s["lecturer"]) if n.strip()]
        s["lecturer_label"] = ", ".join(key[n] for n in names)
        s["programme"] = programme_of(s["group"])

    write_csv(OUT_DIR / "timetable_lecturer_key.csv", [{"label": key[n], "name": n, "sessions": volume[n]} for n in order],
              ["label", "name", "sessions"])
    public = ["semester", "programme", "group", "code", "module", "kind", "lecturer_label", "room", "day", "start", "note"]
    write_csv(OUT_DIR / "timetable_sessions.csv", sessions, public)

    # modules: one row per (module name), with the programmes, kinds, labels and rooms it appears with
    mods: dict[str, dict] = {}
    for s in sessions:
        name = s["module"] or s["code"]
        m = mods.setdefault(name, {"module": name, "codes": set(), "programmes": set(), "semesters": set(),
                                   "kinds": set(), "lecturers": set(), "rooms": set(), "sessions": 0})
        m["codes"].add(s["code"]); m["programmes"].add(s["programme"]); m["semesters"].add(s["semester"])
        m["kinds"].add(s["kind"]); m["sessions"] += 1
        m["lecturers"].update(filter(None, s["lecturer_label"].split(", ")))
        m["rooms"].update(filter(None, re.split(r"[,;]\s*", s["room"])))
    mod_rows = [{k: ("; ".join(sorted(x for x in v if x)) if isinstance(v, set) else v) for k, v in m.items()}
                for m in sorted(mods.values(), key=lambda m: m["module"].lower())]
    write_csv(OUT_DIR / "timetable_modules.csv", mod_rows,
              ["module", "codes", "programmes", "semesters", "kinds", "lecturers", "rooms", "sessions"])

    # capability: what each label teaches
    cap: dict[str, dict] = {}
    for s in sessions:
        for lab in filter(None, s["lecturer_label"].split(", ")):
            c = cap.setdefault(lab, {"lecturer_label": lab, "modules": set(), "programmes": set(), "sessions": 0})
            c["modules"].add(s["module"] or s["code"]); c["programmes"].add(s["programme"]); c["sessions"] += 1
    cap_rows = [{"lecturer_label": c["lecturer_label"], "n_modules": len(c["modules"]), "sessions": c["sessions"],
                 "programmes": "; ".join(sorted(c["programmes"])), "modules": "; ".join(sorted(c["modules"]))}
                for c in sorted(cap.values(), key=lambda c: -c["sessions"])]
    write_csv(OUT_DIR / "timetable_capability.csv", cap_rows,
              ["lecturer_label", "n_modules", "sessions", "programmes", "modules"])

    # rooms: where lab sessions take place
    rooms: dict[str, dict] = {}
    for s in sessions:
        for r in filter(None, re.split(r"[,;]\s*", s["room"])):
            x = rooms.setdefault(r, {"room": r, "sessions": 0, "lab_sessions": 0, "lab_modules": set()})
            x["sessions"] += 1
            if s["kind"] == "lab":
                x["lab_sessions"] += 1
                x["lab_modules"].add(s["module"] or s["code"])
    room_rows = [{"room": x["room"], "sessions": x["sessions"], "lab_sessions": x["lab_sessions"],
                  "lab_modules": "; ".join(sorted(x["lab_modules"]))}
                 for x in sorted(rooms.values(), key=lambda x: (-x["lab_sessions"], x["room"]))]
    write_csv(OUT_DIR / "timetable_rooms.csv", room_rows, ["room", "sessions", "lab_sessions", "lab_modules"])

    with_lecturer = sum(1 for s in sessions if s["lecturer"])
    with_module = sum(1 for s in sessions if s["module"])
    lines = ["# EMI timetables: parse summary", "",
             "Generated by `python -m study_program_intelligence.transform.timetable`. Lecturers appear as neutral",
             "labels; the key is `data/interim/timetable_lecturer_key.csv` (git-ignored).", "",
             "| Semester | Grid pages | Groups with legend | Entries |", "|---|---|---|---|"]
    lines += [f"| {sem} | {st['grid_pages']} | {st['groups']} | {n} |" for sem, st, n in summary]
    lines += ["", f"- Entries: {len(sessions)}; with a module name from the legend: {with_module} "
              f"({with_module / max(len(sessions), 1):.1%}); with a lecturer: {with_lecturer} "
              f"({with_lecturer / max(len(sessions), 1):.1%}).",
              f"- Distinct modules: {len(mod_rows)}; lecturer labels: {len(key)}; rooms: {len(room_rows)} "
              f"({sum(1 for r in room_rows if r['lab_sessions'])} used for lab sessions).", "",
              "## Teaching volume per label (top 15)", "", "| Label | Modules | Entries | Programmes |", "|---|---|---|---|"]
    lines += [f"| {c['lecturer_label']} | {c['n_modules']} | {c['sessions']} | {c['programmes']} |" for c in cap_rows[:15]]
    lines += ["", "## Entries without a lecturer", ""]
    missing = [s for s in sessions if not s["lecturer"]]
    lines += [f"- {s['semester']} {s['group']}: {s['code']} ({s['module']}) {s['day']} {s['start']} {s['room']}"
              for s in missing[:60]] or ["None."]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines[5:12]))
    print(f"Written: {REPORT.relative_to(REPO_ROOT).as_posix()} and data/interim/timetable_*.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
