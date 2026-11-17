import streamlit as st

import state

prep = state.prepared()
st.title("Data sources")
st.write("Where every number in this app comes from. All sources are public except the timetables, "
         "which stay on our computers (lecturers appear only as codes).")
for _, s in prep.sources.iterrows():
    with st.container(border=True):
        c1, c2 = st.columns([3, 2])
        c1.markdown(f"**{s.source}**  \n{s.used_for}")
        c2.markdown(f"**Size:** {s.size}  \n**File:** `{s.file}`  \n**Limits:** {s.limits}")

k = prep.kinds
st.subheader("What the analysis is built on")
c = st.columns(4)
c[0].metric("Full-time BA/MA offers in Germany", f"{prep.universe_size:,}")
c[1].metric("Programme kinds (subject x level)", f"{len(k):,}")
c[2].metric("Kinds with enough topic data", f"{sum(len(v) >= 5 for v in prep.topics.values()):,}")
c[3].metric("EMI programmes in the handbooks", len(prep.programmes))
st.caption("A *programme kind* is an official catalogue subject at one level, e.g. 'IT-Sicherheit | BA'. "
           "Fine subjects that Destatis counts together share one student pool.")

with st.expander("Look up one kind: its raw inputs"):
    kind = st.selectbox("Kind", sorted(k.kind), index=sorted(k.kind).index("IT-Sicherheit | BA"))
    row = k[k.kind == kind].iloc[0]
    st.json({c: (None if v != v else v) for c, v in row.items() if not isinstance(v, (list, dict))}, expanded=False)
    st.write("Focus topics from the catalogue (topic, offers listing it):")
    st.dataframe([{"topic": t, "offers": n} for t, n in prep.topics[kind]], hide_index=True, width="stretch")
