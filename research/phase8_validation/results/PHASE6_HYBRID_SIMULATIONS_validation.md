# Validation Report: PHASE6_HYBRID_SIMULATIONS

## Hybrid multi-paper simulations combining P12, P13, P19, P20, P27

**Validation Date:** 2026-03-13 17:55:19

**Overall Validated:** [FAIL] NO

**Statistical Power:** 0.400

**Reproducibility Score:** 0.928

**Generation Time:** 0.01s


## Claims Validation

### HYBRID-001: [OK] PASSED

- **Description:** Causal CRDT achieves 96.3% consensus rate

- **Mean:** 0.9481 ± 0.0217

- **95% CI:** [0.9438, 0.9524]

- **Confidence:** 99.7%


**Statistical Tests:**

- [OK] **One-Sample t-Test**: 
statistic=-6.8902, 
p=0.0000, 
d=nan (Large)

- [OK] **Wilcoxon Signed-Rank Test**: 
statistic=784.0000, 
p=0.0000, 
d=nan (Large)

- [FAIL] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0100, 
d=0.0000 (Negligible)

### HYBRID-002: [OK] PASSED

- **Description:** Causal CRDT achieves 57% compression

- **Mean:** 0.5707 ± 0.0285

- **95% CI:** [0.5650, 0.5763]

- **Confidence:** 46.3%


**Statistical Tests:**

- [FAIL] **One-Sample t-Test**: 
statistic=0.2315, 
p=0.8174, 
d=nan (Large)

- [FAIL] **Wilcoxon Signed-Rank Test**: 
statistic=2430.0000, 
p=0.7439, 
d=nan (Large)

- [OK] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0500, 
d=0.0000 (Negligible)

### HYBRID-003: [FAIL] FAILED

- **Description:** Topology-Emergence correlation r=0.78

- **Mean:** 0.7727 ± 0.0843

- **95% CI:** [0.7560, 0.7894]

- **Confidence:** 70.9%


**Statistical Tests:**

- [FAIL] **One-Sample t-Test**: 
statistic=-0.8648, 
p=0.3892, 
d=nan (Large)

- [FAIL] **Wilcoxon Signed-Rank Test**: 
statistic=2297.0000, 
p=0.4331, 
d=nan (Large)

- [OK] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0500, 
d=0.0000 (Negligible)

### HYBRID-004: [FAIL] FAILED

- **Description:** Consensus-Memory reduces messages by 42%

- **Mean:** 0.4170 ± 0.0410

- **95% CI:** [0.4089, 0.4251]

- **Confidence:** 66.4%


**Statistical Tests:**

- [FAIL] **One-Sample t-Test**: 
statistic=-0.7332, 
p=0.4652, 
d=nan (Large)

- [FAIL] **Wilcoxon Signed-Rank Test**: 
statistic=2326.0000, 
p=0.4938, 
d=nan (Large)

- [OK] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0500, 
d=0.0000 (Negligible)

### HYBRID-005: [FAIL] FAILED

- **Description:** Emergent Coordination 1.89x faster in small-world

- **Mean:** 1.8810 ± 0.1535

- **95% CI:** [1.8505, 1.9114]

- **Confidence:** 57.4%


**Statistical Tests:**

- [FAIL] **One-Sample t-Test**: 
statistic=-0.5896, 
p=0.5568, 
d=nan (Large)

- [FAIL] **Wilcoxon Signed-Rank Test**: 
statistic=2401.0000, 
p=0.6699, 
d=nan (Large)

- [OK] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0500, 
d=0.0000 (Negligible)


## Recommendations

- 3 claims failed validation - review methodology

- Low statistical power (0.40) - increase sample size
