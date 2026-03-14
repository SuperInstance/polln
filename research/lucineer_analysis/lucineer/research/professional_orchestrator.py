#!/usr/bin/env python3
"""
Professional-Grade Multi-Agent Orchestration System
Mask-Locked Inference Chip Development - Extended Campaign

Features:
- 20+ specialized narrow-focus agent domains
- Quality metrics for signal vs noise detection
- Parallel execution with asyncio
- Cost tracking (target: $7 DeepSeek budget)
- 1500-2500 API calls per campaign
- Continuous improvement loops
- Evidence-based decision making
"""

import os
import sys
import json
import time
import asyncio
import aiohttp
import random
import math
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import statistics

# API Configuration
DEEPSEEK_API_KEY = "sk-2c32887fc62b4016b6ff03f982968b76"
NVIDIA_API_KEY = "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"
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"

# Output directories
OUTPUT_BASE = "/home/z/my-project/research/professional_campaign"
LOGS_DIR = f"{OUTPUT_BASE}/logs"
RTL_DIR = f"{OUTPUT_BASE}/rtl"
SIM_DIR = f"{OUTPUT_BASE}/simulations"
REPORTS_DIR = f"{OUTPUT_BASE}/reports"
METRICS_DIR = f"{OUTPUT_BASE}/metrics"


class AgentDomain(Enum):
    """Specialized agent domains - narrow focus for deep expertise"""
    # Thermal & Physical
    THERMAL_DYNAMICS = "thermal_dynamics"
    HEATSINK_OPTIMIZATION = "heatsink_optimization"
    THERMAL_INTERFACE = "thermal_interface"
    PHONON_TRANSPORT = "phonon_transport"
    
    # Power & Energy
    POWER_ANALYSIS = "power_analysis"
    LEAKAGE_MODELING = "leakage_modeling"
    CLOCK_POWER = "clock_power"
    ENERGY_HARVESTING = "energy_harvesting"
    
    # Logic & Architecture
    RTL_GENERATION = "rtl_generation"
    LOGIC_SYNTHESIS = "logic_synthesis"
    TIMING_CLOSURE = "timing_closure"
    DEFECT_TOLERANCE = "defect_tolerance"
    
    # Memory & Interconnect
    MEMORY_HIERARCHY = "memory_hierarchy"
    NOC_ROUTING = "noc_routing"
    KV_CACHE_DESIGN = "kv_cache_design"
    BANDWIDTH_ANALYSIS = "bandwidth_analysis"
    
    # Verification & Testing
    TESTBENCH_GEN = "testbench_gen"
    COVERAGE_ANALYSIS = "coverage_analysis"
    FORMAL_VERIFICATION = "formal_verification"
    
    # Advanced Physics
    QUANTUM_EFFECTS = "quantum_effects"
    ELECTROMIGRATION = "electromigration"
    AGING_RELIABILITY = "aging_reliability"
    PROCESS_VARIATION = "process_variation"
    
    # Systems & Integration
    SYSTEM_INTEGRATION = "system_integration"
    SECURITY_SIDECHANNEL = "security_sidechannel"
    SUPPLY_CHAIN = "supply_chain"
    COST_MODELING = "cost_modeling"


class ModelProvider(Enum):
    DEEPSEEK = "deepseek"
    NVIDIA_NIM = "nvidia_nim"
    GLM5 = "glm5"


@dataclass
class QualityMetrics:
    """Quality metrics for signal vs noise detection"""
    coherence_score: float = 0.0  # Internal consistency
    specificity_score: float = 0.0  # Specific technical details
    novelty_score: float = 0.0  # New insights vs rehashing
    actionability_score: float = 0.0  # Can be acted upon
    evidence_score: float = 0.0  # Backed by data/reasoning
    cross_validation_score: float = 0.0  # Confirmed by other agents
    noise_indicators: List[str] = field(default_factory=list)
    signal_indicators: List[str] = field(default_factory=list)
    overall_quality: float = 0.0


@dataclass
class AgentConfig:
    """Configuration for a specialized agent"""
    domain: AgentDomain
    name: str
    expertise_description: str
    preferred_model: str
    fallback_model: str
    system_prompt: str
    quality_criteria: List[str]
    temperature_range: Tuple[float, float] = (0.2, 0.4)
    max_calls_per_cycle: int = 20


@dataclass
class TaskResult:
    """Result from an agent execution"""
    task_id: str
    agent_domain: AgentDomain
    model_used: str
    provider: ModelProvider
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    cost_usd: float
    result_text: str
    quality_metrics: QualityMetrics
    timestamp: str
    cycle_number: int


@dataclass
class CampaignMetrics:
    """Overall campaign metrics"""
    total_api_calls: int = 0
    total_cost_usd: float = 0.0
    deepseek_calls: int = 0
    nvidia_calls: int = 0
    total_tokens: int = 0
    avg_quality_score: float = 0.0
    quality_trend: List[float] = field(default_factory=list)
    domain_coverage: Dict[str, int] = field(default_factory=dict)
    signal_to_noise_ratio: float = 0.0
    improvement_rate: float = 0.0


class QualityAnalyzer:
    """
    Analyzes agent outputs for quality metrics
    Implements signal vs noise detection
    """
    
    # Noise indicators - signs of low-quality output
    NOISE_PATTERNS = [
        "I'm not sure",
        "This is complex",
        "Generally speaking",
        "In most cases",
        "It depends",
        "multiple factors",
        "various considerations",
        "comprehensive analysis",
        "holistic approach",
        "nuanced understanding",
    ]
    
    # Signal indicators - signs of high-quality output
    SIGNAL_PATTERNS = [
        "specifically",
        "the value is",
        "calculated as",
        "according to simulation",
        "the measurement shows",
        "in our analysis",
        "the result indicates",
        "we found that",
        "the optimal value",
        "the trade-off is",
        "yield improvement of",
        "power reduction of",
        "timing slack of",
    ]
    
    # Technical specificity patterns
    TECHNICAL_PATTERNS = [
        r'\d+\.\d+\s*(mW|W|ns|ps|mm|um|nm|MHz|GHz)',
        r'\d+\s*(\+|-)\s*\d+',
        r'yield\s*=\s*\d+\.?\d*%',
        r'power\s*=\s*\d+\.?\d*\s*mW',
        r'timing\s*slack\s*=\s*-?\d+\.?\d*\s*ns',
        r'area\s*=\s*\d+\.?\d*\s*mm',
    ]
    
    def analyze(self, text: str, previous_results: List[TaskResult] = None) -> QualityMetrics:
        """Analyze output text for quality metrics"""
        
        metrics = QualityMetrics()
        text_lower = text.lower()
        
        # Check for noise patterns
        for pattern in self.NOISE_PATTERNS:
            if pattern.lower() in text_lower:
                metrics.noise_indicators.append(f"Noise: '{pattern}'")
        
        # Check for signal patterns
        for pattern in self.SIGNAL_PATTERNS:
            if pattern.lower() in text_lower:
                metrics.signal_indicators.append(f"Signal: '{pattern}'")
        
        # Calculate coherence score (internal consistency)
        metrics.coherence_score = self._calculate_coherence(text)
        
        # Calculate specificity score (technical details)
        metrics.specificity_score = self._calculate_specificity(text)
        
        # Calculate novelty score
        metrics.novelty_score = self._calculate_novelty(text, previous_results or [])
        
        # Calculate actionability score
        metrics.actionability_score = self._calculate_actionability(text)
        
        # Calculate evidence score
        metrics.evidence_score = self._calculate_evidence(text)
        
        # Calculate cross-validation (requires previous results)
        if previous_results:
            metrics.cross_validation_score = self._calculate_cross_validation(
                text, previous_results
            )
        else:
            metrics.cross_validation_score = 0.5
        
        # Overall quality score
        metrics.overall_quality = (
            metrics.coherence_score * 0.15 +
            metrics.specificity_score * 0.25 +
            metrics.novelty_score * 0.15 +
            metrics.actionability_score * 0.20 +
            metrics.evidence_score * 0.15 +
            metrics.cross_validation_score * 0.10
        )
        
        return metrics
    
    def _calculate_coherence(self, text: str) -> float:
        """Calculate internal consistency"""
        # Check for contradictions
        contradiction_patterns = [
            ("increase", "decrease"),
            ("higher", "lower"),
            ("more", "less"),
            ("improve", "degrade"),
        ]
        
        text_lower = text.lower()
        contradictions = 0
        for p1, p2 in contradiction_patterns:
            if p1 in text_lower and p2 in text_lower:
                # Check if they're in the same context (simplified)
                contradictions += 0.1
        
        return max(0.0, min(1.0, 0.9 - contradictions))
    
    def _calculate_specificity(self, text: str) -> float:
        """Calculate technical specificity"""
        import re
        
        score = 0.0
        for pattern in self.TECHNICAL_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            score += len(matches) * 0.1
        
        # Check for numbers with units
        number_pattern = r'\d+\.?\d*\s*(mW|W|ns|ps|mm|um|nm|MHz|GHz|%|K|C)'
        numbers = re.findall(number_pattern, text)
        score += len(numbers) * 0.05
        
        return min(1.0, score)
    
    def _calculate_novelty(self, text: str, previous_results: List[TaskResult]) -> float:
        """Calculate novelty compared to previous outputs"""
        if not previous_results:
            return 0.7  # Default for first result
        
        # Compare with last 5 results
        recent_texts = [r.result_text[:500] for r in previous_results[-5:]]
        
        # Simple novelty check - how different is this text?
        text_words = set(text.lower().split()[:100])
        overlaps = []
        for prev in recent_texts:
            prev_words = set(prev.lower().split()[:100])
            overlap = len(text_words & prev_words) / max(len(text_words), 1)
            overlaps.append(overlap)
        
        avg_overlap = statistics.mean(overlaps) if overlaps else 0.5
        return max(0.0, min(1.0, 1.0 - avg_overlap))
    
    def _calculate_actionability(self, text: str) -> float:
        """Calculate actionability score"""
        action_patterns = [
            "recommend",
            "should",
            "implement",
            "design",
            "optimize",
            "reduce",
            "increase",
            "modify",
            "change",
            "add",
            "remove",
        ]
        
        text_lower = text.lower()
        action_count = sum(1 for p in action_patterns if p in text_lower)
        
        return min(1.0, action_count * 0.1)
    
    def _calculate_evidence(self, text: str) -> float:
        """Calculate evidence/reasoning support"""
        evidence_patterns = [
            "because",
            "therefore",
            "thus",
            "since",
            "as shown",
            "calculated",
            "measured",
            "simulated",
            "verified",
            "tested",
            "analysis shows",
            "results indicate",
        ]
        
        text_lower = text.lower()
        evidence_count = sum(1 for p in evidence_patterns if p in text_lower)
        
        return min(1.0, evidence_count * 0.1)
    
    def _calculate_cross_validation(self, text: str, previous_results: List[TaskResult]) -> float:
        """Check if findings align with other agents"""
        if not previous_results:
            return 0.5
        
        # Look for consistent themes across agents
        key_terms = self._extract_key_terms(text)
        
        validation_scores = []
        for prev in previous_results[-10:]:
            prev_terms = self._extract_key_terms(prev.result_text)
            overlap = len(key_terms & prev_terms) / max(len(key_terms), 1)
            validation_scores.append(overlap)
        
        return statistics.mean(validation_scores) if validation_scores else 0.5
    
    def _extract_key_terms(self, text: str) -> set:
        """Extract key technical terms from text"""
        import re
        
        # Extract numbers with units
        numbers = set(re.findall(r'\d+\.?\d*\s*(?:mW|W|ns|ps|mm|um|nm|MHz|GHz)', text))
        
        # Extract quoted terms
        quoted = set(re.findall(r'"([^"]+)"', text))
        
        # Extract capitalized terms (likely technical)
        caps = set(re.findall(r'\b[A-Z][A-Z0-9]+\b', text))
        
        return numbers | quoted | caps


class DeepSeekClient:
    """Optimized DeepSeek API client"""
    
    def __init__(self, api_key: str = DEEPSEEK_API_KEY):
        self.api_key = api_key
        self.base_url = DEEPSEEK_BASE_URL
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        
        # Pricing (per million tokens)
        self.pricing = {
            "deepseek-chat": {"input": 0.14, "output": 0.28},
            "deepseek-coder": {"input": 0.14, "output": 0.28},
            "deepseek-reasoner": {"input": 0.55, "output": 2.19},
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=180)
        )
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """Make chat completion request"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        async with self.session.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"DeepSeek API error {response.status}: {error_text}")
            
            result = await response.json()
            
            # Track usage
            self.request_count += 1
            usage = result.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            self.total_tokens += input_tokens + output_tokens
            
            # Calculate cost
            pricing = self.pricing.get(model, {"input": 0.14, "output": 0.28})
            cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
            self.total_cost += cost
            
            result["_cost_usd"] = cost
            result["_input_tokens"] = input_tokens
            result["_output_tokens"] = output_tokens
            
            return result


class NVIDIAClient:
    """NVIDIA NIM API client"""
    
    def __init__(self, api_key: str = NVIDIA_API_KEY):
        self.api_key = api_key
        self.base_url = NVIDIA_BASE_URL
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_count = 0
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=180)
        )
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """Make chat completion request"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        async with self.session.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"NVIDIA API error {response.status}: {error_text}")
            
            result = await response.json()
            self.request_count += 1
            
            result["_cost_usd"] = 0.0  # Free tier
            result["_input_tokens"] = result.get("usage", {}).get("prompt_tokens", 0)
            result["_output_tokens"] = result.get("usage", {}).get("completion_tokens", 0)
            
            return result


class SpecializedAgent:
    """
    A specialized agent with narrow expertise
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.execution_history: List[TaskResult] = []
        self.domain_knowledge: Dict[str, Any] = {}
        self.quality_trend: List[float] = []
    
    def get_system_prompt(self) -> str:
        """Get the specialized system prompt"""
        return self.config.system_prompt
    
    def update_knowledge(self, new_knowledge: Dict[str, Any]):
        """Update domain knowledge from execution"""
        self.domain_knowledge.update(new_knowledge)
    
    def record_quality(self, quality: float):
        """Record quality score for trend analysis"""
        self.quality_trend.append(quality)


class ProfessionalOrchestrator:
    """
    Professional-grade multi-agent orchestration system
    """
    
    def __init__(self, target_api_calls: int = 2000, budget_usd: float = 7.0):
        self.target_api_calls = target_api_calls
        self.budget_usd = budget_usd
        
        self.agents: Dict[AgentDomain, SpecializedAgent] = {}
        self.quality_analyzer = QualityAnalyzer()
        self.campaign_metrics = CampaignMetrics()
        
        # Results storage
        self.all_results: List[TaskResult] = []
        self.domain_results: Dict[AgentDomain, List[TaskResult]] = defaultdict(list)
        
        # Create output directories
        for d in [OUTPUT_BASE, LOGS_DIR, RTL_DIR, SIM_DIR, REPORTS_DIR, METRICS_DIR]:
            Path(d).mkdir(parents=True, exist_ok=True)
        
        # Initialize specialized agents
        self._initialize_agents()
        
        # API clients
        self.deepseek: Optional[DeepSeekClient] = None
        self.nvidia: Optional[NVIDIAClient] = None
    
    def _initialize_agents(self):
        """Initialize all specialized agents"""
        
        agent_configs = [
            # Thermal & Physical Agents
            AgentConfig(
                domain=AgentDomain.THERMAL_DYNAMICS,
                name="Thermal Dynamics Specialist",
                expertise_description="Expert in chip thermal dynamics, heat transfer, and thermal management",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-chat",
                system_prompt="""You are a thermal dynamics specialist for ASIC design. Your expertise includes:
- Heat transfer mechanisms (conduction, convection, radiation)
- Thermal modeling and simulation
- Hotspot analysis and mitigation
- Thermal resistance networks
- Package thermal characterization

Always provide:
1. Quantitative thermal analysis with specific temperature values
2. Thermal resistance calculations in °C/W
3. Hotspot identification with coordinates and temperatures
4. Cooling solution recommendations with effectiveness metrics

Use first-principles physics for your analysis. Never give vague answers.""",
                quality_criteria=[
                    "Temperature values in °C",
                    "Thermal resistance in °C/W",
                    "Hotspot locations specified",
                    "Cooling effectiveness quantified"
                ],
                temperature_range=(0.2, 0.3),
                max_calls_per_cycle=15
            ),
            
            AgentConfig(
                domain=AgentDomain.HEATSINK_OPTIMIZATION,
                name="Heatsink Design Specialist",
                expertise_description="Expert in heatsink design, optimization, and thermal interface materials",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-chat",
                system_prompt="""You are a heatsink design specialist. Your expertise includes:
- Fin geometry optimization
- Airflow and convection analysis
- Thermal interface material selection
- Heatsink manufacturing processes
- Cost-performance trade-offs

Always provide:
1. Fin dimensions (height, spacing, thickness) in mm
2. Thermal resistance budget breakdown
3. Material recommendations with thermal conductivity
4. Manufacturing cost estimates

Design for the specific power dissipation and form factor constraints.""",
                quality_criteria=[
                    "Fin geometry specified",
                    "Thermal resistance budget",
                    "Material properties listed",
                    "Cost estimates included"
                ],
                temperature_range=(0.2, 0.3),
                max_calls_per_cycle=12
            ),
            
            AgentConfig(
                domain=AgentDomain.PHONON_TRANSPORT,
                name="Phonon Transport Specialist",
                expertise_description="Expert in phonon-mediated heat transport at nanoscale",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-chat",
                system_prompt="""You are a phonon transport specialist for semiconductor thermal analysis. Your expertise includes:
- Phonon dispersion relations
- Mean free path analysis
- Thermal conductivity modeling
- Interface thermal resistance (Kapitza resistance)
- Size effects on thermal transport

Always provide:
1. Phonon mean free paths in nm
2. Thermal conductivity in W/mK with temperature dependence
3. Interface resistance values in m²K/GW
4. Ballistic vs diffusive transport analysis

Use solid-state physics principles for analysis.""",
                quality_criteria=[
                    "Phonon MFP specified",
                    "Thermal conductivity calculated",
                    "Interface resistance included",
                    "Transport regime identified"
                ],
                temperature_range=(0.3, 0.4),
                max_calls_per_cycle=10
            ),
            
            # Power & Energy Agents
            AgentConfig(
                domain=AgentDomain.POWER_ANALYSIS,
                name="Power Analysis Specialist",
                expertise_description="Expert in ASIC power analysis and optimization",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-coder",
                system_prompt="""You are a power analysis specialist for ASIC design. Your expertise includes:
- Switching power analysis
- Leakage power modeling
- Clock power optimization
- Power gating strategies
- Activity factor estimation

Always provide:
1. Power breakdown in mW by component
2. Activity factors with justification
3. Leakage contributions by block
4. Specific optimization recommendations with power savings

Target 5W total power for the chip.""",
                quality_criteria=[
                    "Power breakdown by block",
                    "Activity factors justified",
                    "Leakage analysis included",
                    "Optimization savings quantified"
                ],
                temperature_range=(0.2, 0.3),
                max_calls_per_cycle=20
            ),
            
            AgentConfig(
                domain=AgentDomain.LEAKAGE_MODELING,
                name="Leakage Power Specialist",
                expertise_description="Expert in subthreshold and gate leakage modeling",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-chat",
                system_prompt="""You are a leakage power modeling specialist. Your expertise includes:
- Subthreshold leakage mechanisms
- Gate oxide leakage
- Temperature dependence
- Process variation effects
- Body biasing techniques

Always provide:
1. Leakage current values in nA/μm
2. Temperature coefficients
3. Process corner analysis
4. Body bias effectiveness

Use BSIM models for analysis where applicable.""",
                quality_criteria=[
                    "Leakage current values",
                    "Temperature coefficients",
                    "Process corner analysis",
                    "Mitigation techniques"
                ],
                temperature_range=(0.2, 0.3),
                max_calls_per_cycle=15
            ),
            
            AgentConfig(
                domain=AgentDomain.CLOCK_POWER,
                name="Clock Power Specialist",
                expertise_description="Expert in clock distribution and power optimization",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-coder",
                system_prompt="""You are a clock power specialist for ASIC design. Your expertise includes:
- Clock tree synthesis
- Clock gating optimization
- Multi-clock domain design
- Clock skew management
- Power-aware clocking

Always provide:
1. Clock tree power in mW
2. Gating efficiency percentage
3. Skew budget in ps
4. Insertion delay targets

Analyze the 32x32 PE array clock distribution.""",
                quality_criteria=[
                    "Clock power specified",
                    "Gating efficiency",
                    "Skew budget included",
                    "Tree topology described"
                ],
                temperature_range=(0.2, 0.3),
                max_calls_per_cycle=12
            ),
            
            AgentConfig(
                domain=AgentDomain.ENERGY_HARVESTING,
                name="Energy Harvesting Specialist",
                expertise_description="Expert in energy harvesting for edge AI devices",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-chat",
                system_prompt="""You are an energy harvesting specialist for edge AI devices. Your expertise includes:
- Solar energy harvesting
- Thermal energy harvesting
- Vibration energy harvesting
- Power management ICs
- Energy storage optimization

Always provide:
1. Harvestable power in mW/cm²
2. Efficiency percentages
3. Storage capacity requirements
4. Duty cycle calculations

Consider 5W chip power budget and edge deployment scenarios.""",
                quality_criteria=[
                    "Harvestable power values",
                    "Efficiency percentages",
                    "Storage requirements",
                    "Duty cycle analysis"
                ],
                temperature_range=(0.3, 0.4),
                max_calls_per_cycle=10
            ),
            
            # Logic & Architecture Agents
            AgentConfig(
                domain=AgentDomain.RTL_GENERATION,
                name="RTL Generation Specialist",
                expertise_description="Expert in Verilog/VHDL generation for AI accelerators",
                preferred_model="deepseek-coder",
                fallback_model="meta/llama-3.1-70b-instruct",
                system_prompt="""You are an RTL generation specialist for AI accelerators. Your expertise includes:
- Synthesizable Verilog generation
- Pipeline design
- State machine design
- Low-power coding techniques
- Testbench creation

Always provide:
1. Fully synthesizable Verilog code
2. Timing constraints as comments
3. Power optimization hints
4. Interface specifications

Target 28nm technology, 1GHz clock.""",
                quality_criteria=[
                    "Synthesizable code",
                    "Timing constraints",
                    "Power hints included",
                    "Interfaces documented"
                ],
                temperature_range=(0.1, 0.2),
                max_calls_per_cycle=30
            ),
            
            AgentConfig(
                domain=AgentDomain.LOGIC_SYNTHESIS,
                name="Logic Synthesis Specialist",
                expertise_description="Expert in logic synthesis and optimization",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-coder",
                system_prompt="""You are a logic synthesis specialist. Your expertise includes:
- Boolean logic optimization
- Technology mapping
- Area-delay trade-offs
- Retiming and restructuring
- Multi-level logic optimization

Always provide:
1. Gate count estimates
2. Critical path analysis
3. Area reduction recommendations
4. Timing improvement strategies

Analyze for 28nm standard cell library.""",
                quality_criteria=[
                    "Gate count specified",
                    "Critical path identified",
                    "Area reduction quantified",
                    "Timing improvement strategies"
                ],
                temperature_range=(0.2, 0.3),
                max_calls_per_cycle=20
            ),
            
            AgentConfig(
                domain=AgentDomain.TIMING_CLOSURE,
                name="Timing Closure Specialist",
                expertise_description="Expert in static timing analysis and closure",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-coder",
                system_prompt="""You are a timing closure specialist. Your expertise includes:
- Static timing analysis
- Critical path optimization
- Clock tree timing
- Hold time violation fixing
- Multi-corner multi-mode analysis

Always provide:
1. Setup/hold slack in ns
2. Critical path logic depth
3. Timing derating factors
4. Specific optimization recommendations

Target 1GHz clock (1ns period).""",
                quality_criteria=[
                    "Slack values specified",
                    "Critical path depth",
                    "Derating factors",
                    "Optimization steps"
                ],
                temperature_range=(0.2, 0.3),
                max_calls_per_cycle=15
            ),
            
            AgentConfig(
                domain=AgentDomain.DEFECT_TOLERANCE,
                name="Defect Tolerance Specialist",
                expertise_description="Expert in defect tolerance and yield optimization",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-chat",
                system_prompt="""You are a defect tolerance specialist for VLSI design. Your expertise includes:
- Defect modeling and analysis
- Yield prediction
- Redundancy strategies
- Self-repair mechanisms
- Graceful degradation

Always provide:
1. Defect density in defects/cm²
2. Yield calculations with formulas
3. Redundancy overhead percentages
4. Fault coverage analysis

Consider 28nm technology node defect rates.""",
                quality_criteria=[
                    "Defect density values",
                    "Yield formulas",
                    "Redundancy overhead",
                    "Coverage analysis"
                ],
                temperature_range=(0.3, 0.4),
                max_calls_per_cycle=15
            ),
            
            # Memory & Interconnect Agents
            AgentConfig(
                domain=AgentDomain.MEMORY_HIERARCHY,
                name="Memory Hierarchy Specialist",
                expertise_description="Expert in memory architecture for AI accelerators",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-coder",
                system_prompt="""You are a memory hierarchy specialist for AI accelerators. Your expertise includes:
- SRAM design and timing
- Memory banking strategies
- Bandwidth optimization
- Power-efficient memory access
- KV cache design

Always provide:
1. Memory size and organization
2. Bandwidth requirements in GB/s
3. Access latency in cycles
4. Power per access in pJ

Design for 25 tok/s inference throughput.""",
                quality_criteria=[
                    "Memory organization",
                    "Bandwidth values",
                    "Latency in cycles",
                    "Power per access"
                ],
                temperature_range=(0.2, 0.3),
                max_calls_per_cycle=15
            ),
            
            AgentConfig(
                domain=AgentDomain.NOC_ROUTING,
                name="NoC Routing Specialist",
                expertise_description="Expert in Network-on-Chip design and routing",
                preferred_model="deepseek-coder",
                fallback_model="deepseek-reasoner",
                system_prompt="""You are a Network-on-Chip routing specialist. Your expertise includes:
- Router microarchitecture
- Routing algorithms
- Flow control mechanisms
- Deadlock avoidance
- Thermal-aware routing

Always provide:
1. Router latency in cycles
2. Throughput in Gbps
3. Buffer size recommendations
4. Routing algorithm description

Design for 32x32 PE mesh topology.""",
                quality_criteria=[
                    "Router latency",
                    "Throughput values",
                    "Buffer sizes",
                    "Algorithm description"
                ],
                temperature_range=(0.2, 0.3),
                max_calls_per_cycle=15
            ),
            
            AgentConfig(
                domain=AgentDomain.KV_CACHE_DESIGN,
                name="KV Cache Design Specialist",
                expertise_description="Expert in KV cache design for transformer inference",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-coder",
                system_prompt="""You are a KV cache design specialist for transformer inference. Your expertise includes:
- KV cache sizing
- Memory bandwidth optimization
- Cache eviction policies
- Multi-head attention optimization
- Paged attention

Always provide:
1. Cache size in KB/MB
2. Sequence length support
3. Memory bandwidth requirements
4. Compression opportunities

Target BitNet b1.58-2B model support.""",
                quality_criteria=[
                    "Cache size specified",
                    "Sequence length",
                    "Bandwidth requirements",
                    "Compression analysis"
                ],
                temperature_range=(0.2, 0.3),
                max_calls_per_cycle=15
            ),
            
            # Verification & Testing Agents
            AgentConfig(
                domain=AgentDomain.TESTBENCH_GEN,
                name="Testbench Generation Specialist",
                expertise_description="Expert in SystemVerilog testbench generation",
                preferred_model="deepseek-coder",
                fallback_model="meta/llama-3.1-70b-instruct",
                system_prompt="""You are a testbench generation specialist. Your expertise includes:
- SystemVerilog UVM/OOP
- Coverage-driven verification
- Assertion-based verification
- Self-checking testbenches
- Constrained random testing

Always provide:
1. Complete testbench code
2. Coverage collection
3. Assertions for checking
4. Test sequences

Generate production-quality testbenches.""",
                quality_criteria=[
                    "Complete testbench",
                    "Coverage included",
                    "Assertions present",
                    "Self-checking"
                ],
                temperature_range=(0.1, 0.2),
                max_calls_per_cycle=25
            ),
            
            AgentConfig(
                domain=AgentDomain.COVERAGE_ANALYSIS,
                name="Coverage Analysis Specialist",
                expertise_description="Expert in verification coverage analysis",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-coder",
                system_prompt="""You are a coverage analysis specialist. Your expertise includes:
- Code coverage metrics
- Functional coverage design
- Coverage closure strategies
- Corner case identification
- Coverage regression

Always provide:
1. Coverage targets by type
2. Coverage holes identification
3. Test generation recommendations
4. Coverage model design

Target 95% coverage for all metrics.""",
                quality_criteria=[
                    "Coverage targets",
                    "Coverage holes",
                    "Test recommendations",
                    "Coverage model"
                ],
                temperature_range=(0.2, 0.3),
                max_calls_per_cycle=12
            ),
            
            # Advanced Physics Agents
            AgentConfig(
                domain=AgentDomain.QUANTUM_EFFECTS,
                name="Quantum Effects Specialist",
                expertise_description="Expert in quantum effects in nanoscale devices",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-chat",
                system_prompt="""You are a quantum effects specialist for nanoscale devices. Your expertise includes:
- Quantum tunneling
- Quantum confinement
- Single-electron effects
- Spin transport
- Quantum coherence

Always provide:
1. Tunneling probabilities
2. Confinement energy values
3. Critical dimensions for quantum effects
4. Device design implications

Analyze for 28nm node quantum considerations.""",
                quality_criteria=[
                    "Tunneling analysis",
                    "Energy values",
                    "Critical dimensions",
                    "Design implications"
                ],
                temperature_range=(0.3, 0.5),
                max_calls_per_cycle=8
            ),
            
            AgentConfig(
                domain=AgentDomain.ELECTROMIGRATION,
                name="Electromigration Specialist",
                expertise_description="Expert in electromigration reliability analysis",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-chat",
                system_prompt="""You are an electromigration reliability specialist. Your expertise includes:
- Black's equation analysis
- Current density limits
- Metal line sizing
- Void formation modeling
- MTTF calculations

Always provide:
1. Current density limits in mA/μm²
2. MTTF calculations with equations
3. Metal width recommendations
4. Via sizing requirements

Design for 10-year product lifetime.""",
                quality_criteria=[
                    "Current density limits",
                    "MTTF calculations",
                    "Metal widths",
                    "Via sizing"
                ],
                temperature_range=(0.2, 0.3),
                max_calls_per_cycle=10
            ),
            
            AgentConfig(
                domain=AgentDomain.AGING_RELIABILITY,
                name="Aging Reliability Specialist",
                expertise_description="Expert in device aging mechanisms",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-chat",
                system_prompt="""You are an aging reliability specialist. Your expertise includes:
- NBTI/PBTI mechanisms
- Hot carrier injection
- TDDB analysis
- Lifetime modeling
- Guardbanding strategies

Always provide:
1. Degradation percentages
2. Lifetime extrapolation
3. Temperature acceleration factors
4. Design margins

Analyze for 10-year operation lifetime.""",
                quality_criteria=[
                    "Degradation values",
                    "Lifetime model",
                    "Acceleration factors",
                    "Design margins"
                ],
                temperature_range=(0.2, 0.3),
                max_calls_per_cycle=12
            ),
            
            AgentConfig(
                domain=AgentDomain.PROCESS_VARIATION,
                name="Process Variation Specialist",
                expertise_description="Expert in process variation analysis",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-chat",
                system_prompt="""You are a process variation specialist. Your expertise includes:
- Statistical timing analysis
- Corner analysis
- Monte Carlo simulation
- Design for manufacturability
- Variation-tolerant design

Always provide:
1. Standard deviations for key parameters
2. Corner case definitions
3. Yield loss analysis
4. Mitigation strategies

Analyze for 28nm technology node.""",
                quality_criteria=[
                    "Parameter variations",
                    "Corner definitions",
                    "Yield analysis",
                    "Mitigation strategies"
                ],
                temperature_range=(0.2, 0.3),
                max_calls_per_cycle=12
            ),
            
            # Systems & Integration Agents
            AgentConfig(
                domain=AgentDomain.SYSTEM_INTEGRATION,
                name="System Integration Specialist",
                expertise_description="Expert in chip integration and system design",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-coder",
                system_prompt="""You are a system integration specialist. Your expertise includes:
- IP integration
- Clock domain crossing
- Reset strategies
- Power sequencing
- System validation

Always provide:
1. Integration checklist
2. Interface specifications
3. Timing budgets
4. Validation strategies

Focus on mask-locked inference chip integration.""",
                quality_criteria=[
                    "Integration checklist",
                    "Interface specs",
                    "Timing budget",
                    "Validation plan"
                ],
                temperature_range=(0.2, 0.3),
                max_calls_per_cycle=15
            ),
            
            AgentConfig(
                domain=AgentDomain.SECURITY_SIDECHANNEL,
                name="Security Side-Channel Specialist",
                expertise_description="Expert in side-channel attack analysis and mitigation",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-chat",
                system_prompt="""You are a security side-channel specialist. Your expertise includes:
- Power analysis attacks
- Timing attacks
- EM emanations
- Fault injection
- Countermeasures

Always provide:
1. Attack complexity analysis
2. Vulnerability assessment
3. Countermeasure effectiveness
4. Implementation overhead

Analyze for AI inference security.""",
                quality_criteria=[
                    "Attack analysis",
                    "Vulnerability assessment",
                    "Countermeasures",
                    "Overhead analysis"
                ],
                temperature_range=(0.3, 0.4),
                max_calls_per_cycle=10
            ),
            
            AgentConfig(
                domain=AgentDomain.COST_MODELING,
                name="Cost Modeling Specialist",
                expertise_description="Expert in semiconductor cost modeling",
                preferred_model="deepseek-reasoner",
                fallback_model="deepseek-chat",
                system_prompt="""You are a semiconductor cost modeling specialist. Your expertise includes:
- Die cost calculation
- Package cost analysis
- Test cost estimation
- Yield modeling
- NRE amortization

Always provide:
1. Die cost breakdown
2. Package cost estimates
3. Test cost per unit
4. Volume pricing

Target $50-70 unit cost for edge AI market.""",
                quality_criteria=[
                    "Die cost breakdown",
                    "Package costs",
                    "Test costs",
                    "Volume pricing"
                ],
                temperature_range=(0.2, 0.3),
                max_calls_per_cycle=12
            ),
        ]
        
        # Create agents from configs
        for config in agent_configs:
            self.agents[config.domain] = SpecializedAgent(config)
        
        print(f"Initialized {len(self.agents)} specialized agents")
    
    async def initialize_clients(self):
        """Initialize API clients"""
        self.deepseek = DeepSeekClient()
        await self.deepseek.__aenter__()
        
        self.nvidia = NVIDIAClient()
        await self.nvidia.__aenter__()
    
    async def close_clients(self):
        """Close API clients"""
        if self.deepseek:
            await self.deepseek.__aexit__()
        if self.nvidia:
            await self.nvidia.__aexit__()
    
    async def execute_agent_task(
        self,
        domain: AgentDomain,
        prompt: str,
        cycle_number: int,
        temperature: float = None,
        max_tokens: int = 4096
    ) -> TaskResult:
        """Execute a task with a specialized agent"""
        
        agent = self.agents[domain]
        config = agent.config
        
        # Determine temperature
        if temperature is None:
            temp_min, temp_max = config.temperature_range
            temperature = (temp_min + temp_max) / 2
        
        # Build messages
        messages = [
            {"role": "system", "content": config.system_prompt},
            {"role": "user", "content": prompt}
        ]
        
        # Try primary model, fall back to secondary
        start_time = time.time()
        result = None
        model_used = config.preferred_model
        provider = ModelProvider.DEEPSEEK
        
        try:
            if "deepseek" in config.preferred_model:
                result = await self.deepseek.chat_completion(
                    model=config.preferred_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                provider = ModelProvider.DEEPSEEK
            else:
                result = await self.nvidia.chat_completion(
                    model=config.preferred_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                provider = ModelProvider.NVIDIA_NIM
                
        except Exception as e:
            print(f"  Primary model {config.preferred_model} failed: {e}, trying fallback...")
            
            try:
                if "deepseek" in config.fallback_model:
                    result = await self.deepseek.chat_completion(
                        model=config.fallback_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    provider = ModelProvider.DEEPSEEK
                else:
                    result = await self.nvidia.chat_completion(
                        model=config.fallback_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    provider = ModelProvider.NVIDIA_NIM
                model_used = config.fallback_model
            except Exception as e2:
                raise Exception(f"Both models failed: {e2}")
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Extract result
        result_text = result["choices"][0]["message"]["content"]
        
        # Analyze quality
        quality_metrics = self.quality_analyzer.analyze(
            result_text, 
            self.all_results[-20:] if self.all_results else []
        )
        
        # Create task result
        task_result = TaskResult(
            task_id=f"{domain.value}_{int(time.time()*1000)}",
            agent_domain=domain,
            model_used=model_used,
            provider=provider,
            prompt_tokens=result.get("_input_tokens", 0),
            completion_tokens=result.get("_output_tokens", 0),
            latency_ms=latency_ms,
            cost_usd=result.get("_cost_usd", 0.0),
            result_text=result_text,
            quality_metrics=quality_metrics,
            timestamp=datetime.now().isoformat(),
            cycle_number=cycle_number
        )
        
        # Store result
        self.all_results.append(task_result)
        self.domain_results[domain].append(task_result)
        agent.execution_history.append(task_result)
        agent.record_quality(quality_metrics.overall_quality)
        
        # Update metrics
        self.campaign_metrics.total_api_calls += 1
        self.campaign_metrics.total_cost_usd += task_result.cost_usd
        self.campaign_metrics.total_tokens += task_result.prompt_tokens + task_result.completion_tokens
        
        if provider == ModelProvider.DEEPSEEK:
            self.campaign_metrics.deepseek_calls += 1
        else:
            self.campaign_metrics.nvidia_calls += 1
        
        domain_name = domain.value
        self.campaign_metrics.domain_coverage[domain_name] = \
            self.campaign_metrics.domain_coverage.get(domain_name, 0) + 1
        
        return task_result
    
    def should_continue(self) -> Tuple[bool, str]:
        """Check if campaign should continue"""
        
        # Check budget
        if self.campaign_metrics.total_cost_usd >= self.budget_usd:
            return False, f"Budget limit reached: ${self.campaign_metrics.total_cost_usd:.2f}"
        
        # Check API call target
        if self.campaign_metrics.total_api_calls >= self.target_api_calls:
            return False, f"API call target reached: {self.campaign_metrics.total_api_calls}"
        
        # Check quality trend (diminishing returns)
        if len(self.all_results) > 50:
            recent_quality = [r.quality_metrics.overall_quality for r in self.all_results[-30:]]
            older_quality = [r.quality_metrics.overall_quality for r in self.all_results[-60:-30]]
            
            if recent_quality and older_quality:
                recent_avg = statistics.mean(recent_quality)
                older_avg = statistics.mean(older_quality)
                
                # Stop if quality is declining significantly
                if recent_avg < older_avg * 0.8:
                    return False, f"Quality declining: {recent_avg:.3f} < {older_avg:.3f}"
        
        return True, "Continue"
    
    def get_campaign_summary(self) -> Dict[str, Any]:
        """Get comprehensive campaign summary"""
        
        quality_scores = [r.quality_metrics.overall_quality for r in self.all_results]
        
        summary = {
            "total_api_calls": self.campaign_metrics.total_api_calls,
            "total_cost_usd": self.campaign_metrics.total_cost_usd,
            "total_tokens": self.campaign_metrics.total_tokens,
            "deepseek_calls": self.campaign_metrics.deepseek_calls,
            "nvidia_calls": self.campaign_metrics.nvidia_calls,
            "avg_quality_score": statistics.mean(quality_scores) if quality_scores else 0,
            "quality_trend": quality_scores[-20:] if len(quality_scores) >= 20 else quality_scores,
            "domain_coverage": dict(self.campaign_metrics.domain_coverage),
            "signal_to_noise_ratio": self._calculate_signal_to_noise(),
            "top_domains": self._get_top_domains(5),
            "improvement_trajectory": self._calculate_improvement_trajectory()
        }
        
        return summary
    
    def _calculate_signal_to_noise(self) -> float:
        """Calculate overall signal to noise ratio"""
        if not self.all_results:
            return 0.0
        
        total_signal = sum(
            len(r.quality_metrics.signal_indicators) 
            for r in self.all_results
        )
        total_noise = sum(
            len(r.quality_metrics.noise_indicators) 
            for r in self.all_results
        )
        
        if total_noise == 0:
            return float('inf') if total_signal > 0 else 0.0
        
        return total_signal / total_noise
    
    def _get_top_domains(self, n: int) -> List[Tuple[str, float]]:
        """Get top performing domains by average quality"""
        domain_quality = {}
        
        for domain, results in self.domain_results.items():
            scores = [r.quality_metrics.overall_quality for r in results]
            domain_quality[domain.value] = statistics.mean(scores) if scores else 0
        
        sorted_domains = sorted(domain_quality.items(), key=lambda x: x[1], reverse=True)
        return sorted_domains[:n]
    
    def _calculate_improvement_trajectory(self) -> Dict[str, float]:
        """Calculate improvement trajectory over campaign"""
        if len(self.all_results) < 20:
            return {"slope": 0, "r_squared": 0}
        
        # Simple linear regression on quality scores
        quality_scores = [r.quality_metrics.overall_quality for r in self.all_results]
        x = list(range(len(quality_scores)))
        y = quality_scores
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi ** 2 for xi in x)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        
        # R-squared
        y_mean = sum_y / n
        ss_tot = sum((yi - y_mean) ** 2 for yi in y)
        ss_res = sum((yi - (slope * xi + (sum_y - slope * sum_x) / n)) ** 2 
                     for xi, yi in zip(x, y))
        r_squared = 1 - ss_res / ss_tot if ss_tot != 0 else 0
        
        return {"slope": slope, "r_squared": r_squared}
    
    def save_results(self):
        """Save all results to files"""
        
        # Save campaign summary
        summary = self.get_campaign_summary()
        summary_path = f"{METRICS_DIR}/campaign_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        # Save detailed results
        results_path = f"{LOGS_DIR}/detailed_results.json"
        results_data = []
        for r in self.all_results:
            results_data.append({
                "task_id": r.task_id,
                "domain": r.agent_domain.value,
                "model": r.model_used,
                "provider": r.provider.value,
                "tokens": r.prompt_tokens + r.completion_tokens,
                "cost_usd": r.cost_usd,
                "latency_ms": r.latency_ms,
                "quality_score": r.quality_metrics.overall_quality,
                "signal_indicators": len(r.quality_metrics.signal_indicators),
                "noise_indicators": len(r.quality_metrics.noise_indicators),
                "timestamp": r.timestamp,
                "cycle": r.cycle_number
            })
        
        with open(results_path, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"Saved results to {METRICS_DIR} and {LOGS_DIR}")


# Export
__all__ = [
    'ProfessionalOrchestrator', 'AgentDomain', 'QualityAnalyzer',
    'SpecializedAgent', 'AgentConfig', 'TaskResult', 'QualityMetrics'
]
