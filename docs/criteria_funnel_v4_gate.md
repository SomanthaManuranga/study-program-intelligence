# Criteria: rules version 4, R2 (which candidates get a module check)

Written and committed before the reader marks anything. Rule: `configs/funnel.yaml`, `version_4.gate_breadth` and
the second entry of `version_4.deviations` (the Informatik bachelor as a control). Code: `analysis/funnel_gate4.py`.

## The reader's question (committed before the sheet is made)

> Is this kind of programme inside the field of a faculty of electrical engineering, media and computer science
> (yes, partly or no)?

- **yes:** the programme's core subject is one EMI teaches: electrical or information engineering, computer science
  or informatics (including its applied forms such as software, data or security), or media and design.
- **partly:** the programme joins an EMI subject with a non-EMI subject in roughly equal parts (for example business
  informatics, mechatronics, media management).
- **no:** the core subject is outside these fields, even if some modules touch them (for example civil engineering,
  business administration, architecture).

The reader sees only up to 8 programme titles per group, drawn at random, in a shuffled order of groups; no type
number, no score, no gate order, no candidate name. One line of reason per group.

## Exact readings (decided before the marks)

| # | Case | Reading |
|---|---|---|
| F1 | Where the new marks are kept | `docs/funnel4_emi_labels.csv`, next to `docs/funnel_emi_labels.csv`: Step 3's file must stay the 300-unit sample its code checks, so the new marks are not appended to it |
| F2 | Which units are marked | every unit of the first 20 candidates of the primary gate order and of the control candidate that is not in `docs/funnel_emi_labels.csv` |
| F3 | Titles shown | up to 8 titles of the unit's assigned offers of its level, drawn with numpy default_rng(42), as in Step 3 |
| F4 | A candidate is EMI-field | any of its units marked yes or partly (old or new marks) |
| F5 | Check list | the EMI-field candidates of the first 20 that are not mixed and not below the minimum cohort, plus the control; every other candidate of the first 20 is named with its reason |

## Criteria

| # | Criterion | Target |
|---|---|---|
| G1 | Every unit of F2 has a mark | all |
| G2 | The sheet shows no type number, score, gate order or candidate name; groups shuffled | yes |
| G3 | Question and readings committed before the sheet is made | yes (git order) |
| G4 | The check list is computed by code from the marks, with a reason for every candidate of the first 20 left out | all 20 accounted for |
| G5 | Tests pass | all |
