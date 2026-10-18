# Summary {-}

<!-- Executive summary. All numbers are {{placeholders}} from reports/key_numbers.yaml; do not type numbers here. -->

**Question.** Which new study programme should the Faculty of Electrical Engineering, Media and Computer Science
(EMI) at OTH Amberg-Weiden offer to attract the most additional students, using public data only?

**Answer.** A **Cybersecurity B.Sc.** It ranks first of three shortlisted options in {{p_rank1_cyber_bsc_base}} of
{{mc_draws}} Monte Carlo draws of the weights and scores, and in {{p_rank1_cyber_bsc_rob50}} when robotics is given a
more realistic cannibalisation share. The runner-up is a Cybersecurity M.Sc. with an industrial (OT) profile
({{p_rank1_cyber_msc_base}}); Robotics + AI B.Sc. comes last ({{p_rank1_robotics_bsc_base}}).

**The winner was not chosen first.** The criteria, weights and final kill rules were committed on
{{rules_fixed_date}}, before the first screening. Starting from {{funnel_0_themes}} related to EMI, a demand-trend
filter, a supply-gap filter and kill rule 1 (overlap with existing OTH programmes) left {{funnel_3_shortlist}}
candidates; only then were they modelled and ranked (Section 2).

**Why cybersecurity: four claims.**

- **A. Demand grows, mostly through foreign students.** Computer science is the only large EMI field still growing
  (Bavaria {{informatik_firstyears_by_growth}} per year, 2019-2024), but {{informatik_by_foreign_part}} of that growth are
  foreign students. German first-years grew by {{informatik_by_german_growth}} a year in Bavaria and changed by
  {{informatik_de_german_growth}} a year in Germany; among them, Informatik is still the strongest large EMI subject. The Bavarian recruiting pool for a cyber programme rises from {{cyber_proxy_by_2024}} first-year
  students (2024) to {{cyber_proxy_by_2030_central}} in 2030 (a central planning value, the midpoint of the KMK and trend
  paths; conservative {{cyber_proxy_by_2030_conservative}}). Among the degree search terms we tracked, "Cyber Security
  Studium" is the largest ({{search_cyber_vs_robotik}} since 2022).
- **B. OTH can fill a cohort.** OTH has its own pool of {{own_pool}} qualified school leavers a year, and the nearest
  full-time dedicated cyber bachelor is at TH Ingolstadt (82 km). The capture model, anchored on a planned capacity and one
  anecdotal intake of comparable programmes, gives {{cyber_bsc_gross_low}} / {{cyber_bsc_gross_central}} / {{cyber_bsc_gross_high}}
  first-years a year (low / central / high).
- **C. EMI has the base, not yet the security core.** EMI already teaches about {{emi_cover_gen_ba}} of a cyber bachelor's
  foundations but at most about {{emi_cover_sec_ba}} of its security content (upper-end estimates); the gap needs an
  estimated {{new_professorships}}, a lab engineer and a security lab.
- **D. Graduates are in demand.** {{ads_cyber_security_de}} job ads matching the keyword "Cyber Security" in Germany
  (all qualification levels), {{ads_cyber_security_by_share}}
  of them in Bavaria and {{ads_cyber_security_amberg_100km}} within 100 km of Amberg; IT jobs held by graduates in Bavaria
  grew {{it_jobs_by_academic_growth}} (2019-2023).

**New students, not relabelled ones.** In the capture model only {{cyber_bsc_from_oth_range}} of the new programme's
students would come from existing OTH programmes (the model does not see OTH programmes without a security focus; at
{{stress_share}} cannibalisation net new would be {{stress_netnew}}); net new to OTH are {{cyber_bsc_netnew_low}} / {{cyber_bsc_netnew_central}} /
{{cyber_bsc_netnew_high}} a year, and about {{cyber_bsc_kept_central}} a year (central) would stay in the region instead
of leaving. Kill rule 1 ({{kill_rule_1_threshold}} core overlap with one OTH programme) is passed: {{overlap_test_cyber_ba}} of core
topics in the formal test, {{cyber_bsc_core_overlap}} to {{module_cover_ii_mi}} in later module-level rechecks.

**How robust.** The Cybersecurity B.Sc. clears the {{robustness_bar}} robustness bar and stays first whichever single
criterion is left out (lowest {{loo_min_cyber_bsc}}, without demand). The same capture and cannibalisation model was run
for all three options, so none is ranked on a model the others lack.

**What is weak, and what would change the conclusion.**

- None of the comparable programmes we checked publishes its intake. The capture range rests on a planned capacity
  ({{thi_cyber_capacity}} at TH Ingolstadt) and one anecdotal figure ({{deg_cyber_anecdote}} at TH Deggendorf). In the
  low case the programme reaches just {{cyber_bsc_gross_low}} first-years against an assumed minimum cohort of
  {{min_cohort}}, and only {{cyber_bsc_netnew_low}} of them are new to OTH. One measured intake figure from a comparable
  programme would narrow the range more than any further modelling.
- Cyber demand is measured through proxies (computer-science subject groups, search interest, job-ad keywords), as
  official statistics have no cybersecurity subject.
- The robotics option has the thinnest evidence (no intake anchor, fit and feasibility from a title-level check); its
  ranges were widened, not its scores raised.

**Recommendation and proposals.** Introduce the Cybersecurity B.Sc., with the first intake after accreditation.
Two further proposals are **team judgement, not model results**: (a) offer the Cyber/OT M.Sc. later, once the bachelor
produces its own graduates; (b) develop robotics as a specialisation within the existing KI B.Sc. rather than as a new
programme, because {{robotics_overlap}} of its core topics are already taught there and, if half of its students came
from OTH programmes, only {{robotics_netnew_cannib50}} a year would be new to OTH (Section 10).
