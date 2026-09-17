import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st

from src.stress_testing.stress_test import run_stress_test

st.set_page_config(page_title="Stress Test", page_icon="⚖️", layout="wide")

st.title("Stress Test")
st.caption("Simulate a downturn and see how the verdict changes.")

if "selected_company" not in st.session_state:
    st.warning("Please select a company on the Stock Court page first.")
    st.stop()

company = st.session_state["selected_company"]
st.markdown(f"### Testing: {company}")

st.info(
    "This adjusts fundamentals directly (margin, ROE/ROCE, P/E) and recomputes the Quality and "
    "Valuation scores. Growth and Risk stay based on real historical price data, since a hypothetical "
    "future scenario shouldn't rewrite what already happened to the stock."
)

col1, col2, col3 = st.columns(3)
revenue_decline = col1.slider("Revenue decline (%)", 0, 50, 0)
margin_decline = col2.slider("Margin decline (percentage points)", 0, 15, 0)
pe_shock = col3.slider("P/E contraction (%)", 0, 50, 0)

result = run_stress_test(
    company,
    revenue_decline_pct=revenue_decline,
    margin_decline_pct=margin_decline,
    pe_shock_pct=pe_shock,
)

if result is None:
    st.error("Could not run a stress test for this company.")
    st.stop()

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("#### Baseline (current)")
    st.metric("Overall Score", result["baseline_overall"])
    st.metric("Quality Score", result["baseline_scores"]["quality"])
    st.metric("Valuation Score", result["baseline_scores"]["valuation"])
    st.write(f"**Verdict:** {result['baseline_verdict']}")

with col_b:
    st.markdown("#### Stressed (under this scenario)")
    delta = round(result["stressed_overall"] - result["baseline_overall"], 1) if result["stressed_overall"] is not None and result["baseline_overall"] is not None else None
    st.metric("Overall Score", result["stressed_overall"], delta=delta)
    st.metric("Quality Score", result["stressed_scores"]["quality"])
    st.metric("Valuation Score", result["stressed_scores"]["valuation"])
    st.write(f"**Verdict:** {result['stressed_verdict']}")

st.divider()

if result["stressed_verdict"] != result["baseline_verdict"]:
    st.warning(
        f"⚠️ Under this scenario, the verdict would change from "
        f"**{result['baseline_verdict']}** to **{result['stressed_verdict']}**."
    )
else:
    st.success(f"The verdict stays **{result['stressed_verdict']}** even under this scenario.")
