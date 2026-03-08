/**
 * POLLN Performance Benchmarking Suite
 *
 * Comprehensive benchmarking for core system components:
 * - Agent execution hot paths
 * - Embedding similarity search
 * - Plinko decision selection
 * - World model operations
 * - Colony management
 *
 * Sprint 7: Performance Optimization
 */

import { performance } from 'perf_hooks';
import { v4 as uuidv4 } from 'uuid';
import { BaseAgent } from '../../agent.js';
import { Colony } from '../../colony.js';
import { PlinkoLayer } from '../../decision.js';
import { BES } from '../../embedding.js';
import { WorldModel } from '../../worldmodel.js';
import type { AgentConfig } from '../../types.js';
import { KVAnchorPool } from '../../kvanchor.js';
import { ANNIndex } from '../../ann-index.js';

// Define AgentProposal locally since it's not exported from types
interface AgentProposal {
  agentId: string;
  confidence: number;
  bid: number;
}

// ============================================================================
// BENCHMARK UTILITIES
// ============================================================================

export interface BenchmarkResult {
  name: string;
  iterations: number;
  totalTime: number;
  avgTime: number;
  minTime: number;
  maxTime: number;
  p50: number;
  p95: number;
  p99: number;
  opsPerSecond: number;
  memoryBefore: number;
  memoryAfter: number;
  memoryDelta: number;
}

export interface BenchmarkConfig {
  iterations: number;
  warmupIterations: number;
  gcBefore?: boolean;
}

class BenchmarkRunner {
  private results: Map<string, BenchmarkResult> = new Map();

  /**
   * Run a benchmark with memory tracking
   */
  async runBenchmark(
    name: string,
    fn: () => Promise<void> | void,
    config: BenchmarkConfig
  ): Promise<BenchmarkResult> {
    const { iterations, warmupIterations, gcBefore = true } = config;

    // Warmup
    for (let i = 0; i < warmupIterations; i++) {
      await fn();
    }

    // Force GC if available
    if (gcBefore && global.gc) {
      global.gc();
    }

    // Measure memory before
    const memoryBefore = process.memoryUsage().heapUsed;

    // Run benchmark
    const times: number[] = [];
    for (let i = 0; i < iterations; i++) {
      const start = performance.now();
      await fn();
      const end = performance.now();
      times.push(end - start);
    }

    // Measure memory after
    const memoryAfter = process.memoryUsage().heapUsed;

    // Calculate statistics
    times.sort((a, b) => a - b);
    const totalTime = times.reduce((sum, t) => sum + t, 0);
    const avgTime = totalTime / iterations;
    const minTime = times[0];
    const maxTime = times[iterations - 1];
    const p50 = times[Math.floor(iterations * 0.5)];
    const p95 = times[Math.floor(iterations * 0.95)];
    const p99 = times[Math.floor(iterations * 0.99)];
    const opsPerSecond = 1000 / avgTime;

    const result: BenchmarkResult = {
      name,
      iterations,
      totalTime,
      avgTime,
      minTime,
      maxTime,
      p50,
      p95,
      p99,
      opsPerSecond,
      memoryBefore,
      memoryAfter,
      memoryDelta: memoryAfter - memoryBefore,
    };

    this.results.set(name, result);
    return result;
  }

  /**
   * Get all results
   */
  getResults(): BenchmarkResult[] {
    return Array.from(this.results.values());
  }

  /**
   * Print results as table
   */
  printResults(): void {
    console.log('\n=== Performance Benchmark Results ===\n');
    console.table(
      this.getResults().map(r => ({
        Name: r.name,
        Avg: `${r.avgTime.toFixed(3)}ms`,
        P95: `${r.p95.toFixed(3)}ms`,
        Ops: `${r.opsPerSecond.toFixed(0)}/s`,
        Memory: `${(r.memoryDelta / 1024 / 1024).toFixed(2)}MB`,
      }))
    );
  }

  /**
   * Compare two benchmark runs
   */
  compare(beforeName: string, afterName: string): {
    improvement: number;
    speedup: number;
  } {
    const before = this.results.get(beforeName);
    const after = this.results.get(afterName);

    if (!before || !after) {
      throw new Error('Benchmark results not found');
    }

    const improvement = ((before.avgTime - after.avgTime) / before.avgTime) * 100;
    const speedup = before.avgTime / after.avgTime;

    return { improvement, speedup };
  }
}

// ============================================================================
// AGENT EXECUTION BENCHMARKS
// ============================================================================

class MockAgent extends BaseAgent {
  constructor(public override config: any) {
    super(config);
  }

  async initialize(): Promise<void> {
    this.setState('initialized', true);
  }

  async process<T>(input: T): Promise<any> {
    // Simulate processing
    const result = JSON.stringify(input);
    return {
      id: uuidv4(),
      timestamp: Date.now(),
      senderId: this.id,
      receiverId: 'colony',
      type: 'test',
      payload: { result },
      parentIds: [],
      causalChainId: uuidv4(),
      privacyLevel: 'LOCAL' as const,
      layer: 'HABITUAL' as const,
    };
  }

  async shutdown(): Promise<void> {
    this.state.clear();
  }
}

export async function benchmarkAgentExecution(
  runner: BenchmarkRunner
): Promise<void> {
  console.log('\n--- Agent Execution Benchmarks ---');

  // Benchmark 1: Agent creation
  const config: any = {
    id: uuidv4(),
  };

  await runner.runBenchmark(
    'Agent Creation',
    async () => {
      const agent = new MockAgent({ ...config, id: uuidv4() });
      await agent.initialize();
    },
    { iterations: 1000, warmupIterations: 100 }
  );

  // Benchmark 2: Agent processing
  const agent = new MockAgent(config);
  await agent.initialize();

  await runner.runBenchmark(
    'Agent Processing',
    async () => {
      await agent.process({ test: 'data' });
    },
    { iterations: 1000, warmupIterations: 100 }
  );

  // Benchmark 3: Agent state management
  await runner.runBenchmark(
    'Agent State Get/Set',
    () => {
      agent.setState('key', 'value');
      agent.getState<string>('key');
    },
    { iterations: 10000, warmupIterations: 1000 }
  );

  await agent.shutdown();
}

// ============================================================================
// COLONY MANAGEMENT BENCHMARKS
// ============================================================================

export async function benchmarkColonyManagement(
  runner: BenchmarkRunner
): Promise<void> {
  console.log('\n--- Colony Management Benchmarks ---');

  const colony = new Colony({
    id: uuidv4(),
    gardenerId: 'test-gardener',
    name: 'test-colony',
    maxAgents: 1000,
    resourceBudget: {
      totalCompute: 1000,
      totalMemory: 1000,
      totalNetwork: 1000,
    },
  });

  // Benchmark 1: Agent registration
  await runner.runBenchmark(
    'Colony Agent Registration',
    async () => {
      const agentId = uuidv4();
      await colony.registerAgent({
        id: agentId,
        typeId: 'TASK',
        categoryId: 'EPHEMERAL',
        modelFamily: 'test',
        defaultParams: {},
        inputTopics: [],
        outputTopic: 'output',
        minExamples: 1,
        requiresWorldModel: false,
      } as any);
    },
    { iterations: 1000, warmupIterations: 100 }
  );

  // Benchmark 2: Colony stats computation
  await runner.runBenchmark(
    'Colony Stats Computation',
    () => {
      colony.getStats();
    },
    { iterations: 1000, warmupIterations: 100 }
  );
}

// ============================================================================
// PLINKO DECISION BENCHMARKS
// ============================================================================

export async function benchmarkPlinkoDecision(
  runner: BenchmarkRunner
): Promise<void> {
  console.log('\n--- Plinko Decision Benchmarks ---');

  const plinko = new PlinkoLayer({
    temperature: 1.0,
    minTemperature: 0.1,
    decayRate: 0.001,
  });

  // Generate proposals
  const smallProposals: AgentProposal[] = Array.from({ length: 10 }, () => ({
    agentId: uuidv4(),
    confidence: Math.random(),
    bid: Math.random(),
  }));

  const largeProposals: AgentProposal[] = Array.from(
    { length: 1000 },
    () => ({
      agentId: uuidv4(),
      confidence: Math.random(),
      bid: Math.random(),
    })
  );

  // Benchmark 1: Small proposal set
  await runner.runBenchmark(
    'Plinko Selection (10 proposals)',
    async () => {
      await plinko.process(smallProposals);
    },
    { iterations: 1000, warmupIterations: 100 }
  );

  // Benchmark 2: Large proposal set
  await runner.runBenchmark(
    'Plinko Selection (1000 proposals)',
    async () => {
      await plinko.process(largeProposals);
    },
    { iterations: 1000, warmupIterations: 100 }
  );
}

// ============================================================================
// EMBEDDING SIMILARITY BENCHMARKS
// ============================================================================

export async function benchmarkEmbeddingSimilarity(
  runner: BenchmarkRunner
): Promise<void> {
  console.log('\n--- Embedding Similarity Benchmarks ---');

  const bes = new BES({
    defaultDimensionality: 1024,
    defaultPrivacyTier: 'LOCAL',
  });

  // Create embeddings
  const embeddings = Array.from({ length: 1000 }, () =>
    Array.from({ length: 1024 }, () => Math.random())
  );

  // Benchmark 1: Grain creation
  await runner.runBenchmark(
    'Pollen Grain Creation',
    async () => {
      await bes.createGrain(
        Array.from({ length: 1024 }, () => Math.random()),
        'test-gardener'
      );
    },
    { iterations: 1000, warmupIterations: 100 }
  );

  // Benchmark 2: Similarity search (linear)
  await runner.runBenchmark(
    'Similarity Search (Linear)',
    () => {
      bes.findSimilar(
        Array.from({ length: 1024 }, () => Math.random()),
        10
      );
    },
    { iterations: 100, warmupIterations: 10 }
  );
}

// ============================================================================
// WORLD MODEL BENCHMARKS
// ============================================================================

export async function benchmarkWorldModel(
  runner: BenchmarkRunner
): Promise<void> {
  console.log('\n--- World Model Benchmarks ---');

  const worldModel = new WorldModel({
    latentDim: 64,
    hiddenDim: 256,
    learningRate: 0.001,
  });

  // Generate observations
  const observations = Array.from({ length: 100 }, () =>
    Array.from({ length: 128 }, () => Math.random())
  );

  // Benchmark 1: Encoding
  await runner.runBenchmark(
    'World Model Encode',
    async () => {
      await worldModel.encode(
        Array.from({ length: 128 }, () => Math.random())
      );
    },
    { iterations: 1000, warmupIterations: 100 }
  );

  // Benchmark 2: Training batch
  await runner.runBenchmark(
    'World Model Train Batch',
    async () => {
      await worldModel.train({
        observations: observations.slice(0, 32),
        actions: Array.from({ length: 32 }, () =>
          Array.from({ length: 10 }, () => Math.random())
        ),
        rewards: Array.from({ length: 32 }, () => Math.random()),
        nextObservations: observations.slice(0, 32),
        dones: Array.from({ length: 32 }, () => false),
      });
    },
    { iterations: 100, warmupIterations: 10 }
  );
}

// ============================================================================
// KV-ANCHOR BENCHMARKS
// ============================================================================

export async function benchmarkKVAnchors(
  runner: BenchmarkRunner
): Promise<void> {
  console.log('\n--- KV-Anchor Benchmarks ---');

  const pool = new KVAnchorPool({
    maxAnchors: 10000,
    maxAgeMs: 3600000,
    similarityThreshold: 0.8,
    maxMatches: 10,
    enableANN: true,
    annAlgorithm: 'hnsw',
  });

  // Benchmark 1: Pool stats
  await runner.runBenchmark(
    'KV-Anchor Pool Stats',
    async () => {
      pool.getStats();
    },
    { iterations: 1000, warmupIterations: 100 }
  );

  // Benchmark 2: Simple matching simulation
  await runner.runBenchmark(
    'KV-Anchor Similarity Calculation',
    async () => {
      const embedding1 = Array.from({ length: 128 }, () => Math.random());
      const embedding2 = Array.from({ length: 128 }, () => Math.random());

      // Calculate cosine similarity
      let dotProduct = 0;
      let norm1 = 0;
      let norm2 = 0;

      for (let i = 0; i < 128; i++) {
        dotProduct += embedding1[i] * embedding2[i];
        norm1 += embedding1[i] * embedding1[i];
        norm2 += embedding2[i] * embedding2[i];
      }

      const similarity = dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
    },
    { iterations: 1000, warmupIterations: 100 }
  );
}

// ============================================================================
// MAIN BENCHMARK SUITE
// ============================================================================

export async function runPerformanceBenchmarks(): Promise<void> {
  console.log('╔════════════════════════════════════════════════════════╗');
  console.log('║     POLLN Performance Benchmark Suite (Sprint 7)      ║');
  console.log('╚════════════════════════════════════════════════════════╝');

  const runner = new BenchmarkRunner();

  // Run all benchmarks
  await benchmarkAgentExecution(runner);
  await benchmarkColonyManagement(runner);
  await benchmarkPlinkoDecision(runner);
  await benchmarkEmbeddingSimilarity(runner);
  await benchmarkWorldModel(runner);
  await benchmarkKVAnchors(runner);

  // Print results
  runner.printResults();

  // Generate report
  const results = runner.getResults();
  const totalOps = results.reduce((sum, r) => sum + r.iterations, 0);
  const totalTime = results.reduce((sum, r) => sum + r.totalTime, 0);
  const totalMemory = results.reduce(
    (sum, r) => sum + r.memoryDelta,
    0
  );

  console.log('\n=== Summary ===');
  console.log(`Total operations: ${totalOps}`);
  console.log(`Total time: ${(totalTime / 1000).toFixed(2)}s`);
  console.log(`Total memory used: ${(totalMemory / 1024 / 1024).toFixed(2)}MB`);
  console.log(`Overall throughput: ${(totalOps / (totalTime / 1000)).toFixed(0)} ops/s`);
}

// Run if called directly
if (require.main === module) {
  runPerformanceBenchmarks()
    .then(() => {
      console.log('\n✓ All benchmarks completed successfully');
      process.exit(0);
    })
    .catch((error) => {
      console.error('\n✗ Benchmark failed:', error);
      process.exit(1);
    });
}
