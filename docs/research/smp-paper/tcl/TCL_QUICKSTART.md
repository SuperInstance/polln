# TCL Quick Reference

**Version:** 1.0
**Status:** Quick Reference Guide

---

## Syntax at a Glance

### Composition Operators

| Operator | Name | Example | Description |
|----------|------|---------|-------------|
| `|>` | Sequential | `a \|> b` | Pipe output of a to input of b |
| `()` | Parallel | `(a, b)` | Execute a and b in parallel |
| `@` | Weight | `(a: 0.7, b: 0.3)` | Assign weights to parallel |
| `~>` | Route | `cond ~> path` | Route to path if condition true |
| `<>` | Merge | `a <> b` | Merge streams |

### Keywords

```
flow       - Define a flow
tile       - Define a tile
use        - Import module
compose    - Composition block
input      - Input type
output     - Output type
require    - Constraint
zone       - Zone thresholds
pheromone  - Pheromone declaration
route      - Conditional routing
loop       - Loop construct
```

---

## Basic Patterns

### Sequential Pipeline

```tcl
flow pipeline {
  input: A
  output: D

  compose {
    step1 |> step2 |> step3
  }
}
```

### Parallel Execution

```tcl
flow parallel {
  input: A
  output: (B, C)

  compose {
    (left_branch, right_branch)
  }
}
```

### Weighted Parallel

```tcl
flow weighted {
  compose {
    (primary: 0.7, fallback: 0.3)
  }
}
```

### Conditional Routing

```tcl
flow routing {
  input: Data
  output: Result

  compose {
    route {
      score > 0.9  ~> fast_path
      score > 0.7  ~> medium_path
      default      ~> slow_path
    }
  }
}
```

---

## Type Annotations

### Basic Types

```tcl
input: String
input: Number
input: Boolean
```

### Complex Types

```tcl
input: Array<Number>
input: Object {name: String, age: Number}
input: (String, Number)  # Tuple
```

### Generic Types

```tcl
tile mapper<T, U> {
  input: T
  output: U
}
```

---

## Confidence

### Confidence Requirements

```tcl
require confidence >= 0.90
require confidence > 0.85
```

### Zone Thresholds

```tcl
zone thresholds {
  green: 0.90
  yellow: 0.75
  red: 0.00
}
```

### Zone Requirements

```tcl
require zone is GREEN
require zone != RED
```

---

## Stigmergy

### Pheromone Declaration

```tcl
pheromone trail {
  decay: 0.1
  strength: 0.5
}
```

### Deposit

```tcl
deposit(trail, strength: 0.8)
```

### Sense

```tcl
sense(trail) > 0.5
```

---

## Control Flow

### If Expression

```tcl
if condition {
  true_branch
} else {
  false_branch
}
```

### Loop

```tcl
loop {
  initial: start_value
  condition: continue_while
  body: process_step
}
```

### Let Binding

```tcl
let x = computation in
  use_x(x)
```

---

## Imports

### Basic Import

```tcl
use tiles/validation
```

### Aliased Import

```tcl
use tiles/validation as val
```

---

## Examples Gallery

### Fraud Detection

```tcl
flow fraud_detection {
  input: Transaction
  output: Decision

  require confidence >= 0.85

  pheromone danger { decay: 0.05 }

  compose {
    (ml_model: 0.5, rules: 0.3, reputation: 0.2)
      |> route {
        amount < 1000  ~> basic
        amount < 10000 ~> enhanced
        default        ~> manual
      }
      |> if zone is RED {
        deposit(danger, strength: 0.8)
      }
  }
}
```

### Data Quality

```tcl
flow data_quality {
  input: RawData
  output: CleanData

  compose {
    (null_check: 0.3, range_check: 0.3, format_check: 0.4)
      |> aggregate
      |> route {
        quality >= 0.95 ~> pass
        default          ~> clean
      }
  }
}
```

### Swarm Search

```tcl
flow swarm_search {
  pheromone trail { decay: 0.2 }
  pheromone resource { decay: 0.05 }

  compose {
    (agent1, agent2, agent3)
      |> avoid_pheromone(trail)
      |> if found {
        deposit(resource, strength: 0.9)
      }
      |> deposit(trail, strength: 0.3)
  }
}
```

---

## Command Line

```bash
# Validate syntax
tcl validate file.tcl

# Type check
tcl typecheck file.tcl

# Analyze confidence
tcl analyze file.tcl

# Generate code
tcl build file.tcl -o output.ts

# Run REPL
tcl repl

# Format code
tcl format file.tcl
```

---

## Type System Cheat Sheet

### Type Compatibility

```
String  <: String           # Compatible
Number  <: Number           # Compatible
String  =/=: Number         # Incompatible
Array<T> <: Array<U>        # If T <: U
```

### Variance

```
# Covariant (output)
Tile<Animal> can be used where Tile<Cat> expected

# Contravariant (input)
Tile<Cat> can be used where Tile<Animal> expected

# Invariant (input/output)
Tile<T> requires exact type match
```

---

## Confidence Algebra

### Sequential

```
c(a |> b) = c(a) × c(b)

Example:
  c(a) = 0.9
  c(b) = 0.8
  c(a |> b) = 0.72
```

### Parallel (Weighted)

```
c((a:w1, b:w2)) = (w1×c(a) + w2×c(b)) / (w1+w2)

Example:
  c(a) = 0.9, w1 = 0.5
  c(b) = 0.6, w2 = 0.5
  c(parallel) = 0.75
```

### Zone

```
zone(c) = GREEN    if c >= 0.90
zone(c) = YELLOW   if c >= 0.75
zone(c) = RED      otherwise
```

---

## Error Messages

### Type Mismatch

```
ERROR: Type mismatch
  └─ Expected: Number
  └─ Got: String
  └─ At: line 10, col 5
```

### Confidence Too Low

```
WARNING: Confidence below threshold
  └─ Required: 0.90
  └─ Got: 0.72
  └─ Zone: RED
```

### Paradox Detected

```
ERROR: Composition paradox detected
  └─ Contradictory constraints on variable "amount"
  └─ Tile A requires: amount < 10000
  └─ Tile B requires: amount > 15000
```

---

## Best Practices

### 1. Name Flows Clearly

```tcl
# Good
flow fraud_detection { ... }

# Bad
flow process { ... }
```

### 2. Annotate Types

```tcl
# Good
flow validate {
  input: {data: String, confidence: Number}
  output: {valid: Boolean}
  ...
}

# Bad
flow validate { ... }
```

### 3. Use Weights Explicitly

```tcl
# Good
(ml: 0.5, rules: 0.3, reputation: 0.2)

# Bad (ambiguous)
(ml, rules, reputation)
```

### 4. Require Minimum Confidence

```tcl
# Good
require confidence >= 0.90

# Bad (no safety net)
# No requirement
```

### 5. Declare Pheromones

```tcl
# Good
pheromone trail { decay: 0.1 }

# Bad
# No declaration, implicit defaults
```

---

## Common Patterns

### Fallback Pattern

```tcl
flow fallback {
  compose {
    (primary: 0.8, fallback: 0.2)
      |> if confidence < 0.7 {
        use_fallback
      }
  }
}
```

### Validation Pipeline

```tcl
flow validate {
  compose {
    check_format
      |> check_range
      |> check_consistency
      |> if confidence >= 0.90 {
        approve
      } else {
        reject
      }
  }
}
```

### Parallel Merge

```tcl
flow parallel_merge {
  compose {
    (source_a, source_b, source_c)
      <> normalize
      <> aggregate
      |> output
  }
}
```

---

## Debugging

### Trace Confidence

```tcl
flow traced {
  track confidence: detailed

  compose {
    step1(confidence: "initial")
      |> step2(confidence: "after_validation")
      |> step3(confidence: "final")
  }
}
```

### Inspect Types

```bash
tcl typecheck --explain file.tcl
```

### Visualize Graph

```bash
tcl visualize file.tcl -o graph.png
```

---

*Quick Reference Complete | TCL v1.0*
*POLLN Research | 2026-03-10*
