import pandas as pd
import streamlit as st

from common import evidence, figure, metric, show

st.title("Claim B: capture")

c = st.columns(4)
metric("OTH's own pool (2023/24)", "own_pool_exact", c[0])
metric("... via FOS/BOS", "own_pool_fosbos_share", c[1])
metric("Closer to OTH than to Deggendorf", "catchment_closer_to_oth", c[2])
metric("Closer to OTH than to Nuremberg", "closer_than_nuernberg", c[3])

c = st.columns(4)
metric("Distance decay (calibrated)", "gravity_beta", c[0])
metric("Fit on Bavarian student flows", "gravity_r2", c[1])
metric("Anchor: THI capacity", "thi_cyber_capacity", c[2])
metric("Anchor: TH Deggendorf (anecdote)", "deg_cyber_anecdote", c[3])

st.subheader("Expected first-years, Cybersecurity B.Sc.")
st.dataframe(pd.DataFrame({
    "Scenario": ["Low", "Central", "High"],
    "Anchor": [f"THI intake = capacity {show('thi_cyber_capacity')}", "geometric mean (a choice)",
               f"TH Deggendorf {show('deg_cyber_anecdote')} (weak)"],
    "Year 1": [show("year1_low"), show("year1_central"), show("year1_high")],
    "Steady state": [show("cyber_bsc_gross_low"), show("cyber_bsc_gross_central"), show("cyber_bsc_gross_high")],
}), hide_index=True, width="stretch")
st.caption(f"Assumed minimum cohort: {show('min_cohort')} first-years a year (no rule found). The uncalibrated demand model "
           f"implied {show('thi_implied')} for THI, so the model is used for relative capture only "
           f"({show('rel_capture_thi')} THI's intake).")
figure("f04_capture")
evidence("docs/evidence_catchment.md", "docs/evidence_capture.md", strength="medium (anchors are a capacity and an anecdote)")
