# Marking rules for the module check (funnel Step 7)

Version 4. Written and committed before any row is made. A marker gets rows; each row is one module of some study
programme (title, credit points, description) together with several modules of the faculty EMI (5 to 10, numbered;
title, level, credit points, description) and 3 subjects from EMI's timetables (names only). In addition the marker
has the **whole list** of EMI modules allowed for the level (number, title, credit points, description) and the
**whole list** of timetable subjects, and may cite any of them. The marker does not know which programme or
university the module comes from and sees no similarity value.

The marker records **facts**, not a verdict. The verdicts are computed from the facts by code, under two readings
(`configs/funnel.yaml`, `version_4.marking.readings`).

| Fact | Values | When |
|---|---|---|
| **covered** | E1 / E2 / no | **E1:** one EMI module, or two together, teach essentially the same content at a comparable level; the module could be taken over unchanged. **E2:** one EMI module, or two together, cover at least two thirds of the content; at most one third would have to be added or changed. **no:** otherwise. For E1 and E2 name the module(s): one number, or two as "3+5". Never combine more than two. |
| **topic** | an EMI module number, a timetable subject (as written), or "none" | For **every** row (for a covered row: its covering module). An EMI module whose description, or a timetable subject whose name, has the module's **main topic** (the topic that the module title and at least half of its content are about). A passing mention in a list does not count. Search the whole lists, not only the modules shown in the row. |
| **parent_field** | yes / no | yes if the module belongs to a field EMI teaches: computing (mathematics, physics and programming count as computing), electrical and information engineering, or media and design; no for business, law, management and other sciences. |
| **lab** | yes / no | yes if the module cannot be taught without a laboratory or equipment that is not in the list of EMI labs given with the sheet (for example a chemistry wet lab, a vehicle workshop, a clinic). |
| **general** | yes / no | yes for a foreign-language course, a Studium-generale module, or a soft-skills module (presentation, teamwork, academic writing). English or German as a subject of the programme's field (for example technical English) is also "general". |
| **unsure** | flag | the description is too thin to decide, or two answers are equally defensible; then give the more cautious answer (covered "no" before E2, E2 before E1, topic "none" before a number). |
| **reason** | one line | what in the texts decides it, naming the EMI module or subject cited. |

Rules of thumb:

- Judge content, not titles. The same title with different content is not E1; different titles with the same content are.
- Judge content, not credit points, for **covered**: EMI teaches mostly in 5-ECTS modules, so a larger module may be
  covered by one EMI module with the same content, or by two together. (The code also computes a size reading in
  which credit points count; the marker does not apply it.)
- Level matters: an introductory EMI module does not cover an advanced module of the same field (then covered is
  "no", and the introductory module may be the **topic**).
- A bachelor module of EMI does not cover a master module unless the content is clearly the same.
- General subjects (mathematics, physics, programming, business basics, project work, seminars) are judged like all
  others: covered only if an EMI module has that content.
- Free elective slots without content ("Wahlpflichtmodul 1") are E1 if EMI offers elective modules of that kind at
  that level, otherwise mark "unsure".
- The same topic gets the same facts wherever it appears. If you have marked a module with the same title before,
  give the same facts unless the descriptions really differ, and say how.
- Do not guess what kind of programme the module comes from, and do not let it influence the facts.

How the code turns facts into verdicts (for information; exact rules in `configs/funnel.yaml`, `version_4.marking`):
lab "yes" is "lab". General "yes" is reported separately and is never N, new, T or X. Covered is read in two ways:
as marked (content), or only if the covering modules have at least the module's credit points (size). A row not
covered is **N** under the strict reading only if topic names an EMI module or timetable subject, and under the
lenient reading also if parent_field is yes; else it is **new**. Every figure is computed under all four
combinations (strict or lenient, content or size).

Version 2 (before the second marking): 5 to 10 EMI modules are shown instead of 3, with longer texts.
Version 3 (before the third marking): content counts, not credit points; up to two EMI modules together may cover a
module (Soma).
Version 4 (after the independent re-check, Soma's OK of rules version 4): facts instead of verdicts, so that a strict
and a lenient reading can both be computed; the whole EMI module and timetable lists for every row; "general"
modules apart; the same topic gets the same facts.
