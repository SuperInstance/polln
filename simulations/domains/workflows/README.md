# POLLN Workflow Simulations

Comprehensive simulation suite for optimizing POLLN agents for complex multi-agent workflows.

## Overview

This simulation system models and optimizes workflow patterns, agent compositions, coordination strategies, and reliability mechanisms for POLLN multi-agent systems. The simulations use statistical modeling and machine learning to generate production-ready configurations.

## Directory Structure

```
simulations/domains/workflows/
├── workflow_patterns.py      # Workflow pattern simulation
├── agent_composition.py      # Agent team composition optimization
├── coordination_overhead.py  # Communication cost analysis
├── workflow_reliability.py   # Error handling simulation
├── workflow_optimizer.py     # ML-based prediction engine
├── workflow_generator.py     # Configuration generator
├── run_all.py               # Master orchestrator
├── test_workflows.py        # Test suite
└── README.md               # This file
```

## Installation

### Requirements

```bash
pip install numpy
```

### Setup

```bash
cd simulations/domains/workflows
python run_all.py
```

## Simulation Modules

### 1. Workflow Patterns (`workflow_patterns.py`)

Simulates different workflow coordination patterns:

- **Sequential**: Tasks execute one after another
- **Parallel**: Tasks execute simultaneously with aggregation
- **Hierarchical**: Tree-based coordination structure
- **Map-Reduce**: Distributed processing with centralized aggregation

**Key Features**:
- Models task dependencies and data flow
- Measures completion time, quality, and resource usage
- Tests pattern performance on various workflow types
- Recommends optimal patterns per task type

**Usage**:
```python
from workflow_patterns import WorkflowSimulator, PatternType

# Create simulator
agents = [AgentConfig('core', 1.0, 0.95, 0.001, 100)]
simulator = WorkflowSimulator(agents)

# Run pattern simulation
tasks = [Task('t1', 'Extract', 2.0, 0.3)]
metrics = simulator.simulate_sequential(tasks)
```

### 2. Agent Composition (`agent_composition.py`)

Optimizes agent team composition:

- **Generalist**: Core agents with broad capabilities
- **Specialist**: Role agents with deep expertise
- **Hybrid**: Balanced mix of generalists and specialists

**Key Features**:
- Models agent capabilities and proficiency
- Tests team performance on diverse task types
- Measures cost efficiency, redundancy, and adaptability
- Finds optimal team size and specialization

**Usage**:
```python
from agent_composition import AgentTeamSimulator, TaskType

simulator = AgentTeamSimulator()
task_type = TaskType("data_processing", 0.7, 0.5, 0.8, 0.9)
team = simulator.create_team(config)
metrics = simulator.simulate_team_performance(team, task_type)
```

### 3. Coordination Overhead (`coordination_overhead.py`)

Analyzes communication and synchronization costs:

- **Fine-grained**: Many small tasks with high coordination
- **Medium-grained**: Moderate task size with balanced coordination
- **Coarse-grained**: Few large tasks with low coordination overhead

**Key Features**:
- Models A2A package communication costs
- Tests sync vs async strategies
- Measures overhead vs benefit of parallelization
- Finds optimal task granularity

**Usage**:
```python
from coordination_overhead import CoordinationSimulator, Granularity

simulator = CoordinationSimulator(num_agents=10)
decomposition = TaskDecomposition(Granularity.MEDIUM, 100, 1.0, 20, 0.01)
metrics = simulator.simulate_medium_grained(decomposition, SyncStrategy.ASYNC)
```

### 4. Workflow Reliability (`workflow_reliability.py`)

Tests error handling and fault tolerance:

- **Failure Types**: Agent failures, timeouts, quality issues, network failures
- **Retry Strategies**: Fixed, exponential backoff, circuit breaker
- **Fallback Modes**: Fail fast, degrade gracefully, use backup, skip task

**Key Features**:
- Simulates various failure scenarios
- Tests retry and recovery mechanisms
- Measures success rate and recovery time
- Generates reliability configurations

**Usage**:
```python
from workflow_reliability import ReliabilitySimulator, FailureScenario

simulator = ReliabilitySimulator(num_agents=10)
scenarios = [FailureScenario(FailureType.AGENT_FAILURE, 0.1, 1.0, 'single_agent')]
config = ReliabilityConfig(RetryStrategy.EXPONENTIAL_BACKOFF, 3, ...)
metrics = simulator.simulate_workflow(scenarios, config)
```

### 5. Workflow Optimizer (`workflow_optimizer.py`)

ML-based prediction engine for workflow optimization:

- **Feature Extraction**: Extracts workflow characteristics
- **Pattern Prediction**: Predicts optimal patterns using similarity search
- **Agent Count Prediction**: Recommends optimal number of agents
- **Performance Estimation**: Estimates execution metrics

**Key Features**:
- Learns from historical workflow executions
- Uses similarity search for pattern matching
- Generates confidence scores for recommendations
- Provides performance estimates

**Usage**:
```python
from workflow_optimizer import WorkflowOptimizer

optimizer = WorkflowOptimizer()
optimizer.predictor.train(historical_data)
config = optimizer.optimize_workflow(workflow_spec)
```

### 6. Workflow Generator (`workflow_generator.py`)

Compiles optimal configurations from simulation results:

- **Pattern Configs**: Template configurations for each pattern
- **Composition Configs**: Agent composition strategies
- **Coordination Configs**: Communication and sync settings
- **Error Handling Configs**: Retry and fallback policies
- **Task Type Mappings**: Recommendations per workflow type

**Output**: Generates `src/domains/workflows/config.ts`

**Usage**:
```python
from workflow_generator import WorkflowConfigGenerator

generator = WorkflowConfigGenerator()
config = generator.generate_workflow_config()
generator.generate_typescript_config(config, 'config.ts')
```

### 7. Run All (`run_all.py`)

Master orchestrator that runs all simulations:

- Executes all simulation modules
- Collects and aggregates results
- Generates final configuration files
- Creates TypeScript exports

**Usage**:
```bash
python run_all.py
```

## Running Simulations

### Run Individual Simulation

```bash
python workflow_patterns.py
python agent_composition.py
python coordination_overhead.py
python workflow_reliability.py
python workflow_optimizer.py
```

### Run All Simulations

```bash
python run_all.py
```

### Run Tests

```bash
python test_workflows.py
```

## Output Files

### Simulation Results

Results are saved to `simulation_results/`:

- `pattern_optimization.json` - Pattern performance data
- `composition_optimization.json` - Team composition results
- `coordination_overhead.json` - Communication overhead analysis
- `workflow_reliability.json` - Error handling test results
- `workflow_optimizer.json` - ML prediction results
- `workflow_config.json` - Final configuration JSON
- `orchestrator_results.json` - Master orchestrator summary

### Generated Configuration

TypeScript configuration is generated at `src/domains/workflows/config.ts`:

```typescript
export const WORKFLOW_DOMAIN_CONFIG = {
  patterns: { ... },
  composition: { ... },
  coordination: { ... },
  error_handling: { ... },
  granularity: { ... },
  recommendations: { ... }
};
```

## Key Concepts

### Workflow Patterns

1. **Sequential**
   - Single agent processes tasks one at a time
   - Best for: Simple pipelines, strong dependencies
   - Low overhead, limited parallelism

2. **Parallel**
   - Multiple agents process tasks simultaneously
   - Best for: Independent tasks, redundancy
   - Higher throughput, more coordination

3. **Hierarchical**
   - Tree-based coordination with multiple levels
   - Best for: Large-scale workflows
   - Scalable but complex

4. **Map-Reduce**
   - Distributed mapping with centralized reduction
   - Best for: Data processing, batch operations
   - Highly scalable, data-intensive

### Agent Composition

1. **Generalist**
   - Core agents with broad capabilities
   - High adaptability, low specialization
   - Best for: Dynamic, unknown workloads

2. **Specialist**
   - Role agents with deep expertise
   - Low adaptability, high specialization
   - Best for: Known, specialized tasks

3. **Hybrid**
   - Mix of generalists and specialists
   - Balanced approach
   - Best for: Mixed, predictable workloads

### Coordination Strategies

1. **Sync**
   - Synchronous communication
   - Best for: Coarse-grained tasks
   - Simple but can block

2. **Async**
   - Asynchronous communication
   - Best for: Fine-grained tasks
   - Complex but non-blocking

3. **Hybrid**
   - Mixed sync/async
   - Best for: Medium-grained tasks
   - Balanced approach

### Error Handling

1. **Retry Strategies**
   - None: Fail immediately
   - Fixed: Retry with fixed delay
   - Exponential Backoff: Increasing delays
   - Circuit Breaker: Stop after threshold

2. **Fallback Modes**
   - Fail Fast: Immediate failure
   - Degrade Gracefully: Reduced quality
   - Use Backup: Alternative agent
   - Skip Task: Continue without

## Performance Metrics

Simulations measure:

- **Completion Time**: Total execution time
- **Quality Score**: Result quality (0-1)
- **Success Rate**: Percentage of successful tasks
- **Agent Utilization**: Average agent usage
- **Communication Overhead**: Coordination time
- **Cost Efficiency**: Work per unit cost
- **Redundancy**: Backup capability
- **Adaptability**: Task diversity handling

## Best Practices

1. **Start with run_all.py**: Generates complete configuration
2. **Review simulation results**: Check `simulation_results/` for data
3. **Customize configurations**: Edit generated `config.ts` as needed
4. **Test with real workflows**: Validate recommendations empirically
5. **Iterate and refine**: Run simulations periodically as needs evolve

## Research Background

These simulations are based on research into:

- **Workflow Pattern Selection**: Choosing optimal coordination patterns
- **Agent Team Composition**: Balancing generalization vs specialization
- **Coordination Overhead**: Understanding communication costs in multi-agent systems
- **Fault Tolerance**: Building resilient multi-agent workflows
- **Machine Learning for Systems**: Using ML for configuration optimization

Key References:
- "Pattern-Based Workflow Optimization" (internal research)
- "Agent Composition Strategies" (internal research)
- "Coordination in Multi-Agent Systems" (AAAI 2024)
- "Circuit Breakers for Distributed Systems" (IEEE 2023)

## Troubleshooting

### Simulation Fails

**Problem**: Simulation crashes or hangs
**Solution**: Check Python version (3.7+), install dependencies

### Poor Recommendations

**Problem**: Generated config doesn't match needs
**Solution**: Run simulations with custom parameters, edit config manually

### Memory Issues

**Problem**: Large simulations run out of memory
**Solution**: Reduce task counts, run simulations individually

## Contributing

To add new simulations:

1. Create new Python file in `simulations/domains/workflows/`
2. Save results to `simulation_results/`
3. Import and run from `run_all.py`
4. Update `workflow_generator.py` to use results
5. Add tests to `test_workflows.py`

## License

MIT

## Contact

For questions or issues, please open an issue on GitHub.
