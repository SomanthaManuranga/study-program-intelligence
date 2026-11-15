# Criteria for funnel Step 6 (first-years, and students new to OTH)

Written and committed before the Step 6 code is written. Step 6 applies the rule block `capture` of
`configs/funnel.yaml` to every unit of Step 3 (both lists). It removes no unit: the minimum cohort is recorded as a
flag for the shortlist of Step 7. Nothing of Steps 7 and 8 is computed.

| # | Criterion | Target | How it is checked |
|---|---|---|---|
| C1 | Code before results | committed code on a clean tree; the output carries the commit and the hashes of its inputs | output header, `git log` |
| C2 | Every unit, both lists, the same model | 1,285 units; competitors are the unit's similar-offer sites, taken from the Step 3 definition; no site and no number set by hand | test |
| C3 | Huff model as the rule says | origins: school leavers by Bavarian county (bachelor), students at Bavarian universities of applied sciences by campus (master); new site Amberg and Weiden (bachelor), Amberg (master); OTH's own offers of the type as sites with the weight w (1.0, 0.5, 0.25); the shares of every origin sum to 1 | unit tests on a small example; test on the output |
| C4 | Anchor and scale as the rule says | anchor: German first-years (master: graduates x 0.5) of the pool in Bavaria per Bavarian offer of the pool, offers counted fractionally; Germany-wide if the pool has no Bavarian offer, flagged; scale: OTH's Huff demand over the mean of the unit's Bavarian similar-offer sites; 1.0 and flagged without one | test: recomputed for a sample of units |
| C5 | Gross and net-new as the rule says | gross central = anchor x scale, low x 0.33, high x 3.0; net-new = gross x (1 - share from OTH) with w central, pessimistic, optimistic; low <= central <= high for every unit | test |
| C6 | Honest about the level | the level check against the few published first-year numbers is reported as it is; no correction factor is applied | generated report, reviewer |
| C7 | Foreign students on top, never inside | a corridor from 0 to the pool's foreign share, next to the central number | output columns |
| C8 | Minimum cohort is a flag here | units whose central gross is below 20 are counted and flagged, not removed | test |
| C9 | Reproducible | a second run gives the same table | comparison |
| C10 | Reviewed | a fresh-context reviewer compares code and rule, recomputes the numbers and checks the notes; no open blocker, no wrong number | reviewer |
| C11 | The repository works | `python -m pytest` passes completely | test run |

The notes state the model's known limits (straight-line distance, Bavarian origins only, no attractiveness of a
location, competition counts not validated). If a criterion still fails after 3 rounds, the step stops and Soma is
told. No criterion is loosened.
