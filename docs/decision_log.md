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

Decision: use the hand-curated EMI portfolio (configs/oth\_portfolio.yaml, from the EMI faculty page) for all overlap checks.
Reason: 2 of 14 active EMI programmes (AI for Industrial Applications M.Sc., KI International B.Sc.) are not listed in Hochschulkompass/Studiensuche; an institution-only API query is rejected (HTTP 400).
Consequence: the national competitor catalogue may also miss very new programmes elsewhere; stated as a limitation.
Decided by: team.

## 2026-10-15: Kill rule 1 applied

Decision: drop embedded/cyber-physical master (88 % of core topics already in IT und Automation) and the part-time AI master (already offered by AI for Industrial Applications). Keep cybersecurity bachelor and master; keep robotics + AI bachelor as comparison case (50 %, at threshold).
Evidence: docs/overlap\_test.md, configs/overlap\_test.yaml.
Decided by: team.

## 2026-10-15: Job-ad data and search interest

Decision: count open job ads from the BA Jobsuche API (rest.arbeitsagentur.de/jobboerse/jobsuche-service) by keyword and region; download Google Trends CSVs by hand from trends.google.com.
Reason: Destatis has no separate subject for cybersecurity, so demand and outlet need independent signals; the Python Trends library (pytrends) is no longer reliable.
Safeguards: totals only (no ad content or personal data stored beyond the first result page, kept locally), 2-second delay, snapshot date recorded; Trends settings (terms, region, period, category) recorded with each download.
Decided by: team (Somantha Manuranga).



\## 2026-10-17: Google Trends method

Decision: use one download per comparison with "Informatik Studium" as anchor; report shares of the anchor by year (January-October), never absolute levels; treat 2022-01-01 (Google data-collection change) as a break.

Reason: Trends values are relative per download; absolute search volume for "Informatik Studium" fell while Destatis first-year numbers stayed flat, so levels reflect search behaviour, not students.

Consequence: Trends is a supporting leading indicator for Claim A, not a demand count. Bavaria not downloaded (too sparse).

Decided by: team.

