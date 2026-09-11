import React, { useRef, useEffect, useState } from 'react';
import * as d3 from 'd3';
import NodeDetailsModal from './NodeDetailsModal.jsx';

export default function Graph({ graphData, onSelectNode, isTracing, hasTraced, onQuickStart, traceProgressStep }) {
  const containerRef = useRef(null);
  const svgRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [hoveredLink, setHoveredLink] = useState(null);
  const zoomBehaviorRef = useRef(null);

  // Initialize or update D3 graph
  useEffect(() => {
    if (!containerRef.current || !hasTraced || !graphData || !graphData.nodes || graphData.nodes.length === 0) {
      return;
    }

    const container = containerRef.current;
    const width = container.clientWidth || 840;
    const height = Math.max(container.clientHeight || 580, 580);

    // Deep clone data to avoid D3 mutation conflicts across renders
    const nodes = graphData.nodes.map((d) => ({ ...d }));
    const links = graphData.links.map((d) => ({ ...d }));

    // Select SVG
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', [0, 0, width, height]);

    // Clear previous elements
    svg.selectAll('*').remove();

    // Defs: Gradients, Markers, and Filters
    const defs = svg.append('defs');

    // Arrowhead marker for normal edges
    defs.append('marker')
      .attr('id', 'arrow-default')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 30)
      .attr('refY', 0)
      .attr('markerWidth', 6.5)
      .attr('markerHeight', 6.5)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-4L9,0L0,4')
      .attr('fill', '#475569');

    // Arrowhead marker for traced path edges
    defs.append('marker')
      .attr('id', 'arrow-traced')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 30)
      .attr('refY', 0)
      .attr('markerWidth', 7.5)
      .attr('markerHeight', 7.5)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-4L9,0L0,4')
      .attr('fill', '#06b6d4');

    // Glow filter for target & traced path
    const glowFilter = defs.append('filter')
      .attr('id', 'node-glow')
      .attr('x', '-50%')
      .attr('y', '-50%')
      .attr('width', '200%')
      .attr('height', '200%');

    glowFilter.append('feGaussianBlur')
      .attr('stdDeviation', '4.5')
      .attr('result', 'coloredBlur');

    const feMerge = glowFilter.append('feMerge');
    feMerge.append('feMergeNode').attr('in', 'coloredBlur');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    // Root zoomable container <g>
    const g = svg.append('g').attr('class', 'graph-root-group');

    // Zoom and Pan Behavior
    const zoom = d3.zoom()
      .scaleExtent([0.25, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
      });

    svg.call(zoom);
    zoomBehaviorRef.current = zoom;

    // Simulation Setup with enhanced spacing
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id((d) => d.id).distance(160))
      .force('charge', d3.forceManyBody().strength(-450))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(56));

    // Links Container
    const linkGroup = g.append('g').attr('class', 'links-layer');

    const link = linkGroup.selectAll('.graph-link')
      .data(links)
      .join('path')
      .attr('class', (d) => `graph-link ${d.isTracedPath ? 'traced-path' : 'regular-path'}`)
      .attr('stroke', (d) => (d.isTracedPath ? '#06b6d4' : '#334155'))
      .attr('stroke-width', (d) => (d.isTracedPath ? 2.8 : 1.6))
      .attr('stroke-dasharray', (d) => (d.isTracedPath ? '6,4' : 'none'))
      .attr('fill', 'none')
      .attr('marker-end', (d) => (d.isTracedPath ? 'url(#arrow-traced)' : 'url(#arrow-default)'))
      .on('mouseenter', (event, d) => {
        setHoveredLink(d);
      })
      .on('mouseleave', () => {
        setHoveredLink(null);
      });

    // Edge Labels Container (Transaction Amounts)
    const linkLabelGroup = g.append('g').attr('class', 'link-labels-layer');

    const linkLabel = linkLabelGroup.selectAll('.link-label-wrap')
      .data(links)
      .join('g')
      .attr('class', (d) => `link-label-wrap ${d.isTracedPath ? 'label-traced' : ''}`);

    linkLabel.append('rect')
      .attr('rx', 4)
      .attr('ry', 4)
      .attr('fill', '#070d1a')
      .attr('stroke', (d) => (d.isTracedPath ? 'rgba(6, 182, 212, 0.5)' : 'rgba(255, 255, 255, 0.12)'))
      .attr('stroke-width', 1)
      .attr('height', 18);

    linkLabel.append('text')
      .attr('class', 'link-label font-mono')
      .attr('text-anchor', 'middle')
      .attr('dy', '0.35em')
      .attr('fill', (d) => (d.isTracedPath ? '#38bdf8' : '#94a3b8'))
      .attr('font-size', '9.5px')
      .attr('font-weight', '600')
      .text((d) => d.amount);

    // Resize label bounding rects based on text width
    linkLabel.each(function () {
      const textElem = d3.select(this).select('text').node();
      if (textElem) {
        const bbox = textElem.getBBox();
        d3.select(this).select('rect')
          .attr('x', bbox.x - 5)
          .attr('y', bbox.y - 2)
          .attr('width', bbox.width + 10)
          .attr('height', bbox.height + 4);
      }
    });

    // Drag behavior for nodes
    const drag = d3.drag()
      .on('start', (event, d) => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      })
      .on('drag', (event, d) => {
        d.fx = event.x;
        d.fy = event.y;
      })
      .on('end', (event, d) => {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      });

    // Nodes Container
    const nodeGroup = g.append('g').attr('class', 'nodes-layer');

    const node = nodeGroup.selectAll('.graph-node')
      .data(nodes)
      .join('g')
      .attr('class', (d) => `graph-node node-${d.type} ${d.isSuspicious ? 'is-suspicious' : ''}`)
      .call(drag)
      .on('click', (event, d) => {
        if (event.defaultPrevented) return;
        event.stopPropagation();
        setSelectedNode(d);
        if (onSelectNode) onSelectNode(d);
      });

    // Target pulsing halo ring
    node.filter((d) => d.type === 'target')
      .append('circle')
      .attr('r', 26)
      .attr('class', 'target-pulse-ring')
      .attr('fill', 'none')
      .attr('stroke', '#06b6d4')
      .attr('stroke-width', 1.8)
      .attr('opacity', 0.8);

    // Node Outer Glow / Border circle
    node.append('circle')
      .attr('r', (d) => (d.type === 'target' ? 20 : d.type === 'vasp' ? 18 : 15))
      .attr('class', 'node-circle')
      .attr('fill', (d) => {
        if (d.type === 'target') return '#041d2f';
        if (d.type === 'vasp') return '#06281e';
        return '#251b04';
      })
      .attr('stroke', (d) => {
        if (d.type === 'target') return '#06b6d4';
        if (d.type === 'vasp') return '#10b981';
        return '#f59e0b';
      })
      .attr('stroke-width', 2.2)
      .attr('filter', (d) => (d.type === 'target' ? 'url(#node-glow)' : 'none'));

    // Inner icon or dot
    node.append('circle')
      .attr('r', (d) => (d.type === 'target' ? 7 : 5))
      .attr('fill', (d) => {
        if (d.type === 'target') return '#06b6d4';
        if (d.type === 'vasp') return '#10b981';
        return '#f59e0b';
      });

    // Node Label Group (Address & Hop)
    const labelGroup = node.append('g').attr('class', 'node-labels');

    // Hop badge
    labelGroup.append('text')
      .attr('class', 'node-hop-badge font-mono text-halo')
      .attr('text-anchor', 'middle')
      .attr('y', (d) => (d.type === 'target' ? -28 : -22))
      .attr('fill', (d) => (d.type === 'target' ? '#22d3ee' : d.type === 'vasp' ? '#34d399' : '#fbbf24'))
      .attr('font-size', '9.5px')
      .attr('font-weight', '700')
      .text((d) => (d.hop === 0 ? 'TARGET (HOP 0)' : d.type === 'vasp' ? `VASP (HOP ${d.hop})` : `HOP ${d.hop}`));

    // Short address
    labelGroup.append('text')
      .attr('class', 'node-address-text font-mono text-halo')
      .attr('text-anchor', 'middle')
      .attr('y', (d) => (d.type === 'target' ? 34 : 30))
      .attr('fill', '#f1f5f9')
      .attr('font-size', '10.5px')
      .attr('font-weight', '600')
      .text((d) => (d.label || `${d.id.slice(0, 6)}...${d.id.slice(-4)}`));

    // Secondary sub-label (Balance / Exchange name)
    labelGroup.append('text')
      .attr('class', 'node-sub-text font-mono text-halo')
      .attr('text-anchor', 'middle')
      .attr('y', (d) => (d.type === 'target' ? 47 : 43))
      .attr('fill', '#94a3b8')
      .attr('font-size', '9px')
      .text((d) => (d.vaspName ? d.vaspName : d.balance));

    // Simulation Tick handler
    simulation.on('tick', () => {
      link.attr('d', (d) => `M${d.source.x},${d.source.y} L${d.target.x},${d.target.y}`);

      linkLabel.attr('transform', (d) => {
        const x = (d.source.x + d.target.x) / 2;
        const y = (d.source.y + d.target.y) / 2;
        return `translate(${x},${y})`;
      });

      node.attr('transform', (d) => `translate(${d.x},${d.y})`);
    });

    // Cleanup simulation on unmount
    return () => {
      simulation.stop();
    };
  }, [graphData, hasTraced]);

  // Zoom control handlers
  const handleZoomIn = () => {
    if (svgRef.current && zoomBehaviorRef.current) {
      d3.select(svgRef.current).transition().duration(250).call(zoomBehaviorRef.current.scaleBy, 1.3);
    }
  };

  const handleZoomOut = () => {
    if (svgRef.current && zoomBehaviorRef.current) {
      d3.select(svgRef.current).transition().duration(250).call(zoomBehaviorRef.current.scaleBy, 0.75);
    }
  };

  const handleResetZoom = () => {
    if (svgRef.current && zoomBehaviorRef.current) {
      d3.select(svgRef.current).transition().duration(400).call(
        zoomBehaviorRef.current.transform,
        d3.zoomIdentity
      );
    }
  };

  // Find links connected to currently selected node
  const getConnectedLinks = (node) => {
    if (!node || !graphData || !graphData.links) return [];
    return graphData.links.filter(
      (l) => (l.source?.id || l.source) === node.id || (l.target?.id || l.target) === node.id
    );
  };

  return (
    <div className="card graph-card d3-graph-wrapper" ref={containerRef}>
      <div className="card-header">
        <div className="card-title-group">
          <div className="card-badge-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="18" cy="5" r="3" />
              <circle cx="6" cy="12" r="3" />
              <circle cx="18" cy="19" r="3" />
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
              <line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
            </svg>
          </div>
          <div>
            <h2 className="card-title">Transaction Flow Graph (D3.js)</h2>
            <p className="card-subtitle">Force-directed propagation canvas with multi-hop fund flow attribution</p>
          </div>
        </div>

        <div className="graph-toolbar">
          <span className="graph-tag font-mono">
            {isTracing ? 'SCANNING TOPOLOGY...' : hasTraced ? `Nodes: ${graphData?.nodes?.length || 0} • Edges: ${graphData?.links?.length || 0}` : 'AWAITING TARGET'}
          </span>

          {hasTraced && (
            <div className="tool-buttons">
              <button type="button" className="tool-btn" onClick={handleResetZoom} title="Reset & Center View" aria-label="Reset View">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                  <path d="M3 3v5h5" />
                </svg>
              </button>
              <button type="button" className="tool-btn" onClick={handleZoomIn} title="Zoom In (+)" aria-label="Zoom In">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                  <line x1="11" y1="8" x2="11" y2="14" />
                  <line x1="8" y1="11" x2="14" y2="11" />
                </svg>
              </button>
              <button type="button" className="tool-btn" onClick={handleZoomOut} title="Zoom Out (-)" aria-label="Zoom Out">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                  <line x1="8" y1="11" x2="14" y2="11" />
                </svg>
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="d3-canvas-container">
        {/* Background Radar / Grid Overlay */}
        <div className="grid-overlay"></div>
        {isTracing && <div className="scanning-beam"></div>}

        {/* State 1: Empty State before first trace */}
        {!hasTraced && !isTracing && (
          <div className="graph-empty-state">
            <div className="empty-radar-glow">
              <div className="radar-circle rc-1"></div>
              <div className="radar-circle rc-2"></div>
              <div className="radar-circle rc-3"></div>
              <div className="radar-sweep"></div>
              <div className="radar-center-icon">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10" />
                  <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" />
                </svg>
              </div>
            </div>

            <h3 className="empty-state-headline">Awaiting Target Wallet Address</h3>
            <p className="empty-state-subtext">
              Enter a suspicious blockchain wallet address in the search bar above and click <strong>Trace</strong> to discover multi-hop fund flows and attributed VASP deposit clusters.
            </p>

            <div className="empty-state-quickactions">
              <span className="quick-label">Or quick-start with a verified demo target:</span>
              <div className="quick-buttons-row">
                <button
                  type="button"
                  className="quick-demo-btn"
                  onClick={() => onQuickStart('0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045')}
                >
                  <span className="q-tag">ETH</span>
                  <span>Exploit Cluster Demo</span>
                </button>
                <button
                  type="button"
                  className="quick-demo-btn"
                  onClick={() => onQuickStart('bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq')}
                >
                  <span className="q-tag">BTC</span>
                  <span>Mixer Outflow Demo</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* State 2: Multi-step Loading State while tracing */}
        {isTracing && (
          <div className="graph-loading-overlay">
            <div className="loading-card">
              <div className="loading-spinner-ring">
                <span className="spinner-center-dot"></span>
              </div>
              <h3 className="loading-title">Tracing On-Chain Transaction Flows</h3>
              <p className="loading-subtitle">Querying ledger blocks, expanding peel chains & evaluating attribution heuristics...</p>
              
              <div className="tracing-steps-list">
                <div className={`step-item ${traceProgressStep >= 1 ? 'step-active' : ''}`}>
                  <span className="step-icon">{traceProgressStep > 1 ? '✓' : '1'}</span>
                  <span>Ingesting wallet address & querying parent txs</span>
                </div>
                <div className={`step-item ${traceProgressStep >= 2 ? 'step-active' : ''}`}>
                  <span className="step-icon">{traceProgressStep > 2 ? '✓' : '2'}</span>
                  <span>Mapping multi-hop intermediary flow paths</span>
                </div>
                <div className={`step-item ${traceProgressStep >= 3 ? 'step-active' : ''}`}>
                  <span className="step-icon">{traceProgressStep >= 3 ? '✓' : '3'}</span>
                  <span>Attributing VASP deposit clusters & scoring risk</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* State 3: Populated D3 Graph */}
        <svg ref={svgRef} className={`d3-svg-canvas ${hasTraced ? 'canvas-visible' : 'canvas-hidden'}`}></svg>

        {/* Hovered Link Tooltip */}
        {hoveredLink && (
          <div className="link-hover-tooltip font-mono">
            <div className="tooltip-title">Transfer Record</div>
            <div className="tooltip-row"><span>Amount:</span> <strong>{hoveredLink.amount} ({hoveredLink.amountUsd})</strong></div>
            <div className="tooltip-row"><span>Timestamp:</span> {hoveredLink.timestamp}</div>
            <div className="tooltip-row"><span>Tx Hash:</span> {hoveredLink.txHash}</div>
            <div className="tooltip-row"><span>Classification:</span> {hoveredLink.isTracedPath ? '⚡ Primary Traced Path' : 'Secondary Branch'}</div>
          </div>
        )}

        {/* Node Details Inspection Drawer */}
        {selectedNode && (
          <NodeDetailsModal
            node={selectedNode}
            connectedLinks={getConnectedLinks(selectedNode)}
            onClose={() => setSelectedNode(null)}
          />
        )}
      </div>

      {/* Clear Legend for Target, Intermediate, and VASP */}
      <div className="graph-footer-legend">
        <div className="legend-items-row">
          <div className="legend-chip">
            <span className="legend-dot dot-origin"></span>
            <span>Target Wallet</span>
          </div>
          <div className="legend-chip">
            <span className="legend-dot dot-hop"></span>
            <span>Intermediate Relay</span>
          </div>
          <div className="legend-chip">
            <span className="legend-dot dot-vasp"></span>
            <span>Attributed VASP</span>
          </div>
          <div className="legend-chip">
            <span className="legend-line line-traced"></span>
            <span>Traced Flow Path</span>
          </div>
        </div>

        <span className="graph-hint font-mono">
          {hasTraced
            ? 'Interactive: Click node for inspector • Drag nodes • Scroll wheel to zoom'
            : 'Controls active once tracing starts'}
        </span>
      </div>
    </div>
  );
}
