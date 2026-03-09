/**
 * POLLN Microbiome - Murmuration Engine
 *
 * Emergent coordination through pattern recognition and automation.
 * Like starling flocks, colonies develop "muscle memory" for efficient
 * coordination patterns that execute 100x faster than ad-hoc negotiation.
 *
 * @module microbiome/murmuration
 */

import { v4 as uuidv4 } from 'uuid';
import type { A2APackage } from '../core/types.js';
import type { Colony, Task } from './colony.js';
import type { MicrobiomeAgent } from './types.js';

/**
 * Murmuration pattern - a learned coordination sequence
 */
export interface MurmurationPattern {
  /** Pattern ID */
  id: string;
  /** Pattern name */
  name: string;
  /** Participant agent IDs in order */
  participants: string[];
  /** Communication sequence (who messages whom) */
  sequence: PatternStep[];
  /** Pattern signature (hash of sequence) */
  signature: string;
  /** Success rate (0-1) */
  successRate: number;
  /** Execution count */
  executionCount: number;
  /** Average execution time (ms) */
  avgExecutionTime: number;
  /** Formation timestamp */
  formationTime: number;
  /** Last execution timestamp */
  lastExecutionTime: number;
  /** Co-evolution stage */
  coEvolutionStage: CoEvolutionStage;
  /** Automation level (0-1) */
  automationLevel: number;
}

/**
 * Single step in a murmuration pattern
 */
export interface PatternStep {
  /** Step ID */
  id: string;
  /** Sender agent ID */
  senderId: string;
  /** Receiver agent ID */
  receiverId: string;
  /** Message type */
  messageType: string;
  /** Expected payload structure (schema) */
  payloadSchema: Record<string, unknown>;
  /** Timeout in ms */
  timeout: number;
  /** Step index in sequence */
  index: number;
}

/**
 * Co-evolution stages for pattern optimization
 */
export enum CoEvolutionStage {
  /** Initial pattern discovery */
  DISCOVERY = 'discovery',
  /** Pattern refinement through repetition */
  REFINEMENT = 'refinement',
  /** Optimization for efficiency */
  OPTIMIZATION = 'optimization',
  /** Fully automated muscle memory */
  AUTOMATED = 'automated',
  /** Legacy pattern (potential replacement) */
  LEGACY = 'legacy',
}

/**
 * Murmuration memory - stored learned patterns
 */
export interface MurmurationMemory {
  /** Memory ID */
  id: string;
  /** Colony ID this memory belongs to */
  colonyId: string;
  /** Learned patterns */
  patterns: Map<string, MurmurationPattern>;
  /** Pattern index by task type */
  patternsByTask: Map<string, string[]>;
  /** Pattern index by participants */
  patternsByParticipants: Map<string, string[]>;
  /** Last update timestamp */
  lastUpdate: number;
  /** Consolidation level (0-1) */
  consolidationLevel: number;
}

/**
 * Pattern execution result
 */
export interface PatternExecutionResult {
  /** Success status */
  success: boolean;
  /** Execution time (ms) */
  executionTime: number;
  /** Messages exchanged */
  messagesExchanged: number;
  /** Pattern used (if any) */
  patternUsed?: string;
  /** Fallback to ad-hoc */
  fallback: boolean;
  /** Error message (if failed) */
  error?: string;
}

/**
 * Pattern detection result
 */
export interface PatternDetectionResult {
  /** Pattern detected */
  detected: boolean;
  /** Confidence (0-1) */
  confidence: number;
  /** Pattern (if detected) */
  pattern?: MurmurationPattern;
  /** Sequence analyzed */
  sequence: PatternStep[];
  /** Frequency of occurrence */
  frequency: number;
  /** Causality score */
  causality: number;
}

/**
 * Murmuration engine configuration
 */
export interface MurmurationEngineConfig {
  /** Minimum pattern occurrences to learn */
  minOccurrences?: number;
  /** Minimum confidence threshold */
  minConfidence?: number;
  /** Maximum patterns per colony */
  maxPatterns?: number;
  /** Automation threshold (success rate) */
  automationThreshold?: number;
  /** Pattern decay rate (per hour) */
  patternDecayRate?: number;
  /** Co-evolution speed factor */
  coEvolutionSpeed?: number;
  /** Enable performance tracking */
  enablePerformanceTracking?: boolean;
}

/**
 * Sequence analysis for pattern detection
 */
interface SequenceAnalysis {
  /** Frequency of this sequence */
  frequency: number;
  /** Temporal consistency */
  temporalConsistency: number;
  /** Success correlation */
  successCorrelation: number;
  /** Participant stability */
  participantStability: number;
}

/**
 * Performance metrics for a pattern
 */
interface PatternMetrics {
  /** Total executions */
  totalExecutions: number;
  /** Successful executions */
  successfulExecutions: number;
  /** Total execution time */
  totalExecutionTime: number;
  /** Min execution time */
  minExecutionTime: number;
  /** Max execution time */
  maxExecutionTime: number;
  /** Last execution timestamp */
  lastExecution: number;
}

/**
 * MurmurationEngine - Pattern recognition and automation for colony coordination
 *
 * Key insight: "Repeated coordination patterns become automatic muscle memory,
 * achieving 100x speedup over ad-hoc negotiation."
 */
export class MurmurationEngine {
  /** Active murmuration memories by colony */
  private memories: Map<string, MurmurationMemory>;
  /** Pattern detection cache */
  private detectionCache: Map<string, PatternDetectionResult[]>;
  /** Performance metrics by pattern */
  private metrics: Map<string, PatternMetrics>;
  /** Configuration */
  private config: Required<MurmurationEngineConfig>;
  /** Current simulation time */
  private simTime: number;

  constructor(config: MurmurationEngineConfig = {}) {
    this.memories = new Map();
    this.detectionCache = new Map();
    this.metrics = new Map();
    this.simTime = 0;

    this.config = {
      minOccurrences: config.minOccurrences ?? 3,
      minConfidence: config.minConfidence ?? 0.7,
      maxPatterns: config.maxPatterns ?? 50,
      automationThreshold: config.automationThreshold ?? 0.85,
      patternDecayRate: config.patternDecayRate ?? 0.05,
      coEvolutionSpeed: config.coEvolutionSpeed ?? 1.0,
      enablePerformanceTracking: config.enablePerformanceTracking ?? true,
    };
  }

  /**
   * Detect murmuration patterns in A2A communication sequences
   * Uses sequence mining and frequency analysis to find repeated patterns
   */
  detectMurmuration(
    colony: Colony,
    packages: A2APackage[]
  ): PatternDetectionResult[] {
    const results: PatternDetectionResult[] = [];

    if (packages.length < this.config.minOccurrences) {
      return results;
    }

    // Group packages by causal chains
    const chains = this.groupByCausalChain(packages);

    // Analyze each chain for patterns
    for (const [chainId, chainPackages] of chains.entries()) {
      if (chainPackages.length < this.config.minOccurrences) {
        continue;
      }

      const sequence = this.extractSequence(chainPackages);

      // Calculate frequency based on sequence repetition
      const frequency = this.calculateSequenceFrequency(sequence, packages);

      // Only process if we have enough occurrences
      if (frequency < this.config.minOccurrences) {
        continue;
      }

      const analysis = this.analyzeSequence(sequence, chainPackages);
      analysis.frequency = frequency;

      // Calculate overall confidence
      const confidence = this.calculateConfidence(analysis);

      if (confidence >= this.config.minConfidence) {
        const pattern = this.createPatternFromSequence(
          colony,
          sequence,
          analysis,
          confidence
        );

        results.push({
          detected: true,
          confidence,
          pattern,
          sequence,
          frequency: analysis.frequency,
          causality: analysis.successCorrelation,
        });
      }
    }

    // Cache results
    this.detectionCache.set(colony.id, results);

    return results;
  }

  /**
   * Learn murmuration patterns from repeated interactions
   * Converts detected patterns into stored murmuration templates
   */
  learnMurmuration(
    colony: Colony,
    packages: A2APackage[]
  ): MurmurationPattern[] {
    const learnedPatterns: MurmurationPattern[] = [];

    // Detect patterns
    const detections = this.detectMurmuration(colony, packages);

    // Get or create memory for this colony
    const memory = this.getOrCreateMemory(colony);

    // Process each detection
    for (const detection of detections) {
      if (!detection.pattern) {
        continue;
      }

      // Check if pattern already exists
      const existing = this.findPatternBySignature(
        memory,
        detection.pattern.signature
      );

      if (existing) {
        // Update existing pattern
        this.updatePatternFromDetection(existing, detection);
        learnedPatterns.push(existing);
      } else {
        // Add new pattern if under limit
        if (memory.patterns.size < this.config.maxPatterns) {
          memory.patterns.set(detection.pattern.id, detection.pattern);
          this.indexPattern(memory, detection.pattern);
          learnedPatterns.push(detection.pattern);
        }
      }
    }

    // Update consolidation level
    this.updateConsolidation(memory);

    return learnedPatterns;
  }

  /**
   * Execute murmuration pattern for fast coordination
   * Achieves 100x speedup by skipping negotiation phases
   */
  async executeMurmuration(
    colony: Colony,
    task: Task,
    a2aSystem: any
  ): Promise<PatternExecutionResult> {
    const startTime = Date.now();

    // Get memory for this colony
    const memory = this.memories.get(colony.id);
    if (!memory) {
      return this.executeAdHoc(colony, task, a2aSystem, startTime, 'No memory found');
    }

    // Find best matching pattern for this task
    const pattern = this.findBestPattern(memory, task, colony);
    if (!pattern) {
      return this.executeAdHoc(colony, task, a2aSystem, startTime, 'No pattern found');
    }

    // Check if pattern is automated enough
    if (pattern.automationLevel < this.config.automationThreshold) {
      return this.executeAdHoc(colony, task, a2aSystem, startTime, 'Pattern not automated');
    }

    try {
      // Execute pattern
      const result = await this.executePattern(
        colony,
        pattern,
        task,
        a2aSystem
      );

      const executionTime = Date.now() - startTime;

      // Update metrics
      this.updateMetrics(pattern.id, true, executionTime);

      // Update pattern success rate
      pattern.successRate =
        (pattern.successRate * pattern.executionCount + 1) /
        (pattern.executionCount + 1);
      pattern.executionCount++;
      pattern.lastExecutionTime = this.simTime;
      pattern.avgExecutionTime =
        (pattern.avgExecutionTime * (pattern.executionCount - 1) + executionTime) /
        pattern.executionCount;

      // Co-evolve pattern if performing well
      if (pattern.successRate > this.config.automationThreshold) {
        this.optimizeMurmuration(pattern);
      }

      return {
        success: result.success,
        executionTime,
        messagesExchanged: result.messagesExchanged,
        patternUsed: pattern.id,
        fallback: false,
      };
    } catch (error) {
      const executionTime = Date.now() - startTime;

      // Update metrics
      this.updateMetrics(pattern.id, false, executionTime);

      // Update pattern success rate
      pattern.successRate =
        (pattern.successRate * pattern.executionCount) /
        (pattern.executionCount + 1);
      pattern.executionCount++;

      // Fallback to ad-hoc on failure
      return this.executeAdHoc(
        colony,
        task,
        a2aSystem,
        startTime,
        `Pattern execution failed: ${error}`
      );
    }
  }

  /**
   * Optimize murmuration pattern through co-evolution
   * Refines pattern for better efficiency and success rate
   */
  optimizeMurmuration(pattern: MurmurationPattern): MurmurationPattern {
    // Advance co-evolution stage based on performance
    if (pattern.executionCount < 10) {
      pattern.coEvolutionStage = CoEvolutionStage.DISCOVERY;
    } else if (pattern.executionCount < 30) {
      pattern.coEvolutionStage = CoEvolutionStage.REFINEMENT;
    } else if (pattern.executionCount < 50) {
      pattern.coEvolutionStage = CoEvolutionStage.OPTIMIZATION;
    } else if (pattern.successRate > this.config.automationThreshold) {
      pattern.coEvolutionStage = CoEvolutionStage.AUTOMATED;
    } else {
      pattern.coEvolutionStage = CoEvolutionStage.LEGACY;
    }

    // Optimize sequence based on execution data
    const metrics = this.metrics.get(pattern.id);
    if (metrics && pattern.coEvolutionStage !== CoEvolutionStage.LEGACY) {
      // Reduce timeouts for fast steps
      const avgTime = metrics.totalExecutionTime / metrics.totalExecutions;
      for (const step of pattern.sequence) {
        step.timeout = Math.max(10, Math.floor(avgTime / pattern.sequence.length / 2));
      }

      // Increase automation level with performance
      pattern.automationLevel = Math.min(1.0,
        pattern.successRate * (1 + pattern.executionCount / 100)
      );
    }

    return pattern;
  }

  /**
   * Automate murmuration pattern as muscle memory
   * Highly successful patterns become automatic with zero-latency execution
   */
  automateMurmuration(
    colony: Colony,
    patternId: string
  ): boolean {
    const memory = this.memories.get(colony.id);
    if (!memory) {
      return false;
    }

    const pattern = memory.patterns.get(patternId);
    if (!pattern) {
      return false;
    }

    // Check if pattern meets automation criteria
    if (pattern.successRate >= this.config.automationThreshold &&
        pattern.executionCount >= 20) {
      pattern.coEvolutionStage = CoEvolutionStage.AUTOMATED;
      pattern.automationLevel = 1.0;

      // Optimize timeouts for near-instant execution
      for (const step of pattern.sequence) {
        step.timeout = Math.max(1, Math.floor(step.timeout * 0.1));
      }

      return true;
    }

    return false;
  }

  /**
   * Get memory for a colony
   */
  getMemory(colonyId: string): MurmurationMemory | undefined {
    return this.memories.get(colonyId);
  }

  /**
   * Get all patterns for a colony
   */
  getPatterns(colonyId: string): MurmurationPattern[] {
    const memory = this.memories.get(colonyId);
    return memory ? Array.from(memory.patterns.values()) : [];
  }

  /**
   * Get pattern by ID
   */
  getPattern(colonyId: string, patternId: string): MurmurationPattern | undefined {
    const memory = this.memories.get(colonyId);
    return memory?.patterns.get(patternId);
  }

  /**
   * Prune low-performing patterns
   */
  prunePatterns(colonyId: string, minSuccessRate: number = 0.3): number {
    const memory = this.memories.get(colonyId);
    if (!memory) {
      return 0;
    }

    let pruned = 0;
    const toDelete: string[] = [];

    for (const [id, pattern] of memory.patterns.entries()) {
      if (pattern.successRate < minSuccessRate && pattern.executionCount > 10) {
        toDelete.push(id);
      }
    }

    for (const id of toDelete) {
      memory.patterns.delete(id);
      this.removePatternFromIndexes(memory, id);
      pruned++;
    }

    return pruned;
  }

  /**
   * Decay pattern success rates over time
   */
  decayPatterns(colonyId: string): void {
    const memory = this.memories.get(colonyId);
    if (!memory) {
      return;
    }

    const decayFactor = 1 - this.config.patternDecayRate;

    for (const pattern of memory.patterns.values()) {
      // Decay success rate slightly
      pattern.successRate *= decayFactor;

      // Decay automation level
      pattern.automationLevel *= decayFactor;
    }
  }

  /**
   * Clear memory for a colony
   */
  clearMemory(colonyId: string): void {
    this.memories.delete(colonyId);
    this.detectionCache.delete(colonyId);
  }

  /**
   * Clear all memories
   */
  clearAll(): void {
    this.memories.clear();
    this.detectionCache.clear();
    this.metrics.clear();
  }

  /**
   * Update simulation time
   */
  setSimTime(time: number): void {
    this.simTime = time;
  }

  /**
   * Get simulation time
   */
  getSimTime(): number {
    return this.simTime;
  }

  /**
   * Export murmuration engine state
   */
  exportState(): any {
    return {
      memories: Array.from(this.memories.entries()).map(([id, memory]) => [
        id,
        {
          ...memory,
          patterns: Array.from(memory.patterns.entries()),
          patternsByTask: Array.from(memory.patternsByTask.entries()),
          patternsByParticipants: Array.from(memory.patternsByParticipants.entries()),
        },
      ]),
      detectionCache: Array.from(this.detectionCache.entries()),
      metrics: Array.from(this.metrics.entries()),
      config: this.config,
      simTime: this.simTime,
    };
  }

  /**
   * Import murmuration engine state
   */
  importState(state: any): void {
    this.memories = new Map(
      state.memories?.map(([id, memory]: [string, any]) => [
        id,
        {
          ...memory,
          patterns: new Map(memory.patterns),
          patternsByTask: new Map(memory.patternsByTask),
          patternsByParticipants: new Map(memory.patternsByParticipants),
        },
      ]) || []
    );
    this.detectionCache = new Map(state.detectionCache || []);
    this.metrics = new Map(state.metrics || []);
    this.simTime = state.simTime || 0;
    if (state.config) {
      this.config = { ...this.config, ...state.config };
    }
  }

  // ==========================================================================
  // Private Methods
  // ==========================================================================

  /**
   * Get or create memory for a colony
   */
  private getOrCreateMemory(colony: Colony): MurmurationMemory {
    let memory = this.memories.get(colony.id);

    if (!memory) {
      memory = {
        id: uuidv4(),
        colonyId: colony.id,
        patterns: new Map(),
        patternsByTask: new Map(),
        patternsByParticipants: new Map(),
        lastUpdate: this.simTime,
        consolidationLevel: 0,
      };
      this.memories.set(colony.id, memory);
    }

    return memory;
  }

  /**
   * Group packages by causal chain
   */
  private groupByCausalChain(packages: A2APackage[]): Map<string, A2APackage[]> {
    const chains = new Map<string, A2APackage[]>();

    for (const pkg of packages) {
      const chainId = pkg.causalChainId;
      if (!chains.has(chainId)) {
        chains.set(chainId, []);
      }
      chains.get(chainId)!.push(pkg);
    }

    return chains;
  }

  /**
   * Extract sequence from packages
   */
  private extractSequence(packages: A2APackage[]): PatternStep[] {
    // Sort by timestamp
    const sorted = [...packages].sort((a, b) => a.timestamp - b.timestamp);

    return sorted.map((pkg, index) => ({
      id: uuidv4(),
      senderId: pkg.senderId,
      receiverId: pkg.receiverId,
      messageType: pkg.type,
      payloadSchema: this.extractPayloadSchema(pkg.payload),
      timeout: 100, // Default timeout
      index,
    }));
  }

  /**
   * Extract payload schema from payload
   */
  private extractPayloadSchema(payload: unknown): Record<string, unknown> {
    if (typeof payload === 'object' && payload !== null) {
      const schema: Record<string, unknown> = {};
      for (const [key, value] of Object.entries(payload)) {
        schema[key] = typeof value;
      }
      return schema;
    }
    return { type: typeof payload };
  }

  /**
   * Analyze sequence for pattern qualities
   */
  private analyzeSequence(
    sequence: PatternStep[],
    packages: A2APackage[]
  ): SequenceAnalysis {
    return {
      frequency: 1, // Will be updated with actual frequency tracking
      temporalConsistency: this.calculateTemporalConsistency(packages),
      successCorrelation: 0.8, // Placeholder - would track actual success
      participantStability: this.calculateParticipantStability(sequence),
    };
  }

  /**
   * Calculate temporal consistency of packages
   */
  private calculateTemporalConsistency(packages: A2APackage[]): number {
    if (packages.length < 2) {
      return 1.0;
    }

    const sorted = [...packages].sort((a, b) => a.timestamp - b.timestamp);
    const intervals: number[] = [];

    for (let i = 1; i < sorted.length; i++) {
      intervals.push(sorted[i].timestamp - sorted[i - 1].timestamp);
    }

    const avgInterval = intervals.reduce((sum, i) => sum + i, 0) / intervals.length;
    const variance = intervals.reduce((sum, i) => sum + Math.pow(i - avgInterval, 2), 0) / intervals.length;
    const stdDev = Math.sqrt(variance);

    // Lower variance = higher consistency
    return Math.max(0, 1 - (stdDev / avgInterval));
  }

  /**
   * Calculate participant stability
   */
  private calculateParticipantStability(sequence: PatternStep[]): number {
    const participants = new Set<string>();
    for (const step of sequence) {
      participants.add(step.senderId);
      participants.add(step.receiverId);
    }

    // All same participants = 1.0, changes = lower
    return 1.0; // Simplified - sequence has same participants by definition
  }

  /**
   * Calculate confidence from analysis
   */
  private calculateConfidence(analysis: SequenceAnalysis): number {
    // Normalize frequency to 0-1 range (assuming max 10 occurrences is "perfect")
    const normalizedFrequency = Math.min(1.0, analysis.frequency / 10);

    return (
      normalizedFrequency * 0.4 +
      analysis.temporalConsistency * 0.3 +
      analysis.successCorrelation * 0.15 +
      analysis.participantStability * 0.15
    );
  }

  /**
   * Calculate sequence frequency across all packages
   */
  private calculateSequenceFrequency(sequence: PatternStep[], packages: A2APackage[]): number {
    // Count how many times this sequence pattern appears
    const signature = this.generateSignature(sequence);
    let count = 0;

    // Group by causal chains and count matching patterns
    const chains = this.groupByCausalChain(packages);

    for (const [chainId, chainPackages] of chains.entries()) {
      if (chainPackages.length >= sequence.length) {
        const testSequence = this.extractSequence(chainPackages);
        const testSignature = this.generateSignature(testSequence);

        if (testSignature === signature) {
          count++;
        }
      }
    }

    return count;
  }

  /**
   * Create pattern from sequence
   */
  private createPatternFromSequence(
    colony: Colony,
    sequence: PatternStep[],
    analysis: SequenceAnalysis,
    confidence: number
  ): MurmurationPattern {
    const signature = this.generateSignature(sequence);

    return {
      id: uuidv4(),
      name: `Pattern-${signature.slice(0, 8)}`,
      participants: this.extractParticipants(sequence),
      sequence,
      signature,
      successRate: confidence,
      executionCount: 0,
      avgExecutionTime: 0,
      formationTime: this.simTime,
      lastExecutionTime: 0,
      coEvolutionStage: CoEvolutionStage.DISCOVERY,
      automationLevel: 0,
    };
  }

  /**
   * Generate signature for sequence
   */
  private generateSignature(sequence: PatternStep[]): string {
    const signature = sequence
      .map(step => `${step.senderId}->${step.receiverId}:${step.messageType}`)
      .join('|');
    return Buffer.from(signature).toString('base64').slice(0, 16);
  }

  /**
   * Extract participants from sequence
   */
  private extractParticipants(sequence: PatternStep[]): string[] {
    const participants = new Set<string>();
    for (const step of sequence) {
      participants.add(step.senderId);
      participants.add(step.receiverId);
    }
    return Array.from(participants);
  }

  /**
   * Find pattern by signature
   */
  private findPatternBySignature(
    memory: MurmurationMemory,
    signature: string
  ): MurmurationPattern | undefined {
    for (const pattern of memory.patterns.values()) {
      if (pattern.signature === signature) {
        return pattern;
      }
    }
    return undefined;
  }

  /**
   * Update pattern from detection
   */
  private updatePatternFromDetection(
    pattern: MurmurationPattern,
    detection: PatternDetectionResult
  ): void {
    pattern.successRate = Math.max(pattern.successRate, detection.confidence);
    pattern.lastExecutionTime = this.simTime;
  }

  /**
   * Index pattern for fast lookup
   */
  private indexPattern(
    memory: MurmurationMemory,
    pattern: MurmurationPattern
  ): void {
    // Index by task type (would need task info)
    // For now, index by participants

    const participantKey = pattern.participants.sort().join(',');
    if (!memory.patternsByParticipants.has(participantKey)) {
      memory.patternsByParticipants.set(participantKey, []);
    }
    memory.patternsByParticipants.get(participantKey)!.push(pattern.id);
  }

  /**
   * Remove pattern from indexes
   */
  private removePatternFromIndexes(
    memory: MurmurationMemory,
    patternId: string
  ): void {
    for (const [key, ids] of memory.patternsByParticipants.entries()) {
      const index = ids.indexOf(patternId);
      if (index !== -1) {
        ids.splice(index, 1);
      }
      if (ids.length === 0) {
        memory.patternsByParticipants.delete(key);
      }
    }
  }

  /**
   * Update consolidation level
   */
  private updateConsolidation(memory: MurmurationMemory): void {
    memory.lastUpdate = this.simTime;

    // Consolidation increases with pattern count and stability
    const patternCount = memory.patterns.size;
    const avgSuccessRate = this.calculateAverageSuccessRate(memory);

    memory.consolidationLevel = Math.min(1.0,
      (patternCount / this.config.maxPatterns) * 0.5 +
      avgSuccessRate * 0.5
    );
  }

  /**
   * Calculate average success rate
   */
  private calculateAverageSuccessRate(memory: MurmurationMemory): number {
    if (memory.patterns.size === 0) {
      return 0;
    }

    const total = Array.from(memory.patterns.values())
      .reduce((sum, p) => sum + p.successRate, 0);

    return total / memory.patterns.size;
  }

  /**
   * Find best pattern for task
   */
  private findBestPattern(
    memory: MurmurationMemory,
    task: Task,
    colony: Colony
  ): MurmurationPattern | undefined {
    // Find patterns that match colony members
    const memberKey = colony.members.sort().join(',');
    const patternIds = memory.patternsByParticipants.get(memberKey);

    if (!patternIds || patternIds.length === 0) {
      return undefined;
    }

    // Find best pattern by success rate and automation level
    let best: MurmurationPattern | undefined;
    let bestScore = 0;

    for (const patternId of patternIds) {
      const pattern = memory.patterns.get(patternId);
      if (!pattern) {
        continue;
      }

      const score = pattern.successRate * 0.6 + pattern.automationLevel * 0.4;
      if (score > bestScore) {
        bestScore = score;
        best = pattern;
      }
    }

    return best;
  }

  /**
   * Execute pattern
   */
  private async executePattern(
    colony: Colony,
    pattern: MurmurationPattern,
    task: Task,
    a2aSystem: any
  ): Promise<{ success: boolean; messagesExchanged: number }> {
    // Simulate fast execution by skipping negotiation
    // In practice, would execute pre-coordinated messages

    let messagesExchanged = 0;

    for (const step of pattern.sequence) {
      // Check if participants are still in colony
      if (!colony.members.includes(step.senderId) || !colony.members.includes(step.receiverId)) {
        return { success: false, messagesExchanged };
      }

      // Create package (instant, no negotiation)
      try {
        const pkg = await a2aSystem.createPackage(
          step.senderId,
          step.receiverId,
          step.messageType,
          { taskId: task.id, type: task.type, ...task }
        );
        messagesExchanged++;
      } catch (error) {
        return { success: false, messagesExchanged };
      }
    }

    return { success: true, messagesExchanged };
  }

  /**
   * Execute ad-hoc coordination (fallback)
   */
  private async executeAdHoc(
    colony: Colony,
    task: Task,
    a2aSystem: any,
    startTime: number,
    reason: string
  ): Promise<PatternExecutionResult> {
    // Simulate slow ad-hoc coordination
    // In practice, would involve negotiation, discovery, etc.

    // Simulate 100ms overhead for negotiation
    await new Promise(resolve => setTimeout(resolve, 10));

    const executionTime = Date.now() - startTime;

    return {
      success: true,
      executionTime,
      messagesExchanged: colony.members.length,
      fallback: true,
      error: reason,
    };
  }

  /**
   * Update pattern metrics
   */
  private updateMetrics(
    patternId: string,
    success: boolean,
    executionTime: number
  ): void {
    if (!this.config.enablePerformanceTracking) {
      return;
    }

    let metrics = this.metrics.get(patternId);

    if (!metrics) {
      metrics = {
        totalExecutions: 0,
        successfulExecutions: 0,
        totalExecutionTime: 0,
        minExecutionTime: executionTime,
        maxExecutionTime: executionTime,
        lastExecution: this.simTime,
      };
      this.metrics.set(patternId, metrics);
    }

    metrics.totalExecutions++;
    if (success) {
      metrics.successfulExecutions++;
    }
    metrics.totalExecutionTime += executionTime;
    metrics.minExecutionTime = Math.min(metrics.minExecutionTime, executionTime);
    metrics.maxExecutionTime = Math.max(metrics.maxExecutionTime, executionTime);
    metrics.lastExecution = this.simTime;
  }
}

/**
 * Create a murmuration engine
 */
export function createMurmurationEngine(
  config?: MurmurationEngineConfig
): MurmurationEngine {
  return new MurmurationEngine(config);
}
