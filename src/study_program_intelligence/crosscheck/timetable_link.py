"""Link EMI handbook modules to the modules scheduled in the timetables (WS 2026/27, SS 2026).

Order: exact normalised title -> handbook code in brackets equals a timetable code -> close title (difflib).
Lecturers appear only as codes (T01...). Output: data/interim/crosscheck/timetable_link.csv (git-ignored).
"""

from __future__ import annotations

import difflib
import re

import pandas as pd

from .common import OUT, REPO

TT = REPO / "data" / "interim" / "timetable_modules.csv"
FUZZY_OK, FUZZY_UNSURE = 0.88, 0.75
STRUCTURAL = re.compile(r"bachelorarbeit|masterarbeit|praxis|wahlpflicht|profilierungsmodul|projektarbeit|kolloquium",
                        re.I)


def norm(s) -> str:
    s = re.sub(r"\[[^\]]*\]", " ", str(s)).lower()
    for a, b in [("&", " und "), ("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")]:
        s = s.replace(a, b)
    s = re.sub(r"\b(iv|i{1,3})\b", lambda m: {"i": "1", "ii": "2", "iii": "3", "iv": "4"}[m.group(1)], s)
    s = re.sub(r"\bpraktikum\b", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def link(modules: pd.DataFrame) -> pd.DataFrame:
    t = pd.read_csv(TT)
    t["n"] = t.module.map(norm)
    info = t.groupby("n").agg(tt_module=("module", "first"), lecturers=("lecturers", lambda s: "; ".join(sorted(
        {x.strip() for v in s.dropna() for x in str(v).split(";") if x.strip()}))),
        rooms=("rooms", lambda s: "; ".join(sorted({x.strip() for v in s.dropna() for x in str(v).split(";") if x.strip()}))),
        semesters=("semesters", lambda s: "; ".join(sorted(set(s.dropna())))))
    codes = {}
    for _, r in t.iterrows():
        for c in str(r.codes).split(";"):
            if c.strip():
                codes.setdefault(c.strip().upper(), r.n)
    names = sorted(info.index)
    rows = []
    for _, r in modules.iterrows():
        n = norm(r.title)
        code = re.findall(r"\[\s*([^\]=]+?)\s*(?:=[^\]]*)?\]", str(r.title))
        if n in info.index:
            how, hit, sc = "exact", n, 1.0
        elif code and code[0].upper() in codes:
            how, hit, sc = "code", codes[code[0].upper()], 1.0
        else:
            best = difflib.get_close_matches(n, names, n=1, cutoff=0.0)
            sc = difflib.SequenceMatcher(None, n, best[0]).ratio() if best else 0.0
            hit = best[0] if best else ""
            how = "close" if sc >= FUZZY_OK else "unsure" if sc >= FUZZY_UNSURE else "not scheduled"
        sched = how != "not scheduled"
        rows.append({"programme_id": r.programme_id, "title": r.title, "scheduled": sched, "how": how,
                     "match_score": round(sc, 2), "structural": bool(STRUCTURAL.search(str(r.title))),
                     "tt_module": info.tt_module.get(hit, "") if sched else "",
                     "lecturers": info.lecturers.get(hit, "") if sched else "",
                     "rooms": info.rooms.get(hit, "") if sched else "",
                     "semesters": info.semesters.get(hit, "") if sched else ""})
    out = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT / "timetable_link.csv", index=False)
    return out
