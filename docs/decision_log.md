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

## 2026-10-17: Regional labour market, lean version (Step 43)
Decision (Soma): keep Step 43 lean. (1) Use the Bavarian employment reports A VI 5 - Teil 1 (30.06.2019, 30.06.2023; public PDFs via the Statistische Bibliothek) for IT occupations (KldB 2010 main group 43) Bavaria-wide. (2) Drop the county-level ICT-sector table (Tabelle 9): two parsing attempts timed out (facing-page layout); stated as a limitation. (3) Skip the BA occupation-by-county tables (only behind /SiteGlobals/ download forms, disallowed by robots.txt; Crawl-delay 30 is now honoured by ingest/documents.py). (4) Shortage status from the BA Fachkräfteengpassanalyse 2025 (Germany). (5) Second Jobsuche snapshot.
Result: IT occupations in Bavaria +23.8 % (2019-2023), with academic degree +34.3 % (academic share 48.5 % -> 52.6 %); Informatik (4310) again a shortage occupation at specialist level in 2025, software development no longer at expert level; job-ad counts stable between 15 and 17 Oct (median change 1.4 %), Bavarian security shares unchanged. Details: docs/evidence_outlet_jobs.md.
Decided by: team (Somantha Manuranga).

## 2026-10-17: Staff and labs fit (Step 44)
Decision: (1) Step order swapped (Soma): Step 44 = staff & labs fit, Step 45 = international benchmarks (lean). (2) Teaching capacity from module responsibility in the EMI module handbooks; labs and institutes from public OTH pages found via the sitemap (robots.txt respected, 3 s delay, manifest docs/oth_web_manifest.json). (3) Person pages not read: OTH's robots.txt blocks AI crawlers (GPTBot) from /hochschule/ueber-uns/personen/; we follow that intent although our user agent is not named, and also skip professors' personal microsites. (4) Teaching load 18 SWS per semester for HAW professors (§ 4 AVBayHIG, version 13.02.2023, valid from 01.03.2026); 15 SWS effective as sensitivity. (5) New load = uncovered security ECTS of a full-time competitor bachelor (40-52) x 4/5 SWS + 8 SWS lab groups.
Result: ~4 EMI professors teach security today (information security, cryptography, network security, AI security) and ~4 the industrial/embedded side; gaps in pentesting, forensics, SOC, malware need new staff; OT and software security partly covered; law/governance via teaching assignments. New bachelor load 40-50 SWS/year = 1.1-1.7 professorships -> estimate 2 new professorships + 1 lab engineer + a security lab. Details: docs/evidence_fit_staff.md.
Decided by: team (Somantha Manuranga).

## 2026-10-17: Neutral labels instead of professors' names (Step 45)
Decision (Soma): the repository shows no names of EMI professors; docs/evidence_fit_staff.md uses neutral labels (Prof. A-N with their area) and module titles, keeping the evidence (module responsibilities, counts). Checked with git grep: no names left in tracked files except the course supervisor in CLAUDE.md (project metadata, not evidence). Remaining: the git history (commit eb1bdb8, pushed) still contains the names; rewriting published history was not done (only on explicit request). Local git-ignored data (data/interim/modules.csv, reports/) keep the handbook text as source material.
Decided by: team (Somantha Manuranga).

## 2026-10-17: International benchmarks, lean (Step 45)
Decision: 4 programmes with public curriculum structure: USTP St. Pölten IT Security (BSc, full module list), FH OÖ Hagenberg Sichere Informationssysteme (BSc, module groups), Hochschule Luzern Information & Cyber Security (BSc, module categories), Abertay Ethical Hacking (BSc Hons, frame only). OT-focused programme: none usable (ECAM LaSalle: no ECTS/modules published; Turku UAS Cyber Security and IoT: robots.txt blocks its study guide, skipped; elsewhere ICS/SCADA security is a master topic or a single course); OT reference = TH Deggendorf (Step 41) and HSLU's product-security core modules. Draft OTH bachelor in the verified Bavarian HAW format (7 semesters, 210 ECTS, practical semester 5; BayHIG Art. 77 Abs. 3, RaPO § 2 Abs. 2, HAW regulations): 45 ECTS new by new staff (consistent with 2 new professorships, Step 44), 10 ECTS teaching assignments, 110 ECTS reused/adapted EMI modules, 45 ECTS practical semester and thesis formats; security share 36 %.
Decided by: team (Somantha Manuranga).

## 2026-10-17: Phase 3 plan and demand forecast (Step 46)
Decision: Phase 3 = Steps 46 (demand forecast), 47 (capture model), 48 (cannibalisation), 49 (MCDA + Monte Carlo), each with a Done-when (CLAUDE.md). Step 46: Destatis first-years 2005-2025 (winter semesters) for Informatik and a cyber proxy (Informatik + Technische Informatik + Computer- und Kommunikationstechniken; Destatis has no cyber subject), Germany and Bavaria, trained to 2024 (2025 = Bavarian G9 transition). Models naive, drift, damped-trend ETS; rolling-origin backtests from 2012, h = 1-5, MASE. KMK Dok. 1 (table 5.1) only as a growth index (state-run HEIs, study year), not as levels; the constant-share model can only be checked with actual totals (conditional). Reporting: conservative = KMK scenario (constant share), upside = drift with 80 % band from empirical backtest errors, central = midpoint (stated as a planning value).
Result: drift best in all series (mean MASE 1.0-1.9 vs naive 2.5-3.5); constant share worst (3.8-4.3) because the Informatik share rose; drift under-forecast in 62-80 % of backtest errors. Bavaria cyber proxy: conservative 5,057 / 5,519, upside 6,019 / 6,922, central ~5,540 / 6,220 (2030 / 2035); 2024: 4,936. Cross-check: KMK Bavarian school leavers 2023 (54,773) match the Step 42 parse (54,771). Details: docs/evidence_forecast.md.
Decided by: team (Somantha Manuranga).

## 2026-10-17: Capture model (Step 47)
Decision: (1) Calibrate distance decay on real flows: Bavarian report "Studierende an den Hochschulen in Bayern" WS 2024/25, Tabelle 5 (students of 17 state HAWs by Regierungsbezirk of entrance qualification), doubly-constrained gravity model, beta by lowest SRMSE (best 1.6, R2 0.95; 1.3-1.95 within 10 %). (2) The absolute demand side (qualified leavers x cyber-proxy rate 9.0 % x dedicated-cyber share 3.9-12.6 %) fails the check (THI implied 59-173 vs planned capacity 25), so only relative capture is used, anchored on real intakes: THI capacity 25 (official, likely >= intake; low) and TH Deggendorf ~60 (one student review, weak; high); central = geometric mean (a choice). Secondary competitors (focus areas, Step 38) as sensitivity w = 0/0.5/1. (3) Ramp-up 60/80/100 % (assumption). (4) Minimum viable cohort: no Bavarian rule found; assumption 20, THI's 25 as reference. (5) Step 46 central value restated as a chosen midpoint, not a model output.
Result: OTH draws 0.65-0.86 x THI and 1.20-1.28 x Deggendorf (stable). OTH Cyber B.Sc. steady state: low 21, central 39, high 75 first-years (year 1: 12 / 24 / 45). Viable in central/high, borderline in low. OTH programme-level intake not public (only engineering sciences 452 first-years, WS 2024/25). Next best evidence: actual cyber intakes from THI/TH Deggendorf.
Decided by: team (Somantha Manuranga).

## 2026-10-17: Cannibalisation and regional benefit (Step 48)
Decision: (1) Split the new programme's students with the Step 47 Huff model (with vs without the new OTH programme): (a) from OTH's existing programmes, (b) from other universities (net new), (c) from OTH's own pool whose baseline choice was outside the region (regional benefit, part of b). OTH's Industrie-4.0-Informatik/Medieninformatik enter as security-focus alternatives at weight 0.5/1; beta 1.3/1.6/1.95. (2) Threshold: kill rule 1 (more than 50 % of core modules in one OTH programme at the same level; docs/kill_rules.md, set 14 Oct 2026 before scoring). kill_rules.md has no cannibalisation threshold and none is added after scoring started; cannibalisation enters the MCDA via the student-demand criterion ("includes the new-to-OTH share", configs/analysis.yaml). (3) Public data only (Soma: no intake figures from universities); the Step 47 low/central/high range is carried forward in data/interim/capture_scenarios.csv for the Step 49 Monte Carlo.
Result: (a) 14-27 %, (b) 73-86 %, (c) 13-16 % of gross. Net new first-years low 15.3 / central 32.0 / high 64.4; stress test with 50 % cannibalisation 10.5 / 19.5 / 37.5. Kill rule 1 passed (2 of 15 core security modules = 13 % in Industrie-4.0-Informatik; module-level coverage <= 28 %).
Decided by: team (Somantha Manuranga).

## 2026-10-17: Ranking of the shortlist, MCDA + Monte Carlo (Step 49)
Decision: (1) Against evidence asymmetry (Soma), the Step 47/48 capture + cannibalisation model is run unchanged for the Robotics+AI B.Sc. and the Cyber/OT M.Sc. (analysis/options.py; reproduces Step 48 for the cyber B.Sc.). Robotics: competitors from the robotics theme in the catalogue (title = dedicated, focus areas = w); from OTH = KI B.Sc., E&IT and Mechatronik und digitale Automation (IT und Automation is a master and is used for the master only). Master: hand-checked cyber masters within 150 km; from OTH = AI for Industrial Applications and IT und Automation; origins = Bavarian state HAWs (Tabelle 5). (2) Anchors: robotics has no verified public intake figure (THI Robotik handbook host does not resolve / 404, TH Augsburg 404, Kempten no figure; no workaround) -> assumed comparator intake 20-60 with the range over all model variants; master: THI CASE capacity 30, high = low x cyber B.Sc. spread (assumption). (3) Score sheet configs/scores.yaml proposed by Claude, reviewed by Soma, who changed: robotics fit and feasibility to 2/3/5 and added the rule "weak evidence widens the range, it doesn't raise the centre" (docs/kill_rules.md); robotics labour from the BA Engpassanalyse 2025 (Mechatronik/Automatisierung not named in the published top-10 lists; Elektrotechnik and technical R&D are specialist-level shortages) plus the local job signal -> 3/3.5/4.5. (4) Monte Carlo: Dirichlet weights (10,000, concentration 50, seed 42); one common capture-model draw per iteration for all options (Soma: shared anchor error must not flip the ranking at random); other scores independent triangular. Robotics with 50 % cannibalisation reported as a full scenario. Anchors for criteria other than demand written in Step 49, after evidence collection, before the ranking.
Result: Cyber B.Sc. P(rank 1) 87.8 % (robotics-50 % scenario 91.7 %; independent capture draws 82.5 %); first in every leave-one-criterion-out run except without demand (tie with robotics 49 % / 50 %). Second place open (master 52 % / robotics 37 % rank 2; master 73 % in the robotics-50 % case). Robotics evidence weakest (no anchor, fit/feasibility title-level). The 2/3/5 skew lifts the robotics mean; symmetric 1.5/3/4.5 gives 2.3 % instead of 6.9 %.
Decided by: team (Somantha Manuranga).

## 2026-10-18: Robotics fit/feasibility made symmetric (Step 49 correction)
Decision: robotics institutional fit and feasibility 1.5 / 3 / 4.5 instead of 2 / 3 / 5, so the range follows the rule "weak evidence widens the range, it doesn't raise the centre" (2 / 3 / 5 had a mean of 3.33). 2 / 3 / 5 kept as a sensitivity line.
Result: Cyber B.Sc. P(rank 1) 91.7 % (robotics 50 %: 93.2 %; skewed 2/3/5: 87.8 %); first in every leave-one-criterion-out run (lowest without demand 67.2 %, without labour 77.8 %). Master second (67 % rank 2), robotics last (72 % rank 3).
Decided by: team (Somantha Manuranga).

## 2026-10-18: Key numbers, shared figures, report outline (Step 50)
Decision: one build (python -m study_program_intelligence.report.build) generates reports/key_numbers.yaml, reports/figures/ and reports/final/outline.md. Every number used by report, slides and dashboard is defined once with its source doc; numbers from generated tables are read from data/interim, others are taken as stated in the evidence doc. Each number must occur verbatim in its source doc (no partial matches inside longer numbers; job-ad numbers matched against their full table row). Job-ad numbers use the snapshot shown in the evidence doc (15 Oct) until the 4 Dec freeze. Figures: matplotlib, one palette (options always in the same colour), source line on each figure. Outline numbers inserted from the key-numbers file; an unknown placeholder stops the build. Wording fixes in the outline: "drift is the best model in all four series" (not "every backtest"), no 2026/27 start (semester already running), master as follow-on marked as a proposal. reports/ stays git-ignored; the Step 51 draft source will live in docs/report/.
Result: 74 numbers, all found in their source docs; 7 figures; outline with sections 0-9 + appendix. Spot check of 12 numbers passed (Soma).
Decided by: team (Somantha Manuranga).

## 2026-10-18: Report draft (Step 51)
Decision: (1) Format per Soma: English, Markdown -> .docx/PDF via pandoc (pypandoc_binary in .venv; PDF via MiKTeX xelatex), author-year citations (docs/report/references.yaml, pandoc citeproc), ~20-25 pages + appendix; length, format and section order in docs/report/report.yaml. (2) Section texts in docs/report/ (committed) contain no typed numbers: every number is a {{key}} from reports/key_numbers.yaml, figures are {{fig:...}}, appendix tables {{table:sources}} / {{table:scores}} are generated; the build fails on an unknown placeholder or a typed number (percentages, decimals, thousands separators, integers >= 10 outside allowed patterns). (3) Additions by Soma: a selection-funnel section and figure early in the report (docs/evidence_funnel.md; git history shows weights and kill rules committed 14 Oct 16:35/16:37, before the first screening at 22:42), a "Use of AI tools" paragraph in the method section, section 10 proposals (master as follow-on, robotics as KI specialisation) labelled as team judgement. (4) Register repaired: configs/sources.yaml had unquoted colons (did not parse since Step 39) and lacked BA Studiensuche, BA Jobsuche and Google Trends; fixed and added. (5) Key numbers extended to 179 (method, funnel and claim-level numbers), all matched verbatim in their source docs. (6) Spot check: python -m study_program_intelligence.report.spotcheck draws 10 sentences with key numbers (seed 20261018) and shows the matched source text.
Weak point recorded in the funnel: automation, energy and medtech were not carried forward on 14 Oct without a separate written verdict (OTH already offers each theme).
Decided by: team (Somantha Manuranga).

## 2026-10-18: Dashboard (Step 52)
Decision: Streamlit dashboard in app/, local only (Soma: no deployment; data/ and reports/ stay git-ignored). No analysis of its own: every number is a key number (metrics carry their key and source doc), tables come from data/interim, and the ranking explorer calls analysis.ranking.simulate unchanged (base weights passed through exactly, changed weights normalised to sum 1). Checks: tests/test_dashboard.py (all 8 pages run; every metric equals its key number; explorer reproduces 91.7 / 6.0 / 2.3 %; demand weight 0 reproduces the leave-one-out 67.2 %; Reset restores the base). Same option colours as the report figures; the palette validator could not run (no Node.js), identity is always also given by text labels. Screenshots of all pages as presentation backup via headless Chrome with a throw-away profile (app/screenshots.py). README commands were checked against the module CLIs before this step (document lists need --out/--manifest).
Decided by: team (Somantha Manuranga).

## 2026-10-18: Reproducibility (Step 54)
Decision: one-command pipeline (python -m study_program_intelligence.pipeline) that runs the documented module commands as subprocesses in order, stops at the first failure, runs the tests and compares the new key numbers with the previous run. Downloads only with --ingest (cached files kept; a download list that ends with known gaps, e.g. the two dead anchor links, does not stop the run); job-ad snapshots only with --snapshot, because a snapshot adds dated data. Manual inputs are checked before the run: Google Trends CSVs, OTH module handbooks, and the hand-checked theme labels data/interim/theme_labels_EN.xlsx. The theme labelling sheet is rebuilt from the catalogue (fixed seed) only when missing, never overwritten. Tests (44): PDF number parsing, model building blocks (distances, gravity margins, forecasts, score mappings, Monte Carlo reproducibility), configs (parse, weights, score ranges incl. symmetric weak-evidence ranges, source register, citations), key numbers vs evidence docs, report number rules, dashboard.
Result: in-place rerun 19/19 steps + tests passed, 179/179 key numbers unchanged, no tracked file changed. Clean clone (committed code + data/raw + hand labels, no generated files): 20/20 steps + tests passed, 179/179 key numbers identical; the clone run found and fixed one gap (theme labelling sheet was not rebuilt). Not tested: re-downloading all sources (--ingest) from scratch, to spare the source servers; downloads are recorded in the manifests.
Decided by: team (Somantha Manuranga).

## 2026-10-18: Theme labels committed (Step 54 addition)
Decision (Soma): the 110 hand-checked theme labels of Step 38 are committed as docs/theme_labels.csv (all columns of the reviewed sheet, incl. the English explanations; .gitignore exception for this one file). analysis/theme_check.py reads the labels from there; the pipeline no longer treats them as a manual input. Reason: they are the team's own work and a required input of the rebuild; public programme titles only, no personal data. Check: reports/theme_check.md is identical before and after the switch except for the label-file path in its header (labels y 90, n 20; all results unchanged).
Decided by: team (Somantha Manuranga).
