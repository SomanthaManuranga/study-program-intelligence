"""Study Program Intelligence dashboard (Step 52). Local only.

Run from the repository root with the venv active:

    streamlit run app/dashboard.py

Pages live in app/views/. All numbers come from reports/key_numbers.yaml and data/interim (see app/common.py).
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))   # so views can import common

st.set_page_config(page_title="Study Program Intelligence", page_icon=":material/school:", layout="wide")

VIEWS = Path(__file__).resolve().parent / "views"
pages = [
    st.Page(VIEWS / "overview.py", title="Overview", url_path="overview", default=True),
    st.Page(VIEWS / "demand.py", title="A Demand", url_path="demand"),
    st.Page(VIEWS / "capture.py", title="B Capture", url_path="capture"),
    st.Page(VIEWS / "fit.py", title="C Fit", url_path="fit"),
    st.Page(VIEWS / "outlet.py", title="D Outlet", url_path="outlet"),
    st.Page(VIEWS / "cannibalisation.py", title="Cannibalisation", url_path="cannibalisation"),
    st.Page(VIEWS / "ranking.py", title="Ranking explorer", url_path="ranking"),
    st.Page(VIEWS / "sources.py", title="Sources and method", url_path="sources"),
]
st.navigation(pages).run()
