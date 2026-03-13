# P35: Guardian Angels - Validation Criteria

**Paper:** P35 - Shadow Monitoring for Safety-Critical Systems
**Created:** 2026-03-13
**Status:** Research Phase - Claims to Validate

---

## Core Claims to Validate

### Claim 1: Early Failure Detection
**Statement:** Guardian angels detect failures >10 timesteps before they occur.

**Validation Criteria:**
- [ ] Implement shadow monitoring system
- [ ] Record detection time relative to actual failure
- [ ] Calculate early warning horizon
- [ ] Validate: mean_detection_time - failure_time > 10 timesteps

**Falsification Criteria:**
- If mean detection horizon < 5 timesteps
- If detection occurs after failure (negative horizon)
- If false positive rate > 30%

**Data Required:**
```python
{
    "failure_events": List[int],  # Timesteps when failures occurred
    "detection_times": List[int],  # Timesteps when detected
    "detection_horizons": List[int],  # detection - failure
    "mean_horizon": float,
    "min_horizon": int,
    "detection_rate": float,  # TP / (TP + FN)
    "false_positive_rate": float  # FP / (FP + TN)
}
```

---

### Claim 2: Zero Performance Overhead
**Statement:** Shadow monitoring adds <1% performance overhead to main system.

**Validation Criteria:**
- [ ] Measure system performance without guardian (baseline)
- [ ] Measure system performance with guardian active
- [ ] Calculate overhead percentage
- [ ] Validate: overhead < 1%

**Data Required:**
```python
{
    "baseline_latency_ms": float,
    "with_guardian_latency_ms": float,
    "overhead_percent": float,
    "baseline_throughput": float,  # requests/second
    "with_guardian_throughput": float,
    "memory_overhead_mb": float,
    "cpu_overhead_percent": float
}
```

---

### Claim 3: Intervention Effectiveness
**Statement:** Proactive intervention prevents >80% of predicted failures.

**Validation Criteria:**
- [ ] Detect impending failures via guardian
- [ ] Execute interventions (restart, scaling, rollback)
- [ ] Count prevented vs actual failures
- [ ] Validate: prevention_rate = prevented / (prevented + actual) > 0.8

**Data Required:**
```python
{
    "predicted_failures": int,
    "prevented_failures": int,
    "actual_failures": int,
    "prevention_rate": float,
    "intervention_types": Dict[str, int],  # restart, scale, rollback, etc.
    "intervention_success_rate": float  # Successful interventions / total
}
```

---

### Claim 4: Multi-Dimensional Health Monitoring
**Statement:** Combining multiple health metrics improves prediction accuracy >20% vs single metric.

**Validation Criteria:**
- [ ] Implement single-metric prediction (best individual metric)
- [ ] Implement multi-metric prediction (combined model)
- [ ] Compare prediction accuracies
- [ ] Validate: multi_metric_accuracy > single_metric_accuracy * 1.2

**Data Required:**
```python
{
    "single_metric_accuracy": float,
    "multi_metric_accuracy": float,
    "improvement_percent": float,
    "metrics_used": List[str],  # CPU, memory, error_rate, latency, etc.
    "feature_importance": Dict[str, float],  # Metric importance scores
    "correlation_matrix": np.ndarray  # Metric correlations
}
```

---

### Claim 5: Shadow System Fidelity
**Statement:** Shadow system predictions correlate >0.9 with actual system behavior.

**Validation Criteria:**
- [ ] Run shadow system in parallel with production
- [ ] Record shadow predictions vs actual outcomes
- [ ] Calculate correlation coefficient
- [ ] Validate: correlation > 0.9

**Data Required:**
```python
{
    "shadow_predictions": List[float],
    "actual_outcomes": List[float],
    "correlation_coefficient": float,
    "mean_absolute_error": float,
    "root_mean_squared_error": float,
    "prediction_latencies": List[float],  # Time to make prediction
    "shadow_resource_usage": Dict[str, float]  # CPU, memory
}
```

---

## Mathematical Formulation

### Failure Prediction Model
```
P(failure at t+τ | health_t) = σ(Σ w_i * h_i(t) + b)

where:
- health_t = [h_1(t), h_2(t), ..., h_n(t)]: Health metrics at time t
- w_i: Learned weights for each metric
- τ: Prediction horizon (timesteps into future)
- σ: Sigmoid function
```

### Shadow System Simulation
```
shadow_state_{t+1} = simulate(shadow_state_t, actions_t)
prediction_t = predict_outcome(shadow_state_t)

Constraint: prediction_t must be available before actual outcome
```

### Intervention Decision
```
if P(failure at t+τ) > threshold:
    execute_intervention(intervention_type)
    expected_benefit = prevented_damage - intervention_cost

Intervention types:
1. Scale: Add resources
2. Restart: Reset component
3. Rollback: Revert to previous version
4. Reroute: Redirect traffic
```

### Health Metrics (Multi-Dimensional)
```
health_vector = [
    cpu_utilization,  # 0-1
    memory_utilization,  # 0-1
    error_rate,  # errors/second
    latency_p99,  # milliseconds
    throughput,  # requests/second
    disk_io,  # MB/s
    network_in,  # MB/s
    network_out,  # MB/s
    queue_depth,  # pending requests
    connection_count  # active connections
]
```

---

## Simulation Parameters

### Guardian Configuration
| Parameter | Value | Description |
|-----------|-------|-------------|
| prediction_horizon | 10-20 timesteps | How far ahead to predict |
| health_check_interval | 1 timestep | Frequency of health checks |
| intervention_threshold | 0.7 | Probability threshold for action |
| shadow_update_rate | 1.0 | Shadow system sync rate |
| max_interventions_per_hour | 10 | Rate limit for interventions |

### Health Metric Thresholds
| Metric | Warning | Critical |
|--------|---------|----------|
| CPU Utilization | 70% | 90% |
| Memory Utilization | 75% | 90% |
| Error Rate | 1% | 5% |
| Latency P99 | 500ms | 2000ms |
| Queue Depth | 100 | 500 |

### Failure Injection Scenarios
1. **CPU Spike:** Sustained 100% CPU for 30 seconds
2. **Memory Leak:** Gradual memory exhaustion
3. **Network Partition:** 50% packet loss
4. **Disk Saturation:** 100% disk utilization
5. **Dependency Failure:** Downstream service unavailable

---

## Experimental Design

### Test Environments
1. **Microservice Cluster:** 10 services with dependencies
2. **Database System:** Primary-replica with connection pooling
3. **Message Queue:** Producer-consumer with backpressure
4. **API Gateway:** Load balancing with rate limiting

### Workload Patterns
1. **Constant:** Stable request rate
2. **Diurnal:** Day/night pattern
3. **Flash Crowd:** Sudden 10x spike
4. **Gradual Growth:** Linear increase over time

---

## Experimental Controls

### Baseline Comparisons
1. **No Guardian:** System runs without monitoring
2. **Reactive Monitoring:** Respond only after failures occur
3. **Single Metric:** Monitor only CPU utilization
4. **Threshold-Based:** Simple static thresholds (no ML)

### Ablation Studies
1. **No Shadow System:** Predict from main system metrics only
2. **No Intervention:** Detect but don't intervene
3. **Reduced Metrics:** Test with subsets of health metrics
4. **Different Horizons:** τ ∈ {5, 10, 20, 30}

---

## Success Thresholds

| Metric | Minimum Success | Target Success |
|--------|----------------|----------------|
| Detection Horizon | >5 timesteps | >10 timesteps |
| Performance Overhead | <2% | <1% |
| Prevention Rate | >70% | >80% |
| False Positive Rate | <30% | <20% |
| Multi-Metric Improvement | >15% | >20% |
| Shadow Fidelity | r > 0.85 | r > 0.9 |

---

## Failure Modes to Test

### 1. Cassandra Complex
**Scenario:** Guardian correctly predicts failure but interventions fail
**Detection:** High prediction accuracy but low prevention rate

### 2. False Positive Cascade
**Scenario:** Unnecessary interventions cause new failures
**Detection:** Intervention-triggered failures > 10% of total

### 3. Shadow Drift
**Scenario:** Shadow system diverges from production
**Detection:** Shadow-actual correlation drops below threshold

### 4. Intervention Overload
**Scenario:** Too many interventions degrade system performance
**Detection:** Performance overhead > 5% with active interventions

---

## Safety & Ethical Considerations

### Intervention Safety
```python
def safe_intervention(intervention_type, system_state):
    # Pre-intervention checks
    if not can_safely_execute(intervention_type, system_state):
        return False

    # Execute intervention with rollback plan
    result = execute(intervention_type)

    # Post-intervention validation
    if not validate_intervention(result):
        rollback(intervention_type)

    return result
```

### Ethical Requirements
1. **Transparency:** Log all interventions and reasons
2. **Accountability:** Human approval for high-impact interventions
3. **Fail-Safe:** Guardian must never cause catastrophic failure
4. **Privacy:** Health metrics must not leak sensitive data

---

## Cross-Paper Connections

### FOR Other Papers
- **P19 (Causal Traceability):** Guardian enables causal failure analysis
- **P34 (Federated Learning):** Guardian can monitor federated clients
- **P36 (Time-Travel Debug):** Guardian provides data for replay

### FROM Other Papers
- **P26 (Value Networks):** Value-guided intervention decisions
- **P31 (Health Prediction):** Multi-dimensional health metrics
- **P13 (Agent Networks):** Network topology affects failure propagation

### Synergies to Explore
- **P35 + P34:** Guardian monitoring federated learning clients
- **P35 + P36:** Guardian data for time-travel debugging
- **P35 + P19:** Causal failure tracing with guardian insights

---

## Validation Status

| Claim | Theoretical | Simulation | Status |
|-------|-------------|------------|--------|
| C1: Early detection (>10 steps) | ✓ | 🔲 Needed | Pending |
| C2: Zero overhead (<1%) | ✓ | 🔲 Needed | Pending |
| C3: Intervention effectiveness (>80%) | ✓ | 🔲 Needed | Pending |
| C4: Multi-metric improvement (>20%) | ✓ | 🔲 Needed | Pending |
| C5: Shadow fidelity (>0.9) | ✓ | 🔲 Needed | Pending |

---

## Next Steps

1. Implement shadow monitoring system framework
2. Create failure injection test suite
3. Test detection horizon and intervention effectiveness
4. Measure performance overhead in production-like environment
5. Document cross-paper findings with P19 (Causal) and P36 (Debug)
6. Update NEXT_PHASE_PAPERS.md with results

---

*Schema Version: 1.0*
*Last Updated: 2026-03-13*
