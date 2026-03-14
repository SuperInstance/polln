# Multi-API Simulation Replication Guide

**Version:** 1.0
**Date:** 2026-03-13
**Status:** Active

---

## Overview

This guide explains how to use the Multi-API Simulation Framework for research ideation, hypothesis generation, and paper development using multiple AI APIs.

---

## Table of Contents

1. [Setup](#setup)
2. [API Configuration](#api-configuration)
3. [Quick Start](#quick-start)
4. [Advanced Usage](#advanced-usage)
5. [Best Practices](#best-practices)
6. [Cost Management](#cost-management)
7. [Troubleshooting](#troubleshooting)

---

## Setup

### Prerequisites

- Python 3.8+
- pip package manager
- API keys (see API Configuration)

### Installation

```bash
cd research/simulation_framework
pip install -r requirements.txt
```

### Dependencies

- `aiohttp`: Async HTTP client
- `numpy`: Numerical operations
- `pandas`: Data manipulation
- `pydantic`: Data validation

---

## API Configuration

### API Keys Location

API keys are stored in `apikey/simulation_config.py` (git-ignored for security).

### Available APIs

#### DeepInfra (https://deepinfra.com)
- **Models:** Llama 3 70B-Turbo, Qwen 2 72B, Nemo 340B, Mistral 7B
- **Best For:** Novel architectures, large context, diverse perspectives
- **Cost:** $0.00003-$0.0002 per 1K tokens
- **Use When:** Need different architectural perspectives

#### DeepSeek (https://deepseek.com)
- **Models:** DeepSeek-Chat, DeepSeek-Coder
- **Best For:** Cheap iterations, rapid prototyping
- **Cost:** $0.0001 per 1K tokens
- **Use When:** Exploratory research, multiple iterations needed

#### Moonshot (https://moonshot.cn)
- **Models:** Moonshot-v1-8k, Moonshot-v1-32k
- **Best For:** High-quality reasoning, critical analysis
- **Cost:** $0.00012-$0.00024 per 1K tokens
- **Use When:** Need rigorous validation or analysis

### Adding New APIs

Edit `apikey/simulation_config.py`:

```python
MODEL_CONFIGS = {
    "new_provider": {
        "models": {
            "model_name": {
                "name": "actual-model-name",
                "max_tokens": 8192,
                "cost_per_1k": 0.0001,
                "context_window": 32000,
                "capabilities": ["reasoning", "fast"]
            }
        },
        "base_url": "https://api.example.com/v1"
    }
}

API_KEYS = {
    "new_provider": "your-api-key-here"
}
```

---

## Quick Start

### 1. Test Basic Connectivity

```bash
python test_apis.py
```

Expected output:
```
Initialized 8 models from config
Testing model: deepinfra_llama3_70b
Response: [valid response from API]
```

### 2. Run Mini Ideation Test

```bash
python run_mini_ideation.py
```

This runs a quick ensemble simulation across all models.

### 3. Run Full 5-Phase Simulation

```bash
python run_5_phase_simulation.py
```

This executes:
- Phase 1: Model capability assessment
- Phase 2: Research ideation (15 topics)
- Phase 3: Extensive simulation (30 iterations)
- Phase 4: Paper development (5 papers)
- Phase 5: Integration & documentation

---

## Advanced Usage

### Custom Research Topics

Create a custom script:

```python
from multi_api_orchestrator import MultiAPIOrchestrator, SimulationRequest, ModelCapability
import asyncio

async def custom_research():
    orchestrator = MultiAPIOrchestrator()

    request = SimulationRequest(
        prompt="Your research question here",
        required_capabilities=[
            ModelCapability.REASONING,
            ModelCapability.CREATIVE
        ],
        max_tokens=2000,
        ensemble=True  # Use multiple models
    )

    result = await orchestrator.simulate_ensemble(request)
    print(result.consensus)

asyncio.run(custom_research())
```

### Literature Synthesis

```python
from multi_api_orchestrator import ResearchSimulationSuite

suite = ResearchSimulationSuite(orchestrator)
review = await suite.literature_review("CRDT applications in ML")
print(review)
```

### Hypothesis Generation

```python
hypotheses = await suite.hypothesis_generation(
    topic="Distributed AI coordination",
    num_hypotheses=10
)

for h in hypotheses:
    print(f"- {h}")
```

### Method Development

```python
methods = await suite.method_synthesis(
    problem="Validating CRDT performance"
)
print(methods)
```

---

## Best Practices

### 1. Use Appropriate Models

| Task | Recommended Model | Reason |
|------|-------------------|--------|
| Initial exploration | DeepSeek-Chat | Cheap, fast |
| Code generation | DeepSeek-Coder | Specialized |
| Critical analysis | Moonshot-v1 | High quality |
| Novel perspectives | DeepInfra models | Diverse architectures |
| Large context analysis | Nemo 340B | 128K context |

### 2. Ensemble Methods

Use ensemble simulations for:
- Critical research decisions
- Hypothesis validation
- Paper review
- Method selection

### 3. Cost Optimization

- Start with DeepSeek for exploration
- Use ensemble methods sparingly (every 5th simulation)
- Limit max_tokens for initial exploration
- Monitor costs via `orchestrator.get_simulation_stats()`

### 4. Result Management

- Results automatically saved to `results/` directory
- Each simulation run generates timestamped JSON files
- Check results after long runs:
  ```bash
  ls -la results/
  cat results/latest_result.json
  ```

---

## Cost Management

### Estimated Costs (USD)

| Operation | Models | Tokens | Cost |
|-----------|--------|--------|------|
| Mini test | 8 | ~5K | $0.001 |
| Single hypothesis | 1 | ~1K | $0.0001 |
| Ensemble hypothesis | 8 | ~5K | $0.001 |
| Literature review | 1 | ~3K | $0.0003 |
| Full 5-phase | All | ~100K | $0.01 |

### Budget Controls

Edit `apikey/simulation_config.py`:

```python
DAILY_BUDGET = 10.0    # $10 per day
WEEKLY_BUDGET = 50.0   # $50 per week
MONTHLY_BUDGET = 200.0 # $200 per month
```

### Monitoring Costs

```python
stats = orchestrator.get_simulation_stats()
print(f"Total cost: ${stats['total_cost_usd']:.4f}")
print(f"Tokens used: {stats['total_tokens']:,}")
```

---

## Troubleshooting

### Common Issues

#### 1. Import Error: "No module named 'aiohttp'"

**Solution:**
```bash
pip install -r requirements.txt
```

#### 2. API Key Not Found

**Solution:**
- Check `apikey/simulation_config.py` exists
- Verify API keys are set correctly
- Check environment variables

#### 3. 401 Unauthorized

**Solution:**
- Verify API key is valid
- Check API key hasn't expired
- Ensure sufficient credits

#### 4. 404 Model Not Found

**Solution:**
- Verify model name in config
- Check API provider's model list
- Update `simulation_config.py`

#### 5. Slow Response Times

**Solution:**
- Use smaller `max_tokens`
- Try faster models (DeepSeek)
- Reduce ensemble size

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Examples

### Example 1: Generate Research Hypotheses

```python
from multi_api_orchestrator import ResearchSimulationSuite
import asyncio

async def generate_hypotheses():
    suite = ResearchSimulationSuite(orchestrator)
    hypotheses = await suite.hypothesis_generation(
        "CRDT-based distributed training",
        num_hypotheses=5
    )
    for i, h in enumerate(hypotheses, 1):
        print(f"Hypothesis {i}: {h}")

asyncio.run(generate_hypotheses())
```

### Example 2: Validate with Multiple Models

```python
async def multi_model_validation():
    request = SimulationRequest(
        prompt="Critique this hypothesis: [...]",
        required_capabilities=[ModelCapability.REASONING],
        ensemble=True  # All models
    )
    result = await orchestrator.simulate_ensemble(request)
    print(f"Consensus: {result.consensus}")
    print(f"Confidence: {result.confidence}")

asyncio.run(multi_model_validation())
```

### Example 3: Cost-Effective Exploration

```python
async def cheap_exploration():
    # Use only DeepSeek (cheapest)
    request = SimulationRequest(
        prompt="Generate 10 research ideas on X",
        required_capabilities=[ModelCapability.CHEAP_ITERATION],
        models_to_include=["deepseek_deepseek_chat"],
        max_tokens=1000  # Limit tokens
    )
    results = await orchestrator.simulate(request)
    print(results[0].response)

asyncio.run(cheap_exploration())
```

---

## Output Format

### Simulation Result JSON

```json
{
  "timestamp": "20260313_210032",
  "prompt": "...",
  "models_used": ["deepinfra_llama3_70b", "deepseek_deepseek_chat", ...],
  "total_tokens": 4609,
  "total_cost": 0.000421,
  "consensus": "..."
}
```

### Ensemble Result Fields

- `consensus`: Aggregated response from all models
- `confidence`: Agreement level (0-1)
- `disagreement_score`: Diversity of responses (0-1)
- `results`: Individual model responses

---

## Next Steps

1. Run `python test_apis.py` to verify setup
2. Run `python run_mini_ideation.py` for quick test
3. Customize `run_5_phase_simulation.py` for your research
4. Check `results/` directory for outputs
5. Monitor costs with `orchestrator.get_simulation_stats()`

---

## Support

For issues or questions:
- Check this guide first
- Review code comments in `multi_api_orchestrator.py`
- Examine example scripts in `simulation_framework/`

---

**Last Updated:** 2026-03-13
**Framework Version:** 1.0
