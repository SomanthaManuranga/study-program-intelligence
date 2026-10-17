# Evidence: selection funnel (from all EMI-related fields to one recommendation)

Status: v1, 18 Oct 2026 (Step 51). Synthesis of earlier evidence docs; no new data. Purpose: show the order in which
candidates were filtered, with the count and the reason at each stage, so that it is clear the winner was not chosen
first.

## The rules were fixed before any candidate was scored

Git history of this repository (commit time, Europe/Berlin):

| When | Commit | What was fixed |
|---|---|---|
| 14 Oct 2026, 16:35 | cab5148 | MCDA criteria and weights (configs/analysis.yaml); unchanged since |
| 14 Oct 2026, 16:37 | dff024f | Kill rules 1-5 (docs/kill_rules.md) |
| 14 Oct 2026, 22:42 | 27bf2e0 | First demand/supply screening of all fields (docs/evidence_competition_demand.md) |
| 15 Oct 2026, 21:03 | c546da9 | Kill rule 1 overlap test, shortlist of 3 (docs/overlap_test.md) |
| 17-18 Oct 2026 | bcfb0d1 ... 6c6138f | Capture, cannibalisation, ranking (Steps 47-49) |

Later additions to the rules are logged as such: scoring anchors for criteria other than demand and the rule "weak
evidence widens a score's range, it does not raise its centre" were written in Step 49, after the evidence was
collected but before the ranking was computed (docs/kill_rules.md, docs/decision_log.md).

## Funnel

| Stage | Date | Filter | In | Dropped (reason) | Out |
|---|---|---|---|---|---|
| 0 Screening universe | 14 Oct | 4,840 programme offers from 13 study fields; 11 EMI-related Destatis subjects; title rules for 9 theme groups | 9 theme groups | - | 9 theme groups |
| 1 Demand trend | 14 Oct | feeder subjects of the theme grow (Destatis 21311, 2019-2025) | 9 | media technology / games (Medientechnik -8.6 %/yr, Medieninformatik -3.5 %/yr in Germany) | 8 |
| 2 Supply gap | 14 Oct | thin supply near OTH and not already offered by OTH | 8 | generic AI / data (32 BA / 34 MA within 150 km, OTH offers both levels); automation / Industrie 4.0, energy / e-mobility, medtech / health (already offered at OTH: 1, 1 and 2 titled offers; not carried forward, no separate written verdict); microelectronics to the watch list (116 first-years in Germany 2025, 9 master programmes) | 3 themes = 5 candidates |
| 3 Kill rule 1 (overlap > 50 %) | 15 Oct | core topics already in one OTH programme at the same level | 5 | embedded / CPS master (88 %, IT und Automation); part-time AI master (identical to AI for Industrial Applications) | 3 |
| 4 Kill rules 2-4 (feasibility, trend, pipeline) | 17 Oct | feasibility rating 1; five-year fall in entrants; falling graduate pipeline (master) | 3 | none (no feasibility rating of 1; Informatik entrants not falling; Informatik graduates rising) | 3 |
| 5 Ranking (MCDA + Monte Carlo) | 17-18 Oct | weights fixed 14 Oct; 10,000 draws | 3 | Cyber/OT M.Sc. (P(rank 1) 6.0 %), Robotics+AI B.Sc. (2.3 %) | **1: Cybersecurity B.Sc. (91.7 %)** |

The 5 candidates after stage 2: Cybersecurity B.Sc., Cybersecurity M.Sc. (industrial / OT profile), embedded /
cyber-physical systems M.Sc., Robotics + AI B.Sc., and a part-time AI master as a control case for the
incrementality rule (docs/evidence_competition_demand.md, "Provisional shortlist").

Sources per stage: stage 0-2 docs/evidence_competition_demand.md (tables "Demand" and "Competition", verdict table
"Reading the two together") and docs/theme_precision.md; stage 3 docs/overlap_test.md; stage 4 docs/kill_rules.md,
docs/evidence_forecast.md, docs/evidence_ranking.md (pipeline check); stage 5 docs/evidence_ranking.md.

## Weak points

- Stage 2 for automation, energy and medtech: the 14 Oct screening did not carry them forward and the competition
  table shows OTH already offers each theme, but no separate written verdict exists. Energy and medtech also belong
  mainly to other faculties.
- Stage 0-2 use title keyword rules (precision 90-100 % in the hand-labelled check, small samples for non-cyber
  themes) and the catalogue's 13 study fields; themes outside these fields were not screened.
- Microelectronics stayed on the watch list and was not modelled; its demand base is very small.
