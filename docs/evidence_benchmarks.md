# Evidence: international benchmark programmes and a draft OTH cyber bachelor (lean)

Status: v1, 17 Oct 2026 (Step 45). Scope: curriculum structure only, as input for our proposed curriculum.
Sources: `configs/benchmark_documents.yaml`, manifest `docs/benchmark_manifest.json` (public pages/PDFs, robots.txt
respected). Method decisions: docs/decision_log.md (Step 45).

## Programmes

| Programme | Country, type | Length | Source (downloaded) | Detail available |
|---|---|---|---|---|
| IT Security (BSc), USTP St. Pölten | AT, University of Applied Sciences | 6 sem, 180 ECTS | programme folder 09/2025 (PDF) | full module list with ECTS |
| Sichere Informationssysteme (BSc), FH OÖ Hagenberg | AT, University of Applied Sciences | 6 sem, 180 ECTS | programme page (module groups with ECTS) | module groups |
| Information & Cyber Security (BSc), Hochschule Luzern | CH, University of Applied Sciences | 180 ECTS | module overview page | module categories (no ECTS per module) |
| Ethical Hacking (BSc Hons), Abertay University | UK (Scotland) | 4 years, 480 SCQF = 240 ECTS | programme document (PDF) | frame only (20-credit modules, 40-credit honours project) |

**OT-focused programme: none usable.** No European bachelor with an OT/industrial-security focus and a public ECTS
curriculum was found: ECAM LaSalle's "Bachelor cybersécurité des systèmes industriels et urbains" (FR) publishes no
ECTS or modules; Turku UAS "ICT - Cyber Security and IoT" (FI, 240 ECTS; closest bachelor with an embedded angle)
is blocked by robots.txt on its study-guide site; ICS/SCADA security otherwise appears only at master level (USTP
St. Pölten, TH Augsburg, UPC Barcelona, Leiden) or as a single course in an automation bachelor (TU Cluj-Napoca).
OT reference used instead: TH Deggendorf's bachelor and master (Step 41: 3 OT modules / 15 ECTS in the bachelor)
and HSLU's core modules "Cyber Security in Product Engineering 1/2" (product/embedded security).

## Structure by ECTS

| Block | St. Pölten (180) | Hagenberg (180) | HSLU (180) | Abertay (240) |
|---|---|---|---|---|
| General foundations (maths, programming, networks, OS, DB, soft skills) | 50 (28 %) | 7 + part of mixed groups | in core / related | n/a |
| Security-specific | 90 (50 %) | 54 (30 %) pure security groups (Hacking 12, Incident Handling 12, Kryptographie 11, Recht & Compliance 6, Organisation & Management 13) + 74 mixed (Sichere Software 32, Sichere Infrastruktur 42) | core >= 60 ECTS (>= 33 %), security-dominated | n/a |
| Electives / related modules | 10 (6 %) | 7 (4 %) | related + minor ~45 % | n/a |
| Practice: internship, projects | 20 (11 %) | 38 (21 %) incl. internship and thesis* | project modules, rest | microcredentials 20 (Y1, Y2) |
| Thesis | 10 (6 %) | (in the 38)* | in project modules | honours project 20 (8 %) |
| Sum | 180 | 180 | 180 | 240 |

\* Hagenberg's older info sheet (web-search snippet, not verified in a downloaded file) splits "Projekte und Praktika"
into internship with seminar 22, thesis with seminar and exam 8, projects 8.

Bavarian references (Step 41, module handbooks): TH Ingolstadt Cybersicherheit 210 ECTS with 63 security ECTS
(30 %), TH Deggendorf Cyber Security 210 ECTS with 65 (31 %), both 7 semesters incl. a practical semester.

## Patterns

1. Security share: 30 % (Hagenberg pure groups, THI, DEG) to 50 % (St. Pölten) of all ECTS.
2. Order: foundations and first security modules from semester 1 (St. Pölten: OS & Linux security, cryptography in
   semesters 1-2); offensive/defensive practice (pentesting, forensics, SOC/CDC) in semesters 3-5; architecture and
   capstone at the end.
3. Practice: every programme has a large practical block (internship 20-22 ECTS, projects, labs, a business
   continuity or attack/defence exercise). Management, law and compliance are standard (St. Pölten 20 ECTS of
   security management incl. law; Hagenberg 19).
4. OT/industrial security is not a standard bachelor block abroad; where present it is product/embedded security
   (HSLU) or a master topic. TH Deggendorf is the exception (Step 41).

## Draft structure: OTH cyber bachelor (B.Sc.)

Format (verified): 7 semesters, 210 ECTS, 6 theoretical semesters + 1 practical semester (semester 5), as in Bavarian
HAW bachelors (BayHIG Art. 77 Abs. 3 and RaPO § 2 Abs. 2: bachelor programmes generally include a practical semester;
e.g. HAW Landshut and TH Rosenheim regulations: 7 semesters = 6 theoretical + 1 practical, 210 ECTS; the same pattern
in the OTH, THI and TH Deggendorf handbooks of Step 40). Modules of 5 ECTS unless stated.

| Semester | Module (ECTS) | Status |
|---|---|---|
| 1-2 (60) | Mathematik 1, Mathematik 2, Programmieren für KI 1 (Python), Programmieren für KI 2 (C/C++), Grundlagen digitaler Systeme, Algorithmen und Datenstrukturen, Betriebssysteme, Computernetzwerke, Datenbanksysteme, Theoretische Informatik, Software Engineering 1, Informationssicherheit | **reuse EMI module** (12 x 5) |
| 3-4 (60) | Grundlagen der Codierungstheorie und Kryptologie; Software Engineering 2; Web-Anwendungsentwicklung; Stochastik; Cyberphysische Systeme 1 or Industrielle Kommunikationstechnik | **reuse EMI module** (5 x 5) |
| | Netzwerksicherheit (bachelor version of the existing master module "Cybersicherheit") | **reuse, adapted** (existing staff) |
| | Secure Coding; System- und Betriebssystemsicherheit (Härtung); Penetration Testing & Ethical Hacking; Digitale Forensik | **new** (4 x 5) |
| | Informationssicherheitsmanagement & Risiko (ISMS); IT-Recht & Datenschutz | **new, teaching assignment** (2 x 5) |
| 5 (30) | Practical semester (Praxisphase + Praxisseminar; OTH programmes book 22 ECTS for these, the rest per SPO) | **reuse format** |
| 6-7 (60) | SOC & Incident Response; Malware & Angriffstechniken; OT-/Industrial Security; Security Architecture & Cloud Security; Security Lab Project | **new** (5 x 5) |
| | KI & Sicherheit (bachelor version of the master module "KI Sicherheit") | **reuse, adapted** (existing staff) |
| | Electives from the EMI catalogue (3 x 5) | **reuse EMI module** |
| | Bachelor thesis + seminar/colloquium (15) | **reuse format** |
| **Sum** | **210** | |

Balance:
- **New, taught by new staff: 45 ECTS** (9 modules) -> 36 SWS + 8 SWS lab groups = 44 SWS/year = 1.2 professorships
  nominal (18 SWS/semester, § 4 AVBayHIG) or 1.5 effective -> consistent with Step 44: **2 new professorships**
  (offensive security & forensics; defensive & OT security incl. SOC) + 1 lab engineer.
- **New via teaching assignments: 10 ECTS** (ISMS, law).
- **Reused or adapted EMI modules: 110 ECTS**, plus practical semester and thesis formats (45 ECTS).
- **Security-specific ECTS: 75 (36 %)**: between the Bavarian competitors (30-31 %) and St. Pölten (50 %).
- OT security is one compulsory module plus the industrial basics (Cyberphysische Systeme 1 / Industrielle Kommunikationstechnik)
  and can be deepened via electives and the lab project; a full OT profile would belong to a later master.

## Caveats

- Lean scope: structure only, not learning outcomes or module content. Abertay's per-module split and HSLU's ECTS per
  module are not available in the downloaded sources; Hagenberg's thesis/internship split is from a snippet.
- Classification "general vs security" for St. Pölten is ours (module titles); Hagenberg's mixed groups contain both.
- The draft is a structure for the argument (Claim C, feasibility), not a study and examination regulation; module
  names of reused EMI modules are from the Step 40 handbooks; adaptations of master modules need their owners' consent.
