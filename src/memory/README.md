# Memory

Persistence, retrieval, and indexing systems for POLLN.

## Components

| Component | Purpose |
|-----------|---------|
| **Embeddings** | Vector storage for pollen grains |
| **Index** | Fast similarity search |
| **Cache** | Hot data in memory |
| **Archive** | Long-term storage |

## Memory Model

POLLN's memory is **structural**, not representational:

```
Traditional Memory:
┌─────────────────┐
│  File Storage   │
│  facts.db       │
│  Retrieval: O(n)│
└─────────────────┘

POLLN Memory:
┌─────────────────────────┐
│  Synaptic Weights       │
│  Pathway Strengths      │
│  Retrieval: O(log n)    │
│  Learns via Hebbian     │
└─────────────────────────┘
```

## Storage Hierarchy

```
1. HOT (RAM)
   └── Active agents, recent patterns

2. WARM (SSD/Cache)
   └── Compressed embeddings, frequent access

3. COLD (Disk/Archive)
   └── Historical data, fossils
```

## Retrieval Patterns

```typescript
// Semantic search
const similar = await memory.findSimilar(embedding, { k: 5 });

// Temporal search
const recent = await memory.findSince(timestamp);

// Pattern search
const matches = await memory.findPattern(behaviorSignature);
```

---

*Part of POLLN - Pattern-Organizing Large Language Network*
