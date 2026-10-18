# 8. Comparing the three options

<!-- Plain English. Numbers only as {{key}} placeholders. -->

We compared three finalists: a cybersecurity bachelor, a cybersecurity master with a focus on **OT security** (the
security of machines and factories), and a bachelor in robotics with artificial intelligence.

**How we scored them.** Think of a school report where some subjects count more than others. Each option got a score
from 1 to 5 on six points. The points have fixed **weights**: {{weights}}. Student demand counts most. We recorded no reason when we set
the weights, but this fits the task of attracting students. Every score has a range from low to high, and a score that
rests on weak evidence got a wider range. With the middle scores, the totals are {{total_cyber_bsc}} for the cybersecurity bachelor,
{{total_cyber_msc}} for the master and {{total_robotics}} for robotics.

**What-if scenarios.** Weights and scores are judgements, so a single total could mislead. We therefore repeated the
comparison {{mc_draws}} times. In each run the weights moved a little around the chosen values, and each score was drawn
from its range. Then we counted how often each option came first. It is like replaying a season many times with slightly
different weather and seeing which team usually wins.

**What we found.**

- The cybersecurity bachelor came first in {{p_rank1_cyber_bsc_base}} of the scenarios, the master in
  {{p_rank1_cyber_msc_base}} and robotics in {{p_rank1_robotics_bsc_base}}.
- If robotics takes half of its students from OTH (Section 7), the cybersecurity bachelor wins
  {{p_rank1_cyber_bsc_rob50}} of the scenarios.
- **Sensitivity check:** we left out each scoring point in turn. The cybersecurity bachelor stayed first every time. Its
  lowest share was {{loo_min_cyber_bsc}}, when student demand was left out. So its lead rests mostly on demand, and next on job prospects.
- The master usually comes second ({{p_rank2_cyber_msc_base}} of the scenarios); robotics usually comes last
  ({{p_rank3_robotics_bsc_base}}).

{{fig:f06_rank_probabilities}}

**How sure are we?** First place is robust in the base case. Counting German students only, the demand score of the
cybersecurity bachelor drops, and so does robotics'. The bachelor then comes first in {{p_rank1_cyber_bsc_german}} of
the scenarios, just below our bar for "robust", and the master in {{p_rank1_cyber_msc_german}}. Two more honest
notes. In our first run, robotics' wide ranges were uneven and
raised its average. Leaving out demand then made robotics and the cybersecurity bachelor about level
({{loo_first_run_tie}}). We made the ranges even,
and the cybersecurity bachelor has stayed first in the main checks since. And the {{robustness_bar}} bar we use for "robust" was set when
we reported the results, not before.
