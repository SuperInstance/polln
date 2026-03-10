/**
 * Tile Chain - Pipeline Composition
 *
 * Chains tiles together for sequential execution with:
 * - Confidence multiplication across steps
 * - Trace aggregation
 * - Branching logic
 * - Validation at each step
 *
 * T = (I, O, f, c, τ) composed: T1 ; T2 ; T3
 */

import { Tile, ITile, TileResult, Zone, classifyZone, ValidationResult, ValidationError, ValidationWarning, Schema, TileExecutionError } from './Tile';

// ============================================================================
// TYPES
// ============================================================================

/**
 * A step in the chain
 */
interface ChainStep {
  tile: ITile<any, any>;
  id: string;
  type: string;
}

/**
 * Result of chain execution with full trace
 */
export interface ChainResult<O> {
  output: O;
  confidence: number;
  zone: Zone;
  trace: ChainTrace;
  duration: number;
  steps: StepResult[];
}

/**
 * Result of a single step
 */
export interface StepResult {
  tileId: string;
  tileType: string;
  input: unknown;
  output: unknown;
  confidence: number;
  zone: Zone;
  trace: string;
  duration: number;
}

/**
 * Full chain trace
 */
export interface ChainTrace {
  steps: TraceStep[];
  summary: string;
  confidenceFlow: number[];
}

export interface TraceStep {
  tileId: string;
  tileType: string;
  confidence: number;
  zone: Zone;
  reason: string;
}

/**
 * Branch configuration
 */
interface BranchConfig<A, B> {
  condition: (input: unknown) => boolean;
  ifTrue: ITile<any, A>;
  ifFalse: ITile<any, B>;
}

// ============================================================================
// TILE CHAIN IMPLEMENTATION
// ============================================================================

/**
 * TileChain - Composes tiles into executable pipelines
 *
 * Key properties:
 * - Sequential composition: output of one feeds into next
 * - Confidence multiplies: c(chain) = c(t1) * c(t2) * ... * c(tn)
 * - Traces aggregate: τ(chain) = τ(t1) → τ(t2) → ... → τ(tn)
 * - Type-safe: compile-time verification of types
 */
export class TileChain<I, O> {
  private steps: ChainStep[] = [];
  private branches: Map<string, BranchConfig<any, any>> = new Map();
  private firstInputSchema: Schema<I>;
  private lastOutputSchema: Schema<O>;

  private constructor(
    firstInputSchema: Schema<I>,
    lastOutputSchema: Schema<O>,
    steps: ChainStep[] = []
  ) {
    this.firstInputSchema = firstInputSchema;
    this.lastOutputSchema = lastOutputSchema;
    this.steps = steps;
  }

  /**
   * Create a new chain starting with a tile
   */
  static start<A, B>(tile: ITile<A, B>): TileChain<A, B> {
    return new TileChain<A, B>(
      tile.inputSchema,
      tile.outputSchema,
      [{ tile, id: tile.id, type: tile.type }]
    );
  }

  /**
   * Create an empty chain with input schema
   */
  static empty<I>(inputSchema: Schema<I>): TileChain<I, I> {
    // Identity chain - passes input through unchanged
    const identityTile = new IdentityTile<I>(inputSchema);
    return new TileChain<I, I>(
      inputSchema,
      inputSchema,
      [{ tile: identityTile, id: 'identity', type: 'Identity' }]
    );
  }

  /**
   * Add a tile to the chain
   *
   * Type-safe: O (current output) must match T's input type
   */
  add<T>(tile: ITile<O, T>): TileChain<I, T> {
    // Validate composition at runtime
    if (!this.canCompose(tile)) {
      throw new ChainCompositionError(
        `Cannot compose: output schema ${this.lastOutputSchema.type} does not match input schema ${tile.inputSchema.type}`
      );
    }

    return new TileChain<I, T>(
      this.firstInputSchema,
      tile.outputSchema,
      [...this.steps, { tile, id: tile.id, type: tile.type }]
    );
  }

  /**
   * Add a conditional branch
   *
   * Branches to ifTrue or ifFalse based on condition
   * Both branches must produce compatible types
   */
  branch<A, B>(
    condition: (input: O) => boolean,
    ifTrue: ITile<O, A>,
    ifFalse: ITile<O, B>
  ): TileChain<I, A | B> {
    const branchId = `branch_${Date.now()}`;

    // Create a branch tile that wraps the decision
    const branchTile = new BranchTile<O, A, B>(condition, ifTrue, ifFalse, branchId);

    const newChain = new TileChain<I, A | B>(
      this.firstInputSchema,
      branchTile.outputSchema,
      [...this.steps, { tile: branchTile, id: branchId, type: 'Branch' }]
    );

    return newChain;
  }

  /**
   * Add a parallel split
   *
   * Runs multiple tiles on the same input, collects results
   */
  split<Tiles extends ITile<O, any>[]>(
    ...tiles: Tiles
  ): TileChain<I, { [K in keyof Tiles]: Tiles[K] extends ITile<any, infer R> ? R : never }> {
    if (tiles.length === 0) {
      throw new Error('Split requires at least one tile');
    }

    const parallelTile = new ParallelSplitTile<O, Tiles>(tiles);

    return new TileChain<I, any>(
      this.firstInputSchema,
      parallelTile.outputSchema,
      [...this.steps, { tile: parallelTile, id: `split_${Date.now()}`, type: 'ParallelSplit' }]
    );
  }

  /**
   * Add a merge step
   *
   * Combines parallel results back into single value
   */
  merge<M>(
    merger: (results: any) => M,
    outputSchema?: Schema<M>
  ): TileChain<I, M> {
    const mergeTile = new MergeTile<any, M>(merger, outputSchema);

    return new TileChain<I, M>(
      this.firstInputSchema,
      mergeTile.outputSchema,
      [...this.steps, { tile: mergeTile, id: `merge_${Date.now()}`, type: 'Merge' }]
    );
  }

  /**
   * Execute the chain
   */
  async execute(input: I): Promise<ChainResult<O>> {
    const startTime = performance.now();
    const stepResults: StepResult[] = [];
    const traceSteps: TraceStep[] = [];
    const confidenceFlow: number[] = [];

    let currentInput: unknown = input;
    let chainConfidence = 1.0;

    for (let i = 0; i < this.steps.length; i++) {
      const step = this.steps[i];
      const stepStart = performance.now();

      try {
        // Execute tile
        let result: TileResult<any>;

        if (step.tile instanceof Tile) {
          result = await step.tile.execute(currentInput);
        } else {
          // For non-Tile ITile implementations
          const [output, conf, trace] = await Promise.all([
            step.tile.discriminate(currentInput),
            step.tile.confidence(currentInput),
            step.tile.trace(currentInput),
          ]);
          result = {
            output,
            confidence: conf,
            zone: classifyZone(conf),
            trace,
            duration: performance.now() - stepStart,
          };
        }

        // Track confidence flow (multiplicative)
        chainConfidence *= result.confidence;
        confidenceFlow.push(chainConfidence);

        // Record step result
        const stepResult: StepResult = {
          tileId: step.id,
          tileType: step.type,
          input: currentInput,
          output: result.output,
          confidence: result.confidence,
          zone: result.zone,
          trace: result.trace,
          duration: result.duration,
        };
        stepResults.push(stepResult);

        // Build trace
        traceSteps.push({
          tileId: step.id,
          tileType: step.type,
          confidence: result.confidence,
          zone: result.zone,
          reason: result.trace,
        });

        // Check for RED zone - stop execution
        if (result.zone === 'RED') {
          return {
            output: result.output,
            confidence: chainConfidence,
            zone: 'RED',
            trace: {
              steps: traceSteps,
              summary: this.buildSummary(traceSteps, chainConfidence),
              confidenceFlow,
            },
            duration: performance.now() - startTime,
            steps: stepResults,
          };
        }

        // Feed output to next step
        currentInput = result.output;

      } catch (error) {
        const err = error instanceof Error ? error : new Error(String(error));
        throw new ChainExecutionError(
          `Chain failed at step ${i} (${step.type}): ${err.message}`,
          step.id,
          i,
          err
        );
      }
    }

    const finalZone = classifyZone(chainConfidence);

    return {
      output: currentInput as O,
      confidence: chainConfidence,
      zone: finalZone,
      trace: {
        steps: traceSteps,
        summary: this.buildSummary(traceSteps, chainConfidence),
        confidenceFlow,
      },
      duration: performance.now() - startTime,
      steps: stepResults,
    };
  }

  /**
   * Calculate overall chain confidence without full execution
   */
  async confidence(input: I): Promise<number> {
    let currentInput: unknown = input;
    let confidence = 1.0;

    for (const step of this.steps) {
      const tileConf = await step.tile.confidence(currentInput);
      confidence *= tileConf;

      // Early exit if confidence drops too low
      if (classifyZone(confidence) === 'RED') {
        return confidence;
      }

      // Get output for next step (lighter than full execute)
      if (step.tile instanceof Tile) {
        const result = await step.tile.execute(currentInput);
        currentInput = result.output;
      } else {
        currentInput = await step.tile.discriminate(currentInput);
      }
    }

    return confidence;
  }

  /**
   * Validate the entire chain
   */
  validate(): ValidationResult {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];

    if (this.steps.length === 0) {
      errors.push({ code: 'EMPTY_CHAIN', message: 'Chain has no steps' });
    }

    // Validate each step
    for (let i = 0; i < this.steps.length; i++) {
      const step = this.steps[i];

      if (!step.tile) {
        errors.push({
          code: 'NULL_TILE',
          message: `Step ${i} has null tile`,
          path: `steps[${i}]`,
        });
        continue;
      }

      // Validate tile itself
      const tileValidation = step.tile.validate();
      if (!tileValidation.valid) {
        errors.push(...tileValidation.errors.map(e => ({
          ...e,
          path: `steps[${i}].${e.path || ''}`,
        })));
      }
      warnings.push(...tileValidation.warnings.map(w => ({
        ...w,
        suggestion: w.suggestion,
      })));
    }

    // Validate composition between steps
    for (let i = 1; i < this.steps.length; i++) {
      const prev = this.steps[i - 1];
      const curr = this.steps[i];

      // Check type compatibility
      // Note: This is a runtime check; TypeScript handles compile-time
      if (!this.schemasCompatible(prev.tile.outputSchema, curr.tile.inputSchema)) {
        warnings.push({
          code: 'TYPE_MISMATCH',
          message: `Potential type mismatch between ${prev.type} and ${curr.type}`,
          suggestion: 'Verify schemas are compatible at runtime',
        });
      }
    }

    // Check for confidence degradation warnings
    if (this.steps.length > 5) {
      warnings.push({
        code: 'LONG_CHAIN',
        message: `Chain has ${this.steps.length} steps; confidence may degrade significantly`,
        suggestion: 'Consider splitting into sub-chains or using parallel composition',
      });
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
    };
  }

  /**
   * Generate visual representation of the chain
   */
  visualize(): string {
    const lines: string[] = ['TileChain:'];

    for (let i = 0; i < this.steps.length; i++) {
      const step = this.steps[i];
      const arrow = i < this.steps.length - 1 ? '  │' : '';
      lines.push(`  ├── [${step.type}] ${step.id}`);
      if (arrow) lines.push(arrow);
    }

    lines.push('');
    lines.push(`Input:  ${this.firstInputSchema.type}`);
    lines.push(`Output: ${this.lastOutputSchema.type}`);
    lines.push(`Steps:  ${this.steps.length}`);

    return lines.join('\n');
  }

  /**
   * Get chain length
   */
  get length(): number {
    return this.steps.length;
  }

  /**
   * Get step at index
   */
  getStep(index: number): ChainStep | undefined {
    return this.steps[index];
  }

  /**
   * Convert to simple composed tile
   */
  toTile(): ITile<I, O> {
    if (this.steps.length === 1) {
      return this.steps[0].tile as ITile<I, O>;
    }

    // Compose all steps
    let composed = this.steps[0].tile;
    for (let i = 1; i < this.steps.length; i++) {
      composed = composed.compose(this.steps[i].tile);
    }

    return composed as ITile<I, O>;
  }

  // Private helpers

  private canCompose(next: ITile<any, any>): boolean {
    return this.schemasCompatible(this.lastOutputSchema, next.inputSchema);
  }

  private schemasCompatible(output: Schema<any>, input: Schema<any>): boolean {
    // Simple type matching - can be enhanced
    if (output.type === input.type) return true;
    if (input.type === 'any' || input.type === 'unknown') return true;
    if (output.type === 'union' || input.type === 'union') return true;
    return false;
  }

  private buildSummary(steps: TraceStep[], confidence: number): string {
    const stepSummary = steps.map(s => `${s.tileType}(${s.confidence.toFixed(2)})`).join(' → ');
    return `${stepSummary} = ${confidence.toFixed(3)} [${classifyZone(confidence)}]`;
  }
}

// ============================================================================
// HELPER TILES
// ============================================================================

/**
 * Identity tile - passes input through unchanged
 */
class IdentityTile<T> extends Tile<T, T> {
  constructor(inputSchema: Schema<T>) {
    super(inputSchema, inputSchema, { id: 'identity' });
  }

  async discriminate(input: T): Promise<T> {
    return input;
  }

  async confidence(input: T): Promise<number> {
    return 1.0;
  }

  async trace(input: T): Promise<string> {
    return 'Identity: pass through';
  }
}

/**
 * Branch tile - conditional execution
 */
class BranchTile<I, A, B> extends Tile<I, A | B> {
  private condition: (input: I) => boolean;
  private ifTrue: ITile<I, A>;
  private ifFalse: ITile<I, B>;

  constructor(
    condition: (input: I) => boolean,
    ifTrue: ITile<I, A>,
    ifFalse: ITile<I, B>,
    id: string
  ) {
    super(
      ifTrue.inputSchema,
      {
        type: 'union',
        validate: (v: unknown): v is A | B => true, // Simplified
      },
      { id }
    );
    this.condition = condition;
    this.ifTrue = ifTrue;
    this.ifFalse = ifFalse;
  }

  async discriminate(input: I): Promise<A | B> {
    if (this.condition(input)) {
      if (this.ifTrue instanceof Tile) {
        return (await this.ifTrue.execute(input)).output;
      }
      return await this.ifTrue.discriminate(input);
    } else {
      if (this.ifFalse instanceof Tile) {
        return (await this.ifFalse.execute(input)).output;
      }
      return await this.ifFalse.discriminate(input);
    }
  }

  async confidence(input: I): Promise<number> {
    const tile = this.condition(input) ? this.ifTrue : this.ifFalse;
    return await tile.confidence(input);
  }

  async trace(input: I): Promise<string> {
    const branch = this.condition(input) ? 'TRUE' : 'FALSE';
    const tile = this.condition(input) ? this.ifTrue : this.ifFalse;
    const tileTrace = await tile.trace(input);
    return `Branch(${branch}): ${tileTrace}`;
  }
}

/**
 * Parallel split tile - run multiple tiles on same input
 */
class ParallelSplitTile<I, Tiles extends ITile<I, any>[]> extends Tile<I, any[]> {
  private tiles: Tiles;

  constructor(tiles: Tiles) {
    super(
      tiles[0].inputSchema,
      {
        type: 'array',
        validate: (v: unknown): v is any[] => Array.isArray(v),
      },
      { id: `parallel_split_${Date.now()}` }
    );
    this.tiles = tiles;
  }

  async discriminate(input: I): Promise<any[]> {
    const results = await Promise.all(
      this.tiles.map(async tile => {
        if (tile instanceof Tile) {
          return (await tile.execute(input)).output;
        }
        return await tile.discriminate(input);
      })
    );
    return results;
  }

  async confidence(input: I): Promise<number> {
    const confidences = await Promise.all(
      this.tiles.map(tile => tile.confidence(input))
    );
    // Average confidence for parallel
    return confidences.reduce((a, b) => a + b, 0) / confidences.length;
  }

  async trace(input: I): Promise<string> {
    const traces = await Promise.all(
      this.tiles.map(tile => tile.trace(input))
    );
    return `Parallel[${traces.join(' | ')}]`;
  }
}

/**
 * Merge tile - combine parallel results
 */
class MergeTile<I extends any[], O> extends Tile<I, O> {
  private merger: (results: I) => O;

  constructor(merger: (results: I) => O, outputSchema?: Schema<O>) {
    super(
      { type: 'array', validate: (v): v is I => Array.isArray(v) },
      outputSchema ?? { type: 'unknown', validate: (): v is O => true },
      { id: `merge_${Date.now()}` }
    );
    this.merger = merger;
  }

  async discriminate(input: I): Promise<O> {
    return this.merger(input);
  }

  async confidence(input: I): Promise<number> {
    // Merge confidence is average of input confidences
    // Could be customized based on merger logic
    return 0.9; // Default high confidence for merge
  }

  async trace(input: I): Promise<string> {
    return `Merge(${input.length} inputs)`;
  }
}

// ============================================================================
// ERRORS
// ============================================================================

export class ChainError extends Error {
  constructor(
    message: string,
    public readonly code: string
  ) {
    super(message);
    this.name = 'ChainError';
  }
}

export class ChainCompositionError extends ChainError {
  constructor(message: string) {
    super(message, 'COMPOSITION_ERROR');
    this.name = 'ChainCompositionError';
  }
}

export class ChainExecutionError extends ChainError {
  constructor(
    message: string,
    public readonly tileId: string,
    public readonly stepIndex: number,
    public readonly cause?: Error
  ) {
    super(message, 'EXECUTION_ERROR');
    this.name = 'ChainExecutionError';
  }
}

// ============================================================================
// EXPORTS
// ============================================================================

export default TileChain;
