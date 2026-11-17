# Verification protocol (cross-check)

Written on 17 Nov 2026 by Poovallal Jeyapalan **before** the sweep, the topic check or the handbook test was run. Settings:
`configs/crosscheck_verification.yaml`. Changes after this date go to `docs/decision_log.md` with date and reason.

## Why

The coverage numbers of the cross-check come from automatic text matching (TF-IDF). Before we rely on them, an
independent reader checks the matches (topic check), and the programmes that can realistically win are tested
module by module against the handbooks of real programmes elsewhere (handbook test). The method follows the
funnel analysis (fresh-context AI reviewers, marking rules written first) so that both analyses can be compared, and
adds a second full blind marking and a human spot check.

## 1. Which programmes are checked: the sweep

A changed rule set can produce a different winner. To check in advance every programme that can plausibly win, we draw
2,000 rule sets, each rule at random within the range in the yaml (ranges chosen as values we would defend; tau 0.10
is left out because it was shown to be too loose). For every draw we record the winner at each level (first eligible
programme by score) and which programmes are eligible.

- **Handbook test:** every programme that wins in at least 2 % of the draws at its level, plus the official winners.
- **Topic check:** every programme eligible in at least 5 % of the draws, plus the official shortlist and all
  handbook-test programmes.

## 2. Topic check

One row = one focus topic of one programme kind (from the catalogue). The reviewer sees the topic, the subject and
level, the EMI module catalogue (titles and descriptions) and 8 suggested modules (by automatic similarity, in random
order, without scores). The reviewer may pick any EMI module.

| Verdict | Meaning |
|---|---|
| covered | an EMI module teaches this topic as a substantial part, at the depth the level needs |
| partly | the topic appears, but only as a minor part, a narrower subset, or below the level needed |
| no | no EMI module teaches it |
| unclear | the topic is too vague to judge (e.g. "Informatik", "Design") |

For covered and partly the reviewer names the module; every verdict has a reason of at most 25 words.

- **Blind:** reviewers do not see similarity scores, coverage, rankings, the band or the other reviewer's verdicts.
- **Two reviewers** mark every row independently; agreement is reported (share of equal verdicts and Cohen's kappa).
- **Third reader:** sees both verdicts and reasons and decides where they differ.
- **AI-checked coverage** = (covered + 0.5 x partly) / rows without "unclear", weighted by the number of offers listing
  the topic (as in the automatic method). Strict coverage counts covered only.
- **One-programme share** = covered weight whose named module belongs to the single EMI programme with the most.

## 3. Handbook test

For each handbook-test programme: up to 2 reference programmes of the same catalogue subject and level at other
German universities, full-time, preferring universities of applied sciences, nearest to Amberg first, with a public
module handbook. Each module of the reference (compulsory and listed electives) is marked against EMI's modules:

| Verdict | Meaning |
|---|---|
| covered | one EMI module, or two together, teach at least two thirds of the module's content |
| partly | an EMI module teaches a clear part, less than two thirds |
| new | not taught at EMI; needs new teaching |

Overlap = (covered ECTS + 0.5 x partly ECTS) / total ECTS. One-programme share = covered ECTS from the single EMI
programme with the most / total ECTS. A programme passes when the overlap is within 40-80 % and the one-programme
share is at most 80 % (the agreed rules). Same reviewer set-up as the topic check (two blind AI reviewers, third reader).

## 4. Human spot check

Poovallal checks 20 random rows per handbook-test programme and the third-reader rows of those programmes. Where he
disagrees, his verdict counts and the change is reported.

## 5. Records

All inputs given to the reviewers, the prompts, the model, and every verdict with its reason are saved under
`data/interim/crosscheck/verification/` (not committed; only public data, no timetable data). The method section of
the report states that the marking was done by an AI model.

## Known limits

- Reviewers read module descriptions, not lectures; a description can promise more or less than is taught.
- The 8 suggested modules can steer the reviewer; it may pick others, and we report how often it does.
- AI reviewers can share blind spots; the human spot check is the only fully independent check.
