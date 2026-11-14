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
code. G12: one check round on these notes. G13 pass (170 tests). R1 pass. R3, R4, R5 pass (tests recompute the
selection, the left-over groups and all texts; 0 groups dropped, 0 texts differ). R6 measured as above.

**No programme stays or goes in this step.** By Soma's decision the types go to Step 3 with the coherence check on
every surviving type; G9 stays recorded as not passed.
