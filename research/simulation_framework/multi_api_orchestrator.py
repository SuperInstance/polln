#!/usr/bin/env python3
"""
Multi-API Simulation Orchestrator for SuperInstance Research
=============================================================

A comprehensive framework for leveraging multiple AI APIs for:
- Research ideation and hypothesis generation
- Extensive simulation across different model architectures
- Multi-perspective validation of scientific claims
- Cost-effective iteration strategies

APIs Supported:
- DeepInfra: Novel models (Seed, Nemo, etc.) for diverse perspectives
- DeepSeek: Cheap iterations for rapid prototyping
- Moonshoot: High-quality reasoning for critical analysis

Author: SuperInstance Research Team
Version: 1.0
Date: 2026-03-13
"""

import os
import sys
import asyncio
import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hashlib
from pathlib import Path
import aiohttp
from collections import defaultdict

# Add apikey folder to path for config import
script_dir = Path(__file__).parent
api_key_dir = script_dir.parent.parent / "apikey"
sys.path.insert(0, str(api_key_dir))

try:
    from simulation_config import API_KEYS, MODEL_CONFIGS
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("Could not import simulation_config.py - using environment variables only")
    API_KEYS = {}
    MODEL_CONFIGS = {}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Available AI model providers"""
    DEEPINFRA = "deepinfra"
    DEEPSEEK = "deepseek"
    MOONSHOOT = "moonshot"


class ModelCapability(Enum):
    """Model capabilities for routing"""
    LARGE_CONTEXT = "large_context"
    CHEAP_ITERATION = "cheap_iteration"
    NOVEL_ARCHITECTURE = "novel_architecture"
    REASONING = "reasoning"
    FAST_INFERENCE = "fast_inference"
    CREATIVE = "creative"


@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    name: str
    provider: ModelProvider
    api_key: str
    base_url: str
    capabilities: List[ModelCapability]
    max_tokens: int
    cost_per_1k_tokens: float
    context_window: int


@dataclass
class SimulationRequest:
    """A request for simulation"""
    prompt: str
    required_capabilities: List[ModelCapability]
    max_tokens: int = 2000
    temperature: float = 0.7
    models_to_include: Optional[List[str]] = None
    ensemble: bool = False


@dataclass
class SimulationResult:
    """Result from a simulation"""
    model_name: str
    provider: ModelProvider
    response: str
    tokens_used: int
    cost: float
    latency_ms: float
    timestamp: datetime
    quality_score: float = 0.0


@dataclass
class EnsembleResult:
    """Result from ensemble simulation"""
    prompt_hash: str
    results: List[SimulationResult]
    consensus: str
    disagreement_score: float
    confidence: float
    best_response: str


class MultiAPIOrchestrator:
    """
    Main orchestrator for multi-API simulations

    Uses routing logic to select optimal models for each task:
    - Large context tasks -> Kimi/Moonshoot
    - Cheap iterations -> DeepSeek
    - Novel architectures -> DeepInfra (Seed, Nemo)
    - Critical reasoning -> Moonshoot
    """

    def __init__(self, api_keys_file: str = None):
        """Initialize orchestrator with API keys"""
        self.models: Dict[str, ModelConfig] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        self.simulation_history: List[SimulationResult] = []
        self.ensemble_history: Dict[str, EnsembleResult] = {}

        # Load API keys
        if api_keys_file is None:
            api_keys_file = Path(__file__).parent.parent.parent / "apikey" / "apikeys.txt"

        self.api_keys = self._load_api_keys(api_keys_file)
        self._initialize_models()

    def _load_api_keys(self, keys_file: Path) -> Dict[str, str]:
        """Load API keys from config file or environment"""
        # Use the imported config if available
        if API_KEYS:
            logger.info(f"Using imported API config with {len(API_KEYS)} providers")
            return API_KEYS

        # Fallback to environment variables
        keys = {
            "deepinfra": os.getenv("DEEPINFRA_KEY", ""),
            "deepseek": os.getenv("DEEPSEEK_KEY", ""),
            "moonshot": os.getenv("MOONSHOOT_KEY", "")
        }
        logger.info(f"Loaded {len([k for k in keys.values() if k])} API keys from environment")
        return keys

    def _initialize_models(self):
        """Initialize available models from config"""
        if not MODEL_CONFIGS:
            logger.warning("No model configs found - using defaults")
            self._initialize_default_models()
            return

        # Use MODEL_CONFIGS from simulation_config.py
        for provider, config in MODEL_CONFIGS.items():
            provider_enum = ModelProvider[provider.upper()]
            api_key = self.api_keys.get(provider, "")

            for model_key, model_config in config["models"].items():
                capabilities = []
                for cap in model_config["capabilities"]:
                    cap_upper = cap.upper()
                    if cap_upper == "LARGE_CONTEXT":
                        capabilities.append(ModelCapability.LARGE_CONTEXT)
                    elif cap_upper in ["CHEAP", "FAST"]:
                        capabilities.append(ModelCapability.CHEAP_ITERATION)
                    elif cap_upper == "NOVEL":
                        capabilities.append(ModelCapability.NOVEL_ARCHITECTURE)
                    elif cap_upper in ["REASONING", "CODE", "TECHNICAL"]:
                        capabilities.append(ModelCapability.REASONING)
                    elif cap_upper == "CREATIVE":
                        capabilities.append(ModelCapability.CREATIVE)

                model_name = f"{provider}_{model_key}"
                self.models[model_name] = ModelConfig(
                    name=model_config["name"],
                    provider=provider_enum,
                    api_key=api_key,
                    base_url=config["base_url"],
                    capabilities=capabilities,
                    max_tokens=model_config["max_tokens"],
                    cost_per_1k_tokens=model_config["cost_per_1k"],
                    context_window=model_config["context_window"]
                )

        logger.info(f"Initialized {len(self.models)} models from config")

    def _initialize_default_models(self):
        """Fallback default models if config not available"""
        # DeepInfra - Seed (novel architecture)
        self.models["deepinfra_seed"] = ModelConfig(
            name="seed",
            provider=ModelProvider.DEEPINFRA,
            api_key=self.api_keys.get("deepinfra", ""),
            base_url="https://api.deepinfra.com/v1/openai",
            capabilities=[ModelCapability.NOVEL_ARCHITECTURE, ModelCapability.CREATIVE],
            max_tokens=4096,
            cost_per_1k_tokens=0.0001,
            context_window=8192
        )

        # DeepSeek - Cheap iterations
        self.models["deepseek_chat"] = ModelConfig(
            name="deepseek-chat",
            provider=ModelProvider.DEEPSEEK,
            api_key=self.api_keys.get("deepseek", ""),
            base_url="https://api.deepseek.com/v1",
            capabilities=[ModelCapability.CHEAP_ITERATION, ModelCapability.FAST_INFERENCE],
            max_tokens=8192,
            cost_per_1k_tokens=0.0001,
            context_window=64000
        )

        logger.info(f"Initialized {len(self.models)} default models")

    def select_models_for_request(self, request: SimulationRequest) -> List[str]:
        """Select optimal models based on required capabilities"""
        if request.models_to_include:
            return request.models_to_include

        selected = []
        capability_scores = defaultdict(int)

        # Score each model
        for model_name, model in self.models.items():
            score = 0
            for cap in request.required_capabilities:
                if cap in model.capabilities:
                    score += 1
            capability_scores[model_name] = score

        # Select top models
        sorted_models = sorted(
            capability_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Get top 3 or all if ensemble
        count = len(self.models) if request.ensemble else min(3, len(self.models))
        selected = [m[0] for m in sorted_models[:count]]

        return selected

    async def call_model(self, model_name: str, request: SimulationRequest) -> SimulationResult:
        """Call a specific model"""
        model = self.models[model_name]

        headers = {
            "Authorization": f"Bearer {model.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model.name,
            "messages": [{"role": "user", "content": request.prompt}],
            "max_tokens": request.max_tokens,
            "temperature": request.temperature
        }

        start_time = datetime.now()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{model.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        tokens = data.get("usage", {}).get("total_tokens", 0)
                    else:
                        logger.error(f"Error from {model_name}: {response.status}")
                        content = f"Error: {response.status}"
                        tokens = 0
        except Exception as e:
            logger.error(f"Exception calling {model_name}: {e}")
            content = f"Exception: {str(e)}"
            tokens = 0

        latency = (datetime.now() - start_time).total_seconds() * 1000
        cost = (tokens / 1000) * model.cost_per_1k_tokens

        result = SimulationResult(
            model_name=model_name,
            provider=model.provider,
            response=content,
            tokens_used=tokens,
            cost=cost,
            latency_ms=latency,
            timestamp=datetime.now()
        )

        self.simulation_history.append(result)
        return result

    async def simulate(self, request: SimulationRequest) -> List[SimulationResult]:
        """Run simulation with selected models"""
        selected_models = self.select_models_for_request(request)

        tasks = [self.call_model(m, request) for m in selected_models]
        results = await asyncio.gather(*tasks)

        return results

    async def simulate_ensemble(self, request: SimulationRequest) -> EnsembleResult:
        """Run ensemble simulation and aggregate results"""
        request.ensemble = True
        results = await self.simulate(request)

        # Calculate consensus and disagreement
        prompt_hash = hashlib.md5(request.prompt.encode()).hexdigest()[:8]

        # Simple consensus: most common themes
        responses = [r.response for r in results]

        # Aggregate responses
        if len(results) > 1:
            consensus = "\n\n=== ENSEMBLE CONSENSUS ===\n\n"
            consensus += f"Synthesizing {len(results)} model responses:\n\n"

            for i, result in enumerate(results):
                consensus += f"--- {result.model_name} ---\n{result.response[:500]}...\n\n"

            consensus += "\n=== KEY INSIGHTS ===\n"
            # Extract key insights from each response
            insights = []
            for result in results:
                lines = result.response.split('\n')
                insights.extend([l.strip() for l in lines if l.strip() and len(l) < 200])

            # Unique insights
            unique_insights = list(set(insights))[:10]
            for insight in unique_insights:
                consensus += f"• {insight}\n"
        else:
            consensus = results[0].response if results else "No results"

        # Calculate disagreement score (simple version)
        disagreement_score = len(set([r.model_name for r in results])) / max(len(results), 1)

        # Best response by quality score
        best_result = max(results, key=lambda r: r.cost / (r.tokens_used + 1)) if results else None

        ensemble_result = EnsembleResult(
            prompt_hash=prompt_hash,
            results=results,
            consensus=consensus,
            disagreement_score=disagreement_score,
            confidence=1.0 - disagreement_score,
            best_response=best_result.response if best_result else ""
        )

        self.ensemble_history[prompt_hash] = ensemble_result
        return ensemble_result

    def get_simulation_stats(self) -> Dict[str, Any]:
        """Get statistics about simulations run"""
        if not self.simulation_history:
            return {}

        total_cost = sum(r.cost for r in self.simulation_history)
        total_tokens = sum(r.tokens_used for r in self.simulation_history)
        avg_latency = sum(r.latency_ms for r in self.simulation_history) / len(self.simulation_history)

        by_model = defaultdict(lambda: {"count": 0, "cost": 0, "tokens": 0})
        for r in self.simulation_history:
            by_model[r.model_name]["count"] += 1
            by_model[r.model_name]["cost"] += r.cost
            by_model[r.model_name]["tokens"] += r.tokens_used

        return {
            "total_simulations": len(self.simulation_history),
            "total_cost_usd": total_cost,
            "total_tokens": total_tokens,
            "average_latency_ms": avg_latency,
            "by_model": dict(by_model)
        }


class ResearchSimulationSuite:
    """
    Pre-configured simulation suites for research tasks
    """

    def __init__(self, orchestrator: MultiAPIOrchestrator):
        self.orchestrator = orchestrator

    async def hypothesis_generation(self, topic: str, num_hypotheses: int = 10) -> List[str]:
        """Generate research hypotheses using ensemble methods"""
        prompt = f"""Generate {num_hypotheses} novel, testable research hypotheses related to: {topic}

For each hypothesis, provide:
1. A clear, falsifiable claim
2. The theoretical basis
3. A proposed validation method
4. Expected outcomes

Format as a numbered list. Be ambitious but realistic."""

        request = SimulationRequest(
            prompt=prompt,
            required_capabilities=[
                ModelCapability.CREATIVE,
                ModelCapability.REASONING
            ],
            ensemble=True
        )

        result = await self.orchestrator.simulate_ensemble(request)
        return self._extract_hypotheses(result.consensus)

    async def literature_review(self, topic: str) -> str:
        """Generate comprehensive literature review"""
        prompt = f"""Provide a comprehensive literature review on: {topic}

Include:
1. Key papers and breakthroughs
2. Current state of the art
3. Open problems and challenges
4. Research gaps and opportunities

Be thorough and cite specific works where possible."""

        request = SimulationRequest(
            prompt=prompt,
            required_capabilities=[
                ModelCapability.LARGE_CONTEXT,
                ModelCapability.REASONING
            ],
            max_tokens=4000
        )

        results = await self.orchestrator.simulate(request)
        return results[0].response if results else ""

    async def method_synthesis(self, problem: str) -> str:
        """Synthesize methods from multiple perspectives"""
        prompt = f"""Analyze the problem: {problem}

From different perspectives (theoretical, practical, computational, experimental):
1. Identify key challenges
2. Propose solution approaches
3. Compare trade-offs
4. Recommend optimal strategy

Be specific and actionable."""

        request = SimulationRequest(
            prompt=prompt,
            required_capabilities=[
                ModelCapability.REASONING,
                ModelCapability.NOVEL_ARCHITECTURE
            ],
            ensemble=True
        )

        result = await self.orchestrator.simulate_ensemble(request)
        return result.consensus

    async def validation_design(self, claim: str) -> str:
        """Design validation experiment for a claim"""
        prompt = f"""Design a rigorous validation experiment for the claim: {claim}

Include:
1. Experimental setup
2. Control conditions
3. Metrics to measure
4. Statistical power analysis
5. Potential confounds and mitigation
6. Success/failure criteria

Be specific about methodology."""

        request = SimulationRequest(
            prompt=prompt,
            required_capabilities=[
                ModelCapability.REASONING,
                ModelCapability.CHEAP_ITERATION
            ],
            max_tokens=3000
        )

        results = await self.orchestrator.simulate(request)
        return results[0].response if results else ""

    def _extract_hypotheses(self, text: str) -> List[str]:
        """Extract hypotheses from generated text"""
        lines = text.split('\n')
        hypotheses = []
        current_hypothesis = []

        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')):
                if current_hypothesis:
                    hypotheses.append('\n'.join(current_hypothesis))
                current_hypothesis = [line]
            elif current_hypothesis:
                current_hypothesis.append(line)

        if current_hypothesis:
            hypotheses.append('\n'.join(current_hypothesis))

        return hypotheses


async def main():
    """Example usage"""
    orchestrator = MultiAPIOrchestrator()
    suite = ResearchSimulationSuite(orchestrator)

    # Example: Generate hypotheses for a research topic
    topic = "Distributed AI coordination with CRDTs"
    hypotheses = await suite.hypothesis_generation(topic, num_hypotheses=5)

    print(f"Generated {len(hypotheses)} hypotheses for {topic}")
    for i, h in enumerate(hypotheses):
        print(f"\nHypothesis {i+1}:\n{h[:200]}...")

    # Print stats
    stats = orchestrator.get_simulation_stats()
    print(f"\nSimulation Stats: {json.dumps(stats, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
