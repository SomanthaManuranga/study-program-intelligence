# Evidence: demand tie-break and the two-level answer

Criteria (fixed before building): `docs/criteria_tie_break.md`. Generated tables: `reports/tie_break.md`
(`python -m study_program_intelligence.analysis.tie_break`), `reports/candidates.md`, `reports/ranking.md`.
Hand-check sheet for Soma: `docs/handcheck_sheet.md`. The ranking is not recomputed until Soma's hand check is in.

## Two-level answer

**(a) Existing resources only (primary answer; the supervisor's constraint).** Two candidates pass the feasibility
gate: AR/VR & visual computing and Robotics + AI path B (assistive / service). Their ranking was an open tie that
hangs on one step of the fit rule (`docs/evidence_candidates.md`). On demand alone, **robotics path B is ahead, but
not decisively**: it has the larger and less shrinking student pool, for German and for foreign first-years, and a
measured job market; AR/VR has far fewer competitors. The lean rests on one data source (Destatis), AR/VR's subject
proxy is narrow, and two AR/VR signals are still missing (job ads from 1 Nov, Google Trends after Soma's download), so
the answer is provisional. Both gate passes also wait for Soma's hand check of the adapted modules.

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
AR/VR's closest code is Medieninformatik (visual computing has no Destatis code of its own); Informatik is shown as
the broad pool that visual-computing programmes may also recruit from. Robotics path B uses the baseline feeders
(Mechatronik + Technische Informatik).

| Signal | AR/VR & visual computing | Robotics path B | Favours | Strength |
|---|---|---|---|---|
| Closest series, Bavaria, all, 2019 -> 2024 | Medieninformatik 216 -> 141, -8.2 %/yr | Mechatronik + TI 1,116 -> 1,082, -0.6 %/yr | robotics | medium: Destatis, but AR/VR's code is narrow |
| Same, German first-years, Bavaria | 191 -> 108, -10.8 %/yr | 680 -> 574, -3.3 %/yr | robotics | medium |
| Same, foreign first-years, Bavaria | 25 -> 33, +5.7 %/yr | 436 -> 508, +3.1 %/yr | robotics on level, AR/VR on growth (small base) | medium |
| Same, Germany, all | 2,549 -> 2,094, -3.9 %/yr | 6,121 -> 5,387, -2.5 %/yr | robotics (slightly) | medium |
| Foreign share 2024, Bavaria | 23 % | 47 % | robotics (international demand) | medium |
| Broad pool, Bavaria | Informatik 3,053 -> 4,110, +6.1 %/yr (German +2.3) | Mechatronik 785 -> 762, -0.6 %/yr; TI 331 -> 320, -0.7 %/yr | AR/VR, if it recruits Informatik students | weak: assumption that visual computing draws on Informatik |
| Dedicated competitors (institutions) | 6 in Germany, 1 in Bavaria, 1 within 150 km (Coburg 106 km), 0 within 80 km | 15 in Germany, 6 in Bavaria, 5 within 150 km (nearest THI 82 km), 0 within 80 km | AR/VR | strong: full catalogue |
| Capture model, net new to OTH (low / central / high) | 18.1 / 41.5 / 84.6 | 10.6 / 23.6 / 47.7 | AR/VR | weak: no intake anchor for either; AR/VR's estimate rests on one comparator site and follows from the competitor row, so it is not an independent signal |
| Job ads, matching keywords | no data: "Virtual Reality", "Augmented Reality", "Computergrafik" are counted from the 1 Nov snapshot | "Robotik" 945 in Germany, 289 Bavaria, 162 within 100 km, 58 within 50 km (17 Oct) | no comparison yet | robotics measured, AR/VR missing |
| Search interest (Google Trends) | no data: terms below, manual download | "Robotik Studium" 2.4 % (2019) -> 3.4 % (2026) of "Informatik Studium": flat | no comparison yet | robotics measured, AR/VR missing |
| Language of instruction of competitors | no data: the catalogue has no language field | no data: same | - | - |

**How the tie is decided (E3).** Five rows favour robotics path B (pool size, overall trend, German trend, foreign
level and share, Germany trend); two favour AR/VR (competitors, strong; and the capture model, which follows from the
competitor row); one is weak and conditional (Informatik as a pool); two cannot be compared yet (job ads, Trends).
Dropping any single row leaves robotics path B ahead on demand. But the five robotics rows all come from one source
(Destatis) and partly from one proxy choice: if Medieninformatik understates AR/VR's real pool, they would shrink
together. So the result is "robotics path B leads on demand, moderately", not a clear win.

What would change it: AR/VR job-ad counts at or above "Robotik" in the region; a rising Trends line for the AR/VR terms
against a flat "Robotik Studium"; or evidence that visual-computing first-years are counted under Informatik.

## XR hardware (feasibility side, a limitation)

- OTH's public pages give no headset count. The Digitaler Campus page lists a "Labor VR/AR" (three responsible
  professors); the IKKI page lists an AR-/VR-Labor and a GPU lab with 32 workstations (`data/raw/oth_xr`, manifest
  `docs/oth_xr_manifest.json`). An older Labor Medieninformatik page lists HTC Vive and Microsoft HoloLens without
  quantities. OTH's sitemap has no page of its own for the AR/VR lab.
- Estimate (assumption, not a source): a cohort of about 40 with practicals in two groups of 20 needs 10 headsets at
  two students per headset, 20 at one each; the 32 GPU workstations would cover a group of 20.

## Google Trends: exact terms and settings for the manual download

Same settings as the baseline downloads (`docs/evidence_demand_trends.md`): trends.google.com, "Interest over time",
2004-present (monthly), all categories, web search; download the CSV. Save under `data/raw/trends/` with the names
below (they do not start with `trends_`, so the baseline Trends step is not affected).

| File | Region | Terms (one comparison, max 5) |
|---|---|---|
| tiebreak_DE_anchored.csv | Germany | Informatik Studium; Robotik Studium; Medieninformatik Studium; Virtual Reality Studium; Visual Computing Studium |
| tiebreak_BY_anchored.csv | Bavaria (Bayern) | the same five terms |
| tiebreak_DE_specialist.csv | Germany | Robotik Studium; Servicerobotik; Medieninformatik Studium; Virtual Reality Studium; Computervisualistik Studium |

The anchored downloads give each term's share of "Informatik Studium" (the baseline's robust metric); the specialist
download, without the large anchor, gives the small terms more resolution.

## Job-ad keywords for the 1 Nov snapshot

`configs/jobsuche.yaml` contains, besides the baseline "Robotik": "Servicerobotik" (robotics), "Virtual Reality",
"Augmented Reality", "Computergrafik" (AR/VR). They are counted for Germany, Bavaria, 50 km and 100 km around Amberg
from the 1 Nov snapshot on.

## Opposing view (fresh-context reviewer, E4)

To be filled in by the reviewer.

## Open risks

- The demand lean rests on Destatis and on the choice of Medieninformatik as AR/VR's proxy.
- AR/VR job ads and Trends are missing until 1 Nov and Soma's download.
- Both gate passes wait for Soma's hand check (`docs/handcheck_sheet.md`); the ranking is recomputed only after it.
- XR headset count unknown (estimate 10-20 for a cohort of about 40).
