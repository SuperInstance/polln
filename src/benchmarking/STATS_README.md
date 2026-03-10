# Statistical Testing Module for Benchmark Validation

Production-quality statistical testing framework for validating performance claims with rigorous methodology.

## Features

### Hypothesis Testing
- **One-sample t-test**: Test if sample mean differs from null value
- **Two-sample t-test**: Compare means of two groups (equal variance or Welch's)
- **Paired t-test**: Compare paired observations (before/after)
- **Mann-Whitney U test**: Non-parametric alternative to t-test
- **Wilcoxon signed-rank test**: Non-parametric paired test

### Effect Size Calculation
- **Cohen's d**: Standardized mean difference
- **Hedges' g**: Bias-corrected Cohen's d for small samples
- **Cliff's delta**: Non-parametric effect size
- **Glass's delta**: Using control group SD
- **Pearson's r**: Correlation coefficient

### Confidence Intervals
- **Mean**: T-distribution based
- **Proportion**: Wilson score interval
- **Mean difference**: Independent or paired
- **Bootstrap**: Any statistic with resampling

### Power Analysis
- Sample size calculation for t-tests
- Sample size calculation for paired tests
- Sample size calculation for proportion tests
- Achieved power calculation

### Multiple Comparison Correction
- **Bonferroni**: Conservative control
- **Holm-Bonferroni**: Less conservative step-down
- **Benjamini-Hochberg**: FDR control
- **Benjamini-Yekutieli**: FDR under dependence
- **Q-values**: Adjusted p-values

## Installation

```typescript
import {
  StatisticalTest,
  EffectSizeCalculator,
  SampleSizeCalculator,
  MultipleTestCorrector,
  ConfidenceInterval,
  NormalityTest
} from './stats';
```

## Quick Start

### Basic Hypothesis Test

```typescript
// Validate 15x speedup claim
const baseline = [100, 105, 98, 102, 99, 101, 97, 103, 100, 99];
const optimized = [6, 7, 5, 8, 6, 7, 5, 8, 6, 7];

const test = new StatisticalTest({ alpha: 0.01, twoTailed: true });
const result = test.twoSampleTTest(baseline, optimized);

console.log(`Statistic: ${result.statistic.toFixed(4)}`);
console.log(`P-value: ${result.pValue.toExponential(4)}`);
console.log(`Rejected: ${result.rejected}`);
console.log(`Effect size (Cohen's d): ${result.effectSize?.toFixed(4)}`);
console.log(`95% CI: [${result.confidenceInterval?.[0].toFixed(4)}, ${result.confidenceInterval?.[1].toFixed(4)}]`);
```

### Effect Size Calculation

```typescript
// Calculate Cohen's d with confidence interval
const effectSize = EffectSizeCalculator.cohensD(baseline, optimized);

console.log(`Cohen's d: ${effectSize.value.toFixed(4)}`);
console.log(`Interpretation: ${effectSize.interpretation}`);
console.log(`95% CI: [${effectSize.confidenceInterval[0].toFixed(4)}, ${effectSize.confidenceInterval[1].toFixed(4)}]`);

// Interpretation: 'negligible' | 'small' | 'medium' | 'large'
```

### Sample Size Calculation

```typescript
// How many samples needed for 80% power to detect 20% improvement?
const powerAnalysis = SampleSizeCalculator.forTTest({
  effectSize: 0.8,  // Large effect (Cohen's d)
  power: 0.80,      // 80% power
  alpha: 0.05,      // 5% significance
  twoTailed: true
});

console.log(`Required sample size: ${powerAnalysis.sampleSize}`);
console.log(`Achieved power: ${(powerAnalysis.power * 100).toFixed(2)}%`);
```

### Multiple Comparison Correction

```typescript
// Correct for multiple tests
const pValues = [0.001, 0.02, 0.04, 0.08, 0.12];

// Bonferroni (conservative)
const bonferroniRejected = MultipleTestCorrector.bonferroni(pValues);

// Benjamini-Hochberg (FDR control)
const bhRejected = MultipleTestCorrector.benjaminiHochberg(pValues);

// Calculate q-values
const qValues = MultipleTestCorrector.calculateQValues(pValues);
```

## API Reference

### StatisticalTest

#### Constructor

```typescript
new StatisticalTest(config?: TestConfig)
```

**Config options:**
- `alpha`: Significance level (default: 0.05)
- `twoTailed`: Use two-tailed test (default: true)
- `confidenceLevel`: For CI (default: 0.95)
- `bootstrapIterations`: Bootstrap iterations (default: 10000)

#### Methods

##### oneSampleTTest

```typescript
oneSampleTTest(sample: number[], nullValue?: number): HypothesisTestResult
```

Tests if sample mean differs from specified value.

**Example:**
```typescript
const test = new StatisticalTest();
const result = test.oneSampleTTest([1.2, 1.5, 1.8, 2.1], 0);
// result.rejected: true - mean differs from 0
```

##### twoSampleTTest

```typescript
twoSampleTTest(sample1: number[], sample2: number[], equalVariance?: boolean): HypothesisTestResult
```

Tests if two samples have different means.

**Example:**
```typescript
const result = test.twoSampleTTest(baseline, optimized, false);
// Use Welch's test for unequal variances
```

##### pairedTTest

```typescript
pairedTTest(sample1: number[], sample2: number[]): HypothesisTestResult
```

Tests if paired differences are non-zero.

**Example:**
```typescript
const result = test.pairedTTest(before, after);
```

##### mannWhitneyUTest

```typescript
mannWhitneyUTest(sample1: number[], sample2: number[]): HypothesisTestResult
```

Non-parametric test for distribution differences.

**Example:**
```typescript
const result = test.mannWhitneyUTest(sample1, sample2);
// Robust to outliers, non-normal data
```

##### wilcoxonSignedRankTest

```typescript
wilcoxonSignedRankTest(sample1: number[], sample2: number[]): HypothesisTestResult
```

Non-parametric paired test.

### HypothesisTestResult

```typescript
interface HypothesisTestResult {
  statistic: number;           // Test statistic
  pValue: number;              // P-value
  rejected: boolean;           // H0 rejected?
  alpha: number;               // Significance level used
  testName: string;            // Test name
  effectSize?: number;         // Effect size
  confidenceInterval?: [number, number];  // CI for effect size
  details?: Record<string, unknown>;      // Test-specific details
}
```

### EffectSizeCalculator

All methods return `EffectSizeResult`:

```typescript
interface EffectSizeResult {
  value: number;               // Effect size
  type: string;                // Type ('cohens_d', 'cliff_delta', etc.)
  interpretation: string;      // 'negligible' | 'small' | 'medium' | 'large'
  confidenceInterval: [number, number];
  confidenceLevel: number;
}
```

#### Methods

- `cohensD(sample1, sample2)`: Cohen's d
- `hedgesG(sample1, sample2)`: Bias-corrected d
- `cliffsDelta(sample1, sample2)`: Non-parametric
- `glasssDelta(treatment, control)`: Using control SD
- `pearsonR(x, y)`: Correlation

### SampleSizeCalculator

#### Methods

##### forTTest

```typescript
forTTest(config: {
  effectSize: number;
  power?: number;
  alpha?: number;
  twoTailed?: boolean;
  ratio?: number;
}): PowerAnalysisResult
```

##### forPairedTTest

```typescript
forPairedTTest(config: {
  effectSize: number;
  power?: number;
  alpha?: number;
  twoTailed?: boolean;
}): PowerAnalysisResult
```

##### forProportionTest

```typescript
forProportionTest(config: {
  p1: number;
  p2: number;
  power?: number;
  alpha?: number;
  twoTailed?: boolean;
  ratio?: number;
}): PowerAnalysisResult
```

##### achievedPower

```typescript
achievedPower(config: {
  sampleSize: number | [number, number];
  effectSize: number;
  alpha?: number;
  twoTailed?: boolean;
}): PowerAnalysisResult
```

### MultipleTestCorrector

#### Methods

- `bonferroni(pValues, alpha)`: Conservative correction
- `holm(pValues, alpha)`: Step-down Bonferroni
- `benjaminiHochberg(pValues, qLevel)`: FDR control
- `benjaminiYekutieli(pValues, qLevel)`: FDR under dependence
- `calculateQValues(pValues)`: Adjusted p-values

### ConfidenceInterval

#### Methods

- `forMean(data, confidenceLevel)`: CI for mean
- `forProportion(successes, trials, confidenceLevel)`: Wilson score
- `forMeanDifference(sample1, sample2, confidenceLevel, paired)`: Mean difference
- `bootstrap(data, statistic, confidenceLevel, iterations)`: Bootstrap CI

### NormalityTest

#### Methods

- `shapiroWilk(data)`: Test normality assumption

## Benchmark Validation Workflow

### 1. Determine Required Sample Size

```typescript
const powerAnalysis = SampleSizeCalculator.forTTest({
  effectSize: 0.8,  // Expected effect size
  power: 0.90,      // 90% power
  alpha: 0.01       // 1% significance
});

console.log(`Run ${powerAnalysis.sampleSize} trials per condition`);
```

### 2. Collect Data

```typescript
const baselineTimes: number[] = [];
const optimizedTimes: number[] = [];

// Run trials...
for (let i = 0; i < powerAnalysis.sampleSize / 2; i++) {
  baselineTimes.push(measureBaseline());
  optimizedTimes.push(measureOptimized());
}
```

### 3. Test Assumptions

```typescript
// Check normality
const baselineNormality = NormalityTest.shapiroWilk(baselineTimes);
const optimizedNormality = NormalityTest.shapiroWilk(optimizedTimes);

if (!baselineNormality.rejected && !optimizedNormality.rejected) {
  console.log('Data appears normal - use parametric tests');
} else {
  console.log('Data non-normal - use Mann-Whitney U test');
}
```

### 4. Perform Hypothesis Test

```typescript
const test = new StatisticalTest({ alpha: 0.01 });

if (!baselineNormality.rejected) {
  const result = test.twoSampleTTest(baselineTimes, optimizedTimes);
  console.log(`T-test: p=${result.pValue.toExponential(4)}, d=${result.effectSize?.toFixed(4)}`);
} else {
  const result = test.mannWhitneyUTest(baselineTimes, optimizedTimes);
  console.log(`Mann-Whitney: p=${result.pValue.toExponential(4)}, δ=${result.effectSize?.toFixed(4)}`);
}
```

### 5. Report Results

```typescript
const effectSize = EffectSizeCalculator.cohensD(baselineTimes, optimizedTimes);
const ci = ConfidenceInterval.forMeanDifference(baselineTimes, optimizedTimes);

console.log(`
Performance Validation Results
================================
Baseline mean: ${StatsUtils.mean(baselineTimes).toFixed(2)} ms
Optimized mean: ${StatsUtils.mean(optimizedTimes).toFixed(2)} ms
Speedup: ${(StatsUtils.mean(baselineTimes) / StatsUtils.mean(optimizedTimes)).toFixed(2)}x

Statistical Test: ${result.testName}
Test statistic: ${result.statistic.toFixed(4)}
P-value: ${result.pValue.toExponential(4)}
Result: ${result.rejected ? 'REJECTED' : 'FAILED TO REJECT'} null hypothesis

Effect Size (Cohen's d): ${effectSize.value.toFixed(4)}
Interpretation: ${effectSize.interpretation}
95% CI: [${effectSize.confidenceInterval[0].toFixed(4)}, ${effectSize.confidenceInterval[1].toFixed(4)}]

Mean Difference 95% CI: [${ci[0].toFixed(4)}, ${ci[1].toFixed(4)}]
`);
```

## Statistical Guidelines

### Choosing the Right Test

| Data Type | Test | Assumptions |
|-----------|------|-------------|
| Normal, equal variance | Two-sample t-test | Normality, homoscedasticity |
| Normal, unequal variance | Welch's t-test | Normality only |
| Non-normal, independent | Mann-Whitney U | None |
| Normal, paired | Paired t-test | Normality of differences |
| Non-normal, paired | Wilcoxon signed-rank | Symmetry of differences |

### Effect Size Interpretation

**Cohen's d:**
- < 0.2: Negligible
- 0.2 - 0.5: Small
- 0.5 - 0.8: Medium
- \> 0.8: Large

**Cliff's delta:**
- < 0.147: Negligible
- 0.147 - 0.33: Small
- 0.33 - 0.474: Medium
- \> 0.474: Large

### Multiple Comparison Strategy

1. **Few tests (< 5)**: Use Bonferroni or Holm
2. **Many tests (5-20)**: Use Benjamini-Hochberg
3. **Exploratory analysis**: Use FDR methods
4. **Confirmatory analysis**: Use family-wise error rate methods

## Performance Considerations

- Bootstrap iterations default to 10,000 for accuracy
- Reduce to 1,000-5,000 for faster computation
- Use analytic methods when assumptions are met
- Cache results for repeated analyses

## Error Handling

```typescript
try {
  const result = test.twoSampleTTest(sample1, sample2);
} catch (error) {
  if (error.message.includes('at least 2')) {
    console.error('Need more data points');
  } else if (error.message.includes('same length')) {
    console.error('Samples must match for paired test');
  }
}
```

## References

- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences*
- Welch, B. L. (1947). The generalization of "Student's" problem
- Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate
- Cliff, N. (1993). *Dominance statistics: Ordinal analyses to answer ordinal questions*

## License

MIT
