# Independent review, part 1: claims C001-C157 (Summary, 1 Method, 2 Funnel, 3 Demand, 4 Capture)

Reviewer: independent agent (did not write the report). Basis: evidence docs in docs/, configs/, docs/decision_log.md,
and the git history (read-only). Table cells: any "|" inside a quoted table row is written as "/".

| ID | Verdict | Evidence quote | Problem and suggested fix |
|---|---|---|---|
| C001 | n/a | - | Statement of the research question. |
| C002 | supported | decision_log.md: "Result: Cyber B.Sc. P(rank 1) 91.7 % (robotics 50 %: 93.2 %; skewed 2/3/5: 87.8 %)" | - |
| C003 | supported | decision_log.md: "Master second (67 % rank 2), robotics last (72 % rank 3)." | - |
| C004 | supported | evidence_ranking.md: "Robotics is last in 72 % of draws." | - |
| C005 | supported | kill_rules.md: "Written before any candidate is scored. Set by the team on 14 Oct 2026." (git: final rules 958f823 at 17:40, screening 27bf2e0 at 22:42) | - |
| C006 | supported | evidence_funnel.md: "4,840 programme offers from 13 study fields; 11 EMI-related Destatis subjects; title rules for 9 theme groups" (stage 3 out: 3) | - |
| C007 | overstated | evidence_competition_demand.md: "Computer science is the only large EMI field still growing." | Drops "large": the same table shows other EMI subjects also growing in Germany (Computer- und Kommunikationstechniken +2.5 %, Regenerative Energien +0.7 %, Mikroelektronik +29.1 %). Fix: "Computer science is the only large EMI field still growing (Bavaria 6.1 % per year, 2019-2024)." |
| C008 | caveat | evidence_forecast.md: "a midpoint between the KMK floor and the drift trend, chosen by us as a planning value; it is not a model output." | The summary presents the 5,538 "central" value as if forecast; the evidence labels it a chosen midpoint, and the search-term ranking is only among the terms tracked. Fix: "...to 5,538 in 2030 (central planning value, the midpoint of the KMK and trend paths; conservative 5,057). Among the degree search terms tracked, 'Cyber Security Studium' is the largest..." |
| C009 | supported | evidence_catchment.md: "Yes, OTH has its own regional pool, about 5,500 qualified school leavers a year (10 % of Bavaria)." | - |
| C010 | supported | decision_log.md: "OTH Cyber B.Sc. steady state: low 21, central 39, high 75 first-years (year 1: 12 / 24 / 45)." | - |
| C011 | caveat | evidence_fit_modules.md: "e5 overestimates coverage (4 of 4 errors in the hand check were false "covered"): treat 31 % / 39 % as upper-end." | 71 % and 31 % are e5 headline values that the evidence calls upper-end estimates, and "2 new professorships" is a rounded estimate of 1.1-1.7. Fix: "EMI already teaches about 71 % of a cyber bachelor's foundations but at most about 31 % of its security content (upper-end estimates); the gap needs an estimated 2 new professorships, a lab engineer and a security lab." |
| C012 | caveat | evidence_outlet_jobs.md: "Full-text keyword search: ads can match several keywords, and a match does not mean the ad is for a specialist." | Under the heading "Graduates are in demand", the counts are keyword matches across all qualification levels (evidence: "Ads cover all qualification levels, not only graduates"). Fix: "851 job ads matching the keyword 'Cyber Security' in Germany (snapshot 15 Oct 2026, all qualification levels), 30.9 % of them in Bavaria and 191 within 100 km of Amberg." |
| C013 | supported | evidence_outlet_jobs.md: "with academic degree / 83,924 / 112,676 / +34.3 %" | - |
| C014 | caveat | evidence_cannibalisation.md: "students who would otherwise take OTH's KI or E&IT bachelor without a security focus are not in (a)." | "Only 14-27 %" is a model result that leaves out cannibalisation from OTH programmes without a security focus; the evidence gives a 50 % stress test (net new 10.5 / 19.5 / 37.5). Fix: "In the capture model 14-27 % ... would come from existing OTH programmes (the model misses students from programmes without a security focus; at 50 % cannibalisation net new would be 10.5 / 19.5 / 37.5)." |
| C015 | caveat | evidence_cannibalisation.md: "Both are far below 50 %: kill rule 1 is passed (consistent with the 25 % of docs/overlap_test.md)." | 13 % is a later module-count recheck; the formal kill-rule test (overlap_test.md, core topics) gave 25 % and module-level coverage reaches 28 %. Quoting only the lowest figure understates overlap. Fix: "Kill rule 1 ... is passed: 25 % of core topics in the formal test (13-28 % in later module-level rechecks)." |
| C016 | supported | decision_log.md: "first in every leave-one-criterion-out run (lowest without demand 67.2 %, without labour 77.8 %)" | - |
| C017 | supported | evidence_ranking.md: "the Step 47/48 capture and cannibalisation model was run unchanged for all three options so that none is scored on a model the others lack" | - |
| C018 | n/a | - | Heading. |
| C019 | overstated | evidence_capture.md: "HNU Neu-Ulm Angewandte Cyber Security / HNU pages / admission-free; no intake figure published / not usable" | The evidence shows only that intakes were not found for the few programmes checked (OTH, THI, TH Deggendorf, HNU, robotics comparators); a universal claim about all universities is not established. Fix: "None of the comparable programmes we checked publishes its intake." |
| C020 | supported | evidence_capture.md: "The anchors are a planned capacity (THI) and an anecdote (Deggendorf), not measured intakes." | - |
| C021 | supported | evidence_cannibalisation.md: "Low / 21 / 5.7 / 15.3 / 2.8" | - |
| C022 | supported | evidence_capture.md: "The decisive uncertainty is not the model structure (relative capture is stable) but the real intake of comparable programmes" | - |
| C023 | supported | evidence_forecast.md: "Destatis has no cybersecurity subject; cyber programmes are classified under Informatik." | - |
| C024 | supported | evidence_ranking.md: "Robotics has the thinnest evidence: no intake anchor, fit and feasibility from a title-level overlap check only, no staffing or lab estimate." | - |
| C025 | n/a | - | Recommendation (team judgement). |
| C026 | n/a | - | Labelled as team judgement. |
| C027 | n/a | - | Proposal labelled as team judgement. |
| C028 | supported | evidence_ranking.md: "net new first-years 7.5 / 14.3 / 27.6 (half of the gross 14.9 / 28.7 / 55.3)" (overlap_test.md: "4 of 8 / 50 %") | - |
| C029 | unsupported | Searched docs/ and configs/ for "brief": only decision_log.md ("Reason: specified in the project brief.") and research_protocol.md mention it; the brief's question text is not in any evidence doc. | The wording of the brief ("attract the most students ... why it suits the faculty") cannot be checked. Fix: add the brief (or its question) to the repository/appendix and cite it, e.g. "The project brief (Appendix X) asks ...". |
| C030 | supported | research_protocol.md: "Status: draft v2, 14 Oct 2026 (scope confirmed)" | - |
| C031 | supported | research_protocol.md: "Which new or substantially differentiated degree programme should OTH Amberg-Weiden consider, at bachelor or master level, given new student demand, differentiation" | - |
| C032 | supported | research_protocol.md: "Faculty: Elektrotechnik, Medien und Informatik (EMI), as set out in the project brief." | - |
| C033 | supported | research_protocol.md: "Degree levels: bachelor and master, analysed separately and then compared." | - |
| C034 | caveat | research_protocol.md: "using the Amberg-Weiden region (catchment within 100 and 150 km) for bachelor students and a wider national and international view for master students." | The regional capture scope applies to the bachelor only; the master uses a wider view. Fix: "the region around Amberg and Weiden for bachelor capture, a wider (Bavarian HAW / national) view for the master." |
| C035 | overstated | research_protocol.md: "The team has no OTH application or admission figures" / evidence_capture.md: "all subjects 836; engineering sciences (incl. Informatik) 452" | Public OTH enrolment figures at faculty-group level were available and used; and "no university published programme-level intakes" generalises from the handful of programmes checked. Fix: "We had no OTH application or admission figures and no programme-level enrolment figures (only OTH-wide and subject-group first-years), and none of the comparable programmes we checked published its intake." |
| C036 | supported | research_protocol.md: "so capture is estimated as a range and stated as an assumption in the report." | - |
| C037 | supported | research_protocol.md: "A candidate wins only if all four hold and the feasibility gate passes." | - |
| C038 | supported | research_protocol.md: "A. Demand: enough prospective students across Germany want this field, after demographic change is removed." | - |
| C039 | supported | research_protocol.md: "B. Capture: OTH can win a realistic share, given competitors and location." | - |
| C040 | supported | research_protocol.md: "C. Fit: EMI can teach it with existing staff, labs and modules, or with a costed gap." | - |
| C041 | supported | research_protocol.md: "D. Outlet: graduates find relevant jobs, in Germany and in the region." | - |
| C042 | n/a | - | Structural sentence. |
| C043 | supported | research_protocol.md: "Students who would otherwise study another OTH programme are not new enrolment for OTH. Report total and new-to-OTH enrolment separately." | - |
| C044 | supported | kill_rules.md: "Written before any candidate is scored. Set by the team on 14 Oct 2026." (five rules incl. "at most three candidates per level") | - |
| C045 | supported | evidence_ranking.md: "Evidence: ranking of the three shortlisted options (MCDA + Monte Carlo)" | - |
| C046 | supported | decision_log.md: "download 11 GENESIS tables for 2005 to 2025 (winter semesters / examination years)" | - |
| C047 | supported | configs/sources.yaml: "programme offers (studienangebote) by study field; 4,840 offers from 13 fields, 14-15 Oct 2026" | - |
| C048 | supported | configs/sources.yaml: "coverage: actual 2017-2023, forecast 2024-2035; state-run universities" (Dok. 251: "forecast 2025-2040") | - |
| C049 | supported | configs/sources.yaml: "use: claim B, catchment (Step 42)" ... "use: claim D, IT occupations 2019-2023 (Step 43)" | - |
| C050 | supported | evidence_fit_staff.md: "EMI module handbooks (Step 40, data/interim/modules.csv: module responsibility per module)" | - |
| C051 | supported | decision_log.md: "4 programmes with public curriculum structure: USTP St. Pölten IT Security (BSc, full module list), FH OÖ Hagenberg" | - |
| C052 | supported | configs/sources.yaml: "job offers (/pc/v6/jobs), total matches per keyword and region" | - |
| C053 | supported | configs/sources.yaml: "use: search interest in degree terms (Step 37)" | - |
| C054 | overstated | docs/studiensuche_manifest.json: ""status": "cached", "pages": 37, "items": 724, "retrieved_utc": "2026-10-14T20:04:54+00:00"" (no sha256 field in any of its entries) | Not every download has a SHA-256: the Studiensuche manifest, the job-ad snapshots and the manually downloaded Trends CSVs carry dates but no checksum, and some register entries (e.g. avbayhig_4) have no access route. Fix: "Every data source is registered with its URL and use (Appendix A1); document downloads are recorded with date and SHA-256 checksum, API downloads with date." |
| C055 | supported | theme_precision.md: "Rules: the title keyword rules in analysis/themes.py, applied to titles as in the supply counts" | - |
| C056 | overstated | theme_precision.md: "all 70 cybersecurity title matches, random samples of 10 robotics, 10 ai_data and 5 embedded_iot title matches" | Only three of the eight other theme groups were sampled; automation, energy, medtech, media/games and microelectronics rules were not checked. Fix: "...and samples of the robotics, AI/data and embedded themes were checked by hand". |
| C057 | supported | decision_log.md: "Models naive, drift, damped-trend ETS; rolling-origin backtests from 2012, h = 1-5, MASE." | - |
| C058 | supported | evidence_forecast.md: "Conservative: KMK scenario (constant share x KMK Dok. 1 index)" | - |
| C059 | overstated | evidence_capture.md: "The anchors are a planned capacity (THI) and an anecdote (Deggendorf), not measured intakes." | Calls the anchors "public intake figures"; they are a planned capacity and a student-review anecdote. Fix: "...anchored on a published planned capacity (TH Ingolstadt) and one anecdotal intake (TH Deggendorf) of comparable programmes (Section 4)." |
| C060 | supported | evidence_fit_modules.md: "Similarity: multilingual-e5-base sentence embeddings (headline) and character-n-gram TF-IDF (independent cross-check)." | - |
| C061 | supported | decision_log.md: "Split the new programme's students with the Step 47 Huff model (with vs without the new OTH programme)" | - |
| C062 | supported | configs/analysis.yaml: "dirichlet_concentration: 50 # higher means samples stay closer to the base weights" (six weights listed) | - |
| C063 | supported | decision_log.md: "reviewed row by row by a team member, who agreed with all 110" | - |
| C064 | supported | theme_precision.md: "each of the 110 labels was reviewed by a team member (Somantha Manuranga), who agreed with all 110." | - |
| C065 | supported | evidence_fit_modules.md: "e5 correct in 16 of 20, TF-IDF correct in 14 of 20. Decision (option a): e5 is the headline" | - |
| C066 | supported | evidence_ranking.md: "Score sheet: configs/scores.yaml (proposed by Claude, reviewed and changed by Soma)." (changes: robotics fit, feasibility, labour) | - |
| C067 | overstated | decision_log.md: "Spot check of 12 numbers passed (Soma)." | Logged spot checks exist for Step 40 (10 modules), Step 50 (12 numbers) and Step 51 (10 sentences), not "at each step". Fix: "Key numbers were spot-checked against their source documents when the report was built (12 numbers in Step 50, 10 sentences in Step 51)." |
| C068 | wrong | decision_log.md: "Safeguards: programme data only (no personal data), 2-second delay between requests" | The Studiensuche, Jobsuche and GENESIS API downloads used a 2 s delay (also DELAY_SECONDS = 2 in the ingest code); only document downloads used 3 s. Fix: "...and waited between requests (2 s for the APIs, at least 3 s or the site's crawl delay for document downloads)." |
| C069 | supported | decision_log.md: "Not used: Regionaldatenbank (robots.txt "Disallow: /", all automated access)" (evidence_fit_staff.md: "we treat that as the site owner's wish and did not read person pages") | - |
| C070 | n/a | - | Structural reference. |
| C071 | supported | decision_log.md: "Score sheet configs/scores.yaml proposed by Claude, reviewed by Soma" | - |
| C072 | supported | decision_log.md: "Decided by: team (Somantha Manuranga)." | - |
| C073 | overstated | decision_log.md: "the build fails on an unknown placeholder or a typed number (percentages, decimals, thousands separators, integers >= 10 outside allowed patterns)" | Numbers matching the allowed patterns (distances such as "82 km" and "105 km", years, clock times "16:35", ECTS, integers below 10) are typed in the text and are not in key_numbers.yaml, so not every number is traced and checked. Fix: "Every statistic in this report is inserted from ...; distances, dates, times and small counts are typed and were checked by hand." |
| C074 | supported | research_protocol.md: "One team member is enrolled in the Master Artificial Intelligence for Industrial Applications at OTH." | - |
| C075 | unsupported | research_protocol.md: "Every AI-related score is checked by the other team member." (searched decision_log.md, evidence_ranking.md: score sheet "reviewed and changed by Soma" only) | The protocol states the rule, but no evidence doc records that the other team member actually checked the AI-related scores. Fix: record the check (who, when) in the decision log, or write "the protocol requires that scores related to AI programmes are checked by the other team member". |
| C076 | n/a | - | Normative framing sentence. |
| C077 | n/a | - | Structural sentence. |
| C078 | wrong | git show dff024f:docs/kill_rules.md: "Threshold: [TO AGREE, e.g. more than 50 % of core module titles or descriptions matched]" | The 16:37 commit held a draft with four rules and open thresholds; the five rules with the 50 % threshold were committed in 958f823 at 17:40 (five hours before 22:42). evidence_funnel.md repeats the 16:37 error. Fix: "...criteria and weights at 16:35, a kill-rule draft at 16:37 and the final five kill rules at 17:40, five hours before the first demand and supply screening (22:42)." Correct evidence_funnel.md too. |
| C079 | supported | evidence_funnel.md: "MCDA criteria and weights (configs/analysis.yaml); unchanged since" (git log: only cab5148 touches configs/analysis.yaml) | - |
| C080 | supported | evidence_funnel.md: "scoring anchors for criteria other than demand and the rule "weak evidence widens a score's range, it does not raise its centre"" | - |
| C081 | caveat | kill_rules.md: "(amended 18 Oct 2026: a skewed range such as 2 / 3 / 5 raises the mean and so the centre in effect)" | The weak-evidence rule was amended, and robotics rescored 2/3/5 to 1.5/3/4.5, after a first ranking had been computed (decision_log.md Step 49: 87.8 %). Fix: "Both were written before the first ranking run; the weak-evidence rule was tightened after that run (robotics range made symmetric), and the earlier version is kept as a sensitivity." |
| C082 | supported | evidence_funnel.md: "4,840 programme offers from 13 study fields; 11 EMI-related Destatis subjects; title rules for 9 theme groups" | - |
| C083 | caveat | evidence_competition_demand.md: "Robotics + AI / feeders flat or falling; AI pull / thin (1 BA within 100 km) / Mechatronik, KI, Automation / shortlist (bachelor)" | The stage 1 filter as worded ("feeder subjects must not be shrinking") would also have dropped robotics (Mechatronik -3.6 %, Technische Informatik -0.1 %), which passed on "AI pull". Fix: state the exception, e.g. "feeder subjects must not be shrinking (robotics kept as a combined AI angle despite falling feeders)". |
| C084 | supported | evidence_funnel.md: "generic AI / data (32 BA / 34 MA within 150 km, OTH offers both levels)" | - |
| C085 | supported | overlap_test.md: "Embedded / cyber-physical systems, master / IT und Automation (M.Eng.) / 7 of 8 / 88 % / dropped" | - |
| C086 | supported | evidence_funnel.md: "none (no feasibility rating of 1; Informatik entrants not falling; Informatik graduates rising)" | - |
| C087 | supported | evidence_funnel.md: "weights fixed 14 Oct; 10,000 draws / 3 / Cyber/OT M.Sc. (P(rank 1) 6.0 %), Robotics+AI B.Sc. (2.3 %)" | - |
| C088 | n/a | - | List of evidence documents per stage (citation structure). |
| C089 | supported | evidence_funnel.md: "The 5 candidates after stage 2: Cybersecurity B.Sc., Cybersecurity M.Sc. (industrial / OT profile), embedded / cyber-physical systems M.Sc., Robotics + AI B.Sc." | - |
| C090 | caveat | overlap_test.md: "Part-time AI master (control case) / AI for Industrial Applications (M.Sc.) / identical / — / dropped" | It was dropped by kill rule 1 (identical curriculum), not by the incrementality (cannibalisation) test, which was never run for it. Fix: "The last was included on purpose as a control case for the incrementality rule; it was dropped at kill rule 1 because OTH already offers the same curriculum." |
| C091 | overstated | kill_rules.md: "Anchors for the other criteria were written in Step 49 (configs/scores.yaml), after the evidence was collected but before the ranking was computed." | Not every stage used rules written before its data: the stage 1-2 screening filters are not in the 14 Oct rule files and were committed with the screening data (27bf2e0), and the scoring anchors came after evidence collection. Fix: "The weights and kill rules were committed before the first screening; the later screening filters and scoring anchors are logged with their dates; the git history shows the sequence." |
| C092 | supported | evidence_ranking.md: "Same model for all: Huff split with distance decay beta 1.3-1.95 (calibrated in Step 47)" | - |
| C093 | supported | overlap_test.md: "Robotics + AI sits exactly at the threshold." | - |
| C094 | supported | overlap_test.md: "kept on the list only as the comparison case." | - |
| C095 | supported | evidence_funnel.md: "the competition table shows OTH already offers each theme, but no separate written verdict exists." | - |
| C096 | supported | evidence_funnel.md: "Energy and medtech also belong mainly to other faculties." | - |
| C097 | supported | evidence_funnel.md: "Stage 0-2 use title keyword rules (precision 90-100 % in the hand-labelled check, small samples for non-cyber themes) and the catalogue's 13 study fields" | - |
| C098 | overstated | theme_precision.md: "random samples of 10 robotics, 10 ai_data and 5 embedded_iot title matches" | Only 4 of the 9 theme rules were checked by hand (and three of them on samples of 5-10); the rules for automation, energy, medtech, media/games and microelectronics were not checked. Fix: "The precision of the cybersecurity, robotics, AI/data and embedded rules was checked by hand (Section 1); the other rules were not checked, and themes outside these fields were not screened." |
| C099 | caveat | evidence_catchment.md: "The pool shrinks slowly and a little faster than Bavaria (-19 % vs -13.5 % since 2013/14)." | Only the Bavarian computer-science first-year pool is projected not to shrink; OTH's own regional pool of qualified school leavers has fallen 19 % and is projected at ~5,300 in 2030 (5,501 in 2023/24). Fix: "...and the Bavarian pool of computer-science first-years a cyber programme recruits from is not shrinking." |
| C100 | supported | evidence_forecast.md: "Destatis has no cybersecurity subject; cyber programmes are classified under Informatik." | - |
| C101 | supported | evidence_competition_demand.md: "both sit inside Informatik, so their demand is read through Informatik and through supply." | - |
| C102 | supported | evidence_competition_demand.md: "First-year students in Informatik rose from 18,586 (2019) to 21,428 (2025) in Germany while all subjects fell 1.0 % a year" | - |
| C103 | supported | evidence_competition_demand.md: "Nationally the number has been flat since 2023 (21,434 → 22,083 → 21,428)." | - |
| C104 | supported | evidence_competition_demand.md: "The electrical and media side is shrinking." | - |
| C105 | supported | evidence_competition_demand.md: "Elektrotechnik −2.6 %/yr (Germany 2019–25), Mechatronik −3.6 %/yr, Medieninformatik −3.5 %/yr, Medientechnik −8.6 %/yr" | - |
| C106 | wrong | evidence_forecast.md: "the Informatik share of all first-years rose steadily (DE 3.7 % in 2015 -> 5.4 % in 2024)" | Wrong attribution: the sentence cites evidence_competition_demand.md, which does not contain these shares; they are in evidence_forecast.md and refer to Germany. Fix: "...rose from 3.7 % in 2015 to 5.4 % in 2024 in Germany ([evidence_forecast.md])." |
| C107 | supported | evidence_forecast.md: "2025 is the Bavarian G9 transition year (Bavaria all subjects 68,872 -> 57,216" ... "so all models are trained to 2024." | - |
| C108 | supported | evidence_forecast.md: "Reading: drift is the best model in all four series and 2-2.5 times more accurate than naive." (BY cyber proxy: 1.52 vs 3.17) | - |
| C109 | supported | evidence_forecast.md: "drift under-forecast the 2019-2024 surge in 76-80 % of the Bavarian backtest errors" | - |
| C110 | n/a | - | Description of what is shown. |
| C111 | supported | decision_log.md: "Bavaria cyber proxy: conservative 5,057 / 5,519, upside 6,019 / 6,922, central ~5,540 / 6,220 (2030 / 2035); 2024: 4,936." | - |
| C112 | supported | evidence_forecast.md: "BY cyber proxy / 2030 / 5,057 / 6,019 (6,384-7,477)** / 5,538" | - |
| C113 | supported | evidence_forecast.md: "Even the conservative KMK scenario keeps Bavaria's cyber-proxy first-years at about 5,000 in 2030 and 5,500 in 2035 (2024: 4,936)" | - |
| C114 | supported | evidence_forecast.md: "chosen by us as a planning value; it is not a model output." | - |
| C115 | supported | evidence_demand_trends.md: "Since 2022 it is about 2x KI and 2.6x Robotik, and the only term with no zero months." | - |
| C116 | supported | evidence_demand_trends.md: "Download 2 shows it going from 0 (2015-17) to 18.5 (2022), then only 18.5 to 22.0 by 2026" | - |
| C117 | supported | evidence_demand_trends.md: "The rising share of the anchor after 2022 (6.4 % to 12.6 %) comes mainly from "Informatik Studium" falling" | - |
| C118 | supported | evidence_demand_trends.md: "KI study interest peaked in 2023-24 and is falling (download 2: 13.3 in 2024 to 9.0 in 2026)." | - |
| C119 | supported | evidence_demand_trends.md: "It is a leading indicator, not a student count." | - |
| C120 | supported | theme_precision.md: "31 dedicated bachelor and 32 master programmes in Germany, 4 and 6 within 150 km, none at OTH." | - |
| C121 | supported | evidence_catchment.md: "the nearest full-time competitors remain TH Ingolstadt (82 km) and TH Deggendorf (105 km)" | - |
| C122 | supported | theme_precision.md: "126 general programmes in Germany offer cybersecurity as a focus area, 18 of them within 150 km" | - |
| C123 | n/a | - | Cross-reference. |
| C124 | n/a | - | Method definition. |
| C125 | caveat | evidence_ranking.md: "Informatik graduates Germany 14,249 (2019) -> 21,858 (2025), Bavaria 2,676 -> 4,788 (Destatis 21321, all degrees): not triggered." | The counts are graduates of all degrees, not the bachelor graduates that C124 names as the master pipeline. Fix: "Informatik graduates (all degrees) rose from ..." |
| C126 | overstated | evidence_competition_demand.md: "Computer science is the only large EMI field still growing." | Same as C007: other, smaller EMI subjects also grow. Fix: "...the field it belongs to is the only large EMI field still growing, ..." |
| C127 | supported | evidence_demand_trends.md: "Its growth phase was 2018-2022; since then interest is high but stable, not still rising." | - |
| C128 | supported | evidence_competition_demand.md: "Their natural feeders (Mechatronik, Technische Informatik) are flat or falling" | - |
| C129 | caveat | evidence_capture.md: "an OTH cyber bachelor is viable in the central and high scenarios and borderline in the low one." | The headline claim omits that it holds only in the central and high scenarios. Fix: "Claim: OTH can win enough first-year students for a viable cohort in the central and high scenarios, given its location and its competitors." |
| C130 | supported | evidence_catchment.md: "School leavers with a university entrance qualification by Bavarian county, school years 2013/14 to 2023/24" | - |
| C131 | supported | evidence_catchment.md: "40 % of the own pool comes via Fachoberschule/Berufsoberschule, the classic HAW route." (own pool 5,501, 10.1 %) | - |
| C132 | supported | evidence_catchment.md: "only 42 % of OTH's 100-km catchment is closer to OTH than to the Nuremberg hub" (Deggendorf: 91 %) | - |
| C133 | supported | evidence_catchment.md: "the only dedicated cyber programme there is FAU's part-time online bachelor" | - |
| C134 | supported | evidence_catchment.md: "one third of the own pool (1,694) is in Regensburg city and county" (with OTH Regensburg: 3,807) | - |
| C135 | supported | evidence_catchment.md: "The pool shrinks slowly and a little faster than Bavaria (-19 % vs -13.5 % since 2013/14)." | - |
| C136 | supported | evidence_catchment.md: "The KMK projection implies a recovery to ~5,300 by 2030 and ~5,700 by 2035 after the 2025 G9 gap" | - |
| C137 | supported | evidence_catchment.md: "A new programme should not plan its first intake for autumn 2025 (G9 gap)." | - |
| C138 | supported | evidence_capture.md: "Student flows by origin (7 Regierungsbezirke) for all 17 state HAWs" | - |
| C139 | supported | evidence_capture.md: "Best beta = 1.6 (SRMSE 0.50, R2 0.95 of the flows; beta within 10 % of the best fit: 1.3-1.95)." | - |
| C140 | supported | evidence_capture.md: "The model under-predicts home-region shares (OTH: model 61 % vs actual 71 %" | - |
| C141 | supported | evidence_capture.md: "The uncalibrated demand model implies 59-173 first-years for THI's cyber bachelor against a planned capacity of 25 with no admission limit." | - |
| C142 | supported | evidence_capture.md: "across beta (1.3-1.95) and w (0-1), OTH would draw 0.65-0.86 times THI's intake" | - |
| C143 | n/a | - | Structural sentence. |
| C144 | supported | evidence_capture.md: "Low / THI-anchored (THI intake = its capacity 25) x relative capture / 12 / 16 / 21" | - |
| C145 | supported | evidence_capture.md: "Central / geometric mean of low and high (a choice) / 24 / 31 / 39" | - |
| C146 | supported | evidence_capture.md: "High / Deggendorf-anchored (anecdotal ~60) x relative capture / 45 / 60 / 75" | - |
| C147 | supported | evidence_capture.md: "Ramp-up 60 % / 80 % / 100 % of steady state in the first three intake years is an assumption" | - |
| C148 | unsupported | evidence_capture.md: "upper bound for OTH's informatics-type intake (no programme split published)" | The 452 figure is supported, but "a mid-sized programme, not a large one" is not: no OTH programme-level intakes are known to compare against. Fix: "...452 in winter 2024/25; the central 39 first-years would equal about 9 % of that intake." |
| C149 | supported | evidence_capture.md: "No Bavarian rule or guideline on a minimum first-year cohort was found" | - |
| C150 | supported | evidence_capture.md: "Assumption: 20 first-years per year as the minimum for running a HAW bachelor" | - |
| C151 | supported | evidence_capture.md: ""Kapazität 25 Studierende pro Studienjahr"; admission-free" | - |
| C152 | supported | evidence_capture.md: "Low / 21 / 12 / just / no" (Central 39 / 24 / yes / yes; High 75 / 45 / yes / yes) | - |
| C153 | supported | evidence_capture.md: "an OTH cyber bachelor is viable in the central and high scenarios and borderline in the low one." | - |
| C154 | supported | evidence_capture.md: "Relative capture is stable: across beta (1.3-1.95) and w (0-1)" | - |
| C155 | overstated | evidence_capture.md: "HNU Neu-Ulm Angewandte Cyber Security / HNU pages / admission-free; no intake figure published / not usable" | The anchor weakness is supported, but "because no university publishes programme-level intakes" generalises from the few programmes checked. Fix: "...a planned capacity and one anecdotal intake, because none of the comparable programmes we checked publishes its intake." |
| C156 | supported | evidence_capture.md: "one figure would cut the range by about half." | - |
| C157 | overstated | decision_log.md: "THI capacity 25 (official, likely >= intake; low) and TH Deggendorf ~60 (one student review, weak; high)" | The evidence only says the omission of Saxony/Thuringia "understates the pool"; the estimate as a whole is not shown to be conservative, since the low anchor may exceed THI's real intake and the high anchor is an anecdote. Fix: "...are not modelled; this leaves part of the pool out, which on its own biases the estimate downward." |

## Summary

Counts (157 claims):

- supported: 112
- caveat: 12
- overstated: 13
- unsupported: 3
- wrong: 3
- n/a: 14

Non-supported claims:

- C007 (overstated): "only growing EMI field" drops the evidence's "large"; smaller EMI subjects also grow.
- C008 (caveat): central 5,538 is a chosen midpoint, not a forecast; search ranking is among tracked terms only.
- C011 (caveat): 71 % / 31 % are upper-end e5 estimates; "2 professorships" rounds 1.1-1.7.
- C012 (caveat): job-ad counts are keyword matches across all qualification levels, not graduate jobs.
- C014 (caveat): 14-27 % cannibalisation excludes non-security OTH programmes; 50 % stress test omitted.
- C015 (caveat): 13 % is the lowest recheck; formal kill-rule test gave 25 %, module level up to 28 %.
- C019 (overstated): "no university publishes" generalises from a few checked programmes.
- C029 (unsupported): the project brief's wording is not in any evidence doc.
- C034 (caveat): regional capture scope applies to the bachelor; master uses a wider view.
- C035 (overstated): OTH aggregate enrolment figures were available; "no university" overgeneralises.
- C054 (overstated): API downloads and Trends CSVs have no SHA-256; not all register entries have an access route.
- C056 (overstated): only robotics, AI/data and embedded were sampled, not "the other themes".
- C059 (overstated): anchors are a planned capacity and an anecdote, not "public intake figures".
- C067 (overstated): spot checks logged only at Steps 40, 50, 51, not "at each step".
- C068 (wrong): API downloads used a 2 s delay, not at least 3 s.
- C073 (overstated): distances, times, years and small integers are typed and not checked via key numbers.
- C075 (unsupported): no record that the other team member checked AI-related scores.
- C078 (wrong): the 16:37 commit was a 4-rule draft with open thresholds; final five rules at 17:40.
- C081 (caveat): weak-evidence rule amended and robotics rescored after a first ranking run.
- C083 (caveat): robotics passed stage 1 although its feeder subjects are shrinking.
- C090 (caveat): control case failed kill rule 1 (overlap), not an incrementality test.
- C091 (overstated): stage 1-2 filters and scoring anchors were not written before their data.
- C098 (overstated): only 4 of 9 theme rules were checked by hand.
- C099 (caveat): OTH's own regional pool is shrinking (-19 %); only the Bavarian CS pool is not.
- C106 (wrong): cites evidence_competition_demand.md, but the shares are in evidence_forecast.md (Germany).
- C125 (caveat): graduate counts are all degrees, not bachelor graduates.
- C126 (overstated): same "only growing EMI field" problem as C007.
- C129 (caveat): claim heading omits that viability holds only in central and high scenarios.
- C148 (unsupported): "mid-sized programme" has no programme-level comparison in the evidence.
- C155 (overstated): "no university publishes" generalisation.
- C157 (overstated): omission biases the pool downward, but the estimate as a whole is not shown to be conservative.
