"""Funnel, pool mapping: every catalogue subject label to one Destatis subject code (configs/funnel.yaml pool_mapping).

Run from the repository root, before clustering:

    python -m study_program_intelligence.analysis.funnel_subject_map

Exact name first, else the nearest Destatis name by the project's encoder. Blind to programme types: the table is built
from label names only. Corrections after the second look go in configs/funnel_subject_map_corrections.yaml, each with a
reason. Output: configs/funnel_subject_map.csv (committed before clustering).
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
CATALOGUE = REPO_ROOT / "data" / "processed" / "programmes_full.csv"
DESTATIS = REPO_ROOT / "data" / "raw" / "destatis" / "21311-0015_BY.csv"
OUT = REPO_ROOT / "configs" / "funnel_subject_map.csv"
CORRECTIONS = REPO_ROOT / "configs" / "funnel_subject_map_corrections.yaml"
REVIEW_LINE = 0.90    # raw e5 cosines are compressed; below this a match is listed for the second look


def clean_label(label: str) -> str:
    return re.sub(r"\s*\((grundständig|weiterführend)\)\s*$", "", label).strip()


def catalogue_labels() -> pd.Series:
    d = pd.read_csv(CATALOGUE, low_memory=False, dtype={"programme_id": str})
    return d["subjects"].dropna().str.split("; ").explode().map(clean_label).value_counts()


def destatis_labels() -> pd.DataFrame:
    d = pd.read_csv(DESTATIS, sep=";", low_memory=False, dtype=str)
    pairs = []
    for i in range(1, 8):
        code, label = f"{i}_variable_attribute_code", f"{i}_variable_attribute_label"
        if code in d.columns and d[code].astype(str).str.match(r"^SF\d+$").any():
            pairs = d[[code, label]].drop_duplicates()
            pairs.columns = ["code", "name"]
    return pairs[pairs["code"].str.match(r"^SF\d+$")].drop_duplicates("code").reset_index(drop=True)


def norm(s: str) -> str:
    return re.sub(r"[^a-zäöüß0-9]+", " ", s.lower()).strip()


def build() -> pd.DataFrame:
    from sentence_transformers import SentenceTransformer
    labels, dest = catalogue_labels(), destatis_labels()
    exact = {norm(n): c for n, c in zip(dest["name"], dest["code"])}
    model = SentenceTransformer("intfloat/multilingual-e5-base")
    dv = model.encode([f"query: {n}" for n in dest["name"]], normalize_embeddings=True, batch_size=32)
    lv = model.encode([f"query: {n}" for n in labels.index], normalize_embeddings=True, batch_size=32)
    sim = lv @ dv.T
    rows = []
    for i, (label, n) in enumerate(labels.items()):
        j = int(np.argmax(sim[i]))
        code = exact.get(norm(label), dest.loc[j, "code"])
        how = "exact" if norm(label) in exact else "nearest"
        name = dest.set_index("code").loc[code, "name"]
        rows.append({"label": label, "offers": int(n), "code": code, "destatis_name": name, "how": how,
                     "similarity": round(float(sim[i, j]), 3), "review": how == "nearest" and sim[i, j] < REVIEW_LINE})
    t = pd.DataFrame(rows)
    if CORRECTIONS.exists():
        fix = yaml.safe_load(CORRECTIONS.read_text(encoding="utf-8"))["corrections"]
        names = dest.set_index("code")["name"]
        for f in fix:
            m = t["label"] == f["label"]
            assert m.any(), f["label"]
            t.loc[m, ["code", "destatis_name", "how"]] = [f["code"], names[f["code"]], "corrected: " + f["reason"]]
    return t


def main() -> None:
    t = build()
    t.to_csv(OUT, index=False, encoding="utf-8")
    print(f"{len(t)} labels, {(t['how'] == 'exact').sum()} exact, {t['how'].str.startswith('corrected').sum()} corrected, "
          f"{int(t['review'].sum())} below the review line. Written: {OUT}")


if __name__ == "__main__":
    main()
