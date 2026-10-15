# Overlap test (kill rule 1) and revised shortlist

Status: v1, 15 Oct 2026. Rule: drop a candidate if more than 50 % of its core topics are already taught in **one** OTH programme at the same level (docs/kill_rules.md). Data and mapping: `configs/overlap_test.yaml`; EMI portfolio: `configs/oth_portfolio.yaml`; module handbooks: 7 PDFs in `data/raw/oth modules/` (local).

## Result

| Candidate | Closest EMI programme | Core topics already taught | Share | Kill rule 1 |
| --- | --- | --- | --- | --- |
| Cybersecurity, bachelor | Industrie-4.0-Informatik (B.Eng.) | 2 of 8 | 25 % | **passes** |
| Cybersecurity, master | IT und Automation (M.Eng.) | 3 of 8 | 38 % | **passes** |
| Robotics + AI, bachelor | Künstliche Intelligenz (B.Sc.) | 4 of 8 | 50 % | passes at the threshold |
| Embedded / cyber-physical systems, master | IT und Automation (M.Eng.) | 7 of 8 | 88 % | **dropped** |
| Part-time AI master (control case) | AI for Industrial Applications (M.Sc.) | identical | — | **dropped** |

## What this means

- **Cybersecurity is the strongest candidate at both levels.** EMI already teaches the foundations (Kryptologie as a compulsory module, Informationssicherheit as an elective in the bachelor; information security, cryptography and Cybersicherheit in the master), so staff and modules exist: good fit. But six of the eight specialised topics are missing: network security, data protection, digital forensics, security management (ISMS, ISO 27001), malware and cybercrime, system security engineering. A new programme would add teaching, not relabel it: good differentiation.
- **The embedded/CPS master already exists in practice.** IT und Automation covers digital system design, industrial communication, safety and security, model-based development, control and embedded intelligence. A new master would mainly compete with it.
- **The part-time AI master already exists.** The AI for Industrial Applications handbook contains a complete part-time curriculum.
- **Robotics + AI sits exactly at the threshold.** The KI bachelor already teaches robotics, autonomous mobile systems, ML for robotics and cyber-physical systems; Mechatronik und digitale Automation (other faculty) covers automation, control and mechanics, so OTH as a whole covers 7 of 8 topics. It passes the rule as written, but the cannibalisation risk is high. Better framed as a strengthened specialisation than a new programme; kept on the list only as the comparison case.

## Revised shortlist for full dossiers

1. Cybersecurity, bachelor (lead candidate).
2. Cybersecurity, master: with an industrial / OT security profile, building on IT und Automation.
3. Robotics + AI, bachelor: comparison case (high cannibalisation risk).

Watch list (not enough evidence yet): microelectronics / semiconductors master (9 programmes in Germany, first-year students rising from a very low base).

## Method and limits

- Core topics come from competitor focus lists (Schwerpunkte), not from their module handbooks; synonyms were merged by hand. Generic basics (programming, mathematics) are excluded because every programme shares them.
- Coverage is matched on EMI module titles, then checked against the module text where the title was unclear (e.g. real-time content in IT und Automation).
- The E&IT bachelor handbook for SPO 226B describes only the first study section; its specialisation modules are in the SPO 222B handbook, which is still to be added. It matters only for the robotics and embedded comparisons, and neither verdict would change: embedded is already dropped on the master side, and robotics compares against the KI bachelor.
- Kill rule 1 says nothing about demand. Cybersecurity still has to pass the demand, capture, outlet and feasibility scoring.
