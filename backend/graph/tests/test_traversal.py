"""Tests for graph traversal module."""

import os
import networkx as nx
import pandas as pd
import pytest

from backend.graph.graph_builder import build_transaction_graph
from backend.graph.traversal import traverse_transactions
from backend.graph.data_loader import load_and_validate_transactions

SAMPLE_DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "sample_data.csv")
)

@pytest.fixture
def simple_graph() -> nx.MultiDiGraph:
    """Fixture providing a simple manual graph for testing."""
    df = pd.DataFrame({
        'transaction_hash': ['tx1', 'tx2', 'tx3', 'tx4', 'tx5'],
        'sender': ['A', 'B', 'C', 'D', 'E'],
        'receiver': ['B', 'C', 'D', 'E', 'F'],
        'amount': [100.0, 90.0, 80.0, 70.0, 60.0],
        'timestamp': ['T1', 'T2', 'T3', 'T4', 'T5']
    })
    return build_transaction_graph(df)

@pytest.fixture
def parallel_graph() -> nx.MultiDiGraph:
    """Fixture providing a graph with parallel edges."""
    df = pd.DataFrame({
        'transaction_hash': ['tx_a', 'tx_b', 'tx_c'],
        'sender': ['A', 'A', 'A'],
        'receiver': ['B', 'B', 'B'],
        'amount': [10.0, 20.0, 30.0],
        'timestamp': ['T1', 'T2', 'T3']
    })
    return build_transaction_graph(df)

@pytest.fixture
def cycle_graph() -> nx.MultiDiGraph:
    """Fixture providing a graph with a cycle A->B->C->A."""
    df = pd.DataFrame({
        'transaction_hash': ['tx1', 'tx2', 'tx3'],
        'sender': ['A', 'B', 'C'],
        'receiver': ['B', 'C', 'A'],
        'amount': [100.0, 90.0, 80.0],
        'timestamp': ['T1', 'T2', 'T3']
    })
    return build_transaction_graph(df)


def test_missing_source_wallet(simple_graph):
    """A. Missing source wallet raises ValueError."""
    with pytest.raises(ValueError, match="not found in the transaction graph"):
        traverse_transactions(simple_graph, "UNKNOWN_WALLET", 5)

def test_source_no_outgoing(simple_graph):
    """B. Source with no outgoing transactions returns zero paths."""
    # F has no outgoing transactions in simple_graph
    result = traverse_transactions(simple_graph, "F", 5)
    assert result["source_wallet"] == "F"
    assert result["paths"] == []

def test_one_hop_traversal():
    """C. One-hop traversal."""
    df = pd.DataFrame({
        'transaction_hash': ['tx1'],
        'sender': ['A'],
        'receiver': ['B'],
        'amount': [100.0],
        'timestamp': ['T1']
    })
    graph = build_transaction_graph(df)
    result = traverse_transactions(graph, "A", 1)
    
    paths = result["paths"]
    assert len(paths) == 1
    assert paths[0]["hop_count"] == 1
    assert paths[0]["addresses"] == ["A", "B"]

def test_multi_hop_traversal(simple_graph):
    """D. Multi-hop traversal (e.g. hop_count = 3)."""
    # A -> B -> C -> D is 3 hops
    result = traverse_transactions(simple_graph, "A", 3)
    
    # Paths should be A->B, A->B->C, A->B->C->D
    paths = result["paths"]
    assert len(paths) == 3
    
    # Find the 3-hop path
    three_hop_paths = [p for p in paths if p["hop_count"] == 3]
    assert len(three_hop_paths) == 1
    path = three_hop_paths[0]
    
    assert path["addresses"] == ["A", "B", "C", "D"]
    assert len(path["transactions"]) == 3

def test_max_hop_boundary(simple_graph):
    """E. Maximum hop boundary."""
    # Graph is A->B->C->D->E->F (5 hops max)
    # If max_hops=3, path max length should be 3
    result = traverse_transactions(simple_graph, "A", 3)
    
    paths = result["paths"]
    hop_counts = [p["hop_count"] for p in paths]
    assert max(hop_counts) == 3
    # Paths with 4 or 5 hops should not be included
    assert all(h <= 3 for h in hop_counts)

def test_cycle_protection(cycle_graph):
    """F. Cycle protection."""
    # Cycle A->B->C->A
    result = traverse_transactions(cycle_graph, "A", 10)
    
    paths = result["paths"]
    # Path A->B, A->B->C
    # When at C, the outgoing edge is C->A. A is already in the path, so it shouldn't be added.
    # Therefore, no infinite loop, and maximum path addresses is 3 (A, B, C).
    assert len(paths) == 2
    
    for path in paths:
        assert len(path["addresses"]) == len(set(path["addresses"])) # All unique addresses in each path

def test_parallel_transactions(parallel_graph):
    """G. Parallel transactions."""
    result = traverse_transactions(parallel_graph, "A", 5)
    
    paths = result["paths"]
    assert len(paths) == 3 # Should yield 3 distinct 1-hop paths
    
    tx_hashes = set(path["transactions"][0]["tx_hash"] for path in paths)
    assert tx_hashes == {'tx_a', 'tx_b', 'tx_c'}

def test_transaction_metadata_preservation():
    """H. Transaction metadata preservation."""
    df = pd.DataFrame({
        'transaction_hash': ['tx_meta'],
        'sender': ['Sender1'],
        'receiver': ['Receiver1'],
        'amount': [123.45],
        'timestamp': ['2026-09-11T12:00:00Z']
    })
    graph = build_transaction_graph(df)
    result = traverse_transactions(graph, "Sender1", 1)
    
    tx = result["paths"][0]["transactions"][0]
    assert tx["from"] == "Sender1"
    assert tx["to"] == "Receiver1"
    assert tx["amount"] == 123.45
    assert tx["timestamp"] == "2026-09-11T12:00:00Z"
    assert tx["tx_hash"] == "tx_meta"

def test_amount_fields(simple_graph):
    """I. Amount fields (original_amount, final_amount)."""
    result = traverse_transactions(simple_graph, "A", 3)
    
    # Path A->B->C->D
    path = [p for p in result["paths"] if p["hop_count"] == 3][0]
    
    # A->B amount is 100.0, C->D amount is 80.0
    assert path["original_amount"] == 100.0
    assert path["final_amount"] == 80.0

def test_hop_count_correctness(simple_graph):
    """J. Hop count correctness."""
    result = traverse_transactions(simple_graph, "A", 5)
    
    for path in result["paths"]:
        assert path["hop_count"] == len(path["transactions"])

def test_directed_traversal():
    """K. Directed traversal (A->B doesn't imply B->A)."""
    df = pd.DataFrame({
        'transaction_hash': ['tx1'],
        'sender': ['A'],
        'receiver': ['B'],
        'amount': [100.0],
        'timestamp': ['T1']
    })
    graph = build_transaction_graph(df)
    
    # Traverse from B should yield 0 paths
    result = traverse_transactions(graph, "B", 5)
    assert len(result["paths"]) == 0

def test_deterministic_ordering():
    """L. Deterministic ordering."""
    df = pd.DataFrame({
        'transaction_hash': ['tx2', 'tx1', 'tx3'],
        'sender': ['A', 'A', 'A'],
        'receiver': ['B', 'C', 'D'],
        'amount': [10.0, 20.0, 30.0],
        'timestamp': ['T1', 'T2', 'T3']
    })
    graph = build_transaction_graph(df)
    
    # Traverse from A, should be sorted by tx_hash: tx1, tx2, tx3
    result1 = traverse_transactions(graph, "A", 1)
    result2 = traverse_transactions(graph, "A", 1)
    
    # Ensure they match
    assert result1 == result2
    
    # Ensure order is sorted by tx_hash
    tx_hashes = [p["transactions"][0]["tx_hash"] for p in result1["paths"]]
    assert tx_hashes == ['tx1', 'tx2', 'tx3']

def test_sample_dataset():
    """M. Sample dataset traversal."""
    df = load_and_validate_transactions(SAMPLE_DATA_PATH)
    graph = build_transaction_graph(df)
    
    # Pick a wallet that acts as a sender in the sample dataset
    source_wallet = df.iloc[0]['sender']
    
    result = traverse_transactions(graph, source_wallet, max_hops=3)
    
    assert result["source_wallet"] == source_wallet
    assert isinstance(result["paths"], list)
    
    if len(result["paths"]) > 0:
        path = result["paths"][0]
        assert "addresses" in path
        assert "transactions" in path
        assert "hop_count" in path
        assert "original_amount" in path
        assert "final_amount" in path
        
        tx = path["transactions"][0]
        assert "from" in tx
        assert "to" in tx
        assert "amount" in tx
        assert "timestamp" in tx
        assert "tx_hash" in tx
