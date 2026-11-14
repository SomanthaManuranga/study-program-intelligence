# Criteria for funnel Step 2 (programme types)

Written and committed before the Step 2 code is written. Step 2 groups the offers into types by the rules of
`configs/funnel.yaml` (`universe`, `text`, `similarity`, `discovery`). No type is judged, scored, ranked or dropped,
and nothing about OTH or EMI is used.

| # | Criterion | Target | How it is checked |
|---|---|---|---|
| G1 | The two rule files exist before they are needed | `configs/funnel_title_stoplist.yaml` is committed before any Step 2 code runs; `configs/funnel_boilerplate.yaml` is committed after the scan and before the embedding; the scan lists every focus-item string found in 20 or more offers with the decision "dropped" or "kept" | `git log`, scan table |
| G2 | The offer texts are clean | 0 offer texts contain a dropped phrase or a boilerplate phrase after normalising (the run stops otherwise); the number of offers without focus items is reported | check in the code, test |
| G3 | Code before results | scan, embedding and grouping each run from committed code on a clean tree; every output carries the commit hash | output headers, `git log` |
| G4 | The grid is complete and the choice follows the written rule | 10 settings (5 sizes x 2 methods) on 3 UMAP seeds with 10 refits each; the selected setting is the one the rule `discovery.selection` gives, recomputed from the grid file by a test | grid file, test |
| G5 | Types are built as the rules say | every type has a centroid and a radius; stable types have a mean best-match Jaccard of at least 0.75; every rare type has offers of at least 2 institutions and fewer members than the selected minimum size; an offer is assigned afterwards only inside the radius of its nearest type; nothing is refitted | tests on the output files |
| G6 | All validations are reported, whatever they show | agreement with the catalogue's study fields (ARI); the TF-IDF cross-check with every "method-dependent" type flagged; all 18 old topic lists tested on both offer sets, or named with the reason why not; counts only, no general statement | generated report |
| G7 | The mix is reported | share of offers left without a type, and share inside a type, by focus items present or not and by institution type | generated report |
| G8 | The result can be reproduced | a second run of the grouping from the same embeddings gives the same type for 100 % of the offers | second run, comparison of the two outputs |
| G9 | The types make sense to a reader | for 30 types drawn with `numpy default_rng(42)`, a fresh-context reviewer reads 10 member titles drawn the same way (all members if fewer) and says whether at least 8 of 10 are the same kind of programme; at least 80 % of the 30 types pass | reviewer's table |
| G10 | No judging and no look back | no type is dropped, scored or ranked; no run-1 result file is read; OTH and EMI data are not used | reviewer, code |
| G11 | The code follows the rules | 0 differences between the code and `configs/funnel.yaml` that are not written down as a decision | fresh-context reviewer |
| G12 | Every number in the Step 2 notes is right | 0 wrong claims in a fresh-context check against the generated files | reviewer |
| G13 | The repository works | `python -m pytest` passes completely | test run |

G9 is a quality bar on the result. If it fails, the types are not repaired by hand: the step stops and Soma is told.

If a criterion still fails after 3 rounds, the step stops and Soma is told. No criterion is loosened.
