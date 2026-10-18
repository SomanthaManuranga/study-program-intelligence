import streamlit as st

from common import evidence, figure, metric, show

st.title("Claim A: demand")
st.markdown("Official statistics have no cybersecurity subject, so demand is read through computer-science entrants, "
            "search interest and the supply of programmes.")

c = st.columns(4)
metric("Informatik first-years, Bavaria, 2019-24 / yr", "informatik_firstyears_by_growth", c[0])
metric("Bavarian cyber proxy 2024", "cyber_proxy_by_2024", c[1])
metric("2030 central (planning midpoint)", "cyber_proxy_by_2030_central", c[2])
metric("2030 conservative (KMK)", "cyber_proxy_by_2030_conservative", c[3])

figure("f01_demand_forecast")
st.caption(f"Drift is the best model in all four series (MASE {show('forecast_mase_drift_by_cyber')} vs naive "
           f"{show('mase_naive_by_cyber')} for the Bavarian cyber proxy). The central value is a chosen midpoint, not a model output.")

st.subheader("Search interest")
c = st.columns(3)
metric("'Cyber Security Studium' vs KI", "search_cyber_vs_ki", c[0])
metric("... vs Robotik", "search_cyber_vs_robotik", c[1])
metric("Share of Informatik searches 2026", "cyber_share_of_informatik_search", c[2])
figure("f02_search_interest")
st.caption("Cybersecurity is the largest specialist term, but on a plateau since 2022.")

st.subheader("Supply")
c = st.columns(4)
metric("Dedicated cyber bachelors, Germany", "cyber_ba_germany", c[0])
metric("... within 150 km of OTH", "cyber_ba_150km", c[1])
metric("Dedicated cyber masters within 150 km", "cyber_ma_150km", c[2])
metric("Security focus areas, 150 km", "cyber_focus_150km", c[3])

evidence("docs/evidence_forecast.md", "docs/evidence_demand_trends.md", "docs/evidence_competition_demand.md",
         "docs/theme_precision.md", strength="strong for the field trend, medium for cybersecurity itself")
