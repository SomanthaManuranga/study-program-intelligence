# Funnel reasoning: why each programme stays or goes

The argument chain of the data-driven funnel. Rules: `configs/funnel.yaml`, `docs/funnel_preregistration.md`.
Generated tables: `reports/funnel/`. Each step answers one question, and its result is the next step's input.

## Step 0: which rules decide?

**Question.** How do we stop our earlier favourites from steering the result?

**Evidence.** The first rounds started from topic lists we wrote and six candidates we picked. A research review of
professional programme planning shows the opposite order: score everything first, then shortlist.

**Rule.** All thresholds were committed before any type was computed. A fresh-context reviewer attacked version 1 and
found five blockers; version 2 fixed them before any result existed. For example, "new to OTH" would have equalled
total first-years for every candidate.

**Result.** Commits `9cf9072` (rules), `895c10f` (amended), `66487a9` (subject table and discovery code),
`3e67a81` (screen code).

**What this means for OTH.** Any programme named at the end can be traced through written rules, not our preference.

**Strongest objection.** "You already knew the old results." True, and it is stated in the pre-registration. We cannot
forget them, so the old favourites get no special treatment and the screening rules are stress-tested.

## Step 1: is the data current?

**Question.** Are the inputs up to date?

**Evidence.** 22,093 programme offers in Germany; Destatis first-years by subject and nationality; EMI's current
modules; job-ad counts.

**Result.** The 1 Nov job-ad snapshot had been missed. The pre-registered fallback, the first complete snapshot after
that date, was run on 7 Nov: 92 counts, no errors, no missing totals.

**Open.** The Google Trends tie-break download is still missing. It is not used in this funnel's rules.

## Step 2: what kinds of programme exist?

**Question.** Without any list of ours, what programme types does the German market contain?

**Evidence.** 19,872 bachelor and master offers after removing duplicates; 14,902 full-time offers were clustered by
the content of their title, focus items and subjects.

**Rule.** Ten clustering settings were tested, each on 10 random resamples. The pre-registered rule picks the setting
with the highest share of offers in stable clusters.

**Result.**
- Selected setting: `min_cluster_size` 30, method `eom`. It gives 98 stable types, holding 61.6 % of full-time offers,
  with 14.4 % noise before the rare path.
- The rare path added 383 small groups (at least 2 institutions), because the supervisor welcomes rare programmes.
  These are not stability-tested and carry that flag.
- The types look real: data science and AI; mechatronics with robotics; business informatics; medical technology.
  Cybersecurity appears as rare types of its own, not as part of a broad informatics group.
- Agreement with the catalogue's own study fields is low to moderate (ARI 0.237), so the types add information beyond
  the official fields.
- **Our old lists were not natural groupings:** none of the 15 keyword lists in `analysis/themes.py` was recovered at
  Jaccard 0.5 or above. The closest were mobility/vehicle (0.43), AI/data (0.43) and aerospace (0.40).

**What this means for OTH.** The candidate set now comes from the market, including small profiles we had never
considered.

**Strongest objection.** "Clustering choices steer the result too." Yes: the selection rule favoured broader clusters
over the fine settings, and it is a judgement call. The next-best setting is in the stress tests. The TF-IDF cross-check
flags most small types as method-dependent (435 of 481), mainly because a 98-cluster k-means cannot reproduce very small
groups, so this check says little about rare types.

## Step 3: which types are open to OTH and within EMI's field?

**Question.** Which types could be a new programme at OTH at all?

**Evidence.** 838 type x level combinations were tested on four rules.

**Rule and result.** A combination can fail several rules at once.

| Test | Failed |
|---|---|
| OTH already has a close offer | 23 |
| More than 3 offers within 100 km | 80 |
| German student pool falling more than 3 %/yr, on a validated trend | 103 |
| Outside EMI's field (score below the bar) | 672 |

Primary list: **143** candidates (hash `4ae08c594e0925a5`). Stress list, with only the at-OTH test: 815 (hash
`87a6c338c240aefe`). Both are frozen; nothing is added by hand.

Examples of what the rules did:

| Type | Result | Reason |
|---|---|---|
| Data science and AI, bachelor and master | dropped | OTH's KI programmes are close; 10-11 offers within 100 km |
| Mechatronics with robotics, bachelor | dropped | OTH's Mechatronik und digitale Automation is close; 6 offers within 100 km; EMI score just below the bar |
| Medical technology, bachelor and master | dropped | an OTH offer is close |
| Cybersecurity (types 172, 301), bachelor | kept | 0-1 offers within 100 km; German pool +2.4 to +2.6 %/yr |
| Cybersecurity (type 172), master | kept | no offer within 100 km; German graduates +5.9 %/yr |
| Cybersecurity (type 301), master | dropped | EMI score 0.853, just below the bar of 0.855 |

**What this means for OTH.** Most of the market is outside EMI's field or already served. What remains is a mixed list,
which the next steps test on students, jobs and teaching.

**Weakest point, stated plainly.** The EMI score decides the most cases and is the weakest test:
- The calibration passed its pre-registered bar (AUC 0.839 on 11 EMI and 30 other OTH offers), but the scores sit in a
  very narrow range (EMI offers mean 0.855, others 0.846). The bar of 0.855 cuts 518 combinations on its own.
- It lets obvious non-EMI types through, such as teacher training and social work, and it stops some near misses.
- We do not change it after seeing the result. The stress list runs without it, and the real test of EMI's teaching
  comes at the feasibility gate.

**Logged deviation after seeing the list.** 27 of the 143 candidates are mainly teacher-training types. They lead to
state teaching qualifications, which a faculty cannot open with existing staff alone, so they are excluded from the
ranking. This rule was added after seeing the list; they remain in the stress list.

## Step 4: are students coming?

**Question.** Is the student pool behind each candidate growing or shrinking?

**Evidence.** Destatis first-years (bachelor) and graduates (master) in Bavaria, split by nationality, for each
candidate's mapped subjects. Rolling-origin backtests per pool.

**Rule.** The pre-registered measure is the log-linear trend 2019-2024 of German students. Foreign growth is shown but
never used as a point forecast.

**Result, for the candidates that reached the gate.**

| Candidate | Reference | German %/yr | Foreign %/yr | Own MASE |
|---|---|---|---|---|
| Informatik (type 380), bachelor | Westfälische Hochschule | +2.65 | +14.0 | 0.79 |
| Geoinformation (213), bachelor | BHT Berlin | +1.16 | +12.4 | 0.72 |
| Angewandte Informatik (237), master | Hochschule Mainz | +5.88 | +15.1 | 2.74 |
| Visual Computing (397), master | Universität Magdeburg | +6.15 | +15.2 | 2.86 |
| Cybersecurity (172), bachelor | Hochschule Esslingen | +2.36 | +13.8 | 0.74 |

**What this means for OTH.** The computing pools still grow among German students, slowly. The bachelor trends are
validated (MASE below 1). The master trends are not (MASE above 2), so they count only as direction.

**Strongest objection.** "These candidates share one pool." Yes: most computing types map to Informatik, so the trend
separates them little. Demand here tells computing from non-computing, not one computing type from another.

## Step 5: are there jobs nearby?

**Question.** Is there an outlet for graduates in OTH's region?

**Evidence.** BA job-ad counts within 100 km (7 Nov 2026), 557 counts, up to five keywords per candidate.

**Result.** Counts run from 144 to 5,710 for the candidates above.

**Weakest point, stated plainly.** This measure is unreliable as built. Keywords come from each type's text by script,
as pre-registered, and some are generic ("allgemein", "sicherheit"). The rule takes the largest single count, so one
generic word can dominate. Informatik's 5,710 is inflated in this way. At the ranking step, labour is reported with the
keyword behind it, and a stress test replaces it with occupation-specific keywords.

## Step 6: how many students would be new to OTH?

**Question.** How many first-years would OTH get, and how many of them are new?

**Evidence.** The Huff model on Bavarian school leavers by county (masters: Bavarian HAW students), with the type's
offers as competitors and the level from Destatis first-years per offer.

**Validation.** The level was checked against published intakes on the cyber types: anchor 29.6 first-years per offer,
median absolute log error 0.398 against a limit of 0.405. It passes narrowly, on one programme family only, and the
published values include a capacity and a single student review. No shrink factor was applied.

**Rule and result.** Of the 116 candidates left after the teacher-training exclusion, 35 miss the minimum cohort of 20
in the central case, and 81 go on. The top 20 by pre-gate score went to the gate.

| Candidate | First-years low / central / high | From OTH programmes, central | Net new, central |
|---|---|---|---|
| Informatik (380), bachelor | 15.3 / 30.6 / 61.2 | 57 % | 13.2 |
| Geoinformation (213), bachelor | 23.6 / 47.3 / 94.6 | 56 % | 21.0 |
| Angewandte Informatik (237), master | 14.6 / 29.1 / 58.2 | 24 % | 22.3 |
| Visual Computing (397), master | 11.8 / 23.5 / 47.0 | 78 % | 5.2 |
| Cybersecurity (172), bachelor | 17.6 / 35.2 / 70.4 | 27 % | 25.7 |

**What this means for OTH.** Several computing profiles could reach a cohort, but in the low case most do not.

**Weakest point, stated plainly.**
- The share taken from OTH depends on how many competitors a type has. A rare type has few, so OTH's own programmes
  take a large share in the model (78 % for Visual Computing with one offer, 12 % for Angewandte Informatik's type 89
  with 48 offers). This overstates cannibalisation for rare types, and it is not evidence that those students would
  otherwise have chosen OTH.
- Types with no Bavarian offer have a Huff scale of 1.0 by rule, so their level is not scaled to OTH's location.
- Geoinformation's level rests on a very small mapped pool of offers, so 47 first-years deserves caution.

## Step 7: can EMI teach it with what it has?

**Question.** Does each candidate pass the pre-registered rule F1-F4 on a real curriculum?

**Evidence.** One public module handbook per candidate, found by agents in the pre-registered order under robots.txt,
scaled to OTH's taught ECTS. Modules are matched to EMI's modules with the calibrated threshold. Automatic only: every
counted match still needs Soma's hand check.

**Result.** 20 candidates were tried, as the rule allows. Automatic pass (F1, F2, F4; labs are decided by hand):

| Rank | Candidate | Reference | F1 % | F1 compulsory only % | New ECTS, scaled | F4 % |
|---|---|---|---|---|---|---|
| 9 | Angewandte Informatik, master | Hochschule Mainz | 91.7 | no compulsory modules | 5.0 | 25.0 |
| 12 | Geoinformation, bachelor | BHT Berlin | 87.9 | 73.3 | 20.0 | 39.4 |
| 13 | Informatik, bachelor | Westfälische Hochschule | 93.5 | 89.2 | 10.8 | 32.7 |
| 18 | Visual Computing, master | Universität Magdeburg | 100.0 | no compulsory modules | 0.0 | 30.0 |

Failed, with the reason for OTH:

| Candidate | F1 % | Why it fails |
|---|---|---|
| Coaching und Führung, master | 0.0 | no EMI teaching |
| Heilpädagogik, master and bachelor | 0.0 and 9.8 | no EMI teaching |
| Kunsttherapie, bachelor | 5.6 | no EMI teaching |
| Soziale Arbeit management, master | 23.7 | little EMI teaching |
| Bau-Projektmanagement, bachelor | 30.3 | little EMI teaching |
| Digitale Verwaltung, bachelor | 32.0 | little EMI teaching |
| Cybersecurity, bachelor | 63.3 | security content needs new staff: 60.5 new ECTS scaled |
| Applied AI, bachelor | 62.0 | 62.6 new ECTS |
| Angewandte Informatik (types 89 and 237), bachelor | 73.1 and 69.7 | 44-50 new ECTS |
| Digitale Technologien, master | 72.7 | 16.4 new ECTS against a limit of 15 (T 5 + N 10) at the highest cap |
| Angewandte Informatik (89), master | 67.2 | 19.7 new ECTS |
| Umweltinformatik, master | 17.4 | little EMI teaching |

Two candidates have no reference and need a manual download: AI and Robotics master (Hochschule Hof: robots.txt blocks
the module host and the handbook folder returns 403) and Informatik - Smart Systems bachelor (Frankfurt UAS: site
relaunch; pages announced for 16 Nov 2026).

**What this means for OTH.** This is the first step that truly separates the candidates. The false positives of the EMI
score fall away, and cybersecurity fails again for the same reason as in the baseline: EMI lacks its security teaching.

**Weakest point, stated plainly.**
- The two master passes have no compulsory modules, so the curriculum is filled from elective pools, best covered
  first. That is optimistic by construction: 100 % for Visual Computing does not mean EMI could run that programme.
- The result depends on the reference. General informatics gives 93.5 % with one handbook and 69.7 to 73.1 % with
  others. Second references are therefore being added before the hand check.
- Module content was extracted by agents up to 600 characters, while the threshold was calibrated on longer texts.

**Process slips, logged.** While finding handbooks, agents made one request to a host whose robots.txt disallows it
(Hochschule Hof; nothing from the reply was used) and a few fetches before the robots check; all those hosts were
allowed when checked. The Kiel handbook was replaced because it listed only 67 % of its ECTS.

**Second references.** The pre-registered check on a second curriculum changes the picture:

| Candidate | First reference, F1 % | Second reference, F1 % |
|---|---|---|
| Informatik, bachelor | 93.5 (Westfälische Hochschule) | 88.1 (Hochschule Darmstadt): still passes |
| Geoinformation, bachelor | 87.9 (BHT Berlin) | 60.9 (KIT): fails |
| Angewandte Informatik, master | 91.7 (Hochschule Mainz) | 58.3 (Hochschule Wismar): fails |
| Visual Computing, master | 100.0 (Universität Magdeburg) | no second offer in the type |

## Where the funnel stands: a validity problem found before the hand check

**The Informatik pass is partly an artefact.** Informatik (type 380) shows 0 offers within 100 km, but this holds only for
its small cluster of 2 offers. In the catalogue, 15 bachelors with Informatik or Computer Science in the title lie within
100 km of OTH, including OTH Regensburg, TH Nürnberg, FAU Erlangen-Nürnberg, Hochschule Hof, TH Ingolstadt, Universität
Bayreuth and Universität Bamberg. Clustering split general informatics across many types, so supply measured by cluster
membership understates real competition.

**Why it matters.** The same weakness can affect every rare type, including cybersecurity (0-1 offers within 100 km by
type). This is a failure of the supply test as pre-registered, so the funnel's list is not yet trustworthy, and the
ranking and the hand check should not proceed on it.

**Proposed correction, for Soma's decision.** Measure competition by content, not by cluster: count offers near OTH whose
text is close to the candidate's centroid, with the radius fixed in advance. Then rerun steps 3-7 by script. This
tightens a test after seeing a result, and it would be logged as such.
