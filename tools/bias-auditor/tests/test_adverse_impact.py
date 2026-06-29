"""Unit tests for the core adverse-impact math. Run: pytest -q"""
import pandas as pd

from src.adverse_impact import (
    analyze_attribute,
    coerce_outcome,
    two_proportion_ztest,
)


def _funnel(male_hired, male_n, female_hired, female_n):
    rows = []
    rows += [{"gender": "Male", "hired": 1}] * male_hired
    rows += [{"gender": "Male", "hired": 0}] * (male_n - male_hired)
    rows += [{"gender": "Female", "hired": 1}] * female_hired
    rows += [{"gender": "Female", "hired": 0}] * (female_n - female_hired)
    return pd.DataFrame(rows)


def test_four_fifths_worked_example():
    # Men 40/100 (0.40), Women 28/100 (0.28) -> impact ratio 0.70 -> flagged.
    df = _funnel(40, 100, 28, 100)
    res = analyze_attribute(df, "gender", "hired")
    assert res.reference_group == "Male"
    female = next(g for g in res.groups if g.group == "Female")
    assert abs(female.selection_rate - 0.28) < 1e-9
    assert abs(female.impact_ratio - 0.70) < 1e-9
    assert female.four_fifths_flag is True
    assert res.any_flag is True


def test_no_flag_when_rates_close():
    # Men 40/100 (0.40), Women 36/100 (0.36) -> ratio 0.90 -> no flag.
    df = _funnel(40, 100, 36, 100)
    res = analyze_attribute(df, "gender", "hired")
    female = next(g for g in res.groups if g.group == "Female")
    assert abs(female.impact_ratio - 0.90) < 1e-9
    assert female.four_fifths_flag is False
    assert res.any_flag is False


def test_reference_is_highest_rate_group():
    df = _funnel(20, 100, 50, 100)  # women higher
    res = analyze_attribute(df, "gender", "hired")
    assert res.reference_group == "Female"
    male = next(g for g in res.groups if g.group == "Male")
    assert male.impact_ratio < 0.8 and male.four_fifths_flag is True


def test_two_proportion_ztest_significance():
    # Large, clearly different proportions -> small p-value.
    z, p = two_proportion_ztest(40, 100, 28, 100)
    assert p < 0.10
    # Identical proportions -> p ~ 1.
    z2, p2 = two_proportion_ztest(40, 100, 40, 100)
    assert abs(z2) < 1e-9 and abs(p2 - 1.0) < 1e-9


def test_coerce_outcome_tokens():
    s = pd.Series([1, 0, "Yes", "no", "Hired", "", None, True, False])
    out = list(coerce_outcome(s))
    assert out == [1, 0, 1, 0, 1, 0, 0, 1, 0]
