import streamlit as st

res = st.session_state.res
st.title("Which new study programme for EMI?")
st.caption("OTH Amberg-Weiden · AI Project 3 · independent cross-check")

c1, c2 = st.columns(2)
for col, lvl, name in [(c1, "BA", "Bachelor"), (c2, "MA", "Master")]:
    g = res["ranking"][(res["ranking"].level == lvl) & res["ranking"].eligible]
    with col:
        if g.empty:
            st.metric(f"{name}: winner", "none eligible")
            continue
        top = g.iloc[0]
        st.metric(f"{name}: winner", top.subject)
        st.markdown(f"**Score {top.score:.2f}** of 5 · wins in **{top.p_first_eligible:.0%}** of the weight draws")
        st.caption(f"About {top.new_to_oth:.0f} first-years new to OTH a year · EMI covers {top.coverage:.0%} "
                   f"of its topics · {int(top.within_150km)} offers within 150 km")

st.subheader("Workflow")
steps = [("0", "Rules", "written before the code runs"), ("1", "Universe", "subject x level, EMI field"),
         ("2", "Relabel", "not a copy of one EMI programme"), ("3", "Fit", "share of topics EMI already teaches"),
         ("4", "Demand", "first-years new to OTH"), ("5", "Region", "competition near Amberg"),
         ("6", "Jobs", "job ads near Amberg"), ("7", "Ranking", "weights + Monte Carlo")]
cols = st.columns(len(steps))
for col, (n, t, d) in zip(cols, steps):
    col.markdown(f"**{n} · {t}**  \n<small>{d}</small>", unsafe_allow_html=True)

st.subheader("How many remain after each step")
f = res["funnel"].pivot(index="stage", columns="level", values="remaining").reindex(res["funnel"].stage.unique()[:5])
st.dataframe(f, width="stretch")
cal = res["calibration"]
st.caption(f"Match threshold tau = {cal['tau_used']:.2f} (OTH's own subjects {cal['mean_pos']:.0%} covered vs "
           f"unrelated subjects {cal['mean_neg']:.0%}).")
