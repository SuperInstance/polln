#!/usr/bin/env python3
"""
SuperInstance Production Monitoring Stack

Complete monitoring: Prometheus metrics, OpenTelemetry traces,
structured logging, health checks, and alerting

Deployment: Docker Compose with Prometheus, Grafana, Jaeger
"""

import asyncio
import time
import os
import shutil
from typing import Dict, Callable, List, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import socket
import aiohttp
import psutil

# =============================================================================
# Prometheus Metrics
# =============================================================================

try:
    from prometheus_client import Counter, Histogram, Gauge, start_http_server, CollectorRegistry, REGISTRY
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("Warning: prometheus_client not available. Install with: pip install prometheus_client")

class SuperInstanceMetrics:
    """Prometheus metrics for SuperInstance."""

    def __init__(self, registry: Optional[CollectorRegistry] = None):
        if not PROMETHEUS_AVAILABLE:
            print("Prometheus metrics disabled - package not installed")
            self._enabled = False
            return

        self._enabled = True
        self.registry = registry or REGISTRY

        # Operation metrics
        self.operations_total = Counter(
            "superinstance_operations_total",
            "Total operations",
            ["path_type", "operation_type", "status"],
            registry=self.registry
        )

        self.operation_duration = Histogram(
            "superinstance_operation_duration_seconds",
            "Operation duration",
            ["path_type", "operation_type"],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
            registry=self.registry
        )

        # CRDT metrics
        self.crdt_merge_duration = Histogram(
            "superinstance_crdt_merge_duration_seconds",
            "CRDT merge duration",
            ["replica_id"],
            buckets=[0.001, 0.01, 0.1, 1.0],
            registry=self.registry
        )

        self.crdt_state_size = Gauge(
            "superinstance_crdt_state_size_bytes",
            "CRDT state size in bytes",
            ["node_id"],
            registry=self.registry
        )

        self.crdt_conflict_resolution = Counter(
            "superinstance_crdt_conflict_resolutions_total",
            "Total CRDT conflict resolutions",
            ["resolution_type"],
            registry=self.registry
        )

        # Consensus metrics
        self.consensus_rounds_total = Counter(
            "superinstance_consensus_rounds_total",
            "Total consensus rounds",
            ["round_type", "result"],
            registry=self.registry
        )

        self.consensus_duration = Histogram(
            "superinstance_consensus_duration_seconds",
            "Consensus round duration",
            buckets=[0.01, 0.1, 0.5, 1.0, 5.0, 10.0],
            registry=self.registry
        )

        self.consensus_participants = Gauge(
            "superinstance_consensus_participants",
            "Number of participants in consensus",
            registry=self.registry
        )

        # GPU metrics
        self.gpu_utilization = Gauge(
            "superinstance_gpu_utilization_percent",
            "GPU utilization percentage",
            ["gpu_id"],
            registry=self.registry
        )

        self.gpu_memory_used = Gauge(
            "superinstance_gpu_memory_used_bytes",
            "GPU memory used in bytes",
            ["gpu_id"],
            registry=self.registry
        )

        self.gpu_memory_total = Gauge(
            "superinstance_gpu_memory_total_bytes",
            "GPU memory total in bytes",
            ["gpu_id"],
            registry=self.registry
        )

        self.gpu_temperature = Gauge(
            "superinstance_gpu_temperature_celsius",
            "GPU temperature",
            ["gpu_id"],
            registry=self.registry
        )

        self.gpu_power_draw = Gauge(
            "superinstance_gpu_power_draw_watts",
            "GPU power draw in watts",
            ["gpu_id"],
            registry=self.registry
        )

        # Agent metrics
        self.agent_count = Gauge(
            "superinstance_agent_count",
            "Number of active agents",
            ["agent_type"],
            registry=self.registry
        )

        self.agent_messages_total = Counter(
            "superinstance_agent_messages_total",
            "Total agent messages",
            ["from_type", "to_type", "message_type"],
            registry=self.registry
        )

        # System metrics
        self.cpu_usage = Gauge(
            "superinstance_cpu_usage_percent",
            "CPU usage percentage",
            registry=self.registry
        )

        self.memory_usage = Gauge(
            "superinstance_memory_usage_bytes",
            "Memory usage in bytes",
            registry=self.registry
        )

        self.disk_usage = Gauge(
            "superinstance_disk_usage_percent",
            "Disk usage percentage",
            ["mount_point"],
            registry=self.registry
        )

        # Network metrics
        self.network_requests_total = Counter(
            "superinstance_network_requests_total",
            "Total network requests",
            ["endpoint", "method", "status"],
            registry=self.registry
        )

        self.network_request_duration = Histogram(
            "superinstance_network_request_duration_seconds",
            "Network request duration",
            ["endpoint", "method"],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0],
            registry=self.registry
        )

        # Tile metrics
        self.tile_executions_total = Counter(
            "superinstance_tile_executions_total",
            "Total tile executions",
            ["tile_type", "status"],
            registry=self.registry
        )

        self.tile_execution_duration = Histogram(
            "superinstance_tile_execution_duration_seconds",
            "Tile execution duration",
            ["tile_type"],
            buckets=[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1],
            registry=self.registry
        )

    def record_operation(self,
                        path_type: str,
                        operation_type: str,
                        status: str,
                        duration_sec: float):
        """Record operation metric."""
        if not self._enabled:
            return

        self.operations_total.labels(
            path_type=path_type,
            operation_type=operation_type,
            status=status
        ).inc()

        self.operation_duration.labels(
            path_type=path_type,
            operation_type=operation_type
        ).observe(duration_sec)

    def record_crdt_merge(self, replica_id: str, duration_sec: float, state_size: int, node_id: str):
        """Record CRDT merge metrics."""
        if not self._enabled:
            return

        self.crdt_merge_duration.labels(replica_id=replica_id).observe(duration_sec)
        self.crdt_state_size.labels(node_id=node_id).set(state_size)

    def record_consensus_round(self, round_type: str, result: str, duration_sec: float, participants: int):
        """Record consensus round metrics."""
        if not self._enabled:
            return

        self.consensus_rounds_total.labels(
            round_type=round_type,
            result=result
        ).inc()

        self.consensus_duration.observe(duration_sec)
        self.consensus_participants.set(participants)

    def record_gpu_metrics(self, gpu_id: int, utilization: float, memory_used: int,
                          memory_total: int, temperature: float, power_draw: float):
        """Record GPU metrics."""
        if not self._enabled:
            return

        self.gpu_utilization.labels(gpu_id=str(gpu_id)).set(utilization)
        self.gpu_memory_used.labels(gpu_id=str(gpu_id)).set(memory_used)
        self.gpu_memory_total.labels(gpu_id=str(gpu_id)).set(memory_total)
        self.gpu_temperature.labels(gpu_id=str(gpu_id)).set(temperature)
        self.gpu_power_draw.labels(gpu_id=str(gpu_id)).set(power_draw)

    def update_system_metrics(self):
        """Update system-level metrics."""
        if not self._enabled:
            return

        # CPU
        self.cpu_usage.set(psutil.cpu_percent())

        # Memory
        memory = psutil.virtual_memory()
        self.memory_usage.set(memory.used)

        # Disk
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                self.disk_usage.labels(mount_point=partition.mountpoint).set(usage.percent)
            except:
                pass

    def start_metrics_server(self, port: int = 9090):
        """Start Prometheus metrics server."""
        if not self._enabled:
            print("Prometheus metrics server not started - package not installed")
            return

        start_http_server(port, registry=self.registry)
        print(f"Prometheus metrics server started on port {port}")


# =============================================================================
# OpenTelemetry Tracing
# =============================================================================

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    print("Warning: OpenTelemetry not available. Install with: pip install opentelemetry-api opentelemetry-sdk")

class SuperInstanceTracer:
    """Distributed tracing for SuperInstance."""

    def __init__(self, service_name: str = "superinstance"):
        if not OTEL_AVAILABLE:
            print("OpenTelemetry tracing disabled - packages not installed")
            self._enabled = False
            return

        self._enabled = True
        self.service_name = service_name

        # Configure resource
        resource = Resource(attributes={
            SERVICE_NAME: service_name
        })

        # Configure tracer provider
        self.tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(self.tracer_provider)

        # Add console exporter (for development)
        console_exporter = ConsoleSpanExporter()
        span_processor = BatchSpanProcessor(console_exporter)
        self.tracer_provider.add_span_processor(span_processor)

        self.tracer = trace.get_tracer(__name__)

        # Try to add Jaeger exporter if available
        try:
            from opentelemetry.exporter.jaeger.thrift import JaegerExporter
            jaeger_exporter = JaegerExporter(
                agent_host_name=os.getenv("JAEGER_HOST", "localhost"),
                agent_port=int(os.getenv("JAEGER_PORT", "6831")),
            )
            jaeger_processor = BatchSpanProcessor(jaeger_exporter)
            self.tracer_provider.add_span_processor(jaeger_processor)
            print(f"Jaeger exporter configured: {os.getenv('JAEGER_HOST', 'localhost')}:6831")
        except ImportError:
            print("Jaeger exporter not available - using console only")

    def trace_operation(self, operation_name: str, path_type: str, **attributes):
        """Context manager for tracing operation."""
        if not self._enabled:
            return self._noop_context()

        attrs = {
            "path_type": path_type,
            "component": "crdt-coordination",
            **attributes
        }
        return self.tracer.start_as_current_span(operation_name, attributes=attrs)

    def trace_crdt_merge(self, replica_id: str, state_size: int, **attributes):
        """Trace CRDT merge operation."""
        if not self._enabled:
            return self._noop_context()

        attrs = {
            "replica_id": replica_id,
            "state_size": state_size,
            "component": "crdt",
            **attributes
        }
        return self.tracer.start_as_current_span("crdt_merge", attributes=attrs)

    def trace_consensus_round(self, round_id: str, participants: int, **attributes):
        """Trace consensus round."""
        if not self._enabled:
            return self._noop_context()

        attrs = {
            "round_id": round_id,
            "participants": participants,
            "component": "consensus",
            **attributes
        }
        return self.tracer.start_as_current_span("consensus_round", attributes=attrs)

    def trace_tile_execution(self, tile_type: str, tile_id: str, **attributes):
        """Trace tile execution."""
        if not self._enabled:
            return self._noop_context()

        attrs = {
            "tile_type": tile_type,
            "tile_id": tile_id,
            "component": "execution",
            **attributes
        }
        return self.tracer.start_as_current_span("tile_execution", attributes=attrs)

    def _noop_context(self):
        """Return a no-op context manager."""
        from contextlib import contextmanager

        @contextmanager
        def noop():
            yield None

        return noop()

    def shutdown(self):
        """Shutdown the tracer provider."""
        if self._enabled:
            self.tracer_provider.shutdown()


# =============================================================================
# Structured Logging
# =============================================================================

try:
    import structlog
    import logging
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False
    print("Warning: structlog not available. Install with: pip install structlog")

def configure_logging(service_name: str, level: str = "INFO") -> Any:
    """Configure structured logging."""
    if not STRUCTLOG_AVAILABLE:
        # Fallback to standard logging
        logging.basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            level=getattr(logging, level.upper()),
        )
        return logging.getLogger(service_name)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Also configure standard logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, level.upper()),
    )

    return structlog.get_logger(service_name)


# =============================================================================
# Health Check System
# =============================================================================

class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheck:
    """Single health check result."""
    name: str
    status: HealthStatus
    message: str
    last_check: str
    duration_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "last_check": self.last_check,
            "duration_ms": self.duration_ms,
            "details": self.details
        }

class HealthChecker:
    """Health check system."""

    def __init__(self):
        self.checks: Dict[str, Callable] = {}
        self.timeout_sec: int = 5

    def register_check(self, name: str, check_fn: Callable):
        """Register health check."""
        self.checks[name] = check_fn

    async def check_health(self) -> Dict[str, HealthCheck]:
        """Run all health checks."""
        results = {}

        for name, check_fn in self.checks.items():
            start_time = time.time()
            try:
                is_healthy, message, details = await check_fn()
                duration_ms = (time.time() - start_time) * 1000

                if is_healthy:
                    status = HealthStatus.HEALTHY
                else:
                    status = HealthStatus.UNHEALTHY

                results[name] = HealthCheck(
                    name=name,
                    status=status,
                    message=message,
                    last_check=datetime.utcnow().isoformat(),
                    duration_ms=duration_ms,
                    details=details or {}
                )

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                results[name] = HealthCheck(
                    name=name,
                    status=HealthStatus.UNHEALTHY,
                    message=str(e),
                    last_check=datetime.utcnow().isoformat(),
                    duration_ms=duration_ms
                )

        return results

    def overall_status(self, checks: Dict[str, HealthCheck]) -> HealthStatus:
        """Determine overall health status."""
        if any(c.status == HealthStatus.UNHEALTHY for c in checks.values()):
            return HealthStatus.UNHEALTHY
        elif any(c.status == HealthStatus.DEGRADED for c in checks.values()):
            return HealthStatus.DEGRADED
        return HealthStatus.HEALTHY

    async def health_endpoint(self) -> Dict:
        """Generate health endpoint response."""
        checks = await self.check_health()
        overall = self.overall_status(checks)

        return {
            "status": overall.value,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {k: v.to_dict() for k, v in checks.items()}
        }


# =============================================================================
# Alerting System
# =============================================================================

@dataclass
class AlertRule:
    """Alert rule definition."""
    name: str
    condition: Callable[[Dict], bool]
    severity: str = "warning"
    cooldown_sec: int = 300
    description: str = ""
    enabled: bool = True
    last_alert_time: Optional[float] = None

    def should_alert(self, metrics: Dict) -> bool:
        """Check if alert should fire."""
        if not self.enabled:
            return False

        # Check cooldown
        if self.last_alert_time:
            elapsed = time.time() - self.last_alert_time
            if elapsed < self.cooldown_sec:
                return False

        # Check condition
        try:
            if self.condition(metrics):
                self.last_alert_time = time.time()
                return True
        except Exception as e:
            print(f"Alert rule {self.name} condition error: {e}")

        return False

class Alerter:
    """Alerting system."""

    def __init__(self):
        self.rules: List[AlertRule] = []
        self.alert_handlers: List[Callable] = []
        self.alert_history: List[Dict] = []
        self.max_history = 1000

    def add_rule(self, rule: AlertRule):
        """Add alert rule."""
        self.rules.append(rule)

    def add_handler(self, handler: Callable):
        """Add alert handler (webhook, email, Slack)."""
        self.alert_handlers.append(handler)

    async def evaluate_rules(self, metrics: Dict):
        """Evaluate all alert rules."""
        for rule in self.rules:
            if rule.should_alert(metrics):
                alert = {
                    "rule_name": rule.name,
                    "severity": rule.severity,
                    "description": rule.description,
                    "metrics": metrics,
                    "timestamp": time.time(),
                    "timestamp_iso": datetime.utcnow().isoformat()
                }

                # Add to history
                self.alert_history.append(alert)
                if len(self.alert_history) > self.max_history:
                    self.alert_history.pop(0)

                # Send to all handlers
                for handler in self.alert_handlers:
                    try:
                        await handler(alert)
                    except Exception as e:
                        print(f"Alert handler error: {e}")

    async def send_slack_alert(self, webhook_url: str, alert: Dict):
        """Send alert to Slack."""
        async with aiohttp.ClientSession() as session:
            if webhook_url:
                color = "danger" if alert['severity'] == "critical" else "warning"
                await session.post(webhook_url, json={
                    "text": f"Alert: {alert['rule_name']} ({alert['severity']})",
                    "attachments": [{
                        "color": color,
                        "fields": [
                            {"title": "Severity", "value": alert['severity'], "short": True},
                            {"title": "Timestamp", "value": alert['timestamp_iso'], "short": True},
                            {"title": "Description", "value": alert.get('description', 'N/A'), "short": False},
                            {"title": "Metrics", "value": str(alert['metrics']), "short": False}
                        ]
                    }]
                })

    def get_alert_history(self, limit: int = 100) -> List[Dict]:
        """Get recent alert history."""
        return self.alert_history[-limit:]


# =============================================================================
# Complete Monitoring Stack
# =============================================================================

class MonitoringStack:
    """Complete monitoring stack for SuperInstance."""

    def __init__(self,
                 service_name: str = "superinstance",
                 config: Optional[Dict] = None):
        self.service_name = service_name
        self.config = config or {}

        # Initialize components
        self.metrics = SuperInstanceMetrics()
        self.tracer = SuperInstanceTracer(service_name)
        self.logger = configure_logging(
            service_name,
            level=self.config.get("log_level", "INFO")
        )
        self.health_checker = HealthChecker()
        self.alerter = Alerter()

        # Configuration
        self.replica_urls = self.config.get("replica_urls", [])
        self.consensus_url = self.config.get("consensus_url", "")
        self.slack_webhook = self.config.get("slack_webhook", os.getenv("SLACK_WEBHOOK_URL", ""))

        # Register default health checks
        self._register_default_health_checks()

        # Register default alert rules
        self._register_default_alerts()

        # Register alert handlers
        if self.slack_webhook:
            self.alerter.add_handler(
                lambda alert: self.send_slack_alert(self.slack_webhook, alert)
            )

        self.logger.info("monitoring_stack_initialized",
                        service_name=service_name,
                        prometheus_enabled=self.metrics._enabled,
                        tracing_enabled=self.tracer._enabled)

    def _register_default_health_checks(self):
        """Register default health checks."""
        self.health_checker.register_check("replicas", self._check_replicas)
        self.health_checker.register_check("consensus", self._check_consensus)
        self.health_checker.register_check("gpu", self._check_gpu)
        self.health_checker.register_check("disk_space", self._check_disk_space)
        self.health_checker.register_check("memory", self._check_memory)

    def _register_default_alerts(self):
        """Register default alert rules."""
        # High latency alert
        self.alerter.add_rule(AlertRule(
            name="high_latency",
            condition=lambda m: m.get("p95_latency_ms", 0) > 50,
            severity="warning",
            description="P95 latency exceeds 50ms",
            cooldown_sec=300
        ))

        # Low fast path ratio alert
        self.alerter.add_rule(AlertRule(
            name="low_fast_path_ratio",
            condition=lambda m: m.get("fast_path_ratio", 1) < 0.90,
            severity="warning",
            description="Fast path ratio below 90%",
            cooldown_sec=600
        ))

        # High error rate alert
        self.alerter.add_rule(AlertRule(
            name="high_error_rate",
            condition=lambda m: m.get("error_rate", 0) > 0.01,
            severity="critical",
            description="Error rate exceeds 1%",
            cooldown_sec=60
        ))

        # Replica down alert
        self.alerter.add_rule(AlertRule(
            name="replica_down",
            condition=lambda m: m.get("healthy_replicas", 3) < 2,
            severity="critical",
            description="Less than 2 healthy replicas",
            cooldown_sec=60
        ))

        # High GPU temperature alert
        self.alerter.add_rule(AlertRule(
            name="high_gpu_temperature",
            condition=lambda m: m.get("max_gpu_temp", 0) > 85,
            severity="warning",
            description="GPU temperature exceeds 85°C",
            cooldown_sec=300
        ))

        # High memory usage alert
        self.alerter.add_rule(AlertRule(
            name="high_memory_usage",
            condition=lambda m: m.get("memory_usage_percent", 0) > 90,
            severity="warning",
            description="Memory usage exceeds 90%",
            cooldown_sec=600
        ))

    async def _check_replicas(self) -> Tuple[bool, str, Dict]:
        """Check replica connectivity."""
        if not self.replica_urls:
            return True, "No replicas configured", {}

        healthy_count = 0
        results = []

        for url in self.replica_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{url}/health", timeout=2) as resp:
                        if resp.status == 200:
                            healthy_count += 1
                            results.append({"url": url, "status": "healthy"})
                        else:
                            results.append({"url": url, "status": f"HTTP {resp.status}"})
            except Exception as e:
                results.append({"url": url, "status": str(e)})

        all_healthy = healthy_count == len(self.replica_urls)
        return all_healthy, f"{healthy_count}/{len(self.replica_urls)} replicas healthy", {
            "healthy_count": healthy_count,
            "total_count": len(self.replica_urls),
            "results": results
        }

    async def _check_consensus(self) -> Tuple[bool, str, Dict]:
        """Check consensus service."""
        if not self.consensus_url:
            return True, "Consensus service not configured", {}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.consensus_url}/health", timeout=2) as resp:
                    return resp.status == 200, f"Consensus OK (HTTP {resp.status})", {
                        "status_code": resp.status,
                        "url": self.consensus_url
                    }
        except Exception as e:
            return False, str(e), {"error": str(e)}

    async def _check_gpu(self) -> Tuple[bool, str, Dict]:
        """Check GPU availability."""
        try:
            import pynvml
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()

            gpu_info = []
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)

                gpu_info.append({
                    "id": i,
                    "name": name.decode() if isinstance(name, bytes) else name,
                    "temperature": temp,
                    "memory_used_mb": memory_info.used // (1024*1024),
                    "memory_total_mb": memory_info.total // (1024*1024),
                    "utilization_percent": util.gpu
                })

            return True, f"{device_count} GPU(s) available", {"gpus": gpu_info}

        except ImportError:
            return True, "GPU monitoring not available (pynvml not installed)", {}
        except Exception as e:
            return False, str(e), {"error": str(e)}

    async def _check_disk_space(self) -> Tuple[bool, str, Dict]:
        """Check disk space."""
        try:
            usage = psutil.disk_usage("/")
            percent_used = usage.percent

            details = {
                "total_gb": usage.total // (1024**3),
                "used_gb": usage.used // (1024**3),
                "free_gb": usage.free // (1024**3),
                "percent_used": percent_used
            }

            if percent_used > 90:
                return False, f"Disk usage critical: {percent_used}%", details
            elif percent_used > 80:
                return True, f"Disk usage high: {percent_used}%", details
            else:
                return True, f"Disk usage OK: {percent_used}%", details

        except Exception as e:
            return False, str(e), {"error": str(e)}

    async def _check_memory(self) -> Tuple[bool, str, Dict]:
        """Check memory usage."""
        try:
            memory = psutil.virtual_memory()

            details = {
                "total_gb": memory.total // (1024**3),
                "available_gb": memory.available // (1024**3),
                "percent_used": memory.percent,
                "used_gb": memory.used // (1024**3)
            }

            if memory.percent > 95:
                return False, f"Memory usage critical: {memory.percent}%", details
            elif memory.percent > 85:
                return True, f"Memory usage high: {memory.percent}%", details
            else:
                return True, f"Memory usage OK: {memory.percent}%", details

        except Exception as e:
            return False, str(e), {"error": str(e)}

    async def collect_metrics(self) -> Dict:
        """Collect current metrics."""
        metrics = {
            "timestamp": time.time(),
            "fast_path_ops": 0,
            "slow_path_ops": 0,
            "fast_path_ratio": 1.0,
            "p95_latency_ms": 0,
            "error_rate": 0.0,
            "healthy_replicas": len(self.replica_urls),
            "max_gpu_temp": 0,
            "memory_usage_percent": psutil.virtual_memory().percent
        }

        # Update system metrics
        self.metrics.update_system_metrics()

        return metrics

    async def run_monitoring_loop(self, interval_sec: int = 10):
        """Run continuous monitoring loop."""
        self.logger.info("monitoring_loop_started", interval_sec=interval_sec)

        while True:
            try:
                # Collect metrics
                metrics = await self.collect_metrics()

                # Log metrics periodically
                self.logger.info("metrics_collected", **metrics)

                # Evaluate alert rules
                await self.alerter.evaluate_rules(metrics)

                # Wait before next iteration
                await asyncio.sleep(interval_sec)

            except Exception as e:
                self.logger.error("monitoring_error", error=str(e))
                await asyncio.sleep(interval_sec)

    def start_metrics_server(self, port: int = 9090):
        """Start Prometheus metrics server."""
        self.metrics.start_metrics_server(port)
        self.logger.info("metrics_server_started", port=port)

    async def get_health(self) -> Dict:
        """Get health status."""
        return await self.health_checker.health_endpoint()

    def get_alert_history(self, limit: int = 100) -> List[Dict]:
        """Get alert history."""
        return self.alerter.get_alert_history(limit)

    async def shutdown(self):
        """Shutdown monitoring stack gracefully."""
        self.logger.info("monitoring_stack_shutdown")

        # Shutdown tracer
        if hasattr(self, 'tracer'):
            self.tracer.shutdown()


# =============================================================================
# FastAPI Integration (Optional)
# =============================================================================

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

def create_monitoring_app(monitoring: MonitoringStack) -> FastAPI:
    """Create FastAPI app with monitoring endpoints."""
    if not FASTAPI_AVAILABLE:
        raise ImportError("FastAPI not available")

    app = FastAPI(title="SuperInstance Monitoring")

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return await monitoring.get_health()

    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint."""
        # Prometheus client handles this automatically
        return JSONResponse({"message": "Metrics served on /metrics endpoint by Prometheus client"})

    @app.get("/alerts")
    async def get_alerts(limit: int = 100):
        """Get alert history."""
        return {"alerts": monitoring.get_alert_history(limit)}

    @app.get("/status")
    async def get_status():
        """Get overall system status."""
        health = await monitoring.get_health()
        metrics = await monitoring.collect_metrics()

        return {
            "health": health,
            "metrics": metrics,
            "uptime": time.time()
        }

    return app


# =============================================================================
# Main Entry Point
# =============================================================================

async def main():
    """Run monitoring stack."""
    import argparse

    parser = argparse.ArgumentParser(description="SuperInstance Monitoring Stack")
    parser.add_argument("--port", type=int, default=9090, help="Metrics server port")
    parser.add_argument("--interval", type=int, default=10, help="Monitoring loop interval (seconds)")
    parser.add_argument("--log-level", type=str, default="INFO", help="Log level")
    parser.add_argument("--replicas", type=str, nargs="+", default=[], help="Replica URLs")
    parser.add_argument("--consensus", type=str, default="", help="Consensus service URL")

    args = parser.parse_args()

    # Create monitoring stack
    config = {
        "log_level": args.log_level,
        "replica_urls": args.replicas,
        "consensus_url": args.consensus,
        "slack_webhook": os.getenv("SLACK_WEBHOOK_URL", "")
    }

    monitoring = MonitoringStack("superinstance", config=config)

    # Start metrics server
    monitoring.start_metrics_server(port=args.port)

    # Run monitoring loop
    try:
        await monitoring.run_monitoring_loop(interval_sec=args.interval)
    except KeyboardInterrupt:
        print("\nShutting down monitoring stack...")
        await monitoring.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
