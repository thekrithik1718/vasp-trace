"""Schemas and data models for VASP-TRACE AI analysis.

Pure Python standard library implementation using dataclasses and type hints.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional


class RiskLevel(str, Enum):
    """Standard risk tiers for Virtual Asset Service Provider compliance."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class FeatureContribution:
    """Individual feature contribution to the overall risk evaluation.
222
    Attributes:
        feature_name: Identifiable name of the evaluated metric or flag.
        feature_value: Observed value in the input data.
        contribution: Signed numerical contribution to the risk score.
        explanation: Human-interpretable rationale for this contribution.
    """
    feature_name: str
    feature_value: Any
    contribution: float
    explanation: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert contribution to dictionary representation."""
        return asdict(self)


@dataclass
class AIAnalysisResult:
    """Consolidated AI and explainability evaluation result.

    Attributes:
        risk_score: Normalized risk score from 0.0 (safest) to 100.0 (maximum risk).
        risk_level: Categorical risk tier (LOW, MEDIUM, HIGH, CRITICAL).
        confidence_score: Assessment confidence level between 0.0 and 1.0.
        feature_contributions: Ranked feature contributions (highest impact first).
        narrative: Plain-English audit-ready compliance narrative.
        metadata: Supplementary contextual data (evaluated timestamp, feature counts, etc.).
    """
    risk_score: float
    risk_level: RiskLevel
    confidence_score: float
    feature_contributions: List[FeatureContribution] = field(default_factory=list)
    narrative: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert analysis result to dictionary representation."""
        data = asdict(self)
        # Ensure enum is serialized as string value
        data["risk_level"] = self.risk_level.value
        return data
