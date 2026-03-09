/**
 * POLLN Microbiome - Creativity & Goals Engine
 *
 * Phase 7: Emergent Intelligence - Milestone 3
 * Implements creativity and autonomous goal generation.
 *
 * Core capabilities:
 * - Novelty generation: Create new patterns and combinations
 * - Idea recombination: Cross-domain synthesis
 * - Analogical reasoning: Structure mapping between domains
 * - Divergent thinking: Generate multiple solutions
 * - Autonomous goal generation: Self-directed objectives
 * - Goal hierarchy construction: Nested goal structures
 * - Value discovery: Discover and evolve values
 * - Goal pursuit planning: Plan execution strategies
 * - Goal conflict resolution: Resolve competing goals
 *
 * @module microbiome/creativity
 */

import { EventEmitter } from 'events';
import {
  MicrobiomeAgent,
  AgentTaxonomy,
  FitnessScore,
  EcosystemSnapshot,
  ResourceType,
} from './types.js';
import { MetaLearningEngine, LearningContext, DomainKnowledge } from './metalearning.js';
import { SelfAwarenessEngine, SelfModel, MentalState } from './selfawareness.js';

// ============================================================================
// TYPES
// ============================================================================

/**
 * Creativity level (0-5)
 */
export enum CreativityLevel {
  /** No creativity (rote execution) */
  NONE = 0,
  /** Combinatorial creativity (recombine existing ideas) */
  COMBINATORIAL = 1,
  /** Exploratory creativity (explore solution space) */
  EXPLORATORY = 2,
  /** Transformational creativity (transform thinking) */
  TRANSFORMATIONAL = 3,
  /** Analogical creativity (cross-domain mapping) */
  ANALOGICAL = 4,
  /** Emergent creativity (genuinely novel insights) */
  EMERGENT = 5,
}

/**
 * Novel idea
 */
export interface NovelIdea {
  /** Idea ID */
  id: string;
  /** Idea name */
  name: string;
  /** Idea description */
  description: string;
  /** Creativity level */
  creativityLevel: CreativityLevel;
  /** Novelty score (0-1) */
  novelty: number;
  /** Feasibility score (0-1) */
  feasibility: number;
  /** Value score (0-1) */
  value: number;
  /** Source components (for recombination) */
  sourceComponents: string[];
  /** Domain context */
  domain: string;
  /** Expected outcomes */
  expectedOutcomes: Map<string, number>;
  /** Creation timestamp */
  createdAt: number;
  /** Times used */
  usageCount: number;
  /** Success rate */
  successRate: number;
}

/**
 * Analogy mapping
 */
export interface AnalogyMapping {
  /** Mapping ID */
  id: string;
  /** Source domain */
  sourceDomain: string;
  /** Target domain */
  targetDomain: string;
  /** Structural similarity (0-1) */
  structuralSimilarity: number;
  /** Mapping confidence (0-1) */
  confidence: number;
  /** Mapped concepts */
  conceptMappings: Map<string, string>;
  /** Predicted insights */
  predictedInsights: string[];
  /** Creation timestamp */
  createdAt: number;
  /** Validated flag */
  validated: boolean;
}

/**
 * Divergent thinking result
 */
export interface DivergentThinkingResult {
  /** Result ID */
  id: string;
  /** Problem description */
  problem: string;
  /** Generated solutions */
  solutions: Array<{
    solution: string;
    novelty: number;
    feasibility: number;
    value: number;
  }>;
  /** Diversity score (0-1) */
  diversity: number;
  /** Best solution */
  bestSolution: string;
  /** Generation timestamp */
  timestamp: number;
}

/**
 * Agent goal
 */
export interface Goal {
  /** Goal ID */
  id: string;
  /** Goal name */
  name: string;
  /** Goal description */
  description: string;
  /** Goal type */
  type: GoalType;
  /** Goal priority (0-1) */
  priority: number;
  /** Goal progress (0-1) */
  progress: number;
  /** Goal status */
  status: GoalStatus;
  /** Parent goal ID (if subgoal) */
  parentGoalId?: string;
  /** Child goal IDs */
  childGoalIds: string[];
  /** Created timestamp */
  createdAt: number;
  /** Deadline (optional) */
  deadline?: number;
  /** Expected value (0-1) */
  expectedValue: number;
  /** Actual value */
  actualValue?: number;
  /** Dependencies */
  dependencies: string[];
  /** Related values */
  relatedValues: string[];
}

/**
 * Goal type
 */
export enum GoalType {
  /** Survival goal (maintain existence) */
  SURVIVAL = 'survival',
  /** Growth goal (improve capabilities) */
  GROWTH = 'growth',
  /** Social goal (interact with others) */
  SOCIAL = 'social',
  /** Exploration goal (discover new things) */
  EXPLORATION = 'exploration',
  /** Creativity goal (generate novel ideas) */
  CREATIVITY = 'creativity',
  /** Achievement goal (accomplish something) */
  ACHIEVEMENT = 'achievement',
  /** Altruism goal (help others) */
  ALTRUISM = 'altruism',
}

/**
 * Goal status
 */
export enum GoalStatus {
  /** Not started */
  PENDING = 'pending',
  /** In progress */
  IN_PROGRESS = 'in_progress',
  /** Completed */
  COMPLETED = 'completed',
  /** Failed */
  FAILED = 'failed',
  /** Blocked */
  BLOCKED = 'blocked',
  /** Cancelled */
  CANCELLED = 'cancelled',
}

/**
 * Goal hierarchy
 */
export interface GoalHierarchy {
  /** Root goals (top-level) */
  rootGoals: Goal[];
  /** All goals by ID */
  allGoals: Map<string, Goal>;
  /** Goal relationships */
  relationships: Map<string, GoalRelationship[]>;
  /** Hierarchy depth */
  depth: number;
  /** Total goals */
  totalGoals: number;
  /** Last updated timestamp */
  lastUpdated: number;
}

/**
 * Goal relationship
 */
export interface GoalRelationship {
  /** Relationship type */
  type: GoalRelationType;
  /** Source goal ID */
  fromGoalId: string;
  /** Target goal ID */
  toGoalId: string;
  /** Relationship strength (0-1) */
  strength: number;
}

/**
 * Goal relationship type
 */
export enum GoalRelationType {
  /** Subgoal relationship */
  SUBGOAL = 'subgoal',
  /** Prerequisite relationship */
  PREREQUISITE = 'prerequisite',
  /** Conflicting relationship */
  CONFLICTING = 'conflicting',
  /** Supporting relationship */
  SUPPORTING = 'supporting',
  /** Mutually exclusive */
  MUTUALLY_EXCLUSIVE = 'mutually_exclusive',
}

/**
 * Discovered value
 */
export interface DiscoveredValue {
  /** Value ID */
  id: string;
  /** Value name */
  name: string;
  /** Value description */
  description: string;
  /** Value strength (0-1) */
  strength: number;
  /** Value source (how discovered) */
  source: string;
  /** Discovery timestamp */
  discoveredAt: number;
  /** Validation count */
  validationCount: number;
  /** Related goals */
  relatedGoals: string[];
  /** Value conflicts */
  conflicts: Map<string, number>;
  /** Alignment with human values (0-1) */
  alignment: number;
}

/**
 * Goal plan
 */
export interface GoalPlan {
  /** Plan ID */
  id: string;
  /** Goal ID */
  goalId: string;
  /** Plan steps */
  steps: PlanStep[];
  /** Resource requirements */
  resourceRequirements: Map<ResourceType, number>;
  /** Expected duration (ms) */
  expectedDuration: number;
  /** Success probability (0-1) */
  successProbability: number;
  /** Creation timestamp */
  createdAt: number;
  /** Execution status */
  status: PlanStatus;
}

/**
 * Plan step
 */
export interface PlanStep {
  /** Step ID */
  id: string;
  /** Step description */
  description: string;
  /** Step order */
  order: number;
  /** Required capabilities */
  requiredCapabilities: string[];
  /** Resource cost */
  resourceCost: Map<ResourceType, number>;
  /** Expected duration (ms) */
  expectedDuration: number;
  /** Dependencies (other step IDs) */
  dependencies: string[];
  /** Completion flag */
  completed: boolean;
}

/**
 * Plan status
 */
export enum PlanStatus {
  /** Not started */
  NOT_STARTED = 'not_started',
  /** In progress */
  IN_PROGRESS = 'in_progress',
  /** Completed */
  COMPLETED = 'completed',
  /** Failed */
  FAILED = 'failed',
  /** Abandoned */
  ABANDONED = 'abandoned',
}

/**
 * Goal conflict
 */
export interface GoalConflict {
  /** Conflict ID */
  id: string;
  /** Conflicting goal IDs */
  goalIds: string[];
  /** Conflict description */
  description: string;
  /** Conflict severity (0-1) */
  severity: number;
  /** Conflict type */
  type: ConflictType;
  /** Resolution strategy */
  resolutionStrategy?: ConflictResolution;
  /** Resolution timestamp */
  resolvedAt?: number;
}

/**
 * Conflict type
 */
export enum ConflictType {
  /** Resource conflict */
  RESOURCE = 'resource',
  /** Time conflict */
  TIME = 'time',
  /** Value conflict */
  VALUE = 'value',
  /** Logical conflict */
  LOGICAL = 'logical',
}

/**
 * Conflict resolution strategy
 */
export enum ConflictResolution {
  /** Prioritize one goal */
  PRIORITIZE = 'prioritize',
  /** Sequence goals */
  SEQUENCE = 'sequence',
  /** Compromise */
  COMPROMISE = 'compromise',
  /** Drop lower priority goal */
  DROP = 'drop',
  /** Find creative solution */
  CREATIVE = 'creative',
}

/**
 * Creativity configuration
 */
export interface CreativityConfig {
  /** Enable/disable creativity */
  enabled: boolean;
  /** Maximum novel ideas to store */
  maxNovelIdeas: number;
  /** Maximum analogies to store */
  maxAnalogies: number;
  /** Minimum novelty threshold */
  minNovelty: number;
  /** Minimum feasibility threshold */
  minFeasibility: number;
  /** Minimum value threshold */
  minValue: number;
  /** Exploration vs exploitation (0-1) */
  explorationFactor: number;
  /** Recombination rate (0-1) */
  recombinationRate: number;
  /** Analogy similarity threshold */
  analogyThreshold: number;
  /** Divergent thinking branch factor */
  divergentBranchFactor: number;
  /** Goal generation rate (0-1) */
  goalGenerationRate: number;
  /** Goal hierarchy depth limit */
  maxGoalDepth: number;
  /** Value discovery threshold */
  valueDiscoveryThreshold: number;
  /** Conflict resolution preference */
  conflictResolutionPreference: ConflictResolution;
}

/**
 * Creativity statistics
 */
export interface CreativityStats {
  /** Total novel ideas generated */
  ideasGenerated: number;
  /** Total analogies created */
  analogiesCreated: number;
  /** Total divergent thinking sessions */
  divergentSessions: number;
  /** Average creativity level */
  avgCreativityLevel: number;
  /** Total goals generated */
  goalsGenerated: number;
  /** Total goals completed */
  goalsCompleted: number;
  /** Total values discovered */
  valuesDiscovered: number;
  /** Total conflicts resolved */
  conflictsResolved: number;
  /** Average idea novelty */
  avgIdeaNovelty: number;
  /** Average idea success rate */
  avgIdeaSuccessRate: number;
  /** Last update timestamp */
  lastUpdate: number;
}

// ============================================================================
// CREATIVITY ENGINE
// ============================================================================

/**
 * CreativityEngine - Generate novel solutions and autonomous goals
 *
 * This engine implements creativity by:
 * 1. Generating novel ideas through recombination and mutation
 * 2. Creating analogies between domains for insight transfer
 * 3. Applying divergent thinking for multiple solutions
 * 4. Autonomously generating goals based on values and context
 * 5. Constructing goal hierarchies for complex objectives
 * 6. Discovering and evolving values through experience
 * 7. Planning goal pursuit strategies
 * 8. Resolving conflicts between goals
 *
 * Ethical considerations built-in:
 * - Novelty balanced with feasibility and value
 * - Goals aligned with human values
 * - Value discovery for alignment
 * - Conflict resolution for beneficence
 * - Creative solutions for non-maleficence
 */
export class CreativityEngine extends EventEmitter {
  /** Configuration */
  private config: CreativityConfig;

  /** Meta-learning engine for context assessment */
  private metaLearning?: MetaLearningEngine;

  /** Self-awareness engine for self-model access */
  private selfAwareness?: SelfAwarenessEngine;

  /** Novel ideas registry */
  private novelIdeas: Map<string, NovelIdea[]>;

  /** Analogy mappings registry */
  private analogies: Map<string, AnalogyMapping[]>;

  /** Goal hierarchies per agent */
  private goalHierarchies: Map<string, GoalHierarchy>;

  /** Discovered values per agent */
  private discoveredValues: Map<string, DiscoveredValue[]>;

  /** Goal plans */
  private goalPlans: Map<string, GoalPlan>;

  /** Goal conflicts */
  private goalConflicts: Map<string, GoalConflict>;

  /** Statistics */
  private stats: CreativityStats;

  /** Last update time */
  private lastUpdateTime: number;

  constructor(
    metaLearning?: MetaLearningEngine,
    selfAwareness?: SelfAwarenessEngine,
    config?: Partial<CreativityConfig>
  ) {
    super();

    this.metaLearning = metaLearning;
    this.selfAwareness = selfAwareness;
    this.novelIdeas = new Map();
    this.analogies = new Map();
    this.goalHierarchies = new Map();
    this.discoveredValues = new Map();
    this.goalPlans = new Map();
    this.goalConflicts = new Map();

    this.config = {
      enabled: true,
      maxNovelIdeas: 100,
      maxAnalogies: 50,
      minNovelty: 0.3,
      minFeasibility: 0.4,
      minValue: 0.5,
      explorationFactor: 0.3,
      recombinationRate: 0.5,
      analogyThreshold: 0.6,
      divergentBranchFactor: 5,
      goalGenerationRate: 0.2,
      maxGoalDepth: 5,
      valueDiscoveryThreshold: 0.7,
      conflictResolutionPreference: ConflictResolution.COMPROMISE,
      ...config,
    };

    this.stats = {
      ideasGenerated: 0,
      analogiesCreated: 0,
      divergentSessions: 0,
      avgCreativityLevel: 0,
      goalsGenerated: 0,
      goalsCompleted: 0,
      valuesDiscovered: 0,
      conflictsResolved: 0,
      avgIdeaNovelty: 0,
      avgIdeaSuccessRate: 0,
      lastUpdate: Date.now(),
    };

    this.lastUpdateTime = Date.now();
  }

  // ==========================================================================
  // NOVELTY GENERATION
  // ==========================================================================

  /**
   * Generate novel ideas through recombination and mutation
   *
   * Novelty generation process:
   * 1. Identify existing concepts/patterns
   * 2. Recombine concepts in new ways
   * 3. Mutate parameters for exploration
   * 4. Evaluate novelty, feasibility, and value
   * 5. Select best novel ideas
   */
  public generateNovelIdeas(
    agent: MicrobiomeAgent,
    context: string,
    count: number = 5
  ): NovelIdea[] {
    if (!this.config.enabled) {
      return [];
    }

    const agentId = agent.id;
    const ideas: NovelIdea[] = [];

    // Get existing ideas for recombination
    const existingIdeas = this.novelIdeas.get(agentId) ?? [];

    // Get self-model for capability-based generation
    const selfModel = this.selfAwareness?.getSelfModel(agentId);
    const capabilities = selfModel?.capabilities ?? [];

    // Generate ideas through recombination
    const recombinationIdeas = this.generateRecombinations(
      existingIdeas,
      capabilities,
      context,
      Math.ceil(count * this.config.recombinationRate)
    );
    ideas.push(...recombinationIdeas);

    // Generate ideas through mutation
    const mutationCount = count - recombinationIdeas.length;
    if (mutationCount > 0) {
      const mutationIdeas = this.generateMutations(
        existingIdeas,
        capabilities,
        context,
        mutationCount
      );
      ideas.push(...mutationIdeas);
    }

    // Filter and score ideas
    const scoredIdeas = ideas.filter(idea =>
      idea.novelty >= this.config.minNovelty &&
      idea.feasibility >= this.config.minFeasibility &&
      idea.value >= this.config.minValue
    );

    // Sort by combined score
    scoredIdeas.sort((a, b) => {
      const scoreA = this.calculateIdeaScore(a);
      const scoreB = this.calculateIdeaScore(b);
      return scoreB - scoreA;
    });

    // Store ideas
    const allIdeas = this.novelIdeas.get(agentId) ?? [];
    allIdeas.push(...scoredIdeas);

    // Limit storage
    if (allIdeas.length > this.config.maxNovelIdeas) {
      allIdeas.splice(0, allIdeas.length - this.config.maxNovelIdeas);
    }

    this.novelIdeas.set(agentId, allIdeas);

    // Update statistics
    this.stats.ideasGenerated += scoredIdeas.length;
    this.updateCreativityStats();

    this.emit('novel_ideas_generated', {
      agentId,
      ideas: scoredIdeas,
    });

    return scoredIdeas.slice(0, count);
  }

  /**
   * Generate ideas through recombination
   */
  private generateRecombinations(
    existingIdeas: NovelIdea[],
    capabilities: any[],
    context: string,
    count: number
  ): NovelIdea[] {
    const ideas: NovelIdea[] = [];

    // If no existing ideas, generate from capabilities
    if (existingIdeas.length < 2) {
      return this.generateFromCapabilities(capabilities, context, count);
    }

    // Recombine pairs of existing ideas
    for (let i = 0; i < count; i++) {
      // Select two random ideas
      const idx1 = Math.floor(Math.random() * existingIdeas.length);
      const idx2 = Math.floor(Math.random() * existingIdeas.length);

      const idea1 = existingIdeas[idx1];
      const idea2 = existingIdeas[idx2];

      // Create recombination
      const recombined = this.recombineIdeas(idea1, idea2, context);
      ideas.push(recombined);
    }

    return ideas;
  }

  /**
   * Recombine two ideas
   */
  private recombineIdeas(
    idea1: NovelIdea,
    idea2: NovelIdea,
    context: string
  ): NovelIdea {
    // Blend descriptions
    const description = `Combination of ${idea1.name} and ${idea2.name}`;

    // Calculate novelty (higher when combining dissimilar ideas)
    const novelty = 1 - this.calculateIdeaSimilarity(idea1, idea2);

    // Calculate feasibility (average of parents)
    const feasibility = (idea1.feasibility + idea2.feasibility) / 2;

    // Calculate value (average of parents)
    const value = (idea1.value + idea2.value) / 2;

    // Determine creativity level
    const creativityLevel = novelty > 0.7
      ? CreativityLevel.TRANSFORMATIONAL
      : novelty > 0.5
      ? CreativityLevel.EXPLORATORY
      : CreativityLevel.COMBINATORIAL;

    return {
      id: `idea-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: `${idea1.name} + ${idea2.name}`,
      description,
      creativityLevel,
      novelty,
      feasibility,
      value,
      sourceComponents: [idea1.id, idea2.id],
      domain: context,
      expectedOutcomes: new Map([
        ['success_probability', value],
        ['resource_efficiency', feasibility],
      ]),
      createdAt: Date.now(),
      usageCount: 0,
      successRate: 0,
    };
  }

  /**
   * Generate ideas through mutation
   */
  private generateMutations(
    existingIdeas: NovelIdea[],
    capabilities: any[],
    context: string,
    count: number
  ): NovelIdea[] {
    const ideas: NovelIdea[] = [];

    // If no existing ideas, generate from capabilities
    if (existingIdeas.length === 0) {
      return this.generateFromCapabilities(capabilities, context, count);
    }

    // Mutate existing ideas
    for (let i = 0; i < count; i++) {
      const parentIdx = Math.floor(Math.random() * existingIdeas.length);
      const parent = existingIdeas[parentIdx];

      const mutated = this.mutateIdea(parent, context);
      ideas.push(mutated);
    }

    return ideas;
  }

  /**
   * Mutate an idea
   */
  private mutateIdea(parent: NovelIdea, context: string): NovelIdea {
    // Add variation to description
    const variations = [
      'Optimized version of',
      'Enhanced',
      'Alternative approach to',
      'Simplified',
      'Specialized',
    ];
    const variation = variations[Math.floor(Math.random() * variations.length)];

    // Calculate novelty (moderate mutation)
    const novelty = Math.min(1, parent.novelty + Math.random() * 0.2);

    // Slightly adjust feasibility and value
    const feasibility = Math.max(0, Math.min(1, parent.feasibility + (Math.random() - 0.5) * 0.1));
    const value = Math.max(0, Math.min(1, parent.value + (Math.random() - 0.5) * 0.1));

    return {
      id: `idea-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: `${variation} ${parent.name}`,
      description: `${variation} ${parent.description}`,
      creativityLevel: parent.creativityLevel,
      novelty,
      feasibility,
      value,
      sourceComponents: [parent.id],
      domain: context,
      expectedOutcomes: new Map(parent.expectedOutcomes),
      createdAt: Date.now(),
      usageCount: 0,
      successRate: 0,
    };
  }

  /**
   * Generate ideas from capabilities
   */
  private generateFromCapabilities(
    capabilities: any[],
    context: string,
    count: number
  ): NovelIdea[] {
    const ideas: NovelIdea[] = [];

    // If no capabilities, generate generic ideas
    if (!capabilities || capabilities.length === 0) {
      for (let i = 0; i < count; i++) {
        ideas.push({
          id: `idea-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          name: `Novel approach ${i + 1}`,
          description: `Creative solution for ${context}`,
          creativityLevel: CreativityLevel.EXPLORATORY,
          novelty: 0.5 + Math.random() * 0.3,
          feasibility: 0.6,
          value: 0.6,
          sourceComponents: [],
          domain: context,
          expectedOutcomes: new Map([
            ['success_probability', 0.6],
          ]),
          createdAt: Date.now(),
          usageCount: 0,
          successRate: 0,
        });
      }
      return ideas;
    }

    for (let i = 0; i < count; i++) {
      const cap = capabilities[Math.floor(Math.random() * capabilities.length)];

      ideas.push({
        id: `idea-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: `Novel use of ${cap.name}`,
        description: `Creative application of ${cap.name} capability`,
        creativityLevel: CreativityLevel.COMBINATORIAL,
        novelty: 0.5 + Math.random() * 0.3,
        feasibility: cap.strength,
        value: cap.successRate,
        sourceComponents: [cap.id],
        domain: context,
        expectedOutcomes: new Map([
          ['capability_utilization', cap.strength],
        ]),
        createdAt: Date.now(),
        usageCount: 0,
        successRate: 0,
      });
    }

    return ideas;
  }

  /**
   * Calculate idea similarity
   */
  private calculateIdeaSimilarity(idea1: NovelIdea, idea2: NovelIdea): number {
    // Check for common source components
    const commonComponents = idea1.sourceComponents.filter(c =>
      idea2.sourceComponents.includes(c)
    );

    if (commonComponents.length > 0) {
      return 0.7; // High similarity if share components
    }

    // Domain similarity
    if (idea1.domain === idea2.domain) {
      return 0.5; // Moderate similarity if same domain
    }

    return 0; // Low similarity otherwise
  }

  /**
   * Calculate idea score
   */
  private calculateIdeaScore(idea: NovelIdea): number {
    // Weighted combination of novelty, feasibility, and value
    return idea.novelty * 0.3 + idea.feasibility * 0.3 + idea.value * 0.4;
  }

  // ==========================================================================
  // IDEA RECOMBINATION
  // ==========================================================================

  /**
   * Recombine ideas across domains
   */
  public crossDomainRecombination(
    agentId: string,
    sourceDomain: string,
    targetDomain: string
  ): NovelIdea[] {
    if (!this.config.enabled) {
      return [];
    }

    const sourceIdeas = this.novelIdeas.get(agentId) ?? [];
    const sourceDomainIdeas = sourceIdeas.filter(i => i.domain === sourceDomain);

    if (sourceDomainIdeas.length === 0) {
      return [];
    }

    const recombinations: NovelIdea[] = [];

    // Adapt source domain ideas to target domain
    for (const sourceIdea of sourceDomainIdeas) {
      const adapted = this.adaptIdeaToDomain(sourceIdea, targetDomain);
      recombinations.push(adapted);
    }

    // Store recombinations
    const allIdeas = this.novelIdeas.get(agentId) ?? [];
    allIdeas.push(...recombinations);
    this.novelIdeas.set(agentId, allIdeas);

    this.emit('cross_domain_recombination', {
      agentId,
      sourceDomain,
      targetDomain,
      recombinations,
    });

    return recombinations;
  }

  /**
   * Adapt idea to new domain
   */
  private adaptIdeaToDomain(idea: NovelIdea, targetDomain: string): NovelIdea {
    // Increase novelty for cross-domain application
    const novelty = Math.min(1, idea.novelty + 0.2);

    // Decrease feasibility slightly (new domain)
    const feasibility = Math.max(0, idea.feasibility - 0.1);

    return {
      ...idea,
      id: `idea-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: `${idea.name} (in ${targetDomain})`,
      description: `${idea.description} applied to ${targetDomain}`,
      domain: targetDomain,
      novelty,
      feasibility,
      creativityLevel: novelty > 0.7
        ? CreativityLevel.ANALOGICAL
        : idea.creativityLevel,
      createdAt: Date.now(),
    };
  }

  // ==========================================================================
  // ANALOGICAL REASONING
  // ==========================================================================

  /**
   * Create analogy mapping between domains
   *
   * Analogical reasoning process:
   * 1. Identify structural similarities between domains
   * 2. Map concepts from source to target
   * 3. Predict insights based on mapping
   * 4. Validate analogy quality
   */
  public createAnalogy(
    sourceDomain: string,
    targetDomain: string,
    structuralRelations: Map<string, string[]>
  ): AnalogyMapping | null {
    if (!this.config.enabled) {
      return null;
    }

    // Calculate structural similarity
    const structuralSimilarity = this.calculateStructuralSimilarity(
      sourceDomain,
      targetDomain,
      structuralRelations
    );

    if (structuralSimilarity < this.config.analogyThreshold) {
      return null; // Insufficient similarity for analogy
    }

    // Create concept mappings
    const conceptMappings = this.mapConcepts(
      sourceDomain,
      targetDomain,
      structuralRelations
    );

    // Predict insights
    const predictedInsights = this.predictInsightsFromAnalogy(
      conceptMappings,
      targetDomain
    );

    const analogy: AnalogyMapping = {
      id: `analogy-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      sourceDomain,
      targetDomain,
      structuralSimilarity,
      confidence: structuralSimilarity,
      conceptMappings,
      predictedInsights,
      createdAt: Date.now(),
      validated: false,
    };

    // Store analogy
    const analogies = this.analogies.get(targetDomain) ?? [];
    analogies.push(analogy);

    if (analogies.length > this.config.maxAnalogies) {
      analogies.shift();
    }

    this.analogies.set(targetDomain, analogies);

    // Update statistics
    this.stats.analogiesCreated++;
    this.emit('analogy_created', analogy);

    return analogy;
  }

  /**
   * Calculate structural similarity between domains
   */
  private calculateStructuralSimilarity(
    sourceDomain: string,
    targetDomain: string,
    structuralRelations: Map<string, string[]>
  ): number {
    // Simple similarity calculation
    // In practice, this would use more sophisticated graph matching

    let totalSimilarity = 0;
    let relationCount = 0;

    for (const [relation, entities] of structuralRelations) {
      if (entities.length >= 2) {
        // Domains share similar relation structures
        totalSimilarity += 1;
        relationCount++;
      }
    }

    return relationCount > 0 ? totalSimilarity / relationCount : 0;
  }

  /**
   * Map concepts between domains
   */
  private mapConcepts(
    sourceDomain: string,
    targetDomain: string,
    structuralRelations: Map<string, string[]>
  ): Map<string, string> {
    const mappings = new Map<string, string>();

    // Simple mapping based on relation positions
    // In practice, this would use semantic similarity
    for (const [relation, entities] of structuralRelations) {
      if (entities.length >= 2) {
        // Map first entity to second (simplified)
        mappings.set(entities[0], entities[1]);
      }
    }

    return mappings;
  }

  /**
   * Predict insights from analogy
   */
  private predictInsightsFromAnalogy(
    conceptMappings: Map<string, string>,
    targetDomain: string
  ): string[] {
    const insights: string[] = [];

    // Generate insights based on mappings
    for (const [sourceConcept, targetConcept] of conceptMappings) {
      insights.push(
        `${targetConcept} in ${targetDomain} may behave like ${sourceConcept}`
      );
    }

    return insights;
  }

  // ==========================================================================
  // DIVERGENT THINKING
  // ==========================================================================

  /**
   * Generate multiple diverse solutions to a problem
   *
   * Divergent thinking process:
   * 1. Decompose problem into components
   * 2. Generate solutions for each component
   * 3. Combine solutions in novel ways
   * 4. Evaluate diversity and quality
   * 5. Select best diverse solutions
   */
  public divergentThinking(
    agent: MicrobiomeAgent,
    problem: string,
    branchFactor: number = 5
  ): DivergentThinkingResult {
    if (!this.config.enabled) {
      throw new Error('Creativity is disabled');
    }

    const agentId = agent.id;
    const existingIdeas = this.novelIdeas.get(agentId) ?? [];

    // Generate diverse solutions
    const solutions: Array<{
      solution: string;
      novelty: number;
      feasibility: number;
      value: number;
    }> = [];

    // Branch 1: Conventional solution
    solutions.push({
      solution: `Standard approach to ${problem}`,
      novelty: 0.2,
      feasibility: 0.9,
      value: 0.7,
    });

    // Branch 2: Improved solution
    solutions.push({
      solution: `Optimized approach to ${problem}`,
      novelty: 0.4,
      feasibility: 0.7,
      value: 0.8,
    });

    // Branch 3: Creative solution
    solutions.push({
      solution: `Creative approach to ${problem}`,
      novelty: 0.7,
      feasibility: 0.5,
      value: 0.6,
    });

    // Branch 4: Radical solution
    solutions.push({
      solution: `Radical rethinking of ${problem}`,
      novelty: 0.9,
      feasibility: 0.3,
      value: 0.4,
    });

    // Branch 5: Cross-domain solution
    solutions.push({
      solution: `Cross-domain approach to ${problem}`,
      novelty: 0.6,
      feasibility: 0.6,
      value: 0.7,
    });

    // Calculate diversity
    const diversity = this.calculateSolutionDiversity(solutions);

    // Find best solution
    const bestSolution = solutions.reduce((best, current) => {
      const bestScore = best.novelty * 0.3 + best.feasibility * 0.3 + best.value * 0.4;
      const currentScore = current.novelty * 0.3 + current.feasibility * 0.3 + current.value * 0.4;
      return currentScore > bestScore ? current : best;
    });

    const result: DivergentThinkingResult = {
      id: `divergent-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      problem,
      solutions,
      diversity,
      bestSolution: bestSolution.solution,
      timestamp: Date.now(),
    };

    // Update statistics
    this.stats.divergentSessions++;
    this.emit('divergent_thinking_complete', result);

    return result;
  }

  /**
   * Calculate solution diversity
   */
  private calculateSolutionDiversity(
    solutions: Array<{
      solution: string;
      novelty: number;
      feasibility: number;
      value: number;
    }>
  ): number {
    if (solutions.length < 2) return 0;

    // Calculate variance in novelty scores
    const noveltyValues = solutions.map(s => s.novelty);
    const meanNovelty = noveltyValues.reduce((a, b) => a + b, 0) / noveltyValues.length;
    const variance = noveltyValues.reduce((sum, n) => sum + Math.pow(n - meanNovelty, 2), 0) /
                     noveltyValues.length;

    return Math.min(1, Math.sqrt(variance));
  }

  // ==========================================================================
  // AUTONOMOUS GOAL GENERATION
  // ==========================================================================

  /**
   * Generate autonomous goals based on values and context
   *
   * Goal generation process:
   * 1. Assess current state and capabilities
   * 2. Identify opportunities and needs
   * 3. Generate potential goals
   * 4. Evaluate goal value and feasibility
   * 5. Select and instantiate goals
   */
  public generateAutonomousGoals(
    agent: MicrobiomeAgent,
    snapshot: EcosystemSnapshot
  ): Goal[] {
    if (!this.config.enabled) {
      return [];
    }

    const agentId = agent.id;
    const selfModel = this.selfAwareness?.getSelfModel(agentId);

    // Get discovered values
    const values = this.discoveredValues.get(agentId) ?? [];

    // Generate goals based on values
    const goals: Goal[] = [];

    // Survival goals (always present)
    goals.push(this.createSurvivalGoal(agentId));

    // Growth goals (if capable)
    if (selfModel && selfModel.capabilities.length > 0) {
      goals.push(this.createGrowthGoal(agentId, selfModel));
    }

    // Social goals (if in colony)
    const colony = snapshot.colonies.find(c => c.members.includes(agentId));
    if (colony) {
      goals.push(this.createSocialGoal(agentId, colony));
    }

    // Exploration goals (if explorer agent)
    if (agent.taxonomy === AgentTaxonomy.EXPLORER) {
      goals.push(this.createExplorationGoal(agentId));
    }

    // Creativity goals (if creative capability)
    if (this.stats.avgCreativityLevel >= CreativityLevel.EXPLORATORY) {
      goals.push(this.createCreativityGoal(agentId));
    }

    // Value-based goals
    for (const value of values) {
      if (value.strength > this.config.valueDiscoveryThreshold) {
        goals.push(this.createValueBasedGoal(agentId, value));
      }
    }

    // Filter and prioritize goals
    const prioritizedGoals = goals.filter(g => g.priority >= 0.5);
    prioritizedGoals.sort((a, b) => b.priority - a.priority);

    // Add to goal hierarchy
    for (const goal of prioritizedGoals) {
      this.addGoalToHierarchy(agentId, goal);
    }

    // Update statistics
    this.stats.goalsGenerated += prioritizedGoals.length;
    this.emit('autonomous_goals_generated', {
      agentId,
      goals: prioritizedGoals,
    });

    return prioritizedGoals;
  }

  /**
   * Create survival goal
   */
  private createSurvivalGoal(agentId: string): Goal {
    return {
      id: `goal-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: 'Survive',
      description: 'Maintain existence and health',
      type: GoalType.SURVIVAL,
      priority: 1.0,
      progress: 0,
      status: GoalStatus.IN_PROGRESS,
      childGoalIds: [],
      createdAt: Date.now(),
      expectedValue: 1.0,
      dependencies: [],
      relatedValues: ['survival', 'health'],
    };
  }

  /**
   * Create growth goal
   */
  private createGrowthGoal(agentId: string, selfModel: SelfModel): Goal {
    return {
      id: `goal-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: 'Improve Capabilities',
      description: 'Enhance existing capabilities and develop new ones',
      type: GoalType.GROWTH,
      priority: 0.8,
      progress: 0,
      status: GoalStatus.PENDING,
      childGoalIds: [],
      createdAt: Date.now(),
      expectedValue: 0.8,
      dependencies: [],
      relatedValues: ['growth', 'improvement'],
    };
  }

  /**
   * Create social goal
   */
  private createSocialGoal(agentId: string, colony: any): Goal {
    return {
      id: `goal-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: 'Contribute to Colony',
      description: 'Cooperate with colony members for mutual benefit',
      type: GoalType.SOCIAL,
      priority: colony.stability * 0.7,
      progress: 0,
      status: GoalStatus.PENDING,
      childGoalIds: [],
      createdAt: Date.now(),
      expectedValue: colony.coEvolutionBonus,
      dependencies: [],
      relatedValues: ['cooperation', 'community'],
    };
  }

  /**
   * Create exploration goal
   */
  private createExplorationGoal(agentId: string): Goal {
    return {
      id: `goal-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: 'Explore Novelty',
      description: 'Discover new resources, patterns, and opportunities',
      type: GoalType.EXPLORATION,
      priority: 0.7,
      progress: 0,
      status: GoalStatus.PENDING,
      childGoalIds: [],
      createdAt: Date.now(),
      expectedValue: 0.7,
      dependencies: [],
      relatedValues: ['curiosity', 'discovery'],
    };
  }

  /**
   * Create creativity goal
   */
  private createCreativityGoal(agentId: string): Goal {
    return {
      id: `goal-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: 'Generate Novel Ideas',
      description: 'Create innovative solutions and approaches',
      type: GoalType.CREATIVITY,
      priority: 0.6,
      progress: 0,
      status: GoalStatus.PENDING,
      childGoalIds: [],
      createdAt: Date.now(),
      expectedValue: 0.6,
      dependencies: [],
      relatedValues: ['creativity', 'innovation'],
    };
  }

  /**
   * Create value-based goal
   */
  private createValueBasedGoal(agentId: string, value: DiscoveredValue): Goal {
    return {
      id: `goal-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: `Pursue ${value.name}`,
      description: value.description,
      type: GoalType.ACHIEVEMENT,
      priority: value.strength,
      progress: 0,
      status: GoalStatus.PENDING,
      childGoalIds: [],
      createdAt: Date.now(),
      expectedValue: value.strength,
      dependencies: [],
      relatedValues: [value.id],
    };
  }

  // ==========================================================================
  // GOAL HIERARCHY CONSTRUCTION
  // ==========================================================================

  /**
   * Add goal to hierarchy
   */
  private addGoalToHierarchy(agentId: string, goal: Goal): void {
    let hierarchy = this.goalHierarchies.get(agentId);

    if (!hierarchy) {
      hierarchy = {
        rootGoals: [],
        allGoals: new Map(),
        relationships: new Map(),
        depth: 1,
        totalGoals: 0,
        lastUpdated: Date.now(),
      };
    }

    // Add goal to all goals
    hierarchy.allGoals.set(goal.id, goal);

    // Add to root goals if no parent
    if (!goal.parentGoalId) {
      hierarchy.rootGoals.push(goal);
    }

    // Update hierarchy
    hierarchy.totalGoals = hierarchy.allGoals.size;
    hierarchy.lastUpdated = Date.now();

    this.goalHierarchies.set(agentId, hierarchy);
  }

  /**
   * Construct goal hierarchy with subgoals
   */
  public constructGoalHierarchy(
    agentId: string,
    rootGoal: Goal,
    maxDepth: number = 3
  ): GoalHierarchy {
    if (!this.config.enabled) {
      throw new Error('Creativity is disabled');
    }

    const hierarchy: GoalHierarchy = {
      rootGoals: [rootGoal],
      allGoals: new Map([[rootGoal.id, rootGoal]]),
      relationships: new Map(),
      depth: 1,
      totalGoals: 1,
      lastUpdated: Date.now(),
    };

    // Recursively decompose goals
    this.decomposeGoal(rootGoal, hierarchy, 1, maxDepth);

    // Store hierarchy
    this.goalHierarchies.set(agentId, hierarchy);

    this.emit('goal_hierarchy_constructed', {
      agentId,
      hierarchy,
    });

    return hierarchy;
  }

  /**
   * Decompose goal into subgoals
   */
  private decomposeGoal(
    goal: Goal,
    hierarchy: GoalHierarchy,
    currentDepth: number,
    maxDepth: number
  ): void {
    if (currentDepth >= maxDepth) {
      return;
    }

    // Generate subgoals based on goal type
    const subgoals = this.generateSubgoals(goal);

    for (const subgoal of subgoals) {
      // Set parent relationship
      subgoal.parentGoalId = goal.id;
      goal.childGoalIds.push(subgoal.id);

      // Add to hierarchy
      hierarchy.allGoals.set(subgoal.id, subgoal);
      hierarchy.totalGoals++;

      // Add relationship
      const relationship: GoalRelationship = {
        type: GoalRelationType.SUBGOAL,
        fromGoalId: goal.id,
        toGoalId: subgoal.id,
        strength: 1.0,
      };

      const relationships = hierarchy.relationships.get(goal.id) ?? [];
      relationships.push(relationship);
      hierarchy.relationships.set(goal.id, relationships);

      // Recursively decompose
      this.decomposeGoal(subgoal, hierarchy, currentDepth + 1, maxDepth);
    }

    // Update depth
    hierarchy.depth = Math.max(hierarchy.depth, currentDepth + 1);
  }

  /**
   * Generate subgoals for a goal
   */
  private generateSubgoals(goal: Goal): Goal[] {
    const subgoals: Goal[] = [];

    switch (goal.type) {
      case GoalType.SURVIVAL:
        subgoals.push(
          {
            id: `subgoal-${Date.now()}-1`,
            name: 'Maintain Health',
            description: 'Keep health above threshold',
            type: GoalType.SURVIVAL,
            priority: 0.9,
            progress: 0,
            status: GoalStatus.PENDING,
            childGoalIds: [],
            createdAt: Date.now(),
            expectedValue: 0.9,
            dependencies: [],
            relatedValues: ['health'],
          },
          {
            id: `subgoal-${Date.now()}-2`,
            name: 'Acquire Resources',
            description: 'Gather necessary resources',
            type: GoalType.SURVIVAL,
            priority: 0.8,
            progress: 0,
            status: GoalStatus.PENDING,
            childGoalIds: [],
            createdAt: Date.now(),
            expectedValue: 0.8,
            dependencies: [],
            relatedValues: ['resources'],
          }
        );
        break;

      case GoalType.GROWTH:
        subgoals.push(
          {
            id: `subgoal-${Date.now()}-1`,
            name: 'Learn New Skill',
            description: 'Acquire new capability',
            type: GoalType.GROWTH,
            priority: 0.7,
            progress: 0,
            status: GoalStatus.PENDING,
            childGoalIds: [],
            createdAt: Date.now(),
            expectedValue: 0.7,
            dependencies: [],
            relatedValues: ['learning', 'growth'],
          },
          {
            id: `subgoal-${Date.now()}-2`,
            name: 'Improve Existing Skills',
            description: 'Enhance current capabilities',
            type: GoalType.GROWTH,
            priority: 0.6,
            progress: 0,
            status: GoalStatus.PENDING,
            childGoalIds: [],
            createdAt: Date.now(),
            expectedValue: 0.6,
            dependencies: [],
            relatedValues: ['improvement'],
          }
        );
        break;

      default:
        // Generic subgoal decomposition
        if (goal.priority > 0.7) {
          subgoals.push({
            id: `subgoal-${Date.now()}-1`,
            name: `Plan ${goal.name}`,
            description: `Create plan for ${goal.name}`,
            type: goal.type,
            priority: goal.priority * 0.8,
            progress: 0,
            status: GoalStatus.PENDING,
            childGoalIds: [],
            createdAt: Date.now(),
            expectedValue: goal.expectedValue * 0.3,
            dependencies: [],
            relatedValues: [...goal.relatedValues],
          });
        }
    }

    return subgoals;
  }

  // ==========================================================================
  // VALUE DISCOVERY
  // ==========================================================================

  /**
   * Discover values from experience
   *
   * Value discovery process:
   * 1. Analyze successful outcomes
   * 2. Identify patterns in preferences
   * 3. Extract underlying values
   * 4. Validate value consistency
   * 5. Update value system
   */
  public discoverValues(
    agentId: string,
    experiences: Array<{
      context: string;
      actions: string[];
      outcomes: Map<string, number>;
    }>
  ): DiscoveredValue[] {
    if (!this.config.enabled) {
      return [];
    }

    const discoveredValues: DiscoveredValue[] = [];
    const existingValues = this.discoveredValues.get(agentId) ?? [];

    // Analyze experiences for value patterns
    for (const exp of experiences) {
      // Find successful outcomes
      for (const [outcome, value] of exp.outcomes) {
        if (value > this.config.valueDiscoveryThreshold) {
          // Extract potential value from outcome
          const potentialValue = this.extractValueFromOutcome(outcome, exp);

          // Check if value already exists
          const existing = existingValues.find(v => v.name === potentialValue.name);

          if (existing) {
            // Validate and strengthen existing value
            existing.validationCount++;
            existing.strength = Math.min(1, existing.strength + 0.1);
          } else {
            // Add new discovered value
            discoveredValues.push(potentialValue);
          }
        }
      }
    }

    // Store discovered values
    const allValues = [...existingValues, ...discoveredValues];
    this.discoveredValues.set(agentId, allValues);

    // Update statistics
    this.stats.valuesDiscovered += discoveredValues.length;
    this.emit('values_discovered', {
      agentId,
      values: discoveredValues,
    });

    return discoveredValues;
  }

  /**
   * Extract value from outcome
   */
  private extractValueFromOutcome(
    outcome: string,
    experience: { context: string; actions: string[]; outcomes: Map<string, number> }
  ): DiscoveredValue {
    // Map outcomes to values
    const valueMappings: Record<string, { name: string; description: string }> = {
      'cooperation': {
        name: 'Cooperation',
        description: 'Value working together with others',
      },
      'efficiency': {
        name: 'Efficiency',
        description: 'Value using resources optimally',
      },
      'innovation': {
        name: 'Innovation',
        description: 'Value novel and creative approaches',
      },
      'growth': {
        name: 'Growth',
        description: 'Value personal improvement and development',
      },
      'exploration': {
        name: 'Curiosity',
        description: 'Value discovering new things',
      },
    };

    const mapping = valueMappings[outcome] || {
      name: outcome.charAt(0).toUpperCase() + outcome.slice(1),
      description: `Value ${outcome}`,
    };

    return {
      id: `value-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: mapping.name,
      description: mapping.description,
      strength: 0.7,
      source: 'experience',
      discoveredAt: Date.now(),
      validationCount: 1,
      relatedGoals: [],
      conflicts: new Map(),
      alignment: 1.0, // Default alignment
    };
  }

  // ==========================================================================
  // GOAL PURSUIT PLANNING
  // ==========================================================================

  /**
   * Create plan for goal pursuit
   */
  public createGoalPlan(agentId: string, goalId: string): GoalPlan {
    if (!this.config.enabled) {
      throw new Error('Creativity is disabled');
    }

    const hierarchy = this.goalHierarchies.get(agentId);
    if (!hierarchy) {
      throw new Error(`No goal hierarchy found for agent ${agentId}`);
    }

    const goal = hierarchy.allGoals.get(goalId);
    if (!goal) {
      throw new Error(`Goal ${goalId} not found`);
    }

    // Generate plan steps
    const steps = this.generatePlanSteps(goal);

    // Calculate resource requirements
    const resourceRequirements = this.calculateResourceRequirements(goal);

    // Estimate duration
    const expectedDuration = steps.reduce((sum, step) => sum + step.expectedDuration, 0);

    // Estimate success probability
    const successProbability = this.calculateSuccessProbability(goal, steps);

    const plan: GoalPlan = {
      id: `plan-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      goalId,
      steps,
      resourceRequirements,
      expectedDuration,
      successProbability,
      createdAt: Date.now(),
      status: PlanStatus.NOT_STARTED,
    };

    // Store plan
    this.goalPlans.set(plan.id, plan);

    this.emit('goal_plan_created', {
      agentId,
      goalId,
      plan,
    });

    return plan;
  }

  /**
   * Generate plan steps
   */
  private generatePlanSteps(goal: Goal): PlanStep[] {
    const steps: PlanStep[] = [];

    // Generic planning based on goal type
    switch (goal.type) {
      case GoalType.SURVIVAL:
        steps.push(
          {
            id: `step-${Date.now()}-1`,
            description: 'Assess current health status',
            order: 1,
            requiredCapabilities: ['monitor'],
            resourceCost: new Map([[ResourceType.COMPUTE, 0.1]]),
            expectedDuration: 1000,
            dependencies: [],
            completed: false,
          },
          {
            id: `step-${Date.now()}-2`,
            description: 'Acquire necessary resources',
            order: 2,
            requiredCapabilities: ['gather'],
            resourceCost: new Map([[ResourceType.COMPUTE, 0.3]]),
            expectedDuration: 5000,
            dependencies: [],
            completed: false,
          },
          {
            id: `step-${Date.now()}-3`,
            description: 'Consume resources to maintain health',
            order: 3,
            requiredCapabilities: ['metabolize'],
            resourceCost: new Map([[ResourceType.COMPUTE, 0.2]]),
            expectedDuration: 2000,
            dependencies: [`step-${Date.now()}-2`],
            completed: false,
          }
        );
        break;

      case GoalType.GROWTH:
        steps.push(
          {
            id: `step-${Date.now()}-1`,
            description: 'Identify improvement opportunities',
            order: 1,
            requiredCapabilities: ['analyze'],
            resourceCost: new Map([[ResourceType.COMPUTE, 0.2]]),
            expectedDuration: 3000,
            dependencies: [],
            completed: false,
          },
          {
            id: `step-${Date.now()}-2`,
            description: 'Practice and develop new skills',
            order: 2,
            requiredCapabilities: ['learn'],
            resourceCost: new Map([[ResourceType.COMPUTE, 0.4]]),
            expectedDuration: 10000,
            dependencies: [`step-${Date.now()}-1`],
            completed: false,
          },
          {
            id: `step-${Date.now()}-3`,
            description: 'Validate skill improvements',
            order: 3,
            requiredCapabilities: ['evaluate'],
            resourceCost: new Map([[ResourceType.COMPUTE, 0.1]]),
            expectedDuration: 2000,
            dependencies: [`step-${Date.now()}-2`],
            completed: false,
          }
        );
        break;

      default:
        // Generic plan
        steps.push({
          id: `step-${Date.now()}-1`,
          description: `Plan execution for ${goal.name}`,
          order: 1,
          requiredCapabilities: ['plan'],
          resourceCost: new Map([[ResourceType.COMPUTE, 0.2]]),
          expectedDuration: 1000,
          dependencies: [],
          completed: false,
        });
    }

    return steps;
  }

  /**
   * Calculate resource requirements
   */
  private calculateResourceRequirements(goal: Goal): Map<ResourceType, number> {
    const requirements = new Map<ResourceType, number>();

    // Base energy requirement
    requirements.set(ResourceType.COMPUTE, goal.priority * 0.5);

    // Additional requirements based on goal type
    switch (goal.type) {
      case GoalType.GROWTH:
        requirements.set(ResourceType.COMPUTE, 0.7);
        break;
      case GoalType.EXPLORATION:
        requirements.set(ResourceType.COMPUTE, 0.6);
        break;
      case GoalType.CREATIVITY:
        requirements.set(ResourceType.COMPUTE, 0.5);
        requirements.set(ResourceType.COMPUTE, 0.3);
        break;
    }

    return requirements;
  }

  /**
   * Calculate success probability
   */
  private calculateSuccessProbability(goal: Goal, steps: PlanStep[]): number {
    // Base probability from expected value
    let probability = goal.expectedValue * 0.7;

    // Adjust for complexity (more steps = lower probability)
    probability *= Math.max(0.5, 1 - (steps.length - 3) * 0.05);

    return Math.max(0.1, Math.min(0.95, probability));
  }

  // ==========================================================================
  // GOAL CONFLICT RESOLUTION
  // ==========================================================================

  /**
   * Detect and resolve goal conflicts
   */
  public resolveGoalConflicts(agentId: string): GoalConflict[] {
    if (!this.config.enabled) {
      return [];
    }

    const hierarchy = this.goalHierarchies.get(agentId);
    if (!hierarchy) {
      return [];
    }

    const conflicts: GoalConflict[] = [];

    // Detect conflicts
    const detectedConflicts = this.detectConflicts(hierarchy);
    conflicts.push(...detectedConflicts);

    // Resolve conflicts
    for (const conflict of conflicts) {
      this.resolveConflict(conflict);
    }

    // Store conflicts
    for (const conflict of conflicts) {
      this.goalConflicts.set(conflict.id, conflict);
    }

    // Update statistics
    this.stats.conflictsResolved += conflicts.filter(c => c.resolvedAt).length;
    this.emit('goal_conflicts_resolved', {
      agentId,
      conflicts,
    });

    return conflicts;
  }

  /**
   * Detect conflicts in goal hierarchy
   */
  private detectConflicts(hierarchy: GoalHierarchy): GoalConflict[] {
    const conflicts: GoalConflict[] = [];
    const goals = Array.from(hierarchy.allGoals.values());

    // Check for resource conflicts
    const resourceConflicts = this.detectResourceConflicts(goals);
    conflicts.push(...resourceConflicts);

    // Check for time conflicts
    const timeConflicts = this.detectTimeConflicts(goals);
    conflicts.push(...timeConflicts);

    // Check for value conflicts
    const valueConflicts = this.detectValueConflicts(goals);
    conflicts.push(...valueConflicts);

    return conflicts;
  }

  /**
   * Detect resource conflicts
   */
  private detectResourceConflicts(goals: Goal[]): GoalConflict[] {
    const conflicts: GoalConflict[] = [];

    // Find goals with high resource requirements
    const highResourceGoals = goals.filter(g => g.priority > 0.7);

    for (let i = 0; i < highResourceGoals.length; i++) {
      for (let j = i + 1; j < highResourceGoals.length; j++) {
        const goal1 = highResourceGoals[i];
        const goal2 = highResourceGoals[j];

        // Check if goals are not subgoals of each other
        const areRelated = goal1.childGoalIds.includes(goal2.id) ||
                          goal2.childGoalIds.includes(goal1.id) ||
                          goal1.parentGoalId === goal2.id ||
                          goal2.parentGoalId === goal1.id;

        if (!areRelated) {
          conflicts.push({
            id: `conflict-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            goalIds: [goal1.id, goal2.id],
            description: `Resource conflict between ${goal1.name} and ${goal2.name}`,
            severity: Math.abs(goal1.priority - goal2.priority),
            type: ConflictType.RESOURCE,
          });
        }
      }
    }

    return conflicts;
  }

  /**
   * Detect time conflicts
   */
  private detectTimeConflicts(goals: Goal[]): GoalConflict[] {
    const conflicts: GoalConflict[] = [];

    // Find goals with deadlines
    const goalsWithDeadlines = goals.filter(g => g.deadline);

    for (let i = 0; i < goalsWithDeadlines.length; i++) {
      for (let j = i + 1; j < goalsWithDeadlines.length; j++) {
        const goal1 = goalsWithDeadlines[i];
        const goal2 = goalsWithDeadlines[j];

        if (goal1.deadline && goal2.deadline) {
          // Check if deadlines are close
          const timeDiff = Math.abs(goal1.deadline - goal2.deadline);
          if (timeDiff < 60000) { // Within 1 minute
            conflicts.push({
              id: `conflict-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
              goalIds: [goal1.id, goal2.id],
              description: `Time conflict between ${goal1.name} and ${goal2.name}`,
              severity: 1 - (timeDiff / 60000),
              type: ConflictType.TIME,
            });
          }
        }
      }
    }

    return conflicts;
  }

  /**
   * Detect value conflicts
   */
  private detectValueConflicts(goals: Goal[]): GoalConflict[] {
    const conflicts: GoalConflict[] = [];

    // Find goals with conflicting value priorities
    for (let i = 0; i < goals.length; i++) {
      for (let j = i + 1; j < goals.length; j++) {
        const goal1 = goals[i];
        const goal2 = goals[j];

        // Check for mutually exclusive values
        const hasConflictingValues = goal1.relatedValues.some(v1 =>
          goal2.relatedValues.some(v2 =>
            this.areConflictingValues(v1, v2)
          )
        );

        if (hasConflictingValues) {
          conflicts.push({
            id: `conflict-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            goalIds: [goal1.id, goal2.id],
            description: `Value conflict between ${goal1.name} and ${goal2.name}`,
            severity: 0.7,
            type: ConflictType.VALUE,
          });
        }
      }
    }

    return conflicts;
  }

  /**
   * Check if values are conflicting
   */
  private areConflictingValues(value1: string, value2: string): boolean {
    const conflictPairs: Array<[string, string]> = [
      ['exploration', 'stability'],
      ['novelty', 'tradition'],
      ['individual', 'collective'],
      ['risk', 'safety'],
    ];

    return conflictPairs.some(([v1, v2]) =>
      (value1.toLowerCase().includes(v1) && value2.toLowerCase().includes(v2)) ||
      (value1.toLowerCase().includes(v2) && value2.toLowerCase().includes(v1))
    );
  }

  /**
   * Resolve conflict
   */
  private resolveConflict(conflict: GoalConflict): void {
    // Apply resolution strategy
    switch (this.config.conflictResolutionPreference) {
      case ConflictResolution.PRIORITIZE:
        // Prioritize higher priority goal
        conflict.resolutionStrategy = ConflictResolution.PRIORITIZE;
        break;

      case ConflictResolution.SEQUENCE:
        // Sequence goals temporally
        conflict.resolutionStrategy = ConflictResolution.SEQUENCE;
        break;

      case ConflictResolution.COMPROMISE:
        // Find compromise
        conflict.resolutionStrategy = ConflictResolution.COMPROMISE;
        break;

      case ConflictResolution.DROP:
        // Drop lower priority goal
        conflict.resolutionStrategy = ConflictResolution.DROP;
        break;

      case ConflictResolution.CREATIVE:
        // Find creative solution
        conflict.resolutionStrategy = ConflictResolution.CREATIVE;
        break;
    }

    conflict.resolvedAt = Date.now();
  }

  // ==========================================================================
  // UTILITY METHODS
  // ==========================================================================

  /**
   * Update creativity statistics
   */
  private updateCreativityStats(): void {
    // Calculate average creativity level
    let totalLevel = 0;
    let count = 0;

    for (const ideas of this.novelIdeas.values()) {
      for (const idea of ideas) {
        totalLevel += idea.creativityLevel;
        count++;
      }
    }

    this.stats.avgCreativityLevel = count > 0 ? totalLevel / count : 0;

    // Calculate average novelty
    let totalNovelty = 0;
    let noveltyCount = 0;

    for (const ideas of this.novelIdeas.values()) {
      for (const idea of ideas) {
        totalNovelty += idea.novelty;
        noveltyCount++;
      }
    }

    this.stats.avgIdeaNovelty = noveltyCount > 0 ? totalNovelty / noveltyCount : 0;

    // Calculate average success rate
    let totalSuccessRate = 0;
    let successCount = 0;

    for (const ideas of this.novelIdeas.values()) {
      for (const idea of ideas) {
        if (idea.usageCount > 0) {
          totalSuccessRate += idea.successRate;
          successCount++;
        }
      }
    }

    this.stats.avgIdeaSuccessRate = successCount > 0 ? totalSuccessRate / successCount : 0;
  }

  /**
   * Get novel ideas for agent
   */
  public getNovelIdeas(agentId: string): NovelIdea[] {
    return this.novelIdeas.get(agentId) ?? [];
  }

  /**
   * Get analogies for domain
   */
  public getAnalogies(domain: string): AnalogyMapping[] {
    return this.analogies.get(domain) ?? [];
  }

  /**
   * Get goal hierarchy for agent
   */
  public getGoalHierarchy(agentId: string): GoalHierarchy | undefined {
    return this.goalHierarchies.get(agentId);
  }

  /**
   * Get discovered values for agent
   */
  public getDiscoveredValues(agentId: string): DiscoveredValue[] {
    return this.discoveredValues.get(agentId) ?? [];
  }

  /**
   * Get goal plan
   */
  public getGoalPlan(planId: string): GoalPlan | undefined {
    return this.goalPlans.get(planId);
  }

  /**
   * Get goal conflict
   */
  public getGoalConflict(conflictId: string): GoalConflict | undefined {
    return this.goalConflicts.get(conflictId);
  }

  /**
   * Get current statistics
   */
  public getStats(): CreativityStats {
    return { ...this.stats };
  }

  /**
   * Update configuration
   */
  public updateConfig(config: Partial<CreativityConfig>): void {
    this.config = { ...this.config, ...config };
    this.emit('config_updated', this.config);
  }

  /**
   * Get configuration
   */
  public getConfig(): CreativityConfig {
    return { ...this.config };
  }

  /**
   * Enable or disable creativity
   */
  public setEnabled(enabled: boolean): void {
    this.config.enabled = enabled;
    this.emit('enabled_changed', { enabled });
  }

  /**
   * Check if creativity is enabled
   */
  public isEnabled(): boolean {
    return this.config.enabled;
  }

  /**
   * Record idea usage
   */
  public recordIdeaUsage(agentId: string, ideaId: string, success: boolean): void {
    const ideas = this.novelIdeas.get(agentId);
    if (!ideas) return;

    const idea = ideas.find(i => i.id === ideaId);
    if (!idea) return;

    idea.usageCount++;

    // Update success rate
    if (idea.usageCount === 1) {
      idea.successRate = success ? 1 : 0;
    } else {
      idea.successRate = (idea.successRate * (idea.usageCount - 1) + (success ? 1 : 0)) / idea.usageCount;
    }

    this.updateCreativityStats();
  }

  /**
   * Update goal progress
   */
  public updateGoalProgress(
    agentId: string,
    goalId: string,
    progress: number,
    status?: GoalStatus
  ): void {
    const hierarchy = this.goalHierarchies.get(agentId);
    if (!hierarchy) return;

    const goal = hierarchy.allGoals.get(goalId);
    if (!goal) return;

    goal.progress = Math.max(0, Math.min(1, progress));

    if (status) {
      goal.status = status;

      if (status === GoalStatus.COMPLETED) {
        this.stats.goalsCompleted++;
        this.emit('goal_completed', { agentId, goalId });
      }
    }

    hierarchy.lastUpdated = Date.now();
  }

  /**
   * Clear all data for an agent
   */
  public clearAgentData(agentId: string): void {
    this.novelIdeas.delete(agentId);
    this.goalHierarchies.delete(agentId);
    this.discoveredValues.delete(agentId);
  }

  /**
   * Clear all data
   */
  public clearAllData(): void {
    this.novelIdeas.clear();
    this.analogies.clear();
    this.goalHierarchies.clear();
    this.discoveredValues.clear();
    this.goalPlans.clear();
    this.goalConflicts.clear();
  }
}

// ============================================================================
// FACTORY FUNCTION
// ============================================================================

/**
 * Create a creativity engine with default configuration
 */
export function createCreativityEngine(
  metaLearning?: MetaLearningEngine,
  selfAwareness?: SelfAwarenessEngine,
  config?: Partial<CreativityConfig>
): CreativityEngine {
  return new CreativityEngine(metaLearning, selfAwareness, config);
}
