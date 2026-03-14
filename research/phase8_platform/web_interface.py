"""
SuperInstance Research Platform - Web Interface
===============================================

FastAPI-based web interface for the unified research platform.
Provides REST API for experiment management, execution, and analysis.

Endpoints:
- POST /simulate - Run simulation
- GET /results/{experiment_id} - Retrieve results
- POST /validate - Validate results
- GET /experiments - List experiments
- POST /compare - Compare experiments
- GET /status/{experiment_id} - Get experiment status

Author: SuperInstance Research Team
Version: 1.0.0
Created: 2026-03-13
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

# FastAPI
try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
    from fastapi.responses import JSONResponse, FileResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    # Create stub classes for type checking
    class FastAPI:
        pass
    class BaseModel:
        pass
    class Field:
        pass

# Import platform
from unified_platform import (
    SuperInstanceResearchPlatform,
    PlatformConfig,
    ExperimentConfig,
    ExperimentResult,
    ExperimentStatus,
    Backend,
    SimulationType,
    ValidationType,
    ComparisonReport,
    create_platform,
    create_experiment
)


# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# PYDANTIC MODELS FOR API
# =============================================================================

if FASTAPI_AVAILABLE:
    class ExperimentRequest(BaseModel):
        """Request model for creating experiments."""
        experiment_id: str = Field(..., description="Unique experiment identifier")
        name: str = Field(..., description="Experiment name")
        description: str = Field("", description="Experiment description")
        simulation_type: str = Field(..., description="Type of simulation")
        parameters: Dict[str, Any] = Field(..., description="Simulation parameters")
        backend_preference: str = Field("auto", description="Preferred backend")
        validation_types: List[str] = Field(default_factory=list, description="Validation types to run")
        timeout_seconds: int = Field(3600, description="Timeout in seconds")
        priority: int = Field(5, description="Priority (1-10)")
        tags: List[str] = Field(default_factory=list, description="Experiment tags")
        created_by: str = Field("api", description="User who created experiment")

    class ValidationRequest(BaseModel):
        """Request model for validation."""
        experiment_id: str = Field(..., description="Experiment ID to validate")
        validation_types: List[str] = Field(..., description="Validation types to run")

    class ComparisonRequest(BaseModel):
        """Request model for comparing experiments."""
        experiment_ids: List[str] = Field(..., description="Experiment IDs to compare")
        comparison_type: str = Field("performance", description="Type of comparison")

    class SimulationResponse(BaseModel):
        """Response model for simulation results."""
        experiment_id: str
        status: str
        data: Any
        metadata: Dict[str, Any]
        figures: List[str]
        validation_results: List[Dict[str, Any]]
        backend_used: Optional[str]
        execution_time_ms: float
        cost_usd: float
        error: Optional[str]

    class StatusResponse(BaseModel):
        """Response model for experiment status."""
        experiment_id: str
        status: str
        done: bool


# =============================================================================
# FASTAPI APPLICATION
# =============================================================================

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="SuperInstance Research Platform",
        description="Unified research platform for SuperInstance papers",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Platform instance (will be initialized on startup)
    platform: Optional[SuperInstanceResearchPlatform] = None

    @app.on_event("startup")
    async def startup_event():
        """Initialize platform on startup."""
        global platform
        logger.info("Initializing SuperInstance Research Platform...")

        # Create platform with default config
        config = PlatformConfig()
        platform = create_platform(config)

        logger.info("Platform initialized successfully")

    @app.on_event("shutdown")
    async def shutdown_event():
        """Cleanup on shutdown."""
        global platform
        if platform:
            await platform.shutdown()
            logger.info("Platform shutdown complete")

    @app.get("/")
    async def root():
        """Root endpoint with platform info."""
        return {
            "name": "SuperInstance Research Platform",
            "version": "1.0.0",
            "status": "running",
            "gpu_available": platform.simulation.config is not None if platform else False,
            "endpoints": {
                "simulate": "POST /simulate",
                "results": "GET /results/{experiment_id}",
                "validate": "POST /validate",
                "experiments": "GET /experiments",
                "compare": "POST /compare",
                "status": "GET /status/{experiment_id}",
                "health": "GET /health"
            }
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "platform_active": platform is not None
        }

    @app.post("/simulate", response_model=SimulationResponse)
    async def run_simulation(
        request: ExperimentRequest,
        background_tasks: BackgroundTasks
    ):
        """
        Run a simulation experiment.

        Creates and executes a simulation with the specified parameters.
        Returns the experiment ID for tracking.
        """
        if not platform:
            raise HTTPException(status_code=503, detail="Platform not initialized")

        try:
            # Parse simulation type
            try:
                sim_type = SimulationType(request.simulation_type)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid simulation_type: {request.simulation_type}"
                )

            # Parse backend preference
            try:
                backend = Backend(request.backend_preference)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid backend_preference: {request.backend_preference}"
                )

            # Parse validation types
            validation_types = []
            for vt in request.validation_types:
                try:
                    validation_types.append(ValidationType(vt))
                except ValueError:
                    logger.warning(f"Unknown validation type: {vt}")

            # Create experiment
            experiment = ExperimentConfig(
                experiment_id=request.experiment_id,
                name=request.name,
                description=request.description,
                simulation_type=sim_type,
                parameters=request.parameters,
                backend_preference=backend,
                validation_types=validation_types,
                timeout_seconds=request.timeout_seconds,
                priority=request.priority,
                tags=request.tags,
                created_by=request.created_by
            )

            # Run simulation
            result = await platform.run_simulation(experiment, backend)

            return SimulationResponse(
                experiment_id=result.experiment_id,
                status=result.status.name,
                data=result.data,
                metadata=result.metadata,
                figures=result.figures,
                validation_results=result.validation_results,
                backend_used=result.backend_used.value if result.backend_used else None,
                execution_time_ms=result.execution_time_ms,
                cost_usd=result.cost_usd,
                error=result.error
            )

        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/simulate/async")
    async def run_simulation_async(
        request: ExperimentRequest
    ):
        """
        Run simulation asynchronously in background.

        Returns immediately with experiment ID.
        Check status using GET /status/{experiment_id}
        """
        if not platform:
            raise HTTPException(status_code=503, detail="Platform not initialized")

        try:
            # Parse simulation type
            sim_type = SimulationType(request.simulation_type)
            backend = Backend(request.backend_preference)

            # Create experiment
            experiment = ExperimentConfig(
                experiment_id=request.experiment_id,
                name=request.name,
                description=request.description,
                simulation_type=sim_type,
                parameters=request.parameters,
                backend_preference=backend,
                validation_types=[
                    ValidationType(vt) for vt in request.validation_types
                ],
                timeout_seconds=request.timeout_seconds,
                priority=request.priority,
                tags=request.tags,
                created_by=request.created_by
            )

            # Run in background
            experiment_id = await platform.run_simulation_async(experiment, backend)

            return {
                "experiment_id": experiment_id,
                "status": "submitted",
                "message": "Experiment running in background"
            }

        except Exception as e:
            logger.error(f"Async simulation submission failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/status/{experiment_id}")
    async def get_experiment_status(experiment_id: str):
        """Get status of a running or completed experiment."""
        if not platform:
            raise HTTPException(status_code=503, detail="Platform not initialized")

        try:
            status = await platform.get_experiment_status(experiment_id)
            return status
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/results/{experiment_id}")
    async def get_results(experiment_id: str):
        """Retrieve experimental results."""
        if not platform:
            raise HTTPException(status_code=503, detail="Platform not initialized")

        try:
            result = platform.data.load_results(experiment_id)

            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"Results not found for experiment: {experiment_id}"
                )

            return result.to_dict()

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to load results: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/experiments")
    async def list_experiments(
        tag: Optional[str] = Query(None, description="Filter by tag"),
        status: Optional[str] = Query(None, description="Filter by status")
    ):
        """List all experiments matching criteria."""
        if not platform:
            raise HTTPException(status_code=503, detail="Platform not initialized")

        try:
            # Parse status if provided
            status_filter = None
            if status:
                try:
                    status_filter = ExperimentStatus[status.upper()]
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid status: {status}"
                    )

            experiments = platform.data.list_experiments(tag=tag, status=status_filter)

            return {
                "count": len(experiments),
                "experiments": experiments
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to list experiments: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/validate")
    async def validate_results(request: ValidationRequest):
        """Run validation on experimental results."""
        if not platform:
            raise HTTPException(status_code=503, detail="Platform not initialized")

        try:
            # Load experiment and results
            experiment = platform.data.load_experiment(request.experiment_id)
            result = platform.data.load_results(request.experiment_id)

            if not experiment or not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"Experiment or results not found: {request.experiment_id}"
                )

            # Parse validation types
            validation_types = []
            for vt in request.validation_types:
                try:
                    validation_types.append(ValidationType(vt))
                except ValueError:
                    logger.warning(f"Unknown validation type: {vt}")

            # Update experiment with new validation types
            experiment.validation_types = validation_types

            # Run validation
            validation_reports = await platform.validation.validate(result, experiment)

            return {
                "experiment_id": request.experiment_id,
                "validation_results": [report.to_dict() for report in validation_reports],
                "timestamp": datetime.now().isoformat()
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/compare")
    async def compare_experiments(request: ComparisonRequest):
        """Compare multiple experimental results."""
        if not platform:
            raise HTTPException(status_code=503, detail="Platform not initialized")

        try:
            if len(request.experiment_ids) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="Need at least 2 experiments to compare"
                )

            comparison = await platform.compare_results(
                request.experiment_ids,
                request.comparison_type
            )

            return comparison.to_dict()

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/publication")
    async def prepare_publication(
        paper_id: str = Query(..., description="Paper identifier"),
        experiment_ids: List[str] = Query(..., description="Experiment IDs to include")
    ):
        """Prepare publication-ready package."""
        if not platform:
            raise HTTPException(status_code=503, detail="Platform not initialized")

        try:
            package = platform.prepare_publication(paper_id, experiment_ids)
            return package
        except Exception as e:
            logger.error(f"Publication preparation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/figures/{experiment_id}/{figure_name}")
    async def get_figure(experiment_id: str, figure_name: str):
        """Retrieve a generated figure."""
        figure_path = Path(platform.config.results_dir) / experiment_id / figure_name

        if not figure_path.exists():
            raise HTTPException(status_code=404, detail="Figure not found")

        return FileResponse(figure_path)

    @app.get("/dashboard/{experiment_id}")
    async def get_dashboard(experiment_id: str):
        """Get interactive dashboard for experiment."""
        if not platform:
            raise HTTPException(status_code=503, detail="Platform not initialized")

        try:
            dashboard_path = await platform.visualization.create_dashboard([experiment_id])
            dashboard_file = Path(platform.config.results_dir) / dashboard_path

            if not dashboard_file.exists():
                raise HTTPException(status_code=404, detail="Dashboard not found")

            return FileResponse(dashboard_file)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Dashboard generation failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/experiments/{experiment_id}")
    async def delete_experiment(experiment_id: str):
        """Delete experiment and results."""
        if not platform:
            raise HTTPException(status_code=503, detail="Platform not initialized")

        try:
            # Remove from cache
            if experiment_id in platform.data._experiment_cache:
                del platform.data._experiment_cache[experiment_id]
            if experiment_id in platform.data._result_cache:
                del platform.data._result_cache[experiment_id]

            # Remove files
            exp_file = platform.config.experiments_dir / f"{experiment_id}.json"
            result_file = platform.config.results_dir / f"{experiment_id}_result.json"

            if exp_file.exists():
                exp_file.unlink()
            if result_file.exists():
                result_file.unlink()

            return {
                "message": f"Experiment {experiment_id} deleted successfully"
            }

        except Exception as e:
            logger.error(f"Failed to delete experiment: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/stats")
    async def get_platform_stats():
        """Get platform statistics."""
        if not platform:
            raise HTTPException(status_code=503, detail="Platform not initialized")

        try:
            all_experiments = platform.data.list_experiments()

            # Count by status
            status_counts = {}
            for exp_id in all_experiments:
                result = platform.data.load_results(exp_id)
                if result:
                    status = result.status.name
                    status_counts[status] = status_counts.get(status, 0) + 1

            return {
                "total_experiments": len(all_experiments),
                "status_breakdown": status_counts,
                "active_experiments": len(platform._active_experiments),
                "gpu_available": GPU_AVAILABLE
            }

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# SERVER STARTUP
# =============================================================================

def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the FastAPI server."""
    if not FASTAPI_AVAILABLE:
        logger.error("FastAPI not available. Install with: pip install fastapi uvicorn")
        return

    import uvicorn

    logger.info(f"Starting SuperInstance Research Platform API server on {host}:{port}")

    uvicorn.run(
        "web_interface:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    # Check if GPU is available
    try:
        import cupy as cp
        GPU_AVAILABLE = True
        logger.info("GPU acceleration available (CuPy)")
    except ImportError:
        GPU_AVAILABLE = False
        logger.info("GPU acceleration not available (CuPy not installed)")

    # Run server
    run_server(reload=True)
