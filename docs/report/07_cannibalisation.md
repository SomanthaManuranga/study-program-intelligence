# Incrementality: cannibalisation and regional benefit

<!-- Evidence: docs/evidence_cannibalisation.md, docs/evidence_ranking.md (all options), docs/overlap_test.md,
docs/kill_rules.md. -->

A new programme helps OTH only to the extent that its students would not otherwise have enrolled at OTH anyway. This
section splits the expected students of each option into three groups:

- **(a) taken from existing OTH programmes** (cannibalisation);
- **(b) won from other universities** (net new to OTH);
- **(c) kept in the region**: the part of (b) from OTH's own region whose alternative lay outside it.

## Method

The capture model of Section 4 was run twice, without and with the new programme. In a Huff model a new alternative
draws students from every existing alternative in proportion to its share [@huff1964], so the new programme's students
can be traced back to where they would otherwise have gone. OTH's own related programmes enter the model as
alternatives: for the cyber bachelor Industrie-4.0-Informatik and Medieninformatik, the two bachelors with an
information-security focus. The same model was run for the other two options, with the anchors available for each (one capacity for the
master, an assumed comparator intake for robotics)
([evidence_cannibalisation.md](../../docs/evidence_cannibalisation.md),
[evidence_ranking.md](../../docs/evidence_ranking.md)).

## Cybersecurity B.Sc.

| Scenario | Gross first-years | (b) Net new to OTH | (c) Kept in the region |
|---|---|---|---|
| Low | {{cyber_bsc_gross_low}} | {{cyber_bsc_netnew_low}} | {{cyber_bsc_kept_low}} |
| Central | {{cyber_bsc_gross_central}} | {{cyber_bsc_netnew_central}} | {{cyber_bsc_kept_central}} |
| High | {{cyber_bsc_gross_high}} | {{cyber_bsc_netnew_high}} | {{cyber_bsc_kept_high}} |

- **Most students would be new to OTH:** {{netnew_share_range}} across the model variants (central
  {{netnew_share_central}}). Only {{cyber_bsc_from_oth_range}} would come from OTH's own programmes.
- **Regional benefit:** {{kept_share_range}} of the students would come from OTH's region and would otherwise study
  in Ingolstadt, Deggendorf, Würzburg, Neu-Ulm or Munich.
- **Stress test.** The model only sees programmes with security in the title or focus areas; a student who would
  otherwise take OTH's AI or electrical-engineering bachelor is not counted in (a). If cannibalisation were
  {{stress_share}}, about twice the model's maximum, net new first-years would be {{stress_netnew}}: the central case would
  sit at the assumed minimum cohort.

## Kill rule 1 rechecked

Kill rule 1 drops a candidate if {{kill_rule_1_threshold}} of its core modules already appear in one OTH programme at
the same level. It was set before scoring and contains no separate cannibalisation threshold; none was added
afterwards. Cannibalisation instead enters the ranking through the model half of the demand criterion, which counts only
students new to OTH. The cyber bachelor passes clearly: of the security modules of the draft curriculum, {{cyber_bsc_core_overlap}}
exist in one OTH bachelor, and the module comparison finds at most {{module_cover_ii_mi}} of a cyber bachelor's
security ECTS in Industrie-4.0-Informatik and Medieninformatik together.

## All three options

| Option | Gross first-years | From OTH programmes | Net new to OTH | Kept in the region |
|---|---|---|---|---|
| Cybersecurity B.Sc. | {{cyber_bsc_gross_low}} / {{cyber_bsc_gross_central}} / {{cyber_bsc_gross_high}} | {{cyber_bsc_from_oth_range}} | {{cyber_bsc_netnew_low}} / {{cyber_bsc_netnew_central}} / {{cyber_bsc_netnew_high}} | {{cyber_bsc_kept_low}} / {{cyber_bsc_kept_central}} / {{cyber_bsc_kept_high}} |
| Cyber/OT M.Sc. | {{msc_gross}} | {{msc_from_oth}} | {{cyber_msc_netnew}} | {{msc_kept}} |
| Robotics + AI B.Sc. | {{rob_gross}} | {{rob_from_oth}} | {{robotics_bsc_netnew}} | {{rob_kept}} |

{{fig:f05_cannibalisation}}

- **The master** draws more from OTH ({{msc_from_oth}}), mainly from AI for Industrial Applications and IT und
  Automation, and keeps few students in the region (see the table; in the master model the origins are the Bavarian universities
  of applied sciences, weighted by their students). It has one intake anchor (TH Ingolstadt's Cloud Applications und Security
  Engineering master, capacity {{msc_anchor}}); its high end was widened by the bachelor's spread.
- **Robotics** has **no verified intake anchor**: no public capacity or intake figure for a Bavarian robotics bachelor
  could be obtained, so a comparator intake was assumed and its range taken over all model variants. Its model
  cannibalisation looks low, but a Huff model understates switching between near-identical programmes, and robotics
  overlaps {{robotics_overlap}} with OTH's KI B.Sc. on the same campus. With {{stress_share}} of its students from OTH, only
  {{robotics_netnew_cannib50}} a year would be new to OTH, below the assumed minimum cohort in the low and central case.

## Assessment

The cybersecurity bachelor is **incremental**: about four in five of its students would be new to OTH, and about
one in seven would otherwise leave the region. Robotics carries a high cannibalisation risk that the model does not capture (its core overlap with the KI B.Sc.);
in the model itself the master draws most from OTH. **Strength: medium.**
The model assumes fixed demand (it creates no students who would not have studied at all), covers Bavarian origins
only, and does not see general OTH programmes without a security focus (hence the stress test).
