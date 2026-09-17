import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import plotly.graph_objects as go

from src.portfolio.portfolio_analytics import calculate_portfolio_metrics

st.set_page_config(page_title="Portfolio Court", page_icon="⚖️", layout="wide")

st.title("Portfolio Court")
st.caption("Build a portfolio and put the whole thing on trial.")

companies = [
    "HDFCBANK", "ICICIBANK", "SBIN", "TCS", "INFY", "WIPRO",
    "RELIANCE", "ONGC", "HINDUNILVR", "ITC", "TATAMOTORS",
    "MARUTI", "SUNPHARMA", "DRREDDY", "ULTRACEMCO",
]

selected = st.multiselect("Pick your holdings", companies, default=["RELIANCE", "TCS", "HDFCBANK", "MARUTI"])

if not selected:
    st.info("Pick at least one company to build a portfolio.")
    st.stop()

st.markdown("#### Set each holding's weight (%)")
weights = {}
cols = st.columns(len(selected))
default_weight = round(100 / len(selected), 1)

for i, company in enumerate(selected):
    weights[company] = cols[i].number_input(company, min_value=0.0, max_value=100.0, value=default_weight, step=1.0)

total_weight = sum(weights.values())
st.write(f"Total: {round(total_weight, 1)}%")

if round(total_weight, 1) != 100.0:
    st.warning("Weights must add up to 100% before analyzing.")
    st.stop()

if st.button("Analyze Portfolio"):
    holdings = {company: weight / 100 for company, weight in weights.items()}
    result = calculate_portfolio_metrics(holdings)

    if "error" in result:
        st.error(result["error"])
        st.stop()

    st.divider()
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Portfolio CAGR", f"{result['portfolio_cagr']}%")
    col2.metric("Volatility", f"{result['portfolio_volatility']}%")
    col3.metric("Max Drawdown", f"{result['portfolio_max_drawdown']}%")
    col4.metric("Sharpe Ratio", result['portfolio_sharpe'])
    col5.metric("Beta", result['portfolio_beta'])

    st.divider()
    st.markdown("#### Sector Concentration")

    sector_data = result["sector_breakdown"]
    fig = go.Figure(data=[go.Pie(labels=list(sector_data.keys()), values=list(sector_data.values()), hole=0.4)])
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.markdown("#### Portfolio Verdict")

    largest_sector = max(sector_data, key=sector_data.get)
    largest_weight = sector_data[largest_sector]

    if largest_weight > 50:
        st.warning(
            f"⚠️ This portfolio is heavily concentrated in **{largest_sector}** ({largest_weight}% of holdings). "
            "A downturn in that sector would disproportionately affect the whole portfolio."
        )
    elif largest_weight > 35:
        st.info(
            f"This portfolio leans toward **{largest_sector}** ({largest_weight}% of holdings) — "
            "not extreme, but worth being aware of."
        )
    else:
        st.success("This portfolio is reasonably well diversified across sectors.")

    if result["portfolio_sharpe"] is not None and result["portfolio_sharpe"] > 0.3:
        st.write(f"The portfolio's Sharpe ratio of {result['portfolio_sharpe']} suggests the risk taken has been reasonably rewarded.")
    elif result["portfolio_sharpe"] is not None:
        st.write(f"The portfolio's Sharpe ratio of {result['portfolio_sharpe']} suggests the return hasn't fully compensated for the risk taken.")
