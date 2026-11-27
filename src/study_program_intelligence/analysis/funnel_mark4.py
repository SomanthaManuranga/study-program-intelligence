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
SEED, BLOCK, CAT_TEXT, MODULE_TEXT = 42, 20, 1500, 1500
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

def read_marks(k, rows_wanted: set[str] | None = None) -> pd.DataFrame:
    """The facts of reader k (all its block files), checked (W1)."""
    files = MARKS(k)
    if not files:
        raise SystemExit(f"no marks of reader {k}")
    m = pd.concat([pd.read_csv(f, keep_default_na=False, dtype=str) for f in files], ignore_index=True)
    m.columns = [c.strip() for c in m.columns]
    for c in ("row", "covered", "covering", "topic", "parent_field", "lab", "general", "unsure"):
        m[c] = m[c].str.strip()
    m["covered"] = m["covered"].replace({"No": "no", "NO": "no"})
    for c in ("parent_field", "lab", "general"):
        m[c] = m[c].str.lower()
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
    m = read_marks(k, set(key["row"]) if k == "1" else None)
    print(json.dumps({"reader": int(k), "rows": len(m), "covered": int(m["covered"].isin(["E1", "E2"]).sum()), "topic named": int((m["topic"] != "none").sum()),
                      "parent field yes": int((m["parent_field"] == "yes").sum()), "lab": int((m["lab"] == "yes").sum()), "general": int((m["general"] == "yes").sum()),
                      "unsure": int(m["unsure"].sum())}, indent=1))


# ------------------------------------------------------------------------------------------- comparison and final facts

TAUGHT = {"bachelor": 165.0, "master": 60.0}                      # feasibility_gate.references.scaling
T_CAP = {"bachelor": 10.0, "master": 5.0}                         # version_4.marking.T_and_X
FAMILY = {"oth26_ba_iki": "KI family", "oth26_ba_ki": "KI family", "oth26_ma_mki": "KI family"}
DRAWN, MAY_DIFFER, NEAR_BAND, PERSON_EXTRA, PERSON_MAX, PAIRS_MAX = 10, 1, 0.10, 5, 40, 120
COMBOS = [("strict", "content"), ("strict", "size"), ("lenient", "content"), ("lenient", "size")]


def numbers(covering: str) -> list[str]:
    return [x for x in re.split(r"[+;, ]+", str(covering)) if x]


def size_pass(covering: str, ects: float, cat_ects: dict) -> bool:
    """K7: the covering modules' catalogue ECTS together are at least the module's ECTS."""
    return sum(cat_ects.get(x, 0.0) for x in numbers(covering)) >= ects - 1e-9


def compared(f: pd.Series, ects: float, cat_ects: dict) -> tuple:
    """K6: the facts compared between readers."""
    cov = f["covered"] in ("E1", "E2")
    return (cov, f["topic"] != "none", f["parent_field"], f["lab"], f["general"], size_pass(f["covering"], ects, cat_ects) if cov else None)


def cat_ects() -> dict:
    c = pd.read_csv(CAT_TABLE)
    return dict(zip(c["number"], c["ects"]))


def differs(a: pd.Series, b: pd.Series, ects: float, ce: dict) -> bool:
    x, y = compared(a, ects, ce), compared(b, ects, ce)
    if x[0] and y[0]:
        return x != y
    return x[:5] != y[:5]


def first_overlap(key: pd.DataFrame, facts: pd.DataFrame) -> dict:
    """Content-reading overlap of every reference from the given facts (for the near-band trigger)."""
    out = {}
    for ref, g in key.assign(cov=facts["covered"].reindex(key["row"]).isin(["E1", "E2"]).to_numpy()
                             | facts["general"].reindex(key["row"]).eq("yes").to_numpy()).groupby("ref"):
        out[ref] = fill(g.reset_index(drop=True), g["cov"].reset_index(drop=True), TAUGHT[g["level"].iloc[0]])["share"]
    return out


def fill(g: pd.DataFrame, flag: pd.Series, taught: float) -> dict:
    from .funnel_feasibility import fill_figures
    return fill_figures(g, flag, taught)


def write_blocks(folder, rows_wanted: list[str], tag: str) -> int:
    sheet = json.loads(ROWS4.read_text(encoding="utf-8"))
    pick = [r for r in sheet["rows"] if r["row"] in set(rows_wanted)]
    folder.mkdir(parents=True, exist_ok=True)
    n0 = len(list(folder.glob("block_*.json")))
    for b in range(0, len(pick), BLOCK):
        (folder / f"block_{tag}{n0 + b // BLOCK + 1:02d}.json").write_text(json.dumps({"labs": sheet["labs"], "rows": pick[b:b + BLOCK]}, indent=1, ensure_ascii=False), encoding="utf-8")
    return len(pick)


def sample() -> None:
    """second_and_third_reader: 10 drawn rows per candidate, every row of a near-band candidate, every unsure row; after
    the second reader's first round, every remaining row of a candidate whose sample failed (W3)."""
    run_stamp()
    key, first, ce = pd.read_csv(KEY4), read_marks(1), cat_ects()
    band = config()["feasibility_gate"]["band"]
    drawn = {c: list(np.random.default_rng(SEED).choice(g["row"].to_numpy(), size=min(DRAWN, len(g)), replace=False))
             for c, g in key.sort_values(["ref", "order"]).groupby(["candidate", "level"])}
    ov = first_overlap(key, first)
    near = {c for c, g in key.groupby(["candidate", "level"]) if any(abs(ov[r] - e) <= NEAR_BAND for r in g["ref"].unique() for e in (band["min"], band["max"]))}
    want = {r for v in drawn.values() for r in v} | set(first.index[first["unsure"]]) | set(key.loc[[c in near for c in zip(key["candidate"], key["level"])], "row"])
    second = read_marks(2) if MARKS(2) else None
    failed = []
    if second is not None:
        e = key.set_index("row")["ects"]
        for c, rws in drawn.items():
            done = [r for r in rws if r in second.index]
            if len(done) == len(rws) and sum(differs(first.loc[r], second.loc[r], e[r], ce) for r in rws) > MAY_DIFFER:
                failed.append(c)
                want |= set(key.loc[(key["candidate"] == c[0]) & (key["level"] == c[1]), "row"])
        want -= set(second.index)
    n = write_blocks(REPORTS / "v4_rows2", sorted(want), "r")
    (INTERIM / "funnel4_sample.json").write_text(json.dumps({"drawn": {f"{c[0]} {c[1]}": v for c, v in drawn.items()}, "near band": sorted(f"{c[0]} {c[1]}" for c in near),
                                                             "first overlaps": {k: round(v, 3) for k, v in ov.items()}, "sample failed": [f"{c[0]} {c[1]}" for c in failed]}, indent=1), encoding="utf-8")
    print(json.dumps({"rows for the second reader now": n, "near band": sorted(f"{c[0]} {c[1]}" for c in near), "sample failed": [f"{c[0]} {c[1]}" for c in failed],
                      "unsure rows": int(first["unsure"].sum())}, indent=1))


def third() -> None:
    """W4: every row on which the first two readers differ in a fact of K6, for a blind third reader."""
    run_stamp()
    key, first, second, ce = pd.read_csv(KEY4), read_marks(1), read_marks(2), cat_ects()
    e = key.set_index("row")["ects"]
    rows_ = sorted(r for r in second.index if differs(first.loc[r], second.loc[r], e[r], ce))
    done = set(read_marks(3).index) if MARKS(3) else set()
    n = write_blocks(REPORTS / "v4_rows3", [r for r in rows_ if r not in done], "t")
    print(json.dumps({"marked by both": len(second), "differ": len(rows_), "new rows for the third reader": n}, indent=1))


def final_facts() -> pd.DataFrame:
    """final_facts: the first reader's where the second agreed or did not look; the third reader's where they differ.
    Then the consistency pass, then the persons, each only on its own rows."""
    key, first, ce = pd.read_csv(KEY4).set_index("row"), read_marks(1), cat_ects()
    second = read_marks(2) if MARKS(2) else pd.DataFrame(columns=first.columns)
    third_ = read_marks(3) if MARKS(3) else pd.DataFrame(columns=first.columns)
    out, basis = [], []
    for r in key.index:
        if r not in second.index:
            out.append(first.loc[r]), basis.append("first reader alone")
        elif not differs(first.loc[r], second.loc[r], key.at[r, "ects"], ce):
            out.append(first.loc[r]), basis.append("first two agree")
        elif r in third_.index:
            out.append(third_.loc[r]), basis.append("third reader")
        else:
            raise SystemExit(f"row {r}: the first two readers differ and no third reader has marked it")
    f = pd.DataFrame(out, index=key.index)
    f["basis"] = basis
    if MARKS("c"):
        c = read_marks("c")
        f.loc[c.index, FACTS[:-1]] = c[FACTS[:-1]]
        f.loc[c.index, "basis"] = f.loc[c.index, "basis"] + "; consistency pass"
    if MARKS("p"):
        p = read_marks("p")
        f.loc[p.index, FACTS[:-1]] = p[FACTS[:-1]]
        f.loc[p.index, "basis"] = "persons"
    return key.join(f[[c for c in f.columns if c not in key.columns]])


def consistency() -> None:
    """K8: pairs of rows from different references with equal normalised titles, or sharing a title word with a topic
    on one side and none on the other; at most 120 pairs, equal titles first."""
    from .funnel_merge import normaliser
    run_stamp()
    f = final_facts().reset_index()
    norm = normaliser(config()["version_4"]["title_merge"])
    f["nt"], f["tw"] = f["module"].map(norm), f["module"].map(title_words)
    pairs = []
    for i in range(len(f)):
        for j in range(i + 1, len(f)):
            a, b = f.iloc[i], f.iloc[j]
            if a["ref"] == b["ref"]:
                continue
            if a["nt"] and a["nt"] == b["nt"]:
                pairs.append((0, a["row"], b["row"]))
            elif a["tw"] & b["tw"] and ((a["topic"] == "none") != (b["topic"] == "none")) and a["covered"] == "no" and b["covered"] == "no":
                pairs.append((1, a["row"], b["row"]))
    pairs = sorted(pairs)[:PAIRS_MAX]
    sheet = {r["row"]: r for r in json.loads(ROWS4.read_text(encoding="utf-8"))["rows"]}
    labs = json.loads(ROWS4.read_text(encoding="utf-8"))["labs"]
    folder = REPORTS / "v4_pairs"
    folder.mkdir(parents=True, exist_ok=True)
    for x in folder.glob("block_*.json"):
        x.unlink()
    out = [{"pair": f"P{k + 1:03d}", "rows": [sheet[a], sheet[b]]} for k, (_, a, b) in enumerate(pairs)]
    for b in range(0, len(out), 10):
        (folder / f"block_c{b // 10 + 1:02d}.json").write_text(json.dumps({"labs": labs, "pairs": out[b:b + 10]}, indent=1, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame([{"pair": f"P{k + 1:03d}", "kind": "equal title" if t == 0 else "shared word, topic on one side", "row a": a, "row b": b} for k, (t, a, b) in enumerate(pairs)]).to_csv(INTERIM / "funnel4_pairs.csv", index=False)
    print(json.dumps({"pairs": len(pairs), "equal titles": sum(1 for p in pairs if p[0] == 0), "blocks": -(-len(out) // 10)}, indent=1))


# ------------------------------------------------------------------------------------------------------- verdicts

def readings(f: pd.DataFrame, mark: str, size: str, ce: dict) -> pd.DataFrame:
    """One combination: per row covered / N / new / lab / general, and whether it counts."""
    cov = f["covered"].isin(["E1", "E2"])
    if size == "size":
        cov = cov & [size_pass(c, e, ce) for c, e in zip(f["covering"], f["ects"])]
    gen, lab = f["general"].eq("yes"), f["lab"].eq("yes")
    topic = f["topic"].ne("none") | (f["covered"].isin(["E1", "E2"]) & ~cov)            # a row covered by content only has its covering modules as topic
    n = ~cov & ~gen & ~lab & (topic | (f["parent_field"].eq("yes") if mark == "lenient" else False))
    new = ~cov & ~gen & ~lab & ~n
    return pd.DataFrame({"covered": cov | (gen if size == "content" else False), "N": n, "new": new, "lab": lab, "general": gen,
                         "counts": ~gen if size == "size" else pd.Series(True, index=f.index)}, index=f.index)


def one_programme(g: pd.DataFrame, cov: pd.Series, gen: pd.Series, taught: float, cat: pd.DataFrame) -> tuple[float, str]:
    progs_of = {n: {FAMILY.get(p, p) for p in str(ps).split("; ")} for n, ps in zip(cat["number"], cat["programmes"])}
    allp = sorted({p for v in progs_of.values() for p in v if "_ba_" in p})
    best, name = 0.0, ""
    for p in allp:
        hit = pd.Series([bool(c and not gn and any(p in progs_of.get(x, set()) for x in numbers(cv))) for c, gn, cv in zip(cov, gen, g["covering"])], index=g.index)
        s = fill(g, hit, taught)["share"]
        if np.isfinite(s) and s > best:
            best, name = s, p
    return best, name


def verdict() -> None:
    stamp, rules = run_stamp(), config()
    band, v4 = rules["feasibility_gate"]["band"], rules["version_4"]
    f, ce, cat = final_facts(), cat_ects(), pd.read_csv(CAT_TABLE)
    chk = pd.read_csv(LIST4).set_index(["candidate", "level"])
    rows_, cands = [], []
    for (ref), g in f.groupby("ref"):
        g = g.reset_index()
        lv = g["level"].iloc[0]
        for mark, size in COMBOS:
            r = readings(g, mark, size, ce)
            gg = g[r["counts"]].reset_index(drop=True)
            rr = r[r["counts"]].reset_index(drop=True)
            gen_ects = float(g.loc[r["general"] & (g["kind"] == "compulsory"), "ects"].sum()) if size == "size" else 0.0
            taught = TAUGHT[lv] - gen_ects
            ov = fill(gg, rr["covered"], taught)
            sh = {k: fill(gg, rr[k], taught)["share"] for k in ("N", "new", "lab")}
            new_ects = (1 - ov["share"]) * taught
            n_e, new_e = sh["N"] * taught, (sh["new"] + sh["lab"]) * taught
            t_e = min(sh["new"] * taught, T_CAP[lv])
            x_e = sh["new"] * taught - t_e + sh["lab"] * taught
            op, opn = one_programme(gg, rr["covered"], gg["general"].eq("yes"), taught, cat)
            rows_.append({"ref": ref, "candidate": int(g["candidate"].iloc[0]), "level": lv, "marking": mark, "size": size, "rows": len(g), "counted ECTS": ov["counted"],
                          "taught base": taught, "overlap": ov["share"], "overlap (best electives)": ov["best"], "overlap (worst electives)": ov["worst"],
                          "one-programme share": op, "programme": opn, "N ECTS": n_e, "T ECTS": t_e, "X ECTS": x_e, "new teaching ECTS": new_ects,
                          "professor-equivalents": new_ects * 0.8 / 36, "lab rows": int(r["lab"].sum()), "general ECTS": float(g.loc[r["general"], "ects"].sum())})
    R = pd.DataFrame(rows_)
    for (c, lv), g in R.groupby(["candidate", "level"]):
        out = {"candidate": c, "level": lv, "name": chk.at[(c, lv), "name"], "control": bool(chk.at[(c, lv), "control"]), "references": g["ref"].nunique()}
        for mark, size in COMBOS:
            h = g[(g["marking"] == mark) & (g["size"] == size)]
            ok = bool((h["overlap"] >= band["min"]).all() and (h["one-programme share"] <= band["max"]).all() and (h["lab rows"] == 0).all() and (h["X ECTS"] <= 1e-9).all())
            tag = f"{mark} x {size}"
            out[f"passes {tag}"] = ok
            out[f"overlap {tag}"] = f"{h['overlap'].min():.3f}-{h['overlap'].max():.3f}"
            out[f"X {tag}"] = round(float(h["X ECTS"].max()), 1)
        firm = out["passes strict x size"]
        cond = [t for t in ("strict x content", "lenient x size", "lenient x content") if out[f"passes {t}"]]
        out["verdict"] = "firm existing-resources passer" if firm else (f"conditional passer (needs {cond[0]})" if cond else "fail")
        cands.append(out)
    C = pd.DataFrame(cands)
    R.to_csv(INTERIM / "funnel4_gate_references.csv", index=False)
    C.to_csv(INTERIM / "funnel4_gate.csv", index=False)
    basis = f["basis"].value_counts().to_dict()
    res = {"stamp": stamp, "rows": len(f), "basis": {k: int(v) for k, v in basis.items()},
           "verdicts": {f"{r['name'][:45]} ({r['level']})": r["verdict"] for r in cands},
           "files": {p.name: sha(p) for p in (INTERIM / "funnel4_gate_references.csv", INTERIM / "funnel4_gate.csv")}}
    (INTERIM / "funnel4_step7.json").write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False))


# --------------------------------------------------------------------------------------------------- person sheet

def person() -> None:
    """K9, version_4.person_check: rows new under strict x size or lab, plus 5 covered or N rows per candidate, for the
    candidates in the band under strict x content; at most 40 rows, drawn in proportion."""
    run_stamp()
    f, ce = final_facts(), cat_ects()
    R = pd.read_csv(INTERIM / "funnel4_gate_references.csv")
    band = config()["feasibility_gate"]["band"]
    sc = R[(R["marking"] == "strict") & (R["size"] == "content")]
    inband = {(c, lv) for (c, lv), h in sc.groupby(["candidate", "level"]) if ((h["overlap"] >= band["min"]) & (h["one-programme share"] <= band["max"])).any()}
    pick = {}
    for c in sorted(inband):
        g = f[(f["candidate"] == c[0]) & (f["level"] == c[1])]
        r = readings(g, "strict", "size", ce)
        deciding = list(g.index[r["new"] | r["lab"]])
        other = list(g.index[r["covered"] | r["N"]])
        extra = list(np.random.default_rng(SEED).choice(sorted(other), size=min(PERSON_EXTRA, len(other)), replace=False)) if other else []
        pick[c] = sorted(set(deciding) | set(extra))
    total = sum(len(v) for v in pick.values())
    if total > PERSON_MAX:
        rng = np.random.default_rng(SEED)
        pick = {c: sorted(rng.choice(v, size=max(1, round(PERSON_MAX * len(v) / total)), replace=False)) for c, v in pick.items()}
    rows_ = [r for v in pick.values() for r in v]
    rows_ = [rows_[i] for i in np.random.default_rng(SEED).permutation(len(rows_))]
    sheet = {r["row"]: r for r in json.loads(ROWS4.read_text(encoding="utf-8"))["rows"]}
    lines = ["# Person check: module rows (Soma and the second team member, each alone)", "",
             "For every row, record the facts of docs/funnel_marking_rules.md (version 4) in docs/funnel4_marks_p_1.csv "
             "(columns row,covered,covering,topic,parent_field,lab,general,unsure,reason). The EMI catalogue is reports/funnel2/v4_emi_catalogue_bachelor.md. "
             "You do not see what the AI readers decided. Settle differences between the two of you together afterwards.", ""]
    for rid in rows_:
        s = sheet[rid]
        lines += [f"## {rid}: {s['module']} ({s['credit points']:g} ECTS)", "", "| The module | EMI modules shown (number, title, ECTS) |", "|---|---|",
                  f"| {s['description'][:1500].replace('|', '/').replace(chr(10), ' ')} | " + "<br>".join(f"{e['number']} {e['title']} ({e['ECTS']:g})" for e in s["EMI modules shown"]) +
                  "<br>Timetable: " + "; ".join(s["timetable subjects shown"]) + " |", "",
                  "Question: covered by EMI (E1/E2/no, which)? If not, which EMI module or timetable subject has its main topic (or none)? Parent field EMI? Lab? General?", ""]
    (REPORTS / "v4_person_sheet.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"candidates in the band (strict x content)": [f"{c[0]} {c[1]}" for c in sorted(inband)], "rows qualifying before the cut": total, "rows on the sheet": len(rows_)}, indent=1))


if __name__ == "__main__":
    {"rows": rows, "check": lambda: check(sys.argv[2]), "sample": sample, "third": third, "consistency": consistency,
     "verdict": verdict, "person": person}[sys.argv[1]]()
