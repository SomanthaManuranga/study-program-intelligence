# Criteria: rules version 4, R3-R8 (module marking under one standard)

Written and committed before any row is marked. Rules: `configs/funnel.yaml`, `version_4.marking`,
`version_4.person_check`, `version_4.verdict`; reader instructions `docs/funnel_marking_rules.md` (version 4).
Code: `analysis/funnel_mark4.py`.

## Exact readings (decided before the marks)

| # | Case | Reading |
|---|---|---|
| K1 | Which rows | every compulsory and elective module of every complete table in `data/interim/funnel4_refs/` of a candidate with a module check (`funnel4_check_list.csv`); thesis, internship and practical semester are left out (`feasibility_gate.references.module_kinds`) |
| K2 | The EMI catalogue | one entry per EMI module allowed for the level, copies of one module in several EMI handbooks once (`same_module`), numbered E001...; its ECTS is the largest of its copies; text as `funnel_feasibility.emi_text`, cut at 1,500 characters; timetable subjects without their form, numbered T001..., no lecturer |
| K3 | What a row shows | the module's title, ECTS and description (cut at 1,500 characters for every reference, also the version-3 tables), with institution, city, Land and module codes redacted; the 5 nearest EMI modules and up to 5 title matches with their catalogue number and text up to 3,000 characters; the 3 nearest timetable subjects; rows of all candidates shuffled together (seed 42) |
| K4 | Facts recorded | covered (E1, E2, no), covering (one or two E numbers), topic (an E or T number, or none), parent_field, lab, general (yes or no), unsure, reason |
| K5 | Topic of a covered row | its covering module(s) if the reader leaves it empty |
| K6 | Facts compared between readers (sample_pass, third reader) | covered or not; topic none or not none; parent_field; lab; general; and, for a row both call covered, whether the covering modules pass the size test. Which E numbers are named, and E1 against E2, are not compared |
| K7 | Size test | the covering modules' catalogue ECTS together are at least the module's ECTS |
| K8 | Consistency pass | pairs of rows from different references whose titles are equal after `title_merge.normalise`, or that share a content word of `title_words` with a topic on one side and none on the other; at most 120 pairs, the pairs with equal titles first, then by row number |
| K9 | Person-check sheet | `version_4.person_check`; rows of the candidates in the band under strict x content; English side by side; the persons record the same facts |

## Criteria

| # | Criterion | Target |
|---|---|---|
| W1 | Every row has all facts; every cited E or T number exists | 100 % |
| W2 | Readers blind: no candidate, institution, programme, similarity or earlier verdict on any sheet | yes |
| W3 | sample_pass per candidate (at most 1 of 10 drawn rows differs in a fact of K6), else the second reader marks all rows of it | per rule |
| W4 | Every row on which the first two readers differ in a fact of K6 has a third reader's facts | 100 % |
| W5 | Every consistency pair has the same facts or a written reason | 100 % |
| W6 | Every checked candidate reported under the four combinations (overlap, one-programme share, N, T, X, professor-equivalents, pass or fail) | all |
| W7 | A fresh reviewer recomputes the figures of 3 candidates from the final facts | no wrong number |
| W8 | Tests pass | all |
