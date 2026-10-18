import pandas as pd
import streamlit as st

from common import evidence, figure, metric, show

st.title("Claim D: graduate outlet")
st.caption(f"BA job board, snapshot {show('job_snapshot_date')}; further snapshots until the 4 Dec freeze.")

st.dataframe(pd.DataFrame({
    "Keyword": ["Cyber Security", "OT Security", "Robotik (comparison)"],
    "Germany": [show("ads_cyber_security_de"), show("ads_ot_security_de"), show("ads_robotik_de")],
    "Bavaria's share": [show("ads_cyber_security_by_share"), show("ads_ot_security_by_share"), show("ads_robotik_by_share")],
    "Within 100 km of Amberg": [show("ads_cyber_security_amberg_100km"), show("ads_ot_security_amberg_100km"),
                                show("ads_robotik_amberg_100km")],
}), hide_index=True, width="stretch")
st.caption(f"IT baseline keywords: Bavarian share {show('baseline_share')}.")
figure("f03_job_ads")

c = st.columns(4)
metric("IT jobs in Bavaria 2019-23", "it_jobs_by_growth", c[0])
metric("... held by graduates", "it_jobs_by_academic_growth", c[1])
metric("Academic share 2023", "academic_share_2023", c[2])
metric("Shortage score, Informatik (BA)", "shortage_score", c[3])
st.markdown("At master (expert) level software development is no longer a shortage occupation, so the outlet argument is "
            "strongest for a bachelor.")
evidence("docs/evidence_outlet_jobs.md", strength="medium (keyword counts are indicators, not vacancies)")
