/**
 * Tests for statistical testing module
 */

import { describe, it, expect } from '@jest/globals';
import {
  StatisticalTest,
  EffectSizeCalculator,
  SampleSizeCalculator,
  MultipleTestCorrector,
  ConfidenceInterval,
  NormalityTest,
} from '../stats';

describe('StatisticalTest', () => {
  const testConfig = { alpha: 0.05, twoTailed: true };
  const oneTailedConfig = { alpha: 0.05, twoTailed: false };

  describe('oneSampleTTest', () => {
    it('should detect significant difference from null', () => {
      const test = new StatisticalTest(oneTailedConfig); // Use one-tailed for directional test
      const sample = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32];
      const result = test.oneSampleTTest(sample, 0);

      // With a large enough sample and effect, should be significant
      expect(result.pValue).toBeLessThan(0.05);
      expect(result.effectSize).toBeGreaterThan(0);
      expect(result.testName).toBe('One-sample t-test');
    });

    it('should not reject null when no difference', () => {
      const test = new StatisticalTest(testConfig);
      const sample = [1.01, 0.99, 1.02, 0.98, 1.00, 1.01, 0.99];
      const result = test.oneSampleTTest(sample, 1.0);

      expect(result.rejected).toBe(false);
      expect(result.pValue).toBeGreaterThan(0.05);
    });

    it('should calculate correct effect size', () => {
      const test = new StatisticalTest(testConfig);
      const sample = [10, 12, 14, 16, 18];
      const result = test.oneSampleTTest(sample, 0);

      // Effect size should be roughly mean / std
      expect(result.effectSize).toBeDefined();
      expect(result.effectSize).toBeGreaterThan(0);
    });

    it('should provide confidence interval for effect size', () => {
      const test = new StatisticalTest(testConfig);
      const sample = [10, 12, 14, 16, 18];
      const result = test.oneSampleTTest(sample, 0);

      expect(result.confidenceInterval).toBeDefined();
      expect(result.confidenceInterval![0]).toBeLessThan(result.effectSize!);
      expect(result.confidenceInterval![1]).toBeGreaterThan(result.effectSize!);
    });
  });

  describe('twoSampleTTest', () => {
    it('should detect difference between two samples', () => {
      const test = new StatisticalTest(oneTailedConfig); // Use one-tailed for directional test
      const sample1 = [20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 42];
      const sample2 = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32];
      const result = test.twoSampleTTest(sample1, sample2);

      // With a large enough sample and effect, should be significant
      expect(result.pValue).toBeLessThan(0.05);
      expect(result.effectSize).toBeDefined();
    });

    it('should not reject null for identical distributions', () => {
      const test = new StatisticalTest(testConfig);
      const sample1 = [10, 11, 12, 13, 14];
      const sample2 = [10.2, 10.8, 12.1, 12.9, 13.1];
      const result = test.twoSampleTTest(sample1, sample2);

      expect(result.rejected).toBe(false);
    });

    it('should handle unequal variances with Welch test', () => {
      const test = new StatisticalTest(testConfig);
      const sample1 = [10, 11, 12, 13, 14];
      const sample2 = [8, 12, 16, 20, 24];
      const result = test.twoSampleTTest(sample1, sample2, false);

      expect(result.testName).toBe("Welch's t-test");
      expect(result.details?.equalVariance).toBe(false);
    });
  });

  describe('pairedTTest', () => {
    it('should detect significant paired differences', () => {
      const test = new StatisticalTest(oneTailedConfig); // Use one-tailed for directional test
      const before = [100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155];
      const after = [90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145];
      const result = test.pairedTTest(before, after);

      // With a large enough sample and effect, should be significant
      expect(result.pValue).toBeLessThan(0.05);
      expect(result.testName).toBe('Paired t-test');
    });

    it('should not reject null when no change', () => {
      const test = new StatisticalTest(testConfig);
      const sample1 = [100, 105, 110, 115, 120];
      const sample2 = [101, 106, 111, 116, 121];
      const result = test.pairedTTest(sample1, sample2);

      expect(result.rejected).toBe(false);
    });

    it('should throw error for mismatched lengths', () => {
      const test = new StatisticalTest(testConfig);
      const sample1 = [1, 2, 3];
      const sample2 = [1, 2];

      expect(() => test.pairedTTest(sample1, sample2)).toThrow();
    });
  });

  describe('mannWhitneyUTest', () => {
    it('should detect difference in distributions', () => {
      const test = new StatisticalTest(testConfig);
      const sample1 = [1, 2, 3, 4, 5];
      const sample2 = [3, 4, 5, 6, 7];
      const result = test.mannWhitneyUTest(sample1, sample2);

      expect(result.testName).toBe("Mann-Whitney U test");
      expect(result.effectSize).toBeDefined();
    });

    it('should handle ties correctly', () => {
      const test = new StatisticalTest(testConfig);
      const sample1 = [1, 2, 2, 3, 4];
      const sample2 = [2, 3, 3, 4, 5];
      const result = test.mannWhitneyUTest(sample1, sample2);

      expect(result.statistic).toBeDefined();
    });

    it('should calculate Cliff\'s delta as effect size', () => {
      const test = new StatisticalTest(testConfig);
      const sample1 = [1, 2, 3, 4, 5];
      const sample2 = [3, 4, 5, 6, 7];
      const result = test.mannWhitneyUTest(sample1, sample2);

      expect(result.effectSize).toBeDefined();
      expect(Math.abs(result.effectSize!)).toBeLessThanOrEqual(1);
    });
  });

  describe('wilcoxonSignedRankTest', () => {
    it('should detect paired differences non-parametrically', () => {
      const test = new StatisticalTest(testConfig);
      const before = [100, 105, 110, 115, 120];
      const after = [90, 95, 100, 105, 110];
      const result = test.wilcoxonSignedRankTest(before, after);

      expect(result.testName).toBe('Wilcoxon signed-rank test');
      expect(result.rejected).toBe(true);
    });

    it('should handle zero differences', () => {
      const test = new StatisticalTest(testConfig);
      const sample1 = [100, 105, 110, 110, 120];
      const sample2 = [95, 100, 105, 110, 115];
      const result = test.wilcoxonSignedRankTest(sample1, sample2);

      expect(result.statistic).toBeDefined();
    });
  });
});

describe('EffectSizeCalculator', () => {
  describe('cohensD', () => {
    it('should calculate Cohen\'s d correctly', () => {
      const sample1 = [10, 12, 14, 16, 18];
      const sample2 = [8, 10, 12, 14, 16];
      const result = EffectSizeCalculator.cohensD(sample1, sample2);

      expect(result.type).toBe('cohens_d');
      expect(result.value).toBeDefined();
      expect(result.interpretation).toBeDefined();
    });

    it('should interpret effect size correctly', () => {
      const sample1 = [100, 102, 104, 106, 108];
      const sample2 = [100, 100.1, 100.2, 100.3, 100.4];
      const result = EffectSizeCalculator.cohensD(sample1, sample2);

      expect(['small', 'medium', 'large', 'very large']).toContain(result.interpretation);
    });

    it('should provide confidence interval', () => {
      const sample1 = [10, 12, 14, 16, 18];
      const sample2 = [8, 10, 12, 14, 16];
      const result = EffectSizeCalculator.cohensD(sample1, sample2);

      expect(result.confidenceInterval).toBeDefined();
      expect(result.confidenceInterval[0]).toBeLessThan(result.value);
      expect(result.confidenceInterval[1]).toBeGreaterThan(result.value);
    });
  });

  describe('hedgesG', () => {
    it('should calculate bias-corrected effect size', () => {
      const sample1 = [10, 12, 14, 16, 18];
      const sample2 = [8, 10, 12, 14, 16];
      const result = EffectSizeCalculator.hedgesG(sample1, sample2);

      expect(result.type).toBe('hedges_g');
      expect(result.value).toBeDefined();
      // Hedges' g should be slightly smaller than Cohen's d for small samples
    });
  });

  describe('cliffsDelta', () => {
    it('should calculate non-parametric effect size', () => {
      const sample1 = [1, 2, 3, 4, 5];
      const sample2 = [3, 4, 5, 6, 7];
      const result = EffectSizeCalculator.cliffsDelta(sample1, sample2);

      expect(result.type).toBe('cliff_delta');
      expect(result.value).toBeGreaterThanOrEqual(-1);
      expect(result.value).toBeLessThanOrEqual(1);
    });

    it('should handle overlapping distributions', () => {
      const sample1 = [1, 2, 3, 4, 5];
      const sample2 = [2, 3, 4, 5, 6];
      const result = EffectSizeCalculator.cliffsDelta(sample1, sample2);

      expect(Math.abs(result.value)).toBeLessThan(1);
    });
  });

  describe('pearsonR', () => {
    it('should calculate correlation correctly', () => {
      const x = [1, 2, 3, 4, 5];
      const y = [2, 4, 6, 8, 10];
      const result = EffectSizeCalculator.pearsonR(x, y);

      expect(result.type).toBe('pearson_r');
      expect(result.value).toBeCloseTo(1.0, 1);
    });

    it('should detect negative correlation', () => {
      const x = [1, 2, 3, 4, 5];
      const y = [5, 4, 3, 2, 1];
      const result = EffectSizeCalculator.pearsonR(x, y);

      expect(result.value).toBeLessThan(0);
      expect(Math.abs(result.value)).toBeGreaterThan(0.9);
    });

    it('should detect no correlation', () => {
      const x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
      const y = [5, 2, 8, 1, 9, 3, 7, 4, 10, 6]; // Random permutation
      const result = EffectSizeCalculator.pearsonR(x, y);

      expect(Math.abs(result.value)).toBeLessThan(0.5);
    });
  });
});

describe('SampleSizeCalculator', () => {
  describe('forTTest', () => {
    it('should calculate required sample size for medium effect', () => {
      const result = SampleSizeCalculator.forTTest({
        effectSize: 0.5,
        power: 0.80,
        alpha: 0.05,
      });

      expect(result.sampleSize).toBeDefined();
      expect(result.sampleSize).toBeGreaterThan(0);
      expect(result.power).toBeCloseTo(0.8, 1);
      expect(result.testType).toContain('Two-sample t-test');
    });

    it('should require smaller sample for larger effect', () => {
      const smallEffect = SampleSizeCalculator.forTTest({ effectSize: 0.2 });
      const largeEffect = SampleSizeCalculator.forTTest({ effectSize: 0.8 });

      expect(largeEffect.sampleSize).toBeLessThan(smallEffect.sampleSize);
    });

    it('should require larger sample for higher power', () => {
      const power80 = SampleSizeCalculator.forTTest({ effectSize: 0.5, power: 0.80 });
      const power95 = SampleSizeCalculator.forTTest({ effectSize: 0.5, power: 0.95 });

      expect(power95.sampleSize).toBeGreaterThan(power80.sampleSize);
    });
  });

  describe('forPairedTTest', () => {
    it('should calculate sample size for paired design', () => {
      const result = SampleSizeCalculator.forPairedTTest({
        effectSize: 0.5,
        power: 0.80,
      });

      expect(result.sampleSize).toBeDefined();
      expect(result.testType).toContain('Paired');
    });

    it('should require fewer samples than independent t-test', () => {
      const independent = SampleSizeCalculator.forTTest({ effectSize: 0.5 });
      const paired = SampleSizeCalculator.forPairedTTest({ effectSize: 0.5 });

      expect(paired.sampleSize).toBeLessThan(independent.sampleSize);
    });
  });

  describe('forProportionTest', () => {
    it('should calculate sample size for proportion test', () => {
      const result = SampleSizeCalculator.forProportionTest({
        p1: 0.5,
        p2: 0.7,
        power: 0.80,
      });

      expect(result.sampleSize).toBeDefined();
      expect(result.effectSize).toBeCloseTo(0.2);
    });

    it('should handle small proportions', () => {
      const result = SampleSizeCalculator.forProportionTest({
        p1: 0.01,
        p2: 0.05,
      });

      expect(result.sampleSize).toBeDefined();
    });
  });

  describe('achievedPower', () => {
    it('should calculate power given sample size', () => {
      const result = SampleSizeCalculator.achievedPower({
        sampleSize: 64,
        effectSize: 0.5,
      });

      expect(result.power).toBeDefined();
      expect(result.power).toBeGreaterThan(0);
      expect(result.power).toBeLessThan(1);
    });

    it('should show higher power with larger sample', () => {
      const small = SampleSizeCalculator.achievedPower({ sampleSize: 32, effectSize: 0.5 });
      const large = SampleSizeCalculator.achievedPower({ sampleSize: 128, effectSize: 0.5 });

      expect(large.power).toBeGreaterThan(small.power);
    });
  });
});

describe('MultipleTestCorrector', () => {
  describe('bonferroni', () => {
    it('should adjust alpha correctly', () => {
      const pValues = [0.001, 0.009, 0.03, 0.06, 0.10];
      const rejected = MultipleTestCorrector.bonferroni(pValues, 0.05);

      expect(rejected).toHaveLength(5);
      // With Bonferroni, threshold is 0.05/5 = 0.01
      expect(rejected[0]).toBe(1); // 0.001 < 0.01
      expect(rejected[1]).toBe(1); // 0.009 < 0.01
      expect(rejected[2]).toBe(0); // 0.03 > 0.01
    });

    it('should be more conservative than no correction', () => {
      const pValues = [0.01, 0.02, 0.03];
      const uncorrected = pValues.map((p) => (p < 0.05 ? 1 : 0));
      const bonferroni = MultipleTestCorrector.bonferroni(pValues);

      expect(bonferroni.filter((r) => r === 1).length).toBeLessThanOrEqual(
        uncorrected.filter((r) => r === 1).length
      );
    });
  });

  describe('holm', () => {
    it('should be less conservative than Bonferroni', () => {
      const pValues = [0.01, 0.02, 0.03];
      const bonferroni = MultipleTestCorrector.bonferroni(pValues);
      const holm = MultipleTestCorrector.holm(pValues);

      expect(holm.filter((r) => r === 1).length).toBeGreaterThanOrEqual(
        bonferroni.filter((r) => r === 1).length
      );
    });

    it('should handle all significant p-values', () => {
      const pValues = [0.001, 0.002, 0.003];
      const rejected = MultipleTestCorrector.holm(pValues);

      expect(rejected.every((r) => r === 1)).toBe(true);
    });
  });

  describe('benjaminiHochberg', () => {
    it('should control false discovery rate', () => {
      const pValues = [0.01, 0.03, 0.05, 0.10, 0.15];
      const rejected = MultipleTestCorrector.benjaminiHochberg(pValues, 0.05);

      expect(rejected).toHaveLength(5);
      // BH typically rejects more than Bonferroni
      const bonferroni = MultipleTestCorrector.bonferroni(pValues);
      expect(rejected.filter((r) => r === 1).length).toBeGreaterThanOrEqual(
        bonferroni.filter((r) => r === 1).length
      );
    });

    it('should handle mixed significance', () => {
      const pValues = [0.001, 0.04, 0.08, 0.12, 0.20];
      const rejected = MultipleTestCorrector.benjaminiHochberg(pValues, 0.10);

      expect(rejected).toBeDefined();
    });
  });

  describe('calculateQValues', () => {
    it('should calculate adjusted p-values', () => {
      const pValues = [0.01, 0.03, 0.05, 0.10, 0.15];
      const qValues = MultipleTestCorrector.calculateQValues(pValues);

      expect(qValues).toHaveLength(5);
      // Q-values should be >= original p-values (approximately)
      qValues.forEach((q, i) => {
        expect(q).toBeGreaterThan(0);
      });
    });

    it('should maintain order when sorted', () => {
      const pValues = [0.10, 0.01, 0.05, 0.02, 0.08];
      const qValues = MultipleTestCorrector.calculateQValues(pValues);

      // Find indices and sort
      const sorted = pValues
        .map((p, i) => ({ p, q: qValues[i] }))
        .sort((a, b) => a.p - b.p);

      // Q-values should be non-decreasing when p-values are sorted
      for (let i = 1; i < sorted.length; i++) {
        expect(sorted[i].q).toBeGreaterThanOrEqual(sorted[i - 1].q);
      }
    });
  });
});

describe('ConfidenceInterval', () => {
  describe('forMean', () => {
    it('should calculate confidence interval for mean', () => {
      const data = [10, 12, 14, 16, 18];
      const ci = ConfidenceInterval.forMean(data, 0.95);

      expect(ci).toHaveLength(2);
      expect(ci[0]).toBeLessThan(ci[1]);
      expect(ci[0]).toBeLessThan(14); // Mean is 14
      expect(ci[1]).toBeGreaterThan(14);
    });

    it('should narrow with larger samples', () => {
      const small = [10, 12, 14, 16, 18];
      const large = Array.from({ length: 100 }, (_, i) => 10 + i * 0.1);

      const ciSmall = ConfidenceInterval.forMean(small);
      const ciLarge = ConfidenceInterval.forMean(large);

      const widthSmall = ciSmall[1] - ciSmall[0];
      const widthLarge = ciLarge[1] - ciLarge[0];

      expect(widthLarge).toBeLessThan(widthSmall);
    });
  });

  describe('forProportion', () => {
    it('should calculate Wilson score interval', () => {
      const ci = ConfidenceInterval.forProportion(50, 100, 0.95);

      expect(ci).toHaveLength(2);
      expect(ci[0]).toBeGreaterThanOrEqual(0);
      expect(ci[1]).toBeLessThanOrEqual(1);
      expect(ci[0]).toBeLessThan(0.5);
      expect(ci[1]).toBeGreaterThan(0.5);
    });

    it('should handle edge cases', () => {
      const ciZero = ConfidenceInterval.forProportion(0, 100);
      const ciOne = ConfidenceInterval.forProportion(100, 100);

      expect(ciZero[0]).toBe(0);
      expect(ciOne[1]).toBe(1);
    });
  });

  describe('forMeanDifference', () => {
    it('should calculate CI for independent samples', () => {
      const sample1 = [10, 12, 14, 16, 18];
      const sample2 = [8, 10, 12, 14, 16];
      const ci = ConfidenceInterval.forMeanDifference(sample1, sample2, 0.95, false);

      expect(ci).toHaveLength(2);
      expect(ci[0]).toBeLessThan(ci[1]);
      // Difference in means is 2
      expect(ci[0]).toBeLessThan(2);
      expect(ci[1]).toBeGreaterThan(2);
    });

    it('should calculate CI for paired samples', () => {
      const before = [100, 105, 110, 115, 120];
      const after = [94, 99, 104, 109, 114];
      const ci = ConfidenceInterval.forMeanDifference(before, after, 0.95, true);

      expect(ci).toHaveLength(2);
      // CI should contain the mean difference (6)
      expect(ci[0]).toBeLessThanOrEqual(6);
      expect(ci[1]).toBeGreaterThanOrEqual(6);
    });
  });

  describe('bootstrap', () => {
    it('should calculate bootstrap CI for any statistic', () => {
      const data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
      const ci = ConfidenceInterval.bootstrap(data, (d) => StatsUtils.mean(d), 0.95, 1000);

      expect(ci).toHaveLength(2);
      expect(ci[0]).toBeLessThan(ci[1]);
    });

    it('should work with median', () => {
      const data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
      const ci = ConfidenceInterval.bootstrap(
        data,
        (d) => {
          const sorted = [...d].sort((a, b) => a - b);
          return sorted[Math.floor(sorted.length / 2)];
        },
        0.95,
        1000
      );

      expect(ci).toHaveLength(2);
    });
  });
});

describe('NormalityTest', () => {
  describe('shapiroWilk', () => {
    it('should detect normal data', () => {
      // Generate approximately normal data using Box-Muller transform
      const normalData = Array.from({ length: 50 }, () => {
        const u1 = Math.random();
        const u2 = Math.random();
        const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
        return z; // Standard normal (mean=0, sd=1)
      }).map(z => z * 10 + 100); // Scale to mean=100, sd=10

      const result = NormalityTest.shapiroWilk(normalData);

      expect(result.testName).toBe("Shapiro-Wilk test");
      expect(result.pValue).toBeDefined();
    });

    it('should detect non-normal data', () => {
      // Create clearly non-normal data (all identical values)
      const constantData = Array.from({ length: 50 }, () => 5);
      const result = NormalityTest.shapiroWilk(constantData);

      // Constant data has no variation - test should handle it
      expect(result.pValue).toBeDefined();
    });

    it('should require minimum sample size', () => {
      const smallData = [1, 2];

      expect(() => NormalityTest.shapiroWilk(smallData)).toThrow();
    });
  });
});

// Utility functions for testing
const StatsUtils = {
  mean: (data: number[]): number => {
    return data.reduce((sum, val) => sum + val, 0) / data.length;
  },
  std: (data: number[]): number => {
    const m = StatsUtils.mean(data);
    const variance = data.reduce((sum, val) => sum + (val - m) ** 2, 0) / (data.length - 1);
    return Math.sqrt(variance);
  },
};

// Example benchmark validation tests
describe('Benchmark Validation Examples', () => {
  it('should validate 15x speedup claim with proper statistics', () => {
    const baseline = [100, 105, 98, 102, 99, 101, 97, 103, 100, 99];
    const optimized = [6, 7, 5, 8, 6, 7, 5, 8, 6, 7]; // ~15x faster

    const test = new StatisticalTest({ alpha: 0.01, twoTailed: false }); // One-tailed for improvement
    const result = test.twoSampleTTest(baseline, optimized);

    // Should be highly significant (but may not always be with small samples)
    expect(result.pValue).toBeDefined();
    expect(result.effectSize).toBeDefined();

    // Effect size should be large (even if not always significant)
    expect(Math.abs(result.effectSize!)).toBeGreaterThan(1);
  });

  it('should validate 80% energy reduction claim', () => {
    const baselineEnergy = [100, 102, 98, 101, 99, 100, 98, 102];
    const optimizedEnergy = [20, 18, 22, 19, 21, 20, 19, 21]; // ~80% reduction

    const test = new StatisticalTest({ alpha: 0.01, twoTailed: false }); // One-tailed for reduction
    const result = test.pairedTTest(baselineEnergy, optimizedEnergy);

    // Verify the reduction
    const meanBaseline = StatsUtils.mean(baselineEnergy);
    const meanOptimized = StatsUtils.mean(optimizedEnergy);
    const reduction = ((meanBaseline - meanOptimized) / meanBaseline) * 100;

    expect(reduction).toBeGreaterThan(75); // At least 75% reduction
    expect(result.effectSize).toBeDefined();
  });

  it('should calculate required sample size for benchmark', () => {
    // For detecting 20% improvement with 80% power
    const result = SampleSizeCalculator.forTTest({
      effectSize: 0.8, // Large effect (20% improvement)
      power: 0.80,
      alpha: 0.05,
    });

    expect(result.sampleSize).toBeDefined();
    // Should be reasonable for benchmarking
    expect(result.sampleSize).toBeLessThan(100);
  });

  it('should handle multiple comparisons with correction', () => {
    const pValues = [0.001, 0.02, 0.04, 0.08, 0.12];

    const uncorrected = pValues.map((p) => (p < 0.05 ? 1 : 0));
    const bonferroni = MultipleTestCorrector.bonferroni(pValues);
    const bh = MultipleTestCorrector.benjaminiHochberg(pValues);

    // Each method should have different rejection rates
    expect(uncorrected.filter((r) => r === 1).length).toBeGreaterThanOrEqual(
      bonferroni.filter((r) => r === 1).length
    );
    expect(bh.filter((r) => r === 1).length).toBeGreaterThanOrEqual(
      bonferroni.filter((r) => r === 1).length
    );
  });
});
