import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st

from src.courtroom.ai_narrator import generate_courtroom_dialogue

st.set_page_config(page_title="AI Courtroom", page_icon="⚖️", layout="wide")

st.title("AI Courtroom")
st.caption("The same evidence you've already seen, narrated as courtroom dialogue by AI.")

if "selected_company" not in st.session_state:
    st.warning("Please select a company on the Stock Court page first.")
    st.stop()

company = st.session_state["selected_company"]
st.markdown(f"### Case: {company}")

st.info(
    "The AI only narrates evidence already computed by this app's rule-based engines. "
    "It does not invent any numbers, ratios, or facts of its own."
)

if st.button("🎭 Generate Courtroom Scene"):
    with st.spinner("The court is now in session..."):
        try:
            dialogue = generate_courtroom_dialogue(company)
            st.divider()
            for line in dialogue.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if line.startswith("BULL:"):
                    st.success(line)
                elif line.startswith("BEAR:"):
                    st.error(line)
                elif line.startswith("JUDGE:"):
                    st.warning(line)
                else:
                    st.write(line)
        except Exception as e:
            st.error(f"Could not generate courtroom dialogue: {e}")
