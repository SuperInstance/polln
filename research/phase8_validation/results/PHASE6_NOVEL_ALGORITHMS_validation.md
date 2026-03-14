# Validation Report: PHASE6_NOVEL_ALGORITHMS

## Novel algorithms discovered through automated exploration

**Validation Date:** 2026-03-13 17:55:19

**Overall Validated:** [FAIL] NO

**Statistical Power:** 0.600

**Reproducibility Score:** 0.958

**Generation Time:** 0.01s


## Claims Validation

### ALG-001: [FAIL] FAILED

- **Description:** STL-002 Pattern Mining achieves 170% improvement

- **Mean:** 1.6870 ± 0.1020

- **95% CI:** [1.6668, 1.7072]

- **Confidence:** 85.7%


**Statistical Tests:**

- [FAIL] **One-Sample t-Test**: 
statistic=-1.2747, 
p=0.2054, 
d=nan (Large)

- [FAIL] **Wilcoxon Signed-Rank Test**: 
statistic=2130.0000, 
p=0.1744, 
d=nan (Large)

- [OK] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0500, 
d=0.0000 (Negligible)

### ALG-002: [OK] PASSED

- **Description:** QIO-002 Phase-Encoded Search achieves 78% improvement

- **Mean:** 0.7827 ± 0.0507

- **95% CI:** [0.7726, 0.7927]

- **Confidence:** 67.1%


**Statistical Tests:**

- [FAIL] **One-Sample t-Test**: 
statistic=0.5281, 
p=0.5986, 
d=nan (Large)

- [FAIL] **Wilcoxon Signed-Rank Test**: 
statistic=2246.0000, 
p=0.3374, 
d=nan (Large)

- [OK] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0500, 
d=0.0000 (Negligible)

### ALG-003: [OK] PASSED

- **Description:** CSL-002 Causal Models novelty 0.891

- **Mean:** 0.8919 ± 0.0223

- **95% CI:** [0.8875, 0.8963]

- **Confidence:** 54.5%


**Statistical Tests:**

- [FAIL] **One-Sample t-Test**: 
statistic=0.4083, 
p=0.6840, 
d=nan (Large)

- [FAIL] **Wilcoxon Signed-Rank Test**: 
statistic=2385.0000, 
p=0.6303, 
d=nan (Large)

- [OK] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0500, 
d=0.0000 (Negligible)

### ALG-004: [FAIL] FAILED

- **Description:** EML-002 Predictive Coding novelty 0.867

- **Mean:** 0.8668 ± 0.0248

- **95% CI:** [0.8618, 0.8717]

- **Confidence:** 34.5%


**Statistical Tests:**

- [FAIL] **One-Sample t-Test**: 
statistic=-0.0956, 
p=0.9240, 
d=nan (Large)

- [FAIL] **Wilcoxon Signed-Rank Test**: 
statistic=2522.0000, 
p=0.9918, 
d=nan (Large)

- [OK] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0500, 
d=0.0000 (Negligible)

### ALG-005: [OK] PASSED

- **Description:** TOL-002 Spectral Gap novelty 0.878

- **Mean:** 0.8784 ± 0.0262

- **95% CI:** [0.8732, 0.8836]

- **Confidence:** 39.3%


**Statistical Tests:**

- [FAIL] **One-Sample t-Test**: 
statistic=0.1477, 
p=0.8829, 
d=nan (Large)

- [FAIL] **Wilcoxon Signed-Rank Test**: 
statistic=2484.0000, 
p=0.8879, 
d=nan (Large)

- [OK] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0500, 
d=0.0000 (Negligible)


## Recommendations

- 2 claims failed validation - review methodology

- Low statistical power (0.60) - increase sample size
