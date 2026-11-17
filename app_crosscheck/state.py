"""Shared state for the cross-check app: cached engine, sidebar rule controls, official/what-if banner."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from study_program_intelligence.crosscheck import engine as E  # noqa: E402

CRITERIA = E.CRITERIA


@st.cache_resource(show_spinner="Preparing data (once, about 20 s)...")
def prepared():
    return E.prepare()


@st.cache_data(show_spinner=False, max_entries=64)
def _run(rules_json: str):
    return E.run(prepared(), json.loads(rules_json))


def agreed() -> dict:
    return E.agreed_rules()


# ---- sidebar: one widget per rule; keys "r:<section>.<name>" so a reset can overwrite them
def _key(sec, name):
    return f"r:{sec}.{name}"


def _reset():
    a = agreed()
    for sec, vals in a.items():
        for name, v in vals.items():
            if name == "weights":
                for c, w in v.items():
                    st.session_state[_key(sec, f"w_{c}")] = float(w)
            elif name == "tau":
                st.session_state[_key(sec, "tau_auto")] = v == "auto"
                st.session_state[_key(sec, "tau_value")] = 0.15
            else:
                st.session_state[_key(sec, name)] = v
    st.session_state["band_pair"] = (float(a["step3_fit"]["band_low"]), float(a["step3_fit"]["band_high"]))


def sidebar_rules() -> dict:
    a = agreed()
    if "rules_init" not in st.session_state:
        _reset()
        st.session_state.rules_init = True
    sb = st.sidebar
    sb.header("Rule set")
    sb.button("Reset to the agreed rules", on_click=_reset, width="stretch")
    r = copy.deepcopy(a)

    with sb.expander("Step 1 · Universe", expanded=False):
        r["step1_universe"]["emi_fit_share"] = st.slider(
            "EMI fit: share of offers that co-list an EMI subject", 0.0, 1.0, step=0.05,
            key=_key("step1_universe", "emi_fit_share"))
        r["step1_universe"]["min_topics"] = st.number_input(
            "Minimum focus topics in the catalogue", 1, 20, key=_key("step1_universe", "min_topics"))

    with sb.expander("Step 2 · Relabel check", expanded=False):
        r["step2_relabel"]["max_one_programme"] = st.slider(
            "Max share of topics from ONE existing EMI programme", 0.5, 1.0, step=0.05,
            key=_key("step2_relabel", "max_one_programme"))
        r["step2_relabel"]["relabel_risk_action"] = st.radio(
            "OTH already runs a programme with this subject/name", ["flag", "drop"], horizontal=True,
            key=_key("step2_relabel", "relabel_risk_action"))

    with sb.expander("Step 3 · Fit with EMI", expanded=False):
        r["step3_fit"]["module_basis"] = st.radio(
            "What EMI teaches", ["handbook", "timetable"], horizontal=True, key=_key("step3_fit", "module_basis"),
            format_func={"handbook": "Handbooks (official)", "timetable": "Timetable (stricter)"}.get)
        auto = st.checkbox("Match threshold tau: calibrate on controls", key=_key("step3_fit", "tau_auto"))
        tv = st.slider("tau (used when not calibrated)", 0.05, 0.60, step=0.01, key=_key("step3_fit", "tau_value"),
                       disabled=auto)
        r["step3_fit"]["tau"] = "auto" if auto else float(tv)
        r["step3_fit"]["near_ratio"] = st.slider("'Nearly covered' = at least this share of tau", 0.3, 1.0, step=0.05,
                                                 key=_key("step3_fit", "near_ratio"))
        r["step3_fit"]["band_low"], r["step3_fit"]["band_high"] = st.slider(
            "Ideal coverage band (share of topics EMI already teaches)", 0.0, 1.0, step=0.05, key="band_pair")
        r["step3_fit"]["below_band_action"] = st.radio("Below the band", ["flag", "drop"], horizontal=True,
                                                       key=_key("step3_fit", "below_band_action"))

    with sb.expander("Step 4 · Demand", expanded=False):
        r["step4_demand"]["alpha"] = st.slider("Cannibalisation alpha (share of overlap that are OTH students anyway)",
                                               0.0, 1.0, step=0.05, key=_key("step4_demand", "alpha"))
        r["step4_demand"]["min_cohort"] = st.number_input("Minimum new students a year", 0, 200, step=5,
                                                          key=_key("step4_demand", "min_cohort"))
        r["step4_demand"]["demand_mix_size"] = st.slider("Demand score: weight of size vs trend", 0.0, 1.0, step=0.05,
                                                         key=_key("step4_demand", "demand_mix_size"))

    with sb.expander("Step 5 · Region", expanded=False):
        r["step5_region"]["competition_radius_km"] = st.radio(
            "Competition = same kind offered within", [100, 150], format_func=lambda x: f"{x} km", horizontal=True,
            key=_key("step5_region", "competition_radius_km"))
        st.caption("Feeds the differentiation score. The south gap feeds the regional score.")

    with sb.expander("Step 6 · Jobs", expanded=False):
        r["step6_jobs"]["job_region"] = st.radio(
            "Job ads counted in", ["amberg_100km", "bayern", "germany"], key=_key("step6_jobs", "job_region"),
            format_func={"amberg_100km": "100 km around Amberg", "bayern": "Bavaria", "germany": "Germany"}.get)
        r["step6_jobs"]["min_jobs"] = st.number_input("Minimum job ads (0 = off)", 0, 5000, step=10,
                                                      key=_key("step6_jobs", "min_jobs"))

    with sb.expander("Step 7 · Weights and ranking", expanded=True):
        for c in CRITERIA:
            r["step7_ranking"]["weights"][c] = st.slider(c, 0.0, 1.0, step=0.05, key=_key("step7_ranking", f"w_{c}"))
        tot = sum(r["step7_ranking"]["weights"].values())
        if tot == 0:
            st.error("All weights are 0; using the agreed weights.")
            r["step7_ranking"]["weights"] = a["step7_ranking"]["weights"]
        else:
            st.caption(f"Sum {tot:.2f}; weights are rescaled to 1.")
        r["step7_ranking"]["shortlist_size"] = st.number_input(
            "Candidates checked in depth (shortlist)", 1, 40, key=_key("step7_ranking", "shortlist_size"))
        r["step7_ranking"]["mc_draws"] = st.select_slider("Monte Carlo draws", [1000, 2000, 5000, 10000, 20000],
                                                          key=_key("step7_ranking", "mc_draws"))
        r["step7_ranking"]["dirichlet_concentration"] = st.select_slider(
            "Weight uncertainty (lower = wider)", [5, 10, 20, 50, 100, 200], key=_key("step7_ranking", "dirichlet_concentration"))
        r["step7_ranking"]["seed"] = st.number_input("Random seed", 0, 10_000, key=_key("step7_ranking", "seed"))
    return r


def results(rules: dict) -> dict:
    return _run(json.dumps(rules, sort_keys=True))


def banner(res: dict):
    if not res["changed"]:
        st.success("**Official result**: the agreed rule set (configs/crosscheck_rules.yaml).", icon="✅")
    else:
        st.warning("**What-if**: not the agreed rules. Changed: " + "; ".join(res["changed"]), icon="🧪")


def official() -> dict:
    """Result with the agreed rules (for comparisons on the what-if pages)."""
    return results(agreed())


def fmt_pct(x):
    return "" if x is None or x != x else f"{x:.0%}"


SOMA = E.REPO / "data" / "interim" / "funnel_results"
SOMA_SUBJECT = {312: "Informatik", 223: "IT-Sicherheit", 256: "Stadt-, Regionalplanung", 300: "Bauingenieurwesen",
                22: "Architektur", 242: "Informatik"}


@st.cache_data(show_spinner=False)
def somantha():
    """Somantha's stored funnel results (soma/funnel), or None if the export is missing."""
    try:
        gate = __import__("pandas").read_csv(SOMA / "step7_feasibility" / "gate.csv")
        refs = __import__("pandas").read_csv(SOMA / "step7_feasibility" / "gate_references.csv")
        inputs = __import__("pandas").read_csv(SOMA / "step8_decision" / "rank_inputs.csv")
        rank = __import__("pandas").read_csv(SOMA / "step8_decision" / "rank.csv")
    except FileNotFoundError:
        return None
    return {"gate": gate, "refs": refs, "inputs": inputs, "rank": rank}


@st.cache_data(show_spinner=False)
def hand_check():
    import pandas as pd
    p = E.OUT / "hand_check_sheet.csv"
    return pd.read_csv(p) if p.exists() else None


@st.cache_data(show_spinner=False)
def lab_rooms() -> set:
    import pandas as pd
    p = E.REPO / "data" / "interim" / "timetable_rooms.csv"
    if not p.exists():
        return set()
    r = pd.read_csv(p)
    return set(r[r.lab_sessions > 0].room)
