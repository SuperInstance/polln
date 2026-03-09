"""
Test Suite for LoRA Composition Validation Simulations

Ensures all modules work correctly and produce valid results
"""

import pytest
import torch
import numpy as np
from pathlib import Path
import tempfile
import json


class TestRankAnalysis:
    """Test rank sufficiency analysis module"""

    def test_synthetic_model_generation(self):
        """Test that synthetic models are generated correctly"""
        from rank_analysis import SyntheticModelGenerator

        gen = SyntheticModelGenerator(base_dim=512, seed=42)
        W_base = gen.generate_base_model()

        assert W_base.shape == (512, 512)
        assert torch.is_tensor(W_base)

        # Generate expert models
        W_expert = gen.generate_expert_weights(W_base, "code", expertise_strength=0.3)
        assert W_expert.shape == (512, 512)

        # Check that they're different
        assert not torch.allclose(W_base, W_expert)

    def test_lora_decomposition(self):
        """Test LoRA decomposition"""
        from rank_analysis import LoRADecomposer

        decomposer = LoRADecomposer(rank=32)

        # Create test matrices
        W_base = torch.randn(512, 512) * 0.02
        W_expert = W_base + torch.randn(512, 512) * 0.01

        # Decompose
        B, A = decomposer.decompose(W_base, W_expert, method="svd")

        assert B.shape == (512, 32)
        assert A.shape == (32, 512)

        # Reconstruct
        delta_W_reconstructed = decomposer.reconstruct(B, A)
        assert delta_W_reconstructed.shape == (512, 512)

    def test_rank_analyzer_initialization(self):
        """Test analyzer initialization"""
        from rank_analysis import RankSufficiencyAnalyzer

        analyzer = RankSufficiencyAnalyzer(
            base_dim=256,
            max_rank=64,
            domains=["code", "writing"]
        )

        assert analyzer.base_dim == 256
        assert analyzer.max_rank == 64
        assert analyzer.domains == ["code", "writing"]

    def test_domain_analysis(self):
        """Test analysis of a single domain"""
        from rank_analysis import RankSufficiencyAnalyzer

        analyzer = RankSufficiencyAnalyzer(base_dim=256, max_rank=32)
        results = analyzer.analyze_domain("code", ranks=[8, 16, 32])

        assert len(results) == 3
        assert results[0].rank == 8
        assert results[0].reconstruction_error > 0
        assert 0 <= results[0].explained_variance <= 1

    def test_find_sufficient_rank(self):
        """Test finding minimum sufficient rank"""
        from rank_analysis import RankSufficiencyAnalyzer

        analyzer = RankSufficiencyAnalyzer(base_dim=256, max_rank=32)
        analyzer.analyze_domain("code", ranks=[8, 16, 32])

        r_95 = analyzer.find_sufficient_rank("code", threshold=0.95)
        assert 8 <= r_95 <= 32


class TestInterferenceDetection:
    """Test interference detection module"""

    def test_lora_pair_creation(self):
        """Test LoRA pair creation"""
        from interference import LoRAPair

        B1 = torch.randn(512, 32)
        A1 = torch.randn(32, 512)
        B2 = torch.randn(512, 32)
        A2 = torch.randn(32, 512)

        pair = LoRAPair(B1, A1, B2, A2, "lora1", "lora2")

        assert pair.name1 == "lora1"
        assert pair.name2 == "lora2"
        assert pair.rank1 == 32
        assert pair.rank2 == 32

    def test_delta_W_computation(self):
        """Test delta_W computation"""
        from interference import LoRAPair

        B1 = torch.randn(256, 16)
        A1 = torch.randn(16, 256)
        B2 = torch.randn(256, 16)
        A2 = torch.randn(16, 256)

        pair = LoRAPair(B1, A1, B2, A2)

        delta1 = pair.delta_W1
        delta2 = pair.delta_W2

        assert delta1.shape == (256, 256)
        assert delta2.shape == (256, 256)

    def test_weight_correlation(self):
        """Test weight correlation calculation"""
        from interference import InterferenceCalculator, LoRAPair

        B1 = torch.randn(256, 16)
        A1 = torch.randn(16, 256)
        B2 = torch.randn(256, 16)
        A2 = torch.randn(16, 256)

        pair = LoRAPair(B1, A1, B2, A2)
        calc = InterferenceCalculator()

        corr = calc.weight_correlation(pair)
        assert -1 <= corr <= 1

    def test_subspace_overlap(self):
        """Test subspace overlap calculation"""
        from interference import InterferenceCalculator, LoRAPair

        B1 = torch.randn(256, 16)
        A1 = torch.randn(16, 256)
        B2 = torch.randn(256, 16)
        A2 = torch.randn(16, 256)

        pair = LoRAPair(B1, A1, B2, A2)
        calc = InterferenceCalculator()

        overlap = calc.subspace_overlap(pair, method="principal")
        assert 0 <= overlap <= 1


class TestCompositionOptimization:
    """Test composition optimization module"""

    def test_uniform_strategy(self):
        """Test uniform weighting strategy"""
        from composition import CompositionStrategy

        strategy = CompositionStrategy()
        weights = strategy.uniform(5)

        assert len(weights) == 5
        assert np.allclose(weights.sum(), 1.0)
        assert np.allclose(weights, 0.2)

    def test_inverse_sqrt_strategy(self):
        """Test inverse square root strategy"""
        from composition import CompositionStrategy

        strategy = CompositionStrategy()
        weights = strategy.inverse_sqrt(4)

        assert len(weights) == 4
        assert np.allclose(weights, 1.0 / 2.0)  # 1/√4 = 1/2

    def test_rank_weighted_strategy(self):
        """Test rank-weighted strategy"""
        from composition import CompositionStrategy
        import torch

        strategy = CompositionStrategy()

        loras = [
            (torch.randn(256, 16), torch.randn(16, 256)),
            (torch.randn(256, 32), torch.randn(32, 256)),
        ]

        weights = strategy.rank_weighted(loras)

        assert len(weights) == 2
        assert np.allclose(weights.sum(), 1.0)
        assert weights[1] > weights[0]  # Higher rank = higher weight

    def test_norm_weighted_strategy(self):
        """Test norm-weighted strategy"""
        from composition import CompositionStrategy
        import torch

        strategy = CompositionStrategy()

        # Create LoRAs with different norms
        loras = [
            (torch.randn(256, 16) * 0.1, torch.randn(16, 256) * 0.1),
            (torch.randn(256, 16) * 1.0, torch.randn(16, 256) * 1.0),
        ]

        weights = strategy.norm_weighted(loras)

        assert len(weights) == 2
        assert np.allclose(weights.sum(), 1.0)
        assert weights[1] > weights[0]  # Larger norm = higher weight

    def test_composition_optimizer(self):
        """Test composition optimizer"""
        from composition import CompositionOptimizer

        optimizer = CompositionOptimizer(base_dim=256, lambda_reg=0.01)

        # Generate scenario
        W_target, W_base, loras = optimizer.generate_composition_scenario(
            n_loras=3, ranks=[8, 16, 32]
        )

        assert W_target.shape == (256, 256)
        assert W_base.shape == (256, 256)
        assert len(loras) == 3


class TestScalingLaws:
    """Test scaling laws module"""

    def test_parameter_counting(self):
        """Test parameter counting"""
        from scaling_laws import ScalingLawDataGenerator

        gen = ScalingLawDataGenerator()

        n_params = gen.count_parameters(base_dim=512, n_loras=5, rank=32)

        expected = 512**2 + 5 * 2 * 32 * 512
        assert n_params == expected

    def test_scenario_generation(self):
        """Test scenario generation"""
        from scaling_laws import ScalingLawDataGenerator

        gen = ScalingLawDataGenerator()
        scenario = gen.generate_scenario(
            base_dim=512, n_loras=3, rank=32, interference_level=0.1
        )

        assert "base_dim" in scenario
        assert "n_loras" in scenario
        assert "n_params" in scenario
        assert "accuracy" in scenario
        assert 0 <= scenario["accuracy"] <= 1

    def test_dataset_generation(self):
        """Test dataset generation"""
        from scaling_laws import ScalingLawDataGenerator

        gen = ScalingLawDataGenerator()
        data = gen.generate_dataset(n_scenarios=100)

        assert len(data) == 100
        assert all("accuracy" in d for d in data)

    def test_scaling_law_fitting(self):
        """Test scaling law fitting"""
        from scaling_laws import ScalingLawAnalyzer

        analyzer = ScalingLawAnalyzer()
        gen = analyzer.data_generator

        # Generate training data
        data = gen.generate_dataset(n_scenarios=500)

        # Fit scaling law
        coefficients = analyzer.fit_scaling_law(data)

        assert hasattr(coefficients, "a")
        assert hasattr(coefficients, "b")
        assert hasattr(coefficients, "c")
        assert hasattr(coefficients, "d")

    def test_accuracy_prediction(self):
        """Test accuracy prediction"""
        from scaling_laws import ScalingLawAnalyzer

        analyzer = ScalingLawAnalyzer()
        gen = analyzer.data_generator

        # Generate and fit
        data = gen.generate_dataset(n_scenarios=200)
        analyzer.fit_scaling_law(data)

        # Make prediction
        accuracy = analyzer.predict_accuracy(
            n_params=1e7, n_loras=5, interference=0.5
        )

        assert 0 <= accuracy <= 1


class TestIntegration:
    """Integration tests for the full suite"""

    def test_full_rank_analysis_workflow(self):
        """Test complete rank analysis workflow"""
        from rank_analysis import RankSufficiencyAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = RankSufficiencyAnalyzer(
                base_dim=256, max_rank=32, domains=["code"]
            )

            results = analyzer.run_full_analysis(Path(tmpdir))

            assert "sufficient_ranks" in results
            assert "phase_diagram" in results
            assert "spectral_data" in results

            # Check files were created
            assert (Path(tmpdir) / "rank_analysis_results.json").exists()
            assert (Path(tmpdir) / "phase_diagram.png").exists()

    def test_full_interference_workflow(self):
        """Test complete interference detection workflow"""
        from interference import InterferenceDetector

        with tempfile.TemporaryDirectory() as tmpdir:
            detector = InterferenceDetector(
                base_dim=256, ranks=[16, 32], domains=["code", "writing"]
            )

            results = detector.run_full_analysis(Path(tmpdir))

            assert "clusters" in results
            assert "feature_importance" in results
            assert "metrics_summary" in results

            # Check files
            assert (Path(tmpdir) / "interference_results.json").exists()
            assert (Path(tmpdir) / "interference_matrix.png").exists()

    def test_full_composition_workflow(self):
        """Test complete composition optimization workflow"""
        from composition import CompositionOptimizer

        with tempfile.TemporaryDirectory() as tmpdir:
            optimizer = CompositionOptimizer(base_dim=256, lambda_reg=0.01)

            # Quick test with fewer scenarios
            results = optimizer.compare_strategies(n_scenarios=5, n_loras_range=(2, 4))

            assert "uniform" in results
            assert "inverse_sqrt" in results
            assert "learned" in results

            # Check that results are valid
            for strategy_results in results.values():
                assert len(strategy_results) == 5

    def test_full_scaling_laws_workflow(self):
        """Test complete scaling laws workflow"""
        from scaling_laws import ScalingLawAnalyzer

        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = ScalingLawAnalyzer()

            results = analyzer.run_full_analysis(Path(tmpdir))

            assert "coefficients" in results
            assert "break_even_curves" in results
            assert "optimal_configurations" in results

            # Check files
            assert (Path(tmpdir) / "scaling_law_results.json").exists()
            assert (Path(tmpdir) / "break_even_curves.png").exists()


class TestExamples:
    """Test the example scripts"""

    def test_example_1_runs(self):
        """Test that example 1 runs without errors"""
        import subprocess
        result = subprocess.run(
            ["python", "-c", "from example_usage import example_1_rank_sufficiency; example_1_rank_sufficiency()"],
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0

    def test_example_2_runs(self):
        """Test that example 2 runs without errors"""
        import subprocess
        result = subprocess.run(
            ["python", "-c", "from example_usage import example_2_interference_detection; example_2_interference_detection()"],
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0


def test_all_imports_work():
    """Test that all imports work correctly"""
    from rank_analysis import (
        RankSufficiencyAnalyzer,
        SyntheticModelGenerator,
        LoRADecomposer
    )

    from interference import (
        InterferenceDetector,
        InterferenceCalculator,
        InterferencePredictor,
        LoRAPair
    )

    from composition import (
        CompositionOptimizer,
        CompositionStrategy
    )

    from scaling_laws import (
        ScalingLawAnalyzer,
        ScalingLawDataGenerator
    )


def test_pytorch_tensors():
    """Test that PyTorch tensors work correctly"""
    # Basic tensor operations
    x = torch.randn(100, 256)
    y = torch.randn(256, 256)

    result = x @ y
    assert result.shape == (100, 256)

    # SVD
    U, S, V = torch.linalg.svd(y)
    assert len(S) == 256

    # Gradient computation
    w = torch.randn(256, 256, requires_grad=True)
    loss = torch.norm(w @ x)**2
    loss.backward()
    assert w.grad is not None


if __name__ == "__main__":
    # Run tests
    print("Running LoRA Composition Validation Tests")
    print("=" * 70)

    # Basic imports
    print("\n✓ Testing imports...")
    test_all_imports_work()

    # PyTorch
    print("\n✓ Testing PyTorch...")
    test_pytorch_tensors()

    # Rank analysis
    print("\n✓ Testing rank analysis...")
    test_synthetic_model_generation()
    test_lora_decomposition()
    test_rank_analyzer_initialization()
    test_domain_analysis()
    test_find_sufficient_rank()

    # Interference
    print("\n✓ Testing interference detection...")
    test_lora_pair_creation()
    test_delta_W_computation()
    test_weight_correlation()
    test_subspace_overlap()

    # Composition
    print("\n✓ Testing composition optimization...")
    test_uniform_strategy()
    test_inverse_sqrt_strategy()
    test_rank_weighted_strategy()
    test_norm_weighted_strategy()
    test_composition_optimizer()

    # Scaling laws
    print("\n✓ Testing scaling laws...")
    test_parameter_counting()
    test_scenario_generation()
    test_dataset_generation()
    test_scaling_law_fitting()
    test_accuracy_prediction()

    print("\n" + "=" * 70)
    print("All tests passed!")
    print("=" * 70)
