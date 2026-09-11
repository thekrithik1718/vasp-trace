from typing import List
from backend.scoring.schemas import GraphInput, ScoringResult
from backend.scoring.vasp_detector import VaspDetector
from backend.scoring.features import extract_features
from backend.scoring.scoring import calculate_score

def run_scoring_pipeline(graph_input: GraphInput, vasp_detector: VaspDetector) -> List[ScoringResult]:
    """
    Orchestrates the scoring process.
    Takes a conceptual graph input, extracts features per path,
    applies the scoring heuristic, and returns a list of results.
    """
    results = []
    
    # Pre-calculate supporting paths (how many paths lead to the same destination)
    destinations = {}
    for path in graph_input.paths:
        if path.addresses:
            dest = path.addresses[-1]
            destinations[dest] = destinations.get(dest, 0) + 1
            
    for path in graph_input.paths:
        dest = path.addresses[-1] if path.addresses else None
        supporting_paths = destinations.get(dest, 1)
        
        # 1. Extract Features
        features = extract_features(
            path=path,
            vasp_detector=vasp_detector,
            total_paths_to_destination=supporting_paths
        )
        
        # 2. Calculate Score
        result = calculate_score(features)
        results.append(result)
        
    # Rank results by score descending
    results.sort(key=lambda x: x.score, reverse=True)
    return results
