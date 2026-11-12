from main import get_risk_level

def test_score_80():
    assert get_risk_level(80) == "低风险"

def test_score_79():
    assert get_risk_level(79) == "中风险"

def test_score_50():
    assert get_risk_level(50) == "中风险"

def test_score_49():
    assert get_risk_level(49) == "高风险"