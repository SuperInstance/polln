# POLLN Diagnostics Reference

Complete reference for all diagnostic outputs and metrics.

## Diagnostic Outputs

### A2A Trace Report (`a2a_trace.json`)

```json
{
  "colony_id": "string",
  "generated_at": "ISO 8601 timestamp",
  "summary": {
    "total_packages": "number",
    "total_events": "number",
    "causal_chains": "number",
    "lost_packages": "number",
    "serialization_issues": "number"
  },
  "packages": {
    "package_id": {
      "id": "string",
      "timestamp": "number",
      "sender_id": "string",
      "receiver_id": "string | null",
      "type": "string",
      "layer": "string",
      "privacy_level": "string",
      "parent_ids": ["string"],
      "causal_chain_id": "string",
      "payload_hash": "string",
      "payload_size": "number",
      "current_agent": "string | null",
      "status": "string"
    }
  },
  "events": [
    {
      "event_id": "string",
      "package_id": "string",
      "timestamp": "number",
      "event_type": "string",
      "agent_id": "string",
      "details": {}
    }
  ],
  "causal_chain_analyses": {
    "chain_id": {
      "chain_id": "string",
      "depth": "number",
      "branch_count": "number",
      "total_packages": "number",
      "root_package_id": "string",
      "leaf_package_ids": ["string"],
      "cycle_detected": "boolean",
      "orphan_packages": ["string"],
      "avg_branching_factor": "number"
    }
  },
  "delay_statistics": {
    "chain_id": {
      "avg_delay": "number",
      "min_delay": "number",
      "max_delay": "number",
      "total_delay": "number",
      "hop_count": "number"
    }
  },
  "lost_packages": ["string"],
  "serialization_issues": [
    {
      "type": "string",
      "package_id": "string",
      "severity": "string",
      "message": "string"
    }
  ]
}
```

### Agent States Report (`agent_states.json`)

```json
{
  "colony_id": "string",
  "generated_at": "ISO 8601 timestamp",
  "summary": {
    "total_agents": "number",
    "hung_agents": "number",
    "corrupted_agents": "number",
    "error_agents": "number",
    "convergence_issues": "number",
    "total_synapses": "number"
  },
  "agent_snapshots": {
    "agent_id": [
      {
        "agent_id": "string",
        "agent_type": "string",
        "timestamp": "number",
        "status": "string",
        "last_active": "number",
        "value_function": "number",
        "success_count": "number",
        "failure_count": "number",
        "success_rate": "number",
        "avg_latency_ms": "number",
        "state_snapshot": {},
        "incoming_synapse_count": "number",
        "outgoing_synapse_count": "number",
        "strongest_synapse": {},
        "is_meta": "boolean",
        "meta_potential": "number | null",
        "differentiation_signals": ["string"] | null,
        "is_hung": "boolean",
        "is_corrupted": "boolean",
        "error_message": "string | null"
      }
    ]
  },
  "value_network_states": {
    "agent_id": {
      "agent_id": "string",
      "current_value": "number",
      "value_history": ["number"],
      "eligibility_traces": {},
      "learning_rate": "number",
      "discount_factor": "number",
      "convergence_score": "number",
      "trend": "string"
    }
  },
  "synapse_inspections": {
    "source_target": {
      "source_id": "string",
      "target_id": "string",
      "weight": "number",
      "coactivation_count": "number",
      "last_coactivated": "number",
      "age_seconds": "number",
      "health_score": "number"
    }
  }
}
```

### Colony Health Report (`colony_health.json`)

```json
{
  "colony_id": "string",
  "generated_at": "ISO 8601 timestamp",
  "overall_status": "string",
  "health_score": "number",
  "summary": {
    "total_agents": "number",
    "total_metrics": "number",
    "critical_issues": "number",
    "warning_issues": "number",
    "deadlocked": "boolean",
    "bottlenecks": "number",
    "cascade_risk": "number"
  },
  "health_metrics": [
    {
      "name": "string",
      "value": "number",
      "threshold": "number",
      "status": "string",
      "message": "string",
      "recommendation": "string | null"
    }
  ],
  "resource_usage": {
    "agent_id": {
      "agent_id": "string",
      "cpu_percent": "number",
      "memory_mb": "number",
      "network_io_mb": "number",
      "active_connections": "number",
      "queue_depth": "number",
      "cpu_status": "string",
      "memory_status": "string",
      "network_status": "string",
      "queue_status": "string"
    }
  },
  "deadlock_detection": {
    "is_deadlocked": "boolean",
    "deadlock_cycle": ["string"],
    "deadlock_type": "string",
    "severity": "string",
    "description": "string"
  },
  "bottleneck_analysis": {
    "bottlenecks": [
      {
        "agent_id": "string",
        "type": "string",
        "severity": "string",
        "value": "number",
        "message": "string"
      }
    ],
    "throughput": "number",
    "avg_latency": "number",
    "p95_latency": "number",
    "p99_latency": "number",
    "overloaded_agents": ["string"],
    "underutilized_agents": ["string"]
  },
  "cascade_failure_prediction": {
    "at_risk_agents": ["string"],
    "failure_probability": "number",
    "propagation_path": ["string"],
    "triggers": ["string"],
    "mitigation_actions": ["string"]
  },
  "recommendations": ["string"]
}
```

### Value Network Debug Report (`value_network_debug.json`)

```json
{
  "colony_id": "string",
  "generated_at": "ISO 8601 timestamp",
  "summary": {
    "total_agents": "number",
    "total_updates": "number",
    "converged_agents": "number",
    "oscillating_agents": "number",
    "diverging_agents": "number"
  },
  "update_events": {
    "agent_id": [
      {
        "agent_id": "string",
        "timestamp": "number",
        "old_value": "number",
        "new_value": "number",
        "reward": "number",
        "td_error": "number",
        "eligibility_trace": "number",
        "learning_rate": "number",
        "lambda_param": "number"
      }
    ]
  },
  "value_history": {
    "agent_id": ["number"]
  },
  "convergence_analyses": {
    "agent_id": {
      "agent_id": "string",
      "converged": "boolean",
      "convergence_rate": "number",
      "stability_score": "number",
      "oscillation_detected": "boolean",
      "oscillation_frequency": "number",
      "divergence_detected": "boolean",
      "trend": "string",
      "recommendations": ["string"]
    }
  },
  "value_distributions": {
    "agent_id": {
      "agent_id": "string",
      "mean": "number",
      "std": "number",
      "min": "number",
      "max": "number",
      "median": "number",
      "percentile_25": "number",
      "percentile_75": "number",
      "histogram": [["number", "number"]]
    }
  },
  "issues": [
    {
      "type": "string",
      "severity": "string",
      "agent_id": "string",
      "message": "string",
      "recommendation": "string"
    }
  ]
}
```

### Issues Detected Report (`issues_detected.json`)

```json
{
  "colony_id": "string",
  "generated_at": "ISO 8601 timestamp",
  "summary": {
    "total_issues": "number",
    "critical_issues": "number",
    "warning_issues": "number",
    "info_issues": "number",
    "patterns_detected": "number"
  },
  "issues_by_category": {
    "category": "number"
  },
  "detected_issues": {
    "issue_id": {
      "issue_id": "string",
      "severity": "string",
      "category": "string",
      "agent_id": "string | null",
      "title": "string",
      "description": "string",
      "evidence": {},
      "timestamp": "number",
      "suggested_fixes": ["string"],
      "related_issues": ["string"]
    }
  },
  "patterns": {
    "pattern_id": {
      "pattern_id": "string",
      "pattern_name": "string",
      "description": "string",
      "matched_issues": ["string"],
      "confidence": "number",
      "root_cause_hypothesis": "string",
      "recommended_actions": ["string"]
    }
  },
  "health_trends": {
    "metric_name": [
      {
        "metric_name": "string",
        "current_value": "number",
        "previous_value": "number",
        "trend": "string",
        "rate_of_change": "number",
        "predicted_value": "number",
        "concern_level": "string"
      }
    ]
  },
  "recommendations": ["string"]
}
```

### Comprehensive Diagnostic Report (`diagnostic_report.json`)

```json
{
  "colony_id": "string",
  "generated_at": "ISO 8601 timestamp",
  "overall_health_score": "number",
  "overall_status": "string",
  "summary": {
    "total_agents": "number",
    "critical_issues": "number",
    "warning_issues": "number",
    "deadlocked": "boolean",
    "cascade_risk": "number"
  },
  "diagnostics": {
    "a2a_tracing": {}, // A2A trace report
    "agent_inspection": {}, // Agent states report
    "colony_diagnostics": {}, // Colony health report
    "value_network_debug": {}, // Value network debug report
    "issue_detection": {} // Issues detected report
  },
  "recommendations": ["string"]
}
```

## Metrics Reference

### Agent Metrics

| Metric | Type | Description | Healthy Range |
|--------|------|-------------|---------------|
| `status` | string | Agent status | 'active' |
| `value_function` | float | TD(λ) value prediction | 0.4 - 0.9 |
| `success_rate` | float | Success / (success + failure) | > 0.6 |
| `avg_latency_ms` | float | Average execution latency | < 500 |
| `last_active` | timestamp | Last activity timestamp | < 300s ago |

### Resource Metrics

| Metric | Type | Description | Warning | Critical |
|--------|------|-------------|---------|----------|
| `cpu_percent` | float | CPU usage | 70% | 90% |
| `memory_mb` | float | Memory usage | 500MB | 900MB |
| `queue_depth` | int | Queue size | 500 | 2000 |
| `network_io_mb` | float | Network I/O | 100MB | - |

### Value Network Metrics

| Metric | Type | Description | Healthy Range |
|--------|------|-------------|---------------|
| `current_value` | float | Current value prediction | 0.2 - 0.9 |
| `stability_score` | float | Convergence stability | > 0.8 |
| `convergence_rate` | float | Rate of convergence | > 0.01 |
| `oscillation_frequency` | float | Oscillation frequency | 0.0 |
| `trend` | string | Value trend | 'stable' or 'increasing' |

### Colony Metrics

| Metric | Type | Description | Healthy Range |
|--------|------|-------------|---------------|
| `health_score` | float | Overall colony health | > 0.8 |
| `throughput` | float | Messages per second | > 10 |
| `avg_latency` | float | Average message latency | < 100ms |
| `cascade_risk` | float | Cascade failure probability | < 0.3 |

## Status Values

### Agent Status

- `dormant` - Agent not active
- `active` - Agent processing normally
- `hibernating` - Agent temporarily inactive
- `error` - Agent in error state

### Issue Severity

- `info` - Informational
- `warning` - Warning, needs attention
- `critical` - Critical, immediate action required

### Health Status

- `healthy` - Colony functioning normally
- `warning` - Some issues detected
- `critical` - Serious problems

## Thresholds

Default thresholds can be customized in each tool:

```python
thresholds = {
    # Resource thresholds
    'memory_mb_warning': 500,
    'memory_mb_critical': 900,
    'cpu_percent_warning': 70,
    'cpu_percent_critical': 90,
    'queue_depth_warning': 500,
    'queue_depth_critical': 2000,

    # Activity thresholds
    'idle_time_warning': 300,  # seconds
    'idle_time_critical': 600,

    # Value function thresholds
    'value_function_min': 0.1,
    'value_function_max': 0.9,
    'success_rate_min': 0.5
}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | File not found |
| 4 | Data format error |
| 5 | Threshold exceeded |

## Performance Considerations

### Memory Usage

- **A2A Tracer**: ~1MB per 1000 packages
- **Agent Inspector**: ~500KB per 100 agents
- **Colony Diagnostics**: ~200KB per 100 agents
- **Value Network Debugger**: ~100KB per 1000 updates
- **Replay Debugger**: ~5MB per 1000 events with snapshots

### CPU Usage

- **Real-time tracing**: ~5% CPU
- **Analysis operations**: ~20% CPU (burst)
- **Report generation**: ~30% CPU (burst)

### Storage

- **JSON reports**: ~1-10MB depending on colony size
- **HTML reports**: ~500KB
- **Replay recordings**: ~10-100MB depending on duration

## Integration Examples

### Python Integration

```python
from a2a_tracer import A2ATracer
from agent_inspector import AgentInspector
from colony_diagnostics import ColonyDiagnostics

# Create tools
tracer = A2ATracer("my_colony")
inspector = AgentInspector("my_colony")
diagnostics = ColonyDiagnostics("my_colony")

# Use programmatically
tracer.trace_package(package_data, "agent-1", "in_transit")
inspector.inspect_agent(agent_data)
diagnostics.check_agent_health("agent-1", agent_data)

# Get results
trace_report = tracer.generate_trace_report()
inspection_report = inspector.generate_inspection_report()
health_report = diagnostics.generate_health_report()
```

### CLI Integration

```bash
# Run all diagnostics
python diagnostic_generator.py colony_id colony_data.json

# Parse JSON output
jq '.overall_health_score' reports/diagnostics/diagnostic_report.json

# Check for critical issues
jq '.summary.critical_issues' reports/diagnostics/diagnostic_report.json
```

### Monitoring Integration

```bash
# Continuous monitoring
watch -n 300 'python issue_detector.py colony_id check colony_data.json'

# Alert on critical issues
critical=$(jq '.summary.critical_issues' reports/diagnostics/issues_detected.json)
if [ $critical -gt 0 ]; then
    echo "CRITICAL: $critical issues detected"
    # Send alert
fi
```

---

For more information, see the main README or DEBUGGING_GUIDE.
