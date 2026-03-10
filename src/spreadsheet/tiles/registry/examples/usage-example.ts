/**
 * Tile Registry Usage Examples
 *
 * Demonstrates how to use the tile registry system
 */

import {
  tileRegistry,
  TileRegistry,
  DependencyValidator,
  TileResolver,
  TileMetadata,
  registerExampleTiles
} from '../index';

// ========================================
// Example 1: Basic Registration
// ========================================

async function basicRegistration() {
  console.log('\n=== Example 1: Basic Registration ===\n');

  // Register example tiles
  registerExampleTiles(tileRegistry);

  // List all registered tiles
  const tiles = tileRegistry.list();
  console.log(`Registered ${tiles.length} tiles:`);
  for (const tile of tiles) {
    console.log(`  - ${tile.metadata.id}@${tile.metadata.version}: ${tile.metadata.name}`);
  }

  // Get registry statistics
  const stats = tileRegistry.getStats();
  console.log('\nRegistry Statistics:', stats);
}

// ========================================
// Example 2: Tile Discovery
// ========================================

async function tileDiscovery() {
  console.log('\n=== Example 2: Tile Discovery ===\n');

  // Find by type
  const validators = tileRegistry.findByType('validator');
  console.log(`Found ${validators.length} validator tiles:`);
  for (const tile of validators) {
    console.log(`  - ${tile.metadata.name}: ${tile.metadata.description}`);
  }

  // Find by capability
  const withEmbedCapability = tileRegistry.findByCapability('embed');
  console.log(`\nFound ${withEmbedCapability.length} tiles with 'embed' capability`);

  // Find by tag
  const mlTiles = tileRegistry.findByTag('ml');
  console.log(`\nFound ${mlTiles.length} ML tiles:`);
  for (const tile of mlTiles) {
    console.log(`  - ${tile.metadata.name}`);
  }

  // Search with query
  const results = tileRegistry.search({
    searchText: 'text',
    type: 'transform'
  });
  console.log(`\nSearch results (${results.length} tiles):`);
  for (const tile of results) {
    console.log(`  - ${tile.metadata.name}: ${tile.metadata.description}`);
  }
}

// ========================================
// Example 3: Dependency Validation
// ========================================

async function dependencyValidation() {
  console.log('\n=== Example 3: Dependency Validation ===\n');

  const validator = new DependencyValidator(tileRegistry);

  // Get a tile with dependencies
  const aggregator = tileRegistry.get('array-aggregator');
  if (aggregator) {
    console.log(`Validating dependencies for: ${aggregator.metadata.name}`);

    const resolution = validator.validate(aggregator.metadata);

    console.log(`Resolved: ${resolution.resolved.size} dependencies`);
    for (const [id, version] of resolution.resolved) {
      console.log(`  - ${id}@${version}`);
    }

    console.log(`Unresolved: ${resolution.unresolved.size} dependencies`);
    console.log(`Conflicts: ${resolution.conflicts.length} conflicts`);
    console.log(`Circular: ${resolution.circular.length} circular dependencies`);

    console.log(`Load order: ${resolution.order.join(' -> ')}`);
  }

  // Check if tile can be loaded
  const canLoad = validator.canLoad('array-aggregator');
  console.log(`\nCan load 'array-aggregator': ${canLoad}`);

  // Get dependency tree
  const tree = validator.getDependencyTree('array-aggregator', '2.0.1');
  console.log('\nDependency Tree:');
  console.log(JSON.stringify(tree, null, 2));
}

// ========================================
// Example 4: Tile Resolution and Loading
// ========================================

async function tileResolution() {
  console.log('\n=== Example 4: Tile Resolution and Loading ===\n');

  const validator = new DependencyValidator(tileRegistry);
  const resolver = new TileResolver(tileRegistry, validator);

  // Resolve a tile
  try {
    const result = await resolver.resolve('text-transformer', '1.0.0');

    console.log(`Resolved tile: ${result.tile.metadata.name}`);
    console.log(`Load time: ${result.tile.loadTime}ms`);
    console.log(`Dependencies: ${result.dependencies.size}`);
    console.log(`Total load time: ${result.loadTime}ms`);

    // Execute the tile
    const instance = result.tile.instance;
    const output = await instance.execute({
      operation: 'uppercase',
      text: 'hello world'
    });

    console.log(`\nExecution result: ${output}`);
  } catch (error) {
    console.error('Error resolving tile:', error);
  }

  // Get cache stats
  const cacheStats = resolver.getCacheStats();
  console.log('\nCache Statistics:', cacheStats);
}

// ========================================
// Example 5: Creating Custom Tiles
// ========================================

async function customTileExample() {
  console.log('\n=== Example 5: Creating Custom Tiles ===\n');

  // Define custom tile metadata
  const customTileMetadata: TileMetadata = {
    id: 'date-formatter',
    name: 'Date Formatter',
    version: '1.0.0',
    type: 'transform',
    category: 'datetime',
    description: 'Formats dates using various patterns',
    author: 'Custom Developer',
    tags: ['date', 'time', 'format'],
    capabilities: [
      {
        name: 'format',
        description: 'Format date to string',
        inputTypes: ['Date'],
        outputTypes: ['string'],
        properties: {
          pattern: 'string',
          locale: 'string'
        }
      },
      {
        name: 'parse',
        description: 'Parse date from string',
        inputTypes: ['string'],
        outputTypes: ['Date'],
        properties: {
          pattern: 'string',
          locale: 'string'
        }
      }
    ],
    dependencies: [],
    config: {
      timeout: 1000,
      cacheable: true
    },
    implementation: {
      module: './custom-tiles',
      exportName: 'DateFormatterTile',
      strategy: 'lazy',
      browser: true,
      node: true
    },
    createdAt: new Date(),
    license: 'MIT'
  };

  // Register custom tile
  tileRegistry.register(customTileMetadata);
  console.log(`Registered custom tile: ${customTileMetadata.name}`);

  // Find custom tile
  const custom = tileRegistry.get('date-formatter');
  console.log(`Found custom tile: ${custom?.metadata.name}`);

  // Search for custom tiles
  const customTiles = tileRegistry.findByCategory('datetime');
  console.log(`Custom datetime tiles: ${customTiles.length}`);
}

// ========================================
// Example 6: Version Management
// ========================================

async function versionManagement() {
  console.log('\n=== Example 6: Version Management ===\n');

  // Register multiple versions
  const versions = ['1.0.0', '1.1.0', '2.0.0'];

  for (const version of versions) {
    const metadata: TileMetadata = {
      id: 'versioned-tile',
      name: `Versioned Tile v${version}`,
      version,
      type: 'transform',
      category: 'example',
      description: `Example tile version ${version}`,
      capabilities: [
        {
          name: 'transform',
          description: 'Transform data',
          inputTypes: ['any'],
          outputTypes: ['any']
        }
      ],
      dependencies: [],
      implementation: {
        module: './versioned-tile',
        strategy: 'eager',
        browser: true,
        node: true
      }
    };

    tileRegistry.register(metadata);
  }

  // Find all versions
  const allVersions = tileRegistry.findAllVersions('versioned-tile');
  console.log(`All versions of 'versioned-tile':`);
  for (const tile of allVersions) {
    console.log(`  - ${tile.metadata.version}`);
  }

  // Find latest version
  const latest = tileRegistry.findLatest('versioned-tile');
  console.log(`\nLatest version: ${latest}`);

  // Get specific version
  const specific = tileRegistry.get('versioned-tile', '1.1.0');
  console.log(`Specific version 1.1.0: ${specific?.metadata.name}`);

  // Search by version range
  const results = tileRegistry.search({
    searchText: 'versioned-tile',
    versionRange: '^1.0.0'
  });
  console.log(`\nVersions matching ^1.0.0: ${results.length}`);
  for (const tile of results) {
    console.log(`  - ${tile.metadata.version}`);
  }
}

// ========================================
// Example 7: Registry Export/Import
// ========================================

async function registryExportImport() {
  console.log('\n=== Example 7: Registry Export/Import ===\n');

  // Export registry
  const exported = tileRegistry.export();
  console.log(`Exported ${exported.tiles.length} tiles`);
  console.log(`Export date: ${exported.exportedAt}`);
  console.log(`Format version: ${exported.version}`);

  // Create new registry
  const newRegistry = new TileRegistry();

  // Import into new registry
  await newRegistry.import(exported);
  console.log(`\nImported ${newRegistry.list().length} tiles into new registry`);

  // Verify import
  const importedStats = newRegistry.getStats();
  console.log('Imported registry stats:', importedStats);
}

// ========================================
// Example 8: Confidence Flow
// ========================================

async function confidenceFlowExample() {
  console.log('\n=== Example 8: Confidence Flow ===\n');

  const validator = new DependencyValidator(tileRegistry);
  const resolver = new TileResolver(tileRegistry, validator);

  // Resolve confidence calculator
  const result = await resolver.resolve('confidence-calculator');
  const instance = result.tile.instance;

  // Sequential confidence (multiplication)
  const sequentialConf = await instance.execute({
    operation: 'sequential',
    confidences: [0.95, 0.90, 0.85]
  });
  console.log(`Sequential confidence: ${sequentialConf.toFixed(4)}`);
  console.log(`  (0.95 × 0.90 × 0.85 = ${sequentialConf.toFixed(4)})`);

  // Parallel confidence (weighted average)
  const parallelConf = await instance.execute({
    operation: 'parallel',
    confidences: [0.95, 0.80, 0.90],
    weights: [0.5, 0.3, 0.2]
  });
  console.log(`\nParallel confidence: ${parallelConf.toFixed(4)}`);
  console.log(`  (weighted average of [0.95, 0.80, 0.90] with weights [0.5, 0.3, 0.2])`);

  // Zone determination
  const zones = [
    { confidence: 0.95, label: 'High quality' },
    { confidence: 0.82, label: 'Good quality' },
    { confidence: 0.65, label: 'Low quality' }
  ];

  console.log('\nZone Determination:');
  for (const { confidence, label } of zones) {
    const zone = await instance.execute({
      operation: 'zone',
      confidence
    });
    console.log(`  ${label} (${confidence.toFixed(2)}): ${zone} zone`);
  }
}

// ========================================
// Main Runner
// ========================================

async function main() {
  console.log('='.repeat(50));
  console.log('Tile Registry System - Usage Examples');
  console.log('='.repeat(50));

  try {
    await basicRegistration();
    await tileDiscovery();
    await dependencyValidation();
    await tileResolution();
    await customTileExample();
    await versionManagement();
    await registryExportImport();
    await confidenceFlowExample();

    console.log('\n' + '='.repeat(50));
    console.log('All examples completed successfully!');
    console.log('='.repeat(50));
  } catch (error) {
    console.error('Error running examples:', error);
  }
}

// Run if executed directly
if (require.main === module) {
  main().catch(console.error);
}

export {
  basicRegistration,
  tileDiscovery,
  dependencyValidation,
  tileResolution,
  customTileExample,
  versionManagement,
  registryExportImport,
  confidenceFlowExample
};
