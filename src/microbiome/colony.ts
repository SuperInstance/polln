/**
 * POLLN Microbiome - Colony System
 *
 * Advanced colony formation, optimization, and management.
 * Colonies are biofilm-like structures where agents self-organize
 * into efficient communities through co-evolution and specialization.
 *
 * @module microbiome/colony
 */

import { v4 as uuidv4 } from 'uuid';
import {
  MicrobiomeAgent,
  ColonyStructure,
  ResourceType,
  Symbiosis,
  SymbiosisType,
} from './types.js';

/**
 * Colony lifecycle states
 */
export enum ColonyState {
  /** Colony is forming */
  FORMING = 'forming',
  /** Colony is active and stable */
  ACTIVE = 'active',
  /** Colony is specializing */
  SPECIALIZING = 'specializing',
  /** Colony is declining */
  DECLINING = 'declining',
  /** Colony is dissolving */
  DISSOLVING = 'dissolving',
}

/**
 * Colony proposal - suggested colony formation
 */
export interface ColonyProposal {
  /** Proposed members */
  members: MicrobiomeAgent[];
  /** Compatibility score (0-1) */
  compatibility: number;
  /** Expected efficiency gain (0-1) */
  expectedEfficiency: number;
  /** Formation rationale */
  rationale: string;
  /** Symbiotic relationships between members */
  symbioses: Symbiosis[];
}

/**
 * Task for colony specialization
 */
export interface Task {
  /** Task ID */
  id: string;
  /** Task type */
  type: string;
  /** Required resources */
  requiredResources: ResourceType[];
  /** Task complexity (0-1) */
  complexity: number;
  /** Priority (0-1) */
  priority: number;
}

/**
 * Colony specialization configuration
 */
export interface Specialization {
  /** Specialization ID */
  id: string;
  /** Task type specialized for */
  taskType: string;
  /** Member specializations */
  memberSpecializations: Map<string, string>;
  /** Efficiency gain (0-1) */
  efficiencyGain: number;
  /** Formation time */
  formationTime: number;
}

/**
 * Extended colony structure with lifecycle state
 */
export interface Colony extends ColonyStructure {
  /** Current lifecycle state */
  state: ColonyState;
  /** Age in milliseconds */
  age: number;
  /** Total tasks completed */
  tasksCompleted: number;
  /** Success rate (0-1) */
  successRate: number;
  /** Specializations */
  specializations: Specialization[];
  /** Member roles (agentId -> role) */
  roles: Map<string, string>;
}

/**
 * Colony formation options
 */
export interface ColonyFormationOptions {
  /** Minimum colony size */
  minSize?: number;
  /** Maximum colony size */
  maxSize?: number;
  /** Minimum compatibility threshold */
  minCompatibility?: number;
  /** Enable direct channels */
  enableDirectChannels?: boolean;
  /** Enable specialization */
  enableSpecialization?: boolean;
}

/**
 * Colony statistics
 */
export interface ColonyStats {
  /** Total colonies */
  totalColonies: number;
  /** Colonies by state */
  coloniesByState: Map<ColonyState, number>;
  /** Average colony size */
  averageSize: number;
  /** Average stability */
  averageStability: number;
  /** Average co-evolution bonus */
  averageCoEvolutionBonus: number;
}

/**
 * Colony System - Manages colony lifecycle and optimization
 */
export class ColonySystem {
  /** Active colonies */
  private colonies: Map<string, Colony>;
  /** Colony proposals cache */
  private proposals: Map<string, ColonyProposal[]>;
  /** Performance history for learning */
  private performanceHistory: Map<string, number[]>;
  /** Configuration */
  private config: Required<ColonyFormationOptions>;
  /** Current simulation time */
  private simTime: number;

  constructor(config: ColonyFormationOptions = {}) {
    this.colonies = new Map();
    this.proposals = new Map();
    this.performanceHistory = new Map();
    this.simTime = 0;

    this.config = {
      minSize: config.minSize ?? 2,
      maxSize: config.maxSize ?? 100,
      minCompatibility: config.minCompatibility ?? 0.6,
      enableDirectChannels: config.enableDirectChannels ?? true,
      enableSpecialization: config.enableSpecialization ?? true,
    };
  }

  /**
   * Discover potential colonies from agent interactions
   * Finds combinations of agents that work well together
   */
  discoverColonies(agents: MicrobiomeAgent[]): ColonyProposal[] {
    const proposals: ColonyProposal[] = [];

    // Filter out dead agents
    const liveAgents = agents.filter(a => a.lifecycle.isAlive);
    if (liveAgents.length < this.config.minSize) {
      return proposals;
    }

    // Analyze all possible combinations (up to a limit for performance)
    const maxCombos = Math.min(100, this.calculateCombos(liveAgents.length));

    for (let i = 0; i < maxCombos; i++) {
      const subsetSize = this.getRandomInt(
        this.config.minSize,
        Math.min(this.config.maxSize, liveAgents.length)
      );

      const subset = this.selectRandomSubset(liveAgents, subsetSize);
      if (subset.length < this.config.minSize) continue;

      const proposal = this.evaluateColonyProposal(subset);
      if (proposal.compatibility >= this.config.minCompatibility) {
        proposals.push(proposal);
      }
    }

    // Sort by compatibility and efficiency
    proposals.sort((a, b) => {
      const scoreA = a.compatibility * 0.6 + a.expectedEfficiency * 0.4;
      const scoreB = b.compatibility * 0.6 + b.expectedEfficiency * 0.4;
      return scoreB - scoreA;
    });

    // Cache top proposals
    if (proposals.length > 0) {
      const cacheKey = this.generateCacheKey(liveAgents);
      this.proposals.set(cacheKey, proposals.slice(0, 10));
    }

    return proposals;
  }

  /**
   * Form a colony from a set of agents
   */
  formColony(members: MicrobiomeAgent[]): Colony | null {
    if (members.length < this.config.minSize || members.length > this.config.maxSize) {
      return null;
    }

    // Verify all agents are alive
    for (const agent of members) {
      if (!agent.lifecycle.isAlive) {
        return null;
      }
    }

    // Check for duplicate agents
    const uniqueMembers = new Set(members.map(m => m.id));
    if (uniqueMembers.size !== members.length) {
      return null;
    }

    // Evaluate compatibility
    const proposal = this.evaluateColonyProposal(members);
    if (proposal.compatibility < this.config.minCompatibility) {
      return null;
    }

    const colony: Colony = {
      id: uuidv4(),
      members: members.map(m => m.id),
      communicationChannels: new Map(),
      formationTime: this.simTime,
      stability: 0.4, // Start with moderate stability for faster transition
      coEvolutionBonus: proposal.expectedEfficiency,
      state: ColonyState.FORMING,
      age: 0,
      tasksCompleted: 0,
      successRate: 0.5,
      specializations: [],
      roles: new Map(),
    };

    // Establish direct communication channels
    if (this.config.enableDirectChannels) {
      this.establishDirectChannels(colony, members);
    }

    // Initialize roles based on agent types
    this.initializeRoles(colony, members);

    this.colonies.set(colony.id, colony);

    return colony;
  }

  /**
   * Dissolve a colony
   */
  dissolveColony(colonyId: string): boolean {
    const colony = this.colonies.get(colonyId);
    if (!colony) return false;

    colony.state = ColonyState.DISSOLVING;

    // Clear communication channels
    colony.communicationChannels.clear();

    // Remove from active colonies
    this.colonies.delete(colonyId);

    // Archive performance history
    const history = this.performanceHistory.get(colonyId);
    if (history) {
      // Keep for potential future learning
    }

    return true;
  }

  /**
   * Update colony lifecycle state
   */
  updateColony(colony: Colony, dt: number = 100): ColonyState {
    colony.age += dt;

    // Check member survival
    const aliveMembers = this.countAliveMembers(colony);
    const memberRatio = aliveMembers / colony.members.length;

    // Update stability based on age and success
    // Stability grows faster initially to allow reasonable transition times
    const stabilityBonus = Math.min(0.02, colony.age / 50000);
    colony.stability = Math.min(1.0, colony.stability + stabilityBonus);

    // State transitions
    switch (colony.state) {
      case ColonyState.FORMING:
        if (colony.age > 1000 && colony.stability > 0.5) {
          colony.state = ColonyState.ACTIVE;
        }
        break;

      case ColonyState.ACTIVE:
        // Check if should specialize
        if (this.config.enableSpecialization && colony.tasksCompleted > 10) {
          colony.state = ColonyState.SPECIALIZING;
        }
        // Check if declining
        if (memberRatio < 0.5 || colony.successRate < 0.3) {
          colony.state = ColonyState.DECLINING;
        }
        break;

      case ColonyState.SPECIALIZING:
        // After specialization, return to active
        if (colony.specializations.length > 0) {
          colony.state = ColonyState.ACTIVE;
        }
        break;

      case ColonyState.DECLINING:
        // Dissolve if too few members or very low success rate
        if (memberRatio < 0.3 || colony.successRate < 0.1) {
          colony.state = ColonyState.DISSOLVING;
        }
        // Can recover
        if (memberRatio > 0.7 && colony.successRate > 0.5) {
          colony.state = ColonyState.ACTIVE;
        }
        break;

      case ColonyState.DISSOLVING:
        // Colony will be removed
        break;
    }

    // Co-evolution bonus increases with stability and age
    const coEvolutionFactor = colony.stability * Math.min(1.0, colony.age / 10000);
    colony.coEvolutionBonus = Math.min(0.95, 0.1 + coEvolutionFactor * 0.85);

    return colony.state;
  }

  /**
   * Establish direct A2A communication channels
   * Bypasses standard A2A overhead for colony members
   */
  establishDirectChannels(colony: Colony, members: MicrobiomeAgent[]): void {
    colony.communicationChannels.clear();

    // Create bidirectional channels between all members
    for (let i = 0; i < members.length; i++) {
      for (let j = i + 1; j < members.length; j++) {
        const agent1 = members[i];
        const agent2 = members[j];

        // Check for metabolic compatibility
        const compatibility = this.calculateMetabolicCompatibility(agent1, agent2);

        if (compatibility > 0.5) {
          colony.communicationChannels.set(agent1.id, agent2.id);
          colony.communicationChannels.set(agent2.id, agent1.id);
        }
      }
    }
  }

  /**
   * Specialize a colony for a specific task
   * Members develop specialized roles for improved efficiency
   */
  specialize(colony: Colony, task: Task): Specialization | null {
    if (!this.config.enableSpecialization) {
      return null;
    }

    // Check if already specialized for this task
    const existing = colony.specializations.find(s => s.taskType === task.type);
    if (existing) {
      return existing;
    }

    // Assign roles based on agent capabilities
    const memberSpecializations = new Map<string, string>();
    const memberIds = colony.members;

    for (const memberId of memberIds) {
      const role = this.determineRole(memberId, task);
      memberSpecializations.set(memberId, role);
    }

    // Calculate efficiency gain
    const baseEfficiency = 0.1;
    const specializationBonus = Math.min(0.4, memberIds.length * 0.05);
    const stabilityBonus = colony.stability * 0.3;
    const efficiencyGain = baseEfficiency + specializationBonus + stabilityBonus;

    const specialization: Specialization = {
      id: uuidv4(),
      taskType: task.type,
      memberSpecializations,
      efficiencyGain,
      formationTime: this.simTime,
    };

    colony.specializations.push(specialization);
    colony.roles = new Map([...colony.roles, ...memberSpecializations]);

    // Update co-evolution bonus
    colony.coEvolutionBonus = Math.min(0.95, colony.coEvolutionBonus + efficiencyGain * 0.5);

    return specialization;
  }

  /**
   * Record task completion for a colony
   */
  recordTaskCompletion(colonyId: string, success: boolean): void {
    const colony = this.colonies.get(colonyId);
    if (!colony) return;

    colony.tasksCompleted++;

    // Update success rate with exponential moving average
    const alpha = 0.1;
    const newRate = success ? 1.0 : 0.0;
    colony.successRate = alpha * newRate + (1 - alpha) * colony.successRate;

    // Record in performance history
    if (!this.performanceHistory.has(colonyId)) {
      this.performanceHistory.set(colonyId, []);
    }
    this.performanceHistory.get(colonyId)?.push(success ? 1.0 : 0.0);

    // Keep only last 100 entries
    const history = this.performanceHistory.get(colonyId);
    if (history && history.length > 100) {
      history.shift();
    }
  }

  /**
   * Get colony by ID
   */
  getColony(colonyId: string): Colony | undefined {
    return this.colonies.get(colonyId);
  }

  /**
   * Get all active colonies
   */
  getAllColonies(): Colony[] {
    return Array.from(this.colonies.values());
  }

  /**
   * Get colonies by state
   */
  getColoniesByState(state: ColonyState): Colony[] {
    return Array.from(this.colonies.values()).filter(c => c.state === state);
  }

  /**
   * Get colony statistics
   */
  getStats(): ColonyStats {
    const colonies = Array.from(this.colonies.values());

    const coloniesByState = new Map<ColonyState, number>();
    for (const state of Object.values(ColonyState)) {
      coloniesByState.set(state, colonies.filter(c => c.state === state).length);
    }

    const averageSize = colonies.length > 0
      ? colonies.reduce((sum, c) => sum + c.members.length, 0) / colonies.length
      : 0;

    const averageStability = colonies.length > 0
      ? colonies.reduce((sum, c) => sum + c.stability, 0) / colonies.length
      : 0;

    const averageCoEvolutionBonus = colonies.length > 0
      ? colonies.reduce((sum, c) => sum + c.coEvolutionBonus, 0) / colonies.length
      : 0;

    return {
      totalColonies: colonies.length,
      coloniesByState,
      averageSize,
      averageStability,
      averageCoEvolutionBonus,
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
   * Clear all colonies
   */
  clear(): void {
    this.colonies.clear();
    this.proposals.clear();
    this.performanceHistory.clear();
  }

  /**
   * Export colony system state
   */
  exportState(): any {
    return {
      colonies: Array.from(this.colonies.entries()),
      proposals: Array.from(this.proposals.entries()),
      performanceHistory: Array.from(this.performanceHistory.entries()),
      config: this.config,
      simTime: this.simTime,
    };
  }

  /**
   * Import colony system state
   */
  importState(state: any): void {
    this.colonies = new Map(state.colonies || []);
    this.proposals = new Map(state.proposals || []);
    this.performanceHistory = new Map(state.performanceHistory || []);
    this.simTime = state.simTime || 0;
    if (state.config) {
      this.config = { ...this.config, ...state.config };
    }
  }

  /**
   * Evaluate a colony proposal
   */
  private evaluateColonyProposal(members: MicrobiomeAgent[]): ColonyProposal {
    // Calculate metabolic compatibility
    let totalCompatibility = 0;
    let pairCount = 0;

    for (let i = 0; i < members.length; i++) {
      for (let j = i + 1; j < members.length; j++) {
        const compatibility = this.calculateMetabolicCompatibility(members[i], members[j]);
        totalCompatibility += compatibility;
        pairCount++;
      }
    }

    const avgCompatibility = pairCount > 0 ? totalCompatibility / pairCount : 0;

    // Calculate expected efficiency
    const diversityFactor = this.calculateDiversity(members);
    const sizeFactor = Math.min(1.0, members.length / 20);
    const expectedEfficiency = avgCompatibility * 0.6 + diversityFactor * 0.2 + sizeFactor * 0.2;

    // Generate symbioses
    const symbioses = this.generateSymbioses(members);

    // Generate rationale
    const rationale = this.generateRationale(members, avgCompatibility, expectedEfficiency);

    return {
      members,
      compatibility: avgCompatibility,
      expectedEfficiency,
      rationale,
      symbioses,
    };
  }

  /**
   * Calculate metabolic compatibility between two agents
   */
  private calculateMetabolicCompatibility(agent1: MicrobiomeAgent, agent2: MicrobiomeAgent): number {
    // Check for complementary input/output
    let compatibility = 0;

    for (const output of agent1.metabolism.outputs) {
      if (agent2.metabolism.inputs.includes(output)) {
        compatibility += 0.3;
      }
    }

    for (const output of agent2.metabolism.outputs) {
      if (agent1.metabolism.inputs.includes(output)) {
        compatibility += 0.3;
      }
    }

    // Similar processing rates work well together
    const rateSimilarity = 1 - Math.abs(agent1.metabolism.processingRate - agent2.metabolism.processingRate);
    compatibility += rateSimilarity * 0.2;

    // Efficiency alignment
    const efficiencyAlignment = 1 - Math.abs(agent1.metabolism.efficiency - agent2.metabolism.efficiency);
    compatibility += efficiencyAlignment * 0.2;

    return Math.min(1.0, compatibility);
  }

  /**
   * Calculate diversity of agent types in colony
   */
  private calculateDiversity(members: MicrobiomeAgent[]): number {
    const types = new Set(members.map(m => m.taxonomy));
    const typeCount = types.size;

    // Optimal diversity is 3-5 types
    if (typeCount < 2) return 0.2;
    if (typeCount <= 5) return 1.0;
    return Math.max(0.5, 1.0 - (typeCount - 5) * 0.1);
  }

  /**
   * Generate symbiotic relationships between members
   */
  private generateSymbioses(members: MicrobiomeAgent[]): Symbiosis[] {
    const symbioses: Symbiosis[] = [];

    for (let i = 0; i < members.length; i++) {
      for (let j = i + 1; j < members.length; j++) {
        const agent1 = members[i];
        const agent2 = members[j];

        const compatibility = this.calculateMetabolicCompatibility(agent1, agent2);

        let type: SymbiosisType;
        if (compatibility > 0.8) {
          type = SymbiosisType.MUTUALISM;
        } else if (compatibility > 0.5) {
          type = SymbiosisType.COMMENSALISM;
        } else {
          continue; // No symbiosis
        }

        symbioses.push({
          sourceId: agent1.id,
          targetId: agent2.id,
          type,
          strength: compatibility,
          benefitToSource: compatibility * 0.8,
          benefitToTarget: compatibility * 0.8,
        });
      }
    }

    return symbioses;
  }

  /**
   * Generate rationale for colony formation
   */
  private generateRationale(
    members: MicrobiomeAgent[],
    compatibility: number,
    efficiency: number
  ): string {
    const types = members.map(m => m.taxonomy);
    const uniqueTypes = new Set(types);

    let rationale = `Colony of ${members.length} agents`;

    if (uniqueTypes.size > 1) {
      rationale += ` across ${uniqueTypes.size} types`;
    }

    rationale += `. Compatibility: ${(compatibility * 100).toFixed(0)}%, `;

    if (efficiency > 0.7) {
      rationale += 'high efficiency expected from strong metabolic synergy';
    } else if (efficiency > 0.5) {
      rationale += 'moderate efficiency expected from complementary inputs/outputs';
    } else {
      rationale += 'low efficiency expected, limited synergy detected';
    }

    return rationale;
  }

  /**
   * Initialize roles for colony members
   */
  private initializeRoles(colony: Colony, members: MicrobiomeAgent[]): void {
    for (const member of members) {
      let role = 'worker';

      switch (member.taxonomy) {
        case 'bacteria':
          role = 'processor';
          break;
        case 'virus':
          role = 'specialist';
          break;
        case 'explorer':
          role = 'scout';
          break;
        case 'macrophage':
          role = 'defender';
          break;
        default:
          role = 'contributor';
      }

      colony.roles.set(member.id, role);
    }
  }

  /**
   * Determine role for a member based on task
   */
  private determineRole(memberId: string, task: Task): string {
    // This is a simplified version - in practice would analyze
    // agent capabilities vs task requirements
    const roles = ['executor', 'validator', 'optimizer', 'monitor'];
    return roles[Math.floor(Math.random() * roles.length)];
  }

  /**
   * Count alive members in colony
   */
  private countAliveMembers(colony: Colony): number {
    // This is a simplified check - in practice would query actual agent states
    // For now, assume all members are alive unless marked otherwise
    return colony.members.length;
  }

  /**
   * Calculate number of combinations
   */
  private calculateCombos(n: number): number {
    return Math.floor(n * (n - 1) / 2);
  }

  /**
   * Get random integer in range
   */
  private getRandomInt(min: number, max: number): number {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  /**
   * Select random subset from array
   */
  private selectRandomSubset<T>(array: T[], size: number): T[] {
    const shuffled = [...array].sort(() => Math.random() - 0.5);
    return shuffled.slice(0, size);
  }

  /**
   * Generate cache key for proposals
   */
  private generateCacheKey(agents: MicrobiomeAgent[]): string {
    const ids = agents.map(a => a.id).sort().join(',');
    return `${ids}:${agents.length}`;
  }
}

/**
 * Create a colony system
 */
export function createColonySystem(config?: ColonyFormationOptions): ColonySystem {
  return new ColonySystem(config);
}
