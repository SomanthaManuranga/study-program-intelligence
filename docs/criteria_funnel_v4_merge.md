# Criteria: rules version 4, R1 merge (one candidate per programme title)

Written and committed before the code runs. Rule: `configs/funnel.yaml`, `version_4.title_merge` (and
`version_4.new_to_oth_scenarios` for the scenario columns). Code: `analysis/funnel_merge.py`.

## Exact readings of the rule (decided before the run, from the wording; no result seen)

| # | Case the wording leaves open | Reading |
|---|---|---|
| E1 | A unit's "title match" | its normalised main title is shared by at least one other unit of the same level |
| E2 | Partner of one title group | a unit without a title match whose version-3 group holds title-matched units of exactly one title group joins that candidate (one hop) |
| E3 | Partner of two or more title groups | it joins none of them: it forms a candidate with the other unmatched units of its version-3 group (no chaining between title groups) |
| E4 | Title-matched units in one version-3 group with different titles | each stays with its own title group; a title-matched unit is never a partner |
| E5 | Candidate dropped as a whole (a title-matched unit at OTH) | its title-matched units drop; its partners that are not at OTH form a candidate with the other unmatched units of their version-3 group |
| E6 | Screens | applied to units singly, as in version 3; the merged trend is an input, not a screen |
| E7 | Name and number of a candidate | number = the lowest type number of its units (used for ties, as version 3); name = the shared main title, else the central titles of its lowest surviving type (corrected after the first run: the name came from a dropped unit, e.g. cybersecurity was named after a safety type; no number changed) |
| E8 | Labour with a keyword not counted | labour input "missing counts", value 1 (version 3); no new job-ad request in this step |
| E9 | Foreign share and "international on top" | not computed for merged candidates in this step (not a gate input) |

## Criteria

| # | Criterion | Target |
|---|---|---|
| M1 | Every unit of Step 3 belongs to exactly one candidate, by code | all 1,285, none twice |
| M2 | Version-3 groups with title-matched units of two or more title groups are counted and listed with their handling (E3) | listed |
| M3 | For a candidate of one unit, every measure equals the version-3 value of that unit (trend, validation, EMI score, competition, anchor, scale, gross, net-new) | all equal (check in code) |
| M4 | A fresh-context reviewer recomputes the measures of 5 candidates, the Informatik bachelor among them, from the input tables | no wrong number |
| M5 | The version-3 first 20 of the gate order are shown with their place in the new order (sensitivity) | shown |
| M6 | A second run gives the same output hashes | same |
| M7 | Tests for the normalisation, the partner readings E2-E5 and M1; all tests pass | all pass |
| M8 | Code committed before the run; nothing edited by hand | run stamp clean |
