"""Automated unit tests for VASP-TRACE AI module.

Tests deterministic scoring, explainability, schema serialization,
and input fault-tolerance using Python's built-in unittest framework only.
"""

import json
import threading
import unittest
import urllib.error
import urllib.request

from backend.ai.api import create_server
from backend.ai.schemas import AIAnalysisResult, FeatureContribution, RiskLevel
from backend.ai.service import evaluate_risk


class TestAIModule(unittest.TestCase):
    """Test suite covering the VASP-TRACE AI risk evaluation and explainability engine."""

    def test_empty_graph_and_scoring_data(self):
        """Test Case 1: Empty graph and scoring data returns risk score 0.0 and RiskLevel.LOW."""
        result = evaluate_risk({}, {})
        self.assertIsInstance(result, AIAnalysisResult)
        self.assertEqual(result.risk_score, 0.0)
        self.assertEqual(result.risk_level, RiskLevel.LOW)
        self.assertEqual(result.risk_level.value, "LOW")
        self.assertEqual(len(result.feature_contributions), 0)
        self.assertIn("LOW", result.narrative)

    def test_sanction_hit_escalation(self):
        """Test Case 2: Sanction hit returns RiskLevel.CRITICAL and risk score >= 85.0."""
        # Test sanction_hit flag
        result_hit = evaluate_risk({}, {"sanction_hit": True})
        self.assertEqual(result_hit.risk_level, RiskLevel.CRITICAL)
        self.assertGreaterEqual(result_hit.risk_score, 85.0)
        self.assertIn("CRITICAL", result_hit.narrative)

        # Test alternative naming sanctions_match
        result_match = evaluate_risk({}, {"sanctions_match": True})
        self.assertEqual(result_match.risk_level, RiskLevel.CRITICAL)
        self.assertGreaterEqual(result_match.risk_score, 85.0)

    def test_mixer_proximity_and_darknet_exposure_increase_risk(self):
        """Test Case 3: Mixer proximity and darknet exposure increase risk score."""
        baseline = evaluate_risk({}, {})
        mixer_only = evaluate_risk({"mixer_proximity": 0.8}, {})
        darknet_only = evaluate_risk({}, {"darknet_exposure": True})
        combined = evaluate_risk({"mixer_proximity": 0.8}, {"darknet_exposure": True})

        self.assertGreater(mixer_only.risk_score, baseline.risk_score)
        self.assertGreater(darknet_only.risk_score, baseline.risk_score)
        self.assertGreater(combined.risk_score, mixer_only.risk_score)
        self.assertGreater(combined.risk_score, darknet_only.risk_score)

    def test_verified_kyc_produces_negative_mitigating_contribution(self):
        """Test Case 4: Verified KYC produces a negative mitigating contribution."""
        result = evaluate_risk({"mixer_proximity": 0.6}, {"kyc_verified": True})

        # Locate kyc_verified in feature contributions
        kyc_contrib = next(
            (c for c in result.feature_contributions if c.feature_name == "kyc_verified"),
            None,
        )
        self.assertIsNotNone(kyc_contrib, "kyc_verified should appear in feature contributions")
        self.assertLess(kyc_contrib.contribution, 0.0, "Verified KYC must produce a negative contribution")
        self.assertIn("MITIGATING FACTORS", result.narrative)

    def test_feature_contributions_sorted_descending_by_absolute_contribution(self):
        """Test Case 5: Feature contributions are sorted by absolute contribution descending."""
        graph_data = {
            "hop_count": 1,
            "mixer_proximity": 0.9,
            "peeling_chain_detected": True,
        }
        scoring_data = {
            "darknet_exposure": True,
            "kyc_verified": True,
        }
        result = evaluate_risk(graph_data, scoring_data)

        self.assertGreaterEqual(len(result.feature_contributions), 3)

        abs_contributions = [abs(c.contribution) for c in result.feature_contributions]
        sorted_abs = sorted(abs_contributions, reverse=True)
        self.assertEqual(
            abs_contributions,
            sorted_abs,
            f"Feature contributions should be sorted descending by |contribution|: {abs_contributions}",
        )

        for contrib in result.feature_contributions:
            self.assertIsInstance(contrib.feature_name, str)
            self.assertIsNotNone(contrib.feature_value)
            self.assertIsInstance(contrib.contribution, float)
            self.assertIsInstance(contrib.explanation, str)
            self.assertTrue(len(contrib.explanation) > 0)

    def test_ai_analysis_result_to_dict_format(self):
        """Test Case 6: AIAnalysisResult.to_dict() returns dict with required fields."""
        result = evaluate_risk(
            graph_data={"mixer_proximity": 0.75, "hop_count": 2},
            scoring_data={"sanction_hit": True},
        )
        data = result.to_dict()

        self.assertIsInstance(data, dict)

        required_keys = [
            "risk_score",
            "risk_level",
            "confidence_score",
            "feature_contributions",
            "narrative",
        ]
        for key in required_keys:
            self.assertIn(key, data, f"Required key '{key}' missing from to_dict() output")

        self.assertIsInstance(data["risk_score"], (int, float))
        self.assertEqual(data["risk_level"], "CRITICAL")
        self.assertIsInstance(data["confidence_score"], float)
        self.assertIsInstance(data["feature_contributions"], list)
        self.assertIsInstance(data["narrative"], str)

        # Check serialized items in feature_contributions
        if data["feature_contributions"]:
            first_item = data["feature_contributions"][0]
            self.assertIsInstance(first_item, dict)
            self.assertIn("feature_name", first_item)
            self.assertIn("feature_value", first_item)
            self.assertIn("contribution", first_item)
            self.assertIn("explanation", first_item)

    def test_missing_or_invalid_inputs_do_not_crash(self):
        """Test Case 7: Missing or invalid input values do not crash the service."""
        test_cases = [
            # None inputs
            (None, None),
            # Completely wrong data types for dicts
            ("invalid_string", [1, 2, 3]),
            (12345, True),
            # Invalid values within dictionary
            (
                {
                    "hop_count": "not_an_int",
                    "mixer_proximity": "not_a_float",
                    "peeling_chain_detected": None,
                    "rapid_fan_out": "yes",
                },
                {
                    "sanction_hit": "not_a_bool",
                    "darknet_exposure": None,
                    "kyc_verified": "false",
                    "unknown_flag": 999,
                },
            ),
            # Extreme / special float values
            (
                {"hop_count": -5, "mixer_proximity": float("nan")},
                {"high_risk_jurisdiction": float("inf")},
            ),
            # Boolean passed as hop count
            ({"hop_count": True}, {}),
            # Empty structures
            ({}, {}),
        ]

        for idx, (g_data, s_data) in enumerate(test_cases):
            with self.subTest(case_index=idx):
                try:
                    res = evaluate_risk(g_data, s_data)
                    self.assertIsInstance(res, AIAnalysisResult)
                    self.assertIsInstance(res.risk_score, float)
                    self.assertIsInstance(res.risk_level, RiskLevel)
                    self.assertIsInstance(res.confidence_score, float)
                    self.assertIsInstance(res.feature_contributions, list)
                    self.assertIsInstance(res.narrative, str)
                    self.assertGreaterEqual(res.risk_score, 0.0)
                    self.assertLessEqual(res.risk_score, 100.0)
                except Exception as exc:
                    self.fail(f"evaluate_risk crashed on invalid input case {idx}: {exc}")


class TestAIAPI(unittest.TestCase):
    """Test suite covering HTTP server endpoints using standard-library urllib client."""

    @classmethod
    def setUpClass(cls):
        # Bind to ephemeral port 0
        cls.server = create_server("127.0.0.1", 0)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_post_evaluate_success(self):
        """Test POST /ai/evaluate returns 200 OK with expected JSON structure."""
        url = f"http://127.0.0.1:{self.port}/ai/evaluate"
        payload = {
            "graph_data": {
                "hop_count": 2,
                "mixer_proximity": 0.7,
            },
            "scoring_data": {
                "sanction_hit": False,
                "darknet_exposure": True,
                "kyc_verified": False,
            },
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertIn("risk_score", data)
            self.assertEqual(data["risk_level"], "HIGH")
            self.assertEqual(data["risk_score"], 74.0)
            self.assertIn("confidence_score", data)
            self.assertIn("feature_contributions", data)
            self.assertIn("narrative", data)
            self.assertGreater(len(data["feature_contributions"]), 0)

    def test_post_evaluate_missing_fields_returns_400(self):
        """Test POST /ai/evaluate returns 400 when graph_data or scoring_data is missing."""
        url = f"http://127.0.0.1:{self.port}/ai/evaluate"
        payload = {"graph_data": {"hop_count": 2}}  # missing scoring_data
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 400)
        ctx.exception.close()

    def test_post_evaluate_invalid_json_returns_400(self):
        """Test POST /ai/evaluate returns 400 for malformed JSON."""
        url = f"http://127.0.0.1:{self.port}/ai/evaluate"
        req = urllib.request.Request(
            url,
            data=b"not a valid json string",
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 400)
        ctx.exception.close()

    def test_unsupported_route_returns_404(self):
        """Test unsupported route returns 404 Not Found."""
        url = f"http://127.0.0.1:{self.port}/unsupported"
        req = urllib.request.Request(url, method="GET")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 404)
        ctx.exception.close()


if __name__ == "__main__":
    unittest.main()

