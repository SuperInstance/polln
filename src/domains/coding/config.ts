/**
 * POLLN Coding Domain Configuration
 *
 * Optimized configuration for software development tasks including
 * code generation, review, debugging, and refactoring.
 *
 * Generated: 2026-03-07
 * Source: Python simulations in simulations/domains/coding/
 */

export const CODING_DOMAIN_CONFIG = {
  domain: 'coding',
  version: '1.0.0',

  // ============================================================================
  // CODE GENERATION CONFIGURATION
  // ============================================================================
  generation: {
    // Lower temperature for deterministic code generation
    temperature: 0.3,

    topP: 0.9,
    frequencyPenalty: 0.1,

    // Stop sequences for code generation
    stopTokens: ['```', '\n\n'],

    // Maximum tokens for generated code
    maxTokens: 2000,

    // High checkpoint frequency for granular control
    checkpoints: 15,

    // Optimal model size for coding tasks
    modelSize: '100M',

    // Use value network for quality prediction
    useValueNetwork: true,
  },

  // ============================================================================
  // AGENT CONFIGURATIONS
  // ============================================================================
  agents: {
    // Code Generator Agent
    generator: {
      type: 'role',
      expertise: 'code_generation',
      modelSize: '100M',
      checkpoints: 15,
      temperature: 0.3,
      topP: 0.9,
      frequencyPenalty: 0.1,
      maxTokens: 2000,
    },

    // Code Reviewer Agent
    reviewer: {
      type: 'role',
      expertise: 'code_review',
      modelSize: '100M',
      useValueNetwork: true,
      valueNetwork: 'code_quality',
      minConfidenceThreshold: 0.3,
      maxIssuesPerReview: 50,
      priorityFiltering: true,
    },

    // Debugger Agent
    debugger: {
      type: 'task',
      expertise: 'debugging',
      iterative: true,
      maxIterations: 5,
      checkpointFrequency: 5,
      useIterativeReasoning: true,
      strategySequence: [
        'incremental',
        'hypothesis_testing',
        'symbolic_execution',
        'binary_search',
      ],
      fixValidation: true,
      earlyTerminationThreshold: 0.8,
    },

    // Refactoring Agent
    refactorer: {
      type: 'role',
      expertise: 'refactoring',
      multiFile: true,
      maxFiles: 50,
      chunkSize: 5,
      batchRefactoring: true,
      consistencyThreshold: 0.8,
    },
  },

  // ============================================================================
  // VALUE NETWORK CONFIGURATION
  // ============================================================================
  valueFunction: {
    // Features for code quality prediction
    features: [
      'syntactic_correctness',
      'semantic_correctness',
      'test_coverage',
      'complexity',
      'maintainability',
      'security_score',
    ],

    // Reward function weights
    weights: {
      correctness: 0.5,
      test_pass_rate: 0.3,
      maintainability: 0.1,
      security: 0.1,
    },

    // Network architecture
    network: {
      inputSize: 6,
      hiddenLayers: [64, 32, 16],
      outputSize: 1,
      activation: 'relu',
      outputActivation: 'sigmoid',
    },

    // Training parameters
    training: {
      lossFunction: 'mse',
      optimizer: 'adam',
      learningRate: 0.001,
      batchSize: 32,
      epochs: 100,
    },

    // TD(lambda) parameters
    tdLambda: {
      lambda: 0.9,
      gamma: 0.99,
    },

    // Quality thresholds
    thresholds: {
      excellent: 0.9,
      good: 0.7,
      acceptable: 0.5,
      poor: 0.3,
    },
  },

  // ============================================================================
  // REFACTORING CONFIGURATION
  // ============================================================================
  refactoring: {
    // Multi-file refactoring support
    multiFile: true,

    // Consistency level for multi-file operations
    consistency: 'high',

    // Maximum files to process in one batch
    maxFiles: 50,

    // Files to process per chunk
    chunkSize: 5,

    // Batch refactoring for related opportunities
    batchRefactoring: true,

    // Minimum consistency threshold
    consistencyThreshold: 0.8,

    // Refactoring types to detect
    opportunityTypes: [
      'extract_method',
      'rename_variable',
      'remove_duplication',
      'simplify_conditional',
      'extract_magic_number',
      'optimize_imports',
      'improve_structure',
      'add_type_hints',
    ],
  },

  // ============================================================================
  // DEBUGGING CONFIGURATION
  // ============================================================================
  debugging: {
    // Maximum iterations for debugging
    maxIterations: 5,

    // Checkpoint frequency for incremental debugging
    checkpointFrequency: 5,

    // Use iterative reasoning
    useIterativeReasoning: true,

    // Debugging strategy sequence
    strategySequence: [
      'incremental',
      'hypothesis_testing',
      'symbolic_execution',
      'binary_search',
      'diff_debugging',
    ],

    // Validate generated fixes
    fixValidation: true,

    // Early termination threshold
    earlyTerminationThreshold: 0.8,
  },

  // ============================================================================
  // CODE REVIEW CONFIGURATION
  // ============================================================================
  codeReview: {
    // Model size for review tasks
    modelSize: '100M',

    // Use value network for prioritization
    useValueNetwork: true,

    // Value network to use
    valueNetwork: 'code_quality',

    // Minimum confidence threshold for issues
    minConfidenceThreshold: 0.3,

    // Maximum issues to report per review
    maxIssuesPerReview: 50,

    // Enable priority-based filtering
    priorityFiltering: true,

    // Issue types to detect
    issueTypes: [
      'bug',
      'security',
      'style',
      'performance',
      'maintainability',
    ],
  },

  // ============================================================================
  // LANGUAGE-SPECIFIC CONFIGURATIONS
  // ============================================================================
  languages: {
    python: {
      indentSize: 4,
      quoteStyle: 'double',
      typeHints: true,
      docstringStyle: 'google',
    },

    javascript: {
      indentSize: 2,
      quoteStyle: 'single',
      semicolons: true,
      trailingCommas: true,
    },

    typescript: {
      indentSize: 2,
      quoteStyle: 'single',
      semicolons: true,
      strictNullChecks: true,
    },

    java: {
      indentSize: 4,
      braceStyle: 'k_r',
      namingConvention: 'camelCase',
    },
  },

  // ============================================================================
  // TESTING CONFIGURATION
  // ============================================================================
  testing: {
    // Generate tests alongside code
    generateTests: true,

    // Test framework preferences
    frameworks: {
      python: 'pytest',
      javascript: 'jest',
      typescript: 'jest',
      java: 'junit',
    },

    // Coverage targets
    coverageTargets: {
      minimum: 0.7,
      good: 0.85,
      excellent: 0.95,
    },
  },
};

export default CODING_DOMAIN_CONFIG;
