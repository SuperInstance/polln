#!/bin/bash
# Granular Reasoning Validation - Run All Simulations
# This script executes all four simulation modules

set -e  # Exit on error

echo "========================================================================"
echo "GRANULAR REASONING VALIDATION - RUNNING ALL SIMULATIONS"
echo "========================================================================"
echo ""

# Create results directory
mkdir -p results

# Record start time
start_time=$(date +%s)

# Run simulations
echo "1. Running Decision Theory Simulation..."
python decision_theory.py
echo "✓ Decision Theory complete"
echo ""

echo "2. Running Information Theory Simulation..."
python information_theory.py
echo "✓ Information Theory complete"
echo ""

echo "3. Running Error Propagation Simulation..."
python error_propagation.py
echo "✓ Error Propagation complete"
echo ""

echo "4. Running Double-Slit Experiment Simulation..."
python double_slit.py
echo "✓ Double-Slit Experiment complete"
echo ""

# Calculate elapsed time
end_time=$(date +%s)
elapsed=$((end_time - start_time))
minutes=$((elapsed / 60))
seconds=$((elapsed % 60))

echo "========================================================================"
echo "ALL SIMULATIONS COMPLETE"
echo "========================================================================"
echo ""
echo "Total time: ${minutes}m ${seconds}s"
echo ""
echo "Results saved to: ./results/"
echo "  - CSV files: Raw data"
echo "  - JSON files: Serialized results"
echo "  - PNG files: Publication-quality figures"
echo "  - TXT files: Summary reports"
echo ""
echo "Next steps:"
echo "  1. Review summary reports in ./results/"
echo "  2. Examine figures for validation"
echo "  3. Open granular_reasoning_validation.ipynb for interactive analysis"
echo ""
echo "========================================================================"
