.PHONY: help install dev test lint format clean sim fpga docs

# Default target
help:
	@echo "TernaryAir - Open Source Air-Gapped Inference Hardware"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install     Install Python package"
	@echo "  dev         Install development dependencies"
	@echo "  test        Run all tests"
	@echo "  lint        Run linters"
	@echo "  format      Format code"
	@echo "  clean       Clean build artifacts"
	@echo "  sim         Run RTL simulation"
	@echo "  fpga        Build FPGA bitstream"
	@echo "  docs        Build documentation"
	@echo "  package     Build distribution packages"

# Python setup
install:
	pip install -e .

dev:
	pip install -e ".[dev]"

# Testing
test:
	pytest tests/ -v --cov=software/sdk/ternaryair --cov-report=term-missing

test-hardware:
	cd hardware/rtl && iverilog -g2012 -o sim *.sv && vvp sim

# Code quality
lint:
	black --check software/
	isort --check software/
	mypy software/
	ruff check software/

format:
	black software/
	isort software/

# Build artifacts
clean:
	rm -rf build/ dist/ *.egg-info
	rm -rf .pytest_cache .mypy_cache .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	cd hardware/rtl && rm -f sim *.vcd *.log

# Hardware simulation
sim:
	cd hardware/rtl && iverilog -g2012 -o sim *.sv && vvp sim

sim-wave:
	cd hardware/rtl && iverilog -g2012 -o sim *.sv && vvp sim && gtkwave dump.vcd &

# FPGA build
fpga:
	@echo "Building FPGA bitstream..."
	cd hardware/fpga && $(MAKE) bitstream

fpga-program:
	cd hardware/fpga && $(MAKE) program

# Documentation
docs:
	cd docs && make html

docs-serve:
	cd docs && make livehtml

# Distribution
package:
	python -m build

publish:
	twine upload dist/*

# Quick start
quickstart: install
	@echo ""
	@echo "TernaryAir installed! Try:"
	@echo "  python -c \"from ternaryair import TernaryAir; print(TernaryAir().generate('Hello'))\""
