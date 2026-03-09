/**
 * Code Quality Value Network Configuration
 *
 * Value network for predicting code quality and guiding POLLN agents
 * in software development tasks.
 *
 * Generated: 2026-03-07
 * Source: Python simulations in simulations/domains/coding/
 */

import { ValueNetworkConfig } from '../../core/types';

export const CODE_QUALITY_VALUE_CONFIG: ValueNetworkConfig = {
  // ============================================================================
  // NETWORK CONFIGURATION
  // ============================================================================
  network: {
    inputSize: 8,
    hiddenLayers: [64, 32, 16],
    outputSize: 1,
    activation: 'relu',
    outputActivation: 'sigmoid',
  },

  // ============================================================================
  // INPUT FEATURES
  // ============================================================================
  features: [
    // Correctness metrics
    'syntactic_correctness',    // 0-1: Code parses without errors
    'semantic_correctness',     // 0-1: Code passes tests
    'test_coverage',            // 0-1: Percentage of code covered by tests

    // Quality metrics
    'complexity',               // 0-1: Normalized cyclomatic complexity (inverted)
    'maintainability',          // 0-1: Maintainability index
    'security_score',           // 0-1: Security analysis score

    // Code properties
    'code_length',              // 0-1: Normalized lines of code
    'comment_ratio',            // 0-1: Ratio of comments to code
  ],

  // ============================================================================
  // REWARD FUNCTION
  // ============================================================================
  rewardWeights: {
    correctness: 0.5,        // Primary: Code must work
    test_pass_rate: 0.3,     // Important: Tests validate correctness
    maintainability: 0.1,    // Secondary: Code should be maintainable
    security: 0.1,           // Critical: Security issues must be avoided
  },

  // ============================================================================
  // TRAINING CONFIGURATION
  // ============================================================================
  training: {
    lossFunction: 'mse',
    optimizer: 'adam',
    learningRate: 0.001,
    batchSize: 32,
    epochs: 100,

    // Validation
    validationSplit: 0.2,
    earlyStoppingPatience: 10,

    // Regularization
    l2Regularization: 0.001,
    dropoutRate: 0.2,
  },

  // ============================================================================
  // TD(LAMBDA) PARAMETERS
  // ============================================================================
  tdLambda: {
    lambda: 0.9,      // Eligibility trace decay
    gamma: 0.99,      // Discount factor
  },

  // ============================================================================
  // QUALITY THRESHOLDS
  // ============================================================================
  thresholds: {
    excellent: 0.9,    // Production-ready code
    good: 0.7,        // Acceptable with minor issues
    acceptable: 0.5,  // Needs review
    poor: 0.3,        // Requires significant work
  },

  // ============================================================================
  // FEATURE NORMALIZATION
  // ============================================================================
  normalization: {
    syntactic_correctness: { min: 0, max: 1 },
    semantic_correctness: { min: 0, max: 1 },
    test_coverage: { min: 0, max: 1 },
    complexity: { min: 0, max: 1 },          // Already normalized (inverted)
    maintainability: { min: 0, max: 1 },
    security_score: { min: 0, max: 1 },
    code_length: { min: 0, max: 1 },         // Normalized by max lines
    comment_ratio: { min: 0, max: 1 },
  },

  // ============================================================================
  // PRIORITIZATION WEIGHTS
  // ============================================================================
  prioritization: {
    // Issue severity weights
    severity: {
      critical: 1.0,
      high: 0.8,
      medium: 0.5,
      low: 0.3,
      info: 0.1,
    },

    // Issue type weights
    issueType: {
      security: 2.0,
      bug: 1.5,
      performance: 1.0,
      maintainability: 0.8,
      style: 0.3,
    },
  },
};

export default CODE_QUALITY_VALUE_CONFIG;
