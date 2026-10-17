# Question, scope and method

<!-- Evidence: docs/research_protocol.md, docs/kill_rules.md, docs/decision_log.md, configs/sources.yaml. -->

## Question and scope

The project brief asks which new study programme would attract the most students to OTH Amberg-Weiden and why it
suits the faculty. We narrowed this to one research question (protocol of 14 Oct 2026,
[research_protocol.md](../../docs/research_protocol.md)): *which new or substantially differentiated bachelor or
master programme should EMI consider, given new student demand, differentiation from existing programmes, graduate
outlet and feasibility?*

- **Faculty:** Elektrotechnik, Medien und Informatik (EMI).
- **Levels:** bachelor and master, analysed separately and then compared.
- **Geography:** all of Germany for demand and competition; the region around Amberg and Weiden for capture.
- **Data:** public sources only. We had no OTH application, admission or enrolment figures, and no university
  published programme-level intakes. Every estimate that depends on intakes is therefore a range with a stated
  assumption.

## Argument structure

A candidate is recommended only if four claims hold and it passes a feasibility gate:

- **A. Demand:** enough prospective students want this field, after demographic change is taken into account.
- **B. Capture:** OTH can win a realistic share, given its location and competitors.
- **C. Fit:** EMI can teach it with existing staff, labs and modules, or with a costed gap.
- **D. Outlet:** graduates find relevant jobs, in Germany and in the region.

Two further tests sit across the claims. **Incrementality:** students who would otherwise enrol in another OTH
programme are not new to OTH, so total and net new students are reported separately. **Kill rules:** five rules,
fixed before any candidate was scored, drop a candidate outright (overlap with an existing OTH programme, feasibility
rating of 1, falling demand, falling master pipeline, and a limit of three candidates per level;
[kill_rules.md](../../docs/kill_rules.md)). The shortlist that survives is ranked by a weighted multi-criteria
analysis with Monte Carlo uncertainty (Section 8).

## Data

| Source | What we used | Claim |
|---|---|---|
| Destatis GENESIS 21311 and 21321 [@destatis2026students; @destatis2026exams] | first-year students and graduates by subject, Germany and Bavaria, 2005-2025 | A |
| BA Studiensuche, data of the HRK Hochschulkompass [@ba2026studiensuche] | all bachelor and master programme offers in the relevant study fields | A, B |
| KMK projections [@kmk2025forecast; @kmk2025schools] | first-year and school-leaver projections to 2035 / 2040 | A, B |
| Bavarian State Office for Statistics [@lfstat2024schools; @lfstat2025students; @lfstat2024employment] | school leavers by county, student flows by home region, IT employment | B, D |
| Module handbooks [@handbooks2026; @othhandbooks2026] | competitor and EMI module texts, ECTS and module responsibility | C |
| International curricula [@benchmarks2026] | structure of four cybersecurity bachelors abroad | C |
| BA job board API and shortage analysis [@ba2026jobsuche; @ba2025engpass] | job-ad counts by keyword and region; shortage occupations | D |
| Google Trends [@google2026trends] | search interest in degree terms | A |

Every source is registered with its URL, use and access route (Appendix A1); downloads are recorded with date and
SHA-256 checksum in manifests in the repository.

## Methods

- **Field screening.** Programmes were tagged by transparent keyword rules on their titles. All
  {{cyber_matches}} cybersecurity title matches and samples of the other themes were checked by hand; the
  cybersecurity rule has a precision of {{cyber_precision}} ([theme_precision.md](../../docs/theme_precision.md)).
- **Demand forecast.** Naive, drift and exponential-smoothing models were compared in rolling-origin backtests over
  horizons of one to five years, scored with the mean absolute scaled error, MASE [@hyndman2006]. A KMK-based
  scenario gives the conservative path (Section 3).
- **Catchment and capture.** School leavers with a university entrance qualification were mapped by county and
  assigned to the nearest site; a doubly-constrained gravity model [@wilson1971] was calibrated on observed Bavarian
  student flows and used in a Huff choice model [@huff1964], anchored on public intake figures of comparable
  programmes (Section 4).
- **Module comparison.** Each competitor module was compared with every EMI module using multilingual sentence
  embeddings [@wang2024e5] and, as an independent check, character n-gram TF-IDF; security modules were grouped by
  the Cyber Security Body of Knowledge [@cybok2021] (Section 5).
- **Cannibalisation.** The capture model was run with and without the new programme to split its students into those
  taken from OTH, those won from other universities, and those kept in the region (Section 7).
- **Ranking.** Weighted scores on six criteria, with weights drawn from a Dirichlet distribution and uncertain scores
  drawn from their ranges, in the spirit of stochastic multicriteria acceptability analysis [@lahdelma1998]
  (Section 8).

## Human checks

Three steps were checked by a team member, not left to code: (1) all {{labels_reviewed}} theme labels of the hand
check; (2) a sample of twenty competitor/EMI module pairs, where the embedding model was right in {{pairs_e5}} and
TF-IDF in {{pairs_tfidf}} cases, so the embedding result is the headline and TF-IDF the sensitivity range; (3) the
complete score sheet of the ranking, where the team changed three scores of the robotics option (Appendix A3). Key
numbers were spot-checked against their source tables at each step.

## Data access rules

Automated downloads respected each site's robots.txt, identified the project with a contact address and waited at
least three seconds between requests. Where a site blocked access or required a login, we did not work around it and
recorded the gap: the federal-state regional database (robots.txt), the Bavarian GENESIS web service (login failed),
OTH staff profile pages (blocked for AI crawlers, skipped on principle) and some competitor documents. These gaps are
listed in Section 9.

## Use of AI tools

The analysis code and the drafting of this report were done with Claude Code, an AI coding assistant, under the
direction of the team. The choice of data sources, every method decision, the human checks listed above (theme labels,
module pairs, score sheet) and all final judgements were made by the team; method decisions are logged with date and
reason in the decision log (Appendix A2). Every number in this report is inserted from a generated key-numbers file
(`reports/key_numbers.yaml`) that names the evidence document it comes from, and each number is checked
automatically against that document, so every figure can be traced to its source.

## Conflict of interest

One team member is enrolled in the master programme Artificial Intelligence for Industrial Applications at OTH. This
was declared in the research protocol; scores related to AI programmes were checked by the other team member.
