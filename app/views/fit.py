import pandas as pd
import streamlit as st

from common import evidence, metric, show

st.title("Claim C: fit with EMI")

c = st.columns(4)
metric("EMI covers: general foundations", "emi_cover_gen_ba", c[0])
metric("EMI covers: security content (upper end)", "emi_cover_sec_ba", c[1])
metric("... TF-IDF cross-check", "cover_sec_ba_tfidf", c[2])
metric("... of a cyber master", "emi_cover_sec_ma", c[3])

st.subheader("Security areas (CyBOK): what EMI already covers")
st.dataframe(pd.DataFrame({
    "Area": ["Cryptography", "Network security", "Forensics", "Penetration testing & auditing",
             "Security operations & incident management"],
    "EMI covers": [show(k) for k in ("crypto_cover", "network_cover", "forensics_cover", "pentest_cover", "secops_cover")],
}), hide_index=True, width="stretch")
st.caption(f"Module pairs checked by hand: embeddings right in {show('pairs_e5')}, TF-IDF in {show('pairs_tfidf')}. "
           "All embedding errors were false 'covered', so coverage is an upper-end estimate.")

st.subheader("Staff, labs and a draft curriculum")
c = st.columns(4)
metric("EMI profs teaching security (about)", "security_profs", c[0], bare=True)
metric("New teaching load per year", "new_load_sws", c[1])
metric("New professorships", "new_professorships", c[2], bare=True)
metric("Security ECTS in the draft (of 210)", "draft_security_ects", c[3])
st.markdown(f"Draft: {show('draft_new_ects')} taught by new staff, {show('teaching_assignments')} by teaching assignments, "
            f"{show('draft_reused_ects')} reused from EMI. OT security is not a differentiator against TH Deggendorf "
            f"({show('deg_ma_ot')} of OT modules in its master). Plus one lab engineer and an isolated security lab (cost not estimated).")
evidence("docs/evidence_fit_modules.md", "docs/evidence_fit_staff.md", "docs/evidence_benchmarks.md",
         strength="strong for the module comparison, medium for staffing")
