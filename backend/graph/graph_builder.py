import networkx as nx
import pandas as pd

def build_transaction_graph(df: pd.DataFrame) -> nx.MultiDiGraph:
    """Build a directed graph from a DataFrame of transactions.

    Nodes represent wallet addresses. Edges represent transactions from
    sender to receiver. Multiple transactions between the same sender and
    receiver are preserved as separate edges (using MultiDiGraph).

    Args:
        df: A validated pandas DataFrame containing transaction records.
            Expected columns include:
            'transaction_hash', 'sender', 'receiver', 'amount', 'timestamp'.

    Returns:
        A networkx.MultiDiGraph containing the transaction network.
        Nodes are wallet addresses. Edges contain attributes matching the
        input DataFrame row.
    """
    graph = nx.MultiDiGraph()

    if df.empty:
        return graph

    # Do not mutate the caller's DataFrame unnecessarily
    # We iterate over the records
    for _, row in df.iterrows():
        sender = row['sender']
        receiver = row['receiver']
        
        # Add nodes if they don't exist (NetworkX does this implicitly when adding edges,
        # but adding them explicitly can be clearer, though not strictly required)
        graph.add_node(sender)
        graph.add_node(receiver)

        # Add directed edge from sender to receiver
        # Each edge is unique in a MultiDiGraph even for the same sender and receiver
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
