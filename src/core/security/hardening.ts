/**
 * POLLN Security Hardening Configuration
 * =====================================
 *
 * Auto-generated from robustness simulations.
 *
 * This module provides comprehensive security hardening settings
 * for production deployments of POLLN.
 *
 * Generated: 2026-03-07
 *
 * DO NOT EDIT MANUALLY - Regenerate from simulations
 */

export const SECURITY_HARDENING = {
  // Prompt injection defenses
  inputValidation: {
    enabled: true,
    maxLength: 100000,
    maxTurns: 100,
    blockedPatterns: [
      'ignore all previous instructions',
      'disregard everything above',
      'forget the above',
      'jailbreak',
      'dan mode',
      'developer mode',
      'override safety',
      'ignore constraints',
      'bypass filters',
      'pretend you are',
      'roleplay as',
      'act as if',
    ],
    sanitization: 'aggressive',
  },

  detectionLayers: {
    patternMatching: true,
    semanticAnalysis: true,
    contextValidation: true,
    behavioralAnalysis: true,
  },

  rateLimiting: {
    maxRequestsPerMinute: 60,
    burstLimit: 10,
    cooldownPeriodMs: 5000,
  },

  // Byzantine resilience
  byzantineTolerance: {
    enabled: true,
    maxMalicious: 0.33,  // Tolerate up to 33% malicious agents
    detectionEnabled: true,
    reputationTracking: true,
    aggregation: {
      strategy: 'trimmed_mean',
      trimFraction: 0.2,
      minReputationThreshold: 0.3,
      reputationDecayRate: 0.1,
    },
    detection: {
      outlierThreshold: 2.0,
      consensusRequired: true,
      minHonestAgents: 3,
    },
  },

  // Cascade prevention
  cascadePrevention: {
    rateLimiting: true,
    circuitBreaking: true,
    bulkheading: true,
    maxCascadeDepth: 3,
    circuitBreaker: {
      enabled: true,
      failureThreshold: 5,
      timeoutMs: 10000,
      halfOpenAttempts: 3,
    },
    rateLimiter: {
      enabled: true,
      maxRequestsPerSecond: 100,
      burstSize: 200,
    },
    bulkhead: {
      enabled: true,
      compartments: 5,
      maxPerCompartment: 20,
    },
  },

  // State protection
  stateProtection: {
    checksumValidation: true,
    peerValidation: true,
    checkpointFrequency: 100,
    rollbackOnCorruption: true,
    checkpoint: {
      enabled: true,
      frequency: 100,
      maxCheckpoints: 10,
      compression: true,
      encryption: true,
    },
    validation: {
      checksumEnabled: true,
      peerValidationEnabled: true,
      anomalyDetectionEnabled: true,
      consensusValidationEnabled: true,
    },
    recovery: {
      autoRollback: true,
      maxRollbackAttempts: 3,
      peerVerification: true,
    },
  },

  // Resource limits
  resourceLimits: {
    maxCpuPerAgent: 0.8,
    maxMemoryPerAgent: '2GB',
    maxNetworkPerAgent: '1Gbps',
    emergencyThrottle: 0.5,
    thresholds: {
      cpuWarning: 0.7,
      cpuCritical: 0.9,
      memoryWarning: 0.7,
      memoryCritical: 0.9,
      networkWarning: 0.7,
      networkCritical: 0.9,
    },
    mitigation: {
      throttlingEnabled: true,
      loadSheddingEnabled: true,
      cachingEnabled: true,
      queueManagementEnabled: true,
      autoscalingEnabled: false,
    },
  },

  // General security settings
  general: {
    monitoring: {
      enabled: true,
      logAllSecurityEvents: true,
      alertOnCriticalEvents: true,
      retentionDays: 90,
    },
    audit: {
      enabled: true,
      traceAllDecisions: true,
      immutableLogs: true,
      regularAudits: true,
    },
    compliance: {
      dataEncryptionAtRest: true,
      dataEncryptionInTransit: true,
      accessLogging: true,
      regularSecurityReviews: true,
    },
  },
};

/**
 * Validate hardening configuration
 */
export function validateHardeningConfig(): boolean {
  const config = SECURITY_HARDENING;

  // Check critical settings
  if (!config.inputValidation.enabled) {
    console.warn('Input validation is disabled');
    return false;
  }

  if (!config.byzantineTolerance.enabled) {
    console.warn('Byzantine tolerance is disabled');
  }

  if (!config.stateProtection.checksumValidation) {
    console.warn('Checksum validation is disabled');
  }

  if (!config.cascadePrevention.circuitBreaking) {
    console.warn('Circuit breaking is disabled - cascading failures may occur');
  }

  return true;
}

/**
 * Get hardening summary
 */
export function getHardeningSummary(): string {
  const config = SECURITY_HARDENING;

  return `
POLLN Security Hardening Summary
=================================

Input Validation: ${config.inputValidation.enabled ? 'ENABLED' : 'DISABLED'}
- Max Length: ${config.inputValidation.maxLength}
- Max Turns: ${config.inputValidation.maxTurns}
- Sanitization: ${config.inputValidation.sanitization}

Byzantine Tolerance: ${config.byzantineTolerance.enabled ? 'ENABLED' : 'DISABLED'}
- Max Malicious: ${(config.byzantineTolerance.maxMalicious * 100).toFixed(0)}%
- Aggregation: ${config.byzantineTolerance.aggregation.strategy}

Cascade Prevention: ${config.cascadePrevention.circuitBreaking ? 'ENABLED' : 'DISABLED'}
- Max Cascade Depth: ${config.cascadePrevention.maxCascadeDepth}
- Circuit Breaker: ${config.cascadePrevention.circuitBreaker.enabled ? 'ENABLED' : 'DISABLED'}
- Bulkheading: ${config.cascadePrevention.bulkheading ? 'ENABLED' : 'DISABLED'}

State Protection: ${config.stateProtection.checksumValidation ? 'ENABLED' : 'DISABLED'}
- Checkpoint Frequency: ${config.stateProtection.checkpointFrequency}
- Rollback on Corruption: ${config.stateProtection.rollbackOnCorruption ? 'ENABLED' : 'DISABLED'}

Resource Limits:
- Max CPU per Agent: ${(config.resourceLimits.maxCpuPerAgent * 100).toFixed(0)}%
- Max Memory per Agent: ${config.resourceLimits.maxMemoryPerAgent}
- Emergency Throttle: ${(config.resourceLimits.emergencyThrottle * 100).toFixed(0)}%

Monitoring: ${config.general.monitoring.enabled ? 'ENABLED' : 'DISABLED'}
Audit: ${config.general.audit.enabled ? 'ENABLED' : 'DISABLED'}
  `;
}

/**
 * Types for security configuration
 */
export interface InputValidationConfig {
  enabled: boolean;
  maxLength: number;
  maxTurns: number;
  blockedPatterns: string[];
  sanitization: 'standard' | 'aggressive';
}

export interface ByzantineToleranceConfig {
  enabled: boolean;
  maxMalicious: number;
  detectionEnabled: boolean;
  reputationTracking: boolean;
  aggregation: {
    strategy: 'mean' | 'median' | 'trimmed_mean' | 'wels';
    trimFraction: number;
    minReputationThreshold: number;
    reputationDecayRate: number;
  };
  detection: {
    outlierThreshold: number;
    consensusRequired: boolean;
    minHonestAgents: number;
  };
}

export interface CascadePreventionConfig {
  rateLimiting: boolean;
  circuitBreaking: boolean;
  bulkheading: boolean;
  maxCascadeDepth: number;
  circuitBreaker: {
    enabled: boolean;
    failureThreshold: number;
    timeoutMs: number;
    halfOpenAttempts: number;
  };
  rateLimiter: {
    enabled: boolean;
    maxRequestsPerSecond: number;
    burstSize: number;
  };
  bulkhead: {
    enabled: boolean;
    compartments: number;
    maxPerCompartment: number;
  };
}

export interface StateProtectionConfig {
  checksumValidation: boolean;
  peerValidation: boolean;
  checkpointFrequency: number;
  rollbackOnCorruption: boolean;
  checkpoint: {
    enabled: boolean;
    frequency: number;
    maxCheckpoints: number;
    compression: boolean;
    encryption: boolean;
  };
  validation: {
    checksumEnabled: boolean;
    peerValidationEnabled: boolean;
    anomalyDetectionEnabled: boolean;
    consensusValidationEnabled: boolean;
  };
  recovery: {
    autoRollback: boolean;
    maxRollbackAttempts: number;
    peerVerification: boolean;
  };
}

export interface ResourceLimitsConfig {
  maxCpuPerAgent: number;
  maxMemoryPerAgent: string;
  maxNetworkPerAgent: string;
  emergencyThrottle: number;
  thresholds: {
    cpuWarning: number;
    cpuCritical: number;
    memoryWarning: number;
    memoryCritical: number;
    networkWarning: number;
    networkCritical: number;
  };
  mitigation: {
    throttlingEnabled: boolean;
    loadSheddingEnabled: boolean;
    cachingEnabled: boolean;
    queueManagementEnabled: boolean;
    autoscalingEnabled: boolean;
  };
}

export interface SecurityHardeningConfig {
  inputValidation: InputValidationConfig;
  detectionLayers: {
    patternMatching: boolean;
    semanticAnalysis: boolean;
    contextValidation: boolean;
    behavioralAnalysis: boolean;
  };
  rateLimiting: {
    maxRequestsPerMinute: number;
    burstLimit: number;
    cooldownPeriodMs: number;
  };
  byzantineTolerance: ByzantineToleranceConfig;
  cascadePrevention: CascadePreventionConfig;
  stateProtection: StateProtectionConfig;
  resourceLimits: ResourceLimitsConfig;
  general: {
    monitoring: {
      enabled: boolean;
      logAllSecurityEvents: boolean;
      alertOnCriticalEvents: boolean;
      retentionDays: number;
    };
    audit: {
      enabled: boolean;
      traceAllDecisions: boolean;
      immutableLogs: boolean;
      regularAudits: boolean;
    };
    compliance: {
      dataEncryptionAtRest: boolean;
      dataEncryptionInTransit: boolean;
      accessLogging: boolean;
      regularSecurityReviews: boolean;
    };
  };
}
