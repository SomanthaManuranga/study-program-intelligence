# Independent review of report claims C158-C344 (part 2)

Scope: report sections 5 Fit, 6 Outlet, 7 Cannibalisation, 8 Ranking, 9 Limitations, 10 Recommendation, Appendix A1-A3.
Claims from docs/review_claims.md; evidence from docs/, configs/ and reports/*.md. Quotes are verbatim except that
Markdown bold markers are dropped and table-cell separators are shown as "/".

| ID | Verdict | Evidence quote | Problem and suggested fix |
|---|---|---|---|
| C158 | caveat | evidence_fit_staff.md: "OT-security testbed. Cost is not estimated here." | Staffing is estimated in professorships, but the lab cost is not, so "a costed gap" overstates how far the gap is costed. Fix: "...plus a gap whose staffing is estimated (two professorships, a lab engineer) and whose lab cost is still open." |
| C159 | supported | evidence_fit_modules.md: "Each competitor module is compared with every EMI module (bachelor vs EMI bachelors; master vs EMI bachelors + masters)." | |
| C160 | supported | evidence_fit_modules.md: "It counts as "covered" if its most similar EMI module is above a threshold." | |
| C161 | supported | decision_log.md: "EMI covers ~31 % of a typical cyber bachelor's security ECTS (range 18-39 %) and ~71 % of its general foundations" | |
| C162 | supported | decision_log.md: "EMI covers ~31 % of a typical cyber bachelor's security ECTS (range 18-39 %) and ~71 % of its general foundations" | |
| C163 | supported | decision_log.md: "the 31 % (bachelor) / 39 % (master) headline is an upper-end estimate" | |
| C164 | supported | evidence_fit_modules.md: "All 4 e5 errors are the same kind: an advanced competitor module matched to an EMI basics module" | |
| C165 | supported | evidence_fit_modules.md: "Cryptography / 4 / 7.5 / 100 % / 100 %" | |
| C166 | supported | evidence_fit_modules.md: "Network Security / 6 / 7.5 / 80 % / 60 %" | |
| C167 | supported | evidence_fit_modules.md: "Forensics / 5 / 5 / 12 % / 38 %" | |
| C168 | supported | evidence_fit_modules.md: "Penetration testing & auditing (practice) / 6 / 5 / 0 % / 29 %" | |
| C169 | supported | evidence_fit_modules.md: "Security Operations & Incident Management / 5 / 5 / 0 % / 33 %" | |
| C170 | supported | evidence_fit_modules.md: "They cover cryptography and introductory/network security; nothing in the practical/defensive core." | |
| C171 | overstated | evidence_fit_modules.md: "The practical and defensive core that 5-6 of 7 competitors teach is missing at EMI" | "Most competitors teach" is applied to all seven areas, but the evidence lists software security and human factors as taught by 3 of 7 and law by 4 of 7 (added with "plus"). Fix: "The practical and defensive core that 5-6 of 7 competitors teach is missing (penetration testing, digital forensics, security operations and incident response), as are software security, security management, law and human factors." |
| C172 | wrong | theme_precision.md: "TH Ingolstadt (BA Cybersicherheit; MA Cyber Security Engineer, ... 82 km), TH Deggendorf (BA and MA Cyber Security, 105 km)" | TH Ingolstadt (82 km) also has a cyber bachelor and masters and is nearer, so Deggendorf is not "the nearest competitor with both a bachelor and a master" (evidence_fit_modules.md repeats the same error). Fix: "TH Deggendorf (105 km), which offers both a cyber bachelor and a master, already teaches it..." |
| C173 | supported | evidence_fit_modules.md: "an "industrial/OT security" profile is still a differentiator against FAU, THI, THWS and HDBW, but not against TH Deggendorf" | |
| C174 | supported | evidence_fit_staff.md: "about four professors already teach security modules (information security, cryptography, network security, AI security), and four more teach the industrial/embedded side" | |
| C175 | caveat | evidence_fit_staff.md: "the 31 % coverage is an upper-end estimate (Step 41), so the new load may be somewhat higher." | The 40-50 SWS figure comes from stated assumptions (ECTS-to-SWS, lab groups, cohort 40-60) and may be too low. The claim states it as a fact. Fix: "...amounts to an estimated new teaching load of about 40-50 SWS a year (stated assumptions; possibly higher)." |
| C176 | supported | evidence_fit_staff.md: "18 SWS per week per semester for a HAW professor in Bavaria (§ 4 AVBayHIG, version 13.02.2023, valid from 01.03.2026)" | |
| C177 | supported | evidence_fit_staff.md: "Estimate: 2 new professorships (one offensive security & forensics, one defensive / OT security incl. SOC)" | |
| C178 | supported | evidence_fit_staff.md: "plus one lab engineer and teaching assignments for law and governance." | |
| C179 | supported | evidence_fit_staff.md: "an isolated security lab / cyber range for pentesting, forensics and SOC exercises" | |
| C180 | supported | evidence_fit_staff.md: "Cost is not estimated here." | |
| C181 | supported | evidence_fit_staff.md: "0.7-0.9 professorship, largely the same profile as the second bachelor professorship." | |
| C182 | supported | evidence_benchmarks.md: "Format (verified): 7 semesters, 210 ECTS, 6 theoretical semesters + 1 practical semester (semester 5), as in Bavarian HAW bachelors" | |
| C183 | supported | evidence_benchmarks.md: "Theoretische Informatik, Software Engineering 1, Informationssicherheit / reuse EMI module (12 x 5)" | |
| C184 | supported | evidence_benchmarks.md: "Secure Coding; System- und Betriebssystemsicherheit (Härtung); Penetration Testing & Ethical Hacking; Digitale Forensik / new (4 x 5)" | |
| C185 | supported | evidence_benchmarks.md: "Practical semester (Praxisphase + Praxisseminar; OTH programmes book 22 ECTS for these, the rest per SPO) / reuse format" | |
| C186 | overstated | evidence_benchmarks.md: "SOC & Incident Response; Malware & Angriffstechniken; OT-/Industrial Security; Security Architecture & Cloud Security; Security Lab Project / new (5 x 5)" | Only 25 of the 60 ECTS in semesters 6-7 are new modules. The other 35 are an adapted module (5), EMI electives (15) and the thesis (15), so "mostly new" is wrong for the block. Fix: "about 40 % new (five new modules, 25 ECTS); one adapted module, EMI electives and thesis". |
| C187 | supported | evidence_benchmarks.md: "Reused or adapted EMI modules: 110 ECTS, plus practical semester and thesis formats (45 ECTS)." | |
| C188 | supported | evidence_benchmarks.md: "Security-specific ECTS: 75 (36 %): between the Bavarian competitors (30-31 %) and St. Pölten (50 %)." | |
| C189 | supported | evidence_benchmarks.md: "44 SWS/year = 1.2 professorships nominal (18 SWS/semester, § 4 AVBayHIG) or 1.5 effective -> consistent with Step 44" | |
| C190 | supported | evidence_fit_staff.md: "That is a feasibility cost to be priced into the feasibility gate and the MCDA, not a kill reason in itself." | |
| C191 | supported | evidence_fit_staff.md: "The practical security core is missing and needs about 2 new professorships + 1 lab engineer + a security lab." | |
| C192 | caveat | decision_log.md: "Agreement between the methods is 74 %, below the 80 % target set for this step." | "Validated against a hand check" leaves out that the embedding model was wrong in 4 of 20 pairs, all in the direction of overestimating coverage, and that the method-agreement target was missed. Fix: "strong for the module comparison (hand check: embedding model right in 16 of 20 pairs, all errors overestimate coverage; the two methods agree on 74 %)". |
| C193 | caveat | evidence_outlet_jobs.md: "Counts are indicators, not vacancies by occupation." | The evidence is job-ad counts, not graduate outcomes, and the immediate region is thin (8 "Cyber Security" ads within 50 km). Fix: "Claim: there is substantial job demand for cybersecurity graduates in Germany and within 100 km of Amberg." |
| C194 | supported | evidence_outlet_jobs.md: "Source: BA Jobsuche API (/pc/v6/jobs), job offers only (angebotsart 1), total matches per keyword and region" | |
| C195 | supported | evidence_outlet_jobs.md: "Cybersecurity / Cyber Security / 851 / 263 / 191 / 8 / 30.9 %" | |
| C196 | supported | evidence_outlet_jobs.md: "Cybersecurity / OT Security / 153 / 53 / 34 / 9 / 34.6 %" | |
| C197 | supported | evidence_outlet_jobs.md: "Comparison / Robotik / 944 / 287 / 161 / 58 / 30.4 %" | |
| C198 | supported | evidence_outlet_jobs.md: "each match about as many ads as "Künstliche Intelligenz" (945) and far more than "Data Scientist" (304)" | |
| C199 | overstated | evidence_outlet_jobs.md: "Cybersecurity / IT-Sicherheit / 6,191 / 1,352 / 831 / 111 / 21.8 %" | Only the two English keywords are above the 22-25 % baseline. "IT-Sicherheit" (21.8 %), "Informationssicherheit" (20.8 %) and "Security Engineer" (24.9 %) are at or below it, so "over-represented in security" generalises too far. Fix: "Bavaria is over-represented for the keywords "Cyber Security" (30.9 %) and especially "OT Security" (34.6 %), against 22-25 % for general IT keywords; the German security keywords are at baseline." |
| C200 | supported | evidence_outlet_jobs.md: "Within 50 km of Amberg there are only 8 "Cyber Security" ads, but 191 within 100 km (Nuremberg and Regensburg fall inside)." | |
| C201 | supported | evidence_outlet_jobs.md: "Graduates would mostly work in the wider region, which is normal for a HAW in a small city." | |
| C202 | supported | evidence_outlet_jobs.md: "Changes from 15 to 17 Oct are small for every keyword and region (median absolute change 1.4 %" | |
| C203 | supported | decision_log.md: "IT occupations in Bavaria +23.8 % (2019-2023), with academic degree +34.3 % (academic share 48.5 % -> 52.6 %)" | |
| C204 | supported | evidence_outlet_jobs.md: ""Berufe in der Informatik" (KldB 4310) are again a shortage occupation in 2025 (score 2.0)" | |
| C205 | supported | evidence_outlet_jobs.md: "for a master the shortage argument is weaker and must rest on the security specialisation and industry demand (job ads), not on the shortage list." | |
| C206 | supported | configs/scores.yaml: "Mechatronik/Automatisierung (261) is not named, so its status is unknown; strongest local signal of all keywords (58 ads within 50 km)" | |
| C207 | caveat | evidence_outlet_jobs.md: "The shortage analysis is Germany-wide and by occupation group; it says nothing about IT security specifically or about Bavaria." | The shortage evidence is for computer science in general, Germany-wide, not for security. "Bavarian-heavy" holds only for the English keywords (see C199). Fix: "Claim D holds for a cyber bachelor: security keywords match many ads, "Cyber Security" and "OT Security" ads are over-represented in Bavaria, and computer science (not security specifically) is a German shortage occupation at bachelor level." |
| C208 | caveat | evidence_outlet_jobs.md: "the BA occupation-by-county tables are only behind download forms that robots.txt disallows (skipped by decision)" | County-level data exist. They were skipped under the team's robots.txt rule, and one county table could not be parsed. "Were available" suggests the data do not exist. Fix: "...and no county-level occupation data could be used (behind download forms disallowed by robots.txt; one county table could not be parsed)." |
| C209 | n/a | | Framing statement (definition of incrementality). |
| C210 | n/a | | Describes report structure. |
| C211 | n/a | | Definition. |
| C212 | n/a | | Definition. |
| C213 | n/a | | Definition (matches evidence_cannibalisation.md (c)). |
| C214 | supported | evidence_cannibalisation.md: "is run without and with the new OTH programme." | |
| C215 | supported | evidence_cannibalisation.md: "Under Huff, a new programme draws from every alternative in proportion to its baseline share" | |
| C216 | supported | evidence_cannibalisation.md: "including OTH's own Industrie-4.0-Informatik and Medieninformatik, at weight w = 0.5 or 1." | |
| C217 | caveat | evidence_ranking.md: "Robotics+AI B.Sc. / none verified; assumed comparator intake 20-60, range over all model variants" | The model was the same, but the anchoring was not. Robotics has no anchor (an assumed intake of 20-60), and the master has one anchor with a borrowed spread. Fix: "The same model was run for the other two options, with the anchors available for each (one capacity for the master, an assumed comparator intake for robotics)." |
| C218 | supported | evidence_cannibalisation.md: "Low / 21 / 5.7 / 15.3 / 2.8" | |
| C219 | supported | evidence_cannibalisation.md: "Central / 39 / 7.0 / 32.0 / 6.1" | |
| C220 | supported | evidence_cannibalisation.md: "High / 75 / 10.6 / 64.4 / 11.5" | |
| C221 | supported | evidence_cannibalisation.md: "Most students would be new to OTH: 73-86 % (central 82 %) come from other universities" | |
| C222 | supported | evidence_cannibalisation.md: "Cannibalisation is limited (14-27 %) and concentrated on Industrie-4.0-Informatik and Medieninformatik" | |
| C223 | supported | evidence_cannibalisation.md: "(13-16 %; central 6 per year) would come from OTH's own region and otherwise study in Ingolstadt, Deggendorf, Würzburg, Neu-Ulm or Munich" | |
| C224 | supported | evidence_cannibalisation.md: "students who would otherwise take OTH's KI or E&IT bachelor without a security focus are not in (a)." | |
| C225 | supported | evidence_cannibalisation.md: "If true cannibalisation were 50 % (about twice the model's maximum), net new first-years would be 10.5 / 19.5 / 37.5." | |
| C226 | supported | evidence_cannibalisation.md: "drop a candidate if more than 50 % of its core modules already appear in one OTH programme at the same level." | |
| C227 | supported | evidence_cannibalisation.md: "kill_rules.md contains no separate cannibalisation threshold; we do not add one after scoring has started." | |
| C228 | caveat | evidence_ranking.md: "Demand = 0.5 x capture score (from net new first-years) + 0.5 x trend score" | Only the model half of the demand score uses net-new students. The trend half does not, so cannibalisation affects about 0.15 of the total weight, not the whole demand criterion. Fix: "Cannibalisation instead enters the ranking through the model half of the demand criterion, which counts only students new to OTH." |
| C229 | supported | evidence_cannibalisation.md: "Both are far below 50 %: kill rule 1 is passed" | |
| C230 | supported | evidence_ranking.md: "21 / 39 / 75 / 14-27 % (Industrie-4.0-Informatik, Medieninformatik) / 15 / 32 / 64 / 2.8 / 6.1 / 11.5" | |
| C231 | supported | evidence_ranking.md: "23 / 43 / 81 / 22-37 % ... 14 / 32 / 63 / 0.7 / 2.2 / 5.5" | |
| C232 | supported | evidence_ranking.md: "15 / 29 / 55 / 14-29 % ... 11 / 24 / 48 / 4.1 / 8.5 / 15.6" | |
| C233 | unsupported | evidence_ranking.md: "Master origins are Bavarian state HAWs weighted by their students (Tabelle 5), not school leavers; university graduates are not included." | The numbers and the two source programmes are supported. No evidence doc gives the causal explanation ("because ... OTH's own graduates would mostly stay anyway"). I searched evidence_ranking.md, evidence_cannibalisation.md, reports/options.md and decision_log.md. Fix: drop the "because" clause, or label it as an interpretation ("presumably because...") and note that master origins are HAW students by region, not graduates. |
| C234 | supported | evidence_ranking.md: "THI Cloud Applications und Security Engineering capacity 30; no second anchor (high = low x B.Sc. spread, assumption)" | |
| C235 | supported | decision_log.md: "robotics has no verified public intake figure (THI Robotik handbook host does not resolve / 404, TH Augsburg 404, Kempten no figure; no workaround)" | |
| C236 | supported | configs/scores.yaml: "Huff (IIA) splits by baseline share and therefore understates substitution between near-identical programmes." | |
| C237 | supported | evidence_ranking.md: "net new first-years 7.5 / 14.3 / 27.6 (half of the gross 14.9 / 28.7 / 55.3), below the assumed minimum cohort of 20" | |
| C238 | supported | evidence_cannibalisation.md: "about one in seven students (13-16 %; central 6 per year) would come from OTH's own region" | |
| C239 | overstated | overlap_test.md: "It passes the rule as written, but the cannibalisation risk is high." | The evidence says "high", not "highest". In the model the master draws the most from OTH (22-37 % vs robotics 14-29 %), so robotics' risk rests on the 50 % overlap argument. Fix: "Robotics carries a high cannibalisation risk that the model does not capture (50 % core overlap with the KI B.Sc.); in the model itself the master draws most from OTH." |
| C240 | supported | evidence_cannibalisation.md: "Fixed demand: the model does not create students who would not have studied at all, and it ignores students from outside Bavaria" | |
| C241 | supported | evidence_funnel.md: "14 Oct 2026, 16:35 / cab5148 / MCDA criteria and weights (configs/analysis.yaml); unchanged since" | |
| C242 | supported | configs/scores.yaml: "Each score has low / central / high; the Monte Carlo samples triangular(low, central, high)." | |
| C243 | overstated | configs/scores.yaml: "trend: {low: 3, central: 4, high: 5, strength: strong," | Student demand is only half computed. Its trend half is a hand-set low/central/high score, so the criterion is not "computed from the model, not set by hand". Fix: "Regional contribution and the model half of student demand are computed from the model, not set by hand:" |
| C244 | supported | evidence_ranking.md: "Demand = 0.5 x capture score (from net new first-years) + 0.5 x trend score" | |
| C245 | caveat | configs/scores.yaml: "-> 1 + 4 ln(n/10) / ln 8, clipped to 1-5 (10 net new/yr = 1, i.e. below the assumed minimum" | The score is 1 only at 10 or fewer net-new students (half the minimum cohort of 20). Between 10 and 20 it rises to about 2.3. "1 below the assumed minimum cohort" reads as "1 for anything below 20". Fix: "...from 1 at 10 net new first-years (half the assumed minimum cohort) to 5 at 80 or more." |
| C246 | supported | configs/scores.yaml: "computed: students kept in the region per year c (Step 48 (c)) -> 1 + 4 ln(max(c,1)) / ln 16" | |
| C247 | supported | decision_log.md: "Score sheet configs/scores.yaml proposed by Claude, reviewed by Soma, who changed: robotics fit and feasibility to 2/3/5 and added the rule" | |
| C248 | caveat | kill_rules.md: "(amended 18 Oct 2026: a skewed range such as 2 / 3 / 5 raises the mean and so the centre in effect)" | The team's first change was the skewed 2/3/5. "Symmetrically" was added on 18 Oct, after a first ranking had been computed on 17 Oct (cyber 87.8 %). The claim presents both as one rule set before scoring. Fix: add "(the symmetry requirement was added on 18 Oct after a first ranking run with a skewed 2/3/5 range; that run is kept as a sensitivity)". |
| C249 | supported | evidence_ranking.md: "Cyber B.Sc. / 3.62 / 4.0 / 3 / 3 / 3 / 3.61 / 3.42" | |
| C250 | supported | evidence_ranking.md: "Feasibility gate (kill rule 2): no option has a rating of 1." | |
| C251 | n/a | | Statement about what a point estimate is (methodological, true by definition). |
| C252 | supported | evidence_ranking.md: "One common capture-model draw per iteration for all options (shared anchor uncertainty); all other scores and the weights drawn independently." | |
| C253 | supported | evidence_funnel.md: "Cyber/OT M.Sc. (P(rank 1) 6.0 %), Robotics+AI B.Sc. (2.3 %) / 1: Cybersecurity B.Sc. (91.7 %)" | |
| C254 | supported | evidence_ranking.md: "Cyber/OT M.Sc. / 6.0 % / 67.0 % / 27.0 % / 3.14 (2.89-3.39) / 6.3 % / 82.8 % / 10.9 %" | |
| C255 | caveat | evidence_ranking.md: "above the 80 % robustness bar," | The 80 % bar appears only next to the results. It is not in kill_rules.md, decision_log.md, the Step 49 plan or analysis.yaml, so nothing shows it was set before the run. Fix: "...above an 80 % bar that we use for a robust winner (not fixed before the run)", or log when it was set. |
| C256 | supported | evidence_ranking.md: "Robotics+AI B.Sc. / 2.3 % / 25.6 % / 72.2 %" | |
| C257 | supported | evidence_ranking.md: "and it stays first whichever single criterion is left out." | |
| C258 | supported | decision_log.md: "first in every leave-one-criterion-out run (lowest without demand 67.2 %, without labour 77.8 %)" | |
| C259 | wrong | evidence_ranking.md: "Cyber B.Sc. / medium / strong / medium / strong / medium / strong / medium" | The evidence-strength matrix rates the cyber bachelor's labour evidence medium, below fit and differentiation (strong). The doc only says demand is where cyber evidence is best. Fix: "its lead rests mostly on demand and labour relevance; demand is also where its evidence is best compared with the other options." |
| C260 | supported | evidence_ranking.md: "Independent capture draws (no common factor): 87.0 % / 10.0 % / 3.0 %. The common factor removes noise, it does not create the lead." | |
| C261 | supported | evidence_ranking.md: "Robotics fit and feasibility 2 / 3 / 5 (skewed first draft, mean 3.33): 87.8 % / 5.3 % / 6.9 %" | |
| C262 | supported | evidence_ranking.md: "Cyber B.Sc. / medium / strong / medium / strong / medium / strong / medium" | |
| C263 | supported | evidence_ranking.md: "Cyber/OT M.Sc. / weak / strong / medium / medium / medium / strong / weak" | |
| C264 | supported | evidence_ranking.md: "Robotics+AI B.Sc. / weak / medium / medium / weak / weak / medium / medium" | |
| C265 | supported | evidence_ranking.md: "where an option had no public intake anchor (robotics) or only one (master), this is stated and its range is widened" | |
| C266 | supported | evidence_ranking.md: "The Cybersecurity B.Sc. ranks first in 92 % of draws (93 % if robotics cannibalises 50 %), above the 80 %" | |
| C267 | overstated | evidence_ranking.md: "robotics then wins first place slightly more often than the master, but the master keeps the higher median (3.14 vs 3.10)." | The master is second in only 67 % of base draws (27 % third), 52 % with the skewed robotics range, and the 17 Oct log called second place "open". "Clear" is too strong. Fix: "The master is more likely second (67 % of draws; 83 % if robotics cannibalises 50 %), but this order is less robust than first place." |
| C268 | supported | evidence_ranking.md: "Capture ranges rest on capacities and one anecdote, not measured intakes; real intakes of THI/Deggendorf programmes would narrow every demand range." | |
| C269 | supported | evidence_capture.md: "give first-years and students per institution and campus, not per programme or subject" | |
| C270 | n/a | | Describes report structure; the ordering is a team judgement. |
| C271 | overstated | evidence_capture.md: "HNU Neu-Ulm Angewandte Cyber Security / HNU pages / admission-free; no intake figure published / not usable" | Only a few programmes were checked (THI, TH Deggendorf, HNU, OTH), so "no university publishes" is a generalisation. Fix: "None of the comparable programmes we checked publishes first-year numbers, official statistics give them only per institution, and we had no OTH admission data." |
| C272 | supported | evidence_capture.md: "The anchors are a planned capacity (THI) and an anecdote (Deggendorf), not measured intakes." | |
| C273 | caveat | evidence_cannibalisation.md: "The low case is below the assumed minimum cohort of 20 (Step 47) even before the stress test" | "At the edge of viability" holds for gross intake (21). In net-new terms the low case (15.3) is already below the minimum cohort. Fix: "...the low case is at the edge of viability (21 first-years) and below the minimum cohort in students new to OTH (15.3)." |
| C274 | supported | decision_log.md: "Destatis has no separate subject for cybersecurity, so demand and outlet need independent signals" | |
| C275 | supported | evidence_demand_trends.md: "Cyber security is the largest specialist term, but its rise was 2018-2022; since 2022 it is a plateau." | |
| C276 | supported | evidence_capture.md: "Only Bavarian counties are modelled; students from Saxony/Thuringia and from outside the region add to OTH's intake." | |
| C277 | supported | evidence_ranking.md: "Robotics has the thinnest evidence: no intake anchor, fit and feasibility from a title-level overlap check only" | |
| C278 | supported | evidence_ranking.md: "where an option had no public intake anchor (robotics) or only one (master), this is stated and its range is widened" | |
| C279 | supported | kill_rules.md: "Anchors for the other criteria were written in Step 49 (configs/scores.yaml), after the evidence was collected but before the ranking was computed." | |
| C280 | supported | evidence_fit_modules.md: "Module handbook texts describe intentions, not actual teaching" | |
| C281 | supported | evidence_fit_modules.md: "EMI side incomplete: the E&IT handbook covers only its first study section; SPO 222B still missing." | |
| C282 | supported | evidence_fit_staff.md: "research areas of individual professors were not read (person pages skipped), so existing research capacity may be underestimated." | |
| C283 | caveat | evidence_outlet_jobs.md: "the BA occupation-by-county tables are only behind download forms that robots.txt disallows (skipped by decision)" | Same as C208. The data exist but were skipped under the team's robots.txt rule, and one table could not be parsed. Fix: "...no county-level occupation data could be used (download forms disallowed by robots.txt; one county table not parseable)." |
| C284 | supported | decision_log.md: "Decision: leave Step 42 as it is (PDF reports B I/II 1 j; 2018/19 stays a gap year)." | |
| C285 | supported | decision_log.md: "Anything blocked or not found is not worked around but listed in docs/manual_downloads.md for manual download." | |
| C286 | supported | evidence_funnel.md: "the catalogue's 13 study fields; themes outside these fields were not screened." | |
| C287 | overstated | evidence_ranking.md: "Without demand its first-place probability falls to 67 % (robotics 31 %, helped by regional contribution and local jobs)" | "None" is absolute. The cyber lead rests most on demand, whose proxies are listed as limitation 2, and it ties robotics on fit and differentiation, where its evidence is strongest (its labour evidence is medium). Fix: "In our sensitivity runs no single limitation changes the winner (lowest first-place share 67.2 % without demand), and the weakest evidence concerns the options that rank behind it." |
| C288 | supported | evidence_capture.md: "The best way to narrow the range is a direct question to THI and TH Deggendorf (or the state office)" | |
| C289 | overstated | configs/scores.yaml: "no staffing or lab estimate made (Step 44 covered cyber only)" | The four claims were tested in full only for the cyber bachelor, so it is not shown to be "the only option for which all four claims hold". The security core is "costed" only in staff, not lab cost. Fix: "It is the only shortlisted option tested in full against all four claims, and they hold: ... EMI can carry the foundations and needs an estimated security core (two professorships, a lab engineer, a lab whose cost is open)..." |
| C290 | supported | evidence_funnel.md: "1: Cybersecurity B.Sc. (91.7 %)" | |
| C291 | supported | decision_log.md: "OTH Cyber B.Sc. steady state: low 21, central 39, high 75 first-years (year 1: 12 / 24 / 45)." | |
| C292 | supported | evidence_fit_staff.md: "Estimate: 2 new professorships (one offensive security & forensics, one defensive / OT security incl. SOC), plus one lab engineer" | |
| C293 | supported | evidence_demand_trends.md: "Programme naming should use the English term (or both spellings)." | |
| C294 | supported | evidence_fit_modules.md: "an OT/industrial profile differentiates against most competitors, not against TH Deggendorf." | |
| C295 | supported | evidence_capture.md: "A first intake should not be planned for 2025 (G9 gap, Step 42); from 2026 the Bavarian Abitur cohort recovers" | |
| C296 | supported | evidence_capture.md: "for their actual cyber first-year numbers; one figure would cut the range by about half." | |
| C297 | supported | evidence_capture.md: "OTH would draw 0.65-0.86 times THI's intake and 1.20-1.28 times TH Deggendorf's" | |
| C298 | supported | evidence_ranking.md: "Second place is the master (67 % rank 2; 83 % with realistic robotics cannibalisation)." | |
| C299 | supported | evidence_fit_staff.md: "With the master, the second professorship carries the OT specialisation." | Labelled in the report as team judgement (proposal). |
| C300 | supported | evidence_fit_staff.md: "With the master, the second professorship carries the OT specialisation." | |
| C301 | supported | overlap_test.md: "Robotics + AI, bachelor / Künstliche Intelligenz (B.Sc.) / 4 of 8 / 50 % / passes at the threshold" | |
| C302 | supported | overlap_test.md: "Better framed as a strengthened specialisation than a new programme; kept on the list only as the comparison case." | Labelled in the report as team judgement. |
| C303 | supported | configs/sources.yaml: "snapshots 15 and 17 Oct 2026, next 1 Nov, 15 Nov, 1 Dec" | |
| C304 | n/a | | Monitoring recommendation, not a factual claim. |
| C305 | overstated | evidence_capture.md: "TH Deggendorf Cyber Security / one student review (studycheck.de) / "etwa 60 Studienanfänger"" | I searched configs/sources.yaml: it has no entry for the studycheck.de review or for the EMI module handbooks (references.yaml: "local copies in data/raw/oth modules"), and the HRK Hochschulkompass entry is still "todo". So the register does not hold "all sources used". Fix: "The data sources used in this report, as registered in configs/sources.yaml (the EMI module handbooks and the TH Deggendorf student review are cited separately)", or add them to the register. |
| C306 | wrong | studiensuche_manifest.json: ""status": "cached", "pages": 37, "items": 724, "retrieved_utc": "2026-10-14T20:04:54+00:00"" | Two of the three manifests cited as examples do not record what the sentence says. studiensuche_manifest.json has no URL or SHA-256 field, and genesis_manifest.json has no URL field. Fix: "Downloads are recorded with date and, for downloaded files, URL and SHA-256 in the manifests in docs/ (for example docs/competitor_modules_manifest.json, docs/regional_manifest.json)." |
| C307 | supported | configs/sources.yaml: "THI Robotik (host does not resolve, www path 404) and TH Augsburg (404) not obtained, no workaround" | |
| C308 | caveat | decision_log.md: "No automated access to hochschulkompass.de search pages (blocked by its robots.txt)." | Two documented substitutions are left out: the Hochschulkompass data were obtained through the BA Studiensuche API, and TH Mannheim's module tables came from its programme page after the handbook was robots-blocked. manual_downloads.md also allows manual browser downloads where robots.txt blocks crawlers. Fix: "No blocked or login-protected source was circumvented; where a page was blocked we used only another permitted route (Hochschulkompass data via the BA Studiensuche API, TH Mannheim's programme page)." |
| C309 | overstated | decision_log.md: "Evidence: docs/overlap_test.md, configs/overlap_test.yaml." | Several entries have no reason (e.g. 15 Oct kill rule 1, Steps 39-44). The 14 Oct criteria-and-weights decision and the 80 % robustness bar are not in the log at all (searched decision_log.md). Fix: "Method decisions are logged with date and decider, most with a reason, in decision_log.md; the 14 Oct rules are documented in evidence_funnel.md." |
| C310 | n/a | | Describes report structure. |
| C311 | supported | decision_log.md: "Decision: publicly available sources only. No primary survey and no internal OTH data." | |
| C312 | supported | evidence_funnel.md: "14 Oct 2026, 16:35 / cab5148 / MCDA criteria and weights (configs/analysis.yaml); unchanged since" | True, but documented in evidence_funnel.md (git history), not in decision_log.md (see C309). |
| C313 | supported | decision_log.md: "Keep cybersecurity bachelor and master; keep robotics + AI bachelor as comparison case (50 %, at threshold)." | |
| C314 | supported | decision_log.md: "all 70 programmes whose title matches the cybersecurity rule (census instead of a sample, so the competitor count becomes exact)" | |
| C315 | supported | decision_log.md: "e5 is the headline because it is better validated by hand; TF-IDF (47 % / 45 %) is reported as a sensitivity range." | |
| C316 | supported | decision_log.md: "Not used: Regionaldatenbank (robots.txt "Disallow: /", all automated access) and the GENESIS-Online Bayern API" | |
| C317 | caveat | decision_log.md: "Skip the BA occupation-by-county tables (only behind /SiteGlobals/ download forms, disallowed by robots.txt" | Keeping the step lean was the team's choice (Soma). The county data exist but were skipped under the robots.txt rule, and one table failed to parse. "Not available" hides this. Fix: "county-level occupation data skipped (robots.txt-disallowed download forms) or not parseable". |
| C318 | supported | decision_log.md: "docs/evidence_fit_staff.md uses neutral labels (Prof. A-N with their area) and module titles, keeping the evidence" | |
| C319 | supported | decision_log.md: "trained to 2024 (2025 = Bavarian G9 transition)" | |
| C320 | caveat | decision_log.md: "anchored on real intakes: THI capacity 25 (official, likely >= intake; low) and TH Deggendorf ~60 (one student review, weak; high)" | The anchors are a planned capacity and an anecdote from a student review, not "public intake figures". Fix: "...anchored on a public capacity (TH Ingolstadt, 25) and an anecdotal intake (TH Deggendorf, ~60)". |
| C321 | supported | decision_log.md: "kill_rules.md has no cannibalisation threshold and none is added after scoring started" | |
| C322 | supported | decision_log.md: "Against evidence asymmetry (Soma), the Step 47/48 capture + cannibalisation model is run unchanged for the Robotics+AI B.Sc. and the Cyber/OT M.Sc." | |
| C323 | supported | decision_log.md: "robotics institutional fit and feasibility 1.5 / 3 / 4.5 instead of 2 / 3 / 5, so the range follows the rule" | |
| C324 | supported | decision_log.md: "one common capture-model draw per iteration for all options (Soma: shared anchor error must not flip the ranking at random)" | |
| C325 | overstated | decision_log.md: "a typed number (percentages, decimals, thousands separators, integers >= 10 outside allowed patterns)" | The build rule exempts small integers and allowed patterns, and the report text types numbers such as "150 km", "210 ECTS", "2 / 3 / 5" and "4 December". So not "every report number" comes from the key-numbers file. Fix: "Every key number (percentages, decimals, larger counts) generated from a key-numbers file and checked against its evidence document". |
| C326 | supported | kill_rules.md: "Written before any candidate is scored. Set by the team on 14 Oct 2026." | |
| C327 | supported | kill_rules.md: "A candidate is dropped if any rule applies." | |
| C328 | supported | kill_rules.md: "Overlap: more than 50 % of its core modules already appear in one OTH programme at the same level, and no credible differentiator remains." | |
| C329 | supported | kill_rules.md: "Feasibility: its feasibility rating is 1 (no staff, no lab, no accreditation path)." | |
| C330 | supported | kill_rules.md: "Trend: entrants in the related field across Germany fell in each of the last five years, and the KMK scenario shows no recovery." | |
| C331 | supported | kill_rules.md: "Pipeline (master only): bachelor graduates in related fields across Germany are falling, and too few are in the region to fill a cohort" | |
| C332 | supported | kill_rules.md: "Scope: at most three candidates per level, six in total, go into full dossiers." | |
| C333 | supported | kill_rules.md: "Rule added 17 Oct 2026 (Step 49, Soma): weak evidence widens a score's range, it does not raise its centre." | |
| C334 | caveat | kill_rules.md: "(amended 18 Oct 2026: a skewed range such as 2 / 3 / 5 raises the mean and so the centre in effect)" | The rule added on 17 Oct did not say "symmetrically". That wording is an 18 Oct amendment, made after a first ranking run had been computed (decision_log.md, 17 Oct: cyber 87.8 %). The heading "before the ranking" does not hold for it. Fix: add "(symmetry requirement amended 18 Oct, after a first ranking run; the earlier skewed range is reported as a sensitivity)". |
| C335 | n/a | | Table heading. |
| C336 | supported | kill_rules.md: "5: related-field entrants across Germany rose over five years, and the regional catchment supports a cohort" | |
| C337 | supported | configs/scores.yaml: "5 = shortage occupation at the matching level AND Bavarian job-ad share above the IT" | |
| C338 | supported | configs/scores.yaml: "5 = EMI already teaches >70 % of the programme's specific core and has the staff;" | |
| C339 | supported | configs/scores.yaml: "5 = no new professorship or lab; 3 = 1-2 new professorships and one new lab;" | |
| C340 | supported | configs/scores.yaml: "5 = no dedicated programme within 150 km; 3 = 3-5 within 150 km but none within 80 km" | |
| C341 | supported | configs/scores.yaml: "computed: students kept in the region per year c (Step 48 (c))" | |
| C342 | supported | configs/scores.yaml: "0.5 x capture score + 0.5 x trend score." | |
| C343 | supported | configs/scores.yaml: "AND >150 ads within 100 km; 3 = two of these; 1 = none." | |
| C344 | supported | configs/scores.yaml: "Proposed by Claude, reviewed by Soma, who changed robotics fit," | |

## Summary

187 claims reviewed (C158-C344).

| Verdict | Count |
|---|---|
| supported | 144 |
| caveat | 17 |
| overstated | 12 |
| unsupported | 1 |
| wrong | 3 |
| n/a | 10 |

Non-supported claims:

- C158 (caveat): the "costed gap" is costed only in staff; the security-lab cost is not estimated.
- C171 (overstated): "most competitors teach" also covers software security, human factors (3 of 7) and law (4 of 7).
- C172 (wrong): TH Ingolstadt (82 km, cyber BA and MAs) is nearer than Deggendorf, so Deggendorf is not "the nearest competitor with both a bachelor and a master".
- C175 (caveat): the 40-50 SWS load is an assumption-based estimate that may be higher; it is stated as a fact.
- C186 (overstated): semesters 6-7 are "mostly new", but only 25 of 60 ECTS are new modules.
- C192 (caveat): "validated against a hand check" leaves out 4 of 20 errors (all overestimates) and the missed 74 % agreement target.
- C193 (caveat): the claim is about graduates finding jobs, but the evidence is job-ad counts, and the 50 km market is thin.
- C199 (overstated): Bavaria is over-represented only for "Cyber Security" and "OT Security"; three other security keywords are at or below baseline.
- C207 (caveat): the shortage evidence is Germany-wide and not security-specific, and "Bavarian-heavy" holds only for the English keywords.
- C208 (caveat): county-level data were skipped under the robots.txt rule or not parseable, not "unavailable".
- C217 (caveat): the anchoring logic differs by option (robotics uses an assumed intake, the master one anchor).
- C228 (caveat): only the model half of the demand score counts net-new students.
- C233 (unsupported): no evidence doc gives the causal explanation for the master's low regional effect.
- C239 (overstated): the evidence calls robotics' risk "high", not "highest"; in the model the master draws most from OTH.
- C243 (overstated): student demand is half hand-scored (trend), so it is not "computed, not set by hand".
- C245 (caveat): the score is 1 only at 10 or fewer net-new students, not for anything below the minimum cohort of 20.
- C248 (caveat): the "symmetric" rule was amended on 18 Oct, after a first ranking run with a skewed range.
- C255 (caveat): no document shows the 80 % robustness bar was set before the results.
- C259 (wrong): the cyber bachelor's labour evidence is rated medium, not among its strongest.
- C267 (overstated): the order of second and third place is not "clear" (master second in 67 % of draws, 52 % with the skewed range).
- C271 (overstated): "no university publishes" generalises from the few programmes that were checked.
- C273 (caveat): in net-new terms the low case (15.3) is already below the minimum cohort.
- C283 (caveat): same as C208.
- C287 (overstated): "none points towards a different winner" is absolute, and "leads on the criteria with the strongest evidence" contradicts the matrix.
- C289 (overstated): "the only option for which all four claims hold", although the other options were not tested on all four; "costed" although the lab cost is open.
- C305 (overstated): sources.yaml lacks the EMI module handbooks and the studycheck.de review, so it is not "all sources used".
- C306 (wrong): studiensuche_manifest.json has no URL or SHA-256, and genesis_manifest.json has no URL.
- C308 (caveat): two substitutions are left out (Hochschulkompass data via the BA API, TH Mannheim's programme page), and a manual-download policy exists for robots-blocked files.
- C309 (overstated): several log entries have no reason, and the weights decision and the 80 % bar are not logged.
- C317 (caveat): the lean step was a choice; the county data exist but were skipped or failed to parse.
- C320 (caveat): the anchors are a capacity and an anecdote, not "public intake figures".
- C325 (overstated): small integers and allowed patterns are typed in the text, so not "every report number" comes from the key-numbers file.
- C334 (caveat): the "symmetrically" wording was added on 18 Oct, after a first ranking run.
