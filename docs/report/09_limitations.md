# Limitations

<!-- Collected from the caveats of all evidence docs; each item names where it matters. -->

The evidence is strongest where official statistics exist (field trends, school leavers, employment) and weakest
where they do not (programme intakes, cyber demand itself). The main limitations, in order of how much they could
change the conclusion:

1. **No measured programme intakes.** None of the comparable programmes we checked publishes first-year numbers, official
   statistics give them only per institution, and we had no OTH admission data. The capture range rests on a planned capacity ({{thi_cyber_capacity}} at TH Ingolstadt) and one
   anecdotal figure ({{deg_cyber_anecdote}} at TH Deggendorf). This is the largest single uncertainty (Sections 4 and 7);
   the low case is at the edge of viability ({{cyber_bsc_gross_low}} first-years) and below the minimum cohort in
   students new to OTH ({{cyber_bsc_netnew_low}}).
2. **Cybersecurity demand is measured through proxies.** Official statistics have no cybersecurity subject, so demand
   is read through computer-science entrants, search interest and job-ad keywords (Sections 3 and 6). Search
   interest has plateaued since 2022.
3. **The capture model is simple.** Straight-line distances, Bavarian origins only (students from Saxony, Thuringia
   and further away are missing, which on its own biases the estimate downward), fixed total demand, and a Huff structure that
   understates substitution between near-identical programmes (Sections 4 and 7).
4. **Uneven evidence across the options.** Robotics has no intake anchor and its fit and feasibility come from a
   title-level overlap check only; the master's demand model has one anchor and a borrowed spread. Both were handled by
   wider ranges (Section 8), but the comparison is still less certain than the cyber bachelor's own case.
5. **Scoring anchors written late.** The weights and kill rules were fixed before screening, but the scoring anchors
   for criteria other than demand were written after the evidence was collected, though before the first ranking run, and the weak-evidence rule
   was tightened after that run (Sections 2 and 8).
6. **Module comparison.** Similarity models judge module texts, not actual teaching; the embedding model tends to
   overestimate coverage (Section 5). One EMI handbook covers only its first study section.
7. **Staffing and cost.** Staffing rests on stated assumptions (cohort size, lab groups, teaching reductions), staff
   research profiles were not read (blocked for AI crawlers, skipped on principle), and the cost of the security lab is
   not estimated (Section 5).
8. **Job ads are indicators.** Keyword counts are not vacancies by occupation; the job board does not cover all ads;
   no county-level occupation data could be used (Section 6).
9. **Blocked or missing sources.** The federal-state regional database (robots.txt), the Bavarian GENESIS web service
   (login failed), OTH person pages and some competitor documents were not used, and one school year (2018/19) is
   missing from the school-leaver series. None was worked around (Section 1, Appendix A1).
10. **Screening scope.** Themes were screened with keyword rules on titles within the catalogue's
    {{funnel_fields}} study fields; four of the rules were checked by hand, and themes outside these fields were not screened
    (Section 2).

In our sensitivity runs no single limitation changes the winner (lowest first-place share {{loo_min_cyber_bsc}},
without demand), and the weakest evidence concerns the options that rank behind it. They do matter for the size of
the programme and for the decision to start: the intake range should be narrowed before committing resources
(Section 10).
