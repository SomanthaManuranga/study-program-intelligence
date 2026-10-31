# Study Program Intelligence

**Which new study programme would attract the most students to OTH Amberg-Weiden, and why does it suit the faculty?**

A reproducible data-analytics project that answers this for the Faculty of Electrical Engineering, Media and
Computer Science (EMI) at OTH Amberg-Weiden. It combines public data from federal and state statistics offices,
the Federal Employment Agency, programme catalogues, competitor module handbooks and search trends, and ranks
the shortlisted options with a multi-criteria decision analysis under uncertainty.

---

## Result (preliminary, as of 18 Oct 2026; final after the 4 Dec 2026 data freeze)

> **Status note:** the result below is the **baseline with new resources**. The supervisor has since made "existing
> staff and labs only" binding, and the cybersecurity bachelor needs new staff and a lab. Current answer
> (`docs/evidence_tie_break.md`): under the strict existing-resources rule no candidate passes; under the lenient
> sensitivity, Robotics + AI B.Sc. (path B, assistive / service robotics) is a conditional candidate; with investment,
> the cybersecurity bachelor below remains the answer. This section is rewritten after the 4 Dec 2026 freeze.

**Recommendation: a Cyber Security B.Sc. at the EMI faculty.**

| | Result |
|---|---|
| Ranking (10,000 Monte Carlo draws) | Cyber Security B.Sc. ranked first in **~92 %** of draws; first in every leave-one-criterion-out run (base case; five of six with German-only demand trends). With demand measured on German entrants only: first in ~78 %, just below the 80 % robustness bar |
| Expected first-years per year | **21 / 39 / 75** (low / central / high), year 1: 12 / 24 / 45 |
| New to OTH (not taken from existing programmes) | **~82 %** in the central case (73-86 % across model variants; a model estimate that does not see OTH programmes without a security focus) |
| Regional pool | ~5,500 qualified school leavers a year; no full-time dedicated cyber bachelor within ~80 km |
| Demand trend | Bavarian first-years in the cyber-related subjects: 4,936 (2024); central planning value (midpoint of KMK scenario and trend) ~5,540 (2030), ~6,220 (2035). Most of the growth is foreign students: German first-years +1.9 % a year (2019-2024), foreign +12.8 % |
| Labour market | IT occupations in Bavaria +24 % (2019-2023), +34 % with a degree; Informatik a shortage occupation at bachelor level in Germany (2025) |
| Faculty fit | EMI covers ~71 % of the foundations but at most ~31 % of the security content |
| Resources needed | ~2 new professorships, 1 lab engineer, 1 security lab |

Options compared: Cyber Security B.Sc. (winner), Cyber/OT Security M.Sc. (second; proposed as a later
follow-on), Robotics + AI B.Sc. (third; better as a specialisation of the existing KI B.Sc.).

**Main limitations:** no published intake figures for comparable programmes (wide first-year range; the low case
only just reaches the assumed minimum cohort of 20, and only about 15 of its 21 first-years would be new to OTH), Destatis has no separate cyber-security subject (a proxy is used),
and job-ad counts are keyword matches, not vacancy statistics. All of these are stated in the report.

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
reports/            generated tables, figures and the final report (git-ignored)
tests/              tests
```

Key documents to start with:
- `docs/evidence_funnel.md`: how the shortlist was narrowed down
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

Main sources: Destatis GENESIS-Online (tables 21311, 21321), Bayerisches Landesamt für Statistik (school leavers,
employment, students by origin), KMK projections, Bundesagentur für Arbeit (Studiensuche/Hochschulkompass data,
Jobsuche, Engpassanalyse), university module handbooks, Google Trends.

