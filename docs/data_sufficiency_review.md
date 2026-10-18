# Review of the data-sufficiency changes (report, summary, Q&A, README, dashboard)

A fresh-context reviewer agent checked every new or changed factual sentence of the data-sufficiency round, and every
old sentence that the new results might contradict. It checked them against the evidence docs, the generated tables,
configs/scores.yaml, the decision log and the key numbers.

**Result:** about 95 new or changed sentences:

- about 62 supported, 27 caveat, 4 overstated, 2 wrong, none unsupported;
- 10 old sentences contradicted by the new results.

All were fixed; the main fixes by theme:

| Theme | Finding | Fix applied |
|---|---|---|
| Robustness | "stays first whichever criterion is left out" and "lowest share 67.2 %" now hold only in the base case; with German-only demand trends the bachelor wins five of six leave-one-out runs (lowest 58.6 %) and loses narrowly without labour relevance | limited to the base case everywhere (report summary and Section 8, limitations, Q22, README, dashboard overview and metric label, f07 caption); 58.6 % added as a key number |
| Published intakes | "no university of applied sciences publishes" overstated a one-day search; THI's 25 lies below the 42-156 range, not at its low end; first subject semester includes subject changers | "none of the universities of applied sciences we searched"; "below that range"; subject-changer caveat |
| Out-of-state share | an exact share (13.7 %) was compared with approximate ones; the effect on the estimate is reasoned, not tested | like-with-like comparison on the approximate method (OTH 11.5 %, THI 11.0 %, THD 8.0 %); "reasoned, not tested" |
| Demand wording | "strongest large EMI subject" among Germans holds in Bavaria only; 2025 foreign share inflated by the G9 gap; nationality is not origin | "only large subject that grew in Bavaria; in Germany about level with Wirtschaftsinformatik"; 2024 share (40 %) with 2025 in brackets; "foreign-nationality" / "foreign students" |
| English-taught | one cyber data point, bachelors only; OTH's contract is a positive non-cyber point | "not supported as the main variant on the one cyber data point"; "whether an English master would do better is not measured"; term given (winter 2025/26) |
| Theme verdicts | "almost all rows"; health informatics fits none of the listed reasons; next stage judged at title level | "all but two of the original rows"; "small and falling base" added; "judged at title level, not tested" |
| Competition | Deggendorf's transfer centre supports, but does not establish, "OT is no differentiator" | "supports the finding that OT security is no differentiator" |
| Sensitivity scores | German-only trend scores are Claude's proposal | "(scores proposed by the AI assistant, pending the team's review)" in Section 8 |
| Old, now wrong | summary: "none of the programmes we checked publishes this number"; Q24: Saxony/Thuringia "biases the estimate downward" | "none of the similar programmes at universities of applied sciences"; replaced with the measured out-of-state comparison |

## Recheck

The same reviewer rechecked all 41 findings: 40 fixed, 1 missed (summary Section 5). It also found 1 new overstatement
introduced by a fix (summary intro: "we checked" dropped) and 1 older overstatement in configs/sources.yaml (rendered in
the report appendix). Two optional wording points remained: the out-of-state comparison in Q24, and "strongest large
EMI subject" in Q6, summary 6.1 and the dashboard. All five were fixed the same way as the report wording.
