# Evidence: equal evidence for the confirmed candidates

Criteria (fixed before building): `docs/criteria_equal_evidence.md`. Generated tables: `reports/feasibility.md`,
`reports/candidates.md`, `reports/ranking_candidates.md`. Configs: `configs/candidates.yaml`,
`configs/reference_documents.yaml`, `configs/feasibility_handcheck.yaml`, `configs/scores_candidates.yaml`.
Run: `python -m study_program_intelligence.analysis.feasibility`, `... .analysis.candidates`,
`... .analysis.ranking --candidates`.

Candidates (all six week-2 proposals; Soma delegated the choice, `docs/decision_log.md`):

| Key | Candidate | Level | Reference curriculum |
|---|---|---|---|
| robotics_b | Robotics + AI, path B (assistive / service) | bachelor | Hochschule Kempten Robotik (week 2) |
| autonomous | Autonomous mobile systems | bachelor | TH Deggendorf, Elektromobilität, autonomes Fahren und mobile Robotik |
| arvr | AR/VR & visual computing | bachelor | Hochschule Coburg, Visual Computing |
| energydata | Energy data management | bachelor | FH Dortmund, Energiewirtschaft und Energiedatenmanagement |
| geodata | Geo-data & geovisualisation | bachelor | Hochschule München, Geodata Science |
| ot_master | Reduced OT-security master | master | none fits; designed from EMI's existing master modules |

Two closer references could not be used: the HFT Stuttgart AR/VR handbook exists only on a studycheck.de mirror whose
robots.txt disallows PDFs, and the THWS Geovisualisierung handbook is under the disallowed `/fileadmin/` path.

## Result in one table

| Candidate | Gate F1-F4 | Why |
|---|---|---|
| robotics_b | **passes** | F1 91.2 %, T 7 + N 5 ECTS, educational robots only (thin), F4 25.5 % |
| arvr | **passes** | F1 91.7 %, N 10 ECTS (computer graphics), Visual Computing lab (thin), F4 32.2 % |
| autonomous | fails | 77.0 % from E&IT (F4) on the autonomous-driving / mobile-robotics track; F1 93.4 %, N 10 ECTS, labs sufficient |
| energydata | fails | F1 69.4 %, T 26 ECTS (energy economics, regulation, law, billing systems) + N 18 ECTS (energy efficiency, energy management, grid control) |
| geodata | fails | 62.3 % from OTH's own Geoinformatik und Landmanagement (F4) |
| ot_master | fails | 83.3 % from IT und Automation (strict), 58.3 % from KI master (lenient) (F4) |

Demand tie-break and the two-level answer (existing resources vs with investment): `docs/evidence_tie_break.md`.
The ranking under the gate is therefore a two-way comparison: AR/VR & visual computing ahead of robotics path B,
**P(rank 1) 73.5 %, below the 80 % robustness bar**; the lead hangs on one step of the fit rule (section 8), so the
two are reported as an open tie. The baseline winner (Cybersecurity B.Sc., 91.7 %) fails the gate.

## 1. Feasibility with existing resources (gate)

- **Method:** the week-2 method (e5, best EMI match, ECTS-weighted). The thresholds are calibrated on the week-2
  reference programmes only, and TF-IDF is fitted on the week-2 module set, so adding references does not move the
  week-2 numbers. The EMI module set did change: the parser had dropped the Digital Design module "AR/VR"; with it the
  recalibrated e5 threshold is 0.285 (was 0.277), as the pre-registered rule requires, and the automatic week-2 numbers
  were updated in `docs/evidence_feasibility.md` (no overall verdict changed; robotics' automatic match now also fails F1).
- **Hand check:** every taught core module of each reference got a verdict (E1, E2, T, N), as for robotics in week 2
  (`configs/feasibility_handcheck.yaml`, proposed by Claude). Frame modules (practical semester, thesis, placeholder
  electives) are left out; listed electives are not counted in F1, because a degree needs only some of them. Where a
  reference has specialisations, a student takes one: Kempten's paths A/B, and for TH Deggendorf the autonomous-driving
  / mobile-robotics track (FR); its electromobility track (EM: Leistungselektronik 2, Batterietechnologien,
  Ladestationen / Wasserstofftechnologie) is left out.

| Candidate | e5, all listed modules | TF-IDF, all listed modules | Gap | Hand check E1+E2 | E1 only | T | N | F3 | F4 largest |
|---|---|---|---|---|---|---|---|---|---|
| robotics_b | 75.4 % | 48.1 % | 27.3 pp | 91.2 % | 56.9 % | 7 | 5 | educational robots (thin) | 25.5 % KI |
| autonomous | 82.5 % | 56.1 % | 26.4 pp | 93.4 % | 73.0 % | 0 | 10 | sufficient on the FR track | 77.0 % E&IT |
| arvr | 55.4 % | 41.0 % | 14.4 pp | 91.7 % | 61.2 % | 0 | 10 | Visual Computing lab (thin) | 32.2 % II |
| energydata | 44.4 % | 50.0 % | -5.6 pp | 69.4 % | 34.0 % | 26 | 18 | - | 47.2 % E&IT |
| geodata | 58.2 % | 30.8 % | 27.4 pp | 100.0 % | 68.5 % | 0 | 0 | - | 62.3 % GI |
| ot_master | design: 100 % | - | - | 100 % | 100 % | 0 | 0 | IA labs; no OT-security testbed (thin) | 83.3 % IA |

**Method agreement (E3).** Gaps over 20 percentage points between e5 and TF-IDF, and how they were decided:

| Candidate | Gap | Decision |
|---|---|---|
| robotics_b | 27.3 pp | hand check decides (week 2): 91.2 %. TF-IDF misses modules that e5 matches under other names (e.g. RO 71 Ethik und Recht im Kontext der Robotik, RO 33 Aktorik) |
| autonomous | 26.4 pp | hand check decides: 93.4 % on the FR track (e5 counts both tracks). The verdict does not depend on F1: F4 fails |
| geodata | 27.4 pp | hand check decides: 100 %. Most matches are GI modules with other names (e.g. "Geo Sensorik" to "Ingenieurvermessung und Sensorik"); the verdict rests on F4 after the hand check (62.3 % GI); with the automatic match it would fail F1 (58.2 %) instead |

AR/VR (14.4 pp) and energy data (-5.6 pp, TF-IDF higher) are under the 20 pp line. The e5 and TF-IDF columns cover all listed modules,
electives included; the hand check covers core modules only. On the same core base e5 gives 62.0 % for AR/VR, 29.7 pp
below the hand check: e5 misses modules whose EMI twin has another name ("Programmieren 2" scores 0.232 against
"Programmierung 2"; its best automatic match is "Programmieren für KI 3 (Java)", 0.243) and counts nothing as adapted. Read without adapted modules (E1 only) AR/VR reaches 61.2 % and would fail F1; the same holds for robotics
path B (56.9 %). Both gate passes therefore rest on the E2 verdicts, which are proposed, not confirmed.

**Electives.** AR/VR students must choose 44 elective ECTS; the automatic match covers 75 ECTS of Coburg's listed
electives. Energy data must choose 12 elective ECTS and the automatic match covers 6 of its 36 listed elective ECTS: a weakness, not part of the gate. The Hochschule München handbook
lists 188 ECTS; the remaining 22 ECTS of the 210 are not described in it (presumably general electives).

**Reduced OT-security master.** No reference fits (the cyber/OT references reach at most 49 %: THI 49.4 %, HDBW 47.2 %, Deggendorf 0 % as an artefact), so the candidate is the
master that EMI's existing master modules could form: 20 security ECTS (all four master-level security modules), 30 OT
ECTS, 10 project ECTS. F1 and F2 pass by construction, but 83.3 % of it is listed by IT und Automation; even if every
module shared with another master is attributed to that master, 58.3 % comes from the KI master. It fails F4: it is
an IT und Automation profile, not a new programme.

## 2. Demand (Destatis first-years; master: graduates)

Closest subject codes (`configs/candidates.yaml`); Bavaria and Germany, German and foreign nationality separately.
Trend scores by the rule fixed before computing (Bavaria; at least +5 %/yr = 4, +1 = 3, -2 = 2, below = 1); the rule
reproduces all six baseline trend scores.

| Candidate | Series | Bavaria 2019 -> 2024 | Bavaria %/yr | German %/yr | Foreign %/yr | Germany %/yr | Score (German only) |
|---|---|---|---|---|---|---|---|
| robotics_b | Mechatronik + Technische Informatik | 1,116 -> 1,082 | -0.6 | -3.3 | 3.1 | -2.5 | 2 (1) |
| autonomous | Fahrzeugtechnik + Mechatronik | 1,191 -> 1,318 | 2.0 | -3.0 | 10.1 | -4.1 | 3 (1) |
| arvr | Medieninformatik | 216 -> 141 | -8.2 | -10.8 | 5.7 | -3.9 | 1 (1) |
| energydata | Elektrische Energietechnik + Regenerative Energien | 109 -> 147 | 6.2 | 7.1 | 5.7 | -2.9 | 4 (4) |
| geodata | Vermessungswesen + Kartografie | 299 -> 200 | -7.7 | -12.2 | 3.7 | -5.3 | 1 (1) |
| ot_master | Informatik graduates (2019 -> 2025) | 2,676 -> 4,788 | 10.2 | 7.2 | 19.2 | 7.4 | 4 (4) |

- Every bachelor series except energy data falls for German first-years in Bavaria. Autonomous systems grows only
  through foreign first-years (German -3.0 %/yr, foreign +10.1 %/yr); energy data and the master pipeline grow for
  both groups.
- AR/VR's series is a rough proxy: visual computing has no Destatis subject code of its own, Medieninformatik is the
  closest, and it had only 141 first-years in Bavaria in 2024.
- Energy data grows from a small base (109 -> 147 first-years).
- **Google Trends: no data.** The Trends API is not public; the search terms are listed per candidate in
  `configs/candidates.yaml` for a manual download by Soma. The trend scores above rest on Destatis only (the baseline
  scores also used search interest).
- **BA job ads: no counts yet.** The keywords are added to `configs/jobsuche.yaml` and are counted from the 1 Nov
  snapshot. Until then labour relevance uses only the shortage condition of the anchor (BA Engpassanalyse 2025,
  specialist top 10): Informatik (4310, 2.0) for AR/VR, Elektrotechnik (2630, 2.2) and technical R&D (2710, 2.0) for
  autonomous systems; energy economics and geoinformatics are not in the top 10 (unknown). Robotics path B and the OT
  master keep the baseline scores, which rest on ad counts.

## 3. Competition (full catalogue, full-time offers)

Dedicated = theme in the title; focus = theme only in the focus field. Themes and exclusions in `configs/candidates.yaml`
(hand-checked on every hit within 150 km, `reports/candidates.md`). Maps: `reports/figures/competitors_<key>.png`.

| Candidate | Dedicated institutions Germany | Bavaria | Within 150 km | Within 80 km | Nearest | OTH's own matches |
|---|---|---|---|---|---|---|
| robotics_b | 15 | 6 | 5 | 0 | TH Ingolstadt 82 km | E&IT, KI B.Sc. (focus) |
| autonomous | 6 | 3 | 3 | 1 | FAU Erlangen-Nürnberg 63 km | - |
| arvr | 6 | 1 | 1 | 0 | Hochschule Coburg 106 km | Digital Design (focus) |
| energydata | 1 | 0 | 0 | 0 | FH Dortmund 386 km | KI B.Sc. (focus) |
| geodata | 16 | 3 | 3 | 0 | Universität Augsburg 138 km | **Geoinformatik und Landmanagement (dedicated)** |
| ot_master | 15 | 3 | 3 | 0 | TH Ingolstadt 82 km | Digital Business M.Sc. (focus) |

- Energy data is the rarest type (one institution in Germany); AR/VR is rare too (six institutions, one in Bavaria).
- Geo-data is a type OTH already offers: kill rule 1 risk, consistent with its F4 failure.

## 4. Capture and cannibalisation (Step 47/48 model)

The model is unchanged; sites come from the full catalogue (Bavaria). **No new candidate has a public intake figure
for a comparator**, so the robotics logic applies to the three own runs (autonomous, AR/VR, geo-data): assumed comparator intake 20-60 at the nearest dedicated
site, range over all model variants. Robotics path B and the OT master reuse the baseline robotics and cyber-master
runs (same competitor set).

| Candidate | Comparator | Gross first-years low / central / high | Net new to OTH | From OTH programmes | Kept in region |
|---|---|---|---|---|---|
| robotics_b | none (THI site, assumed 20-60) | 14.9 / 28.7 / 55.3 | 10.6 / 23.6 / 47.7 | 4.3 / 5.1 / 7.6 | 4.1 / 8.5 / 15.6 |
| autonomous | none (FAU site, assumed 20-60) | 10.1 / 21.8 / 46.9 | 7.2 / 17.9 / 40.3 | 3.0 / 3.8 / 6.5 | 3.0 / 6.3 / 12.0 |
| arvr | none (Coburg site, assumed 20-60) | 29.9 / 58.5 / 114.4 | 18.1 / 41.5 / 84.6 | 11.8 / 17.0 / 29.8 | 2.6 / 5.6 / 11.7 |
| energydata | no site in Bavaria at all | 10.0 / 24.5 / 60.0 | 6.1 / 17.4 / 51.7 | 3.9 / 7.1 / 8.3 | 0.8 / 2.5 / 17.8 |
| geodata | none (Augsburg site, assumed 20-60) | 14.0 / 26.4 / 49.9 | 8.7 / 17.7 / 37.8 | 5.3 / 8.8 / 12.1 | 1.1 / 2.4 / 5.5 |
| ot_master | THI capacity 30 (baseline master) | 22.7 / 42.9 / 81.2 | 14.3 / 31.5 / 62.9 | 8.4 / 11.5 / 18.2 | 0.7 / 2.2 / 5.5 |

- **AR/VR's high capture is a model artefact risk.** It has only one dedicated competitor in Bavaria, so OTH is
  predicted to draw 1.50-1.91 times Coburg's intake. The central 58.5 gross first-years would be 41 % of all 141
  Medieninformatik first-years in Bavaria in 2024. Tested in the ranking (AR/VR capture replaced by robotics' rows).
- **Energy data:** with no competitor site in Bavaria the Huff split is degenerate (everything would come from OTH);
  the gross range is the assumption widened to 10-60 and the shares are the span of the other candidates' runs.
- **Geo-data:** OTH's GI counts as a dedicated site, so a third of the students would come from OTH.

## 5. Lab reality check (whole degree)

| Candidate | What the whole degree needs | EMI's public lab list | Verdict |
|---|---|---|---|
| robotics_b | four robotics project modules and service-robotics practice | Physical Computing lab: Mindstorms and Aldebaran humanoids (teaching grade) | **thin**: cohort-size capacity unknown |
| arvr | VR/AR headsets and tracking, GPU workstations for computer graphics | Visual Computing lab (spatial computing, 3D computer graphics courses); OTH's AI competence centre IKKI (Digitaler Campus) has a GPU lab with 32 workstations and an AR/VR lab; Labor Medieninformatik lists HTC Vive and Microsoft HoloLens without quantities (page from about 2020); AR/VR modules in DD ("AR/VR", head-mounted displays), GI and IA/MKI (Unity) | **thin**: GPU seats documented (32), XR headset count unknown |
| autonomous | FR track: sensors, control, mobile robots and vehicle automation (the battery, charging and hydrogen needs belong to the EM track, which is left out) | power electronics, drives, control and measurement labs; educational robots; a race-car project in the KI programme | sufficient for the FR track (vehicle platforms for cohort projects not documented) |
| energydata | power-system lab, energy-data and billing software | high-voltage and power-electronics labs | software licences unknown; not a lab gap |
| geodata | surveying and GNSS equipment | not in the EMI lab list; GI's own modules (Vermessungskunde 1-3, Satellitenpositionierung) need such equipment, so OTH has it | sufficient (GI's equipment, not listed) |
| ot_master | OT testbed for security practice | automation, PLC and industrial-communication labs | **thin**: no isolated security lab (week 2) |

A thin lab case lowers the feasibility score from 5 to 4 at the low end; it does not fail the gate.

## 6. Neighbouring countries

Only the two candidates that pass the gate could change the ranking. No foreign data was collected. In this model the only criterion a
foreign competitor could move is differentiation (weight 0.10): Plzeň (Czech Republic) is about 115 km from Amberg
(straight line, city-centre coordinates 49.75 N, 13.38 E). The
ranking was rerun with AR/VR's differentiation one step lower (4 -> 3) as a stress test: AR/VR stays first but only at
51.7 %. Under the differentiation rule one Plzeň programme alone would not cause that step (two institutions within
150 km still score 4); it needs one within 80 km, two more within 150 km, or the same profile nearby. Checking Plzeň's
programmes is still worth doing before the freeze.

## 7. Ranking with the gate, next to the frozen baseline

Same weights, Monte Carlo (10,000 draws, seed 42) and capture logic as the baseline (`reports/ranking_candidates.md`).
Candidates that fail the gate are excluded; their central scores are shown for comparison only.

| | Baseline (with new resources) | Equal evidence, gate F1-F4 |
|---|---|---|
| Winner | Cybersecurity B.Sc., P(rank 1) 91.7 % | AR/VR & visual computing B.Sc., P(rank 1) 73.5 % |
| Second | Cyber/OT M.Sc. 6.0 % | Robotics + AI B.Sc. path B 26.5 % |
| Gate | not applied | cyber options fail; four of six candidates fail |

Central weighted totals: arvr 3.63, robotics_b 3.45 (gate passed); ot_master 3.14, autonomous 2.90, energydata 2.58,
geodata 2.43 (gate failed, excluded).

**Robustness (E4).** P(rank 1) of AR/VR:

| Scenario | AR/VR | Robotics path B |
|---|---|---|
| (a) base | 73.5 % | 26.5 % |
| (b) German-only trends | 89.1 % | 10.9 % |
| (c) lenient feasibility gate | 73.5 % | 26.5 % |
| (d) leave one criterion out | first in all six (51.5-98.0 %) | - |
| 50 % cannibalisation for both | 82.5 % | 17.5 % |
| independent capture draws | 68.1 % | 31.9 % |
| AR/VR capture = robotics rows | 43.3 % | 56.7 % |
| AR/VR differentiation one step lower | 51.7 % | 48.3 % |
| AR/VR institutional fit 4 (more than 10 new ECTS) | 51.8 % | 48.2 % |
| all AR/VR counter-arguments at once | 1.2 % | 98.8 % |

AR/VR is first in (b), (c) and every (d) run, but (a) is below 80 %: **not robust**. At central scores the lead is 0.18 points
(3.63 vs 3.45): institutional fit adds 0.20 and differentiation 0.10, student demand 0.01, labour relevance takes away
0.10 and regional contribution 0.03. Leaving out institutional fit or differentiation brings it to a near tie (51.6 % and 51.5 %);
capture is the largest uncertainty (43.3 % when replaced by robotics' rows).

## 8. Argument check for the leading candidate (AR/VR & visual computing B.Sc.)

| Claim | Evidence | Strength | What would change it |
|---|---|---|---|
| EMI can run it with existing staff and labs | hand check 91.7 % E1+E2, 10 ECTS new by existing professors (computer graphics) | medium: proposed hand check; E1 only 61.2 % | any rejected E2 module adds new ECTS: as N it breaks the N cap (already 10), as teaching assignments it fails F2 above 10 ECTS, and F1 falls below 80 % above 14 ECTS; any rejection lowers fit to 4 (a tie); too few XR headsets for a cohort |
| Few competitors | 1 dedicated institution in Bavaria, 6 in Germany | strong: full catalogue | foreign or new programmes that lower the score under the rule: one within 80 km, two more within 150 km, or the same profile nearby (Plzeň not checked) |
| Enough students | model: 58.5 gross first-years (central) | weak: no intake anchor; one comparator site | an intake figure for Coburg Visual Computing; capture at robotics' level flips the ranking |
| Demand trend | Medieninformatik first-years Bavaria -8.2 %/yr | medium: proxy code | a better proxy (visual computing inside Informatik) |
| Graduate outlet | Informatik is a specialist shortage occupation | weak: ad counts pending | the 1 Nov / 15 Nov / 1 Dec snapshots for "Virtual Reality", "Augmented Reality", "Computergrafik" |

**Strongest counter-argument (fresh-context reviewer, E7).** AR/VR is ahead because of one cut-off and one
unanchored model run, not on the evidence. Institutional fit (5 vs 4) adds 0.20, more than its whole central lead of
0.18, and that step is the staff rule "new ECTS <= 10 -> 5": AR/VR needs exactly 10 new ECTS, robotics path B 12. With fit 4, AR/VR's total
would be 3.43 and robotics path B (3.45) would lead at central scores; in the Monte Carlo the two tie
(AR/VR 51.8 %). The 10 ECTS are Computergrafik 1 and 2; no EMI bachelor
module is a computer-graphics programming course (GI's VR/AR module and MT/DD "Visual Computing" touch on 3D rendering). OTH documents 32 GPU
workstations and an AR/VR lab (IKKI), but no XR headset count; Labor Medieninformatik lists HTC Vive and HoloLens
without quantities on a page from about 2020. EMI's AR/VR teaching is spread over single modules: among them DD's
"AR/VR" (5 ECTS profile module), GI's "Virtual / Augmented Reality", Educational Technology's "VR und AR in der
Weiterbildung" and the master elective "Ausgewählte Themen AR/VR" (IA/MKI), capped at 20 participants. The gate pass rests on proposed E2 verdicts (E1 only: 61.2 %). The
model's 58.5 first-years would be 41 % of a Bavarian Medieninformatik pool that falls by 8.2 %/yr. Robotics path B
scores higher on labour relevance (partly on ad counts) and keeps more students in the region (8.5 vs 5.6 central).
With German-only trends, AR/VR capture at half of robotics' net new first-years, differentiation one step lower
(neighbouring countries) and fit 4 applied together, AR/VR's P(rank 1) falls to 1.2 %.

**Answer.** The attack holds. The fit rule was written before the ranking and is not changed after it, but the lead
depends on one step of it, so the result is reported as a tie that the evidence does not yet separate, not as a
recommendation for AR/VR. Four pieces of evidence decide it, in this order: (1) Soma's confirmation or rejection of the
E2 verdicts and of who teaches Computergrafik 1 and 2 (if it needs more than 10 new ECTS, fit drops to 4: robotics
path B leads at central scores and the Monte Carlo is a tie); (2) an inventory of EMI's XR hardware against a cohort; (3) the job-ad snapshots for the new keywords;
(4) a check of programmes in Plzeň. An intake figure for Coburg Visual Computing would replace the assumed comparator
intake, the largest uncertainty in AR/VR's capture.

## Evidence completeness (E1)

Value = measured or modelled in this step; "no data" carries its reason.

| Criterion | robotics_b | autonomous | arvr | energydata | geodata | ot_master |
|---|---|---|---|---|---|---|
| F1-F4 with hand check | value | value | value | value | value | value (design) |
| e5 vs TF-IDF | value | value | value | value | value | not applicable: no reference curriculum |
| Destatis German / foreign | value | value | value | value | value | value |
| Google Trends | no data: manual download pending | no data: same | no data: same | no data: same | no data: same | no data: same |
| BA job-ad counts | value (baseline "Robotik"); new keyword from 1 Nov | no data: first snapshot 1 Nov | no data: same | no data: same | no data: same | value (baseline cyber keywords) |
| Shortage occupation | value | value | value | value (not in top 10) | value (not in top 10) | value |
| Competition count and map | value | value | value | value | value | value |
| Capture and cannibalisation | value (no anchor) | value (no anchor) | value (no anchor) | value (no comparator, widened) | value (no anchor) | value (THI anchor) |
| Lab check, whole degree | value (thin) | value (FR track sufficient) | value (thin) | value | value | value (thin) |
| Neighbouring countries | no data; not varied (only AR/VR's run) | not needed: fails the gate | no data; sensitivity run (differentiation 3) | not needed: fails the gate | not needed: fails the gate | not needed: fails the gate |
| Ranking score | value | value (excluded) | value | value (excluded) | value (excluded) | value (excluded) |

## Open risks

- The gate passes of AR/VR and robotics path B rest on proposed E2 verdicts (Soma's confirmation pending).
- AR/VR's capture has no intake anchor and only one comparator site; its demand proxy is rough and falling.
- No ad counts for the new keywords before 1 Nov; no Google Trends data (manual download).
- Lab capacity at cohort size is unknown for both candidates that pass (XR device types listed without quantities on an old lab page; teaching-grade robots).
