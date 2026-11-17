import plotly.express as px
import streamlit as st

import state

res, off = st.session_state.res, state.official()
R = res["ranking"]
st.title("Ranking")
st.write("Scores are 1-5 within each level (quintiles), combined with the weights. P(first) is how often a "
         "programme wins when the weights are varied at random around the chosen ones (Monte Carlo).")

lvl = st.radio("Level", ["BA", "MA"], horizontal=True, format_func=lambda x: {"BA": "Bachelor", "MA": "Master"}[x])
only_el = st.toggle("Only eligible programmes", value=True)
g = R[R.level == lvl]
if only_el:
    g = g[g.eligible]
n = int(st.session_state.rules["step7_ranking"]["shortlist_size"])
g = g.head(n)
st.caption(f"Showing the top {len(g)} (shortlist size from the sidebar).")

crit = [f"s_{c}" for c in state.CRITERIA]
w = st.session_state.rules["step7_ranking"]["weights"]
tot = sum(w.values()) or 1
long = g.melt(id_vars=["subject"], value_vars=crit, var_name="criterion", value_name="s")
long["points"] = [s * w[c[2:]] / tot for c, s in zip(long.criterion, long.s)]
long["criterion"] = long.criterion.str[2:]
fig = px.bar(long, y="subject", x="points", color="criterion", orientation="h",
             category_orders={"subject": g.subject.tolist(), "criterion": state.CRITERIA},
             color_discrete_sequence=px.colors.qualitative.Safe)
fig.update_layout(height=120 + 28 * len(g), margin=dict(l=10, r=10, t=10, b=10), xaxis_title="weighted score (max 5)",
                  yaxis_title=None, legend_title=None)
st.plotly_chart(fig, width="stretch")

tbl = g.assign(
    **{"P(first)": g.p_first_eligible.map(state.fmt_pct), "coverage": g.coverage.map(state.fmt_pct),
       "new to OTH / year": g.new_to_oth.round(0), "relabel risk": g.relabel_risk.map({True: "yes", False: ""}),
       "eligible": g.eligible.map({True: "yes", False: "no"})})
offr = off["ranking"].set_index("kind")["rank"]
tbl["official rank"] = [offr.get(k) for k in g.kind]
cols = ["rank", "subject", "score", "P(first)", "eligible", "band", "coverage", "new to OTH / year", "within_150km",
        "jobs_100km", "relabel risk"] + (["official rank"] if res["changed"] else []) + crit
st.dataframe(tbl[cols], hide_index=True, width="stretch",
             column_config={"score": st.column_config.NumberColumn(format="%.2f"),
                            "within_150km": "offers ≤150 km", "jobs_100km": "jobs ≤100 km"})
flag = g[g.relabel_risk]
if len(flag):
    st.caption("Relabel risk = OTH already runs a programme with this subject or name at this level: "
               + "; ".join(f"**{r.subject}**: {r.oth_programmes_same_subject}" for r in flag.itertuples()))
