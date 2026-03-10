/**
 * Tile Tracer Tests
 *
 * Comprehensive test suite for tile execution tracing
 */

import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import {
  TileTracer,
  Span,
  TraceExporter,
  traceTile,
  monitorPerformance,
  type TraceContext,
  type TileMetadata
} from './tile-tracer';

// ============================================================================
// Test Fixtures
// ============================================================================

class TestTile {
  @traceTile('test-transform', {
    initialConfidence: 0.95,
    recordArgs: true,
    recordResult: true
  })
  @monitorPerformance(100)
  async transform(input: number[]): Promise<{ result: number; confidence: number }> {
    await new Promise(resolve => setTimeout(resolve, 50));
    return {
      result: input[0] * 2,
      confidence: 0.92
    };
  }

  @traceTile('failing-tile', {
    initialConfidence: 0.90
  })
  async failingMethod(): Promise<void> {
    throw new Error('Intentional failure');
  }
}

// ============================================================================
// Span Tests
// ============================================================================

describe('Span', () => {
  let span: Span;
  let context: TraceContext;
  let metadata: TileMetadata;

  beforeEach(() => {
    context = {
      traceId: 'test-trace-123',
      spanId: 'test-span-456',
      baggage: new Map()
    };

    metadata = {
      tileId: 'test-tile',
      tileType: 'test-type',
      version: '1.0.0',
      inputHash: 'abc123',
      cellCoordinates: 'A1'
    };

    span = new Span(context, metadata, 0.95);
  });

  describe('Construction', () => {
    it('should create span with correct initial state', () => {
      expect(span.getContext().traceId).toBe('test-trace-123');
      expect(span.getContext().spanId).toBe('test-span-456');
      expect(span.getConfidenceMetrics().initial).toBe(0.95);
      expect(span.getConfidenceMetrics().current).toBe(0.95);
      expect(span.getConfidenceZone()).toBe('GREEN');
    });

    it('should initialize performance metrics', () => {
      const perf = span.getPerformanceMetrics();
      expect(perf.startTime).toBeGreaterThan(0);
      expect(perf.memoryBefore).toBeGreaterThanOrEqual(0);
      expect(perf.endTime).toBeUndefined();
      expect(perf.duration).toBeUndefined();
    });
  });

  describe('Confidence Tracking', () => {
    it('should update confidence value', () => {
      span.updateConfidence(0.85, 'processing');

      const metrics = span.getConfidenceMetrics();
      expect(metrics.current).toBe(0.85);
      expect(metrics.cascadeHistory).toHaveLength(2);
      expect(metrics.cascadeHistory[1].reason).toBe('processing');
    });

    it('should update confidence zone correctly', () => {
      expect(span.getConfidenceZone()).toBe('GREEN');

      span.updateConfidence(0.80, 'degraded');
      expect(span.getConfidenceZone()).toBe('YELLOW');

      span.updateConfidence(0.50, 'failed');
      expect(span.getConfidenceZone()).toBe('RED');
    });

    it('should maintain confidence history', () => {
      span.updateConfidence(0.90, 'step1');
      span.updateConfidence(0.85, 'step2');
      span.updateConfidence(0.80, 'step3');

      const history = span.getConfidenceMetrics().cascadeHistory;
      expect(history).toHaveLength(4); // initial + 3 updates
      expect(history[0].value).toBe(0.95);
      expect(history[3].value).toBe(0.80);
    });
  });

  describe('Pheromone Logging', () => {
    it('should log pheromone signals', () => {
      span.logPheromone({
        type: 'coordination',
        sourceCell: 'A2',
        strength: 0.7,
        timestamp: Date.now()
      });

      span.end(true);

      const json = span.toJSON();
      expect(json.pheromones).toHaveLength(1);
      expect(json.pheromones[0].type).toBe('coordination');
    });
  });

  describe('Attributes & Events', () => {
    it('should set attributes', () => {
      span.setAttribute('custom.attr', 'value');
      span.setAttribute('custom.number', 42);

      span.end(true);

      const json = span.toJSON();
      expect(json.attributes['custom.attr']).toBe('value');
      expect(json.attributes['custom.number']).toBe(42);
    });

    it('should add events', () => {
      span.addEvent('start');
      span.addEvent('middle', { key: 'value' });
      span.addEvent('end');

      span.end(true);

      const json = span.toJSON();
      expect(json.events).toHaveLength(3);
      expect(json.events[0].name).toBe('start');
      expect(json.events[1].attributes?.key).toBe('value');
    });
  });

  describe('Span Lifecycle', () => {
    it('should end successfully', () => {
      span.end(true);

      const perf = span.getPerformanceMetrics();
      expect(perf.endTime).toBeDefined();
      expect(perf.duration).toBeDefined();
      expect(perf.duration).toBeGreaterThan(0);
      expect(perf.memoryAfter).toBeDefined();
      expect(perf.memoryDelta).toBeDefined();
    });

    it('should end with error', () => {
      span.end(false, 'Test error');

      const json = span.toJSON();
      expect(json.status).toBe('ERROR');
      expect(json.errorMessage).toBe('Test error');
    });
  });

  describe('Export Formats', () => {
    it('should export to JSON', () => {
      span.updateConfidence(0.85, 'test');
      span.addEvent('test-event');
      span.end(true);

      const json = span.toJSON();

      expect(json.traceId).toBe('test-trace-123');
      expect(json.spanId).toBe('test-span-456');
      expect(json.metadata.tileId).toBe('test-tile');
      expect(json.confidence.current).toBe(0.85);
      expect(json.events).toHaveLength(1);
    });

    it('should export to Jaeger format', () => {
      span.updateConfidence(0.85, 'test');
      span.end(true);

      const jaeger = span.toJaeger();

      expect(jaeger.traceID).toBe('test-trace-123');
      expect(jaeger.spanID).toBe('test-span-456');
      expect(jaeger.operationName).toBe('test-type:test-tile');
      expect(jaeger.tags).toContainEqual({
        key: 'confidence.zone',
        value: 'YELLOW'
      });
      expect(jaeger.tags).toContainEqual({
        key: 'tile.type',
        value: 'test-type'
      });
    });

    it('should export to Zipkin format', () => {
      span.updateConfidence(0.85, 'test');
      span.end(true);

      const zipkin = span.toZipkin();

      expect(zipkin.traceId).toBe('test-trace-123');
      expect(zipkin.id).toBe('test-span-456');
      expect(zipkin.name).toBe('test-type:test-tile');
      expect(zipkin.tags['confidence.zone']).toBe('YELLOW');
      expect(zipkin.tags['tile.type']).toBe('test-type');
    });
  });
});

// ============================================================================
// TileTracer Tests
// ============================================================================

describe('TileTracer', () => {
  let tracer: TileTracer;

  beforeEach(() => {
    tracer = TileTracer.getInstance();
    tracer.clear();
    tracer.setSamplingRate(1.0);
    tracer.setEnabled(true);
  });

  afterEach(() => {
    tracer.shutdown();
  });

  describe('Singleton Pattern', () => {
    it('should return same instance', () => {
      const instance1 = TileTracer.getInstance();
      const instance2 = TileTracer.getInstance();
      expect(instance1).toBe(instance2);
    });
  });

  describe('Span Management', () => {
    it('should start and track spans', () => {
      const span = tracer.startSpan('test', 'test-type', {
        version: '1.0.0'
      });

      expect(span).toBeDefined();
      expect(tracer.getActiveSpans()).toHaveLength(1);
    });

    it('should end and complete spans', () => {
      const span = tracer.startSpan('test', 'test-type', {
        version: '1.0.0'
      });

      tracer.endSpan(span.getContext().spanId, true);

      expect(tracer.getActiveSpans()).toHaveLength(0);
      expect(tracer.getCompletedSpans()).toHaveLength(1);
    });

    it('should create parent-child relationships', () => {
      const parent = tracer.startSpan('parent', 'parent-type', {
        version: '1.0.0'
      });

      const child = tracer.startSpan(
        'child',
        'child-type',
        { version: '1.0.0' },
        tracer.getCurrentContext(parent)
      );

      expect(child.getContext().parentSpanId).toBe(parent.getContext().spanId);
      expect(child.getContext().traceId).toBe(parent.getContext().traceId);
    });
  });

  describe('Sampling', () => {
    it('should respect sampling rate', () => {
      tracer.setSamplingRate(0.0);

      const span = tracer.startSpan('test', 'test-type', { version: '1.0.0' });
      expect(span.getContext().spanId).toBe('noop');

      tracer.setSamplingRate(1.0);

      const span2 = tracer.startSpan('test2', 'test-type', { version: '1.0.0' });
      expect(span2.getContext().spanId).not.toBe('noop');
    });
  });

  describe('Enable/Disable', () => {
    it('should disable tracing', () => {
      tracer.setEnabled(false);

      const span = tracer.startSpan('test', 'test-type', { version: '1.0.0' });
      expect(span.getContext().spanId).toBe('noop');
    });
  });

  describe('Statistics', () => {
    it('should calculate accurate statistics', () => {
      // Create successful spans
      for (let i = 0; i < 8; i++) {
        const span = tracer.startSpan(`success-${i}`, 'test', { version: '1.0.0' }, undefined, 0.95);
        tracer.endSpan(span.getContext().spanId, true);
      }

      // Create failed spans
      for (let i = 0; i < 2; i++) {
        const span = tracer.startSpan(`error-${i}`, 'test', { version: '1.0.0' }, undefined, 0.50);
        tracer.endSpan(span.getContext().spanId, false, 'Test error');
      }

      const stats = tracer.getStatistics();

      expect(stats.totalSpans).toBe(10);
      expect(stats.completedSpans).toBe(10);
      expect(stats.errorRate).toBe(0.2);
      expect(stats.confidenceDistribution.GREEN).toBe(8);
      expect(stats.confidenceDistribution.RED).toBe(2);
    });
  });

  describe('Auto-flush', () => {
    it('should auto-flush when buffer is full', () => {
      const exporter = TraceExporter.getInstance();
      const exportSpy = jest.spyOn(exporter, 'export');

      // Create spans to fill buffer
      for (let i = 0; i < 1001; i++) {
        const span = tracer.startSpan(`test-${i}`, 'test', { version: '1.0.0' });
        tracer.endSpan(span.getContext().spanId, true);
      }

      // Should have called export at least once
      expect(exportSpy).toHaveBeenCalled();
    });
  });
});

// ============================================================================
// TraceExporter Tests
// ============================================================================

describe('TraceExporter', () => {
  let exporter: TraceExporter;
  let spans: Span[];

  beforeEach(() => {
    exporter = TraceExporter.getInstance();
    spans = [];

    // Create test spans
    for (let i = 0; i < 3; i++) {
      const span = new Span(
        {
          traceId: 'trace-123',
          spanId: `span-${i}`,
          baggage: new Map()
        },
        {
          tileId: `tile-${i}`,
          tileType: 'test',
          version: '1.0.0',
          inputHash: '',
          cellCoordinates: 'A1'
        },
        0.90
      );
      span.end(true);
      spans.push(span);
    }
  });

  it('should export to all registered exporters', () => {
    const mockExporter1 = jest.fn();
    const mockExporter2 = jest.fn();

    exporter.registerExporter('mock1', mockExporter1);
    exporter.registerExporter('mock2', mockExporter2);

    exporter.export(spans);

    expect(mockExporter1).toHaveBeenCalledWith(spans);
    expect(mockExporter2).toHaveBeenCalledWith(spans);
  });

  it('should unregister exporters', () => {
    const mockExporter = jest.fn();

    exporter.registerExporter('mock', mockExporter);
    exporter.unregisterExporter('mock');

    exporter.export(spans);

    expect(mockExporter).not.toHaveBeenCalled();
  });
});

// ============================================================================
// Decorator Tests
// ============================================================================

describe('Decorators', () => {
  describe('@traceTile', () => {
    it('should trace successful execution', async () => {
      const tile = new TestTile();
      const result = await tile.transform([5]);

      expect(result.result).toBe(10);
      expect(result.confidence).toBe(0.92);

      const tracer = TileTracer.getInstance();
      expect(tracer.getCompletedSpans().length).toBeGreaterThan(0);
    });

    it('should trace failed execution', async () => {
      const tile = new TestTile();

      await expect(tile.failingMethod()).rejects.toThrow('Intentional failure');

      const tracer = TileTracer.getInstance();
      const errorSpans = tracer.getCompletedSpans().filter(
        s => s['status'] === 'ERROR'
      );

      expect(errorSpans.length).toBeGreaterThan(0);
    });
  });

  describe('@monitorPerformance', () => {
    it('should warn on slow execution', async () => {
      const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();

      class SlowTile {
        @monitorPerformance(10)
        async slowMethod() {
          await new Promise(r => setTimeout(r, 50));
        }
      }

      const tile = new SlowTile();
      await tile.slowMethod();

      expect(consoleSpy).toHaveBeenCalled();
      expect(consoleSpy.mock.calls[0][0]).toContain('SLOW TILE');

      consoleSpy.mockRestore();
    });
  });
});

// ============================================================================
// Integration Tests
// ============================================================================

describe('Integration Tests', () => {
  let tracer: TileTracer;

  beforeEach(() => {
    tracer = TileTracer.getInstance();
    tracer.clear();
    tracer.setSamplingRate(1.0);
  });

  afterEach(() => {
    tracer.shutdown();
  });

  it('should trace complex nested execution', async () => {
    // Root span
    const root = tracer.startSpan('pipeline', 'pipeline', {
      version: '1.0.0',
      cellCoordinates: 'A1'
    });

    root.addEvent('pipeline-started');

    // Level 1 child
    const child1 = tracer.startSpan(
      'transform',
      'transform',
      { version: '1.0.0', cellCoordinates: 'A1' },
      tracer.getCurrentContext(root),
      0.95
    );

    child1.updateConfidence(0.88, 'processing');
    child1.logPheromone({
      type: 'coordination',
      sourceCell: 'A2',
      strength: 0.7,
      timestamp: Date.now()
    });

    // Level 2 child
    const child2 = tracer.startSpan(
      'validate',
      'validate',
      { version: '1.0.0', cellCoordinates: 'A1' },
      tracer.getCurrentContext(child1),
      0.92
    );

    child2.updateConfidence(0.85, 'validation-warning');
    tracer.endSpan(child2.getContext().spanId, true);

    tracer.endSpan(child1.getContext().spanId, true);
    tracer.endSpan(root.getContext().spanId, true);

    // Verify trace structure
    const completed = tracer.getCompletedSpans();
    expect(completed).toHaveLength(3);

    const stats = tracer.getStatistics();
    expect(stats.totalSpans).toBe(3);
    expect(stats.averageDuration).toBeGreaterThan(0);
  });

  it('should export to multiple formats', async () => {
    const span = tracer.startSpan('test', 'test', { version: '1.0.0' });
    span.end(true);

    const exporter = TraceExporter.getInstance();

    // Mock fetch for HTTP exporters
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        statusText: 'OK'
      } as Response)
    );

    await exporter.exportToJaeger(tracer.getCompletedSpans());
    await exporter.exportToZipkin(tracer.getCompletedSpans());

    expect(global.fetch).toHaveBeenCalledTimes(2);
  });
});
