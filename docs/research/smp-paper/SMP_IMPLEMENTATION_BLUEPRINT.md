# SMP Implementation Blueprint

**From Research to Working System**

---

## Purpose

140+ research agents have explored SMP from every angle. This document cuts through the research and provides:

1. **What to build first** (MVP architecture)
2. **How the pieces connect** (system design)
3. **Concrete interfaces** (actual TypeScript)
4. **What to defer** (later phases)

No theory. No justification. Just: here's what we're building.

---

## Core Architecture (MVP)

```
┌─────────────────────────────────────────────────────────────────┐
│                         SMP RUNTIME                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   SPREADSHEET │    │  TILE ENGINE │    │  CONFIDENCE  │      │
│  │    LAYER      │───▶│   RUNTIME    │───▶│   CASCADE    │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  CELL WATCH  │    │  TILE MEMORY │    │  ZONE MONITOR│      │
│  │  (Reactivity)│    │   (L1-L4)    │    │  (Alerting)  │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                 │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │  STIGMERGY   │    │  TRACING     │    │  REGISTRY    │      │
│  │  (Pheromones)│    │  (Debug)     │    │  (Discovery) │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## The 5 Core Interfaces

### 1. Tile (The Atom)

```typescript
interface Tile<I, O> {
  // Identity
  id: string;
  version: string;

  // Types
  inputSchema: Schema<I>;
  outputSchema: Schema<O>;

  // Core operations
  discriminate(input: I): Promise<O>;
  confidence(input: I): Promise<number>;
  trace(input: I): Promise<string>;

  // Composition
  compose<R>(other: Tile<O, R>): Tile<I, R>;
  parallel<O2>(other: Tile<I, O2>): Tile<I, [O, O2]>;

  // Lifecycle
  validate(): ValidationResult;
  serialize(): SerializedTile;
}
```

**What it does**: Single responsibility unit. Takes input, produces output, reports confidence.

**Where it lives**: `src/spreadsheet/tiles/core/Tile.ts`

---

### 2. TileChain (The Pipeline)

```typescript
interface TileChain<I, O> {
  // Construction
  add<T>(tile: Tile<O, T>): TileChain<I, T>;
  branch<A, B>(
    condition: (input: O) => boolean,
    ifTrue: Tile<O, A>,
    ifFalse: Tile<O, B>
  ): TileChain<I, A | B>;

  // Execution
  execute(input: I): Promise<TileResult<O>>;

  // Analysis
  confidence(input: I): Promise<number>;
  validate(): ValidationResult;
  visualize(): string;
}

interface TileResult<O> {
  output: O;
  confidence: number;
  zone: 'GREEN' | 'YELLOW' | 'RED';
  trace: TraceStep[];
  duration: number;
}
```

**What it does**: Composes tiles into pipelines. Handles confidence multiplication.

**Where it lives**: `src/spreadsheet/tiles/core/TileChain.ts`

---

### 3. ConfidenceCascade (The Flow)

```typescript
interface ConfidenceCascade {
  // Configuration
  thresholds: {
    green: number;   // default: 0.90
    yellow: number;  // default: 0.75
  };

  // Operations
  classify(confidence: number): Zone;
  compose(zones: Zone[]): Zone;
  propagate(chain: TileChain<any, any>, input: any): Promise<CascadeResult>;

  // Monitoring
  onZoneChange(callback: (event: ZoneEvent) => void): Unsubscribe;
  getHistory(tileId: string): ZoneHistory;
}

type Zone = 'GREEN' | 'YELLOW' | 'RED';

interface CascadeResult {
  zone: Zone;
  confidence: number;
  shouldProceed: boolean;
  requiresReview: boolean;
}
```

**What it does**: Three-zone model. Routes based on confidence.

**Where it lives**: `src/spreadsheet/tiles/confidence-cascade.ts` (EXISTS)

---

### 4. TileMemory (The State)

```typescript
interface TileMemory {
  // L1: Register (immediate, per-tile)
  l1: {
    get<T>(tileId: string, key: string): T | undefined;
    set<T>(tileId: string, key: string, value: T): void;
    clear(tileId: string): void;
  };

  // L2: Working (session, tile-type shared)
  l2: {
    get<T>(tileType: string, key: string): T | undefined;
    set<T>(tileType: string, key: string, value: T): void;
    invalidate(tileType: string): void;
  };

  // L3: Session (user session, persistent)
  l3: {
    get<T>(key: string): T | undefined;
    set<T>(key: string, value: T): void;
    save(): Promise<void>;
    load(): Promise<void>;
  };

  // L4: Long-term (cross-session, persistent)
  l4: {
    get<T>(key: string): Promise<T | undefined>;
    set<T>(key: string, value: T): Promise<void>;
    query(pattern: string): Promise<T[]>;
  };
}
```

**What it does**: Tiles remember across executions. Cumulative learning.

**Where it lives**: `src/spreadsheet/tiles/tile-memory.ts` (EXISTS)

---

### 5. Stigmergy (The Coordination)

```typescript
interface StigmergyEngine {
  // Pheromone operations
  deposit(cell: CellRef, signal: PheromoneSignal): void;
  sense(cell: CellRef, types?: PheromoneType[]): PheromoneSignal[];
  evaporate(rate?: number): void;

  // Query
  findNearest(cell: CellRef, type: PheromoneType): CellRef | undefined;
  getStrength(cell: CellRef, type: PheromoneType): number;

  // Configuration
  decayRate: number;
  maxStrength: number;
}

interface PheromoneSignal {
  type: 'TASK' | 'RESULT' | 'LOAD' | 'PRIORITY' | 'ERROR';
  strength: number;
  source: string;
  timestamp: number;
  metadata?: Record<string, unknown>;
}
```

**What it does**: Tiles coordinate through the spreadsheet itself. No central controller.

**Where it lives**: `src/spreadsheet/tiles/stigmergy.ts` (EXISTS)

---

## System Design

### Execution Flow

```
1. USER enters formula in cell A1
   =TILE_CHAIN("sentiment", A2:A100)

2. SPREADSHEET LAYER detects change
   └─▶ Cell watcher fires

3. TILE ENGINE receives input
   └─▶ Looks up "sentiment" in Registry
   └─▶ Loads tile chain definition
   └─▶ Validates input schema

4. EXECUTION begins
   └─▶ For each tile in chain:
       ├─▶ Check L1 memory for cached result
       ├─▶ Execute tile.discriminate()
       ├─▶ Calculate tile.confidence()
       ├─▶ Update ConfidenceCascade
       └─▶ Store result in L1 memory

5. CONFIDENCE CASCADE evaluates
   └─▶ If RED: Stop, return error
   └─▶ If YELLOW: Continue, flag for review
   └─▶ If GREEN: Continue normally

6. STIGMERGY coordination
   └─▶ Deposit RESULT pheromone in cell
   └─▶ Other tiles can sense and react

7. RESULT returned to spreadsheet
   └─▶ Cell displays output
   └─▶ Zone indicator shows confidence
   └─▶ Click for full trace
```

### Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                      DATA FLOW                               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  USER INPUT ──▶ SPREADSHEET ──▶ TILE ENGINE                 │
│                                     │                        │
│                                     ▼                        │
│                              ┌──────────────┐               │
│                              │ TILE CHAIN   │               │
│                              │              │               │
│                              │ ┌──────────┐ │               │
│                              │ │ Tile A   │─┼──▶ L1 Cache  │
│                              │ └────┬─────┘ │               │
│                              │      │       │               │
│                              │      ▼       │               │
│                              │ ┌──────────┐ │               │
│                              │ │ Tile B   │─┼──▶ Confidence │
│                              │ └────┬─────┘ │    Cascade   │
│                              │      │       │               │
│                              │      ▼       │               │
│                              │ ┌──────────┐ │               │
│                              │ │ Tile C   │─┼──▶ Stigmergy │
│                              │ └──────────┘ │               │
│                              └──────┬───────┘               │
│                                     │                        │
│                                     ▼                        │
│  USER OUTPUT ◀── SPREADSHEET ◀── RESULT                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Build Order (What to Build First)

### Phase 1: Core (Weeks 1-2)

**Build these files:**

1. `src/spreadsheet/tiles/core/Tile.ts`
   - Base Tile interface
   - Tile composition (sequential, parallel)
   - Validation

2. `src/spreadsheet/tiles/core/TileChain.ts`
   - Chain construction
   - Execution engine
   - Result aggregation

3. `src/spreadsheet/tiles/core/Registry.ts`
   - Tile registration
   - Tile lookup
   - Dependency resolution

**Success criteria:**
```typescript
// This works:
const sentiment = new TileChain<string, Sentiment>()
  .add(new TokenizeTile())
  .add(new AnalyzeTile())
  .add(new NormalizeTile());

const result = await sentiment.execute("I love this product!");
// result.confidence = 0.92
// result.zone = 'GREEN'
```

### Phase 2: Infrastructure (Weeks 3-4)

**Already exists (verify/extend):**

1. `src/spreadsheet/tiles/confidence-cascade.ts` ✓
2. `src/spreadsheet/tiles/tile-memory.ts` ✓
3. `src/spreadsheet/tiles/stigmergy.ts` ✓
4. `src/spreadsheet/tiles/composition-validator.ts` ✓

**Build these:**

5. `src/spreadsheet/tiles/tracing/tile-tracer.ts` ✓ (BUILT)
6. `src/spreadsheet/tiles/registry/tile-registry.ts` ✓ (BUILT)
7. `src/spreadsheet/tiles/monitoring/zone-monitor.ts` ✓ (BUILT)

**Success criteria:**
- All 7 core files have 80%+ test coverage
- Integration tests pass
- Performance <10ms per tile

### Phase 3: Advanced (Weeks 5-8)

**Build these:**

1. `src/spreadsheet/tiles/advanced/CounterfactualTile.ts`
2. `src/spreadsheet/tiles/advanced/FederatedTile.ts`
3. `src/spreadsheet/tiles/advanced/CrossModalTile.ts`
4. `src/spreadsheet/tiles/advanced/StreamingTile.ts`

**Success criteria:**
- Each advanced tile has 3+ use case examples
- Performance benchmarks established
- Documentation complete

### Phase 4: Production (Weeks 9-12)

**Build these:**

1. `src/spreadsheet/backend/TileWorker.ts` (distributed execution)
2. `src/spreadsheet/backend/TileCache.ts` (KV-cache sharing)
3. `src/spreadsheet/backend/TileCompiler.ts` (optimization)
4. `src/benchmarking/benchmark-core.ts` ✓ (STARTED)

**Success criteria:**
- Benchmark validates 10x+ speedup
- Distributed tiles work across 3+ nodes
- Production deployment guide complete

---

## What We're NOT Building (Yet)

### Deferred to Phase 2+

1. **TCL (Tile Composition Language)**
   - DSL is powerful but not MVP
   - Use TypeScript composition for now
   - Build TCL after core is stable

2. **Meta-tiles**
   - Power user feature
   - Requires stable core first
   - Build after Phase 4

3. **Tile Compilation**
   - Performance optimization
   - Only needed at scale
   - Build after benchmarks prove need

4. **Quantum Tiles**
   - Research complete, implementation future
   - Requires quantum hardware access
   - Build when NISQ algorithms mature

5. **Tile Marketplace**
   - Ecosystem feature
   - Requires critical mass of tiles
   - Build after community forms

---

## API Design Principles

### 1. Progressive Disclosure

```typescript
// Level 1: Simple (for users)
const result = await analyze("text");

// Level 2: Configured (for power users)
const result = await analyze("text", { confidence: 0.9 });

// Level 3: Expert (for developers)
const chain = new TileChain()
  .add(tokenize, { cache: true })
  .add(analyze, { model: "gpt-4" })
  .add(normalize);
const result = await chain.execute("text");
```

### 2. Fail Loudly

```typescript
// Bad: Silent fallback
const result = tile.execute(input) || defaultResult;

// Good: Explicit handling
try {
  const result = await tile.execute(input);
  if (result.zone === 'RED') {
    throw new LowConfidenceError(result.confidence);
  }
} catch (e) {
  logger.error('Tile failed', { tile: tile.id, error: e });
  throw e;
}
```

### 3. Observable by Default

```typescript
// Every tile execution produces trace
const result = await tile.execute(input);
console.log(result.trace);
// "TokenizeTile(0.98) → AnalyzeTile(0.92) → NormalizeTile(0.95)"
// "Composite confidence: 0.86 (GREEN)"
```

### 4. Type-Safe Composition

```typescript
// Compile-time error if types don't match
const chain = new TileChain<string, number>()
  .add(new TokenizeTile()) // string → string[]
  .add(new AnalyzeTile())  // string[] → Score  ✓ types match
  .add(new NormalizeTile()); // Score → NormalizedScore ✓

// This would fail at compile time:
// .add(new ImageTile()) // Error: string[] != Image
```

---

## Testing Strategy

### Unit Tests (Every Tile)

```typescript
describe('SentimentTile', () => {
  it('returns confidence between 0 and 1', async () => {
    const tile = new SentimentTile();
    const confidence = await tile.confidence('test input');
    expect(confidence).toBeGreaterThanOrEqual(0);
    expect(confidence).toBeLessThanOrEqual(1);
  });

  it('produces trace explaining decision', async () => {
    const tile = new SentimentTile();
    const trace = await tile.trace('I love this!');
    expect(trace).toContain('positive');
  });

  it('composes with other tiles', () => {
    const tile = new SentimentTile();
    const chain = tile.compose(new NormalizeTile());
    expect(chain).toBeInstanceOf(TileChain);
  });
});
```

### Integration Tests (Chains)

```typescript
describe('Sentiment Pipeline', () => {
  it('produces GREEN zone for clear inputs', async () => {
    const chain = createSentimentPipeline();
    const result = await chain.execute('This product is amazing!');
    expect(result.zone).toBe('GREEN');
  });

  it('produces YELLOW zone for ambiguous inputs', async () => {
    const chain = createSentimentPipeline();
    const result = await chain.execute('It is what it is.');
    expect(result.zone).toBe('YELLOW');
  });

  it('propagates confidence correctly', async () => {
    const chain = createSentimentPipeline();
    const result = await chain.execute('test');
    // Sequential: 0.95 * 0.90 * 0.85 = 0.726
    expect(result.confidence).toBeCloseTo(0.726, 2);
  });
});
```

### Performance Tests (Benchmarks)

```typescript
describe('Performance', () => {
  it('executes simple tile in <10ms', async () => {
    const tile = new SimpleTile();
    const start = performance.now();
    await tile.execute('test');
    const duration = performance.now() - start;
    expect(duration).toBeLessThan(10);
  });

  it('scales linearly with parallel tiles', async () => {
    const tiles = Array(10).fill(null).map(() => new SimpleTile());
    const parallel = Tile.parallel(...tiles);

    const start = performance.now();
    await parallel.execute('test');
    const duration = performance.now() - start;

    // Parallel should be ~same as single, not 10x
    expect(duration).toBeLessThan(50);
  });
});
```

---

## Success Metrics

### Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Single tile latency | <10ms | p50, p95, p99 |
| Chain latency (5 tiles) | <50ms | p50, p95, p99 |
| Memory per tile | <1MB | Peak allocation |
| Test coverage | >80% | Lines covered |
| Type safety | 100% | No `any` types |

### Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Confidence accuracy | >0.9 | Calibration error |
| Zone accuracy | >0.95 | Manual review |
| Trace usefulness | >4/5 | User survey |

---

## File Structure (Target)

```
src/spreadsheet/
├── core/
│   ├── Tile.ts              # Base interface
│   ├── TileChain.ts         # Composition
│   ├── Registry.ts          # Discovery
│   └── Types.ts             # Shared types
│
├── tiles/
│   ├── confidence-cascade.ts   # ✓ EXISTS
│   ├── stigmergy.ts            # ✓ EXISTS
│   ├── tile-memory.ts          # ✓ EXISTS
│   ├── composition-validator.ts # ✓ EXISTS
│   ├── counterfactual.ts       # ✓ EXISTS
│   ├── federated-tile.ts       # ✓ EXISTS
│   ├── cross-modal.ts          # ✓ EXISTS
│   │
│   ├── registry/               # ✓ BUILT
│   │   ├── tile-registry.ts
│   │   └── dependency-validator.ts
│   │
│   ├── tracing/                # ✓ BUILT
│   │   └── tile-tracer.ts
│   │
│   ├── monitoring/             # ✓ BUILT
│   │   └── zone-monitor.ts
│   │
│   └── examples/               # TODO
│       ├── SentimentTile.ts
│       ├── FraudDetectionTile.ts
│       └── AnomalyDetectionTile.ts
│
├── backend/
│   ├── TileWorker.ts           # TODO: Distributed
│   ├── TileCache.ts            # TODO: KV-cache
│   └── TileCompiler.ts         # TODO: Optimization
│
└── benchmarking/
    ├── stats.ts                # ✓ BUILT
    ├── benchmark-core.ts       # TODO: Complete
    └── baseline-comparison.ts  # TODO
```

---

## Next Actions

### Immediate (This Week)

1. **Create `src/spreadsheet/tiles/core/Tile.ts`**
   - Define base interface
   - Implement composition
   - Add validation

2. **Create `src/spreadsheet/tiles/core/TileChain.ts`**
   - Chain construction
   - Execution engine
   - Result type

3. **Create `src/spreadsheet/tiles/examples/SentimentTile.ts`**
   - Working example tile
   - Demonstrates all interfaces
   - Used for testing

### Short-term (Next 2 Weeks)

4. **Complete benchmark-core.ts**
   - Finish benchmark infrastructure
   - Run first performance tests
   - Validate methodology

5. **Integration tests**
   - Test all existing tiles together
   - Validate confidence flow
   - Test stigmergic coordination

6. **Documentation**
   - API reference for core interfaces
   - Getting started guide
   - Example gallery

---

## Summary

**We have:**
- 7 PoC implementations (confidence, stigmergy, memory, counterfactual, federated, cross-modal, composition)
- 4 infrastructure systems (tracer, registry, zone monitor, stats)
- Comprehensive research on 15+ breakthrough domains

**We need:**
- Core interfaces (Tile, TileChain, Registry)
- Integration tests
- Example tiles
- Benchmark validation

**The path:**
1. Build core (2 weeks)
2. Integrate existing (2 weeks)
3. Build advanced (4 weeks)
4. Production harden (4 weeks)

**Total: 12 weeks to production-ready SMP**

---

*Implementation Blueprint v1.0 | 2026-03-10*
*Next Review: After Phase 1 complete*
