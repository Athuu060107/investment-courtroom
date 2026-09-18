import mysql.connector
import os
from dotenv import load_dotenv

from src.scoring.scorer import score_higher_is_better, score_lower_is_better

load_dotenv()

MIN_DECISIONS_NEEDED = 3

SECTOR_MAP = {
    "HDFCBANK": "Banking", "ICICIBANK": "Banking", "SBIN": "Banking",
    "TCS": "IT", "INFY": "IT", "WIPRO": "IT",
    "RELIANCE": "Energy", "ONGC": "Energy",
    "HINDUNILVR": "FMCG", "ITC": "FMCG",
    "TATAMOTORS": "Auto", "MARUTI": "Auto",
    "SUNPHARMA": "Pharma", "DRREDDY": "Pharma",
    "ULTRACEMCO": "Cement",
}


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
    )


def get_decisions_with_context():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT ud.decision, ud.was_correct, c.name AS company_name,
               ic.cagr_as_of_case, ic.volatility_as_of_case, vm.pe_ratio
        FROM user_decisions ud
        JOIN investment_cases ic ON ud.case_id = ic.case_id
        JOIN companies c ON ic.company_id = c.company_id
        LEFT JOIN valuation_metrics vm ON vm.company_id = c.company_id
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def average(values):
    valid = [v for v in values if v is not None]
    if not valid:
        return None
    return sum(float(v) for v in valid) / len(valid)


def calculate_investor_profile():
    decisions = get_decisions_with_context()

    if len(decisions) < MIN_DECISIONS_NEEDED:
        return {
            "enough_data": False,
            "decisions_made": len(decisions),
            "decisions_needed": MIN_DECISIONS_NEEDED,
        }

    buys = [d for d in decisions if d["decision"] == "BUY"]
    correct_count = sum(1 for d in decisions if d["was_correct"])
    accuracy = round((correct_count / len(decisions)) * 100, 1)

    avg_cagr_buy = average([d["cagr_as_of_case"] for d in buys])
    avg_volatility_buy = average([d["volatility_as_of_case"] for d in buys])
    avg_pe_buy = average([d["pe_ratio"] for d in buys])

    growth_bias = score_higher_is_better(avg_cagr_buy, 0, 25) if avg_cagr_buy is not None else None
    value_bias = round(100 - growth_bias, 1) if growth_bias is not None else None
    risk_appetite = score_higher_is_better(avg_volatility_buy, 15, 40) if avg_volatility_buy is not None else None
    valuation_discipline = score_lower_is_better(avg_pe_buy, 10, 50) if avg_pe_buy is not None else None

    buy_sectors = set(SECTOR_MAP.get(d["company_name"], "Unknown") for d in buys)
    total_sectors = len(set(SECTOR_MAP.values()))
    diversification_discipline = round((len(buy_sectors) / total_sectors) * 100, 1) if buys else None

    observations = []
    if growth_bias is not None and growth_bias > 65:
        observations.append("You tend to favor high-growth stories when deciding to buy, even when that growth came with more volatility.")
    if risk_appetite is not None and risk_appetite > 65:
        observations.append("You've shown a willingness to buy into higher-volatility stocks rather than sticking to calmer ones.")
    if valuation_discipline is not None and valuation_discipline < 40:
        observations.append("Your buy decisions have leaned toward stocks that are currently expensive on a P/E basis.")
    if diversification_discipline is not None and diversification_discipline < 30 and len(buys) >= 2:
        observations.append("Your buy decisions have clustered in a narrow set of sectors rather than spreading across the market.")
    if not observations:
        observations.append("Not enough of a clear pattern yet — play a few more cases to sharpen this profile.")

    return {
        "enough_data": True,
        "decisions_made": len(decisions),
        "accuracy": accuracy,
        "growth_bias": growth_bias,
        "value_bias": value_bias,
        "risk_appetite": risk_appetite,
        "valuation_discipline": valuation_discipline,
        "diversification_discipline": diversification_discipline,
        "observations": observations,
    }


if __name__ == "__main__":
    profile = calculate_investor_profile()
    print(profile)
