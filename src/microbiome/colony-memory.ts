/**
 * POLLN Microbiome - Colony Memory System
 *
 * Long-term memory storage and retrieval for colonies.
 * Colonies learn from successful patterns and transfer knowledge
 * across time and space through episodic and semantic memory.
 *
 * @module microbiome/colony-memory
 */

import { v4 as uuidv4 } from 'uuid';
import type { Colony, Task } from './colony.js';
import type { MurmurationPattern, MurmurationMemory } from './murmuration.js';

/**
 * Memory pattern - stored successful configuration
 */
export interface MemoryPattern {
  /** Pattern ID */
  id: string;
  /** Pattern name */
  name: string;
  /** Pattern type */
  type: PatternType;
  /** Colony configuration */
  colonyConfig: ColonyConfiguration;
  /** Task type this pattern is for */
  taskType: string;
  /** Success rate (0-1) */
  successRate: number;
  /** Usage count */
  usageCount: number;
  /** Formation timestamp */
  formationTime: number;
  /** Last access timestamp */
  lastAccessTime: number;
  /** Last update timestamp */
  lastUpdateTime: number;
  /** Memory strength (0-1) */
  strength: number;
  /** Importance score (0-1) */
  importance: number;
  /** Associated murmuration pattern (if any) */
  murmurationPattern?: MurmurationPattern;
  /** Tags for semantic retrieval */
  tags: string[];
  /** Embedding vector for similarity search */
  embedding?: number[];
}

/**
 * Pattern type enumeration
 */
export enum PatternType {
  /** Murmuration coordination pattern */
  MURMURATION = 'murmuration',
  /** Colony configuration pattern */
  COLONY_CONFIG = 'colony_config',
  /** Task execution template */
  TASK_TEMPLATE = 'task_template',
  /** Specialized role assignment */
  ROLE_ASSIGNMENT = 'role_assignment',
}

/**
 * Colony configuration snapshot
 */
export interface ColonyConfiguration {
  /** Member agent IDs */
  members: string[];
  /** Member roles */
  roles: Map<string, string>;
  /** Specializations */
  specializations: string[];
  /** Communication topology */
  communicationTopology: Map<string, string[]>;
  /** Expected efficiency gain */
  expectedEfficiency: number;
  /** Stability score */
  stability: number;
}

/**
 * Memory retrieval result
 */
export interface MemoryRetrievalResult {
  /** Retrieved patterns */
  patterns: MemoryPattern[];
  /** Confidence scores (0-1) */
  confidences: number[];
  /** Similarity scores (0-1) */
  similarities: number[];
  /** Query used */
  query: MemoryQuery;
}

/**
 * Memory query for retrieval
 */
export interface MemoryQuery {
  /** Task type to match */
  taskType?: string;
  /** Member IDs to match */
  members?: string[];
  /** Tags to match */
  tags?: string[];
  /** Minimum success rate */
  minSuccessRate?: number;
  /** Minimum strength */
  minStrength?: number;
  /** Pattern types to include */
  patternTypes?: PatternType[];
  /** Maximum results */
  maxResults?: number;
  /** Embedding for similarity search */
  embedding?: number[];
  /** Similarity threshold (0-1) */
  similarityThreshold?: number;
}

/**
 * Consolidation result
 */
export interface ConsolidationResult {
  /** Patterns strengthened */
  strengthened: number;
  /** Patterns merged */
  merged: number;
  /** Patterns pruned */
  pruned: number;
  /** New long-term memories */
  longTermMemories: number;
  /** Consolidation time (ms) */
  consolidationTime: number;
}

/**
 * Decay result
 */
export interface DecayResult {
  /** Patterns decayed */
  decayed: number;
  /** Patterns forgotten (removed) */
  forgotten: number;
  /** Patterns preserved */
  preserved: number;
  /** Average strength remaining */
  avgStrength: number;
}

/**
 * Memory transfer result
 */
export interface MemoryTransferResult {
  /** Patterns transferred */
  transferred: number;
  /** Patterns skipped (already present) */
  skipped: number;
  /** Patterns merged (combined with existing) */
  merged: number;
  /** Transfer confidence (0-1) */
  confidence: number;
}

/**
 * Colony memory configuration
 */
export interface ColonyMemoryConfig {
  /** Maximum patterns per colony */
  maxPatterns?: number;
  /** Memory decay rate (per hour) */
  decayRate?: number;
  /** Consolidation interval (ms) */
  consolidationInterval?: number;
  /** Minimum strength for retention */
  minStrength?: number;
  /** Forgetting curve exponent */
  forgettingExponent?: number;
  /** Importance decay rate */
  importanceDecayRate?: number;
  /** Similarity threshold for merging */
  mergeSimilarityThreshold?: number;
  /** Enable semantic memory */
  enableSemanticMemory?: boolean;
  /** Enable episodic memory */
  enableEpisodicMemory?: boolean;
}

/**
 * Colony memory statistics
 */
export interface ColonyMemoryStats {
  /** Total patterns stored */
  totalPatterns: number;
  /** Patterns by type */
  patternsByType: Map<PatternType, number>;
  /** Average strength */
  avgStrength: number;
  /** Average importance */
  avgImportance: number;
  /** Total access count */
  totalAccessCount: number;
  /** Long-term memory count */
  longTermMemoryCount: number;
  /** Most accessed patterns */
  mostAccessed: MemoryPattern[];
  /** Strongest patterns */
  strongest: MemoryPattern[];
}

/**
 * ColonyMemory - Long-term memory storage and retrieval for colonies
 *
 * Key insight: "Colonies remember successful configurations through
 * episodic and semantic memory, enabling knowledge transfer across
 * time and colony instances."
 */
export class ColonyMemory {
  /** Memory patterns by colony */
  private memories: Map<string, Map<string, MemoryPattern>>;
  /** Semantic index (tag -> pattern IDs) */
  private semanticIndex: Map<string, Set<string>>;
  /** Episodic index (timestamp -> pattern IDs) */
  private episodicIndex: Map<number, Set<string>>;
  /** Colony index (colony ID -> pattern IDs) */
  private colonyIndex: Map<string, Set<string>>;
  /** Task type index (task type -> pattern IDs) */
  private taskIndex: Map<string, Set<string>>;
  /** Access tracking (pattern ID -> count) */
  private accessCounts: Map<string, number>;
  /** Long-term memories (consolidated patterns) */
  private longTermMemories: Set<string>;
  /** Configuration */
  private config: Required<ColonyMemoryConfig>;
  /** Current simulation time */
  private simTime: number;
  /** Last consolidation time */
  private lastConsolidationTime: number;

  constructor(config: ColonyMemoryConfig = {}) {
    this.memories = new Map();
    this.semanticIndex = new Map();
    this.episodicIndex = new Map();
    this.colonyIndex = new Map();
    this.taskIndex = new Map();
    this.accessCounts = new Map();
    this.longTermMemories = new Set();
    this.simTime = 0;
    this.lastConsolidationTime = 0;

    this.config = {
      maxPatterns: config.maxPatterns ?? 100,
      decayRate: config.decayRate ?? 0.1,
      consolidationInterval: config.consolidationInterval ?? 10000,
      minStrength: config.minStrength ?? 0.1,
      forgettingExponent: config.forgettingExponent ?? 1.5,
      importanceDecayRate: config.importanceDecayRate ?? 0.05,
      mergeSimilarityThreshold: config.mergeSimilarityThreshold ?? 0.85,
      enableSemanticMemory: config.enableSemanticMemory ?? true,
      enableEpisodicMemory: config.enableEpisodicMemory ?? true,
    };
  }

  /**
   * Store a successful pattern in memory
   * Stores murmuration patterns, colony configurations, and task templates
   */
  storePattern(
    colony: Colony,
    patternType: PatternType,
    config: ColonyConfiguration,
    taskType: string,
    murmurationPattern?: MurmurationPattern,
    tags: string[] = []
  ): MemoryPattern {
    // Get or create memory for this colony
    let colonyMemory = this.memories.get(colony.id);
    if (!colonyMemory) {
      colonyMemory = new Map();
      this.memories.set(colony.id, colonyMemory);
    }

    // Check if under max patterns
    if (colonyMemory.size >= this.config.maxPatterns) {
      // Prune weakest pattern
      this.pruneWeakestPattern(colony.id);
    }

    // Create pattern
    const pattern: MemoryPattern = {
      id: uuidv4(),
      name: `${patternType}-${taskType}-${colony.id.slice(0, 8)}`,
      type: patternType,
      colonyConfig: config,
      taskType,
      successRate: 0.8, // Initial success rate
      usageCount: 0,
      formationTime: this.simTime,
      lastAccessTime: this.simTime,
      lastUpdateTime: this.simTime,
      strength: 0.5, // Initial strength
      importance: this.calculateImportance(config, taskType),
      murmurationPattern,
      tags: [...tags, taskType, patternType],
      embedding: this.generateEmbedding(config, taskType),
    };

    // Store pattern
    colonyMemory.set(pattern.id, pattern);

    // Index pattern
    this.indexPattern(pattern, colony.id);

    // Initialize access count
    this.accessCounts.set(pattern.id, 0);

    return pattern;
  }

  /**
   * Retrieve patterns similar to a query
   * Uses semantic and episodic memory for context-aware retrieval
   */
  retrievePattern(query: MemoryQuery): MemoryRetrievalResult {
    const allPatterns = this.collectAllPatterns();
    let candidates = allPatterns;

    // Filter by pattern types
    if (query.patternTypes && query.patternTypes.length > 0) {
      candidates = candidates.filter(p => query.patternTypes!.includes(p.type));
    }

    // Filter by task type
    if (query.taskType) {
      candidates = candidates.filter(p => p.taskType === query.taskType);
    }

    // Filter by members
    if (query.members && query.members.length > 0) {
      candidates = candidates.filter(p =>
        this.hasMembers(p, query.members!)
      );
    }

    // Filter by tags
    if (query.tags && query.tags.length > 0) {
      candidates = candidates.filter(p =>
        query.tags!.some(tag => p.tags.includes(tag))
      );
    }

    // Filter by minimum success rate
    if (query.minSuccessRate !== undefined) {
      candidates = candidates.filter(p => p.successRate >= query.minSuccessRate!);
    }

    // Filter by minimum strength
    if (query.minStrength !== undefined) {
      candidates = candidates.filter(p => p.strength >= query.minStrength!);
    }

    // Calculate similarity scores
    const similarities = candidates.map(p =>
      this.calculateSimilarity(p, query)
    );

    // Filter by similarity threshold
    if (query.similarityThreshold !== undefined) {
      const filtered: MemoryPattern[] = [];
      const filteredSims: number[] = [];
      for (let i = 0; i < candidates.length; i++) {
        if (similarities[i] >= query.similarityThreshold!) {
          filtered.push(candidates[i]);
          filteredSims.push(similarities[i]);
        }
      }
      candidates = filtered;
      similarities.length = 0;
      similarities.push(...filteredSims);
    }

    // Sort by combined score (similarity + success + strength)
    const combinedScores = candidates.map((p, i) => ({
      pattern: p,
      score: similarities[i] * 0.4 + p.successRate * 0.3 + p.strength * 0.3,
    }));

    combinedScores.sort((a, b) => b.score - a.score);

    // Limit results
    const maxResults = query.maxResults ?? 10;
    const topPatterns = combinedScores.slice(0, maxResults);

    // Update access tracking
    for (const { pattern } of topPatterns) {
      this.updateAccess(pattern.id);
    }

    return {
      patterns: topPatterns.map(s => s.pattern),
      confidences: topPatterns.map(s => s.score),
      similarities: topPatterns.map(s =>
        similarities[candidates.indexOf(s.pattern)]
      ),
      query,
    };
  }

  /**
   * Consolidate important memories
   * Strengthens frequently-used patterns and merges similar ones
   */
  consolidate(): ConsolidationResult {
    const startTime = Date.now();
    let strengthened = 0;
    let merged = 0;
    let pruned = 0;
    let longTermMemories = 0;

    // Process each colony's memory
    for (const [colonyId, colonyMemory] of this.memories.entries()) {
      const patterns = Array.from(colonyMemory.values());

      // Strengthen frequently-used patterns
      for (const pattern of patterns) {
        const accessCount = this.accessCounts.get(pattern.id) ?? 0;

        if (accessCount > 5) {
          // Strengthen based on usage
          const strengthBonus = Math.min(0.3, accessCount * 0.05);
          pattern.strength = Math.min(1.0, pattern.strength + strengthBonus);
          pattern.importance = Math.min(1.0, pattern.importance + strengthBonus * 0.5);
          strengthened++;
        }

        // Mark as long-term memory if very strong
        if (pattern.strength > 0.9 && pattern.importance > 0.8) {
          this.longTermMemories.add(pattern.id);
          longTermMemories++;
        }
      }

      // Merge similar patterns
      const toMerge = this.findSimilarPatterns(colonyId);
      for (const [id1, id2] of toMerge) {
        const pattern1 = colonyMemory.get(id1);
        const pattern2 = colonyMemory.get(id2);

        if (pattern1 && pattern2) {
          this.mergePatterns(pattern1, pattern2);
          colonyMemory.delete(id2);
          this.removeFromIndexes(id2);
          merged++;
        }
      }

      // Prune weak patterns
      const toPrune = patterns.filter(p =>
        p.strength < this.config.minStrength &&
        !this.longTermMemories.has(p.id)
      );

      for (const pattern of toPrune) {
        colonyMemory.delete(pattern.id);
        this.removeFromIndexes(pattern.id);
        this.accessCounts.delete(pattern.id);
        pruned++;
      }
    }

    this.lastConsolidationTime = this.simTime;

    const consolidationTime = Date.now() - startTime;

    return {
      strengthened,
      merged,
      pruned,
      longTermMemories,
      consolidationTime,
    };
  }

  /**
   * Decay unused memories over time
   * Implements forgetting curve with exponential decay
   */
  decay(): DecayResult {
    let decayed = 0;
    let forgotten = 0;
    let preserved = 0;
    let totalStrength = 0;

    for (const colonyMemory of this.memories.values()) {
      for (const pattern of colonyMemory.values()) {
        // Skip long-term memories
        if (this.longTermMemories.has(pattern.id)) {
          preserved++;
          totalStrength += pattern.strength;
          continue;
        }

        // Calculate time since last access
        const timeSinceAccess = this.simTime - pattern.lastAccessTime;

        // Apply forgetting curve (exponential decay)
        const decayFactor = Math.exp(
          -this.config.decayRate * Math.pow(timeSinceAccess / 1000, this.config.forgettingExponent)
        );

        // Decay strength
        const oldStrength = pattern.strength;
        pattern.strength *= decayFactor;

        // Decay importance slowly
        pattern.importance *= (1 - this.config.importanceDecayRate);

        if (pattern.strength < oldStrength) {
          decayed++;
        }

        // Forget if below threshold
        if (pattern.strength < this.config.minStrength) {
          forgotten++;
        } else {
          preserved++;
          totalStrength += pattern.strength;
        }
      }
    }

    // Remove forgotten patterns
    this.removeForgottenPatterns();

    const avgStrength = preserved > 0 ? totalStrength / preserved : 0;

    return {
      decayed,
      forgotten,
      preserved,
      avgStrength,
    };
  }

  /**
   * Transfer memory between colonies
   * Enables knowledge sharing across colony instances
   */
  transferMemory(
    fromColonyId: string,
    toColonyId: string,
    selective: boolean = true
  ): MemoryTransferResult {
    const sourceMemory = this.memories.get(fromColonyId);
    if (!sourceMemory) {
      return {
        transferred: 0,
        skipped: 0,
        merged: 0,
        confidence: 0,
      };
    }

    // Get or create target memory
    let targetMemory = this.memories.get(toColonyId);
    if (!targetMemory) {
      targetMemory = new Map();
      this.memories.set(toColonyId, targetMemory);
    }

    let transferred = 0;
    let skipped = 0;
    let merged = 0;

    // Select patterns to transfer
    let patternsToTransfer = Array.from(sourceMemory.values());

    if (selective) {
      // Only transfer important patterns
      patternsToTransfer = patternsToTransfer.filter(p =>
        p.importance > 0.5 && p.strength > 0.6
      );
    }

    // Transfer patterns
    for (const pattern of patternsToTransfer) {
      // Check if similar pattern exists in target
      const existing = this.findSimilarInTarget(targetMemory, pattern);

      if (existing) {
        // Merge with existing
        this.mergePatterns(existing, pattern, 0.5);
        merged++;
      } else {
        // Create copy for target
        const copy: MemoryPattern = {
          ...pattern,
          id: uuidv4(),
          formationTime: this.simTime,
          lastAccessTime: this.simTime,
          lastUpdateTime: this.simTime,
          strength: pattern.strength * 0.8, // Slight penalty for transfer
          usageCount: 0,
        };

        targetMemory.set(copy.id, copy);
        this.indexPattern(copy, toColonyId);
        this.accessCounts.set(copy.id, 0);
        transferred++;
      }
    }

    // Calculate confidence based on transfer quality
    const confidence = patternsToTransfer.length > 0
      ? (transferred + merged) / patternsToTransfer.length
      : 0;

    return {
      transferred,
      skipped,
      merged,
      confidence,
    };
  }

  /**
   * Get memory for a colony
   */
  getMemory(colonyId: string): Map<string, MemoryPattern> | undefined {
    return this.memories.get(colonyId);
  }

  /**
   * Get pattern by ID
   */
  getPattern(colonyId: string, patternId: string): MemoryPattern | undefined {
    const colonyMemory = this.memories.get(colonyId);
    return colonyMemory?.get(patternId);
  }

  /**
   * Get statistics for a colony
   */
  getStats(colonyId: string): ColonyMemoryStats | undefined {
    const colonyMemory = this.memories.get(colonyId);
    if (!colonyMemory) {
      return undefined;
    }

    const patterns = Array.from(colonyMemory.values());

    const patternsByType = new Map<PatternType, number>();
    for (const type of Object.values(PatternType)) {
      patternsByType.set(type, patterns.filter(p => p.type === type).length);
    }

    const avgStrength = patterns.length > 0
      ? patterns.reduce((sum, p) => sum + p.strength, 0) / patterns.length
      : 0;

    const avgImportance = patterns.length > 0
      ? patterns.reduce((sum, p) => sum + p.importance, 0) / patterns.length
      : 0;

    const totalAccessCount = patterns.reduce((sum, p) => {
      return sum + (this.accessCounts.get(p.id) ?? 0);
    }, 0);

    const longTermMemoryCount = patterns.filter(p =>
      this.longTermMemories.has(p.id)
    ).length;

    const mostAccessed = [...patterns]
      .sort((a, b) => (this.accessCounts.get(b.id) ?? 0) - (this.accessCounts.get(a.id) ?? 0))
      .slice(0, 5);

    const strongest = [...patterns]
      .sort((a, b) => b.strength - a.strength)
      .slice(0, 5);

    return {
      totalPatterns: patterns.length,
      patternsByType,
      avgStrength,
      avgImportance,
      totalAccessCount,
      longTermMemoryCount,
      mostAccessed,
      strongest,
    };
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
   * Check if consolidation is needed
   */
  needsConsolidation(): boolean {
    return this.simTime - this.lastConsolidationTime >= this.config.consolidationInterval;
  }

  /**
   * Clear memory for a colony
   */
  clearMemory(colonyId: string): void {
    const colonyMemory = this.memories.get(colonyId);
    if (colonyMemory) {
      for (const patternId of colonyMemory.keys()) {
        this.removeFromIndexes(patternId);
        this.accessCounts.delete(patternId);
      }
    }
    this.memories.delete(colonyId);
  }

  /**
   * Clear all memories
   */
  clearAll(): void {
    this.memories.clear();
    this.semanticIndex.clear();
    this.episodicIndex.clear();
    this.colonyIndex.clear();
    this.taskIndex.clear();
    this.accessCounts.clear();
    this.longTermMemories.clear();
  }

  /**
   * Export colony memory state
   */
  exportState(): any {
    return {
      memories: Array.from(this.memories.entries()).map(([colonyId, patterns]) => [
        colonyId,
        Array.from(patterns.entries()),
      ]),
      semanticIndex: Array.from(this.semanticIndex.entries()),
      episodicIndex: Array.from(this.episodicIndex.entries()),
      colonyIndex: Array.from(this.colonyIndex.entries()),
      taskIndex: Array.from(this.taskIndex.entries()),
      accessCounts: Array.from(this.accessCounts.entries()),
      longTermMemories: Array.from(this.longTermMemories),
      config: this.config,
      simTime: this.simTime,
      lastConsolidationTime: this.lastConsolidationTime,
    };
  }

  /**
   * Import colony memory state
   */
  importState(state: any): void {
    this.memories = new Map(
      state.memories?.map(([colonyId, patterns]: [string, any]) => [
        colonyId,
        new Map(patterns),
      ]) || []
    );
    this.semanticIndex = new Map(
      state.semanticIndex?.map(([tag, ids]: [string, string[]]) => [tag, new Set(ids)]) || []
    );
    this.episodicIndex = new Map(
      state.episodicIndex?.map(([time, ids]: [number, string[]]) => [time, new Set(ids)]) || []
    );
    this.colonyIndex = new Map(
      state.colonyIndex?.map(([colonyId, ids]: [string, string[]]) => [colonyId, new Set(ids)]) || []
    );
    this.taskIndex = new Map(
      state.taskIndex?.map(([taskType, ids]: [string, string[]]) => [taskType, new Set(ids)]) || []
    );
    this.accessCounts = new Map(state.accessCounts || []);
    this.longTermMemories = new Set(state.longTermMemories || []);
    this.simTime = state.simTime || 0;
    this.lastConsolidationTime = state.lastConsolidationTime || 0;
    if (state.config) {
      this.config = { ...this.config, ...state.config };
    }
  }

  // ==========================================================================
  // Private Methods
  // ==========================================================================

  /**
   * Calculate importance of a pattern
   */
  private calculateImportance(config: ColonyConfiguration, taskType: string): number {
    let importance = 0.5;

    // Higher importance for larger colonies
    importance += Math.min(0.2, config.members.length * 0.02);

    // Higher importance for higher efficiency
    importance += config.expectedEfficiency * 0.2;

    // Higher importance for more stable colonies
    importance += config.stability * 0.1;

    return Math.min(1.0, importance);
  }

  /**
   * Generate embedding for similarity search
   */
  private generateEmbedding(config: ColonyConfiguration, taskType: string): number[] {
    // Simple embedding based on configuration features
    const embedding: number[] = [];

    // Colony size feature
    embedding.push(Math.min(1.0, config.members.length / 20));

    // Efficiency feature
    embedding.push(config.expectedEfficiency);

    // Stability feature
    embedding.push(config.stability);

    // Specialization count feature
    embedding.push(Math.min(1.0, config.specializations.length / 5));

    // Task type hash (simple numeric representation)
    const taskHash = taskType.split('').reduce((sum, char) => sum + char.charCodeAt(0), 0);
    embedding.push((taskHash % 100) / 100);

    return embedding;
  }

  /**
   * Index pattern for fast retrieval
   */
  private indexPattern(pattern: MemoryPattern, colonyId: string): void {
    // Semantic index (tags)
    if (this.config.enableSemanticMemory) {
      for (const tag of pattern.tags) {
        if (!this.semanticIndex.has(tag)) {
          this.semanticIndex.set(tag, new Set());
        }
        this.semanticIndex.get(tag)!.add(pattern.id);
      }
    }

    // Episodic index (timestamp)
    if (this.config.enableEpisodicMemory) {
      const timeBucket = Math.floor(pattern.formationTime / 1000) * 1000;
      if (!this.episodicIndex.has(timeBucket)) {
        this.episodicIndex.set(timeBucket, new Set());
      }
      this.episodicIndex.get(timeBucket)!.add(pattern.id);
    }

    // Colony index
    if (!this.colonyIndex.has(colonyId)) {
      this.colonyIndex.set(colonyId, new Set());
    }
    this.colonyIndex.get(colonyId)!.add(pattern.id);

    // Task index
    if (!this.taskIndex.has(pattern.taskType)) {
      this.taskIndex.set(pattern.taskType, new Set());
    }
    this.taskIndex.get(pattern.taskType)!.add(pattern.id);
  }

  /**
   * Remove pattern from indexes
   */
  private removeFromIndexes(patternId: string): void {
    for (const ids of this.semanticIndex.values()) {
      ids.delete(patternId);
    }
    for (const ids of this.episodicIndex.values()) {
      ids.delete(patternId);
    }
    for (const ids of this.colonyIndex.values()) {
      ids.delete(patternId);
    }
    for (const ids of this.taskIndex.values()) {
      ids.delete(patternId);
    }
  }

  /**
   * Collect all patterns from all colonies
   */
  private collectAllPatterns(): MemoryPattern[] {
    const allPatterns: MemoryPattern[] = [];
    for (const colonyMemory of this.memories.values()) {
      allPatterns.push(...Array.from(colonyMemory.values()));
    }
    return allPatterns;
  }

  /**
   * Check if pattern has specified members
   */
  private hasMembers(pattern: MemoryPattern, members: string[]): boolean {
    const patternMembers = new Set(pattern.colonyConfig.members);
    return members.every(m => patternMembers.has(m));
  }

  /**
   * Calculate similarity between pattern and query
   */
  private calculateSimilarity(pattern: MemoryPattern, query: MemoryQuery): number {
    let similarity = 0.5;

    // Embedding similarity
    if (query.embedding && pattern.embedding) {
      const cosSim = this.cosineSimilarity(query.embedding, pattern.embedding);
      similarity += cosSim * 0.3;
    }

    // Tag similarity
    if (query.tags && query.tags.length > 0) {
      const matchingTags = query.tags.filter(t => pattern.tags.includes(t)).length;
      similarity += (matchingTags / query.tags.length) * 0.2;
    }

    // Member similarity
    if (query.members && query.members.length > 0) {
      const matchingMembers = query.members.filter(m =>
        pattern.colonyConfig.members.includes(m)
      ).length;
      similarity += (matchingMembers / query.members.length) * 0.2;
    }

    return Math.min(1.0, similarity);
  }

  /**
   * Calculate cosine similarity between vectors
   */
  private cosineSimilarity(vec1: number[], vec2: number[]): number {
    if (vec1.length !== vec2.length) {
      return 0;
    }

    let dotProduct = 0;
    let norm1 = 0;
    let norm2 = 0;

    for (let i = 0; i < vec1.length; i++) {
      dotProduct += vec1[i] * vec2[i];
      norm1 += vec1[i] * vec1[i];
      norm2 += vec2[i] * vec2[i];
    }

    norm1 = Math.sqrt(norm1);
    norm2 = Math.sqrt(norm2);

    if (norm1 === 0 || norm2 === 0) {
      return 0;
    }

    return dotProduct / (norm1 * norm2);
  }

  /**
   * Update access tracking for pattern
   */
  private updateAccess(patternId: string): void {
    const currentCount = this.accessCounts.get(patternId) ?? 0;
    this.accessCounts.set(patternId, currentCount + 1);
  }

  /**
   * Find similar patterns in colony memory
   */
  private findSimilarPatterns(colonyId: string): [string, string][] {
    const colonyMemory = this.memories.get(colonyId);
    if (!colonyMemory) {
      return [];
    }

    const patterns = Array.from(colonyMemory.values());
    const similarPairs: [string, string][] = [];

    for (let i = 0; i < patterns.length; i++) {
      for (let j = i + 1; j < patterns.length; j++) {
        const p1 = patterns[i];
        const p2 = patterns[j];

        // Calculate similarity
        let similarity = 0;

        // Same task type
        if (p1.taskType === p2.taskType) {
          similarity += 0.3;
        }

        // Same pattern type
        if (p1.type === p2.type) {
          similarity += 0.2;
        }

        // Member overlap
        const members1 = new Set(p1.colonyConfig.members);
        const members2 = new Set(p2.colonyConfig.members);
        const intersection = new Set([...members1].filter(m => members2.has(m)));
        const union = new Set([...members1, ...members2]);
        similarity += (intersection.size / union.size) * 0.3;

        // Tag overlap
        const tags1 = new Set(p1.tags);
        const tags2 = new Set(p2.tags);
        const tagIntersection = new Set([...tags1].filter(t => tags2.has(t)));
        const tagUnion = new Set([...tags1, ...tags2]);
        similarity += (tagIntersection.size / tagUnion.size) * 0.2;

        if (similarity >= this.config.mergeSimilarityThreshold) {
          similarPairs.push([p1.id, p2.id]);
        }
      }
    }

    return similarPairs;
  }

  /**
   * Find similar pattern in target memory
   */
  private findSimilarInTarget(
    targetMemory: Map<string, MemoryPattern>,
    pattern: MemoryPattern
  ): MemoryPattern | undefined {
    for (const targetPattern of targetMemory.values()) {
      let similarity = 0;

      if (targetPattern.taskType === pattern.taskType) {
        similarity += 0.4;
      }

      if (targetPattern.type === pattern.type) {
        similarity += 0.3;
      }

      const tagOverlap = pattern.tags.filter(t => targetPattern.tags.includes(t)).length;
      similarity += (tagOverlap / pattern.tags.length) * 0.3;

      if (similarity >= this.config.mergeSimilarityThreshold) {
        return targetPattern;
      }
    }

    return undefined;
  }

  /**
   * Merge two patterns
   */
  private mergePatterns(
    target: MemoryPattern,
    source: MemoryPattern,
    weight: number = 0.5
  ): void {
    // Merge success rates
    target.successRate = target.successRate * (1 - weight) + source.successRate * weight;

    // Merge strength
    target.strength = Math.min(1.0, target.strength + source.strength * weight);

    // Merge importance
    target.importance = Math.min(1.0, target.importance + source.importance * weight * 0.5);

    // Merge tags
    for (const tag of source.tags) {
      if (!target.tags.includes(tag)) {
        target.tags.push(tag);
      }
    }

    // Update timestamp
    target.lastUpdateTime = this.simTime;
  }

  /**
   * Prune weakest pattern from colony memory
   */
  private pruneWeakestPattern(colonyId: string): void {
    const colonyMemory = this.memories.get(colonyId);
    if (!colonyMemory || colonyMemory.size === 0) {
      return;
    }

    let weakest: MemoryPattern | undefined;
    let lowestStrength = 1.0;

    for (const pattern of colonyMemory.values()) {
      // Skip long-term memories
      if (this.longTermMemories.has(pattern.id)) {
        continue;
      }

      if (pattern.strength < lowestStrength) {
        lowestStrength = pattern.strength;
        weakest = pattern;
      }
    }

    if (weakest) {
      colonyMemory.delete(weakest.id);
      this.removeFromIndexes(weakest.id);
      this.accessCounts.delete(weakest.id);
    }
  }

  /**
   * Remove forgotten patterns
   */
  private removeForgottenPatterns(): void {
    for (const [colonyId, colonyMemory] of this.memories.entries()) {
      const toDelete: string[] = [];

      for (const [patternId, pattern] of colonyMemory.entries()) {
        if (pattern.strength < this.config.minStrength &&
            !this.longTermMemories.has(patternId)) {
          toDelete.push(patternId);
        }
      }

      for (const patternId of toDelete) {
        colonyMemory.delete(patternId);
        this.removeFromIndexes(patternId);
        this.accessCounts.delete(patternId);
      }
    }
  }
}

/**
 * Create a colony memory system
 */
export function createColonyMemory(config?: ColonyMemoryConfig): ColonyMemory {
  return new ColonyMemory(config);
}
