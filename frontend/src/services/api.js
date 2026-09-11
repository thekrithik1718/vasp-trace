// Base API URL configurable via environment variables (default to local backend proxy/port)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const REQUEST_TIMEOUT_MS = 5000;

/**
 * Check backend health
 * @returns {Promise<boolean>}
 */
export async function checkBackendHealth() {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 1500);

    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      signal: controller.signal,
      headers: { 'Accept': 'application/json' }
    });

    clearTimeout(timeoutId);
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * Send wallet address and hop depth to backend trace endpoint.
 * Note: The backend currently exposes Python modules and not a real HTTP endpoint yet.
 * This function acts as the exact API contract for the future FastAPI integration.
 *
 * @param {string} address - Suspicious blockchain wallet address
 * @param {number} hopDepth - Multi-hop depth
 * @returns {Promise<{ source_wallet: string, paths: Array, scoring_results: Array }>}
 */
export async function traceWallet(address, hopDepth = 2) {
  const cleanAddr = address ? address.trim() : '';

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  const response = await fetch(`${API_BASE_URL}/trace`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify({
      address: cleanAddr,
      hop_depth: hopDepth
    }),
    signal: controller.signal
  });

  clearTimeout(timeoutId);

  if (!response.ok) {
    throw new Error(`Backend API returned status ${response.status}`);
  }

  // The expected backend data schema is raw Member 1 + Member 2 combined output.
  const data = await response.json();
  return data;
}
