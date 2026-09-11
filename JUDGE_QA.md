# VASP-TRACE: Judge Q&A Guide

Quick-reference answers to anticipated questions from competition judges regarding the AI, Explainability, and Integration architecture.

---

## 1. Problem & Value Proposition

### Q1: What exact problem does VASP-TRACE solve?
**A:** Virtual Asset Service Providers (VASPs) are legally mandated under FATF Travel Rule regulations to identify and report illicit transaction counterparties. Existing tools either produce opaque "black-box" risk numbers that cannot stand up in regulatory audits or produce disjointed alert lists. VASP-TRACE solves this by providing unified, transparent risk scores paired with ranked feature attributions and audit-ready plain-English narratives that can be directly pasted into formal Suspicious Activity Reports (SAR/STR).

### Q2: Who is the primary user of this interface?
**A:** AML Compliance Officers, Crypto Forensics Investigators, and Regulatory Auditors who must quickly understand *why* a wallet or transaction was flagged and what regulatory step to take next.

---

## 2. AI Model & Risk Scoring

### Q3: How does your risk model calculate risk scores?
**A:** The model uses a deterministic, multi-factor weighted rule engine. It ingests graph topological features (hop distance to illicit nodes, mixer intensity, peeling chains) and compliance scoring flags (sanctions list matches, darknet exposure, KYC status). Each signal is scored and normalized between `0.0` and `100.0`.

### Q4: How are risk tiers established?
**A:** 
- **`LOW` (0.0 – 24.9)**: Routine automated processing.
- **`MEDIUM` (25.0 – 49.9)**: Standard due diligence and continued monitoring.
- **`HIGH` (50.0 – 74.9)**: Enhanced Due Diligence (EDD) required before fund release.
- **`CRITICAL` (75.0 – 100.0)**: Mandatory freeze, immediate compliance escalation, and SAR filing.

### Q5: What is the "Critical Escalation Override"?
**A:** Under OFAC and international sanctions law, strict liability applies. If a confirmed sanctions match (`sanction_hit` or `sanctions_match`) is detected, the model automatically overrides the score to at least `85.0` (`CRITICAL`), regardless of other mitigating factors.

### Q6: How is the confidence score determined?
**A:** Confidence is calculated based on input signal density and indicator agreement. A sparse request with few observed signals starts at `0.50–0.60`, scaling up to `0.95` as corroborating topological and compliance indicators are evaluated. Confirmed sanctions automatically raise confidence above `0.90`.

---

## 3. Explainability (XAI) & Compliance Narrative

### Q7: Why is Explainability (XAI) so important in crypto AML?
**A:** Financial regulators (FinCEN, FATF, FCA) reject uninterpretable AI models. If a VASP freezes customer funds or files a SAR based solely on a black-box probability, they face severe legal and regulatory liability. Regulators require clear, auditable evidence and specific factual drivers.

### Q8: How are feature contributions ranked?
**A:** Every active signal is assigned a signed contribution score (+ points for risk amplifiers, − points for mitigating factors like verified KYC). The explainability engine sorts these features in descending order of their absolute contribution magnitude (`|contribution|`), ensuring the most decisive factors appear first.

### Q9: What makes your compliance narrative unique?
**A:** Instead of showing raw JSON numbers, the narrative engine synthesizes:
1. **Executive Summary** (risk tier, score, confidence percentage).
2. **Primary Risk Drivers** (the top factors driving up risk).
3. **Mitigating Factors** (e.g., Tier-3 KYC verification).
4. **Actionable Regulatory Recommendation** (clear protocol instructions for the analyst).

---

## 4. Architecture & Integration

### Q10: How does the AI section connect to peer modules (`graph` and `scoring`)?
**A:** The entry point `evaluate_risk(graph_data: dict, scoring_data: dict) -> AIAnalysisResult` defines a clear, decoupled contract. The `graph` module passes topological metrics (hops, mixer proximity, clustering), and the `scoring` module passes compliance screening flags. The AI module operates independently without depending on private internals.

### Q11: Why did you use Python’s standard library `http.server` instead of FastAPI or Flask?
**A:** To ensure **maximum portability and zero external dependency risk**. The entire backend and frontend run out-of-the-box on any vanilla Python 3 installation without requiring `pip install`, virtual environments, or Node.js toolchains, while still supporting standard REST JSON requests, HTTP status codes (`200`, `400`, `404`), and CORS preflight.

### Q12: How does the frontend communicate with the backend?
**A:** The frontend uses standard ES Modules (`fetch` API) to send `POST` requests to `http://127.0.0.1:8000/ai/evaluate`. It handles loading states, input validation, network unavailability, and dynamically renders the response.

---

## 5. Testing & Validation

### Q13: How did you test your implementation?
**A:** We built two automated test suites using standard-library tools:
1. **Unit & API Suite (`backend.ai.test_ai`)**: 11 unit tests verifying edge cases (empty inputs, missing keys, extreme float values, sanctions escalation, KYC deduction, and API status codes).
2. **End-to-End Suite (`backend.ai.test_e2e`)**: Spawns both backend and frontend servers simultaneously and tests real HTTP network requests, static asset delivery, and schema consistency.

### Q14: How does the system handle corrupt or invalid inputs?
**A:** Defensive programming guards all entry points. Non-numeric strings, negative hop counts, `NaN`, and `Infinity` are rejected by safe parsers without crashing the server, defaulting safely to valid normalized assessments.

---

## 6. Limitations & Design Decisions

### Q15: Why use deterministic weighted rules rather than a trained deep learning model?
**A:** In high-stakes regulatory compliance:
- **Auditability**: Every single point must be traceable to a defined regulatory standard.
- **Zero Hallucination**: Rule-backed models never invent false connections.
- **Instant Deployment**: No massive checkpoint files, GPU requirements, or dependency drift.
- **Baseline for Future ML**: Transparent rules establish the ground-truth benchmark against which future ML models are trained and calibrated.

---

## 7. Future Scope & Roadmap

### Q16: What is the next step for this project?
**A:** 
1. **Graph Neural Networks (GNNs)**: Implement GraphSAGE/GAT on transaction subgraphs to produce automated structural embeddings.
2. **Hybrid TreeSHAP**: Combine XGBoost classification with SHAP attributions so complex non-linear interactions remain 100% explainable.
3. **Live Blockchain RPC Sync**: Ingest real-time mempool and block data from Ethereum/Bitcoin RPC nodes.
4. **Automated SAR XML Export**: One-click generation of FinCEN-compliant SAR filings directly from the AI narrative.
