import React from 'react';

export default function VaspResults({ hasTraced, isTracing, candidates }) {
  const displayCandidates = (candidates && candidates.length > 0) ? candidates : [];

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
            <p className="card-subtitle">Entity identification & scoring logic</p>
          </div>
        </div>

        <span className="results-count-pill font-mono">
          {hasTraced ? `${displayCandidates.length} Attributed` : '0 Attributed'}
        </span>
      </div>

      <div className="vasp-content-area">
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
        ) : hasTraced && displayCandidates.length > 0 ? (
          /* State 2: Populated Candidate List */
          <div className="candidate-list">
            {displayCandidates.map((vasp, idx) => (
              <div key={idx} className="candidate-card">
                <div className="candidate-card-top">
                  <div className="candidate-identity">
                    <h4 className="candidate-name">{vasp.vasp_name}</h4>
                    <span className="candidate-type">Score: {vasp.score}/100</span>
                  </div>
                  <div className="confidence-badge">
                    <span className="conf-value font-mono">{vasp.confidence_level}</span>
                    <span className="conf-label">Confidence</span>
                  </div>
                </div>

                <div className="candidate-details font-mono">
                  <div className="detail-row">
                    <span className="detail-key">Hop Count:</span>
                    <span className="detail-val text-cyan">{vasp.hop_count}</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-key">Amount Retention:</span>
                    <span className="detail-val">{(vasp.amount_retention * 100).toFixed(2)}%</span>
                  </div>
                  <div className="detail-row">
                    <span className="detail-key">Supporting Paths:</span>
                    <span className="detail-val">{vasp.supporting_path_count}</span>
                  </div>
                </div>

                {vasp.evidence && vasp.evidence.length > 0 && (
                  <div className="evidence-list font-mono" style={{ marginTop: '12px', paddingTop: '8px', borderTop: '1px solid rgba(255,255,255,0.1)'}}>
                    <div className="evidence-title" style={{ fontSize: '10px', color: '#94a3b8', marginBottom: '4px' }}>Scoring Evidence:</div>
                    {vasp.evidence.map((ev, i) => (
                      <div key={i} className="evidence-item" style={{ fontSize: '11px', color: '#cbd5e1', marginBottom: '2px' }}>- {ev}</div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : hasTraced ? (
          /* State 3: Traced but no VASPs found */
          <div className="vasp-empty-state">
             <div className="empty-icon-shield">
              <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="12" cy="12" r="10" />
                <line x1="4.93" y1="4.93" x2="19.07" y2="19.07" />
              </svg>
            </div>
            <h4 className="empty-vasp-title">No VASPs Detected</h4>
            <p className="empty-vasp-desc">
              The traced paths did not reach any known Virtual Asset Service Providers within the selected hop depth.
            </p>
          </div>
        ) : (
          /* State 4: Empty State before trace */
          <div className="vasp-empty-state">
            <div className="empty-icon-shield">
              <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                <path d="m9 12 2 2 4-4" />
              </svg>
            </div>
            <h4 className="empty-vasp-title">No VASP Attribution Yet</h4>
            <p className="empty-vasp-desc">
              Execute a wallet trace to evaluate destination deposits against known Virtual Asset Service Provider heuristics. Attributed exchanges and risk scores will display here.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
