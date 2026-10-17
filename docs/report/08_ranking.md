# Ranking of the three options

<!-- Evidence: docs/evidence_ranking.md, configs/analysis.yaml, configs/scores.yaml, docs/kill_rules.md. -->

## Criteria, weights and scores

The six criteria and their weights were fixed on {{rules_fixed_date}}, before the screening: {{weights}}. Each option
was scored from 1 to 5 on each criterion, as a low / central / high range with its source and an evidence-strength
label (Appendix A3). Two criteria are computed from the model, not set by hand:

- **Student demand** is half a model score from the number of first-years new to OTH (Section 7) and half a trend
  score (Section 3). The model score rises with the logarithm of the net new first-years, from 1 below the assumed
  minimum cohort to 5 for a large programme.
- **Regional contribution** is computed from the students kept in the region.

The score sheet was drafted by the AI assistant and reviewed by the team, who changed three robotics scores and added
one rule: **weak evidence widens a score's range symmetrically, it does not raise its centre.** Robotics' fit and
feasibility, both based only on a title-level check, were therefore scored like the cyber bachelor in the centre but
with a wider range ([kill_rules.md](../../docs/kill_rules.md)).

At central scores and base weights the weighted totals are {{total_cyber_bsc}} for the Cybersecurity B.Sc.,
{{total_cyber_msc}} for the Cyber/OT M.Sc. and {{total_robotics}} for Robotics + AI. No option has a feasibility
rating of 1, so the feasibility gate (kill rule 2) removes none.

## Monte Carlo

The central totals ignore uncertainty in both the weights and the scores. In {{mc_draws}} draws the weights were
sampled from a Dirichlet distribution centred on the base weights (concentration {{dirichlet_conc}}), the hand scores
from triangular distributions over their ranges, and the capture model once per draw for all options together: the
uncertainty of the intake anchors is shared model error and should not reorder the options at random.

| | Cybersecurity B.Sc. | Cyber/OT M.Sc. | Robotics + AI B.Sc. |
|---|---|---|---|
| First place, base case | **{{p_rank1_cyber_bsc_base}}** | {{p_rank1_cyber_msc_base}} | {{p_rank1_robotics_bsc_base}} |
| First place, robotics with {{stress_share}} cannibalisation | **{{p_rank1_cyber_bsc_rob50}}** | {{p_rank1_cyber_msc_rob50}} | {{p_rank1_robotics_bsc_rob50}} |

{{fig:f06_rank_probabilities}}

The Cybersecurity B.Sc. ranks first in {{p_rank1_cyber_bsc_base}} of the draws, above the {{robustness_bar}} bar we
set for a robust winner. Second place goes to the master ({{p_rank2_cyber_msc_base}} of draws); robotics is last in
{{p_rank3_robotics_bsc_base}}.

## Sensitivity

- **Leave one criterion out.** Dropping each criterion in turn (and rescaling the others) never changes the winner.
  The lowest first-place share of the cyber bachelor is {{loo_min_cyber_bsc}} without student demand, then
  {{loo_labour_cyber_bsc}} without labour relevance and {{loo_diff_cyber_bsc}} without differentiation: **its lead rests
  mostly on demand and labour relevance**, the criteria where its evidence is strongest.
- **Shared capture draw.** With independent capture draws per option the cyber bachelor still wins
  {{p1_independent}} of draws; the shared draw removes noise, it does not create the lead.
- **Skewed robotics range.** With the first draft of the robotics scores (fit and feasibility 2 / 3 / 5, whose mean
  lies above 3) the cyber bachelor wins {{p_rank1_cyber_bsc_skew}}.

{{fig:f07_leave_one_out}}

## Evidence strength

| Option | Demand model | Demand trend | Labour | Fit | Feasib. | Differ. | Regional |
|-------------------|--------|--------|--------|--------|--------|--------|--------|
| Cybersecurity B.Sc. | medium | strong | medium | strong | medium | strong | medium |
| Cyber/OT M.Sc. | weak | strong | medium | medium | medium | strong | weak |
| Robotics + AI B.Sc. | **weak** | medium | medium | **weak** | **weak** | medium | medium |

**Evidence asymmetry and how it was handled.** Before ranking, the capture and cannibalisation model of Sections 4
and 7 was run unchanged for all three options, so that none is scored on a model the others lack; where an option had
no public intake anchor (robotics) or only one (the master), this is stated and its range is widened, and weak
evidence widens a score's range without raising its centre.

## Assessment

The Cybersecurity B.Sc. is a robust first choice. The order of the other two is also clear in the base case, and
clearer still when robotics' likely cannibalisation is taken into account. The ranking is only as good as the score
sheet; its weakest inputs are the intake anchors (all options) and the title-level evidence for robotics.
