# Criteria for funnel Step 3 (screen, competition, frozen lists)

Written and committed before the Step 3 code is written. Step 3 applies the rules `definitions`, `pool_mapping`,
`screen` and `freeze` of `configs/funnel.yaml` to the 824 types of Step 2. The trend screen needs the rule
`demand.validated`, so the pools' backtests are computed here; the full demand numbers follow in Step 4. Nothing of
Steps 5 to 8 is computed (no job ads, no first-year estimate, no curriculum, no ranking).

| # | Criterion | Target | How it is checked |
|---|---|---|---|
| S1 | Code before results | the code is committed before it runs on a clean tree; every output carries the commit and the hashes of its input files | output header, `git log` |
| S2 | Every unit gets the same tests | every type x level with assigned offers at 2 or more institutions is in the screen table, with the result of each of the four screens and its numbers; none is added or removed by hand | test: units recomputed from the Step 2 files |
| S3 | "Already at OTH" as the rule says | a unit is dropped if an OTH offer of its level lies within the type's median member distance of the centroid; a merged group with such a unit is dropped as a whole | test: recomputed from the vectors for all units |
| S4 | Teacher training as the rule says | share of assigned offers matching the pattern; dropped from 0.5 | test on the offer table; reviewer reads 20 units on each side of the line |
| S5 | Trend screen as the rule says | pool weights of every unit sum to 1; every subject label has a Destatis code; slope on 2019-2024 (master: graduates 2019-2025); dropped only below -3.0 %/yr and only if the pool's trend is validated (drift beats naive and MASE below 1; no backtest, no drop) | tests; reviewer |
| S6 | EMI-field screen as the rule says | calibration on OTH's own offers reported (positives, negatives, AUC, bar); below AUC 0.8 the screen flags and does not drop | generated report, test |
| S7 | Competition is counted by content similarity | similar offers = assigned offers of the type plus every other offer of that level inside the type's radius, without OTH's own offers and without distance-learning offers; counts within 50, 100 and 150 km of Amberg, in Bavaria, in the south, in Germany; never used as a cut | test: recomputed from the vectors for all units |
| S8 | Regional gap as the rule says | the two flags, the Bavarian quotient with 5 pseudo-offers and the popularity tier 2 from the Destatis tables by Land, for every unit | test on the formulas; reviewer |
| S9 | Every type on the primary list is read | a fresh reader, titles only, 10 member titles per type; the share of types that pass is reported next to the bar of 80 %; a failing type carries the flag "mixed" | reader's table, flag in the list |
| S10 | The check of "similar" is ready for Soma | 100 offers of 10 units drawn as the rule says, in shuffled order, without the side they are on; the key is kept apart; until Soma has marked them the competition counts carry the flag "not validated yet" | sheet, key file, flag |
| S11 | Both lists are frozen | primary (four screens) and stress (at OTH only), each with a hash, the code commit and a clean tree | files, report |
| S12 | The result can be reproduced | a second run gives the same screen table and the same two lists | comparison of two runs |
| S13 | The code follows the rules | 0 differences between the code and `configs/funnel.yaml` that are not written down as a decision | fresh-context reviewer |
| S14 | Every number in the Step 3 notes is right | 0 wrong claims in a fresh-context check against the generated files | reviewer |
| S15 | The repository works | `python -m pytest` passes completely | test run |
| S16 | Soma can check without searching | an English side-by-side table of 15 units (5 dropped as "at OTH", 5 dropped by another screen, 5 kept): the unit's titles, the test, the number, the source file | table in the notes |

The notes of the step say for every unit why it stays or goes (the full table is a generated file; the notes show
the counts per reason and the surviving units).

If a criterion still fails after 3 rounds, the step stops and Soma is told. No criterion is loosened.

## After the first run (15 Nov 2026)

Written and committed before the changed code runs. The first run followed the rules as written and is void: the
merged groups chained most units together and the EMI-field score could not tell EMI's field from others
(docs/decision_log.md). Two rules are changed as a proposal for Soma; the criteria above stay, with these additions.

| # | Criterion | Target | How it is checked |
|---|---|---|---|
| S17 | Merged groups do not chain | every pair of units in a group has centroids inside each other's radius; the largest group is reported | test: all pairs recomputed from the centroids |
| S18 | The EMI-field score works on units it has not been tuned on by hand | AUC of at least 0.8 on the 300 marked units ("yes" or "partly" against "no"); the bar keeps at least 95 % of the marked field units; the share of marked outside units it keeps is reported | test on docs/funnel_emi_labels.csv |
| S19 | Soma confirms or rejects the two changed rules | asked at the end of the step, with the first run's result next to the new one | Soma's answer |

