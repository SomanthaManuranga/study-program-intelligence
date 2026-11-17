# Independent cross-check: results v1 (provisional until the hand check)

Method: `docs/crosscheck/method.md` (fixed before the code ran). Code: `python -m study_program_intelligence.crosscheck.steps`. Inputs: raw data and the cleaned catalogue only; the funnel's results were not read.

## Funnel in numbers

- Full-time bachelor and master offers in Germany (teacher training removed): 12,069
- Kinds (official subject x level): 663; fit EMI (own subject or >= 25 % co-listed with an EMI subject): 70
- With enough topic data (>= 5 focus items): 64; dropped as relabelled (> 80 % from one EMI programme): 4
- Ranked candidates: BA 33 (eligible: in band and >= 20 new students: 19), MA 27 (eligible: in band and >= 20 new students: 16)

## Matching threshold (calibrated before scoring)

tau = 0.15 (near from 0.105). Mean coverage of subjects EMI already teaches: 72%; of clearly non-EMI subjects: 15%.

## Control: subjects OTH already offers (Step 2 check)

**The control fails.** Subjects OTH already teaches should come out above 80 % from one EMI programme; they range from 10 % to 93 %. Catalogue focus lists are short and generic, so they measure whether EMI touches a topic (topic fit), not how much of a curriculum one programme covers. **Consequence:** the 80 % copy test is NOT decided from catalogue topics. Kinds whose subject an OTH programme of the same level already lists are flagged 'relabel risk' and are tested first with real module handbooks (ECTS level) in the hand-check step. The 'topic fit' column is used only as a relative fit score.

| Kind | Coverage | Max from one EMI programme | Programme | Dropped as relabelled? |
|---|---|---|---|---|
| Vermessungstechnik | MA | 93% | 93% | Geoinformatik und Landmanagement (BA) | yes |
| Informations-, Kommunikationstechnik | BA | 91% | 82% | Elektro- und Informationstechnik (BA) | yes |
| Elektrotechnik | MA | 88% | 81% | Elektro- und Informationstechnik (BA) | yes |
| Elektrotechnik | BA | 89% | 81% | Elektro- und Informationstechnik (BA) | yes |
| Ingenieurinformatik, Computational Engineering | MA | 90% | 76% | Elektro- und Informationstechnik (BA) | no |
| Ingenieurinformatik, Computational Engineering | BA | 82% | 73% | Elektro- und Informationstechnik (BA) | no |
| Datenwissenschaft, Data Science | MA | 87% | 69% | Industrie-4.0-Informatik (BA) | no |
| Informations-, Kommunikationstechnik | MA | 86% | 68% | Elektro- und Informationstechnik (BA) | no |
| Vermessungstechnik | BA | 81% | 66% | Geoinformatik und Landmanagement (BA) | no |
| Medienproduktion | MA | 82% | 59% | Medientechnik und Medienproduktion (MA) | no |
| Technische Informatik | BA | 84% | 56% | Informatik-Studiengang II (BA) | no |
| Druck-, Medientechnik | BA | 68% | 54% | Medienproduktion und Medientechnik (BA) | no |
| Datenwissenschaft, Data Science | BA | 81% | 51% | Industrie-4.0-Informatik (BA) | no |
| Medieninformatik | MA | 64% | 50% | IT und Automation (MA) | no |
| Informatik | BA | 84% | 49% | Informatik-Studiengang II (BA) | no |
| Informatik | MA | 83% | 47% | Industrie-4.0-Informatik (BA) | no |
| Film-, Fernsehproduktion | BA | 66% | 47% | Digital Design (BA) | no |
| Technische Informatik | MA | 73% | 45% | Elektro- und Informationstechnik (BA) | no |
| Kommunikationsdesign, visuelle Kommunikation | MA | 71% | 43% | Digital Design (BA) | no |
| Medieninformatik | BA | 74% | 42% | Medieninformatik (BA) | no |
| Druck-, Medientechnik | MA | 77% | 39% | Medientechnik und Medienproduktion (MA) | no |
| Kommunikationsdesign, visuelle Kommunikation | BA | 53% | 32% | Digital Design (BA) | no |
| Mediendesign, -kunst | BA | 46% | 25% | Digital Design (BA) | no |
| Mediendesign, -kunst | MA | 53% | 22% | Medientechnik und Medienproduktion (MA) | no |
| Film-, Fernsehproduktion | MA | 11% | 11% | Digital Design (BA) | no |
| Medienproduktion | BA | 10% | 10% | Digital Design (BA) | no |

## Ranking bachelor (top 15)

| # | Kind | Score | P(first), eligible only | Topic fit (band) | Relabel risk: OTH programme in same subject | New to OTH / year | Trend German / foreign | Within 150 km | South gap | Jobs 100 km (keyword) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Informatik | 4.20 | 70% | 84% (above 80 %) | Geoinformatik und Landmanagement; Industrie-4.0-Informatik; Medieninformatik; Künstliche Intelligenz; Angewandte Wirtschaftsinformatik | 38 | 2% / 12% | 51 | 0.96 | 685 (informatik) |
| 2 | IT-Sicherheit | 4.15 | 27% | 91% (above 80 %) | - | 36 | 2% / 12% | 2 | 0.66 | 527 (it-sicherheit) |
| 3 | Sensortechnik | 3.95 | 3% | 84% (above 80 %) | - | 57 | -18% / 7% | 1 | 0.71 |  () |
| 4 | Mikrotechnik, Mikrosystemtechnik | 3.80 | 0% | 89% (above 80 %) | - | 58 | -18% / 7% | 1 | 1.06 | 5 (mikrosystemtechnik) |
| 5 | Produktentwicklung | 3.65 | not eligible | 20% (below 40 % (costly)) | - | 55 | 3% / 32% | 0 | 1.49 | 125 (produktentwicklung) |
| 6 | Medien-, Multimediatechnik | 3.60 | 0% | 68% (40-80 %) | - | 46 | -15% / 1% | 2 | 2.58 | 329 (medien) |
| 7 | Automatisierungstechnik | 3.55 | 0% | 81% (above 80 %) | - | 31 | -5% / 3% | 7 | 0.70 | 724 (automatisierungstechnik) |
| 8 | Technische Informatik | 3.55 | 0% | 84% (above 80 %) | - | 26 | -3% / 3% | 5 | 1.24 | 34 (technische informatik) |
| 9 | Datenwissenschaft, Data Science | 3.55 | 0% | 81% (above 80 %) | Digital Technology and Management; Künstliche Intelligenz | 37 | 2% / 12% | 20 | 0.26 | 109 (data science) |
| 10 | Softwaretechnik | 3.50 | 0% | 88% (above 80 %) | - | 34 | 2% / 12% | 3 | 0.78 |  () |
| 11 | Film-, Fernsehproduktion | 3.35 | 0% | 66% (40-80 %) | Digital Design | 33 | 5% / -6% | 0 | none in south | 12 (film) |
| 12 | Technomathematik | 3.25 | 0% | 71% (40-80 %) | - | 49 | -3% / 24% | 3 | 0.95 | 0 (technomathematik) |
| 13 | Kybernetik | 3.25 | not eligible | 85% (above 80 %) | - | 0 |  /  | 2 | 15.00 |  () |
| 14 | Computermathematik | 3.20 | 0% | 50% (40-80 %) | - | 42 | -4% / 5% | 0 | 0.49 |  () |
| 15 | Künstliche Intelligenz | 3.15 | 0% | 65% (40-80 %) | Künstliche Intelligenz | 41 | 2% / 12% | 5 | 0.36 | 67 (künstliche intelligenz) |

## Ranking master (top 15)

| # | Kind | Score | P(first), eligible only | Topic fit (band) | Relabel risk: OTH programme in same subject | New to OTH / year | Trend German / foreign | Within 150 km | South gap | Jobs 100 km (keyword) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | IT-Sicherheit | 4.55 | 97% | 90% (above 80 %) | - | 54 | 7% / 19% | 3 | 0.66 | 527 (it-sicherheit) |
| 2 | Informatik | 4.40 | 3% | 83% (above 80 %) | Applied Research in Engineering Sciences; Künstliche Intelligenz | 59 | 7% / 19% | 43 | 0.90 | 685 (informatik) |
| 3 | Datenwissenschaft, Data Science | 3.80 | 0% | 87% (above 80 %) | Künstliche Intelligenz | 51 | 7% / 19% | 14 | 0.64 | 109 (data science) |
| 4 | Technische Informatik | 3.75 | 0% | 73% (40-80 %) | IT und Automation | 42 | -0% / 21% | 2 | 1.83 | 34 (technische informatik) |
| 5 | Softwaretechnik | 3.55 | 0% | 89% (above 80 %) | - | 51 | 7% / 19% | 5 | 0.59 |  () |
| 6 | Künstliche Intelligenz | 3.55 | 0% | 64% (40-80 %) | Künstliche Intelligenz | 56 | 7% / 19% | 9 | 0.43 | 67 (künstliche intelligenz) |
| 7 | Medien-, Multimediatechnik | 3.50 | 0% | 70% (40-80 %) | International Energy Engineering | 37 | -6% / -6% | 3 | 0.88 | 329 (medien) |
| 8 | Mediendesign, -kunst | 3.40 | 0% | 53% (40-80 %) | - | 35 | 3% / -0% | 3 | 0.76 | 1,175 (kunst) |
| 9 | Informations-, Kommunikationstechnik | 3.25 | not eligible | 86% (above 80 %) | IT und Automation | 9 |  / 3% | 10 | 0.63 | 101 (kommunikationstechnik) |
| 10 | Mensch-Maschine-Interaktion, Interfacedesign | 3.25 | not eligible | 37% (below 40 % (costly)) | - | 71 | 7% / 19% | 2 | 0.94 |  () |
| 11 | Projektmanagement, -ingenieurwesen | 3.20 | not eligible | 60% (40-80 %) | - |  |  /  | 2 |  |  () |
| 12 | Umweltinformatik | 3.15 | 0% | 50% (40-80 %) | - | 67 | 7% / 19% | 0 | 1.88 | 0 (umweltinformatik) |
| 13 | Computermathematik | 3.05 | 0% | 64% (40-80 %) | - | 41 | -3% / 13% | 1 | 0.00 |  () |
| 14 | Mikroelektronik | 2.95 | not eligible | 76% (40-80 %) | - | 0 |  /  | 5 |  |  () |
| 15 | Druck-, Medientechnik | 2.95 | 0% | 77% (40-80 %) | Medientechnik und Medienproduktion | 33 | -6% / -6% | 2 | 0.14 |  () |

## Comparison with the funnel (soma/funnel)

Known before this method was written: only the funnel's headline from its plain-English PDF (general Informatik bachelor passes; cybersecurity bachelor in the band but needs outside teaching). Its tables, candidate lists and AI marks were not read.

| Question | Funnel | This cross-check |
|---|---|---|
| Top bachelor | general Informatik | Informatik first, IT-Sicherheit a close second |
| Cybersecurity | in the band, needs outside teaching (forensics, IT law, auditing) | IT-Sicherheit: no OTH programme in the subject, few competitors within 150 km; first among masters |
| Is Informatik new to OTH? | yes (57 % would come from Medieninformatik, under the 80 % limit) | relabel risk: OTH already runs Industrie-4.0-Informatik and Kuenstliche Intelligenz in the same subject; must be tested with handbooks |
| Candidates checked in depth | 6 | all EMI-fit kinds ranked (33 bachelor, 27 master); handbook test still to do |

## What is still open

- **Hand check**: `data/interim/crosscheck/hand_check_sheet.csv` lists every topic match of the top 15 per level (671 rows). Fill `hand_verdict` with covered / near / new; the ranking is rerun with the hand verdicts.
- Job counts come from the 15 Nov raw replies (keywords of the other analysis); subjects without a matching keyword get a neutral score.
- Scores are relative (quintiles within each level), not absolute grades.
