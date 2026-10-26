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
SECTIONS = ["M_method", "S_selection", "A_demand", "B_capture", "C_fit", "D_outlet", "E_cannibalisation", "F_ranking",
            "G_candidates", "H_tie_break"]


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("‑", "-").replace("–", "-").replace("−", "-"))


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
    # ---------------- S: selection funnel ----------------
    s = "docs/evidence_funnel.md"
    funnel = [("funnel_0_themes", "Stage 0: theme groups screened (14 Oct)", 9, "9 theme groups", "| 9 theme groups | - | 9 theme groups |"),
              ("funnel_1_demand", "Stage 1: after the demand-trend filter", 8, "8", "Medieninformatik -3.5 %/yr in Germany) | 8 |"),
              ("funnel_2_candidates", "Stage 2: candidates after the supply-gap filter", 5, "5 candidates", "| 3 themes = 5 candidates |"),
              ("funnel_3_shortlist", "Stage 3: shortlist after kill rule 1", 3, "3", "(identical to AI for Industrial Applications) | 3 |"),
              ("funnel_4_after_gates", "Stage 4: after kill rules 2-4", 3, "3", "Informatik graduates rising) | 3 |")]
    for key, label, v, disp, chk in funnel:
        n.add(key, "S_selection", label, v, disp, s, check=chk)
    n.add("funnel_offers", "S_selection", "Programme offers screened (13 study fields, 14 Oct)", 4840, "4,840", s)
    n.add("funnel_fields", "S_selection", "Catalogue study fields screened", 13, "13", s, check="4,840 programme offers from 13 study fields")
    n.add("funnel_subjects", "S_selection", "EMI-related Destatis subjects screened", 11, "11", s, check="11 EMI-related Destatis subjects")
    n.add("funnel_medientechnik", "S_selection", "Medientechnik first-years Germany, per year 2019-2025", -8.6, "-8.6 %", s, check="Medientechnik -8.6 %/yr")
    n.add("funnel_medieninformatik", "S_selection", "Medieninformatik first-years Germany, per year 2019-2025", -3.5, "-3.5 %", s, check="Medieninformatik -3.5 %/yr")
    n.add("funnel_ai_ba_150km", "S_selection", "AI/data bachelors within 150 km", 32, "32", s, check="32 BA / 34 MA within 150 km")
    n.add("funnel_ai_ma_150km", "S_selection", "AI/data masters within 150 km", 34, "34", s, check="32 BA / 34 MA within 150 km")
    n.add("funnel_micro_firstyears", "S_selection", "Mikroelektronik first-years Germany 2025 (watch list)", 116, "116", s, check="116 first-years in Germany 2025")
    n.add("funnel_embedded_overlap", "S_selection", "Embedded/CPS master: core topics already in IT und Automation", 88, "88 %", s, check="(88 %, IT und Automation)")
    n.add("kill_rule_1_threshold", "S_selection", "Kill rule 1 threshold: core-module overlap with one OTH programme", 50, "more than 50 %",
          "docs/kill_rules.md", check="more than 50 % of its core modules")
    n.add("rules_fixed_date", "S_selection", "Weights and kill rules committed (before the first screening)", "2026-10-14", "14 Oct 2026",
          s, check="| 14 Oct 2026, 17:40 | 958f823 |")
    os_ = pd.read_csv(INTERIM / "option_scenarios.csv")
    n.add("mc_draws", "F_ranking", "Monte Carlo draws", 10000, "10,000", "docs/evidence_ranking.md", check="(10,000 draws")
    n.add("robotics_overlap", "S_selection", "Robotics+AI B.Sc.: core topics already in the KI B.Sc. (kill rule 1)", 50, "50 %",
          "docs/overlap_test.md", check="| 4 of 8 | 50 % | passes at the threshold |")
    rob = os_[os_["option"] == "robotics_bsc"].set_index("scenario")
    half = [0.5 * float(rob.at[k, "gross first-years"]) for k in ("low", "central", "high")]
    n.add("robotics_netnew_cannib50", "F_ranking", "Robotics+AI net new first-years if 50 % come from OTH (low / central / high)",
          [round(v, 1) for v in half], " / ".join(f"{v:.1f}" for v in half), "docs/evidence_ranking.md",
          data="data/interim/option_scenarios.csv")
    n.add("robustness_bar", "F_ranking", "Robustness bar for the winner (share of draws)", 80, "80 %", "docs/evidence_ranking.md", check="above the 80 % robustness bar")
    # ---------------- A: demand ----------------
    s = "docs/evidence_competition_demand.md"
    n.add("informatik_firstyears_by_growth", "A_demand", "Informatik first-years in Bavaria, growth per year 2019-2024", 6.1, "6.1 %",
          s, unit="%/yr", check="rose 6.1 % a year (2019–2024)")
    n.add("informatik_firstyears_de_2019", "A_demand", "Informatik first-years Germany 2019", 18586, "18,586", s)
    # German vs foreign first-years (data-sufficiency audit G1)
    from study_program_intelligence.analysis.demand_split import load as load_split, series_table, university_type
    st = series_table(load_split()).set_index(["series", "region"])
    s = "docs/evidence_demand_split.md"
    pct1 = lambda v: f"{v:.1f} %"
    pct0 = lambda v: f"{v:.0f} %"
    for key, label, idx, col, disp in (
            ("informatik_by_german_growth", "Informatik first-years Bavaria, German only, growth per year 2019-2024", ("Informatik", "BY"), "German %/yr", pct1),
            ("informatik_by_foreign_growth", "Informatik first-years Bavaria, foreign only, growth per year 2019-2024", ("Informatik", "BY"), "foreign %/yr", pct1),
            ("informatik_de_german_growth", "Informatik first-years Germany, German only, growth per year 2019-2024", ("Informatik", "DE"), "German %/yr", pct1),
            ("informatik_de_foreign_growth", "Informatik first-years Germany, foreign only, growth per year 2019-2024", ("Informatik", "DE"), "foreign %/yr", pct1),
            ("cyber_proxy_by_german_growth", "Cyber proxy first-years Bavaria, German only, growth per year 2019-2024", ("cyber proxy", "BY"), "German %/yr", pct1),
            ("cyber_proxy_de_german_growth", "Cyber proxy first-years Germany, German only, growth per year 2019-2024", ("cyber proxy", "DE"), "German %/yr", pct1),
            ("grads_by_german_growth", "Informatik graduates Bavaria, German only, growth per year 2019-2025", ("Informatik graduates", "BY"), "German %/yr", pct1),
            ("robotics_feeders_by_german_growth", "Robotics feeder first-years Bavaria, German only, growth per year 2019-2024", ("robotics feeders", "BY"), "German %/yr", pct1),
            ("informatik_by_foreign_part", "Foreign part of the Informatik first-year growth, Bavaria 2019-2024", ("Informatik", "BY"), "foreign part of change %", pct0),
            ("cyber_proxy_by_foreign_part", "Foreign part of the cyber-proxy first-year growth, Bavaria 2019-2024", ("cyber proxy", "BY"), "foreign part of change %", pct0),
            ("cyber_proxy_by_foreign_share_2024", "Foreign share of cyber-proxy first-years, Bavaria 2024", ("cyber proxy", "BY"), "foreign share end %", pct0),
            ("informatik_de_foreign_share_2025", "Foreign share of Informatik first-years, Germany 2025", ("Informatik", "DE"), "foreign share 2025 %", pct0),
            ("informatik_de_foreign_share_2024", "Foreign share of Informatik first-years, Germany 2024", ("Informatik", "DE"), "foreign share end %", pct0)):
        v = float(st.at[idx, col])
        n.add(key, "A_demand", label, v, disp(v), s, unit="%", data="data/interim/demand_split.csv")
    ut = university_type().set_index("university type")
    v = float(ut.at["universities of applied sciences", "foreign share 1st univ. sem. %"])
    n.add("haw_informatik_foreign_share", "A_demand", "Foreign share of Informatik first-years at Bavarian HAWs, WS 2024/25", v,
          f"{v:.0f} %", s, unit="%", check=f"({v:.0f} % foreign)")
    s = "docs/evidence_competition_demand.md"
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
    n.add("weights", "F_ranking", "MCDA base weights", w, ", ".join(f"{k.replace('_', ' ')} {v:.2f}" for k, v in w.items()),
          "docs/evidence_ranking.md", data="configs/analysis.yaml", check="Demand (.30) | Labour (.20) | Fit (.20) | Feasibility (.15) | Differentiation (.10) | Regional (.05)")
    rs = pd.read_csv(INTERIM / "ranking_summary.csv")
    for scen, tag in (("base", "base"), ("robotics 50 % cannibalisation", "rob50"), ("base, robotics fit/feasibility 2/3/5", "skew"),
                      ("base, trend scores from German first-years only", "german")):
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
    for crit, key in (("labour_relevance", "loo_labour_cyber_bsc"), ("differentiation", "loo_diff_cyber_bsc")):
        p = 100 * float(b.loc[b["criterion left out"] == crit, "P(rank 1) cyber_bsc"].iloc[0])
        n.add(key, "F_ranking", f"P(rank 1) cyber B.Sc. without {crit}", round(p, 1), f"{p:.1f} %", s, data="data/interim/ranking_loo.csv")
    words = ["zero", "one", "two", "three", "four", "five", "six"]
    g = loo[loo["scenario"] == "base, trend scores from German first-years only"]
    won = int((g["winner"] == "cyber_bsc").sum())
    n.add("loo_german_cyber_wins", "F_ranking", "Leave-one-out runs won by the cyber B.Sc., German-only trend", won,
          f"{words[won]} of {words[len(g)]}", s, data="data/interim/ranking_loo.csv")
    gw = g[g["winner"] == "cyber_bsc"]
    lo = gw.loc[gw["P(rank 1) cyber_bsc"].idxmin()]
    n.add("loo_german_min_cyber", "F_ranking", f"Lowest winning P(rank 1) of the cyber B.Sc., German-only leave-one-out (without {lo['criterion left out']})",
          round(100 * lo["P(rank 1) cyber_bsc"], 1), f"{100 * lo['P(rank 1) cyber_bsc']:.1f} %", s, data="data/interim/ranking_loo.csv")
    gl = g[g["criterion left out"] == "labour_relevance"].iloc[0]
    for opt, key in (("cyber_msc", "loo_german_labour_msc"), ("cyber_bsc", "loo_german_labour_cyber")):
        p = 100 * float(gl[f"P(rank 1) {opt}"])
        n.add(key, "F_ranking", f"P(rank 1) {opt}, German-only trend, without labour_relevance", round(p, 1), f"{p:.1f} %", s,
              data="data/interim/ranking_loo.csv")
    # B: students from outside Bavaria and published intakes elsewhere (audit G4, G3)
    s = "docs/evidence_capture.md"
    oos = pd.read_csv(INTERIM / "out_of_state.csv", index_col=0)
    ex, ap = oos[oos["method"].str.startswith("exact")], oos[oos["method"].str.startswith("approx")]
    for key, label, v in (("oth_outside_bavaria", "OTH German students with a school certificate from outside Bavaria (exact)", ex.at["OTH Amberg-Weiden", "share outside Bavaria %"]),
                          ("haw_outside_bavaria", "All Bavarian HAWs: German students with a certificate from outside Bavaria", ex.at["all HAWs in Bavaria", "share outside Bavaria %"]),
                          ("oth_outside_bavaria_approx", "OTH: approx. share of German students from outside Bavaria (same method as THI/THD)", ap.at["OTH Amberg-Weiden", "approx. share outside Bavaria %"]),
                          ("thi_outside_bavaria_approx", "TH Ingolstadt: approx. share of German students from outside Bavaria", ap.at["TH Ingolstadt", "approx. share outside Bavaria %"]),
                          ("thd_outside_bavaria_approx", "TH Deggendorf: approx. share of German students from outside Bavaria", ap.at["TH Deggendorf", "approx. share outside Bavaria %"])):
        n.add(key, "B_capture", label, float(v), f"{float(v):.1f} %", s, unit="%", data="data/interim/out_of_state.csv")
    v = 100 * float(ex.at["OTH Amberg-Weiden", "of which Sachsen + Thüringen"]) / float(ex.at["OTH Amberg-Weiden", "German students"])
    n.add("oth_sachsen_thueringen_share", "B_capture", "OTH German students with a certificate from Sachsen or Thüringen", round(v, 1),
          f"{v:.1f} %", s, unit="%", data="data/interim/out_of_state.csv")
    for key, label, v, chk in (("rub_cyber_ba_firstyears", "Ruhr-Uni Bochum IT-Sicherheit/Informationstechnik B.Sc. first-years 2024 (plausibility check)", 156, "| 2024 | 156 |"),
                               ("uds_cyber_ba_firstyears", "Saarland Cybersicherheit B.Sc. (German) first-years WS 2025/26", 42, "| 44 / 42 |"),
                               ("uds_cyber_en_firstyears", "Saarland Cybersecurity B.Sc. (English) first-years WS 2025/26", 3, "| 4 / 3 |")):
        n.add(key, "B_capture", label, v, str(v), s, check=chk, data="reports/intake_benchmark.md")
    # S: written verdict for every theme group (audit G5)
    tv = pd.read_csv(INTERIM / "theme_verdicts.csv")
    k = int(tv["theme"].nunique())
    n.add("themes_all", "S_selection", "Theme groups with a written verdict (incl. 3 sub-themes)", k, str(k),
          "docs/evidence_theme_verdicts.md", check=f"all {k} themes", data="data/interim/theme_verdicts.csv")
    s = "docs/evidence_ranking.md"
    for opt, rank, key, scen in (("cyber_msc", "P(rank 2)", "p_rank2_cyber_msc_base", "base"),
                                 ("robotics_bsc", "P(rank 3)", "p_rank3_robotics_bsc_base", "base"),
                                 ("cyber_msc", "P(rank 2)", "p_rank2_cyber_msc_rob50", "robotics 50 % cannibalisation")):
        p = 100 * float(rs[(rs["scenario"] == scen) & (rs["option"] == opt)][rank].iloc[0])
        n.add(key, "F_ranking", f"{rank} {opt}, {scen}", round(p, 1), f"{p:.1f} %", s, data="data/interim/ranking_summary.csv")
    for k, label, v, disp, src, chk in LITERALS:
        sec, key = k.split("__")
        n.add(key, sec, label, v, disp, src, check=chk)
    candidates(n)
    tie_break(n)
    return n


def tie_break(n: Numbers) -> None:
    """Demand tie-break (docs/evidence_tie_break.md), read from data/interim/tie_break.csv."""
    s, g, src = "docs/evidence_tie_break.md", "H_tie_break", "data/interim/tie_break.csv"
    t = pd.read_csv(INTERIM / "tie_break.csv", dtype={"value": str})
    val = lambda c, ser, reg, grp, m: t[(t["candidate"] == c) & (t["series"].fillna("") == ser) & (t["region"].fillna("") == reg)
                                       & (t["group"].fillna("") == grp) & (t["metric"] == m)]["value"].iloc[0]
    sign = lambda v: f"+{float(v):.1f}" if float(v) > 0 else f"{float(v):.1f}"
    num = lambda v: f"{int(v):,}"
    closest = {"arvr": ("Medieninformatik", "Medieninformatik"), "robotics_b": ("Mechatronik + Technische Informatik", "Mechatronik + TI")}
    for c, (ser, label) in closest.items():
        for reg, grp, pre, key in (("BY", "all", f"{label} ", "by_all"), ("BY", "German", "", "by_german"),
                                   ("BY", "foreign", "", "by_foreign"), ("DE", "all", "", "de_all")):
            a, b, gr = (val(c, ser, reg, grp, m) for m in ("2019", "2024", "%/yr 2019-24"))
            disp = f"{pre}{num(a)} -> {num(b)}, {sign(gr)} %/yr"
            n.add(f"{c}_{key}", g, f"{label} first-years {reg} {grp} 2019 -> 2024 and growth", [int(a), int(b), float(gr)], disp, s,
                  data=src)
        share = val(c, ser, "BY", "all", "foreign share 2024 %")
        n.add(f"{c}_foreign_share_by", g, f"Foreign share of {label} first-years, Bavaria 2024", int(share), f"{share} %", s,
              check=f"| Foreign share 2024, Bavaria | {val('arvr', 'Medieninformatik', 'BY', 'all', 'foreign share 2024 %')} % | "
                    f"{val('robotics_b', 'Mechatronik + Technische Informatik', 'BY', 'all', 'foreign share 2024 %')} % |", data=src)
    a, b, gr = (val("arvr", "Informatik (broad pool)", "BY", "all", m) for m in ("2019", "2024", "%/yr 2019-24"))
    gg = val("arvr", "Informatik (broad pool)", "BY", "German", "%/yr 2019-24")
    n.add("informatik_pool_by", g, "Informatik first-years Bavaria 2019 -> 2024 (broad pool)", [int(a), int(b), float(gr)],
          f"Informatik {num(a)} -> {num(b)}, {sign(gr)} %/yr (German {sign(gg)})", s, data=src)
    for ser, label in (("Mechatronik", "Mechatronik"), ("Technische Informatik", "TI")):
        a, b, gr = (val("robotics_b", ser, "BY", "all", m) for m in ("2019", "2024", "%/yr 2019-24"))
        n.add(f"robotics_{label.lower()}_by", g, f"{ser} first-years Bavaria 2019 -> 2024", [int(a), int(b), float(gr)],
              f"{label} {num(a)} -> {num(b)}, {sign(gr)} %/yr", s, data=src)
    for c in ("arvr", "robotics_b"):
        cells = [val(c, "", "", "", m) for m in ("dedicated institutions Germany", "dedicated institutions Bavaria",
                                                 "dedicated institutions within 150 km", "dedicated institutions within 80 km")]
        n.add(f"{c}_competitors", g, f"Dedicated competitor institutions (Germany, Bavaria, 150 km, 80 km), {c}", [int(x) for x in cells],
              f"{cells[0]} in Germany, {cells[1]} in Bavaria, {cells[2]} within 150 km", s, data=src)
        cap = val(c, "(b) net new to OTH", "", "", "low / central / high")
        n.add(f"{c}_net_new", g, f"Capture model, net new first-years low / central / high, {c}", cap, cap, s, data=src)
    jobs = {r: val("robotics_b", "robotik", r, "", t[(t["series"] == "robotik")]["metric"].iloc[0]) for r in ("germany", "bayern", "amberg_100km", "amberg_50km")}
    n.add("robotik_ads", g, "Job ads 'Robotik' (Germany, Bavaria, 100 km, 50 km), latest snapshot", [int(v) for v in jobs.values()],
          f'"Robotik" {jobs["germany"]} in Germany, {jobs["bayern"]} Bavaria, {jobs["amberg_100km"]} within 100 km, {jobs["amberg_50km"]} within 50 km', s,
          data="docs/jobsuche_snapshots.json")
    for k, label, v, disp, chk in TIE_BREAK_LITERALS:
        n.add(k, g, label, v, disp, s, check=chk)
    for c in ("arvr", "robotics_b"):   # proxy fit, German first-years per competitor, German-only trend score
        prox = val(c, "", "", "", "dedicated offers whose catalogue subject is the proxy subject")
        n.add(f"{c}_proxy_tagged", g, f"Dedicated offers whose catalogue subject is the proxy subject, {c}", int(prox), prox, s, data=src,
              check={"arvr": f"carries the catalogue subject Medieninformatik ({prox})", "robotics_b": f"{prox} of 19 carry"}[c])
        ser = closest[c][0]
        per = val(c, ser, "BY", "German", "2024 per dedicated Bavarian institution")
        n.add(f"{c}_german_per_competitor", g, f"German first-years per dedicated Bavarian competitor institution 2024, {c}", int(per),
              per, s, data=src, check=f"| {per} ({val(c, '', '', '', 'dedicated institutions Bavaria')} institution")
        n.add(f"{c}_german_trend_score", g, f"German-only trend score by the rule, {c}", int(val(c, ser, "BY", "German", "trend score (rule)")),
              val(c, ser, "BY", "German", "trend score (rule)"), s, data=src, check="(1 and 1 by the pre-registered rule)")
    for c in ("arvr", "robotics_b"):   # nearest competitor, from the same table
        near = val(c, "", "", "", "nearest 1")
        km = int(near.rsplit(" ", 2)[-2])
        n.add(f"{c}_nearest_km", g, f"Distance to the nearest dedicated competitor, {c}", km, f"{km} km", s, data=src)
    # hand-check sheet (docs/handcheck_sheet.md): F1-F4 now and if every adapted module were rejected
    from study_program_intelligence.report import handcheck_sheet as H
    cfg, hc, rule = H.config()
    for c in ("arvr", "robotics_b"):
        t = H.verdict_table(c, {**cfg, "decisions": {}}, hc)
        now = H.f1_f4(t, rule)
        for mod, m in cfg["candidates"][c]["modules"].items():
            t.loc[t["module"] == mod, ["verdict", "prog"]] = [m["if_rejected"], None]
        worst = H.f1_f4(t, rule)
        n.add(f"sheet_{c}_e2_rows", g, f"Adapted-module (E2) verdicts on the hand-check sheet, {c}", len(cfg["candidates"][c]["modules"]),
              str(len(cfg["candidates"][c]["modules"])), "docs/handcheck_sheet.md",
              check=f"F1 {now['F1 %']} %, T {now['T']:g}, N {now['N']:g}")
        n.add(f"sheet_{c}_f1_worst", g, f"F1 if every E2 verdict were rejected, {c}", worst["F1 %"], f"{worst['F1 %']} %",
              "docs/handcheck_sheet.md", check=f"If every E2 is rejected: F1 {worst['F1 %']} %, T {worst['T']:g}, N {worst['N']:g}",
              data="configs/handcheck_sheet.yaml")


TIE_BREAK_LITERALS = [   # stated in docs/evidence_tie_break.md, from the sources named there
    ("tb_baseline_p1_cyber", "Baseline: P(rank 1) Cybersecurity B.Sc.", 91.7, "91.7 %", "P(rank 1) 91.7 % in the baseline ranking"),
    ("cyber_professorships", "Baseline: new professorships the cyber bachelor needs", 2, "2", "2 new professorships, 1 lab engineer, a security lab"),
    ("cyber_security_cover", "Baseline: EMI's cover of a cyber bachelor's security content (upper end)", 31, "31 %", "security content (31 %)"),
    ("cyber_proxy_by", "Baseline: cyber proxy first-years Bavaria, growth 2019-24 (all / German)", [5.9, 1.9], "+5.9 / +1.9 %/yr",
     "cyber proxy first-years Bavaria +5.9 %/yr 2019-24, but German only +1.9 %/yr"),
    ("cyber_gross", "Baseline: cyber bachelor gross first-years low / central / high", [21, 39, 75], "21 / 39 / 75", "gross first-years 21 / 39 / 75"),
    ("cyber_net_new", "Baseline: cyber bachelor net new low / central / high", [15.3, 32.0, 64.4], "15.3 / 32.0 / 64.4", "net new to OTH 15.3 / 32.0 / 64.4"),
    ("cyber_ads", "Baseline: job ads 'Cyber Security' Germany / Bavaria share / 100 km", [851, 30.9, 191], "851 / 30.9 % / 191",
     '"Cyber Security" 851 ads in Germany, Bavaria 30.9 %, 191 within 100 km'),
    ("cyber_competitors_150km", "Baseline: dedicated cyber bachelors within 150 km", 4, "4", "4 dedicated bachelors within 150 km"),
    ("trends_robotik_share", "'Robotik Studium' share of 'Informatik Studium', 2019 / 2021 / 2026", [2.4, 3.5, 3.4], "2.4 / 3.5 / 3.4 %",
     '"Robotik Studium" 2.4 % (2019), 3.5 % (2021), 3.4 % (2026, Jan-Oct)'),
    ("gross_share_informatik", "AR/VR central gross first-years as a share of Bavarian Informatik first-years 2024", 1.4, "1.4 %",
     "would be 1.4 % of Bavaria's 4,110"),
    ("rule_groups", "Decision rule: signal groups a candidate must lead to win on demand", [3, 4], "3 of 4", "leads in at least three of the four"),
    ("rule_jobs_band", "Decision rule: job-ad counts within this margin are neutral", 10, "10 %", "within 10 % of each other is neutral"),
    ("rule_trends_band", "Decision rule: Trends slope difference below this is neutral (pp/yr)", 0.1, "0.1", "under 0.1 percentage points a year"),
    ("rule_jobs_radius", "Decision rule: radius for the job-ad comparison", 100, "100 km", "within 100 km of Amberg: the largest"),
    ("gpu_workstations", "GPU workstations listed on the IKKI page", 32, "32", "GPU lab with 32 workstations"),
    ("xr_headsets_estimate", "XR headsets a cohort of about 40 would need (assumption)", [10, 20], "10-20", "estimate 10-20 for a cohort of about 40"),
]


def candidates(n: Numbers) -> None:
    """Equal-evidence step (docs/evidence_candidates.md): read from the generated tables where they exist."""
    s, g = "docs/evidence_candidates.md", "G_candidates"
    hc = pd.read_csv(INTERIM / "feasibility_handcheck_candidates.csv")
    names = {"Autonomous mobile systems B.Eng.": "autonomous", "AR/VR & visual computing B.Sc.": "arvr",
             "Energy data management B.Sc.": "energydata", "Geo-data & geovisualisation B.Sc.": "geodata"}
    pid = {"autonomous": "thd_ba_em", "arvr": "hsc_ba_vc", "energydata": "fhdo_ba_eedm", "geodata": "hm_ba_gds"}
    auto = pd.read_csv(INTERIM / "feasibility_modules.csv")
    for option, t in hc.groupby("option"):
        k = names[option]
        tot = t["ects"].sum()
        e12 = 100 * t.loc[t["verdict"].isin(["E1", "E2"]), "ects"].sum() / tot
        e1 = 100 * t.loc[t["verdict"] == "E1", "ects"].sum() / tot
        a = auto[auto["programme_id"] == pid[k]]
        e5 = round(100 * a.loc[a["covered"], "ects_used"].sum() / a["ects_used"].sum(), 1)
        tf = round(100 * a.loc[a["tfidf_covered"], "ects_used"].sum() / a["ects_used"].sum(), 1)
        row = f"| {k} | {e5:.1f} % | {tf:.1f} % | {e5 - tf:.1f} pp | {e12:.1f} % | {e1:.1f} % |"
        src = "data/interim/feasibility_handcheck_candidates.csv"
        n.add(f"f1_hand_{k}", g, f"F1 after the hand check (E1+E2), {k}", round(e12, 1), f"{e12:.1f} %", s, check=row, data=src)
        n.add(f"f1_e1only_{k}", g, f"F1 without adapted modules (E1 only), {k}", round(e1, 1), f"{e1:.1f} %", s, check=row, data=src)
        n.add(f"e5_tfidf_gap_{k}", g, f"Gap e5 vs TF-IDF coverage, {k}", round(e5 - tf, 1), f"{e5 - tf:.1f} pp", s, check=row,
              data="data/interim/feasibility_modules.csv")
        el = a[a["elective"]]
        if len(el) and k in ("arvr", "energydata"):   # elective coverage stated in the electives paragraph
            cov = el.loc[el["covered"], "ects_used"].sum()
            n.add(f"electives_covered_{k}", g, f"Listed elective ECTS the automatic match covers, {k}", float(cov), f"{cov:g}", s,
                  check=f"the automatic match covers {cov:g}", data="data/interim/feasibility_modules.csv")
    by = pd.read_csv(INTERIM / "candidate_demand.csv")
    by = by[by["region"] == "BY"].set_index("candidate")
    for k in by.index:
        r = by.loc[k]
        chk = f"| {int(r['all start']):,} -> {int(r['all end']):,} | {r['all %/yr']} | {r['German %/yr']} | {r['foreign %/yr']} |"
        n.add(f"by_growth_{k}", g, f"Bavarian growth of the demand series, {k} (%/yr)", float(r["all %/yr"]), f"{r['all %/yr']}", s,
              check=chk, data="data/interim/candidate_demand.csv")
        n.add(f"by_german_growth_{k}", g, f"Bavarian growth, German nationality only, {k} (%/yr)", float(r["German %/yr"]),
              f"{r['German %/yr']}", s, check=chk, data="data/interim/candidate_demand.csv")
    comp = pd.read_csv(INTERIM / "candidate_competition.csv").set_index("candidate")
    for k in comp.index:
        r = comp.loc[k]
        chk = (f"| {k} | {r['dedicated institutions DE']} | {r['dedicated institutions BY']} | "
               f"{r['dedicated institutions <=150 km']} | {r['dedicated institutions <=80 km']} |")
        n.add(f"competitors_150km_{k}", g, f"Dedicated competitor institutions within 150 km, {k}",
              int(r["dedicated institutions <=150 km"]), str(r["dedicated institutions <=150 km"]), s, check=chk,
              data="data/interim/candidate_competition.csv")
        n.add(f"competitors_de_{k}", g, f"Dedicated competitor institutions in Germany, {k}", int(r["dedicated institutions DE"]),
              str(r["dedicated institutions DE"]), s, check=chk, data="data/interim/candidate_competition.csv")
    sc = pd.read_csv(INTERIM / "candidate_scenarios.csv")
    for k, t in sc.groupby("option"):
        t = t.set_index("scenario")
        levels = ("low", "central", "high")
        gross = " / ".join(f"{t.at[x, 'gross first-years']:.1f}" for x in levels)
        net = " / ".join(f"{t.at[x, '(b) net new to OTH']:.1f}" for x in levels)
        n.add(f"gross_{k}", g, f"Gross first-years low / central / high, {k}",
              [float(t.at[x, "gross first-years"]) for x in levels], gross, s, check=f"| {gross} | {net} |",
              data="data/interim/candidate_scenarios.csv")
    rs = pd.read_csv(INTERIM / "ranking_candidates_summary.csv")
    slug = lambda x: "".join(ch if ch.isalnum() else "_" for ch in x.lower()).strip("_")
    for r in rs.itertuples():   # every scenario of the robustness table
        p = 100 * float(r._2)
        n.add(f"p1_{r.option}_{slug(r.scenario)}", g, f"P(rank 1) {r.option}, {r.scenario}", round(p, 1), f"{p:.1f} %", s,
              data="data/interim/ranking_candidates_summary.csv")
    # central weighted totals (deterministic, base weights)
    from study_program_intelligence.analysis import ranking as R
    cfg, sc, cap = R.load(sheet_path=R.CAND_SCORES, scen_path=R.CAND_SCEN)
    for r in R.deterministic(cfg, sc, cap).itertuples():
        n.add(f"total_{r.option}", g, f"Weighted total at central scores, {r.option}", float(r._8), f"{r.option} {r._8:.2f}", s)
    for k, label, v, disp, chk in CANDIDATE_LITERALS:
        n.add(k, g, label, v, disp, s, check=chk)


CANDIDATE_LITERALS = [   # stated in docs/evidence_candidates.md
    ("f4_ot_strict", "Reduced OT master: share listed by IT und Automation", 83.3, "83.3 %", "83.3 % of it is listed by IT und Automation"),
    ("f4_ot_lenient", "Reduced OT master: largest share if shared modules count elsewhere", 58.3, "58.3 %", "58.3 % comes from the KI master"),
    ("f4_geodata", "Geo-data: share from OTH's Geoinformatik und Landmanagement", 62.3, "62.3 %", "| geodata | fails | 62.3 % from OTH's own"),
    ("f4_autonomous", "Autonomous systems (FR track): share from E&IT", 77.0, "77.0 %", "77.0 % from E&IT (F4)"),
    ("arvr_share_of_mi", "AR/VR central gross as a share of Bavarian Medieninformatik first-years 2024", 41, "41 %", "would be 41 % of all 141"),
    ("arvr_rel_capture", "AR/VR: OTH new relative to the Coburg site, all model variants", "1.50-1.91", "1.50-1.91",
     "draw 1.50-1.91 times Coburg's intake"),
    ("arvr_e2_margin", "AR/VR: ECTS of E2 verdicts that could be rejected before F1 falls below 80 %", 14, "14 ECTS", "F1 falls below 80 % above 14 ECTS"),
    ("plzen_km", "Distance Amberg - Plzen (straight line)", 115, "about 115 km", "about 115 km from Amberg"),
    ("baseline_p1_cyber", "Baseline winner P(rank 1), Cybersecurity B.Sc.", 91.7, "91.7 %", "Cybersecurity B.Sc., P(rank 1) 91.7 %"),
]


# Numbers taken as stated in an evidence doc (key prefix = section). check = verbatim text in that doc.
_D, _T, _F, _CA, _CT, _FM, _FS, _B, _O, _CN, _R, _TP = (
    "docs/evidence_competition_demand.md", "docs/evidence_demand_trends.md", "docs/evidence_forecast.md",
    "docs/evidence_capture.md", "docs/evidence_catchment.md", "docs/evidence_fit_modules.md", "docs/evidence_fit_staff.md",
    "docs/evidence_benchmarks.md", "docs/evidence_outlet_jobs.md", "docs/evidence_cannibalisation.md",
    "docs/evidence_ranking.md", "docs/theme_precision.md")
LITERALS = [
    # method
    ("M_method__labels_reviewed", "Theme labels proposed by Claude and reviewed by the team", 110, "110", _TP, "who agreed with all 110"),
    ("M_method__cyber_precision", "Precision of the cybersecurity title rule (all matches checked)", 94, "94 %", _TP, "| Cybersecurity | all 70 | 66 | 94 % |"),
    ("M_method__cyber_matches", "Cybersecurity title matches checked by hand", 70, "70", _TP, "| Cybersecurity | all 70 | 66 | 94 % |"),
    ("M_method__pairs_e5", "Module pairs judged correctly by e5 (hand check of 20)", 16, "16 of 20", _FM, "**16 of 20**"),
    ("M_method__review_n_claims", "Statements checked in the independent claim review", 443, "443", "docs/review_verdicts.md", "docs/review_claims.md (443 claims"),
    ("M_method__method_agreement", "Agreement of e5 and TF-IDF on covered/gap labels", 74, "74 %", _FM, "The two methods agree on 74 % of covered/gap labels"),
    ("M_method__pairs_tfidf", "Module pairs judged correctly by TF-IDF (hand check of 20)", 14, "14 of 20", _FM, "**14 of 20**"),
    # A demand
    ("A_demand__informatik_share_2015", "Informatik share of all first-years, Germany 2015", 3.7, "3.7 %", _F, "DE 3.7 % in 2015"),
    ("A_demand__informatik_share_2024", "Informatik share of all first-years, Germany 2024", 5.4, "5.4 %", _F, "5.4 % in 2024"),
    ("A_demand__mase_naive_by_cyber", "Backtest MASE of the naive model, Bavaria cyber proxy", 3.17, "3.17", _F, "| BY cyber proxy | **1.52** | 1.70 | 3.17 | 3.98 |"),
    ("A_demand__drift_underforecast", "Share of Bavarian backtest errors where drift under-forecast", "76-80", "76-80 %", _F, "76-80 % of the Bavarian backtest errors"),
    ("A_demand__kmk_by_2030", "KMK index for Bavarian first-years 2030 (base 2024)", 0.99, "0.99", _F, "Bavaria 0.99 (2030)"),
    ("A_demand__by_all_2024", "Bavarian first-years, all subjects, 2024", 68872, "68,872", _D, "fell from 68,872 to 57,216"),
    ("A_demand__by_all_2025", "Bavarian first-years, all subjects, 2025 (G9 transition)", 57216, "57,216", _D, "fell from 68,872 to 57,216"),
    ("A_demand__elektro_trend", "Elektrotechnik first-years Germany, per year 2019-2025", -2.6, "-2.6 %", _D, "Elektrotechnik -2.6 %/yr"),
    ("A_demand__mechatronik_trend", "Mechatronik first-years Germany, per year 2019-2025", -3.6, "-3.6 %", _D, "Mechatronik -3.6 %/yr"),
    ("A_demand__cyber_share_of_informatik_search", "'Cyber Security Studium' as share of 'Informatik Studium' searches, 2026", 12.6, "12.6 %", _T, "| 2026 | 12.6 % |"),
    ("A_demand__cyber_search_2022", "'Cyber Security Studium' search index 2022 (specialist download)", 18.5, "18.5", _T, "| 2022 | 18.5 |"),
    ("A_demand__cyber_search_2026", "'Cyber Security Studium' search index 2026 (specialist download)", 22.0, "22.0", _T, "| 2026 | 22.0 |"),
    ("A_demand__ki_search_2024", "'KI Studium' search index 2024 (peak)", 13.3, "13.3", _T, "13.3 in 2024 to 9.0 in 2026"),
    ("A_demand__ki_search_2026", "'KI Studium' search index 2026", 9.0, "9.0", _T, "13.3 in 2024 to 9.0 in 2026"),
    ("A_demand__cyber_ba_nearest_km", "Nearest dedicated cyber bachelor (FAU, part-time online)", 63, "63 km", _D, "FAU (63 km)"),
    ("A_demand__cyber_focus_germany", "General programmes in Germany with a security focus area", 126, "126", _D, "126 general programmes offer cybersecurity as a focus area"),
    ("A_demand__cyber_ba_haw_share", "Share of dedicated cyber bachelors at HAWs", 81, "81 %", _D, "81 % of bachelor programmes are at HAW"),
    # B capture
    ("B_capture__own_pool_exact", "Own pool 2023/24 (exact)", 5501, "5,501", _CT, "| 14 | 3,279 | 2,222 | **5,501** | **-19 %** | **10.1 %** |"),
    ("B_capture__own_pool_trend", "Own pool change since 2013/14", -19, "-19 %", _CT, "**-19 %**"),
    ("B_capture__own_pool_share_by", "Own pool as share of Bavaria's qualified school leavers", 10.1, "10.1 %", _CT, "**10.1 %**"),
    ("B_capture__pool_without_regensburg", "Own pool if OTH Regensburg counts as a competitor", 3807, "3,807", _CT, "| 12 | 2,312 | 1,495 | 3,807 | -24 % | 7.0 % |"),
    ("B_capture__regensburg_part", "Regensburg city and county in the own pool", 1694, "1,694", _CT, "Regensburg city and county 1,694"),
    ("B_capture__closer_than_nuernberg", "Share of OTH's 100-km catchment closer to OTH than to Nuremberg/Erlangen", 42, "42 %", _CT, "| FAU / TH Nürnberg | **42 %** |"),
    ("B_capture__pool_g9_gap", "Own pool in the G9 gap year 2024/25", 2850, "~2,850", _CT, "| 2024/25 | ~2,850 |"),
    ("B_capture__pool_2030", "Own pool forecast 2029/30 (KMK path)", 5300, "~5,300", _CT, "| 2029/30 | ~5,300"),
    ("B_capture__beta_band", "Distance-decay values within 10 % of the best fit", "1.3-1.95", "1.3-1.95", _CA, "beta within 10 % of the best fit: 1.3-1.95"),
    ("B_capture__home_share_model", "OTH home-region share, model", 61, "61 %", _CA, "OTH: model 61 % vs actual 71 %"),
    ("B_capture__home_share_actual", "OTH home-region share, actual (Tabelle 5)", 71, "71 %", _CA, "OTH: model 61 % vs actual 71 %"),
    ("B_capture__thi_implied", "THI cyber intake implied by the uncalibrated demand model", "59-173", "59-173", _CA, "implies 59-173 first-years"),
    ("B_capture__rel_capture_thi", "OTH intake relative to THI's, over all model variants", "0.65-0.86", "0.65-0.86 times", _CA, "OTH would draw 0.65-0.86 times THI's intake"),
    ("B_capture__low_variant_range", "Low case across the nine model variants (THI-anchored)", "16-21", "16-21", _CA, "Ranges across the 9 model variants: low 16-21"),
    ("B_capture__rel_capture_deg", "OTH intake relative to TH Deggendorf's, over all model variants", "1.20-1.28", "1.20-1.28 times", _CA, "1.20-1.28 times TH Deggendorf's"),
    ("F_ranking__loo_first_run_tie", "First ranking run (skewed robotics range): leave out demand, cyber vs robotics", "49 / 50", "49 % / 50 %", "docs/decision_log.md", "tie with robotics 49 % / 50 %"),
    ("B_capture__oth_eng_firstyears", "OTH first-years in engineering sciences incl. Informatik, WS 2024/25", 452, "452", _CA, "engineering sciences (incl. Informatik) 452"),
    ("B_capture__year1_low", "Cyber B.Sc. first-years in year 1, low", 12, "12", _CA, "| 12 | 16 | **21** |"),
    ("B_capture__year1_central", "Cyber B.Sc. first-years in year 1, central", 24, "24", _CA, "| 24 | 31 | **39** |"),
    ("B_capture__year1_high", "Cyber B.Sc. first-years in year 1, high", 45, "45", _CA, "| 45 | 60 | **75** |"),
    # C fit
    ("C_fit__cover_sec_ba_range", "EMI coverage of security ECTS, range over competitor bachelors", "18-39", "18-39 %", _FM, "| **31 %** | 18-39 % | 47 % | 71 % |"),
    ("C_fit__cover_sec_ba_tfidf", "EMI coverage of a cyber bachelor's security ECTS, TF-IDF", 47, "47 %", _FM, "| **31 %** | 18-39 % | 47 % | 71 % |"),
    ("C_fit__pentest_cover", "EMI coverage of penetration testing & auditing (e5)", 0, "0 %", _FM, "| Penetration testing & auditing (practice) | 6 | 5 | **0 %** |"),
    ("C_fit__forensics_cover", "EMI coverage of forensics (e5)", 12, "12 %", _FM, "| Forensics | 5 | 5 | **12 %** |"),
    ("C_fit__secops_cover", "EMI coverage of security operations & incident management (e5)", 0, "0 %", _FM, "| Security Operations & Incident Management | 5 | 5 | **0 %** |"),
    ("C_fit__crypto_cover", "EMI coverage of cryptography (e5)", 100, "100 %", _FM, "| Cryptography | 4 | 7.5 | 100 % |"),
    ("C_fit__network_cover", "EMI coverage of network security (e5)", 80, "80 %", _FM, "| Network Security | 6 | 7.5 | 80 % |"),
    ("C_fit__deg_ma_ot", "TH Deggendorf master: OT/industrial security modules (ECTS)", 50, "50 ECTS", _FM, "8 modules, 50 ECTS"),
    ("C_fit__security_profs", "EMI professors already teaching security modules", 4, "about four", _FS, "about four professors already teach security modules"),
    ("C_fit__new_load_sws", "New teaching load of the cyber B.Sc. (SWS per year)", "40-50", "40-50 SWS", _FS, "| **New teaching load, bachelor** | **40-50** |"),
    ("C_fit__master_profs", "Additional professorship share for the master", "0.7-0.9", "0.7-0.9", _FS, "0.7-0.9 professorship"),
    ("C_fit__teaching_assignments", "ECTS via teaching assignments in the draft (ISMS, law)", 10, "10 ECTS", _B, "New via teaching assignments: 10 ECTS"),
    ("C_fit__competitor_sec_share", "Security share of Bavarian competitor bachelors", "30-31", "30-31 %", _B, "between the Bavarian competitors (30-31 %)"),
    ("C_fit__stpoelten_sec_share", "Security share of St. Pölten's bachelor", 50, "50 %", _B, "and St. Pölten (50 %)"),
    # D outlet
    ("D_outlet__ads_it_sicherheit", "Job ads 'IT-Sicherheit', Germany", 6191, "6,191", _O, "| Cybersecurity | IT-Sicherheit | 6,191 |"),
    ("D_outlet__ads_security_engineer", "Job ads 'Security Engineer', Germany", 838, "838", _O, "| Cybersecurity | Security Engineer | 838 |"),
    ("D_outlet__ads_ki", "Job ads 'Künstliche Intelligenz', Germany", 945, "945", _O, "| Baseline | Künstliche Intelligenz | 945 |"),
    ("D_outlet__baseline_share", "Bavarian share of German job ads, IT baseline keywords", "22-25", "22-25 %", _O, "against 22–25 % for the computer-science baselines"),
    ("D_outlet__ads_cyber_50km", "Job ads 'Cyber Security' within 50 km of Amberg", 8, "8", _O, "Within 50 km of Amberg there are only 8"),
    ("D_outlet__snapshot_change", "Median absolute change between the two job-ad snapshots", 1.4, "1.4 %", _O, "median absolute change 1.4 %"),
    ("D_outlet__academic_share_2023", "Academic share of IT employees in Bavaria 2023", 52.6, "52.6 %", _O, "| academic share | 48.5 % | 52.6 % |"),
    ("D_outlet__shortage_score", "BA shortage score, Berufe in der Informatik (specialist level), 2025", 2.0, "2.0", _O, "(score 2.0)"),
    # E cannibalisation
    ("E_cannibalisation__netnew_share_range", "Cyber B.Sc. share of students new to OTH (model variants)", "73-86", "73-86 %", _CN, "73-86 % (central 82 %)"),
    ("E_cannibalisation__netnew_share_central", "Cyber B.Sc. share new to OTH, central", 82, "82 %", _CN, "73-86 % (central 82 %)"),
    ("E_cannibalisation__kept_share_range", "Cyber B.Sc. share kept in the region", "13-16", "13-16 %", _CN, "(13-16 %; central 6 per year)"),
    ("E_cannibalisation__overlap_test_cyber_ba", "Kill rule 1 overlap test: cyber B.Sc. core topics already in one OTH programme", 25, "25 %", "docs/overlap_test.md", "| 2 of 8 | 25 % | **passes** |"),
    ("E_cannibalisation__stress_share", "Cannibalisation share assumed in the stress test", 50, "50 %", _CN, "cannibalisation were 50 % (about twice the model's maximum)"),
    ("E_cannibalisation__stress_netnew", "Cyber B.Sc. net new if cannibalisation were 50 %", [10.5, 19.5, 37.5], "10.5 / 19.5 / 37.5", _CN, "10.5 / 19.5 / 37.5"),
    ("E_cannibalisation__module_cover_ii_mi", "Security ECTS of a cyber bachelor covered by Industrie-4.0-Informatik and Medieninformatik", 28, "28 %", _CN, "at most 28 %"),
    ("E_cannibalisation__msc_from_oth", "Cyber/OT M.Sc. share taken from OTH programmes", "22-37", "22-37 %", _R, "| 22-37 % (AI for Industrial Applications, IT und Automation) |"),
    ("E_cannibalisation__rob_from_oth", "Robotics+AI B.Sc. share taken from OTH programmes (model)", "14-29", "14-29 %", _R, "| 14-29 % (KI B.Sc., E&IT, Mechatronik und digitale Automation) |"),
    ("E_cannibalisation__rob_kept", "Robotics+AI B.Sc. students kept in region, low / central / high", [4.1, 8.5, 15.6], "4.1 / 8.5 / 15.6", _R, "| 4.1 / 8.5 / 15.6 |"),
    ("E_cannibalisation__msc_kept", "Cyber/OT M.Sc. students kept in region, low / central / high", [0.7, 2.2, 5.5], "0.7 / 2.2 / 5.5", _R, "| 0.7 / 2.2 / 5.5 |"),
    ("E_cannibalisation__msc_gross", "Cyber/OT M.Sc. gross first-years, low / central / high", [23, 43, 81], "23 / 43 / 81", _R, "| 23 / 43 / 81 |"),
    ("E_cannibalisation__rob_gross", "Robotics+AI B.Sc. gross first-years, low / central / high", [15, 29, 55], "15 / 29 / 55", _R, "| 15 / 29 / 55 |"),
    ("E_cannibalisation__msc_anchor", "THI Cloud Applications und Security Engineering capacity (master anchor)", 30, "30", _R, "THI Cloud Applications und Security Engineering capacity 30"),
    ("E_cannibalisation__grads_de_2019", "Informatik graduates Germany 2019", 14249, "14,249", _R, "Informatik graduates Germany 14,249 (2019)"),
    ("E_cannibalisation__grads_de_2025", "Informatik graduates Germany 2025", 21858, "21,858", _R, "-> 21,858 (2025)"),
    # F ranking
    ("F_ranking__total_cyber_bsc", "Weighted total at central scores, Cyber B.Sc.", 3.42, "3.42", _R, "| 3.61 | **3.42** |"),
    ("F_ranking__total_cyber_msc", "Weighted total at central scores, Cyber/OT M.Sc.", 3.04, "3.04", _R, "| 2.14 | 3.04 |"),
    ("F_ranking__total_robotics", "Weighted total at central scores, Robotics+AI B.Sc.", 2.95, "2.95", _R, "| 4.09 | 2.95 |"),
    ("F_ranking__p1_independent", "P(rank 1) Cyber B.Sc. with independent capture draws", 87.0, "87.0 %", _R, "87.0 % / 10.0 % / 3.0 %"),
    ("F_ranking__dirichlet_conc", "Dirichlet concentration of the weight draws", 50, "50", _R, "Dirichlet concentration 50"),
]


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
