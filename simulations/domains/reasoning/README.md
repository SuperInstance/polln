# POLLN Reasoning Domain Simulations

Python simulations to optimize POLLN agents for dialogue and multi-step reasoning tasks.

## Overview

This simulation suite optimizes POLLN agents for:

- **Dialogue Management**: Turn-taking, context tracking, persona consistency
- **Chain-of-Thought**: Multi-step reasoning with checkpoints and verification
- **Context Tracking**: Long-term memory, compression, retrieval
- **Reasoning Depth**: Shallow vs deep exploration tradeoffs
- **Consistency Validation**: Self-consistency, factual, temporal, logical

## Directory Structure

```
simulations/domains/reasoning/
├── dialogue_simulation.py      # Dialogue management simulation
├── chain_of_thought.py          # Multi-step reasoning simulation
├── context_tracking.py          # Context compression simulation
├── reasoning_depth.py           # Depth optimization simulation
├── consistency_checker.py       # Consistency validation simulation
├── reasoning_optimizer.py       # Configuration compiler
├── run_all.py                   # Master orchestrator
├── test_reasoning.py            # Test suite
├── README.md                    # This file
├── REASONING_GUIDE.md           # Detailed guide
├── DIALOGUE_DESIGN.md           # Dialogue system design
└── *.json                       # Simulation results
```

## Quick Start

### Run All Simulations

```bash
cd simulations/domains/reasoning
python run_all.py
```

This will:
1. Run all reasoning simulations
2. Compile optimal configuration
3. Generate TypeScript config file
4. Validate results
5. Generate comprehensive report

### Run Individual Simulations

```bash
# Dialogue management
python dialogue_simulation.py

# Chain-of-thought reasoning
python chain_of_thought.py

# Context tracking
python context_tracking.py

# Reasoning depth
python reasoning_depth.py

# Consistency validation
python consistency_checker.py
```

### Generate Configuration Only

```bash
python reasoning_optimizer.py
```

### Run Tests

```bash
python test_reasoning.py
```

## Simulation Modules

### 1. Dialogue Simulation (`dialogue_simulation.py`)

Simulates dialogue scenarios to optimize agent composition.

**Features:**
- Multiple dialogue types (short, long, multi-party, task-oriented, social)
- Turn-taking simulation
- Context tracking and entity extraction
- Persona consistency monitoring
- Context compression strategies

**Metrics:**
- Coherence score
- Relevance score
- Engagement score
- Consistency score
- Context retention

**Output:** `dialogue_results.json`

### 2. Chain-of-Thought (`chain_of_thought.py`)

Simulates multi-step reasoning with checkpoints.

**Features:**
- GSM8K-style math problems
- Self-consistency sampling
- Reasoning chain generation
- Checkpoint optimization strategies
- Verifier integration

**Metrics:**
- Accuracy
- Reasoning quality
- Consensus rate
- Average confidence
- Checkpoint utilization

**Output:** `cot_results.json`

### 3. Context Tracking (`context_tracking.py`)

Simulates long-term context management.

**Features:**
- Entity tracking and relationship inference
- Conversation summarization
- KV-cache optimization
- Memory retrieval system
- Compression strategies (sliding window, hierarchical, hybrid)

**Metrics:**
- Compression ratio
- Information retention
- Retrieval accuracy
- Entity tracking accuracy
- Memory efficiency

**Output:** `context_tracking_results.json`

### 4. Reasoning Depth (`reasoning_depth.py`)

Optimizes depth vs breadth tradeoffs.

**Features:**
- Tree-of-thoughts exploration
- Iterative refinement
- Debate-based reasoning
- Task complexity estimation
- Adaptive depth selection

**Metrics:**
- Solution quality
- Compute cost
- Exploration efficiency
- Optimal depth per task

**Output:** `depth_results.json`

### 5. Consistency Checker (`consistency_checker.py`)

Validates response consistency.

**Features:**
- Self-consistency checking
- Factual consistency validation
- Temporal consistency tracking
- Logical coherence checking
- Persona consistency monitoring

**Metrics:**
- Violation rate
- Detection accuracy
- Consistency score
- False positive rate

**Output:** `consistency_results.json`

### 6. Reasoning Optimizer (`reasoning_optimizer.py`)

Compiles all results into production configuration.

**Features:**
- Loads all simulation results
- Compiles optimal configuration
- Generates TypeScript config file
- Creates summary reports

**Output:**
- `src/domains/reasoning/config.ts` - TypeScript configuration
- `full_config.json` - Complete configuration
- `OPTIMIZATION_SUMMARY.md` - Optimization summary

### 7. Master Orchestrator (`run_all.py`)

Runs complete simulation pipeline.

**Features:**
- Executes all simulations
- Compiles results
- Validates outputs
- Generates comprehensive report

**Output:** `COMPREHENSIVE_REPORT.md`

## Generated Configuration

The simulations generate `src/domains/reasoning/config.ts` with optimal settings:

```typescript
export const REASONING_DOMAIN_CONFIG = {
  // Dialogue management
  dialogue: {
    maxTurns: 100,
    contextWindow: '128K',
    summarizationThreshold: 10,
    entityTracking: true,
    personaConsistency: 'high'
  },

  // Chain-of-thought reasoning
  chainOfThought: {
    enabled: true,
    selfConsistency: { samples: 5, aggregation: 'majority' },
    verifier: { enabled: true, confidence: 0.7 },
    checkpoints: { placement: 'auto' }
  },

  // Context management
  context: {
    compression: { strategy: 'hybrid' },
    kvCache: { enabled: true, strategy: 'attention_prior' },
    memoryRetrieval: { enabled: true, topK: 5 }
  },

  // Reasoning depth
  depth: {
    shallow: { maxSteps: 3, breadth: 10 },
    medium: { maxSteps: 7, breadth: 5 },
    deep: { maxSteps: 15, breadth: 3 }
  },

  // Agent composition
  agents: {
    reasoner: { type: 'role', expertise: 'logical_reasoning' },
    verifier: { type: 'task', expertise: 'verification' },
    summarizer: { type: 'task', expertise: 'summarization' }
  }
};
```

## Results Files

After running simulations, you'll find:

- `dialogue_results.json` - Dialogue optimization results
- `cot_results.json` - Chain-of-thought results
- `context_tracking_results.json` - Context management results
- `depth_results.json` - Reasoning depth results
- `consistency_results.json` - Consistency validation results
- `full_config.json` - Compiled configuration
- `COMPREHENSIVE_REPORT.md` - Full report
- `OPTIMIZATION_SUMMARY.md` - Optimization summary

## Testing

Run the test suite:

```bash
python test_reasoning.py
```

Tests cover:
- Dialogue simulation correctness
- Chain-of-thought reasoning
- Context tracking
- Reasoning depth optimization
- Consistency validation
- Metrics validation
- Integration tests

## Requirements

```bash
pip install numpy
```

## Integration with POLLN

The generated configuration can be imported into POLLN:

```typescript
import { REASONING_DOMAIN_CONFIG } from '@polln/reasoning';

// Use in agent initialization
const agent = new PollnAgent({
  domain: 'reasoning',
  config: REASONING_DOMAIN_CONFIG
});
```

## Contributing

To add new reasoning simulations:

1. Create simulation file in `simulations/domains/reasoning/`
2. Follow the pattern of existing simulations
3. Add to orchestrator in `run_all.py`
4. Update optimizer to include new results
5. Add tests to `test_reasoning.py`

## License

Part of the POLLN project. See main LICENSE file.
