# Quantum Tiles: Quick Start Guide

**For:** Developers wanting to implement quantum tiles
**Prerequisites:** Familiarity with SMP tiles, basic quantum computing concepts
**Date:** 2026-03-10

---

## 30-Second Summary

SMP tiles can call quantum computers for specific problems (optimization, search, simulation). The tile interface remains classical; only the implementation changes. Always include a classical fallback.

```typescript
// Classical tile
const classical = {run: (input) => classicalAlgorithm(input)}

// Quantum tile (same interface!)
const quantum = {
    run: (input) => quantumAlgorithm(input),
    fallback: classical  // Use classical if quantum unavailable
}
```

---

## When to Use Quantum Tiles

### Green Light (Use Quantum)
- **Quantum-native problems:** Molecular simulation, materials science
- **Optimization:** Combinatorial problems (MaxCut, TSP, portfolio)
- **Search:** Unstructured search (future: fault-tolerant QC)

### Yellow Light (Evaluate Case-by-Case)
- **Machine learning:** Quantum kernels, quantum neural networks (unproven)
- **Linear algebra:** HHL algorithm (needs deep circuits)
- **Sampling:** Monte Carlo, probabilistic algorithms

### Red Light (Use Classical)
- **Small problems:** < 2^20 search space (classical is faster)
- **Simple operations:** Sorting, basic arithmetic (no quantum advantage)
- **No quantum hardware:** If backend unavailable (use fallback)

---

## Quantum Tile Checklist

Before implementing a quantum tile, verify:

- [ ] **Problem fits:** Is there a quantum algorithm for this problem?
- [ ] **Size appropriate:** Is problem large enough for quantum advantage (> 2^20)?
- [ ] **NISQ-compatible:** Can algorithm run on noisy hardware (depth < 1000 gates)?
- [ ] **Classical baseline:** Do we have a working classical implementation for fallback?
- [ ] **Confidence metric:** Can we measure quantum result confidence?
- [ ] **Error mitigation:** What error mitigation strategy will we use?
- [ ] **Testing plan:** How will we validate against classical baseline?

---

## Anatomy of a Quantum Tile

```typescript
interface QuantumTile<I, O> {
    // Classical tile interface (required)
    name: string
    discriminate: (input: I) => O
    confidence: (input: I) => number
    trace: (input: I) => string

    // Quantum-specific (required for quantum tiles)
    quantumBackend: {
        provider: 'ibm' | 'google' | 'amazon' | 'azure' | 'simulated'
        device: string
        shots: number
        mitigation: 'zne' | 'pec' | 'symmetry' | 'none'
    }

    quantumSubroutine: {
        circuit: (input: I) => QuantumCircuit
        encoding: (input: I) => QuantumState
        decoding: (measurements: Bitstring[]) => O
    }

    // Hybrid pattern (required)
    hybridPattern: 'variational' | 'divide-and-conquer' | 'quantum-preprocessing'

    // Fallback (required)
    fallback: Tile<I, O>  # Classical tile to use if quantum unavailable
}
```

---

## Three Quantum Tile Patterns

### Pattern 1: Variational (VQE, QAOA)

**Use for:** Optimization, quantum simulation

```typescript
function variationalTile(input: Problem): Solution {
    let theta = initialize()

    while (!converged) {
        // Quantum: Evaluate cost function
        const energy = runQuantumCircuit(input, theta)

        // Classical: Update parameters
        theta = optimizer.update(theta)
    }

    return decodeSolution(theta)
}
```

**Examples:** `maxcut_qaoa`, `molecular_vqe`, `portfolio_qaoa`

---

### Pattern 2: Divide-and-Conquer

**Use for:** Large problems that decompose

```typescript
function divideAndConquerTile(input: LargeProblem): Solution {
    // Classical: Decompose
    const subproblems = decompose(input)

    // Quantum/Classical: Solve subproblems
    const solutions = subproblems.map(sp => {
        if (sp.size <= quantumBackend.maxQubits) {
            return quantumSolve(sp)
        } else {
            return classicalSolve(sp)
        }
    })

    // Classical: Combine
    return combine(solutions)
}
```

**Examples:** `large_scale_optimization`, `distributed_molecular_sim`

---

### Pattern 3: Quantum Pre-processing

**Use for:** Feature enhancement, kernel estimation

```typescript
function quantumPreprocessTile(input: Data): EnhancedData {
    // Quantum: Compute features
    const quantumFeatures = runQuantumCircuit(input)

    // Classical: Use quantum features
    return classicalAlgorithm(input, quantumFeatures)
}
```

**Examples:** `quantum_kernel_svm`, `quantum_feature_map`

---

## Confidence Metrics for Quantum Tiles

### 1. Measurement Concentration
Are measurements clustered around one outcome?

```typescript
function measurementConfidence(measurements): number {
    const counts = histogram(measurements)
    const maxCount = Math.max(...Object.values(counts))
    return maxCount / measurements.length
}
```

- **1.0** = Perfect concentration (all measurements identical)
- **0.5** = Random (uniform distribution)
- **< 0.3** = Too noisy (use fallback)

---

### 2. Error Mitigation Residual
How much did error mitigation help?

```typescript
function errorMitigationConfidence(raw, mitigated): number {
    const improvement = abs(mitigated.error - raw.error)
    return min(improvement / raw.error, 1.0)
}
```

- **> 0.5** = Significant improvement (good mitigation)
- **0.1 - 0.5** = Moderate improvement
- **< 0.1** = No improvement (try different strategy)

---

### 3. Convergence (Variational)
Did the optimization converge?

```typescript
function convergenceConfidence(history): number {
    const variance = var(history.slice(-10))
    return variance < tolerance ? 0.95 : 0.60
}
```

---

### 4. Solution Quality (Optimization)
How good is the solution compared to bounds?

```typescript
function qualityConfidence(solution, upperBound): number {
    return solution / upperBound  # Ratio of optimal
}
```

- **> 0.95** = Near-optimal
- **0.85 - 0.95** = Good
- **< 0.85** = Suboptimal

---

## Development Workflow

### Phase 1: Local Development (Simulator)
```bash
# 1. Create tile
npm run generate-tile -- quantum --name maxcut_qaoa

# 2. Test with simulator
npm run test -- --tile=maxcut_qaoa --backend=simulator

# 3. Validate against classical
npm run benchmark -- --tile=maxcut_qaoa --vs=classical
```

### Phase 2: Real Hardware (Weekly)
```bash
# 1. Run on quantum hardware
npm run test -- --tile=maxcut_qaoa --backend=ibmq_manila

# 2. Compare simulator vs hardware
npm run compare -- --simulator --hardware

# 3. Update noise model if mismatch
npm run calibrate-noise -- --tile=maxcut_qaoa
```

### Phase 3: Production
```bash
# 1. Deploy with fallback
npm run deploy -- --tile=maxcut_qaoa --fallback-enabled

# 2. Monitor quantum vs classical usage
npm run monitor -- --tile=maxcut_qaoa --metrics=usage,confidence

# 3. Auto-fallback if quantum degrades
# (configured in tile settings)
```

---

## Quick Example: MaxCut QAOA Tile

```typescript
// In 5 minutes
import { QAOA, IBMQBackend } from '@smp/quantum'

const tile = {
    name: 'maxcut_qaoa',

    // Problem: Graph MaxCut
    encode: (graph) => {
        // Build QUBO from graph edges
        const Q = buildMaxCutQUBO(graph)
        return Q
    },

    // QAOA circuit
    circuit: (Q, depth) => {
        return QAOA.circuit(Q, {
            depth: depth,
            optimizer: 'COBYLA'
        })
    },

    // Decode measurement to cut
    decode: (measurements) => {
        const best = mode(measurements)
        const value = evaluateCut(best)
        return {
            cut: best,
            value: value,
            confidence: frequency(best, measurements)
        }
    },

    // Classical fallback
    fallback: (graph) => {
        return classicalMaxCut(graph)  # Goemans-Williamson
    },

    // Configuration
    config: {
        backend: 'ibmq_manila',
        shots: 1000,
        depth: 3,
        mitigation: 'zne'
    }
}

export default tile
```

---

## Common Pitfalls

### Pitfall 1: No Classical Fallback
```typescript
// BAD: No fallback
const tile = {run: quantumAlgorithm}

// GOOD: With fallback
const tile = {
    run: quantumAlgorithm,
    fallback: classicalAlgorithm
}
```

### Pitfall 2: Not Checking Confidence
```typescript
// BAD: Always use quantum result
const result = await quantumTile.run(input)

// GOOD: Check confidence first
const result = await quantumTile.run(input)
if (result.confidence < 0.75) {
    return await quantumTile.fallback.run(input)
}
```

### Pitfall 3: Deep Circuits on NISQ
```typescript
// BAD: Grover with 2^20 iterations (impossible on NISQ)
const circuit = grover(data, iterations=2^20)

// GOOD: QAOA with depth 3 (NISQ-friendly)
const circuit = qaoa(data, depth=3)
```

### Pitfall 4: No Error Mitigation
```typescript
// BAD: Raw measurements
const result = backend.run(circuit)

// GOOD: With error mitigation
const result = backend.run(circuit, {mitigation: 'zne'})
```

---

## Quantum Tile Catalog

| Tile Name | Problem | Algorithm | NISQ Ready | Status |
|-----------|---------|-----------|------------|--------|
| `maxcut_qaoa` | Graph MaxCut | QAOA | Yes | PoC |
| `molecular_vqe` | Molecular ground state | VQE | Yes | PoC |
| `portfolio_qaoa` | Portfolio optimization | QAOA | Yes | Proposed |
| `search_grover` | Unstructured search | Grover | No (future) | Research |
| `quantum_kernel` | SVM kernel | Quantum feature map | Yes | Proposed |
| `linear_hhl` | Linear systems | HHL | No (future) | Research |

---

## Resources

### Documentation
- [Main Research Document](./QUANTUM_TILES_RESEARCH.md) - Full research
- [Examples](./QUANTUM_TILES_EXAMPLES.md) - Concrete implementations
- [Tile Algebra](../formal/TILE_ALGEBRA_FORMAL.md) - Formal foundations

### Tools
- `@smp/quantum` - Quantum tile SDK
- `@smp/simulator` - Quantum simulator integration
- `@smp/testing` - Quantum tile testing framework

### Quantum Backends
- IBM Quantum: `ibmq_manila`, `ibmq_guadalupe`
- Google Cirq: `google_sycamore`
- Amazon Braket: `ionq_harmony`, `rigetti_aspen`

---

## Getting Help

1. **Start simple:** Begin with variational algorithms (VQE, QAOA)
2. **Use simulators:** Develop locally before using real hardware
3. **Validate:** Always compare against classical baseline
4. **Ask questions:** Join the SMP Discord `#quantum` channel

---

*Quick Start Guide | Quantum Tiles v1.0 | Last Updated: 2026-03-10*
