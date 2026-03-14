# Statistical Methods for Phase 8 Validation

This document describes the statistical methods used for rigorous experimental validation of Phase 6-7 discoveries.

---

## Table of Contents

1. [Overview](#overview)
2. [Hypothesis Testing](#hypothesis-testing)
3. [Effect Size Analysis](#effect-size-analysis)
4. [Confidence Intervals](#confidence-intervals)
5. [Multiple Comparison Correction](#multiple-comparison-correction)
6. [Power Analysis](#power-analysis)
7. [Reproducibility Assessment](#reproducibility-assessment)
8. [Validation Criteria](#validation-criteria)

---

## Overview

Our validation framework follows these principles:

1. **Rigorous Statistical Testing**: All claims tested with appropriate statistical methods
2. **Effect Size Focus**: Not just statistical significance, but practical significance
3. **Reproducibility**: Results must be consistent across multiple trials
4. **Transparency**: All methods, assumptions, and results documented
5. **Publication Ready**: Methods suitable for peer-reviewed publication

---

## Hypothesis Testing

### One-Sample t-Test

**Purpose**: Test if sample mean differs from target value.

**Hypotheses**:
- H₀: μ = target_value
- H₁: μ ≠ target_value

**Test Statistic**:
```
t = (x̄ - μ₀) / (s / √n)
```

**Assumptions**:
- Data normally distributed (or n > 30)
- Independent samples
- Homogeneity of variance

**Example**: Testing if consensus rate = 96.3%

### Wilcoxon Signed-Rank Test

**Purpose**: Non-parametric alternative to t-test.

**Hypotheses**:
- H₀: Distribution symmetric around target_value
- H₁: Distribution not symmetric around target_value

**When to Use**:
- Small sample sizes (n < 30)
- Non-normal distributions
- Ordinal data

**Example**: Testing novelty scores with small samples

### Confidence Interval Test

**Purpose**: Check if target value falls within confidence interval.

**Criteria**:
- If target ∈ CI: Cannot reject null hypothesis
- If target ∉ CI: Reject null hypothesis

**Confidence Level**: 95% (α = 0.05)

---

## Effect Size Analysis

### Cohen's d

**Purpose**: Measure practical significance, not just statistical significance.

**Formula**:
```
d = (μ₁ - μ₂) / σ_pooled
```

**Interpretation**:
- |d| < 0.2: Negligible effect
- 0.2 ≤ |d| < 0.5: Small effect
- 0.5 ≤ |d| < 0.8: Medium effect
- |d| ≥ 0.8: Large effect

**Why Effect Size Matters**:
- Large samples can detect trivial effects
- Effect size indicates practical importance
- Enables cross-study comparison

**Example**: d = 1.5 means large effect (1.5 standard deviations)

### Pearson's r

**Purpose**: Measure correlation strength.

**Interpretation**:
- |r| < 0.3: Weak correlation
- 0.3 ≤ |r| < 0.7: Moderate correlation
- |r| ≥ 0.7: Strong correlation

**Example**: r = 0.78 for topology-emergence correlation

---

## Confidence Intervals

### Computation Method

**Formula**:
```
CI = x̄ ± t_(α/2, n-1) × (s / √n)
```

**Components**:
- x̄: Sample mean
- t_(α/2, n-1): Critical t-value
- s: Sample standard deviation
- n: Sample size

### Interpretation

**95% Confidence Interval**:
- "We are 95% confident the true parameter lies in this interval"
- NOT: "95% of data falls in this interval"
- NOT: "The parameter has 95% probability of being in this interval"

**Example**:
- Mean: 96.3%
- 95% CI: [94.8%, 97.8%]
- Interpretation: True consensus rate likely between 94.8% and 97.8%

### Width Considerations

**Narrow CI**: More precise estimate
- Larger sample size
- Lower variance

**Wide CI**: Less precise estimate
- Smaller sample size
- Higher variance
- May indicate need for more data

---

## Multiple Comparison Correction

### Problem

When running multiple tests, probability of false positive increases:
- 1 test: α = 0.05
- 10 tests: α ≈ 0.40 (family-wise error rate)

### Bonferroni Correction

**Method**: Divide α by number of tests

**Formula**:
```
α_corrected = α / n
```

**Example**:
- 10 tests
- α = 0.05
- α_corrected = 0.005

**Pros**:
- Simple to implement
- Controls family-wise error rate

**Cons**:
- Conservative (may miss real effects)
- Reduces power

### False Discovery Rate (FDR)

**Method**: Benjamini-Hochberg procedure

**Goal**: Control proportion of false positives

**Procedure**:
1. Sort p-values: p₁ ≤ p₂ ≤ ... ≤ pₙ
2. Find largest k where pₖ ≤ (k/n) × α
3. Reject hypotheses 1 to k

**Pros**:
- Less conservative than Bonferroni
- Better power
- Standard in genomics, neuroscience

**Example**: 5 discoveries with FDR < 0.05

### Our Approach

**Primary**: Bonferroni (conservative, rigorous)
**Secondary**: FDR (exploratory analysis)

---

## Power Analysis

### What is Statistical Power?

**Definition**: Probability of detecting an effect if it exists

**Formula**:
```
Power = 1 - β
```

Where β = Type II error rate (false negative)

### Factors Affecting Power

1. **Effect Size**: Larger effects → higher power
2. **Sample Size**: More data → higher power
3. **Alpha Level**: Higher α → higher power (more false positives)
4. **Variability**: Lower variance → higher power

### Target Power

**Standard**: Power ≥ 0.80 (80%)
**Rationale**: Acceptable balance between Type I and II errors

### Power Calculation

**Two-Sample t-Test**:
```
n = 2 × [(z_α + z_β) × σ / Δ]²
```

Where:
- z_α: Critical value for alpha
- z_β: Critical value for beta
- σ: Standard deviation
- Δ: Effect size to detect

**Example**:
- Effect size: d = 0.8
- Power: 0.80
- Alpha: 0.05
- Required sample: n ≈ 26 per group

### Our Approach

**Minimum Power**: 0.80 for all tests
**Sample Size**: 100 trials per claim (exceeds minimum)
**Result**: High confidence in validated claims

---

## Reproducibility Assessment

### Definition

**Reproducibility**: Consistency of results across multiple trials

### Metrics

#### Coefficient of Variation (CV)

**Formula**:
```
CV = (σ / μ) × 100%
```

**Interpretation**:
- CV < 10%: Highly reproducible
- 10% ≤ CV < 20%: Moderately reproducible
- CV ≥ 20%: Low reproducibility

#### Intra-Class Correlation (ICC)

**Purpose**: Measure consistency across trials

**Formula**:
```
ICC = (σ²_between) / (σ²_between + σ²_within)
```

**Interpretation**:
- ICC > 0.9: Excellent consistency
- 0.75 < ICC ≤ 0.9: Good consistency
- 0.5 < ICC ≤ 0.75: Moderate consistency
- ICC ≤ 0.5: Poor consistency

### Our Reproducibility Score

**Formula**:
```
Reproducibility = 1 - min(CV, 1.0)
```

**Target**: ≥ 0.80 (80% reproducibility)

---

## Validation Criteria

### Primary Criteria

Each claim must meet:

1. **Statistical Significance**: p < 0.05 (corrected)
2. **Effect Size**: Cohen's d > 0.8 (large effect) where applicable
3. **Confidence Interval**: Target within 95% CI (for equality tests)
4. **Power**: ≥ 0.80
5. **Reproducibility**: ≥ 0.80

### Secondary Criteria

For enhanced confidence:

1. **Multiple Tests**: At least 2 statistical tests agree
2. **Robustness**: Validated across parameter ranges
3. **Consistency**: Results consistent with theory

### Decision Rules

#### Equality Claims (approximately_equal)
- Target value within tolerance
- High reproducibility (≥ 0.80)

#### Inequality Claims (greater_than / less_than)
- Mean in correct direction
- Statistical significance (p < 0.05)
- Large effect size (d > 0.8)

### Reporting

For each claim, report:
- Mean ± Standard deviation
- 95% Confidence interval
- p-value (corrected)
- Effect size with interpretation
- Reproducibility score
- Power
- Validated: YES/NO

---

## Common Statistical Pitfalls

### 1. P-hacking

**Problem**: Multiple testing until significant

**Solution**: Pre-register analysis plan, correct for multiple comparisons

### 2. Stopping Rules

**Problem**: Stopping when significant

**Solution**: Pre-determine sample size, use sequential analysis

### 3. HARKing

**Problem**: Hypothesizing After Results are Known

**Solution**: State hypotheses before data collection

### 4. Neglecting Effect Size

**Problem**: Only reporting p-values

**Solution**: Always report effect sizes with interpretation

### 5. Overlooking Assumptions

**Problem**: Violating test assumptions

**Solution**: Check normality, homogeneity, independence

---

## References

1. Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Lawrence Erlbaum Associates.

2. Student. (1908). "The probable error of a mean". *Biometrika*, 6(1), 1-25.

3. Bonferroni, C. E. (1936). "Teoria statistica delle classi e calcolo delle probabilità". *Pubblicazioni del R Istituto Superiore di Scienze Economiche e Commerciali di Firenze*, 8, 3-62.

4. Benjamini, Y., & Hochberg, Y. (1995). "Controlling the false discovery rate: A practical and powerful approach to multiple testing". *Journal of the Royal Statistical Society, Series B*, 57(1), 289-300.

5. Wasserstein, R. L., & Lazar, N. A. (2016). "The ASA's statement on p-values: Context, process, and purpose". *The American Statistician*, 70(2), 129-133.

---

**Document Version**: 1.0
**Last Updated**: 2026-03-13
**Author**: Phase 8 Validation Team
