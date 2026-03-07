/**
 * POLLN Knowledge Succession Protocol
 * Tile lifecycle management and knowledge transfer
 *
 * Based on FINAL_INTEGRATION.md: Tile Lifespans and Knowledge Stages
 */

import { v4 as uuidv4 } from 'uuid';
import { EventEmitter } from 'events';

// ============================================================================
// KNOWLEDGE STAGES
// ============================================================================

/**
 * KnowledgeStage - Time-based evolution of knowledge
 *
 * From FINAL_INTEGRATION.md:
 * - EPHEMERAL: Fresh, untested, high uncertainty
 * - WORKING: Validated through use, medium confidence
 * - EMBEDDED: Deeply integrated, high confidence
 * - FOSSIL: Outdated but preserved for reference
 */
export enum KnowledgeStage {
  EPHEMERAL = 'EPHEMERAL',  // Fresh patterns, < 100 executions
  WORKING = 'WORKING',      // Validated patterns, 100-1000 executions
  EMBEDDED = 'EMBEDDED',    // Deep patterns, > 1000 executions
  FOSSIL = 'FOSSIL',        // Archived patterns, no longer active
}

// ============================================================================
// KNOWLEDGE PACKET
// ============================================================================

export interface KnowledgePacket {
  id: string;
  sourceAgentId: string;
  targetAgentId?: string;
  stage: KnowledgeStage;
  patterns: Map<string, PatternData>;
  valueFunction: number;
  executionCount: number;
  successRate: number;
  createdAt: number;
  expiresAt?: number;
  metadata: {
    sourceTypeId: string;
    sourceCategoryId: string;
    transferReason: TransferReason;
    compressionRatio: number;
  };
}

export interface PatternData {
  key: string;
  value: unknown;
  count: number;
  lastUsed: number;
  successRate: number;
  stage: KnowledgeStage;
}

export type TransferReason =
  | 'death'           // Agent dying, final transfer
  | 'succession'      // Planned handoff to successor
  | 'backup'          // Periodic backup
  | 'migration'       // Moving to new agent type
  | 'compression';    // Compressing for storage

// ============================================================================
// SUCCESSION EVENT
// ============================================================================

export interface SuccessionEvent {
  id: string;
  timestamp: number;
  predecessorId: string;
  successorId: string;
  knowledgeTransferred: number;
  patternsPreserved: number;
  valueFunctionInherited: number;
  success: boolean;
  failureReason?: string;
}

// ============================================================================
// KNOWLEDGE SUCCESSION MANAGER
// ============================================================================

/**
 * KnowledgeSuccessionManager - Orchestrates knowledge transfer between agents
 *
 * Key responsibilities:
 * 1. Extract knowledge from dying agents
 * 2. Compress and stage knowledge for transfer
 * 3. Inject knowledge into successor agents
 * 4. Track succession history
 */
export class KnowledgeSuccessionManager extends EventEmitter {
  private knowledgeStore: Map<string, KnowledgePacket> = new Map();
  private successionHistory: SuccessionEvent[] = [];
  private pendingTransfers: Map<string, KnowledgePacket> = new Map();

  // Configuration
  private config = {
    maxPatternAge: 7 * 24 * 60 * 60 * 1000, // 7 days in ms
    minPatternCount: 5,                     // Minimum executions to preserve
    compressionThreshold: 100,              // Patterns before compression
    maxPendingAge: 24 * 60 * 60 * 1000,     // 24 hours
  };

  constructor() {
    super();
  }

  /**
   * Extract knowledge from an agent before death
   */
  extractKnowledge(
    agentId: string,
    agentType: string,
    agentCategory: string,
    state: Map<string, unknown>,
    valueFunction: number,
    executionCount: number,
    successCount: number,
    reason: TransferReason
  ): KnowledgePacket {
    const now = Date.now();
    const successRate = executionCount > 0 ? successCount / executionCount : 0;

    // Determine knowledge stage based on execution count
    const stage = this.determineStage(executionCount);

    // Extract and filter patterns
    const patterns = this.extractPatterns(state, executionCount);

    // Calculate compression ratio
    const originalSize = state.size;
    const compressedSize = patterns.size;
    const compressionRatio = originalSize > 0 ? compressedSize / originalSize : 1;

    const packet: KnowledgePacket = {
      id: uuidv4(),
      sourceAgentId: agentId,
      stage,
      patterns,
      valueFunction,
      executionCount,
      successRate,
      createdAt: now,
      metadata: {
        sourceTypeId: agentType,
        sourceCategoryId: agentCategory,
        transferReason: reason,
        compressionRatio,
      },
    };

    // Store the packet
    this.knowledgeStore.set(packet.id, packet);

    this.emit('knowledge_extracted', {
      packetId: packet.id,
      agentId,
      patternCount: patterns.size,
      stage,
    });

    return packet;
  }

  /**
   * Transfer knowledge to a successor agent
   */
  transferKnowledge(
    packetId: string,
    successorId: string,
    targetState: Map<string, unknown>
  ): SuccessionEvent {
    const packet = this.knowledgeStore.get(packetId);
    const now = Date.now();

    if (!packet) {
      return this.createFailureEvent(
        'unknown-predecessor',
        successorId,
        'Knowledge packet not found'
      );
    }

    try {
      // Inject patterns into target state
      let patternsPreserved = 0;
      for (const [key, pattern] of packet.patterns) {
        // Only inject if pattern is still valid
        if (this.isPatternValid(pattern)) {
          targetState.set(key, pattern.value);
          patternsPreserved++;
        }
      }

      // Create succession event
      const event: SuccessionEvent = {
        id: uuidv4(),
        timestamp: now,
        predecessorId: packet.sourceAgentId,
        successorId,
        knowledgeTransferred: packet.patterns.size,
        patternsPreserved,
        valueFunctionInherited: packet.valueFunction,
        success: true,
      };

      // Record history
      this.successionHistory.push(event);

      // Clean up transferred packet
      this.knowledgeStore.delete(packetId);

      this.emit('succession_complete', event);

      return event;
    } catch (error) {
      return this.createFailureEvent(
        packet.sourceAgentId,
        successorId,
        error instanceof Error ? error.message : 'Unknown error'
      );
    }
  }

  /**
   * Queue knowledge for delayed transfer
   */
  queueForTransfer(packet: KnowledgePacket, targetAgentId: string): void {
    packet.targetAgentId = targetAgentId;
    packet.expiresAt = Date.now() + this.config.maxPendingAge;
    this.pendingTransfers.set(packet.id, packet);

    this.emit('knowledge_queued', {
      packetId: packet.id,
      targetAgentId,
    });
  }

  /**
   * Process pending transfers for a specific agent
   */
  processPendingTransfers(
    agentId: string,
    targetState: Map<string, unknown>
  ): SuccessionEvent[] {
    const events: SuccessionEvent[] = [];

    for (const [packetId, packet] of this.pendingTransfers) {
      if (packet.targetAgentId === agentId) {
        // Check if expired
        if (packet.expiresAt && packet.expiresAt < Date.now()) {
          this.pendingTransfers.delete(packetId);
          continue;
        }

        const event = this.transferKnowledge(packetId, agentId, targetState);
        events.push(event);
        this.pendingTransfers.delete(packetId);
      }
    }

    return events;
  }

  /**
   * Compress knowledge for long-term storage
   */
  compressKnowledge(packet: KnowledgePacket): KnowledgePacket {
    if (packet.patterns.size < this.config.compressionThreshold) {
      return packet;
    }

    // Sort patterns by importance (count * successRate)
    const sortedPatterns = Array.from(packet.patterns.entries())
      .sort((a, b) => {
        const scoreA = a[1].count * a[1].successRate;
        const scoreB = b[1].count * b[1].successRate;
        return scoreB - scoreA;
      });

    // Keep top patterns (50% compression)
    const keepCount = Math.floor(sortedPatterns.length * 0.5);
    const compressedPatterns = new Map(
      sortedPatterns.slice(0, keepCount).map(([key, value]) => [key, value])
    );

    // Update compression ratio
    packet.patterns = compressedPatterns;
    packet.metadata.compressionRatio = compressedPatterns.size / sortedPatterns.length;

    this.emit('knowledge_compressed', {
      packetId: packet.id,
      originalSize: sortedPatterns.length,
      compressedSize: compressedPatterns.size,
    });

    return packet;
  }

  /**
   * Age out old patterns and fossilize stale knowledge
   */
  ageKnowledge(): number {
    const now = Date.now();
    let aged = 0;

    for (const packet of this.knowledgeStore.values()) {
      for (const [key, pattern] of packet.patterns) {
        const age = now - pattern.lastUsed;

        // Fossilize old patterns
        if (age > this.config.maxPatternAge && pattern.stage !== KnowledgeStage.FOSSIL) {
          pattern.stage = KnowledgeStage.FOSSIL;
          aged++;
        }
      }
    }

    // Clean up expired pending transfers
    for (const [packetId, packet] of this.pendingTransfers) {
      if (packet.expiresAt && packet.expiresAt < now) {
        this.pendingTransfers.delete(packetId);
        aged++;
      }
    }

    return aged;
  }

  /**
   * Get succession statistics
   */
  getStats(): {
    storedPackets: number;
    pendingTransfers: number;
    totalSuccessions: number;
    successfulSuccessions: number;
    failedSuccessions: number;
    averagePatternsPreserved: number;
  } {
    const successful = this.successionHistory.filter(e => e.success);
    const avgPreserved = successful.length > 0
      ? successful.reduce((sum, e) => sum + e.patternsPreserved, 0) / successful.length
      : 0;

    return {
      storedPackets: this.knowledgeStore.size,
      pendingTransfers: this.pendingTransfers.size,
      totalSuccessions: this.successionHistory.length,
      successfulSuccessions: successful.length,
      failedSuccessions: this.successionHistory.length - successful.length,
      averagePatternsPreserved: avgPreserved,
    };
  }

  /**
   * Get succession history for an agent
   */
  getSuccessionHistory(agentId: string): SuccessionEvent[] {
    return this.successionHistory.filter(
      e => e.predecessorId === agentId || e.successorId === agentId
    );
  }

  // ============================================================================
  // PRIVATE METHODS
  // ============================================================================

  private determineStage(executionCount: number): KnowledgeStage {
    if (executionCount < 100) return KnowledgeStage.EPHEMERAL;
    if (executionCount < 1000) return KnowledgeStage.WORKING;
    return KnowledgeStage.EMBEDDED;
  }

  private extractPatterns(
    state: Map<string, unknown>,
    executionCount: number
  ): Map<string, PatternData> {
    const patterns = new Map<string, PatternData>();
    const now = Date.now();

    for (const [key, value] of state) {
      // Skip internal state keys
      if (key.startsWith('_') || key === 'initializedAt' || key === 'shutdownAt') {
        continue;
      }

      // Extract pattern metadata if available
      const patternValue = value as { count?: number; successRate?: number };
      const count = patternValue.count || 1;
      const successRate = patternValue.successRate || 0.5;

      // Skip low-count patterns
      if (count < this.config.minPatternCount) {
        continue;
      }

      const stage = this.determineStage(count);

      patterns.set(key, {
        key,
        value,
        count,
        lastUsed: now,
        successRate,
        stage,
      });
    }

    return patterns;
  }

  private isPatternValid(pattern: PatternData): boolean {
    // Fossil patterns are not transferred
    if (pattern.stage === KnowledgeStage.FOSSIL) {
      return false;
    }

    // Check minimum count
    if (pattern.count < this.config.minPatternCount) {
      return false;
    }

    // Check age
    const age = Date.now() - pattern.lastUsed;
    if (age > this.config.maxPatternAge) {
      return false;
    }

    return true;
  }

  private createFailureEvent(
    predecessorId: string,
    successorId: string,
    reason: string
  ): SuccessionEvent {
    const event: SuccessionEvent = {
      id: uuidv4(),
      timestamp: Date.now(),
      predecessorId,
      successorId,
      knowledgeTransferred: 0,
      patternsPreserved: 0,
      valueFunctionInherited: 0,
      success: false,
      failureReason: reason,
    };

    this.successionHistory.push(event);
    this.emit('succession_failed', event);

    return event;
  }
}

// ============================================================================
// TILE LIFECYCLE MANAGER
// ============================================================================

/**
 * TileLifecycleManager - Manages agent lifecycle events
 *
 * Coordinates with KnowledgeSuccessionManager for smooth transitions
 */
export class TileLifecycleManager extends EventEmitter {
  private successionManager: KnowledgeSuccessionManager;
  private agentRegistry: Map<string, {
    status: 'active' | 'dying' | 'dead';
    successorId?: string;
    deathScheduled?: number;
  }> = new Map();

  constructor(successionManager: KnowledgeSuccessionManager) {
    super();
    this.successionManager = successionManager;
  }

  /**
   * Register an agent for lifecycle management
   */
  registerAgent(agentId: string): void {
    this.agentRegistry.set(agentId, { status: 'active' });
  }

  /**
   * Schedule agent death with succession
   */
  scheduleDeath(
    agentId: string,
    successorId: string,
    delayMs: number = 0
  ): void {
    const entry = this.agentRegistry.get(agentId);
    if (!entry) return;

    entry.status = 'dying';
    entry.successorId = successorId;
    entry.deathScheduled = Date.now() + delayMs;

    this.emit('death_scheduled', { agentId, successorId, delayMs });
  }

  /**
   * Execute agent death with knowledge transfer
   */
  async executeDeath(
    agentId: string,
    agentType: string,
    agentCategory: string,
    state: Map<string, unknown>,
    valueFunction: number,
    executionCount: number,
    successCount: number
  ): Promise<SuccessionEvent | null> {
    const entry = this.agentRegistry.get(agentId);
    if (!entry) return null;

    // Extract knowledge
    const packet = this.successionManager.extractKnowledge(
      agentId,
      agentType,
      agentCategory,
      state,
      valueFunction,
      executionCount,
      successCount,
      'death'
    );

    // Transfer to successor if designated
    if (entry.successorId) {
      const event = this.successionManager.transferKnowledge(
        packet.id,
        entry.successorId,
        state // This would be the successor's state in real usage
      );

      entry.status = 'dead';
      this.emit('agent_died', { agentId, successorId: entry.successorId, event });

      return event;
    }

    // No successor - just archive the knowledge
    entry.status = 'dead';
    this.emit('agent_died', { agentId, successorId: null });

    return null;
  }

  /**
   * Check if agent is scheduled for death
   */
  isDying(agentId: string): boolean {
    const entry = this.agentRegistry.get(agentId);
    return entry?.status === 'dying';
  }

  /**
   * Get agents scheduled for death
   */
  getDyingAgents(): string[] {
    const dying: string[] = [];
    for (const [agentId, entry] of this.agentRegistry) {
      if (entry.status === 'dying') {
        dying.push(agentId);
      }
    }
    return dying;
  }
}
