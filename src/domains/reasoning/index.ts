/**
 * POLLN Reasoning Domain
 *
 * Exports for reasoning-optimized POLLN agents.
 * Includes configuration, types, and convenience functions.
 */

// Main configuration
export { REASONING_DOMAIN_CONFIG } from './config';

// Convenience functions
export {
  getDialogueConfig,
  getCOTConfig,
  getContextConfig,
  getDepthConfig,
  isConsistencyEnabled,
  getReasoningAgent
} from './config';

// Types
export {
  ReasoningDomainConfig,
  DialogueConfig,
  ChainOfThoughtConfig,
  ContextConfig,
  DepthConfig,
  ConsistencyConfig,
  AgentComposition,
  DialogueType,
  ReasoningMode,
  ExplorationStrategy,
  CompressionStrategy,
  ConsistencyType
} from './types';

// Re-export types as default
export { default } from './types';
