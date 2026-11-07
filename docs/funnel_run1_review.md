# Funnel run 1: review result

Run 1 is **not a result**. A fresh-context claim review of `docs/funnel_reasoning.md` found 6 wrong, 3 unsupported and
13 overstated claims, and 8 rules that the code applied differently from `configs/funnel.yaml`. About 200 other claims
checked out. A separate check found that the supply test itself is not valid.

## Implementation differences to fix before the next run

| # | Rule | What the code did | Effect |
|---|---|---|---|
| R1 | `text.dropped` | "Inhalte bitte bei der Hochschule erfragen" stayed in 41 offer texts | Formed type 397 and junk keywords |
| R3 | `freeze.lists` | Only the primary list went through steps 4-6 | No stress results exist |
| R4 | `capture.oth_sites` | One fixed site at Amberg instead of the assigned OTH offers | "From OTH" shares are not candidate-specific |
| R5 | `demand.model_choice` | Each pool's own best model instead of the pooled best | 103 validated drops instead of 101 on naive |
| R6 | `labour` | Germany and Bavaria only for the first keyword; no German/English pairing; keywords stored after counting | Weak job-ad measure |
| R7 | `capture.w`, scale | w labels inverted against the yaml; scale 1.0 is an unstated default affecting 75 of 143 candidates | Low and high cases swapped against the rule |
| R2, R8 | smaller | 15 of 18 old lists tested; unscaled figure not reported; variants not merged in supply | Minor |

## Other problems found

- **Supply test not valid:** competition counted by cluster membership understates it. "Informatik dual" shows 0 offers
  within 100 km, while 15 general informatics bachelors (one distance-only) lie within 100 km.
- **Job-ad keywords:** boilerplate and generic words passed the stoplist. Among the five candidates in the reasoning,
  only cybersecurity's count comes from an on-topic keyword.
- **Level check:** it passes only because Saarland counts twice. With Saarland once, the median error is about 0.54
  against the limit of 0.405, which would trigger a shrink factor of about 1.74.
- **Old-list recovery:** on full-time offers only, AI/data reaches 0.628 and mobility/vehicle 0.541, so the statement
  that the old lists were not natural groupings does not hold as written.
- **Screen commit:** the frozen list came from code changed in `fe8ffc3`, not `3e67a81` alone. The fix also changed
  one validated trend.
- **Thresholds added after the types were computed:** the 80 % reference rule, the teacher share of 0.5, and the
  fit-proxy anchor.

## What held

- Selection of the clustering setting, rare-path limits, at-OTH test, supply limit, trend threshold, EMI bar, list
  hashes, minimum cohort, top 20 list and the F1/F2/F4 arithmetic were applied as stated.
- The feasibility gate on real curricula separates the candidates, and the second-reference check caught two false
  passes.

## Consequence

`docs/funnel_reasoning.md` describes run 1 and carries the errors above. Steps 2-7 must rerun after the fixes, and the
hand-check sheet is not issued until then.
