# Evidence: graduate outlet from job-ad counts (claim D)

Status: v2, 17 Oct 2026 (Step 43): job-ad snapshots 15 and 17 Oct 2026, IT occupations in Bavaria 2019-2023, BA shortage analysis 2025. Source: BA Jobsuche API (/pc/v6/jobs), job offers only (angebotsart 1), total matches per keyword and region; data in `docs/jobsuche_snapshots.json`, produced by `python -m study_program_intelligence.ingest.jobsuche snapshot`. Shares are own calculations.

## Counts

| Group | Keyword | Germany | Bavaria | ≤ 100 km Amberg | ≤ 50 km Amberg | Bavaria share of Germany |
| --- | --- | --- | --- | --- | --- | --- |
| Cybersecurity | IT-Sicherheit | 6,191 | 1,352 | 831 | 111 | 21.8 % |
| Cybersecurity | Cyber Security | 851 | 263 | 191 | 8 | 30.9 % |
| Cybersecurity | Security Engineer | 838 | 209 | 153 | 16 | 24.9 % |
| Cybersecurity | Informationssicherheit | 751 | 156 | 101 | 6 | 20.8 % |
| Cybersecurity | OT Security | 153 | 53 | 34 | 9 | 34.6 % |
| Comparison | Robotik | 944 | 287 | 161 | 58 | 30.4 % |
| Baseline | Informatiker | 3,378 | 842 | 601 | 99 | 24.9 % |
| Baseline | Softwareentwickler | 3,421 | 772 | 608 | 98 | 22.6 % |
| Baseline | Künstliche Intelligenz | 945 | 191 | 160 | 18 | 20.2 % |
| Baseline | Data Scientist | 304 | 56 | 59 | 6 | 18.4 % |
| Baseline | Embedded | 1,248 | 319 | 351 | 54 | 25.6 % |
| Baseline | Elektroingenieur | 653 | 115 | 63 | 9 | 17.6 % |

## Reading

1. **Security is a large job market, not a niche.** Specific security titles ("Cyber Security" 851, "Security Engineer" 838) each match about as many ads as "Künstliche Intelligenz" (945) and far more than "Data Scientist" (304). "IT-Sicherheit" matches 6,191 ads, more than "Informatiker" or "Softwareentwickler"; part of that is security named as a requirement in other IT jobs, which still shows employers want the skill.
2. **Bavaria is over-represented in security, especially industrial security.** Bavaria's share is 30.9 % for "Cyber Security" and 34.6 % for "OT Security", against 22–25 % for the computer-science baselines. OT (operational technology) security is the industrial niche that fits EMI's automation profile (IT und Automation, Industrie-4.0-Informatik).
3. **The immediate region is thin; the 100 km catchment is not.** Within 50 km of Amberg there are only 8 "Cyber Security" ads, but 191 within 100 km (Nuremberg and Regensburg fall inside). Graduates would mostly work in the wider region, which is normal for a HAW in a small city.
4. **Robotics has the strongest local signal** (58 ads within 50 km, more than AI with 18), which supports keeping robotics + AI as the comparison case.
5. This is consistent with the BA shortage analysis 2025 (see below): Informatik is a shortage occupation at specialist (bachelor-type) level.

## Second snapshot (17 Oct 2026)

Changes from 15 to 17 Oct are small for every keyword and region (median absolute change 1.4 %; "Cyber Security" Germany 851 -> 858, Bavaria 263 -> 270; "IT-Sicherheit" 6,191 -> 6,378; "OT Security" 153 -> 152). Bavarian shares are unchanged ("Cyber Security" 31.5 %, "OT Security" 34.2 %). Two days show that the counts are stable to measure, not a trend; snapshots continue every 2-4 weeks until 4 Dec.

## IT occupations in Bavaria (employment)

Source: Bayerisches Landesamt für Statistik, Statistische Berichte A VI 5 - Teil 1 (BA employment statistics), Tabelle 10, employees subject to social insurance at place of residence, KldB 2010 main group 43 "Informatik-, Informations- und Kommunikationstechnologieberufe". Tables: `reports/labour.md` (`python -m study_program_intelligence.analysis.labour`).

| | 30.06.2019 | 30.06.2023 | Change |
|---|---|---|---|
| IT occupations, all | 173,057 | 214,223 | +23.8 % |
| with vocational degree | 64,454 | 74,392 | +15.4 % |
| with academic degree | 83,924 | 112,676 | **+34.3 %** |
| academic share | 48.5 % | 52.6 % | |

Reading: IT employment in Bavaria grew by a quarter in four years, and graduate IT employment by a third: demand is shifting towards degree holders.

## Shortage status (BA Fachkräfteengpassanalyse 2025, Germany)

- **Specialist level (bachelor-type):** "Berufe in der Informatik" (KldB 4310) are again a shortage occupation in 2025 (score 2.0); IT sales dropped out.
- **Expert level (master-type):** software development is no longer a shortage occupation in 2025.
- IT security is not shown as a separate occupation; the report has no Bavarian or regional breakdown.
Reading: the shortage is at the bachelor-type level, which fits a HAW bachelor; for a master the shortage argument is weaker and must rest on the security specialisation and industry demand (job ads), not on the shortage list.

## Caveats

- Full-text keyword search: ads can match several keywords, and a match does not mean the ad is for a specialist. Counts are indicators, not vacancies by occupation.
- Two snapshots two days apart (stable). Continue every 2–4 weeks until the analysis freeze (4 Dec) for a trend.
- The BA job board does not contain all ads in Germany (private job portals are missing), so levels are lower bounds; shares between regions are more robust than levels.
- "Bayern" is passed as a location text; how the API resolves it (state vs. place) is not documented. The plausible ratios (about a quarter of German IT ads) suggest it is read as the state.
- Ads cover all qualification levels, not only graduates.
- Region filters differ: the radius search (<= 100 km of Amberg) and the "Bayern" location text are resolved differently by the API (e.g. "Embedded": 358 within 100 km vs 322 in "Bayern"). Compare shares within one filter, not across filters.
- No county-level occupation or ICT-sector data (limitation, Step 43): the BA occupation-by-county tables are only behind download forms that robots.txt disallows (skipped by decision), and the county table by economic sector in the Bavarian report (Tabelle 9, split over facing pages) could not be parsed reliably within two attempts. Regional demand therefore rests on the job-ad counts.
- The shortage analysis is Germany-wide and by occupation group; it says nothing about IT security specifically or about Bavaria.
