# Evaluation criteria: capture, cost and demand pre-registration for the three-level answer (fixed before building)

Task: (1) first-years for robotics path B, AR/VR and the strongest candidate that fails only F4 (as a reference) with
the capture pipeline cyber uses (catchment, Huff, cannibalisation, German and international split, low / central /
high, year 1 and steady state); candidate inputs from config with their source; the German feeder trend (-3.3 %/yr for
robotics) feeds the projection; the low case compared with the assumed minimum cohort of 20. (2) Each level's resource
need in professor-equivalents, with the legal teaching load of Bavarian HAW professors quoted from the regulation;
new modules (SWS), teaching assignments, new professorships and the lab engineer; cost per expected first-year
(central and low) for level (b) robotics and level (c) cyber; lab and equipment cost "not estimated" unless sourced.
(3) configs/demand_thresholds.yaml and a short section in docs/evidence_tie_break.md, committed and pushed before the
1 Nov snapshot, commit hash in the decision log: for robotics path B vs AR/VR and for robotics vs the minimum-cohort
level, which job-ad and Trends results favour, are neutral or go against, and what overall result downgrades robotics
from "conditional candidate" to "not recommended"; the 3-of-4 rule unchanged. (4) First-years, professor-equivalents
and "what would change this answer" in the three-level table.

| # | Criterion | Target |
|---|---|---|
| E1 | Cyber numbers reproduce unchanged through the shared code path | regression test passes |
| E2 | Robotics path B: low / central / high, year 1 and steady state, German and international; the -3.3 %/yr trend is a model input | test passes |
| E3 | Rolling-origin backtest of robotics' subject pool reported with MASE; if MASE > 1, said plainly | reported |
| E4 | Teaching load quoted from the regulation with its paragraph; every professor-equivalent figure recomputed by a test from config | test passes |
| E5 | demand_thresholds.yaml committed before any 1 Nov data exists (test of commit order or timestamps); every threshold numeric | test passes |
| E6 | Fresh-context reviewer attacks the cost comparison ("is cost per student misleading for small cohorts?"); attack and answer recorded | recorded |
| E7 | All tests pass | all pass |
| E8 | Full fresh-context claim review of every changed doc, no exceptions | 0 wrong, 0 unsupported, 0 overstated |

Iterate: at most 3 rounds; if a criterion still fails, stop and report; never loosen a criterion. Push to soma/rescope
when all pass (the demand thresholds are pushed before the 1 Nov snapshot, as the task requires).
