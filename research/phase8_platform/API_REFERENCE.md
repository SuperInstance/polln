# SuperInstance Research Platform - API Reference

Complete API reference for the SuperInstance Research Platform.

## Table of Contents

- [Python API](#python-api)
  - [Core Classes](#core-classes)
  - [Data Models](#data-models)
  - [Enums](#enums)
- [REST API](#rest-api)
  - [Simulation Endpoints](#simulation-endpoints)
  - [Data Endpoints](#data-endpoints)
  - [Analysis Endpoints](#analysis-endpoints)
  - [Platform Endpoints](#platform-endpoints)

---

## Python API

### Core Classes

#### `SuperInstanceResearchPlatform`

Main platform class integrating all layers.

**Constructor:**
```python
SuperInstanceResearchPlatform(config: Optional[PlatformConfig] = None)
```

**Methods:**

##### `run_simulation()`
```python
async def run_simulation(
    self,
    experiment: ExperimentConfig,
    backend_preference: Backend = Backend.AUTO
) -> ExperimentResult
```

Run a complete simulation with validation.

**Parameters:**
- `experiment`: Experiment configuration
- `backend_preference`: Preferred execution backend (default: AUTO)

**Returns:** `ExperimentResult`

**Raises:**
- `ValueError`: Invalid experiment configuration
- `RuntimeError`: Backend unavailable

##### `run_simulation_async()`
```python
async def run_simulation_async(
    self,
    experiment: ExperimentConfig,
    backend_preference: Backend = Backend.AUTO
) -> str
```

Run simulation asynchronously in background.

**Returns:** Experiment ID for tracking

##### `get_experiment_status()`
```python
async def get_experiment_status(self, experiment_id: str) -> Dict[str, Any]
```

Get status of running or completed experiment.

**Parameters:**
- `experiment_id`: Experiment identifier

**Returns:** Status dictionary with keys:
- `experiment_id`: str
- `status`: str ("running", "completed", "not_found")
- `done`: bool

##### `compare_results()`
```python
async def compare_results(
    self,
    experiment_ids: List[str],
    comparison_type: str = 'performance'
) -> ComparisonReport
```

Compare multiple experimental results.

**Parameters:**
- `experiment_ids`: List of experiment IDs (min 2)
- `comparison_type`: Type of comparison ("performance", "accuracy", "cost")

**Returns:** `ComparisonReport`

##### `prepare_publication()`
```python
def prepare_publication(
    self,
    paper_id: str,
    experiment_ids: List[str]
) -> Dict[str, Any]
```

Prepare publication-ready package.

**Returns:** Dictionary with:
- `paper_id`: str
- `experiments`: List[str]
- `figures`: List[str]
- `tables`: List[Dict]
- `metadata`: Dict

##### `shutdown()`
```python
async def shutdown(self)
```

Gracefully shutdown the platform.

---

#### `SimulationLayer`

Handles execution of all simulation types.

**Methods:**

##### `execute()`
```python
async def execute(
    self,
    experiment: ExperimentConfig,
    backend: Backend
) -> ExperimentResult
```

Execute a simulation with specified backend.

---

#### `ValidationLayer`

Handles statistical validation and verification.

**Methods:**

##### `validate()`
```python
async def validate(
    self,
    result: ExperimentResult,
    experiment: ExperimentConfig
) -> List[ValidationReport]
```

Run validation checks on experimental results.

**Returns:** List of validation reports

---

#### `DataLayer`

Handles data persistence, caching, and experiment tracking.

**Methods:**

##### `register_experiment()`
```python
def register_experiment(self, experiment: ExperimentConfig) -> str
```

Register a new experiment.

**Returns:** Experiment ID

##### `store_results()`
```python
def store_results(self, experiment_id: str, result: ExperimentResult)
```

Store experimental results.

##### `load_experiment()`
```python
def load_experiment(self, experiment_id: str) -> Optional[ExperimentConfig]
```

Load experiment configuration.

##### `load_results()`
```python
def load_results(self, experiment_id: str) -> Optional[ExperimentResult]
```

Load experimental results.

##### `list_experiments()`
```python
def list_experiments(
    self,
    tag: Optional[str] = None,
    status: Optional[ExperimentStatus] = None
) -> List[str]
```

List experiments matching criteria.

**Returns:** List of experiment IDs

##### `clear_cache()`
```python
def clear_cache(self)
```

Clear in-memory caches.

---

#### `OrchestrationLayer`

Intelligent resource allocation and backend selection.

**Methods:**

##### `select_backend()`
```python
async def select_backend(
    self,
    experiment: ExperimentConfig,
    preference: Backend
) -> Backend
```

Select optimal backend for experiment.

##### `estimate_cost()`
```python
def estimate_cost(
    self,
    experiment: ExperimentConfig,
    backend: Backend
) -> float
```

Estimate execution cost in USD.

**Returns:** Estimated cost

---

#### `VisualizationLayer`

Handles real-time visualization and publication plotting.

**Methods:**

##### `create_figures()`
```python
async def create_figures(
    self,
    result: ExperimentResult,
    experiment: ExperimentConfig
) -> List[str]
```

Create visualization figures for results.

**Returns:** List of figure file paths

##### `create_dashboard()`
```python
async def create_dashboard(self, experiment_ids: List[str]) -> str
```

Create interactive dashboard for experiments.

**Returns:** Dashboard HTML file path

---

### Data Models

#### `ExperimentConfig`

Configuration for an experiment.

**Attributes:**
```python
experiment_id: str              # Unique identifier
name: str                       # Human-readable name
description: str                # Detailed description
simulation_type: SimulationType # Type of simulation
parameters: Dict[str, Any]      # Simulation parameters
backend_preference: Backend     # Preferred backend (default: AUTO)
validation_types: List[ValidationType]  # Validations to run
timeout_seconds: int            # Timeout (default: 3600)
priority: int                   # Priority 1-10 (default: 5)
tags: List[str]                 # Organizational tags
created_by: str                 # Creator (default: "system")
created_at: str                 # ISO timestamp
```

**Methods:**
- `to_dict()`: Convert to dictionary
- `from_dict(data)`: Create from dictionary

#### `ExperimentResult`

Results from an experiment.

**Attributes:**
```python
experiment_id: str              # Experiment identifier
status: ExperimentStatus        # Completion status
data: Any                       # Result data
metadata: Dict[str, Any]        # Execution metadata
figures: List[str]              # Generated figure paths
validation_results: List[Dict]  # Validation reports
backend_used: Optional[Backend] # Actual backend used
execution_time_ms: float        # Execution time in milliseconds
cost_usd: float                 # Execution cost in USD
error: Optional[str]            # Error message if failed
started_at: Optional[str]       # Start timestamp
completed_at: Optional[str]     # Completion timestamp
```

**Methods:**
- `to_dict()`: Convert to dictionary

#### `PlatformConfig`

Configuration for the platform.

**Attributes:**
```python
data_dir: Path                  # Data storage directory
cache_dir: Path                 # Cache directory
results_dir: Path               # Results directory
experiments_dir: Path           # Experiments directory
max_concurrent_experiments: int # Max concurrent (default: 5)
max_gpu_memory_gb: float        # GPU memory limit (default: 4.0)
experiment_timeout_default: int # Default timeout (default: 3600)
cloud_api_key: Optional[str]    # Cloud API key
cloud_api_base: str             # Cloud API base URL
cloud_max_cost_usd: float       # Max cloud cost (default: 10.0)
enable_auto_validation: bool    # Auto-validation (default: true)
validation_significance_level: float  # Alpha level (default: 0.05)
regression_threshold: float     # Regression threshold (default: 0.05)
enable_realtime_viz: bool       # Real-time visualization (default: true)
plot_backend: str               # Plotting library (default: "matplotlib")
log_level: str                  # Logging level (default: "INFO")
log_to_file: bool               # File logging (default: true)
```

#### `ValidationReport`

Report from validation.

**Attributes:**
```python
validation_type: ValidationType # Type of validation
passed: bool                    # Pass/fail
score: float                    # Validation score (0-1)
metrics: Dict[str, float]       # Validation metrics
details: str                    # Detailed description
timestamp: str                  # ISO timestamp
```

#### `ComparisonReport`

Report comparing multiple experiments.

**Attributes:**
```python
experiment_ids: List[str]       # Experiments compared
comparison_type: str            # Type of comparison
results: Dict[str, Any]         # Comparison results
winner: Optional[str]           # Winning experiment ID
insights: List[str]             # Generated insights
timestamp: str                  # ISO timestamp
```

---

### Enums

#### `Backend`

Execution backend options.

**Values:**
- `LOCAL_GPU`: Local GPU execution (CuPy)
- `LOCAL_CPU`: Local CPU execution (NumPy)
- `CLOUD`: Cloud execution (DeepInfra)
- `HYBRID`: Hybrid GPU + Cloud
- `AUTO`: Automatic selection

#### `SimulationType`

Types of simulations supported.

**Values:**
- `HYBRID_MULTI_PAPER`: Multi-paper integration
- `HARDWARE_ACCURATE`: Realistic hardware modeling
- `IMPOSSIBLE_SIMULATION`: Theoretical edge cases
- `NOVEL_ALGORITHM`: New algorithm discovery
- `EMERGENCE_PREDICTION`: Emergence detection
- `GPU_ACCELERATED`: GPU-optimized workloads
- `CLOUD_ENHANCED`: Cloud LLM integration
- `ADAPTIVE_LEARNING`: Learning optimization
- `PRODUCTION_BENCHMARK`: Production validation

#### `ValidationType`

Types of validation.

**Values:**
- `STATISTICAL`: Statistical significance testing
- `CROSS_VALIDATION`: Cross-validation with historical
- `GPU_CLOUD_CROSS`: GPU vs Cloud consistency
- `REGRESSION`: Performance regression check
- `SANITY`: Basic sanity checks

#### `ExperimentStatus`

Status of experiments.

**Values:**
- `PENDING`: Waiting to run
- `RUNNING`: Currently executing
- `COMPLETED`: Finished successfully
- `FAILED`: Failed with error
- `CANCELLED`: Cancelled by user

---

### Factory Functions

#### `create_platform()`
```python
def create_platform(config: Optional[PlatformConfig] = None) -> SuperInstanceResearchPlatform
```

Create a new platform instance.

#### `create_experiment()`
```python
def create_experiment(
    experiment_id: str,
    name: str,
    simulation_type: SimulationType,
    parameters: Dict[str, Any],
    **kwargs
) -> ExperimentConfig
```

Create an experiment configuration.

**Optional kwargs:**
- `description`: str
- `backend_preference`: Backend
- `validation_types`: List[ValidationType]
- `timeout_seconds`: int
- `priority`: int
- `tags`: List[str]
- `created_by`: str

---

## REST API

### Base URL
```
http://localhost:8000
```

### Simulation Endpoints

#### POST /simulate

Run a simulation experiment synchronously.

**Request Body:**
```json
{
  "experiment_id": "string (required)",
  "name": "string (required)",
  "description": "string (default: '')",
  "simulation_type": "string (required)",
  "parameters": "object (required)",
  "backend_preference": "string (default: 'auto')",
  "validation_types": "array<string> (default: [])",
  "timeout_seconds": "integer (default: 3600)",
  "priority": "integer (default: 5)",
  "tags": "array<string> (default: [])",
  "created_by": "string (default: 'api')"
}
```

**Response (200 OK):**
```json
{
  "experiment_id": "string",
  "status": "string",
  "data": "any",
  "metadata": "object",
  "figures": ["string"],
  "validation_results": ["object"],
  "backend_used": "string | null",
  "execution_time_ms": "number",
  "cost_usd": "number",
  "error": "string | null"
}
```

**Errors:**
- `400 Bad Request`: Invalid request parameters
- `500 Internal Server Error`: Simulation execution failed
- `503 Service Unavailable`: Platform not initialized

---

#### POST /simulate/async

Run simulation asynchronously in background.

**Request Body:** Same as `/simulate`

**Response (200 OK):**
```json
{
  "experiment_id": "string",
  "status": "submitted",
  "message": "string"
}
```

---

#### GET /status/{experiment_id}

Get status of a running or completed experiment.

**Parameters:**
- `experiment_id` (path): Experiment identifier

**Response (200 OK):**
```json
{
  "experiment_id": "string",
  "status": "string",
  "done": boolean
}
```

---

### Data Endpoints

#### GET /results/{experiment_id}

Retrieve experimental results.

**Parameters:**
- `experiment_id` (path): Experiment identifier

**Response (200 OK):**
```json
{
  "experiment_id": "string",
  "status": "string",
  "data": "any",
  "metadata": "object",
  "figures": ["string"],
  "validation_results": ["object"],
  "backend_used": "string | null",
  "execution_time_ms": "number",
  "cost_usd": "number",
  "error": "string | null",
  "started_at": "string | null",
  "completed_at": "string | null"
}
```

**Errors:**
- `404 Not Found`: Results not found

---

#### GET /experiments

List all experiments matching criteria.

**Query Parameters:**
- `tag` (optional): Filter by tag
- `status` (optional): Filter by status (PENDING, RUNNING, COMPLETED, FAILED, CANCELLED)

**Response (200 OK):**
```json
{
  "count": "integer",
  "experiments": ["string"]
}
```

---

#### DELETE /experiments/{experiment_id}

Delete experiment and results.

**Parameters:**
- `experiment_id` (path): Experiment identifier

**Response (200 OK):**
```json
{
  "message": "string"
}
```

---

### Analysis Endpoints

#### POST /validate

Run validation on experimental results.

**Request Body:**
```json
{
  "experiment_id": "string (required)",
  "validation_types": ["string"] (required)
}
```

**Response (200 OK):**
```json
{
  "experiment_id": "string",
  "validation_results": [
    {
      "validation_type": "string",
      "passed": "boolean",
      "score": "number",
      "metrics": "object",
      "details": "string",
      "timestamp": "string"
    }
  ],
  "timestamp": "string"
}
```

**Errors:**
- `404 Not Found`: Experiment or results not found

---

#### POST /compare

Compare multiple experimental results.

**Request Body:**
```json
{
  "experiment_ids": ["string"] (required, min 2),
  "comparison_type": "string (default: 'performance')"
}
```

**Response (200 OK):**
```json
{
  "experiment_ids": ["string"],
  "comparison_type": "string",
  "results": "object",
  "winner": "string | null",
  "insights": ["string"],
  "timestamp": "string"
}
```

**Errors:**
- `400 Bad Request`: Less than 2 experiments provided

---

### Platform Endpoints

#### GET /

Root endpoint with platform info.

**Response (200 OK):**
```json
{
  "name": "string",
  "version": "string",
  "status": "string",
  "gpu_available": "boolean",
  "endpoints": "object"
}
```

---

#### GET /health

Health check endpoint.

**Response (200 OK):**
```json
{
  "status": "string",
  "timestamp": "string",
  "platform_active": "boolean"
}
```

---

#### GET /stats

Get platform statistics.

**Response (200 OK):**
```json
{
  "total_experiments": "integer",
  "status_breakdown": {
    "COMPLETED": "integer",
    "RUNNING": "integer",
    "FAILED": "integer"
  },
  "active_experiments": "integer",
  "gpu_available": "boolean"
}
```

---

#### GET /figures/{experiment_id}/{figure_name}

Retrieve a generated figure.

**Parameters:**
- `experiment_id` (path): Experiment identifier
- `figure_name` (path): Figure filename

**Response (200 OK):** Image file

**Errors:**
- `404 Not Found`: Figure not found

---

#### GET /dashboard/{experiment_id}

Get interactive dashboard for experiment.

**Parameters:**
- `experiment_id` (path): Experiment identifier

**Response (200 OK):** HTML file

**Errors:**
- `404 Not Found`: Dashboard not found

---

#### POST /publication

Prepare publication-ready package.

**Query Parameters:**
- `paper_id` (required): Paper identifier
- `experiment_ids` (required): List of experiment IDs

**Response (200 OK):**
```json
{
  "paper_id": "string",
  "experiments": ["string"],
  "figures": ["string"],
  "tables": ["object"],
  "metadata": "object"
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message description"
}
```

**Common HTTP Status Codes:**
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Platform not initialized

---

## Rate Limiting

Currently no rate limiting is enforced. For production deployment, implement rate limiting based on:
- User ID/API key
- Endpoint type
- Resource consumption

---

## Authentication

Currently no authentication is required. For production deployment, implement:
- OAuth2/JWT authentication
- API key authentication
- User management and authorization

---

## Pagination

List endpoints (like `/experiments`) may support pagination in future versions:

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50)
- `sort`: Sort field
- `order`: Sort order (asc/desc)

---

## Webhooks

Future versions may support webhooks for experiment completion:

**Configuration:**
```json
{
  "webhook_url": "https://your-server.com/webhook",
  "webhook_events": ["experiment_completed", "experiment_failed"]
}
```

**Webhook Payload:**
```json
{
  "event": "experiment_completed",
  "experiment_id": "string",
  "timestamp": "string",
  "data": "object"
}
```
