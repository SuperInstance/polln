# Quantum Tiles: Concrete Examples

**Companion to:** QUANTUM_TILES_RESEARCH.md
**Date:** 2026-03-10
**Status:** Working Examples

---

## Example 1: QAOA MaxCut Tile

### Problem Definition

Given a graph G = (V, E), partition vertices into two sets to maximize the number of edges crossing the partition.

### Classical Baseline

```typescript
// Classical MaxCut using Goemans-Williamson (approximation ratio ~0.878)
function classicalMaxCut(graph: Graph): Cut {
    const sdpmatrix = solveSDP(graph)  // Semidefinite programming
    const cut = hyperplaneRounding(sdpmatrix)
    return {
        partition: cut,
        value: countCrossingEdges(graph, cut),
        confidence: 0.88  // Approximation ratio
    }
}
```

### Quantum Tile Implementation

```typescript
import { QuantumCircuit, QAOA, IBMQBackend } from '@smp/quantum'

interface MaxCutTile extends QuantumTile<Graph, Cut> {
    name: "maxcut_qaoa"

    // Tile configuration
    config: {
        qaoaDepth: 3  // p = 3 QAOA layers
        shots: 1000
        backend: "ibmq_manila"
        mitigation: "zero_noise_extrapolation"
    }

    // Problem encoding: QUBO formulation
    encode: (graph: Graph) => QUBO => {
        const n = graph.vertices.length
        const Q = zeros(n, n)

        // MaxCut QUBO: maximize sum of x_i * (1-x_j) for edges (i,j)
        for (const [i, j] of graph.edges) {
            Q[i][i] += 1
            Q[j][j] += 1
            Q[i][j] -= 2
            Q[j][i] -= 2
        }

        return {Q, offset: 0}
    }

    // QAOA circuit
    circuit: (qubo: QUBO, depth: number) => QuantumCircuit => {
        const n = qubo.Q.length
        const circuit = new QuantumCircuit(n)

        // Initial state: Hadamard on all qubits (superposition)
        circuit.h(all)

        // QAOA layers
        for (let p = 0; p < depth; p++) {
            // Problem unitary: exp(-i * gamma_p * H_C)
            const gamma = parameters.gamma[p]
            for (let i = 0; i < n; i++) {
                for (let j = i; j < n; j++) {
                    if (qubo.Q[i][j] !== 0) {
                        circuit.rzz(2 * gamma * qubo.Q[i][j], i, j)
                    }
                }
            }

            // Mixer unitary: exp(-i * beta_p * H_B)
            const beta = parameters.beta[p]
            circuit.rx(2 * beta, all)
        }

        // Measurement
        circuit.measure(all)

        return circuit
    }

    // Decode measurements to cut
    decode: (measurements: Bitstring[]) => Cut => {
        // Most frequent measurement
        const best = mode(measurements)

        // Partition: qubit = 0 -> set A, qubit = 1 -> set B
        const partition = {
            setA: best.filter((bit, i) => bit === 0).map((_, i) => i),
            setB: best.filter((bit, i) => bit === 1).map((_, i) => i)
        }

        const value = countCrossingEdges(graph, partition)
        const concentration = frequency(best, measurements)

        return {
            partition,
            value,
            confidence: concentration  // Higher concentration = higher confidence
        }
    }

    // Classical fallback
    fallback: classicalMaxCut

    // Hybrid metadata
    hybrid: {
        pattern: "variational"
        classicalOptimizer: "COBYLA"
        maxIterations: 100
        convergenceTolerance: 1e-4
    }
}
```

### Usage in SMP

```tcl
# In the spreadsheet
A1: =GRAPH(vertices, edges)  # Problem instance
B1: =MAXCUT_QAOA(A1)         # Quantum tile
C1: =B1.value                # Extract cut value
D1: =B1.confidence           # Extract confidence
E1: =IF(D1 > 0.90, "AUTO_ACCEPT", "REVIEW")

# If quantum unavailable, automatically falls back to classical
```

---

## Example 2: VQE Molecular Ground State

### Problem Definition

Find the ground state energy of a molecule (e.g., H2, LiH, BeH2).

### Classical Baseline

```typescript
// Classical: Full Configuration Interaction (FCI)
function classicalMolecularGroundState(molecule: Molecule): GroundState {
    const hamiltonian = buildHamiltonian(molecule)  // Second quantization
    const eigenvalues = diagonalize(hamiltonian)  # Exponential scaling
    const groundEnergy = min(eigenvalues)

    return {
        energy: groundEnergy,
        wavefunction: eigenvectors[0],
        confidence: 1.0  // Exact (within basis set)
    }
}
```

### Quantum Tile Implementation

```typescript
interface MolecularVQETile extends QuantumTile<Molecule, GroundState> {
    name: "molecular_vqe"

    config: {
        ansatz: "unitary_coupled_cluster"  // UCCSD
        shots: 10000
        backend: "ibmq_guadalupe"
        mitigation: "symmetry_verification"
    }

    // Encode molecule to Hamiltonian
    encode: (molecule: Molecule) => Hamiltonian => {
        // 1. Compute integrals (classical)
        const integrals = computeIntegrals(molecule)

        // 2. Second quantization
        const secondQuantized = secondQuantization(integrals, molecule.basis)

        // 3. Jordan-Wigner mapping to qubits
        const jordanWigner = jordanWignerTransform(secondQuantized)

        return jordanWigner
    }

    // VQE circuit
    circuit: (hamiltonian: Hamiltonian, theta: number[]) => QuantumCircuit => {
        const n = hamiltonian.numQubits
        const circuit = new QuantumCircuit(n)

        // Hartree-Fock initial state |111100...>
        prepareHartreeFock(circuit, molecule.numElectrons)

        // UCCSD ansatz
        const numExcitations = countSingleExcitations() + countDoubleExcitations()
        for (let i = 0; i < numExcitations; i++) {
            const excitation = excitations[i]
            const theta_i = theta[i]

            // Excitation: exp(-i * theta_i * (a_dagger_a - a_a_dagger))
            circuit.cuExcitation(excitation, theta_i)
        }

        circuit.measure(all)
        return circuit
    }

    // Decode measurements to energy
    decode: (measurements: Bitstring[], hamiltonian: Hamiltonian) => number => {
        // Compute expectation value <psi|H|psi>
        let energy = 0
        for (const [coeff, pauli] of hamiltonian.terms) {
            const measurement = measurePauli(measurements, pauli)
            energy += coeff * measurement
        }
        return energy
    }

    // Variational loop
    run: (molecule: Molecule) => GroundState => {
        const hamiltonian = this.encode(molecule)
        let theta = randomInitialize(hamiltonian.numExcitations)
        const energies = []

        while (!converged) {
            // Quantum: Evaluate energy at theta
            const circuit = this.circuit(hamiltonian, theta)
            const measurements = quantumBackend.run(circuit, this.config.shots)
            const energy = this.decode(measurements, hamiltonian)

            energies.push(energy)

            // Classical: Update theta
            const gradient = estimateGradient(theta, hamiltonian)
            theta = optimizer.update(theta, gradient)

            // Check convergence
            if (abs(energy - energies[-2]) < 1e-6) {
                break
            }
        }

        return {
            energy: energies[energies.length - 1],
            wavefunction: theta,  # Parameters define the state
            confidence: convergenceConfidence(energies)
        }
    }

    fallback: classicalMolecularGroundState
}
```

### Usage in SMP

```tcl
# Drug discovery pipeline
A1: =MOLECULE("caffeine")              # Target molecule
B1: =MOLECULAR_VQE(A1)                 # Quantum tile
C1: =B1.energy                         # Ground state energy
D1: =PROPERTY_PREDICTION(A1, C1)       # Classical: predict properties
E1: =FILTER(D1, "binding_affinity > 0.9")

# If VQE fails, falls back to classical FCI (slower, same result)
```

---

## Example 3: Quantum Kernel SVM

### Problem Definition

Classify data points using quantum feature space for kernel estimation.

### Classical Baseline

```typescript
// Classical: RBF kernel SVM
function classicalSVM(train: Data[], test: Data): Classification {
    const svm = new SVM({kernel: 'rbf'})
    svm.train(train)
    return svm.predict(test)
}
```

### Quantum Tile Implementation

```typescript
interface QuantumKernelTile extends QuantumTile<{x1: Vector, x2: Vector}, number> {
    name: "quantum_kernel"

    config: {
        featureMap: "zz_feature_map"  # Hardware-efficient
        shots: 10000
        backend: "ibmq_perth"
        mitigation: "readout_error_mitigation"
    }

    // ZZ feature map
    circuit: ({x1, x2}: {x1: Vector, x2: Vector}) => QuantumCircuit => {
        const n = x1.length
        const circuit = new QuantumCircuit(n)

        // Encode x1 into data qubits
        for (let i = 0; i < n; i++) {
            circuit.h(i)
            circuit.rz(2 * x1[i], i)
        }

        // Entanglement
        for (let i = 0; i < n - 1; i++) {
            circuit.zz(2 * x1[i] * x1[i+1], i, i+1)
        }

        // Encode x2 into ancilla (for overlap measurement)
        // ... (omitted for brevity)

        // Measure overlap
        circuit.swapTest(all)

        return circuit
    }

    // Decode to kernel value
    decode: (measurements: Bitstring[]) => number => {
        // Swap test: probability of measuring |0> on control qubit
        const zeroCount = measurements.filter(m => m[0] === 0).length
        const probability = zeroCount / measurements.length

        // Kernel = |<phi(x1)|phi(x2)>|^2
        return 2 * probability - 1
    }

    // Confidence from measurement statistics
    confidence: (measurements: Bitstring[]) => number => {
        const variance = computeVariance(measurements)
        return 1 - sqrt(variance / measurements.length)
    }

    fallback: ({x1, x2}) => rbfKernel(x1, x2)  # Classical RBF
}
```

### Full SVM Pipeline (Multiple Tiles)

```tcl
# Training phase
A1:A1000 = TRAINING_DATA
B1:B1000 = QUANTUM_KERNEL(A1:A1000, A1:A1000)  # Kernel matrix
C1 = SVM_TRAIN(B1:B1000, LABELS)               # Classical SVM training

# Inference phase
D1 = TEST_DATA
E1 = QUANTUM_KERNEL(C1.alpha, D1)              # Quantum kernel evaluation
F1 = SVM_PREDICT(C1.model, E1)                  # Classical SVM prediction
```

---

## Example 4: Hybrid Quantum-Classical Optimization

### Problem: Portfolio Optimization

Classical: Markowitz mean-variance optimization (quadratic programming)
Quantum: QAOA for discrete asset selection

```typescript
interface PortfolioTile extends QuantumTile<MarketData, Portfolio> {
    name: "portfolio_qaoa"

    // Two-stage optimization
    run: (marketData: MarketData) => Portfolio => {
        // Stage 1: Quantum - Discrete asset selection (QAOA)
        const selection = this.quantumSelection(marketData)

        // Stage 2: Classical - Continuous allocation (quadratic programming)
        const allocation = this.classicalAllocation(marketData, selection)

        return {
            assets: selection,
            weights: allocation,
            expectedReturn: computeReturn(allocation),
            risk: computeRisk(allocation)
        }
    }

    // Quantum stage: Select top k assets
    quantumSelection: (marketData: MarketData) => Asset[] => {
        // Formulate as QUBO: maximize return, minimize correlation
        const Q = buildSelectionQUBO(marketData)

        const circuit = qaoaCircuit(Q, depth=3)
        const measurements = quantumBackend.run(circuit, shots=5000)

        // Select top assets from measurement
        const selected = this.decodeSelection(measurements)
        return selected
    }

    // Classical stage: Allocate weights to selected assets
    classicalAllocation: (marketData: MarketData, selected: Asset[]) => number[] => {
        // Quadratic programming: min w^T * Sigma * w
        const sigma = marketData.covarianceMatrix.subset(selected)
        const mu = marketData.expectedReturns.subset(selected)

        const result = solveQP({objective: 'minimize', Q: sigma, c: -mu, constraints: [...]})

        return result.weights
    }

    fallback: (marketData) => classicalMarkowitz(marketData)
}
```

### Usage

```tcl
# Financial portfolio optimization
A1:F100 = MARKET_DATA(stocks, bonds, crypto)
G1 = PORTFOLIO_QAOA(A1:F100)
H1 = RISK_ANALYSIS(G1)
I1 = IF(G1.confidence > 0.85, "EXECUTE", "REVIEW")
```

---

## Example 5: Quantum Tile Composition

### Chain: Search → Verify → Optimize

```tcl
# Tile chain for optimization problem

# Tile 1: Quantum search (Grover)
A1 = PROBLEM_INSTANCE
B1 = GROVER_SEARCH(A1, constraints)  # Find feasible solutions

# Tile 2: Classical filter (remove duplicates)
C1 = UNIQUE(B1)

# Tile 3: Quantum optimization (QAOA)
D1 = QAOA_OPTIMIZE(C1, objective)  # Optimize among feasible solutions

# Tile 4: Classical validation
E1 = VALIDATE_SOLUTION(D1, A1)

# Tile 5: Confidence aggregation
F1 = AGGREGATE_CONFIDENCE(B1, D1, E1)

# Result: Optimal solution with quantum confidence
G1 = IF(F1 > 0.90, D1, FALLBACK_CLASSICAL(A1))
```

### Confidence Flow

```
B1.confidence: 0.88 (Grover found solutions)
C1.confidence: 0.88 (no change, classical filter)
D1.confidence: 0.92 (QAOA optimized)
E1.confidence: 0.95 (validation passed)
F1.confidence: 0.75 (0.88 * 0.92 * 0.95 < 0.90 due to multiplication)

# Result: FALLBACK (not high enough confidence)
```

---

## ASCII Diagrams

### Quantum Tile Lifecycle

```
┌────────────────────────────────────────────────────────────┐
│  Input: Classical Data                                     │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│  Decision: Quantum Backend Available?                      │
│  ┌────────────────┬───────────────────────────────────┐   │
│  │ YES            │ NO                               │   │
│  ▼                ▼                                   │   │
│  [Quantum Path]   [Classical Fallback]                │   │
└────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│  Quantum Path (if available)                               │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 1. Encode: Classical → Quantum State                 │ │
│  │    (amplitude encoding, angle encoding, etc.)        │ │
│  ├──────────────────────────────────────────────────────┤ │
│  │ 2. Execute: Quantum Circuit (with error mitigation)  │ │
│  │    (QAOA, VQE, Grover, etc.)                         │ │
│  ├──────────────────────────────────────────────────────┤ │
│  │ 3. Measure: Quantum → Classical (repeated shots)     │ │
│  │    (100-10000 measurements)                          │ │
│  ├──────────────────────────────────────────────────────┤ │
│  │ 4. Decode: Measurements → Solution                   │ │
│  │    (most frequent, expectation value, etc.)          │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│  Output: Classical Data + Confidence                       │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ solution: <classical result>                         │ │
│  │ confidence: 0.XX (from measurement concentration)    │ │
│  │ trace: "Quantum path: QAOA depth=3, shots=1000"      │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
```

---

### Hybrid Variational Loop (VQE/QAOA)

```
┌─────────────────────────────────────────────────────────────┐
│  Classical Optimizer (COBYLA, SPSA, Adam)                   │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                                                       │ │
│  │  Parameters θ                                        │ │
│  │     │                                                 │ │
│  │     ▼                                                 │ │
│  │  ┌─────────────────────────────────────────────┐     │ │
│  │  │  Quantum Computer                            │     │ │
│  │  │  ┌────────────────────────────────────────┐  │     │ │
│  │  │  │ 1. Prepare state |ψ(θ)>               │  │     │ │
│  │  │  ├────────────────────────────────────────┤  │     │ │
│  │  │  │ 2. Apply problem Hamiltonian H         │  │     │ │
│  │  │  ├────────────────────────────────────────┤  │     │ │
│  │  │  │ 3. Measure expectation ⟨ψ(θ)|H|ψ(θ)⟩   │  │     │ │
│  │  │  └────────────────────────────────────────┘  │     │ │
│  │  │                                                │     │ │
│  │  │  Energy E(θ)                                   │     │ │
│  │  └─────────────────────────────────────────────┘     │ │
│  │     │                                                 │ │
│  │     ▼                                                 │ │
│  │  Update θ → θ - α * ∇E(θ)                            │ │
│  │     │                                                 │ │
│  │     └─────────────────────────────────────────────┘   │ │
│  │                                                       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                          │
│  Repeat until convergence (|E_new - E_old| < ε)           │
└─────────────────────────────────────────────────────────────┘
```

---

### Divide-and-Conquer Pattern

```
┌────────────────────────────────────────────────────────────┐
│  Input: Large Problem (N variables)                       │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│  Classical Decomposition                                   │
│  ┌──────────────┬──────────────┬──────────────┐           │
│  │ Subproblem 1 │ Subproblem 2 │ Subproblem 3 │  (N/3 each)│
│  └──────────────┴──────────────┴──────────────┘           │
└────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│  Parallel Quantum Solving                                  │
│  ┌──────────────┬──────────────┬──────────────┐           │
│  │ [Quantum]    │ [Classical]  │ [Quantum]    │           │
│  │ Subproblem 1 │ Subproblem 2 │ Subproblem 3 │           │
│  │ (< 50 qubits)│ (> 50 qubits)│ (< 50 qubits)│           │
│  └──────────────┴──────────────┴──────────────┘           │
└────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│  Classical Combination                                     │
│  Combine subproblem solutions → Full solution              │
└────────────────────────────────────────────────────────────┘
```

---

### Error Mitigation Pipeline

```
┌────────────────────────────────────────────────────────────┐
│  Raw Quantum Result (Noisy)                                │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Energy: -1.234 ± 0.15 Hartree                        │ │
│  │ Error: 8%                                            │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────┬───────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│  Error Mitigation Strategy Selection                       │
│  ┌────────────────┬────────────────┬──────────────────┐  │
│  │ ZNE            │ PEC             │ Symmetry         │  │
│  │ (Extrapolation)│ (Cancellation)  │ (Verification)   │  │
│  └────────────────┴────────────────┴──────────────────┘  │
└────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│  Mitigated Result                                         │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ Energy: -1.287 ± 0.03 Hartree                        │ │
│  │ Error: 1.5%                                          │ │
│  │ Improvement: 5.3x                                    │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│  Confidence Update                                        │
│  raw_confidence: 0.72                                      │
│  mitigated_confidence: 0.93                                │
│  improvement: +0.21                                        │
└────────────────────────────────────────────────────────────┘
```

---

## Testing Strategy

### Unit Tests

```typescript
describe('QuantumTile: MaxCut QAOA', () => {
    it('should return valid cut', async () => {
        const graph = createTestGraph(10)  // 10 vertices
        const tile = new MaxCutQAOATile()

        const result = await tile.run(graph)

        expect(result.partition.setA.size + result.partition.setB.size).toBe(10)
        expect(result.value).toBeGreaterThan(0)
        expect(result.confidence).toBeGreaterThan(0)
    })

    it('should fallback to classical if quantum unavailable', async () => {
        const graph = createTestGraph(10)
        const tile = new MaxCutQAOATile({backend: 'unavailable'})

        const result = await tile.run(graph)

        expect(result.trace).toContain('Classical fallback')
    })

    it('should improve with error mitigation', async () => {
        const graph = createTestGraph(10)
        const tile = new MaxCutQAOATile()

        const resultRaw = await tile.run(graph, {mitigation: 'none'})
        const resultMitigated = await tile.run(graph, {mitigation: 'zne'})

        expect(resultMitigated.confidence).toBeGreaterThan(resultRaw.confidence)
    })
})
```

### Integration Tests

```typescript
describe('Quantum Tile Integration', () => {
    it('should compose with classical tiles', async () => {
        const graph = createTestGraph(10)

        // Quantum tile
        const maxcutTile = new MaxCutQAOATile()

        // Classical tile (filter)
        const filterTile = new FilterTile((cut) => cut.value > 5)

        // Compose: maxcut >> filter
        const result = await maxcutTile.run(graph)
        const filtered = await filterTile.run(result)

        expect(filtered.value).toBeGreaterThan(5)
        expect(filtered.confidence).toBeLessThanOrEqual(result.confidence)
    })
})
```

---

*Examples Complete | For implementation questions, see main research document*
