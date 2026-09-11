"""Tests for graph builder module."""

import os
import pandas as pd
import pytest
import networkx as nx

from backend.graph.graph_builder import build_transaction_graph
from backend.graph.data_loader import load_and_validate_transactions

SAMPLE_DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "sample_data.csv")
)

def test_empty_dataframe():
    """A. Verify building a graph from an empty valid DataFrame returns an empty MultiDiGraph."""
    df = pd.DataFrame(columns=['transaction_hash', 'sender', 'receiver', 'amount', 'timestamp'])
    graph = build_transaction_graph(df)
    assert isinstance(graph, nx.MultiDiGraph)
    assert graph.number_of_nodes() == 0
    assert graph.number_of_edges() == 0

def test_nodes_exist():
    """B. Verify sender and receiver wallets become graph nodes."""
    df = pd.DataFrame({
        'transaction_hash': ['tx1'],
        'sender': ['wallet_A'],
        'receiver': ['wallet_B'],
        'amount': [100.0],
        'timestamp': ['2026-01-01T00:00:00Z']
    })
    graph = build_transaction_graph(df)
    assert 'wallet_A' in graph.nodes
    assert 'wallet_B' in graph.nodes
    assert graph.number_of_nodes() == 2

def test_edges_exist():
    """C. Verify every transaction becomes an edge."""
    df = pd.DataFrame({
        'transaction_hash': ['tx1', 'tx2'],
        'sender': ['A', 'C'],
        'receiver': ['B', 'D'],
        'amount': [10.0, 20.0],
        'timestamp': ['T1', 'T2']
    })
    graph = build_transaction_graph(df)
    assert graph.number_of_edges() == 2
    assert graph.has_edge('A', 'B')
    assert graph.has_edge('C', 'D')

def test_edge_attributes():
    """D. Verify transaction_hash, amount, timestamp, sender, receiver are preserved correctly."""
    df = pd.DataFrame({
        'transaction_hash': ['tx_xyz'],
        'sender': ['Alice'],
        'receiver': ['Bob'],
        'amount': [500.5],
        'timestamp': ['2026-12-31T23:59:59Z']
    })
    graph = build_transaction_graph(df)
    
    # In a MultiDiGraph, edges are keyed by an index (0, 1, etc.)
    edge_data = graph.get_edge_data('Alice', 'Bob')
    assert edge_data is not None
    assert len(edge_data) == 1
    
    attr = edge_data[0]
    assert attr['transaction_hash'] == 'tx_xyz'
    assert attr['amount'] == 500.5
    assert attr['timestamp'] == '2026-12-31T23:59:59Z'
    assert attr['sender'] == 'Alice'
    assert attr['receiver'] == 'Bob'

def test_multiple_transactions():
    """E. Given multiple transactions between same nodes, verify all exist as separate edges."""
    df = pd.DataFrame({
        'transaction_hash': ['tx1', 'tx2', 'tx3'],
        'sender': ['A', 'A', 'A'],
        'receiver': ['B', 'B', 'B'],
        'amount': [500, 800, 1200],
        'timestamp': ['T1', 'T2', 'T3']
    })
    graph = build_transaction_graph(df)
    
    assert graph.number_of_edges() == 3
    # Check that there are exactly 3 edges between A and B
    edge_data = graph.get_edge_data('A', 'B')
    assert len(edge_data) == 3
    
    amounts = sorted([data['amount'] for data in edge_data.values()])
    assert amounts == [500, 800, 1200]

def test_directed_behavior():
    """F. A -> B must not automatically create B -> A."""
    df = pd.DataFrame({
        'transaction_hash': ['tx1'],
        'sender': ['A'],
        'receiver': ['B'],
        'amount': [100.0],
        'timestamp': ['T1']
    })
    graph = build_transaction_graph(df)
    assert graph.has_edge('A', 'B')
    assert not graph.has_edge('B', 'A')

def test_transaction_identity():
    """G. Verify transaction hashes are preserved and can distinguish parallel transactions."""
    df = pd.DataFrame({
        'transaction_hash': ['hash_alpha', 'hash_beta'],
        'sender': ['Wallet1', 'Wallet1'],
        'receiver': ['Wallet2', 'Wallet2'],
        'amount': [10.0, 10.0],
        'timestamp': ['T1', 'T1'] # same amount and timestamp
    })
    graph = build_transaction_graph(df)
    
    edge_data = graph.get_edge_data('Wallet1', 'Wallet2')
    assert len(edge_data) == 2
    
    hashes = set(data['transaction_hash'] for data in edge_data.values())
    assert hashes == {'hash_alpha', 'hash_beta'}

def test_sample_dataset():
    """H. Load the existing 27-transaction sample dataset and verify the graph."""
    df = load_and_validate_transactions(SAMPLE_DATA_PATH)
    # The sample dataset contains 27 transactions according to the user
    # However we just verify it matches the length of the dataframe
    expected_edges = len(df)
    
    graph = build_transaction_graph(df)
    
    assert isinstance(graph, nx.MultiDiGraph)
    assert graph.number_of_edges() == expected_edges
    
    # Check that every unique wallet is a node
    expected_nodes = set(df['sender']).union(set(df['receiver']))
    assert set(graph.nodes) == expected_nodes
