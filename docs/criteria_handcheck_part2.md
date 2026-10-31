# Evaluation criteria: hand check part 2 and the three-level conclusion (fixed before building)

Task: record Soma's part-2 verdicts (rows 3, 7, 9 rejected with reasons; row 16's law part counted by its share of
RO 71's learning outcomes, or 2.5 ECTS if that cannot be determined); recompute F1-F4 under the strict rule (the
decision) and the lenient rule (the pre-registered sensitivity, configs/feasibility.yaml) for all candidates; restructure
the conclusion as three levels: (a) strict existing resources, (b) lenient existing resources (up to 20 ECTS of new
modules by existing professors), (c) with investment (the cybersecurity baseline), each with best option, cost,
robustness and main risk; state that the 10-ECTS cap is the project's own operationalisation of the supervisor's
constraint, fixed before re-scoring. The demand ranking is not rerun before the 1 Nov job ads and the Trends downloads;
the demand comparison is marked pending.

| # | Criterion | Target |
|---|---|---|
| E1 | The recorded verdicts match Soma's decisions row by row (automated test) | 17 of 17 |
| E2 | F1-F4 correct under both rules (test against a hand-computed example for one candidate) | test passes |
| E3 | Each of the three levels has best option, cost, robustness and main risk | no gaps |
| E4 | A fresh-context reviewer attacks the three-level conclusion ("is this just avoiding a recommendation?"); attack and answer recorded | recorded |
| E5 | All tests pass | all pass |
| E6 | Fresh-context claim review | 0 wrong, 0 unsupported, 0 overstated |

Iterate: at most 3 rounds; if a criterion still fails, stop and report. Push to soma/rescope when E1, E2, E5 and E6 pass.
