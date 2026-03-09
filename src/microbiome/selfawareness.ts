/**
 * POLLN Microbiome - Self-Awareness Engine
 *
 * Phase 7: Emergent Intelligence - Milestone 2
 * Implements self-awareness: know thyself through modeling, prediction, and reflection.
 *
 * Core capabilities:
 * - Self-modeling: Build accurate models of own capabilities and limitations
 * - Self-prediction: Predict own behavior and outcomes
 * - Performance monitoring: Meta-cognition about performance
 * - Blind spot detection: Discover unknown unknowns
 * - Theory of mind: Model other agents' mental states
 * - Reflective reasoning: Think about thinking
 *
 * @module microbiome/selfawareness
 */

import { EventEmitter } from 'events';
import {
  MicrobiomeAgent,
  AgentTaxonomy,
  FitnessScore,
  EcosystemSnapshot,
  ResourceType,
  LifecycleState,
  MetabolicProfile,
} from './types.js';
import { MetaLearningEngine, LearningContext, LearningStrategy } from './metalearning.js';

// ============================================================================
// TYPES
// ============================================================================

/**
 * Self-awareness level (0-5)
 */
export enum AwarenessLevel {
  /** No self-awareness (reactive only) */
  NONE = 0,
  /** Performance monitoring (know how well doing) */
  PERFORMANCE = 1,
  /** Self-modeling (know own capabilities) */
  MODELING = 2,
  /** Self-prediction (predict own behavior) */
  PREDICTION = 3,
  /** Blind spot awareness (know what don't know) */
  BLIND_SPOTS = 4,
  /** Theory of mind (understand others) */
  THEORY_OF_MIND = 5,
}

/**
 * Agent capability
 */
export interface Capability {
  /** Capability ID */
  id: string;
  /** Capability name */
  name: string;
  /** Capability description */
  description: string;
  /** Capability strength (0-1) */
  strength: number;
  /** Capability confidence (0-1) */
  confidence: number;
  /** Last validated timestamp */
  lastValidated: number;
  /** Usage count */
  usageCount: number;
  /** Success rate */
  successRate: number;
}

/**
 * Agent limitation
 */
export interface Limitation {
  /** Limitation ID */
  id: string;
  /** Limitation name */
  name: string;
  /** Limitation description */
  description: string;
  /** Severity (0-1) */
  severity: number;
  /** Confidence (0-1) */
  confidence: number;
  /** Discovered timestamp */
  discoveredAt: number;
  /** Mitigation strategies */
  mitigations: string[];
}

/**
 * Behavioral pattern
 */
export interface BehavioralPattern {
  /** Pattern ID */
  id: string;
  /** Pattern name */
  name: string;
  /** Pattern description */
  description: string;
  /** Pattern frequency (0-1) */
  frequency: number;
  /** Pattern strength (0-1) */
  strength: number;
  /** Typical contexts */
  contexts: string[];
  /** Expected outcomes */
  outcomes: Map<string, number>;
  /** Last observed timestamp */
  lastObserved: number;
}

/**
 * Performance history entry
 */
export interface PerformanceEntry {
  /** Timestamp */
  timestamp: number;
  /** Task context */
  context: string;
  /** Performance score (0-1) */
  performance: number;
  /** Resources consumed */
  resourcesConsumed: Map<ResourceType, number>;
  /** Time taken (ms) */
  timeTaken: number;
  /** Success flag */
  success: boolean;
}

/**
 * Self-model of an agent
 */
export interface SelfModel {
  /** Agent ID */
  agentId: string;
  /** Agent taxonomy */
  taxonomy: AgentTaxonomy;
  /** Current awareness level */
  awarenessLevel: AwarenessLevel;
  /** Capabilities */
  capabilities: Capability[];
  /** Limitations */
  limitations: Limitation[];
  /** Typical behaviors */
  typicalBehaviors: BehavioralPattern[];
  /** Performance history */
  performanceHistory: PerformanceEntry[];
  /** Social connections */
  socialConnections: Map<string, number>;
  /** Goals and preferences */
  goals: Goal[];
  /** Values */
  values: ValueSystem;
  /** Last updated timestamp */
  lastUpdated: number;
  /** Model confidence (0-1) */
  confidence: number;
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
  /** Goal priority (0-1) */
  priority: number;
  /** Goal progress (0-1) */
  progress: number;
  /** Goal status */
  status: GoalStatus;
  /** Created timestamp */
  createdAt: number;
  /** Deadline (optional) */
  deadline?: number;
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
}

/**
 * Value system
 */
export interface ValueSystem {
  /** Value ID */
  id: string;
  /** Value name */
  name: string;
  /** Value description */
  description: string;
  /** Value strength (0-1) */
  strength: number;
  /** Value conflicts */
  conflicts: Map<string, number>;
  /** Value alignment (0-1, with human values) */
  alignment: number;
}

/**
 * Self-prediction
 */
export interface SelfPrediction {
  /** Prediction ID */
  id: string;
  /** Situation context */
  situation: Situation;
  /** Predicted behavior */
  predictedBehavior: string;
  /** Predicted outcome */
  predictedOutcome: number;
  /** Confidence (0-1) */
  confidence: number;
  /** Alternative behaviors considered */
  alternatives: Array<{ behavior: string; probability: number }>;
  /** Prediction timestamp */
  timestamp: number;
}

/**
 * Situation for prediction
 */
export interface Situation {
  /** Situation ID */
  id: string;
  /** Context description */
  context: string;
  /** Available resources */
  resources: Map<ResourceType, number>;
  /** Environmental factors */
  environmentalFactors: Map<string, number>;
  /** Social context */
  socialContext: Map<string, number>;
  /** Time pressure (0-1) */
  timePressure: number;
}

/**
 * Performance report
 */
export interface PerformanceReport {
  /** Agent ID */
  agentId: string;
  /** Overall performance (0-1) */
  overallPerformance: number;
  /** Performance trend (-1 to 1) */
  performanceTrend: number;
  /** Strengths identified */
  strengths: string[];
  /** Weaknesses identified */
  weaknesses: string[];
  /** Improvement recommendations */
  recommendations: string[];
  /** Report timestamp */
  timestamp: number;
}

/**
 * Blind spot
 */
export interface BlindSpot {
  /** Blind spot ID */
  id: string;
  /** Blind spot description */
  description: string;
  /** Severity (0-1) */
  severity: number;
  /** Confidence (0-1) */
  confidence: number;
  /** Discovery method */
  discoveryMethod: string;
  /** Discovered timestamp */
  discoveredAt: number;
  /** Mitigation suggestions */
  mitigations: string[];
  /** Related contexts */
  relatedContexts: string[];
}

/**
 * Optimization plan
 */
export interface OptimizationPlan {
  /** Plan ID */
  id: string;
  /** Agent ID */
  agentId: string;
  /** Optimization goals */
  goals: string[];
  /** Optimization strategies */
  strategies: OptimizationStrategy[];
  /** Expected improvement (0-1) */
  expectedImprovement: number;
  /** Confidence (0-1) */
  confidence: number;
  /** Plan timestamp */
  timestamp: number;
}

/**
 * Optimization strategy
 */
export interface OptimizationStrategy {
  /** Strategy ID */
  id: string;
  /** Strategy name */
  name: string;
  /** Strategy description */
  description: string;
  /** Priority (0-1) */
  priority: number;
  /** Expected impact (0-1) */
  expectedImpact: number;
  /** Difficulty (0-1) */
  difficulty: number;
  /** Dependencies */
  dependencies: string[];
}

/**
 * Mental state (for theory of mind)
 */
export interface MentalState {
  /** Agent ID */
  agentId: string;
  /** Beliefs */
  beliefs: Map<string, number>;
  /** Desires */
  desires: Map<string, number>;
  /** Intentions */
  intentions: Map<string, number>;
  /** Emotional state */
  emotions: Map<string, number>;
  /** Current goals */
  goals: Goal[];
  /** Inference confidence (0-1) */
  confidence: number;
}

/**
 * Experience for reflection
 */
export interface Experience {
  /** Experience ID */
  id: string;
  /** Experience description */
  description: string;
  /** Context */
  context: LearningContext;
  /** Actions taken */
  actions: string[];
  /** Outcomes */
  outcomes: Map<string, number>;
  /** Reflections */
  reflections: string[];
  /** Learnings */
  learnings: string[];
  /** Experience timestamp */
  timestamp: number;
}

/**
 * Insight from reflection
 */
export interface Insight {
  /** Insight ID */
  id: string;
  /** Insight description */
  description: string;
  /** Insight type */
  type: InsightType;
  /** Confidence (0-1) */
  confidence: number;
  /** Applicability */
  applicability: string[];
  /** Insight timestamp */
  timestamp: number;
}

/**
 * Insight type
 */
export enum InsightType {
  /** Self-discovery */
  SELF_DISCOVERY = 'self_discovery',
  /** Pattern recognition */
  PATTERN_RECOGNITION = 'pattern_recognition',
  /** Improvement opportunity */
  IMPROVEMENT = 'improvement',
  /** Value alignment */
  VALUE_ALIGNMENT = 'value_alignment',
  /** Social understanding */
  SOCIAL_UNDERSTANDING = 'social_understanding',
}

/**
 * Self-awareness configuration
 */
export interface SelfAwarenessConfig {
  /** Enable/disable self-awareness */
  enabled: boolean;
  /** Maximum performance history size */
  maxHistorySize: number;
  /** Model update interval (ms) */
  updateInterval: number;
  /** Prediction confidence threshold */
  predictionThreshold: number;
  /** Blind spot detection sensitivity (0-1) */
  blindSpotSensitivity: number;
  /** Theory of mind inference depth */
  theoryOfMindDepth: number;
  /** Reflection frequency (0-1, per decision) */
  reflectionFrequency: number;
  /** Self-model learning rate */
  learningRate: number;
  /** Minimum capability confidence */
  minCapabilityConfidence: number;
  /** Maximum blind spot age (ms) */
  maxBlindSpotAge: number;
}

/**
 * Self-awareness statistics
 */
export interface SelfAwarenessStats {
  /** Total self-models built */
  modelsBuilt: number;
  /** Total predictions made */
  predictionsMade: number;
  /** Prediction accuracy */
  predictionAccuracy: number;
  /** Total blind spots discovered */
  blindSpotsDiscovered: number;
  /** Total insights generated */
  insightsGenerated: number;
  /** Average awareness level */
  avgAwarenessLevel: number;
  /** Total optimizations suggested */
  optimizationsSuggested: number;
  /** Theory of mind inferences */
  theoryOfMindInferences: number;
  /** Last update timestamp */
  lastUpdate: number;
}

// ============================================================================
// SELF-AWARENESS ENGINE
// ============================================================================

/**
 * SelfAwarenessEngine - Know thyself through modeling, prediction, and reflection
 *
 * This engine implements self-awareness by:
 * 1. Building accurate self-models of capabilities and limitations
 * 2. Predicting own behavior and outcomes in situations
 * 3. Monitoring performance with meta-cognition
 * 4. Detecting blind spots (unknown unknowns)
 * 5. Modeling other agents' mental states (theory of mind)
 * 6. Reflecting on experiences to generate insights
 *
 * Ethical considerations built-in:
 * - Self-modeling used for alignment, not manipulation
 * - Blind spot detection for safety and transparency
 * - Theory of mind for empathy and cooperation
 * - Reflection for value alignment and beneficence
 */
export class SelfAwarenessEngine extends EventEmitter {
  /** Configuration */
  private config: SelfAwarenessConfig;

  /** Meta-learning engine for context assessment */
  private metaLearning?: MetaLearningEngine;

  /** Self-models registry */
  private selfModels: Map<string, SelfModel>;

  /** Prediction history */
  private predictionHistory: Map<string, SelfPrediction[]>;

  /** Performance reports */
  private performanceReports: Map<string, PerformanceReport[]>;

  /** Blind spots registry */
  private blindSpots: Map<string, BlindSpot[]>;

  /** Theory of mind models */
  private mentalStates: Map<string, MentalState>;

  /** Insights registry */
  private insights: Map<string, Insight[]>;

  /** Optimization plans */
  private optimizationPlans: Map<string, OptimizationPlan[]>;

  /** Statistics */
  private stats: SelfAwarenessStats;

  /** Last update time */
  private lastUpdateTime: number;

  constructor(metaLearning?: MetaLearningEngine, config?: Partial<SelfAwarenessConfig>) {
    super();

    this.metaLearning = metaLearning;
    this.selfModels = new Map();
    this.predictionHistory = new Map();
    this.performanceReports = new Map();
    this.blindSpots = new Map();
    this.mentalStates = new Map();
    this.insights = new Map();
    this.optimizationPlans = new Map();

    this.config = {
      enabled: true,
      maxHistorySize: 1000,
      updateInterval: 60000, // 1 minute
      predictionThreshold: 0.6,
      blindSpotSensitivity: 0.7,
      theoryOfMindDepth: 2,
      reflectionFrequency: 0.1,
      learningRate: 0.1,
      minCapabilityConfidence: 0.5,
      maxBlindSpotAge: 86400000, // 24 hours
      ...config,
    };

    this.stats = {
      modelsBuilt: 0,
      predictionsMade: 0,
      predictionAccuracy: 0,
      blindSpotsDiscovered: 0,
      insightsGenerated: 0,
      avgAwarenessLevel: 0,
      optimizationsSuggested: 0,
      theoryOfMindInferences: 0,
      lastUpdate: Date.now(),
    };

    this.lastUpdateTime = Date.now();
  }

  // ==========================================================================
  // SELF-MODELING
  // ==========================================================================

  /**
   * Build self-model for an agent
   *
   * Self-model components:
   * - Capabilities: What can I do well?
   * - Limitations: What are my constraints?
   * - Behaviors: How do I typically act?
   * - Performance: How have I performed?
   * - Social: Who do I interact with?
   * - Goals: What am I trying to achieve?
   * - Values: What principles guide me?
   */
  public buildSelfModel(agent: MicrobiomeAgent, snapshot: EcosystemSnapshot): SelfModel {
    if (!this.config.enabled) {
      throw new Error('Self-awareness is disabled');
    }

    const agentId = agent.id;

    // Get or create self-model
    let model = this.selfModels.get(agentId);

    if (!model) {
      // Initialize new self-model
      model = {
        agentId,
        taxonomy: agent.taxonomy,
        awarenessLevel: AwarenessLevel.NONE,
        capabilities: [],
        limitations: [],
        typicalBehaviors: [],
        performanceHistory: [],
        socialConnections: new Map(),
        goals: [],
        values: this.initializeValueSystem(),
        lastUpdated: Date.now(),
        confidence: 0,
      };
    }

    // Extract capabilities from agent
    model.capabilities = this.extractCapabilities(agent, snapshot);

    // Identify limitations
    model.limitations = this.identifyLimitations(agent, snapshot);

    // Analyze typical behaviors
    model.typicalBehaviors = this.analyzeBehaviors(agent, snapshot);

    // Update performance history
    model.performanceHistory = this.updatePerformanceHistory(agent, model);

    // Analyze social connections
    model.socialConnections = this.analyzeSocialConnections(agent, snapshot);

    // Update awareness level
    model.awarenessLevel = this.calculateAwarenessLevel(model);

    // Update model confidence
    model.confidence = this.calculateModelConfidence(model);

    // Update timestamp
    model.lastUpdated = Date.now();

    // Store model
    this.selfModels.set(agentId, model);

    // Update statistics
    this.stats.modelsBuilt++;
    this.updateAverageAwarenessLevel();

    this.emit('self_model_updated', {
      agentId,
      model,
      awarenessLevel: model.awarenessLevel,
    });

    return model;
  }

  /**
   * Extract agent capabilities
   */
  private extractCapabilities(
    agent: MicrobiomeAgent,
    snapshot: EcosystemSnapshot
  ): Capability[] {
    const capabilities: Capability[] = [];

    // Metabolic capabilities
    if (agent.metabolism) {
      for (const input of agent.metabolism.inputs) {
        capabilities.push({
          id: `metabolize_${input}`,
          name: `Process ${input}`,
          description: `Can process ${input} resources`,
          strength: agent.metabolism.efficiency,
          confidence: 0.8,
          lastValidated: Date.now(),
          usageCount: 0,
          successRate: agent.metabolism.efficiency,
        });
      }
    }

    // Processing capability
    capabilities.push({
      id: 'process',
      name: 'Processing',
      description: 'Can process inputs and produce outputs',
      strength: agent.complexity,
      confidence: 0.9,
      lastValidated: Date.now(),
      usageCount: 0,
      successRate: agent.lifecycle?.health ?? 0.8,
    });

    // Reproduction capability
    capabilities.push({
      id: 'reproduce',
      name: 'Reproduction',
      description: 'Can create offspring agents',
      strength: agent.lifecycle?.health ?? 0.5,
      confidence: 0.7,
      lastValidated: Date.now(),
      usageCount: 0,
      successRate: 0.5,
    });

    // Taxonomy-specific capabilities
    switch (agent.taxonomy) {
      case AgentTaxonomy.BACTERIA:
        capabilities.push({
          id: 'form_colony',
          name: 'Colony Formation',
          description: 'Can form structured colonies with other agents',
          strength: 0.7,
          confidence: 0.8,
          lastValidated: Date.now(),
          usageCount: 0,
          successRate: 0.7,
        });
        break;

      case AgentTaxonomy.EXPLORER:
        capabilities.push({
          id: 'explore',
          name: 'Exploration',
          description: 'Can explore and discover novel resources',
          strength: 0.8,
          confidence: 0.9,
          lastValidated: Date.now(),
          usageCount: 0,
          successRate: 0.8,
        });
        break;
    }

    return capabilities;
  }

  /**
   * Identify agent limitations
   */
  private identifyLimitations(
    agent: MicrobiomeAgent,
    snapshot: EcosystemSnapshot
  ): Limitation[] {
    const limitations: Limitation[] = [];

    // Resource-based limitations
    if (agent.metabolism) {
      const canMetabolizeAll = agent.metabolize?.toString().includes('true') ?? false;

      if (!canMetabolizeAll && agent.metabolism.inputs.length < 3) {
        limitations.push({
          id: 'limited_metabolism',
          name: 'Limited Metabolism',
          description: 'Can only process a limited range of resource types',
          severity: 0.5,
          confidence: 0.8,
          discoveredAt: Date.now(),
          mitigations: [
            'Form symbioses with complementary agents',
            'Evolve to process new resource types',
            'Join colony for diverse metabolic capabilities',
          ],
        });
      }
    }

    // Complexity-based limitations
    if (agent.complexity < 0.3) {
      limitations.push({
        id: 'low_complexity',
        name: 'Low Complexity',
        description: 'Limited cognitive capacity for complex tasks',
        severity: 0.6,
        confidence: 0.9,
        discoveredAt: Date.now(),
        mitigations: [
          'Delegate complex tasks to specialized agents',
          'Form colonies for collective intelligence',
          'Use heuristics instead of deep reasoning',
        ],
      });
    }

    // Health-based limitations
    if (agent.lifecycle && agent.lifecycle.health < 0.5) {
      limitations.push({
        id: 'poor_health',
        name: 'Poor Health',
        description: 'Reduced capacity due to low health',
        severity: 0.7,
        confidence: 0.9,
        discoveredAt: Date.now(),
        mitigations: [
          'Consume resources to restore health',
          'Enter dormant state until conditions improve',
          'Seek mutualistic relationships',
        ],
      });
    }

    // Efficiency-based limitations
    if (agent.metabolism && agent.metabolism.efficiency < 0.5) {
      limitations.push({
        id: 'low_efficiency',
        name: 'Low Efficiency',
        description: 'Resource processing is inefficient',
        severity: 0.4,
        confidence: 0.8,
        discoveredAt: Date.now(),
        mitigations: [
          'Optimize metabolic pathways',
          'Evolve more efficient processing',
          'Scale back operations to critical functions',
        ],
      });
    }

    return limitations;
  }

  /**
   * Analyze typical behavioral patterns
   */
  private analyzeBehaviors(
    agent: MicrobiomeAgent,
    snapshot: EcosystemSnapshot
  ): BehavioralPattern[] {
    const patterns: BehavioralPattern[] = [];

    // Default processing pattern
    patterns.push({
      id: 'default_processing',
      name: 'Default Processing',
      description: 'Standard processing of inputs to outputs',
      frequency: 0.8,
      strength: agent.complexity,
      contexts: ['normal'],
      outcomes: new Map([
        ['output_generated', agent.metabolism?.efficiency ?? 0.8],
        ['resources_consumed', 1 - (agent.metabolism?.efficiency ?? 0.8)],
      ]),
      lastObserved: Date.now(),
    });

    // Colony behavior pattern
    const colony = snapshot.colonies.find(c => c.members.includes(agent.id));
    if (colony) {
      patterns.push({
        id: 'colony_behavior',
        name: 'Colony Cooperation',
        description: 'Cooperative behavior within colony',
        frequency: colony.stability,
        strength: colony.coEvolutionBonus,
        contexts: ['colony', 'cooperation'],
        outcomes: new Map([
          ['cooperation_benefit', colony.coEvolutionBonus],
          ['communication_cost', 0.1],
        ]),
        lastObserved: Date.now(),
      });
    }

    // Symbiosis behavior pattern
    const symbioses = snapshot.symbioses.filter(s =>
      s.sourceId === agent.id || s.targetId === agent.id
    );
    if (symbioses.length > 0) {
      const avgBenefit = symbioses.reduce((sum, s) => {
        return sum + (s.sourceId === agent.id ? s.benefitToSource : s.benefitToTarget);
      }, 0) / symbioses.length;

      patterns.push({
        id: 'symbiosis_behavior',
        name: 'Symbiotic Interaction',
        description: 'Engages in symbiotic relationships',
        frequency: 0.7,
        strength: avgBenefit,
        contexts: ['symbiosis', 'cooperation'],
        outcomes: new Map([
          ['symbiosis_benefit', avgBenefit],
          ['dependency_risk', 0.2],
        ]),
        lastObserved: Date.now(),
      });
    }

    return patterns;
  }

  /**
   * Update performance history
   */
  private updatePerformanceHistory(
    agent: MicrobiomeAgent,
    model: SelfModel
  ): PerformanceEntry[] {
    const history = model.performanceHistory;

    // Add current performance if available
    const currentFitness = agent.evaluateFitness?.();
    if (currentFitness) {
      const entry: PerformanceEntry = {
        timestamp: Date.now(),
        context: 'general',
        performance: currentFitness.overall,
        resourcesConsumed: new Map(),
        timeTaken: 0,
        success: currentFitness.overall > 0.5,
      };

      history.push(entry);

      // Limit history size
      if (history.length > this.config.maxHistorySize) {
        history.shift();
      }
    }

    return history;
  }

  /**
   * Analyze social connections
   */
  private analyzeSocialConnections(
    agent: MicrobiomeAgent,
    snapshot: EcosystemSnapshot
  ): Map<string, number> {
    const connections = new Map<string, number>();

    // Colony connections
    const colony = snapshot.colonies.find(c => c.members.includes(agent.id));
    if (colony) {
      for (const member of colony.members) {
        if (member !== agent.id) {
          connections.set(member, colony.stability);
        }
      }
    }

    // Symbiosis connections
    for (const symbiosis of snapshot.symbioses) {
      if (symbiosis.sourceId === agent.id) {
        connections.set(symbiosis.targetId, symbiosis.strength);
      } else if (symbiosis.targetId === agent.id) {
        connections.set(symbiosis.sourceId, symbiosis.strength);
      }
    }

    return connections;
  }

  /**
   * Initialize value system
   */
  private initializeValueSystem(): ValueSystem {
    return {
      id: 'default_values',
      name: 'Default Values',
      description: 'Basic value system aligned with ecosystem health',
      strength: 0.7,
      conflicts: new Map(),
      alignment: 1.0, // Fully aligned with human values
    };
  }

  /**
   * Calculate awareness level from self-model
   */
  private calculateAwarenessLevel(model: SelfModel): AwarenessLevel {
    let level = AwarenessLevel.NONE;

    // Check for performance monitoring
    if (model.performanceHistory.length > 0) {
      level = Math.max(level, AwarenessLevel.PERFORMANCE);
    }

    // Check for self-modeling
    if (model.capabilities.length > 0 && model.limitations.length > 0) {
      level = Math.max(level, AwarenessLevel.MODELING);
    }

    // Check for prediction capability
    const predictions = this.predictionHistory.get(model.agentId);
    if (predictions && predictions.length > 0) {
      level = Math.max(level, AwarenessLevel.PREDICTION);
    }

    // Check for blind spot awareness
    const blindSpots = this.blindSpots.get(model.agentId);
    if (blindSpots && blindSpots.length > 0) {
      level = Math.max(level, AwarenessLevel.BLIND_SPOTS);
    }

    // Check for theory of mind (has modeled other agents)
    if (this.mentalStates.size > 0) {
      level = Math.max(level, AwarenessLevel.THEORY_OF_MIND);
    }

    return level;
  }

  /**
   * Calculate model confidence
   */
  private calculateModelConfidence(model: SelfModel): number {
    let confidence = 0;

    // Capability confidence
    if (model.capabilities.length > 0) {
      const avgCapConfidence = model.capabilities.reduce((sum, c) => sum + c.confidence, 0) /
                               model.capabilities.length;
      confidence += avgCapConfidence * 0.3;
    }

    // Performance history confidence
    if (model.performanceHistory.length > 10) {
      confidence += 0.3;
    } else if (model.performanceHistory.length > 0) {
      confidence += 0.1;
    }

    // Behavior pattern confidence
    if (model.typicalBehaviors.length > 0) {
      confidence += 0.2;
    }

    // Limitation confidence
    if (model.limitations.length > 0) {
      const avgLimConfidence = model.limitations.reduce((sum, l) => sum + l.confidence, 0) /
                               model.limitations.length;
      confidence += avgLimConfidence * 0.2;
    }

    return Math.min(1, confidence);
  }

  // ==========================================================================
  // SELF-PREDICTION
  // ==========================================================================

  /**
   * Predict own behavior in a situation
   *
   * Prediction process:
   * 1. Retrieve self-model
   * 2. Match situation to known contexts
   * 3. Identify relevant behavioral patterns
   * 4. Predict most likely behavior
   * 5. Estimate confidence in prediction
   */
  public predictOwnBehavior(
    agent: MicrobiomeAgent,
    situation: Situation
  ): SelfPrediction {
    if (!this.config.enabled) {
      throw new Error('Self-awareness is disabled');
    }

    const agentId = agent.id;
    const model = this.selfModels.get(agentId);

    if (!model) {
      throw new Error(`No self-model found for agent ${agentId}`);
    }

    // Find matching behavioral patterns
    const matchingPatterns = this.findMatchingPatterns(model, situation);

    if (matchingPatterns.length === 0) {
      // No pattern match - low confidence prediction
      const prediction: SelfPrediction = {
        id: `pred-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        situation,
        predictedBehavior: 'default_processing',
        predictedOutcome: model.capabilities[0]?.strength ?? 0.5,
        confidence: 0.3,
        alternatives: [],
        timestamp: Date.now(),
      };

      this.storePrediction(agentId, prediction);
      return prediction;
    }

    // Select best matching pattern
    const bestPattern = matchingPatterns[0];

    // Calculate predicted outcome
    const predictedOutcome = bestPattern.strength * bestPattern.frequency;

    // Generate alternatives
    const alternatives = matchingPatterns.slice(1, 4).map(p => ({
      behavior: p.id,
      probability: p.frequency,
    }));

    const prediction: SelfPrediction = {
      id: `pred-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      situation,
      predictedBehavior: bestPattern.id,
      predictedOutcome,
      confidence: Math.min(1, bestPattern.frequency + bestPattern.strength) / 2,
      alternatives,
      timestamp: Date.now(),
    };

    this.storePrediction(agentId, prediction);
    this.stats.predictionsMade++;

    // Update awareness level (may have increased due to prediction capability)
    model.awarenessLevel = this.calculateAwarenessLevel(model);
    this.selfModels.set(agentId, model);
    this.updateAverageAwarenessLevel();

    this.emit('behavior_predicted', {
      agentId,
      prediction,
      model,
    });

    return prediction;
  }

  /**
   * Find behavioral patterns matching situation
   */
  private findMatchingPatterns(
    model: SelfModel,
    situation: Situation
  ): BehavioralPattern[] {
    const matches: BehavioralPattern[] = [];

    for (const pattern of model.typicalBehaviors) {
      let matchScore = 0;

      // Check context match
      for (const context of pattern.contexts) {
        if (situation.context.toLowerCase().includes(context.toLowerCase())) {
          matchScore += 0.5;
        }
      }

      // Check resource availability match
      for (const [resource, amount] of situation.resources) {
        if (amount > 0.5) {
          matchScore += 0.2;
        }
      }

      if (matchScore > 0) {
        matches.push({ ...pattern, strength: pattern.strength * matchScore });
      }
    }

    // Sort by strength
    matches.sort((a, b) => b.strength - a.strength);

    return matches;
  }

  /**
   * Store prediction in history
   */
  private storePrediction(agentId: string, prediction: SelfPrediction): void {
    const history = this.predictionHistory.get(agentId) ?? [];
    history.push(prediction);

    // Limit history size
    if (history.length > this.config.maxHistorySize) {
      history.shift();
    }

    this.predictionHistory.set(agentId, history);
  }

  /**
   * Validate prediction against actual outcome
   */
  public validatePrediction(
    agentId: string,
    predictionId: string,
    actualOutcome: number
  ): { accuracy: number; error: number } {
    const history = this.predictionHistory.get(agentId);
    if (!history) {
      throw new Error(`No prediction history for agent ${agentId}`);
    }

    const prediction = history.find(p => p.id === predictionId);
    if (!prediction) {
      throw new Error(`Prediction ${predictionId} not found`);
    }

    const error = Math.abs(prediction.predictedOutcome - actualOutcome);
    const accuracy = 1 - error;

    // Update prediction accuracy stats
    this.stats.predictionAccuracy =
      (this.stats.predictionAccuracy * (this.stats.predictionsMade - 1) + accuracy) /
      this.stats.predictionsMade;

    this.emit('prediction_validated', {
      agentId,
      predictionId,
      accuracy,
      error,
    });

    return { accuracy, error };
  }

  // ==========================================================================
  // PERFORMANCE MONITORING
  // ==========================================================================

  /**
   * Monitor agent performance with meta-cognition
   *
   * Monitoring aspects:
   * - Overall performance trend
   * - Strengths identification
   * - Weaknesses identification
   * - Improvement recommendations
   */
  public monitorPerformance(agent: MicrobiomeAgent): PerformanceReport {
    if (!this.config.enabled) {
      throw new Error('Self-awareness is disabled');
    }

    const agentId = agent.id;
    const model = this.selfModels.get(agentId);

    if (!model) {
      throw new Error(`No self-model found for agent ${agentId}`);
    }

    const history = model.performanceHistory;

    // Calculate overall performance
    const overallPerformance = history.length > 0
      ? history.reduce((sum, entry) => sum + entry.performance, 0) / history.length
      : 0.5;

    // Calculate performance trend
    const performanceTrend = this.calculatePerformanceTrend(history);

    // Identify strengths
    const strengths = this.identifyStrengths(model);

    // Identify weaknesses
    const weaknesses = this.identifyWeaknesses(model);

    // Generate recommendations
    const recommendations = this.generateRecommendations(model, strengths, weaknesses);

    const report: PerformanceReport = {
      agentId,
      overallPerformance,
      performanceTrend,
      strengths,
      weaknesses,
      recommendations,
      timestamp: Date.now(),
    };

    // Store report
    const reports = this.performanceReports.get(agentId) ?? [];
    reports.push(report);
    if (reports.length > 100) {
      reports.shift();
    }
    this.performanceReports.set(agentId, reports);

    this.emit('performance_monitored', {
      agentId,
      report,
    });

    return report;
  }

  /**
   * Calculate performance trend
   */
  private calculatePerformanceTrend(history: PerformanceEntry[]): number {
    if (history.length < 2) return 0;

    const recent = history.slice(-10);
    const firstHalf = recent.slice(0, Math.floor(recent.length / 2));
    const secondHalf = recent.slice(Math.floor(recent.length / 2));

    const avgFirst = firstHalf.reduce((sum, e) => sum + e.performance, 0) / firstHalf.length;
    const avgSecond = secondHalf.reduce((sum, e) => sum + e.performance, 0) / secondHalf.length;

    return avgSecond - avgFirst;
  }

  /**
   * Identify strengths from self-model
   */
  private identifyStrengths(model: SelfModel): string[] {
    const strengths: string[] = [];

    // Strong capabilities
    for (const cap of model.capabilities) {
      if (cap.strength > 0.7 && cap.confidence > this.config.minCapabilityConfidence) {
        strengths.push(cap.name);
      }
    }

    // Successful behavioral patterns
    for (const pattern of model.typicalBehaviors) {
      if (pattern.strength > 0.7 && pattern.frequency > 0.6) {
        strengths.push(pattern.name);
      }
    }

    // Good performance trend
    const history = model.performanceHistory;
    if (history.length >= 10) {
      const recent = history.slice(-10);
      const avgRecent = recent.reduce((sum, e) => sum + e.performance, 0) / recent.length;
      if (avgRecent > 0.7) {
        strengths.push('Consistent high performance');
      }
    }

    return strengths;
  }

  /**
   * Identify weaknesses from self-model
   */
  private identifyWeaknesses(model: SelfModel): string[] {
    const weaknesses: string[] = [];

    // Weak capabilities
    for (const cap of model.capabilities) {
      if (cap.strength < 0.4 && cap.confidence > this.config.minCapabilityConfidence) {
        weaknesses.push(cap.name);
      }
    }

    // Limitations
    for (const limit of model.limitations) {
      if (limit.severity > 0.5) {
        weaknesses.push(limit.name);
      }
    }

    // Poor performance trend
    const history = model.performanceHistory;
    if (history.length >= 10) {
      const recent = history.slice(-10);
      const avgRecent = recent.reduce((sum, e) => sum + e.performance, 0) / recent.length;
      if (avgRecent < 0.4) {
        weaknesses.push('Consistent low performance');
      }
    }

    return weaknesses;
  }

  /**
   * Generate improvement recommendations
   */
  private generateRecommendations(
    model: SelfModel,
    strengths: string[],
    weaknesses: string[]
  ): string[] {
    const recommendations: string[] = [];

    // Recommendations for weaknesses
    for (const weakness of weaknesses) {
      const limitation = model.limitations.find(l => l.name === weakness);
      if (limitation && limitation.mitigations.length > 0) {
        recommendations.push(...limitation.mitigations);
      }
    }

    // Leverage strengths
    if (strengths.length > 0) {
      recommendations.push(`Focus on leveraging strengths: ${strengths.join(', ')}`);
    }

    // Performance-based recommendations
    const history = model.performanceHistory;
    if (history.length >= 10) {
      const trend = this.calculatePerformanceTrend(history);
      if (trend < -0.1) {
        recommendations.push('Address declining performance trend');
      } else if (trend > 0.1) {
        recommendations.push('Maintain positive performance trajectory');
      }
    }

    return recommendations;
  }

  // ==========================================================================
  // BLIND SPOT DETECTION
  // ==========================================================================

  /**
   * Detect blind spots (unknown unknowns)
   *
   * Detection methods:
   * - Prediction failures: Where are we consistently wrong?
   * - Performance anomalies: Unexpected drops or spikes
   * - Context gaps: What situations haven't we experienced?
   * - Feedback inconsistencies: Where does self-assessment differ from external?
   */
  public detectBlindSpots(
    agent: MicrobiomeAgent,
    snapshot: EcosystemSnapshot
  ): BlindSpot[] {
    if (!this.config.enabled) {
      throw new Error('Self-awareness is disabled');
    }

    const agentId = agent.id;
    const model = this.selfModels.get(agentId);

    if (!model) {
      throw new Error(`No self-model found for agent ${agentId}`);
    }

    const blindSpots: BlindSpot[] = [];

    // Check for prediction failures
    const predictionFailures = this.detectPredictionFailures(agentId);
    blindSpots.push(...predictionFailures);

    // Check for performance anomalies
    const performanceAnomalies = this.detectPerformanceAnomalies(model);
    blindSpots.push(...performanceAnomalies);

    // Check for context gaps
    const contextGaps = this.detectContextGaps(model, snapshot);
    blindSpots.push(...contextGaps);

    // Check for feedback inconsistencies
    const feedbackInconsistencies = this.detectFeedbackInconsistencies(model, agent);
    blindSpots.push(...feedbackInconsistencies);

    // Filter by sensitivity threshold
    const filteredBlindSpots = blindSpots.filter(bs =>
      bs.confidence >= this.config.blindSpotSensitivity
    );

    // Store blind spots
    const existing = this.blindSpots.get(agentId) ?? [];
    const merged = this.mergeBlindSpots(existing, filteredBlindSpots);
    this.blindSpots.set(agentId, merged);

    // Update awareness level (may have increased due to blind spot detection)
    model.awarenessLevel = this.calculateAwarenessLevel(model);
    this.selfModels.set(agentId, model);
    this.updateAverageAwarenessLevel();

    // Update statistics
    this.stats.blindSpotsDiscovered += filteredBlindSpots.length;

    this.emit('blind_spots_detected', {
      agentId,
      blindSpots: filteredBlindSpots,
    });

    return filteredBlindSpots;
  }

  /**
   * Detect prediction failure patterns
   */
  private detectPredictionFailures(agentId: string): BlindSpot[] {
    const blindSpots: BlindSpot[] = [];
    const predictions = this.predictionHistory.get(agentId) ?? [];

    // Find predictions with high error (assume validated elsewhere)
    // This is a simplified version - in practice, you'd track validation results
    const recentPredictions = predictions.slice(-20);

    // Group by situation context
    const contextGroups = new Map<string, SelfPrediction[]>();
    for (const pred of recentPredictions) {
      const context = pred.situation.context;
      if (!contextGroups.has(context)) {
        contextGroups.set(context, []);
      }
      contextGroups.get(context)!.push(pred);
    }

    // Find contexts with consistently low confidence
    for (const [context, preds] of contextGroups) {
      const avgConfidence = preds.reduce((sum, p) => sum + p.confidence, 0) / preds.length;
      if (avgConfidence < 0.5 && preds.length >= 3) {
        blindSpots.push({
          id: `blindspot-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          description: `Uncertain predictions in context: ${context}`,
          severity: 1 - avgConfidence,
          confidence: avgConfidence,
          discoveryMethod: 'prediction_confidence',
          discoveredAt: Date.now(),
          mitigations: [
            'Gather more experience in this context',
            'Seek guidance from agents with relevant expertise',
            'Use conservative decision-making in this context',
          ],
          relatedContexts: [context],
        });
      }
    }

    return blindSpots;
  }

  /**
   * Detect performance anomalies
   */
  private detectPerformanceAnomalies(model: SelfModel): BlindSpot[] {
    const blindSpots: BlindSpot[] = [];
    const history = model.performanceHistory;

    if (history.length < 10) return blindSpots;

    // Calculate statistics
    const performances = history.map(e => e.performance);
    const mean = performances.reduce((a, b) => a + b, 0) / performances.length;
    const variance = performances.reduce((sum, p) => sum + Math.pow(p - mean, 2), 0) / performances.length;
    const stdDev = Math.sqrt(variance);

    // Find outliers (>2 standard deviations)
    for (const entry of history) {
      const zScore = Math.abs((entry.performance - mean) / stdDev);
      if (zScore > 2) {
        const isUnexpected = entry.performance < mean; // Unexpectedly poor
        if (isUnexpected) {
          blindSpots.push({
            id: `blindspot-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            description: `Unexpectedly poor performance in context: ${entry.context}`,
            severity: zScore / 3, // Normalize roughly to 0-1
            confidence: Math.min(1, zScore / 2),
            discoveryMethod: 'performance_anomaly',
            discoveredAt: Date.now(),
            mitigations: [
              'Investigate factors causing poor performance',
              'Consider alternative approaches in this context',
              'Review and adjust capabilities or limitations',
            ],
            relatedContexts: [entry.context],
          });
        }
      }
    }

    return blindSpots;
  }

  /**
   * Detect context gaps
   */
  private detectContextGaps(
    model: SelfModel,
    snapshot: EcosystemSnapshot
  ): BlindSpot[] {
    const blindSpots: BlindSpot[] = [];

    // Check for resource types not in metabolic profile
    if (model.capabilities.length > 0) {
      const knownResources = new Set<ResourceType>();
      for (const cap of model.capabilities) {
        if (cap.id.startsWith('metabolize_')) {
          const resource = cap.id.replace('metabolize_', '') as ResourceType;
          knownResources.add(resource);
        }
      }

      for (const resource of Object.values(ResourceType)) {
        if (!knownResources.has(resource)) {
          blindSpots.push({
            id: `blindspot-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            description: `No capability to process resource type: ${resource}`,
            severity: 0.5,
            confidence: 0.8,
            discoveryMethod: 'context_gap',
            discoveredAt: Date.now(),
            mitigations: [
              `Evolve to process ${resource}`,
              `Form symbiosis with agents that process ${resource}`,
              `Join colony with diverse metabolic capabilities`,
            ],
            relatedContexts: [`resource_${resource}`],
          });
        }
      }
    }

    return blindSpots;
  }

  /**
   * Detect feedback inconsistencies
   */
  private detectFeedbackInconsistencies(
    model: SelfModel,
    agent: MicrobiomeAgent
  ): BlindSpot[] {
    const blindSpots: BlindSpot[] = [];

    // Compare self-assessment with actual fitness
    if (model.performanceHistory.length > 0) {
      const recentPerformance = model.performanceHistory.slice(-5);
      const avgSelfAssessed = recentPerformance.reduce((sum, e) => sum + e.performance, 0) /
                             recentPerformance.length;

      const actualFitness = agent.evaluateFitness?.();
      if (actualFitness) {
        const discrepancy = Math.abs(avgSelfAssessed - actualFitness.overall);
        if (discrepancy > 0.2) {
          blindSpots.push({
            id: `blindspot-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            description: `Self-assessment differs from actual performance by ${discrepancy.toFixed(2)}`,
            severity: discrepancy,
            confidence: 0.7,
            discoveryMethod: 'feedback_inconsistency',
            discoveredAt: Date.now(),
            mitigations: [
              'Recalibrate self-assessment mechanisms',
              'Seek external feedback more frequently',
              'Review and update self-model',
            ],
            relatedContexts: ['self_assessment'],
          });
        }
      }
    }

    return blindSpots;
  }

  /**
   * Merge blind spots avoiding duplicates
   */
  private mergeBlindSpots(
    existing: BlindSpot[],
    newSpots: BlindSpot[]
  ): BlindSpot[] {
    const merged = [...existing];
    const now = Date.now();

    // Remove old blind spots
    const filtered = merged.filter(bs =>
      now - bs.discoveredAt < this.config.maxBlindSpotAge
    );

    // Add new blind spots (avoiding near-duplicates)
    for (const newSpot of newSpots) {
      const isDuplicate = filtered.some(existing =>
        existing.description === newSpot.description ||
        (existing.relatedContexts.some(ctx =>
          newSpot.relatedContexts.includes(ctx)
        ) && existing.severity === newSpot.severity)
      );

      if (!isDuplicate) {
        filtered.push(newSpot);
      }
    }

    return filtered;
  }

  // ==========================================================================
  // THEORY OF MIND
  // ==========================================================================

  /**
   * Model other agents' mental states
   *
   * Theory of mind components:
   * - Beliefs: What does the agent believe to be true?
   * - Desires: What does the agent want?
   * - Intentions: What is the agent trying to do?
   * - Emotions: How is the agent feeling?
   */
  public modelOtherAgents(
    observer: MicrobiomeAgent,
    targets: MicrobiomeAgent[],
    snapshot: EcosystemSnapshot
  ): Map<string, MentalState> {
    if (!this.config.enabled) {
      throw new Error('Self-awareness is disabled');
    }

    const mentalStates = new Map<string, MentalState>();

    for (const target of targets) {
      if (target.id === observer.id) continue; // Don't model self

      const state = this.inferMentalState(observer, target, snapshot);
      mentalStates.set(target.id, state);

      // Store mental state
      this.mentalStates.set(target.id, state);
      this.stats.theoryOfMindInferences++;
    }

    // Update observer's awareness level (may have increased due to theory of mind)
    const observerModel = this.selfModels.get(observer.id);
    if (observerModel) {
      observerModel.awarenessLevel = this.calculateAwarenessLevel(observerModel);
      this.selfModels.set(observer.id, observerModel);
      this.updateAverageAwarenessLevel();
    }

    this.emit('mental_states_modeled', {
      observerId: observer.id,
      mentalStates,
    });

    return mentalStates;
  }

  /**
   * Infer mental state of target agent
   */
  private inferMentalState(
    observer: MicrobiomeAgent,
    target: MicrobiomeAgent,
    snapshot: EcosystemSnapshot
  ): MentalState {
    const beliefs = new Map<string, number>();
    const desires = new Map<string, number>();
    const intentions = new Map<string, number>();
    const emotions = new Map<string, number>();
    const goals: Goal[] = [];

    // Infer beliefs from target's capabilities
    for (const cap of target.metabolism?.outputs ?? []) {
      beliefs.set(`can_produce_${cap}`, 0.8);
    }

    // Infer desires from target's metabolism inputs
    for (const input of target.metabolism?.inputs ?? []) {
      desires.set(`wants_${input}`, 0.9);
    }

    // Infer intentions from taxonomy
    switch (target.taxonomy) {
      case AgentTaxonomy.BACTERIA:
        intentions.set('survive', 0.9);
        intentions.set('reproduce', 0.7);
        intentions.set('cooperate', 0.6);
        break;
      case AgentTaxonomy.EXPLORER:
        intentions.set('explore', 0.9);
        intentions.set('discover', 0.8);
        intentions.set('innovate', 0.7);
        break;
      case AgentTaxonomy.MACROPHAGE:
        intentions.set('protect', 0.9);
        intentions.set('defend', 0.8);
        intentions.set('maintain_order', 0.7);
        break;
    }

    // Infer emotions from lifecycle state
    if (target.lifecycle) {
      emotions.set('energy', target.lifecycle.health);
      emotions.set('maturity', Math.min(1, target.lifecycle.age / 10000));
    }

    // Infer goals from intentions
    for (const [intention, strength] of intentions) {
      if (strength > 0.7) {
        goals.push({
          id: `goal-${intention}`,
          name: intention,
          description: `Achieve ${intention}`,
          priority: strength,
          progress: 0.5,
          status: GoalStatus.IN_PROGRESS,
          createdAt: Date.now(),
        });
      }
    }

    // Calculate confidence based on available information
    const confidence = this.calculateMentalStateConfidence(target, snapshot);

    return {
      agentId: target.id,
      beliefs,
      desires,
      intentions,
      emotions,
      goals,
      confidence,
    };
  }

  /**
   * Calculate confidence in mental state inference
   */
  private calculateMentalStateConfidence(
    target: MicrobiomeAgent,
    snapshot: EcosystemSnapshot
  ): number {
    let confidence = 0.5; // Base confidence

    // More information = higher confidence
    if (target.metabolism) confidence += 0.1;
    if (target.lifecycle) confidence += 0.1;
    if (target.taxonomy) confidence += 0.1;

    // Social relationship increases confidence
    const symbioses = snapshot.symbioses.filter(s =>
      s.sourceId === target.id || s.targetId === target.id
    );
    confidence += Math.min(0.2, symbioses.length * 0.05);

    return Math.min(1, confidence);
  }

  // ==========================================================================
  // REFLECTIVE REASONING
  // ==========================================================================

  /**
   * Reflect on experience to generate insights
   *
   * Reflection process:
   * 1. Review experience in detail
   * 2. Compare with expectations
   * 3. Identify patterns and anomalies
   * 4. Generate insights
   * 5. Update self-model
   */
  public reflect(
    agent: MicrobiomeAgent,
    experience: Experience
  ): Insight[] {
    if (!this.config.enabled) {
      throw new Error('Self-awareness is disabled');
    }

    const agentId = agent.id;
    const model = this.selfModels.get(agentId);

    if (!model) {
      throw new Error(`No self-model found for agent ${agentId}`);
    }

    const insights: Insight[] = [];

    // Analyze outcomes vs expectations
    const outcomeInsights = this.analyzeOutcomes(experience, model);
    insights.push(...outcomeInsights);

    // Identify patterns
    const patternInsights = this.identifyPatterns(experience, model);
    insights.push(...patternInsights);

    // Find improvement opportunities
    const improvementInsights = this.findImprovements(experience, model);
    insights.push(...improvementInsights);

    // Check value alignment
    const valueInsights = this.checkValueAlignment(experience, model);
    insights.push(...valueInsights);

    // Store insights
    const existing = this.insights.get(agentId) ?? [];
    existing.push(...insights);
    if (existing.length > 100) {
      existing.splice(0, insights.length);
    }
    this.insights.set(agentId, existing);

    // Update statistics
    this.stats.insightsGenerated += insights.length;

    this.emit('reflection_complete', {
      agentId,
      experience,
      insights,
    });

    return insights;
  }

  /**
   * Analyze outcomes to generate insights
   */
  private analyzeOutcomes(experience: Experience, model: SelfModel): Insight[] {
    const insights: Insight[] = [];

    for (const [outcome, value] of experience.outcomes) {
      // Unexpected positive outcomes
      if (value > 0.8) {
        insights.push({
          id: `insight-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          description: `Unexpected success in ${outcome}: ${value.toFixed(2)}`,
          type: InsightType.SELF_DISCOVERY,
          confidence: 0.8,
          applicability: [experience.context.domainKnowledge.toString()],
          timestamp: Date.now(),
        });
      }

      // Unexpected negative outcomes
      if (value < 0.3) {
        insights.push({
          id: `insight-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          description: `Unexpected failure in ${outcome}: ${value.toFixed(2)}`,
          type: InsightType.IMPROVEMENT,
          confidence: 0.7,
          applicability: [experience.context.domainKnowledge.toString()],
          timestamp: Date.now(),
        });
      }
    }

    return insights;
  }

  /**
   * Identify patterns in experience
   */
  private identifyPatterns(experience: Experience, model: SelfModel): Insight[] {
    const insights: Insight[] = [];

    // Check if actions match typical behaviors
    const matchingPatterns = model.typicalBehaviors.filter(bp =>
      experience.actions.some(a => a.includes(bp.id))
    );

    if (matchingPatterns.length === 0 && experience.actions.length > 0) {
      insights.push({
        id: `insight-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        description: 'Novel behavior pattern detected',
        type: InsightType.PATTERN_RECOGNITION,
        confidence: 0.6,
        applicability: ['learning', 'adaptation'],
        timestamp: Date.now(),
      });
    }

    return insights;
  }

  /**
   * Find improvement opportunities
   */
  private findImprovements(experience: Experience, model: SelfModel): Insight[] {
    const insights: Insight[] = [];

    // Check for resource inefficiency
    for (const [action, outcome] of experience.outcomes) {
      if (outcome < 0.5) {
        insights.push({
          id: `insight-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          description: `Opportunity to improve ${action} efficiency`,
          type: InsightType.IMPROVEMENT,
          confidence: 0.7,
          applicability: [action],
          timestamp: Date.now(),
        });
      }
    }

    return insights;
  }

  /**
   * Check value alignment
   */
  private checkValueAlignment(experience: Experience, model: SelfModel): Insight[] {
    const insights: Insight[] = [];

    // Check if actions align with values
    // This is simplified - in practice, you'd have more sophisticated value checking
    if (experience.outcomes.has('cooperation') && experience.outcomes.get('cooperation')! > 0.7) {
      insights.push({
        id: `insight-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        description: 'Actions demonstrate cooperative values',
        type: InsightType.VALUE_ALIGNMENT,
        confidence: 0.8,
        applicability: ['cooperation', 'social'],
        timestamp: Date.now(),
      });
    }

    return insights;
  }

  // ==========================================================================
  // SELF-OPTIMIZATION
  // ==========================================================================

  /**
   * Generate optimization plan for agent
   */
  public optimizeSelf(agent: MicrobiomeAgent): OptimizationPlan {
    if (!this.config.enabled) {
      throw new Error('Self-awareness is disabled');
    }

    const agentId = agent.id;
    const model = this.selfModels.get(agentId);

    if (!model) {
      throw new Error(`No self-model found for agent ${agentId}`);
    }

    // Get performance report
    const perfReport = this.performanceReports.get(agentId)?.[0];
    if (!perfReport) {
      throw new Error(`No performance report available for agent ${agentId}`);
    }

    // Get blind spots
    const blindSpots = this.blindSpots.get(agentId) ?? [];

    // Generate optimization strategies
    const strategies: OptimizationStrategy[] = [];

    for (const weakness of perfReport.weaknesses) {
      strategies.push({
        id: `strategy-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: `Address ${weakness}`,
        description: `Improve capability in ${weakness}`,
        priority: 0.7,
        expectedImpact: 0.3,
        difficulty: 0.6,
        dependencies: [],
      });
    }

    for (const blindSpot of blindSpots) {
      strategies.push({
        id: `strategy-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: `Address blind spot: ${blindSpot.description}`,
        description: blindSpot.description,
        priority: blindSpot.severity,
        expectedImpact: blindSpot.severity * 0.5,
        difficulty: 0.7,
        dependencies: [],
      });
    }

    // Calculate expected improvement
    const expectedImprovement = strategies.reduce((sum, s) => sum + s.expectedImpact, 0) /
                                 Math.max(1, strategies.length);

    const plan: OptimizationPlan = {
      id: `plan-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      agentId,
      goals: perfReport.recommendations,
      strategies,
      expectedImprovement,
      confidence: model.confidence,
      timestamp: Date.now(),
    };

    // Store plan
    const plans = this.optimizationPlans.get(agentId) ?? [];
    plans.push(plan);
    if (plans.length > 10) {
      plans.shift();
    }
    this.optimizationPlans.set(agentId, plans);

    // Update statistics
    this.stats.optimizationsSuggested++;

    this.emit('optimization_plan_created', {
      agentId,
      plan,
    });

    return plan;
  }

  // ==========================================================================
  // UTILITY METHODS
  // ==========================================================================

  /**
   * Update average awareness level
   */
  private updateAverageAwarenessLevel(): void {
    if (this.selfModels.size === 0) {
      this.stats.avgAwarenessLevel = 0;
      return;
    }

    const total = Array.from(this.selfModels.values())
      .reduce((sum, model) => sum + model.awarenessLevel, 0);

    this.stats.avgAwarenessLevel = total / this.selfModels.size;
  }

  /**
   * Get self-model for agent
   */
  public getSelfModel(agentId: string): SelfModel | undefined {
    return this.selfModels.get(agentId);
  }

  /**
   * Get all self-models
   */
  public getAllSelfModels(): Map<string, SelfModel> {
    return new Map(this.selfModels);
  }

  /**
   * Get prediction history for agent
   */
  public getPredictionHistory(agentId: string): SelfPrediction[] {
    return this.predictionHistory.get(agentId) ?? [];
  }

  /**
   * Get blind spots for agent
   */
  public getBlindSpots(agentId: string): BlindSpot[] {
    return this.blindSpots.get(agentId) ?? [];
  }

  /**
   * Get mental state for agent
   */
  public getMentalState(agentId: string): MentalState | undefined {
    return this.mentalStates.get(agentId);
  }

  /**
   * Get insights for agent
   */
  public getInsights(agentId: string): Insight[] {
    return this.insights.get(agentId) ?? [];
  }

  /**
   * Get optimization plans for agent
   */
  public getOptimizationPlans(agentId: string): OptimizationPlan[] {
    return this.optimizationPlans.get(agentId) ?? [];
  }

  /**
   * Get current statistics
   */
  public getStats(): SelfAwarenessStats {
    return { ...this.stats };
  }

  /**
   * Update configuration
   */
  public updateConfig(config: Partial<SelfAwarenessConfig>): void {
    this.config = { ...this.config, ...config };
    this.emit('config_updated', this.config);
  }

  /**
   * Get configuration
   */
  public getConfig(): SelfAwarenessConfig {
    return { ...this.config };
  }

  /**
   * Enable or disable self-awareness
   */
  public setEnabled(enabled: boolean): void {
    this.config.enabled = enabled;
    this.emit('enabled_changed', { enabled });
  }

  /**
   * Check if self-awareness is enabled
   */
  public isEnabled(): boolean {
    return this.config.enabled;
  }

  /**
   * Clear all data for an agent
   */
  public clearAgentData(agentId: string): void {
    this.selfModels.delete(agentId);
    this.predictionHistory.delete(agentId);
    this.performanceReports.delete(agentId);
    this.blindSpots.delete(agentId);
    this.mentalStates.delete(agentId);
    this.insights.delete(agentId);
    this.optimizationPlans.delete(agentId);
    this.updateAverageAwarenessLevel();
  }

  /**
   * Clear all data
   */
  public clearAllData(): void {
    this.selfModels.clear();
    this.predictionHistory.clear();
    this.performanceReports.clear();
    this.blindSpots.clear();
    this.mentalStates.clear();
    this.insights.clear();
    this.optimizationPlans.clear();
    this.stats.avgAwarenessLevel = 0;
  }
}

// ============================================================================
// FACTORY FUNCTION
// ============================================================================

/**
 * Create a self-awareness engine with default configuration
 */
export function createSelfAwarenessEngine(
  metaLearning?: MetaLearningEngine,
  config?: Partial<SelfAwarenessConfig>
): SelfAwarenessEngine {
  return new SelfAwarenessEngine(metaLearning, config);
}
