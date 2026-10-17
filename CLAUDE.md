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
- Plain English, blunt, evidence-based. Numbers with sources. Say clearly when evidence is weak.
- Windows + PowerShell. Python venv in .venv (activate: .venv\Scripts\Activate.ps1). Run modules from repo root:
  python -m study_program_intelligence.<package>.<module>
- Do the file edits, test runs and git commits yourself; I only do manual downloads that robots.txt or
  logins block.

## Current step
Step 38: hand-labelled precision check of the theme rules (Next steps item 1). Status: open.
Last finished: Step 37, second Google Trends download without the anchor (2026-10-17).

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

## Findings so far
- Informatik is the only growing EMI field (Bavaria first-years +6.1 %/yr 2019-24; Germany flat since 2023).
  Electrical and media fields shrink. Generic AI is crowded and OTH already offers it.
- Cybersecurity is the clearest gap: 34 BA / 36 MA programmes in Germany, 4 / 7 within 150 km, none at OTH.
- Jobs: "Cyber Security" 851 ads in Germany; Bavaria share 31 % (OT Security 35 %) vs 22-25 % baseline;
  191 ads within 100 km of Amberg.
- Trends: "Cyber Security Studium" rose 2018-2022, plateau since 2022, and is the largest specialist term
  (about 2x KI, 2.6x Robotik since 2022; confirmed by a second download without the anchor). Its share of
  "Informatik Studium" (12.6 % in 2026) still rises only because the anchor falls. KI peaked 2023-24 and falls;
  Robotik flat; "IT Sicherheit" replaced by English terms.
- Shortlist after kill rule 1: (1) Cybersecurity B.Sc. (lead), (2) Cybersecurity M.Sc. with industrial/OT
  security profile, (3) Robotics + AI B.Sc. (comparison case). Watch list: Microelectronics M.Sc.
  Dropped: embedded/CPS master (88 % overlap with IT und Automation), part-time AI master (AIIA exists).

## Next steps (in order)
1. Hand-labelled precision check of the theme rules (50 programmes).
2. Competitor module handbooks for the shortlist -> NLP/embedding gap analysis vs EMI modules.
3. Regionaldatenbank: school leavers by county (catchment); BA regional shortage data.
4. 4-6 international benchmark programmes.
5. Forecasting with backtests; MCDA + Monte Carlo.
6. Dashboard, report, presentation.
Known gap: E&IT module handbook SPO 222B not found (file in data/raw/oth modules is a duplicate of 226B).
