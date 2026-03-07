# Source Directory

Application source code for POLLN.

## Structure

```
src/
├── core/           # Core runtime (agents, learning, safety)
├── agents/         # Specialized agent implementations
├── coordination/   # Multi-agent coordination patterns
├── memory/         # Persistence and memory systems
├── safety/         # Safety infrastructure
└── utils/          # Shared utilities
```

## Core vs. Application

| Layer | Purpose | Examples |
|-------|---------|----------|
| **Core** | Runtime infrastructure | Agent classes, protocols, learning |
| **Agents** | Specialized implementations | Specific task/role agents |
| **Coordination** | Multi-agent patterns | Voting, consensus, stigmergy |
| **Memory** | Persistence | Storage, retrieval, indexing |
| **Safety** | Guardrails | Constraints, monitoring, recovery |
| **Utils** | Helpers | Logging, validation, formatting |

## Import Paths

```typescript
// Core components
import { Colony, TaskAgent, HebbianLearning } from './core';

// Specialized agents
import { ResearchAgent, CodeAgent } from './agents';

// Coordination patterns
import { ConsensusProtocol, Stigmergy } from './coordination';

// Safety
import { ConstitutionalAI, SafetyMonitor } from './safety';
```

---

*Part of POLLN - Pattern-Organizing Large Language Network*
