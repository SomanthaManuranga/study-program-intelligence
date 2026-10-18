import altair as alt
import pandas as pd
import streamlit as st

from common import LABEL, OPTION, csv, evidence, figure, metric, show

st.title("Incrementality: where the students would come from")
st.markdown("(a) taken from existing OTH programmes · (b) won from other universities = net new to OTH · "
            "(c) part of (b) kept in the region who would otherwise have left.")

scen = st.segmented_control("Scenario", ["low", "central", "high"], default="central")
d = csv("option_scenarios.csv")
d = d[d["scenario"] == (scen or "central")].set_index("option").loc[list(OPTION)]
table = pd.DataFrame({
    "Option": [LABEL[o] for o in d.index],
    "Gross first-years": d["gross first-years"].round(1),
    "(a) from OTH": d["(a) from OTH programmes"].round(1),
    "(b) net new to OTH": d["(b) net new to OTH"].round(1),
    "(c) kept in region": d["(c) kept in region"].round(1),
    "Net-new share": (100 * d["net-new share"]).round(0).astype(int).astype(str) + " %",
})
st.dataframe(table, hide_index=True, width="stretch")

long = table.melt(id_vars="Option", value_vars=["(a) from OTH", "(b) net new to OTH"], var_name="Part", value_name="First-years")
chart = alt.Chart(long).mark_bar(cornerRadiusEnd=4).encode(
    y=alt.Y("Option:N", sort=list(LABEL.values()), title=None, axis=alt.Axis(labelOverlap=False, labelLimit=220)),
    x=alt.X("First-years:Q", stack=True, title=f"First-years per year ({scen or 'central'} scenario)"),
    color=alt.Color("Part:N", scale=alt.Scale(range=["#BFBFBF", "#1F4E79"]), legend=alt.Legend(orient="top", title=None)),
    tooltip=["Option", "Part", "First-years"],
).properties(height=240)
st.altair_chart(chart, width="stretch")

c = st.columns(3)
metric("Cyber B.Sc.: share from OTH", "cyber_bsc_from_oth_range", c[0])
metric("Net new if cannibalisation were 50 %", "stress_netnew", c[1])
metric("Kill rule 1: core-module overlap", "cyber_bsc_core_overlap", c[2])
st.caption(f"Kill rule 1 drops a candidate at {show('kill_rule_1_threshold')} overlap; no separate cannibalisation threshold "
           f"was added after scoring. Robotics overlaps {show('robotics_overlap')} with OTH's KI B.Sc.; with half its students "
           f"from OTH only {show('robotics_netnew_cannib50')} a year would be new.")
figure("f05_cannibalisation")
evidence("docs/evidence_cannibalisation.md", "docs/evidence_ranking.md", "docs/overlap_test.md", strength="medium")
