import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st

from app.cache_utils import cached_bull_case, cached_bear_case, cached_cross_exam
st.set_page_config(page_title="Bull vs Bear", page_icon="⚖️", layout="wide")

st.title("Bull vs Bear")

if "selected_company" not in st.session_state:
    st.warning("Please select a company on the Stock Court page first.")
    st.stop()

company = st.session_state["selected_company"]
st.caption(f"Arguments for and against investing in {company}")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🟢 Bull Case")
    bull_points = cached_bull_case(company)
    if not bull_points:
        st.write("No strong bullish signals found.")
    else:
        for point in bull_points:
            st.success(point)

with col2:
    st.markdown("### 🔴 Bear Case")
    bear_points = cached_bear_case(company)
    if not bear_points:
        st.write("No strong bearish signals found.")
    else:
        for point in bear_points:
            st.error(point)

st.divider()
st.markdown("### ⚔️ Cross-Examination")
st.caption("Where the Bull's evidence is directly challenged by the Bear's evidence.")

challenges = cached_cross_exam(company)
if not challenges:
    st.info("No direct contradictions found between the Bull and Bear evidence.")
else:
    for challenge in challenges:
        st.warning(f"⚠️ {challenge}")
