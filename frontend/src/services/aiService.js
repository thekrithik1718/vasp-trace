/**
 * AI Service for communicating with the VASP-TRACE AI backend.
 * Zero external dependencies, uses native fetch API.
 */

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

/**
 * Send graph metrics and scoring flags to the AI evaluation endpoint.
 *
 * @param {Object} graphData - Topological graph metrics (hop_count, mixer_proximity, etc.)
 * @param {Object} scoringData - Compliance flags (sanction_hit, darknet_exposure, kyc_verified)
 * @param {string} [baseUrl] - Base API URL (defaults to http://127.0.0.1:8000)
 * @returns {Promise<Object>} The AIAnalysisResult object
 * @throws {Error} Descriptive error on network failure, 400 bad request, or server issues
 */
export async function evaluateRisk(graphData, scoringData, baseUrl = DEFAULT_API_BASE_URL) {
  const endpoint = `${baseUrl}/ai/evaluate`;

  let response;
  try {
    response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        graph_data: graphData,
        scoring_data: scoringData,
      }),
    });
  } catch (networkError) {
    // Network failure (e.g. backend server is not running or CORS blocked)
    throw new Error(
      `Cannot connect to AI backend at ${baseUrl}. ` +
      `Please verify that the backend server is running via 'python -m backend.ai.api'.`
    );
  }

  // Handle error responses from API
  if (!response.ok) {
    let errorMessage = `Server responded with HTTP ${response.status} (${response.statusText})`;
    try {
      const errorPayload = await response.json();
      if (errorPayload && errorPayload.error) {
        errorMessage = errorPayload.error;
      }
    } catch {
      // Non-JSON error body fallback
    }
    throw new Error(errorMessage);
  }

  // Parse successful response
  try {
    const data = await response.json();
    return data;
  } catch (parseError) {
    throw new Error("Failed to parse response JSON from AI service.");
  }
}
