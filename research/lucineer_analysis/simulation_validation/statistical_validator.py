#!/usr/bin/env python3
"""
Lucineer Simulation Validation Suite - Statistical Validator
Statistical analysis framework for validation results

Author: Simulation & Validation Expert Team
Version: 1.0
Date: 2026-03-13
"""

import numpy as np
import scipy.stats
from dataclasses import dataclass
from typing import Tuple, Optional, List
import json


@dataclass
class StatisticalResult:
    """Result of statistical validation"""
    claim_value: float
    measured_mean: float
    measured_std: float
    sample_size: int
    p_value: float
    claim_validated: bool
    confidence_interval: Tuple[float, float]
    effect_size: float
    is_normal: bool
    test_used: str

    def to_dict(self) -> dict:
        return {
            'claim_value': self.claim_value,
            'measured_mean': self.measured_mean,
            'measured_std': self.measured_std,
            'sample_size': self.sample_size,
            'p_value': self.p_value,
            'claim_validated': self.claim_validated,
            'confidence_interval': self.confidence_interval,
            'effect_size': self.effect_size,
            'is_normal': self.is_normal,
            'test_used': self.test_used,
        }


class StatisticalValidator:
    """
    Statistical validation framework

    Methods:
    1. Hypothesis testing
    2. Confidence intervals
    3. Effect size
    4. Power analysis
    5. Sample size calculation
    """

    def __init__(self, alpha: float = 0.05, power: float = 0.95):
        self.alpha = alpha
        self.power = power

    def validate_claim(self,
                      claim_value: float,
                      measured_data: np.ndarray,
                      comparison_type: str = 'greater_than') -> StatisticalResult:
        """
        Validate claim using statistical testing

        Args:
            claim_value: Target value from claim
            measured_data: Array of measurements
            comparison_type: 'greater_than', 'less_than', 'equal'
        """
        # Descriptive statistics
        n = len(measured_data)
        mean = np.mean(measured_data)
        std = np.std(measured_data, ddof=1)
        sem = std / np.sqrt(n)

        # Check normality
        _, p_normality = scipy.stats.shapiro(measured_data)
        is_normal = p_normality > self.alpha

        # Choose appropriate test
        if comparison_type == 'greater_than':
            # H0: mean <= claim_value
            # H1: mean > claim_value

            if is_normal and n >= 30:
                # One-sample t-test
                t_stat, p_value = scipy.stats.ttest_1samp(
                    measured_data,
                    claim_value,
                    alternative='greater'
                )
                test_used = 'one_sample_t_test'
            else:
                # Wilcoxon signed-rank test
                stat, p_value = scipy.stats.wilcoxon(
                    measured_data - claim_value,
                    alternative='greater'
                )
                test_used = 'wilcoxon_signed_rank'

        elif comparison_type == 'less_than':
            # H0: mean >= claim_value
            # H1: mean < claim_value

            if is_normal and n >= 30:
                t_stat, p_value = scipy.stats.ttest_1samp(
                    measured_data,
                    claim_value,
                    alternative='less'
                )
                test_used = 'one_sample_t_test'
            else:
                stat, p_value = scipy.stats.wilcoxon(
                    measured_data - claim_value,
                    alternative='less'
                )
                test_used = 'wilcoxon_signed_rank'

        elif comparison_type == 'equal':
            # H0: mean != claim_value
            # H1: mean == claim_value

            if is_normal and n >= 30:
                t_stat, p_value = scipy.stats.ttest_1samp(
                    measured_data,
                    claim_value,
                    alternative='two-sided'
                )
                test_used = 'one_sample_t_test'
            else:
                stat, p_value = scipy.stats.wilcoxon(
                    measured_data - claim_value,
                    alternative='two-sided'
                )
                test_used = 'wilcoxon_signed_rank'

        else:
            raise ValueError(f"Unknown comparison type: {comparison_type}")

        # Confidence interval
        ci_low, ci_high = self._calculate_ci(
            measured_data,
            confidence=1 - self.alpha
        )

        # Effect size (Cohen's d)
        effect_size = (mean - claim_value) / std

        # Validation result
        claim_validated = p_value < self.alpha

        return StatisticalResult(
            claim_value=claim_value,
            measured_mean=mean,
            measured_std=std,
            sample_size=n,
            p_value=p_value,
            claim_validated=claim_validated,
            confidence_interval=(ci_low, ci_high),
            effect_size=effect_size,
            is_normal=is_normal,
            test_used=test_used,
        )

    def _calculate_ci(self,
                     data: np.ndarray,
                     confidence: float = 0.95) -> Tuple[float, float]:
        """Calculate confidence interval"""
        n = len(data)
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        sem = std / np.sqrt(n)

        # Use t-distribution
        t_critical = scipy.stats.t.ppf(
            (1 + confidence) / 2,
            df=n - 1
        )

        ci_low = mean - t_critical * sem
        ci_high = mean + t_critical * sem

        return ci_low, ci_high

    def calculate_sample_size(self,
                             effect_size: float,
                             alpha: float = None,
                             power: float = None) -> int:
        """
        Calculate required sample size using power analysis

        Args:
            effect_size: Cohen's d (target effect size)
            alpha: Significance level (default from init)
            power: Statistical power (default from init)
        """
        alpha = alpha or self.alpha
        power = power or self.power

        # Power analysis for t-test
        from scipy.stats import norm

        z_alpha = norm.ppf(1 - alpha)
        z_beta = norm.ppf(power)

        # Sample size formula for two-sided test
        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2

        return int(np.ceil(n))

    def bootstrap_confidence_interval(self,
                                     data: np.ndarray,
                                     n_bootstrap: int = 10000,
                                     confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calculate bootstrap confidence interval

        Args:
            data: Sample data
            n_bootstrap: Number of bootstrap samples
            confidence: Confidence level
        """
        bootstrap_means = []

        for _ in range(n_bootstrap):
            sample = np.random.choice(data, size=len(data), replace=True)
            bootstrap_means.append(np.mean(sample))

        alpha = 1 - confidence
        ci_low = np.percentile(bootstrap_means, 100 * alpha / 2)
        ci_high = np.percentile(bootstrap_means, 100 * (1 - alpha / 2))

        return ci_low, ci_high

    def compare_distributions(self,
                             data1: np.ndarray,
                             data2: np.ndarray) -> dict:
        """
        Compare two distributions

        Tests:
        1. Mann-Whitney U test (non-parametric)
        2. Kolmogorov-Smirnov test
        3. Effect size (Cliff's delta)
        """
        # Mann-Whitney U test
        u_stat, p_mw = scipy.stats.mannwhitneyu(data1, data2, alternative='two-sided')

        # Kolmogorov-Smirnov test
        ks_stat, p_ks = scipy.stats.ks_2samp(data1, data2)

        # Cliff's delta (effect size for non-parametric)
        def cliffs_delta(x1, x2):
            n1 = len(x1)
            n2 = len(x2)

            greater = sum(1 for i in x1 for j in x2 if i > j)
            less = sum(1 for i in x1 for j in x2 if i < j)

            delta = (greater - less) / (n1 * n2)
            return delta

        delta = cliffs_delta(data1, data2)

        # Interpret effect size
        if abs(delta) < 0.147:
            effect_interpretation = "negligible"
        elif abs(delta) < 0.33:
            effect_interpretation = "small"
        elif abs(delta) < 0.474:
            effect_interpretation = "medium"
        else:
            effect_interpretation = "large"

        return {
            'mann_whitney_u': u_stat,
            'mann_whitney_p': p_mw,
            'ks_statistic': ks_stat,
            'ks_p_value': p_ks,
            'cliffs_delta': delta,
            'effect_interpretation': effect_interpretation,
        }

    def power_analysis(self,
                      effect_size: float,
                      sample_size: int,
                      alpha: float = None) -> float:
        """
        Calculate statistical power

        Args:
            effect_size: Cohen's d
            sample_size: Sample size per group
            alpha: Significance level

        Returns:
            Statistical power (0-1)
        """
        alpha = alpha or self.alpha

        # Use power analysis from statsmodels if available
        try:
            from statsmodels.stats.power import tt_solve_power
            power = tt_solve_power(
                effect_size=effect_size,
                nobs1=sample_size,
                alpha=alpha,
                alternative='two-sided'
            )
            return power
        except ImportError:
            # Approximation
            from scipy.stats import norm
            z_alpha = norm.ppf(1 - alpha / 2)
            z_beta = effect_size * np.sqrt(sample_size / 2) - z_alpha
            power = scipy.stats.norm.cdf(z_beta)
            return power

    def anova_test(self, *groups: np.ndarray) -> dict:
        """
        One-way ANOVA test for comparing multiple groups

        Args:
            *groups: Variable number of group arrays

        Returns:
            Dictionary with test results
        """
        # Check normality for each group
        normality_results = []
        for i, group in enumerate(groups):
            _, p_norm = scipy.stats.shapiro(group)
            normality_results.append({
                'group': i,
                'is_normal': p_norm > self.alpha,
                'p_value': p_norm
            })

        # Check homogeneity of variances (Levene's test)
        _, p_levene = scipy.stats.levene(*groups)

        # ANOVA
        f_stat, p_anova = scipy.stats.f_oneway(*groups)

        # Effect size (eta-squared)
        all_data = np.concatenate(groups)
        grand_mean = np.mean(all_data)

        ss_between = sum(len(group) * (np.mean(group) - grand_mean) ** 2
                        for group in groups)
        ss_total = sum((x - grand_mean) ** 2 for x in all_data)

        eta_squared = ss_between / ss_total

        return {
            'f_statistic': f_stat,
            'p_value': p_anova,
            'eta_squared': eta_squared,
            'levene_p_value': p_levene,
            'homogeneous_variances': p_levene > self.alpha,
            'normality_results': normality_results,
        }


if __name__ == '__main__':
    # Example usage
    validator = StatisticalValidator(alpha=0.05, power=0.95)

    # Example 1: Validate throughput claim
    print("Example 1: Throughput Validation")
    print("-" * 50)

    # Simulate measurements
    np.random.seed(42)
    measured_throughput = np.random.normal(loc=95, scale=10, size=30)

    result = validator.validate_claim(
        claim_value=80,
        measured_data=measured_throughput,
        comparison_type='greater_than'
    )

    print(f"Claim: Throughput > 80 tok/s")
    print(f"Measured mean: {result.measured_mean:.2f} tok/s")
    print(f"Measured std: {result.measured_std:.2f} tok/s")
    print(f"P-value: {result.p_value:.6f}")
    print(f"95% CI: [{result.confidence_interval[0]:.2f}, {result.confidence_interval[1]:.2f}]")
    print(f"Effect size: {result.effect_size:.3f}")
    print(f"Validated: {result.claim_validated}")
    print()

    # Example 2: Sample size calculation
    print("Example 2: Sample Size Calculation")
    print("-" * 50)

    required_n = validator.calculate_sample_size(
        effect_size=0.8,  # Large effect
        alpha=0.05,
        power=0.95
    )

    print(f"For effect size d=0.8, α=0.05, power=0.95:")
    print(f"Required sample size: n={required_n}")
    print()

    # Example 3: Compare two distributions
    print("Example 3: Distribution Comparison")
    print("-" * 50)

    traditional = np.random.normal(loc=0.37, scale=0.05, size=30)
    mask_locked = np.random.normal(loc=0.02, scale=0.005, size=30)

    comparison = validator.compare_distributions(traditional, mask_locked)

    print(f"Traditional: mean={np.mean(traditional):.4f}, std={np.std(traditional):.4f}")
    print(f"Mask-locked: mean={np.mean(mask_locked):.4f}, std={np.std(mask_locked):.4f}")
    print(f"Mann-Whitney U p-value: {comparison['mann_whitney_p']:.6e}")
    print(f"Cliff's delta: {comparison['cliffs_delta']:.3f} ({comparison['effect_interpretation']})")
    print()

    # Example 4: Bootstrap CI
    print("Example 4: Bootstrap Confidence Interval")
    print("-" * 50)

    ci_low, ci_high = validator.bootstrap_confidence_interval(
        measured_throughput,
        n_bootstrap=10000,
        confidence=0.95
    )

    print(f"Bootstrap 95% CI: [{ci_low:.2f}, {ci_high:.2f}]")
    print(f"Parametric 95% CI: [{result.confidence_interval[0]:.2f}, {result.confidence_interval[1]:.2f}]")
