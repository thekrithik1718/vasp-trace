/**
 * Service generating realistic multi-hop transaction graph data for VASP TRACE
 */

export function generateMockGraph(targetAddress = '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045', hopDepth = 2) {
  const cleanAddr = targetAddress.trim() || '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045';
  
  // Format short address helper
  const short = (addr) => `${addr.slice(0, 6)}...${addr.slice(-4)}`;

  const nodes = [
    {
      id: cleanAddr,
      label: 'Target Wallet',
      fullAddress: cleanAddr,
      type: 'target',
      hop: 0,
      balance: '142.80 ETH',
      txCount: 184,
      riskScore: 94,
      riskLevel: 'Critical',
      vaspName: null,
      isSuspicious: true,
      role: 'Subject of Investigation',
      firstSeen: '2026-08-14',
      lastActive: '2026-09-11 10:14:02 UTC'
    }
  ];

  const links = [];

  // Hop 1 Intermediate Nodes
  const hop1Wallets = [
    {
      id: '0x3a91F08A663cE9fA1052E9B3a14e1c2d0f509B11',
      label: 'Peel Relay 1',
      fullAddress: '0x3a91F08A663cE9fA1052E9B3a14e1c2d0f509B11',
      type: 'intermediate',
      hop: 1,
      balance: '34.20 ETH',
      txCount: 68,
      riskScore: 82,
      riskLevel: 'High',
      vaspName: null,
      isSuspicious: true,
      role: 'Intermediate Relay / Mux',
      firstSeen: '2026-08-20',
      lastActive: '2026-09-11 10:45:19 UTC'
    },
    {
      id: '0x7e29C8B93f0b2fD35160A441dD2d2e1B6B2a09A4',
      label: 'Unrelated Node',
      fullAddress: '0x7e29C8B93f0b2fD35160A441dD2d2e1B6B2a09A4',
      type: 'intermediate',
      hop: 1,
      balance: '2.15 ETH',
      txCount: 12,
      riskScore: 35,
      riskLevel: 'Low',
      vaspName: null,
      isSuspicious: false,
      role: 'Secondary Counterparty',
      firstSeen: '2026-09-01',
      lastActive: '2026-09-08 14:12:00 UTC'
    }
  ];

  nodes.push(...hop1Wallets);

  // Link from Target to Hop 1
  links.push({
    source: cleanAddr,
    target: hop1Wallets[0].id,
    amount: '45.00 ETH',
    amountUsd: '$121,500',
    timestamp: '2026-09-11 10:20:12 UTC',
    txHash: '0x9a8f3b...4c1e',
    isTracedPath: true,
    hop: 1
  });

  links.push({
    source: cleanAddr,
    target: hop1Wallets[1].id,
    amount: '3.50 ETH',
    amountUsd: '$9,450',
    timestamp: '2026-09-10 18:05:44 UTC',
    txHash: '0x1b2c3d...9f8e',
    isTracedPath: false,
    hop: 1
  });

  // Hop 2
  if (hopDepth >= 2) {
    const hop2Wallets = [
      {
        id: '0x8192bC7F359aB02a3d38A24b2231F6052044C71E',
        label: 'Consolidator',
        fullAddress: '0x8192bC7F359aB02a3d38A24b2231F6052044C71E',
        type: 'intermediate',
        hop: 2,
        balance: '78.90 ETH',
        txCount: 142,
        riskScore: 78,
        riskLevel: 'High',
        vaspName: null,
        isSuspicious: true,
        role: 'Layering Aggregator',
        firstSeen: '2026-08-25',
        lastActive: '2026-09-11 11:02:50 UTC'
      },
      {
        id: '0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE',
        label: 'Binance Deposit',
        fullAddress: '0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE',
        type: 'vasp',
        hop: 2,
        balance: '1,420.50 ETH',
        txCount: 12400,
        riskScore: 45,
        riskLevel: 'Moderate',
        vaspName: 'Binance Global',
        vaspCategory: 'Tier 1 Centralized Exchange',
        isSuspicious: false,
        role: 'Exchange Deposit Hot Wallet',
        firstSeen: '2021-04-10',
        lastActive: '2026-09-11 11:30:00 UTC'
      }
    ];

    nodes.push(...hop2Wallets);

    links.push({
      source: hop1Wallets[0].id,
      target: hop2Wallets[0].id,
      amount: '40.00 ETH',
      amountUsd: '$108,000',
      timestamp: '2026-09-11 10:52:33 UTC',
      txHash: '0x4d5e6f...8a7b',
      isTracedPath: true,
      hop: 2
    });

    links.push({
      source: hop1Wallets[0].id,
      target: hop2Wallets[1].id,
      amount: '4.80 ETH',
      amountUsd: '$12,960',
      timestamp: '2026-09-11 11:05:14 UTC',
      txHash: '0x7e8f9a...3b2c',
      isTracedPath: false,
      hop: 2
    });

    // Hop 3
    if (hopDepth >= 3) {
      const hop3Wallets = [
        {
          id: '0x28C6c06298d514Db089934071355E5743bf21d60',
          label: 'Binance Hot 14',
          fullAddress: '0x28C6c06298d514Db089934071355E5743bf21d60',
          type: 'vasp',
          hop: 3,
          balance: '15,200.00 ETH',
          txCount: 45000,
          riskScore: 20,
          riskLevel: 'Low',
          vaspName: 'Binance Central Sweeper',
          vaspCategory: 'Exchange Internal Aggregator',
          isSuspicious: false,
          role: 'Final Identified VASP Hot Wallet',
          firstSeen: '2019-06-15',
          lastActive: '2026-09-11 11:32:10 UTC'
        },
        {
          id: '0xA090e606E30bD747d4E6245a1517EbE430F0057e',
          label: 'Coinbase Custody',
          fullAddress: '0xA090e606E30bD747d4E6245a1517EbE430F0057e',
          type: 'vasp',
          hop: 3,
          balance: '8,450.00 ETH',
          txCount: 8200,
          riskScore: 15,
          riskLevel: 'Low',
          vaspName: 'Coinbase Institutional',
          vaspCategory: 'Regulated US VASP',
          isSuspicious: false,
          role: 'Secondary Identified Exchange Deposit',
          firstSeen: '2020-01-20',
          lastActive: '2026-09-11 11:15:22 UTC'
        }
      ];

      nodes.push(...hop3Wallets);

      links.push({
        source: hop2Wallets[0].id,
        target: hop3Wallets[0].id,
        amount: '38.50 ETH',
        amountUsd: '$103,950',
        timestamp: '2026-09-11 11:15:02 UTC',
        txHash: '0x3c4d5e...1a2b',
        isTracedPath: true,
        hop: 3
      });

      links.push({
        source: hop2Wallets[0].id,
        target: hop3Wallets[1].id,
        amount: '1.50 ETH',
        amountUsd: '$4,050',
        timestamp: '2026-09-11 11:18:40 UTC',
        txHash: '0x9e8d7c...6b5a',
        isTracedPath: false,
        hop: 3
      });

      // Hop 5 (extended hops if user selects 5)
      if (hopDepth >= 5) {
        const hop5Wallets = [
          {
            id: '0x503828976D22510aad0201ac7EC88293211A23Da',
            label: 'Cold Reserve Cold Storage',
            fullAddress: '0x503828976D22510aad0201ac7EC88293211A23Da',
            type: 'vasp',
            hop: 4,
            balance: '85,000.00 ETH',
            txCount: 1200,
            riskScore: 10,
            riskLevel: 'Low',
            vaspName: 'Binance Cold Vault',
            vaspCategory: 'Multi-Sig Cold Storage',
            isSuspicious: false,
            role: 'Institutional Cold Reserve',
            firstSeen: '2018-11-12',
            lastActive: '2026-09-11 11:40:00 UTC'
          }
        ];

        nodes.push(...hop5Wallets);

        links.push({
          source: hop3Wallets[0].id,
          target: hop5Wallets[0].id,
          amount: '35.00 ETH',
          amountUsd: '$94,500',
          timestamp: '2026-09-11 11:35:45 UTC',
          txHash: '0xfa8e7d...1b2c',
          isTracedPath: true,
          hop: 4
        });
      }
    }
  }

  return { nodes, links };
}
