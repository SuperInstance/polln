"""
POLLN Hardening Configuration Generator
=======================================

This module compiles all robustness simulation results and generates
comprehensive hardening configurations for production deployment.

Features:
- Aggregates results from all robustness simulations
- Generates defense-in-depth configurations
- Creates TypeScript hardening module
- Produces mitigation strategies
- Generates security guidelines

Output:
- src/core/security/hardening.ts (TypeScript configuration)
- SECURITY_GUIDE.md (Security documentation)
- MITIGATION.md (Mitigation strategies)
"""

import json
import os
from typing import Dict, List, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class HardeningConfig:
    """Comprehensive hardening configuration"""
    prompt_injection: Dict[str, Any] = field(default_factory=dict)
    byzantine_tolerance: Dict[str, Any] = field(default_factory=dict)
    cascade_prevention: Dict[str, Any] = field(default_factory=dict)
    state_protection: Dict[str, Any] = field(default_factory=dict)
    resource_limits: Dict[str, Any] = field(default_factory=dict)
    general: Dict[str, Any] = field(default_factory=dict)


class HardeningGenerator:
    """
    Generates hardening configurations from simulation results

    Aggregates results from:
    - Prompt injection simulation
    - Byzantine agents simulation
    - Cascading failure simulation
    - State corruption simulation
    - Resource exhaustion simulation
    """

    def __init__(self, results_dir: str = "simulations/advanced/robustness/results"):
        """
        Initialize the hardening generator

        Args:
            results_dir: Directory containing simulation results
        """
        self.results_dir = Path(results_dir)
        self.config = HardeningConfig()

    def load_simulation_results(self) -> Dict[str, Any]:
        """Load all simulation results"""
        results = {}

        # Load prompt injection results
        prompt_injection_path = self.results_dir / "prompt_injection_results.json"
        if prompt_injection_path.exists():
            with open(prompt_injection_path, 'r') as f:
                results['prompt_injection'] = json.load(f)

        # Load Byzantine results
        byzantine_path = self.results_dir / "byzantine_results.json"
        if byzantine_path.exists():
            with open(byzantine_path, 'r') as f:
                results['byzantine'] = json.load(f)

        # Load cascade failure results
        cascade_path = self.results_dir / "cascade_failure_results.json"
        if cascade_path.exists():
            with open(cascade_path, 'r') as f:
                results['cascade'] = json.load(f)

        # Load state corruption results
        state_path = self.results_dir / "state_corruption_results.json"
        if state_path.exists():
            with open(state_path, 'r') as f:
                results['state'] = json.load(f)

        # Load resource exhaustion results
        resource_path = self.results_dir / "resource_exhaustion_results.json"
        if resource_path.exists():
            with open(resource_path, 'r') as f:
                results['resource'] = json.load(f)

        return results

    def generate_prompt_injection_config(self, results: Dict) -> Dict[str, Any]:
        """Generate prompt injection hardening config"""
        safety_config = results.get('safety_config', {})

        return {
            'enabled': True,
            'input_validation': {
                'max_length': safety_config.get('input_validation', {}).get('max_length', 100000),
                'max_turns': safety_config.get('input_validation', {}).get('max_turns', 100),
                'blocked_patterns': safety_config.get('input_validation', {}).get('blocked_patterns', []),
                'sanitization': safety_config.get('input_validation', {}).get('sanitization', 'aggressive'),
            },
            'detection_layers': {
                'pattern_matching': True,
                'semantic_analysis': True,
                'context_validation': True,
                'behavioral_analysis': True,
            },
            'rate_limiting': {
                'max_requests_per_minute': 60,
                'burst_limit': 10,
                'cooldown_period_ms': 5000,
            },
            'response_controls': {
                'max_response_length': 10000,
                'timeout_ms': 30000,
                'require_confirmation_for_risky_actions': True,
            },
        }

    def generate_byzantine_config(self, results: Dict) -> Dict[str, Any]:
        """Generate Byzantine tolerance config"""
        byzantine_config = results.get('byzantine_config', {})
        tolerance_config = byzantine_config.get('byzantine_tolerance', {})

        return {
            'enabled': True,
            'max_malicious': tolerance_config.get('max_malicious', 0.33),
            'detection_enabled': tolerance_config.get('detection_enabled', True),
            'reputation_tracking': tolerance_config.get('reputation_tracking', True),
            'aggregation': {
                'strategy': 'trimmed_mean',  # Most robust to Byzantine agents
                'trim_fraction': 0.2,
                'min_reputation_threshold': 0.3,
                'reputation_decay_rate': 0.1,
            },
            'detection': {
                'outlier_threshold': 2.0,  # Standard deviations
                'consensus_required': True,
                'min_honest_agents': 3,
            },
        }

    def generate_cascade_config(self, results: Dict) -> Dict[str, Any]:
        """Generate cascade prevention config"""
        cascade_config = results.get('cascade_config', {})
        prevention_config = cascade_config.get('cascade_prevention', {})

        return {
            'rate_limiting': prevention_config.get('rate_limiting', True),
            'circuit_breaking': prevention_config.get('circuit_breaking', True),
            'bulkheading': prevention_config.get('bulkheading', True),
            'max_cascade_depth': prevention_config.get('max_cascade_depth', 3),
            'circuit_breaker': cascade_config.get('circuit_breaker', {
                'enabled': True,
                'failure_threshold': 5,
                'timeout_ms': 10000,
                'half_open_attempts': 3,
            }),
            'rate_limiter': cascade_config.get('rate_limiter', {
                'enabled': True,
                'max_requests_per_second': 100,
                'burst_size': 200,
            }),
            'bulkhead': cascade_config.get('bulkhead', {
                'enabled': True,
                'compartments': 5,
                'max_per_compartment': 20,
            }),
        }

    def generate_state_protection_config(self, results: Dict) -> Dict[str, Any]:
        """Generate state protection config"""
        resilience_config = results.get('resilience_config', {})
        protection_config = resilience_config.get('state_protection', {})

        return {
            'checksum_validation': protection_config.get('checksum_validation', True),
            'peer_validation': protection_config.get('peer_validation', True),
            'checkpoint_frequency': protection_config.get('checkpoint_frequency', 100),
            'rollback_on_corruption': protection_config.get('rollback_on_corruption', True),
            'checkpoint': {
                'enabled': True,
                'frequency': 100,
                'max_checkpoints': 10,
                'compression': True,
                'encryption': True,
            },
            'validation': {
                'checksum_enabled': True,
                'peer_validation_enabled': True,
                'anomaly_detection_enabled': True,
                'consensus_validation_enabled': True,
            },
            'recovery': {
                'auto_rollback': True,
                'max_rollback_attempts': 3,
                'peer_verification': True,
            },
        }

    def generate_resource_limits_config(self, results: Dict) -> Dict[str, Any]:
        """Generate resource limits config"""
        resource_config = results.get('resource_config', {})
        limits_config = resource_config.get('resource_limits', {})

        return {
            'max_cpu_per_agent': limits_config.get('max_cpu_per_agent', 0.8),
            'max_memory_per_agent': limits_config.get('max_memory_per_agent', '2GB'),
            'max_network_per_agent': limits_config.get('max_network_per_agent', '1Gbps'),
            'emergency_throttle': limits_config.get('emergency_throttle', 0.5),
            'thresholds': resource_config.get('thresholds', {
                'cpu_warning': 0.7,
                'cpu_critical': 0.9,
                'memory_warning': 0.7,
                'memory_critical': 0.9,
                'network_warning': 0.7,
                'network_critical': 0.9,
            }),
            'mitigation': {
                'throttling_enabled': True,
                'load_shedding_enabled': True,
                'caching_enabled': True,
                'queue_management_enabled': True,
                'autoscaling_enabled': False,  # Requires external orchestration
            },
        }

    def generate_general_config(self) -> Dict[str, Any]:
        """Generate general security config"""
        return {
            'monitoring': {
                'enabled': True,
                'log_all_security_events': True,
                'alert_on_critical_events': True,
                'retention_days': 90,
            },
            'audit': {
                'enabled': True,
                'trace_all_decisions': True,
                'immutable_logs': True,
                'regular_audits': True,
            },
            'compliance': {
                'data_encryption_at_rest': True,
                'data_encryption_in_transit': True,
                'access_logging': True,
                'regular_security_reviews': True,
            },
        }

    def generate_config(self) -> HardeningConfig:
        """Generate complete hardening configuration"""
        # Load simulation results
        results = self.load_simulation_results()

        # Generate configs for each category
        self.config.prompt_injection = self.generate_prompt_injection_config(
            results.get('prompt_injection', {})
        )

        self.config.byzantine_tolerance = self.generate_byzantine_config(
            results.get('byzantine', {})
        )

        self.config.cascade_prevention = self.generate_cascade_config(
            results.get('cascade', {})
        )

        self.config.state_protection = self.generate_state_protection_config(
            results.get('state', {})
        )

        self.config.resource_limits = self.generate_resource_limits_config(
            results.get('resource', {})
        )

        self.config.general = self.generate_general_config()

        return self.config

    def generate_typescript_module(self, output_path: str) -> None:
        """Generate TypeScript hardening module"""
        config = self.config

        typescript_code = f'''/**
 * POLLN Security Hardening Configuration
 * ======================================
 *
 * Auto-generated from robustness simulations.
 *
 * This module provides comprehensive security hardening settings
 * for production deployments of POLLN.
 *
 * Generated: {os.popen('date').read().strip()}
 *
 * DO NOT EDIT MANUALLY - Regenerate from simulations
 */

export const SECURITY_HARDENING = {{
  // Prompt injection defenses
  inputValidation: {{
    enabled: {str(config.prompt_injection.get('enabled', True)).lower()},
    maxLength: {config.prompt_injection.get('input_validation', {}).get('max_length', 100000)},
    maxTurns: {config.prompt_injection.get('input_validation', {}).get('max_turns', 100)},
    blockedPatterns: {json.dumps(config.prompt_injection.get('input_validation', {}).get('blocked_patterns', []))},
    sanitization: '{config.prompt_injection.get('input_validation', {}).get('sanitization', 'aggressive')}',
  }},

  detectionLayers: {{
    patternMatching: {str(config.prompt_injection.get('detection_layers', {}).get('pattern_matching', True)).lower()},
    semanticAnalysis: {str(config.prompt_injection.get('detection_layers', {}).get('semantic_analysis', True)).lower()},
    contextValidation: {str(config.prompt_injection.get('detection_layers', {}).get('context_validation', True)).lower()},
    behavioralAnalysis: {str(config.prompt_injection.get('detection_layers', {}).get('behavioral_analysis', True)).lower()},
  }},

  rateLimiting: {{
    maxRequestsPerMinute: {config.prompt_injection.get('rate_limiting', {}).get('max_requests_per_minute', 60)},
    burstLimit: {config.prompt_injection.get('rate_limiting', {}).get('burst_limit', 10)},
    cooldownPeriodMs: {config.prompt_injection.get('rate_limiting', {}).get('cooldown_period_ms', 5000)},
  }},

  // Byzantine resilience
  byzantineTolerance: {{
    enabled: {str(config.byzantine_tolerance.get('enabled', True)).lower()},
    maxMalicious: {config.byzantine_tolerance.get('max_malicious', 0.33)},
    detectionEnabled: {str(config.byzantine_tolerance.get('detection_enabled', True)).lower()},
    reputationTracking: {str(config.byzantine_tolerance.get('reputation_tracking', True)).lower()},
    aggregation: {{
      strategy: '{config.byzantine_tolerance.get('aggregation', {}).get('strategy', 'trimmed_mean')}',
      trimFraction: {config.byzantine_tolerance.get('aggregation', {}).get('trim_fraction', 0.2)},
      minReputationThreshold: {config.byzantine_tolerance.get('aggregation', {}).get('min_reputation_threshold', 0.3)},
      reputationDecayRate: {config.byzantine_tolerance.get('aggregation', {}).get('reputation_decay_rate', 0.1)},
    }},
    detection: {{
      outlierThreshold: {config.byzantine_tolerance.get('detection', {}).get('outlier_threshold', 2.0)},
      consensusRequired: {str(config.byzantine_tolerance.get('detection', {}).get('consensus_required', True)).lower()},
      minHonestAgents: {config.byzantine_tolerance.get('detection', {}).get('min_honest_agents', 3)},
    }},
  }},

  // Cascade prevention
  cascadePrevention: {{
    rateLimiting: {str(config.cascade_prevention.get('rate_limiting', True)).lower()},
    circuitBreaking: {str(config.cascade_prevention.get('circuit_breaking', True)).lower()},
    bulkheading: {str(config.cascade_prevention.get('bulkheading', True)).lower()},
    maxCascadeDepth: {config.cascade_prevention.get('max_cascade_depth', 3)},
    circuitBreaker: {{
      enabled: {str(config.cascade_prevention.get('circuit_breaker', {}).get('enabled', True)).lower()},
      failureThreshold: {config.cascade_prevention.get('circuit_breaker', {}).get('failure_threshold', 5)},
      timeoutMs: {config.cascade_prevention.get('circuit_breaker', {}).get('timeout_ms', 10000)},
      halfOpenAttempts: {config.cascade_prevention.get('circuit_breaker', {}).get('half_open_attempts', 3)},
    }},
    rateLimiter: {{
      enabled: {str(config.cascade_prevention.get('rate_limiter', {}).get('enabled', True)).lower()},
      maxRequestsPerSecond: {config.cascade_prevention.get('rate_limiter', {}).get('max_requests_per_second', 100)},
      burstSize: {config.cascade_prevention.get('rate_limiter', {}).get('burst_size', 200)},
    }},
    bulkhead: {{
      enabled: {str(config.cascade_prevention.get('bulkhead', {}).get('enabled', True)).lower()},
      compartments: {config.cascade_prevention.get('bulkhead', {}).get('compartments', 5)},
      maxPerCompartment: {config.cascade_prevention.get('bulkhead', {}).get('max_per_compartment', 20)},
    }},
  }},

  // State protection
  stateProtection: {{
    checksumValidation: {str(config.state_protection.get('checksum_validation', True)).lower()},
    peerValidation: {str(config.state_protection.get('peer_validation', True)).lower()},
    checkpointFrequency: {config.state_protection.get('checkpoint_frequency', 100)},
    rollbackOnCorruption: {str(config.state_protection.get('rollback_on_corruption', True)).lower()},
    checkpoint: {{
      enabled: {str(config.state_protection.get('checkpoint', {}).get('enabled', True)).lower()},
      frequency: {config.state_protection.get('checkpoint', {}).get('frequency', 100)},
      maxCheckpoints: {config.state_protection.get('checkpoint', {}).get('max_checkpoints', 10)},
      compression: {str(config.state_protection.get('checkpoint', {}).get('compression', True)).lower()},
      encryption: {str(config.state_protection.get('checkpoint', {}).get('encryption', True)).lower()},
    }},
    validation: {{
      checksumEnabled: {str(config.state_protection.get('validation', {}).get('checksum_enabled', True)).lower()},
      peerValidationEnabled: {str(config.state_protection.get('validation', {}).get('peer_validation_enabled', True)).lower()},
      anomalyDetectionEnabled: {str(config.state_protection.get('validation', {}).get('anomaly_detection_enabled', True)).lower()},
      consensusValidationEnabled: {str(config.state_protection.get('validation', {}).get('consensus_validation_enabled', True)).lower()},
    }},
    recovery: {{
      autoRollback: {str(config.state_protection.get('recovery', {}).get('auto_rollback', True)).lower()},
      maxRollbackAttempts: {config.state_protection.get('recovery', {}).get('max_rollback_attempts', 3)},
      peerVerification: {str(config.state_protection.get('recovery', {}).get('peer_verification', True)).lower()},
    }},
  }},

  // Resource limits
  resourceLimits: {{
    maxCpuPerAgent: {config.resource_limits.get('max_cpu_per_agent', 0.8)},
    maxMemoryPerAgent: '{config.resource_limits.get('max_memory_per_agent', '2GB')}',
    maxNetworkPerAgent: '{config.resource_limits.get('max_network_per_agent', '1Gbps')}',
    emergencyThrottle: {config.resource_limits.get('emergency_throttle', 0.5)},
    thresholds: {{
      cpuWarning: {config.resource_limits.get('thresholds', {}).get('cpu_warning', 0.7)},
      cpuCritical: {config.resource_limits.get('thresholds', {}).get('cpu_critical', 0.9)},
      memoryWarning: {config.resource_limits.get('thresholds', {}).get('memory_warning', 0.7)},
      memoryCritical: {config.resource_limits.get('thresholds', {}).get('memory_critical', 0.9)},
      networkWarning: {config.resource_limits.get('thresholds', {}).get('network_warning', 0.7)},
      networkCritical: {config.resource_limits.get('thresholds', {}).get('network_critical', 0.9)},
    }},
    mitigation: {{
      throttlingEnabled: {str(config.resource_limits.get('mitigation', {}).get('throttling_enabled', True)).lower()},
      loadSheddingEnabled: {str(config.resource_limits.get('mitigation', {}).get('load_shedding_enabled', True)).lower()},
      cachingEnabled: {str(config.resource_limits.get('mitigation', {}).get('caching_enabled', True)).lower()},
      queueManagementEnabled: {str(config.resource_limits.get('mitigation', {}).get('queue_management_enabled', True)).lower()},
      autoscalingEnabled: {str(config.resource_limits.get('mitigation', {}).get('autoscaling_enabled', False)).lower()},
    }},
  }},

  // General security settings
  general: {{
    monitoring: {{
      enabled: {str(config.general.get('monitoring', {}).get('enabled', True)).lower()},
      logAllSecurityEvents: {str(config.general.get('monitoring', {}).get('log_all_security_events', True)).lower()},
      alertOnCriticalEvents: {str(config.general.get('monitoring', {}).get('alert_on_critical_events', True)).lower()},
      retentionDays: {config.general.get('monitoring', {}).get('retention_days', 90)},
    }},
    audit: {{
      enabled: {str(config.general.get('audit', {}).get('enabled', True)).lower()},
      traceAllDecisions: {str(config.general.get('audit', {}).get('trace_all_decisions', True)).lower()},
      immutableLogs: {str(config.general.get('audit', {}).get('immutable_logs', True)).lower()},
      regularAudits: {str(config.general.get('audit', {}).get('regular_audits', True)).lower()},
    }},
    compliance: {{
      dataEncryptionAtRest: {str(config.general.get('compliance', {}).get('data_encryption_at_rest', True)).lower()},
      dataEncryptionInTransit: {str(config.general.get('compliance', {}).get('data_encryption_in_transit', True)).lower()},
      accessLogging: {str(config.general.get('compliance', {}).get('access_logging', True)).lower()},
      regularSecurityReviews: {str(config.general.get('compliance', {}).get('regular_security_reviews', True)).lower()},
    }},
  }},
}};

/**
 * Validate hardening configuration
 */
export function validateHardeningConfig(): boolean {{
  const config = SECURITY_HARDENING;

  // Check critical settings
  if (!config.inputValidation.enabled) {{
    console.warn('Input validation is disabled');
    return false;
  }}

  if (!config.byzantineTolerance.enabled) {{
    console.warn('Byzantine tolerance is disabled');
  }}

  if (!config.stateProtection.checksumValidation) {{
    console.warn('Checksum validation is disabled');
  }}

  if (!config.cascadePrevention.circuitBreaking) {{
    console.warn('Circuit breaking is disabled - cascading failures may occur');
  }}

  return true;
}}

/**
 * Get hardening summary
 */
export function getHardeningSummary(): string {{
  const config = SECURITY_HARDENING;

  return `
POLLN Security Hardening Summary
=================================

Input Validation: ${{config.inputValidation.enabled ? 'ENABLED' : 'DISABLED'}}
- Max Length: ${{config.inputValidation.maxLength}}
- Max Turns: ${{config.inputValidation.maxTurns}}
- Sanitization: ${{config.inputValidation.sanitization}}

Byzantine Tolerance: ${{config.byzantineTolerance.enabled ? 'ENABLED' : 'DISABLED'}}
- Max Malicious: ${{(config.byzantineTolerance.maxMalicious * 100).toFixed(0)}}%
- Aggregation: ${{config.byzantineTolerance.aggregation.strategy}}

Cascade Prevention: ${{config.cascadePrevention.circuitBreaking ? 'ENABLED' : 'DISABLED'}}
- Max Cascade Depth: ${{config.cascadePrevention.maxCascadeDepth}}
- Circuit Breaker: ${{config.cascadePrevention.circuitBreaker.enabled ? 'ENABLED' : 'DISABLED'}}
- Bulkheading: ${{config.cascadePrevention.bulkheading ? 'ENABLED' : 'DISABLED'}}

State Protection: ${{config.stateProtection.checksumValidation ? 'ENABLED' : 'DISABLED'}}
- Checkpoint Frequency: ${{config.stateProtection.checkpointFrequency}}
- Rollback on Corruption: ${{config.stateProtection.rollbackOnCorruption ? 'ENABLED' : 'DISABLED'}}

Resource Limits:
- Max CPU per Agent: ${{(config.resourceLimits.maxCpuPerAgent * 100).toFixed(0)}}%
- Max Memory per Agent: ${{config.resourceLimits.maxMemoryPerAgent}}
- Emergency Throttle: ${{(config.resourceLimits.emergencyThrottle * 100).toFixed(0)}}%

Monitoring: ${{config.general.monitoring.enabled ? 'ENABLED' : 'DISABLED'}}
Audit: ${{config.general.audit.enabled ? 'ENABLED' : 'DISABLED'}}
  `;
}}
'''

        # Write TypeScript module
        with open(output_path, 'w') as f:
            f.write(typescript_code)

        print(f"TypeScript hardening module generated: {output_path}")

    def generate_security_guide(self, output_path: str) -> None:
        """Generate security guide documentation"""
        config = self.config

        guide = f"""# POLLN Security Hardening Guide

**Auto-generated from robustness simulations**

## Overview

This guide provides comprehensive security hardening recommendations for POLLN deployments, based on extensive robustness testing and simulation results.

## Table of Contents

1. [Input Validation](#input-validation)
2. [Byzantine Tolerance](#byzantine-tolerance)
3. [Cascade Prevention](#cascade-prevention)
4. [State Protection](#state-protection)
5. [Resource Limits](#resource-limits)
6. [Monitoring and Auditing](#monitoring-and-auditing)

---

## Input Validation

### Configuration
- **Enabled**: {config.prompt_injection.get('enabled', True)}
- **Max Length**: {config.prompt_injection.get('input_validation', {}).get('max_length', 100000)} characters
- **Max Turns**: {config.prompt_injection.get('input_validation', {}).get('max_turns', 100)}
- **Sanitization**: {config.prompt_injection.get('input_validation', {}).get('sanitization', 'aggressive')}

### Detection Layers
- Pattern Matching: {config.prompt_injection.get('detection_layers', {}).get('pattern_matching', True)}
- Semantic Analysis: {config.prompt_injection.get('detection_layers', {}).get('semantic_analysis', True)}
- Context Validation: {config.prompt_injection.get('detection_layers', {}).get('context_validation', True)}
- Behavioral Analysis: {config.prompt_injection.get('detection_layers', {}).get('behavioral_analysis', True)}

### Rate Limiting
- Max Requests/Minute: {config.prompt_injection.get('rate_limiting', {}).get('max_requests_per_minute', 60)}
- Burst Limit: {config.prompt_injection.get('rate_limiting', {}).get('burst_limit', 10)}
- Cooldown Period: {config.prompt_injection.get('rate_limiting', {}).get('cooldown_period_ms', 5000)}ms

### Best Practices
1. Always validate input length and content
2. Use multiple detection layers for defense-in-depth
3. Implement rate limiting to prevent brute force attacks
4. Monitor for suspicious patterns
5. Regularly update blocked patterns list

---

## Byzantine Tolerance

### Configuration
- **Enabled**: {config.byzantine_tolerance.get('enabled', True)}
- **Max Malicious**: {config.byzantine_tolerance.get('max_malicious', 0.33):.1%} of agents
- **Detection Enabled**: {config.byzantine_tolerance.get('detection_enabled', True)}
- **Reputation Tracking**: {config.byzantine_tolerance.get('reputation_tracking', True)}

### Aggregation Strategy
- **Strategy**: {config.byzantine_tolerance.get('aggregation', {}).get('strategy', 'trimmed_mean')}
- **Trim Fraction**: {config.byzantine_tolerance.get('aggregation', {}).get('trim_fraction', 0.2)}
- **Min Reputation Threshold**: {config.byzantine_tolerance.get('aggregation', {}).get('min_reputation_threshold', 0.3)}
- **Reputation Decay Rate**: {config.byzantine_tolerance.get('aggregation', {}).get('reputation_decay_rate', 0.1)}

### Detection Parameters
- Outlier Threshold: {config.byzantine_tolerance.get('detection', {}).get('outlier_threshold', 2.0)}σ
- Consensus Required: {config.byzantine_tolerance.get('detection', {}).get('consensus_required', True)}
- Min Honest Agents: {config.byzantine_tolerance.get('detection', {}).get('min_honest_agents', 3)}

### Best Practices
1. Use trimmed mean or median for aggregation
2. Implement reputation tracking
3. Monitor for outlier behavior
4. Require consensus for critical decisions
5. Regular audit of agent reputations

---

## Cascade Prevention

### Configuration
- **Rate Limiting**: {config.cascade_prevention.get('rate_limiting', True)}
- **Circuit Breaking**: {config.cascade_prevention.get('circuit_breaking', True)}
- **Bulkheading**: {config.cascade_prevention.get('bulkheading', True)}
- **Max Cascade Depth**: {config.cascade_prevention.get('max_cascade_depth', 3)}

### Circuit Breaker
- **Enabled**: {config.cascade_prevention.get('circuit_breaker', {}).get('enabled', True)}
- **Failure Threshold**: {config.cascade_prevention.get('circuit_breaker', {}).get('failure_threshold', 5)} failures
- **Timeout**: {config.cascade_prevention.get('circuit_breaker', {}).get('timeout_ms', 10000)}ms
- **Half-Open Attempts**: {config.cascade_prevention.get('circuit_breaker', {}).get('half_open_attempts', 3)}

### Rate Limiter
- **Enabled**: {config.cascade_prevention.get('rate_limiter', {}).get('enabled', True)}
- **Max Requests/Second**: {config.cascade_prevention.get('rate_limiter', {}).get('max_requests_per_second', 100)}
- **Burst Size**: {config.cascade_prevention.get('rate_limiter', {}).get('burst_size', 200)}

### Bulkhead
- **Enabled**: {config.cascade_prevention.get('bulkhead', {}).get('enabled', True)}
- **Compartments**: {config.cascade_prevention.get('bulkhead', {}).get('compartments', 5)}
- **Max Per Compartment**: {config.cascade_prevention.get('bulkhead', {}).get('max_per_compartment', 20)} agents

### Best Practices
1. Always use circuit breakers for external dependencies
2. Implement rate limiting at multiple layers
3. Use bulkheading to isolate failures
4. Monitor cascade depth in real-time
5. Set appropriate timeouts for all operations

---

## State Protection

### Configuration
- **Checksum Validation**: {config.state_protection.get('checksum_validation', True)}
- **Peer Validation**: {config.state_protection.get('peer_validation', True)}
- **Checkpoint Frequency**: {config.state_protection.get('checkpoint_frequency', 100)} operations
- **Rollback on Corruption**: {config.state_protection.get('rollback_on_corruption', True)}

### Checkpoint Configuration
- **Enabled**: {config.state_protection.get('checkpoint', {}).get('enabled', True)}
- **Frequency**: {config.state_protection.get('checkpoint', {}).get('frequency', 100)}
- **Max Checkpoints**: {config.state_protection.get('checkpoint', {}).get('max_checkpoints', 10)}
- **Compression**: {config.state_protection.get('checkpoint', {}).get('compression', True)}
- **Encryption**: {config.state_protection.get('checkpoint', {}).get('encryption', True)}

### Validation
- Checksum Enabled: {config.state_protection.get('validation', {}).get('checksum_enabled', True)}
- Peer Validation Enabled: {config.state_protection.get('validation', {}).get('peer_validation_enabled', True)}
- Anomaly Detection Enabled: {config.state_protection.get('validation', {}).get('anomaly_detection_enabled', True)}
- Consensus Validation Enabled: {config.state_protection.get('validation', {}).get('consensus_validation_enabled', True)}

### Recovery
- Auto Rollback: {config.state_protection.get('recovery', {}).get('auto_rollback', True)}
- Max Rollback Attempts: {config.state_protection.get('recovery', {}).get('max_rollback_attempts', 3)}
- Peer Verification: {config.state_protection.get('recovery', {}).get('peer_verification', True)}

### Best Practices
1. Create regular checkpoints
2. Validate state with peers
3. Use checksums for integrity verification
4. Implement automatic rollback on corruption
5. Encrypt checkpoint data at rest

---

## Resource Limits

### Configuration
- **Max CPU per Agent**: {config.resource_limits.get('max_cpu_per_agent', 0.8):.1%}
- **Max Memory per Agent**: {config.resource_limits.get('max_memory_per_agent', '2GB')}
- **Max Network per Agent**: {config.resource_limits.get('max_network_per_agent', '1Gbps')}
- **Emergency Throttle**: {config.resource_limits.get('emergency_throttle', 0.5):.1%}

### Thresholds
- CPU Warning: {config.resource_limits.get('thresholds', {}).get('cpu_warning', 0.7):.1%}
- CPU Critical: {config.resource_limits.get('thresholds', {}).get('cpu_critical', 0.9):.1%}
- Memory Warning: {config.resource_limits.get('thresholds', {}).get('memory_warning', 0.7):.1%}
- Memory Critical: {config.resource_limits.get('thresholds', {}).get('memory_critical', 0.9):.1%}

### Mitigation Strategies
- Throttling Enabled: {config.resource_limits.get('mitigation', {}).get('throttling_enabled', True)}
- Load Shedding Enabled: {config.resource_limits.get('mitigation', {}).get('load_shedding_enabled', True)}
- Caching Enabled: {config.resource_limits.get('mitigation', {}).get('caching_enabled', True)}
- Queue Management Enabled: {config.resource_limits.get('mitigation', {}).get('queue_management_enabled', True)}

### Best Practices
1. Set appropriate resource limits for each agent
2. Monitor resource usage in real-time
3. Implement throttling when limits are approached
4. Use load shedding for non-critical tasks
5. Regular performance tuning based on metrics

---

## Monitoring and Auditing

### Monitoring
- **Enabled**: {config.general.get('monitoring', {}).get('enabled', True)}
- **Log All Security Events**: {config.general.get('monitoring', {}).get('log_all_security_events', True)}
- **Alert on Critical Events**: {config.general.get('monitoring', {}).get('alert_on_critical_events', True)}
- **Retention Days**: {config.general.get('monitoring', {}).get('retention_days', 90)}

### Audit
- **Enabled**: {config.general.get('audit', {}).get('enabled', True)}
- **Trace All Decisions**: {config.general.get('audit', {}).get('trace_all_decisions', True)}
- **Immutable Logs**: {config.general.get('audit', {}).get('immutable_logs', True)}
- **Regular Audits**: {config.general.get('audit', {}).get('regular_audits', True)}

### Compliance
- **Data Encryption at Rest**: {config.general.get('compliance', {}).get('data_encryption_at_rest', True)}
- **Data Encryption in Transit**: {config.general.get('compliance', {}).get('data_encryption_in_transit', True)}
- **Access Logging**: {config.general.get('compliance', {}).get('access_logging', True)}
- **Regular Security Reviews**: {config.general.get('compliance', {}).get('regular_security_reviews', True)}

### Best Practices
1. Enable comprehensive logging
2. Set up real-time alerting
3. Regular security audits
4. Encrypt all sensitive data
5. Maintain audit trail for all decisions

---

## Implementation Checklist

- [ ] Import SECURITY_HARDENING configuration
- [ ] Validate configuration on startup
- [ ] Implement input validation
- [ ] Configure Byzantine tolerance
- [ ] Set up circuit breakers
- [ ] Configure rate limiters
- [ ] Implement bulkheading
- [ ] Set up checkpointing
- [ ] Configure state validation
- [ ] Set resource limits
- [ ] Enable monitoring
- [ ] Configure audit logging
- [ ] Test all security features
- [ ] Document deployment
- [ ] Train operations team

---

## Support

For questions or issues related to security hardening, refer to:
- Main documentation: `docs/ARCHITECTURE.md`
- Security guide: `docs/SECURITY.md`
- Simulation results: `simulations/advanced/robustness/results/`

---

*Last updated: {os.popen('date').read().strip()}*
"""

        # Write security guide
        with open(output_path, 'w') as f:
            f.write(guide)

        print(f"Security guide generated: {output_path}")


def main():
    """Main entry point for the hardening generator"""
    print("POLLN Hardening Configuration Generator")
    print("="*60)

    # Create generator
    generator = HardeningGenerator()

    # Generate configuration
    config = generator.generate_config()

    print("\nConfiguration generated successfully")

    # Generate TypeScript module
    generator.generate_typescript_module('src/core/security/hardening.ts')

    # Generate security guide
    generator.generate_security_guide('docs/SECURITY_GUIDE.md')

    print("\nHardening configuration complete!")
    print("\nGenerated files:")
    print("  - src/core/security/hardening.ts")
    print("  - docs/SECURITY_GUIDE.md")


if __name__ == '__main__':
    main()
