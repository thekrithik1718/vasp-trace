"""AI Service Interface for VASP-TRACE.

Provides the primary entry point for AI risk analysis, explainability, and pipeline integration.
Pure Python standard library implementation.
"""

from typing import Any, Dict, Optional
from .explainer import ExplainabilityEngine
from .model import RiskModel
from .schemas import AIAnalysisResult


def evaluate_risk(
    graph_data: Optional[Dict[str, Any]] = None,
    scoring_data: Optional[Dict[str, Any]] = None,
) -> AIAnalysisResult:
    """Evaluate VASP/transaction risk from graph metrics and compliance scoring flags.

    This is the primary integration entry point connecting the AI module to the
    rest of the VASP-TRACE system (graph analysis and rule-based scoring engines).

    Args:
        graph_data: Dictionary containing graph topological metrics, such as:
            - hop_count_to_illicit (int)
            - mixer_proximity (float 0.0-1.0 or bool)
            - peeling_chain_detected (bool)
            - velocity_anomaly (float 0.0-1.0 or bool)
            - rapid_fan_out (bool)
            - direct_counterparty_risk (float 0.0-1.0)
        scoring_data: Dictionary containing compliance and AML flags, such as:
            - sanction_hit / sanctions_match (bool)
            - darknet_exposure (bool)
            - ransomware_association (bool)
            - unlicensed_vasp (bool)
            - high_risk_jurisdiction (float or bool)
            - kyc_verified (bool)

    Returns:
        AIAnalysisResult containing:
            - risk_score (float, 0.0 - 100.0)
            - risk_level (RiskLevel: LOW, MEDIUM, HIGH, CRITICAL)
            - confidence_score (float, 0.0 - 1.0)
            - feature_contributions (List[FeatureContribution], ranked highest to lowest impact)
            - narrative (plain-English audit and compliance summary)
            - metadata (dictionary of evaluation details)
    """
    safe_graph_data = dict(graph_data) if isinstance(graph_data, dict) else {}
    safe_scoring_data = dict(scoring_data) if isinstance(scoring_data, dict) else {}

    # 1. Run deterministic risk model
    (
        risk_score,
        risk_level,
        confidence_score,
        raw_contributions,
        metadata,
    ) = RiskModel.evaluate(safe_graph_data, safe_scoring_data)

    # 2. Extract ranked explainability features
    ranked_contributions = ExplainabilityEngine.rank_feature_contributions(raw_contributions)

    # 3. Generate plain-English compliance narrative
    narrative = ExplainabilityEngine.generate_narrative(
        risk_score=risk_score,
        risk_level=risk_level,
        confidence_score=confidence_score,
        ranked_contributions=ranked_contributions,
        metadata=metadata,
    )

    # 4. Return consolidated audit-ready result
    return AIAnalysisResult(
        risk_score=risk_score,
        risk_level=risk_level,
        confidence_score=confidence_score,
        feature_contributions=ranked_contributions,
        narrative=narrative,
        metadata=metadata,
    )
