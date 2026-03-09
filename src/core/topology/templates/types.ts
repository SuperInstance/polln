/**
 * Type definitions for topology templates
 */

/**
 * Parameters for topology generation
 */
export interface TopologyParams {
  k?: number;  // Mean degree
  p?: number;  // Rewiring probability
  m?: number;  // Edges per step (BA)
  modules?: number;  // Number of modules
  levels?: number;  // Hierarchy levels
}

/**
 * Expected performance metrics
 */
export interface ExpectedMetrics {
  avgPathLength: number;
  clusteringCoeff: number;
  globalEfficiency: number;
  localEfficiency: number;
  attackTolerance: number;
  failureTolerance: number;
  edgeCost: number;
  degreeCost: number;
}

/**
 * Topology characteristics
 */
export interface Characteristics {
  networkType: 'small_world' | 'scale_free' | 'community' | 'random';
  efficiency: 'high' | 'medium' | 'low';
  robustness: 'high' | 'medium' | 'low';
  cost: 'high' | 'medium' | 'low';
}

/**
 * Complete topology template
 */
export interface TopologyTemplate {
  name: string;
  description: string;
  colonySizeRange: [number, number];
  topologyType: string;
  params: TopologyParams;
  expectedMetrics: ExpectedMetrics;
  characteristics: Characteristics;
  useCases: string[];
  limitations: string[];
}
