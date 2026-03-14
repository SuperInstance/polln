# Contributing to SuperInstance.AI

First off, thank you for considering contributing to SuperInstance.AI! It's people like you that make SuperInstance such a great tool for the edge AI community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guides](#style-guides)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by the [SuperInstance.AI Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [conduct@superinstance.ai](mailto:conduct@superinstance.ai).

## Getting Started

### Prerequisites

- Python 3.8 or later
- Git
- A SuperInstance device (for hardware-related contributions)
- Familiarity with LLMs and edge computing concepts

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/superinstance-sdk.git
cd superinstance-sdk
```

3. Add the upstream remote:

```bash
git remote add upstream https://github.com/superinstance-ai/superinstance-sdk.git
```

## How Can I Contribute?

### Report Bugs

Before creating bug reports, please check the existing issues as you might find that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed and expected**
- **Include screenshots or code snippets if relevant**
- **Include your environment details** (OS, Python version, SDK version, device type)

Use the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md).

### Suggest Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and explain the expected behavior**
- **Explain why this enhancement would be useful**
- **List any other tools or applications that have this feature**

Use the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md).

### Improve Documentation

Documentation improvements are always welcome! This includes:

- Fixing typos or inaccuracies
- Adding missing documentation
- Improving code examples
- Writing tutorials or guides

Documentation files are in the `docs/` directory.

### Submit Pull Requests

We welcome pull requests for:

- Bug fixes
- New features
- Documentation improvements
- Code refactoring
- Performance improvements
- Additional test coverage

## Development Setup

### Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs the package in editable mode with development dependencies including:
- `pytest` — Testing framework
- `black` — Code formatter
- `isort` — Import sorter
- `mypy` — Type checker
- `flake8` — Linter
- `sphinx` — Documentation generator

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=superinstance --cov-report=html

# Run specific test file
pytest tests/test_device.py

# Run tests matching a pattern
pytest -k "test_generate"
```

### Code Formatting

```bash
# Format code with black
black superinstance tests

# Sort imports
isort superinstance tests

# Check with flake8
flake8 superinstance tests

# Type check with mypy
mypy superinstance
```

### Build Documentation

```bash
cd docs
make html
# Open docs/_build/html/index.html in your browser
```

## Pull Request Process

### Before Submitting

1. **Sync with upstream**:

```bash
git fetch upstream
git checkout main
git merge upstream/main
```

2. **Create a feature branch**:

```bash
git checkout -b feature/your-feature-name
```

3. **Make your changes** following our [style guides](#style-guides)

4. **Add tests** for any new functionality

5. **Update documentation** if needed

6. **Run the test suite** to ensure all tests pass

7. **Commit your changes** with a clear commit message

### Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `perf`: A code change that improves performance
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

**Examples:**

```
feat(api): add streaming support for chat method

Add generate_stream() method to Model class for real-time
token streaming. This enables responsive UI updates during
generation.

Closes #123
```

```
fix(device): handle device disconnection gracefully

Add proper error handling for unexpected device disconnections.
Previously, the SDK would hang indefinitely. Now raises
DeviceDisconnectedError with reconnection suggestions.

Fixes #456
```

### Submitting

1. Push your branch:

```bash
git push origin feature/your-feature-name
```

2. Open a Pull Request on GitHub

3. Fill out the PR template completely:
   - Description of changes
   - Related issue numbers
   - Type of change (bug fix, feature, docs, etc.)
   - Testing performed
   - Breaking changes if any

4. Wait for review from maintainers

### Review Process

- All PRs require at least one approval from a maintainer
- CI tests must pass
- Code coverage should not decrease
- Documentation must be updated for API changes
- Breaking changes require discussion in an issue first

## Style Guides

### Python Style Guide

We follow [PEP 8](https://peps.python.org/pep-0008/) with some modifications:

- **Line length**: 100 characters (not 79)
- **Quotes**: Double quotes for strings, single quotes for internal strings
- **Imports**: Use `isort` with the following config:

```ini
[settings]
profile = black
line_length = 100
known_first_party = superinstance
```

### Code Organization

```python
# Standard library imports first
import os
import sys
from typing import Optional, List

# Third-party imports
import numpy as np

# Local imports
from superinstance import errors
from superinstance.device import Device
```

### Type Hints

We use type hints throughout the codebase:

```python
def generate(
    self,
    prompt: str,
    config: Optional[GenerationConfig] = None,
) -> GenerationResult:
    """Generate text from prompt.
    
    Args:
        prompt: Input text prompt.
        config: Generation parameters.
        
    Returns:
        GenerationResult with output text and metadata.
        
    Raises:
        ContextLengthExceededError: Prompt exceeds context length.
    """
    ...
```

### Documentation Style

We use Google-style docstrings:

```python
def function(arg1: str, arg2: int) -> bool:
    """Short description of function.
    
    Longer description if needed. Can span multiple lines
    and include examples.
    
    Args:
        arg1: Description of arg1.
        arg2: Description of arg2.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: If arg1 is empty.
        
    Example:
        >>> function("hello", 42)
        True
    """
```

### Testing Style

```python
import pytest
from superinstance import Device, GenerationConfig


class TestModelGeneration:
    """Tests for Model.generate() method."""
    
    @pytest.fixture
    def device(self):
        """Create a Device instance for testing."""
        return Device()
    
    @pytest.fixture
    def model(self, device):
        """Create a Model instance for testing."""
        return device.load_cartridge()
    
    def test_basic_generation(self, model):
        """Test basic text generation."""
        result = model.generate("Hello")
        assert result.text
        assert result.generated_tokens > 0
        
    def test_generation_with_config(self, model):
        """Test generation with custom config."""
        config = GenerationConfig(temperature=0.5, max_tokens=50)
        result = model.generate("Hello", config)
        assert len(result.tokens) <= 50
        
    @pytest.mark.parametrize("temperature", [0.0, 0.5, 1.0, 1.5])
    def test_various_temperatures(self, model, temperature):
        """Test generation with various temperatures."""
        config = GenerationConfig(temperature=temperature)
        result = model.generate("Test", config)
        assert result.text
```

## Project Structure

```
superinstance-sdk/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
├── superinstance/
│   ├── __init__.py
│   ├── device.py
│   ├── model.py
│   ├── config.py
│   ├── profiler.py
│   ├── errors.py
│   └── utils/
├── examples/
│   ├── basic/
│   ├── chat/
│   └── integration/
├── docs/
│   ├── getting-started.md
│   ├── api-reference.md
│   └── examples.md
├── tests/
│   ├── __init__.py
│   ├── test_device.py
│   ├── test_model.py
│   └── test_profiler.py
├── bindings/
│   ├── cpp/
│   ├── rust/
│   └── js/
├── setup.py
├── pyproject.toml
├── requirements-dev.txt
└── README.md
```

## Recognition

Contributors are recognized in several ways:

- **Contributors file**: All contributors are listed in `CONTRIBUTORS.md`
- **Release notes**: Significant contributions mentioned in `CHANGELOG.md`
- **Community spotlight**: Featured in our monthly newsletter
- **Swag**: Active contributors receive SuperInstance swag!

## Community

### Getting Help

- **Discord**: Join our [Discord server](https://discord.gg/superinstance) for real-time help
- **GitHub Discussions**: Ask questions in [Discussions](https://github.com/superinstance-ai/superinstance-sdk/discussions)
- **Stack Overflow**: Use the `superinstance` tag

### Monthly Community Calls

We host monthly community calls on the first Thursday of each month:

- **Time**: 10:00 AM PT / 1:00 PM ET / 6:00 PM UTC
- **Location**: Discord voice channel
- **Agenda**: Roadmap updates, community demos, Q&A

### Office Hours

Core maintainers hold weekly office hours for one-on-one help:

- **Tuesday**: 2:00 PM PT (Developer Advocate)
- **Thursday**: 10:00 AM PT (Engineering Lead)

Check Discord for the calendar link.

---

Thank you for contributing to SuperInstance.AI! 🚀

Questions? Reach out to us at [devrel@superinstance.ai](mailto:devrel@superinstance.ai).
