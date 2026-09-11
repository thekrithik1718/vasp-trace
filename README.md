# VASP-TRACE: AI-Powered Risk & Explainability Engine

**VASP-TRACE** is an auditable compliance and transaction tracing platform for Virtual Asset Service Providers (VASPs). It bridges blockchain graph topological analysis with regulatory anti-money laundering (AML) compliance rules, delivering transparent risk scoring, ranked feature attributions, and audit-ready compliance narratives.

---

## 1. Problem Statement

Under Financial Action Task Force (FATF) Travel Rule and international AML/CFT directives, financial institutions and VASPs must monitor transaction counterparties for sanctions exposure, darknet interactions, and money laundering typologies. 

Traditional approaches suffer from two major flaws:
1. **Opaque "Black-Box" AI**: Machine learning models that produce a risk score without transparent rationales fail regulatory scrutiny and cannot be cited in formal Suspicious Activity Reports (SAR/STR).
2. **Disconnected Rule Silos**: Graph tracing tools and compliance screening databases operate in isolation without unified scoring or plain-English narrative synthesis.

**VASP-TRACE AI** solves this by unifying graph topological indicators and compliance flags into a single, deterministic, explainable evaluation pipeline.

---

## 2. AI Module Responsibilities

The AI section ([`backend/ai/`](backend/ai/)) is structured around four core pillars:

1. **Deterministic Risk Scoring ([`model.py`](backend/ai/model.py))**:
   - Computes an auditable, normalized risk score from `0.0` (clean) to `100.0` (maximum risk).
   - Combines graph features (hop count to illicit entities, coin mixer proximity, peeling chain structures, transaction velocity anomalies) and compliance flags (sanctions matches, darknet exposure, unlicensed VASP, verified KYC).
   - Enforces an immediate **Critical Escalation Override** ($\ge 85.0$) upon confirmed sanctions list match.
2. **Standard Risk Levels**:
   - `LOW`: Score $0.0 - 24.9$ (Routine automated processing).
   - `MEDIUM`: Score $25.0 - 49.9$ (Standard monitoring).
   - `HIGH`: Score $50.0 - 74.9$ (Enhanced Due Diligence required).
   - `CRITICAL`: Score $75.0 - 100.0$ (Mandatory freeze and SAR escalation).
3. **Ranked Explainability ([`explainer.py`](backend/ai/explainer.py))**:
   - Quantifies individual feature impact (+/− score points).
   - Ranks factors by absolute contribution magnitude so analysts immediately see the primary drivers.
4. **Plain-English Compliance Narrative**:
   - Synthesizes an executive summary, primary risk drivers, mitigating factors (e.g., verified KYC), and specific regulatory action recommendations.

---

## 3. Setup and Installation

The solution is built **strictly with the Python standard library** and **Vanilla Web standards**—zero external package installations (`pip` or `npm`) are required.

### Prerequisites
- Python 3.8+

### Step 1: Start the AI Backend API
Run from the project root:
```bash
python -m backend.ai.api
```
*Backend runs at `http://127.0.0.1:8000`.*

### Step 2: Serve the Frontend
In a separate terminal, run from the project root:
```bash
python -m http.server 3000 --directory frontend
```
*Frontend runs at `http://127.0.0.1:3000`.*

---

## 4. API Specification

- **Endpoint**: `POST /ai/evaluate`
- **Headers**: `Content-Type: application/json`

### Sample Request
```json
{
  "graph_data": {
    "hop_count": 2,
    "mixer_proximity": 0.7
  },
  "scoring_data": {
    "sanction_hit": false,
    "darknet_exposure": true,
    "kyc_verified": false
  }
}
```

### Sample Response (`200 OK`)
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

---

## 5. End-to-End Demo Walkthrough

1. Open your browser to **`http://127.0.0.1:3000`**.
2. **Demo Scenario A: Multi-Hop Obfuscation (High Risk)**
   - Set **Hop Count** to `2`.
   - Set **Mixer Proximity** to `0.70`.
   - Check **Darknet Marketplace Exposure**.
   - Click **Evaluate Risk**.
   - *Observation*: Score is `74.0` (`HIGH` badge). The top 3 ranked drivers break down points (+35 darknet, +21 mixer, +18 hops) with an Enhanced Due Diligence (EDD) recommendation.
3. **Demo Scenario B: Critical Sanctions Match**
   - Check **Sanction List Match (OFAC/UN/EU)**.
   - Click **Evaluate Risk**.
   - *Observation*: System escalates to `CRITICAL` risk with an immediate transaction block recommendation and SAR filing directive.
4. **Demo Scenario C: Mitigating Factor (KYC Verified)**
   - Check **Verified KYC & Regulated Counterparty VASP**.
   - *Observation*: The model applies a `-15.0 pts` mitigating factor under the "Mitigating Factors" narrative section.
5. **Demo Scenario D: Backend Resilience**
   - Stop the backend server and click **Evaluate Risk**.
   - *Observation*: The UI catches the network error and provides a clear alert instructing the user to start the backend, preventing application lockup.

---

## 6. Automated Testing & Verification

Automated tests cover unit logic, edge cases, HTTP endpoints, and full end-to-end integration.

### Run AI Unit & API Tests
```bash
python -m unittest backend.ai.test_ai -v
```
**Confirmed Result:**
```text
Ran 11 tests in 0.556s
OK
```

### Run End-to-End Integration Suite
```bash
python backend/ai/test_e2e.py
```
**Confirmed Result:**
```text
All 15 E2E checks passed (Backend delivery, static asset paths, JS modules, HTTP 200, 400, 404, schema verification).
0 issues found.
```

---

## 7. Known Limitations

- **Deterministic Weighted Rules vs. Statistical ML**:
  - *Current Design*: The current engine utilizes a transparent, weighted rule-based heuristic model.
  - *Rationale*: Guarantees 100% auditable explanations, zero hallucination, strict regulatory determinism, zero external dependency weight, and instant out-of-the-box execution on any machine.
  - *Trade-off*: Does not yet perform unsupervised clustering or non-linear probabilistic graph representation learning.

---

## 8. Future Improvements

1. **Graph Neural Network (GNN) Integration**:
   - Train inductive GNNs (GraphSAGE / GAT) on transaction graphs to output latent counterparty risk embeddings.
2. **SHAP & Tree-Based Explainability**:
   - Integrate TreeSHAP with an XGBoost/LightGBM risk classifier to maintain explainability alongside non-linear ML predictions.
3. **Live Blockchain RPC Ingestion**:
   - Connect directly to Ethereum / Bitcoin nodes to extract real-time UTXO peeling chains and contract interactions.
4. **Automated Regulatory SAR/STR Export**:
   - One-click export of AI-generated compliance narratives into standard FinCEN XML / FATF reporting formats.