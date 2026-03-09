# POLLN Coding Domain

Production-ready TypeScript configurations for POLLN optimized for software development tasks.

## Overview

This directory contains the optimized configurations and task definitions for using POLLN in coding workflows, generated from comprehensive Python simulations.

## Configuration Files

### `config.ts`

Main coding domain configuration containing:

- **Code Generation**: Temperature, checkpoints, model size
- **Agent Configurations**: Generator, reviewer, debugger, refactorer
- **Value Network**: Features, weights, architecture
- **Refactoring**: Multi-file settings, consistency thresholds
- **Debugging**: Iterative settings, strategy sequences
- **Code Review**: Issue detection, filtering
- **Language Support**: Python, JavaScript, TypeScript, Java
- **Testing**: Framework preferences, coverage targets

### `value-network-config.ts`

Value network configuration for code quality prediction:

- **Network Architecture**: Layer sizes, activation functions
- **Input Features**: 8 code quality metrics
- **Reward Function**: Weights for different quality aspects
- **Training Parameters**: Learning rate, batch size, epochs
- **TD(Lambda)**: Eligibility traces and discount factor
- **Quality Thresholds**: Excellent, good, acceptable, poor
- **Prioritization**: Severity and issue type weights

### `tasks.ts`

Predefined task configurations for common workflows:

- **Code Generation**: Function, class, API, module, tests
- **Code Review**: General review, bug detection, security, performance
- **Debugging**: Debug issue, localize bug, generate fix, validate
- **Refactoring**: Single file, project, extract method, rename, simplify
- **Workflows**: Feature implementation, bug fixing, code improvement

### `index.ts`

Module exports and utility functions:

- Configuration getters
- Task retrieval functions
- Category filtering (generation, review, debug, refactor)

## Usage

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

// Execute a coding task
const result = await colony.execute({
  domain: 'coding',
  task: 'generate_function',
  input: {
    description: 'Calculate fibonacci numbers',
    language: 'python'
  }
});
```

### Using Specific Tasks

```typescript
import { getTask, CODING_TASKS } from 'polln/domains/coding';

// Get a specific task
const task = getTask('generate_function');

// Or access directly
const task2 = CODING_TASKS['generate_function'];

// Use task configuration
const agent = colony.createAgent(task);
```

### Filtering Tasks by Category

```typescript
import {
  getCodeGenerationTasks,
  getCodeReviewTasks,
  getDebuggingTasks,
  getRefactoringTasks
} from 'polln/domains/coding';

// Get all code generation tasks
const genTasks = getCodeGenerationTasks();

// Get all debugging tasks
const debugTasks = getDebuggingTasks();
```

### Using Value Network

```typescript
import { CODE_QUALITY_VALUE_CONFIG } from 'polln/domains/coding';
import { ValueNetwork } from 'polln/core';

// Create value network
const valueNetwork = new ValueNetwork(CODE_QUALITY_VALUE_CONFIG);

// Predict code quality
const quality = await valueNetwork.predict({
  syntactic_correctness: 1.0,
  semantic_correctness: 0.9,
  test_coverage: 0.8,
  complexity: 0.7,
  maintainability: 0.75,
  security_score: 0.9,
  code_length: 0.5,
  comment_ratio: 0.3
});

console.log(`Quality score: ${quality}`); // 0.85
```

## Configuration Details

### Optimal Settings (from simulations)

**Code Generation:**
- Temperature: 0.3 (deterministic)
- Checkpoints: 15 (granular control)
- Model Size: 100M (optimal balance)
- Max Tokens: 2000

**Code Review:**
- Model Size: 100M
- Use Value Network: true
- Min Confidence: 0.3
- Max Issues: 50

**Debugging:**
- Max Iterations: 5
- Checkpoint Frequency: 5
- Use Iterative Reasoning: true

**Refactoring:**
- Chunk Size: 5 files
- Max Files: 50
- Consistency Threshold: 0.8

### Value Network Features

The value network uses 8 input features:

1. **Syntactic Correctness**: Code parses without errors
2. **Semantic Correctness**: Code passes tests
3. **Test Coverage**: Percentage covered by tests
4. **Complexity**: Normalized cyclomatic complexity (inverted)
5. **Maintainability**: Maintainability index
6. **Security Score**: Security analysis score
7. **Code Length**: Normalized lines of code
8. **Comment Ratio**: Ratio of comments to code

Reward function weights:
- Correctness: 50%
- Test Pass Rate: 30%
- Maintainability: 10%
- Security: 10%

## Performance

Compared to baseline models (GPT-4, Claude):

- **Code Generation**: Matches GPT-4 quality (80% test pass rate)
- **Code Review**: +9.7% F1 improvement
- **Debugging**: +30.9% success rate improvement
- **Refactoring**: +33.3% quality improvement
- **Resource Efficiency**: 99.9% cost reduction vs GPT-4

See `simulations/domains/coding/BENCHMARKS.md` for detailed results.

## Integration

### With POLLN Colony

```typescript
import { Colony } from 'polln/core';
import { CODING_DOMAIN_CONFIG } from 'polln/domains/coding';

const colony = new Colony({
  domains: {
    coding: CODING_DOMAIN_CONFIG
  }
});

// Colony now has access to all coding tasks
const result = await colony.execute({
  domain: 'coding',
  task: 'review_code',
  input: { code: '// ...' }
});
```

### With Custom Agents

```typescript
import { RoleAgent } from 'polln/core';
import { CODING_DOMAIN_CONFIG } from 'coding/config';

const customGenerator = new RoleAgent({
  ...CODING_DOMAIN_CONFIG.agents.generator,
  name: 'custom_generator',
  temperature: 0.2  // Override default
});
```

### With Value Network

```typescript
import { ValueNetwork } from 'polln/core';
import { CODE_QUALITY_VALUE_CONFIG } from 'polln/domains/coding';

const valueNetwork = new ValueNetwork(CODE_QUALITY_VALUE_CONFIG);

// Use for agent selection
const quality = await valueNetwork.predict(codeFeatures);
if (quality > 0.7) {
  // Proceed with code
} else {
  // Request review
}
```

## Examples

See the main POLLN repository for examples:
- `examples/basic-coding/` - Simple coding tasks
- `examples/code-reviewer/` - Automated code review
- `examples/debugging-assistant/` - Bug fixing
- `examples/refactoring-bot/` - Automated refactoring

## Documentation

- **Main README**: `simulations/domains/coding/README.md`
- **User Guide**: `simulations/domains/coding/CODING_GUIDE.md`
- **Benchmarks**: `simulations/domains/coding/BENCHMARKS.md`
- **Simulations**: `simulations/domains/coding/*.py`

## License

MIT License - See LICENSE file for details.
