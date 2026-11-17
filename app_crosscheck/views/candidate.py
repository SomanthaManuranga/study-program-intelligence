import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

import state
from study_program_intelligence.crosscheck.common import EMI_PROGRAMME_NAMES

res, prep = st.session_state.res, state.prepared()
K = res["kinds"].set_index("kind")
R = res["ranking"].set_index("kind")
st.title("Candidate details")

short = res["ranking"][res["ranking"].shortlist].kind.tolist()
opts = short + sorted(set(K.index) - set(short))
default = res["ranking"][res["ranking"].eligible].kind.iloc[0]
kind = st.selectbox("Programme kind (shortlist first)", opts, index=opts.index(default))
x = K.loc[kind]

if kind in R.index:
    r = R.loc[kind]
    st.markdown(f"**Rank {int(r['rank'])}** at {x.level} · score **{r.score:.2f}** · P(first) **{r.p_first_eligible:.0%}** · "
                + ("eligible ✅" if x.eligible else "not eligible ⚠️"))
else:
    st.error("Not ranked.")
reasons = res["drop_log"][res["drop_log"].kind == kind]
for t in reasons.reason:
    st.warning(t)
if x.relabel_risk:
    st.info(f"Relabel risk: OTH already runs {x.oth_programmes_same_subject}")

c = st.columns(5)
c[0].metric("EMI covers", state.fmt_pct(x.coverage), f"+{state.fmt_pct(x.near)} nearly", delta_color="off")
c[1].metric("Most from one programme", state.fmt_pct(x.max_one_programme))
c[2].metric("New to OTH / year", "" if pd.isna(x.new_to_oth) else f"{x.new_to_oth:.0f}")
c[3].metric("Offers ≤150 km", int(x.within_150km))
c[4].metric("Job ads ≤100 km", "" if pd.isna(x.jobs_100km) else int(x.jobs_100km))

st.subheader("Topic by topic: which EMI module covers it")
tau = res["calibration"]["tau_used"]
nr = st.session_state.rules["step3_fit"]["near_ratio"]
tp = prep.topics[kind]
if not tp:
    st.info("No focus topics in the catalogue for this kind.")
else:
    best = prep.best_all[kind]
    status = np.where(best >= tau, "covered", np.where(best >= nr * tau, "nearly", "not covered"))
    t = pd.DataFrame({"topic": [a for a, _ in tp], "offers listing it": [n for _, n in tp], "status": status,
                      "similarity": best.round(3), "best EMI module": [m for m, _ in prep.best_module[kind]],
                      "programme": [p for _, p in prep.best_module[kind]]})
    st.dataframe(t, hide_index=True, width="stretch", height=360,
                 column_config={"similarity": st.column_config.ProgressColumn(min_value=0, max_value=max(0.5, best.max()), format="%.2f")})
    st.caption(f"Covered = text similarity ≥ tau ({tau:.2f}); nearly = ≥ {nr:.0%} of tau. Automatic matching; "
               "the hand check below is the human verdict.")
    w = np.array([n for _, n in tp], float)
    per = [(w * (prep.best_prog[kind][:, j] >= tau)).sum() / w.sum() for j in range(len(prep.programmes))]
    pp = pd.DataFrame({"EMI programme": [EMI_PROGRAMME_NAMES.get(p, p) for p in prep.programmes], "share": per})
    pp = pp[pp.share > 0].sort_values("share")
    fig = px.bar(pp, x="share", y="EMI programme", orientation="h", range_x=[0, 1])
    fig.add_vline(x=st.session_state.rules["step2_relabel"]["max_one_programme"], line_dash="dash",
                  annotation_text="relabel limit")
    fig.update_layout(height=80 + 26 * len(pp), margin=dict(l=10, r=10, t=30, b=10), xaxis_tickformat=".0%",
                      title="Share of its topics covered by each EMI programme alone")
    st.plotly_chart(fig, width="stretch")

st.subheader("Who teaches it now (timetable)")
if tp:
    L = prep.tt["link"]
    covered = [i for i in range(len(tp)) if prep.tt["best_all"][kind][i] >= tau]
    idx = [prep.tt["best_idx"][kind][i] for i in covered]
    rows = L.iloc[sorted(set(idx))] if idx else L.iloc[0:0]
    lect = sorted({x.strip() for v in rows.lecturers for x in str(v).split(";") if x.strip()})
    rooms = sorted({x.strip() for v in rows.rooms for x in str(v).split(";") if x.strip()})
    labs = state.lab_rooms()
    cc = st.columns(3)
    cc[0].metric("Topics covered by scheduled modules", f"{len(covered)} / {len(tp)}")
    cc[1].metric("Lecturers already teaching them", len(lect))
    cc[2].metric("Lab rooms in use for them", len([r for r in rooms if r in labs]))
    st.dataframe(rows[["title", "tt_module", "semesters", "lecturers", "rooms"]].rename(
        columns={"title": "handbook module", "tt_module": "timetable module"}), hide_index=True, width="stretch")
    st.caption("Lecturers appear only as codes. A programme resting on one or two lecturers is a staffing risk.")

st.subheader("Stored checks (not recomputed)")
hc = state.hand_check()
done = hc is not None and hc[(hc.kind == kind) & hc.hand_verdict.notna()].shape[0] > 0
st.markdown(f"- **Hand check of the topic matches:** {'done' if done else 'not done yet'}")
soma = state.somantha()
lvl = {"BA": "bachelor", "MA": "master"}[x.level]
if soma is not None:
    ids = [k for k, s in state.SOMA_SUBJECT.items() if s == x.subject]
    g = soma["gate"][soma["gate"].type.isin(ids) & (soma["gate"].level == lvl)]
    if len(g):
        for _, row in g.iterrows():
            st.markdown(f"- **Handbook test (Somantha, module by module):** type {row.type}: overlap "
                        f"{row['overlap (mean)']:.0%} (range {row['overlap low']:.0%}-{row['overlap high']:.0%}), most from one "
                        f"programme {row['largest share from one programme']:.0%}, about {row['professor-equivalents (mean)']:.1f} "
                        f"professor-equivalents of new teaching → **{row.verdict}**")
    else:
        st.markdown("- **Handbook test:** not part of Somantha's gate list")
