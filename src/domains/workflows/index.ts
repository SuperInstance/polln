/**
 * Workflow Domain Module for POLLN
 * Provides workflow optimization and pattern configurations
 */

export { WORKFLOW_DOMAIN_CONFIG } from './config';
export {
  getPatternConfig,
  getCompositionConfig,
  getGranularityConfig,
  getRecommendation
} from './config';

/**
 * Workflow pattern types
 */
export type WorkflowPattern =
  | 'sequential'
  | 'parallel'
  | 'hierarchical'
  | 'map_reduce';

/**
 * Agent composition strategies
 */
export type CompositionStrategy =
  | 'generalist'
  | 'specialist'
  | 'hybrid';

/**
 * Task granularity levels
 */
export type GranularityLevel =
  | 'fine'
  | 'medium'
  | 'coarse';

/**
 * Sync strategies
 */
export type SyncStrategy =
  | 'async'
  | 'sync'
  | 'hybrid';

/**
 * Retry strategies
 */
export type RetryStrategy =
  | 'none'
  | 'fixed'
  | 'exponential_backoff'
  | 'circuit_breaker';

/**
 * Fallback modes
 */
export type FallbackMode =
  | 'fail_fast'
  | 'degrade_gracefully'
  | 'use_backup'
  | 'skip_task';

/**
 * Workflow configuration interface
 */
export interface WorkflowConfig {
  pattern: WorkflowPattern;
  agentCount: number;
  composition: CompositionStrategy;
  granularity: GranularityLevel;
  syncStrategy: SyncStrategy;
  retryStrategy: RetryStrategy;
  fallbackMode: FallbackMode;
}

/**
 * Workflow optimization result
 */
export interface WorkflowOptimization {
  recommendedPattern: WorkflowPattern;
  recommendedAgents: number;
  expectedTime: number;
  expectedQuality: number;
  confidence: number;
}
