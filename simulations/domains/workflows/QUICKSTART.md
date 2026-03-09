# POLLN Workflow Simulations - Quick Start

## 5-Minute Setup

### 1. Install Dependencies

```bash
cd simulations/domains/workflows
pip install numpy
```

### 2. Run All Simulations

```bash
python run_all.py
```

This will:
- Run all 7 simulation modules
- Generate workflow configurations
- Create TypeScript files
- Produce comprehensive results

### 3. View Results

Results are saved to:
- `simulation_results/workflow_config.json` - Complete configuration
- `src/domains/workflows/config.ts` - TypeScript configuration

## Basic Usage

### In TypeScript

```typescript
import { getRecommendation } from '@polln/domains/workflows';

// Get recommendation for your task type
const config = getRecommendation('data_pipeline');
console.log(config);
// { pattern: 'sequential', granularity: 'medium', composition: 'specialist' }
```

### In Python

```python
from workflow_optimizer import WorkflowOptimizer

optimizer = WorkflowOptimizer()
config = optimizer.optimize_workflow(workflow_spec)
print(config)
```

## Common Workflows

### Data Pipeline
```typescript
const config = getRecommendation('data_pipeline');
// Sequential pattern, medium granularity, specialist composition
```

### Code Review
```typescript
const config = getRecommendation('code_review');
// Parallel pattern, fine granularity, specialist composition
```

### Research Task
```typescript
const config = getRecommendation('research_task');
// Map-reduce pattern, fine granularity, hybrid composition
```

## Pattern Selection Guide

| Your Workflow | Use Pattern |
|--------------|-------------|
| Strong dependencies | Sequential |
| Independent tasks | Parallel |
| Large scale | Hierarchical |
| Data processing | Map-Reduce |

## Composition Guide

| Your Need | Use Composition |
|-----------|----------------|
| Dynamic workloads | Generalist |
| Specialized tasks | Specialist |
| Mixed needs | Hybrid |

## Granularity Guide

| Task Duration | Use Granularity |
|--------------|-----------------|
| Seconds | Fine |
| Minutes | Medium |
| Hours | Coarse |

## Next Steps

1. Read the full documentation:
   - [README.md](./README.md) - Complete simulation guide
   - [WORKFLOW_GUIDE.md](./WORKFLOW_GUIDE.md) - Practical usage
   - [PATTERNS.md](./PATTERNS.md) - Pattern deep dive

2. Run individual simulations:
   ```bash
   python workflow_patterns.py
   python agent_composition.py
   python coordination_overhead.py
   python workflow_reliability.py
   python workflow_optimizer.py
   ```

3. Run tests:
   ```bash
   python test_workflows.py
   ```

4. Customize configurations:
   - Edit `src/domains/workflows/config.ts`
   - Adjust patterns, composition, coordination
   - Tune for your specific needs

## Troubleshooting

### Issue: Import errors
**Solution**: Make sure you're in the correct directory
```bash
cd simulations/domains/workflows
```

### Issue: Config not generated
**Solution**: Run the generator directly
```bash
python workflow_generator.py
```

### Issue: Poor recommendations
**Solution**: Customize config for your use case
```typescript
// Edit src/domains/workflows/config.ts
export const WORKFLOW_DOMAIN_CONFIG = {
  // Customize patterns, composition, etc.
};
```

## Support

- Check documentation in `simulations/domains/workflows/`
- Review examples in `src/domains/workflows/README.md`
- Open an issue on GitHub

## License

MIT
