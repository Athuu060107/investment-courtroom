import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st

from src.data.case_mode import get_random_case, evaluate_decision, save_decision

st.set_page_config(page_title="Historical Case Mode", page_icon="⚖️", layout="wide")

st.title("Historical Case Mode")
st.caption("A real, anonymized case from the past. Would you have invested?")

if "current_case" not in st.session_state:
    st.session_state["current_case"] = get_random_case()
    st.session_state["revealed"] = False

if st.button("🔀 New Case"):
    st.session_state["current_case"] = get_random_case()
    st.session_state["revealed"] = False
    st.rerun()

case = st.session_state["current_case"]

if case is None:
    st.error("No historical cases found. Run the case generator script first.")
    st.stop()

st.divider()
st.markdown(f"### Case dated: {case['case_date']}")
st.caption("Company name hidden. Judge only by the evidence below.")

col1, col2, col3 = st.columns(3)
col1.metric("Price at that time", f"₹{case['price_at_case']}")
col2.metric("5yr CAGR (as of then)", f"{case['cagr_as_of_case']}%")
col3.metric("Volatility (as of then)", f"{case['volatility_as_of_case']}%")

st.divider()

if not st.session_state["revealed"]:
    st.markdown("#### Your decision")
    decision = st.radio("Would you have invested?", ["BUY", "HOLD", "AVOID"], horizontal=True)

    if st.button("Submit Decision"):
        was_correct = evaluate_decision(decision, case["outcome_return_1y"])
        save_decision(case["case_id"], decision, was_correct)
        st.session_state["revealed"] = True
        st.session_state["last_decision"] = decision
        st.session_state["last_correct"] = was_correct
        st.rerun()
else:
    st.markdown("#### 🎭 Reveal")
    st.markdown(f"### This was: **{case['company_name']}**")

    col4, col5 = st.columns(2)
    col4.metric("Actual 1-year return", f"{case['outcome_return_1y']}%")
    col5.metric("Return to today", f"{case['outcome_return_to_date']}%")

    st.write(f"Your decision: **{st.session_state['last_decision']}**")

    if st.session_state["last_correct"]:
        st.success("✅ Correct call! The outcome matched your decision.")
    else:
        st.error("❌ Not quite — the actual outcome didn't match your decision.")

    st.caption(
        "Correctness rule (illustrative): BUY is correct if the 1-year return was above +10%, "
        "AVOID if below -10%, HOLD if roughly flat in between."
    )
