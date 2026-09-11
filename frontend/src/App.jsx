import React, { useState } from 'react';
import Header from './components/Header.jsx';
import TraceInput from './components/TraceInput.jsx';
import Graph from './components/Graph.jsx';
import VaspResults from './components/VaspResults.jsx';
import { traceWallet } from './services/api.js';
import { transformBackendData } from './services/dataTransformer.js';
import './App.css';

function App() {
  const [address, setAddress] = useState('wallet_suspicious_001');
  const [hopDepth, setHopDepth] = useState(2);
  const [isTracing, setIsTracing] = useState(false);
  const [hasTraced, setHasTraced] = useState(false);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [candidates, setCandidates] = useState([]);
  const [error, setError] = useState(null);

  // Main Trace handler: sends address & hopDepth
  const handleTrace = async (targetAddress) => {
    const addr = targetAddress || address;
    if (!addr || !addr.trim()) return;

    setIsTracing(true);
    setError(null);
    setHasTraced(false);

    try {
      // Call the backend API
      const result = await traceWallet(addr, hopDepth);
      
      // result should contain { source_wallet, paths, scoring_results } based on backend contract
      const transformedGraph = transformBackendData(result, result.scoring_results || []);
      setGraphData(transformedGraph);
      setCandidates(result.scoring_results || []);
      setHasTraced(true);
    } catch (err) {
      console.error('[VASP TRACE] Trace execution error:', err);
      setError(err.message || "Failed to trace wallet");
    } finally {
      setIsTracing(false);
    }
  };

  // Quick start directly from the empty state
  const handleQuickStart = (presetAddress) => {
    setAddress(presetAddress);
    handleTrace(presetAddress);
  };

  // Hop depth update handler
  const handleHopDepthChange = async (newDepth) => {
    setHopDepth(newDepth);
    if (hasTraced && address) {
      handleTrace(address);
    }
  };

  return (
    <div className="dashboard-container">
      {/* Top Navigation & Brand with Hackathon Badge */}
      <Header />

      <main className="dashboard-main">
        {/* Suspicious Address Search & Controls */}
        <TraceInput
          address={address}
          setAddress={setAddress}
          onTrace={handleTrace}
          isTracing={isTracing}
          hopDepth={hopDepth}
          setHopDepth={handleHopDepthChange}
        />

        {error && (
          <div style={{ color: '#ef4444', padding: '12px 24px', backgroundColor: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', margin: '0 24px 20px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
            Error: {error}
          </div>
        )}

        {/* Core Content Grid: D3 Transaction Graph on Left, VASP Results on Right */}
        <div className="dashboard-grid">
          <section className="graph-section">
            <Graph
              graphData={graphData}
              isTracing={isTracing}
              hasTraced={hasTraced}
              onQuickStart={handleQuickStart}
              onSelectNode={() => {}}
            />
          </section>

          <aside className="results-section">
            <VaspResults
              hasTraced={hasTraced}
              isTracing={isTracing}
              candidates={candidates}
            />
          </aside>
        </div>
      </main>

      {/* Footer Info Bar */}
      <footer className="dashboard-footer">
        <div className="footer-content">
          <span>VASP TRACE Engine • Autonomous Multi-Chain Attribution System</span>
          <span className="footer-status font-mono">
             Backend Integration Pending
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;
