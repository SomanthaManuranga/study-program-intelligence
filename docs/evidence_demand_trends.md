# Evidence: search interest (Google Trends)

Source: Google Trends, trends.google.com, "Interest over time", downloaded by hand on 2026-10-17 (two downloads).
Settings (both): Germany, 2004-present (monthly), all categories, web search. Analysis uses 2015-01 to 2026-10.
Tables: reports/trends.md (python -m study_program_intelligence.analysis.trends).
- Download 1 (anchored): data/raw/trends/trends_DE_2015_2026.csv. Terms: Informatik Studium (anchor),
  Cyber Security Studium, IT Sicherheit Studium, Kuenstliche Intelligenz Studium, Robotik Studium.
- Download 2 (specialist only, check): data/raw/trends/trends_DE_specialist_2015_2026.csv. Terms: Cyber Security
  Studium, Cybersecurity Studium, IT Sicherheit Studium, Kuenstliche Intelligenz Studium, Robotik Studium.
  Without the large anchor the specialist terms use more of the 0-100 scale (higher resolution).

## Main metric: share of the anchor

Trends values are relative, and Google changed its data collection on 2022-01-01. Absolute levels therefore
say little. The robust metric is each term's share of "Informatik Studium" inside the same download:
anything that moves all searches (data-collection changes, people asking chatbots instead of Google) moves
the anchor too and cancels out.

| Year (Jan-Oct) | Cyber Security Studium | IT Sicherheit Studium | KI Studium | Robotik Studium |
|---|---|---|---|---|
| 2019 | 1.3 % | 4.4 % | 1.5 % | 2.4 % |
| 2021 | 4.5 % | 3.7 % | 2.4 % | 3.5 % |
| 2023 | 7.3 % | 2.4 % | 4.5 % | 2.7 % |
| 2025 | 10.4 % | 1.3 % | 4.9 % | 3.0 % |
| 2026 | 12.6 % | 2.1 % | 5.7 % | 3.4 % |

## Check: specialist terms without the anchor (download 2)

Yearly means, January-October, 0-100 scale of download 2 (peak of all five terms = 100).

| Year | Cyber Security Studium | Cybersecurity Studium | IT Sicherheit Studium | KI Studium | Robotik Studium |
|---|---|---|---|---|---|
| 2019 | 3.2 | 0.0 | 11.0 | 3.5 | 6.4 |
| 2021 | 9.5 | 0.0 | 7.5 | 4.7 | 7.7 |
| 2022 | 18.5 | 0.6 | 9.4 | 5.0 | 11.5 |
| 2023 | 20.2 | 0.7 | 7.0 | 12.5 | 7.2 |
| 2024 | 21.3 | 5.4 | 6.1 | 13.3 | 9.4 |
| 2025 | 21.7 | 2.9 | 2.9 | 9.8 | 5.8 |
| 2026 | 22.0 | 11.6 | 3.1 | 9.0 | 6.0 |

Mean 2022-2026 (monthly): Cyber Security Studium 20.1, KI 9.6, Robotik 7.6, IT Sicherheit 5.5, Cybersecurity 4.2.
Zero months since 2022: Cyber Security Studium 0 %, KI 17 %, Robotik 24 %, IT Sicherheit 40 %, Cybersecurity 60 %.

## Reading

1. **Cyber security is the largest specialist term, but its rise was 2018-2022; since 2022 it is a plateau.**
   Download 2 shows it going from 0 (2015-17) to 18.5 (2022), then only 18.5 to 22.0 by 2026
   (slope +1.05 points/yr). Since 2022 it is about 2x KI and 2.6x Robotik, and the only term with no zero months.
   The rising share of the anchor after 2022 (6.4 % to 12.6 %) comes mainly from "Informatik Studium" falling,
   not from more cyber searches (download 1: cyber level 4.6 to 5.5, flat).
2. **"IT-Sicherheit" is being replaced by English terms.** The German term falls in both downloads
   (download 2: 9.4 in 2022 to 3.1 in 2026). "Cybersecurity Studium" (one word) appears from 2024, but is still
   0 in 60 % of months, so its 2026 jump (11.6) is weak evidence. All three security terms together: 28.5 (2022)
   to 36.7 (2026). Programme naming should use the English term (or both spellings).
3. **KI study interest peaked in 2023-24 and is falling** (download 2: 13.3 in 2024 to 9.0 in 2026). It sits
   below cyber security, and OTH already offers AI programmes (kill rule 1).
4. **Robotik is flat or slightly falling** (download 2: 6-11, slope -1.2/yr since 2022; download 1: 2-4 % of
   Informatik). No sign of rising study demand for a robotics programme.
5. **"Informatik Studium" falls since 2023** (Jan-Oct mean 71 to 44). Destatis shows German Informatik
   first-year numbers flat 2023-2025, so this is mostly a change in how people search, not fewer students.
   This is why only shares are used, never absolute levels.

## Support for the argument

Claim A (Demand): supports cybersecurity over robotics and generic AI. Cyber security has been the largest of
the tested specialisations since 2022 (about 2x KI) and is now about 1/8 of all Informatik degree interest.
Its growth phase was 2018-2022; since then interest is high but stable, not still rising. It is a leading
indicator, not a student count.

## Caveats

- Small values: in download 1 the specialist terms are 0-7 on the 0-100 scale and 30-51 % of months are 0.
  Download 2 removes most of this for Cyber Security Studium (0 % zero months since 2022) but not for
  "Cybersecurity Studium" (60 %) and "IT Sicherheit Studium" (40 %). Yearly means smooth this; single months are noise.
- The two downloads agree on direction for every term (rank order since 2022: cyber > KI > Robotik > IT Sicherheit).
- Search terms are a narrow proxy: people also search "Cybersecurity studieren", programme names or university names.
- Germany only; Bavaria-level data would be mostly zeros for these terms.
- Google does not publish the sampling method; values can change slightly between downloads.
