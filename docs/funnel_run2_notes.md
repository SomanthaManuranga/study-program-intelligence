# Funnel rerun: notes per step

Short notes on what each step found and why each programme stays or goes. Rules: `configs/funnel.yaml`. Generated
tables: `reports/funnel2/` (not committed). The full documentation is written after Step 8.

## Step 0: which rules decide?

All rules and thresholds are fixed in `configs/funnel.yaml` before any data is touched. They hold the supervisor's
answers and a fix for each problem of run 1 (`docs/funnel_preregistration.md`). No programme was looked at.

## Step 1: is the data there and current?

**Question.** Does every rule have the data it needs, how old is it, and what is missing?

**Rule.** Data table in `docs/funnel_preregistration.md`; criteria in `docs/criteria_funnel_step1.md`. Inventory run
on 14 Nov 2026 with code commit 8fddcb2; tracked files were clean.

**What is there** (one row per line of the pre-registered data table).

| Source | Size | Period or date | Gaps |
|---|---|---|---|
| Study catalogue | 22,093 offers; 19,872 bachelor and master offers in Germany after merging variants (9,703 bachelor, 10,169 master), 14,902 of them full-time, at 404 institutions; 90 study fields; 396 subject labels, all with a Destatis code | retrieved 19 Oct 2026 | 10,184 offers carry the phrase "Inhalte bitte bei der Hochschule erfragen"; 10,139 have no content left once the phrase and the university's note are dropped; focus items exist for 48 %; 1 offer without a Land |
| EMI modules and OTH offers | 447 module rows (293 distinct titles; 333 bachelor, 114 master rows) from 14 handbook sets; 46 OTH offers in the catalogue; 23 labs listed | handbooks retrieved 19 Oct 2026 | 38 modules without ECTS; 1 of 15 EMI programmes has no handbook set (Ingenieurpaedagogik, which is phasing out) |
| First-years and graduates by subject, Bavaria and Germany | 4 tables, 297 subjects each | 2005-2025, retrieved 14 Oct 2026 | none |
| First-years by subject, other Laender | 15 of 15 Laender, 297 subjects each | 2018-2025, retrieved 14 Nov 2026 | none |
| Job ads | 3 snapshots: 48 counts for 12 keywords on 15 Oct and on 17 Oct, 92 counts for 23 keywords on 7 Nov 2026 | day counts | the keywords of Step 5 are new and have no history; they are counted on one day |
| Language of instruction per offer | no such field in the catalogue | - | German and English keywords cannot be paired by rule (`labour.english`) |
| School leavers by county | 96 counties | 2014-2024 | 2019 is missing |
| Students by campus (master origins) | 17 campuses, 83,481 students | winter 2024/25 | none |
| Published first-year numbers of single programmes (level check) | 3 documents from 2 universities, plus the two baseline anchors | 2024, winter 2024/25, winter 2025/26 | one subject only; the rows per programme are built in Step 6 |
| Reference handbooks of other universities | 27 files left from run 1, counted and not opened | - | collected again in Step 7 |
| EMI timetables (internal) | 80 group plans (40 per semester), 1,028 timetable entries (494 distinct sessions, because a session shared by several groups appears once per group), 314 subject names, 98 lecturers as labels | summer 2026 (plan printed 20 Jan 2026), winter 2026/27 (printed 22 Sep 2026) | no ECTS, no hours, no student numbers; 46 room lists are cut off in the PDF |
| Published first-year numbers of similar programmes outside the south | not collected yet | - | looked for after the gate list is fixed, for the gate candidates only |

**New in this step.**

- First-years by subject were downloaded for the 15 Laender other than Bavaria (Destatis table 21311-0015, official
  API, 2 s delay). The inventory checks that each file holds only its own Land and covers 2019-2024. This makes
  the north/south check possible at the level of subjects.
- The two timetable PDFs were read into one table: per group and day, the subject, the lecturer as a neutral label
  and the room. 160 of 160 pages were read and no text of a weekly grid was left over. 19 subjects are listed for a
  group without a weekly slot (block courses or dates by arrangement); they are kept without a lecturer. Four pages
  were compared by eye with the PDFs: 59 of 59 cells match; a second, independent reading of all 80 grid pages with
  another PDF library gave the same 1,028 cells. The PDFs, the name-to-label table, the salt that sets the label
  order and the spot-check sheet stay in `data/raw/oth_internal/`, outside the repository. Two lecturers with the
  same surname would share one label; the PDFs do not allow telling them apart.
- The offer list is now built by one function for all steps: of several variants of an offer the full-time one is
  kept, then the one with the lowest programme id, so the list does not depend on the order of the file.
- The matching threshold for Step 7 is fixed at 0.285 (`feasibility_gate.covered_threshold`). The existing
  calibration procedure gives exactly the value of the earlier feasibility report. Its quality is moderate
  (true-positive rate 0.66, false-positive rate 0.14, AUC 0.762, on 80 positive and 88 negative reference modules).
  The reference modules come from the 7 cybersecurity and robotics programmes of the baseline, so the threshold is
  tuned on two subject areas only. For both reasons every match in Step 7 is checked by hand.
- The test that failed in Step 0 is repaired. `analysis/tie_break.py` always took the newest job-ad snapshot, while
  `docs/evidence_tie_break.md` stays on the 17 Oct snapshot until the freeze. The snapshot is now pinned in the code
  (`SNAPSHOT_UNTIL`, to be moved at the freeze together with `JOB_SNAPSHOT`), and the test checks that every count
  comes from the newest snapshot up to that date. The regenerated table shows the 17 Oct counts that the evidence
  document states (945 / 289 / 162 / 58 for "Robotik"). All 125 tests pass.

**What this means for the next steps.**

- Step 2: about half of the offers (10,139) have no content text once the boilerplate is removed. They are grouped
  by title and subject labels only. The two rule files Step 2 needs (`configs/funnel_boilerplate.yaml`,
  `configs/funnel_title_stoplist.yaml`) do not exist yet and are written first.
- Step 5: the catalogue has no language field, so German and English keywords cannot be paired by rule; this is a
  stated limit.
- Step 7: by title, 252 of 447 EMI module rows are found among the timetable subjects after the titles are
  normalised (175 letter for letter); that is 169 of 293 distinct titles. This is a first look only; Step 7
  matches by content and by hand. The timetables give no hours, so they show who teaches a topic, not who has time.
- All 18 old topic lists are available for the validation in Step 2.

**No programme stays or goes in this step.** Nothing was grouped or scored.

**How it was built.** The timetable reader was developed on the PDFs and then committed; the tables above come from
runs of the committed code. A fresh-context check recomputed the numbers in two rounds; its findings (two wrongly
worded numbers, one missing inventory row, the unpinned baseline snapshot) are corrected here. The pre-registration's
data table said "the four rows already collected" for the published numbers; that count was not derived from the
rule and is replaced by what exists (3 documents and two anchors).

**Strongest objection.** The catalogue is a single snapshot of 19 Oct 2026 and half of it has no content text.
**Answer.** It is the only complete public catalogue; the date is stated, and the grouping in Step 2 reports its
results separately for offers with and without focus items.

## Step 1b: a matching threshold that does not come from the old candidates

**Question.** The threshold of 0.285 for "EMI already teaches this module" was tuned on seven cybersecurity and
robotics programmes, the candidates of the earlier analysis. What is the threshold if only EMI's own handbooks are
used?

**Rule.** Procedure and criteria in `docs/criteria_funnel_step1b.md`, committed before any value was computed. Run
on 14 Nov 2026 with code commit d64fe10; the procedure was not changed afterwards.

**Result of the pre-registered procedure.**

| | |
|---|---|
| Source | `data/interim/modules_emi_2026.csv` only: 447 modules in 13 handbook files |
| Same-title pairs across different handbooks | 190, of which 74 are copied texts and left out |
| Anchor modules | 121 (2 have only generic words in the title and get no negative value) |
| Values | 121 positive (median 0.476), 119 negative (median 0.376) |
| Threshold | 0.463 (bootstrap interval 0.382 to 0.538) |
| Quality of the cut-off | true-positive rate 0.57, false-positive rate 0.28, AUC 0.627: weak (below the bar of 0.70) |
| The former 0.285 on this set | true-positive rate 0.83, false-positive rate 0.82 |

**What a fresh-context check and two diagnostics after the run add** (not part of the pre-registered result):

- **The ranking is good, the cut-off is not.** For 51 % of the 121 anchors the true partner is the single most
  similar module among about 408 modules of the other handbooks; for 74 % it is among the top 3, for 83 % among the
  top 5. Against a random other module the true match wins almost always (AUC 0.973). Only the test "true match
  against the hardest wrong match" is weak.
- **0.463 is not a sharp value.** The criterion is nearly flat: every threshold from 0.378 to 0.47 is within 0.03 of
  the best one.
- **The value does not carry over to other universities.** Two EMI handbooks share wording habits that a handbook of
  another university does not have; this limit was named before the run, and its size is large. The checker looked
  at the earlier cross-university scores: of 26 foundation modules EMI certainly teaches (Mathematik 1,
  Programmierung 1, ...), 92 % reach 0.285 but only 19 % reach 0.463. With 0.463 as a gate most candidates would be
  stopped before the hand check.
- **The test set is not clean.** The "wrong" matches were chosen by title words, without a human judgement. Thesis,
  seminar and elective placeholder modules are in it (28 of 121 anchors), and so are real synonyms ("Websysteme"
  against "Web-Client-Technologien", 0.82). Some true matches score near 0 because of data defects (a
  cross-reference stub instead of a text). The false-positive rate of 0.82 for the former value is therefore an
  upper bound, not a measured error rate; in the earlier cross-university calibration it was 0.14.
- **Undeclared choices of the procedure:** bachelor and master modules were mixed, although the gate compares a
  bachelor candidate with bachelor modules only; thesis and placeholder modules were not excluded; square-bracket
  codes in titles were not removed, so two handbook sets contributed no anchors.

**Conclusion.**

- The dependence on the old candidates is removed, but it is replaced by a same-university effect of unknown size
  per candidate. Neither 0.285 nor 0.463 is a value that should decide anything.
- 0.463 is in the rules as pre-registered (`feasibility_gate.covered_threshold`), flagged weak, with 0.285 as a
  stress value. As long as the rule `feasibility_gate.eligible` lets the automatic overlap decide which candidates
  reach the hand check, this value would exclude candidates wrongly. This must be settled before Step 7; Step 2
  to Step 6 do not use it.

**Settled by Soma: no threshold decides a module match.** In Step 7 the computer lists, for every module of a
reference curriculum, the three most similar EMI modules, without a similarity value or a proposal. A fresh-context
reviewer (an AI agent) reads the texts and marks every row by marking rules that are written first. Soma checks 10
rows per candidate and every row the reviewer is unsure about; if 2 or more of a candidate's 10 rows change between
covered and not covered, Soma marks all rows of that candidate. The second team member's blind repetition stays.
Candidates reach the check in the order of the pre-gate ranking, not by automatic overlap. Rules:
`feasibility_gate.eligible` and `hand_check` in `configs/funnel.yaml`. The option not taken was a labelled
cross-university calibration set (handbook downloads and about 160 to 200 pairs marked by two people).

**No programme stays or goes in this step.**

## Step 2: what kinds of programme exist?

**Question.** Which programme types does the catalogue hold, found from the offers' texts with no topic list?

**Rule.** `configs/funnel.yaml`, blocks `universe`, `text`, `similarity`, `discovery`; criteria in
`docs/criteria_funnel_step2.md`. Code: `analysis/funnel_types.py` (scan, embed, run). The step ran twice: a first
result by the pre-registered rules, and a redo after Soma changed three rules (below). The result files are those of
the redo and carry code commit 92da989.

**What was done.** One text per offer (title without degree words, focus items, subject labels), encoded, and the
14,902 full-time offers grouped over a grid of 10 settings. A group counts as stable if it comes back on 80 % samples.
Left-over offers are grouped again: a group at 2 or more institutions is a rare type if it is smaller than the
selected group size and a mid-sized type otherwise. All other offers go to the nearest type if inside its radius.

**The first result and why the rules were changed.** The pre-registered selection rule (highest share of offers in
stable groups) chose the coarsest setting, 50/eom: 63 stable and 229 rare types. An independent reader judged 30
types drawn at random, 10 titles each: are at least 8 of 10 the same kind of programme? The bar, fixed beforehand, is
24 of 30.

| Grouping | Types | Sample of all types | Second sample (stable types; for the labels, 30 other labels) |
|---|---|---|---|
| First result (50/eom) | 63 stable, 229 rare | 17 of 30 | 14 of 30 |
| Diagnostic: 20/eom | 140 stable, 425 rare | 19 of 30 | 20 of 30 |
| Diagnostic: 10/eom (finest of the grid) | 263 stable, 409 rare | 21 of 30 | 21 of 30 |
| Diagnostic: the catalogue's own subject labels as types | 339 labels | 10 of 30 | 13 of 30 |

The first result's types were broad fields that merge neighbouring subjects. It also dropped 30 left-over groups of 50
to 203 offers (2,513 full-time offers, among them Architektur, Psychologie, Medieninformatik), because they were too
large for the rare path. Soma then decided (14 Nov 2026, docs/decision_log.md): use the finest setting of the grid;
keep left-over groups that are too large for the rare path as mid-sized types with a flag; read every type that
survives the Step 3 screen for coherence (`screen.type_coherence`). The changes were made after seeing Step 2's types
and before any type was screened or scored; the setting was chosen by the reader's check, not by a candidate.

**Result of the redo.**

| | |
|---|---|
| Offers | 19,872; 9,456 with focus items, 10,416 with title and subject labels only; 17,154 distinct texts |
| Text check | 0 texts with a dropped phrase, 0 empty; 4 boilerplate strings removed as whole items in 113 offers |
| Grid | 10 settings, all inside the limits; share of offers in stable groups from 0.412 to 0.659 |
| Setting | 10/eom by the changed rule (share in stable groups 0.541); the former rule would again choose 50/eom (0.659) |
| Types | 824: 233 stable (median 28 offers, largest 186), 130 mid-sized (median 20, largest 152), 461 rare (median 3, at most 9) |
| Full-time offers | 8,063 in a stable type, 3,702 in a mid-sized type, 1,814 in a rare type, 1,323 without a type (752 single offers, 571 in 197 groups at one institution only) |
| Assigned afterwards | 3,809 offers (3,637 of other study forms, 172 full-time); 2,484 offers have no type at the end |
| Units (type x level, 2 or more institutions) | 1,285: 462 from stable, 253 from mid-sized, 570 from rare types; 44 types have no unit |
| Agreement with the catalogue's study fields | ARI 0.085 on 13,579 offers (the types are much finer than the 90 study fields) |
| TF-IDF cross-check (stable types) | 138 of 233 flagged method-dependent; 80 of 233 if k-means only has to place the offers in stable types |
| Old topic lists | 17 of 18 testable (energy_informatics has no title match); 3 recovered on the fitted offers (cybersecurity, embedded_iot, aerospace), 3 on all assigned offers (cybersecurity, quantum, aerospace) |
| Second run | identical: same type for all 19,872 offers, same file hashes |

**Reader's check of the redo (criterion G9, measured again).** A fresh reader, titles only: 22 of 30 in the sample of
all types (stable 5 of 6, mid-sized 4 of 4, rare 13 of 20) and 22 of 30 in the sample of stable types. That is 73 %,
better than the first result and still below the bar of 24. With every borderline case counted as a fail it is 14
and 20, as a pass 24 and 26. G9 is not passed. What still fails: neighbouring subjects merged under a shared word
(North and Latin American studies; applied chemistry with chemical engineering), catch-all groups held together by an
organisational label or a broad theme, and small rare types of two to four loosely related titles. Teaching and
non-teaching programmes are rarely mixed. The reader also noted that some types are the same kind as each other
(two biology teacher-training types): the check measures purity, not splitting.

**What this means for the next steps.**

- About 1 type in 4 is mixed. Step 3 therefore reads every type that survives the screen; a mixed type is flagged and
  cannot take a gate slot without a full reading of its titles.
- Mid-sized types (130, with a quarter of the full-time offers) and rare types are not stability-tested and carry a
  flag. Mid-sized types hold mainstream kinds such as Betriebswirtschaft, Elektrotechnik, Informatik and
  Medizintechnik. Part of them come from groups that were tested and fell below the stability bar.
- More than half of the stable types (138 of 233) are not found again by a word-based method; they carry the flag
  "method-dependent".
- The grid is sensitive to small changes of the text: after 37 titles were corrected, the 10/eom setting has 233
  stable types where the diagnostic on the earlier texts had 263. The same programme kind can be split over several
  types; the similarity radius of Step 3, not type membership, counts the competition.

**What went wrong on the way.** A first complete run (commit e578105) was void: 1,798 texts still carried the level
marker in its long form ("grundständig außer Staatsexamen"). Three code reviews: round 1 found 3 blockers and 8
majors (title cleaning deleted subject words after "Master of"; the rare-path cut-off used at most 60 members per
type; note headings cut inside the word were left in; tests could pass with a wrong result), all fixed; round 2 found
no blocker, recomputed every number with 0 mismatches and found a title rule that removed a real word in 21 titles
(fixed; 37 titles changed, in the redo); the review of the redo found no blocker and no major, 11 minor points.

**Choices the rules left open** (written in the yaml comments, the code or the decision log): noise for the selection
is counted before unstable groups are dissolved, and a setting needs at least one stable group; the rare-path cut-off
is the median over all within-type pairs of the stable types (0.0720; the median of the types' own medians, 0.0625,
would give 124 mid-sized and 545 rare types); all 461 rare types take the median radius of the stable types (0.0494),
which is larger than their own largest distance; the cross-check uses k = the number of stable types and tests stable
types only; stability uses 10 refits per setting on the three UMAP seeds in turn, and UMAP is not refitted on the
samples; a boilerplate string is dropped only as a whole focus item (1,779 longer items contain one and stay); old
lists are matched on titles.

**Scorecard.** G1 pass. G2 not met as worded (the boilerplate part can only hold for whole items; the rule's wording
was made exact). G3 pass, except that the sample file carries no commit line. G4 to G8 pass. **G9 not passed (22 of
30; bar 24).** G10 pass. G11: no open blocker or major; 11 minor points of the last review are not changed in the
code. G12: one check round on these notes (2 wrong statements and 3 misleading wordings corrected, no wrong number).
G13 pass (170 tests). R1 pass (rules 5101371 before code 92da989 before the run; the selection rule's wording was
completed after the run to name the third limit, with no effect on the selection). R3, R4, R5 pass (tests recompute the
selection, the left-over groups and all texts; 0 groups dropped, 0 texts differ). R6 measured as above.

**No programme stays or goes in this step.** By Soma's decision the types go to Step 3 with the coherence check on
every surviving type; G9 stays recorded as not passed.

## Step 3: which units stay, and how much competition do they have?

**Question.** Which programme types are open to OTH and inside EMI's field, and how many similar programmes exist
near Amberg, in Bavaria, in the south and in Germany?

**Rule.** `configs/funnel.yaml`, blocks `definitions`, `pool_mapping`, `screen`, `freeze`; criteria in
`docs/criteria_funnel_step3.md`. Code: `analysis/funnel_units.py` (items, labels, run, sheet). Result files carry
code commit 7f24b79. A unit is a type x level (bachelor or master) with offers at 2 or more institutions.

**Three rules did not work with the finer types of Step 2 and were changed (confirmed by Soma on 15 Nov 2026).**
The step ran three times; the first two results are void.

| Rule | As first written | What happened | Changed to |
|---|---|---|---|
| Merged candidates | units linked through chains of close centroids | 411 of 613 bachelor units and 448 of 672 master units fell into one group each; the whole group was dropped as "at OTH" (840 units); 424 units were left after this test and 43 after all four screens | a group only if every pair is close to each other; largest group 6 |
| EMI's field | raw similarity of an offer's title and focus areas to the full text of EMI's modules; bar from 11 EMI and 30 other OTH offers | Informatik (type 13) and 30 of the 49 marked field units fell outside; 55 of the 251 marked outside units were inside, among them Philosophie (2 Fächer) and Kunstgeschichte (2-Fächer); on the 300 units marked by an independent reader the score reached AUC 0.71 | similarity to the titles of EMI's modules on centred vectors, mean over all offers of the unit; bar set on the 300 marked units so that 95 % of the field's units are kept; AUC 0.965 |
| Already at OTH | an OTH offer within the type's median member distance | 24 of OTH's 46 offers dropped no unit (7 of the 12 EMI offers); units holding an OTH programme stayed | an OTH offer is assigned to the type, or lies within the median distance; 45 of 46 OTH offers now drop a unit; a merged group is no longer dropped as a whole |

All three changes were chosen by checks that look at no candidate: group sizes, agreement with labels made from
titles only, and the share of OTH's own offers that trigger the test. The former rules are stress specs.

**Result.**

| | |
|---|---|
| Units tested | 1,285 (613 bachelor, 672 master) from 780 types |
| Dropped: already at OTH | 44 units (29 for this reason only) |
| Dropped: teacher training (half or more of the offers) | 244 (32 for this reason only) |
| Dropped: falling and validated trend (below -3 % a year) | 17, none for this reason only; only 51 units have a validated trend, 35 could not be backtested, 29 have no slope |
| Dropped: outside EMI's field | 859 (620 for this reason only) |
| Primary list | 365 units (183 bachelor, 182 master) of 247 types, in 268 candidates after merging; 201 from rare, 100 from stable, 64 from mid-sized types |
| Stress list (only "at OTH" applied) | 1,241 units |
| Merged groups | 300 groups hold 734 units; the largest has 6 |
| Repeat of the final run | identical screen table and lists |

**The EMI-field screen is a generous first filter, not a statement that a unit is in EMI's field.** The bar keeps 47
of the 49 marked field units and 49 of the 251 marked outside units. Of the 77 marked units on the primary list,
38 are outside EMI's field by the reader's labels: about half of the list. 68 units lie just above the bar and 75
just below (within 0.02). The score rewards any subject that appears among EMI's module titles, so Physik and
Mathematik rank at the top, and look-alike words pass (Philosophie, Komposition). Step 7 measures the real fit on
curricula; a unit dropped here would be lost, which is why the bar is generous. Of the 10 marked field units that
are not on the list, 6 are teacher training, 2 are already at OTH and 2 fall just below the bar.

**Head of the primary list by EMI score** (the full list with all numbers: `reports/funnel2/step3_screen.md`,
`data/interim/funnel2_candidates.csv`):

| Unit | Titles nearest the centre | Kind | EMI score | Similar offers in Germany | within 150 km | Mixed type |
|---|---|---|---|---|---|---|
| 12 bachelor | Physik; Physics; Physik / Physics; Mathematische Physik; Physik, Theor... | stable | 0.89 | 53 | 12 | no |
| 438 master | Mechatronische Systeme; Mechatronische Systementwicklung; Mechatronisc... | rare | 0.84 | 28 | 5 | no |
| 12 master | Physik; Physics; Physik / Physics; Mathematische Physik; Physik, Theor... | stable | 0.79 | 53 | 11 | no |
| 206 bachelor | Elektrotechnik; Elektrotechnik / Electrical Engineering; Electrical En... | stable | 0.76 | 283 | 41 | no |
| 6 master | Mathematik; Mathematik (2-Fächer); Mathematik in Medizin und Lebenswis... | stable | 0.71 | 65 | 10 | no |
| 206 master | Elektrotechnik; Elektrotechnik / Electrical Engineering; Electrical En... | stable | 0.70 | 193 | 39 | no |
| 684 bachelor | Creative Technologies; Creative Engineering | rare | 0.69 | 2 | 1 | yes |
| 736 master | Elektrotechnik - Erneuerbare Energien und Systemtechnik (dt.-frz. Stud... | rare | 0.68 | 6 | 0 | no |
| 235 master | Embedded Systems; Embedded Systems Engineering; Embedded Systems - Aer... | mid-sized | 0.67 | 7 | 0 | no |
| 6 bachelor | Mathematik; Mathematik (2-Fächer); Mathematik in Medizin und Lebenswis... | stable | 0.67 | 78 | 12 | no |
| 648 bachelor | Künstliche Intelligenz in der Medizin; Künstliche Intelligenz in der M... | rare | 0.67 | 5 | 0 | yes |
| 284 bachelor | Medienwissenschaften; Medieninformatik; Medienwissenschaft (Verbund); ... | mid-sized | 0.66 | 22 | 3 | yes |
| 793 master | Artificial Intelligence; Artificial Intelligence and Intelligent Syste... | rare | 0.66 | 4 | 1 | no |
| 368 bachelor | Informationssystemtechnik; Informationstechnik / Medizintechnik; Infot... | rare | 0.65 | 32 | 3 | yes |
| 237 master | Energietechnik; Energie- und Umwelttechnik: Energietechnik; Energie-, ... | mid-sized | 0.65 | 39 | 6 | no |
| 666 master | Advanced Information Technology; Advanced Information Technology (beru... | rare | 0.65 | 5 | 0 | no |
| 734 bachelor | Medien- und Kommunikationsmanagement; Kultur- und Medienmanagement; Me... | rare | 0.65 | 13 | 3 | yes |
| 704 bachelor | Vermessung; Vermessung (ausbildungsbegleitend); Geovisualisierung | rare | 0.65 | 8 | 2 | yes |
| 710 master | Strategische Produkt- und Innovationsentwicklung; Management and Innov... | rare | 0.64 | 5 | 1 | yes |
| 809 bachelor | Design | rare | 0.64 | 1 | 0 | no |
| 809 master | Design | rare | 0.64 | 3 | 1 | no |
| 703 bachelor | Kooperatives Ingenieurstudium Elektrotechnik; Elektrotechnik - Koopera... | rare | 0.64 | 5 | 0 | yes |
| 734 master | Medien- und Kommunikationsmanagement; Kultur- und Medienmanagement; Me... | rare | 0.64 | 12 | 1 | yes |
| 407 master | Künstliche Intelligenz und industrielle Digitalisierung; Robotics, Cog... | rare | 0.64 | 25 | 6 | yes |
| 294 bachelor | Technische Informatik; Informatik und Systems-Engineering; Informatik ... | mid-sized | 0.64 | 15 | 1 | no |

**Competition and regional gap on the primary list** (similar offers by content: offers of the type plus offers
inside its radius, each institution and cleaned title once, without OTH and distance learning). 90 units have no
similar offer within 150 km; 80 have none in Bavaria although the kind exists elsewhere; 33 have none within 150 km
and none in the south ("gap"). For 30 units the subject pool is not shrinking in the Laender that host the
programme outside the south (popularity tier 2; 2 of them are among the 33 gap units). These counts are **not validated** (next paragraph).

**The check of "similar" failed twice; the competition counts are not validated.** Soma decided that the 100
offers are marked by three AI readers instead of by him (an offer counts as "yes" if two of three say yes). For 10
units of the list each sample holds the 5 farthest offers inside the radius and the 5 nearest outside it.

| Round | Radius | "Same kind" inside (needed: at least 70 %) | "Same kind" outside (allowed: at most 30 %) | Result |
|---|---|---|---|---|
| 1 | each type's own radius | 46 % | 40 % | fail |
| 2 (the rule's fallback, new sample) | one common radius, 0.0494 | 64 % | 46 % | fail |

By the rule (`validity_check.second_failure`) the per-type radius stays in force, every competition count carries
the flag "not validated", and the offers half of the differentiation value takes the full range 1 to 5 in the
ranking. What the check shows: the radius is not a sharp line. Just inside it about half of the offers are the
same kind of programme, just outside it nearly as many. The counts are therefore a rough measure of how crowded a
field is, not a count of direct competitors. The three readers are the same AI model: in round 1 their marks were
identical on all 100 offers, in round 2 (separate folders, different row order) they differed on 2. They count as
one judgement, not three, and no person has marked the offers.

**Coherence of the types on the list (rule `screen.type_coherence`).** Independent readers read 10 titles of each of
the 247 types: 172 hold one kind of programme (70 %; bar 80 %), 75 are flagged "mixed" (103 of the 365 units). With
every borderline case counted as a pass it is 203, as a fail 129. By kind: stable 43 of 59, mid-sized 32 of 38,
rare 97 of 150. A mixed type keeps its place on the list with the flag and cannot take a gate slot without a full
reading (`docs/funnel_type_coherence.csv`).

**Spot check for Soma** (source for every row: `data/interim/funnel2_screen.csv`):

| Unit | Titles nearest the centre | Result | Test | Numbers (data/interim/funnel2_screen.csv) |
|---|---|---|---|---|
| 112 master | Logistikmanagement; Logistik, Infrastruktur und Mobilität; Supply Chai... | dropped: already at OTH | an OTH offer of this level belongs to the type | Logistik & Digitalisierung Master of Science |
| 216 bachelor | Maschinenbau; Maschinenbau und Design; Maschinenbau/Verfahrenstechnik;... | dropped: already at OTH | an OTH offer of this level belongs to the type | Maschinenbau Bachelor of Engineering |
| 216 master | Maschinenbau; Maschinenbau und Design; Maschinenbau/Verfahrenstechnik;... | dropped: already at OTH | an OTH offer of this level belongs to the type | Innovationsfokussierter Maschinenbau Master of Engineering |
| 262 bachelor | Betriebswirtschaft; Betriebswirtschaftslehre; Betriebswirtschaft & Man... | dropped: already at OTH | an OTH offer of this level belongs to the type | Handels- und Dienstleistungsmanagement Bachelor of Arts |
| 297 bachelor | Engineering Science; Mechanical Engineering; Engineering; Engineering ... | dropped: already at OTH | an OTH offer of this level belongs to the type | Technical Engineering Bachelor of Engineering |
| 51 bachelor | Tourismusmanagement; Internationales Tourismus- und Eventmanagement; I... | dropped: other screen | outside EMI's field | teacher share 0.00; trend -3.6 %/yr, validated False; EMI score 0.374 |
| 326 master | Gesundheitswissenschaft; Public Health; Health Sciences; Gesundheitswi... | dropped: other screen | outside EMI's field | teacher share 0.00; trend -1.1 %/yr, validated False; EMI score 0.325 |
| 528 master | Soziologie; Soziologie: Diversität und Gesellschaft; Demokratiewissens... | dropped: other screen | outside EMI's field | teacher share 0.00; trend 0.5 %/yr, validated False; EMI score 0.237 |
| 551 master | Inklusive Pädagogik und Elementarbildung; Blinden- und Sehbehindertenp... | dropped: other screen | teacher training; outside EMI's field | teacher share 1.00; trend 0.4 %/yr, validated False; EMI score 0.304 |
| 791 bachelor | Wirtschaftsingenieurwesen; Wirtschaftsingenieurwesen/Technischer Vertr... | dropped: other screen | outside EMI's field | teacher share 0.00; trend -3.8 %/yr, validated False; EMI score 0.358 |
| 189 master | Digital Engineering; Digital Engineering Elektrotechnik; Digital Engin... | kept | passes all four screens | teacher share 0.00; trend -1.1 %/yr; EMI score 0.593; similar offers within 150 km 1 |
| 294 bachelor | Technische Informatik; Informatik und Systems-Engineering; Informatik ... | kept | passes all four screens | teacher share 0.00; trend 0.7 %/yr; EMI score 0.636; similar offers within 150 km 1 |
| 352 master | Umweltingenieurwesen; Umwelttechnik; Umweltingenieurwissenschaften; Um... | kept | passes all four screens | teacher share 0.00; trend -2.0 %/yr; EMI score 0.458; similar offers within 150 km 6 |
| 386 bachelor | Intermedia Design; Design interaktiver Medien; Intermedia Design mit P... | kept | passes all four screens | teacher share 0.00; trend -2.3 %/yr; EMI score 0.472; similar offers within 150 km 0 |
| 691 master | Agrarmanagement; Land- und Ernährungswirtschaft - Agrarmanagement; Lan... | kept | passes all four screens | teacher share 0.00; trend -18.3 %/yr; EMI score 0.475; similar offers within 150 km 1 |

**Limits and choices.**

- A type that only resembles an OTH programme, without holding an OTH offer, stays on the list (for example a second
  Medieninformatik type), unless an OTH offer lies within its median distance (1 unit: 212 bachelor). The capture
  model and the one-programme limit of the gate deal with it later.
- The trend screen is almost inert: 521 units have a slope below -3 % a year, but only
  validated trends drop a unit, and few trends are validated.
- The bar and the choice of the score were set on the same 300 marked units; nothing was held out. The labels were
  made by one AI reader from titles only; a second AI reader agreed on 27 of 30 units.
- The 15 of EMI's 293 module titles matched by the pattern for change tables, theses, internships and elective
  placeholders are left out; a few such titles with other spellings remain (2 units on the list depend on them).
  Units' scores are the mean over all their offers.
- One offer lies exactly on a type's radius; the code counts it outside, exact arithmetic inside (unit 3 master, 398
  against 399 similar offers; not on the list).
- The check of 100 offers has three weak points: in round 1, 3 of the 50 "outside" rows are the type's own offers
  beyond the radius; in 3 units the same title appears on both sides (the model tells them apart by focus areas,
  which the sheet does not show); two descriptions have fewer than 5 titles. It also tests the edge of the radius
  only, where a clear difference between the two sides is hardest to reach.
- An offer without a Land or coordinates counts for Germany only (1 offer). Bavaria's base share for the quotient is
  taken over all offers of the level (0.123 bachelor, 0.125 master).
- The first-years backtest ends in 2024, because 2025 is the Bavarian G9 gap year.

**Reviews.** First review: 2 blockers, 12 majors, 12 minors (the two rule failures above; teacher share on labels
with the level marker; backtest details; sheet could leak the side). Second review: every number recomputed without
mismatch; 2 blockers, 6 majors, 9 minors (similar offers undercounted in 176 units; a parsing leftover among the
module titles; the "at OTH" test missed half of OTH's offers; the bar is fragile). All fixed or stated above. The
third result was checked once more together with these notes.

**Scorecard.** S1 pass (labels file was untracked when first used; its hash is recorded). S2, S4, S5, S7, S8 pass
(tests recompute units, teacher share on 60 units, all counts, flags and quotients); S3 and S6 as first written are
replaced by the changed rules (S17, S18, S20). S9
done: 70 % of the types pass, below the bar of 80 %; mixed types are flagged. S10 done: the check failed in both rounds; the competition
counts are flagged "not validated". S11 pass. S12 pass (two runs identical). S13 after two review rounds and a final recomputation of all units: no
open blocker. S14 one check round (1 wrong statement and 10 unclear wordings corrected, no wrong number). S15 pass. S16 above. S17 pass (largest group 6; every pair mutual). S18 pass (AUC
0.965; 47 of 49 kept), with the limit that nothing was held out. S19 pass: Soma confirmed the three changed rules on 15 Nov 2026. S20 pass (45 of 46).
S21 above.

**Step 3 is complete.** Nothing is open for Soma; Step 4 starts with Soma's OK.

## Step 4: are students coming?

**Question.** How do the student numbers behind every unit develop, in Bavaria and in Germany, for German and for
foreign students?

**Rule.** `configs/funnel.yaml`, block `demand` (with `pool_mapping`); criteria in `docs/criteria_funnel_step4.md`.
Code: `analysis/funnel_demand.py`. Result files carry the code commit of the final run (see data/interim/funnel2_step4.json). No unit is removed in this step.

**What the numbers are.** Destatis counts students by subject, not by programme. Every unit therefore gets a *pool*:
the Destatis subjects of its offers, weighted by how often they occur. The trend is that of the pool, not of the
programme type. Two units with the same subjects have the same trend (for example the media-design master units 245
and 408).

**Result.**

| | |
|---|---|
| Units with demand numbers | 1,285 (primary list 365, stress list 1,241) |
| Distinct pools (weight mixes per series) | 1,141; 1,118 backtested, 23 not (no students in the last year, or fewer than 12 consecutive years) |
| Model comparison: average error (MASE) over pools and horizons 1 to 5 | naive 2.01, drift 2.41, ets 2.53 |
| Model for the projection to 2030 | naive: the last value is the best forecast; no model beats it on average |
| Reliable trends (the test of Step 3: drift beats naive and its MASE is below 1) | 51 units in 39 pools, 23 of them on the primary list (22 growing, 1 falling); drift beats naive at all for 210 units |
| Primary list, German trend in Bavaria (first-years 2019-2024; master: graduates 2019-2025) | 128 growing, 93 falling by up to 3 % a year, 136 falling faster, 8 without a slope |
| Primary list, German trend in Germany | 95 growing, 269 falling, 1 without a slope; 76 units grow in both |
| Median trend on the primary list | German: -2.0 % a year in Bavaria, -1.9 % in Germany; foreign: +9.3 % in Bavaria, +6.3 % in Germany |
| Foreign students' share in the pool (Bavaria, last year, median of the primary list) | 30 % |
| Second run | identical table |

**What it means.**

- **Most pools lose German students.** On the primary list 229 of 365 units have a falling German pool in Bavaria, and
  the middle unit loses about 2 % a year. Foreign students grow in most pools. This repeats the baseline finding for
  Informatik on the level of all candidates.
- **The trends are weak evidence.** Only 51 of 1,285 units pass the test for a reliable trend, a trend line beats
  "next year is like this year" at all for 210, and on average the naive model wins. The projection to 2030 is therefore the last value, and a slope
  says what happened since 2019, not what will happen.
- **The fastest-growing German pools with at least 100 students** on the primary list are media design (Destatis
  subject "Neue Medien", +22 % a year for master graduates), two bachelor units whose pools are mostly
  "Interdisziplinäre Studien (Schwerpunkt Ingenieurwissenschaften)" (Bionik, Service Engineering; +13 %),
  Informationstechnologie and Informatik master units (+7 to +10 %) and media studies (master, +9 %). The largest
  falls are Tonmeister and Medienproduktion (pool Medientechnik, -10 to -13 %), Visual Computing (Medieninformatik,
  -10 %) and Energietechnik (-9 %), all bachelor units.
- **Foreign students are a corridor.** For each unit the 2030 value lies between "as many as today" and "the slope
  since 2019 continues" (up or down); it is reported next to the German number and never added to it. A unit
  without a foreign slope has no corridor.

**Limits.** A pool is as coarse as the Destatis subject list: a niche programme inside "Informatik" shares the trend
of all of Informatik. 21 primary units have a pool of fewer than 50 German students in the last year. 322 of the 365
primary units have a weight mix of their own, but many mixes are nearly the same subject. Master units use
graduates, which react years later than first-years. The first-years series ends in 2024 because 2025 is the
Bavarian G9 gap year.

**Scorecard.** T1 pass. T2 pass (1,285 units, both lists). T3 pass (slopes recomputed from the Destatis tables for 40
units). T4 pass: "validated" uses the backtest of Step 3; the comparison of the three models uses the same origins for
all models (at least 5 training years) and has its own column names. T5 pass (naive under both). T6 pass. T7 pass (slope and "validated" equal Step 3 for every unit). T8 above.
T9 pass (two runs identical). T10 one review round: every per-unit number recomputed without mismatch; 1 inconsistent headline number and 3
wrong statements in these notes corrected. T11 pass.

**No programme stays or goes in this step.** The full table: `data/interim/funnel2_demand.csv`,
`reports/funnel2/step4_demand.md`.

## Step 5: are there jobs?

**Question.** How many job ads match each unit, in Germany, in Bavaria and within 100 km of Amberg?

**Rule.** `configs/funnel.yaml`, block `labour`; criteria in `docs/criteria_funnel_step5.md`. Code:
`analysis/funnel_labour.py` (keywords, fetch, measure). Source: the job board of the Federal Employment Agency, one
request per keyword and region, 2 s apart, all counts of the primary list on 15 Nov 2026. No unit is removed.

**How the keywords are made.** For every type the titles of its programmes are split into phrases; the up to 3
phrases shared by most titles (at least 2) are the keywords; if no phrase occurs twice, the parts of the most
central title are used. Degree and catalogue words are dropped by a list written before Step 2. Nothing was added or
struck by hand. The keyword file (`docs/funnel_keywords.csv`: 1,172 distinct keywords for 824 types) was committed
before the first request (commit 87811c7).

**A first set of counts was void: the wrong Amberg.** The job board read the place "Amberg" as Amberg bei Buchloe
in Swabia, 177 km from Amberg in der Oberpfalz, so every "within 100 km" count covered Munich, Augsburg and Ulm
instead of our region. A reviewer found it in the stored replies. The place is now sent as "Amberg, Oberpfalz", and
the code checks the coordinates of every reply. **The same error is in the baseline's job snapshots** (regions
within 50 and 100 km of 15 and 17 Oct 2026; mixed on 7 Nov), so the baseline figure "191 ads within 100 km" is not
valid; that is a follow-up for the baseline report.

**Result for the primary list.**

| | |
|---|---|
| Units with all counts | 365 of 365; 355 distinct keywords, 1,068 counts, 0 errors, one day |
| All job ads on that day | 780,392 in Germany; 131,440 in Bavaria (16.8 %); 49,476 within 100 km of Amberg (6.3 %) |
| Measure: ads within 100 km for the unit's median keyword | median 22; a quarter of the units at 2 or fewer, a quarter above 116 |
| Units with no ad within 100 km | 63 |
| Units below 10 ads (the lowest value of the ranking scale is 10) | 152 |
| Units with 150 ads or more (the highest value of the scale) | 82 |
| Bavaria's share of a unit's German ads | median 20 % (all ads: 16.8 %); above the share of all ads for 271 of the 357 units with any German ad |

**What the measure can and cannot say.**

- **It counts how often a word appears in job ads of every level, not how many jobs wait for graduates of a
  programme.** The top of the list is led by general words: "mechatronik" 2,254 ads within 100 km, "organisation"
  2,538 and "führung" 1,843 (their unit: 2,191, the mean of the two), "management" 2,074, "elektrotechnik" 2,009,
  "maschinenbau" 1,256, "informatik" 685.
- **Specific programmes get specific, small counts.** "data science" 109, "robotik" 85 ("robotics" 24),
  "mechatronische systeme" 73, "künstliche intelligenz" 67, "embedded systems engineering" 22, "künstliche
  intelligenz in der medizin" 1. These are closer to what the step should measure, but long phrases are rarely
  written in an ad.
- **One keyword decides for many units.** 144 of the 365 units have a single keyword, and 285 of the 478 keyword
  rows are single words. The 67 units whose keywords come from the most central title have a median of 11 ads, the
  298 others 28. With two keywords the median is their mean, so the larger word dominates.
- **The scale of the ranking saturates.** 82 units reach the top value of 150 ads and 152 are below the bottom
  value of 10, so the measure separates only the middle third.
- **Some keywords are word stems or general words.** By the rule hyphens stay, so "Elektro- und
  Informationstechnik" gives "elektro-" (1,587 ads) and "Produkt- und Objektdesign" gives "produkt-" (389). The rule
  allows striking such keywords by hand before the counts; no hand work was done, so they stay and are named here.
- **The 5 % rule dropped nothing.** The most frequent phrase among the types' top three, "management", is in 40 of
  824 types (ties counted); the line is 41.
- **No English pairing.** The catalogue has no language field.
- **Counts of one day.** New keywords have no history, so nothing is known about their trend.

**Reviews.** One review round: keywords and the arithmetic of the measure recomputed for all units without mismatch;
1 blocker (the wrong Amberg) and 3 majors (hyphens were stripped against the rule; the tie reading of the 5 % rule;
the day of a list was not enforced), all fixed; keywords and counts were then made again.

**Scorecard.** L1 pass (keywords recomputed by the reviewer for all 824 types and by a test for 40). L2 pass (keyword
file committed before the first request; its hash is stored with every count). L3 pass for the primary list. L4
pass. L5 pass (test recomputes the measure for 60 units and checks the place of the stored replies). L6 pass: both lists were counted on 15 Nov 2026. L7 one review round, fixed. L8 pass.

**Stress list.** All 1,241 units of the stress list have their counts too (1,115 distinct keywords, 3,348 counts in
all, 0 errors, the same day). Their median is 5 ads within 100 km.

**No programme stays or goes in this step.** Full table: `data/interim/funnel2_labour.csv`,
`reports/funnel2/step5_labour.md`.

## Step 6: how many first-years, and how many new to OTH?

**Question.** For every unit: how many first-years could a new programme in Amberg or Weiden expect, and how many of
them would not come from OTH's existing programmes?

**Rule.** `configs/funnel.yaml`, block `capture`; criteria in `docs/criteria_funnel_step6.md`. Code:
`analysis/funnel_capture.py`. All 1,285 units (both lists and the 44 units on neither), the same model. No unit is removed: the minimum cohort of
20 is a flag for Step 7.

**How the number is made.**

- **Anchor.** German first-years of the unit's subject pool in Bavaria (2024) divided by the Bavarian bachelor offers
  of that pool; for a master the graduates (2025) times 0.5. This is "students per programme" of the subject.
- **Scale.** A distance model (Huff, as in the baseline, distance decay 1.6): school leavers of 96 Bavarian counties
  (master: students at 17 campuses) choose between the new programme in Amberg and Weiden (master: Amberg), the sites
  of the unit's similar offers, and OTH's own offer. The scale is the new programme's demand over the mean demand of
  the unit's Bavarian comparator sites; 1.0 without one.
- **Gross** = anchor x scale, with a band from x0.33 to x3.0. **Net-new** = gross minus the share the model takes
  from OTH's own offer (weight 0.5; band 1.0 and 0.25).

**Result for the primary list (365 units).**

| | |
|---|---|
| Anchor | median 28.9 (quartiles 23.2 and 38.9) |
| Scale | median 0.8 (0.6 and 1.0) |
| Gross first-years, central | median 24.2 (15.4 and 34.0); bachelor 29.1, master 19.0 |
| Net-new first-years, central | median 16.5 (11.3 and 23.9); 294 units at 10 or more, 20 units at 40 or more |
| Share taken from OTH, central | median 24 % (range 4 % to 78 %) |
| Below the minimum cohort of 20 (central gross) | 140 units (41 bachelor, 99 master); 225 at or above |
| Foreign students on top (never inside the central number) | up to 9.0 for the median unit; no value for 4 units |
| Stress list | 630 of 1,241 units below the minimum cohort |

**What the numbers can say.** An order of magnitude: a new programme in a mid-sized subject lands at roughly 15 to 34
first-years, about 11 to 24 of them new to OTH, with a band of x0.33 to x3.

**What they cannot say.**

- **They are not a demand ranking.** The top of the list is made by thin data: of the 25 units with the highest
  net-new value, 14 carry a flag (5 with fewer than 2 Bavarian offers in the pool, 12 with at most one Bavarian
  comparator site). Example: the first unit (408 master, media art) has an anchor of 133 because its pool has under
  2 Bavarian offers.
- **The anchor is the subject's size, not the programme's.** Units of one pool share one anchor. First-years by
  subject include state-exam and teacher-training students, the offers do not, so subjects such as law, physics and
  biology are too high. 19 primary units have fewer than 2 Bavarian offers in the pool, 29 have a tenth or more of
  the pool on subjects for which the statistics show no German student although the catalogue has offers, 4 have an
  anchor of 0, 2 take the Germany-wide value.
- **The scale rests on few sites and rewards having none.** 83 units have no Bavarian comparator (scale 1.0), 71 have
  exactly one. The median scale is 1.00 without a comparator, 0.81 with one, 0.70 with two, 0.73 with three, 0.65 with four or more.
  All 16 units with a scale above 1.5 have exactly one Bavarian site (highest: 2.31).
- **"New to OTH" is geometry, not content, on the primary list.** Units with an OTH offer were dropped in Step 3, so
  all 365 units use the nearest OTH offer of the level as OTH's site. It lies within the type's radius for 33 units
  only. The share from OTH follows the number of competitor sites (correlation -0.74 with its logarithm): the fewer
  competitors, the larger the share. Incrementality is therefore not measured for these units; the gross value is
  the firmer number.
- **The minimum cohort is not a sharp line.** For 325 of 365 units the gross band includes 20. 76 units are below 20
  only because their scale is below 1.
- **The level check is one subject.** Four published numbers, all for the cybersecurity bachelor unit (anchor 30.4):
  capacity 25 at one university of applied sciences, about 60 from one student review at another, 156 and 3 at two
  research universities. Absolute log errors 0.20, 0.68, 1.64, 2.32 (median 1.16). It validates nothing for the
  other anchors. No correction is applied.
- **Known limits of the model:** straight-line distance, Bavarian origins only, no attractiveness of a location,
  competition counts not validated (Step 3).

**Without any flag** (2 or more Bavarian offers in the pool, under a tenth on subjects without students, 2 or more
Bavarian comparator sites): 198 units, 105 at or above the minimum cohort, net-new median 17.4 (11.2 and 23.9).

**Reviews.** Round 1: the reviewer recomputed all 1,285 units and every summary number with own code, 0 mismatches.
2 blockers: (B1) the code took the mean of per-subject ratios as the anchor, the rule says pool students over pool
offers; fixed, table made again (the first table is void; the cohort flag differs for 17 primary units, 85 of all 1,285, between the two
readings, the per-subject value stays as a column). (B2) thin anchors lead the top of the list; flags added, no
rule changed. Majors: the placeholder OTH site, the scale on single comparators, the level check's wording, the
cohort as a soft line; all stated above and flagged in the table. Capture is per unit, not per merged group
(`similarity.which_set`); logged. Choices the rule does not state are in the decision log.

**Scorecard.** C1 pass (commit f9d8ef0, clean tree, input hashes). C2 pass. C3 pass. C4 pass after the fix. C5 pass.
C6 pass. C7 pass. C8 pass. C9 pass (two runs, identical file). C10 pass after one round of fixes and a fact check of these notes (5 wordings corrected). C11 pass (196 tests).

**Proposals for Soma before Step 8** (rule changes, not made): a floor for the anchor's denominator; the scale
shrunk towards 1 with fewer than 3 comparator sites; net-new not scored for units whose OTH offer is a placeholder.

**No programme stays or goes in this step.** Full table: `data/interim/funnel2_capture.csv`,
`reports/funnel2/step6_capture.md`.

## Step 7: can EMI teach it with what it has?

**Question.** For the best candidates so far: how much of a real programme of that kind does EMI already teach?

**Rule.** `configs/funnel.yaml`, blocks `shortlist` and `feasibility_gate`; criteria in
`docs/criteria_funnel_step7.md`; marking rules in `docs/funnel_marking_rules.md` (version 3). Code:
`analysis/funnel_shortlist.py` (gate order), `funnel_refs.py` (references), `funnel_feasibility.py` (rows, sample,
third reader, verdicts). No person has checked a module verdict (Soma's decision).

**How it ran.**

- **Gate list.** 268 candidates ordered by the pre-gate score. Down that order: 10 tried, 6 eligible (3 per level),
  2 mixed types not candidates, later bachelor candidates skipped once 3 were eligible. 4 tried masters had no
  public, complete handbook.
- **References.** 10 handbooks, 357 modules; 134 requests through the project fetcher, 1 blocked by robots.txt and
  not worked around.
- **Sheet.** Each module next to the 5 most similar EMI modules plus up to 5 whose title shares a word (English and
  German), copies shown once, EMI texts up to 3,000 characters, 3 timetable subjects; universities, cities,
  regions and module codes removed.
- **Marking (third pass).** Four fresh AI markers marked all rows. A second, blind marker took 189 rows: 10 drawn
  per candidate, every unsure row, and every row of the computer science master (within 0.10 of the 40 % bar).
  All samples passed; agreement on covered or not covered 92 %. A third, blind reader settled the 15
  disagreements.

**Three passes, and why.**

| Pass | What changed before it | Computer science BA | Cybersecurity BA |
|---|---|---|---|
| 1 | - | 44 % | 39 % / 39 % |
| 2 | sheet showed 3 EMI modules and missed real partners; now 5 plus title matches (Soma) | 46 % | 35 % / 39 % |
| 3 | readers treated credit points in opposite ways; now content counts and two EMI modules may cover one, because EMI teaches in 5-ECTS modules (Soma) | 68 % | 63 % / 58 % |

The third rule was set knowing the second result; it is logged as such, and the result without it is reported.

**Result.**

| Gate | Candidate | Handbooks | Overlap with EMI | Verdict |
|---|---|---|---|---|
| 1 | Computer science, bachelor | 1 | 68 % | **passes with existing resources**: no new lab, 2 ECTS taught from outside; 52.5 ECTS of new modules by current lecturers, about 1.2 professor-equivalents |
| 3 | Cybersecurity, bachelor | 2 | 63 % and 58 % | in the band, but needs 3 and 10 ECTS taught from outside (forensics, IT law); not an existing-resources candidate |
| 10 | Computer science, master | 2 | 35 % and 52 % | depends on the handbook; most covered rows rest on EMI bachelor modules |
| 25 | Architecture, master (took the slot of communication and media master, below the minimum cohort; see Step 8) | 2 | 0 % and 4 % | fails |
| 2 | Urban planning, bachelor | 1 | 14 % | fails |
| 6 | Civil engineering, master | 2 | 5 % and 1 %, needs labs | fails |

**How sure.** Computer science bachelor under every reading the reviews tested:

| Reading | Overlap |
|---|---|
| As marked | 68 % |
| Least-covered electives counted | 61 % |
| Rows marked covered but flagged unsure counted as not covered | 57 % |
| Reviewer's corrections (clear errors and debatable rows, incl. the German language courses) | 49 % |
| Without the two-module rule | 33 % |
| One handbook, so the range is widened by 0.10 each way | 58-78 % |

It passes in every reading except the one without Soma's two-module rule. Cybersecurity stays in the band in
every reading but the last (lowest 42 %), and needs outside teaching in all of them.

**What the numbers do not say.**

- Overlap measures content, not lectures students can share: one EMI module can cover several modules (for
  example one information security module covers three rows of a cybersecurity handbook). The
  professor-equivalents therefore count only the new modules; shared lectures may need extra groups.
- The computer science pass rests on one handbook (Regensburg); the only other offer's handbook is blocked by
  robots.txt.
- Language courses taught by the language centre are counted as covered by EMI's foreign-language slots in some
  rows; the reviewer counts these as debatable.
- Only three candidates per level were examined; candidates further down (Informatik, Elektrotechnik, data
  science, software engineering) were not.
- All marks are by AI readers with blind cross-checks; no person checked a row.

**Reviews.** Three review rounds, each recomputing every number with own code without a mismatch. Round 1: the
sheet hid real EMI partners (fixed by a fuller sheet). Round 2: credit points treated inconsistently (Soma's rule).
Round 3: no blocker; sensitivities added (without two-module covers, unsure rows not covered); minor blind-sheet
gaps remain (a region name with a space after its hyphen, some handbook codes) and are stated here.

**Scorecard.** F1 pass (rules, marking rules and code committed before every run; outputs carry hashes). F2 pass
(pre-gate score and order recomputed by test and reviewer). F3 pass (tries and reasons recorded; robots.txt
respected). F4 pass. F5 pass with the minor gaps above. F6 pass (second and third blind readers as the changed rule
says). F7 pass (test and reviewer recompute every figure). F8 pass (10 tried, 6 eligible, 3 per level). F9 pass (no
lecturer name; timetable subjects as names). F10 pass (second run identical). F11 pass after three rounds (no open
blocker). F12 pass (213 tests).

**What goes to Step 8.** The ranking's first decision is taken among existing-resources passers: computer science
bachelor only. The second decision (band passers, for information) adds cybersecurity bachelor.

## Step 8: which programme, and how sure are we?

**Question.** Of the candidates that pass the gate, which one should EMI start, and how stable is that answer?

**Rule.** `configs/funnel.yaml`, blocks `ranking`, `stress_tests` and `decision`; criteria in
`docs/criteria_funnel_step8.md`. Code: `analysis/funnel_rank.py` (8a: inputs, value functions, Monte Carlo,
PROMETHEE, the stress grid, decision) and `analysis/funnel_listspecs.py` (8b: list-changing specs). Weights as in
`configs/analysis.yaml` (demand .30, labour .20, fit .20, feasibility .15, differentiation .10, regional .05).

**A gate error corrected first.** The minimum cohort of 20 first-years drops a candidate before it takes a gate
slot; the Step 7 walk had not applied it. Communication and media master (modelled gross first-years 12) left the gate (mechatronic systems master, 13.5, would not take a slot either), and its slot
went to architecture master, which was marked the same way (92 modules, second and third reader) and fails at 2 %.

**Result.**

| Decision | Set | Result |
|---|---|---|
| First (the recommendation) | existing-resources passers: computer science bachelor only | **recommend**: 26.5 first-years new to OTH a year (central; range 7 to 88), above the bar of 15 |
| Second (for information, never a recommendation) | band passers: computer science bachelor, cybersecurity bachelor | computer science first (P(rank 1) 0.82, PROMETHEE agrees, wins 66 % of the stress grid); cybersecurity needs 10 ECTS by teaching assignments and 3 to 10 ECTS beyond what existing staff can take: outside the scope, needs new expertise |

**The recommendation in one sentence.** Start a general computer science / Informatik bachelor (modelled on OTH
Regensburg's International Computer Science); about 26 first-years a year would be new to OTH; EMI already teaches
about two thirds of it; it needs 52.5 ECTS of new teaching, 50.5 ECTS as new modules by current lecturers and 2 ECTS
by a teaching assignment, about 1.2 professor-equivalents, and no new lab.

**How sure: what keeps it and what breaks it.**

| Reading | Recommendation |
|---|---|
| Least-covered electives (61 %), unsure rows not covered (57 %), band 0.5-0.8 or 0.3-0.9, both band ends on all EMI modules, primary handbook only, minimum cohort 25 for this unit, one-passer bar 10 | stays |
| Measured as the plain Informatik types (13 or 242) instead of the small "Computer Science" type | stays (18.1 and 20.2 new first-years) |
| Same, with minimum cohort 25 | breaks (gross 20.9 and 23.2) |
| A cap on new modules by current lecturers (20 or 10 ECTS; it needs 50.5) | breaks |
| At most 50 % from one existing programme (it has 57 % from Medieninformatik) | breaks |
| Without the two-module rule of Step 7 (overlap 33 %) | breaks: no candidate passes; closest cybersecurity at 35 % |
| The project's former strict rule (80 % covered, at most 20 % new) | breaks: no candidate passes |

In the full stress grid (17.9 million combinations of the 20 pre-registered factors) the recommendation holds in
22 %; in the other 78 % no candidate passes at all, entirely because of the two caps above. Under the agreed rules
(no cap on new modules, 80 % from one programme) it holds.

**Why "computer science" and not "Informatik".** Step 2 split the field into a small type of mostly English-titled
"Computer Science" offers (type 312: 3 similar offers in Germany, 2 within 150 km) and large "Informatik" types
(13: 30 within 150 km; 242: 13). The small type looks rare and keeps almost no students in OTH's region (0.5 %),
which are artefacts of the split. The programme is a general Informatik bachelor; measured as types 13 or 242 the
recommendation stays, but its demand is lower (18 to 20 new first-years). In the information-only comparison,
as type 13 cybersecurity comes first; as type 242 Informatik is first with P(rank 1) 0.72, below the bar (shortlist). Type 13's labour value rests on a keyword with no ads and is
flagged.

**The information-only comparison is close.** Computer science is first with P(rank 1) 0.82 under the rule's
reading; it falls to 0.77 or 0.78 with more weight uncertainty (concentration 10) or with the competition half
drawn uniformly over 1 to 5, below the bar of 0.8 (then "shortlist").

**List-changing specs (8b).** 18 of the 25 pre-registered spec values were run from stored data (17 list specs and
the former strict feasibility rule). Computer science
bachelor stays the first bachelor that can take a slot in 16 of them; under the widest similarity radius it is
third. 5 or 6 of the 6 gate candidates stay in the first 20 in every spec. Not run (7 values), because Steps 2, 3 or 5
would have to run again: boilerplate scan from 10, the former clustering setting, the four keyword variants, and one
common similarity radius. The radius specs change only the competition input.

**Second-handbook check (public data only).** The recommendation rests on one handbook, because the only other
offer of its type at a university of applied sciences blocks scripts. As a check, one plain Informatik bachelor
handbook (TH Ingolstadt, type 242, the largest Informatik type) was marked the same way in its own files (31 modules;
second reader on 14 rows, sample 0 of 10 different; third reader on 1 row). It does not change the gate or the
decision.

| | TH Ingolstadt, Informatik (check) | OTH Regensburg, International Computer Science (gate) |
|---|---|---|
| Share EMI already teaches | 66.7 % | 68.2 % |
| Least- / best-covered electives | 66.7 % / 66.7 % | 61.2 % / 75.2 % |
| Unsure covered rows not covered | 63.6 % | 57.0 % |
| Without the two-module rule | 31.5 % | 33.0 % |
| Largest share from one programme | 52.7 % (Medieninformatik) | 56.7 % (Medieninformatik) |
| New teaching (N / T / X ECTS) | 55.0 (50.0 / 5.0 / 0) | 52.5 (50.5 / 2.0 / 0) |
| Professor-equivalents | 1.22 | 1.17 |
| Verdict | would pass with existing resources | passes with existing resources |

The result does not hang on Regensburg's international programme; it hangs, for both handbooks, on counting two EMI
modules together.

**Decisions on the open questions (Soma: existing resources only, public data only).** New modules by current
lecturers count as existing resources (the supervisor's 40 % measure accepts up to 60 % new content); they are stated
as the condition, not capped. One handbook is what the rule allows; the check above adds a second, public one. The 7
stress values that need Steps 2, 3 or 5 again stay a stated limit.

**Limits.** One handbook carries the gate result (a second, public one confirms it). All module judgements are by AI readers. The two-module rule of
Step 7, without which no candidate passes, was set knowing the second-pass result. Competition, trend and overlap
enter the score more than once (`ranking.disclosed`). Competition counts are not validated (Step 3). "New to OTH" rests on the nearest OTH programme as a stand-in (Step 6). The overlap measures
content, not lectures students can share.

**Reviews.** Two review rounds on 8a and one on 8b; every number recomputed independently. Fixed: the competition
half drawn over 1 to 5 as the rule says; decision sentences with the split of new teaching; the cache of the stress
grid ignored the reference reading (win shares corrected); the Informatik types shown next to the recommendation;
8b supply cut, measure and notes.

**Scorecard.** D1 pass. D2 pass. D3 pass (test recomputes every input). D4 pass. D5 pass. D6 pass. D7 pass (17.9
million specs counted; test guards the cache). D8 pass after round 1. D9 partly: 18 of 25 spec values run, 7 named as
not run with the reason. D10 pass. D11 pass after the final fact check and its wording corrections. D12 pass.

## Re-check and rules version 4

An independent re-check after Step 8 (`docs/funnel_recheck.md`) confirmed the arithmetic and the band pass of an
Informatik bachelor (49-68 % on two handbooks), but not that it is the only programme EMI can run, that it attracts
the most students, the 26 new to OTH, or freedom from bias. The result is therefore preliminary. Soma approved rules
version 4 (`docs/funnel_rules_v4.md`; `version_4` in `configs/funnel.yaml`; marking rules version 4) before any rerun:
merged Informatik candidate, module check for every EMI-field candidate in the first 20, facts-based marking with
strict / lenient and content / size readings, a person check of the deciding rows, "new to OTH" as scenarios, and a
recommendation only from firm passers. The criteria for the rerun (V1-V9) are in `docs/funnel_rules_v4.md`.

## Rules version 4, R1: one candidate per programme title

Code `analysis/funnel_merge.py`; criteria and exact readings E1-E9 in `docs/criteria_funnel_v4_merge.md`; outputs
`data/interim/funnel4_units.csv`, `funnel4_candidates.csv`, `funnel4_gate_order.csv`, report
`reports/funnel2/v4_merge.md`.

**What changed.** Units of one level whose types share a normalised main title are one candidate, with their
complete-linkage partners one hop out. All 1,285 units fall into 723 candidates; 219 are on the list (version 3: 268
candidates). 23 title groups (62 units) drop whole because OTH already has a programme of that
title (among them Elektrotechnik und Informationstechnik, Medieninformatik, Wirtschaftsinformatik, Mechatronik and
the KI bachelor). Pool, trend, competition, job ads, EMI-field score, first-years and the new-to-OTH scenarios are
computed again on every merged candidate.

**Result: the gate order changes at the top.** Version 3's first candidate, "Computer Science" (type 312), is now part
of one Informatik bachelor (types 13, 149, 203, 242, 268, 312, 421, 488) at **order 79** (pre-gate score 2.39):
38 similar offers within 150 km (differentiation 1.0), job-ad measure 0 within 100 km (labour 1.0), net-new 18.1
(gross 21.9; break-even share from OTH 31 %). The first 20 now hold 11 bachelors and 9 masters; EMI-near candidates
among them include cybersecurity (2), business analytics and data science (3), technische Informatik (5),
Elektrotechnik (8), systems engineering (12) and data science (13, mixed). Which of them are EMI-field is decided in
the next step (R2).

**Artefact A1 (open, Soma to decide).** The job-ad measure of a merged candidate is the median over the union of its
types' keywords (rule `version_4.title_merge.measures`). For Informatik that union has 8 keywords: "informatik" has
685 ads within 100 km, "computer science" 33, "angewandte informatik" 9, and five niche phrases have 0, so the median
is 0. With the version-3 keyword rule applied to the merged titles (3 phrases: informatik, angewandte informatik,
computer science; median 33) Informatik would rank 29, still outside the first 20; with type 312's own 359 it would
rank 3. Changing the measure now would be a deviation after seeing the result; it is not applied.

**Scorecard.**

| # | Criterion | Target | Result | Pass |
|---|---|---|---|---|
| M1 | Every unit in exactly one candidate | 1,285, none twice | 1,285, none twice | yes |
| M2 | Partners of two or more title groups listed | listed | 27 units (E3), 37 partners of a dropped title group (E5), in `funnel4_merge.json` | yes |
| M3 | One-unit candidates equal version 3 | all equal | asserted in code for every one-unit candidate | yes |
| M4 | Fresh reviewer recomputes 5 candidates | no wrong number | 85 of 85 values match; 4 code-to-rule differences, 3 fixed (square brackets, candidate number, negative break-even flagged), 1 kept (a candidate may carry the number of a dropped type) | yes |
| M5 | Version-3 first 20 shown in the new order | shown | `reports/funnel2/v4_merge.md` | yes |
| M6 | Second run gives the same hashes | same | same | yes |
| M7 | Tests | all pass | 20 new tests pass | yes |
| M8 | Code committed before the run | clean stamp | clean | yes |

**What we achieved.** We counted Informatik as one programme instead of several small groups, as the re-check
asked. Measured that way it has a lot of competition nearby and drops from first to 79th in the order of candidates
to check. Other EMI-near programmes, such as cybersecurity, technische Informatik, data science and Elektrotechnik,
are now near the top. One open point: the job measure gives Informatik 0 ads because rare keyword variants pull the
median down; fixing it would still leave Informatik at 29th.
