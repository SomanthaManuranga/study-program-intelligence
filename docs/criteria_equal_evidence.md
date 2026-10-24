# Evaluation criteria: equal evidence for all confirmed candidates (fixed before building)

Task: for every candidate confirmed in Soma's week-2 review (including robotics path B), collect the same evidence the
baseline options had, so all are compared on equal data:
1. demand (Destatis first-years for the closest subject codes, German and international separately; Google Trends terms
   where useful; BA job-ad keywords added to the snapshot config);
2. competition (count and map from the full catalogue: Germany, Bavaria, within 150 km);
3. capture and cannibalisation (the Step 47/48 model with the same anchor logic; where no anchor exists, say so and
   widen the range);
4. lab reality check (does existing equipment support a whole degree, not just single modules; thin cases are a risk);
5. neighbouring countries (final shortlist only, and only if it could change the ranking);
6. ranking with the feasibility gate F1-F4, compared with the frozen baseline (docs/baseline_new_resources.md).

| # | Criterion | Target |
|---|---|---|
| E1 | Equal evidence: every candidate has a value or an explicit "no data + reason" for every criterion | 100 % of cells |
| E2 | Traceability: every number is in reports/key_numbers.yaml and matches its source doc | 100 % (not_found_in_source_doc empty) |
| E3 | Method agreement: e5 vs TF-IDF coverage per candidate; every gap over 20 percentage points listed and decided by hand | all gaps > 20 pp listed and decided |
| E4 | Robustness: winner's P(rank 1) under (a) base, (b) German-only trends, (c) lenient feasibility, (d) leave-one-criterion-out | all reported; "robust" only if >= 80 % in (a) and first in most of (b)-(d) |
| E5 | Sanity tests: pytest for new code (parsing, the nationality split adds up, competitor counts reproduce the catalogue, the ranking reproduces with a fixed seed) | all pass |
| E6 | Claim review: a fresh-context reviewer checks every new factual sentence against the evidence docs | 0 wrong, 0 unsupported, 0 overstated |
| E7 | Argument check: for the winner, claim -> evidence -> strength -> what would change the conclusion; the reviewer attacks it with the strongest counter-argument; the answer goes into the evidence doc | argument written, attack answered |

Iterate: fix failures and re-run the failing checks, at most 3 rounds. If a criterion still fails, stop and report;
never loosen a criterion. Push only when E1, E2, E5 and E6 pass. Report: scorecard (E1-E7: target, result, pass/fail,
what was fixed), the new ranking next to the baseline, open risks.
