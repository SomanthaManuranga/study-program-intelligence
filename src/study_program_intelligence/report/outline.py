"""Report outline (Step 50), built around the four claims, cannibalisation, ranking and limitations.

Run from the repository root (normally via report.build):

    python -m study_program_intelligence.report.outline

Every number is inserted from reports/key_numbers.yaml (placeholders {key}); a placeholder without a key number
stops the build. Each section links its evidence doc(s) and shared figure(s); links are relative to reports/final/.
Output: reports/final/outline.md.
"""

from __future__ import annotations

import re
from pathlib import Path

from .key_numbers import load as load_numbers

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT = REPO_ROOT / "reports" / "final" / "outline.md"
D = "../../docs/"
F = "../figures/"

# (heading, evidence docs, figures, bullets); bullets may use {key} placeholders from key_numbers.yaml
SECTIONS = [
    ("0 Summary and recommendation", ["evidence_ranking.md"], ["f06_rank_probabilities.png"], [
        "Recommendation: introduce a **Cybersecurity B.Sc.** at OTH Amberg-Weiden (EMI); it ranks first in "
        "{p_rank1_cyber_bsc_base} of 10,000 Monte Carlo draws ({p_rank1_cyber_bsc_rob50} if robotics cannibalises 50 %).",
        "Expected first-years (steady state): {cyber_bsc_gross_low} / {cyber_bsc_gross_central} / {cyber_bsc_gross_high} "
        "(low / central / high); net new to OTH {cyber_bsc_netnew_low} / {cyber_bsc_netnew_central} / {cyber_bsc_netnew_high}.",
        "Main risk: the low case is below the assumed minimum cohort of {min_cohort}; real intakes of comparable programmes "
        "are not public (capacities and one anecdote are used).",
    ]),
    ("1 Question, scope and method", ["research_protocol.md", "kill_rules.md", "decision_log.md"], [], [
        "Brief: which new programme would attract the most students and suit EMI; public data only, bachelor and master, all of Germany.",
        "Four claims (A demand, B capture, C fit, D outlet) + incrementality test + feasibility gate + kill rules set before scoring.",
        "Pipeline overview: Destatis GENESIS, BA Studiensuche (programme catalogue), module handbooks, Bavarian statistical "
        "reports, BA Jobsuche, Google Trends; every source and method decision logged.",
        "Shortlist after kill rules: Cybersecurity B.Sc., Cyber/OT M.Sc., Robotics+AI B.Sc. (embedded/CPS master and part-time AI master dropped).",
    ]),
    ("2 Claim A - Demand: the recruiting pool grows", ["evidence_forecast.md", "evidence_demand_trends.md", "evidence_competition_demand.md"],
     ["f01_demand_forecast.png", "f02_search_interest.png"], [
        "Informatik is the only growing EMI field: Bavaria +{informatik_firstyears_by_growth} per year (2019-2024); Germany "
        "{informatik_firstyears_de_2019} -> {informatik_firstyears_de_2025}, flat since 2023.",
        "Bavaria cyber proxy {cyber_proxy_by_2024} (2024) -> central {cyber_proxy_by_2030_central} (2030), {cyber_proxy_by_2035_central} (2035); "
        "conservative {cyber_proxy_by_2030_conservative} / {cyber_proxy_by_2035_conservative}. Central = midpoint, a planning choice.",
        "Model choice: drift is the best model in all four series (MASE {forecast_mase_drift_by_cyber} for Bavaria cyber proxy vs naive 3.17).",
        "Search interest: 'Cyber Security Studium' {search_cyber_vs_ki} and {search_cyber_vs_robotik} since 2022, but flat since 2022.",
        "Supply: {cyber_ba_germany} dedicated cyber bachelors and {cyber_ma_germany} masters in Germany; {cyber_ba_150km} / {cyber_ma_150km} within 150 km; "
        "{cyber_focus_150km} general programmes with a security focus within 150 km.",
        "Weak point to state: the proxy is not cyber demand itself (Destatis has no cyber subject).",
    ]),
    ("3 Claim B - Capture: OTH can fill a cohort", ["evidence_catchment.md", "evidence_capture.md"], ["f04_capture.png"], [
        "Own pool {own_pool} qualified school leavers a year ({own_pool_fosbos_share} via FOS/BOS); {catchment_closer_to_oth} of the 100-km catchment is closer to OTH than to Deggendorf.",
        "Gravity model calibrated on Bavarian student flows: beta {gravity_beta}, {gravity_r2}; used for relative capture only (absolute scale fails the THI check).",
        "Anchors: THI capacity {thi_cyber_capacity}, TH Deggendorf {deg_cyber_anecdote} (anecdote) -> {cyber_bsc_gross_low} / {cyber_bsc_gross_central} / {cyber_bsc_gross_high} first-years.",
        "Minimum viable cohort {min_cohort} is an assumption (no rule found); start 2026 or later (G9 gap 2025).",
    ]),
    ("4 Claim C - Fit: EMI has the base, not the security core", ["evidence_fit_modules.md", "evidence_fit_staff.md", "evidence_benchmarks.md"], [], [
        "EMI already teaches {emi_cover_gen_ba} of a cyber bachelor's foundations but only {emi_cover_sec_ba} of its security ECTS (master {emi_cover_sec_ma}).",
        "Missing: pentesting, forensics, SOC/incident response, software security, security management, law.",
        "Staff: {new_professorships} + lab engineer + security lab ({teaching_load_sws} teaching load per professor).",
        "Draft curriculum: 7 semesters / 210 ECTS, security ECTS {draft_security_ects}; {draft_new_ects} new, {draft_reused_ects} reused from EMI.",
    ]),
    ("5 Claim D - Outlet: graduates are in demand", ["evidence_outlet_jobs.md"], ["f03_job_ads.png"], [
        "Job ads ({job_snapshot_date}): 'Cyber Security' {ads_cyber_security_de} in Germany, Bavaria {ads_cyber_security_by_share}, "
        "{ads_cyber_security_amberg_100km} within 100 km; 'OT Security' Bavaria {ads_ot_security_by_share}.",
        "Robotics comparison: 'Robotik' {ads_robotik_de} ads, {ads_robotik_amberg_50km} within 50 km (strongest local signal).",
        "IT occupations in Bavaria {it_jobs_by_growth} (2019-2023), with academic degree {it_jobs_by_academic_growth}; Informatik a shortage occupation at bachelor level (BA 2025).",
        "Weak point: keyword counts are indicators, not vacancies; snapshots continue to 4 Dec.",
    ]),
    ("6 Incrementality: cannibalisation and regional benefit", ["evidence_cannibalisation.md", "overlap_test.md", "kill_rules.md"], ["f05_cannibalisation.png"], [
        "Share taken from OTH's own programmes {cyber_bsc_from_oth_range}; net new to OTH {cyber_bsc_netnew_low} / {cyber_bsc_netnew_central} / {cyber_bsc_netnew_high}.",
        "Regional benefit: {cyber_bsc_kept_central} students a year (central) kept in the region who would otherwise leave.",
        "Kill rule 1 (more than 50 % core overlap) passed: {cyber_bsc_core_overlap}. No separate cannibalisation threshold exists; cannibalisation enters via demand.",
        "Same model for the other options: robotics {robotics_bsc_netnew}, master {cyber_msc_netnew} net new (low / central / high).",
    ]),
    ("7 Ranking: MCDA + Monte Carlo", ["evidence_ranking.md"], ["f06_rank_probabilities.png", "f07_leave_one_out.png"], [
        "Weights: {weights}; Dirichlet draws, common capture-model factor, feasibility gate.",
        "P(rank 1): Cybersecurity B.Sc. {p_rank1_cyber_bsc_base}, Cyber/OT M.Sc. {p_rank1_cyber_msc_base}, Robotics+AI B.Sc. {p_rank1_robotics_bsc_base}.",
        "Leave-one-criterion-out: cyber B.Sc. {loo_winner_always_cyber} run; lowest {loo_min_cyber_bsc} (without demand).",
        "Sensitivity: skewed robotics range 2/3/5 -> cyber B.Sc. {p_rank1_cyber_bsc_skew}.",
        "Evidence asymmetry: same capture model for all options; missing anchors widen ranges; weak evidence widens, never raises a score.",
    ]),
    ("8 Limitations", ["evidence_capture.md", "evidence_cannibalisation.md", "evidence_ranking.md", "manual_downloads.md"], [], [
        "No measured programme intakes (only capacities and one anecdote); one public figure would cut the demand range by about half.",
        "Cyber demand only via proxies (Destatis subject groups, search interest, job-ad keywords).",
        "Huff model: fixed demand, Bavarian origins only, IIA understates substitution between near-identical programmes.",
        "Robotics: no intake anchor, fit and feasibility from a title-level check only.",
        "Scoring anchors for criteria other than demand written after evidence collection (before ranking).",
        "Blocked sources (robots.txt, logins) were not worked around; listed in the decision log.",
    ]),
    ("9 Recommendation and next steps", ["evidence_capture.md", "evidence_fit_staff.md", "evidence_benchmarks.md", "overlap_test.md"], [], [
        "Introduce the Cybersecurity B.Sc., staffed with {new_professorships}; first intake not before the G9 gap is over "
        "(2026 or later) and realistically after accreditation.",
        "Proposal to discuss (not a model result): the Cyber/OT M.Sc. ranks second; offer it later as a follow-on that uses the bachelor's staff and lab.",
        "Before a decision: ask THI and TH Deggendorf (or the state office) for actual cyber first-year numbers to narrow the range.",
        "Robotics: better as a strengthened specialisation of the KI B.Sc. than a new programme.",
    ]),
    ("Appendix", ["decision_log.md", "research_protocol.md"], [], [
        "Data sources and manifests (configs/sources.yaml, docs/*_manifest.json); key numbers (reports/key_numbers.yaml); reproducibility (Step 54).",
    ]),
]


def render() -> str:
    kn = load_numbers()
    out = ["# Report outline: a new study programme for EMI, OTH Amberg-Weiden (generated)", "",
           "Built by `python -m study_program_intelligence.report.outline` from reports/key_numbers.yaml. Numbers in "
           "**bold** come from the key-numbers file; edit the evidence docs or analysis modules, not this file.", ""]
    for head, docs, figs, bullets in SECTIONS:
        out += [f"## {head}", ""]
        out.append("Evidence: " + ", ".join(f"[{d}]({D}{d})" for d in docs))
        if figs:
            out.append("Figures: " + ", ".join(f"[{f}]({F}{f})" for f in figs))
        out.append("")
        for b in bullets:
            keys = re.findall(r"\{(\w+)\}", b)
            missing = [k for k in keys if k not in kn]
            if missing:
                raise KeyError(f"outline placeholder(s) without key number: {missing}")
            out.append("- " + re.sub(r"\{(\w+)\}", lambda m: f"**{kn[m.group(1)]['display']}**", b))
        out.append("")
    return "\n".join(out)


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"Written: {OUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
