from typing import Dict, Any
from backend.scoring.schemas import TransactionPath
from backend.scoring.vasp_detector import VaspDetector

def extract_features(path: TransactionPath, vasp_detector: VaspDetector, total_paths_to_destination: int) -> Dict[str, Any]:
    """
    Extracts measurable features from a transaction path for scoring.
    Assumes Member 1 has populated the path with hop_count, original_amount, final_amount, etc.
    """
    final_address = path.addresses[-1] if path.addresses else None
    
    # 1. VASP Match
    vasp_name = None
    if final_address:
        vasp_name = vasp_detector.get_vasp_name(final_address)
        
    is_vasp_destination = vasp_name is not None
    
    # 2. Amount Retention
    retention_ratio = 0.0
    if path.original_amount > 0:
        retention_ratio = path.final_amount / path.original_amount
        
    # 3. Hop count (consumed directly from the path)
    hop_count = path.hop_count
    
    # 4. Supporting Path Count (paths found from source to this specific destination)
    supporting_path_count = total_paths_to_destination

    return {
        "vasp_name": vasp_name,
        "is_vasp_destination": is_vasp_destination,
        "hop_count": hop_count,
        "amount_retention": retention_ratio,
        "supporting_path_count": supporting_path_count
    }
