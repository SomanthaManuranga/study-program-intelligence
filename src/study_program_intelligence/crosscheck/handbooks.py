"""Split reference module handbooks into modules (number, title, ECTS, compulsory/elective, content).

Public handbooks of other universities. Names of lecturers are removed from the content.
Output: data/interim/crosscheck/verification/handbook_modules.csv
"""

from __future__ import annotations

import re

import pandas as pd
import pdfplumber

from .common import RAW
from .packets import NAME, VDIR

REFS = {
    "itsec_ba_thd": ("IT-Sicherheit | BA", "TH Deggendorf, Cyber Security (B.Sc.)", RAW / "funnel2_refs" / "223_bachelor_b_handbook.pdf", "thd"),
    "itsec_ba_thws": ("IT-Sicherheit | BA", "TH Würzburg-Schweinfurt, Informationssicherheit (B.Sc.)", RAW / "handbook_test" / "itsec_ba_thws.pdf", "thws"),
    "itsec_ma_thd": ("IT-Sicherheit | MA", "TH Deggendorf, Cyber Security (M.Eng., part-time)", RAW / "handbook_test" / "itsec_ma_thd.pdf", "thd"),
    "itsec_ma_aalen": ("IT-Sicherheit | MA", "Hochschule Aalen, Cyber Security (M.Sc., part-time)", RAW / "handbook_test" / "itsec_ma_aalen.pdf", "aalen"),
}
CONTENT_START = re.compile(r"(Lerninhalte|Inhalte der Lehrveranstaltung|Inhalte|Lehrinhalte|Qualifikationsziele des Moduls|Modulziele)")
CONTENT_STOP = re.compile(r"(Literatur|Lehr- und Lernmethoden|Lehrmethoden|Prüfungsform|Enthaltene Lehrveranstaltungen|Empfohlene Literatur)")


def clean(t: str, limit: int = 1500) -> str:
    m = CONTENT_START.search(t)
    s = t[m.start():] if m else t
    e = CONTENT_STOP.search(s, 20)
    s = s[: e.start()] if e else s
    s = NAME.sub("[name]", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s[:limit]


def _pages(path, crop_right=False):
    with pdfplumber.open(path) as pdf:
        out = []
        for p in pdf.pages:
            full = p.extract_text() or ""
            right = (p.crop((p.width * 0.33, 0, p.width, p.height)).extract_text() or "") if crop_right else full
            out.append((full, right))
        return out


def parse_thd(path):
    pages = _pages(path)
    text = "\n".join(f for f, _ in pages)
    starts = list(re.finditer(r"^([BM]-CY-\d+)\s+((?:(?!Modul Nr\.)[^\n]+\n){1,3}?)Modul Nr\.\s*\1", text, re.M))
    rows = []
    for i, m in enumerate(starts):
        block = text[m.start(): starts[i + 1].start() if i + 1 < len(starts) else len(text)]
        ects = re.search(r"^ECTS\s+(\d+(?:[.,]\d+)?)", block, re.M)
        kind = re.search(r"Art der Lehrveranstaltungen\s+(\w+)", block)
        rows.append({"module_no": m.group(1), "title": " ".join(m.group(2).split()), "ects": float(ects.group(1).replace(",", ".")) if ects else None,
                     "type": "elective" if kind and "Wahl" in kind.group(1) else "compulsory", "content": clean(block)})
    return rows


def parse_thws(path):
    pages = _pages(path, crop_right=True)
    rows, cur = [], None
    for full, right in pages:
        m = re.search(r"^Modul:\s*([\d,]+)\s*\n((?:(?!Modulprofil)[^\n]+\n){1,3}?)Modulprofil", full, re.M)
        if m:
            if cur:
                rows.append(cur)
            ects = re.search(r"(\d+(?:\.\d+)?)\s", full[full.find("ECTS-Credits"):] if "ECTS-Credits" in full else "")
            kind = re.search(r"Art des Moduls\s+(\w+)", full)
            cur = {"module_no": m.group(1).split(",")[0], "title": " ".join(m.group(2).split()), "ects": float(ects.group(1)) if ects else None,
                   "type": "elective" if kind and re.search(r"Wahl|WPM", kind.group(1)) else "compulsory", "_text": right}
        elif cur:
            cur["_text"] += "\n" + right
    if cur:
        rows.append(cur)
    for r in rows:
        r["content"] = clean(r.pop("_text"))
    return rows


def parse_aalen(path):
    pages = _pages(path)
    rows, cur = [], None
    for full, _ in pages:
        m = re.search(r"Modul-Nr:\s*(\d+)\s+(.+?)\s+SPO\s*\d+\s+Seite\s+(\d+)", full)
        if m and m.group(3) == "1":
            if cur:
                rows.append(cur)
            cp = re.search(r"Credits\s+(\d+(?:[.,]\d+)?)\s*CP", full)
            kind = re.search(r"Modulart\s+(\w+)", full)
            cur = {"module_no": m.group(1), "title": m.group(2).strip(), "ects": float(cp.group(1).replace(",", ".")) if cp else None,
                   "type": "elective" if kind and "Wahl" in kind.group(1) else "compulsory", "_text": full}
        elif cur:
            cur["_text"] += "\n" + full
    if cur:
        rows.append(cur)
    for r in rows:
        r["content"] = clean(r.pop("_text"))
    return rows


PARSERS = {"thd": parse_thd, "thws": parse_thws, "aalen": parse_aalen}


def main():
    out = []
    for ref, (kind, name, path, fmt) in REFS.items():
        for r in PARSERS[fmt](path):
            out.append({"ref": ref, "kind": kind, "reference": name, **r})
    d = pd.DataFrame(out)
    # Aalen lists specialisation modules twice (as specialisation and as elective): keep one; only the core is compulsory
    aalen_core = {"25807", "25808", "25809", "25610", "25901", "91031", "9999", "91999"}
    d["module_no"] = d.module_no.astype(str)
    a = d.ref == "itsec_ma_aalen"
    d.loc[a, "type"] = ["compulsory" if n in aalen_core else "elective" for n in d.loc[a, "module_no"]]
    d = d.drop_duplicates(["ref", "module_no"]).reset_index(drop=True)
    d.insert(0, "row_id", [f"H{i:04d}" for i in range(len(d))])
    d.to_csv(VDIR / "handbook_modules.csv", index=False)
    return d


if __name__ == "__main__":
    d = main()
    print(d.groupby(["ref", "type"]).agg(n=("title", "size"), ects=("ects", "sum"), no_ects=("ects", lambda s: s.isna().sum()),
                                         short=("content", lambda s: (s.str.len() < 150).sum())).to_string())


def packets(n_suggest: int = 8, max_rows: int = 32, seed: int = 2026):
    import numpy as np
    from . import steps as S
    from .common import REPO
    d = pd.read_csv(VDIR / "handbook_modules.csv")
    cat = pd.read_csv(VDIR / "emi_module_catalogue.csv")
    modules = pd.read_csv(REPO / "data" / "interim" / "modules_emi_2026.csv")
    modules = modules[modules.title.notna()].reset_index(drop=True)
    match = S.build_matcher(modules)
    sims = match((d.title.fillna("") + " ") * 3 + d.content.fillna(""))
    rng = np.random.default_rng(seed)
    sugg = []
    for i in range(len(d)):
        top = list(np.argsort(-sims[i])[:n_suggest]); rng.shuffle(top)
        sugg.append(" ".join(cat.module_id.iloc[j] for j in top))
    d["suggested"] = sugg
    d.to_csv(VDIR / "handbook_modules.csv", index=False)
    out = VDIR / "handbook_packets"; out.mkdir(exist_ok=True)
    index = "\n".join(f"{r.module_id} | {r.programme} | {r.title}" for r in cat.itertuples())
    man = []
    for ref, g in d.groupby("ref"):
        parts = [g.iloc[i:i + max_rows] for i in range(0, len(g), max_rows)]
        for k, part in enumerate(parts, 1):
            name = f"{ref}_{k}"
            need = sorted({m for s in part.suggested for m in s.split()})
            L = [f"# Handbook-test packet {name}", "", f"Reference programme: {part.reference.iloc[0]}", "",
                 "## Modules of the reference programme to mark", ""]
            for r in part.itertuples():
                L += [f"### {r.row_id} | {r.title} | {r.ects:g} ECTS | {r.type}", r.content or "(no description)",
                      f"Suggested EMI modules: {r.suggested}", ""]
            L += ["## Suggested EMI modules (descriptions)", ""]
            for mid, m in cat.set_index("module_id").loc[need].iterrows():
                L.append(f"#### {mid}: {m.title} ({m.programme}, {m.level}, {m.ects} ECTS)\n{m.description}\n")
            L += ["## Index of all EMI modules (id | programme | title)", "", index]
            (out / f"{name}.md").write_text("\n".join(L), encoding="utf-8")
            man.append({"packet": name, "rows": len(part), "kb": round((out / f"{name}.md").stat().st_size / 1024)})
    return pd.DataFrame(man)


TOTAL_CREDITS = {"itsec_ba_thd": 210, "itsec_ba_thws": 210, "itsec_ma_thd": 90, "itsec_ma_aalen": 90}
HSCORE = {"covered": 1.0, "partly": 0.5, "new": 0.0}
HORDER = {"new": 0, "unclear": 1, "partly": 2, "covered": 3}


def _load(rev):
    fs = sorted((VDIR / "handbook_reviews" / rev).glob("*.csv"))
    d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True)
    d["verdict"] = d.verdict.str.strip().str.lower()
    return d


def results():
    from .verify import kappa
    from .common import EMI_PROGRAMME_NAMES
    d = pd.read_csv(VDIR / "handbook_modules.csv")
    cat = pd.read_csv(VDIR / "emi_module_catalogue.csv").set_index("module_id")
    A, B = _load("A"), _load("B")
    m = d.merge(A[["row_id", "verdict", "emi_modules"]].rename(columns={"verdict": "a", "emi_modules": "a_mod"}), on="row_id") \
         .merge(B[["row_id", "verdict", "emi_modules"]].rename(columns={"verdict": "b", "emi_modules": "b_mod"}), on="row_id")
    m["agree"] = m.a == m.b
    tr_p = VDIR / "handbook_reviews" / "third_reader.csv"
    tr = pd.read_csv(tr_p).set_index("row_id") if tr_p.exists() else pd.DataFrame(columns=["verdict", "emi_modules"])
    if len(tr):
        tr["verdict"] = tr.verdict.str.strip().str.lower()
    def final(r):
        if r.agree:
            return r.a, r.a_mod, "both reviewers"
        if r.row_id in tr.index:
            return tr.verdict[r.row_id], tr.emi_modules[r.row_id], "third reader"
        lo = r.a if HORDER[r.a] <= HORDER[r.b] else r.b
        return lo, (r.a_mod if lo == r.a else r.b_mod), "cautious (pending)"
    m[["final", "final_mod", "settled_by"]] = pd.DataFrame([final(r) for r in m.itertuples()], index=m.index)
    CATS = ["covered", "partly", "new", "unclear"]
    out = []
    for ref, g in m.groupby("ref"):
        j = g[g.final != "unclear"]
        comp, elec = j[j.type == "compulsory"], j[j.type == "elective"]
        comp_cr = g[g.type == "compulsory"].ects.sum()
        need_el = max(TOTAL_CREDITS[ref] - comp_cr, 0) if len(g[g.type == "elective"]) else 0
        sc = lambda x: x.final.map(HSCORE)
        num_c, den_c = (comp.ects * sc(comp)).sum(), comp.ects.sum()
        el_mean = sc(elec).mean() if len(elec) else 0.0
        el_best = sc(elec).sort_values(ascending=False) if len(elec) else pd.Series(dtype=float)
        # best / worst: fill the needed elective credits with the best / worst marked electives (5-credit modules)
        k = int(round(need_el / 5)) if need_el else 0
        best = el_best.head(k).mean() if k else 0.0
        worst = el_best.tail(k).mean() if k else 0.0
        ov = lambda e: (num_c + e * need_el) / (den_c + need_el) if den_c + need_el else float("nan")
        # one-programme share: covered credits (compulsory + elective share) by the EMI programme of the first named module
        cov = comp[comp.final == "covered"].copy()
        cov["prog"] = cov.final_mod.astype(str).str.split().str[0].map(cat.programme)
        by = cov.groupby("prog").ects.sum()
        one = (by.max() / (den_c + need_el)) if len(by) else 0.0
        out.append({"ref": ref, "kind": g.kind.iloc[0], "reference": g.reference.iloc[0], "modules": len(g),
                    "agreement": g.agree.mean(), "kappa": kappa(g.a.where(g.a.isin(CATS)), g.b.where(g.b.isin(CATS))),
                    "unclear": int((g.final == "unclear").sum()), "compulsory_overlap": num_c / den_c if den_c else float("nan"),
                    "overlap": ov(el_mean), "overlap_best_electives": ov(best), "overlap_worst_electives": ov(worst),
                    "new_teaching_credits": float(((1 - sc(comp)) * comp.ects).sum() + (1 - el_mean) * need_el),
                    "one_programme": one, "one_programme_name": by.idxmax() if len(by) else "",
                    "pending": int((g.settled_by == "cautious (pending)").sum())})
    R = pd.DataFrame(out)
    R["passes"] = R.overlap.between(0.40, 0.80) & (R.one_programme <= 0.80)
    m.to_csv(VDIR / "handbook_rows.csv", index=False)
    R.to_csv(VDIR / "handbook_results.csv", index=False)
    return R, m
