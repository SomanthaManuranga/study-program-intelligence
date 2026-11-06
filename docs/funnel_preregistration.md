# Funnel pre-registration: the programme comes out of the analysis

Rules: `configs/funnel.yaml`, committed before any programme type is computed. Method background: research report
"Data driven study programme discovery". Earlier results stay as a baseline and are not inputs.

## What we already knew before this run

The analysis cannot be blind, so the prior knowledge is stated:

- Earlier rounds screened 18 topic groups we wrote ourselves and six hand-picked candidates.
- Earlier results: Cybersecurity B.Sc. first with investment; Robotics + AI path B closest under existing resources;
  AR/VR, autonomous systems, geo-data, energy data and a reduced OT master failed the gate.
- The earlier feeder trend for robotics was German -3.3 %/yr in Bavaria, close to the -3 % line used here. The line
  is the old G5 number, unchanged; removing "and Germany" is a response to the review finding, and the stress tests
  run it at -3, -5 and off.
- Before writing the rules we read catalogue metadata only: degree and form counts, and that about half the offers
  have no content text. No clustering or scoring of the catalogue was run.

Cyber and robotics are old hypotheses. They get no special treatment and count only if they come out of the funnel.
The 18 lists are used once, after discovery, to report how many the data recovers.

## How each known failure is corrected

| Failure | Correction | Step |
|---|---|---|
| Topics written by us; six candidates picked by hand | Types come from clustering all full-time bachelor and master offers; list frozen and hashed | 2, 3 |
| Rare programmes could be missed | Separate rare path for groups of 2-9 offers | 2 |
| Filters written after the screening | All thresholds committed before the run | 0 |
| Loose demand filter ("and Germany") | German first-years in Bavaria decide; stress-tested | 3 |
| Intake level from a capacity and one student review | Level from Destatis first-years per offer, checked against published intakes | 6 |
| Foreign growth carried forward as a point | Unprojected numbers lead; foreign is a corridor | 4, 6 |
| 137-ECTS base against 165 taught ECTS | Reference curriculum scaled before the caps apply | 7 |
| The cap decides the answer | Results shown for each cap; the faculty's answer selects the row | 7 |
| One rater | Second rater on a sample, Cohen's kappa reported | 7 |
| Hand-set keywords for job ads | Keyword taken from each type by script | 5 |
| Robustness only over the three baseline options | Stress grid covers every candidate and the screening rules | 8 |

## Steps

Each step's output is the next step's input.

| Step | Question | Output |
|---|---|---|
| 0 | Which rules decide? | this file, `configs/funnel.yaml` |
| 1 | Is the data current? | job-ad snapshot, data inventory |
| 2 | What kinds of programme exist? | programme types from all offers |
| 3 | Which types are open to OTH and within EMI's field? | frozen candidate list with hash |
| 4 | Are students coming? | pool, trend and backtest per candidate |
| 5 | Are there jobs nearby? | job-ad counts per candidate |
| 6 | How many students would be new to OTH? | low / central / high net-new first-years |
| 7 | Can EMI teach it with what it has? | F1-F4 per shortlisted candidate; hand check by Soma |
| 8 | Which one, and how sure are we? | ranking, stress tests, decision |

## Reasoning format

Every step writes to `docs/funnel_reasoning.md`:

1. **Question** the step answers.
2. **Evidence**, with numbers and sources.
3. **Rule** applied, as pre-registered.
4. **Result**, including what was dropped and why.
5. **What this means for OTH.**
6. **Strongest objection and answer.**

Every candidate keeps a dossier from step to step, so the final answer can be traced back one reason at a time.

## Judgement calls and known deviations

- **Judgement numbers:** the anchor band (0.5-1.5), the minimum cohort (20), the value-function anchors and the
  decision bars (0.5) have no literature anchor. They are stress-tested.
- **Decision bar:** the earlier 80 % bar was set after a first ranking and compared three options. With more
  candidates the probability of rank 1 falls by construction, so the bar here is "more likely than all others
  combined".
- **Deviations from the research design, for practical reasons:**
  - no ESCO skill linking: the job-ad source gives counts, so demand for skills is measured by counts per type;
  - no cross-nested logit or travel times yet: the Huff model is reused, and its limits are stated;
  - the encoder is not chosen by benchmark: the cached project encoder is used, with TF-IDF as the cross-check.
- **Agents:** fresh-context agents review rules and claims. An agent is not a human rater and never replaces the
  hand check or the second team member's check.

## Amendments after the independent attack (before any result)

A fresh-context reviewer attacked version 1 and found five blockers and seven major problems. No programme type had
been computed. Version 2 of `configs/funnel.yaml` makes these changes:

| Problem found | Change |
|---|---|
| Net-new would equal gross for every survivor | OTH offers assigned to a type become OTH sites at weight w, or the nearest OTH offer if none |
| Shortlist score needed gate results not yet computed | Pre-gate score without feasibility; automatic gate down the list; replacements from the list |
| Most catalogue labels have no exact Destatis name | Full label-to-code table committed before clustering |
| Intake anchor undefined for masters, ambiguous for bachelors | German numerator, all-form denominator, fractional offers, separate master rule, numeric validation bar |
| EMI-domain bar degenerate | Raw cosine, calibrated on EMI against other OTH offers; flag instead of drop if AUC < 0.8 |
| Trend screen kills whole subject fields | Only a validated trend (own MASE < 1) can drop a type; a stress list carries dropped types forward |
| "At OTH" depended on cluster size | Only a close OTH offer drops a type; otherwise it counts as an OTH site |
| Selection rewarded many small clusters | Selected on share of offers in stable clusters, with a limit on the largest cluster |
| Text mixed content with administrative notes | Notes and degree markers removed |
| Part-time offers invisible as competitors | Assigned afterwards and counted as supply |
| Fit and feasibility measured one number twice | Feasibility is now the tightest gate margin; minimum cohort is a gate |
| Decision undefined with one passer or a cap conflict | Rules for two or more, one and no passers; cap 10 until the faculty answers |

Limitation stated: a programme not yet offered anywhere in Germany cannot be found by clustering offers.

Pool mapping: 330 of 398 catalogue labels were matched by nearest name and reviewed by a fresh-context agent (178
corrected, each with a reason in `configs/funnel_subject_map_corrections.yaml`), blind to any type. Teacher-training
labels have no real Destatis series (those students count under their teaching subjects), so a type mainly made of
them has a nominal pool and is flagged low confidence. Wirtschaftsingenieurwesen goes to its engineering-focus code.
