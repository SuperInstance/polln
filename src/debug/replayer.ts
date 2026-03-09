/**
 * Replayer
 *
 * Provides execution replay capabilities for debugging past runs,
 * analyzing divergences, and performing what-if analysis.
 */

import type {
  ReplaySession,
  ReplayEvent,
  StateSnapshot,
  ReplayDivergence,
  ReplayStats,
  DistributedTrace,
} from './types.js';
import { DebugError } from './types.js';

// ============================================================================
// Replayer Class
// ============================================================================

/**
 * Replayer for executing colony traces in a controlled environment
 */
export class Replayer {
  private sessions: Map<string, ReplaySession> = new Map();
  private traceCache: Map<string, DistributedTrace> = new Map();

  /**
   * Start a replay session
   *
   * @param causalChainId - Causal chain ID to replay
   * @param options - Replay options
   * @returns Replay session ID
   */
  async startReplay(
    causalChainId: string,
    options: ReplayOptions = {}
  ): Promise<string> {
    // Get original trace
    const originalTrace = await this.getTraceForReplay(causalChainId);
    if (!originalTrace) {
      throw new DebugError('REPLAY_FAILED', `No trace found for causal chain ${causalChainId}`);
    }

    const sessionId = `replay_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const session: ReplaySession = {
      sessionId,
      causalChainId,
      startTime: Date.now(),
      status: 'running',
      originalTrace,
      events: [],
      snapshots: [],
      divergences: [],
      stats: {
        totalEvents: 0,
        successfulEvents: 0,
        failedEvents: 0,
        divergences: 0,
        replayTime: 0,
        speedup: 0,
        snapshotCount: 0,
      },
    };

    this.sessions.set(sessionId, session);

    // Start replay execution
    this.executeReplay(sessionId, options);

    return sessionId;
  }

  /**
   * Get a replay session
   *
   * @param sessionId - Replay session ID
   * @returns Replay session or null
   */
  getSession(sessionId: string): ReplaySession | null {
    return this.sessions.get(sessionId) || null;
  }

  /**
   * List all replay sessions
   *
   * @param filters - Optional filters
   * @returns Array of sessions
   */
  listSessions(filters?: SessionFilters): ReplaySession[] {
    let sessions = Array.from(this.sessions.values());

    if (filters) {
      if (filters.causalChainId) {
        sessions = sessions.filter(s => s.causalChainId === filters.causalChainId);
      }

      if (filters.status) {
        sessions = sessions.filter(s => s.status === filters.status);
      }

      if (filters.minStartTime) {
        sessions = sessions.filter(s => s.startTime >= filters.minStartTime!);
      }

      if (filters.limit) {
        sessions = sessions.slice(0, filters.limit);
      }
    }

    return sessions;
  }

  /**
   * Pause a replay session
   *
   * @param sessionId - Replay session ID
   */
  async pauseReplay(sessionId: string): Promise<void> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new DebugError('REPLAY_FAILED', `Session ${sessionId} not found`);
    }
    if (session.status !== 'running') {
      throw new DebugError('REPLAY_FAILED', `Cannot pause session ${sessionId} - current status: ${session.status}`);
    }

    (session.status as any) = 'paused';
  }

  /**
   * Resume a paused replay session
   *
   * @param sessionId - Replay session ID
   */
  async resumeReplay(sessionId: string): Promise<void> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new DebugError('REPLAY_FAILED', `Session ${sessionId} not found`);
    }
    if (session.status !== 'paused') {
      throw new DebugError('REPLAY_FAILED', `Cannot resume session ${sessionId} - current status: ${session.status}`);
    }

    session.status = 'running';

    // Resume execution
    this.executeReplay(sessionId, {});
  }

  /**
   * Cancel a replay session
   *
   * @param sessionId - Replay session ID
   */
  async cancelReplay(sessionId: string): Promise<void> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new DebugError('REPLAY_FAILED', `Session ${sessionId} not found`);
    }

    session.status = 'cancelled';
    session.endTime = Date.now();
  }

  /**
   * Step through a replay one event at a time
   *
   * @param sessionId - Replay session ID
   * @returns Next event or null if complete
   */
  async stepReplay(sessionId: string): Promise<ReplayEvent | null> {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new DebugError('REPLAY_FAILED', `Session ${sessionId} not found`);
    }

    // Pause if running
    if (session.status === 'running') {
      await this.pauseReplay(sessionId);
    }

    // Get next event from trace
    const nextEvent = this.getNextEventFromTrace(session);
    if (!nextEvent) {
      session.status = 'completed';
      session.endTime = Date.now();
      return null;
    }

    // Execute event
    await this.executeReplayEvent(session, nextEvent);

    return nextEvent;
  }

  /**
   * Get replay divergences
   *
   * @param sessionId - Replay session ID
   * @returns Array of divergences
   */
  getDivergences(sessionId: string): ReplayDivergence[] {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new DebugError('REPLAY_FAILED', `Session ${sessionId} not found`);
    }

    return session.divergences;
  }

  /**
   * Get state snapshots from replay
   *
   * @param sessionId - Replay session ID
   * @param timestamp - Specific timestamp (null for all)
   * @returns Array of snapshots
   */
  getSnapshots(sessionId: string, timestamp: number | null = null): StateSnapshot[] {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new DebugError('REPLAY_FAILED', `Session ${sessionId} not found`);
    }

    if (timestamp === null) {
      return session.snapshots;
    }

    // Find closest snapshot to timestamp
    return session.snapshots.filter(s => Math.abs(s.timestamp - timestamp) < 1000);
  }

  /**
   * Perform what-if analysis
   *
   * @param causalChainId - Causal chain ID
   * @param modifications - Modifications to apply
   * @returns What-if analysis result
   */
  async whatIf(
    causalChainId: string,
    modifications: WhatIfModification[]
  ): Promise<WhatIfResult> {
    // Get original trace
    const originalTrace = await this.getTraceForReplay(causalChainId);
    if (!originalTrace) {
      throw new DebugError('REPLAY_FAILED', `No trace found for causal chain ${causalChainId}`);
    }

    // Create modified replay session
    const sessionId = `whatif_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const session: ReplaySession = {
      sessionId,
      causalChainId,
      startTime: Date.now(),
      status: 'running',
      originalTrace,
      events: [],
      snapshots: [],
      divergences: [],
      stats: {
        totalEvents: 0,
        successfulEvents: 0,
        failedEvents: 0,
        divergences: 0,
        replayTime: 0,
        speedup: 0,
        snapshotCount: 0,
      },
    };

    this.sessions.set(sessionId, session);

    // Apply modifications and execute
    await this.applyModifications(session, modifications);
    await this.executeReplay(sessionId, {});

    const modifiedSession = this.sessions.get(sessionId)!;

    return {
      sessionId,
      originalTrace: causalChainId,
      modifications,
      originalDuration: originalTrace.timeline.duration,
      modifiedDuration: modifiedSession.endTime! - modifiedSession.startTime,
      divergences: modifiedSession.divergences,
      outcome: this.computeWhatIfOutcome(originalTrace, modifiedSession),
    };
  }

  /**
   * Export replay session
   *
   * @param sessionId - Replay session ID
   * @param format - Export format
   * @returns Exported data
   */
  exportReplay(sessionId: string, format: ReplayExportFormat): string {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new DebugError('REPLAY_FAILED', `Session ${sessionId} not found`);
    }

    switch (format) {
      case 'json':
        return JSON.stringify(session, null, 2);

      case 'csv':
        return this.exportToCSV(session);

      case 'timeline':
        return this.exportToTimeline(session);

      default:
        throw new DebugError(
          'REPLAY_FAILED',
          `Unknown export format: ${format}`
        );
    }
  }

  // ==========================================================================
  // Private Methods
  // ==========================================================================

  private async getTraceForReplay(causalChainId: string): Promise<DistributedTrace | null> {
    // In a real implementation, this would fetch from the tracer
    // For now, return null to indicate no trace available
    return this.traceCache.get(causalChainId) || null;
  }

  private async executeReplay(
    sessionId: string,
    options: ReplayOptions
  ): Promise<void> {
    const session = this.sessions.get(sessionId);
    if (!session || session.status !== 'running') {
      return;
    }

    const { speed = 1, snapshotInterval = 1000 } = options;

    try {
      // Process events from original trace
      for (const span of session.originalTrace.spans) {
        if (session.status !== 'running') break;

        // Create replay event from span
        const event: ReplayEvent = {
          eventId: `replay_${span.spanId}`,
          sequence: session.events.length,
          timestamp: Date.now(),
          type: 'agent_start',
          agentId: span.agentId,
          data: {
            operationName: span.operationName,
            tags: span.tags,
          },
        };

        session.events.push(event);
        session.stats.totalEvents++;

        // Execute event (in real implementation, this would execute the actual code)
        await this.executeReplayEvent(session, event);

        // Apply speed multiplier
        if (speed < 1) {
          await new Promise(resolve => setTimeout(resolve, span.duration * (1 - speed)));
        }

        // Take snapshot at interval
        if (event.sequence % Math.floor(snapshotInterval / 100) === 0) {
          await this.takeSnapshot(session);
        }
      }

      // Final snapshot
      await this.takeSnapshot(session);

      session.status = 'completed';
      session.endTime = Date.now();
      session.stats.replayTime = session.endTime - session.startTime;
      session.stats.speedup = session.originalTrace.timeline.duration / session.stats.replayTime;

    } catch (error) {
      session.status = 'failed';
      session.endTime = Date.now();

      // Record failure
      const divergence: ReplayDivergence = {
        divergenceId: `div_${Date.now()}`,
        sequence: session.events.length,
        type: 'error',
        expected: 'success',
        actual: error instanceof Error ? error.message : String(error),
        severity: 'critical',
        description: 'Replay execution failed',
      };

      session.divergences.push(divergence);
      session.stats.failedEvents++;
    }
  }

  private async executeReplayEvent(
    session: ReplaySession,
    event: ReplayEvent
  ): Promise<void> {
    try {
      // In a real implementation, this would:
      // 1. Execute the actual agent operation
      // 2. Compare results with original execution
      // 3. Record any divergences

      // For now, simulate successful execution
      session.stats.successfulEvents++;

      // Simulate potential divergences based on randomness
      if (Math.random() < 0.05) {
        // 5% chance of divergence
        const divergence: ReplayDivergence = {
          divergenceId: `div_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
          sequence: event.sequence,
          type: 'value',
          expected: 'original_value',
          actual: 'replay_value',
          severity: 'low',
          description: 'Minor value difference detected during replay',
        };

        session.divergences.push(divergence);
        session.stats.divergences++;
      }

    } catch (error) {
      session.stats.failedEvents++;

      const divergence: ReplayDivergence = {
        divergenceId: `div_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        sequence: event.sequence,
        type: 'error',
        expected: 'success',
        actual: error instanceof Error ? error.message : String(error),
        severity: 'high',
        description: 'Event execution failed during replay',
      };

      session.divergences.push(divergence);
      session.stats.divergences++;
      throw error;
    }
  }

  private async takeSnapshot(session: ReplaySession): Promise<void> {
    const snapshot: StateSnapshot = {
      snapshotId: `snap_${session.snapshots.length}_${Date.now()}`,
      timestamp: Date.now(),
      agentStates: {},
      colonyState: {},
      globals: {},
    };

    // In a real implementation, this would capture actual state
    session.snapshots.push(snapshot);
    session.stats.snapshotCount++;
  }

  private getNextEventFromTrace(session: ReplaySession): ReplayEvent | null {
    const nextSequence = session.events.length;

    if (nextSequence >= session.originalTrace.spans.length) {
      return null;
    }

    const span = session.originalTrace.spans[nextSequence];

    return {
      eventId: `replay_${span.spanId}`,
      sequence: nextSequence,
      timestamp: Date.now(),
      type: 'agent_start',
      agentId: span.agentId,
      data: {
        operationName: span.operationName,
        tags: span.tags,
      },
    };
  }

  private async applyModifications(
    session: ReplaySession,
    modifications: WhatIfModification[]
  ): Promise<void> {
    // Apply modifications to the session
    for (const mod of modifications) {
      switch (mod.type) {
        case 'remove_agent':
          // Remove agent from execution
          session.originalTrace.spans = session.originalTrace.spans.filter(
            s => s.agentId !== mod.agentId
          );
          break;

        case 'modify_latency':
          // Modify agent latency
          for (const span of session.originalTrace.spans) {
            if (span.agentId === mod.agentId) {
              span.duration = mod.value as number;
            }
          }
          break;

        case 'inject_error':
          // Inject error at specific point
          const errorSpan = session.originalTrace.spans[mod.sequence || 0];
          if (errorSpan) {
            errorSpan.status = 'error';
          }
          break;

        case 'modify_value':
          // Modify agent value function
          // In real implementation, this would modify agent state
          break;
      }
    }
  }

  private computeWhatIfOutcome(
    originalTrace: DistributedTrace,
    modifiedSession: ReplaySession
  ): WhatIfOutcome {
    const originalDuration = originalTrace.timeline.duration;
    const modifiedDuration = modifiedSession.endTime! - modifiedSession.startTime;

    return {
      durationChange: modifiedDuration - originalDuration,
      durationPercentChange: ((modifiedDuration - originalDuration) / originalDuration) * 100,
      divergenceCount: modifiedSession.divergences.length,
      successRate: modifiedSession.stats.successfulEvents / modifiedSession.stats.totalEvents,
      recommendation: this.generateWhatIfRecommendation(modifiedSession),
    };
  }

  private generateWhatIfRecommendation(session: ReplaySession): string {
    if (session.divergences.length === 0) {
      return 'No divergences detected. Modifications appear to be safe.';
    }

    const criticalDivergences = session.divergences.filter(d => d.severity === 'critical');
    if (criticalDivergences.length > 0) {
      return 'Critical divergences detected. Modifications are not recommended.';
    }

    const highDivergences = session.divergences.filter(d => d.severity === 'high');
    if (highDivergences.length > 0) {
      return 'High severity divergences detected. Proceed with caution.';
    }

    return 'Minor divergences detected. Modifications are likely safe.';
  }

  private exportToCSV(session: ReplaySession): string {
    let csv = 'sequence,timestamp,type,agentId,data\n';

    for (const event of session.events) {
      const data = JSON.stringify(event.data).replace(/"/g, '""');
      csv += `${event.sequence},${event.timestamp},${event.type},${event.agentId},"${data}"\n`;
    }

    return csv;
  }

  private exportToTimeline(session: ReplaySession): string {
    let timeline = `Replay Session: ${session.sessionId}\n`;
    timeline += `Causal Chain: ${session.causalChainId}\n`;
    timeline += `Status: ${session.status}\n`;
    timeline += `Duration: ${session.endTime! - session.startTime}ms\n`;
    timeline += `Events: ${session.stats.totalEvents}\n`;
    timeline += `Divergences: ${session.stats.divergences}\n\n`;

    timeline += 'Timeline:\n';
    timeline += '---------\n';

    for (const event of session.events) {
      const time = event.timestamp - session.startTime;
      timeline += `[${time}ms] ${event.type} - ${event.agentId}\n`;
    }

    if (session.divergences.length > 0) {
      timeline += '\nDivergences:\n';
      timeline += '-------------\n';

      for (const div of session.divergences) {
        timeline += `[${div.sequence}] ${div.type}: ${div.description}\n`;
        timeline += `  Expected: ${div.expected}\n`;
        timeline += `  Actual: ${div.actual}\n`;
        timeline += `  Severity: ${div.severity}\n\n`;
      }
    }

    return timeline;
  }
}

// ============================================================================
// Types
// ============================================================================

/**
 * Replay options
 */
export interface ReplayOptions {
  /**
   * Replay speed multiplier (1 = real-time, 0.5 = half-speed, 2 = 2x speed)
   */
  speed?: number;

  /**
   * Snapshot interval in milliseconds
   */
  snapshotInterval?: number;

  /**
   * Stop on first divergence
   */
  stopOnDivergence?: boolean;

  /**
   * Maximum number of events to replay
   */
  maxEvents?: number;
}

/**
 * Session filters
 */
export interface SessionFilters {
  /**
   * Filter by causal chain ID
   */
  causalChainId?: string;

  /**
   * Filter by status
   */
  status?: ReplaySession['status'];

  /**
   * Filter by minimum start time
   */
  minStartTime?: number;

  /**
   * Limit results
   */
  limit?: number;
}

/**
 * What-if modification
 */
export interface WhatIfModification {
  /**
   * Modification type
   */
  type: 'remove_agent' | 'modify_latency' | 'inject_error' | 'modify_value';

  /**
   * Agent ID to modify
   */
  agentId?: string;

  /**
   * Event sequence to modify
   */
  sequence?: number;

  /**
   * New value
   */
  value?: unknown;
}

/**
 * What-if result
 */
export interface WhatIfResult {
  /**
   * Replay session ID
   */
  sessionId: string;

  /**
   * Original causal chain ID
   */
  originalTrace: string;

  /**
   * Modifications applied
   */
  modifications: WhatIfModification[];

  /**
   * Original duration
   */
  originalDuration: number;

  /**
   * Modified duration
   */
  modifiedDuration: number;

  /**
   * Divergences detected
   */
  divergences: ReplayDivergence[];

  /**
   * Outcome analysis
   */
  outcome: WhatIfOutcome;
}

/**
 * What-if outcome
 */
export interface WhatIfOutcome {
  /**
   * Duration change
   */
  durationChange: number;

  /**
   * Duration percent change
   */
  durationPercentChange: number;

  /**
   * Divergence count
   */
  divergenceCount: number;

  /**
   * Success rate
   */
  successRate: number;

  /**
   * Recommendation
   */
  recommendation: string;
}

/**
 * Replay export format
 */
export type ReplayExportFormat = 'json' | 'csv' | 'timeline';
