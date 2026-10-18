"""Shared helpers for the dashboard (Step 52): data loading, key-number metrics, links, guards.

The dashboard does no analysis of its own: every number comes from reports/key_numbers.yaml or a generated table in
data/interim; the only computation is the ranking explorer, which calls analysis.ranking.simulate unchanged.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import streamlit as st

REPO = Path(__file__).resolve().parents[1]
FIG = REPO / "reports" / "figures"
INTERIM = REPO / "data" / "interim"
GITHUB = "https://github.com/SomanthaManuranga/study-program-intelligence/blob/main/"
OPTION = {"cyber_bsc": "#1F4E79", "cyber_msc": "#5B9BD5", "robotics_bsc": "#C55A11"}   # same as report figures
LABEL = {"cyber_bsc": "Cybersecurity B.Sc.", "cyber_msc": "Cyber/OT M.Sc.", "robotics_bsc": "Robotics + AI B.Sc."}
BUILD_HINT = """Run the pipeline first (from the repo root, venv active):

    python -m study_program_intelligence.analysis.options
    python -m study_program_intelligence.analysis.ranking
    python -m study_program_intelligence.report.build"""


@st.cache_data
def numbers() -> dict:
    from study_program_intelligence.report.key_numbers import load
    return load()


def require(*paths: Path) -> None:
    """Stop the page with a build hint if a generated file is missing."""
    missing = [p for p in paths if not p.exists()]
    if missing:
        st.error("Missing generated file(s): " + ", ".join(str(p.relative_to(REPO)) for p in missing))
        st.code(BUILD_HINT, language="powershell")
        st.stop()


def kn(key: str) -> dict:
    require(REPO / "reports" / "key_numbers.yaml")
    return numbers()[key]


def show(key: str) -> str:
    return kn(key)["display"]


def doc_link(path: str) -> str:
    """Markdown link to an evidence doc on GitHub."""
    return f"[{Path(path).name}]({GITHUB}{path})"


def metric(label: str, key: str, col=None, bare: bool = False) -> None:
    """A metric card whose value is the key number's display text (bare=True: its plain value, for wordy displays
    such as "2 new professorships"); hover shows the source doc."""
    e = kn(key)
    value = str(e["value"]) if bare else e["display"]
    (col or st).metric(label, value, help=f"{e['label']} ({e['display']}). Source: {e['source_doc']} (key: {key}{', bare' if bare else ''})")


def figure(name: str, caption: str | None = None, width: int = 900) -> None:
    p = FIG / f"{name}.png"
    require(p)
    st.image(str(p), caption=caption, width=width)


def evidence(*docs: str, strength: str | None = None) -> None:
    line = "**Evidence:** " + ", ".join(doc_link(d) for d in docs)
    if strength:
        line += f" · **Evidence strength:** {strength}"
    st.caption(line)


@st.cache_data
def csv(name: str) -> pd.DataFrame:
    p = INTERIM / name
    require(p)
    return pd.read_csv(p)


def report_section(file: str, heading: str | None = None) -> str:
    """Text of a report section (docs/report/), comments removed, placeholders filled from the key numbers."""
    t = (REPO / "docs" / "report" / file).read_text(encoding="utf-8")
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    if heading:
        m = re.search(rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)", t, flags=re.S | re.M)
        t = m.group(1) if m else ""
    t = re.sub(r"\[@[^\]]*\]", "", t)
    return re.sub(r"\{\{\s*(?:val:)?(\w+)\s*\}\}", lambda m: show(m.group(1)), t)
