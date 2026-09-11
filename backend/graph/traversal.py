"""Graph traversal algorithms for tracing paths to VASPs."""

from typing import Dict, List, Any
import networkx as nx

def traverse_transactions(graph: nx.MultiDiGraph, source_wallet: str, max_hops: int) -> Dict[str, Any]:
    """
    Traverse the transaction graph from a source wallet up to max_hops.
    
    Returns all valid paths originating from the source wallet. A path is a 
    sequence of transactions.
    
    Args:
        graph: networkx.MultiDiGraph containing the transactions.
        source_wallet: The starting wallet address.
        max_hops: Maximum number of transaction hops to traverse.
        
    Returns:
        A dictionary containing the source wallet and a list of paths.
        
    Raises:
        ValueError: If the source_wallet does not exist in the graph.
    """
    if source_wallet not in graph:
        raise ValueError(f"Source wallet '{source_wallet}' not found in the transaction graph.")
        
    paths: List[Dict[str, Any]] = []
    
    def dfs(current_wallet: str, current_addresses: List[str], current_transactions: List[Dict[str, Any]]) -> None:
        # Save path if it has at least one hop
        if len(current_transactions) > 0:
            paths.append({
                "addresses": list(current_addresses),
                "transactions": list(current_transactions),
                "hop_count": len(current_transactions),
                "original_amount": current_transactions[0]["amount"],
                "final_amount": current_transactions[-1]["amount"]
            })
            
        # Stop traversing if we reach the maximum number of hops
        if len(current_transactions) >= max_hops:
            return
            
        # Fetch outgoing edges, yielding (u, v, data)
        edges = list(graph.out_edges(current_wallet, data=True))
        
        # Sort edges deterministically by transaction_hash to ensure reproducible results
        edges.sort(key=lambda edge: edge[2].get('transaction_hash', ''))
        
        for u, v, data in edges:
            # Cycle protection: do not revisit a wallet already in the current path
            if v in current_addresses:
                continue
                
            tx_data = {
                "from": data["sender"],
                "to": data["receiver"],
                "amount": data["amount"],
                "timestamp": data["timestamp"],
                "tx_hash": data["transaction_hash"]
            }
            
            # Recurse
            current_addresses.append(v)
            current_transactions.append(tx_data)
            
            dfs(v, current_addresses, current_transactions)
            
            # Backtrack
            current_addresses.pop()
            current_transactions.pop()
            
    dfs(source_wallet, [source_wallet], [])
    
    return {
        "source_wallet": source_wallet,
        "paths": paths
    }
