from main import get_risk_level
import pytest

@pytest.mark.parametrize("score, expected", [
    (80, "低风险"),
    (79, "中风险"),
    (50, "中风险"),
    (49, "高风险"),
    (100, "低风险"),
    (0, "高风险")
])
def test_risk_level(score, expected):
    assert get_risk_level(score) == expected