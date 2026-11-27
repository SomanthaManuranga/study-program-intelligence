"""Rules version 4, R2: which candidates get a module check (configs/funnel.yaml: version_4.gate_breadth and the second
entry of version_4.deviations; criteria and readings in docs/criteria_funnel_v4_gate.md)

Run from the repository root, each command from committed code on a clean tree, after analysis.funnel_merge run:

    python -m study_program_intelligence.analysis.funnel_gate4 sheet    # blind title sheet for the units not yet marked
    (a fresh reader writes docs/funnel4_emi_labels.csv: group, label, reason; commit it)
    python -m study_program_intelligence.analysis.funnel_gate4 list     # the check list, with a reason for every other candidate

Outputs: reports/funnel2/v4_emi_sheet.md (the sheet), data/interim/funnel4_emi_key.csv (group -> unit, not shown to
the reader), data/interim/funnel4_check_list.csv, funnel4_check_list.json.
"""

from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd

from .funnel_common import INTERIM, REPO_ROOT, REPORTS, run_stamp
from .funnel_merge import FIRST, ORDER4
from .funnel_types import OFFER_TYPES, sha
from .funnel_units import EMI_LABELS

LABELS4 = REPO_ROOT / "docs" / "funnel4_emi_labels.csv"
KEY4, SHEET4 = INTERIM / "funnel4_emi_key.csv", REPORTS / "v4_emi_sheet.md"
LIST4, LIST4_JSON = INTERIM / "funnel4_check_list.csv", INTERIM / "funnel4_check_list.json"
TITLES = 8                                     # F3, as Step 3
QUESTION = ("Is this kind of programme inside the field of a faculty of electrical engineering, media and computer science "
            "(yes, partly or no)?")


def gate_units(order: pd.DataFrame) -> pd.DataFrame:
    """F2: the units (type, level) of the first 20 candidates and of the control, with their candidate."""
    pick = pd.concat([order.head(FIRST), order[order["control"].astype(bool)]]).drop_duplicates(["candidate", "level"])
    return pd.DataFrame([{"candidate": int(r.candidate), "level": r.level, "type": int(t)} for r in pick.itertuples() for t in str(r.types).split("; ")])


def sheet() -> None:
    stamp = run_stamp()
    order = pd.read_csv(ORDER4)
    old = pd.read_csv(EMI_LABELS, keep_default_na=False)
    units = gate_units(order)
    todo = units[~units.set_index(["type", "level"]).index.isin(old.set_index(["type", "level"]).index)].drop_duplicates(["type", "level"])
    todo = todo.sort_values(["type", "level"]).reset_index(drop=True)
    d = pd.read_csv(OFFER_TYPES, low_memory=False, dtype={"programme_id": str})
    rng = np.random.default_rng(42)
    todo = todo.iloc[rng.permutation(len(todo))].reset_index(drop=True)          # G2: shuffled
    lines = ["# Groups of study programmes", "", f"Question for every group: {QUESTION}", "",
             "yes: the core subject is one the faculty teaches (electrical or information engineering, computer science or informatics "
             "including applied forms such as software, data or security, media and design). partly: an EMI subject joined with a non-EMI "
             "subject in roughly equal parts (for example business informatics, mechatronics, media management). no: the core subject is "
             "outside these fields, even if some modules touch them.", "",
             "Answer in a CSV with the columns group, label, reason (one line).", ""]
    keys = []
    for n, r in enumerate(todo.itertuples(), 1):
        a = d[(d["assigned_type"] == r.type) & (d["level"] == r.level)]
        take = a.iloc[np.sort(rng.choice(len(a), min(TITLES, len(a)), replace=False))]
        lines += [f"### Group {n} ({r.level}, {len(a)} programmes)", ""] + [f"- {t}" for t in take["title"]] + [""]
        keys.append({"group": n, "type": int(r.type), "level": r.level})
    REPORTS.mkdir(parents=True, exist_ok=True)
    SHEET4.write_text("\n".join(lines) + "\n", encoding="utf-8")
    pd.DataFrame(keys).to_csv(KEY4, index=False)
    print(json.dumps({"commit": stamp["commit"], "units in the first 20 and the control": len(units), "already marked": int(len(units) - len(todo)),
                      "groups on the sheet": len(todo)}, indent=1))


def emi_marks() -> pd.DataFrame:
    old = pd.read_csv(EMI_LABELS, keep_default_na=False)[["type", "level", "label"]].assign(source="Step 3")
    key = pd.read_csv(KEY4)
    new = pd.read_csv(LABELS4, keep_default_na=False)
    if set(new["group"]) != set(key["group"]) or not new["label"].isin(["yes", "partly", "no"]).all():
        raise SystemExit("docs/funnel4_emi_labels.csv must mark every group of the sheet with yes, partly or no")
    new = key.merge(new, on="group")[["type", "level", "label"]].assign(source="R2 reader")
    return pd.concat([old, new], ignore_index=True)


def check_list() -> None:
    stamp = run_stamp()
    order = pd.read_csv(ORDER4)
    marks = emi_marks().set_index(["type", "level"])
    rows = []
    pick = pd.concat([order.head(FIRST), order[order["control"].astype(bool)]]).drop_duplicates(["candidate", "level"])
    for r in pick.to_dict("records"):
        types = [int(t) for t in str(r["types"]).split("; ")]
        labels = [marks.at[(t, r["level"]), "label"] for t in types]                 # G1: a missing mark raises here
        emi = any(x in ("yes", "partly") for x in labels)                             # F4
        why = [] if emi else ["outside EMI's field"]
        if r["mixed"]:
            why.append(f"mixed type ({r['mixed types']})")
        if r["below the minimum cohort"]:
            why.append("below the minimum cohort")
        control = bool(r["control"])
        rows.append({"gate order": int(r["gate order"]), "candidate": int(r["candidate"]), "level": r["level"], "name": r["name"], "types": r["types"],
                     "marks": "; ".join(f"{t}:{x}" for t, x in zip(types, labels)), "EMI-field": emi, "mixed": bool(r["mixed"]),
                     "below the minimum cohort": bool(r["below the minimum cohort"]), "control": control,
                     "module check": control or not why, "reason": "control (version_4.deviations)" if control else ("; ".join(why) or "checked")})
    out = pd.DataFrame(rows)
    out.to_csv(LIST4, index=False)
    label = lambda r: f"{str(r['name'])[:50]} ({r['level']}, order {r['gate order']})"
    res = {"stamp": stamp, "candidates": len(out), "module check": int(out["module check"].sum()),
           "checked": [label(r) for r in out[out["module check"]].to_dict("records")],
           "left out": {label(r): r["reason"] for r in out[~out["module check"]].to_dict("records")},
           "inputs": {f.name: sha(f) for f in (ORDER4, EMI_LABELS, LABELS4, KEY4)}, "files": {LIST4.name: sha(LIST4)}}
    LIST4_JSON.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False))


def tries() -> None:
    """version_4.title_merge.measures (reference curricula) with feasibility_gate.references.choice: for every candidate
    of the check list, the assigned full-time offers of all its units at universities of applied sciences other than
    OTH (universities only if there is none), nearest the centroid of its title-matched type with the most assigned
    offers of that level first (deviation 4; any of its types without a title match; ties: lower type number); one offer per institution and cleaned title. A table already collected in
    version 3 for the same offer is marked so it can be reused."""
    from .funnel_refs import HAW, TABLES
    from .funnel_units import load_step2
    stamp = run_stamp()
    d, t, emb, cent = load_step2()
    chk = pd.read_csv(LIST4)
    from .funnel_merge import UNITS4
    units = pd.read_csv(UNITS4)
    known = {}
    for f in sorted(TABLES.glob("*_[ab].json")):
        meta = json.loads(f.read_text(encoding="utf-8"))
        if meta.get("programme_id"):
            known[str(meta["programme_id"])] = f.stem
    rows = []
    for r in chk[chk["module check"]].to_dict("records"):
        types = [int(x) for x in str(r["types"]).split("; ")]
        a = d[d["assigned_type"].isin(types) & (d["level"] == r["level"]) & d["full_time"].astype(bool) & ~d["is_oth"].astype(bool)].copy()
        titled = [int(x) for x in units.loc[(units["candidate"] == r["candidate"]) & (units["level"] == r["level"]) & (units["how"] == "title"), "type"] if int(x) in types]
        base = titled or types                                                          # version_4.deviations, fourth entry: the title type
        sizes = d[d["assigned_type"].isin(base) & (d["level"] == r["level"])].groupby("assigned_type").size()
        centre = int(sorted(sizes.items(), key=lambda kv: (-kv[1], kv[0]))[0][0])
        a["distance to the centroid"] = 1 - emb[a.index] @ cent[centre]
        haw = a[a["institution_type"] == HAW]
        use, pool = (haw, "universities of applied sciences") if len(haw) else (a, "universities only")
        use = use.sort_values(["distance to the centroid", "programme_id"], kind="mergesort").drop_duplicates(["institution", "clean_title"])
        for k, o in enumerate(use.to_dict("records"), 1):
            rows.append({"gate order": int(r["gate order"]), "candidate": int(r["candidate"]), "level": r["level"], "name": r["name"], "centre type": centre,
                         "try": k, "institution": o["institution"], "city": o["city"], "title": o["title"], "programme_id": o["programme_id"],
                         "distance to the centroid": o["distance to the centroid"], "offers from": pool,
                         "version-3 table": known.get(str(o["programme_id"]), "")})
    out = pd.DataFrame(rows)
    out.to_csv(INTERIM / "funnel4_reference_tries.csv", index=False)
    print(json.dumps({"commit": stamp["commit"]}, indent=1))
    print(out[out["try"] <= 8][["gate order", "candidate", "level", "try", "institution", "title", "version-3 table"]].to_string())


if __name__ == "__main__":
    {"sheet": sheet, "list": check_list, "tries": tries}[sys.argv[1]]()
