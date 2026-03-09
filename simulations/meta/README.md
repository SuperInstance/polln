# META Tile Simulations

Python simulations proving that pluripotent META tiles can learn and adapt through plasticity mechanisms.

## Overview

This simulation suite provides empirical validation for POLLN's META tile system through four comprehensive experiments:

1. **Differentiation Dynamics** - Proves signal-based differentiation converges to specialists
2. **Plasticity Rules** - Compares learning rules for optimal meta-learning
3. **Knowledge Succession** - Validates efficient knowledge transfer between generations
4. **MAML vs Reptile** - Tests first-order vs second-order meta-learning efficiency

## Mathematical Foundations

### Differentiation

```python
P(specialized|signals) = σ(W_meta × signals + b)
```

META tiles differentiate based on environmental signals using attractor dynamics from gene regulatory networks (GRNs).

### Plasticity

```python
# Hebbian learning
Δw_ij = η × pre_i × post_j

# Oja's rule (normalized)
Δw_ij = η × pre_i × post_j - α × post_j² × w_ij
```

Synaptic weights evolve according to local learning rules inspired by neuroscience.

### Succession

```python
W_new = W_old + α × W_teacher + ε
retention = α × transfer + (1-α) × decay
```

Knowledge transfer enables lifelong learning without catastrophic forgetting.

### Meta-Learning

```python
# MAML (second-order)
θ ← θ - α∇_θ L_train(θ - β∇_θ L_val(θ))

# Reptile (first-order)
θ ← θ + α × Σ(θ_i - θ) / N
```

Few-shot learning through gradient-based meta-learning.

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
cd simulations/meta

# Run all experiments
python differentiation.py
python plasticity.py
python succession.py
python maml_vs_reptile.py
```

### Individual Simulations

#### 1. Differentiation Dynamics

```bash
python differentiation.py
```

**Tests:**
- Signal-based differentiation trajectories
- Varying signal strength, noise, cardinality
- Differentiation accuracy and stability
- Convergence to specialist attractors

**Outputs:**
- `results/differentiation_results.json`
- `figures/differentiation_main.png`

**Hypotheses:**
- H1: Differentiation converges in O(log N) steps
- H1: Signal strength correlates with accuracy
- H1: Noise tolerance exists up to threshold

#### 2. Plasticity Rules

```bash
python plasticity.py
```

**Tests:**
- Hebbian vs Oja vs BCM vs Anti-Hebbian
- Synaptic weight evolution
- Convergence speed and stability
- Learning rate optimization

**Outputs:**
- `results/plasticity_results.json`
- `figures/plasticity_comparison.png`

**Hypotheses:**
- H2: For η < 2/λ_max, weights converge
- H2: Oja's rule provides best stability
- H2: Optimal learning rate exists for META tiles

#### 3. Knowledge Succession

```bash
python succession.py
```

**Tests:**
- Teacher-student knowledge transfer
- Transfer rate and decay rate optimization
- Knowledge preservation across generations
- Lifelong learning without forgetting

**Outputs:**
- `results/succession_results.json`
- `figures/succession_main.png`

**Hypotheses:**
- H3: Optimal transfer rate maximizes retention
- H3: Decay balances adaptation vs retention
- H3: Succession enables lifelong learning

#### 4. MAML vs Reptile

```bash
python maml_vs_reptile.py
```

**Tests:**
- First-order vs second-order meta-learning
- Few-shot learning performance (1-shot, 5-shot)
- Sample efficiency comparison
- Computational efficiency

**Outputs:**
- `results/metalearning_results.json`
- `figures/maml_vs_reptile.png`

**Hypotheses:**
- H4: First-order approximation is sufficient
- H4: Reptile converges faster with comparable accuracy
- H4: Sample efficiency favors Reptile

## Results Interpretation

### Differentiation Results

Key metrics:
- **Differentiation rate**: % of META tiles that successfully differentiate
- **Convergence step**: Average steps to differentiation
- **Type diversity**: Shannon entropy of type distribution
- **Final distribution**: Count of each agent type

Success criteria:
- Differentiation rate > 80%
- Convergence in < 100 steps
- Type diversity > 1.5 bits
- Balanced type distribution

### Plasticity Results

Key metrics:
- **Final error**: Prediction error after training
- **Convergence episode**: Steps to convergence
- **Stability score**: Inverse of error variance
- **Weight variance**: Measure of weight stability

Success criteria:
- Oja's rule achieves best stability
- Hebbian shows fastest initial learning
- Learning rate < 2/λ_max converges

### Succession Results

Key metrics:
- **Retention rate**: Knowledge preserved across generations
- **Performance improvement**: Gain over initial generation
- **Patterns transferred**: Average patterns per succession
- **Compression ratio**: Efficiency of knowledge compression

Success criteria:
- Retention rate > 0.7
- Performance improves over generations
- Compression ratio < 0.6
- No catastrophic forgetting

### Meta-Learning Results

Key metrics:
- **Test loss**: Performance on novel tasks
- **Training time**: Computational cost
- **Speedup**: Reptile time / MAML time
- **Sample efficiency**: Performance vs shots

Success criteria:
- Reptile achieves < 10% accuracy loss
- Reptile provides > 3x speedup
- First-order is sufficient for META tiles

## File Structure

```
simulations/
├── meta/
│   ├── differentiation.py      # Differentiation dynamics
│   ├── plasticity.py           # Plasticity rules comparison
│   ├── succession.py           # Knowledge transfer
│   ├── maml_vs_reptile.py      # Meta-learning comparison
│   ├── README.md               # This file
│   └── requirements.txt        # Python dependencies
├── results/
│   ├── differentiation_results.json
│   ├── plasticity_results.json
│   ├── succession_results.json
│   └── metalearning_results.json
└── figures/
    ├── differentiation_main.png
    ├── plasticity_comparison.png
    ├── succession_main.png
    └── maml_vs_reptile.png
```

## Scientific Contribution

These simulations provide empirical evidence for:

1. **Pluripotent Agent Theory**: Undifferentiated agents can specialize via signals
2. **Attractor Dynamics**: Gene regulatory network models enable stable differentiation
3. **Plasticity Optimization**: Oja's rule provides stability for lifelong learning
4. **Knowledge Transfer**: Succession protocol prevents catastrophic forgetting
5. **Meta-Learning Efficiency**: First-order methods sufficient for META tiles

## Citation

If you use these simulations in your research:

```bibtex
@misc{polln_meta_simulations,
  title={META Tile Simulations: Proving Plasticity in Pluripotent Agents},
  author={POLLN Research Team},
  year={2026},
  url={https://github.com/SuperInstance/polln}
}
```

## References

1. Huang, S. (2009). "Gene Expression Profiling, Genetic Networks, and Cellular States"
2. Oja, E. (1982). "Simplified Neuron Model as a Principal Component Analyzer"
3. Kirkpatrick, J. et al. (2017). "Overcoming catastrophic forgetting with EWC"
4. Finn, C. et al. (2017). "Model-Agnostic Meta-Learning (MAML)"
5. Nichol, A. et al. (2018). "On First-Order Meta-Learning Algorithms"

## License

MIT License - See LICENSE file in main repository.

---

*Generated for POLLN: Pattern-Organized Large Language Network*
*https://github.com/SuperInstance/polln*
