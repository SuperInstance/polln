"""
Profiling Decorators
Decorators for profiling agents and colonies.
"""

import functools
import time
import psutil
import threading
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass
from contextlib import contextmanager

from .metrics import MetricsCollector, TimingContext


@dataclass
class ProfileResult:
    """Result of profiling a function call."""
    duration: float
    cpu_percent: float
    memory_mb: float
    memory_delta_mb: float
    thread_count: int
    success: bool
    error: Optional[str] = None


# Global metrics collector for decorators
_global_collector = MetricsCollector()
_collector_lock = threading.Lock()


def get_global_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    return _global_collector


def profile_agent(
    metric_name: Optional[str] = None,
    track_memory: bool = True,
    track_cpu: bool = True,
    collector: Optional[MetricsCollector] = None
):
    """
    Decorator to profile agent methods.

    Args:
        metric_name: Name for the metric (defaults to function name)
        track_memory: Whether to track memory usage
        track_cpu: Whether to track CPU usage
        collector: Metrics collector (uses global if None)

    Example:
        @profile_agent(metric_name="agent_process")
        async def process(self, input_data):
            # ... agent logic
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            col = collector or _global_collector
            name = metric_name or f"agent_{func.__name__}"

            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024 if track_memory else 0

            # Start timing
            start_time = time.time()
            cpu_before = process.cpu_percent() if track_cpu else 0

            try:
                result = await func(*args, **kwargs)

                # Record metrics
                duration = time.time() - start_time
                cpu_after = process.cpu_percent() if track_cpu else 0
                memory_after = process.memory_info().rss / 1024 / 1024 if track_memory else 0

                col.observe_timing(f"{name}_duration", duration)
                if track_cpu:
                    col.observe_histogram(f"{name}_cpu", cpu_after - cpu_before)
                if track_memory:
                    col.observe_histogram(f"{name}_memory", memory_after - start_memory)

                return result

            except Exception as e:
                duration = time.time() - start_time
                col.observe_timing(f"{name}_duration", duration)
                col.increment_counter(f"{name}_errors")
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            col = collector or _global_collector
            name = metric_name or f"agent_{func.__name__}"

            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024 if track_memory else 0

            # Start timing
            start_time = time.time()
            cpu_before = process.cpu_percent() if track_cpu else 0

            try:
                result = func(*args, **kwargs)

                # Record metrics
                duration = time.time() - start_time
                cpu_after = process.cpu_percent() if track_cpu else 0
                memory_after = process.memory_info().rss / 1024 / 1024 if track_memory else 0

                col.observe_timing(f"{name}_duration", duration)
                if track_cpu:
                    col.observe_histogram(f"{name}_cpu", cpu_after - cpu_before)
                if track_memory:
                    col.observe_histogram(f"{name}_memory", memory_after - start_memory)

                return result

            except Exception as e:
                duration = time.time() - start_time
                col.observe_timing(f"{name}_duration", duration)
                col.increment_counter(f"{name}_errors")
                raise

        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def profile_colony(
    metric_name: Optional[str] = None,
    track_agent_counts: bool = True,
    collector: Optional[MetricsCollector] = None
):
    """
    Decorator to profile colony-level operations.

    Args:
        metric_name: Name for the metric
        track_agent_counts: Whether to track active/dormant agent counts
        collector: Metrics collector (uses global if None)

    Example:
        @profile_colony(metric_name="colony_spawn")
        async def spawn_agent(self, config):
            # ... spawn logic
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            col = collector or _global_collector
            name = metric_name or f"colony_{func.__name__}"

            # Track agent counts before
            if track_agent_counts and args:
                colony = args[0]
                if hasattr(colony, 'agents'):
                    before_count = len(colony.agents)

            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                # Track agent counts after
                if track_agent_counts and args:
                    colony = args[0]
                    if hasattr(colony, 'agents'):
                        after_count = len(colony.agents)
                        col.set_gauge(f"{name}_agent_count", after_count)
                        if hasattr(colony, 'activeAgents'):
                            col.set_gauge(f"{name}_active_agents", colony.activeAgents)

                duration = time.time() - start_time
                col.observe_timing(f"{name}_duration", duration)
                col.increment_counter(f"{name}_calls")

                return result

            except Exception as e:
                duration = time.time() - start_time
                col.observe_timing(f"{name}_duration", duration)
                col.increment_counter(f"{name}_errors")
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            col = collector or _global_collector
            name = metric_name or f"colony_{func.__name__}"

            # Track agent counts before
            if track_agent_counts and args:
                colony = args[0]
                if hasattr(colony, 'agents'):
                    before_count = len(colony.agents)

            start_time = time.time()

            try:
                result = func(*args, **kwargs)

                # Track agent counts after
                if track_agent_counts and args:
                    colony = args[0]
                    if hasattr(colony, 'agents'):
                        after_count = len(colony.agents)
                        col.set_gauge(f"{name}_agent_count", after_count)
                        if hasattr(colony, 'activeAgents'):
                            col.set_gauge(f"{name}_active_agents", colony.activeAgents)

                duration = time.time() - start_time
                col.observe_timing(f"{name}_duration", duration)
                col.increment_counter(f"{name}_calls")

                return result

            except Exception as e:
                duration = time.time() - start_time
                col.observe_timing(f"{name}_duration", duration)
                col.increment_counter(f"{name}_errors")
                raise

        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def time_execution(
    metric_name: Optional[str] = None,
    collector: Optional[MetricsCollector] = None
):
    """
    Simple decorator to time function execution.

    Args:
        metric_name: Name for the timing metric
        collector: Metrics collector (uses global if None)

    Example:
        @time_execution(metric_name="my_function")
        def my_function():
            # ... logic
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            col = collector or _global_collector
            name = metric_name or func.__name__

            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                col.observe_timing(name, duration)
                return result
            except Exception:
                duration = time.time() - start_time
                col.observe_timing(f"{name}_error", duration)
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            col = collector or _global_collector
            name = metric_name or func.__name__

            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                col.observe_timing(name, duration)
                return result
            except Exception:
                duration = time.time() - start_time
                col.observe_timing(f"{name}_error", duration)
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


@contextmanager
def profile_context(
    metric_name: str,
    collector: Optional[MetricsCollector] = None
):
    """
    Context manager for profiling code blocks.

    Args:
        metric_name: Name for the timing metric
        collector: Metrics collector

    Example:
        with profile_context("custom_operation"):
            # ... code to profile
            pass
    """
    col = collector or _global_collector
    start_time = time.time()

    try:
        yield
    finally:
        duration = time.time() - start_time
        col.observe_timing(metric_name, duration)


# Import asyncio at module level for checking
import asyncio
