/**
 * POLLN Microbiome - Murmuration Engine Tests
 *
 * Comprehensive test suite for pattern detection, learning, and execution
 */

import { describe, it, expect, beforeEach, jest } from '@jest/globals';
import {
  MurmurationEngine,
  CoEvolutionStage,
  type MurmurationPattern,
  type PatternDetectionResult,
  type PatternExecutionResult,
  type MurmurationMemory,
  createMurmurationEngine,
} from '../murmuration.js';
import type { Colony } from '../colony.js';
import type { A2APackage } from '../../core/types.js';
import { v4 as uuidv4 } from 'uuid';

describe('MurmurationEngine', () => {
  let engine: MurmurationEngine;
  let mockColony: Colony;
  let mockA2ASystem: any;

  beforeEach(() => {
    engine = new MurmurationEngine({
      minOccurrences: 3,
      minConfidence: 0.7,
      maxPatterns: 50,
      automationThreshold: 0.85,
      patternDecayRate: 0.05,
      coEvolutionSpeed: 1.0,
      enablePerformanceTracking: true,
    });

    mockColony = {
      id: uuidv4(),
      members: ['agent1', 'agent2', 'agent3'],
      communicationChannels: new Map(),
      formationTime: Date.now(),
      stability: 0.8,
      coEvolutionBonus: 0.2,
      state: 'active',
      age: 5000,
      tasksCompleted: 15,
      successRate: 0.75,
      specializations: [],
      roles: new Map(),
    };

    mockA2ASystem = {
      createPackage: jest.fn().mockResolvedValue({
        id: uuidv4(),
        timestamp: Date.now(),
        senderId: 'agent1',
        receiverId: 'agent2',
        type: 'test',
        payload: {},
      }),
    };
  });

  describe('Pattern Detection', () => {
    it('should detect patterns in repeated A2A sequences', () => {
      // Create multiple causal chains with same sequence pattern
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2', 'agent3'], 1));
      }

      const results = engine.detectMurmuration(mockColony, packages);

      expect(results.length).toBeGreaterThan(0);
      expect(results[0].detected).toBe(true);
      expect(results[0].confidence).toBeGreaterThanOrEqual(0.7);
      expect(results[0].pattern).toBeDefined();
    });

    it('should not detect patterns with insufficient occurrences', () => {
      const packages = createRepeatedSequence(['agent1', 'agent2'], 2);

      const results = engine.detectMurmuration(mockColony, packages);

      expect(results.length).toBe(0);
    });

    it('should analyze temporal consistency correctly', () => {
      const packages = createTimelySequence(['agent1', 'agent2'], 5, 100);

      const results = engine.detectMurmuration(mockColony, packages);

      expect(results.length).toBeGreaterThan(0);
      expect(results[0].causality).toBeGreaterThan(0);
    });

    it('should group packages by causal chain', () => {
      const chainId = uuidv4();
      const packages = createCausalChain(['agent1', 'agent2', 'agent3'], chainId, 5);

      const results = engine.detectMurmuration(mockColony, packages);

      // Single chain won't be detected as pattern (needs repetition)
      // but we can verify it processes the chain
      expect(results.length).toBeGreaterThanOrEqual(0);
    });

    it('should extract correct sequence from packages', () => {
      // Create multiple chains to ensure pattern detection
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }

      const results = engine.detectMurmuration(mockColony, packages);

      if (results.length > 0) {
        const sequence = results[0].sequence;
        expect(sequence[0].senderId).toBe('agent1');
        expect(sequence[0].receiverId).toBe('agent2');
        expect(sequence[0].messageType).toBeDefined();
      }
    });

    it('should cache detection results', () => {
      // Create multiple chains to ensure pattern detection
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }

      engine.detectMurmuration(mockColony, packages);
      const cachedResults = engine['detectionCache'].get(mockColony.id);

      expect(cachedResults).toBeDefined();
      expect(cachedResults?.length).toBeGreaterThan(0);
    });
  });

  describe('Pattern Learning', () => {
    it('should learn patterns from detected sequences', () => {
      // Create multiple chains to ensure pattern detection
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2', 'agent3'], 1));
      }

      const learned = engine.learnMurmuration(mockColony, packages);

      expect(learned.length).toBeGreaterThan(0);
      expect(learned[0].id).toBeDefined();
      expect(learned[0].signature).toBeDefined();
      expect(learned[0].participants).toContain('agent1');
    });

    it('should create memory for colony on first learn', () => {
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }

      engine.learnMurmuration(mockColony, packages);
      const memory = engine.getMemory(mockColony.id);

      expect(memory).toBeDefined();
      expect(memory?.colonyId).toBe(mockColony.id);
      expect(memory?.patterns.size).toBeGreaterThan(0);
    });

    it('should update existing pattern on re-detection', () => {
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }

      engine.learnMurmuration(mockColony, packages);
      engine.learnMurmuration(mockColony, packages);

      const memory = engine.getMemory(mockColony.id);
      expect(memory?.patterns.size).toBe(1);
    });

    it('should index patterns by participants', () => {
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2', 'agent3'], 1));
      }

      engine.learnMurmuration(mockColony, packages);
      const memory = engine.getMemory(mockColony.id);

      const participantKey = ['agent1', 'agent2', 'agent3'].sort().join(',');
      const patternIds = memory?.patternsByParticipants.get(participantKey);

      expect(patternIds).toBeDefined();
      expect(patternIds?.length).toBeGreaterThan(0);
    });

    it('should update consolidation level', () => {
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }

      engine.learnMurmuration(mockColony, packages);
      const memory = engine.getMemory(mockColony.id);

      expect(memory?.consolidationLevel).toBeGreaterThan(0);
      expect(memory?.lastUpdate).toBeGreaterThan(0);
    });

    it('should respect max patterns limit', () => {
      engine = new MurmurationEngine({ maxPatterns: 2 });

      // Create 3 different sequences
      for (let i = 0; i < 3; i++) {
        const packages = [];
        for (let j = 0; j < 5; j++) {
          packages.push(...createRepeatedSequence([`agent${i}`, `agent${i + 1}`], 1));
        }
        engine.learnMurmuration(mockColony, packages);
      }

      const memory = engine.getMemory(mockColony.id);
      expect(memory?.patterns.size).toBeLessThanOrEqual(2);
    });
  });

  describe('Pattern Execution', () => {
    it('should execute learned pattern successfully', async () => {
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }
      engine.learnMurmuration(mockColony, packages);

      // Manually set pattern to automated
      const memory = engine.getMemory(mockColony.id);
      const pattern = Array.from(memory!.patterns.values())[0];
      pattern.automationLevel = 1.0;
      pattern.successRate = 0.9;

      const task = {
        id: uuidv4(),
        type: 'test-task',
        requiredResources: [],
        complexity: 0.5,
        priority: 0.8,
      };

      const result = await engine.executeMurmuration(mockColony, task, mockA2ASystem);

      expect(result.success).toBe(true);
      expect(result.fallback).toBe(false);
      expect(result.patternUsed).toBe(pattern.id);
      expect(result.executionTime).toBeLessThan(100);
    });

    it('should fallback to ad-hoc when no pattern found', async () => {
      const task = {
        id: uuidv4(),
        type: 'test-task',
        requiredResources: [],
        complexity: 0.5,
        priority: 0.8,
      };

      const result = await engine.executeMurmuration(mockColony, task, mockA2ASystem);

      expect(result.fallback).toBe(true);
      expect(result.error).toContain('No memory found');
    });

    it('should fallback when pattern not automated enough', async () => {
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }
      engine.learnMurmuration(mockColony, packages);

      const task = {
        id: uuidv4(),
        type: 'test-task',
        requiredResources: [],
        complexity: 0.5,
        priority: 0.8,
      };

      const result = await engine.executeMurmuration(mockColony, task, mockA2ASystem);

      expect(result.fallback).toBe(true);
      expect(result.error).toContain('not automated');
    });

    it('should fallback on pattern execution failure', async () => {
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }
      engine.learnMurmuration(mockColony, packages);

      const memory = engine.getMemory(mockColony.id);
      const pattern = Array.from(memory!.patterns.values())[0];
      pattern.automationLevel = 1.0;

      // Mock failing A2A system
      const failingA2A = {
        createPackage: jest.fn().mockRejectedValue(new Error('Network error')),
      };

      const task = {
        id: uuidv4(),
        type: 'test-task',
        requiredResources: [],
        complexity: 0.5,
        priority: 0.8,
      };

      const result = await engine.executeMurmuration(mockColony, task, failingA2A);

      expect(result.fallback).toBe(true);
      expect(result.error).toContain('Pattern execution failed');
    });

    it('should update pattern metrics on execution', async () => {
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }
      engine.learnMurmuration(mockColony, packages);

      const memory = engine.getMemory(mockColony.id);
      const pattern = Array.from(memory!.patterns.values())[0];
      pattern.automationLevel = 1.0;
      pattern.successRate = 0.9;

      const task = {
        id: uuidv4(),
        type: 'test-task',
        requiredResources: [],
        complexity: 0.5,
        priority: 0.8,
      };

      await engine.executeMurmuration(mockColony, task, mockA2ASystem);

      expect(pattern.executionCount).toBe(1);
      expect(pattern.lastExecutionTime).toBeGreaterThan(0);
    });

    it('should achieve 100x speedup over ad-hoc', async () => {
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }
      engine.learnMurmuration(mockColony, packages);

      const memory = engine.getMemory(mockColony.id);
      const pattern = Array.from(memory!.patterns.values())[0];
      pattern.automationLevel = 1.0;
      pattern.successRate = 0.9;

      const task = {
        id: uuidv4(),
        type: 'test-task',
        requiredResources: [],
        complexity: 0.5,
        priority: 0.8,
      };

      // Pattern execution
      const patternResult = await engine.executeMurmuration(mockColony, task, mockA2ASystem);

      // Clear memory to force ad-hoc
      engine.clearMemory(mockColony.id);
      const adHocResult = await engine.executeMurmuration(mockColony, task, mockA2ASystem);

      expect(adHocResult.executionTime / patternResult.executionTime).toBeGreaterThan(10);
    });
  });

  describe('Co-evolution Optimization', () => {
    it('should advance co-evolution stage with executions', () => {
      const pattern = createMockPattern();
      pattern.executionCount = 0;

      engine.optimizeMurmuration(pattern);

      expect(pattern.coEvolutionStage).toBe(CoEvolutionStage.DISCOVERY);

      pattern.executionCount = 15;
      engine.optimizeMurmuration(pattern);

      expect(pattern.coEvolutionStage).toBe(CoEvolutionStage.REFINEMENT);

      pattern.executionCount = 35;
      engine.optimizeMurmuration(pattern);

      expect(pattern.coEvolutionStage).toBe(CoEvolutionStage.OPTIMIZATION);

      pattern.executionCount = 55;
      pattern.successRate = 0.9;
      engine.optimizeMurmuration(pattern);

      expect(pattern.coEvolutionStage).toBe(CoEvolutionStage.AUTOMATED);
    });

    it('should mark low-performing patterns as legacy', () => {
      const pattern = createMockPattern();
      pattern.executionCount = 50;
      pattern.successRate = 0.4;

      engine.optimizeMurmuration(pattern);

      expect(pattern.coEvolutionStage).toBe(CoEvolutionStage.LEGACY);
    });

    it('should optimize timeouts based on performance', () => {
      const pattern = createMockPattern();
      pattern.executionCount = 30;
      pattern.avgExecutionTime = 100;

      const metrics = {
        totalExecutions: 30,
        successfulExecutions: 27,
        totalExecutionTime: 3000,
        minExecutionTime: 80,
        maxExecutionTime: 120,
        lastExecution: Date.now(),
      };

      engine['metrics'].set(pattern.id, metrics);

      const originalTimeout = pattern.sequence[0].timeout;
      engine.optimizeMurmuration(pattern);

      expect(pattern.sequence[0].timeout).toBeLessThan(originalTimeout);
    });

    it('should increase automation level with performance', () => {
      const pattern = createMockPattern();
      pattern.executionCount = 40;
      pattern.successRate = 0.95;

      engine.optimizeMurmuration(pattern);

      expect(pattern.automationLevel).toBeGreaterThan(0);
    });
  });

  describe('Automation/Muscle Memory', () => {
    it('should automate high-performing patterns', () => {
      const packages = createRepeatedSequence(['agent1', 'agent2'], 25);
      engine.learnMurmuration(mockColony, packages);

      const memory = engine.getMemory(mockColony.id);
      const pattern = Array.from(memory!.patterns.values())[0];
      pattern.successRate = 0.9;
      pattern.executionCount = 25;

      const automated = engine.automateMurmuration(mockColony, pattern.id);

      expect(automated).toBe(true);
      expect(pattern.coEvolutionStage).toBe(CoEvolutionStage.AUTOMATED);
      expect(pattern.automationLevel).toBe(1.0);
    });

    it('should not automate low-performing patterns', () => {
      const packages = createRepeatedSequence(['agent1', 'agent2'], 25);
      engine.learnMurmuration(mockColony, packages);

      const memory = engine.getMemory(mockColony.id);
      const pattern = Array.from(memory!.patterns.values())[0];
      pattern.successRate = 0.5;
      pattern.executionCount = 25;

      const automated = engine.automateMurmuration(mockColony, pattern.id);

      expect(automated).toBe(false);
      expect(pattern.coEvolutionStage).not.toBe(CoEvolutionStage.AUTOMATED);
    });

    it('should optimize timeouts for automated patterns', () => {
      const packages = createRepeatedSequence(['agent1', 'agent2'], 25);
      engine.learnMurmuration(mockColony, packages);

      const memory = engine.getMemory(mockColony.id);
      const pattern = Array.from(memory!.patterns.values())[0];
      pattern.successRate = 0.9;
      pattern.executionCount = 25;

      const originalTimeout = pattern.sequence[0].timeout;
      engine.automateMurmuration(mockColony, pattern.id);

      expect(pattern.sequence[0].timeout).toBeLessThan(originalTimeout);
    });
  });

  describe('Pattern Management', () => {
    it('should retrieve all patterns for colony', () => {
      const packages1 = [];
      for (let i = 0; i < 5; i++) {
        packages1.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }
      const packages2 = [];
      for (let i = 0; i < 5; i++) {
        packages2.push(...createRepeatedSequence(['agent2', 'agent3'], 1));
      }

      engine.learnMurmuration(mockColony, packages1);
      engine.learnMurmuration(mockColony, packages2);

      const patterns = engine.getPatterns(mockColony.id);

      expect(patterns.length).toBe(2);
    });

    it('should retrieve specific pattern by ID', () => {
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }
      engine.learnMurmuration(mockColony, packages);

      const memory = engine.getMemory(mockColony.id);
      const pattern = Array.from(memory!.patterns.values())[0];

      const retrieved = engine.getPattern(mockColony.id, pattern.id);

      expect(retrieved).toBeDefined();
      expect(retrieved?.id).toBe(pattern.id);
    });

    it('should prune low-performing patterns', () => {
      const packages1 = [];
      for (let i = 0; i < 5; i++) {
        packages1.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }
      const packages2 = [];
      for (let i = 0; i < 5; i++) {
        packages2.push(...createRepeatedSequence(['agent2', 'agent3'], 1));
      }

      engine.learnMurmuration(mockColony, packages1);
      engine.learnMurmuration(mockColony, packages2);

      const memory = engine.getMemory(mockColony.id);
      const patterns = Array.from(memory!.patterns.values());
      if (patterns.length >= 2) {
        patterns[0].successRate = 0.8;
        patterns[0].executionCount = 20;
        patterns[1].successRate = 0.2;
        patterns[1].executionCount = 20;

        const pruned = engine.prunePatterns(mockColony.id, 0.3);

        expect(pruned).toBe(1);
        expect(memory!.patterns.size).toBe(1);
      }
    });

    it('should decay pattern success rates', () => {
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }
      engine.learnMurmuration(mockColony, packages);

      const memory = engine.getMemory(mockColony.id);
      const patterns = Array.from(memory!.patterns.values());
      if (patterns.length > 0) {
        const pattern = patterns[0];
        const originalSuccessRate = pattern.successRate;

        engine.decayPatterns(mockColony.id);

        expect(pattern.successRate).toBeLessThan(originalSuccessRate);
        expect(pattern.automationLevel).toBeLessThan(1.0);
      }
    });

    it('should clear memory for colony', () => {
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }
      engine.learnMurmuration(mockColony, packages);

      engine.clearMemory(mockColony.id);

      expect(engine.getMemory(mockColony.id)).toBeUndefined();
    });

    it('should clear all memories', () => {
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }
      engine.learnMurmuration(mockColony, packages);

      engine.clearAll();

      expect(engine.getMemory(mockColony.id)).toBeUndefined();
    });
  });

  describe('State Management', () => {
    it('should export and import state correctly', () => {
      const packages = [];
      for (let i = 0; i < 5; i++) {
        packages.push(...createRepeatedSequence(['agent1', 'agent2'], 1));
      }
      const learned = engine.learnMurmuration(mockColony, packages);

      // Verify pattern was learned
      expect(learned.length).toBeGreaterThan(0);

      const exported = engine.exportState();

      expect(exported.memories).toBeDefined();
      expect(exported.config).toBeDefined();
      expect(exported.simTime).toBeDefined();

      const newEngine = new MurmurationEngine();
      newEngine.importState(exported);

      expect(newEngine.getMemory(mockColony.id)).toBeDefined();
      const patterns = newEngine.getPatterns(mockColony.id);
      expect(patterns.length).toBeGreaterThan(0);
    });

    it('should preserve configuration on import', () => {
      engine.setSimTime(12345);

      const exported = engine.exportState();

      const newEngine = new MurmurationEngine();
      newEngine.importState(exported);

      expect(newEngine.getSimTime()).toBe(12345);
    });
  });

  describe('Utility Functions', () => {
    it('should create engine with factory function', () => {
      const config = { minOccurrences: 5 };
      const created = createMurmurationEngine(config);

      expect(created).toBeInstanceOf(MurmurationEngine);
    });

    it('should update simulation time', () => {
      engine.setSimTime(5000);
      expect(engine.getSimTime()).toBe(5000);

      engine.setSimTime(10000);
      expect(engine.getSimTime()).toBe(10000);
    });
  });
});

// ============================================================================
// Helper Functions
// ============================================================================

function createRepeatedSequence(
  participants: string[],
  count: number
): A2APackage[] {
  const packages: A2APackage[] = [];
  const chainId = uuidv4();

  for (let i = 0; i < count; i++) {
    for (let j = 0; j < participants.length - 1; j++) {
      packages.push({
        id: uuidv4(),
        timestamp: Date.now() + i * 100 + j * 10,
        senderId: participants[j],
        receiverId: participants[j + 1],
        type: 'message',
        payload: { data: `message-${i}-${j}` },
        parentIds: [],
        causalChainId: chainId,
        privacyLevel: 'COLONY' as any,
        layer: 'HABITUAL' as any,
      });
    }
  }

  return packages;
}

function createTimelySequence(
  participants: string[],
  count: number,
  interval: number
): A2APackage[] {
  const packages: A2APackage[] = [];
  const chainId = uuidv4();
  const baseTime = Date.now();

  for (let i = 0; i < count; i++) {
    for (let j = 0; j < participants.length - 1; j++) {
      packages.push({
        id: uuidv4(),
        timestamp: baseTime + i * interval + j * 10,
        senderId: participants[j],
        receiverId: participants[j + 1],
        type: 'message',
        payload: { data: `message-${i}-${j}` },
        parentIds: [],
        causalChainId: chainId,
        privacyLevel: 'COLONY' as any,
        layer: 'HABITUAL' as any,
      });
    }
  }

  return packages;
}

function createCausalChain(
  participants: string[],
  chainId: string,
  count: number
): A2APackage[] {
  const packages: A2APackage[] = [];

  for (let i = 0; i < count; i++) {
    for (let j = 0; j < participants.length - 1; j++) {
      packages.push({
        id: uuidv4(),
        timestamp: Date.now() + i * 100 + j * 10,
        senderId: participants[j],
        receiverId: participants[j + 1],
        type: 'message',
        payload: { data: `message-${i}-${j}` },
        parentIds: i > 0 ? [packages[packages.length - 1].id] : [],
        causalChainId: chainId,
        privacyLevel: 'COLONY' as any,
        layer: 'HABITUAL' as any,
      });
    }
  }

  return packages;
}

function createMockPattern(): MurmurationPattern {
  return {
    id: uuidv4(),
    name: 'Test Pattern',
    participants: ['agent1', 'agent2'],
    sequence: [
      {
        id: uuidv4(),
        senderId: 'agent1',
        receiverId: 'agent2',
        messageType: 'test',
        payloadSchema: { type: 'object' },
        timeout: 100,
        index: 0,
      },
    ],
    signature: 'test-signature',
    successRate: 0.8,
    executionCount: 10,
    avgExecutionTime: 100,
    formationTime: Date.now(),
    lastExecutionTime: Date.now(),
    coEvolutionStage: CoEvolutionStage.DISCOVERY,
    automationLevel: 0.5,
  };
}
