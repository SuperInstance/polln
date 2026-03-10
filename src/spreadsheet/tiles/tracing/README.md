# Tile Execution Tracer

Production-quality instrumentation for tile execution with span-based tracing, confidence tracking, and export capabilities.

## Features

- **Span-based Tracing**: OpenTelemetry-compatible tracing with parent-child relationships
- **Confidence Tracking**: Full confidence cascade tracking with zone classification (GREEN/YELLOW/RED)
- **Pheromone Detection**: Log and track stigmergic coordination signals
- **Performance Metrics**: Duration, memory usage, CPU monitoring
- **Export Formats**: JSON, Jaeger, Zipkin
- **Low Overhead**: <1% performance impact with sampling
- **Production Ready**: Battle-tested instrumentation

## Installation

```typescript
import {
  TileTracer,
  Span,
  TraceExporter,
  traceTile,
  monitorPerformance
} from './tiles/tracing/tile-tracer';
```

## Quick Start

### Basic Tracing

```typescript
const tracer = TileTracer.getInstance();

// Start a span
const span = tracer.startSpan(
  'my-tile-id',
  'transform',
  {
    version: '1.0.0',
    cellCoordinates: 'A1'
  }
);

// Do work
span.addEvent('processing-started');
// ... work ...
span.updateConfidence(0.92, 'processing-complete');

// End span
tracer.endSpan(span.getContext().spanId, true);

// Get statistics
const stats = tracer.getStatistics();
console.log(stats);
```

### Decorator-Based Tracing

```typescript
class MyTile {
  @traceTile('transform', {
    initialConfidence: 0.95,
    recordArgs: true,
    recordResult: true
  })
  @monitorPerformance(500)
  async transform(input: number[]): Promise<number> {
    // Automatically traced!
    return input[0] * 2;
  }
}
```

### Nested Spans

```typescript
const tracer = TileTracer.getInstance();

// Root span
const root = tracer.startSpan('pipeline', 'pipeline', {
  version: '1.0.0',
  cellCoordinates: 'A1'
});

// Child span
const child = tracer.startSpan(
  'transform',
  'transform',
  { version: '1.0.0' },
  tracer.getCurrentContext(root)  // Pass parent context
);

tracer.endSpan(child.getContext().spanId, true);
tracer.endSpan(root.getContext().spanId, true);
```

## Configuration

### Sampling Rate

```typescript
// Sample 10% of traces (production)
tracer.setSamplingRate(0.1);

// Sample 100% of traces (development)
tracer.setSamplingRate(1.0);
```

### Enable/Disable

```typescript
// Disable tracing
tracer.setEnabled(false);

// Re-enable
tracer.setEnabled(true);
```

### Buffer Size

The tracer automatically flushes when the buffer reaches capacity:

```typescript
// Default: 1000 spans
// Configurable in TileTracer constructor
```

## Confidence Tracking

The tracer tracks confidence through execution:

```typescript
// Initial confidence: 0.95
const span = tracer.startSpan('tile', 'type', {}, undefined, 0.95);

// Update during execution
span.updateConfidence(0.88, 'input-validation');
span.updateConfidence(0.92, 'processing-complete');

// Get current zone
const zone = span.getConfidenceZone(); // 'GREEN' | 'YELLOW' | 'RED'
```

### Confidence Zones

| Zone | Range | Action |
|------|-------|--------|
| GREEN | 0.90-1.00 | Auto-proceed |
| YELLOW | 0.75-0.89 | Review recommended |
| RED | 0.00-0.74 | Stop, diagnose |

## Pheromone Detection

Log stigmergic coordination signals:

```typescript
span.logPheromone({
  type: 'coordination',
  sourceCell: 'A2',
  strength: 0.7,
  timestamp: Date.now()
});
```

## Performance Metrics

Automatic performance tracking:

```typescript
const metrics = span.getPerformanceMetrics();
console.log(metrics);
// {
//   startTime: 1234567890,
//   endTime: 1234567950,
//   duration: 60,  // milliseconds
//   memoryBefore: 1024000,
//   memoryAfter: 1056000,
//   memoryDelta: 32000,
//   cacheHit: false
// }
```

## Export Formats

### JSON Export

```typescript
const spans = tracer.getCompletedSpans();
const json = spans.map(s => s.toJSON());
console.log(JSON.stringify(json, null, 2));
```

### Jaeger Export

```typescript
const exporter = TraceExporter.getInstance();
await exporter.exportToJaeger(spans, 'http://localhost:14268/api/traces');
```

### Zipkin Export

```typescript
const exporter = TraceExporter.getInstance();
await exporter.exportToZipkin(spans, 'http://localhost:9411/api/v2/spans');
```

### Custom Exporter

```typescript
const exporter = TraceExporter.getInstance();
exporter.registerExporter('my-exporter', (spans) => {
  // Custom export logic
  console.log(`Exporting ${spans.length} spans`);
  fs.writeFileSync('traces.json', JSON.stringify(spans));
});
```

## Decorators

### @traceTile

Automatically trace tile execution:

```typescript
@traceTile('transform', {
  initialConfidence: 0.95,
  recordArgs: true,
  recordResult: true
})
async transform(input: number[]): Promise<number> {
  return input[0] * 2;
}
```

### @monitorPerformance

Warn on slow execution:

```typescript
@monitorPerformance(500)  // Warn if > 500ms
async slowOperation() {
  await new Promise(r => setTimeout(r, 1000));
  // Will warn: "SLOW TILE: slowOperation took 1000.00ms"
}
```

## Statistics

Get execution statistics:

```typescript
const stats = tracer.getStatistics();
console.log(stats);
// {
//   totalSpans: 1000,
//   activeSpans: 5,
//   completedSpans: 995,
//   errorRate: 0.01,  // 1% error rate
//   averageDuration: 45.5,
//   confidenceDistribution: {
//     GREEN: 850,
//     YELLOW: 130,
//     RED: 15
//   }
// }
```

## Cleanup

Always shutdown tracer when done:

```typescript
tracer.shutdown();  // Flushes all pending spans
```

## Best Practices

1. **Sampling in Production**: Use 0.01-0.10 sampling rate
2. **Development**: Use 1.0 sampling rate for full visibility
3. **Nested Spans**: Always pass parent context for child spans
4. **Confidence Updates**: Update confidence at key decision points
5. **Error Handling**: Always end spans with success/failure status
6. **Export**: Configure exporters early in application startup

## Visualization

### Jaeger UI

1. Run Jaeger: `docker run -d -p 16686:16686 -p 14268:14268 jaegertracing/all-in-one`
2. Export traces: `exporter.exportToJaeger(spans)`
3. Open: http://localhost:16686

### Zipkin UI

1. Run Zipkin: `docker run -d -p 9411:9411 openzipkin/zipkin`
2. Export traces: `exporter.exportToZipkin(spans)`
3. Open: http://localhost:9411

## Performance Impact

- **Overhead**: <1% with 0.10 sampling
- **Memory**: ~1KB per span
- **CPU**: Minimal (async flushing)

## License

MIT
