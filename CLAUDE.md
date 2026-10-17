# Study Program Intelligence - project guide for Claude

## What this is
AI Project course, OTH Amberg-Weiden (Prof. Dr.-Ing. Thomas Nierhoff), WS 2026/27, team of 2.
Brief: use public data (Destatis, other universities' websites, ...) to find and argue which NEW study
programme would attract the most students and why it suits our faculty.
Scope: faculty EMI (Elektrotechnik, Medien und Informatik); bachelor and master; public data only; all of Germany.
Deadlines: analysis freeze 4 Dec 2026; submission 10 Jan 2027 23:59; presentation 11 Jan 2027.

## How to work with me (Soma)
- Work in numbered steps (Step N), one step at a time. Each step ends with a "Done when" check.
- After giving a step, wait until I report back or paste the output. Check the result against "Done when".
  Only move to the next step when it succeeded; otherwise help me fix it (same step number).
- After each finished step, update "Current step" below and commit it with the step's other changes.
- Push after each step passes its "Done when" check without asking (standing rule, confirmed by Soma 17 Oct 2026).
- Spot checks for me: give an English side-by-side table (extracted title, ECTS, first 300 characters of
  text, PDF page number) so I only compare, never search.
- Step 41: allowed to install sentence-transformers and a multilingual model that handles German
  (e.g. paraphrase-multilingual-MiniLM-L12-v2 or multilingual-e5-base); always add a TF-IDF cross-check
  so results do not depend on one model.
- Plain English, blunt, evidence-based. Numbers with sources. Say clearly when evidence is weak.
- Windows + PowerShell. Python venv in .venv (activate: .venv\Scripts\Activate.ps1). Run modules from repo root:
  python -m study_program_intelligence.<package>.<module>
- Do the file edits, test runs and git commits yourself; I only do manual downloads that robots.txt or
  logins block.

## Current step
Step 43: BA regional labour-market / shortage data (Next steps item 1, part 2). Status: open.
Last finished: Step 42, catchment (2026-10-17): own pool ~5,500 qualified school leavers/yr (10 % of Bavaria;
3,800 without Regensburg); docs/evidence_catchment.md.

## Rules
- Never print or commit secrets. .env holds GENESIS_TOKEN and CONTACT_EMAIL; load via ingest/documents.py load_env().
- data/ and generated reports (reports/) are git-ignored on purpose; regenerate them with the analysis modules. Commit code, configs and docs only.
- Scraping: respect robots.txt (allowed_by_robots in ingest/documents.py), User-Agent with CONTACT_EMAIL,
  2-3 s delay, cache raw replies, record every source in configs/sources.yaml and a manifest in docs/.
  Hochschulkompass search pages and OTH /fileadmin/ are disallowed -> manual download by me.
- Every method decision goes into docs/decision_log.md (date, decision, reason, decided by).
- Windows Notepad escapes Markdown (\#, \_) when saving .md files; if you see that, fix it.

## Argument structure
Four claims: A Demand, B Capture (competition/catchment), C Fit (EMI staff, labs, modules), D Outlet (jobs).
Plus incrementality test (does it cannibalise existing EMI programmes?), feasibility gate, kill rules (docs/kill_rules.md).
Final ranking: MCDA, weights in configs/analysis.yaml (demand .30, labour .20, fit .20, feasibility .15,
differentiation .10, regional .05), Monte Carlo with Dirichlet weights (10,000 draws), leave-one-criterion-out.
Forecasts validated with rolling-origin backtests (MASE).

## Data collected (code -> output)
- ingest/documents.py: 8 reference PDFs (KMK forecasts, BA Engpassanalyse, HRK, IHF) -> docs/evidence_documents.md
- ingest/genesis.py: Destatis GENESIS REST, 11 tables (21311 first-year students, 21321 graduates), 2005-2025.
  Notes: POST only, token in "username" header; startyear/endyear needed; error 98 = too large (script halves
  the range); Bavaria 2025 = G9 dip, so Bavarian trends end 2024. Winter semesters only.
- ingest/studiensuche.py + transform/programmes.py: BA Studiensuche API (Hochschulkompass data),
  4,875 programme offers in Germany with distance to Amberg/Weiden -> data/processed/programmes.csv
- analysis/themes.py, analysis/first_look.py: demand and supply tables -> reports/first_look.md,
  docs/evidence_competition_demand.md
- configs/oth_portfolio.yaml: 15 EMI programmes; docs/overlap_test.md: kill rule 1
- ingest/jobsuche.py: BA Jobsuche API v6, job-ad counts by keyword x region (snapshot 2026-10-15)
  -> docs/jobsuche_snapshots.json, docs/evidence_outlet_jobs.md. Repeat snapshot every 2-4 weeks until 4 Dec.
- analysis/trends.py: Google Trends CSVs downloaded by hand into data/raw/trends/trends_*.csv
  (first term = anchor; monthly; break at 2022-01-01) -> reports/trends.md, docs/evidence_demand_trends.md.
  Two files: trends_DE_2015_2026.csv (anchor Informatik Studium), trends_DE_specialist_2015_2026.csv (no anchor).
- analysis/theme_check.py: hand-label sheet for the title theme rules (all cyber title matches + samples +
  miss check, seed 20261017) -> data/interim/theme_labels.xlsx; labels in data/interim/theme_labels_EN.xlsx
  (proposed by Claude, reviewed by Soma); score -> reports/theme_check.md, docs/theme_precision.md
- ingest/documents.py --config configs/competitor_modules.yaml (Step 39): competitor module handbooks
  -> data/raw/competitor modules/, docs/competitor_modules_manifest.json; manual ones in docs/manual_downloads.md
- analysis/module_gaps.py (Step 41): e5 (per-handbook centred) + char TF-IDF, best-match calibration, CyBOK areas,
  OT flag -> data/interim/module_scores.csv, reports/module_gaps.md, docs/evidence_fit_modules.md
- transform/school_leavers.py + analysis/catchment.py (Step 42): Bavarian school leavers by county (B I/II 1 j PDFs)
  -> data/interim/school_leavers_by.csv, counties_geo.csv, reports/catchment.md, docs/evidence_catchment.md.
  Regionaldatenbank blocked by robots.txt; GENESIS Bayern API unusable (form-field login = guest, error 15;
  header login times out). 2018/19 stays a gap year.
- transform/modules.py (Step 40): one module table from all handbooks (TOC-anchored parser)
  -> data/interim/modules.csv, reports/modules_check.md (counts vs TOC, spot-check table)
- transform/thm_modules.py: TH Mannheim focus-area module tables from the cached programme page
  -> data/raw/competitor modules/thm_ma_technische_informatik_modules.csv (handbook PDF blocked by robots.txt)

## Findings so far
- Informatik is the only growing EMI field (Bavaria first-years +6.1 %/yr 2019-24; Germany flat since 2023).
  Electrical and media fields shrink. Generic AI is crowded and OTH already offers it.
- Cybersecurity is the clearest gap: 31 BA / 32 MA distinct dedicated programmes in Germany (exact, hand-checked),
  4 / 6 within 150 km, none at OTH. Theme-rule precision 90-100 %. But 126 general programmes have a security
  focus area (18 within 150 km), incl. OTH's own Medieninformatik and Industrie-4.0-Informatik (Informationssicherheit)
  -> incrementality test must cover them.
- Jobs: "Cyber Security" 851 ads in Germany; Bavaria share 31 % (OT Security 35 %) vs 22-25 % baseline;
  191 ads within 100 km of Amberg.
- Trends: "Cyber Security Studium" rose 2018-2022, plateau since 2022, and is the largest specialist term
  (about 2x KI, 2.6x Robotik since 2022; confirmed by a second download without the anchor). Its share of
  "Informatik Studium" (12.6 % in 2026) still rises only because the anchor falls. KI peaked 2023-24 and falls;
  Robotik flat; "IT Sicherheit" replaced by English terms.
- Modules (Step 41): EMI covers at most ~31 % of a typical cyber bachelor's security ECTS (master 39 %;
  e5 headline, upper-end estimate; TF-IDF 47 % / 45 %) but ~71 % of its general foundations. Missing at EMI:
  pentesting/auditing, forensics, security operations/incident response, software security, security
  management, law, human factors. TH Deggendorf (105 km) already teaches OT/industrial security (BA + MA), so an
  OT profile differentiates against FAU/THI/THWS/HDBW but not against Deggendorf.
- Catchment (Step 42): OTH has its own pool (~5,500 Abitur + FOS/BOS leavers/yr, 40 % FOS/BOS), as large as
  TH Deggendorf's and barely overlapping it (91 % of OTH's 100-km catchment is closer to OTH). OT alone is no
  differentiator, but regional reach is: no full-time dedicated cyber bachelor nearer than ~80 km. Overlap mainly
  with Nuremberg/Erlangen; Regensburg is a third of the pool. Pool -19 % since 2013/14; G9 gap 2024/25.
- Shortlist after kill rule 1: (1) Cybersecurity B.Sc. (lead), (2) Cybersecurity M.Sc. with industrial/OT
  security profile, (3) Robotics + AI B.Sc. (comparison case). Watch list: Microelectronics M.Sc.
  Dropped: embedded/CPS master (88 % overlap with IT und Automation), part-time AI master (AIIA exists).

## Next steps (in order)
1. BA regional shortage data (labour market, Claim D) - school-leaver catchment done in Step 42.
2. 4-6 international benchmark programmes.
3. Forecasting with backtests; MCDA + Monte Carlo (incl. update of kill rule 1 / incrementality with the
   shared intro-security and cryptography modules from docs/evidence_fit_modules.md).
4. Dashboard, report, presentation.
Known gap: E&IT module handbook SPO 222B not found (file in data/raw/oth modules is a duplicate of 226B).
