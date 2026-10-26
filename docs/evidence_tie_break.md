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
| (a) Strict existing resources (the decision rule) | **None passes the full gate.** Closest: Robotics + AI path B | robotics path B fails F2 only: 15 ECTS of new modules by existing professors against the cap of 10. Autonomous systems, geo-data and the reduced OT master pass F1-F3 (coverage, new teaching, labs) and fail only F4, the rule against taking most of the content from one existing OTH programme; AR/VR fails F1 (79.3 %) and F2 (25); energy data fails F1 and F2 | the smallest new resource that would let robotics path B pass: 5 ECTS of new teaching beyond the cap if whole modules stay new modules by existing professors, about 4 SWS a year (configs/feasibility.yaml: 10 ECTS is about 8 SWS a year); if 1.75 ECTS of it are moved into teaching assignments up to their cap (8.25 + 1.75 = 10), 3.25 ECTS (about 2.6 SWS) remain beyond the caps; moving all 5 ECTS would breach the teaching-assignment cap (8.25 + 5 = 13.25 against 10). All on the 137-ECTS reference base; scaled to 165 taught ECTS the gap is about 8.1 ECTS (about 6.5 SWS), or 8.0 with the split | among single flips, only confirming row 9 or row 11 would change the no-pass result (single-flip table); confirming rows 3 and 7 together would let AR/VR pass | the cap is our own operationalisation; the configs/feasibility.yaml assumption treats up to 10 ECTS (about 8 SWS a year) as absorbable, and 15 ECTS is outside it |
| (b) Lenient existing resources (pre-registered sensitivity, reported, not used to decide) | Robotics + AI B.Sc., path B (assistive / service): the only candidate that passes | F1 83.0 %, teaching assignments 8.25 ECTS, new modules by existing professors 15 ECTS, new content 17.0 %, F4 34.3 % (KI family); labs thin | no new professorship or lab; 15 ECTS of new modules by existing professors (about 12 SWS a year by the same assumption) and 8.25 ECTS of teaching assignments (mechanics 5, quality management 2, the law part of RO 71 1.25) | thin on two caps: rejecting any further 5-ECTS module that would become a new module by an existing professor (rows 10, 12, 13, 15, 17) pushes new content over the 20 % share (28.25 of 137 ECTS), and teaching all of RO 71 as a teaching assignment breaks the teaching-assignment cap (T 12) (single-flip table); with RO 71's law part at 2.5 ECTS the teaching-assignment headroom is 0.5 ECTS; with the recorded 1.25 ECTS, scaled to OTH's 165 taught ECTS (below), the headroom is about 0 | it wins by elimination, not on demand: its demand position is pending; its feeder subjects shrink (German first-years Bavaria -3.3 %/yr); robotics projects run on teaching-grade robots (lab capacity unknown) |
| (c) With investment (outside constraint 1; the baseline result) | Cybersecurity B.Sc. | fails the gate by design: it needs new staff and a lab | 2 new professorships, 1 lab engineer, a security lab (cost not estimated) | P(rank 1) 91.7 % in the baseline ranking of three options (cyber bachelor, cyber/OT master, Robotics + AI B.Sc.); 78.2 % with demand trends from German first-years only, below the 80 % bar (docs/evidence_ranking.md); not comparable with the six re-scope candidates, which were never ranked against it | most of the growing demand is foreign students (German cyber-proxy first-years Bavaria +1.9 %/yr); the intake estimate rests on THI's capacity 25 and an anecdotal Deggendorf ~60 |

Shares at level (b) are relative to the reference curriculum's taught core modules (137 ECTS at Hochschule Kempten), as
in every hand check since week 2. Scaled to the 165 taught ECTS that configs/feasibility.yaml sets for an OTH bachelor,
F1 and the new-content share stay the same, teaching assignments become 9.9 ECTS and new modules by existing
professors 18.1 ECTS: still within the lenient caps, with almost no headroom on teaching assignments.

The F4 figure for robotics path B has three values in the documents: 25.5 % in week 2 (automatic programme match),
38.0 % on the hand-check sheet with every adapted module confirmed (programme of the EMI module the sheet names), and
34.3 % after Soma's verdicts (rejected modules no longer count for a programme). All three pass the 50 % limit.

### Three-level table, continued: first-years and resource need per level

| Level | Option | First-years, year 1 (low / central / high) | First-years, steady state (low / central / high); central German + international | Minimum cohort of 20 | Professor-equivalents | Per expected first-year, steady state (central / low) |
|---|---|---|---|---|---|---|
| (a) | none passes; smallest new resource for robotics path B | – | – | – | 0.11 (5 ECTS, 4 SWS a year, 137-ECTS reference base; about 0.18 scaled to 165 taught ECTS) | – |
| (b) | Robotics + AI path B | 8.9 / 17.1 / 33.0 | 14.9 / 28.6 / 55.1; 12.4 + 16.2 | missed in the low case (14.9) and in year 1 of the central case (17.1) | 0.52 (15 + 8.25 ECTS, 18.6 SWS a year, 137-ECTS reference base; 0.62 scaled to 165 taught ECTS; no new position) | 0.018 / 0.035 (scaled: 0.022 / 0.042) |
| (c) | Cybersecurity B.Sc. | 16.6 / 30.8 / 59.2 | 32.2 / 59.8 / 115.1; 24.3 + 35.6 | missed only in year 1 of the low case (16.6) | 3.22 (2 professorships, 1 lab engineer, 10 ECTS of teaching assignments) | 0.054 / 0.100 (without the trend projection, 39 / 21 first-years: 0.083 / 0.153) |

How the numbers are made (`analysis/first_years.py`, `analysis/cost.py`; inputs `configs/first_years.yaml`,
`configs/cost.yaml`; generated tables `reports/first_years.md`, `reports/cost.md`):
- **Same code path for every option.** The Step 47/48 Huff model's gross steady-state intake (cyber 21 / 39 / 75,
  unchanged), split into German and international students by the mix of the option's Bavarian subject pool in its
  base year, each group projected with its pool's yearly growth 2019-24, then the ramp-up 60 / 80 / 100 %. Assumed:
  first intake in winter 2028/29, steady state in year 3. For robotics path B the German pool's −3.3 %/yr lowers the
  German first-years; the foreign pool's +3.1 %/yr nearly offsets it (central steady state 28.6 with the trends, 28.7
  without). Cyber's projected numbers rise mainly through foreign first-years growing 12.8 %/yr, carried on to 2030.
- **The pool trend is not a validated forecast.** In a rolling-origin backtest of robotics' German pool (origins
  2012-2023, horizons 1-5) no model beats the naive scale: best MASE 1.30 (last value carried forward); a trend model
  (drift) scores 2.03. The forecast does not beat naive. Cyber's German pool: drift 0.92.
- **Professor-equivalent** = 18 SWS per semester, the regular teaching load (Regellehrverpflichtung) of a professor
  in civil-servant status at a Bavarian HAW (AVBayHIG § 4 Abs. 1 Nr. 1: "Professorinnen und Professoren 18
  Lehrveranstaltungsstunden", gesetze-bayern.de), so 36 SWS-semesters a year;
  ECTS to SWS by the configs/feasibility.yaml assumption (10 ECTS ≈ 8 SWS a year). A new professorship counts 1; the
  lab engineer is counted as one position (a headcount convention, not a salary comparison). Lab and equipment cost:
  not estimated.

**Opposing view on the cost comparison (fresh-context reviewer, E6).** Attack: the per-first-year column compares
different kinds of cost. Level (b) counts only new teaching (15 ECTS by existing professors plus 8.25 ECTS of teaching
assignments); level (c) counts whole
new positions, and the lab engineer adds a position with no teaching. On new teaching alone (cyber: the 45 ECTS taught
by the new professors, docs/evidence_benchmarks.md, plus 10 ECTS of teaching assignments) cyber needs 1.22
professor-equivalents, 0.020 / 0.038 per first-year (central / low; 0.031 / 0.058 without the trend projection),
against 0.018 / 0.035 for robotics path B on the 137-ECTS reference base; scaled to 165 taught ECTS robotics path B
needs 0.62, 0.022 / 0.042 per first-year, so on new teaching alone it is not cheaper per first-year. So the column does not show that robotics path B teaches a student more
cheaply; it shows that it needs no new position, which is constraint 1 itself. The reviewer also noted: the numerator
is a fixed yearly load, so the ratio moves one-for-one with the intake forecast and means little below the minimum
cohort (robotics low 14.9, central year 1 17.1); the existing professors' share of level (b) (15 ECTS) is taken from other work, not free; extra
lab and exercise groups that grow with the cohort are not counted for either option. Answer: accepted. The column is kept only with this reading: annual new resource divided by
annual intake, not cost per enrolled student and not a cost-efficiency ranking.

**The project's answer.** Under the decision rule, no candidate passes. The closest is robotics path B: it misses only
the cap on new modules by existing professors (15 against 10 ECTS, the project's own operationalisation). It is a
conditional candidate, not a recommendation, until two conditions hold: the faculty confirms that about 15 ECTS (about
12 SWS a year; about 18 ECTS or 14.5 SWS scaled to 165 taught ECTS) of new teaching by existing professors is
absorbable, and the demand data due after 1 Nov do not go
against it. If the faculty can invest instead, the cybersecurity bachelor is the baseline answer, outside constraint 1.

**What would change this answer:** the faculty ruling out about 15 ECTS of new teaching by existing professors (level
(b) falls away); confirming hand-check row 9 or row 11 (robotics path B passes the strict rule); or the demand data
after 1 Nov triggering the downgrade rule in configs/demand_thresholds.yaml.

What the investment at level (c) would buy, from the baseline evidence:

| Item | Cybersecurity B.Sc. (with investment) | Source |
|---|---|---|
| Investment | 2 new professorships, 1 lab engineer, a security lab (cost not estimated) | docs/evidence_fit_staff.md |
| Why it is needed | EMI's modules cover at most about a third of a cyber bachelor's security content (31 %) | docs/evidence_fit_modules.md |
| Student pool | cyber proxy first-years Bavaria +5.9 %/yr 2019-24, but German only +1.9 %/yr | reports/demand_split.md |
| Students | gross first-years 21 / 39 / 75, net new to OTH 15.3 / 32.0 / 64.4 (low / central / high) | docs/evidence_cannibalisation.md |
| Job market | "Cyber Security" 851 ads in Germany, Bavaria 30.9 %, 191 within 100 km | docs/evidence_outlet_jobs.md |
| Competition | 4 dedicated bachelors within 150 km, none within about 80 km (THI 82 km) | configs/scores.yaml (cyber B.Sc. differentiation) |

Against robotics path B, the investment buys a growing pool (Informatik-led; 80 % of the growth is foreign students) and an anchored intake
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

**Demand thresholds (pre-registered before the 1 Nov data; `configs/demand_thresholds.yaml`, applied by
`analysis/demand_thresholds.py`).** Job ads: the 1 Nov snapshot, within 100 km of Amberg, each group's largest single
keyword count (robotics: "Robotik", "Servicerobotik"; AR/VR: "Virtual Reality", "Augmented Reality", "Computergrafik").
Trends: the OLS slope 2022-2026 of each term's yearly (January-October) mean share of "Informatik Studium", in
percentage points a year. The 3-of-4 rule above is unchanged.

| Comparison | Signal | Favours robotics path B | Neutral | Goes against robotics path B |
|---|---|---|---|---|
| Robotics path B vs AR/VR | job ads | robotics count > 1.10 x AR/VR count | larger / smaller <= 1.10 | AR/VR count > 1.10 x robotics count |
| Robotics path B vs AR/VR | Trends slope | robotics slope higher by >= 0.1 | difference < 0.1 | AR/VR best slope higher by >= 0.1 |
| Robotics path B vs minimum cohort of 20 | job ads | robotics count >= 150 (the ">150 ads within 100 km" anchor of configs/scores.yaml, taken as >= 150) | 75-149 | <= 74 |
| Robotics path B vs minimum cohort of 20 | Trends slope of "Robotik Studium" | >= +0.1 | between | <= -0.1 |

Downgrade from "conditional candidate" to "not recommended": both robotics-vs-minimum-cohort signals go against; or
one goes against and the capture model's central steady-state gross first-years for robotics path B are below 20
(28.7, the model's base-year value; 28.6 with the trend projection). At pre-registration robotics already had 162
"Robotik" ads within 100 km (17 Oct snapshot), above the 150 threshold, and 28.7 is above 20, so a downgrade needs the
count to fall to 74 or fewer and the "Robotik Studium" slope to be -0.1 or lower.
AR/VR winning the 3-of-4 rule does not downgrade robotics on its own, because AR/VR fails the feasibility gate.

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

## Opposing view on the three-level answer (fresh-context reviewer, E4)

**Attack.** The supervisor asked for one programme. The re-scope plan said what to do if nothing passed: report it
plainly, show the lenient sensitivity and name the smallest new resource (docs/rescope_plan.md). The first draft
instead called robotics path B "the recommendation" under the lenient rule, which configs/feasibility.yaml says is
"never used to decide", and left the choice of level to the faculty. Robotics path B wins level (b) by elimination:
after the hand check its new modules by existing professors rose from 5 to 15 ECTS, beyond the 10 ECTS the config treats as absorbable, and
one more rejected 5-ECTS module makes it fail; its feeder subjects shrink and its demand evidence is pending; its modelled
net new first-years (23.6) are below the OT master's (31.5) and AR/VR's (41.5). Level (c) brings back an answer that
constraint 1 rules out. And "no candidate is feasible with existing resources" is not literally true: autonomous
systems, geo-data and the OT master pass the staff and lab tests and fail only F4.

**Answer.** Most of the attack holds, and the section was changed:
- level (b) is labelled a sensitivity, and the answer above names one candidate with its conditions instead of handing
  the choice to the faculty;
- level (a) now separates the three candidates that fail only F4 from those that fail on resources;
- the smallest new resource is stated (5 ECTS, about 4 SWS a year, with whole modules; 3.25 ECTS, about 2.6 SWS, if part
  of it fills the free teaching-assignment headroom; on the 137-ECTS reference base, about 8 ECTS scaled to 165);
- the 137 vs 165 ECTS base is disclosed with the scaled check;
- level (c) is marked as outside constraint 1, with its P(rank 1) labelled as coming from the three-option baseline.

Two parts are not adopted:
- **F4 stays a gate.** Failing only F4 means the programme would mostly repackage an existing OTH programme. That is
  the project's success measure ("students new to OTH"), so those three stay out.
- **The three levels stay.** Soma asked for this structure, and the reader needs to see what each reading of
  "existing resources" yields. The answer is still one candidate with conditions, so the levels do not avoid a
  recommendation.

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
