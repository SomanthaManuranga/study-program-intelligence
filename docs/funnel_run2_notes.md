# Funnel rerun: notes per step

Short notes on what each step found and why each programme stays or goes. Rules: `configs/funnel.yaml`. Generated
tables: `reports/funnel2/` (not committed). The full documentation is written after Step 8.

## Step 0: which rules decide?

All rules and thresholds are fixed in `configs/funnel.yaml` before any data is touched. They hold the supervisor's
answers and a fix for each problem of run 1 (`docs/funnel_preregistration.md`). No programme was looked at.

## Step 1: is the data there and current?

**Question.** Does every rule have the data it needs, how old is it, and what is missing?

**Rule.** Data table in `docs/funnel_preregistration.md`; criteria in `docs/criteria_funnel_step1.md`. Inventory run
on 14 Nov 2026 with code commit 9544d62 on a clean working tree.

**What is there.**

| Source | Size | Period or date | Gaps |
|---|---|---|---|
| Study catalogue | 22,093 offers; 19,872 bachelor and master offers in Germany after merging variants (9,703 bachelor, 10,169 master), 14,902 of them full-time, at 404 institutions | retrieved 19 Oct 2026 | 10,183 offers have only the phrase "Inhalte bitte bei der Hochschule erfragen" as content; focus items exist for 48 %; no language-of-instruction field; 1 offer without a Land |
| Subject labels to Destatis codes | 396 labels in use, all with a code | - | none |
| EMI modules | 447 modules (333 bachelor, 114 master) from 14 handbook sets; 46 OTH offers in the catalogue; 23 labs listed | handbooks retrieved 19 Oct 2026 | 38 modules without ECTS |
| First-years and graduates by subject, Bavaria and Germany | 4 tables, 297 subjects each | 2005-2025, retrieved 14 Oct 2026 | none |
| First-years by subject, other Laender | 15 of 15 Laender, 297 subjects each | 2018-2025, retrieved 14 Nov 2026 | none |
| Job ads | 3 snapshots: 48, 48 and 92 counts, 23 old keywords | 15 Oct, 17 Oct, 7 Nov 2026 | the new keywords have no history; they are counted on one day in Step 5 |
| School leavers by county | 96 counties | 2014-2024 | 2019 is missing |
| Students by campus (master origins) | 17 campuses, 83,481 students | winter 2024/25 | none |
| Published first-year numbers of single programmes | 3 documents from 2 universities | 2024, 2025 | one subject only |
| Reference handbooks | 27 files left from run 1, not opened | - | collected again in Step 7 |
| EMI timetables (internal) | 80 group plans (40 per semester), 1,028 timetable entries, 314 subject names, 98 lecturers as labels | summer 2026, winter 2026/27 | no ECTS, no hours, no student numbers |

**New in this step.**

- First-years by subject were downloaded for the 15 Laender other than Bavaria (Destatis table 21311-0015, official
  API, 2 s delay). Each file was checked to hold its own Land. This makes the north/south check possible at the
  level of subjects.
- The two timetable PDFs were read into one table: per group and day, the subject, the lecturer as a neutral label
  and the room. 160 of 160 pages were read and no text of a weekly grid was left over. 19 subjects are listed for a
  group without a weekly slot (block courses or dates by arrangement); they are kept without a lecturer. Four pages
  were compared by eye with the PDFs: 59 of 59 cells match. The PDFs, the name-to-label table and the spot-check
  sheet stay in `data/raw/oth_internal/`, outside the repository.
- The matching threshold for Step 7 is fixed at 0.285 (`feasibility_gate.covered_threshold`). The existing
  calibration procedure gives exactly the value of the earlier feasibility report. Its quality is moderate
  (true-positive rate 0.66, false-positive rate 0.14, AUC 0.762, on 80 positive and 88 negative reference modules),
  which is why every match in Step 7 is checked by hand.
- The test that failed in Step 0 is repaired. It compared the baseline tie-break table with the newest job-ad
  snapshot, but the baseline stays on its own snapshot (17 Oct) until the freeze. The test now checks every count
  against the snapshot of the date named in its row. The baseline table and `docs/evidence_tie_break.md` are
  unchanged. All 124 tests pass.

**What this means for the next steps.**

- Step 2: about half of the offers (10,183) have no content beyond a boilerplate sentence. After that sentence is
  removed they are grouped by title and subject labels only. The two rule files Step 2 needs
  (`configs/funnel_boilerplate.yaml`, `configs/funnel_title_stoplist.yaml`) do not exist yet and are written first.
- Step 5: the catalogue has no language field, so German and English keywords cannot be paired by rule
  (`labour.english`); this is a stated limit.
- Step 7: 252 of 447 EMI module titles appear word for word among the timetable subjects. This is a first look
  only; Step 7 matches by content and by hand.
- All 18 old topic lists are available for the validation in Step 2.

**No programme stays or goes in this step.** Nothing was grouped or scored.

**Strongest objection.** The catalogue is a single snapshot of 19 Oct 2026 and half of it has no content text.
**Answer.** It is the only complete public catalogue; the date is stated, and the grouping in Step 2 reports its
results separately for offers with and without focus items.
