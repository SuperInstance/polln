# LoRA Composition Mathematics Validation

A comprehensive Python simulation suite to mathematically validate POLLN's LoRA Library concept: **Small base models + interchangeable LoRA adapters = expert agents**.

## Overview

This simulation suite validates the mathematical foundations of composing multiple LoRA (Low-Rank Adaptation) adapters to create specialized expert agents from a shared base model.

### Mathematical Foundation

The total weight matrix when composing LoRA adapters:

```
W_total = W_base + Σ w_i × (B_i × A_i)
```

Where:
- `W_base`: Frozen base model weights
- `B_i, A_i`: Low-rank adapter matrices (rank r << d)
- `w_i`: Composition weights

### Key Hypotheses

**H1: Rank Decomposition**
```
For expertise E: rank(W_E - W_base) ≤ r_min
Question: Is r_min ≈ 64 for most domains?
```

**H2: Composition Linearity**
```
For compatible LoRAs: (L1 ⊕ L2)(x) ≈ L1(x) + L2(x) - L1∩L2(x)
Question: When does linearity break down?
```

**H3: Library Efficiency**
```
N LoRAs of rank r: N×r×2d parameters vs single model of size S
Break-even: S > 2×N×r×d
Question: When is LoRA library more efficient?
```

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Run All Simulations

```bash
# Full analysis (comprehensive but slower)
python run_all.py

# Quick mode (faster testing)
python run_all.py --quick

# Run specific modules
python run_all.py --modules rank interference

# Custom output directory
python run_all.py --output-dir ./my_results
```

### Run Individual Modules

```python
# Rank sufficiency analysis
from rank_analysis import RankSufficiencyAnalyzer

analyzer = RankSufficiencyAnalyzer(
    base_dim=1024,
    max_rank=256,
    domains=["code", "writing", "analysis", "research"]
)
results = analyzer.run_full_analysis()
h1_results = analyzer.test_hypothesis_h1()

# Interference detection
from interference import InterferenceDetector

detector = InterferenceDetector(
    base_dim=1024,
    ranks=[8, 16, 32, 64],
    domains=["code", "writing", "analysis", "research"]
)
results = detector.run_full_analysis()

# Composition optimization
from composition import CompositionOptimizer

optimizer = CompositionOptimizer(base_dim=1024, lambda_reg=0.01)
results = optimizer.run_full_analysis()

# Scaling laws
from scaling_laws import ScalingLawAnalyzer

analyzer = ScalingLawAnalyzer()
results = analyzer.run_full_analysis()
```

## Simulation Modules

### 1. Rank Sufficiency Analysis (`rank_analysis.py`)

**Purpose**: Determine what rank r is needed to capture expertise.

**Metrics**:
- `reconstruction_error = ||W_expert - (W_base + BA)||_F`
- Spectral norm analysis
- Cumulative explained variance

**Key Functions**:
- `SyntheticModelGenerator`: Generates expert model weights for different domains
- `LoRADecomposer`: Decomposes expertise difference into low-rank matrices
- `RankSufficiencyAnalyzer`: Main analysis class

**Outputs**:
- Phase diagram: error vs rank for all domains
- Sufficient ranks per domain (95% and 99% variance thresholds)
- Spectral decay curves
- Hypothesis H1 validation results

### 2. Interference Detection (`interference.py`)

**Purpose**: Predict when two LoRAs interfere with each other.

**Metrics**:
- `interference = corr(B_1×A_1, B_2×A_2)`
- `gradient_conflict = cos(g_1, g_2)`
- `performance_degradation = metrics(L_1 alone) - metrics(L_1 ⊕ L_2)`

**Key Functions**:
- `InterferenceCalculator`: Computes various interference metrics
- `InterferencePredictor`: Predicts interference from LoRA parameters
- `InterferenceDetector`: Main analysis class with clustering

**Outputs**:
- Interference heatmap matrix
- Feature importance for prediction
- Compatible vs incompatible LoRA pair clusters
- Interference prediction model

### 3. Composition Optimization (`composition.py`)

**Purpose**: Find optimal weights for combining LoRAs.

**Mathematical Formulation**:
```
loss = ||W_target - W_base - Σ w_i(B_iA_i)||² + λΣw_i²
```

**Strategies Compared**:
- Uniform: `w_i = 1/N`
- Inverse sqrt: `w_i = 1/√N`
- Rank-weighted: `w_i ∝ rank_i`
- Norm-weighted: `w_i ∝ ||BA||_F`
- Learned: Gradient descent optimization
- Closed-form: Analytical solution

**Key Functions**:
- `CompositionStrategy`: Implements different weighting strategies
- `CompositionOptimizer`: Compares strategies and analyzes linearity

**Outputs**:
- Strategy comparison (reconstruction error, performance)
- 1/√N hypothesis validation
- Linearity analysis results
- Non-linear composition optimization

### 4. Scaling Laws (`scaling_laws.py`)

**Purpose**: Derive performance scaling relationships.

**Scaling Law**:
```
accuracy = a + b·log(params) + c·n_loras - d·interference
```

**Key Questions**:
- When is LoRA library more efficient than bigger model?
- What is the optimal base model size for N LoRAs?
- Where do diminishing returns occur?

**Key Functions**:
- `ScalingLawDataGenerator`: Generates synthetic scaling data
- `ScalingLawAnalyzer`: Fits scaling law coefficients
- Break-even curve computation
- Diminishing returns detection

**Outputs**:
- Scaling law coefficients (a, b, c, d)
- Break-even curves (LoRA vs single model)
- Optimal configurations for target accuracies
- Diminishing returns points
- 3D accuracy surface plots

## Results Structure

```
simulations/lora/results/
├── rank_analysis_results.json          # Rank sufficiency data
├── interference_results.json            # Interference metrics
├── composition_results.json             # Composition optimization
├── scaling_law_results.json             # Scaling law coefficients
├── summary_report.json                  # Comprehensive summary
├── phase_diagram.png                    # Rank vs error plot
├── interference_matrix.png              # Interference heatmap
├── strategy_comparison.png              # Composition strategies
├── linearity_analysis.png               # Linearity error distribution
├── break_even_curves.png                # Efficiency comparison
├── accuracy_surface.png                 # 3D accuracy surface
├── diminishing_returns.png              # Diminishing returns points
└── simulation_log_*.txt                 # Execution log
```

## Key Findings Template

After running simulations, check `summary_report.json` for:

### Rank Sufficiency
- Minimum sufficient rank per domain (95% variance)
- Hypothesis H1 validation: Is r=64 sufficient?

### Interference
- Top predictive features for interference
- Compatible vs incompatible expert pairs
- Interference prediction accuracy

### Composition
- Best weighting strategy
- 1/√N validation results
- Linearity breakdown threshold

### Scaling Laws
- Coefficient values
- Break-even parameter counts
- Optimal configurations
- Diminishing returns points

## Examples

### Example 1: Test Rank Sufficiency for Code Domain

```python
from rank_analysis import RankSufficiencyAnalyzer

analyzer = RankSufficiencyAnalyzer(base_dim=1024, max_rank=128)
results = analyzer.analyze_domain("code", ranks=[8, 16, 32, 64, 128])

for r in results:
    print(f"Rank {r.rank}: error={r.reconstruction_error:.4f}, "
          f"variance={r.explained_variance:.4f}")

# Find sufficient rank
r_min = analyzer.find_sufficient_rank("code", threshold=0.95)
print(f"Minimum sufficient rank: {r_min}")
```

### Example 2: Predict LoRA Interference

```python
from interference import InterferenceDetector, LoRAPair
import torch

# Create LoRA pair
B1 = torch.randn(1024, 32)
A1 = torch.randn(32, 1024)
B2 = torch.randn(1024, 32)
A2 = torch.randn(32, 1024)

pair = LoRAPair(B1, A1, B2, A2, "code_lora", "writing_lora")

# Compute interference
detector = InterferenceDetector()
metrics = detector.compute_all_metrics()[0]

print(f"Weight correlation: {metrics.weight_correlation:.4f}")
print(f"Subspace overlap: {metrics.subspace_overlap:.4f}")
print(f"Gradient conflict: {metrics.gradient_conflict:.4f}")
```

### Example 3: Compare Composition Strategies

```python
from composition import CompositionOptimizer

optimizer = CompositionOptimizer(base_dim=1024)
results = optimizer.compare_strategies(n_scenarios=20)

for strategy, strategy_results in results.items():
    errors = [r.reconstruction_error for r in strategy_results]
    print(f"{strategy}: {np.mean(errors):.4f} ± {np.std(errors):.4f}")
```

### Example 4: Find Optimal Configuration

```python
from scaling_laws import ScalingLawAnalyzer

analyzer = ScalingLawAnalyzer()
analyzer.fit_scaling_law(data)  # Fit from data

# Find optimal config for 80% accuracy
config = analyzer.find_optimal_configuration(target_accuracy=0.8)
print(f"Optimal: {config['n_loras']} LoRAs, rank={config['rank']}, "
      f"base_dim={config['base_dim']}")
```

## Validation Success Criteria

The simulation suite is considered successful if:

1. **Rank Sufficiency (H1)**
   - ✓ Prove rank sufficiency bounds for each domain
   - ✓ Validate r=64 for 95% variance in most domains

2. **Interference Prediction**
   - ✓ Build interference prediction model with R² > 0.7
   - ✓ Identify compatible vs incompatible pairs

3. **Composition Optimization**
   - ✓ Prove optimal composition theorems
   - ✓ Validate 1/√N or better weighting strategy

4. **Scaling Laws**
   - ✓ Fit scaling law coefficients with statistical significance
   - ✓ Derive break-even conditions for LoRA vs single model

## Mathematical Proofs Targeted

### Theorem 1: Rank Decomposition Bound
If expertise E can be captured by LoRA of rank r, then:
```
||W_E - W_base - BA||_F / ||W_E - W_base||_F ≤ ε
```
where r = O(log(1/ε)) for most domains.

### Theorem 2: Composition Linearity
For compatible LoRAs L_1, L_2:
```
(L_1 ⊕ L_2)(x) = L_1(x) + L_2(x) + O(γ(L_1, L_2))
```
where γ is the interference metric.

### Theorem 3: Library Efficiency
LoRA library is more efficient than single model when:
```
N × 2 × r × d < S_large - S_base
```
where S_large is the large model size.

### Theorem 4: Optimal Composition
Optimal weights for L2-regularized composition:
```
w* = (X^T X + λI)^(-1) X^T y
```
where X contains flattened LoRA matrices.

## Performance

**Quick Mode** (testing):
- Base dimension: 512
- Runtime: ~5-10 minutes
- Suitable for development

**Full Analysis** (production):
- Base dimension: 1024-2048
- Runtime: ~30-60 minutes
- Comprehensive results

## Dependencies

- PyTorch: Weight manipulation and gradients
- NumPy: Numerical computations
- SciPy: Optimization and statistics
- Scikit-learn: Clustering and ML utilities
- Matplotlib/Seaborn: Visualization

## Citation

If you use this simulation suite, please cite:

```bibtex
@software{polln_lora_simulations,
  title = {LoRA Composition Mathematics Validation Suite},
  author = {POLLN Research Team},
  year = {2026},
  url = {https://github.com/SuperInstance/polln}
}
```

## License

MIT License - See LICENSE file for details.

## Contact

For questions or issues, please open a GitHub issue or contact the POLLN research team.
