# POLLN Coding Domain Simulations

Comprehensive Python simulation suite for optimizing POLLN agents for software development tasks.

## Overview

This simulation suite models and optimizes POLLN agents for coding workflows including code generation, review, debugging, and refactoring. The simulations use realistic coding task modeling, HumanEval benchmarking, and generate production-ready configurations.

## Simulation Modules

### 1. Code Generation (`code_generation.py`)

Simulates code generation workflows with checkpoint-based generation.

**Features:**
- Function, class, API, and multi-file generation
- Syntactic and semantic correctness validation
- Test pass rate measurement
- Baseline comparison to GPT-4/Claude
- Checkpoint frequency optimization

**Metrics:**
- Syntactic correctness (parsable code)
- Semantic correctness (passes tests)
- Test pass rate
- Generation time
- Tokens used

**Usage:**
```python
from code_generation import POLLNCodeGenerator, create_human_eval_tasks

generator = POLLNCodeGenerator(temperature=0.3, checkpoints=15)
tasks = create_human_eval_tasks()

for task in tasks:
    result = generator.generate(task)
    print(f"Success: {result.success}, Score: {result.semantic_correctness:.2f}")
```

### 2. Code Review (`code_review.py`)

Simulates code review workflows with value network integration.

**Features:**
- Bug, security, style, performance, and maintainability detection
- Precision/recall/F1 measurement
- Value network for quality prediction
- Priority-based issue filtering
- Configuration optimization

**Metrics:**
- Precision (correct bugs flagged / total flagged)
- Recall (correct bugs flagged / total bugs)
- F1 score
- False positive rate
- Review time

**Usage:**
```python
from code_review import POLLNCodeReviewer, create_code_samples

reviewer = POLLNCodeReviewer(use_value_network=True)
samples = create_code_samples()

for sample in samples:
    result = reviewer.review(sample)
    print(f"F1: {result.f1:.2f}, Issues: {len(result.issues_found)}")
```

### 3. Debugging (`debugging_simulation.py`)

Simulates debugging workflows with iterative reasoning.

**Features:**
- Multiple debugging strategies (binary search, symbolic execution, etc.)
- Bug localization
- Fix generation and validation
- Iterative reasoning with checkpoints
- Workflow optimization

**Metrics:**
- Bugs found
- Bugs fixed
- Iterations needed
- Time to fix
- Success rate

**Usage:**
```python
from debugging_simulation import POLLNDebugger, create_bug_reports

debugger = POLLNDebugger(max_iterations=5, checkpoint_frequency=5)
bug_reports = create_bug_reports()

for bug_report in bug_reports:
    result = debugger.debug(code, bug_report)
    print(f"Fixed: {result.success}, Iterations: {result.total_iterations}")
```

### 4. Refactoring (`refactoring.py`)

Simulates code refactoring workflows with multi-file consistency.

**Features:**
- Single and multi-file refactoring
- Cross-file consistency checking
- Quality improvement measurement
- Batch refactoring
- Configuration optimization

**Metrics:**
- Quality improvement (maintainability, complexity)
- Consistency maintained
- Files processed
- Refactoring time

**Usage:**
```python
from refactoring import POLLNRefactoringAgent, create_project_files

agent = POLLNRefactoringAgent(chunk_size=5, max_files=50)
files = create_project_files()

# Single file
results, quality = agent.refactor_file("main.py", code)

# Multi-file
project_results = agent.refactor_project(files)
```

### 5. Code Metrics (`code_metrics.py`)

Implements code quality metrics and reward functions.

**Features:**
- Cyclomatic complexity analysis
- Maintainability index calculation
- Test coverage estimation
- Security analysis
- Code smell detection
- Value network feature extraction

**Metrics:**
- Cyclomatic complexity
- Maintainability index (0-1)
- Test coverage (0-1)
- Security score (0-1)
- Code smells

**Usage:**
```python
from code_metrics import CodeMetricsAnalyzer

analyzer = CodeMetricsAnalyzer()
report = analyzer.analyze("example.py", code, test_code)

print(f"Overall Score: {report.overall_score:.2f}")
for metric in report.metrics:
    print(f"  {metric.name}: {metric.value:.2f}")
```

### 6. Coding Optimizer (`coding_optimizer.py`)

Compiles optimal configurations from simulation results.

**Features:**
- Loads all simulation results
- Compiles optimal configuration
- Generates TypeScript config files
- Creates task definitions
- Value network configuration

**Output Files:**
- `src/domains/coding/config.ts` - Main configuration
- `src/domains/coding/value-network-config.ts` - Value network
- `src/domains/coding/tasks.ts` - Task definitions

### 7. Master Orchestrator (`run_all.py`)

Runs all simulations and generates configurations.

**Usage:**
```bash
python run_all.py
```

This will:
1. Run all simulations
2. Generate configuration files
3. Create final report (JSON and Markdown)

## Running Simulations

### Run Individual Simulation

```bash
# Code generation
python code_generation.py

# Code review
python code_review.py

# Debugging
python debugging_simulation.py

# Refactoring
python refactoring.py

# Code metrics
python code_metrics.py
```

### Run All Simulations

```bash
python run_all.py
```

### Run Tests

```bash
python test_coding.py
```

## Output Files

Each simulation generates a results file:
- `code_generation_results.json`
- `code_review_results.json`
- `debugging_results.json`
- `refactoring_results.json`

The orchestrator generates:
- `FINAL_REPORT.json` - Complete results
- `FINAL_REPORT.md` - Human-readable report
- `src/domains/coding/config.ts` - TypeScript configuration

## Key Findings

### Optimal Configurations

**Code Generation:**
- Temperature: 0.3 (lower for deterministic code)
- Checkpoints: 15 (high granularity for control)
- Model Size: 100M
- Max Tokens: 2000

**Code Review:**
- Model Size: 100M
- Use Value Network: True
- Min Confidence: 0.3
- Priority Filtering: True

**Debugging:**
- Max Iterations: 5
- Checkpoint Frequency: 5
- Use Iterative Reasoning: True
- Strategy Sequence: incremental → hypothesis → symbolic → binary search

**Refactoring:**
- Chunk Size: 5 files
- Max Files: 50
- Consistency Threshold: 0.8
- Batch Refactoring: True

## Architecture

```
simulations/domains/coding/
├── code_generation.py      # Code generation simulation
├── code_review.py          # Code review simulation
├── debugging_simulation.py # Debugging simulation
├── refactoring.py          # Refactoring simulation
├── code_metrics.py         # Code quality metrics
├── coding_optimizer.py     # Configuration compiler
├── run_all.py             # Master orchestrator
├── test_coding.py         # Test suite
├── README.md              # This file
├── CODING_GUIDE.md        # Detailed guide
├── BENCHMARKS.md          # Benchmark results
└── docs/
    ├── ARCHITECTURE.md    # System architecture
    └── API.md             # API documentation
```

## Dependencies

- Python 3.8+
- NumPy
- AST (standard library)

No external ML frameworks required - simulations are self-contained.

## Integration with POLLN

The generated TypeScript configurations integrate with the POLLN system:

```typescript
import { CODING_DOMAIN_CONFIG } from './domains/coding/config';

// Use in colony configuration
const colony = new Colony({
  domains: {
    coding: CODING_DOMAIN_CONFIG
  }
});
```

## Contributing

When adding new simulations:
1. Follow the existing structure
2. Include proper metrics measurement
3. Generate JSON results
4. Add tests to `test_coding.py`
5. Update this README

## License

MIT License - See LICENSE file for details.
