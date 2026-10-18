import altair as alt
import pandas as pd
import streamlit as st

from common import LABEL, OPTION, csv, evidence, figure, metric, show

from study_program_intelligence.analysis import ranking

st.title("Ranking explorer")
st.markdown(f"MCDA with Monte Carlo: {show('mc_draws')} draws, Dirichlet weights around the chosen weights "
            f"(concentration {show('dirichlet_conc')}), scores drawn from their ranges, one shared capture-model draw. "
            "Move the weights to see how robust the order is; the run uses `analysis.ranking.simulate` unchanged.")

cfg, scores, _ = ranking.load()
BASE = cfg["weights"]
for k in BASE:
    st.session_state.setdefault(f"s_{k}", float(BASE[k]))


def reset() -> None:
    for k in BASE:
        st.session_state[f"s_{k}"] = float(BASE[k])


left, right = st.columns([1, 2])
with left:
    scenario = st.radio("Scenario", ["Base", "Robotics with 50 % cannibalisation", "Demand trend from German entrants only"],
                        horizontal=False)
    for k in BASE:
        st.slider(k.replace("_", " "), 0.0, 0.6, step=0.05, key=f"s_{k}")
    st.button("Reset to the chosen weights", on_click=reset)
    st.session_state.w = {k: st.session_state[f"s_{k}"] for k in BASE}


@st.cache_data(show_spinner="Running 10,000 draws ...")
def run(weights: tuple, rob50: bool, german: bool) -> pd.DataFrame:
    c, sc, cap = ranking.load(robotics_cannib_50=rob50, german_trend=german)
    w = dict(weights)
    if all(abs(w[k] - c["weights"][k]) < 1e-9 for k in c["weights"]):
        w = c["weights"]                                   # exactly the report's run
    else:
        tot = sum(w.values())
        w = {k: v / tot for k, v in w.items()}
    return ranking.summarise(ranking.simulate(c, sc, cap, w))


weights = st.session_state.w
if sum(weights.values()) == 0:
    st.warning("All weights are zero.")
    st.stop()
res = run(tuple(weights.items()), scenario.startswith("Robotics"), scenario.startswith("Demand")).set_index("option").loc[list(OPTION)]

with right:
    is_base = all(abs(weights[k] - BASE[k]) < 1e-9 for k in BASE)
    st.markdown("**Chosen weights (as in the report)**" if is_base else "**Changed weights** (normalised to sum 1)")
    long = pd.DataFrame([{"Option": LABEL[o], "Rank": r.replace("P(", "").replace(")", ""), "Share of draws": 100 * res.at[o, r]}
                         for o in res.index for r in ("P(rank 1)", "P(rank 2)", "P(rank 3)")])
    chart = alt.Chart(long).mark_bar(cornerRadiusEnd=4).encode(
        y=alt.Y("Option:N", sort=list(LABEL.values()), title=None, axis=alt.Axis(labelOverlap=False, labelLimit=220)),
        x=alt.X("Share of draws:Q", stack=True, scale=alt.Scale(domain=[0, 100]), title="% of draws"),
        color=alt.Color("Rank:N", scale=alt.Scale(domain=["rank 1", "rank 2", "rank 3"], range=["#1F4E79", "#9DB7D5", "#E3E3E3"]),
                        legend=alt.Legend(orient="top", title=None)),
        order=alt.Order("Rank:N"),
        tooltip=["Option", "Rank", alt.Tooltip("Share of draws:Q", format=".1f")],
    ).properties(height=260)
    st.altair_chart(chart, width="stretch")
    out = pd.DataFrame({"Option": [LABEL[o] for o in res.index],
                        "First place": [f"{100 * res.at[o, 'P(rank 1)']:.1f} %" for o in res.index],
                        "Second": [f"{100 * res.at[o, 'P(rank 2)']:.1f} %" for o in res.index],
                        "Third": [f"{100 * res.at[o, 'P(rank 3)']:.1f} %" for o in res.index],
                        "Median score": res["median score"].round(2).values,
                        "80 % range": res["80 % range"].values})
    st.dataframe(out, hide_index=True, width="stretch")
    if is_base and scenario == "Base":
        st.caption(f"Report: {show('p_rank1_cyber_bsc_base')} / {show('p_rank1_cyber_msc_base')} / "
                   f"{show('p_rank1_robotics_bsc_base')} first place.")
    if is_base and scenario.startswith("Demand"):
        st.caption(f"Report: {show('p_rank1_cyber_bsc_german')} / {show('p_rank1_cyber_msc_german')} / "
                   f"{show('p_rank1_robotics_bsc_german')} first place. Trend scores from German first-years / graduates "
                   "only, for all three options (cyber B.Sc. 4 to 3, master 4, robotics 2 to 1).")

st.subheader("Leave one criterion out (chosen weights)")
loo = csv("ranking_loo.csv")
loo = loo[loo["scenario"] == {"Base": "base", "Robotics with 50 % cannibalisation": "robotics 50 % cannibalisation"}.get(
    scenario, "base, trend scores from German first-years only")]
st.dataframe(pd.DataFrame({
    "Criterion left out": loo["criterion left out"].str.replace("_", " "),
    **{LABEL[o]: (100 * loo[f"P(rank 1) {o}"]).map(lambda v: f"{v:.1f} %") for o in OPTION},
}), hide_index=True, width="stretch")
c = st.columns(3)
metric("Lowest first place, base case (no demand)", "loo_min_cyber_bsc", c[0])
metric("Robustness bar", "robustness_bar", c[1])
metric("With independent capture draws", "p1_independent", c[2])
figure("f07_leave_one_out")

st.subheader("Evidence strength")
st.table(pd.DataFrame([{   # from configs/scores.yaml, the reviewed score sheet; static table (also prints in screenshots)
    "Option": LABEL[o],
    "Demand model": scores[o]["student_demand"]["capture"]["strength"],
    "Demand trend": scores[o]["student_demand"]["trend"]["strength"],
    **{c.replace("_", " ").capitalize(): scores[o][c]["strength"]
       for c in ("labour_relevance", "institutional_fit", "feasibility", "differentiation", "regional_contribution")},
} for o in OPTION]).set_index("Option"))
st.caption("Same capture model for all options; missing anchors widen ranges; weak evidence widens a score's range "
           "symmetrically, never raises its centre.")
evidence("docs/evidence_ranking.md", "configs/scores.yaml", "configs/analysis.yaml")
