# TypeScript Fix Plan - Detailed Error Resolution

**Generated:** 2026-03-10
**Total Errors:** 82 (down from 200+)
**Strategy:** Fix by error type, not by file
**Team Coordination:** TypeScript Fixer agent - coordinate via `/agent-messages/`

---

## PROGRESS RECEIPT — 2026-10-04 lane (batches 1-11)

**5,900 -> 2,372 total errors (-3,528, -60%). All commits on main, never a redder intermediate state.**

| Batch | Category | Before | After | Commit |
|-------|----------|--------|-------|--------|
| 1 | Missing types: @types/react-dom | 5900 | 5899 | 5fd2168 |
| 2 | UI cascade root cause: tsconfig jsx + DOM lib (killed TS17004 x1771, TS2812/2584 x418 + cascades) | 5899 | 3027 | 6a641e0 |
| 3 | Backup module (enum values, Buffer variance, index signatures) | 3027 | 3015 | eababbb |
| 4 | API module | 3015 | 3015 | (already 0 — skipped) |
| 5 | CLI module (static-vs-instance, real vendor types exposed 2 API-name bugs) | 3015 | 2981 | 02b69ae |
| 6 | Benchmarks module — API-drift repair, shared result adapter, suites rewritten against real Colony/Meadow/TileDreamer APIs | 2981 | 2829 | 2210d08 |
| 7 | Vendor declarations for thin optional integrations (Category 1A) | 2829 | 2796 | 6fd4abf |
| 8 | TS1361 import-type-as-value, all 131 | 2796 | 2665 | 11b1220 |
| 9 | TS2693 type-used-as-value, all 83 (dead default-export type registries excised) | 2665 | 2590 | 390bf7b |
| 10 | TS2300 duplicate identifiers, all 59 | 2590 | 2498 | 2903909 |
| 11 | TS2304 cannot-find-name, 140/255 (SuperInstance imports, smpbot I/O generics, barrel re-export bindings) | 2498 | 2372 | 5018328 |

### Dominant debt patterns (what the 5,900 actually was)
1. **One tsconfig root cause** (~48% of the debt): no `jsx` flag + no DOM lib — every .tsx and every DOM API errored. Single config fix killed 2,872.
2. **Imagined APIs**: benchmarks + CLI written against APIs that never existed (spawnAgent, generateDream, OutputFormatter instances, renderTable). tsc had silenced them via unresolved imports/any.
3. **Barrel re-export without binding** (`export {X} from` then local use of X) — InstanceType, SuperInstanceValidator, CODING_TASKS.
4. **import type on runtime enums** (TS1361) — the repo's prevailing 'import type' style applied to enums switched on at runtime.
5. **Undeclared generics** — smpbot I/O type params used in non-generic interfaces.

### What NOT to do (measured)
- Don't install types for pg/socket.io/prom-client/@elastic yet, don't declare them, and don't install @types/d3/chart.js yet: consumers are drifted enough that ANY resolution net-increases errors (measured +27..+38). Fix consumers first (see vendor-modules.d.ts header).

### Remaining 2,372 — suggested next batches
- TS2339 (~380) + TS2322/TS2345/TS2353 (~700): spreadsheet ui/admin, visualizations, backend — per-module design work.
- TS7006 (~250): implicit-any annotations, spread thin.
- TS18046/TS18004 (~130): unknown-type tightening + shorthand-property bugs.
- Remaining TS2304 (115): 1-3-per-file long tail.
- TS2307 (122): missing RELATIVE modules (LogCell, io/Logger, SecretScanner...) — files that don't exist or moved; per-module archaeology.
- 5 pre-existing jest failures in benchmarks suites (logic/test drift, was invisible behind compile failure).

---

**Original plan below (kept for history):**

## Error Categories & Fix Patterns

### Category 1: Module Resolution Errors (~40%)
**Pattern:** `Cannot find module 'X' or its corresponding type declarations`

**Files Affected:**
- src/backup/schedulers.ts - `node-cron`
- src/api/revocation.ts - `redis`
- Various UI files - missing `.js` extensions

**Fix Pattern:**
```typescript
// Option A: Install missing types
npm install --save-dev @types/node-cron @types/redis

// Option B: Add type declaration
declare module 'node-cron' {
  interface ScheduledTask {
    start(): void;
    stop(): void;
    destroy(): void;
  }
  export function schedule(expression: string, func: () => void): ScheduledTask;
  export function validate(expression: string): boolean;
}

// Option C: Use any for quick fix
const cron = await import('node-cron') as any;
```

### Category 2: Implicit Any Errors (~25%)
**Pattern:** `Parameter 'X' implicitly has an 'any' type`

**Files Affected:**
- src/benchmarking/examples/benchmarkValidation.ts
- src/cli/commands/backup/*.ts
- Various UI components

**Fix Pattern:**
```typescript
// Before
.map((r, i) => ...)

// After
.map((r: ResultType, i: number) => ...)
```

### Category 3: Type Mismatches (~20%)
**Pattern:** `Type 'X' is not assignable to type 'Y'`

**Files Affected:**
- src/backup/strategies/*.ts - Buffer<ArrayBufferLike> vs Buffer<ArrayBuffer>
- src/backup/backup-manager.ts - BackupType enum issues

**Fix Pattern:**
```typescript
// Buffer type fix
import { Buffer } from 'buffer';
const buffer = Buffer.from(JSON.stringify(data));

// Enum fix - use enum value, not string literal
// Before
const type = "FULL";

// After
import { BackupType } from './types.js';
const type = BackupType.FULL;
```

### Category 4: Override Modifiers (~10%)
**Pattern:** `This member must have an 'override' modifier`

**Files Affected:**
- src/api/memory-protection.ts (already fixed)
- src/api/revocation.ts

**Fix Pattern:**
```typescript
// Before
async revokeRefreshToken(token: string): Promise<boolean>

// After
override async revokeRefreshToken(token: string): Promise<boolean>
```

### Category 5: Index Signature Errors (~5%)
**Pattern:** `Index signature for type 'string' is missing in type 'X'`

**Files Affected:**
- src/backup/strategies/full-backup.ts
- src/backup/strategies/snapshot-backup.ts

**Fix Pattern:**
```typescript
// Before
const config: Record<string, unknown> = colonyConfig;

// After
const config: Record<string, unknown> = { ...colonyConfig } as Record<string, unknown>;
```

---

## Fix Execution Order

### Batch 1: Install Missing Types (5 min)
```bash
npm install --save-dev @types/node-cron @types/redis
```

### Batch 2: Fix High-Error UI Files (30 min)
Priority order:
1. FeatureFlagPanel.tsx (436 errors) - Likely a cascade failure from one root issue
2. CellInspectorWithTheater.tsx (301 errors)
3. TouchCellInspector.tsx (253 errors)

**Strategy:** These files likely share a common import issue. Fix one, fix all.

### Batch 3: Fix Backup Module (15 min)
1. Fix BackupType enum imports
2. Fix Buffer type assertions
3. Add node-cron type declaration

### Batch 4: Fix API Module (10 min)
1. Add override modifiers
2. Fix AuditEvent types
3. Add redis type declaration

### Batch 5: Fix CLI Module (10 min)
1. Add type annotations
2. Fix config type access

### Batch 6: Fix Benchmarking (5 min)
1. Add .js extension to imports
2. Add parameter types

---

## Verification After Each Batch

```bash
# Count errors
npx tsc --noEmit 2>&1 | grep -c "error TS"

# Should decrease by ~15-20 errors per batch
```

---

## Common Pitfalls

1. **Don't fix imports with `.js` in UI files** - Use `.tsx` extension
2. **Don't change Buffer types globally** - Only fix where needed
3. **Enum imports must be value imports** - Use `import { X }` not `import type { X }`
4. **React component props** - Check parent component for correct types

---

## Expected Timeline

| Batch | Files | Est. Errors Fixed | Time |
|-------|-------|-------------------|------|
| 1 | Types install | 5-10 | 5 min |
| 2 | UI Components | 40-50 | 30 min |
| 3 | Backup Module | 15-20 | 15 min |
| 4 | API Module | 8-12 | 10 min |
| 5 | CLI Module | 5-8 | 10 min |
| 6 | Benchmarking | 3-5 | 5 min |
| **Total** | **~30 files** | **~82 errors** | **~75 min** |

---

*Generated: 2026-03-10*
