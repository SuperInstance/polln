# Compaction Checklist

**⚠️ USE THIS WHEN CONTEXT REACHES 50% REMAINING**

---

## Pre-Compaction: Assessment

- [ ] **Context check**: How much context remains? (Current: ____%)
- [ ] **Active agents**: Which agents are running? (alpha: ___, beta: ___, gamma: ___)
- [ ] **Current milestone**: What phase are we in? (Phase ___)
- [ ] **Blocking issues**: Any unresolved problems? (___)

---

## Compaction Steps

### 1. Update Roadmaps (5 min)
- [ ] Open `docs/agents/alpha-roadmap.md`
- [ ] Mark completed tasks with [X]
- [ ] Update progress log with latest session notes
- [ ] Repeat for beta and gamma roadmaps

### 2. Consolidate Tests (5 min)
- [ ] Run `npm test` and capture results
- [ ] Document pass rate: ____ passing / ____ total
- [ ] Identify any failing tests: ___
- [ ] Note test coverage if available: ___%

### 3. Update Documentation (10 min)
- [ ] Update `CLAUDE.md` with new capabilities
- [ ] Update `docs/MICROBIOME_ORCHESTRATION.md` progress tracking
- [ ] Add any new file types to exports in `src/core/index.ts`
- [ ] Update `src/microbiome/index.ts` if needed

### 4. Create Summary (5 min)
- [ ] Write brief summary of completed work
- [ ] Note any architectural decisions made
- [ ] List any issues or concerns for next phase
- [ ] Save summary to `docs/archive/phase-X-summary.md`

### 5. Archive Old Docs (2 min)
- [ ] Move completed planning docs to `docs/archive/`
- [ ] Keep only active roadmaps in `docs/agents/`
- [ ] Update archive index if needed

### 6. Prepare Handoff (3 min)
- [ ] Note what's ready for next phase
- [ ] Identify dependencies between phases
- [ ] List any tech debt to address
- [ ] Create handoff notes for next session

---

## Post-Compaction Verification

- [ ] **Context gained**: Estimate context recovered (____%)
- [ ] **Roadmaps current**: All 3 roadmaps updated
- [ ] **Tests passing**: Full suite passes
- [ ] **Docs updated**: Main docs reflect current state
- [ ] **Ready for next**: Clear path forward documented

---

## Quick Reference: What to Archive

**Archive these when phase complete:**
- Phase planning documents
- Old onboarding drafts
- Temporary research notes
- Completed milestone checklists

**Keep these active:**
- Current agent roadmaps (`docs/agents/*-roadmap.md`)
- Agent onboarding docs (`docs/agents/*-onboarding.md`)
- Main orchestration doc (`docs/MICROBIOME_ORCHESTRATION.md`)
- Main architecture doc (`docs/MICROBIOME_ARCHITECTURE.md`)

---

## Compaction Template

When compacting, use this template for your summary:

```markdown
# Phase X Compaction Summary

**Date**: 2026-__
**Orchestrator**: Claude
**Context Before**: ___%
**Context After**: ___%

## Completed Work

### Agent Alpha (Phase 2)
- [X] Milestone 1: Symbiosis Foundation
- [ ] Milestone 2: Immune System
- [ ] Milestone 3: Competition Engine

### Agent Beta (Phase 3)
- [ ] Milestone 1: Evolution Engine
...

### Agent Gamma (Phase 4)
- [ ] Milestone 1: Colony System
...

## Issues Found
- List any blocking issues or concerns

## Next Steps
- Clear priorities for next phase
- Dependencies to resolve

## Files Changed
- List key files added/modified

---
*Compact complete. Ready to continue.*
```

---

**Remember**: Compact BEFORE context gets critical, not after. Stay ahead of it!
