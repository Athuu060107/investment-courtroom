import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st

from app.cache_utils import cached_judge

st.set_page_config(page_title="Judge's Verdict", page_icon="⚖️", layout="wide")

st.title("Judge's Verdict")

if "selected_company" not in st.session_state:
    st.warning("Please select a company on the Stock Court page first.")
    st.stop()

company = st.session_state["selected_company"]
result = cached_judge(company)

if result is None:
    st.error("Could not calculate a verdict for this company.")
    st.stop()

st.caption(f"Final verdict for {company}")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Quality Score", result["pillar_scores"]["quality"])
col2.metric("Growth Score", result["pillar_scores"]["growth"])
col3.metric("Valuation Score", result["pillar_scores"]["valuation"])
col4.metric("Risk Score", result["pillar_scores"]["risk"])

st.divider()

verdict = result["verdict"]
overall = result["overall_score"]

if verdict == "BUY":
    st.success(f"## 🟢 VERDICT: {verdict}\n### Overall Score: {overall} / 100")
elif verdict == "HOLD / WATCH":
    st.warning(f"## 🟡 VERDICT: {verdict}\n### Overall Score: {overall} / 100")
else:
    st.error(f"## 🔴 VERDICT: {verdict}\n### Overall Score: {overall} / 100")

st.divider()

col5, col6 = st.columns(2)
with col5:
    st.markdown("#### Strongest Bull Argument")
    st.write(result["strongest_bull_argument"])
with col6:
    st.markdown("#### Strongest Bear Argument")
    st.write(result["strongest_bear_argument"])

st.markdown(f"#### Biggest Risk Area")
st.write(f"**{result['biggest_risk'].capitalize()}** was this company's weakest scoring pillar.")

st.divider()

st.info(
    "This verdict is generated from a rule-based scoring model using historical financial data. "
    "It is for educational and analytical purposes only and is not personalized financial advice."
)
