# SMP Baseline Comparison Infrastructure

Compare SMP tile chains vs monolithic LLM calls on latency, accuracy, confidence, and energy.

## Overview

The baseline comparison infrastructure provides **fair, accuracy-equivalent** comparisons between:
- **Monolithic LLM**: Single large model call (e.g., GPT-4)
- **SMP Tile Chains**: Composed tile networks (sequential, parallel, mixed)

### Key Features

1. **Accuracy-Equivalent Comparison**: Find tile chains that match baseline accuracy within tolerance
2. **Pareto Frontier Analysis**: Identify non-dominated solutions across multiple metrics
3. **Multiple Tile Patterns**: Test sequential, parallel, and hybrid tile configurations
4. **Comprehensive Metrics**: Latency, accuracy, confidence, energy, throughput, memory
5. **Multiple Report Formats**: Text, JSON, Markdown, HTML

## Quick Start

```typescript
import { runComparison } from './baseline-comparison.js';

// Run a comparison
const report = await runComparison(
  'I love this product!',  // prompt
  'sentiment',             // task type
  'text'                   // format
);

console.log(report);
```

## Architecture

### Core Components

```
MonolithicBaseline         // Monolithic LLM wrapper
    ├── execute()          // Run LLM call
    └── simulateLLM()      // Simulate LLM response

TileChainBuilder          // Build tile patterns
    ├── buildSequential()  // Sequential chain
    ├── buildParallel()    // Parallel ensemble
    ├── buildMixed()       // Hybrid pattern
    └── estimateMetrics()  // Predict performance

AccuracyEquivalentFinder // Find accuracy-matched chains
    ├── findEquivalent()   // Filter by accuracy
    └── adjustToTarget()   // Tune to target accuracy

ParetoFrontierCalculator  // Pareto analysis
    ├── calculate()        // Find frontier
    ├── dominates()        // Check domination
    └── rank()            // Rank solutions

ComparisonEngine          // Main comparison engine
    ├── compare()         // Run full comparison
    ├── runBaseline()     // Execute monolithic
    └── runSMPPatterns()  // Execute tile chains

ComparisonReportGenerator // Report generation
    ├── generateText()    // Text format
    ├── generateJSON()    // JSON format
    ├── generateMarkdown()// Markdown format
    └── generateHTML()    // HTML format
```

### Data Flow

```
1. User provides prompt and task type
       ↓
2. MonolithicBaseline runs LLM call
       ↓
3. TileChainBuilder creates patterns
       ↓
4. ComparisonEngine executes both
       ↓
5. ParetoFrontierCalculator ranks results
       ↓
6. ComparisonReportGenerator outputs report
```

## Test Cases

### 1. Sentiment Analysis

**Single Tile vs Tile Chain**

```typescript
const report = await runComparison(
  'I absolutely love this product! It works great.',
  'sentiment'
);
```

**Monolithic Approach:**
- Single LLM call
- Latency: ~100ms
- Accuracy: 85%

**SMP Sequential Chain:**
1. Tokenizer (10ms)
2. Sentiment Lexicon (5ms)
3. Sentiment Classifier (15ms)
4. Confidence Calculator (5ms)
- Total Latency: 35ms
- Accuracy: 88%

**Improvement:**
- Latency: -65%
- Accuracy: +3.5%

### 2. Document Classification

**Parallel Tiles**

```typescript
const report = await runComparison(
  'AI researchers developed a new machine learning algorithm.',
  'classification'
);
```

**Monolithic:**
- Single classification call
- Latency: 120ms
- Accuracy: 80%

**SMP Parallel Ensemble:**
1. Feature Extractor (15ms)
2. Classifier A (18ms) ┐
3. Classifier B (20ms) ├→ Parallel
4. Classifier C (15ms) ┘
5. Meta Classifier (10ms)
- Total Latency: 40ms (max parallel + sequential)
- Accuracy: 85%

**Improvement:**
- Latency: -67%
- Accuracy: +6.25%

### 3. Multi-step Reasoning

**Sequential Chain**

```typescript
const report = await runComparison(
  'If all Bloops are Razzies and all Razzies are Lazzies, are all Bloops definitely Lazzies?',
  'reasoning'
);
```

**Monolithic:**
- Single reasoning call
- Latency: 500ms
- Accuracy: 75%

**SMP Sequential Chain:**
1. Problem Parser (10ms)
2. Knowledge Retriever (20ms)
3. Reasoning Engine (30ms)
4. Conclusion Validator (15ms)
- Total Latency: 75ms
- Accuracy: 82%

**Improvement:**
- Latency: -85%
- Accuracy: +9.3%

## API Reference

### `runComparison()`

Run a single comparison.

```typescript
async function runComparison(
  prompt: string,              // Input prompt
  taskType: string,           // Task type: 'sentiment' | 'classification' | 'reasoning'
  format?: 'text' | 'json' | 'markdown' | 'html'  // Report format
): Promise<string>
```

### `MonolithicBaseline`

Monolithic LLM wrapper.

```typescript
class MonolithicBaseline {
  constructor(modelId: string, latencyOverhead: number = 100)

  async execute(
    prompt: string,
    context: ExecutionContext
  ): Promise<BaselineResult>
}
```

### `TileChainBuilder`

Build tile patterns.

```typescript
class TileChainBuilder {
  static buildSequential(taskType: string): TilePattern
  static buildParallel(taskType: string): TilePattern
  static buildMixed(taskType: string): TilePattern
  static estimateMetrics(pattern: TilePattern): {
    latency: number
    confidence: number
    energy: number
  }
}
```

### `ComparisonEngine`

Main comparison engine.

```typescript
class ComparisonEngine {
  constructor(baseline: MonolithicBaseline)

  async compare(
    prompt: string,
    taskType: string,
    context?: Partial<ExecutionContext>
  ): Promise<ComparisonReport>
}
```

### `ComparisonReport`

Comparison result.

```typescript
interface ComparisonReport {
  id: string
  task: string
  prompt: string
  baseline: BaselineResult
  smpResults: BaselineResult[]
  winner: 'monolithic' | 'smp' | 'tie'
  improvement: {
    latency: number      // percentage improvement
    accuracy: number     // percentage difference
    energy: number       // percentage improvement
  }
  paretoRank: number     // 1 = best
  timestamp: number
}
```

## Running Benchmarks

### Using the Test Runner

```typescript
import { runAllTests, runSingleTest, runCustomBenchmark } from './run-benchmark.js';

// Run all test cases
await runAllTests('text');

// Run single test
await runSingleTest(
  'I love this product!',
  'sentiment',
  'markdown'
);

// Run custom benchmark
await runCustomBenchmark(
  [
    'Great product!',
    'Terrible service.',
    'Just okay.'
  ],
  'sentiment',
  'html'
);
```

### Command Line

```bash
# Run full test suite
npx tsx src/benchmarking/run-benchmark.ts

# Run single prompt
npx tsx src/benchmarking/run-benchmark.ts "I love this!" --task=sentiment

# Specify output format
npx tsx src/benchmarking/run-benchmark.ts --format=markdown

# Custom task type
npx tsx src/benchmarking/run-benchmark.ts "AI is amazing" --task=classification --format=html
```

## Understanding the Results

### Metrics Explained

1. **Latency**: Time to complete the request (lower is better)
2. **Accuracy**: How correct the output is (higher is better)
3. **Confidence**: How confident the system is (higher is better)
4. **Energy**: Computational energy used (lower is better)
5. **Throughput**: Requests per second (higher is better)
6. **Memory**: Memory usage in MB (lower is better)

### Pareto Ranking

Pareto ranking identifies **non-dominated** solutions:
- **Rank 1**: Not dominated by any other solution
- **Rank 2**: Only dominated by Rank 1 solutions
- **Rank N**: Dominated by all higher ranks

A solution **dominates** another if it's:
- Better or equal in ALL metrics
- Strictly better in AT LEAST ONE metric

### Winner Determination

```
if (SMP latency < Baseline latency × 0.9) {
  winner = 'SMP';
} else if (Baseline latency < SMP latency × 0.9) {
  winner = 'Monolithic';
} else {
  winner = 'tie';
}
```

## Example Output

### Text Format

```
================================================================================
SMP BASELINE COMPARISON REPORT
================================================================================

Task: sentiment
Prompt: "I absolutely love this product!"
--------------------------------------------------------------------------------
MONOLITHIC BASELINE
--------------------------------------------------------------------------------
Latency:      100.00 ms
Accuracy:     85.0%
Confidence:   85.0%
Energy:       250.00 units
Throughput:   10.00 req/s
Memory:       2000 MB

--------------------------------------------------------------------------------
SMP TILE CHAINS
--------------------------------------------------------------------------------
Pattern 1: sequential (4 tiles)
Latency:      35.00 ms
Accuracy:     88.0%
Confidence:   88.0%
Energy:       17.50 units
Throughput:   28.57 req/s
Memory:       200 MB

Pattern 2: parallel (5 tiles)
Latency:      28.00 ms
Accuracy:     90.0%
Confidence:   90.0%
Energy:       15.50 units
Throughput:   35.71 req/s
Memory:       250 MB

...
```

### JSON Format

```json
{
  "id": "uuid",
  "task": "sentiment",
  "prompt": "I love this product!",
  "baseline": {
    "approach": "monolithic",
    "metrics": {
      "latency": 100,
      "accuracy": 0.85,
      "confidence": 0.85,
      "energy": 250,
      "throughput": 10,
      "memory": 2000
    }
  },
  "smpResults": [...],
  "winner": "smp",
  "improvement": {
    "latency": 65.0,
    "accuracy": 3.5,
    "energy": 93.0
  },
  "paretoRank": 1
}
```

## Extending the Framework

### Adding New Task Types

```typescript
// In TileChainBuilder.buildSequential()
case 'mytask':
  tiles.push(
    { id: 'tile1', name: 'Tile 1', type: 'preprocessing', estimatedConfidence: 1.0, estimatedLatency: 10 },
    { id: 'tile2', name: 'Tile 2', type: 'analysis', estimatedConfidence: 0.85, estimatedLatency: 20 }
  );
  break;

// In MonolithicBaseline.simulateLLM()
case 'mytask':
  return this.simulateMyTask(prompt);
```

### Custom Metrics

Add new metrics to `ComparisonMetrics`:

```typescript
export interface ComparisonMetrics {
  latency: number;
  accuracy: number;
  confidence: number;
  energy: number;
  throughput: number;
  memory: number;
  cost: number;        // NEW: Dollar cost
  carbon: number;      // NEW: Carbon emissions
}
```

### Custom Tile Patterns

```typescript
const customPattern: TilePattern = {
  type: 'custom',
  tiles: [
    // Your tiles
  ],
  connections: [
    // Your connections
  ]
};
```

## Performance Tips

1. **Warmup Runs**: Enable warmup for consistent measurements
2. **Multiple Iterations**: Run multiple iterations and average
3. **Accuracy Tolerance**: Adjust tolerance for finding equivalent chains
4. **Parallel Execution**: Execute tile patterns in parallel when possible

## Limitations

1. **Simulated LLM**: Current implementation uses simulated LLM calls
2. **Fixed Tile Patterns**: Predefined patterns for each task type
3. **Simplified Metrics**: Energy and memory are estimated, not measured
4. **No Learning**: Tiles don't adapt based on feedback (yet)

## Future Work

1. **Real LLM Integration**: Connect to actual LLM APIs
2. **Automatic Tile Discovery**: AI finds optimal tile decomposition
3. **Learning Tiles**: Tiles that improve with use
4. **Distributed Execution**: Run tiles across multiple machines
5. **Energy Measurement**: Actual energy consumption measurements
6. **More Task Types**: Translation, summarization, code generation

## Contributing

To add new features:

1. Update types in `baseline-comparison.ts`
2. Add implementation in appropriate class
3. Add test cases to `run-benchmark.ts`
4. Update this README

## License

MIT
