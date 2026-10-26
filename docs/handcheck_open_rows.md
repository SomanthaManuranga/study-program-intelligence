# Hand check: the three open rows, side by side (facts only, no proposed verdict)

Rows 3, 7 and 9 of `docs/handcheck_sheet.md`. Every handbook statement is quoted word for word in German with its
PDF page (`[file p. N]`, page index of the PDF file as opened, not the printed page number), followed by an English
rendering. Quote check: `tests/test_handcheck_open_rows.py` finds every quote on its stated page (also quotes that
wrap a line; letters and digits are compared, punctuation and spacing ignored). Files:
`data/raw/references/ref_visual_computing_coburg.pdf` (Hochschule Coburg), `data/raw/anchors/hske_ba_robotik.pdf`
(Hochschule Kempten), `data/raw/oth handbooks 2026/oth_hb_ii_mi_ba.pdf` (OTH Industrie-4.0-Informatik / Medieninformatik),
`oth_hb_ei_ba_2022.pdf` (OTH E&IT), `oth_hb_iki_ba.pdf` (OTH KI International) in the same folder, and
`data/raw/oth modules/Künstliche Intelligenz (B.Sc.).pdf` (OTH KI, the copy used in the EMI module table).

## Row 3: Coburg "Mathematik für Visual Computing" vs OTH "Mathematik 3" (II)

Frame: Coburg „Leistungspunkte 5 ECTS Arbeitsaufwand 150h Fachsemester 3“ [ref_visual_computing_coburg.pdf p. 43]
(5 ECTS, 150 h, semester 3). OTH „Pflichtmodul im 3. Semester, Studiengänge Industrie-4.0- Informatik“
[oth_hb_ii_mi_ba.pdf p. 33] (compulsory module in semester 3); „MA3 Pflichtmodul 5“ [oth_hb_ii_mi_ba.pdf p. 33] (5 ECTS).

Learning outcomes, Coburg:
- „Koordinatentransformationen und Rotationsrepräsentationen in 2D und 3D kennen, verstehen und anwenden“ [ref_visual_computing_coburg.pdf p. 43] (know, understand and apply coordinate transformations and rotation representations in 2D and 3D)
- „Optimierungsverfahren kennen, verstehen und anwenden“ [ref_visual_computing_coburg.pdf p. 43] (optimisation methods)
- „Elemente und Verfahren der multivariaten Analysis kennen und anwenden“ [ref_visual_computing_coburg.pdf p. 43] (multivariable calculus; German "Analysis" means calculus)
- „Eigenwerte bestimmen und Singulärwertzerlegungen durchführen können“ [ref_visual_computing_coburg.pdf p. 43] (eigenvalues and singular value decomposition)

Learning outcomes, OTH: „mehrdimensionale Extremwertbestimmung, Eigenwertrechnung“ [oth_hb_ii_mi_ba.pdf p. 33]
(multidimensional extreme values, eigenvalue computation, named as examples of the methods students master).

Contents, item by item. Coverage is Claude's reading of the two contents lists, shown so Soma can check it:

| Coburg contents item (quote) | OTH Mathematik 3 contents (quote) | Coverage |
|---|---|---|
| „Koordinatentransformationen“ [ref_visual_computing_coburg.pdf p. 43] | „Eigenwertrechnung und Basistransformation“ [oth_hb_ii_mi_ba.pdf p. 33] (change of basis) | partly: a change of basis is listed, coordinate transformations as such are not |
| „Rotationsrepräsentationen in 3D (Matrixdarstellung, Komplexe Zahlen, Eulersche Winkel, Quaternionen, Rodrigues-Rotation, SO3, Lie-Algebra)“ [ref_visual_computing_coburg.pdf p. 43] | „Skalarprodukt und orthogonale Abbildungen“ [oth_hb_ii_mi_ba.pdf p. 33] (orthogonal maps) | partly: orthogonal maps (the matrix form of rotations) are listed; Euler angles, quaternions, Rodrigues rotation, SO3 and Lie algebra are not |
| „Methode der kleinsten Quadrate“ [ref_visual_computing_coburg.pdf p. 43] (least squares) | not listed | missing |
| „Lineare Optimierung, lineare Ausgleichsrechnung“ [ref_visual_computing_coburg.pdf p. 43] (linear optimisation, linear adjustment) | not listed | missing |
| „Nicht-lineare Optimierung“ [ref_visual_computing_coburg.pdf p. 43] (non-linear optimisation) | „mehrdimensionale Differentialrechnung, Extrema“ [oth_hb_ii_mi_ba.pdf p. 33] (multivariable calculus, extrema) | partly: extrema of functions of several variables are listed, optimisation methods are not |
| „Multivariate Analysis (Kurven, Flächen)“ [ref_visual_computing_coburg.pdf p. 43] (multivariable calculus: curves, surfaces) | „mehrdimensionale Differentialrechnung, Extrema“ [oth_hb_ii_mi_ba.pdf p. 33] | partly: multivariable calculus is listed, curves and surfaces are not |
| „Eigenwerte und Singulärwertzerlegung“ [ref_visual_computing_coburg.pdf p. 44] (eigenvalues and SVD) | „Eigenwertrechnung und Basistransformation“ [oth_hb_ii_mi_ba.pdf p. 33] | eigenvalues covered; singular value decomposition not listed |

The five topics Soma asked about (decision log, 2026-10-26, part 1): 3D rotations partly; coordinate transforms
partly; optimisation partly (extrema) and missing (least squares, linear optimisation); multivariable calculus
("multivariate analysis") partly; eigenvalues covered (SVD missing).

OTH Mathematik 3 also teaches what the Coburg module does not list: „Taylor- und Fourier-Reihen“
[oth_hb_ii_mi_ba.pdf p. 33] (Taylor and Fourier series) and „gewöhnliche Differentialgleichungen“
[oth_hb_ii_mi_ba.pdf p. 33] (ordinary differential equations).

Share of new content (Claude's count, method stated): the Coburg contents list has 8 items when the SVD is counted
apart from the eigenvalues (coordinate transformations, 3D rotations, least squares, linear optimisation, non-linear
optimisation, multivariable calculus, eigenvalues, SVD). Covered 1, partly 4, missing 3. New content is therefore
between 3 of 8 items (38 %, partly-covered items counted as existing) and 7 of 8 (88 %, partly-covered items counted
as new). The handbooks give no hours per item, so a share of hours cannot be computed. For reference, the definition
of an adapted module (E2) in `configs/feasibility.yaml` is "at most a third of the content new".

## Row 7: Coburg "Interdisziplinäre Projektarbeit" (10 ECTS) vs OTH "Software-Projekt" (II, 5 ECTS)

| | Coburg Interdisziplinäre Projektarbeit | OTH Software-Projekt (II) |
|---|---|---|
| Frame | „Lehrform / SWS Projekt / 30h Leistungspunkte 10 ECTS Arbeitsaufwand 30h Präsenzstudium, 270h Eigenarbeit Fachsemester 6“ [ref_visual_computing_coburg.pdf p. 77] (project, 10 ECTS, 30 h attendance and 270 h self-study, semester 6) | „SWP Pflichtmodul 5“ [oth_hb_ii_mi_ba.pdf p. 50] (compulsory module, 5 ECTS); „150 h, davon Kontaktstudium: 30 h (2 SWS) Eigenstudium/Teamarbeit: ca. 120 h“ [oth_hb_ii_mi_ba.pdf p. 50] (150 h: 30 h contact, about 120 h self-study and team work) |
| Learning outcomes and contents | Outcomes: „Anforderungsanalyse, Software-Architektur, Software- Entwicklung, Software-Testen, Projektmanagement auf einer komplexen, interdisziplinären Problemstellung in einem Anwendungsfeld des Visual Computing“ [ref_visual_computing_coburg.pdf p. 77] (requirements, architecture, development, testing and project management on a complex interdisciplinary problem in a visual-computing application field). Contents: „Werkzeuge, Methoden und Techniken der Software- Entwicklung und Software-Architektur-Entwurfs“ [ref_visual_computing_coburg.pdf p. 78] (tools, methods and techniques of software development and architecture design) | „Ein Auftrag zur Neu- oder Weiterentwicklung eines Software-Produkts“ [oth_hb_ii_mi_ba.pdf p. 50] (an assignment to develop a new or extend an existing software product); „die Aufgabenstellungen haben daher i.A. nicht kommerziellen Charakter“ [oth_hb_ii_mi_ba.pdf p. 50] (tasks are generally non-commercial) |
| Format and team | „Realisierung einer komplexen, interdisziplinären Software-Aufgabenstellung im Team von bis zu 5 Personen“ [ref_visual_computing_coburg.pdf p. 78] (teams of up to 5) | „Eigenständige Durchführung eines kleineren Software- Entwicklungsprojekts in einem studentischen Team“ [oth_hb_ii_mi_ba.pdf p. 50] (a smaller software project in a student team); team size not stated |
| Supervision | „Dozenten des Visual Computing“ [ref_visual_computing_coburg.pdf p. 77] (lecturers of visual computing); hours per group not stated | „Beratung durch Betreuer nach Bedarf“ [oth_hb_ii_mi_ba.pdf p. 50] (advice from supervisors as needed); hours per group not stated |
| Assessment | „Endnotenbildende Studien- / Prüfungsleistungen Praktische Studienarbeit“ [ref_visual_computing_coburg.pdf p. 78] (practical project work) | „Arbeitsergebnis des gesamten Teams: 40% Inhalt der persönlichen Reflexionsberichte und Zeitprotokolle: 60%“ [oth_hb_ii_mi_ba.pdf p. 51] (team result 40 %, personal reflection reports and time logs 60 %) |

Supervision effort per student group: **no data + reason**: neither handbook states supervisor hours per group.
What they state: Coburg 30 h attendance per student and teams of up to 5; OTH 30 h contact (2 SWS) and advice as
needed. The workloads differ by a factor of two: 300 h (30 + 270) against 150 h.

## Row 9: Kempten RO 31 "Wissenschaftliches Arbeiten und statistische Datenanalyse" vs OTH "Data Analytics" (II) and "Stochastik" (KI)

Frame: RO 31 „Vertiefungsstudium, 3. Semester“ [hske_ba_robotik.pdf p. 62] (semester 3); „Vorlesung: 2 SWS 3 LP
Praktikum, Übung: 2 SWS 2 LP“ [hske_ba_robotik.pdf p. 62] (lecture 3 credits, lab/exercise 2 credits; the handbook
does not split the 5 credits between part 1 and part 2).

| RO 31 contents (quote) | OTH Data Analytics (II) | OTH Stochastik (KI) |
|---|---|---|
| Part 1: „Zielsetzung wissenschaftlichen Arbeitens“ [hske_ba_robotik.pdf p. 65] (aims of scientific work) | not listed | not listed |
| „Grundlagen- und anwendungsorientiertes Forschen“ [hske_ba_robotik.pdf p. 65] (basic and applied research) | not listed | not listed |
| „Formulierung wissenschaftlicher Fragestel- lungen und Hypothesen“ [hske_ba_robotik.pdf p. 65] (research questions, hypotheses) | not listed | not listed |
| „Durchführung von Literaturrecherchen, Quellenarbeit“ [hske_ba_robotik.pdf p. 65] (literature search) | not listed | not listed |
| „Wissenschaftliches Schreiben (Stil der Ab- fassung wissenschaftlicher Arbeiten, wis- senschaftliches Zitieren“ [hske_ba_robotik.pdf p. 65] (scientific writing, citation) | not listed | not listed |
| „Lern- und Arbeitstechniken“ [hske_ba_robotik.pdf p. 65] (learning and working techniques) | not listed | not listed |
| „Ethische Aspekte wissenschaftlichen Arbei- tens“ [hske_ba_robotik.pdf p. 65] (research ethics) | not listed | not listed |
| Part 2: „Statistische Versuchsplanung, Design of Experiments (DoE)“ [hske_ba_robotik.pdf p. 65] | not listed | not listed |
| „Charakterisierung von Stichprobe und Grundgesamtheit“ [hske_ba_robotik.pdf p. 65] (sample and population) | not listed | „Stichproben, Gesetz der großen Zahl, Parameterschätzung, Hypothesentest“ [Künstliche Intelligenz (B.Sc.).pdf p. 32] (samples, law of large numbers, estimation, hypothesis test) |
| „Statistische Tests“ [hske_ba_robotik.pdf p. 65] | not listed | „Hypothesentest“ [Künstliche Intelligenz (B.Sc.).pdf p. 32] |
| „Korrelation • Regression • Klassifikation“ [hske_ba_robotik.pdf p. 65] | „Deskriptive und prädiktive Datenanalyse“ [oth_hb_ii_mi_ba.pdf p. 22] (descriptive and predictive analysis); „Einführung in Machine Learning“ [oth_hb_ii_mi_ba.pdf p. 22]; regression and classification are not named | „mehrdimensionale Zufallsvariablen („Zufallsvektoren“), Kovarianz und Korrelation, Grenzwertsätze“ [Künstliche Intelligenz (B.Sc.).pdf p. 32] (correlation); regression and classification not listed |
| Software: „Weiter erlernen die Studierenden den Umgang mit der auf Datenanalyse spezialisierten Sprache R“ [hske_ba_robotik.pdf p. 65] (the R language) | „Einführung in die Programmiersprache Python“ [oth_hb_ii_mi_ba.pdf p. 22]; „Datenbereinigung, -transformation und –visualisierung mit Pandas, Numpy und Matplotlib“ [oth_hb_ii_mi_ba.pdf p. 22] (Python, data cleaning and visualisation) | no software named; „Die Studierenden können grundlegende Methoden zur Darstellung und Aufbereitung empirischer Daten anwenden“ [Künstliche Intelligenz (B.Sc.).pdf p. 32] (presenting and preparing empirical data) |

Data Analytics lists basic probability and statistics as a prerequisite and does not list statistical tests, sampling or
experiment design among its contents: its prerequisites say students „sind mit den
grundlegenden Begriffen und Methoden der Stochastik und Statistik vertraut“ [oth_hb_ii_mi_ba.pdf p. 22] (are familiar
with the basic concepts and methods of probability and statistics).

**Scientific writing in existing EMI modules** (the content of RO 31 part 1):
- E&IT "Wissenschaftliches Arbeiten": „Pflichtmodul im 4. oder 5. Semester“ [oth_hb_ei_ba_2022.pdf p. 57] (compulsory,
  semester 4 or 5); „Einführung in technisch-wissenschaftliches Schreiben“ [oth_hb_ei_ba_2022.pdf p. 57] (introduction
  to technical-scientific writing); „korrekter Umgang mit fremdem geistigem Eigentum, formale Anforderungen, korrektes
  Zitieren“ [oth_hb_ei_ba_2022.pdf p. 57] (intellectual property, formal requirements, citation); „Recherchetools für
  wissenschaftliche Publikationen“ [oth_hb_ei_ba_2022.pdf p. 57] (search tools for scientific publications).
- Industrie-4.0-Informatik / Medieninformatik "Bachelorseminar": „Pflichtmodul im 6. oder 7. Semester“
  [oth_hb_ii_mi_ba.pdf p. 53] (compulsory, semester 6 or 7, i.e. with the thesis); „Einführung in wissenschaftliches
  Arbeiten Einführung in technisch-wissenschaftliches Schreiben“ [oth_hb_ii_mi_ba.pdf p. 53].
- KI International "Bachelormodul (Bachelorarbeit & Bachelorseminar)": „Bachelorseminar: Einführung in
  technisch-wissenschaftliches Schreiben“ [oth_hb_iki_ba.pdf p. 86] (part of the thesis module).
- Not found in these modules: research ethics as a named topic, statistical experiment design.
