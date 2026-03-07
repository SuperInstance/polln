/**
 * POLLN Knowledge Succession Protocol Tests
 */

import {
  KnowledgeSuccessionManager,
  TileLifecycleManager,
  KnowledgeStage,
} from '../succession.js';

describe('POLLN Knowledge Succession Protocol', () => {
  let manager: KnowledgeSuccessionManager;

  beforeEach(() => {
    manager = new KnowledgeSuccessionManager();
  });

  describe('KnowledgeStage', () => {
    it('should have correct stage progression', () => {
      expect(KnowledgeStage.EPHEMERAL).toBe('EPHEMERAL');
      expect(KnowledgeStage.WORKING).toBe('WORKING');
      expect(KnowledgeStage.EMBEDDED).toBe('EMBEDDED');
      expect(KnowledgeStage.FOSSIL).toBe('FOSSIL');
    });
  });

  describe('Knowledge Extraction', () => {
    it('should extract knowledge from agent state', () => {
      const state = new Map([
        ['pattern1', { data: 'test', count: 10 }],
        ['pattern2', { data: 'test2', count: 5 }],
      ]);

      const packet = manager.extractKnowledge(
        'agent-1',
        'task',
        'ephemeral',
        state,
        0.8,
        100,
        80,
        'death'
      );

      expect(packet.sourceAgentId).toBe('agent-1');
      expect(packet.valueFunction).toBe(0.8);
      expect(packet.executionCount).toBe(100);
      expect(packet.successRate).toBe(0.8);
      expect(packet.stage).toBe(KnowledgeStage.WORKING);
    });

    it('should assign correct knowledge stage based on execution count', () => {
      // EPHEMERAL: < 100
      const ephemeral = manager.extractKnowledge('a1', 'task', 'ephemeral', new Map(), 0.5, 50, 40, 'death');
      expect(ephemeral.stage).toBe(KnowledgeStage.EPHEMERAL);

      // WORKING: 100-1000
      const working = manager.extractKnowledge('a2', 'task', 'ephemeral', new Map(), 0.5, 500, 400, 'death');
      expect(working.stage).toBe(KnowledgeStage.WORKING);

      // EMBEDDED: > 1000
      const embedded = manager.extractKnowledge('a3', 'task', 'ephemeral', new Map(), 0.5, 1500, 1200, 'death');
      expect(embedded.stage).toBe(KnowledgeStage.EMBEDDED);
    });
  });

  describe('Knowledge Transfer', () => {
    it('should transfer knowledge between agents', async () => {
      // Create source knowledge
      const sourceState = new Map([
        ['pattern1', { data: 'value1', count: 20 }],
      ]);

      const packet = manager.extractKnowledge(
        'predecessor',
        'role',
        'role',
        sourceState,
        0.9,
        200,
        180,
        'succession'
      );

      // Create target state
      const targetState = new Map();

      const event = manager.transferKnowledge(packet.id, 'successor', targetState);

      expect(event.success).toBe(true);
      expect(event.predecessorId).toBe('predecessor');
      expect(event.successorId).toBe('successor');
      expect(event.patternsPreserved).toBeGreaterThan(0);
    });

    it('should handle transfer failure gracefully', async () => {
      const event = manager.transferKnowledge('nonexistent-packet', 'successor', new Map());
      expect(event.success).toBe(false);
    });
  });

  describe('Knowledge Compression', () => {
    it('should compress large pattern sets', () => {
      // Create many patterns
      const largeState = new Map();
      for (let i = 0; i < 150; i++) {
        largeState.set(`pattern-${i}`, { data: `value-${i}`, count: i + 1 });
      }

      const packet = manager.extractKnowledge(
        'compress-test',
        'role',
        'role',
        largeState,
        0.7,
        200,
        150,
        'compression'
      );

      expect(packet.metadata.compressionRatio).toBeLessThan(1);
    });
  });

  describe('Succession History', () => {
    it('should track succession events', async () => {
      const packet = manager.extractKnowledge('p1', 'role', 'role', new Map(), 0.5, 100, 80, 'succession');
      manager.transferKnowledge(packet.id, 's1', new Map());

      const history = manager.getSuccessionHistory('p1');
      expect(history.length).toBeGreaterThan(0);
      expect(history[0].success).toBe(true);
    });

    it('should provide statistics', () => {
      // Create some succession events
      const packet1 = manager.extractKnowledge('p1', 'role', 'role', new Map(), 0.8, 100, 80, 'succession');
      manager.transferKnowledge(packet1.id, 's1', new Map());

      const stats = manager.getStats();
      expect(stats.totalSuccessions).toBeGreaterThan(0);
      expect(stats.successfulSuccessions).toBeGreaterThan(0);
    });
  });

  describe('TileLifecycleManager', () => {
    let lifecycleManager: TileLifecycleManager;

    beforeEach(() => {
      lifecycleManager = new TileLifecycleManager(manager);
    });

    it('should register agents', () => {
      lifecycleManager.registerAgent('agent-1');
      expect(lifecycleManager.isDying('agent-1')).toBe(false);
    });

    it('should schedule agent death', () => {
      lifecycleManager.registerAgent('agent-1');
      lifecycleManager.scheduleDeath('agent-1', 'agent-2', 1000);

      expect(lifecycleManager.isDying('agent-1')).toBe(true);
    });

    it('should get dying agents', () => {
      lifecycleManager.registerAgent('agent-1');
      lifecycleManager.registerAgent('agent-2');
      lifecycleManager.scheduleDeath('agent-1', 'agent-3', 1000);

      const dying = lifecycleManager.getDyingAgents();
      expect(dying).toContain('agent-1');
      expect(dying).not.toContain('agent-2');
    });

    it('should execute death with knowledge transfer', async () => {
      lifecycleManager.registerAgent('agent-1');

      const state = new Map([['key', 'value']]);
      const event = await lifecycleManager.executeDeath(
        'agent-1',
        'role',
        'role',
        state,
        0.8,
        100,
        80
      );

      expect(event).toBeDefined();
      expect(lifecycleManager.isDying('agent-1')).toBe(false);
    });
  });
});
