import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))



import streamlit as st
import plotly.graph_objects as go

from src.analytics.price_metrics import get_price_history
from src.courtroom.bull_engine import get_company_data

st.set_page_config(page_title="Stock Court", page_icon="⚖️", layout="wide")

st.title("Stock Court")
st.caption("Select a company to see its evidence.")

companies = [
    "HDFCBANK", "ICICIBANK", "SBIN", "TCS", "INFY", "WIPRO",
    "RELIANCE", "ONGC", "HINDUNILVR", "ITC", "TATAMOTORS",
    "MARUTI", "SUNPHARMA", "DRREDDY", "ULTRACEMCO",
]

selected_company = st.selectbox("Choose a company", companies)

# save the selection so other pages can use it too
st.session_state["selected_company"] = selected_company

st.divider()

price_df = get_price_history(selected_company)

fig = go.Figure()
fig.add_trace(go.Scatter(x=price_df["price_date"], y=price_df["close_price"], mode="lines", name=selected_company))
fig.update_layout(
    title=f"{selected_company} — 5 Year Price History",
    xaxis_title="Date",
    yaxis_title="Close Price (₹)",
    height=450,
)
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("Evidence Room — Key Metrics")

data = get_company_data(selected_company)

if data is None:
    st.warning("No data found for this company.")
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("CAGR (5yr)", f"{data['cagr']}%" if data['cagr'] is not None else "N/A")
    col2.metric("Volatility", f"{data['volatility']}%" if data['volatility'] is not None else "N/A")
    col3.metric("Max Drawdown", f"{data['max_drawdown']}%" if data['max_drawdown'] is not None else "N/A")
    col4.metric("Sharpe Ratio", f"{data['sharpe_ratio']}" if data['sharpe_ratio'] is not None else "N/A")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Beta", f"{data['beta']}" if data['beta'] is not None else "N/A")
    col6.metric("ROE", f"{data['roe']}%" if data['roe'] is not None else "N/A")
    col7.metric("ROCE", f"{data['roce']}%" if data['roce'] is not None else "N/A")
    col8.metric("P/E Ratio", f"{data['pe_ratio']}" if data['pe_ratio'] is not None else "N/A")
