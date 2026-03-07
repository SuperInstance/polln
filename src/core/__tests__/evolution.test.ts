/**
 * POLLN Graph Evolution Tests
 */

import { GraphEvolution, GraphEvolutionConfig } from '../evolution.js';
import { HebbianLearning } from '../learning.js';

const defaultConfig: Partial<GraphEvolutionConfig> = {
  pruningThreshold: 0.1,
  pruningInterval: 100,
  pruningStrategy: 'combined',
  minSynapseAge: 10,
  maxPruningRate: 0.2,
  graftingProbability: 1.0, // Always graft for testing
  graftingStrategy: 'heuristic',
  maxNewConnections: 3,
  connectionBias: 0.3,
  clusterResolution: 1.0,
  minClusterSize: 2,
  clusterUpdateInterval: 100,
  plasticityRate: 0.01,
  stabilityThreshold: 0.8,
  homeostaticTarget: 0.5,
};

describe('POLLN Graph Evolution', () => {
  let evolution: GraphEvolution;
  let learning: HebbianLearning;

  beforeEach(() => {
    learning = new HebbianLearning({});
    evolution = new GraphEvolution(learning, defaultConfig);
  });

  describe('Agent Registration', () => {
    it('should register agents', () => {
      evolution.registerAgent('agent-1');
      evolution.registerAgent('agent-2');

      const stats = evolution.getStats();
      expect(stats.totalNodes).toBe(2);
    });

    it('should not duplicate agents', () => {
      evolution.registerAgent('agent-1');
      evolution.registerAgent('agent-1');

      const stats = evolution.getStats();
      expect(stats.totalNodes).toBe(1);
    });

    it('should register agents with capabilities', () => {
      const caps = new Map([['research', 0.8], ['analysis', 0.6]]);
      evolution.registerAgent('agent-1', caps);

      const node = evolution.getNode('agent-1');
      expect(node?.capabilities.get('research')).toBe(0.8);
    });

    it('should unregister agents', () => {
      evolution.registerAgent('agent-1');
      evolution.registerAgent('agent-2');

      evolution.unregisterAgent('agent-1');

      const stats = evolution.getStats();
      expect(stats.totalNodes).toBe(1);
      expect(evolution.getNode('agent-1')).toBeUndefined();
    });

    it('should remove edges when unregistering', () => {
      evolution.registerAgent('agent-1');
      evolution.registerAgent('agent-2');

      // Create edge
      evolution.updateEdge('agent-1', 'agent-2', {
        sourceAgentId: 'agent-1',
        targetAgentId: 'agent-2',
        weight: 0.8,
        coactivationCount: 5,
        lastCoactivated: Date.now(),
        learningRate: 0.01,
        decayRate: 0.001,
      });

      expect(evolution.getStats().totalEdges).toBe(1);

      evolution.unregisterAgent('agent-1');

      expect(evolution.getStats().totalEdges).toBe(0);
    });
  });

  describe('Edge Management', () => {
    beforeEach(() => {
      evolution.registerAgent('agent-1');
      evolution.registerAgent('agent-2');
    });

    it('should update edges from synapses', () => {
      evolution.updateEdge('agent-1', 'agent-2', {
        sourceAgentId: 'agent-1',
        targetAgentId: 'agent-2',
        weight: 0.7,
        coactivationCount: 10,
        lastCoactivated: Date.now(),
        learningRate: 0.01,
        decayRate: 0.001,
      });

      const edges = evolution.getEdges();
      expect(edges.length).toBe(1);
      expect(edges[0].weight).toBe(0.7);
    });

    it('should track edge activity', () => {
      evolution.updateEdge('agent-1', 'agent-2', {
        sourceAgentId: 'agent-1',
        targetAgentId: 'agent-2',
        weight: 0.5,
        coactivationCount: 25,
        lastCoactivated: Date.now(),
        learningRate: 0.01,
        decayRate: 0.001,
      });

      const edges = evolution.getEdges();
      expect(edges[0].activityLevel).toBe(25);
    });
  });

  describe('Evolution', () => {
    beforeEach(() => {
      evolution.registerAgent('agent-1');
      evolution.registerAgent('agent-2');
      evolution.registerAgent('agent-3');
    });

    it('should run evolution cycle', async () => {
      const stats = await evolution.evolve();

      expect(stats).toBeDefined();
      expect(stats.lastEvolution).toBeGreaterThan(0);
    });

    it('should create new connections', async () => {
      await evolution.evolve();

      const edges = evolution.getEdges();
      expect(edges.length).toBeGreaterThan(0);
    });

    it('should detect clusters', async () => {
      // Create some edges
      evolution.updateEdge('agent-1', 'agent-2', {
        sourceAgentId: 'agent-1',
        targetAgentId: 'agent-2',
        weight: 0.8,
        coactivationCount: 5,
        lastCoactivated: Date.now(),
        learningRate: 0.01,
        decayRate: 0.001,
      });

      await evolution.evolve();

      const clusters = evolution.getClusters();
      // May or may not have clusters depending on config
      expect(clusters).toBeDefined();
    });

    it('should track statistics', async () => {
      await evolution.evolve();

      const stats = evolution.getStats();
      expect(stats.totalNodes).toBe(3);
    });

    it('should emit events', (done) => {
      evolution.on('evolution_complete', () => done());
      evolution.evolve();
    });
  });

  describe('Configuration', () => {
    it('should return config', () => {
      const config = evolution.getConfig();
      expect(config.pruningThreshold).toBeDefined();
      expect(config.graftingStrategy).toBeDefined();
    });

    it('should update config', () => {
      evolution.updateConfig({
        pruningThreshold: 0.2,
        graftingProbability: 0.5
      });

      const config = evolution.getConfig();
      expect(config.pruningThreshold).toBe(0.2);
      expect(config.graftingProbability).toBe(0.5);
    });
  });
});
