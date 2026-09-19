import pytest
from backend.app.services.scoring import compute_weighted_score, calculate_attribute_score

def test_weighted_score_calculation():
    """
    Test 0.50*semantic + 0.30*fuzzy + 0.20*attribute scoring formula.
    """
    sem = 0.92
    fuz = 0.88
    attr = 0.95
    # expected: 0.50 * 0.92 + 0.30 * 0.88 + 0.20 * 0.95 = 0.46 + 0.264 + 0.19 = 0.914
    score, band = compute_weighted_score(sem, fuz, attr)
    assert score == pytest.approx(0.914, abs=1e-3)
    assert band == "HIGH"

def test_confidence_routing_bands():
    # HIGH (> 0.90)
    score_high, band_high = compute_weighted_score(0.95, 0.92, 0.90)
    assert band_high == "HIGH"

    # MEDIUM (0.60 - 0.90)
    score_med, band_med = compute_weighted_score(0.70, 0.75, 0.80)
    assert band_med == "MEDIUM"

    # LOW (< 0.60)
    score_low, band_low = compute_weighted_score(0.40, 0.50, 0.30)
    assert band_low == "LOW"

def test_attribute_type_discrimination_gate_vs_globe():
    """
    Deliberate Near-Miss: Gate Valve vs Globe Valve.
    Critical equipment type conflict must yield 0.0 attribute score!
    """
    attr_gate = {
        "type": "GATE VALVE",
        "material": "CARBON STEEL",
        "size_mm": "150MM (6 INCH)",
        "pressure_class": "CLASS 150"
    }
    attr_globe = {
        "type": "GLOBE VALVE",
        "material": "CARBON STEEL",
        "size_mm": "150MM (6 INCH)",
        "pressure_class": "CLASS 150"
    }
    score = calculate_attribute_score(attr_gate, attr_globe)
    assert score == 0.0

def test_attribute_matching_identical():
    attr1 = {
        "type": "GATE VALVE",
        "material": "CARBON STEEL",
        "size_mm": "150MM (6 INCH)",
        "pressure_class": "CLASS 150"
    }
    attr2 = {
        "type": "GATE VALVE",
        "material": "CARBON STEEL",
        "size_mm": "150MM (6 INCH)",
        "pressure_class": "CLASS 150"
    }
    score = calculate_attribute_score(attr1, attr2)
    assert score >= 0.95
