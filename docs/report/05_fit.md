# Claim C: fit with EMI

<!-- Evidence: docs/evidence_fit_modules.md, docs/evidence_fit_staff.md, docs/evidence_benchmarks.md. -->

**Claim:** EMI can teach a cybersecurity bachelor with its existing staff, labs and modules, plus a costed gap.

## What EMI already teaches

We compared every module of the seven dedicated cyber programmes within 150 km that publish a module handbook
[@handbooks2026] with every module of the related EMI programmes [@othhandbooks2026]. A competitor module counts as
"covered" if its most similar EMI module passes a calibrated similarity threshold
([evidence_fit_modules.md](../../docs/evidence_fit_modules.md)).

- EMI already covers **{{emi_cover_gen_ba}} of a typical cyber bachelor's general foundations** (mathematics,
  programming, databases, networks, theory),
- but only **{{emi_cover_sec_ba}} of its security content** (range over the competitor bachelors
  {{cover_sec_ba_range}}; TF-IDF cross-check {{cover_sec_ba_tfidf}}). For a cyber master the figure is
  {{emi_cover_sec_ma}}.

These are upper-end estimates: in the hand check all errors of the embedding model were advanced competitor modules
matched to an EMI basics module, i.e. false "covered".

| Security area (CyBOK) | EMI covers |
|---|---|
| Cryptography | {{crypto_cover}} |
| Network security | {{network_cover}} |
| Forensics | {{forensics_cover}} |
| Penetration testing and auditing | {{pentest_cover}} |
| Security operations and incident management | {{secops_cover}} |

EMI teaches cryptography and introductory and network security. **The practical and defensive core that most
competitors teach is missing:** penetration testing, digital forensics, security operations and incident response,
software security, security management, law and human factors.

**Industrial (OT) security is not a differentiator against everyone.** TH Deggendorf, the nearest competitor with
both a bachelor and a master, already teaches it ({{deg_ma_ot}} of OT-related modules in its master). An OT profile
sets OTH apart from FAU, TH Ingolstadt, THWS and HDBW, not from Deggendorf.

## Staff and labs

From module responsibilities in the handbooks, {{security_profs}} EMI professors already teach security modules
(information security, cryptography, network security, AI security), and four more teach the industrial and embedded
side that OT security needs ([evidence_fit_staff.md](../../docs/evidence_fit_staff.md)). The missing practical core
amounts to a new teaching load of {{new_load_sws}} a year. With a teaching load of {{teaching_load_sws}} per semester
for a professor at a Bavarian university of applied sciences [@avbayhig], this means:

- **{{new_professorships}}**: one for offensive security and forensics, one for defensive and OT security including
  security operations;
- **one lab engineer**, and teaching assignments for law and security management;
- **an isolated security lab** for penetration testing, forensics and incident-response exercises, ideally coupled
  to the existing automation and process-data labs as an OT testbed. Its cost has not been estimated.

A master with an OT profile would add {{master_profs}} of a professorship, largely the same profile as the second
bachelor professorship.

## A draft curriculum

Using the standard Bavarian bachelor format (7 semesters, 210 ECTS, one practical semester) and four international
programmes as benchmarks [@benchmarks2026], we drafted a structure
([evidence_benchmarks.md](../../docs/evidence_benchmarks.md)):

| Block | Content | Status |
|---|---|---|
| Semesters 1-2 (60 ECTS) | mathematics, programming, digital systems, algorithms, operating systems, networks, databases, theory, software engineering, information security | existing EMI modules |
| Semesters 3-4 (60 ECTS) | cryptology, software engineering, web development, statistics, industrial communication; network security (adapted); secure coding, system security, penetration testing, digital forensics; security management, IT law | about half new |
| Semester 5 (30 ECTS) | practical semester | existing format |
| Semesters 6-7 (60 ECTS) | security operations and incident response, malware, OT / industrial security, security architecture, security lab project; AI and security (adapted); electives; thesis | mostly new |

In total {{draft_new_ects}} would be taught by new staff and {{teaching_assignments}} by teaching assignments, while
{{draft_reused_ects}} come from existing or adapted EMI modules. The security share is {{draft_security_ects}}, between
the Bavarian competitors ({{competitor_sec_share}}) and St. Pölten ({{stpoelten_sec_share}}). The new load of the
draft matches the staffing estimate above.

## Assessment

Claim C holds with a cost: EMI can carry the foundations, cryptography and networking, and has a genuine base for
OT security, but the practical security core is new and needs two professorships, a lab engineer and a lab.
**Strength: strong for the module comparison** (validated against a hand check), **medium for staffing**, which rests
on stated assumptions (cohort size, lab groups, teaching reductions) and could not use staff research profiles.
