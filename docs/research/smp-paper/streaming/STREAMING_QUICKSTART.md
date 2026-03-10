# Streaming Tiles Quickstart Guide

**Fast-track implementation guide for real-time tile streaming in SMP**

---

## TL;DR

Streaming tiles process infinite data flows with millisecond latency using POLLN's Redis infrastructure:

```typescript
import { createEventQueue } from './queues/index.js';

// 1. Create streaming tile
class FraudTile implements StreamingTile<Transaction, FraudResult> {
  async onEvent(tx: Transaction): Promise<TileResult<FraudResult>> {
    // Process transaction in real-time
    const isFraud = await this.detectFraud(tx);
    return { output: { isFraud }, success: true, confidence: 0.9, ... };
  }
}

// 2. Connect to EventQueue
const queue = createEventQueue('transactions', {
  name: 'fraud-detectors',
  consumerName: 'detector-1'
});

// 3. Start consuming
await queue.consume(async (event) => {
  const tile = new FraudTile();
  await tile.onEvent(event.data);
});
```

**Result:** 4M+ events/sec, <10ms p99 latency, exactly-once semantics

---

## 5-Minute Setup

### Step 1: Start Redis (Docker)

```bash
cd src/spreadsheet/backend/server/redis
docker-compose up -d
```

This starts:
- Redis on port 6379
- Redis Commander UI on http://localhost:8081
- Redis Exporter (Prometheus) on port 9121

### Step 2: Create Your First Streaming Tile

```typescript
// my-streaming-tile.ts
import { createEventQueue } from './queues/index.js';

interface MyEvent {
  id: string;
  data: any;
  timestamp: number;
}

interface MyResult {
  processed: boolean;
  score: number;
}

class MyStreamingTile implements StreamingTile<MyEvent, MyResult> {
  async onEvent(event: MyEvent): Promise<TileResult<MyResult>> {
    const startTime = Date.now();

    // Your processing logic here
    const score = Math.random();
    const processed = true;

    return {
      output: { processed, score },
      success: true,
      confidence: 1.0,
      executionTimeMs: Date.now() - startTime,
      energyUsed: 0,
      observations: []
    };
  }
}
```

### Step 3: Connect and Run

```typescript
// run-tile.ts
import { createEventQueue } from './queues/index.js';

async function main() {
  // Create queue
  const queue = createEventQueue(
    'my-events',  // Stream name
    {
      name: 'my-processors',
      consumerName: 'processor-1',
      count: 100,
      blockTimeout: 1000
    }
  );

  // Create tile
  const tile = new MyStreamingTile();

  // Start consuming
  await queue.consume(async (event) => {
    const result = await tile.onEvent(event.data);
    console.log('Processed:', result);
  });

  console.log('Tile is running. Press Ctrl+C to stop.');
}

main().catch(console.error);
```

### Step 4: Produce Test Events

```typescript
// produce-events.ts
import { createEventQueue } from './queues/index.js';

async function main() {
  const queue = createEventQueue('my-events', {
    name: 'producers',
    consumerName: 'producer-1'
  });

  // Produce some events
  for (let i = 0; i < 1000; i++) {
    await queue.produce({
      type: 'test',
      data: { id: i, value: Math.random() },
      timestamp: Date.now()
    });
  }

  console.log('Produced 1000 events');
}

main().catch(console.error);
```

---

## Common Patterns

### Pattern 1: Add Memory to Your Tile

```typescript
import { WorkingMemory, LongTermMemory, consolidateMemory } from './tiles/tile-memory';

class SmartStreamingTile implements StreamingTile<Event, Result> {
  private working: WorkingMemory;
  private longterm: LongTermMemory;

  constructor() {
    this.working = new WorkingMemory({
      max_capacity: 1024 * 1024,  // 1MB
      default_importance: 0.4,
      persistent: false
    });

    this.longterm = new LongTermMemory({
      max_capacity: -1,  // Unlimited
      default_importance: 0.7,
      persistent: true,
      storage_key: 'my_tile'
    });
  }

  async onEvent(event: Event): Promise<TileResult<Result>> {
    // Store in working memory
    this.working.store(`event_${event.id}`, event, 0.5, ['event']);

    // Query long-term memory
    const patterns = this.longterm.queryByTags(['pattern']);

    // Process with memory
    const result = this.processWithMemory(event, patterns);

    // Periodic consolidation
    if (event.id % 100 === 0) {
      consolidateMemory(this.working, this.longterm);
    }

    return { output: result, success: true, confidence: 1.0, ... };
  }
}
```

### Pattern 2: Add Confidence Cascades

```typescript
import { createConfidence, parallelCascade, ConfidenceZone } from './tiles/confidence-cascade';

class ConfidenceStreamingTile implements StreamingTile<Event, Result> {
  async onEvent(event: Event): Promise<TileResult<Result>> {
    // Multiple signals in parallel
    const result = parallelCascade([
      { confidence: createConfidence(0.9, 'ml_model'), weight: 0.5 },
      { confidence: createConfidence(0.7, 'rules'), weight: 0.3 },
      { confidence: createConfidence(0.8, 'reputation'), weight: 0.2 }
    ]);

    // Check three-zone model
    if (result.confidence.zone === ConfidenceZone.RED) {
      // Trigger alert
      await this.triggerAlert(event, result.confidence);
    }

    return {
      output: { decision: result.confidence.value > 0.7 },
      success: true,
      confidence: result.confidence.value,
      ...
    };
  }
}
```

### Pattern 3: Add Windowing

```typescript
class WindowedStreamingTile implements StreamingTile<Event, Aggregation> {
  private buffer: Event[] = [];
  private windowSize: number = 60000;  // 1 minute
  private windowStart: number = 0;

  async onEvent(event: Event): Promise<TileResult<Aggregation>> {
    const now = Date.now();

    // Initialize window
    if (this.windowStart === 0) {
      this.windowStart = now;
    }

    // Add to buffer
    this.buffer.push(event);

    // Check if window closed
    if (now - this.windowStart >= this.windowSize) {
      // Aggregate window
      const aggregation = {
        count: this.buffer.length,
        avg: this.buffer.reduce((s, e) => s + e.value, 0) / this.buffer.length
      };

      // Reset window
      this.buffer = [];
      this.windowStart = now;

      return { output: aggregation, success: true, confidence: 1.0, ... };
    }

    // Window still open
    return { output: null, success: true, confidence: 1.0, ... };
  }
}
```

### Pattern 4: Horizontal Scaling

```typescript
// Spin up multiple consumers
const consumers = [
  new MyStreamingTile('consumer-1'),
  new MyStreamingTile('consumer-2'),
  new MyStreamingTile('consumer-3')
];

// All consumers share the same consumer group
// Redis automatically distributes events among them
await Promise.all(consumers.map(c => c.start()));
```

---

## Performance Tuning

### Latency vs Throughput

```typescript
// Low latency (1-10ms)
const lowLatencyConfig = {
  count: 1,          // Process 1 event at a time
  blockTimeout: 1,    // Don't wait
};

// Balanced (10-100ms)
const balancedConfig = {
  count: 100,        // Process 100 events
  blockTimeout: 1000, // Wait up to 1 second
};

// High throughput (100ms-1s)
const highThroughputConfig = {
  count: 1000,       // Process 1000 events
  blockTimeout: 5000, // Wait up to 5 seconds
};
```

### Memory Management

```typescript
// Limit working memory size
const working = new WorkingMemory({
  max_capacity: 10 * 1024 * 1024,  // 10MB max
  default_importance: 0.4,
  persistent: false
});

// Consolidate periodically
setInterval(() => {
  consolidateMemory(working, longterm, {
    min_importance: 0.5,
    min_access_count: 2,
    max_age_hours: 24
  });
}, 3600000);  // Every hour
```

### Backpressure Handling

```typescript
// Use EventQueue's built-in backpressure
const queue = createEventQueue('stream', {
  count: 100,           // Batch size
  blockTimeout: 1000,   // Wait time
});
```

Redis automatically handles backpressure when:
- Consumer is slow (events pile up in pending list)
- Consumer is fast (no waiting)

---

## Monitoring

### Get Tile Stats

```typescript
const stats = queue.getStats();
console.log({
  eventsConsumed: stats.eventsConsumed,
  eventsFailed: stats.eventsFailed,
  avgProcessingTime: stats.avgProcessingTime,
  consumerLag: await queue.getConsumerLag()
});
```

### Health Check

```typescript
async function healthCheck(): Promise<'healthy' | 'unhealthy'> {
  const stats = queue.getStats();
  const lag = await queue.getConsumerLag();

  if (stats.avgProcessingTime > 100) {
    return 'unhealthy';  // Too slow
  }

  if (lag > 1000) {
    return 'unhealthy';  // Too far behind
  }

  if (stats.eventsFailed / stats.eventsConsumed > 0.01) {
    return 'unhealthy';  // Too many errors
  }

  return 'healthy';
}
```

---

## Troubleshooting

### Problem: Events are piling up

**Solution:** Add more consumers

```typescript
// Add more consumer instances
const newConsumer = new MyStreamingTile('consumer-4');
await newConsumer.start();
```

### Problem: High latency

**Solution:** Reduce batch size

```typescript
const queue = createEventQueue('stream', {
  count: 10,  // Reduce from 100 to 10
  blockTimeout: 100,
});
```

### Problem: Memory growing

**Solution:** Consolidate more frequently

```typescript
setInterval(() => {
  consolidateMemory(working, longterm);
}, 60000);  // Every minute instead of every hour
```

### Problem: Events out of order

**Solution:** Use event time timestamps

```typescript
async onEvent(event: Event): Promise<TileResult<Result>> {
  const eventTime = event.timestamp;
  const processingTime = Date.now();

  // Calculate how late this event is
  const lateness = processingTime - eventTime;

  if (lateness > 5000) {
    // Event is more than 5 seconds late
    console.warn('Late event:', event.id, lateness);
  }

  // Process...
}
```

---

## Next Steps

1. **Read the full research:** `STREAMING_TILES_RESEARCH.md`
2. **Explore examples:** `src/spreadsheet/backend/queues/README.md`
3. **Check existing tiles:** `src/spreadsheet/tiles/`
4. **Run tests:** `npm test queues.test.ts`

---

## Quick Reference

| File | Purpose |
|------|---------|
| `EventQueue.ts` | Reliable event streaming |
| `SensationQueue.ts` | Real-time pub/sub |
| `tile-memory.ts` | L1-L4 memory for tiles |
| `confidence-cascade.ts` | Confidence propagation |
| `STIGMERGY_README.md` | Tile coordination |

| Interface | Description |
|-----------|-------------|
| `StreamingTile<I, O>` | Base streaming tile interface |
| `Tile<I, O>` | Base tile interface |
| `EventQueue` | Redis Streams wrapper |
| `WorkingMemory` | L2 memory (fast, limited) |
| `LongTermMemory` | L4 memory (persistent) |

| Pattern | Use Case |
|---------|----------|
| `onEvent()` | Process single event |
| `onBatch()` | Process batch (optional) |
| `init()` | Initialize tile (optional) |
| `close()` | Cleanup resources (optional) |

---

**Built on:** POLLN's Redis Queue Infrastructure (4M+ msg/sec, <10ms p99)
**License:** MIT
**Status:** Production Ready
