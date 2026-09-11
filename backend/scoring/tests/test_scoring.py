import pytest
from backend.scoring.scoring import calculate_score

def test_calculate_score_not_vasp():
    features = {
        "is_vasp_destination": False,
        "hop_count": 2,
        "amount_retention": 0.5,
        "supporting_path_count": 1
    }
    result = calculate_score(features)
    assert result.score == 0
    assert result.confidence_level == "VERY_LOW"

def test_calculate_score_perfect_match():
    features = {
        "is_vasp_destination": True,
        "vasp_name": "Test VASP",
        "hop_count": 1, # 25 points
        "amount_retention": 1.0, # 15 points
        "supporting_path_count": 5 # 10 points
    }
    result = calculate_score(features)
    # raw score = 40 (base) + 25 + 15 + 10 = 90
    # final score = (90/90) * 100 = 100
    assert result.score == 100
    assert result.confidence_level == "VERY_HIGH"

def test_calculate_score_average_match():
    features = {
        "is_vasp_destination": True,
        "vasp_name": "Test VASP",
        "hop_count": 3, # 19 points
        "amount_retention": 0.5, # 5 points
        "supporting_path_count": 2 # 6 points
    }
    result = calculate_score(features)
    # raw score = 40 + 19 + 5 + 6 = 70
    # final score = round((70/90) * 100) = 78
    assert result.score == 78
    assert result.confidence_level == "HIGH"
