from typing import Dict, Any, List
from backend.scoring.schemas import ScoringResult

def calculate_score(features: Dict[str, Any]) -> ScoringResult:
    """
    Deterministic rules engine to calculate VASP score according to exact spec.
    Returns a structured ScoringResult.
    """
    vasp_name = features.get("vasp_name")
    is_vasp = features.get("is_vasp_destination", False)
    hop_count = features.get("hop_count", 0)
    amount_retention = features.get("amount_retention", 0.0)
    supporting_path_count = features.get("supporting_path_count", 1)

    evidence: List[str] = []
    
    if not is_vasp:
        evidence.append("Destination is not a known VASP.")
        return ScoringResult(
            vasp_name=None,
            destination_address=features.get("destination_address"),
            score=0,
            confidence_level="VERY_LOW",
            hop_count=hop_count,
            amount_retention=amount_retention,
            supporting_path_count=supporting_path_count,
            evidence=evidence
        )

    evidence.append("Known VASP address match: 40 points.")
    raw_score = 40
    
    # 1. Hop/proximity
    if hop_count == 1:
        h_pts = 25
    elif hop_count == 2:
        h_pts = 22
    elif hop_count == 3:
        h_pts = 19
    elif hop_count == 4:
        h_pts = 16
    elif hop_count == 5:
        h_pts = 13
    elif hop_count == 6:
        h_pts = 10
    elif hop_count == 7:
        h_pts = 7
    else:
        h_pts = 4
    
    raw_score += h_pts
    evidence.append(f"Hop/proximity ({hop_count} hops): {h_pts} points.")

    # 2. Amount retention
    if amount_retention >= 0.95:
        r_pts = 15
    elif amount_retention >= 0.85:
        r_pts = 12
    elif amount_retention >= 0.70:
        r_pts = 9
    elif amount_retention >= 0.50:
        r_pts = 5
    else:
        r_pts = 2
        
    raw_score += r_pts
    evidence.append(f"Amount retention ({amount_retention * 100:.1f}%): {r_pts} points.")

    # 3. Supporting paths
    if supporting_path_count == 1:
        p_pts = 3
    elif supporting_path_count == 2:
        p_pts = 6
    elif supporting_path_count == 3:
        p_pts = 8
    else:
        p_pts = 10
        
    raw_score += p_pts
    evidence.append(f"Supporting paths ({supporting_path_count} paths): {p_pts} points.")

    # Final score
    final_score = round((raw_score / 90) * 100)
    
    # Confidence calculation
    if final_score >= 90:
        confidence_level = "VERY_HIGH"
    elif final_score >= 75:
        confidence_level = "HIGH"
    elif final_score >= 50:
        confidence_level = "MEDIUM"
    elif final_score >= 25:
        confidence_level = "LOW"
    else:
        confidence_level = "VERY_LOW"
        
    evidence.append(f"Raw score: {raw_score}/90. Final score: {final_score}/100 with {confidence_level} confidence.")

    return ScoringResult(
        vasp_name=vasp_name,
        destination_address=features.get("destination_address"),
        score=final_score,
        confidence_level=confidence_level,
        hop_count=hop_count,
        amount_retention=amount_retention,
        supporting_path_count=supporting_path_count,
        evidence=evidence
    )
