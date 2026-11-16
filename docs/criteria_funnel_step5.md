# Criteria for funnel Step 5 (job ads)

Written and committed before the Step 5 code is written. Step 5 applies the rule block `labour` of
`configs/funnel.yaml`: keywords from the titles of each type's programmes, and job-ad counts from the job board of
the Federal Employment Agency. It removes no unit and computes nothing of Steps 6 to 8.

| # | Criterion | Target | How it is checked |
|---|---|---|---|
| L1 | Keywords come from the rule, not from a person | phrases from the cleaned titles of the fitted members, split as the rule says; generic phrases dropped by the stop list and by the 5 % rule; the 3 phrases with the highest share that occur in 2 or more titles, else the parts of the member nearest the centroid; nothing added or struck by hand | test: recomputed for a sample of types; reviewer |
| L2 | Keywords are fixed before any count is seen | the keyword file is committed with its hash before the first request | `git log`, hash in the output |
| L3 | Every keyword in every region | Germany, Bavaria, 100 km around Amberg; each list fetched on one recorded day; a count of 0 is valid, a reply without a total is an error and is asked again; what is still missing is named | test on the count table |
| L4 | Polite and allowed | robots.txt checked, the project's User-Agent, at least 2 s between requests, raw replies kept | code, log |
| L5 | Measure as the rule says | per unit the median over its keywords of the count within 100 km; the largest keyword count as the stress value; Bavaria's share of the German count next to the share for all ads; a type without a keyword or without counts has a missing input | test |
| L6 | Both lists | the primary and the stress list are processed by the same code; if the stress list cannot be finished on the day, that is said and its requests are repeated on one later day | output |
| L7 | Reviewed | a fresh-context reviewer compares code and rule, recomputes keywords and measures, and checks every number in the notes; no open blocker, no wrong number | reviewer |
| L8 | The repository works | `python -m pytest` passes completely | test run |

The catalogue has no language field, so no English keyword is paired (stated limit). Soma strikes no keyword
(no hand work); off-topic keywords are named in the notes instead. If a criterion still fails after 3 rounds, the
step stops and Soma is told. No criterion is loosened.
