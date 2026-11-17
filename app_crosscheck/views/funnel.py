import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import state

res, off = st.session_state.res, state.official()
st.title("Funnel and removals")
st.write("Each rule removes programme kinds or makes them not eligible. Every removal has its reason.")

c1, c2 = st.columns(2)
for col, lvl, name in [(c1, "BA", "Bachelor"), (c2, "MA", "Master")]:
    f = res["funnel"][res["funnel"].level == lvl]
    fig = go.Figure(go.Funnel(y=f.stage, x=f.remaining, textinfo="value", marker_color="#3b6ea8"))
    fig.update_layout(title=name, height=330, margin=dict(l=10, r=10, t=40, b=10))
    col.plotly_chart(fig, width="stretch")

dl = res["drop_log"].copy()
dl["value"] = dl["value"].astype(str)
dl["threshold"] = dl["threshold"].astype(str)
first = dl.groupby("kind").head(1)

st.subheader("Removed by rule")
summary = first.groupby(["step", "rule", "level"]).size().unstack("level", fill_value=0)
st.dataframe(summary, width="stretch")

st.subheader("Why each programme was removed")
f1, f2, f3, f4 = st.columns([1, 1, 1, 2])
lvl = f1.selectbox("Level", ["all", "BA", "MA"])
step = f2.selectbox("Step", ["all"] + sorted(first.step.unique()))
allr = f3.checkbox("Show every failed rule", help="Off: only the first rule each kind fails")
q = f4.text_input("Search a subject", placeholder="e.g. Medizin, Robotik, Wirtschaft")
t = dl if allr else first
if lvl != "all":
    t = t[t.level == lvl]
if step != "all":
    t = t[t.step == step]
if q:
    t = t[t.subject.str.contains(q, case=False, regex=False)]
st.dataframe(t[["subject", "level", "step", "rule", "value", "threshold", "reason"]], hide_index=True,
             width="stretch", height=380)
st.caption(f"{len(t)} rows. Step 1 removes most kinds because they are outside EMI's field "
           "(medicine, law, languages, ...).")

if res["changed"]:
    st.subheader("Compared with the official result")
    a = off["kinds"].set_index("kind")[["ranked", "eligible"]]
    b = res["kinds"].set_index("kind")[["ranked", "eligible"]]
    d = a.join(b, lsuffix="_official", rsuffix="_now")
    d = d[(d.eligible_official != d.eligible_now) | (d.ranked_official != d.ranked_now)]
    if d.empty:
        st.info("This what-if removes the same programmes as the official rules.")
    else:
        d["change"] = ["now eligible" if n else "no longer eligible" for n in d.eligible_now]
        reasons = res["first_reason"].set_index("kind").reason
        d["reason now"] = [reasons.get(k, "") for k in d.index]
        st.dataframe(d[["change", "reason now"]], width="stretch")
