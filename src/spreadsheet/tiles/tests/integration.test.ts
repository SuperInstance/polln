/**
 * Integration Tests for Tile System
 *
 * Tests the confidence flow, zone classification, and composition behavior.
 */

import { Tile, Schemas, classifyZone, TileResult } from '../core/Tile';
import { TileChain } from '../core/TileChain';
import { TileRegistry } from '../core/Registry';

// ============================================================================
// TEST TILES
// ============================================================================

/**
 * Simple test tile for testing
 */
class TestTile<I, O> extends Tile<I, O> {
  private confValue: number;
  private traceValue: string;
  private outputValue: O;

  constructor(
    inputSchema: Schema<I>,
    outputSchema: Schema<O>,
    config: {
      id: string;
      confidence: number;
      trace: string;
      output: O;
    }
  ) {
    super(inputSchema, outputSchema, { id: config.id });
    this.confValue = config.confidence;
    this.traceValue = config.trace;
    this.outputValue = config.output;
  }

  async discriminate(input: I): Promise<O> {
    return this.outputValue;
  }

  async confidence(input: I): Promise<number> {
    return this.confValue;
  }

  async trace(input: I): Promise<string> {
    return this.traceValue;
  }
}

/**
 * Test input/output types
 */
interface TestInput {
  value: string;
}

interface TestOutput {
  result: string;
}

// ============================================================================
// INTEGRATION TESTS
// ============================================================================

describe('Tile Integration Tests', () => {
  let registry: TileRegistry;

  beforeEach(() => {
    registry = new TileRegistry();
  });

  // ---------------------------------------------------------------------------
  // Zone Classification Tests
  // ---------------------------------------------------------------------------

  describe('Zone Classification', () => {
    it('should classify GREEN zone for high confidence', () => {
    expect(classifyZone(0.0)).toBe('GREEN');
    expect(classifyZone(0.00)).toBe('GREEN');
    expect(classifyZone(0.95)).toBe('GREEN');
  });

  it('should classify YELLOW zone for medium confidence', () => {
    expect(classifyZone(0.89)).toBe('YELLOW');
    expect(classifyZone(0.80)).toBe('YELLOW');
    expect(classifyZone(0.75)).toBe('YELLOW');
  });

  it('should classify RED zone for low confidence', () => {
    expect(classifyZone(0.74)).toBe('RED');
    expect(classifyZone(0.50)).toBe('RED');
    expect(classifyZone(0.00)).toBe('RED');
  });
  });

  // ---------------------------------------------------------------------------
  // Confidence Flow Tests
  // ---------------------------------------------------------------------------

  describe('Confidence Flow', () => {
    it('should multiply confidence in sequential composition', async () => {
    const tile1 = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'tile1',
        confidence: 0.90,
        trace: 'First tile',
        output: { result: 'step1' },
      }
    );

    const tile2 = new TestTile<TestOutput, TestOutput>(
      Schemas.object({ result: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'tile2',
        confidence: 0.80,
        trace: 'Second tile',
        output: { result: 'step2' },
      }
    );

    const composed = tile1.compose(tile2);
    const result = await composed.execute({ value: 'test' });

    // Confidence should multiply: 0.90 * 0.80 = 0.72
    expect(result.confidence).toBeCloseTo(0.72, 2);
    expect(result.zone).toBe('RED'); // 0.72 is below 0.75
  });

  it('should average confidence in parallel composition', async () => {
    const tile1 = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'parallel1',
        confidence: 0.90,
        trace: 'Parallel tile 1',
        output: { result: 'p1' },
      }
    );

    const tile2 = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'parallel2',
        confidence: 0.70,
        trace: 'Parallel tile 2',
        output: { result: 'p2' },
      }
    );

    const parallel = tile1.parallel(tile2);
    const result = await parallel.execute({ value: 'test' });

    // Confidence should average: (0.90 + 0.70) / 2 = 0.80
    expect(result.confidence).toBeCloseTo(0.80, 2);
    expect(result.zone).toBe('YELLOW');
  });

  });

  // ---------------------------------------------------------------------------
  // Tile Chain Tests
  // ---------------------------------------------------------------------------

  describe('TileChain', () => {
    it('should build and execute a simple chain', async () => {
    const tile1 = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'chain-tile-1',
        confidence: 0.95,
        trace: 'Chain step 1',
        output: { result: 'processed' },
      }
    );

    const chain = TileChain.start(tile1);
    const result = await chain.execute({ value: 'input' });

    expect(result.output.result).toBe('processed');
    expect(result.confidence).toBe(0.95);
    expect(result.zone).toBe('GREEN');
    expect(result.steps.length).toBe(1);
  });

  it('should build multi-step chain with cascading confidence', async () => {
    const tile1 = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'multi-1',
        confidence: 0.95,
        trace: 'Step 1',
        output: { result: 'step1' },
      }
    );

    const tile2 = new TestTile<TestOutput, TestOutput>(
      Schemas.object({ result: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'multi-2',
        confidence: 0.90,
        trace: 'Step 2',
        output: { result: 'step2' },
      }
    );

    const tile3 = new TestTile<TestOutput, TestOutput>(
      Schemas.object({ result: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'multi-3',
        confidence: 0.85,
        trace: 'Step 3',
        output: { result: 'final' },
      }
    );

    const chain = TileChain.start(tile1)
      .add(tile2)
      .add(tile3);

    const result = await chain.execute({ value: 'test' });

    // Confidence: 0.95 * 0.90 * 0.85 = 0.726
    expect(result.confidence).toBeCloseTo(0.726, 3);
    expect(result.output.result).toBe('final');
    expect(result.steps.length).toBe(3);
  });

  it('should stop execution on RED zone', async () => {
    const tile1 = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'red-tile-1',
        confidence: 0.70, // Will produce RED zone
        trace: 'Failing tile',
        output: { result: 'partial' },
      }
    );

    const tile2 = new TestTile<TestOutput, TestOutput>(
      Schemas.object({ result: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'red-tile-2',
        confidence: 0.90,
        trace: 'Should not execute',
        output: { result: 'never' },
      }
    );

    const chain = TileChain.start(tile1).add(tile2);
    const result = await chain.execute({ value: 'test' });

    // Should stop at first tile due to RED zone
    expect(result.zone).toBe('RED');
    expect(result.output.result).toBe('partial');
    expect(result.steps.length).toBe(1); // Only first step executed
  });

  it('should handle branching logic', async () => {
    const trueTile = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'true-tile',
        confidence: 0.95,
        trace: 'True branch',
        output: { result: 'positive' },
      }
    );

    const falseTile = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'false-tile',
        confidence: 0.90,
        trace: 'False branch',
        output: { result: 'negative' },
      }
    );

    const chain = TileChain.start<TestInput, TestOutput>(
      new TestTile(
        Schemas.object({ value: Schemas.string }),
        Schemas.object({ result: Schemas.string }),
        {
          id: 'start',
          confidence: 1.0,
          trace: 'Start',
          output: { result: 'start' },
        }
      )
    ).branch(
      (input) => input.value === 'positive',
      trueTile,
      falseTile
    );

    // Test true branch
    const trueResult = await chain.execute({ value: 'positive' });
    expect(trueResult.output.result).toBe('positive');

    // Test false branch
    const falseResult = await chain.execute({ value: 'negative' });
    expect(falseResult.output.result).toBe('negative');
  });

  it('should generate trace for entire chain', async () => {
    const tile = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'trace-tile',
        confidence: 0.90,
        trace: 'Processing input',
        output: { result: 'done' },
      }
    );

    const chain = TileChain.start(tile);
    const result = await chain.execute({ value: 'test' });

    expect(result.trace.steps.length).toBe(1);
    expect(result.trace.steps[0].trace).toBe('Processing input');
    expect(result.trace.summary).toContain('0.90');
    expect(result.trace.summary).toContain('GREEN');
  });

  it('should visualize chain structure', () => {
    const tile = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'viz-tile',
        confidence: 0.90,
        trace: 'Test',
        output: { result: 'done' },
      }
    );

    const chain = TileChain.start(tile);
    const viz = chain.visualize();

    expect(viz).toContain('TileChain');
    expect(viz).toContain('viz-tile');
  });

  // ---------------------------------------------------------------------------
  // Registry Tests
  // ---------------------------------------------------------------------------

  describe('TileRegistry', () => {
    it('should register and retrieve tiles', () => {
    const tile = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'registered-tile',
        confidence: 0.90,
        trace: 'Test',
        output: { result: 'done' },
      }
    );

    const result = registry.register(tile);
    expect(result.valid).toBe(true);

    const retrieved = registry.get<TestInput, TestOutput>('registered-tile');
    expect(retrieved).toBeDefined();
    expect(retrieved.id).toBe('registered-tile');
  });

  it('should find tiles by type', () => {
    const tile1 = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'find-1',
        confidence: 0.90,
        trace: 'Test 1',
        output: { result: 'done' },
      }
    );

    const tile2 = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'find-2',
        confidence: 0.85,
        trace: 'Test 2',
        output: { result: 'done' },
      }
    );

    registry.register(tile1);
    registry.register(tile2);

    const found = registry.find({ type: 'TestTile' });
    expect(found.length).toBe(2);
  });

  it('should find chain between types', () => {
    // Create tiles that form a chain
    const tile1 = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'chain-start',
        confidence: 0.90,
        trace: 'Start',
        output: { result: 'step1' },
      }
    );

    const tile2 = new TestTile<TestOutput, TestOutput>(
      Schemas.object({ result: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'chain-end',
        confidence: 0.85,
        trace: 'End',
        output: { result: 'final' },
      }
    );

    registry.register(tile1);
    registry.register(tile2);

    const chain = registry.findChain('object', 'object');
    expect(chain).toBeDefined();
    expect(chain!.length).toBe(2);
  });

  it('should validate dependencies', () => {
    const tile = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'dep-tile',
        confidence: 0.90,
        trace: 'Test',
        output: { result: 'done' },
      }
    );

    const result = registry.register(tile, {
      dependencies: ['non-existent-tile'],
    });

    expect(result.valid).toBe(true); // Registration succeeds
    expect(result.warnings.some(w => w.code === 'MISSING_DEPENDENCY')).toBe(true);
  });

  it('should track statistics', () => {
    const tile = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'stats-tile',
        confidence: 0.90,
        trace: 'Test',
        output: { result: 'done' },
      }
    );

    registry.register(tile);

    const stats = registry.getStats();
    expect(stats.totalTiles).toBe(1);
    expect(stats.uniqueTypes).toBe(1);
  });

  // ---------------------------------------------------------------------------
  // Composition Validation Tests
  // ---------------------------------------------------------------------------

  describe('Composition Validation', () => {
    it('should validate simple chain', () => {
    const tile = new TestTile<TestInput, TestOutput>(
      Schemas.object({ value: Schemas.string }),
      Schemas.object({ result: Schemas.string }),
      {
        id: 'validate-tile',
        confidence: 0.90,
        trace: 'Test',
        output: { result: 'done' },
      }
    );

    const chain = TileChain.start(tile);
    const result = chain.validate();

    expect(result.valid).toBe(true);
    expect(result.errors.length).toBe(0);
  });

  it('should warn about long chains', () => {
    const tiles = Array(10).fill(null).map((_, i) =>
      new TestTile<TestInput, TestOutput>(
        Schemas.object({ value: Schemas.string }),
        Schemas.object({ result: Schemas.string }),
        {
          id: `long-tile-${i}`,
          confidence: 0.90,
          trace: `Tile ${i}`,
          output: { result: `step${i}` },
        }
      )
    );

    let chain = TileChain.start(tiles[0]);
    for (let i = 1; i < tiles.length; i++) {
      chain = chain.add(tiles[i]);
    }

    const result = chain.validate();
    expect(result.warnings.some(w => w.code === 'LONG_CHAIN')).toBe(true);
  });
  });
});

// ============================================================================
// RUN TESTS
// ============================================================================

// Run tests if in test environment
if (process.env.NODE_ENV === 'test') {
  console.log('Running Tile Integration Tests...');
}
