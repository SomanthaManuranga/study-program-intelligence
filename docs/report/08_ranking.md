# Ranking of the three options

<!-- Evidence: docs/evidence_ranking.md, configs/analysis.yaml, configs/scores.yaml, docs/kill_rules.md. -->

## Criteria, weights and scores

The six criteria and their weights were fixed on {{rules_fixed_date}}, before the screening: {{weights}}. Each option
was scored from 1 to 5 on each criterion, as a low / central / high range with its source and an evidence-strength
label (Appendix A3). Regional contribution and half of student demand are computed from the model, not set by hand:

- **Student demand** is half a model score from the number of first-years new to OTH (Section 7) and half a trend
  score (Section 3). The model score rises with the logarithm of the net new first-years, from 1 at ten or fewer (half the
  assumed minimum cohort) to 5 at eighty or more.
- **Regional contribution** is computed from the students kept in the region.

The score sheet was drafted by the AI assistant and reviewed by the team, who changed three robotics scores and added
one rule: **weak evidence widens a score's range symmetrically, it does not raise its centre.** The symmetry was added
after a first ranking run with a skewed robotics range (2 / 3 / 5); that run is kept as a sensitivity below. Robotics' fit and
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
use for a robust winner (a bar set when the results were reported, not before the run). Second place goes to the master ({{p_rank2_cyber_msc_base}} of draws); robotics is last in
{{p_rank3_robotics_bsc_base}}.

## Sensitivity

- **Leave one criterion out.** In the base case, dropping each criterion in turn (and rescaling the others) never
  changes the winner (one exception with German-only trends, below).
  The lowest first-place share of the cyber bachelor is {{loo_min_cyber_bsc}} without student demand, then
  {{loo_labour_cyber_bsc}} without labour relevance and {{loo_diff_cyber_bsc}} without differentiation: **its lead rests
  mostly on demand and labour relevance**; demand is also where its evidence is best compared with the other options.
- **Shared capture draw.** With independent capture draws per option the cyber bachelor still wins
  {{p1_independent}} of draws; the shared draw removes noise, it does not create the lead.
- **Skewed robotics range.** With the first draft of the robotics scores (fit and feasibility 2 / 3 / 5, whose mean
  lies above 3) the cyber bachelor wins {{p_rank1_cyber_bsc_skew}}.
- **Demand measured on German entrants only** (Section 3). The trend anchor applied to German first-years or graduates,
  for all three options (scores proposed by the AI assistant, pending the team's review), gives the cyber bachelor 3
  instead of 4 and robotics 1 instead of 2; the master keeps 4, as German graduates in Informatik still grow
  ({{grads_by_german_growth}} a year in Bavaria). The cyber bachelor then wins {{p_rank1_cyber_bsc_german}} of draws,
  just below the {{robustness_bar}} bar (master {{p_rank1_cyber_msc_german}}, robotics {{p_rank1_robotics_bsc_german}}).
  Leaving out one criterion on top, it stays first in {{loo_german_cyber_wins}} runs; without labour relevance the master
  is narrowly ahead ({{loo_german_labour_msc}} against {{loo_german_labour_cyber}}).

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

The Cybersecurity B.Sc. is a robust first choice in the base case; measured on German entrants only, its lead is
smaller and falls just below the robustness bar, while it still ranks first. The master is more likely second ({{p_rank2_cyber_msc_base}} of draws; {{p_rank2_cyber_msc_rob50}} if robotics
cannibalises {{stress_share}}), but this order is less robust than first place. The ranking is only as good as the score
sheet; its weakest inputs are the intake anchors (all options) and the title-level evidence for robotics.
