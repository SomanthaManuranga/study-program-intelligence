# Criteria for funnel Step 7 (can EMI teach it with what it has?)

Written and committed before the Step 7 code is written. Step 7 applies the rule blocks `shortlist` and
`feasibility_gate` of `configs/funnel.yaml`. Nothing of Step 8 is computed.

| # | Criterion | Target | How it is checked |
|---|---|---|---|
| F1 | Code and rules before results | the marking rules and the changed checking rule are committed before the shortlist is made; the code is committed before it runs; outputs carry the commit and the hashes of their inputs | `git log`, output header |
| F2 | The gate list comes from the rule, not from us | pre-gate score from the value functions and weights of the rule; one representative per merged candidate; the order is never edited by hand; a mixed type is read in full before it takes a slot | test: scores recomputed; reviewer |
| F3 | References by the rule | the offer nearest the type's centroid among full-time offers at universities of applied sciences other than OTH; up to 5 tries per reference; a second reference from another institution; every try and every reason for a miss is recorded; robots.txt respected for every host | reference log, reviewer |
| F4 | Complete references only | a reference lists modules for at least 80 % of the programme's ECTS; thesis, internship and practical semester left out of the count | test on the module tables |
| F5 | Marking is blind and rule-bound | rows show the module, the EMI modules the rule names (5 nearest plus title matches) and 3 nearest timetable subjects in shuffled order, without candidate, institution, title, rank or similarity value; the marker has seen none of this project's results | sheet check by test; reviewer |
| F6 | The check of the marks is run as the changed rule says | a second, independent AI reviewer marks 10 drawn rows per candidate, every "unsure" row and every row of a candidate within 0.10 of a band end, without seeing the first verdicts; with 2 or more changes between covered and not covered among the 10, all rows of the candidate are marked again; a third reader, blind to both, settles every row on which the two differ | marks files, test |
| F7 | Overlap, one-programme share, new teaching and verdicts as the rule says | recomputed from the marks for every eligible candidate | test; reviewer recomputes |
| F8 | Stop rule kept | the list stops at 6 eligible candidates or 20 tried; at most 3 eligible per level | gate log |
| F9 | Internal data stay internal | no lecturer name in any committed file or output shown; timetable subjects appear only as subject names | grep, reviewer |
| F10 | Reproducible | the shortlist and the verdict table are the same in a second run from the stored marks | comparison |
| F11 | Reviewed | a fresh-context reviewer compares code and rule, recomputes the numbers and checks the notes; no open blocker, no wrong number | reviewer |
| F12 | The repository works | `python -m pytest` passes completely | test run |

Stated in the notes whatever the result: no person has checked the AI markers' rows (Soma decided against a hand
check); the automatic overlap is shown next to the marked one. If a criterion still
fails after 3 rounds, the step stops and Soma is told. No criterion is loosened.
