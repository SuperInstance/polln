/**
 * SMP Tile Core Module
 *
 * The foundation of Seed-Model-Prompt programming.
 * Every tile is: Discriminating, Inspectable, Trainable, Composable.
 *
 * T = (I, O, f, c, τ)
 * - I: Input type
 * - O: Output type
 * - f: Discrimination function
 * - c: Confidence function
 * - τ: Trace function
 *
 * @module @polln/spreadsheet/tiles/core
 */

// ============================================================================
// CORE TILE INTERFACE AND IMPLEMENTATION
// ============================================================================

export {
  // Types
  Zone,
  ZONE_THRESHOLDS,
  classifyZone,
  TileResult,
  ValidationResult,
  ValidationError,
  ValidationWarning,
  Schema,
  SerializedTile,
  TileConfig,

  // Core interface
  ITile,

  // Base implementation
  Tile,

  // Errors
  TileError,
  TileValidationError,
  TileExecutionError,
  TileTimeoutError,

  // Schema builders
  Schemas,
} from './Tile';

// ============================================================================
// TILE CHAIN - PIPELINE COMPOSITION
// ============================================================================

export {
  // Main class
  TileChain,

  // Types
  ChainResult,
  StepResult,
  ChainTrace,
  TraceStep,

  // Errors
  ChainError,
  ChainCompositionError,
  ChainExecutionError,
} from './TileChain';

// ============================================================================
// REGISTRY - DISCOVERY AND RESOLUTION
// ============================================================================

export {
  // Main class
  TileRegistry,
  globalRegistry,

  // Types
  TileMetadata,
  RegistrationOptions,
  TileQuery,
  RegistryStats,

  // Decorator
  RegisterTile,
} from './Registry';

// ============================================================================
// RE-EXPORT CONVENIENCE
// ============================================================================

/**
 * Create a new tile chain starting with a tile
 *
 * @example
 * ```typescript
 * import { chain, SentimentTile } from '@polln/spreadsheet/tiles/core';
 *
 * const pipeline = chain(new SentimentTile())
 *   .add(new NormalizeTile())
 *   .add(new FormatTile());
 *
 * const result = await pipeline.execute("I love this product!");
 * console.log(result.zone); // 'GREEN'
 * ```
 */
import { TileChain } from './TileChain';
import { ITile } from './Tile';

export function chain<I, O>(tile: ITile<I, O>): TileChain<I, O> {
  return TileChain.start(tile);
}

/**
 * Create an empty chain with input schema
 *
 * @example
 * ```typescript
 * import { emptyChain, Schemas } from '@polln/spreadsheet/tiles/core';
 *
 * const pipeline = emptyChain(Schemas.string)
 *   .add(new TokenizeTile())
 *   .add(new AnalyzeTile());
 * ```
 */
import { Schema } from './Tile';

export function emptyChain<I>(inputSchema: Schema<I>): TileChain<I, I> {
  return TileChain.empty(inputSchema);
}
