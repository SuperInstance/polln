/**
 * POLLN Microbiome - Symbiosis System
 *
 * Manages symbiotic relationships between microbiome agents.
 * Implements mutualism, commensalism, parasitism, and predation.
 *
 * @module microbiome/symbiosis
 */

import { v4 as uuidv4 } from 'uuid';
import {
  MicrobiomeAgent,
  Symbiosis,
  SymbiosisType,
  ResourceType,
  MetabolicProfile,
} from './types.js';

/**
 * Interaction outcome for relationship evolution
 */
export type InteractionOutcome = 'positive' | 'negative' | 'neutral';

/**
 * Relationship history for tracking evolution
 */
export interface RelationshipHistory {
  /** Timestamp of interaction */
  timestamp: number;
  /** Outcome of interaction */
  outcome: InteractionOutcome;
  /** Strength before interaction */
  previousStrength: number;
  /** Reward/punishment magnitude */
  magnitude: number;
}

/**
 * Extended symbiosis with evolution tracking
 */
export interface EvolvableSymbiosis extends Symbiosis {
  /** Unique relationship ID */
  id: string;
  /** Formation timestamp */
  formationTime: number;
  /** Last interaction timestamp */
  lastInteraction: number;
  /** Total interaction count */
  interactionCount: number;
  /** Positive interaction count */
  positiveCount: number;
  /** Negative interaction count */
  negativeCount: number;
  /** Relationship history */
  history: RelationshipHistory[];
  /** Current stability score (0-1) */
  stability: number;
}

/**
 * Benefit calculation result
 */
export interface BenefitCalculation {
  /** Benefit to source agent (0-1) */
  toSource: number;
  /** Benefit to target agent (0-1) */
  toTarget: number;
  /** Net benefit to ecosystem (-1 to 1) */
  net: number;
  /** Efficiency score (0-1) */
  efficiency: number;
}

/**
 * Symbiosis formation options
 */
export interface SymbiosisOptions {
  /** Initial strength (0-1, default: 0.5) */
  initialStrength?: number;
  /** Enable auto-evolution (default: true) */
  autoEvolve?: boolean;
  /** Evolution rate (0-1, default: 0.1) */
  evolutionRate?: number;
  /** Minimum strength threshold (default: 0.1) */
  minStrengthThreshold?: number;
  /** Maximum history size (default: 100) */
  maxHistorySize?: number;
}

/**
 * Symbiosis statistics
 */
export interface SymbiosisStats {
  /** Total active relationships */
  totalRelationships: number;
  /** Relationships by type */
  byType: Map<SymbiosisType, number>;
  /** Average strength */
  averageStrength: number;
  /** Average stability */
  averageStability: number;
  /** Most successful relationship type */
  mostSuccessfulType: SymbiosisType | null;
  /** Evolution events count */
  evolutionEvents: number;
}

/**
 * Symbiosis manager - handles all symbiotic relationships
 *
 * Key behaviors:
 * - MUTUALISM: Both partners gain (e.g., compression + video processing)
 * - COMMENSALISM: One gains, other unaffected (e.g., log scavenger)
 * - PARASITISM: One gains, other harmed (e.g., virus)
 * - PREDATION: Predator consumes prey (e.g., resource auditor)
 *
 * Evolution: Relationships strengthen/weaken based on interaction outcomes
 */
export class SymbiosisManager {
  /** All active relationships */
  private relationships: Map<string, EvolvableSymbiosis>;
  /** Relationships by source ID */
  bySource: Map<string, Set<string>>;
  /** Relationships by target ID */
  byTarget: Map<string, Set<string>>;
  /** Default options */
  private defaultOptions: Required<SymbiosisOptions>;
  /** Evolution events counter */
  private evolutionEvents: number;

  constructor(options: Partial<SymbiosisOptions> = {}) {
    this.relationships = new Map();
    this.bySource = new Map();
    this.byTarget = new Map();
    this.evolutionEvents = 0;

    this.defaultOptions = {
      initialStrength: options.initialStrength ?? 0.5,
      autoEvolve: options.autoEvolve ?? true,
      evolutionRate: options.evolutionRate ?? 0.1,
      minStrengthThreshold: options.minStrengthThreshold ?? 0.1,
      maxHistorySize: options.maxHistorySize ?? 100,
    };
  }

  /**
   * Form a new symbiotic relationship
   *
   * @param source - Source agent
   * @param target - Target agent
   * @param type - Type of symbiosis
   * @param strength - Relationship strength (0-1)
   * @param options - Formation options
   * @returns The formed relationship
   * @throws Error if relationship already exists
   */
  formSymbiosis(
    source: MicrobiomeAgent,
    target: MicrobiomeAgent,
    type: SymbiosisType,
    strength: number = this.defaultOptions.initialStrength,
    options: Partial<SymbiosisOptions> = {}
  ): EvolvableSymbiosis {
    // Validate inputs
    if (!source.id || !target.id) {
      throw new Error('Agents must have valid IDs');
    }

    if (source.id === target.id) {
      throw new Error('Cannot form symbiosis with self');
    }

    if (strength < 0 || strength > 1) {
      throw new Error('Strength must be between 0 and 1');
    }

    // Check if relationship already exists
    const relationshipId = this.getRelationshipId(source.id, target.id);
    if (this.relationships.has(relationshipId)) {
      throw new Error(`Symbiosis already exists between ${source.id} and ${target.id}`);
    }

    // Calculate benefits based on type and metabolic profiles
    const benefits = this.calculateInitialBenefits(source, target, type, strength);

    // Create relationship
    const now = Date.now();
    const symbiosis: EvolvableSymbiosis = {
      id: uuidv4(),
      sourceId: source.id,
      targetId: target.id,
      type,
      strength,
      benefitToSource: benefits.toSource,
      benefitToTarget: benefits.toTarget,
      formationTime: now,
      lastInteraction: now,
      interactionCount: 0,
      positiveCount: 0,
      negativeCount: 0,
      history: [],
      stability: 0.5,
    };

    // Store relationship
    this.relationships.set(relationshipId, symbiosis);

    // Update indices
    if (!this.bySource.has(source.id)) {
      this.bySource.set(source.id, new Set());
    }
    this.bySource.get(source.id)!.add(relationshipId);

    if (!this.byTarget.has(target.id)) {
      this.byTarget.set(target.id, new Set());
    }
    this.byTarget.get(target.id)!.add(relationshipId);

    return symbiosis;
  }

  /**
   * Break a symbiotic relationship
   *
   * @param sourceId - Source agent ID
   * @param targetId - Target agent ID
   * @returns True if relationship was broken, false if not found
   */
  breakSymbiosis(sourceId: string, targetId: string): boolean {
    const relationshipId = this.getRelationshipId(sourceId, targetId);
    const relationship = this.relationships.get(relationshipId);

    if (!relationship) {
      return false;
    }

    // Remove from indices
    this.bySource.get(sourceId)?.delete(relationshipId);
    this.byTarget.get(targetId)?.delete(relationshipId);

    // Remove relationship
    this.relationships.delete(relationshipId);

    return true;
  }

  /**
   * Calculate benefits for a symbiotic relationship
   *
   * @param symbiosis - The symbiosis to calculate benefits for
   * @returns Benefit calculation result
   */
  calculateBenefit(symbiosis: Symbiosis): BenefitCalculation {
    const { type, strength, benefitToSource, benefitToTarget } = symbiosis;

    let net: number;
    let efficiency: number;

    switch (type) {
      case SymbiosisType.MUTUALISM:
        // Both gain - positive net
        net = (benefitToSource + benefitToTarget) * strength;
        efficiency = (benefitToSource + benefitToTarget) / 2;
        break;

      case SymbiosisType.COMMENSALISM:
        // One gains, other unaffected - slightly positive net
        net = benefitToSource * strength * 0.8;
        efficiency = benefitToSource;
        break;

      case SymbiosisType.PARASITISM:
        // One gains, other harmed - negative net for ecosystem
        net = (benefitToSource - benefitToTarget) * strength;
        efficiency = benefitToSource; // Parasite efficiency
        break;

      case SymbiosisType.PREDATION:
        // Predator gains, prey consumed - neutral to slightly negative
        net = (benefitToSource - benefitToTarget) * strength;
        efficiency = benefitToSource; // Predator efficiency
        break;

      default:
        net = 0;
        efficiency = 0.5;
    }

    return {
      toSource: benefitToSource * strength,
      toTarget: benefitToTarget * strength,
      net: Math.max(-1, Math.min(1, net)),
      efficiency,
    };
  }

  /**
   * Evolve a relationship based on interaction outcome
   *
   * @param sourceId - Source agent ID
   * @param targetId - Target agent ID
   * @param outcome - Interaction outcome
   * @param magnitude - Magnitude of reward/punishment (0-1)
   * @returns Updated relationship or null if not found
   */
  evolveRelationship(
    sourceId: string,
    targetId: string,
    outcome: InteractionOutcome,
    magnitude: number = 0.5
  ): EvolvableSymbiosis | null {
    const relationshipId = this.getRelationshipId(sourceId, targetId);
    const relationship = this.relationships.get(relationshipId);

    if (!relationship) {
      return null;
    }

    const now = Date.now();
    const previousStrength = relationship.strength;

    // Update counts
    relationship.interactionCount++;
    if (outcome === 'positive') {
      relationship.positiveCount++;
    } else if (outcome === 'negative') {
      relationship.negativeCount++;
    }

    // Record history
    relationship.history.push({
      timestamp: now,
      outcome,
      previousStrength,
      magnitude,
    });

    // Trim history if too long
    if (relationship.history.length > this.defaultOptions.maxHistorySize) {
      relationship.history.shift();
    }

    // Evolve strength based on outcome
    if (outcome === 'positive') {
      // Strengthen relationship
      const increase = magnitude * this.defaultOptions.evolutionRate;
      relationship.strength = Math.min(1, relationship.strength + increase);
    } else if (outcome === 'negative') {
      // Weaken relationship
      const decrease = magnitude * this.defaultOptions.evolutionRate;
      relationship.strength = Math.max(0, relationship.strength - decrease);
    }
    // Neutral: no change to strength

    // Update stability based on consistency
    this.updateStability(relationship);

    // Update last interaction time
    relationship.lastInteraction = now;

    // Update benefits based on new strength
    const benefits = this.calculateBenefit(relationship);
    relationship.benefitToSource = benefits.toSource;
    relationship.benefitToTarget = benefits.toTarget;

    // Check if relationship should break
    if (relationship.strength < this.defaultOptions.minStrengthThreshold) {
      this.breakSymbiosis(sourceId, targetId);
      this.evolutionEvents++;
      return null;
    }

    this.evolutionEvents++;
    return relationship;
  }

  /**
   * Get all relationships for an agent
   *
   * @param agentId - Agent ID
   * @returns Array of relationships
   */
  getRelationships(agentId: string): EvolvableSymbiosis[] {
    const results: EvolvableSymbiosis[] = [];

    // Check as source
    const asSource = this.bySource.get(agentId);
    if (asSource) {
      for (const relId of asSource) {
        const rel = this.relationships.get(relId);
        if (rel) results.push(rel);
      }
    }

    // Check as target
    const asTarget = this.byTarget.get(agentId);
    if (asTarget) {
      for (const relId of asTarget) {
        const rel = this.relationships.get(relId);
        if (rel && !results.includes(rel)) {
          results.push(rel);
        }
      }
    }

    return results;
  }

  /**
   * Get a specific relationship
   *
   * @param sourceId - Source agent ID
   * @param targetId - Target agent ID
   * @returns Relationship or null if not found
   */
  getRelationship(sourceId: string, targetId: string): EvolvableSymbiosis | null {
    return this.relationships.get(this.getRelationshipId(sourceId, targetId)) || null;
  }

  /**
   * Get all relationships
   *
   * @returns Array of all relationships
   */
  getAllRelationships(): EvolvableSymbiosis[] {
    return Array.from(this.relationships.values());
  }

  /**
   * Get relationships by type
   *
   * @param type - Symbiosis type
   * @returns Array of relationships
   */
  getRelationshipsByType(type: SymbiosisType): EvolvableSymbiosis[] {
    return Array.from(this.relationships.values()).filter(r => r.type === type);
  }

  /**
   * Get symbiosis statistics
   *
   * @returns Statistics about all relationships
   */
  getStats(): SymbiosisStats {
    const relationships = Array.from(this.relationships.values());
    const byType = new Map<SymbiosisType, number>();

    for (const type of Object.values(SymbiosisType)) {
      byType.set(type, 0);
    }

    let totalStrength = 0;
    let totalStability = 0;
    let mostSuccessfulType: SymbiosisType | null = null;
    let maxSuccessRate = 0;

    for (const rel of relationships) {
      byType.set(rel.type, (byType.get(rel.type) || 0) + 1);
      totalStrength += rel.strength;
      totalStability += rel.stability;

      // Calculate success rate
      const successRate = rel.positiveCount / Math.max(1, rel.interactionCount);
      if (successRate > maxSuccessRate) {
        maxSuccessRate = successRate;
        mostSuccessfulType = rel.type;
      }
    }

    return {
      totalRelationships: relationships.length,
      byType,
      averageStrength: relationships.length > 0 ? totalStrength / relationships.length : 0,
      averageStability: relationships.length > 0 ? totalStability / relationships.length : 0,
      mostSuccessfulType,
      evolutionEvents: this.evolutionEvents,
    };
  }

  /**
   * Clear all relationships
   */
  clear(): void {
    this.relationships.clear();
    this.bySource.clear();
    this.byTarget.clear();
    this.evolutionEvents = 0;
  }

  /**
   * Get relationship ID from two agent IDs
   */
  private getRelationshipId(sourceId: string, targetId: string): string {
    return `${sourceId}->${targetId}`;
  }

  /**
   * Calculate initial benefits for a new relationship
   */
  private calculateInitialBenefits(
    source: MicrobiomeAgent,
    target: MicrobiomeAgent,
    type: SymbiosisType,
    strength: number
  ): { toSource: number; toTarget: number } {
    const sourceMeta = source.metabolism;
    const targetMeta = target.metabolism;

    // Calculate metabolic complementarity
    const complementarity = this.calculateComplementarity(sourceMeta, targetMeta);

    switch (type) {
      case SymbiosisType.MUTUALISM:
        // Both benefit based on complementarity
        return {
          toSource: 0.5 + complementarity * 0.5,
          toTarget: 0.5 + complementarity * 0.5,
        };

      case SymbiosisType.COMMENSALISM:
        // Only source benefits
        return {
          toSource: 0.6 + complementarity * 0.4,
          toTarget: 0, // No benefit or harm
        };

      case SymbiosisType.PARASITISM:
        // Source benefits at target's expense
        return {
          toSource: 0.8,
          toTarget: -0.5, // Target is harmed
        };

      case SymbiosisType.PREDATION:
        // Predator (source) gains, prey (target) loses heavily
        return {
          toSource: 0.9,
          toTarget: -1.0, // Prey is consumed
        };

      default:
        return { toSource: 0.5, toTarget: 0.5 };
    }
  }

  /**
   * Calculate metabolic complementarity between two agents
   */
  private calculateComplementarity(sourceMeta: MetabolicProfile, targetMeta: MetabolicProfile): number {
    // Check if source's outputs match target's inputs
    let outputMatchesInput = 0;
    for (const output of sourceMeta.outputs) {
      if (targetMeta.inputs.includes(output)) {
        outputMatchesInput++;
      }
    }

    // Check if target's outputs match source's inputs
    let inputMatchesOutput = 0;
    for (const output of targetMeta.outputs) {
      if (sourceMeta.inputs.includes(output)) {
        inputMatchesOutput++;
      }
    }

    // Calculate complementarity score
    const maxMatches = Math.max(sourceMeta.outputs.length, targetMeta.outputs.length);
    return maxMatches > 0 ? (outputMatchesInput + inputMatchesOutput) / (2 * maxMatches) : 0;
  }

  /**
   * Update stability based on interaction history consistency
   */
  private updateStability(relationship: EvolvableSymbiosis): void {
    if (relationship.interactionCount < 3) {
      relationship.stability = 0.5;
      return;
    }

    // Calculate recent outcomes (last 10 interactions)
    const recentHistory = relationship.history.slice(-10);
    const positiveRatio = recentHistory.filter(h => h.outcome === 'positive').length / recentHistory.length;

    // Stability increases with consistency
    const variance = Math.abs(positiveRatio - 0.5) * 2; // 0 = mixed outcomes, 1 = consistent
    relationship.stability = 0.3 + variance * 0.7; // Range: 0.3 to 1.0
  }
}
