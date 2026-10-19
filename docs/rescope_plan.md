# Re-scope plan: a new programme with EMI's existing resources (approved)

The supervisor's constraint 1 ("feasible with EMI's existing staff and labs, no new professorships or labs";
CLAUDE.md, Scope) changes the core of the analysis. Our current winner needs about two new professorships, a lab
engineer and a new security lab, so it does not meet the constraint. This plan says how we re-scope before any code
changes. The current results are kept as **"baseline: with new resources"**.

What stays: the four claims (demand, capture, fit, outlet), the success measure (new to OTH), the kill rules, the
MCDA weights, the Monte Carlo and every data source. What changes:

- a feasibility gate fixed before re-scoring;
- new candidates (recombination, rarity);
- a full-time filter;
- international students as a second target group.

## (a) Pre-registered definition of "feasible with existing resources"

**Unit of assessment.** A reference curriculum per candidate in OTH format:

- bachelor: 210 ECTS, 7 semesters incl. the practical semester;
- master: 90 ECTS incl. the thesis.

Coverage is measured on **taught ECTS only**: bachelor 210 - 30 (practical semester) - 15 (thesis with seminar) = 165;
master 90 - 30 (thesis) = 60. Practical semester and thesis are formats existing staff already run; counting them
would inflate coverage by a fifth.

**What counts as covered by existing resources:**

| Code | Category | Rule |
|---|---|---|
| E1 | Existing EMI module, unchanged | the module exists in a current EMI handbook; shared with another programme is fine |
| E2 | Existing EMI module, adapted | same responsible EMI professor (neutral label), same core topic, at most a third of the content new; match by the e5 model at the Step 41 threshold AND confirmed by hand |
| T | New module by teaching assignment (Lehrauftrag) | allowed up to 10 ECTS (bachelor) / 5 ECTS (master) |
| N | New module by an existing EMI professor | allowed only if that professor already teaches a module on the same topic; up to 10 ECTS (bachelor) / 5 ECTS (master) |
| - | Not allowed | a new professorship or lab-engineer post; a module that needs equipment not in EMI's public lab list; modules of other OTH faculties (not counted as covered, see R2) |

**The test (all must hold):**

| Rule | Bachelor | Master |
|---|---|---|
| F1 coverage: E1 + E2 | at least 80 % of taught ECTS (132 of 165) | at least 80 % (48 of 60) |
| F2 new content: T + N | at most 20 %, with T and N each within the limits above | the same |
| F3 labs | every lab-based module maps to an existing EMI lab (public lab list, `configs/sources.yaml` oth_web_labs) | the same |
| F4 no single source | at most 50 % of taught ECTS from any one existing OTH programme (kill rule 1 at module level) | the same |

- **Sensitivity (not the decision rule):** lenient F1 of at least 70 % and N up to 20 / 10 ECTS.
- **Teaching load:** N of at most 10 ECTS is about 8 SWS a year, under a quarter of one professor's annual load. We
  treat that as absorbable by reallocation; this is an assumption, stated as such.
- **Larger groups:** extra exercise or lab groups from shared modules cannot be measured with public data (limitation).

**Pre-registration.** The rule goes into `configs/feasibility.yaml` and the decision log and is committed BEFORE any
candidate is re-scored. The git timestamp shows the order, as for the kill rules. The thresholds above are a proposal
(decision R1).

**The tension to watch.** A programme built from existing modules easily overlaps one existing programme. F4 and kill
rule 1 keep that in check: the sweet spot is a programme that combines modules from several EMI programmes into a
profile none of them has.

## (b) Re-check of the current three options

| Option | What we know | Expected result under F1-F4 (to be tested, not assumed) |
|---|---|---|
| Cybersecurity B.Sc. (current winner) | draft curriculum: 110 of 165 taught ECTS reused or adapted (67 %), 45 new ECTS by new staff, 10 by teaching assignments; needs a new security lab | fails F1, F2 and F3; stays as the baseline |
| Reduced "existing-resources" cyber bachelor | built from EMI's existing security modules (EMI covers at most about a third of a cyber bachelor's security content; about four professors teach security) plus foundations | likely fails kill rule 1 / F4 against Industrie-4.0-Informatik and Medieninformatik (both already have an information-security focus); its security share would sit well below the 30-36 % of dedicated cyber bachelors, so it is hardly a cyber programme. Test formally (module-level overlap), then drop or report it as a specialisation of an existing programme |
| Cyber/OT M.Sc. | needs 30-40 new security ECTS (0.7-0.9 professorship); the strongest existing base is OT (industrial communication, CPS, embedded, functional safety) | the full version fails F1/F2; test a reduced **OT-security master** on the existing OT base plus existing security modules; watch the overlap with IT und Automation |
| Robotics + AI B.Sc. | 7 of 8 core topics already taught at OTH (title level); 50 % core overlap with the KI B.Sc. (at the kill-rule limit) | the most likely of the three to pass F1-F3; needs a module-level check against a reference curriculum (TH Kempten Robotik handbook, already downloaded) and a robotics-lab check; F4 against the KI B.Sc. is the risk |

The cannibalisation estimate becomes central: a programme built from existing modules tends to draw from OTH's own
students, and "new to OTH" is the success measure.

## (c) New candidate generation

### (i) Recombination candidates

1. **Complete the EMI module inventory.** We hold handbooks for 7 of 14 active EMI programmes, and E&IT covers only
   its first study section. Missing:
   - Digital Design B.A.
   - Elektro- und Informationstechnik B.Eng. (full)
   - Geoinformatik und Landmanagement B.Eng.
   - KI International B.Sc.
   - Medienproduktion und Medientechnik B.Eng.
   - Applied Research in Engineering Sciences M.Sc.
   - Educational Technology M.Eng.
   - Medientechnik und Medienproduktion M.Eng.

   OTH /fileadmin/ is closed to scripts, so this is a **manual download by Soma** (critical path, week 1). They are
   parsed with the existing `transform/modules.py`.
2. **Cluster the EMI modules.** Using the e5 embeddings from Steps 40-41, run agglomerative clustering with a fixed
   seed, choosing the number of clusters by silhouette. Each cluster is described by its module titles and top terms.
   The labels are proposed by Claude and reviewed by Soma.
3. **Form profiles.** A candidate profile is one or more clusters with at least 60 specialist ECTS (bachelor) or 30
   (master). It draws from at least two EMI programmes, with at most 50 % from any one, and is completed with
   existing foundation modules. Then F1-F4 are checked.
4. **Map each profile to the market.** Programmes with that profile in Germany come from a catalogue title and teaser
   search (supply, rarity). Demand comes from Destatis feeder subjects.

Hypotheses, not results: AI in media production (KI + Medien/Digital Design), smart energy informatics (E&IT energy +
KI Smart Energy), embedded/edge AI, industrial data science, geo-AI (Geoinformatik + KI).

### (ii) Rarity candidates

1. **Widen the catalogue.** The current harvest covers 13 study fields. Stralsund's Motorsport programme, the
   supervisor's example, is not in it, so rarity cannot be counted on it. Re-harvest the BA Studiensuche (same public
   API, robots.txt allows it, cached) for all study fields with any EMI link, or the whole catalogue if the API allows
   it (decision R4).
2. **Define a programme type** as the catalogue's own subject classification (`studienfaecher`), cross-checked with
   normalised title clusters.
3. **Rare** means offered full-time at no more than 3 institutions in Germany.
4. **Keep rare types EMI could teach.** Screen first by teaser-to-module similarity against EMI modules, then check at
   module level for the shortlist, with one public handbook of an existing programme of that type.

### Funnel for all candidates (written before running, in the same config)

1. Demand trend (filter 1): feeder subjects shown for all students AND German students, since both target groups
   count. Rare types without a feeder subject use search interest and get wider ranges (existing weak-evidence rule).
2. Supply gap (filter 2): Germany-wide and near OTH, full-time offers only.
3. Feasibility gate F1-F4 (new).
4. Kill rule 1 (overlap with one OTH programme), then kill rules 2-4.
5. Shortlist of at most 3-4, modelled and ranked as before.

## (d) International demand

- **Demand trend.** With both groups as targets, the all-nationality series is the base again. The German and foreign
  components (demand-split analysis) are shown next to it. The German-only sensitivity stays as a check.
- **Capture: two streams.**
  1. German / Bavarian school leavers: gravity model and anchors, as now.
  2. International first-years: not distance-based. The pool is OTH's own international intake (Destatis 21311-0011,
     foreign first-years per OTH campus and year; LfStat Tabelle 3.1, by subject group), both in hand. A new programme
     takes a share of it within a stated range. Low case for an English-taught bachelor: the Saarland data point (3
     against 42). The stream applies only to English-taught or bilingual variants. German-taught variants get no extra
     stream; their anchors already contain their foreign students. Decision R5.
- **Cannibalisation.** OTH's English-taught programmes (AI for Industrial Applications, KI International, the Weiden
  international programmes) are the "from OTH" source for the international stream.
- **Language and jobs.** Whether regional employers need German-speaking graduates is not measured (limitation).

## (e) Neighbouring countries

Only for the final shortlist, and only if the result could change, for example when a candidate's differentiation
rests on thin supply within 150 km. Light check of same-type programmes in the Czech Republic (Plzeň region) and
Austria (Upper Austria) in official catalogues, after a robots.txt check. Time-boxed to half a day; otherwise it is
stated as a limitation.

## (f) Pipeline steps and the baseline

**Baseline first.** Before any change:

- tag the repository (`baseline-new-resources`);
- commit `docs/baseline_new_resources.md`, a frozen table of the current shortlist, ranking, key results and resources
  needed;
- keep `configs/scores.yaml` as `configs/scores_baseline.yaml`.

The report keeps a short comparison section: baseline vs existing resources.

| Step | Change |
|---|---|
| ingest.studiensuche | wider harvest (rarity) |
| transform.modules | 8 more EMI handbooks (manual download) |
| analysis.recombination | **new**: EMI module clusters -> profiles |
| analysis.rarity | **new**: rare programme types |
| analysis.feasibility | **new**: gate F1-F4 from `configs/feasibility.yaml` |
| first_look, theme_verdicts | full-time filter; new candidates through filters 1-2 |
| demand_split | both groups as base, components shown |
| capture, options | international stream; anchors per new candidate |
| cannibalisation | new shortlist; international stream |
| ranking | new score sheet (Claude proposes, Soma reviews); baseline kept as a scenario |
| key numbers, figures, report, summary, Q&A, dashboard | rebuilt; report sections 0, 2 and 4-10 rewritten |
| claim review | fresh-context review of the rewritten texts |

Unchanged: forecast, labour, out-of-state share, intake plausibility check, job-ad snapshots.

## (g) Timeline (to the 4 Dec freeze)

| Week | Work | Done when |
|---|---|---|
| 20-26 Oct | approval of this plan and R1-R6; feasibility rule committed; baseline tag and table; Soma downloads the 8 handbooks; wider catalogue harvest | rule committed before re-scoring; handbooks parsed |
| 27 Oct-2 Nov | F1-F4 re-check of the three options and the reduced cyber variant; module clustering; rarity screen; **1 Nov job-ad snapshot** | verdicts for the three options; cluster labels reviewed by Soma |
| 3-9 Nov | all candidates through the funnel; shortlist of 3-4; reference handbooks for the shortlist; module-level coverage | shortlist with written verdicts |
| 10-16 Nov | capture with the international stream; cannibalisation; score sheet proposal; **15 Nov snapshot** | score sheet reviewed by Soma |
| 17-23 Nov | ranking and sensitivities (incl. baseline comparison); neighbouring-country check if needed; evidence docs | ranking robust or its weakness stated |
| 24-30 Nov | report, summary, Q&A and dashboard rewritten; claim review and fixes | review clean |
| 1-4 Dec | **1 Dec snapshot**; **4 Dec freeze** rerun | frozen numbers everywhere |

Then, as planned: Step 57 final (and the README update), Phase 5 (locked), Step 53 slides.

## Risks

- **Handbooks** are on the critical path; without them, recombination works on half of EMI's modules.
- **Anchors:** rare and recombined programmes will have no intake anchors, so their ranges will be wide. Capture can
  only be estimated by analogy.
- **No pass:** possibly no candidate passes F1-F4. We would report that plainly, show the lenient sensitivity, and say
  what the smallest new resource would be.
- **Time:** the report rewrite is large. Slides stay after the freeze.

## Decisions for Soma before we start

| # | Decision | Recommendation |
|---|---|---|
| R1 | Feasibility thresholds | strict rule as the decision (F1 at least 80 %, T and N at most 10 / 5 ECTS each); lenient (70 %, N at most 20 / 10) as a sensitivity |
| R2 | Count modules of other OTH faculties as covered? | no (conservative; EMI fit only) |
| R3 | Feasibility in the MCDA | keep weight 0.15 with the gate in front (passed options still differ in how much is new) |
| R4 | Width of the wider harvest | the whole Studiensuche catalogue if the API allows it; otherwise all fields with an EMI link |
| R5 | International stream | only for English-taught or bilingual variants |
| R6 | Baseline | git tag plus a committed comparison table; baseline also shown as a ranking scenario |
