/**
 * Workflow Domain Configuration for POLLN
 * Auto-generated from simulation results
 */

export const WORKFLOW_DOMAIN_CONFIG = {
  // Workflow patterns
  patterns: {
    sequential: {
      agent_count: 1,
      checkpoint_frequency: 'high',
      parallelism: false,
      coordination: 'sync',
      best_for: ['simple_pipelines', 'low_dependency_workflows']
    },
    parallel: {
      agent_count: 'auto',
      checkpoint_frequency: 'low',
      parallelism: true,
      coordination: 'async',
      aggregation: 'majority',
      best_for: ['independent_tasks', 'redundancy_required']
    },
    hierarchical: {
      levels: 3,
      fan_out: 5,
      checkpoint_frequency: 'medium',
      coordination: 'tree',
      best_for: ['large_scale_workflows', 'clear_authority']
    },
    map_reduce: {
      mappers: 'auto',
      reducers: 'auto',
      chunk_size: 10,
      aggregation: 'mean',
      best_for: ['data_processing', 'batch_operations']
    }
  },

  // Agent composition strategies
  composition: {
    generalist: {
      agent_types: ['core'],
      specialization: 'low',
      adaptability: 'high',
      best_for: ['dynamic_workloads', 'unknown_task_types']
    },
    specialist: {
      agent_types: ['role'],
      specialization: 'high',
      adaptability: 'low',
      best_for: ['specialized_tasks', 'high_quality_requirements']
    },
    hybrid: {
      agent_types: ['core', 'role', 'task'],
      generalist_ratio: 0.3,
      specialist_ratio: 0.7,
      best_for: ['mixed_workloads', 'balanced_performance']
    }
  },

  // Coordination
  coordination: {
    a2a_overhead: 0.001,  // 1ms per A2A package
    sync_strategy: 'async',
    timeout_ms: 5000,
    max_retries: 3,
    strategies: {
      fine_grained: {
        sync: 'async',
        batching: true,
        batch_size: 10
      },
      medium_grained: {
        sync: 'hybrid',
        batching: false,
        sync_frequency: 5
      },
      coarse_grained: {
        sync: 'sync',
        batching: false,
        checkpoint_frequency: 'high'
      }
    }
  },

  // Error handling
  error_handling: {
    retry_strategy: 'exponential_backoff',
    fallback: 'degrade_gracefully',
    circuit_breaker: {
      enabled: true,
      threshold: 0.5,
      window_ms: 60000,
      half_open_after_ms: 30000
    },
    stress_levels: {
      low: {
        max_retries: 1,
        fallback: 'fail_fast'
      },
      medium: {
        max_retries: 3,
        fallback: 'degrade_gracefully'
      },
      high: {
        max_retries: 5,
        fallback: 'use_backup',
        circuit_breaker: true
      },
      extreme: {
        max_retries: 5,
        fallback: 'use_backup',
        circuit_breaker: true,
        redundancy: 2
      }
    }
  },

  // Task granularity
  granularity: {
    fine: {
      task_duration: 'seconds',
      overhead_ratio: 0.1,
      best_for: ['real_time_processing', 'interactive_workflows'],
      coordination: 'async'
    },
    medium: {
      task_duration: 'minutes',
      overhead_ratio: 0.05,
      best_for: ['batch_processing', 'data_pipelines'],
      coordination: 'hybrid'
    },
    coarse: {
      task_duration: 'hours',
      overhead_ratio: 0.01,
      best_for: ['long_running_jobs', 'analytics'],
      coordination: 'sync'
    }
  },

  // Recommendations
  recommendations: {
    task_type_mapping: {
      data_pipeline: {
        pattern: 'sequential',
        granularity: 'medium',
        composition: 'specialist'
      },
      code_review: {
        pattern: 'parallel',
        granularity: 'fine',
        composition: 'specialist'
      },
      research_task: {
        pattern: 'map_reduce',
        granularity: 'fine',
        composition: 'hybrid'
      },
      batch_processing: {
        pattern: 'map_reduce',
        granularity: 'coarse',
        composition: 'generalist'
      },
      complex_workflow: {
        pattern: 'hierarchical',
        granularity: 'medium',
        composition: 'hybrid'
      }
    },
    complexity_guidelines: {
      low: {
        recommended_pattern: 'sequential',
        agent_count: 1,
        coordination: 'sync'
      },
      medium: {
        recommended_pattern: 'parallel',
        agent_count: 5,
        coordination: 'async'
      },
      high: {
        recommended_pattern: 'hierarchical',
        agent_count: 10,
        coordination: 'tree'
      }
    },
    scalability_guidelines: {
      small_scale: {
        max_agents: 5,
        pattern: 'sequential',
        granularity: 'coarse'
      },
      medium_scale: {
        max_agents: 20,
        pattern: 'parallel',
        granularity: 'medium'
      },
      large_scale: {
        max_agents: 100,
        pattern: 'map_reduce',
        granularity: 'fine'
      }
    }
  }
};

/**
 * Helper function to get pattern config
 */
export function getPatternConfig(pattern: string) {
  return WORKFLOW_DOMAIN_CONFIG.patterns[pattern];
}

/**
 * Helper function to get composition config
 */
export function getCompositionConfig(composition: string) {
  return WORKFLOW_DOMAIN_CONFIG.composition[composition];
}

/**
 * Helper function to get granularity config
 */
export function getGranularityConfig(granularity: string) {
  return WORKFLOW_DOMAIN_CONFIG.granularity[granularity];
}

/**
 * Helper function to get recommendation for task type
 */
export function getRecommendation(taskType: string) {
  return WORKFLOW_DOMAIN_CONFIG.recommendations.task_type_mapping[taskType];
}
