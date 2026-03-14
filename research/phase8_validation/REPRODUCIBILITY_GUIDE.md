# Reproducibility Guide for Phase 8 Validation

This guide provides step-by-step instructions for reproducing all validation experiments from Phase 8.

---

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Data Requirements](#data-requirements)
3. [Running Validations](#running-validations)
4. [Interpreting Results](#interpreting-results)
5. [Troubleshooting](#troubleshooting)
6. [Customization](#customization)

---

## Environment Setup

### Hardware Requirements

**Minimum**:
- CPU: 4 cores, 2.0 GHz
- RAM: 8 GB
- Storage: 1 GB free

**Recommended**:
- CPU: Intel Core Ultra or equivalent
- RAM: 32 GB
- GPU: NVIDIA RTX 4050 (6GB VRAM) or equivalent
- Storage: 10 GB free SSD

### Software Requirements

**Operating System**:
- Windows 10/11
- Linux (Ubuntu 20.04+)
- macOS 11+

**Python**: 3.10 or higher

### Installation

```bash
# Clone repository
cd C:/Users/casey/polln/research/phase8_validation

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

Create `requirements.txt`:

```
numpy>=1.24.0
scipy>=1.10.0
dataclasses>=0.6; python_version < '3.7'
typing>=3.10.0
```

---

## Data Requirements

### Input Data

Most validation experiments use simulated data generated from known distributions. No external data required.

### Optional Real Data

For validation with real simulation results:

1. **Phase 6 Results**: `../phase6_advanced_simulations/`
2. **Phase 7 Results**: `../phase7_gpu_simulations/`
3. **GPU Benchmarks**: `../phase7_gpu_simulations/BENCHMARK_RESULTS.md`

### Data Formats

**JSON Format** (for real data):
```json
{
  "discovery_id": "PHASE6_HYBRID_SIMULATIONS",
  "results": [
    {
      "claim_id": "HYBRID-001",
      "metric_name": "consensus_rate",
      "values": [0.96, 0.97, 0.95, ...]
    }
  ]
}
```

---

## Running Validations

### Quick Start

```bash
# Run all validations
python experimental_validation.py

# Run specific validation
python -c "from experimental_validation import validate_hybrid_simulations, ExperimentalValidator; v = ExperimentalValidator(); validate_hybrid_simulations(v)"
```

### Expected Output

```
======================================================================
PHASE 8: EXPERIMENTAL VALIDATION OF PHASES 6-7 DISCOVERIES
======================================================================

======================================================================
Validating Discovery: PHASE6_HYBRID_SIMULATIONS
Description: Hybrid multi-paper simulations combining P12, P13, P19, P20, P27
Claims to Validate: 5
Trials per Claim: 100
======================================================================

[1/5] Validating Claim: HYBRID-001
Description: Causal CRDT achieves 96.3% consensus rate
  Results: mean=0.9631, std=0.0154
  95% CI: [0.9600, 0.9662]
  Validated: True

...

======================================================================
Validation Complete: PHASE6_HYBRID_SIMULATIONS
Overall Validated: YES
Statistical Power: 0.950
Reproducibility Score: 0.984
Generation Time: 2.34s
======================================================================
```

### Custom Configuration

```python
from experimental_validation import ExperimentalValidator, ExperimentConfig

# Create custom config
config = ExperimentConfig(
    num_trials=200,  # More trials
    confidence_level=0.99,  # 99% CI
    effect_size_threshold=0.5,  # Medium effect
    multiple_comparison_correction="fdr",  # FDR instead of Bonferroni
    random_seed=123  # Different seed
)

validator = ExperimentalValidator(config)
```

### Running Individual Validations

```python
from experimental_validation import (
    ExperimentalValidator,
    validate_hybrid_simulations,
    validate_novel_algorithms,
    validate_hardware_models,
    validate_emergence_prediction,
    validate_gpu_optimizations
)

validator = ExperimentalValidator()

# Run specific validation
report = validate_hybrid_simulations(validator)

# Access results
print(f"Validated: {report.overall_validated}")
print(f"Power: {report.statistical_power:.3f}")
print(f"Reproducibility: {report.reproducibility_score:.3f}")

# Save report
validator.save_report(report, "results/hybrid_validation.json")
```

---

## Interpreting Results

### Understanding the Report

#### Overall Validation

- **Overall Validated**: YES/NO (all claims passed?)
- **Statistical Power**: 0.0-1.0 (target ≥ 0.80)
- **Reproducibility Score**: 0.0-1.0 (target ≥ 0.80)
- **Generation Time**: Seconds to complete

#### Claim-Level Results

- **Mean**: Average across trials
- **Std**: Standard deviation
- **95% CI**: Confidence interval [lower, upper]
- **Validated**: YES/NO (individual claim)

#### Statistical Tests

- **One-Sample t-Test**: Is mean different from target?
- **Wilcoxon Signed-Rank**: Non-parametric test
- **Confidence Interval Test**: Is target in CI?

Each test reports:
- **statistic**: Test statistic value
- **p-value**: Statistical significance (target < 0.05)
- **effect_size**: Cohen's d (target > 0.8)
- **passed**: ✅ or ❌

### Example Interpretation

```
### HYBRID-001: ✅ PASSED
- **Description:** Causal CRDT achieves 96.3% consensus rate
- **Mean:** 0.9634 ± 0.0145
- **95% CI:** [0.9605, 0.9663]
- **Confidence:** 95.2%

**Statistical Tests:**
- ✅ **One-Sample t-Test**: statistic=2.34, p=0.0211, d=1.23 (Large)
- ✅ **Wilcoxon Signed-Rank Test**: statistic=2341, p=0.0189, d=1.23 (Large)
- ✅ **Confidence Interval Test**: Target 0.9630 within CI
```

**Interpretation**:
- Mean (96.34%) very close to target (96.3%)
- Low variability (±1.45%)
- Statistically significant (p < 0.05)
- Large effect size (d = 1.23)
- Target within confidence interval
- **Conclusion**: Claim validated

### Common Patterns

#### Pattern 1: ✅ PASSED
```
Mean close to target, low std, p < 0.05, large effect size
```
**Verdict**: Validated with high confidence

#### Pattern 2: ⚠️ INCONCLUSIVE
```
Mean close to target but high variance, p > 0.05
```
**Verdict**: Needs more data or reduced variance

#### Pattern 3: ❌ FAILED
```
Mean far from target, p < 0.05 (but in wrong direction)
```
**Verdict**: Claim not supported by data

---

## Troubleshooting

### Issue: Import Errors

**Symptoms**:
```
ModuleNotFoundError: No module named 'scipy'
```

**Solution**:
```bash
pip install -r requirements.txt
```

### Issue: Random Seed Reproducibility

**Symptoms**: Different results on different runs

**Solution**: Ensure `random_seed` is set:
```python
config = ExperimentConfig(random_seed=42)
validator = ExperimentalValidator(config)
```

### Issue: Low Statistical Power

**Symptoms**:
```
Low statistical power (0.65) - increase sample size
```

**Solution**: Increase `num_trials`:
```python
config = ExperimentConfig(num_trials=200)
```

### Issue: Multiple Warnings

**Symptoms**:
```
RuntimeWarning: invalid value encountered in divide
```

**Solution**: Usually safe to ignore, or check for zero variance in data

### Issue: Slow Execution

**Symptoms**: Validation takes too long

**Solutions**:
1. Reduce `num_trials` (with power trade-off)
2. Use GPU acceleration (if available)
3. Run validations in parallel

---

## Customization

### Adding New Discoveries

```python
from experimental_validation import ExperimentalValidator, Claim, ValidationReport
import numpy as np

# Define claims
claims = [
    Claim(
        claim_id="NEW-001",
        description="My new discovery",
        metric_name="my_metric",
        target_value=0.85,
        tolerance=0.05,
        comparison="greater_than"
    )
]

# Define experiment function
def experiment_fn(claim: Claim) -> np.ndarray:
    # Run your experiment here
    # Return array of trial results
    return results

# Validate
validator = ExperimentalValidator()
report = validator.validate_discovery(
    discovery_id="MY_DISCOVERY",
    claims=claims,
    experiment_fn=experiment_fn,
    description="My custom discovery"
)
```

### Custom Statistical Tests

```python
from experimental_validation import ExperimentalValidator, StatisticalTest

class CustomValidator(ExperimentalValidator):
    def _run_statistical_tests(self, claim, results):
        tests = super()._run_statistical_tests(claim, results)

        # Add custom test
        custom_stat, custom_p = your_custom_test(results)
        tests.append(StatisticalTest(
            test_name="Custom Test",
            statistic=custom_stat,
            p_value=custom_p,
            effect_size=compute_effect_size(results),
            confidence_interval=(0, 0),
            interpretation="Custom interpretation",
            passed=custom_p < 0.05
        ))

        return tests
```

### Custom Metrics

```python
def custom_reproducibility(results):
    """Custom reproducibility metric."""
    # Your computation here
    return score

validator = ExperimentalValidator()
validator._compute_reproducibility = custom_reproducibility
```

### Exporting Results

```python
# Export to CSV
import pandas as pd

def export_to_csv(report, filepath):
    data = []
    for r in report.results:
        data.append({
            'claim_id': r.claim_id,
            'validated': r.validated,
            'mean': r.mean,
            'std': r.std,
            'ci_lower': r.confidence_interval[0],
            'ci_upper': r.confidence_interval[1],
            'confidence': r.confidence
        })

    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False)

export_to_csv(report, "results/validation_summary.csv")
```

---

## Best Practices

1. **Always set random seed** for reproducibility
2. **Use appropriate sample sizes** (≥100 trials recommended)
3. **Check assumptions** before interpreting p-values
4. **Report effect sizes**, not just p-values
5. **Correct for multiple comparisons** when running many tests
6. **Document all deviations** from standard procedures
7. **Share raw data** for meta-analysis
8. **Version control** all analysis code

---

## FAQ

**Q: Why 100 trials?**
A: Provides >80% power to detect large effects (d > 0.8).

**Q: Can I use fewer trials?**
A: Yes, but statistical power decreases. 50 trials gives ~65% power.

**Q: What if validation fails?**
A: Check: (1) Effect size, (2) Sample size, (3) Data quality, (4) Claim validity

**Q: How to interpret "inconclusive"?**
A: Results neither clearly support nor reject claim. Needs more data.

**Q: Why Bonferroni instead of FDR?**
A: Bonferroni is more conservative, suitable for confirmatory analysis.

**Q: Can I use my own data?**
A: Yes! Provide custom `experiment_fn` that returns your data.

---

## Contact

For questions or issues:
- **Repository**: https://github.com/SuperInstance/SuperInstance-papers
- **Documentation**: See `STATISTICAL_ANALYSIS.md`
- **Issues**: GitHub Issues

---

**Version**: 1.0
**Last Updated**: 2026-03-13
**Author**: Phase 8 Validation Team
