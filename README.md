# Study Program Intelligence

**Which new study programme would attract the most students to OTH Amberg-Weiden, and why does it suit the faculty?**

A reproducible data-analytics project that answers this for the Faculty of Electrical Engineering, Media and
Computer Science (EMI) at OTH Amberg-Weiden. It combines public data from federal and state statistics offices,
the Federal Employment Agency, programme catalogues, competitor module handbooks and search trends, and ranks
the shortlisted options with a multi-criteria decision analysis under uncertainty.

---

## Result (data-driven funnel; preliminary, under re-check before the 4 Dec 2026 data freeze)

**Preliminary finding: a general computer science / Informatik bachelor at the EMI faculty fits the supervisor's
40-80 % overlap band with existing staff and labs.** An independent re-check of Steps 0-8 found that the
arithmetic is correct but that four further statements are not established: that it is the *only* programme EMI can
run, that it attracts the *most* students, how many first-years would be new to OTH, and that the result was reached
without bias. A rerun with corrected rules (version 4) is planned; until then this is a working result.

| | What holds | What is open |
|---|---|---|
| How it was found | All ~20,000 German bachelor and master offers grouped into 824 programme types by content; screened for "not at OTH" and "in EMI's field"; demand, job ads and first-years measured for every remaining candidate | Only 6 candidates were checked module by module, 2 of them plausible EMI bachelors (computer science, cybersecurity); plain Informatik, electrical engineering, data science and software engineering were skipped by a 3-per-level stopping rule; automation and robotics (gate order 38) and Angewandte Informatik (40) were never reached |
| Share EMI already teaches | 49-68 % of a real computer science bachelor (OTH Regensburg's International Computer Science; 68 % as marked, 49 % after a reviewer's corrections), 66.7 % of a second one (TH Ingolstadt Informatik); the band is 40-80 % | The figure moved between marking passes (44, 46, 68 %); about 7 points come from language courses counted through EMI's foreign-language slot |
| New teaching needed | about 52.5-55 ECTS, about 1.2 professor-equivalents a year; no new lab | Whether staff have the hours is unknown; 11.5 of the 50.5 ECTS of new modules are language courses (10 of them Spanish) |
| Computer science vs. cybersecurity | | The split comes partly from inconsistent marking: the same topic (penetration testing) was judged teachable by current lecturers in one handbook and new in the other, following which EMI modules the sheet showed. Under one consistent standard both pass or neither does |
| First-years new to OTH | about 18-20 a year measured as general Informatik (types 13 and 242); the small "Computer Science" group of the model gives 26 (range 7-88), a grouping artefact | The share taken from OTH's own programmes is modelled, not measured; measured as general Informatik, above 28-35 % taken from OTH the estimate falls below the bar of 15 |
| Ranking | | A two-candidate comparison for information only; measured as the stable Informatik type 13, cybersecurity comes first; as type 242 Informatik stays first |
| Robustness | holds under the agreed rules | Breaks with a cap on new modules by current lecturers, with at most 50 % from one existing programme, without counting two EMI modules together, or under the project's former strict rule. The "holds in 22 % of the stress grid" figure means 2 of 9 combinations of two factors, not a probability |

**Not passed:** the Step 2 reader check (22 of 30, bar 24), the Step 3 coherence check (70 %, bar 80 %), the Step 3
similarity check (competition counts not validated), the Step 1b matching threshold (no reliable cut-off); 7 stress
values were not run.

**Rules and bias:** several decisive rules were set or changed after earlier results were known (the 40-80 % band
without a cap on new modules, and "two EMI modules may cover one", set together with "content counts, not credits" 15 minutes after the notes recorded that if module size
counted, no bachelor would pass). Every module judgement comes from one AI model; no person has checked them yet. The supervisor
has not confirmed the band reading, the uncapped new modules or the two-module rule. The re-check: `docs/funnel_recheck.md`. Details:
`docs/funnel_run2_notes.md`; tables in `results/`.

**Earlier baseline (with new resources):** before the existing-resources condition, the analysis recommended a
Cyber Security B.Sc. (needs ~2 new professorships and a lab). It is kept for comparison (tag
`baseline-new-resources`, `docs/evidence_tie_break.md`); the report and dashboard are rewritten to the funnel result
before the freeze.

---

## How the argument is built

| Claim | Question | Main methods |
|---|---|---|
| A. Demand | Do enough students want this? | Destatis first-year series, KMK projection, forecasting with rolling-origin backtests (MASE), Google Trends |
| B. Capture | How many would come to OTH? | Programme catalogue (4,875 unique offers, 4,806 of them bachelor or master), catchment from county school-leaver data, gravity/Huff model, cannibalisation model |
| C. Fit | Can EMI teach it? | NLP comparison of competitor and EMI module handbooks (multilingual embeddings + TF-IDF cross-check, CyBOK areas), staff and lab mapping |
| D. Outlet | Are there jobs? | BA job-ad snapshots, Bavarian employment statistics, BA shortage analysis |

All options then go through the kill rules (`docs/kill_rules.md`) and a ranking with MCDA + Monte Carlo
(Dirichlet-sampled weights, sampled score ranges, leave-one-criterion-out). Rules, weights and scoring scales
were fixed before any ranking was run; every method decision is in `docs/decision_log.md`.

**The data-driven funnel** (the current working answer; rules written before each step in `configs/funnel.yaml`,
`docs/funnel_preregistration.md`, later changes recorded in `docs/decision_log.md`; one step at a time, each
reviewed):

| Step | Question | Code (`analysis/`) |
|---|---|---|
| 0-1 | Rules; is the data there? | `funnel_inventory.py`, `funnel_modules.py` |
| 2 | What kinds of programme exist? (824 types from all offers, multilingual embeddings + clustering) | `funnel_types.py` |
| 3 | Not at OTH, in EMI's field; competition by content similarity | `funnel_units.py` |
| 4 | Are students coming? (subject pools, backtested trends) | `funnel_demand.py` |
| 5 | Are there jobs nearby? (BA job board) | `funnel_labour.py` |
| 6 | How many first-years, how many new to OTH? (Huff model) | `funnel_capture.py` |
| 7 | Can EMI teach it? (real handbooks, module by module, AI readers) | `funnel_shortlist.py`, `funnel_refs.py`, `funnel_feasibility.py` |
| 8 | Which one, and how sure? (MCDA, Monte Carlo, PROMETHEE, stress grid) | `funnel_rank.py`, `funnel_listspecs.py` |

---

## Repository structure

```
configs/            weights, scores, source register, download lists, portfolio and overlap configs
docs/               evidence documents (one per claim/step), decision log, kill rules, manifests
docs/report/        report source (one Markdown file per section; numbers are placeholders)
src/study_program_intelligence/
  ingest/           data collection (Destatis GENESIS, BA Studiensuche, BA Jobsuche, documents)
  transform/        parsing and cleaning (programmes, module handbooks, school-leaver tables)
  analysis/         themes, trends, module gaps, catchment, labour, forecast, capture,
                    cannibalisation, options, ranking
  report/           key numbers, figures, outline, report builder, spot checks
app/                Streamlit dashboard
data/               raw / interim / processed data (git-ignored, regenerated by the code)
results/            final tables of the funnel, one folder per step (committed; MANIFEST.csv lists every file)
reports/            generated tables, figures and the final report (git-ignored)
tests/              tests
```

Key documents to start with:
- `docs/funnel_run2_notes.md`: the data-driven funnel, step by step, with every number
- `notebooks/funnel_progress.ipynb`: the same in plain language, for the progress meetings
- `docs/evidence_funnel.md`: how the baseline shortlist was narrowed down
- `docs/evidence_ranking.md`: the final ranking and its robustness
- `docs/decision_log.md`: every method decision with date and reason
- `docs/kill_rules.md`: the exclusion and scoring rules

---

## Setup (Windows / PowerShell)

Requires Python 3.11+ (developed with 3.13).

```powershell
git clone https://github.com/SomanthaManuranga/study-program-intelligence.git
cd study-program-intelligence
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev,nlp,report,dashboard]"
```

Create a `.env` file in the repo root (never commit it; it is git-ignored):

```
GENESIS_TOKEN=<your Destatis GENESIS-Online API token>
CONTACT_EMAIL=<your email, sent in the User-Agent of every request>
```

A free GENESIS-Online account gives the API token. The PDF build of the report also needs a LaTeX engine
(xelatex, e.g. MiKTeX); Markdown and .docx work without it.

---

## Running the analysis

Run from the repo root with the virtual environment active. **One command rebuilds everything** from the data in
`data/raw/` (transform, analysis, key numbers, figures, report) and runs the tests:

```powershell
python -m study_program_intelligence.pipeline
```

Before it starts it checks that the manual inputs are in place (see *Manual downloads* below). It stops at the first
failing step, writes the full console output to `reports/pipeline_output.log`, and writes `reports/pipeline_log.md`
with the time of every step and a comparison of the new key numbers with the previous run, so any change in a result
is visible.

| Option | Use |
|---|---|
| `--ingest` | download the sources first (needs `.env`; files already downloaded are kept) |
| `--snapshot` | also take a dated job-ad snapshot (only on the snapshot dates; it adds data) |
| `--list` | show every step with its exact command |
| `--from <step>` | resume at a step, e.g. `--from analysis.forecast` |
| `--skip <step> ...` | leave steps out |
| `--no-tests` | do not run the tests at the end |

Every step is an ordinary module call (`python -m study_program_intelligence.<package>.<module>`) and can also be run
on its own; `--list` prints them in order. The `ingest` modules have a command-line help (`--help`).

**Tests** (also run at the end of the pipeline):
```powershell
python -m pytest
```
They check the PDF number parsing, the model building blocks (distances, gravity model, forecasts, score mappings,
Monte Carlo reproducibility), the configs (weights, score ranges, source register, citations), that every key number
is found in its evidence document and the report contains no hand-typed numbers, and the dashboard.

**Dashboard** (local only)
```powershell
streamlit run app/dashboard.py
python app/screenshots.py      # screenshots of every page (dashboard must be running)
```

Every number in the report and dashboard comes from `reports/key_numbers.yaml`, which links each value to its
evidence document. The report build stops on unknown placeholders or hand-typed numbers.

**The funnel** runs step by step, each from committed code (it refuses to run on uncommitted changes):
```powershell
python -m study_program_intelligence.analysis.funnel_types scan; python -m study_program_intelligence.analysis.funnel_types embed; python -m study_program_intelligence.analysis.funnel_types run
python -m study_program_intelligence.analysis.funnel_units run
python -m study_program_intelligence.analysis.funnel_demand
python -m study_program_intelligence.analysis.funnel_labour measure
python -m study_program_intelligence.analysis.funnel_capture
python -m study_program_intelligence.analysis.funnel_shortlist
python -m study_program_intelligence.analysis.funnel_feasibility verdict
python -m study_program_intelligence.analysis.funnel_rank
python -m study_program_intelligence.analysis.funnel_listspecs
python -m study_program_intelligence.analysis.funnel_results      # copies the final tables into results/
```
Steps 5 and 7 also collect data (job-ad counts, reference handbooks, AI marks); how is described in
`docs/funnel_run2_notes.md`. The marks of the AI readers are committed in `docs/funnel_module_marks_*.csv`.

### Manual downloads
A few sources cannot be fetched by script (robots.txt or no API). These files must be placed by hand:
- **Google Trends** CSVs in `data/raw/trends/` (settings are recorded in `docs/evidence_demand_trends.md`)
- **OTH module handbooks** in `data/raw/oth modules/` (OTH `/fileadmin/` is disallowed for scripts)
- anything listed in `docs/manual_downloads.md`

The team's hand-checked theme labels (Step 38) are committed as `docs/theme_labels.csv`.

---

## Data sources and ethics

- **Public data only**, no personal data. Professors are referred to by role, not by name.
- **robots.txt respected** for every site; when a site disallows scripts, the data was skipped or downloaded by
  hand. Requests use a User-Agent with a contact address and a delay of at least 3 s (more if a site's Crawl-delay asks for it).
- **Every source is registered** in `configs/sources.yaml` with licence notes, and every download is recorded in
  a manifest in `docs/` (URL, date, SHA-256).
- **Raw data is not redistributed.** `data/` is git-ignored; the code regenerates it from the original sources.
  `results/` holds only derived tables (no raw download, no module text of another university, no internal file).

Main sources: Destatis GENESIS-Online (tables 21311, 21321), Bayerisches Landesamt für Statistik (school leavers,
employment, students by origin), KMK projections, Bundesagentur für Arbeit (Studiensuche/Hochschulkompass data,
Jobsuche, Engpassanalyse), university module handbooks, Google Trends.

