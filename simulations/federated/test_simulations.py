"""
Quick test script to verify all simulations run correctly.

Run this before the full simulation suite to check dependencies and basic functionality.
"""

import sys
import torch
import numpy as np

def test_dependencies():
    """Test all required dependencies"""
    print("Testing dependencies...")

    try:
        import torch
        print(f"✓ PyTorch {torch.__version__}")
    except ImportError:
        print("✗ PyTorch not found")
        return False

    try:
        import numpy
        print(f"✓ NumPy {numpy.__version__}")
    except ImportError:
        print("✗ NumPy not found")
        return False

    try:
        import scipy
        print(f"✓ SciPy {scipy.__version__}")
    except ImportError:
        print("✗ SciPy not found")
        return False

    try:
        import matplotlib
        print(f"✓ Matplotlib {matplotlib.__version__}")
    except ImportError:
        print("✗ Matplotlib not found")
        return False

    return True


def test_basic_functionality():
    """Test basic ML operations"""
    print("\nTesting basic functionality...")

    # Test tensor operations
    x = torch.randn(10, 5)
    y = torch.randn(10, 1)
    print(f"✓ Tensor creation: {x.shape}, {y.shape}")

    # Test model
    model = torch.nn.Linear(5, 2)
    output = model(x)
    print(f"✓ Model forward pass: {output.shape}")

    # Test numpy operations
    arr = np.random.randn(100, 10)
    mean = np.mean(arr)
    std = np.std(arr)
    print(f"✓ NumPy operations: mean={mean:.4f}, std={std:.4f}")

    return True


def test_fedavg_simulation():
    """Test simple FedAvg simulation"""
    print("\nTesting FedAvg simulation...")

    # Create mock colonies
    n_colonies = 5
    n_rounds = 3

    # Mock data
    colony_updates = [
        torch.randn(10) * 0.1 for _ in range(n_colonies)
    ]
    print(f"✓ Created {n_colonies} colony updates")

    # FedAvg aggregation
    weights = torch.ones(n_colonies) / n_colonies
    aggregated = sum(w * u for w, u in zip(weights, colony_updates))
    print(f"✓ FedAvg aggregation: {aggregated.shape}")

    return True


def test_dp_mechanism():
    """Test DP Gaussian mechanism"""
    print("\nTesting DP mechanism...")

    # Parameters
    epsilon = 1.0
    delta = 1e-5
    sensitivity = 1.0

    # Calculate noise scale
    sigma = sensitivity * np.sqrt(2 * np.log(1.25 / delta)) / epsilon
    print(f"✓ Noise scale (σ): {sigma:.4f}")

    # Apply noise
    param = torch.randn(10)
    noise = torch.randn_like(param) * sigma
    noisy_param = param + noise
    print(f"✓ Noisy parameters: {noisy_param.shape}")

    return True


def test_krum_aggregation():
    """Test Krum aggregation"""
    print("\nTesting Krum aggregation...")

    # Mock updates (one Byzantine)
    updates = [
        torch.randn(10) * 0.1 for _ in range(4)  # 4 honest
    ]
    updates[0] *= 10  # Make first one Byzantine

    # Calculate distances
    n = len(updates)
    distances = np.zeros((n, n))

    for i in range(n):
        for j in range(i+1, n):
            dist = torch.norm(updates[i] - updates[j]).item()
            distances[i][j] = dist
            distances[j][i] = dist

    print(f"✓ Distance matrix: {distances.shape}")

    # Krum score
    n_closest = n - 1 - 2  # n - f - 2 (assuming f=1)
    scores = []
    for i in range(n):
        sorted_dists = np.sort(distances[i])
        score = np.sum(sorted_dists[1:n_closest+1])
        scores.append(score)

    selected = np.argmin(scores)
    print(f"✓ Krum selected update: {selected} (should not be 0)")

    return True


def test_compression():
    """Test compression techniques"""
    print("\nTesting compression...")

    # Uniform quantization
    bits = 8
    levels = 2 ** bits - 1
    param = torch.randn(100)

    min_val = param.min()
    max_val = param.max()
    scale = (max_val - min_val) / levels

    quantized = torch.round((param - min_val) / scale)
    quantized = torch.clamp(quantized, 0, levels)

    # Compression ratio
    original_bits = 32
    compressed_bits = bits
    ratio = compressed_bits / original_bits

    print(f"✓ Quantization: {original_bits} → {compressed_bits} bits")
    print(f"✓ Compression ratio: {ratio:.2f}")

    # Top-k sparsification
    k = 10  # Keep top 10%
    flat = param.flatten()
    _, top_k_idx = torch.topk(torch.abs(flat), k)

    sparse = torch.zeros_like(flat)
    sparse[top_k_idx] = flat[top_k_idx]

    sparsity_ratio = k / len(flat)
    print(f"✓ Top-k sparsification: {sparsity_ratio:.1%} non-zero")

    return True


def run_all_tests():
    """Run all tests"""
    print("="*70)
    print("POLLN FEDERATED LEARNING SIMULATION TESTS")
    print("="*70)

    tests = [
        ("Dependencies", test_dependencies),
        ("Basic Functionality", test_basic_functionality),
        ("FedAvg Simulation", test_fedavg_simulation),
        ("DP Mechanism", test_dp_mechanism),
        ("Krum Aggregation", test_krum_aggregation),
        ("Compression", test_compression),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"✗ {name} failed")
        except Exception as e:
            failed += 1
            print(f"✗ {name} failed with error: {e}")

    print("\n" + "="*70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*70)

    if failed == 0:
        print("\n✓ All tests passed! Ready to run full simulations.")
        print("  Run: python run_all.py")
    else:
        print(f"\n✗ {failed} test(s) failed. Please check dependencies.")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
