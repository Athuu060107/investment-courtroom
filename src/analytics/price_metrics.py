import mysql.connector
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()

RISK_FREE_RATE = 0.07  # roughly the Indian 10-yr govt bond yield, used for Sharpe ratio


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl_ca="config/ca.pem",
    )
def get_engine():
    user = os.getenv("DB_USER")
    password = quote_plus(os.getenv("DB_PASSWORD"))
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "3306")
    dbname = os.getenv("DB_NAME")
    return create_engine(
        f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{dbname}",
        connect_args={"ssl_ca": "config/ca.pem"},
    )
def get_price_history(company_name):
    conn = get_engine()
    query = """
        SELECT sp.price_date, sp.close_price
        FROM stock_prices sp
        JOIN companies c ON sp.company_id = c.company_id
        WHERE c.name = %s
        ORDER BY sp.price_date
    """
    df = pd.read_sql(query, conn, params=(company_name,))
    conn.dispose()
    return df
def get_returns(company_name):
    df = get_price_history(company_name)
    df["daily_return"] = df["close_price"].pct_change()
    return df[["price_date", "daily_return"]].dropna()


def calculate_beta(company_name, market_name="NIFTY50"):
    stock_returns = get_returns(company_name)
    market_returns = get_returns(market_name)

    merged = pd.merge(stock_returns, market_returns, on="price_date", suffixes=("_stock", "_market"))

    covariance = merged["daily_return_stock"].cov(merged["daily_return_market"])
    market_variance = merged["daily_return_market"].var()

    beta = covariance / market_variance
    return beta


def calculate_cagr(df):
    start_price = df["close_price"].iloc[0]
    end_price = df["close_price"].iloc[-1]

    start_date = df["price_date"].iloc[0]
    end_date = df["price_date"].iloc[-1]
    years = (end_date - start_date).days / 365.25

    cagr = (end_price / start_price) ** (1 / years) - 1
    return cagr


def calculate_volatility(df):
    daily_returns = df["close_price"].pct_change().dropna()
    daily_vol = daily_returns.std()
    annual_vol = daily_vol * np.sqrt(252)  # 252 trading days in a year
    return annual_vol


def calculate_max_drawdown(df):
    prices = df["close_price"]
    running_max = prices.cummax()
    drawdown = (prices - running_max) / running_max
    return drawdown.min()  # most negative value = worst drawdown


def calculate_sharpe_ratio(df, cagr, volatility):
    if volatility == 0:
        return None
    sharpe = (cagr - RISK_FREE_RATE) / volatility
    return sharpe


def get_all_metrics(company_name):
    df = get_price_history(company_name)

    if df.empty:
        print(f"No price data found for {company_name}")
        return None

    cagr = calculate_cagr(df)
    volatility = calculate_volatility(df)
    max_drawdown = calculate_max_drawdown(df)
    sharpe = calculate_sharpe_ratio(df, cagr, volatility)

    return {
        "company": company_name,
        "cagr": round(cagr * 100, 2),
        "volatility": round(volatility * 100, 2),
        "max_drawdown": round(max_drawdown * 100, 2),
        "sharpe_ratio": round(sharpe, 2) if sharpe is not None else None,
    }


if __name__ == "__main__":
    result = get_all_metrics("TCS")
    print(result)

    beta = calculate_beta("TCS")
    print(f"TCS beta: {round(beta, 2)}")