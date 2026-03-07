# Coordination

Multi-agent coordination patterns for distributed decision making.

## Patterns

| Pattern | Purpose | Use Case |
|---------|---------|----------|
| **Consensus** | Agreement on decisions | Voting on actions |
| **Stigmergy** | Indirect coordination | Pheromone trails |
| **Auction** | Task allocation | Bidding for work |
| **Market** | Resource pricing | Token economies |

## Key Concepts

### Stigmergy (Pheromone Trails)

Agents leave signals in a shared space that influence others:

```
Agent A executes task
    │
    ▼
Leave "scent trail" in shared state
    │
    ▼
Agent B detects scent
    │
    ▼
Agent B follows trail (or branches)
```

### Consensus Protocol

Distributed agreement without central authority:

```
1. PROPOSE: Agent proposes action
2. VOTE: Other agents vote yes/no
3. DECIDE: Action proceeds if threshold met
4. EXECUTE: All agents commit to decision
```

### Auction-Based Allocation

Task assignment through competitive bidding:

```
Task appears
    │
    ├── Agent A bids 0.8 (confidence)
    ├── Agent B bids 0.6 (confidence)
    └── Agent C bids 0.9 (confidence) ← Winner
```

---

*Part of POLLN - Pattern-Organizing Large Language Network*
