# Graph Evolution Simulations - Quick Start Guide

## Prerequisites

```bash
# Install Python dependencies
pip install numpy scipy networkx python-louvain scikit-learn powerlaw matplotlib seaborn tqdm
```

## Quick Start

### 1. Run All Simulations (Recommended)

```bash
# Full simulation (takes 10-30 minutes depending on hardware)
python simulations/run_all.py

# Quick run for testing (2-5 minutes)
python simulations/run_all.py --quick
```

### 2. Run Individual Simulations

```bash
# Pruning - Prove optimal sparsity (H1)
python simulations/run_all.py --simulation pruning

# Grafting - Discover useful connections
python simulations/run_all.py --simulation grafting

# Clustering - Organize agents optimally
python simulations/run_all.py --simulation clustering

# Co-evolution - Validate stability (H3)
python simulations/run_all.py --simulation coevolution
```

## Expected Output

Each simulation generates:

1. **PNG plots** - Visualizations of results
2. **JSON data** - Numerical results for further analysis

Location: `simulations/results/{simulation_name}/`

## Key Results to Look For

### Pruning Simulation
- **File**: `performance_vs_sparsity.png`
- **What to check**: Concave curve with peak at sparsity ≈ 0.3-0.5
- **Hypothesis H1**: Confirmed if peak falls in this range

### Grafting Simulation
- **File**: `grafting_smallworld.png`
- **What to check**: Sigma (σ) > 1 for intelligent strategies
- **Hypothesis H2**: Confirmed if σ > 1

### Clustering Simulation
- **File**: `clustering_metrics.png`
- **What to check**: Louvain or Spectral performs best
- **Validation**: High modularity (Q > 0.3) and low conductance

### Co-evolution Simulation
- **File**: `coevolution_stability.png`
- **What to check**: Stability > 0.5 for gradual/static environments
- **Hypothesis H3**: Confirmed if evolved networks are more stable

## Parameter Guide

```bash
--agents, -n        # Number of agents (default: 100)
--generations, -g   # Number of generations (default: 500)
--trials, -t        # Trials per condition (default: 5)
--quick, -q         # Reduce parameters for faster execution
```

### Recommended Settings

| Purpose | Agents | Generations | Trials |
|---------|--------|-------------|--------|
| Quick test | 50 | 200 | 3 |
| Normal run | 100 | 500 | 5 |
| Publication | 200 | 1000 | 10 |

## Interpreting Results

### Performance Score

Higher is better. Computed from:
- Small-world properties (40%)
- Communication efficiency (30%)
- Community structure (30%)

### Sparsity

Ratio of missing edges to possible edges:
- 0.0 = fully connected
- 0.5 = half connected
- 1.0 = no edges

Optimal range: 0.3-0.5

### Small-World Sigma (σ)

- σ < 1: Random network
- σ > 1: Small-world network (desirable)
- σ >> 1: Highly clustered

### Modularity (Q)

- Q < 0.3: Weak community structure
- Q > 0.3: Good community structure
- Q > 0.5: Excellent community structure

## Troubleshooting

### "ModuleNotFoundError: No module named 'numpy'"

```bash
pip install -r simulations/requirements.txt
```

### "Memory Error" or Slow Execution

```bash
# Use quick mode
python simulations/run_all.py --quick

# Or reduce parameters manually
python simulations/run_all.py --agents 50 --generations 200 --trials 3
```

### "No such file or directory" errors

```bash
# Create results directories
mkdir -p simulations/results/pruning
mkdir -p simulations/results/grafting
mkdir -p simulations/results/clustering
mkdir -p simulations/results/coevolution
```

## Next Steps

After simulations complete:

1. **View plots**: Open PNG files in `simulations/results/`
2. **Analyze data**: Parse JSON files for custom analysis
3. **Compare strategies**: Look at summary in terminal output
4. **Generate report**: Use results for validation documentation

## Integration with TypeScript

These simulations validate the implementation in `src/core/evolution.ts`:

- **Pruning** → `GraphEvolution.prune()` method
- **Grafting** → `GraphEvolution.graft()` method
- **Clustering** → `GraphEvolution.detectClusters()` method
- **Metrics** → `EvolutionStats` interface

For details, see `docs/graph-evolution-simulations.md`.

---

**Need Help?** Check the main README or open an issue on GitHub.
