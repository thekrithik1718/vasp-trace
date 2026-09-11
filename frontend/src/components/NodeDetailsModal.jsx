import React, { useState, useEffect } from 'react';

export default function NodeDetailsModal({ node, connectedLinks, onClose }) {
  const [copied, setCopied] = useState(false);

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  if (!node) return null;

  const handleCopy = async () => {
    const textToCopy = node.fullAddress || node.id;
    let successful = false;

    // Try modern asynchronous Clipboard API
    if (navigator?.clipboard?.writeText) {
      try {
        await navigator.clipboard.writeText(textToCopy);
        successful = true;
      } catch {
        // Fall back to execCommand below if document is not focused
      }
    }

    // Fallback using temporary textarea
    if (!successful) {
      try {
        const textArea = document.createElement('textarea');
        textArea.value = textToCopy;
        textArea.style.position = 'fixed';
        textArea.style.left = '-9999px';
        textArea.style.top = '-9999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        successful = document.execCommand('copy');
        document.body.removeChild(textArea);
      } catch (err) {
        console.warn('[VASP TRACE] Clipboard copy failed:', err);
      }
    }

    if (successful) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const formatAddress = (addr) => {
    if (!addr || typeof addr !== 'string') return '--';
    if ((addr.startsWith('0x') || addr.startsWith('bc1')) && addr.length > 18) {
      return `${addr.slice(0, 8)}...${addr.slice(-6)}`;
    }
    return addr;
  };

  const getRiskClass = (level) => {
    switch (level?.toLowerCase()) {
      case 'critical': return 'risk-crimson';
      case 'high': return 'risk-crimson';
      case 'moderate': return 'risk-amber';
      case 'low': return 'risk-emerald';
      default: return 'risk-emerald';
    }
  };

  return (
    <div className="node-details-drawer">
      <div className="drawer-header">
        <div className="drawer-title-group">
          <span className={`drawer-type-badge type-${node.type}`}>
            {node.type === 'target' ? 'TARGET WALLET' : node.type === 'vasp' ? 'VASP ENTITY' : 'INTERMEDIATE HOP'}
          </span>
          <h3 className="drawer-title">{node.label}</h3>
        </div>
        <button type="button" className="drawer-close-btn" onClick={onClose} title="Close Panel">
          ✕
        </button>
      </div>

      <div className="drawer-body">
        {/* Full Address Bar with Copy */}
        <div className="drawer-address-box">
          <span className="address-label">Wallet Address</span>
          <div className="address-value-row">
            <span className="address-value font-mono">{node.fullAddress || node.id}</span>
            <button type="button" className="copy-btn" onClick={handleCopy} title="Copy Address">
              {copied ? '✓ Copied' : 'Copy'}
            </button>
          </div>
        </div>

        {/* Key Metrics Grid */}
        <div className="drawer-grid">
          <div className="drawer-stat">
            <span className="d-label">Hop Depth</span>
            <span className="d-val font-mono">{node.hop === 0 ? '0 (Origin)' : `Hop ${node.hop}`}</span>
          </div>

          <div className="drawer-stat">
            <span className="d-label">Balance</span>
            <span className="d-val font-mono text-cyan">{node.balance || '--'}</span>
          </div>

          <div className="drawer-stat">
            <span className="d-label">Risk Rating</span>
            <span className={`risk-tag ${getRiskClass(node.riskLevel)}`}>
              {node.riskLevel || 'Unknown'} ({node.riskScore}/100)
            </span>
          </div>

          <div className="drawer-stat">
            <span className="d-label">Tx Count</span>
            <span className="d-val font-mono">{node.txCount?.toLocaleString() || '--'}</span>
          </div>
        </div>

        {/* Attribution Info */}
        {node.vaspName && (
          <div className="attribution-box">
            <div className="attr-row">
              <span className="attr-key">Identified VASP:</span>
              <span className="attr-val text-emerald font-semibold">{node.vaspName}</span>
            </div>
            {node.vaspCategory && (
              <div className="attr-row">
                <span className="attr-key">Entity Category:</span>
                <span className="attr-val">{node.vaspCategory}</span>
              </div>
            )}
          </div>
        )}

        {/* Connected Transactions */}
        <div className="connected-transfers">
          <h4 className="transfers-title">
            Adjacent Transfers ({connectedLinks.length})
          </h4>
          <div className="transfer-list">
            {connectedLinks.map((link, idx) => {
              const isOutgoing = (link.source?.id || link.source) === node.id;
              const counterparty = isOutgoing ? (link.target?.label || link.target?.id || link.target) : (link.source?.label || link.source?.id || link.source);

              return (
                <div key={idx} className={`transfer-item ${link.isTracedPath ? 'traced-transfer' : ''}`}>
                  <div className="transfer-direction">
                    <span className={`direction-badge ${isOutgoing ? 'badge-out' : 'badge-in'}`}>
                      {isOutgoing ? 'OUT →' : '← IN'}
                    </span>
                    <span className="transfer-amount font-mono text-cyan">{link.amount}</span>
                    <span className="transfer-usd">{link.amountUsd}</span>
                  </div>

                  <div className="transfer-meta">
                    <span className="transfer-party">
                      {isOutgoing ? 'To: ' : 'From: '}<strong>{formatAddress(counterparty)}</strong>
                    </span>
                    <span className="transfer-time font-mono">{link.timestamp}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
