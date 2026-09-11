import React, { useState } from 'react';

const SAMPLE_ADDRESSES = [
  { label: 'ETH Exploit Cluster', address: '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045', chain: 'Ethereum' },
  { label: 'BTC Mixer Outflow', address: 'bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq', chain: 'Bitcoin' },
  { label: 'High-Volume Nexus', address: '0x3cD751E6b0078Be393132286c442345e5DC49699', chain: 'Ethereum' }
];

export default function TraceInput({ address, setAddress, onTrace, isTracing, hopDepth, setHopDepth }) {
  const [validationError, setValidationError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!address.trim()) {
      setValidationError('Please enter a valid blockchain wallet or contract address');
      return;
    }
    setValidationError('');
    onTrace(address.trim());
  };

  const handleSelectSample = (sampleAddr) => {
    setAddress(sampleAddr);
    setValidationError('');
  };

  return (
    <section className="search-section">
      <form className="trace-form" onSubmit={handleSubmit}>
        <div className="input-group-container">
          <div className="input-field-wrapper">
            <div className="input-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.3-4.3" />
              </svg>
            </div>
            
            <input
              type="text"
              className="wallet-input font-mono"
              placeholder="Enter suspicious wallet address (0x... / bc1... / sol...)"
              value={address}
              onChange={(e) => {
                setAddress(e.target.value);
                if (validationError) setValidationError('');
              }}
              spellCheck="false"
              autoComplete="off"
            />

            {address && (
              <button 
                type="button" 
                className="clear-button" 
                onClick={() => setAddress('')}
                title="Clear input"
                aria-label="Clear address"
              >
                ✕
              </button>
            )}
          </div>

          <div className="controls-wrapper">
            <div className="hop-depth-selector">
              <span className="control-label">Hop Depth:</span>
              <div className="hop-buttons">
                {[1, 2, 3, 5].map((depth) => (
                  <button
                    key={depth}
                    type="button"
                    className={`hop-pill ${hopDepth === depth ? 'active' : ''}`}
                    onClick={() => setHopDepth(depth)}
                  >
                    {depth}
                  </button>
                ))}
              </div>
            </div>

            <button 
              type="submit" 
              className={`trace-button ${isTracing ? 'loading' : ''}`}
              disabled={isTracing}
            >
              {isTracing ? (
                <>
                  <span className="spinner"></span>
                  <span>Tracing Flows...</span>
                </>
              ) : (
                <>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                  </svg>
                  <span>Trace</span>
                </>
              )}
            </button>
          </div>
        </div>

        {validationError && (
          <div className="validation-banner">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span>{validationError}</span>
          </div>
        )}

        <div className="quick-presets">
          <span className="preset-label">Test with sample wallet:</span>
          <div className="preset-chips">
            {SAMPLE_ADDRESSES.map((item) => (
              <button
                key={item.address}
                type="button"
                className="preset-chip"
                onClick={() => handleSelectSample(item.address)}
              >
                <span className="chip-tag">{item.chain}</span>
                <span className="chip-name">{item.label}</span>
                <span className="chip-addr font-mono">{item.address.slice(0, 6)}...{item.address.slice(-4)}</span>
              </button>
            ))}
          </div>
        </div>
      </form>
    </section>
  );
}
