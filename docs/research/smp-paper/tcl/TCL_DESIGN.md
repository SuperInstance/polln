# TCL: Tile Composition Language

**Status:** Design Draft v1.0
**Date:** 2026-03-10
**Authors:** POLLN Research Team

---

## Abstract

TCL (Tile Composition Language) is a domain-specific language for declarative tile graph composition. It enables developers to express complex tile relationships using concise, type-safe syntax inspired by functional programming paradigms. TCL transforms tile composition from imperative wiring to declarative flow.

---

## Table of Contents

1. [Motivation](#motivation)
2. [Design Principles](#design-principles)
3. [Syntax Overview](#syntax-overview)
4. [Core Operators](#core-operators)
5. [Type System](#type-system)
6. [Confidence Constraints](#confidence-constraints)
7. [Stigmergic Rules](#stigmergic-rules)
8. [Examples](#examples)
9. [Formal Semantics](#formal-semantics)
10. [Comparison to Alternatives](#comparison-to-alternatives)
11. [Implementation Roadmap](#implementation-roadmap)

---

## Motivation

### The Problem

As tile ecosystems grow, manual composition becomes unwieldy:

```typescript
// Manual composition (painful)
const tile1 = new TransformerTile({ ... });
const tile2 = new ValidatorTile({ ... });
const tile3 = new RouterTile({ ... });

const result = await tile3.execute(
  await tile2.execute(
    await tile1.execute(input, context),
    context
  ),
  context
);
```

This approach has fatal flaws:
- **No static verification** of type compatibility
- **No confidence propagation** analysis
- **No composition validation** (the "safe tile, unsafe composition" paradox)
- **No declarative optimization** opportunities
- **Error-prone manual wiring**

### The TCL Solution

```tcl
# TCL composition (elegant)
flow fraud_detection {
  input: Transaction

  # Parallel signals with weighted confidence
  (ml_score: 0.5, rules: 0.3, reputation: 0.2) |> validate
    |> confidence_zone(green: 0.85, yellow: 0.60)

  # Conditional routing based on amount
  |> route {
    amount < 1000  ~> basic_validation
    amount < 10000 ~> enhanced_validation
    default        ~> manual_review
  }

  # Final safety check
  |> location_check
    ~> output: Decision
}
```

TCL provides:
- **Static type checking** at compile time
- **Automatic confidence propagation** through chains
- **Composition validation** (detects paradoxes)
- **Declarative optimization** (parallel execution, memoization)
- **Human-readable** graph structure

---

## Design Principles

TCL follows these core principles:

### 1. **Declarative over Imperative**

Describe WHAT, not HOW:

```tcl
# Good: declarative
a |> b |> c

# Bad: imperative
result = execute(a)
result = execute(b, result)
result = execute(c, result)
```

### 2. **Type Safety by Default**

Every composition is type-checked:

```tcl
# Compile-time error: type mismatch
string_processor |> number_consumer  # ERROR!
```

### 3. **Confidence as First-Class Citizen**

Confidence flows through the graph:

```tcl
# Confidence multiplies through sequence
a(conf: 0.9) |> b(conf: 0.8)  # Result: 0.72
```

### 4. **Stigmergy Native**

Pheromone rules are built-in:

```tcl
# Tiles coordinate through pheromones
tile_a ~> deposit(trail, 0.5)
tile_b ~> sense(trail) ~> follow
```

### 5. **Minimal Syntax**

Less is more:

```tcl
# Pipe operator (main composition)
a |> b

# Parallel composition
(a, b, c)

# Conditional routing
route { cond ~> path_a, default ~> path_b }
```

---

## Syntax Overview

### TCL Program Structure

```tcl
# Import tiles
use tiles/fraud_detection
use tiles/validation

# Define a flow
flow my_flow {
  # Type signature
  input: Transaction
  output: Decision

  # Confidence constraints
  require confidence >= 0.85

  # Stigmergic rules
  pheromone trail: decay=0.1

  # Composition
  compose {
    # ... tile graph ...
  }
}
```

### Comments

```tcl
# Single-line comment

#=
Multi-line comment
Can span multiple lines
=#
```

### Identifiers

```tcl
# Variables and tiles
my_tile
anotherTile
camelCase

# Flow names
flow_name
fraud_detection

# Pheromone types
trail
danger
resource
```

---

## Core Operators

### 1. **Sequential Composition (`|>`)**

Pipes output of left tile to input of right tile.

```tcl
# Basic composition
tile_a |> tile_b |> tile_c

# With labels
tile_a |> validate |> transform |> output
```

**Semantics:**
- Types: If `tile_a: A -> B` and `tile_b: B -> C`, then `tile_a |> tile_b: A -> C`
- Confidence: `c_result = c_a * c_b` (multiplies)
- Zone: Zones compose monotonically (GREEN -> YELLOW -> RED)

**Example:**
```tcl
flow transaction_processing {
  compose {
    parse_input
      |> validate_format
      |> check_amount
      |> detect_fraud
      |> make_decision
  }
}
```

### 2. **Parallel Composition (`()`)**

Executes tiles in parallel, combines results.

```tcl
# Unweighted parallel (equal weights)
(tile_a, tile_b, tile_c)

# Weighted parallel
(ml_model: 0.5, rules_engine: 0.3, reputation: 0.2)
```

**Semantics:**
- Types: If `tile_a: A -> B` and `tile_b: C -> D`, then `(tile_a, tile_b): (A, C) -> (B, D)`
- Confidence: Weighted average of confidences
- Zone: Maximum zone (worst case)

**Example:**
```tcl
flow fraud_detection {
  compose {
    # Parallel signals with different weights
    (ml_score: 0.5, rules_engine: 0.3, user_reputation: 0.2)
      |> aggregate_scores
      |> make_decision
  }
}
```

### 3. **Branching (`route`)**

Routes input to different paths based on conditions.

```tcl
# Conditional routing
route {
  condition_1 ~> path_a
  condition_2 ~> path_b
  default     ~> path_c
}
```

**Semantics:**
- Exactly one path is taken
- Type of all paths must be compatible
- Confidence comes from chosen path

**Example:**
```tcl
flow transaction_router {
  compose {
    route {
      amount < 1000      ~> basic_validation
      amount < 10000     ~> enhanced_validation
      risk_score > 0.8   ~> manual_review
      default            ~> standard_validation
    }
  }
}
```

### 4. **Merge (`<>`)**

Merges multiple streams into one.

```tcl
# Merge parallel results
stream_a <> stream_b <> stream_c
```

**Semantics:**
- Types: All inputs must have compatible types
- Confidence: Average (configurable)
- Zone: Maximum zone

**Example:**
```tcl
flow multi_source_validation {
  compose {
    (source_a, source_b, source_c)
      <> merge_results
      |> output
  }
}
```

### 5. **Feedback (`loop`)**

Creates feedback loops (advanced).

```tcl
# Recursive composition
loop {
  initial: init_value
  condition: continue_while
  body: process_step
}
```

**Semantics:**
- Executes `body` repeatedly until `condition` is false
- Confidence degrades with each iteration
- Zone can only get worse

**Example:**
```tcl
flow iterative_refinement {
  compose {
    loop {
      initial: raw_data
      condition: confidence < 0.95
      body: refine_estimate
    }
  }
}
```

---

## Type System

### Basic Types

```tcl
# Primitive types
String
Number
Boolean
Array<T>
Object { prop1: Type1, prop2: Type2 }

# Special types
Confidence      # 0.0 to 1.0
Zone           # GREEN | YELLOW | RED
Pheromone      # Trail | Task | Danger | Resource
```

### Type Annotations

```tcl
# On flows
flow my_flow {
  input: Transaction
  output: Decision
}

# On tiles (when defining)
tile validator {
  input: { data: String, confidence: Number }
  output: { valid: Boolean, confidence: Number }
}
```

### Type Inference

TCL infers types automatically:

```tcl
# Types inferred from tile definitions
flow auto_typed {
  # If parse: String -> Transaction
  # And validate: Transaction -> ValidatedTransaction
  # Then this flow has type: String -> ValidatedTransaction
  parse |> validate
}
```

### Type Constraints

```tcl
# Require specific types
flow constrained {
  require input is Transaction
  require output is Decision
  require confidence >= 0.85

  compose { ... }
}
```

### Generic Types

```tcl
# Generic tile definition
tile mapper<T, U> {
  input: T
  output: U
  fn: (T) -> U
}

# Usage
flow specific {
  mapper<Transaction, Decision> with my_mapper_fn
}
```

---

## Confidence Constraints

### Confidence Zones

```tcl
# Define zone thresholds
zone thresholds {
  green: 0.90    # Auto-proceed
  yellow: 0.75   # Review required
  red: 0.00      # Stop
}
```

### Confidence Requirements

```tcl
# Require minimum confidence
flow high_confidence {
  require confidence >= 0.90

  compose {
    validate |> transform
  }
}

# Zone-based requirements
flow zone_required {
  require zone is GREEN

  compose { ... }
}
```

### Confidence Propagation

```tcl
# Sequential: multiplies
a(0.9) |> b(0.8) |> c(0.7)  # Result: 0.504

# Parallel: weighted average
(a: 0.9 @ 0.5, b: 0.6 @ 0.3, c: 0.3 @ 0.2)  # Result: 0.69

# Conditional: chosen path
route {
  cond ~> a(0.9)  # If chosen: 0.9
  default ~> b(0.5)  # If chosen: 0.5
}
```

### Confidence Tracking

```tcl
# Track confidence through flow
flow tracked {
  input: Transaction
  output: Decision
  track confidence: detailed

  compose {
    step1(confidence: "initial_check")
      |> step2(confidence: "validation")
      |> step3(confidence: "final_decision")
  }
}
```

---

## Stigmergic Rules

### Pheromone Declarations

```tcl
# Declare pheromone types in flow
flow stigmergic {
  pheromone trail {
    decay: 0.1
    strength: 0.5
  }

  pheromone danger {
    decay: 0.05
    strength: 0.8
  }

  compose { ... }
}
```

### Deposit Operations

```tcl
# Deposit pheromone
tile forager {
  action {
    deposit(trail, strength: 0.8)
  }
}
```

### Sense Operations

```tcl
# Sense pheromone
tile follower {
  condition {
    sense(trail) > 0.5
  }

  action {
    follow_trail
  }
}
```

### Stigmergic Patterns

```tcl
# Foraging pattern
flow foraging {
  pheromone trail { decay: 0.1 }
  pheromone resource { decay: 0.05 }

  compose {
    explore
      |> if found_resource {
        deposit(resource, strength: 0.9)
      }
      |> deposit(trail, strength: 0.3)
  }
}

# Flocking pattern
flow flocking {
  pheromone trail { decay: 0.2 }

  compose {
    sense_nearby |> align_velocity |> deposit(trail)
  }
}

# Task allocation
flow task_allocation {
  pheromone task { decay: 0.05 }

  compose {
    sense(task) |> if strength > 0.3 { take_task }
  }
}
```

---

## Examples

### Example 1: Fraud Detection

```tcl
use tiles/fraud
use tiles/validation

flow fraud_detection {
  input: Transaction
  output: FraudDecision

  # Confidence requirements
  require confidence >= 0.85
  zone thresholds { green: 0.90, yellow: 0.75, red: 0.00 }

  # Stigmergic coordination
  pheromone trail { decay: 0.1 }
  pheromone danger { decay: 0.05 }

  compose {
    # Step 1: Parallel signal collection
    (
      ml_model: 0.5,
      rules_engine: 0.3,
      user_reputation: 0.2
    ) |> aggregate_signals

    # Step 2: Route by amount
    |> route {
      amount < 1000     ~> basic_validation
      amount < 10000    ~> enhanced_validation
      risk_score > 0.8  ~> manual_review
      default           ~> standard_validation
    }

    # Step 3: Final checks
    |> location_check
      |> velocity_check

    # Step 4: Mark dangerous transactions
    |> if zone is RED {
      deposit(danger, strength: 0.8)
    }

    ~> output
  }
}
```

### Example 2: Data Quality Pipeline

```tcl
use tiles/quality
use tiles/transform

flow data_quality_pipeline {
  input: RawData
  output: CleanedData

  require confidence >= 0.90

  pheromone checked { decay: 0.3 }

  compose {
    # Parallel quality checks
    (
      null_check: 0.3,
      range_check: 0.3,
      format_check: 0.2,
      duplicate_check: 0.2
    ) |> aggregate_quality

    # Route by quality score
    |> route {
      quality_score >= 0.95 ~> pass_through
      quality_score >= 0.80 ~> clean_data
      default              ~> quarantine
    }

    # Mark as checked
    |> deposit(checked, strength: 0.5)

    ~> output
  }
}
```

### Example 3: Swarm Search

```tcl
use tiles/search
use tiles/coordination

flow swarm_search {
  input: SearchQuery
  output: SearchResult

  pheromone trail { decay: 0.2 }
  pheromone resource { decay: 0.05 }

  compose {
    # Multiple search agents
    (
      agent_1,
      agent_2,
      agent_3,
      agent_4
    ) |> parallel_search

    # Avoid already-searched areas
    |> avoid_pheromone(trail)

    # Mark findings
    |> if found_match {
      deposit(resource, strength: 0.9)
    }

    # Leave trail
    |> deposit(trail, strength: 0.3)

    ~> aggregate_results
  }
}
```

### Example 4: Counterfactual Branching

```tcl
use tiles/branching
use tiles/simulation

flow counterfactual_analysis {
  input: Decision
  output: Analysis

  compose {
    # Branch into parallel simulations
    (
      branch("option_a"): 0.33,
      branch("option_b"): 0.33,
      branch("option_c"): 0.34
    ) |> simulate_outcomes

    # Compare results
    |> compare_branches

    # Select best branch
    |> select_max(outcome_score)

    ~> output
  }
}
```

---

## Formal Semantics

### Type Rules

**Sequential Composition:**
```
Γ ⊢ t1: A → B
Γ ⊢ t2: B → C
─────────────────
Γ ⊢ t1 |> t2: A → C
```

**Parallel Composition:**
```
Γ ⊢ t1: A1 → B1
Γ ⊢ t2: A2 → B2
─────────────────────────────
Γ ⊢ (t1, t2): (A1, A2) → (B1, B2)
```

**Conditional Routing:**
```
Γ ⊢ route: {condi: pi}
Γ ⊢ p1: A → B
⋮
Γ ⊢ pn: A → B
─────────────────────────────────
Γ ⊢ route {cond1 ~> p1, ...}: A → B
```

### Confidence Algebra

**Sequential:**
```
c(t1 |> t2) = c(t1) × c(t2)
```

**Parallel (weighted):**
```
c((t1: w1, ..., tn: wn)) = Σ(wi × c(ti)) / Σ(wi)
```

**Conditional:**
```
c(route {cond ~> path}) = c(path) if cond else c(default)
```

### Zone Monotonicity

**Theorem:** Zones compose monotonically (can only stay same or get worse).

```
zone(t1 |> t2) = worst_zone(zone(t1), zone(t2))
```

Where:
```
worst_zone(GREEN, GREEN) = GREEN
worst_zone(GREEN, YELLOW) = YELLOW
worst_zone(YELLOW, RED) = RED
```

---

## Comparison to Alternatives

### vs. TypeScript/JavaScript

| Aspect | TCL | TypeScript |
|--------|-----|-----------|
| Type checking | Compile-time | Runtime (mostly) |
| Confidence tracking | Automatic | Manual |
| Composition validation | Built-in | Manual |
| Parallel optimization | Automatic | Manual |
| Declarative | Yes | No |
| Learning curve | Medium | Low |

**TCL advantage:** Designed for tile composition, not general programming.

### vs. Haskell

| Aspect | TCL | Haskell |
|--------|-----|---------|
| Type system | Tile-specific | General (HKT) |
| Confidence | First-class | Library-only |
| Syntax | Simple | Complex |
| Learning curve | Medium | High |
| Optimization | Tile-aware | General |

**TCL advantage:** Focused on tiles, simpler syntax, built-in confidence.

### vs. SQL

| Aspect | TCL | SQL |
|--------|-----|-----|
| Purpose | Tile graphs | Data queries |
| Composition | First-class | Joins |
| Type safety | Strong | Weak |
| Optimization | Graph-specific | Query-specific |

**TCL advantage:** Designed for computation graphs, not data retrieval.

### vs. Apache Airflow

| Aspect | TCL | Airflow |
|--------|-----|---------|
| Paradigm | Declarative | Imperative |
| Type safety | Compile-time | Runtime |
| Confidence | Built-in | Manual |
| Real-time | Yes | Batch-oriented |

**TCL advantage:** Real-time tile composition with static verification.

---

## Implementation Roadmap

### Phase 1: Core Parser (Weeks 1-2)

**Goal:** Parse TCL syntax into AST

- [ ] Lexical analyzer (tokenizer)
- [ ] Parser (AST generation)
- [ ] Basic syntax validation
- [ ] Error reporting

**Deliverables:**
- `tcl-parser` package
- CLI tool: `tcl parse <file>`

### Phase 2: Type Checker (Weeks 3-4)

**Goal:** Type-check compositions

- [ ] Type inference engine
- [ ] Type compatibility checking
- [ ] Generic type support
- [ ] Type error messages

**Deliverables:**
- `tcl-typechecker` package
- CLI tool: `tcl typecheck <file>`

### Phase 3: Confidence Engine (Weeks 5-6)

**Goal:** Compute confidence propagation

- [ ] Confidence algebra implementation
- [ ] Zone classification
- [ ] Confidence bounds calculation
- [ ] Degradation analysis

**Deliverables:**
- `tcl-confidence` package
- CLI tool: `tcl analyze <file>`

### Phase 4: Composition Validator (Weeks 7-8)

**Goal:** Detect composition paradoxes

- [ ] Paradox detection algorithm
- [ ] Constraint propagation
- [ ] Algebra law verification
- [ ] Safety analysis

**Deliverables:**
- `tcl-validator` package
- CLI tool: `tcl validate <file>`

### Phase 5: Code Generator (Weeks 9-10)

**Goal:** Generate executable TypeScript

- [ ] AST to TypeScript transpiler
- [ ] Runtime composition library
- [ ] Execution optimization
- [ ] Error handling

**Deliverables:**
- `tcl-codegen` package
- CLI tool: `tcl build <file>`

### Phase 6: Stigmergy Runtime (Weeks 11-12)

**Goal:** Execute stigmergic rules

- [ ] Pheromone field implementation
- [ ] Deposit/sense operations
- [ ] Decay scheduling
- [ ] Pattern implementations

**Deliverables:**
- `tcl-stigmergy` package
- Runtime integration

### Phase 7: IDE Integration (Weeks 13-14)

**Goal:** Developer experience

- [ ] VS Code extension
- [ ] Syntax highlighting
- [ ] Intellisense/autocomplete
- [ ] Real-time validation
- [ ] Debugging support

**Deliverables:**
- `tcl-vscode` extension
- Language server

### Phase 8: Optimization Engine (Weeks 15-16)

**Goal:** Automatic optimization

- [ ] Parallel execution analysis
- [ ] Memoization opportunities
- [ ] Dead code elimination
- [ ] Tile fusion

**Deliverables:**
- `tcl-optimizer` package
- Optimization passes

---

## Usage Examples

### Command Line

```bash
# Parse and validate
tcl validate my_flow.tcl

# Type check
tcl typecheck my_flow.tcl

# Analyze confidence
tcl analyze --confidence my_flow.tcl

# Generate TypeScript
tcl build my_flow.tcl --output ./dist

# Run with REPL
tcl repl my_flow.tcl
```

### TypeScript Integration

```typescript
import { compileFlow } from '@polln/tcl';

// Compile TCL to executable function
const fraudDetection = compileFlow(`
  flow fraud_detection {
    input: Transaction
    output: Decision

    compose {
      ml_model |> validate |> decide
    }
  }
`);

// Use in code
const result = await fraudDetection(transaction);

// Check confidence
console.log(result.confidence); // 0.92
console.log(result.zone); // 'GREEN'
```

### VS Code Extension

```
# Real-time validation
tcl-vscode:
  - Syntax highlighting
  - Type tooltips
  - Confidence annotations
  - Paradox detection highlights
  - Flow visualization
```

---

## Future Directions

### 1. **Visual Editor**

Graph-based TCL editor:
- Drag-and-drop tiles
- Real-time validation
- Confidence flow visualization
- Export to TCL code

### 2. **Auto-Tile Discovery**

AI-powered tile decomposition:
- Analyze monolithic model
- Discover tile boundaries
- Generate TCL automatically
- Optimize composition

### 3. **Distributed Execution**

Run tiles across machines:
- Automatic partitioning
- Distributed pheromone fields
- Fault tolerance
- Load balancing

### 4. **Tile Marketplace**

Share and sell tiles:
- Package tiles as TCL modules
- Type-safe tile imports
- Confidence guarantees
- Version management

### 5. **Formal Verification**

Prove tile properties:
- Pre/post conditions
- Invariant checking
- Termination proofs
- Resource bounds

---

## Conclusion

TCL transforms tile composition from manual wiring to declarative specification. By combining:

- **Type safety** (catch errors at compile time)
- **Confidence tracking** (propagate automatically)
- **Composition validation** (detect paradoxes)
- **Stigmergy native** (built-in coordination)
- **Declarative syntax** (human-readable)

TCL enables developers to build complex tile systems with confidence.

**The future of AI is glass boxes, not black boxes. TCL is the language for opening those boxes.**

---

*Design Complete | TCL v1.0*
*POLLN Research | 2026-03-10*
