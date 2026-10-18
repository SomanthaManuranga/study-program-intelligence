import streamlit as st

from common import doc_link, report_section

from study_program_intelligence.report.draft import table_sources

st.title("Sources and method")

st.subheader("Use of AI tools")
st.markdown(report_section("01_method.md", "Use of AI tools"))

st.subheader("Method decisions")
st.markdown(report_section("A2_decisions.md").replace("## A2 Method decisions {-}", ""))

st.subheader("Data sources")
st.markdown(table_sources())
st.caption("Full register: " + doc_link("configs/sources.yaml") + " · downloads with date and SHA-256 in the manifests in docs/ · "
           "decision log: " + doc_link("docs/decision_log.md"))
