/**
 * POLLN Agent Graph Evolution
 *
 * Dynamic restructuring of agent networks through:
 * - Synaptic pruning (removing weak connections)
 * - Connection grafting (forming new pathways)
 * - Spectral clustering (community detection)
 * - Structural plasticity (adaptive rewiring)
 *
 * Based on neuroscience principles of neural network optimization
 */

import { EventEmitter } from 'events';
import { HebbianLearning, SynapseState } from './learning.js';

// ============================================================================
// TYPES
// ============================================================================

/**
 * Pruning strategy options
 */
export type PruningStrategy =
  | 'threshold'      // Remove connections below weight threshold
  | 'age'            // Remove old unused connections
  | 'random'         // Random dropout for regularization
  | 'magnitude'      // Remove smallest magnitude weights
  | 'activity'       // Remove low-activity connections
  | 'combined';      // Combine multiple strategies

/**
 * Grafting strategy options
 */
export type GraftingStrategy =
  | 'random'         // Random new connections
  | 'similarity'     // Based on agent similarity
  | 'complementary'  // Connect complementary capabilities
  | 'gradient'       // Follow gradient of network improvement
  | 'heuristic';     // Rule-based connection formation

/**
 * Configuration for graph evolution
 */
export interface GraphEvolutionConfig {
  // Pruning parameters
  pruningThreshold: number;      // Weight threshold for pruning
  pruningInterval: number;       // MS between pruning cycles
  pruningStrategy: PruningStrategy;
  minSynapseAge: number;         // MS before synapse can be pruned
  maxPruningRate: number;        // Max fraction to prune per cycle

  // Grafting parameters
  graftingProbability: number;   // Probability of forming new connection
  graftingStrategy: GraftingStrategy;
  maxNewConnections: number;     // Max new connections per cycle
  connectionBias: number;        // Bias toward similar agents

  // Clustering parameters
  clusterResolution: number;     // Resolution parameter for community detection
  minClusterSize: number;        // Minimum agents per cluster
  clusterUpdateInterval: number; // MS between cluster updates

  // Plasticity parameters
  plasticityRate: number;        // Rate of structural changes
  stabilityThreshold: number;    // Network stability threshold
  homeostaticTarget: number;     // Target average connection strength
}

/**
 * Agent node in the graph
 */
export interface AgentNode {
  id: string;
  capabilities: Map<string, number>;
  activationHistory: number[];
  cluster: number | null;
  centrality: number;
}

/**
 * Edge in the agent graph
 */
export interface AgentEdge {
  source: string;
  target: string;
  weight: number;
  age: number;
  activityLevel: number;
  lastActive: number;
}

/**
 * Community cluster
 */
export interface AgentCluster {
  id: number;
  members: string[];
  cohesion: number;       // Internal connection density
  separation: number;     // Separation from other clusters
  modularity: number;     // Contribution to modularity
}

/**
 * Evolution statistics
 */
export interface EvolutionStats {
  totalNodes: number;
  totalEdges: number;
  avgDegree: number;
  clusteringCoeff: number;
  modularity: number;
  prunedThisCycle: number;
  graftedThisCycle: number;
  lastEvolution: number;
}

/**
 * Evolution event
 */
export interface EvolutionEvent {
  type: 'prune' | 'graft' | 'rewire' | 'cluster';
  timestamp: number;
  details: Record<string, unknown>;
}

// ============================================================================
// GRAPH EVOLUTION IMPLEMENTATION
// ============================================================================

/**
 * GraphEvolution - Manages dynamic restructuring of agent networks
 *
 * Implements structural plasticity based on:
 * 1. Activity-dependent pruning (use it or lose it)
 * 2. Hebbian grafting (wire together, fire together)
 * 3. Community detection (clustering by function)
 * 4. Homeostatic regulation (maintain network stability)
 */
export class GraphEvolution extends EventEmitter {
  private config: GraphEvolutionConfig;
  private hebbianLearning: HebbianLearning;
  private nodes: Map<string, AgentNode> = new Map();
  private edges: Map<string, AgentEdge> = new Map();
  private clusters: AgentCluster[] = [];
  private stats: EvolutionStats;
  private eventHistory: EvolutionEvent[] = [];
  private lastPruningTime: number = 0;
  private lastClusteringTime: number = 0;

  constructor(
    hebbianLearning: HebbianLearning,
    config?: Partial<GraphEvolutionConfig>
  ) {
    super();
    this.hebbianLearning = hebbianLearning;

    this.config = {
      pruningThreshold: 0.05,
      pruningInterval: 60000,      // 1 minute
      pruningStrategy: 'combined',
      minSynapseAge: 30000,        // 30 seconds
      maxPruningRate: 0.1,         // 10% max
      graftingProbability: 0.01,
      graftingStrategy: 'heuristic',
      maxNewConnections: 5,
      connectionBias: 0.3,
      clusterResolution: 1.0,
      minClusterSize: 2,
      clusterUpdateInterval: 300000, // 5 minutes
      plasticityRate: 0.001,
      stabilityThreshold: 0.8,
      homeostaticTarget: 0.5,
      ...config
    };

    this.stats = {
      totalNodes: 0,
      totalEdges: 0,
      avgDegree: 0,
      clusteringCoeff: 0,
      modularity: 0,
      prunedThisCycle: 0,
      graftedThisCycle: 0,
      lastEvolution: Date.now()
    };
  }

  /**
   * Register an agent in the graph
   */
  registerAgent(
    id: string,
    capabilities: Map<string, number> = new Map()
  ): void {
    if (this.nodes.has(id)) return;

    this.nodes.set(id, {
      id,
      capabilities,
      activationHistory: [],
      cluster: null,
      centrality: 0
    });

    this.stats.totalNodes = this.nodes.size;
    this.emit('agent_registered', { id });
  }

  /**
   * Unregister an agent from the graph
   */
  unregisterAgent(id: string): void {
    if (!this.nodes.has(id)) return;

    // Remove all edges involving this agent
    for (const [key, edge] of this.edges) {
      if (edge.source === id || edge.target === id) {
        this.edges.delete(key);
      }
    }

    this.nodes.delete(id);
    this.stats.totalNodes = this.nodes.size;
    this.stats.totalEdges = this.edges.size;
    this.emit('agent_unregistered', { id });
  }

  /**
   * Update edge based on synapse state
   */
  updateEdge(source: string, target: string, synapse: SynapseState): void {
    const key = `${source}->${target}`;

    this.edges.set(key, {
      source,
      target,
      weight: synapse.weight,
      age: Date.now() - synapse.lastCoactivated,
      activityLevel: synapse.coactivationCount,
      lastActive: synapse.lastCoactivated
    });

    this.stats.totalEdges = this.edges.size;
  }

  /**
   * Record agent activation
   */
  recordActivation(agentId: string, activationLevel: number): void {
    const node = this.nodes.get(agentId);
    if (!node) return;

    node.activationHistory.push(activationLevel);

    // Keep only recent history
    if (node.activationHistory.length > 100) {
      node.activationHistory.shift();
    }
  }

  /**
   * Run evolution cycle (pruning + grafting + clustering)
   */
  async evolve(): Promise<EvolutionStats> {
    const now = Date.now();

    // Pruning phase
    if (now - this.lastPruningTime >= this.config.pruningInterval) {
      this.stats.prunedThisCycle = await this.prune();
      this.lastPruningTime = now;
    }

    // Grafting phase
    this.stats.graftedThisCycle = await this.graft();

    // Clustering phase
    if (now - this.lastClusteringTime >= this.config.clusterUpdateInterval) {
      this.clusters = this.detectClusters();
      this.lastClusteringTime = now;
    }

    // Homeostatic regulation
    this.regulateHomeostasis();

    // Update stats
    this.updateStats();
    this.stats.lastEvolution = now;

    this.emit('evolution_complete', this.stats);
    return this.stats;
  }

  /**
   * Prune weak connections based on strategy
   */
  private async prune(): Promise<number> {
    const edgesToPrune: string[] = [];

    for (const [key, edge] of this.edges) {
      if (edge.age < this.config.minSynapseAge) continue;

      let shouldPrune = false;

      switch (this.config.pruningStrategy) {
        case 'threshold':
          shouldPrune = edge.weight < this.config.pruningThreshold;
          break;

        case 'age':
          // Prune old, weak connections
          shouldPrune = edge.age > 60000 && edge.activityLevel < 2;
          break;

        case 'random':
          // Random dropout (regularization)
          shouldPrune = Math.random() < 0.01 && edge.weight < 0.2;
          break;

        case 'magnitude':
          // Prune lowest magnitude weights
          // Handled separately below
          break;

        case 'activity':
          shouldPrune = edge.activityLevel < 1 && edge.age > 30000;
          break;

        case 'combined':
          shouldPrune = this.combinedPruningDecision(edge);
          break;
      }

      if (shouldPrune) {
        edgesToPrune.push(key);
      }
    }

    // For magnitude-based pruning, take bottom percentile
    if (this.config.pruningStrategy === 'magnitude') {
      const weights = Array.from(this.edges.entries())
        .sort((a, b) => a[1].weight - b[1].weight);

      const toPrune = Math.min(
        Math.floor(weights.length * this.config.maxPruningRate),
        weights.length
      );

      for (let i = 0; i < toPrune; i++) {
        if (weights[i][1].age >= this.config.minSynapseAge) {
          edgesToPrune.push(weights[i][0]);
        }
      }
    }

    // Apply max pruning rate
    const maxPrune = Math.floor(
      this.edges.size * this.config.maxPruningRate
    );
    const toRemove = edgesToPrune.slice(0, maxPrune);

    // Remove edges
    for (const key of toRemove) {
      this.edges.delete(key);
      this.recordEvent('prune', { edge: key });
    }

    return toRemove.length;
  }

  /**
   * Combined pruning decision using multiple factors
   */
  private combinedPruningDecision(edge: AgentEdge): boolean {
    const factors = {
      weight: edge.weight < this.config.pruningThreshold ? 1 : 0,
      activity: edge.activityLevel < 2 ? 1 : 0,
      age: edge.age > 60000 ? 1 : 0
    };

    const score = factors.weight * 0.5 + factors.activity * 0.3 + factors.age * 0.2;
    return score > 0.5;
  }

  /**
   * Graft new connections based on strategy
   */
  private async graft(): Promise<number> {
    if (Math.random() > this.config.graftingProbability) {
      return 0;
    }

    const newConnections: Array<{ source: string; target: string; weight: number }> = [];
    const nodeIds = Array.from(this.nodes.keys());

    if (nodeIds.length < 2) return 0;

    for (let i = 0; i < this.config.maxNewConnections; i++) {
      const source = nodeIds[Math.floor(Math.random() * nodeIds.length)];
      let target: string;

      switch (this.config.graftingStrategy) {
        case 'random':
          target = this.selectRandomTarget(source, nodeIds);
          break;

        case 'similarity':
          target = this.selectSimilarTarget(source);
          break;

        case 'complementary':
          target = this.selectComplementaryTarget(source);
          break;

        case 'gradient':
          target = this.selectGradientTarget(source);
          break;

        case 'heuristic':
        default:
          target = this.selectHeuristicTarget(source, nodeIds);
          break;
      }

      if (target && !this.edgeExists(source, target)) {
        newConnections.push({
          source,
          target,
          weight: this.config.homeostaticTarget
        });
      }
    }

    // Create new edges
    for (const conn of newConnections) {
      const key = `${conn.source}->${conn.target}`;
      this.edges.set(key, {
        source: conn.source,
        target: conn.target,
        weight: conn.weight,
        age: 0,
        activityLevel: 0,
        lastActive: Date.now()
      });

      this.recordEvent('graft', conn);
    }

    return newConnections.length;
  }

  /**
   * Select random target for new connection
   */
  private selectRandomTarget(source: string, nodeIds: string[]): string {
    let target: string;
    do {
      target = nodeIds[Math.floor(Math.random() * nodeIds.length)];
    } while (target === source);
    return target;
  }

  /**
   * Select similar target based on capabilities
   */
  private selectSimilarTarget(source: string): string {
    const sourceNode = this.nodes.get(source);
    if (!sourceNode) return '';

    let bestTarget = '';
    let bestSimilarity = -Infinity;

    for (const [id, node] of this.nodes) {
      if (id === source || this.edgeExists(source, id)) continue;

      const similarity = this.computeCapabilitySimilarity(
        sourceNode.capabilities,
        node.capabilities
      );

      // Add some randomness
      const adjusted = similarity + (Math.random() - 0.5) * this.config.connectionBias;

      if (adjusted > bestSimilarity) {
        bestSimilarity = adjusted;
        bestTarget = id;
      }
    }

    return bestTarget;
  }

  /**
   * Select complementary target (different capabilities)
   */
  private selectComplementaryTarget(source: string): string {
    const sourceNode = this.nodes.get(source);
    if (!sourceNode) return '';

    let bestTarget = '';
    let bestComplementarity = -Infinity;

    for (const [id, node] of this.nodes) {
      if (id === source || this.edgeExists(source, id)) continue;

      const complementarity = this.computeComplementarity(
        sourceNode.capabilities,
        node.capabilities
      );

      if (complementarity > bestComplementarity) {
        bestComplementarity = complementarity;
        bestTarget = id;
      }
    }

    return bestTarget;
  }

  /**
   * Select target following gradient of network improvement
   */
  private selectGradientTarget(source: string): string {
    // Simplified: prefer connecting to high-centrality nodes
    const nodeIds = Array.from(this.nodes.keys());
    const candidates = nodeIds.filter(id =>
      id !== source && !this.edgeExists(source, id)
    );

    if (candidates.length === 0) return '';

    // Sort by centrality and pick from top with some randomness
    candidates.sort((a, b) => {
      const nodeA = this.nodes.get(a)!;
      const nodeB = this.nodes.get(b)!;
      return nodeB.centrality - nodeA.centrality;
    });

    const topN = Math.min(3, candidates.length);
    return candidates[Math.floor(Math.random() * topN)];
  }

  /**
   * Heuristic target selection combining multiple factors
   */
  private selectHeuristicTarget(source: string, nodeIds: string[]): string {
    const sourceNode = this.nodes.get(source);
    if (!sourceNode) return this.selectRandomTarget(source, nodeIds);

    interface Candidate {
      id: string;
      score: number;
    }

    const candidates: Candidate[] = [];

    for (const [id, node] of this.nodes) {
      if (id === source || this.edgeExists(source, id)) continue;

      const similarity = this.computeCapabilitySimilarity(
        sourceNode.capabilities,
        node.capabilities
      );

      const complementarity = this.computeComplementarity(
        sourceNode.capabilities,
        node.capabilities
      );

      // Combine factors
      const score =
        similarity * 0.3 +
        complementarity * 0.3 +
        node.centrality * 0.2 +
        Math.random() * 0.2;

      candidates.push({ id, score });
    }

    if (candidates.length === 0) return '';

    // Pick highest score
    candidates.sort((a, b) => b.score - a.score);
    return candidates[0].id;
  }

  /**
   * Check if edge exists
   */
  private edgeExists(source: string, target: string): boolean {
    return this.edges.has(`${source}->${target}`) ||
           this.edges.has(`${target}->${source}`);
  }

  /**
   * Compute capability similarity (cosine similarity)
   */
  private computeCapabilitySimilarity(
    caps1: Map<string, number>,
    caps2: Map<string, number>
  ): number {
    let dotProduct = 0;
    let norm1 = 0;
    let norm2 = 0;

    const allKeys = new Set([...caps1.keys(), ...caps2.keys()]);

    for (const key of allKeys) {
      const v1 = caps1.get(key) || 0;
      const v2 = caps2.get(key) || 0;

      dotProduct += v1 * v2;
      norm1 += v1 * v1;
      norm2 += v2 * v2;
    }

    if (norm1 === 0 || norm2 === 0) return 0;
    return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
  }

  /**
   * Compute complementarity (how well capabilities complement each other)
   */
  private computeComplementarity(
    caps1: Map<string, number>,
    caps2: Map<string, number>
  ): number {
    // High complementarity = one has what the other lacks
    let complement = 0;
    let count = 0;

    const allKeys = new Set([...caps1.keys(), ...caps2.keys()]);

    for (const key of allKeys) {
      const v1 = caps1.get(key) || 0;
      const v2 = caps2.get(key) || 0;

      // XOR-like complementarity
      complement += Math.abs(v1 - v2) * Math.min(v1, v2);
      count++;
    }

    return count > 0 ? complement / count : 0;
  }

  /**
   * Detect communities using spectral clustering (simplified)
   */
  private detectClusters(): AgentCluster[] {
    if (this.nodes.size < this.config.minClusterSize) {
      return [];
    }

    // Build adjacency matrix
    const nodeIds = Array.from(this.nodes.keys());
    const n = nodeIds.length;
    const adjacency: number[][] = [];

    for (let i = 0; i < n; i++) {
      adjacency[i] = [];
      for (let j = 0; j < n; j++) {
        const key = `${nodeIds[i]}->${nodeIds[j]}`;
        const edge = this.edges.get(key);
        adjacency[i][j] = edge ? edge.weight : 0;
      }
    }

    // Simplified community detection using modularity optimization
    const clusters = this.louvainClustering(nodeIds, adjacency);

    // Update node cluster assignments
    for (let i = 0; i < clusters.length; i++) {
      for (const nodeId of clusters[i].members) {
        const node = this.nodes.get(nodeId);
        if (node) {
          node.cluster = clusters[i].id;
        }
      }
    }

    // Compute cluster metrics
    for (const cluster of clusters) {
      cluster.cohesion = this.computeCohesion(cluster, adjacency, nodeIds);
      cluster.separation = this.computeSeparation(cluster, adjacency, nodeIds);
    }

    return clusters;
  }

  /**
   * Simplified Louvain clustering algorithm
   */
  private louvainClustering(
    nodeIds: string[],
    adjacency: number[][]
  ): AgentCluster[] {
    const n = nodeIds.length;

    // Start with each node in its own cluster
    const assignments: number[] = nodeIds.map((_, i) => i);
    let improved = true;
    let iterations = 0;
    const maxIterations = 100;

    while (improved && iterations < maxIterations) {
      improved = false;
      iterations++;

      for (let i = 0; i < n; i++) {
        const currentCluster = assignments[i];
        let bestCluster = currentCluster;
        let bestModularityGain = 0;

        // Try moving to neighboring clusters
        for (let j = 0; j < n; j++) {
          if (adjacency[i][j] > 0) {
            const targetCluster = assignments[j];
            if (targetCluster !== currentCluster) {
              const gain = this.computeModularityGain(
                i, currentCluster, targetCluster, assignments, adjacency
              );

              if (gain > bestModularityGain) {
                bestModularityGain = gain;
                bestCluster = targetCluster;
              }
            }
          }
        }

        if (bestCluster !== currentCluster) {
          assignments[i] = bestCluster;
          improved = true;
        }
      }
    }

    // Convert assignments to clusters
    const clusterMap = new Map<number, string[]>();
    for (let i = 0; i < n; i++) {
      const clusterId = assignments[i];
      if (!clusterMap.has(clusterId)) {
        clusterMap.set(clusterId, []);
      }
      clusterMap.get(clusterId)!.push(nodeIds[i]);
    }

    // Filter and create cluster objects
    const clusters: AgentCluster[] = [];
    let clusterIndex = 0;

    for (const [_, members] of clusterMap) {
      if (members.length >= this.config.minClusterSize) {
        clusters.push({
          id: clusterIndex++,
          members,
          cohesion: 0,
          separation: 0,
          modularity: 0
        });
      }
    }

    return clusters;
  }

  /**
   * Compute modularity gain from moving a node
   */
  private computeModularityGain(
    nodeIndex: number,
    fromCluster: number,
    toCluster: number,
    assignments: number[],
    adjacency: number[][]
  ): number {
    const n = adjacency.length;
    const resolution = this.config.clusterResolution;

    // Compute degree
    let ki = 0;
    for (let j = 0; j < n; j++) {
      ki += adjacency[nodeIndex][j] + adjacency[j][nodeIndex];
    }

    // Sum of edges to each cluster
    let sumToFrom = 0;
    let sumToTo = 0;

    for (let j = 0; j < n; j++) {
      if (assignments[j] === fromCluster) {
        sumToFrom += adjacency[nodeIndex][j] + adjacency[j][nodeIndex];
      }
      if (assignments[j] === toCluster) {
        sumToTo += adjacency[nodeIndex][j] + adjacency[j][nodeIndex];
      }
    }

    // Simplified modularity gain
    return (sumToTo - sumToFrom) * resolution / ki;
  }

  /**
   * Compute cluster cohesion (internal density)
   */
  private computeCohesion(
    cluster: AgentCluster,
    adjacency: number[][],
    nodeIds: string[]
  ): number {
    if (cluster.members.length < 2) return 0;

    let internalWeight = 0;
    let possibleEdges = cluster.members.length * (cluster.members.length - 1);

    for (const source of cluster.members) {
      for (const target of cluster.members) {
        if (source !== target) {
          const i = nodeIds.indexOf(source);
          const j = nodeIds.indexOf(target);
          internalWeight += adjacency[i][j];
        }
      }
    }

    return internalWeight / possibleEdges;
  }

  /**
   * Compute cluster separation (external sparsity)
   */
  private computeSeparation(
    cluster: AgentCluster,
    adjacency: number[][],
    nodeIds: string[]
  ): number {
    if (cluster.members.length === nodeIds.length) return 1;

    let externalWeight = 0;
    let possibleExternal = 0;

    const clusterSet = new Set(cluster.members);

    for (const source of cluster.members) {
      for (let j = 0; j < nodeIds.length; j++) {
        const target = nodeIds[j];
        if (!clusterSet.has(target)) {
          const i = nodeIds.indexOf(source);
          externalWeight += adjacency[i][j];
          possibleExternal++;
        }
      }
    }

    if (possibleExternal === 0) return 1;
    return 1 - (externalWeight / possibleExternal);
  }

  /**
   * Regulate network to maintain homeostasis
   */
  private regulateHomeostasis(): void {
    if (this.edges.size === 0) return;

    // Compute average weight
    let totalWeight = 0;
    for (const edge of this.edges.values()) {
      totalWeight += edge.weight;
    }
    const avgWeight = totalWeight / this.edges.size;

    // Adjust all weights toward target
    const adjustment = (this.config.homeostaticTarget - avgWeight) *
                       this.config.plasticityRate;

    for (const edge of this.edges.values()) {
      edge.weight = Math.max(0.01, Math.min(1.0, edge.weight + adjustment));
    }
  }

  /**
   * Update statistics
   */
  private updateStats(): void {
    const n = this.nodes.size;
    const m = this.edges.size;

    this.stats.totalNodes = n;
    this.stats.totalEdges = m;
    this.stats.avgDegree = n > 0 ? (2 * m) / n : 0;

    // Compute clustering coefficient
    this.stats.clusteringCoeff = this.computeClusteringCoefficient();

    // Compute modularity
    this.stats.modularity = this.computeModularity();
  }

  /**
   * Compute average clustering coefficient
   */
  private computeClusteringCoefficient(): number {
    if (this.nodes.size < 3) return 0;

    let totalCoeff = 0;
    let count = 0;

    for (const nodeId of this.nodes.keys()) {
      const neighbors = this.getNeighbors(nodeId);
      if (neighbors.length < 2) continue;

      let triangles = 0;
      let possibleTriangles = (neighbors.length * (neighbors.length - 1)) / 2;

      for (let i = 0; i < neighbors.length; i++) {
        for (let j = i + 1; j < neighbors.length; j++) {
          if (this.edgeExists(neighbors[i], neighbors[j])) {
            triangles++;
          }
        }
      }

      if (possibleTriangles > 0) {
        totalCoeff += triangles / possibleTriangles;
        count++;
      }
    }

    return count > 0 ? totalCoeff / count : 0;
  }

  /**
   * Get neighbors of a node
   */
  private getNeighbors(nodeId: string): string[] {
    const neighbors: string[] = [];

    for (const [key, edge] of this.edges) {
      if (edge.source === nodeId) {
        neighbors.push(edge.target);
      } else if (edge.target === nodeId) {
        neighbors.push(edge.source);
      }
    }

    return neighbors;
  }

  /**
   * Compute network modularity
   */
  private computeModularity(): number {
    if (this.clusters.length === 0) return 0;

    let totalModularity = 0;
    for (const cluster of this.clusters) {
      totalModularity += cluster.cohesion - cluster.separation;
    }

    return totalModularity / Math.max(1, this.clusters.length);
  }

  /**
   * Record evolution event
   */
  private recordEvent(type: EvolutionEvent['type'], details: Record<string, unknown>): void {
    this.eventHistory.push({
      type,
      timestamp: Date.now(),
      details
    });

    // Keep only recent events
    if (this.eventHistory.length > 1000) {
      this.eventHistory.shift();
    }
  }

  // =========================================================================
  // PUBLIC API
  // =========================================================================

  /**
   * Get current statistics
   */
  getStats(): EvolutionStats {
    return { ...this.stats };
  }

  /**
   * Get all clusters
   */
  getClusters(): AgentCluster[] {
    return [...this.clusters];
  }

  /**
   * Get node information
   */
  getNode(id: string): AgentNode | undefined {
    return this.nodes.get(id);
  }

  /**
   * Get all edges
   */
  getEdges(): AgentEdge[] {
    return Array.from(this.edges.values());
  }

  /**
   * Get event history
   */
  getEventHistory(): EvolutionEvent[] {
    return [...this.eventHistory];
  }

  /**
   * Get configuration
   */
  getConfig(): GraphEvolutionConfig {
    return { ...this.config };
  }

  /**
   * Update configuration
   */
  updateConfig(config: Partial<GraphEvolutionConfig>): void {
    this.config = { ...this.config, ...config };
  }
}
