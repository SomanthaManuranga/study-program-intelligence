# Fact-check of the plain-English summary (Step 57, preliminary)

Fresh-context reviewer agent: every factual sentence of the built summary (`reports/final/project_summary.md`):

- Section 1 (including its table) and Sections 4-12: full check.
- Sections 2-3: light check; their full review is in [summary_review_1-3.md](summary_review_1-3.md).

Each sentence was checked against the evidence docs, the technical report, the decision log, the configs, the key
numbers and the git log.

**Result: 232 sentences checked. 190 supported, 25 caveat, 6 overstated, 4 unsupported, 7 wrong.**

- Every number matches `reports/key_numbers.yaml`.
- The worked examples add up: 0.65-0.86 x 25 = 16-21; 1.20-1.28 x ~60 = 72-77; 39 - 7 = 32; 39 / 5,501 is about
  0.7 %.

All non-supported sentences were fixed in `docs/summary/*.md` (column "Fix applied").

| Section | Sentence (short) | Verdict | Evidence | Fix applied |
|---|---|---|---|---|
| 1 table | computer science "the only large faculty subject still growing in Bavaria" | caveat | evidence_forecast.md: Bavarian Informatik 4,309 (2023) -> 4,110 (2024) | "grew in Bavaria 2019-2024, with a dip in 2024" |
| 1 table | "at most 31 % of security" | overstated | evidence_fit_modules.md: range 18-39 %, TF-IDF 47 % | "about a third of the security content" |
| 1 table, 6.4 | "mostly in Nuremberg and Regensburg" | unsupported | evidence_outlet_jobs.md: "(Nuremberg and Regensburg fall inside)" | "an area that includes Nuremberg and Regensburg" |
| 4 | "Most of them are official statistics, which count everyone" | overstated | only Destatis and the Bavarian office are full counts | "Most come from public offices; the core counts are official statistics" |
| 4 table | Destatis "count of all students" | caveat | winter semesters only | "students starting in the winter semester" |
| 4 table | KMK "used for planning" | unsupported | used only as a growth index | "official forecasts of the education ministers" |
| 4 table | student review "used only for our high estimate" | wrong | the middle case is the geometric mean of low and high | "sets our high estimate and so also the middle one" |
| 4 | "did not work around it; used another permitted route or left the data out" | caveat | GENESIS via personal token; manual downloads where robots.txt blocks automation | own accounts / downloads by hand / left out |
| 4 | "every number ... from one generated list" | overstated | distances, years, small counts are typed (01_method.md) | "every statistic" |
| 5 | hiring-panel analogy "We did the same" | overstated | 02_funnel.md: screening filters committed with the screening | weights and kill rules in advance; screening filters on the day of the screening |
| 5 | "32 bachelors and 34 masters within 150 km" | caveat | raw title matches | "offers" |
| 5 caption | "rules written in advance" | overstated | as above | caption reworded |
| 5 | robotics "50 % of its core topics are already taught at OTH" | wrong | overlap_test.md: 50 % in one programme, 7 of 8 across OTH | "in one OTH programme, the AI bachelor" |
| 5, 9 | "scoring scales for five of the six points" written late | caveat | scores.yaml (Step 49) also has the student-number half of demand | "and part of the sixth" |
| 5 | even-range rule "came after the first ranking" | wrong | evidence_funnel.md: widening rule before, symmetry after the first run | split into the two rules |
| 6.1 | "still growing: in Bavaria by 6.1 % a year" | caveat | dip in 2024 | "with a dip in 2024" |
| 6.1 caption | "stay above its 2024 level" | caveat | 2025 dip | "back above ... after the 2025 dip" |
| 6.2 | "each Bavarian university of applied sciences" | caveat | 17 state HAWs, by region | "state-run ... by region" |
| 6.2 | catchment "closer to OTH than to its nearest competitors" | caveat | competitors = cyber programme locations; Regensburg 1,694 of 5,501 | "nearest universities with a cybersecurity programme"; Regensburg third added |
| 6.2 | middle "lies between the two" | caveat | geometric mean, a choice | "our choice, not a model result" |
| 6.3 | "always counted too much" | caveat | 4 of 4 errors false "covered" | "all four of its mistakes"; "probably on the high side" |
| 6.3 | "at most 31 %" | overstated | as for the table | "about a third (18-39 % by competitor)" |
| 6.3 | professorships, lab engineer, lab "would close the gap" | caveat | plus teaching assignments for law and governance | outside teachers added |
| 6.3 | "Sure ... checked by hand" | caveat | sample of 20; methods agree on 74 % | "Fairly sure; checked a sample" |
| 8 | demand counts most "because the task was to attract students" | caveat | no reason per weight recorded (defence_qa.md Q21) | "no reason recorded; fits the task" |
| 8 | "weak evidence got a wide range instead of a single value" | wrong | every score has low/central/high | "every score has a range; weak evidence a wider one" |
| 8 | "lead rests mostly on demand" | caveat | evidence_ranking.md: demand and labour relevance | "and next on job prospects" |
| 8 | "put robotics narrowly ahead (49 % / 50 %)" | caveat | "tie" | "about level" |
| 9 | robotics "no comparable programme to anchor" | caveat | 6 comparators, none with a published number | "no published student number" |
| 9 | "wider ranges instead of guessing" | wrong | assumed comparator intake 20-60 | "assumed 20 to 60 and widened its ranges" |
| 9 | blocked sources "We did not work around that" | caveat | GENESIS login timed out | "or our login did not work" |
| 10 | "Cyber Security" "what students search for" | caveat | evidence_demand_trends.md | "what people use most when searching" |
| 10 | start "avoid a year with few school leavers" | caveat | 2025 gap already past; no 2026/27 start | "that year is past; earliest realistic start 2027" |
| 10 (b) | robotics net new | caveat | assumed comparator intake | note added |
| 11 | cannibalisation "mainly takes students" | wrong | "the part taken from existing OTH programmes" | redefined as the part |
| 11 | catchment "area ... gets most of its students" | unsupported | evidence_catchment.md: geographic advantage, not market share | redefined |
| 11 | capture model "how far students live" | caveat | counts by school location | "go to school" |
| 12 | "one document per question" | wrong | 13 evidence docs | "several documents per question" |
| 12 | "Every method decision and why" | caveat | most with a reason | "most with the reason" |
| 12 | "rebuild ... run one command" | caveat | manual inputs needed | "once the files downloaded by hand are in place" |
| 3 (light) | "Earlier candidates were only screened on demand and competition" | caveat | embedded and part-time AI master also tested on kill rule 1 | "and two also on the overlap rule" |
| 3 (light) | "Section 5 says which" rules were added later | caveat | screening filters, 80 % bar | Section 5 now names both |

## Recheck of the changed sentences

The same reviewer rechecked all 54 changed sentences: 51 supported, 3 caveat, none overstated, unsupported or wrong. It
also found one unchanged sentence that no longer matched the corrected Section 4. All four were fixed:

| Section | Sentence (short) | Verdict | Fix applied |
|---|---|---|---|
| 6.2 | "About a third of them live in and around Regensburg" | caveat (counts are by school location) | "finish school in Regensburg or its county, where other universities are close by" |
| 9 | robotics "no published student number for any comparable programme" | caveat (THI handbook figure unverifiable) | "could not obtain a verified student number" |
| 10 (b) | "no comparable programme publishes one" | caveat | "an assumed range ... could not obtain a verified figure" |
| 11 | key numbers "every number in this summary" | overstated | "every statistic" |
