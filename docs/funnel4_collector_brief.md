# Collecting the reference handbooks (rules version 4, R2)

Fixed before any handbook is collected. Rule: `configs/funnel.yaml`, `feasibility_gate.references` (choice, two,
one_only, none, complete, module_kinds, electives) with `version_4` (reference offers from the title type,
deviation 4). The offers to try, in order, are in `data/interim/funnel4_reference_tries.csv`.

## What a collector does, per candidate

1. Take the offers of the candidate in `try` order. Reference **a** is the first offer whose official module
   handbook is public, fetchable and complete; reference **b** the next one at a **different institution**. At most
   5 offers are tried per reference. A candidate with only one offer, or with no second complete handbook within the
   tries, has one reference and is flagged "single reference".
2. Find the handbook on the institution's own website (a web search may point to the page). **Every page and every
   document is requested only through**
   `python -m study_program_intelligence.analysis.funnel_refs fetch <id> <url>` (it checks robots.txt, sends the
   project's User-Agent and waits as the site asks). A page or file that robots.txt blocks, that needs a login, or
   that fails, is recorded and **never worked around** (no other tool, no cache, no mirror).
3. Use the current handbook of the full-time programme. If several versions exist, the newest that the programme
   page links.
4. Complete = the modules listed cover at least 80 % of the programme's ECTS, thesis included; of the listed electives
   only the ECTS a student must take count. A handbook that lists only titles without descriptions is not complete.
5. Write the module table `data/interim/funnel4_refs/<candidate>_<level>_<a|b>.csv` with the columns
   `module, ects, kind, semester, content, page`:
   - `kind`: compulsory, elective, thesis, internship or practical semester (as the handbook says);
   - `ects`: the module total;
   - `content`: the learning outcomes and the content as the handbook gives them, up to the literature; **no names of
     persons** (module leads, lecturers), no literature lists;
   - one row per module; an elective catalogue is listed in full.
6. Write `data/interim/funnel4_refs/<candidate>_<level>_<a|b>.json` with the keys `ref, candidate, gate_order, level,
   try, institution, title, programme_id, handbook_url, handbook_version, doc_ids, programme_ects, compulsory_ects,
   elective_ects_required, thesis_internship_practical_ects, listed_elective_ects, notes` (as the version-3 tables).
7. Write `data/interim/funnel4_refs/tries_<candidate>_<level>.json`: every offer tried, with the outcome (reference a,
   reference b, not complete, no handbook found, blocked by robots.txt, login, error) and the URLs asked.

Version-3 tables of the same offer (`version-3 table` column) are copied, not collected again.
Nothing is marked or judged by the collector; the module check comes later and blind.
