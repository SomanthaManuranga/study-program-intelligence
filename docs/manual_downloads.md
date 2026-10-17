# Manual downloads

Files the scripts do not fetch (robots.txt, login, or no working public link). Save each file exactly under
"Target file" (folder relative to the repo root), then tell Claude; Claude adds URL, date and SHA-256 to the
manifest named in the section, with status "manual". A manual download in the browser is fine where robots.txt
blocks automated access (robots.txt applies to crawlers, not to a person reading the page).

## Step 39: competitor module handbooks (updated 17 Oct 2026)

Folder: `data/raw/competitor modules/`. Manifest: `docs/competitor_modules_manifest.json`.

Status of the 11 programmes:
- Downloaded automatically (7): FAU BA, THI BA Cybersicherheit, THI MA Cloud Applications und Security Engineering,
  TH Deggendorf BA (th-deg.de link from Soma; first link's host did not resolve) and MA, THWS BA, HDBW MA.
- No published handbook (1): THI MA Sociotechnical Cybersecurity. The SPO notice of 24.10.2025 contains no module
  list (checked by Soma). Manifest status `not_published`.
- Still open (3): below.

| # | Programme | Why manual | Page / file link | What to download | Target file |
|---|---|---|---|---|---|
| 1 | Technische Informatik - Security und Industrial Internet of Things M.Sc., TH Mannheim (244 km; benchmark) | robots.txt of www.inftech.hs-mannheim.de: `Disallow: /fileadmin/` for all robots | https://www.inftech.hs-mannheim.de/fileadmin/user_upload/fakultaeten/fakultaet_n_neu/PDF/Modulhandbuecher/Master-Modulhandbuch_ab_Studienstart_SS2025.pdf (page: https://www.inftech.hs-mannheim.de/masterstudiengaenge/technische-informatik.html) | Master-Modulhandbuch ab Studienstart SS 2025 (open in the browser, save as) | `thm_ma_technische_informatik_security_iiot.pdf` |
| 2 | Cyber Security M.Sc. (berufsbegleitend), Hochschule Aalen (145 km) | SPO 511 link from search returns HTTP 404 (moved) | https://www.hs-aalen.de/en/study-programmes/computer-science-artificial-intelligence/part-time/cyber-security/ (old link: https://www.hs-aalen.de/uploads/mediapool/media/file/43955/MAW-TB-CSC-511.pdf) | Current SPO Teil B MAW-TB-CSC-511 (module names and ECTS); a module handbook instead if one is now published | `aalen_ma_cyber_security_spo.pdf` (handbook: `aalen_ma_cyber_security.pdf`) |
| 3 | Cyber Security Engineer M.Sc. (weiterbildend), TH Ingolstadt (82 km) | No official handbook. The SPO module annex exists only on a third-party mirror, whose robots.txt is contradictory (`Disallow: /` and `Disallow: *.pdf`, but `Allow: /media/`); treated as blocked | https://static.studycheck.de/media/documents/course_documents/thi/msc_cyber-security-engineer/655216ca96e00_2022-12-12-spo-cybersecurity-anlage-1.pdf (page: https://www.thi.de/en/lifelong-learning/study-courses/cyber-security-engineer-msc/) | Optional: SPO 12.12.2022, Anlage 1 (module annex). Label: third-party mirror (StudyCheck), not THI. If skipped: "no official handbook" | `thi_ma_cyber_security_engineer_spo.pdf` |

Notes
- An SPO is only a fallback: it lists modules and ECTS but not their content.
- Outdated automatic download: THI MA Cloud Applications und Security Engineering is "Stand 28.09.2023". If the THI
  page has a newer version, save it as `thi_ma_cloud_applications_security_engineering_new.pdf` (optional).
