import pytest
from datetime import datetime
from backend.scoring.schemas import GraphInput, TransactionPath, Transaction
from backend.scoring.pipeline import run_scoring_pipeline

class MockDetector:
    def get_vasp_name(self, address):
        if address == "VASP001":
            return "Exchange Alpha"
        return None

def test_run_scoring_pipeline():
    # Setup mock input
    tx = Transaction(**{"from": "SUSP", "to": "VASP001", "amount": 100, "timestamp": datetime.now(), "tx_hash": "tx1"})
    
    path1 = TransactionPath(
        addresses=["SUSP", "A", "VASP001"],
        transactions=[tx],
        hop_count=2,
        original_amount=100.0,
        final_amount=90.0
    )
    
    path2 = TransactionPath(
        addresses=["SUSP", "B", "VASP001"],
        transactions=[tx],
        hop_count=2,
        original_amount=100.0,
        final_amount=95.0
    )
    
    path3 = TransactionPath(
        addresses=["SUSP", "C", "UNKNOWN"],
        transactions=[],
        hop_count=2,
        original_amount=100.0,
        final_amount=50.0
    )
    
    graph_input = GraphInput(source_wallet="SUSP", paths=[path1, path2, path3])
    
    results = run_scoring_pipeline(graph_input, MockDetector())
    
    assert len(results) == 3
    # First two should be VASP001 (score > 0), third should be UNKNOWN (score 0)
    # They should be ranked by score descending
    assert results[0].vasp_name == "Exchange Alpha"
    assert results[1].vasp_name == "Exchange Alpha"
    assert results[2].vasp_name is None
    assert results[2].score == 0
