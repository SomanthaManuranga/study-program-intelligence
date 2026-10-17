"""Key numbers for the report, slides and dashboard (Step 50).

Run from the repository root (normally via report.build):

    python -m study_program_intelligence.report.key_numbers

Every number the report, slides and dashboard use is defined once here, with its source doc (the evidence doc that
states and explains it). Where the number comes from a generated table (data/interim), it is read from there, so a
rerun after the 4 Dec freeze updates it; otherwise it is taken from the evidence doc as stated there.
Check: each number's display text must occur verbatim in its source doc; the result is stored per number
(`in_source_doc`) and a summary is printed, so drift between data, docs and report is visible.
Output: reports/key_numbers.yaml.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT = REPO_ROOT / "reports" / "key_numbers.yaml"
INTERIM = REPO_ROOT / "data" / "interim"
DOCS = REPO_ROOT / "docs"
JOB_SNAPSHOT = "2026-10-15"   # snapshot the evidence doc's table shows; move to the frozen snapshot on 4 Dec
SECTIONS = ["A_demand", "B_capture", "C_fit", "D_outlet", "E_cannibalisation", "F_ranking"]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("‑", "-").replace("–", "-"))


def _found(probe: str, doc: str) -> bool:
    """Verbatim match that may not be part of a longer number (e.g. '191' inside '6,191')."""
    return re.search(r"(?<![\d.,])" + re.escape(probe) + r"(?![\d])", doc) is not None


class Numbers:
    def __init__(self) -> None:
        self.items: dict[str, dict] = {}
        self._docs: dict[str, str] = {}

    def add(self, key: str, section: str, label: str, value, display: str, source: str, *,
            unit: str = "", data: str | None = None, note: str | None = None, check: str | None = None) -> None:
        """display = how the report writes it; check = text searched in the source doc (default: display)."""
        if key in self.items:
            raise ValueError(f"duplicate key {key}")
        doc = self._docs.setdefault(source, _norm((REPO_ROOT / source).read_text(encoding="utf-8")))
        value = json.loads(json.dumps(value, default=lambda o: o.item()))   # numpy -> plain Python for YAML
        self.items[key] = {"section": section, "label": label, "value": value, "unit": unit, "display": display,
                           "source_doc": source, **({"data": data} if data else {}), **({"note": note} if note else {}),
                           "check": check or display, "in_source_doc": _found(_norm(check or display), doc)}


def _f(x: float, nd: int = 0) -> str:
    return f"{x:,.{nd}f}"


def collect() -> Numbers:
    n = Numbers()
    # ---------------- A: demand ----------------
    s = "docs/evidence_competition_demand.md"
    n.add("informatik_firstyears_by_growth", "A_demand", "Informatik first-years in Bavaria, growth per year 2019-2024", 6.1, "6.1 %",
          s, unit="%/yr", check="rose 6.1 % a year (2019–2024)")
    n.add("informatik_firstyears_de_2019", "A_demand", "Informatik first-years Germany 2019", 18586, "18,586", s)
    n.add("informatik_firstyears_de_2025", "A_demand", "Informatik first-years Germany 2025 (flat since 2023)", 21428, "21,428", s)
    fc = pd.read_csv(INTERIM / "forecast.csv")
    by = fc[fc["series"] == "BY cyber_proxy"].set_index("year")
    s = "docs/evidence_forecast.md"
    n.add("cyber_proxy_by_2024", "A_demand", "Bavaria cyber-proxy first-years 2024 (last training year)", 4936, "4,936", s,
          data="data/interim/forecast.csv")
    for y in (2030, 2035):
        kmk, drift = float(by.at[y, "KMK scenario"]), float(by.at[y, "drift (statistical)"])
        n.add(f"cyber_proxy_by_{y}_conservative", "A_demand", f"Bavaria cyber proxy {y}, conservative (KMK, constant share)",
              round(kmk), _f(kmk), s, data="data/interim/forecast.csv")
        n.add(f"cyber_proxy_by_{y}_central", "A_demand", f"Bavaria cyber proxy {y}, central (midpoint, a planning choice)",
              round((kmk + drift) / 2), _f((kmk + drift) / 2), s, data="data/interim/forecast.csv")
    n.add("forecast_mase_drift_by_cyber", "A_demand", "Backtest MASE of drift, Bavaria cyber proxy (naive 3.17)", 1.52, "1.52", s)
    s = "docs/evidence_demand_trends.md"
    n.add("search_cyber_vs_ki", "A_demand", "Search interest 'Cyber Security Studium' vs KI since 2022", 2, "about 2x KI", s)
    n.add("search_cyber_vs_robotik", "A_demand", "Search interest 'Cyber Security Studium' vs Robotik since 2022", 2.6, "2.6x Robotik", s)
    s = "docs/theme_precision.md"
    n.add("cyber_ba_germany", "A_demand", "Dedicated cybersecurity bachelors in Germany (hand-checked)", 31, "31", s,
          check="| Bachelor | 34 | 1 | 2 | **31** | 5 | 2 | 4 | 81 % |")
    n.add("cyber_ma_germany", "A_demand", "Dedicated cybersecurity masters in Germany (hand-checked)", 32, "32", s,
          check="| Master | 36 | 3 | 1 | **32** | 6 | 3 | 6 | 72 % |")
    n.add("cyber_ba_150km", "A_demand", "Dedicated cyber bachelors within 150 km of OTH", 4, "4", s, check="4 and 6 within 150 km")
    n.add("cyber_ma_150km", "A_demand", "Dedicated cyber masters within 150 km of OTH", 6, "6", s, check="4 and 6 within 150 km")
    n.add("cyber_focus_150km", "A_demand", "General programmes with a security focus area within 150 km", 18, "18", s,
          check="18 of them within 150 km")
    s = "docs/evidence_ranking.md"
    n.add("informatik_grads_by_2019", "A_demand", "Informatik graduates Bavaria 2019 (master pipeline)", 2676, "2,676", s)
    n.add("informatik_grads_by_2025", "A_demand", "Informatik graduates Bavaria 2025 (master pipeline)", 4788, "4,788", s)
    # ---------------- B: capture ----------------
    s = "docs/evidence_catchment.md"
    n.add("own_pool", "B_capture", "OTH's own pool of qualified school leavers per year", 5500, "about 5,500", s)
    n.add("own_pool_fosbos_share", "B_capture", "Share of the own pool via FOS/BOS", 40, "40 %", s, check="own pool 40 %")
    n.add("catchment_closer_to_oth", "B_capture", "Share of OTH's 100-km catchment closer to OTH than to Deggendorf", 91, "91 %", s)
    s = "docs/evidence_capture.md"
    n.add("gravity_beta", "B_capture", "Calibrated distance decay beta (Bavarian student flows)", 1.6, "1.6", s, check="Best beta = 1.6")
    n.add("gravity_r2", "B_capture", "Gravity model R2 on Bezirk x HAW flows", 0.95, "R2 0.95", s)
    n.add("thi_cyber_capacity", "B_capture", "THI Cybersicherheit planned capacity per year (anchor)", 25, "25", s,
          check="Kapazität 25 Studierende pro Studienjahr")
    n.add("deg_cyber_anecdote", "B_capture", "TH Deggendorf Cyber Security first-years (one student review, weak)", 60, "~60", s)
    n.add("min_cohort", "B_capture", "Minimum viable first-year cohort (assumption, no rule found)", 20, "20", s,
          check="Assumption: 20 first-years per year")
    cs = pd.read_csv(INTERIM / "capture_scenarios.csv").set_index("scenario")
    for k in ("low", "central", "high"):
        n.add(f"cyber_bsc_gross_{k}", "B_capture", f"Cyber B.Sc. first-years, steady state, {k}", int(cs.at[k, "gross first-years"]),
              str(int(cs.at[k, "gross first-years"])), s, data="data/interim/capture_scenarios.csv",
              check=f"**{int(cs.at[k, 'gross first-years'])}**")
    # ---------------- C: fit ----------------
    s = "docs/evidence_fit_modules.md"
    n.add("emi_cover_sec_ba", "C_fit", "EMI coverage of a cyber bachelor's security ECTS (e5, upper-end)", 31, "31 %", s, check="**31 %**")
    n.add("emi_cover_gen_ba", "C_fit", "EMI coverage of a cyber bachelor's general foundations", 71, "71 %", s,
          check="| Cyber bachelor vs EMI bachelors | **31 %** | 18-39 % | 47 % | 71 % |")
    n.add("emi_cover_sec_ma", "C_fit", "EMI coverage of a cyber master's security ECTS", 39, "39 %", s, check="**39 %**")
    s = "docs/evidence_fit_staff.md"
    n.add("new_professorships", "C_fit", "New professorships needed for the cyber B.Sc.", 2, "2 new professorships", s)
    n.add("teaching_load_sws", "C_fit", "Teaching load of a Bavarian HAW professor (§ 4 AVBayHIG)", 18, "18 SWS", s)
    s = "docs/evidence_benchmarks.md"
    n.add("draft_security_ects", "C_fit", "Security-specific ECTS in the draft OTH cyber B.Sc. (of 210)", 75, "75 (36 %)", s)
    n.add("draft_new_ects", "C_fit", "New ECTS taught by new staff in the draft", 45, "45 ECTS", s)
    n.add("draft_reused_ects", "C_fit", "Reused or adapted EMI module ECTS in the draft", 110, "110 ECTS", s)
    # ---------------- D: outlet ----------------
    snaps = pd.DataFrame(json.loads((DOCS / "jobsuche_snapshots.json").read_text(encoding="utf-8")))
    first = snaps[snaps["date"] == JOB_SNAPSHOT].pivot(index="keyword_id", columns="region_id", values="total")
    s = "docs/evidence_outlet_jobs.md"
    n.add("job_snapshot_date", "D_outlet", "Job-ad snapshot used in report, slides and dashboard (= table in the evidence doc)",
          JOB_SNAPSHOT, JOB_SNAPSHOT, s, data="docs/jobsuche_snapshots.json", check="15 and 17 Oct 2026")
    for kid, label in (("cyber_security", "Cyber Security"), ("ot_security", "OT Security"), ("robotik", "Robotik")):
        if kid not in first.index:
            continue
        r = first.loc[kid]
        share = 100 * r["bayern"] / r["germany"]
        row = (f"| {label} | {_f(r['germany'])} | {_f(r['bayern'])} | {_f(r['amberg_100km'])} | {_f(r['amberg_50km'])} "
               f"| {share:.1f} % |")   # the keyword's full row in the evidence doc's table
        n.add(f"ads_{kid}_de", "D_outlet", f"Job ads '{label}', Germany ({JOB_SNAPSHOT})", int(r["germany"]), _f(r["germany"]), s,
              data="docs/jobsuche_snapshots.json", check=row)
        n.add(f"ads_{kid}_by_share", "D_outlet", f"Job ads '{label}', Bavaria share of Germany", round(share, 1), f"{share:.1f} %", s,
              data="docs/jobsuche_snapshots.json", check=row)
        for reg in ("amberg_100km", "amberg_50km"):
            if reg in r.index:
                n.add(f"ads_{kid}_{reg}", "D_outlet", f"Job ads '{label}', within {reg.split('_')[1].replace('km', ' km')} of Amberg",
                      int(r[reg]), _f(r[reg]), s, data="docs/jobsuche_snapshots.json", check=row)
    n.add("it_jobs_by_growth", "D_outlet", "IT occupations in Bavaria, employees 2019-2023", 23.8, "+23.8 %", s)
    n.add("it_jobs_by_academic_growth", "D_outlet", "IT occupations in Bavaria with academic degree 2019-2023", 34.3, "+34.3 %", s)
    # ---------------- E: cannibalisation ----------------
    s = "docs/evidence_cannibalisation.md"
    for k in ("low", "central", "high"):
        n.add(f"cyber_bsc_netnew_{k}", "E_cannibalisation", f"Cyber B.Sc. net new first-years to OTH, {k}",
              float(cs.at[k, "(b) net new to OTH"]), f"{cs.at[k, '(b) net new to OTH']:.1f}", s, data="data/interim/capture_scenarios.csv")
        n.add(f"cyber_bsc_kept_{k}", "E_cannibalisation", f"Cyber B.Sc. students kept in the region, {k}",
              float(cs.at[k, "(c) kept in region"]), f"{cs.at[k, '(c) kept in region']:.1f}", s, data="data/interim/capture_scenarios.csv")
    n.add("cyber_bsc_from_oth_range", "E_cannibalisation", "Cyber B.Sc. share taken from OTH programmes (model variants)",
          [14, 27], "14-27 %", s, check="(14-27 %)")
    n.add("cyber_bsc_core_overlap", "E_cannibalisation", "Core security modules of the draft already in one OTH bachelor (kill rule 1: >50 %)",
          13, "13 %", s, check="= 13 %")
    os_ = pd.read_csv(INTERIM / "option_scenarios.csv")
    s = "docs/evidence_ranking.md"
    for opt in ("robotics_bsc", "cyber_msc"):
        d = os_[os_["option"] == opt].set_index("scenario")
        vals = [round(float(d.at[k, "(b) net new to OTH"])) for k in ("low", "central", "high")]
        n.add(f"{opt}_netnew", "E_cannibalisation", f"{opt} net new first-years low / central / high", vals,
              " / ".join(str(v) for v in vals), s, data="data/interim/option_scenarios.csv")
    # ---------------- F: ranking ----------------
    w = yaml.safe_load((REPO_ROOT / "configs" / "analysis.yaml").read_text(encoding="utf-8"))["weights"]
    n.add("weights", "F_ranking", "MCDA base weights", w, ", ".join(f"{k} {v:.2f}" for k, v in w.items()),
          "docs/evidence_ranking.md", data="configs/analysis.yaml", check="Demand (.30) | Labour (.20) | Fit (.20) | Feasibility (.15) | Differentiation (.10) | Regional (.05)")
    rs = pd.read_csv(INTERIM / "ranking_summary.csv")
    for scen, tag in (("base", "base"), ("robotics 50 % cannibalisation", "rob50"), ("base, robotics fit/feasibility 2/3/5", "skew")):
        d = rs[rs["scenario"] == scen].set_index("option")
        for opt in d.index:
            p = 100 * float(d.at[opt, "P(rank 1)"])
            n.add(f"p_rank1_{opt}_{tag}", "F_ranking", f"P(rank 1) {opt}, {scen}", round(p, 1), f"{p:.1f} %", s,
                  data="data/interim/ranking_summary.csv")
    loo = pd.read_csv(INTERIM / "ranking_loo.csv")
    b = loo[loo["scenario"] == "base"]
    lo = b.loc[b["P(rank 1) cyber_bsc"].idxmin()]
    n.add("loo_min_cyber_bsc", "F_ranking", f"Lowest P(rank 1) of the cyber B.Sc. in leave-one-out (without {lo['criterion left out']})",
          round(100 * lo["P(rank 1) cyber_bsc"], 1), f"{100 * lo['P(rank 1) cyber_bsc']:.1f} %", s, data="data/interim/ranking_loo.csv")
    n.add("loo_winner_always_cyber", "F_ranking", "Cyber B.Sc. first in every leave-one-out run", bool((b["winner"] == "cyber_bsc").all()),
          "first in every", s, data="data/interim/ranking_loo.csv", check="stays first whichever single criterion is left out")
    return n


def write(n: Numbers) -> dict:
    by_section = {sec: {k: v for k, v in n.items.items() if v["section"] == sec} for sec in SECTIONS}
    for sec in by_section.values():
        for v in sec.values():
            v.pop("section")
    missing = [k for k, v in n.items.items() if not v["in_source_doc"]]
    doc = {"generated_by": "python -m study_program_intelligence.report.key_numbers",
           "note": "Edit numbers only via the analysis modules or the evidence docs, never by hand here.",
           "n_numbers": len(n.items), "not_found_in_source_doc": missing, **by_section}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    return doc


def load() -> dict:
    """Flat {key: entry} view of reports/key_numbers.yaml for figures, outline and dashboard."""
    d = yaml.safe_load(OUT.read_text(encoding="utf-8"))
    return {k: v for sec in SECTIONS for k, v in d[sec].items()}


def main() -> None:
    n = collect()
    doc = write(n)
    print(f"Written: {OUT.relative_to(REPO_ROOT)} ({doc['n_numbers']} numbers)")
    if doc["not_found_in_source_doc"]:
        print("NOT found verbatim in their source doc:", ", ".join(doc["not_found_in_source_doc"]))
    else:
        print("All numbers found verbatim in their source doc.")


if __name__ == "__main__":
    main()
