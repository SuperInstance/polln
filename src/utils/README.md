# Utilities

Shared utility functions for POLLN.

## Modules

| Module | Purpose |
|--------|---------|
| `logging.ts` | Structured logging with levels |
| `validation.ts` | Input validation helpers |
| `formatting.ts` | Data formatting utilities |
| `async.ts` | Async helpers (retry, timeout) |
| `crypto.ts` | Hashing, encryption utilities |

## Usage

```typescript
import { logger } from './utils/logging';
import { validate } from './utils/validation';
import { formatDuration } from './utils/formatting';
import { withRetry } from './utils/async';
import { hash } from './utils/crypto';

// Structured logging
logger.info('Agent started', { agentId: 'agent-1', type: 'task' });

// Validation
const result = validate(input, schema);

// Retry with backoff
const data = await withRetry(fetchData, { maxAttempts: 3, backoff: 'exponential' });
```

## Logging Levels

| Level | When |
|-------|------|
| `DEBUG` | Development, detailed traces |
| `INFO` | Normal operations |
| `WARN` | Unexpected but recoverable |
| `ERROR` | Failures, exceptions |
| `CRITICAL` | System-level failures |

---

*Part of POLLN - Pattern-Organizing Large Language Network*
