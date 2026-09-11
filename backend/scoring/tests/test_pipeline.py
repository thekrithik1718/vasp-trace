import pytest
from datetime import datetime
from backend.scoring.schemas import GraphInput, TransactionPath, Transaction
from backend.scoring.pipeline import run_scoring_pipeline

class MockDetector:
    def get_vasp_name(self, address):
        if address == "VASP_A":
            return "Exchange Alpha"
        if address == "VASP_B":
            return "Exchange Beta"
        return None

def test_run_scoring_pipeline_sorting_and_exclusion():
    tx = Transaction(**{"from": "SUSP", "to": "VASP_A", "amount": 100, "timestamp": datetime.now(), "tx_hash": "tx1"})
    
    # Path 1: 1 hop to VASP_A (Should score high)
    path1 = TransactionPath(
        addresses=["SUSP", "VASP_A"],
        transactions=[tx],
        hop_count=1,
        original_amount=100.0,
        final_amount=100.0
    )
    
    # Path 2: 3 hops to VASP_B (Should score lower than VASP_A)
    path2 = TransactionPath(
        addresses=["SUSP", "X", "Y", "VASP_B"],
        transactions=[tx],
        hop_count=3,
        original_amount=100.0,
        final_amount=90.0
    )
    
    # Path 3: 4 hops to UNKNOWN (Should be excluded)
    path3 = TransactionPath(
        addresses=["SUSP", "C", "D", "E", "UNKNOWN"],
        transactions=[],
        hop_count=4,
        original_amount=100.0,
        final_amount=50.0
    )
    
    # Path 4: duplicate path to VASP_B (Increases supporting paths for VASP_B)
    path4 = TransactionPath(
        addresses=["SUSP", "X", "Z", "VASP_B"],
        transactions=[tx],
        hop_count=3,
        original_amount=100.0,
        final_amount=80.0
    )
    
    graph_input = GraphInput(source_wallet="SUSP", paths=[path1, path2, path3, path4])
    
    results = run_scoring_pipeline(graph_input, MockDetector())
    
    # Excluded the UNKNOWN, so we expect 3 results (1 for VASP_A, 2 for VASP_B)
    assert len(results) == 3
    
    # They should be sorted by score descending
    assert results[0].score >= results[1].score
    assert results[1].score >= results[2].score
    
    # VASP_A should be the highest (1 hop, 100% retention)
    assert results[0].vasp_name == "Exchange Alpha"
    
    # The others should be Exchange Beta
    assert results[1].vasp_name == "Exchange Beta"
    assert results[2].vasp_name == "Exchange Beta"
    
    # Verify supporting paths incremented correctly (VASP_A = 1 path, VASP_B = 2 paths)
    assert results[0].supporting_path_count == 1
    assert results[1].supporting_path_count == 2
    assert results[2].supporting_path_count == 2
