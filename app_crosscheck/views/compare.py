import pandas as pd
import streamlit as st

import state

res = st.session_state.res
soma = state.somantha()
st.title("Comparison with Somantha's analysis")
st.write("Two independent analyses on the same data and the same agreed rules. Somantha's funnel (soma/funnel) "
         "tests the finalists module by module against real handbooks; the cross-check ranks every subject with "
         "automatic topic matching. Agreement between them is the strongest evidence.")
if soma is None:
    st.error("Somantha's result files are not in data/interim/funnel_results/.")
    st.stop()

K = res["kinds"].set_index("kind")
R = res["ranking"].set_index("kind")
first = res["first_reason"].set_index("kind").reason
rows = []
for _, g in soma["gate"].iterrows():
    subj = state.SOMA_SUBJECT.get(g.type, "?")
    kind = f"{subj} | {'BA' if g.level == 'bachelor' else 'MA'}"
    mine = ("not in the data" if kind not in K.index else
            f"rank {int(R.loc[kind, 'rank'])}, P(first) {R.loc[kind, 'p_first_eligible']:.0%}" if kind in R.index and K.loc[kind, "eligible"]
            else first.get(kind, "ranked, not eligible"))
    rows.append({"Somantha: candidate": f"{g.type} {g.level}", "titles": g["central titles"].split(";")[0] + " …",
                 "handbook overlap": f"{g['overlap (mean)']:.0%}", "verdict (Somantha)": g.verdict,
                 "cross-check kind": kind, "cross-check (current rules)": mine})
st.subheader("Somantha's six gate candidates, seen by the cross-check")
st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

cy = res["kinds"].set_index("kind").loc["IT-Sicherheit | BA"]
cyr = res["ranking"].set_index("kind")
cyber = (f"rank {int(cyr.loc['IT-Sicherheit | BA', 'rank'])} and {int(cy.within_150km)} competing offers within 150 km"
         if "IT-Sicherheit | BA" in cyr.index else "no rank under the current rules")
st.subheader("Where the two agree and differ")
st.markdown(f"""
- **Agree:** computer science and cyber security are the two strongest bachelor ideas in both analyses.
- **Bachelor winner:** Somantha recommends **Informatik / Computer Science (312)**, the only *existing-resources passer*.
  The cross-check currently has **{res['winners'].get('BA')}** first. Informatik carries a relabel risk: OTH already runs
  Medieninformatik, Industrie-4.0-Informatik, KI and Wirtschaftsinformatik.
- **Cyber security (223):** passes Somantha's band (63% / 58% overlap) but needs about 1.5 professor-equivalents of new
  teaching; in the cross-check it has {cyber}.
- **Master:** Somantha's master candidates fail or depend on the reference handbook; the cross-check puts
  **{res['winners'].get('MA')}** first. Somantha did not test a cyber security master.
""")
rk = soma["rank"]
st.subheader("Somantha's final ranking (stored)")
st.dataframe(rk[["set", "type", "level", "central score", "P(rank 1)"]], hide_index=True, width="stretch")
