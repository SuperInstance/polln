# POLLN Workflow Guide

Practical guide for using POLLN workflow optimizations in production.

## Quick Start

### 1. Installation

```bash
npm install @polln/domains/workflows
```

### 2. Basic Usage

```typescript
import { getRecommendation } from '@polln/domains/workflows';

// Get workflow configuration for your task type
const config = getRecommendation('data_pipeline');

// Use configuration to initialize colony
const colony = new Colony({
  workflow: {
    pattern: config.pattern,
    granularity: config.granularity,
    composition: config.composition
  }
});
```

## Workflow Patterns

### Sequential Pattern

**Use When**: Tasks have strong dependencies, simple pipelines

```typescript
import { getPatternConfig } from '@polln/domains/workflows';

const config = getPatternConfig('sequential');
// {
//   agent_count: 1,
//   checkpoint_frequency: 'high',
//   parallelism: false,
//   coordination: 'sync'
// }

const colony = new Colony({
  agents: [{ type: 'core', count: config.agent_count }],
  coordination: {
    strategy: config.coordination,
    syncPoints: 'high'
  }
});
```

**Best For**:
- Data ETL pipelines
- Sequential document processing
- Workflow stages with dependencies

**Avoid When**:
- Tasks are independent
- High throughput required
- Tasks can run in parallel

### Parallel Pattern

**Use When**: Tasks are independent, redundancy needed

```typescript
const config = getPatternConfig('parallel');
// {
//   agent_count: 'auto',
//   checkpoint_frequency: 'low',
//   parallelism: true,
//   coordination: 'async',
//   aggregation: 'majority'
// }

const colony = new Colony({
  agents: [
    { type: 'role', count: 5, specialization: 'validator' },
    { type: 'role', count: 5, specialization: 'analyzer' }
  ],
  coordination: {
    strategy: config.coordination,
    aggregation: config.aggregation
  }
});
```

**Best For**:
- Code review (multiple reviewers)
- Redundant validation
- Independent data processing

**Avoid When**:
- Strong task dependencies
- Coordination cost is high
- Resources are limited

### Hierarchical Pattern

**Use When**: Large-scale workflows, natural hierarchy

```typescript
const config = getPatternConfig('hierarchical');
// {
//   levels: 3,
//   fan_out: 5,
//   checkpoint_frequency: 'medium',
//   coordination: 'tree'
// }

const colony = new Colony({
  agents: {
    coordinators: { type: 'core', count: 1 },
    supervisors: { type: 'role', count: 5 },
    workers: { type: 'task', count: 25 }
  },
  hierarchy: {
    levels: config.levels,
    fanOut: config.fan_out
  }
});
```

**Best For**:
- Large-scale data processing
- Multi-level approval workflows
- Distributed computing

**Avoid When**:
- Small task counts
- Flat organization preferred
- Complex to implement

### Map-Reduce Pattern

**Use When**: Data processing, batch operations

```typescript
const config = getPatternConfig('map_reduce');
// {
//   mappers: 'auto',
//   reducers: 'auto',
//   chunk_size: 10,
//   aggregation: 'mean'
// }

const colony = new Colony({
  agents: {
    mappers: { type: 'task', count: 10 },
    reducers: { type: 'role', count: 3 }
  },
  processing: {
    chunks: config.chunk_size,
    aggregation: config.aggregation
  }
});
```

**Best For**:
- Batch data processing
- Log analysis
- Aggregate computations

**Avoid When**:
- Low data volume
- Complex task dependencies
- Real-time requirements

## Agent Composition

### Generalist Strategy

**Use When**: Dynamic workloads, unknown task types

```typescript
import { getCompositionConfig } from '@polln/domains/workflows';

const config = getCompositionConfig('generalist');
// {
//   agent_types: ['core'],
//   specialization: 'low',
//   adaptability: 'high'
// }

const colony = new Colony({
  agents: [
    {
      type: 'core',
      capabilities: ['analysis', 'processing', 'coordination'],
      count: 5
    }
  ]
});
```

**Benefits**:
- Adaptable to changing tasks
- Simple deployment
- Good for exploration

**Drawbacks**:
- Lower peak performance
- Less efficient for specialized tasks

### Specialist Strategy

**Use When**: Known task types, high quality requirements

```typescript
const config = getCompositionConfig('specialist');
// {
//   agent_types: ['role'],
//   specialization: 'high',
//   adaptability: 'low'
// }

const colony = new Colony({
  agents: [
    { type: 'role', specialization: 'validation', count: 3 },
    { type: 'role', specialization: 'analysis', count: 3 },
    { type: 'role', specialization: 'processing', count: 3 }
  ]
});
```

**Benefits**:
- High quality output
- Efficient for known tasks
- Optimal resource usage

**Drawbacks**:
- Less flexible
- More complex setup
- Poor for unknown tasks

### Hybrid Strategy

**Use When**: Mixed workloads, balanced needs

```typescript
const config = getCompositionConfig('hybrid');
// {
//   agent_types: ['core', 'role', 'task'],
//   generalist_ratio: 0.3,
//   specialist_ratio: 0.7
// }

const colony = new Colony({
  agents: [
    // Generalists (30%)
    { type: 'core', count: 3 },
    // Specialists (70%)
    { type: 'role', specialization: 'validator', count: 4 },
    { type: 'role', specialization: 'analyzer', count: 4 },
    // Task agents as needed
    { type: 'task', count: 2 }
  ]
});
```

**Benefits**:
- Balanced performance
- Handles variety well
- Optimal for most cases

**Drawbacks**:
- More complex configuration
- Requires tuning

## Task Granularity

### Fine-Grained

**Use When**: Real-time processing, interactive workflows

```typescript
import { getGranularityConfig } from '@polln/domains/workflows';

const config = getGranularityConfig('fine');
// {
//   task_duration: 'seconds',
//   overhead_ratio: 0.1,
//   coordination: 'async'
// }

const colony = new Colony({
  tasks: {
    duration: '1-10s',
    coordination: config.coordination,
    batching: true,
    batchSize: 10
  }
});
```

**Best For**:
- Real-time data processing
- Interactive workflows
- Quick feedback loops

**Avoid When**:
- High overhead unacceptable
- Simple coordination preferred

### Medium-Grained

**Use When**: Batch processing, data pipelines

```typescript
const config = getGranularityConfig('medium');
// {
//   task_duration: 'minutes',
//   overhead_ratio: 0.05,
//   coordination: 'hybrid'
// }

const colony = new Colony({
  tasks: {
    duration: '1-10m',
    coordination: config.coordination,
    syncFrequency: 5
  }
});
```

**Best For**:
- Batch jobs
- Data pipelines
- General processing

**Avoid When**:
- Real-time requirements
- Very long-running tasks

### Coarse-Grained

**Use When**: Long-running jobs, analytics

```typescript
const config = getGranularityConfig('coarse');
// {
//   task_duration: 'hours',
//   overhead_ratio: 0.01,
//   coordination: 'sync'
// }

const colony = new Colony({
  tasks: {
    duration: '1h+',
    coordination: config.coordination,
    checkpointing: 'high'
  }
});
```

**Best For**:
- Analytics jobs
- Report generation
- Batch analytics

**Avoid When**:
- Quick turnaround needed
- Many small tasks

## Error Handling

### Retry Strategies

```typescript
import { WORKFLOW_DOMAIN_CONFIG } from '@polln/domains/workflows';

const errorConfig = WORKFLOW_DOMAIN_CONFIG.error_handling;

// Configure agent with retry strategy
const agent = new Agent({
  retryStrategy: errorConfig.retry_strategy, // 'exponential_backoff'
  maxRetries: 3,
  fallback: errorConfig.fallback, // 'degrade_gracefully'
  circuitBreaker: errorConfig.circuit_breaker
});
```

### Circuit Breaker

```typescript
const agent = new Agent({
  circuitBreaker: {
    enabled: true,
    threshold: 0.5,      // Trip at 50% failure rate
    window: 60000,       // 1 minute window
    halfOpenAfter: 30000 // Try again after 30s
  }
});
```

### Fallback Modes

1. **Fail Fast**: Immediate failure, no retry
2. **Degrade Gracefully**: Return partial/lower quality results
3. **Use Backup**: Route to backup agent
4. **Skip Task**: Continue without this task

## Common Workflows

### Data Pipeline

```typescript
const config = getRecommendation('data_pipeline');

const pipeline = new Colony({
  workflow: {
    pattern: 'sequential',
    agents: [
      { type: 'role', specialization: 'extractor', count: 1 },
      { type: 'role', specialization: 'transformer', count: 1 },
      { type: 'role', specialization: 'loader', count: 1 }
    ]
  },
  coordination: {
    strategy: 'sync',
    checkpointing: 'high'
  }
});
```

### Code Review

```typescript
const config = getRecommendation('code_review');

const review = new Colony({
  workflow: {
    pattern: 'parallel',
    agents: [
      { type: 'role', specialization: 'security_reviewer', count: 3 },
      { type: 'role', specialization: 'performance_reviewer', count: 3 },
      { type: 'role', specialization: 'style_reviewer', count: 2 }
    ]
  },
  coordination: {
    strategy: 'async',
    aggregation: 'majority'
  }
});
```

### Research Task

```typescript
const config = getRecommendation('research_task');

const research = new Colony({
  workflow: {
    pattern: 'map_reduce',
    agents: {
      mappers: { type: 'task', count: 10 },
      reducers: { type: 'role', count: 3 }
    }
  },
  processing: {
    chunks: 10,
    aggregation: 'mean'
  }
});
```

## Performance Tuning

### Monitor Metrics

```typescript
const colony = new Colony({ ... });

// Monitor key metrics
colony.on('metrics', (metrics) => {
  console.log('Completion time:', metrics.completionTime);
  console.log('Quality score:', metrics.qualityScore);
  console.log('Agent utilization:', metrics.agentUtilization);
  console.log('Communication overhead:', metrics.communicationOverhead);
});
```

### Adjust Configuration

Based on metrics:

1. **Low quality**: Increase specialization, add validation
2. **Slow execution**: Increase parallelism, reduce coordination
3. **High overhead**: Coarser granularity, fewer agents
4. **Low utilization**: Fewer agents, different composition

### A/B Testing

```typescript
// Test different configurations
const configs = [
  { pattern: 'sequential', agents: 1 },
  { pattern: 'parallel', agents: 5 },
  { pattern: 'hierarchical', agents: 10 }
];

for (const config of configs) {
  const colony = new Colony(config);
  const metrics = await colony.run(workflow);
  console.log(config, metrics);
}
```

## Best Practices

1. **Start with recommendations**: Use `getRecommendation()` for your task type
2. **Monitor metrics**: Track performance continuously
3. **Iterate gradually**: Change one parameter at a time
4. **Test thoroughly**: Validate with realistic workloads
5. **Consider scale**: Configurations that work for 10 tasks may not work for 1000

## Troubleshooting

### Low Quality Scores

**Symptoms**: Quality < 0.8
**Solutions**:
- Increase agent specialization
- Add validation agents
- Use parallel pattern with majority aggregation
- Increase checkpoint frequency

### Slow Execution

**Symptoms**: Completion time too high
**Solutions**:
- Increase agent count
- Use parallel or map-reduce patterns
- Reduce coordination overhead
- Coarser task granularity

### High Overhead

**Symptoms**: Overhead ratio > 0.3
**Solutions**:
- Coarser granularity
- Fewer agents
- Reduce sync points
- Use async coordination

### Poor Reliability

**Symptoms**: Success rate < 0.9
**Solutions**:
- Enable circuit breaker
- Increase retry count
- Use fallback modes
- Add redundancy

## Resources

- [Simulation README](./README.md) - Simulation details
- [Pattern Reference](./PATTERNS.md) - Pattern deep dive
- [API Documentation](../../src/domains/workflows/README.md) - TypeScript API
- [Research Papers](../../docs/research/) - Theoretical background

## License

MIT
