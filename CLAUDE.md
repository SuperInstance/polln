# POLLN - Pattern-Organized Large Language Network

**Repo:** https://github.com/SuperInstance/polln | **v0.1.0**

---

## The Swarm That Learns

> "Bees are not that smart individually. But as a swarm, they become durable intelligence."

POLLN is a distributed intelligence system where simple agents become collectively intelligent through emergent behavior.

---

## Implementation Status

| Component | Status | Tests |
|-----------|--------|-------|
| Base Agent Runtime | COMPLETE | 18 |
| Tile Categories (Task/Role/Core) | COMPLETE | 24 |
| Knowledge Succession Protocol | COMPLETE | 14 |
| META Tiles (Pluripotent Agents) | COMPLETE | 22 |
| Value Network (TD(λ) Learning) | COMPLETE | 20 |
| Stigmergic Coordination | COMPLETE | 12 |
| Plinko Decision Layer | COMPLETE | 12 |
| **Total** | | **122** |

---

## Core Components (`src/core/`)

| File | Purpose |
|------|---------|
| `types.ts` | Core type definitions |
| `agent.ts` | BaseAgent class |
| `agents.ts` | TaskAgent, RoleAgent, CoreAgent |
| `protocol.ts` | SPORE protocol |
| `decision.ts` | Plinko decision layer |
| `learning.ts` | Hebbian learning |
| `colony.ts` | Agent colony management |
| `communication.ts` | A2A package system |
| `embedding.ts` | BES embeddings (Pollen Grains) |
| `safety.ts` | Safety layer |
| `worldmodel.ts` | VAE world model for dreaming |
| `meta.ts` | Pluripotent META tiles |
| `valuenetwork.ts` | TD(λ) value prediction |
| `succession.ts` | Knowledge transfer protocol |

---

## Coordination Components (`src/coordination/`)

| File | Purpose |
|------|---------|
| `stigmergy.ts` | Pheromone-based coordination |

---

## Key Concepts

| Term | Meaning |
|------|---------|
| **Pollen Grain** | Compressed behavioral seed |
| **Keeper** | User cultivating their hive |
| **Meadow** | Where patterns cross-pollinate |
| **Honeycomb Cell** | Reusable routine |
| **Plinko** | Stochastic selection layer |
| **A2A Package** | Agent-to-agent communication artifact |
| **META Tile** | Pluripotent agent that can differentiate |
| **Value Network** | TD(λ) predictions of state values |
| **Stigmergy** | Indirect coordination via environmental signals |

---

## Key Insights

- **Traceability**: A2A packages are artifacts - every step inspectable
- **Memory = Structure**: Body stores pathway activation probability
- **Durability Through Diversity**: Stochastic selection allows variants
- **Differentiation**: META tiles become specialized based on signals
- **Learning = Connection Adjustment**: Hebbian learning strengthens paths

---

## Reference Documents

| Doc | Purpose |
|-----|---------|
| `docs/ROADMAP.md` | Phased development plan |
| `docs/ARCHITECTURE.md` | System architecture |
| `docs/research/QUICK_REFERENCE.md` | Research synthesis |
| `docs/research/pluripotent-agents-research.md` | META tile math foundations |
| `docs/research/scouts/FINAL_INTEGRATION.md` | Complete spec |

---

## Operating Principles

1. **Parallel agents** - Spawn multiple research agents when independent
2. **Document-driven** - Every decision documented
3. **Test-first** - Validate each component
4. **Commit milestones** - Don't batch commits
5. **Compact context** - Summarize and clear often

---

## Commands

```bash
npm install && npm test
npm run build
npm run test:coverage
```

---

## Current Phase: 2+ Enhancement

**Active Work**: R&D waves exploring new components

### Recent Commits
1. `4a642bb` - Enhanced META tiles with mathematical foundations
2. `6952aae` - Add stigmergic coordination and value networks
3. `42ab09a` - POLLN breakthrough synthesis

### Next Research Areas
- World Model / VAE enhancement for dreaming
- Agent Graph Evolution (pruning, grafting)
- Federated Learning patterns
- Meadow/Community system
- Scent Trail / Loomcast
- Exchange/Marketplace

---

*Repository: https://github.com/SuperInstance/polln*
*Creator: Casey DiGennaro*
*Last Updated: 2026-03-06*
