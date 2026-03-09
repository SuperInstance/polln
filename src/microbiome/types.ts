/**
 * POLLN Microbiome Architecture - Core Types
 *
 * Reframes POLLN as a living ecosystem of computational agents.
 * Intelligence emerges from the interactions, not any single agent.
 *
 * @module microbiome/types
 */

/**
 * Taxonomy of digital life
 */
export enum AgentTaxonomy {
  /** Minimal, parasitic agents (10-100 bytes) */
  VIRUS = 'virus',
  /** Full agents with metabolic needs (1KB - 1MB) */
  BACTERIA = 'bacteria',
  /** Structured communities (10-1000+ agents) */
  COLONY = 'colony',
  /** System guardians (variable size) */
  MACROPHAGE = 'macrophage',
  /** Novelty seekers (lightweight to mobile) */
  EXPLORER = 'explorer',
}

/**
 * Resource types in the ecosystem
 */
export enum ResourceType {
  /** Raw text data */
  TEXT = 'text',
  /** Structured data (JSON, etc.) */
  STRUCTURED = 'structured',
  /** Audio data */
  AUDIO = 'audio',
  /** Image data */
  IMAGE = 'image',
  /** Video data */
  VIDEO = 'video',
  /** Code data */
  CODE = 'code',
  /** A2A packages */
  PACKAGES = 'packages',
  /** KV-cache anchors */
  ANCHORS = 'anchors',
  /** Compute cycles */
  COMPUTE = 'compute',
  /** Memory allocation */
  MEMORY = 'memory',
}

/**
 * Metabolic profile - what an agent consumes and produces
 */
export interface MetabolicProfile {
  /** Input resource types this agent consumes */
  inputs: ResourceType[];
  /** Output resource types this agent produces */
  outputs: ResourceType[];
  /** Processing rate (resources per second) */
  processingRate: number;
  /** Efficiency (0-1, higher is better) */
  efficiency: number;
}

/**
 * Agent health and lifecycle
 */
export interface LifecycleState {
  /** Current health (0-1) */
  health: number;
  /** Age in milliseconds */
  age: number;
  /** Generation (how many reproductions deep) */
  generation: number;
  /** Whether agent is alive */
  isAlive: boolean;
}

/**
 * Population dynamics for an agent type
 */
export interface PopulationDynamics {
  /** Current population count */
  population: number;
  /** Birth rate (per second) */
  birthRate: number;
  /** Death rate (per second) */
  deathRate: number;
  /** Carrying capacity (max sustainable) */
  carryingCapacity: number;
}

/**
 * Resource flow in the ecosystem
 */
export interface ResourceFlow {
  /** Resource type */
  resource: ResourceType;
  /** Flow rate (per second) */
  flowRate: number;
  /** Available amount */
  available: number;
  /** Total capacity */
  capacity: number;
}

/**
 * Mutation configuration
 */
export interface MutationConfig {
  /** Mutation rate (0-1) */
  mutationRate: number;
  /** Mutation types allowed */
  mutationTypes: MutationType[];
  /** Maximum change per mutation */
  maxMutationImpact: number;
}

/**
 * Types of mutations
 */
export enum MutationType {
  /** Goal adjustment (10% change in parameters) */
  GOAL_ADJUSTMENT = 'goal_adjustment',
  /** Method variation (different algorithm) */
  METHOD_VARIATION = 'method_variation',
  /** Metabolic shift (new input/output) */
  METABOLIC_SHIFT = 'metabolic_shift',
  /** Symbiosis gain (new dependency) */
  SYMBIOSIS_GAIN = 'symbiosis_gain',
}

/**
 * Fitness evaluation for natural selection
 */
export interface FitnessScore {
  /** Overall fitness (0-1) */
  overall: number;
  /** Processing speed score */
  throughput: number;
  /** Output quality score */
  accuracy: number;
  /** Resource efficiency score */
  efficiency: number;
  /** Symbiotic value score */
  cooperation: number;
}

/**
 * Symbiotic relationship
 */
export enum SymbiosisType {
  /** Both benefit */
  MUTUALISM = 'mutualism',
  /** One benefits, other unaffected */
  COMMENSALISM = 'commensalism',
  /** One benefits, other harmed */
  PARASITISM = 'parasitism',
  /** Predator-prey relationship */
  PREDATION = 'predation',
}

/**
 * Symbiotic relationship between agents
 */
export interface Symbiosis {
  /** Source agent ID */
  sourceId: string;
  /** Target agent ID */
  targetId: string;
  /** Type of relationship */
  type: SymbiosisType;
  /** Strength of relationship (0-1) */
  strength: number;
  /** Benefit to source (0-1) */
  benefitToSource: number;
  /** Benefit to target (0-1) */
  benefitToTarget: number;
}

/**
 * Colony structure (biofilm)
 */
export interface ColonyStructure {
  /** Colony ID */
  id: string;
  /** Member agent IDs */
  members: string[];
  /** Communication channels (direct A2A shortcuts) */
  communicationChannels: Map<string, string>;
  /** Formation time */
  formationTime: number;
  /** Stability score (0-1) */
  stability: number;
  /** Efficiency gain from co-evolution (0-1) */
  coEvolutionBonus: number;
}

/**
 * Ecosystem snapshot
 */
export interface EcosystemSnapshot {
  /** Timestamp */
  timestamp: number;
  /** All agents in ecosystem */
  agents: Map<string, MicrobiomeAgent>;
  /** Resource flows */
  resourceFlows: Map<ResourceType, ResourceFlow>;
  /** Population dynamics by type */
  populations: Map<AgentTaxonomy, PopulationDynamics>;
  /** Active colonies */
  colonies: ColonyStructure[];
  /** Symbiotic relationships */
  symbioses: Symbiosis[];
}

/**
 * Base microbiome agent interface
 */
export interface MicrobiomeAgent {
  /** Unique identifier */
  id: string;
  /** Taxonomic type */
  taxonomy: AgentTaxonomy;
  /** Agent name */
  name: string;
  /** Metabolic profile */
  metabolism: MetabolicProfile;
  /** Lifecycle state */
  lifecycle: LifecycleState;
  /** Parent ID (if reproduced) */
  parentId?: string;
  /** Generation */
  generation: number;
  /** Agent size in bytes */
  size: number;
  /** Complexity score (0-1) */
  complexity: number;

  /** Process resources */
  process(resources: Map<ResourceType, number>): Promise<Map<ResourceType, number>>;

  /** Reproduce (asexual) */
  reproduce(config: MutationConfig): Promise<MicrobiomeAgent>;

  /** Evaluate fitness */
  evaluateFitness(): FitnessScore;

  /** Check if can metabolize given resources */
  canMetabolize(resources: Map<ResourceType, number>): boolean;
}

/**
 * Virus/Prion - minimal parasitic agent
 */
export interface VirusAgent extends MicrobiomeAgent {
  taxonomy: AgentTaxonomy.VIRUS;
  /** Pattern to match */
  pattern: RegExp | string;
  /** Action to execute when pattern matches */
  action: (match: string | RegExpMatchArray) => any;
  /** Detection difficulty (0-1, higher is harder) */
  stealth: number;
}

/**
 * Bacteria/Protozoa - worker agent
 */
export interface BacteriaAgent extends MicrobiomeAgent {
  taxonomy: AgentTaxonomy.BACTERIA;
  /** Reproduction threshold (resources needed) */
  reproductionThreshold: number;
  /** Current accumulated resources */
  accumulatedResources: number;
  /** Dependencies (other agents this needs) */
  dependencies: string[];
}

/**
 * Macrophage - immune system agent
 */
export interface MacrophageAgent extends MicrobiomeAgent {
  taxonomy: AgentTaxonomy.MACROPHAGE;
  /** Targets to eliminate */
  targets: string[];
  /** Actions to take */
  actions: string[];
}

/**
 * Explorer - novelty-seeking agent
 */
export interface ExplorerAgent extends MicrobiomeAgent {
  taxonomy: AgentTaxonomy.EXPLORER;
  /** Exploration strategy */
  strategy: 'random_walk' | 'pattern_matching' | 'goal_directed';
  /** Targets to explore */
  targets: string[];
  /** Novelty detection function */
  noveltyScore: (data: any) => number;
}

/**
 * Ecosystem configuration
 */
export interface EcosystemConfig {
  /** Maximum total agents */
  maxAgents: number;
  /** Maximum colony size */
  maxColonySize: number;
  /** Resource refresh rate (per second) */
  resourceRefreshRate: number;
  /** Evolution enabled */
  evolutionEnabled: boolean;
  /** Mutation configuration */
  mutationConfig: MutationConfig;
  /** Selection pressure (0-1) */
  selectionPressure: number;
}

/**
 * Gardener actions (user interventions)
 */
export interface GardenerAction {
  /** Action type */
  type: 'introduce' | 'cull' | 'fertilize' | 'restrict' | 'graft' | 'export';
  /** Target agent ID (if applicable) */
  targetId?: string;
  /** Parameters */
  params: Record<string, any>;
}
