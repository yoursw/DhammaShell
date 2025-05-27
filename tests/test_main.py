import pytest
from dhammashell.main import DhammaShell


def test_compassion_analysis():
    ds = DhammaShell()

    # Test positive message
    score, feedback = ds.analyze_compassion("I appreciate your help and kindness")
    assert score >= 4
    assert "Excellent" in feedback

    # Test negative message
    score, feedback = ds.analyze_compassion("I hate this stupid thing")
    assert score <= 2
    assert "rephrasing" in feedback

    # Test neutral message
    score, feedback = ds.analyze_compassion("The weather is cloudy today")
    assert 2 <= score <= 4


def test_calm_mode():
    ds = DhammaShell(calm_mode=True)
    assert ds.calm_mode is True
