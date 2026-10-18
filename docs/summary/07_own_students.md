# 7. Would it just take students from OTH's own programmes?

<!-- Plain English. Numbers only as {{key}} placeholders. -->

A new café helps its owner only if it brings in new customers. If it mainly takes customers from the owner's other café
down the street, little is gained. A new study programme is the same: students who would have studied at OTH anyway are
not new students for OTH. We call this **cannibalisation**.

**What we did.** We ran the capture model twice, once without and once with the new programme. When a new option
opens, the model takes its students from all the other options in proportion to how popular they were before. So we can
see where each new student would otherwise have gone: to another OTH programme, or to another university.

**A worked example.** Of the {{cyber_bsc_gross_central}} first-year students in the middle case, about 7 would come from
OTH's own programmes with a security focus. The other {{cyber_bsc_netnew_central}} would be new to OTH. About
{{cyber_bsc_kept_central}} of them come from OTH's own region and would otherwise have left it to study elsewhere.

**What we found.**

- Across the model variants, {{cyber_bsc_from_oth_range}} of the students would come from OTH's own programmes.
- New to OTH: {{cyber_bsc_netnew_low}} / {{cyber_bsc_netnew_central}} / {{cyber_bsc_netnew_high}} students a year (low /
  middle / high).
- Kill rule 1 is clearly passed: {{overlap_test_cyber_ba}} of the programme's core topics are already taught at OTH;
  the limit is {{kill_rule_1_threshold}}.

{{fig:f05_cannibalisation}}

**How sure are we?** Medium. The model only knows OTH programmes that already have a security focus. It does not see a
student who would otherwise study artificial intelligence or electrical engineering at OTH. As a stress test we assumed
that half of the students come from OTH. Then {{stress_netnew}} students a year would be new to OTH (low / middle /
high). The middle case would then be close to the minimum of {{min_cohort}}.

Robotics carries a bigger risk of this kind. {{robotics_overlap}} of its core topics are already taught in OTH's
artificial intelligence bachelor, on the same campus.
