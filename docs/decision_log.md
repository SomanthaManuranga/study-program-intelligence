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
