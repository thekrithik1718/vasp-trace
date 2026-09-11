"""Integration test verifying Member 1 graph traversal and Member 2 scoring pipeline."""

import pytest
import pandas as pd
import networkx as nx
from typing import Dict, Any, List

from backend.scoring.schemas import GraphInput, ScoringResult
from backend.scoring.vasp_detector import VaspDetector
from backend.scoring.pipeline import run_scoring_pipeline

# =============================================================================
# MEMBER 1 ACTUAL FUNCTIONS (from blockchain-graph branch)
# =============================================================================
def build_transaction_graph(df: pd.DataFrame) -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph()
    if df.empty:
        return graph
    for _, row in df.iterrows():
        sender = row['sender']
        receiver = row['receiver']
        graph.add_node(sender)
        graph.add_node(receiver)
        graph.add_edge(
            sender,
            receiver,
            transaction_hash=row['transaction_hash'],
            amount=row['amount'],
            timestamp=row['timestamp'],
            sender=sender,
            receiver=receiver
        )
    return graph

def traverse_transactions(graph: nx.MultiDiGraph, source_wallet: str, max_hops: int) -> Dict[str, Any]:
    if source_wallet not in graph:
        raise ValueError(f"Source wallet '{source_wallet}' not found in the transaction graph.")
    paths: List[Dict[str, Any]] = []
    
    def dfs(current_wallet: str, current_addresses: List[str], current_transactions: List[Dict[str, Any]]) -> None:
        if len(current_transactions) > 0:
            paths.append({
                "addresses": list(current_addresses),
                "transactions": list(current_transactions),
                "hop_count": len(current_transactions),
                "original_amount": current_transactions[0]["amount"],
                "final_amount": current_transactions[-1]["amount"]
            })
        if len(current_transactions) >= max_hops:
            return
        edges = list(graph.out_edges(current_wallet, data=True))
        edges.sort(key=lambda edge: edge[2].get('transaction_hash', ''))
        for u, v, data in edges:
            if v in current_addresses:
                continue
            tx_data = {
                "from": data["sender"],
                "to": data["receiver"],
                "amount": data["amount"],
                "timestamp": data["timestamp"],
                "tx_hash": data["transaction_hash"]
            }
            current_addresses.append(v)
            current_transactions.append(tx_data)
            dfs(v, current_addresses, current_transactions)
            current_addresses.pop()
            current_transactions.pop()
            
    dfs(source_wallet, [source_wallet], [])
    return {
        "source_wallet": source_wallet,
        "paths": paths
    }
# =============================================================================

def test_integration_pipeline(tmp_path):
    """
    Verifies that Member 1's graph construction and traversal output
    can be directly fed into Member 2's scoring pipeline, and that
    the correct score/VASP destination is calculated without adapters.
    """
    # 1. Create a dummy known_vasps CSV file to inject into VaspDetector
    vasp_csv = tmp_path / "known_vasps.csv"
    vasp_csv.write_text("address,vasp_name\nVASP001,Exchange Alpha\n")
    vasp_detector = VaspDetector(str(vasp_csv))
    
    # 2. Setup Member 1 DataFrame
    df = pd.DataFrame({
        'transaction_hash': ['TX001', 'TX002'],
        'sender': ['SUSPICIOUS', 'INTERMEDIARY'],
        'receiver': ['INTERMEDIARY', 'VASP001'],
        'amount': [100.0, 95.0],
        'timestamp': ['2026-09-11T10:00:00Z', '2026-09-11T10:05:00Z']
    })
    
    # 3. Execute Member 1 Graph Construction
    graph = build_transaction_graph(df)
    
    # 4. Execute Member 1 Traversal
    traversal_result: Dict[str, Any] = traverse_transactions(graph, "SUSPICIOUS", 5)
    
    # 5. Verify Member 1 structure
    assert "source_wallet" in traversal_result
    assert "paths" in traversal_result
    assert len(traversal_result["paths"]) == 2 # 1 hop path and 2 hop path
    
    # 6. Pass directly to Member 2's GraphInput
    # This proves direct structural compatibility without adapters
    graph_input = GraphInput(**traversal_result)
    
    assert graph_input.source_wallet == "SUSPICIOUS"
    assert len(graph_input.paths) == 2
    
    # 7. Execute Member 2 Pipeline
    results = run_scoring_pipeline(graph_input, vasp_detector)
    
    # 8. Verify Pipeline Output
    assert len(results) == 1
    
    score_result: ScoringResult = results[0]
    
    assert score_result.vasp_name == "Exchange Alpha"
    assert score_result.hop_count == 2
    assert score_result.amount_retention == 0.95 # 95.0 / 100.0
    assert score_result.supporting_path_count == 1
    
    assert score_result.score == 89
    assert score_result.confidence_level == "HIGH"
