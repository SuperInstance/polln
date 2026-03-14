# Contributing to TernaryAir

First off, thank you for considering contributing to TernaryAir! It's people like you that make this project a great tool for accessible, private AI.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title**
* **Describe the exact steps to reproduce the problem**
* **Provide specific examples to demonstrate the steps**
* **Describe the behavior you observed and what you expected**
* **Include screenshots or code samples if relevant**

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

* **Use a clear and descriptive title**
* **Provide a step-by-step description of the suggested enhancement**
* **Provide specific examples to demonstrate the use case**
* **Describe the current behavior and explain the expected behavior**
* **Explain why this enhancement would be useful**

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Include screenshots and animated GIFs in your pull request whenever possible
* Follow the code style guidelines below
* Document new code based on the Documentation Styleguide
* End all files with a newline

## Development Setup

### Prerequisites

* Python 3.9+ (for SDK development)
* Icarus Verilog or Verilator (for RTL simulation)
* Git

### Getting Started

```bash
# Clone the repository
git clone https://github.com/superinstance/ternaryair.git
cd ternaryair

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run RTL simulation
cd hardware/rtl
iverilog -g2012 -o sim *.sv
vvp sim
```

## Style Guidelines

### Python Code Style

* Follow PEP 8
* Use Black for formatting
* Use type hints for all public functions
* Write docstrings for all public modules, functions, classes, and methods

```python
def generate(
    self,
    prompt: str,
    max_tokens: int = 100,
    temperature: float = 0.7
) -> str:
    """Generate text completion for the given prompt.

    Args:
        prompt: The input prompt to complete.
        max_tokens: Maximum number of tokens to generate.
        temperature: Sampling temperature (0.0 to 2.0).

    Returns:
        The generated text completion.

    Raises:
        ValueError: If temperature is out of range.
    """
```

### SystemVerilog Code Style

* Use 4-space indentation
* One statement per line
* Meaningful signal and module names
* Comment complex logic
* Include formal properties where applicable

```systemverilog
//-----------------------------------------------------------------------------
// Module: rau (Rotation-Accumulate Unit)
// Description: Multiplication-free inference unit for ternary weights
// 
// TernaryAir - Open Source Air-Gapped Inference Hardware
// Copyright (c) 2026 Casey DiGennaro (SuperInstance.AI)
// MIT License
//-----------------------------------------------------------------------------

module rau #(
    parameter int ACTIVATION_WIDTH = 8,
    parameter int ACCUMULATOR_WIDTH = 24
)(
    input  logic                                  clk,
    input  logic                                  rst_n,
    input  logic signed [ACTIVATION_WIDTH-1:0]    activation,
    input  logic [1:0]                            weight,
    output logic signed [ACCUMULATOR_WIDTH-1:0]   result
);
```

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

```
Add streaming inference support to SDK

- Implement token-by-token streaming
- Add callback interface for real-time output
- Update documentation with examples

Closes #42
```

## Project Structure

```
ternaryair/
├── hardware/
│   ├── rtl/           # SystemVerilog source
│   ├── fpga/          # FPGA bitstreams and build files
│   └── reference/     # PCB, BOM, enclosure designs
├── software/
│   ├── sdk/           # Python SDK (ternaryair package)
│   ├── drivers/       # USB drivers
│   ├── examples/      # Example applications
│   └── server/        # REST API server
├── models/
│   ├── converter/     # Model conversion tools
│   ├── pretrained/    # Pre-trained model info
│   └── training/      # Training scripts
├── docs/              # Documentation
└── tests/             # Test suites
```

## Questions?

Feel free to open an issue with the "question" label, or start a discussion on GitHub Discussions.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
