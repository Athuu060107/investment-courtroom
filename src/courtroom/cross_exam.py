from src.courtroom.bull_engine import get_company_data
from src.courtroom.bear_engine import get_latest_debt_equity


def cross_examine(company_name):
    data = get_company_data(company_name)
    if data is None:
        return []

    challenges = []
    debt_equity = get_latest_debt_equity(company_name)

    # 1. strong growth but expensive valuation
    if data["cagr"] is not None and data["cagr"] > 10 and data["pe_ratio"] is not None and data["pe_ratio"] > 40:
        challenges.append(
            f"Valuation challenge: the Bull's growth argument ({data['cagr']}% CAGR) is weakened by "
            f"an expensive P/E of {data['pe_ratio']} — much of that growth may already be priced in."
        )

    # 2. strong ROE/ROCE but high leverage
    if debt_equity is not None and debt_equity > 1:
        if (data["roe"] is not None and data["roe"] > 15) or (data["roce"] is not None and data["roce"] > 15):
            challenges.append(
                f"Leverage challenge: the Bull's efficiency argument (strong ROE/ROCE) is weakened by "
                f"a debt-to-equity ratio of {round(debt_equity, 2)} — high returns can be partly a side effect of borrowing, not pure efficiency."
            )

    # 3. strong growth but poor risk-adjusted return
    if data["cagr"] is not None and data["cagr"] > 10 and data["sharpe_ratio"] is not None and data["sharpe_ratio"] < 0:
        challenges.append(
            f"Risk challenge: despite {data['cagr']}% CAGR, a negative Sharpe ratio of {data['sharpe_ratio']} "
            f"shows the return didn't actually compensate for the risk taken to get it."
        )

    # 4. beta says defensive, but volatility says otherwise
    if data["beta"] is not None and data["beta"] < 1 and data["volatility"] is not None and data["volatility"] > 30:
        challenges.append(
            f"Consistency challenge: a beta of {data['beta']} suggests this stock is defensive relative to the market, "
            f"but its own volatility of {data['volatility']}% is still high — its risk may be more company-specific than market-driven."
        )

    # 5. strong margins but declining stock price
    if data["net_margin"] is not None and data["net_margin"] > 15 and data["cagr"] is not None and data["cagr"] < -3:
        challenges.append(
            f"Market skepticism challenge: the company keeps a healthy {data['net_margin']}% net margin, "
            f"yet the stock has still declined {abs(data['cagr'])}% per year — the market may be pricing in a future risk the current fundamentals don't show."
        )
    return challenges


if __name__ == "__main__":
    challenges = cross_examine("TCS")
    print(f"CROSS-EXAMINATION for TCS:")
    if not challenges:
        print("  No direct contradictions found between Bull and Bear evidence.")
    for c in challenges:
        print(f"  - {c}")
