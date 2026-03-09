#!/bin/bash
# Quick start script for POLLN Topology Optimization Simulator

set -e

echo "========================================="
echo "POLLN Topology Optimization Simulator"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python --version || python3 --version

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Run quick demo
echo ""
echo "Running quick demo..."
echo ""

# Generate a sample topology
echo "1. Generating a sample topology (50 agents, Watts-Strogatz)..."
python generate_topology.py generate -n 50 -t watts_strogatz -k 6 -p 0.1 -o demo_topology.graphml

echo ""
echo "2. Evaluating the topology..."
python generate_topology.py evaluate -n 50 -t watts_strogatz -k 6 -p 0.1

echo ""
echo "3. Comparing topologies..."
python generate_topology.py compare -n 50

echo ""
echo "4. Getting topology recommendation..."
python generate_topology.py recommend -n 50

echo ""
echo "========================================="
echo "Quick start complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  - Run full optimization: python run_all.py --quick"
echo "  - Generate specific topology: python generate_topology.py generate -n 100 -t watts_strogatz"
echo "  - See documentation: README.md"
echo ""
