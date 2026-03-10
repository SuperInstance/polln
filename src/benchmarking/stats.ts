/**
 * Statistical Testing Module for Benchmark Validation
 *
 * Provides rigorous statistical methodology for validating performance claims
 * including hypothesis testing, effect size calculation, confidence intervals,
 * sample size calculation, and multiple comparison correction.
 *
 * @module benchmarking/stats
 */

/**
 * Result of a statistical hypothesis test
 */
export interface HypothesisTestResult {
  /** Test statistic value */
  statistic: number;
  /** P-value */
  pValue: number;
  /** Whether null hypothesis is rejected at given alpha */
  rejected: boolean;
  /** Significance level used */
  alpha: number;
  /** Test name */
  testName: string;
  /** Effect size */
  effectSize?: number;
  /** Confidence interval for effect size */
  confidenceInterval?: [number, number];
  /** Additional test-specific information */
  details?: Record<string, unknown>;
}

/**
 * Result of an effect size calculation
 */
export interface EffectSizeResult {
  /** Effect size value */
  value: number;
  /** Effect size type (e.g., 'cohens_d', 'cliff_delta') */
  type: string;
  /** Interpretation (e.g., 'small', 'medium', 'large') */
  interpretation: string;
  /** Confidence interval */
  confidenceInterval: [number, number];
  /** Confidence level */
  confidenceLevel: number;
}

/**
 * Result of a power analysis
 */
export interface PowerAnalysisResult {
  /** Required sample size */
  sampleSize: number;
  /** Statistical power achieved */
  power: number;
  /** Significance level */
  alpha: number;
  /** Effect size assumed */
  effectSize: number;
  /** Test type */
  testType: string;
}

/**
 * Configuration for hypothesis tests
 */
export interface TestConfig {
  /** Significance level (default: 0.05) */
  alpha?: number;
  /** Whether to use two-tailed test (default: true) */
  twoTailed?: boolean;
  /** Confidence level for intervals (default: 0.95) */
  confidenceLevel?: number;
  /** Number of bootstrap iterations (default: 10000) */
  bootstrapIterations?: number;
}

/**
 * Default test configuration
 */
const DEFAULT_CONFIG: Required<TestConfig> = {
  alpha: 0.05,
  twoTailed: true,
  confidenceLevel: 0.95,
  bootstrapIterations: 10000,
};

/**
 * Statistical distributions for critical values
 */
class Distributions {
  /**
   * Approximate normal CDF using error function
   */
  static normalCDF(x: number): number {
    const a1 = 0.254829592;
    const a2 = -0.284496736;
    const a3 = 1.421413741;
    const a4 = -1.453152027;
    const a5 = 1.061405429;
    const p = 0.3275911;

    const sign = x < 0 ? -1 : 1;
    x = Math.abs(x) / Math.sqrt(2);

    const t = 1.0 / (1.0 + p * x);
    const y =
      1.0 -
      (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x);

    return 0.5 * (1.0 + sign * y);
  }

  /**
   * Approximate inverse normal CDF (quantile function)
   */
  static normalInverse(p: number): number {
    if (p <= 0 || p >= 1) {
      throw new Error('p must be between 0 and 1');
    }

    const a = [-3.969683028665376e1, 2.209460984245205e2, -2.759285104469687e2, 1.383577518672690e2, -3.066479806614716e1, 2.506628277459239e0];
    const b = [-5.447609879822406e1, 1.615858368580409e2, -1.556989798598866e2, 6.680131188771972e1, -1.328068155288572e1];
    const c = [-7.784894002430293e-3, -3.223964580411365e-1, -2.400758277161838e0, -2.549732539343734e0, 4.374664141464968e0, 2.938163982698783e0];
    const d = [7.784695709041462e-3, 3.224671290700398e-1, 2.445134137142996e0, 3.754408661907416e0];

    const pLow = 0.02425;
    const pHigh = 1 - pLow;
    let q: number;
    let r: number;

    if (p < pLow) {
      q = Math.sqrt(-2 * Math.log(p));
      return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1);
    } else if (p <= pHigh) {
      q = p - 0.5;
      r = q * q;
      return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1);
    } else {
      q = Math.sqrt(-2 * Math.log(1 - p));
      return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1);
    }
  }

  /**
   * Student's t distribution CDF (approximation)
   */
  static tCDF(t: number, df: number): number {
    if (df === Infinity) {
      return this.normalCDF(t);
    }

    const x = (t * t) / (df + t * t);
    const a = df / 2;
    const b = 0.5;

    // Regularized incomplete beta function approximation
    return this.betaRegularized(x, a, b);
  }

  /**
   * Regularized incomplete beta function
   */
  static betaRegularized(x: number, a: number, b: number): number {
    if (x === 0) return 0;
    if (x === 1) return 1;

    // Lanczos approximation for continued fraction
    const lbeta = (x: number, a: number, b: number): number => {
      const EPS = 3.0e-7;
      const MAXIT = 100;

      let qab = a + b;
      let qap = a + 1;
      let qam = a - 1;
      let c = 1;
      let d = 1 - qab * x / qap;

      if (Math.abs(d) < EPS) d = EPS;
      d = 1 / d;
      let h = d;

      for (let m = 1; m <= MAXIT; m++) {
        let m2 = 2 * m;
        let aa = m * (b - m) * x / ((qam + m2) * (a + m2));
        d = 1 + aa * d;
        if (Math.abs(d) < EPS) d = EPS;
        c = 1 + aa / c;
        if (Math.abs(c) < EPS) c = EPS;
        d = 1 / d;
        h *= d * c;

        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2));
        d = 1 + aa * d;
        if (Math.abs(d) < EPS) d = EPS;
        c = 1 + aa / c;
        if (Math.abs(c) < EPS) c = EPS;
        d = 1 / d;
        h *= d * c;
      }

      return h;
    };

    return Math.exp(a * Math.log(x) + b * Math.log(1 - x)) * lbeta(x, a, b) / a;
  }

  /**
   * Get critical value for two-tailed t-test
   */
  static tCritical(alpha: number, df: number): number {
    const p = 1 - alpha / 2;
    // Binary search for inverse
    let low = -10;
    let high = 10;
    for (let i = 0; i < 50; i++) {
      const mid = (low + high) / 2;
      if (this.tCDF(mid, df) < p) {
        low = mid;
      } else {
        high = mid;
      }
    }
    return (low + high) / 2;
  }
}

/**
 * Statistical utility functions
 */
class StatsUtils {
  /**
   * Calculate mean of array
   */
  static mean(data: number[]): number {
    if (data.length === 0) throw new Error('Cannot calculate mean of empty array');
    return data.reduce((sum, val) => sum + val, 0) / data.length;
  }

  /**
   * Calculate sample standard deviation
   */
  static std(data: number[], ddof = 1): number {
    if (data.length < 2) throw new Error('Need at least 2 data points');
    const m = this.mean(data);
    const variance = data.reduce((sum, val) => sum + (val - m) ** 2, 0) / (data.length - ddof);
    return Math.sqrt(variance);
  }

  /**
   * Calculate median
   */
  static median(data: number[]): number {
    if (data.length === 0) throw new Error('Cannot calculate median of empty array');
    const sorted = [...data].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 !== 0 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
  }

  /**
   * Calculate percentile using linear interpolation
   */
  static percentile(data: number[], p: number): number {
    if (data.length === 0) throw new Error('Cannot calculate percentile of empty array');
    if (p < 0 || p > 100) throw new Error('Percentile must be between 0 and 100');

    const sorted = [...data].sort((a, b) => a - b);
    const index = (p / 100) * (sorted.length - 1);
    const lower = Math.floor(index);
    const upper = Math.ceil(index);
    const weight = index - lower;

    return sorted[lower] * (1 - weight) + sorted[upper] * weight;
  }

  /**
   * Calculate variance
   */
  static variance(data: number[], ddof = 1): number {
    if (data.length < 2) throw new Error('Need at least 2 data points');
    const m = this.mean(data);
    return data.reduce((sum, val) => sum + (val - m) ** 2, 0) / (data.length - ddof);
  }

  /**
   * Calculate standard error of the mean
   */
  static sem(data: number[]): number {
    if (data.length < 2) throw new Error('Need at least 2 data points');
    return this.std(data) / Math.sqrt(data.length);
  }

  /**
   * Calculate sum of products for two arrays
   */
  static sumProduct(x: number[], y: number[]): number {
    if (x.length !== y.length) throw new Error('Arrays must have same length');
    return x.reduce((sum, val, i) => sum + val * y[i], 0);
  }
}

/**
 * Bootstrap resampling for confidence intervals
 */
class Bootstrap {
  /**
   * Generate bootstrap sample
   */
  static resample(data: number[]): number[] {
    const n = data.length;
    const sample: number[] = [];
    for (let i = 0; i < n; i++) {
      sample.push(data[Math.floor(Math.random() * n)]);
    }
    return sample;
  }

  /**
   * Calculate bootstrap confidence interval
   */
  static confidenceInterval(
    data: number[],
    statistic: (data: number[]) => number,
    confidenceLevel: number,
    iterations: number = 10000
  ): [number, number] {
    const alpha = 1 - confidenceLevel;
    const bootstrapStats: number[] = [];

    for (let i = 0; i < iterations; i++) {
      const sample = this.resample(data);
      bootstrapStats.push(statistic(sample));
    }

    bootstrapStats.sort((a, b) => a - b);
    const lowerIndex = Math.floor((alpha / 2) * iterations);
    const upperIndex = Math.floor((1 - alpha / 2) * iterations);

    return [bootstrapStats[lowerIndex], bootstrapStats[upperIndex]];
  }

  /**
   * Calculate standard error using bootstrap
   */
  static standardError(
    data: number[],
    statistic: (data: number[]) => number,
    iterations: number = 10000
  ): number {
    const bootstrapStats: number[] = [];

    for (let i = 0; i < iterations; i++) {
      const sample = this.resample(data);
      bootstrapStats.push(statistic(sample));
    }

    return StatsUtils.std(bootstrapStats);
  }
}

/**
 * Statistical hypothesis testing framework
 */
export class StatisticalTest {
  private config: Required<TestConfig>;

  constructor(config: TestConfig = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config };
  }

  /**
   * One-sample t-test
   * Tests if sample mean differs from specified value
   */
  oneSampleTTest(sample: number[], nullValue: number = 0): HypothesisTestResult {
    if (sample.length < 2) {
      throw new Error('Sample must have at least 2 observations');
    }

    const n = sample.length;
    const sampleMean = StatsUtils.mean(sample);
    const sampleStd = StatsUtils.std(sample);
    const standardError = sampleStd / Math.sqrt(n);
    const statistic = (sampleMean - nullValue) / standardError;
    const df = n - 1;

    // Calculate p-value
    let pValue: number;
    if (this.config.twoTailed) {
      pValue = 2 * (1 - Distributions.tCDF(Math.abs(statistic), df));
    } else {
      // One-tailed: check direction
      if (statistic > 0) {
        pValue = 1 - Distributions.tCDF(statistic, df);
      } else {
        pValue = Distributions.tCDF(statistic, df);
      }
    }

    const effectSize = (sampleMean - nullValue) / sampleStd;
    const ci = this.bootstrapConfidenceInterval(
      sample,
      (d) => (StatsUtils.mean(d) - nullValue) / StatsUtils.std(d)
    );

    return {
      statistic,
      pValue,
      rejected: pValue < this.config.alpha,
      alpha: this.config.alpha,
      testName: 'One-sample t-test',
      effectSize,
      confidenceInterval: ci,
      details: { df, sampleMean, sampleStd, standardError },
    };
  }

  /**
   * Two-sample independent t-test
   * Tests if two samples have different means
   */
  twoSampleTTest(sample1: number[], sample2: number[], equalVariance: boolean = true): HypothesisTestResult {
    if (sample1.length < 2 || sample2.length < 2) {
      throw new Error('Both samples must have at least 2 observations');
    }

    const n1 = sample1.length;
    const n2 = sample2.length;
    const mean1 = StatsUtils.mean(sample1);
    const mean2 = StatsUtils.mean(sample2);
    const var1 = StatsUtils.variance(sample1);
    const var2 = StatsUtils.variance(sample2);

    let statistic: number;
    let df: number;

    if (equalVariance) {
      // Pooled variance t-test
      const pooledVar = ((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2);
      const standardError = Math.sqrt(pooledVar * (1 / n1 + 1 / n2));
      statistic = (mean1 - mean2) / standardError;
      df = n1 + n2 - 2;
    } else {
      // Welch's t-test (unequal variance)
      const se1 = var1 / n1;
      const se2 = var2 / n2;
      const standardError = Math.sqrt(se1 + se2);
      statistic = (mean1 - mean2) / standardError;

      // Welch-Satterthwaite degrees of freedom
      df = Math.floor(
        (se1 + se2) ** 2 / (se1 ** 2 / (n1 - 1) + se2 ** 2 / (n2 - 1))
      );
    }

    // Calculate p-value
    let pValue: number;
    if (this.config.twoTailed) {
      pValue = 2 * (1 - Distributions.tCDF(Math.abs(statistic), df));
    } else {
      // One-tailed: check direction (mean1 > mean2)
      if (statistic > 0) {
        pValue = 1 - Distributions.tCDF(statistic, df);
      } else {
        pValue = Distributions.tCDF(statistic, df);
      }
    }

    // Calculate effect size (Cohen's d)
    const pooledStd = Math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2));
    const effectSize = (mean1 - mean2) / pooledStd;

    const ci = this.bootstrapConfidenceInterval(
      [...sample1, ...sample2],
      (data) => {
        const split = Math.floor(data.length / 2);
        const s1 = data.slice(0, split);
        const s2 = data.slice(split);
        return (StatsUtils.mean(s1) - StatsUtils.mean(s2)) / pooledStd;
      }
    );

    return {
      statistic,
      pValue,
      rejected: pValue < this.config.alpha,
      alpha: this.config.alpha,
      testName: equalVariance ? 'Two-sample t-test (equal variance)' : "Welch's t-test",
      effectSize,
      confidenceInterval: ci,
      details: { df, mean1, mean2, equalVariance },
    };
  }

  /**
   * Paired t-test
   * Tests if the mean difference between paired observations is zero
   */
  pairedTTest(sample1: number[], sample2: number[]): HypothesisTestResult {
    if (sample1.length !== sample2.length) {
      throw new Error('Samples must have the same length for paired test');
    }
    if (sample1.length < 2) {
      throw new Error('Need at least 2 paired observations');
    }

    const differences = sample1.map((val, i) => val - sample2[i]);
    const n = differences.length;
    const meanDiff = StatsUtils.mean(differences);
    const stdDiff = StatsUtils.std(differences);
    const standardError = stdDiff / Math.sqrt(n);
    const statistic = meanDiff / standardError;
    const df = n - 1;

    // Calculate p-value
    let pValue: number;
    if (this.config.twoTailed) {
      pValue = 2 * (1 - Distributions.tCDF(Math.abs(statistic), df));
    } else {
      // One-tailed: check direction (before > after, so differences should be positive)
      if (statistic > 0) {
        pValue = 1 - Distributions.tCDF(statistic, df);
      } else {
        pValue = Distributions.tCDF(statistic, df);
      }
    }

    // Effect size (Cohen's d for paired samples)
    const effectSize = meanDiff / stdDiff;

    const ci = this.bootstrapConfidenceInterval(
      differences,
      (d) => StatsUtils.mean(d) / StatsUtils.std(d)
    );

    return {
      statistic,
      pValue,
      rejected: pValue < this.config.alpha,
      alpha: this.config.alpha,
      testName: 'Paired t-test',
      effectSize,
      confidenceInterval: ci,
      details: { df, meanDiff, stdDiff },
    };
  }

  /**
   * Mann-Whitney U test (non-parametric alternative to t-test)
   * Tests if two samples come from different distributions
   */
  mannWhitneyUTest(sample1: number[], sample2: number[]): HypothesisTestResult {
    if (sample1.length === 0 || sample2.length === 0) {
      throw new Error('Both samples must have at least 1 observation');
    }

    const n1 = sample1.length;
    const n2 = sample2.length;
    const combined = [...sample1.map((v) => ({ value: v, group: 1 })), ...sample2.map((v) => ({ value: v, group: 2 }))];

    // Rank all values
    combined.sort((a, b) => a.value - b.value);

    // Handle ties: assign average rank
    const ranks: number[] = [];
    let i = 0;
    while (i < combined.length) {
      let j = i;
      while (j < combined.length && combined[j].value === combined[i].value) {
        j++;
      }
      const avgRank = (i + j + 1) / 2;
      for (let k = i; k < j; k++) {
        ranks[k] = avgRank;
      }
      i = j;
    }

    // Sum ranks for sample 1
    const R1 = combined.reduce((sum, obs, idx) => (obs.group === 1 ? sum + ranks[idx] : sum), 0);

    // Calculate U statistic
    const U1 = R1 - (n1 * (n1 + 1)) / 2;
    const U2 = n1 * n2 - U1;
    const U = Math.min(U1, U2);

    // Calculate mean and standard deviation for large samples
    const meanU = (n1 * n2) / 2;
    const varU = (n1 * n2 * (n1 + n2 + 1)) / 12;

    // Z-score approximation (valid for n1 > 20 and n2 > 20)
    const statistic = (U - meanU) / Math.sqrt(varU);

    // Calculate p-value
    let pValue: number;
    if (this.config.twoTailed) {
      pValue = 2 * (1 - Distributions.normalCDF(Math.abs(statistic)));
    } else {
      pValue = 1 - Distributions.normalCDF(statistic);
    }

    // Effect size (Cliff's delta)
    const effectSize = this.cliffsDelta(sample1, sample2);

    const ci = this.bootstrapConfidenceInterval(
      [...sample1, ...sample2],
      (data) => {
        const split = Math.floor(data.length / 2);
        return this.cliffsDelta(data.slice(0, split), data.slice(split));
      }
    );

    return {
      statistic,
      pValue,
      rejected: pValue < this.config.alpha,
      alpha: this.config.alpha,
      testName: "Mann-Whitney U test",
      effectSize,
      confidenceInterval: ci,
      details: { U, U1, U2, R1, largeSampleApproximation: n1 > 20 && n2 > 20 },
    };
  }

  /**
   * Wilcoxon signed-rank test (non-parametric paired test)
   * Tests if paired differences are symmetric around zero
   */
  wilcoxonSignedRankTest(sample1: number[], sample2: number[]): HypothesisTestResult {
    if (sample1.length !== sample2.length) {
      throw new Error('Samples must have the same length for paired test');
    }
    if (sample1.length < 2) {
      throw new Error('Need at least 2 paired observations');
    }

    const differences = sample1.map((val, i) => val - sample2[i]);

    // Remove zero differences
    const nonZeroDiffs = differences.filter((d) => d !== 0);
    const n = nonZeroDiffs.length;

    if (n < 2) {
      throw new Error('Need at least 2 non-zero differences');
    }

    // Rank absolute values
    const absDiffs = nonZeroDiffs.map((d, i) => ({ abs: Math.abs(d), sign: Math.sign(d), idx: i }));
    absDiffs.sort((a, b) => a.abs - b.abs);

    // Handle ties
    const ranks: number[] = [];
    let i = 0;
    while (i < absDiffs.length) {
      let j = i;
      while (j < absDiffs.length && absDiffs[j].abs === absDiffs[i].abs) {
        j++;
      }
      const avgRank = (i + j + 1) / 2;
      for (let k = i; k < j; k++) {
        ranks[k] = avgRank;
      }
      i = j;
    }

    // Sum ranks for positive and negative differences
    let WPlus = 0;
    let WMinus = 0;
    for (let i = 0; i < absDiffs.length; i++) {
      if (absDiffs[i].sign > 0) {
        WPlus += ranks[i];
      } else {
        WMinus += ranks[i];
      }
    }

    const W = Math.min(WPlus, WMinus);

    // Normal approximation for large samples (n > 20)
    const meanW = n * (n + 1) / 4;
    const varW = n * (n + 1) * (2 * n + 1) / 24;
    const statistic = (W - meanW) / Math.sqrt(varW);

    // Calculate p-value
    let pValue: number;
    if (this.config.twoTailed) {
      pValue = 2 * (1 - Distributions.normalCDF(Math.abs(statistic)));
    } else {
      pValue = 1 - Distributions.normalCDF(statistic);
    }

    // Effect size (rank-biserial correlation)
    const effectSize = (WPlus - WMinus) / (WPlus + WMinus);

    const ci = this.bootstrapConfidenceInterval(
      differences.filter((d) => d !== 0),
      (diffs) => {
        const abs = diffs.map((d) => Math.abs(d)).sort((a, b) => a - b);
        const ranks = abs.map((_, i) => i + 1);
        const posSum = diffs.filter((d) => d > 0).reduce((sum, d) => sum + ranks[abs.indexOf(Math.abs(d))], 0);
        const negSum = diffs.filter((d) => d < 0).reduce((sum, d) => sum + ranks[abs.indexOf(Math.abs(d))], 0);
        return (posSum - negSum) / (posSum + negSum);
      }
    );

    return {
      statistic,
      pValue,
      rejected: pValue < this.config.alpha,
      alpha: this.config.alpha,
      testName: 'Wilcoxon signed-rank test',
      effectSize,
      confidenceInterval: ci,
      details: { W, WPlus, WMinus, n, largeSampleApproximation: n > 20 },
    };
  }

  /**
   * Calculate Cliff's delta effect size
   */
  private cliffsDelta(sample1: number[], sample2: number[]): number {
    let greater = 0;
    let less = 0;

    for (const x of sample1) {
      for (const y of sample2) {
        if (x > y) greater++;
        else if (x < y) less++;
      }
    }

    const total = sample1.length * sample2.length;
    return (greater - less) / total;
  }

  /**
   * Bootstrap confidence interval for effect size
   */
  private bootstrapConfidenceInterval(
    data: number[],
    statistic: (data: number[]) => number
  ): [number, number] {
    return Bootstrap.confidenceInterval(
      data,
      statistic,
      this.config.confidenceLevel,
      this.config.bootstrapIterations
    );
  }
}

/**
 * Effect size calculator
 */
export class EffectSizeCalculator {
  /**
   * Calculate Cohen's d (standardized mean difference)
   */
  static cohensD(sample1: number[], sample2: number[]): EffectSizeResult {
    const mean1 = StatsUtils.mean(sample1);
    const mean2 = StatsUtils.mean(sample2);
    const var1 = StatsUtils.variance(sample1);
    const var2 = StatsUtils.variance(sample2);
    const n1 = sample1.length;
    const n2 = sample2.length;

    // Pooled standard deviation
    const pooledStd = Math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2));
    const cohensD = (mean1 - mean2) / pooledStd;

    // Bootstrap confidence interval
    const ci = Bootstrap.confidenceInterval(
      [...sample1, ...sample2],
      (data) => {
        const split = Math.floor(data.length / 2);
        const s1 = data.slice(0, split);
        const s2 = data.slice(split);
        const m1 = StatsUtils.mean(s1);
        const m2 = StatsUtils.mean(s2);
        const v1 = StatsUtils.variance(s1);
        const v2 = StatsUtils.variance(s2);
        const sn1 = s1.length;
        const sn2 = s2.length;
        const ps = Math.sqrt(((sn1 - 1) * v1 + (sn2 - 1) * v2) / (sn1 + sn2 - 2));
        return (m1 - m2) / ps;
      },
      0.95,
      10000
    );

    return {
      value: cohensD,
      type: 'cohens_d',
      interpretation: this.interpretCohensD(Math.abs(cohensD)),
      confidenceInterval: ci,
      confidenceLevel: 0.95,
    };
  }

  /**
   * Calculate Hedges' g (bias-corrected Cohen's d)
   */
  static hedgesG(sample1: number[], sample2: number[]): EffectSizeResult {
    const cohensDResult = this.cohensD(sample1, sample2);
    const n1 = sample1.length;
    const n2 = sample2.length;
    const df = n1 + n2 - 2;

    // Bias correction factor
    const J = 1 - 3 / (4 * df - 1);
    const hedgesG = cohensDResult.value * J;

    // Adjust confidence interval
    const ci: [number, number] = [
      cohensDResult.confidenceInterval[0] * J,
      cohensDResult.confidenceInterval[1] * J,
    ];

    return {
      value: hedgesG,
      type: 'hedges_g',
      interpretation: this.interpretCohensD(Math.abs(hedgesG)),
      confidenceInterval: ci,
      confidenceLevel: 0.95,
    };
  }

  /**
   * Calculate Cliff's delta (non-parametric effect size)
   */
  static cliffsDelta(sample1: number[], sample2: number[]): EffectSizeResult {
    let greater = 0;
    let less = 0;

    for (const x of sample1) {
      for (const y of sample2) {
        if (x > y) greater++;
        else if (x < y) less++;
      }
    }

    const total = sample1.length * sample2.length;
    const delta = (greater - less) / total;

    // Bootstrap confidence interval
    const ci = Bootstrap.confidenceInterval(
      [...sample1, ...sample2],
      (data) => {
        const split = Math.floor(data.length / 2);
        const s1 = data.slice(0, split);
        const s2 = data.slice(split);
        let g = 0;
        let l = 0;
        for (const x of s1) {
          for (const y of s2) {
            if (x > y) g++;
            else if (x < y) l++;
          }
        }
        return (g - l) / (s1.length * s2.length);
      },
      0.95,
      10000
    );

    return {
      value: delta,
      type: 'cliff_delta',
      interpretation: this.interpretCliffsDelta(Math.abs(delta)),
      confidenceInterval: ci,
      confidenceLevel: 0.95,
    };
  }

  /**
   * Calculate Glass's delta (using control group standard deviation)
   */
  static glasssDelta(
    treatment: number[],
    control: number[]
  ): EffectSizeResult {
    const meanTreatment = StatsUtils.mean(treatment);
    const meanControl = StatsUtils.mean(control);
    const stdControl = StatsUtils.std(control);

    const glasssDelta = (meanTreatment - meanControl) / stdControl;

    // Bootstrap confidence interval
    const ci = Bootstrap.confidenceInterval(
      [...treatment, ...control],
      (data) => {
        const split = Math.floor(data.length / 2);
        const t = data.slice(0, split);
        const c = data.slice(split);
        return (StatsUtils.mean(t) - StatsUtils.mean(c)) / StatsUtils.std(c);
      },
      0.95,
      10000
    );

    return {
      value: glasssDelta,
      type: 'glass_delta',
      interpretation: this.interpretCohensD(Math.abs(glasssDelta)),
      confidenceInterval: ci,
      confidenceLevel: 0.95,
    };
  }

  /**
   * Calculate Pearson correlation coefficient (r)
   */
  static pearsonR(x: number[], y: number[]): EffectSizeResult {
    if (x.length !== y.length) {
      throw new Error('Arrays must have same length');
    }
    if (x.length < 3) {
      throw new Error('Need at least 3 data points');
    }

    const n = x.length;
    const meanX = StatsUtils.mean(x);
    const meanY = StatsUtils.mean(y);

    const numerator = StatsUtils.sumProduct(
      x.map((xi) => xi - meanX),
      y.map((yi) => yi - meanY)
    );

    const denominator =
      Math.sqrt(x.reduce((sum, xi) => sum + (xi - meanX) ** 2, 0)) *
      Math.sqrt(y.reduce((sum, yi) => sum + (yi - meanY) ** 2, 0));

    const r = numerator / denominator;

    // Bootstrap confidence interval using Fisher's z transformation
    const ci = Bootstrap.confidenceInterval(
      Array.from({ length: n }, (_, i) => [x[i], y[i]]),
      (pairs) => {
        const px = pairs.map((p) => p[0]);
        const py = pairs.map((p) => p[1]);
        const pmx = StatsUtils.mean(px);
        const pmy = StatsUtils.mean(py);
        const pNum = StatsUtils.sumProduct(
          px.map((xi) => xi - pmx),
          py.map((yi) => yi - pmy)
        );
        const pDen =
          Math.sqrt(px.reduce((sum, xi) => sum + (xi - pmx) ** 2, 0)) *
          Math.sqrt(py.reduce((sum, yi) => sum + (yi - pmy) ** 2, 0));
        return pNum / pDen;
      },
      0.95,
      10000
    );

    return {
      value: r,
      type: 'pearson_r',
      interpretation: this.interpretCorrelation(Math.abs(r)),
      confidenceInterval: ci,
      confidenceLevel: 0.95,
    };
  }

  /**
   * Interpret Cohen's d effect size
   */
  private static interpretCohensD(d: number): string {
    if (d < 0.2) return 'negligible';
    if (d < 0.5) return 'small';
    if (d < 0.8) return 'medium';
    return 'large';
  }

  /**
   * Interpret Cliff's delta effect size
   */
  private static interpretCliffsDelta(delta: number): string {
    if (delta < 0.147) return 'negligible';
    if (delta < 0.33) return 'small';
    if (delta < 0.474) return 'medium';
    return 'large';
  }

  /**
   * Interpret correlation strength
   */
  private static interpretCorrelation(r: number): string {
    if (r < 0.1) return 'negligible';
    if (r < 0.3) return 'small';
    if (r < 0.5) return 'medium';
    if (r < 0.7) return 'large';
    return 'very large';
  }
}

/**
 * Sample size calculator (power analysis)
 */
export class SampleSizeCalculator {
  /**
   * Calculate required sample size for t-test
   */
  static forTTest(config: {
    /** Effect size (Cohen's d) */
    effectSize: number;
    /** Desired statistical power (default: 0.80) */
    power?: number;
    /** Significance level (default: 0.05) */
    alpha?: number;
    /** Whether test is two-tailed (default: true) */
    twoTailed?: boolean;
    /** Allocation ratio (n2/n1, default: 1 for equal sizes) */
    ratio?: number;
  }): PowerAnalysisResult {
    const power = config.power ?? 0.80;
    const alpha = config.alpha ?? 0.05;
    const twoTailed = config.twoTailed ?? true;
    const ratio = config.ratio ?? 1;

    if (config.effectSize <= 0) {
      throw new Error('Effect size must be positive');
    }

    // Z-scores for power and alpha
    const zBeta = Distributions.normalInverse(power);
    const zAlpha = Distributions.normalInverse(1 - alpha / (twoTailed ? 2 : 1));

    // Sample size formula for two-sample t-test
    const numerator = 2 * (zAlpha + zBeta) ** 2;
    const denominator = config.effectSize ** 2;

    // Adjust for unequal allocation
    const n1 = Math.ceil((numerator / denominator) * (1 + ratio) / (2 * ratio));
    const n2 = Math.ceil(n1 * ratio);

    return {
      sampleSize: n1 + n2,
      power,
      alpha,
      effectSize: config.effectSize,
      testType: twoTailed ? 'Two-sample t-test (two-tailed)' : 'Two-sample t-test (one-tailed)',
    };
  }

  /**
   * Calculate required sample size for paired t-test
   */
  static forPairedTTest(config: {
    /** Effect size (Cohen's d for paired) */
    effectSize: number;
    /** Desired statistical power (default: 0.80) */
    power?: number;
    /** Significance level (default: 0.05) */
    alpha?: number;
    /** Whether test is two-tailed (default: true) */
    twoTailed?: boolean;
  }): PowerAnalysisResult {
    const power = config.power ?? 0.80;
    const alpha = config.alpha ?? 0.05;
    const twoTailed = config.twoTailed ?? true;

    if (config.effectSize <= 0) {
      throw new Error('Effect size must be positive');
    }

    // Z-scores
    const zBeta = Distributions.normalInverse(power);
    const zAlpha = Distributions.normalInverse(1 - alpha / (twoTailed ? 2 : 1));

    // Sample size formula for paired t-test
    const n = Math.ceil(((zAlpha + zBeta) / config.effectSize) ** 2);

    return {
      sampleSize: n,
      power,
      alpha,
      effectSize: config.effectSize,
      testType: twoTailed ? 'Paired t-test (two-tailed)' : 'Paired t-test (one-tailed)',
    };
  }

  /**
   * Calculate required sample size for proportion test
   */
  static forProportionTest(config: {
    /** Expected proportion in group 1 */
    p1: number;
    /** Expected proportion in group 2 */
    p2: number;
    /** Desired statistical power (default: 0.80) */
    power?: number;
    /** Significance level (default: 0.05) */
    alpha?: number;
    /** Whether test is two-tailed (default: true) */
    twoTailed?: boolean;
    /** Allocation ratio (n2/n1, default: 1) */
    ratio?: number;
  }): PowerAnalysisResult {
    const power = config.power ?? 0.80;
    const alpha = config.alpha ?? 0.05;
    const twoTailed = config.twoTailed ?? true;
    const ratio = config.ratio ?? 1;

    if (config.p1 <= 0 || config.p1 >= 1 || config.p2 <= 0 || config.p2 >= 1) {
      throw new Error('Proportions must be between 0 and 1');
    }

    // Pooled proportion
    const pBar = (config.p1 + ratio * config.p2) / (1 + ratio);

    // Effect size
    const effectSize = Math.abs(config.p1 - config.p2);

    // Z-scores
    const zBeta = Distributions.normalInverse(power);
    const zAlpha = Distributions.normalInverse(1 - alpha / (twoTailed ? 2 : 1));

    // Sample size formula
    const p1q1 = config.p1 * (1 - config.p1);
    const p2q2 = config.p2 * (1 - config.p2);

    const n1 = Math.ceil(
      ((zAlpha * Math.sqrt(pBar * (1 - pBar) * (1 + 1 / ratio)) +
        zBeta * Math.sqrt(p1q1 + p2q2 / ratio)) ** 2) /
        effectSize ** 2
    );

    const n2 = Math.ceil(n1 * ratio);

    return {
      sampleSize: n1 + n2,
      power,
      alpha,
      effectSize,
      testType: twoTailed ? 'Two-proportion z-test (two-tailed)' : 'Two-proportion z-test (one-tailed)',
    };
  }

  /**
   * Calculate achieved power given sample size
   */
  static achievedPower(config: {
    /** Sample size(s) - single number or [n1, n2] */
    sampleSize: number | [number, number];
    /** Effect size */
    effectSize: number;
    /** Significance level (default: 0.05) */
    alpha?: number;
    /** Whether test is two-tailed (default: true) */
    twoTailed?: boolean;
  }): PowerAnalysisResult {
    const alpha = config.alpha ?? 0.05;
    const twoTailed = config.twoTailed ?? true;

    let n1: number;
    let n2: number;

    if (typeof config.sampleSize === 'number') {
      n1 = config.sampleSize;
      n2 = config.sampleSize;
    } else {
      [n1, n2] = config.sampleSize;
    }

    // Z-score for alpha
    const zAlpha = Distributions.normalInverse(1 - alpha / (twoTailed ? 2 : 1));

    // Non-centrality parameter (effect size adjusted for sample sizes)
    const n = (n1 + n2) / 2;
    const delta = config.effectSize * Math.sqrt(n / 2);

    // Power = P(Z > z_alpha - delta)
    const power = 1 - Distributions.normalCDF(zAlpha - delta);

    return {
      sampleSize: n1 + n2,
      power,
      alpha,
      effectSize: config.effectSize,
      testType: twoTailed ? 'Two-sample t-test (two-tailed)' : 'Two-sample t-test (one-tailed)',
    };
  }
}

/**
 * Multiple comparison correction
 */
export class MultipleTestCorrector {
  /**
   * Bonferroni correction (conservative)
   */
  static bonferroni(pValues: number[], alpha: number = 0.05): number[] {
    const adjustedAlpha = alpha / pValues.length;
    return pValues.map((p) => (p < adjustedAlpha ? 1 : 0));
  }

  /**
   * Holm-Bonferroni correction (less conservative, more powerful)
   */
  static holm(pValues: number[], alpha: number = 0.05): number[] {
    // Sort p-values with original indices
    const sorted = pValues
      .map((p, i) => ({ p, i }))
      .sort((a, b) => a.p - b.p);

    const rejected = new Array(pValues.length).fill(0);
    let k = 0;

    for (let j = 0; j < sorted.length; j++) {
      const threshold = alpha / (sorted.length - j);
      if (sorted[j].p < threshold) {
        rejected[sorted[j].i] = 1;
        k = j + 1;
      } else {
        break;
      }
    }

    return rejected;
  }

  /**
   * Benjamini-Hochberg FDR correction
   */
  static benjaminiHochberg(pValues: number[], qLevel: number = 0.05): number[] {
    // Sort p-values with original indices
    const sorted = pValues
      .map((p, i) => ({ p, i }))
      .sort((a, b) => a.p - b.p);

    const rejected = new Array(pValues.length).fill(0);
    let largestK = -1;

    // Find largest k where p_k <= (k/m) * q
    for (let k = sorted.length - 1; k >= 0; k--) {
      const threshold = ((k + 1) / sorted.length) * qLevel;
      if (sorted[k].p <= threshold) {
        largestK = k;
        break;
      }
    }

    // Reject all hypotheses with p-value <= p_largestK
    for (let k = 0; k <= largestK; k++) {
      rejected[sorted[k].i] = 1;
    }

    return rejected;
  }

  /**
   * Benjamini-Yekutieli FDR correction (more conservative, valid under dependence)
   */
  static benjaminiYekutieli(pValues: number[], qLevel: number = 0.05): number[] {
    const m = pValues.length;

    // Harmonic number correction factor
    const c = 0;
    for (let i = 1; i <= m; i++) {
      c + 1 / i;
    }

    // Sort p-values with original indices
    const sorted = pValues
      .map((p, i) => ({ p, i }))
      .sort((a, b) => a.p - b.p);

    const rejected = new Array(pValues.length).fill(0);
    let largestK = -1;

    // Find largest k with BY correction
    for (let k = sorted.length - 1; k >= 0; k--) {
      const threshold = ((k + 1) / (m * c)) * qLevel;
      if (sorted[k].p <= threshold) {
        largestK = k;
        break;
      }
    }

    for (let k = 0; k <= largestK; k++) {
      rejected[sorted[k].i] = 1;
    }

    return rejected;
  }

  /**
   * Calculate adjusted p-values (q-values) for FDR
   */
  static calculateQValues(pValues: number[]): number[] {
    // Sort p-values with original indices
    const sorted = pValues
      .map((p, i) => ({ p, i }))
      .sort((a, b) => a.p - b.p);

    const qValues = new Array(pValues.length).fill(1);

    // Calculate adjusted p-values
    let minQ = 1;
    for (let k = sorted.length - 1; k >= 0; k--) {
      const q = (sorted[k].p * sorted.length) / (k + 1);
      minQ = Math.min(q, minQ);
      qValues[sorted[k].i] = minQ;
    }

    return qValues;
  }
}

/**
 * Confidence interval calculator
 */
export class ConfidenceInterval {
  /**
   * Calculate confidence interval for mean (t-distribution)
   */
  static forMean(data: number[], confidenceLevel: number = 0.95): [number, number] {
    if (data.length < 2) {
      throw new Error('Need at least 2 data points');
    }

    const n = data.length;
    const mean = StatsUtils.mean(data);
    const std = StatsUtils.std(data);
    const sem = std / Math.sqrt(n);
    const df = n - 1;
    const alpha = 1 - confidenceLevel;

    const tCritical = Distributions.tCritical(alpha, df);
    const margin = tCritical * sem;

    return [mean - margin, mean + margin];
  }

  /**
   * Calculate confidence interval for proportion (Wilson score interval)
   */
  static forProportion(
    successes: number,
    trials: number,
    confidenceLevel: number = 0.95
  ): [number, number] {
    if (trials === 0) {
      throw new Error('Number of trials must be greater than 0');
    }

    const p = successes / trials;
    const z = Distributions.normalInverse(1 - (1 - confidenceLevel) / 2);
    const z2 = z * z;
    const denominator = 2 * (trials + z2);

    const center = (2 * trials * p + z2) / denominator;
    const margin = (z * Math.sqrt(z2 + 4 * trials * p * (1 - p))) / denominator;

    return [Math.max(0, center - margin), Math.min(1, center + margin)];
  }

  /**
   * Bootstrap confidence interval for any statistic
   */
  static bootstrap(
    data: number[],
    statistic: (data: number[]) => number,
    confidenceLevel: number = 0.95,
    iterations: number = 10000
  ): [number, number] {
    return Bootstrap.confidenceInterval(data, statistic, confidenceLevel, iterations);
  }

  /**
   * Calculate confidence interval for difference in means
   */
  static forMeanDifference(
    sample1: number[],
    sample2: number[],
    confidenceLevel: number = 0.95,
    paired: boolean = false
  ): [number, number] {
    if (paired) {
      if (sample1.length !== sample2.length) {
        throw new Error('Samples must have same length for paired CI');
      }

      const differences = sample1.map((val, i) => val - sample2[i]);
      return this.forMean(differences, confidenceLevel);
    }

    // Independent samples
    const n1 = sample1.length;
    const n2 = sample2.length;
    const mean1 = StatsUtils.mean(sample1);
    const mean2 = StatsUtils.mean(sample2);
    const var1 = StatsUtils.variance(sample1);
    const var2 = StatsUtils.variance(sample2);

    // Welch's t-test approach
    const meanDiff = mean1 - mean2;
    const seDiff = Math.sqrt(var1 / n1 + var2 / n2);

    // Welch-Satterthwaite degrees of freedom
    const df = Math.floor(
      (var1 / n1 + var2 / n2) ** 2 /
      (var1 ** 2 / (n1 ** 2 * (n1 - 1)) + var2 ** 2 / (n2 ** 2 * (n2 - 1)))
    );

    const alpha = 1 - confidenceLevel;
    const tCritical = Distributions.tCritical(alpha, df);
    const margin = tCritical * seDiff;

    return [meanDiff - margin, meanDiff + margin];
  }
}

/**
 * Normality test (Shapiro-Wilk approximation)
 */
export class NormalityTest {
  /**
   * Test if data is normally distributed using Shapiro-Wilk test
   * Note: This is an approximation suitable for large samples
   */
  static shapiroWilk(data: number[]): HypothesisTestResult {
    if (data.length < 3) {
      throw new Error('Need at least 3 data points for Shapiro-Wilk test');
    }

    const n = data.length;
    const sorted = [...data].sort((a, b) => a - b);

    // Calculate expected values of normal order statistics
    const m: number[] = [];
    for (let i = 1; i <= n; i++) {
      const p = (i - 0.375) / (n + 0.25);
      m.push(Distributions.normalInverse(p));
    }

    // Calculate weights
    const sumMSq = m.reduce((sum, val) => sum + val * val, 0);
    const c = Math.sqrt(sumMSq);

    // Calculate test statistic W
    const mean = StatsUtils.mean(data);
    const b = StatsUtils.sumProduct(
      sorted,
      m.map((mi) => mi / c)
    );
    const ss = sorted.reduce((sum, val) => sum + (val - mean) ** 2, 0);
    const W = (b * b) / ss;

    // Approximate p-value using transformation
    // This is a simplified approximation
    const logW = Math.log(W);
    const mu = -1.2725 + 1.3055 * Math.log(n) - 0.3642 * Math.log(n) ** 2;
    const sigma =
      1.0143 - 0.5777 * Math.log(n) - 0.2675 * Math.log(n) ** 2 + 0.0581 * Math.log(n) ** 3;
    const z = (logW - mu) / sigma;
    const pValue = 1 - Distributions.normalCDF(z);

    return {
      statistic: W,
      pValue,
      rejected: pValue < 0.05,
      alpha: 0.05,
      testName: "Shapiro-Wilk test",
      details: { n, normality: !pValue < 0.05 },
    };
  }
}
