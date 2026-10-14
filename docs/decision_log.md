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
