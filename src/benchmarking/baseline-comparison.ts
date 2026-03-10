/**
 * SMP Baseline Comparison Infrastructure
 *
 * Compare SMP tile chains vs monolithic LLM calls on:
 * - Latency (ms)
 * - Accuracy (score)
 * - Confidence (0-1)
 * - Energy (arbitrary units)
 *
 * FAIR COMPARISON: Accuracy-equivalent baselines
 */

import { v4 } from 'uuid';

// ============================================================================
// CORE TYPES
// ============================================================================

export interface ComparisonMetrics {
  latency: number;        // milliseconds
  accuracy: number;       // 0-1 score
  confidence: number;     // 0-1 confidence
  energy: number;         // arbitrary units
  throughput: number;     // requests/second
  memory: number;         // MB
}

export interface BaselineResult {
  approach: 'monolithic' | 'smp';
  metrics: ComparisonMetrics;
  output: unknown;
  tileCount?: number;
  tilePattern?: TilePattern;
  timestamp: number;
}

export interface ComparisonReport {
  id: string;
  task: string;
  prompt: string;
  baseline: BaselineResult;
  smpResults: BaselineResult[];
  winner: 'monolithic' | 'smp' | 'tie';
  improvement: {
    latency: number;      // percentage improvement
    accuracy: number;     // percentage difference
    energy: number;       // percentage improvement
  };
  paretoRank: number;     // 1 = best
  timestamp: number;
}

export interface TilePattern {
  type: 'sequential' | 'parallel' | 'mixed';
  tiles: TileSpec[];
  connections?: Connection[];
}

export interface TileSpec {
  id: string;
  name: string;
  type: string;
  estimatedConfidence: number;
  estimatedLatency: number;
}

export interface Connection {
  from: string;
  to: string;
  type: 'sequence' | 'parallel';
}

// ============================================================================
// MONOLITHIC LLM BASELINE
// ============================================================================

/**
 * Monolithic LLM wrapper for baseline comparison
 */
export class MonolithicBaseline {
  private modelId: string;
  private latencyOverhead: number;

  constructor(modelId: string, latencyOverhead: number = 100) {
    this.modelId = modelId;
    this.latencyOverhead = latencyOverhead;
  }

  /**
   * Execute monolithic LLM call
   */
  async execute(prompt: string, context: ExecutionContext): Promise<BaselineResult> {
    const startTime = Date.now();

    // Simulate LLM execution
    const output = await this.simulateLLM(prompt, context);

    const endTime = Date.now();
    const latency = endTime - startTime + this.latencyOverhead;

    // Calculate metrics
    const confidence = this.calculateConfidence(output, context);
    const accuracy = this.calculateAccuracy(output, context);
    const energy = this.calculateEnergy(latency);

    return {
      approach: 'monolithic',
      metrics: {
        latency,
        accuracy,
        confidence,
        energy,
        throughput: 1000 / latency,
        memory: 2000, // Base model memory
      },
      output,
      timestamp: Date.now(),
    };
  }

  private async simulateLLM(prompt: string, context: ExecutionContext): Promise<unknown> {
    // In production, this would call actual LLM
    // For now, simulate based on task type
    const taskType = context.taskType;

    switch (taskType) {
      case 'sentiment':
        return this.simulateSentimentAnalysis(prompt);
      case 'classification':
        return this.simulateClassification(prompt);
      case 'reasoning':
        return this.simulateReasoning(prompt);
      default:
        return { result: 'simulated_output' };
    }
  }

  private simulateSentimentAnalysis(prompt: string) {
    const words = prompt.toLowerCase().split(/\s+/);
    const positiveWords = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'love'];
    const negativeWords = ['bad', 'terrible', 'awful', 'hate', 'worst', 'horrible'];

    let score = 0;
    words.forEach(word => {
      if (positiveWords.includes(word)) score += 1;
      if (negativeWords.includes(word)) score -= 1;
    });

    const sentiment = score > 0 ? 'positive' : score < 0 ? 'negative' : 'neutral';
    return { sentiment, confidence: Math.min(0.9, 0.5 + Math.abs(score) * 0.1) };
  }

  private simulateClassification(prompt: string) {
    const categories = ['technology', 'science', 'business', 'health', 'entertainment'];
    const keywords = {
      technology: ['software', 'ai', 'computer', 'digital', 'tech'],
      science: ['research', 'study', 'experiment', 'discovery', 'scientific'],
      business: ['market', 'economy', 'company', 'financial', 'investment'],
      health: ['medical', 'health', 'treatment', 'disease', 'patient'],
      entertainment: ['movie', 'music', 'game', 'entertainment', 'show'],
    };

    const lowerPrompt = prompt.toLowerCase();
    let bestCategory = 'general';
    let bestScore = 0;

    for (const [category, keys] of Object.entries(keywords)) {
      const score = keys.filter(key => lowerPrompt.includes(key)).length;
      if (score > bestScore) {
        bestScore = score;
        bestCategory = category;
      }
    }

    return { category: bestCategory, confidence: 0.7 + bestScore * 0.05 };
  }

  private simulateReasoning(prompt: string) {
    // Multi-step reasoning simulation
    const steps = [
      'Identify the core question',
      'Break down into sub-problems',
      'Apply relevant knowledge',
      'Synthesize conclusions',
      'Verify reasoning',
    ];

    return {
      reasoning: steps,
      conclusion: 'Based on systematic analysis',
      confidence: 0.75 + Math.random() * 0.15,
    };
  }

  private calculateConfidence(output: any, context: ExecutionContext): number {
    if (output.confidence) return output.confidence;
    return 0.85; // Default monolithic confidence
  }

  private calculateAccuracy(output: any, context: ExecutionContext): number {
    if (output.confidence) return output.confidence * 0.95; // Slightly lower than confidence
    return 0.80;
  }

  private calculateEnergy(latency: number): number {
    // Energy proportional to latency and model size
    return latency * 2.5; // Arbitrary energy units
  }
}

// ============================================================================
// TILE CHAIN BUILDER
// ============================================================================

/**
 * Build tile chains for comparison
 */
export class TileChainBuilder {
  /**
   * Build sequential tile chain
   */
  static buildSequential(taskType: string): TilePattern {
    const tiles: TileSpec[] = [];

    switch (taskType) {
      case 'sentiment':
        tiles.push(
          { id: 'tokenizer', name: 'Tokenizer', type: 'preprocessing', estimatedConfidence: 1.0, estimatedLatency: 10 },
          { id: 'sentiment_lexicon', name: 'Sentiment Lexicon', type: 'analysis', estimatedConfidence: 0.85, estimatedLatency: 5 },
          { id: 'sentiment_classifier', name: 'Sentiment Classifier', type: 'classification', estimatedConfidence: 0.88, estimatedLatency: 15 },
          { id: 'confidence_calculator', name: 'Confidence Calculator', type: 'validation', estimatedConfidence: 0.90, estimatedLatency: 5 }
        );
        break;

      case 'classification':
        tiles.push(
          { id: 'feature_extractor', name: 'Feature Extractor', type: 'preprocessing', estimatedConfidence: 1.0, estimatedLatency: 15 },
          { id: 'category_classifier', name: 'Category Classifier', type: 'classification', estimatedConfidence: 0.82, estimatedLatency: 20 },
          { id: 'confidence_validator', name: 'Confidence Validator', type: 'validation', estimatedConfidence: 0.85, estimatedLatency: 5 }
        );
        break;

      case 'reasoning':
        tiles.push(
          { id: 'problem_parser', name: 'Problem Parser', type: 'preprocessing', estimatedConfidence: 1.0, estimatedLatency: 10 },
          { id: 'knowledge_retriever', name: 'Knowledge Retriever', type: 'retrieval', estimatedConfidence: 0.90, estimatedLatency: 20 },
          { id: 'reasoning_engine', name: 'Reasoning Engine', type: 'inference', estimatedConfidence: 0.85, estimatedLatency: 30 },
          { id: 'conclusion_validator', name: 'Conclusion Validator', type: 'validation', estimatedConfidence: 0.82, estimatedLatency: 15 }
        );
        break;
    }

    return {
      type: 'sequential',
      tiles,
    };
  }

  /**
   * Build parallel tile chain
   */
  static buildParallel(taskType: string): TilePattern {
    const tiles: TileSpec[] = [];

    switch (taskType) {
      case 'sentiment':
        tiles.push(
          { id: 'tokenizer', name: 'Tokenizer', type: 'preprocessing', estimatedConfidence: 1.0, estimatedLatency: 10 },
          { id: 'sentiment_lexicon', name: 'Sentiment Lexicon', type: 'analysis', estimatedConfidence: 0.85, estimatedLatency: 5 },
          { id: 'sentiment_ml', name: 'Sentiment ML', type: 'analysis', estimatedConfidence: 0.88, estimatedLatency: 8 },
          { id: 'sentiment_rule', name: 'Sentiment Rules', type: 'analysis', estimatedConfidence: 0.80, estimatedLatency: 3 },
          { id: 'ensemble', name: 'Ensemble', type: 'aggregation', estimatedConfidence: 0.90, estimatedLatency: 5 }
        );
        break;

      case 'classification':
        tiles.push(
          { id: 'feature_extractor', name: 'Feature Extractor', type: 'preprocessing', estimatedConfidence: 1.0, estimatedLatency: 15 },
          { id: 'classifier_a', name: 'Classifier A', type: 'classification', estimatedConfidence: 0.80, estimatedLatency: 18 },
          { id: 'classifier_b', name: 'Classifier B', type: 'classification', estimatedConfidence: 0.82, estimatedLatency: 20 },
          { id: 'classifier_c', name: 'Classifier C', type: 'classification', estimatedConfidence: 0.78, estimatedLatency: 15 },
          { id: 'meta_classifier', name: 'Meta Classifier', type: 'aggregation', estimatedConfidence: 0.85, estimatedLatency: 10 }
        );
        break;
    }

    return {
      type: 'parallel',
      tiles,
    };
  }

  /**
   * Build mixed (hybrid) tile chain
   */
  static buildMixed(taskType: string): TilePattern {
    const sequential = this.buildSequential(taskType);
    const parallel = this.buildParallel(taskType);

    // Combine: start with preprocessing, then parallel analysis, then aggregation
    const tiles = [
      sequential.tiles[0], // Preprocessing
      ...parallel.tiles.slice(1, -1), // Parallel classifiers
      parallel.tiles[parallel.tiles.length - 1], // Aggregation
    ];

    return {
      type: 'mixed',
      tiles,
    };
  }

  /**
   * Estimate tile chain metrics
   */
  static estimateMetrics(pattern: TilePattern): {
    latency: number;
    confidence: number;
    energy: number;
  } {
    let latency = 0;
    let confidence = 1.0;

    if (pattern.type === 'sequential') {
      // Sequential: latencies add, confidences multiply
      pattern.tiles.forEach(tile => {
        latency += tile.estimatedLatency;
        confidence *= tile.estimatedConfidence;
      });
    } else if (pattern.type === 'parallel') {
      // Parallel: max latency, average confidence weighted
      const processingTiles = pattern.tiles.slice(1, -1);
      latency = pattern.tiles[0].estimatedLatency; // Preprocessing
      latency += Math.max(...processingTiles.map(t => t.estimatedLatency));
      latency += pattern.tiles[pattern.tiles.length - 1].estimatedLatency; // Aggregation

      const avgConfidence = processingTiles.reduce((sum, t) => sum + t.estimatedConfidence, 0) / processingTiles.length;
      confidence = avgConfidence * pattern.tiles[pattern.tiles.length - 1].estimatedConfidence;
    } else {
      // Mixed: calculate based on structure
      latency = pattern.tiles[0].estimatedLatency; // Preprocessing
      const parallelTiles = pattern.tiles.slice(1, -2);
      latency += Math.max(...parallelTiles.map(t => t.estimatedLatency));
      latency += pattern.tiles[pattern.tiles.length - 1].estimatedLatency;

      const avgConfidence = parallelTiles.reduce((sum, t) => sum + t.estimatedConfidence, 0) / parallelTiles.length;
      confidence = avgConfidence * pattern.tiles[pattern.tiles.length - 1].estimatedConfidence;
    }

    // Energy: sum of all tile energies
    const energy = pattern.tiles.reduce((sum, tile) => sum + tile.estimatedLatency * 0.5, 0);

    return { latency, confidence, energy };
  }
}

// ============================================================================
// ACCURACY-EQUIVALENT FINDER
// ============================================================================

/**
 * Find tile chains that match baseline accuracy
 */
export class AccuracyEquivalentFinder {
  /**
   * Find tile chain with accuracy within tolerance of baseline
   */
  static findEquivalent(
    baselineAccuracy: number,
    patterns: TilePattern[],
    tolerance: number = 0.02
  ): TilePattern[] {
    return patterns.filter(pattern => {
      const metrics = TileChainBuilder.estimateMetrics(pattern);
      return Math.abs(metrics.confidence - baselineAccuracy) <= tolerance;
    });
  }

  /**
   * Adjust tile parameters to match target accuracy
   */
  static adjustToTarget(
    pattern: TilePattern,
    targetAccuracy: number
  ): TilePattern {
    const adjusted = { ...pattern, tiles: [...pattern.tiles] };
    const currentAccuracy = TileChainBuilder.estimateMetrics(pattern).confidence;
    const adjustmentFactor = targetAccuracy / currentAccuracy;

    // Adjust tile confidences
    adjusted.tiles = adjusted.tiles.map(tile => ({
      ...tile,
      estimatedConfidence: Math.min(1.0, tile.estimatedConfidence * adjustmentFactor),
    }));

    return adjusted;
  }
}

// ============================================================================
// PARETO FRONTIER CALCULATOR
// ============================================================================

export interface ParetoPoint {
  id: string;
  metrics: ComparisonMetrics;
  pattern: TilePattern;
  dominates: string[];
  dominatedBy: string[];
}

/**
 * Calculate Pareto frontier of tile configurations
 */
export class ParetoFrontierCalculator {
  /**
   * Find non-dominated solutions
   */
  static calculate(results: BaselineResult[]): ParetoPoint[] {
    const points: ParetoPoint[] = results.map(r => ({
      id: v4(),
      metrics: r.metrics,
      pattern: r.tilePattern!,
      dominates: [],
      dominatedBy: [],
    }));

    // Check domination
    for (let i = 0; i < points.length; i++) {
      for (let j = 0; j < points.length; j++) {
        if (i === j) continue;

        if (this.dominates(points[i], points[j])) {
          points[i].dominates.push(points[j].id);
          points[j].dominatedBy.push(points[i].id);
        }
      }
    }

    // Return non-dominated points
    return points.filter(p => p.dominatedBy.length === 0);
  }

  /**
   * Check if point A dominates point B
   * A dominates B if A is better or equal in all metrics and strictly better in at least one
   */
  private static dominates(a: ParetoPoint, b: ParetoPoint): boolean {
    const am = a.metrics;
    const bm = b.metrics;

    const betterLatency = am.latency < bm.latency;
    const betterAccuracy = am.accuracy > bm.accuracy;
    const betterEnergy = am.energy < bm.energy;
    const betterConfidence = am.confidence > bm.confidence;

    // At least one strictly better
    const hasStrictlyBetter = betterLatency || betterAccuracy || betterEnergy || betterConfidence;

    // All better or equal
    const allBetterOrEqual =
      am.latency <= bm.latency &&
      am.accuracy >= bm.accuracy &&
      am.energy <= bm.energy &&
      am.confidence >= bm.confidence;

    return hasStrictlyBetter && allBetterOrEqual;
  }

  /**
   * Rank solutions by Pareto dominance
   */
  static rank(results: BaselineResult[]): number[] {
    const ranks: number[] = new Array(results.length).fill(0);
    const remaining = [...results];
    let currentRank = 1;

    while (remaining.length > 0) {
      const frontier = this.calculate(remaining);
      frontier.forEach(point => {
        const idx = remaining.findIndex(r => r.metrics === point.metrics);
        if (idx >= 0) {
          ranks[results.indexOf(remaining[idx])] = currentRank;
          remaining.splice(idx, 1);
        }
      });
      currentRank++;
    }

    return ranks;
  }
}

// ============================================================================
// COMPARISON ENGINE
// ============================================================================

export interface ExecutionContext {
  taskType: string;
  timeout?: number;
  iterations?: number;
  warmup?: boolean;
}

/**
 * Main comparison engine
 */
export class ComparisonEngine {
  private baseline: MonolithicBaseline;

  constructor(baseline: MonolithicBaseline) {
    this.baseline = baseline;
  }

  /**
   * Run full comparison
   */
  async compare(
    prompt: string,
    taskType: string,
    context?: Partial<ExecutionContext>
  ): Promise<ComparisonReport> {
    const fullContext: ExecutionContext = {
      taskType,
      iterations: 3,
      warmup: true,
      ...context,
    };

    // Run baseline
    const baseline = await this.runBaseline(prompt, fullContext);

    // Run SMP patterns
    const smpResults = await this.runSMPPatterns(prompt, fullContext);

    // Determine winner
    const winner = this.determineWinner(baseline, smpResults);

    // Calculate improvements
    const improvement = this.calculateImprovement(baseline, smpResults);

    // Calculate Pareto rank
    const allResults = [baseline, ...smpResults];
    const ranks = ParetoFrontierCalculator.rank(allResults);
    const baselineRank = ranks[0];
    const paretoRank = Math.min(...ranks.slice(1));

    return {
      id: v4(),
      task: taskType,
      prompt,
      baseline,
      smpResults,
      winner,
      improvement,
      paretoRank,
      timestamp: Date.now(),
    };
  }

  /**
   * Run monolithic baseline
   */
  private async runBaseline(
    prompt: string,
    context: ExecutionContext
  ): Promise<BaselineResult> {
    const iterations = context.iterations || 3;

    // Warmup
    if (context.warmup) {
      await this.baseline.execute(prompt, context);
    }

    // Measure iterations
    const results: BaselineResult[] = [];
    for (let i = 0; i < iterations; i++) {
      const result = await this.baseline.execute(prompt, context);
      results.push(result);
    }

    // Average metrics
    return this.averageResults(results);
  }

  /**
   * Run SMP tile patterns
   */
  private async runSMPPatterns(
    prompt: string,
    context: ExecutionContext
  ): Promise<BaselineResult[]> {
    const patterns = [
      TileChainBuilder.buildSequential(context.taskType),
      TileChainBuilder.buildParallel(context.taskType),
      TileChainBuilder.buildMixed(context.taskType),
    ];

    const results: BaselineResult[] = [];

    for (const pattern of patterns) {
      const result = await this.executeTilePattern(prompt, pattern, context);
      results.push(result);
    }

    return results;
  }

  /**
   * Execute a tile pattern
   */
  private async executeTilePattern(
    prompt: string,
    pattern: TilePattern,
    context: ExecutionContext
  ): Promise<BaselineResult> {
    const startTime = Date.now();

    // Simulate tile execution
    const output = await this.simulateTiles(prompt, pattern, context);

    const endTime = Date.now();
    const metrics = TileChainBuilder.estimateMetrics(pattern);

    return {
      approach: 'smp',
      metrics: {
        latency: metrics.latency,
        accuracy: metrics.confidence,
        confidence: metrics.confidence,
        energy: metrics.energy,
        throughput: 1000 / metrics.latency,
        memory: pattern.tiles.length * 50, // 50MB per tile
      },
      output,
      tileCount: pattern.tiles.length,
      tilePattern: pattern,
      timestamp: Date.now(),
    };
  }

  /**
   * Simulate tile execution
   */
  private async simulateTiles(
    prompt: string,
    pattern: TilePattern,
    context: ExecutionContext
  ): Promise<unknown> {
    // Simulate tile execution based on pattern
    const delay = TileChainBuilder.estimateMetrics(pattern).latency;
    await new Promise(resolve => setTimeout(resolve, delay));

    // Return result based on task type
    switch (context.taskType) {
      case 'sentiment':
        return { sentiment: 'positive', confidence: 0.88 };
      case 'classification':
        return { category: 'technology', confidence: 0.85 };
      case 'reasoning':
        return { conclusion: 'Based on tile analysis', confidence: 0.82 };
      default:
        return { result: 'tile_output' };
    }
  }

  /**
   * Determine winner
   */
  private determineWinner(
    baseline: BaselineResult,
    smpResults: BaselineResult[]
  ): 'monolithic' | 'smp' | 'tie' {
    const bestSMP = smpResults.reduce((best, current) =>
      current.metrics.latency < best.metrics.latency &&
      current.metrics.accuracy >= baseline.metrics.accuracy - 0.02
        ? current
        : best
    );

    if (bestSMP.metrics.latency < baseline.metrics.latency * 0.9) {
      return 'smp';
    } else if (baseline.metrics.latency < bestSMP.metrics.latency * 0.9) {
      return 'monolithic';
    }
    return 'tie';
  }

  /**
   * Calculate improvement percentages
   */
  private calculateImprovement(
    baseline: BaselineResult,
    smpResults: BaselineResult[]
  ): { latency: number; accuracy: number; energy: number } {
    // Use best SMP result
    const bestSMP = smpResults.reduce((best, current) =>
      current.metrics.latency < best.metrics.latency ? current : best
    );

    return {
      latency: ((baseline.metrics.latency - bestSMP.metrics.latency) / baseline.metrics.latency) * 100,
      accuracy: ((bestSMP.metrics.accuracy - baseline.metrics.accuracy) / baseline.metrics.accuracy) * 100,
      energy: ((baseline.metrics.energy - bestSMP.metrics.energy) / baseline.metrics.energy) * 100,
    };
  }

  /**
   * Average multiple results
   */
  private averageResults(results: BaselineResult[]): BaselineResult {
    const avgMetrics: ComparisonMetrics = {
      latency: results.reduce((sum, r) => sum + r.metrics.latency, 0) / results.length,
      accuracy: results.reduce((sum, r) => sum + r.metrics.accuracy, 0) / results.length,
      confidence: results.reduce((sum, r) => sum + r.metrics.confidence, 0) / results.length,
      energy: results.reduce((sum, r) => sum + r.metrics.energy, 0) / results.length,
      throughput: results.reduce((sum, r) => sum + r.metrics.throughput, 0) / results.length,
      memory: results.reduce((sum, r) => sum + r.metrics.memory, 0) / results.length,
    };

    return {
      approach: results[0].approach,
      metrics: avgMetrics,
      output: results[0].output,
      tileCount: results[0].tileCount,
      tilePattern: results[0].tilePattern,
      timestamp: Date.now(),
    };
  }
}

// ============================================================================
// REPORT GENERATOR
// ============================================================================

/**
 * Generate comparison reports
 */
export class ComparisonReportGenerator {
  /**
   * Generate text report
   */
  static generateText(report: ComparisonReport): string {
    const lines: string[] = [];

    lines.push('='.repeat(80));
    lines.push('SMP BASELINE COMPARISON REPORT');
    lines.push('='.repeat(80));
    lines.push('');
    lines.push(`Task: ${report.task}`);
    lines.push(`Prompt: "${report.prompt}"`);
    lines.push(`Timestamp: ${new Date(report.timestamp).toISOString()}`);
    lines.push('');
    lines.push('-'.repeat(80));
    lines.push('MONOLITHIC BASELINE');
    lines.push('-'.repeat(80));
    this.printMetrics(lines, report.baseline.metrics);
    lines.push('');

    lines.push('-'.repeat(80));
    lines.push('SMP TILE CHAINS');
    lines.push('-'.repeat(80));
    report.smpResults.forEach((result, idx) => {
      lines.push(`Pattern ${idx + 1}: ${result.tilePattern?.type} (${result.tileCount} tiles)`);
      this.printMetrics(lines, result.metrics);
      lines.push('');
    });

    lines.push('-'.repeat(80));
    lines.push('SUMMARY');
    lines.push('-'.repeat(80));
    lines.push(`Winner: ${report.winner}`);
    lines.push(`Pareto Rank: ${report.paretoRank}`);
    lines.push('');
    lines.push('Improvement:');
    lines.push(`  Latency: ${report.improvement.latency.toFixed(1)}%`);
    lines.push(`  Accuracy: ${report.improvement.accuracy.toFixed(1)}%`);
    lines.push(`  Energy: ${report.improvement.energy.toFixed(1)}%`);
    lines.push('');
    lines.push('='.repeat(80));

    return lines.join('\n');
  }

  /**
   * Generate JSON report
   */
  static generateJSON(report: ComparisonReport): string {
    return JSON.stringify(report, null, 2);
  }

  /**
   * Generate markdown report
   */
  static generateMarkdown(report: ComparisonReport): string {
    const lines: string[] = [];

    lines.push('# SMP Baseline Comparison Report');
    lines.push('');
    lines.push(`## Task: ${report.task}`);
    lines.push('');
    lines.push(`**Prompt:** "${report.prompt}"`);
    lines.push(`**Timestamp:** ${new Date(report.timestamp).toISOString()}`);
    lines.push('');

    lines.push('## Monolithic Baseline');
    lines.push('');
    this.printMetricsTable(lines, report.baseline.metrics, 'Monolithic');
    lines.push('');

    lines.push('## SMP Tile Chains');
    lines.push('');
    report.smpResults.forEach((result, idx) => {
      lines.push(`### Pattern ${idx + 1}: ${result.tilePattern?.type}`);
      lines.push(`- **Tiles:** ${result.tileCount}`);
      lines.push('');
      this.printMetricsTable(lines, result.metrics, `SMP ${idx + 1}`);
      lines.push('');
    });

    lines.push('## Summary');
    lines.push('');
    lines.push(`- **Winner:** ${report.winner}`);
    lines.push(`- **Pareto Rank:** ${report.paretoRank}`);
    lines.push('');
    lines.push('### Improvement');
    lines.push('');
    lines.push('| Metric | Improvement |');
    lines.push('|--------|-------------|');
    lines.push(`| Latency | ${report.improvement.latency.toFixed(1)}% |`);
    lines.push(`| Accuracy | ${report.improvement.accuracy.toFixed(1)}% |`);
    lines.push(`| Energy | ${report.improvement.energy.toFixed(1)}% |`);
    lines.push('');

    return lines.join('\n');
  }

  /**
   * Generate HTML report
   */
  static generateHTML(report: ComparisonReport): string {
    const improvementColor = (val: number) => val > 0 ? 'green' : 'red';

    return `
<!DOCTYPE html>
<html>
<head>
  <title>SMP Baseline Comparison</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 40px; }
    h1 { color: #333; }
    h2 { color: #666; margin-top: 30px; }
    table { border-collapse: collapse; width: 100%; margin: 20px 0; }
    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
    th { background-color: #4CAF50; color: white; }
    tr:nth-child(even) { background-color: #f2f2f2; }
    .metric { font-weight: bold; }
    .positive { color: green; }
    .negative { color: red; }
    .winner { font-size: 1.2em; font-weight: bold; }
  </style>
</head>
<body>
  <h1>SMP Baseline Comparison Report</h1>

  <h2>Task: ${report.task}</h2>
  <p><strong>Prompt:</strong> "${report.prompt}"</p>
  <p><strong>Timestamp:</strong> ${new Date(report.timestamp).toISOString()}</p>

  <h2>Monolithic Baseline</h2>
  ${this.generateMetricsTableHTML(report.baseline.metrics, 'Monolithic')}

  <h2>SMP Tile Chains</h2>
  ${report.smpResults.map((result, idx) => `
    <h3>Pattern ${idx + 1}: ${result.tilePattern?.type}</h3>
    <p><strong>Tiles:</strong> ${result.tileCount}</p>
    ${this.generateMetricsTableHTML(result.metrics, `SMP ${idx + 1}`)}
  `).join('')}

  <h2>Summary</h2>
  <p class="winner">Winner: ${report.winner}</p>
  <p><strong>Pareto Rank:</strong> ${report.paretoRank}</p>

  <h3>Improvement</h3>
  <table>
    <tr><th>Metric</th><th>Improvement</th></tr>
    <tr>
      <td>Latency</td>
      <td class="${improvementColor(report.improvement.latency)}">${report.improvement.latency.toFixed(1)}%</td>
    </tr>
    <tr>
      <td>Accuracy</td>
      <td class="${improvementColor(report.improvement.accuracy)}">${report.improvement.accuracy.toFixed(1)}%</td>
    </tr>
    <tr>
      <td>Energy</td>
      <td class="${improvementColor(report.improvement.energy)}">${report.improvement.energy.toFixed(1)}%</td>
    </tr>
  </table>
</body>
</html>
    `;
  }

  private static printMetrics(lines: string[], metrics: ComparisonMetrics): void {
    lines.push(`Latency:      ${metrics.latency.toFixed(2)} ms`);
    lines.push(`Accuracy:     ${(metrics.accuracy * 100).toFixed(1)}%`);
    lines.push(`Confidence:   ${(metrics.confidence * 100).toFixed(1)}%`);
    lines.push(`Energy:       ${metrics.energy.toFixed(2)} units`);
    lines.push(`Throughput:   ${metrics.throughput.toFixed(2)} req/s`);
    lines.push(`Memory:       ${metrics.memory.toFixed(0)} MB`);
  }

  private static printMetricsTable(lines: string[], metrics: ComparisonMetrics, label: string): void {
    lines.push(`| Metric | ${label} |`);
    lines.push('|--------|---------|');
    lines.push(`| Latency | ${metrics.latency.toFixed(2)} ms |`);
    lines.push(`| Accuracy | ${(metrics.accuracy * 100).toFixed(1)}% |`);
    lines.push(`| Confidence | ${(metrics.confidence * 100).toFixed(1)}% |`);
    lines.push(`| Energy | ${metrics.energy.toFixed(2)} units |`);
    lines.push(`| Throughput | ${metrics.throughput.toFixed(2)} req/s |`);
    lines.push(`| Memory | ${metrics.memory.toFixed(0)} MB |`);
  }

  private static generateMetricsTableHTML(metrics: ComparisonMetrics, label: string): string {
    return `
  <table>
    <tr><th>Metric</th><th>${label}</th></tr>
    <tr><td>Latency</td><td>${metrics.latency.toFixed(2)} ms</td></tr>
    <tr><td>Accuracy</td><td>${(metrics.accuracy * 100).toFixed(1)}%</td></tr>
    <tr><td>Confidence</td><td>${(metrics.confidence * 100).toFixed(1)}%</td></tr>
    <tr><td>Energy</td><td>${metrics.energy.toFixed(2)} units</td></tr>
    <tr><td>Throughput</td><td>${metrics.throughput.toFixed(2)} req/s</td></tr>
    <tr><td>Memory</td><td>${metrics.memory.toFixed(0)} MB</td></tr>
  </table>
    `;
  }
}

// ============================================================================
// MAIN RUNNER
// ============================================================================

/**
 * Run comparison from command line
 */
export async function runComparison(
  prompt: string,
  taskType: string = 'sentiment',
  format: 'text' | 'json' | 'markdown' | 'html' = 'text'
): Promise<string> {
  const baseline = new MonolithicBaseline('gpt-4', 100);
  const engine = new ComparisonEngine(baseline);

  const report = await engine.compare(prompt, taskType);

  switch (format) {
    case 'json':
      return ComparisonReportGenerator.generateJSON(report);
    case 'markdown':
      return ComparisonReportGenerator.generateMarkdown(report);
    case 'html':
      return ComparisonReportGenerator.generateHTML(report);
    default:
      return ComparisonReportGenerator.generateText(report);
  }
}
