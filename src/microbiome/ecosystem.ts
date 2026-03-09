/**
 * POLLN Microbiome - Ecosystem Manager
 *
 * The digital terrarium that hosts all microbiome agents.
 * Manages the complete ecosystem including populations, resources,
 * evolution, and the gardener's interventions.
 *
 * @module microbiome/ecosystem
 */

import { v4 as uuidv4 } from 'uuid';
import {
  MicrobiomeAgent,
  AgentTaxonomy,
  ResourceType,
  ResourceFlow,
  EcosystemSnapshot,
  EcosystemConfig,
  GardenerAction,
  ColonyStructure,
  Symbiosis,
  PopulationDynamics,
  MutationConfig,
  MutationType,
} from './types.js';
import { MetabolismManager } from './metabolism.js';
import { PopulationDynamicsEngine } from './population.js';
import { SymbiosisManager, EvolvableSymbiosis } from './symbiosis.js';
import { SymbiosisType } from './types.js';
import { ImmuneSystem, ImmuneSystemConfig } from './immune.js';
import { PerformanceMonitor } from './performance.js';

/**
 * Ecosystem event types
 */
export enum EcosystemEvent {
  AGENT_BORN = 'agent_born',
  AGENT_DIED = 'agent_died',
  AGENT_REPRODUCED = 'agent_reproduced',
  COLONY_FORMED = 'colony_formed',
  COLONY_DISSOLVED = 'colony_dissolved',
  SYMBIOSIS_FORMED = 'symbiosis_formed',
  SYMBIOSIS_BROKEN = 'symbiosis_broken',
  RESOURCE_DEPLETED = 'resource_depleted',
  POPULATION_CRASH = 'population_crash',
  EVOLUTION_STEP = 'evolution_step',
  THREAT_DETECTED = 'threat_detected',
  THREAT_NEUTRALIZED = 'threat_neutralized',
  ANTIBODY_PRODUCED = 'antibody_produced',
  AGENT_QUARANTINED = 'agent_quarantined',
  AGENT_TERMINATED = 'agent_terminated',
}

/**
 * Event listener
 */
export type EventListener = (event: EcosystemEvent, data: any) => void;

/**
 * Digital terrarium - the complete ecosystem
 */
export class DigitalTerrarium {
  /** All agents in the ecosystem */
  private agents: Map<string, MicrobiomeAgent>;
  /** Agents by taxonomy */
  private agentsByTaxonomy: Map<AgentTaxonomy, Set<string>>;
  /** Metabolism manager */
  private metabolism: MetabolismManager;
  /** Population dynamics engine */
  private population: PopulationDynamicsEngine;
  /** Symbiosis manager */
  private symbiosisMgr: SymbiosisManager;
  /** Immune system */
  private immuneSystem: ImmuneSystem;
  /** Active colonies */
  private colonies: Map<string, ColonyStructure>;
  /** Event listeners */
  private listeners: Map<EcosystemEvent, Set<EventListener>>;
  /** Performance monitor */
  private performanceMonitor: PerformanceMonitor;
  /** Configuration */
  private config: EcosystemConfig;
  /** Running state */
  private running: boolean;
  /** Simulation time */
  private simTime: number;

  constructor(config: Partial<EcosystemConfig> = {}) {
    this.agents = new Map();
    this.agentsByTaxonomy = new Map();
    for (const taxonomy of Object.values(AgentTaxonomy)) {
      this.agentsByTaxonomy.set(taxonomy, new Set());
    }

    this.metabolism = new MetabolismManager();
    this.population = new PopulationDynamicsEngine();
    this.symbiosisMgr = new SymbiosisManager();
    this.immuneSystem = new ImmuneSystem();
    this.colonies = new Map();
    this.listeners = new Map();
    this.performanceMonitor = new PerformanceMonitor();
    this.running = false;
    this.simTime = 0;

    this.config = {
      maxAgents: config.maxAgents ?? 10000,
      maxColonySize: config.maxColonySize ?? 1000,
      resourceRefreshRate: config.resourceRefreshRate ?? 1000,
      evolutionEnabled: config.evolutionEnabled ?? true,
      mutationConfig: config.mutationConfig ?? {
        mutationRate: 0.01,
        mutationTypes: [
          MutationType.GOAL_ADJUSTMENT,
          MutationType.METHOD_VARIATION,
          MutationType.METABOLIC_SHIFT,
          MutationType.SYMBIOSIS_GAIN,
        ],
        maxMutationImpact: 0.2,
      },
      selectionPressure: config.selectionPressure ?? 0.7,
    };
  }

  /**
   * Start the ecosystem simulation
   */
  async start(): Promise<void> {
    if (this.running) return;
    this.running = true;

    // Register existing agents with metabolism
    for (const [id, agent] of this.agents.entries()) {
      this.metabolism.registerChamber(id, agent.metabolism);
    }

    this.emit(EcosystemEvent.RESOURCE_DEPLETED, { message: 'Ecosystem started' });
  }

  /**
   * Stop the ecosystem simulation
   */
  async stop(): Promise<void> {
    this.running = false;
  }

  /**
   * Simulate one time step
   */
  async tick(dt: number = 100): Promise<void> {
    if (!this.running) return;

    await this.performanceMonitor.recordOperationAsync('ecosystem_tick', async () => {
      this.simTime += dt;

      // Process metabolism
      await this.performanceMonitor.recordOperationAsync('metabolism_process', async () => {
        await this.metabolism.processTick();
      });

      // Update population dynamics
      this.performanceMonitor.recordOperation('population_dynamics_update', 0);
      this.updatePopulationDynamics();

      // Process evolution
      if (this.config.evolutionEnabled) {
        await this.processEvolution();
      }

      // Age all agents
      this.performanceMonitor.recordOperation('agent_aging', 0);
      for (const agent of this.agents.values()) {
        if (agent.lifecycle.isAlive) {
          agent.age(dt);
        }
      }

      // Immune system scan and response
      await this.processImmuneSystem();

      // Remove dead agents
      this.performanceMonitor.recordOperation('remove_dead_agents', 0);
      this.removeDeadAgents();

      // Manage colonies
      this.performanceMonitor.recordOperation('manage_colonies', 0);
      this.manageColonies();

      // Enforce carrying capacity
      this.performanceMonitor.recordOperation('enforce_carrying_capacity', 0);
      this.enforceCarryingCapacity();
    });
  }

  /**
   * Introduce a new agent to the ecosystem
   */
  introduce(agent: MicrobiomeAgent): boolean {
    if (this.agents.size >= this.config.maxAgents) {
      return false;
    }

    this.agents.set(agent.id, agent);
    this.agentsByTaxonomy.get(agent.taxonomy)?.add(agent.id);

    // Register with metabolism
    this.metabolism.registerChamber(agent.id, agent.metabolism);

    // Update population
    const currentPop = this.population.getPopulation(agent.taxonomy);
    this.population.setPopulation(agent.taxonomy, currentPop + 1);

    this.emit(EcosystemEvent.AGENT_BORN, { agentId: agent.id, taxonomy: agent.taxonomy });

    return true;
  }

  /**
   * Remove an agent from the ecosystem
   */
  cull(agentId: string): boolean {
    const agent = this.agents.get(agentId);
    if (!agent) return false;

    // Mark as dead
    agent.lifecycle.isAlive = false;

    this.emit(EcosystemEvent.AGENT_DIED, { agentId: agent.id, taxonomy: agent.taxonomy });

    return true;
  }

  /**
   * Cull agents matching a condition
   */
  cullWhere(condition: (agent: MicrobiomeAgent) => boolean): number {
    let count = 0;
    for (const agent of this.agents.values()) {
      if (agent.lifecycle.isAlive && condition(agent)) {
        this.cull(agent.id);
        count++;
      }
    }
    return count;
  }

  /**
   * Add resources to the ecosystem
   */
  fertilize(resource: ResourceType, amount: number): void {
    this.metabolism.addResources(resource, amount);
  }

  /**
   * Restrict resource flow
   */
  restrict(resource: ResourceType, limit: number): void {
    const pool = this.metabolism.getResourcePool();
    pool.setCapacity(resource, limit);
  }

  /**
   * Create a colony (biofilm) from agents
   */
  graft(memberIds: string[]): ColonyStructure | null {
    if (memberIds.length < 2 || memberIds.length > this.config.maxColonySize) {
      return null;
    }

    // Verify all agents exist
    for (const id of memberIds) {
      if (!this.agents.has(id)) return null;
    }

    const colony: ColonyStructure = {
      id: uuidv4(),
      members: memberIds,
      communicationChannels: new Map(),
      formationTime: this.simTime,
      stability: 0.5,
      coEvolutionBonus: 0.1,
    };

    // Create direct communication channels (A2A shortcuts)
    for (let i = 0; i < memberIds.length; i++) {
      for (let j = i + 1; j < memberIds.length; j++) {
        colony.communicationChannels.set(memberIds[i], memberIds[j]);
        colony.communicationChannels.set(memberIds[j], memberIds[i]);
      }
    }

    this.colonies.set(colony.id, colony);

    this.emit(EcosystemEvent.COLONY_FORMED, { colonyId: colony.id, memberCount: memberIds.length });

    return colony;
  }

  /**
   * Form a symbiotic relationship between agents
   */
  formSymbiosis(
    sourceId: string,
    targetId: string,
    type: SymbiosisType,
    strength: number = 0.5
  ): EvolvableSymbiosis | null {
    const source = this.agents.get(sourceId);
    const target = this.agents.get(targetId);

    if (!source || !target) {
      return null;
    }

    try {
      const symbiosis = this.symbiosisMgr.formSymbiosis(source, target, type, strength);
      this.emit(EcosystemEvent.SYMBIOSIS_FORMED, {
        sourceId,
        targetId,
        type,
        strength: symbiosis.strength,
      });
      return symbiosis;
    } catch (error) {
      console.error('Failed to form symbiosis:', error);
      return null;
    }
  }

  /**
   * Break a symbiotic relationship
   */
  breakSymbiosis(sourceId: string, targetId: string): boolean {
    const result = this.symbiosisMgr.breakSymbiosis(sourceId, targetId);
    if (result) {
      this.emit(EcosystemEvent.SYMBIOSIS_BROKEN, { sourceId, targetId });
    }
    return result;
  }

  /**
   * Evolve a symbiotic relationship based on interaction outcome
   */
  evolveSymbiosis(
    sourceId: string,
    targetId: string,
    outcome: 'positive' | 'negative' | 'neutral',
    magnitude: number = 0.5
  ): EvolvableSymbiosis | null {
    return this.symbiosisMgr.evolveRelationship(sourceId, targetId, outcome, magnitude);
  }

  /**
   * Get all symbiotic relationships for an agent
   */
  getSymbioses(agentId: string): EvolvableSymbiosis[] {
    return this.symbiosisMgr.getRelationships(agentId);
  }

  /**
   * Get a specific symbiotic relationship
   */
  getSymbiosis(sourceId: string, targetId: string): EvolvableSymbiosis | null {
    return this.symbiosisMgr.getRelationship(sourceId, targetId);
  }

  /**
   * Get all symbiotic relationships in the ecosystem
   */
  getAllSymbioses(): EvolvableSymbiosis[] {
    return this.symbiosisMgr.getAllRelationships();
  }

  /**
   * Get symbiosis statistics
   */
  getSymbiosisStats() {
    return this.symbiosisMgr.getStats();
  }

  /**
   * Get ecosystem snapshot
   */
  getSnapshot(): EcosystemSnapshot {
    return {
      timestamp: this.simTime,
      agents: new Map(this.agents),
      resourceFlows: this.metabolism.getResourcePool().getAllFlows(),
      populations: this.getPopulations(),
      colonies: Array.from(this.colonies.values()),
      symbioses: this.symbiosisMgr.getAllRelationships(),
    };
  }

  /**
   * Get populations by taxonomy
   */
  getPopulations(): Map<AgentTaxonomy, PopulationDynamics> {
    const populations = new Map<AgentTaxonomy, PopulationDynamics>();

    for (const taxonomy of Object.values(AgentTaxonomy)) {
      const dynamics = this.population.getPopulationDynamics(taxonomy);
      if (dynamics) {
        populations.set(taxonomy, dynamics);
      }
    }

    return populations;
  }

  /**
   * Get agent by ID
   */
  getAgent(id: string): MicrobiomeAgent | undefined {
    return this.agents.get(id);
  }

  /**
   * Get agents by taxonomy
   */
  getAgentsByTaxonomy(taxonomy: AgentTaxonomy): MicrobiomeAgent[] {
    const ids = this.agentsByTaxonomy.get(taxonomy);
    if (!ids) return [];

    const agents: MicrobiomeAgent[] = [];
    for (const id of ids) {
      const agent = this.agents.get(id);
      if (agent && agent.lifecycle.isAlive) {
        agents.push(agent);
      }
    }

    return agents;
  }

  /**
   * Get ecosystem health
   */
  getHealth(): {
    totalAgents: number;
    diversity: number;
    dominantSpecies: AgentTaxonomy[];
    stability: number;
  } {
    const totalAgents = Array.from(this.agents.values()).filter(a => a.lifecycle.isAlive).length;

    let diversity = 0;
    const distribution = new Map<AgentTaxonomy, number>();

    for (const taxonomy of Object.values(AgentTaxonomy)) {
      const count = this.getAgentsByTaxonomy(taxonomy).length;
      distribution.set(taxonomy, count);
    }

    for (const p of distribution.values()) {
      if (p > 0 && totalAgents > 0) {
        const prob = p / totalAgents;
        diversity -= prob * Math.log(prob);
      }
    }

    let maxCount = 0;
    const dominant: AgentTaxonomy[] = [];
    for (const [taxonomy, count] of distribution.entries()) {
      if (count > maxCount) {
        maxCount = count;
        dominant.length = 0;
        dominant.push(taxonomy);
      } else if (count === maxCount) {
        dominant.push(taxonomy);
      }
    }

    // Stability based on population variance
    const isStable = this.population.isStable();

    return {
      totalAgents,
      diversity,
      dominantSpecies: dominant,
      stability: isStable ? 1 : 0,
    };
  }

  /**
   * Get immune system statistics
   */
  getImmuneStats() {
    return this.immuneSystem.getStats();
  }

  /**
   * Get immune system antibodies
   */
  getImmuneAntibodies() {
    return this.immuneSystem.getAntibodies();
  }

  /**
   * Get immune system memory
   */
  getImmuneMemory() {
    return this.immuneSystem.getMemory();
  }

  /**
   * Get quarantined agents
   */
  getQuarantinedAgents(): string[] {
    return this.immuneSystem.getQuarantined();
  }

  /**
   * Check if agent is quarantined
   */
  isAgentQuarantined(agentId: string): boolean {
    return this.immuneSystem.isQuarantined(agentId);
  }

  /**
   * Trigger manual immune scan
   */
  triggerImmuneScan() {
    const agentsArray = Array.from(this.agents.values());
    return this.immuneSystem.scan(agentsArray);
  }

  /**
   * Configure immune system
   */
  configureImmuneSystem(config: Partial<ImmuneSystemConfig>) {
    // For now, just log - full reconfiguration would require recreating the immune system
    console.log('Immune system configuration requested:', config);
  }

  /**
   * Execute gardener action
   */
  async executeAction(action: GardenerAction): Promise<boolean> {
    switch (action.type) {
      case 'introduce':
        const agent = action.params.agent as MicrobiomeAgent;
        return this.introduce(agent);

      case 'cull':
        if (action.targetId) {
          return this.cull(action.targetId);
        } else if (action.params.condition) {
          const count = this.cullWhere(action.params.condition);
          return count > 0;
        }
        return false;

      case 'fertilize':
        this.fertilize(action.params.resource as ResourceType, action.params.amount as number);
        return true;

      case 'restrict':
        this.restrict(action.params.resource as ResourceType, action.params.limit as number);
        return true;

      case 'graft':
        const members = action.params.members as string[];
        return this.graft(members) !== null;

      case 'export':
        const snapshot = this.getSnapshot();
        action.params.callback?.(snapshot);
        return true;

      default:
        return false;
    }
  }

  /**
   * Add event listener
   */
  on(event: EcosystemEvent, listener: EventListener): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)?.add(listener);
  }

  /**
   * Remove event listener
   */
  off(event: EcosystemEvent, listener: EventListener): void {
    this.listeners.get(event)?.delete(listener);
  }

  /**
   * Emit event
   */
  private emit(event: EcosystemEvent, data: any): void {
    const listeners = this.listeners.get(event);
    if (listeners) {
      for (const listener of listeners) {
        try {
          listener(event, data);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      }
    }
  }

  /**
   * Update population dynamics based on actual agent counts
   */
  private updatePopulationDynamics(): void {
    for (const taxonomy of Object.values(AgentTaxonomy)) {
      const count = this.getAgentsByTaxonomy(taxonomy).length;
      this.population.setPopulation(taxonomy, count);
    }

    // Update resource flows for population
    const flows = this.metabolism.getResourcePool().getAllFlows();
    for (const [resource, flow] of flows.entries()) {
      this.population.setResourceFlow(resource, flow);
    }
  }

  /**
   * Process evolution step
   */
  private async processEvolution(): Promise<void> {
    for (const agent of this.agents.values()) {
      if (!agent.lifecycle.isAlive) continue;

      // Evaluate fitness
      const fitness = agent.evaluateFitness();

      // High fitness agents get to reproduce
      if (fitness.overall > this.config.selectionPressure) {
        try {
          const child = await agent.reproduce(this.config.mutationConfig);
          this.introduce(child);
          this.emit(EcosystemEvent.AGENT_REPRODUCED, {
            parentId: agent.id,
            childId: child.id,
            fitness,
          });
        } catch (error) {
          // Reproduction failed
        }
      }

      // Low fitness agents die
      if (fitness.overall < 0.2) {
        this.cull(agent.id);
      }
    }
  }

  /**
   * Remove dead agents
   */
  private removeDeadAgents(): void {
    for (const [id, agent] of this.agents.entries()) {
      if (!agent.lifecycle.isAlive) {
        // Clean up symbiotic relationships
        const symbioses = this.symbiosisMgr.getRelationships(id);
        for (const symbiosis of symbioses) {
          this.breakSymbiosis(symbiosis.sourceId, symbiosis.targetId);
        }

        this.agents.delete(id);
        this.agentsByTaxonomy.get(agent.taxonomy)?.delete(id);
        this.metabolism.unregisterChamber(id);
      }
    }
  }

  /**
   * Process immune system scan and response
   */
  private async processImmuneSystem(): Promise<void> {
    await this.performanceMonitor.recordOperationAsync('immune_system_process', async () => {
      // Release quarantined agents if quarantine period expired
      this.immuneSystem.releaseQuarantined(this.agents);

      // Scan for threats
      const agentsArray = Array.from(this.agents.values());
      const threats = await this.performanceMonitor.recordOperationAsync('immune_scan', async () => {
        return this.immuneSystem.scan(agentsArray);
      });

      // Emit threat detection events
      for (const threat of threats) {
        this.emit(EcosystemEvent.THREAT_DETECTED, threat);
      }

      // Respond to threats
      const result = this.immuneSystem.respond(this.agents, threats);

      // Emit response events
      for (const [agentId, agent] of this.agents.entries()) {
        if (!agent.lifecycle.isAlive) {
          this.emit(EcosystemEvent.AGENT_TERMINATED, { agentId });
          this.emit(EcosystemEvent.THREAT_NEUTRALIZED, { agentId });
        } else if ((agent as any).quarantined) {
          this.emit(EcosystemEvent.AGENT_QUARANTINED, { agentId });
        }
      }

      // Update statistics
      if (result.neutralized > 0) {
        this.emit(EcosystemEvent.THREAT_NEUTRALIZED, result);
      }
    });
  }

  /**
   * Manage colony formation and dissolution
   */
  private manageColonies(): void {
    // Update colony stability
    for (const colony of this.colonies.values()) {
      let aliveMembers = 0;
      for (const memberId of colony.members) {
        const agent = this.agents.get(memberId);
        if (agent && agent.lifecycle.isAlive) {
          aliveMembers++;
        }
      }

      // Dissolve colony if too few members
      if (aliveMembers < 2) {
        this.colonies.delete(colony.id);
        this.emit(EcosystemEvent.COLONY_DISSOLVED, { colonyId: colony.id });
      } else {
        // Increase stability over time
        colony.stability = Math.min(1.0, colony.stability + 0.001);
      }
    }
  }

  /**
   * Enforce carrying capacity
   */
  private enforceCarryingCapacity(): void {
    const totalAgents = this.agents.size;
    if (totalAgents <= this.config.maxAgents) return;

    // Remove lowest fitness agents first
    const agentsByFitness = Array.from(this.agents.values())
      .map(agent => ({ agent, fitness: agent.evaluateFitness().overall }))
      .sort((a, b) => a.fitness - b.fitness);

    const toRemove = totalAgents - this.config.maxAgents;
    for (let i = 0; i < toRemove; i++) {
      this.cull(agentsByFitness[i].agent.id);
    }
  }

  /**
   * Export state
   */
  exportState(): any {
    return {
      simTime: this.simTime,
      agents: Array.from(this.agents.entries()),
      colonies: Array.from(this.colonies.entries()),
      population: this.population.exportState(),
      config: this.config,
    };
  }

  /**
   * Import state
   */
  importState(state: any): void {
    this.simTime = state.simTime || 0;
    this.agents = new Map(state.agents);
    this.colonies = new Map(
      state.colonies.map(([id, colony]: [string, ColonyStructure]) => [id, colony])
    );
    this.population.importState(state.population);
    if (state.config) {
      this.config = { ...this.config, ...state.config };
    }
  }

  /**
   * Get performance metrics summary
   */
  getPerformanceMetrics() {
    return this.performanceMonitor.getSummary();
  }

  /**
   * Get performance alerts
   */
  getPerformanceAlerts() {
    return this.performanceMonitor.getAlerts();
  }

  /**
   * Export performance metrics in specified format
   */
  exportPerformanceMetrics(format: 'prometheus' | 'json' | 'influx' = 'json') {
    return this.performanceMonitor.exportMetrics(format);
  }

  /**
   * Detect performance anomalies
   */
  detectPerformanceAnomalies() {
    return this.performanceMonitor.detectAnomalies();
  }

  /**
   * Get performance monitor instance for advanced usage
   */
  getPerformanceMonitor(): PerformanceMonitor {
    return this.performanceMonitor;
  }
}

/**
 * Create a digital terrarium
 */
export function createTerrarium(config?: Partial<EcosystemConfig>): DigitalTerrarium {
  return new DigitalTerrarium(config);
}
