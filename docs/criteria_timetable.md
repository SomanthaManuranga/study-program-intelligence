# Criteria: timetable parser and capability map (fixed before building)

Input: the two EMI timetable PDFs from the supervisor (winter 2026/27, summer 2026) in `data/raw/oth_internal/`
(git-ignored). Code: `python -m study_program_intelligence.transform.timetable`.

| # | Criterion | Target |
|---|---|---|
| T1 | Every semester group in both PDFs is parsed | groups parsed = grid pages in the PDFs |
| T2 | Every timetable entry has a module code that is in its group's legend | 100 % |
| T3 | Entries with a lecturer | at least 95 %; the rest listed |
| T4 | Hand check: 3 groups compared with the PDF page, entry by entry | no missing or wrong entry |
| T5 | No lecturer name in any file outside `data/` | names only in `data/interim/timetable_lecturer_key.csv` |
| T6 | Outputs: sessions table, module list, capability map per lecturer label, room list | all four written |
