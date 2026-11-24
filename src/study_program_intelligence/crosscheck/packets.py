"""Blind marking packets for the AI topic check (public data only; no scores, ranks or timetable data)."""

from __future__ import annotations

import json
import re

import numpy as np
import pandas as pd

from . import engine as E
from . import steps as S
from .common import EMI_PROGRAMME_NAMES

VDIR = E.OUT / "verification"


NAME = re.compile(r"(Prof\.?|Dr\.?|Dipl\.?-?\w*\.?|M\.\s?(Sc|A|Eng)\.?|B\.\s?(Sc|A|Eng)\.?)(\s*(Dr\.?|-Ing\.?|rer\.\s?nat\.?|habil\.?))*"
                  r"(\s+[A-ZÄÖÜ][\w\-]+){1,3}")
STOP = re.compile(r"(Lehrmaterial|Teaching Material|Literatur\b|Reading List|Prüfungsform|Assessment|Medienformen)", re.I)
OUTCOME = re.compile(r"(Learning Outcomes|Qualifikationsziele|Lernziele)", re.I)
CONTENT = re.compile(r"(Course Content|Inhalte der Lehrveranstaltung\w*|Lehrinhalte|Inhalte)", re.I)
BOILER = [r"Nach dem erfolgreiche\w* Absolvieren des Moduls verfügen die Studierenden über die folgenden[^:]*:",
          r"Persönliche Kompetenz\w*.*?(?=(Inhalte|Course Content|$))", r"\(Sozial- und Selbstkompetenz\)",
          r"Fachkompetenz\w*:?", r"Methodenkompetenz\w*:?", r"\d+ / \d+", r"Learning Outcomes|Course Content"]


def content_text(raw: str, limit: int = 1100) -> str:
    """The module's real content: course content first, then subject/method outcomes. No header table, no names."""
    t = re.sub(r"\s+", " ", str(raw))
    def section(start_re):
        m = start_re.search(t)
        if not m:
            return ""
        s = t[m.end():]
        e = STOP.search(s)
        return s[: e.start()] if e else s
    cont = section(CONTENT)
    outc = section(OUTCOME)
    outc = CONTENT.split(outc)[0] if outc else ""
    txt = ("Content: " + cont.strip() if cont.strip() else "") + (" | Outcomes: " + outc.strip() if outc.strip() else "")
    if not txt:
        m = re.search(r"Workload.*?h\b(.*)", t)
        txt = m.group(1) if m else t
    for b in BOILER:
        txt = re.sub(b, " ", txt, flags=re.I | re.S)
    txt = NAME.sub("[name]", txt)
    txt = re.sub(r"\s+", " ", txt).strip(" -|•")
    return txt[:limit]


def catalogue(modules: pd.DataFrame) -> pd.DataFrame:
    clean = content_text
    return pd.DataFrame({
        "module_id": [f"M{i:03d}" for i in range(len(modules))],
        "programme": modules.programme_id.map(EMI_PROGRAMME_NAMES).fillna(modules.programme_id),
        "level": modules.level, "title": modules.title.map(lambda s: re.sub(r"\s+", " ", str(s)).strip()),
        "ects": modules.ects, "description": modules.text.fillna("").map(clean)})


def export(kinds: list[str], seed: int = 2026, n_suggest: int = 8):
    prep = E.prepare()
    modules = pd.read_csv(E.REPO / "data" / "interim" / "modules_emi_2026.csv")
    modules = modules[modules.title.notna()].reset_index(drop=True)
    cat = catalogue(modules)
    match = S.build_matcher(modules)
    rng = np.random.default_rng(seed)
    rows = []
    for kind in kinds:
        tp = prep.topics[kind]
        if not tp:
            continue
        sims = match([t for t, _ in tp])
        subj, lvl = kind.split(" | ")
        for i, (topic, n) in enumerate(tp):
            top = list(np.argsort(-sims[i])[:n_suggest])
            rng.shuffle(top)                                  # random order, no scores
            rows.append({"row_id": "", "kind": kind, "subject": subj, "level": lvl, "topic": topic, "weight": n,
                         "suggested": " ".join(cat.module_id.iloc[j] for j in top)})
    R = pd.DataFrame(rows).sample(frac=1, random_state=seed).reset_index(drop=True)   # rows in random order
    R["row_id"] = [f"T{i:04d}" for i in range(len(R))]
    VDIR.mkdir(parents=True, exist_ok=True)
    cat.to_csv(VDIR / "emi_module_catalogue.csv", index=False)
    R.to_csv(VDIR / "topic_rows_key.csv", index=False)                      # with weight (not given to reviewers)
    R.drop(columns=["weight"]).to_csv(VDIR / "topic_rows_for_review.csv", index=False)
    return cat, R


def batches(target_rows: int = 55):
    """Write one markdown packet per batch: rows (grouped by kind, rows shuffled) + needed module texts + title index."""
    cat = pd.read_csv(VDIR / "emi_module_catalogue.csv")
    R = pd.read_csv(VDIR / "topic_rows_for_review.csv")
    out = VDIR / "packets"
    out.mkdir(parents=True, exist_ok=True)
    groups, cur = [], []
    for kind, g in R.groupby("kind", sort=True):
        if cur and sum(len(x) for x in cur) + len(g) > target_rows:
            groups.append(cur); cur = []
        cur.append(g)
    if cur:
        groups.append(cur)
    index = "\n".join(f"{r.module_id} | {r.programme} | {r.title}" for r in cat.itertuples())
    manifest = []
    for b, gs in enumerate(groups, 1):
        rows = pd.concat(gs).sample(frac=1, random_state=b)
        need = sorted({m for s in rows.suggested for m in s.split()})
        mods = cat.set_index("module_id").loc[need]
        lines = [f"# Topic-check packet B{b:02d}", "", "## Rows to mark", "",
                 "| row_id | programme kind | topic | suggested EMI modules |", "|---|---|---|---|"]
        lines += [f"| {r.row_id} | {r.kind} | {r.topic} | {r.suggested} |" for r in rows.itertuples()]
        lines += ["", "## Suggested modules (full descriptions)", ""]
        for mid, m in mods.iterrows():
            d = str(m.description)
            lines.append(f"### {mid}: {m.title} ({m.programme}, {m.level}, {m.ects} ECTS)\n{d}\n")
        lines += ["## Index of all EMI modules (id | programme | title)", "", index]
        p = out / f"B{b:02d}.md"
        p.write_text("\n".join(lines), encoding="utf-8")
        manifest.append({"batch": f"B{b:02d}", "rows": len(rows), "kinds": "; ".join(g.kind.iloc[0] for g in gs),
                         "kb": round(p.stat().st_size / 1024)})
    pd.DataFrame(manifest).to_csv(out / "manifest.csv", index=False)
    return pd.DataFrame(manifest)
