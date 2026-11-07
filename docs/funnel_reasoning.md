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
