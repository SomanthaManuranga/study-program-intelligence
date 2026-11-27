"""Rules version 4, R3-R8: module marking under one standard (configs/funnel.yaml: version_4.marking, person_check,
verdict; readings and criteria in docs/criteria_funnel_v4_marking.md; reader instructions in
docs/funnel_marking_rules.md, version 4)

Run from the repository root, each command from committed code on a clean tree, after analysis.funnel_gate4:

    python -m study_program_intelligence.analysis.funnel_mark4 rows          # catalogue, blind rows, reader blocks
    (fresh readers write docs/funnel4_marks_1_<block>.csv; commit)
    python -m study_program_intelligence.analysis.funnel_mark4 check 1       # every row has valid facts
    python -m study_program_intelligence.analysis.funnel_mark4 sample        # rows for the blind second reader
    python -m study_program_intelligence.analysis.funnel_mark4 third         # rows on which the first two differ
    python -m study_program_intelligence.analysis.funnel_mark4 consistency   # pairs of the same topic side by side
    python -m study_program_intelligence.analysis.funnel_mark4 person        # the persons' sheet
    python -m study_program_intelligence.analysis.funnel_mark4 verdict       # the four combinations per candidate

The readers record facts (covered, covering, topic, parent_field, lab, general); the code turns them into verdicts
under a strict and a lenient marking reading and a content and a size reading. Sheets and keys stay under
data/interim and reports/ (module texts of other universities); the marks are committed in docs/.
"""

from __future__ import annotations

import json
import re
import sys

import numpy as np
import pandas as pd
import yaml

from .funnel_common import INTERIM, REPO_ROOT, REPORTS, config, run_stamp
from .funnel_feasibility import (LABS, NEAREST, SUBJECTS, TIMETABLE, emi_allowed, emi_text, nearest, redact, same_module, subject_name,
                                 title_matches, title_words, complete)
from .funnel_gate4 import LIST4
from .funnel_modules import EMI_MODULES, vectors
from .funnel_refs import LEFT_OUT
from .funnel_types import sha
from .module_gaps import embed

REFS4 = INTERIM / "funnel4_refs"
TRIES4 = INTERIM / "funnel4_reference_tries.csv"
CATALOGUE = {lv: REPORTS / f"v4_emi_catalogue_{lv}.md" for lv in ("bachelor", "master")}
CAT_TABLE, TT_TABLE = INTERIM / "funnel4_emi_catalogue.csv", INTERIM / "funnel4_timetable_subjects.csv"
ROWS4, KEY4 = INTERIM / "funnel4_rows.json", INTERIM / "funnel4_rows_key.csv"
BLOCKS = REPORTS / "v4_rows"
MARKS = lambda k: sorted((REPO_ROOT / "docs").glob(f"funnel4_marks_{k}_*.csv"))
SEED, BLOCK, CAT_TEXT, MODULE_TEXT = 42, 50, 1500, 1500
FACTS = ["covered", "covering", "topic", "parent_field", "lab", "general", "unsure", "reason"]


# ----------------------------------------------------------------------------------------------------- catalogue

def catalogue(emi: pd.DataFrame) -> pd.DataFrame:
    """K2: one entry per EMI module allowed for the level, copies once, E numbers in order of level and title; the ECTS
    is the largest of its copies."""
    rows = []
    for lv, code in (("bachelor", "BA"), ("master", None)):
        allowed = emi[emi_allowed(emi, lv)].assign(t=lambda x: x["title"].map(same_module))
        for t, g in allowed.sort_values(["t", "module_id"]).groupby("t", sort=True):
            first = g.iloc[0]
            rows.append({"level": lv, "same": t, "title": first["title"], "ects": float(pd.to_numeric(g["ects"], errors="coerce").max()),
                         "module_ids": "; ".join(g["module_id"]), "programmes": "; ".join(sorted(set(g["programme_id"]))),
                         "text": emi_text(first["text"], first["title"])[:CAT_TEXT]})
    c = pd.DataFrame(rows)
    c["number"] = [f"E{i:03d}" for i in range(1, len(c) + 1)]                 # one numbering across both levels
    return c


def timetable() -> pd.DataFrame:
    tt = sorted({subject_name(s) for s in pd.read_csv(TIMETABLE)["subject"].dropna()} - {""})
    return pd.DataFrame({"number": [f"T{i:03d}" for i in range(1, len(tt) + 1)], "subject": tt})


# ------------------------------------------------------------------------------------------------------------ rows

def tables() -> tuple[pd.DataFrame, dict]:
    """K1: the counted modules of every complete table of a candidate with a module check."""
    chk = pd.read_csv(LIST4)
    want = {(int(c), lv) for c, lv, m in zip(chk["candidate"], chk["level"], chk["module check"]) if m}
    frames, metas = [], {}
    for f in sorted(REFS4.glob("*_[ab].json")):
        meta = json.loads(f.read_text(encoding="utf-8"))
        c, lv = int(f.stem.split("_")[0]), f.stem.split("_")[1]
        if (c, lv) not in want:
            continue
        m = pd.read_csv(f.with_suffix(".csv"))
        ok, share = complete(m, meta, 0.8)
        metas[f.stem] = {**meta, "complete": ok, "share listed": share}
        if ok:
            m = m[~m["kind"].isin(LEFT_OUT)].reset_index(drop=True)
            frames.append(m.assign(ref=f.stem, candidate=c, level=lv, order=np.arange(len(m)), ects=pd.to_numeric(m["ects"])))
    return pd.concat(frames, ignore_index=True), metas


def blind_terms(metas: dict) -> list[str]:
    tries = pd.read_csv(TRIES4)
    common = {"hochschule", "technische", "university", "universität", "angewandte", "wissenschaften", "fachhochschule", "für", "und", "des", "der", "die", "applied",
              "sciences", "technology", "technik", "wirtschaft", "kultur", "gestaltung", "of", "and", "ostbayerische"}
    out = set()
    for m in metas.values():
        out.add(m["institution"])
        out |= {w for w in re.findall(r"[A-ZÄÖÜ][\wäöüß-]{3,}", m["institution"]) if w.lower() not in common}
        city = tries.loc[tries["programme_id"].astype(str) == str(m.get("programme_id")), "city"]
        if len(city):
            out.add(re.split(r"[,(]", str(city.iloc[0]))[0].strip())
    return sorted((t for t in out if t), key=len, reverse=True)


def rows() -> None:
    stamp = run_stamp()
    ref, metas = tables()
    emi = pd.read_csv(EMI_MODULES, low_memory=False)
    cat, tt = catalogue(emi), timetable()
    cat.to_csv(CAT_TABLE, index=False)
    tt.to_csv(TT_TABLE, index=False)
    number_of = {(lv, s): n for lv, s, n in zip(cat["level"], cat["same"], cat["number"])}
    REPORTS.mkdir(parents=True, exist_ok=True)
    for lv in ("bachelor", "master"):
        c = cat[cat["level"] == lv]
        CATALOGUE[lv].write_text("\n".join([f"# EMI modules allowed for a {lv} programme ({len(c)}), and the timetable subjects", "",
                                            "Cite a module by its number (E...), a timetable subject by its number (T...).", ""] +
                                           [f"## {r.number} {r.title} ({r.ects:g} ECTS)\n\n{r.text}\n" for r in c.itertuples()] +
                                           ["# Timetable subjects (what current lecturers teach)", ""] + [f"- {r.number} {r.subject}" for r in tt.itertuples()]) + "\n", encoding="utf-8")
    ev = vectors(emi)
    rv = vectors(ref.rename(columns={"module": "title", "content": "text"}), handbook="ref")
    sim = rv @ ev.T
    titles = emi["title"].map(same_module).to_numpy()
    words = [title_words(t) for t in emi["title"]]
    tv, mv = embed(tt["subject"].tolist()), embed(ref["module"].astype(str).tolist())
    mean = tv.mean(axis=0)
    unit = lambda v: (v - mean) / np.maximum(np.linalg.norm(v - mean, axis=1, keepdims=True), 1e-9)
    tsim = unit(mv) @ unit(tv).T
    terms = blind_terms(metas)
    order = np.random.default_rng(SEED).permutation(len(ref))
    sheet, key = [], []
    for n, i in enumerate(order, 1):
        r = ref.iloc[i]
        allowed = emi_allowed(emi, r["level"])
        near = nearest(sim[i], titles, allowed, NEAREST)
        near = near + title_matches(r["module"], sim[i], titles, words, allowed, near)
        near = [near[k] for k in np.random.default_rng(SEED + n).permutation(len(near))]
        subj = np.random.default_rng(SEED + n).permutation(np.argsort(-tsim[i], kind="mergesort")[:SUBJECTS])
        rid = f"V{n:04d}"
        sheet.append({"row": rid, "module": redact(str(r["module"]), terms), "credit points": float(r["ects"]), "level of the programme": r["level"],
                      "description": redact(str(r["content"])[:MODULE_TEXT], terms) if isinstance(r["content"], str) else "",
                      "EMI modules shown": [{"number": number_of[(r["level"], titles[j])], "title": emi.at[j, "title"],
                                             "ECTS": float(cat.loc[cat["number"] == number_of[(r["level"], titles[j])], "ects"].iloc[0]),
                                             "description": emi_text(emi.at[j, "text"], emi.at[j, "title"])} for j in near],
                      "timetable subjects shown": [f"{tt.at[j, 'number']} {tt.at[j, 'subject']}" for j in subj]})
        key.append({"row": rid, "ref": r["ref"], "candidate": int(r["candidate"]), "level": r["level"], "order": int(r["order"]), "module": r["module"],
                    "ects": float(r["ects"]), "kind": r["kind"], "shown": "; ".join(number_of[(r["level"], titles[j])] for j in near)})
    labs = [x["name"] for x in yaml.safe_load(LABS.read_text(encoding="utf-8"))["labs"]]
    ROWS4.write_text(json.dumps({"labs": labs, "rows": sheet}, indent=1, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame(key).to_csv(KEY4, index=False)
    BLOCKS.mkdir(parents=True, exist_ok=True)
    for f in BLOCKS.glob("block_*.json"):
        f.unlink()
    for b in range(0, len(sheet), BLOCK):
        (BLOCKS / f"block_{b // BLOCK + 1:02d}.json").write_text(json.dumps({"labs": labs, "rows": sheet[b:b + BLOCK]}, indent=1, ensure_ascii=False), encoding="utf-8")
    k = pd.DataFrame(key)
    print(json.dumps({"stamp": stamp, "references": {r: round(m["share listed"], 3) for r, m in metas.items()}, "rows": len(sheet),
                      "rows per reference": k.groupby("ref").size().to_dict(), "blocks": -(-len(sheet) // BLOCK),
                      "catalogue": cat.groupby("level").size().to_dict(), "timetable subjects": len(tt), "redacted terms": len(terms),
                      "files": {p.name: sha(p) for p in (ROWS4, KEY4, CAT_TABLE, TT_TABLE)}}, indent=1, ensure_ascii=False))


# ----------------------------------------------------------------------------------------------------------- marks

def read_marks(k: int, rows_wanted: set[str] | None = None) -> pd.DataFrame:
    """The facts of reader k (all its block files), checked (W1)."""
    files = MARKS(k)
    if not files:
        raise SystemExit(f"no marks of reader {k}")
    m = pd.concat([pd.read_csv(f, keep_default_na=False, dtype=str) for f in files], ignore_index=True)
    m.columns = [c.strip() for c in m.columns]
    cat, tt = set(pd.read_csv(CAT_TABLE)["number"]), set(pd.read_csv(TT_TABLE)["number"])
    errors = []
    if m["row"].duplicated().any():
        errors.append(f"rows marked twice: {sorted(m.loc[m['row'].duplicated(), 'row'])[:5]}")
    for r in m.itertuples():
        cov, covering, topic = r.covered.strip(), [x.strip() for x in re.split(r"[+;, ]+", r.covering) if x.strip()], r.topic.strip()
        if cov not in ("E1", "E2", "no"):
            errors.append(f"{r.row}: covered {cov!r}")
        if cov in ("E1", "E2") and not (1 <= len(covering) <= 2 and all(x in cat for x in covering)):
            errors.append(f"{r.row}: covering {r.covering!r}")
        if topic and topic != "none" and topic.split()[0] not in cat | tt:
            errors.append(f"{r.row}: topic {topic!r}")
        for f in ("parent_field", "lab", "general"):
            if getattr(r, f).strip() not in ("yes", "no"):
                errors.append(f"{r.row}: {f} {getattr(r, f)!r}")
    if rows_wanted is not None and set(m["row"]) != rows_wanted:
        errors.append(f"rows missing: {sorted(rows_wanted - set(m['row']))[:8]}; rows not asked: {sorted(set(m['row']) - rows_wanted)[:8]}")
    if errors:
        raise SystemExit(f"reader {k}: {len(errors)} problems, e.g. " + " | ".join(errors[:12]))
    m["topic"] = [t.strip().split()[0] if t.strip() and t.strip() != "none" else (c.split("+")[0].strip() if v in ("E1", "E2") and c.strip() else "none")
                  for t, c, v in zip(m["topic"], m["covering"], m["covered"])]                                                          # K5
    m["unsure"] = m["unsure"].str.strip().str.lower().isin(["yes", "true", "1", "unsure"])
    return m.set_index("row")


def check(k: str) -> None:
    key = pd.read_csv(KEY4)
    m = read_marks(int(k), set(key["row"]) if k == "1" else None)
    print(json.dumps({"reader": int(k), "rows": len(m), "covered": int(m["covered"].isin(["E1", "E2"]).sum()), "topic named": int((m["topic"] != "none").sum()),
                      "parent field yes": int((m["parent_field"] == "yes").sum()), "lab": int((m["lab"] == "yes").sum()), "general": int((m["general"] == "yes").sum()),
                      "unsure": int(m["unsure"].sum())}, indent=1))


if __name__ == "__main__":
    {"rows": rows, "check": lambda: check(sys.argv[2])}[sys.argv[1]]()
