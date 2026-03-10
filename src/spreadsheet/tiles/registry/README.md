# Tile Registry System

A comprehensive extensibility and discovery system for SMP tiles. Provides type-safe registration, semantic versioning, dependency resolution, and dynamic loading.

## Features

- **Type-safe registry** with full TypeScript support
- **Semantic versioning** (semver) with range matching
- **Dependency validation** with conflict detection
- **Circular dependency detection**
- **Dynamic tile loading** with caching
- **Tile discovery** by type, capability, metadata
- **Registry export/import** for sharing

## Architecture

```
tile-registry.ts        # Main registry, SemVer, indexing
dependency-validator.ts  # Dependency resolution, validation
tile-resolver.ts        # Dynamic loading, caching
examples/
  ├── example-tiles.ts  # Example tile implementations
  └── usage-example.ts  # Comprehensive usage examples
```

## Quick Start

### Basic Registration

```typescript
import { tileRegistry, TileMetadata } from './src/spreadsheet/tiles/registry';

const metadata: TileMetadata = {
  id: 'my-tile',
  name: 'My Custom Tile',
  version: '1.0.0',
  type: 'transform',
  category: 'custom',
  description: 'Does something cool',
  capabilities: [
    {
      name: 'transform',
      description: 'Transforms data',
      inputTypes: ['any'],
      outputTypes: ['any']
    }
  ],
  dependencies: [],
  implementation: {
    module: './my-tile',
    exportName: 'MyTile',
    strategy: 'lazy',
    browser: true,
    node: true
  }
};

tileRegistry.register(metadata);
```

### Tile Discovery

```typescript
// Find by type
const validators = tileRegistry.findByType('validator');

// Find by capability
const withEmbed = tileRegistry.findByCapability('embed');

// Find by tag
const mlTiles = tileRegistry.findByTag('ml');

// Advanced search
const results = tileRegistry.search({
  searchText: 'text',
  type: 'transform',
  tags: ['nlp']
});
```

### Dependency Validation

```typescript
import { DependencyValidator } from './src/spreadsheet/tiles/registry';

const validator = new DependencyValidator(tileRegistry);
const resolution = validator.validate(metadata);

console.log('Resolved:', resolution.resolved.size);
console.log('Conflicts:', resolution.conflicts.length);
console.log('Load order:', resolution.order);
```

### Tile Loading

```typescript
import { TileResolver, DependencyValidator } from './src/spreadsheet/tiles/registry';

const validator = new DependencyValidator(tileRegistry);
const resolver = new TileResolver(tileRegistry, validator);

// Resolve and load
const result = await resolver.resolve('text-transformer', '1.0.0');

// Use the tile
const output = await result.tile.instance.execute({
  operation: 'uppercase',
  text: 'hello'
});
```

## Tile Metadata Structure

```typescript
interface TileMetadata {
  // Core identification
  id: string;              // Unique identifier
  name: string;            // Human-readable name
  version: string;         // Semver version (e.g., "1.2.3")

  // Classification
  type: TileType;          // transform, validator, aggregator, etc.
  category: string;        // Custom category (e.g., "text-processing")

  // Description
  description: string;     // Short description
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
```

## Tile Types

- `transform` - Data transformation
- `validator` - Data validation
- `aggregator` - Data aggregation
- `generator` - Data generation
- `classifier` - Classification
- `regressor` - Regression
- `embedder` - Embedding generation
- `retriever` - Retrieval
- `memory` - Memory operations
- `controller` - Control flow
- `adapter` - Format conversion
- `custom` - Custom type

## Semantic Versioning

The registry supports full semver with range matching:

```typescript
import { SemVer } from './src/spreadsheet/tiles/registry';

const version = SemVer.parse('1.2.3');

// Check if satisfies range
version.satisfies('^1.0.0');  // true
version.satisfies('~1.2.0');  // true
version.satisfies('>=1.0.0'); // true
version.satisfies('<2.0.0');  // true

// Compare versions
version.compare(SemVer.parse('1.2.4')); // -1 (less than)
```

## Dependency Management

### Specifying Dependencies

```typescript
dependencies: [
  {
    tileId: 'text-embedder',
    versionRange: '^1.0.0',  // semver range
    optional: false,
    reason: 'Used for text embedding'
  }
]
```

### Version Ranges

- `^1.2.3` - Compatible with 1.x.x (>=1.2.3 <2.0.0)
- `~1.2.3` - Approximately 1.2.x (>=1.2.3 <1.3.0)
- `>=1.2.3` - Greater than or equal to
- `<2.0.0` - Less than
- `1.2.3 - 2.0.0` - Range
- `1.2.3` - Exact match

## Creating Custom Tiles

### Tile Interface

```typescript
export interface Tile {
  metadata: TileMetadata;
  execute(input: any, context?: TileContext): Promise<any>;
}
```

### Example Implementation

```typescript
export class MyCustomTile implements Tile {
  metadata: TileMetadata = {
    id: 'my-custom',
    name: 'My Custom Tile',
    version: '1.0.0',
    type: 'transform',
    category: 'custom',
    description: 'Does something cool',
    capabilities: [
      {
        name: 'process',
        description: 'Process data',
        inputTypes: ['any'],
        outputTypes: ['any']
      }
    ],
    dependencies: [],
    implementation: {
      module: './my-custom-tile',
      exportName: 'MyCustomTile',
      strategy: 'lazy',
      browser: true,
      node: true
    }
  };

  async execute(input: any, context?: TileContext): Promise<any> {
    // Process input
    return { result: 'processed' };
  }
}
```

## Registry Events

The registry emits events for monitoring:

```typescript
tileRegistry.on('tile:registered', (id, metadata) => {
  console.log(`Registered: ${id}`);
});

tileRegistry.on('tile:loaded', (id) => {
  console.log(`Loaded: ${id}`);
});

tileRegistry.on('tile:load-error', (id, error) => {
  console.error(`Failed to load ${id}:`, error);
});
```

## Advanced Features

### Dependency Graph

```typescript
const validator = new DependencyValidator(tileRegistry);
const graph = validator.buildGraph(metadata);
const tree = validator.getDependencyTree('tile-id', '1.0.0');
```

### Version Management

```typescript
// Find all versions
const versions = tileRegistry.findAllVersions('my-tile');

// Find latest version
const latest = tileRegistry.findLatest('my-tile');

// Get specific version
const tile = tileRegistry.get('my-tile', '1.2.3');
```

### Registry Export/Import

```typescript
// Export
const exported = tileRegistry.export();
console.log(exported.tiles);

// Import to new registry
const newRegistry = new TileRegistry();
await newRegistry.import(exported);
```

### Cache Management

```typescript
const resolver = new TileResolver(tileRegistry, validator);

// Preload tiles
await resolver.preload(['tile1', 'tile2']);

// Get cache stats
const stats = resolver.getCacheStats();

// Clear cache
resolver.clear();
```

## Example Tiles Included

1. **TextTransformerTile** - Text transformation (uppercase, lowercase, trim, normalize)
2. **NumberValidatorTile** - Numeric validation (range, integer, positive)
3. **ArrayAggregatorTile** - Array aggregation (sum, average, min, max, count)
4. **TextEmbedderTile** - Text embedding generation with caching
5. **ConfidenceCalculatorTile** - Confidence flow calculations

## Running Examples

```bash
# Run all examples
ts-node src/spreadsheet/tiles/registry/examples/usage-example.ts

# Or run individual examples
import { basicRegistration, tileDiscovery } from './examples/usage-example';

await basicRegistration();
await tileDiscovery();
```

## Marketplace Foundation

This registry provides the foundation for a tile marketplace:

- **Unique identification** with id and version
- **Metadata** for searchability and discovery
- **Semantic versioning** for compatibility
- **Dependencies** for integration
- **Implementation specs** for dynamic loading
- **Export/import** for sharing

Future marketplace features can build on:
- Tile ratings and reviews
- Download counts and popularity
- Verified publisher badges
- Commercial licensing support
- Usage analytics

## License

MIT
