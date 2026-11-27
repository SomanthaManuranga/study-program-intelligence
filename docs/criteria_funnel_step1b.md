# Criteria for funnel Step 1b (a neutral matching threshold)

Written and committed before any similarity or threshold of this step is computed.

## Why

The threshold of 0.285 (`feasibility_gate.covered_threshold`) was calibrated on reference modules of seven
cybersecurity and robotics programmes, the candidates of the earlier analysis. A tool tuned on the old favourites
does not belong in an analysis that must not favour them. The threshold is therefore calibrated again on EMI's own
module handbooks only, while no programme type and no candidate exists.

## Procedure (fixed here; not changed after the value is seen)

1. **Data:** `data/interim/modules_emi_2026.csv` only. No handbook of another university is read.
2. **Text and vectors, as the gate will use them:** the module text is `clean(text, title)` of
   `analysis/module_gaps.py`; the encoder embedding is centred per handbook file. Step 7 uses the same function for
   the reference curricula.
3. **Same module in two handbooks:** two modules with the same normalised title (lower case, brackets removed,
   umlauts written out, punctuation removed) in two different handbook files and two different programme sets.
4. **Copies are left out:** a pair whose cleaned texts share at least 90 % of their words (token Jaccard >= 0.9) is a
   copied description and says nothing about matching by content.
5. **Anchors:** every module that has at least one same-title partner that is not a copy.
6. **Positive value of an anchor:** its highest similarity to a same-title partner that is not a copy.
7. **Negative value of an anchor:** its highest similarity to any module in another handbook file whose title shares
   no content word with the anchor's title. Content words are the words of the normalised title with at least 3
   letters, without the generic words listed in the code (for example "grundlagen", "einfuehrung", "praktikum",
   "projekt", "modul", "seminar"). This is the hardest wrong match, as in the earlier procedure.
8. **Threshold:** the value that maximises true-positive rate minus false-positive rate (Youden), as before.
9. **Uncertainty:** 1,000 bootstrap resamples of the anchors (seed 42); the 2.5th and 97.5th percentile of the
   threshold are reported.
10. The design check that preceded this file counted same-title pairs and copies (190 pairs, 74 copies, 121 anchors)
    and computed no similarity.

## Criteria

| # | Criterion | Target | How it is checked |
|---|---|---|---|
| E1 | Procedure before value | this file and the code are committed before the run; the code runs once; nothing in the procedure is changed after the value is seen | `git log`, run stamp |
| E2 | Only EMI handbooks | the calibration reads `modules_emi_2026.csv` and nothing else; no reference programme of the baseline enters | code, test |
| E3 | Enough pairs | at least 30 positive and 30 negative values; otherwise the step stops and Soma is told | generated report |
| E4 | Quality is known | true-positive rate, false-positive rate, AUC and the bootstrap interval are reported; an AUC below 0.70 is flagged "weak" and reported to Soma | generated report |
| E5 | Rules follow | the new value is in `configs/funnel.yaml`; 0.285 stays as a stress value; the pre-registration and the decision log record the change | test, reviewer |
| E6 | One text preparation | calibration and Step 7 share one function for text and vectors | code |
| E7 | Tests | `python -m pytest` passes completely | test run |
| E8 | Claims | 0 wrong numbers in the notes in a fresh-context check | reviewer |

Known limit, stated before the result: both modules of a pair come from the same university, so they may share
wording habits that a module of another university does not have. If so, the threshold comes out higher and the
automatic match is stricter than it should be. The hand check of Step 7 can add a match the automatic step missed,
and the old value stays as a stress test.

If a criterion still fails after 3 rounds, the step stops and Soma is told. No criterion is loosened.
