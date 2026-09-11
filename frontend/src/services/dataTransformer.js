export function transformBackendData(graphInput, scoringResults) {
  const nodesMap = new Map();
  const linksMap = new Map();

  // Create a quick lookup for VASP entities from scoring results
  const vaspLookup = {};
  if (scoringResults && Array.isArray(scoringResults)) {
    scoringResults.forEach(res => {
      // Find the destination address for this VASP if possible,
      // or we'll just match it when we traverse paths
      vaspLookup[res.vasp_name] = res;
    });
  }

  // Helper to add a node
  const addNode = (address, hop, isTarget = false, vaspName = null) => {
    if (!nodesMap.has(address)) {
      nodesMap.set(address, {
        id: address,
        label: `${address.slice(0, 6)}...${address.slice(-4)}`,
        fullAddress: address,
        type: isTarget ? 'target' : (vaspName ? 'vasp' : 'intermediate'),
        hop: hop,
        vaspName: vaspName,
        isSuspicious: isTarget // Target is the suspicious wallet
      });
    } else {
      // Update hop if we found a shorter path
      const existing = nodesMap.get(address);
      if (hop < existing.hop) {
        existing.hop = hop;
      }
      if (vaspName && !existing.vaspName) {
        existing.type = 'vasp';
        existing.vaspName = vaspName;
      }
    }
  };

  // Process all paths
  if (graphInput && graphInput.paths && Array.isArray(graphInput.paths)) {
    graphInput.paths.forEach((path) => {
      const addresses = path.addresses || [];
      const transactions = path.transactions || [];

      // Determine if this path ends in a known VASP based on scoring results
      let pathVaspName = null;
      if (scoringResults && Array.isArray(scoringResults)) {
        const destination = addresses[addresses.length - 1];
        const matchingResult = scoringResults.find(r => r.destination_address === destination);
        if (matchingResult) {
          pathVaspName = matchingResult.vasp_name;
        }
      }

      addresses.forEach((addr, idx) => {
        const hop = idx;
        const isTarget = hop === 0;
        const isDestination = idx === addresses.length - 1;
        const vaspName = isDestination ? pathVaspName : null;
        addNode(addr, hop, isTarget, vaspName);
      });

      transactions.forEach((tx) => {
        const linkId = `${tx.tx_hash}-${tx.from}-${tx.to}`;
        if (!linksMap.has(linkId)) {
          linksMap.set(linkId, {
            source: tx.from,
            target: tx.to,
            amount: tx.amount,
            timestamp: tx.timestamp,
            txHash: tx.tx_hash,
            isTracedPath: true, // All returned paths are traced paths
            hop: 1 // Link hop isn't strictly necessary but we can set it
          });
        }
      });
    });
  } else if (graphInput && graphInput.source_wallet) {
    // Just add the source wallet if there are no paths
    addNode(graphInput.source_wallet, 0, true);
  }

  return {
    nodes: Array.from(nodesMap.values()),
    links: Array.from(linksMap.values())
  };
}
