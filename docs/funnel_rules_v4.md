# Funnel rules version 4 (approved by Soma; nothing rerun yet)

Why: the independent re-check (`docs/funnel_recheck.md`) found seven loopholes. Soma decided three points
(`docs/decision_log.md`, 27 Nov): check every EMI-field candidate near the top, mark so that a strict and a lenient
reading can both be computed, and a person check of the rows that decide outside teaching. This draft turns those
decisions, and the other fixes the re-check asks for, into rules. Soma approved it as drafted (top-20 cut and R10
as proposed). The rules are in
`configs/funnel.yaml` (version 4) and `docs/funnel_marking_rules.md` (version 4) and are committed **before** any
step runs again. After that, a rule changed after a result is seen is a deviation: the result is then reported under
both the old and the new value, never the new one alone.

## The changes

| # | Fixes | Rule now (v3) | Rule proposed (v4) | Steps rerun |
|---|---|---|---|---|
| R1 | 4, 5 | Types are candidates as the clustering found them; Informatik is split into 312 "Computer Science", 13, 242 (+268, 294), 203 | **One candidate per programme title.** Units of one level are merged when the main title of their types is the same after a written normalisation: lower case; English to German by the word groups of Step 7 (computer science = informatik, electrical engineering = elektrotechnik, ...); the words *dual, international, allgemeine / general, angewandte / applied, berufsbegleitend, praxisintegriert* and degree names removed. Competition = the union of the merged types' similar offers; jobs = the keywords of all merged types; first-years = Step 6 run on the merged pool and sites. Applies to every unit, not only Informatik | 3 (merge only), 5 (measure only), 6, 7a |
| R2 | 1 | Module check for the first 3 eligible bachelors and 3 masters, at most 20 tried | **Every EMI-field candidate among the first 20 of the gate order gets a module check**, no cap per level. EMI-field = marked "yes" or "partly" by a fresh reader from titles only, by the marking rules of Step 3 (`docs/funnel_emi_labels.csv`); units already marked keep their mark. Non-EMI candidates are not checked and are named. Note: in the current order Angewandte Informatik (40) and automation and robotics (38) lie outside the first 20; R1 merges Angewandte Informatik into Informatik, but automation and robotics stays outside unless the merged order moves it up. **Soma decided: keep "first 20"** | 7 |
| R3 | 2 | The reader sees the 5 nearest EMI modules + up to 5 title matches; N if a current lecturer "already teaches the topic" | **Same EMI material for every row.** Besides the nearest modules, every reader gets the whole list of EMI modules allowed for the level (id, title, ECTS, text) and the timetable subject list, and may cite any of them. The reader records facts, not a verdict: (a) covered or not, with the id(s) of the covering EMI module(s); (b) if not covered: the id of an EMI module or timetable subject whose text has the module's main topic, or "none"; (c) whether EMI teaches the parent field (computing, electrical engineering, media). The code turns these facts into verdicts | 7 (all rows marked again) |
| R4 | 2 | One standard (as applied, inconsistently) | **Two readings, both reported.** Strict: N only if (b) names an EMI module or timetable subject. Lenient: N also if (b) is "none" and (c) is yes. Each candidate is reported as passing under strict, lenient, both or neither | 7, 8 |
| R5 | 6 | Content counts; two EMI modules may cover one (v3) | **Overlap as a range under both readings of module size.** Content reading: as v3. Size reading: a row counts as covered only if the covering EMI modules together have at least the module's ECTS. Both figures reported for every candidate; the band test is reported under each | 7, 8 |
| R6 | 6 | Language courses marked like any module (Spanish counted as N) | **Language and general-studies modules** (foreign languages, Studium generale, soft skills) are never N or X: they are reported separately and counted in one reading as covered by OTH's existing language offer and in the other left out of the taught ECTS | 7 |
| R7 | 2 | No check that the same topic gets the same verdict | **Consistency pass.** Rows of different handbooks with the same normalised module title (or the same main topic named in (b)) must get the same facts; a difference goes to the third reader, who sees both rows side by side | 7 |
| R8 | 2, 3 | No person checks a row (Soma, 15 Nov) | **Person check of the deciding rows.** Soma and the second team member each mark, blind to the AI and to each other, every row that is new (T or X) under strict x size or lab, plus 5 covered or N rows per candidate, for every candidate in the band; on an English side-by-side sheet (module text, the EMI text cited, the question). Disagreements are settled by the two together; their verdict replaces the AI's. If more than 40 rows qualify, the rows of the top 3 candidates in gate order come first and the rest stay AI-only (stated) | 7 |
| R9 | 5 | One net-new figure (share from OTH by the distance model) | **"New to OTH" as scenarios.** Net-new at the model's share, at 35 % and at 50 % taken from OTH, plus the break-even share at which net-new falls below 15. The decision rule "one passer: net-new at least 15" is stated with its break-even share | 6, 8 |
| R10 | 3 | Decision from the existing-resources passers | **Confirmed by Soma:** a candidate is a **firm** existing-resources passer only if it passes under the strict marking **and** the size reading; it is a **conditional** passer if it passes only under the lenient marking or the content reading, with the condition named (e.g. "the faculty accepts N new modules on topics no current lecturer teaches today"). The recommendation is taken from firm passers. If there is none, the decision says so and ranks the conditional passers with their conditions | 8 |

Unchanged: the 40-80 % band and its reading, labs, minimum cohort 20, weights, value functions, Monte Carlo, the
stress grid, public data only, robots.txt, internal timetables outside the repository.

## Still needed from outside

- **Supervisor, in writing:** the 40-80 % reading (lower end on all EMI modules, upper end on one programme),
  uncapped new modules by current lecturers, and two EMI modules covering one. Without it, these three stay stated
  assumptions in the report.

## Made exact after a fresh review

A fresh reviewer read the approved draft against the rest of the rules and found 26 places where two people could
apply it differently, or where it contradicted version 3. The wording in `configs/funnel.yaml` (`version_4`) is the
binding text. Most changes only make the draft exact (normalisation, one hop of linkage, the first 20 counted before
exclusions, the four combinations, T and X restated, the order of the checking passes). Four go a little further and
are shown to Soma with the commit:

- **at OTH:** a candidate is dropped as a whole only if one of its title-matched units is at OTH (OTH already has a
  programme of that title), so an Elektrotechnik bachelor drops if OTH's electrical programme normalises to the same
  title; linked units drop singly as in version 3.
- **Person check in both directions:** besides the new / lab rows, 5 rows per candidate drawn from its covered or N
  rows, so the persons can also move rows towards failing; the sheet shows no AI citations.
- **If the supervisor rejects a point:** the stricter reading becomes primary (both ends on all EMI modules; the size
  reading; an N cap of 10 / 5 ECTS); an answer after the freeze is a sensitivity only.
- **New to OTH:** the scenarios are reported, but the ranking and the decision keep the model's share (stated as a
  limit).

Not taken: making strict N require a timetable subject (version 3's N); Soma's decision names "an EMI module or
timetable subject", so that stays.

## Order and time (freeze 4 Dec 2026)

| Order | Step | Who | Days | Fits before 4 Dec? |
|---|---|---|---|---|
| 1 | Rules v4 committed | Claude, Soma | 0.5 | yes |
| 2 | R1 merge; Steps 5, 6 and the gate order again; R9 scenarios | Claude | 1 | yes |
| 3 | R2 EMI-field marks for the top 20; reference handbooks for the new candidates (robots.txt) | Claude | 1 | yes, if handbooks are public |
| 4 | R3-R7 marking of all rows of all checked candidates (about 10 candidates, about 1,000 rows) by blind AI readers | Claude (agents) | 1.5 | tight |
| 5 | R8 person check (up to 40 rows) | Soma + teammate | 0.5 | depends on the team |
| 6 | Step 8 again; notes, README, explainer, notebook, results | Claude | 1 | tight |

If a step does not finish by 4 Dec, the report states it as a limitation: steps 4-6 open means "only two EMI
bachelors were compared; marking inconsistent; no person checked a row".

## Criteria for the rerun (written before it runs)

| # | Criterion | Target |
|---|---|---|
| V1 | Merge rule applied to every unit by code; the merged groups listed | 100 % by code, none by hand |
| V2 | Every EMI-field candidate among the first 20 has a module check, or is named with the reason it could not be checked (no public handbook) | all |
| V3 | Every row has all facts of `version_4.marking.facts_per_row`; every cited number exists | 100 % |
| V4 | Every pair sent to the consistency pass has the same facts or a written reason | 100 % |
| V5 | Each candidate's verdict reported under strict / lenient and content / size | all four |
| V6 | Person check done on every qualifying row (or the cut named) | all, or the cut named |
| V7 | Net-new reported with the break-even share for every band passer | all |
| V8 | Fresh-context reviewer recomputes every number in the notes | no wrong number left |
| V9 | All tests pass | all |
