# Validation Report: PHASE6_EMERGENCE_PREDICTION

## Emergence prediction system with early warning signals

**Validation Date:** 2026-03-13 17:55:19

**Overall Validated:** [FAIL] NO

**Statistical Power:** 0.333

**Reproducibility Score:** 0.915

**Generation Time:** 0.00s


## Claims Validation

### EMERG-001: [OK] PASSED

- **Description:** Prediction accuracy 83.7%

- **Mean:** 0.8574 ± 0.0326

- **95% CI:** [0.8510, 0.8639]

- **Confidence:** 99.7%


**Statistical Tests:**

- [OK] **One-Sample t-Test**: 
statistic=6.2680, 
p=0.0000, 
d=nan (Large)

- [OK] **Wilcoxon Signed-Rank Test**: 
statistic=859.0000, 
p=0.0000, 
d=nan (Large)

- [FAIL] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0100, 
d=0.0000 (Negligible)

### EMERG-002: [FAIL] FAILED

- **Description:** Average lead time 7.2 steps

- **Mean:** 7.1769 ± 0.7765

- **95% CI:** [7.0228, 7.3310]

- **Confidence:** 44.1%


**Statistical Tests:**

- [FAIL] **One-Sample t-Test**: 
statistic=-0.2972, 
p=0.7670, 
d=nan (Large)

- [FAIL] **Wilcoxon Signed-Rank Test**: 
statistic=2474.0000, 
p=0.8608, 
d=nan (Large)

- [OK] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0500, 
d=0.0000 (Negligible)

### EMERG-003: [FAIL] FAILED

- **Description:** False alarm rate 17.3%

- **Mean:** 0.1751 ± 0.0188

- **95% CI:** [0.1714, 0.1788]

- **Confidence:** 75.2%


**Statistical Tests:**

- [FAIL] **One-Sample t-Test**: 
statistic=1.1098, 
p=0.2698, 
d=nan (Large)

- [FAIL] **Wilcoxon Signed-Rank Test**: 
statistic=2292.0000, 
p=0.4231, 
d=nan (Large)

- [OK] **Confidence Interval Test**: 
statistic=0.0000, 
p=0.0500, 
d=0.0000 (Negligible)


## Recommendations

- 2 claims failed validation - review methodology

- Low statistical power (0.33) - increase sample size
