# Manual downloads

Files the scripts do not fetch (robots.txt, login, or no public link found). Save each file exactly under
"Target file" (folder relative to the repo root), then tell Claude; Claude adds URL, date and SHA-256 to the
manifest named in the section, with status "manual".

## Step 39: competitor module handbooks (17 Oct 2026)

Folder: `data/raw/competitor modules/`. Manifest: `docs/competitor_modules_manifest.json`.
Downloaded automatically (6): FAU BA, THI BA Cybersicherheit, THI MA Cloud Applications und Security Engineering,
TH Deggendorf MA Cyber Security, THWS BA Informationssicherheit, HDBW MA Cyber Security.

| # | Programme | Why manual | Page link | What to download | Target file |
|---|---|---|---|---|---|
| 1 | Cyber Security B.Sc., TH Deggendorf (105 km) | Search found the handbook only on cs-mariakirchen.th-deg.de, which does not resolve (DNS error) | https://www.th-deg.de (Studierende > Anträge und Organisatorisches > Modulhandbücher); likely the same file at https://www.th-deg.de/Studierende/Antraege-und-Organisatorisches/Modulhandbuecher/modulhandbuch_cy_bachelor_2024.pdf (not checked) | Current Modulhandbuch Bachelor Cyber Security (Prüfungsordnung 10.07.2024 or newer), German | `deg_ba_cyber_security.pdf` |
| 2 | Cyber Security Engineer M.Sc. (weiterbildend), TH Ingolstadt (82 km) | No handbook PDF found | https://www.thi.de/en/lifelong-learning/study-courses/cyber-security-engineer-msc/ | Modulhandbuch; if none is published, the SPO with module annex (SPO of 12.12.2022 or newer) | `thi_ma_cyber_security_engineer.pdf` (SPO: `thi_ma_cyber_security_engineer_spo.pdf`) |
| 3 | Sociotechnical Cybersecurity M.Sc., TH Ingolstadt (82 km) | No handbook PDF found (new programme, SPO of 07.07.2025) | https://www.thi.de/en/computer-science/news-and-events/news-in-the-faculty/news/cybersecurity-mit-weitblick-technische-hochschule-ingolstadt-thi-bringt-interdisziplinaeren-master-an-den-start/ ; SPO notice: https://www.thi.de/fileadmin/daten/recht/Amtliche_Bekanntmachungen/Okt_2025/2025_10_24_Bekanntgabe_SPO_MA_SOC.pdf | Modulhandbuch (THI pattern would be MHBuch_SOC-M.pdf); if none, the SPO notice above | `thi_ma_sociotechnical_cybersecurity.pdf` (SPO: `thi_ma_sociotechnical_cybersecurity_spo.pdf`) |
| 4 | Cyber Security M.Sc. (berufsbegleitend, formerly IT-Sicherheitsmanagement), Hochschule Aalen (145 km) | No handbook for the current SPO 511 found; only the old SPO 501 handbook (IT-Sicherheitsmanagement) | https://www.hs-aalen.de/en/study-programmes/computer-science-artificial-intelligence/part-time/cyber-security/ ; SPO 511: https://www.hs-aalen.de/uploads/mediapool/media/file/43955/MAW-TB-CSC-511.pdf | Modulhandbuch for SPO 511 (Cyber Security); if none, the SPO 511 PDF above | `aalen_ma_cyber_security.pdf` (SPO: `aalen_ma_cyber_security_spo.pdf`) |
| 5 | Technische Informatik - Security und Industrial Internet of Things M.Sc., TH Mannheim (244 km; benchmark, industrial/OT security) | No handbook PDF found | https://www.inftech.hs-mannheim.de/masterstudiengaenge/technische-informatik.html ; https://www.hs-mannheim.de/master-technische-informatik.html | Modulhandbuch Master Technische Informatik (current SPO), with the Security and IIoT tracks | `thm_ma_technische_informatik_security_iiot.pdf` |

Notes
- If a page offers several versions, take the newest for the current SPO and note its "Stand" date.
- An SPO is only a fallback: it lists modules but usually not their content. Say which one you took.
- Outdated automatic download: THI MA Cloud Applications und Security Engineering is "Stand 28.09.2023". If the THI
  page has a newer version, save it as `thi_ma_cloud_applications_security_engineering_new.pdf` (optional).
