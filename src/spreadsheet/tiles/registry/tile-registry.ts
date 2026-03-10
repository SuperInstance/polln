/**
 * Tile Registry - Extensibility and Discovery System
 *
 * Provides:
 * - Tile registration with metadata
 * - Semantic versioning
 * - Dependency resolution
 * - Dynamic tile loading
 * - Type-safe registry
 */

import { EventEmitter } from 'events';

/**
 * Semantic version parser and comparator
 */
export class SemVer {
  constructor(
    public major: number,
    public minor: number,
    public patch: number,
    public prerelease?: string,
    public build?: string
  ) {}

  static parse(version: string): SemVer {
    const match = version.match(
      /^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+))?(?:\+([0-9A-Za-z-]+))?$/
    );
    if (!match) {
      throw new Error(`Invalid semver: ${version}`);
    }
    return new SemVer(
      parseInt(match[1]),
      parseInt(match[2]),
      parseInt(match[3]),
      match[4],
      match[5]
    );
  }

  compare(other: SemVer): number {
    if (this.major !== other.major) return this.major - other.major;
    if (this.minor !== other.minor) return this.minor - other.minor;
    if (this.patch !== other.patch) return this.patch - other.patch;

    // Prerelease versions come before release versions
    if (!this.prerelease && other.prerelease) return 1;
    if (this.prerelease && !other.prerelease) return -1;
    if (this.prerelease && other.prerelease) {
      return this.prerelease.localeCompare(other.prerelease);
    }

    return 0;
  }

  satisfies(range: string): boolean {
    // Simple semver range matching
    // Supports: ^1.2.3, ~1.2.3, >=1.2.3, <2.0.0, 1.2.3 - 2.0.0
    if (range.startsWith('^')) {
      const min = SemVer.parse(range.slice(1));
      const max = new SemVer(min.major + 1, 0, 0);
      return this.compare(min) >= 0 && this.compare(max) < 0;
    }

    if (range.startsWith('~')) {
      const min = SemVer.parse(range.slice(1));
      const max = new SemVer(min.major, min.minor + 1, 0);
      return this.compare(min) >= 0 && this.compare(max) < 0;
    }

    if (range.startsWith('>=')) {
      const min = SemVer.parse(range.slice(2));
      return this.compare(min) >= 0;
    }

    if (range.startsWith('<')) {
      const max = SemVer.parse(range.slice(1));
      return this.compare(max) < 0;
    }

    if (range.includes(' - ')) {
      const [minStr, maxStr] = range.split(' - ');
      const min = SemVer.parse(minStr);
      const max = SemVer.parse(maxStr);
      return this.compare(min) >= 0 && this.compare(max) <= 0;
    }

    // Exact match
    const exact = SemVer.parse(range);
    return this.compare(exact) === 0;
  }

  toString(): string {
    let result = `${this.major}.${this.minor}.${this.patch}`;
    if (this.prerelease) result += `-${this.prerelease}`;
    if (this.build) result += `+${this.build}`;
    return result;
  }
}

/**
 * Tile capability descriptor
 */
export interface TileCapability {
  name: string;
  description: string;
  inputTypes: string[];
  outputTypes: string[];
  properties?: Record<string, any>;
}

/**
 * Tile metadata interface
 */
export interface TileMetadata {
  // Core identification
  id: string;
  name: string;
  version: string;

  // Classification
  type: TileType;
  category: string;

  // Description
  description: string;
  longDescription?: string;
  author?: string;
  tags?: string[];

  // Capabilities
  capabilities: TileCapability[];

  // Dependencies
  dependencies?: TileDependency[];

  // Configuration
  config?: TileConfig;

  // Loading
  implementation?: TileImplementation;

  // Validation
  schema?: TileSchema;

  // Metadata
  createdAt?: Date;
  updatedAt?: Date;
  license?: string;
  homepage?: string;
  repository?: string;
}

/**
 * Tile types
 */
export type TileType =
  | 'transform'      // Data transformation
  | 'validator'      // Data validation
  | 'aggregator'     // Data aggregation
  | 'generator'      // Data generation
  | 'classifier'     // Classification
  | 'regressor'      // Regression
  | 'embedder'       // Embedding generation
  | 'retriever'      // Retrieval
  | 'memory'         // Memory operations
  | 'controller'     // Control flow
  | 'adapter'        // Format conversion
  | 'custom';        // Custom type

/**
 * Tile dependency specification
 */
export interface TileDependency {
  tileId: string;
  versionRange: string;
  optional?: boolean;
  reason?: string;
}

/**
 * Tile configuration
 */
export interface TileConfig {
  // Execution settings
  timeout?: number;
  maxRetries?: number;
  parallelizable?: boolean;

  // Resource limits
  maxMemory?: number;
  maxCpu?: number;

  // Caching
  cacheable?: boolean;
  cacheTTL?: number;

  // Monitoring
  metrics?: boolean;
  logging?: boolean;

  // Custom config
  custom?: Record<string, any>;
}

/**
 * Tile implementation specification
 */
export interface TileImplementation {
  // Module path for dynamic loading
  module: string;

  // Export name
  exportName?: string;

  // Loading strategy
  strategy: 'eager' | 'lazy' | 'async';

  // Browser-compatible
  browser?: boolean;

  // Node-compatible
  node?: boolean;
}

/**
 * Tile schema for validation
 */
export interface TileSchema {
  input: any;
  output: any;
  config?: any;
}

/**
 * Registered tile entry
 */
export interface RegisteredTile {
  metadata: TileMetadata;
  instance?: any;
  loaded: boolean;
  loadError?: Error;
}

/**
 * Registry events
 */
export type RegistryEvent =
  | 'tile:registered'
  | 'tile:unregistered'
  | 'tile:updated'
  | 'tile:loaded'
  | 'tile:load-error';

/**
 * Main Tile Registry class
 */
export class TileRegistry extends EventEmitter {
  private tiles: Map<string, RegisteredTile> = new Map();
  private byType: Map<TileType, Set<string>> = new Map();
  private byCategory: Map<string, Set<string>> = new Map();
  private byCapability: Map<string, Set<string>> = new Map();
  private byTag: Map<string, Set<string>> = new Map();

  /**
   * Register a tile
   */
  register(metadata: TileMetadata): void {
    const id = this.makeTileId(metadata.id, metadata.version);

    if (this.tiles.has(id)) {
      throw new Error(`Tile already registered: ${id}`);
    }

    // Validate metadata
    this.validateMetadata(metadata);

    // Create registered tile
    const registeredTile: RegisteredTile = {
      metadata,
      loaded: false
    };

    // Store tile
    this.tiles.set(id, registeredTile);

    // Index by type
    if (!this.byType.has(metadata.type)) {
      this.byType.set(metadata.type, new Set());
    }
    this.byType.get(metadata.type)!.add(id);

    // Index by category
    if (!this.byCategory.has(metadata.category)) {
      this.byCategory.set(metadata.category, new Set());
    }
    this.byCategory.get(metadata.category)!.add(id);

    // Index by capabilities
    for (const cap of metadata.capabilities) {
      if (!this.byCapability.has(cap.name)) {
        this.byCapability.set(cap.name, new Set());
      }
      this.byCapability.get(cap.name)!.add(id);
    }

    // Index by tags
    for (const tag of metadata.tags || []) {
      if (!this.byTag.has(tag)) {
        this.byTag.set(tag, new Set());
      }
      this.byTag.get(tag)!.add(id);
    }

    this.emit('tile:registered', id, metadata);
  }

  /**
   * Unregister a tile
   */
  unregister(tileId: string, version?: string): boolean {
    const id = version ? this.makeTileId(tileId, version) : this.findLatest(tileId);

    if (!id || !this.tiles.has(id)) {
      return false;
    }

    const tile = this.tiles.get(id)!;

    // Remove from indexes
    this.byType.get(tile.metadata.type)?.delete(id);
    this.byCategory.get(tile.metadata.category)?.delete(id);

    for (const cap of tile.metadata.capabilities) {
      this.byCapability.get(cap.name)?.delete(id);
    }

    for (const tag of tile.metadata.tags || []) {
      this.byTag.get(tag)?.delete(id);
    }

    // Remove tile
    this.tiles.delete(id);

    this.emit('tile:unregistered', id);
    return true;
  }

  /**
   * Update a tile
   */
  update(metadata: TileMetadata): void {
    const id = this.makeTileId(metadata.id, metadata.version);

    if (!this.tiles.has(id)) {
      throw new Error(`Tile not found: ${id}`);
    }

    this.unregister(metadata.id, metadata.version);
    this.register(metadata);

    this.emit('tile:updated', id, metadata);
  }

  /**
   * Get a tile
   */
  get(tileId: string, version?: string): RegisteredTile | undefined {
    const id = version ? this.makeTileId(tileId, version) : this.findLatest(tileId);
    return id ? this.tiles.get(id) : undefined;
  }

  /**
   * Check if tile exists
   */
  has(tileId: string, version?: string): boolean {
    const id = version ? this.makeTileId(tileId, version) : this.findLatest(tileId);
    return id !== undefined && this.tiles.has(id);
  }

  /**
   * Find all versions of a tile
   */
  findAllVersions(tileId: string): RegisteredTile[] {
    const versions: RegisteredTile[] = [];

    for (const [id, tile] of this.tiles) {
      if (id.startsWith(`${tileId}@`)) {
        versions.push(tile);
      }
    }

    // Sort by version descending
    versions.sort((a, b) => {
      const verA = SemVer.parse(a.metadata.version);
      const verB = SemVer.parse(b.metadata.version);
      return verB.compare(verA);
    });

    return versions;
  }

  /**
   * Find latest version of a tile
   */
  findLatest(tileId: string): string | undefined {
    const versions = this.findAllVersions(tileId);
    return versions.length > 0
      ? this.makeTileId(tileId, versions[0].metadata.version)
      : undefined;
  }

  /**
   * Find tiles by type
   */
  findByType(type: TileType): RegisteredTile[] {
    const ids = this.byType.get(type);
    if (!ids) return [];

    return Array.from(ids)
      .map(id => this.tiles.get(id))
      .filter(Boolean) as RegisteredTile[];
  }

  /**
   * Find tiles by category
   */
  findByCategory(category: string): RegisteredTile[] {
    const ids = this.byCategory.get(category);
    if (!ids) return [];

    return Array.from(ids)
      .map(id => this.tiles.get(id))
      .filter(Boolean) as RegisteredTile[];
  }

  /**
   * Find tiles by capability
   */
  findByCapability(capability: string): RegisteredTile[] {
    const ids = this.byCapability.get(capability);
    if (!ids) return [];

    return Array.from(ids)
      .map(id => this.tiles.get(id))
      .filter(Boolean) as RegisteredTile[];
  }

  /**
   * Find tiles by tag
   */
  findByTag(tag: string): RegisteredTile[] {
    const ids = this.byTag.get(tag);
    if (!ids) return [];

    return Array.from(ids)
      .map(id => this.tiles.get(id))
      .filter(Boolean) as RegisteredTile[];
  }

  /**
   * Search tiles by query
   */
  search(query: TileSearchQuery): RegisteredTile[] {
    let results = Array.from(this.tiles.values());

    if (query.type) {
      results = results.filter(t => t.metadata.type === query.type);
    }

    if (query.category) {
      results = results.filter(t => t.metadata.category === query.category);
    }

    if (query.capability) {
      results = results.filter(t =>
        t.metadata.capabilities.some(c => c.name === query.capability)
      );
    }

    if (query.tags && query.tags.length > 0) {
      results = results.filter(t =>
        query.tags!.some(tag => t.metadata.tags?.includes(tag))
      );
    }

    if (query.author) {
      results = results.filter(t => t.metadata.author === query.author);
    }

    if (query.searchText) {
      const searchLower = query.searchText.toLowerCase();
      results = results.filter(t =>
        t.metadata.name.toLowerCase().includes(searchLower) ||
        t.metadata.description.toLowerCase().includes(searchLower) ||
        t.metadata.id.toLowerCase().includes(searchLower)
      );
    }

    if (query.versionRange) {
      results = results.filter(t => {
        const ver = SemVer.parse(t.metadata.version);
        return ver.satisfies(query.versionRange!);
      });
    }

    return results;
  }

  /**
   * List all registered tiles
   */
  list(): RegisteredTile[] {
    return Array.from(this.tiles.values());
  }

  /**
   * Get registry statistics
   */
  getStats(): RegistryStats {
    const byType: Record<TileType, number> = {} as any;
    const byCategory: Record<string, number> = {};

    for (const tile of this.tiles.values()) {
      byType[tile.metadata.type] = (byType[tile.metadata.type] || 0) + 1;
      byCategory[tile.metadata.category] = (byCategory[tile.metadata.category] || 0) + 1;
    }

    return {
      totalTiles: this.tiles.size,
      byType,
      byCategory,
      totalCapabilities: this.byCapability.size,
      totalTags: this.byTag.size
    };
  }

  /**
   * Validate metadata
   */
  private validateMetadata(metadata: TileMetadata): void {
    if (!metadata.id) throw new Error('Tile ID is required');
    if (!metadata.name) throw new Error('Tile name is required');
    if (!metadata.version) throw new Error('Tile version is required');
    if (!metadata.type) throw new Error('Tile type is required');
    if (!metadata.category) throw new Error('Tile category is required');
    if (!metadata.description) throw new Error('Tile description is required');
    if (!metadata.capabilities || metadata.capabilities.length === 0) {
      throw new Error('Tile must have at least one capability');
    }

    // Validate version format
    SemVer.parse(metadata.version);

    // Validate dependencies
    if (metadata.dependencies) {
      for (const dep of metadata.dependencies) {
        if (!dep.tileId) throw new Error('Dependency tileId is required');
        if (!dep.versionRange) throw new Error('Dependency versionRange is required');
      }
    }
  }

  /**
   * Make tile ID from id and version
   */
  private makeTileId(tileId: string, version: string): string {
    return `${tileId}@${version}`;
  }

  /**
   * Export registry to JSON
   */
  export(): RegistryExport {
    const tiles: Record<string, TileMetadata> = {};

    for (const [id, tile] of this.tiles) {
      tiles[id] = tile.metadata;
    }

    return {
      version: '1.0.0',
      exportedAt: new Date().toISOString(),
      tiles
    };
  }

  /**
   * Import registry from JSON
   */
  async import(data: RegistryExport): Promise<void> {
    for (const [id, metadata] of Object.entries(data.tiles)) {
      try {
        this.register(metadata);
      } catch (error) {
        console.error(`Failed to import tile ${id}:`, error);
      }
    }
  }
}

/**
 * Tile search query
 */
export interface TileSearchQuery {
  type?: TileType;
  category?: string;
  capability?: string;
  tags?: string[];
  author?: string;
  searchText?: string;
  versionRange?: string;
}

/**
 * Registry statistics
 */
export interface RegistryStats {
  totalTiles: number;
  byType: Record<TileType, number>;
  byCategory: Record<string, number>;
  totalCapabilities: number;
  totalTags: number;
}

/**
 * Registry export format
 */
export interface RegistryExport {
  version: string;
  exportedAt: string;
  tiles: Record<string, TileMetadata>;
}

// Create singleton registry instance
export const tileRegistry = new TileRegistry();
