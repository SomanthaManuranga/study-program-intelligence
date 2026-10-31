# Evidence: deep-analysis layer (robustness, benchmarks, corridors)

Criteria (fixed before building): `docs/criteria_deep_analysis.md`. Added 31 Oct 2026 on Soma's instruction;
everything here is ADDITIVE evidence around the pre-registered three-level answer (strict rule: no candidate passes;
lenient sensitivity: robotics path B conditional; with investment: the cybersecurity baseline). No pre-registered
criterion, threshold, weight or score changed. Generated tables: `reports/data_quality.md`, `reports/spec_curve.md`,
`reports/intake_model.md`, `reports/capture_benchmark.md`, `reports/cannibalisation_similarity.md`,
`reports/demand_corridor.md`; figures `reports/figures/f09_spec_curve.*`, `f10_intake_model.*`. All modules run in
the one-command pipeline and are covered by `tests/test_deep_analysis.py`.

## 1. Data-quality gate (`analysis/data_quality.py`)

26 structural checks on the consumed tables (schema, key uniqueness, cross-table sums, anchor cross-checks) - all
pass: the county table carries 401 counties (96 Bavarian; the documented own pool of 14 Bavarian counties sits inside
76 German counties for which OTH is the nearest of the four sites); the school-leaver counties sum to Bavaria in
every year; the Bavarian cyber-proxy 2024 reproduces the forecast anchor (4,936); the full catalogue holds 22,093
unique offers, 9 of them without coordinates. The gate runs in the pipeline, so silent data damage now stops a rerun.

## 2. Specification curve (`analysis/spec_curve.py`; the multiverse check)

The Step 47/48 machinery was rerun from the generated tables under every combination of the reasonable alternatives a
critic could propose (anchors, ratio variant, central rule, ramp-up, cannibalisation, minimum cohort, pool-trend
treatment: 2,880 specifications per candidate; for the ranking: trend scores, robotics range, capture draws,
robotics cannibalisation, four seeds, three Dirichlet concentrations: 192 specifications). A reproduction gate
asserts first that the pre-registered specification reproduces the committed numbers exactly (it does: 21 / 39 / 75,
15.3 / 32.0 / 64.4, 14.9 / 28.7 / 55.3).

- **Cyber:** central steady-state gross median 42.4 (IQR 36.3-52.4, extremes 27.1-75.5); the central estimate clears
  the minimum cohort of 20 in **100.0 %** of specifications. The LOW scenario clears 20 in only 55.0 % - the low case
  stays the honest weak point, as the evidence docs already say.
- **Robotics path B:** central median 25.1 (22.2-29.4, extremes 16.4-36.9); central clears 20 in **91.2 %** of
  specifications; the low scenario never does (0 %).
- **Ranking:** cyber ranks first in **100.0 %** of the 192 specifications; P(rank 1) spans 0.659-0.945 (median
  0.804), the pre-registered specification gives 0.917, and the seed spread at the pre-registered settings is
  0.914-0.917 (Monte Carlo noise about +-0.2 percentage points). A one-at-a-time weight sweep (each criterion scaled
  0.5x-1.5x, renormalised) keeps P(rank 1) between 0.858 and 0.958.
- **What drives the spread** (variance decomposition): for cyber the pool-trend treatment (62.2 %) and the central
  rule / high anchor; for robotics the high anchor (48.9 %). So the conclusions depend most on exactly the two
  things the docs flag as assumptions - the trend carried to 2030 and the unanchored high intake - and on nothing
  hidden.

Limits: the grid is our list of alternatives; specifications share data and are correlated; no inference is implied.

## 3. Intake shrinkage model (`analysis/intake_model.py`)

The published comparable intakes (THI 25, Saarland 44 and 42, Deggendorf ~60) fitted as a Gamma-Poisson shrinkage
model and mapped through the pre-registered relative-capture envelope give a predictive distribution for OTH
first-years: q05 21.0 / median 39.2 / q95 68.5, **92.5 % of the predictive mass inside the pre-registered 21-75**
and 3.8 % below the minimum cohort of 20. The anchored range is therefore consistent with a structured reading of
the same public evidence; it is not independent of the anchors: THI 25 and Deggendorf ~60 are in its sample, and the two Saarland values are one research-university programme in two years, while Bochum is left out for being a research university, so it is a consistency check, not independent confirmation. Including Bochum's 156 (research-university scale)
blows up the right tail (q95 164.7), which is why it stays a plausibility check. Limits: n = 4, a capacity is not an
intake, one value is an anecdote, publishers may be a selected sample; the pre-registered range remains the decision
input.

## 4. Required share vs demonstrated share, and accessibility (`analysis/capture_benchmark.py`)

- The minimum cohort of 20 equals **0.36 %** of OTH's own pool (5,501 qualified leavers); the central cyber case
  (39) equals **0.71 %** of the own pool and 0.21 % of the 100-km pool (18,630). TH Deggendorf's reported ~60
  corresponds to **1.07 %** of its equivalent nearest-site pool (5,595) - a peer is reported (one student review) to reach
  about half again more than OTH's central ask. THI's 25 against its (Munich-inflated) nearest-site pool of 22,785 is 0.11 %.
- Accessibility (demand access at d^-1.6 per unit of distance-weighted competition): cyber 24,644, robotics 13,696,
  AR/VR 50,433 leavers per competition unit. Relative to its nearest dedicated competitor's own location, OTH's
  index is 0.77 (cyber, vs THI) and 0.85 (robotics) - the Ingolstadt/Nuremberg corridor is demand-richer, which
  matches the catchment doc; OTH's case rests on its own low-competition pool, not on a better region. For AR/VR
  the index favours OTH (2.07), consistent with its one-competitor market.

## 5. Embedding-based cannibalisation profile (`analysis/cannibalisation_similarity.py`)

Programme embeddings (cached multilingual-e5 module vectors, ECTS-weighted, centred on the EMI centroid) give a
content-based profile of WHERE OTH-internal substitution would concentrate: for cyber the two security-focus
informatics programmes take 52.6 % of the profile (Industrie-4.0-Informatik 41.3 + Medieninformatik 11.3), for
robotics path B the KI family takes 41.3 % - the same programmes the Huff model and the hand check point at, so the
cannibalisation story does not depend on the title/focus rules alone. The E&IT pole that tops every raw list is a
known artefact of the dominant technical-vs-media axis and is read as generic overlap. Levels stay with the Step 48
shares (14-27 %) and the 50 % stress case; this profile is directional evidence only.

## 6. Demand corridors to 2030 (`analysis/demand_corridor.py`)

Corridors replace single projected points, using each pool's own backtest: the German cyber pool is the only one
with a validated trend model (drift, MASE 0.92); foreign pools get scenario bands (flat to compounded). Cyber's
central 39 becomes a 2030 corridor of **39.4-63.2** with a conservative point of **42.7** (validated German path,
foreign held flat) - the argument does not need the unvalidated foreign compounding to stay at or above the central
case. Robotics path B's corridor is 22.7-29.4 around its base-year 28.7 (flat, not falling off a cliff - but no
growth story either), AR/VR 37.7-65.3, the OT master 49.2-79.2 (graduates grow, but it fails F4).

## Scorecard (criteria D1-D7)

| # | Criterion | Result |
|---|---|---|
| D1 | additive only | pass: new modules, reports, tests and pipeline steps; no pre-registered file or result changed |
| D2 | reproduction gate | pass (automated test: tests/test_deep_analysis.py::test_reproduction_gate_passes) |
| D3 | every number generated; method and limits stated per module | pass |
| D4 | framed as sensitivity/benchmark around the pre-registered answer | pass (each report carries the framing) |
| D5 | tests | pass: 10 new tests; full suite green apart from this machine's known gaps (no data/raw, no streamlit) |
| D6 | argument brief complete with counterarguments | pass: docs/argument_brief.md |
| D7 | data-quality gate | pass: 26 of 26 checks |

## What this adds to the three-level answer

The answer itself does not move - that is by design. What changes is how it can be DEFENDED: the winner's rank
survives every specification in the project's own grid (100 % of 192), the viability of the central case survives
every capture specification in that grid (100 % cyber, 91 % robotics), the intake range is consistent with a
shrinkage model over the same public values (which include the two anchors), the required catchment share is modest
against a reported peer value, the cannibalisation reading is
confirmed by a content-based method, and the demand projection now has an honest corridor whose conservative end
still carries the argument. The known weak points stay visible and quantified: the cyber LOW scenario clears the
minimum cohort in only 55 % of specifications, robotics' low scenario never does, and both main spread drivers
(pool trend, high anchor) are declared assumptions.
