"""Rarity screen: programme types offered at very few German universities that EMI could teach (re-scope, week 2).

Run from the repository root (after transform.programmes --set full and transform.modules --set emi2026):

    python -m study_program_intelligence.analysis.rarity

Rules: configs/rarity.yaml (fixed before running). Full-time bachelor and master offers in EMI-linked study fields;
a type is rare if at most 3 institutions offer it full-time. Two type definitions: the catalogue's subject
classification, and the normalised programme title. Rare title types are ranked by how closely EMI's current modules
match their texts (mean of the 10 best e5 similarities); the top 40 go to a hand review.
Outputs: data/interim/rarity_types.csv, reports/rarity.md.
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from study_program_intelligence.analysis.module_gaps import category, centre, clean, embed

REPO_ROOT = Path(__file__).resolve().parents[3]
RULES = REPO_ROOT / "configs" / "rarity.yaml"
PROGS = REPO_ROOT / "data" / "processed" / "programmes_full.csv"
FIELDS = REPO_ROOT / "data" / "processed" / "programme_fields_full.csv"
EMI_2026 = REPO_ROOT / "data" / "interim" / "modules_emi_2026.csv"
OUT = REPO_ROOT / "data" / "interim" / "rarity_types.csv"
REPORT = REPO_ROOT / "reports" / "rarity.md"
DEGREE = re.compile(r"\b(bachelor|master|of|science|engineering|arts|dual|berufsbegleitend|vollzeit|teilzeit|online)\b|"
                    r"\b[bm]\.?\s?(sc|eng|a)\.?(?=\s|$)|\([^)]*\)", re.I)


STOP = set("""aber alle als auch auf aus bei bzw das dem den der des die durch ein eine einer eines für fuer
in im ist mit nach oder sowie über und unter von vom vor zum zur and for the with into from under over their this that
studium studiengang schwerpunkt profil vertiefung richtung""".split())


def topics(title: str) -> set[str]:
    return {w for w in re.findall(r"[a-zäöüß]+", title) if len(w) >= 5 and w not in STOP}


def norm_title(t: str) -> str:
    t = DEGREE.sub(" ", str(t).lower())
    t = re.sub(r"[^\wäöüß+ ]", " ", t)
    return " ".join(t.split())


def all_fulltime() -> pd.DataFrame:
    p = pd.read_csv(PROGS, dtype={"programme_id": str})
    p = p[p["degree"].isin(["Bachelor/Bakkalaureus", "Master"]) & (p["study_form"] == "Vollzeitstudium")].copy()
    p["type_title"] = p["title"].map(norm_title)
    return p


def offers(rules: dict) -> pd.DataFrame:
    p = pd.read_csv(PROGS, dtype={"programme_id": str})
    f = pd.read_csv(FIELDS, dtype={"programme_id": str, "field_key": str})
    keys = set(rules["study_fields"]["fields"])
    linked = f[f["field_key"].isin(keys) | f["field_key"].str[:2].isin(rules["study_fields"]["groups"])]["programme_id"]
    p = p[p["programme_id"].isin(set(linked)) & p["degree"].isin(["Bachelor/Bakkalaureus", "Master"])
          & (p["study_form"] == "Vollzeitstudium")].copy()
    p["level"] = p["degree"].map({"Bachelor/Bakkalaureus": "BA", "Master": "MA"})
    p["type_title"] = p["title"].map(norm_title)
    return p


def type_table(p: pd.DataFrame, col: str) -> pd.DataFrame:
    g = p.groupby([col, "level"]).agg(institutions=("institution", "nunique"), offers=("programme_id", "nunique"),
                                      where=("institution", lambda s: "; ".join(sorted(set(s))[:4])),
                                      oth=("is_oth", "any")).reset_index()
    return g


def main() -> None:
    rules = yaml.safe_load(RULES.read_text(encoding="utf-8"))
    rmax = rules["rare_max_institutions"]
    p = offers(rules)
    subj = type_table(p.assign(subject=p["subjects"].fillna("").str.split(r"\s*[;|]\s*")).explode("subject"), "subject")
    titles = type_table(p, "type_title")
    rare_titles = titles[titles["institutions"] <= rmax]
    # primary type (amendment): rare topic words, counted over ALL full-time bachelor/master titles in Germany
    full = all_fulltime()
    word_inst = full.assign(word=full["type_title"].map(topics)).explode("word").groupby("word")["institution"].nunique()
    rare_words = set(word_inst[word_inst <= rmax].index)
    pw = p.assign(word=p["type_title"].map(lambda s: topics(s) & rare_words)).explode("word").dropna(subset=["word"])
    rare = pw.groupby("word").agg(institutions=("institution", "nunique"), offers=("programme_id", "nunique"),
                                  levels=("level", lambda s: "/".join(sorted(set(s)))),
                                  where=("institution", lambda s: "; ".join(sorted(set(s))[:3])),
                                  titles=("title", lambda s: "; ".join(sorted(set(s))[:3])), oth=("is_oth", "any")).reset_index()

    # teachability: catalogue texts of each rare title type vs EMI modules
    emi = pd.read_csv(EMI_2026)
    emi["clean"] = [clean(t if isinstance(t, str) else "", ti) for t, ti in zip(emi["text"], emi["title"])]
    emi = emi[[category(ti, c) != "frame" for ti, c in zip(emi["title"], emi["clean"])]].drop_duplicates("title")
    e_emi = centre(embed(emi["clean"].tolist()), emi["source_file"])
    rare = rare.sort_values("word").reset_index(drop=True)
    texts = []
    for w in rare["word"]:
        g = pw[pw["word"] == w].drop_duplicates("programme_id")
        texts.append(" ".join(g["title"].tolist() + g["content"].fillna("").astype(str).tolist())[:4000])
    e_rare = centre(embed(texts))
    sims = e_rare @ e_emi.T
    top = np.sort(sims, axis=1)[:, -10:]
    rare["teachability"] = top.mean(axis=1).round(3)
    best = sims.argmax(axis=1)
    rare["closest EMI modules"] = ["; ".join(re.sub(r"^\[[^\]]*\]\s*", "", emi["title"].iloc[j])[:35]
                                             for j in np.argsort(-sims[i])[:4]) for i in range(len(rare))]
    rare = rare.sort_values("teachability", ascending=False).reset_index(drop=True)
    n_review = 40
    rare["hand review"] = rare.index < n_review
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rare.to_csv(OUT, index=False)

    md = lambda df: "\n".join(["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
                              + ["| " + " | ".join(str(v).replace("|", "/") for v in r) + " |" for r in df.itertuples(index=False)])
    subj_rare = subj[subj["institutions"] <= rmax]
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join([
        "# Rarity screen (generated)", "",
        f"Full-time bachelor and master offers in EMI-linked study fields: {len(p):,} offers at {p['institution'].nunique()} "
        f"institutions. Rare = at most {rmax} institutions.", "",
        f"- Subject types: {len(subj):,}, rare: {len(subj_rare):,}.",
        f"- Exact title types: {len(titles):,}, rare: {len(rare_titles):,} (wording, not rarity; see the decision log).",
        f"- Rare topic words (primary): {len(rare):,} in EMI-linked full-time offers.", "",
        f"## Top {n_review} rare topic words by teachability (for the hand review)", "",
        md(rare.head(n_review)[["word", "levels", "institutions", "offers", "where", "titles", "oth", "teachability", "closest EMI modules"]]), "",
        "## Rare subject types", "", md(subj_rare.sort_values("institutions")[["subject", "level", "institutions", "where", "oth"]]), ""]),
        encoding="utf-8")
    print(f"offers {len(p):,}; rare topic words {len(rare):,}; subject types {len(subj):,}, rare {len(subj_rare):,}")
    pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 70)
    print(rare.head(n_review)[["word", "levels", "institutions", "titles", "oth", "teachability"]].to_string())
    print(f"\nWritten: {OUT.relative_to(REPO_ROOT)}, {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
