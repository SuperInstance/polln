/**
 * SMP Baseline Comparison Tests
 */

import { describe, it, expect } from '@jest/globals';
import {
  MonolithicBaseline,
  TileChainBuilder,
  AccuracyEquivalentFinder,
  ParetoFrontierCalculator,
  ComparisonEngine,
  ComparisonReportGenerator,
} from '../baseline-comparison.js';

describe('MonolithicBaseline', () => {
  it('should create baseline instance', () => {
    const baseline = new MonolithicBaseline('gpt-4', 100);
    expect(baseline).toBeDefined();
  });

  it('should execute sentiment analysis', async () => {
    const baseline = new MonolithicBaseline('gpt-4', 100);
    const result = await baseline.execute('I love this product!', { taskType: 'sentiment' });

    expect(result.approach).toBe('monolithic');
    expect(result.metrics.latency).toBeGreaterThan(0);
    expect(result.metrics.accuracy).toBeGreaterThan(0);
    expect(result.metrics.confidence).toBeGreaterThan(0);
    expect(result.metrics.energy).toBeGreaterThan(0);
  });

  it('should execute classification', async () => {
    const baseline = new MonolithicBaseline('gpt-4', 100);
    const result = await baseline.execute('AI is amazing', { taskType: 'classification' });

    expect(result.output).toBeDefined();
    expect(result.metrics.accuracy).toBeGreaterThan(0);
  });

  it('should execute reasoning', async () => {
    const baseline = new MonolithicBaseline('gpt-4', 100);
    const result = await baseline.execute('If A then B', { taskType: 'reasoning' });

    expect(result.output).toBeDefined();
    expect(result.metrics.latency).toBeGreaterThan(0);
  });
});

describe('TileChainBuilder', () => {
  it('should build sequential pattern for sentiment', () => {
    const pattern = TileChainBuilder.buildSequential('sentiment');

    expect(pattern.type).toBe('sequential');
    expect(pattern.tiles.length).toBeGreaterThan(0);
    expect(pattern.tiles[0].type).toBe('preprocessing');
  });

  it('should build parallel pattern for classification', () => {
    const pattern = TileChainBuilder.buildParallel('classification');

    expect(pattern.type).toBe('parallel');
    expect(pattern.tiles.length).toBeGreaterThan(0);
  });

  it('should build mixed pattern', () => {
    const pattern = TileChainBuilder.buildMixed('sentiment');

    expect(pattern.type).toBe('mixed');
    expect(pattern.tiles.length).toBeGreaterThan(0);
  });

  it('should estimate metrics for sequential pattern', () => {
    const pattern = TileChainBuilder.buildSequential('sentiment');
    const metrics = TileChainBuilder.estimateMetrics(pattern);

    expect(metrics.latency).toBeGreaterThan(0);
    expect(metrics.confidence).toBeGreaterThan(0);
    expect(metrics.confidence).toBeLessThanOrEqual(1);
    expect(metrics.energy).toBeGreaterThan(0);
  });

  it('should estimate metrics for parallel pattern', () => {
    const pattern = TileChainBuilder.buildParallel('sentiment');
    const metrics = TileChainBuilder.estimateMetrics(pattern);

    expect(metrics.latency).toBeGreaterThan(0);
    expect(metrics.confidence).toBeGreaterThan(0);
    expect(metrics.energy).toBeGreaterThan(0);
  });

  it('parallel should be faster than sequential for same task', () => {
    const sequential = TileChainBuilder.buildSequential('sentiment');
    const parallel = TileChainBuilder.buildParallel('sentiment');

    const seqMetrics = TileChainBuilder.estimateMetrics(sequential);
    const parMetrics = TileChainBuilder.estimateMetrics(parallel);

    expect(parMetrics.latency).toBeLessThan(seqMetrics.latency);
  });
});

describe('AccuracyEquivalentFinder', () => {
  it('should find patterns matching baseline accuracy', () => {
    const patterns = [
      TileChainBuilder.buildSequential('sentiment'),
      TileChainBuilder.buildParallel('sentiment'),
      TileChainBuilder.buildMixed('sentiment'),
    ];

    const baselineAccuracy = 0.85;
    const equivalent = AccuracyEquivalentFinder.findEquivalent(baselineAccuracy, patterns, 0.05);

    expect(equivalent.length).toBeGreaterThan(0);
  });

  it('should adjust pattern to target accuracy', () => {
    const pattern = TileChainBuilder.buildSequential('sentiment');
    const targetAccuracy = 0.90;

    const adjusted = AccuracyEquivalentFinder.adjustToTarget(pattern, targetAccuracy);

    expect(adjusted.tiles.length).toBe(pattern.tiles.length);
    expect(adjusted.type).toBe(pattern.type);
  });
});

describe('ParetoFrontierCalculator', () => {
  it('should calculate Pareto frontier', () => {
    const results = [
      {
        approach: 'smp' as const,
        metrics: {
          latency: 100,
          accuracy: 0.85,
          confidence: 0.85,
          energy: 250,
          throughput: 10,
          memory: 2000,
        },
        output: {},
        timestamp: Date.now(),
        tilePattern: TileChainBuilder.buildSequential('sentiment'),
      },
      {
        approach: 'smp' as const,
        metrics: {
          latency: 50,
          accuracy: 0.88,
          confidence: 0.88,
          energy: 100,
          throughput: 20,
          memory: 500,
        },
        output: {},
        timestamp: Date.now(),
        tilePattern: TileChainBuilder.buildParallel('sentiment'),
      },
    ];

    const frontier = ParetoFrontierCalculator.calculate(results);

    expect(frontier.length).toBeGreaterThan(0);
    expect(frontier.length).toBeLessThanOrEqual(results.length);
  });

  it('should rank solutions by Pareto dominance', () => {
    const results = [
      {
        approach: 'smp' as const,
        metrics: {
          latency: 100,
          accuracy: 0.85,
          confidence: 0.85,
          energy: 250,
          throughput: 10,
          memory: 2000,
        },
        output: {},
        timestamp: Date.now(),
        tilePattern: TileChainBuilder.buildSequential('sentiment'),
      },
      {
        approach: 'smp' as const,
        metrics: {
          latency: 50,
          accuracy: 0.88,
          confidence: 0.88,
          energy: 100,
          throughput: 20,
          memory: 500,
        },
        output: {},
        timestamp: Date.now(),
        tilePattern: TileChainBuilder.buildParallel('sentiment'),
      },
    ];

    const ranks = ParetoFrontierCalculator.rank(results);

    expect(ranks).toHaveLength(results.length);
    expect(ranks.every(r => r > 0)).toBe(true);
  });
});

describe('ComparisonEngine', () => {
  it('should run comparison', async () => {
    const baseline = new MonolithicBaseline('gpt-4', 100);
    const engine = new ComparisonEngine(baseline);

    const report = await engine.compare('I love this!', 'sentiment');

    expect(report.id).toBeDefined();
    expect(report.task).toBe('sentiment');
    expect(report.prompt).toBe('I love this!');
    expect(report.baseline).toBeDefined();
    expect(report.smpResults).toBeDefined();
    expect(report.smpResults.length).toBeGreaterThan(0);
    expect(report.winner).toMatch(/monolithic|smp|tie/);
    expect(report.improvement).toBeDefined();
  });

  it('should determine winner correctly', async () => {
    const baseline = new MonolithicBaseline('gpt-4', 100);
    const engine = new ComparisonEngine(baseline);

    const report = await engine.compare('Great product!', 'sentiment');

    expect(['monolithic', 'smp', 'tie']).toContain(report.winner);
  });

  it('should calculate improvement percentages', async () => {
    const baseline = new MonolithicBaseline('gpt-4', 100);
    const engine = new ComparisonEngine(baseline);

    const report = await engine.compare('Amazing!', 'sentiment');

    expect(typeof report.improvement.latency).toBe('number');
    expect(typeof report.improvement.accuracy).toBe('number');
    expect(typeof report.improvement.energy).toBe('number');
  });

  it('should assign Pareto rank', async () => {
    const baseline = new MonolithicBaseline('gpt-4', 100);
    const engine = new ComparisonEngine(baseline);

    const report = await engine.compare('Love it!', 'sentiment');

    expect(typeof report.paretoRank).toBe('number');
    expect(report.paretoRank).toBeGreaterThan(0);
  });
});

describe('ComparisonReportGenerator', () => {
  it('should generate text report', () => {
    const report = {
      id: 'test-id',
      task: 'sentiment',
      prompt: 'Test prompt',
      baseline: {
        approach: 'monolithic' as const,
        metrics: {
          latency: 100,
          accuracy: 0.85,
          confidence: 0.85,
          energy: 250,
          throughput: 10,
          memory: 2000,
        },
        output: {},
        timestamp: Date.now(),
      },
      smpResults: [
        {
          approach: 'smp' as const,
          metrics: {
            latency: 50,
            accuracy: 0.88,
            confidence: 0.88,
            energy: 100,
            throughput: 20,
            memory: 500,
          },
          output: {},
          tileCount: 4,
          tilePattern: TileChainBuilder.buildSequential('sentiment'),
          timestamp: Date.now(),
        },
      ],
      winner: 'smp' as const,
      improvement: {
        latency: 50,
        accuracy: 3.5,
        energy: 60,
      },
      paretoRank: 1,
      timestamp: Date.now(),
    };

    const text = ComparisonReportGenerator.generateText(report);

    expect(text).toContain('SMP BASELINE COMPARISON REPORT');
    expect(text).toContain('sentiment');
    expect(text).toContain('Test prompt');
    expect(text).toContain('MONOLITHIC BASELINE');
    expect(text).toContain('SMP TILE CHAINS');
    expect(text).toContain('SUMMARY');
  });

  it('should generate JSON report', () => {
    const report = {
      id: 'test-id',
      task: 'sentiment',
      prompt: 'Test prompt',
      baseline: {
        approach: 'monolithic' as const,
        metrics: {
          latency: 100,
          accuracy: 0.85,
          confidence: 0.85,
          energy: 250,
          throughput: 10,
          memory: 2000,
        },
        output: {},
        timestamp: Date.now(),
      },
      smpResults: [],
      winner: 'tie' as const,
      improvement: { latency: 0, accuracy: 0, energy: 0 },
      paretoRank: 1,
      timestamp: Date.now(),
    };

    const json = ComparisonReportGenerator.generateJSON(report);
    const parsed = JSON.parse(json);

    expect(parsed.id).toBe('test-id');
    expect(parsed.task).toBe('sentiment');
  });

  it('should generate markdown report', () => {
    const report = {
      id: 'test-id',
      task: 'sentiment',
      prompt: 'Test prompt',
      baseline: {
        approach: 'monolithic' as const,
        metrics: {
          latency: 100,
          accuracy: 0.85,
          confidence: 0.85,
          energy: 250,
          throughput: 10,
          memory: 2000,
        },
        output: {},
        timestamp: Date.now(),
      },
      smpResults: [],
      winner: 'tie' as const,
      improvement: { latency: 0, accuracy: 0, energy: 0 },
      paretoRank: 1,
      timestamp: Date.now(),
    };

    const markdown = ComparisonReportGenerator.generateMarkdown(report);

    expect(markdown).toContain('# SMP Baseline Comparison Report');
    expect(markdown).toContain('## Task: sentiment');
  });

  it('should generate HTML report', () => {
    const report = {
      id: 'test-id',
      task: 'sentiment',
      prompt: 'Test prompt',
      baseline: {
        approach: 'monolithic' as const,
        metrics: {
          latency: 100,
          accuracy: 0.85,
          confidence: 0.85,
          energy: 250,
          throughput: 10,
          memory: 2000,
        },
        output: {},
        timestamp: Date.now(),
      },
      smpResults: [],
      winner: 'tie' as const,
      improvement: { latency: 0, accuracy: 0, energy: 0 },
      paretoRank: 1,
      timestamp: Date.now(),
    };

    const html = ComparisonReportGenerator.generateHTML(report);

    expect(html).toContain('<!DOCTYPE html>');
    expect(html).toContain('SMP Baseline Comparison Report');
    expect(html).toContain('</html>');
  });
});

describe('Integration Tests', () => {
  it('should run full comparison workflow', async () => {
    const baseline = new MonolithicBaseline('gpt-4', 100);
    const engine = new ComparisonEngine(baseline);

    const report = await engine.compare('This is amazing!', 'sentiment', {
      iterations: 2,
      warmup: true,
    });

    expect(report).toBeDefined();
    expect(report.smpResults.length).toBe(3); // sequential, parallel, mixed
  });

  it('should handle different task types', async () => {
    const baseline = new MonolithicBaseline('gpt-4', 100);
    const engine = new ComparisonEngine(baseline);

    const sentimentReport = await engine.compare('Love it!', 'sentiment');
    const classificationReport = await engine.compare('AI research', 'classification');
    const reasoningReport = await engine.compare('If A then B', 'reasoning');

    expect(sentimentReport.task).toBe('sentiment');
    expect(classificationReport.task).toBe('classification');
    expect(reasoningReport.task).toBe('reasoning');
  });
});
