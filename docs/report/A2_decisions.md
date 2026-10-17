## A2 Method decisions {-}

<!-- Summary of docs/decision_log.md; the log has the full reasoning, date and decider for each entry. -->

Every method decision is logged with date, reason and who decided in
[decision_log.md](../../docs/decision_log.md). The decisions that shape the result:

| Date | Decision | Why |
|---|---|---|
| 14 Oct | Scope: EMI, bachelor and master, Germany for demand, public data only | project brief; no access to internal OTH data |
| 14 Oct | Criteria, weights and kill rules fixed before screening | avoid choosing the winner first |
| 15 Oct | Kill rule 1 applied: embedded / CPS master and part-time AI master dropped, robotics kept at the threshold | overlap with IT und Automation and AI for Industrial Applications |
| 17 Oct | Theme rules checked by hand (all cyber matches, samples of the others); exact dedicated-programme counts | keyword rules must be shown to be precise |
| 17 Oct | Module comparison: multilingual embeddings as headline, TF-IDF as sensitivity, after a hand check of twenty pairs | the embedding model agreed better with the hand check |
| 17 Oct | Catchment from school-leaver statistics; the regional database and the Bavarian web service not used | robots.txt and failed login; no workaround |
| 17 Oct | Lean labour-market evidence (job ads, state employment table, shortage analysis) | county-level occupation data not available |
| 17 Oct | Professors shown as neutral labels | personal names are not needed for the argument |
| 17 Oct | Forecast trained to 2024; central value = midpoint between KMK path and drift trend | 2025 is the G9 transition year; the midpoint is a stated choice |
| 17 Oct | Capture model used for relative capture only, anchored on public intake figures | the absolute demand scale failed the TH Ingolstadt check |
| 17 Oct | No new cannibalisation threshold; cannibalisation enters via net new demand | the kill rules were set before scoring |
| 17 Oct | Same capture model for all three options; missing anchors widen ranges | avoid evidence asymmetry |
| 17 Oct, 18 Oct | Score sheet reviewed by the team; weak evidence widens ranges symmetrically | robotics fit and feasibility rest on a title-level check |
| 17 Oct | One shared capture draw per Monte Carlo iteration | shared model error should not reorder options at random |
| 18 Oct | Every report number generated from a key-numbers file and checked against its evidence document | traceability |
