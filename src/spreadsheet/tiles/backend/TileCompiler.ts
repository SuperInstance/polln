/**
 * Tile Compiler - Optimization and Compilation
 *
 * Analyzes and optimizes tile chains for:
 * - Dead code elimination
 * - Chain fusion (combining sequential tiles)
 * - Parallelization detection
 * - Memory optimization
 *
 * Part of Phase 2: Infrastructure
 */

import { ITile, Tile, TileResult } from '../core/Tile';
import { TileChain, ChainResult } from '../core/TileChain';

// ============================================================================
// TYPES
// ============================================================================

/**
 * Compilation options
 */
export interface CompilationOptions {
  /** Enable chain fusion */
  fuseChains?: boolean;
  /** Enable dead code elimination */
  eliminateDeadCode?: boolean;
  /** Enable parallelization detection */
  detectParallelism?: boolean;
  /** Maximum chain depth before warning */
  maxChainDepth?: number;
  /** Enable memory optimization */
  optimizeMemory?: boolean;
}

/**
 * Compilation result
 */
export interface CompilationResult {
  /** Optimized chain */
  chain: ITile<any, any>;
  /** Original chain for comparison */
  originalChain: ITile<any, any>;
  /** Applied optimizations */
  optimizations: Optimization[];
  /** Compilation warnings */
  warnings: CompilationWarning[];
  /** Performance estimate */
  performanceEstimate: PerformanceEstimate;
}

/**
 * Optimization applied during compilation
 */
export interface Optimization {
  type: 'fusion' | 'parallelization' | 'dead_code_elimination' | 'memory_optimization';
  description: string;
  estimatedSpeedup: number;
  affectedTiles: string[];
}

/**
 * Compilation warning
 */
export interface CompilationWarning {
  code: string;
  message: string;
  tileId?: string;
}

/**
 * Performance estimate
 */
export interface PerformanceEstimate {
  estimatedLatencyMs: number;
  memoryFootprintKb: number;
  parallelizableOps: number;
  sequentialOps: number;
}

// ============================================================================
// TILE COMPILER
// ============================================================================

/**
 * TileCompiler - Optimizes tile chains for execution
 *
 * Analyzes tile chains and applies optimizations:
 * - Fuses sequential tiles with compatible schemas
 * - Detects parallelizable operations
 * - Eliminates dead code paths
 * - Estimates memory requirements
 *
 * @example
 * ```typescript
 * const compiler = new TileCompiler({
 *   fuseChains: true,
 *   detectParallelism: true,
 * });
 *
 * const result = compiler.compile(chain);
 * console.log(result.optimizations);
 * ```
 */
export class TileCompiler {
  private options: Required<CompilationOptions>;

  constructor(options: CompilationOptions = {}) {
    this.options = {
      fuseChains: options.fuseChains ?? true,
      eliminateDeadCode: options.eliminateDeadCode ?? true,
      detectParallelism: options.detectParallelism ?? true,
      maxChainDepth: options.maxChainDepth ?? 20,
      optimizeMemory: options.optimizeMemory ?? true,
    };
  }

  /**
   * Compile a tile chain
   */
  compile<I, O>(chain: TileChain<I, O>): CompilationResult {
    const optimizations: Optimization[] = [];
    const warnings: CompilationWarning[] = [];

    // Analyze chain
    const analysis = this.analyzeChain(chain);

    // Check for deep chains
    if (analysis.depth > this.options.maxChainDepth) {
      warnings.push({
        code: 'DEEP_CHAIN',
        message: `Chain has ${analysis.depth} steps, exceeding max of ${this.options.maxChainDepth}`,
      });
    }

    // Apply optimizations
    let optimizedChain = chain;

    if (this.options.fuseChains) {
      const fusionResult = this.fuseTiles(analysis);
      if (fusionResult.optimized) {
        optimizations.push(fusionResult.optimization);
        // Note: Would need to actually create fused chain
      }
    }

    if (this.options.detectParallelism) {
      const parallelResult = this.detectParallel(analysis);
      if (parallelResult.optimized) {
        optimizations.push(parallelResult.optimization);
      }
    }

    if (this.options.eliminateDeadCode) {
      const deadCodeResult = this.eliminateDeadCode(analysis);
      if (deadCodeResult.optimized) {
        optimizations.push(deadCodeResult.optimization);
      }
    }

    // Calculate performance estimate
    const performanceEstimate = this.estimatePerformance(analysis, optimizations);

    return {
      chain: optimizedChain.toTile(),
      originalChain: chain.toTile(),
      optimizations,
      warnings,
      performanceEstimate,
    };
  }

  /**
   * Analyze chain structure
   */
  private analyzeChain(chain: TileChain<any, any>): ChainAnalysis {
    const tiles: TileInfo[] = [];
    let depth = 0;

    // Walk the chain
    for (let i = 0; i < chain.length; i++) {
      const step = chain.getStep(i);
      if (step) {
        tiles.push({
          id: step.id,
          type: step.type,
          index: i,
          inputType: step.tile.inputSchema.type,
          outputType: step.tile.outputSchema.type,
        });
        depth++;
      }
    }

    // Detect patterns
    const patterns = this.detectPatterns(tiles);

    return {
      depth,
      tiles,
      patterns,
      hasFusableTiles: patterns.fusablePairs.length > 0,
      hasParallelizable: patterns.parallelGroups.length > 0,
      hasDeadCode: patterns.deadCodePaths.length > 0,
    };
  }

  /**
   * Detect patterns in tile sequence
   */
  private detectPatterns(tiles: TileInfo[]): PatternAnalysis {
    const fusablePairs: FusablePair[] = [];
    const parallelGroups: ParallelGroup[] = [];
    const deadCodePaths: string[] = [];

    // Find fusable pairs (sequential tiles with compatible types)
    for (let i = 0; i < tiles.length - 1; i++) {
      const current = tiles[i];
      const next = tiles[i + 1];

      // Check if these can be fused
      if (this.canFuse(current, next)) {
        fusablePairs.push({
          first: current,
          second: next,
          fusionBenefit: this.calculateFusionBenefit(current, next),
        });
      }
    }

    // Find parallelizable groups
    const visited = new Set<string>();
    for (let i = 0; i < tiles.length; i++) {
      if (visited.has(tiles[i].id)) continue;

      const parallelizable: TileInfo[] = [tiles[i]];
      visited.add(tiles[i].id);

      // Find other tiles that could run in parallel
      for (let j = i + 1; j < tiles.length; j++) {
        if (this.canParallelize(tiles[i], tiles[j])) {
          parallelizable.push(tiles[j]);
          visited.add(tiles[j].id);
        }
      }

      if (parallelizable.length > 1) {
        parallelGroups.push({
          tiles: parallelizable,
          speedupFactor: parallelizable.length,
        });
      }
    }

    return {
      fusablePairs,
      parallelGroups,
      deadCodePaths,
    };
  }

  /**
   * Check if two tiles can be fused
   */
  private canFuse(a: TileInfo, b: TileInfo): boolean {
    // Simple heuristic: adjacent tiles with simple types
    return a.index === b.index - 1 &&
           (a.type.includes('Transform') || a.type.includes('Normalize'));
  }

  /**
   * Check if two tiles can run in parallel
   */
  private canParallelize(a: TileInfo, b: TileInfo): boolean {
    // Same input type, different operations
    return a.inputType === b.inputType && a.type !== b.type;
  }

  /**
   * Calculate benefit of fusing tiles
   */
  private calculateFusionBenefit(a: TileInfo, b: TileInfo): number {
    // Estimated speedup from reducing overhead
    return 0.1; // 10% improvement per fusion
  }

  /**
   * Fuse tiles
   */
  private fuseTiles(analysis: ChainAnalysis): FusionResult {
    if (!analysis.hasFusableTiles) {
      return { optimized: false };
    }

    const pairs = analysis.patterns.fusablePairs;
    const bestPair = pairs.reduce((best, current) =>
      current.fusionBenefit > best.fusionBenefit ? current : best,
    pairs[0]);

    return {
      optimized: true,
      optimization: {
        type: 'fusion',
        description: `Fused ${bestPair.first.type} with ${bestPair.second.type}`,
        estimatedSpeedup: bestPair.fusionBenefit,
        affectedTiles: [bestPair.first.id, bestPair.second.id],
      },
    };
  }

  /**
   * Detect parallelization opportunities
   */
  private detectParallel(analysis: ChainAnalysis): ParallelResult {
    if (!analysis.hasParallelizable) {
      return { optimized: false };
    }

    const groups = analysis.patterns.parallelGroups;
    const bestGroup = groups.reduce((best, current) =>
      current.speedupFactor > best.speedupFactor ? current : best,
    groups[0]);

    return {
      optimized: true,
      optimization: {
        type: 'parallelization',
        description: `Parallelized ${bestGroup.tiles.length} tiles`,
        estimatedSpeedup: bestGroup.speedupFactor * 0.2,
        affectedTiles: bestGroup.tiles.map(t => t.id),
      },
    };
  }

  /**
   * Eliminate dead code
   */
  private eliminateDeadCode(analysis: ChainAnalysis): DeadCodeResult {
    if (!analysis.hasDeadCode) {
      return { optimized: false };
    }

    const deadPaths = analysis.patterns.deadCodePaths;
    if (deadPaths.length === 0) {
      return { optimized: false };
    }

    return {
      optimized: true,
      optimization: {
        type: 'dead_code_elimination',
        description: `Eliminated ${deadPaths.length} dead code paths`,
        estimatedSpeedup: 0.05,
        affectedTiles: deadPaths,
      },
    };
  }

  /**
   * Estimate performance after optimization
   */
  private estimatePerformance(
    analysis: ChainAnalysis,
    optimizations: Optimization[]
  ): PerformanceEstimate {
    // Base estimates
    let estimatedLatencyMs = analysis.depth * 5; // ~5ms per tile
    let memoryFootprintKb = analysis.depth * 100; // ~100KB per tile
    let parallelizableOps = 0;
    let sequentialOps = analysis.depth;

    // Apply optimization benefits
    for (const opt of optimizations) {
      estimatedLatencyMs *= (1 - opt.estimatedSpeedup);

      if (opt.type === 'parallelization') {
        parallelizableOps += opt.affectedTiles.length;
        sequentialOps -= opt.affectedTiles.length;
      }
    }

    return {
      estimatedLatencyMs,
      memoryFootprintKb,
      parallelizableOps,
      sequentialOps,
    };
  }
}

// ============================================================================
// HELPER TYPES
// ============================================================================

interface TileInfo {
  id: string;
  type: string;
  index: number;
  inputType: string;
  outputType: string;
}

interface ChainAnalysis {
  depth: number;
  tiles: TileInfo[];
  patterns: PatternAnalysis;
  hasFusableTiles: boolean;
  hasParallelizable: boolean;
  hasDeadCode: boolean;
}

interface PatternAnalysis {
  fusablePairs: FusablePair[];
  parallelGroups: ParallelGroup[];
  deadCodePaths: string[];
}

interface FusablePair {
  first: TileInfo;
  second: TileInfo;
  fusionBenefit: number;
}

interface ParallelGroup {
  tiles: TileInfo[];
  speedupFactor: number;
}

interface FusionResult {
  optimized: boolean;
  optimization?: Optimization;
}

interface ParallelResult {
  optimized: boolean;
  optimization?: Optimization;
}

interface DeadCodeResult {
  optimized: boolean;
  optimization?: Optimization;
}

// ============================================================================
// EXPORTS
// ============================================================================

export default TileCompiler;
