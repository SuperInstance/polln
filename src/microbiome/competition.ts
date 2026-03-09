/**
 * POLLN Microbiome - Competition Engine
 *
 * Manages competitive interactions between agents based on resource scarcity.
 * Implements Gause's competitive exclusion principle, niche differentiation,
 * and character displacement.
 *
 * @module microbiome/competition
 */

import {
  MicrobiomeAgent,
  ResourceType,
  MetabolicProfile,
  FitnessScore,
  SymbiosisType,
} from './types.js';
import { MetabolismManager, ResourcePool } from './metabolism.js';
import { FitnessEvaluator } from './fitness.js';
import { SymbiosisManager } from './symbiosis.js';

/**
 * Scarcity level for a resource
 */
export enum ScarcityLevel {
  /** Abundant resource (> 60% capacity) */
  ABUNDANT = 'abundant',
  /** Moderate availability (30-60% capacity) */
  MODERATE = 'moderate',
  /** Scarce resource (10-30% capacity) */
  SCARCE = 'scarce',
  /** Critical shortage (< 10% capacity) */
  CRITICAL = 'critical',
}

/**
 * Scarcity report for a resource
 */
export interface ScarcityReport {
  /** Resource type */
  resource: ResourceType;
  /** Scarcity level */
  level: ScarcityLevel;
  /** Current availability */
  available: number;
  /** Total capacity */
  capacity: number;
  /** Scarcity ratio (0-1, 1 = completely depleted) */
  scarcityRatio: number;
  /** Number of agents competing */
  competitorCount: number;
  /** Competition intensity (0-1) */
  competitionIntensity: number;
}

/**
 * Competitive interaction result
 */
export interface CompetitiveInteraction {
  /** Winning agent ID */
  winner: string;
  /** Losing agent ID */
  loser: string;
  /** Resource competed for */
  resource: ResourceType;
  /** Competition intensity (0-1) */
  intensity: number;
  /** Fitness difference */
  fitnessDifference: number;
  /** Outcome type */
  outcome: 'exclusion' | 'coexistence' | 'differentiation';
}

/**
 * Niche specialization
 */
export interface NicheSpecialization {
  /** Agent ID */
  agentId: string;
  /** Specialized resources */
  specializedResources: ResourceType[];
  /** Avoided resources (reduced competition) */
  avoidedResources: ResourceType[];
  /** Temporal niche (active time period) */
  temporalNiche: { start: number; end: number };
  /** Behavioral specialization */
  behavioralTraits: string[];
  /** Specialization strength (0-1) */
  strength: number;
}

/**
 * Character displacement
 */
export interface CharacterDisplacement {
  /** Agent pair experiencing displacement */
  agents: [string, string];
  /** Resource being partitioned */
  resource: ResourceType;
  /** Initial niche overlap (0-1) */
  initialOverlap: number;
  /** Current niche overlap (0-1) */
  currentOverlap: number;
  /** Displacement magnitude (0-1) */
  displacementMagnitude: number;
  /** Trait differences that emerged */
  traitDifferences: string[];
}

/**
 * Competition statistics
 */
export interface CompetitionStats {
  /** Total competitive interactions */
  totalInteractions: number;
  /** Competitive exclusion events */
  exclusions: number;
  /** Niche differentiation events */
  differentiations: number;
  /** Character displacements */
  displacements: number;
  /** Coexistence events */
  coexistences: number;
  /** Current competition level (0-1) */
  currentCompetitionLevel: number;
}

/**
 * Competition engine configuration
 */
export interface CompetitionEngineConfig {
  /** Scarcity threshold to trigger competition (0-1) */
  scarcityThreshold?: number;
  /** Minimum fitness difference for exclusion (0-1) */
  exclusionThreshold?: number;
  /** Niche differentiation rate (0-1) */
  differentiationRate?: number;
  /** Character displacement rate (0-1) */
  displacementRate?: number;
  /** Enable competitive exclusion */
  enableExclusion?: boolean;
  /** Enable niche differentiation */
  enableDifferentiation?: boolean;
  /** Enable character displacement */
  enableDisplacement?: boolean;
}

/**
 * Competition Engine
 *
 * Manages competitive interactions based on resource scarcity using
 * Gause's competitive exclusion principle and niche differentiation.
 */
export class CompetitionEngine {
  /** Metabolism manager for resource tracking */
  private metabolism: MetabolismManager;
  /** Fitness evaluator for competitive fitness */
  private fitness: FitnessEvaluator;
  /** Symbiosis manager for mutualistic vs competitive */
  private symbiosis: SymbiosisManager;
  /** Configuration */
  private config: Required<CompetitionEngineConfig>;
  /** Statistics */
  private stats: CompetitionStats;
  /** Active niche specializations */
  private niches: Map<string, NicheSpecialization>;
  /** Active character displacements */
  private displacements: Map<string, CharacterDisplacement>;
  /** Competitive history */
  private history: CompetitiveInteraction[];

  constructor(
    metabolism: MetabolismManager,
    fitness: FitnessEvaluator,
    symbiosis: SymbiosisManager,
    config: CompetitionEngineConfig = {}
  ) {
    this.metabolism = metabolism;
    this.fitness = fitness;
    this.symbiosis = symbiosis;

    this.config = {
      scarcityThreshold: config.scarcityThreshold ?? 0.4,
      exclusionThreshold: config.exclusionThreshold ?? 0.3,
      differentiationRate: config.differentiationRate ?? 0.2,
      displacementRate: config.displacementRate ?? 0.15,
      enableExclusion: config.enableExclusion ?? true,
      enableDifferentiation: config.enableDifferentiation ?? true,
      enableDisplacement: config.enableDisplacement ?? true,
    };

    this.stats = {
      totalInteractions: 0,
      exclusions: 0,
      differentiations: 0,
      displacements: 0,
      coexistences: 0,
      currentCompetitionLevel: 0,
    };

    this.niches = new Map();
    this.displacements = new Map();
    this.history = [];
  }

  /**
   * Calculate scarcity for all resources
   */
  calculateScarcity(agents: MicrobiomeAgent[]): Map<ResourceType, ScarcityReport> {
    const pool = this.metabolism.getResourcePool();
    const flows = pool.getAllFlows();
    const reports = new Map<ResourceType, ScarcityReport>();

    for (const resource of Object.values(ResourceType)) {
      const flow = flows.get(resource);
      const available = pool.getAvailable(resource);
      const capacity = flow?.capacity || Number.MAX_SAFE_INTEGER;

      // Calculate scarcity ratio (0 = abundant, 1 = depleted)
      const scarcityRatio = capacity > 0
        ? Math.max(0, 1 - (available / capacity))
        : 0;

      // Determine scarcity level
      let level: ScarcityLevel;
      if (scarcityRatio < 0.4) {
        level = ScarcityLevel.ABUNDANT;
      } else if (scarcityRatio < 0.7) {
        level = ScarcityLevel.MODERATE;
      } else if (scarcityRatio < 0.9) {
        level = ScarcityLevel.SCARCE;
      } else {
        level = ScarcityLevel.CRITICAL;
      }

      // Count competitors (agents that consume this resource)
      const competitorCount = agents.filter(agent =>
        agent.lifecycle.isAlive &&
        agent.metabolism.inputs.includes(resource)
      ).length;

      // Calculate competition intensity
      const competitionIntensity = this.calculateCompetitionIntensity(
        scarcityRatio,
        competitorCount
      );

      reports.set(resource, {
        resource,
        level,
        available,
        capacity,
        scarcityRatio,
        competitorCount,
        competitionIntensity,
      });
    }

    return reports;
  }

  /**
   * Resolve competitive conflicts
   */
  resolveCompetition(agents: MicrobiomeAgent[]): CompetitiveInteraction[] {
    const interactions: CompetitiveInteraction[] = [];
    const scarcityReports = this.calculateScarcity(agents);

    // Find scarce resources that trigger competition
    const scarceResources = Array.from(scarcityReports.entries())
      .filter(([_, report]) =>
        report.scarcityRatio >= this.config.scarcityThreshold &&
        report.competitionIntensity > 0.5
      )
      .sort((a, b) => b[1].competitionIntensity - a[1].competitionIntensity);

    for (const [resource, report] of scarceResources) {
      // Get competitors for this resource
      const competitors = agents.filter(agent =>
        agent.lifecycle.isAlive &&
        agent.metabolism.inputs.includes(resource)
      );

      if (competitors.length < 2) continue;

      // Evaluate fitness for all competitors
      const fitnessScores = new Map<string, FitnessScore>();
      for (const competitor of competitors) {
        const score = competitor.evaluateFitness();
        fitnessScores.set(competitor.id, score);
      }

      // Resolve competition between pairs
      for (let i = 0; i < competitors.length; i++) {
        for (let j = i + 1; j < competitors.length; j++) {
          const agent1 = competitors[i];
          const agent2 = competitors[j];
          const fitness1 = fitnessScores.get(agent1.id)!;
          const fitness2 = fitnessScores.get(agent2.id)!;

          const interaction = this.resolvePairwiseCompetition(
            agent1,
            agent2,
            fitness1,
            fitness2,
            resource,
            report.competitionIntensity
          );

          if (interaction) {
            interactions.push(interaction);
            this.history.push(interaction);
            this.stats.totalInteractions++;

            // Update statistics
            switch (interaction.outcome) {
              case 'exclusion':
                this.stats.exclusions++;
                break;
              case 'coexistence':
                this.stats.coexistences++;
                break;
              case 'differentiation':
                this.stats.differentiations++;
                break;
            }

            // Apply outcome
            this.applyCompetitionOutcome(interaction, agents);
          }
        }
      }
    }

    // Update overall competition level
    this.stats.currentCompetitionLevel = this.calculateOverallCompetitionLevel(scarcityReports);

    return interactions;
  }

  /**
   * Differentiate niches to reduce competition
   */
  differentiateNiche(agent: MicrobiomeAgent, competitor: MicrobiomeAgent): NicheSpecialization | null {
    if (!this.config.enableDifferentiation) {
      return null;
    }

    // Calculate niche overlap
    const overlap = this.calculateNicheOverlap(agent, competitor);

    if (overlap < 0.3) {
      // Already differentiated enough
      return null;
    }

    // Create new specialization
    const specialization = this.createNicheSpecialization(agent, competitor);

    if (Math.random() < this.config.differentiationRate) {
      this.niches.set(agent.id, specialization);
      return specialization;
    }

    return null;
  }

  /**
   * Apply character displacement
   */
  applyCharacterDisplacement(
    agent1: MicrobiomeAgent,
    agent2: MicrobiomeAgent,
    resource: ResourceType
  ): CharacterDisplacement | null {
    if (!this.config.enableDisplacement) {
      return null;
    }

    const pairId = this.getPairId(agent1.id, agent2.id);
    const existing = this.displacements.get(pairId);

    const initialOverlap = existing?.initialOverlap ?? this.calculateNicheOverlap(agent1, agent2);

    // Calculate trait differences
    const traitDifferences = this.identifyTraitDifferences(agent1, agent2);

    // Calculate displacement magnitude
    const displacementMagnitude = Math.random() * this.config.displacementRate;

    // Update current overlap (reduces with displacement)
    const currentOverlap = Math.max(0, initialOverlap - displacementMagnitude);

    const displacement: CharacterDisplacement = {
      agents: [agent1.id, agent2.id],
      resource,
      initialOverlap,
      currentOverlap,
      displacementMagnitude,
      traitDifferences,
    };

    this.displacements.set(pairId, displacement);
    this.stats.displacements++;

    return displacement;
  }

  /**
   * Get competition statistics
   */
  getStats(): CompetitionStats {
    return { ...this.stats };
  }

  /**
   * Get active niche specializations
   */
  getNicheSpecializations(): NicheSpecialization[] {
    return Array.from(this.niches.values());
  }

  /**
   * Get active character displacements
   */
  getCharacterDisplacements(): CharacterDisplacement[] {
    return Array.from(this.displacements.values());
  }

  /**
   * Get competitive history
   */
  getHistory(): CompetitiveInteraction[] {
    return [...this.history];
  }

  /**
   * Reset statistics
   */
  resetStats(): void {
    this.stats = {
      totalInteractions: 0,
      exclusions: 0,
      differentiations: 0,
      displacements: 0,
      coexistences: 0,
      currentCompetitionLevel: 0,
    };
    this.history = [];
  }

  /**
   * Clear all niche specializations and displacements
   */
  clear(): void {
    this.niches.clear();
    this.displacements.clear();
    this.history = [];
  }

  /**
   * Calculate competition intensity
   */
  private calculateCompetitionIntensity(scarcityRatio: number, competitorCount: number): number {
    // Intensity increases with both scarcity and competition
    const scarcityFactor = Math.pow(scarcityRatio, 2); // Non-linear
    const competitionFactor = Math.min(1, competitorCount / 10); // Diminishing returns

    return Math.min(1, scarcityFactor * (1 + competitionFactor) / 2);
  }

  /**
   * Resolve pairwise competition between two agents
   */
  private resolvePairwiseCompetition(
    agent1: MicrobiomeAgent,
    agent2: MicrobiomeAgent,
    fitness1: FitnessScore,
    fitness2: FitnessScore,
    resource: ResourceType,
    intensity: number
  ): CompetitiveInteraction | null {
    const fitnessDiff = Math.abs(fitness1.overall - fitness2.overall);
    const winner = fitness1.overall > fitness2.overall ? agent1 : agent2;
    const loser = fitness1.overall > fitness2.overall ? agent2 : agent1;

    // Check for existing mutualism (mutualists should coexist)
    const relationship = this.symbiosis.getRelationship(agent1.id, agent2.id);
    if (relationship && relationship.type === SymbiosisType.MUTUALISM && relationship.strength > 0.5) {
      return {
        winner: winner.id,
        loser: loser.id,
        resource,
        intensity,
        fitnessDifference: fitnessDiff,
        outcome: 'coexistence',
      };
    }

    // Gause's principle: competitive exclusion if fitness difference is large
    if (this.config.enableExclusion && fitnessDiff > this.config.exclusionThreshold) {
      return {
        winner: winner.id,
        loser: loser.id,
        resource,
        intensity,
        fitnessDifference: fitnessDiff,
        outcome: 'exclusion',
      };
    }

    // Moderate competition: niche differentiation
    if (this.config.enableDifferentiation && fitnessDiff > 0.1) {
      return {
        winner: winner.id,
        loser: loser.id,
        resource,
        intensity,
        fitnessDifference: fitnessDiff,
        outcome: 'differentiation',
      };
    }

    // Low competition: coexistence
    return {
      winner: winner.id,
      loser: loser.id,
      resource,
      intensity,
      fitnessDifference: fitnessDiff,
      outcome: 'coexistence',
    };
  }

  /**
   * Apply competition outcome
   */
  private applyCompetitionOutcome(interaction: CompetitiveInteraction, agents: MicrobiomeAgent[]): void {
    const loser = agents.find(a => a.id === interaction.loser);
    if (!loser) return;

    switch (interaction.outcome) {
      case 'exclusion':
        // Competitive exclusion: reduce loser's health or kill
        const damage = interaction.intensity * 0.3;
        loser.lifecycle.health = Math.max(0, loser.lifecycle.health - damage);
        if (loser.lifecycle.health <= 0.1) {
          loser.lifecycle.isAlive = false;
        }
        break;

      case 'differentiation':
        // Niche differentiation: modify metabolism
        if (this.config.enableDifferentiation) {
          this.modifyMetabolismForNiche(loser, interaction.resource);
        }
        break;

      case 'coexistence':
        // Coexistence: slight health reduction for both
        const coexistenceCost = interaction.intensity * 0.05;
        loser.lifecycle.health = Math.max(0, loser.lifecycle.health - coexistenceCost);
        break;
    }
  }

  /**
   * Modify agent metabolism for niche differentiation
   */
  private modifyMetabolismForNiche(agent: MicrobiomeAgent, competedResource: ResourceType): void {
    // Reduce reliance on competed resource
    const index = agent.metabolism.inputs.indexOf(competedResource);
    if (index > -1 && agent.metabolism.inputs.length > 1) {
      // Shift to alternative resources
      agent.metabolism.inputs.splice(index, 1);

      // Reduce processing rate (specialization cost)
      agent.metabolism.processingRate *= 0.9;

      // Increase efficiency in remaining niches
      agent.metabolism.efficiency = Math.min(1, agent.metabolism.efficiency * 1.1);
    }
  }

  /**
   * Create niche specialization
   */
  private createNicheSpecialization(
    agent: MicrobiomeAgent,
    competitor: MicrobiomeAgent
  ): NicheSpecialization {
    // Find resources competitor doesn't use
    const avoidedResources = competitor.metabolism.inputs.filter(
      r => !agent.metabolism.inputs.includes(r)
    );

    // Specialize in non-competing resources
    const specializedResources = agent.metabolism.inputs.filter(
      r => !competitor.metabolism.inputs.includes(r)
    );

    // Create temporal niche (random time period)
    const hour = 3600000; // 1 hour in ms
    const temporalNiche = {
      start: Math.floor(Math.random() * 24) * hour,
      end: Math.floor(Math.random() * 24) * hour,
    };

    // Behavioral traits
    const behavioralTraits = [
      'nocturnal',
      'specialized',
      'efficient',
      'opportunistic',
    ].filter(() => Math.random() > 0.5);

    return {
      agentId: agent.id,
      specializedResources,
      avoidedResources,
      temporalNiche,
      behavioralTraits,
      strength: Math.random(),
    };
  }

  /**
   * Calculate niche overlap between two agents
   */
  private calculateNicheOverlap(agent1: MicrobiomeAgent, agent2: MicrobiomeAgent): number {
    // Resource overlap
    const resourceOverlap = this.calculateResourceOverlap(
      agent1.metabolism.inputs,
      agent2.metabolism.inputs
    );

    // Efficiency similarity
    const efficiencySimilarity = 1 - Math.abs(
      agent1.metabolism.efficiency - agent2.metabolism.efficiency
    );

    // Processing rate similarity
    const rateSimilarity = 1 - Math.min(1,
      Math.abs(agent1.metabolism.processingRate - agent2.metabolism.processingRate) / 100
    );

    // Combined overlap
    return (resourceOverlap * 0.6 + efficiencySimilarity * 0.2 + rateSimilarity * 0.2);
  }

  /**
   * Calculate resource overlap
   */
  private calculateResourceOverlap(resources1: ResourceType[], resources2: ResourceType[]): number {
    if (resources1.length === 0 || resources2.length === 0) {
      return 0;
    }

    const intersection = resources1.filter(r => resources2.includes(r));
    const union = new Set([...resources1, ...resources2]);

    return intersection.length / union.size;
  }

  /**
   * Identify trait differences between agents
   */
  private identifyTraitDifferences(agent1: MicrobiomeAgent, agent2: MicrobiomeAgent): string[] {
    const differences: string[] = [];

    // Size difference
    if (Math.abs(agent1.size - agent2.size) > 100) {
      differences.push('size');
    }

    // Complexity difference
    if (Math.abs(agent1.complexity - agent2.complexity) > 0.2) {
      differences.push('complexity');
    }

    // Efficiency difference
    if (Math.abs(agent1.metabolism.efficiency - agent2.metabolism.efficiency) > 0.3) {
      differences.push('efficiency');
    }

    // Processing rate difference
    if (Math.abs(agent1.metabolism.processingRate - agent2.metabolism.processingRate) > 50) {
      differences.push('processing_rate');
    }

    // Input resources difference
    const inputSymDiff = new Set([
      ...agent1.metabolism.inputs.filter(r => !agent2.metabolism.inputs.includes(r)),
      ...agent2.metabolism.inputs.filter(r => !agent1.metabolism.inputs.includes(r)),
    ]);
    if (inputSymDiff.size > 0) {
      differences.push('resource_preference');
    }

    return differences;
  }

  /**
   * Calculate overall competition level
   */
  private calculateOverallCompetitionLevel(
    scarcityReports: Map<ResourceType, ScarcityReport>
  ): number {
    if (scarcityReports.size === 0) return 0;

    const totalIntensity = Array.from(scarcityReports.values())
      .reduce((sum, report) => sum + report.competitionIntensity, 0);

    return Math.min(1, totalIntensity / scarcityReports.size);
  }

  /**
   * Get unique pair ID for two agents
   */
  private getPairId(id1: string, id2: string): string {
    return [id1, id2].sort().join('-');
  }
}

/**
 * Create a competition engine with default configuration
 */
export function createCompetitionEngine(
  metabolism: MetabolismManager,
  fitness: FitnessEvaluator,
  symbiosis: SymbiosisManager,
  config?: CompetitionEngineConfig
): CompetitionEngine {
  return new CompetitionEngine(metabolism, fitness, symbiosis, config);
}
