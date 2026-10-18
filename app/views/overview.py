import streamlit as st

from common import evidence, figure, metric, show

st.title("Which new study programme should EMI offer?")
st.markdown(
    f"**Answer: a Cybersecurity B.Sc.** It ranks first of three shortlisted options in **{show('p_rank1_cyber_bsc_base')}** "
    f"of {show('mc_draws')} Monte Carlo draws and, in the base case, stays first whichever single criterion is left out; "
    f"with demand trends judged on German entrants only it is first in {show('p_rank1_cyber_bsc_german')}. "
    "Public data only; preliminary until the analysis freeze on 4 Dec 2026."
)

c = st.columns(4)
metric("First place (Monte Carlo)", "p_rank1_cyber_bsc_base", c[0])
metric("First-years / yr, central (from year 3)", "cyber_bsc_gross_central", c[1])
metric("Net new to OTH, central", "cyber_bsc_netnew_central", c[2])
metric("Own pool, school leavers / yr", "own_pool_exact", c[3])

c = st.columns(4)
metric("Bavarian cyber-proxy first-years 2030 (midpoint)", "cyber_proxy_by_2030_central", c[0])
metric("Security content EMI covers (at most)", "emi_cover_sec_ba", c[1])
metric("'Cyber Security' job ads, Germany", "ads_cyber_security_de", c[2])
metric("New professorships needed", "new_professorships", c[3], bare=True)

st.subheader("How the winner was found")
st.markdown(
    f"Criteria, weights and the final kill rules were committed on **{show('rules_fixed_date')}**, before the first screening; "
    "the scoring anchors for the other criteria and the weak-evidence rule followed on 17 Oct, before the first ranking run "
    "(the rule was tightened to symmetric ranges after that run). "
    "Candidates were then filtered stage by stage; only three were modelled and ranked."
)
figure("f00_funnel")
evidence("docs/evidence_funnel.md", "docs/kill_rules.md", "docs/decision_log.md")

st.subheader("What is weak")
st.markdown(
    f"- None of the comparable programmes we checked publishes its intake: the range rests on a capacity ({show('thi_cyber_capacity')} at TH Ingolstadt) "
    f"and one anecdote ({show('deg_cyber_anecdote')} at TH Deggendorf). Low case: {show('cyber_bsc_gross_low')} first-years "
    f"against an assumed minimum cohort of {show('min_cohort')}.\n"
    "- Cyber demand is measured through proxies (computer-science entrants, search interest, job-ad keywords).\n"
    "- Robotics has the thinnest evidence (no intake anchor, title-level fit check); its ranges were widened, not raised."
)
