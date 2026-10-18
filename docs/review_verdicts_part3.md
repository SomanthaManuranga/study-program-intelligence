# Review verdicts, part 3 (claims C345-C443: dashboard pages and README "Result" block)

Independent check against docs/evidence_*.md, docs/overlap_test.md, docs/kill_rules.md, docs/theme_precision.md,
docs/decision_log.md, configs/*.yaml and reports/key_numbers.yaml. Quotes are verbatim; where a quote comes from a
table row, the pipes are shown as "/".

| ID | Verdict | Evidence quote | Problem and suggested fix |
|---|---|---|---|
| C345 | n/a | - (definition of the (a)/(b)/(c) split; matches evidence_cannibalisation.md "Method") | |
| C346 | supported | decision_log.md: "kill_rules.md has no cannibalisation threshold and none is added after scoring started" | |
| C347 | supported | evidence_ranking.md: "Robotics with 50 % cannibalisation (scenario column above): net new first-years 7.5 / 14.3 / 27.6" | |
| C348 | supported | decision_log.md: "Result: (a) 14-27 %, (b) 73-86 %, (c) 13-16 % of gross." | |
| C349 | supported | evidence_cannibalisation.md: "If true cannibalisation were 50 % (about twice the model's maximum), net new first-years would be 10.5 / 19.5 / 37.5." | |
| C350 | caveat | decision_log.md: "Kill rule 1 passed (2 of 15 core security modules = 13 % in Industrie-4.0-Informatik; module-level coverage <= 28 %)." | The formal kill-rule-1 test (overlap_test.md) gave 25 % (2 of 8 core topics); 13 % is only a recheck on the draft's 15 security modules, so the label presents the smaller of two numbers as "the" kill-rule-1 overlap. Fix: label it "Kill rule 1 recheck: draft security modules already at OTH: 13 %" or show "25 % of core topics (13 % of draft security modules)". |
| C351 | supported | evidence_capture.md: "No Bavarian rule or guideline on a minimum first-year cohort was found" | |
| C352 | supported | evidence_capture.md: "The uncalibrated demand model implies 59-173 first-years for THI's cyber bachelor against a planned capacity of 25 with no admission limit." | |
| C353 | supported | evidence_catchment.md: "OTH 5,501; TH Deggendorf 5,595; FAU/TH Nürnberg 14,872" | |
| C354 | supported | evidence_catchment.md: "FOS/BOS share: own pool 40 %, Bavaria 39 %." | |
| C355 | caveat | evidence_catchment.md: "91 % of OTH's 100-km catchment is closer to Amberg/Weiden than to Deggendorf." | The label omits the base (OTH's <= 100 km catchment, 18,630 leavers); next to the own-pool metric it can be read as a share of the own pool, which is 100 % closer by definition. Fix: "Of OTH's 100-km catchment, closer to OTH than to Deggendorf: 91 %". |
| C356 | caveat | evidence_catchment.md: "only 42 % of OTH's 100-km catchment is closer to OTH than to the Nuremberg hub." | Same missing base as C355. Fix: "Of OTH's 100-km catchment, closer to OTH than to Nuremberg/Erlangen: 42 %". |
| C357 | supported | evidence_capture.md: "Best beta = 1.6 (SRMSE 0.50, R2 0.95 of the flows; beta within 10 % of the best fit: 1.3-1.95)." | |
| C358 | supported | evidence_capture.md: "Spatial pattern: good at Bezirk level (R2 0.95), but home shares are too low (see above)." | |
| C359 | supported | decision_log.md: "THI capacity 25 (official, likely >= intake; low)" | |
| C360 | supported | decision_log.md: "TH Deggendorf ~60 (one student review, weak; high)" | |
| C361 | supported | evidence_competition_demand.md: "Destatis has no separate subject for AI or cybersecurity; both sit inside Informatik, so their demand is read through Informatik and through supply." | |
| C362 | supported | evidence_forecast.md: "drift is the best model in all four series and 2-2.5 times more accurate than naive." | |
| C363 | supported | evidence_forecast.md: "a midpoint between the KMK floor and the drift trend, chosen by us as a planning value; it is not a model output." | |
| C364 | supported | evidence_demand_trends.md: "Cyber security is the largest specialist term, but its rise was 2018-2022; since 2022 it is a plateau." | |
| C365 | caveat | evidence_competition_demand.md: "in Bavaria they rose 6.1 % a year (2019–2024). Nationally the number has been flat since 2023" | The label gives no period or unit; 6.1 % is first-year students 2019-24 only, and the doc adds that the national number is flat since 2023 (and Bavaria fell in the 2025 G9 year). Fix: "Informatik first-years, Bavaria, 2019-24: +6.1 %/yr". |
| C366 | supported | evidence_forecast.md: "Even the conservative KMK scenario keeps Bavaria's cyber-proxy first-years at about 5,000 in 2030 and 5,500 in 2035 (2024: 4,936)" | |
| C367 | supported | evidence_forecast.md: "BY cyber proxy / 2030 / 5,057 / 6,019 (6,384-7,477)** / 5,538" | |
| C368 | supported | evidence_forecast.md: "BY cyber proxy / 2030 / 5,057 / 6,019 (6,384-7,477)** / 5,538" | |
| C369 | supported | evidence_demand_trends.md: "Since 2022 it is about 2x KI and 2.6x Robotik, and the only term with no zero months." | |
| C370 | supported | evidence_demand_trends.md: "Mean 2022-2026 (monthly): Cyber Security Studium 20.1, KI 9.6, Robotik 7.6" | |
| C371 | supported | evidence_demand_trends.md: "is now about 1/8 of all Informatik degree interest" | |
| C372 | supported | theme_precision.md: "31 dedicated bachelor and 32 master programmes in Germany, 4 and 6 within 150 km, none at OTH." | |
| C373 | supported | theme_precision.md: "31 dedicated bachelor and 32 master programmes in Germany, 4 and 6 within 150 km, none at OTH." | |
| C374 | supported | theme_precision.md: "31 dedicated bachelor and 32 master programmes in Germany, 4 and 6 within 150 km, none at OTH." | |
| C375 | supported | theme_precision.md: "126 general programmes in Germany offer cybersecurity as a focus area, 18 of them within 150 km (16 outside OTH" | |
| C376 | supported | decision_log.md: "45 ECTS new by new staff (consistent with 2 new professorships, Step 44), 10 ECTS teaching assignments, 110 ECTS reused/adapted EMI modules" | |
| C377 | supported | evidence_fit_modules.md: "Claim B (differentiation): an OT/industrial profile differentiates against most competitors, not against TH Deggendorf." | |
| C378 | supported | decision_log.md: "estimate 2 new professorships + 1 lab engineer + a security lab" (evidence_fit_staff.md: "Cost is not estimated here.") | |
| C379 | supported | decision_log.md: "e5 16/20 correct, TF-IDF 14/20." | |
| C380 | supported | evidence_fit_modules.md: "e5 overestimates coverage (4 of 4 errors in the hand check were false "covered"): treat 31 % / 39 % as upper-end." | |
| C381 | supported | decision_log.md: "EMI covers ~31 % of a typical cyber bachelor's security ECTS (range 18-39 %) and ~71 % of its general foundations" | |
| C382 | supported | decision_log.md: "the 31 % (bachelor) / 39 % (master) headline is an upper-end estimate." | |
| C383 | supported | decision_log.md: "TF-IDF (47 % / 45 %) is reported as a sensitivity range." | |
| C384 | supported | decision_log.md: "the 31 % (bachelor) / 39 % (master) headline is an upper-end estimate." | |
| C385 | supported | evidence_fit_staff.md: "about four professors already teach security modules (information security, cryptography, network security, AI security)" | |
| C386 | supported | decision_log.md: "New bachelor load 40-50 SWS/year = 1.1-1.7 professorships" | |
| C387 | supported | decision_log.md: "estimate 2 new professorships + 1 lab engineer + a security lab" | |
| C388 | supported | evidence_benchmarks.md: "Security-specific ECTS: 75 (36 %)" | |
| C389 | supported | evidence_outlet_jobs.md: "the shortage is at the bachelor-type level, which fits a HAW bachelor; for a master the shortage argument is weaker" | |
| C390 | supported | evidence_outlet_jobs.md: "Two snapshots two days apart (stable). Continue every 2–4 weeks until the analysis freeze (4 Dec) for a trend." | |
| C391 | supported | decision_log.md: "IT occupations in Bavaria +23.8 % (2019-2023), with academic degree +34.3 % (academic share 48.5 % -> 52.6 %)" | |
| C392 | supported | decision_log.md: "IT occupations in Bavaria +23.8 % (2019-2023), with academic degree +34.3 % (academic share 48.5 % -> 52.6 %)" | |
| C393 | supported | decision_log.md: "IT occupations in Bavaria +23.8 % (2019-2023), with academic degree +34.3 % (academic share 48.5 % -> 52.6 %)" | |
| C394 | supported | evidence_outlet_jobs.md: ""Berufe in der Informatik" (KldB 4310) are again a shortage occupation in 2025 (score 2.0)" | |
| C395 | supported | decision_log.md: "Cyber B.Sc. P(rank 1) 91.7 % (robotics 50 %: 93.2 %; skewed 2/3/5: 87.8 %); first in every leave-one-criterion-out run" | |
| C396 | supported | decision_log.md: "Decision: publicly available sources only. No primary survey and no internal OTH data." | |
| C397 | caveat | evidence_funnel.md: "the rule "weak evidence widens a score's range, it does not raise its centre" were written in Step 49" | True for the 14 Oct commit, but the funnel doc says later additions to the rules (non-demand scoring anchors, the weak-evidence rule, amended 18 Oct) came after evidence collection; the sentence implies the full rule set predates screening. Fix: add "; scoring anchors for the other criteria and one kill-rule addition followed on 17-18 Oct, before the ranking". |
| C398 | supported | evidence_funnel.md: "show the order in which candidates were filtered, with the count and the reason at each stage" | |
| C399 | overstated | evidence_capture.md: "The anchors are a planned capacity (THI) and an anecdote (Deggendorf), not measured intakes." | "No university publishes programme intakes" is a universal claim; the evidence only shows that the checked programmes (THI, TH Deggendorf, HNU, OTH, Kempten, TH Augsburg) publish none. Fix: "None of the comparable programmes we checked publishes its intake: the range rests on ...". |
| C400 | supported | evidence_ranking.md: "Robotics has the thinnest evidence: no intake anchor, fit and feasibility from a title-level overlap check only, no staffing or lab estimate." | |
| C401 | supported | decision_log.md: "Cyber B.Sc. P(rank 1) 91.7 % (robotics 50 %: 93.2 %; skewed 2/3/5: 87.8 %)" | |
| C402 | caveat | evidence_capture.md: "Ramp-up 60 % / 80 % / 100 % of steady state in the first three intake years is an assumption" | 39 is the steady state from year 3; the central first intake is 24, which the label does not show. Fix: "First-years / yr, central (steady state from year 3; year 1: 24)". |
| C403 | supported | evidence_cannibalisation.md: "Net new first-years: low 15, central 32, high 64." | |
| C404 | supported | evidence_catchment.md: "Yes, OTH has its own regional pool, about 5,500 qualified school leavers a year (10 % of Bavaria)." | |
| C405 | caveat | evidence_forecast.md: "The proxy measures the pool cyber programmes recruit from, not cyber demand itself" | The label leaves out that 5,538 is Bavarian first-years in Informatik-type subjects and a chosen midpoint; next to "Own pool 5,501" it reads like a forecast of OTH's regional pool, which the catchment doc puts at ~5,300 for 2029/30. Fix: "Bavarian first-years, cyber-proxy subjects, 2030 (central midpoint): 5,538". |
| C406 | caveat | evidence_fit_modules.md: "at most about a third of its security content, and less if the e5 overestimate is taken into account" | On the overview the 31 % appears without "upper end" (the fit page has it), so readers may take it as a point estimate. Fix: "Security content EMI covers (at most)": 31 %. |
| C407 | supported | evidence_outlet_jobs.md: "Specific security titles ("Cyber Security" 851, "Security Engineer" 838) each match about as many ads as" | |
| C408 | supported | evidence_fit_staff.md: "Estimate: 2 new professorships" | |
| C409 | supported | evidence_ranking.md: "Monte Carlo (10,000 draws, Dirichlet concentration 50, seed 42)" | |
| C410 | supported | decision_log.md: "the ranking explorer calls analysis.ranking.simulate unchanged (base weights passed through exactly, changed weights normalised to sum 1)" | |
| C411 | n/a | - (section heading) | |
| C412 | supported | decision_log.md: "explorer reproduces 91.7 / 6.0 / 2.3 %" | |
| C413 | supported | evidence_ranking.md: "its range is widened, and weak evidence widens a score's range without raising its centre" | |
| C414 | supported | decision_log.md: "lowest without demand 67.2 %, without labour 77.8 %" | |
| C415 | supported | evidence_ranking.md: "above the 80 % robustness bar" | |
| C416 | supported | evidence_ranking.md: "Independent capture draws (no common factor): 87.0 % / 10.0 % / 3.0 %." | |
| C417 | unsupported | decision_log.md: "a "Use of AI tools" paragraph in the method section" | Searched docs/*.md, configs/ and decision_log.md for "Claude Code", "AI coding" and "use of AI": the evidence docs only name Claude as proposer of the theme labels and the score sheet; that the analysis code and drafting were done with Claude Code is stated only in the report itself (docs/report/01_method.md). The statement is an honest disclosure, but nothing outside the report records it. Fix: add a decision-log entry recording AI-tool use for code and drafting, or keep the sentence and cite the method section as its source. |
| C418 | supported | decision_log.md: "Decided by: team (Somantha Manuranga)." | |
| C419 | overstated | decision_log.md: "the build fails on an unknown placeholder or a typed number (percentages, decimals, thousands separators, integers >= 10 outside allowed patterns)" | Integers below 10 and "allowed patterns" may still be typed, and the appendix tables are generated from configs, so "every number" is checked automatically only for the number classes listed. Fix: "Every percentage, decimal and number of 10 or more in the report text is inserted from ... and checked against its source document; small integers and the generated appendix tables are exempt". |
| C420 | overstated | evidence_funnel.md: "MCDA criteria and weights (configs/analysis.yaml); unchanged since" | The decision log has no entry for the 14 Oct criteria/weights or the kill rules (they are recorded in configs/analysis.yaml, docs/kill_rules.md and git history), and several entries (e.g. Steps 41, 44, 46) have no stated reason. Fix: "Method decisions are logged with date and who decided, most with a reason, in decision_log.md; criteria, weights and kill rules are in configs/analysis.yaml and docs/kill_rules.md". |
| C421 | n/a | - (table header) | |
| C422 | caveat | evidence_capture.md: "The anchors are a planned capacity (THI) and an anecdote (Deggendorf), not measured intakes." | Most rows match the decision log, but the capture row says "anchored on public intake figures", which contradicts the overview (C399) and the capture doc: the anchors are a capacity and an anecdote. Fix: "Capture model used for relative capture only, anchored on a public capacity (THI 25) and one anecdote (TH Deggendorf ~60)". |
| C423 | supported | configs/sources.yaml: "claim D, outlet (157 shortage occupations in 2025)" | |
| C424 | supported | configs/sources.yaml: "module handbooks (Modulhandbuecher) of the 10 dedicated cybersecurity programmes within 150 km + TH Mannheim benchmark" | |
| C425 | supported | configs/sources.yaml: "robots.txt disallows all automated access -> not used" | |
| C426 | supported | configs/sources.yaml: "teaching load of HAW professors (18 SWS), Step 44" | |
| C427 | supported | configs/sources.yaml: "Turku UAS skipped (robots.txt); manifest docs/benchmark_manifest.json" | |
| C428 | supported | configs/sources.yaml: "public intake/capacity anchors for the robotics bachelor and cyber master capture runs (Step 49)" | |
| C429 | supported | configs/sources.yaml: "THI Cloud Applications und Security Engineering capacity 30 from the Step 39 cache" | |
| C430 | supported | configs/sources.yaml: "snapshots 15 and 17 Oct 2026, next 1 Nov, 15 Nov, 1 Dec" | |
| C431 | overstated | docs/studiensuche_manifest.json: ""retrieved_utc": "2026-10-14T20:04:54+00:00"" (no hash field) | SHA-256 values appear in 8 manifests but not in studiensuche_manifest.json or jobsuche_snapshots.json (API downloads have a date only), so "downloads with date and SHA-256" overstates. Fix: "downloads with date (and SHA-256 for downloaded files) in the manifests in docs/". |
| C432 | supported | decision_log.md: "Cyber B.Sc. P(rank 1) 91.7 % (robotics 50 %: 93.2 %; skewed 2/3/5: 87.8 %); first in every leave-one-criterion-out run" | |
| C433 | supported | decision_log.md: "OTH Cyber B.Sc. steady state: low 21, central 39, high 75 first-years (year 1: 12 / 24 / 45)." | |
| C434 | caveat | evidence_cannibalisation.md: "students who would otherwise take OTH's KI or E&IT bachelor without a security focus are not in (a)" | ~82 % (73-86 %) is the Huff model's estimate, which the evidence doc calls a limitation; at 50 % cannibalisation net new would be 19.5 central, and no main limitation in C442 mentions this. Fix: "~82 % in the central case (73-86 % across model variants; the model does not count students drawn from OTH's KI and E&IT bachelors)". |
| C435 | supported | evidence_catchment.md: "a full-time cyber bachelor in the northern Oberpfalz / eastern Oberfranken has no dedicated competitor nearer than 80 km." | |
| C436 | caveat | evidence_forecast.md: "a midpoint between the KMK floor and the drift trend, chosen by us as a planning value; it is not a model output." | The 2030/2035 "central" values are a chosen midpoint, not a forecast, and the README does not say so (the dashboard does, C363). Fix: "4,936 (2024); central planning value (midpoint of KMK scenario and drift trend) ~5,540 (2030), ~6,220 (2035); KMK scenario alone 5,057 / 5,519". |
| C437 | caveat | evidence_outlet_jobs.md: "The shortage analysis is Germany-wide and by occupation group; it says nothing about IT security specifically or about Bavaria." | The shortage status holds only at specialist (bachelor-type) level and Germany-wide (software development is not a shortage at expert level); the README line has no level or region. Fix: "Informatik a shortage occupation at specialist (bachelor) level in Germany (BA, 2025)". |
| C438 | supported | decision_log.md: "EMI covers ~31 % of a typical cyber bachelor's security ECTS (range 18-39 %) and ~71 % of its general foundations" | |
| C439 | supported | decision_log.md: "estimate 2 new professorships + 1 lab engineer + a security lab" | |
| C440 | supported | evidence_ranking.md: "The Cybersecurity B.Sc. ranks first in 92 % of draws (93 % if robotics cannibalises 50 %), above the 80 %" | |
| C441 | supported | decision_log.md: "Master second (67 % rank 2), robotics last (72 % rank 3)." | |
| C442 | wrong | evidence_capture.md: "Low / 21 / 12 / just / no" (minimum-cohort table: steady state, year 1, meets 20 steady, meets 20 in year 1) | In the first-year range the README lists (21 / 39 / 75), the low case of 21 "just" meets the assumed minimum of 20; only its net new value (15.3) and year 1 (12) are below 20. The dashboard (C400) and the report say "21 against 20". Fix: "(wide first-year range; the low case only just reaches the assumed minimum cohort of 20, and only 15 of its 21 first-years are new to OTH)". |
| C443 | caveat | docs/report/09_limitations.md: "the low case is at the edge of viability" | The report states all three limitations, but it describes the low case as at the edge (21 vs 20), not below 20 as C442 says. This becomes true once C442 is reworded; no other change needed. |

## Summary

Counts (99 claims): supported 77, caveat 13, overstated 4, unsupported 1, wrong 1, n/a 3.

Non-supported claims:

- C350 (caveat): "Kill rule 1 overlap 13 %" is the recheck on the draft's security modules; the formal kill-rule-1 test gave 25 %.
- C355 (caveat): 91 % lacks its base (share of OTH's 100-km catchment).
- C356 (caveat): 42 % lacks its base (share of OTH's 100-km catchment).
- C365 (caveat): +6.1 %/yr lacks period and unit (Informatik first-years, Bavaria 2019-24; flat nationally since 2023).
- C397 (caveat): the 14 Oct commit is true, but the scoring anchors and the weak-evidence rule were added 17-18 Oct.
- C399 (overstated): "No university publishes programme intakes" generalises from the handful of programmes checked.
- C402 (caveat): 39 is the steady state from year 3; the central year-1 intake is 24.
- C405 (caveat): "Recruiting pool 2030" is Bavarian cyber-proxy first-years (a chosen midpoint), and next to the own pool it reads like a regional-pool forecast.
- C406 (caveat): 31 % is shown on the overview without "at most / upper end".
- C417 (unsupported): only the report itself says Claude Code wrote the code and drafted the report; no evidence doc or decision-log entry records it.
- C419 (overstated): "every number" is checked; small integers, allowed patterns and the appendix tables are exempt.
- C420 (overstated): not every method decision is in the decision log (weights and kill rules are not), and not every entry gives a reason.
- C422 (caveat): the decisions table says the capture model is "anchored on public intake figures"; the anchors are a capacity and an anecdote.
- C431 (overstated): SHA-256 values are missing from the Studiensuche and Jobsuche manifests.
- C434 (caveat): ~82 % new to OTH is a model estimate that misses cannibalisation from OTH's KI and E&IT bachelors (50 % stress test gives 19.5 central).
- C436 (caveat): the 2030/2035 "central" values are a chosen midpoint, not a forecast.
- C437 (caveat): the Informatik shortage holds at specialist (bachelor) level and Germany-wide only.
- C442 (wrong): the low case (21 first-years) just meets the minimum cohort of 20; only net new (15) and year 1 (12) are below it.
- C443 (caveat): the report gives the low case as "at the edge" (21 vs 20), not below 20; this is fixed once C442 is reworded.
