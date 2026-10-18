## A3 Kill rules, scoring anchors and score sheet {-}

<!-- Kill rules and anchors summarised from docs/kill_rules.md and configs/scores.yaml; score table generated. -->

**Kill rules** (fixed {{rules_fixed_date}}, before any candidate was scored; [kill_rules.md](../../docs/kill_rules.md)).
A candidate is dropped if any rule applies:

1. **Overlap:** {{kill_rule_1_threshold}} of its core modules already appear in one OTH programme at the same level,
   and no credible differentiator remains.
2. **Feasibility:** its feasibility rating is 1 (no staff, no lab, no accreditation path).
3. **Trend:** entrants in the related field across Germany fell in each of the last five years, and the KMK scenario
   shows no recovery.
4. **Pipeline (master only):** bachelor graduates in related fields are falling and too few are in the region. No
   numeric threshold was set; the rule was applied as a direction check (graduates rising, so it does not apply).
5. **Scope:** at most three candidates per level go into full dossiers.

Added in Step 49 (after the evidence was collected, before the first ranking run): *weak evidence widens a score's
range; it does not raise the centre.* Amended on 17 Oct, after the first run (git: ranking 23:36, amendment 23:40): the widened range must be symmetric
around the centre (the earlier skewed range is reported as a sensitivity).

**Scoring anchors (1 to 5, 5 = best).**

| Criterion | 5 | 3 | 1 |
|---|---|---|---|
| Student demand | related entrants (or, for a master, graduates) rose over five years and the catchment supports a cohort | - | related entrants fell over five years and the catchment is too small |
| Labour relevance | shortage occupation at the matching level, above-baseline Bavarian job-ad share and many ads within 100 km | two of these | none |
| Institutional fit | EMI already teaches most of the specific core and has the staff | a minority of the core, staff gaps closable by one or two hires | almost nothing, no related staff |
| Feasibility | no new professorship or lab | one or two new professorships and one new lab | no staff, no lab, no accreditation path (kill rule 2) |
| Differentiation | no dedicated programme within 150 km | a few within 150 km but none very close, or a profile none of them has | many within 150 km, profile already offered nearby |
| Regional contribution | computed from the students kept in the region (Section 7) | | |

Student demand combines a computed model score (net new first-years, Section 7) with a trend score. The exact
thresholds are in `configs/scores.yaml`.

**Score sheet** (proposed by the AI assistant, reviewed and changed by the team; `configs/scores.yaml`):

{{table:scores}}
