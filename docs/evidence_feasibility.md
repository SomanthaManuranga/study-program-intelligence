# Evidence: feasibility with existing resources (re-scope, week 2)

Rule: `configs/feasibility.yaml` (pre-registered before any re-scoring). Labs: `configs/emi_labs.yaml`. Tables:
`reports/feasibility.md` (`python -m study_program_intelligence.analysis.feasibility`). Hand check:
`configs/feasibility_handcheck.yaml` (proposed by Claude, to be confirmed by Soma).

## Method

- **EMI modules:** the current handbooks of all EMI programmes, 412 modules (`data/interim/modules_emi_2026.csv`).
- **Reference curricula:**
  - cyber bachelor: TH Ingolstadt, TH Deggendorf, THWS (FAU is part-time and left out);
  - cyber master: TH Ingolstadt, TH Deggendorf, HDBW;
  - robotics bachelor: Hochschule Kempten Robotik.
- **Matching:** the Step 41 method (e5 embeddings centred per handbook, best EMI match, ECTS-weighted). The threshold
  was recalibrated on this module set with the Step 41 procedure, as the rule requires: 0.277 (AUC 0.762); it was 0.295
  in Step 41. TF-IDF is shown as a cross-check.
- **Known artefact:** the TH Deggendorf master scores 0 %. Its handbook has only security modules, and centring it
  removes the shared security signal; the matches are meaningless (e.g. "Cybersecurity Fundamentals" to
  "Fahrzeugautomatisierung"). The verdict for the master rests on THI and HDBW.

## The current three options

| Option | Evidence | F1 coverage (at least 80 %) | F2 new content | F3 labs | F4 one source | Verdict |
|---|---|---|---|---|---|---|
| Cybersecurity B.Sc. | OTH draft curriculum (Step 45) | 67 % (110 of 165 taught ECTS) | 45 ECTS need new professors | new security lab needed | - | **fails** F1, F2, F3 |
| Cybersecurity B.Sc. | reference curricula | 51-79 % (THWS, THI, THD) | 34-81 ECTS new at OTH size | 12-28 % of core ECTS need a security lab | 16-25 % | **fails** F1, F2, F3 |
| Reduced cyber bachelor | EMI's own security modules | - | - | - | - | **not viable**: only 2 distinct security modules (10 ECTS) at bachelor level, against roughly 45-75 security ECTS in dedicated cyber bachelors; it would be an informatics bachelor with a security focus, which Industrie-4.0-Informatik and Medieninformatik already are |
| Cyber/OT M.Sc. | reference curricula (THI, HDBW) | 47-49 % | about 30 ECTS new at OTH size | 12-19 % need a security lab | 19-32 % | **fails** F1, F2, F3 |
| Reduced OT-security master | EMI's security and OT modules | - | - | - | - | **open**: 16 distinct modules (80 ECTS), half at bachelor level; at master level IT und Automation supplies most of them, so F4 against IA is the risk. Carried into the recombination step |
| Robotics + AI B.Sc. | Kempten, automatic | 80.7 % (TF-IDF 48 %) | about 32 ECTS new | industrial robot cells | 25 % | fails F2 and F3 automatically |
| Robotics + AI B.Sc., path A (industrial robotics) | Kempten, hand check | 94.9 % | 7 ECTS (teaching assignments) | **two modules need industrial robot cells, which EMI lacks** | 29 % | **fails F3** |
| Robotics + AI B.Sc., path B (assistive / service robotics) | Kempten, hand check | 91.2 % | 7 ECTS teaching assignments + 5 ECTS existing professor | educational / humanoid robots in the Physical Computing lab | 26 % (KI family) | **passes F1-F4, pending Soma's confirmation of the hand check** |

- **Labs (public EMI lab list):** no isolated security lab and no industrial or collaborative robot cell. The only
  robots are teaching-grade ones (Mindstorms, Aldebaran humanoids) in the Physical Computing lab.
- **More security teaching than the baseline saw:** the current master handbooks (IA, MKI, MP) share "Cybersicherheit",
  "Moderne Anwendungen der Kryptographie" and "Grundlagen der Informationssicherheit und Funktionalen Sicherheit", and
  MKI adds "KI Sicherheit". This does not change any verdict.

## Recombination (clusters of existing EMI modules)

- **Data:** 263 distinct EMI modules (frame modules left out), clustered with e5 embeddings (agglomerative, cosine).
- **Weak structure:** the silhouette is highest at k = 30, the top of the allowed range, and low (0.092). The clusters
  are hypotheses for the hand review, not findings.
- **Generic clusters:** many clusters that pass the size and source rule are foundations (mathematics, programming,
  business, languages). They are not programme profiles.

| Proposed profile | Cluster(s) | ECTS | Programmes / largest source | Note |
|---|---|---|---|---|
| Robotics & autonomous systems | 15 | 70 | 5 / KI 36 % | the same space as the robotics option (path B) |
| Computer vision & visual AI | 6 | 63 | 6 / KI 24 % | CV, deep vision, visual computing, ML |
| Visual computing, interaction & XR | 6 + 19 (+ 10) | 98 | 9 / DD 34 % | adds media design, HCI, AR/VR |
| Data engineering & geo-data | 13 | 65 | 7 / GI 31 % | big data, cloud, geo data analytics |
| Security | 22 | 30 | 5 / E&IT 33 % | too small: confirms that cyber cannot be built from existing modules |

Clusters that mirror an existing programme (media production, audio: MT/DD; educational technology: EDU; surveying:
GI; electrical energy: E&IT, 57 % from one programme) are not candidates.

## Rarity (rare topic words in EMI-linked full-time offers)

- **Data:** 5,034 full-time bachelor and master offers in EMI-linked fields; 1,017 rare topic words (at most 3
  institutions Germany-wide).
- **Hand review:** the top 40 by teachability (`reports/rarity.md`). They mix genuine rare types with word artefacts:
  general words; the cyber family, whose type is not rare, only its wording; media arts; business programmes.
- **Proposed to keep** (EMI-teachable, rare, not at OTH):
  - AR/VR engineering (2-3 institutions);
  - automated driving / electromobility / mobile robotics (3);
  - energy data management (1-2);
  - geovisualisation (1);
  - technical cybernetics (2);
  - electromobility and energy grids (master, 1);
  - rail power supply and catenary (1).
- **The supervisor's example works:** Motorsport Engineering appears at Amberg and Stralsund only (Stralsund
  part-time), so the method finds the kind of programme he means.

## Candidates for week 3 (proposed)

1. Robotics + AI B.Sc., assistive / service robotics profile (path B).
2. Autonomous mobile systems / automated driving (robotics cluster plus the rarity hit; EMI has autonomous mobile
   systems and race-car modules).
3. AR/VR & visual computing engineering (clusters 6 + 19 + 10 plus the rarity hit).
4. Energy data management / energy informatics (E&IT energy plus KI Smart Energy; rarity hit; E&IT source share to
   watch).
5. Geo-data & geovisualisation (GI plus visual computing / data; rarity hit).
6. Reduced OT-security master (IA source share to watch).

Week 3 runs all of them through the funnel filters (demand trend, supply gap, full-time only) and the module-level
F1-F4 check with a reference curriculum each.

## Caveats

- The matches are automatic until the hand check is confirmed; for robotics, e5 (80.7 %) and TF-IDF (48 %) disagree
  strongly, so the hand check decides.
- Kempten is one reference; its two specialisations make two paths. The path verdicts use core and specialisation
  modules; the electives could only raise coverage.
- "Teaching-grade robots" may not be enough for a full robotics programme; whether the Physical Computing lab can carry
  robotics projects at cohort size is not known from public data.
