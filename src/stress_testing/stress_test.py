from src.courtroom.bull_engine import get_company_data
from src.scoring.scorer import calculate_quality_score, calculate_valuation_score, calculate_growth_score, calculate_risk_score
from src.scoring.judge import calculate_overall_score, get_verdict


def apply_stress(data, revenue_decline_pct=0, margin_decline_pct=0, pe_shock_pct=0):
    # makes a stressed copy of the company's data - never touches the original
    stressed = dict(data)

    # revenue decline and margin decline both shrink net income
    # scale factor tells us how much smaller net income becomes as a result of both effects combined
    old_margin = float(data["net_margin"]) if data["net_margin"] is not None else None
    new_margin = None
    if old_margin is not None:
        new_margin = old_margin - margin_decline_pct
        stressed["net_margin"] = round(new_margin, 2)

    scale_factor = (1 - revenue_decline_pct / 100)
    if old_margin is not None and old_margin != 0 and new_margin is not None:
        scale_factor *= (new_margin / old_margin)

    if data["roe"] is not None:
        stressed["roe"] = round(float(data["roe"]) * scale_factor, 2)
    if data["roce"] is not None:
        stressed["roce"] = round(float(data["roce"]) * scale_factor, 2)

    if data["pe_ratio"] is not None:
        stressed["pe_ratio"] = round(float(data["pe_ratio"]) * (1 - pe_shock_pct / 100), 2)

    return stressed


def run_stress_test(company_name, revenue_decline_pct=0, margin_decline_pct=0, pe_shock_pct=0):
    baseline_data = get_company_data(company_name)
    if baseline_data is None:
        return None

    stressed_data = apply_stress(
        baseline_data,
        revenue_decline_pct=revenue_decline_pct,
        margin_decline_pct=margin_decline_pct,
        pe_shock_pct=pe_shock_pct,
    )

    # growth and risk scores stay based on real historical price data - a hypothetical
    # future shock doesn't rewrite what already happened to the stock's price
    baseline_scores = {
        "quality": calculate_quality_score(baseline_data),
        "growth": calculate_growth_score(baseline_data),
        "valuation": calculate_valuation_score(baseline_data),
        "risk": calculate_risk_score(baseline_data),
    }
    stressed_scores = {
        "quality": calculate_quality_score(stressed_data),
        "growth": baseline_scores["growth"],
        "valuation": calculate_valuation_score(stressed_data),
        "risk": baseline_scores["risk"],
    }

    baseline_overall = calculate_overall_score(baseline_scores)
    stressed_overall = calculate_overall_score(stressed_scores)

    return {
        "company": company_name,
        "baseline_scores": baseline_scores,
        "stressed_scores": stressed_scores,
        "baseline_overall": baseline_overall,
        "stressed_overall": stressed_overall,
        "baseline_verdict": get_verdict(baseline_overall),
        "stressed_verdict": get_verdict(stressed_overall),
    }


if __name__ == "__main__":
    result = run_stress_test("MARUTI", revenue_decline_pct=20, margin_decline_pct=5, pe_shock_pct=15)
    print(f"STRESS TEST for {result['company']}")
    print(f"Baseline: {result['baseline_overall']} ({result['baseline_verdict']})")
    print(f"Stressed: {result['stressed_overall']} ({result['stressed_verdict']})")
