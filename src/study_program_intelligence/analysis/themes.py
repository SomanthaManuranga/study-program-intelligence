"""Theme tagging of programmes by transparent keyword rules (baseline before NLP).

Each programme gets one boolean column per theme if the theme's pattern matches its
title or content text. Rules are deliberately simple and readable so they can be
checked by hand; the hand-labelled check (docs/methodology) measures their precision.
"""

from __future__ import annotations

import re

import pandas as pd

THEMES: dict[str, str] = {
    "ai_data": r"künstliche intelligenz|artificial intelligence|\bki\b|\bai\b|machine learning|maschinelles lernen|deep learning|data science|data analytics|data engineering|big data",
    "cybersecurity": r"cyber[- ]?secur|cybersicherheit|it-sicherheit|informationssicherheit|\bsecurity\b|sichere systeme",
    "embedded_iot": r"embedded|eingebettete|internet of things|\biot\b|cyber-physi",
    "robotics": r"robotik|robotics|roboter",
    "automation_i40": r"automatisierung|automation|industrie 4\.0|industry 4\.0|smart factory|smart manufacturing",
    "energy_emobility": r"energie|energy|elektromobil|e-mobility|electromobility|leistungselektronik|power electronics|erneuerbar|renewable|wasserstoff|hydrogen",
    "microelectronics": r"mikroelektronik|microelectronic|halbleiter|semiconductor|chip design|chipdesign|vlsi",
    "medtech_health": r"medizin|medical|health|gesundheit|biomedical",
    "games_xr": r"\bgame|games|spiele|virtual reality|augmented reality|\bxr\b|extended reality",
    "software_eng": r"software engineering|softwaretechnik|softwareentwicklung|software development",
    "media_tech": r"medientechnik|media technology|medienproduktion|media production|audio|video",
    "quantum": r"quanten|quantum",
    "aerospace": r"luft- und raumfahrt|aerospace|raumfahrt|space",
    "sustainability": r"nachhaltig|sustainab|klimaschutz|climate|green it|umwelt",
    "mobility_vehicle": r"fahrzeug|automotive|vehicle|motorsport|autonomous driving|autonomes fahren",
}


def tag(df: pd.DataFrame) -> pd.DataFrame:
    text = (df["title"].fillna("") + " " + df["content"].fillna("")).str.lower()
    out = df.copy()
    for theme, pattern in THEMES.items():
        out[f"t_{theme}"] = text.str.contains(pattern, regex=True, flags=re.IGNORECASE)
    return out
