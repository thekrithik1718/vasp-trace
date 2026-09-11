import React from 'react';

const DEFAULT_CANDIDATES = [
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
    confidence: 88.0,
    depositCluster: '0xd90e2...77bb',
    riskLevel: 'Critical',
    riskColor: 'crimson',
    jurisdiction: 'Sanctioned Protocol'
  }
];

export default function VaspResultsPlaceholder({ hasTraced, isTracing, candidates, metrics }) {
  const displayCandidates = (candidates && candidates.length > 0) ? candidates : DEFAULT_CANDIDATES;
  const displayMetrics = metrics || {
    attributionConfidence: '94.2%',
    depositMatch: 'Cluster 0x3f5',
    travelRuleRisk: 'FLAGGED'
  };

  return (
    <div className="card vasp-card">
      <div className="card-header">
        <div className="card-title-group">
          <div className="card-badge-icon icon-shield">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
            </svg>
          </div>
          <div>
            <h2 className="card-title">VASP Attribution & Risk</h2>
            <p className="card-subtitle">Entity identification & deposit clustering scores</p>
          </div>
        </div>

        <span className="results-count-pill font-mono">
          {hasTraced ? `${displayCandidates.length} Candidates` : '0 Attributed'}
        </span>
      </div>

      <div className="vasp-content-area">
        {/* Quick Summary Metrics */}
        <div className="vasp-metrics-grid">
          <div className="metric-box">
            <span className="metric-name">Attribution Confidence</span>
            <span className="metric-value font-mono">
              {hasTraced ? displayMetrics.attributionConfidence : '--'}
            </span>
          </div>
          <div className="metric-box">
            <span className="metric-name">Deposit Match</span>
            <span className="metric-value font-mono">
              {hasTraced ? displayMetrics.depositMatch : 'None'}
            </span>
          </div>
          <div className="metric-box">
            <span className="metric-name">Travel Rule Risk</span>
            <span className={`metric-value font-mono ${hasTraced ? 'text-amber' : ''}`}>
              {hasTraced ? displayMetrics.travelRuleRisk : 'Pending'}
            </span>
          </div>
        </div>

        {/* State 1: Shimmer Loading Skeleton while tracing */}
        {isTracing ? (
          <div className="candidate-skeleton-list">
            <div className="skeleton-hint font-mono">
              <span className="spinner-small"></span>
              <span>Scoring entity attribution signatures...</span>
            </div>
            <div className="skeleton-card shimmer"></div>
            <div className="skeleton-card shimmer"></div>
            <div className="skeleton-card shimmer"></div>
          </div>
        ) : hasTraced ? (
          /* State 2: Populated Candidate List */
          <div className="candidate-list">
            {displayCandidates.map((vasp, idx) => (
              <div key={vasp.name || idx} className="candidate-card">
                <div className="candidate-card-top">
                  <div className="candidate-identity">
                    <h4 className="candidate-name">{vasp.name}</h4>
                    <span className="candidate-type">{vasp.type}</span>
                  </div>
                  <div className="confidence-badge">
                    <span className="conf-value font-mono">{vasp.confidence}%</span>
                    <span className="conf-label">Confidence</span>
                  </div>
                </div>

                <div className="candidate-details font-mono">
                  <div className="detail-row">
                    <span className="detail-key">Deposit Cluster:</span>
                    <span className="detail-val text-cyan">{vasp.depositCluster}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-key">Jurisdiction:</span>
                    <span className="detail-val">{vasp.jurisdiction || 'Global'}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-key">Risk Rating:</span>
                    <span className={`risk-tag risk-${vasp.riskColor || 'emerald'}`}>{vasp.riskLevel || 'Low'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* State 3: Empty State before trace */
          <div className="vasp-empty-state">
            <div className="empty-icon-shield">
              <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                <path d="m9 12 2 2 4-4" />
              </svg>
            </div>
            <h4 className="empty-vasp-title">No VASP Attribution Yet</h4>
            <p className="empty-vasp-desc">
              Execute a wallet trace to evaluate destination deposit clusters against known Virtual Asset Service Provider heuristics. Attributed exchanges, institutional custodians, and risk scores will display here.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
