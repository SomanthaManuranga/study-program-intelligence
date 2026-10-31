# Argument brief: why a new EMI programme can attract many NEW students to OTH

Audience: the supervisor and the defence. Purpose: the complete argument chain with its numbers, each claim mapped to
its evidence, its strength and the strongest counterargument with the honest answer. Compiled 31 Oct 2026 from the
evidence documents and the deep-analysis layer (docs/evidence_deep_analysis.md); every number is stated in the named
source. The frame is the supervisor's binding constraint and the pre-registered three-level answer:

- **(a) strict existing-resources rule: no candidate passes** (closest: robotics path B, 15 ECTS of new modules by
  existing professors against the cap of 10 - the project's own operationalisation).
- **(b) lenient sensitivity: Robotics + AI B.Sc. path B** as a conditional candidate (condition: the faculty absorbs
  about 15 ECTS, about 18 scaled; the 1 Nov demand data can realistically only confirm it).
- **(c) with investment (outside constraint 1): Cybersecurity B.Sc.** - 2 professorships, 1 lab engineer, 1 lab.

The attraction argument below is the same chain for both candidate levels; where a number is candidate-specific it
is given for cyber (level c) first and robotics path B (level b) second.

---

## The chain in one sentence

OTH sits on a measured pool of its own that no nearby competitor serves for these profiles; the demand behind the
profiles is real even when measured honestly on German entrants only; the intake OTH needs is a small fraction of
that pool and below the share a named peer is reported to reach (an anecdote); most of those students would be NEW
to OTH, not moved from existing programmes; the job market pulls in these fields; and the main statements hold under
the project's own robustness checks (a specification curve over its own list of alternatives, a shrinkage model over
the same anchors, leave-one-out).

## Argument 1 - OTH has a pool of its own

**Claim:** there is a distinct regional pool of potential first-years that OTH, and no close competitor, serves.
**Numbers:** ~5,501 qualified school leavers a year in the own pool (counties closer to OTH than to Deggendorf,
Ingolstadt and the Nuremberg hub; 10.1 % of Bavaria), 18,630 within 100 km; 91 % of the 100-km catchment is closer
to OTH than to TH Deggendorf; 40 % come via FOS/BOS, the classic HAW route. Source: docs/evidence_catchment.md.
**Strength:** strong (official county statistics, sums verified by the parser's own arithmetic and the data-quality
gate). **Counter:** the pool shrank 19 % since 2013/14 and a third of it is the Regensburg area (3,807 without it).
**Answer:** the KMK path recovers the pool to ~5,300 by 2030 after the G9 gap, and Argument 4 shows the required
share is so small that even the no-Regensburg pool carries it (20 of 3,807 is 0.5 %).

## Argument 2 - the demand behind the profiles is real, measured honestly

**Claim:** the feeder demand grows (cyber) or at least holds (robotics), even when the growth is split honestly by
nationality. **Numbers:** Bavarian cyber-proxy first-years +5.9 %/yr 2019-24 (German only: +1.9 %/yr - Informatik is
the only large EMI subject that grew among German entrants); 4,936 in 2024; conservative KMK floor ~5,057 by 2030.
Robotics feeders: -0.6 %/yr overall, German -3.3 %/yr - stated as flat-to-falling, no growth story. Sources:
docs/evidence_forecast.md, docs/evidence_demand_split.md. **New (deep layer):** the demand CORRIDOR to 2030 from
each pool's own backtest errors: cyber first-years corridor 39.4-63.2 around the central 39, with a conservative
point of 42.7 that uses only the validated German path (drift, MASE 0.92) and holds the foreign pool flat; robotics
corridor 22.7-29.4 around 28.7. Source: reports/demand_corridor.md. **Strength:** strong for direction, medium for
levels. **Counter:** 80 % of the cyber growth is foreign students, and the foreign pool is unforecastable (best MASE
4.22). **Answer:** conceded and priced in - the conservative corridor point EXCLUDES all foreign growth and still
sits above the central case; nothing in the viability argument needs the foreign compounding.

## Argument 3 - the supply gap is measured, not asserted

**Claim:** within realistic commuting range the profile is scarcely offered. **Numbers:** cyber - 4 dedicated
bachelors within 150 km, none within ~80 km (THI at 82 km is the nearest full-time one); robotics - 5 within 150 km,
none within 80 km; AR/VR - 1 (Coburg). Hand-checked counts from the full catalogue (22,093 offers). Sources:
docs/theme_precision.md, docs/evidence_candidates.md, reports/data_quality.md. **New (deep layer):** accessibility
indices (distance-weighted leavers per unit of distance-weighted competition): cyber 24,644, robotics 13,696, AR/VR
50,433; and a neighbours check - no robotics-titled bachelor in Plzen, Austria's sites beyond 150 km
(docs/neighbours_check.md). **Strength:** strong. **Counter:** OTH's accessibility index relative to the nearest
competitor's own site is below 1 for cyber (0.77) and robotics (0.85) - Ingolstadt/Nuremberg sit in richer demand.
**Answer:** stated openly: OTH's case is not a better region but an UNSERVED own pool (Arguments 1 and 4); for the
candidate with the index above 1 (AR/VR, 2.07) the gate failed on other grounds, which shows the gate is doing its
job rather than chasing the nicest market.

## Argument 4 - the required share is modest against a reported peer value

**Claim:** the intake OTH needs is a small slice of its pool, below the share a peer is reported to reach. **Numbers:** the minimum
cohort of 20 equals 0.36 % of the own pool; the central cyber case (39) equals 0.71 % of the own pool and 0.21 % of
the 100-km pool; TH Deggendorf's reported ~60 first-years correspond to 1.07 % of its equivalent nearest-site pool
(5,595). Source: reports/capture_benchmark.md. **New (deep layer):** a Gamma-Poisson shrinkage model
over the published comparable intakes (THI 25, Saarland 44/42, Deggendorf ~60), mapped through the pre-registered
relative-capture envelope, puts 92.5 % of its predictive mass inside the pre-registered 21-75, median 39.2, and only
3.8 % below the minimum cohort; it is not independent of the anchors: THI 25 and Deggendorf ~60 are in its sample, and the two Saarland values are one research-university programme in two years, while Bochum is left out for being a research university. Source: reports/intake_model.md. **Strength:** medium (anchors stay a capacity and
an anecdote). **Counter:** no comparable programme publishes a measured intake; the whole level rests on two points.
**Answer:** conceded - it is the project's stated main limitation, the shrinkage model shows the range is consistent
with the few published values (which include the two anchors), and the first recommendation remains one measured intake from THI or Deggendorf, which
would cut the range by about half.

## Argument 5 - the students would be NEW to OTH

**Claim:** a new programme wins students OTH does not have today, instead of moving its own. **Numbers:** the Huff
cannibalisation model puts 73-86 % of first-years as net new to OTH (central 32.0 a year for cyber); the stress test
with double the model's worst internal draw (50 %) still leaves 19.5 central; about one in seven students is kept in
the region who would otherwise study elsewhere. Sources: docs/evidence_cannibalisation.md. **New (deep layer):** an
embedding-based profile concentrates OTH-internal substitution exactly where the model says - the two security-focus
informatics programmes for cyber (52.6 % of the profile), the KI family for robotics (41.3 %) - so the reading does
not depend on the title/focus rules alone. Source: reports/cannibalisation_similarity.md. **Strength:** medium
(model-based; OTH programme intakes are not public). **Counter:** Huff's proportional draw understates substitution
between near-identical programmes. **Answer:** that is exactly why the 50 % stress case is carried everywhere and
why robotics' 50 %-case numbers (14.3 central net new) are reported next to the base.

## Argument 6 - the job market pulls

**Claim:** graduates of these profiles are demanded, especially in Bavaria. **Numbers:** "Cyber Security" 851 ads in
Germany (Bavaria 30.9 % against an IT baseline of 22-25 %; "OT Security" 34.6 %), 191 within 100 km; Informatik is a
shortage occupation at bachelor level (2025); IT employment with a degree in Bavaria +34 % in four years; robotics
has the strongest local signal of the specialist keywords (58 ads within 50 km; only generic keywords such as
"IT-Sicherheit" with 113 are higher). Sources: docs/evidence_outlet_jobs.md. A probe
on 31 Oct confirmed the counts' continuity ("Cyber Security" 872 in Germany against 851/858 on 15/17 Oct) and that
the 1 Nov snapshot path works. **Strength:** medium (keyword counts, not vacancy statistics - stated). **Counter:**
keyword counts overstate specialist demand. **Answer:** conceded in the score (cyber labour scored 4, not the 5 the
anchors would allow) and cross-checked against the official shortage analysis and employment statistics.

## Argument 7 - the conclusion survives systematic attack

**Claim:** none of the above depends on a lucky analysis choice within the project's own list of alternatives.
**Numbers (all new, deep layer):** the ranking of the three baseline options (level (c); robotics path B is not
ranked against them) - its winner is first in **100 % of 192 specifications** (P(rank 1) 0.659-0.945, median 0.804; seeds move it by about
+-0.2 points; any single weight scaled 0.5x-1.5x keeps it between 0.858 and 0.958); the central intake clears the
minimum cohort in **100 % (cyber) and 91.2 % (robotics) of 2,880 capture specifications**; the pre-registered
specification reproduces the committed numbers exactly before any variant runs. Source: reports/spec_curve.md,
figure f09. Together with the existing checks: first in every leave-one-criterion-out run; 78.2 % under German-only
trends (honestly below the 80 % bar); claim-review rounds on every evidence doc. **Strength:** strong.
**Counter:** the spec grid is the project's own list, and specifications are correlated. **Answer:** stated in the
method; the grid covers every choice a reviewer attacked in the recorded opposing views, and the two dimensions that
drive most of the spread (pool trend, high anchor) are precisely the declared assumptions.

---

## What stays honestly weak, and what would change the answer

- The cyber LOW scenario clears the minimum cohort in only 55 % of specifications, robotics' low scenario never
  does: if intakes come in at the bottom of the range, the programmes are small. One measured competitor intake is
  the single most valuable missing number.
- Robotics path B carries no demand growth story (German feeders -3.3 %/yr); its case is feasibility within the
  constraint plus the local job signal, and it stands only under the lenient reading until the faculty confirms the
  ~15 ECTS of new teaching.
- The downgrade rule for robotics is pre-registered but, given the 17 Oct baseline (162 ads), practically out of
  reach: the 1 Nov data confirm rather than test it. The binding open condition is the faculty's answer.
- Level (c) remains outside the supervisor's constraint 1 by definition; its argument chain is the strongest, and it
  costs 2 professorships, 1 lab engineer and a lab.

## The one-slide answer for the defence

Under the constraint as operationalised, no candidate passes strictly; robotics path B stands as the conditional
existing-resources candidate, and the cybersecurity bachelor is what an investment would buy. For either, the
attraction logic is the same: a measured own pool of ~5,500 school leavers with no dedicated
competitor within ~80 km, a required share of well under one percent where a peer is reported (one student review) at about one percent, 73-86 %
of the intake new to OTH, a pulling job market - and, for level (c), a ranking that holds in 100 % of 192 specifications; the central intake clears 20
in 100 % (cyber) / 91 % (robotics) of 2,880 capture specifications, with its weak points quantified instead of
hidden.
