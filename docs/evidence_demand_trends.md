\# Evidence: search interest (Google Trends)



Source: Google Trends, trends.google.com, "Interest over time", downloaded by hand on 2026-10-17.

Settings: Germany, 2004-present (monthly), all categories, web search. Analysis uses 2015-01 to 2026-10.

File: data/raw/trends/trends\_DE\_2015\_2026.csv. Tables: reports/trends.md (python -m study\_program\_intelligence.analysis.trends).

Terms: Informatik Studium (anchor), Cyber Security Studium, IT Sicherheit Studium, Kuenstliche Intelligenz Studium, Robotik Studium.



\## Main metric: share of the anchor



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



\## Reading



1\. \*\*Cyber security is the only specialist term with a sustained rise.\*\* From almost zero before 2018 to

&#x20;  12.6 % of the Informatik interest in 2026, rising every year since 2018. Within the post-2022 regime its own

&#x20;  level also rises slightly (4.6 to 5.5) while the anchor falls.

2\. \*\*"IT-Sicherheit" is being replaced by "Cyber Security".\*\* The German term falls (4.4 % to about 2 %), the

&#x20;  English one rises. Combined security interest goes from 5.7 % (2019) to 14.7 % (2026) of Informatik.

&#x20;  Programme naming should use the English term (or both).

3\. \*\*KI study interest rose after 2022 and then levelled off\*\* (about 5 % since 2024). It sits below cyber

&#x20;  security, and OTH already offers AI programmes (kill rule 1).

4\. \*\*Robotik is flat\*\* at 2-4 % throughout. No sign of rising study demand for a robotics programme.

5\. \*\*"Informatik Studium" falls since 2023\*\* (Jan-Oct mean 71 to 44). Destatis shows German Informatik

&#x20;  first-year numbers flat 2023-2025, so this is mostly a change in how people search, not fewer students.

&#x20;  This is why only shares are used, never absolute levels.



\## Support for the argument



Claim A (Demand): supports cybersecurity over robotics and generic AI. Search interest in a cyber security

degree has grown faster than in any other tested specialisation and is now about 1/8 of all Informatik degree

interest. It is a leading indicator, not a student count.



\## Caveats



\- Small values: specialist terms are 0-7 on the 0-100 scale, Google rounds to integers, and 30-51 % of months

&#x20; are 0. Yearly means smooth this, but single months are noise. A second download without the anchor

&#x20; (higher resolution for the specialist terms) is planned as a check.

\- Search terms are a narrow proxy: people also search "Cybersecurity studieren", programme names or university names.

\- Germany only; Bavaria-level data would be mostly zeros for these terms.

\- Google does not publish the sampling method; values can change slightly between downloads.

