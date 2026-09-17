from src.courtroom.bull_engine import get_company_data, build_bull_case
from src.courtroom.bear_engine import build_bear_case
from src.courtroom.cross_exam import cross_examine
from src.scoring.scorer import (
    calculate_quality_score,
    calculate_growth_score,
    calculate_valuation_score,
    calculate_risk_score,
)

# illustrative weights - not tuned against real outcomes, just a reasonable starting point
WEIGHTS = {
    "quality": 0.35,
    "growth": 0.25,
    "valuation": 0.20,
    "risk": 0.20,
}


def calculate_overall_score(pillar_scores):
    available = {k: v for k, v in pillar_scores.items() if v is not None}
    if not available:
        return None

    # if a pillar is missing (e.g. no P/E data), we still calculate a fair score
    # by only weighting the pillars we actually have data for
    total_weight = sum(WEIGHTS[k] for k in available)
    weighted_sum = sum(pillar_scores[k] * WEIGHTS[k] for k in available)
    return round(weighted_sum / total_weight, 1)


def get_verdict(overall_score):
    if overall_score is None:
        return "INSUFFICIENT DATA"
    if overall_score >= 70:
        return "BUY"
    if overall_score >= 50:
        return "HOLD / WATCH"
    return "AVOID"


def find_weakest_pillar(pillar_scores):
    available = {k: v for k, v in pillar_scores.items() if v is not None}
    if not available:
        return None
    return min(available, key=available.get)


def judge_company(company_name):
    data = get_company_data(company_name)
    if data is None:
        print(f"No data found for {company_name}")
        return None

    pillar_scores = {
        "quality": calculate_quality_score(data),
        "growth": calculate_growth_score(data),
        "valuation": calculate_valuation_score(data),
        "risk": calculate_risk_score(data),
    }

    overall_score = calculate_overall_score(pillar_scores)
    verdict = get_verdict(overall_score)

    bull_points = build_bull_case(company_name)
    bear_points = build_bear_case(company_name)
    challenges = cross_examine(company_name)

    strongest_bull = bull_points[0] if bull_points else "No strong bullish signals found."
    strongest_bear = bear_points[0] if bear_points else "No strong bearish signals found."
    weakest_pillar = find_weakest_pillar(pillar_scores)

    return {
        "company": company_name,
        "pillar_scores": pillar_scores,
        "overall_score": overall_score,
        "verdict": verdict,
        "strongest_bull_argument": strongest_bull,
        "strongest_bear_argument": strongest_bear,
        "biggest_risk": weakest_pillar,
        "bull_case": bull_points,
        "bear_case": bear_points,
        "cross_examination": challenges,
    }


def print_verdict(company_name):
    result = judge_company(company_name)
    if result is None:
        return

    print(f"\nINVESTMENT COURTROOM — {result['company']}")
    print(f"Quality Score: {result['pillar_scores']['quality']}")
    print(f"Growth Score: {result['pillar_scores']['growth']}")
    print(f"Valuation Score: {result['pillar_scores']['valuation']}")
    print(f"Risk Score: {result['pillar_scores']['risk']}")
    print(f"\nOverall Score: {result['overall_score']}")
    print(f"VERDICT: {result['verdict']}")
    print(f"\nStrongest Bull Argument: {result['strongest_bull_argument']}")
    print(f"Strongest Bear Argument: {result['strongest_bear_argument']}")
    print(f"Weakest area (biggest risk): {result['biggest_risk']}")


if __name__ == "__main__":
    print_verdict("MARUTI")
