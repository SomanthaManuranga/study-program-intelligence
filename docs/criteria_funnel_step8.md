# Criteria for funnel Step 8 (ranking, stress tests, decision)

Written and committed before the Step 8 code is written. Step 8 applies the rule blocks `ranking`, `stress_tests`
and `decision` of `configs/funnel.yaml` to the result of Step 7. It runs in two parts: 8a the decision (ranking,
Monte Carlo, cross-check, downstream factorial, decision rule) and 8b the list-changing specs (earlier steps rerun
with one rule changed, up to the pre-gate ranking).

| # | Criterion | Target | How it is checked |
|---|---|---|---|
| D1 | Code before results | committed code on a clean tree; outputs carry the commit and the hashes of their inputs | output header |
| D2 | Sets as the rule says | decision.first among existing-resources passers, decision.second among band passers, both from Step 7 unchanged; every probability within its set | test |
| D3 | Inputs as the rule says | central, low and high of every criterion from the earlier steps' files; a missing input is 1 and flagged; no number typed by hand | test recomputes every input for every candidate |
| D4 | Value functions and weights as the rule says | the anchors of `ranking.value_functions`; weights of configs/analysis.yaml unchanged | test |
| D5 | Monte Carlo as the rule says | Dirichlet concentration 50, 10,000 draws, seed 42, triangular inputs (log for net-new and labour), widenings uniform, clipped 1-5; P(rank 1) and P(beats the runner-up) | test on a small example; reproducible |
| D6 | Cross-check | PROMETHEE II on the central values, linear preference, indifference 0, preference 4 | test on a small example |
| D7 | Downstream factorial complete | every combination of the 20 factors is counted (factors that cannot change a set or a central score are counted by multiplicity, not dropped); win share with no-winner specs in the denominator; regret table; which missing number would change the winner | test: counts sum to the full factorial |
| D8 | Decision as the rule says | the decision rule applied to each set; the sentence of decision.first states new teaching in ECTS and professor-equivalents; decision.second never worded as a recommendation | test, reviewer |
| D9 | List-changing specs (8b) | each spec run up to the pre-gate ranking with only its one rule changed; reported: how many of the primary gate candidates stay in the first 20; a spec that cannot be run is named with the reason | reviewer |
| D10 | Reproducible | a second run gives the same tables | comparison |
| D11 | Reviewed | a fresh-context reviewer compares code and rules, recomputes the numbers and checks the notes; no open blocker, no wrong number | reviewer |
| D12 | The repository works | `python -m pytest` passes completely | test run |

The notes state, whatever the result: the recommendation rests on one handbook and on AI judgements; the two-module
rule of Step 7 was set knowing the second-pass result, and the decision without it is reported; competition, trend
and overlap enter more than once (`ranking.disclosed`). If a criterion still fails after 3 rounds, the step stops and
Soma is told. No criterion is loosened.
