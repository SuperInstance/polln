/**
 * POLLN Microbiome - Evolution Engine
 *
 * Phase 3: Evolution & Natural Selection
 * Implements sophisticated evolutionary mechanisms with selection,
 * mutation, and survival strategies for population optimization.
 *
 * @module microbiome/evolution
 */

import {
  MicrobiomeAgent,
  FitnessScore,
  MutationConfig,
  EcosystemSnapshot,
} from './types.js';

/**
 * Selection strategy for choosing parents
 */
export enum SelectionStrategy {
  /** Tournament selection: pick k random, choose best */
  TOURNAMENT = 'tournament',
  /** Roulette wheel: fitness-proportional selection */
  ROULETTE = 'roulette',
  /** Rank selection: based on fitness rank */
  RANK = 'rank',
  /** Truncation selection: top n get to reproduce */
  TRUNCATION = 'truncation',
}

/**
 * Survival selection strategy
 */
export enum SurvivalStrategy {
  /** Generational: replace all parents */
  GENERATIONAL = 'generational',
  /** Steady-state: replace worst individuals */
  STEADY_STATE = 'steady_state',
  /** Mixed: replace some parents */
  MIXED = 'mixed',
}

/**
 * Evolution report after each generation
 */
export interface EvolutionReport {
  /** Current generation number */
  generation: number;
  /** Best fitness in population */
  bestFitness: number;
  /** Average fitness in population */
  avgFitness: number;
  /** Worst fitness in population */
  worstFitness: number;
  /** Population diversity (Shannon entropy) */
  diversity: number;
  /** Number of mutations applied */
  mutationCount: number;
  /** Number of births */
  births: number;
  /** Number of deaths */
  deaths: number;
  /** Number of crossovers */
  crossoverCount: number;
  /** Change in best fitness from previous generation */
  fitnessDelta: number;
  /** Population size */
  populationSize: number;
  /** Number of species (distinct groups) */
  speciesCount: number;
}

/**
 * Evolutionary metrics over time
 */
export interface EvolutionMetrics {
  /** Current generation */
  generation: number;
  /** Best fitness ever seen */
  bestFitnessEver: number;
  /** Generation when best fitness was achieved */
  bestFitnessGeneration: number;
  /** Average fitness history */
  fitnessHistory: number[];
  /** Diversity history */
  diversityHistory: number[];
  /** Population size history */
  populationHistory: number[];
  /** Convergence rate (fitness improvement per generation) */
  convergenceRate: number;
  /** Stagnation count (generations without improvement) */
  stagnationCount: number;
}

/**
 * Evolution engine configuration
 */
export interface EvolutionConfig {
  /** Selection strategy */
  selectionStrategy: SelectionStrategy;
  /** Survival strategy */
  survivalStrategy: SurvivalStrategy;
  /** Selection pressure (0-1, higher = more selective) */
  selectionPressure: number;
  /** Mutation rate (0-1) */
  mutationRate: number;
  /** Crossover rate (0-1) */
  crossoverRate: number;
  /** Elitism: top % to preserve unchanged (0-1) */
  elitism: number;
  /** Tournament size for tournament selection */
  tournamentSize: number;
  /** Survival rate for steady-state (0-1) */
  survivalRate: number;
  /** Maximum population size */
  maxPopulation: number;
  /** Minimum population size */
  minPopulation: number;
  /** Enable crossover operations */
  enableCrossover: boolean;
  /** Enable mutation operations */
  enableMutation: boolean;
  /** Stagnation threshold for adaptive evolution */
  stagnationThreshold: number;
}

/**
 * Species information for speciation
 */
export interface Species {
  /** Species ID */
  id: string;
  /** Member agent IDs */
  members: Set<string>;
  /** Species representative (first member) */
  representative: MicrobiomeAgent;
  /** Fitness threshold for this species */
  fitnessThreshold: number;
  /** Age of species in generations */
  age: number;
}

/**
 * Evolution Engine
 *
 * Orchestrates the evolutionary process with sophisticated selection,
 * reproduction, and survival mechanisms. Maintains population diversity
 * while driving fitness improvement.
 */
export class EvolutionEngine {
  /** Current population */
  private population: Map<string, MicrobiomeAgent>;
  /** Current generation number */
  private generation: number;
  /** Configuration */
  private config: EvolutionConfig;
  /** Species information */
  private species: Map<string, Species>;
  /** Fitness cache for performance */
  private fitnessCache: Map<string, FitnessScore>;
  /** Evolutionary metrics */
  private metrics: EvolutionMetrics;
  /** Previous generation's best fitness */
  private previousBestFitness: number;
  /** Stagnation counter */
  private stagnationCounter: number;

  constructor(config: Partial<EvolutionConfig> = {}) {
    this.population = new Map();
    this.generation = 0;
    this.species = new Map();
    this.fitnessCache = new Map();

    this.metrics = {
      generation: 0,
      bestFitnessEver: 0,
      bestFitnessGeneration: 0,
      fitnessHistory: [],
      diversityHistory: [],
      populationHistory: [],
      convergenceRate: 0,
      stagnationCount: 0,
    };

    this.previousBestFitness = 0;
    this.stagnationCounter = 0;

    this.config = {
      selectionStrategy: config.selectionStrategy ?? SelectionStrategy.TOURNAMENT,
      survivalStrategy: config.survivalStrategy ?? SurvivalStrategy.GENERATIONAL,
      selectionPressure: config.selectionPressure ?? 0.7,
      mutationRate: config.mutationRate ?? 0.01,
      crossoverRate: config.crossoverRate ?? 0.7,
      elitism: config.elitism ?? 0.1,
      tournamentSize: config.tournamentSize ?? 3,
      survivalRate: config.survivalRate ?? 0.5,
      maxPopulation: config.maxPopulation ?? 10000,
      minPopulation: config.minPopulation ?? 100,
      enableCrossover: config.enableCrossover ?? true,
      enableMutation: config.enableMutation ?? true,
      stagnationThreshold: config.stagnationThreshold ?? 10,
    };
  }

  /**
   * Set the population for evolution
   */
  setPopulation(population: Map<string, MicrobiomeAgent>): void {
    this.population = new Map(population);
    this.fitnessCache.clear();
    this.updateSpecies();
  }

  /**
   * Add an agent to the population
   */
  addAgent(agent: MicrobiomeAgent): void {
    this.population.set(agent.id, agent);
    this.fitnessCache.delete(agent.id);
  }

  /**
   * Remove an agent from the population
   */
  removeAgent(agentId: string): boolean {
    this.fitnessCache.delete(agentId);
    return this.population.delete(agentId);
  }

  /**
   * Get current population
   */
  getPopulation(): Map<string, MicrobiomeAgent> {
    return new Map(this.population);
  }

  /**
   * Evolve one generation
   */
  async evolveGeneration(): Promise<EvolutionReport> {
    const startTime = Date.now();

    // Clear fitness cache
    this.fitnessCache.clear();

    // Evaluate fitness for all agents
    const fitnessMap = this.evaluateAllFitness();

    // Calculate current metrics
    const fitnessValues = Array.from(fitnessMap.values()).map(f => f.overall);
    const avgFitness = fitnessValues.reduce((a, b) => a + b, 0) / fitnessValues.length;
    const bestFitness = Math.max(...fitnessValues);
    const worstFitness = Math.min(...fitnessValues);
    const diversity = this.calculateDiversity();

    // Track best fitness ever
    if (bestFitness > this.metrics.bestFitnessEver) {
      this.metrics.bestFitnessEver = bestFitness;
      this.metrics.bestFitnessGeneration = this.generation;
      this.stagnationCounter = 0;
    } else {
      this.stagnationCounter++;
    }

    const fitnessDelta = bestFitness - this.previousBestFitness;
    this.previousBestFitness = bestFitness;

    // Select parents
    const parents = await this.selectParents(fitnessMap);

    // Create offspring
    const offspring = await this.reproduce(parents);

    // Select survivors
    const survivors = await this.selectSurvivors(fitnessMap, offspring);

    // Update population
    this.population = survivors;
    this.generation++;

    // Update species
    this.updateSpecies();

    // Update metrics
    this.metrics.generation = this.generation;
    this.metrics.fitnessHistory.push(avgFitness);
    this.metrics.diversityHistory.push(diversity);
    this.metrics.populationHistory.push(this.population.size);
    this.metrics.stagnationCount = this.stagnationCounter;

    // Calculate convergence rate (average improvement over last 10 generations)
    const historyLength = Math.min(10, this.metrics.fitnessHistory.length);
    if (historyLength >= 2) {
      const recent = this.metrics.fitnessHistory.slice(-historyLength);
      const improvements: number[] = [];
      for (let i = 1; i < recent.length; i++) {
        improvements.push(recent[i] - recent[i - 1]);
      }
      this.metrics.convergenceRate = improvements.reduce((a, b) => a + b, 0) / improvements.length;
    }

    // Calculate mutation and crossover counts
    const mutationCount = offspring.filter(o => o.parentId && o.generation > 0).length;
    const crossoverCount = Math.floor(parents.length / 2);

    // Generate report
    const report: EvolutionReport = {
      generation: this.generation,
      bestFitness,
      avgFitness,
      worstFitness,
      diversity,
      mutationCount,
      births: offspring.length,
      deaths: this.population.size - offspring.length,
      crossoverCount,
      fitnessDelta,
      populationSize: this.population.size,
      speciesCount: this.species.size,
    };

    return report;
  }

  /**
   * Evaluate fitness for all agents
   */
  private evaluateAllFitness(): Map<string, FitnessScore> {
    const fitnessMap = new Map<string, FitnessScore>();

    for (const [id, agent] of this.population.entries()) {
      if (agent.lifecycle.isAlive) {
        const fitness = agent.evaluateFitness();
        this.fitnessCache.set(id, fitness);
        fitnessMap.set(id, fitness);
      }
    }

    return fitnessMap;
  }

  /**
   * Select parents for reproduction
   */
  private async selectParents(fitnessMap: Map<string, FitnessScore>): Promise<MicrobiomeAgent[]> {
    const aliveAgents = Array.from(this.population.entries())
      .filter(([_, agent]) => agent.lifecycle.isAlive);

    let parents: MicrobiomeAgent[] = [];

    // Elitism: preserve top performers unchanged
    const eliteCount = Math.floor(aliveAgents.length * this.config.elitism);
    if (eliteCount > 0) {
      const sorted = [...aliveAgents].sort((a, b) => {
        const fitnessA = fitnessMap.get(a[0])?.overall ?? 0;
        const fitnessB = fitnessMap.get(b[0])?.overall ?? 0;
        return fitnessB - fitnessA;
      });

      for (let i = 0; i < eliteCount; i++) {
        parents.push(sorted[i][1]);
      }
    }

    // Select remaining parents based on strategy
    const remainingCount = Math.max(aliveAgents.length - eliteCount, 0);

    switch (this.config.selectionStrategy) {
      case SelectionStrategy.TOURNAMENT:
        parents.push(...this.tournamentSelection(aliveAgents, fitnessMap, remainingCount));
        break;

      case SelectionStrategy.ROULETTE:
        parents.push(...this.rouletteWheelSelection(aliveAgents, fitnessMap, remainingCount));
        break;

      case SelectionStrategy.RANK:
        parents.push(...this.rankSelection(aliveAgents, fitnessMap, remainingCount));
        break;

      case SelectionStrategy.TRUNCATION:
        parents.push(...this.truncationSelection(aliveAgents, fitnessMap, remainingCount));
        break;
    }

    return parents;
  }

  /**
   * Tournament selection
   */
  private tournamentSelection(
    agents: [string, MicrobiomeAgent][],
    fitnessMap: Map<string, FitnessScore>,
    count: number
  ): MicrobiomeAgent[] {
    const selected: MicrobiomeAgent[] = [];

    for (let i = 0; i < count; i++) {
      // Pick k random agents for tournament
      const tournament: [string, MicrobiomeAgent][] = [];
      for (let j = 0; j < this.config.tournamentSize; j++) {
        const randomIdx = Math.floor(Math.random() * agents.length);
        tournament.push(agents[randomIdx]);
      }

      // Select best from tournament
      tournament.sort((a, b) => {
        const fitnessA = fitnessMap.get(a[0])?.overall ?? 0;
        const fitnessB = fitnessMap.get(b[0])?.overall ?? 0;
        return fitnessB - fitnessA;
      });

      selected.push(tournament[0][1]);
    }

    return selected;
  }

  /**
   * Roulette wheel selection
   */
  private rouletteWheelSelection(
    agents: [string, MicrobiomeAgent][],
    fitnessMap: Map<string, FitnessScore>,
    count: number
  ): MicrobiomeAgent[] {
    const selected: MicrobiomeAgent[] = [];

    // Calculate total fitness
    let totalFitness = 0;
    for (const [id, _] of agents) {
      const fitness = fitnessMap.get(id)?.overall ?? 0;
      totalFitness += Math.max(0, fitness); // Ensure non-negative
    }

    if (totalFitness === 0) {
      // If all fitness is 0, select randomly
      for (let i = 0; i < count; i++) {
        const randomIdx = Math.floor(Math.random() * agents.length);
        selected.push(agents[randomIdx][1]);
      }
      return selected;
    }

    // Select with probability proportional to fitness
    for (let i = 0; i < count; i++) {
      let roulette = Math.random() * totalFitness;
      for (const [id, agent] of agents) {
        const fitness = Math.max(0, fitnessMap.get(id)?.overall ?? 0);
        roulette -= fitness;
        if (roulette <= 0) {
          selected.push(agent);
          break;
        }
      }

      // Fallback if we didn't select anyone
      if (selected.length <= i) {
        selected.push(agents[Math.floor(Math.random() * agents.length)][1]);
      }
    }

    return selected;
  }

  /**
   * Rank selection
   */
  private rankSelection(
    agents: [string, MicrobiomeAgent][],
    fitnessMap: Map<string, FitnessScore>,
    count: number
  ): MicrobiomeAgent[] {
    // Sort by fitness rank
    const sorted = [...agents].sort((a, b) => {
      const fitnessA = fitnessMap.get(a[0])?.overall ?? 0;
      const fitnessB = fitnessMap.get(b[0])?.overall ?? 0;
      return fitnessB - fitnessA;
    });

    // Assign ranks (best gets rank n)
    const n = sorted.length;
    const totalRank = n * (n + 1) / 2;

    const selected: MicrobiomeAgent[] = [];

    for (let i = 0; i < count; i++) {
      let roulette = Math.random() * totalRank;
      for (let j = 0; j < sorted.length; j++) {
        const rank = n - j; // Best has highest rank
        roulette -= rank;
        if (roulette <= 0) {
          selected.push(sorted[j][1]);
          break;
        }
      }

      // Fallback
      if (selected.length <= i) {
        selected.push(sorted[Math.floor(Math.random() * sorted.length)][1]);
      }
    }

    return selected;
  }

  /**
   * Truncation selection
   */
  private truncationSelection(
    agents: [string, MicrobiomeAgent][],
    fitnessMap: Map<string, FitnessScore>,
    count: number
  ): MicrobiomeAgent[] {
    // Sort by fitness
    const sorted = [...agents].sort((a, b) => {
      const fitnessA = fitnessMap.get(a[0])?.overall ?? 0;
      const fitnessB = fitnessMap.get(b[0])?.overall ?? 0;
      return fitnessB - fitnessA;
    });

    // Select top count
    return sorted.slice(0, count).map(([_, agent]) => agent);
  }

  /**
   * Create offspring from parents
   */
  private async reproduce(parents: MicrobiomeAgent[]): Promise<MicrobiomeAgent[]> {
    const offspring: MicrobiomeAgent[] = [];

    // Shuffle parents for random pairing
    const shuffled = [...parents].sort(() => Math.random() - 0.5);

    // Create mutation config
    const mutationConfig: MutationConfig = {
      mutationRate: this.config.mutationRate,
      mutationTypes: ['goal_adjustment', 'method_variation', 'metabolic_shift', 'symbiosis_gain'] as any,
      maxMutationImpact: 0.2,
    };

    // Apply crossover if enabled
    if (this.config.enableCrossover && this.config.crossoverRate > 0) {
      for (let i = 0; i < shuffled.length - 1; i += 2) {
        if (Math.random() < this.config.crossoverRate) {
          const parent1 = shuffled[i];
          const parent2 = shuffled[i + 1];

          // Simple crossover: each parent produces one child
          // In a full implementation, this would blend traits
          if (this.config.enableMutation && Math.random() < this.config.mutationRate) {
            try {
              const child = await parent1.reproduce(mutationConfig);
              offspring.push(child);
            } catch (error) {
              // Reproduction failed, skip this child
            }
          } else {
            try {
              const child = await parent1.reproduce({
                ...mutationConfig,
                mutationRate: 0, // No mutation
              });
              offspring.push(child);
            } catch (error) {
              // Reproduction failed
            }
          }
        }
      }
    }

    // Apply mutation to remaining parents
    if (this.config.enableMutation && this.config.mutationRate > 0) {
      for (const parent of shuffled) {
        if (Math.random() < this.config.mutationRate) {
          try {
            const child = await parent.reproduce(mutationConfig);
            offspring.push(child);
          } catch (error) {
            // Reproduction failed
          }
        }
      }
    }

    // Enforce population limits
    const maxSize = this.config.maxPopulation;
    if (this.population.size + offspring.length > maxSize) {
      // Trim offspring to fit
      const allowedOffspring = Math.max(0, maxSize - this.population.size);
      return offspring.slice(0, allowedOffspring);
    }

    return offspring;
  }

  /**
   * Select survivors for next generation
   */
  private async selectSurvivors(
    fitnessMap: Map<string, FitnessScore>,
    offspring: MicrobiomeAgent[]
  ): Promise<Map<string, MicrobiomeAgent>> {
    const survivors = new Map<string, MicrobiomeAgent>();

    switch (this.config.survivalStrategy) {
      case SurvivalStrategy.GENERATIONAL:
        // Replace all parents with offspring
        for (const child of offspring) {
          survivors.set(child.id, child);
        }

        // Ensure minimum population
        if (survivors.size < this.config.minPopulation) {
          // Add best parents to reach minimum
          const sortedParents = Array.from(this.population.entries())
            .filter(([_, agent]) => agent.lifecycle.isAlive)
            .sort((a, b) => {
              const fitnessA = fitnessMap.get(a[0])?.overall ?? 0;
              const fitnessB = fitnessMap.get(b[0])?.overall ?? 0;
              return fitnessB - fitnessA;
            });

          const needed = this.config.minPopulation - survivors.size;
          for (let i = 0; i < Math.min(needed, sortedParents.length); i++) {
            survivors.set(sortedParents[i][0], sortedParents[i][1]);
          }
        }
        break;

      case SurvivalStrategy.STEADY_STATE:
        // Replace worst individuals with offspring
        const allAgents = new Map<string, MicrobiomeAgent>();

        // Add all current agents
        for (const [id, agent] of this.population.entries()) {
          if (agent.lifecycle.isAlive) {
            allAgents.set(id, agent);
          }
        }

        // Add offspring
        for (const child of offspring) {
          allAgents.set(child.id, child);
        }

        // Keep top survivalRate
        const sorted = Array.from(allAgents.entries())
          .sort((a, b) => {
            const fitnessA = fitnessMap.get(a[0])?.overall ?? (a[1].evaluateFitness().overall);
            const fitnessB = fitnessMap.get(b[0])?.overall ?? (b[1].evaluateFitness().overall);
            return fitnessB - fitnessA;
          });

        const survivalCount = Math.floor(sorted.length * this.config.survivalRate);
        const toKeep = Math.max(this.config.minPopulation, survivalCount);

        for (let i = 0; i < Math.min(toKeep, sorted.length); i++) {
          survivors.set(sorted[i][0], sorted[i][1]);
        }
        break;

      case SurvivalStrategy.MIXED:
        // Keep elite parents and add offspring
        const eliteCount = Math.floor(this.population.size * this.config.elitism);

        // Add elite parents
        const eliteParents = Array.from(this.population.entries())
          .filter(([_, agent]) => agent.lifecycle.isAlive)
          .sort((a, b) => {
            const fitnessA = fitnessMap.get(a[0])?.overall ?? 0;
            const fitnessB = fitnessMap.get(b[0])?.overall ?? 0;
            return fitnessB - fitnessA;
          })
          .slice(0, eliteCount);

        for (const [id, agent] of eliteParents) {
          survivors.set(id, agent);
        }

        // Add offspring
        for (const child of offspring) {
          survivors.set(child.id, child);
        }

        // Ensure population limits
        if (survivors.size > this.config.maxPopulation) {
          // Trim to max
          const sortedSurvivors = Array.from(survivors.entries())
            .sort((a, b) => {
              const fitnessA = fitnessMap.get(a[0])?.overall ?? (a[1].evaluateFitness().overall);
              const fitnessB = fitnessMap.get(b[0])?.overall ?? (b[1].evaluateFitness().overall);
              return fitnessB - fitnessA;
            });

          survivors.clear();
          for (let i = 0; i < this.config.maxPopulation; i++) {
            survivors.set(sortedSurvivors[i][0], sortedSurvivors[i][1]);
          }
        }

        if (survivors.size < this.config.minPopulation) {
          // Add more parents to reach minimum
          const remainingParents = Array.from(this.population.entries())
            .filter(([_, agent]) => agent.lifecycle.isAlive && !survivors.has(agent.id))
            .sort((a, b) => {
              const fitnessA = fitnessMap.get(a[0])?.overall ?? 0;
              const fitnessB = fitnessMap.get(b[0])?.overall ?? 0;
              return fitnessB - fitnessA;
            });

          const needed = this.config.minPopulation - survivors.size;
          for (let i = 0; i < Math.min(needed, remainingParents.length); i++) {
            survivors.set(remainingParents[i][0], remainingParents[i][1]);
          }
        }
        break;
    }

    return survivors;
  }

  /**
   * Update species information
   */
  private updateSpecies(): void {
    this.species.clear();

    const aliveAgents = Array.from(this.population.values())
      .filter(agent => agent.lifecycle.isAlive);

    if (aliveAgents.length === 0) return;

    // Simple speciation based on taxonomy and complexity
    const speciesMap = new Map<string, MicrobiomeAgent[]>();

    for (const agent of aliveAgents) {
      const speciesKey = `${agent.taxonomy}_${Math.floor(agent.complexity * 10)}`;

      if (!speciesMap.has(speciesKey)) {
        speciesMap.set(speciesKey, []);
      }

      speciesMap.get(speciesKey)!.push(agent);
    }

    // Create species objects
    let speciesId = 0;
    for (const [key, members] of speciesMap.entries()) {
      this.species.set(`species_${speciesId++}`, {
        id: `species_${speciesId}`,
        members: new Set(members.map(m => m.id)),
        representative: members[0],
        fitnessThreshold: members[0].evaluateFitness().overall,
        age: this.generation,
      });
    }
  }

  /**
   * Calculate population diversity using Shannon entropy
   */
  private calculateDiversity(): number {
    const aliveAgents = Array.from(this.population.values())
      .filter(agent => agent.lifecycle.isAlive);

    if (aliveAgents.length === 0) return 0;

    const distribution = new Map<string, number>();

    // Count by taxonomy
    for (const agent of aliveAgents) {
      const key = agent.taxonomy;
      distribution.set(key, (distribution.get(key) ?? 0) + 1);
    }

    // Calculate Shannon entropy
    let diversity = 0;
    const total = aliveAgents.length;

    for (const count of distribution.values()) {
      if (count > 0) {
        const probability = count / total;
        diversity -= probability * Math.log(probability);
      }
    }

    return diversity;
  }

  /**
   * Get evolutionary metrics
   */
  getMetrics(): EvolutionMetrics {
    return { ...this.metrics };
  }

  /**
   * Get current configuration
   */
  getConfig(): EvolutionConfig {
    return { ...this.config };
  }

  /**
   * Update configuration
   */
  updateConfig(updates: Partial<EvolutionConfig>): void {
    this.config = { ...this.config, ...updates };
  }

  /**
   * Reset evolution state
   */
  reset(): void {
    this.generation = 0;
    this.metrics = {
      generation: 0,
      bestFitnessEver: 0,
      bestFitnessGeneration: 0,
      fitnessHistory: [],
      diversityHistory: [],
      populationHistory: [],
      convergenceRate: 0,
      stagnationCount: 0,
    };
    this.previousBestFitness = 0;
    this.stagnationCounter = 0;
    this.species.clear();
    this.fitnessCache.clear();
  }

  /**
   * Export state
   */
  exportState(): any {
    return {
      generation: this.generation,
      config: this.config,
      metrics: this.metrics,
      species: Array.from(this.species.entries()),
      population: Array.from(this.population.entries()),
    };
  }

  /**
   * Import state
   */
  importState(state: any): void {
    this.generation = state.generation ?? 0;
    this.config = { ...this.config, ...(state.config ?? {}) };
    this.metrics = { ...this.metrics, ...(state.metrics ?? {}) };
    this.species = new Map(state.species ?? []);
    this.population = new Map(state.population ?? []);
    this.previousBestFitness = this.metrics.bestFitnessEver;
    this.stagnationCounter = this.metrics.stagnationCount;
  }
}

/**
 * Create an evolution engine with default configuration
 */
export function createEvolutionEngine(
  config?: Partial<EvolutionConfig>
): EvolutionEngine {
  return new EvolutionEngine(config);
}
