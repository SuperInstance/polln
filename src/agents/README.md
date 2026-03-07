# Specialized Agents

Domain-specific agent implementations that extend the core agent types.

## Structure

```
agents/
├── research.ts    # Research and investigation agents
├── code.ts        # Code generation and└── analysis.ts     # Data analysis
└── coordination.ts # Multi-task coordination
```

## Agent Types

| Type | Parent | Purpose |
|------|--------|---------|
| `ResearchAgent` | RoleAgent | Search, summarize, investigate |
| `CodeAgent` | RoleAgent | Generate, refactor, debug code |
| `AnalysisAgent` | RoleAgent | Process and analyze data |
| `CoordinatorAgent` | CoreAgent | Orchestrate multi-agent tasks |

## Usage

```typescript
import { ResearchAgent } from './agents/research';

const researcher = new ResearchAgent({
  id: 'research-1',
  typeId: 'research',
  categoryId: 'role',
  // ... config
});

await researcher.initialize();
const result = await researcher.process({ query: 'POLLN architecture' });
```

## Specialization Pattern

Agents inherit from core types based on their lifespan needs:

- **Task-bound** → TaskAgent (EPHEMERAL)
- **Role-bound** → RoleAgent (ROLE)
- **System-critical** → CoreAgent (CORE)

---

*Part of POLLN - Pattern-Organizing Large Language Network*
