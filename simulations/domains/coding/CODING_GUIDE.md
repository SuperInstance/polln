# POLLN Coding Domain Guide

Complete guide for using POLLN optimized for software development tasks.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Domain Configuration](#domain-configuration)
3. [Code Generation](#code-generation)
4. [Code Review](#code-review)
5. [Debugging](#debugging)
6. [Refactoring](#refactoring)
7. [Value Network](#value-network)
8. [Best Practices](#best-practices)
9. [Advanced Usage](#advanced-usage)
10. [Troubleshooting](#troubleshooting)

## Quick Start

### Installation

```bash
# Install POLLN
npm install polln

# For coding domain
npm install polln/dist/domains/coding
```

### Basic Usage

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
    description: 'Calculate fibonacci numbers',
    language: 'python'
  }
});
```

## Domain Configuration

### Main Configuration

The coding domain is configured via `CODING_DOMAIN_CONFIG`:

```typescript
export const CODING_DOMAIN_CONFIG = {
  // Code generation settings
  generation: {
    temperature: 0.3,      // Low temperature for deterministic code
    topP: 0.9,
    frequencyPenalty: 0.1,
    stopTokens: ['```', '\\n\\n'],
    maxTokens: 2000,
    checkpoints: 15       // High granularity for code
  },

  // Agent configurations
  agents: {
    generator: {
      type: 'role',
      expertise: 'code_generation',
      modelSize: '100M',
      checkpoints: 15
    },
    reviewer: {
      type: 'role',
      expertise: 'code_review',
      modelSize: '100M',
      valueNetwork: 'code_quality'
    },
    debugger: {
      type: 'task',
      expertise: 'debugging',
      iterative: true,
      maxIterations: 5
    }
  },

  // Value network for code quality
  valueFunction: {
    features: [
      'syntactic_correctness',
      'semantic_correctness',
      'test_coverage',
      'complexity',
      'maintainability',
      'security_score'
    ],
    weights: {
      correctness: 0.5,
      test_pass_rate: 0.3,
      maintainability: 0.1,
      security: 0.1
    }
  },

  // Refactoring settings
  refactoring: {
    multiFile: true,
    consistency: 'high',
    maxFiles: 50,
    chunkSize: 5
  }
};
```

### Custom Configuration

```typescript
import { Colony } from 'polln/core';
import { CODING_DOMAIN_CONFIG } from 'polln/domains/coding';

// Customize configuration
const customConfig = {
  ...CODING_DOMAIN_CONFIG,
  generation: {
    ...CODING_DOMAIN_CONFIG.generation,
    temperature: 0.2,  // Even more deterministic
    checkpoints: 20     // More granular control
  }
};

const colony = new Colony({
  domains: {
    coding: customConfig
  }
});
```

## Code Generation

### Function Generation

```typescript
const result = await colony.execute({
  domain: 'coding',
  task: 'generate_function',
  input: {
    description: 'Calculate the nth Fibonacci number',
    language: 'python',
    requirements: [
      'Handle edge cases (n < 0)',
      'Use memoization for efficiency',
      'Include type hints'
    ],
    testCases: [
      'fib(0) == 0',
      'fib(1) == 1',
      'fib(10) == 55'
    ]
  }
});

console.log(result.code);
```

### Class Generation

```typescript
const result = await colony.execute({
  domain: 'coding',
  task: 'generate_class',
  input: {
    description: 'Stack implementation with push, pop, and peek',
    language: 'python',
    requirements: [
      'Generic implementation',
      'Error handling for empty stack',
      'O(1) operations'
    ]
  }
});
```

### API Generation

```typescript
const result = await colony.execute({
  domain: 'coding',
  task: 'generate_api',
  input: {
    description: 'REST API endpoint for user authentication',
    framework: 'fastapi',
    requirements: [
      'JWT token generation',
      'Input validation',
      'Error handling',
      'Rate limiting'
    ]
  }
});
```

## Code Review

### Basic Review

```typescript
const result = await colony.execute({
  domain: 'coding',
  task: 'review_code',
  input: {
    code: `
def process_data(data):
    tmp = []
    for i in range(len(data)):
        tmp.append(data[i] * 2)
    return tmp
`,
    language: 'python',
    focus: ['bugs', 'security', 'performance']
  }
});

console.log(result.issues);
// [
//   { type: 'performance', line: 3, message: 'Use enumerate()' },
//   { type: 'style', line: 2, message: 'Rename tmp to more descriptive name' }
// ]
```

### Custom Review Rules

```typescript
const result = await colony.execute({
  domain: 'coding',
  task: 'review_code',
  input: {
    code: codeToReview,
    customRules: [
      {
        pattern: 'print\\(',
        message: 'Use logging instead of print',
        severity: 'low'
      },
      {
        pattern: 'except:',
        message: 'Specify exception type',
        severity: 'high'
      }
    ]
  }
});
```

### Value Network Integration

The code reviewer uses a value network to prioritize issues:

```typescript
import { CODE_QUALITY_VALUE_CONFIG } from 'polln/domains/coding';

// Value network predicts code quality
const qualityScore = await valueNetwork.predict({
  syntactic_correctness: 1.0,
  semantic_correctness: 0.8,
  test_coverage: 0.6,
  complexity: 0.7,
  maintainability: 0.5,
  security_score: 0.9
});

// Returns: 0.75 (overall quality score)
```

## Debugging

### Bug Localization

```typescript
const result = await colony.execute({
  domain: 'coding',
  task: 'localize_bug',
  input: {
    code: codeWithBug,
    bugReport: {
      type: 'runtime',
      error: 'IndexError: list index out of range',
      reproduction: 'Call function with empty list',
      expected: 'Handle empty list gracefully',
      actual: 'Crashes with IndexError'
    },
    strategy: 'incremental'  // or 'symbolic', 'binary_search', etc.
  }
});

console.log(result.locations);
// [{ file: 'main.py', line: 15, confidence: 0.85 }]
```

### Fix Generation

```typescript
const result = await colony.execute({
  domain: 'coding',
  task: 'debug_issue',
  input: {
    code: buggyCode,
    bugReport: bugReport,
    maxIterations: 5,
    validateFixes: true
  }
});

console.log(result.fixes);
// [
//   {
//     line: 15,
//     original: 'return items[0]',
//     fixed: 'return items[0] if items else None',
//     confidence: 0.9
//   }
// ]
```

### Iterative Debugging

The debugger uses iterative reasoning with checkpoints:

```typescript
const debugger = colony.getAgent('debugger');

// Each iteration uses a different strategy
for (let i = 0; i < 5; i++) {
  const iteration = await debugger.debug(code, bugReport, {
    iteration: i,
    strategy: ['incremental', 'hypothesis', 'symbolic', 'binary_search'][i]
  });

  if (iteration.fixed) {
    break;
  }
}
```

## Refactoring

### Single File Refactoring

```typescript
const result = await colony.execute({
  domain: 'coding',
  task: 'refactor_file',
  input: {
    code: codeToRefactor,
    opportunities: [
      'extract_method',
      'remove_duplication',
      'improve_names'
    ]
  }
});

console.log(result.refactoredCode);
console.log(result.qualityImprovement);  // +0.25
```

### Multi-File Refactoring

```typescript
const result = await colony.execute({
  domain: 'coding',
  task: 'refactor_project',
  input: {
    files: {
      'main.py': mainCode,
      'utils.py': utilsCode,
      'config.py': configCode
    },
    consistency: 'high',
    chunkSize: 5
  }
});

console.log(result.changes);
// {
//   'main.py': [{ type: 'extract_method', line: 15 }],
//   'utils.py': [{ type: 'rename', line: 8 }],
//   'config.py': [{ type: 'extract_constant', line: 3 }]
// }
```

### Consistency Checking

```typescript
// Ensure cross-file consistency
const consistency = await colony.execute({
  domain: 'coding',
  task: 'check_consistency',
  input: {
    files: projectFiles,
    checks: [
      'naming_conventions',
      'import_patterns',
      'error_handling'
    ]
  }
});

console.log(consistency.score);  // 0.85
console.log(consistency.issues);
```

## Value Network

### Training the Value Network

```typescript
import { ValueNetworkManager } from 'polln/core';
import { CODE_QUALITY_VALUE_CONFIG } from 'polln/domains/coding';

const manager = new ValueNetworkManager(CODE_QUALITY_VALUE_CONFIG);

// Train with code quality data
await manager.train({
  samples: [
    {
      features: [1.0, 0.9, 0.8, 0.7, 0.6, 0.9],
      label: 0.85  // High quality code
    },
    {
      features: [0.5, 0.6, 0.3, 0.3, 0.4, 0.5],
      label: 0.45  // Lower quality code
    }
  ]
});
```

### Using the Value Network

```typescript
// Predict code quality
const quality = await manager.predict({
  syntactic_correctness: 1.0,
  semantic_correctness: 0.9,
  test_coverage: 0.8,
  complexity: 0.6,
  maintainability: 0.7,
  security_score: 0.9
});

// Use for agent selection
if (quality > 0.7) {
  // Code is good enough, proceed
} else {
  // Request review or refactoring
}
```

## Best Practices

### Code Generation

1. **Use Lower Temperature**: Code should be deterministic
   ```typescript
   temperature: 0.3
   ```

2. **High Checkpoint Frequency**: More granular control
   ```typescript
   checkpoints: 15
   ```

3. **Clear Requirements**: Specify exactly what you need
   ```typescript
   requirements: [
     'Include type hints',
     'Add docstrings',
     'Handle edge cases'
   ]
   ```

4. **Provide Test Cases**: Helps validate semantic correctness
   ```typescript
   testCases: [
     'fib(0) == 0',
     'fib(1) == 1'
   ]
   ```

### Code Review

1. **Specify Focus Areas**: Target specific issue types
   ```typescript
   focus: ['security', 'performance']
   ```

2. **Use Value Network**: Prioritize high-impact issues
   ```typescript
   useValueNetwork: true
   ```

3. **Set Confidence Threshold**: Filter low-confidence detections
   ```typescript
   minConfidence: 0.3
   ```

### Debugging

1. **Provide Detailed Bug Reports**: Include error messages
   ```typescript
   bugReport: {
     error: 'IndexError: list index out of range',
     reproduction: 'Call with empty list'
   }
   ```

2. **Limit Iterations**: Prevent infinite loops
   ```typescript
   maxIterations: 5
   ```

3. **Validate Fixes**: Ensure fixes don't break things
   ```typescript
   validateFixes: true
   ```

### Refactoring

1. **Process in Chunks**: Maintain consistency
   ```typescript
   chunkSize: 5
   ```

2. **Set Consistency Threshold**: Ensure quality
   ```typescript
   consistencyThreshold: 0.8
   ```

3. **Test After Refactoring**: Validate changes
   ```typescript
   runTests: true
   ```

## Advanced Usage

### Custom Agents

```typescript
import { RoleAgent } from 'polln/core';

const customReviewer = new RoleAgent({
  name: 'custom_reviewer',
  expertise: 'security_review',
  modelSize: '200M',
  temperature: 0.2,
  valueNetwork: 'security_quality'
});

colony.addAgent(customReviewer);
```

### Custom Value Functions

```typescript
const customValueFunction = {
  features: ['complexity', 'maintainability', 'security'],
  weights: {
    complexity: 0.3,
    maintainability: 0.4,
    security: 0.3
  },
  calculate: (features) => {
    return features.complexity * 0.3 +
           features.maintainability * 0.4 +
           features.security * 0.3;
  }
};
```

### Pipelines

```typescript
const pipeline = [
  { task: 'generate_function' },
  { task: 'review_code' },
  { task: 'refactor_file', if: (r) => r.quality < 0.7 },
  { task: 'run_tests' }
];

const result = await colony.executePipeline(pipeline, input);
```

## Troubleshooting

### Common Issues

**Issue**: Generated code has syntax errors
- **Solution**: Lower temperature (0.2-0.3), increase checkpoints

**Issue**: Review returns too many false positives
- **Solution**: Increase minConfidence threshold (0.4-0.5)

**Issue**: Debugging doesn't find the bug
- **Solution**: Try different strategies, provide more detailed bug report

**Issue**: Refactoring breaks tests
- **Solution**: Lower consistency threshold, enable test validation

### Performance Tuning

**Slow Code Generation**:
```typescript
checkpoints: 10  // Reduce from 15
maxTokens: 1500  // Reduce from 2000
```

**Slow Code Review**:
```typescript
maxIssuesPerReview: 30  // Limit issues
```

**Slow Debugging**:
```typescript
maxIterations: 3  // Reduce iterations
```

### Getting Help

- Check the [main README](README.md) for overview
- See [BENCHMARKS.md](BENCHMARKS.md) for performance data
- Review simulation results in `*_results.json`
- Run tests: `python test_coding.py`

## Examples

See the `examples/` directory for complete examples:
- `basic-coding/` - Simple coding tasks
- `code-reviewer/` - Automated code review
- `debugging-assistant/` - Bug fixing
- `refactoring-bot/` - Automated refactoring
