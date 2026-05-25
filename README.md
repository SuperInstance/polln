# polln

**Pattern-Organized Large Language Network** — a tile-based AI system that transforms AI agents into visible, inspectable, improvable components composed like LEGO blocks, with mathematical confidence propagation and a spreadsheet interface for domain experts.

## What It Does

POLLN decomposes AI into **tiles** — self-contained units of behavior with formal confidence scores, traceability, and category-theory composition rules. Each tile observes, learns, and adapts. Tiles compose into pipelines with mathematically guaranteed confidence flow. The system includes a full spreadsheet UI for non-programmers to interact with tile intelligence.

### Core Innovation: The Three-Zone Confidence Model

| Zone | Confidence | Action |
|------|-----------|--------|
| GREEN | ≥ 0.90 | Auto-proceed |
| YELLOW | 0.75–0.89 | Human review |
| RED | < 0.75 | Stop and diagnose |

### Tiles

A tile is a typed, composable unit: `Tile = (I, O, f, c, τ)` where `f` is the discriminate function, `c` is confidence (0–1), and `τ` is the trace/explanation. Tile categories mirror biological lifespans:

- **EPHEMERAL** — Task-bound (minutes), no succession
- **ROLE** — Performance-bound (days), knowledge handoff
- **CORE** — Long-lived (months), infrastructure

Built-in tile types: `TransformerTile`, `RouterTile`, `AccumulatorTile`, `ValidatorTile`.

## Architecture

```
UI Layer (React)  ↔  Core Tile System  ↔  Backend Services (Express/Fastify)
     ↓                    ↓                       ↓
  Cells/Sheets      Tile Registry           Distributed Workers
  (LogCell,         (Discovery)             (Colony-based execution)
   ExplainCell)
                    ┌─────────────────────────┐
                    │   Confidence System      │
                    │   (Three-Zone Model)     │
                    └─────────────────────────┘
```

### Key Subsystems

| Subsystem | Path | Description |
|-----------|------|-------------|
| **Core Tiles** | `src/core/tiles/` | Transformer, Router, Accumulator, Validator tiles |
| **Tile System** | `src/core/tile.ts` | BaseTile with observation, adaptation, serialization |
| **Colony Manager** | `src/core/colony-manager/` | Multi-colony orchestration |
| **Hydraulic System** | `src/core/hydraulic/` | Flow-based resource management (pumps, valves, pressure) |
| **Guardian Agent** | `src/core/guardian/` | Safety constraints and learning |
| **LoRA Adapters** | `src/core/lora/` | Trainable LLM adapters for domain specialization |
| **KV Cache** | `src/core/kv/` | Key-value caching for inference optimization |
| **World Model** | `src/core/worldmodel.ts` | Internal model of the environment |
| **Spreadsheet** | `src/spreadsheet/` | Full spreadsheet engine (formula, charts, collaboration, GPU acceleration) |
| **GPU Engine** | `src/gpu/` | WebGL/WebGPU tensor operations |
| **Monitoring** | `src/monitoring/` | OpenTelemetry metrics, tracing, alerts, health checks |
| **Scaling** | `src/scaling/` | Auto-scaling with prediction |
| **CLI** | `src/cli/` | Colony management, LoRA training, monitoring commands |
| **API** | `src/api/` | REST/WebSocket server |
| **SDK** | `src/sdk/` | Client SDK |
| **Simulations** | `simulations/` | Hydraulic, deployment, dreaming (model-based RL), coding, reasoning |

## Installation

```bash
npm install
npm run build
```

Requires Node.js ≥ 18.

## Quick Start

### CLI

```bash
# Colony management
npx polln colonies list
npx polln colonies create --name my-colony
npx polln colonies status

# LoRA adapters
npx polln lora list
npx polln lora train --dataset data.jsonl

# Monitoring
npx polln monitor metrics
npx polln monitor health

# Scaling
npx polln scale status
npx polln scale predict
```

### Programmatic

```typescript
import { Tile, TileCategory } from 'polln/core';

// Create and execute a tile
const result = await myTile.execute(input, {
  colonyId: 'colony-1',
  keeperId: 'keeper-1',
  timestamp: Date.now(),
  causalChainId: 'chain-1',
  energyBudget: 100,
});

console.log(result.confidence); // 0.0 – 1.0
console.log(result.trace);      // Explanation
```

### Spreadsheet Collaboration

```typescript
import { createSpreadsheet } from 'polln/spreadsheet';

const sheet = createSpreadsheet({ collaborative: true });
// WebSocket-based real-time collaboration via Yjs
```

## Testing

```bash
npm test                    # Unit tests (Jest)
npm run test:integration    # Integration tests
npm run test:coverage       # Coverage report
npm run bench:all           # Benchmark suites
```

## Deployment

Docker and Kubernetes configs included:

```bash
docker-compose up                    # Development
docker-compose -f docker-compose.prod.yml up  # Production

# Kubernetes
kubectl apply -f k8s/
```

Terraform configs for cloud deployment in `terraform/` and `deployment/terraform/`.

## Monitoring

Built-in OpenTelemetry integration: Prometheus metrics export, OTLP-gRPC tracing, structured logging (Pino), health checks, and alert dashboards.

## Related Repos

- **[flux-check-py](https://github.com/SuperInstance/flux-check-py)** — Python constraint checking CLI
- **[flux-fracture-c](https://github.com/SuperInstance/flux-fracture-c)** — C99 fracture-coalesce library
- **[constraint-theory-rust-python](https://github.com/SuperInstance/constraint-theory-rust-python)** — Rust constraint engine with Python bindings
- **[constraint-theory-engine-cpp-lua](https://github.com/SuperInstance/constraint-theory-engine-cpp-lua)** — C++ engine with LuaJIT, CDCL, AVX-512

## License

MIT
