# Independent cross-check: method (Step 0, written before any analysis code runs)

Author: Poovallal (branch `poovallal/dev`). Purpose: answer the project question a second time, independently of the
funnel on `soma/funnel`, with the SAME rules and weights but OWN grouping, measures and code. Agreement or
disagreement with the funnel's answer is a result in itself.

## Independence rules
- Inputs: only `data/raw/` and the cleaned catalogue in `data/processed/`, plus EMI's parsed module handbooks
  (`data/interim/modules_emi_2026.csv`, an input-cleaning file, no decisions). The funnel's working tables, results and
  AI marks in `data/interim/` are NOT read.
- The funnel's result is opened only after Step 7 of this cross-check is finished.

## Shared rules (from the supervisor and the team; `configs/overlap_rule.yaml`)
- A new degree, not already at OTH; more than 80 % overlap with one existing OTH programme -> dropped.
- 40-80 % of the content covered by lectures EMI already runs; below 40 % kept but flagged as costly.
- EMI field only; bachelor and master; full-time; German and international students.
- Success = students new to OTH; minimum class of 20 first-years (assumption).
- Existing staff and labs only.
- Weights: demand .30, labour .20, fit .20, feasibility .15, differentiation .10, regional .05.

## Steps and measures

| Step | Question | Method (this cross-check) |
|---|---|---|
| 1 | Which kinds of programme exist, fit EMI and are not at OTH? | A kind = official subject (catalogue subject classification, the same subjects Destatis counts) x level. Universe: full-time bachelor and master offers in Germany. Teacher training excluded. **EMI fit**: the subject is one of EMI's own subjects, or at least 25 % of its offers in Germany also list one of EMI's subjects (co-occurrence). **At OTH**: no drop by subject or title; whether a kind is already at OTH is decided only by the module test in Step 2 (amended before any code ran: a subject rule would remove plain Informatik because Industrie-4.0-Informatik carries the subject Informatik). Control: subjects OTH already offers (e.g. Medieninformatik) must come out above 80 % in Step 2. |
| 2 | Is it just a relabelled OTH programme? | Topic profile of each kind = the focus items ("Schwerpunkte") its offers list in the catalogue, weighted by how many offers list them. Each topic is matched to EMI's modules (TF-IDF on words and character 3-5-grams; module title weighted 3x plus module text). Overlap with one OTH programme = weighted share of topics covered by that programme's modules alone. **More than 80 % -> dropped.** |
| 3 | Can EMI teach it (40-80 %)? | Coverage = weighted share of topics covered by any EMI module (similarity >= tau). Topics with tau_low <= similarity < tau count as "near" (an existing lecturer teaches a related topic). tau and tau_low are calibrated BEFORE scoring on controls: kinds OTH already offers (should be high) vs clearly non-EMI kinds (law, medicine, theology, languages; should be low); tau maximises the gap in mean coverage. Kinds with fewer than 5 topics: coverage "insufficient data", kept and flagged. **Hand check**: every topic match of the shortlist goes to a sheet for Poovallal to confirm or reject. |
| 4 | Will students come? | Bachelor: Destatis first-years in the subject, Bavaria, German and foreign, winter semesters 2019-2024 (2025 left out: Bavarian G9 gap year). Master: graduates in the subject, Bavaria (pipeline), 2019-2025. Size = average per existing Bavarian full-time programme of that subject and level. Trend = yearly growth 2019-2024 (German and total reported separately). **New to OTH** = size x (1 - 0.5 x max overlap with one OTH programme) [assumption; 0.25 and 0.75 as sensitivities]. Below 20 -> not recommendable. |
| 5 | Is there a regional gap? | Same-subject, same-level full-time offers within 100 km and 150 km of OTH (Amberg or Weiden, whichever is nearer), in Bavaria and in Germany. **South gap** = offers per 1,000 first-years of the subject in Bavaria + Baden-Wuerttemberg, compared with the rest of Germany (Destatis first-years by Land). |
| 6 | Are there jobs nearby? | Federal Employment Agency job board: ads for the subject's core term, within 100 km of Amberg (Oberpfalz), in Bavaria, in Germany, on one day. Place of each reply is checked (Amberg, Oberpfalz, not Amberg near Buchloe). A snapshot, not a trend; the multi-year trend comes from official employment statistics where available. |
| 7 | Which one, and how sure? | Each criterion -> score 1-5 by quintile among the candidates that pass Steps 1-3 (relative scores, stated). Demand = new-to-OTH size (2/3) + trend (1/3); labour = jobs within 100 km; fit = coverage; feasibility = covered + near share; differentiation = fewer competitors within 150 km; regional = south gap. Weighted sum with the shared weights; Monte Carlo with 10,000 Dirichlet weight draws (concentration 50) -> how often each candidate ranks first. The top 15 go to the hand check; the result is "provisional" until it is done. |

## Known limits (stated before running)
- Topics from catalogue focus lists are a stand-in for full module handbooks; about half of the offers list no focus
  items. Coverage is a share of topics, not of credits.
- Subjects are coarse: a rare programme (e.g. Motorsport Engineering) sits inside a broad subject; rare titles are a
  separate list, not ranked.
- First-years by subject do not split bachelor and master; master demand uses graduates as the pipeline.
- The 0.5 factor for students taken from OTH programmes is an assumption.
- Module data exist only for EMI's programmes; overlap with programmes of other OTH faculties (e.g. Maschinenbau, Motorsport Engineering) is not tested at module level.
- Bachelor and master are ranked separately: master demand uses graduates (pipeline), so its size is not comparable with bachelor first-years.
- Job ads are a one-day count of a word, not a vacancy statistic.
