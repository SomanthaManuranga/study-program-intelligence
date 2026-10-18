# Claim B: capture

<!-- Evidence: docs/evidence_catchment.md, docs/evidence_capture.md. -->

**Claim:** OTH can win enough first-year students for a viable cohort in the central and high scenarios, given its
location and its competitors.

## OTH has its own regional pool

We counted school leavers with a university entrance qualification by Bavarian county (school years 2013/14 to
2023/24) [@lfstat2024schools] and assigned each county to the nearest of OTH and the three nearest cyber competitor
locations (TH Deggendorf, TH Ingolstadt, Nuremberg/Erlangen). OTH's **own pool** is {{own_pool_exact}} qualified
school leavers a year, {{own_pool_share_by}} of Bavaria; {{own_pool_fosbos_share}} of them come through the
Fachoberschule / Berufsoberschule route that typically leads to universities of applied sciences
([evidence_catchment.md](../../docs/evidence_catchment.md)).

- **Little overlap with Deggendorf, much with Nuremberg.** {{catchment_closer_to_oth}} of OTH's 100-km catchment is
  closer to OTH than to Deggendorf, but only {{closer_than_nuernberg}} is closer to OTH than to Nuremberg/Erlangen. The
  only dedicated cyber programme there is FAU's part-time online bachelor, so for a full-time programme the nearest
  competitors stay Ingolstadt and Deggendorf.
- **Regensburg is the swing area.** {{regensburg_part}} of the own pool are in Regensburg city and county, next to
  OTH Regensburg and the University of Regensburg; counting OTH Regensburg as a competitor, the own pool is
  {{pool_without_regensburg}}.
- **The pool shrinks slowly.** It fell {{own_pool_trend}} since 2013/14, a little faster than Bavaria. The G9 reform
  leaves a gap year (about {{pool_g9_gap}} in 2024/25); after it the KMK projection [@kmk2025schools] implies about
  {{pool_2030}} by 2030. A first intake should therefore not fall into the gap year.

## Calibrated distance decay

How strongly distance deters students was estimated from real flows: the Bavarian student statistics report, for
each of the state universities of applied sciences, where its students obtained their entrance qualification
[@lfstat2025students]. A doubly-constrained gravity model fits these flows with distance decay
{{gravity_beta}} ({{gravity_r2}}; values almost as good as the best fit: {{beta_band}}). The fit is good at the
level of the seven administrative regions, but it under-predicts how local students are: for OTH the model gives a
home-region share of {{home_share_model}} against an actual {{home_share_actual}}.

## Anchoring on comparable programmes

The demand side cannot be modelled in absolute terms: the share of cyber students among computer-science entrants is
unknown, and an uncalibrated estimate implied {{thi_implied}} first-years for TH Ingolstadt's cyber bachelor, whose
planned capacity is {{thi_cyber_capacity}} with no admission limit [@thi2025csi]. We therefore used the model only for
**relative capture**: across all model variants OTH would attract {{rel_capture_thi}} TH Ingolstadt's intake.
Absolute numbers come from two anchors:

| Scenario | Anchor | Year 1 | Steady state (year 3) |
|---|---|---|---|
| Low | TH Ingolstadt intake = its planned capacity ({{thi_cyber_capacity}}) | {{year1_low}} | **{{cyber_bsc_gross_low}}** |
| Central | geometric mean of low and high (a choice) | {{year1_central}} | **{{cyber_bsc_gross_central}}** |
| High | TH Deggendorf intake {{deg_cyber_anecdote}} (one student review; weak) | {{year1_high}} | **{{cyber_bsc_gross_high}}** |

The ramp-up to the steady state over the first three intake years is an assumption. For
comparison, OTH's own first-year intake in engineering sciences including Informatik was {{oth_eng_firstyears}} in
winter 2024/25 ([evidence_capture.md](../../docs/evidence_capture.md)).

**Plausibility check, not an anchor.** No university of applied sciences with a dedicated cyber bachelor publishes
first-years per programme. Two research universities do: Ruhr-Universität Bochum had {{rub_cyber_ba_firstyears}}
first-years in IT-Sicherheit/Informationstechnik (2024), and Saarland University {{uds_cyber_ba_firstyears}} in its
German-taught Cybersicherheit bachelor (WS 2025/26). TH Deggendorf's {{deg_cyber_anecdote}} lies inside that range and
TH Ingolstadt's planned {{thi_cyber_capacity}} at its low end; the check does not narrow the range.

**A strong competitor in security.** TH Deggendorf's ministry contract 2023-2027 names its technology transfer centre
for digital security in Vilshofen, which supports Bavarian firms on IT security
([evidence_ministry_contracts.md](../../docs/evidence_ministry_contracts.md)). TH Deggendorf is therefore a stronger
regional competitor in security than its programme list shows, and OT security is no differentiator against it.

{{fig:f04_capture}}

## Is a cohort viable?

No Bavarian rule or guideline on a minimum first-year cohort was found. We assume **{{min_cohort}} first-years a year**
as the minimum for running a bachelor; TH Ingolstadt plans its cyber bachelor for {{thi_cyber_capacity}}. In the
central and high scenarios the programme clears this bar from the first year; in the low scenario it reaches it only
at steady state, and only just.

## Assessment

Claim B holds in the central and high scenarios and is borderline in the low one. The model structure is robust
(relative capture varies little across the model variants); **the weak point is the anchors**: a planned capacity and
one anecdotal intake, because none of the comparable programmes we checked publishes its intake. One measured intake figure from TH
Ingolstadt or TH Deggendorf would cut the range by about half. **Strength: medium.** Students from outside Bavaria are
not modelled, but they matter little for this estimate: {{oth_outside_bavaria}} of OTH's German students gained their
school-leaving certificate outside Bavaria (Bavarian universities of applied sciences: {{haw_outside_bavaria}}), about
as many as at TH Ingolstadt ({{thi_outside_bavaria_approx}}, approximate) and TH Deggendorf
({{thd_outside_bavaria_approx}}). Because the estimate is relative to those two universities, leaving them out shifts it
by a few per cent at most.
