import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.scoring.scorer import score_higher_is_better, score_lower_is_better
from src.scoring.judge import calculate_overall_score, get_verdict
from src.data.case_mode import evaluate_decision
from src.stress_testing.stress_test import apply_stress


def test_score_higher_is_better_boundaries():
    assert score_higher_is_better(0, 0, 30) == 0
    assert score_higher_is_better(30, 0, 30) == 100
    assert score_higher_is_better(15, 0, 30) == 50
    assert score_higher_is_better(-5, 0, 30) == 0  # below range clamps to 0
    assert score_higher_is_better(100, 0, 30) == 100  # above range clamps to 100
    assert score_higher_is_better(None, 0, 30) is None


def test_score_lower_is_better_boundaries():
    assert score_lower_is_better(10, 10, 50) == 100
    assert score_lower_is_better(50, 10, 50) == 0
    assert score_lower_is_better(30, 10, 50) == 50
    assert score_lower_is_better(5, 10, 50) == 100  # below range clamps to 100 (cheap is good)
    assert score_lower_is_better(None, 10, 50) is None


def test_get_verdict_thresholds():
    assert get_verdict(70) == "BUY"
    assert get_verdict(100) == "BUY"
    assert get_verdict(69.9) == "HOLD / WATCH"
    assert get_verdict(50) == "HOLD / WATCH"
    assert get_verdict(49.9) == "AVOID"
    assert get_verdict(0) == "AVOID"
    assert get_verdict(None) == "INSUFFICIENT DATA"


def test_calculate_overall_score_all_pillars_present():
    scores = {"quality": 80, "growth": 60, "valuation": 40, "risk": 100}
    expected = 80 * 0.35 + 60 * 0.25 + 40 * 0.20 + 100 * 0.20
    assert calculate_overall_score(scores) == round(expected, 1)


def test_calculate_overall_score_missing_pillar_renormalizes():
    scores = {"quality": 80, "growth": 60, "valuation": None, "risk": 100}
    result = calculate_overall_score(scores)
    naive_score_if_treated_as_zero = 80 * 0.35 + 60 * 0.25 + 0 * 0.20 + 100 * 0.20
    assert result > naive_score_if_treated_as_zero


def test_calculate_overall_score_all_missing_returns_none():
    scores = {"quality": None, "growth": None, "valuation": None, "risk": None}
    assert calculate_overall_score(scores) is None


def test_evaluate_decision_buy():
    assert evaluate_decision("BUY", 15) is True
    assert evaluate_decision("BUY", 10) is False
    assert evaluate_decision("BUY", -5) is False


def test_evaluate_decision_avoid():
    assert evaluate_decision("AVOID", -15) is True
    assert evaluate_decision("AVOID", -10) is False
    assert evaluate_decision("AVOID", 5) is False


def test_evaluate_decision_hold():
    assert evaluate_decision("HOLD", 0) is True
    assert evaluate_decision("HOLD", 10) is True
    assert evaluate_decision("HOLD", -10) is True
    assert evaluate_decision("HOLD", 11) is False
    assert evaluate_decision("HOLD", -11) is False


def test_apply_stress_no_shock_leaves_data_unchanged():
    data = {"net_margin": 20, "roe": 15, "roce": 18, "pe_ratio": 25}
    stressed = apply_stress(data, revenue_decline_pct=0, margin_decline_pct=0, pe_shock_pct=0)
    assert stressed["net_margin"] == 20
    assert stressed["roe"] == 15
    assert stressed["pe_ratio"] == 25


def test_apply_stress_reduces_roe_under_shock():
    data = {"net_margin": 20, "roe": 15, "roce": 18, "pe_ratio": 25}
    stressed = apply_stress(data, revenue_decline_pct=20, margin_decline_pct=5, pe_shock_pct=0)
    assert stressed["roe"] < 15
    assert stressed["net_margin"] == 15


def test_apply_stress_pe_shock_reduces_pe_only():
    data = {"net_margin": 20, "roe": 15, "roce": 18, "pe_ratio": 40}
    stressed = apply_stress(data, revenue_decline_pct=0, margin_decline_pct=0, pe_shock_pct=25)
    assert stressed["pe_ratio"] == 30
    assert stressed["roe"] == 15
