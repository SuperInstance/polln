# POLLN Implementation Strategies - Round 5 Research

**Pattern-Organized Large Language Network**
**Research Agent:** Research Synthesizer
**Date:** 2026-03-06
**Status:** COMPLETE

---

## Executive Summary

This document provides **detailed implementation strategies** for the top 2 most impactful innovation patterns identified in Round 4 research. Each pattern includes:

1. **Implementation Roadmap** - Step-by-step how to build it
2. **Code Skeleton** - Key interfaces and class structures (TypeScript)
3. **Integration Points** - How it connects to existing `src/core/` components
4. **Testing Strategy** - How to verify it works
5. **Risk Assessment** - What could go wrong

These patterns are prioritized based on:
- **Impact on system safety and scalability**
- **Feasibility given existing architecture**
- **Dependency relationships** (Stigmergic enables later patterns)
- **Quick wins vs. long-term value**

---

## Table of Contents

1. [Guardian Angel Safety Pattern](#1-guardian-angel-safety-pattern)
2. [Stigmergic Coordination Pattern](#2-stigmergic-coordination-pattern)

---

## 1. Guardian Angel Safety Pattern

### 1.1 Pattern Overview

**Novelty Score:** 8/10
**Implementation Complexity:** Medium
**Estimated Effort:** 4-5 weeks
**Priority:** HIGH (Critical for safety)

**Key Insight:** A shadow agent that runs in parallel with each agent, having veto power over dangerous actions while remaining transparent to the main agent.

**Why Build First:**
- Extends existing `SafetyLayer` in `src/core/safety.ts`
- Critical for production readiness
- Enables safe experimentation with other patterns
- Builds trust through visible safety measures

---

### 1.2 Implementation Roadmap

#### Phase 1: Foundation (Week 1)
**Goal:** Set up basic guardian infrastructure

**Steps:**
1. Create `src/core/guardian.ts` with base interfaces
2. Implement `GuardianAngelAgent` class skeleton
3. Create `GuardianAngelManager` for lifecycle management
4. Add guardian configuration to existing `SafetyLayer`
5. Set up basic A2A package interception

**Deliverables:**
- `GuardianAngelAgent` class with proposal review
- `GuardianAngelManager` for agent assignment
- Integration with existing `SafetyLayer`
- Basic unit tests

**Acceptance Criteria:**
- Guardian can intercept agent proposals
- Basic ALLOW/VETO decisions work
- Integration tests pass

---

#### Phase 2: Safety Constraints Engine (Week 2)
**Goal:** Implement constraint evaluation system

**Steps:**
1. Extend `SafetyConstraint` interface from `src/core/safety.ts`
2. Create constraint evaluation engine
3. Implement pre-check, mid-execution, post-validation
4. Add constraint learning system
5. Create constraint library

**Deliverables:**
- Enhanced `SafetyConstraint` with executable rules
- `ConstraintEngine` class for evaluation
- Pre/mid/post checkpoint system
- Standard constraint library (20+ constraints)

**Acceptance Criteria:**
- Constraints can be checked at all execution phases
- Constraint violations trigger appropriate actions
- Learning system updates constraint thresholds

---

#### Phase 3: Modification Engine (Week 2-3)
**Goal:** Implement action modification capability

**Steps:**
1. Create `ActionModifier` class
2. Implement parameter adjustment algorithms
3. Add context-aware modification strategies
4. Build modification effectiveness tracker
5. Integrate with proposal review flow

**Deliverables:**
- `ActionModifier` with multiple strategies
- Parameter adjustment algorithms
- Modification effectiveness metrics
- Integration with guardian decision flow

**Acceptance Criteria:**
- Unsafe actions can be modified to safe versions
- Modifications maintain action intent
- Effectiveness is tracked and learned

---

#### Phase 4: Execution Monitoring (Week 3)
**Goal:** Implement real-time execution monitoring

**Steps:**
1. Create `ExecutionMonitor` class
2. Implement checkpoint system for long-running actions
3. Add emergency stop mechanism
4. Build risk assessment during execution
5. Create monitoring dashboard hooks

**Deliverables:**
- `ExecutionMonitor` with real-time checks
- Emergency stop infrastructure
- Risk assessment algorithms
- Metrics and logging

**Acceptance Criteria:**
- Long-running actions are monitored
- Emergency stop triggers on high risk
- Monitoring doesn't add significant latency

---

#### Phase 5: Learning & Adaptation (Week 4)
**Goal:** Implement guardian learning system

**Steps:**
1. Create intervention learning module
2. Implement false positive reduction
3. Add constraint threshold optimization
4. Build guardian performance metrics
5. Create A/B testing framework

**Deliverables:**
- Intervention learning system
- False positive reduction
- Constraint optimization
- Performance dashboard

**Acceptance Criteria:**
- Guardian improves from feedback
- False positive rate decreases over time
- Constraint thresholds auto-tune

---

#### Phase 6: Integration & Testing (Week 4-5)
**Goal:** Full system integration and testing

**Steps:**
1. Integrate with existing agent lifecycle
2. Add guardian to all agent types
3. Create comprehensive test suite
4. Performance testing and optimization
5. Documentation and examples

**Deliverables:**
- Full integration with agent system
- Comprehensive test suite (unit + integration)
- Performance benchmarks
- Complete documentation

**Acceptance Criteria:**
- All agents have guardians by default
- Test coverage > 80%
- Performance overhead < 10ms per decision
- Documentation complete

---

### 1.3 Code Skeleton

#### File: `src/core/guardian/types.ts`

```typescript
/**
 * Guardian Angel Safety Pattern Types
 * Extends existing SafetyLayer types
 */

import type { SafetyConstraint, SafetySeverity } from '../safety';

/**
 * Guardian decision types
 */
export type GuardianDecision =
  | { action: 'ALLOW'; reason: string; confidence: number; warnings?: string[] }
  | { action: 'VETO'; reason: string; constraintId?: string; confidence: number }
  | { action: 'MODIFY'; reason: string; modification: Modification; confidence: number };

/**
 * Action proposal from agent
 */
export interface ActionProposal {
  id: string;
  agentId: string;
  actionType: string;
  action: unknown;
  context: Record<string, unknown>;
  timestamp: number;
}

/**
 * Modification to make action safe
 */
export interface Modification {
  originalProposal: ActionProposal;
  modifiedProposal: ActionProposal;
  safety: number;
  fixesViolation: string;
  changes: ParameterChange[];
}

/**
 * Parameter change in modification
 */
export interface ParameterChange {
  path: string;
  originalValue: unknown;
  modifiedValue: unknown;
  reason: string;
}

/**
 * Safety violation
 */
export interface SafetyViolation {
  constraintId: string;
  rule: string;
  severity: SafetySeverity;
  reason: string;
  canOverride: boolean;
}

/**
 * Intervention record
 */
export interface Intervention {
  id: string;
  proposal: ActionProposal;
  decision: GuardianDecision;
  constraintId?: string;
  risk: number;
  timestamp: number;
}

/**
 * Intervention outcome for learning
 */
export interface InterventionOutcome {
  wasCorrect: boolean;
  actualOutcome?: string;
  userFeedback?: number;
  safetyScore: number;
}

/**
 * Guardian configuration
 */
export interface GuardianConfig {
  id: string;
  protectedAgentId: string;
  constraints: SafetyConstraint[];
  learningRate: number;
  falsePositiveTolerance: number;
  interventionThreshold: number;
  emergencyStopEnabled: boolean;
  monitoringEnabled: boolean;
}

/**
 * Execution checkpoint
 */
export interface ExecutionCheckpoint {
  timestamp: number;
  risk: number;
  state: Record<string, unknown>;
  passedSafetyChecks: boolean;
}

/**
 * Execution monitor
 */
export interface ExecutionMonitor {
  action: ActiveAction;
  checkpoints: ExecutionCheckpoint[];
  emergencyStop: boolean;
  reason?: string;
}

/**
 * Active action being monitored
 */
export interface ActiveAction {
  id: string;
  proposal: ActionProposal;
  startTime: number;
  state: Record<string, unknown>;
}

/**
 * Guardian statistics
 */
export interface GuardianStats {
  interventions: number;
  vetoes: number;
  modifications: number;
  allows: number;
  falsePositives: number;
  falseNegatives: number;
  avgResponseTime: number;
}
```

#### File: `src/core/guardian/guardian.ts`

```typescript
/**
 * Guardian Angel Agent Implementation
 * Shadow agent with veto power over dangerous actions
 */

import { v4 as uuidv4 } from 'uuid';
import type {
  GuardianConfig,
  ActionProposal,
  GuardianDecision,
  Modification,
  SafetyViolation,
  Intervention,
  InterventionOutcome,
  ExecutionMonitor,
} from './types';
import type { SafetyConstraint } from '../safety';
import { ConstraintEngine } from './constraint-engine';
import { ActionModifier } from './action-modifier';
import { ExecutionMonitor } from './execution-monitor';

/**
 * GuardianAngelAgent - Shadow agent for safety
 *
 * Runs in parallel with protected agent, reviewing all actions
 * before execution. Can veto, modify, or allow actions based on
 * safety constraints.
 */
export class GuardianAngelAgent {
  private id: string;
  private config: GuardianConfig;
  private constraintEngine: ConstraintEngine;
  private actionModifier: ActionModifier;
  private executionMonitor: ExecutionMonitor;
  private interventionHistory: Intervention[] = [];
  private learningState: Map<string, number> = new Map();

  constructor(config: GuardianConfig) {
    this.id = uuidv4();
    this.config = config;
    this.constraintEngine = new ConstraintEngine(config.constraints);
    this.actionModifier = new ActionModifier();
    this.executionMonitor = new ExecutionMonitor(config.monitoringEnabled);
  }

  /**
   * Review agent action proposal
   *
   * Main decision point: analyze proposal and decide ALLOW/MODIFY/VETO
   */
  async reviewProposal(proposal: ActionProposal): Promise<GuardianDecision> {
    const startTime = Date.now();

    // Phase 1: Check against all safety constraints
    const violations = await this.constraintEngine.checkConstraints(proposal);

    // Phase 2: Assess risk level
    const risk = this.assessRisk(proposal, violations);

    // Phase 3: Make decision
    let decision: GuardianDecision;

    if (violations.length === 0) {
      // No violations - allow immediately
      decision = {
        action: 'ALLOW',
        reason: 'No safety violations detected',
        confidence: 1.0,
      };
    } else {
      // Check for critical violations
      const critical = violations.find(v => v.severity === 'CRITICAL');

      if (critical) {
        // Critical violation - veto immediately
        decision = {
          action: 'VETO',
          reason: `Critical violation: ${critical.rule}`,
          constraintId: critical.id,
          confidence: 1.0,
        };
      } else {
        // Check if modifiable
        const modifications = await this.generateModifications(proposal, violations);

        if (modifications.length > 0 && risk < this.config.interventionThreshold) {
          // Select best modification
          const bestModification = modifications.sort((a, b) => b.safety - a.safety)[0];

          decision = {
            action: 'MODIFY',
            reason: `Action modified for safety: ${violations.map(v => v.rule).join(', ')}`,
            modification: bestModification,
            confidence: bestModification.safety,
          };
        } else if (risk >= this.config.interventionThreshold) {
          // Too risky - veto
          decision = {
            action: 'VETO',
            reason: `Unacceptable risk: ${risk.toFixed(2)} (threshold: ${this.config.interventionThreshold})`,
            confidence: risk,
          };
        } else {
          // Allow with warnings
          decision = {
            action: 'ALLOW',
            reason: 'Acceptable risk with warnings',
            confidence: 1 - risk,
            warnings: violations.map(v => v.rule),
          };
        }
      }
    }

    // Log intervention
    this.recordIntervention(proposal, decision, risk, Date.now() - startTime);

    return decision;
  }

  /**
   * Monitor action during execution
   *
   * For long-running actions, set up monitoring checkpoints
   */
  async monitorExecution(action: ActiveAction): Promise<ExecutionMonitor> {
    return this.executionMonitor.monitor(action, async (state) => {
      // Assess execution state
      const risk = await this.assessExecutionState(state);

      // Check if emergency stop needed
      if (risk > 0.9) {
        return { stop: true, reason: `High risk during execution: ${risk.toFixed(2)}` };
      }

      return { stop: false };
    });
  }

  /**
   * Learn from intervention outcome
   *
   * Update learning based on whether intervention was correct
   */
  async learnFromIntervention(
    intervention: Intervention,
    outcome: InterventionOutcome
  ): Promise<void> {
    // Update constraint thresholds
    if (intervention.decision.action === 'VETO' && outcome.wasCorrect) {
      await this.constraintEngine.reinforceConstraint(intervention.constraintId!);
    }

    // Reduce false positives
    if (intervention.decision.action === 'VETO' && !outcome.wasCorrect) {
      await this.constraintEngine.relaxConstraint(intervention.constraintId!);
    }

    // Update learning state
    const key = `${intervention.proposal.agentId}-${intervention.proposal.actionType}`;
    const currentLearning = this.learningState.get(key) || 0.5;
    const targetLearning = outcome.wasCorrect ? 1.0 : 0.0;
    const newLearning = currentLearning + this.config.learningRate * (targetLearning - currentLearning);
    this.learningState.set(key, newLearning);
  }

  /**
   * Assess risk level of proposal
   */
  private assessRisk(proposal: ActionProposal, violations: SafetyViolation[]): number {
    let risk = 0.0;

    // Base risk from violations
    for (const violation of violations) {
      switch (violation.severity) {
        case 'CRITICAL':
          risk += 0.5;
          break;
        case 'ERROR':
          risk += 0.3;
          break;
        case 'WARNING':
          risk += 0.1;
          break;
        case 'INFO':
          risk += 0.0;
          break;
      }
    }

    // Adjust for agent's track record
    const agentTrust = this.learningState.get(`${proposal.agentId}-trust`) ?? 0.5;
    risk *= (1.0 - agentTrust * 0.5);

    return Math.min(1.0, risk);
  }

  /**
   * Generate safe modifications to proposal
   */
  private async generateModifications(
    proposal: ActionProposal,
    violations: SafetyViolation[]
  ): Promise<Modification[]> {
    const modifications: Modification[] = [];

    // For each violation, try to generate fix
    for (const violation of violations) {
      if (violation.canOverride) {
        const modification = await this.actionModifier.modifyForViolation(
          proposal,
          violation
        );

        if (modification) {
          modifications.push(modification);
        }
      }
    }

    // Try combined modifications
    const combined = await this.actionModifier.combineModifications(
      proposal,
      modifications
    );

    return [...modifications, ...combined];
  }

  /**
   * Assess execution state during monitoring
   */
  private async assessExecutionState(state: Record<string, unknown>): Promise<number> {
    // Simplified risk assessment
    // In production, this would use more sophisticated analysis
    let risk = 0.0;

    // Check for warning signs
    if (state.error) risk += 0.3;
    if (state.unexpectedState) risk += 0.2;
    if (state.resourceUsage) {
      const usage = state.resourceUsage as { cpu: number; memory: number };
      if (usage.cpu > 0.9) risk += 0.2;
      if (usage.memory > 0.9) risk += 0.2;
    }

    return Math.min(1.0, risk);
  }

  /**
   * Record intervention for learning
   */
  private recordIntervention(
    proposal: ActionProposal,
    decision: GuardianDecision,
    risk: number,
    responseTime: number
  ): void {
    const intervention: Intervention = {
      id: uuidv4(),
      proposal,
      decision,
      constraintId: decision.action === 'VETO' ? decision.constraintId : undefined,
      risk,
      timestamp: Date.now(),
    };

    this.interventionHistory.push(intervention);

    // Keep history manageable
    if (this.interventionHistory.length > 1000) {
      this.interventionHistory = this.interventionHistory.slice(-500);
    }
  }

  /**
   * Get guardian statistics
   */
  getStats(): GuardianStats {
    const interventions = this.interventionHistory.length;
    const vetoes = this.interventionHistory.filter(i => i.decision.action === 'VETO').length;
    const modifications = this.interventionHistory.filter(i => i.decision.action === 'MODIFY').length;
    const allows = this.interventionHistory.filter(i => i.decision.action === 'ALLOW').length;

    return {
      interventions,
      vetoes,
      modifications,
      allows,
      falsePositives: 0, // Track via learning
      falseNegatives: 0,
      avgResponseTime: 10, // Track via timing
    };
  }
}
```

#### File: `src/core/guardian/constraint-engine.ts`

```typescript
/**
 * Constraint Engine
 * Evaluates safety constraints against proposals
 */

import type { SafetyConstraint, SafetySeverity } from '../safety';
import type { ActionProposal, SafetyViolation } from './types';

/**
 * ConstraintEngine - Evaluate safety constraints
 */
export class ConstraintEngine {
  private constraints: Map<string, SafetyConstraint> = new Map();
  private constraintPerformance: Map<string, ConstraintPerformance> = new Map();

  constructor(constraints: SafetyConstraint[]) {
    for (const constraint of constraints) {
      this.constraints.set(constraint.id, constraint);
      this.constraintPerformance.set(constraint.id, {
        truePositiveRate: 0.5,
        falsePositiveRate: 0.5,
        triggerCount: 0,
        lastUpdated: Date.now(),
      });
    }
  }

  /**
   * Check proposal against all constraints
   */
  async checkConstraints(proposal: ActionProposal): Promise<SafetyViolation[]> {
    const violations: SafetyViolation[] = [];

    for (const constraint of this.constraints.values()) {
      if (!constraint.isActive) continue;

      const result = await this.evaluateConstraint(constraint, proposal);

      if (!result.passed) {
        violations.push({
          constraintId: constraint.id,
          rule: constraint.rule,
          severity: constraint.severity,
          reason: result.reason,
          canOverride: !constraint.cannotOverride,
        });

        // Update performance tracking
        const perf = this.constraintPerformance.get(constraint.id)!;
        perf.triggerCount++;
        perf.lastUpdated = Date.now();
      }
    }

    return violations;
  }

  /**
   * Evaluate single constraint
   */
  private async evaluateConstraint(
    constraint: SafetyConstraint,
    proposal: ActionProposal
  ): Promise<{ passed: boolean; reason: string }> {
    if (constraint.ruleCode) {
      // Execute machine-checkable rule
      return this.evaluateRuleCode(constraint.ruleCode, proposal);
    }

    // Natural language matching
    return this.naturalLanguageMatch(constraint.rule, proposal);
  }

  /**
   * Evaluate machine-checkable rule code
   */
  private async evaluateRuleCode(
    ruleCode: string,
    proposal: ActionProposal
  ): Promise<{ passed: boolean; reason: string }> {
    try {
      // Create safe execution context
      const context = {
        proposal,
        action: proposal.action,
        context: proposal.context,
      };

      // Execute rule code (in production, use proper sandbox)
      const result = this.safeExecute(ruleCode, context);

      return {
        passed: result === true,
        reason: result === true ? 'Rule check passed' : 'Rule check failed',
      };
    } catch (error) {
      return {
        passed: false,
        reason: `Rule execution error: ${error}`,
      };
    }
  }

  /**
   * Safe rule execution
   */
  private safeExecute(ruleCode: string, context: Record<string, unknown>): boolean {
    // Placeholder for safe execution
    // In production, use proper sandboxing
    return true;
  }

  /**
   * Natural language matching
   */
  private async naturalLanguageMatch(
    rule: string,
    proposal: ActionProposal
  ): Promise<{ passed: boolean; reason: string }> {
    const actionStr = JSON.stringify(proposal.action).toLowerCase();
    const ruleStr = rule.toLowerCase();

    // Simple keyword matching
    const dangerousKeywords = ['delete', 'destroy', 'harm', 'damage', 'exploit'];
    const foundKeywords = dangerousKeywords.filter(k => actionStr.includes(k));

    if (foundKeywords.length > 0) {
      return {
        passed: false,
        reason: `Action contains potentially dangerous keywords: ${foundKeywords.join(', ')}`,
      };
    }

    return {
      passed: true,
      reason: 'No dangerous patterns detected',
    };
  }

  /**
   * Reinforce constraint (make it stricter)
   */
  async reinforceConstraint(constraintId: string): Promise<void> {
    const constraint = this.constraints.get(constraintId);
    if (constraint && constraint.threshold !== undefined) {
      constraint.threshold *= 0.95; // Make 5% stricter
    }

    const perf = this.constraintPerformance.get(constraintId);
    if (perf) {
      perf.truePositiveRate += 0.1;
    }
  }

  /**
   * Relax constraint (reduce false positives)
   */
  async relaxConstraint(constraintId: string): Promise<void> {
    const constraint = this.constraints.get(constraintId);
    if (constraint && constraint.threshold !== undefined) {
      constraint.threshold *= 1.05; // Make 5% more lenient
    }

    const perf = this.constraintPerformance.get(constraintId);
    if (perf) {
      perf.falsePositiveRate += 0.1;
    }
  }

  /**
   * Add constraint
   */
  addConstraint(constraint: SafetyConstraint): void {
    this.constraints.set(constraint.id, constraint);
    this.constraintPerformance.set(constraint.id, {
      truePositiveRate: 0.5,
      falsePositiveRate: 0.5,
      triggerCount: 0,
      lastUpdated: Date.now(),
    });
  }

  /**
   * Remove constraint
   */
  removeConstraint(constraintId: string): boolean {
    this.constraintPerformance.delete(constraintId);
    return this.constraints.delete(constraintId);
  }
}

interface ConstraintPerformance {
  truePositiveRate: number;
  falsePositiveRate: number;
  triggerCount: number;
  lastUpdated: number;
}
```

#### File: `src/core/guardian/action-modifier.ts`

```typescript
/**
 * Action Modifier
 * Modifies unsafe actions to make them safe
 */

import type { ActionProposal, Modification, SafetyViolation, ParameterChange } from './types';

/**
 * ActionModifier - Make unsafe actions safe
 */
export class ActionModifier {
  /**
   * Modify proposal to fix violation
   */
  async modifyForViolation(
    proposal: ActionProposal,
    violation: SafetyViolation
  ): Promise<Modification | null> {
    const modifiedProposal = { ...proposal };
    const changes: ParameterChange[] = [];

    // Extract action
    const action = modifiedProposal.action as Record<string, unknown>;

    switch (violation.constraintId) {
      case 'resource-limit':
        // Reduce resource usage
        if (action.resourceLimit) {
          changes.push({
            path: 'action.resourceLimit',
            originalValue: action.resourceLimit,
            modifiedValue: Math.floor(Number(action.resourceLimit) * 0.8),
            reason: 'Reduced to stay within safe limits',
          });
          (action as Record<string, unknown>).resourceLimit = changes[0].modifiedValue;
        }
        break;

      case 'data-access':
        // Add data filtering
        if (action.query) {
          changes.push({
            path: 'action.query.filter',
            originalValue: undefined,
            modifiedValue: 'safeFilter',
            reason: 'Added safety filter to data access',
          });
          (action as Record<string, unknown>).filter = 'safeFilter';
        }
        break;

      case 'external-call':
        // Add timeout and retry limits
        changes.push({
          path: 'action.timeout',
          originalValue: action.timeout || undefined,
          modifiedValue: 5000,
          reason: 'Added timeout to prevent hanging',
        });
        (action as Record<string, unknown>).timeout = 5000;

        changes.push({
          path: 'action.maxRetries',
          originalValue: action.maxRetries || undefined,
          modifiedValue: 3,
          reason: 'Limited retries to prevent resource exhaustion',
        });
        (action as Record<string, unknown>).maxRetries = 3;
        break;

      default:
        // Generic modification
        return null;
    }

    // Estimate safety improvement
    const safety = this.estimateSafety(proposal, modifiedProposal);

    return {
      originalProposal: proposal,
      modifiedProposal,
      safety,
      fixesViolation: violation.constraintId,
      changes,
    };
  }

  /**
   * Combine multiple modifications
   */
  async combineModifications(
    proposal: ActionProposal,
    modifications: Modification[]
  ): Promise<Modification[]> {
    const combined: Modification[] = [];

    // Try all combinations
    for (let i = 0; i < modifications.length; i++) {
      for (let j = i + 1; j < modifications.length; j++) {
        const combinedProposal = this.mergeProposals(
          modifications[i].modifiedProposal,
          modifications[j].modifiedProposal
        );

        const safety = this.estimateSafety(proposal, combinedProposal);

        combined.push({
          originalProposal: proposal,
          modifiedProposal: combinedProposal,
          safety,
          fixesViolation: `${modifications[i].fixesViolation}+${modifications[j].fixesViolation}`,
          changes: [
            ...modifications[i].changes,
            ...modifications[j].changes,
          ],
        });
      }
    }

    return combined;
  }

  /**
   * Merge two proposals
   */
  private mergeProposals(
    proposal1: ActionProposal,
    proposal2: ActionProposal
  ): ActionProposal {
    const merged = { ...proposal1 };
    merged.action = {
      ...(proposal1.action as Record<string, unknown>),
      ...(proposal2.action as Record<string, unknown>),
    };
    merged.context = {
      ...proposal1.context,
      ...proposal2.context,
    };
    return merged;
  }

  /**
   * Estimate safety of modified proposal
   */
  private estimateSafety(original: ActionProposal, modified: ActionProposal): number {
    // Simplified safety estimation
    // In production, use more sophisticated analysis
    let safety = 0.5;

    // Check for safety features
    const modAction = modified.action as Record<string, unknown>;

    if (modAction.timeout) safety += 0.1;
    if (modAction.maxRetries) safety += 0.1;
    if (modAction.filter) safety += 0.15;
    if (modAction.rateLimit) safety += 0.15;
    if (modAction.validation) safety += 0.1;

    return Math.min(1.0, safety);
  }
}
```

#### File: `src/core/guardian/execution-monitor.ts`

```typescript
/**
 * Execution Monitor
 * Real-time monitoring of long-running actions
 */

import type { ActiveAction, ExecutionCheckpoint, ExecutionMonitor as Monitor } from './types';

/**
 * ExecutionMonitor - Monitor actions during execution
 */
export class ExecutionMonitor {
  private monitors: Map<string, Monitor> = new Map();
  private enabled: boolean;

  constructor(enabled: boolean = true) {
    this.enabled = enabled;
  }

  /**
   * Start monitoring an action
   */
  async monitor(
    action: ActiveAction,
    checkInterval: number = 1000,
    checkFunction?: (state: Record<string, unknown>) => Promise<{ stop: boolean; reason?: string }>
  ): Promise<Monitor> {
    if (!this.enabled) {
      return {
        action,
        checkpoints: [],
        emergencyStop: false,
      };
    }

    const monitor: Monitor = {
      action,
      checkpoints: [],
      emergencyStop: false,
    };

    this.monitors.set(action.id, monitor);

    // Start monitoring loop
    if (checkFunction) {
      this.startMonitoringLoop(action, checkInterval, checkFunction, monitor);
    }

    return monitor;
  }

  /**
   * Start monitoring loop
   */
  private async startMonitoringLoop(
    action: ActiveAction,
    interval: number,
    checkFunction: (state: Record<string, unknown>) => Promise<{ stop: boolean; reason?: string }>,
    monitor: Monitor
  ): Promise<void> {
    const loopId = setInterval(async () => {
      try {
        // Get current state
        const state = await this.getActionState(action);

        // Run safety check
        const result = await checkFunction(state);

        // Record checkpoint
        monitor.checkpoints.push({
          timestamp: Date.now(),
          risk: await this.assessRisk(state),
          state,
          passedSafetyChecks: !result.stop,
        });

        // Check if emergency stop needed
        if (result.stop) {
          monitor.emergencyStop = true;
          monitor.reason = result.reason;
          clearInterval(loopId);

          // Trigger emergency stop
          await this.emergencyStop(action);
        }
      } catch (error) {
        console.error(`Monitoring error for action ${action.id}:`, error);
      }
    }, interval);

    // Clean up on completion
    action.onComplete?.(() => {
      clearInterval(loopId);
    });
  }

  /**
   * Get action state
   */
  private async getActionState(action: ActiveAction): Promise<Record<string, unknown>> {
    // Placeholder for state retrieval
    return action.state;
  }

  /**
   * Assess risk from state
   */
  private async assessRisk(state: Record<string, unknown>): Promise<number> {
    let risk = 0.0;

    // Check for warning signs
    if (state.error) risk += 0.3;
    if (state.unexpectedState) risk += 0.2;
    if (state.exceptions) risk += 0.3;

    // Check resource usage
    if (state.resourceUsage) {
      const usage = state.resourceUsage as { cpu: number; memory: number };
      if (usage.cpu > 0.9) risk += 0.2;
      if (usage.memory > 0.9) risk += 0.2;
    }

    return Math.min(1.0, risk);
  }

  /**
   * Emergency stop
   */
  private async emergencyStop(action: ActiveAction): Promise<void> {
    console.warn(`EMERGENCY STOP triggered for action ${action.id}`);

    // Notify action to stop
    if (action.stop) {
      await action.stop();
    }
  }

  /**
   * Get monitor
   */
  getMonitor(actionId: string): Monitor | undefined {
    return this.monitors.get(actionId);
  }

  /**
   * Remove monitor
   */
  removeMonitor(actionId: string): void {
    this.monitors.delete(actionId);
  }
}
```

#### File: `src/core/guardian/manager.ts`

```typescript
/**
 * Guardian Angel Manager
 * Manages lifecycle of guardian agents
 */

import { v4 as uuidv4 } from 'uuid';
import type { GuardianConfig, GuardianStats } from './types';
import { GuardianAngelAgent } from './guardian';

/**
 * GuardianAngelManager - Manage all guardians
 */
export class GuardianAngelManager {
  private guardians: Map<string, GuardianAngelAgent> = new Map();
  private agentToGuardian: Map<string, string> = new Map();

  /**
   * Assign guardian to agent
   */
  assignGuardian(agentId: string, config: Partial<GuardianConfig>): string {
    const guardianConfig: GuardianConfig = {
      id: uuidv4(),
      protectedAgentId: agentId,
      constraints: config.constraints || [],
      learningRate: config.learningRate || 0.1,
      falsePositiveTolerance: config.falsePositiveTolerance || 0.1,
      interventionThreshold: config.interventionThreshold || 0.8,
      emergencyStopEnabled: config.emergencyStopEnabled ?? true,
      monitoringEnabled: config.monitoringEnabled ?? true,
    };

    const guardian = new GuardianAngelAgent(guardianConfig);
    const guardianId = guardianConfig.id;

    this.guardians.set(guardianId, guardian);
    this.agentToGuardian.set(agentId, guardianId);

    return guardianId;
  }

  /**
   * Get guardian for agent
   */
  getGuardian(agentId: string): GuardianAngelAgent | undefined {
    const guardianId = this.agentToGuardian.get(agentId);
    return guardianId ? this.guardians.get(guardianId) : undefined;
  }

  /**
   * Remove guardian
   */
  removeGuardian(agentId: string): boolean {
    const guardianId = this.agentToGuardian.get(agentId);
    if (!guardianId) return false;

    this.agentToGuardian.delete(agentId);
    return this.guardians.delete(guardianId);
  }

  /**
   * Get all guardians
   */
  getAllGuardians(): GuardianAngelAgent[] {
    return Array.from(this.guardians.values());
  }

  /**
   * Get aggregate statistics
   */
  getStats(): GuardianStats & { guardiansActive: number } {
    let totalInterventions = 0;
    let totalVetoes = 0;
    let totalModifications = 0;
    let totalAllows = 0;
    let totalFalsePositives = 0;
    let totalFalseNegatives = 0;
    let totalResponseTime = 0;

    for (const guardian of this.guardians.values()) {
      const stats = guardian.getStats();
      totalInterventions += stats.interventions;
      totalVetoes += stats.vetoes;
      totalModifications += stats.modifications;
      totalAllows += stats.allows;
      totalFalsePositives += stats.falsePositives;
      totalFalseNegatives += stats.falseNegatives;
      totalResponseTime += stats.avgResponseTime;
    }

    return {
      guardiansActive: this.guardians.size,
      interventions: totalInterventions,
      vetoes: totalVetoes,
      modifications: totalModifications,
      allows: totalAllows,
      falsePositives: totalFalsePositives,
      falseNegatives: totalFalseNegatives,
      avgResponseTime: this.guardians.size > 0 ? totalResponseTime / this.guardians.size : 0,
    };
  }
}
```

---

### 1.4 Integration Points

#### Integration with Existing SafetyLayer

```typescript
// File: src/core/safety.ts (extend existing)

import { GuardianAngelManager } from './guardian/manager';

export class SafetyLayer {
  // ... existing code ...

  private guardianManager: GuardianAngelManager;

  constructor(/* ... existing ... */) {
    // ... existing initialization ...
    this.guardianManager = new GuardianAngelManager();
  }

  /**
   * Check action with guardian review
   */
  async checkActionWithGuardian(
    agentId: string,
    action: unknown,
    context?: Record<string, unknown>
  ): Promise<SafetyCheckResult> {
    // First, check with traditional safety layer
    const traditionalResult = this.checkAction(agentId, action, context);

    // Then, check with guardian
    const guardian = this.guardianManager.getGuardian(agentId);
    if (guardian) {
      const proposal = {
        id: uuidv4(),
        agentId,
        actionType: action?.constructor?.name || 'unknown',
        action,
        context: context || {},
        timestamp: Date.now(),
      };

      const guardianDecision = await guardian.reviewProposal(proposal);

      // Combine results
      if (guardianDecision.action === 'VETO') {
        return {
          passed: false,
          constraintId: guardianDecision.constraintId,
          severity: 'CRITICAL',
          message: guardianDecision.reason,
          blockedBy: 'guardian',
        };
      }
    }

    return traditionalResult;
  }

  /**
   * Assign guardian to agent
   */
  assignGuardian(agentId: string, config?: Partial<GuardianConfig>): string {
    return this.guardianManager.assignGuardian(agentId, {
      constraints: this.getConstraints(),
      ...config,
    });
  }
}
```

#### Integration with BaseAgent

```typescript
// File: src/core/agent.ts (extend existing)

import type { GuardianDecision } from './guardian/types';

export abstract class BaseAgent<TConfig = unknown, TInput = unknown> extends EventEmitter {
  // ... existing code ...

  private guardianId?: string;

  /**
   * Process with guardian review
   */
  async processWithGuardian<T>(input: T): Promise<A2APackage<T>> {
    // Get action proposal
    const proposal = this.createActionProposal(input);

    // Check with guardian
    const guardian = this.getGuardian();
    if (guardian) {
      const decision = await guardian.reviewProposal(proposal);

      switch (decision.action) {
        case 'VETO':
          throw new Error(`Action vetoed by guardian: ${decision.reason}`);

        case 'MODIFY':
          proposal.action = decision.modification.modifiedProposal.action;
          break;

        case 'ALLOW':
          // Proceed with original action
          break;
      }
    }

    // Execute action
    return this.process(proposal.action as T);
  }

  /**
   * Create action proposal for guardian review
   */
  private createActionProposal<T>(input: T): any {
    return {
      id: uuidv4(),
      agentId: this.id,
      actionType: this.constructor.name,
      action: input,
      context: {
        state: Object.fromEntries(this.state),
        lastActive: this.lastActive,
      },
      timestamp: Date.now(),
    };
  }

  /**
   * Get guardian for this agent
   */
  private getGuardian() {
    // Access from safety layer
    return this.colony?.safetyLayer?.getGuardian(this.id);
  }
}
```

---

### 1.5 Testing Strategy

#### Unit Tests

```typescript
// File: src/core/guardian/__tests__/guardian.test.ts

describe('GuardianAngelAgent', () => {
  let guardian: GuardianAngelAgent;
  let mockConfig: GuardianConfig;

  beforeEach(() => {
    mockConfig = {
      id: 'test-guardian',
      protectedAgentId: 'test-agent',
      constraints: [
        {
          id: 'test-constraint',
          name: 'Test Constraint',
          category: 'safety',
          rule: 'No dangerous actions',
          severity: 'ERROR',
          isActive: true,
          cannotOverride: false,
        },
      ],
      learningRate: 0.1,
      falsePositiveTolerance: 0.1,
      interventionThreshold: 0.8,
      emergencyStopEnabled: true,
      monitoringEnabled: true,
    };

    guardian = new GuardianAngelAgent(mockConfig);
  });

  describe('reviewProposal', () => {
    it('should allow safe proposals', async () => {
      const proposal: ActionProposal = {
        id: 'test-proposal',
        agentId: 'test-agent',
        actionType: 'safe-action',
        action: { type: 'safe', value: 42 },
        context: {},
        timestamp: Date.now(),
      };

      const decision = await guardian.reviewProposal(proposal);

      expect(decision.action).toBe('ALLOW');
      expect(decision.confidence).toBeGreaterThan(0.8);
    });

    it('should veto dangerous proposals', async () => {
      const proposal: ActionProposal = {
        id: 'test-proposal',
        agentId: 'test-agent',
        actionType: 'dangerous-action',
        action: { type: 'deleteEverything' },
        context: {},
        timestamp: Date.now(),
      };

      const decision = await guardian.reviewProposal(proposal);

      expect(decision.action).toBe('VETO');
      expect(decision.reason).toContain('dangerous');
    });

    it('should modify modifiable proposals', async () => {
      const proposal: ActionProposal = {
        id: 'test-proposal',
        agentId: 'test-agent',
        actionType: 'resource-intensive',
        action: { type: 'compute', resourceLimit: 1000 },
        context: {},
        timestamp: Date.now(),
      };

      const decision = await guardian.reviewProposal(proposal);

      expect(decision.action).toBe('MODIFY');
      if (decision.action === 'MODIFY') {
        expect(decision.modification.changes.length).toBeGreaterThan(0);
      }
    });
  });

  describe('learnFromIntervention', () => {
    it('should reinforce constraint on correct veto', async () => {
      const intervention: Intervention = {
        id: 'test-intervention',
        proposal: {} as any,
        decision: { action: 'VETO', reason: 'Test', constraintId: 'test-constraint', confidence: 1.0 },
        constraintId: 'test-constraint',
        risk: 0.9,
        timestamp: Date.now(),
      };

      const outcome: InterventionOutcome = {
        wasCorrect: true,
        safetyScore: 1.0,
      };

      await guardian.learnFromIntervention(intervention, outcome);

      // Verify constraint was reinforced
      const stats = guardian.getStats();
      expect(stats.interventions).toBeGreaterThan(0);
    });

    it('should relax constraint on false positive', async () => {
      const intervention: Intervention = {
        id: 'test-intervention',
        proposal: {} as any,
        decision: { action: 'VETO', reason: 'Test', constraintId: 'test-constraint', confidence: 1.0 },
        constraintId: 'test-constraint',
        risk: 0.9,
        timestamp: Date.now(),
      };

      const outcome: InterventionOutcome = {
        wasCorrect: false,
        safetyScore: 0.0,
      };

      await guardian.learnFromIntervention(intervention, outcome);

      // Verify constraint was relaxed
      const stats = guardian.getStats();
      expect(stats.falsePositives).toBeGreaterThan(0);
    });
  });
});
```

#### Integration Tests

```typescript
// File: src/core/guardian/__tests__/integration.test.ts

describe('Guardian Integration', () => {
  let safetyLayer: SafetyLayer;
  let agent: TestAgent;

  beforeEach(() => {
    safetyLayer = new SafetyLayer();
    agent = new TestAgent({
      id: 'test-agent',
      typeId: 'test',
      categoryId: 'test',
      modelFamily: 'test',
      defaultParams: {},
      inputTopics: [],
      outputTopic: 'test',
      minExamples: 1,
      requiresWorldModel: false,
    });
  });

  it('should intercept unsafe actions', async () => {
    // Assign guardian
    safetyLayer.assignGuardian(agent.id);

    // Try unsafe action
    const result = safetyLayer.checkActionWithGuardian(
      agent.id,
      { type: 'deleteEverything' }
    );

    expect(result.passed).toBe(false);
    expect(result.blockedBy).toBe('guardian');
  });

  it('should allow safe actions', async () => {
    // Assign guardian
    safetyLayer.assignGuardian(agent.id);

    // Try safe action
    const result = safetyLayer.checkActionWithGuardian(
      agent.id,
      { type: 'read', resource: 'test.txt' }
    );

    expect(result.passed).toBe(true);
  });

  it('should modify unsafe but fixable actions', async () => {
    // Assign guardian
    safetyLayer.assignGuardian(agent.id);

    // Try resource-intensive action
    const result = safetyLayer.checkActionWithGuardian(
      agent.id,
      { type: 'compute', resourceLimit: 10000 }
    );

    // Should be modified to use less resources
    expect(result.passed).toBe(true);
  });
});
```

#### Performance Tests

```typescript
// File: src/core/guardian/__tests__/performance.test.ts

describe('Guardian Performance', () => {
  it('should add minimal latency', async () => {
    const guardian = new GuardianAngelAgent(mockConfig);
    const proposal: ActionProposal = {
      id: 'test',
      agentId: 'test',
      actionType: 'test',
      action: {},
      context: {},
      timestamp: Date.now(),
    };

    const start = Date.now();
    await guardian.reviewProposal(proposal);
    const latency = Date.now() - start;

    expect(latency).toBeLessThan(50); // Less than 50ms
  });

  it('should handle high throughput', async () => {
    const guardian = new GuardianAngelAgent(mockConfig);
    const proposals = Array(100).fill(null).map((_, i) => ({
      id: `test-${i}`,
      agentId: 'test',
      actionType: 'test',
      action: {},
      context: {},
      timestamp: Date.now(),
    }));

    const start = Date.now();
    await Promise.all(proposals.map(p => guardian.reviewProposal(p)));
    const totalTime = Date.now() - start;

    expect(totalTime / 100).toBeLessThan(20); // Average < 20ms per proposal
  });
});
```

---

### 1.6 Risk Assessment

#### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Performance degradation** | Medium | High | - Async processing<br>- Caching constraint results<br>- Optimizing rule execution |
| **False positive rate too high** | High | Medium | - Learning system adaptation<br>- User feedback integration<br>- Tunable thresholds |
| **False negative rate too high** | Low | Critical | - Conservative defaults<br>- Multiple constraint layers<br>- Human-in-the-loop review |
| **Guardian bypass** | Low | Critical | - Deep integration with agent lifecycle<br>- Cannot be disabled by agents<br>- Audit logging |

#### Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Over-blocking legitimate actions** | Medium | Medium | - Gradual rollout<br>- A/B testing<br>- User override mechanism |
| **Learning from bad feedback** | Medium | Low | - Validate feedback sources<br>- Rate limit learning<br>- Manual review triggers |
| **Emergency stop false triggers** | Low | High | - High threshold for emergency<br>- Multiple confirmations<br>- Quick recovery mechanism |

#### Mitigation Strategies

1. **Gradual Rollout**
   - Start in read-only mode (log only, no blocking)
   - Gradually increase enforcement
   - Monitor metrics closely

2. **A/B Testing**
   - Compare with/without guardian
   - Measure impact on safety and performance
   - Iterate based on results

3. **Human Oversight**
   - Regular audit of guardian decisions
   - Override mechanism for emergencies
   - Feedback loop for learning

4. **Monitoring & Alerting**
   - Track guardian performance metrics
   - Alert on unusual patterns
   - Regular review meetings

---

## 2. Stigmergic Coordination Pattern

### 2.1 Pattern Overview

**Novelty Score:** 7/10
**Implementation Complexity:** Medium
**Estimated Effort:** 3-4 weeks
**Priority:** HIGH (Enables scalability)

**Key Insight:** Virtual pheromone fields for agent coordination, inspired by ant colony optimization. Agents deposit and sense pheromones in a shared environment, enabling self-organizing behavior without direct communication.

**Why Build Second:**
- Enables scalable coordination (critical for large agent colonies)
- Builds on existing `PathwayState` infrastructure in `types.ts`
- Lower complexity than Guardian Angel
- Enables other patterns (e.g., Overnight Evolution)

---

### 2.2 Implementation Roadmap

#### Phase 1: Pheromone Field Foundation (Week 1)
**Goal:** Implement core pheromone field data structure

**Steps:**
1. Create `src/core/stigmergy/pheromone.ts`
2. Implement spatial indexing for efficient queries
3. Add pheromone deposition and sensing
4. Implement evaporation logic
5. Create pheromone type system

**Deliverables:**
- `PheromoneField` class
- Spatial indexing (grid-based)
- Basic deposit/sense/evaporate operations
- Unit tests

**Acceptance Criteria:**
- Can deposit pheromones at locations
- Can sense pheromones in radius
- Evaporation works correctly
- Performance acceptable for 1000+ pheromones

---

#### Phase 2: Stigmergic Agent Integration (Week 1-2)
**Goal:** Integrate pheromone field with existing agents

**Steps:**
1. Extend `BaseAgent` with pheromone sensing
2. Add pheromone deposition methods
3. Create stigmergic decision logic
4. Integrate with existing `PathwayState`
5. Add pheromone-based routing

**Deliverables:**
- `StigmergicAgent` mixin/extension
- Pheromone-aware routing
- Integration with pathway strength
- Integration tests

**Acceptance Criteria:**
- Agents can deposit pheromones
- Agents can sense and follow pheromones
- Pathway strength and pheromones linked

---

#### Phase 3: Coordination Primitives (Week 2)
**Goal:** Implement common coordination patterns

**Steps:**
1. Task allocation via pheromones
2. Path formation and optimization
3. Resource discovery
4. Danger zone marking
5. Load balancing

**Deliverables:**
- `StigmergicTaskAllocator` class
- `StigmergicPathFormation` class
- Standard coordination patterns
- Examples and documentation

**Acceptance Criteria:**
- Tasks automatically allocated to idle agents
- Optimal paths emerge from pheromone trails
- Resources discovered via pheromone gradients

---

#### Phase 4: Integration with Existing Systems (Week 2-3)
**Goal:** Integrate with existing POLLN components

**Steps:**
1. Link with `HebbianLearning` (synapse strength = pheromone)
2. Integrate with `PlinkoLayer` (pheromone influences selection)
3. Connect to `ResourceAllocation` (pheromones guide resources)
4. Add safety layer integration (DANGER pheromones)
5. Create monitoring dashboard

**Deliverables:**
- Full integration with core systems
- Pheromone visualizations
- Performance metrics
- Integration tests

**Acceptance Criteria:**
- Pheromones work with all core systems
- Visualizations show pheromone fields
- Performance impact minimal

---

#### Phase 5: Testing & Optimization (Week 3-4)
**Goal:** Comprehensive testing and optimization

**Steps:**
1. Performance testing (scale to 10k+ pheromones)
2. Simulation testing (emergent behavior)
3. Optimization of spatial indexing
4. Memory optimization
5. Documentation

**Deliverables:**
- Performance benchmarks
- Simulation results
- Optimized implementation
- Complete documentation

**Acceptance Criteria:**
- Handles 10k+ pheromones efficiently
- Emergent behavior demonstrated
- Memory usage reasonable
- Documentation complete

---

### 2.3 Code Skeleton

#### File: `src/core/stigmergy/types.ts`

```typescript
/**
 * Stigmergic Coordination Types
 * Virtual pheromones for agent coordination
 */

/**
 * Pheromone types
 */
export enum PheromoneType {
  SUCCESS = 'success',           // Positive reinforcement
  DANGER = 'danger',             // Negative reinforcement
  RESOURCE = 'resource',         // Resource availability
  TASK = 'task',                 // Pending work
  PATH = 'path',                 // Route marker
  EXPLORATION = 'exploration',   // Exploration marker
}

/**
 * Spatial location (2D for simplicity, can extend to 3D)
 */
export interface Location {
  x: number;
  y: number;
  z?: number;
}

/**
 * Pheromone deposit
 */
export interface PheromoneDeposit {
  id: string;
  location: Location;
  type: PheromoneType;
  concentration: number;         // 0-1
  depositedBy: string;           // Agent ID
  depositedAt: number;           // Timestamp
  decayRate: number;             // Evaporation rate
}

/**
 * Pheromone reading
 */
export interface PheromoneReading {
  type: PheromoneType;
  concentration: number;
  direction?: Location;          // Gradient direction
  distance?: number;             // Distance to nearest
}

/**
 * Pheromone sense result
 */
export interface SenseResult {
  location: Location;
  radius: number;
  pheromones: Map<PheromoneType, PheromoneReading>;
  gradient: Map<PheromoneType, Location>;
}

/**
 * Pheromone field configuration
 */
export interface PheromoneFieldConfig {
  gridSize: number;              // Spatial grid size
  decayRate: number;             // Default decay rate
  maxConcentration: number;      // Max concentration (0-1)
  evaporationInterval: number;   // Evaporation tick interval (ms)
}

/**
 * Stigmergic agent configuration
 */
export interface StigmergicAgentConfig {
  senseRadius: number;           // How far to sense
  depositStrength: number;       // How much to deposit
  pheromoneTypes: PheromoneType[]; // Types to use
  followGradient: boolean;       // Whether to follow gradients
}

/**
 * Task for stigmergic allocation
 */
export interface StigmergicTask {
  id: string;
  type: string;
  location: Location;
  priority: number;
  requiredPheromone: PheromoneType;
  createdAt: number;
}

/**
 * Path for stigmergic routing
 */
export interface StigmergicPath {
  id: string;
  start: Location;
  end: Location;
  waypoints: Location[];
  strength: number;
  type: PheromoneType;
}
```

#### File: `src/core/stigmergy/pheromone-field.ts`

```typescript
/**
 * Pheromone Field Implementation
 * Virtual pheromones for agent coordination
 */

import { v4 as uuidv4 } from 'uuid';
import type {
  Location,
  PheromoneDeposit,
  PheromoneType,
  PheromoneFieldConfig,
  SenseResult,
} from './types';

/**
 * PheromoneField - Spatial field of virtual pheromones
 *
 * Inspired by ant colony optimization, this enables agents to
 * coordinate through environmental deposits rather than direct
 * communication.
 */
export class PheromoneField {
  private config: PheromoneFieldConfig;
  private deposits: Map<string, PheromoneDeposit> = new Map();
  private spatialIndex: Map<string, string[]> = new Map(); // Grid cell -> deposit IDs
  private evaporationTimer?: NodeJS.Timeout;

  constructor(config?: Partial<PheromoneFieldConfig>) {
    this.config = {
      gridSize: 1.0,
      decayRate: 0.01,
      maxConcentration: 1.0,
      evaporationInterval: 1000,
      ...config,
    };

    // Start evaporation loop
    this.startEvaporation();
  }

  /**
   * Deposit pheromone at location
   */
  deposit(
    location: Location,
    type: PheromoneType,
    concentration: number,
    agentId: string
  ): string {
    // Cap concentration
    concentration = Math.min(concentration, this.config.maxConcentration);

    // Get grid cell
    const gridKey = this.locationToGrid(location);

    // Check for existing deposit at this location
    const existingId = this.findDepositAtLocation(location, type);
    let deposit: PheromoneDeposit;

    if (existingId) {
      // Accumulate with existing
      deposit = this.deposits.get(existingId)!;
      deposit.concentration = Math.min(
        this.config.maxConcentration,
        deposit.concentration + concentration
      );
      deposit.depositedAt = Date.now();
      deposit.depositedBy = agentId;
    } else {
      // Create new deposit
      const id = uuidv4();
      deposit = {
        id,
        location,
        type,
        concentration,
        depositedBy: agentId,
        depositedAt: Date.now(),
        decayRate: this.config.decayRate,
      };

      this.deposits.set(id, deposit);

      // Update spatial index
      if (!this.spatialIndex.has(gridKey)) {
        this.spatialIndex.set(gridKey, []);
      }
      this.spatialIndex.get(gridKey)!.push(id);
    }

    return deposit.id;
  }

  /**
   * Sense pheromones at location within radius
   */
  sense(location: Location, radius: number, type?: PheromoneType): SenseResult {
    const nearby = this.findNearbyDeposits(location, radius, type);

    // Aggregate by pheromone type
    const pheromones = new Map<PheromoneType, import('./types').PheromoneReading>();
    const gradient = new Map<PheromoneType, Location>();

    // Group by type
    const byType = new Map<PheromoneType, PheromoneDeposit[]>();
    for (const deposit of nearby) {
      if (!byType.has(deposit.type)) {
        byType.set(deposit.type, []);
      }
      byType.get(deposit.type)!.push(deposit);
    }

    // Compute readings for each type
    for (const [pheromoneType, deposits] of byType) {
      // Aggregate concentration
      const totalConcentration = deposits.reduce((sum, d) => sum + d.concentration, 0);
      const avgConcentration = totalConcentration / deposits.length;

      // Find nearest
      let nearest = deposits[0];
      let minDistance = this.distance(location, deposits[0].location);
      for (const deposit of deposits) {
        const dist = this.distance(location, deposit.location);
        if (dist < minDistance) {
          minDistance = dist;
          nearest = deposit;
        }
      }

      // Compute gradient direction
      const gradientDirection = this.computeGradient(location, deposits);

      pheromones.set(pheromoneType, {
        type: pheromoneType,
        concentration: avgConcentration,
        direction: gradientDirection,
        distance: minDistance,
      });

      gradient.set(pheromoneType, gradientDirection);
    }

    return {
      location,
      radius,
      pheromones,
      gradient,
    };
  }

  /**
   * Get pheromone gradient for a type at location
   */
  getGradient(location: Location, type: PheromoneType): Location {
    const nearby = this.findNearbyDeposits(location, this.config.gridSize * 2, type);

    if (nearby.length === 0) {
      return { x: 0, y: 0 };
    }

    return this.computeGradient(location, nearby);
  }

  /**
   * Compute gradient direction towards pheromones
   */
  private computeGradient(location: Location, deposits: PheromoneDeposit[]): Location {
    if (deposits.length === 0) {
      return { x: 0, y: 0 };
    }

    // Compute weighted sum of vectors
    let gradientX = 0;
    let gradientY = 0;

    for (const deposit of deposits) {
      const dx = deposit.location.x - location.x;
      const dy = deposit.location.y - location.y;
      const distance = Math.sqrt(dx * dx + dy * dy) + 0.001;

      // Weight by concentration and inverse distance
      const weight = deposit.concentration / distance;

      gradientX += dx * weight;
      gradientY += dy * weight;
    }

    // Normalize
    const magnitude = Math.sqrt(gradientX * gradientX + gradientY * gradientY);
    if (magnitude > 0) {
      gradientX /= magnitude;
      gradientY /= magnitude;
    }

    return { x: gradientX, y: gradientY };
  }

  /**
   * Find deposits near location
   */
  private findNearbyDeposits(
    location: Location,
    radius: number,
    type?: PheromoneType
  ): PheromoneDeposit[] {
    const nearby: PheromoneDeposit[] = [];

    // Check grid cells in range
    const gridRadius = Math.ceil(radius / this.config.gridSize);
    const centerGrid = this.locationToGrid(location);
    const [centerX, centerY] = centerGrid.split(',').map(Number);

    for (let dx = -gridRadius; dx <= gridRadius; dx++) {
      for (let dy = -gridRadius; dy <= gridRadius; dy++) {
        const gridKey = `${centerX + dx},${centerY + dy}`;
        const depositIds = this.spatialIndex.get(gridKey);

        if (depositIds) {
          for (const id of depositIds) {
            const deposit = this.deposits.get(id);
            if (deposit && (!type || deposit.type === type)) {
              const distance = this.distance(location, deposit.location);
              if (distance <= radius) {
                nearby.push(deposit);
              }
            }
          }
        }
      }
    }

    return nearby;
  }

  /**
   * Find existing deposit at location
   */
  private findDepositAtLocation(location: Location, type: PheromoneType): string | null {
    const gridKey = this.locationToGrid(location);
    const depositIds = this.spatialIndex.get(gridKey);

    if (!depositIds) return null;

    for (const id of depositIds) {
      const deposit = this.deposits.get(id);
      if (deposit && deposit.type === type) {
        const distance = this.distance(location, deposit.location);
        if (distance < 0.1) { // Very close
          return id;
        }
      }
    }

    return null;
  }

  /**
   * Evaporate all pheromones
   */
  evaporate(): void {
    const now = Date.now();
    const toRemove: string[] = [];

    for (const [id, deposit] of this.deposits) {
      // Time-based decay
      const age = (now - deposit.depositedAt) / 1000; // seconds
      const decay = 1 - Math.exp(-deposit.decayRate * age);

      deposit.concentration *= (1 - decay);

      // Remove weak pheromones
      if (deposit.concentration < 0.01) {
        toRemove.push(id);
      }
    }

    // Cleanup
    for (const id of toRemove) {
      this.removeDeposit(id);
    }
  }

  /**
   * Remove deposit
   */
  private removeDeposit(id: string): void {
    const deposit = this.deposits.get(id);
    if (deposit) {
      const gridKey = this.locationToGrid(deposit.location);
      const cell = this.spatialIndex.get(gridKey);
      if (cell) {
        const index = cell.indexOf(id);
        if (index > -1) {
          cell.splice(index, 1);
        }
      }
      this.deposits.delete(id);
    }
  }

  /**
   * Start evaporation loop
   */
  private startEvaporation(): void {
    this.evaporationTimer = setInterval(() => {
      this.evaporate();
    }, this.config.evaporationInterval);
  }

  /**
   * Stop evaporation loop
   */
  stopEvaporation(): void {
    if (this.evaporationTimer) {
      clearInterval(this.evaporationTimer);
      this.evaporationTimer = undefined;
    }
  }

  /**
   * Convert location to grid key
   */
  private locationToGrid(location: Location): string {
    const gx = Math.floor(location.x / this.config.gridSize);
    const gy = Math.floor(location.y / this.config.gridSize);
    return `${gx},${gy}`;
  }

  /**
   * Distance between two locations
   */
  private distance(a: Location, b: Location): number {
    const dx = a.x - b.x;
    const dy = a.y - b.y;
    const dz = (a.z || 0) - (b.z || 0);
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }

  /**
   * Get statistics
   */
  getStats(): {
    totalDeposits: number;
    byType: Record<string, number>;
    avgConcentration: number;
  } {
    const byType: Record<string, number> = {};
    let totalConcentration = 0;

    for (const deposit of this.deposits.values()) {
      byType[deposit.type] = (byType[deposit.type] || 0) + 1;
      totalConcentration += deposit.concentration;
    }

    return {
      totalDeposits: this.deposits.size,
      byType,
      avgConcentration: this.deposits.size > 0
        ? totalConcentration / this.deposits.size
        : 0,
    };
  }

  /**
   * Clear all pheromones
   */
  clear(): void {
    this.deposits.clear();
    this.spatialIndex.clear();
  }
}
```

#### File: `src/core/stigmergy/stigmergic-agent.ts`

```typescript
/**
 * Stigmergic Agent Mixin
 * Adds pheromone sensing and deposition to agents
 */

import type { BaseAgent } from '../agent';
import type {
  Location,
  PheromoneType,
  PheromoneDeposit,
  SenseResult,
  StigmergicAgentConfig,
} from './types';
import { PheromoneField } from './pheromone-field';

/**
 * StigmergicAgent - Mixin for pheromone-based coordination
 *
 * Extends BaseAgent with pheromone sensing and deposition capabilities
 */
export function StigmergicAgent<TBase extends new (...args: any[]) => BaseAgent>(
  Base: TBase,
  config: StigmergicAgentConfig
) {
  return class extends Base {
    private pheromoneField: PheromoneField;
    private stigmergicConfig: StigmergicAgentConfig;
    private location: Location;

    constructor(...args: any[]) {
      super(...args);
      this.pheromoneField = args[0]?.pheromoneField || new PheromoneField();
      this.stigmergicConfig = config;
      this.location = { x: 0, y: 0 }; // Default location
    }

    /**
     * Sense pheromones in environment
     */
    sensePheromones(radius?: number, type?: PheromoneType): SenseResult {
      const senseRadius = radius || this.stigmergicConfig.senseRadius;
      return this.pheromoneField.sense(this.location, senseRadius, type);
    }

    /**
     * Deposit pheromone at current location
     */
    depositPheromone(
      type: PheromoneType,
      concentration?: number
    ): string {
      const strength = concentration || this.stigmergicConfig.depositStrength;
      return this.pheromoneField.deposit(
        this.location,
        type,
        strength,
        this.id
      );
    }

    /**
     * Follow pheromone gradient
     */
    followPheromoneGradient(type: PheromoneType): Location {
      const gradient = this.pheromoneField.getGradient(this.location, type);

      // Move in direction of gradient
      const stepSize = 0.1;
      return {
        x: this.location.x + gradient.x * stepSize,
        y: this.location.y + gradient.y * stepSize,
        z: this.location.z,
      };
    }

    /**
     * Move to new location
     */
    moveTo(location: Location): void {
      this.location = location;
    }

    /**
     * Get current location
     */
    getLocation(): Location {
      return this.location;
    }

    /**
     * Process with stigmergic awareness
     *
     * Extends base process() to include pheromone operations
     */
    async processWithStigmergy<T>(input: T): Promise<any> {
      // Sense environment
      const senseResult = this.sensePheromones();

      // Deposit task pheromone if we're working
      if (this.state.get('busy')) {
        this.depositPheromone(PheromoneType.TASK, 0.5);
      }

      // Call base process
      const result = await super.process(input);

      // Deposit success/failure pheromone
      if (result.success) {
        this.depositPheromone(PheromoneType.SUCCESS, 0.8);
      } else {
        this.depositPheromone(PheromoneType.DANGER, 0.3);
      }

      return result;
    }
  };
}
```

#### File: `src/core/stigmergy/task-allocator.ts`

```typescript
/**
 * Stigmergic Task Allocator
 * Self-organizing task allocation via pheromones
 */

import type { StigmergicTask, Location, PheromoneType } from './types';
import { PheromoneField } from './pheromone-field';

/**
 * StigmergicTaskAllocator - Allocate tasks via pheromone gradients
 *
 * Tasks are posted to the environment as TASK pheromones.
 * Idle agents naturally follow the gradient to find work.
 */
export class StigmergicTaskAllocator {
  private pheromoneField: PheromoneField;
  private tasks: Map<string, StigmergicTask> = new Map();

  constructor(pheromoneField: PheromoneField) {
    this.pheromoneField = pheromoneField;
  }

  /**
   * Post task to environment
   *
   * Deposits TASK pheromone at task location
   */
  postTask(task: StigmergicTask): void {
    // Store task
    this.tasks.set(task.id, task);

    // Deposit TASK pheromone
    // Higher priority = higher concentration
    const concentration = 0.5 + (task.priority * 0.5);
    this.pheromoneField.deposit(
      task.location,
      PheromoneType.TASK,
      concentration,
      'system'
    );

    // Also deposit type-specific marker
    this.pheromoneField.deposit(
      task.location,
      task.requiredPheromone,
      concentration * 0.8,
      'system'
    );
  }

  /**
   * Agent picks up task
   *
   * Reduces TASK pheromone concentration to signal work in progress
   */
  pickUpTask(agentId: string, task: StigmergicTask): void {
    // Decrease TASK pheromone concentration
    const nearby = this.pheromoneField.sense(task.location, 1.0, PheromoneType.TASK);
    const taskPheromones = nearby.pheromones.get(PheromoneType.TASK);

    if (taskPheromones && taskPheromones.concentration > 0) {
      // Reduce concentration to half
      this.pheromoneField.deposit(
        task.location,
        PheromoneType.TASK,
        -taskPheromones.concentration * 0.5,
        agentId
      );
    }
  }

  /**
   * Agent completes task
   *
   * Clears TASK pheromone, deposits SUCCESS pheromone
   */
  completeTask(agentId: string, task: StigmergicTask, success: boolean): void {
    // Clear TASK pheromone
    const nearby = this.pheromoneField.sense(task.location, 1.0, PheromoneType.TASK);

    // Clear TASK pheromone by depositing negative
    for (const [type, reading] of nearby.pheromones) {
      if (type === PheromoneType.TASK) {
        this.pheromoneField.deposit(
          task.location,
          type,
          -reading.concentration,
          agentId
        );
      }
    }

    // Deposit outcome pheromone
    if (success) {
      // Success trail - reinforces this location for similar tasks
      this.pheromoneField.deposit(
        task.location,
        PheromoneType.SUCCESS,
        0.7,
        agentId
      );
      this.pheromoneField.deposit(
        task.location,
        task.requiredPheromone,
        0.5,
        agentId
      );
    } else {
      // Danger zone - discourages this location
      this.pheromoneField.deposit(
        task.location,
        PheromoneType.DANGER,
        0.5,
        agentId
      );
    }

    // Remove task
    this.tasks.delete(task.id);
  }

  /**
   * Get nearby tasks for an agent
   *
   * Agents use this to discover tasks via pheromone gradient
   */
  getNearbyTasks(location: Location, radius: number): StigmergicTask[] {
    const nearby: StigmergicTask[] = [];

    for (const task of this.tasks.values()) {
      const distance = this.distance(location, task.location);
      if (distance <= radius) {
        nearby.push(task);
      }
    }

    // Sort by priority
    return nearby.sort((a, b) => b.priority - a.priority);
  }

  /**
   * Get task statistics
   */
  getStats(): {
    totalTasks: number;
    pendingTasks: number;
    byType: Record<string, number>;
  } {
    const byType: Record<string, number> = {};

    for (const task of this.tasks.values()) {
      byType[task.type] = (byType[task.type] || 0) + 1;
    }

    return {
      totalTasks: this.tasks.size,
      pendingTasks: this.tasks.size,
      byType,
    };
  }

  /**
   * Distance between locations
   */
  private distance(a: Location, b: Location): number {
    const dx = a.x - b.x;
    const dy = a.y - b.y;
    const dz = (a.z || 0) - (b.z || 0);
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }
}
```

#### File: `src/core/stigmergy/path-formation.ts`

```typescript
/**
 * Stigmergic Path Formation
 * Self-organizing path optimization via pheromones
 */

import type { Location, StigmergicPath, PheromoneType } from './types';
import { PheromoneField } from './pheromone-field';

/**
 * StigmergicPathFormation - Optimize paths through pheromone trails
 *
 * Agents deposit PATH pheromones along routes they take.
 * Over time, optimal paths emerge as pheromone concentrations
 * reflect route quality.
 */
export class StigmergicPathFormation {
  private pheromoneField: PheromoneField;
  private paths: Map<string, StigmergicPath> = new Map();

  constructor(pheromoneField: PheromoneField) {
    this.pheromoneField = pheromoneField;
  }

  /**
   * Agent marks path they took
   *
   * Deposits PATH pheromone along route
   */
  markPath(
    agentId: string,
    path: Location[],
    quality: number,
    type: PheromoneType = PheromoneType.PATH
  ): string {
    const pathId = `${agentId}-${Date.now()}`;

    // Deposit pheromone along path
    for (const location of path) {
      // Concentration based on quality
      const concentration = quality * 0.2;
      this.pheromoneField.deposit(location, type, concentration, agentId);
    }

    // Store path
    this.paths.set(pathId, {
      id: pathId,
      start: path[0],
      end: path[path.length - 1],
      waypoints: path,
      strength: quality,
      type,
    });

    return pathId;
  }

  /**
   * Agent follows existing path
   *
   * Returns next location along pheromone gradient
   */
  followPath(currentLocation: Location, type: PheromoneType = PheromoneType.PATH): Location {
    // Get gradient of PATH pheromone
    const gradient = this.pheromoneField.getGradient(currentLocation, type);

    // Move in direction of gradient
    const stepSize = 0.1;
    return {
      x: currentLocation.x + gradient.x * stepSize,
      y: currentLocation.y + gradient.y * stepSize,
      z: currentLocation.z,
    };
  }

  /**
   * Optimize paths through evaporation
   *
   * Poor paths evaporate faster, good paths persist
   */
  optimizePaths(): void {
    // Natural evaporation handles optimization
    // High-quality paths get reinforced, low-quality fade away
    this.pheromoneField.evaporate();
  }

  /**
   * Get best path between locations
   */
  getBestPath(start: Location, end: Location, type: PheromoneType = PheromoneType.PATH): StigmergicPath | null {
    // Find paths that connect these points
    const candidates: StigmergicPath[] = [];

    for (const path of this.paths.values()) {
      if (path.type === type) {
        const distToStart = this.distance(start, path.start);
        const distToEnd = this.distance(end, path.end);

        if (distToStart < 1.0 && distToEnd < 1.0) {
          candidates.push(path);
        }
      }
    }

    if (candidates.length === 0) return null;

    // Return strongest path
    return candidates.sort((a, b) => b.strength - a.strength)[0];
  }

  /**
   * Get path statistics
   */
  getStats(): {
    totalPaths: number;
    avgStrength: number;
    byType: Record<string, number>;
  } {
    const byType: Record<string, number> = {};
    let totalStrength = 0;

    for (const path of this.paths.values()) {
      byType[path.type] = (byType[path.type] || 0) + 1;
      totalStrength += path.strength;
    }

    return {
      totalPaths: this.paths.size,
      avgStrength: this.paths.size > 0 ? totalStrength / this.paths.size : 0,
      byType,
    };
  }

  /**
   * Distance between locations
   */
  private distance(a: Location, b: Location): number {
    const dx = a.x - b.x;
    const dy = a.y - b.y;
    const dz = (a.z || 0) - (b.z || 0);
    return Math.sqrt(dx * dx + dy * dy + dz * dz);
  }
}
```

---

### 2.4 Integration Points

#### Integration with HebbianLearning

```typescript
// File: src/core/learning.ts (extend existing)

import { PheromoneField } from './stigmergy/pheromone-field';
import type { PathwayState } from './types';

export class HebbianLearning {
  // ... existing code ...

  /**
   * Link synaptic strength to pheromone concentration
   */
  linkToPheromoneField(pheromoneField: PheromoneField): void {
    // When synapse strengthens, deposit pheromone
    this.on('synapse-strengthened', (data: { sourceId: string; targetId: string; weight: number }) => {
      // Create location from agent IDs (hash-based)
      const location = this.agentIdsToLocation(data.sourceId, data.targetId);

      // Deposit SUCCESS pheromone proportional to weight
      const concentration = data.weight * 0.5;
      pheromoneField.deposit(location, PheromoneType.SUCCESS, concentration, data.sourceId);
    });

    // When synapse weakens, deposit DANGER pheromone
    this.on('synapse-weakened', (data: { sourceId: string; targetId: string; weight: number }) => {
      const location = this.agentIdsToLocation(data.sourceId, data.targetId);

      // Deposit DANGER pheromone
      const concentration = (1 - data.weight) * 0.3;
      pheromoneField.deposit(location, PheromoneType.DANGER, concentration, data.sourceId);
    });
  }

  /**
   * Convert agent IDs to location
   */
  private agentIdsToLocation(sourceId: string, targetId: string): Location {
    // Hash-based mapping
    const hash = (s: string) => {
      let h = 0;
      for (let i = 0; i < s.length; i++) {
        h = Math.sin(h + s.charCodeAt(i)) * 10000;
        h -= Math.floor(h);
      }
      return h;
    };

    return {
      x: hash(sourceId) * 100,
      y: hash(targetId) * 100,
    };
  }

  /**
   * Update from pheromone reading
   */
  updateFromPheromone(
    sourceId: string,
    targetId: string,
    pheromoneReading: import('./stigmergy/types').PheromoneReading
  ): void {
    // Adjust synapse based on pheromone
    const key = `${sourceId}->${targetId}`;
    const synapse = this.synapses.get(key);

    if (synapse) {
      if (pheromoneReading.type === PheromoneType.SUCCESS) {
        // Strengthen synapse
        synapse.weight = Math.min(1.0, synapse.weight + pheromoneReading.concentration * 0.1);
      } else if (pheromoneReading.type === PheromoneType.DANGER) {
        // Weaken synapse
        synapse.weight = Math.max(0.01, synapse.weight - pheromoneReading.concentration * 0.1);
      }
    }
  }
}
```

#### Integration with PlinkoLayer

```typescript
// File: src/core/decision.ts (extend existing)

import { PheromoneField } from './stigmergy/pheromone-field';
import type { PheromoneType } from './stigmergy/types';

export class PlinkoLayer {
  // ... existing code ...

  /**
   * Incorporate pheromone strength into bids
   */
  async processWithPheromones(
    proposals: AgentProposal[],
    pheromoneField: PheromoneField
  ): Promise<PlinkoResult> {
    // Adjust bids based on pheromone concentration
    const adjustedProposals = proposals.map(proposal => {
      // Get agent location (hash-based)
      const location = this.agentIdToLocation(proposal.agentId);

      // Sense pheromones
      const senseResult = pheromoneField.sense(location, 5.0);

      // Boost confidence based on SUCCESS pheromone
      const successPheromone = senseResult.pheromones.get(PheromoneType.SUCCESS);
      if (successPheromone) {
        proposal.confidence *= (1 + successPheromone.concentration * 0.5);
      }

      // Reduce confidence based on DANGER pheromone
      const dangerPheromone = senseResult.pheromones.get(PheromoneType.DANGER);
      if (dangerPheromone) {
        proposal.confidence *= (1 - dangerPheromone.concentration * 0.5);
      }

      return proposal;
    });

    // Process with adjusted proposals
    return this.process(adjustedProposals);
  }

  /**
   * Convert agent ID to location
   */
  private agentIdToLocation(agentId: string): Location {
    const hash = (s: string) => {
      let h = 0;
      for (let i = 0; i < s.length; i++) {
        h = Math.sin(h + s.charCodeAt(i)) * 10000;
        h -= Math.floor(h);
      }
      return h;
    };

    return {
      x: hash(agentId) * 100,
      y: hash(agentId + 'y') * 100,
    };
  }
}
```

#### Integration with Resource Allocation

```typescript
// File: src/core/colony.ts (extend existing)

import { PheromoneField } from './stigmergy/pheromone-field';
import type { PheromoneType } from './stigmergy/types';

export class Colony {
  // ... existing code ...

  /**
   * Allocate resources based on pheromone gradients
   */
  allocateResourcesByPheromones(
    pheromoneField: PheromoneField,
    totalResources: number
  ): Map<string, number> {
    const allocation = new Map<string, number>();
    let totalWeight = 0;

    // Calculate weights based on pheromone concentrations
    for (const agent of this.agents.values()) {
      const location = this.agentIdToLocation(agent.id);
      const senseResult = pheromoneField.sense(location, 5.0);

      // Weight by TASK and SUCCESS pheromones
      let weight = 1.0;
      const taskPheromone = senseResult.pheromones.get(PheromoneType.TASK);
      const successPheromone = senseResult.pheromones.get(PheromoneType.SUCCESS);

      if (taskPheromone) {
        weight += taskPheromone.concentration * 2.0;
      }
      if (successPheromone) {
        weight += successPheromone.concentration;
      }

      // Reduce by DANGER pheromone
      const dangerPheromone = senseResult.pheromones.get(PheromoneType.DANGER);
      if (dangerPheromone) {
        weight *= (1 - dangerPheromone.concentration);
      }

      allocation.set(agent.id, weight);
      totalWeight += weight;
    }

    // Normalize to total resources
    for (const [agentId, weight] of allocation) {
      allocation.set(agentId, (weight / totalWeight) * totalResources);
    }

    return allocation;
  }
}
```

---

### 2.5 Testing Strategy

#### Unit Tests

```typescript
// File: src/core/stigmergy/__tests__/pheromone-field.test.ts

describe('PheromoneField', () => {
  let field: PheromoneField;

  beforeEach(() => {
    field = new PheromoneField({
      gridSize: 1.0,
      decayRate: 0.01,
      maxConcentration: 1.0,
      evaporationInterval: 100,
    });
  });

  afterEach(() => {
    field.stopEvaporation();
  });

  describe('deposit', () => {
    it('should deposit pheromone at location', () => {
      const id = field.deposit(
        { x: 0, y: 0 },
        PheromoneType.SUCCESS,
        0.5,
        'agent1'
      );

      expect(id).toBeDefined();

      const stats = field.getStats();
      expect(stats.totalDeposits).toBe(1);
    });

    it('should accumulate deposits at same location', () => {
      field.deposit({ x: 0, y: 0 }, PheromoneType.SUCCESS, 0.5, 'agent1');
      field.deposit({ x: 0, y: 0 }, PheromoneType.SUCCESS, 0.3, 'agent1');

      const stats = field.getStats();
      expect(stats.totalDeposits).toBe(1); // Still one deposit
      expect(stats.avgConcentration).toBeGreaterThan(0.5);
    });

    it('should cap concentration at max', () => {
      field.deposit({ x: 0, y: 0 }, PheromoneType.SUCCESS, 1.5, 'agent1');

      const stats = field.getStats();
      expect(stats.avgConcentration).toBeLessThanOrEqual(1.0);
    });
  });

  describe('sense', () => {
    it('should sense pheromones in radius', () => {
      field.deposit({ x: 0, y: 0 }, PheromoneType.SUCCESS, 0.8, 'agent1');

      const result = field.sense({ x: 0.5, y: 0 }, 2.0);

      expect(result.pheromones.size).toBeGreaterThan(0);
      expect(result.pheromones.has(PheromoneType.SUCCESS)).toBe(true);
    });

    it('should not sense pheromones outside radius', () => {
      field.deposit({ x: 0, y: 0 }, PheromoneType.SUCCESS, 0.8, 'agent1');

      const result = field.sense({ x: 10, y: 10 }, 1.0);

      expect(result.pheromones.size).toBe(0);
    });
  });

  describe('evaporate', () => {
    it('should reduce pheromone concentration over time', async () => {
      field.deposit({ x: 0, y: 0 }, PheromoneType.SUCCESS, 1.0, 'agent1');

      const stats1 = field.getStats();
      const initialConcentration = stats1.avgConcentration;

      // Wait for evaporation
      await new Promise(resolve => setTimeout(resolve, 200));
      field.evaporate();

      const stats2 = field.getStats();
      expect(stats2.avgConcentration).toBeLessThan(initialConcentration);
    });

    it('should remove weak pheromones', async () => {
      field.deposit({ x: 0, y: 0 }, PheromoneType.SUCCESS, 0.001, 'agent1');

      // Wait for evaporation
      await new Promise(resolve => setTimeout(resolve, 200));
      field.evaporate();

      const stats = field.getStats();
      expect(stats.totalDeposits).toBe(0);
    });
  });

  describe('getGradient', () => {
    it('should compute gradient towards pheromones', () => {
      field.deposit({ x: 10, y: 0 }, PheromoneType.SUCCESS, 0.8, 'agent1');

      const gradient = field.getGradient({ x: 0, y: 0 }, PheromoneType.SUCCESS);

      expect(gradient.x).toBeGreaterThan(0); // Points towards positive x
    });

    it('should return zero gradient when no pheromones', () => {
      const gradient = field.getGradient({ x: 0, y: 0 }, PheromoneType.SUCCESS);

      expect(gradient.x).toBe(0);
      expect(gradient.y).toBe(0);
    });
  });
});
```

#### Integration Tests

```typescript
// File: src/core/stigmergy/__tests__/integration.test.ts

describe('Stigmergy Integration', () => {
  let pheromoneField: PheromoneField;
  let taskAllocator: StigmergicTaskAllocator;
  let pathFormation: StigmergicPathFormation;

  beforeEach(() => {
    pheromoneField = new PheromoneField();
    taskAllocator = new StigmergicTaskAllocator(pheromoneField);
    pathFormation = new StigmergicPathFormation(pheromoneField);
  });

  describe('Task Allocation', () => {
    it('should allocate tasks via pheromone gradient', () => {
      const task: StigmergicTask = {
        id: 'task1',
        type: 'test',
        location: { x: 10, y: 10 },
        priority: 0.8,
        requiredPheromone: PheromoneType.RESOURCE,
        createdAt: Date.now(),
      };

      taskAllocator.postTask(task);

      // Agent senses pheromones
      const senseResult = pheromoneField.sense({ x: 0, y: 0 }, 20.0);

      expect(senseResult.pheromones.has(PheromoneType.TASK)).toBe(true);
    });

    it('should reduce task pheromone when picked up', () => {
      const task: StigmergicTask = {
        id: 'task1',
        type: 'test',
        location: { x: 10, y: 10 },
        priority: 0.8,
        requiredPheromone: PheromoneType.RESOURCE,
        createdAt: Date.now(),
      };

      taskAllocator.postTask(task);

      const sense1 = pheromoneField.sense(task.location, 1.0);
      const conc1 = sense1.pheromones.get(PheromoneType.TASK)?.concentration || 0;

      taskAllocator.pickUpTask('agent1', task);

      const sense2 = pheromoneField.sense(task.location, 1.0);
      const conc2 = sense2.pheromones.get(PheromoneType.TASK)?.concentration || 0;

      expect(conc2).toBeLessThan(conc1);
    });
  });

  describe('Path Formation', () => {
    it('should form paths through pheromone deposition', () => {
      const path = [
        { x: 0, y: 0 },
        { x: 1, y: 0 },
        { x: 2, y: 0 },
        { x: 3, y: 0 },
      ];

      pathFormation.markPath('agent1', path, 0.9);

      // Check pheromones along path
      for (const location of path) {
        const sense = pheromoneField.sense(location, 0.5);
        expect(sense.pheromones.has(PheromoneType.PATH)).toBe(true);
      }
    });

    it('should optimize paths over time', async () => {
      // Create two paths
      const goodPath = [
        { x: 0, y: 0 },
        { x: 1, y: 0 },
        { x: 2, y: 0 },
      ];

      const badPath = [
        { x: 0, y: 0 },
        { x: 1, y: 1 },
        { x: 2, y: 2 },
        { x: 3, y: 0 },
        { x: 4, y: 0 },
      ];

      // Mark good path frequently
      for (let i = 0; i < 10; i++) {
        pathFormation.markPath('agent1', goodPath, 0.9);
      }

      // Mark bad path rarely
      pathFormation.markPath('agent2', badPath, 0.3);

      // Wait for evaporation
      await new Promise(resolve => setTimeout(resolve, 500));
      pathFormation.optimizePaths();

      // Good path should have stronger pheromones
      const goodSense = pheromoneField.sense({ x: 1, y: 0 }, 0.5);
      const badSense = pheromoneField.sense({ x: 1, y: 1 }, 0.5);

      const goodConc = goodSense.pheromones.get(PheromoneType.PATH)?.concentration || 0;
      const badConc = badSense.pheromones.get(PheromoneType.PATH)?.concentration || 0;

      expect(goodConc).toBeGreaterThan(badConc);
    });
  });
});
```

#### Performance Tests

```typescript
// File: src/core/stigmergy/__tests__/performance.test.ts

describe('Stigmergy Performance', () => {
  it('should handle 10k+ pheromones efficiently', () => {
    const field = new PheromoneField();

    // Deposit 10k pheromones
    const start = Date.now();
    for (let i = 0; i < 10000; i++) {
      field.deposit(
        { x: Math.random() * 100, y: Math.random() * 100 },
        PheromoneType.SUCCESS,
        Math.random(),
        `agent${i % 100}`
      );
    }
    const depositTime = Date.now() - start;

    expect(depositTime).toBeLessThan(1000); // Less than 1 second

    // Sense operations should still be fast
    const senseStart = Date.now();
    const result = field.sense({ x: 50, y: 50 }, 10.0);
    const senseTime = Date.now() - senseStart;

    expect(senseTime).toBeLessThan(10); // Less than 10ms

    field.stopEvaporation();
  });

  it('should maintain performance with evaporation', async () => {
    const field = new PheromoneField({
      evaporationInterval: 100,
    });

    // Deposit 5k pheromones
    for (let i = 0; i < 5000; i++) {
      field.deposit(
        { x: Math.random() * 100, y: Math.random() * 100 },
        PheromoneType.SUCCESS,
        Math.random() * 0.5,
        `agent${i % 100}`
      );
    }

    // Wait for several evaporation cycles
    await new Promise(resolve => setTimeout(resolve, 500));

    // Performance should remain good
    const start = Date.now();
    const result = field.sense({ x: 50, y: 50 }, 10.0);
    const senseTime = Date.now() - start;

    expect(senseTime).toBeLessThan(10);

    field.stopEvaporation();
  });
});
```

---

### 2.6 Risk Assessment

#### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Spatial index performance** | Medium | High | - Optimized grid-based indexing<br>- Adaptive grid sizing<br>- Quadtree for 3D |
| **Memory usage at scale** | Medium | Medium | - Aggressive evaporation<br>- Concentration thresholds<br>- Periodic cleanup |
| **Pheromone interference** | Low | Medium | - Type-based separation<br>- Frequency-based weighting<br>- Spatial decay |
| **Oscillation/instability** | Low | Medium | - Damping factors<br>- Maximum deposition rates<br}- Stochastic perturbation |

#### Operational Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Poor emergent behavior** | Medium | High | - Simulation testing<br}- Parameter tuning<br}- Gradual rollout |
| **Overwhelming strong signals** | Low | Medium | - Saturation limits<br}- Anti-pheromones<br}- Diversity preservation |
| **Debugging difficulty** | High | Low | - Visualization tools<br}- Logging and metrics<br}- Simulation replays |

#### Mitigation Strategies

1. **Gradual Rollout**
   - Start with single pheromone type
   - Add types incrementally
   - Monitor emergent behavior

2. **Simulation Testing**
   - Test in simulated environments
   - Verify emergent behavior
   - Tune parameters

3. **Monitoring**
   - Track pheromone distributions
   - Monitor spatial index performance
   - Alert on unusual patterns

4. **Visualization**
   - Real-time pheromone field visualization
   - Agent movement tracking
   - Gradient heat maps

---

## 3. Implementation Priority and Timeline

### 3.1 Recommended Implementation Order

1. **Guardian Angel Safety Pattern** (Weeks 1-5)
   - Critical for safety
   - Enables safe experimentation
   - Builds trust

2. **Stigmergic Coordination** (Weeks 6-9)
   - Enables scalability
   - Builds on Guardian safety
   - Foundation for other patterns

3. **Future Patterns** (Weeks 10+)
   - Bytecode Bridge (performance)
   - Overnight Evolution (continuous improvement)
   - Edge Optimization (expansion)

### 3.2 Resource Requirements

**Team:**
- 2-3 Full-time developers
- 1 Safety engineer (for Guardian Angel)
- 1 Test engineer
- 1 DevOps engineer (for infrastructure)

**Infrastructure:**
- Development environment
- CI/CD pipeline
- Monitoring and alerting
- Simulation environment

### 3.3 Success Metrics

**Guardian Angel:**
- Intervention rate < 5%
- False positive rate < 1%
- Response time < 50ms
- Zero safety incidents

**Stigmergic Coordination:**
- Task allocation latency < 100ms
- Path optimization convergence < 100 iterations
- Memory usage < 1GB for 10k pheromones
- Agent scalability > 1000 concurrent

---

## 4. Conclusion

This document provides detailed implementation strategies for the top 2 most impactful innovation patterns from Round 4 research:

### 4.1 Guardian Angel Safety Pattern
- **Novel shadow agent approach** to AI safety
- **Veto, modify, or allow** actions based on safety constraints
- **Learns from feedback** to reduce false positives
- **Real-time monitoring** for long-running actions
- **4-5 weeks** to full implementation

### 4.2 Stigmergic Coordination Pattern
- **Virtual pheromone fields** for self-organizing coordination
- **Task allocation, path formation** emerge from simple rules
- **Integrates with existing** Hebbian learning and Plinko decision
- **3-4 weeks** to full implementation

Together, these patterns make POLLN **safer** and **more scalable**, enabling it to grow from prototype to production-ready system.

---

## 5. Next Steps

1. **Review and approval** of implementation strategies
2. **Set up development environment** and CI/CD
3. **Begin Guardian Angel implementation** (Phase 1)
4. **Set up simulation environment** for testing
5. **Establish monitoring and metrics** from day one

---

**Document Status:** COMPLETE
**Next Phase:** Implementation
**Review Date:** After Phase 1 completion

---

*Research Agent:* Research Synthesizer
*Date:* 2026-03-06
*Version:* 1.0.0
*Repository:* https://github.com/SuperInstance/POLLN
