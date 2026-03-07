# Core Runtime

The foundational layer of POLLN - implements the agent runtime, communication, learning, and safety systems.

## Components

### Agent System
| File | Purpose |
|------|---------|
| `types.ts` | Core type definitions for the entire system |
| `agent.ts` | BaseAgent abstract class |
| `agents.ts` | Concrete agents: TaskAgent, RoleAgent, CoreAgent |
| `colony.ts` | Colony management and agent coordination |

### Communication
| File | Purpose |
|------|---------|
| `communication.ts` | A2A package system for agent-to-agent messaging |
| `protocol.ts` | SPORE protocol for agent lifecycle |

### Decision Making
| File | Purpose |
|------|---------|
| `decision.ts` | Plinko decision layer with Gumbel-Softmax |
| `protocol.ts` | SPORE protocol implementation |

### Learning
| File | Purpose |
|------|---------|
| `learning.ts` | Hebbian learning with Oja's rule normalization |
| `worldmodel.ts` | VAE-based world model for dreaming/simulation |
| `embedding.ts` | BES (Behavioral Embedding Space) with differential privacy |

### Safety
| File | Purpose |
|------|---------|
| `safety.ts` | Constitutional constraints and safety layer |

### Lifecycle
| File | Purpose |
|------|---------|
| `succession.ts` | Knowledge succession protocol for agent handoff |
| `tile.ts` | Tile abstraction for reusable routines |

## Key Types

```typescript
// Tile Categories (lifespans)
enum TileCategory {
  EPHEMERAL = 'EPHEMERAL',  // Task-bound (minutes-hours)
  ROLE = 'ROLE',            // Performance-bound (days-weeks)
  CORE = 'CORE',            // Long-lived (months-years)
}

// Knowledge Stages (maturity)
enum KnowledgeStage {
  EPHEMERAL = 'EPHEMERAL',  // < 100 executions
  WORKING = 'WORKING',      // 100-1000 executions
  EMBEDDED = 'EMBEDDED',    // > 1000 executions
  FOSSIL = 'FOSSIL',        // Archived
}

// Privacy Levels
enum PrivacyLevel {
  PUBLIC = 'PUBLIC',
  COLONY = 'COLONY',
  PRIVATE = 'PRIVATE'
}

// Subsumption Layers
enum SubsumptionLayer {
  SAFETY = 'SAFETY',       // Layer 0: Instant override
  REFLEX = 'REFLEX',       // Layer 1: Fast reactions
  HABITUAL = 'HABITUAL',   // Layer 2: Learned routines
  DELIBERATE = 'DELIBERATE' // Layer 3: Slow planning
}
```

## Agent Hierarchy

```
BaseAgent (abstract)
    │
    ├── TaskAgent (EPHEMERAL)
    │   └── Born → Execute → Die (no succession)
    │
    ├── RoleAgent (ROLE)
    │   └── Learn → Execute → Transfer → Die
    │
    └── CoreAgent (CORE)
        └── Slow wisdom → Backup → Rarely replaced
```

## Knowledge Flow

```
Agent Death
    │
    ▼
extractKnowledge() ──▶ KnowledgePacket
    │                       │
    │                       ├── patterns: Map<string, PatternData>
    │                       ├── valueFunction: number
    │                       └── stage: KnowledgeStage
    │
    ▼
transferKnowledge() ──▶ Successor Agent
    │
    ▼
SuccessionEvent (recorded)
```

## Tests

All core components have comprehensive tests in `__tests__/`:

```bash
npm test                    # Run all tests
npm test -- --coverage      # With coverage
```

## Exports

Main exports are available via `index.ts`:

```typescript
import {
  // Agents
  BaseAgent, TaskAgent, RoleAgent, CoreAgent, TileCategory,

  // Communication
  A2APackageSystem,

  // Learning
  HebbianLearning, BES,

  // Decision
  PlinkoLayer,

  // Safety
  SafetyLayer,

  // Lifecycle
  KnowledgeSuccessionManager, KnowledgeStage,

  // Colony
  Colony
} from './core';
```

---

*Part of POLLN - Pattern-Organizing Large Language Network*
