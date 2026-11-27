# Criteria for funnel Step 0 (rules, version 3)

Written and committed before the rules are rewritten. Step 0 touches no data and runs no analysis code.

| # | Criterion | Target | How it is checked |
|---|---|---|---|
| C1 | Every problem in `docs/funnel_run1_review.md` has a rule that prevents it | 14 of 14 (R1-R8 and the six "other problems") | table in `docs/funnel_preregistration.md`, checked by the reviewer |
| C2 | Every point the supervisor made (meeting and email) maps to a rule or to "no change" | 9 of 9 | table in `docs/funnel_preregistration.md`, checked by the reviewer against the transcript |
| C3 | Every number in `configs/funnel.yaml` names its origin: supervisor, literature, carried over, or own judgement | 100 %; every own-judgement number has a stress range | reviewer lists numbers without an origin |
| C4 | Every rule names the public data it needs, or its fallback if the data cannot be had | 0 rules without a data path | reviewer |
| C5 | No result is produced or read in this step | only `configs/`, `docs/` and `CLAUDE.md` change; no file under `data/` or `reports/` is opened | `git diff --stat`, session record |
| C6 | Rules are unambiguous: two people implementing them would get the same candidate list | 0 open blockers after at most 3 review rounds | fresh-context reviewer; a blocker is a rule that leaves a choice open or can be decided after seeing results |
| C7 | Prior knowledge is declared | the pre-registration lists what was known from run 1 and which rules were written knowing a run-1 number | reviewer |
| C8 | Internal timetable data is protected | no lecturer name and no timetable file in the repository | search of the diff for the surnames in the timetables |
| C9 | The repository still works | `python -m pytest` passes; `configs/funnel.yaml` parses | test run |

If a criterion still fails after 3 rounds, the step stops and Soma is told. No criterion is loosened.
