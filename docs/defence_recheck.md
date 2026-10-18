# Re-check of the flagged statements in docs/defence_qa.md

Status: 18 Oct 2026. Reviewer: independent fresh-context AI reviewer. I did not write the Q&A or the first review.
Input: the 30 rows of `docs/defence_review.md` whose verdict was not "supported". Current wording is from
`docs/defence_qa.md` (generated 18 Oct 18:34 from `docs/defence/qa.md`, commit bcc14d0, "first review applied").
Evidence: `docs/*.md`, `configs/*.yaml`, `reports/key_numbers.yaml`, `reports/final/report.md` and `git log`, all read-only.
No existing file was changed.

Verdicts: **supported** / **caveat** / **overstated** / **unsupported** / **wrong**, defined as in the first review.
Quotes are verbatim, with Markdown emphasis removed.

| Q | Current wording (excerpt) | Verdict now | Evidence | Remaining problem and fix |
|---|---|---|---|---|
| Q1 | "every number traces to a public source and the code rebuilds all results from the downloaded data" ... If pressed: "a rebuild needs the downloaded raw data plus a few manual downloads" | supported | decision_log.md: "Clean clone (committed code + data/raw + hand labels, no generated files): 20/20 steps + tests passed, 179/179 key numbers identical" | - ("rebuilt by anyone" is gone. The If pressed line gives the data/raw condition. The "every number traces to a public source" part is a new issue, see N1.) |
| Q2 | "school leavers by county for the bachelor capture, students of the Bavarian universities of applied sciences for the master, graduate numbers for the master pipeline" | supported | evidence_ranking.md: "Master origins are Bavarian state HAWs weighted by their students (Tabelle 5), not school leavers" | - |
| Q3 | "No, and the git history shows the order." | caveat | research_protocol.md: "Set in week 1 from the longlist in the final roadmap, reviewed separately for bachelor and master. Fixed on [date]." | Not changed. The protocol still points to an external "final roadmap" longlist that is not in the repository, and the "[date]" is still blank. Fix: add to If pressed "the repository contains no candidate list before the 22:42 screening; the protocol's week-1 longlist was never filled in". Or fill in or delete the protocol's longlist line. |
| Q3 | "Candidates then left the funnel stage by stage" + If pressed: "the screening filters themselves (stages 1 and 2) were written with the screening" | supported | report.md: "the screening filters (stages 1-2) were committed with the screening itself" | - (the pointer for this point is wrong, see N2) |
| Q3 | If pressed: "the weak-evidence rule was tightened after the first ranking run" | supported | decision_log.md: "Robotics fit/feasibility made symmetric (Step 49 correction; ... git 6c6138f 23:40)" | - |
| Q5 | "was run through the same capture, cannibalisation and ranking models" | supported | decision_log.md: "the Step 47/48 capture + cannibalisation model is run unchanged for the Robotics+AI B.Sc. and the Cyber/OT M.Sc." | - |
| Q5 | If pressed: "with Mechatronik und digitale Automation, OTH as a whole covers 7 of 8 robotics topics" | supported | overlap_test.md: "Mechatronik und digitale Automation (other faculty) covers automation, control and mechanics, so OTH as a whole covers 7 of 8 topics." | - |
| Q6 | "Informatik is the only large EMI field still growing (Bavaria 6.1 % a year, 2019-2024)" + If pressed: "nationally Informatik has been flat since 2023" | supported | evidence_competition_demand.md: "in Bavaria they rose 6.1 % a year (2019–2024). Nationally the number has been flat since 2023" | - (evidence_competition_demand.md is now cited) |
| Q6 | "the Bavarian cyber-proxy pool (first-years in Informatik, Technische Informatik and Computer- und Kommunikationstechniken) was 4,936 in 2024" | supported | evidence_forecast.md: "Cyber proxy = Informatik + Ingenieurinformatik/Technische Informatik + Computer- und Kommunikationstechniken." | - |
| Q6 | "Search interest only shows that cybersecurity is the largest specialist term we tracked, not that it grows." | supported | evidence_demand_trends.md: "since 2022 it is a plateau." | - |
| Q8 | "We do not use search interest as a growth argument" | supported | decision_log.md: "Trends is a supporting leading indicator for Claim A, not a demand count." | - (now consistent with Q6) |
| Q9 | "The low case applies the first ratio to TH Ingolstadt's planned capacity of 25, the high case the second ratio to an anecdotal ~60 at TH Deggendorf" | supported | evidence_capture.md: "High / Deggendorf-anchored (anecdotal ~60) x relative capture" | - |
| Q11 | If pressed: "the low case is not a floor: it is the median of 16-21 across the model variants, and TH Ingolstadt's capacity may be above its real intake" | supported | evidence_capture.md: "Ranges across the 9 model variants: low 16-21"; reports/capture.md: "low = THI-anchored median" | - |
| Q11 | "In the central and high cases the gross intake clears the bar from the first year." | supported | evidence_capture.md: "Central / 39 / 24 / yes / yes" and "High / 75 / 45 / yes / yes" | - |
| Q12 | If pressed: "a higher minimum would change the viability verdicts: at 25, even the central case would miss it in year 1 (24)" | supported | evidence_capture.md: "Central / geometric mean of low and high (a choice) / 24 / 31 / 39" | - (24 < 25 is arithmetic on the evidence table. The unsupported "not the ranking" clause has been removed.) |
| Q13 | "partly because the seven administrative regions are coarse" | supported | evidence_capture.md: "partly because Bezirke are coarse; real local pull is stronger." | - |
| Q13 | "only for relative quantities (OTH's intake relative to its competitors, and the cannibalisation shares), never for absolute numbers" | supported | evidence_cannibalisation.md: "The Step 47 Huff model (qualified school leavers by Bavarian county; distance decay calibrated on Bavarian student" | - (Evidence pointer gap, see N3) |
| Q13 | If pressed: "the error is larger for TH Ingolstadt, so we do not know in which direction it shifts the ratio" | supported | evidence_capture.md: "OTH: model 61 % vs actual 71 %; THI 37 % vs 71 %" | - |
| Q15 | "The new teaching load is an estimated 40-50 SWS a year." + If pressed: "leaves out extra exercise groups and thesis supervision, so the load may be higher" | supported | evidence_fit_staff.md: "Not included: extra exercise groups in the shared foundation modules ... thesis and internship supervision" | - (the 40-50 figure is labelled "New teaching load, bachelor", which matches the question) |
| Q16 | If pressed: "counting OTH Regensburg as a competitor the own pool is 3,807" | supported | evidence_catchment.md: "Own pool, with OTH Regensburg as competitor / 12 / 2,312 / 1,495 / 3,807" | - (the Answer still says "school leavers", not "qualified school leavers", which is minor) |
| Q17 | "a shortage occupation at bachelor level in Germany" + If pressed: "for computer science in general, not IT security specifically" | supported | evidence_outlet_jobs.md: "The shortage analysis is Germany-wide and by occupation group; it says nothing about IT security specifically or about Bavaria." | - |
| Q18 | If pressed: "the German security keywords ("IT-Sicherheit", "Informationssicherheit") are at or below that baseline" | supported | report.md: "the other security keywords ("Security Engineer", "IT-Sicherheit", "Informationssicherheit") are at or below the baseline." | - |
| Q20 | If pressed: "their first ranges (2 / 3 / 5) raised the mean and were made symmetric after the first ranking run; with the first ranges the cyber bachelor still won 87.8 %" | supported | evidence_ranking.md: "Robotics fit and feasibility 2 / 3 / 5 (skewed first draft, mean 3.33): 87.8 % / 5.3 % / 6.9 %" | - |
| Q21 | "They are a judgement, and no reason per weight is recorded; the logged rule was only to fix them before any candidate was seen." | supported | decision_log.md: "Reason: fix the rules before any candidate is seen, so the winner cannot be chosen first." | - (If pressed now says only "in line with the brief's question". research_protocol.md has the brief: "attract the most students") |
| Q22 | If pressed: "in the first ranking run, with robotics' skewed ranges, leaving out demand gave a near tie with robotics (49 % / 50 %)" | supported | decision_log.md: "first in every leave-one-criterion-out run except without demand (tie with robotics 49 % / 50 %)." | - (on the wording "near tie", see N4) |
| Q25 | "proposed the theme labels and the score sheet. We chose the sources and made or approved every method decision" | supported | configs/scores.yaml: "Proposed by Claude, reviewed by Soma, who changed robotics fit," | - |
| Q25 | "we reviewed all 110 proposed theme labels, judged twenty module pairs and changed the score sheet" | supported | theme_precision.md: "labels were proposed by Claude (AI) ... each of the 110 labels was reviewed by a team member"; evidence_fit_modules.md: "Hand check by Soma of 20 competitor/EMI pairs" | - |
| Q25 | "Every statistic in the report is checked automatically to appear in its evidence document" + If pressed: "the automatic check covers statistics, not small typed numbers" | caveat | report.md: "distances, years and dates, times, ECTS sizes, step numbers, table codes and small counts are typed in the text and not checked automatically" | Better than before: "to appear" is accurate, and the If pressed line narrows the claim. But "small typed numbers" understates the gap. Distances (50/100/150 km), dates, times and ECTS sizes are not checked either, and some of them are 10 or more. Fix: Answer "every percentage, decimal and number of ten or more in the report text is inserted from the key-numbers file and checked automatically to appear in its evidence document"; If pressed "distances, dates, times, ECTS sizes and small counts are typed and not checked". |
| Q25 | "flagged ones were fixed and re-checked" + If pressed: "the last two fixes were checked by the drafting session only" | supported | review_verdicts.md: "Verified by the drafting session against the code and the file, not by a third reviewer." | - |
| Q25 | If pressed: "the protocol's check of AI-related scores by our second team member is not recorded yet" | supported | decision_log.md: "Open for the team: the protocol requires that AI-related scores are checked by the second team member; this check is not recorded yet." | - (still open. Close it before the defence if possible.) |

## New issues

I read the whole of the current `docs/defence_qa.md` again. I compared every number with `reports/key_numbers.yaml`
(all match its display value and source document, including the new keys `loo_first_run_tie`,
`p_rank1_cyber_bsc_skew`, `pool_without_regensburg`, `low_variant_range` and `year1_central`) and checked every new
or rewritten sentence against the evidence. Four sentences need attention. All are caveats; none is overstated,
unsupported or wrong.

| # | Q | Current wording (excerpt) | Verdict | Evidence | Problem and fix |
|---|---|---|---|---|---|
| N1 | Q1 | "so every number traces to a public source" | caveat | evidence_capture.md: "Assumption: 20 first-years per year as the minimum"; evidence_forecast.md: "chosen by us as a planning value; it is not a model output." | Several numbers are team assumptions or choices, not public data. Examples: the minimum cohort of 20, the 60/80/100 % ramp-up, the weights, the forecast midpoint and the ECTS-to-SWS conversion. The 110 hand labels are team work. Fix: "so every data input is public (assumptions are labelled as ours), and the code rebuilds all results from the downloaded data". |
| N2 | Q3 | If pressed: "...the weak-evidence rule was tightened after the first ranking run; all of this is logged in decision_log.md" | caveat | decision_log.md: "Anchors for criteria other than demand written in Step 49, after evidence collection, before the ranking." (no entry dates the stage 1-2 filters) | decision_log.md logs the anchors and the rule change, but not the fact that the stage 1-2 screening filters were written with the screening. That fact is in evidence_funnel.md (funnel table, "14 Oct") and report Section 2. Fix: "...all of this is logged in evidence_funnel.md and decision_log.md". |
| N3 | Q13 | Evidence: "[evidence_capture.md]" for "and the cannibalisation shares" | caveat (pointer) | evidence_cannibalisation.md: "The Step 47 Huff model ... distance decay calibrated on Bavarian student" | The cannibalisation use of the model is documented in evidence_cannibalisation.md, which Q13 does not cite. Fix: add evidence_cannibalisation.md to the Evidence line. |
| N4 | Q22 | If pressed: "leaving out demand gave a near tie with robotics (49 % / 50 %)" | caveat (minor) | decision_log.md: "tie with robotics 49 % / 50 %" | The figures are right, but "near tie" with the numbers in this order hides that robotics was narrowly ahead (50 %). So in that run the cyber bachelor was not first without demand, which is exactly what the Answer's "stays first whichever single criterion is left out" refers to. Fix: "...leaving out demand put robotics narrowly ahead (50 % against 49 %)". |

Not counted as issues:
- Q3 "about five hours before": this holds for the kill rules (17:40). The weights (16:35) came about six hours before.
- Q16 says "school leavers" for "qualified school leavers" and omits the 19 % fall of the pool since 2013/14.
- Q18 lists only the German security keywords. "Security Engineer" (24.9 %) is also at baseline.
- Q15 "cost" gives no money figure for any item, which was already noted in the first review.
- `reports/final/defence_qa.pdf` (18:34:58) is newer than the Markdown (18:34:51), so it presumably has the current text. I did not open it.

## Summary

30 flagged rows re-checked:

| Verdict now | Count |
|---|---|
| supported | 28 |
| caveat | 2 |
| overstated | 0 |
| unsupported | 0 |
| wrong | 0 |

New issues in the rewritten text: 4, all caveat (N1-N4). There are no new overstated, unsupported or wrong statements.

Still not supported:
- Q3 (caveat): "the git history shows the order". The protocol's week-1 "final roadmap" longlist is not in the repo and its date is blank.
- Q25 (caveat): "Every statistic ... checked automatically". Distances, dates, times and ECTS sizes are typed and not checked, not only "small" numbers.
- N1 Q1 (caveat): "every number traces to a public source". The minimum cohort, ramp-up, weights and midpoint are team assumptions.
- N2 Q3 (caveat): "all of this is logged in decision_log.md". The stage 1-2 filter timing is in evidence_funnel.md and report Section 2 only.
- N3 Q13 (caveat, pointer): the cannibalisation use of the model needs evidence_cannibalisation.md in the Evidence line.
- N4 Q22 (caveat, minor): "near tie (49 % / 50 %)". Robotics was narrowly ahead without demand in the first run.

Open item outside the Q&A wording: the second-member check of AI-related scores (decision_log.md, Step 55) is still
not recorded. Q25 states this correctly.
