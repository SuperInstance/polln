# Tile Execution Tracer - Architecture Diagram

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Tile Execution Tracer                           │
│                      (Production-Ready Instrumentation)                 │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                              TileTracer                                 │
│                            (Singleton Manager)                          │
├─────────────────────────────────────────────────────────────────────────┤
│  • Active Spans Map                                                     │
│  • Completed Spans Buffer                                               │
│  • Sampling Rate Control (0-100%)                                       │
│  • Auto-Flush Timer (30s default)                                       │
│  • Enable/Disable Toggle                                                │
└──────────────────────┬────────────────────────────┬─────────────────────┘
                       │                            │
                       ▼                            ▼
              ┌────────────────┐          ┌────────────────┐
              │   Start Span   │          │   End Span     │
              │                │          │                │
              │ • traceId      │          │ • success/fail │
              │ • spanId       │          │ • duration     │
              │ • parentSpanId │          │ • memory delta │
              │ • confidence   │          │ • flush        │
              └───────┬────────┘          └────────┬───────┘
                      │                            │
                      ▼                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                Span                                     │
│                         (Individual Trace)                              │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐               │
│  │   Context     │  │  Confidence   │  │ Performance   │               │
│  │               │  │               │  │               │               │
│  │ • traceId     │  │ • initial     │  │ • startTime   │               │
│  │ • spanId      │  │ • current     │  │ • endTime     │               │
│  │ • parentSpanId│  │ • zone        │  │ • duration    │               │
│  │ • baggage     │  │ • history     │  │ • memory      │               │
│  └───────────────┘  └───────────────┘  └───────────────┘               │
│                                                                           │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐               │
│  │ Pheromone Log │  │   Attributes  │  │    Events     │               │
│  │               │  │               │  │               │               │
│  │ • type        │  │ • key=value   │  │ • name        │               │
│  │ • sourceCell  │  │ • custom      │  │ • timestamp   │               │
│  │ • strength    │  │ • metadata    │  │ • attributes  │               │
│  └───────────────┘  └───────────────┘  └───────────────┘               │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────┐           │
│  │                    Children Spans                       │           │
│  │  (Nested spans with parent-child relationships)        │           │
│  └─────────────────────────────────────────────────────────┘           │
└───────────────────────────┬─────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            TraceExporter                                │
│                         (Multi-Format Export)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │   Console   │  │    File     │  │   Jaeger    │  │   Zipkin    │   │
│  │             │  │             │  │             │  │             │   │
│  │ • dev logs  │  │ • .traces/  │  │ • HTTP API  │  │ • HTTP API  │   │
│  │ • debugging │  │ • JSON      │  │ • localhost │  │ • localhost │   │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘   │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────┐           │
│  │              Custom Exporters (Extensible)             │           │
│  │  exporter.registerExporter('my-exporter', callback)    │           │
│  └─────────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        Visualization Tools                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐      │
│  │      Jaeger UI              │  │      Zipkin UI              │      │
│  │  http://localhost:16686     │  │  http://localhost:9411      │      │
│  │                             │  │                             │      │
│  │ • Trace timeline            │  │ • Trace timeline            │      │
│  │ • Span details              │  │ • Span details              │      │
│  │ • Service graph             │  │ • Service graph             │      │
│  │ • Search/filter             │  │ • Search/filter             │      │
│  └─────────────────────────────┘  └─────────────────────────────┘      │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Confidence Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Confidence Cascade Tracking                        │
└─────────────────────────────────────────────────────────────────────────┘

Initial: 0.98
    │
    ▼
┌─────────────────┐
│ Input Validation│
│                 │
│ ▼ 0.95          │  -3% (slight degradation)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Data Transform  │
│                 │
│ ▼ 0.88          │  -7% (processing complexity)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Aggregation     │
│                 │
│ ▼ 0.82          │  -6% (accumulated uncertainty)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Result Verify   │
│                 │
│ ▲ 0.90          │  +8% (verification passed!)
└─────────────────┘

ZONE CLASSIFICATION:
┌────────────────────────────────────────────────────────────────┐
│ GREEN (0.90-1.00):  Auto-proceed, no intervention              │
│ YELLOW (0.75-0.89): Review recommended, may need attention     │
│ RED (0.00-0.74):    Stop execution, diagnose required          │
└────────────────────────────────────────────────────────────────┘
```

## Span Lifecycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Span Lifecycle                             │
└─────────────────────────────────────────────────────────────────────────┘

START                  RUNNING                  COMPLETED/ERROR
  │                       │                          │
  ▼                       ▼                          ▼
┌─────────┐         ┌─────────┐              ┌─────────────┐
│ Created │────────▶│Active   │─────────────▶│   Ended     │
└─────────┘         └─────────┘              └─────────────┘
                           │                          │
                           │                          ├─ success: true
                           │                          │  errorMessage: undefined
                           │                          │
                           │                          └─ success: false
                           │                             errorMessage: "..."
                           │
                           ├─ updateConfidence()
                           ├─ logPheromone()
                           ├─ setAttribute()
                           ├─ addEvent()
                           └─ addChild()
```

## Decorator Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Decorator Stack                                 │
└─────────────────────────────────────────────────────────────────────────┘

@traceTile('transform', {
  initialConfidence: 0.95,
  recordArgs: true,
  recordResult: true
})
@monitorPerformance(500)
@trackConfidence('confidence')
async transform(input: number[]): Promise<number> {
  return input[0] * 2;
}

EXECUTION FLOW:
┌─────────────────────────────────────────────────────────────────┐
│ 1. @traceTile starts span                                       │
│    • Creates span with initial confidence                       │
│    • Records args if recordArgs: true                           │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. @monitorPerformance wraps execution                          │
│    • Measures start time                                        │
│    • Executes method                                            │
│    • Warns if duration > threshold                              │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. @trackConfidence monitors result                             │
│    • Extracts confidence from result                            │
│    • Updates span confidence                                    │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. @traceTile ends span                                         │
│    • Records result if recordResult: true                       │
│    • Marks span complete/failed                                 │
│    • Flushes if buffer full                                     │
└─────────────────────────────────────────────────────────────────┘
```

## Export Format Mappings

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Span → Export Format Mapping                      │
└─────────────────────────────────────────────────────────────────────────┘

INTERNAL SPAN FORMAT
├─ Context
│  ├─ traceId          ─┐
│  ├─ spanId           ─┼──▶ All formats
│  └─ parentSpanId     ─┘
├─ Metadata
│  ├─ tileId           ─┐
│  ├─ tileType         ─┼──▶ All formats (as tags)
│  └─ version          ─┘
├─ Confidence
│  ├─ current          ─┼──▶ All formats (as tags)
│  └─ zone             ─┘
├─ Performance
│  ├─ startTime        ─┼──▶ All formats
│  ├─ endTime          ─┘
│  └─ duration
└─ Events              ───▶ Jaeger (logs), Zipkin (annotations)

JAEGER FORMAT:
{
  traceID: "abc123",
  spanID: "def456",
  operationName: "transform:my-tile",
  startTime: 1234567890,
  duration: 1000,
  tags: [
    { key: "confidence.zone", value: "GREEN" },
    { key: "tile.type", value: "transform" }
  ],
  logs: [
    {
      timestamp: 1234567890000000,
      fields: [
        { key: "event", value: "processing-started" }
      ]
    }
  ]
}

ZIPKIN FORMAT:
{
  traceId: "abc123",
  id: "def456",
  name: "transform:my-tile",
  timestamp: 1234567890,
  duration: 1000,
  localEndpoint: { serviceName: "tile-spreadsheet" },
  tags: {
    "confidence.zone": "GREEN",
    "tile.type": "transform"
  }
}
```

## Performance Characteristics

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Performance Impact Analysis                       │
└─────────────────────────────────────────────────────────────────────────┘

SAMPLING RATE    OVERHEAD       MEMORY       TRACE COVERAGE
──────────────────────────────────────────────────────────────────────
0% (disabled)    0%            0 KB          0%
10%              0.1%          ~1 KB/span    10%
50%              0.5%          ~1 KB/span    50%
100%             <1%           ~1 KB/span    100%

BUFFER MANAGEMENT:
┌─────────────────────────────────────────────────────────┐
│ Buffer Size: 1000 spans (~1 MB)                         │
│ Auto-flush: Every 30 seconds                            │
│ Manual flush: tracer.flush()                            │
│ Shutdown flush: tracer.shutdown()                       │
└─────────────────────────────────────────────────────────┘

ASYNC OPERATIONS:
┌─────────────────────────────────────────────────────────┐
│ • Span creation: Synchronous (<1μs)                     │
│ • Confidence updates: Synchronous (<1μs)                │
│ • Performance tracking: Synchronous (<1μs)              │
│ • Export to Jaeger/Zipkin: Asynchronous                 │
│ • File export: Synchronous (Node.js)                    │
│ • Auto-flush: Asynchronous                              │
└─────────────────────────────────────────────────────────┘
```

## Integration Points

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Integration with SMP System                        │
└─────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │   TileTracer    │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌───────────────┐  ┌─────────────────┐  ┌───────────────┐
│ Confidence    │  │   Stigmergy     │  │   Tile        │
│ Cascade       │  │   System        │  │   Memory      │
│               │  │                 │  │               │
│ • updateConf  │  │ • logPheromone  │  │ • attachState │
│ • getZone     │  │ • detectSignals │  │ • getState    │
│ • getHistory  │  │ • propagate     │  │ • setState    │
└───────────────┘  └─────────────────┘  └───────────────┘

INTEGRATION EXAMPLES:

1. Confidence Cascade Integration:
   tile-tracer.ts → confidence-cascade.ts
   - Real-time confidence tracking
   - Zone-based decision making
   - Cascade history analysis

2. Stigmergy Integration:
   tile-tracer.ts → stigmergy.ts
   - Pheromone signal logging
   - Coordination tracking
   - Signal strength monitoring

3. Tile Memory Integration:
   tile-tracer.ts → tile-memory.ts
   - State snapshot capture
   - Memory delta tracking
   - Session persistence
```
