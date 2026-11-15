# Marking rules for the module check (funnel Step 7)

Written and committed before any row is made. A marker gets rows; each row is one module of some study programme
(title, credit points, description) together with the 3 most similar modules of the faculty EMI (title, level,
description) and 3 subjects from EMI's timetables (names only). The marker does not know which programme or
university the module comes from and sees no similarity value.

Set exactly one verdict per row and give one line of reason.

| Verdict | When |
|---|---|
| **E1** | One of the 3 EMI modules teaches essentially the same content at a comparable level. The module could be taken over unchanged. Name which one (1, 2 or 3). |
| **E2** | One of the 3 EMI modules covers at least two thirds of the content; at most one third would have to be added or changed. Name which one. |
| **N** | No EMI module covers two thirds, but the module's main topic is clearly taught in EMI already: one of the 3 timetable subjects, or one of the 3 EMI modules, is on the same main topic. A current lecturer could write this module. |
| **new** | The main topic is not taught in EMI as far as the row shows. |
| **lab** | The module cannot be taught without a laboratory or equipment that is not in the list of EMI labs given with the sheet (for example a chemistry wet lab, a workshop for vehicles, a clinic). This verdict wins over all others. |

Rules of thumb:

- Judge content, not titles. The same title with different content is not E1; different titles with the same content are.
- Level matters: an introductory EMI module does not cover an advanced module of the same field (at most N).
- A bachelor module of EMI does not cover a master module unless the content is clearly the same.
- General modules (mathematics, physics, programming, English, business basics, project work, seminars) are judged
  like all others: covered only if one of the 3 EMI modules has that content.
- Free elective slots without content ("Wahlpflichtmodul 1") are E1 if EMI offers elective modules of that kind at
  that level in the row, otherwise mark "unsure".
- If the description is too thin to decide, or two verdicts are equally defensible, give the more cautious one
  (the one further down the table, except "lab") and add the flag **unsure**.
- Do not guess what kind of programme the module comes from, and do not let it influence the verdict.

Covered means E1 or E2. Not covered means N, new or lab.
