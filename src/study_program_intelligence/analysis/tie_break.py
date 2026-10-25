"""Demand tie-break: AR/VR & visual computing vs robotics path B (the two candidates that pass the gate).

Run from the repository root (after analysis.candidates):

    python -m study_program_intelligence.analysis.tie_break

Every demand signal for the two candidates, side by side, from data already collected (no new download):
- Destatis first-years 2019-24 (analysis/demand_split.py): the candidate's closest subjects, each subject alone and the
  broader pool, German and foreign, Bavaria and Germany;
- competitors (full catalogue, full-time bachelors, configs/candidates.yaml themes): counts and the nearest distances;
- international demand: foreign first-years (level, share, growth); the language of instruction of competitors is not
  in the catalogue (no field), so it is not compared;
- job ads: the existing snapshots (docs/jobsuche_snapshots.json) for keywords that match a candidate;
- search interest: the existing Google Trends downloads (docs/evidence_demand_trends.md);
- capture model: gross and net-new first-years (data/interim/candidate_scenarios.csv).
Outputs: data/interim/tie_break.csv (one row per signal, metric and candidate), reports/tie_break.md.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .candidates import config, matches, offers
from .demand_split import cagr, load as load_destatis

REPO_ROOT = Path(__file__).resolve().parents[3]
SNAPSHOTS = REPO_ROOT / "docs" / "jobsuche_snapshots.json"
SCEN = REPO_ROOT / "data" / "interim" / "candidate_scenarios.csv"
OUT = REPO_ROOT / "data" / "interim" / "tie_break.csv"
REPORT = REPO_ROOT / "reports" / "tie_break.md"
CANDIDATES = ("arvr", "robotics_b")
SERIES = {  # candidate: [(label, subject codes)]; the first is the series behind the trend score
    "arvr": [("Medieninformatik", ["SF121"]), ("Informatik (broad pool)", ["SF079"])],
    "robotics_b": [("Mechatronik + Technische Informatik", ["SF380", "SF123"]), ("Mechatronik", ["SF380"]),
                   ("Technische Informatik", ["SF123"])],
}
PROXY_SUBJECT = {"arvr": "Medieninformatik", "robotics_b": "Mechatronik|Technische Informatik"}   # catalogue subject names
JOB_KEYWORDS = {"arvr": ["virtual_reality", "augmented_reality", "computergrafik"], "robotics_b": ["robotik", "servicerobotik"]}


def destatis_rows(long: pd.DataFrame) -> list[dict]:
    rows = []
    for cand in CANDIDATES:
        for label, codes in SERIES[cand]:
            for region in ("BY", "DE"):
                d = long[(long["kind"] == "first-years") & (long["region"] == region) & long["code"].isin(codes)]
                p = d.pivot_table(index="year", columns="nationality", values="value", aggfunc="sum")
                for nat in ("German", "foreign"):
                    rows += [{"signal": "Destatis first-years", "candidate": cand, "series": label, "region": region, "group": nat,
                              "metric": m, "value": v} for m, v in
                             (("2019", int(p.at[2019, nat])), ("2024", int(p.at[2024, nat])),
                              ("%/yr 2019-24", round(cagr(p.at[2019, nat], p.at[2024, nat], 5), 1)))]
                tot = p["German"] + p["foreign"]
                rows += [{"signal": "Destatis first-years", "candidate": cand, "series": label, "region": region, "group": "all",
                          "metric": m, "value": v} for m, v in
                         (("2019", int(tot[2019])), ("2024", int(tot[2024])), ("%/yr 2019-24", round(cagr(tot[2019], tot[2024], 5), 1)),
                          ("foreign share 2024 %", int(round(100 * p.at[2024, "foreign"] / tot[2024]))))]
    return rows


def competition_rows() -> list[dict]:
    cfg = config()["candidates"]
    rows = []
    for cand in CANDIDATES:
        p = offers(cfg[cand])
        title, _ = matches(p, cfg[cand])
        d = p[title & ~p["is_oth"]].sort_values("km_oth")
        inst = d.drop_duplicates("institution")
        add = lambda m, v, sig="competition": rows.append({"signal": sig, "candidate": cand, "series": "", "region": "",
                                                           "group": "", "metric": m, "value": v})
        add("dedicated institutions Germany", inst["institution"].nunique())
        add("dedicated institutions Bavaria", inst.loc[inst["state"] == "Bayern", "institution"].nunique())
        add("dedicated institutions within 150 km", int((inst["km_oth"] <= 150).sum()))
        add("dedicated institutions within 80 km", int((inst["km_oth"] <= 80).sum()))
        for k, r in enumerate(inst.head(3).itertuples(), 1):
            add(f"nearest {k}", f"{r.institution} {r.km_oth:.0f} km")
        add("dedicated offers (Germany)", len(d))
        add("dedicated offers whose catalogue subject is the proxy subject", int(d["subjects"].fillna("").str.contains(PROXY_SUBJECT[cand]).sum()))
    return rows


def job_rows() -> list[dict]:
    s = pd.DataFrame(json.loads(SNAPSHOTS.read_text(encoding="utf-8")))
    rows = []
    for cand, keys in JOB_KEYWORDS.items():
        for k in keys:
            d = s[s["keyword_id"] == k]
            if d.empty:
                rows.append({"signal": "job ads", "candidate": cand, "series": k, "region": "", "group": "", "metric": "count",
                             "value": "no data: keyword added for the 1 Nov snapshot"})
                continue
            last = d[d["date"] == d["date"].max()]
            for r in last.itertuples():
                rows.append({"signal": "job ads", "candidate": cand, "series": k, "region": r.region_id, "group": "",
                             "metric": f"ads {r.date}", "value": int(r.total)})
    return rows


def capture_rows() -> list[dict]:
    sc = pd.read_csv(SCEN)
    rows = []
    for cand in CANDIDATES:
        t = sc[sc["option"] == cand].set_index("scenario")
        for col in ("gross first-years", "(b) net new to OTH"):
            rows.append({"signal": "capture model", "candidate": cand, "series": col, "region": "", "group": "",
                         "metric": "low / central / high", "value": " / ".join(f"{t.at[x, col]:.1f}" for x in ("low", "central", "high"))})
    return rows


def derived_rows(rows: list[dict]) -> list[dict]:
    """German first-years of the closest series per dedicated Bavarian competitor institution, and the German-only
    trend score (configs/candidates.yaml trend_rule)."""
    from .candidates import trend_score
    t = pd.DataFrame(rows)
    rule = config()["trend_rule"]
    out = []
    for cand in CANDIDATES:
        ser = SERIES[cand][0][0]
        g = lambda grp, m: t[(t["candidate"] == cand) & (t["series"] == ser) & (t["region"] == "BY") & (t["group"] == grp)
                              & (t["metric"] == m)]["value"].iloc[0]
        inst = t[(t["candidate"] == cand) & (t["metric"] == "dedicated institutions Bavaria")]["value"].iloc[0]
        out.append({"signal": "Destatis first-years", "candidate": cand, "series": ser, "region": "BY", "group": "German",
                    "metric": "2024 per dedicated Bavarian institution", "value": round(int(g("German", "2024")) / int(inst))})
        out.append({"signal": "Destatis first-years", "candidate": cand, "series": ser, "region": "BY", "group": "German",
                    "metric": "trend score (rule)", "value": trend_score(float(g("German", "%/yr 2019-24")), rule)["central"]})
    return out


def table() -> pd.DataFrame:
    rows = destatis_rows(load_destatis()) + competition_rows() + job_rows() + capture_rows()
    return pd.DataFrame(rows + derived_rows(rows))


def _md(df: pd.DataFrame) -> str:
    return "\n".join(["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
                     + ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)])


def main() -> None:
    t = table()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT, index=False)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(["# Demand tie-break: AR/VR vs robotics path B (generated)", "",
                                 *sum(([f"## {sig}", "", _md(t[t["signal"] == sig].drop(columns=["signal"])), ""]
                                       for sig in t["signal"].unique()), [])]), encoding="utf-8")
    pd.set_option("display.width", 250); pd.set_option("display.max_rows", 300)
    print(t.to_string(index=False))
    print(f"\nWritten: {OUT.relative_to(REPO_ROOT)}, {REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
