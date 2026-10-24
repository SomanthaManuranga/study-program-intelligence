# Study Program Intelligence - project guide for Claude

## What this is
AI Project course, OTH Amberg-Weiden (Prof. Dr.-Ing. Thomas Nierhoff), WS 2026/27, team of 2.
Brief: use public data (Destatis, other universities' websites, ...) to find and argue which NEW study
programme would attract the most students and why it suits our faculty.
Deadlines: analysis freeze 4 Dec 2026; submission 10 Jan 2027 23:59; presentation 11 Jan 2027.

## Scope (binding; confirmed by the supervisor)
1. **Existing resources only:** the new programme must be feasible with EMI's existing staff and labs (no new
   professorships, no new labs). The pre-registered test is in docs/rescope_plan.md (once approved).
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
   (48 counts, about 2 minutes; a rerun on the same day replaces that day's rows). Done when: 48 counts without ERROR
   for the date, docs/jobsuche_snapshots.json committed and pushed. No pipeline rerun: the report stays on the 15 Oct
   snapshot until the freeze.
2. Analysis freeze 4 Dec 2026: full pipeline rerun from the frozen data; move JOB_SNAPSHOT in report/key_numbers.py to
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

Current: re-scope week 2 (docs/evidence_feasibility.md). The cyber options fail the feasibility rule; robotics path B
(assistive / service) passes pending Soma's hand-check confirmation (configs/feasibility_handcheck.yaml); recombination
clusters and rarity screen give six proposed week-3 candidates, pending Soma's review of labels and verdicts. Fixed date:
job-ad snapshot on 1 Nov 2026 (item 1). Done: data-sufficiency audit
(docs/data_gap_audit.md) with items G1, G3, G4, G5 and the German-only trend scores (reviewed by Soma); Step 56 defence
Q&A updated, fact-checked (docs/data_sufficiency_review.md) and reviewed by Soma.
Open for the team: the research protocol requires that AI-related scores are checked by the second team member; this
check is not recorded yet. Title page of the report: second author and supervisor still placeholders.

## Rules
- Never print or commit secrets. .env holds GENESIS_TOKEN, CONTACT_EMAIL and the GENESIS-Bayern credentials; load via
  ingest/documents.py load_env().
- Public data only; no intake or admission figures from universities.
- data/ and generated reports (reports/) are git-ignored on purpose; regenerate them with the pipeline. Commit code,
  configs and docs only (exception: docs/theme_labels.csv, the reviewed theme labels).
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
