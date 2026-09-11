"""Explainability and Narrative Generation Module for VASP-TRACE.

Produces ranked feature attributions and audit-ready plain-English compliance narratives.
Pure Python standard library implementation.
"""

from typing import Any, Dict, List
from .schemas import FeatureContribution, RiskLevel


class ExplainabilityEngine:
    """Transforms model outputs into human-interpretable feature attributions and compliance narratives."""

    @staticmethod
    def rank_feature_contributions(raw_contributions: List[Dict[str, Any]]) -> List[FeatureContribution]:
        """Convert raw feature contributions into ranked FeatureContribution objects.

        Sorts features by absolute contribution in descending order (highest impact first).

        Args:
            raw_contributions: Raw dictionary entries with feature_name, feature_value, contribution, explanation.

        Returns:
            List of sorted FeatureContribution instances.
        """
        contributions = [
            FeatureContribution(
                feature_name=item["feature_name"],
                feature_value=item["feature_value"],
                contribution=float(item["contribution"]),
                explanation=item["explanation"],
            )
            for item in raw_contributions
        ]

        # Rank by absolute impact descending
        contributions.sort(key=lambda x: abs(x.contribution), reverse=True)
        return contributions

    @classmethod
    def generate_narrative(
        cls,
        risk_score: float,
        risk_level: RiskLevel,
        confidence_score: float,
        ranked_contributions: List[FeatureContribution],
        metadata: Dict[str, Any],
    ) -> str:
        """Generate a structured, plain-English compliance narrative for audit trails and AML analysts.

        Args:
            risk_score: Normalized risk score (0.0 to 100.0).
            risk_level: Risk tier (LOW, MEDIUM, HIGH, CRITICAL).
            confidence_score: Assessment confidence (0.0 to 1.0).
            ranked_contributions: Ranked feature contributions.
            metadata: Evaluation metadata.

        Returns:
            Formatted plain-English compliance narrative.
        """
        confidence_pct = int(confidence_score * 100)
        lines: List[str] = []

        # 1. Executive Summary
        lines.append(
            f"EXECUTIVE SUMMARY: Entity evaluated at {risk_level.value} risk with a score of "
            f"{risk_score:.1f}/100.0 (model confidence: {confidence_pct}%)."
        )

        # 2. Key Findings & Drivers
        positive_drivers = [c for c in ranked_contributions if c.contribution > 0]
        mitigating_factors = [c for c in ranked_contributions if c.contribution < 0]

        if positive_drivers:
            lines.append("\nPRIMARY RISK DRIVERS:")
            for idx, driver in enumerate(positive_drivers[:4], start=1):
                sign = "+" if driver.contribution >= 0 else ""
                lines.append(
                    f"  {idx}. [{driver.feature_name}] ({sign}{driver.contribution:.1f} pts) - {driver.explanation}"
                )
        else:
            lines.append("\nPRIMARY RISK DRIVERS: No active high-risk indicators or anomalies identified.")

        if mitigating_factors:
            lines.append("\nMITIGATING FACTORS:")
            for idx, mit in enumerate(mitigating_factors, start=1):
                lines.append(
                    f"  {idx}. [{mit.feature_name}] ({mit.contribution:.1f} pts) - {mit.explanation}"
                )

        # 3. Regulatory / Operational Recommendation
        lines.append("\nRECOMMENDED COMPLIANCE ACTION:")
        if risk_level == RiskLevel.CRITICAL:
            lines.append(
                "  [CRITICAL ESCALATION] Immediate transaction block recommended. Initiate formal "
                "Suspicious Activity Report (SAR/STR) filing and freeze associated transfers in "
                "accordance with FATF Travel Rule sanctions protocols."
            )
        elif risk_level == RiskLevel.HIGH:
            lines.append(
                "  [ENHANCED DUE DILIGENCE] Place on heightened watchlist. Request verifiable KYC and "
                "source-of-funds documentation from counterparty VASP prior to fund release."
            )
        elif risk_level == RiskLevel.MEDIUM:
            lines.append(
                "  [STANDARD DUE DILIGENCE] Transaction permitted under routine monitoring. Log audit "
                "entry and track for subsequent velocity spikes or high-risk hops."
            )
        else:
            lines.append(
                "  [LOW RISK - CLEAR] No adverse compliance findings. Proceed with standard automated "
                "processing."
            )

        return "\n".join(lines)
