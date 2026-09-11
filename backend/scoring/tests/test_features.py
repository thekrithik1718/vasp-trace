import pytest
from datetime import datetime
from backend.scoring.schemas import TransactionPath, Transaction
from backend.scoring.features import extract_features

class MockDetector:
    def get_vasp_name(self, address):
        if address == "VASP_KNOWN":
            return "Test VASP"
        return None

def test_extract_features():
    path = TransactionPath(
        addresses=["SUSP", "A", "VASP_KNOWN"],
        transactions=[
            Transaction(**{"from": "SUSP", "to": "A", "amount": 100, "timestamp": datetime.now(), "tx_hash": "tx1"}),
            Transaction(**{"from": "A", "to": "VASP_KNOWN", "amount": 90, "timestamp": datetime.now(), "tx_hash": "tx2"}),
        ],
        hop_count=2,
        original_amount=100.0,
        final_amount=90.0
    )
    detector = MockDetector()
    
    features = extract_features(path, detector, total_paths_to_destination=3)
    
    assert features["vasp_name"] == "Test VASP"
    assert features["is_vasp_destination"] is True
    assert features["hop_count"] == 2
    assert features["amount_retention"] == 0.9
    assert features["supporting_path_count"] == 3

def test_extract_features_not_vasp():
    path = TransactionPath(
        addresses=["SUSP", "UNKNOWN"],
        transactions=[],
        hop_count=1,
        original_amount=100.0,
        final_amount=100.0
    )
    features = extract_features(path, MockDetector(), 1)
    assert features["is_vasp_destination"] is False
    assert features["vasp_name"] is None
