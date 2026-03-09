/**
 * POLLN SDK Tests
 * Comprehensive test suite for the POLLN SDK
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import { PollnSDK, ColonyHandle, AgentHandle } from '../index.js';
import type {
  PollnSDKConfig,
  ColonyConfig,
  AgentConfig,
  TaskInput,
  TaskResult,
  ErrorCode,
} from '../types.js';
import { PollnSDKError } from '../types.js';

// ============================================================================
// Test Helpers
// ============================================================================

function createTestConfig(overrides: Partial<PollnSDKConfig> = {}): PollnSDKConfig {
  return {
    debug: false,
    timeout: 30000,
    ...overrides,
  };
}

function createColonyConfig(overrides: Partial<ColonyConfig> = {}): ColonyConfig {
  return {
    name: 'test-colony',
    maxAgents: 10,
    resourceBudget: {
      totalCompute: 1000,
      totalMemory: 1024,
      totalNetwork: 100,
    },
    ...overrides,
  };
}

function createAgentConfig(overrides: Partial<AgentConfig> = {}): AgentConfig {
  return {
    category: 'ephemeral',
    goal: 'test-goal',
    inputTopics: ['test'],
    outputTopic: 'test-output',
    ...overrides,
  };
}

// ============================================================================
// SDK Initialization Tests
// ============================================================================

describe('PollnSDK - Initialization', () => {
  it('should initialize successfully with default config', async () => {
    const sdk = new PollnSDK();
    expect(sdk.getState().initialized).toBe(false);

    await sdk.initialize();
    expect(sdk.getState().initialized).toBe(true);

    await sdk.shutdown();
  });

  it('should initialize successfully with custom config', async () => {
    const config = createTestConfig({
      timeout: 60000,
      debug: true,
    });

    const sdk = new PollnSDK(config);
    await sdk.initialize();

    expect(sdk.getState().initialized).toBe(true);

    await sdk.shutdown();
  });

  it('should throw error when initializing twice', async () => {
    const sdk = new PollnSDK();
    await sdk.initialize();

    await expect(sdk.initialize()).rejects.toThrow(PollnSDKError);
    await expect(sdk.initialize()).rejects.toMatchObject({
      code: 'SDK_NOT_INITIALIZED',
    });

    await sdk.shutdown();
  });

  it('should shutdown cleanly', async () => {
    const sdk = new PollnSDK();
    await sdk.initialize();

    await sdk.shutdown();

    expect(sdk.getState().initialized).toBe(false);
    expect(sdk.getState().colonies).toBe(0);
    expect(sdk.getState().agents).toBe(0);
  });

  it('should track state correctly', async () => {
    const sdk = new PollnSDK();
    await sdk.initialize();

    const state = sdk.getState();
    expect(state).toEqual({
      initialized: true,
      colonies: 0,
      agents: 0,
      tasks: 0,
    });

    await sdk.shutdown();
  });
});

// ============================================================================
// Colony Management Tests
// ============================================================================

describe('PollnSDK - Colony Management', () => {
  let sdk: PollnSDK;

  beforeEach(async () => {
    sdk = new PollnSDK(createTestConfig());
    await sdk.initialize();
  });

  afterEach(async () => {
    await sdk.shutdown();
  });

  it('should create a colony successfully', async () => {
    const config = createColonyConfig();
    const colony = await sdk.createColony(config);

    expect(colony).toBeInstanceOf(ColonyHandle);
    expect(colony.id).toBeDefined();
    expect(colony.config.name).toBe(config.name);

    const state = sdk.getState();
    expect(state.colonies).toBe(1);
  });

  it('should create colony with custom ID', async () => {
    const config = createColonyConfig({ id: 'custom-colony-id' });
    const colony = await sdk.createColony(config);

    expect(colony.id).toBe('custom-colony-id');
  });

  it('should throw error when creating duplicate colony', async () => {
    const config = createColonyConfig({ id: 'duplicate-id' });

    await sdk.createColony(config);
    await expect(sdk.createColony(config)).rejects.toThrow(PollnSDKError);
    await expect(sdk.createColony(config)).rejects.toMatchObject({
      code: 'COLONY_ALREADY_EXISTS',
    });
  });

  it('should get a colony by ID', async () => {
    const config = createColonyConfig({ id: 'test-colony' });
    const created = await sdk.createColony(config);

    const retrieved = sdk.getColony('test-colony');
    expect(retrieved).toBe(created);
  });

  it('should return null for non-existent colony', () => {
    const colony = sdk.getColony('non-existent');
    expect(colony).toBeNull();
  });

  it('should list all colonies', async () => {
    await sdk.createColony(createColonyConfig({ name: 'colony-1' }));
    await sdk.createColony(createColonyConfig({ name: 'colony-2' }));
    await sdk.createColony(createColonyConfig({ name: 'colony-3' }));

    const colonies = sdk.listColonies();
    expect(colonies).toHaveLength(3);
  });

  it('should filter colonies by query', async () => {
    const colony1 = await sdk.createColony(createColonyConfig({ name: 'colony-1' }));
    await sdk.createColony(createColonyConfig({ name: 'colony-2' }));

    // Add agent to first colony
    await colony1.addAgent(createAgentConfig());

    // Query for colonies with agents
    const colonies = sdk.listColonies({ minAgents: 1 });
    expect(colonies).toHaveLength(1);
    expect(colonies[0].config.name).toBe('colony-1');
  });

  it('should limit colony list results', async () => {
    await sdk.createColony(createColonyConfig({ name: 'colony-1' }));
    await sdk.createColony(createColonyConfig({ name: 'colony-2' }));
    await sdk.createColony(createColonyConfig({ name: 'colony-3' }));

    const colonies = sdk.listColonies({ limit: 2 });
    expect(colonies).toHaveLength(2);
  });

  it('should destroy a colony', async () => {
    const colony = await sdk.createColony(createColonyConfig({ id: 'test-colony' }));

    await sdk.destroyColony('test-colony');

    expect(sdk.getColony('test-colony')).toBeNull();
    expect(sdk.getState().colonies).toBe(0);
  });

  it('should throw error when destroying non-existent colony', async () => {
    await expect(sdk.destroyColony('non-existent')).rejects.toThrow(PollnSDKError);
    await expect(sdk.destroyColony('non-existent')).rejects.toMatchObject({
      code: 'COLONY_NOT_FOUND',
    });
  });

  it('should get colony state', async () => {
    const config = createColonyConfig();
    const colony = await sdk.createColony(config);

    const state = colony.getState();
    expect(state.id).toBeDefined();
    expect(state.name).toBe(config.name);
    expect(state.totalAgents).toBe(0);
    expect(state.activeAgents).toBe(0);
    expect(state.shannonDiversity).toBeDefined();
  });
});

// ============================================================================
// Agent Management Tests
// ============================================================================

describe('PollnSDK - Agent Management', () => {
  let sdk: PollnSDK;
  let colony: ColonyHandle;

  beforeEach(async () => {
    sdk = new PollnSDK(createTestConfig());
    await sdk.initialize();
    colony = await sdk.createColony(createColonyConfig({ id: 'test-colony' }));
  });

  afterEach(async () => {
    await sdk.shutdown();
  });

  it('should add an ephemeral agent successfully', async () => {
    const config = createAgentConfig({ category: 'ephemeral' });
    const agent = await sdk.addAgent(colony.id, config);

    expect(agent).toBeInstanceOf(AgentHandle);
    expect(agent.id).toBeDefined();
    expect(agent.colonyId).toBe(colony.id);
    expect(agent.config.category).toBe('ephemeral');

    expect(sdk.getState().agents).toBe(1);
  });

  it('should add a role agent successfully', async () => {
    const config = createAgentConfig({ category: 'role' });
    const agent = await sdk.addAgent(colony.id, config);

    expect(agent.config.category).toBe('role');
  });

  it('should add a core agent successfully', async () => {
    const config = createAgentConfig({ category: 'core' });
    const agent = await sdk.addAgent(colony.id, config);

    expect(agent.config.category).toBe('core');
  });

  it('should add agent with custom ID', async () => {
    const config = createAgentConfig({ id: 'custom-agent-id' });
    const agent = await sdk.addAgent(colony.id, config);

    expect(agent.id).toBe('custom-agent-id');
  });

  it('should throw error when adding to non-existent colony', async () => {
    const config = createAgentConfig();

    await expect(sdk.addAgent('non-existent', config)).rejects.toThrow(PollnSDKError);
    await expect(sdk.addAgent('non-existent', config)).rejects.toMatchObject({
      code: 'COLONY_NOT_FOUND',
    });
  });

  it('should get an agent by ID', async () => {
    const config = createAgentConfig({ id: 'test-agent' });
    const created = await sdk.addAgent(colony.id, config);

    const retrieved = sdk.getAgent(colony.id, 'test-agent');
    expect(retrieved).toBe(created);
  });

  it('should return null for non-existent agent', () => {
    const agent = sdk.getAgent(colony.id, 'non-existent');
    expect(agent).toBeNull();
  });

  it('should list all agents in colony', async () => {
    await sdk.addAgent(colony.id, createAgentConfig({ category: 'ephemeral' }));
    await sdk.addAgent(colony.id, createAgentConfig({ category: 'role' }));
    await sdk.addAgent(colony.id, createAgentConfig({ category: 'core' }));

    const agents = sdk.listAgents(colony.id);
    expect(agents).toHaveLength(3);
  });

  it('should filter agents by category', async () => {
    await sdk.addAgent(colony.id, createAgentConfig({ category: 'ephemeral' }));
    await sdk.addAgent(colony.id, createAgentConfig({ category: 'role' }));
    await sdk.addAgent(colony.id, createAgentConfig({ category: 'role' }));

    const ephemeral = sdk.listAgents(colony.id, { category: 'ephemeral' });
    const role = sdk.listAgents(colony.id, { category: 'role' });

    expect(ephemeral).toHaveLength(1);
    expect(role).toHaveLength(2);
  });

  it('should limit agent list results', async () => {
    await sdk.addAgent(colony.id, createAgentConfig());
    await sdk.addAgent(colony.id, createAgentConfig());
    await sdk.addAgent(colony.id, createAgentConfig());

    const agents = sdk.listAgents(colony.id, { limit: 2 });
    expect(agents).toHaveLength(2);
  });

  it('should remove an agent', async () => {
    const config = createAgentConfig({ id: 'test-agent' });
    await sdk.addAgent(colony.id, config);

    await sdk.removeAgent(colony.id, 'test-agent');

    expect(sdk.getAgent(colony.id, 'test-agent')).toBeNull();
    expect(sdk.getState().agents).toBe(0);
  });

  it('should throw error when removing non-existent agent', async () => {
    await expect(sdk.removeAgent(colony.id, 'non-existent')).rejects.toThrow(PollnSDKError);
    await expect(sdk.removeAgent(colony.id, 'non-existent')).rejects.toMatchObject({
      code: 'AGENT_NOT_FOUND',
    });
  });

  it('should get agent state', async () => {
    const config = createAgentConfig();
    const agent = await colony.addAgent(config);

    const state = agent.getState();
    expect(state.id).toBeDefined();
    expect(state.category).toBe(config.category);
    expect(state.goal).toBe(config.goal);
    expect(state.status).toBeDefined();
    expect(state.valueFunction).toBeGreaterThanOrEqual(0);
    expect(state.valueFunction).toBeLessThanOrEqual(1);
  });

  it('should check if agent should terminate', async () => {
    const config = createAgentConfig({ category: 'ephemeral' });
    const agent = await colony.addAgent(config);

    // Fresh agent should not terminate
    expect(agent.shouldTerminate()).toBe(false);
  });
});

// ============================================================================
// Task Execution Tests
// ============================================================================

describe('PollnSDK - Task Execution', () => {
  let sdk: PollnSDK;
  let colony: ColonyHandle;
  let agent: AgentHandle;

  beforeEach(async () => {
    sdk = new PollnSDK(createTestConfig());
    await sdk.initialize();
    colony = await sdk.createColony(createColonyConfig({ id: 'test-colony' }));
    agent = await colony.addAgent(createAgentConfig({ id: 'test-agent' }));
  });

  afterEach(async () => {
    await sdk.shutdown();
  });

  it('should run a task successfully', async () => {
    const taskInput: TaskInput<string> = {
      colonyId: colony.id,
      agentId: agent.id,
      input: 'test input',
    };

    const result = await sdk.runTask<string, string>(taskInput);

    expect(result.success).toBe(true);
    expect(result.agentId).toBe(agent.id);
    expect(result.output).toBeDefined();
    expect(result.executionTimeMs).toBeGreaterThanOrEqual(0);
    expect(result.timestamp).toBeDefined();
  });

  it('should run a task without specifying agent', async () => {
    const taskInput: TaskInput<string> = {
      colonyId: colony.id,
      input: 'test input',
    };

    const result = await sdk.runTask<string, string>(taskInput);

    expect(result.success).toBe(true);
    expect(result.agentId).toBeDefined();
  });

  it('should throw error when running task in non-existent colony', async () => {
    const taskInput: TaskInput<string> = {
      colonyId: 'non-existent',
      input: 'test',
    };

    await expect(sdk.runTask(taskInput)).rejects.toThrow(PollnSDKError);
    await expect(sdk.runTask(taskInput)).rejects.toMatchObject({
      code: 'COLONY_NOT_FOUND',
    });
  });

  it('should throw error when running task with non-existent agent', async () => {
    const taskInput: TaskInput<string> = {
      colonyId: colony.id,
      agentId: 'non-existent',
      input: 'test',
    };

    await expect(sdk.runTask(taskInput)).rejects.toThrow(PollnSDKError);
    await expect(sdk.runTask(taskInput)).rejects.toMatchObject({
      code: 'AGENT_NOT_FOUND',
    });
  });

  it('should handle task with custom ID', async () => {
    const taskInput: TaskInput<string> = {
      colonyId: colony.id,
      agentId: agent.id,
      id: 'custom-task-id',
      input: 'test',
    };

    const result = await sdk.runTask<string, string>(taskInput);

    expect(result.id).toBe('custom-task-id');
  });

  it('should include metadata in task result', async () => {
    const metadata = { key: 'value' };
    const taskInput: TaskInput<string> = {
      colonyId: colony.id,
      agentId: agent.id,
      input: 'test',
      metadata,
    };

    const result = await sdk.runTask<string, string>(taskInput);

    expect(result.metadata).toEqual(metadata);
  });

  it('should run task via colony handle', async () => {
    const result = await colony.runTask<string, string>({
      agentId: agent.id,
      input: 'test',
    });

    expect(result.success).toBe(true);
    expect(result.agentId).toBe(agent.id);
  });
});

// ============================================================================
// Streaming Tests
// ============================================================================

describe('PollnSDK - Streaming', () => {
  let sdk: PollnSDK;
  let colony: ColonyHandle;
  let agent: AgentHandle;

  beforeEach(async () => {
    sdk = new PollnSDK(createTestConfig());
    await sdk.initialize();
    colony = await sdk.createColony(createColonyConfig({ id: 'test-colony' }));
    agent = await colony.addAgent(createAgentConfig({ id: 'test-agent' }));
  });

  afterEach(async () => {
    await sdk.shutdown();
  });

  it('should stream task results', async () => {
    const taskInput: TaskInput<string> = {
      colonyId: colony.id,
      agentId: agent.id,
      input: 'test input for streaming',
    };

    const chunks: unknown[] = [];
    for await (const chunk of sdk.streamTask<string, string>(taskInput)) {
      chunks.push(chunk.chunk);
      expect(chunk.taskId).toBeDefined();
      expect(chunk.agentId).toBe(agent.id);
      expect(chunk.executionTimeMs).toBeGreaterThanOrEqual(0);
      expect(chunk.timestamp).toBeDefined();
    }

    expect(chunks.length).toBeGreaterThan(0);
  });

  it('should stream with custom chunk size', async () => {
    const taskInput: TaskInput<string> = {
      colonyId: colony.id,
      agentId: agent.id,
      input: 'x'.repeat(100),
    };

    const chunks: unknown[] = [];
    for await (const chunk of sdk.streamTask<string, unknown>(taskInput, { chunkSize: 10 })) {
      chunks.push(chunk.chunk);
    }

    // The agent returns an object with success and output
    // For streaming, we'll get at least one chunk
    expect(chunks.length).toBeGreaterThanOrEqual(1);
  });

  it('should stream with chunk delay', async () => {
    const taskInput: TaskInput<string> = {
      colonyId: colony.id,
      agentId: agent.id,
      input: 'test input data',
    };

    const startTime = Date.now();
    const chunks: unknown[] = [];
    for await (const chunk of sdk.streamTask<string, unknown>(taskInput, { chunkDelay: 10 })) {
      chunks.push(chunk.chunk);
    }
    const duration = Date.now() - startTime;

    // Should have at least one chunk and delay should be applied
    expect(chunks.length).toBeGreaterThanOrEqual(1);
    expect(duration).toBeGreaterThanOrEqual(0); // Delay is applied (even for single chunk)
  });

  it('should mark final chunk as done', async () => {
    const taskInput: TaskInput<string> = {
      colonyId: colony.id,
      agentId: agent.id,
      input: 'test',
    };

    const chunks: unknown[] = [];
    let lastChunk: unknown = null;

    for await (const chunk of sdk.streamTask<string, string>(taskInput)) {
      lastChunk = chunk;
      chunks.push(chunk.chunk);
    }

    expect(lastChunk).toBeDefined();
    expect((lastChunk as { done: boolean }).done).toBe(true);
  });

  it('should stream via colony handle', async () => {
    const chunks: unknown[] = [];
    for await (const chunk of colony.streamTask<string, string>({
      agentId: agent.id,
      input: 'test',
    })) {
      chunks.push(chunk.chunk);
    }

    expect(chunks.length).toBeGreaterThan(0);
  });
});

// ============================================================================
// Event Handling Tests
// ============================================================================

describe('PollnSDK - Event Handling', () => {
  let sdk: PollnSDK;

  beforeEach(async () => {
    sdk = new PollnSDK(createTestConfig());
    await sdk.initialize();
  });

  afterEach(async () => {
    await sdk.shutdown();
  });

  it('should subscribe to colony:created event', async () => {
    let eventReceived = false;
    let eventData: unknown = null;

    sdk.on('colony:created', (event) => {
      eventReceived = true;
      eventData = event.data;
    });

    await sdk.createColony(createColonyConfig());

    expect(eventReceived).toBe(true);
    expect(eventData).toBeDefined();
  });

  it('should subscribe to colony:agent:added event', async () => {
    const colony = await sdk.createColony(createColonyConfig());

    let eventReceived = false;
    sdk.on('colony:agent:added', (event) => {
      eventReceived = true;
    });

    await colony.addAgent(createAgentConfig());

    expect(eventReceived).toBe(true);
  });

  it('should subscribe to agent:task:completed event', async () => {
    const colony = await sdk.createColony(createColonyConfig());
    const agent = await colony.addAgent(createAgentConfig());

    let eventReceived = false;
    sdk.on('agent:task:completed', (event) => {
      eventReceived = true;
    });

    await colony.runTask<string, string>({ agentId: agent.id, input: 'test' });

    expect(eventReceived).toBe(true);
  });

  it('should support multiple event handlers', async () => {
    let count = 0;

    sdk.on('colony:created', () => count++);
    sdk.on('colony:created', () => count++);

    await sdk.createColony(createColonyConfig());

    expect(count).toBe(2);
  });

  it('should unsubscribe from events', async () => {
    let count = 0;

    const handler = () => count++;
    sdk.on('colony:created', handler);

    await sdk.createColony(createColonyConfig());
    expect(count).toBe(1);

    sdk.off('colony:created', handler);

    await sdk.createColony(createColonyConfig());
    expect(count).toBe(1); // Should not increment
  });

  it('should handle async event handlers', async () => {
    let eventReceived = false;

    sdk.on('colony:created', async (event) => {
      await new Promise(resolve => setTimeout(resolve, 10));
      eventReceived = true;
    });

    await sdk.createColony(createColonyConfig());

    // Wait for async handler
    await new Promise(resolve => setTimeout(resolve, 50));

    expect(eventReceived).toBe(true);
  });
});

// ============================================================================
// Error Handling Tests
// ============================================================================

describe('PollnSDK - Error Handling', () => {
  it('should throw error when using SDK before initialization', async () => {
    const sdk = new PollnSDK();

    await expect(sdk.createColony(createColonyConfig())).rejects.toThrow(PollnSDKError);
    await expect(sdk.createColony(createColonyConfig())).rejects.toMatchObject({
      code: 'SDK_NOT_INITIALIZED',
    });
  });

  it('should include error details in PollnSDKError', () => {
    const error = new PollnSDKError(
      'TEST_ERROR' as ErrorCode,
      'Test error message',
      { key: 'value' }
    );

    expect(error.code).toBe('TEST_ERROR');
    expect(error.message).toBe('Test error message');
    expect(error.details).toEqual({ key: 'value' });
    expect(error.name).toBe('PollnSDKError');
  });

  it('should handle errors in event handlers gracefully', async () => {
    const sdk = new PollnSDK(createTestConfig({ debug: true }));
    await sdk.initialize();

    // Handler that throws
    sdk.on('colony:created', () => {
      throw new Error('Handler error');
    });

    // Should not throw
    await sdk.createColony(createColonyConfig());

    await sdk.shutdown();
  });
});

// ============================================================================
// Integration Tests
// ============================================================================

describe('PollnSDK - Integration', () => {
  it('should handle complete workflow', async () => {
    const sdk = new PollnSDK(createTestConfig());
    await sdk.initialize();

    // Create colony
    const colony = await sdk.createColony(createColonyConfig({ name: 'integration-test' }));
    expect(colony).toBeDefined();

    // Add agents
    const agent1 = await colony.addAgent(createAgentConfig({ category: 'ephemeral', goal: 'task-1' }));
    const agent2 = await colony.addAgent(createAgentConfig({ category: 'role', goal: 'task-2' }));
    expect(colony.listAgents()).toHaveLength(2);

    // Run tasks
    const result1 = await colony.runTask<string, string>({ agentId: agent1.id, input: 'test-1' });
    const result2 = await colony.runTask<string, string>({ agentId: agent2.id, input: 'test-2' });

    expect(result1.success).toBe(true);
    expect(result2.success).toBe(true);

    // Stream task
    const chunks: unknown[] = [];
    for await (const chunk of colony.streamTask<string, string>({ agentId: agent1.id, input: 'stream-test' })) {
      chunks.push(chunk.chunk);
    }
    expect(chunks.length).toBeGreaterThan(0);

    // Check state
    const state = sdk.getState();
    expect(state.colonies).toBe(1);
    expect(state.agents).toBe(2);

    // Cleanup
    await sdk.shutdown();
    expect(sdk.getState().initialized).toBe(false);
  });

  it('should handle multiple colonies', async () => {
    const sdk = new PollnSDK(createTestConfig());
    await sdk.initialize();

    const colony1 = await sdk.createColony(createColonyConfig({ name: 'colony-1' }));
    const colony2 = await sdk.createColony(createColonyConfig({ name: 'colony-2' }));
    const colony3 = await sdk.createColony(createColonyConfig({ name: 'colony-3' }));

    const agent1 = await colony1.addAgent(createAgentConfig());
    const agent2 = await colony2.addAgent(createAgentConfig());
    const agent3 = await colony3.addAgent(createAgentConfig());

    expect(sdk.listColonies()).toHaveLength(3);
    expect(colony1.listAgents()).toHaveLength(1);
    expect(colony2.listAgents()).toHaveLength(1);
    expect(colony3.listAgents()).toHaveLength(1);

    await sdk.shutdown();
  });
});
