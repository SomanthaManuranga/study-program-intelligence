# Defence Q&A: the 25 most likely examiner questions

<!-- Source for docs/defence_qa.md. Numbers only as {{key}} placeholders (reports/key_numbers.yaml). Links are relative
to docs/ (where the rendered file lives). Answers: about 30 seconds each. -->

Short answers for the presentation. Each answer has three parts: **Answer** (what to say), **Evidence** (where it is
shown), **If pressed** (the honest limit). Numbers come from the key-numbers file, like the report.

**Rehearse these six first:** Q10 (weak anchors), Q11 (low case), Q3 (winner chosen first?), Q6 (demand is mostly
foreign students), Q19 (cannibalisation), Q25 (use of AI).

## Question and scope

### Q1. Why only public data? Why not simply ask the universities for their intake numbers?

**Answer.** Public data only was the scope of the brief and our protocol, so every data input is public (our own assumptions are
labelled as ours) and the code rebuilds all results from the downloaded data. We say openly that this is the main weakness: no comparable
programme we checked publishes its intake. Asking TH Ingolstadt and TH Deggendorf for one measured number is our first
recommendation before a decision.

**Evidence:** [research_protocol.md](research_protocol.md), report Section 9 and Section 10.

**If pressed:** one measured intake would cut the first-year range by about half
([evidence_capture.md](evidence_capture.md)); a rebuild needs the downloaded raw data plus a few manual downloads.

### Q2. Why only EMI, and why compare bachelors and masters together?

**Answer.** The brief asks which programme suits our faculty, so the candidates had to fit EMI. Bachelor and master
were analysed separately (school leavers by county for the bachelor capture, students of the Bavarian universities of
applied sciences for the master, graduate numbers for the master pipeline) and only compared at the ranking stage with
the same criteria.

**Evidence:** [research_protocol.md](research_protocol.md), [evidence_ranking.md](evidence_ranking.md).

**If pressed:** the master's demand model has one intake anchor only, so its ranking rests on weaker evidence.

## Did you choose the winner first?

### Q3. Did you pick cybersecurity first and then justify it?

**Answer.** No, and the git history shows the order. The criteria and weights were committed at 16:35 and the final
five kill rules at 17:40 on {{rules_fixed_date}}, about five hours before the first screening of all fields at 22:42.
The weights never changed. Candidates then left the funnel stage by stage: {{funnel_0_themes}}, then
{{funnel_2_candidates}}, then {{funnel_3_shortlist}} for the ranking.

**Evidence:** [evidence_funnel.md](evidence_funnel.md), report Section 2.

**If pressed:** the screening filters themselves (stages 1 and 2) were written with the screening, the scoring anchors
for criteria other than demand after the evidence was collected, and the weak-evidence rule was tightened after the
first ranking run (see [evidence_funnel.md](evidence_funnel.md), report Section 2 and
[decision_log.md](decision_log.md)). The protocol's candidate longlist was never written into the repository; the
first list of candidates is the screening itself.

### Q4. Why were automation, energy and medical technology dropped so early?

**Answer.** At the supply-gap stage we kept only themes that OTH does not already offer. OTH already has titled
programmes in all three, and energy and medtech belong mainly to other faculties. A later check wrote the two filters
out as thresholds and applied them to all {{themes_all}} themes, including data science, health informatics and energy
informatics. On the same filters no theme came out stronger than cybersecurity; the next step was judged on titles
only.

**Evidence:** [evidence_funnel.md](evidence_funnel.md), [evidence_theme_verdicts.md](evidence_theme_verdicts.md).

**If pressed:** the thresholds were written after the screening, so they explain it rather than having been fixed
before. Health/medical informatics passes both filters; its overlap with OTH's Medizintechnik was not tested.

### Q5. Robotics overlaps {{robotics_overlap}} with your KI bachelor. Why was it not dropped?

**Answer.** Kill rule 1 drops a candidate only with {{kill_rule_1_threshold}} core overlap with one OTH programme, set
before scoring. Robotics sat exactly at the threshold, so it stayed in as the comparison case and was run through the
same capture, cannibalisation and ranking models. It ranks last, and we propose it as a specialisation of the KI
bachelor instead.

**Evidence:** [overlap_test.md](overlap_test.md), [kill_rules.md](kill_rules.md).

**If pressed:** with Mechatronik und digitale Automation, OTH as a whole covers 7 of 8 robotics topics; the overlap test
matched topics on titles, and robotics' fit and feasibility rest on that title-level check only.

## Demand

### Q6. Official statistics have no cybersecurity subject. How can you say demand grows?

**Answer.** Through the field it belongs to. Informatik is the only large EMI field still growing (Bavaria
{{informatik_firstyears_by_growth}} a year, 2019-2024), though mostly through foreign students: German first-years grew
by {{informatik_by_german_growth}} a year in Bavaria. The Bavarian cyber-proxy pool (first-years in Informatik,
Technische Informatik and Computer- und Kommunikationstechniken) was {{cyber_proxy_by_2024}} in 2024 and stays above
that level in the conservative forecast. Search interest only shows that cybersecurity is the largest specialist term
we tracked, not that it grows.

**Evidence:** [evidence_competition_demand.md](evidence_competition_demand.md), [evidence_forecast.md](evidence_forecast.md),
[evidence_demand_split.md](evidence_demand_split.md).

**If pressed:** {{informatik_by_foreign_part}} of the Bavarian growth is foreign students, and in Germany German
first-years changed by {{informatik_de_german_growth}} a year. Among German first-years Informatik is the only large
EMI subject that grew in Bavaria; in Germany it is about level with Wirtschaftsinformatik. These are proxies, not cyber enrolments; we tested the split in the ranking (Q22).

### Q7. Your 2030 forecast is a "midpoint". Isn't that arbitrary?

**Answer.** Yes, it is a planning value we chose, and we say so. Drift won the backtests (MASE
{{forecast_mase_drift_by_cyber}} against {{mase_naive_by_cyber}} for naive), but it under-forecast the recent surge
and may over-extrapolate now. So we show both paths: the conservative KMK path gives {{cyber_proxy_by_2030_conservative}}
in 2030, the midpoint {{cyber_proxy_by_2030_central}}. Even the conservative path stays above the 2024 level.

**Evidence:** [evidence_forecast.md](evidence_forecast.md).

**If pressed:** the KMK index for Bavaria is {{kmk_by_2030}} in 2030, i.e. almost flat.

### Q8. Search interest in cybersecurity has been flat since 2022. Doesn't that weaken your case?

**Answer.** It means interest is high but no longer rising: {{cyber_search_2022}} in 2022 and {{cyber_search_2026}} in
2026 on the same scale. We do not use search interest as a growth argument, only to show that cybersecurity is the
largest specialist term we tracked, ahead of AI ({{search_cyber_vs_ki}}) and robotics.

**Evidence:** [evidence_demand_trends.md](evidence_demand_trends.md).

**If pressed:** search terms are a narrow proxy; people also search programme or university names.

## Capture

### Q9. How did you arrive at {{cyber_bsc_gross_low}} / {{cyber_bsc_gross_central}} / {{cyber_bsc_gross_high}} first-years?

**Answer.** A gravity model calibrated on real Bavarian student flows (distance decay {{gravity_beta}}, {{gravity_r2}})
gives OTH's intake relative to competitors: {{rel_capture_thi}} TH Ingolstadt's and {{rel_capture_deg}} TH Deggendorf's.
The low case applies the first ratio to TH Ingolstadt's planned capacity of {{thi_cyber_capacity}}, the high case the
second ratio to an anecdotal {{deg_cyber_anecdote}} at TH Deggendorf; central is the geometric mean, a choice.

**Evidence:** [evidence_capture.md](evidence_capture.md), report Section 4.

**If pressed:** the model alone could not give absolute numbers: uncalibrated it implied {{thi_implied}} first-years
for TH Ingolstadt, against a capacity of {{thi_cyber_capacity}}.

### Q10. Your anchors are a planned capacity and one student review. Why should we trust them?

**Answer.** You should treat them as the weakest part, and we do. That is why we give a range, not a point, and
recommend getting one measured intake before deciding. The model structure itself is stable: relative capture varies
little across all model variants.

**Evidence:** [evidence_capture.md](evidence_capture.md), report Section 9 (limitation 1).

**If pressed:** the high anchor comes from one review on studycheck.de; it is registered as weak evidence in
`configs/sources.yaml`. As a plausibility check, two research universities publish per-programme figures:
{{rub_cyber_ba_firstyears}} first-years at Ruhr-Uni Bochum and {{uds_cyber_ba_firstyears}} at Saarland. The Deggendorf
figure lies inside that range. None of the universities of applied sciences we searched publishes such figures; the
two that do are research universities, not peers, so this is a check, not an anchor.

### Q11. In the low case you reach only {{cyber_bsc_gross_low}} first-years. Is the programme viable?

**Answer.** In the low case it is borderline: {{cyber_bsc_gross_low}} first-years against our assumed minimum of
{{min_cohort}}, and only {{cyber_bsc_netnew_low}} of them are new to OTH. In the central and high cases the gross intake
clears the bar from the first year. That is exactly why we recommend checking real intakes of comparable programmes
first.

**Evidence:** [evidence_capture.md](evidence_capture.md), [evidence_cannibalisation.md](evidence_cannibalisation.md).

**If pressed:** the low case is not a floor: it is the median of {{low_variant_range}} across the model variants, and
TH Ingolstadt's capacity may be above its real intake; year 1 in the low case is only {{year1_low}}.

### Q12. Where does the minimum cohort of {{min_cohort}} come from?

**Answer.** It is our assumption, and labelled as one: we found no Bavarian rule or guideline. As a reference, TH
Ingolstadt plans its cyber bachelor for {{thi_cyber_capacity}} students a year.

**Evidence:** [evidence_capture.md](evidence_capture.md).

**If pressed:** a higher minimum would change the viability verdicts: at {{thi_cyber_capacity}}, even the central case
would miss it in year 1 ({{year1_central}}).

### Q13. Your gravity model under-predicts how local students are. What does that do to the result?

**Answer.** For OTH the model gives a home-region share of {{home_share_model}} against an actual {{home_share_actual}},
partly because the seven administrative regions are coarse. We use the model only for relative quantities (OTH's
intake relative to its competitors, and the cannibalisation shares), never for absolute numbers.

**Evidence:** [evidence_capture.md](evidence_capture.md), [evidence_cannibalisation.md](evidence_cannibalisation.md).

**If pressed:** the error is larger for TH Ingolstadt, so we do not know in which direction it shifts the ratio; we
have not quantified it. Students from outside Bavaria are not modelled either. Their share is measured: on the same
approximate method {{oth_outside_bavaria_approx}} of OTH's German students and {{thi_outside_bavaria_approx}} at TH
Ingolstadt; its effect on the estimate is small by reasoning, not tested.

## Fit and feasibility

### Q14. You say EMI covers {{emi_cover_sec_ba}} of the security content. How reliable is that?

**Answer.** It is an upper-end estimate. We compared every competitor module with every EMI module using multilingual
embeddings; in a hand check of twenty pairs the model was right in {{pairs_e5}}, and all its errors overestimated
coverage. A TF-IDF cross-check gives {{cover_sec_ba_tfidf}}.

**Evidence:** [evidence_fit_modules.md](evidence_fit_modules.md).

**If pressed:** the two methods agree on {{method_agreement}} of labels, below our target; module texts describe
intentions, not actual teaching.

### Q15. What would the programme cost the faculty?

**Answer.** We estimate {{new_professorships}} (offensive security and forensics; defensive and OT security), one lab
engineer, teaching assignments for law and security management, and an isolated security lab. The new teaching load is
an estimated {{new_load_sws}} a year.

**Evidence:** [evidence_fit_staff.md](evidence_fit_staff.md), [evidence_benchmarks.md](evidence_benchmarks.md).

**If pressed:** the cost of the lab is not estimated; the staffing rests on stated assumptions and leaves out extra
exercise groups and thesis supervision, so the load may be higher.

### Q16. TH Deggendorf already teaches OT security. Where is your differentiation?

**Answer.** Not in OT, and we say so: OT sets OTH apart from FAU, TH Ingolstadt, THWS and HDBW, but not from
Deggendorf. The differentiation is regional reach: OTH has its own pool of {{own_pool}} school leavers a year, and
{{catchment_closer_to_oth}} of its 100-km catchment is closer to OTH than to Deggendorf.

**Evidence:** [evidence_catchment.md](evidence_catchment.md), [evidence_fit_modules.md](evidence_fit_modules.md),
[evidence_ministry_contracts.md](evidence_ministry_contracts.md).

**If pressed:** Deggendorf is strong in security beyond teaching: its ministry contract names an IT-security transfer
centre in Vilshofen. The overlap with Nuremberg/Erlangen is large (only {{closer_than_nuernberg}} of the catchment is closer to
OTH than to that hub), and counting OTH Regensburg as a competitor the own pool is {{pool_without_regensburg}}.

## Outlet

### Q17. Job-ad counts are not jobs for graduates. Why use them?

**Answer.** They are the best public regional signal; we found no usable county-level occupation data. We use them as
indicators and back them with employment statistics: IT jobs held by graduates in Bavaria grew
{{it_jobs_by_academic_growth}} (2019-2023), and computer science is a shortage occupation at bachelor level in Germany.

**Evidence:** [evidence_outlet_jobs.md](evidence_outlet_jobs.md).

**If pressed:** ads match keywords at all qualification levels, the job board does not contain every ad, and the
shortage status is for computer science in general, not IT security specifically.

### Q18. There are only {{ads_cyber_50km}} "Cyber Security" ads within 50 km. Will graduates find jobs nearby?

**Answer.** Within 100 km, where Nuremberg and Regensburg fall inside, there are {{ads_cyber_security_amberg_100km}}.
That is normal for a university in a small town: graduates work in the wider region. Bavaria's share of "Cyber Security"
ads is {{ads_cyber_security_by_share}}, above the {{baseline_share}} of general IT keywords.

**Evidence:** [evidence_outlet_jobs.md](evidence_outlet_jobs.md).

**If pressed:** the German security keywords ("IT-Sicherheit", "Informationssicherheit") are at or below that baseline;
snapshots continue until the freeze (two days apart, the counts changed by a median of {{snapshot_change}}).

## Cannibalisation

### Q19. Won't the new programme just take students from Industrie-4.0-Informatik and Medieninformatik?

**Answer.** Some, not most. In our capture model {{cyber_bsc_from_oth_range}} of its students would come from existing
OTH programmes; net new to OTH are {{cyber_bsc_netnew_low}} / {{cyber_bsc_netnew_central}} / {{cyber_bsc_netnew_high}} a
year. Kill rule 1 is passed: {{overlap_test_cyber_ba}} of core topics already at OTH, against a threshold of
{{kill_rule_1_threshold}}.

**Evidence:** [evidence_cannibalisation.md](evidence_cannibalisation.md), [overlap_test.md](overlap_test.md).

**If pressed:** the model does not see OTH programmes without a security focus; at {{stress_share}} cannibalisation,
net new would be {{stress_netnew}}.

### Q20. Robotics has the strongest local job signal. Why does it rank last?

**Answer.** Its demand evidence is the weakest: its feeder subjects are flat or falling, its search interest is flat,
and there is no public intake anchor. It also overlaps {{robotics_overlap}} with our KI bachelor; if half its students
came from OTH programmes, only {{robotics_netnew_cannib50}} a year would be new.

**Evidence:** [evidence_ranking.md](evidence_ranking.md), [evidence_outlet_jobs.md](evidence_outlet_jobs.md).

**If pressed:** robotics' fit and feasibility come from a title-level check only; their first ranges (2 / 3 / 5) raised
the mean and were made symmetric after the first ranking run; with the first ranges the cyber bachelor still won
{{p_rank1_cyber_bsc_skew}}.

## Ranking

### Q21. Who chose the weights, and why these?

**Answer.** The team set them before any screening: {{weights}}. They are a judgement, and no reason per weight is
recorded; the logged rule was only to fix them before any candidate was seen. Because they are a judgement, we drew
{{mc_draws}} weight sets around them and also left out each criterion in turn.

**Evidence:** `configs/analysis.yaml` (values), [evidence_funnel.md](evidence_funnel.md) (timing),
[evidence_ranking.md](evidence_ranking.md) (sensitivity).

**If pressed:** demand has the largest weight, in line with the brief's question about attracting students; the
sensitivity runs show how far the result depends on the weights.

### Q22. How robust is first place?

**Answer.** The cyber bachelor ranks first in {{p_rank1_cyber_bsc_base}} of the Monte Carlo draws and, in the base
case, stays first whichever single criterion is left out; the lowest is {{loo_min_cyber_bsc}}, without demand. With independent capture
draws it is {{p1_independent}}. With demand measured on German entrants only, for all three options, it still ranks
first, but in {{p_rank1_cyber_bsc_german}} of draws, just below our bar.

**Evidence:** [evidence_ranking.md](evidence_ranking.md), report Section 8.

**If pressed:** in the first ranking run, with robotics' skewed ranges, leaving out demand put robotics narrowly
ahead (cyber bachelor and robotics: {{loo_first_run_tie}}); the {{robustness_bar}} bar was set when the results were reported, not before; and
the lead rests mostly on demand and labour relevance. With German-only demand and labour relevance also left out, the
master is narrowly ahead ({{loo_german_labour_msc}} against {{loo_german_labour_cyber}}).

### Q23. Why not start with the master?

**Answer.** The master ranks second. It faces more competition ({{cyber_ma_150km}} dedicated cyber masters within
150 km, and Deggendorf already teaches OT security in its master), draws more from OTH's own programmes
({{msc_from_oth}}) and keeps few students in the region. We propose it as a follow-on once the bachelor produces its
own graduates: a team judgement, not a model result. Taught in English, it could also reach foreign-nationality
students, {{informatik_de_foreign_share_2024}} of computer-science first-years in Germany in 2024. For the bachelor our
one data point is against English: Saarland's English-taught cyber bachelor had {{uds_cyber_en_firstyears}} first-years against
{{uds_cyber_ba_firstyears}} in the German one (winter 2025/26).

**Evidence:** [evidence_ranking.md](evidence_ranking.md), [evidence_demand_split.md](evidence_demand_split.md), report
Section 10.

**If pressed:** the master's demand model has one anchor ({{msc_anchor}} at TH Ingolstadt) and a borrowed spread. With
demand measured on German entrants the master gains ({{p_rank1_cyber_msc_german}} first places), because German
graduates in Informatik still grow ({{grads_by_german_growth}} a year in Bavaria).

## Limits and data access

### Q24. What could you not get, and did you work around any block?

**Answer.** We did not circumvent anything blocked. Missing: programme-level intakes (not published by the programmes we
checked), the federal-state regional database (robots.txt), the Bavarian GENESIS web service (login failed), OTH staff
profile pages (skipped on principle) and some competitor handbooks. Where scripts were blocked we used another
permitted route or downloaded public files by hand.

**Evidence:** report Appendix A1, [decision_log.md](decision_log.md).

**If pressed:** students from outside Bavaria are not in the catchment model; OTH's share is similar to that of the
anchor universities: close to TH Ingolstadt's ({{oth_outside_bavaria_approx}} against {{thi_outside_bavaria_approx}}) and
above TH Deggendorf's {{thd_outside_bavaria_approx}} (approximate), so the effect is small.

## Use of AI

### Q25. What did the AI do, and how do you know the numbers are right?

**Answer.** Claude Code wrote the analysis code and drafted the texts under our direction, and proposed the theme labels
and the score sheet. We chose the sources and made or approved every method decision; we reviewed all
{{labels_reviewed}} proposed theme labels, judged twenty module pairs and changed the score sheet. Every statistic in
the report (percentages, decimals and numbers of ten or more) is checked automatically to appear in its evidence
document, and independent AI reviewers checked all
{{val:review_n_claims}} statements; flagged ones were fixed and re-checked.

**Evidence:** report Section 1, [review_verdicts.md](review_verdicts.md), [decision_log.md](decision_log.md).

**If pressed:** the reviews were done by AI reviewers in a fresh context, not by people; distances, dates, times, ECTS sizes and
small counts are typed and not checked automatically; the last two fixes were checked by the drafting session only; and the protocol's
check of AI-related scores by our second team member is not recorded yet.
