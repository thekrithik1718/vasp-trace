from fastapi.testclient import TestClient
from backend.api import app

client = TestClient(app)

def test_api_trace_valid_request():
    response = client.post(
        "/api/trace",
        json={"address": "wallet_suspicious_001", "hop_depth": 4}
    )
    assert response.status_code == 200, f"Request failed: {response.text}"
    data = response.json()

    assert "source_wallet" in data
    assert "paths" in data
    assert "scoring_results" in data

    assert isinstance(data["paths"], list)
    assert isinstance(data["scoring_results"], list)

    # At least one known VASP is detected from sample dataset
    assert len(data["scoring_results"]) > 0

    # Verify the additive destination_address schema change
    first_res = data["scoring_results"][0]
    assert "destination_address" in first_res
    assert first_res["destination_address"] is not None
    assert first_res["destination_address"] in [
        path["addresses"][-1] for path in data["paths"] if path["addresses"]
    ]

def test_api_trace_invalid_address():
    response = client.post(
        "/api/trace",
        json={"address": "invalid_or_missing_wallet", "hop_depth": 4}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Source wallet not found"

def test_api_trace_invalid_hop_depth():
    response = client.post(
        "/api/trace",
        json={"address": "wallet_suspicious_001", "hop_depth": 0}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid request"

def test_api_trace_missing_body():
    response = client.post("/api/trace")
    assert response.status_code == 422
