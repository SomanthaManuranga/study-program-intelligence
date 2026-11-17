import copy

import numpy as np
import pandas as pd
import streamlit as st

import state

rules, prep = st.session_state.rules, state.prepared()
st.title("Handbook vs timetable")
st.write("The official fit check counts every module in the EMI handbooks. The stricter check counts only modules "
         "that are actually scheduled in the timetables of WS 2026/27 and SS 2026. Decided before the run: the "
         "handbook stays official, because some electives run only every other year.")

hb_rules, tt_rules = copy.deepcopy(rules), copy.deepcopy(rules)
hb_rules["step3_fit"]["module_basis"], tt_rules["step3_fit"]["module_basis"] = "handbook", "timetable"
hb, tt = state.results(hb_rules), state.results(tt_rules)

c = st.columns(2)
for col, lvl, name in [(c[0], "BA", "Bachelor"), (c[1], "MA", "Master")]:
    col.metric(f"{name} winner: handbook → timetable", f"{hb['winners'].get(lvl)} → {tt['winners'].get(lvl)}")

# ---- per kind comparison
H, T = hb["kinds"].set_index("kind"), tt["kinds"].set_index("kind")
HR, TR = hb["ranking"].set_index("kind"), tt["ranking"].set_index("kind")
reason_tt = tt["first_reason"].set_index("kind").reason
tau_h, tau_t = hb["calibration"]["tau_used"], tt["calibration"]["tau_used"]
rows = []
for kind in H.index[H.ranked | T.ranked]:
    tp = prep.topics[kind]
    if not tp:
        continue
    lost = [f"{tp[i][0]} → {prep.best_module[kind][i][0]}" for i in range(len(tp))
            if prep.best_all[kind][i] >= tau_h and prep.tt["best_all"][kind][i] < tau_t]
    st_h = f"rank {int(HR.loc[kind, 'rank'])}" + ("" if H.loc[kind, "eligible"] else ", not eligible")
    st_t = f"rank {int(TR.loc[kind, 'rank'])}" + ("" if T.loc[kind, "eligible"] else ", not eligible") if kind in TR.index else "removed"
    why = "; ".join(lost[:4]) + (f" (+{len(lost) - 4} more)" if len(lost) > 4 else "")
    if H.loc[kind, "eligible"] and not T.loc[kind, "eligible"]:
        why = reason_tt.get(kind, "") + (" · topics lost: " + why if why else "")
    rows.append({"kind": kind, "level": H.loc[kind, "level"], "handbook": st_h, "timetable": st_t,
                 "coverage handbook": H.loc[kind, "coverage"], "coverage timetable": T.loc[kind, "coverage"],
                 "eligible change": ("survives both" if H.loc[kind, "eligible"] and T.loc[kind, "eligible"] else
                                     "fails with timetable" if H.loc[kind, "eligible"] else
                                     "only with timetable" if T.loc[kind, "eligible"] else "fails both"),
                 "why (topics covered only by modules not scheduled)": why})
d = pd.DataFrame(rows).sort_values(["level", "coverage handbook"], ascending=[True, False])
d["drop"] = d["coverage handbook"] - d["coverage timetable"]

f1, f2 = st.columns([1, 2])
lvl = f1.radio("Level", ["BA", "MA"], horizontal=True)
show = f2.multiselect("Show", ["survives both", "fails with timetable", "only with timetable", "fails both"],
                      default=["survives both", "fails with timetable", "only with timetable"])
v = d[(d.level == lvl) & d["eligible change"].isin(show)]
st.dataframe(v.drop(columns=["level"]), hide_index=True, width="stretch", height=420,
             column_config={"coverage handbook": st.column_config.NumberColumn(format="percent"),
                            "coverage timetable": st.column_config.NumberColumn(format="percent"),
                            "drop": st.column_config.NumberColumn("coverage lost", format="percent")})
st.caption(f"tau: handbook {tau_h:.2f}, timetable {tau_t:.2f} (each calibrated on its own module set).")

# ---- link quality
st.subheader("How handbook modules were linked to the timetable")
L = prep.tt["link"]
from study_program_intelligence.crosscheck.common import EMI_PROGRAMME_NAMES
q = L.assign(programme=L.programme_id.map(EMI_PROGRAMME_NAMES)).groupby("programme").agg(
    modules=("title", "size"), scheduled=("scheduled", "mean"),
    unsure=("how", lambda s: int((s == "unsure").sum())),
    not_scheduled_lectures=("scheduled", lambda s: int((~s & ~L.loc[s.index, "structural"]).sum())))
st.dataframe(q.sort_values("scheduled"), width="stretch",
             column_config={"scheduled": st.column_config.ProgressColumn("share scheduled", format="percent", min_value=0, max_value=1),
                            "not_scheduled_lectures": "not scheduled (excl. thesis, internship, electives)"})
st.caption("Linked by exact title, then by module code, then by a close title. Thesis, internship and "
           "elective-placeholder modules are never in a timetable. Applied Research (MA) is barely in these two "
           "timetables, so the stricter check is unfair to it.")
with st.expander("Matches to check by hand (unsure)"):
    st.dataframe(L[L.how == "unsure"][["programme_id", "title", "tt_module", "match_score"]], hide_index=True, width="stretch")
with st.expander("All handbook modules not found in the timetable"):
    st.dataframe(L[~L.scheduled][["programme_id", "title", "structural"]], hide_index=True, width="stretch")
