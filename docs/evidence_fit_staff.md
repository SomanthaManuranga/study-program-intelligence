# Evidence: staff and labs fit for a cybersecurity programme (Claim C, feasibility)

Status: v1, 17 Oct 2026 (Step 44). Sources: EMI module handbooks (Step 40, `data/interim/modules.csv`: module
responsibility per module), public OTH web pages on labs and research institutes (`docs/oth_web_manifest.json`,
raw pages in `data/raw/oth_web/`), § 4 AVBayHIG. Method decisions: docs/decision_log.md (Step 44).

## Method and data access

- Teaching: the responsible lecturer of each EMI module with security or security-adjacent content, taken from the
  official module handbooks (public documents).
- Research and labs: OTH lab and institute pages found via the public sitemap; robots.txt respected, 3 s delay, raw
  pages cached with SHA-256.
- Not used: individual staff profile pages. OTH's robots.txt blocks AI crawlers (GPTBot) from
  `/hochschule/ueber-uns/personen/`; although our user agent is not covered, we treat that as the site owner's wish and
  did not read person pages or professors' personal microsites. Research profiles are therefore not complete.

## Who teaches security at EMI today (module handbooks)

| Area | Lecturer (module responsibility) | Modules |
|---|---|---|
| Information security, cryptography | Prof. Dr. Daniel Loebenberger | Informationssicherheit (BA II/MI); Moderne Anwendungen der Kryptographie (MA) |
| Network security, security basics, functional safety | Prof. Dr. Christian Roth | Computernetzwerke (BA); Cybersicherheit (MA KI, MA IT und Automation); Grundlagen der Informations- und Funktionalen Sicherheit (MA IT und Automation) |
| Cryptology, coding theory | Prof. Dr. Jan Ortmann | Grundlagen der Codierungstheorie und Kryptologie (BA); Informationstheorie, Codierung (MA) |
| AI security | Prof. Dr. Patrick Levi | KI Sicherheit (MA KI) |
| OT-adjacent: industrial communication, CPS, embedded | Prof. Dr.-Ing. Thomas Stein; Prof. Dr. Michael Wiehl; Prof. Dr. Peter Raab; Prof. Dr. Gerald Pirkl | Industrielle Kommunikationssysteme; Cyberphysische Systeme 1/2; Embedded Systems, Echtzeitbetriebssysteme; Eingebettete Intelligenz |
| Software engineering, systems | Prof. Dr. Sandra Rebholz; Prof. Dr. Josef Pösl; Prof. Dr. Ulrich Schäfer / Prof. Dr. Christoph Neumann | Software Engineering 1/2; Betriebssysteme, Technologien verteilter Systeme; Web-Anwendungsentwicklung |
| Ethics | Prof. Dr. Dominikus Heckmann; Prof. Dr. Lisa-Marie Ranisch | Informationsethik und Technikphilosophie; Ethik, Kognition & Meeting |

Reading: about four professors already teach security modules (information security, cryptography, network
security, AI security), and four more teach the industrial/embedded side that an OT-security profile needs. This
is a real base, but it is concentrated in introductory security, cryptography and networks (Step 41).

## Gap areas (Step 41) mapped to existing staff

| Gap area (CyBOK, competitors teaching it) | Existing EMI capacity | Verdict |
|---|---|---|
| Penetration testing & auditing (6 of 7) | none | **new staff** |
| Digital forensics (5 of 7) | none | **new staff** |
| Security operations / incident management, SOC (5 of 7) | none (network monitoring basics in Computernetzwerke) | **new staff** |
| Malware & attack technologies (2 of 7) | none | **new staff** (same profile as pentesting) |
| Software security, secure coding (3 of 7) | software engineering, web development; no security focus | **partly** (existing staff with added security content, or new staff) |
| OT / industrial security (Deggendorf, Aalen) | functional + information security (Roth), industrial communication (Stein), CPS (Wiehl), embedded/RTOS (Raab) | **partly**: strongest base; needs one OT-security specialist to integrate it |
| Risk management & governance, ISMS (4 of 7) | none in EMI | **new** (teaching assignment or other faculty) |
| Law & regulation (4 of 7) | none in EMI | **teaching assignment** (lawyer) or other faculty |
| Human factors (3 of 7) | ethics modules | **partly** |
| Cryptography, network security, AI security | Loebenberger, Ortmann, Roth, Levi | **covered** |

## New teaching load and professorships

Assumptions (stated, not measured):
- A full-time cyber bachelor has about 63-65 security ECTS (TH Ingolstadt 63, TH Deggendorf 65; Step 41). EMI covers
  at most ~31 % of a typical competitor bachelor's security ECTS (e5 headline, an upper-end estimate), so **new
  security content of about 40-52 ECTS** (the uncovered security ECTS of TH Deggendorf and TH Ingolstadt).
- 5 ECTS = 4 SWS (OTH standard in the handbooks, e.g. "Kontaktstudium 60 h (4 SWS)" for a 5-ECTS module); each
  module offered once a year.
- Practical modules (pentesting, forensics, SOC, malware: about 4 modules with ~2 SWS lab each) need two lab groups
  for a cohort of 40-60: +8 SWS.
- Teaching load: **18 SWS per week per semester for a HAW professor in Bavaria (§ 4 AVBayHIG, version 13.02.2023,
  valid from 01.03.2026)**, i.e. 36 module-SWS per year; with typical reductions (research, offices) about 15 SWS
  effective (30 per year).

| Item | SWS per year |
|---|---|
| New security modules (40-52 ECTS x 4/5) | 32-42 |
| Extra lab groups | +8 |
| **New teaching load, bachelor** | **40-50** |
| Professorships at 36 SWS/year (nominal) | **1.1-1.4** |
| Professorships at 30 SWS/year (effective) | **1.3-1.7** |

Law (~4 SWS) can be bought in as a teaching assignment and is included above. Not included: extra exercise groups
in the shared foundation modules (maths, programming, networks) when 40-60 more students join them, thesis and
internship supervision; both add load to existing staff.

Master (optional, OT-security profile): roughly 30-40 new security ECTS of 90 -> 24-32 SWS -> 0.7-0.9 professorship,
largely the same profile as the second bachelor professorship.

**Estimate: 2 new professorships** (one offensive security & forensics, one defensive / OT security incl. SOC),
**plus one lab engineer** and teaching assignments for law and governance. With the master, the second
professorship carries the OT specialisation.

## Infrastructure

Reusable (EMI labs listed on the public lab overview): Rechnernetze (computer networks), Prozessdatentechnik
(industrial process data/communication), Automatisierungssysteme, Mikrocomputertechnik, Software Projekte, plus the
Kompetenzzentrum Digitaler Campus and the AI competence centre IKKI (lists "Cybersicherheit" among its topics).
No dedicated security lab or security research institute is visible on the public pages.

Needed: an isolated security lab / cyber range for pentesting, forensics and SOC exercises (separate network,
attack/defence VMs, forensic workstations), ideally coupled to the existing automation/process-data labs for an
OT-security testbed. Cost is not estimated here.

## Reading for the argument

- Claim C (fit): EMI has a genuine starting point (about four professors teaching security, an industrial/embedded
  base for OT, network and automation labs). The practical security core is missing and needs about **2 new
  professorships + 1 lab engineer + a security lab**. That is a feasibility cost to be priced into the feasibility
  gate and the MCDA, not a kill reason in itself.
- OT security is where existing staff help most; offensive security, forensics and SOC are where they help least.

## Caveats

- Teaching is read from module responsibility in the handbooks; research areas of individual professors were not
  read (person pages skipped), so existing research capacity may be underestimated.
- The ECTS-to-SWS conversion, lab-group split and cohort size are assumptions; the 31 % coverage is an upper-end
  estimate (Step 41), so the new load may be somewhat higher.
- Teaching reductions differ by person; 15 SWS effective is a rough planning value.
- Lab equipment of the listed labs is not described on the public pages; reuse is plausible, not verified.
