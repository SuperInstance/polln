/**
 * Agent Inspector
 *
 * Provides detailed inspection capabilities for individual agents,
 * including state, call stacks, variables, breakpoints, and metrics.
 */

import type {
  AgentInspection,
  StackFrame,
  BreakpointStatus,
  AgentMetrics,
  A2APackageTrace,
  Breakpoint,
  BreakpointCondition,
  DebugErrorCode,
} from './types.js';
import { DebugError } from './types.js';

// ============================================================================
// AgentInspector Class
// ============================================================================

/**
 * Inspector for detailed agent state and behavior
 */
export class AgentInspector {
  private breakpoints: Map<string, Breakpoint> = new Map();
  private inspectionHistory: Map<string, AgentInspection[]> = new Map();
  private packageHistory: Map<string, A2APackageTrace[]> = new Map();
  private maxHistorySize: number = 1000;

  /**
   * Inspect an agent's current state
   *
   * @param agentId - Agent ID to inspect
   * @param agentInstance - Agent instance
   * @returns Detailed agent inspection
   */
  async inspect(
    agentId: string,
    agentInstance: any
  ): Promise<AgentInspection> {
    if (!agentInstance) {
      throw new DebugError('AGENT_NOT_FOUND', `Agent ${agentId} not found`);
    }

    // Gather agent state
    const state = this.extractState(agentInstance);

    // Gather call stack (simulated for async agents)
    const callStack = this.extractCallStack(agentInstance);

    // Gather local variables
    const variables = this.extractVariables(agentInstance);

    // Get recent A2A packages
    const sentPackages = this.getPackageHistory(agentId, 'sent');
    const receivedPackages = this.getPackageHistory(agentId, 'received');

    // Check breakpoint status
    const breakpointStatus = this.getBreakpointStatus(agentId);

    // Gather metrics
    const metrics = this.extractMetrics(agentInstance);

    // Get category from agent
    const category = agentInstance.categoryId || agentInstance.constructor?.name || 'Unknown';

    const inspection: AgentInspection = {
      agentId,
      category: category as any,
      state,
      callStack,
      variables,
      sentPackages: sentPackages.slice(-10), // Last 10
      receivedPackages: receivedPackages.slice(-10), // Last 10
      breakpointStatus,
      metrics,
      timestamp: Date.now(),
    };

    // Store in history
    this.storeInspection(agentId, inspection);

    return inspection;
  }

  /**
   * Get agent state at a specific point in history
   *
   * @param agentId - Agent ID
   * @param timestamp - Timestamp to retrieve (null for latest)
   * @returns Agent inspection or null if not found
   */
  getHistoricalState(
    agentId: string,
    timestamp: number | null = null
  ): AgentInspection | null {
    const history = this.inspectionHistory.get(agentId);
    if (!history || history.length === 0) {
      return null;
    }

    if (timestamp === null) {
      return history[history.length - 1]; // Latest
    }

    // Find closest inspection to timestamp
    let closest: AgentInspection | null = null;
    let minDiff = Infinity;

    for (const inspection of history) {
      const diff = Math.abs(inspection.timestamp - timestamp);
      if (diff < minDiff) {
        minDiff = diff;
        closest = inspection;
      }
    }

    return closest;
  }

  /**
   * Set a breakpoint on an agent
   *
   * @param condition - Breakpoint condition
   * @returns Breakpoint ID
   */
  setBreakpoint(condition: BreakpointCondition): string {
    const breakpointId = `bp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const breakpoint: Breakpoint = {
      id: breakpointId,
      condition,
      action: { type: 'pause' },
      enabled: true,
      hitCount: 0,
      maxHits: 0,
      createdAt: Date.now(),
    };

    this.breakpoints.set(breakpointId, breakpoint);

    return breakpointId;
  }

  /**
   * Remove a breakpoint
   *
   * @param breakpointId - Breakpoint ID
   */
  removeBreakpoint(breakpointId: string): void {
    if (!this.breakpoints.has(breakpointId)) {
      throw new DebugError('BREAKPOINT_NOT_FOUND', `Breakpoint ${breakpointId} not found`);
    }

    this.breakpoints.delete(breakpointId);
  }

  /**
   * List all breakpoints
   *
   * @param agentId - Optional agent ID filter
   * @returns Array of breakpoints
   */
  listBreakpoints(agentId?: string): Breakpoint[] {
    let breakpoints = Array.from(this.breakpoints.values());

    if (agentId) {
      breakpoints = breakpoints.filter(bp => bp.condition.agentId === agentId);
    }

    return breakpoints;
  }

  /**
   * Check if breakpoint should trigger
   *
   * @param agentId - Agent ID
   * @param currentState - Current agent state
   * @returns Whether breakpoint triggered
   */
  checkBreakpoints(agentId: string, currentState: Record<string, unknown>): boolean {
    for (const breakpoint of Array.from(this.breakpoints.values())) {
      if (!breakpoint.enabled) {
        continue;
      }

      // Check agent filter
      if (breakpoint.condition.agentId && breakpoint.condition.agentId !== agentId) {
        continue;
      }

      // Check if max hits reached
      if (breakpoint.maxHits > 0 && breakpoint.hitCount >= breakpoint.maxHits) {
        continue;
      }

      // Evaluate condition
      if (this.evaluateCondition(breakpoint.condition, currentState)) {
        breakpoint.hitCount++;
        breakpoint.lastHitAt = Date.now();
        return true;
      }
    }

    return false;
  }

  /**
   * Track an A2A package
   *
   * @param packageTrace - Package trace information
   */
  trackPackage(packageTrace: A2APackageTrace): void {
    const agentId = packageTrace.fromAgentId;
    let history = this.packageHistory.get(agentId);

    if (!history) {
      history = [];
      this.packageHistory.set(agentId, history);
    }

    history.push(packageTrace);

    // Enforce max size
    if (history.length > this.maxHistorySize) {
      history.shift();
    }
  }

  /**
   * Get inspection history for an agent
   *
   * @param agentId - Agent ID
   * @param limit - Maximum number of inspections to return
   * @returns Array of inspections
   */
  getInspectionHistory(agentId: string, limit?: number): AgentInspection[] {
    const history = this.inspectionHistory.get(agentId) || [];
    return limit ? history.slice(-limit) : history;
  }

  /**
   * Clear inspection history for an agent
   *
   * @param agentId - Agent ID
   */
  clearHistory(agentId: string): void {
    this.inspectionHistory.delete(agentId);
    this.packageHistory.delete(agentId);
  }

  /**
   * Compare two agent states
   *
   * @param inspection1 - First inspection
   * @param inspection2 - Second inspection
   * @returns Differences between states
   */
  compareStates(
    inspection1: AgentInspection,
    inspection2: AgentInspection
  ): StateDifference[] {
    const differences: StateDifference[] = [];

    // Compare state fields
    const allKeys = new Set([
      ...Object.keys(inspection1.state),
      ...Object.keys(inspection2.state),
    ]);

    for (const key of allKeys) {
      const val1 = inspection1.state[key];
      const val2 = inspection2.state[key];

      if (JSON.stringify(val1) !== JSON.stringify(val2)) {
        differences.push({
          field: key,
          oldValue: val1,
          newValue: val2,
          changeType: val1 === undefined ? 'added' :
                      val2 === undefined ? 'removed' : 'changed',
        });
      }
    }

    return differences;
  }

  // ==========================================================================
  // Private Methods
  // ==========================================================================

  private extractState(agentInstance: any): Record<string, unknown> {
    const state: Record<string, unknown> = {
      id: agentInstance.id,
      typeId: agentInstance.typeId,
      categoryId: agentInstance.categoryId,
      status: agentInstance.status || 'unknown',
    };

    // Extract value function if available
    if (agentInstance.valueFunction !== undefined) {
      state.valueFunction = agentInstance.valueFunction;
    }

    // Extract success/failure counts
    if (agentInstance.successCount !== undefined) {
      state.successCount = agentInstance.successCount;
    }
    if (agentInstance.failureCount !== undefined) {
      state.failureCount = agentInstance.failureCount;
    }

    // Extract model family
    if (agentInstance.modelFamily) {
      state.modelFamily = agentInstance.modelFamily;
    }

    // Extract last output if available
    if (agentInstance.lastOutput) {
      state.lastOutput = agentInstance.lastOutput;
    }

    return state;
  }

  private extractCallStack(agentInstance: any): StackFrame[] {
    // For async agents, we simulate a call stack
    // In a real implementation, this would capture actual stack traces
    const stack: StackFrame[] = [
      {
        functionName: 'process',
        file: 'agent.ts',
        line: 100,
        column: 0,
      },
    ];

    return stack;
  }

  private extractVariables(agentInstance: any): Record<string, unknown> {
    const variables: Record<string, unknown> = {};

    // Extract configuration
    if (agentInstance.defaultParams) {
      variables.defaultParams = { ...agentInstance.defaultParams };
    }

    // Extract input/output topics
    if (agentInstance.inputTopics) {
      variables.inputTopics = [...agentInstance.inputTopics];
    }
    if (agentInstance.outputTopic) {
      variables.outputTopic = agentInstance.outputTopic;
    }

    // Extract learning parameters
    if (agentInstance.learningRate) {
      variables.learningRate = agentInstance.learningRate;
    }
    if (agentInstance.discountFactor) {
      variables.discountFactor = agentInstance.discountFactor;
    }

    return variables;
  }

  private getPackageHistory(
    agentId: string,
    type: 'sent' | 'received'
  ): A2APackageTrace[] {
    const history = this.packageHistory.get(agentId) || [];

    if (type === 'sent') {
      return history.filter(p => p.fromAgentId === agentId);
    } else {
      return history.filter(p => p.toAgentId === agentId);
    }
  }

  private getBreakpointStatus(agentId: string): BreakpointStatus {
    const breakpoints = this.listBreakpoints(agentId).filter(bp => bp.enabled);

    return {
      isHit: false, // Would be set to true if breakpoint is currently hit
      hitCount: breakpoints.reduce((sum, bp) => sum + bp.hitCount, 0),
    };
  }

  private extractMetrics(agentInstance: any): AgentMetrics {
    const successCount = agentInstance.successCount || 0;
    const failureCount = agentInstance.failureCount || 0;
    const executionCount = successCount + failureCount;

    return {
      executionCount,
      successCount,
      failureCount,
      avgLatencyMs: agentInstance.avgLatencyMs || 0,
      minLatencyMs: agentInstance.minLatencyMs || 0,
      maxLatencyMs: agentInstance.maxLatencyMs || 0,
      avgCpuUsage: 0, // Would be tracked separately
      avgMemoryUsage: 0, // Would be tracked separately
      avgValueFunction: agentInstance.valueFunction || 0.5,
      learningEvents: agentInstance.learningEvents || 0,
    };
  }

  private storeInspection(agentId: string, inspection: AgentInspection): void {
    let history = this.inspectionHistory.get(agentId);

    if (!history) {
      history = [];
      this.inspectionHistory.set(agentId, history);
    }

    history.push(inspection);

    // Enforce max size
    if (history.length > this.maxHistorySize) {
      history.shift();
    }
  }

  private evaluateCondition(
    condition: BreakpointCondition,
    currentState: Record<string, unknown>
  ): boolean {
    // Simple condition evaluation
    // In a real implementation, this would use a safe expression evaluator

    switch (condition.type) {
      case 'agent_state':
        if (condition.agentId && condition.predicate) {
          // Evaluate predicate against current state
          return this.evaluatePredicate(condition.predicate, currentState);
        }
        return false;

      case 'error':
        // Check if agent is in error state
        return currentState.status === 'error';

      default:
        return false;
    }
  }

  private evaluatePredicate(
    predicate: string,
    state: Record<string, unknown>
  ): boolean {
    // Safe predicate evaluation
    // In a real implementation, this would use a proper expression parser

    try {
      // Simple evaluation for common patterns
      if (predicate.includes('=== ')) {
        const [field, value] = predicate.split('===');
        const fieldName = field.trim();
        const expectedValue = JSON.parse(value.trim());
        return state[fieldName] === expectedValue;
      }

      if (predicate.includes('> ')) {
        const [field, value] = predicate.split('>');
        const fieldName = field.trim();
        const numValue = parseFloat(value.trim());
        return typeof state[fieldName] === 'number' &&
               (state[fieldName] as number) > numValue;
      }

      if (predicate.includes('< ')) {
        const [field, value] = predicate.split('<');
        const fieldName = field.trim();
        const numValue = parseFloat(value.trim());
        return typeof state[fieldName] === 'number' &&
               (state[fieldName] as number) < numValue;
      }

      return false;
    } catch {
      return false;
    }
  }
}

// ============================================================================
// Types
// ============================================================================

/**
 * State difference
 */
export interface StateDifference {
  /**
   * Field name
   */
  field: string;

  /**
   * Old value
   */
  oldValue: unknown;

  /**
   * New value
   */
  newValue: unknown;

  /**
   * Change type
   */
  changeType: 'added' | 'removed' | 'changed';
}
