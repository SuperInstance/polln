# Quick Start Guide - POLLN Cost Simulations

Get up and running with POLLN cost simulations in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- pip package manager

## Installation

```bash
# Navigate to simulations directory
cd simulations/cost

# Install dependencies
pip install numpy matplotlib
```

## Run Your First Simulation

### Option 1: Run Everything

```bash
python run_all.py
```

This will:
- Run all 4 cost simulations
- Generate text reports
- Create visualization charts
- Build an interactive calculator

### Option 2: Run One Simulation

```bash
# Try token cost analysis (fastest)
python token_cost_analysis.py
```

Expected output:
```
================================================================================
TOKEN COST ANALYSIS: POLLN vs MONOLITHIC LLMs
================================================================================

EXECUTIVE SUMMARY
--------------------------------------------------------------------------------
H1: POLLN reduces token costs by 85.2% vs GPT-4
H1: POLLN reduces token costs by 78.3% vs Claude Opus
Target: 80% reduction - ✓ ACHIEVED

DETAILED COST BREAKDOWN (1000 requests)
--------------------------------------------------------------------------------

MEDIUM COMPLEXITY:
  Input/Output Tokens: 2000/800

  GPT-4:
    Total Cost: $84.00
    Cost per Request: $0.0840
    Total Tokens: 2,800,000

  POLLN:
    Total Cost: $12.40
    Cost per Request: $0.0124
    Total Tokens: 840,000

  SAVINGS:
    vs GPT-4: 85.2% ($71.60)
    vs Claude: 78.3% ($44.60)

...
```

## View Results

### Text Reports

```bash
# View summary
cat COST_ANALYSIS_SUMMARY.txt

# View token cost details
cat token_cost_report.txt
```

### Interactive Calculator

```bash
# Open in browser
open cost_calculator.html  # macOS
xdg-open cost_calculator.html  # Linux
start cost_calculator.html  # Windows
```

### Charts

View generated PNG files:
- `token_cost_comparison.png`
- `quality_cost_frontier.png`
- `scaling_comparison.png`
- `cost_curves.png`

## Common Use Cases

### Use Case 1: Prove Cost Savings to Stakeholders

```bash
# Run all simulations
python run_all.py

# Open summary report
cat COST_ANALYSIS_SUMMARY.txt

# Open interactive calculator for demos
open cost_calculator.html
```

### Use Case 2: Compare Specific Configurations

```python
# Create custom_analysis.py
from token_cost_analysis import TokenCostAnalyzer, TokenProfile

analyzer = TokenCostAnalyzer()

# Your specific workload
profile = TokenProfile(
    input_tokens=5000,
    output_tokens=2000
)

results = analyzer.compare_costs(num_requests=10000)

# Print your savings
print(f"vs GPT-4: {results['complex']['polln']['cost_per_request'] / results['complex']['gpt-4']['cost_per_request'] * 100:.1f}%")
```

### Use Case 3: Find Your Break-Even Point

```python
# Create find_breakeven.py
from break_even_analysis import BreakEvenAnalyzer

analyzer = BreakEvenAnalyzer()

# Test different request volumes
for requests in [50, 100, 200, 500]:
    bre_days, _ = analyzer.find_break_even_point(requests)
    print(f"{requests} req/day: Break-even at day {bre_days}")
```

## Understanding the Results

### Token Cost Analysis

**Key Metric**: Cost per request

- **Good**: < $0.02 per request
- **Target**: 80% savings vs GPT-4
- **Factor**: Checkpoint efficiency

**What to look for**:
- Higher complexity = more savings
- Checkpoint efficiency > 70% for best results

### Compute Efficiency

**Key Metric**: Quality at cost percentage

- **Good**: > 90% quality at < 10% cost
- **Target**: 90% quality at 10% compute
- **Factor**: Number of agents

**What to look for**:
- More agents = higher quality (up to a point)
- 100 agents is often optimal
- Tiny agents (10M) are most cost-effective

### Dynamic Scaling

**Key Metric**: Auto-scaling savings

- **Good**: > 60% savings vs static
- **Target**: 60% cost reduction
- **Factor**: Workload variability

**What to look for**:
- Bursty workloads show most savings
- Constant workloads show minimal savings
- Auto-scaling beats static for variable loads

### Break-Even Analysis

**Key Metric**: Requests per day for break-even

- **Good**: < 100 requests/day
- **Target**: 100 requests/day
- **Factor**: Fixed cost amortization

**What to look for**:
- Break-even typically 60-90 days
- Higher volume = faster break-even
- Long-term ROI is significant

## Troubleshooting

### Issue: "Module not found"

```bash
# Install dependencies
pip install numpy matplotlib
```

### Issue: "Permission denied"

```bash
# Make directory writable
chmod +w .
```

### Issue: Charts not generated

```bash
# Install matplotlib backend
pip install matplotlib pillow
```

### Issue: Numbers don't match expectations

Check the assumptions in each simulation:
- Token costs: Based on published API pricing
- Compute costs: Based on cloud GPU pricing
- Quality benchmarks: Based on literature values

## Next Steps

1. **Customize parameters**: Edit simulation files to match your use case
2. **Run tests**: `python test_cost.py` to validate calculations
3. **Explore code**: Read source files for detailed methodology
4. **Integrate**: Use results in your own analysis

## Getting Help

- Read `README.md` for detailed documentation
- Check `CALCULATOR.md` for calculator guide
- Review `ROI.md` for business case analysis
- Open GitHub issue for bugs

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python run_all.py` | Run all simulations |
| `python token_cost_analysis.py` | Token cost comparison |
| `python compute_efficiency.py` | Compute optimization |
| `python dynamic_scaling.py` | Resource allocation |
| `python break_even_analysis.py` | Cost-benefit threshold |
| `python test_cost.py` | Run tests |
| `open cost_calculator.html` | Interactive calculator |

## Key Files

| File | Purpose |
|------|---------|
| `README.md` | Full documentation |
| `QUICKSTART.md` | This file |
| `CALCULATOR.md` | Calculator guide |
| `ROI.md` | Business case |
| `run_all.py` | Master script |
| `test_cost.py` | Test suite |

Happy simulating!
