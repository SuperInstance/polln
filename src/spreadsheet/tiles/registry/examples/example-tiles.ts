/**
 * Example Custom Tiles
 *
 * Demonstrates how to create and register custom tiles
 */

import {
  TileMetadata,
  TileType,
  TileRegistry,
  tileRegistry
} from '../tile-registry';

// ========================================
// Base Tile Interface
// ========================================

export interface Tile {
  metadata: TileMetadata;
  execute(input: any, context?: TileContext): Promise<any>;
}

export interface TileContext {
  cache?: any;
  memory?: any;
  dependencies?: Map<string, any>;
}

// ========================================
// Example Tile 1: Text Transformer
// ========================================

export class TextTransformerTile implements Tile {
  metadata: TileMetadata = {
    id: 'text-transformer',
    name: 'Text Transformer',
    version: '1.0.0',
    type: 'transform',
    category: 'text-processing',
    description: 'Transforms text using various operations',
    longDescription: 'Provides text transformation capabilities including case conversion, trimming, and normalization',
    author: 'Example Author',
    tags: ['text', 'transform', 'string'],
    capabilities: [
      {
        name: 'uppercase',
        description: 'Convert text to uppercase',
        inputTypes: ['string'],
        outputTypes: ['string'],
        properties: { locale: 'en-US' }
      },
      {
        name: 'lowercase',
        description: 'Convert text to lowercase',
        inputTypes: ['string'],
        outputTypes: ['string'],
        properties: { locale: 'en-US' }
      },
      {
        name: 'trim',
        description: 'Remove whitespace from text',
        inputTypes: ['string'],
        outputTypes: ['string']
      },
      {
        name: 'normalize',
        description: 'Normalize text (NFC)',
        inputTypes: ['string'],
        outputTypes: ['string']
      }
    ],
    dependencies: [],
    config: {
      timeout: 5000,
      cacheable: true,
      cacheTTL: 60000
    },
    implementation: {
      module: './example-tiles',
      exportName: 'TextTransformerTile',
      strategy: 'lazy',
      browser: true,
      node: true
    },
    createdAt: new Date(),
    license: 'MIT'
  };

  async execute(input: any, context?: TileContext): Promise<any> {
    const { operation, text } = input;

    switch (operation) {
      case 'uppercase':
        return text.toUpperCase();
      case 'lowercase':
        return text.toLowerCase();
      case 'trim':
        return text.trim();
      case 'normalize':
        return text.normalize('NFC');
      default:
        throw new Error(`Unknown operation: ${operation}`);
    }
  }
}

// ========================================
// Example Tile 2: Number Validator
// ========================================

export class NumberValidatorTile implements Tile {
  metadata: TileMetadata = {
    id: 'number-validator',
    name: 'Number Validator',
    version: '1.2.0',
    type: 'validator',
    category: 'validation',
    description: 'Validates numeric values against constraints',
    longDescription: 'Provides comprehensive numeric validation with range checking, type validation, and custom constraints',
    author: 'Example Author',
    tags: ['validation', 'number', 'constraints'],
    capabilities: [
      {
        name: 'range',
        description: 'Validate number is within range',
        inputTypes: ['number'],
        outputTypes: ['boolean'],
        properties: {
          min: 'number',
          max: 'number',
          inclusive: 'boolean'
        }
      },
      {
        name: 'integer',
        description: 'Validate number is integer',
        inputTypes: ['number'],
        outputTypes: ['boolean']
      },
      {
        name: 'positive',
        description: 'Validate number is positive',
        inputTypes: ['number'],
        outputTypes: ['boolean']
      }
    ],
    dependencies: [],
    config: {
      timeout: 1000,
      cacheable: true
    },
    implementation: {
      module: './example-tiles',
      exportName: 'NumberValidatorTile',
      strategy: 'eager',
      browser: true,
      node: true
    },
    createdAt: new Date(),
    license: 'MIT'
  };

  async execute(input: any, context?: TileContext): Promise<any> {
    const { operation, value, constraints } = input;

    switch (operation) {
      case 'range':
        const { min, max, inclusive = true } = constraints;
        if (inclusive) {
          return value >= min && value <= max;
        } else {
          return value > min && value < max;
        }

      case 'integer':
        return Number.isInteger(value);

      case 'positive':
        return typeof value === 'number' && value > 0;

      default:
        throw new Error(`Unknown operation: ${operation}`);
    }
  }
}

// ========================================
// Example Tile 3: Array Aggregator
// ========================================

export class ArrayAggregatorTile implements Tile {
  metadata: TileMetadata = {
    id: 'array-aggregator',
    name: 'Array Aggregator',
    version: '2.0.1',
    type: 'aggregator',
    category: 'aggregation',
    description: 'Aggregates array data using various functions',
    longDescription: 'Provides array aggregation capabilities including sum, average, min, max, and custom aggregations',
    author: 'Example Author',
    tags: ['aggregation', 'array', 'statistics'],
    capabilities: [
      {
        name: 'sum',
        description: 'Calculate sum of numbers',
        inputTypes: ['array'],
        outputTypes: ['number'],
        properties: { property: 'string' }
      },
      {
        name: 'average',
        description: 'Calculate average of numbers',
        inputTypes: ['array'],
        outputTypes: ['number'],
        properties: { property: 'string' }
      },
      {
        name: 'min',
        description: 'Find minimum value',
        inputTypes: ['array'],
        outputTypes: ['number'],
        properties: { property: 'string' }
      },
      {
        name: 'max',
        description: 'Find maximum value',
        inputTypes: ['array'],
        outputTypes: ['number'],
        properties: { property: 'string' }
      },
      {
        name: 'count',
        description: 'Count elements',
        inputTypes: ['array'],
        outputTypes: ['number']
      }
    ],
    dependencies: [
      {
        tileId: 'number-validator',
        versionRange: '^1.0.0',
        optional: true,
        reason: 'Used for validating numeric inputs'
      }
    ],
    config: {
      timeout: 5000,
      parallelizable: true,
      cacheable: true
    },
    implementation: {
      module: './example-tiles',
      exportName: 'ArrayAggregatorTile',
      strategy: 'lazy',
      browser: true,
      node: true
    },
    createdAt: new Date(),
    license: 'MIT'
  };

  async execute(input: any, context?: TileContext): Promise<any> {
    const { operation, array, property } = input;

    // Extract property if specified
    const values = property
      ? array.map((item: any) => item[property])
      : array;

    switch (operation) {
      case 'sum':
        return values.reduce((a: number, b: number) => a + b, 0);

      case 'average':
        return values.reduce((a: number, b: number) => a + b, 0) / values.length;

      case 'min':
        return Math.min(...values);

      case 'max':
        return Math.max(...values);

      case 'count':
        return values.length;

      default:
        throw new Error(`Unknown operation: ${operation}`);
    }
  }
}

// ========================================
// Example Tile 4: Text Embedder
// ========================================

export class TextEmbedderTile implements Tile {
  metadata: TileMetadata = {
    id: 'text-embedder',
    name: 'Text Embedder',
    version: '1.5.0',
    type: 'embedder',
    category: 'ml',
    description: 'Generates text embeddings using a small model',
    longDescription: 'Creates dense vector representations of text for similarity search and clustering',
    author: 'Example Author',
    tags: ['embedding', 'ml', 'nlp', 'vector'],
    capabilities: [
      {
        name: 'embed',
        description: 'Generate text embedding',
        inputTypes: ['string'],
        outputTypes: ['array'],
        properties: {
          dimensions: 384,
          model: 'miniLM'
        }
      },
      {
        name: 'batch-embed',
        description: 'Generate embeddings for multiple texts',
        inputTypes: ['array'],
        outputTypes: ['array'],
        properties: {
          dimensions: 384,
          batchSize: 32
        }
      }
    ],
    dependencies: [],
    config: {
      timeout: 30000,
      maxMemory: 512 * 1024 * 1024, // 512MB
      cacheable: true,
      cacheTTL: 3600000 // 1 hour
    },
    implementation: {
      module: './example-tiles',
      exportName: 'TextEmbedderTile',
      strategy: 'async',
      browser: false,
      node: true
    },
    createdAt: new Date(),
    license: 'MIT'
  };

  private cache: Map<string, number[]> = new Map();

  async execute(input: any, context?: TileContext): Promise<any> {
    const { operation, text, texts } = input;

    switch (operation) {
      case 'embed':
        // Check cache
        if (this.cache.has(text)) {
          return this.cache.get(text);
        }

        // Simulate embedding generation (in reality, would call a model)
        const embedding = this.generateMockEmbedding(text);
        this.cache.set(text, embedding);
        return embedding;

      case 'batch-embed':
        return texts.map((t: string) => this.generateMockEmbedding(t));

      default:
        throw new Error(`Unknown operation: ${operation}`);
    }
  }

  private generateMockEmbedding(text: string): number[] {
    // Simulate embedding with deterministic pseudo-random values
    const dims = 384;
    const embedding: number[] = [];

    for (let i = 0; i < dims; i++) {
      const hash = this.hash(text + i);
      embedding.push((hash % 1000) / 1000);
    }

    return embedding;
  }

  private hash(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
  }
}

// ========================================
// Example Tile 5: Confidence Calculator
// ========================================

export class ConfidenceCalculatorTile implements Tile {
  metadata: TileMetadata = {
    id: 'confidence-calculator',
    name: 'Confidence Calculator',
    version: '1.0.0',
    type: 'transform',
    category: 'confidence',
    description: 'Calculates confidence flow through tile chains',
    longDescription: 'Implements confidence flow theory for sequential and parallel tile compositions',
    author: 'Example Author',
    tags: ['confidence', 'validation', 'quality'],
    capabilities: [
      {
        name: 'sequential',
        description: 'Calculate sequential confidence (multiplication)',
        inputTypes: ['array'],
        outputTypes: ['number'],
        properties: {
          confidences: 'array<number>'
        }
      },
      {
        name: 'parallel',
        description: 'Calculate parallel confidence (weighted average)',
        inputTypes: ['array', 'array'],
        outputTypes: ['number'],
        properties: {
          confidences: 'array<number>',
          weights: 'array<number>'
        }
      },
      {
        name: 'zone',
        description: 'Determine confidence zone',
        inputTypes: ['number'],
        outputTypes: ['string'],
        properties: {
          greenThreshold: 0.90,
          yellowThreshold: 0.75
        }
      }
    ],
    dependencies: [],
    config: {
      timeout: 1000,
      cacheable: false
    },
    implementation: {
      module: './example-tiles',
      exportName: 'ConfidenceCalculatorTile',
      strategy: 'eager',
      browser: true,
      node: true
    },
    createdAt: new Date(),
    license: 'MIT'
  };

  async execute(input: any, context?: TileContext): Promise<any> {
    const { operation, confidences, weights, confidence, thresholds } = input;

    switch (operation) {
      case 'sequential':
        // Multiply confidences
        return confidences.reduce((acc: number, c: number) => acc * c, 1.0);

      case 'parallel':
        // Weighted average
        const totalWeight = weights.reduce((a: number, b: number) => a + b, 0);
        return confidences.reduce((acc: number, c: number, i: number) =>
          acc + (c * weights[i]) / totalWeight, 0.0
        );

      case 'zone':
        const greenThreshold = thresholds?.green || 0.90;
        const yellowThreshold = thresholds?.yellow || 0.75;

        if (confidence >= greenThreshold) return 'GREEN';
        if (confidence >= yellowThreshold) return 'YELLOW';
        return 'RED';

      default:
        throw new Error(`Unknown operation: ${operation}`);
    }
  }
}

// ========================================
// Registration Helper
// ========================================

export function registerExampleTiles(registry: TileRegistry = tileRegistry): void {
  registry.register(new TextTransformerTile().metadata);
  registry.register(new NumberValidatorTile().metadata);
  registry.register(new ArrayAggregatorTile().metadata);
  registry.register(new TextEmbedderTile().metadata);
  registry.register(new ConfidenceCalculatorTile().metadata);

  console.log('Registered 5 example tiles');
}

// Auto-register if this module is imported
if (typeof window === 'undefined') {
  registerExampleTiles();
}
