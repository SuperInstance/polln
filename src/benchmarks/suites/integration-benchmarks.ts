/**
 * POLLN Integration Benchmarks
 *
 * End-to-end benchmarks covering the REAL integration surfaces:
 * Colony agent lifecycle (registerAgent/unregisterAgent/recordResult),
 * PlinkoLayer selection, DreamBasedPolicyOptimizer cycles, and
 * Meadow community operations.
 *
 * Rewritten 2026-10-04: the previous version benchmarked an imagined API
 * (spawnAgent/removeAgent/shutdown/mergeState/sharePattern) that never
 * existed in core — tsc had been silencing it via unresolved imports.
 */

import { performance } from 'perf_hooks';
import { v4 as uuidv4 } from 'uuid';
import type { BenchmarkSuite, BenchmarkConfig, BenchmarkMetrics, BenchmarkFunction } from '../types.js';
import { Colony } from '../../core/colony.js';
import type { ColonyConfig } from '../../core/colony.js';
import type { AgentConfig, AgentState } from '../../core/types.js';
import { PlinkoLayer } from '../../core/decision.js';
import { DreamBasedPolicyOptimizer } from '../../core/dreaming.js';
import { WorldModel } from '../../core/worldmodel.js';
import { ValueNetwork } from '../../core/valuenetwork.js';
import { Meadow } from '../../core/meadow.js';
import { calculateStats, calculateThroughput } from '../benchmark-profiler.js';

/** Valid ColonyConfig for benchmarks. */
function benchColonyConfig(maxAgents: number): ColonyConfig {
  return {
    id: `bench-colony-${uuidv4().slice(0, 8)}`,
    gardenerId: 'bench-gardener',
    name: 'Benchmark Colony',
    maxAgents,
    resourceBudget: {
      totalCompute: 1000,
      totalMemory: 1000,
      totalNetwork: 1000,
    },
  };
}

/** Minimal valid AgentConfig (registerAgent requires full core/types shape). */
function benchAgentConfig(): AgentConfig {
  return {
    id: uuidv4(),
    typeId: 'task',
    categoryId: 'benchmark',
    modelFamily: 'benchmark-model',
    defaultParams: {},
    inputTopics: [],
    outputTopic: 'benchmark.out',
    minExamples: 0,
    requiresWorldModel: false,
  };
}

/**
 * IntegrationBenchmarks - End-to-end integration performance tests
 */
export class IntegrationBenchmarks implements BenchmarkSuite {
  name = 'integration';
  description = 'End-to-end integration benchmarks';
  version = '1.1.0';

  private colony?: Colony;
  private plinko?: PlinkoLayer;
  private dreamOptimizer?: DreamBasedPolicyOptimizer;
  private meadow?: Meadow;

  async setup(): Promise<void> {
    this.colony = new Colony(benchColonyConfig(100));

    this.plinko = new PlinkoLayer({
      temperature: 1.0,
      minTemperature: 0.1,
      decayRate: 0.001,
    });

    const worldModel = new WorldModel({ latentDim: 32, learningRate: 0.001 });
    this.dreamOptimizer = new DreamBasedPolicyOptimizer(
      worldModel,
      new ValueNetwork(),
      null,
      { dreamHorizon: 10, dreamBatchSize: 50, explorationRate: 0.1 }
    );

    this.meadow = new Meadow();
  }

  async teardown(): Promise<void> {
    // Colony has no shutdown(): unregister everything it tracks
    if (this.colony) {
      for (const agent of this.colony.getAllAgents()) {
        this.colony.unregisterAgent(agent.id);
      }
    }
    this.colony = undefined;
    this.plinko = undefined;
    this.dreamOptimizer = undefined;
    this.meadow = undefined;
  }

  benchmarks = new Map<string, (config: BenchmarkConfig) => Promise<BenchmarkMetrics>>([
    ['agent-lifecycle', this.benchmarkAgentLifecycle.bind(this)],
    ['batch-spawn', this.benchmarkBatchSpawn.bind(this)],
    ['dream-cycle', this.benchmarkWorkflowDreamCycle.bind(this)],
    ['meadow-community', this.benchmarkWorkflowMeadowCommunity.bind(this)],
    ['full-pipeline', this.benchmarkWorkflowFullPipeline.bind(this)],
    ['consensus-coordination', this.benchmarkCoordinationConsensus.bind(this)],
    ['pipeline-coordination', this.benchmarkCoordinationPipeline.bind(this)],
    ['stats-sync', this.benchmarkFederatedStatsSync.bind(this)],
    ['evolution-pruning', this.benchmarkEvolutionPruning.bind(this)],
    ['large-colony-scalability', this.benchmarkScalabilityLargeColony.bind(this)],
  ]);

  /**
   * Benchmark: Agent lifecycle (register -> record -> unregister)
   */
  private async benchmarkAgentLifecycle(config: BenchmarkConfig): Promise<BenchmarkMetrics> {
    if (!this.colony) throw new Error('Colony not initialized');

    const samples: number[] = [];

    for (let i = 0; i < config.iterations; i++) {
      const start = performance.now();

      const state = this.colony.registerAgent(benchAgentConfig());
      this.colony.recordResult(state.id, true, Math.random() * 10);
      this.colony.unregisterAgent(state.id);

      const end = performance.now();
      samples.push(end - start);
    }

    const stats = calculateStats(samples);
    const throughput = calculateThroughput(samples, 1);

    return {
      ...stats,
      memoryBefore: 0,
      memoryAfter: 0,
      memoryDelta: 0,
      memoryPeak: 0,
      ...throughput,
    };
  }

  /**
   * Benchmark: Batch registration + parallel result recording
   */
  private async benchmarkBatchSpawn(config: BenchmarkConfig): Promise<BenchmarkMetrics> {
    if (!this.colony) throw new Error('Colony not initialized');

    const numAgents = 10;
    const samples: number[] = [];

    for (let i = 0; i < Math.floor(config.iterations / numAgents); i++) {
      const start = performance.now();

      const agents: AgentState[] = [];
      for (let j = 0; j < numAgents; j++) {
        agents.push(this.colony.registerAgent(benchAgentConfig()));
      }

      // Record work in parallel
      await Promise.all(
        agents.map((agent, j) =>
          Promise.resolve(this.colony!.recordResult(agent.id, true, j))
        )
      );

      // Unregister all
      await Promise.all(
        agents.map(agent => Promise.resolve(this.colony!.unregisterAgent(agent.id)))
      );

      const end = performance.now();
      samples.push(end - start);
    }

    const stats = calculateStats(samples);
    const throughput = calculateThroughput(samples, numAgents);

    return {
      ...stats,
      memoryBefore: 0,
      memoryAfter: 0,
      memoryDelta: 0,
      memoryPeak: 0,
      ...throughput,
    };
  }

  /**
   * Benchmark: Dream cycle workflow (experience intake + optimize)
   */
  private async benchmarkWorkflowDreamCycle(config: BenchmarkConfig): Promise<BenchmarkMetrics> {
    if (!this.dreamOptimizer) throw new Error('DreamOptimizer not initialized');

    const samples: number[] = [];

    for (let i = 0; i < Math.min(config.iterations, 20); i++) {
      const experiences = Array.from({ length: 50 }, () => ({
        state: new Array(128).fill(0).map(() => Math.random()),
        action: Math.floor(Math.random() * 10),
        reward: Math.random() * 2 - 1,
        nextState: new Array(128).fill(0).map(() => Math.random()),
      }));

      const start = performance.now();

      // Real dream path: add experiences, then run an optimization cycle
      for (const exp of experiences) {
        this.dreamOptimizer.addExperience(exp.state, exp.action, exp.reward, exp.nextState, false);
      }
      await this.dreamOptimizer.optimize();

      const end = performance.now();
      samples.push(end - start);
    }

    const stats = calculateStats(samples);
    const throughput = calculateThroughput(samples, 1);

    return {
      ...stats,
      memoryBefore: 0,
      memoryAfter: 0,
      memoryDelta: 0,
      memoryPeak: 0,
      ...throughput,
    };
  }

  /**
   * Benchmark: Meadow community operations (create/join/list)
   */
  private async benchmarkWorkflowMeadowCommunity(config: BenchmarkConfig): Promise<BenchmarkMetrics> {
    if (!this.meadow) throw new Error('Meadow not initialized');

    const samples: number[] = [];

    for (let i = 0; i < config.iterations; i++) {
      const start = performance.now();

      const community = this.meadow.createCommunity({
        name: `bench-community-${i}`,
        description: 'Benchmark community',
        visibility: 'PUBLIC' as never,
        createdBy: 'bench-keeper',
      });
      this.meadow.addMember(community.id, `bench-member-${i}`, 'MEMBER' as never);
      this.meadow.listCommunities();

      const end = performance.now();
      samples.push(end - start);
    }

    const stats = calculateStats(samples);
    const throughput = calculateThroughput(samples, 1);

    return {
      ...stats,
      memoryBefore: 0,
      memoryAfter: 0,
      memoryDelta: 0,
      memoryPeak: 0,
      ...throughput,
    };
  }

  /**
   * Benchmark: Full pipeline (register -> plinko select -> record -> dream -> unregister)
   */
  private async benchmarkWorkflowFullPipeline(config: BenchmarkConfig): Promise<BenchmarkMetrics> {
    if (!this.colony || !this.plinko || !this.dreamOptimizer) throw new Error('Components not initialized');

    const samples: number[] = [];

    for (let i = 0; i < Math.min(config.iterations, 10); i++) {
      const start = performance.now();

      // Register agents
      const agents: AgentState[] = [];
      for (let j = 0; j < 5; j++) {
        agents.push(this.colony.registerAgent(benchAgentConfig()));
      }

      // Generate proposals and run Plinko selection
      const proposals = agents.map(agent => ({
        agentId: agent.id,
        confidence: Math.random(),
        bid: Math.random(),
      }));
      await this.plinko.process(proposals);

      // Record outcomes
      for (const agent of agents) {
        this.colony.recordResult(agent.id, true, Math.random() * 10);
      }

      // Dream cycle
      this.dreamOptimizer.addExperience(
        new Array(128).fill(0).map(() => Math.random()),
        Math.floor(Math.random() * 4),
        Math.random() * 2 - 1,
        new Array(128).fill(0).map(() => Math.random()),
        false
      );

      // Teardown agents
      for (const agent of agents) {
        this.colony.unregisterAgent(agent.id);
      }

      const end = performance.now();
      samples.push(end - start);
    }

    const stats = calculateStats(samples);
    const throughput = calculateThroughput(samples, 1);

    return {
      ...stats,
      memoryBefore: 0,
      memoryAfter: 0,
      memoryDelta: 0,
      memoryPeak: 0,
      ...throughput,
    };
  }

  /**
   * Benchmark: Consensus coordination (parallel work + stats collection)
   */
  private async benchmarkCoordinationConsensus(config: BenchmarkConfig): Promise<BenchmarkMetrics> {
    if (!this.colony) throw new Error('Colony not initialized');

    const samples: number[] = [];

    for (let i = 0; i < Math.floor(config.iterations / 5); i++) {
      const start = performance.now();

      const agents: AgentState[] = [];
      for (let j = 0; j < 5; j++) {
        agents.push(this.colony.registerAgent(benchAgentConfig()));
      }

      // All agents "process" the same task via result recording
      await Promise.all(
        agents.map(agent =>
          Promise.resolve(this.colony!.recordResult(agent.id, true, Math.random() * 5))
        )
      );

      // Collect colony stats
      await this.colony.getStats();

      for (const agent of agents) {
        this.colony.unregisterAgent(agent.id);
      }

      const end = performance.now();
      samples.push(end - start);
    }

    const stats = calculateStats(samples);
    const throughput = calculateThroughput(samples, 5);

    return {
      ...stats,
      memoryBefore: 0,
      memoryAfter: 0,
      memoryDelta: 0,
      memoryPeak: 0,
      ...throughput,
    };
  }

  /**
   * Benchmark: Pipeline coordination (staged register/record/unregister)
   */
  private async benchmarkCoordinationPipeline(config: BenchmarkConfig): Promise<BenchmarkMetrics> {
    if (!this.colony) throw new Error('Colony not initialized');

    const numStages = 3;
    const samples: number[] = [];

    for (let i = 0; i < Math.floor(config.iterations / numStages); i++) {
      const start = performance.now();

      const stages: AgentState[] = [];
      for (let j = 0; j < numStages; j++) {
        stages.push(this.colony.registerAgent(benchAgentConfig()));
      }

      // Flow data through stages
      for (const [j, stage] of stages.entries()) {
        this.colony.recordResult(stage.id, j < numStages - 1, j);
      }

      for (const stage of stages) {
        this.colony.unregisterAgent(stage.id);
      }

      const end = performance.now();
      samples.push(end - start);
    }

    const stats = calculateStats(samples);
    const throughput = calculateThroughput(samples, numStages);

    return {
      ...stats,
      memoryBefore: 0,
      memoryAfter: 0,
      memoryDelta: 0,
      memoryPeak: 0,
      ...throughput,
    };
  }

  /**
   * Benchmark: Cross-colony state sync (stats + roster exchange).
   * The old mergeState() API never existed; the real distributed surface
   * is Colony#getStats / getAllAgents.
   */
  private async benchmarkFederatedStatsSync(config: BenchmarkConfig): Promise<BenchmarkMetrics> {
    if (!this.colony) throw new Error('Colony not initialized');

    const samples: number[] = [];

    for (let i = 0; i < Math.min(config.iterations, 20); i++) {
      const localColony = new Colony(benchColonyConfig(50));
      localColony.registerAgent(benchAgentConfig());

      const start = performance.now();

      // Exchange state the way the core actually supports
      const localStats = await localColony.getStats();
      const mainStats = await this.colony.getStats();
      const localRoster = localColony.getAllAgents().length + mainStats.totalAgents;

      const end = performance.now();
      samples.push(end - start);
      void localRoster;

      for (const agent of localColony.getAllAgents()) {
        localColony.unregisterAgent(agent.id);
      }
    }

    const stats = calculateStats(samples);
    const throughput = calculateThroughput(samples, 1);

    return {
      ...stats,
      memoryBefore: 0,
      memoryAfter: 0,
      memoryDelta: 0,
      memoryPeak: 0,
      ...throughput,
    };
  }

  /**
   * Benchmark: Evolution pruning (unregister half the roster)
   */
  private async benchmarkEvolutionPruning(config: BenchmarkConfig): Promise<BenchmarkMetrics> {
    if (!this.colony) throw new Error('Colony not initialized');

    const samples: number[] = [];

    for (let i = 0; i < Math.min(config.iterations, 10); i++) {
      const agents: AgentState[] = [];
      for (let j = 0; j < 50; j++) {
        agents.push(this.colony.registerAgent(benchAgentConfig()));
      }

      const start = performance.now();

      // Prune weak agents (lowest value first half)
      const weakAgents = agents.slice(0, 25);
      for (const agent of weakAgents) {
        this.colony.unregisterAgent(agent.id);
      }

      const end = performance.now();
      samples.push(end - start);

      // Cleanup remaining
      for (const agent of agents.slice(25)) {
        this.colony.unregisterAgent(agent.id);
      }
    }

    const stats = calculateStats(samples);
    const throughput = calculateThroughput(samples, 1);

    return {
      ...stats,
      memoryBefore: 0,
      memoryAfter: 0,
      memoryDelta: 0,
      memoryPeak: 0,
      ...throughput,
    };
  }

  /**
   * Benchmark: Large colony scalability
   */
  private async benchmarkScalabilityLargeColony(config: BenchmarkConfig): Promise<BenchmarkMetrics> {
    if (!this.colony) throw new Error('Colony not initialized');

    const colonySizes = [10, 25, 50, 100];
    const samples: number[] = [];

    for (const size of colonySizes) {
      const start = performance.now();

      const agents: AgentState[] = [];
      for (let j = 0; j < size; j++) {
        agents.push(this.colony.registerAgent(benchAgentConfig()));
      }

      // Record work across the roster
      for (const [j, agent] of agents.entries()) {
        this.colony.recordResult(agent.id, true, j % 10);
      }

      for (const agent of agents) {
        this.colony.unregisterAgent(agent.id);
      }

      const end = performance.now();
      samples.push(end - start);
    }

    const stats = calculateStats(samples);
    const throughput = calculateThroughput(samples, 1);

    return {
      ...stats,
      memoryBefore: 0,
      memoryAfter: 0,
      memoryDelta: 0,
      memoryPeak: 0,
      ...throughput,
    };
  }
}
