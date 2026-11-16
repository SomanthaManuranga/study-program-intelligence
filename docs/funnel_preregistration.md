# Funnel pre-registration, version 3: the programme comes out of the analysis

Rules: `configs/funnel.yaml` (version 3), committed before any run-2 code runs. Pass criteria for this step:
`docs/criteria_funnel_rules.md`. Run 1 is not a result (`docs/funnel_run1_review.md`); earlier results stay as a
baseline and are not inputs. Method background: research report "Data driven study programme discovery".

## The rules at a glance

| Step | Question | Rule in one sentence |
|---|---|---|
| 0 | Which rules decide? | Everything below is fixed before any data is touched. |
| 1 | Is the data there and current? | Every source is listed with its date, size and gaps; missing public data is downloaded or named as a limit. |
| 2 | What kinds of programme exist? | All full-time bachelor and master offers in Germany are grouped by their text; no topic list is written by hand. |
| 3 | Which types are open to OTH and in EMI's field? | A type goes out if OTH already has it, if it is mainly teacher training, if its German student pool in Bavaria shrinks by more than 3 % a year on a trend that has predicted well, or if it lies outside what EMI teaches. Competition is counted by content similarity and is not a cut. |
| 4 | Are students coming? | The trend of German first-years in the matching subjects in Bavaria, with a backtest that says whether the trend can be trusted. |
| 5 | Are there jobs nearby? | Job ads within 100 km for keywords taken from the type's own programme titles. |
| 6 | How many students would be new to OTH? | A location model gives low, central and high first-years and subtracts those taken from OTH's own programmes; a central value under 20 drops the candidate. |
| 7 | Can EMI teach it? | Two real curricula per candidate: at least 40 % of the credits must be covered by modules EMI already teaches, and at most 80 % may come from one existing programme. Soma checks every module of the short list by hand. |
| 8 | Which one, and how sure are we? | Weighted ranking with uncertainty and stress tests; the recommendation comes only from candidates existing staff and labs can carry. |

## What the supervisor said and the rule it becomes

| # | Supervisor (meeting, email) | Rule |
|---|---|---|
| 1 | An entire new degree programme, not extra modules; not already at OTH | `universe.new_programme_only`, `screen.at_oth` |
| 2 | Bachelor or master | both levels; no change |
| 3 | Overlap with existing lectures of 40-80 % is ideal; more is a relabelled programme, less costs too many resources (email, replacing the 50-80 % of the meeting) | `feasibility_gate.band`, `band_reading`: at least 40 % overlap with all EMI modules, at most 80 % from one existing programme (Soma, as the supervisor's meaning). Only existing facilities count: `verdict.existing_resources_passer`, `labs` |
| 4 | Asked for a minimum cohort, he gave none: assume students come and argue why | `capture.min_cohort` stays 20 as the project's own assumption. It is also run at 25, and at 15 and without any minimum up to the pre-gate ranking, to show how the candidate list changes |
| 5 | Need not be unique in Germany; other countries are fine as inspiration | competition is measured, not a cut (`screen.competition`); the catalogue covers Germany only, so programmes that exist only abroad are a stated limit |
| 6 | Valid arguments: unique in Germany, or only a few similar programmes elsewhere (north) that attract many students, with nothing comparable in the south | `screen.regional_gap`: flags for "absent in Bavaria" and "none in the south", a Bavarian quotient, and how well the popularity elsewhere is shown (three tiers) |
| 7 | No student numbers per course; lecture timetables are provided | `feasibility_gate.hand_check.N` (who already teaches the topic), `timetable_confirmation`, `internal_data` |
| 8 | Sources: other universities' websites and handbooks, Destatis, plus those in use | no change; reference curricula come from other universities' handbooks |
| 9 | The chain of reasoning and the documentation are what count | `conformance.steps_stop`: short notes per step; the full documentation is written at the end |

## How each run-1 problem is prevented

| Problem (`docs/funnel_run1_review.md`) | Rule |
|---|---|
| R1 boilerplate left in 41 offer texts | `text.dropped`, `text.normalise`, `text.boilerplate_scan`, `text.check` (the run stops) |
| R2 only 15 of 18 old lists tested | `discovery.validation.old_lists`: all 18, untestable ones named |
| R3 stress list never run | `freeze.both_lists`, `freeze.stress_list_use` |
| R4 OTH modelled as one fixed Amberg site | `capture.oth_sites`: assigned OTH offers at their own city |
| R5 each pool's own best model | `demand.pools`, `demand.validated`, `demand.model_choice`: one stated rule for all pools |
| R6 weak job-ad measure | `labour.regions` (every keyword in every region), `labour.english`, `labour.stored_first` |
| R7 w labels inverted; unstated scale default | `capture.w_substitute` named by effect; `capture.scale.without` stated and flagged |
| R8 unscaled figure missing; variants not merged in supply | `feasibility_gate.references.scaling`; `universe.counted_as_supply` |
| Supply test not valid (cluster membership) | `similarity.similar_offer`; `screen.competition.validity_check` with a pass rule and a fallback |
| Generic job-ad keywords | `labour.phrases`, `drop_generic`, `keywords`, `strike_only_review`, `measure` (median, not the largest) |
| Level check passed only because Saarland counted twice | `capture.level_check`: one row per programme, reported only; no correction factor |
| Old-list recovery statement did not hold | `discovery.validation.wording`: counts only, both offer sets side by side |
| Frozen list came from code changed after the commit | `freeze.record`, `conformance.code_first` |
| Three thresholds added after the types were computed | now rules: `references.complete`, `screen.teacher_training`, `shortlist.fit_proxy` (marked [K]) |

## What was known before version 3

The analysis cannot be blind, so the prior knowledge is stated.

- Earlier rounds screened 18 topic groups and six hand-picked candidates. Cybersecurity came first with investment;
  robotics path B was closest under existing resources. Under the project's former strict rule no candidate passed.
- Run 1 of the funnel produced types, a candidate list and gate results. Soma and the earlier session saw them.
- Version 3 was written from the review file, the code and the supervisor's input. The run-1 reasoning text, type
  list, candidate list and gate tables were not opened while writing it.
- Run-1 facts known when writing, from the review file: the boilerplate type; "Informatik dual" showing 0 offers
  within 100 km against 15 informatics bachelors; only the cybersecurity job count was on topic; the level check
  failed with Saarland once (median error about 0.54, implied factor about 1.74 upward); the pooled best model was
  naive, with 101 validated drops; AI/data and mobility/vehicle were recovered on full-time offers; second
  references removed two automatic passers; 27 mainly teacher-training candidates had been excluded.

Rules written knowing a run-1 number (marked [K] in the yaml), with the direction of the choice:

| Rule | What was known | Direction of the choice |
|---|---|---|
| `capture.level_check`, `capture.gross` | the old rule would multiply every candidate by about 1.74 | No upward factor from four values of one subject. Every candidate gets the wide range instead. This lowers nobody's rank but leaves the level uncertain. |
| `demand.validated` | with the naive model 101 units were dropped | A trend now counts only if extrapolating it has beaten "no change". Fewer units are dropped, so more candidates stay in. |
| `screen.teacher_training` | 27 candidates were excluded at a share of 0.5 | Same number as the run-1 deviation; run at 0.3 and 0.7; the types stay in the stress list. |
| `shortlist.fit_proxy` | the anchor was added during run 1 | Unchanged; it only orders the gate list. |
| `references.complete` | fixed before the run-1 gate ran, after the types | Unchanged. |
| `references.electives` | "best covered first" raised overlap | Changed to the mean coverage of the electives, because the band now has an upper end; both extremes are reported. |
| `references.two` | second references removed two run-1 passers | A second reference is required; this makes passing harder. |
| `capture.scale.without` | 75 of 143 run-1 candidates used the silent default | Default kept at 1.0, now stated and flagged. |
| `feasibility_gate.covered_threshold` | the former value 0.285 came from the baseline's cybersecurity and robotics references | Calibrated again on EMI's own handbooks only, with the procedure committed before the value was seen (0.463, flagged weak). The higher value makes the automatic match stricter for every candidate and does not carry over to handbooks of other universities; 0.285 stays as a stress value. Neither value decides which candidates reach the hand check: Soma settled that no threshold decides (`eligible`, `hand_check.first_marking`, `sample_check`). |
| `one_programme.max` | run-1 gate tables held one-programme shares (not opened) | Set to the band's upper end of 0.80 after Soma's answer on the supervisor's meaning; this is easier to pass than the former 0.50, which stays as a stress value. |
| Supply cut removed from the primary list | the cut by cluster membership was invalid | The supervisor's point 5 is the reason; the cut stays as a stress test on the corrected unit. |
| `discovery.validation.old_lists` | full-time offers recover more old lists | Both offer sets are reported side by side; neither is called primary. |
| `feasibility_gate.band` | under the former rule no candidate passed | The band is the supervisor's number. The former rule is kept as a stress spec, and the recommendation comes only from candidates existing staff and labs can carry. |

Cyber and robotics are old hypotheses. They get no special treatment and count only if they come out of the funnel.

## Data each step needs

| Step | Data | Source | If it cannot be had |
|---|---|---|---|
| 2, 3 | all bachelor and master offers with title, focus items, subject labels, place, form, institution type | BA Studiensuche catalogue (already downloaded) | - |
| 3 | EMI modules; OTH offers | OTH module handbooks, catalogue | - |
| 3, 4, 6 | first-years and graduates by subject, German and foreign, Bavaria and Germany | Destatis GENESIS 21311-0012/-0015, 21321-0003/-0006 | - |
| 3 | first-years by subject for the other Laender | Destatis GENESIS 21311-0015 per Land | popularity tier 2 cannot be shown; units fall to tier 3; stated |
| 5 | job-ad counts for the new keywords | BA Jobsuche, one day's counts (no history for new keywords) | asked again the next day; then a missing input |
| 5 | language of instruction per offer | catalogue field, if it exists | no English pairing; stated |
| 6 | school leavers by county (bachelor); students at Bavarian universities of applied sciences by campus (master) | Bavarian statistics, as in the baseline capture model | - |
| 6 | published first-year numbers of single programmes | the 3 documents already collected and the two baseline anchors | level check reported as it is; no correction either way |
| 7 | handbooks of two reference programmes per candidate | other universities' websites under robots.txt | next nearest offer, up to 5 tries; then single reference or no reference |
| 7 | EMI timetables, summer 2026 and winter 2026/27 | provided by the supervisor (internal) | - |
| 7 | published first-year numbers of similar programmes outside the south | university statistics pages under robots.txt | popularity tier 1 cannot be shown; stated |

The stress list adds keywords and requests in Step 5; they run in the background at the same delay. The timetables
are the one internal source. They stay outside the repository; lecturers appear only as neutral labels. No intake or
admission figures from OTH are used.

## Notes at every step

Each step ends with short notes in `docs/funnel_run2_notes.md`: the question, the rule applied, the numbers, what
was dropped and why, and the strongest objection. Every candidate keeps one line per step, so the final answer can
be traced back. The full documentation is written after Step 8.

## Judgement calls, open questions and limits

- **Own numbers without a literature anchor** carry [J] or [C] in the yaml, and every [J] number names its stress
  values. Numbers marked [N] have none, because another value would need another manual check: the samples of the
  competition check (10 units, 5 offers each side) and its pass rule (70 % / 30 %), the 10 rows per candidate of Soma's
  sample check and its pass rule (at most 1 of 10), the 3 EMI modules and 3 timetable subjects shown per row, the 2 published numbers of popularity tier 1, the
  10 stress-only units that are named, the one candidate per level for the second rater, and the 0.10 widening
  after a low kappa. Two of these can change a candidate's numbers: the pass rule of the competition check (it
  decides which radius is in force) and the pass rule of the sample check. Also without a stress value: the two thresholds of the
  PROMETHEE cross-check, and four [K] numbers (the 90th percentile of the fit proxy, the 80 % completeness of a
  reference, "MASE below 1", and the scale of 1.0 without a Bavarian comparator).
- **Settled by Soma after the first review of these rules** (to be shown to the supervisor at the next progress
  meeting): (1) only the university's existing facilities count. The recommendation is taken only from
  candidates whose new modules lie on topics a current lecturer already teaches (apart from a small part for
  teaching assignments) and that need no new lab. The best candidate that needs new expertise is reported for
  information, never as a recommendation. The amount of new modules by current lecturers is not capped; caps of
  10 and 20 ECTS are stress specs, and the recommendation states the professor-equivalents. (2) "Too much
  overlap" means a relabelled copy of one existing programme: the 80 % end applies to the share from one
  programme, the 40 % end to the overlap with all EMI modules. The reading with both ends on all EMI modules and
  the former 50 % limit per programme (kill rule 1) are stress specs. (3) After Step 1b: no similarity threshold
  decides a module match. A fresh-context reviewer (an AI agent) marks every row from the module texts by marking
  rules written first; Soma checks 10 rows per candidate and every row the reviewer is unsure about, and marks all
  rows of a candidate whose sample fails. The second team member's blind repetition stays.
  Changed before Step 7 (Soma, 15 Nov 2026): Soma does no hand work, so the sample check is done by a second AI
  reviewer who does not see the first verdicts; a third reader settles a candidate whose sample fails. No person
  has then checked a module verdict.
- **Changed after Step 2's first result (Soma, 14 Nov 2026).** The types of the pre-registered selection rule were
  too broad: 17 of 30 held one kind of programme in the reader's check, the bar was 24. No type had been screened or
  scored at that point. Three rules changed (the first two are marked [K] in the yaml, the third carries Soma's dated
  comment): the finest setting of the grid is used
  (`discovery.selection`; the former rule's setting is a stress spec); left-over groups too large for the rare path
  are kept as mid-sized types with a flag (`rare_path.larger_groups`); and every type that survives the Step 3
  screen is read for coherence, a failing type is flagged "mixed" and cannot take a gate slot without a full
  reading (`screen.type_coherence`). The finest setting was chosen by the reader's check alone (21 of 30, still
  below the bar), not by any candidate.
- **Hours of existing staff** cannot be known from public data. Every candidate reports its new teaching in ECTS
  and professor-equivalents; whether the faculty can absorb it is the faculty's answer.
- **Demand is measured per subject, not per programme type.** Two candidates in the same Destatis subject share a
  trend and a level and differ only through competition and location.
- **Popularity elsewhere** rests on subject-level statistics by Land and a few published programme numbers. No
  public source gives first-years per programme across Germany.
- **Deviations from the research design:** no ESCO skill linking (the job source gives counts only); the Huff model
  is reused instead of a nested logit with travel times; the encoder is the project's cached one, with TF-IDF and a
  hand-labelled sample as the checks.
- **Limit:** a programme offered nowhere in Germany cannot be found from a catalogue of German offers.
- **Agents:** fresh-context agents review rules, code and claims, and one makes the first marking of the module
  rows in Step 7. An agent is not a human rater: its marks are checked by a second, blind agent (changed on 15 Nov
  2026, see above), and it never replaces the second team member's check.

## Review record of this step

A fresh-context reviewer attacked the rules in three rounds, blind to all run-1 results: 11 blockers and 10 major
points in round 1, 9 blockers and 5 major points in round 2, 3 blockers in round 3. All were reworded as proposed.
The last three rewordings (the draw of the manual-check samples, the widening of the value anchors, the pass rule
of the second overlap reading) were not reviewed again. Criterion C3 fails on its wording: the numbers listed above
have no stress value. Criterion C9 fails on one test that predates this step (`tests/test_tie_break.py`). Soma accepted
the step with these two exceptions. The two points settled by Soma were written in after the review rounds and
before any run-2 code ran.
