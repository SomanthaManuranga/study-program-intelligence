"""Independent cross-check, Steps 1-7. Method fixed in docs/crosscheck/method.md before this code ran.

Run from the repository root:   python -m study_program_intelligence.crosscheck.steps
Outputs: data/interim/crosscheck/*.csv (working tables), docs/crosscheck/results.md (summary, no internal data).
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from .common import (DOCS, EMI_OFFERS, EMI_PROGRAMME_NAMES, EMI_SUBJECT_EXCLUDE, OUT, RAW, REPO,
                     destatis_match, load_universe, write)

FIT_SHARE = 0.25          # Step 1: share of a subject's offers that also list an EMI subject
ONE_PROG_MAX = 0.80       # Step 2
BAND = (0.40, 0.80)       # Step 3
NEAR_RATIO = 0.70         # tau_low = 0.7 * tau
MIN_TOPICS = 5
ALPHA = 0.5               # Step 4: share of overlapping students that would otherwise study at OTH
MIN_COHORT = 20
WEIGHTS = {"demand": .30, "labour": .20, "fit": .20, "feasibility": .15, "differentiation": .10, "regional": .05}
SOUTH = {"Bayern", "Baden-Württemberg"}
STATES = {"BW": "Baden-Württemberg", "BY": "Bayern", "BE": "Berlin", "BB": "Brandenburg", "HB": "Bremen",
          "HH": "Hamburg", "HE": "Hessen", "MV": "Mecklenburg-Vorpommern", "NI": "Niedersachsen",
          "NW": "Nordrhein-Westfalen", "RP": "Rheinland-Pfalz", "SL": "Saarland", "SN": "Sachsen",
          "ST": "Sachsen-Anhalt", "SH": "Schleswig-Holstein", "TH": "Thüringen"}
NEG_CONTROLS = ["Rechtswissenschaft", "Germanistik/Deutsch", "Geschichte", "Evangelische Theologie", "Biologie",
                "Psychologie", "Soziale Arbeit", "Kunstgeschichte, Kunstwissenschaft", "Anglistik/Englisch",
                "Sportwissenschaft"]
log: dict = {}


# ---------------------------------------------------------------- Step 1
def step1(u: pd.DataFrame) -> pd.DataFrame:
    emi_subj = set(s for xs in u[u.programme_id.astype(int).isin(EMI_OFFERS)].subj for s in xs) - EMI_SUBJECT_EXCLUDE
    rows = []
    ex = u.explode("subj").dropna(subset=["subj"])
    for (s, lvl), g in ex.groupby(["subj", "level"]):
        offers = u[u.programme_id.isin(g.programme_id)]
        co = offers.subj.map(lambda xs: bool(set(xs) & emi_subj)).mean()
        fit = s in emi_subj or co >= FIT_SHARE
        core = s.split(",")[0].strip().lower()
        oth_lvl = u[(u.is_oth == True) & (u.level == lvl)]
        oth_same = oth_lvl[oth_lvl.subj.map(lambda xs: s in xs) | oth_lvl.title.str.lower().str.contains(core, regex=False)].title
        rows.append({"kind": f"{s} | {lvl}", "subject": s, "level": lvl, "offers_de": len(offers),
                     "oth_programmes_same_subject": "; ".join(t.split(" Bachelor")[0].split(" Master")[0] for t in oth_same),
                     "institutions_de": offers.institution.nunique(), "emi_subject": s in emi_subj,
                     "co_occurrence": round(co, 3), "emi_fit": fit})
    k = pd.DataFrame(rows)
    log["step1"] = {"offers_fulltime_ba_ma": len(u), "kinds": len(k), "emi_subjects": sorted(emi_subj),
                    "kinds_emi_fit": int(k.emi_fit.sum())}
    write(k, "step1_kinds.csv")
    return k


# ---------------------------------------------------------------- Step 2/3: topics and matching
TOPIC_RE = re.compile(r"Schwerpunkte:\s*:\s*(.*?)(?:Anmerkung der Hochschule|$)", re.S)


def topics_of(content) -> list[str]:
    if not isinstance(content, str):
        return []
    m = TOPIC_RE.search(content)
    if not m:
        return []
    items = [t.strip(" .;:-").lower() for t in re.split(r",\s+(?=[A-ZÄÖÜ0-9])|;", m.group(1))]
    return [t for t in items if 2 < len(t) < 90]


def kind_topics(u: pd.DataFrame, k: pd.DataFrame) -> dict[str, list[tuple[str, int]]]:
    ex = u.explode("subj").dropna(subset=["subj"])
    out = {}
    for _, r in k.iterrows():
        ids = ex[(ex.subj == r.subject) & (ex.level == r.level)].programme_id
        c = Counter(t for content in u[u.programme_id.isin(ids)].content for t in set(topics_of(content)))
        keep = [(t, n) for t, n in c.most_common() if n >= 2][:40]
        if len(keep) < MIN_TOPICS:
            keep = c.most_common(30)
        out[r.kind] = keep
    return out


def build_matcher(modules: pd.DataFrame):
    docs = ((modules.title.fillna("") + " ") * 3 + modules.text.fillna("").str[:2000]).tolist()
    w = TfidfVectorizer(analyzer="word", lowercase=True, token_pattern=r"(?u)\b\w\w+\b", sublinear_tf=True, min_df=1)
    c = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), lowercase=True, sublinear_tf=True, min_df=2)
    w.fit(docs)
    c.fit(docs)

    def vec(texts):
        return normalize(hstack([w.transform(texts), c.transform(texts)]).tocsr())

    M = vec(docs)
    return lambda texts: (vec(texts) @ M.T).toarray()


def coverage(topics, sims, modules, tau, programme=None):
    if len(topics) < MIN_TOPICS:
        return np.nan, np.nan
    w = np.array([n for _, n in topics], float)
    S = sims if programme is None else sims[:, (modules.programme_id == programme).values]
    best = S.max(axis=1) if S.shape[1] else np.zeros(len(topics))
    cov = (w * (best >= tau)).sum() / w.sum()
    near = (w * ((best >= NEAR_RATIO * tau) & (best < tau))).sum() / w.sum()
    return cov, near


def step2_3(u, k, modules):
    kt = kind_topics(u, k)
    match = build_matcher(modules)
    sims = {kind: (match([t for t, _ in tp]) if tp else np.zeros((0, len(modules)))) for kind, tp in kt.items()}

    # calibration of tau on controls, before any candidate is scored
    pos = [kd for kd in k[k.emi_subject].kind if len(kt[kd]) >= MIN_TOPICS]
    neg = [kd for kd in k.kind if kd.split(" | ")[0] in NEG_CONTROLS and len(kt[kd]) >= MIN_TOPICS]
    grid = np.round(np.arange(0.05, 0.61, 0.01), 2)
    gaps = []
    for tau in grid:
        mp = np.nanmean([coverage(kt[x], sims[x], modules, tau)[0] for x in pos])
        mn = np.nanmean([coverage(kt[x], sims[x], modules, tau)[0] for x in neg])
        gaps.append((mp - mn, tau, mp, mn))
    gap, tau, mp, mn = max(gaps)
    log["calibration"] = {"positives": pos, "negatives": neg, "tau": float(tau), "tau_low": round(NEAR_RATIO * tau, 3),
                          "mean_cov_positives": round(mp, 3), "mean_cov_negatives": round(mn, 3), "gap": round(gap, 3)}

    progs = sorted(modules.programme_id.unique())
    rows, hand = [], []
    for _, r in k.iterrows():
        tp, S = kt[r.kind], sims[r.kind]
        cov, near = coverage(tp, S, modules, tau)
        per = {p: coverage(tp, S, modules, tau, p)[0] for p in progs}
        pmax = max(per, key=lambda p: -1 if np.isnan(per[p]) else per[p]) if len(tp) >= MIN_TOPICS else None
        rows.append({"kind": r.kind, "n_topics": len(tp), "coverage": cov, "near": near,
                     "max_one_programme": per[pmax] if pmax else np.nan,
                     "max_programme": EMI_PROGRAMME_NAMES.get(pmax, "") if pmax else ""})
        for i, (t, n) in enumerate(tp):
            j = int(S[i].argmax()) if S.shape[1] else -1
            hand.append({"kind": r.kind, "topic": t, "offers_listing": n, "best_emi_module": modules.title.iloc[j],
                         "programme": EMI_PROGRAMME_NAMES.get(modules.programme_id.iloc[j], ""),
                         "similarity": round(float(S[i, j]), 3),
                         "auto": "covered" if S[i, j] >= tau else ("near" if S[i, j] >= NEAR_RATIO * tau else "new")})
    c = pd.DataFrame(rows)
    write(c, "step2_3_coverage.csv")
    return c, pd.DataFrame(hand)


# ---------------------------------------------------------------- Step 4: demand
def destatis_series(path, kind="first"):
    d = pd.read_csv(path, sep=";", dtype=str)
    if kind == "first":
        d = d[d["3_variable_attribute_label"] == "Insgesamt"]
        d["year"] = d.time.str[:4].astype(int)
        d["nat"] = d["2_variable_attribute_label"]
        d["fach"] = d["4_variable_attribute_label"]
    else:   # graduates: passed exams, sum over sex
        d = d[d["4_variable_attribute_label"] == "Bestandene Prüfung"]
        d["year"] = d.time.astype(int)
        d["nat"] = d["2_variable_attribute_label"]
        d["fach"] = d["5_variable_attribute_label"]
    d["v"] = pd.to_numeric(d.value.str.replace("-", "0").str.replace(".", "0", regex=False), errors="coerce").fillna(0)
    t = d.groupby(["fach", "year", "nat"]).v.sum().unstack("nat").fillna(0)
    if "Insgesamt" not in t:
        t["Insgesamt"] = t.get("Deutsche", 0) + t.get("Ausländer", 0)
    return t.reset_index()


def cagr(a, b, n):
    return (b / a) ** (1 / n) - 1 if a > 0 and b > 0 else np.nan


def step4(u, k, c):
    fy = destatis_series(RAW / "destatis" / "21311-0015_BY.csv", "first")
    gr = destatis_series(RAW / "destatis" / "21321-0006_BY.csv", "grad")
    labels = sorted(fy.fach.unique())
    ex = u.explode("subj").dropna(subset=["subj"])
    k = k.merge(c, on="kind")
    k["destatis"], k["map_quality"] = zip(*k.subject.map(lambda s: destatis_match(s, labels)))
    # denominator: Bavarian offers (same level) of all catalogue subjects that map to the same Destatis pool
    by = ex[ex.state == "Bayern"]
    pool_offers = defaultdict(set)
    for _, r in k.iterrows():
        if r.destatis:
            ids = by[(by.subj == r.subject) & (by.level == r.level)].programme_id
            pool_offers[(r.destatis, r.level)].update(ids)
    out = []
    for _, r in k.iterrows():
        rec = {"kind": r.kind}
        if r.destatis:
            if r.level == "BA":
                s = fy[fy.fach == r.destatis].set_index("year")
                y0, y1 = 2019, 2024
            else:
                s = gr[gr.fach == r.destatis].set_index("year")
                y0, y1 = 2019, 2025
            if y1 in s.index and y0 in s.index:
                size_pool = s.loc[y1, "Insgesamt"]
                n_off = max(1, len(pool_offers[(r.destatis, r.level)]))
                rec.update(pool=size_pool, pool_german=s.loc[y1, "Deutsche"], bavarian_offers_in_pool=n_off,
                           size_per_programme=size_pool / n_off,
                           trend_total=cagr(s.loc[y0, "Insgesamt"], s.loc[y1, "Insgesamt"], y1 - y0),
                           trend_german=cagr(s.loc[y0, "Deutsche"], s.loc[y1, "Deutsche"], y1 - y0),
                           trend_foreign=cagr(s.loc[y0, "Ausländer"], s.loc[y1, "Ausländer"], y1 - y0))
                ov = 0 if np.isnan(r.max_one_programme) else r.max_one_programme
                for a in (0.25, ALPHA, 0.75):
                    rec[f"new_to_oth_a{int(a * 100)}"] = rec["size_per_programme"] * (1 - a * ov)
        out.append(rec)
    d = pd.DataFrame(out)
    write(k.merge(d, on="kind")[["kind", "destatis", "map_quality"] + list(d.columns[1:])], "step4_demand.csv")
    return k.merge(d, on="kind")


# ---------------------------------------------------------------- Step 5: region
def step5(u, k):
    ex = u.explode("subj").dropna(subset=["subj"])
    # first-years by subject and Land (2024), for the south gap
    fy_land = {}
    for code, land in STATES.items():
        p = RAW / "destatis" / f"21311-0015_{code}.csv"
        if p.exists():
            t = destatis_series(p, "first")
            fy_land[land] = t[t.year == 2024].set_index("fach").Insgesamt
    rows = []
    for _, r in k.iterrows():
        g = ex[(ex.subj == r.subject) & (ex.level == r.level) & (ex.is_oth != True)]
        rec = {"kind": r.kind, "within_100km": int((g.km_oth <= 100).sum()), "within_150km": int((g.km_oth <= 150).sum()),
               "in_bavaria": int((g.state == "Bayern").sum()), "nearest_km": float(g.km_oth.min()) if len(g) else np.nan}
        if r.destatis and fy_land:
            fs = sum(fy_land[l].get(r.destatis, 0) for l in fy_land if l in SOUTH)
            fr = sum(fy_land[l].get(r.destatis, 0) for l in fy_land if l not in SOUTH)
            os_, or_ = (g.state.isin(SOUTH)).sum(), (~g.state.isin(SOUTH)).sum()
            if fs > 0 and fr > 0 and os_ + or_ > 0:
                rec["south_gap"] = ((or_ / fr) / (os_ / fs)) if os_ > 0 else np.inf
        rows.append(rec)
    d = pd.DataFrame(rows)
    write(d, "step5_region.csv")
    return k.merge(d, on="kind")


# ---------------------------------------------------------------- Step 6: jobs
def step6(k):
    folder = RAW / "jobsuche_funnel" / "2026-11-15"
    counts = defaultdict(dict)
    places = Counter()
    for f in folder.glob("*.json"):
        j = json.loads(f.read_text(encoding="utf-8"))
        rep = j.get("reply") or {}
        counts[j["keyword"]][j["region"]] = rep.get("maxErgebnisse")
        if j["region"] == "amberg_100km":
            places[str(rep.get("woOutput", ""))[:80]] += 1
    log["step6_places"] = places.most_common(3)
    kws = set(counts)

    def terms(subject):
        parts = re.split(r"[,/]|\s-\s", subject)
        cand = [subject.lower()] + [p.strip(" -").lower() for p in parts if len(p.strip()) > 3]
        return [t for t in cand if t in kws]

    rows = []
    for _, r in k.iterrows():
        t = terms(r.subject)
        rec = {"kind": r.kind, "job_keyword": t[0] if t else ""}
        if t:
            best = max(t, key=lambda x: counts[x].get("amberg_100km") or 0)
            rec.update(job_keyword=best, jobs_100km=counts[best].get("amberg_100km"),
                       jobs_bavaria=counts[best].get("bayern"), jobs_germany=counts[best].get("germany"))
        rows.append(rec)
    d = pd.DataFrame(rows)
    write(d, "step6_jobs.csv")
    return k.merge(d, on="kind")


# ---------------------------------------------------------------- Step 7: ranking
def quintile_score(x: pd.Series, higher_better=True) -> pd.Series:
    r = x.rank(pct=True, method="average")
    if not higher_better:
        r = 1 - r + 1 / max(len(x.dropna()), 1)
    s = np.ceil(r * 5).clip(1, 5)
    return s.fillna(3)


def step7(k):
    k = k.copy()
    k["gate_fit"] = k.emi_fit
    k["gate_not_relabelled"] = ~(k.max_one_programme > ONE_PROG_MAX)
    k["relabel_risk"] = k.oth_programmes_same_subject.fillna("").ne("")
    k["gate_data"] = k.coverage.notna()
    k["band"] = np.select([k.coverage < BAND[0], k.coverage > BAND[1]], ["below 40 % (costly)", "above 80 %"], "40-80 %")
    k.loc[k.coverage.isna(), "band"] = "no topic data"
    k["new_to_oth"] = k[f"new_to_oth_a{int(ALPHA * 100)}"]
    k["min_cohort_ok"] = k.new_to_oth >= MIN_COHORT
    cand = k[k.gate_fit & k.gate_not_relabelled & k.gate_data].copy()
    res = []
    for lvl, g in cand.groupby("level"):
        g = g.copy()
        g["s_demand"] = (2 * quintile_score(g.new_to_oth) + quintile_score(g.trend_german)) / 3
        g["s_labour"] = quintile_score(g.jobs_100km.astype(float))
        g["s_fit"] = quintile_score(g.coverage)
        g["s_feasibility"] = quintile_score(g.coverage + g.near)
        g["s_differentiation"] = quintile_score(g.within_150km.astype(float), higher_better=False)
        g["s_regional"] = quintile_score(g.south_gap.replace(np.inf, np.nan).fillna(g.south_gap.replace(np.inf, np.nan).max()))
        S = g[[f"s_{c}" for c in WEIGHTS]].to_numpy()
        w = np.array(list(WEIGHTS.values()))
        g["score"] = S @ w
        rng = np.random.default_rng(42)
        W = rng.dirichlet(50 * w, 10000)
        eligible = (g.band != "below 40 % (costly)").values & g.min_cohort_ok.values
        tot = S @ W.T
        g["p_first_all"] = np.bincount(tot.argmax(0), minlength=len(g)) / 10000
        tot_e = np.where(eligible[:, None], tot, -np.inf)
        g["p_first_eligible"] = (np.bincount(tot_e.argmax(0), minlength=len(g)) / 10000) if eligible.any() else 0
        g["eligible"] = eligible
        res.append(g.sort_values("score", ascending=False))
    r = pd.concat(res)
    write(r, "step7_ranking.csv")
    log["step7"] = {lvl: {"candidates": int((r.level == lvl).sum()), "eligible": int(r[r.level == lvl].eligible.sum())}
                    for lvl in r.level.unique()}
    return k, r


# ---------------------------------------------------------------- report
def pct(x):
    return "" if pd.isna(x) else f"{x:.0%}"


def num(x, d=0):
    return "" if pd.isna(x) else (f"{x:,.{d}f}" if np.isfinite(x) else "none in south")


def report(k, r, hand):
    top = r.groupby("level").head(15)
    hand_top = hand[hand.kind.isin(top.kind)]
    hand_top = hand_top.assign(hand_verdict="", note="")
    write(hand_top, "hand_check_sheet.csv")
    L = ["# Independent cross-check: results v1 (provisional until the hand check)", "",
         "Method: `docs/crosscheck/method.md` (fixed before the code ran). Code: "
         "`python -m study_program_intelligence.crosscheck.steps`. Inputs: raw data and the cleaned catalogue only; "
         "the funnel's results were not read.", ""]
    s1 = log["step1"]
    cal = log["calibration"]
    L += ["## Funnel in numbers", "",
          f"- Full-time bachelor and master offers in Germany (teacher training removed): {s1['offers_fulltime_ba_ma']:,}",
          f"- Kinds (official subject x level): {s1['kinds']:,}; fit EMI (own subject or >= 25 % co-listed with an EMI "
          f"subject): {s1['kinds_emi_fit']}",
          f"- With enough topic data (>= {MIN_TOPICS} focus items): {int(k[k.emi_fit].coverage.notna().sum())}; "
          f"dropped as relabelled (> 80 % from one EMI programme): {int((k.emi_fit & (k.max_one_programme > ONE_PROG_MAX)).sum())}",
          f"- Ranked candidates: " + ", ".join(f"{lvl} {v['candidates']} (eligible: in band and >= {MIN_COHORT} new "
                                               f"students: {v['eligible']})" for lvl, v in log["step7"].items()), "",
          "## Matching threshold (calibrated before scoring)", "",
          f"tau = {cal['tau']} (near from {cal['tau_low']}). Mean coverage of subjects EMI already teaches: "
          f"{pct(cal['mean_cov_positives'])}; of clearly non-EMI subjects: {pct(cal['mean_cov_negatives'])}.", "",
          "## Control: subjects OTH already offers (Step 2 check)", "",
          "**The control fails.** Subjects OTH already teaches should come out above 80 % from one EMI programme; they "
          "range from 10 % to 93 %. Catalogue focus lists are short and generic, so they measure whether EMI touches a "
          "topic (topic fit), not how much of a curriculum one programme covers. **Consequence:** the 80 % copy test is "
          "NOT decided from catalogue topics. Kinds whose subject an OTH programme of the same level already lists are "
          "flagged 'relabel risk' and are tested first with real module handbooks (ECTS level) in the hand-check step. "
          "The 'topic fit' column is used only as a relative fit score.", "",
          "| Kind | Coverage | Max from one EMI programme | Programme | Dropped as relabelled? |", "|---|---|---|---|---|"]
    ctrl = k[k.emi_subject & k.coverage.notna()].sort_values("max_one_programme", ascending=False)
    L += [f"| {x.kind} | {pct(x.coverage)} | {pct(x.max_one_programme)} | {x.max_programme} | "
          f"{'yes' if x.max_one_programme > ONE_PROG_MAX else 'no'} |" for x in ctrl.itertuples()]
    for lvl in ["BA", "MA"]:
        g = r[r.level == lvl].head(15)
        L += ["", f"## Ranking {'bachelor' if lvl == 'BA' else 'master'} (top 15)", "",
              "| # | Kind | Score | P(first), eligible only | Topic fit (band) | Relabel risk: OTH programme in same subject | New to OTH / year | "
              "Trend German / foreign | Within 150 km | South gap | Jobs 100 km (keyword) |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
        for i, x in enumerate(g.itertuples(), 1):
            L.append(f"| {i} | {x.kind.split(' | ')[0]} | {x.score:.2f} | {pct(x.p_first_eligible) if x.eligible else 'not eligible'} | "
                     f"{pct(x.coverage)} ({x.band}) | {x.oth_programmes_same_subject or '-'} | {num(x.new_to_oth)} | "
                     f"{pct(x.trend_german)} / {pct(x.trend_foreign)} | {x.within_150km} | {num(x.south_gap, 2)} | "
                     f"{num(x.jobs_100km)} ({x.job_keyword}) |")
    L += ["", "## Comparison with the funnel (soma/funnel)", "",
          "Known before this method was written: only the funnel's headline from its plain-English PDF (general "
          "Informatik bachelor passes; cybersecurity bachelor in the band but needs outside teaching). Its tables, "
          "candidate lists and AI marks were not read.", "",
          "| Question | Funnel | This cross-check |", "|---|---|---|",
          "| Top bachelor | general Informatik | Informatik first, IT-Sicherheit a close second |",
          "| Cybersecurity | in the band, needs outside teaching (forensics, IT law, auditing) | IT-Sicherheit: no OTH programme in the subject, few competitors within 150 km; first among masters |",
          "| Is Informatik new to OTH? | yes (57 % would come from Medieninformatik, under the 80 % limit) | relabel risk: OTH already runs Industrie-4.0-Informatik and Kuenstliche Intelligenz in the same subject; must be tested with handbooks |",
          "| Candidates checked in depth | 6 | all EMI-fit kinds ranked (33 bachelor, 27 master); handbook test still to do |", "",
          "## What is still open", "",
          f"- **Hand check**: `data/interim/crosscheck/hand_check_sheet.csv` lists every topic match of the top 15 per "
          f"level ({len(hand_top)} rows). Fill `hand_verdict` with covered / near / new; the ranking is rerun with "
          "the hand verdicts.",
          "- Job counts come from the 15 Nov raw replies (keywords of the other analysis); subjects without a matching "
          "keyword get a neutral score.",
          "- Scores are relative (quintiles within each level), not absolute grades.", ""]
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "results.md").write_text("\n".join(L), encoding="utf-8")
    (OUT / "log.json").write_text(json.dumps(log, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    print("\n".join(L))


def main():
    u = load_universe()
    k = step1(u)
    modules = pd.read_csv(REPO / "data" / "interim" / "modules_emi_2026.csv")
    modules = modules[modules.title.notna()].reset_index(drop=True)
    c, hand = step2_3(u, k, modules)
    k = step4(u, k, c)
    k = step5(u, k)
    k = step6(k)
    k, r = step7(k)
    report(k, r, hand)


if __name__ == "__main__":
    main()
