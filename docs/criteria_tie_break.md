# Evaluation criteria: hand check and demand tie-break (fixed before building)

Task 1: an English side-by-side sheet of every adapted-module (E2) verdict behind the AR/VR and robotics path-B gate
passes (candidate module, EMI module, ECTS, first 300 characters of both texts, proposed verdict) for Soma to confirm
or reject; F1-F4 recomputed for both after Soma's answers. The ranking is not recomputed before the hand check is in.

Task 2: break the AR/VR vs robotics path-B tie on demand, not on fit: Destatis first-years for the closest subjects
(German and international, Bavaria and Germany, 2019-24), competitor counts and distances from the full catalogue,
international demand, existing job-ad counts for matching keywords, XR hardware (public headset count, or an estimate
for a cohort of about 40 as a stated limitation); exact Google Trends terms and settings for Soma's manual download;
the new keywords in configs/jobsuche.yaml for the 1 Nov snapshot. The conclusion becomes two-level: (a) existing
resources only (primary): AR/VR vs robotics path B, decided by demand; (b) with investment: Cybersecurity B.Sc. as the
baseline result, with what about two professorships and a lab would buy.

| # | Criterion | Target |
|---|---|---|
| E1 | Every demand cell is filled or says "no data + reason" | 100 % of cells |
| E2 | Every new number is in reports/key_numbers.yaml and matches its source doc | 100 % |
| E3 | The tie decision states which demand signals favour which option and how strong each is; no single signal decides alone | stated for every signal; decision holds without any one signal |
| E4 | A fresh-context reviewer argues the opposite conclusion; attack and answer recorded in the evidence doc | recorded |
| E5 | All tests pass, with new tests for new code | all pass |
| E6 | A fresh-context claim review | 0 wrong, 0 unsupported, 0 overstated |

Iterate: fix and re-check, at most 3 rounds; if a criterion still fails, stop and report; never loosen a criterion.
Push to soma/rescope only when E1, E2, E5 and E6 pass. Report: scorecard, the demand comparison table, open risks.
