# Independent review of docs/defence_qa.md

Status: 18 Oct 2026. Reviewer: fresh-context AI reviewer, did not write the Q&A. Scope: every factual statement in
Answer, Evidence and "If pressed" of Q1-Q25 in `docs/defence_qa.md`, checked against `docs/*.md`, `configs/*.yaml`,
`reports/key_numbers.yaml`, `reports/final/report.md` and `git log` (read-only). No existing file was changed.

Verdicts: **supported** / **caveat** (misleading without a qualification the evidence attaches, incl. omission of a
stated weak point, wrong-meaning number or wrong Evidence pointer) / **overstated** / **unsupported** / **wrong**.
Quotes are verbatim (Markdown emphasis removed); "git log" quotes are from `git log --date=iso`.

| Q | Statement (short excerpt) | Verdict | Evidence quote | Problem and suggested fix |
|---|---|---|---|---|
| Q1 | Public data only was the scope of the brief and our protocol | supported | research_protocol.md: "Data: publicly available sources only. No primary survey. No internal OTH data." | - |
| Q1 | "so the whole analysis can be checked and rebuilt by anyone" | overstated | decision_log.md: "Not tested: re-downloading all sources (--ingest) from scratch, to spare the source servers"; .gitignore: "data/raw/" | The verified rebuild used a local copy of data/raw (not in the repo), and the Trends files and EMI handbooks are manual downloads. The decision log gives the brief as the reason for public data, not reproducibility. Fix: "...so every source is public and the pipeline rebuilds all key numbers from the cached raw data." |
| Q1 | we say openly that this is the main weakness | supported | report.md: "This is the largest single uncertainty (Sections 4 and 7)" | - |
| Q1 | no comparable programme we checked publishes its intake | supported | report.md: "None of the comparable programmes we checked publishes first-year numbers" | - |
| Q1 | asking THI and Deggendorf for one measured number is our first recommendation before a decision | supported | report.md: "The cheapest way to reduce the main uncertainty is one measured number: the actual first-year intakes of TH Ingolstadt's and TH Deggendorf's cyber bachelors" | - (the report also names the State Office as a route) |
| Q1 | one measured intake would cut the range by about half | supported | evidence_capture.md: "one figure would cut the range by about half." | - |
| Q2 | the brief asks which programme suits our faculty, so candidates had to fit EMI | supported | research_protocol.md: "Faculty: Elektrotechnik, Medien und Informatik (EMI), as set out in the project brief." | - |
| Q2 | analysed separately with level-specific evidence (school leavers for bachelors, graduates for masters) | caveat | evidence_ranking.md: "Master origins are Bavarian state HAWs weighted by their students (Tabelle 5), not school leavers; university graduates are not included." | The master's capture model does not use graduates. Graduates appear only in the pipeline/trend check (Informatik graduates of all degrees). Fix: "(school leavers for bachelors; for masters, HAW students by origin plus the graduate pipeline)". |
| Q2 | only compared at the ranking stage with the same criteria | supported | research_protocol.md: "Degree levels: bachelor and master, analysed separately and then compared." | - (funnel stages 0-2 screened themes for both levels together; kill rules 1 and 4 were applied per level) |
| Q2 | the master's demand model has one intake anchor only | supported | evidence_ranking.md: "The master's demand model rests on one capacity figure, its high end is borrowed." | - |
| Q3 | No, and the git history shows the order | caveat | research_protocol.md: "Set in week 1 from the longlist in the final roadmap, reviewed separately for bachelor and master. Fixed on [date]." | Git supports the order (no tracked file mentions cyber/security before 27bf2e0, checked with git grep). But the protocol points to an external "final roadmap" longlist that is not in the repo. Be ready to say what it contained. Fix ("If pressed"): "the repository contains no candidate list before the 22:42 screening." |
| Q3 | criteria and weights committed at 16:35 on 14 Oct | supported | git log: "cab5148 2026-10-14 16:35:08 +0200 Add source register and analysis settings" | - |
| Q3 | final five kill rules at 17:40 | supported | evidence_funnel.md: "958f823 ... Final kill rules 1-5 incl. the 50 % overlap threshold"; git log: "958f823 2026-10-14 17:40:40 +0200" | - |
| Q3 | about five hours before the first screening at 22:42 | supported | git log: "27bf2e0 2026-10-14 22:42:17 +0200 Add programme catalogue, demand-supply first look and evidence summary" | - (weights about six hours before) |
| Q3 | The weights never changed | supported | evidence_funnel.md: "MCDA criteria and weights (configs/analysis.yaml); unchanged since" (git log -- configs/analysis.yaml: only cab5148) | - |
| Q3 | candidates left the funnel stage by stage: 9 theme groups, 5 candidates, 3 for the ranking | caveat | report.md: "the screening filters (stages 1-2) were committed with the screening itself" | The counts are right (evidence_funnel.md), but the stage 1-2 filters were not fixed in advance. Only the weights and kill rules were, and the answer implies more. Fix: add "the stage 1-2 screening filters were written with the screening itself." |
| Q3 | anchors for other criteria written later, after evidence, before the first ranking run; logged | supported | decision_log.md: "Anchors for criteria other than demand written in Step 49, after evidence collection, before the ranking." | - |
| Q3 | (omission) rule change after the first ranking run | caveat | evidence_funnel.md: "the rule was tightened after that run (ranges must be symmetric, 17 Oct 23:40)" | "If pressed" omits that a scoring rule changed after results were seen, and this change moved the leave-one-out result (see Q22). Fix: add "and the weak-evidence rule was tightened after the first run; the earlier version is kept as a sensitivity." |
| Q4 | at the supply-gap stage we kept only themes OTH does not already offer | supported | evidence_funnel.md: "thin supply near OTH and not already offered by OTH" | - |
| Q4 | OTH already has titled programmes in all three | supported | evidence_funnel.md: "already offered at OTH: 1, 1 and 2 titled offers; not carried forward, no separate written verdict" | - |
| Q4 | energy and medtech belong mainly to other faculties | supported | evidence_funnel.md: "Energy and medtech also belong mainly to other faculties." | - |
| Q4 | no separate written verdict; the funnel document says so | supported | evidence_funnel.md: "the competition table shows OTH already offers each theme, but no separate written verdict exists." | - |
| Q5 | kill rule 1 drops only with more than 50 % core overlap with one OTH programme, set before scoring | supported | kill_rules.md: "more than 50 % of its core modules already appear in one OTH programme at the same level, and no credible differentiator remains." | - (set 14 Oct 17:40, see Q3) |
| Q5 | robotics sat exactly at the threshold, so it stayed in as the comparison case | supported | overlap_test.md: "Robotics + AI sits exactly at the threshold." | - |
| Q5 | "and was modelled in full" | caveat | evidence_ranking.md: "Robotics has the thinnest evidence: no intake anchor, fit and feasibility from a title-level overlap check only, no staffing or lab estimate." | The capture/cannibalisation/ranking models were run for robotics, but its fit, feasibility and intake anchor were not assessed in full. Fix: "and was run through the same capture and ranking models." |
| Q5 | it ranks last | supported | evidence_ranking.md: "Robotics is last in 72 % of draws." | - |
| Q5 | we propose it as a specialisation of the KI bachelor | supported | report.md: "Proposals (team judgement, not model results)" ... "(b) Robotics as a specialisation within the KI B.Sc." | - (say "team judgement", as in Q23) |
| Q5 | the overlap test matched topics on titles, not full module texts | supported | overlap_test.md: "Coverage is matched on EMI module titles, then checked against the module text where the title was unclear" | - (core topics came from competitor focus lists) |
| Q5 | (omission) OTH-wide overlap | caveat | overlap_test.md: "so OTH as a whole covers 7 of 8 topics. It passes the rule as written, but the cannibalisation risk is high." | An examiner will see 7 of 8 as the stronger counter-argument. Fix ("If pressed"): add "with Mechatronik (other faculty) OTH covers 7 of 8 topics; that is why we model 50 % cannibalisation for it." |
| Q6 | we read demand through three proxies | supported | report.md: "demand is read through computer-science entrants, search interest and job-ad keywords" | - |
| Q6 | Informatik is the only large EMI field still growing (Bavaria 6.1 % a year, 2019-2024) | caveat | evidence_competition_demand.md: "in Bavaria they rose 6.1 % a year (2019–2024). Nationally the number has been flat since 2023" | It omits the national plateau that the same sentence attaches (Germany Wirtschaftsinformatik is also +1.2 %/yr). Evidence pointer: 6.1 % and "only large EMI field" are in evidence_competition_demand.md, which the answer does not cite. Fix: "...still growing (Bavaria +6.1 % a year 2019-2024; Germany flat since 2023)" and add the pointer. |
| Q6 | Bavarian recruiting pool of computer-science first-years is 4,936 (2024) | caveat | evidence_forecast.md: "Cyber proxy = Informatik + Ingenieurinformatik/Technische Informatik + Computer- und Kommunikationstechniken." | The number is used with a different meaning. 4,936 is the cyber proxy (key "Bavaria cyber-proxy first-years 2024"), while Informatik alone is 4,110. Fix: "the Bavarian cyber-proxy pool (Informatik and two related subjects) is 4,936 first-years (2024)". |
| Q6 | "Cyber Security Studium" is the largest specialist term (2.6x Robotik since 2022) | caveat | evidence_demand_trends.md: "Since 2022 it is about 2x KI and 2.6x Robotik" ... "since 2022 it is a plateau." | The number is right, but it is a level and is given here as an answer to "demand grows". That contradicts Q8 ("we do not use search interest as a growth argument"). Fix: "...is the largest specialist search term (2.6x Robotik since 2022, but flat since then)". |
| Q6 | we label demand evidence "strong for the field, medium for cybersecurity itself" | supported | report.md: "Strength: strong for the field trend, medium for cybersecurity itself" | Minor pointer gap: the label is in report Section 3, not in the two cited evidence docs. |
| Q7 | the midpoint is a planning value we chose | supported | evidence_forecast.md: "a midpoint between the KMK floor and the drift trend, chosen by us as a planning value; it is not a model output." | - |
| Q7 | drift won the backtests (MASE 1.52 against 3.17 for naive) | supported | evidence_forecast.md: "drift is the best model in all four series and 2-2.5 times more accurate than naive."; key_numbers.yaml: "Backtest MASE of drift, Bavaria cyber proxy (naive 3.17)" | - (values are for the Bavarian cyber proxy) |
| Q7 | it under-forecast the recent surge and may over-extrapolate now | supported | evidence_forecast.md: "drift's errors were mostly under-forecasts, and recent data (Germany flat since 2023, Bavaria's 2025 dip) argue against simply extrapolating." | - |
| Q7 | conservative KMK path 5,057 in 2030, midpoint 5,538 | supported | decision_log.md: "Bavaria cyber proxy: conservative 5,057 / 5,519, upside 6,019 / 6,922, central ~5,540 / 6,220 (2030 / 2035)" | - (forecast table: 5,538) |
| Q7 | even the conservative path stays above the 2024 level | supported | evidence_forecast.md: "Even the conservative KMK scenario keeps Bavaria's cyber-proxy first-years at about 5,000 in 2030 and 5,500 in 2035 (2024: 4,936)" | - |
| Q7 | KMK index for Bavaria 0.99 in 2030 | supported | evidence_forecast.md: "Bavaria 0.99 (2030), 1.08 (2035)" | - |
| Q8 | high but no longer rising: 18.5 in 2022 and 22.0 in 2026 on the same scale | supported | evidence_demand_trends.md: "then only 18.5 to 22.0 by 2026 (slope +1.05 points/yr)" | - |
| Q8 | we do not use search interest as a growth argument | caveat | decision_log.md: "Trends is a supporting leading indicator for Claim A, not a demand count." | This is true for the report, but Q6 of this Q&A lists search interest as one of three answers to "how can you say demand grows". Fix Q6 as above, so that the two answers agree. |
| Q8 | cybersecurity is the largest specialist term, ahead of AI (about 2x KI) and robotics | supported | evidence_demand_trends.md: "Since 2022 it is about 2x KI and 2.6x Robotik, and the only term with no zero months." | - |
| Q8 | search terms are a narrow proxy; people also search programme or university names | supported | evidence_demand_trends.md: "Search terms are a narrow proxy: people also search "Cybersecurity studieren", programme names or university names." | - |
| Q9 | gravity model calibrated on Bavarian flows (distance decay 1.6, R2 0.95) | supported | evidence_capture.md: "Best beta = 1.6 (SRMSE 0.50, R2 0.95 of the flows" | - |
| Q9 | gives OTH 0.65-0.86 times TH Ingolstadt's intake | supported | evidence_capture.md: "OTH would draw 0.65-0.86 times THI's intake and 1.20-1.28 times TH Deggendorf's" | - |
| Q9 | "We then anchor that ratio": low on THI capacity 25, high on ~60 at Deggendorf | caveat | evidence_capture.md: "High / Deggendorf-anchored (anecdotal ~60) x relative capture" and "1.20-1.28 times TH Deggendorf's" | The high case uses a second ratio (OTH/Deggendorf 1.20-1.28), not the THI ratio. Fix: "low = 25 times the THI ratio; high = ~60 times the Deggendorf ratio (1.20-1.28)". |
| Q9 | central is the geometric mean, a choice | supported | evidence_capture.md: "geometric mean of low and high (a choice)" | - |
| Q9 | the model alone could not give absolute numbers: 59-173 for THI against capacity 25 | supported | evidence_capture.md: "The uncalibrated demand model implies 59-173 first-years for THI's cyber bachelor against a planned capacity of 25" | - |
| Q10 | treat the anchors as the weakest part | supported | report.md: "No measured programme intakes." ... "This is the largest single uncertainty" | - |
| Q10 | range, not a point; recommend one measured intake before deciding | supported | evidence_capture.md: "The best way to narrow the range is a direct question to THI and TH Deggendorf" | - |
| Q10 | model structure is stable: relative capture varies little across all model variants | supported | evidence_capture.md: "Relative capture is stable: across beta (1.3-1.95) and w (0-1)" | - ("all model variants" = the 9 beta/w variants; structural choices such as Bavarian-only origins were not varied) |
| Q10 | high anchor from one studycheck.de review; registered as weak evidence in sources.yaml | supported | configs/sources.yaml: "use: weak upper anchor of the capture model (Step 47)" and "status: used as weak evidence only" | - |
| Q11 | low case borderline: 21 against our assumed minimum of 20 | caveat | evidence_capture.md: "Ranges across the 9 model variants: low 16-21, high 72-77." and THI "anchor (intake likely <= 25)" | 21 is the median of the THI-anchored variants (reports/capture.md), and THI's capacity is likely an upper bound on its intake, so the low case is not a floor. Fix: "21 (16-21 across model variants, and THI may fill fewer than 25) against our assumed minimum of 20". |
| Q11 | only 15.3 of them are new to OTH | supported | decision_log.md: "Net new first-years low 15.3 / central 32.0 / high 64.4" | - |
| Q11 | central and high clear the bar from the first year | caveat | decision_log.md: "OTH Cyber B.Sc. steady state: low 21, central 39, high 75 first-years (year 1: 12 / 24 / 45)." | True for gross first-years only. The evidence has no year-1 net-new figure (reviewer's arithmetic: 60 % x 32.0 is about 19). Fix: "In the central and high cases the gross intake clears the bar from the first year (24 and 45)". |
| Q11 | that is why we recommend checking real intakes first | supported | evidence_capture.md: "The decisive uncertainty is not the model structure (relative capture is stable) but the real intake of comparable programmes" | - |
| Q11 | year 1 in the low case is only 12; the ramp-up is an assumption | supported | evidence_capture.md: "Ramp-up 60 % / 80 % / 100 % of steady state in the first three intake years is an assumption" | - |
| Q12 | our assumption; no Bavarian rule or guideline found | supported | evidence_capture.md: "No Bavarian rule or guideline on a minimum first-year cohort was found" | - |
| Q12 | TH Ingolstadt plans its cyber bachelor for 25 a year | supported | evidence_capture.md: "THI runs its cyber bachelor with a planned capacity of 25." | - |
| Q12 | a different minimum would move the viability verdict of the low case, not the ranking | caveat | configs/scores.yaml: "-> 1 + 4 ln(n/10) / ln 8, clipped to 1-5 (10 net new/yr = 1"; evidence_capture.md: "Central / 39 / 24 / yes / yes" | "Not the ranking" holds: the capture score does not use the minimum, but the pointer to scores.yaml is missing. "Only the low case" does not hold: a minimum of 25 (the THI figure cited one sentence earlier) would also fail the central case in year 1 (24). Fix: "...would move the viability verdicts (low case; central year 1 at a minimum of 25), not the ranking (configs/scores.yaml)". |
| Q13 | home-region share 61 % model against 71 % actual | supported | evidence_capture.md: "OTH: model 61 % vs actual 71 %; THI 37 % vs 71 %" | - |
| Q13 | "because the seven administrative regions are coarse" | overstated | evidence_capture.md: "partly because Bezirke are coarse; real local pull is stronger." | The evidence gives coarse regions as only part of the cause. Fix: "partly because...". |
| Q13 | we use the model only for OTH's intake relative to TH Ingolstadt's, never for absolute numbers | caveat | evidence_capture.md: "it is used only for relative capture"; "1.20-1.28 times TH Deggendorf's" | The model is also used relative to Deggendorf (high case) and for the cannibalisation shares (evidence_cannibalisation.md). Fix: "only for relative quantities (OTH against THI and Deggendorf, and the cannibalisation split), never for absolute numbers." |
| Q13 | (If pressed) not quantified how much the bias shifts relative capture | caveat | evidence_capture.md: "THI 37 % vs 71 %" | No document quantifies the bias, so this part is correct. But it omits that the under-prediction is much larger for THI, the denominator of the ratio, so the direction of the effect is unclear. Fix: add "the error is larger for TH Ingolstadt (37 % vs 71 %), so the effect on the ratio has no known direction." |
| Q14 | an upper-end estimate | supported | evidence_fit_modules.md: "e5 therefore tends to overestimate coverage: the headline numbers are upper-end estimates." | - |
| Q14 | every competitor module compared with every EMI module using multilingual embeddings | supported | evidence_fit_modules.md: "Each competitor module is compared with every EMI module" | - |
| Q14 | hand check of twenty pairs: right in 16 of 20, all errors overestimated coverage | supported | evidence_fit_modules.md: "e5 correct in 16 of 20" ... "All 4 e5 errors are the same kind: an advanced competitor module matched to an EMI basics module" | - (sample was stratified, 10 near the threshold) |
| Q14 | TF-IDF cross-check gives 47 % | supported | decision_log.md: "TF-IDF (47 % / 45 %) is reported as a sensitivity range." | - |
| Q14 | methods agree on 74 %, below target; module texts describe intentions | supported | evidence_fit_modules.md: "The two methods agree on 74 % of covered/gap labels (target was 80 %; not met"; "Module handbook texts describe intentions, not actual teaching" | - |
| Q15 | 2 new professorships (offensive security and forensics; defensive and OT security) | supported | evidence_fit_staff.md: "Estimate: 2 new professorships (one offensive security & forensics, one defensive / OT security incl. SOC)" | - |
| Q15 | one lab engineer, teaching assignments for law and security management, isolated security lab | supported | evidence_fit_staff.md: "plus one lab engineer and teaching assignments for law and governance"; "Needed: an isolated security lab / cyber range" | - |
| Q15 | new teaching load an estimated 40-50 SWS a year | caveat | evidence_fit_staff.md: "thesis and internship supervision; both add load to existing staff." and "the 31 % coverage is an upper-end estimate (Step 41), so the new load may be somewhat higher." | 40-50 is the new security load for the bachelor only. It leaves out extra exercise groups and supervision, and the evidence says it may be higher. Fix: "about 40-50 SWS a year of new security teaching (bachelor; extra exercise groups and supervision not included, so possibly more)". |
| Q15 | lab cost not estimated; staffing rests on stated assumptions | supported | evidence_fit_staff.md: "Cost is not estimated here." and "The ECTS-to-SWS conversion, lab-group split and cohort size are assumptions" | - (no money figure exists for any item, not only the lab) |
| Q16 | OT sets OTH apart from FAU, THI, THWS and HDBW, but not from Deggendorf | supported | evidence_fit_modules.md: "still a differentiator against FAU, THI, THWS and HDBW, but not against TH Deggendorf" | - |
| Q16 | the differentiation is regional reach | supported | evidence_catchment.md: "Differentiation therefore rests less on the OT label and more on regional reach" | - |
| Q16 | OTH has its own pool of about 5,500 school leavers a year | caveat | evidence_catchment.md: "a distinct catchment of ~5,500 qualified leavers a year (~3,800 without Regensburg)" | It omits the stated qualifier. A third of the pool is the Regensburg swing area next to OTH Regensburg, and the pool fell 19 % since 2013/14. Fix: "about 5,500 qualified school leavers a year (3,800 without Regensburg)". |
| Q16 | 91 % of its 100-km catchment is closer to OTH than to Deggendorf | supported | evidence_catchment.md: "91 % of OTH's 100-km catchment is closer to Amberg/Weiden than to Deggendorf" | - |
| Q16 | only 42 % of the catchment is closer to OTH than to Nuremberg/Erlangen | supported | evidence_catchment.md: "only 42 % of OTH's 100-km catchment is closer to OTH than to the Nuremberg hub" | - |
| Q17 | best public regional signal; no usable county-level occupation data | supported | evidence_outlet_jobs.md: "Regional demand therefore rests on the job-ad counts." | - |
| Q17 | IT jobs held by graduates in Bavaria grew +34.3 % (2019-2023) | supported | decision_log.md: "with academic degree +34.3 % (academic share 48.5 % -> 52.6 %)" | - |
| Q17 | computer science is a shortage occupation at bachelor level | caveat | evidence_outlet_jobs.md: "The shortage analysis is Germany-wide and by occupation group; it says nothing about IT security specifically or about Bavaria." | Placed next to a Bavarian figure, it reads as regional and security-specific. Fix: "...a shortage occupation at bachelor (specialist) level in Germany; IT security is not listed separately." |
| Q17 | ads match all qualification levels; the job board does not contain every ad | supported | evidence_outlet_jobs.md: "Ads cover all qualification levels, not only graduates." | - |
| Q18 | only 8 within 50 km; 191 within 100 km, Nuremberg and Regensburg inside | supported | evidence_outlet_jobs.md: "Within 50 km of Amberg there are only 8 "Cyber Security" ads, but 191 within 100 km (Nuremberg and Regensburg fall inside)." | - |
| Q18 | normal for a university in a small town | supported | evidence_outlet_jobs.md: "Graduates would mostly work in the wider region, which is normal for a HAW in a small city." | - (a judgement in the evidence doc) |
| Q18 | Bavaria's share of "Cyber Security" ads is 30.9 %, above the 22-25 % of general IT keywords | caveat | report.md: "the other security keywords ("Security Engineer", "IT-Sicherheit", "Informationssicherheit") are at or below the baseline." | The answer picks the security keyword with the highest share (apart from OT) and drops the qualifier that the report itself attaches. Fix: add "; the broader terms such as IT-Sicherheit (21.8 %) are at baseline." |
| Q18 | snapshots continue until the freeze; two days apart, median change 1.4 % | supported | evidence_outlet_jobs.md: "median absolute change 1.4 %" ... "snapshots continue every 2-4 weeks until 4 Dec." | - |
| Q19 | some, not most; 14-27 % from existing OTH programmes | supported | evidence_cannibalisation.md: "Most students would be new to OTH" ... "Cannibalisation is limited (14-27 %)" | - |
| Q19 | net new 15.3 / 32.0 / 64.4 a year | supported | decision_log.md: "Net new first-years low 15.3 / central 32.0 / high 64.4" | - |
| Q19 | kill rule 1 passed: 25 % of core topics, threshold more than 50 % | supported | evidence_cannibalisation.md: "kill rule 1 is passed (consistent with the 25 % of docs/overlap_test.md)" | - |
| Q19 | model does not see non-security OTH programmes; at 50 %: 10.5 / 19.5 / 37.5 | supported | evidence_cannibalisation.md: "If true cannibalisation were 50 % (about twice the model's maximum), net new first-years would be 10.5 / 19.5 / 37.5." | - |
| Q20 | robotics has the strongest local job signal (question premise) | supported | evidence_outlet_jobs.md: "Robotics has the strongest local signal (58 ads within 50 km, more than AI with 18)" | - |
| Q20 | its demand evidence is the weakest | supported | evidence_ranking.md: "the robotics evidence worst (falling feeders, no anchor)" | - |
| Q20 | feeder subjects flat or falling | supported | evidence_funnel.md: "robotics kept as a combined AI angle although its feeders are flat or falling" | - |
| Q20 | search interest is flat | supported | evidence_demand_trends.md: "Robotik is flat or slightly falling" | - |
| Q20 | no public intake anchor | supported | evidence_ranking.md: "none verified; assumed comparator intake 20-60" | - |
| Q20 | overlaps 50 % with KI; at half from OTH only 7.5 / 14.3 / 27.6 new | supported | evidence_ranking.md: "net new first-years 7.5 / 14.3 / 27.6 (half of the gross 14.9 / 28.7 / 55.3)" | - |
| Q20 | fit/feasibility title-level only; "we widened their ranges instead of raising the scores" | caveat | evidence_ranking.md: "the first version 2 / 3 / 5 had a mean of 3.33 and so raised the centre in effect, now a sensitivity" | The first version did raise the mean. It was corrected only after the first ranking run. Fix: add "(a first, skewed range was made symmetric after the first run; it is kept as a sensitivity)". |
| Q21 | the team chose the weights, before any screening | supported | decision_log.md: "all before the first screening (22:42)" and "Decided by: team (Somantha Manuranga)." | Minor pointer gap: configs/analysis.yaml holds the values only, while the timing is in evidence_funnel.md and decision_log.md. |
| Q21 | demand 0.30, labour 0.20, fit 0.20, feasibility 0.15, differentiation 0.10, regional 0.05 | supported | configs/analysis.yaml: "student_demand: 0.30 # includes the new-to-OTH share" (and the five other lines) | - |
| Q21 | "Demand has the largest weight because the brief asks which programme attracts the most students" | unsupported | decision_log.md: "Reason: fix the rules before any candidate is seen, so the winner cannot be chosen first." | No document records a reason for any weight value, and the brief was written down only on 18 Oct. As worded, this is a reason given after the fact. Fix: "Demand has the largest weight; our reason was the brief's question (which programme attracts the most students), though we did not write a rationale down at the time." |
| Q21 | drew 10,000 weight sets around these values | supported | configs/analysis.yaml: "draws: 10000" and "dirichlet_concentration: 50 # higher means samples stay closer to the base weights" | - (scores were drawn as well) |
| Q21 | left out each criterion in turn | supported | evidence_ranking.md: "Leave-one-criterion-out (P(rank 1), weights renormalised)" | - |
| Q21 | weights are a judgement; sensitivity runs show the dependence | supported | evidence_ranking.md: "The lead rests mostly on student demand and labour relevance." | - |
| Q22 | first in 91.7 % of draws | supported | evidence_funnel.md: "1: Cybersecurity B.Sc. (91.7 %)" | - |
| Q22 | stays first whichever single criterion is left out; lowest 67.2 % without demand | caveat | decision_log.md: "first in every leave-one-criterion-out run except without demand (tie with robotics 49 % / 50 %)." | This holds only after the robotics range was made symmetric. In the first ranking run, leaving out demand gave a tie with robotics, and the change was made after that run. Fix ("If pressed"): add "with the first, skewed robotics range, leaving out demand gave a tie with robotics (49 % / 50 %)." |
| Q22 | with independent capture draws 87.0 % | supported | evidence_ranking.md: "Independent capture draws (no common factor): 87.0 % / 10.0 % / 3.0 %." | - |
| Q22 | 80 % bar set at reporting, not before the run; lead rests on demand and labour | supported | decision_log.md: "The 80 % robustness bar was set when the ranking results were reported (17 Oct), not before the run" | - |
| Q23 | the master ranks second | supported | evidence_ranking.md: "Second place is the master (67 % rank 2" | - |
| Q23 | 6 dedicated cyber masters within 150 km | supported | theme_precision.md: "31 dedicated bachelor and 32 master programmes in Germany, 4 and 6 within 150 km, none at OTH." | - |
| Q23 | Deggendorf already teaches OT security in its master | supported | evidence_ranking.md: "held back by differentiation (6 cyber masters within 150 km, OT already at Deggendorf) and a low regional effect." | - |
| Q23 | draws more from OTH's own programmes (22-37 %) | supported | evidence_ranking.md: "22-37 % (AI for Industrial Applications, IT und Automation)" | - |
| Q23 | keeps few students in the region | supported | evidence_ranking.md: "and a low regional effect." (kept in region 0.7 / 2.2 / 5.5) | - |
| Q23 | follow-on once the bachelor produces graduates: a team judgement, not a model result | supported | report.md: "Proposals (team judgement, not model results)" ... "(a) The Cyber/OT M.Sc. as a follow-on." | - |
| Q23 | one anchor (30 at TH Ingolstadt) and a borrowed spread | supported | evidence_ranking.md: "THI Cloud Applications und Security Engineering capacity 30; no second anchor (high = low x B.Sc. spread, assumption)" | - |
| Q24 | we did not circumvent anything blocked | supported | report.md: "No blocked or login-protected source was circumvented" | - |
| Q24 | programme-level intakes not published by the programmes we checked | supported | report.md: "None of the comparable programmes we checked publishes first-year numbers" | - |
| Q24 | federal-state regional database (robots.txt) | supported | report.md: "The federal-state regional database (robots.txt disallows all automated access)" | - |
| Q24 | Bavarian GENESIS web service (login failed) | supported | report.md: "the Bavarian GENESIS web service (the login fell back to guest access)" | - (more exactly: guest access only, and the header login timed out) |
| Q24 | OTH staff profile pages (skipped on principle) | supported | report.md: "OTH staff profile pages (blocked for AI crawlers; skipped on principle)" | - |
| Q24 | some competitor handbooks | supported | report.md: "the TH Mannheim module handbook (robots.txt), and the THI robotics and TH Augsburg robotics module handbooks (no longer reachable)" | - |
| Q24 | where scripts were blocked we used another permitted route or downloaded public files by hand | supported | report.md: "we used only another permitted route" ... "or downloaded the public file by hand (the EMI module handbooks under OTH's /fileadmin/" | - (be ready to say the hand-downloaded files were OTH's own handbooks) |
| Q24 | Saxony and Thuringia not in the model, which on its own biases the estimate downward | supported | report.md: "students from Saxony, Thuringia and further away are missing, which on its own biases the estimate downward" | - |
| Q25 | Claude Code wrote the code and drafted the texts under our direction | supported | report.md: "The analysis code and the drafting of this report were done with Claude Code, an AI coding assistant, under the direction of the team." | - |
| Q25 | we chose the sources, made every method decision | caveat | configs/scores.yaml: "Proposed by Claude, reviewed by Soma"; theme_precision.md: "labels were proposed by Claude (AI)" | This matches the team's own statement (report Section 1, decision_log.md), but the record shows that several method artefacts were proposed by Claude and then approved or changed. Fix: "we made or approved every method decision; each is logged with who decided." |
| Q25 | human checks: all 110 theme labels, twenty module pairs, the score sheet | caveat | theme_precision.md: "each of the 110 labels was reviewed by a team member (Somantha Manuranga), who agreed with all 110." | The 110 labels were proposed by the AI and reviewed by a person (110 of 110 agreed). An examiner may call that a rubber stamp. Fix: "reviewed all 110 AI-proposed theme labels". |
| Q25 | every statistic comes from the key-numbers file and is checked against its evidence document automatically | caveat | report.md: "distances, years and dates, times, ECTS sizes, step numbers, table codes and small counts are typed in the text and not checked automatically" | "Every statistic" is too broad, and the automatic check tests only that the number occurs verbatim in its source (decision_log.md: "Each number must occur verbatim in its source doc"), not that it carries the same meaning. Fix: "every percentage, decimal and number of ten or more is inserted from the key-numbers file and checked to occur in its evidence document." |
| Q25 | independent AI reviewers checked all 443 statements | supported | decision_log.md: "(443 claims; ...) and judged by three fresh-context reviewer agents against the evidence docs" | - (report, dashboard and README) |
| Q25 | every flagged one was fixed and re-checked | caveat | review_recheck2.md: "Caveat: 2." ... "C306 (new error from the edit)"; git log: "93224ff ... 13 + 2 remaining findings fixed" | All are fixed (report.md now reads correctly for C306 and C068), but no re-check of the last two fixes is recorded. Fix: "every flagged one was fixed; the fixes went through two re-check rounds." |
| Q25 | review by AI reviewers, not people; spot checks covered samples | supported | decision_log.md: "The Step 55 claim review was done by separate fresh-context AI reviewers that did not see the drafting conversation." | - |
| Q25 | (omission) conflict-of-interest check | caveat | decision_log.md: "Open for the team: the protocol requires that AI-related scores are checked by the second team member; this check is not recorded yet." | The answer lists the human checks but omits that a check the protocol requires is not yet done. Close it before the defence, or add "the second-member check of AI-related scores required by our protocol is still open." |

## Summary

131 statements checked (Answer, Evidence and "If pressed" of all 25 questions, plus five omission rows and the
Evidence-pointer checks folded into the rows).

| Verdict | Count |
|---|---|
| supported | 101 |
| caveat | 27 |
| overstated | 2 |
| unsupported | 1 |
| wrong | 0 |

Numbers: every figure in the Q&A matches reports/key_numbers.yaml and its source document. One is used with a
different meaning: Q6 calls the cyber-proxy figure 4,936 "computer-science first-years".

Evidence pointers that lack the support: Q6 (6.1 % and "only large EMI field" are in evidence_competition_demand.md, not
cited; the "strong / medium" label is in report Section 3), Q12 ("not the ranking" rests on configs/scores.yaml, not
cited), Q21 (configs/analysis.yaml has the values, not the "before any screening" timing).

### Non-supported items

Unsupported
- Q21: "Demand has the largest weight because the brief asks..." No document records a rationale for the weights.

Overstated
- Q1: "the whole analysis can be checked and rebuilt by anyone." The rebuild needs the local data/raw (git-ignored) and manual downloads, and a fresh re-download was not tested.
- Q13: "because the seven administrative regions are coarse." The evidence says "partly because".

Caveat
- Q2: "graduates for masters." The master capture model uses HAW students by origin; graduates appear only in the pipeline check.
- Q3: "git history shows the order." The protocol refers to an external "final roadmap" longlist that is not in the repo.
- Q3: "candidates left the funnel stage by stage." The stage 1-2 filters were written with the screening, not in advance.
- Q3 (omission): the weak-evidence rule was tightened after the first ranking run.
- Q5: "modelled in full." Robotics fit, feasibility and anchor rest on a title-level check and assumptions only.
- Q5 (omission): OTH as a whole covers 7 of 8 robotics topics.
- Q6: "only large EMI field still growing (Bavaria 6.1 %)." It omits the national plateau since 2023, and the source doc is not cited.
- Q6: 4,936 is the cyber proxy, not computer-science first-years.
- Q6: the search-interest level is offered as growth evidence, which contradicts Q8 (plateau since 2022).
- Q8: "we do not use search interest as a growth argument." Q6 of the same Q&A does.
- Q9: "anchor that ratio." The high case uses the separate OTH/Deggendorf ratio (1.20-1.28).
- Q11: "low case 21." It is the median of the variants (16-21), and THI's 25 is likely an upper bound.
- Q11: "central and high clear the bar from the first year." This holds for gross only; year-1 net new is not shown.
- Q12: "only the low case's viability would move." A minimum of 25 also fails central year 1 (24), and the scores.yaml pointer is missing.
- Q13: "relative to TH Ingolstadt's" only. The model is also used against Deggendorf and for the cannibalisation shares.
- Q13: the bias is larger for THI (37 % vs 71 %), so the direction of the effect on the ratio is unknown.
- Q15: 40-50 SWS excludes extra exercise groups and supervision and may be higher.
- Q16: the 5,500 pool omits "3,800 without Regensburg".
- Q17: the shortage status is Germany-wide and not security-specific.
- Q18: the 30.9 % share is the top security keyword; IT-Sicherheit and Informationssicherheit are at or below baseline.
- Q20: "widened ranges instead of raising the scores." The first skewed range did raise the mean and was corrected after the first run.
- Q22: "first whichever criterion is left out." In the first run, leaving out demand gave a 49 % / 50 % tie with robotics.
- Q25: "made every method decision." Score sheet and labels were proposed by Claude and approved by the team.
- Q25: "all 110 theme labels." These were AI-proposed labels that the reviewer agreed with in all 110 cases.
- Q25: "every statistic... checked automatically." Only percentages, decimals and numbers of 10 or more are checked, and only that they occur verbatim.
- Q25: "every flagged one... re-checked." No re-check of the last two fixes is recorded.
- Q25 (omission): the protocol's second-member check of AI-related scores is still open.

Most important for the defence: Q21 (an unsupported reason for the weights), Q22 together with Q3 and Q20 (the leave-one-out
robustness depends on a rule change made after the first ranking run), Q11 and Q12 (the low case is not a floor; a minimum of 25
affects the central case in year 1) and Q25 (the protocol check is still open).
