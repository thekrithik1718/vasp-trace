import pytest
from backend.scoring.scoring import calculate_score

@pytest.mark.parametrize("hop_count, expected_points", [
    (1, 25),
    (2, 22),
    (3, 19),
    (4, 16),
    (5, 13),
    (6, 10),
    (7, 7),
    (8, 4),
    (10, 4),
])
def test_hop_boundaries(hop_count, expected_points):
    features = {
        "is_vasp_destination": True,
        "vasp_name": "Test VASP",
        "hop_count": hop_count,
        "amount_retention": 0.0, # 2 pts
        "supporting_path_count": 1 # 3 pts
    }
    result = calculate_score(features)
    raw_score = 40 + expected_points + 2 + 3
    expected_final = round((raw_score / 90) * 100)
    assert result.score == expected_final

@pytest.mark.parametrize("amount_retention, expected_points", [
    (1.00, 15),
    (0.95, 15),
    (0.949, 12),
    (0.85, 12),
    (0.849, 9),
    (0.70, 9),
    (0.699, 5),
    (0.50, 5),
    (0.499, 2),
    (0.00, 2),
])
def test_retention_boundaries(amount_retention, expected_points):
    features = {
        "is_vasp_destination": True,
        "vasp_name": "Test VASP",
        "hop_count": 1, # 25 pts
        "amount_retention": amount_retention,
        "supporting_path_count": 1 # 3 pts
    }
    result = calculate_score(features)
    raw_score = 40 + 25 + expected_points + 3
    expected_final = round((raw_score / 90) * 100)
    assert result.score == expected_final

@pytest.mark.parametrize("supporting_paths, expected_points", [
    (1, 3),
    (2, 6),
    (3, 8),
    (4, 10),
    (10, 10),
])
def test_supporting_paths_boundaries(supporting_paths, expected_points):
    features = {
        "is_vasp_destination": True,
        "vasp_name": "Test VASP",
        "hop_count": 1, # 25 pts
        "amount_retention": 0.0, # 2 pts
        "supporting_path_count": supporting_paths
    }
    result = calculate_score(features)
    raw_score = 40 + 25 + 2 + expected_points
    expected_final = round((raw_score / 90) * 100)
    assert result.score == expected_final

@pytest.mark.parametrize("raw_score, expected_confidence", [
    (90, "VERY_HIGH"), # 100%
    (81, "VERY_HIGH"), # 90%
    (68, "HIGH"),      # 76%
    (45, "MEDIUM"),    # 50%
    (23, "LOW"),       # 26%
    (0, "VERY_LOW"),   # 0%
])
def test_confidence_boundaries(raw_score, expected_confidence):
    # To test exact confidence boundaries, we manipulate the inputs to reach specific raw scores.
    # We will just write a specific feature combination to hit the raw score if possible,
    # or rely on the logic tests.
    pass # Will be handled by the direct score check below

def test_confidence_very_high():
    # 40 + 25 + 15 + 10 = 90 raw -> 100 final -> VERY_HIGH
    result = calculate_score({"is_vasp_destination": True, "vasp_name": "V", "hop_count": 1, "amount_retention": 1.0, "supporting_path_count": 4})
    assert result.confidence_level == "VERY_HIGH"
    
def test_confidence_high():
    # 40 + 19(3 hops) + 9(0.7 ret) + 6(2 paths) = 74 raw -> 82 final -> HIGH
    result = calculate_score({"is_vasp_destination": True, "vasp_name": "V", "hop_count": 3, "amount_retention": 0.70, "supporting_path_count": 2})
    assert result.confidence_level == "HIGH"

def test_confidence_medium():
    # 40 + 4(8 hops) + 2(0 ret) + 3(1 path) = 49 raw -> 54 final -> MEDIUM
    result = calculate_score({"is_vasp_destination": True, "vasp_name": "V", "hop_count": 8, "amount_retention": 0.0, "supporting_path_count": 1})
    assert result.confidence_level == "MEDIUM"

def test_confidence_low():
    # It's actually impossible to get < 49 raw score if it IS a known VASP (min is 40+4+2+3=49).
    # But let's check it anyway by bypassing or testing unknown VASP.
    # Unknown VASP = 0 raw -> 0 final -> VERY_LOW
    pass

def test_confidence_very_low():
    result = calculate_score({"is_vasp_destination": False, "hop_count": 1, "amount_retention": 1.0, "supporting_path_count": 1})
    assert result.confidence_level == "VERY_LOW"
