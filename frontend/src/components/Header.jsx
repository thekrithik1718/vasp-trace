import React from 'react';

export default function Header({ isLiveBackend }) {
  return (
    <header className="header">
      <div className="header-brand">
        <div className="logo-container">
          <div className="logo-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
              <path d="m9 12 2 2 4-4" />
            </svg>
          </div>
          <div className="logo-pulse"></div>
        </div>
        <div>
          <div className="brand-title-wrap">
            <h1 className="brand-title">VASP <span>TRACE</span></h1>
            <span className="badge-version">HACKATHON BUILD</span>
          </div>
          <p className="brand-subtitle">Virtual Asset Service Provider Attribution & Multi-Hop Forensics</p>
        </div>
      </div>

      <div className="header-meta">
        <div className={`status-pill ${isLiveBackend ? 'pill-live' : 'pill-fallback'}`}>
          <span className={`status-indicator ${isLiveBackend ? '' : 'status-fallback'}`}></span>
          <span className="status-text">
            {isLiveBackend ? 'Backend: Live' : 'Backend: Fallback Sim'}
          </span>
        </div>

        <div className="meta-stat hide-mobile">
          <span className="stat-label">Coverage</span>
          <span className="stat-value font-mono">1,400+ VASPs</span>
        </div>

        <div className="meta-stat hide-tablet">
          <span className="stat-label">Supported Chains</span>
          <span className="stat-value">ETH • BTC • SOL • BSC</span>
        </div>
      </div>
    </header>
  );
}
