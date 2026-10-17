# Decision log

## 2026-10-14: Faculty

Decision: Elektrotechnik, Medien und Informatik (EMI).
Reason: specified in the project brief.
Decided by: team.

## 2026-10-14: Degree levels

Decision: bachelor and master, analysed separately, then compared.
Reason: the project brief asks for both.
Decided by: team.

## 2026-10-14: Data sources

Decision: publicly available sources only. No primary survey and no internal OTH data.
Reason: the project brief specifies publicly available data.
Consequence: capture is estimated from public data and stated as a limitation.
Decided by: team.

## 2026-10-14: Geography

Decision: all of Germany for demand and competition; capture estimated regionally for bachelor and nationally for master.
Reason: national data shows whether the field is growing; capture depends on location, because most bachelor students choose a university near home.
Decided by: team.

## 2026-10-14: GENESIS scope

Decision: download 11 GENESIS tables for 2005 to 2025 (winter semesters / examination years); state-by-subject tables for Bavaria only, national figures from Germany-level tables.
Reason: token logins cannot start background jobs; Bavaria plus Germany covers the regional and national views.
Consequence: summer-semester entrants are not included; stated as a limitation.
Decided by: team.

## 2026-10-14: Competitor data source

Decision: retrieve programme listings from the Bundesagentur fuer Arbeit study search API (rest.arbeitsagentur.de/infosysbub/studisu), which publishes Hochschulkompass data. No automated access to hochschulkompass.de search pages (blocked by its robots.txt).
Reason: structured, complete programme data; the API has no published terms of use, which the team accepts for this academic project.
Safeguards: programme data only (no personal data), 2-second delay between requests, raw replies cached and not redistributed, source cited as Hochschulkompass via BA Studiensuche with retrieval date.
Decided by: team (Somantha Manuranga).

## 2026-10-15: Catalogue coverage
Decision: use the hand-curated EMI portfolio (configs/oth_portfolio.yaml, from the EMI faculty page) for all overlap checks.
Reason: 2 of 14 active EMI programmes (AI for Industrial Applications M.Sc., KI International B.Sc.) are not listed in Hochschulkompass/Studiensuche; an institution-only API query is rejected (HTTP 400).
Consequence: the national competitor catalogue may also miss very new programmes elsewhere; stated as a limitation.
Decided by: team.

## 2026-10-15: Kill rule 1 applied
Decision: drop embedded/cyber-physical master (88 % of core topics already in IT und Automation) and the part-time AI master (already offered by AI for Industrial Applications). Keep cybersecurity bachelor and master; keep robotics + AI bachelor as comparison case (50 %, at threshold).
Evidence: docs/overlap_test.md, configs/overlap_test.yaml.
Decided by: team.

## 2026-10-15: Job-ad data and search interest
Decision: count open job ads from the BA Jobsuche API (rest.arbeitsagentur.de/jobboerse/jobsuche-service) by keyword and region; download Google Trends CSVs by hand from trends.google.com.
Reason: Destatis has no separate subject for cybersecurity, so demand and outlet need independent signals; the Python Trends library (pytrends) is no longer reliable.
Safeguards: totals only (no ad content or personal data stored beyond the first result page, kept locally), 2-second delay, snapshot date recorded; Trends settings (terms, region, period, category) recorded with each download.
Decided by: team (Somantha Manuranga).

## 2026-10-17: Google Trends method
Decision: use one download per comparison with "Informatik Studium" as anchor; report shares of the anchor by year (January-October), never absolute levels; treat 2022-01-01 (Google data-collection change) as a break.
Reason: Trends values are relative per download; absolute search volume for "Informatik Studium" fell while Destatis first-year numbers stayed flat, so levels reflect search behaviour, not students.
Consequence: Trends is a supporting leading indicator for Claim A, not a demand count. Bavaria not downloaded (too sparse).
Decided by: team.

## 2026-10-17: Google Trends check without the anchor
Decision: add a second download with the five specialist terms only (Cyber Security Studium, Cybersecurity Studium, IT Sicherheit Studium, Kuenstliche Intelligenz Studium, Robotik Studium; same settings) as a resolution check; the first term is the reference for ratios, not an anchor.
Reason: with "Informatik Studium" in the download the specialist terms were 0-7 on the 0-100 scale with 30-51 % zero months.
Consequence: both downloads give the same rank order since 2022 (cyber > KI > Robotik > IT Sicherheit). Reading corrected: cyber search interest rose 2018-2022 and is a plateau since 2022; its rising share of the anchor after 2022 comes from the anchor falling.
Decided by: team.

## 2026-10-17: Precision check of the theme rules (Step 38)
Decision: check the title keyword rules (analysis/themes.py, title match as used for the supply counts in analysis/first_look.py) by hand on bachelor and master offers in data/processed/programmes.csv. Sheet built by analysis/theme_check.py (seed 20261017) -> data/interim/theme_labels.xlsx, 110 rows:
- all 70 programmes whose title matches the cybersecurity rule (census instead of a sample, so the competitor count becomes exact);
- random samples of title matches: 10 robotics (of 43), 10 ai_data (of 274), 5 embedded_iot (of 21), for precision;
- miss check: 15 programmes (5 per theme) whose title matches none of cybersecurity/robotics/ai_data but whose content text matches one of them (pools: 139 / 125 / 329), to find specialised programmes the title rules miss.
Label per row: is this a specialised programme of the theme (main focus or a named track in the title)? y / n / ?.
Reason: the competitor counts in Claim B depend on the rules; precision was so far only checked informally. A random untagged sample would almost never contain a missed programme, so the miss check targets near-misses.
Limitation: content is the short Studiensuche teaser (max ~400 characters); the miss check estimates whether misses exist, not the full miss rate.
Decided by: team (Somantha Manuranga).

## 2026-10-17: Theme-rule check results, exact cyber count, secondary competitors (Step 38)
Decision: (1) Labels in data/interim/theme_labels_EN.xlsx were proposed by Claude (AI) with an English summary of each content text and reviewed row by row by a team member, who agreed with all 110; this is reported in the method. (2) Keep all theme rules unchanged: precision cybersecurity 94 % (66/70), robotics 90 % (9/10), AI/data 100 % (10/10), embedded/IoT 100 % (5/5), all >= 80 %; 0 of 15 near-misses were specialised programmes. (3) Count dedicated cybersecurity programmes as distinct programmes: drop the 4 false matches (rows 40, 43, 46, 48) and merge 3 duplicate pairs (HS Niederrhein B.Sc. and M.Sc. Teilzeit/Vollzeit; shared online B.Sc. IT-Sicherheit at TH Brandenburg/Ostfalia) -> 31 BA / 32 MA in Germany, 5 / 6 in Bavaria, 4 / 6 within 150 km. Saarland's English/German cyber bachelors and TH Lübeck's online bachelor are kept as separate (to verify; not near OTH). (4) Count secondary competitors automatically: general programmes whose title does not match the theme but whose "Schwerpunkte" list names it (same rules; "security printing" excluded; variants of one programme counted once).
Reason: the competitor count enters Claim B and the MCDA; variants and non-IT "security" titles inflated it. General programmes with a focus area compete for the same students but are not dedicated programmes, so they are reported separately rather than added.
Consequence: OTH's own Medieninformatik and Industrie-4.0-Informatik list "Informationssicherheit" as a focus area; the incrementality test must cover them. Secondary counts are lower bounds (focus areas come from a ~400-character teaser).
Decided by: team (Somantha Manuranga).

## 2026-10-17: Competitor module handbooks (Step 39)
Decision: collect the current module handbooks of the 10 dedicated cybersecurity programmes within 150 km of OTH (docs/theme_precision.md) plus the TH Mannheim master "Technische Informatik - Security und Industrial Internet of Things" (244 km) as a benchmark, because it is the only one with an industrial/OT security focus like our master idea. Download only public PDFs that robots.txt allows, 3 s delay after every request (incl. robots.txt), contact User-Agent, non-PDF replies rejected; every file recorded with URL, retrieval time, version (title page) and SHA-256 in docs/competitor_modules_manifest.json. Anything blocked or not found is not worked around but listed in docs/manual_downloads.md for manual download.
Result: 6 of 11 downloaded (FAU BA, THI BA, THI MA Cloud Applications und Security Engineering, TH Deggendorf MA, THWS BA, HDBW MA); 5 manual (TH Deggendorf BA: host of the found link does not resolve; THI MA Cyber Security Engineer, THI MA Sociotechnical Cybersecurity, HS Aalen MA Cyber Security, TH Mannheim MA: no public handbook found). URLs found by web search.
Caveat: THI MA Cloud Applications handbook is "Stand 28.09.2023"; an SPO is used only as a fallback where no handbook exists.
Decided by: team (Somantha Manuranga).

## 2026-10-17: Competitor handbooks, second round (Step 39)
Decision: official university URLs supplied by Soma are used with the same downloader rules. A third-party mirror (StudyCheck) is acceptable only for a document the university does not publish, labelled as a mirror. robots.txt is read with Python's robotparser (first match); where a file's rules conflict (static.studycheck.de: Disallow / and *.pdf, Allow /media/), it is treated as blocked and left to manual download.
Result: TH Deggendorf BA downloaded from th-deg.de; TH Mannheim handbook blocked by robots.txt (Disallow /fileadmin/) -> manual; Aalen SPO 511 link returns 404 -> manual; THI Sociotechnical Cybersecurity marked "no published handbook" (SPO notice has no module list, checked by Soma).
Decided by: team (Somantha Manuranga).

## 2026-10-17: Competitor handbooks closed (Step 39)
Decision: (1) TH Mannheim: the handbook PDF stays blocked (robots.txt Disallow /fileadmin/); the module tables of "Schwerpunkt Security" and "Schwerpunkt Industrial Internet of Things" are taken from the programme page, which robots.txt allows (transform/thm_modules.py; term = WS/SS offered, not semester number). (2) HS Aalen: use the two current module lists (Pflicht-/Wahlpflichtmodule, Stand 02.03.2026); names only, no module content. The page's "Modulhandbuch SPO 511" link is the Data Science und Business Analytics handbook (title page checked), so it is not used and its local copy was deleted. (3) THI Cyber Security Engineer: "no official handbook"; the StudyCheck mirror is skipped.
Consequence: of 11 programmes, 7 have full module descriptions, 2 only module names (Aalen, Mannheim), 2 none (THI Cyber Security Engineer, THI Sociotechnical Cybersecurity). The gap analysis must weight or flag programmes by how much text exists.
Decided by: team (Somantha Manuranga).

## 2026-10-17: One module table from all handbooks (Step 40)
Decision: build data/interim/modules.csv with transform/modules.py from 7 competitor handbooks, 6 EMI handbook files (8 EMI programmes; Industrie-4.0-Informatik and Medieninformatik share one handbook, modules assigned by section) and the names-only sources (HS Aalen module lists, TH Mannheim programme page). Module list = each handbook's table of contents in order; titles are found forward in the body by letters/digits only (robust to line breaks, hyphenation, bilingual headings); TOC page numbers are not used (several EMI handbooks restart numbering). Headers/footers are removed only as the repeated top/bottom block of a page, so field labels stay. Second pass for EMI layouts: a second "Modul-ID" block inside one module marks a module missing from the TOC. "siehe Seite N" pointers take the text of the referenced module; empty TOC group headings are dropped.
Result: 382 handbook modules + 1 cross-reference + 42 names-only rows (452 programme-module rows). Every TOC entry found; 2 modules not in the KI M.Sc. TOC added (Advanced Deep Learning, Modellbasierte Entwicklung); 3 group headings dropped; 0 texts under 200 characters; ECTS missing for 6 modules (5 KI B.Sc. where the handbook cell has no number, THI Einführungsprojekt). Independent check: per-module field labels counted in each handbook agree (differences are label words in running text).
Limitations: the E&IT B.Eng. file describes only the 10 first-section modules (sections 3.2-3.6 are headings only) and is SPO 226B; SPO 222B is still missing. Module texts include the form fields; Step 41 strips them before comparing.
Decided by: team (Somantha Manuranga).
Check: Soma compared 10 random modules (seed 20261017) with the PDFs; title, ECTS and text correct in 10 of 10. Step 40 closed.

## 2026-10-17: Module gap analysis (Step 41)
Decision: (1) Embeddings: intfloat/multilingual-e5-base ("query: " prefix, symmetric task) on 200-word chunks, mean-pooled; chosen over paraphrase-multilingual-MiniLM-L12-v2, which truncates at ~128 tokens. Embeddings are centred per handbook (each handbook's mean subtracted): raw e5 cosines are compressed (~0.9 for unrelated pairs) and every handbook has a house style. (2) Cross-check: character 3-5-gram TF-IDF (chosen over word TF-IDF by reference-set AUC, 0.75 vs 0.67; robust to German compounds). (3) Thresholds by Youden's J at the best-match level (per competitor module: best score among same-topic EMI modules vs among other-topic ones; topic groups from titles). Pair-level calibration had labelled 100 % as covered, because the best of ~150 candidates nearly always exceeds a pair threshold. (4) Literature sections are cut only at headings, not at the word "Literatur" in running text (this had removed most of the EMI content). (5) CyBOK areas by ordered title rules, else OT flag -> Cyber-Physical Systems Security, else embedding fallback (103 of 111 security modules by title rule). (6) Headline: ECTS-weighted share of security / general ECTS covered, median over competitor programmes.
Validation: Soma's hand check of 20 pairs (10 near the threshold, 5 clearly covered, 5 clearly gap): e5 16/20 correct, TF-IDF 14/20. All 4 e5 errors are "advanced competitor module matched to an EMI basics module" (pairs 7, 8, 13, 15), so e5 overestimates coverage; the 31 % (bachelor) / 39 % (master) headline is an upper-end estimate. Agreement between the methods is 74 %, below the 80 % target set for this step.
Decision on the missed target (Soma, option a): e5 is the headline because it is better validated by hand; TF-IDF (47 % / 45 %) is reported as a sensitivity range. The 80 % agreement target is not treated as a hard gate.
Result: EMI covers ~31 % of a typical cyber bachelor's security ECTS (range 18-39 %) and ~71 % of its general foundations; missing core: penetration testing/auditing, forensics, security operations/incident response, software security, management, law, human factors. TH Deggendorf already teaches OT/industrial security (BA and MA). Details: docs/evidence_fit_modules.md.
Decided by: team (Somantha Manuranga).

## 2026-10-17: Catchment data and method (Step 42)
Decision: (1) Data source: Bayerisches Landesamt für Statistik, Statistische Berichte B I/II 1 j (Tabelle 5: school leavers by general-education qualification and county), public PDFs via the Statistische Bibliothek, report years 2014-2018 and 2020-2024 (2019 edition not in the archive). Not used: Regionaldatenbank (robots.txt "Disallow: /", all automated access) and the GENESIS-Online Bayern API (account registered by Soma; login works with credentials as form fields, but table/catalogue services return error 15 "not entitled", i.e. no web-service rights for this account). (2) Parsing by the table's own arithmetic (row subtotals; counties sum to Bezirk, Bezirke to Bavaria; rows with several valid splits resolved by these sums). (3) Groups: Gymnasium Abitur, FOS/BOS (Fachhochschulreife + Hochschulreife from vocational schools), combined. (4) Catchment geometry: population-weighted county centres (Destatis GV-ISys 30.06.2026), straight-line distance; OTH = nearer of Amberg/Weiden; competitors = locations of their cybersecurity programmes (TH Deggendorf, TH Ingolstadt, nearer of FAU Erlangen/TH Nürnberg); own pool = counties closer to OTH than to all three; sensitivity with OTH Regensburg. (5) Forecast = 2023/24 values x KMK Dok. 251 index for Bavaria; sensitivity: the region's own trend gap continued.
Reason: county-level data with both Abitur and FOS/BOS for 10 years, from an official public source that allows automated download; the overlap test answers whether OTH has its own pool now that OT security is not a differentiator against TH Deggendorf.
Result: own pool ~5,500 qualified leavers a year (10.1 % of Bavaria; 3,800 without Regensburg), -19 % since 2013/14 (Bavaria -13.5 %); 91 % of OTH's 100-km catchment is closer to OTH than to TH Deggendorf, only 42 % closer than to Nuremberg/Erlangen; G9 gap 2024/25 halves the pool for one year. Details: docs/evidence_catchment.md.
Limitations: counts by school location; 17 non-Bavarian counties within 150 km not covered (Regionaldatenbank blocked).
Decided by: team (Somantha Manuranga).

## 2026-10-17: GENESIS-Online Bayern retest and correction (Step 42)
Correction: the Step 42 entry said the registered account "logs in with credentials as form fields, but has no web-service rights". That was wrong: with form fields the server ignores the credentials and logs in as the guest ("Username": "GAST"); the guest gets error 15 on every data/catalogue service. The account itself was never tested with a correct password (the password in .env was wrong at the time).
Retest after Soma corrected the password (once, as agreed): credentials as form fields -> guest, error 15; credentials in the HTTP headers (the documented way) -> no reply within 60 s (request timed out), as already observed in Step 42.
Decision: leave Step 42 as it is (PDF reports B I/II 1 j; 2018/19 stays a gap year). No further API attempts; if the API is needed later, ask genesis-online@statistik.bayern.de whether registered accounts have web-service access.
Decided by: team (Somantha Manuranga).
