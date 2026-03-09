/**
 * POLLN Microbiome Bridge
 *
 * Bidirectional bridge between Microbiome and Core POLLN systems.
 * Enables seamless agent conversion, message translation, and resource sharing.
 *
 * @module microbiome/bridge
 */

import { v4 as uuidv4 } from 'uuid';
import type {
  BaseAgent,
  A2APackage as CoreA2APackage,
  TileCategory,
  PollenGrain,
} from '../core/index.js';
import type {
  MicrobiomeAgent,
  MetabolicProfile,
  BacteriaAgent,
  VirusAgent,
  LifecycleState,
  ColonyStructure,
} from './types.js';
import { AgentTaxonomy, ResourceType } from './types.js';

// ============================================================================
// GOAL TYPES (Core System)
// ============================================================================

/**
 * Goal - core system objective representation
 */
export interface Goal {
  id: string;
  name: string;
  description: string;

  // Preconditions (inputs)
  preconditions: Map<string, any>;

  // Expected outcomes (outputs)
  expectedOutcomes: Map<string, any>;

  // Priority (0-1)
  priority: number;

  // Reward function
  rewardFunction: (outcome: any) => number;

  // Subsumption layer
  layer: 'SAFETY' | 'REFLEX' | 'HABITUAL' | 'DELIBERATE';
}

// ============================================================================
// BRIDGE MAPPINGS
// ============================================================================

/**
 * Mapping between Microbiome taxonomy and Core tile categories
 */
const TAXONOMY_TO_TILE: Record<string, string> = {
  ['bacteria']: 'EPHEMERAL',  // Single-purpose workers
  ['virus']: 'CORE',           // Pluripotent/differentiating
  ['macrophage']: 'CORE',      // System guardians
  ['explorer']: 'ROLE',        // Ongoing exploration
  ['colony']: 'CORE',          // Structured communities
};

/**
 * Reverse mapping: Tile Category to Taxonomy
 */
const TILE_TO_TAXONOMY: Record<string, string> = {
  'EPHEMERAL': 'bacteria',
  'ROLE': 'explorer',
  'CORE': 'macrophage',
};

/**
 * Mapping between Microbiome resources and Core resources
 */
const RESOURCE_MAPPING: Record<string, string> = {
  'text': 'text',
  'structured': 'structured',
  'audio': 'audio',
  'image': 'image',
  'video': 'video',
  'code': 'code',
  'packages': 'packages',
  'anchors': 'anchors',
  'compute': 'compute',
  'memory': 'memory',
};

/**
 * Reverse mapping for resource lookup
 */
const RESOURCE_REVERSE_MAPPING: Record<string, string> = {
  'text': 'text',
  'structured': 'structured',
  'audio': 'audio',
  'image': 'image',
  'video': 'video',
  'code': 'code',
  'packages': 'packages',
  'anchors': 'anchors',
  'compute': 'compute',
  'memory': 'memory',
};

// ============================================================================
// BRIDGE CONFIGURATION
// ============================================================================

/**
 * Bridge configuration options
 */
export interface BridgeConfig {
  /** Enable detailed logging */
  verbose?: boolean;

  /** Preservation level for converted agents (0-1) */
  preservationLevel?: number;

  /** Auto-sync colony membership */
  autoSyncColonies?: boolean;

  /** Bridge A2A packages automatically */
  autoBridgePackages?: boolean;

  /** Custom taxonomy mappings */
  customTaxonomyMappings?: Partial<Record<AgentTaxonomy, TileCategory>>;

  /** Custom tile mappings */
  customTileMappings?: Partial<Record<TileCategory, AgentTaxonomy>>;
}

// ============================================================================
// MICROBIOME BRIDGE
// ============================================================================

/**
 * MicrobiomeBridge - bidirectional conversion between systems
 *
 * This bridge enables:
 * 1. Agent conversion (microbiome ↔ core)
 * 2. Taxonomy ↔ Tile category mapping
 * 3. Metabolism ↔ Goal translation
 * 4. A2A package bridging
 * 5. Colony synchronization
 */
export class MicrobiomeBridge {
  private config: Required<BridgeConfig>;
  private bridgeId: string;
  private colonySyncMap: Map<string, string>; // microColonyId -> coreColonyId
  private agentConversionCache: Map<string, any>; // microAgentId -> coreAgent (and vice versa)

  constructor(config: BridgeConfig = {}) {
    this.bridgeId = uuidv4();
    this.config = {
      verbose: config.verbose ?? false,
      preservationLevel: config.preservationLevel ?? 0.8,
      autoSyncColonies: config.autoSyncColonies ?? true,
      autoBridgePackages: config.autoBridgePackages ?? true,
      customTaxonomyMappings: config.customTaxonomyMappings ?? {},
      customTileMappings: config.customTileMappings ?? {},
    };

    this.colonySyncMap = new Map();
    this.agentConversionCache = new Map();

    if (this.config.verbose) {
      console.log(`[MicrobiomeBridge] Initialized bridge ${this.bridgeId}`);
    }
  }

  // ==========================================================================
  // AGENT CONVERSION
  // ==========================================================================

  /**
   * Convert microbiome agent to core agent representation
   *
   * @param microAgent - Microbiome agent to convert
   * @returns Core agent configuration
   */
  toCoreAgent(microAgent: MicrobiomeAgent): {
    config: any;
    goals: Goal[];
    metadata: Record<string, any>;
  } {
    const tileCategory = this.mapTaxonomyToTile(microAgent.taxonomy);

    // Extract core agent configuration
    const config = {
      id: microAgent.id,
      typeId: String(microAgent.taxonomy),
      categoryId: tileCategory,
      modelFamily: 'microbiome-bridge',
      defaultParams: {
        name: microAgent.name,
        size: microAgent.size,
        complexity: microAgent.complexity,
        generation: microAgent.generation,
      },
      inputTopics: microAgent.metabolism.inputs.map(r => RESOURCE_MAPPING[String(r)]),
      outputTopic: microAgent.metabolism.outputs[0] ? RESOURCE_MAPPING[String(microAgent.metabolism.outputs[0])] : 'default',
      minExamples: 0,
      requiresWorldModel: String(microAgent.taxonomy) === String(AgentTaxonomy.COLONY),
    };

    // Translate metabolism to goals
    const goals = this.translateMetabolismToGoals(microAgent.metabolism, microAgent.taxonomy);

    // Metadata preservation
    const metadata = {
      sourceSystem: 'microbiome',
      originalAgentId: microAgent.id,
      originalTaxonomy: String(microAgent.taxonomy),
      parentId: microAgent.parentId,
      health: microAgent.lifecycle.health,
      age: microAgent.lifecycle.age,
      isAlive: microAgent.lifecycle.isAlive,
      bridgeId: this.bridgeId,
      bridgeTimestamp: Date.now(),
      preservationLevel: this.config.preservationLevel,
    };

    // Cache the conversion
    this.agentConversionCache.set(microAgent.id, { config, goals, metadata });

    if (this.config.verbose) {
      console.log(`[MicrobiomeBridge] Converted agent ${microAgent.id} to core representation`);
    }

    return { config, goals, metadata };
  }

  /**
   * Convert core agent to microbiome agent representation
   *
   * @param coreAgent - Core agent to convert
   * @param metadata - Additional metadata for conversion
   * @returns Microbiome agent configuration
   */
  toMicrobiomeAgent(
    coreAgent: BaseAgent | any,
    metadata?: {
      tileCategory?: string | TileCategory;
      goals?: Goal[];
      customTaxonomy?: string | AgentTaxonomy;
    }
  ): {
    taxonomy: string;
    metabolism: MetabolicProfile;
    lifecycle: LifecycleState;
    metadata: Record<string, any>;
  } {
    // Determine taxonomy from tile category or custom
    const tileCategory = metadata?.tileCategory || 'EPHEMERAL';
    const taxonomy = metadata?.customTaxonomy
      ? String(metadata.customTaxonomy)
      : this.mapTileToTaxonomy(tileCategory);

    // Translate goals to metabolism
    const metabolism = metadata?.goals && metadata.goals.length > 0
      ? this.translateGoalsToMetabolism(metadata.goals)
      : this.getDefaultMetabolism(taxonomy as any);

    // Extract lifecycle from agent state
    const lifecycle: LifecycleState = {
      health: 1.0,
      age: 0,
      generation: 0,
      isAlive: true,
    };

    // Preserve metadata
    const agentMetadata = {
      sourceSystem: 'core',
      originalAgentId: coreAgent.id,
      originalTileCategory: tileCategory,
      bridgeId: this.bridgeId,
      bridgeTimestamp: Date.now(),
      preservationLevel: this.config.preservationLevel,
    };

    // Cache the conversion
    this.agentConversionCache.set(coreAgent.id, { taxonomy, metabolism, lifecycle, metadata: agentMetadata });

    if (this.config.verbose) {
      console.log(`[MicrobiomeBridge] Converted agent ${coreAgent.id} to microbiome representation`);
    }

    return {
      taxonomy,
      metabolism,
      lifecycle,
      metadata: agentMetadata,
    };
  }

  // ==========================================================================
  // TAXONOMY ↔ TILE MAPPING
  // ==========================================================================

  /**
   * Map microbiome taxonomy to core tile category
   *
   * @param taxonomy - Microbiome agent taxonomy
   * @returns Core tile category
   */
  mapTaxonomyToTile(taxonomy: string | AgentTaxonomy): string {
    const taxonomyStr = typeof taxonomy === 'string' ? taxonomy : String(taxonomy);

    // Check custom mappings first
    if (this.config.customTaxonomyMappings[taxonomy as AgentTaxonomy]) {
      return this.config.customTaxonomyMappings[taxonomy as AgentTaxonomy] as string;
    }

    // Use default mapping
    return TAXONOMY_TO_TILE[taxonomyStr] || 'EPHEMERAL';
  }

  /**
   * Map core tile category to microbiome taxonomy
   *
   * @param tile - Core tile category
   * @returns Microbiome agent taxonomy
   */
  mapTileToTaxonomy(tile: string | TileCategory): string {
    const tileStr = typeof tile === 'string' ? tile : String(tile);

    // Check custom mappings first
    if (this.config.customTileMappings[tileStr as TileCategory]) {
      return this.config.customTileMappings[tileStr as TileCategory];
    }

    // Use default mapping
    return TILE_TO_TAXONOMY[tileStr] || AgentTaxonomy.BACTERIA;
  }

  // ==========================================================================
  // METABOLISM ↔ GOAL TRANSLATION
  // ==========================================================================

  /**
   * Translate microbiome metabolism to core goals
   *
   * @param metabolism - Microbiome metabolic profile
   * @param taxonomy - Agent taxonomy for context
   * @returns Array of core goals
   */
  translateMetabolismToGoals(metabolism: MetabolicProfile, taxonomy: string | AgentTaxonomy): Goal[] {
    const goals: Goal[] = [];
    const taxonomyStr = String(taxonomy);

    // Primary goal: process inputs to outputs
    const primaryGoal: Goal = {
      id: uuidv4(),
      name: `${taxonomyStr}_processing_goal`,
      description: `Process ${metabolism.inputs.join(', ')} into ${metabolism.outputs.join(', ')}`,
      preconditions: new Map(
        metabolism.inputs.map(input => [RESOURCE_MAPPING[String(input)], true])
      ),
      expectedOutcomes: new Map(
        metabolism.outputs.map(output => [RESOURCE_MAPPING[String(output)], true])
      ),
      priority: this.mapProcessingRateToPriority(metabolism.processingRate),
      rewardFunction: (outcome: any) => {
        // Reward based on efficiency and success
        return metabolism.efficiency * (outcome?.success ? 1.0 : 0.5);
      },
      layer: this.mapTaxonomyToLayer(taxonomyStr as any),
    };

    goals.push(primaryGoal);

    // Survival goal (for bacteria)
    if (taxonomyStr === String(AgentTaxonomy.BACTERIA)) {
      goals.push({
        id: uuidv4(),
        name: 'survival_goal',
        description: 'Maintain health and reproduce',
        preconditions: new Map([['health', '> 0.5']]),
        expectedOutcomes: new Map([['reproduction', 'possible']]),
        priority: 0.8,
        rewardFunction: (outcome: any) => outcome?.health || 0.5,
        layer: 'HABITUAL',
      });
    }

    return goals;
  }

  /**
   * Translate core goals to microbiome metabolism
   *
   * @param goals - Array of core goals
   * @returns Microbiome metabolic profile
   */
  translateGoalsToMetabolism(goals: Goal[]): MetabolicProfile {
    if (goals.length === 0) {
      return this.getDefaultMetabolism(AgentTaxonomy.BACTERIA);
    }

    // Extract from primary goal
    const primaryGoal = goals[0];

    // Convert preconditions to inputs
    const inputs: ResourceType[] = [];
    primaryGoal.preconditions.forEach((value, key) => {
      const resourceTypeStr = this.findResourceTypeByMapping(key);
      if (resourceTypeStr) {
        // Convert string to ResourceType enum
        const enumKey = resourceTypeStr.toUpperCase() as keyof typeof ResourceType;
        if (ResourceType[enumKey]) {
          inputs.push(ResourceType[enumKey]);
        }
      }
    });

    // Convert outcomes to outputs
    const outputs: ResourceType[] = [];
    primaryGoal.expectedOutcomes.forEach((value, key) => {
      const resourceTypeStr = this.findResourceTypeByMapping(key);
      if (resourceTypeStr) {
        // Convert string to ResourceType enum
        const enumKey = resourceTypeStr.toUpperCase() as keyof typeof ResourceType;
        if (ResourceType[enumKey]) {
          outputs.push(ResourceType[enumKey]);
        }
      }
    });

    return {
      inputs: inputs.length > 0 ? inputs : [ResourceType.TEXT],
      outputs: outputs.length > 0 ? outputs : [ResourceType.STRUCTURED],
      processingRate: this.mapPriorityToProcessingRate(primaryGoal.priority),
      efficiency: 0.7, // Default efficiency
    };
  }

  // ==========================================================================
  // A2A PACKAGE BRIDGING
  // ==========================================================================

  /**
   * Bridge A2A package from microbiome to core format
   *
   * @param microPackage - Microbiome-style package
   * @returns Core A2A package
   */
  bridgeA2AToCore(microPackage: any): CoreA2APackage<any> {
    const corePackage: CoreA2APackage<any> = {
      id: microPackage.id || uuidv4(),
      timestamp: microPackage.timestamp || Date.now(),
      senderId: microPackage.senderId || microPackage.sourceId || 'unknown',
      receiverId: microPackage.receiverId || microPackage.targetId || 'unknown',
      type: microPackage.type || 'bridged',
      payload: microPackage.payload,
      parentIds: microPackage.parentIds || [],
      causalChainId: microPackage.causalChainId || uuidv4(),
      privacyLevel: microPackage.privacyLevel || 'PUBLIC',
      layer: microPackage.layer || 'HABITUAL',
      dpMetadata: microPackage.dpMetadata,
    };

    if (this.config.verbose) {
      console.log(`[MicrobiomeBridge] Bridged package ${corePackage.id} to core format`);
    }

    return corePackage;
  }

  /**
   * Bridge A2A package from core to microbiome format
   *
   * @param corePackage - Core A2A package
   * @returns Microbiome-style package
   */
  bridgeA2AToMicrobiome(corePackage: CoreA2APackage<any>): any {
    const microPackage = {
      id: corePackage.id,
      timestamp: corePackage.timestamp,
      sourceId: corePackage.senderId,
      targetId: corePackage.receiverId,
      type: corePackage.type,
      payload: corePackage.payload,
      parentIds: corePackage.parentIds,
      causalChainId: corePackage.causalChainId,
      privacyLevel: corePackage.privacyLevel,
      layer: corePackage.layer,
      dpMetadata: corePackage.dpMetadata,
    };

    if (this.config.verbose) {
      console.log(`[MicrobiomeBridge] Bridged package ${microPackage.id} to microbiome format`);
    }

    return microPackage;
  }

  // ==========================================================================
  // COLONY SYNCHRONIZATION
  // ==========================================================================

  /**
   * Register colony mapping between systems
   *
   * @param microColonyId - Microbiome colony ID
   * @param coreColonyId - Core colony ID
   */
  registerColonyMapping(microColonyId: string, coreColonyId: string): void {
    this.colonySyncMap.set(microColonyId, coreColonyId);

    if (this.config.verbose) {
      console.log(`[MicrobiomeBridge] Registered colony mapping: ${microColonyId} -> ${coreColonyId}`);
    }
  }

  /**
   * Sync colony membership between systems
   *
   * @param microColony - Microbiome colony
   * @param coreColony - Core colony
   */
  syncColonies(microColony: ColonyStructure, coreColony: any): void {
    // Register mapping
    this.registerColonyMapping(microColony.id, coreColony.id);

    // Sync members
    const microMembers = new Set(microColony.members);
    const coreMembers = new Set(coreColony.agents?.map((a: any) => a.id) || []);

    // Find members to add to core
    for (const memberId of microMembers) {
      if (!coreMembers.has(memberId)) {
        // Convert microbiome agent to core
        const converted = this.agentConversionCache.get(memberId);
        if (converted && this.config.autoSyncColonies) {
          // Would add to core colony here
          if (this.config.verbose) {
            console.log(`[MicrobiomeBridge] Would add member ${memberId} to core colony ${coreColony.id}`);
          }
        }
      }
    }

    // Sync communication channels
    for (const [source, target] of microColony.communicationChannels.entries()) {
      if (!coreColony.communicationChannels?.has(source)) {
        // Would add channel to core colony here
        if (this.config.verbose) {
          console.log(`[MicrobiomeBridge] Would add channel ${source} -> ${target} to core colony`);
        }
      }
    }

    if (this.config.verbose) {
      console.log(`[MicrobiomeBridge] Synced colonies: ${microColony.id} <-> ${coreColony.id}`);
    }
  }

  /**
   * Get mapped colony ID
   *
   * @param colonyId - Colony ID (from either system)
   * @param system - Which system the ID is from
   * @returns Mapped colony ID from the other system
   */
  getMappedColonyId(colonyId: string, system: 'microbiome' | 'core'): string | undefined {
    if (system === 'microbiome') {
      return this.colonySyncMap.get(colonyId);
    } else {
      // Reverse lookup
      for (const [microId, coreId] of this.colonySyncMap.entries()) {
        if (coreId === colonyId) {
          return microId;
        }
      }
    }
    return undefined;
  }

  // ==========================================================================
  // UTILITY METHODS
  // ==========================================================================

  /**
   * Get bridge statistics
   */
  getStats() {
    return {
      bridgeId: this.bridgeId,
      registeredColonyMappings: this.colonySyncMap.size,
      cachedConversions: this.agentConversionCache.size,
      config: this.config,
    };
  }

  /**
   * Clear conversion cache
   */
  clearCache(): void {
    this.agentConversionCache.clear();
    if (this.config.verbose) {
      console.log(`[MicrobiomeBridge] Cleared conversion cache`);
    }
  }

  // ==========================================================================
  // PRIVATE HELPERS
  // ==========================================================================

  /**
   * Map processing rate to priority
   */
  private mapProcessingRateToPriority(processingRate: number): number {
    // Normalize processing rate to 0-1 priority
    // Assuming max processing rate of 1000
    return Math.min(1.0, processingRate / 1000);
  }

  /**
   * Map priority to processing rate
   */
  private mapPriorityToProcessingRate(priority: number): number {
    // Convert priority back to processing rate
    return Math.floor(priority * 1000);
  }

  /**
   * Map taxonomy to subsumption layer
   */
  private mapTaxonomyToLayer(taxonomy: string | AgentTaxonomy): 'SAFETY' | 'REFLEX' | 'HABITUAL' | 'DELIBERATE' {
    const taxonomyStr = String(taxonomy);

    switch (taxonomyStr) {
      case String(AgentTaxonomy.MACROPHAGE):
        return 'SAFETY';
      case String(AgentTaxonomy.VIRUS):
        return 'REFLEX';
      case String(AgentTaxonomy.BACTERIA):
        return 'HABITUAL';
      case String(AgentTaxonomy.EXPLORER):
        return 'DELIBERATE';
      case String(AgentTaxonomy.COLONY):
        return 'DELIBERATE';
      default:
        return 'HABITUAL';
    }
  }

  /**
   * Get default metabolism for taxonomy
   */
  private getDefaultMetabolism(taxonomy: string | AgentTaxonomy): MetabolicProfile {
    const taxonomyStr = String(taxonomy);

    switch (taxonomyStr) {
      case String(AgentTaxonomy.BACTERIA):
        return {
          inputs: [ResourceType.TEXT],
          outputs: [ResourceType.STRUCTURED],
          processingRate: 10,
          efficiency: 0.7,
        };
      case String(AgentTaxonomy.VIRUS):
        return {
          inputs: [ResourceType.PACKAGES],
          outputs: [ResourceType.PACKAGES],
          processingRate: 100,
          efficiency: 0.9,
        };
      case String(AgentTaxonomy.MACROPHAGE):
        return {
          inputs: [ResourceType.PACKAGES],
          outputs: [ResourceType.ANCHORS],
          processingRate: 50,
          efficiency: 0.8,
        };
      case String(AgentTaxonomy.EXPLORER):
        return {
          inputs: [ResourceType.TEXT],
          outputs: [ResourceType.STRUCTURED],
          processingRate: 5,
          efficiency: 0.6,
        };
      case String(AgentTaxonomy.COLONY):
        return {
          inputs: [ResourceType.PACKAGES],
          outputs: [ResourceType.PACKAGES],
          processingRate: 1000,
          efficiency: 0.95,
        };
      default:
        return {
          inputs: [ResourceType.TEXT],
          outputs: [ResourceType.STRUCTURED],
          processingRate: 10,
          efficiency: 0.7,
        };
    }
  }

  /**
   * Find resource type by mapping key
   */
  private findResourceTypeByMapping(mapping: string): string | null {
    return RESOURCE_REVERSE_MAPPING[mapping] || null;
  }
}

// ============================================================================
// FACTORY FUNCTIONS
// ============================================================================

/**
 * Create a default microbiome bridge
 */
export function createMicrobiomeBridge(config?: BridgeConfig): MicrobiomeBridge {
  return new MicrobiomeBridge(config);
}

/**
 * Create a bridge with verbose logging
 */
export function createVerboseBridge(config?: Omit<BridgeConfig, 'verbose'>): MicrobiomeBridge {
  return new MicrobiomeBridge({ ...config, verbose: true });
}
