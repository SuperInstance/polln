# Tile Execution Tracer - Quick Start

## Installation

```bash
npm install @polln/tile-tracer
```

## Basic Usage

### 1. Import and Initialize

```typescript
import { TileTracer } from '@polln/tile-tracer';

const tracer = TileTracer.getInstance();
tracer.setSamplingRate(1.0); // 100% sampling for development
tracer.setEnabled(true);
```

### 2. Trace Tile Execution

```typescript
// Start a span
const span = tracer.startSpan(
  'my-tile-id',
  'transform',
  {
    version: '1.0.0',
    cellCoordinates: 'Sheet1!A1'
  }
);

// Do work
span.addEvent('processing-started');
// ... your tile logic ...
span.updateConfidence(0.92, 'processing-complete');

// End span
tracer.endSpan(span.getContext().spanId, true);
```

### 3. View Statistics

```typescript
const stats = tracer.getStatistics();
console.log(stats);
// {
//   totalSpans: 100,
//   activeSpans: 2,
//   completedSpans: 98,
//   errorRate: 0.02,
//   averageDuration: 45.5,
//   confidenceDistribution: { GREEN: 85, YELLOW: 12, RED: 3 }
// }
```

### 4. Export Traces

```typescript
import { TraceExporter } from '@polln/tile-tracer';

const exporter = TraceExporter.getInstance();

// Export to Jaeger
await exporter.exportToJaeger(tracer.getCompletedSpans());

// Export to Zipkin
await exporter.exportToZipkin(tracer.getCompletedSpans());

// Export to file (automatic)
exporter.export(tracer.getCompletedSpans());
```

## Decorator-Based Tracing

```typescript
import { traceTile, monitorPerformance } from '@polln/tile-tracer';

class MyTile {
  @traceTile('transform', {
    initialConfidence: 0.95,
    recordArgs: true,
    recordResult: true
  })
  @monitorPerformance(500)
  async transform(input: number[]): Promise<number> {
    return input[0] * 2;
  }
}
```

## Confidence Tracking

```typescript
// Initial confidence
const span = tracer.startSpan('tile', 'type', {}, undefined, 0.95);

// Update during execution
span.updateConfidence(0.88, 'input-validation');
span.updateConfidence(0.92, 'processing-complete');

// Check zone
const zone = span.getConfidenceZone(); // 'GREEN' | 'YELLOW' | 'RED'
```

## Configuration

### Production Settings

```typescript
tracer.setSamplingRate(0.1); // 10% sampling
tracer.setEnabled(true);
```

### Development Settings

```typescript
tracer.setSamplingRate(1.0); // 100% sampling
tracer.setEnabled(true);
```

### Disable Tracing

```typescript
tracer.setEnabled(false);
```

## Cleanup

```typescript
tracer.shutdown(); // Flush and cleanup
```

## Visualization

### Jaeger

```bash
docker run -d -p 16686:16686 -p 14268:14268 jaegertracing/all-in-one
```

Open: http://localhost:16686

### Zipkin

```bash
docker run -d -p 9411:9411 openzipkin/zipkin
```

Open: http://localhost:9411

## API Reference

### TileTracer

| Method | Description |
|--------|-------------|
| `getInstance()` | Get singleton instance |
| `startSpan()` | Start a new span |
| `endSpan()` | End a span |
| `getStatistics()` | Get execution statistics |
| `getCompletedSpans()` | Get completed spans |
| `setSamplingRate()` | Set sampling rate (0-1) |
| `setEnabled()` | Enable/disable tracing |
| `clear()` | Clear completed spans |
| `flush()` | Flush spans to exporters |
| `shutdown()` | Shutdown tracer |

### Span

| Method | Description |
|--------|-------------|
| `getContext()` | Get span context |
| `updateConfidence()` | Update confidence value |
| `getConfidenceZone()` | Get confidence zone |
| `logPheromone()` | Log pheromone signal |
| `setAttribute()` | Set span attribute |
| `addEvent()` | Add span event |
| `end()` | End the span |
| `getPerformanceMetrics()` | Get performance metrics |
| `toJSON()` | Export to JSON |
| `toJaeger()` | Export to Jaeger format |
| `toZipkin()` | Export to Zipkin format |

### TraceExporter

| Method | Description |
|--------|-------------|
| `getInstance()` | Get singleton instance |
| `export()` | Export to all registered exporters |
| `exportToJaeger()` | Export to Jaeger |
| `exportToZipkin()` | Export to Zipkin |
| `registerExporter()` | Register custom exporter |
| `unregisterExporter()` | Unregister exporter |

## Best Practices

1. **Use sampling in production** (0.01-0.10)
2. **Use full sampling in development** (1.0)
3. **Always end spans** with success/failure
4. **Update confidence** at key decision points
5. **Add events** for important milestones
6. **Export traces** regularly
7. **Shutdown tracer** when done

## Performance Impact

- **Overhead**: <1% with 0.10 sampling
- **Memory**: ~1KB per span
- **CPU**: Minimal (async flushing)

## License

MIT
