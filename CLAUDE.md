# Study Program Intelligence - project guide for Claude

## What this is
AI Project course, OTH Amberg-Weiden (Prof. Dr.-Ing. Thomas Nierhoff), WS 2026/27, team of 2.
Brief: use public data (Destatis, other universities' websites, ...) to find and argue which NEW study
programme would attract the most students and why it suits our faculty.
Deadlines: analysis freeze 4 Dec 2026; submission 10 Jan 2027 23:59; presentation 11 Jan 2027.

## Scope (binding; confirmed by the supervisor)
1. **Existing resources only:** the new programme must be feasible with EMI's existing staff and labs (no new
   professorships, no new labs). The supervisor's own measure: 40-80 % of the new programme should overlap with
   existing lectures (more = relabelled programme, less = too many resources); a whole new degree, not extra modules.
   He gave no minimum cohort. Earlier test: docs/rescope_plan.md; funnel test: configs/funnel.yaml.
2. Competition and trends: Germany-wide. Student numbers: Bavaria and the OTH catchment.
3. Bachelor and master both allowed.
4. Target group: German AND international students.
5. EMI fit only (faculty Elektrotechnik, Medien und Informatik).
6. Success measure: students new to OTH (not taken from existing OTH programmes).
7. Full-time programmes only; part-time is at most a minor variant.
8. Programmes that are rare or not yet offered in Germany are explicitly welcome (example: Motorsport Engineering,
   only Stralsund and Amberg). Neighbouring countries optional (supervisor unsure it helps).
9. Internal OTH data: the supervisor will ask; do not plan around it. Public data only.

## How to work with me (Soma)
- **Standing rule for every step: Build -> Evaluate -> Iterate -> Report.** Write the criteria and thresholds down
  BEFORE building (committed first). Score your own output against them, run the tests, have a fresh-context reviewer
  check every factual claim, fix what fails and repeat, at most 3 rounds. Then report a scorecard (criterion, target,
  result, pass/fail, what was fixed). If a criterion still fails after 3 rounds, stop and tell Soma; never loosen a
  criterion to make it pass.
- No AI attribution in commits, pull requests or repo files (no "Co-Authored-By" or "Generated with" lines).
- Work in numbered steps (Step N), one step at a time. Each step ends with a "Done when" check.
- After giving a step, wait until I report back or paste the output. Check the result against "Done when".
  Only move to the next step when it succeeded; otherwise help me fix it (same step number).
- After each finished step, update "Current step" below and commit it with the step's other changes.
- Git: never commit or push to main. Work on a personal topic branch (soma/<topic>; the collaborator uses
  <name>/<topic>), commit there, and push that branch after each step passes its "Done when" check without asking.
  Work reaches main only through a reviewed pull request (CONTRIBUTING.md). Keep the branch up to date by merging main
  into it; never rewrite or force-push main.
- Spot checks for me: an English side-by-side table (what was extracted or claimed, the source text, where it is)
  so I only compare, never search.
- Plain English, blunt, evidence-based. Numbers with sources. Say clearly when evidence is weak.
- Style for all .md files (CLAUDE.md, README, docs): no unnecessary dates or history; keep only the most important,
  relevant details. Keep real deadlines (freeze, submission, presentation). Dated records belong in
  docs/decision_log.md only.
- Windows + PowerShell. Python venv in .venv (activate: .venv\Scripts\Activate.ps1). Run modules from repo root:
  python -m study_program_intelligence.<package>.<module>
- Do the file edits, test runs and git commits yourself; I only do manual downloads that robots.txt or logins block.

## Current step
Done: evidence (Steps 37-45), modelling (Steps 46-49), key numbers / figures / report / dashboard / pipeline / claim
review (Steps 50-52, 54, 55), defence Q&A (Step 56), preliminary plain-English summary (Step 57 preliminary),
data-sufficiency audit with its collected items.

Remaining work, in this order:
0. Re-scope to existing resources (Scope constraint 1): plan in docs/rescope_plan.md (approved), timeline there
   (decisions R1-R6). The current results are the "baseline: with new resources" (tag baseline-new-resources).
1. Job-ad snapshots on 1 Nov, 15 Nov and 1 Dec 2026: `python -m study_program_intelligence.ingest.jobsuche snapshot`
   (92 counts: 23 keywords x 4 regions since the tie-break keywords were added, about 4 minutes; a rerun on the same
   day replaces that day's rows only when it is at least as complete). Done when: 92 counts without ERROR and no null
   totals for the date, docs/jobsuche_snapshots.json committed and pushed. No pipeline rerun: the report stays on the
   15 Oct snapshot until the freeze.
2. Analysis freeze 4 Dec 2026: full pipeline rerun from the frozen data; move JOB_SNAPSHOT in report/key_numbers.py and SNAPSHOT_UNTIL in analysis/tie_break.py to
   the frozen snapshot; add the snapshot series (15 Oct to 1 Dec) to docs/evidence_outlet_jobs.md; regenerate key numbers, figures, report,
   defence Q&A, dashboard screenshots.
3. Step 57 Plain-English project summary: a short PDF (about 10-15 pages) for readers with no data-analytics
   background; simple language, every technical term explained in one sentence or avoided, the key figures, and clear
   answers to: what was the question, what did we do, what did we find, what do we recommend, how sure are we, what
   are the limits. Numbers from key_numbers.yaml as in the report. The final PDF is committed (.gitignore exception
   for reports/final/project_summary.pdf only). Final README update at the same time: keep Soma's current README
   structure (the AI-tools and timeline sections were removed on purpose; do not re-add).
   Done when: PDF built from key numbers, reviewed by Soma, committed and pushed with the README update.
4. Phase 5 (LOCKED until Step 57 is finished and every baseline step is complete): a deep evaluation of the whole
   pipeline from a senior data-analytics perspective, comparing an improved approach with the baseline. Do not start
   or plan it; Soma gives the full instructions then.
5. Step 53 Slides for 11 Jan 2027 (last, so they show the final results). Open questions: format (generated .pptx vs.
   hand-made), time limit, OTH template, live demo. Done when: deck complete within the time limit, every number from
   key_numbers.yaml.

Current: re-scope week 3, merged into main. Three-level answer in docs/evidence_tie_break.md: (a) strict existing
resources: no candidate passes (robotics path B fails F2 only: 15 ECTS of new modules by existing professors, cap 10;
the cap is the project's own operationalisation, pre-registered in configs/feasibility.yaml); (b) lenient
sensitivity: robotics path B passes as a conditional candidate (first-years 14.9 / 28.6 / 55.1, 0.52
professor-equivalents, no new position); (c) with investment: the cybersecurity baseline (3.22 professor-equivalents).
The binding open condition for (b) is the faculty's answer on absorbing about 15 ECTS of new teaching. Demand
thresholds are pre-registered (configs/demand_thresholds.yaml); the demand ranking is rerun after the 1 Nov job ads
and the Google Trends tie-break download (terms in docs/evidence_tie_break.md). The external review's fixes and the
deep-analysis layer are in (docs/evidence_deep_analysis.md, docs/argument_brief.md). E8 of the capture/cost/demand
step is recorded as failed; its wording fix is checked in the claim review of the report rewrite. The report, README
result, summary, Q&A and dashboard still show the baseline and are rewritten before the freeze. Main is protected:
changes go through a pull request with one approval and the tests check.
Open for the team: the research protocol requires that AI-related scores are checked by the second team member; this
check is not recorded yet. Title page of the report: second author and supervisor still placeholders.

Funnel redo (branch soma/funnel): the programme must come out of the data, not from hand-picked candidates. Run 1 is
not a result (docs/funnel_run1_review.md); its code and write-up were removed (git history only). Rules version 3: configs/funnel.yaml, docs/funnel_preregistration.md
(supervisor's input, run-1 fixes, what was known beforehand). One step at a time, each with Soma's OK and a short
plain-English paragraph on what was achieved; notes per step in docs/funnel_run2_notes.md; full documentation only at
the end. Steps: 0 rules (done), 1 data inventory (done), 2 programme types, 3 screen and competition by content similarity,
4 student trend, 5 job ads, 6 first-years new to OTH, 7 feasibility on two curricula (AI readers),
8 ranking, stress tests, decision. Steps 2 to 8 are done (8b partly: 7 of 25 spec values not run, Soma to decide). The supervisor's timetable PDFs are internal: they
stay outside the repository and lecturers appear only as neutral labels. Settled by Soma: only existing facilities
count (the recommendation comes only from candidates existing staff and labs can carry); the 40 % end is overlap
with all EMI modules, the 80 % end is the share from one existing programme. Progress notebook for the meetings with
the supervisor: notebooks/funnel_progress.ipynb, one section added and executed after every finished step.
Step 1 added: first-years by subject for all 16 Laender (data/raw/destatis/21311-0015_<Land>.csv), the timetable table
(transform/timetables.py -> data/interim/timetable_subjects.csv, labels only), analysis/funnel_inventory.py and
funnel_common.py (universe(): the one offer list for all steps; run_stamp(): code is committed before a step runs).
Step 1b: the matching threshold for Step 7 is 0.463, calibrated on EMI's own handbooks only (analysis/funnel_modules.py;
vectors() is the one text preparation for module matching). It is flagged weak and does not carry over to other
universities; the matcher ranks well (true partner in the top 3 for 74 %) but no cut-off is reliable. Settled by Soma:
no threshold decides in Step 7. A fresh-context reviewer marks every row from the three closest EMI modules by marking
rules written first; Soma checks 10 rows per candidate and marks all rows of a candidate whose sample fails.
Step 2 (analysis/funnel_types.py: scan, embed, run; rule file configs/funnel_boilerplate.yaml; the Step 5 list
configs/funnel_title_stoplist.yaml was committed with the Step 2 code): the pre-registered rule gave 63 stable and 229
rare types that failed the reader's check (17 of 30 types hold one kind of programme, stable types alone 14 of 30;
bar 24). Soma changed three rules: the finest
setting of the grid is used, left-over groups too large for the rare path are kept as mid-sized types, and Step 3
reads every type that survives the screen (`screen.type_coherence`; a mixed type is flagged and takes no gate slot
without a full reading). Redo: 824 types (233 stable, 130 mid-sized, 461 rare; mid-sized and rare are flagged as not
stability-tested), reproducible; reader's check 22 of 30, still below the bar, so G9 stays recorded as not passed.
Outputs for the next steps: data/interim/funnel2_offer_types.csv, funnel2_types.csv, funnel2_centroids.npy,
funnel2_embeddings.npy. Details in docs/funnel_run2_notes.md. `run <size> <method>` is a diagnostic mode, never a result.
Step 3 (analysis/funnel_units.py: items, labels, run, sheet): three rules did not work with the finer types and were
changed, confirmed by Soma (merged groups without chaining; EMI-field score against module titles with a bar from
300 units marked by an AI reader, docs/funnel_emi_labels.csv; "at OTH" when an OTH offer belongs to the type or lies
within its median distance). Result: 1,285 units,
365 on the primary list (268 candidates), 1,241 on the stress list; the EMI screen is a generous filter (about half
of the list is outside EMI's field by the marks); 75 of the 247 types on the list are flagged "mixed"
(docs/funnel_type_coherence.csv). The check of "similar" (100 offers, marked by three AI readers by Soma's decision) failed in both rounds (46 % / 40 %
and, with a common radius, 64 % / 46 % yes inside / outside; needed 70 % / 30 %): all competition counts are flagged
"not validated" and the offers half of the differentiation value takes the range 1 to 5 in the ranking
(data/interim/funnel2_similarity_result.json, _2.json; docs/funnel_similarity_marks.csv, _2.csv).
Step 4 (analysis/funnel_demand.py): student numbers of every unit's subject pool (data/interim/funnel2_demand.csv).
On the primary list 128 units have a growing and 229 a falling German pool in Bavaria (median -2.0 % a year); foreign
students grow (+9.3 %). Trends are weak evidence: naive is the best model on average (MASE 2.01), so the 2030
projection is the last value; only 51 units (23 primary) have a validated trend.
Step 5 (analysis/funnel_labour.py: keywords, fetch, measure): keywords by rule from programme titles
(docs/funnel_keywords.csv, committed before the first request), job-ad counts of 15 Nov 2026
(data/interim/funnel2_job_counts.csv, funnel2_labour.csv). Primary list: all 365 units counted; median 22 ads within
100 km for the median keyword. The measure counts words in ads, not jobs for graduates: general words lead
(mechatronik, management), 82 units reach the scale's top of 150 and 152 are below its bottom of 10. The job board
reads a bare "Amberg" as Amberg bei Buchloe: the place is sent as "Amberg, Oberpfalz" and checked in every reply.
OPEN for the baseline: its job snapshots (docs/jobsuche_snapshots.json, regions amberg_50km and amberg_100km) have
this error, so "191 ads within 100 km" in the Findings is not valid until configs/jobsuche.yaml is fixed and the
snapshot is taken again.
Step 6 (analysis/funnel_capture.py -> data/interim/funnel2_capture.csv): gross first-years = anchor (German students
of the pool in Bavaria per Bavarian offer of the pool) x scale (Huff model against the unit's Bavarian comparator
sites); net-new = gross minus the share from OTH's offer. Primary list: gross median 24.2, net-new median 16.5; 140
of 365 units below the minimum cohort of 20 (a flag, nobody removed). Rough sizes only, not a ranking: thin anchors
and single comparators lead the top (flag columns in the table), and "new to OTH" rests on the nearest OTH offer,
which lies within the type's radius for 33 units only. OPEN for Soma before Step 8: a floor for the anchor's
denominator, a scale shrunk towards 1 with few comparators, net-new where the OTH site is a placeholder; and for
Step 7: who checks the AI reviewer's rows, since Soma does no hand work.
Step 7 (analysis/funnel_shortlist.py, funnel_refs.py, funnel_feasibility.py; notes in docs/funnel_run2_notes.md):
10 candidates tried, 6 eligible, 421 modules of 10 handbooks marked by AI readers in three passes (rules version 3:
content counts, two EMI modules may cover one; no person checks, by Soma's decision). Computer science bachelor
passes with existing resources (68 %, one handbook, 52.5 new ECTS, about 1.2 professor-equivalents; 49-61 % under
the reviewers' stricter readings, 33 % without the two-module rule). Cybersecurity bachelor is in the band (63 / 58 %)
but needs outside teaching. Computer science master depends on the handbook (35 / 52 %); urban planning, civil engineering and architecture master fail.
Step 8 (analysis/funnel_rank.py 8a, funnel_listspecs.py 8b): recommendation = a general computer science /
Informatik bachelor (type 312, modelled on OTH Regensburg's International Computer Science): 26.5 first-years new to
OTH, 52.5 ECTS new teaching (50.5 N, 2 T), about 1.2 professor-equivalents, no new lab. It holds under the agreed
rules and as Informatik types 13 / 242 (18-20 new first-years), but breaks with a cap on new modules, with at most
50 % from one programme, without the two-module rule, and under the former strict rule; it holds in 22 % of the stress
grid and has no passer in the other 78 %.
A second, public handbook (TH Ingolstadt Informatik, check only) confirms it: 66.7 %, 55 ECTS new teaching, 1.22
professor-equivalents. Cybersecurity bachelor is second for information only (needs new expertise). The gate walk now applies the minimum
cohort (architecture master took the slot of communication master).
Re-check after Step 8 (docs/funnel_recheck.md): the arithmetic holds, but "only candidate", "most students", "26 new to OTH"
and "without bias" are not established; README, explainer and notebook say so and call the result preliminary. Soma
decided for the rerun: module check for every EMI-field candidate in the first 20, strict and lenient marking both
reported, Soma and the teammate check the rows that decide outside teaching. Rules version 4 are drafted in
docs/funnel_rules_v4.md, approved and committed. R1 merge done (analysis/funnel_merge.py, notes in docs/funnel_run2_notes.md):
merged Informatik bachelor at gate order 30 after the job-ad deviation (79 as written), checked as a control; next R2 (EMI-field marks
for the first 20, module checks).
Read data/interim/funnel2_screen.csv with float_precision="round_trip". The label CSVs in docs/ are tracked
(exceptions in .gitignore).

## Rules
- Never print or commit secrets. .env holds GENESIS_TOKEN, CONTACT_EMAIL and the GENESIS-Bayern credentials; load via
  ingest/documents.py load_env().
- Public data only; no intake or admission figures from universities.
- data/ and generated reports (reports/) are git-ignored on purpose; regenerate them with the pipeline. Commit code,
  configs and docs only (exception: docs/theme_labels.csv, the reviewed theme labels), and results/: the funnel's
  final tables, copied by `python -m study_program_intelligence.analysis.funnel_results` (derived data only; never raw
  downloads, module text of other universities or internal files).
- Scraping: respect robots.txt (allowed_by_robots in ingest/documents.py), User-Agent with CONTACT_EMAIL, delay 2 s for
  the APIs and at least 3 s (or the site's Crawl-delay) for documents, cache raw replies, record every source in
  configs/sources.yaml and a manifest in docs/. Hochschulkompass search pages and OTH /fileadmin/ are disallowed ->
  manual download by me. OTH /files/ (current module handbooks) is allowed and fetched by script. Check robots.txt
  before fetching any page of a new host, also for one-off checks.
- Anything blocked by robots.txt or a login: do not work around it; skip it and state it as a limitation.
- Professors are shown as neutral labels (Prof. A-N), never by name; OTH person pages are not read.
- Every method decision goes into docs/decision_log.md (date, decision, reason, decided by).
- Report, dashboard and slides: numbers only from reports/key_numbers.yaml (placeholders), never typed by hand.
- Windows Notepad escapes Markdown (\#, \_) when saving .md files; if you see that, fix it.

## Argument structure
Four claims: A Demand, B Capture (competition/catchment), C Fit (EMI staff, labs, modules), D Outlet (jobs).
Plus incrementality test (does it cannibalise existing EMI programmes?), feasibility gate, kill rules (docs/kill_rules.md).
Final ranking: MCDA, weights in configs/analysis.yaml (demand .30, labour .20, fit .20, feasibility .15,
differentiation .10, regional .05), Monte Carlo with Dirichlet weights (10,000 draws), leave-one-criterion-out.
Forecasts validated with rolling-origin backtests (MASE).

## Code and outputs
- One command: `python -m study_program_intelligence.pipeline` (transform -> analysis -> key numbers -> figures ->
  report -> tests; --ingest, --snapshot, --from, --skip, --list, --no-tests). Checks the manual inputs first (Trends
  CSVs, OTH handbooks); writes reports/pipeline_log.md (step times, key-number changes vs. the previous run). Tests:
  `python -m pytest`.
- ingest/: documents.py (document lists in configs/*documents*.yaml, competitor_modules.yaml; manifests in docs/),
  genesis.py (Destatis GENESIS REST; POST, token in "username" header; error 98 = too large), studiensuche.py (BA
  Studiensuche = Hochschulkompass data), jobsuche.py (BA job board; snapshots in docs/jobsuche_snapshots.json).
- transform/: programmes.py (catalogue -> data/processed/programmes.csv), modules.py (TOC-anchored handbook parser),
  thm_modules.py (TH Mannheim module list from its programme page), school_leavers.py (Bavarian B I/II 1 j tables;
  2018/19 missing), pdf_numbers.py (number splitting by the table's own arithmetic).
- analysis/: themes.py + first_look.py (supply/demand), trends.py (Google Trends, manual CSVs), theme_check.py (hand
  labels in docs/theme_labels.csv), module_gaps.py (e5 + TF-IDF, CyBOK), catchment.py, labour.py, forecast.py,
  capture.py, cannibalisation.py, options.py (same capture model for all three options), ranking.py (MCDA + Monte Carlo;
  sensitivities incl. German-only trend scores), demand_split.py (German vs foreign first-years / graduates),
  out_of_state.py (students from outside Bavaria), intake_benchmark.py (published cyber intakes, plausibility check),
  theme_verdicts.py (written verdict for every theme group).
- report/: key_numbers.py (every number with its source doc, verbatim check), figures.py, outline.py, draft.py
  (docs/report/ -> reports/final/report.md/.docx/.pdf; fails on unknown placeholders or typed numbers; pandoc via
  pypandoc_binary, PDF via MiKTeX xelatex), spotcheck.py, claims.py (claim sheet for reviews).
- app/: Streamlit dashboard, local only (`streamlit run app/dashboard.py`); screenshots via `python app/screenshots.py`.
- Blocked or unusable sources: Regionaldatenbank (robots.txt), GENESIS Bayern (login falls back to guest), OTH person
  pages, TH Mannheim handbook, THI and TH Augsburg robotics handbooks. data/interim/pdf_text and module_emb.npy are
  leftovers no code uses. E&IT handbook SPO 222B not found.

## Findings (baseline: with new resources; the winner needs new staff and a lab, so it fails Scope constraint 1)
- Informatik is the only large EMI field still growing (Bavaria first-years +6.1 %/yr 2019-24; Germany flat since
  2023), but mostly through foreign students: German first-years +2.3 %/yr in Bavaria, -0.2 %/yr in Germany; foreign
  students are 77 % of the Bavarian growth. Among German first-years Informatik is still the strongest large EMI
  subject. Electrical and media fields shrink. Generic AI is crowded and OTH already offers it.
- Every theme group (18, incl. data science, health informatics, energy informatics) has a written verdict with the
  funnel's two filters; none is a stronger candidate than cybersecurity; health informatics is the closest new case.
- Cybersecurity is the clearest gap: 31 BA / 32 MA dedicated programmes in Germany (hand-checked), 4 / 6 within 150 km,
  none at OTH; nearest full-time cyber bachelor TH Ingolstadt (82 km). 126 general programmes have a security focus
  area (18 within 150 km), incl. OTH's Medieninformatik and Industrie-4.0-Informatik.
- Search interest: "Cyber Security Studium" is the largest tracked specialist term (about 2x KI, 2.6x Robotik since
  2022) but has plateaued since 2022. KI falls, Robotik flat.
- Forecast: Bavaria cyber-proxy first-years 4,936 (2024) -> central planning value ~5,540 (2030), ~6,220 (2035);
  conservative (KMK) 5,057 / 5,519; drift is the best backtest model.
- Catchment: OTH's own pool ~5,500 qualified school leavers a year (40 % FOS/BOS); little overlap with Deggendorf,
  much with Nuremberg/Erlangen; Regensburg is a third of the pool.
- Capture: Cyber B.Sc. first-years 21 / 39 / 75 at steady state (year 1: 12 / 24 / 45), anchored on THI's capacity 25
  and an anecdotal Deggendorf ~60; no comparable programme publishes its intake. Minimum cohort 20 is an assumption.
- Fit: EMI covers ~71 % of a cyber bachelor's foundations but at most ~31 % of its security content (upper end);
  missing: pentesting, forensics, SOC/incident response, software security, management, law. Needed: ~2 new
  professorships, a lab engineer, a security lab (cost open). OT is not a differentiator against TH Deggendorf.
- Outlet: "Cyber Security" 851 job ads in Germany, Bavaria 30.9 % ("OT Security" 34.6 %) vs 22-25 % baseline, 191
  within 100 km; IT jobs with a degree in Bavaria +34 %; Informatik a shortage occupation at bachelor level.
- Cannibalisation: 14-27 % from OTH programmes in the model, net new 15 / 32 / 64; kill rule 1 passed (25 % in the
  formal test); robotics overlaps 50 % with the KI B.Sc.
- Ranking: Cyber B.Sc. first in 91.7 % of draws (93.2 % with robotics at 50 % cannibalisation), first in every
  leave-one-out (lowest 67.2 % without demand). Master second, robotics last. Weak evidence widens ranges
  symmetrically, never raises a score. With German-only trend scores for all options: 78.2 % (below the 80 % bar),
  master 19.5 %; without labour relevance on top, the master is narrowly ahead (50.1 % vs 48.2 %).
- Out-of-state: 13.7 % of OTH's German students come from outside Bavaria, about as at THI and TH Deggendorf, so the
  Bavaria-only capture model is barely biased. Published cyber intakes exist only at research universities (Bochum
  156, Saarland 42; Saarland's English-taught bachelor 3): a plausibility check, not an anchor.
- English-taught cyber bachelor: not supported; fits better as an English-taught master later (proposal (a)).
