import React, { useState, useEffect } from 'react';
import Header from './components/Header.jsx';
import FallbackNotice from './components/FallbackNotice.jsx';
import TraceInput from './components/TraceInput.jsx';
import Graph from './components/Graph.jsx';
import VaspResultsPlaceholder from './components/VaspResultsPlaceholder.jsx';
import { traceWallet, checkBackendHealth } from './services/api.js';
import './App.css';

function App() {
  const [address, setAddress] = useState('0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045');
  const [hopDepth, setHopDepth] = useState(2);
  const [isTracing, setIsTracing] = useState(false);
  const [hasTraced, setHasTraced] = useState(false);
  const [traceProgressStep, setTraceProgressStep] = useState(1);
  const [isLiveBackend, setIsLiveBackend] = useState(false);
  const [isRetryingBackend, setIsRetryingBackend] = useState(false);
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [candidates, setCandidates] = useState([]);
  const [metrics, setMetrics] = useState(null);

  // Check backend health on initial mount
  useEffect(() => {
    checkBackendHealth().then((isHealthy) => {
      setIsLiveBackend(isHealthy);
    });
  }, []);

  // Retry connecting to backend API
  const handleRetryBackend = async () => {
    setIsRetryingBackend(true);
    try {
      const isHealthy = await checkBackendHealth();
      setIsLiveBackend(isHealthy);
      if (hasTraced && address) {
        await handleTrace(address);
      }
    } finally {
      setIsRetryingBackend(false);
    }
  };

  // Main Trace handler: sends address & hopDepth with animated progress steps
  const handleTrace = async (targetAddress) => {
    const addr = targetAddress || address;
    if (!addr || !addr.trim()) return;

    setIsTracing(true);
    setTraceProgressStep(1);

    // Progressive step simulation for hackathon visual feedback
    const step2Timer = setTimeout(() => setTraceProgressStep(2), 400);
    const step3Timer = setTimeout(() => setTraceProgressStep(3), 850);

    try {
      const result = await traceWallet(addr, hopDepth);
      
      // Allow user to see progressive scan steps
      await new Promise((resolve) => setTimeout(resolve, 1100));

      if (result && result.graph) {
        setGraphData(result.graph);
        setCandidates(result.candidates || []);
        setMetrics(result.metrics || null);
        setIsLiveBackend(!result.isFallback);
        setHasTraced(true);
      }
    } catch (err) {
      console.error('[VASP TRACE] Trace execution error:', err);
    } finally {
      clearTimeout(step2Timer);
      clearTimeout(step3Timer);
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
      setIsTracing(true);
      try {
        const result = await traceWallet(address, newDepth);
        if (result && result.graph) {
          setGraphData(result.graph);
          setCandidates(result.candidates || []);
          setMetrics(result.metrics || null);
          setIsLiveBackend(!result.isFallback);
        }
      } finally {
        setIsTracing(false);
      }
    }
  };

  return (
    <div className="dashboard-container">
      {/* Top Navigation & Brand with Hackathon Badge */}
      <Header isLiveBackend={isLiveBackend} />

      <main className="dashboard-main">
        {/* Transparent Fallback Notice for Judges & Hackathon Demo */}
        <FallbackNotice
          isLiveBackend={isLiveBackend}
          onRetry={handleRetryBackend}
          isRetrying={isRetryingBackend}
        />

        {/* Suspicious Address Search & Controls */}
        <TraceInput
          address={address}
          setAddress={setAddress}
          onTrace={handleTrace}
          isTracing={isTracing}
          hopDepth={hopDepth}
          setHopDepth={handleHopDepthChange}
        />

        {/* Core Content Grid: D3 Transaction Graph on Left, VASP Results on Right */}
        <div className="dashboard-grid">
          <section className="graph-section">
            <Graph
              graphData={graphData}
              isTracing={isTracing}
              hasTraced={hasTraced}
              traceProgressStep={traceProgressStep}
              onQuickStart={handleQuickStart}
              onSelectNode={() => {}}
            />
          </section>

          <aside className="results-section">
            <VaspResultsPlaceholder
              hasTraced={hasTraced}
              isTracing={isTracing}
              candidates={candidates}
              metrics={metrics}
            />
          </aside>
        </div>
      </main>

      {/* Footer Info Bar */}
      <footer className="dashboard-footer">
        <div className="footer-content">
          <span>VASP TRACE Engine • Autonomous Multi-Chain Attribution System</span>
          <span className="footer-status font-mono">
            {isLiveBackend ? '● API: Connected (Live)' : '○ Mode: Hackathon Demo (Simulation Fallback)'}
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;
