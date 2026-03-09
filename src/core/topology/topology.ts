/**
 * Topology Builder for POLLN Colonies
 *
 * Builds agent connection topologies from template definitions.
 * Generates network graphs using various topology types.
 */

import { TopologyTemplate } from './templates/types';

/**
 * Adjacency list representation of a graph
 */
export type AdjacencyList = Record<string, number[]>;

/**
 * Build agent topology from template
 *
 * @param agentIds - List of agent IDs
 * @param template - Topology template to use
 * @returns Adjacency list of connections
 */
export function buildTopology(
  agentIds: string[],
  template: TopologyTemplate
): Map<string, string[]> {
  const n = agentIds.length;

  // Generate graph topology
  const adjacency = generateGraph(
    n,
    template.topologyType,
    template.params
  );

  // Convert numeric indices to agent IDs
  const connections = new Map<string, string[]>();

  for (const [sourceIdx, targetIndices] of Object.entries(adjacency)) {
    const sourceId = agentIds[parseInt(sourceIdx)];

    if (sourceId && targetIndices.length > 0) {
      const targetIds = targetIndices
        .map(idx => agentIds[idx])
        .filter(id => id !== undefined) as string[];

      connections.set(sourceId, targetIds);
    }
  }

  return connections;
}

/**
 * Generate graph from template parameters
 *
 * @param n - Number of nodes
 * @param type - Topology type
 * @param params - Template parameters
 * @returns Adjacency list (0-indexed)
 */
function generateGraph(
  n: number,
  type: string,
  params: Record<string, any>
): AdjacencyList {
  // Initialize empty graph
  const adjacency: AdjacencyList = {};
  for (let i = 0; i < n; i++) {
    adjacency[i] = [];
  }

  switch (type) {
    case 'watts_strogatz':
      return wattsStrogatz(n, params.k || 4, params.p || 0.1);
    case 'barabasi_albert':
      return barabasiAlbert(n, params.m || 2);
    case 'modular':
      return modular(n, params.modules || 5);
    case 'hierarchical':
      return hierarchical(n, params.levels || 3);
    case 'two_tier':
      return twoTier(n, params.k || 4);
    case 'three_tier':
      return threeTier(n);
    case 'erdos_renyi':
      return erdosRenyi(n, params.p || 0.1);
    case 'regular_lattice':
      return regularLattice(n);
    case 'random_geometric':
      return randomGeometric(n, params.k || 6);
    case 'hybrid_small_world_sf':
      return hybridSmallWorldSF(n, params.k || 6, params.p || 0.1);
    default:
      throw new Error(`Unknown topology type: ${type}`);
  }
}

/**
 * Watts-Strogatz small-world topology
 */
function wattsStrogatz(n: number, k: number, p: number): AdjacencyList {
  const adjacency: AdjacencyList = {};

  // Initialize empty
  for (let i = 0; i < n; i++) {
    adjacency[i] = [];
  }

  // Create ring lattice
  for (let i = 0; i < n; i++) {
    for (let j = 1; j <= k / 2; j++) {
      const neighbor = (i + j) % n;
      adjacency[i].push(neighbor);
      adjacency[neighbor].push(i);
    }
  }

  // Rewire edges with probability p
  for (let i = 0; i < n; i++) {
    const targets = [...adjacency[i]];

    for (const j of targets) {
      if (j > i && Math.random() < p) {
        // Remove edge
        adjacency[i] = adjacency[i].filter((x) => x !== j);
        adjacency[j] = adjacency[j].filter((x) => x !== i);

        // Add new edge to random node
        let newNeighbor = Math.floor(Math.random() * n);
        let attempts = 0;
        while (
          (newNeighbor === i || adjacency[i].includes(newNeighbor)) &&
          attempts < 10
        ) {
          newNeighbor = Math.floor(Math.random() * n);
          attempts++;
        }

        if (newNeighbor !== i && !adjacency[i].includes(newNeighbor)) {
          adjacency[i].push(newNeighbor);
          adjacency[newNeighbor].push(i);
        }
      }
    }
  }

  return adjacency;
}

/**
 * Barabási-Albert scale-free topology
 */
function barabasiAlbert(n: number, m: number): AdjacencyList {
  const adjacency: AdjacencyList = {};

  if (n <= m) {
    // Complete graph for small n
    for (let i = 0; i < n; i++) {
      adjacency[i] = [];
      for (let j = 0; j < n; j++) {
        if (i !== j) {
          adjacency[i].push(j);
        }
      }
    }
    return adjacency;
  }

  // Initialize with small clique
  for (let i = 0; i < m; i++) {
    adjacency[i] = [];
    for (let j = 0; j < m; j++) {
      if (i !== j) {
        adjacency[i].push(j);
      }
    }
  }

  // Add nodes with preferential attachment
  for (let i = m; i < n; i++) {
    adjacency[i] = [];

    // Calculate degrees
    const degrees: number[] = [];
    let totalDegree = 0;
    for (let j = 0; j < i; j++) {
      degrees[j] = adjacency[j].length;
      totalDegree += degrees[j];
    }

    // Add m edges with probability proportional to degree
    const connected = new Set<number>();
    while (connected.size < m && connected.size < i) {
      const r = Math.random() * totalDegree;
      let sum = 0;

      for (let j = 0; j < i; j++) {
        sum += degrees[j];
        if (sum >= r && !connected.has(j)) {
          adjacency[i].push(j);
          adjacency[j].push(i);
          connected.add(j);
          break;
        }
      }
    }
  }

  return adjacency;
}

/**
 * Modular topology
 */
function modular(n: number, modules: number): AdjacencyList {
  const adjacency: AdjacencyList = {};
  const moduleSize = Math.floor(n / modules);

  // Initialize
  for (let i = 0; i < n; i++) {
    adjacency[i] = [];
  }

  // Create modules
  for (let m = 0; m < modules; m++) {
    const startIdx = m * moduleSize;
    const endIdx = Math.min(startIdx + moduleSize, n);
    const size = endIdx - startIdx;

    if (size < 2) continue;

    // Small-world within module
    const k = Math.min(4, size - 1);
    const moduleAdj = wattsStrogatz(size, k, 0.1);

    for (const [src, targets] of Object.entries(moduleAdj)) {
      const realSrc = startIdx + parseInt(src);
      adjacency[realSrc] = [
        ...adjacency[realSrc],
        ...targets.map((t) => startIdx + t)
      ];
    }
  }

  // Add bridge connections between modules
  for (let m = 0; m < modules - 1; m++) {
    const bridgeCount = 2;

    for (let b = 0; b < bridgeCount; b++) {
      const srcModuleStart = m * moduleSize;
      const dstModuleStart = (m + 1) * moduleSize;

      const srcIdx = srcModuleStart + Math.floor(Math.random() * Math.min(moduleSize, n - srcModuleStart));
      const dstIdx = dstModuleStart + Math.floor(Math.random() * Math.min(moduleSize, n - dstModuleStart));

      if (srcIdx < n && dstIdx < n && !adjacency[srcIdx].includes(dstIdx)) {
        adjacency[srcIdx].push(dstIdx);
        adjacency[dstIdx].push(srcIdx);
      }
    }
  }

  return adjacency;
}

/**
 * Hierarchical topology
 */
function hierarchical(n: number, levels: number): AdjacencyList {
  const adjacency: AdjacencyList = {};
  const nodesPerLevel: number[] = [];

  // Calculate nodes per level
  let remaining = n;
  for (let l = 0; l < levels; l++) {
    if (l === levels - 1) {
      nodesPerLevel.push(remaining);
    } else {
      const count = Math.max(1, Math.floor(remaining / 4));
      nodesPerLevel.push(count);
      remaining -= count;
    }
  }

  // Initialize
  for (let i = 0; i < n; i++) {
    adjacency[i] = [];
  }

  // Build hierarchy
  let levelStart = 0;
  const upperNodes: number[] = [];

  for (let levelIdx = 0; levelIdx < levels; levelIdx++) {
    const count = nodesPerLevel[levelIdx];
    const levelNodes: number[] = [];

    for (let i = 0; i < count; i++) {
      levelNodes.push(levelStart + i);
    }

    if (levelIdx === 0) {
      // Top level: fully connected
      for (const i of levelNodes) {
        for (const j of levelNodes) {
          if (i < j && !adjacency[i].includes(j)) {
            adjacency[i].push(j);
            adjacency[j].push(i);
          }
        }
      }
      upperNodes.push(...levelNodes);
    } else {
      // Connect to upper level
      for (const node of levelNodes) {
        const numConnections = Math.min(upperNodes.length, 3);
        const targets = upperNodes.slice(0, numConnections);

        for (const target of targets) {
          if (!adjacency[node].includes(target)) {
            adjacency[node].push(target);
            adjacency[target].push(node);
          }
        }
      }

      // Some within-level connections
      for (const i of levelNodes) {
        for (const j of levelNodes) {
          if (i < j && Math.random() < 0.3 && !adjacency[i].includes(j)) {
            adjacency[i].push(j);
            adjacency[j].push(i);
          }
        }
      }

      upperNodes.push(...levelNodes.slice(0, Math.max(1, Math.floor(levelNodes.length / 4))));
    }

    levelStart += count;
  }

  return adjacency;
}

/**
 * Two-tier topology
 */
function twoTier(n: number, k: number): AdjacencyList {
  const adjacency: AdjacencyList = {};
  const coreSize = Math.max(3, Math.floor(n * 0.2));

  // Initialize
  for (let i = 0; i < n; i++) {
    adjacency[i] = [];
  }

  // Core tier: fully connected
  for (let i = 0; i < coreSize; i++) {
    for (let j = i + 1; j < coreSize; j++) {
      adjacency[i].push(j);
      adjacency[j].push(i);
    }
  }

  // Edge tier: connect to core
  for (let i = coreSize; i < n; i++) {
    const numConnections = Math.min(k, coreSize);
    const targets = [];

    for (let j = 0; j < numConnections; j++) {
      targets.push(j);
    }

    for (const target of targets) {
      adjacency[i].push(target);
      adjacency[target].push(i);
    }
  }

  // Some edge-to-edge connections
  for (let i = coreSize; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      if (Math.random() < 0.1) {
        adjacency[i].push(j);
        adjacency[j].push(i);
      }
    }
  }

  return adjacency;
}

/**
 * Three-tier topology
 */
function threeTier(n: number): AdjacencyList {
  const adjacency: AdjacencyList = {};

  const coreSize = Math.max(3, Math.floor(n * 0.1));
  const aggSize = Math.max(5, Math.floor(n * 0.3));
  const edgeSize = n - coreSize - aggSize;

  if (edgeSize < 1) {
    // Fall back to two-tier
    return twoTier(n, 4);
  }

  // Initialize
  for (let i = 0; i < n; i++) {
    adjacency[i] = [];
  }

  // Core tier: fully connected
  for (let i = 0; i < coreSize; i++) {
    for (let j = i + 1; j < coreSize; j++) {
      adjacency[i].push(j);
      adjacency[j].push(i);
    }
  }

  // Aggregation tier: connect to core
  for (let i = coreSize; i < coreSize + aggSize; i++) {
    const numConnections = Math.min(3, coreSize);
    for (let j = 0; j < numConnections; j++) {
      adjacency[i].push(j);
      adjacency[j].push(i);
    }
  }

  // Within aggregation tier
  for (let i = coreSize; i < coreSize + aggSize; i++) {
    for (let j = i + 1; j < coreSize + aggSize; j++) {
      if (Math.random() < 0.3) {
        adjacency[i].push(j);
        adjacency[j].push(i);
      }
    }
  }

  // Edge tier: connect to aggregation
  for (let i = coreSize + aggSize; i < n; i++) {
    const numConnections = Math.min(2, aggSize);
    for (let j = 0; j < numConnections; j++) {
      const target = coreSize + j;
      adjacency[i].push(target);
      adjacency[target].push(i);
    }
  }

  return adjacency;
}

/**
 * Regular lattice topology
 */
function regularLattice(n: number): AdjacencyList {
  const adjacency: AdjacencyList = {};

  // Try to create 2D grid
  const side = Math.floor(Math.sqrt(n));

  if (side * side === n) {
    // Perfect 2D grid
    for (let i = 0; i < n; i++) {
      adjacency[i] = [];
      const row = Math.floor(i / side);
      const col = i % side;

      // Connect to neighbors
      if (col > 0) {
        adjacency[i].push(i - 1);
        adjacency[i - 1].push(i);
      }
      if (col < side - 1) {
        adjacency[i].push(i + 1);
        adjacency[i + 1].push(i);
      }
      if (row > 0) {
        adjacency[i].push(i - side);
        adjacency[i - side].push(i);
      }
      if (row < side - 1) {
        adjacency[i].push(i + side);
        adjacency[i + side].push(i);
      }
    }
  } else {
    // Fallback to ring lattice
    const k = 4;
    for (let i = 0; i < n; i++) {
      adjacency[i] = [];
      for (let j = 1; j <= k / 2; j++) {
        const neighbor = (i + j) % n;
        adjacency[i].push(neighbor);
        adjacency[neighbor].push(i);
      }
    }
  }

  return adjacency;
}

/**
 * Erdős-Rényi random topology
 */
function erdosRenyi(n: number, p: number): AdjacencyList {
  const adjacency: AdjacencyList = {};

  // Initialize
  for (let i = 0; i < n; i++) {
    adjacency[i] = [];
  }

  // Add edges with probability p
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      if (Math.random() < p) {
        adjacency[i].push(j);
        adjacency[j].push(i);
      }
    }
  }

  return adjacency;
}

/**
 * Random geometric topology
 */
function randomGeometric(n: number, k: number): AdjacencyList {
  const adjacency: AdjacencyList = {};

  // Initialize
  for (let i = 0; i < n; i++) {
    adjacency[i] = [];
  }

  // Place nodes randomly in unit square
  const points: [number, number][] = [];
  for (let i = 0; i < n; i++) {
    points.push([Math.random(), Math.random()]);
  }

  // Calculate radius for average degree ~k
  const radius = Math.sqrt(k / (n * Math.PI));

  // Connect nodes within radius
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const dx = points[i][0] - points[j][0];
      const dy = points[i][1] - points[j][1];
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance <= radius) {
        adjacency[i].push(j);
        adjacency[j].push(i);
      }
    }
  }

  return adjacency;
}

/**
 * Hybrid small-world + scale-free topology
 */
function hybridSmallWorldSF(n: number, k: number, p: number): AdjacencyList {
  // Start with Watts-Strogatz
  const adjacency = wattsStrogatz(n, k, p);

  // Add scale-free characteristics by enhancing high-degree nodes
  const degrees: number[] = [];
  for (let i = 0; i < n; i++) {
    degrees[i] = adjacency[i].length;
  }

  // Add extra edges to high-degree nodes
  const numExtraEdges = Math.floor(n * 0.1);

  for (let e = 0; e < numExtraEdges; e++) {
    // Select node with probability proportional to degree
    const totalDegree = degrees.reduce((a, b) => a + b, 0);
    let r = Math.random() * totalDegree;
    let node1 = 0;

    for (let i = 0; i < n; i++) {
      r -= degrees[i];
      if (r <= 0) {
        node1 = i;
        break;
      }
    }

    // Find non-neighbor
    const nonNeighbors: number[] = [];
    for (let j = 0; j < n; j++) {
      if (j !== node1 && !adjacency[node1].includes(j)) {
        nonNeighbors.push(j);
      }
    }

    if (nonNeighbors.length > 0) {
      const node2 = nonNeighbors[Math.floor(Math.random() * nonNeighbors.length)];
      adjacency[node1].push(node2);
      adjacency[node2].push(node1);
      degrees[node1]++;
      degrees[node2]++;
    }
  }

  return adjacency;
}

/**
 * Validate topology connectivity
 *
 * @param adjacency - Adjacency list to validate
 * @returns True if graph is connected
 */
export function isConnected(adjacency: AdjacencyList): boolean {
  const nodes = Object.keys(adjacency).map(Number);
  if (nodes.length === 0) return true;

  const visited = new Set<number>();
  const queue = [nodes[0]];

  while (queue.length > 0) {
    const node = queue.shift()!;
    if (visited.has(node)) continue;

    visited.add(node);
    queue.push(...adjacency[node].filter((n) => !visited.has(n)));
  }

  return visited.size === nodes.length;
}

/**
 * Calculate average path length
 *
 * @param adjacency - Adjacency list
 * @returns Average shortest path length
 */
export function averagePathLength(adjacency: AdjacencyList): number {
  const nodes = Object.keys(adjacency).map(Number);
  if (nodes.length === 0) return 0;

  let totalPathLength = 0;
  let pathCount = 0;

  for (const source of nodes) {
    const distances = new Map<number, number>();
    const queue = [source];
    distances.set(source, 0);

    while (queue.length > 0) {
      const node = queue.shift()!;

      for (const neighbor of adjacency[node]) {
        if (!distances.has(neighbor)) {
          distances.set(neighbor, distances.get(node)! + 1);
          queue.push(neighbor);
        }
      }
    }

    for (const [node, distance] of distances) {
      if (node > source) {
        totalPathLength += distance;
        pathCount++;
      }
    }
  }

  return pathCount > 0 ? totalPathLength / pathCount : 0;
}

/**
 * Calculate clustering coefficient
 *
 * @param adjacency - Adjacency list
 * @returns Average clustering coefficient
 */
export function clusteringCoefficient(adjacency: AdjacencyList): number {
  const nodes = Object.keys(adjacency).map(Number);
  if (nodes.length === 0) return 0;

  let totalClustering = 0;

  for (const node of nodes) {
    const neighbors = adjacency[node];
    const k = neighbors.length;

    if (k < 2) {
      totalClustering += 0;
      continue;
    }

    // Count triangles
    let triangles = 0;
    for (let i = 0; i < k; i++) {
      for (let j = i + 1; j < k; j++) {
        if (adjacency[neighbors[i]].includes(neighbors[j])) {
          triangles++;
        }
      }
    }

    // Possible triangles
    const possibleTriangles = (k * (k - 1)) / 2;
    totalClustering += triangles / possibleTriangles;
  }

  return totalClustering / nodes.length;
}
