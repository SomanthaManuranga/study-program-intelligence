"""Cross-check app (local only): run with  streamlit run app_crosscheck/app.py"""

import streamlit as st

st.set_page_config(page_title="New study programme: cross-check", page_icon="🎓", layout="wide")

import state  # noqa: E402

rules = state.sidebar_rules()
res = state.results(rules)
st.session_state.rules, st.session_state.res = rules, res

pages = [
    st.Page("views/overview.py", title="Overview", icon="🧭", default=True),
    st.Page("views/sources.py", title="Data sources", icon="🗂️"),
    st.Page("views/funnel.py", title="Funnel and removals", icon="🔻"),
    st.Page("views/ranking.py", title="Ranking", icon="🏆"),
    st.Page("views/candidate.py", title="Candidate details", icon="🔍"),
    st.Page("views/timetable.py", title="Handbook vs timetable", icon="📅"),
    st.Page("views/robustness.py", title="Robustness", icon="🧪"),
    st.Page("views/compare.py", title="Compare with Somantha", icon="🤝"),
]
state.banner(res)
st.navigation(pages).run()
