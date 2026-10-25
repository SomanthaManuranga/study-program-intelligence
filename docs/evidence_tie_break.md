# Evidence: demand tie-break and the two-level answer

Criteria (fixed before building): `docs/criteria_tie_break.md`. Generated tables: `reports/tie_break.md`
(`python -m study_program_intelligence.analysis.tie_break`), `reports/candidates.md`, `reports/ranking.md`.
Hand-check sheet for Soma: `docs/handcheck_sheet.md`. The ranking is not recomputed until Soma's hand check is in.

## Two-level answer

**(a) Existing resources only (primary answer; the supervisor's constraint).** Two candidates pass the feasibility
gate: AR/VR & visual computing and Robotics + AI path B (assistive / service). Their ranking was an open tie that
hangs on one step of the fit rule (`docs/evidence_candidates.md`). **On the demand evidence collected so far the tie is
not broken.** Robotics path B has the larger feeder pool in Destatis; AR/VR has far fewer competitors. These are the
two independent demand signals available for both, and they point in opposite directions. The signals that could
decide it are not in yet: job ads for the AR/VR and service-robotics keywords (from the 1 Nov snapshot) and Google
Trends for the AR/VR terms (Soma's download). A decision rule for them is fixed below, before the data arrive. Both
gate passes also wait for Soma's hand check of the adapted modules.

**(b) With investment (the baseline result).** If EMI could add staff and a lab, the baseline ranking stands:
Cybersecurity B.Sc. first, P(rank 1) 91.7 % (`reports/ranking.md`). What the investment would buy, from the baseline
evidence:

| Item | Cybersecurity B.Sc. (with investment) | Source |
|---|---|---|
| Investment | 2 new professorships, 1 lab engineer, a security lab (cost not estimated) | docs/evidence_fit_staff.md |
| Why it is needed | EMI's modules cover at most about a third of a cyber bachelor's security content (31 %) | docs/evidence_fit_modules.md |
| Student pool | cyber proxy first-years Bavaria +5.9 %/yr 2019-24, but German only +1.9 %/yr | reports/demand_split.md |
| Students | gross first-years 21 / 39 / 75, net new to OTH 15.3 / 32.0 / 64.4 (low / central / high) | docs/evidence_cannibalisation.md |
| Job market | "Cyber Security" 851 ads in Germany, Bavaria 30.9 %, 191 within 100 km | docs/evidence_outlet_jobs.md |
| Competition | 4 dedicated bachelors within 150 km, none within about 80 km (THI 82 km) | configs/scores.yaml (cyber B.Sc. differentiation) |

Against the existing-resources candidates, the investment buys a growing pool (Informatik-led, mostly foreign) and an
anchored intake estimate; it does not buy a larger modelled intake than AR/VR's unanchored estimate (net new central
41.5), and it costs what constraint 1 rules out.

## Side-by-side demand comparison (AR/VR vs robotics path B)

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

## Open risks

- AR/VR's Destatis proxy does not match its competitors' classification; the Destatis signal is weak as a comparison.
- AR/VR job ads and Trends are missing until 1 Nov and Soma's download; "Robotik" is a generic keyword.
- Both gate passes wait for Soma's hand check (`docs/handcheck_sheet.md`); the ranking is recomputed only after it.
- XR headset count unknown (estimate 10-20 for a cohort of about 40).
