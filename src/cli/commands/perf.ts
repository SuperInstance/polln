/**
 * Performance Monitoring CLI Command
 *
 * Features:
 * - Real-time performance metrics display
 * - Memory usage tracking
 * - CPU profiling integration
 * - Benchmark execution
 * - Performance comparison reports
 *
 * Sprint 7: Performance Optimization
 */

import { Command } from 'commander';
import { performance } from 'perf_hooks';
import { table } from 'table';
import * as fs from 'fs';
import * as path from 'path';

// ============================================================================
// PERFORMANCE MONITOR
// ============================================================================

interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  timestamp: number;
}

interface PerformanceSnapshot {
  timestamp: number;
  metrics: PerformanceMetric[];
  memory: NodeJS.MemoryUsage;
  cpu: NodeJS.CpuUsage;
}

class PerformanceMonitor {
  private snapshots: PerformanceSnapshot[] = [];
  private startTime: number;
  private startCpu: NodeJS.CpuUsage;
  private maxSnapshots: number = 1000;

  constructor() {
    this.startTime = Date.now();
    this.startCpu = process.cpuUsage();
  }

  /**
   * Capture current performance snapshot
   */
  capture(label: string): void {
    const now = Date.now();
    const snapshot: PerformanceSnapshot = {
      timestamp: now,
      metrics: [
        {
          name: 'uptime',
          value: (now - this.startTime) / 1000,
          unit: 's',
          timestamp: now,
        },
        {
          name: 'heap_used',
          value: process.memoryUsage().heapUsed / 1024 / 1024,
          unit: 'MB',
          timestamp: now,
        },
        {
          name: 'heap_total',
          value: process.memoryUsage().heapTotal / 1024 / 1024,
          unit: 'MB',
          timestamp: now,
        },
        {
          name: 'rss',
          value: process.memoryUsage().rss / 1024 / 1024,
          unit: 'MB',
          timestamp: now,
        },
        {
          name: 'external',
          value: process.memoryUsage().external / 1024 / 1024,
          unit: 'MB',
          timestamp: now,
        },
      ],
      memory: process.memoryUsage(),
      cpu: process.cpuUsage(this.startCpu),
    };

    this.snapshots.push(snapshot);

    // Limit snapshot history
    if (this.snapshots.length > this.maxSnapshots) {
      this.snapshots.shift();
    }
  }

  /**
   * Get current performance metrics
   */
  getCurrentMetrics(): PerformanceMetric[] {
    const latest = this.snapshots[this.snapshots.length - 1];
    return latest ? latest.metrics : [];
  }

  /**
   * Get performance delta between two snapshots
   */
  getDelta(fromIndex: number, toIndex: number): Record<string, number> {
    const from = this.snapshots[fromIndex];
    const to = this.snapshots[toIndex];

    if (!from || !to) {
      throw new Error('Invalid snapshot indices');
    }

    const timeDelta = (to.timestamp - from.timestamp) / 1000; // seconds

    const cpuUserDelta = (to.cpu.user - from.cpu.user) / 1e6; // Convert to seconds
    const cpuSystemDelta = (to.cpu.system - from.cpu.system) / 1e6;

    return {
      timeDelta,
      cpuUserPercent: (cpuUserDelta / timeDelta) * 100,
      cpuSystemPercent: (cpuSystemDelta / timeDelta) * 100,
      heapGrowthMB: (to.memory.heapUsed - from.memory.heapUsed) / 1024 / 1024,
      rssGrowthMB: (to.memory.rss - from.memory.rss) / 1024 / 1024,
    };
  }

  /**
   * Get all snapshots
   */
  getSnapshots(): PerformanceSnapshot[] {
    return [...this.snapshots];
  }

  /**
   * Clear all snapshots
   */
  clear(): void {
    this.snapshots = [];
    this.startTime = Date.now();
    this.startCpu = process.cpuUsage();
  }

  /**
   * Export snapshots to JSON
   */
  export(filePath: string): void {
    const data = {
      startTime: this.startTime,
      snapshots: this.snapshots,
    };

    fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
  }

  /**
   * Generate performance report
   */
  generateReport(): {
    summary: Record<string, number>;
    trends: Record<string, 'up' | 'down' | 'stable'>;
    recommendations: string[];
  } {
    if (this.snapshots.length < 2) {
      return {
        summary: {},
        trends: {},
        recommendations: ['Insufficient data for analysis'],
      };
    }

    const first = this.snapshots[0];
    const last = this.snapshots[this.snapshots.length - 1];

    const summary = {
      uptime: (last.timestamp - first.timestamp) / 1000,
      avgHeapUsed: 0,
      peakHeapUsed: 0,
      heapGrowth: 0,
      avgCpuUser: 0,
      avgCpuSystem: 0,
    };

    let totalHeap = 0;
    let peakHeap = 0;

    for (const snapshot of this.snapshots) {
      const heapUsed = snapshot.metrics.find(m => m.name === 'heap_used')?.value || 0;
      totalHeap += heapUsed;
      if (heapUsed > peakHeap) {
        peakHeap = heapUsed;
      }
    }

    summary.avgHeapUsed = totalHeap / this.snapshots.length;
    summary.peakHeapUsed = peakHeap;
    summary.heapGrowth = (last.memory.heapUsed - first.memory.heapUsed) / 1024 / 1024;

    const duration = (last.timestamp - first.timestamp) / 1000;
    const cpuUser = (last.cpu.user - first.cpu.user) / 1e6;
    const cpuSystem = (last.cpu.system - first.cpu.system) / 1e6;

    summary.avgCpuUser = (cpuUser / duration) * 100;
    summary.avgCpuSystem = (cpuSystem / duration) * 100;

    // Analyze trends
    const trends: Record<string, 'up' | 'down' | 'stable'> = {};
    const recommendations: string[] = [];

    // Memory trend
    const midPoint = Math.floor(this.snapshots.length / 2);
    const firstHalfAvg = this.snapshots.slice(0, midPoint).reduce(
      (sum, s) => sum + (s.metrics.find(m => m.name === 'heap_used')?.value || 0),
      0
    ) / midPoint;

    const secondHalfAvg = this.snapshots.slice(midPoint).reduce(
      (sum, s) => sum + (s.metrics.find(m => m.name === 'heap_used')?.value || 0),
      0
    ) / (this.snapshots.length - midPoint);

    const growthRate = (secondHalfAvg - firstHalfAvg) / firstHalfAvg;

    if (growthRate > 0.1) {
      trends.memory = 'up';
      recommendations.push('Memory usage is trending upward. Consider investigating memory leaks.');
    } else if (growthRate < -0.1) {
      trends.memory = 'down';
    } else {
      trends.memory = 'stable';
    }

    // CPU trend
    if (summary.avgCpuUser > 80) {
      recommendations.push('High CPU usage detected. Consider profiling hot paths.');
    }

    // Heap size
    if (summary.peakHeapUsed > 500) {
      recommendations.push('Peak heap usage exceeds 500MB. Consider memory optimization.');
    }

    return {
      summary,
      trends,
      recommendations,
    };
  }
}

// ============================================================================
// BENCHMARK RUNNER
// ============================================================================

interface BenchmarkResult {
  name: string;
  iterations: number;
  totalTime: number;
  avgTime: number;
  minTime: number;
  maxTime: number;
  opsPerSecond: number;
}

async function runBenchmark(
  name: string,
  fn: () => Promise<void>,
  iterations: number
): Promise<BenchmarkResult> {
  const times: number[] = [];

  // Warmup
  for (let i = 0; i < Math.min(10, iterations); i++) {
    await fn();
  }

  // Benchmark
  for (let i = 0; i < iterations; i++) {
    const start = performance.now();
    await fn();
    const end = performance.now();
    times.push(end - start);
  }

  times.sort((a, b) => a - b);

  const totalTime = times.reduce((sum, t) => sum + t, 0);
  const avgTime = totalTime / iterations;
  const minTime = times[0];
  const maxTime = times[iterations - 1];
  const opsPerSecond = 1000 / avgTime;

  return {
    name,
    iterations,
    totalTime,
    avgTime,
    minTime,
    maxTime,
    opsPerSecond,
  };
}

// ============================================================================
// CLI COMMAND
// ============================================================================

export function registerPerfCommand(program: Command): void {
  const perfCmd = program
    .command('perf')
    .description('Performance monitoring and benchmarking tools');

  // Monitor subcommand
  perfCmd
    .command('monitor')
    .description('Monitor performance in real-time')
    .option('-i, --interval <ms>', 'Snapshot interval in milliseconds', '1000')
    .option('-d, --duration <seconds>', 'Monitoring duration', '60')
    .option('-o, --output <file>', 'Output file for results')
    .action(async (options) => {
      const monitor = new PerformanceMonitor();
      const interval = parseInt(options.interval);
      const duration = parseInt(options.duration) * 1000;

      console.log(`\n🔍 Monitoring performance for ${duration / 1000}s...\n`);

      const intervalId = setInterval(() => {
        monitor.capture('auto');
      }, interval);

      // Wait for duration
      await new Promise(resolve => setTimeout(resolve, duration));
      clearInterval(intervalId);

      // Generate report
      const report = monitor.generateReport();

      console.log('\n📊 Performance Report\n');
      console.log('Summary:');
      console.log(`  Uptime: ${report.summary.uptime.toFixed(2)}s`);
      console.log(`  Avg Heap Used: ${report.summary.avgHeapUsed.toFixed(2)}MB`);
      console.log(`  Peak Heap Used: ${report.summary.peakHeapUsed.toFixed(2)}MB`);
      console.log(`  Heap Growth: ${report.summary.heapGrowth.toFixed(2)}MB`);
      console.log(`  Avg CPU User: ${report.summary.avgCpuUser.toFixed(2)}%`);
      console.log(`  Avg CPU System: ${report.summary.avgCpuSystem.toFixed(2)}%`);

      console.log('\nTrends:');
      for (const [key, trend] of Object.entries(report.trends)) {
        const icon = trend === 'up' ? '📈' : trend === 'down' ? '📉' : '➡️';
        console.log(`  ${icon} ${key}: ${trend}`);
      }

      if (report.recommendations.length > 0) {
        console.log('\n💡 Recommendations:');
        for (const rec of report.recommendations) {
          console.log(`  • ${rec}`);
        }
      }

      // Export if requested
      if (options.output) {
        monitor.export(options.output);
        console.log(`\n✓ Results exported to ${options.output}`);
      }
    });

  // Benchmark subcommand
  perfCmd
    .command('benchmark')
    .description('Run performance benchmarks')
    .option('-i, --iterations <n>', 'Number of iterations', '1000')
    .option('-o, --output <file>', 'Output file for results')
    .action(async (options) => {
      const iterations = parseInt(options.iterations);

      console.log('\n⚡ Running performance benchmarks...\n');

      const results: BenchmarkResult[] = [];

      // Benchmark: Object creation
      results.push(await runBenchmark('Object Creation', async () => {
        const obj = { a: 1, b: 2, c: 3 };
        JSON.stringify(obj);
      }, iterations));

      // Benchmark: Map operations
      const testMap = new Map();
      results.push(await runBenchmark('Map Set', async () => {
        testMap.set(Math.random().toString(), Math.random());
      }, iterations));

      results.push(await runBenchmark('Map Get', async () => {
        testMap.get(Math.random().toString());
      }, iterations));

      // Benchmark: Array operations
      const testArray: number[] = [];
      results.push(await runBenchmark('Array Push', async () => {
        testArray.push(Math.random());
      }, iterations));

      results.push(await runBenchmark('Array Find', async () => {
        testArray.find(v => v === Math.random());
      }, iterations));

      // Display results
      console.log('\n📊 Benchmark Results\n');

      const data = [
        ['Benchmark', 'Iterations', 'Avg Time', 'Min Time', 'Max Time', 'Ops/s'],
        ...results.map(r => [
          r.name,
          r.iterations.toString(),
          `${r.avgTime.toFixed(4)}ms`,
          `${r.minTime.toFixed(4)}ms`,
          `${r.maxTime.toFixed(4)}ms`,
          r.opsPerSecond.toFixed(0),
        ]),
      ];

      console.log(table(data));

      // Export if requested
      if (options.output) {
        fs.writeFileSync(options.output, JSON.stringify(results, null, 2));
        console.log(`\n✓ Results exported to ${options.output}`);
      }
    });

  // Compare subcommand
  perfCmd
    .command('compare <file1> <file2>')
    .description('Compare two benchmark results')
    .action((file1, file2) => {
      console.log(`\n📊 Comparing ${file1} vs ${file2}\n`);

      const data1 = JSON.parse(fs.readFileSync(file1, 'utf-8'));
      const data2 = JSON.parse(fs.readFileSync(file2, 'utf-8'));

      console.log('Benchmark Comparison:');
      console.table(
        data1.map((r1: BenchmarkResult, i: number) => {
          const r2 = data2[i];
          const improvement = r1 && r2
            ? (((r1.avgTime - r2.avgTime) / r1.avgTime) * 100).toFixed(2)
            : 'N/A';

          return {
            Benchmark: r1?.name || 'N/A',
            Before: r1 ? `${r1.avgTime.toFixed(4)}ms` : 'N/A',
            After: r2 ? `${r2.avgTime.toFixed(4)}ms` : 'N/A',
            Improvement: improvement !== 'N/A' ? `${improvement}%` : 'N/A',
          };
        })
      );
    });

  // Profile subcommand
  perfCmd
    .command('profile <script>')
    .description('Profile a script and generate performance report')
    .option('-o, --output <file>', 'Output file for profile')
    .action(async (script, options) => {
      const monitor = new PerformanceMonitor();

      console.log(`\n🔍 Profiling ${script}...\n`);

      monitor.capture('start');

      // Run script
      try {
        await import(path.resolve(process.cwd(), script));
      } catch (error) {
        console.error(`Error running script: ${error}`);
        process.exit(1);
      }

      monitor.capture('end');

      // Generate report
      const report = monitor.generateReport();

      console.log('\n📊 Profile Report\n');
      console.log(JSON.stringify(report, null, 2));

      // Export if requested
      const outputFile = options.output || `${script}.profile.json`;
      monitor.export(outputFile);
      console.log(`\n✓ Profile saved to ${outputFile}`);
    });
}
