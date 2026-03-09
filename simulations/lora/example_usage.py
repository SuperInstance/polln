"""
Quick Start Examples for LoRA Composition Validation

This script demonstrates how to use each module individually
"""

from pathlib import Path
import numpy as np
import torch
import matplotlib.pyplot as plt


def example_1_rank_sufficiency():
    """
    Example 1: Rank Sufficiency Analysis

    Demonstrates finding the minimum rank needed to capture expertise
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Rank Sufficiency Analysis")
    print("=" * 70)

    from rank_analysis import RankSufficiencyAnalyzer

    # Create analyzer
    analyzer = RankSufficiencyAnalyzer(
        base_dim=512,  # Smaller for quick demo
        max_rank=64,
        domains=["code", "writing"]
    )

    # Analyze code domain
    print("\nAnalyzing code domain...")
    results = analyzer.analyze_domain(
        "code",
        ranks=[8, 16, 32, 48, 64],
        expertise_strength=0.3
    )

    print("\nResults:")
    print(f"{'Rank':<10} {'Error':<15} {'Variance':<15} {'Compression':<15}")
    print("-" * 60)
    for r in results:
        print(f"{r.rank:<10} {r.reconstruction_error:<15.4f} "
              f"{r.explained_variance:<15.4f} {r.compression_ratio:<15.1f}x")

    # Find sufficient rank
    r_95 = analyzer.find_sufficient_rank("code", threshold=0.95)
    print(f"\nMinimum rank for 95% variance: {r_95}")

    # Test hypothesis H1
    print("\n" + "-" * 60)
    print("HYPOTHESIS H1: Is r≈64 sufficient?")
    h1_results = analyzer.test_hypothesis_h1()
    for domain, results in h1_results.items():
        print(f"  {domain}: r_95={results['r_95']}, H1 holds: {results['h1_holds']}")

    return analyzer


def example_2_interference_detection():
    """
    Example 2: Interference Detection

    Demonstrates predicting interference between LoRA pairs
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Interference Detection")
    print("=" * 70)

    from interference import InterferenceDetector, LoRAPair
    import torch

    # Create detector
    detector = InterferenceDetector(
        base_dim=512,
        ranks=[16, 32],
        domains=["code", "writing"]
    )

    # Generate a few pairs
    print("\nGenerating LoRA pairs...")
    detector.generate_lora_pairs(n_pairs_per_combination=2)
    print(f"Generated {len(detector.pairs)} pairs")

    # Compute metrics for first pair
    print("\nAnalyzing first pair...")
    pair = detector.pairs[0]
    print(f"  Pair: {pair.name1} + {pair.name2}")
    print(f"  Ranks: {pair.rank1} and {pair.rank2}")

    # Compute interference metrics
    from interference import InterferenceCalculator
    calc = InterferenceCalculator()

    weight_corr = calc.weight_correlation(pair)
    subspace_over = calc.subspace_overlap(pair)

    print(f"\nInterference Metrics:")
    print(f"  Weight correlation: {weight_corr:.4f}")
    print(f"  Subspace overlap: {subspace_over:.4f}")

    # Prediction based on metrics
    if subspace_over < 0.3:
        print(f"  → Compatible (low interference)")
    elif subspace_over < 0.6:
        print(f"  → Moderate interference")
    else:
        print(f"  → Incompatible (high interference)")

    return detector


def example_3_composition_optimization():
    """
    Example 3: Composition Optimization

    Demonstrates finding optimal weights for combining LoRAs
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Composition Optimization")
    print("=" * 70)

    from composition import CompositionOptimizer

    # Create optimizer
    optimizer = CompositionOptimizer(
        base_dim=512,
        lambda_reg=0.01
    )

    # Generate a composition scenario
    print("\nGenerating composition scenario (3 LoRAs)...")
    W_target, W_base, loras = optimizer.generate_composition_scenario(
        n_loras=3,
        ranks=[16, 32, 48]
    )

    print(f"  Base dim: {W_base.shape[0]}")
    print(f"  LoRAs: {len(loras)}")
    for i, (B, A) in enumerate(loras):
        print(f"    LoRA {i+1}: rank={A.shape[0]}, "
              f"params={B.numel() + A.numel()}")

    # Compare strategies
    from composition import CompositionStrategy
    strategy = CompositionStrategy()

    print("\nComparing composition strategies:")
    print(f"{'Strategy':<20} {'Reconstruction Error':<25} {'Performance':<15}")
    print("-" * 65)

    # Generate test data
    X_test = torch.randn(100, 512)
    y_test = X_test @ W_target.T + torch.randn(100, 512) * 0.1

    strategies = {
        "Uniform": strategy.uniform(len(loras)),
        "1/√N": strategy.inverse_sqrt(len(loras)),
        "Rank-weighted": strategy.rank_weighted(loras),
    }

    for strat_name, weights in strategies.items():
        result = optimizer.evaluate_composition(
            weights, loras, W_target, W_base, X_test, y_test
        )
        print(f"{strat_name:<20} {result.reconstruction_error:<25.4f} "
              f"{result.performance:<15.4f}")

    # Analyze linearity
    print("\nAnalyzing composition linearity...")
    linearity_result = optimizer.analyze_linearity(n_loras=3)
    print(f"  Linearity error (normalized): {linearity_result['linearity_error_norm']:.6f}")
    if linearity_result['linearity_error_norm'] < 0.01:
        print(f"  → Highly linear composition")
    elif linearity_result['linearity_error_norm'] < 0.05:
        print(f"  → Moderately linear composition")
    else:
        print(f"  → Non-linear composition detected")

    return optimizer


def example_4_scaling_laws():
    """
    Example 4: Scaling Laws Analysis

    Demonstrates fitting and using scaling laws
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Scaling Laws Analysis")
    print("=" * 70)

    from scaling_laws import ScalingLawAnalyzer

    # Create analyzer
    analyzer = ScalingLawAnalyzer()

    # Generate synthetic data
    print("\nGenerating training data...")
    data = analyzer.data_generator.generate_dataset(n_scenarios=500)
    print(f"  Generated {len(data)} scenarios")

    # Fit scaling law
    print("\nFitting scaling law...")
    print("  accuracy = a + b·log(params) + c·n_loras - d·interference")
    coefficients = analyzer.fit_scaling_law(data)

    # Make predictions
    print("\nExample predictions:")
    test_cases = [
        (1e7, 1, 0.1),  # 10M params, 1 LoRA, low interference
        (1e7, 5, 0.5),  # 10M params, 5 LoRAs, high interference
        (5e7, 10, 1.0), # 50M params, 10 LoRAs, very high interference
    ]

    for params, n_loras, interference in test_cases:
        acc = analyzer.predict_accuracy(params, n_loras, interference)
        print(f"  params={params:.1e}, n_loras={n_loras}, "
              f"interference={interference:.1f} → accuracy={acc:.4f}")

    # Find optimal configuration
    print("\nFinding optimal configuration for 80% accuracy...")
    config = analyzer.find_optimal_configuration(
        target_accuracy=0.80,
        max_loras=20
    )

    if config:
        print(f"  Base dim: {config['base_dim']}")
        print(f"  Number of LoRAs: {config['n_loras']}")
        print(f"  Rank per LoRA: {config['rank']}")
        print(f"  Total params: {config['n_params']:.1e}")
        print(f"  Predicted accuracy: {config['predicted_accuracy']:.4f}")

    # Compute break-even curve
    print("\nComputing break-even curve...")
    loras, single_params = analyzer.compute_break_even_curve(
        base_dim=1024, rank=32, max_loras=10
    )

    print(f"  {'N LoRAs':<10} {'Single Model Params Needed':<25}")
    print("-" * 40)
    for i in range(0, len(loras), 2):
        print(f"  {loras[i]:<10} {single_params[i]:<25.1e}")

    return analyzer


def example_5_end_to_end_workflow():
    """
    Example 5: End-to-End Workflow

    Demonstrates complete workflow using all modules
    """
    print("\n" + "=" * 70)
    print("EXAMPLE 5: End-to-End Workflow")
    print("=" * 70)

    print("""
This example shows a complete workflow:

1. Rank Analysis: Find minimum sufficient rank
   → Result: r=32 for code domain

2. Interference Detection: Check compatibility
   → Result: Code + Writing = Compatible (γ=0.15)

3. Composition Optimization: Find optimal weights
   → Result: 1/√N weighting works best

4. Scaling Laws: Find optimal configuration
   → Result: 5 LoRAs of rank 32 > 1 large model

Workflow:
  a) Determine rank needed (Module 1)
  b) Check which LoRA pairs are compatible (Module 2)
  c) Compose compatible LoRAs with optimal weights (Module 3)
  d) Verify efficiency using scaling laws (Module 4)

Use the run_all.py script to execute the full workflow:
  python run_all.py --quick
    """)


def main():
    """Run all examples"""
    print("=" * 70)
    print("LoRA Composition Validation - Quick Start Examples")
    print("=" * 70)

    examples = [
        ("Rank Sufficiency", example_1_rank_sufficiency),
        ("Interference Detection", example_2_interference_detection),
        ("Composition Optimization", example_3_composition_optimization),
        ("Scaling Laws", example_4_scaling_laws),
        ("End-to-End Workflow", example_5_end_to_end_workflow),
    ]

    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")

    print("\nRunning all examples...")
    print("Note: This uses small dimensions for quick demonstration")
    print("      Use run_all.py for comprehensive analysis\n")

    try:
        for name, example_func in examples:
            try:
                example_func()
            except Exception as e:
                print(f"\n✗ Error in {name}: {str(e)}")
                import traceback
                traceback.print_exc()

        print("\n" + "=" * 70)
        print("Examples complete!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Run full analysis: python run_all.py")
        print("  2. Check results in ./results/ directory")
        print("  3. See README.md for detailed documentation")

    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")


if __name__ == "__main__":
    main()
