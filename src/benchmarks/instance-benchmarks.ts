/**
 * Instance Type Benchmarks
 *
 * Benchmarks for all 19 SuperInstance types with different configurations
 */

import { SuperInstanceSystem, InstanceType } from '../superinstance';
import { performanceMonitor } from '../superinstance/performance/SuperInstancePerformanceMonitor';
import { BenchmarkConfig, BenchmarkResult } from './benchmark-runner';

export class InstanceBenchmarkRunner {
  private system: SuperInstanceSystem;
  private config: BenchmarkConfig;

  constructor(config: BenchmarkConfig) {
    this.config = config;
    this.system = new SuperInstanceSystem();
  }

  async runAll(): Promise<BenchmarkResult[]> {
    const results: BenchmarkResult[] = [];

    // Test all available instance types
    const instanceTypes = SuperInstanceSystem.getAvailableTypes();

    for (const type of instanceTypes) {
      console.log(`  📊 Benchmarking ${InstanceType[type]} instances...`);

      // Instance creation benchmarks
      results.push(await this.benchmarkInstanceCreation(type));

      // Instance operation benchmarks
      results.push(await this.benchmarkInstanceOperations(type));

      // Instance serialization benchmarks
      results.push(await this.benchmarkInstanceSerialization(type));

      // Instance communication benchmarks
      results.push(await this.benchmarkInstanceCommunication(type));
    }

    // Special benchmarks for confidence cascade
    results.push(await this.benchmarkConfidenceCascade());

    // Special benchmarks for rate-based changes
    results.push(await this.benchmarkRateBasedChanges());

    return results;
  }

  private async benchmarkInstanceCreation(type: InstanceType): Promise<BenchmarkResult> {
    const times: number[] = [];
    let memoryBefore = process.memoryUsage().heapUsed;
    let peakMemory = memoryBefore;

    // Warmup
    for (let i = 0; i < this.config.warmupRuns; i++) {
      await this.createInstance(type, `warmup-${i}`);
    }

    // Actual benchmark
    for (let i = 0; i < this.config.iterations; i++) {
      const start = performance.now();
      await this.createInstance(type, `bench-${i}`);
      const end = performance.now();
      times.push(end - start);

      // Track memory
      const currentMemory = process.memoryUsage().heapUsed;
      peakMemory = Math.max(peakMemory, currentMemory);
    }

    const memoryAfter = process.memoryUsage().heapUsed;

    return this.createResult(
      `${InstanceType[type]} Instance Creation`,
      'instance_creation',
      times,
      {
        before: memoryBefore,
        after: memoryAfter,
        peak: peakMemory,
        delta: memoryAfter - memoryBefore
      },
      {
        instanceType: InstanceType[type],
        iterations: this.config.iterations
      }
    );
  }

  private async benchmarkInstanceOperations(type: InstanceType): Promise<BenchmarkResult> {
    const times: number[] = [];
    let peakMemory = 0;

    // Create test instance
    const instance = await this.createInstance(type, 'operations-test');
    const memoryBefore = process.memoryUsage().heapUsed;
    peakMemory = memoryBefore;

    // Test instance-specific operations
    const operations = this.getInstanceOperations(type);

    for (let i = 0; i < this.config.iterations; i++) {
      const start = performance.now();

      // Run operations based on instance type
      await this.runInstanceOperations(instance, operations);

      const end = performance.now();
      times.push(end - start);

      // Track memory
      const currentMemory = process.memoryUsage().heapUsed;
      peakMemory = Math.max(peakMemory, currentMemory);
    }

    const memoryAfter = process.memoryUsage().heapUsed;

    return this.createResult(
      `${InstanceType[type]} Operations`,
      'instance_operations',
      times,
      {
        before: memoryBefore,
        after: memoryAfter,
        peak: peakMemory,
        delta: memoryAfter - memoryBefore
      },
      {
        instanceType: InstanceType[type],
        operations: operations.length
      }
    );
  }

  private async benchmarkInstanceSerialization(type: InstanceType): Promise<BenchmarkResult> {
    const times: number[] = [];
    let peakMemory = 0;

    // Create test instance with data
    const instance = await this.createInstance(type, 'serialization-test', true);
    const memoryBefore = process.memoryUsage().heapUsed;
    peakMemory = memoryBefore;

    for (let i = 0; i < this.config.iterations; i++) {
      const start = performance.now();

      // Serialize
      const snapshot = await instance.serialize();

      // Deserialize
      await instance.deserialize(snapshot);

      const end = performance.now();
      times.push(end - start);

      // Track memory
      const currentMemory = process.memoryUsage().heapUsed;
      peakMemory = Math.max(peakMemory, currentMemory);
    }

    const memoryAfter = process.memoryUsage().heapUsed;

    return this.createResult(
      `${InstanceType[type]} Serialization`,
      'instance_serialization',
      times,
      {
        before: memoryBefore,
        after: memoryAfter,
        peak: peakMemory,
        delta: memoryAfter - memoryBefore
      },
      {
        instanceType: InstanceType[type],
        iterations: this.config.iterations
      }
    );
  }

  private async benchmarkInstanceCommunication(type: InstanceType): Promise<BenchmarkResult> {
    const times: number[] = [];
    let peakMemory = 0;

    // Create two instances for communication
    const sender = await this.createInstance(type, 'sender-test');
    const receiver = await this.createInstance(type, 'receiver-test');

    const memoryBefore = process.memoryUsage().heapUsed;
    peakMemory = memoryBefore;

    for (let i = 0; i < this.config.iterations; i++) {
      const start = performance.now();

      // Send message
      const message = {
        id: `msg-${i}`,
        type: 'data',
        sender: sender.id,
        recipient: receiver.id,
        payload: { data: `message-${i}` },
        timestamp: Date.now()
      };

      await sender.sendMessage(message);
      await receiver.receiveMessage(message);

      const end = performance.now();
      times.push(end - start);

      // Track memory
      const currentMemory = process.memoryUsage().heapUsed;
      peakMemory = Math.max(peakMemory, currentMemory);
    }

    const memoryAfter = process.memoryUsage().heapUsed;

    return this.createResult(
      `${InstanceType[type]} Communication`,
      'instance_communication',
      times,
      {
        before: memoryBefore,
        after: memoryAfter,
        peak: peakMemory,
        delta: memoryAfter - memoryBefore
      },
      {
        instanceType: InstanceType[type],
        iterations: this.config.iterations
      }
    );
  }

  private async benchmarkConfidenceCascade(): Promise<BenchmarkResult> {
    console.log(`  📊 Benchmarking Confidence Cascade...`);

    const times: number[] = [];
    let peakMemory = 0;

    const memoryBefore = process.memoryUsage().heapUsed;
    peakMemory = memoryBefore;

    // Create instances with confidence cascade
    const instances = [];
    for (let i = 0; i < 100; i++) {
      const instance = await this.createInstance(InstanceType.DATA_BLOCK, `confidence-${i}`);
      instance.confidenceScore = Math.random();
      instances.push(instance);
    }

    // Time confidence updates
    for (let i = 0; i < this.config.iterations; i++) {
      const start = performance.now();

      // Update confidence scores
      instances.forEach(instance => {
        instance.updateConfidence(Math.random());
        instance.updateConfidenceZone();
      });

      const end = performance.now();
      times.push(end - start);

      // Track memory
      const currentMemory = process.memoryUsage().heapUsed;
      peakMemory = Math.max(peakMemory, currentMemory);
    }

    const memoryAfter = process.memoryUsage().heapUsed;

    return this.createResult(
      'Confidence Cascade',
      'confidence_cascade',
      times,
      {
        before: memoryBefore,
        after: memoryAfter,
        peak: peakMemory,
        delta: memoryAfter - memoryBefore
      },
      {
        instances: 100,
        iterations: this.config.iterations
      }
    );
  }

  private async benchmarkRateBasedChanges(): Promise<BenchmarkResult> {
    console.log(`  📊 Benchmarking Rate-Based Changes...`);

    const times: number[] = [];
    let peakMemory = 0;

    const memoryBefore = process.memoryUsage().heapUsed;
    peakMemory = memoryBefore;

    // Instance for rate benchmarks
    const instance = await this.createInstance(InstanceType.DATA_BLOCK, 'rate-test');

    for (let i = 0; i < this.config.iterations; i++) {
      const start = performance.now();

      // Update rate state with random values
      instance.updateRateState(Math.random() * 1000, Date.now());

      // Predict future state
      instance.predictState(Date.now() + 1000);

      const end = performance.now();
      times.push(end - start);

      // Track memory
      const currentMemory = process.memoryUsage().heapUsed;
      peakMemory = Math.max(peakMemory, currentMemory);
    }

    const memoryAfter = process.memoryUsage().heapUsed;

    return this.createResult(
      'Rate-Based Changes',
      'rate_based_changes',
      times,
      {
        before: memoryBefore,
        after: memoryAfter,
        peak: peakMemory,
        delta: memoryAfter - memoryBefore
      },
      {
        iterations: this.config.iterations
      }
    );
  }

  private createResult(
    name: string,
    category: string,
    times: number[],
    memory: any,
    metadata: Record<string, any>
  ): BenchmarkResult {
    times.sort((a, b) => a - b);
    const iterations = times.length;
    const totalTime = times.reduce((sum, t) => sum + t, 0);
    const avgTime = totalTime / iterations;
    const minTime = times[0];
    const maxTime = times[times.length - 1];
    const p50 = times[Math.floor(iterations * 0.5)];
    const p95 = times[Math.floor(iterations * 0.95)];
    const p99 = times[Math.floor(iterations * 0.99)];

    // Record metrics
    performanceMonitor.recordMetric(`${category}_avg`, avgTime, 'ms');
    performanceMonitor.recordMetric(`${category}_p95`, p95, 'ms');
    performanceMonitor.recordMetric(`${category}_p99`, p99, 'ms');

    return {
      name,
      category,
      iterations,
      timing: {
        avg: avgTime,
        min: minTime,
        max: maxTime,
        p50,
        p95,
        p99
      },
      memory,
      throughput: {
        opsPerSecond: 1000 / avgTime
      },
      errors: 0,
      metadata
    };
  }

  private async createInstance(type: InstanceType, id: string, withData = false) {
    const baseConfig = {
      type,
      id: `${type}-${id}`,
      name: `${type} Benchmark`,
      description: 'Benchmark instance',
      cellPosition: { row: 0, col: 0 },
      spreadsheetId: 'benchmark-spreadsheet'
    };

    let config = baseConfig;

    // Add type-specific configuration
    switch (type) {
      case InstanceType.DATA_BLOCK:
        config = { ...config, dataFormat: 'json' };
        if (withData) {
          config['data'] = Array.from({ length: 1000 }, (_, i) => ({
            id: i,
            value: Math.random(),
            timestamp: Date.now()
          }));
        }
        break;
      case InstanceType.PROCESS:
        config = {
          ...config,
          command: 'echo',
          arguments: ['test'],
          workingDirectory: '/tmp'
        };
        break;
      case InstanceType.LEARNING_AGENT:
        config = {
          ...config,
          modelType: 'classification',
          trainingData: withData ? Array.from({ length: 100 }, (_, i) => ({
            input: [i],
            output: i % 2
          })) : undefined
        };
        break;
      // Add other type-specific config as needed
    }

    return await this.system.createInstance(config);
  }

  private getInstanceOperations(type: InstanceType): string[] {
    const allOperations = {
      [InstanceType.DATA_BLOCK]: ['read', 'write', 'query'],
      [InstanceType.PROCESS]: ['start', 'stop', 'monitor'],
      [InstanceType.LEARNING_AGENT]: ['train', 'predict', 'evaluate'],
      [InstanceType.VIEWPORT]: ['render', 'update', 'resize'],
      [InstanceType.CONNECTOR]: ['connect', 'disconnect', 'transfer'],
      [InstanceType.VALIDATOR]: ['validate', 'check', 'audit'],
      [InstanceType.TRIGGER]: ['trigger', 'reset', 'configure'],
      [InstanceType.CACHE]: ['get', 'set', 'clear'],
      // Add operations for other types
    };

    return allOperations[type] || ['operate'];
  }

  private async runInstanceOperations(instance: any, operations: string[]) {
    // Simulate operations based on instance type
    for (const op of operations) {
      switch (op) {
        case 'read':
          await instance.read({ limit: 100 });
          break;
        case 'write':
          await instance.write({ data: Math.random() });
          break;
        case 'train':
          if (instance.train) {
            await instance.train({ epochs: 1 });
          }
          break;
        case 'predict':
          if (instance.predict) {
            await instance.predict([Math.random()]);
          }
          break;
        default:
          // Simulate operation
          await new Promise(resolve => setTimeout(resolve, 0.1));
      }
    }
  }
}