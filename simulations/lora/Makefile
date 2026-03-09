# LoRA Composition Mathematics Validation
# Makefile for easy execution

.PHONY: help install test quick full clean all rank interference composition scaling

# Default target
help:
	@echo "LoRA Composition Mathematics Validation"
	@echo ""
	@echo "Available targets:"
	@echo "  install      - Install Python dependencies"
	@echo "  test         - Run quick test (1 module, small scale)"
	@echo "  quick        - Run all modules in quick mode"
	@echo "  full         - Run comprehensive analysis"
	@echo "  rank         - Run rank sufficiency analysis only"
	@echo "  interference - Run interference detection only"
	@echo "  composition  - Run composition optimization only"
	@echo "  scaling      - Run scaling laws analysis only"
	@echo "  report       - Generate summary report from existing results"
	@echo "  clean        - Remove all generated files"
	@echo "  all          - clean + full"

# Installation
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

# Test (single module, very fast)
test:
	@echo "Running quick test..."
	python run_all.py --quick --modules rank --output-dir ./results/test

# Quick mode (all modules, faster)
quick:
	@echo "Running all modules in quick mode..."
	python run_all.py --quick --output-dir ./results/quick

# Full analysis
full:
	@echo "Running comprehensive analysis..."
	python run_all.py --output-dir ./results/full

# Individual modules
rank:
	@echo "Running rank sufficiency analysis..."
	python run_all.py --modules rank --output-dir ./results/rank

interference:
	@echo "Running interference detection..."
	python run_all.py --modules interference --output-dir ./results/interference

composition:
	@echo "Running composition optimization..."
	python run_all.py --modules composition --output-dir ./results/composition

scaling:
	@echo "Running scaling laws analysis..."
	python run_all.py --modules scaling --output-dir ./results/scaling

# Generate report from existing results
report:
	@echo "Generating summary report..."
	@python -c "
import json
from pathlib import Path

results_dir = Path('./results/full')
if not results_dir.exists():
    results_dir = Path('./results/quick')

summary_file = results_dir / 'summary_report.json'
if summary_file.exists():
    with open(summary_file) as f:
        summary = json.load(f)
    print(json.dumps(summary, indent=2))
else:
    print('No summary report found. Run simulations first.')
"

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -rf ./results/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✓ Cleaned"

# All: clean then full
all: clean full

# Docker targets (optional)
docker-build:
	docker build -t polln-lora-simulations .

docker-run:
	docker run -v $(PWD)/results:/app/results polln-lora-simulations

docker-quick:
	docker run -v $(PWD)/results:/app/results polln-lora-simulations python run_all.py --quick

# Development targets
dev-install:
	pip install -r requirements.txt
	pip install pytest black mypy flake8

dev-test:
	pytest simulations/lora/ -v

dev-format:
	black simulations/lora/

dev-lint:
	flake8 simulations/lora/

# Documentation
docs:
	@echo "Generating documentation..."
	@cat README.md

# Results summary
summary:
	@echo "Recent simulation results:"
	@echo ""
	@ls -lt results/*/summary_report.json 2>/dev/null | head -5 || echo "No results found yet"
