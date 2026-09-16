-- Investment Courtroom database schema
-- Phase 2: core tables for companies, prices, financials, valuation

CREATE TABLE companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    ticker VARCHAR(20) NOT NULL UNIQUE,
    sector VARCHAR(50)
);

CREATE TABLE stock_prices (
    price_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    price_date DATE NOT NULL,
    open_price DECIMAL(12,2),
    high_price DECIMAL(12,2),
    low_price DECIMAL(12,2),
    close_price DECIMAL(12,2),
    volume BIGINT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE KEY unique_price (company_id, price_date)
);

CREATE TABLE financial_statements (
    statement_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    period_end_date DATE NOT NULL,
    revenue DECIMAL(20,2),
    ebitda DECIMAL(20,2),
    ebit DECIMAL(20,2),
    net_income DECIMAL(20,2),
    total_debt DECIMAL(20,2),
    cash DECIMAL(20,2),
    equity DECIMAL(20,2),
    operating_cash_flow DECIMAL(20,2),
    free_cash_flow DECIMAL(20,2),
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE KEY unique_statement (company_id, period_end_date)
);

CREATE TABLE valuation_metrics (
    valuation_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    market_cap DECIMAL(20,2),
    pe_ratio DECIMAL(10,2),
    pb_ratio DECIMAL(10,2),
    dividend_yield DECIMAL(10,4),
    roe DECIMAL(10,4),
    shares_outstanding BIGINT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE KEY unique_valuation (company_id)
);
CREATE TABLE financial_ratios (
    ratio_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    cagr DECIMAL(10,2),
    volatility DECIMAL(10,2),
    max_drawdown DECIMAL(10,2),
    sharpe_ratio DECIMAL(10,2),
    beta DECIMAL(10,2),
    roe DECIMAL(10,2),
    roce DECIMAL(10,2),
    net_margin DECIMAL(10,2),
    operating_margin DECIMAL(10,2),
    calculated_on DATE,
    FOREIGN KEY (company_id) REFERENCES companies(company_id),
    UNIQUE KEY unique_ratio (company_id)
);