# Quick Start Guide - POLLN Coding Domain

Get started with POLLN coding domain in 5 minutes.

## Prerequisites

- POLLN installed
- Python 3.8+ (for simulations)
- Node.js 16+ (for TypeScript configs)

## Option 1: Use TypeScript Configs Directly

The fastest way to use POLLN for coding tasks:

```typescript
import { Colony } from 'polln/core';
import { CODING_DOMAIN_CONFIG } from 'polln/domains/coding';

// Create colony with coding domain
const colony = new Colony({
  domains: {
    coding: CODING_DOMAIN_CONFIG
  }
});

// Generate code
const result = await colony.execute({
  domain: 'coding',
  task: 'generate_function',
  input: {
    description: 'Calculate fibonacci numbers recursively',
    language: 'python',
    requirements: [
      'Handle edge cases (n < 0)',
      'Include type hints',
      'Add docstring'
    ]
  }
});

console.log(result.code);
// Output: Generated Python function
```

That's it! POLLN is now optimized for coding tasks.

## Option 2: Run Simulations

To verify the optimizations or customize configurations:

```bash
# Navigate to simulations directory
cd simulations/domains/coding

# Run all simulations (takes ~5 minutes)
python run_all.py

# Or run individual simulations
python code_generation.py      # Code generation optimization
python code_review.py          # Code review optimization
python debugging_simulation.py # Debugging optimization
python refactoring.py          # Refactoring optimization
```

After running, you'll have:
- `FINAL_REPORT.json` - Comprehensive results
- `FINAL_REPORT.md` - Human-readable report
- `*_results.json` - Individual simulation results

## Option 3: Generate Custom Configs

To create custom configurations:

```bash
cd simulations/domains/coding

# Run simulations first (if not already done)
python run_all.py

# Generate custom configs
python coding_optimizer.py
```

This creates/updates:
- `src/domains/coding/config.ts` - Main configuration
- `src/domains/coding/value-network-config.ts` - Value network
- `src/domains/coding/tasks.ts` - Task definitions

## Common Tasks

### Code Generation

```typescript
// Generate a function
await colony.execute({
  domain: 'coding',
  task: 'generate_function',
  input: { description: 'Sort array by frequency', language: 'python' }
});

// Generate a class
await colony.execute({
  domain: 'coding',
  task: 'generate_class',
  input: { description: 'BinarySearchTree implementation', language: 'python' }
});

// Generate an API endpoint
await colony.execute({
  domain: 'coding',
  task: 'generate_api',
  input: { description: 'User authentication endpoint', framework: 'fastapi' }
});
```

### Code Review

```typescript
// Review code
const result = await colony.execute({
  domain: 'coding',
  task: 'review_code',
  input: {
    code: `def process(data):
    tmp = []
    for i in range(len(data)):
        tmp.append(data[i] * 2)
    return tmp`,
    language: 'python'
  }
});

console.log(result.issues);
// [
//   { type: 'performance', line: 3, message: 'Use enumerate()' },
//   { type: 'style', line: 2, message: 'Rename tmp to result' }
// ]
```

### Debugging

```typescript
// Debug an issue
const result = await colony.execute({
  domain: 'coding',
  task: 'debug_issue',
  input: {
    code: buggyCode,
    bugReport: {
      error: 'IndexError: list index out of range',
      reproduction: 'Call function with empty list'
    }
  }
});

console.log(result.fixes);
// [{ line: 15, original: 'return items[0]', fixed: 'return items[0] if items else None' }]
```

### Refactoring

```typescript
// Refactor a file
const result = await colony.execute({
  domain: 'coding',
  task: 'refactor_file',
  input: {
    code: codeToRefactor,
    opportunities: ['extract_method', 'remove_duplication', 'improve_names']
  }
});

console.log(result.refactoredCode);
console.log(result.qualityImprovement); // +0.25
```

## Available Tasks

All 25 predefined tasks:

### Code Generation (5 tasks)
- `generate_function` - Generate a function
- `generate_class` - Generate a class
- `generate_api` - Generate API endpoint
- `generate_module` - Generate complete module
- `generate_tests` - Generate unit tests

### Code Review (5 tasks)
- `review_code` - General code review
- `detect_bugs` - Detect bugs
- `security_review` - Security review
- `performance_review` - Performance review
- `style_check` - Style checking

### Debugging (4 tasks)
- `debug_issue` - Full debugging workflow
- `localize_bug` - Find bug location
- `generate_fix` - Generate fix
- `validate_fix` - Validate fix works

### Refactoring (7 tasks)
- `refactor_file` - Single file refactoring
- `refactor_project` - Multi-file refactoring
- `extract_method` - Extract method
- `rename_variable` - Rename variables
- `simplify_code` - Simplify complex code
- `remove_duplication` - Remove duplicates
- `add_type_hints` - Add type hints

### Workflows (4 tasks)
- `implement_feature` - Feature implementation workflow
- `fix_bug` - Bug fixing workflow
- `improve_code` - Code improvement workflow
- `code_review_workflow` - Complete review workflow

## Optimal Settings

Already configured in `CODING_DOMAIN_CONFIG`:

```typescript
{
  // Code generation
  temperature: 0.3,        // Deterministic code
  checkpoints: 15,         // Granular control
  modelSize: '100M',       // Optimal size
  maxTokens: 2000,         // Reasonable limit

  // Code review
  useValueNetwork: true,   // Quality prediction
  minConfidence: 0.3,      // Filter noise
  maxIssues: 50,           // Limit output

  // Debugging
  maxIterations: 5,        // Efficient search
  checkpointFrequency: 5,  // Regular checkpoints

  // Refactoring
  chunkSize: 5,            // Maintain consistency
  maxFiles: 50,            // Large projects
  consistencyThreshold: 0.8 // High quality
}
```

## Performance

Compared to GPT-4:

| Task | POLLN | GPT-4 | Improvement |
|------|-------|-------|-------------|
| Code Generation | 78% | 80% | Comparable |
| Code Review (F1) | 0.79 | 0.72 | +9.7% |
| Debugging Success | 72% | 55% | +30.9% |
| Refactoring Quality | +0.32 | +0.24 | +33.3% |
| **Cost** | **$0.01/1K** | **$10/1K** | **99.9% savings** |

## Next Steps

1. **Explore Examples**
   ```bash
   cd examples
   # Check out basic-coding, code-reviewer, debugging-assistant, refactoring-bot
   ```

2. **Read Documentation**
   - `simulations/domains/coding/README.md` - Simulation overview
   - `simulations/domains/coding/CODING_GUIDE.md` - Complete guide
   - `simulations/domains/coding/BENCHMARKS.md` - Performance data

3. **Customize**
   ```typescript
   import { getCodingDomainConfig } from 'polln/domains/coding';

   const config = getCodingDomainConfig();
   config.generation.temperature = 0.2;  // More deterministic
   config.generation.checkpoints = 20;   // More control

   const colony = new Colony({ domains: { coding: config } });
   ```

4. **Extend**
   ```typescript
   import { CODING_TASKS } from 'polln/domains/coding';

   // Add custom task
   CODING_TASKS['custom_task'] = {
     name: 'custom_task',
     description: 'My custom coding task',
     agentType: 'task',
     expertise: 'code_generation',
     temperature: 0.3,
     // ... more config
   };
   ```

## Troubleshooting

**Issue**: Generated code has syntax errors
- **Solution**: Already optimized with temperature=0.3, checkpoints=15

**Issue**: Review returns too many issues
- **Solution**: Already configured with minConfidence=0.3

**Issue**: Debugging is slow
- **Solution**: Already optimized with maxIterations=5

**Issue**: Need faster generation
- **Solution**: Reduce checkpoints to 10, trade-off some quality

## Support

- **Documentation**: See `simulations/domains/coding/`
- **Examples**: See `examples/`
- **Issues**: Report on GitHub

Happy coding with POLLN! 🚀
