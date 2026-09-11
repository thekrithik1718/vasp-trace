import os
import sys
import re

# Ensure backend can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.graph.data_loader import load_and_validate_transactions
from backend.graph.graph_builder import build_transaction_graph
from backend.graph.traversal import traverse_transactions
from backend.scoring.schemas import GraphInput
from backend.scoring.vasp_detector import VaspDetector
from backend.scoring.pipeline import run_scoring_pipeline

def main():
    sample_data_path = os.path.join("backend", "graph", "sample_data.csv")
    known_vasps_path = os.path.join("backend", "scoring", "data", "known_vasps.csv")
    
    # 1. Load actual sample data
    df = load_and_validate_transactions(sample_data_path)
    
    # 2. Build graph using actual builder
    graph = build_transaction_graph(df)
    
    # 6. Instantiate actual VaspDetector
    vasp_detector = VaspDetector(known_vasps_path)
    
    # 3. Automatically identify a source wallet that reaches a known VASP
    valid_results = []
    best_source = None
    best_traversal = None
    graph_input = None
    
    # Find all suspicious wallets in sample data (e.g. ones that start with 'wallet_suspicious')
    # or just iterate all wallets until we hit a known VASP.
    suspicious_wallets = [node for node in graph.nodes if isinstance(node, str) and 'suspicious' in node]
    # Fallback to all nodes if none found
    wallets_to_check = suspicious_wallets if suspicious_wallets else graph.nodes
    
    for wallet in wallets_to_check:
        if graph.out_degree(wallet) == 0:
            continue
            
        # 4. Actual Member 1 traversal
        traversal_result = traverse_transactions(graph, wallet, max_hops=5)
        
        # 5. Convert to Member 2 schema
        try:
            curr_input = GraphInput(**traversal_result)
            # 7. Actual scoring pipeline
            results = run_scoring_pipeline(curr_input, vasp_detector)
            if results:
                valid_results = results
                best_source = wallet
                best_traversal = traversal_result
                graph_input = curr_input
                break
        except Exception as e:
            continue
            
    if not best_source or not valid_results:
        print("No paths found reaching a known VASP in the sample data.")
        return

    # 8. Print the COMPLETE real result
    print("============================================================")
    print("VASP TRACE — REAL END-TO-END DEMONSTRATION")
    print("==========================================")
    print()
    print(f"SOURCE WALLET: {best_source}")
    print()
    
    for i, score_res in enumerate(valid_results):
        if i > 0:
            print("\n------------------------------------------------------------\n")
            
        # Find the matching path to print details
        matching_path = None
        for p in graph_input.paths:
            if not p.addresses:
                continue
            dest = p.addresses[-1]
            # Match by destination, hop count, and retention
            if (vasp_detector.get_vasp_name(dest) == score_res.vasp_name and 
                p.hop_count == score_res.hop_count and 
                abs((p.final_amount / p.original_amount if p.original_amount > 0 else 0) - score_res.amount_retention) < 0.001):
                matching_path = p
                break
                
        if not matching_path:
            for p in graph_input.paths:
                if p.addresses and vasp_detector.get_vasp_name(p.addresses[-1]) == score_res.vasp_name:
                    matching_path = p
                    break

        if matching_path:
            print(f"GRAPH PATH: {' -> '.join(matching_path.addresses)}")
            print("\nTRANSACTIONS:")
            for idx, tx in enumerate(matching_path.transactions):
                print(f"  {idx+1}. {tx.tx_hash} | {tx.from_address} -> {tx.to_address} | amount={tx.amount}")
            print()
            
        print(f"DETECTED VASP: {score_res.vasp_name}")
        print("\nFEATURES:")
        print(f"  * VASP match: {'true' if score_res.vasp_name else 'false'}")
        print(f"  * Hop count: {score_res.hop_count}")
        if matching_path:
            print(f"  * Original amount: {matching_path.original_amount}")
            print(f"  * Final amount: {matching_path.final_amount}")
        print(f"  * Amount retention: {score_res.amount_retention * 100:.2f}%")
        print(f"  * Supporting path count: {score_res.supporting_path_count}")
        print("\nSCORING:")
        
        vasp_points = 40 if score_res.vasp_name else 0
        hop_points = 0
        ret_points = 0
        path_points = 0
        raw_score = 0
        
        for ev in score_res.evidence:
            if "Hop/proximity" in ev:
                match = re.search(r':\s*(\d+)\s*points', ev)
                if match: hop_points = int(match.group(1))
            elif "Amount retention" in ev:
                match = re.search(r':\s*(\d+)\s*points', ev)
                if match: ret_points = int(match.group(1))
            elif "Supporting paths" in ev:
                match = re.search(r':\s*(\d+)\s*points', ev)
                if match: path_points = int(match.group(1))
            elif "Raw score:" in ev:
                match = re.search(r'Raw score:\s*(\d+)/90', ev)
                if match: raw_score = int(match.group(1))
                
        print(f"  * VASP match points: {vasp_points}")
        print(f"  * Hop points: {hop_points}")
        print(f"  * Retention points: {ret_points}")
        print(f"  * Supporting path points: {path_points}")
        print(f"  * Raw score: {raw_score}/90")
        print(f"  * Final score: {score_res.score}/100")
        print(f"  * Confidence: {score_res.confidence_level}")
        
        print("\nEVIDENCE:")
        for ev in score_res.evidence:
            print(f"  * {ev}")
            
    print("\n============================================================")
    print("END-TO-END RESULT")
    print("=================")

if __name__ == "__main__":
    main()
