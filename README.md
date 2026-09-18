# ⚖️ Investment Courtroom

**Every investment has a case. The Court decides whether it deserves your money.**

A rule-based investment analysis tool that puts a stock "on trial." A Bull side builds the
strongest case for investing, a Bear side builds the strongest case against it, a Cross-Examination
engine checks where their evidence actually contradicts, and a Judge combines everything into an
explainable BUY / HOLD / AVOID verdict — all backed by real financial data, not a black-box model.

Built as a portfolio project to combine Python, SQL, data analytics, and financial analysis into
something that actually works end-to-end, not just a notebook.

---



## Screenshots



**Home**

![Home page](docs/screenshots/01_home.png)



**Stock Court** — real 5-year price history and key metrics

![Stock Court](docs/screenshots/02_stock_court.png)



**Bull vs Bear** — TCS: strong fundamentals vs. a real multi-year price decline

![Bull vs Bear](docs/screenshots/03_bull_vs_bear.png)



**Judge's Verdict** — the same TCS case, combined into one explainable score

![Judge's Verdict](docs/screenshots/04_judges_verdict.png)



**Stress Test** — MARUTI's verdict shifting under a simulated downturn

![Stress Test](docs/screenshots/05_stress_test.png)



**Portfolio Court** — sector concentration and diversification check

![Portfolio Court](docs/screenshots/06_portfolio_court.png)



**Historical Case Mode** — blind-guessing game using real historical data

![Historical Case Mode](docs/screenshots/07_historical_case.png)

## What it actually does

* **Stock Court** — pick any of 15 tracked companies, see a 5-year price chart and 8 key financial metrics
* **Bull vs Bear** — rule-based arguments generated from real computed ratios (CAGR, ROE, ROCE, Sharpe, beta, margins)
* **Cross-Examination** — checks whether the Bear's evidence actually undercuts a specific Bull claim (e.g. "growth looks strong, but it's already priced into an expensive P/E")
* **Judge's Verdict** — a weighted 4-pillar score (Quality / Growth / Valuation / Risk) with a plain-language explanation of the strongest arguments on each side
* **Stress Test** — drag sliders to simulate a revenue decline, margin compression, or P/E contraction, and watch the verdict update live
* **Portfolio Court** — build a multi-stock portfolio and get real diversification-aware volatility, drawdown, Sharpe ratio, and a sector-concentration check
* **Historical Case Mode** — a blind-guessing game: see a real, anonymized case from ~2 years ago, guess BUY/HOLD/AVOID, then find out what actually happened
* **Investor DNA** — a behavioral profile (growth bias, risk appetite, valuation discipline, etc.) built from your own decisions in Historical Case Mode
* **AI Courtroom** *(optional)* — the same computed evidence, narrated as natural courtroom dialogue by an LLM, which is strictly constrained to never invent a number

---

## Tech stack

|Layer|Tool|
|-|-|
|Language|Python|
|Data analysis|Pandas, NumPy|
|Database|MySQL|
|Visualization|Plotly|
|Web app|Streamlit|
|AI narration (optional)|Google Gemini API|
|Data source|yfinance|
|Version control|Git / GitHub|

---

## How it works

```mermaid
flowchart TD
    A[yfinance] -->|prices + fundamentals| B[(MySQL Database)]
    B --> C[Analytics Engine<br/>CAGR, volatility, Sharpe,<br/>beta, ROE, ROCE, margins]
    C --> D[Bull Engine]
    C --> E[Bear Engine]
    D --> F[Cross-Examination Engine]
    E --> F
    C --> G[Scoring Engine<br/>Quality / Growth / Valuation / Risk]
    G --> H[Judge<br/>Overall Score + Verdict]
    D --> H
    E --> H
    F --> H
    H --> I[Streamlit App]
    D --> I
    E --> I
    F --> I
    H -.optional.-> J[AI Narrator<br/>Gemini API]
    J -.-> I
```

Nothing downstream of the database is a black box — every argument the Bull or Bear makes, and
every score the Judge produces, is directly traceable back to a real, computed number. The optional
AI layer only rephrases evidence that already exists; it is never asked to analyze anything itself.

---

## Database schema

```mermaid
erDiagram
    companies ||--o{ stock_prices : has
    companies ||--o{ financial_statements : has
    companies ||--o{ valuation_metrics : has
    companies ||--o{ financial_ratios : has
    companies ||--o{ investment_cases : has
    investment_cases ||--o{ user_decisions : has

    companies {
        int company_id PK
        string name
        string ticker
        string sector
    }
    stock_prices {
        int price_id PK
        int company_id FK
        date price_date
        decimal close_price
        bigint volume
    }
    financial_statements {
        int statement_id PK
        int company_id FK
        date period_end_date
        decimal revenue
        decimal net_income
        decimal total_debt
        decimal equity
    }
    valuation_metrics {
        int valuation_id PK
        int company_id FK
        decimal market_cap
        decimal pe_ratio
        decimal pb_ratio
    }
    financial_ratios {
        int ratio_id PK
        int company_id FK
        decimal cagr
        decimal volatility
        decimal sharpe_ratio
        decimal beta
        decimal roe
        decimal roce
    }
    investment_cases {
        int case_id PK
        int company_id FK
        date case_date
        decimal outcome_return_1y
    }
    user_decisions {
        int decision_id PK
        int case_id FK
        string decision
        boolean was_correct
    }
```

---

## Testing

Core calculation logic (scoring, stress testing, and the Historical Case correctness rules) has
unit tests covering boundary conditions and known expected values:

```bash
pip install pytest
pytest tests/test_calculations.py -v
```

---

## Companies covered

15 large-cap NSE-listed companies across Banking, IT, Energy, FMCG, Auto, Pharma, and Cement,
plus the Nifty 50 index as a market benchmark for beta calculations.

---

## Running it locally

```bash
git clone https://github.com/Athuu060107/investment-courtroom.git
cd investment-courtroom
python -m venv venv
venv\\Scripts\\activate          # Windows
pip install -r requirements.txt
```

Create a `.env` file in the project root with:

```
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=investment_courtroom
GEMINI_API_KEY=your_gemini_api_key   # only needed for the optional AI Courtroom page
```

Set up the database, then run the data pipeline in order:

```bash
python -m src.data.fetch_prices
python -m src.data.fetch_fundamentals
python -m src.data.fetch_market_index
python -m src.data.load_to_database
python -m src.analytics.save_ratios
python -m src.data.generate_historical_cases
```

Then launch the app:

```bash
streamlit run app\\Home.py
```

---

## Known limitations

* The scoring weights and Bull/Bear thresholds are illustrative, chosen to be reasonable and
explainable — not backtested or statistically optimized against real market outcomes.
* ROCE is unavailable for banks (HDFCBANK, ICICIBANK, SBIN) since they don't report EBIT in the
standard way — the tool surfaces this as a real limitation rather than hiding it.
* Historical Case Mode reconstructs price-based metrics (CAGR, volatility) as they would have
looked at the case date, but does not yet reconstruct historical fundamentals (ROE, margins) —
only current-day fundamentals are available in Investor DNA's Valuation Discipline score.
* Portfolio beta and CAGR use a weighted-average approximation rather than a full covariance-based
reconstruction (volatility and drawdown, however, ARE computed from real combined daily returns).
* The AI Courtroom feature depends on a third-party API (Google Gemini) with a free-tier quota;
every other feature in this app has zero dependency on any external AI service.

## Possible future improvements

* Reconstruct historical fundamentals for Historical Case Mode and Investor DNA
* Backtest and tune the scoring weights against actual historical outcomes
* Expand beyond 15 companies
* Deploy publicly (Streamlit Community Cloud)
* Add a proper covariance-matrix-based portfolio beta and expected return model

---

## Author

Built by Atharva Jadhav as a personal project to bring together data analytics, financial
analysis, and full-stack Python development in one place.

