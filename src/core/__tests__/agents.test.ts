/**
 * POLLN Concrete Agent Tests
 * TaskAgent, RoleAgent, CoreAgent
 */

import { TaskAgent, RoleAgent, CoreAgent, TileCategory } from '../agents.js';
import type { AgentConfig } from '../types.js';

// Mock agent configs
const createTaskAgentConfig = (): AgentConfig => ({
  id: 'task-agent-1',
  typeId: 'task',
  categoryId: 'ephemeral',
  modelFamily: 'test',
  defaultParams: {},
  inputTopics: ['input'],
  outputTopic: 'output',
  minExamples: 1,
  requiresWorldModel: false,
});

const createRoleAgentConfig = (): AgentConfig => ({
  id: 'role-agent-1',
  typeId: 'role',
  categoryId: 'role',
  modelFamily: 'test',
  defaultParams: {},
  inputTopics: ['input'],
  outputTopic: 'output',
  minExamples: 10,
  requiresWorldModel: false,
});

const createCoreAgentConfig = (): AgentConfig => ({
  id: 'core-agent-1',
  typeId: 'core',
  categoryId: 'core',
  modelFamily: 'test',
  defaultParams: {},
  inputTopics: ['input'],
  outputTopic: 'output',
  minExamples: 100,
  requiresWorldModel: true,
});

// Concrete test implementations
class TestTaskAgent extends TaskAgent {
  protected executeTask<T>(input: T): { success: boolean; output: unknown } {
    return { success: !!input, output: input };
  }
}

class TestRoleAgent extends RoleAgent {
  protected executeRole<T>(input: T): { success: boolean; output: unknown } {
    return { success: true, output: `processed: ${input}` };
  }
}

class TestCoreAgent extends CoreAgent {
  protected executeCore<T>(input: T): { success: boolean; output: unknown } {
    return { success: true, output: input };
  }
}

describe('POLLN Concrete Agents', () => {
  describe('TaskAgent', () => {
    let agent: TestTaskAgent;

    beforeEach(() => {
      agent = new TestTaskAgent(createTaskAgentConfig(), 10000);
    });

    it('should initialize as EPHEMERAL', async () => {
      await agent.initialize();
      expect(agent.category).toBe(TileCategory.EPHEMERAL);
    });

    it('should process input successfully', async () => {
      await agent.initialize();
      const result = await agent.process({ data: 'test' });

      expect(result.senderId).toBe('task-agent-1');
      expect(result.type).toBe('task_result');
    });

    it('should terminate when task complete', async () => {
      await agent.initialize();
      await agent.process({ data: 'test' });
      expect(agent.shouldTerminate()).toBe(true);
    });

    it('should not transfer knowledge (ephemeral)', () => {
      expect(agent.extractKnowledge()).toBeNull();
    });

    it('should terminate after max lifetime', async () => {
      const shortLivedAgent = new TestTaskAgent(createTaskAgentConfig(), 1);
      await shortLivedAgent.initialize();
      await new Promise(resolve => setTimeout(resolve, 10));
      expect(shortLivedAgent.shouldTerminate()).toBe(true);
    });
  });

  describe('RoleAgent', () => {
    let agent: TestRoleAgent;
    let successor: TestRoleAgent;

    beforeEach(() => {
      agent = new TestRoleAgent(createRoleAgentConfig());
      successor = new TestRoleAgent({
        ...createRoleAgentConfig(),
        id: 'role-agent-2',
      });
    });

    it('should initialize as ROLE', async () => {
      await agent.initialize();
      expect(agent.category).toBe(TileCategory.ROLE);
    });

    it('should accumulate knowledge from successful executions', async () => {
      await agent.initialize();
      for (let i = 0; i < 10; i++) {
        await agent.process({ data: `test-${i}` });
      }
      const knowledge = agent.extractKnowledge();
      expect(knowledge.size).toBeGreaterThan(0);
    });

    it('should track performance metrics', async () => {
      await agent.initialize();
      for (let i = 0; i < 25; i++) {
        await agent.process({ data: 'test' });
      }
      const metrics = agent.getPerformanceMetrics();
      expect(metrics.totalExecutions).toBe(25);
      expect(metrics.successRate).toBeGreaterThan(0);
    });

    it('should transfer knowledge to successor', async () => {
      await agent.initialize();
      await successor.initialize();

      for (let i = 0; i < 20; i++) {
        await agent.process({ data: 'test' });
      }

      agent.setSuccessor(successor);
      await agent.shutdown();

      const successorKnowledge = successor.extractKnowledge();
      expect(successorKnowledge.size).toBeGreaterThan(0);
    });

    it('should not terminate early with good performance', async () => {
      await agent.initialize();
      for (let i = 0; i < 50; i++) {
        await agent.process({ data: 'test' });
      }
      expect(agent.shouldTerminate()).toBe(false);
    });
  });

  describe('CoreAgent', () => {
    let agent: TestCoreAgent;

    beforeEach(() => {
      agent = new TestCoreAgent(createCoreAgentConfig());
    });

    it('should initialize as CORE', async () => {
      await agent.initialize();
      expect(agent.category).toBe(TileCategory.CORE);
    });

    it('should create backups periodically', async () => {
      agent = new TestCoreAgent({
        ...createCoreAgentConfig(),
        id: 'core-backup-test',
      });
      // @ts-ignore
      agent['backupIntervalMs'] = 10;

      await agent.initialize();
      await agent.process({ data: 'test1' });
      await new Promise(resolve => setTimeout(resolve, 20));
      await agent.process({ data: 'test2' });

      const backupStatus = agent.getBackupStatus();
      expect(backupStatus.hasBackup).toBe(true);
    });

    it('should rarely terminate', async () => {
      await agent.initialize();
      for (let i = 0; i < 100; i++) {
        await agent.process({ data: 'test' });
      }
      expect(agent.shouldTerminate()).toBe(false);
    });
  });
});
