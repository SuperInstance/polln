# Tile-Based Agentic Systems Research

**Date:** 2026-03-06
**Vision:** ScratchJr blocks that LEARN and ADAPT

---

## The Core Metaphor

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   SCRATCHJR                    POLLN                            │
│   ─────────                    ─────                            │
│   Static blocks                Living tiles                     │
│   Manual connections           Self-organizing                  │
│   Fixed behavior               Adapts through observation       │
│   No memory                    Remembers outcomes               │
│   Single user                  Shareable (pollen grains)        │
│                                                                 │
│   ┌─────┐                      ┌─────┐                         │
│   │move │ → fixed              │move │ → adapts based on        │
│   │ 10  │                      │  *  │   context & history     │
│   └─────┘                      └─────┘                         │
│                                                                 │
│   Pollen Grain = A trained tile ready to share                  │
│   Meadow = Marketplace of trained tiles                         │
│   Keeper = User cultivating their tile garden                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tile Architecture

### Tile Definition

```typescript
/**
 * A Tile is a self-contained, trainable, shareable unit of behavior.
 * Like a ScratchJr block, but alive - it observes, learns, and adapts.
 */
interface Tile<TInput = unknown, TOutput = unknown> {
  // Identity
  id: string;
  name: string;
  category: TileCategory;

  // Core function (the "block" behavior)
  execute: (input: TInput, context: TileContext) => Promise<TOutput>;

  // Learning capabilities
  observe: (outcome: TileOutcome) => void;  // Watch what happened
  adapt: () => void;                         // Modify based on observations

  // Serialization (for sharing)
  serialize: () => PollenGrain;              // Export as pollen
  deserialize: (grain: PollenGrain) => void; // Import pollen

  // Composition
  inputs: TilePort[];
  outputs: TilePort[];

  // State
  memory: TileMemory;
  trainingData: Observation[];
}

type TileCategory =
  | 'perception'   // Sense the world
  | 'decision'     // Make choices
  | 'action'       // Do things
  | 'memory'       // Remember/forget
  | 'communication' // Talk to other tiles
  | 'learning'     // Improve behavior
  | 'safety'       // Prevent harm
  | 'meta';        // Reason about tiles

interface TilePort {
  name: string;
  type: string;
  required: boolean;
  description: string;
}

interface TileMemory {
  shortTerm: Map<string, unknown>;   // Current execution
  longTerm: Map<string, unknown>;    // Learned patterns
  episodic: Episode[];               // History of experiences
}

interface Observation {
  timestamp: number;
  input: unknown;
  output: unknown;
  context: TileContext;
  reward: number;  // How good was this outcome?
  tags: string[];
}
```

### Pollen Grain = Trained Tile

```typescript
/**
 * A Pollen Grain is a serialized, trained tile ready for sharing.
 * It contains the tile's learned behavior, not its implementation.
 */
interface PollenGrainV2 {
  id: string;
  tileId: string;
  tileName: string;
  category: TileCategory;

  // Compressed learned behavior
  embedding: number[];           // Behavioral fingerprint
  weights: SerializedWeights;    // Learned parameters

  // Training provenance
  trainingEpisodes: number;
  successRate: number;
  avgReward: number;

  // Transfer metadata
  sourceKeeper: string;
  createdAt: number;
  signature: string;  // Cryptographic proof of origin

  // Compatibility
  inputSchema: JSONSchema;
  outputSchema: JSONSchema;
  dependencies: string[];
}
```

---

## Tile Composition (Snapping Together)

### Sequential Composition

```typescript
// Tiles snap together like ScratchJr blocks
const pipeline = tileA.pipe(tileB).pipe(tileC);

// But they're ALIVE - they observe the whole chain
const result = await pipeline.execute(input);
// tileA observes tileB's output
// tileB observes tileC's output
// All tiles learn from final outcome
```

### Parallel Composition

```typescript
// Multiple tiles work together
const parallel = Tile.parallel([tileA, tileB, tileC]);
const results = await parallel.execute(input);

// Each tile observes others' outputs
// They can specialize (division of labor)
```

### Conditional Composition

```typescript
// Plinko-style stochastic selection
const branch = Tile.branch({
  conditions: [
    { when: isSafe, then: tileA },
    { when: isUrgent, then: tileB },
    { default: tileC }
  ],
  temperature: 0.7  // Some randomness
});

// The branch tile learns which path works best
```

---

## Tile Learning Mechanisms

### 1. Observation-Based Learning

```typescript
class ObservableTile implements Tile {
  async execute(input, context) {
    const output = await this.coreBehavior(input, context);

    // Observe our own execution
    this.observe({
      input,
      output,
      context,
      reward: context.lastReward,
      timestamp: Date.now()
    });

    return output;
  }

  observe(outcome: Observation) {
    this.trainingData.push(outcome);

    // Periodically adapt
    if (this.trainingData.length % 100 === 0) {
      this.adapt();
    }
  }

  adapt() {
    // Learn from observations
    // - Which inputs lead to good outcomes?
    // - Which contexts need different behavior?
    // - Update internal weights
  }
}
```

### 2. Cross-Pollination (Tile-to-Tile Learning)

```typescript
class TileGarden {
  // Tiles learn from each other
  async crossPollinate() {
    const tiles = this.getAllTiles();

    // Find tiles with similar input patterns
    const pairs = this.findSimilarPairs(tiles);

    for (const [tileA, tileB] of pairs) {
      // Tile A learns from Tile B's successes
      tileA.borrowKnowledge(tileB.exportWisdom());

      // Tile B learns from Tile A's successes
      tileB.borrowKnowledge(tileA.exportWisdom());
    }
  }
}
```

### 3. Keeper-Guided Learning

```typescript
class Keeper {
  // Human guides tile training
  async trainTile(tile: Tile, examples: Example[]) {
    for (const example of examples) {
      const output = await tile.execute(example.input, this.context);

      // Keeper provides reward signal
      const reward = this.evaluate(output, example.expected);
      tile.observe({ ...example, output, reward });

      // Tile adapts to match keeper's preferences
      if (reward < 0.5) {
        tile.adapt();
      }
    }
  }
}
```

---

## Tile Marketplace (The Meadow)

```typescript
interface Meadow {
  // Browse available pollen grains
  browse(category?: TileCategory): Promise<PollenGrain[]>;

  // Search by behavior
  search(query: string): Promise<PollenGrain[]>;

  // Import a pollen grain
  plant(grain: PollenGrain): Promise<Tile>;

  // Export a trained tile
  harvest(tile: Tile): Promise<PollenGrain>;

  // Rate a pollen grain
  rate(grainId: string, rating: number, review: string): Promise<void>;
}
```

### Meadow Features

1. **Behavioral Search**: Find tiles by what they DO, not just name
2. **Compatibility Checking**: Verify tile fits your system
3. **Provenance Tracking**: Know where a tile came from
4. **Quality Ratings**: Community-driven quality signals
5. **Privacy Tiers**: Public, Colony-Private, Keeper-Private

---

## Implementation Roadmap

### Phase 1: Core Tile System
- [ ] Define Tile interface
- [ ] Implement ObservableTile base class
- [ ] Create basic tile categories
- [ ] Build tile composition primitives

### Phase 2: Learning & Adaptation
- [ ] Implement observation collection
- [ ] Add adaptation mechanisms
- [ ] Create cross-pollination system
- [ ] Build keeper training interface

### Phase 3: Pollen Sharing
- [ ] Design PollenGrain serialization
- [ ] Build Meadow marketplace
- [ ] Add privacy tiers
- [ ] Implement behavioral search

### Phase 4: Advanced Features
- [ ] Tile debugging/inspection
- [ ] Performance profiling
- [ ] Version control for tiles
- [ ] Tile testing framework

---

## Key Insights

1. **Tiles are alive** - They don't just execute, they observe and adapt
2. **Training = Value** - A trained tile is worth more than an untrained one
3. **Sharing = Multiplication** - One keeper's training benefits all
4. **Composition = Emergence** - Simple tiles combine into complex behaviors
5. **Observation = Learning** - Every execution is a training opportunity

---

## Next Steps

1. Design the minimal Tile interface
2. Build first observable tile prototype
3. Create tile composition playground
4. Design pollen grain format
5. Build meadow prototype

---

*"In ScratchJr, blocks are tools. In POLLN, tiles are companions that grow with you."*
