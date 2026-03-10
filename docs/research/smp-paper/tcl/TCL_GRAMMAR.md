# TCL Grammar and Formal Specification

**Status:** Formal Grammar v1.0
**Date:** 2026-03-10

---

## Lexical Grammar

### Keywords

```
flow       tile       use        compose
input      output     require    zone
pheromone  deposit    sense      route
loop       if         else       match
case        let        in         and
or          not        true       false
```

### Operators

```
|>          # Sequential composition (pipe)
<>          # Merge
()          # Parallel composition
~>          # Route mapping
@           # Weight specification
:           # Type annotation
=           # Assignment
,           # Separator
;           # Terminator (optional)
```

### Literals

```
NUMBER      [0-9]+(\.[0-9]+)?
STRING      "[^"]*"
IDENTIFIER  [a-zA-Z_][a-zA-Z0-9_]*
```

### Comments

```
LINE_COMMENT    #.*\n
BLOCK_COMMENT   #=([^=#]|#[^=]|=#[^#])*=#\n
```

---

## Syntactic Grammar

### Program

```
program ::= (use_decl | flow_decl | tile_decl)*
```

### Use Declaration

```
use_decl ::= 'use' STRING ('as' IDENTIFIER)?
```

### Flow Declaration

```
flow_decl ::= 'flow' IDENTIFIER '{'
    (input_decl)?
    (output_decl)?
    (require_decl)*
    (zone_decl)?
    (pheromone_decl)*
    compose_block
'}'
```

### Tile Declaration

```
tile_decl ::= 'tile' IDENTIFIER ('<' type_params '>')? '{'
    (input_decl)?
    (output_decl)?
    (tile_body)
'}'
```

### Type Declarations

```
input_decl ::= 'input' ':' type
output_decl ::= 'output' ':' type

type ::= base_type
       | 'Array' '<' type '>'
       | 'Object' '{' (prop_decl (',' prop_decl)*)? '}'
       | '(' type (',' type)* ')'
       | IDENTIFIER

base_type ::= 'String' | 'Number' | 'Boolean' | 'Confidence' | 'Zone'

prop_decl ::= IDENTIFIER ':' type
```

### Constraints

```
require_decl ::= 'require' constraint

constraint ::= confidence_constraint
            | zone_constraint
            | type_constraint

confidence_constraint ::= 'confidence' cmp_op NUMBER
zone_constraint ::= 'zone' 'is' zone_lit
type_constraint ::= IDENTIFIER 'is' type

cmp_op ::= '>=' | '<=' | '>' | '<' | '==' | '!='

zone_lit ::= 'GREEN' | 'YELLOW' | 'RED'
```

### Zone Declaration

```
zone_decl ::= 'zone' 'thresholds' '{'
    'green' ':' NUMBER
    'yellow' ':' NUMBER
    'red' ':' NUMBER
'}'
```

### Pheromone Declaration

```
pheromone_decl ::= 'pheromone' IDENTIFIER '{'
    ('decay' ':' NUMBER)?
    ('strength' ':' NUMBER)?
    ('type' ':' pheromone_type)?
'}'

pheromone_type ::= 'TRAIL' | 'TASK' | 'DANGER' | 'RESOURCE'
```

### Compose Block

```
compose_block ::= 'compose' '{' pipeline '}'
```

### Pipeline

```
pipeline ::= expr (('|>' | '<>') expr)*
```

### Expression

```
expr ::= IDENTIFIER                                  # Tile reference
       | '(' expr (',' expr)* ')'                    # Parallel
       | '(' expr ('@' NUMBER)? (',' expr ('@' NUMBER)?)? ')'  # Weighted parallel
       | 'route' '{' route_branch+ '}'               # Route
       | 'loop' '{' loop_body '}'                   # Loop
       | 'if' expr '{' pipeline '}' ('else' '{' pipeline '}')?  # Conditional
       | 'let' IDENTIFIER '=' expr 'in' expr        # Let binding
       | expr '(' arg_list? ')'                      # Application
       | '(' pipeline ')'                            # Grouping
```

### Route Branch

```
route_branch ::= condition '~>' pipeline
```

### Condition

```
condition ::= expr cmp_op expr             # Comparison
            | expr 'and' expr             # Logical AND
            | expr 'or' expr              # Logical OR
            | 'not' expr                  # Logical NOT
            | '(' condition ')'           # Grouping
```

### Loop Body

```
loop_body ::= 'initial' ':' expr
             'condition' ':' condition
             'body' ':' pipeline
```

### Argument List

```
arg_list ::= expr (',' expr)*
```

---

## Type System

### Type Environment

```
Γ ::= ∅ | Γ, x:τ
```

### Type Judgment

```
Γ ⊢ e:τ
```

Program e has type τ under environment Γ.

### Typing Rules

**Variable:**
```
Γ(x) = τ
─────────
Γ ⊢ x:τ
```

**Sequential Composition:**
```
Γ ⊢ e1:τ1      Γ ⊢ e2:τ2      τ1 = τ2.in
─────────────────────────────────────
Γ ⊢ e1 |> e2:τ2.out
```

**Parallel Composition:**
```
Γ ⊢ e1:τ1      Γ ⊢ e2:τ2
───────────────────────────────────────────────────────
Γ ⊢ (e1, e2):(τ1.in, τ2.in) → (τ1.out, τ2.out)
```

**Route:**
```
Γ ⊢ route:{ci→pi}      ∀i. Γ ⊢ pi:τ
───────────────────────────────────────────────
Γ ⊢ route {c1→p1, ...}:input → τ
```

**Loop:**
```
Γ ⊢ init:τ      Γ ⊢ body:τ→τ      Γ ⊢ cond:τ→Boolean
───────────────────────────────────────────────────
Γ ⊢ loop {init, cond, body}:τ
```

### Type Unification

```
unify(τ1, τ2) = subst    if τ1 = τ2
unify(Array(τ1), Array(τ2)) = unify(τ1, τ2)
unify(Object(f1), Object(f2)) = unify_fields(f1, f2)
unify(_, _) = ERROR       otherwise
```

---

## Operational Semantics

### Values

```
v ::= n                # Number
      | s              # String
      | b              # Boolean
      | [v1, ..., vn]  # Array
      | {f1: v1, ...}  # Object
      | ⊥              # Error
```

### Configuration

```
C ::= e, ρ, σ
```

Expression e with environment ρ and store σ.

### Reduction Rules

**Sequential:**
```
C1 ⟶ C1'      C2 ⟶ C2'
─────────────────────────
C1 |> C2 ⟶ C1' |> C2'
```

**Parallel:**
```
C1 ⟶ C1'      C2 ⟶ C2'
─────────────────────────
(C1, C2) ⟶ (C1', C2')
```

**Route:**
```
cond evaluates to true
─────────────────────────
route {cond→path, ...} ⟶ path
```

---

## Confidence Algebra

### Confidence Values

```
c ::= [0, 1]    # Real number between 0 and 1
```

### Confidence Operations

**Sequential Multiplication:**
```
c(e1 |> e2) = c(e1) × c(e2)
```

**Parallel Average (weighted):**
```
c((e1:w1, ..., en:wn)) = Σ(wi × c(ei)) / Σ(wi)
```

**Conditional Selection:**
```
c(route {cond→path, default→d}) =
    c(path) if cond else c(d)
```

### Zone Classification

```
zone(c) = GREEN    if c ≥ 0.90
zone(c) = YELLOW   if c ≥ 0.75
zone(c) = RED      otherwise
```

### Zone Composition

```
zone(e1 |> e2) = worst(zone(e1), zone(e2))

worst(GREEN, GREEN) = GREEN
worst(GREEN, YELLOW) = YELLOW
worst(YELLOW, RED) = RED
worst(_, _) = max(zone1, zone2)
```

---

## Stigmergic Semantics

### Pheromone Field

```
Φ ::= Map(CellCoord, List(Pheromone))
```

### Pheromone Value

```
p ::= {
    type: PheromoneType,
    strength: [0, 1],
    decay_rate: [0, 1],
    source: TileID,
    timestamp: Number
}
```

### Deposit Operation

```
Φ' = Φ with Φ[cell] = Φ[cell] ++ [p]

where:
    p.strength = min(strength, max_strength)
    p.timestamp = now()
```

### Sense Operation

```
sense(Φ, cell, type?) = {
    p ∈ Φ[cell] | (type? = null or p.type = type?)
}
```

### Evaporation

```
evaporate(Φ, Δt):
    for each p in Φ:
        p.strength *= (1 - p.decay_rate)^Δt
        remove p if p.strength < min_strength
```

### Stigmergic Patterns

**Foraging:**
```
decide_next(field, current, neighbors):
    candidates = []
    for n in neighbors:
        resource = sense(field, n, RESOURCE)
        danger = sense(field, n, DANGER)
        score = sum(resource.strength) - 2*sum(danger.strength)
        candidates.add((n, score))
    return argmax(candidates)
```

**Flocking:**
```
update_velocity(field, tile, neighbors):
    separation = average(tile.pos - n.pos for n in neighbors)
    alignment = average(n.velocity for n in neighbors)
    cohesion = average(n.pos for n in neighbors) - tile.pos
    return w1*separation + w2*alignment + w3*cohesion
```

---

## Examples

### Example 1: Simple Pipeline

```tcl
flow simple {
  input: Number
  output: Number

  compose {
    increment |> double |> square
  }
}
```

**Type Derivation:**
```
increment: Number -> Number
double: Number -> Number
square: Number -> Number

increment |> double: Number -> Number
(increment |> double) |> square: Number -> Number
```

### Example 2: Parallel with Weights

```tcl
flow weighted {
  input: Number
  output: Number

  compose {
    (fast: 0.3, accurate: 0.7)
      |> merge
  }
}
```

**Confidence Calculation:**
```
c(fast) = 0.6
c(accurate) = 0.95

c(parallel) = 0.3*0.6 + 0.7*0.95 = 0.845
zone = YELLOW
```

### Example 3: Route

```tcl
flow routing {
  input: {value: Number}
  output: Number

  compose {
    route {
      value < 0   ~> negate
      value > 0   ~> identity
      default     ~> zero
    }
  }
}
```

**Semantics:**
```
If value < 0: execute negate
If value > 0: execute identity
Else: execute zero
```

---

## Implementation Notes

### Parser Strategy

1. **Recursive Descent:** Simple, readable, maintainable
2. **Error Recovery:** Continue parsing after errors
3. **Source Locations:** Track line/column for errors

### Type Checker Strategy

1. **Constraint Generation:** Generate type constraints
2. **Unification:** Solve constraints using unification
3. **Error Reporting:** Explain type mismatches clearly

### Code Generation Strategy

1. **AST → TypeScript:** Direct translation
2. **Runtime Library:** Minimal runtime for execution
3. **Optimization:** Inline small tiles, fuse operations

---

## Testing Strategy

### Unit Tests

- Parser: Valid and invalid syntax
- Type checker: Type errors and inference
- Confidence: Calculation accuracy
- Stigmergy: Field operations

### Integration Tests

- Full flows compilation
- Generated code execution
- Confidence propagation
- Pheromone coordination

### Property Tests

- Type soundness
- Confidence bounds
- Algebraic laws
- Round-trip (parse → unparse)

---

*Grammar Specification Complete | TCL v1.0*
*POLLN Research | 2026-03-10*
