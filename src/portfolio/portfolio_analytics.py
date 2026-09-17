import numpy as np

from src.analytics.price_metrics import get_price_history, RISK_FREE_RATE
from src.courtroom.bull_engine import get_company_data

# kept here rather than pulled from the database each time, since it never changes
# and this avoids adding an extra query just for one text field
SECTOR_MAP = {
    "HDFCBANK": "Banking", "ICICIBANK": "Banking", "SBIN": "Banking",
    "TCS": "IT", "INFY": "IT", "WIPRO": "IT",
    "RELIANCE": "Energy", "ONGC": "Energy",
    "HINDUNILVR": "FMCG", "ITC": "FMCG",
    "TATAMOTORS": "Auto", "MARUTI": "Auto",
    "SUNPHARMA": "Pharma", "DRREDDY": "Pharma",
    "ULTRACEMCO": "Cement",
}


def get_portfolio_daily_returns(holdings):
    # holdings is a dict like {"TCS": 0.3, "HDFCBANK": 0.3, "MARUTI": 0.4}
    combined = None

    for company, weight in holdings.items():
        df = get_price_history(company)
        df = df.set_index("price_date")
        daily_return = df["close_price"].pct_change()
        weighted_return = daily_return * weight

        if combined is None:
            combined = weighted_return
        else:
            combined = combined.add(weighted_return, fill_value=0)

    return combined.dropna()


def get_sector_breakdown(holdings):
    breakdown = {}
    for company, weight in holdings.items():
        sector = SECTOR_MAP.get(company, "Unknown")
        breakdown[sector] = breakdown.get(sector, 0) + weight
    return {k: round(v * 100, 1) for k, v in breakdown.items()}


def calculate_portfolio_metrics(holdings):
    weights_sum = sum(holdings.values())
    if round(weights_sum, 2) != 1.0:
        return {"error": f"Weights must sum to 100%. Currently sum to {round(weights_sum * 100, 1)}%."}

    portfolio_returns = get_portfolio_daily_returns(holdings)

    # annualized volatility from the actual combined daily returns - this is where
    # diversification shows up, since correlated/uncorrelated moves cancel out naturally
    volatility = portfolio_returns.std() * np.sqrt(252)

    # rebuild a portfolio value index from daily returns to get a real max drawdown
    portfolio_value = (1 + portfolio_returns).cumprod()
    running_max = portfolio_value.cummax()
    drawdown = (portfolio_value - running_max) / running_max
    max_drawdown = drawdown.min()

    # weighted average CAGR and beta - simpler than reconstructing from scratch,
    # and a standard, explainable approximation for portfolio-level return/beta
    weighted_cagr = 0
    weighted_beta = 0

    for company, weight in holdings.items():
        data = get_company_data(company)
        if data is None:
            continue
        if data["cagr"] is not None:
            weighted_cagr += float(data["cagr"]) * weight
        if data["beta"] is not None:
            weighted_beta += float(data["beta"]) * weight

    sharpe = None
    if volatility != 0:
        sharpe = (weighted_cagr / 100 - RISK_FREE_RATE) / volatility

    return {
        "portfolio_cagr": round(weighted_cagr, 2),
        "portfolio_volatility": round(volatility * 100, 2),
        "portfolio_max_drawdown": round(max_drawdown * 100, 2),
        "portfolio_sharpe": round(sharpe, 2) if sharpe is not None else None,
        "portfolio_beta": round(weighted_beta, 2),
        "sector_breakdown": get_sector_breakdown(holdings),
    }


if __name__ == "__main__":
    sample_portfolio = {
        "RELIANCE": 0.30,
        "TCS": 0.30,
        "HDFCBANK": 0.20,
        "MARUTI": 0.20,
    }
    result = calculate_portfolio_metrics(sample_portfolio)
    print(result)
