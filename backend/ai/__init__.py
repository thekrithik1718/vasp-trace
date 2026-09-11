"""VASP-TRACE AI Package.

Provides AI risk scoring, explainability (XAI), and integration interfaces.
"""

from .schemas import (
    AIAnalysisResult,
    FeatureContribution,
    RiskLevel,
)
from .service import evaluate_risk

__all__ = [
    "evaluate_risk",
    "AIAnalysisResult",
    "RiskLevel",
    "FeatureContribution",
]
