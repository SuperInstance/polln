/**
 * POLLN Microbiome - Population Dynamics
 *
 * Models agent populations using Lotka-Volterra equations.
 * Populations follow resource availability (the data diet).
 *
 * @module microbiome/population
 */

import { AgentTaxonomy, ResourceType, PopulationDynamics, ResourceFlow } from './types.js';

/**
 * Lotka-Volterra parameters for a population
 */
export interface LotkaVolterraParams {
  /** Natural growth rate (births per capita) */
  alpha: number;
  /** Natural death rate (deaths per capita) */
  beta: number;
  /** Carrying capacity */
  K: number;
  /** Predation/competition coefficient */
  gamma: number;
}

/**
 * Population state
 */
export interface PopulationState {
  /** Current population */
  N: number;
  /** Growth rate */
  dN: number;
  /** Time since last update */
  lastUpdate: number;
}

/**
 * Population dynamics engine
 */
export class PopulationDynamicsEngine {
  /** Population states by taxonomy */
  private populations: Map<AgentTaxonomy, PopulationState>;
  /** LV parameters by taxonomy */
  private params: Map<AgentTaxonomy, LotkaVolterraParams>;
  /** Resource flows */
  private resourceFlows: Map<ResourceType, ResourceFlow>;
  /** Predation matrix (who eats whom) */
  private predationMatrix: Map<AgentTaxonomy, Map<AgentTaxonomy, number>>;

  constructor() {
    this.populations = new Map();
    this.params = new Map();
    this.resourceFlows = new Map();
    this.predationMatrix = new Map();

    // Initialize default populations
    for (const taxonomy of Object.values(AgentTaxonomy)) {
      this.populations.set(taxonomy, {
        N: 0,
        dN: 0,
        lastUpdate: Date.now(),
      });

      // Default parameters
      this.params.set(taxonomy, {
        alpha: 0.1,  // 10% growth rate
        beta: 0.05,  // 5% death rate
        K: 1000,     // Carrying capacity
        gamma: 0.01, // Low predation
      });
    }

    // Initialize predation matrix
    for (const predator of Object.values(AgentTaxonomy)) {
      this.predationMatrix.set(predator, new Map());
    }

    // Set up natural predation relationships
    // Macrophages eat viruses
    this.setPredation(AgentTaxonomy.MACROPHAGE, AgentTaxonomy.VIRUS, 0.1);
    // Explorers might be consumed by larger colonies
    this.setPredation(AgentTaxonomy.COLONY, AgentTaxonomy.EXPLORER, 0.05);
  }

  /**
   * Set Lotka-Volterra parameters for a taxonomy
   */
  setParams(taxonomy: AgentTaxonomy, params: Partial<LotkaVolterraParams>): void {
    const current = this.params.get(taxonomy);
    if (current) {
      this.params.set(taxonomy, { ...current, ...params });
    }
  }

  /**
   * Set predation coefficient
   */
  setPredation(predator: AgentTaxonomy, prey: AgentTaxonomy, coefficient: number): void {
    const row = this.predationMatrix.get(predator);
    if (row) {
      row.set(prey, coefficient);
    }
  }

  /**
   * Set initial population
   */
  setPopulation(taxonomy: AgentTaxonomy, N: number): void {
    const state = this.populations.get(taxonomy);
    if (state) {
      state.N = Math.max(0, N);
      state.lastUpdate = Date.now();
    }
  }

  /**
   * Update resource flow
   */
  setResourceFlow(resource: ResourceType, flow: ResourceFlow): void {
    this.resourceFlows.set(resource, flow);
  }

  /**
   * Get population
   */
  getPopulation(taxonomy: AgentTaxonomy): number {
    return this.populations.get(taxonomy)?.N || 0;
  }

  /**
   * Get population dynamics
   */
  getPopulationDynamics(taxonomy: AgentTaxonomy): PopulationDynamics | null {
    const state = this.populations.get(taxonomy);
    const params = this.params.get(taxonomy);
    if (!state || !params) return null;

    return {
      population: state.N,
      birthRate: state.dN > 0 ? state.dN : 0,
      deathRate: state.dN < 0 ? -state.dN : 0,
      carryingCapacity: params.K,
    };
  }

  /**
   * Get carrying capacity based on resource availability
   */
  private getCarryingCapacity(taxonomy: AgentTaxonomy): number {
    const params = this.params.get(taxonomy);
    if (!params) return params?.K || 1000;

    // Modify carrying capacity based on resource availability
    let resourceMultiplier = 1.0;

    // Calculate total resource flow
    let totalResourceFlow = 0;
    for (const flow of this.resourceFlows.values()) {
      totalResourceFlow += flow.flowRate;
    }

    // If resources are scarce, reduce carrying capacity
    if (totalResourceFlow < 100) {
      resourceMultiplier = 0.5;
    } else if (totalResourceFlow > 1000) {
      resourceMultiplier = 1.5;
    }

    return params.K * resourceMultiplier;
  }

  /**
   * Calculate growth rate using Lotka-Volterra equation
   *
   * dN/dt = alpha*N - beta*N^2/K - sum(gamma*N*P)
   *
   * Where:
   * - alpha: birth rate
   * - beta: death rate
   * - K: carrying capacity
   * - gamma: predation coefficient
   * - P: predator population
   */
  private calculateGrowthRate(taxonomy: AgentTaxonomy): number {
    const state = this.populations.get(taxonomy);
    const params = this.params.get(taxonomy);
    if (!state || !params || state.N <= 0) return 0;

    const N = state.N;
    const K = this.getCarryingCapacity(taxonomy);

    // Natural growth: alpha * N
    const birthTerm = params.alpha * N;

    // Intraspecific competition: beta * N^2 / K
    const competitionTerm = params.beta * (N * N) / K;

    // Predation/competition from other species
    let predationTerm = 0;
    for (const [predator, preyMap] of this.predationMatrix.entries()) {
      const coefficient = preyMap.get(taxonomy) || 0;
      if (coefficient > 0) {
        const predatorPop = this.getPopulation(predator);
        predationTerm += coefficient * N * predatorPop;
      }
    }

    // Net growth rate
    const dN = birthTerm - competitionTerm - predationTerm;

    return dN;
  }

  /**
   * Update populations by one time step
   */
  update(dt: number = 1000): void {
    // Calculate growth rates for all populations
    const growthRates = new Map<AgentTaxonomy, number>();

    for (const taxonomy of Object.values(AgentTaxonomy)) {
      const rate = this.calculateGrowthRate(taxonomy);
      growthRates.set(taxonomy, rate);
    }

    // Apply updates
    for (const [taxonomy, state] of this.populations.entries()) {
      const dN = growthRates.get(taxonomy) || 0;
      const deltaN = (dN * dt) / 1000; // Convert to population change

      state.N = Math.max(0, state.N + deltaN);
      state.dN = dN;
      state.lastUpdate = Date.now();
    }
  }

  /**
   * Simulate population dynamics over time
   */
  simulate(duration: number, stepMs: number = 1000): Map<AgentTaxonomy, number[]> {
    const results = new Map<AgentTaxonomy, number[]>();

    // Initialize arrays
    for (const taxonomy of Object.values(AgentTaxonomy)) {
      results.set(taxonomy, [this.getPopulation(taxonomy)]);
    }

    // Simulate
    let time = 0;
    while (time < duration) {
      this.update(stepMs);
      time += stepMs;

      for (const taxonomy of Object.values(AgentTaxonomy)) {
        const arr = results.get(taxonomy);
        if (arr) {
          arr.push(this.getPopulation(taxonomy));
        }
      }
    }

    return results;
  }

  /**
   * Get equilibrium populations
   *
   * Solves for dN/dt = 0
   */
  getEquilibrium(): Map<AgentTaxonomy, number> {
    const equilibrium = new Map<AgentTaxonomy, number>();

    for (const [taxonomy, params] of this.params.entries()) {
      // Simple equilibrium without predation: N = K * alpha / beta
      const N = (params.K * params.alpha) / params.beta;
      equilibrium.set(taxonomy, Math.max(0, N));
    }

    return equilibrium;
  }

  /**
   * Check if populations are stable
   */
  isStable(threshold: number = 0.01): boolean {
    for (const [_, state] of this.populations) {
      if (Math.abs(state.dN) > threshold * state.N) {
        return false;
      }
    }
    return true;
  }

  /**
   * Get total population
   */
  getTotalPopulation(): number {
    let total = 0;
    for (const state of this.populations.values()) {
      total += state.N;
    }
    return total;
  }

  /**
   * Get population distribution
   */
  getDistribution(): Map<AgentTaxonomy, number> {
    const total = this.getTotalPopulation();
    const distribution = new Map<AgentTaxonomy, number>();

    for (const [taxonomy, state] of this.populations) {
      distribution.set(taxonomy, total > 0 ? state.N / total : 0);
    }

    return distribution;
  }

  /**
   * Get diversity index (Shannon entropy)
   */
  getDiversity(): number {
    const distribution = this.getDistribution();
    let diversity = 0;

    for (const p of distribution.values()) {
      if (p > 0) {
        diversity -= p * Math.log(p);
      }
    }

    return diversity;
  }

  /**
   * Get dominant species
   */
  getDominantSpecies(): AgentTaxonomy[] {
    const distribution = this.getDistribution();
    const maxP = Math.max(...distribution.values());

    const dominant: AgentTaxonomy[] = [];
    for (const [taxonomy, p] of distribution.entries()) {
      if (p === maxP) {
        dominant.push(taxonomy);
      }
    }

    return dominant;
  }

  /**
   * Export state
   */
  exportState(): any {
    return {
      populations: Object.fromEntries(this.populations),
      params: Object.fromEntries(this.params),
      resourceFlows: Object.fromEntries(this.resourceFlows),
      predationMatrix: Object.fromEntries(
        Array.from(this.predationMatrix.entries()).map(([k, v]) => [
          k,
          Object.fromEntries(v),
        ])
      ),
    };
  }

  /**
   * Import state
   */
  importState(state: any): void {
    if (state.populations) {
      for (const [key, value] of Object.entries(state.populations)) {
        this.populations.set(key as AgentTaxonomy, value as PopulationState);
      }
    }
    if (state.params) {
      for (const [key, value] of Object.entries(state.params)) {
        this.params.set(key as AgentTaxonomy, value as LotkaVolterraParams);
      }
    }
    if (state.resourceFlows) {
      for (const [key, value] of Object.entries(state.resourceFlows)) {
        this.resourceFlows.set(key as ResourceType, value as ResourceFlow);
      }
    }
    if (state.predationMatrix) {
      for (const [predator, preyMap] of Object.entries(state.predationMatrix)) {
        const row = new Map<AgentTaxonomy, number>();
        for (const [prey, coeff] of Object.entries(preyMap)) {
          row.set(prey as AgentTaxonomy, coeff as number);
        }
        this.predationMatrix.set(predator as AgentTaxonomy, row);
      }
    }
  }
}

/**
 * Create a population dynamics engine with default settings
 */
export function createPopulationEngine(): PopulationDynamicsEngine {
  return new PopulationDynamicsEngine();
}

/**
 * Analyze population time series
 */
export function analyzePopulationSeries(
  series: Map<AgentTaxonomy, number[]>
): {
  min: Map<AgentTaxonomy, number>;
  max: Map<AgentTaxonomy, number>;
  mean: Map<AgentTaxonomy, number>;
  variance: Map<AgentTaxonomy, number>;
} {
  const min = new Map<AgentTaxonomy, number>();
  const max = new Map<AgentTaxonomy, number>();
  const mean = new Map<AgentTaxonomy, number>();
  const variance = new Map<AgentTaxonomy, number>();

  for (const [taxonomy, values] of series.entries()) {
    if (values.length === 0) continue;

    let minValue = Infinity;
    let maxValue = -Infinity;
    let sum = 0;

    for (const v of values) {
      minValue = Math.min(minValue, v);
      maxValue = Math.max(maxValue, v);
      sum += v;
    }

    const avg = sum / values.length;
    let sumSquaredDiff = 0;

    for (const v of values) {
      sumSquaredDiff += (v - avg) ** 2;
    }

    min.set(taxonomy, minValue);
    max.set(taxonomy, maxValue);
    mean.set(taxonomy, avg);
    variance.set(taxonomy, sumSquaredDiff / values.length);
  }

  return { min, max, mean, variance };
}
