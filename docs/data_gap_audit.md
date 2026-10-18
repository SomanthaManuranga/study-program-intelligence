# Data-sufficiency audit (before the 4 Dec freeze)

Scope: is the data enough for each claim, and which additional public data is worth collecting before the freeze?
This audit does not re-evaluate the methods; that stays locked for Phase 5. Nothing was collected for the analysis.
Candidate sources were only checked: robots.txt, licence, and whether the needed table really exists. Copies made for
those checks sit in a scratch folder, not in data/.

## Verdict

1. **The recommendation is not data-limited; the intake range is.** The ranking is robust in every sensitivity run,
   and no gap below is likely to change which option comes first. The 21-75 intake range rests on two weak anchors.
   No public source we found publishes the real first-year numbers of the competing cyber programmes. The range cannot
   be narrowed much with public data before 4 Dec.
2. **One new finding, from data we already hold:** the growth of our demand proxy comes mostly from foreign students.
   In Bavaria, first-years in the proxy subjects (Informatik, Computer- und Kommunikationstechniken,
   Ingenieurinformatik/Technische Informatik) grew from 3,705 (2019) to 4,936 (2024), +5.9 % a year. German first-years
   grew from 2,506 to 2,748 (+1.9 % a year). Foreign first-years grew from 1,199 to 2,188 (+12.8 % a year) and are now
   44 % of the proxy. In Germany, German first-years in Informatik fell slightly (13,274 in 2019, 13,146 in 2024).
   Source: Destatis 21311-0012 (Germany) and 21311-0015 (Bavaria), already cached in data/raw/destatis/.
   A German-language bachelor at OTH recruits mainly German school leavers, so "demand grows" holds, but much more
   weakly than the 6.1 % headline suggests.
3. **Worth collecting or computing before the freeze:** four items, three of them from data already in hand (priority
   list at the end).

## 1. Data per claim: what we used, weaknesses, what is missing

| Claim | Data used | Weaknesses | Missing |
|---|---|---|---|
| Candidate selection (funnel) | BA Studiensuche catalogue (4,840 offers, 13 study fields); Destatis 21311 first-years for 11 EMI-related subjects; title keyword rules (9 theme groups) | 4 of the 15 theme rules checked by hand; automation, energy and medtech/health dropped as "already at OTH" without a written verdict; 5 themes in the code (software engineering, sustainability, mobility, quantum, aerospace) never got a stage-1 verdict | a written verdict for every theme group, using the same two filters |
| A Demand | Destatis first-years by subject (Germany, Bavaria, 2005-2025); KMK forecasts; Google Trends; job-ad keywords | cyber is not a statistical subject, so the proxy is the wider Informatik field; the proxy mixes German and foreign entrants and bachelor and master entrants (see Verdict 2); Trends is relative and flat since 2022 | proxy split by nationality (in hand); split by degree level (Bavaria, one year: report table 3.2, in hand) |
| B Capture | LfStat flows by Regierungsbezirk to 17 state HAWs (Tabelle 5); school leavers by county; THI capacity 25 (module handbook); Deggendorf "about 60" (one student review) | no measured intake for any competing cyber programme; Bavarian origins only (students from other states missing); Bezirk-level flows | measured first-years of the THI and TH Deggendorf cyber bachelors; share of students from outside Bavaria (in hand: report tables 4 and 8) |
| C Fit | module handbooks (7 competitors, all EMI programmes); hand check of 20 module pairs; staffing rules (§ 4 AVBayHIG) | module texts, not real teaching; staff research profiles not read (blocked); lab cost not estimated | lab cost benchmark; nothing public found that would change the fit score |
| D Outlet | BA job board (2 snapshots, 3 more scheduled); BA shortage analysis; Bavarian employment by IT occupation | keyword counts, not vacancies by occupation; no salary data; no county-level occupation data | salaries (BA Entgeltatlas); the scheduled snapshots |
| Cannibalisation | capture model with and without the new programme | model sees only OTH programmes with a security focus; OTH programme intakes are not published | OTH first-years per programme (not public; OTH /fileadmin/ is excluded by robots.txt) |
| Ranking | scores from all claims; 10,000 what-if scenarios | robotics has no intake anchor; robotics fit is title-level only | a published robotics intake or capacity (none found; THI robotics handbook unreachable) |

## 2. Candidate sources checked

| Source | Gap it would fill | Exists? | Allowed? | Result |
|---|---|---|---|---|
| THI published statistics | capture anchor | no per-programme statistics page found; the cyber bachelor is admission-free, so it is not in THI's admission-quota statute; the 2024 statute URL is gone (404) | robots.txt blocks only /suche | not available; capacity 25 (module handbook) remains the only figure |
| TH Deggendorf "Zahlen, Daten, Fakten" | capture anchor | yes, yearly PDFs up to Dec 2022 on th-deg.de; no newer edition found | robots.txt blocks only login/admin | **students per faculty only** (Angewandte Informatik: 1,098 students over 7 bachelors and 5 masters, Dec 2022); no programme split; not usable as an anchor |
| FAU | capture anchor | admission-quota statute exists (caps, not intakes) | allowed | FAU's cyber bachelor is part-time online, not a full-time competitor; not needed |
| THWS, HNU | capture anchors | no per-programme statistics found | THWS: /fileadmin/ disallowed; HNU: no restrictions | not available |
| OTH "Zahlen und Fakten" | cannibalisation base | no current per-programme figures found | OTH /fileadmin/ disallowed for scripts | manual check by Soma only |
| Destatis GENESIS 21311 | intakes per programme | catalogue checked: tables per university (21311-0011) or per subject (-0012, -0015), never both | allowed via API (token) | no official programme-level or university-by-subject first-years |
| Bavarian GENESIS (statistikdaten.bayern.de) | same | first-years by university and subject group only (21311-106s/107s) | robots.txt disallows /genesis/online/ for all crawlers (one listing page was opened before this was checked; nothing stored) | too coarse (subject group, not subject); manual only |
| LfStat report "Studierende an den Hochschulen in Bayern" | out-of-state students; degree level | in hand: Tabelle 4 and 8 (German students by state of entrance qualification per university), Tabelle 3.2 (subjects by university type) | public PDF, already registered | **use**: closes the "Bavaria-only" gap with a measured share |
| Other universities' per-programme statistics | national benchmark for cyber intakes | yes for some universities: Ruhr-Uni Bochum (IT-Sicherheit/Informationstechnik, 202 first-semester students in 2024 over all degree levels); Saarland University (Cybersicherheit B.Sc., 42 first-semester students in WS 2025/26) | Bochum: allowed; Saarland: rules only for one named bot, so allowed | **exists**, but both are research universities with large security institutes, not HAW peers; a plausibility check, not an anchor |
| Accreditation reports | intake history of competitors | database at antrag.akkreditierungsrat.de; some HAWs host reports (HAW Kiel cyber bachelor: capacity 30, not started yet) | **akkreditierungsrat.de disallows all crawlers** | manual only; expected yield low (new programmes have no intake history) |
| Ministry contracts 2023-2027 (OTH, THI, TH Deggendorf) | capacity plans; is OTH already planning cyber? | yes, public PDFs on wissenschaftkunst.bayern.de | allowed (/download) | no programme-level capacity or intake; THI plans professorships "especially in AI and cybersecurity"; OTH's contract has no cyber programme, only internal IT security; context only |
| International students: Destatis | demand proxy split | **in hand** (nationality x subject, Germany and Bavaria) | already used | **use** (Verdict 2) |
| International students: DAAD Wissenschaft weltoffen | degree-level split of foreign entrants | yes; figures as XLSX downloads, mostly at subject-group level | robots.txt has no rules; site states no licence (the 2021 publication is CC BY-SA 4.0) | not needed if report table 3.2 suffices |
| BA Entgeltatlas | graduate salaries | yes; API on rest.arbeitsagentur.de (same host and published-key model as our Studiensuche and Jobsuche clients); filters for occupation code, level (expert), region (Bavaria) | web robots.txt allows all; no licence stated, as for our other BA APIs | available; the IT-security occupation code is to be confirmed |
| Broader candidate check | candidate selection | **in hand**: programmes.csv and Destatis subjects | already used | **use** (see below) |

**Broader candidates, first trend look (data in hand).** First-years in Germany, 2019 to 2025, per year:

- Medizinische Informatik: -0.8 %.
- Wirtschaftsinformatik: +1.2 %.
- Computer- und Kommunikationstechniken: +2.5 %.
- Gesundheitswissenschaften: -1.3 %.
- Medientechnik: -8.6 %.
- Elektronische Energietechnik: -14.1 %.
- Statistik/data: a new subject code, with too short a series.

In every one of them the growth comes from foreign students. None grows faster than Informatik, so the broader check is
unlikely to produce a new finalist. Its value is that every theme would get a written verdict.

## 3. Gaps rated

Value of information (VoI): could the data change the recommendation, or narrow the 21-75 intake range?

| # | Gap | Change the recommendation? | Narrow 21-75? | Effort | Risk | Verdict |
|---|---|---|---|---|---|---|
| G1 | Demand proxy by nationality (and degree level) | unlikely: cyber stays first even with demand left out (lowest share 67.2 %); but it weakens the headline demand claim | no (intake uses anchors) | low, data in hand (half a day) | low | **collect before freeze** |
| G2 | Measured first-years of THI and TH Deggendorf cyber bachelors | no | **yes, the only item that would** (about half the width) | no public source exists | - | **limitation**; a direct request or a paid custom tabulation from LfStat is not public data (decision D2) |
| G3 | National benchmark of cyber intakes from universities that publish per-programme statistics | no | slightly: checks whether "about 60" is plausible | medium (time-box 1 day; expect 3-8 programmes, few at HAWs) | medium: research universities are not HAW peers; only those who publish are visible | **optional, time-boxed**; needs decision D1 |
| G4 | Students from outside Bavaria | no | slightly: measures the known downward bias | low, data in hand | low | **collect before freeze** |
| G5 | Broader candidate check through the same funnel filters | very unlikely (trend look above) | no | low to medium (1 day, data in hand) | low | **collect before freeze**: it closes the "no written verdict" gap |
| G6 | Robotics intake anchor | no (robotics last in 72.2 % of scenarios) | no | no public source found | - | **limitation** |
| G7 | Salaries (Entgeltatlas) | no | no | low | low | **optional**; adds colour to the outlet claim only |
| G8 | Lab cost | no (feasibility weight .15; the ranking holds without it) | no | medium, no reliable public benchmark found | high (not comparable) | **limitation** |
| G9 | OTH first-years per programme | no | no | manual check by Soma | low | **limitation** unless OTH publishes them |
| G10 | Staff research profiles | no | no | blocked | - | **limitation** (unchanged) |
| G11 | Accreditation reports | no | maybe, if one has intake history | manual (robots) | low yield | **optional manual check**, 30 minutes |
| G12 | Job-ad snapshots | no | no | scheduled | low | **already planned** (1 Nov, 15 Nov, 1 Dec) |

## Priority list before 4 Dec

1. **G1: split the demand proxy by nationality** (and by degree level for one year). This is the most important gap,
   because it changes how strong the headline demand claim is. Report it as an added fact and a sensitivity; whether
   the proxy itself changes is a method question for Phase 5 (decision D3).
2. **G5: broader candidate check.** A written verdict for every theme group, using the two existing filters (trend,
   supply near OTH), including data science, medical/health informatics, energy informatics, games/media and the five
   themes that were never screened.
3. **G4: share of students from outside Bavaria** for OTH and the cyber competitors (LfStat Tabelle 4 and 8). It
   puts a number on the known downward bias of the capture model.
4. **G3 (optional, after D1): a time-boxed national benchmark** of published cyber programme intakes, as a
   plausibility check on the "about 60" figure only, not as a new anchor.

State as limitations instead: G2, G6, G8, G9, G10 (and G7 and G11 if not done).

## Decisions for Soma

- **D1:** CLAUDE.md says "no intake or admission figures from universities". Does that cover figures that other
  universities publish themselves (G3, e.g. Bochum, Saarland)? My reading: published figures are public data and
  allowed; only figures obtained by request are excluded.
- **D2:** a direct request to THI / TH Deggendorf, or a paid custom tabulation from LfStat, is the only way to narrow
  the intake range. It is not public data, so it is outside the project's rules. The report already recommends it as
  OTH's first step. Keep it that way?
- **D3:** G1 touches the demand proxy. Proposal: before the freeze, add the split as a fact and a sensitivity in the
  demand evidence and the limitations, and leave the proxy definition as it is; any redefinition goes to Phase 5.
