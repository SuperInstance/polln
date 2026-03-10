# Quantum Tiles: Visual Guide

**Companion to:** QUANTUM_TILES_RESEARCH.md
**Date:** 2026-03-10

---

## Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SMP QUANTUM TILE ECOSYSTEM                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐                │
│  │   CLASSICAL│    │   HYBRID   │    │   QUANTUM  │                │
│  │    TILES   │    │    TILES   │    │    TILES   │                │
│  │            │    │            │    │            │                │
│  │  - Filter  │    │  - QAOA    │    │  - Grover  │                │
│  │  - Transform│   │  - VQE     │    │  - HHL     │                │
│  │  - Validate│    │  - Quantum │    │  - Shor    │                │
│  │  - Aggregate│   │    Kernel  │    │            │                │
│  └────────────┘    └────────────┘    └────────────┘                │
│         │                  │                  │                     │
│         └──────────────────┴──────────────────┘                     │
│                            │                                        │
│                            ▼                                        │
│                 ┌─────────────────────┐                             │
│                 │  TILE COMPOSITION   │                             │
│                 │  (Chain, Parallel)  │                             │
│                 └─────────────────────┘                             │
│                            │                                        │
│                            ▼                                        │
│                 ┌─────────────────────┐                             │
│                 │  EXECUTION ENGINE   │                             │
│                 │  - Auto-route       │                             │
│                 │  - Parallelize      │                             │
│                 │  - Fallback         │                             │
│                 └─────────────────────┘                             │
│                            │                                        │
│                            ▼                                        │
│                 ┌─────────────────────┐                             │
│                 │  BACKEND LAYER      │                             │
│                 │  ┌─────────┐        │                             │
│                 │  │CPU/GPU  │        │                             │
│                 │  ├─────────┤        │                             │
│                 │  │Quantum  │        │                             │
│                 │  │Simulator│       │                             │
│                 │  ├─────────┤        │                             │
│                 │  │Real QC  │        │                             │
│                 │  │(IBM/Google)│     │                             │
│                 │  └─────────┘        │                             │
│                 └─────────────────────┘                             │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Quantum Tile Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                     QUANTUM TILE INTERNAL STRUCTURE                 │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  INPUT: Classical Data                                            │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ {problem: "maxcut", graph: {vertices: 10, edges: [...]}   │     │
│  └──────────────────────────────────────────────────────────┘     │
│                              │                                     │
│                              ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              CLASSICAL PRE-PROCESSING                      │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ 1. Validate input constraints                        │  │   │
│  │  │ 2. Check quantum backend availability                │  │   │
│  │  │ 3. Decide: quantum or classical fallback?             │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                     │
│              ┌───────────────┴───────────────┐                     │
│              │                               │                     │
│              ▼                               ▼                     │
│  ┌──────────────────────┐      ┌──────────────────────┐           │
│  │   QUANTUM PATH       │      │  CLASSICAL FALLBACK  │           │
│  │  (if backend OK)     │      │  (if quantum fails)  │           │
│  ├──────────────────────┤      ├──────────────────────┤           │
│  │ 1. ENCODE            │      │ 1. Run classical     │           │
│  │    Classical →       │      │    algorithm         │           │
│  │    Quantum State     │      │ 2. Compute confidence│           │
│  │                      │      │ 3. Return result     │           │
│  │    Example:           │      │                      │           │
│  │    - Amplitude encode │      │                      │           │
│  │    - Angle encode     │      │                      │           │
│  │    - Basis encode     │      │                      │           │
│  │                      │      │                      │           │
│  │ 2. EXECUTE           │      │                      │           │
│  │    Quantum Circuit   │      │                      │           │
│  │                      │      │                      │           │
│  │    Example:           │      │                      │           │
│  │    - QAOA circuit     │      │                      │           │
│  │    - VQE circuit      │      │                      │           │
│  │    - Grover circuit   │      │                      │           │
│  │    - Depth: 3-100     │      │                      │           │
│  │                      │      │                      │           │
│  │ 3. MEASURE           │      │                      │           │
│  │    Quantum →          │      │                      │           │
│  │    Classical          │      │                      │           │
│  │                      │      │                      │           │
│  │    Shots: 100-10000   │      │                      │           │
│  │                      │      │                      │           │
│  │ 4. ERROR MITIGATION  │      │                      │           │
│  │    - ZNE              │      │                      │           │
│  │    - PEC              │      │                      │           │
│  │    - Symmetry         │      │                      │           │
│  │                      │      │                      │           │
│  │ 5. DECODE            │      │                      │           │
│  │    Measurements →     │      │                      │           │
│  │    Solution           │      │                      │           │
│  │                      │      │                      │           │
│  │    Example:           │      │                      │           │
│  │    - Most frequent    │      │                      │           │
│  │    - Expectation      │      │                      │           │
│  │    - Histogram        │      │                      │           │
│  │                      │      │                      │           │
│  │ 6. CONFIDENCE        │      │                      │           │
│  │    - Measurement      │      │                      │           │
│  │      concentration    │      │                      │           │
│  │    - Error mitigation │      │                      │           │
│  │      residual         │      │                      │           │
│  │    - Convergence      │      │                      │           │
│  │    - Solution quality │      │                      │           │
│  └──────────────────────┘      └──────────────────────┘           │
│              │                               │                     │
│              └───────────────┬───────────────┘                     │
│                              │                                     │
│                              ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              CLASSICAL POST-PROCESSING                     │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ 1. Validate output constraints                       │  │   │
│  │  │ 2. Compute trace (which path was used?)              │  │   │
│  │  │ 3. Aggregate confidence                              │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  OUTPUT: Classical Data + Confidence + Trace                     │
│  ┌──────────────────────────────────────────────────────────┐     │
│  │ {                                                        │     │
│  │   solution: {cut: [0,1,1,0,1,0,0,1,1,0], value: 12},     │     │
│  │   confidence: 0.87,                                      │     │
│  │   trace: "Quantum path: QAOA depth=3, shots=1000, ZNE"  │     │
│  │ }                                                        │     │
│  └──────────────────────────────────────────────────────────┘     │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Hybrid Algorithm: Variational Loop (VQE/QAOA)

```
┌────────────────────────────────────────────────────────────────────┐
│                    VARIATIONAL QUANTUM-CLASSICAL LOOP               │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              CLASSICAL OPTIMIZER                           │   │
│  │              (COBYLA, SPSA, Adam)                          │   │
│  │                                                             │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ Parameters θ (initial: random)                       │  │   │
│  │  │ θ = [θ₁, θ₂, ..., θₙ]                                │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                          │                                 │   │
│  │                          ▼                                 │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ Send θ to quantum computer                          │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────────────┘   │
│                          │                                         │
│                          ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              QUANTUM COMPUTER                             │   │
│  │                                                             │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ 1. PREPARE STATE |ψ(θ)⟩                             │  │   │
│  │  │    - Encode problem into qubits                      │  │   │
│  │  │    - Apply parameterized unitary U(θ)                 │  │   │
│  │  │                                                       │  │   │
│  │  │    Example:                                          │  │   │
│  │  │    QAOA: |+⟩ → U_C(γ) → U_B(β) → ... → |ψ(θ)⟩      │  │   │
│  │  │    VQE:  |HF⟩ → UCCSD(θ) → |ψ(θ)⟩                  │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                          │                                 │   │
│  │                          ▼                                 │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ 2. APPLY PROBLEM HAMILTONIAN                         │  │   │
│  │  │    - QAOA: Cost Hamiltonian H_C (MaxCut, TSP, etc.)  │  │   │
│  │  │    - VQE: Molecular Hamiltonian H_mol                │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                          │                                 │   │
│  │                          ▼                                 │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ 3. MEASURE EXPECTATION VALUE                         │  │   │
│  │  │    - Measure qubits in computational basis           │  │   │
│  │  │    - Repeat for N shots (100-10000)                  │  │   │
│  │  │    - Compute ⟨ψ(θ)|H|ψ(θ)⟩                           │  │   │
│  │  │                                                       │  │   │
│  │  │    Result: Energy E(θ) or Cost C(θ)                  │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────────────┘   │
│                          │                                         │
│                          ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              RETURN E(θ) TO CLASSICAL OPTIMIZER            │   │
│  └────────────────────────────────────────────────────────────┘   │
│                          │                                         │
│                          ▼                                         │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              CLASSICAL OPTIMIZER (CONTINUED)               │   │
│  │                                                             │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ Compute gradient ∇E(θ) or ∇C(θ)                       │  │   │
│  │  │    - Parameter-shift rule (exact)                    │  │   │
│  │  │    - Finite difference (approximate)                 │  │   │
│  │  │                                                       │  │   │
│  │  │ Update parameters:                                   │  │   │
│  │  │ θ_new = θ_old - α * ∇E(θ)                            │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                          │                                 │   │
│  │                          ▼                                 │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ Check convergence:                                   │  │   │
│  │  │ |E_new - E_old| < ε ?                                │  │   │
│  │  │                                                       │  │   │
│  │  ┌───────────┬───────────┐                              │  │   │
│  │  │ YES       │ NO        │                              │  │   │
│  │  │ (Done)    │ (Repeat)  │                              │  │   │
│  │  └───────────┴───────────┘                              │  │   │
│  │       │           │                                      │  │   │
│  │       │           └────────────────────────┐             │  │   │
│  │       │                                  │             │  │   │
│  │       ▼                                  ▼             │  │   │
│  │  ┌─────────────────┐           ┌────────────────────┐   │  │   │
│  │  │ RETURN          │           │ SEND θ_new BACK    │   │  │   │
│  │  │ θ_optimal,      │           │ TO QUANTUM         │   │  │   │
│  │  │ E_optimal       │           │ COMPUTER          │   │  │   │
│  │  └─────────────────┘           └────────────────────┘   │  │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

Typical convergence: 50-1000 iterations
Each iteration: 1-10 quantum circuit executions (for gradient)
Total quantum time: minutes to hours
```

---

## Divide and Conquer Pattern

```
┌────────────────────────────────────────────────────────────────────┐
│                    DIVIDE-AND-CONQUER QUANTUM TILE                 │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  INPUT: Large Problem (N variables, N > quantum qubits)           │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Problem: TSP with 100 cities (needs > 100 qubits)          │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              CLASSICAL DECOMPOSITION                       │   │
│  │                                                             │   │
│  │  Strategy 1: Geographic clustering                         │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ Cluster 1: Cities 1-20   (North)                     │  │   │
│  │  │ Cluster 2: Cities 21-40  (South)                     │  │   │
│  │  │ Cluster 3: Cities 41-60  (East)                      │  │   │
│  │  │ Cluster 4: Cities 61-80  (West)                      │  │   │
│  │  │ Cluster 5: Cities 81-100 (Central)                   │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                          │                                 │   │
│  │                          ▼                                 │   │
│  │  Each cluster: ~20 cities → needs ~20 qubits ✓             │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              PARALLEL SOLVING (HYBRID)                    │   │
│  │                                                             │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ Cluster 1: [QUANTUM] QAOA, 20 qubits                 │  │   │
│  │  │ Cluster 2: [QUANTUM] QAOA, 20 qubits                 │  │   │
│  │  │ Cluster 3: [CLASSICAL] Simulated annealing           │  │   │
│  │  │ Cluster 4: [QUANTUM] QAOA, 20 qubits                 │  │   │
│  │  │ Cluster 5: [CLASSICAL] Genetic algorithm             │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  │                          │                                 │   │
│  │                          ▼                                 │   │
│  │  Note: Can run 2-3 clusters in parallel on real QC       │   │
│  │       (if backend has enough qubits)                      │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              CLASSICAL COMBINATION                        │   │
│  │                                                             │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ 1. Solve inter-cluster routing (classical TSP)       │  │   │
│  │  │ 2. Merge intra-cluster solutions                     │  │   │
│  │  │ 3. Global optimization (local search)                │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  OUTPUT: Full solution for 100-city TSP                           │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Solution: 2 → 15 → 3 → ... → 87 → 12                       │   │
│  │ Cost: 3247 (quantum-enhanced)                              │   │
│  │ Confidence: 0.82 (some clusters classical)                 │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Error Mitigation Pipeline

```
┌────────────────────────────────────────────────────────────────────┐
│                    ERROR MITIGATION STRATEGIES                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  RAW QUANTUM RESULT (Noisy)                                        │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Measurements: [0, 1, 0, 1, 0, 0, 1, 1, 0, 1, ...]           │   │
│  │ Energy: -1.234 Hartree                                    │   │
│  │ Error: ±0.15 Hartree (12%)                                │   │
│  │ Confidence: 0.68 (low)                                    │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │         SELECT ERROR MITIGATION STRATEGY                   │   │
│  │                                                             │   │
│  │  ┌──────────────┬────────────────┬──────────────────────┐  │   │
│  │  │ ZNE          │ PEC            │ Symmetry             │  │   │
│  │  │ (Extrapolate)│ (Invert noise) │ (Check laws)         │  │   │
│  │  ├──────────────┼────────────────┼──────────────────────┤  │   │
│  │  │ Run circuit  │ Run circuit    │ Run circuit          │  │   │
│  │  │ at 3 noise   │ with noise     │ (once)               │  │   │
│  │  │ levels:      │ model          │                      │  │   │
│  │  │ 1x, 2x, 3x   │                │                      │  │   │
│  │  │              │ Estimate noise │ Check if result     │  │   │
│  │  │ Fit line:    │ Invert classically│ respects symmetry │  │   │
│  │  │ E(λ) = a + bλ │ Cancel noise   │ (e.g., particle     │  │   │
│  │  │              │                │ number conservation) │  │   │
│  │  │ Extrapolate  │ Overhead:      │ Overhead: minimal    │  │   │
│  │  │ to λ = 0     │ exponential    │                      │  │   │
│  │  │              │                │ Discard violating    │  │   │
│  │  │ Overhead:    │                │ measurements         │  │   │
│  │  │ 3x           │                │                      │  │   │
│  │  └──────────────┴────────────────┴──────────────────────┘  │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  MITIGATED RESULT                                                │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Energy: -1.287 Hartree                                    │   │
│  │ Error: ±0.02 Hartree (1.5%)                               │   │
│  │ Improvement: 8x reduction in error                        │   │
│  │ Confidence: 0.93 (high)                                   │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │         CONFIDENCE UPDATE                                 │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │ Raw confidence:      0.68                           │  │   │
│  │  │ Mitigation bonus:     +0.25                          │  │   │
│  │  │ Final confidence:     0.93 ✓                         │  │   │
│  │  │                                                       │  │   │
│  │  │ Quality: GOOD → Auto-proceed                         │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Quantum Tile Decision Tree

``┌────────────────────────────────────────────────────────────────────┐
│                  SHOULD THIS TILE BE QUANTUM?                       │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Start: New tile requirement                                       │
│      │                                                             │
│      ▼                                                             │
│  ┌────────────────────────────────┐                               │
│  │ Is problem quantum-native?     │                               │
│  │ (chemistry, physics simulation)│                               │
│  └────────────────────────────────┘                               │
│      │                                                             │
│      ├─YES──► Use QUANTUM tile (VQE)                              │
│      │                                                             │
│      └─NO──► ┌────────────────────────────────┐                   │
│               │ Is there a quantum algorithm? │                   │
│               └────────────────────────────────┘                   │
│                    │                                               │
│                    ├─NO──► Use CLASSICAL tile                      │
│                    │                                               │
│                    └─YES──► ┌─────────────────────────┐            │
│                              │ Problem size small?    │            │
│                              │ (< 2^20 search space)   │            │
│                              └─────────────────────────┘            │
│                                   │                               │
│                                   ├─YES──► Use CLASSICAL          │
│                                   │          (overhead too high)  │
│                                   │                               │
│                                   └─NO──► ┌──────────────────┐    │
│                                            │ Quantum hardware  │    │
│                                            │ available?        │    │
│                                            └──────────────────┘    │
│                                                 │                 │
│                                                 ├─NO──► Use CLASSICAL│
│                                                 │                 │
│                                                 └─YES──► ┌──────────────┐
│                                                           │ Is algorithm │
│                                                           │ NISQ-ready?  │
│                                                           └──────────────┘
│                                                                │
│                                             ┌─────────────────┴────────┐
│                                             │                          │
│                                          YES                        NO
│                                             │                          │
│                                             ▼                          ▼
│                                    Use QUANTUM tile           Use CLASSICAL
│                                    with fallback              (future: fault-
│                                    (QAOA, VQE)                tolerant QC)
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## Confidence Flow in Quantum Tile Chains

```
┌────────────────────────────────────────────────────────────────────┐
│              CONFIDENCE PROPAGATION: QUANTUM TILE CHAIN            │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Input: Market Data                                               │
│  Confidence: 1.0 (given)                                          │
│      │                                                             │
│      ▼                                                             │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Tile 1: DATA_PREPROCESSING (Classical)                     │   │
│  │ Confidence: 1.0 → 1.0 (no change, deterministic)           │   │
│  └────────────────────────────────────────────────────────────┘   │
│      │                                                             │
│      ▼                                                             │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Tile 2: FEATURE_SELECTION (Classical)                      │   │
│  │ Confidence: 1.0 → 0.95 (some uncertainty in features)      │   │
│  └────────────────────────────────────────────────────────────┘   │
│      │                                                             │
│      ▼                                                             │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Tile 3: PORTFOLIO_QAOA (Quantum)                           │   │
│  │ Confidence: 0.95 → 0.87 (quantum uncertainty)              │   │
│  │   - Measurement concentration: 0.92                        │   │
│  │   - Error mitigation residual: 0.95                        │   │
│  │   - Combined: 0.87                                         │   │
│  └────────────────────────────────────────────────────────────┘   │
│      │                                                             │
│      ▼                                                             │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Tile 4: RISK_ANALYSIS (Classical)                          │   │
│  │ Confidence: 0.87 → 0.83 (adds estimation uncertainty)      │   │
│  └────────────────────────────────────────────────────────────┘   │
│      │                                                             │
│      ▼                                                             │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Tile 5: VALIDATION (Classical)                             │   │
│  │ Confidence: 0.83 → 0.79 (validation checks)                │   │
│  └────────────────────────────────────────────────────────────┘   │
│      │                                                             │
│      ▼                                                             │
│  OUTPUT: Portfolio Recommendation                                  │
│  Confidence: 0.79 (YELLOW zone → Human review)                    │
│                                                                    │
│  ZONE CHECK:                                                       │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ GREEN  (0.90-1.00): Auto-proceed                           │   │
│  │ YELLOW (0.75-0.89):  Human review ← THIS                   │   │
│  │ RED    (0.00-0.74):  Stop, diagnose                        │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## NISQ to Fault-Tolerant Roadmap

```
┌────────────────────────────────────────────────────────────────────┐
│               QUANTUM TILE EVOLUTION OVER TIME                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  2026-2028: NISQ ERA                                              │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Hardware: 50-500 physical qubits, noisy                    │   │
│  │                                                            │   │
│  │ Available Tiles:                                           │   │
│  │  ✓ QAOA (optimization, depth < 100)                       │   │
│  │  ✓ VQE (quantum chemistry, shallow circuits)             │   │
│  │  ✓ Quantum kernels (feature maps, shallow)                │   │
│  │  ✓ Quantum neural networks (variational)                  │   │
│  │                                                            │   │
│  │ Not Available:                                             │   │
│  │  ✗ Grover (circuit too deep)                             │   │
│  │  ✗ HHL (circuit too deep)                                │   │
│  │  ✗ Shor (circuit too deep)                               │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  2029-2032: EARLY FAULT-TOLERANT                                  │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Hardware: 1000-10000 logical qubits, error-corrected       │   │
│  │                                                            │   │
│  │ New Tiles Available:                                      │   │
│  │  + Grover (moderate depth search)                         │   │
│  │  + Quantum simulation (larger molecules)                  │   │
│  │  + Quantum ML (improved kernels, QNNs)                    │   │
│  │                                                            │   │
│  │ Still Limited:                                            │   │
│  │  ~ HHL (needs more qubits)                                │   │
│  │  ~ Shor (needs more qubits)                              │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                     │
│                              ▼                                     │
│  2033+: LARGE-SCALE FAULT-TOLERANT                                │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ Hardware: > 10000 logical qubits, fully error-corrected    │   │
│  │                                                            │   │
│  │ All Quantum Algorithms Available:                         │   │
│  │  ✓ Grover (large-scale search)                            │   │
│  │  ✓ HHL (linear systems)                                   │   │
│  │  ✓ Shor (cryptography)                                    │   │
│  │  ✓ Full quantum chemistry                                 │   │
│  │  ✓ Quantum ML (exponential advantages)                    │   │
│  │                                                            │   │
│  │ SMP tiles seamlessly leverage any available quantum        │   │
│  │ speedup without user intervention                           │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

*Visual Guide Complete | For implementation details, see main research document*
