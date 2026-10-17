# From all EMI fields to three candidates: the selection funnel

<!-- Evidence: docs/evidence_funnel.md (synthesis of evidence_competition_demand, theme_precision, overlap_test,
kill_rules, evidence_ranking). Numbers only via {{placeholders}}. -->

A recommendation is only convincing if the candidate was not picked first and justified afterwards. This section
shows the order of the decisions: which rules were fixed in advance, which fields were screened, and why each
candidate left the funnel. Evidence: [evidence_funnel.md](../../docs/evidence_funnel.md).

## Rules fixed before screening

The scoring criteria and their weights (configuration file `configs/analysis.yaml`) and the five kill rules
(`docs/kill_rules.md`) were committed to the project repository on {{rules_fixed_date}} at 16:35 and 16:37, six hours
before the first demand and supply screening (22:42 the same day). The weights have not changed since. Two later
additions are recorded as such in the decision log: scoring anchors for the criteria other than demand, and the rule
that weak evidence widens a score's range without raising its centre. Both were written after the evidence was
collected but before the ranking was computed.

## The funnel

{{fig:f00_funnel}}

| Stage and filter | Left | Dropped, and why |
|---------------------------|------|--------------------------------------------------------|
| **0 Screening:** {{funnel_offers}} programme offers [@ba2026studiensuche], {{funnel_subjects}} EMI-related subjects [@destatis2026students], title rules per theme | {{val:funnel_0_themes}} | - |
| **1 Demand trend:** feeder subjects must not be shrinking | {{funnel_1_demand}} | media technology / games: Medientechnik {{funnel_medientechnik}} and Medieninformatik {{funnel_medieninformatik}} first-years a year in Germany |
| **2 Supply gap:** thin supply near OTH, not already offered by OTH | {{val:funnel_2_candidates}} | generic AI / data ({{funnel_ai_ba_150km}} bachelors and {{funnel_ai_ma_150km}} masters within 150 km; OTH offers both levels); automation, energy, medtech (already at OTH); microelectronics to the watch list ({{funnel_micro_firstyears}} first-years in Germany in 2025) |
| **3 Kill rule 1:** {{kill_rule_1_threshold}} of core topics in one OTH programme at the same level | {{funnel_3_shortlist}} | embedded / cyber-physical systems master ({{funnel_embedded_overlap}} already in IT und Automation); part-time AI master (identical to AI for Industrial Applications) |
| **4 Kill rules 2-4:** feasibility rating 1; five-year fall in entrants; shrinking graduate pipeline (master) | {{funnel_4_after_gates}} | none |
| **5 Ranking:** weighted criteria, {{mc_draws}} Monte Carlo draws | 1 | Cyber/OT M.Sc. ({{p_rank1_cyber_msc_base}} first place), Robotics + AI B.Sc. ({{p_rank1_robotics_bsc_base}}) |

Evidence per stage: stages 0-2 [competition and demand](../../docs/evidence_competition_demand.md) and
[theme precision](../../docs/theme_precision.md); stage 3 [overlap test](../../docs/overlap_test.md); stage 4
[kill rules](../../docs/kill_rules.md) and [ranking](../../docs/evidence_ranking.md); stage 5
[ranking](../../docs/evidence_ranking.md).

The five candidates after stage 2 were a Cybersecurity B.Sc., a Cybersecurity M.Sc. with an industrial profile, an
embedded / cyber-physical systems M.Sc., a Robotics + AI B.Sc., and a part-time AI master. The last was included on
purpose as a control case: it should fail the incrementality test, and it did.

## What the funnel does and does not show

- **Order, not hindsight.** Each stage used rules written before its data were looked at; the git history shows the
  sequence. Cybersecurity survived every stage on the same terms as the other candidates.
- **Robotics was kept although it sat exactly at the kill-rule threshold** ({{robotics_overlap}} of its core topics are
  already taught in the KI B.Sc.; kill rule 1 drops only candidates with {{kill_rule_1_threshold}}). It stayed in as the
  comparison case, which is why it was modelled in full.
- **Weak point: stage 2 for automation, energy and medtech.** The screening table shows that OTH already offers each of
  these themes, and they were not carried forward, but no separate written verdict exists for them. Energy and medtech
  also belong mainly to other faculties.
- **Weak point: the screening relies on keyword rules on programme titles** in {{funnel_subjects}} subjects and
  {{funnel_fields}} catalogue study fields. Their precision was checked by hand (Section 3); themes outside these fields were not screened.
