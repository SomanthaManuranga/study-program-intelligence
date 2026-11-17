"""Cross-check engine: rules -> results, with a log of why each programme kind is removed.

prepare()  slow (about 15 s): loads the data, builds topic profiles and the text-similarity arrays, demand, region and
           job tables. Independent of the rules; cached in data/interim/crosscheck/prepared.pkl.
run(prep, rules)  fast (under 1 s): applies every rule, scores, weights and the Monte Carlo; returns all tables plus
           the drop log. Used by the CLI (steps.py) and by the web app (app_crosscheck/).
"""

from __future__ import annotations

import copy
import hashlib
import pickle
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import yaml

from . import steps as S
from . import timetable_link as TL
from .common import EMI_PROGRAMME_NAMES, OUT, PROCESSED, RAW, REPO, load_universe

RULES_FILE = REPO / "configs" / "crosscheck_rules.yaml"
CACHE = OUT / "prepared.pkl"
INPUTS = [PROCESSED / "programmes_full.csv", REPO / "data" / "interim" / "modules_emi_2026.csv",
          RAW / "destatis" / "21311-0015_BY.csv", RAW / "destatis" / "21321-0006_BY.csv",
          REPO / "data" / "interim" / "timetable_modules.csv"]
CRITERIA = ["demand", "labour", "fit", "feasibility", "differentiation", "regional"]


def agreed_rules() -> dict:
    return yaml.safe_load(RULES_FILE.read_text(encoding="utf-8"))


def rules_differ(rules: dict, base: dict | None = None) -> list[str]:
    """Paths of rule values that differ from the agreed rules (for the what-if banner)."""
    base = base or agreed_rules()
    out = []

    def walk(a, b, path):
        if isinstance(b, dict):
            for key in b:
                walk(a.get(key) if isinstance(a, dict) else None, b[key], f"{path}.{key}" if path else key)
        elif a != b and not (isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(a - b) < 1e-9):
            out.append(f"{path}: {b} -> {a}")
    walk(rules, base, "")
    return out


# ----------------------------------------------------------------------------- prepare (slow, cached)
@dataclass
class Prepared:
    kinds: pd.DataFrame                 # one row per kind: subject, level, co-occurrence, relabel names, demand, region, jobs
    topics: dict                        # kind -> list[(topic, offers_listing)]
    best_all: dict                      # kind -> array (topics,) best similarity to any EMI module
    best_prog: dict                     # kind -> array (topics, programmes) best similarity per EMI programme
    best_module: dict                   # kind -> list of (module title, programme name) of the best match per topic
    programmes: list                    # EMI programme ids (columns of best_prog)
    universe_size: int
    sources: pd.DataFrame               # data source register for the app
    fingerprint: str = ""
    meta: dict = field(default_factory=dict)
    tt: dict = field(default_factory=dict)   # same three arrays with only timetable-scheduled modules, + "link", "best_idx"


def _fingerprint() -> str:
    h = hashlib.sha1()
    for p in INPUTS:
        st = p.stat()
        h.update(f"{p.name}{st.st_size}{int(st.st_mtime)}".encode())
    for p in sorted((REPO / "src" / "study_program_intelligence" / "crosscheck").glob("*.py")):
        if p.name in ("steps.py", "common.py", "engine.py", "timetable_link.py"):
            h.update(p.read_bytes())
    return h.hexdigest()[:12]


def prepare(force: bool = False) -> Prepared:
    fp = _fingerprint()
    if CACHE.exists() and not force:
        try:
            prep = pickle.loads(CACHE.read_bytes())
            if prep.fingerprint == fp:
                return prep
        except Exception:   # cache from another Python/pandas version: rebuild
            pass
    u = load_universe()
    k = S.step1(u)                                       # subject x level, co-occurrence (threshold applied in run)
    # relabel names: OTH programmes of the same level carrying the subject or its name
    modules = pd.read_csv(REPO / "data" / "interim" / "modules_emi_2026.csv")
    modules = modules[modules.title.notna()].reset_index(drop=True)
    kt = S.kind_topics(u, k)
    match = S.build_matcher(modules)
    progs = sorted(modules.programme_id.unique())
    tlink = TL.link(modules)
    sched = tlink.scheduled.to_numpy()
    best_all, best_prog, best_module = {}, {}, {}
    tt = {"best_all": {}, "best_prog": {}, "best_module": {}, "best_idx": {}, "best_idx_hb": {}, "link": tlink}
    for kind, tp in kt.items():
        if not tp:
            for d in (best_all, tt["best_all"]):
                d[kind] = np.zeros(0)
            for d in (best_prog, tt["best_prog"]):
                d[kind] = np.zeros((0, len(progs)))
            best_module[kind], tt["best_module"][kind], tt["best_idx"][kind], tt["best_idx_hb"][kind] = [], [], [], []
            continue
        sims = match([t for t, _ in tp])
        for target, S_ in ((None, sims), ("tt", np.where(sched[None, :], sims, -1.0))):
            ba = S_.max(axis=1)
            bp = np.column_stack([S_[:, (modules.programme_id == p).values].max(axis=1) for p in progs])
            j = S_.argmax(axis=1)
            bm = [(modules.title.iloc[x], EMI_PROGRAMME_NAMES.get(modules.programme_id.iloc[x], "")) for x in j]
            if target is None:
                best_all[kind], best_prog[kind], best_module[kind] = ba, bp, bm
                tt["best_idx_hb"][kind] = j.tolist()
            else:
                tt["best_all"][kind], tt["best_prog"][kind], tt["best_module"][kind] = np.clip(ba, 0, None), np.clip(bp, 0, None), bm
                tt["best_idx"][kind] = j.tolist()
    # demand / region / jobs do not depend on the rules except through max_one_programme (applied in run)
    dummy = pd.DataFrame({"kind": k.kind, "n_topics": [len(kt[x]) for x in k.kind], "coverage": np.nan,
                          "near": np.nan, "max_one_programme": np.nan, "max_programme": ""})
    kk = S.step4(u, k, dummy)
    kk = S.step5(u, kk)
    kk = S.step6(kk)
    drop_cols = [c for c in kk.columns if c.startswith("new_to_oth_")] + ["coverage", "near", "max_one_programme",
                                                                          "max_programme"]
    kk = kk.drop(columns=drop_cols)
    prep = Prepared(kinds=kk, topics=kt, best_all=best_all, best_prog=best_prog, best_module=best_module, tt=tt,
                    programmes=progs, universe_size=len(u), sources=_sources(u, modules), fingerprint=fp,
                    meta={"emi_subjects": S.log["step1"]["emi_subjects"], "step6_places": S.log.get("step6_places")})
    OUT.mkdir(parents=True, exist_ok=True)
    CACHE.write_bytes(pickle.dumps(prep))
    return prep


def _sources(u: pd.DataFrame, modules: pd.DataFrame) -> pd.DataFrame:
    jobs = list((RAW / "jobsuche_funnel" / "2026-11-15").glob("*.json"))
    return pd.DataFrame([
        {"source": "Programme catalogue (Hochschulkompass data via the Federal Employment Agency study search)",
         "used_for": "Steps 1-3, 5: which programmes exist, where, their subjects and focus topics",
         "size": f"{len(u):,} full-time bachelor/master offers (of 22,093)", "file": "data/processed/programmes_full.csv",
         "limits": "about half of the offers list no focus topics"},
        {"source": "EMI module handbooks (OTH, public)", "used_for": "Steps 2-3: what EMI already teaches",
         "size": f"{len(modules)} modules in {modules.programme_id.nunique()} programmes",
         "file": "data/interim/modules_emi_2026.csv", "limits": "two international masters only partly documented"},
        {"source": "Destatis 21311: first-year students by subject and Land", "used_for": "Steps 4-5: demand, trend, south gap",
         "size": "WS 2005-2025, German / foreign", "file": "data/raw/destatis/21311-0015_*.csv",
         "limits": "no split bachelor/master; 2025 is the Bavarian G9 gap year (left out)"},
        {"source": "Destatis 21321: graduates by subject, Bavaria", "used_for": "Step 4: master pipeline",
         "size": "exam years 2009-2025", "file": "data/raw/destatis/21321-0006_BY.csv", "limits": "all degree types"},
        {"source": "Federal Employment Agency job board", "used_for": "Step 6: job ads near Amberg",
         "size": f"{len(jobs):,} replies of 15 Nov 2026", "file": "data/raw/jobsuche_funnel/2026-11-15/",
         "limits": "one day; counts of a word, not vacancies"},
        {"source": "EMI timetables WS 2026/27 and SS 2026 (supervisor, INTERNAL)",
         "used_for": "staff capability (lecturers as codes only)", "size": "1,028 entries, 255 modules",
         "file": "data/raw/oth_internal/ (never published)", "limits": "who teaches, not who could teach"},
    ])


# ----------------------------------------------------------------------------- run (fast)
def _coverage(w, best, tau, near_ratio):
    cov = (w * (best >= tau)).sum() / w.sum()
    near = (w * ((best >= near_ratio * tau) & (best < tau))).sum() / w.sum()
    return cov, near


def basis(prep: Prepared, name: str):
    """(best_all, best_prog, best_module) for the chosen module basis."""
    if name == "timetable":
        return prep.tt["best_all"], prep.tt["best_prog"], prep.tt["best_module"]
    return prep.best_all, prep.best_prog, prep.best_module


def calibrate(prep: Prepared, near_ratio: float, min_topics: int, basis_name: str = "handbook") -> dict:
    best_all = basis(prep, basis_name)[0]
    k = prep.kinds
    ok = lambda x: len(prep.topics[x]) >= min_topics
    pos = [x for x in k[k.emi_subject].kind if ok(x)]
    neg = [x for x in k.kind if x.split(" | ")[0] in S.NEG_CONTROLS and ok(x)]
    best = None
    for tau in np.round(np.arange(0.05, 0.61, 0.01), 2):
        f = lambda xs: np.mean([_coverage(np.array([n for _, n in prep.topics[x]], float), best_all[x], tau,
                                          near_ratio)[0] for x in xs])
        mp, mn = f(pos), f(neg)
        if best is None or mp - mn > best["gap"]:
            best = {"tau": float(tau), "mean_pos": mp, "mean_neg": mn, "gap": mp - mn, "n_pos": len(pos), "n_neg": len(neg)}
    return best


def run(prep: Prepared, rules: dict) -> dict:
    r1, r2, r3, r4, r7 = (rules[k] for k in ("step1_universe", "step2_relabel", "step3_fit", "step4_demand", "step7_ranking"))
    r5 = rules.get("step5_region", {"competition_radius_km": 150})
    r6 = rules.get("step6_jobs", {"job_region": "amberg_100km", "min_jobs": 0})
    comp_col = f"within_{int(r5['competition_radius_km'])}km"
    job_col = {"amberg_100km": "jobs_100km", "bayern": "jobs_bavaria", "germany": "jobs_germany"}[r6["job_region"]]
    bname = r3.get("module_basis", "handbook")
    B_all, B_prog, _ = basis(prep, bname)
    cal = calibrate(prep, r3["near_ratio"], r1["min_topics"], bname)
    tau = cal["tau"] if r3["tau"] == "auto" else float(r3["tau"])
    k = prep.kinds.copy()
    k["n_topics"] = [len(prep.topics[x]) for x in k.kind]
    cov, near, mone, mprog = [], [], [], []
    for x in k.kind:
        tp = prep.topics[x]
        if len(tp) < r1["min_topics"]:
            cov.append(np.nan); near.append(np.nan); mone.append(np.nan); mprog.append("")
            continue
        w = np.array([n for _, n in tp], float)
        c, n = _coverage(w, B_all[x], tau, r3["near_ratio"])
        per = [(w * (B_prog[x][:, j] >= tau)).sum() / w.sum() for j in range(len(prep.programmes))]
        j = int(np.argmax(per))
        cov.append(c); near.append(n); mone.append(per[j]); mprog.append(EMI_PROGRAMME_NAMES.get(prep.programmes[j], ""))
    k["coverage"], k["near"], k["max_one_programme"], k["max_programme"] = cov, near, mone, mprog
    k["emi_fit"] = k.emi_subject | (k.co_occurrence >= r1["emi_fit_share"])
    k["relabel_risk"] = k.oth_programmes_same_subject.fillna("").ne("")
    ov = k.max_one_programme.fillna(0)
    k["new_to_oth"] = k.size_per_programme * (1 - r4["alpha"] * ov)

    # ---- drop log: every rule a kind fails, in order; the first one is "the" reason
    log = []

    def drop(mask, step, rule, value, threshold, text):
        for _, x in k[mask].iterrows():
            log.append({"kind": x.kind, "subject": x.subject, "level": x.level, "step": step, "rule": rule,
                        "value": value(x), "threshold": threshold, "reason": text(x)})

    pct = lambda v: "n/a" if pd.isna(v) else f"{v:.0%}"
    drop(~k.emi_fit, "1 Universe", "emi_fit_share", lambda x: round(x.co_occurrence, 3), r1["emi_fit_share"],
         lambda x: f"outside EMI's field: only {pct(x.co_occurrence)} of its offers also list an EMI subject "
                   f"(rule: at least {r1['emi_fit_share']:.0%})")
    drop(k.emi_fit & (k.n_topics < r1["min_topics"]), "1 Universe", "min_topics", lambda x: x.n_topics, r1["min_topics"],
         lambda x: f"too little topic data: {x.n_topics} focus items in the catalogue (rule: at least {r1['min_topics']})")
    gate = k.emi_fit & (k.n_topics >= r1["min_topics"])
    drop(gate & (k.max_one_programme > r2["max_one_programme"]), "2 Relabel", "max_one_programme",
         lambda x: round(x.max_one_programme, 3), r2["max_one_programme"],
         lambda x: f"relabelled: {pct(x.max_one_programme)} of its topics come from one EMI programme "
                   f"({x.max_programme}); rule: at most {r2['max_one_programme']:.0%}")
    gate &= ~(k.max_one_programme > r2["max_one_programme"])
    if r2["relabel_risk_action"] == "drop":
        drop(gate & k.relabel_risk, "2 Relabel", "relabel_risk_action", lambda x: "OTH programme(s)", "drop",
             lambda x: f"OTH already runs a programme in this subject or name: {x.oth_programmes_same_subject}")
        gate &= ~k.relabel_risk
    k["ranked"] = gate

    below = k.coverage < r3["band_low"]
    no_demand = k.new_to_oth.isna()
    small = k.new_to_oth < r4["min_cohort"]
    act3 = "dropped" if r3["below_band_action"] == "drop" else "not eligible"
    drop(gate & below, "3 Fit", "band_low", lambda x: round(x.coverage, 3), r3["band_low"],
         lambda x: f"{act3}: EMI covers only {pct(x.coverage)} of its topics (rule: at least {r3['band_low']:.0%}; "
                   f"below that it 'will cost us a lot of resources')")
    if r3["below_band_action"] == "drop":
        gate &= ~below
        k["ranked"] = gate
    drop(gate & no_demand, "4 Demand", "destatis_mapping", lambda x: "none", "a Destatis subject",
         lambda x: "not eligible: no student statistics for this subject")
    drop(gate & ~no_demand & small, "4 Demand", "min_cohort", lambda x: round(x.new_to_oth, 1), r4["min_cohort"],
         lambda x: f"not eligible: about {x.new_to_oth:.0f} first-years new to OTH a year (rule: at least {r4['min_cohort']})")
    few_jobs = (k[job_col].fillna(0) < r6["min_jobs"]) if r6["min_jobs"] > 0 else pd.Series(False, index=k.index)
    drop(gate & ~below & ~no_demand & ~small & few_jobs, "6 Jobs", "min_jobs", lambda x: int(x[job_col] if x[job_col] == x[job_col] else 0),
         r6["min_jobs"], lambda x: f"not eligible: {0 if x[job_col] != x[job_col] else int(x[job_col])} job ads ({r6['job_region']}); "
                                   f"rule: at least {r6['min_jobs']}")
    k["eligible"] = gate & ~below & ~no_demand & ~small & ~few_jobs
    k["band"] = np.select([k.coverage < r3["band_low"], k.coverage > r3["band_high"]],
                          [f"below {r3['band_low']:.0%}", f"above {r3['band_high']:.0%}"],
                          f"{r3['band_low']:.0%}-{r3['band_high']:.0%}")
    k.loc[k.coverage.isna(), "band"] = "no topic data"

    # ---- scores, weights, Monte Carlo (per level)
    w = np.array([r7["weights"][c] for c in CRITERIA], float)
    w = w / w.sum()
    ranked = []
    for lvl, g in k[k.ranked].groupby("level"):
        g = g.copy()
        mix = r4["demand_mix_size"]
        g["s_demand"] = mix * S.quintile_score(g.new_to_oth) + (1 - mix) * S.quintile_score(g.trend_german)
        g["s_labour"] = S.quintile_score(g[job_col].astype(float))
        g["s_fit"] = S.quintile_score(g.coverage)
        g["s_feasibility"] = S.quintile_score(g.coverage + g.near)
        g["s_differentiation"] = S.quintile_score(g[comp_col].astype(float), higher_better=False)
        sg = g.south_gap.replace(np.inf, np.nan)
        g["s_regional"] = S.quintile_score(sg.fillna(sg.max()))
        Sm = g[[f"s_{c}" for c in CRITERIA]].to_numpy()
        g["score"] = Sm @ w
        rng = np.random.default_rng(int(r7["seed"]))
        W = rng.dirichlet(r7["dirichlet_concentration"] * w, int(r7["mc_draws"]))
        tot = Sm @ W.T
        el = g.eligible.to_numpy()
        g["p_first_all"] = np.bincount(tot.argmax(0), minlength=len(g)) / len(W)
        g["p_first_eligible"] = (np.bincount(np.where(el[:, None], tot, -np.inf).argmax(0), minlength=len(g)) / len(W)
                                 if el.any() else 0.0)
        g = g.sort_values("score", ascending=False)
        g["rank"] = range(1, len(g) + 1)
        g["shortlist"] = g["rank"] <= int(r7["shortlist_size"])
        ranked.append(g)
    ranking = pd.concat(ranked) if ranked else k.iloc[0:0]

    # ---- robustness: leave one criterion out (winner among eligible)
    loo = []
    for lvl, g in ranking.groupby("level"):
        e = g[g.eligible]
        if e.empty:
            continue
        base_winner = e.sort_values("score", ascending=False).iloc[0].subject
        for i, c in enumerate(CRITERIA):
            w2 = w.copy(); w2[i] = 0; w2 /= w2.sum()
            sc = e[[f"s_{x}" for x in CRITERIA]].to_numpy() @ w2
            loo.append({"level": lvl, "left_out": c, "winner": e.iloc[int(np.argmax(sc))].subject,
                        "same_as_base": e.iloc[int(np.argmax(sc))].subject == base_winner})
    winners = {lvl: (g[g.eligible].iloc[0].subject if g.eligible.any() else None) for lvl, g in ranking.groupby("level")}
    dl = pd.DataFrame(log)
    first = dl.groupby("kind").head(1) if len(dl) else dl
    funnel = []
    for lvl in ["BA", "MA"]:
        kl = k[k.level == lvl]
        funnel += [
            {"level": lvl, "stage": "All kinds (subject x level)", "remaining": len(kl)},
            {"level": lvl, "stage": "1 Fit EMI's field", "remaining": int(kl.emi_fit.sum())},
            {"level": lvl, "stage": "1 Enough topic data", "remaining": int((kl.emi_fit & (kl.n_topics >= r1['min_topics'])).sum())},
            {"level": lvl, "stage": "2 Not relabelled (ranked)", "remaining": int(kl.ranked.sum())},
            {"level": lvl, "stage": "3-6 Eligible (fit band, demand, cohort, jobs)", "remaining": int(kl.eligible.sum())},
        ]
    return {"kinds": k, "ranking": ranking, "drop_log": dl, "first_reason": first, "funnel": pd.DataFrame(funnel),
            "calibration": cal | {"tau_used": tau, "basis": bname}, "loo": pd.DataFrame(loo), "winners": winners,
            "changed": rules_differ(rules)}


def run_agreed(force: bool = False) -> dict:
    return run(prepare(force), agreed_rules())
