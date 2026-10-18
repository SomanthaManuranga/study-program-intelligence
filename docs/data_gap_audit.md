# Data-sufficiency audit (before the 4 Dec freeze)

Scope: is the data enough for each claim, and which additional public data is worth collecting before the freeze?
This audit does not re-evaluate the methods; that stays locked for Phase 5. Nothing was collected for the analysis.
Candidate sources were only checked: robots.txt, licence, and whether the needed table really exists. Copies made for
those checks sit in a scratch folder, not in data/.

## 1. Key finding: the demand growth is mostly international students

Source: Destatis 21311-0012 (Germany) and 21311-0015 (Bavaria), first-years (1st university semester, winter
semester), German and foreign nationality. Already cached in data/raw/destatis/. Cyber proxy = Informatik +
Ingenieurinformatik/Technische Informatik + Computer- und Kommunikationstechniken (as in the forecast).

| Series | 2019: German / foreign | 2024: German / foreign | Growth a year 2019-24: all / German / foreign | Foreign part of the 2019-24 growth | Foreign share 2019 / 2024 / 2025 |
|---|---|---|---|---|---|
| Informatik, Germany | 13,274 / 5,312 | 13,146 / 8,937 | +3.5 % / -0.2 % / +11.0 % | all of it (German entrants fell by 128) | 29 % / 40 % / 46 % |
| Cyber proxy, Germany | 15,607 / 6,409 | 15,214 / 10,648 | +3.3 % / -0.5 % / +10.7 % | all of it (German entrants fell by 393) | 29 % / 41 % / 46 % |
| Informatik, Bavaria | 2,019 / 1,034 | 2,257 / 1,853 | **+6.1 %** / +2.3 % / +12.4 % | 77 % (+819 of +1,057) | 34 % / 45 % / 54 % |
| Cyber proxy, Bavaria | 2,506 / 1,199 | 2,748 / 2,188 | +5.9 % / +1.9 % / +12.8 % | 80 % (+989 of +1,231) | 32 % / 44 % / 52 % |

By university type (Bavaria, WS 2024/25, study area Informatik, 1st university semester; LfStat report, Tabelle 3.2,
in hand): universities of applied sciences 2,359 German / 1,457 foreign (38 % foreign); universities 1,640 / 1,344
(45 % foreign).

Caveats:

- "Foreign" means foreign nationality. It includes foreigners who went to school in Germany. No table we hold splits by
  where the school-leaving certificate was gained at subject level.
- First-years in their 1st university semester include international master students starting their first semester
  in Germany. Degree level is not available at subject level in any table we hold.
- 2025 is the Bavarian G9 gap year for German school leavers, so 2025 shares overstate the trend.

**What it means for Claim A (demand):**

- The headline "+6.1 % a year in Bavaria" is true for all first-years. For German first-years, who are the main target
  group of a German-language bachelor, it is +2.3 % in Bavaria and -0.2 % in Germany.
- The relative claim survives. Among German first-years, Informatik is still the strongest large EMI subject. In
  Bavaria it is the only large one that grew: Informatik +2.3 %, Wirtschaftsinformatik -3.1 %, Elektrotechnik -5.0 %,
  Mechatronik -3.5 % a year. In Germany it fell least: Informatik -0.2 %, Wirtschaftsinformatik -0.4 %,
  Elektrotechnik -5.5 %, Mechatronik -5.9 %.
- The forecast's central planning value (5,538 for Bavaria in 2030) continues a trend that is mostly international.
  For the German target group the careful (KMK) path is the more relevant one.
- The capture estimate (21 / 39 / 75) is not affected. It is anchored on competitors' intakes, which already contain
  whatever share of foreign students they have.
- Effect on the ranking: the demand trend score of the cyber options (central 4) rests on "related-field entrants rose
  over five years". In Bavaria that still holds for German entrants, but more weakly; in Germany it does not. A
  sensitivity with a lower trend score is bounded by an existing result: with demand left out completely, the cyber
  bachelor still comes first in 67.2 % of the scenarios.

**An English-taught programme: assessment.**

- **For:**
  - International first-years in Informatik grow by about 11 % a year and are now close to half of all first-years.
  - OTH's own ministry contract credits new English-taught bachelors with a clear rise in international students
    (quote in Section 4).
  - TH Deggendorf runs English-taught programmes in all faculties.
- **Against:**
  - The only cyber data point we have is negative. At Saarland University, the English-taught Cybersecurity B.Sc. had 3
    first-semester students in WS 2025/26, against 42 in the German-taught Cybersicherheit B.Sc.
  - Much of the international growth is probably master entrants, but we cannot measure it at subject level.
  - Our capture model covers Bavarian school leavers only. It cannot estimate international applicants, so an
    English-taught variant would have no intake estimate at all.
  - The regional employers' need for German-speaking graduates is not measured.
- **Verdict:**
  - Not supported as the main variant with the data we have.
  - Better fits: English electives within the German bachelor, or the English-taught cyber master later (the report's
    proposal (a)), because international demand concentrates at master level.
  - State it in the report as an option and a limitation, not as a recommendation.

## 2. Data per claim: what we used, weaknesses, what is missing

| Claim | Data used | Weaknesses | Missing |
|---|---|---|---|
| Candidate selection (funnel) | BA Studiensuche catalogue (4,840 offers, 13 study fields); Destatis 21311 first-years for 11 EMI-related subjects; title keyword rules (9 theme groups) | 4 of the 15 theme rules checked by hand; automation, energy and medtech/health dropped as "already at OTH" without a written verdict; 5 themes in the code (software engineering, sustainability, mobility, quantum, aerospace) never got a stage-1 verdict; feeder trends not split by nationality | a written verdict for every theme group, using the same two filters |
| A Demand | Destatis first-years by subject (Germany, Bavaria, 2005-2025); KMK forecasts; Google Trends; job-ad keywords | cyber is not a statistical subject, so the proxy is the wider Informatik field; the proxy's growth is mostly foreign entrants (Section 1); degree level unknown at subject level; Trends is relative and flat since 2022 | the nationality split in the evidence and report (in hand) |
| B Capture | LfStat flows by Regierungsbezirk to 17 state HAWs (Tabelle 5); school leavers by county; THI capacity 25 (module handbook); Deggendorf "about 60" (one student review) | no measured intake for any competing cyber programme; Bavarian origins only (students from other states missing); Bezirk-level flows | measured first-years of the THI and TH Deggendorf cyber bachelors; share of students from outside Bavaria (in hand: report Tabelle 4 and 8) |
| C Fit | module handbooks (7 competitors, all EMI programmes); hand check of 20 module pairs; staffing rules (§ 4 AVBayHIG) | module texts, not real teaching; staff research profiles not read (blocked); lab cost not estimated | lab cost benchmark; nothing public found that would change the fit score |
| D Outlet | BA job board (2 snapshots, 3 more scheduled); BA shortage analysis; Bavarian employment by IT occupation | keyword counts, not vacancies by occupation; no salary data; no county-level occupation data | salaries (BA Entgeltatlas); the scheduled snapshots |
| Cannibalisation | capture model with and without the new programme | model sees only OTH programmes with a security focus; OTH programme intakes are not published | OTH first-years per programme (not public; OTH /fileadmin/ is excluded by robots.txt) |
| Ranking | scores from all claims; 10,000 what-if scenarios | robotics has no intake anchor; robotics fit is title-level only; demand trend score does not reflect the nationality split | a published robotics intake or capacity (none found); a trend-score sensitivity (Section 1) |

## 3. Candidate sources checked

| Source | Gap it would fill | Exists? | Allowed? | Result |
|---|---|---|---|---|
| THI published statistics | capture anchor | no per-programme statistics page found; the cyber bachelor is admission-free, so it is not in THI's admission-quota statute; the 2024 statute URL is gone (404) | robots.txt blocks only /suche | not available; capacity 25 (module handbook) remains the only figure |
| TH Deggendorf "Zahlen, Daten, Fakten" | capture anchor | yes, yearly PDFs up to Dec 2022 on th-deg.de; no newer edition found | robots.txt blocks only login/admin | **students per faculty only** (Angewandte Informatik: 1,098 students over 7 bachelors and 5 masters, Dec 2022); not usable as an anchor |
| FAU | capture anchor | admission-quota statute exists (caps, not intakes) | allowed | FAU's cyber bachelor is part-time online, not a full-time competitor; not needed |
| THWS, HNU | capture anchors | no per-programme statistics found | THWS: /fileadmin/ disallowed; HNU: no restrictions | not available |
| OTH "Zahlen und Fakten" | cannibalisation base | no current per-programme figures found | OTH /fileadmin/ disallowed for scripts | manual check by Soma only |
| Destatis GENESIS 21311 | intakes per programme | catalogue checked: tables per university (21311-0011) or per subject (-0012, -0015), never both | allowed via API (token) | no official programme-level or university-by-subject first-years |
| Bavarian GENESIS (statistikdaten.bayern.de) | same | not checked | robots.txt disallows /genesis/online/ for all crawlers; one page there was fetched before the robots check caught it; it is not used (decision log) | manual check by Soma only; the published LfStat report gives first-years per university only by subject group (Tabelle 3.1) |
| LfStat report "Studierende an den Hochschulen in Bayern" | out-of-state students; university type | in hand: Tabelle 4 and 8 (German students by state of entrance qualification per university), Tabelle 3.2 (study areas by university type and nationality) | public PDF, already registered | **use** |
| Other universities' per-programme statistics | national benchmark for cyber intakes | yes for some universities: Ruhr-Uni Bochum (IT-Sicherheit/Informationstechnik, 202 first-semester students in 2024 over all degree levels); Saarland University (Cybersicherheit B.Sc. 42, Cybersecurity B.Sc. in English 3 first-semester students, WS 2025/26) | Bochum: allowed; Saarland: rules only for one named bot, so allowed | **exists**, but both are research universities with large security institutes, not HAW peers; a plausibility check, not an anchor |
| Accreditation reports | intake history of competitors | database at antrag.akkreditierungsrat.de; some HAWs host reports (HAW Kiel cyber bachelor: capacity 30, not started yet) | **akkreditierungsrat.de disallows all crawlers** | manual only; TH Deggendorf is system-accredited and accredits its programmes itself (contract, Section 4), so its cyber bachelor has no report there; yield very low |
| Ministry contracts 2023-2027 (OTH, THI, TH Deggendorf) | capacity plans; is OTH already planning cyber? | yes, public PDFs on wissenschaftkunst.bayern.de | allowed (/download) | no programme-level capacity, intake or planned degree programme (quotes in Section 4) |
| International students: Destatis | demand proxy split | **in hand** (nationality x subject, Germany and Bavaria) | already used | **use** (Section 1) |
| International students: DAAD Wissenschaft weltoffen | degree-level split of foreign entrants | yes; figures as XLSX downloads, mostly at subject-group level | robots.txt has no rules; site states no licence (the 2021 publication is CC BY-SA 4.0) | not needed: subject-group level only |
| BA Entgeltatlas | graduate salaries | yes; API on rest.arbeitsagentur.de (same host and published-key model as our Studiensuche and Jobsuche clients); filters for occupation code, level (expert), region (Bavaria) | web robots.txt allows all; no licence stated, as for our other BA APIs | available; the IT-security occupation code is to be confirmed |
| Broader candidate check | candidate selection | **in hand**: programmes.csv and Destatis subjects | already used | **use** |

**Broader candidates, first trend look (data in hand).** First-years in Germany, per year from 2019 to 2025:

- Medizinische Informatik: -0.8 %.
- Wirtschaftsinformatik: +1.2 %.
- Computer- und Kommunikationstechniken: +2.5 %.
- Gesundheitswissenschaften: -1.3 %.
- Medientechnik: -8.6 %.
- Elektronische Energietechnik: -14.1 %.
- Statistik/data: a new subject code, with too short a series.

The growth in each of them comes from foreign students. None grows faster than Informatik, for all students or for
German students. The broader check is unlikely to produce a new finalist; its value is a written verdict for every
theme.

## 4. Ministry contracts 2023-2027: exact wording

Quoted from the Hochschulverträge 2023-2027 published by the Bavarian ministry (wissenschaftkunst.bayern.de/download/
22334_OTH-Amberg-Weiden.pdf, 22339_TH-Deggendorf.pdf, 22341_TH-Ingolstadt.pdf). Page = PDF page. The words are verbatim;
line-break hyphens and spacing errors from the PDF text layer are removed. English summaries are mine.

**OTH Amberg-Weiden**

| Topic | Exact wording | Page | In plain English |
|---|---|---|---|
| New programmes (continuing education only) | "Das Studienspektrum umfasst derzeit einen berufsbegleitenden Bachelorstudiengang sowie sieben weiterbildende Masterstudiengänge mit den Schwerpunkten Digitalisierung, Management und Recht. Ein Fokus der nächsten Jahre wird in der Weiterentwicklung von weiterbildenden Studienangeboten in den Bereichen Technik, Gesundheit, Nachhaltigkeit und Internationalisierung liegen." | 6 | planned development is in continuing education, not in full-time degree programmes |
| Target for programmes | "Verstetigung von mindestens einem berufsbegleitenden Bachelor-Studiengang (aktuell einer vorhanden) und von 8 weiterbildenden Master-Studiengängen (aktuell 7 vorhanden) bis 2027" | 7 | the only programme target: keep 1 part-time bachelor, go from 7 to 8 continuing-education masters |
| Hightech Agenda | "Über die vom Freistaat Bayern – vorbehaltlich der Mittelbereitstellung durch den Haushaltsgesetzgeber – in den Jahren 2023 bis 2027 in den lehrrelevanten Teilprojekten der HTA zur Verfügung gestellten Stellen und Mittel wird die Hochschule insbesondere die Attraktivität der Studienangebote in diesen Zukunftsbereichen steigern, indem u.a. neueste Erkenntnisse und Entwicklungen in das Studium integriert werden." | 5 | Hightech Agenda posts improve existing programmes; no new programme named (same wording in the Deggendorf contract) |
| Research profile | "Die OTH Amberg-Weiden hat in Forschung und Entwicklung zentrale Profilfelder herausgebildet: Informations- und Kommunikationstechnik, Industrie 4.0, Energie- und Ressourceneffizienz, Nachhaltigkeit, Produktion und Logistik, Medizintechnik und Gesundheitswirtschaft, E-Commerce, Medien und Pädagogik sowie übergreifend Digitalisierung, IT-Security und Künstliche Intelligenz." | 8 | IT security is named as a cross-cutting research field, which supports institutional fit |
| English-taught programmes | "Mit der Einführung internationaler, englischsprachiger Studiengänge hat sich die Zahl der internationalen Studierenden deutlich gesteigert, insbesondere durch neue, grundständige englischsprachige Studiengänge steigerte die OTH Amberg-Weiden ihre Attraktivität für Studierende aus dem Ausland." | 16-17 | new English-taught bachelor programmes raised international numbers (no figures given) |
| Digitalisation and IT security | "Neben der Nutzung der Vorteile der Digitalen Transformation gilt es, die IT-Sicherheit zu beachten und diese kontinuierlich zu adaptieren und zu optimieren." | 20 | IT security of the university itself |
| IT security goal | "8.2 Stärkung der IT-Sicherheit Etablierung eines Informationssicherheitsmanagementsystems (ISMS)" | 21 | internal security management system, not teaching |
| IT security measure | "Weitere Stärkung der etablierten IT-Sicherheit zur Absicherung der IT-Prozesse nach innen und außen" ... "Die Finanzierung erfolgt aus dem Strategiefonds mit einem Mitteleinsatz in Höhe von rund € 112.250/Jahr." | 25 | internal IT operations (endpoint security, 2FA, vulnerability scans, ISMS) |

**TH Deggendorf**

| Topic | Exact wording | Page | In plain English |
|---|---|---|---|
| Strategy | "Digitalisierung: Das Zentrum für Digitalisierungstechnologien ist unsere Vision für die digitale Transformation der Bayerischen Wirtschaft." | 2 | digitalisation is THD's first strategic goal |
| Accreditation | "Als systemakkreditierte Hochschule akkreditiert die THD ihr Studienangebot selbstständig." | 6 | THD accredits its own programmes, so no external accreditation reports for its cyber bachelor |
| English-taught programmes | "Durch die konsequent englischsprachigen Studienprogramme in allen Fakultäten (natürlich insbesondere an den internationalen Standorten Pfarrkirchen und Cham), eröffnet sich für diesen Bewerberinnen- und Bewerberkreis ein attraktives Feld." | 17 | English-taught programmes in all faculties (said about recruiting women professors) |
| Digitalisation | "Die THD hat sich durch die Gründung des Zentrums für Digitalisierungstechnologien und dem durch die letzten Zielvereinbarungen angestoßenen und jetzt nachhaltig weitergeführten Aufbau eines Impulszentrums für Digitale Entwicklung der Region zu einem der führenden Zentren für Ausbildung und Transfer in Digitalisierungsthemen entwickelt." | 22 | THD positions itself as a leading centre for digital education and transfer |
| IT security | "Zur Stärkung der IT-Sicherheit wurde das Technologietransferzentrum Vilshofen (Bayerischen Zentrum für Digitale Sicherheit) gegründet. Das Zentrum wirkt bereits jetzt sehr erfolgreich in der Region und unterstützt bayerische Firmen auf allen Ebenen bei Themen der IT-Sicherheit." | 23 | THD runs a dedicated IT-security transfer centre: a strong regional competitor in security |
| IT security goal | "8.2 Stärkung der IT-Sicherheit Etablierung eines Informationssicherheitsmanagementsystems (ISMS)" | 23 | internal, as at OTH |

**TH Ingolstadt** (one passage only): "... hat aber in den Berufungsgebieten der Informatik, speziell im Bereich KI und
Cybersicherheit, massive Probleme weibliche Bewerbungen zu generieren." (PDF p. 12). THI recruits professors in AI and
cybersecurity and finds it hard to attract women applicants. It says nothing about programmes or capacity.

**Reading:**

- Neither the OTH nor the Deggendorf contract names a planned full-time degree programme, a capacity or an intake.
- OTH's contract names IT security as a cross-cutting research field (supports fit). All other mentions of IT
  security concern the universities' own IT operations.
- TH Deggendorf's security transfer centre makes it a stronger regional competitor in security than the module
  comparison alone shows.

## 5. Gaps rated

Value of information (VoI): could the data change the recommendation, or narrow the 21-75 intake range?

| # | Gap | Change the recommendation? | Narrow 21-75? | Effort | Risk | Verdict |
|---|---|---|---|---|---|---|
| G1 | Demand proxy by nationality | unlikely (cyber first in 67.2 % even with demand left out); weakens the headline demand claim | no | low, data in hand | low | **collect** |
| G2 | Measured first-years of THI and TH Deggendorf cyber bachelors | no | **yes, the only item that would** | no public source exists | - | **limitation** (D2) |
| G3 | National benchmark of published cyber intakes | no | slightly: plausibility of "about 60" | medium, time-box 1 day | medium: research universities are not HAW peers | **collect, time-boxed** |
| G4 | Students from outside Bavaria | no | slightly: measures the known downward bias | low, data in hand | low | **collect** |
| G5 | Broader candidate check | very unlikely | no | low to medium, data in hand | low | **collect** |
| G6 | Robotics intake anchor | no | no | no public source | - | **limitation** |
| G7 | Salaries (Entgeltatlas) | no | no | low | low | optional |
| G8 | Lab cost | no | no | medium, no reliable public benchmark | high | **limitation** |
| G9 | OTH first-years per programme | no | no | manual check by Soma | low | **limitation** |
| G10 | Staff research profiles | no | no | blocked | - | **limitation** |
| G11 | Accreditation reports | no | very unlikely (Deggendorf self-accredits) | manual (robots) | - | **drop** |
| G12 | Job-ad snapshots | no | no | scheduled | low | already planned |
| G13 | English-taught variant | no (as a variant, not the main option) | no | no intake model possible | - | **limitation and option** in the report |

## 6. Priority list

**Collect before the 4 Dec freeze:**

| # | Item | Changes which claim | Effort |
|---|---|---|---|
| 1 | G1: German / foreign split of the demand proxy, plus a trend-score sensitivity | **Claim A** wording (growth is mostly international); demand trend score and ranking sensitivity; report demand section and limitations; summary section 6.1 | half a day |
| 2 | G5: written verdict for every theme group (same two filters, shown for all and for German first-years) | **candidate selection** (funnel); closes the "no written verdict" gap | 1 day |
| 3 | G4: share of students from outside Bavaria (OTH and cyber competitors) | **Claim B** limitation becomes a number; the range itself stays | half a day |
| 4 | G3: time-boxed benchmark of published cyber intakes | **Claim B** plausibility of the high anchor only; not a new anchor | 1 day maximum |

**Stays a limitation:** G2 (real competitor intakes), G6 (robotics anchor), G8 (lab cost), G9 (OTH programme
intakes), G10 (staff profiles), G13 (English-taught variant: option, no intake estimate). G7 is optional, G11 dropped.

## Decisions (approved)

- **D1:** figures that universities publish themselves count as public data and are allowed; figures obtained by
  request are not.
- **D2:** a direct request to THI / TH Deggendorf, or a paid custom tabulation from LfStat, stays a recommendation
  for OTH, not something the project does.
- **D3:** the nationality split is added as a fact and a sensitivity in the demand evidence and the limitations; the
  proxy definition is unchanged; any redefinition goes to Phase 5.
