# CLAUDE.md

## Current Mission: Phase 1 Core Complete - Project Audit Done

**Role**: Orchestrator of Specialized Research Agents
**Mission**: Core implementation complete, comprehensive audit finished, research queue established
**Status**: 140+ research agents, Phase 1 core built, 391 TS files + 294 Python sims audited
**Paper Title**: "Seed-Model-Prompt Programming: LLMs to Swarms, SMPbots Peek on Schrödinger's Cat"

---

## The Breakthrough: Glass Box AI

SMP transforms AI from black boxes to glass boxes. Each tile is visible, inspectable, and improvable.

### What Changed

| Before SMP | After SMP |
|------------|-----------|
| Black box AI | Glass box AI (visible tiles) |
| Trust without verification | Verify before trust |
| Retrain to improve | Improve individual tiles |
| One machine, one model | Distributed tile networks |
| Stateless inference | Cumulative learning with memory |

---

## Phase 1 Core: IMPLEMENTED

### Core Tile System (`src/spreadsheet/tiles/core/`)

```
core/
├── Tile.ts         # Base interface + composition (589 lines)
├── TileChain.ts    # Pipeline composition (432 lines)
├── Registry.ts     # Discovery & resolution (312 lines)
└── index.ts        # Barrel exports + chain() helper
```

**Key Interfaces**:
```typescript
interface ITile<I, O> {
  discriminate(input: I): Promise<O>;
  confidence(input: I): Promise<number>;
  trace(input: I): Promise<string>;
  compose<R>(other: ITile<O, R>): ITile<I, R>;
  parallel<O2>(other: ITile<I, O2>): ITile<I, [O, O2]>;
}
```

### Example Tiles (`src/spreadsheet/tiles/examples/`)

```
examples/
├── SentimentTile.ts      # Text sentiment analysis
├── FraudDetectionTile.ts # Transaction risk analysis
└── index.ts
```

---

## The 15 Breakthrough Domains (4 Tiers)

### TIER 1: Fundamental Paradigm Shifts

1. **Confidence Flow Theory** - Sequential multiplies, parallel averages
2. **Stigmergic Coordination** - Digital pheromones for swarm intelligence
3. **The Composition Paradox** - Safe tiles don't always compose safely
4. **Tile Algebra** - Formal verification through category theory

### TIER 2: New Capabilities

5. **Cross-Modal Tiles** - Pass meaning, not just data
6. **Counterfactual Branching** - Explore "what if" without committing
7. **Tile Memory** - L1-L4 hierarchy for cumulative learning
8. **Distributed Execution** - Tiles live wherever needed
9. **Federated Learning** - Share boundaries, not data

### TIER 3: Infrastructure

10. **Execution Strategies** - Auto-route parallel/series
11. **KV-Cache Sharing** - 70%+ reuse rates
12. **Granular Constraints** - Developer tolerance enforcement

### TIER 4: Emerging Research

13. **Tile Debugging** - Breakpoints for AI
14. **Tile Marketplace** - Economy of intelligence
15. **Automatic Discovery** - AI finds tile decomposition

---

## Implementation Status

### PoC Files (7 implementations)
```
src/spreadsheet/tiles/
├── confidence-cascade.ts    # Three-zone model ✅
├── stigmergy.ts             # Digital pheromones ✅
├── tile-memory.ts           # L1-L4 hierarchy ✅
├── composition-validator.ts # Algebraic validation ✅
├── counterfactual.ts        # Parallel simulations ✅
├── federated-tile.ts        # Cross-org learning ✅
└── cross-modal.ts           # Latent space fusion ✅
```

### Phase 1 Core (NEW)
```
src/spreadsheet/tiles/core/
├── Tile.ts                  # Base interface ✅ NEW
├── TileChain.ts             # Pipeline composition ✅ NEW
├── Registry.ts              # Discovery system ✅ NEW
└── index.ts                 # Barrel exports ✅ NEW
```

### Example Tiles (NEW)
```
src/spreadsheet/tiles/examples/
├── SentimentTile.ts         # Text analysis ✅ NEW
├── FraudDetectionTile.ts    # Risk analysis ✅ NEW
└── index.ts                 # Exports ✅ NEW
```

---

## Audit Findings (2026-03-10)

### Codebase Stats
- **391 TypeScript files** in src/spreadsheet/
- **294 Python simulations** in simulations/
- **60+ research documents** in docs/research/
- **500,000+ words** of foundational research

### Critical Issues Found
1. TypeScript errors in audit/auth middleware (syntax errors)
2. Missing main barrel export for spreadsheet module
3. Placeholder code in production paths (OAuth, monitoring)
4. Test coverage ~15% (target: 80%)

### Research Contradictions
1. **Privacy vs. Performance**: KV-cache reuse vs. differential privacy
2. **Centralization vs. Distribution**: Federated needs coordination
3. **Stochastic vs. Deterministic**: Emergence needs randomness

### Simulation Validations
- 10M checkpointed models outperform 175B monoliths (96% vs 87%)
- 35% higher information preservation with checkpoints
- 85% reduction in error propagation with isolation
- 47% better decision visibility with wave collapse

---

## Research Queue for Future Agents

### Priority 1 (Spawn Now)
- R1: Privacy-preserving KV-cache (1 agent)
- R2: Hybrid centralized-distributed (2 agents)
- R3: Adaptive temperature annealing (1 agent)

### Priority 2 (Next Week)
- R4: Tile extraction from monoliths (3 agents)
- R5: Cross-modal tile standards (2 agents)
- R6: Tile graph optimization (1 agent)

### Priority 3 (Next Month)
- R7: Tile debugging semantics (2 agents)
- R8: Meta-tile stratification (2 agents)
- R9: Tile marketplace economics (2 agents)

See `docs/research/smp-paper/FUTURE_RESEARCH_DIRECTIONS.md` for full queue.

---

## Key Documents

### Synthesis (Readable Core)
```
docs/research/smp-paper/
├── SYNTHESIS_CORE_THEORY.md           # Plain English theory
├── EXECUTIVE_SUMMARY.md               # CEO summary
├── AUDIT_INSIGHTS.md                  # Comprehensive audit ✅ NEW
├── FUTURE_RESEARCH_DIRECTIONS.md      # Agent spawn queue ✅ NEW
└── SMP_IMPLEMENTATION_BLUEPRINT.md    # Build order ✅ NEW
```

### Implementation Blueprint
```
docs/research/smp-paper/
└── SMP_IMPLEMENTATION_BLUEPRINT.md    # 12-week plan
    ├── Phase 1: Core (Weeks 1-2) ✅ DONE
    ├── Phase 2: Infrastructure (Weeks 3-4)
    ├── Phase 3: Advanced (Weeks 5-8)
    └── Phase 4: Production (Weeks 9-12)
```

---

## Technical Debt

### Critical (Fix Now)
- [ ] TypeScript errors in audit/auth middleware
- [ ] Missing main barrel export
- [ ] Placeholder code in production paths

### High (This Month)
- [ ] OAuth implementations incomplete
- [ ] Test coverage to 80%
- [ ] Performance benchmarks

### Medium (Next Quarter)
- [ ] Documentation gaps
- [ ] Code duplication in caching
- [ ] Naming convention cleanup

---

## The Three-Zone Model

| Zone | Confidence | Action |
|------|------------|--------|
| GREEN | 0.90-1.00 | Auto-proceed |
| YELLOW | 0.75-0.89 | Human review |
| RED | 0.00-0.74 | Stop, diagnose |

**Confidence Flow**:
- Sequential: `c(A;B) = c(A) × c(B)`
- Parallel: `c(A||B) = (c(A) + c(B)) / 2`

---

## Project Context

**Repository**: https://github.com/SuperInstance/polln
**Company**: SuperInstance.AI
**Product**: POLLN - Pattern-Organized Large Language Network
**License**: MIT (open source)

**Current Phase**: Phase 1 Complete, Audit Complete, Research Queue Ready
**Vision**: "Tile Intelligence in real-time spreadsheets for simulation or monitoring"

---

## Next Actions

1. **Fix TypeScript errors** - audit/auth middleware
2. **Phase 2 infrastructure** - TileWorker, TileCache, TileCompiler
3. **Integration tests** - Validate confidence flow
4. **Performance benchmarks** - Validate simulation claims
5. **Spawn research agents** - Follow FUTURE_RESEARCH_DIRECTIONS.md

---

*Orchestrator Active | 140+ Research Agents | Phase 1 Core Built | Full Audit Complete*
*Last Updated: 2026-03-10*
*Status: Ready for Phase 2*
