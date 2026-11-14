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
