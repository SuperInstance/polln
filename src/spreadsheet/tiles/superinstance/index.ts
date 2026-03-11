/**
 * SuperInstance Tile Types Index
 *
 * Exports all SuperInstance-related tile types for integration with
 * the main tile system.
 */

// OriginMetricTile: Tracks radial distance changes
export { OriginMetricTile, createOriginMetricTile } from './OriginMetricTile';
export type {
  OriginMetricInput,
  OriginMetricOutput,
  OriginMetricConfig,
} from './OriginMetricTile';

// RateDeltaTile: Monitors rate of change per unit
export { RateDeltaTile, createRateDeltaTile } from './RateDeltaTile';
export type {
  RateDeltaInput,
  RateDeltaOutput,
  RateDeltaConfig,
} from './RateDeltaTile';

// CompoundRateTile: Combines multiple rate vectors
export { CompoundRateTile, createCompoundRateTile } from './CompoundRateTile';
export type {
  RateSource,
  CompoundRateInput,
  CompoundRateOutput,
  CompoundRateConfig,
} from './CompoundRateTile';

// ConfidenceCascadeTile: Propagates confidence scores
// Note: This integrates with the existing confidence-cascade.ts
// Re-export for convenience
export {
  createConfidence,
  sequentialCascade,
  parallelCascade,
  conditionalCascade,
  ConfidenceZone,
  EscalationLevel,
} from '../confidence-cascade';
export type {
  Confidence,
  CascadeConfig,
  CascadeResult,
  CascadeStep,
  ParallelBranch,
  ConditionalPath,
} from '../confidence-cascade';

// FederatedLearningTile: Each cell as independent learner
// Note: Implementation pending - placeholder export
export type {
  FederatedLearningInput,
  FederatedLearningOutput,
  FederatedLearningConfig,
} from './FederatedLearningTile';

/**
 * Register all SuperInstance tile types with the tile registry
 */
export function registerSuperInstanceTiles(registry: any): void {
  // In a real implementation, this would register tiles with the system registry
  // For now, this is a placeholder
  console.log('SuperInstance tiles would be registered here');
}

/**
 * Create a complete SuperInstance tile suite
 */
export function createSuperInstanceTileSuite(config?: {
  originMetric?: Partial<import('./OriginMetricTile').OriginMetricConfig>;
  rateDelta?: Partial<import('./RateDeltaTile').RateDeltaConfig>;
  compoundRate?: Partial<import('./CompoundRateTile').CompoundRateConfig>;
}) {
  return {
    originMetric: createOriginMetricTile(config?.originMetric),
    rateDelta: createRateDeltaTile(config?.rateDelta),
    compoundRate: createCompoundRateTile(config?.compoundRate),
  };
}

/**
 * Default export for convenience
 */
export default {
  OriginMetricTile,
  RateDeltaTile,
  CompoundRateTile,
  createOriginMetricTile,
  createRateDeltaTile,
  createCompoundRateTile,
  createSuperInstanceTileSuite,
  registerSuperInstanceTiles,
};