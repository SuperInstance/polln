#!/usr/bin/env python3
"""
CRDT Production Deployment System

Deploys CRDT-enhanced coordination in real distributed systems
FastAPI service with async merge, health checks, metrics

Hardware: Production servers (not GPU-dependent)
Author: Production Backend Team
Version: 1.0.0
"""

import asyncio
import os
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json
import hashlib

import aiohttp
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uvicorn

# =============================================================================
# Logging Configuration
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# Data Models
# =============================================================================

@dataclass
class Operation:
    """CRDT operation."""
    op_id: str
    op_type: str  # "read", "write", "compute"
    key: str
    value: Optional[str] = None
    criticality: float = 0.5
    conflict_probability: float = 0.1
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "op_id": self.op_id,
            "op_type": self.op_type,
            "key": self.key,
            "value": self.value,
            "criticality": self.criticality,
            "conflict_probability": self.conflict_probability,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Operation":
        """Create from dictionary."""
        return cls(**data)

    def __hash__(self) -> int:
        """Hash for set operations."""
        return hash(self.op_id)


@dataclass
class OperationResult:
    """Result of operation execution."""
    op_id: str
    success: bool
    value: Optional[Any] = None
    error: Optional[str] = None
    version: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "op_id": self.op_id,
            "success": self.success,
            "value": self.value,
            "error": self.error,
            "version": self.version
        }


# =============================================================================
# Path Prediction
# =============================================================================

class PathPredictor:
    """Predict whether to use fast (CRDT) or slow (consensus) path."""

    def __init__(self,
                 criticality_threshold: float = 0.7,
                 conflict_threshold: float = 0.3):
        self.criticality_threshold = criticality_threshold
        self.conflict_threshold = conflict_threshold
        self.fast_path_count = 0
        self.slow_path_count = 0

    async def predict_path(self, op: Operation) -> str:
        """
        Predict optimal execution path.

        Returns: "fast" for CRDT path, "slow" for consensus path
        """
        # High criticality requires strong consistency
        if op.criticality >= self.criticality_threshold:
            self.slow_path_count += 1
            return "slow"

        # High conflict probability requires consensus
        if op.conflict_probability >= self.conflict_threshold:
            self.slow_path_count += 1
            return "slow"

        # Default to fast path
        self.fast_path_count += 1
        return "fast"


# =============================================================================
# CRDT State Management
# =============================================================================

class TA_CRDTState:
    """
    Two-Phase CRDT State.

    Implements a simplified CRDT for production deployment.
    """

    def __init__(self):
        self.data: Dict[str, Any] = {}
        self.version_vector: Dict[str, int] = {}
        self.pending_ops: List[Operation] = []
        self.applied_ops: set = set()

    def apply(self, op: Operation) -> OperationResult:
        """
        Apply operation to CRDT state.

        Returns: OperationResult with applied state
        """
        try:
            if op.op_type == "read":
                return self._apply_read(op)
            elif op.op_type == "write":
                return self._apply_write(op)
            elif op.op_type == "compute":
                return self._apply_compute(op)
            else:
                return OperationResult(
                    op_id=op.op_id,
                    success=False,
                    error=f"Unknown operation type: {op.op_type}"
                )
        except Exception as e:
            logger.error(f"Error applying operation {op.op_id}: {e}")
            return OperationResult(
                op_id=op.op_id,
                success=False,
                error=str(e)
            )

    def _apply_read(self, op: Operation) -> OperationResult:
        """Apply read operation."""
        value = self.data.get(op.key)
        version = self.version_vector.get(op.key, 0)

        return OperationResult(
            op_id=op.op_id,
            success=True,
            value=value,
            version=version
        )

    def _apply_write(self, op: Operation) -> OperationResult:
        """Apply write operation."""
        self.data[op.key] = op.value
        self.version_vector[op.key] = self.version_vector.get(op.key, 0) + 1

        return OperationResult(
            op_id=op.op_id,
            success=True,
            value=op.value,
            version=self.version_vector[op.key]
        )

    def _apply_compute(self, op: Operation) -> OperationResult:
        """Apply compute operation."""
        # Example: simple increment operation
        current_value = self.data.get(op.key, 0)

        try:
            if isinstance(current_value, (int, float)):
                new_value = current_value + 1
                self.data[op.key] = new_value
                self.version_vector[op.key] = self.version_vector.get(op.key, 0) + 1

                return OperationResult(
                    op_id=op.op_id,
                    success=True,
                    value=new_value,
                    version=self.version_vector[op.key]
                )
            else:
                return OperationResult(
                    op_id=op.op_id,
                    success=False,
                    error=f"Cannot compute on non-numeric value: {current_value}"
                )
        except Exception as e:
            return OperationResult(
                op_id=op.op_id,
                success=False,
                error=str(e)
            )

    def merge(self, other_state: Dict[str, Any]) -> None:
        """
        Merge state from another replica.

        Implements CRDT merge semantics (Last-Writer-Wins).
        """
        for key, value in other_state.get("data", {}).items():
            other_version = other_state.get("version_vector", {}).get(key, 0)
            my_version = self.version_vector.get(key, 0)

            if other_version > my_version:
                self.data[key] = value
                self.version_vector[key] = other_version
                logger.debug(f"Merged key {key} at version {other_version}")

    def get_state(self) -> Dict[str, Any]:
        """Get current state for replication."""
        return {
            "data": self.data,
            "version_vector": self.version_vector
        }


# =============================================================================
# Consensus Client (Slow Path)
# =============================================================================

class ConsensusClient:
    """Client for consensus protocol (Raft/Paxos)."""

    def __init__(self, consensus_url: str, timeout: float = 5.0):
        self.consensus_url = consensus_url
        self.timeout = timeout

    async def propose(self, op: Operation) -> OperationResult:
        """
        Propose operation via consensus protocol.

        This is the slow path (~200ms latency).
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.consensus_url}/propose",
                    json=op.to_dict(),
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return OperationResult.from_dict(data)
                    else:
                        error_text = await response.text()
                        return OperationResult(
                            op_id=op.op_id,
                            success=False,
                            error=f"Consensus failed: {error_text}"
                        )
        except asyncio.TimeoutError:
            return OperationResult(
                op_id=op.op_id,
                success=False,
                error="Consensus timeout"
            )
        except Exception as e:
            logger.error(f"Consensus error: {e}")
            return OperationResult(
                op_id=op.op_id,
                success=False,
                error=str(e)
            )


# =============================================================================
# Async Merge Scheduler
# =============================================================================

class AsyncMergeScheduler:
    """Asynchronous background merge for CRDT replicas."""

    def __init__(self,
                 merge_interval_ms: int = 100,
                 max_batch_size: int = 100,
                 replica_urls: List[str] = None):
        self.merge_interval = merge_interval_ms
        self.max_batch_size = max_batch_size
        self.replica_urls = replica_urls or []
        self.merge_queue = asyncio.Queue()
        self.running = False
        self.merge_task = None
        self.merge_stats = defaultdict(int)

    async def schedule_merge(self, op: Operation):
        """Schedule operation for background merge."""
        await self.merge_queue.put(op)
        logger.debug(f"Scheduled merge for operation {op.op_id}")

    async def start(self, crdt_state: TA_CRDTState):
        """Start background merge process."""
        self.crdt_state = crdt_state
        self.running = True
        self.merge_task = asyncio.create_task(self._merge_loop())
        logger.info("Merge scheduler started")

    async def stop(self):
        """Stop background merge process."""
        self.running = False
        if self.merge_task:
            self.merge_task.cancel()
            try:
                await self.merge_task
            except asyncio.CancelledError:
                pass
        logger.info("Merge scheduler stopped")

    async def _merge_loop(self):
        """Main merge loop."""
        while self.running:
            try:
                # Get batch of operations
                batch = await self._get_merge_batch()

                if batch:
                    await self._merge_batch(batch)
                    self.merge_stats["batches_merged"] += 1
                    self.merge_stats["ops_merged"] += len(batch)

                # Wait before next batch
                await asyncio.sleep(self.merge_interval / 1000.0)

            except asyncio.CancelledError:
                logger.info("Merge loop cancelled")
                break
            except Exception as e:
                logger.error(f"Merge loop error: {e}")
                await asyncio.sleep(1)  # Backoff on error

    async def _get_merge_batch(self) -> List[Operation]:
        """Get batch of operations to merge."""
        batch = []
        timeout = 0.010  # 10ms

        try:
            while len(batch) < self.max_batch_size:
                try:
                    op = await asyncio.wait_for(
                        self.merge_queue.get(),
                        timeout=timeout
                    )
                    batch.append(op)
                except asyncio.TimeoutError:
                    break
        except Exception as e:
            logger.error(f"Batch collection error: {e}")

        return batch

    async def _merge_batch(self, batch: List[Operation]):
        """Merge batch of operations across replicas."""
        if not self.replica_urls:
            logger.debug("No replicas configured for merge")
            return

        # Prepare state for merge
        state = self.crdt_state.get_state()

        # Send merge requests to all replicas
        merge_tasks = [
            self._merge_with_replica(replica_url, state)
            for replica_url in self.replica_urls
        ]

        # Run merges in parallel
        results = await asyncio.gather(*merge_tasks, return_exceptions=True)

        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Merge failed to {self.replica_urls[i]}: {result}")
                self.merge_stats["merge_errors"] += 1

    async def _merge_with_replica(self, replica_url: str, state: Dict[str, Any]):
        """Merge with specific replica."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{replica_url}/merge",
                    json=state,
                    timeout=aiohttp.ClientTimeout(total=1.0)
                ) as response:
                    if response.status == 200:
                        # Merge their state back to us
                        their_state = await response.json()
                        self.crdt_state.merge(their_state)
                        self.merge_stats["successful_merges"] += 1
                    else:
                        logger.warning(f"Merge failed to {replica_url}: {response.status}")
                        self.merge_stats["merge_errors"] += 1
        except Exception as e:
            logger.error(f"Merge error with {replica_url}: {e}")
            self.merge_stats["merge_errors"] += 1
            raise

    def get_stats(self) -> Dict[str, int]:
        """Get merge statistics."""
        return dict(self.merge_stats)


# =============================================================================
# Service Metrics
# =============================================================================

@dataclass
class ServiceMetrics:
    """Production metrics."""
    fast_path_count: int = 0
    slow_path_count: int = 0
    total_ops: int = 0
    total_latency_ms: float = 0.0
    merge_count: int = 0
    error_count: int = 0
    path_predictor_fast: int = 0
    path_predictor_slow: int = 0

    @property
    def avg_latency_ms(self) -> float:
        if self.total_ops == 0:
            return 0.0
        return self.total_latency_ms / self.total_ops

    @property
    def fast_path_ratio(self) -> float:
        if self.total_ops == 0:
            return 0.0
        return self.fast_path_count / self.total_ops

    def record_operation(self, latency_ms: float, path: str, success: bool):
        """Record operation metrics."""
        self.total_ops += 1
        self.total_latency_ms += latency_ms

        if path == "fast":
            self.fast_path_count += 1
        else:
            self.slow_path_count += 1

        if not success:
            self.error_count += 1


# =============================================================================
# Main CRDT Coordination Service
# =============================================================================

class CRDTCoordinationService:
    """Production CRDT-based coordination service."""

    def __init__(self,
                 node_id: str,
                 replica_urls: List[str],
                 consensus_url: Optional[str] = None,
                 merge_interval_ms: int = 100):
        self.node_id = node_id
        self.replica_urls = replica_urls
        self.consensus_url = consensus_url

        # Initialize components
        self.crdt_state = TA_CRDTState()
        self.path_selector = PathPredictor()
        self.metrics = ServiceMetrics()
        self.merge_scheduler = AsyncMergeScheduler(
            merge_interval_ms=merge_interval_ms,
            replica_urls=replica_urls
        )

        # Consensus client (lazy initialization)
        self.consensus: Optional[ConsensusClient] = None

        logger.info(f"CRDT Coordination Service initialized: node_id={node_id}")

    async def start(self):
        """Start the service."""
        await self.merge_scheduler.start(self.crdt_state)
        logger.info("CRDT Coordination Service started")

    async def stop(self):
        """Stop the service."""
        await self.merge_scheduler.stop()
        logger.info("CRDT Coordination Service stopped")

    async def submit_operation(self, op: Operation) -> Tuple[OperationResult, str, float]:
        """
        Submit operation with tiered consistency.

        Returns: (OperationResult, path_used, latency_ms)

        Fast path: CRDT (2ms latency)
        Slow path: Consensus (200ms latency)
        """
        start_time = time.time()

        try:
            # Predict path
            path = await self.path_selector.predict_path(op)

            # Execute operation
            if path == "fast":
                result = await self._fast_path(op)
            else:
                result = await self._slow_path(op)

            # Record metrics
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_operation(latency_ms, path, result.success)

            return result, path, latency_ms

        except Exception as e:
            logger.error(f"Operation {op.op_id} failed: {e}")
            latency_ms = (time.time() - start_time) * 1000
            result = OperationResult(
                op_id=op.op_id,
                success=False,
                error=str(e)
            )
            self.metrics.record_operation(latency_ms, "error", False)
            return result, "error", latency_ms

    async def _fast_path(self, op: Operation) -> OperationResult:
        """Execute via CRDT fast path."""
        # Apply operation locally
        result = self.crdt_state.apply(op)

        # Schedule async merge
        await self.merge_scheduler.schedule_merge(op)

        return result

    async def _slow_path(self, op: Operation) -> OperationResult:
        """Execute via consensus slow path."""
        if not self.consensus_url:
            raise RuntimeError("Consensus not configured for slow path")

        # Lazy initialize consensus client
        if not self.consensus:
            self.consensus = ConsensusClient(self.consensus_url)

        # Run consensus protocol
        result = await self.consensus.propose(op)

        # Apply to CRDT state if successful
        if result.success:
            self.crdt_state.apply(op)

            # Still schedule merge for state propagation
            await self.merge_scheduler.schedule_merge(op)

        return result

    async def merge_state(self, remote_state: Dict[str, Any]) -> Dict[str, Any]:
        """Merge remote state into local state."""
        try:
            self.crdt_state.merge(remote_state)

            # Return our state for bidirectional merge
            return self.crdt_state.get_state()
        except Exception as e:
            logger.error(f"State merge error: {e}")
            raise

    def get_metrics(self) -> Dict[str, Any]:
        """Get service metrics."""
        return {
            "node_id": self.node_id,
            "fast_path_ops": self.metrics.fast_path_count,
            "slow_path_ops": self.metrics.slow_path_count,
            "total_ops": self.metrics.total_ops,
            "avg_latency_ms": self.metrics.avg_latency_ms,
            "fast_path_ratio": self.metrics.fast_path_ratio,
            "error_count": self.metrics.error_count,
            "merge_queue_size": self.merge_scheduler.merge_queue.qsize(),
            "merge_stats": self.merge_scheduler.get_stats(),
            "path_predictor": {
                "fast_path": self.path_selector.fast_path_count,
                "slow_path": self.path_selector.slow_path_count
            }
        }


# =============================================================================
# FastAPI Application
# =============================================================================

# Request/Response models
class OperationRequest(BaseModel):
    op_id: str
    op_type: str  # "read", "write", "compute"
    key: str
    value: Optional[str] = None
    criticality: float = 0.5
    conflict_probability: float = 0.1


class OperationResponse(BaseModel):
    op_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    latency_ms: float
    path_used: str  # "fast" or "slow"


class MergeRequest(BaseModel):
    data: Dict[str, Any]
    version_vector: Dict[str, int]


class HealthResponse(BaseModel):
    status: str
    node_id: str
    uptime_seconds: float


class MetricsResponse(BaseModel):
    node_id: str
    fast_path_ops: int
    slow_path_ops: int
    total_ops: int
    avg_latency_ms: float
    fast_path_ratio: float
    error_count: int
    merge_queue_size: int


# Create FastAPI app
app = FastAPI(
    title="CRDT Coordination Service",
    description="Production CRDT-enhanced coordination service",
    version="1.0.0"
)

# Global service instance
crdt_service: Optional[CRDTCoordinationService] = None
service_start_time: float = 0.0


@app.on_event("startup")
async def startup_event():
    """Initialize CRDT service."""
    global crdt_service, service_start_time
    service_start_time = time.time()

    config = {
        "node_id": os.getenv("NODE_ID", "node-1"),
        "replica_urls": [
            url.strip()
            for url in os.getenv("REPLICA_URLS", "").split(",")
            if url.strip()
        ],
        "consensus_url": os.getenv("CONSENSUS_URL"),
        "merge_interval_ms": int(os.getenv("MERGE_INTERVAL_MS", "100"))
    }

    logger.info(f"Starting CRDT service with config: {config}")

    crdt_service = CRDTCoordinationService(**config)
    await crdt_service.start()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global crdt_service
    if crdt_service:
        await crdt_service.stop()


@app.post("/operation", response_model=OperationResponse)
async def submit_operation(request: OperationRequest):
    """Submit operation for execution."""
    if not crdt_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        # Submit operation
        result, path, latency = await crdt_service.submit_operation(
            Operation(
                op_id=request.op_id,
                op_type=request.op_type,
                key=request.key,
                value=request.value,
                criticality=request.criticality,
                conflict_probability=request.conflict_probability
            )
        )

        return OperationResponse(
            op_id=request.op_id,
            status="success" if result.success else "error",
            result=result.to_dict() if result.success else None,
            error=result.error if not result.success else None,
            latency_ms=latency,
            path_used=path
        )

    except Exception as e:
        logger.error(f"Operation submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/merge")
async def merge_state(request: MergeRequest):
    """Merge state from another replica."""
    if not crdt_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        remote_state = {
            "data": request.data,
            "version_vector": request.version_vector
        }

        merged_state = await crdt_service.merge_state(remote_state)

        return {
            "status": "success",
            "state": merged_state
        }

    except Exception as e:
        logger.error(f"State merge error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    if not crdt_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    return HealthResponse(
        status="healthy",
        node_id=crdt_service.node_id,
        uptime_seconds=time.time() - service_start_time
    )


@app.get("/metrics", response_model=MetricsResponse)
async def metrics():
    """Prometheus metrics endpoint."""
    if not crdt_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    service_metrics = crdt_service.get_metrics()

    return MetricsResponse(
        node_id=service_metrics["node_id"],
        fast_path_ops=service_metrics["fast_path_ops"],
        slow_path_ops=service_metrics["slow_path_ops"],
        total_ops=service_metrics["total_ops"],
        avg_latency_ms=service_metrics["avg_latency_ms"],
        fast_path_ratio=service_metrics["fast_path_ratio"],
        error_count=service_metrics["error_count"],
        merge_queue_size=service_metrics["merge_queue_size"]
    )


@app.get("/metrics/detail")
async def metrics_detail():
    """Detailed metrics endpoint."""
    if not crdt_service:
        raise HTTPException(status_code=503, detail="Service not initialized")

    return crdt_service.get_metrics()


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Run production service."""
    # Load config from environment
    port = int(os.getenv("PORT", "8001"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()

    # Run server
    uvicorn.run(
        "crdt_coordination_service:app",
        host="0.0.0.0",
        port=port,
        log_level=log_level,
        reload=False
    )


if __name__ == "__main__":
    main()
