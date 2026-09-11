import pytest
from datetime import datetime
from backend.scoring.schemas import TransactionPath, Transaction
from backend.scoring.features import extract_features

class MockDetector:
    def get_vasp_name(self, address):
        if address == "VASP_KNOWN":
            return "Test VASP"
        return None

def test_extract_features_zero_original_amount():
    path = TransactionPath(
        addresses=["A", "VASP_KNOWN"],
        transactions=[],
        hop_count=1,
        original_amount=0.0,
        final_amount=0.0
    )
    features = extract_features(path, MockDetector(), 1)
    assert features["amount_retention"] == 0.0

def test_extract_features_zero_final_amount():
    path = TransactionPath(
        addresses=["A", "VASP_KNOWN"],
        transactions=[],
        hop_count=1,
        original_amount=100.0,
        final_amount=0.0
    )
    features = extract_features(path, MockDetector(), 1)
    assert features["amount_retention"] == 0.0

def test_extract_features_empty_paths():
    path = TransactionPath(
        addresses=[],
        transactions=[],
        hop_count=0,
        original_amount=100.0,
        final_amount=100.0
    )
    features = extract_features(path, MockDetector(), 1)
    assert features["is_vasp_destination"] is False
    assert features["vasp_name"] is None

def test_extract_features_unknown_vasp():
    path = TransactionPath(
        addresses=["A", "UNKNOWN"],
        transactions=[],
        hop_count=1,
        original_amount=100.0,
        final_amount=100.0
    )
    features = extract_features(path, MockDetector(), 1)
    assert features["is_vasp_destination"] is False
    assert features["vasp_name"] is None

def test_extract_features_8_plus_hops():
    path = TransactionPath(
        addresses=["A"] + ["B"]*8 + ["VASP_KNOWN"],
        transactions=[],
        hop_count=9,
        original_amount=100.0,
        final_amount=100.0
    )
    features = extract_features(path, MockDetector(), 1)
    assert features["hop_count"] == 9
