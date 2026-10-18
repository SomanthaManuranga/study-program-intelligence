# From all EMI fields to three candidates: the selection funnel

<!-- Evidence: docs/evidence_funnel.md (synthesis of evidence_competition_demand, theme_precision, overlap_test,
kill_rules, evidence_ranking). Numbers only via {{placeholders}}. -->

A recommendation is only convincing if the candidate was not picked first and justified afterwards. This section
shows the order of the decisions: which rules were fixed in advance, which fields were screened, and why each
candidate left the funnel. Evidence: [evidence_funnel.md](../../docs/evidence_funnel.md).

## Rules fixed before screening

The scoring criteria and their weights (configuration file `configs/analysis.yaml`) were committed to the project
repository on {{rules_fixed_date}} at 16:35, a draft of the kill rules at 16:37 and the final five kill rules
(`docs/kill_rules.md`) at 17:40, about five hours before the first demand and supply screening (22:42 the same day).
The weights have not changed since. Later additions are recorded as such in the decision log: scoring anchors for the
criteria other than demand and the rule that weak evidence widens a score's range without raising its centre were
written after the evidence was collected but before the first ranking run; after that run the rule was tightened
(ranges must be symmetric), and the earlier version is kept as a sensitivity (Section 8).

## The funnel

{{fig:f00_funnel}}

| Stage and filter | Left | Dropped, and why |
|---------------------------|------|--------------------------------------------------------|
| **0 Screening:** {{funnel_offers}} programme offers [@ba2026studiensuche], {{funnel_subjects}} EMI-related subjects [@destatis2026students], title rules per theme | {{val:funnel_0_themes}} | - |
| **1 Demand trend:** feeder subjects must not be shrinking (robotics kept as a combined AI angle although its feeders are flat or falling) | {{funnel_1_demand}} | media technology / games: Medientechnik {{funnel_medientechnik}} and Medieninformatik {{funnel_medieninformatik}} first-years a year in Germany |
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
purpose as a control case for the incrementality rule; it was dropped at kill rule 1 because OTH already offers the
same curriculum.

## What the funnel does and does not show

- **Order, not hindsight.** The weights and kill rules were committed before the first screening; the screening
  filters (stages 1-2) were committed with the screening itself, and the later scoring anchors are logged with their
  dates; the git history shows the sequence. Cybersecurity survived every stage on the same terms as the other
  candidates.
- **Robotics was kept although it sat exactly at the kill-rule threshold** ({{robotics_overlap}} of its core topics are
  already taught in the KI B.Sc.; kill rule 1 drops only candidates with {{kill_rule_1_threshold}}). It stayed in as the
  comparison case, which is why it was modelled in full.
- **A written verdict for every theme.** Automation, energy and medtech were first dropped as "already at OTH" without
  a written verdict, and five themes in the code (software engineering, sustainability, mobility, quantum, aerospace)
  were never screened. A later check applied the same two filters, with thresholds written out, to all
  {{themes_all}} themes including data science, health/medical informatics and energy informatics
  ([evidence_theme_verdicts.md](../../docs/evidence_theme_verdicts.md)). It reproduces the funnel's outcome for almost
  all original rows. Some new themes pass both filters, but each faces a likely kill rule 1 at title level, lies
  outside EMI's subjects, or has no market evidence. Health/medical informatics is the closest case; its overlap with
  OTH's Medizintechnik was not tested. The thresholds were written after the screening, so they explain it rather than
  having been fixed before.
- **Weak point: the screening relies on keyword rules on programme titles** in {{funnel_subjects}} subjects and
  {{funnel_fields}} catalogue study fields. The precision of the cybersecurity, robotics, AI/data and embedded rules was checked by hand (Section 1); the
  other rules were not checked, and themes outside these fields were not screened.
