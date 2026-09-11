import React, { useState } from 'react';

export default function FallbackNotice({ isLiveBackend, onRetry, isRetrying }) {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  return (
    <aside 
      className={`fallback-banner ${isLiveBackend ? 'banner-live' : 'banner-fallback'}`}
      role="status"
      aria-live="polite"
    >
      <div className="banner-content">
        <div className="banner-icon-wrap">
          {isLiveBackend ? (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          )}
        </div>

        <div className="banner-text-group">
          <div className="banner-title">
            {isLiveBackend ? (
              <strong>Live Backend Connected</strong>
            ) : (
              <strong>Hackathon Demo Mode: Local Simulation Fallback Active</strong>
            )}
          </div>
          <p className="banner-description">
            {isLiveBackend
              ? 'Receiving live multi-hop transaction topologies and VASP entity scores from the backend API.'
              : 'Backend server is offline (http://localhost:8000/api). The dashboard is automatically operating in resilient client-side simulation mode with high-fidelity multi-hop transaction data.'}
          </p>
        </div>
      </div>

      <div className="banner-actions">
        {!isLiveBackend && (
          <button 
            type="button" 
            className={`btn-retry-backend ${isRetrying ? 'loading' : ''}`}
            onClick={onRetry}
            disabled={isRetrying}
          >
            {isRetrying ? (
              <>
                <span className="spinner-small"></span>
                <span>Connecting...</span>
              </>
            ) : (
              <>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                  <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                  <path d="M3 3v5h5" />
                </svg>
                <span>Retry Backend</span>
              </>
            )}
          </button>
        )}

        <button 
          type="button" 
          className="btn-dismiss-banner" 
          onClick={() => setDismissed(true)}
          title="Dismiss notification"
          aria-label="Dismiss banner"
        >
          ✕
        </button>
      </div>
    </aside>
  );
}
