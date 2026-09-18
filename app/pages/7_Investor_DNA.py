import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st

from src.data.investor_dna import calculate_investor_profile

st.set_page_config(page_title="Investor DNA", page_icon="⚖️", layout="wide")

st.title("Investor DNA")
st.caption("A behavioral profile built from your decisions in Historical Case Mode.")

profile = calculate_investor_profile()

if not profile["enough_data"]:
    st.info(
        f"You've made {profile['decisions_made']} decision(s) so far. "
        f"Play at least {profile['decisions_needed']} cases in Historical Case Mode to build your profile."
    )
    st.stop()

st.write(f"Based on **{profile['decisions_made']}** decisions, with an overall accuracy of **{profile['accuracy']}%**.")

st.divider()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Growth Bias", profile["growth_bias"])
col2.metric("Value Bias", profile["value_bias"])
col3.metric("Risk Appetite", profile["risk_appetite"])
col4.metric("Valuation Discipline", profile["valuation_discipline"])
col5.metric("Diversification Discipline", profile["diversification_discipline"])

st.caption(
    "Scores are illustrative (0-100), based only on your BUY decisions. Valuation Discipline uses "
    "each company's current P/E as a proxy, since historical P/E at the time of each case isn't tracked."
)

st.divider()
st.markdown("### Patterns we've noticed")

for observation in profile["observations"]:
    st.write(f"- {observation}")
