/**
 * Core Tile Interface
 *
 * The atom of SMP programming. Every tile is:
 * - Discriminating: Makes bounded decisions
 * - Inspectable: Exposes reasoning traces
 * - Trainable: Learns independently
 * - Composable: Combines through well-defined interfaces
 *
 * T = (I, O, f, c, τ)
 * - I: Input type
 * - O: Output type
 * - f: Discrimination function
 * - c: Confidence function
 * - τ: Trace function
 */

// ============================================================================
// TYPES
// ============================================================================

/**
 * Confidence zone classification
 */
export type Zone = 'GREEN' | 'YELLOW' | 'RED';

/**
 * Zone thresholds
 */
export const ZONE_THRESHOLDS = {
  green: 0.90,
  yellow: 0.75,
} as const;

/**
 * Classify confidence into zone
 */
export function classifyZone(confidence: number): Zone {
  if (confidence >= ZONE_THRESHOLDS.green) return 'GREEN';
  if (confidence >= ZONE_THRESHOLDS.yellow) return 'YELLOW';
  return 'RED';
}

/**
 * Result of tile execution
 */
export interface TileResult<O> {
  output: O;
  confidence: number;
  zone: Zone;
  trace: string;
  duration: number;
  metadata?: Record<string, unknown>;
}

/**
 * Validation result
 */
export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  code: string;
  message: string;
  path?: string;
}

export interface ValidationWarning {
  code: string;
  message: string;
  suggestion?: string;
}

/**
 * Schema definition (simplified for core)
 */
export interface Schema<T> {
  type: string;
  description?: string;
  validate(value: unknown): value is T;
}

/**
 * Serialized tile for storage/transfer
 */
export interface SerializedTile {
  id: string;
  version: string;
  type: string;
  inputSchema: unknown;
  outputSchema: unknown;
  config: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

/**
 * Tile configuration
 */
export interface TileConfig {
  id?: string;
  version?: string;
  timeout?: number;
  retries?: number;
  cache?: boolean;
  cacheTTL?: number;
}

// ============================================================================
// CORE TILE INTERFACE
// ============================================================================

/**
 * Base Tile interface
 *
 * Every tile implements this interface. The five components:
 * - I (Input): What it takes
 * - O (Output): What it produces
 * - f (discriminate): The work it does
 * - c (confidence): How sure it is [0, 1]
 * - τ (trace): Why it decided
 */
export interface ITile<I, O> {
  // Identity
  readonly id: string;
  readonly version: string;
  readonly type: string;

  // Types
  readonly inputSchema: Schema<I>;
  readonly outputSchema: Schema<O>;

  // Core operations
  discriminate(input: I): Promise<O>;
  confidence(input: I): Promise<number>;
  trace(input: I): Promise<string>;

  // Lifecycle
  validate(): ValidationResult;
  serialize(): SerializedTile;

  // Composition
  compose<R>(other: ITile<O, R>): ITile<I, R>;
  parallel<O2>(other: ITile<I, O2>): ITile<I, [O, O2]>;
}

// ============================================================================
// BASE TILE IMPLEMENTATION
// ============================================================================

/**
 * Abstract base class for tiles
 *
 * Provides common functionality while requiring implementation of:
 * - discriminate()
 * - confidence()
 * - trace()
 */
export abstract class Tile<I, O> implements ITile<I, O> {
  readonly id: string;
  readonly version: string;
  readonly type: string;
  readonly inputSchema: Schema<I>;
  readonly outputSchema: Schema<O>;

  protected config: TileConfig;
  private cache: Map<string, { result: TileResult<O>; timestamp: number }> = new Map();

  constructor(
    inputSchema: Schema<I>,
    outputSchema: Schema<O>,
    config: TileConfig = {}
  ) {
    this.id = config.id ?? this.generateId();
    this.version = config.version ?? '1.0.0';
    this.type = this.constructor.name;
    this.inputSchema = inputSchema;
    this.outputSchema = outputSchema;
    this.config = {
      timeout: 30000,
      retries: 0,
      cache: true,
      cacheTTL: 60000,
      ...config,
    };
  }

  // Abstract methods - must be implemented by subclasses
  abstract discriminate(input: I): Promise<O>;
  abstract confidence(input: I): Promise<number>;
  abstract trace(input: I): Promise<string>;

  /**
   * Execute the tile with full result
   */
  async execute(input: I): Promise<TileResult<O>> {
    const startTime = performance.now();

    // Check cache
    if (this.config.cache) {
      const cached = this.getCached(input);
      if (cached) {
        return { ...cached, duration: performance.now() - startTime };
      }
    }

    // Validate input
    if (!this.inputSchema.validate(input)) {
      throw new TileValidationError(
        `Invalid input for tile ${this.id}: expected ${this.inputSchema.type}`
      );
    }

    // Execute with retries
    let lastError: Error | null = null;
    for (let attempt = 0; attempt <= (this.config.retries ?? 0); attempt++) {
      try {
        const [output, conf, tr] = await Promise.all([
          this.discriminate(input),
          this.confidence(input),
          this.trace(input),
        ]);

        const result: TileResult<O> = {
          output,
          confidence: conf,
          zone: classifyZone(conf),
          trace: tr,
          duration: performance.now() - startTime,
        };

        // Cache result
        if (this.config.cache) {
          this.setCached(input, result);
        }

        return result;
      } catch (e) {
        lastError = e instanceof Error ? e : new Error(String(e));
        if (attempt < (this.config.retries ?? 0)) {
          await this.delay(100 * Math.pow(2, attempt)); // Exponential backoff
        }
      }
    }

    throw lastError ?? new Error('Tile execution failed');
  }

  /**
   * Validate the tile configuration
   */
  validate(): ValidationResult {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];

    if (!this.id) {
      errors.push({ code: 'MISSING_ID', message: 'Tile ID is required' });
    }

    if (!this.version) {
      warnings.push({
        code: 'MISSING_VERSION',
        message: 'Tile version not specified',
        suggestion: 'Add version for better tracking',
      });
    }

    if (!this.inputSchema) {
      errors.push({ code: 'MISSING_INPUT_SCHEMA', message: 'Input schema is required' });
    }

    if (!this.outputSchema) {
      errors.push({ code: 'MISSING_OUTPUT_SCHEMA', message: 'Output schema is required' });
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
    };
  }

  /**
   * Serialize tile for storage/transfer
   */
  serialize(): SerializedTile {
    return {
      id: this.id,
      version: this.version,
      type: this.type,
      inputSchema: this.inputSchema,
      outputSchema: this.outputSchema,
      config: this.config,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
  }

  /**
   * Sequential composition: this ; other
   *
   * Output of this tile feeds into the other tile.
   * Confidence multiplies: c(this ; other) = c(this) × c(other)
   */
  compose<R>(other: ITile<O, R>): ITile<I, R> {
    return new ComposedTile(this, other);
  }

  /**
   * Parallel composition: this || other
   *
   * Both tiles run independently on the same input.
   * Confidence averages: c(this || other) = (c(this) + c(other)) / 2
   */
  parallel<O2>(other: ITile<I, O2>): ITile<I, [O, O2]> {
    return new ParallelTile(this, other);
  }

  // Protected helpers
  protected generateId(): string {
    return `${this.constructor.name}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private getCached(input: I): TileResult<O> | null {
    const key = this.hashInput(input);
    const cached = this.cache.get(key);
    if (!cached) return null;

    const age = Date.now() - cached.timestamp;
    if (age > (this.config.cacheTTL ?? 60000)) {
      this.cache.delete(key);
      return null;
    }

    return cached.result;
  }

  private setCached(input: I, result: TileResult<O>): void {
    const key = this.hashInput(input);
    this.cache.set(key, { result, timestamp: Date.now() });
  }

  private hashInput(input: I): string {
    return JSON.stringify(input);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// ============================================================================
// COMPOSED TILE (Sequential)
// ============================================================================

/**
 * Tile created by sequential composition: A ; B
 *
 * Properties:
 * - Output of A feeds into B
 * - Confidence multiplies: c(A ; B) = c(A) × c(B)
 * - Traces concatenate: τ(A ; B) = τ(A) + τ(B)
 */
class ComposedTile<I, M, O> extends Tile<I, O> {
  private first: ITile<I, M>;
  private second: ITile<M, O>;

  constructor(first: ITile<I, M>, second: ITile<M, O>) {
    super(
      first.inputSchema,
      second.outputSchema,
      { id: `${first.id}_${second.id}`, version: '1.0.0' }
    );
    this.first = first;
    this.second = second;
  }

  async discriminate(input: I): Promise<O> {
    const intermediate = await this.executeFirst(input);
    return await this.executeSecond(intermediate);
  }

  async confidence(input: I): Promise<number> {
    const c1 = await this.first.confidence(input);
    const intermediate = await this.executeFirst(input);
    const c2 = await this.second.confidence(intermediate);
    return c1 * c2; // Multiplicative composition
  }

  async trace(input: I): Promise<string> {
    const t1 = await this.first.trace(input);
    const intermediate = await this.executeFirst(input);
    const t2 = await this.second.trace(intermediate);
    return `${t1} → ${t2}`;
  }

  private async executeFirst(input: I): Promise<M> {
    if (this.first instanceof Tile) {
      const result = await this.first.execute(input);
      return result.output;
    }
    return await this.first.discriminate(input);
  }

  private async executeSecond(input: M): Promise<O> {
    if (this.second instanceof Tile) {
      const result = await this.second.execute(input);
      return result.output;
    }
    return await this.second.discriminate(input);
  }
}

// ============================================================================
// PARALLEL TILE
// ============================================================================

/**
 * Tile created by parallel composition: A || B
 *
 * Properties:
 * - Both tiles run on the same input
 * - Output is a tuple: [O1, O2]
 * - Confidence averages: c(A || B) = (c(A) + c(B)) / 2
 * - Traces combine: τ(A || B) = τ(A) | τ(B)
 */
class ParallelTile<I, O1, O2> extends Tile<I, [O1, O2]> {
  private first: ITile<I, O1>;
  private second: ITile<I, O2>;

  constructor(first: ITile<I, O1>, second: ITile<I, O2>) {
    super(
      first.inputSchema,
      {
        type: 'tuple',
        validate: (v): v is [O1, O2] => Array.isArray(v) && v.length === 2,
      },
      { id: `${first.id}_parallel_${second.id}`, version: '1.0.0' }
    );
    this.first = first;
    this.second = second;
  }

  async discriminate(input: I): Promise<[O1, O2]> {
    const [o1, o2] = await Promise.all([
      this.executeFirst(input),
      this.executeSecond(input),
    ]);
    return [o1, o2];
  }

  async confidence(input: I): Promise<number> {
    const [c1, c2] = await Promise.all([
      this.first.confidence(input),
      this.second.confidence(input),
    ]);
    return (c1 + c2) / 2; // Average composition
  }

  async trace(input: I): Promise<string> {
    const [t1, t2] = await Promise.all([
      this.first.trace(input),
      this.second.trace(input),
    ]);
    return `${t1} | ${t2}`;
  }

  private async executeFirst(input: I): Promise<O1> {
    if (this.first instanceof Tile) {
      const result = await this.first.execute(input);
      return result.output;
    }
    return await this.first.discriminate(input);
  }

  private async executeSecond(input: I): Promise<O2> {
    if (this.second instanceof Tile) {
      const result = await this.second.execute(input);
      return result.output;
    }
    return await this.second.discriminate(input);
  }
}

// ============================================================================
// ERRORS
// ============================================================================

export class TileError extends Error {
  constructor(
    message: string,
    public readonly tileId: string,
    public readonly code: string
  ) {
    super(message);
    this.name = 'TileError';
  }
}

export class TileValidationError extends TileError {
  constructor(message: string, tileId: string = 'unknown') {
    super(message, tileId, 'VALIDATION_ERROR');
    this.name = 'TileValidationError';
  }
}

export class TileExecutionError extends TileError {
  constructor(message: string, tileId: string, public readonly cause?: Error) {
    super(message, tileId, 'EXECUTION_ERROR');
    this.name = 'TileExecutionError';
  }
}

export class TileTimeoutError extends TileError {
  constructor(tileId: string, timeout: number) {
    super(
      `Tile ${tileId} timed out after ${timeout}ms`,
      tileId,
      'TIMEOUT_ERROR'
    );
    this.name = 'TileTimeoutError';
  }
}

// ============================================================================
// SCHEMA BUILDERS
// ============================================================================

/**
 * Common schema builders
 */
export const Schemas = {
  string: {
    type: 'string',
    validate: (v: unknown): v is string => typeof v === 'string',
  },

  number: {
    type: 'number',
    validate: (v: unknown): v is number => typeof v === 'number' && !isNaN(v),
  },

  boolean: {
    type: 'boolean',
    validate: (v: unknown): v is boolean => typeof v === 'boolean',
  },

  array: <T>(itemSchema: Schema<T>): Schema<T[]> => ({
    type: 'array',
    validate: (v: unknown): v is T[] =>
      Array.isArray(v) && v.every(itemSchema.validate),
  }),

  object: <T extends Record<string, unknown>>(
    shape: { [K in keyof T]: Schema<T[K]> }
  ): Schema<T> => ({
    type: 'object',
    validate: (v: unknown): v is T => {
      if (typeof v !== 'object' || v === null) return false;
      const obj = v as Record<string, unknown>;
      return Object.entries(shape).every(
        ([key, schema]) => key in obj && schema.validate(obj[key])
      );
    },
  }),

  union: <T extends readonly unknown[]>(
    ...schemas: { [K in keyof T]: Schema<T[K]> }
  ): Schema<T[number]> => ({
    type: 'union',
    validate: (v: unknown): v is T[number] =>
      schemas.some(schema => schema.validate(v)),
  }),

  literal: <T extends string | number | boolean>(value: T): Schema<T> => ({
    type: 'literal',
    validate: (v: unknown): v is T => v === value,
  }),
};

// ============================================================================
// EXPORTS
// ============================================================================

export default Tile;
