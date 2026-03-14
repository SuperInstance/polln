# Contributing to SuperInstance

First off, thank you for considering contributing to SuperInstance! 🎉

## Ways to Contribute

- 🐛 **Report bugs** - Use our [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- 💡 **Suggest features** - Use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- 📝 **Improve documentation** - Docs are in the `/docs` folder
- 🔧 **Submit code** - See the development setup below
- 🌍 **Translations** - Help us reach more developers worldwide

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/superinstance-sdk.git
cd superinstance-sdk
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=superinstance

# Run specific test file
pytest tests/test_device.py
```

### 5. Code Style

We use:
- **Black** for code formatting
- **isort** for import sorting
- **mypy** for type checking
- **ruff** for linting

```bash
# Format code
black superinstance tests

# Sort imports
isort superinstance tests

# Type check
mypy superinstance

# Lint
ruff check superinstance
```

## Pull Request Process

1. **Create a branch**: `git checkout -b feature/your-feature-name`
2. **Make changes**: Write code and tests
3. **Run checks**: `pytest && black . && mypy superinstance`
4. **Commit**: Use conventional commits
   ```
   feat: add streaming support for chat API
   fix: resolve device detection on Windows
   docs: update getting started guide
   ```
5. **Push**: `git push origin feature/your-feature-name`
6. **Open PR**: Fill out the PR template

### PR Checklist

- [ ] Tests pass locally
- [ ] Code is formatted with Black
- [ ] Type hints are complete
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.

## Questions?

- 💬 [Discord](https://discord.gg/superinstance)
- 📧 Email: dev@superinstance.ai
- 🐛 [GitHub Issues](https://github.com/superinstance-ai/sdk/issues)

---

Thank you for contributing! 🙌
