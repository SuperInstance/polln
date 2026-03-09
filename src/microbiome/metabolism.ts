/**
 * POLLN Microbiome - Metabolism System
 *
 * Manages the flow of resources through agents.
 * Input → Processing → Output
 *
 * @module microbiome/metabolism
 */

import { ResourceType, ResourceFlow, MetabolicProfile } from './types.js';

/**
 * Resource pool - tracks available resources
 */
export class ResourcePool {
  private resources: Map<ResourceType, ResourceFlow>;

  constructor() {
    this.resources = new Map();

    // Initialize all resource types
    for (const type of Object.values(ResourceType)) {
      this.resources.set(type, {
        resource: type,
        flowRate: 0,
        available: 0,
        capacity: Number.MAX_SAFE_INTEGER,
      });
    }
  }

  /**
   * Add resources to the pool
   */
  add(resource: ResourceType, amount: number): void {
    const flow = this.resources.get(resource);
    if (flow) {
      flow.available += amount;
      flow.flowRate += amount;
    }
  }

  /**
   * Consume resources from the pool
   */
  consume(resource: ResourceType, amount: number): number {
    const flow = this.resources.get(resource);
    if (!flow) return 0;

    const consumed = Math.min(amount, flow.available);
    flow.available -= consumed;
    return consumed;
  }

  /**
   * Get available amount of a resource
   */
  getAvailable(resource: ResourceType): number {
    return this.resources.get(resource)?.available || 0;
  }

  /**
   * Get flow rate of a resource
   */
  getFlowRate(resource: ResourceType): number {
    return this.resources.get(resource)?.flowRate || 0;
  }

  /**
   * Set capacity for a resource
   */
  setCapacity(resource: ResourceType, capacity: number): void {
    const flow = this.resources.get(resource);
    if (flow) {
      flow.capacity = capacity;
    }
  }

  /**
   * Get all resource flows
   */
  getAllFlows(): Map<ResourceType, ResourceFlow> {
    return new Map(this.resources);
  }

  /**
   * Decay flow rates (call each tick)
   */
  decayFlowRates(decayFactor: number = 0.95): void {
    for (const flow of this.resources.values()) {
      flow.flowRate *= decayFactor;
    }
  }

  /**
   * Get total resource value (weighted sum)
   */
  getTotalValue(): number {
    let total = 0;
    for (const flow of this.resources.values()) {
      total += flow.available;
    }
    return total;
  }
}

/**
 * Metabolic chamber - processes resources for a single agent
 */
export class MetabolicChamber {
  private profile: MetabolicProfile;
  private inputBuffer: Map<ResourceType, number>;
  private outputBuffer: Map<ResourceType, number>;
  private processingQueue: Array<{
    inputs: Map<ResourceType, number>;
    timestamp: number;
  }> = [];

  constructor(profile: MetabolicProfile) {
    this.profile = profile;
    this.inputBuffer = new Map();
    this.outputBuffer = new Map();
  }

  /**
   * Feed resources to the chamber
   */
  feed(resources: Map<ResourceType, number>): void {
    for (const [resource, amount] of resources.entries()) {
      // Only accept resources this agent can metabolize
      if (this.profile.inputs.includes(resource)) {
        const current = this.inputBuffer.get(resource) || 0;
        this.inputBuffer.set(resource, current + amount);
      }
    }
  }

  /**
   * Process resources (one tick)
   */
  process(deltaMs: number): Map<ResourceType, number> {
    const outputs = new Map<ResourceType, number>();

    // Calculate processing capacity for this tick
    const processingCapacity = (this.profile.processingRate * deltaMs) / 1000;

    // Process each input
    for (const input of this.profile.inputs) {
      const available = this.inputBuffer.get(input) || 0;
      if (available <= 0) continue;

      // Process amount limited by capacity and efficiency
      const toProcess = Math.min(available, processingCapacity);
      const actualProcessed = toProcess * this.profile.efficiency;

      // Remove from input buffer
      this.inputBuffer.set(input, available - toProcess);

      // Add to output buffer (transformed)
      // For simplicity, 1 unit of input = 1 unit of output (after efficiency)
      // In real system, this would be more complex transformation
      for (const outputType of this.profile.outputs) {
        const currentOutput = this.outputBuffer.get(outputType) || 0;
        this.outputBuffer.set(outputType, currentOutput + actualProcessed / this.profile.outputs.length);
      }
    }

    return outputs;
  }

  /**
   * Extract output from chamber
   */
  extract(): Map<ResourceType, number> {
    const outputs = new Map(this.outputBuffer);
    this.outputBuffer.clear();
    return outputs;
  }

  /**
   * Get input buffer levels
   */
  getInputLevels(): Map<ResourceType, number> {
    return new Map(this.inputBuffer);
  }

  /**
   * Get output buffer levels
   */
  getOutputLevels(): Map<ResourceType, number> {
    return new Map(this.outputBuffer);
  }

  /**
   * Get metabolic profile
   */
  getProfile(): MetabolicProfile {
    return this.profile;
  }

  /**
   * Check if chamber has enough inputs to process
   */
  canProcess(): boolean {
    for (const input of this.profile.inputs) {
      if ((this.inputBuffer.get(input) || 0) > 0) {
        return true;
      }
    }
    return false;
  }

  /**
   * Get processing utilization (0-1)
   */
  getUtilization(): number {
    let totalInput = 0;
    for (const amount of this.inputBuffer.values()) {
      totalInput += amount;
    }
    // Utilization based on buffer vs processing rate
    return Math.min(1, totalInput / this.profile.processingRate);
  }
}

/**
 * Metabolism manager - coordinates all metabolic chambers
 */
export class MetabolismManager {
  private resourcePool: ResourcePool;
  private chambers: Map<string, MetabolicChamber>;
  private tickRate: number; // milliseconds per tick

  constructor(tickRate: number = 100) {
    this.resourcePool = new ResourcePool();
    this.chambers = new Map();
    this.tickRate = tickRate;
  }

  /**
   * Register a metabolic chamber for an agent
   */
  registerChamber(agentId: string, profile: MetabolicProfile): void {
    this.chambers.set(agentId, new MetabolicChamber(profile));
  }

  /**
   * Unregister a chamber
   */
  unregisterChamber(agentId: string): void {
    this.chambers.delete(agentId);
  }

  /**
   * Feed resources to an agent's chamber
   */
  feed(agentId: string, resources: Map<ResourceType, number>): boolean {
    const chamber = this.chambers.get(agentId);
    if (!chamber) return false;

    chamber.feed(resources);
    return true;
  }

  /**
   * Process one tick
   */
  async processTick(): Promise<Map<string, Map<ResourceType, number>>> {
    const results = new Map<string, Map<ResourceType, number>>();

    // Process each chamber
    for (const [agentId, chamber] of this.chambers.entries()) {
      if (chamber.canProcess()) {
        const outputs = chamber.process(this.tickRate);
        results.set(agentId, outputs);
      }
    }

    // Decay flow rates
    this.resourcePool.decayFlowRates();

    return results;
  }

  /**
   * Extract outputs from all chambers
   */
  extractAll(): Map<string, Map<ResourceType, number>> {
    const outputs = new Map<string, Map<ResourceType, number>>();

    for (const [agentId, chamber] of this.chambers.entries()) {
      const chamberOutput = chamber.extract();
      if (chamberOutput.size > 0) {
        outputs.set(agentId, chamberOutput);
      }
    }

    return outputs;
  }

  /**
   * Add resources to the global pool
   */
  addResources(resource: ResourceType, amount: number): void {
    this.resourcePool.add(resource, amount);
  }

  /**
   * Get resource pool
   */
  getResourcePool(): ResourcePool {
    return this.resourcePool;
  }

  /**
   * Get chamber for an agent
   */
  getChamber(agentId: string): MetabolicChamber | undefined {
    return this.chambers.get(agentId);
  }

  /**
   * Get system-wide statistics
   */
  getStats() {
    let totalInputBuffer = 0;
    let totalOutputBuffer = 0;
    let activeChambers = 0;

    for (const chamber of this.chambers.values()) {
      for (const amount of chamber.getInputLevels().values()) {
        totalInputBuffer += amount;
      }
      for (const amount of chamber.getOutputLevels().values()) {
        totalOutputBuffer += amount;
      }
      if (chamber.canProcess()) {
        activeChambers++;
      }
    }

    return {
      totalChambers: this.chambers.size,
      activeChambers,
      totalInputBuffer,
      totalOutputBuffer,
      totalResources: this.resourcePool.getTotalValue(),
      averageUtilization: activeChambers > 0
        ? Array.from(this.chambers.values())
            .reduce((sum, c) => sum + c.getUtilization(), 0) / activeChambers
        : 0,
    };
  }
}

/**
 * Metabolic pathway - chain of agents processing resources
 */
export class MetabolicPathway {
  private agentIds: string[];
  private metabolismManager: MetabolismManager;
  private throughput: number = 0;
  private bottleneck: string | null = null;

  constructor(agentIds: string[], metabolismManager: MetabolismManager) {
    this.agentIds = agentIds;
    this.metabolismManager = metabolismManager;
  }

  /**
   * Process resources through the pathway
   */
  async process(inputResources: Map<ResourceType, number>): Promise<Map<ResourceType, number>> {
    let currentResources = inputResources;

    for (const agentId of this.agentIds) {
      // Feed to current agent
      this.metabolismManager.feed(agentId, currentResources);

      // Process tick
      await this.metabolismManager.processTick();

      // Extract output
      const outputs = this.metabolismManager.extractAll().get(agentId);
      if (outputs) {
        currentResources = outputs;
      } else {
        // Agent produced no output - bottleneck detected
        this.bottleneck = agentId;
        return new Map();
      }
    }

    this.bottleneck = null;
    this.throughput += inputResources.size;
    return currentResources;
  }

  /**
   * Get pathway statistics
   */
  getStats() {
    return {
      agentIds: this.agentIds,
      length: this.agentIds.length,
      throughput: this.throughput,
      bottleneck: this.bottleneck,
    };
  }
}

/**
 * Create a metabolic pathway from agent profiles
 */
export function createPathway(
  metabolismManager: MetabolismManager,
  profiles: Array<{ id: string; profile: MetabolicProfile }>
): MetabolicPathway {
  // Register all chambers
  for (const { id, profile } of profiles) {
    metabolismManager.registerChamber(id, profile);
  }

  const agentIds = profiles.map(p => p.id);
  return new MetabolicPathway(agentIds, metabolismManager);
}
