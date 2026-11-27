# Funnel (Steps 0-8): independent re-check, 27 Nov 2026

Three independent checks of the funnel result on `soma/funnel` (commit 3e05b90): one of the result tables, one of the
Step 7 module marking (fresh reviewer), one of the rule-change history in git (fresh reviewer). Nothing in the
pipeline was changed.

## Verdict

- **The arithmetic is correct.** Every figure the reviewers recomputed matches the result tables.
- **One statement holds:** an Informatik bachelor overlaps with EMI's existing teaching by roughly 49-68 %, inside
  the 40-80 % band, on two handbooks.
- **Four statements are not established:** that it is the *only* programme EMI can run, that it attracts the *most*
  students, that about *26* first-years would be new to OTH, and that the result was reached *without bias*.

## Loopholes, most serious first

### 1. Only two EMI-relevant bachelors were compared

- The module check took 3 bachelors in gate order: computer science, urban planning, cybersecurity.
- Skipped because "3 are eligible already": Informatik (order 4), Elektrotechnik (5), data science and business
  analytics (8, modelled net-new 54.8), software engineering (9), automation and robotics (38), Angewandte
  Informatik (40, net-new 31.7).
- "The only candidate that passes" therefore means 1 of 2 plausible candidates tested, out of 268.
- The project's own Ingolstadt check shows a second type (242) would pass too.
- Source: `results/step7_feasibility/gate_walk.csv`, `gate_order.csv`.

### 2. The split between computer science and cybersecurity comes from inconsistent marking

- Computer science passes because its "beyond existing staff" figure (X) is 0; cybersecurity fails with X of 3 and 10.
- The same topic got opposite verdicts: Penetration Testing is "N" (a current lecturer can write it) in one
  cybersecurity handbook (R0143) and "new" in the other (R0131). EMI's own module Informationssicherheit lists
  penetration testing.
- The verdict followed which EMI modules the sheet happened to show: 19 of 21 security rows shown next to
  Informationssicherheit are N; all 7 shown with no security module are "new".
- Computer science rows got the lenient standard: Stochastic Algorithms (R0349) and Simulation (R0303) are N
  although no EMI text has the content.
- Under one consistent standard, either both candidates pass or neither does:

| Standard | Computer science N / T / X | Cyber a | Cyber b | Passers |
|---|---|---|---|---|
| As marked | 50.5 / 2 / 0 | 47.8 / 10 / 3.0 | 50 / 10 / 10 | computer science only |
| Lenient everywhere (N if EMI teaches the parent field) | 50.5 / 2 / 0 | 54.1 / 6.7 / 0 | 65 / 5 / 0 | all |
| Strict everywhere (N only if an EMI text has the topic) | 40.5 / 10 / 2 | unchanged | unchanged | none |

- Cyber a's X of 3 is the pro-rata share of 7 electives (4 of them business) in a 293-ECTS catalogue.
- N against "new" is decided by the AI label alone; the code makes no timetable or lecturer check for it.

### 3. The decisive rules were set after the result they produce was known

- Run 1 (7 Nov) already showed an Informatik bachelor as the only gate passer. The rules of version 3 (14 Nov) then
  replaced the strict gate (80 % covered, cap on new modules) by the 40-80 % band with no cap on new modules.
- Marking rule version 3 (a8da729, 15 Nov 22:29) was set 15 minutes after the notes recorded (57ed695, 22:14) that
  "if size counts, no bachelor passes". Overlap moved 46 % to 68 %, new teaching 89 to 52.5 ECTS.
- About 24 rules or procedures changed after a result was seen; 9 helped or protected the result, none hurt it.
- Every human check was removed on the way (Soma's 10 rows per candidate, the team member's blind repetition, the
  100 "similar" offers). All module judgements come from one AI model.
- Sound: no history rewriting; the Step 8 decision rule pre-dates the run-2 Step 7 result; all three marking passes
  are kept; the notes disclose most changes.

### 4. The recommended "type" is an artefact of the grouping

- Type 312 "Computer Science" has 11 members, 3 of them bachelors: Hof, OTH Regensburg (international), and one
  DHBW cyber offer. It is mid-sized, not stability-tested, and exists only through a rule changed after Step 2.
- Same field, different scores:

| | Type 312 "Computer Science" | Type 13 "Informatik" (63 members, stable) |
|---|---|---|
| Similar offers within 150 km | 2 | 30 |
| Differentiation value | 4.2 | 1.0 |
| Job keyword measure (ads within 100 km) | 359 | 0 ("informatik dual" is the median keyword) |
| Labour value | 5.0 | 1.0 |
| Scale in the capture model | 1.11 | 0.68 |
| Gross first-years | 33.9 | 20.9 |

- Counted over the Informatik types together there are 12 general Informatik bachelors at 8 institutions within
  100 km, 32 within 150 km.
- In the two-candidate comparison, cybersecurity comes first when Informatik is measured as type 13.

### 5. "26 new to OTH" is not measured

- The share taken from OTH (22 %) comes from the distance model with the nearest OTH offer as a stand-in; the notes
  say incrementality is not measured.
- The proposed curriculum is the shared core of Medieninformatik, Industrie-4.0-Informatik and the KI bachelors
  (57 %, 54 % and 47 % of its ECTS) plus about 37 ECTS of new computer science content.
- Break-even: measured as real Informatik (gross 20.9 to 23.2) the result falls below the bar of 15 if more than
  28-35 % of the students come from OTH's existing programmes.
- The range of 7 to 88 already includes values below the bar.

### 6. The overlap figure is unstable

- Same handbook: 44 % (pass 1), 46 % (pass 2), 68 % (pass 3), 49 % (reviewer's corrections); the automatic measure
  says 4 %.
- 11.5 of the 50.5 "new modules by current lecturers" ECTS are Spanish courses; 7 points of the overlap are language
  courses counted through EMI's foreign-language slot.
- 47 points of the 68 rest on a single reader.
- Fresh reviewer's estimate: low 49 %, middle 57 %, high 68 %. The band pass holds in all three.

### 7. The README overstates

- "final after the 4 Dec 2026 data freeze": the freeze has not happened; the word "preliminary" was dropped.
- "the only candidate the faculty can run": see 1 and 2.
- "first in 82 % of draws": two candidates, information only, reverses as type 13.
- "17.9 million stress combinations": 22 % is 2 of 9 combinations of two factors.
- Failed checks not in the README: Step 2 reader check (22 of 30, bar 24), Step 3 coherence (70 %, bar 80 %),
  Step 1b threshold (AUC 0.63), 7 stress values not run.
- Whether existing staff have the hours for about 1.2 professor-equivalents is unknown.

## What a fair rerun needs

1. One Informatik candidate: merge types 312, 13, 242, 203, 268 and measure competition, jobs and first-years on it.
2. Module check for every EMI-field candidate near the top, not 3 per level: at least Informatik, cybersecurity,
   data science, software engineering, automation and robotics.
3. One written standard for "a current lecturer can write it", the same EMI modules shown for the same topic, and
   a person (Soma and the second team member) deciding the rows that carry T and X.
4. Overlap reported as a range under both readings of module size, not one figure.
5. "New to OTH" reported as scenarios with the break-even share, not one number.
6. The supervisor confirms three rules in writing: the 40-80 % band, uncapped new modules by current lecturers, and
   two EMI modules covering one.
7. README and explainer corrected to what is established.
