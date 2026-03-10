/**
 * Tile Registry - Discovery and Dependency Resolution
 *
 * Central registry for tiles with:
 * - Registration and lookup
 * - Dependency validation
 * - Version management
 * - Type discovery
 */

import { ITile, Tile, Schema, ValidationResult, ValidationError, ValidationWarning } from './Tile';

// ============================================================================
// TYPES
// ============================================================================

/**
 * Tile metadata stored in registry
 */
export interface TileMetadata {
  id: string;
  type: string;
  version: string;
  description?: string;
  tags: string[];
  inputType: string;
  outputType: string;
  dependencies: string[];
  createdAt: Date;
  updatedAt: Date;
  deprecated?: boolean;
  supersededBy?: string;
}

/**
 * Registration options
 */
export interface RegistrationOptions {
  description?: string;
  tags?: string[];
  dependencies?: string[];
  deprecated?: boolean;
  supersededBy?: string;
}

/**
 * Search query for tiles
 */
export interface TileQuery {
  type?: string | RegExp;
  inputType?: string;
  outputType?: string;
  tags?: string[];
  deprecated?: boolean;
  version?: string;
}

/**
 * Registry statistics
 */
export interface RegistryStats {
  totalTiles: number;
  uniqueTypes: number;
  deprecatedCount: number;
  inputTypes: Record<string, number>;
  outputTypes: Record<string, number>;
  tagFrequency: Record<string, number>;
}

// ============================================================================
// TILE REGISTRY IMPLEMENTATION
// ============================================================================

/**
 * TileRegistry - Central tile discovery and management
 *
 * Features:
 * - Register tiles with metadata
 * - Lookup by id, type, or capability
 * - Dependency resolution
 * - Version management
 * - Deprecation handling
 */
export class TileRegistry {
  private tiles: Map<string, ITile<any, any>> = new Map();
  private metadata: Map<string, TileMetadata> = new Map();
  private typeIndex: Map<string, Set<string>> = new Map();
  private tagIndex: Map<string, Set<string>> = new Map();
  private inputTypeIndex: Map<string, Set<string>> = new Map();
  private outputTypeIndex: Map<string, Set<string>> = new Map();

  /**
   * Register a tile
   */
  register<I, O>(
    tile: ITile<I, O>,
    options: RegistrationOptions = {}
  ): ValidationResult {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];

    // Validate tile
    const tileValidation = tile.validate();
    if (!tileValidation.valid) {
      errors.push(...tileValidation.errors);
    }
    warnings.push(...tileValidation.warnings);

    // Check for duplicate ID
    if (this.tiles.has(tile.id)) {
      const existing = this.metadata.get(tile.id);
      if (existing && existing.version === tile.version) {
        errors.push({
          code: 'DUPLICATE_REGISTRATION',
          message: `Tile ${tile.id} v${tile.version} already registered`,
          path: 'id',
        });
      } else {
        warnings.push({
          code: 'VERSION_OVERRIDE',
          message: `Overriding ${tile.id} v${existing?.version} with v${tile.version}`,
        });
      }
    }

    // Validate dependencies exist
    if (options.dependencies) {
      for (const dep of options.dependencies) {
        if (!this.tiles.has(dep)) {
          warnings.push({
            code: 'MISSING_DEPENDENCY',
            message: `Dependency ${dep} not yet registered`,
            suggestion: 'Register dependencies before use',
          });
        }
      }
    }

    // If validation passed, register
    if (errors.length === 0) {
      this.tiles.set(tile.id, tile);

      const meta: TileMetadata = {
        id: tile.id,
        type: tile.type,
        version: tile.version,
        description: options.description,
        tags: options.tags ?? [],
        inputType: tile.inputSchema.type,
        outputType: tile.outputSchema.type,
        dependencies: options.dependencies ?? [],
        createdAt: new Date(),
        updatedAt: new Date(),
        deprecated: options.deprecated,
        supersededBy: options.supersededBy,
      };

      this.metadata.set(tile.id, meta);
      this.updateIndexes(tile.id, meta);
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
    };
  }

  /**
   * Unregister a tile
   */
  unregister(id: string): boolean {
    const tile = this.tiles.get(id);
    if (!tile) return false;

    const meta = this.metadata.get(id);
    if (meta) {
      this.removeFromIndexes(id, meta);
    }

    this.tiles.delete(id);
    this.metadata.delete(id);
    return true;
  }

  /**
   * Get tile by ID
   */
  get<I, O>(id: string): ITile<I, O> | undefined {
    return this.tiles.get(id) as ITile<I, O> | undefined;
  }

  /**
   * Get metadata by ID
   */
  getMetadata(id: string): TileMetadata | undefined {
    return this.metadata.get(id);
  }

  /**
   * Check if tile exists
   */
  has(id: string): boolean {
    return this.tiles.has(id);
  }

  /**
   * Find tiles matching query
   */
  find(query: TileQuery): ITile<any, any>[] {
    let candidates = new Set(this.tiles.keys());

    // Filter by type
    if (query.type) {
      const typeIds = this.findByType(query.type);
      candidates = this.intersect(candidates, typeIds);
    }

    // Filter by input type
    if (query.inputType) {
      const inputIds = this.inputTypeIndex.get(query.inputType) ?? new Set();
      candidates = this.intersect(candidates, inputIds);
    }

    // Filter by output type
    if (query.outputType) {
      const outputIds = this.outputTypeIndex.get(query.outputType) ?? new Set();
      candidates = this.intersect(candidates, outputIds);
    }

    // Filter by tags
    if (query.tags && query.tags.length > 0) {
      for (const tag of query.tags) {
        const tagIds = this.tagIndex.get(tag) ?? new Set();
        candidates = this.intersect(candidates, tagIds);
      }
    }

    // Filter deprecated
    if (query.deprecated === false) {
      candidates = new Set(
        [...candidates].filter(id => !this.metadata.get(id)?.deprecated)
      );
    }

    // Filter version
    if (query.version) {
      candidates = new Set(
        [...candidates].filter(id => this.metadata.get(id)?.version === query.version)
      );
    }

    return [...candidates].map(id => this.tiles.get(id)!);
  }

  /**
   * Find tiles by type (supports regex)
   */
  findByType(type: string | RegExp): Set<string> {
    if (typeof type === 'string') {
      return this.typeIndex.get(type) ?? new Set();
    }

    // Regex search
    const matches = new Set<string>();
    for (const [t, ids] of this.typeIndex) {
      if (type.test(t)) {
        for (const id of ids) {
          matches.add(id);
        }
      }
    }
    return matches;
  }

  /**
   * Find tiles that can produce given output type
   */
  findByOutputType(outputType: string): ITile<any, any>[] {
    const ids = this.outputTypeIndex.get(outputType) ?? new Set();
    return [...ids].map(id => this.tiles.get(id)!);
  }

  /**
   * Find tiles that accept given input type
   */
  findByInputType(inputType: string): ITile<any, any>[] {
    const ids = this.inputTypeIndex.get(inputType) ?? new Set();
    return [...ids].map(id => this.tiles.get(id)!);
  }

  /**
   * Find chain from input type to output type
   *
   * Uses BFS to find shortest path
   */
  findChain(inputType: string, outputType: string): ITile<any, any>[] | null {
    // Direct connection
    const direct = this.find({
      inputType,
      outputType,
      deprecated: false,
    });

    if (direct.length > 0) {
      return [direct[0]];
    }

    // BFS for path
    const queue: { type: string; path: ITile<any, any>[] }[] = [
      { type: inputType, path: [] },
    ];
    const visited = new Set<string>();

    while (queue.length > 0) {
      const current = queue.shift()!;

      if (visited.has(current.type)) continue;
      visited.add(current.type);

      // Find tiles that accept current type as input
      const nextTiles = this.findByInputType(current.type).filter(
        t => !this.metadata.get(t.id)?.deprecated
      );

      for (const tile of nextTiles) {
        const meta = this.metadata.get(tile.id)!;
        const newPath = [...current.path, tile];

        if (meta.outputType === outputType) {
          return newPath;
        }

        queue.push({
          type: meta.outputType,
          path: newPath,
        });
      }
    }

    return null; // No path found
  }

  /**
   * Validate dependencies for all registered tiles
   */
  validateDependencies(): ValidationResult {
    const errors: ValidationError[] = [];
    const warnings: ValidationWarning[] = [];

    for (const [id, meta] of this.metadata) {
      for (const dep of meta.dependencies) {
        if (!this.tiles.has(dep)) {
          errors.push({
            code: 'UNRESOLVED_DEPENDENCY',
            message: `Tile ${id} depends on ${dep} which is not registered`,
            path: id,
          });
        }
      }

      // Check for deprecated dependencies
      for (const dep of meta.dependencies) {
        const depMeta = this.metadata.get(dep);
        if (depMeta?.deprecated) {
          warnings.push({
            code: 'DEPRECATED_DEPENDENCY',
            message: `Tile ${id} depends on deprecated tile ${dep}`,
            suggestion: depMeta.supersededBy
              ? `Use ${depMeta.supersededBy} instead`
              : 'Consider updating dependency',
          });
        }
      }
    }

    return {
      valid: errors.length === 0,
      errors,
      warnings,
    };
  }

  /**
   * Get registry statistics
   */
  getStats(): RegistryStats {
    const inputTypes: Record<string, number> = {};
    const outputTypes: Record<string, number> = {};
    const tagFrequency: Record<string, number> = {};
    let deprecatedCount = 0;

    for (const meta of this.metadata.values()) {
      inputTypes[meta.inputType] = (inputTypes[meta.inputType] ?? 0) + 1;
      outputTypes[meta.outputType] = (outputTypes[meta.outputType] ?? 0) + 1;

      for (const tag of meta.tags) {
        tagFrequency[tag] = (tagFrequency[tag] ?? 0) + 1;
      }

      if (meta.deprecated) deprecatedCount++;
    }

    return {
      totalTiles: this.tiles.size,
      uniqueTypes: this.typeIndex.size,
      deprecatedCount,
      inputTypes,
      outputTypes,
      tagFrequency,
    };
  }

  /**
   * List all registered tile IDs
   */
  listIds(): string[] {
    return [...this.tiles.keys()];
  }

  /**
   * Clear all registrations
   */
  clear(): void {
    this.tiles.clear();
    this.metadata.clear();
    this.typeIndex.clear();
    this.tagIndex.clear();
    this.inputTypeIndex.clear();
    this.outputTypeIndex.clear();
  }

  // Private helpers

  private updateIndexes(id: string, meta: TileMetadata): void {
    // Type index
    if (!this.typeIndex.has(meta.type)) {
      this.typeIndex.set(meta.type, new Set());
    }
    this.typeIndex.get(meta.type)!.add(id);

    // Input type index
    if (!this.inputTypeIndex.has(meta.inputType)) {
      this.inputTypeIndex.set(meta.inputType, new Set());
    }
    this.inputTypeIndex.get(meta.inputType)!.add(id);

    // Output type index
    if (!this.outputTypeIndex.has(meta.outputType)) {
      this.outputTypeIndex.set(meta.outputType, new Set());
    }
    this.outputTypeIndex.get(meta.outputType)!.add(id);

    // Tag index
    for (const tag of meta.tags) {
      if (!this.tagIndex.has(tag)) {
        this.tagIndex.set(tag, new Set());
      }
      this.tagIndex.get(tag)!.add(id);
    }
  }

  private removeFromIndexes(id: string, meta: TileMetadata): void {
    this.typeIndex.get(meta.type)?.delete(id);
    this.inputTypeIndex.get(meta.inputType)?.delete(id);
    this.outputTypeIndex.get(meta.outputType)?.delete(id);

    for (const tag of meta.tags) {
      this.tagIndex.get(tag)?.delete(id);
    }
  }

  private intersect(a: Set<string>, b: Set<string>): Set<string> {
    return new Set([...a].filter(x => b.has(x)));
  }
}

// ============================================================================
// GLOBAL REGISTRY (Singleton)
// ============================================================================

/**
 * Global tile registry instance
 *
 * Use for shared tile discovery across the application
 */
export const globalRegistry = new TileRegistry();

// ============================================================================
// REGISTRY DECORATOR
// ============================================================================

/**
 * Decorator to auto-register a tile class
 *
 * @example
 * ```typescript
 * @RegisterTile({ tags: ['nlp', 'sentiment'] })
 * class SentimentTile extends Tile<string, Sentiment> {
 *   // ...
 * }
 * ```
 */
export function RegisterTile(options: RegistrationOptions = {}) {
  return function <T extends { new (...args: any[]): ITile<any, any> }>(constructor: T) {
    // Create instance with default args
    const instance = new constructor();
    globalRegistry.register(instance, options);
    return constructor;
  };
}

// ============================================================================
// EXPORTS
// ============================================================================

export default TileRegistry;
