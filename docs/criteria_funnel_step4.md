# Criteria for funnel Step 4 (student trend)

Written and committed before the Step 4 code is written. Step 4 applies the rule block `demand` of
`configs/funnel.yaml` (with `pool_mapping`) to every unit of Step 3. It reports student numbers of each unit's
subject pool; it removes no unit (the trend screen was applied in Step 3) and computes nothing of Steps 5 to 8.

| # | Criterion | Target | How it is checked |
|---|---|---|---|
| T1 | Code before results | committed code on a clean tree; the output carries the commit and the hashes of its inputs | output header, `git log` |
| T2 | Every unit of Step 3 has its demand numbers, on both lists | 1,285 units; none added or removed; the primary and the stress list are both covered by the same run | test |
| T3 | Trend as the rule says | German first-years (master: graduates) of the unit's pool in Bavaria, log-linear slope 2019-2024 (2019-2025); the same slope for Germany, and for foreign students in Bavaria and Germany | test: recomputed from the Destatis tables for a sample of units |
| T4 | Backtests as the rule says | every distinct pool once; origins from 2012, horizons 1 to 5, MASE for naive, drift and ets; a pool with fewer than 12 consecutive years is not backtested; validated only if drift beats naive and its MASE is below 1 | test; reviewer |
| T5 | One model for all pools | the model with the lowest MASE averaged over pools and horizons projects every pool to 2030; the three averages are reported | generated report, test |
| T6 | Foreign students are a corridor, never a point forecast | from flat to compounded growth, reported next to the German number and not added to it | output columns, reviewer |
| T7 | The numbers agree with Step 3 | slope and "validated" of every unit equal those in the Step 3 screen table | test |
| T8 | The pool is named for what it is | notes and output say that the trend is that of the subject pool, not of the programme type, and how many units share a pool | notes, checked by the reviewer |
| T9 | Reproducible | a second run gives the same table | comparison |
| T10 | Reviewed | a fresh-context reviewer compares code and rules and checks every number in the notes; no open blocker, no wrong number | reviewer |
| T11 | The repository works | `python -m pytest` passes completely | test run |

The notes say for the primary list how many units have a growing, flat or falling pool and how reliable the trends
are. If a criterion still fails after 3 rounds, the step stops and Soma is told. No criterion is loosened.
