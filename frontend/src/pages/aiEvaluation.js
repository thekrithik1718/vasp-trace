/**
 * Controller logic for AI Evaluation Page.
 * Connects UI inputs to aiService and renders results into the DOM.
 */

import { evaluateRisk } from "../services/aiService.js";

// DOM Element references
const form = document.getElementById("ai-evaluation-form");
const submitBtn = document.getElementById("submit-btn");
const submitBtnText = document.getElementById("btn-text");
const submitSpinner = document.getElementById("btn-spinner");

const alertError = document.getElementById("alert-error");
const placeholderBox = document.getElementById("placeholder-box");
const resultsContainer = document.getElementById("results-container");

// Metric display elements
const statRiskScore = document.getElementById("stat-risk-score");
const statRiskLevel = document.getElementById("stat-risk-level");
const statConfidence = document.getElementById("stat-confidence");
const contributionsTableBody = document.getElementById("contributions-tbody");
const narrativeBox = document.getElementById("narrative-box");

// Input element references
const hopCountInput = document.getElementById("hop_count");
const mixerProximityInput = document.getElementById("mixer_proximity");
const mixerProximityDisplay = document.getElementById("mixer_proximity_val");
const sanctionHitInput = document.getElementById("sanction_hit");
const darknetExposureInput = document.getElementById("darknet_exposure");
const kycVerifiedInput = document.getElementById("kyc_verified");

// Scenario button references
const btnScenarioHigh = document.getElementById("btn-scenario-high");
const btnScenarioSanction = document.getElementById("btn-scenario-sanction");
const btnScenarioKyc = document.getElementById("btn-scenario-kyc");
const btnScenarioLow = document.getElementById("btn-scenario-low");

/**
 * Populate form inputs without automatically submitting.
 * @param {Object} values
 */
function populateScenario(values) {
  clearError();
  if (hopCountInput) {
    hopCountInput.value = values.hop_count;
  }
  if (mixerProximityInput) {
    mixerProximityInput.value = values.mixer_proximity;
    if (mixerProximityDisplay) {
      mixerProximityDisplay.textContent = parseFloat(values.mixer_proximity).toFixed(2);
    }
  }
  if (sanctionHitInput) {
    sanctionHitInput.checked = Boolean(values.sanction_hit);
  }
  if (darknetExposureInput) {
    darknetExposureInput.checked = Boolean(values.darknet_exposure);
  }
  if (kycVerifiedInput) {
    kycVerifiedInput.checked = Boolean(values.kyc_verified);
  }
}

if (btnScenarioHigh) {
  btnScenarioHigh.addEventListener("click", () => {
    populateScenario({
      hop_count: 2,
      mixer_proximity: 0.70,
      sanction_hit: false,
      darknet_exposure: true,
      kyc_verified: false,
    });
  });
}

if (btnScenarioSanction) {
  btnScenarioSanction.addEventListener("click", () => {
    populateScenario({
      hop_count: 1,
      mixer_proximity: 0.40,
      sanction_hit: true,
      darknet_exposure: false,
      kyc_verified: false,
    });
  });
}

if (btnScenarioKyc) {
  btnScenarioKyc.addEventListener("click", () => {
    populateScenario({
      hop_count: 3,
      mixer_proximity: 0.30,
      sanction_hit: false,
      darknet_exposure: false,
      kyc_verified: true,
    });
  });
}

if (btnScenarioLow) {
  btnScenarioLow.addEventListener("click", () => {
    populateScenario({
      hop_count: 0,
      mixer_proximity: 0.00,
      sanction_hit: false,
      darknet_exposure: false,
      kyc_verified: true,
    });
  });
}

// Keep slider and text display in sync
if (mixerProximityInput && mixerProximityDisplay) {
  mixerProximityInput.addEventListener("input", (e) => {
    mixerProximityDisplay.textContent = parseFloat(e.target.value).toFixed(2);
  });
}

/**
 * Display an error message in the alert box.
 * @param {string} message - Message to display
 */
function showError(message) {
  if (!alertError) return;
  alertError.textContent = message;
  alertError.style.display = "block";
}

/**
 * Clear the error alert.
 */
function clearError() {
  if (!alertError) return;
  alertError.textContent = "";
  alertError.style.display = "none";
}

/**
 * Set loading UI state.
 * @param {boolean} isLoading
 */
function setLoading(isLoading) {
  if (submitBtn) submitBtn.disabled = isLoading;
  if (submitSpinner) submitSpinner.style.display = isLoading ? "inline-block" : "none";
  if (submitBtnText) submitBtnText.textContent = isLoading ? "Evaluating Risk..." : "Evaluate Risk";
}

/**
 * Render evaluation results in the UI.
 * @param {Object} result - Result from evaluateRisk
 */
function renderResults(result) {
  // 1. Overall Metrics
  if (statRiskScore) {
    statRiskScore.textContent = `${Number(result.risk_score).toFixed(1)}`;
  }

  if (statConfidence) {
    const confidencePct = Math.round(Number(result.confidence_score) * 100);
    statConfidence.textContent = `${confidencePct}%`;
  }

  if (statRiskLevel) {
    statRiskLevel.textContent = result.risk_level;
    statRiskLevel.className = "badge";
    switch (result.risk_level) {
      case "CRITICAL":
        statRiskLevel.classList.add("badge-critical");
        break;
      case "HIGH":
        statRiskLevel.classList.add("badge-high");
        break;
      case "MEDIUM":
        statRiskLevel.classList.add("badge-medium");
        break;
      case "LOW":
      default:
        statRiskLevel.classList.add("badge-low");
        break;
    }
  }

  // 2. Feature Contributions Table
  if (contributionsTableBody) {
    contributionsTableBody.innerHTML = "";

    const contributions = result.feature_contributions || [];
    if (contributions.length === 0) {
      const emptyRow = document.createElement("tr");
      emptyRow.innerHTML = `<td colspan="4" style="text-align: center; color: var(--text-muted);">No active risk features or flags detected.</td>`;
      contributionsTableBody.appendChild(emptyRow);
    } else {
      contributions.forEach((item) => {
        const row = document.createElement("tr");

        const sign = item.contribution > 0 ? "+" : "";
        const contribClass = item.contribution > 0 ? "contrib-pos" : item.contribution < 0 ? "contrib-neg" : "";

        // Format value safely
        let displayVal = item.feature_value;
        if (typeof displayVal === "boolean") {
          displayVal = displayVal ? "true" : "false";
        }

        row.innerHTML = `
          <td><code>${escapeHtml(item.feature_name)}</code></td>
          <td>${escapeHtml(String(displayVal))}</td>
          <td class="${contribClass}">${sign}${Number(item.contribution).toFixed(1)}</td>
          <td>${escapeHtml(item.explanation)}</td>
        `;
        contributionsTableBody.appendChild(row);
      });
    }
  }

  // 3. Compliance Narrative
  if (narrativeBox) {
    narrativeBox.textContent = result.narrative || "No narrative generated.";
  }

  // 4. Reveal Results Container
  if (placeholderBox) placeholderBox.style.display = "none";
  if (resultsContainer) resultsContainer.style.display = "block";
}

/**
 * Basic HTML escaping helper to prevent injection.
 * @param {string} str
 */
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

/**
 * Handle form submission.
 */
if (form) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearError();

    // 1. Validate inputs
    const hopCountRaw = hopCountInput ? hopCountInput.value.trim() : "";
    const hopCount = parseInt(hopCountRaw, 10);
    if (isNaN(hopCount) || hopCount < 0) {
      showError("Please enter a valid non-negative integer for Hop Count.");
      if (hopCountInput) hopCountInput.focus();
      return;
    }

    const mixerProximityRaw = mixerProximityInput ? mixerProximityInput.value.trim() : "";
    const mixerProximity = parseFloat(mixerProximityRaw);
    if (isNaN(mixerProximity) || mixerProximity < 0 || mixerProximity > 1) {
      showError("Mixer Proximity must be a valid number between 0.00 and 1.00.");
      if (mixerProximityInput) mixerProximityInput.focus();
      return;
    }

    // 2. Prepare payload
    const graphData = {
      hop_count: hopCount,
      mixer_proximity: mixerProximity,
    };

    const scoringData = {
      sanction_hit: sanctionHitInput ? Boolean(sanctionHitInput.checked) : false,
      darknet_exposure: darknetExposureInput ? Boolean(darknetExposureInput.checked) : false,
      kyc_verified: kycVerifiedInput ? Boolean(kycVerifiedInput.checked) : false,
    };

    // 3. Trigger API Call
    setLoading(true);
    try {
      const result = await evaluateRisk(graphData, scoringData);
      renderResults(result);
    } catch (err) {
      showError(err.message || "An unexpected error occurred during evaluation.");
    } finally {
      setLoading(false);
    }
  });
}
