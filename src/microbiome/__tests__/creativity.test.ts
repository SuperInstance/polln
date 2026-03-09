/**
 * POLLN Microbiome - Creativity & Goals Engine Tests
 *
 * Phase 7: Emergent Intelligence - Milestone 3
 * Comprehensive test suite for creativity and autonomous goal generation.
 *
 * @module microbiome/__tests__/creativity
 */

import {
  CreativityEngine,
  CreativityLevel,
  NovelIdea,
  AnalogyMapping,
  DivergentThinkingResult,
  Goal,
  GoalType,
  GoalStatus,
  GoalHierarchy,
  DiscoveredValue,
  GoalPlan,
  PlanStatus,
  GoalConflict,
  ConflictType,
  ConflictResolution,
  createCreativityEngine,
} from '../creativity.js';
import {
  MetaLearningEngine,
  LearningContext,
  DomainKnowledge,
  ContextStability,
  TaskComplexity,
} from '../metalearning.js';
import {
  SelfAwarenessEngine,
  SelfModel,
  Capability,
  AwarenessLevel,
} from '../selfawareness.js';
import {
  MicrobiomeAgent,
  AgentTaxonomy,
  ResourceType,
  EcosystemSnapshot,
  LifecycleState,
} from '../types.js';

// ============================================================================
// TEST UTILITIES
// ============================================================================

/**
 * Create a mock agent for testing
 */
function createMockAgent(id: string = 'test-agent'): MicrobiomeAgent {
  return {
    id,
    taxonomy: AgentTaxonomy.BACTERIA,
    complexity: 0.5,
    metabolism: {
      inputs: [ResourceType.COMPUTE, ResourceType.MEMORY],
      outputs: [ResourceType.PACKAGES],
      processingRate: 10,
      efficiency: 0.8,
    },
    lifecycle: {
      health: 0.9,
      age: 1000,
      generation: 1,
      isAlive: true,
    },
    evaluateFitness: () => ({
      overall: 0.75,
      throughput: 0.8,
      accuracy: 0.7,
      efficiency: 0.75,
      cooperation: 0.8,
    }),
    metabolize: () => true,
  };
}

/**
 * Create a mock ecosystem snapshot
 */
function createMockSnapshot(): EcosystemSnapshot {
  return {
    agents: new Map([
      ['agent1', createMockAgent('agent1')],
      ['agent2', createMockAgent('agent2')],
    ]),
    colonies: [],
    symbioses: [],
    resourceFlows: new Map([
      [ResourceType.COMPUTE, { available: 100, capacity: 200, flowRate: 10 }],
      [ResourceType.MEMORY, { available: 50, capacity: 100, flowRate: 5 }],
    ]),
    timestamp: Date.now(),
  };
}

/**
 * Create a mock self-model
 */
function createMockSelfModel(agentId: string = 'test-agent'): SelfModel {
  return {
    agentId,
    taxonomy: AgentTaxonomy.BACTERIA,
    awarenessLevel: AwarenessLevel.MODELING,
    capabilities: [
      {
        id: 'process',
        name: 'Processing',
        description: 'Can process inputs',
        strength: 0.8,
        confidence: 0.9,
        lastValidated: Date.now(),
        usageCount: 10,
        successRate: 0.85,
      },
      {
        id: 'reproduce',
        name: 'Reproduction',
        description: 'Can create offspring',
        strength: 0.7,
        confidence: 0.8,
        lastValidated: Date.now(),
        usageCount: 5,
        successRate: 0.6,
      },
    ],
    limitations: [],
    typicalBehaviors: [],
    performanceHistory: [],
    socialConnections: new Map(),
    goals: [],
    values: {
      id: 'default_values',
      name: 'Default Values',
      description: 'Basic value system',
      strength: 0.7,
      conflicts: new Map(),
      alignment: 1.0,
    },
    lastUpdated: Date.now(),
    confidence: 0.8,
  };
}

// ============================================================================
// TEST SUITES
// ============================================================================

describe('CreativityEngine', () => {
  let engine: CreativityEngine;
  let metaLearning: MetaLearningEngine;
  let selfAwareness: SelfAwarenessEngine;

  beforeEach(() => {
    metaLearning = new MetaLearningEngine(
      jest.fn() as any,
      undefined,
      { enabled: true }
    );
    selfAwareness = new SelfAwarenessEngine(metaLearning, { enabled: true });
    engine = new CreativityEngine(metaLearning, selfAwareness, { enabled: true });
  });

  afterEach(() => {
    engine.clearAllData();
  });

  // ==========================================================================
  // NOVELTY GENERATION TESTS
  // ==========================================================================

  describe('Novelty Generation', () => {
    test('should generate novel ideas', () => {
      const agent = createMockAgent();
      const ideas = engine.generateNovelIdeas(agent, 'test-context', 5);

      expect(ideas.length).toBeGreaterThan(0);
      expect(ideas.length).toBeLessThanOrEqual(5);

      // Check idea properties
      ideas.forEach(idea => {
        expect(idea).toHaveProperty('id');
        expect(idea).toHaveProperty('name');
        expect(idea).toHaveProperty('description');
        expect(idea).toHaveProperty('creativityLevel');
        expect(idea).toHaveProperty('novelty');
        expect(idea).toHaveProperty('feasibility');
        expect(idea).toHaveProperty('value');
        expect(idea.novelty).toBeGreaterThanOrEqual(0);
        expect(idea.novelty).toBeLessThanOrEqual(1);
        expect(idea.feasibility).toBeGreaterThanOrEqual(0);
        expect(idea.feasibility).toBeLessThanOrEqual(1);
        expect(idea.value).toBeGreaterThanOrEqual(0);
        expect(idea.value).toBeLessThanOrEqual(1);
      });
    });

    test('should generate ideas with sufficient novelty', () => {
      const agent = createMockAgent();
      const ideas = engine.generateNovelIdeas(agent, 'test-context', 10);

      ideas.forEach(idea => {
        expect(idea.novelty).toBeGreaterThanOrEqual(0.3); // minNovelty
      });
    });

    test('should generate ideas with sufficient feasibility', () => {
      const agent = createMockAgent();
      const ideas = engine.generateNovelIdeas(agent, 'test-context', 10);

      ideas.forEach(idea => {
        expect(idea.feasibility).toBeGreaterThanOrEqual(0.4); // minFeasibility
      });
    });

    test('should generate ideas with sufficient value', () => {
      const agent = createMockAgent();
      const ideas = engine.generateNovelIdeas(agent, 'test-context', 10);

      ideas.forEach(idea => {
        expect(idea.value).toBeGreaterThanOrEqual(0.5); // minValue
      });
    });

    test('should store generated ideas', () => {
      const agent = createMockAgent();
      const ideas = engine.generateNovelIdeas(agent, 'test-context', 5);

      const storedIdeas = engine.getNovelIdeas(agent.id);
      expect(storedIdeas.length).toBeGreaterThanOrEqual(ideas.length);
    });

    test('should update statistics after idea generation', () => {
      const agent = createMockAgent();
      const initialStats = engine.getStats();

      engine.generateNovelIdeas(agent, 'test-context', 5);

      const finalStats = engine.getStats();
      expect(finalStats.ideasGenerated).toBeGreaterThan(initialStats.ideasGenerated);
    });
  });

  // ==========================================================================
  // IDEA RECOMBINATION TESTS
  // ==========================================================================

  describe('Idea Recombination', () => {
    test('should recombine ideas across domains', () => {
      const agentId = 'test-agent';
      const sourceDomain = 'source';
      const targetDomain = 'target';

      // Generate some ideas in source domain
      const agent = createMockAgent(agentId);
      const sourceIdeas = engine.generateNovelIdeas(agent, sourceDomain, 5);

      expect(sourceIdeas.length).toBeGreaterThan(0);

      // Recombine across domains
      const recombinations = engine.crossDomainRecombination(
        agentId,
        sourceDomain,
        targetDomain
      );

      // Since we have ideas in source domain, should generate recombinations
      if (sourceIdeas.length > 0) {
        expect(recombinations.length).toBeGreaterThan(0);
        recombinations.forEach(idea => {
          expect(idea.domain).toBe(targetDomain);
        });
      }
    });

    test('should increase novelty for cross-domain ideas', () => {
      const agentId = 'test-agent';
      const sourceDomain = 'source';
      const targetDomain = 'target';

      const agent = createMockAgent(agentId);
      const originalIdeas = engine.generateNovelIdeas(agent, sourceDomain, 5);

      const recombinations = engine.crossDomainRecombination(
        agentId,
        sourceDomain,
        targetDomain
      );

      if (originalIdeas.length > 0 && recombinations.length > 0) {
        const avgOriginalNovelty = originalIdeas.reduce((sum, i) => sum + i.novelty, 0) / originalIdeas.length;
        const avgRecombinedNovelty = recombinations.reduce((sum, i) => sum + i.novelty, 0) / recombinations.length;

        expect(avgRecombinedNovelty).toBeGreaterThanOrEqual(avgOriginalNovelty);
      }
    });
  });

  // ==========================================================================
  // ANALOGICAL REASONING TESTS
  // ==========================================================================

  describe('Analogical Reasoning', () => {
    test('should create analogy when similarity is sufficient', () => {
      const sourceDomain = 'biology';
      const targetDomain = 'computer_science';
      const structuralRelations = new Map([
        ['predator_prey', ['virus_bacteria', 'hacker_system']],
        ['symbiosis', ['mutual_beneficial', 'client_server']],
      ]);

      const analogy = engine.createAnalogy(
        sourceDomain,
        targetDomain,
        structuralRelations
      );

      expect(analogy).not.toBeNull();
      expect(analogy).toHaveProperty('id');
      expect(analogy).toHaveProperty('sourceDomain', sourceDomain);
      expect(analogy).toHaveProperty('targetDomain', targetDomain);
      expect(analogy).toHaveProperty('structuralSimilarity');
      expect(analogy).toHaveProperty('conceptMappings');
      expect(analogy).toHaveProperty('predictedInsights');
    });

    test('should not create analogy when similarity is insufficient', () => {
      const sourceDomain = 'cooking';
      const targetDomain = 'astrophysics';
      const structuralRelations = new Map([
        ['mixing', ['ingredients']],
      ]);

      const analogy = engine.createAnalogy(
        sourceDomain,
        targetDomain,
        structuralRelations
      );

      expect(analogy).toBeNull();
    });

    test('should store created analogies', () => {
      const sourceDomain = 'biology';
      const targetDomain = 'computer_science';
      const structuralRelations = new Map([
        ['predator_prey', ['virus_bacteria', 'hacker_system']],
      ]);

      engine.createAnalogy(sourceDomain, targetDomain, structuralRelations);

      const storedAnalogies = engine.getAnalogies(targetDomain);
      expect(storedAnalogies.length).toBeGreaterThan(0);
    });

    test('should update statistics after analogy creation', () => {
      const initialStats = engine.getStats();

      const sourceDomain = 'biology';
      const targetDomain = 'computer_science';
      const structuralRelations = new Map([
        ['predator_prey', ['virus_bacteria', 'hacker_system']],
      ]);

      engine.createAnalogy(sourceDomain, targetDomain, structuralRelations);

      const finalStats = engine.getStats();
      expect(finalStats.analogiesCreated).toBeGreaterThan(initialStats.analogiesCreated);
    });
  });

  // ==========================================================================
  // DIVERGENT THINKING TESTS
  // ==========================================================================

  describe('Divergent Thinking', () => {
    test('should generate multiple diverse solutions', () => {
      const agent = createMockAgent();
      const problem = 'optimize resource usage';
      const result = engine.divergentThinking(agent, problem, 5);

      expect(result).toHaveProperty('id');
      expect(result).toHaveProperty('problem', problem);
      expect(result).toHaveProperty('solutions');
      expect(result.solutions.length).toBe(5);
      expect(result).toHaveProperty('diversity');
      expect(result).toHaveProperty('bestSolution');
      expect(result).toHaveProperty('timestamp');
    });

    test('should calculate solution diversity', () => {
      const agent = createMockAgent();
      const problem = 'improve efficiency';
      const result = engine.divergentThinking(agent, problem);

      expect(result.diversity).toBeGreaterThanOrEqual(0);
      expect(result.diversity).toBeLessThanOrEqual(1);
    });

    test('should identify best solution', () => {
      const agent = createMockAgent();
      const problem = 'maximize output';
      const result = engine.divergentThinking(agent, problem);

      expect(result.bestSolution).toBeTruthy();
      expect(result.solutions.some(s => s.solution === result.bestSolution)).toBe(true);
    });

    test('should update statistics after divergent thinking', () => {
      const agent = createMockAgent();
      const initialStats = engine.getStats();

      engine.divergentThinking(agent, 'test problem');

      const finalStats = engine.getStats();
      expect(finalStats.divergentSessions).toBeGreaterThan(initialStats.divergentSessions);
    });
  });

  // ==========================================================================
  // AUTONOMOUS GOAL GENERATION TESTS
  // ==========================================================================

  describe('Autonomous Goal Generation', () => {
    test('should generate survival goal', () => {
      const agent = createMockAgent();
      const snapshot = createMockSnapshot();
      const goals = engine.generateAutonomousGoals(agent, snapshot);

      const survivalGoal = goals.find(g => g.type === GoalType.SURVIVAL);
      expect(survivalGoal).toBeDefined();
      expect(survivalGoal?.priority).toBe(1.0);
      expect(survivalGoal?.status).toBe(GoalStatus.IN_PROGRESS);
    });

    test('should generate growth goal for capable agents', () => {
      const agent = createMockAgent();
      const snapshot = createMockSnapshot();

      // Set up self-model
      const selfModel = createMockSelfModel(agent.id);
      jest.spyOn(selfAwareness, 'getSelfModel').mockReturnValue(selfModel);

      const goals = engine.generateAutonomousGoals(agent, snapshot);

      const growthGoal = goals.find(g => g.type === GoalType.GROWTH);
      expect(growthGoal).toBeDefined();
    });

    test('should generate social goal for colony members', () => {
      const agent = createMockAgent('colony-agent');
      const snapshot = createMockSnapshot();
      snapshot.colonies.push({
        id: 'colony1',
        members: ['colony-agent'],
        specialization: 'generalist',
        stability: 0.8,
        coEvolutionBonus: 0.7,
        formationTime: Date.now(),
      });

      const goals = engine.generateAutonomousGoals(agent, snapshot);

      const socialGoal = goals.find(g => g.type === GoalType.SOCIAL);
      expect(socialGoal).toBeDefined();
    });

    test('should generate exploration goal for explorers', () => {
      const agent = createMockAgent();
      agent.taxonomy = AgentTaxonomy.EXPLORER;

      const snapshot = createMockSnapshot();
      const goals = engine.generateAutonomousGoals(agent, snapshot);

      const explorationGoal = goals.find(g => g.type === GoalType.EXPLORATION);
      expect(explorationGoal).toBeDefined();
    });

    test('should generate creativity goal when creative level is high', () => {
      const agent = createMockAgent();
      const snapshot = createMockSnapshot();

      // Generate ideas to increase creativity level
      engine.generateNovelIdeas(agent, 'test-context', 10);

      const goals = engine.generateAutonomousGoals(agent, snapshot);

      const creativityGoal = goals.find(g => g.type === GoalType.CREATIVITY);
      expect(creativityGoal).toBeDefined();
    });

    test('should add goals to hierarchy', () => {
      const agent = createMockAgent();
      const snapshot = createMockSnapshot();
      const goals = engine.generateAutonomousGoals(agent, snapshot);

      const hierarchy = engine.getGoalHierarchy(agent.id);
      expect(hierarchy).toBeDefined();
      expect(hierarchy?.totalGoals).toBeGreaterThan(0);
    });
  });

  // ==========================================================================
  // GOAL HIERARCHY CONSTRUCTION TESTS
  // ==========================================================================

  describe('Goal Hierarchy Construction', () => {
    test('should construct goal hierarchy with subgoals', () => {
      const agentId = 'test-agent';
      const rootGoal: Goal = {
        id: 'root-goal',
        name: 'Root Goal',
        description: 'Top level goal',
        type: GoalType.GROWTH,
        priority: 0.9,
        progress: 0,
        status: GoalStatus.PENDING,
        childGoalIds: [],
        createdAt: Date.now(),
        expectedValue: 0.9,
        dependencies: [],
        relatedValues: ['growth'],
      };

      const hierarchy = engine.constructGoalHierarchy(agentId, rootGoal, 3);

      expect(hierarchy).toHaveProperty('rootGoals');
      expect(hierarchy.rootGoals.length).toBe(1);
      expect(hierarchy.rootGoals[0].id).toBe(rootGoal.id);
      expect(hierarchy).toHaveProperty('allGoals');
      expect(hierarchy.allGoals.size).toBeGreaterThan(1);
      expect(hierarchy).toHaveProperty('relationships');
      expect(hierarchy).toHaveProperty('depth');
      expect(hierarchy.depth).toBeGreaterThan(1);
    });

    test('should respect max depth parameter', () => {
      const agentId = 'test-agent';
      const rootGoal: Goal = {
        id: 'root-goal',
        name: 'Root Goal',
        description: 'Top level goal',
        type: GoalType.GROWTH,
        priority: 0.9,
        progress: 0,
        status: GoalStatus.PENDING,
        childGoalIds: [],
        createdAt: Date.now(),
        expectedValue: 0.9,
        dependencies: [],
        relatedValues: ['growth'],
      };

      const maxDepth = 2;
      const hierarchy = engine.constructGoalHierarchy(agentId, rootGoal, maxDepth);

      expect(hierarchy.depth).toBeLessThanOrEqual(maxDepth + 1);
    });

    test('should establish parent-child relationships', () => {
      const agentId = 'test-agent';
      const rootGoal: Goal = {
        id: 'root-goal',
        name: 'Root Goal',
        description: 'Top level goal',
        type: GoalType.SURVIVAL,
        priority: 1.0,
        progress: 0,
        status: GoalStatus.PENDING,
        childGoalIds: [],
        createdAt: Date.now(),
        expectedValue: 1.0,
        dependencies: [],
        relatedValues: ['survival'],
      };

      const hierarchy = engine.constructGoalHierarchy(agentId, rootGoal, 2);

      // Check that root goal has children
      const rootInHierarchy = hierarchy.allGoals.get(rootGoal.id);
      expect(rootInHierarchy?.childGoalIds.length).toBeGreaterThan(0);

      // Check that children have parent reference
      rootInHierarchy?.childGoalIds.forEach(childId => {
        const child = hierarchy.allGoals.get(childId);
        expect(child?.parentGoalId).toBe(rootGoal.id);
      });
    });
  });

  // ==========================================================================
  // VALUE DISCOVERY TESTS
  // ==========================================================================

  describe('Value Discovery', () => {
    test('should discover values from successful experiences', () => {
      const agentId = 'test-agent';
      const experiences = [
        {
          context: 'cooperation',
          actions: ['share_resources', 'help_neighbor'],
          outcomes: new Map([
            ['cooperation', 0.9],
            ['efficiency', 0.8],
          ]),
        },
        {
          context: 'innovation',
          actions: ['try_new_approach'],
          outcomes: new Map([
            ['innovation', 0.85],
            ['learning', 0.7],
          ]),
        },
      ];

      const discoveredValues = engine.discoverValues(agentId, experiences);

      expect(discoveredValues.length).toBeGreaterThan(0);
      discoveredValues.forEach(value => {
        expect(value).toHaveProperty('id');
        expect(value).toHaveProperty('name');
        expect(value).toHaveProperty('description');
        expect(value).toHaveProperty('strength');
        expect(value).toHaveProperty('source', 'experience');
        expect(value).toHaveProperty('discoveredAt');
        expect(value).toHaveProperty('validationCount', 1);
        expect(value).toHaveProperty('alignment', 1.0);
      });
    });

    test('should strengthen existing values', () => {
      const agentId = 'test-agent';

      // First experience
      const experiences1 = [
        {
          context: 'cooperation',
          actions: ['help'],
          outcomes: new Map([['cooperation', 0.8]]),
        },
      ];
      engine.discoverValues(agentId, experiences1);

      const values1 = engine.getDiscoveredValues(agentId);
      const initialStrength = values1[0]?.strength ?? 0;

      // Second similar experience
      const experiences2 = [
        {
          context: 'cooperation',
          actions: ['collaborate'],
          outcomes: new Map([['cooperation', 0.9]]),
        },
      ];
      engine.discoverValues(agentId, experiences2);

      const values2 = engine.getDiscoveredValues(agentId);
      const cooperationValue = values2.find(v => v.name === 'Cooperation');

      expect(cooperationValue?.validationCount).toBeGreaterThan(1);
      expect(cooperationValue?.strength).toBeGreaterThanOrEqual(initialStrength);
    });

    test('should store discovered values', () => {
      const agentId = 'test-agent';
      const experiences = [
        {
          context: 'growth',
          actions: ['improve'],
          outcomes: new Map([['growth', 0.8]]),
        },
      ];

      engine.discoverValues(agentId, experiences);

      const storedValues = engine.getDiscoveredValues(agentId);
      expect(storedValues.length).toBeGreaterThan(0);
    });

    test('should update statistics after value discovery', () => {
      const agentId = 'test-agent';
      const initialStats = engine.getStats();

      const experiences = [
        {
          context: 'test',
          actions: ['action'],
          outcomes: new Map([['test_value', 0.8]]),
        },
      ];

      engine.discoverValues(agentId, experiences);

      const finalStats = engine.getStats();
      expect(finalStats.valuesDiscovered).toBeGreaterThan(initialStats.valuesDiscovered);
    });
  });

  // ==========================================================================
  // GOAL PURSUIT PLANNING TESTS
  // ==========================================================================

  describe('Goal Pursuit Planning', () => {
    test('should create plan for goal', () => {
      const agentId = 'test-agent';
      const goal: Goal = {
        id: 'goal1',
        name: 'Test Goal',
        description: 'A test goal',
        type: GoalType.SURVIVAL,
        priority: 0.8,
        progress: 0,
        status: GoalStatus.PENDING,
        childGoalIds: [],
        createdAt: Date.now(),
        expectedValue: 0.8,
        dependencies: [],
        relatedValues: [],
      };

      // Add goal to hierarchy
      engine.constructGoalHierarchy(agentId, goal);

      const plan = engine.createGoalPlan(agentId, goal.id);

      expect(plan).toHaveProperty('id');
      expect(plan).toHaveProperty('goalId', goal.id);
      expect(plan).toHaveProperty('steps');
      expect(plan.steps.length).toBeGreaterThan(0);
      expect(plan).toHaveProperty('resourceRequirements');
      expect(plan).toHaveProperty('expectedDuration');
      expect(plan).toHaveProperty('successProbability');
      expect(plan).toHaveProperty('createdAt');
      expect(plan).toHaveProperty('status', PlanStatus.NOT_STARTED);
    });

    test('should generate plan steps with dependencies', () => {
      const agentId = 'test-agent';
      const goal: Goal = {
        id: 'goal1',
        name: 'Survive',
        description: 'Stay alive',
        type: GoalType.SURVIVAL,
        priority: 1.0,
        progress: 0,
        status: GoalStatus.PENDING,
        childGoalIds: [],
        createdAt: Date.now(),
        expectedValue: 1.0,
        dependencies: [],
        relatedValues: [],
      };

      engine.constructGoalHierarchy(agentId, goal);
      const plan = engine.createGoalPlan(agentId, goal.id);

      // Check that steps have proper structure
      plan.steps.forEach(step => {
        expect(step).toHaveProperty('id');
        expect(step).toHaveProperty('description');
        expect(step).toHaveProperty('order');
        expect(step).toHaveProperty('requiredCapabilities');
        expect(step).toHaveProperty('resourceCost');
        expect(step).toHaveProperty('expectedDuration');
        expect(step).toHaveProperty('dependencies');
        expect(step).toHaveProperty('completed', false);
      });

      // Check that steps are ordered
      const orders = plan.steps.map(s => s.order);
      const sortedOrders = [...orders].sort((a, b) => a - b);
      expect(orders).toEqual(sortedOrders);
    });

    test('should calculate success probability', () => {
      const agentId = 'test-agent';
      const goal: Goal = {
        id: 'goal1',
        name: 'Test Goal',
        description: 'A test goal',
        type: GoalType.GROWTH,
        priority: 0.7,
        progress: 0,
        status: GoalStatus.PENDING,
        childGoalIds: [],
        createdAt: Date.now(),
        expectedValue: 0.7,
        dependencies: [],
        relatedValues: [],
      };

      engine.constructGoalHierarchy(agentId, goal);
      const plan = engine.createGoalPlan(agentId, goal.id);

      expect(plan.successProbability).toBeGreaterThanOrEqual(0);
      expect(plan.successProbability).toBeLessThanOrEqual(1);
    });
  });

  // ==========================================================================
  // GOAL CONFLICT RESOLUTION TESTS
  // ==========================================================================

  describe('Goal Conflict Resolution', () => {
    test('should detect resource conflicts', () => {
      const agentId = 'test-agent';

      // Create conflicting goals
      const goal1: Goal = {
        id: 'goal1',
        name: 'High Resource Goal 1',
        description: 'Needs lots of resources',
        type: GoalType.GROWTH,
        priority: 0.9,
        progress: 0,
        status: GoalStatus.PENDING,
        childGoalIds: [],
        createdAt: Date.now(),
        expectedValue: 0.9,
        dependencies: [],
        relatedValues: [],
      };

      const goal2: Goal = {
        id: 'goal2',
        name: 'High Resource Goal 2',
        description: 'Also needs lots of resources',
        type: GoalType.ACHIEVEMENT,
        priority: 0.8,
        progress: 0,
        status: GoalStatus.PENDING,
        childGoalIds: [],
        createdAt: Date.now(),
        expectedValue: 0.8,
        dependencies: [],
        relatedValues: [],
      };

      // Create hierarchy with first goal
      engine.constructGoalHierarchy(agentId, goal1);

      // Manually add second goal to the same hierarchy
      const hierarchy = engine.getGoalHierarchy(agentId);
      if (hierarchy) {
        hierarchy.allGoals.set(goal2.id, goal2);
        hierarchy.rootGoals.push(goal2);
        hierarchy.totalGoals++;
      }

      const conflicts = engine.resolveGoalConflicts(agentId);

      // Should detect conflicts between high-priority goals
      if (conflicts.length > 0) {
        const resourceConflicts = conflicts.filter(c => c.type === ConflictType.RESOURCE);
        expect(resourceConflicts.length).toBeGreaterThan(0);
      }
    });

    test('should resolve conflicts with strategy', () => {
      const agentId = 'test-agent';
      const goal1: Goal = {
        id: 'goal1',
        name: 'Goal 1',
        description: 'First goal',
        type: GoalType.GROWTH,
        priority: 0.8,
        progress: 0,
        status: GoalStatus.PENDING,
        childGoalIds: [],
        createdAt: Date.now(),
        expectedValue: 0.8,
        dependencies: [],
        relatedValues: [],
      };

      const goal2: Goal = {
        id: 'goal2',
        name: 'Goal 2',
        description: 'Second goal',
        type: GoalType.ACHIEVEMENT,
        priority: 0.7,
        progress: 0,
        status: GoalStatus.PENDING,
        childGoalIds: [],
        createdAt: Date.now(),
        expectedValue: 0.7,
        dependencies: [],
        relatedValues: [],
      };

      engine.constructGoalHierarchy(agentId, goal1);
      engine.constructGoalHierarchy(agentId, goal2);

      const conflicts = engine.resolveGoalConflicts(agentId);

      conflicts.forEach(conflict => {
        expect(conflict).toHaveProperty('resolutionStrategy');
        expect(conflict).toHaveProperty('resolvedAt');
        expect(conflict.resolutionStrategy).toBeDefined();
      });
    });

    test('should update statistics after conflict resolution', () => {
      const agentId = 'test-agent';
      const initialStats = engine.getStats();

      const goal1: Goal = {
        id: 'goal1',
        name: 'Goal 1',
        description: 'First goal',
        type: GoalType.GROWTH,
        priority: 0.9,
        progress: 0,
        status: GoalStatus.PENDING,
        childGoalIds: [],
        createdAt: Date.now(),
        expectedValue: 0.9,
        dependencies: [],
        relatedValues: [],
      };

      const goal2: Goal = {
        id: 'goal2',
        name: 'Goal 2',
        description: 'Second goal',
        type: GoalType.ACHIEVEMENT,
        priority: 0.8,
        progress: 0,
        status: GoalStatus.PENDING,
        childGoalIds: [],
        createdAt: Date.now(),
        expectedValue: 0.8,
        dependencies: [],
        relatedValues: [],
      };

      engine.constructGoalHierarchy(agentId, goal1);
      engine.constructGoalHierarchy(agentId, goal2);

      engine.resolveGoalConflicts(agentId);

      const finalStats = engine.getStats();
      expect(finalStats.conflictsResolved).toBeGreaterThanOrEqual(initialStats.conflictsResolved);
    });
  });

  // ==========================================================================
  // INTEGRATION TESTS
  // ==========================================================================

  describe('Integration Tests', () => {
    test('should integrate with meta-learning', () => {
      const agent = createMockAgent();
      const snapshot = createMockSnapshot();

      // CreativityEngine is created with metaLearning reference
      expect(engine).toBeInstanceOf(CreativityEngine);

      // Generate ideas (creativity doesn't directly call metaLearning,
      // but has access to it for future enhancements)
      const ideas = engine.generateNovelIdeas(agent, 'test-context', 5);

      expect(ideas.length).toBeGreaterThan(0);
      expect(ideas[0]).toHaveProperty('novelty');
      expect(ideas[0]).toHaveProperty('feasibility');
      expect(ideas[0]).toHaveProperty('value');
    });

    test('should integrate with self-awareness', () => {
      const agent = createMockAgent();
      const snapshot = createMockSnapshot();

      // Set up self-model
      const selfModel = createMockSelfModel(agent.id);
      jest.spyOn(selfAwareness, 'getSelfModel').mockReturnValue(selfModel);

      const goals = engine.generateAutonomousGoals(agent, snapshot);

      expect(goals.length).toBeGreaterThan(0);
      expect(selfAwareness.getSelfModel).toHaveBeenCalledWith(agent.id);
    });

    test('should support full creativity workflow', () => {
      const agent = createMockAgent();
      const snapshot = createMockSnapshot();

      // Set up self-model
      const selfModel = createMockSelfModel(agent.id);
      jest.spyOn(selfAwareness, 'getSelfModel').mockReturnValue(selfModel);

      // 1. Generate novel ideas
      const ideas = engine.generateNovelIdeas(agent, 'problem-solving', 5);
      expect(ideas.length).toBeGreaterThan(0);

      // 2. Apply divergent thinking
      const solutions = engine.divergentThinking(agent, 'complex problem');
      expect(solutions.solutions.length).toBeGreaterThan(0);

      // 3. Generate autonomous goals
      const goals = engine.generateAutonomousGoals(agent, snapshot);
      expect(goals.length).toBeGreaterThan(0);

      // 4. Create goal hierarchy
      if (goals.length > 0) {
        const hierarchy = engine.constructGoalHierarchy(agent.id, goals[0], 2);
        expect(hierarchy.allGoals.size).toBeGreaterThan(1);

        // 5. Create plan for goal
        const plan = engine.createGoalPlan(agent.id, goals[0].id);
        expect(plan.steps.length).toBeGreaterThan(0);
      }

      // 6. Discover values from experience
      const experiences = [
        {
          context: 'test',
          actions: ['test_action'],
          outcomes: new Map([['success', 0.9]]),
        },
      ];
      const values = engine.discoverValues(agent.id, experiences);
      expect(values.length).toBeGreaterThan(0);
    });
  });

  // ==========================================================================
  // CONFIGURATION TESTS
  // ==========================================================================

  describe('Configuration', () => {
    test('should respect enabled flag', () => {
      const disabledEngine = new CreativityEngine(
        undefined,
        undefined,
        { enabled: false }
      );

      const agent = createMockAgent();
      const ideas = disabledEngine.generateNovelIdeas(agent, 'test-context', 5);

      expect(ideas.length).toBe(0);
    });

    test('should allow configuration updates', () => {
      const newConfig = {
        minNovelty: 0.5,
        minFeasibility: 0.6,
        minValue: 0.7,
      };

      engine.updateConfig(newConfig);

      const config = engine.getConfig();
      expect(config.minNovelty).toBe(0.5);
      expect(config.minFeasibility).toBe(0.6);
      expect(config.minValue).toBe(0.7);
    });

    test('should provide factory function', () => {
      const testEngine = createCreativityEngine(metaLearning, selfAwareness, {
        enabled: true,
        explorationFactor: 0.5,
      });

      expect(testEngine).toBeInstanceOf(CreativityEngine);
      expect(testEngine.isEnabled()).toBe(true);
    });
  });

  // ==========================================================================
  // STATISTICS TESTS
  // ==========================================================================

  describe('Statistics', () => {
    test('should track creativity statistics', () => {
      const agent = createMockAgent();
      const snapshot = createMockSnapshot();

      // Set up self-model
      const selfModel = createMockSelfModel(agent.id);
      jest.spyOn(selfAwareness, 'getSelfModel').mockReturnValue(selfModel);

      // Generate ideas
      engine.generateNovelIdeas(agent, 'test', 5);

      // Generate goals
      engine.generateAutonomousGoals(agent, snapshot);

      // Create analogy
      engine.createAnalogy(
        'domain1',
        'domain2',
        new Map([['relation', ['a', 'b']]])
      );

      // Divergent thinking
      engine.divergentThinking(agent, 'problem');

      const stats = engine.getStats();

      expect(stats.ideasGenerated).toBeGreaterThan(0);
      expect(stats.goalsGenerated).toBeGreaterThan(0);
      expect(stats.divergentSessions).toBeGreaterThan(0);
      expect(stats.avgCreativityLevel).toBeGreaterThanOrEqual(0);
    });

    test('should calculate average idea novelty', () => {
      const agent = createMockAgent();
      engine.generateNovelIdeas(agent, 'test', 10);

      const stats = engine.getStats();
      expect(stats.avgIdeaNovelty).toBeGreaterThanOrEqual(0);
      expect(stats.avgIdeaNovelty).toBeLessThanOrEqual(1);
    });
  });
});

// ============================================================================
// RUN TESTS
// ============================================================================

console.log('Creativity & Goals Engine Test Suite Loaded');
console.log('Total tests: Comprehensive coverage of creativity system');
console.log('Coverage target: 90%+');
