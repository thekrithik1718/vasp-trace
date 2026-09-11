import { generateMockGraph } from './mockGraphData.js';

// Base API URL configurable via environment variables (default to local backend proxy/port)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const REQUEST_TIMEOUT_MS = 3000;

/**
 * Fallback candidate generator based on address and hop depth
 */
function getFallbackCandidates(address, hopDepth) {
  const shortAddr = address.slice(0, 6) + '...' + address.slice(-4);
  return [
    {
      name: 'Binance Global (Cluster 0x3f5)',
      type: 'Tier 1 Centralized Exchange',
      confidence: 94.2,
      depositCluster: '0x3f5ce...8401',
      riskLevel: 'Moderate',
      riskColor: 'amber',
      jurisdiction: 'Global / Multi'
    },
    {
      name: 'Coinbase Custody',
      type: 'Regulated Institutional VASP',
      confidence: 76.5,
      depositCluster: '0xa090e...1294',
      riskLevel: 'Low',
      riskColor: 'emerald',
      jurisdiction: 'United States'
    },
    {
      name: 'Tornado.Cash Proxy Router',
      type: 'Smart Contract Mixer',
      confidence: hopDepth >= 3 ? 88.0 : 42.0,
      depositCluster: '0xd90e2...77bb',
      riskLevel: 'Critical',
      riskColor: 'crimson',
      jurisdiction: 'Sanctioned Protocol'
    }
  ];
}

function getFallbackMetrics(address, hopDepth) {
  return {
    attributionConfidence: '94.2%',
    depositMatch: 'Cluster 0x3f5',
    travelRuleRisk: 'FLAGGED'
  };
}

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
 * Send wallet address and hop depth to backend trace endpoint
 * with automatic fallback to high-fidelity mock data if backend is offline.
 *
 * @param {string} address - Suspicious blockchain wallet address
 * @param {number} hopDepth - Multi-hop depth (1, 2, 3, 5)
 * @returns {Promise<{ graph: Object, candidates: Array, metrics: Object, isFallback: boolean }>}
 */
export async function traceWallet(address, hopDepth = 2) {
  const cleanAddr = address ? address.trim() : '';

  // Attempt backend API call
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    // Primary endpoint: POST /api/trace
    const response = await fetch(`${API_BASE_URL}/trace`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        address: cleanAddr,
        hop_depth: hopDepth,
        hopDepth: hopDepth
      }),
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (response.ok) {
      const data = await response.json();

      // Normalize response structure
      const graph = data.graph || {
        nodes: data.nodes || [],
        links: data.links || data.edges || []
      };

      const candidates = data.candidates || data.vasp_candidates || data.vaspCandidates || [];
      const metrics = data.metrics || {
        attributionConfidence: data.confidence ? `${data.confidence}%` : '85.0%',
        depositMatch: data.depositCluster || 'Detected',
        travelRuleRisk: data.riskLevel || 'FLAGGED'
      };

      return {
        graph,
        candidates,
        metrics,
        isFallback: false
      };
    } else {
      console.warn(`[VASP TRACE] Backend API returned status ${response.status}. Using fallback mock data.`);
    }
  } catch (error) {
    // Network failure, connection refused, or timeout
    console.info('[VASP TRACE] Backend API unavailable or timed out. Operating in client fallback mode with simulation data.', error?.message || error);
  }

  // Fallback path
  const fallbackGraph = generateMockGraph(cleanAddr, hopDepth);
  const fallbackCandidates = getFallbackCandidates(cleanAddr, hopDepth);
  const fallbackMetrics = getFallbackMetrics(cleanAddr, hopDepth);

  return {
    graph: fallbackGraph,
    candidates: fallbackCandidates,
    metrics: fallbackMetrics,
    isFallback: true
  };
}
