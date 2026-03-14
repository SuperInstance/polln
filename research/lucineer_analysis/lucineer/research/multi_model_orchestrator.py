#!/usr/bin/env python3
"""
Multi-Model AI Orchestration System for Chip Design
DeepSeek + NVIDIA NIM + GLM 5 Coordination Framework

This system orchestrates multiple AI models for optimal chip design workflow:
- DeepSeek: Specialized hardware logic, RTL generation, stochastic reasoning
- NVIDIA NIM: Code generation, Verilog synthesis, creative exploration
- GLM 5: General orchestration, synthesis, project management
"""

import os
import json
import time
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib

# API Keys
DEEPSEEK_API_KEY = "sk-2c32887fc62b4016b6ff03f982968b76"
NVIDIA_API_KEY = "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"

# API Endpoints
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"


class ModelProvider(Enum):
    DEEPSEEK = "deepseek"
    NVIDIA_NIM = "nvidia_nim"
    GLM5 = "glm5"


class TaskType(Enum):
    VERILOG_GENERATION = "verilog_generation"
    TESTBENCH_CREATION = "testbench_creation"
    LOGIC_OPTIMIZATION = "logic_optimization"
    STOCHASTIC_REASONING = "stochastic_reasoning"
    ARCHITECTURE_ANALYSIS = "architecture_analysis"
    PHYSICAL_DESIGN = "physical_design"
    VERIFICATION = "verification"
    POWER_ANALYSIS = "power_analysis"
    TIMING_ANALYSIS = "timing_analysis"
    DEFECT_ANALYSIS = "defect_analysis"
    CREATIVE_EXPLORATION = "creative_exploration"
    SYNTHESIS = "synthesis"


@dataclass
class ModelCapabilities:
    """Capabilities and specializations of each model"""
    name: str
    provider: ModelProvider
    strengths: List[str]
    optimal_tasks: List[TaskType]
    context_window: int
    cost_per_token: float
    latency_ms: int
    quality_score: float  # 1-10


@dataclass
class TaskResult:
    """Result from a model execution"""
    task_id: str
    task_type: TaskType
    model_used: str
    provider: ModelProvider
    input_tokens: int
    output_tokens: int
    latency_ms: int
    result: str
    quality_rating: Optional[float] = None
    feedback: Optional[str] = None


@dataclass
class OrchestrationConfig:
    """Configuration for the orchestration system"""
    max_retries: int = 3
    timeout_seconds: int = 120
    enable_caching: bool = True
    enable_feedback_loop: bool = True
    quality_threshold: float = 0.8
    preferred_providers: Dict[TaskType, ModelProvider] = field(default_factory=dict)


# Model Registry - Documented capabilities
MODEL_REGISTRY: Dict[str, ModelCapabilities] = {
    # DeepSeek Models
    "deepseek-chat": ModelCapabilities(
        name="deepseek-chat",
        provider=ModelProvider.DEEPSEEK,
        strengths=[
            "General reasoning", "Multi-turn conversation", "Instruction following",
            "Balanced performance", "Cost-effective"
        ],
        optimal_tasks=[
            TaskType.SYNTHESIS, TaskType.ARCHITECTURE_ANALYSIS,
            TaskType.CREATIVE_EXPLORATION
        ],
        context_window=64000,
        cost_per_token=0.00014,
        latency_ms=500,
        quality_score=8.0
    ),
    "deepseek-coder": ModelCapabilities(
        name="deepseek-coder",
        provider=ModelProvider.DEEPSEEK,
        strengths=[
            "Code generation", "Verilog/VHDL expertise", "Debugging",
            "Code explanation", "Refactoring", "Hardware description languages"
        ],
        optimal_tasks=[
            TaskType.VERILOG_GENERATION, TaskType.TESTBENCH_CREATION,
            TaskType.LOGIC_OPTIMIZATION, TaskType.VERIFICATION
        ],
        context_window=16000,
        cost_per_token=0.00014,
        latency_ms=600,
        quality_score=9.2
    ),
    "deepseek-reasoner": ModelCapabilities(
        name="deepseek-reasoner",
        provider=ModelProvider.DEEPSEEK,
        strengths=[
            "Complex reasoning", "Stochastic analysis", "Multi-concept synthesis",
            "Contradiction resolution", "Deep logical analysis", "Hardware trade-offs"
        ],
        optimal_tasks=[
            TaskType.STOCHASTIC_REASONING, TaskType.PHYSICAL_DESIGN,
            TaskType.TIMING_ANALYSIS, TaskType.DEFECT_ANALYSIS,
            TaskType.POWER_ANALYSIS
        ],
        context_window=64000,
        cost_per_token=0.00055,
        latency_ms=2000,
        quality_score=9.5
    ),
    
    # NVIDIA NIM Models
    "meta/llama-3.1-70b-instruct": ModelCapabilities(
        name="meta/llama-3.1-70b-instruct",
        provider=ModelProvider.NVIDIA_NIM,
        strengths=[
            "Fast generation", "Verilog synthesis", "General coding",
            "Creative exploration", "Large context handling"
        ],
        optimal_tasks=[
            TaskType.VERILOG_GENERATION, TaskType.TESTBENCH_CREATION,
            TaskType.CREATIVE_EXPLORATION
        ],
        context_window=128000,
        cost_per_token=0.0,  # Free tier
        latency_ms=800,
        quality_score=8.5
    ),
    "meta/llama-3.1-405b-instruct": ModelCapabilities(
        name="meta/llama-3.1-405b-instruct",
        provider=ModelProvider.NVIDIA_NIM,
        strengths=[
            "Highest quality", "Complex reasoning", "Detailed analysis",
            "Architecture optimization", "Comprehensive documentation"
        ],
        optimal_tasks=[
            TaskType.ARCHITECTURE_ANALYSIS, TaskType.LOGIC_OPTIMIZATION,
            TaskType.STOCHASTIC_REASONING
        ],
        context_window=128000,
        cost_per_token=0.0,
        latency_ms=3000,
        quality_score=9.3
    ),
}


class DeepSeekClient:
    """Client for DeepSeek API"""
    
    def __init__(self, api_key: str = DEEPSEEK_API_KEY):
        self.api_key = api_key
        self.base_url = DEEPSEEK_BASE_URL
        
    async def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """Make chat completion request to DeepSeek"""
        
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
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"DeepSeek API error {response.status}: {error_text}")
                
                return await response.json()
    
    async def test_connection(self) -> bool:
        """Test API connection"""
        try:
            result = await self.chat_completion(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "Say 'OK' in one word"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            print(f"DeepSeek connection failed: {e}")
            return False


class NVIDIAClient:
    """Client for NVIDIA NIM API"""
    
    def __init__(self, api_key: str = NVIDIA_API_KEY):
        self.api_key = api_key
        self.base_url = NVIDIA_BASE_URL
    
    async def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096,
        **kwargs
    ) -> Dict[str, Any]:
        """Make chat completion request to NVIDIA NIM"""
        
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
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"NVIDIA API error {response.status}: {error_text}")
                
                return await response.json()
    
    async def test_connection(self) -> bool:
        """Test API connection"""
        try:
            result = await self.chat_completion(
                model="meta/llama-3.1-70b-instruct",
                messages=[{"role": "user", "content": "Say 'OK' in one word"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            print(f"NVIDIA connection failed: {e}")
            return False


class ModelOrchestrator:
    """
    High-level orchestrator for multi-model AI system.
    Manages task routing, execution, and feedback loops.
    """
    
    def __init__(self, config: OrchestrationConfig = None):
        self.config = config or OrchestrationConfig()
        self.deepseek = DeepSeekClient()
        self.nvidia = NVIDIAClient()
        self.execution_history: List[TaskResult] = []
        self.model_performance: Dict[str, List[float]] = {}
        self.cache: Dict[str, str] = {}
        
        # Initialize preferred providers for each task type
        self._init_task_routing()
    
    def _init_task_routing(self):
        """Initialize optimal task-to-model routing"""
        self.task_model_map = {
            # Hardware Development - DeepSeek Coder excels here
            TaskType.VERILOG_GENERATION: [
                ("deepseek-coder", 0.95),
                ("meta/llama-3.1-70b-instruct", 0.85),
            ],
            TaskType.TESTBENCH_CREATION: [
                ("deepseek-coder", 0.92),
                ("meta/llama-3.1-70b-instruct", 0.80),
            ],
            TaskType.LOGIC_OPTIMIZATION: [
                ("deepseek-reasoner", 0.95),
                ("deepseek-coder", 0.88),
            ],
            
            # Complex Reasoning - DeepSeek Reasoner shines
            TaskType.STOCHASTIC_REASONING: [
                ("deepseek-reasoner", 0.98),
                ("meta/llama-3.1-405b-instruct", 0.90),
            ],
            TaskType.PHYSICAL_DESIGN: [
                ("deepseek-reasoner", 0.92),
                ("deepseek-coder", 0.85),
            ],
            TaskType.TIMING_ANALYSIS: [
                ("deepseek-reasoner", 0.90),
                ("deepseek-coder", 0.82),
            ],
            TaskType.POWER_ANALYSIS: [
                ("deepseek-reasoner", 0.88),
                ("deepseek-chat", 0.80),
            ],
            TaskType.DEFECT_ANALYSIS: [
                ("deepseek-reasoner", 0.92),
                ("deepseek-coder", 0.85),
            ],
            
            # General Tasks - Balanced approach
            TaskType.ARCHITECTURE_ANALYSIS: [
                ("deepseek-chat", 0.88),
                ("meta/llama-3.1-405b-instruct", 0.90),
            ],
            TaskType.VERIFICATION: [
                ("deepseek-coder", 0.90),
                ("deepseek-reasoner", 0.85),
            ],
            
            # Creative - NVIDIA models excel
            TaskType.CREATIVE_EXPLORATION: [
                ("meta/llama-3.1-405b-instruct", 0.92),
                ("deepseek-chat", 0.85),
            ],
            
            # Synthesis - DeepSeek Chat for balance
            TaskType.SYNTHESIS: [
                ("deepseek-chat", 0.88),
                ("meta/llama-3.1-70b-instruct", 0.85),
            ],
        }
    
    def get_cache_key(self, model: str, messages: List[Dict]) -> str:
        """Generate cache key for request"""
        content = json.dumps({"model": model, "messages": messages}, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def select_model(self, task_type: TaskType, complexity: float = 0.5) -> str:
        """Select optimal model for task based on complexity and history"""
        
        candidates = self.task_model_map.get(task_type, [("deepseek-chat", 0.5)])
        
        # Adjust scores based on historical performance
        adjusted_candidates = []
        for model, base_score in candidates:
            if model in self.model_performance:
                perf = self.model_performance[model]
                avg_perf = sum(perf[-10:]) / len(perf[-10:]) if perf else 0.5
                adjusted_score = base_score * 0.7 + avg_perf * 0.3
            else:
                adjusted_score = base_score
            
            # Consider complexity
            model_caps = MODEL_REGISTRY.get(model)
            if model_caps:
                if complexity > 0.7 and model_caps.quality_score > 9.0:
                    adjusted_score *= 1.1
                if complexity < 0.3 and model_caps.latency_ms < 600:
                    adjusted_score *= 1.05
            
            adjusted_candidates.append((model, adjusted_score))
        
        # Sort by adjusted score
        adjusted_candidates.sort(key=lambda x: x[1], reverse=True)
        return adjusted_candidates[0][0]
    
    async def execute_task(
        self,
        task_type: TaskType,
        prompt: str,
        system_prompt: str = None,
        complexity: float = 0.5,
        temperature: float = None,
        max_tokens: int = 4096
    ) -> TaskResult:
        """Execute a task using optimal model selection"""
        
        task_id = f"{task_type.value}_{int(time.time()*1000)}"
        model = self.select_model(task_type, complexity)
        model_caps = MODEL_REGISTRY.get(model)
        
        # Build messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Check cache
        cache_key = self.get_cache_key(model, messages)
        if self.config.enable_caching and cache_key in self.cache:
            return TaskResult(
                task_id=task_id,
                task_type=task_type,
                model_used=model,
                provider=model_caps.provider if model_caps else ModelProvider.DEEPSEEK,
                input_tokens=0,
                output_tokens=0,
                latency_ms=0,
                result=self.cache[cache_key],
                quality_rating=1.0,
                feedback="Cache hit"
            )
        
        # Set temperature
        if temperature is None:
            temperature = 0.3 if task_type in [
                TaskType.VERILOG_GENERATION,
                TaskType.TESTBENCH_CREATION,
                TaskType.LOGIC_OPTIMIZATION
            ] else 0.5
        
        # Execute based on provider
        start_time = time.time()
        
        try:
            if model_caps and model_caps.provider == ModelProvider.DEEPSEEK:
                result = await self.deepseek.chat_completion(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            else:
                result = await self.nvidia.chat_completion(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            
            content = result["choices"][0]["message"]["content"]
            latency = int((time.time() - start_time) * 1000)
            
            # Cache result
            if self.config.enable_caching:
                self.cache[cache_key] = content
            
            task_result = TaskResult(
                task_id=task_id,
                task_type=task_type,
                model_used=model,
                provider=model_caps.provider if model_caps else ModelProvider.NVIDIA_NIM,
                input_tokens=result.get("usage", {}).get("prompt_tokens", 0),
                output_tokens=result.get("usage", {}).get("completion_tokens", 0),
                latency_ms=latency,
                result=content
            )
            
            # Record performance
            if model not in self.model_performance:
                self.model_performance[model] = []
            self.model_performance[model].append(0.8)  # Default good performance
            
            self.execution_history.append(task_result)
            return task_result
            
        except Exception as e:
            # Fallback to alternative model
            print(f"Error with {model}: {e}, trying fallback...")
            candidates = self.task_model_map.get(task_type, [])
            for fallback_model, _ in candidates[1:]:  # Skip first (already tried)
                try:
                    fallback_caps = MODEL_REGISTRY.get(fallback_model)
                    if fallback_caps and fallback_caps.provider == ModelProvider.DEEPSEEK:
                        result = await self.deepseek.chat_completion(
                            model=fallback_model,
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                    else:
                        result = await self.nvidia.chat_completion(
                            model=fallback_model,
                            messages=messages,
                            temperature=temperature,
                            max_tokens=max_tokens
                        )
                    
                    content = result["choices"][0]["message"]["content"]
                    latency = int((time.time() - start_time) * 1000)
                    
                    task_result = TaskResult(
                        task_id=task_id,
                        task_type=task_type,
                        model_used=fallback_model,
                        provider=fallback_caps.provider if fallback_caps else ModelProvider.NVIDIA_NIM,
                        input_tokens=result.get("usage", {}).get("prompt_tokens", 0),
                        output_tokens=result.get("usage", {}).get("completion_tokens", 0),
                        latency_ms=latency,
                        result=content,
                        feedback=f"Fallback from {model}"
                    )
                    
                    self.execution_history.append(task_result)
                    return task_result
                    
                except Exception as e2:
                    print(f"Fallback {fallback_model} also failed: {e2}")
                    continue
            
            raise Exception(f"All models failed for task {task_type}")
    
    def record_feedback(self, task_id: str, quality_rating: float, feedback: str = None):
        """Record human feedback on task result"""
        for result in self.execution_history:
            if result.task_id == task_id:
                result.quality_rating = quality_rating
                result.feedback = feedback
                
                # Update model performance
                model = result.model_used
                if model not in self.model_performance:
                    self.model_performance[model] = []
                self.model_performance[model].append(quality_rating)
                break
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report for all models"""
        report = {
            "total_tasks": len(self.execution_history),
            "models_used": {},
            "task_type_performance": {},
            "recommendations": []
        }
        
        # Aggregate by model
        for result in self.execution_history:
            model = result.model_used
            if model not in report["models_used"]:
                report["models_used"][model] = {
                    "tasks": 0,
                    "total_tokens": 0,
                    "total_latency_ms": 0,
                    "avg_quality": 0
                }
            
            report["models_used"][model]["tasks"] += 1
            report["models_used"][model]["total_tokens"] += result.input_tokens + result.output_tokens
            report["models_used"][model]["total_latency_ms"] += result.latency_ms
            if result.quality_rating:
                report["models_used"][model]["avg_quality"] += result.quality_rating
        
        # Calculate averages
        for model, stats in report["models_used"].items():
            if stats["tasks"] > 0:
                stats["avg_latency_ms"] = stats["total_latency_ms"] / stats["tasks"]
                if stats["avg_quality"] > 0:
                    stats["avg_quality"] /= stats["tasks"]
        
        return report


# Export for use
__all__ = [
    'ModelOrchestrator', 'OrchestrationConfig', 'TaskType', 
    'TaskResult', 'ModelCapabilities', 'MODEL_REGISTRY'
]
