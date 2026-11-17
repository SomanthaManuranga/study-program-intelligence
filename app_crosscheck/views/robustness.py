import copy

import plotly.express as px
import streamlit as st

import state

rules, res = st.session_state.rules, st.session_state.res
R = res["ranking"]
st.title("Robustness")
st.write("Does the answer survive if our choices were different?")

st.subheader("1 · How often each programme wins when the weights vary")
cols = st.columns(2)
for col, lvl, name in [(cols[0], "BA", "Bachelor"), (cols[1], "MA", "Master")]:
    g = R[(R.level == lvl) & R.eligible & (R.p_first_eligible > 0.005)].sort_values("p_first_eligible")
    fig = px.bar(g, x="p_first_eligible", y="subject", orientation="h", range_x=[0, 1], title=name, text_auto=".0%")
    fig.update_layout(height=120 + 30 * len(g), margin=dict(l=10, r=10, t=40, b=10), xaxis_tickformat=".0%",
                      xaxis_title="P(first)", yaxis_title=None)
    col.plotly_chart(fig, width="stretch")
r7 = rules["step7_ranking"]
st.caption(f"{r7['mc_draws']:,} random weight sets (Dirichlet, concentration {r7['dirichlet_concentration']}) around the "
           "chosen weights; only eligible programmes compete.")

st.subheader("2 · Leave one criterion out")
loo = res["loo"].pivot(index="left_out", columns="level", values="winner")
st.dataframe(loo, width="stretch")

st.subheader("3 · Change one rule at a time")
scen = [
    ("Relabel risk: drop instead of flag", lambda r: r["step2_relabel"].update(relabel_risk_action="drop")),
    ("Below-band programmes dropped", lambda r: r["step3_fit"].update(below_band_action="drop")),
    ("tau 0.10 (looser matching)", lambda r: r["step3_fit"].update(tau=0.10)),
    ("tau 0.20 (stricter matching)", lambda r: r["step3_fit"].update(tau=0.20)),
    ("Cannibalisation alpha 0.25", lambda r: r["step4_demand"].update(alpha=0.25)),
    ("Cannibalisation alpha 0.75", lambda r: r["step4_demand"].update(alpha=0.75)),
    ("Minimum cohort 30", lambda r: r["step4_demand"].update(min_cohort=30)),
    ("Competition within 100 km", lambda r: r["step5_region"].update(competition_radius_km=100)),
    ("Job ads: all of Germany", lambda r: r["step6_jobs"].update(job_region="germany")),
    ("Equal weights", lambda r: r["step7_ranking"].update(weights={c: 1.0 for c in state.CRITERIA})),
    ("Demand weight doubled", lambda r: r["step7_ranking"]["weights"].update(demand=r["step7_ranking"]["weights"]["demand"] * 2)),
]
base = res["winners"]
rows = []
for label, f in scen:
    rr = copy.deepcopy(rules)
    f(rr)
    w = state.results(rr)["winners"]
    rows.append({"change": label, "Bachelor winner": w.get("BA"), "Master winner": w.get("MA"),
                 "same as now": "yes" if w == base else "no"})
import pandas as pd
t = pd.DataFrame(rows)
same = (t["same as now"] == "yes").sum()
c = st.columns(3)
c[0].metric("Bachelor winner kept", f"{(t['Bachelor winner'] == base.get('BA')).sum()} / {len(t)}")
c[1].metric("Master winner kept", f"{(t['Master winner'] == base.get('MA')).sum()} / {len(t)}")
c[2].metric("Both kept", f"{same} / {len(t)}")
st.dataframe(t, hide_index=True, width="stretch")
st.caption(f"Each row changes one rule of the current rule set (now: Bachelor {base.get('BA')}, Master {base.get('MA')}).")
