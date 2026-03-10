/**
 * Tile Resolver
 *
 * Handles dynamic loading and resolution of tiles
 */

import { TileRegistry, TileMetadata, TileImplementation } from './tile-registry';
import { DependencyValidator, DependencyResolution } from './dependency-validator';

/**
 * Load options
 */
export interface LoadOptions {
  timeout?: number;
  retries?: number;
  force?: boolean;
  resolveDependencies?: boolean;
}

/**
 * Loaded tile instance
 */
export interface LoadedTile {
  metadata: TileMetadata;
  instance: any;
  loadTime: number;
  dependencies: Map<string, LoadedTile>;
}

/**
 * Tile resolution result
 */
export interface TileResolution {
  tile: LoadedTile;
  dependencies: Map<string, LoadedTile>;
  loadTime: number;
  errors: Error[];
}

/**
 * Tile Resolver class
 */
export class TileResolver {
  private cache: Map<string, LoadedTile> = new Map();
  private loading: Map<string, Promise<LoadedTile>> = new Map();

  constructor(
    private registry: TileRegistry,
    private validator: DependencyValidator
  ) {}

  /**
   * Resolve and load a tile
   */
  async resolve(
    tileId: string,
    version?: string,
    options: LoadOptions = {}
  ): Promise<TileResolution> {
    const startTime = Date.now();
    const errors: Error[] = [];
    const dependencies = new Map<string, LoadedTile>();

    // Get tile
    const tile = version
      ? this.registry.get(tileId, version)
      : this.registry.get(tileId);

    if (!tile) {
      throw new Error(`Tile not found: ${tileId}${version ? `@${version}` : ''}`);
    }

    // Validate dependencies if requested
    if (options.resolveDependencies !== false) {
      const resolution = this.validator.validate(tile.metadata);

      if (resolution.unresolved.size > 0) {
        throw new Error(
          `Unresolved dependencies: ${Array.from(resolution.unresolved).join(', ')}`
        );
      }

      if (resolution.circular.length > 0) {
        errors.push(
          new Error(`Circular dependencies detected: ${resolution.circular.join(' -> ')}`)
        );
      }

      // Load dependencies in order
      for (const depId of resolution.order) {
        const [depTileId, depVersion] = depId.split('@');
        if (depTileId !== tileId) {
          try {
            const dep = await this.load(depTileId, depVersion, options);
            dependencies.set(depId, dep);
          } catch (error) {
            errors.push(error as Error);
          }
        }
      }
    }

    // Load the tile
    const loaded = await this.load(tileId, tile.metadata.version, options);

    return {
      tile: loaded,
      dependencies,
      loadTime: Date.now() - startTime,
      errors
    };
  }

  /**
   * Load a tile instance
   */
  async load(
    tileId: string,
    version: string,
    options: LoadOptions = {}
  ): Promise<LoadedTile> {
    const cacheKey = `${tileId}@${version}`;

    // Check cache
    if (!options.force && this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }

    // Check if already loading
    if (this.loading.has(cacheKey)) {
      return this.loading.get(cacheKey)!;
    }

    // Get tile
    const tile = this.registry.get(tileId, version);
    if (!tile) {
      throw new Error(`Tile not found: ${tileId}@${version}`);
    }

    // Check if already loaded
    if (tile.loaded && tile.instance && !options.force) {
      const loaded: LoadedTile = {
        metadata: tile.metadata,
        instance: tile.instance,
        loadTime: 0,
        dependencies: new Map()
      };
      this.cache.set(cacheKey, loaded);
      return loaded;
    }

    // Load implementation
    const loadPromise = this.loadImplementation(tile.metadata, options);

    this.loading.set(cacheKey, loadPromise);

    try {
      const loaded = await loadPromise;
      this.cache.set(cacheKey, loaded);
      return loaded;
    } finally {
      this.loading.delete(cacheKey);
    }
  }

  /**
   * Load tile implementation
   */
  private async loadImplementation(
    metadata: TileMetadata,
    options: LoadOptions
  ): Promise<LoadedTile> {
    const startTime = Date.now();

    if (!metadata.implementation) {
      throw new Error(`Tile ${metadata.id} has no implementation specified`);
    }

    const impl = metadata.implementation;

    // Check platform compatibility
    if (typeof window !== 'undefined' && !impl.browser) {
      throw new Error(`Tile ${metadata.id} is not browser-compatible`);
    }

    if (typeof window === 'undefined' && !impl.node) {
      throw new Error(`Tile ${metadata.id} is not Node-compatible`);
    }

    // Dynamic import
    const retries = options.retries || 0;
    let lastError: Error | undefined;

    for (let i = 0; i <= retries; i++) {
      try {
        const module = await this.importModule(impl.module, options.timeout);

        // Get export
        const exportName = impl.exportName || 'default';
        const TileClass = module[exportName];

        if (!TileClass) {
          throw new Error(`Export '${exportName}' not found in ${impl.module}`);
        }

        // Instantiate
        const instance = new TileClass(metadata.config || {});

        const loaded: LoadedTile = {
          metadata,
          instance,
          loadTime: Date.now() - startTime,
          dependencies: new Map()
        };

        return loaded;
      } catch (error) {
        lastError = error as Error;
        if (i < retries) {
          await this.delay(100 * (i + 1)); // Exponential backoff
        }
      }
    }

    throw lastError || new Error('Failed to load tile');
  }

  /**
   * Import module with timeout
   */
  private async importModule(modulePath: string, timeout?: number): Promise<any> {
    if (timeout) {
      return Promise.race([
        import(modulePath),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Load timeout')), timeout)
        )
      ]);
    }

    return import(modulePath);
  }

  /**
   * Unload a tile
   */
  unload(tileId: string, version?: string): boolean {
    const id = version ? `${tileId}@${version}` : this.findCached(tileId);

    if (!id) {
      return false;
    }

    return this.cache.delete(id);
  }

  /**
   * Clear cache
   */
  clear(): void {
    this.cache.clear();
  }

  /**
   * Get cached tile
   */
  getCached(tileId: string, version?: string): LoadedTile | undefined {
    const id = version ? `${tileId}@${version}` : this.findCached(tileId);
    return id ? this.cache.get(id) : undefined;
  }

  /**
   * List cached tiles
   */
  listCached(): LoadedTile[] {
    return Array.from(this.cache.values());
  }

  /**
   * Get cache statistics
   */
  getCacheStats(): CacheStats {
    const byType: Record<string, number> = {};

    for (const tile of this.cache.values()) {
      const type = tile.metadata.type;
      byType[type] = (byType[type] || 0) + 1;
    }

    return {
      totalTiles: this.cache.size,
      byType,
      loading: this.loading.size
    };
  }

  /**
   * Find cached tile by ID
   */
  private findCached(tileId: string): string | undefined {
    for (const key of this.cache.keys()) {
      if (key.startsWith(`${tileId}@`)) {
        return key;
      }
    }
    return undefined;
  }

  /**
   * Delay helper
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Preload tiles
   */
  async preload(tileIds: string[], options: LoadOptions = {}): Promise<void> {
    await Promise.all(
      tileIds.map(id => this.resolve(id, undefined, options))
    );
  }
}

/**
 * Cache statistics
 */
export interface CacheStats {
  totalTiles: number;
  byType: Record<string, number>;
  loading: number;
}
