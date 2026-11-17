"""Shared helpers for the independent cross-check (method: docs/crosscheck/method.md)."""

from __future__ import annotations

import difflib
import re
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[3]
RAW = REPO / "data" / "raw"
PROCESSED = REPO / "data" / "processed"
OUT = REPO / "data" / "interim" / "crosscheck"          # git-ignored working tables
DOCS = REPO / "docs" / "crosscheck"                      # committed method and results

# OTH programmes per (subject, level): a kind whose subject an OTH programme of the same level lists is flagged
# "relabel risk" and goes first to the handbook test (Step 2 cannot be decided from catalogue topics, see results).

# EMI's own catalogue offers (titles in data/processed/programmes_full.csv)
EMI_OFFERS = {73209589, 123052702, 73209645, 120874688, 73209604, 73209637, 73209627, 73209623, 73209620,
              106484148, 109780672, 334031608}
# generic subjects of EMI offers that do not describe EMI's field (Applied Research lists Maschinenbau,
# Educational Technology lists Erziehungswissenschaft)
EMI_SUBJECT_EXCLUDE = {"Maschinenbau", "Erziehungs-, Bildungswissenschaft"}

EMI_PROGRAMME_NAMES = {
    "oth26_ba_dd": "Digital Design (BA)", "oth26_ba_ei": "Elektro- und Informationstechnik (BA)",
    "oth26_ba_gi": "Geoinformatik und Landmanagement (BA)", "oth26_ba_ii": "Informatik-Studiengang II (BA)",
    "oth26_ba_iki": "Industrie-4.0-Informatik (BA)", "oth26_ba_ki": "Kuenstliche Intelligenz (BA)",
    "oth26_ba_mi": "Medieninformatik (BA)", "oth26_ba_mt": "Medienproduktion und Medientechnik (BA)",
    "oth26_ma_edu": "Educational Technology (MA)", "oth26_ma_ia": "IT und Automation (MA)",
    "oth26_ma_mai": "AI for Industrial Applications (MA)", "oth26_ma_mapr": "Applied Research (MA)",
    "oth26_ma_mki": "Kuenstliche Intelligenz (MA)", "oth26_ma_mp": "Medientechnik und Medienproduktion (MA)",
}


def base_subject(s: str) -> str:
    """'Informatik (grundstaendig)' -> 'Informatik'."""
    return re.sub(r"\s*\((?:grundständig|weiterführend)[^)]*\)\s*$", "", s.strip())


def subjects_of(cell) -> list[str]:
    if not isinstance(cell, str):
        return []
    return [base_subject(x) for x in cell.split(";") if x.strip()]


def load_universe() -> pd.DataFrame:
    """Full-time bachelor and master offers in Germany, one row per offer, with level and base subjects."""
    d = pd.read_csv(PROCESSED / "programmes_full.csv", low_memory=False, dtype={"programme_id": str})
    d = d[d.degree.isin(["Bachelor/Bakkalaureus", "Master"]) & (d.study_form == "Vollzeitstudium")].copy()
    d["level"] = d.degree.map({"Bachelor/Bakkalaureus": "BA", "Master": "MA"})
    d["subj"] = d.subjects.map(subjects_of)
    teacher = d.subj.map(lambda xs: any(x.startswith(("Lehramt", "Lernbereich")) for x in xs)) | \
        d.title.str.contains(r"Lehramt|Master of Education", case=False, na=False)
    d = d[~teacher]
    return d


def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"\(ab \d\d.*?\)|a\.n\.g\.|\(allg.*?\)", " ", s)
    s = re.sub(r"[/,\-–.()]", " ", s)
    s = re.sub(r"\b(und|u|allg|allgemein|wiss|wissenschaft|wesen)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# catalogue subject -> Destatis Studienfach, for subjects whose name differs (decided before any demand number was
# looked at; fine subjects share their parent's pool)
DESTATIS_MAP = {
    "IT-Sicherheit": "Informatik", "Datenwissenschaft, Data Science": "Informatik",
    "Künstliche Intelligenz": "Informatik", "Softwaretechnik": "Informatik", "Computervisualistik": "Informatik",
    "Umweltinformatik": "Informatik", "Verwaltungsinformatik": "Informatik",
    "Robotik, Autonome Systeme": "Mechatronik", "Technische Informatik": "Ingenieurinformatik/Technische Informatik",
    "Ingenieurinformatik, Computational Engineering": "Ingenieurinformatik/Technische Informatik",
    "Fahrzeuginformatik, -elektronik": "Ingenieurinformatik/Technische Informatik",
    "Informations-, Kommunikationstechnik": "Kommunikations- und Informationstechnik",
    "Elektrotechnik": "Elektrotechnik/Elektronik", "Elektromobilität": "Elektrotechnik/Elektronik",
    "Medien-, Multimediatechnik": "Medientechnik", "Druck-, Medientechnik": "Medientechnik",
    "Medienproduktion": "Medientechnik", "Geoinformatik": "Vermessungswesen (Geodäsie)",
    "Vermessungstechnik": "Vermessungswesen (Geodäsie)", "Sensortechnik": "Mikrosystemtechnik",
    "Mikrotechnik, Mikrosystemtechnik": "Mikrosystemtechnik", "Photonik, Optische Technologien": "Optoelektronik",
    "Kommunikationsdesign, visuelle Kommunikation": "Grafikdesign/Kommunikationsgestaltung",
    "Medienwirtschaft, -management": "Medienwirtschaft/Medienmanagement",
    # added after v1 (data cleaning: subjects without an exact Destatis name; decided by name, not by result)
    "Automatisierungstechnik": "Elektrotechnik/Elektronik", "Kybernetik": "Technische Kybernetik",
    "Design": "Grafikdesign/Kommunikationsgestaltung", "Mediendesign, -kunst": "Grafikdesign/Kommunikationsgestaltung",
    "Gamedesign, Interactiondesign": "Grafikdesign/Kommunikationsgestaltung",
    "Film-, Fernsehproduktion": "Film und Fernsehen", "Film-, Fernsehkamera": "Film und Fernsehen",
    "Regie": "Darstellende Kunst/Bühnenkunst/Regie", "Audio-, Sounddesign": "Tonmeister", "Ton-, Bildtechnik": "Tonmeister",
    "Produktentwicklung": "Industriedesign/Produktgestaltung", "Computermathematik": "Mathematik",
    "Digitale Geisteswissenschaften/Computerphilologie": "Computerlinguistik",
    "Mensch-Maschine-Interaktion, Interfacedesign": "Informatik",
}


def destatis_match(subject: str, labels: list[str]) -> tuple[str | None, str]:
    """Map a catalogue subject to a Destatis Studienfach label: manual map, exact, normalised, or fuzzy."""
    if subject in DESTATIS_MAP:
        tgt = DESTATIS_MAP[subject]
        if tgt in labels:
            return tgt, "manual"
        m = difflib.get_close_matches(tgt, labels, n=1, cutoff=0.6)
        return (m[0], "manual~") if m else (None, "manual-missing")
    if subject in labels:
        return subject, "exact"
    nl = {norm(x): x for x in labels}
    if norm(subject) in nl:
        return nl[norm(subject)], "normalised"
    m = difflib.get_close_matches(norm(subject), list(nl), n=1, cutoff=0.92)   # v1 used 0.8: false matches
    return (nl[m[0]], "fuzzy") if m else (None, "none")


def write(df: pd.DataFrame, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / name
    df.to_csv(p, index=False)
    return p
