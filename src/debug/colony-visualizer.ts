/**
 * Colony Visualizer
 *
 * Provides graph visualization capabilities for colony structure,
 * agent relationships, communication flows, and resource usage.
 */

import type {
  GraphVisualization,
  GraphNode,
  GraphEdge,
  Position,
  GraphLayout,
  GraphCluster,
  VisualizationMetadata,
} from './types.js';
import { DebugError } from './types.js';

// ============================================================================
// ColonyVisualizer Class
// ============================================================================

/**
 * Visualizer for colony graph structure and dynamics
 */
export class ColonyVisualizer {
  private visualizationCache: Map<string, GraphVisualization> = new Map();

  /**
   * Visualize a colony's graph structure
   *
   * @param colonyId - Colony ID
   * @param colony - Colony instance
   * @param agents - Map of agent instances
   * @param options - Visualization options
   * @returns Graph visualization
   */
  async visualize(
    colonyId: string,
    colony: any,
    agents: Map<string, any>,
    options: VisualizationOptions = {}
  ): Promise<GraphVisualization> {
    const {
      layout = 'force',
      includeClusters = true,
      dimensions = { width: 1000, height: 800 },
    } = options;

    // Extract nodes from agents
    const nodes = this.extractNodes(agents);

    // Extract edges from connections
    const edges = this.extractEdges(agents);

    // Apply layout algorithm
    const layoutInfo = this.applyLayout(nodes, edges, layout, dimensions);

    // Update node positions from layout
    nodes.forEach(node => {
      const pos = layoutInfo.positions?.get(node.id);
      if (pos) {
        node.position = pos;
      }
    });

    // Compute clusters if requested
    let clusters: GraphCluster[] | undefined;
    if (includeClusters) {
      clusters = this.computeClusters(nodes, edges);
    }

    // Compute metadata
    const metadata = this.computeMetadata(nodes, edges, clusters);

    const visualization: GraphVisualization = {
      colonyId,
      nodes,
      edges,
      layout: layoutInfo,
      clusters,
      metadata,
    };

    // Cache visualization
    this.visualizationCache.set(colonyId, visualization);

    return visualization;
  }

  /**
   * Get a cached visualization
   *
   * @param colonyId - Colony ID
   * @returns Cached visualization or null
   */
  getCached(colonyId: string): GraphVisualization | null {
    return this.visualizationCache.get(colonyId) || null;
  }

  /**
   * Clear visualization cache
   *
   * @param colonyId - Colony ID (or null to clear all)
   */
  clearCache(colonyId?: string): void {
    if (colonyId) {
      this.visualizationCache.delete(colonyId);
    } else {
      this.visualizationCache.clear();
    }
  }

  /**
   * Export visualization to various formats
   *
   * @param visualization - Visualization to export
   * @param format - Export format
   * @returns Exported data
   */
  export(visualization: GraphVisualization, format: ExportFormat): string {
    switch (format) {
      case 'json':
        return JSON.stringify(visualization, null, 2);

      case 'dot':
        return this.exportToDot(visualization);

      case 'gexf':
        return this.exportToGEXF(visualization);

      case 'csv':
        return this.exportToCSV(visualization);

      default:
        throw new DebugError(
          'VISUALIZATION_FAILED',
          `Unknown export format: ${format}`
        );
    }
  }

  /**
   * Create a real-time visualization stream
   *
   * @param colonyId - Colony ID
   * @param interval - Update interval in milliseconds
   * @returns Async generator of visualizations
   */
  async *streamVisualization(
    colonyId: string,
    colony: any,
    agents: Map<string, any>,
    interval: number = 1000
  ): AsyncGenerator<GraphVisualization> {
    while (true) {
      const visualization = await this.visualize(colonyId, colony, agents);
      yield visualization;

      await new Promise(resolve => setTimeout(resolve, interval));
    }
  }

  /**
   * Compute graph metrics
   *
   * @param visualization - Graph visualization
   * @returns Graph metrics
   */
  computeGraphMetrics(visualization: GraphVisualization): GraphMetrics {
    const { nodes, edges } = visualization;

    // Degree centrality
    const degreeCentrality = this.computeDegreeCentrality(nodes, edges);

    // Betweenness centrality
    const betweennessCentrality = this.computeBetweennessCentrality(nodes, edges);

    // Closeness centrality
    const closenessCentrality = this.computeClosenessCentrality(nodes, edges);

    // PageRank
    const pageRank = this.computePageRank(nodes, edges);

    return {
      degreeCentrality,
      betweennessCentrality,
      closenessCentrality,
      pageRank,
    };
  }

  // ==========================================================================
  // Private Methods
  // ==========================================================================

  private extractNodes(agents: Map<string, any>): GraphNode[] {
    const nodes: GraphNode[] = [];

    for (const [agentId, agent] of agents) {
      const node: GraphNode = {
        id: agentId,
        agentId,
        label: agent.typeId || agentId,
        type: agent.categoryId || 'unknown',
        position: { x: 0, y: 0 }, // Will be set by layout
        size: this.computeNodeSize(agent),
        color: this.getAgentColor(agent),
        properties: {
          valueFunction: agent.valueFunction || 0.5,
          successCount: agent.successCount || 0,
          failureCount: agent.failureCount || 0,
        },
        health: this.computeNodeHealth(agent),
        activity: this.computeNodeActivity(agent),
      };

      nodes.push(node);
    }

    return nodes;
  }

  private extractEdges(agents: Map<string, any>): GraphEdge[] {
    const edges: GraphEdge[] = [];
    let edgeId = 0;

    // Extract edges from agent connections
    for (const [agentId, agent] of agents) {
      // Input topics (incoming connections)
      if (agent.inputTopics) {
        for (const topic of agent.inputTopics) {
          // Find agents that output to this topic
          for (const [otherAgentId, otherAgent] of agents) {
            if (otherAgentId === agentId) continue;

            if (otherAgent.outputTopic === topic) {
              const edge: GraphEdge = {
                id: `edge_${edgeId++}`,
                source: otherAgentId,
                target: agentId,
                label: topic,
                type: 'strong',
                weight: agent.connectionWeights?.[otherAgentId] || 0.5,
                thickness: 1,
                frequency: agent.communicationFrequency?.[otherAgentId] || 0,
                color: this.getEdgeColor('strong'),
                directed: true,
              };

              edges.push(edge);
            }
          }
        }
      }
    }

    // Add edges based on synaptic weights (Hebbian learning)
    for (const [agentId, agent] of agents) {
      if (agent.synapticWeights) {
        for (const [otherAgentId, weight] of Object.entries(agent.synapticWeights)) {
          // Skip if edge already exists
          const exists = edges.some(
            e => e.source === agentId && e.target === otherAgentId
          );

          if (!exists && weight > 0.1) {
            const edge: GraphEdge = {
              id: `edge_${edgeId++}`,
              source: agentId,
              target: otherAgentId,
              type: weight > 0.5 ? 'strong' : 'weak',
              weight,
              thickness: Math.max(1, weight * 5),
              frequency: 0,
              color: this.getEdgeColor(weight > 0.5 ? 'strong' : 'weak'),
              directed: true,
            };

            edges.push(edge);
          }
        }
      }
    }

    return edges;
  }

  private applyLayout(
    nodes: GraphNode[],
    edges: GraphEdge[],
    algorithm: GraphLayout['algorithm'],
    dimensions: { width: number; height: number }
  ): GraphLayout {
    const positions = new Map<string, Position>();

    switch (algorithm) {
      case 'force':
        this.applyForceLayout(nodes, edges, dimensions, positions);
        break;

      case 'hierarchical':
        this.applyHierarchicalLayout(nodes, edges, dimensions, positions);
        break;

      case 'circular':
        this.applyCircularLayout(nodes, dimensions, positions);
        break;

      case 'random':
        this.applyRandomLayout(nodes, dimensions, positions);
        break;
    }

    return {
      algorithm,
      dimensions,
      parameters: {},
    };
  }

  private applyForceLayout(
    nodes: GraphNode[],
    edges: GraphEdge[],
    dimensions: { width: number; height: number },
    positions: Map<string, Position>
  ): void {
    // Simple force-directed layout
    const iterations = 100;
    const k = Math.sqrt((dimensions.width * dimensions.height) / nodes.length);
    const cooling = 0.95;

    // Initialize random positions
    for (const node of nodes) {
      positions.set(node.id, {
        x: Math.random() * dimensions.width,
        y: Math.random() * dimensions.height,
      });
    }

    // Iteratively refine positions
    let temperature = dimensions.width / 10;

    for (let i = 0; i < iterations; i++) {
      // Repulsive forces
      for (const u of nodes) {
        const posU = positions.get(u.id)!;

        for (const v of nodes) {
          if (u.id === v.id) continue;

          const posV = positions.get(v.id)!;
          const dx = posU.x - posV.x;
          const dy = posU.y - posV.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;

          const force = (k * k) / dist;
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;

          posU.x += fx * 0.1;
          posU.y += fy * 0.1;
        }
      }

      // Attractive forces
      for (const edge of edges) {
        const posU = positions.get(edge.source);
        const posV = positions.get(edge.target);

        if (!posU || !posV) continue;

        const dx = posU.x - posV.x;
        const dy = posU.y - posV.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;

        const force = (dist * dist) / k;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;

        posU.x -= fx * 0.1;
        posU.y -= fy * 0.1;
        posV.x += fx * 0.1;
        posV.y += fy * 0.1;
      }

      // Cool down
      temperature *= cooling;

      // Clamp positions
      for (const node of nodes) {
        const pos = positions.get(node.id)!;
        pos.x = Math.max(50, Math.min(dimensions.width - 50, pos.x));
        pos.y = Math.max(50, Math.min(dimensions.height - 50, pos.y));
      }
    }
  }

  private applyHierarchicalLayout(
    nodes: GraphNode[],
    edges: GraphEdge[],
    dimensions: { width: number; height: number },
    positions: Map<string, Position>
  ): void {
    // Simple hierarchical layout by agent type
    const levels = new Map<string, GraphNode[]>();

    for (const node of nodes) {
      let level = node.type;
      if (!levels.has(level)) {
        levels.set(level, []);
      }
      levels.get(level)!.push(node);
    }

    const levelNames = Array.from(levels.keys());
    const levelHeight = dimensions.height / (levelNames.length + 1);

    levelNames.forEach((level, levelIndex) => {
      const levelNodes = levels.get(level)!;
      const nodeWidth = dimensions.width / (levelNodes.length + 1);

      levelNodes.forEach((node, nodeIndex) => {
        positions.set(node.id, {
          x: nodeWidth * (nodeIndex + 1),
          y: levelHeight * (levelIndex + 1),
        });
      });
    });
  }

  private applyCircularLayout(
    nodes: GraphNode[],
    dimensions: { width: number; height: number },
    positions: Map<string, Position>
  ): void {
    const centerX = dimensions.width / 2;
    const centerY = dimensions.height / 2;
    const radius = Math.min(dimensions.width, dimensions.height) / 2 - 50;

    nodes.forEach((node, i) => {
      const angle = (2 * Math.PI * i) / nodes.length;
      positions.set(node.id, {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
      });
    });
  }

  private applyRandomLayout(
    nodes: GraphNode[],
    dimensions: { width: number; height: number },
    positions: Map<string, Position>
  ): void {
    nodes.forEach(node => {
      positions.set(node.id, {
        x: Math.random() * dimensions.width,
        y: Math.random() * dimensions.height,
      });
    });
  }

  private computeClusters(
    nodes: GraphNode[],
    edges: GraphEdge[]
  ): GraphCluster[] {
    // Simple clustering by agent type
    const typeGroups = new Map<string, string[]>();

    for (const node of nodes) {
      const type = node.type;
      if (!typeGroups.has(type)) {
        typeGroups.set(type, []);
      }
      typeGroups.get(type)!.push(node.id);
    }

    const clusters: GraphCluster[] = [];
    let clusterId = 0;

    for (const [type, agentIds] of typeGroups) {
      if (agentIds.length > 1) {
        clusters.push({
          id: `cluster_${clusterId++}`,
          label: type,
          nodes: agentIds,
          color: this.getClusterColor(clusterId),
          strength: agentIds.length / nodes.length,
        });
      }
    }

    return clusters;
  }

  private computeMetadata(
    nodes: GraphNode[],
    edges: GraphEdge[],
    clusters?: GraphCluster[]
  ): VisualizationMetadata {
    const nodeCount = nodes.length;
    const edgeCount = edges.length;
    const maxPossibleEdges = (nodeCount * (nodeCount - 1)) / 2;
    const density = maxPossibleEdges > 0 ? edgeCount / maxPossibleEdges : 0;

    // Estimate clustering coefficient
    const avgClusteringCoefficient = this.estimateClusteringCoefficient(nodes, edges);

    // Estimate average path length
    const avgPathLength = this.estimateAveragePathLength(nodes, edges);

    // Compute modularity
    const modularity = clusters ? this.computeModularity(nodes, edges, clusters) : 0;

    return {
      timestamp: Date.now(),
      nodeCount,
      edgeCount,
      density,
      avgClusteringCoefficient,
      avgPathLength,
      modularity,
    };
  }

  private estimateClusteringCoefficient(nodes: GraphNode[], edges: GraphEdge[]): number {
    // Simple estimate based on edge connectivity
    const adjacency = this.buildAdjacencyList(nodes, edges);
    let totalClustering = 0;

    for (const node of nodes) {
      const neighbors = adjacency.get(node.id) || [];
      if (neighbors.length < 2) continue;

      let connectedNeighbors = 0;
      for (let i = 0; i < neighbors.length; i++) {
        for (let j = i + 1; j < neighbors.length; j++) {
          const n1 = adjacency.get(neighbors[i]) || [];
          if (n1.includes(neighbors[j])) {
            connectedNeighbors++;
          }
        }
      }

      const possible = neighbors.length * (neighbors.length - 1) / 2;
      totalClustering += possible > 0 ? connectedNeighbors / possible : 0;
    }

    return nodes.length > 0 ? totalClustering / nodes.length : 0;
  }

  private estimateAveragePathLength(nodes: GraphNode[], edges: GraphEdge[]): number {
    // Use BFS to compute average shortest path
    const adjacency = this.buildAdjacencyList(nodes, edges);
    let totalPathLength = 0;
    let pathCount = 0;

    for (const source of nodes) {
      const distances = new Map<string, number>();
      const queue: string[] = [source.id];
      distances.set(source.id, 0);

      while (queue.length > 0) {
        const current = queue.shift()!;
        const dist = distances.get(current)!;

        for (const neighbor of adjacency.get(current) || []) {
          if (!distances.has(neighbor)) {
            distances.set(neighbor, dist + 1);
            queue.push(neighbor);
          }
        }
      }

      for (const [target, distance] of distances) {
        if (target !== source.id) {
          totalPathLength += distance;
          pathCount++;
        }
      }
    }

    return pathCount > 0 ? totalPathLength / pathCount : 0;
  }

  private computeModularity(
    nodes: GraphNode[],
    edges: GraphEdge[],
    clusters: GraphCluster[]
  ): number {
    // Simple modularity calculation
    const nodeToCluster = new Map<string, string>();

    for (const cluster of clusters) {
      for (const nodeId of cluster.nodes) {
        nodeToCluster.set(nodeId, cluster.id);
      }
    }

    let modularity = 0;
    const totalEdges = edges.length;

    for (const edge of edges) {
      const sourceCluster = nodeToCluster.get(edge.source);
      const targetCluster = nodeToCluster.get(edge.target);

      if (sourceCluster && sourceCluster === targetCluster) {
        modularity += 1 / totalEdges;
      }
    }

    return modularity;
  }

  private buildAdjacencyList(nodes: GraphNode[], edges: GraphEdge[]): Map<string, string[]> {
    const adjacency = new Map<string, string[]>();

    for (const node of nodes) {
      adjacency.set(node.id, []);
    }

    for (const edge of edges) {
      const sourceList = adjacency.get(edge.source);
      const targetList = adjacency.get(edge.target);

      if (sourceList && !sourceList.includes(edge.target)) {
        sourceList.push(edge.target);
      }

      if (!edge.directed && targetList && !targetList.includes(edge.source)) {
        targetList.push(edge.source);
      }
    }

    return adjacency;
  }

  private computeNodeSize(agent: any): number {
    // Size based on activity/importance
    const successCount = agent.successCount || 0;
    const baseSize = 10;
    const growthFactor = Math.min(successCount / 100, 2);
    return baseSize + growthFactor * 20;
  }

  private getAgentColor(agent: any): string {
    const type = agent.categoryId || 'unknown';

    const colors: Record<string, string> = {
      TASK: '#4CAF50',
      ROLE: '#2196F3',
      CORE: '#FF9800',
      META: '#9C27B0',
      unknown: '#9E9E9E',
    };

    return colors[type] || colors.unknown;
  }

  private getEdgeColor(type: string): string {
    const colors: Record<string, string> = {
      strong: '#4CAF50',
      weak: '#81C784',
      inhibitory: '#F44336',
    };

    return colors[type] || colors.weak;
  }

  private getClusterColor(index: number): string {
    const colors = [
      '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
      '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2',
    ];

    return colors[index % colors.length];
  }

  private computeNodeHealth(agent: any): 'healthy' | 'degraded' | 'unhealthy' {
    const successRate = agent.successCount / (agent.successCount + agent.failureCount || 1);

    if (successRate > 0.8) return 'healthy';
    if (successRate > 0.5) return 'degraded';
    return 'unhealthy';
  }

  private computeNodeActivity(agent: any): number {
    // Activity based on recent executions
    const totalExecutions = (agent.successCount || 0) + (agent.failureCount || 0);
    return Math.min(totalExecutions / 100, 1);
  }

  private computeDegreeCentrality(
    nodes: GraphNode[],
    edges: GraphEdge[]
  ): Map<string, number> {
    const degrees = new Map<string, number>();

    for (const node of nodes) {
      const inDegree = edges.filter(e => e.target === node.id).length;
      const outDegree = edges.filter(e => e.source === node.id).length;
      degrees.set(node.id, inDegree + outDegree);
    }

    return degrees;
  }

  private computeBetweennessCentrality(
    nodes: GraphNode[],
    edges: GraphEdge[]
  ): Map<string, number> {
    // Simplified betweenness calculation
    const betweenness = new Map<string, number>();

    for (const node of nodes) {
      betweenness.set(node.id, 0);
    }

    // Count how many shortest paths pass through each node
    const allPairs = this.getAllPairsShortestPaths(nodes, edges);

    for (const sources of allPairs.values()) {
      for (const paths of sources.values()) {
        for (const intermediate of paths) {
          if (intermediate) {
            const current = betweenness.get(intermediate) || 0;
            betweenness.set(intermediate, current + 1);
          }
        }
      }
    }

    return betweenness;
  }

  private computeClosenessCentrality(
    nodes: GraphNode[],
    edges: GraphEdge[]
  ): Map<string, number> {
    const closeness = new Map<string, number>();
    const allPairs = this.getAllPairsShortestPaths(nodes, edges);

    for (const node of nodes) {
      const distances = allPairs.get(node.id);
      if (!distances) continue;

      let totalDistance = 0;
      let reachable = 0;

      for (const path of distances.values()) {
        totalDistance += path.length;
        if (path.length > 0) reachable++;
      }

      const closenessValue = reachable > 1 ? (reachable - 1) / totalDistance : 0;
      closeness.set(node.id, closenessValue);
    }

    return closeness;
  }

  private computePageRank(nodes: GraphNode[], edges: GraphEdge[]): Map<string, number> {
    const dampingFactor = 0.85;
    const tolerance = 1e-6;
    const nodeCount = nodes.length;

    // Initialize PageRank
    const pageRank = new Map<string, number>();
    for (const node of nodes) {
      pageRank.set(node.id, 1 / nodeCount);
    }

    // Build adjacency list with weights
    const adjacency = new Map<string, Array<{ node: string; weight: number }>>();
    for (const node of nodes) {
      adjacency.set(node.id, []);
    }

    for (const edge of edges) {
      const list = adjacency.get(edge.source);
      if (list) {
        list.push({ node: edge.target, weight: edge.weight });
      }
    }

    // Power iteration
    let diff = 1;
    while (diff > tolerance) {
      const newPageRank = new Map<string, number>();

      for (const node of nodes) {
        let rank = (1 - dampingFactor) / nodeCount;

        // Add contributions from incoming edges
        for (const edge of edges) {
          if (edge.target === node.id) {
            const sourceRank = pageRank.get(edge.source) || 0;
            const outEdges = adjacency.get(edge.source) || [];
            const outWeightSum = outEdges.reduce((sum, e) => sum + e.weight, 0);

            if (outWeightSum > 0) {
              rank += dampingFactor * sourceRank * (edge.weight / outWeightSum);
            }
          }
        }

        newPageRank.set(node.id, rank);
      }

      // Compute difference
      diff = 0;
      for (const node of nodes) {
        const oldRank = pageRank.get(node.id) || 0;
        const newRank = newPageRank.get(node.id) || 0;
        diff += Math.abs(newRank - oldRank);
      }

      // Update pageRank map with new values
      for (const [nodeId, rank] of newPageRank) {
        pageRank.set(nodeId, rank);
      }
    }

    return pageRank;
  }

  private getAllPairsShortestPaths(
    nodes: GraphNode[],
    edges: GraphEdge[]
  ): Map<string, Map<string, string[]>> {
    const paths = new Map<string, Map<string, string[]>>();

    for (const source of nodes) {
      const sourcePaths = new Map<string, string[]>();

      for (const target of nodes) {
        if (source.id === target.id) {
          sourcePaths.set(target.id, []);
          continue;
        }

        // BFS to find shortest path
        const queue: Array<{ node: string; path: string[] }> = [
          { node: source.id, path: [] },
        ];
        const visited = new Set<string>([source.id]);
        let found = false;

        while (queue.length > 0 && !found) {
          const { node, path } = queue.shift()!;

          for (const edge of edges) {
            let nextNode: string | null = null;

            if (edge.source === node && !visited.has(edge.target)) {
              nextNode = edge.target;
            } else if (!edge.directed && edge.target === node && !visited.has(edge.source)) {
              nextNode = edge.source;
            }

            if (nextNode) {
              const newPath = [...path, node];
              if (nextNode === target.id) {
                sourcePaths.set(target.id, newPath);
                found = true;
                break;
              }

              visited.add(nextNode);
              queue.push({ node: nextNode, path: newPath });
            }
          }
        }

        if (!found) {
          sourcePaths.set(target.id, []);
        }
      }

      paths.set(source.id, sourcePaths);
    }

    return paths;
  }

  private exportToDot(visualization: GraphVisualization): string {
    let dot = 'digraph colony {\n';
    dot += '  rankdir=TB;\n';
    dot += '  node [shape=circle];\n\n';

    // Nodes
    for (const node of visualization.nodes) {
      dot += `  "${node.id}" [label="${node.label}", fillcolor="${node.color}"];\n`;
    }

    dot += '\n';

    // Edges
    for (const edge of visualization.edges) {
      const style = edge.type === 'inhibitory' ? 'dashed' : 'solid';
      dot += `  "${edge.source}" -> "${edge.target}" [label="${edge.label || ''}", style=${style}];\n`;
    }

    dot += '}\n';

    return dot;
  }

  private exportToGEXF(visualization: GraphVisualization): string {
    // Simplified GEXF export
    let gexf = '<?xml version="1.0" encoding="UTF-8"?>\n';
    gexf += '<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">\n';
    gexf += '  <graph mode="static" defaultedgetype="directed">\n';

    // Nodes
    gexf += '    <nodes>\n';
    for (const node of visualization.nodes) {
      gexf += `      <node id="${node.id}" label="${node.label}"/>\n`;
    }
    gexf += '    </nodes>\n';

    // Edges
    gexf += '    <edges>\n';
    let edgeId = 0;
    for (const edge of visualization.edges) {
      gexf += `      <edge id="${edgeId++}" source="${edge.source}" target="${edge.target}" weight="${edge.weight}"/>\n`;
    }
    gexf += '    </edges>\n';

    gexf += '  </graph>\n';
    gexf += '</gexf>\n';

    return gexf;
  }

  private exportToCSV(visualization: GraphVisualization): string {
    let csv = 'source,target,weight,type\n';

    for (const edge of visualization.edges) {
      csv += `${edge.source},${edge.target},${edge.weight},${edge.type}\n`;
    }

    return csv;
  }
}

// ============================================================================
// Types
// ============================================================================

/**
 * Visualization options
 */
export interface VisualizationOptions {
  /**
   * Layout algorithm
   */
  layout?: GraphLayout['algorithm'];

  /**
   * Include clusters
   */
  includeClusters?: boolean;

  /**
   * Visualization dimensions
   */
  dimensions?: {
    width: number;
    height: number;
  };

  /**
   * Color scheme
   */
  colorScheme?: string;
}

/**
 * Export format
 */
export type ExportFormat = 'json' | 'dot' | 'gexf' | 'csv';

/**
 * Graph metrics
 */
export interface GraphMetrics {
  /**
   * Degree centrality for each node
   */
  degreeCentrality: Map<string, number>;

  /**
   * Betweenness centrality for each node
   */
  betweennessCentrality: Map<string, number>;

  /**
   * Closeness centrality for each node
   */
  closenessCentrality: Map<string, number>;

  /**
   * PageRank for each node
   */
  pageRank: Map<string, number>;
}
