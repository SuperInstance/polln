/**
 * Tile Registry System
 *
 * Main entry point for the tile registry, dependency validation, and resolution
 */

// Core registry
export {
  TileRegistry,
  tileRegistry,
  SemVer,
  TileMetadata,
  TileType,
  TileCapability,
  TileDependency,
  TileConfig,
  TileImplementation,
  TileSchema,
  RegisteredTile,
  RegistryEvent,
  TileSearchQuery,
  RegistryStats,
  RegistryExport
} from './tile-registry';

// Dependency validation
export {
  DependencyValidator,
  DependencyNode,
  DependencyEdge,
  DependencyResolution,
  DependencyConflict,
  ValidationOptions,
  DependencyTree,
  DependencyTreeNode
} from './dependency-validator';

// Tile resolution
export {
  TileResolver,
  LoadOptions,
  LoadedTile,
  TileResolution,
  CacheStats
} from './tile-resolver';

// Example tiles
export {
  TextTransformerTile,
  NumberValidatorTile,
  ArrayAggregatorTile,
  TextEmbedderTile,
  ConfidenceCalculatorTile,
  registerExampleTiles,
  Tile,
  TileContext
} from './examples/example-tiles';
