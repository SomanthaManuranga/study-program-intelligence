"""Funnel step 7c: can EMI teach it with what it has? (configs/funnel.yaml: feasibility_gate; docs/criteria_funnel_step7.md)

Run from the repository root, from committed code on a clean tree, after the reference tables are in
data/interim/funnel2_refs/ (analysis.funnel_refs):

    python -m study_program_intelligence.analysis.funnel_feasibility rows      # the blind rows for the first marking
    python -m study_program_intelligence.analysis.funnel_feasibility sample    # the rows for the second reviewer
    python -m study_program_intelligence.analysis.funnel_feasibility verdict   # overlap, new teaching, verdicts

rows: every counted module of every complete reference with the 3 most similar EMI modules (funnel_modules.vectors)
and the 3 nearest timetable subjects, shuffled, without candidate, institution, programme or similarity value. The
key stays in data/interim. Marks are read from docs/funnel_module_marks_1.csv (first reviewer), _2.csv (second,
blind to the first) and _3.csv (third reader, only for candidates whose sample failed).
Outputs: data/interim/funnel2_rows.json, funnel2_rows_key.csv, funnel2_rows_sample.json, funnel2_gate.csv,
funnel2_gate_references.csv, funnel2_step7.json; reports/funnel2/step7_gate.md.
"""

from __future__ import annotations

import json
import re
import sys

import numpy as np
import pandas as pd
import yaml

from .funnel_common import INTERIM, REPO_ROOT, REPORTS, config, md_table, run_stamp
from .funnel_modules import EMI_MODULES, norm_title, vectors
from .funnel_refs import LEFT_OUT, TABLES
from .funnel_shortlist import ORDER
from .funnel_types import sha
from .module_gaps import embed

ROWS, KEY, SAMPLE = INTERIM / "funnel2_rows.json", INTERIM / "funnel2_rows_key.csv", INTERIM / "funnel2_rows_sample.json"
GATE, GATE_REFS, STEP7 = INTERIM / "funnel2_gate.csv", INTERIM / "funnel2_gate_references.csv", INTERIM / "funnel2_step7.json"
MARKS = {k: REPO_ROOT / "docs" / f"funnel_module_marks_{k}.csv" for k in (1, 2, 3)}
TIMETABLE = INTERIM / "timetable_subjects.csv"
COHERENCE = REPO_ROOT / "docs" / "funnel_type_coherence.csv"
WALK = INTERIM / "funnel2_gate_walk.csv"
GATE_RULE = (6, 3, 20)                                            # shortlist.gate_list: eligible, per level, tried
LABS = REPO_ROOT / "configs" / "emi_labs.yaml"
TAUGHT = {"bachelor": 165.0, "master": 60.0}                      # references.scaling
T_CAP = {"bachelor": 10.0, "master": 5.0}                         # hand_check.computed_T_and_X
FAMILY = {"oth26_ba_iki": "KI family", "oth26_ba_ki": "KI family", "oth26_ma_mki": "KI family"}       # one_programme.share
COVERED, VERDICTS = ("E1", "E2"), ("E1", "E2", "N", "new", "lab")
SEED, NEAREST, DRAWN, MAY_DIFFER = 42, 3, 10, 1                   # hand_check: rows, sample_check, sample_pass
SWS_PER_ECTS, SWS_A_YEAR = 0.8, 36.0                              # professor_equivalents
SINGLE_WIDEN = 0.10                                               # references.one_only
EMI_TEXT, MODULE_TEXT = 1200, 1500                                # characters of text shown to a marker


def subject_name(s: str) -> str:
    """A timetable subject without its form in brackets ("Informatik 1 (Vorlesung)" -> "Informatik 1")."""
    return re.sub(r"\s*\((vorlesung|praktikum|übung|uebung|seminar|seminaristischer unterricht|su|vl|pr|ü|labor)[^)]*\)\s*$", "", str(s), flags=re.I).strip()


ACRONYMS = ("HTWK", "HKA", "THD", "OTH", "HSMW", "HTW", "THM", "THB", "HS", "TH", "FH")     # short forms of institutions, matched as whole upper-case words


def blind_terms(metas: dict) -> list[str]:
    """Names that would show where a module comes from: every reference's institution, the city of its offer, and the
    institution's distinctive words (a place or a name of four letters or more that is not a common word)."""
    tries = pd.read_csv(INTERIM / "funnel2_reference_tries.csv")
    common = {"hochschule", "technische", "university", "universität", "angewandte", "wissenschaften", "fachhochschule", "für", "und", "des", "der", "die", "applied", "sciences", "technology", "technik", "wirtschaft", "kultur", "gestaltung", "of", "and"}
    out = set()
    for m in metas.values():
        out.add(m["institution"])
        out |= {w for w in re.findall(r"[A-ZÄÖÜ][\wäöüß-]{3,}", m["institution"]) if w.lower() not in common}
        city = tries.loc[tries["programme_id"].astype(str) == str(m.get("programme_id")), "city"]
        if len(city):
            out.add(re.split(r"[,(]", str(city.iloc[0]))[0].strip())
    return sorted(out, key=len, reverse=True)


def redact(text: str, terms: list[str]) -> str:
    """Replaces the terms (whole words, any case) and the acronyms (whole upper-case words) by "[university]"."""
    for t in terms:
        text = re.sub(rf"(?<![\wäöüß]){re.escape(t)}(?![\wäöüß])", "[university]", text, flags=re.I)
    return re.sub(rf"\b({'|'.join(ACRONYMS)})\b(?=[\s.,;:)-]|$)", "[university]", text)


def complete(m: pd.DataFrame, meta: dict, share: float) -> tuple[bool, float]:
    """references.complete: modules for at least 80 % of the programme's ECTS, thesis included; of the listed electives
    only the ECTS a student must take count."""
    e = pd.to_numeric(m["ects"], errors="coerce")
    listed = float(e[m["kind"] != "elective"].sum()) + min(float(e[m["kind"] == "elective"].sum()), float(meta.get("elective_ects_required") or 0.0))
    return bool(listed / float(meta["programme_ects"]) >= share and e.notna().all()), listed / float(meta["programme_ects"])


def references(share: float = 0.8) -> tuple[pd.DataFrame, dict]:
    """All module tables of the collectors, with their candidate; counted rows are compulsory and elective modules."""
    frames, metas = [], {}
    for f in sorted(TABLES.glob("*_[ab].json")):
        meta = json.loads(f.read_text(encoding="utf-8"))
        csv = f.with_suffix(".csv")
        if not csv.exists():
            continue
        m = pd.read_csv(csv)
        ok, listed = complete(m, meta, share)
        metas[f.stem] = {**meta, "complete": ok, "share listed": listed}
        if ok:
            m = m[~m["kind"].isin(LEFT_OUT)].reset_index(drop=True)
            frames.append(m.assign(ref=f.stem, type=int(meta["type"]), level=meta["level"], order=np.arange(len(m)), ects=pd.to_numeric(m["ects"])))
    return (pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()), metas


def emi_allowed(emi: pd.DataFrame, level: str) -> np.ndarray:
    return emi["level"].eq("BA").to_numpy() if level == "bachelor" else np.ones(len(emi), bool)       # feasibility_gate.emi_modules


def nearest(sim: np.ndarray, titles: np.ndarray, allowed: np.ndarray, n: int = NEAREST) -> list[int]:
    """The n most similar allowed EMI modules with different normalised titles (a module listed in several handbooks is shown once)."""
    out, seen = [], set()
    for j in np.argsort(-sim, kind="mergesort"):
        if allowed[j] and titles[j] not in seen:
            out.append(int(j))
            seen.add(titles[j])
            if len(out) == n:
                break
    return out


def gate_order() -> pd.DataFrame:
    """The gate order of Step 7a with the number of fitted members of each type."""
    from .funnel_types import TYPES
    order = pd.read_csv(ORDER, float_precision="round_trip")
    return order.assign(members=order["type"].map(pd.read_csv(TYPES).set_index("type")["members"]))


def rows() -> None:
    stamp, rules = run_stamp(), config()
    ref, metas = references(0.8)
    order = gate_order()
    w = walk(order, metas, not_candidates(order), GATE_RULE)
    w.to_csv(WALK, index=False)
    if not w.empty and w["status"].iloc[-1] in ("not yet tried", "waiting"):
        print(w.to_string())
        raise SystemExit("the walk down the gate list is not finished")
    keep = {(int(t), lv) for t, lv, st in zip(w["type"], w["level"], w["status"]) if st == "eligible"}
    ref = ref[[(int(t), lv) in keep for t, lv in zip(ref["type"], ref["level"])]].reset_index(drop=True)
    print(w.to_string())
    emi = pd.read_csv(EMI_MODULES, low_memory=False)
    ev = vectors(emi)
    rv = vectors(ref.rename(columns={"module": "title", "content": "text"}), handbook="ref")
    sim = rv @ ev.T
    titles = emi["title"].map(norm_title).to_numpy()
    tt = sorted({subject_name(s) for s in pd.read_csv(TIMETABLE)["subject"].dropna()} - {""})
    tv, mv = embed(tt), embed(ref["module"].astype(str).tolist())
    mean = tv.mean(axis=0)
    unit = lambda v: (v - mean) / np.maximum(np.linalg.norm(v - mean, axis=1, keepdims=True), 1e-9)
    tsim = unit(mv) @ unit(tv).T
    threshold = float(rules["feasibility_gate"]["covered_threshold"])
    order = np.random.default_rng(SEED).permutation(len(ref))
    terms = [t for t in blind_terms({k: v for k, v in metas.items() if k in set(ref["ref"])}) if t]
    sheet, key = [], []
    for n, i in enumerate(order, 1):
        r = ref.iloc[i]
        near = nearest(sim[i], titles, emi_allowed(emi, r["level"]))
        show = np.random.default_rng(SEED + n).permutation(len(near))                 # shuffled order of the 3 EMI modules
        near = [near[k] for k in show]
        best = max(sim[i][emi_allowed(emi, r["level"])])
        sheet.append({"row": f"R{n:04d}", "module": redact(str(r["module"]), terms), "credit points": float(r["ects"]), "level of the programme": r["level"],
                      "description": redact(str(r["content"])[:MODULE_TEXT], terms) if isinstance(r["content"], str) else "",
                      "EMI modules": [{"number": k + 1, "title": emi.at[j, "title"], "level": {"BA": "bachelor", "MA": "master"}.get(emi.at[j, "level"], emi.at[j, "level"]),
                                       "description": str(emi.at[j, "text"])[:EMI_TEXT]} for k, j in enumerate(near)],
                      "timetable subjects": [tt[j] for j in np.random.default_rng(SEED + n).permutation(np.argsort(-tsim[i], kind="mergesort")[:NEAREST])]})
        key.append({"row": f"R{n:04d}", "ref": r["ref"], "type": r["type"], "level": r["level"], "order": r["order"], "module": r["module"], "ects": r["ects"], "kind": r["kind"],
                    **{f"emi {k + 1}": emi.at[j, "module_id"] for k, j in enumerate(near)}, **{f"emi {k + 1} programme": emi.at[j, "programme_id"] for k, j in enumerate(near)},
                    **{f"similarity {k + 1}": float(sim[i, j]) for k, j in enumerate(near)}, "best similarity": float(best), "automatic: covered": bool(best >= threshold)})
    ROWS.write_text(json.dumps({"labs": [x["name"] for x in yaml.safe_load(LABS.read_text(encoding="utf-8"))["labs"]], "rows": sheet}, indent=1, ensure_ascii=False), encoding="utf-8")
    pd.DataFrame(key).to_csv(KEY, index=False)
    print(json.dumps({"stamp": stamp, "references": {k: {"complete": v["complete"], "share listed": round(v["share listed"], 3)} for k, v in metas.items()},
                      "rows": len(sheet), "rows per reference": pd.DataFrame(key).groupby("ref").size().to_dict(), "rows_hash": sha(ROWS), "key_hash": sha(KEY)}, indent=1))


def read_marks(k: int) -> pd.DataFrame:
    m = pd.read_csv(MARKS[k], keep_default_na=False)
    if not m["verdict"].isin(VERDICTS).all() or m["row"].duplicated().any():
        raise SystemExit(f"{MARKS[k].name}: unknown verdict or a row marked twice")
    return m.assign(unsure=m["unsure"].astype(str).str.lower().isin(["true", "1", "yes", "unsure"])).set_index("row")


def drawn_rows(key: pd.DataFrame) -> dict[tuple[int, str], list[str]]:
    """hand_check.sample_check: 10 rows per candidate by default_rng(42).choice from its rows sorted by reference and module order."""
    out = {}
    for cand, g in key.sort_values(["ref", "order"]).groupby(["type", "level"], sort=True):
        out[cand] = list(np.random.default_rng(SEED).choice(g["row"].to_numpy(), size=min(DRAWN, len(g)), replace=False))
    return out


def sample() -> None:
    key, first = pd.read_csv(KEY), read_marks(1)
    if set(key["row"]) != set(first.index):
        raise SystemExit("the first marking does not cover exactly the rows of the key")
    drawn = drawn_rows(key)
    want = sorted({r for v in drawn.values() for r in v} | set(first.index[first["unsure"]]))
    sheet = json.loads(ROWS.read_text(encoding="utf-8"))
    sheet["rows"] = [r for r in sheet["rows"] if r["row"] in set(want)]
    SAMPLE.write_text(json.dumps(sheet, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"drawn": {f"{t} {lv}": v for (t, lv), v in drawn.items()}, "unsure rows": int(first["unsure"].sum()), "rows for the second reviewer": len(want)}, indent=1))


def final_marks(key: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """hand_check.final_verdict, sample_pass. Returns the key with the final verdict of every row and, per candidate, the result of the sample."""
    first, second = read_marks(1), read_marks(2)
    third = read_marks(3) if MARKS[3].exists() else pd.DataFrame(columns=first.columns)
    cov = lambda v: v in COVERED
    k = key.set_index("row")
    k["first"], k["first unsure"], k["which"] = first["verdict"].reindex(k.index), first["unsure"].reindex(k.index), first["which"].reindex(k.index)
    k["second"], k["second which"], k["third"] = second["verdict"].reindex(k.index), second["which"].reindex(k.index), third["verdict"].reindex(k.index) if len(third) else np.nan
    info = {}
    for cand, rws in drawn_rows(key).items():
        differ = [r for r in rws if cov(k.at[r, "first"]) != cov(k.at[r, "second"])]
        all_rows = k.index[(k["type"] == cand[0]) & (k["level"] == cand[1])]
        failed = len(differ) > MAY_DIFFER
        if failed and k.loc[all_rows, "second"].isna().any():
            raise SystemExit(f"candidate {cand}: the sample failed ({len(differ)} of {len(rws)}); the second reviewer has to mark all its rows")
        info[cand] = {"drawn": len(rws), "differ": len(differ), "sample failed": failed, "rows": len(all_rows), "rows the second reviewer marked": int(k.loc[all_rows, "second"].notna().sum())}
    final, basis = [], []
    for r in k.itertuples():
        if not isinstance(r.second, str):
            final.append(r.first), basis.append("first reviewer alone")
        elif cov(r.first) == cov(r.second):
            final.append(r.first), basis.append("both reviewers")
        elif isinstance(r.third, str):
            final.append(r.third), basis.append("third reader")
        else:
            final.append(r.second if cov(r.first) else r.first), basis.append("reviewers differ: not covered")
    k["final"], k["basis"] = final, basis
    k["which final"] = third["which"].reindex(k.index).where(k["basis"] == "third reader", k["which"]) if len(third) else k["which"]
    return k.reset_index(), info


def fill_figures(g: pd.DataFrame, flag: pd.Series, taught: float) -> dict:
    """references.electives for one reference and one yes/no property of its rows: the share of the counted ECTS with the
    property when the ECTS missing up to the taught ECTS are filled with electives, split like all listed electives;
    also with the electives that have the property first and last."""
    comp, elec = g[g["kind"] == "compulsory"], g[g["kind"] == "elective"]
    c, cf = float(comp["ects"].sum()), float(comp.loc[flag[comp.index], "ects"].sum())
    e, ef = float(elec["ects"].sum()), float(elec.loc[flag[elec.index], "ects"].sum())
    fill = min(max(taught - c, 0.0), e)
    counted = c + fill
    if counted <= 0:
        return {"counted": 0.0, "fill": 0.0, "share": np.nan, "best": np.nan, "worst": np.nan}
    return {"counted": counted, "fill": fill, "share": (cf + (fill * ef / e if e else 0.0)) / counted,
            "best": (cf + min(fill, ef)) / counted, "worst": (cf + max(fill - (e - ef), 0.0)) / counted}


def one_programme(g: pd.DataFrame, emi: pd.DataFrame, level: str, taught: float) -> tuple[float, str]:
    """one_programme.share: the largest share of counted ECTS covered by the modules of one OTH programme of the level."""
    lv = "BA" if level == "bachelor" else "MA"
    prog_of = emi[emi["level"] == lv].assign(t=lambda x: x["title"].map(norm_title)).groupby("t")["programme_id"].agg(set).to_dict()
    level_of = emi.drop_duplicates("programme_id").set_index("programme_id")["level"].to_dict()
    best, name = 0.0, ""
    progs = sorted({FAMILY.get(p, p) for p in emi.loc[emi["level"] == lv, "programme_id"]})
    for p in progs:
        hit = pd.Series([bool(r["final"] in COVERED and p in {FAMILY.get(x, x) for x in ({r["confirmed programme"]} | prog_of.get(r["confirmed title"], set())) if level_of.get(x) == lv})
                         for _, r in g.iterrows()], index=g.index)
        s = fill_figures(g, hit, taught)["share"]
        if np.isfinite(s) and s > best:
            best, name = s, p
    return best, name


def not_candidates(order: pd.DataFrame) -> dict[tuple[int, str], str]:
    """screen.type_coherence.before_the_gate for the candidates of the gate order: a mixed type whose reading already
    showed every fitted member (all titles read) and found under 80 % in the main kind is "mixed, not a candidate".
    A mixed type with members left unread would need a full reading first; the walk stops there."""
    coh = pd.read_csv(COHERENCE).set_index("type")
    out = {}
    for r in order.itertuples():
        t = int(r.type)
        if t in coh.index and bool(coh.at[t, "mixed"]):
            members = int(r._asdict().get("members", 0) or 0)
            shown, largest = int(coh.at[t, "shown"]), int(coh.at[t, "largest"])
            out[(t, r.level)] = (f"mixed type, all {shown} titles read, {largest} in the main kind (below 80 %)" if members and shown >= members and largest / shown < 0.8
                                 else "mixed type: needs the full reading before it can take a slot")
    return out


def walk(order: pd.DataFrame, metas: dict, not_a_candidate: dict[tuple[int, str], str], rule: tuple) -> pd.DataFrame:
    """shortlist.gate_list: down the gate order; a candidate is tried when its references were looked for; it is eligible
    with at least one complete reference; stop when 6 are eligible or 20 were tried; once a level has 3 eligible, its
    later candidates are skipped without looking for references and are not counted. A mixed type read in full and
    found mixed takes no slot (screen.type_coherence.before_the_gate)."""
    eligible_max, per_level, tried_max = rule
    out, n_tried, n_eligible, by_level = [], 0, 0, {"bachelor": 0, "master": 0}
    for r in order.itertuples():
        cand = (int(r.type), r.level)
        if n_eligible >= eligible_max or n_tried >= tried_max:
            break
        if cand in not_a_candidate:
            if not_a_candidate[cand].startswith("mixed type: needs"):
                out.append({"gate order": r._1, "type": cand[0], "level": cand[1], "status": "waiting", "reason": not_a_candidate[cand]})
                break
            out.append({"gate order": r._1, "type": cand[0], "level": cand[1], "status": "not a candidate", "reason": not_a_candidate[cand]})
            continue
        if by_level[cand[1]] >= per_level:
            out.append({"gate order": r._1, "type": cand[0], "level": cand[1], "status": "skipped", "reason": f"{per_level} {cand[1]} candidates are eligible already"})
            continue
        refs = {k: v for k, v in metas.items() if (int(v["type"]), v["level"]) == cand}
        if not (TABLES / f"tries_{r._1}.json").exists():
            out.append({"gate order": r._1, "type": cand[0], "level": cand[1], "status": "not yet tried", "reason": "no record of the references being looked for"})
            break
        n_tried += 1
        ok = [k for k, v in refs.items() if v["complete"]]
        if ok:
            n_eligible += 1
            by_level[cand[1]] += 1
            out.append({"gate order": r._1, "type": cand[0], "level": cand[1], "status": "eligible", "reason": f"{len(ok)} complete reference(s): {', '.join(sorted(ok))}"})
        else:
            out.append({"gate order": r._1, "type": cand[0], "level": cand[1], "status": "tried, not eligible", "reason": "no complete reference"})
    return pd.DataFrame(out)


def verdict() -> None:
    stamp, rules = run_stamp(), config()
    gate = rules["feasibility_gate"]
    lo, hi, one_max = float(gate["band"]["min"]), float(gate["band"]["max"]), float(gate["one_programme"]["max"])
    key = pd.read_csv(KEY)
    k, info = final_marks(key)
    emi = pd.read_csv(EMI_MODULES, low_memory=False).set_index("module_id", drop=False)
    which = pd.to_numeric(k["which final"], errors="coerce")
    conf = [k.at[i, f"emi {int(w)}"] if np.isfinite(w) and 1 <= w <= NEAREST else None for i, w in zip(k.index, which)]
    k["confirmed module"] = conf
    k["confirmed programme"] = [emi.at[c, "programme_id"] if c in emi.index else "" for c in conf]
    k["confirmed title"] = [norm_title(emi.at[c, "title"]) if c in emi.index else "" for c in conf]
    tt = {norm_title(s) for s in pd.read_csv(TIMETABLE)["subject"].dropna().map(lambda x: re.sub(r"\(.*?\)", "", str(x)))}
    k["in the timetable"] = [t != "" and t in tt for t in k["confirmed title"]]
    _, metas = references(0.8)
    refs = []
    for ref, g in k.groupby("ref", sort=True):
        level, taught = g["level"].iloc[0], TAUGHT[g["level"].iloc[0]]
        is_ = lambda *v: g["final"].isin(v)
        ov, auto = fill_figures(g, is_(*COVERED), taught), fill_figures(g, g["automatic: covered"].astype(bool), taught)
        n, new, lab = (fill_figures(g, is_(x), taught)["share"] for x in ("N", "new", "lab"))
        new_ects = (1 - ov["share"]) * taught
        t_ects = min(new * taught, T_CAP[level])
        x_ects = new * taught - t_ects + lab * taught
        share1, prog1 = one_programme(g, emi.reset_index(drop=True), level, taught)
        cov_ects = float(g.loc[is_(*COVERED), "ects"].sum())
        alone = float(g.loc[is_(*COVERED) & (g["basis"] == "first reviewer alone"), "ects"].sum())
        ok = bool(ov["share"] >= lo and share1 <= one_max and lab == 0)
        why = [w for w, bad in (("too little overlap", ov["share"] < lo), ("too much from one programme", share1 > one_max), ("lab", lab > 0)) if bad]
        refs.append({"ref": ref, "type": int(g["type"].iloc[0]), "level": level, "institution": metas[ref]["institution"], "programme": metas[ref]["title"],
                     "modules": len(g), "counted ECTS": ov["counted"], "elective fill ECTS": ov["fill"], "overlap": ov["share"], "overlap (best-covered electives first)": ov["best"],
                     "overlap (worst-covered electives first)": ov["worst"], "automatic overlap": auto["share"], "largest share from one programme": share1, "that programme": prog1,
                     "share N": n, "share new, not N": new, "share lab": lab, "new teaching ECTS (scaled)": new_ects, "N ECTS": n * taught, "T ECTS": t_ects, "X ECTS": x_ects,
                     "professor-equivalents": new_ects * SWS_PER_ECTS / SWS_A_YEAR, "share of new ECTS in N": n * taught / new_ects if new_ects > 0 else np.nan,
                     "timetable confirmation": float(g.loc[is_(*COVERED) & g["in the timetable"], "ects"].sum()) / cov_ects if cov_ects else np.nan,
                     "covered ECTS on the first reviewer alone": alone / cov_ects if cov_ects else np.nan, "meets band and one-programme limit": ok, "why not": "; ".join(why)})
    refs = pd.DataFrame(refs)
    order = pd.read_csv(ORDER).set_index(["type", "level"])
    cands = []
    for (t, lv), g in refs.groupby(["type", "level"], sort=False):
        n_ok, single = int(g["meets band and one-programme limit"].sum()), len(g) == 1
        if n_ok == len(g):
            v = "existing-resources passer" if (g["X ECTS"] <= 1e-9).all() else "band passer"
        elif n_ok == 1:
            v = "reference-dependent"
        else:
            v = "fail"
        why = "; ".join(sorted({w for x in g["why not"] for w in x.split("; ") if w}))
        widen = SINGLE_WIDEN if single else 0.0
        cands.append({"gate order": int(order.at[(t, lv), "gate order"]), "type": t, "level": lv, "central titles": order.at[(t, lv), "central titles"], "references": len(g),
                      "single reference": single, "overlap (mean)": g["overlap"].mean(), "overlap low": g["overlap"].min() - widen, "overlap high": g["overlap"].max() + widen,
                      "automatic overlap (mean)": g["automatic overlap"].mean(), "largest share from one programme": g["largest share from one programme"].max(),
                      "new teaching ECTS (mean)": g["new teaching ECTS (scaled)"].mean(), "N ECTS (mean)": g["N ECTS"].mean(), "T ECTS (mean)": g["T ECTS"].mean(), "X ECTS (mean)": g["X ECTS"].mean(),
                      "professor-equivalents (mean)": g["professor-equivalents"].mean(), "share of new ECTS in N (mean)": g["share of new ECTS in N"].mean(),
                      "verdict": v, "why": "mixed" if v == "fail" and len(why.split("; ")) > 1 else why,
                      "sample: rows that differ": info[(t, lv)]["differ"], "sample failed": info[(t, lv)]["sample failed"]})
    cands = pd.DataFrame(cands).sort_values("gate order").reset_index(drop=True)
    refs.to_csv(GATE_REFS, index=False)
    cands.to_csv(GATE, index=False)
    k.to_csv(INTERIM / "funnel2_rows_final.csv", index=False)
    both = k[k["second"].notna()]
    agree = float(((both["first"].isin(COVERED)) == (both["second"].isin(COVERED))).mean()) if len(both) else None
    res = {"stamp": stamp, "rows": len(k), "references": len(refs), "candidates": len(cands), "verdicts": cands["verdict"].value_counts().to_dict(),
           "first_marking": k["first"].value_counts().to_dict(), "first_marking_unsure": int(k["first unsure"].sum()), "rows_marked_by_both": len(both), "agreement_on_covered_or_not": agree,
           "final_basis": k["basis"].value_counts().to_dict(), "samples": {f"{t} {lv}": v for (t, lv), v in info.items()},
           "band": [lo, hi], "one_programme_max": one_max,
           "inputs": {**{f.name: sha(f) for f in (KEY, ROWS, MARKS[1], MARKS[2])}, **({MARKS[3].name: sha(MARKS[3])} if MARKS[3].exists() else {})},
           "files": {f.name: sha(f) for f in (GATE, GATE_REFS)}}
    STEP7.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "step7_gate.md").write_text("\n".join([
        "# Funnel step 7: the feasibility gate (generated)", "", f"Code commit {stamp['commit']}, run on {stamp['date']}, tracked files clean: {stamp['clean']}.", "",
        "All module verdicts are made by AI readers; no person has checked a row.", "", "## Candidates", "",
        md_table(cands.assign(**{"central titles": cands["central titles"].str.slice(0, 50)}).round(2)), "", "## References", "", md_table(refs.round(2))]) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    {"rows": rows, "sample": sample, "verdict": verdict}[sys.argv[1] if len(sys.argv) > 1 else ""]()
