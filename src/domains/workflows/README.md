# Workflow Domain for POLLN

This domain provides workflow optimization capabilities for multi-agent systems.

## Overview

The Workflow Domain optimizes POLLN agents for complex workflows requiring coordination across multiple specialized agents. It provides:

- **Pattern Optimization**: Selects optimal workflow patterns (sequential, parallel, hierarchical, map-reduce)
- **Agent Composition**: Optimizes team composition (generalist, specialist, hybrid)
- **Coordination Analysis**: Balances parallelism benefits with coordination overhead
- **Reliability Engineering**: Tests error handling and fault tolerance
- **ML-Based Prediction**: Learns from historical executions to recommend configurations

## Installation

The workflow domain is included in the main POLLN package:

```typescript
import { WORKFLOW_DOMAIN_CONFIG, getRecommendation } from '@polln/domains/workflows';
```

## Usage

### Get Workflow Recommendation

```typescript
import { getRecommendation } from '@polln/domains/workflows';

// Get recommendation for a task type
const config = getRecommendation('data_pipeline');
console.log(config);
// {
//   pattern: 'sequential',
//   granularity: 'medium',
//   composition: 'specialist'
// }
```

### Access Pattern Configuration

```typescript
import { getPatternConfig } from '@polln/domains/workflows';

const parallelConfig = getPatternConfig('parallel');
console.log(parallelConfig);
// {
//   agent_count: 'auto',
//   checkpoint_frequency: 'low',
//   parallelism: true,
//   coordination: 'async',
//   aggregation: 'majority'
// }
```

## Workflow Patterns

### Sequential
- **Best for**: Simple pipelines, low-dependency workflows
- **Characteristics**: Single agent, high checkpoint frequency
- **Use when**: Tasks have strong dependencies

### Parallel
- **Best for**: Independent tasks, redundancy required
- **Characteristics**: Multiple agents, async coordination
- **Use when**: Tasks can execute simultaneously

### Hierarchical
- **Best for**: Large-scale workflows, clear authority structure
- **Characteristics**: Tree-based coordination, multiple levels
- **Use when**: Workflow has natural hierarchy

### Map-Reduce
- **Best for**: Data processing, batch operations
- **Characteristics**: Distributed mapping, centralized reduction
- **Use when**: Processing large datasets

## Agent Composition

### Generalist
- High adaptability, low specialization
- Best for: Dynamic workloads, unknown task types

### Specialist
- Low adaptability, high specialization
- Best for: Specialized tasks, high quality requirements

### Hybrid
- Balanced approach with both generalists and specialists
- Best for: Mixed workloads, balanced performance

## Configuration

See `config.ts` for complete configuration options:

- **Patterns**: Workflow pattern configurations
- **Composition**: Agent composition strategies
- **Coordination**: A2A communication settings
- **Error Handling**: Retry and fallback strategies
- **Granularity**: Task decomposition settings

## Simulation Results

All configurations are generated from extensive simulations in `simulations/domains/workflows/`:

1. **Pattern Optimization**: Tests pattern performance on various workflows
2. **Agent Composition**: Finds optimal team compositions
3. **Coordination Overhead**: Analyzes communication costs
4. **Workflow Reliability**: Tests error handling strategies
5. **Workflow Optimizer**: ML-based prediction engine

Run all simulations:

```bash
cd simulations/domains/workflows
python run_all.py
```

## Examples

### Optimizing a Data Pipeline

```typescript
import { WORKFLOW_DOMAIN_CONFIG } from '@polln/domains/workflows';

const config = WORKFLOW_DOMAIN_CONFIG.recommendations.task_type_mapping.data_pipeline;

// Use config to initialize colony
const colony = new Colony({
  workflow: {
    pattern: config.pattern,
    granularity: config.granularity,
    composition: config.composition
  }
});
```

### Error Handling Configuration

```typescript
import { WORKFLOW_DOMAIN_CONFIG } from '@polln/domains/workflows';

const errorConfig = WORKFLOW_DOMAIN_CONFIG.error_handling;

// Configure agent with error handling
const agent = new Agent({
  retryStrategy: errorConfig.retry_strategy,
  fallback: errorConfig.fallback,
  circuitBreaker: errorConfig.circuit_breaker
});
```

## Research Background

This domain is based on research into:

- **Workflow Pattern Selection**: Choosing optimal coordination patterns
- **Agent Team Composition**: Balancing generalization and specialization
- **Coordination Overhead**: Understanding communication costs
- **Fault Tolerance**: Building resilient multi-agent systems

Key papers:
- "Pattern-Based Workflow Optimization" (internal research)
- "Agent Composition Strategies" (internal research)
- "Coordination in Multi-Agent Systems" (AAAI 2024)

## License

MIT
