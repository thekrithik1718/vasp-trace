# VASP-TRACE AI & Explainability Service

Lightweight, zero-dependency AI risk scoring, explainability (XAI), and audit narrative service for Virtual Asset Service Provider (VASP) transaction monitoring and compliance.

Built entirely using Python's standard library (`dataclasses`, `http.server`, `unittest`).

---

## 1. How to Start the API

Run the server from the repository root directory:

```bash
python -m backend.ai.api
```

By default, the server listens at:
```
http://127.0.0.1:8000/
```

### Custom Host and Port
You can customize the host and port via environment variables:

```bash
# Windows PowerShell
$env:PORT="8080"; python -m backend.ai.api

# Linux/macOS
PORT=8080 python -m backend.ai.api
```

---

## 2. Endpoint & Method

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/ai/evaluate` | Evaluates graph metrics and scoring flags, returning risk classification, ranked feature attributions, and a plain-English compliance narrative. |
| `OPTIONS` | `/ai/evaluate` | CORS preflight handling for browser clients. |

---

## 3. Request Example

### Headers
- `Content-Type: application/json`

### Request Body (JSON)
```json
{
  "graph_data": {
    "hop_count": 2,
    "mixer_proximity": 0.7,
    "peeling_chain_detected": true
  },
  "scoring_data": {
    "sanction_hit": false,
    "darknet_exposure": true,
    "kyc_verified": false
  }
}
```

### cURL Example
```bash
curl -X POST http://127.0.0.1:8000/ai/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "graph_data": {
      "hop_count": 2,
      "mixer_proximity": 0.7
    },
    "scoring_data": {
      "sanction_hit": false,
      "darknet_exposure": true,
      "kyc_verified": false
    }
  }'
```

---

## 4. Response Structure

Status: `200 OK`
Content-Type: `application/json`

```json
{
  "risk_score": 74.0,
  "risk_level": "HIGH",
  "confidence_score": 0.85,
  "feature_contributions": [
    {
      "feature_name": "darknet_exposure",
      "feature_value": true,
      "contribution": 35.0,
      "explanation": "Darknet Market Exposure active: Direct or indirect interaction with known darknet illicit marketplaces."
    },
    {
      "feature_name": "mixer_proximity",
      "feature_value": 0.7,
      "contribution": 21.0,
      "explanation": "Coin Mixer Proximity intensity at 0.7: Proximity to privacy pools, mixers, or coin join contracts."
    },
    {
      "feature_name": "hop_count",
      "feature_value": 2,
      "contribution": 18.0,
      "explanation": "Close (2-hop) intermediary connection to confirmed illicit node."
    }
  ],
  "narrative": "EXECUTIVE SUMMARY: Entity evaluated at HIGH risk with a score of 74.0/100.0 (model confidence: 85%).\n\nPRIMARY RISK DRIVERS:\n  1. [darknet_exposure] (+35.0 pts) - Darknet Market Exposure active: Direct or indirect interaction with known darknet illicit marketplaces.\n  2. [mixer_proximity] (+21.0 pts) - Coin Mixer Proximity intensity at 0.7: Proximity to privacy pools, mixers, or coin join contracts.\n  3. [hop_count] (+18.0 pts) - Close (2-hop) intermediary connection to confirmed illicit node.\n\nRECOMMENDED COMPLIANCE ACTION:\n  [ENHANCED DUE DILIGENCE] Place on heightened watchlist. Request verifiable KYC and source-of-funds documentation from counterparty VASP prior to fund release.",
  "metadata": {
    "signals_evaluated": 5,
    "total_raw_inputs": 5,
    "critical_escalation_applied": false
  }
}
```

### Error Responses

- `400 Bad Request`: Malformed JSON or missing `graph_data` / `scoring_data`.
  ```json
  {
    "error": "Missing required fields. Both 'graph_data' and 'scoring_data' are required."
  }
  ```
- `404 Not Found`: Unsupported route or method.
  ```json
  {
    "error": "Route not found",
    "path": "/unknown"
  }
  ```

---

## 5. How the Frontend Can Call It

Browser clients can directly query the endpoint. Built-in CORS headers (`Access-Control-Allow-Origin: *`) allow requests from Vite / React dev servers (`http://localhost:5173` or `http://localhost:3000`).

### Example: JavaScript / TypeScript (`frontend/src/services/aiService.js`)

```javascript
const API_BASE_URL = 'http://127.0.0.1:8000';

export async function evaluateVaspRisk(graphData, scoringData) {
  const response = await fetch(`${API_BASE_URL}/ai/evaluate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      graph_data: graphData,
      scoring_data: scoringData,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `HTTP error ${response.status}`);
  }

  const result = await response.json();
  return result;
}
```

### Frontend Usage in a Component

```javascript
import { evaluateVaspRisk } from '../services/aiService';

async function handleAnalyze() {
  const result = await evaluateVaspRisk(
    { hop_count: 2, mixer_proximity: 0.7 },
    { sanction_hit: false, darknet_exposure: true, kyc_verified: false }
  );

  console.log('Risk Level:', result.risk_level); // "HIGH"
  console.log('Score:', result.risk_score);       // 74.0
  console.log('Narrative:', result.narrative);
}
```

---

## 6. Running Automated Tests

Run the unit test suite:

```bash
python -m unittest backend.ai.test_ai -v
```
