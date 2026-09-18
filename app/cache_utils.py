import streamlit as st

from src.analytics.price_metrics import get_price_history
from src.courtroom.bull_engine import get_company_data, build_bull_case
from src.courtroom.bear_engine import build_bear_case
from src.courtroom.cross_exam import cross_examine
from src.scoring.judge import judge_company
from src.stress_testing.stress_test import run_stress_test
from src.portfolio.portfolio_analytics import calculate_portfolio_metrics
from src.courtroom.ai_narrator import generate_courtroom_dialogue


# caching these means repeat visits to the same company don't hit the database
# or recompute everything again - big speed win for a shared, publicly hosted app
CACHE_TIME = 3600  # 1 hour


@st.cache_data(ttl=CACHE_TIME)
def cached_price_history(company_name):
    return get_price_history(company_name)


@st.cache_data(ttl=CACHE_TIME)
def cached_company_data(company_name):
    return get_company_data(company_name)


@st.cache_data(ttl=CACHE_TIME)
def cached_bull_case(company_name):
    return build_bull_case(company_name)


@st.cache_data(ttl=CACHE_TIME)
def cached_bear_case(company_name):
    return build_bear_case(company_name)


@st.cache_data(ttl=CACHE_TIME)
def cached_cross_exam(company_name):
    return cross_examine(company_name)


@st.cache_data(ttl=CACHE_TIME)
def cached_judge(company_name):
    return judge_company(company_name)


@st.cache_data(ttl=CACHE_TIME)
def cached_stress_test(company_name, revenue_decline_pct, margin_decline_pct, pe_shock_pct):
    return run_stress_test(company_name, revenue_decline_pct, margin_decline_pct, pe_shock_pct)


@st.cache_data(ttl=CACHE_TIME)
def cached_portfolio_metrics(holdings_items):
    # dicts can't be cache keys directly, so pages pass a sorted tuple of (company, weight) pairs
    holdings = dict(holdings_items)
    return calculate_portfolio_metrics(holdings)


@st.cache_data(ttl=CACHE_TIME)
def cached_ai_dialogue(company_name):
    return generate_courtroom_dialogue(company_name)
