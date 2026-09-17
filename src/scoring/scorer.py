def score_higher_is_better(value, low, high):
    # turns a raw metric into a 0-100 score, where higher raw value = higher score
    # anything at or below "low" scores 0, anything at or above "high" scores 100
    if value is None:
        return None
    if value <= low:
        return 0
    if value >= high:
        return 100
    return round((value - low) / (high - low) * 100, 1)


def score_lower_is_better(value, low, high):
    # same idea but flipped - used for things like P/E or volatility where lower is better
    if value is None:
        return None
    if value <= low:
        return 100
    if value >= high:
        return 0
    return round((high - value) / (high - low) * 100, 1)


def average_ignoring_none(values):
    valid = [v for v in values if v is not None]
    if not valid:
        return None
    return round(sum(valid) / len(valid), 1)


def calculate_quality_score(data):
    roe_score = score_higher_is_better(data["roe"], 0, 30)
    roce_score = score_higher_is_better(data["roce"], 0, 30)
    margin_score = score_higher_is_better(data["net_margin"], 0, 25)
    return average_ignoring_none([roe_score, roce_score, margin_score])


def calculate_growth_score(data):
    return score_higher_is_better(data["cagr"], -10, 20)


def calculate_valuation_score(data):
    pe_score = score_lower_is_better(data["pe_ratio"], 10, 50)
    pb_score = score_lower_is_better(data["pb_ratio"], 1, 10)
    return average_ignoring_none([pe_score, pb_score])


def calculate_risk_score(data):
    # higher risk_score = safer/lower risk, to stay consistent with the other pillars
    volatility_score = score_lower_is_better(data["volatility"], 15, 40)
    drawdown_score = score_lower_is_better(abs(data["max_drawdown"]) if data["max_drawdown"] is not None else None, 15, 60)
    sharpe_score = score_higher_is_better(data["sharpe_ratio"], -1, 1)
    return average_ignoring_none([volatility_score, drawdown_score, sharpe_score])
