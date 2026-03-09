/**
 * POLLN Microbiome - Genetic Operations
 *
 * Phase 3: Evolution & Natural Selection
 * Implements sophisticated genetic operations including point mutations,
 * chromosomal rearrangements, crossover, horizontal transfer, and speciation.
 *
 * @module microbiome/genetic
 */

import {
  MicrobiomeAgent,
  FitnessScore,
  MutationConfig,
  MutationType,
  ResourceType,
  MetabolicProfile,
  AgentTaxonomy,
} from './types.js';
import { BaseBacteria } from './bacteria.js';

/**
 * Point mutation type
 */
export enum PointMutationType {
  /** Adjust processing parameters */
  GOAL_ADJUSTMENT = 'goal_adjustment',
  /** Vary processing method */
  METHOD_VARIATION = 'method_variation',
  /** Shift metabolic profile */
  METABOLIC_SHIFT = 'metabolic_shift',
  /** Gain symbiosis dependency */
  SYMBIOSIS_GAIN = 'symbiosis_gain',
  /** Lose symbiosis dependency */
  SYMBIOSIS_LOSS = 'symbiosis_loss',
}

/**
 * Chromosomal operation type
 */
export enum ChromosomalOperationType {
  /** Reverse a segment of genes */
  INVERSION = 'inversion',
  /** Move a segment to new location */
  TRANSPOSITION = 'transposition',
  /** Remove a segment of genes */
  DELETION = 'deletion',
  /** Duplicate a segment of genes */
  DUPLICATION = 'duplication',
}

/**
 * Crossover type
 */
export enum CrossoverType {
  /** Single-point crossover */
  SINGLE_POINT = 'single_point',
  /** Multi-point crossover */
  MULTI_POINT = 'multi_point',
  /** Uniform crossover (gene by gene) */
  UNIFORM = 'uniform',
  /** Colony-aware crossover */
  COLONY_AWARE = 'colony_aware',
}

/**
 * Genetic operation result
 */
export interface GeneticOperationResult {
  /** Operation performed */
  operation: string;
  /** Success status */
  success: boolean;
  /** Mutation/crossover details */
  details: string;
  /** Parent IDs */
  parentIds: string[];
  /** Child agent (if successful) */
  child?: MicrobiomeAgent;
  /** Fitness change */
  fitnessDelta?: number;
}

/**
 * Speciation info
 */
export interface SpeciationInfo {
  /** Species ID */
  speciesId: string;
  /** Species members */
  members: Set<string>;
  /** Species fitness threshold */
  fitnessThreshold: number;
  /** Species age */
  age: number;
  /** Genetic distance threshold */
  geneticDistanceThreshold: number;
}

/**
 * Genetic operator configuration
 */
export interface GeneticOperatorsConfig {
  /** Point mutation rate (0-1) */
  pointMutationRate: number;
  /** Chromosomal operation rate (0-1) */
  chromosomalOperationRate: number;
  /** Crossover rate (0-1) */
  crossoverRate: number;
  /** Horizontal transfer rate (0-1) */
  horizontalTransferRate: number;
  /** Maximum mutation impact (0-1) */
  maxMutationImpact: number;
  /** Speciation genetic distance threshold (0-1) */
  speciationThreshold: number;
  /** Minimum species size for survival */
  minSpeciesSize: number;
  /** Maximum number of species */
  maxSpecies: number;
  /** Enable point mutations */
  enablePointMutations: boolean;
  /** Enable chromosomal operations */
  enableChromosomalOperations: boolean;
  /** Enable crossover */
  enableCrossover: boolean;
  /** Enable horizontal transfer */
  enableHorizontalTransfer: boolean;
  /** Enable speciation */
  enableSpeciation: boolean;
}

/**
 * Gene representation (agent traits)
 */
export interface Gene {
  /** Gene ID */
  id: string;
  /** Gene type */
  type: 'metabolic' | 'processing' | 'symbiosis' | 'structural';
  /** Gene value */
  value: any;
  /** Gene dominance (0-1) */
  dominance: number;
}

/**
 * Chromosome representation (collection of genes)
 */
export interface Chromosome {
  /** Chromosome ID */
  id: string;
  /** Genes in order */
  genes: Gene[];
  /** Chromosome fitness contribution */
  fitnessContribution: number;
}

/**
 * Default genetic operators configuration
 */
const DEFAULT_GENETIC_CONFIG: GeneticOperatorsConfig = {
  pointMutationRate: 0.01,
  chromosomalOperationRate: 0.005,
  crossoverRate: 0.7,
  horizontalTransferRate: 0.02,
  maxMutationImpact: 0.2,
  speciationThreshold: 0.3,
  minSpeciesSize: 5,
  maxSpecies: 20,
  enablePointMutations: true,
  enableChromosomalOperations: true,
  enableCrossover: true,
  enableHorizontalTransfer: true,
  enableSpeciation: true,
};

/**
 * Genetic Operators
 *
 * Implements sophisticated genetic operations for evolutionary computation.
 * Supports point mutations, chromosomal rearrangements, crossover, horizontal
 * transfer, and speciation mechanisms.
 */
export class GeneticOperators {
  /** Configuration */
  private config: GeneticOperatorsConfig;
  /** Species information */
  private species: Map<string, SpeciationInfo>;
  /** Operation history */
  private operationHistory: GeneticOperationResult[];
  /** Genetic distance cache */
  private distanceCache: Map<string, Map<string, number>>;

  constructor(config: Partial<GeneticOperatorsConfig> = {}) {
    this.config = { ...DEFAULT_GENETIC_CONFIG, ...config };
    this.species = new Map();
    this.operationHistory = [];
    this.distanceCache = new Map();
  }

  /**
   * Apply point mutation to an agent
   */
  async applyPointMutation(agent: MicrobiomeAgent): Promise<GeneticOperationResult> {
    if (!this.config.enablePointMutations || Math.random() > this.config.pointMutationRate) {
      return {
        operation: 'point_mutation',
        success: false,
        details: 'Point mutation disabled or did not trigger',
        parentIds: [agent.id],
      };
    }

    const mutationType = this.selectPointMutationType();
    const oldFitness = agent.evaluateFitness();
    let mutatedAgent = agent;
    let details = '';

    try {
      switch (mutationType) {
        case PointMutationType.GOAL_ADJUSTMENT:
          mutatedAgent = this.applyGoalAdjustment(agent);
          details = `Goal adjustment: processing rate and efficiency modified`;
          break;

        case PointMutationType.METHOD_VARIATION:
          mutatedAgent = this.applyMethodVariation(agent);
          details = `Method variation: processing algorithm changed`;
          break;

        case PointMutationType.METABOLIC_SHIFT:
          mutatedAgent = this.applyMetabolicShift(agent);
          details = `Metabolic shift: input/output resources changed`;
          break;

        case PointMutationType.SYMBIOSIS_GAIN:
          mutatedAgent = this.applySymbiosisGain(agent);
          details = `Symbiosis gain: new dependency added`;
          break;

        case PointMutationType.SYMBIOSIS_LOSS:
          mutatedAgent = this.applySymbiosisLoss(agent);
          details = `Symbiosis loss: dependency removed`;
          break;
      }

      const newFitness = mutatedAgent.evaluateFitness();
      const fitnessDelta = newFitness.overall - oldFitness.overall;

      this.recordOperation({
        operation: 'point_mutation',
        success: true,
        details,
        parentIds: [agent.id],
        child: mutatedAgent,
        fitnessDelta,
      });

      return {
        operation: 'point_mutation',
        success: true,
        details,
        parentIds: [agent.id],
        child: mutatedAgent,
        fitnessDelta,
      };
    } catch (error) {
      return {
        operation: 'point_mutation',
        success: false,
        details: `Point mutation failed: ${error}`,
        parentIds: [agent.id],
      };
    }
  }

  /**
   * Apply chromosomal operation to an agent
   */
  async applyChromosomalOperation(agent: MicrobiomeAgent): Promise<GeneticOperationResult> {
    if (!this.config.enableChromosomalOperations || Math.random() > this.config.chromosomalOperationRate) {
      return {
        operation: 'chromosomal_operation',
        success: false,
        details: 'Chromosomal operation disabled or did not trigger',
        parentIds: [agent.id],
      };
    }

    const operationType = this.selectChromosomalOperation();
    const oldFitness = agent.evaluateFitness();
    let modifiedAgent = agent;
    let details = '';

    try {
      switch (operationType) {
        case ChromosomalOperationType.INVERSION:
          modifiedAgent = this.applyInversion(agent);
          details = `Inversion: gene segment reversed`;
          break;

        case ChromosomalOperationType.TRANSPOSITION:
          modifiedAgent = this.applyTransposition(agent);
          details = `Transposition: gene segment moved`;
          break;

        case ChromosomalOperationType.DELETION:
          modifiedAgent = this.applyDeletion(agent);
          details = `Deletion: gene segment removed`;
          break;

        case ChromosomalOperationType.DUPLICATION:
          modifiedAgent = this.applyDuplication(agent);
          details = `Duplication: gene segment copied`;
          break;
      }

      const newFitness = modifiedAgent.evaluateFitness();
      const fitnessDelta = newFitness.overall - oldFitness.overall;

      this.recordOperation({
        operation: 'chromosomal_operation',
        success: true,
        details,
        parentIds: [agent.id],
        child: modifiedAgent,
        fitnessDelta,
      });

      return {
        operation: 'chromosomal_operation',
        success: true,
        details,
        parentIds: [agent.id],
        child: modifiedAgent,
        fitnessDelta,
      };
    } catch (error) {
      return {
        operation: 'chromosomal_operation',
        success: false,
        details: `Chromosomal operation failed: ${error}`,
        parentIds: [agent.id],
      };
    }
  }

  /**
   * Apply crossover between two agents
   */
  async applyCrossover(
    parent1: MicrobiomeAgent,
    parent2: MicrobiomeAgent,
    crossoverType?: CrossoverType
  ): Promise<GeneticOperationResult> {
    if (!this.config.enableCrossover || Math.random() > this.config.crossoverRate) {
      return {
        operation: 'crossover',
        success: false,
        details: 'Crossover disabled or did not trigger',
        parentIds: [parent1.id, parent2.id],
      };
    }

    const type = crossoverType || this.selectCrossoverType();
    const avgFitness = (parent1.evaluateFitness().overall + parent2.evaluateFitness().overall) / 2;
    let child: MicrobiomeAgent | undefined;
    let details = '';

    try {
      switch (type) {
        case CrossoverType.SINGLE_POINT:
          child = this.singlePointCrossover(parent1, parent2);
          details = `Single-point crossover: genes swapped at single point`;
          break;

        case CrossoverType.MULTI_POINT:
          child = this.multiPointCrossover(parent1, parent2, 2);
          details = `Multi-point crossover: genes swapped at 2 points`;
          break;

        case CrossoverType.UNIFORM:
          child = this.uniformCrossover(parent1, parent2);
          details = `Uniform crossover: genes selected randomly from parents`;
          break;

        case CrossoverType.COLONY_AWARE:
          child = this.colonyAwareCrossover(parent1, parent2);
          details = `Colony-aware crossover: colony membership considered`;
          break;
      }

      if (child) {
        const childFitness = child.evaluateFitness().overall;
        const fitnessDelta = childFitness - avgFitness;

        this.recordOperation({
          operation: 'crossover',
          success: true,
          details,
          parentIds: [parent1.id, parent2.id],
          child,
          fitnessDelta,
        });

        return {
          operation: 'crossover',
          success: true,
          details,
          parentIds: [parent1.id, parent2.id],
          child,
          fitnessDelta,
        };
      } else {
        return {
          operation: 'crossover',
          success: false,
          details: 'Crossover produced no viable offspring',
          parentIds: [parent1.id, parent2.id],
        };
      }
    } catch (error) {
      return {
        operation: 'crossover',
        success: false,
        details: `Crossover failed: ${error}`,
        parentIds: [parent1.id, parent2.id],
      };
    }
  }

  /**
   * Apply horizontal gene transfer between agents
   */
  async applyHorizontalTransfer(
    donor: MicrobiomeAgent,
    recipient: MicrobiomeAgent
  ): Promise<GeneticOperationResult> {
    if (!this.config.enableHorizontalTransfer || Math.random() > this.config.horizontalTransferRate) {
      return {
        operation: 'horizontal_transfer',
        success: false,
        details: 'Horizontal transfer disabled or did not trigger',
        parentIds: [donor.id, recipient.id],
      };
    }

    const oldFitness = recipient.evaluateFitness();
    let modifiedRecipient = recipient;
    let details = '';

    try {
      // Transfer metabolic genes
      if (Math.random() < 0.3) {
        modifiedRecipient = this.transferMetabolicGenes(donor, recipient);
        details = `Metabolic gene transfer from ${donor.id}`;
      }
      // Transfer processing genes
      else if (Math.random() < 0.3) {
        modifiedRecipient = this.transferProcessingGenes(donor, recipient);
        details = `Processing gene transfer from ${donor.id}`;
      }
      // Transfer symbiosis genes
      else {
        modifiedRecipient = this.transferSymbiosisGenes(donor, recipient);
        details = `Symbiosis gene transfer from ${donor.id}`;
      }

      const newFitness = modifiedRecipient.evaluateFitness();
      const fitnessDelta = newFitness.overall - oldFitness.overall;

      this.recordOperation({
        operation: 'horizontal_transfer',
        success: true,
        details,
        parentIds: [donor.id, recipient.id],
        child: modifiedRecipient,
        fitnessDelta,
      });

      return {
        operation: 'horizontal_transfer',
        success: true,
        details,
        parentIds: [donor.id, recipient.id],
        child: modifiedRecipient,
        fitnessDelta,
      };
    } catch (error) {
      return {
        operation: 'horizontal_transfer',
        success: false,
        details: `Horizontal transfer failed: ${error}`,
        parentIds: [donor.id, recipient.id],
      };
    }
  }

  /**
   * Update speciation information for population
   */
  updateSpeciation(population: MicrobiomeAgent[]): void {
    if (!this.config.enableSpeciation) {
      return;
    }

    this.species.clear();

    if (population.length === 0) {
      return;
    }

    // Calculate genetic distances and form species
    const assigned = new Set<string>();
    let speciesId = 0;

    for (const agent of population) {
      if (assigned.has(agent.id)) {
        continue;
      }

      // Start a new species
      const speciesMembers = new Set<string>([agent.id]);
      assigned.add(agent.id);

      // Find similar agents
      for (const other of population) {
        if (other.id === agent.id || assigned.has(other.id)) {
          continue;
        }

        const distance = this.calculateGeneticDistance(agent, other);
        if (distance < this.config.speciationThreshold) {
          speciesMembers.add(other.id);
          assigned.add(other.id);
        }
      }

      // Only create species if it meets minimum size
      if (speciesMembers.size >= this.config.minSpeciesSize || this.species.size < this.config.maxSpecies) {
        const members = Array.from(speciesMembers);
        const representative = population.find(a => a.id === members[0])!;

        this.species.set(`species_${speciesId}`, {
          speciesId: `species_${speciesId}`,
          members: speciesMembers,
          fitnessThreshold: representative.evaluateFitness().overall * 0.9,
          age: 0,
          geneticDistanceThreshold: this.config.speciationThreshold,
        });

        speciesId++;

        // Limit number of species
        if (this.species.size >= this.config.maxSpecies) {
          break;
        }
      }
    }
  }

  /**
   * Get species for an agent
   */
  getSpeciesForAgent(agentId: string): SpeciationInfo | null {
    for (const species of this.species.values()) {
      if (species.members.has(agentId)) {
        return species;
      }
    }
    return null;
  }

  /**
   * Check if two agents are in the same species
   */
  areSameSpecies(agentId1: string, agentId2: string): boolean {
    const species1 = this.getSpeciesForAgent(agentId1);
    const species2 = this.getSpeciesForAgent(agentId2);

    if (!species1 || !species2) {
      return false;
    }

    return species1.speciesId === species2.speciesId;
  }

  /**
   * Encourage mating within species
   */
  encourageIntraSpeciesMating(
    population: MicrobiomeAgent[],
    candidate: MicrobiomeAgent
  ): MicrobiomeAgent[] {
    if (!this.config.enableSpeciation) {
      return population;
    }

    const candidateSpecies = this.getSpeciesForAgent(candidate.id);
    if (!candidateSpecies) {
      return population;
    }

    // Prefer same-species mates
    const sameSpeciesMates: MicrobiomeAgent[] = [];
    const otherSpeciesMates: MicrobiomeAgent[] = [];

    for (const agent of population) {
      if (agent.id === candidate.id) {
        continue;
      }

      if (candidateSpecies.members.has(agent.id)) {
        sameSpeciesMates.push(agent);
      } else {
        otherSpeciesMates.push(agent);
      }
    }

    // Return same-species mates first (with 80% probability)
    if (Math.random() < 0.8 && sameSpeciesMates.length > 0) {
      return sameSpeciesMates;
    }

    return [...sameSpeciesMates, ...otherSpeciesMates];
  }

  /**
   * Get all species
   */
  getAllSpecies(): Map<string, SpeciationInfo> {
    return new Map(this.species);
  }

  /**
   * Get species diversity (count)
   */
  getSpeciesCount(): number {
    return this.species.size;
  }

  /**
   * Get operation history
   */
  getOperationHistory(): GeneticOperationResult[] {
    return [...this.operationHistory];
  }

  /**
   * Clear operation history
   */
  clearHistory(): void {
    this.operationHistory = [];
  }

  /**
   * Get configuration
   */
  getConfig(): GeneticOperatorsConfig {
    return { ...this.config };
  }

  /**
   * Update configuration
   */
  updateConfig(updates: Partial<GeneticOperatorsConfig>): void {
    this.config = { ...this.config, ...updates };
  }

  // ========== Private Methods ==========

  /**
   * Select a point mutation type
   */
  private selectPointMutationType(): PointMutationType {
    const types = [
      PointMutationType.GOAL_ADJUSTMENT,
      PointMutationType.METHOD_VARIATION,
      PointMutationType.METABOLIC_SHIFT,
      PointMutationType.SYMBIOSIS_GAIN,
      PointMutationType.SYMBIOSIS_LOSS,
    ];
    return types[Math.floor(Math.random() * types.length)];
  }

  /**
   * Select a chromosomal operation type
   */
  private selectChromosomalOperation(): ChromosomalOperationType {
    const operations = [
      ChromosomalOperationType.INVERSION,
      ChromosomalOperationType.TRANSPOSITION,
      ChromosomalOperationType.DELETION,
      ChromosomalOperationType.DUPLICATION,
    ];
    return operations[Math.floor(Math.random() * operations.length)];
  }

  /**
   * Select a crossover type
   */
  private selectCrossoverType(): CrossoverType {
    const types = [
      CrossoverType.SINGLE_POINT,
      CrossoverType.MULTI_POINT,
      CrossoverType.UNIFORM,
      CrossoverType.COLONY_AWARE,
    ];
    return types[Math.floor(Math.random() * types.length)];
  }

  /**
   * Apply goal adjustment mutation
   */
  private applyGoalAdjustment(agent: MicrobiomeAgent): MicrobiomeAgent {
    if (!(agent instanceof BaseBacteria)) {
      return agent; // Only works with BaseBacteria
    }

    // Create a mutated copy
    const mutated = this.cloneAgent(agent);

    // Adjust processing rate (±10%)
    mutated.metabolism.processingRate = Math.max(
      1,
      mutated.metabolism.processingRate * (1 + (Math.random() - 0.5) * this.config.maxMutationImpact)
    );

    // Adjust efficiency (±5%)
    mutated.metabolism.efficiency = Math.max(
      0.1,
      Math.min(
        1.0,
        mutated.metabolism.efficiency * (1 + (Math.random() - 0.5) * this.config.maxMutationImpact * 0.5)
      )
    );

    return mutated;
  }

  /**
   * Apply method variation mutation
   */
  private applyMethodVariation(agent: MicrobiomeAgent): MicrobiomeAgent {
    if (!(agent instanceof BaseBacteria)) {
      return agent;
    }

    const mutated = this.cloneAgent(agent);

    // Change efficiency more significantly (different algorithm)
    mutated.metabolism.efficiency = Math.max(
      0.1,
      Math.min(
        1.0,
        mutated.metabolism.efficiency + (Math.random() - 0.5) * this.config.maxMutationImpact
      )
    );

    // Also adjust processing rate
    mutated.metabolism.processingRate = Math.max(
      1,
      mutated.metabolism.processingRate * (1 + (Math.random() - 0.5) * this.config.maxMutationImpact * 0.3)
    );

    return mutated;
  }

  /**
   * Apply metabolic shift mutation
   */
  private applyMetabolicShift(agent: MicrobiomeAgent): MicrobiomeAgent {
    if (!(agent instanceof BaseBacteria)) {
      return agent;
    }

    const mutated = this.cloneAgent(agent);

    // 50% chance to add input, 50% to add output
    if (Math.random() < 0.5 && mutated.metabolism.inputs.length < 5) {
      // Add new input
      const newInput = this.getRandomResourceType();
      if (!mutated.metabolism.inputs.includes(newInput)) {
        mutated.metabolism.inputs = [...mutated.metabolism.inputs, newInput];
      }
    } else if (mutated.metabolism.outputs.length < 5) {
      // Add new output
      const newOutput = this.getRandomResourceType();
      if (!mutated.metabolism.outputs.includes(newOutput)) {
        mutated.metabolism.outputs = [...mutated.metabolism.outputs, newOutput];
      }
    }

    return mutated;
  }

  /**
   * Apply symbiosis gain mutation
   */
  private applySymbiosisGain(agent: MicrobiomeAgent): MicrobiomeAgent {
    if (!(agent instanceof BaseBacteria)) {
      return agent;
    }

    const mutated = this.cloneAgent(agent);

    // Add a new dependency
    const newDependency = `dep_${Math.random().toString(36).slice(2, 8)}`;
    mutated.dependencies = [...mutated.dependencies, newDependency];

    return mutated;
  }

  /**
   * Apply symbiosis loss mutation
   */
  private applySymbiosisLoss(agent: MicrobiomeAgent): MicrobiomeAgent {
    if (!(agent instanceof BaseBacteria)) {
      return agent;
    }

    const mutated = this.cloneAgent(agent);

    // Remove a random dependency if any exist
    if (mutated.dependencies.length > 0) {
      const idxToRemove = Math.floor(Math.random() * mutated.dependencies.length);
      mutated.dependencies = mutated.dependencies.filter((_, idx) => idx !== idxToRemove);
    }

    return mutated;
  }

  /**
   * Apply inversion chromosomal operation
   */
  private applyInversion(agent: MicrobiomeAgent): MicrobiomeAgent {
    if (!(agent instanceof BaseBacteria)) {
      return agent;
    }

    const mutated = this.cloneAgent(agent);

    // Reverse the order of inputs and outputs (simulating gene segment reversal)
    mutated.metabolism.inputs = [...mutated.metabolism.inputs].reverse();
    mutated.metabolism.outputs = [...mutated.metabolism.outputs].reverse();

    return mutated;
  }

  /**
   * Apply transposition chromosomal operation
   */
  private applyTransposition(agent: MicrobiomeAgent): MicrobiomeAgent {
    if (!(agent instanceof BaseBacteria)) {
      return agent;
    }

    const mutated = this.cloneAgent(agent);

    // Move an input to output or vice versa
    if (mutated.metabolism.inputs.length > 0 && Math.random() < 0.5) {
      const idxToMove = Math.floor(Math.random() * mutated.metabolism.inputs.length);
      const moved = mutated.metabolism.inputs[idxToMove];
      mutated.metabolism.inputs = mutated.metabolism.inputs.filter((_, idx) => idx !== idxToMove);

      if (!mutated.metabolism.outputs.includes(moved)) {
        mutated.metabolism.outputs = [...mutated.metabolism.outputs, moved];
      }
    } else if (mutated.metabolism.outputs.length > 0) {
      const idxToMove = Math.floor(Math.random() * mutated.metabolism.outputs.length);
      const moved = mutated.metabolism.outputs[idxToMove];
      mutated.metabolism.outputs = mutated.metabolism.outputs.filter((_, idx) => idx !== idxToMove);

      if (!mutated.metabolism.inputs.includes(moved)) {
        mutated.metabolism.inputs = [...mutated.metabolism.inputs, moved];
      }
    }

    return mutated;
  }

  /**
   * Apply deletion chromosomal operation
   */
  private applyDeletion(agent: MicrobiomeAgent): MicrobiomeAgent {
    if (!(agent instanceof BaseBacteria)) {
      return agent;
    }

    const mutated = this.cloneAgent(agent);

    // Remove a random input or output (but keep at least one of each)
    if (mutated.metabolism.inputs.length > 1 && Math.random() < 0.5) {
      const idxToDelete = Math.floor(Math.random() * mutated.metabolism.inputs.length);
      mutated.metabolism.inputs = mutated.metabolism.inputs.filter((_, idx) => idx !== idxToDelete);
    } else if (mutated.metabolism.outputs.length > 1) {
      const idxToDelete = Math.floor(Math.random() * mutated.metabolism.outputs.length);
      mutated.metabolism.outputs = mutated.metabolism.outputs.filter((_, idx) => idx !== idxToDelete);
    }

    return mutated;
  }

  /**
   * Apply duplication chromosomal operation
   */
  private applyDuplication(agent: MicrobiomeAgent): MicrobiomeAgent {
    if (!(agent instanceof BaseBacteria)) {
      return agent;
    }

    const mutated = this.cloneAgent(agent);

    // Duplicate a random input or output
    if (Math.random() < 0.5 && mutated.metabolism.inputs.length > 0 && mutated.metabolism.inputs.length < 5) {
      const idxToDuplicate = Math.floor(Math.random() * mutated.metabolism.inputs.length);
      const duplicated = mutated.metabolism.inputs[idxToDuplicate];
      // Insert at random position
      const insertPos = Math.floor(Math.random() * (mutated.metabolism.inputs.length + 1));
      mutated.metabolism.inputs = [
        ...mutated.metabolism.inputs.slice(0, insertPos),
        duplicated,
        ...mutated.metabolism.inputs.slice(insertPos),
      ];
    } else if (mutated.metabolism.outputs.length > 0 && mutated.metabolism.outputs.length < 5) {
      const idxToDuplicate = Math.floor(Math.random() * mutated.metabolism.outputs.length);
      const duplicated = mutated.metabolism.outputs[idxToDuplicate];
      const insertPos = Math.floor(Math.random() * (mutated.metabolism.outputs.length + 1));
      mutated.metabolism.outputs = [
        ...mutated.metabolism.outputs.slice(0, insertPos),
        duplicated,
        ...mutated.metabolism.outputs.slice(insertPos),
      ];
    }

    return mutated;
  }

  /**
   * Single-point crossover
   */
  private singlePointCrossover(parent1: MicrobiomeAgent, parent2: MicrobiomeAgent): MicrobiomeAgent {
    if (!(parent1 instanceof BaseBacteria) || !(parent2 instanceof BaseBacteria)) {
      return parent1; // Fallback
    }

    // Create child with mixture of parents' traits
    const child = this.cloneAgent(parent1);

    // Crossover point: mix inputs and outputs
    const crossoverPoint = Math.random();

    if (crossoverPoint < 0.5) {
      // Take inputs from parent1, outputs from parent2
      child.metabolism.inputs = [...parent2.metabolism.inputs];
    } else {
      // Take outputs from parent2
      child.metabolism.outputs = [...parent2.metabolism.outputs];
    }

    // Average the processing parameters
    child.metabolism.processingRate = Math.floor(
      (parent1.metabolism.processingRate + parent2.metabolism.processingRate) / 2
    );
    child.metabolism.efficiency = (parent1.metabolism.efficiency + parent2.metabolism.efficiency) / 2;

    // Mix dependencies
    const allDependencies = [...new Set([...parent1.dependencies, ...parent2.dependencies])];
    child.dependencies = allDependencies.slice(0, Math.max(parent1.dependencies.length, parent2.dependencies.length));

    return child;
  }

  /**
   * Multi-point crossover
   */
  private multiPointCrossover(parent1: MicrobiomeAgent, parent2: MicrobiomeAgent, points: number): MicrobiomeAgent {
    if (!(parent1 instanceof BaseBacteria) || !(parent2 instanceof BaseBacteria)) {
      return parent1;
    }

    const child = this.cloneAgent(parent1);

    // Apply multiple crossover points
    for (let i = 0; i < points; i++) {
      const crossoverPoint = Math.random();

      if (crossoverPoint < 0.33) {
        // Swap some inputs
        const swapCount = Math.floor(Math.random() * parent1.metabolism.inputs.length);
        child.metabolism.inputs = [
          ...parent1.metabolism.inputs.slice(0, swapCount),
          ...parent2.metabolism.inputs.slice(swapCount),
        ];
      } else if (crossoverPoint < 0.66) {
        // Swap some outputs
        const swapCount = Math.floor(Math.random() * parent1.metabolism.outputs.length);
        child.metabolism.outputs = [
          ...parent1.metabolism.outputs.slice(0, swapCount),
          ...parent2.metabolism.outputs.slice(swapCount),
        ];
      } else {
        // Swap dependencies
        child.dependencies = i % 2 === 0 ? [...parent2.dependencies] : [...parent1.dependencies];
      }
    }

    // Average processing parameters
    child.metabolism.processingRate = Math.floor(
      (parent1.metabolism.processingRate + parent2.metabolism.processingRate) / 2
    );
    child.metabolism.efficiency = (parent1.metabolism.efficiency + parent2.metabolism.efficiency) / 2;

    return child;
  }

  /**
   * Uniform crossover
   */
  private uniformCrossover(parent1: MicrobiomeAgent, parent2: MicrobiomeAgent): MicrobiomeAgent {
    if (!(parent1 instanceof BaseBacteria) || !(parent2 instanceof BaseBacteria)) {
      return parent1;
    }

    const child = this.cloneAgent(parent1);

    // For each input, randomly choose from parent1 or parent2
    const maxInputs = Math.max(parent1.metabolism.inputs.length, parent2.metabolism.inputs.length);
    child.metabolism.inputs = [];
    for (let i = 0; i < maxInputs; i++) {
      const fromParent1 = parent1.metabolism.inputs[i] !== undefined;
      const fromParent2 = parent2.metabolism.inputs[i] !== undefined;

      if (fromParent1 && fromParent2) {
        child.metabolism.inputs.push(Math.random() < 0.5 ? parent1.metabolism.inputs[i] : parent2.metabolism.inputs[i]);
      } else if (fromParent1) {
        child.metabolism.inputs.push(parent1.metabolism.inputs[i]);
      } else if (fromParent2) {
        child.metabolism.inputs.push(parent2.metabolism.inputs[i]);
      }
    }

    // For each output, randomly choose from parent1 or parent2
    const maxOutputs = Math.max(parent1.metabolism.outputs.length, parent2.metabolism.outputs.length);
    child.metabolism.outputs = [];
    for (let i = 0; i < maxOutputs; i++) {
      const fromParent1 = parent1.metabolism.outputs[i] !== undefined;
      const fromParent2 = parent2.metabolism.outputs[i] !== undefined;

      if (fromParent1 && fromParent2) {
        child.metabolism.outputs.push(Math.random() < 0.5 ? parent1.metabolism.outputs[i] : parent2.metabolism.outputs[i]);
      } else if (fromParent1) {
        child.metabolism.outputs.push(parent1.metabolism.outputs[i]);
      } else if (fromParent2) {
        child.metabolism.outputs.push(parent2.metabolism.outputs[i]);
      }
    }

    // Average processing parameters
    child.metabolism.processingRate = Math.floor(
      (parent1.metabolism.processingRate + parent2.metabolism.processingRate) / 2
    );
    child.metabolism.efficiency = (parent1.metabolism.efficiency + parent2.metabolism.efficiency) / 2;

    // Randomly select dependencies
    child.dependencies = [];
    const allDependencies = [...new Set([...parent1.dependencies, ...parent2.dependencies])];
    for (const dep of allDependencies) {
      if (Math.random() < 0.5) {
        child.dependencies.push(dep);
      }
    }

    return child;
  }

  /**
   * Colony-aware crossover
   */
  private colonyAwareCrossover(parent1: MicrobiomeAgent, parent2: MicrobiomeAgent): MicrobiomeAgent {
    // Get species information
    const species1 = this.getSpeciesForAgent(parent1.id);
    const species2 = this.getSpeciesForAgent(parent2.id);

    // If parents are in different species, discourage crossover
    if (species1 && species2 && species1.speciesId !== species2.speciesId) {
      // Return fitter parent
      return parent1.evaluateFitness().overall > parent2.evaluateFitness().overall ? parent1 : parent2;
    }

    // If same species, perform enhanced crossover
    const child = this.uniformCrossover(parent1, parent2);

    // Boost fitness if parents are compatible
    if (!(child instanceof BaseBacteria)) {
      return child;
    }

    // Enhance efficiency slightly for same-species crossover
    child.metabolism.efficiency = Math.min(1.0, child.metabolism.efficiency * 1.05);

    return child;
  }

  /**
   * Transfer metabolic genes
   */
  private transferMetabolicGenes(donor: MicrobiomeAgent, recipient: MicrobiomeAgent): MicrobiomeAgent {
    if (!(recipient instanceof BaseBacteria) || !(donor instanceof BaseBacteria)) {
      return recipient;
    }

    const modified = this.cloneAgent(recipient);

    // Transfer some inputs from donor
    const transferCount = Math.min(donor.metabolism.inputs.length, 2);
    for (let i = 0; i < transferCount; i++) {
      const input = donor.metabolism.inputs[i];
      if (!modified.metabolism.inputs.includes(input) && modified.metabolism.inputs.length < 5) {
        modified.metabolism.inputs = [...modified.metabolism.inputs, input];
      }
    }

    // Transfer some outputs from donor
    const outputTransferCount = Math.min(donor.metabolism.outputs.length, 2);
    for (let i = 0; i < outputTransferCount; i++) {
      const output = donor.metabolism.outputs[i];
      if (!modified.metabolism.outputs.includes(output) && modified.metabolism.outputs.length < 5) {
        modified.metabolism.outputs = [...modified.metabolism.outputs, output];
      }
    }

    return modified;
  }

  /**
   * Transfer processing genes
   */
  private transferProcessingGenes(donor: MicrobiomeAgent, recipient: MicrobiomeAgent): MicrobiomeAgent {
    if (!(recipient instanceof BaseBacteria) || !(donor instanceof BaseBacteria)) {
      return recipient;
    }

    const modified = this.cloneAgent(recipient);

    // Blend processing parameters
    modified.metabolism.processingRate = Math.floor(
      (modified.metabolism.processingRate + donor.metabolism.processingRate) / 2
    );
    modified.metabolism.efficiency = (modified.metabolism.efficiency + donor.metabolism.efficiency) / 2;

    return modified;
  }

  /**
   * Transfer symbiosis genes
   */
  private transferSymbiosisGenes(donor: MicrobiomeAgent, recipient: MicrobiomeAgent): MicrobiomeAgent {
    if (!(recipient instanceof BaseBacteria)) {
      return recipient;
    }

    const modified = this.cloneAgent(recipient);

    // Transfer some dependencies
    const transferCount = Math.min(donor.dependencies.length, 2);
    for (let i = 0; i < transferCount; i++) {
      const dep = donor.dependencies[i];
      if (!modified.dependencies.includes(dep)) {
        modified.dependencies = [...modified.dependencies, dep];
      }
    }

    return modified;
  }

  /**
   * Calculate genetic distance between two agents
   */
  private calculateGeneticDistance(agent1: MicrobiomeAgent, agent2: MicrobiomeAgent): number {
    // Check cache
    if (this.distanceCache.has(agent1.id) && this.distanceCache.get(agent1.id)!.has(agent2.id)) {
      return this.distanceCache.get(agent1.id)!.get(agent2.id)!;
    }

    let distance = 0;

    // Metabolic distance (40%)
    const metabolicDistance = this.calculateMetabolicDistance(agent1, agent2);
    distance += 0.4 * metabolicDistance;

    // Taxonomy distance (30%)
    const taxonomyDistance = agent1.taxonomy === agent2.taxonomy ? 0 : 1;
    distance += 0.3 * taxonomyDistance;

    // Complexity distance (20%)
    const complexityDistance = Math.abs(agent1.complexity - agent2.complexity);
    distance += 0.2 * complexityDistance;

    // Size distance (10%)
    const sizeDistance = Math.abs(agent1.size - agent2.size) / Math.max(agent1.size, agent2.size);
    distance += 0.1 * sizeDistance;

    // Cache result
    if (!this.distanceCache.has(agent1.id)) {
      this.distanceCache.set(agent1.id, new Map());
    }
    this.distanceCache.get(agent1.id)!.set(agent2.id, distance);

    return distance;
  }

  /**
   * Calculate metabolic distance
   */
  private calculateMetabolicDistance(agent1: MicrobiomeAgent, agent2: MicrobiomeAgent): number {
    const inputs1 = new Set(agent1.metabolism.inputs);
    const inputs2 = new Set(agent2.metabolism.inputs);
    const outputs1 = new Set(agent1.metabolism.outputs);
    const outputs2 = new Set(agent2.metabolism.outputs);

    // Jaccard distance for inputs
    const inputIntersection = new Set([...inputs1].filter(x => inputs2.has(x)));
    const inputUnion = new Set([...inputs1, ...inputs2]);
    const inputDistance = inputUnion.size === 0 ? 0 : 1 - inputIntersection.size / inputUnion.size;

    // Jaccard distance for outputs
    const outputIntersection = new Set([...outputs1].filter(x => outputs2.has(x)));
    const outputUnion = new Set([...outputs1, ...outputs2]);
    const outputDistance = outputUnion.size === 0 ? 0 : 1 - outputIntersection.size / outputUnion.size;

    // Efficiency difference
    const efficiencyDistance = Math.abs(agent1.metabolism.efficiency - agent2.metabolism.efficiency);

    return (inputDistance + outputDistance + efficiencyDistance) / 3;
  }

  /**
   * Clone an agent (deep copy for mutation)
   */
  private cloneAgent(agent: MicrobiomeAgent): MicrobiomeAgent {
    if (!(agent instanceof BaseBacteria)) {
      return agent;
    }

    // Create a new instance with the same properties
    const cloned = new BaseBacteria({
      name: agent.name,
      inputs: [...agent.metabolism.inputs],
      outputs: [...agent.metabolism.outputs],
      processingRate: agent.metabolism.processingRate,
      efficiency: agent.metabolism.efficiency,
      processor: async (input) => {
        // Use a default processor that mimics the original
        const output = new Map();
        for (const out of agent.metabolism.outputs) {
          output.set(out, 1);
        }
        return output;
      },
      reproductionThreshold: (agent as any).reproductionThreshold || 1000,
      dependencies: [...agent.dependencies],
      parentId: agent.parentId,
      generation: agent.generation,
      size: agent.size,
      complexity: agent.complexity,
    });

    // Copy lifecycle state
    cloned.lifecycle = { ...agent.lifecycle };
    cloned.accumulatedResources = (agent as any).accumulatedResources || 0;

    return cloned;
  }

  /**
   * Get a random resource type
   */
  private getRandomResourceType(): ResourceType {
    const types = Object.values(ResourceType);
    return types[Math.floor(Math.random() * types.length)];
  }

  /**
   * Record genetic operation
   */
  private recordOperation(result: GeneticOperationResult): void {
    this.operationHistory.push(result);

    // Keep only last 1000 operations
    if (this.operationHistory.length > 1000) {
      this.operationHistory.shift();
    }
  }
}

/**
 * Create genetic operators with default configuration
 */
export function createGeneticOperators(config?: Partial<GeneticOperatorsConfig>): GeneticOperators {
  return new GeneticOperators(config);
}
