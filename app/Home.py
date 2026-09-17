import streamlit as st

st.set_page_config(page_title="Investment Courtroom", page_icon="⚖️", layout="wide")

st.title("⚖️ Investment Courtroom")
st.subheader("Every investment has a case. The Court decides whether it deserves your money.")

st.markdown("""
This is an analytical tool that puts a stock "on trial." A Bull side builds the strongest
case for investing, a Bear side builds the strongest case against it, and a Judge combines
real financial data into an explainable verdict.

**Use the sidebar to navigate:**
- **Stock Court** — pick a company and see its key evidence
- **Bull vs Bear** — see the arguments on both sides, and where they contradict each other
- **Judge's Verdict** — the final combined score and decision
""")

st.divider()

st.markdown("### Companies currently covered")

companies = [
    "HDFCBANK", "ICICIBANK", "SBIN", "TCS", "INFY", "WIPRO",
    "RELIANCE", "ONGC", "HINDUNILVR", "ITC", "TATAMOTORS",
    "MARUTI", "SUNPHARMA", "DRREDDY", "ULTRACEMCO",
]

cols = st.columns(5)
for i, name in enumerate(companies):
    cols[i % 5].markdown(f"- {name}")

st.divider()

st.info(
    "This tool is for educational and analytical purposes only. It is not personalized "
    "financial advice. All figures are computed from historical data and should not be "
    "the sole basis for an investment decision."
)
