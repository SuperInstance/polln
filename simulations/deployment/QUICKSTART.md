# Deployment Simulations - Quick Start Guide

Get started with deployment simulations in 5 minutes.

## Prerequisites

- Python 3.8+
- pip package manager

## Installation

```bash
cd simulations/deployment

# Install dependencies
pip install -r requirements.txt
```

Or install manually:

```bash
pip install numpy matplotlib pytest
```

## Run Your First Simulation

### Option 1: Run All Simulations

```bash
python run_all.py
```

This will:
- Run all 4 deployment pattern simulations
- Compare strategies across dimensions
- Generate recommendations
- Validate hypotheses
- Save results to `results/latest_results.json`

### Option 2: Run Individual Simulation

**Rolling Deployment:**
```bash
python rolling_deployment.py
```

**Blue-Green Deployment:**
```bash
python blue_green_deployment.py
```

**Canary Deployment:**
```bash
python canary_deployment.py
```

**Rollback Simulation:**
```bash
python rollback_simulation.py
```

## Understanding the Output

### Rolling Deployment Output

```
ROLLING DEPLOYMENT: v1.0 → v1.1
Instances: 10
Batch sizes: [0.01, 0.05, 0.10, 0.25, 0.50, 1.0]

Deploying batch: 1.0% (1 instances)
✓ Batch completed in 2.45s (downtime: 0.012s)

Deploying batch: 5.0% (5 instances)
✓ Batch completed in 12.34s (downtime: 0.087s)
...

============================================================
Deployment Results:
  Success: True
  Total time: 45.23s
  Total downtime: 0.087s
  H1 (< 1s downtime): ✓ PASS
============================================================
```

**Key Metrics:**
- **Success**: Did deployment complete successfully?
- **Total time**: Full deployment duration
- **Total downtime**: Time when service was unavailable
- **H1**: Hypothesis 1 validation (< 1s downtime)

### Blue-Green Deployment Output

```
BLUE-GREEN DEPLOYMENT: v1.0 → v1.1
Instances: 10 per environment

[timestamp] Starting deployment to green
[timestamp] Testing green environment
[timestamp] Switching traffic from blue to green
[timestamp] Traffic cutover complete

============================================================
Deployment Summary:
  Result: True
  Reason: Deployment successful
  Deployment time: 32.45s
  Cutover time: 0.010s
  Downtime: 0.010s
============================================================
```

**Key Metrics:**
- **Deployment time**: Time to deploy and test green environment
- **Cutover time**: Time to switch traffic (nearly instant)
- **Downtime**: Equals cutover time for blue-green

### Canary Deployment Output

```
CANARY DEPLOYMENT: v1.0 → v1.1
Instances: 100
Rollout schedule: ['1%', '5%', '25%', '100%']
Regression: False

📍 Phase 1: 1% canary
   Created 1 canary instances
   Monitoring: 30s / 300s
   ...
   ✓ Phase complete: No regressions detected

📍 Phase 2: 5% canary
   Created 4 canary instances
   ...

✓ CANARY DEPLOYMENT SUCCESSFUL
   Total time: 1234.5s
   Final canary percentage: 100%
```

**Key Metrics:**
- **Phase duration**: Time spent testing each canary level
- **Regression detected**: Whether issues were found
- **Detection time**: Time until regression identified

### Rollback Simulation Output

```
📍 Triggering rollback: full_rollback
   Executing full rollback...
   ✓ Traffic redirect complete in 0.010s
   ✓ State restore complete in 2.456s
   ✓ State consistency verified

Result:
  Success: True
  Rollback time: 2.456s
  State consistent: True
```

**Key Metrics:**
- **Rollback time**: Time to complete rollback
- **State consistent**: Whether state was fully restored

## Customizing Simulations

### Change Instance Count

```python
# Rolling deployment with 100 instances
simulator = RollingDeploymentSimulator(
    num_instances=100,
    current_version="v1.0",
    target_version="v1.1"
)
```

### Change Batch Sizes

```python
# Conservative batch sizes
simulator = RollingDeploymentSimulator(
    num_instances=10,
    current_version="v1.0",
    target_version="v1.1",
    batch_sizes=[0.01, 0.02, 0.05, 0.10, 0.25, 0.50, 1.0]
)
```

### Simulate Regression

```python
# Canary with performance regression
simulator = CanaryDeploymentSimulator(
    num_instances=100,
    baseline_version="v1.0",
    canary_version="v1.1",
    regression={
        "has_regression": True,
        "type": RegressionType.PERFORMANCE,
        "severity": 2.0
    }
)
```

### Change Rollback Type

```python
# Test different rollback strategies
result = simulator.trigger_rollback(
    snapshots,
    RollbackType.VERSION_REVERT    # Fastest
    # or
    RollbackType.STATE_RESTORE     # Safest
    # or
    RollbackType.TRAFFIC_REDIRECT  # Instant
    # or
    RollbackType.FULL_ROLLBACK     # Complete
)
```

## Run Tests

```bash
# Run all tests
pytest test_deployment.py -v

# Run specific test
pytest test_deployment.py::TestRollingDeployment::test_rolling_deployment_basic -v

# Run with coverage
pytest test_deployment.py --cov=. --cov-report=html
```

## View Results

Results are saved in JSON format:

```bash
# View latest results
cat results/latest_results.json

# Or pretty-print
python -m json.tool results/latest_results.json
```

### Parse Results Programmatically

```python
import json

with open('results/latest_results.json', 'r') as f:
    results = json.load(f)

# Check hypothesis validation
for key, hypothesis in results['hypothesis_validation'].items():
    if key != 'overall':
        print(f"{key}: {hypothesis['status']}")

# Get recommendations
for scenario, strategy in results['recommendations'].items():
    print(f"{scenario}: {strategy}")
```

## Common Use Cases

### 1. Test Emergency Hotfix Deployment

```python
from blue_green_deployment import BlueGreenDeploymentSimulator

simulator = BlueGreenDeploymentSimulator(
    num_instances=10,
    blue_version="v1.0",
    green_version="v1.0.1",  # Hotfix
    enable_auto_rollback=True
)

result = simulator.run_deployment()
print(f"Hotfix deployed in {result['deployment_time']:.2f}s")
```

### 2. Test Canary Detection Capability

```python
from canary_deployment import CanaryDeploymentSimulator, RegressionType

# Test with different regression types
for regression_type in [
    RegressionType.PERFORMANCE,
    RegressionType.ERROR_RATE,
    RegressionType.SUBTLE
]:
    simulator = CanaryDeploymentSimulator(
        num_instances=100,
        baseline_version="v1.0",
        canary_version="v1.1",
        regression={
            "has_regression": True,
            "type": regression_type,
            "severity": 2.0
        }
    )

    result = simulator.run_canary_deployment()

    if result['regression_detected']:
        print(f"{regression_type.value}: Detected in {result['detection_time']:.1f}s")
    else:
        print(f"{regression_type.value}: NOT DETECTED")
```

### 3. Find Optimal Batch Size

```python
from rolling_deployment import RollingDeploymentSimulator

simulator = RollingDeploymentSimulator(
    num_instances=50,
    current_version="v1.0",
    target_version="v1.1"
)

analysis = simulator.analyze_optimal_batch_size()
print(f"Optimal batch size: {analysis['optimal_batch_size']*100:.1f}%")
```

### 4. Validate Rollback Safety

```python
from rollback_simulation import RollbackSimulator, RollbackType

simulator = RollbackSimulator(
    num_instances=20,
    old_version="v1.0",
    new_version="v1.1"
)

# Deploy
snapshots = simulator.deploy_new_version()

# Rollback with full state restore
result = simulator.trigger_rollback(snapshots, RollbackType.FULL_ROLLBACK)

print(f"Rollback time: {result['rollback_time']:.3f}s")
print(f"State consistent: {result['state_consistent']}")
```

## Troubleshooting

### Import Errors

If you get import errors:

```bash
# Make sure you're in the right directory
cd simulations/deployment

# Check Python path
python -c "import sys; print(sys.path)"
```

### Simulation Takes Too Long

Reduce instance count or trials:

```python
# Use fewer instances
simulator = RollingDeploymentSimulator(
    num_instances=5,  # Instead of 10 or 100
    ...
)
```

### Tests Fail

Check test output for specific failures:

```bash
pytest test_deployment.py -v --tb=long
```

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore individual simulation modules
3. Check out [STRATEGIES.md](STRATEGIES.md) for deployment strategy guidance
4. Review [CHECKLIST.md](CHECKLIST.md) for pre-deployment verification

## Support

For issues or questions:
- Check the main POLLN documentation
- Review simulation source code comments
- Run tests to verify your environment
