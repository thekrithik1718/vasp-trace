"""Deterministic Risk Evaluation Model for VASP-TRACE.

Implements transparent, auditable weighted rules combining graph topological
metrics and regulatory compliance scoring flags.
Pure Python standard library implementation.
"""

import math
from typing import Any, Dict, List, Optional, Tuple
from .schemas import RiskLevel


# Core weight definitions for scoring flags
SCORING_FLAG_RULES: Dict[str, Dict[str, Any]] = {
    "sanction_hit": {
        "weight": 65.0,
        "label": "Sanctions List Match",
        "description": "Counterparty or wallet identified on international sanctions lists (OFAC/UN/EU).",
        "critical_escalation": True,
    },
    "sanctions_match": {
        "weight": 65.0,
        "label": "Sanctions List Match",
        "description": "Counterparty or wallet identified on international sanctions lists (OFAC/UN/EU).",
        "critical_escalation": True,
    },
    "darknet_exposure": {
        "weight": 35.0,
        "label": "Darknet Market Exposure",
        "description": "Direct or indirect interaction with known darknet illicit marketplaces.",
    },
    "darknet_interaction": {
        "weight": 35.0,
        "label": "Darknet Market Exposure",
        "description": "Direct or indirect interaction with known darknet illicit marketplaces.",
    },
    "ransomware_association": {
        "weight": 35.0,
        "label": "Ransomware Association",
        "description": "Funds traced to addresses linked with known ransomware extortion campaigns.",
    },
    "unlicensed_vasp": {
        "weight": 25.0,
        "label": "Unregistered / Unlicensed VASP",
        "description": "Operating without verified regulatory registration or FATF Travel Rule compliance.",
    },
    "high_risk_jurisdiction": {
        "weight": 20.0,
        "label": "High-Risk Jurisdiction",
        "description": "Entity operates in or routes funds through a FATF-designated high-risk jurisdiction.",
    },
    "structuring_detected": {
        "weight": 18.0,
        "label": "Transaction Structuring (Smurfing)",
        "description": "Repetitive transactions just beneath statutory threshold reporting limits.",
    },
    "layering_pattern": {
        "weight": 22.0,
        "label": "Layering Pattern",
        "description": "Complex chain of rapid cross-entity transfers indicative of laundering layering phase.",
    },
    "pep_involvement": {
        "weight": 15.0,
        "label": "Politically Exposed Person (PEP)",
        "description": "Beneficiary or originator classified as PEP, requiring enhanced due diligence.",
    },
    "kyc_verified": {
        "weight": -15.0,
        "label": "Verified KYC & Regulated VASP",
        "description": "Counterparty completed full Tier-3 KYC and operates under compliant supervision.",
    },
}

# Core weight definitions for graph metrics
GRAPH_METRIC_RULES: Dict[str, Dict[str, Any]] = {
    "mixer_proximity": {
        "max_weight": 30.0,
        "label": "Coin Mixer Proximity",
        "description": "Proximity to privacy pools, mixers, or coin join contracts.",
    },
    "mixer_used": {
        "max_weight": 30.0,
        "label": "Mixer Usage Detected",
        "description": "Direct deposit or withdrawal detected with cryptocurrency mixing service.",
    },
    "peeling_chain_detected": {
        "max_weight": 20.0,
        "label": "Peeling Chain Pattern",
        "description": "Repeated peeling chain structure where change outputs are systematically stripped.",
    },
    "velocity_anomaly": {
        "max_weight": 18.0,
        "label": "Abnormal Transaction Velocity",
        "description": "Turnover rate exceeds baseline activity standard deviations significantly.",
    },
    "rapid_fan_out": {
        "max_weight": 15.0,
        "label": "Rapid Fan-Out Dispersion",
        "description": "Single-origin funds quickly distributed to dozens of disparate unlinked addresses.",
    },
    "rapid_fan_in": {
        "max_weight": 15.0,
        "label": "Consolidation Fan-In Pattern",
        "description": "Multiple independent wallets rapidly consolidating funds into a single endpoint.",
    },
    "direct_counterparty_risk": {
        "max_weight": 20.0,
        "label": "Counterparty Exposure Risk",
        "description": "Average composite risk rating of immediate graph counterparty nodes.",
    },
}


class RiskModel:
    """Evaluates raw graph topological metrics and scoring flags using deterministic weighted rules."""

    @staticmethod
    def _parse_float(value: Any) -> Optional[float]:
        """Safely parse a numeric float, rejecting booleans, nan, inf, and invalid types."""
        if isinstance(value, bool):
            return None
        try:
            val = float(value)
            if math.isnan(val) or math.isinf(val):
                return None
            return val
        except (ValueError, TypeError):
            return None

    @classmethod
    def _evaluate_hop_count(cls, hop_count: Any) -> Tuple[float, str]:
        """Compute score contribution for proximity hops to known illicit nodes."""
        if isinstance(hop_count, bool):
            return 0.0, "Invalid hop count."
        try:
            hops = int(hop_count)
        except (ValueError, TypeError):
            return 0.0, "Invalid hop count."

        if hops <= 0:
            return 0.0, "No illicit connection detected within graph search depth."
        elif hops == 1:
            return 28.0, "Direct (1-hop) immediate counterparty connection to confirmed illicit node."
        elif hops == 2:
            return 18.0, "Close (2-hop) intermediary connection to confirmed illicit node."
        elif hops == 3:
            return 10.0, "3-hop association to illicit entity in transaction graph."
        elif hops <= 5:
            return 4.0, f"Distant ({hops}-hop) transaction graph association."
        else:
            return 1.0, f"De minimis association ({hops} hops away)."

    @classmethod
    def evaluate(
        cls, graph_data: Dict[str, Any], scoring_data: Dict[str, Any]
    ) -> Tuple[float, RiskLevel, float, List[Dict[str, Any]], Dict[str, Any]]:
        """Run transparent rule-based risk evaluation.

        Args:
            graph_data: Graph metrics dictionary (hops, mixer proximity, clustering, etc.).
            scoring_data: Scoring and compliance flags dictionary.

        Returns:
            Tuple of:
                - risk_score: Clamped float between 0.0 and 100.0.
                - risk_level: RiskLevel enum.
                - confidence_score: Assessment confidence between 0.0 and 1.0.
                - raw_contributions: List of raw evaluated feature contributions.
                - metadata: Summary evaluation metadata.
        """
        raw_contributions: List[Dict[str, Any]] = []
        total_score: float = 0.0
        signals_evaluated: int = 0
        has_critical_escalation: bool = False

        # 1. Process scoring flags
        for key, value in scoring_data.items():
            rule = SCORING_FLAG_RULES.get(key)
            if rule:
                signals_evaluated += 1
                weight = rule["weight"]
                if isinstance(value, bool):
                    if value:
                        contribution = weight
                        if rule.get("critical_escalation"):
                            has_critical_escalation = True
                        explanation = f"{rule['label']} active: {rule['description']}"
                        raw_contributions.append({
                            "feature_name": key,
                            "feature_value": value,
                            "contribution": round(contribution, 2),
                            "explanation": explanation,
                        })
                        total_score += contribution
                else:
                    parsed = cls._parse_float(value)
                    if parsed is not None:
                        # Numeric flag (e.g. tier 1-3 or probability 0.0-1.0)
                        normalized_factor = min(max(parsed, 0.0), 1.0)
                        contribution = weight * normalized_factor
                        if contribution != 0.0:
                            raw_contributions.append({
                                "feature_name": key,
                                "feature_value": value,
                                "contribution": round(contribution, 2),
                                "explanation": f"{rule['label']} rated at {value}: {rule['description']}",
                            })
                            total_score += contribution
            else:
                # Custom or untracked scoring flag handling
                if isinstance(value, bool) and value:
                    signals_evaluated += 1
                    contribution = 10.0
                    total_score += contribution
                    raw_contributions.append({
                        "feature_name": key,
                        "feature_value": value,
                        "contribution": contribution,
                        "explanation": f"Custom compliance flag '{key}' is active.",
                    })
                else:
                    parsed = cls._parse_float(value)
                    if parsed is not None and parsed > 0:
                        signals_evaluated += 1

        # 2. Process graph metrics
        # Check hop count first
        hop_keys = ["hop_count_to_illicit", "hop_count", "hops_to_sanctioned"]
        for hop_key in hop_keys:
            if hop_key in graph_data:
                signals_evaluated += 1
                val = graph_data[hop_key]
                contrib, expl = cls._evaluate_hop_count(val)
                if contrib > 0:
                    raw_contributions.append({
                        "feature_name": hop_key,
                        "feature_value": val,
                        "contribution": round(contrib, 2),
                        "explanation": expl,
                    })
                    total_score += contrib
                break

        # Process other graph metrics
        for key, value in graph_data.items():
            if key in hop_keys:
                continue

            rule = GRAPH_METRIC_RULES.get(key)
            if rule:
                signals_evaluated += 1
                max_w = rule["max_weight"]
                if isinstance(value, bool):
                    if value:
                        contribution = max_w
                        raw_contributions.append({
                            "feature_name": key,
                            "feature_value": value,
                            "contribution": round(contribution, 2),
                            "explanation": f"{rule['label']} detected: {rule['description']}",
                        })
                        total_score += contribution
                else:
                    parsed = cls._parse_float(value)
                    if parsed is not None:
                        # Ratio / continuous metric (0.0 to 1.0 expected, clamp gracefully)
                        norm = min(max(parsed, 0.0), 1.0)
                        contribution = max_w * norm
                        if contribution > 0.0:
                            raw_contributions.append({
                                "feature_name": key,
                                "feature_value": value,
                                "contribution": round(contribution, 2),
                                "explanation": f"{rule['label']} intensity at {value}: {rule['description']}",
                            })
                            total_score += contribution
            else:
                # Custom or generic numeric/bool graph metric
                if isinstance(value, bool) and value:
                    signals_evaluated += 1
                    contrib = 8.0
                    total_score += contrib
                    raw_contributions.append({
                        "feature_name": key,
                        "feature_value": value,
                        "contribution": contrib,
                        "explanation": f"Graph metric '{key}' indicates active pattern.",
                    })
                else:
                    parsed = cls._parse_float(value)
                    if parsed is not None and parsed > 0:
                        signals_evaluated += 1

        # 3. Apply critical escalation override if confirmed sanctions match
        if has_critical_escalation and total_score < 85.0:
            total_score = 85.0

        # Clamp final score between 0.0 and 100.0
        final_risk_score = min(max(round(total_score, 2), 0.0), 100.0)

        # 4. Map to RiskLevel
        if final_risk_score < 25.0:
            risk_level = RiskLevel.LOW
        elif final_risk_score < 50.0:
            risk_level = RiskLevel.MEDIUM
        elif final_risk_score < 75.0:
            risk_level = RiskLevel.HIGH
        else:
            risk_level = RiskLevel.CRITICAL

        # 5. Compute assessment confidence score
        # Base confidence begins at 0.60; each evaluated signal adds confidence up to 0.95
        total_inputs_count = len(graph_data) + len(scoring_data)
        if total_inputs_count == 0:
            confidence = 0.50
        else:
            confidence = min(0.60 + (signals_evaluated * 0.05), 0.95)
            # High agreement with critical flags boosts confidence
            if has_critical_escalation:
                confidence = max(confidence, 0.92)
        confidence = round(confidence, 2)

        metadata = {
            "signals_evaluated": signals_evaluated,
            "total_raw_inputs": total_inputs_count,
            "critical_escalation_applied": has_critical_escalation,
        }

        return final_risk_score, risk_level, confidence, raw_contributions, metadata
