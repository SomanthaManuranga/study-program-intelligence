"""Topic check: agreement of the two AI reviewers and AI-checked coverage per programme kind."""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import engine as E

VDIR = E.OUT / "verification"
SCORE = {"covered": 1.0, "partly": 0.5, "no": 0.0}
CATS = ["covered", "partly", "no", "unclear"]


def load(reviewer: str) -> pd.DataFrame:
    fs = sorted((VDIR / "reviews" / reviewer).glob("B*.csv"))
    d = pd.concat([pd.read_csv(f).assign(batch=f.stem) for f in fs], ignore_index=True) if fs else pd.DataFrame()
    if len(d):
        d["verdict"] = d.verdict.str.strip().str.lower()
    return d


def kappa(a: pd.Series, b: pd.Series) -> float:
    po = (a.values == b.values).mean()
    pe = sum((a == c).mean() * (b == c).mean() for c in CATS)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def coverage(rows: pd.DataFrame, verdict_col: str) -> tuple[float, float, int]:
    r = rows[rows[verdict_col] != "unclear"]
    if r.empty:
        return np.nan, np.nan, 0
    w = r.weight.astype(float)
    full = (w * r[verdict_col].map(SCORE)).sum() / w.sum()
    strict = (w * (r[verdict_col] == "covered")).sum() / w.sum()
    return full, strict, len(rows) - len(r)


def one_programme(rows: pd.DataFrame, verdict_col: str, module_col: str, cat: pd.DataFrame) -> tuple[float, str]:
    r = rows[rows[verdict_col] != "unclear"]
    if r.empty:
        return np.nan, ""
    prog = cat.set_index("module_id").programme
    cov = r[r[verdict_col] == "covered"]
    by = cov.assign(p=cov[module_col].map(prog)).groupby("p").weight.sum()
    if by.empty:
        return 0.0, ""
    return by.max() / r.weight.sum(), by.idxmax()


def summary():
    key = pd.read_csv(VDIR / "topic_rows_key.csv")
    cat = pd.read_csv(VDIR / "emi_module_catalogue.csv")
    A, B = load("A"), load("B")
    m = key.merge(A[["row_id", "verdict", "module_id", "batch"]].rename(columns={"verdict": "a", "module_id": "a_mod"}), on="row_id") \
           .merge(B[["row_id", "verdict", "module_id"]].rename(columns={"verdict": "b", "module_id": "b_mod"}), on="row_id")
    m["agree"] = m.a == m.b
    # where they differ, until the third reader: the more cautious verdict (lower score; unclear counts as unclear)
    order = {"no": 0, "unclear": 1, "partly": 2, "covered": 3}
    m["cautious"] = [x if order[x] <= order[y] else y for x, y in zip(m.a, m.b)]
    m["cautious_mod"] = np.where(m.cautious == m.a, m.a_mod, m.b_mod)
    agree = {"rows": len(m), "agreement": m.agree.mean(), "kappa": kappa(m.a, m.b)}
    per_batch = m.groupby("batch").apply(lambda g: pd.Series({"rows": len(g), "agreement": g.agree.mean(),
                                                               "kappa": kappa(g.a, g.b)}))
    res = E.run(E.prepare(), E.agreed_rules())
    auto = res["kinds"].set_index("kind")
    out = []
    for kind, g in m.groupby("kind"):
        ca, sa, ua = coverage(g, "a")
        cb, sb, ub = coverage(g, "b")
        cc, sc, uc = coverage(g, "cautious")
        op, opn = one_programme(g, "cautious", "cautious_mod", cat)
        out.append({"kind": kind, "rows": len(g), "agreement": g.agree.mean(), "auto_coverage": auto.loc[kind, "coverage"],
                    "A": ca, "B": cb, "cautious": cc, "cautious_strict": sc, "unclear_rows": uc,
                    "one_programme": op, "one_programme_name": opn,
                    "in_band_40_80": (0.40 <= cc <= 0.80) if cc == cc else None})
    K = pd.DataFrame(out)
    m.to_csv(VDIR / "topic_check_rows.csv", index=False)
    K.to_csv(VDIR / "topic_check_kinds.csv", index=False)
    return agree, per_batch, K, m
