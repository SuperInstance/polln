# POLLN Robustness Testing Suite

Comprehensive adversarial testing framework for validating POLLN's resilience under attack conditions.

## Overview

This suite tests POLLN's ability to withstand and recover from various adversarial conditions, including prompt injection, Byzantine attacks, cascading failures, state corruption, and resource exhaustion.

## Simulations

### 1. Prompt Injection Testing (`prompt_injection.py`)

Tests resilience against adversarial input attacks.

**Attack Types:**
- Jailbreak attempts (DAN, role-playing)
- Context overflow attacks
- Instruction override attempts
- Poisoned context injections
- Base64 encoded payloads

**Metrics:**
- Attack detection rate
- Block success rate
- Response time
- False positive rate

**Usage:**
```python
from prompt_injection import PromptInjectionSimulator

simulator = PromptInjectionSimulator(seed=42)
metrics = simulator.run_simulation(num_iterations=10)
simulator.print_metrics()
```

### 2. Byzantine Fault Tolerance (`byzantine_agents.py`)

Tests tolerance to malicious agents in the network.

**Attack Types:**
- Liar agents (always false values)
- Flipper agents (random decisions)
- Colluding agents (coordinated attacks)
- Sybil attacks (multiple identities)

**Aggregation Strategies:**
- Simple mean
- Median (robust to outliers)
- Trimmed mean (removes extremes)
- WELS (Weighted Elastic Least Squares)

**Metrics:**
- System performance vs attack fraction
- Convergence rate
- Malicious detection rate
- Resilience threshold

**Usage:**
```python
from byzantine_agents import ByzantineSimulator, AggregationStrategy

simulator = ByzantineSimulator(
    num_agents=100,
    malicious_fraction=0.2,
    aggregation_strategy=AggregationStrategy.TRIMMED_MEAN,
)
metrics = simulator.run_simulation(num_rounds=50)
simulator.find_resilience_threshold()
```

### 3. Cascading Failure Simulation (`cascade_failure.py`)

Tests containment of failure propagation.

**Failure Types:**
- Agent crashes
- Network partitions
- Resource exhaustion
- Dependency failures

**Containment Strategies:**
- Circuit breaking
- Rate limiting
- Bulkheading (isolation)
- Timeouts

**Metrics:**
- Failure propagation rate
- Cascade depth
- Containment effectiveness
- System recovery time

**Usage:**
```python
from cascade_failure import CascadingFailureSimulator, ContainmentStrategy

simulator = CascadingFailureSimulator(
    num_agents=100,
    initial_failure_rate=0.05,
    containment_strategies=[
        ContainmentStrategy.CIRCUIT_BREAKER,
        ContainmentStrategy.RATE_LIMITING,
    ],
)
metrics = simulator.run_simulation(max_steps=100)
```

### 4. State Corruption Recovery (`state_corruption.py`)

Tests detection and recovery from corrupted state.

**Corruption Types:**
- Value network corruption
- World model corruption
- Communication history poisoning
- Synaptic weight alteration
- Reputation manipulation

**Recovery Strategies:**
- Checkpoint rollback
- Peer validation
- Consensus recovery
- Anomaly detection

**Metrics:**
- Corruption detection rate
- Recovery success rate
- Recovery time
- Data loss percentage

**Usage:**
```python
from state_corruption import StateCorruptionSimulator, RecoveryStrategy

simulator = StateCorruptionSimulator(
    num_agents=50,
    checkpoint_frequency=10,
    recovery_strategies=[
        RecoveryStrategy.CHECKPOINT_ROLLBACK,
        RecoveryStrategy.PEER_VALIDATION,
    ],
)
metrics = simulator.run_simulation(num_steps=100)
```

### 5. Resource Exhaustion Testing (`resource_exhaustion.py`)

Tests graceful degradation under resource pressure.

**Resource Types:**
- CPU exhaustion
- Memory exhaustion
- Network saturation
- Cache overflow
- Disk I/O exhaustion

**Mitigation Strategies:**
- Throttling
- Load shedding
- Caching
- Queue management

**Metrics:**
- Performance degradation rate
- Task completion rate
- System stability index
- Recovery time

**Usage:**
```python
from resource_exhaustion import ResourceExhaustionSimulator, MitigationStrategy

simulator = ResourceExhaustionSimulator(
    num_agents=50,
    base_load=0.5,
    peak_load=1.5,
    mitigation_strategies=[
        MitigationStrategy.THROTTLING,
        MitigationStrategy.LOAD_SHEDDING,
    ],
)
metrics = simulator.run_simulation(num_steps=100, surge_at_step=30)
```

## Running Simulations

### Run All Simulations

```bash
# Full comprehensive testing
python run_all.py

# Quick testing (reduced iterations)
python run_all.py --quick

# Generate TypeScript hardening config
python run_all.py --generate-config
```

### Run Individual Simulations

```bash
# Prompt injection testing
python prompt_injection.py

# Byzantine fault tolerance
python byzantine_agents.py

# Cascading failure
python cascade_failure.py

# State corruption
python state_corruption.py

# Resource exhaustion
python resource_exhaustion.py
```

### Run Tests

```bash
# Run all tests
pytest test_robustness.py -v

# Run specific test class
pytest test_robustness.py::TestPromptInjection -v

# Run with coverage
pytest test_robustness.py --cov=. --cov-report=html
```

## Output

### Simulation Results

Results are saved to `simulations/advanced/robustness/results/`:

- `prompt_injection_results.json`
- `byzantine_results.json`
- `cascade_failure_results.json`
- `state_corruption_results.json`
- `resource_exhaustion_results.json`
- `comprehensive_security_report.json`
- `comprehensive_security_report.md`

### Hardening Configurations

When run with `--generate-config`:

- `src/core/security/hardening.ts` - TypeScript configuration module
- `docs/SECURITY_GUIDE.md` - Comprehensive security guide

## Configuration

### Simulation Parameters

Each simulator accepts configuration parameters:

```python
simulator = PromptInjectionSimulator(
    seed=42,  # Random seed for reproducibility
)

simulator = ByzantineSimulator(
    num_agents=100,              # Total agents
    malicious_fraction=0.2,      # Fraction that are malicious
    aggregation_strategy=...,    # Aggregation method
)
```

### Safety Configuration

Safety settings can be customized:

```python
simulator.safety_config = {
    'max_input_length': 100000,
    'max_turns': 100,
    'blocked_patterns': [...],
    'sanitization': 'aggressive',
}
```

## Metrics Interpretation

### Prompt Injection

- **Detection Rate**: Should be > 95%
- **Block Rate**: Should be > 90%
- **Response Time**: Should be < 100ms
- **False Positive Rate**: Should be < 5%

### Byzantine Tolerance

- **Resilience Threshold**: Should tolerate > 20% malicious
- **Detection Rate**: Should be > 80%
- **Convergence**: Should converge in < 50 rounds

### Cascade Prevention

- **Containment Effectiveness**: Should be > 70%
- **Cascade Depth**: Should be < 5 levels
- **Healthy Agents**: Should remain > 50%

### State Protection

- **Detection Rate**: Should be > 90%
- **Recovery Success Rate**: Should be > 80%
- **Data Loss**: Should be < 10%

### Resource Management

- **Task Completion Rate**: Should be > 80% under stress
- **System Stability**: Should be > 0.5
- **Recovery Time**: Should be < 1000ms

## Architecture

```
simulations/advanced/robustness/
├── prompt_injection.py          # Adversarial input testing
├── byzantine_agents.py          # Byzantine fault tolerance
├── cascade_failure.py           # Failure propagation
├── state_corruption.py          # State corruption recovery
├── resource_exhaustion.py       # Resource stress testing
├── hardening_generator.py       # Config generation
├── run_all.py                   # Master orchestrator
├── test_robustness.py           # Unit tests
├── README.md                    # This file
└── results/                     # Simulation outputs
    ├── prompt_injection_results.json
    ├── byzantine_results.json
    ├── cascade_failure_results.json
    ├── state_corruption_results.json
    ├── resource_exhaustion_results.json
    └── comprehensive_security_report.json
```

## Contributing

When adding new simulations:

1. Create a new simulation file following the existing pattern
2. Implement required methods: `run_simulation()`, `print_metrics()`, `save_results()`
3. Add configuration generation method
4. Add unit tests to `test_robustness.py`
5. Update `run_all.py` to include new simulation
6. Update this README with documentation

## Dependencies

```bash
pip install numpy scipy networkx
pip install pytest pytest-cov  # For testing
```

## License

MIT License - See main repository LICENSE file.

## Support

For questions or issues:
- Main documentation: `docs/ARCHITECTURE.md`
- Security guide: `docs/SECURITY_GUIDE.md`
- Create an issue on GitHub
