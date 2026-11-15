"""Funnel step 5: are there jobs? (configs/funnel.yaml: labour; criteria in docs/criteria_funnel_step5.md)

Run from the repository root, each command from committed code on a clean tree, after analysis.funnel_units run:

    python -m study_program_intelligence.analysis.funnel_labour keywords          # keywords of every type, from its titles
    (commit docs/funnel_keywords.csv)
    python -m study_program_intelligence.analysis.funnel_labour fetch primary     # job-ad counts, one request per keyword and region
    python -m study_program_intelligence.analysis.funnel_labour fetch stress
    python -m study_program_intelligence.analysis.funnel_labour measure           # the measure per unit

Keywords are made by rule from the cleaned titles of a type's fitted members; nothing is added or struck by hand.
Counts come from the job board of the Federal Employment Agency (ingest/jobsuche.py: robots.txt, User-Agent, 2 s).
Outputs: docs/funnel_keywords.csv; data/raw/jobsuche_funnel/<date>/; data/interim/funnel2_job_counts.csv,
funnel2_labour.csv, funnel2_step5.json; reports/funnel2/step5_labour.md.
"""

from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter
from datetime import date

import numpy as np
import pandas as pd
import yaml

from .funnel_common import INTERIM, REPO_ROOT, REPORTS, config, md_table, run_stamp
from .funnel_types import OFFER_TYPES, normalise, sha
from .funnel_units import SCREEN, STEP3

STOPLIST = REPO_ROOT / "configs" / "funnel_title_stoplist.yaml"
KEYWORDS = REPO_ROOT / "docs" / "funnel_keywords.csv"
RAW = REPO_ROOT / "data" / "raw" / "jobsuche_funnel"
COUNTS, LABOUR, STEP5 = INTERIM / "funnel2_job_counts.csv", INTERIM / "funnel2_labour.csv", INTERIM / "funnel2_step5.json"
REGIONS = {"germany": {}, "bayern": {"wo": "Bayern"}, "amberg_100km": {"wo": "Amberg, Oberpfalz", "umkreis": 100}}     # labour.regions
AMBERG = (49.4537, 11.8481)     # the job board reads a bare "Amberg" as Amberg bei Buchloe; every reply's place is checked against this
SPLIT = re.compile(r"\s+(?:und|and)\s+|[&/,+]")           # labour.phrases
TOP, MIN_TITLES, GENERIC_SHARE = 3, 2, 0.05               # labour.keywords, labour.drop_generic
ALL_ADS = "(all ads)"


def title_parts(clean_title: str) -> list[str]:
    """Rule labour.phrases: the cleaned title without bracketed text, lower case, split at "und", "and", "&", "/", ","
    and "+"; hyphens stay ("elektro-" of "Elektro- und Informationstechnik"). A part needs a letter and at least 2
    characters."""
    t = re.sub(r"\([^)]*\)|\[[^\]]*\]", " ", str(clean_title)).lower()
    parts = [re.sub(r"\s+", " ", p).strip(" .:;") for p in SPLIT.split(t)]
    return [p for p in parts if len(p) >= 2 and re.search(r"[^\W\d_]", p)]


def stoplist() -> set[str]:
    s = yaml.safe_load(STOPLIST.read_text(encoding="utf-8"))
    return set(s["degree_words"]) | set(s["catalogue_words"])


def ranked_phrases(titles: list[str], drop: set[str]) -> list[tuple[str, int]]:
    """Phrases of a type with the number of member titles that have them as a part, without the dropped ones; most
    titles first, then alphabetical (labour.phrase_ties). A phrase is compared in the form of text.normalise and
    written as it is most often written."""
    n, forms = Counter(), {}
    for t in titles:
        for key in {normalise(p): p for p in title_parts(t)}.items():
            n[key[0]] += 1
            forms.setdefault(key[0], Counter())[key[1]] += 1
    out = [(sorted(forms[k].items(), key=lambda kv: (-kv[1], kv[0]))[0][0], c) for k, c in n.items() if k not in drop]
    return sorted(out, key=lambda kv: (-kv[1], kv[0]))


def keywords_of(titles: list[str], nearest_title: str, drop: set[str]) -> tuple[list[str], str]:
    """Rule labour.keywords: the 3 phrases with the highest share that occur in at least 2 member titles; if none occurs
    twice, the parts of the member nearest the centroid in title order, at most 3."""
    top = [p for p, c in ranked_phrases(titles, drop) if c >= MIN_TITLES][:TOP]
    if top:
        return top, "phrases in 2 or more titles"
    return [p for p in title_parts(nearest_title) if normalise(p) not in drop][:TOP], "parts of the member nearest the centroid"


def build_keywords(d: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    stop = stoplist()
    members = {int(c): g.sort_values("dist_to_assigned", kind="stable") for c, g in d[d["type"] >= 0].groupby("type")}
    first = {}
    for c, g in members.items():                  # the 3 highest-share phrases of a type; phrases tied with the third count too
        ranked = ranked_phrases(g["clean_title"].tolist(), stop)
        cut = ranked[TOP - 1][1] if len(ranked) >= TOP else 0
        first[c] = [normalise(p) for p, n in ranked if n >= cut]
    in_top = Counter(p for ps in first.values() for p in ps)
    generic = {p for p, n in in_top.items() if n > GENERIC_SHARE * len(members)}                   # labour.drop_generic, second part
    rows = []
    for c, g in members.items():
        kws, how = keywords_of(g["clean_title"].tolist(), g["clean_title"].iloc[0], stop | generic)
        counts = dict(ranked_phrases(g["clean_title"].tolist(), stop | generic))
        for rank, k in enumerate(kws, 1):
            rows.append({"type": c, "rank": rank, "keyword": k, "member titles with it": counts.get(k, 1), "members": len(g),
                         "share": round(counts.get(k, 1) / len(g), 3), "from": how})
        if not kws:
            rows.append({"type": c, "rank": 0, "keyword": "", "member titles with it": 0, "members": len(g), "share": 0.0, "from": "no keyword left"})
    return pd.DataFrame(rows), {"types": len(members), "stop list phrases": len(stop), "generic by the 5 % rule": sorted(generic)}


def keywords() -> None:
    stamp = run_stamp()
    d = pd.read_csv(OFFER_TYPES, low_memory=False, dtype={"programme_id": str})
    k, info = build_keywords(d)
    k.to_csv(KEYWORDS, index=False, lineterminator="\n")
    real = k[k["rank"] > 0]
    print(json.dumps({"commit": stamp["commit"], **info, "keyword rows": len(real), "distinct keywords": int(real["keyword"].nunique()),
                      "types without a keyword": int((k["rank"] == 0).sum()), "from": real.groupby("from")["type"].nunique().to_dict()}, indent=1, ensure_ascii=False))


def wanted(which: str) -> list[str]:
    """Distinct keywords of the types with a unit on the list, in type order."""
    s = pd.read_csv(SCREEN, float_precision="round_trip")
    types = set(s.loc[s[which], "type"])
    k = pd.read_csv(KEYWORDS, keep_default_na=False)
    return list(dict.fromkeys(k.loc[k["type"].isin(types) & (k["rank"] > 0), "keyword"]))


def fetch(which: str) -> None:
    """Rule labour.query and labour.regions: every keyword in every region, unquoted, plus all ads per region for the
    baseline share. A keyword and region already counted today is not asked again; an error is not stored."""
    from ..ingest.jobsuche import DELAY_SECONDS, _get, _total
    stamp = run_stamp()
    import subprocess
    if subprocess.run(["git", "status", "--porcelain", "--", str(KEYWORDS)], cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip() or not \
            subprocess.run(["git", "ls-files", str(KEYWORDS.relative_to(REPO_ROOT))], cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip():
        raise SystemExit("docs/funnel_keywords.csv must be committed before the first request (labour.stored_first)")
    endpoint = yaml.safe_load((REPO_ROOT / "configs" / "jobsuche.yaml").read_text(encoding="utf-8"))["endpoint"]
    import hashlib
    today = date.today().isoformat()
    folder = RAW / today
    folder.mkdir(parents=True, exist_ok=True)
    have = pd.read_csv(COUNTS, keep_default_na=False) if COUNTS.exists() else pd.DataFrame(columns=["date", "keyword", "region", "total", "keywords_file", "commit"])
    done = set(zip(have.loc[have["date"] == today, "keyword"], have.loc[have["date"] == today, "region"]))
    todo = [(k, r) for k in [ALL_ADS] + wanted(which) for r in REGIONS if (k, r) not in done]
    print(f"{which}: {len(todo)} requests to do on {today} ({len(done)} already counted today)", flush=True)
    rows, errors = [], 0
    for i, (k, r) in enumerate(todo, 1):
        params = {"was": None if k == ALL_ADS else k, **REGIONS[r], "angebotsart": 1, "page": 1, "size": 1}     # angebotsart 1: regular jobs of every level
        if date.today().isoformat() != today:
            raise SystemExit("the day changed during the run: a list is counted on one day (labour.query); run it again on one day")
        try:
            resp = _get(endpoint, params)
            if resp.status_code != 200:
                raise RuntimeError(f"HTTP {resp.status_code}")
            payload = resp.json()
            total = _total(payload)
            if total is None:
                raise RuntimeError("no total in the reply")
            if r == "amberg_100km":
                place = (payload.get("woOutput") or {}).get("koordinaten") or [{}]
                if abs(place[0].get("lat", 0) - AMBERG[0]) > 0.05 or abs(place[0].get("lon", 0) - AMBERG[1]) > 0.05:
                    raise RuntimeError(f"the reply is not centred on Amberg in der Oberpfalz: {payload.get('woOutput')}")
            (folder / f"{hashlib.sha256((k + '|' + r).encode()).hexdigest()[:16]}.json").write_text(json.dumps({"keyword": k, "region": r, "reply": payload}, ensure_ascii=False), encoding="utf-8")
            rows.append({"date": today, "keyword": k, "region": r, "total": int(total), "keywords_file": sha(KEYWORDS), "commit": stamp["commit"]})
        except Exception as exc:                                   # counted as missing; asked again by the next call
            errors += 1
            print(f"ERROR {k!r} {r}: {exc}", flush=True)
        if i % 100 == 0 or i == len(todo):
            pd.concat([have, pd.DataFrame(rows)], ignore_index=True).to_csv(COUNTS, index=False)
            print(f"{i} of {len(todo)} done, {errors} errors", flush=True)
        time.sleep(DELAY_SECONDS)
    pd.concat([have, pd.DataFrame(rows)], ignore_index=True).to_csv(COUNTS, index=False)
    print(f"{which}: {len(rows)} counts stored for {today}, {errors} errors", flush=True)


def measure() -> None:
    stamp = run_stamp()
    s = pd.read_csv(SCREEN, float_precision="round_trip")
    k = pd.read_csv(KEYWORDS, keep_default_na=False)
    c = pd.read_csv(COUNTS, keep_default_na=False)
    if not (c["keywords_file"] == sha(KEYWORDS)).all():
        raise SystemExit("some counts were fetched for another keyword file")
    latest = c.sort_values("date").drop_duplicates(["keyword", "region"], keep="last")
    table = latest.pivot(index="keyword", columns="region", values="total")
    day = latest.set_index("keyword")["date"].groupby(level=0).agg(lambda x: "; ".join(sorted(set(x))))
    base = table.loc[ALL_ADS]
    rows = []
    for r in s.itertuples():
        kws = k.loc[(k["type"] == r.type) & (k["rank"] > 0), "keyword"].tolist()
        got = [x for x in kws if x in table.index and table.loc[x].notna().all()]
        near = [float(table.at[x, "amberg_100km"]) for x in got]
        de, by = sum(table.at[x, "germany"] for x in got), sum(table.at[x, "bayern"] for x in got)
        rows.append({"type": r.type, "level": r.level, "primary": bool(r.primary), "stress": bool(r.stress), "central titles": s.at[r.Index, "central titles"],
                     "keywords": "; ".join(kws), "keywords with counts": len(got),
                     "ads within 100 km (median keyword)": float(np.median(near)) if near else np.nan,
                     "ads within 100 km (smallest keyword)": min(near) if near else np.nan, "ads within 100 km (largest keyword)": max(near) if near else np.nan,
                     "ads in Germany (sum of keywords)": de if got else np.nan, "ads in Bavaria (sum of keywords)": by if got else np.nan,
                     "Bavaria's share of the German ads": by / de if got and de > 0 else np.nan,
                     "labour input": "ok" if len(got) == len(kws) and kws else "missing: no keyword" if not kws else "missing counts",
                     "counted on": "; ".join(sorted({day[x] for x in got}))})
    out = pd.DataFrame(rows)
    out.to_csv(LABOUR, index=False)
    prim = out[out["primary"]]
    med = prim["ads within 100 km (median keyword)"]
    res = {"stamp": stamp, "step3_commit": json.loads(STEP3.read_text(encoding="utf-8"))["stamp"]["commit"], "keywords_file": sha(KEYWORDS),
           "units": len(out), "counts_stored": len(latest), "days": sorted(latest["date"].unique().tolist()),
           "all_ads": {r: int(base[r]) for r in REGIONS}, "bavaria_share_of_all_ads": round(float(base["bayern"] / base["germany"]), 4),
           "share_of_all_german_ads_within_100km": round(float(base["amberg_100km"] / base["germany"]), 4),
           "primary": {"units": len(prim), "labour input ok": int((prim["labour input"] == "ok").sum()), "missing": prim.loc[prim["labour input"] != "ok", "labour input"].value_counts().to_dict(),
                       "median of the measure": float(med.median()), "quartiles": [float(med.quantile(0.25)), float(med.quantile(0.75))],
                       "units with 0 ads within 100 km": int((med == 0).sum()), "units with 150 or more": int((med >= 150).sum()), "units below 10": int((med < 10).sum()),
                       "median Bavarian share": round(float(prim["Bavaria's share of the German ads"].median()), 4)},
           "stress": {"units": int(out["stress"].sum()), "labour input ok": int((out.loc[out["stress"], "labour input"] == "ok").sum())},
           "files": {LABOUR.name: sha(LABOUR), COUNTS.name: sha(COUNTS)}}
    STEP5.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    show = ["type", "level", "central titles", "keywords", "ads within 100 km (median keyword)", "ads within 100 km (largest keyword)", "ads in Germany (sum of keywords)", "Bavaria's share of the German ads", "labour input"]
    cut = lambda x: x.assign(**{"central titles": x["central titles"].str.slice(0, 60)})[show].round(3)
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "step5_labour.md").write_text("\n".join([
        "# Funnel step 5: job ads for every unit's keywords (generated)", "",
        f"Code commit {stamp['commit']}, run on {stamp['date']}; keyword file {res['keywords_file']}; counts of {res['days']}.", "",
        f"- All ads: {res['all_ads']}; Bavaria's share {res['bavaria_share_of_all_ads']:.1%}; within 100 km of Amberg {res['share_of_all_german_ads_within_100km']:.1%} of the German ads.",
        f"- Primary list: {res['primary']}.", f"- Stress list: {res['stress']}.", "",
        "## Primary list, by the measure", "", md_table(cut(prim.sort_values("ads within 100 km (median keyword)", ascending=False)))]) + "\n", encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    {"keywords": keywords, "measure": measure}[sys.argv[1]]() if sys.argv[1] != "fetch" else fetch(sys.argv[2])
