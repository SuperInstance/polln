# Validation Report: PHASE7_GPU_OPTIMIZATIONS

## GPU-accelerated simulations on NVIDIA RTX 4050

**Validation Date:** 2026-03-13 17:55:19

**Overall Validated:** [FAIL] NO

**Statistical Power:** 0.500

**Reproducibility Score:** 0.943

**Generation Time:** 0.00s


## Claims Validation

### GPU-001: [FAIL] FAILED

- **Description:** CRDT 59x speedup

- **Mean:** 58.7983 ± 3.3361

- **95% CI:** [58.1363, 59.4602]

- **Confidence:** 54.9%


**Statistical Tests:**

- [FAIL] **One-Sample t-Test**: 
statistic=-0.6047, 
p=0.5468, 
d=nan (Large)

- [FAIL] **Wilcoxon Signed-Rank Test**: 
statistic=2435.0000, 
p=0.7570, 
d=nan (Large)

- [OK] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0500, 
d=0.0000 (Negligible)

### GPU-002: [OK] PASSED

- **Description:** Transfer Entropy 46x speedup

- **Mean:** 46.4044 ± 2.9819

- **95% CI:** [45.8127, 46.9961]

- **Confidence:** 88.9%


**Statistical Tests:**

- [FAIL] **One-Sample t-Test**: 
statistic=1.3562, 
p=0.1781, 
d=nan (Large)

- [FAIL] **Wilcoxon Signed-Rank Test**: 
statistic=2054.0000, 
p=0.1054, 
d=nan (Large)

- [OK] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0500, 
d=0.0000 (Negligible)

### GPU-003: [FAIL] FAILED

- **Description:** Neural Evolution 51x speedup

- **Mean:** 50.5770 ± 2.7147

- **95% CI:** [50.0383, 51.1156]

- **Confidence:** 90.6%


**Statistical Tests:**

- [FAIL] **One-Sample t-Test**: 
statistic=-1.5582, 
p=0.1224, 
d=nan (Large)

- [FAIL] **Wilcoxon Signed-Rank Test**: 
statistic=2061.0000, 
p=0.1106, 
d=nan (Large)

- [OK] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0500, 
d=0.0000 (Negligible)

### GPU-004: [OK] PASSED

- **Description:** Quantum Search 95x speedup

- **Mean:** 96.2692 ± 5.0126

- **95% CI:** [95.2746, 97.2638]

- **Confidence:** 99.1%


**Statistical Tests:**

- [OK] **One-Sample t-Test**: 
statistic=2.5320, 
p=0.0129, 
d=nan (Large)

- [OK] **Wilcoxon Signed-Rank Test**: 
statistic=1704.0000, 
p=0.0048, 
d=nan (Large)

- [FAIL] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0100, 
d=0.0000 (Negligible)


## Recommendations

- 2 claims failed validation - review methodology

- Low statistical power (0.50) - increase sample size
