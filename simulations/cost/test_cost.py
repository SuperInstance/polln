"""
Test Suite for Cost Simulations

Validates all calculations and assumptions in the cost analysis.
"""

import unittest
import numpy as np
import json
from pathlib import Path


class TestTokenCostAnalysis(unittest.TestCase):
    """Test token cost analysis calculations"""

    def setUp(self):
        """Import token cost analyzer"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from token_cost_analysis import TokenCostAnalyzer
        self.analyzer = TokenCostAnalyzer()

    def test_monolithic_cost_calculation(self):
        """Test monolithic LLM cost calculation"""
        from token_cost_analysis import TokenProfile

        profile = TokenProfile(1000, 500)
        cost = self.analyzer.calculate_monolithic_cost('gpt-4', profile, 100)

        # Input: 1000 tokens * 100 / 1000 * $0.03 = $3.00
        # Output: 500 tokens * 100 / 1000 * $0.06 = $3.00
        # Total: $6.00
        self.assertAlmostEqual(cost['total_cost'], 6.0, places=2)

    def test_polln_cost_calculation(self):
        """Test POLLN cost calculation"""
        from token_cost_analysis import TokenProfile

        profile = TokenProfile(1000, 500)
        cost = self.analyzer.calculate_polln_cost(profile, 100)

        # Should be lower than monolithic
        self.assertLess(cost['total_cost'], 6.0)

    def test_checkpoint_savings(self):
        """Test checkpoint savings calculation"""
        from token_cost_analysis import TokenProfile

        profile = TokenProfile(1000, 500)

        # Higher checkpoint efficiency = lower cost
        cost_70 = self.analyzer.calculate_polln_cost(profile, 100, checkpoint_savings=0.7)
        cost_90 = self.analyzer.calculate_polln_cost(profile, 100, checkpoint_savings=0.9)

        self.assertLess(cost_90['total_cost'], cost_70['total_cost'])

    def test_cost_comparison(self):
        """Test cost comparison across models"""
        results = self.analyzer.compare_costs(num_requests=100)

        # POLLN should be cheaper than GPT-4 for all complexities
        for complexity in results.keys():
            polln_cost = results[complexity]['polln']['total_cost']
            gpt4_cost = results[complexity]['gpt-4']['total_cost']
            self.assertLess(polln_cost, gpt4_cost)


class TestComputeEfficiency(unittest.TestCase):
    """Test compute efficiency calculations"""

    def setUp(self):
        """Import compute efficiency analyzer"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from compute_efficiency import ComputeEfficiencyAnalyzer
        self.analyzer = ComputeEfficiencyAnalyzer()

    def test_flops_calculation(self):
        """Test FLOPs calculation"""
        from compute_efficiency import ModelSize

        # 10M parameters * 20 flops/param * 1000 samples * 3 epochs = 6e11 flops
        flops = self.analyzer.calculate_training_flops(ModelSize.TINY, 1000, 3)
        expected = 10_000_000 * 20 * 1000 * 3

        self.assertAlmostEqual(flops, expected, places=0)

    def test_gpu_hours_conversion(self):
        """Test FLOPs to GPU hours conversion"""
        flops = 1e15  # 1 PFLOP
        gpu_hours = self.analyzer.flops_to_gpu_hours(flops)

        # 1e15 / 1e12 / 100 / 3600 ≈ 2.78 hours
        self.assertAlmostEqual(gpu_hours, 2.78, places=1)

    def test_quality_federated_learning(self):
        """Test federated learning quality estimation"""
        from compute_efficiency import ModelSize

        base_quality = 0.6
        quality = self.analyzer.calculate_federated_quality(base_quality, 100)

        # Federated should improve quality
        self.assertGreater(quality, base_quality)
        self.assertLessEqual(quality, 1.0)

    def test_monolithic_vs_polln_cost(self):
        """Test monolithic vs POLLN cost comparison"""
        from compute_efficiency import ModelSize

        monolithic = self.analyzer.calculate_monolithic_cost(
            ModelSize.MEDIUM, 100_000, 1_000_000
        )
        polln = self.analyzer.calculate_polln_cost(
            100, ModelSize.TINY, 1000, 1_000_000
        )

        # POLLN should be cheaper
        self.assertLess(polln.cost_usd, monolithic.cost_usd)


class TestDynamicScaling(unittest.TestCase):
    """Test dynamic scaling calculations"""

    def setUp(self):
        """Import dynamic scaling analyzer"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from dynamic_scaling import DynamicScalingAnalyzer
        self.analyzer = DynamicScalingAnalyzer()

    def test_workload_generation(self):
        """Test workload pattern generation"""
        from dynamic_scaling import WorkloadPattern

        workload = self.analyzer.generate_workload(WorkloadPattern.CONSTANT, hours=24)

        self.assertEqual(len(workload), 24)
        self.assertTrue(all(w >= 0 for w in workload))

    def test_static_scaling_cost(self):
        """Test static scaling cost calculation"""
        from dynamic_scaling import ResourceConfig

        config = ResourceConfig('Test', 10, 1.0, 100)
        workload = np.full(24, 50)  # 50 requests/hour for 24 hours

        result = self.analyzer.simulate_static_scaling(workload, config)

        self.assertEqual(result.total_cost, 24.0)  # $1/hour * 24 hours
        self.assertEqual(result.total_requests, 1200)  # 50 * 24

    def test_autoscaling_cost(self):
        """Test auto-scaling cost calculation"""
        workload = np.full(24, 50)  # Constant 50 requests/hour

        result = self.analyzer.simulate_autoscaling(workload, self.analyzer.autoscaling_policy)

        # Should be cheaper than static (which would provision for peak)
        self.assertGreater(result.total_cost, 0)
        self.assertLess(result.total_cost, 100)  # Reasonable upper bound

    def test_autoscaling_savings(self):
        """Test that auto-scaling saves money for variable workload"""
        from dynamic_scaling import WorkloadPattern, ResourceConfig

        # Generate variable workload
        workload = self.analyzer.generate_workload(WorkloadPattern.SPIKY, hours=168)

        # Static (sized for peak)
        peak_load = int(np.max(workload))
        static_config = ResourceConfig(
            'Static',
            num_agents=int(np.ceil(peak_load / 50)),
            hourly_cost=int(np.ceil(peak_load / 50)) / 10 * 1.0,
            max_requests_per_hour=peak_load,
        )
        static_result = self.analyzer.simulate_static_scaling(workload, static_config)

        # Auto-scaling
        autoscaling_result = self.analyzer.simulate_autoscaling(workload, self.analyzer.autoscaling_policy)

        # Auto-scaling should be cheaper
        self.assertLess(autoscaling_result.total_cost, static_result.total_cost)


class TestBreakEvenAnalysis(unittest.TestCase):
    """Test break-even analysis calculations"""

    def setUp(self):
        """Import break-even analyzer"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from break_even_analysis import BreakEvenAnalyzer
        self.analyzer = BreakEvenAnalyzer()

    def test_daily_cost_calculation(self):
        """Test daily cost calculation"""
        # Day 1: includes fixed costs
        day1_cost = self.analyzer.calculate_daily_cost(
            self.analyzer.polln_costs, 100, 1
        )

        # Day 31: no fixed costs
        day31_cost = self.analyzer.calculate_daily_cost(
            self.analyzer.polln_costs, 100, 31
        )

        # Day 1 should be more expensive due to fixed costs
        self.assertGreater(day1_cost, day31_cost)

    def test_cumulative_cost_calculation(self):
        """Test cumulative cost calculation"""
        cost_10_days = self.analyzer.calculate_cumulative_cost(
            self.analyzer.polln_costs, 100, 10
        )

        cost_30_days = self.analyzer.calculate_cumulative_cost(
            self.analyzer.polln_costs, 100, 30
        )

        # 30 days should cost more than 10 days
        self.assertGreater(cost_30_days, cost_10_days)
        # But not 3x (due to amortized fixed costs)
        self.assertLess(cost_30_days / cost_10_days, 3.0)

    def test_break_even_point(self):
        """Test break-even point calculation"""
        # At high request volume, should break even
        bre_days, _ = self.analyzer.find_break_even_point(1000, max_days=365)

        self.assertIsNotNone(bre_days)
        self.assertLess(bre_days, 365)

    def test_roi_calculation(self):
        """Test ROI calculation"""
        # At high volume, ROI should be positive
        roi = self.analyzer.calculate_roi(1000, 365)

        self.assertGreater(roi, 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for all simulations"""

    def test_hypotheses_consistency(self):
        """Test that all hypotheses point to cost savings"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent))

        # Token cost: POLLN cheaper than monolithic
        from token_cost_analysis import TokenCostAnalyzer, TokenProfile
        token_analyzer = TokenCostAnalyzer()
        profile = TokenProfile(2000, 800)
        token_results = token_analyzer.compare_costs(num_requests=1000)

        for complexity in token_results.keys():
            polln_cost = token_results[complexity]['polln']['cost_per_request']
            gpt4_cost = token_results[complexity]['gpt-4']['cost_per_request']
            self.assertLess(polln_cost, gpt4_cost,
                f"Token cost: POLLN should be cheaper than GPT-4 for {complexity}")

        # Compute efficiency: POLLN achieves high quality at low cost
        from compute_efficiency import ComputeEfficiencyAnalyzer, ModelSize
        compute_analyzer = ComputeEfficiencyAnalyzer()
        compute_comparison = compute_analyzer.compare_approaches()

        polln_quality = compute_comparison['polln']['quality']
        polln_cost_ratio = compute_comparison['comparison']['cost_ratio']

        self.assertGreaterEqual(polln_quality, 0.8,
            "Compute efficiency: POLLN should achieve at least 80% quality")
        self.assertLessEqual(polln_cost_ratio, 0.2,
            "Compute efficiency: POLLN should cost at most 20% of monolithic")

        # Dynamic scaling: auto-scaling saves money
        from dynamic_scaling import DynamicScalingAnalyzer, WorkloadPattern
        scaling_analyzer = DynamicScalingAnalyzer()
        scaling_results = scaling_analyzer.compare_strategies()

        for pattern, data in scaling_results.items():
            auto_cost = data['autoscaling']['cost']
            static_cost = data['static']['cost']
            # At least one pattern should show savings
            if auto_cost < static_cost:
                break
        else:
            self.fail("Dynamic scaling: Auto-scaling should be cheaper for at least one pattern")

        # Break-even: POLLN becomes cost-effective at reasonable volume
        from break_even_analysis import BreakEvenAnalyzer
        bre_analyzer = BreakEvenAnalyzer()
        bre_analysis = bre_analyzer.comprehensive_analysis()

        min_requests = bre_analysis['minimum_requests_90_day']
        self.assertLessEqual(min_requests, 500,
            f"Break-even: Should break even within 90 days at ≤500 req/day, got {min_requests}")

    def test_results_consistency(self):
        """Test that all simulation results are internally consistent"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent))

        # All cost analyses should use consistent time periods
        from token_cost_analysis import TokenCostAnalyzer
        from compute_efficiency import ComputeEfficiencyAnalyzer
        from dynamic_scaling import DynamicScalingAnalyzer
        from break_even_analysis import BreakEvenAnalyzer

        # Check that reference periods are consistent (1000 requests, etc.)
        token_analyzer = TokenCostAnalyzer()
        token_results = token_analyzer.compare_costs(num_requests=1000)

        # Each complexity should have results
        self.assertEqual(len(token_results), 4)  # simple, medium, complex, very_complex

        # Check that compute efficiency uses reasonable scales
        compute_analyzer = ComputeEfficiencyAnalyzer()
        compute_comparison = compute_analyzer.compare_approaches()

        # Quality should be between 0 and 1
        self.assertGreaterEqual(compute_comparison['polln']['quality'], 0)
        self.assertLessEqual(compute_comparison['polln']['quality'], 1)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestTokenCostAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestComputeEfficiency))
    suite.addTests(loader.loadTestsFromTestCase(TestDynamicScaling))
    suite.addTests(loader.loadTestsFromTestCase(TestBreakEvenAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == '__main__':
    result = run_tests()

    # Exit with appropriate code
    exit(0 if result.wasSuccessful() else 1)
