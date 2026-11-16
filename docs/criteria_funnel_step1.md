# Criteria for funnel Step 1 (data inventory)

Written and committed before the Step 1 code is written. Step 1 looks at no programme type and scores nothing.

| # | Criterion | Target | How it is checked |
|---|---|---|---|
| D1 | Every data source named in the data table of `docs/funnel_preregistration.md` is in the inventory with its path, size, period, retrieval date and gaps | 11 of 11 rows | generated inventory against the table |
| D2 | First-years by subject are downloaded for the 15 Laender other than Bavaria | 15 of 15 files without error, each covering 2019-2024; a Land that fails is named | `docs/genesis_manifest.json` |
| D3 | The two timetable PDFs are read completely and correctly | all 160 pages; every subject code in a weekly grid is in that group's subject list (100 %); four pages read by eye match the table in every cell (subject, lecturer label, room) | parser report; spot-check table for Soma |
| D4 | No lecturer name leaves the protected folder | 0 names in tracked files and in `data/interim`; the name-to-label table exists only under `data/raw/oth_internal/` | search for the surnames |
| D5 | The matching threshold for Step 7 is fixed | `calibrate()` reproduces the value in the earlier feasibility report to 3 decimals; the value is in `configs/funnel.yaml` | test |
| D6 | The repository works | `python -m pytest` passes completely, including the test that failed in Step 0 | test run |
| D7 | Code before results | the Step 1 code is committed before it runs; the inventory carries that commit hash; the working tree is clean at run time | inventory header, `git log` |
| D8 | Every number in the Step 1 notes is right | 0 wrong claims in a fresh-context check against the generated inventory | reviewer |
| D9 | No look at results | no clustering, scoring or candidate list is produced; no run-1 result file is opened except to count files | reviewer, code |
| D10 | Downloads follow the project rules | official API only, 2 s delay, source recorded in `configs/sources.yaml` and the manifest | code, manifest |

If a criterion still fails after 3 rounds, the step stops and Soma is told. No criterion is loosened.
