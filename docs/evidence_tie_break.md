# Evidence: hand check, three-level answer and demand tie-break

Criteria (fixed before building): `docs/criteria_tie_break.md`, `docs/criteria_handcheck_part1.md`,
`docs/criteria_handcheck_part2.md`. Generated tables: `reports/tie_break.md`
(`python -m study_program_intelligence.analysis.tie_break`), the gate and sensitivity tables below
(`python -m study_program_intelligence.report.handcheck_sheet`), `reports/ranking.md`. Hand-check sheet:
`docs/handcheck_sheet.md`. The demand ranking is not rerun before the 1 Nov job ads and the Trends downloads.

## Three-level answer

**What "existing resources" means here.** The supervisor's constraint is "feasible with EMI's existing staff and labs".
The project turned it into a testable rule, `configs/feasibility.yaml`, committed before any candidate was re-scored
(commit 71d281a, decision log "Feasibility rule pre-registered"): at least 80 % of the taught ECTS covered by existing
EMI modules (F1); at most 10 ECTS of teaching assignments and at most 10 ECTS of new modules by existing professors, and
at most 20 % new content in total, for a bachelor (F2); existing labs only (F3); at most 50 % from one OTH programme
(F4). **The 10-ECTS cap is the project's own operationalisation, not the supervisor's wording.** The same file
pre-registered a lenient sensitivity (F1 at least 70 %, up to 20 ECTS of new modules by existing professors); it is
reported, never used to decide.

| Level | Best option | Gate result | What it costs | How robust | Main risk |
|---|---|---|---|---|---|
| (a) Strict existing resources (the decision) | **None passes.** Nearest: Robotics + AI path B | robotics path B fails F2 only: 15 ECTS of new modules by existing professors against the cap of 10; AR/VR fails F1 (79.3 %) and F2 (25); the other four fail as in the equal-evidence step | - (robotics path B would need 5 ECTS more new teaching by existing professors than the cap allows) | the no-pass result would change only if row 9 or row 11 were confirmed instead of rejected (single-flip table) | the cap is our own operationalisation: a reader who accepts 15 ECTS of new teaching by existing staff as "existing resources" gets level (b) |
| (b) Lenient existing resources (small stretch, pre-registered sensitivity) | **Robotics + AI B.Sc., path B** (assistive / service), the only candidate that passes | F1 83.0 %, teaching assignments 8.25 ECTS, new modules by existing professors 15 ECTS, new content 17.0 % of 137 taught ECTS, F4 34.3 % (KI family); labs thin | no new professorship or lab; 15 ECTS of new modules by existing professors and 8.25 ECTS of teaching assignments (mechanics 5, quality management 2, the law part of RO 71 1.25) | thin: rejecting any further 5-ECTS module, or teaching all of RO 71 as a teaching assignment, makes it fail (single-flip table); the demand ranking is pending, so its demand position against other options is not measured | robotics projects on teaching-grade robots only (lab capacity unknown); its feeder subjects shrink (German first-years Bavaria -3.3 %/yr) |
| (c) With investment (the baseline) | **Cybersecurity B.Sc.** | fails the gate by design: it needs new staff and a lab | 2 new professorships, 1 lab engineer, a security lab (cost not estimated) | P(rank 1) 91.7 % in the baseline ranking; 78.2 % with demand trends from German first-years only, below the 80 % bar (docs/evidence_ranking.md) | most of the growing demand is foreign students (German cyber-proxy first-years Bavaria +1.9 %/yr); the intake estimate rests on THI's capacity 25 and an anecdotal Deggendorf ~60 |

**Recommendation by level.** Under the supervisor's constraint as we operationalised it, no candidate is feasible.
If the faculty accepts the small stretch, robotics path B is the recommendation. If it can invest, the cybersecurity
bachelor is. Which level applies is the faculty's decision, not the project's.

What the investment at level (c) would buy, from the baseline evidence:

| Item | Cybersecurity B.Sc. (with investment) | Source |
|---|---|---|
| Investment | 2 new professorships, 1 lab engineer, a security lab (cost not estimated) | docs/evidence_fit_staff.md |
| Why it is needed | EMI's modules cover at most about a third of a cyber bachelor's security content (31 %) | docs/evidence_fit_modules.md |
| Student pool | cyber proxy first-years Bavaria +5.9 %/yr 2019-24, but German only +1.9 %/yr | reports/demand_split.md |
| Students | gross first-years 21 / 39 / 75, net new to OTH 15.3 / 32.0 / 64.4 (low / central / high) | docs/evidence_cannibalisation.md |
| Job market | "Cyber Security" 851 ads in Germany, Bavaria 30.9 %, 191 within 100 km | docs/evidence_outlet_jobs.md |
| Competition | 4 dedicated bachelors within 150 km, none within about 80 km (THI 82 km) | configs/scores.yaml (cyber B.Sc. differentiation) |

Against robotics path B, the investment buys a growing pool (Informatik-led, mostly foreign) and an anchored intake
estimate (net new central 32.0 against 23.6 for robotics path B, both from the same model); it costs what constraint 1
rules out.

## Side-by-side demand comparison (AR/VR vs robotics path B)

**Status: pending.** This comparison was built to break the tie between the two candidates that passed the gate at
the time. After Soma's hand check AR/VR passes neither rule, so at level (b) robotics path B stands alone and the
comparison no longer decides between gate passes. It is kept, unchanged, for the demand ranking that is rerun after
the 1 Nov job ads and the Trends downloads.

Destatis first-years (1st university semester, winter semesters), 2019 -> 2024; "%/yr" is the yearly growth rate.
AR/VR's closest code is Medieninformatik (visual computing has no Destatis code of its own); robotics path B uses the
baseline feeders (Mechatronik + Technische Informatik).

| Signal | AR/VR & visual computing | Robotics path B | Favours | Strength |
|---|---|---|---|---|
| Closest series, Bavaria, all | Medieninformatik 216 -> 141, -8.2 %/yr | Mechatronik + TI 1,116 -> 1,082, -0.6 %/yr | robotics | medium for robotics; weak as a comparison, because AR/VR's proxy does not match how its competitors are classified (next row) |
| Does the proxy fit the competitors? | none of the 6 dedicated offers carries the catalogue subject Medieninformatik (0) | 5 of 19 carry Mechatronik or Technische Informatik | - | AR/VR's Destatis rows describe a neighbouring pool, not its own |
| German first-years, Bavaria | 191 -> 108, -10.8 %/yr | 680 -> 574, -3.3 %/yr | robotics on level; the trend score is the same (1 and 1 by the pre-registered rule) | medium |
| German first-years per dedicated Bavarian competitor institution (2024) | 108 (1 institution) | 96 (6 institutions) | about level | weak: a rough ratio |
| Foreign first-years, Bavaria | 25 -> 33, +5.7 %/yr | 436 -> 508, +3.1 %/yr | robotics on level, AR/VR on growth (small base) | medium |
| Foreign share 2024, Bavaria | 23 % | 47 % | robotics (international demand), but whether OTH could recruit them depends on the teaching language, for which there is no data | weak |
| Germany, all | 2,549 -> 2,094, -3.9 %/yr | 6,121 -> 5,387, -2.5 %/yr | robotics (slightly) | medium |
| Components of the closest series, Bavaria | - | Mechatronik 785 -> 762, -0.6 %/yr; TI 331 -> 320, -0.7 %/yr | - | - |
| Broad pool, Bavaria | Informatik 3,053 -> 4,110, +6.1 %/yr (German +2.3) | the same Informatik pool (robotics programmes also recruit there) | neither | weak |
| Dedicated competitors (institutions) | 6 in Germany, 1 in Bavaria, 1 within 150 km (Coburg 106 km), 0 within 80 km | 15 in Germany, 6 in Bavaria, 5 within 150 km (nearest THI 82 km), 0 within 80 km | AR/VR | strong: full catalogue |
| Capture model, net new to OTH (low / central / high) | 18.1 / 41.5 / 84.6 | 10.6 / 23.6 / 47.7 | AR/VR | weak: no intake anchor for either; it combines the pool and competitor rows under the model, so it is not an independent signal |
| Job ads, matching keywords | no data: "Virtual Reality", "Augmented Reality", "Computergrafik" are counted from the 1 Nov snapshot | "Robotik" 945 in Germany, 289 Bavaria, 162 within 100 km, 58 within 50 km (17 Oct); "Servicerobotik" from 1 Nov | no comparison yet | robotics measured (generic keyword), AR/VR missing |
| Search interest (Google Trends) | no data: terms below, manual download | "Robotik Studium" 2.4 % (2019), 3.5 % (2021), 3.4 % (2026, Jan-Oct) of "Informatik Studium": flat since 2021 | no comparison yet | robotics measured, AR/VR missing |
| Language of instruction of competitors | no data: the catalogue has no language field | no data: same | - | - |

**How the tie is decided (E3).** The Destatis rows are one signal, not several: the Bavarian total is German plus
foreign, the share is derived from them, and the Germany rows contain Bavaria. That signal favours robotics path B on
size, but it is a weak comparison because AR/VR's proxy matches none of its competitors. The competitor row favours
AR/VR and is strong. The capture model combines the two and is not independent. Job ads and Trends cannot be compared
yet. So two independent signals point in opposite directions and no single one may decide: **demand does not break the
tie yet.**

**Decision rule for the pending signals (fixed before the data arrive).** Four independent signal groups: (1) Destatis
pool (robotics), (2) competitors (AR/VR), (3) job ads, (4) search interest. A candidate wins on demand only if it
leads in at least three of the four; otherwise the demand tie stands and the decision moves to the hand check (fit)
and to Soma.
- (3) Job ads, 1 Nov snapshot, within 100 km of Amberg: the largest single count of "Virtual Reality", "Augmented
  Reality", "Computergrafik" against the largest of "Robotik", "Servicerobotik" (largest, not sum, to avoid counting
  one ad twice). The higher one leads; within 10 % of each other is neutral.
- (4) Google Trends, anchored download for Germany: the 2022-2026 slope of each candidate's best term as a share of
  "Informatik Studium" ("Virtual Reality Studium" or "Visual Computing Studium" against "Robotik Studium"). The higher
  slope leads; a difference under 0.1 percentage points a year is neutral.

What would change the reading of the existing signals: a public figure for Coburg Visual Computing's intake (it would
anchor AR/VR's capture model), or a Destatis breakdown that shows under which code visual-computing first-years are
counted.

## XR hardware (feasibility side, a limitation)

- OTH's public pages give no headset count. The Digitaler Campus page lists a "Labor VR/AR" (three responsible
  professors); the IKKI page lists an AR-/VR-Labor and a GPU lab with 32 workstations (`data/raw/oth_xr`, manifest
  `docs/oth_xr_manifest.json`). An older Labor Medieninformatik page lists HTC Vive and Microsoft HoloLens without
  quantities. OTH's sitemap has no page of its own for the AR/VR lab.
- Estimate (assumption, not a source): a cohort of about 40 with practicals in two groups of 20 needs 10 headsets at
  two students per headset, 20 at one each; the 32 GPU workstations would cover a group of 20. So the estimate is
  10-20 for a cohort of about 40.

## Google Trends: exact terms and settings for the manual download

Same settings as the baseline downloads (`docs/evidence_demand_trends.md`): trends.google.com, "Interest over time",
2004-present (monthly), all categories, web search; download the CSV. Save under `data/raw/trends/` with the names
below (they do not start with `trends_`, so the baseline Trends step is not affected).

| File | Region | Terms (one comparison, max 5) |
|---|---|---|
| tiebreak_DE_anchored.csv | Germany | Informatik Studium; Robotik Studium; Medieninformatik Studium; Virtual Reality Studium; Visual Computing Studium |
| tiebreak_BY_anchored.csv | Bavaria (Bayern) | the same five terms |
| tiebreak_DE_specialist.csv | Germany | Robotik Studium; Servicerobotik; Medieninformatik Studium; Virtual Reality Studium; Computervisualistik Studium |

The anchored downloads give each term's share of "Informatik Studium" (the baseline's robust metric and the input of
decision-rule group 4); the specialist download, without the large anchor, gives the small terms more resolution.

## Job-ad keywords for the 1 Nov snapshot

`configs/jobsuche.yaml` contains, besides the baseline "Robotik": "Servicerobotik" (robotics), "Virtual Reality",
"Augmented Reality", "Computergrafik" (AR/VR). They are counted for Germany, Bavaria, 50 km and 100 km around Amberg
from the 1 Nov snapshot on.

## Opposing view (fresh-context reviewer, E4)

**Attack.** The first draft concluded that robotics path B leads on demand. The reviewer argued the opposite:
- The five "robotics" rows are one Destatis series: Bavaria all = German + foreign, the share is derived, and Germany
  contains Bavaria.
- AR/VR's proxy matches none of its competitors. In the catalogue they are classified as Computervisualistik,
  Softwaretechnik or Mediendesign, never Medieninformatik. So the -8.2 %/yr describes a neighbouring pool, not AR/VR's.
  Against the broad Informatik pool, the modelled 58.5 gross first-years would be 1.4 % of Bavaria's 4,110.
- Robotics' feeder pool partly contains its competitors' own students: THI's robotics bachelor is classified as
  Mechatronik.
- Per competitor the German pools are about level (108 vs 96). Both German-only trend scores are 1 by the
  pre-registered rule.
- The capture model, the only signal that combines pool and competition, gives AR/VR almost twice robotics' net new
  first-years.
- The robotics outlet signals are generic: "Robotik" ads, not service robotics, and Trends flat since 2021.

**Answer.** The attack holds on the main point, and the conclusion was changed. Counted as independent signals, the
demand evidence has one signal for each side, and the criterion forbids letting one signal decide. So the tie is not
broken on demand yet. Two parts of the attack go too far:
- **Capture is not decisive.** It is not independent evidence: it rests on an assumed comparator intake at a single
  site, Coburg, which has no public figure.
- **The project's demand score is not a verdict.** The scored demand criterion is 2.37 vs 2.33, a difference of 0.04
  on a 1-5 scale: the capture model's lead for AR/VR (+0.54) almost cancels robotics' higher Destatis trend score (+0.5).

The decision now rests on the pre-registered rule above: with the existing signals split one to one, a candidate wins
on demand only if both missing signals point to it.

## Hand check (Soma's verdicts), gates under both rules, single-flip sensitivity

Soma's verdicts are recorded per sheet row in `configs/handcheck_sheet.yaml` (with reasons) and shown in
`docs/handcheck_sheet.md`: rows 1, 2, 4, 5, 6, 8, 10 and 12-17 confirmed; rows 3, 7, 9 and 11 rejected (reasons in the
YAML; the side-by-side facts behind rows 3, 7 and 9 are in `docs/handcheck_open_rows.md`). Row 16 is confirmed with its
law part taught as a teaching assignment. By Soma's instruction the law part is counted by its share of RO 71's
learning outcomes: outcome 1 of 4 is the legal framework („Verständnis rechtlicher Rahmenbedingungen“, hske_ba_robotik.pdf
p. 118), so 1.25 of its 5 ECTS. Outcome 4 also names the rules and laws machines must follow; counting it as law too
gives 2.5 ECTS, and teaching assignments of 9.5 ECTS still stay within the cap of 10.

Gates for all candidates under the strict rule (the decision) and the lenient sensitivity. AR/VR and robotics path B
with Soma's verdicts; the other four as in the equal-evidence step (`docs/evidence_candidates.md`); F3 = no module of
the path needs a lab EMI lacks:

<!-- gate table: generated by report.handcheck_sheet, do not edit -->

| candidate | rule | F1 % | T | N | F2 pass | F3 pass | F4 % | F4 pass | gate |
|---|---|---|---|---|---|---|---|---|---|
| robotics_b | strict | 83.0 | 8.25 | 15 | no | yes | 34.3 | yes | fail |
| robotics_b | lenient | 83.0 | 8.25 | 15 | yes | yes | 34.3 | yes | pass |
| arvr | strict | 79.3 | 0 | 25 | no | yes | 28.9 | yes | fail |
| arvr | lenient | 79.3 | 0 | 25 | no | yes | 28.9 | yes | fail |
| autonomous | strict | 93.4 | 0 | 10 | yes | yes | 77.0 | no | fail |
| autonomous | lenient | 93.4 | 0 | 10 | yes | yes | 77.0 | no | fail |
| energydata | strict | 69.4 | 26 | 18 | no | yes | 47.2 | yes | fail |
| energydata | lenient | 69.4 | 26 | 18 | no | yes | 47.2 | yes | fail |
| geodata | strict | 100.0 | 0 | 0 | yes | yes | 62.3 | no | fail |
| geodata | lenient | 100.0 | 0 | 0 | yes | yes | 62.3 | no | fail |
| ot_master | strict | 100.0 | 0 | 0 | yes | yes | 83.3 | no | fail |
| ot_master | lenient | 100.0 | 0 | 0 | yes | yes | 83.3 | no | fail |

<!-- end of gate table -->

Every adapted-module row flipped on its own (confirm -> reject, reject -> confirm), all other rows as recorded, under
both rules. A row belongs to one candidate, so a flip never affects the other. Reading: under the strict rule no
candidate passes, and robotics path B would pass if row 9 or row 11 were confirmed. Under the lenient rule robotics path
B passes; rejecting any further 5-ECTS module (rows 10, 12, 13, 15, 17), or teaching all of RO 71 as a teaching
assignment (row 16), makes it fail, while rejecting row 8 (4 ECTS) or row 14 (3 ECTS) alone does not. AR/VR would pass
the lenient rule if row 3 or row 7 were confirmed.

<!-- sensitivity table: generated by report.handcheck_sheet, do not edit -->

F1-F4 with Soma's verdicts (strict rule):

| candidate | open rows | open rows counted as | rows confirmed / rejected | F1 % | T | N | F2 pass | F4 % | F4 programme | gate (F1, F2, F4) |
|---|---|---|---|---|---|---|---|---|---|---|
| robotics_b | - | confirm | 8 / 2 | 83.0 | 8.25 | 15 | no | 34.3 | KI family: ba_ki + ba_iki | fail |
| robotics_b | - | reject | 8 / 2 | 83.0 | 8.25 | 15 | no | 34.3 | KI family: ba_ki + ba_iki | fail |
| arvr | - | confirm | 5 / 2 | 79.3 | 0 | 25 | no | 28.9 | KI family: ba_ki + ba_iki | fail |
| arvr | - | reject | 5 / 2 | 79.3 | 0 | 25 | no | 28.9 | KI family: ba_ki + ba_iki | fail |

Single flips:

| # | candidate | module | recorded | flipped to | F1 % | T | N | gate before | gate after flip | flips the gate | lenient gate before | lenient gate after flip | flips the lenient gate | other candidate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | arvr | Grundlagen des Visual Computing | confirm | reject | 73.6 | 0 | 32 | fail | fail | no | fail | fail | no | robotics_b: no effect |
| 2 | arvr | Bildverarbeitung 2 | confirm | reject | 75.2 | 0 | 30 | fail | fail | no | fail | fail | no | robotics_b: no effect |
| 3 | arvr | Mathematik für Visual Computing | reject | confirm | 83.5 | 0 | 20 | fail | fail | no | fail | pass | yes | robotics_b: no effect |
| 4 | arvr | Mensch-Maschine-Interaktion 2 | confirm | reject | 75.2 | 0 | 30 | fail | fail | no | fail | fail | no | robotics_b: no effect |
| 5 | arvr | Visual-Computing-Seminar | confirm | reject | 76.9 | 0 | 28 | fail | fail | no | fail | fail | no | robotics_b: no effect |
| 6 | arvr | Englisch (GER B2) 2 | confirm | reject | 77.7 | 2 | 25 | fail | fail | no | fail | fail | no | robotics_b: no effect |
| 7 | arvr | Interdisziplinäre Projektarbeit | reject | confirm | 87.6 | 0 | 15 | fail | fail | no | fail | pass | yes | robotics_b: no effect |
| 8 | robotics_b | RO 262 Robotik Projekt 1 | confirm | reject | 80.1 | 8.25 | 19 | fail | fail | no | pass | pass | no | arvr: no effect |
| 9 | robotics_b | RO 31 Wissenschaftliches Arbeiten und statistische Datenanalyse | reject | confirm | 86.7 | 8.25 | 10 | fail | pass | yes | pass | pass | no | arvr: no effect |
| 10 | robotics_b | RO 33 Aktorik | confirm | reject | 79.4 | 8.25 | 20 | fail | fail | no | pass | fail | yes | arvr: no effect |
| 11 | robotics_b | RO 34 Verteilte Softwaresysteme | reject | confirm | 86.7 | 8.25 | 10 | fail | pass | yes | pass | pass | no | arvr: no effect |
| 12 | robotics_b | RO 36 Robotik Projekt 2 | confirm | reject | 79.4 | 8.25 | 20 | fail | fail | no | pass | fail | yes | arvr: no effect |
| 13 | robotics_b | RO 45 Robotik Projekt 3 | confirm | reject | 79.4 | 8.25 | 20 | fail | fail | no | pass | fail | yes | arvr: no effect |
| 14 | robotics_b | RO 632 Robotik Projekt 4 Teil 1 | confirm | reject | 80.8 | 8.25 | 18 | fail | fail | no | pass | pass | no | arvr: no effect |
| 15 | robotics_b | RO 633 Robotik Projekt 4 Teil 2 | confirm | reject | 79.4 | 8.25 | 20 | fail | fail | no | pass | fail | yes | arvr: no effect |
| 16 | robotics_b | RO 71 Ethik und Recht im Kontext der Robotik | confirm | reject | 80.3 | 12 | 15 | fail | fail | no | pass | fail | yes | arvr: no effect |
| 17 | robotics_b | RO 6221 Mensch-Maschine-Interaktion | confirm | reject | 79.4 | 8.25 | 20 | fail | fail | no | pass | fail | yes | arvr: no effect |

<!-- end of sensitivity table -->

## Open risks

- AR/VR's Destatis proxy does not match its competitors' classification; the Destatis signal is weak as a comparison.
- AR/VR job ads and Trends are missing until 1 Nov and Soma's download; "Robotik" is a generic keyword.
- Both gate passes wait for Soma's hand check (`docs/handcheck_sheet.md`); the ranking is recomputed only after it.
- XR headset count unknown (estimate 10-20 for a cohort of about 40).
