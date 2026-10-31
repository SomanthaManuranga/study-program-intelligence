# Evaluation criteria: hand check part 1, open rows and sensitivity (fixed before building)

Task: record Soma's part-1 verdicts (sheet rows 1, 2, 4, 5, 6, 8, 10, 12-17 confirm; 11 reject; 3, 7, 9 open); for the
open rows 3, 7 and 9 an English side-by-side comparison of the module texts (facts only, no proposed verdict); a
sensitivity table showing which single verdicts flip each candidate's gate result; F1-F4 recomputed with part 1
applied and the open rows marked "open". The ranking is not rerun before the 1 Nov job ads and the Trends downloads.

| # | Criterion | Target |
|---|---|---|
| E1 | Every recorded verdict matches Soma's list, row by row (automated check against the sheet) | 17 of 17 rows |
| E2 | Each side-by-side comparison quotes the module text with its PDF page; nothing is paraphrased without a source | every statement sourced |
| E3 | The sensitivity table tests every E2 row as a single flip for both candidates | 17 of 17 rows |
| E4 | Tests pass, including a test that the sheet's row numbers and the YAML match | all pass |
| E5 | Fresh-context claim review of the new text | 0 wrong, 0 unsupported, 0 overstated |

Iterate: at most 3 rounds; if a criterion still fails, stop and report. Commit locally; push only after Soma has
answered rows 3, 7 and 9 and the recompute passes.
