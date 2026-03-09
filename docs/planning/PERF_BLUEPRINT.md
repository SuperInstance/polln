# Performance Optimization Blueprint

**Version**: 1.0.0
**Created**: 2026-03-08
**Target Implementation Agent**: glm-4.7

This document provides implementation guides, code examples, edge case handling, and test scenarios for performance optimization in the POLLN system.

---

## Table of Contents

1. [Cache Implementation Guide](#1-cache-implementation-guide)
2. [Benchmark Implementation Guide](#2-benchmark-implementation-guide)
3. [Edge Cases and Solutions](#3-edge-cases-and-solutions)
4. [Test Scenarios](#4-test-scenarios)
5. [Performance Patterns](#5-performance-patterns)

---

## 1. Cache Implementation Guide

### 1.1 LRU Cache with TTL Support

```typescript
/**
 * High-performance LRU cache with TTL support
 *
 * Implementation notes for glm-4.7:
 * - Use Map for O(1) lookups
 * - Use doubly-linked list for O(1) LRU operations
 * - Track memory usage for capacity management
 * - Handle TTL expiration lazily on access
 */

interface LRUCacheEntry<V> {
  key: string;
  value: V;
  createdAt: number;
  ttl: number;
  size: number;
  prev: LRUCacheEntry<V> | null;
  next: LRUCacheEntry<V> | null;
}

export class LRUCacheWithTTL<V> {
  private cache: Map<string, LRUCacheEntry<V>> = new Map();
  private head: LRUCacheEntry<V> | null = null;
  private tail: LRUCacheEntry<V> | null = null;
  private currentMemory: number = 0;

  constructor(
    private maxEntries: number,
    private maxMemoryBytes: number,
    private defaultTTL: number
  ) {}

  /**
   * Get value from cache
   * Time complexity: O(1)
   */
  get(key: string): V | undefined {
    const entry = this.cache.get(key);

    if (!entry) {
      return undefined;
    }

    // Check TTL expiration
    if (this.isExpired(entry)) {
      this.deleteEntry(entry);
      return undefined;
    }

    // Move to front (most recently used)
    this.moveToFront(entry);

    return entry.value;
  }

  /**
   * Set value in cache
   * Time complexity: O(1) amortized (may trigger eviction)
   */
  set(key: string, value: V, ttl?: number): void {
    // Calculate size
    const size = this.estimateSize(value);

    // Check if single entry exceeds max memory
    if (size > this.maxMemoryBytes) {
      throw new Error('Value exceeds maximum cache memory');
    }

    // Evict if necessary
    while (
      this.cache.size >= this.maxEntries ||
      this.currentMemory + size > this.maxMemoryBytes
    ) {
      this.evictLRU();
    }

    // Remove existing entry if present
    const existing = this.cache.get(key);
    if (existing) {
      this.deleteEntry(existing);
    }

    // Create new entry
    const entry: LRUCacheEntry<V> = {
      key,
      value,
      createdAt: Date.now(),
      ttl: ttl ?? this.defaultTTL,
      size,
      prev: null,
      next: null,
    };

    // Add to cache and list
    this.cache.set(key, entry);
    this.addToFront(entry);
    this.currentMemory += size;
  }

  /**
   * Delete entry from cache
   * Time complexity: O(1)
   */
  delete(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) {
      return false;
    }

    this.deleteEntry(entry);
    return true;
  }

  /**
   * Check if entry is expired
   */
  private isExpired(entry: LRUCacheEntry<V>): boolean {
    if (entry.ttl === 0) return false; // No expiration
    return Date.now() > entry.createdAt + entry.ttl;
  }

  /**
   * Move entry to front of LRU list
   */
  private moveToFront(entry: LRUCacheEntry<V>): void {
    if (entry === this.head) return;

    // Remove from current position
    this.removeFromList(entry);

    // Add to front
    this.addToFront(entry);
  }

  /**
   * Add entry to front of list
   */
  private addToFront(entry: LRUCacheEntry<V>): void {
    entry.prev = null;
    entry.next = this.head;

    if (this.head) {
      this.head.prev = entry;
    }

    this.head = entry;

    if (!this.tail) {
      this.tail = entry;
    }
  }

  /**
   * Remove entry from list
   */
  private removeFromList(entry: LRUCacheEntry<V>): void {
    if (entry.prev) {
      entry.prev.next = entry.next;
    } else {
      this.head = entry.next;
    }

    if (entry.next) {
      entry.next.prev = entry.prev;
    } else {
      this.tail = entry.prev;
    }
  }

  /**
   * Delete entry from cache and list
   */
  private deleteEntry(entry: LRUCacheEntry<V>): void {
    this.removeFromList(entry);
    this.cache.delete(entry.key);
    this.currentMemory -= entry.size;
  }

  /**
   * Evict least recently used entry
   */
  private evictLRU(): void {
    if (!this.tail) return;

    // Try to evict expired entries first
    let current: LRUCacheEntry<V> | null = this.tail;
    while (current) {
      if (this.isExpired(current)) {
        this.deleteEntry(current);
        return;
      }
      current = current.prev;
    }

    // Fall back to evicting LRU
    this.deleteEntry(this.tail);
  }

  /**
   * Estimate size of value in bytes
   */
  private estimateSize(value: V): number {
    if (value === null || value === undefined) return 0;

    if (typeof value === 'string') {
      return value.length * 2; // UTF-16
    }

    if (value instanceof ArrayBuffer) {
      return value.byteLength;
    }

    if (ArrayBuffer.isView(value)) {
      return value.byteLength;
    }

    // Rough estimate for objects
    try {
      return JSON.stringify(value).length * 2;
    } catch {
      return 1024; // Default estimate
    }
  }

  /**
   * Get cache statistics
   */
  getStats() {
    let expired = 0;
    for (const entry of this.cache.values()) {
      if (this.isExpired(entry)) expired++;
    }

    return {
      entries: this.cache.size,
      memoryBytes: this.currentMemory,
      maxEntries: this.maxEntries,
      maxMemoryBytes: this.maxMemoryBytes,
      expiredEntries: expired,
    };
  }

  /**
   * Clear all entries
   */
  clear(): void {
    this.cache.clear();
    this.head = null;
    this.tail = null;
    this.currentMemory = 0;
  }
}
```

### 1.2 Hybrid Eviction Cache

```typescript
/**
 * Hybrid eviction cache combining LRU, LFU, and quality scores
 *
 * Score = lruWeight * recencyScore +
 *         lfuWeight * frequencyScore +
 *         qualityWeight * qualityScore
 *
 * Lowest score gets evicted.
 */

interface HybridCacheEntry<V> extends LRUCacheEntry<V> {
  accessCount: number;
  qualityScore: number;
  lastAccessedAt: number;
}

export class HybridEvictionCache<V> {
  private cache: Map<string, HybridCacheEntry<V>> = new Map();
  private entries: HybridCacheEntry<V>[] = []; // For eviction scanning

  constructor(
    private config: {
      maxEntries: number;
      maxMemoryBytes: number;
      lruWeight: number;
      lfuWeight: number;
      qualityWeight: number;
      evictionBatchSize: number;
      evictionThreshold: number;
    }
  ) {}

  get(key: string): V | undefined {
    const entry = this.cache.get(key);
    if (!entry) return undefined;

    if (this.isExpired(entry)) {
      this.delete(key);
      return undefined;
    }

    // Update access metrics
    entry.accessCount++;
    entry.lastAccessedAt = Date.now();

    return entry.value;
  }

  set(key: string, value: V, qualityScore: number = 0.5, ttl?: number): void {
    // Check if eviction needed
    const threshold = this.config.maxEntries * this.config.evictionThreshold;
    if (this.cache.size >= threshold) {
      this.evict(this.config.evictionBatchSize);
    }

    // Remove existing
    if (this.cache.has(key)) {
      this.delete(key);
    }

    // Create entry
    const entry: HybridCacheEntry<V> = {
      key,
      value,
      createdAt: Date.now(),
      ttl: ttl ?? 3600000,
      size: this.estimateSize(value),
      accessCount: 0,
      qualityScore,
      lastAccessedAt: Date.now(),
      prev: null,
      next: null,
    };

    this.cache.set(key, entry);
    this.entries.push(entry);
  }

  /**
   * Evict entries with lowest hybrid scores
   */
  private evict(count: number): void {
    if (this.entries.length === 0) return;

    // Calculate scores and sort
    const scored = this.entries.map(entry => ({
      entry,
      score: this.calculateScore(entry),
    }));

    scored.sort((a, b) => a.score - b.score);

    // Evict lowest scoring entries
    const toEvict = scored.slice(0, count);
    for (const { entry } of toEvict) {
      this.cache.delete(entry.key);
    }

    // Update entries array
    const evictedKeys = new Set(toEvict.map(e => e.entry.key));
    this.entries = this.entries.filter(e => !evictedKeys.has(e.key));
  }

  /**
   * Calculate hybrid eviction score (lower = more likely to evict)
   */
  private calculateScore(entry: HybridCacheEntry<V>): number {
    const { lruWeight, lfuWeight, qualityWeight } = this.config;

    // Recency score: 0-1, higher for more recent access
    const age = Date.now() - entry.lastAccessedAt;
    const maxAge = 3600000; // 1 hour
    const recencyScore = Math.max(0, 1 - age / maxAge);

    // Frequency score: 0-1, higher for more accesses
    const maxAccess = 100;
    const frequencyScore = Math.min(1, entry.accessCount / maxAccess);

    // Quality score: 0-1
    const qualityScore = entry.qualityScore;

    return (
      lruWeight * recencyScore +
      lfuWeight * frequencyScore +
      qualityWeight * qualityScore
    );
  }

  private isExpired(entry: HybridCacheEntry<V>): boolean {
    return Date.now() > entry.createdAt + entry.ttl;
  }

  private estimateSize(value: V): number {
    // Same as LRUCacheWithTTL
    if (typeof value === 'string') return value.length * 2;
    if (value instanceof ArrayBuffer) return value.byteLength;
    if (ArrayBuffer.isView(value)) return value.byteLength;
    try {
      return JSON.stringify(value).length * 2;
    } catch {
      return 1024;
    }
  }

  delete(key: string): boolean {
    const entry = this.cache.get(key);
    if (!entry) return false;

    this.cache.delete(key);
    this.entries = this.entries.filter(e => e.key !== key);
    return true;
  }

  clear(): void {
    this.cache.clear();
    this.entries = [];
  }

  getStats() {
    return {
      entries: this.cache.size,
      avgAccessCount: this.entries.reduce((sum, e) => sum + e.accessCount, 0) / this.entries.length || 0,
      avgQualityScore: this.entries.reduce((sum, e) => sum + e.qualityScore, 0) / this.entries.length || 0,
    };
  }
}
```

### 1.3 Cache Invalidation Manager

```typescript
/**
 * Cache invalidation manager with dependency tracking
 *
 * Handles:
 * - Explicit invalidation
 * - Dependency-based cascading invalidation
 * - Pattern-based invalidation
 * - Version-based invalidation
 */

export class CacheInvalidationManager {
  private dependencies: Map<string, Set<string>> = new Map();
  private dependents: Map<string, Set<string>> = new Map();
  private versions: Map<string, number> = new Map();
  private rules: Map<string, InvalidationRule> = new Map();

  constructor(
    private storage: {
      delete: (key: string) => Promise<boolean>;
      get: (key: string) => Promise<unknown>;
    }
  ) {}

  /**
   * Register a dependency relationship
   */
  addDependency(key: string, dependsOn: string): void {
    if (!this.dependencies.has(key)) {
      this.dependencies.set(key, new Set());
    }
    this.dependencies.get(key)!.add(dependsOn);

    if (!this.dependents.has(dependsOn)) {
      this.dependents.set(dependsOn, new Set());
    }
    this.dependents.get(dependsOn)!.add(key);
  }

  /**
   * Add invalidation rule
   */
  addRule(rule: InvalidationRule): void {
    this.rules.set(rule.id, rule);
  }

  /**
   * Invalidate a key and optionally cascade to dependents
   */
  async invalidate(
    key: string,
    cascade: boolean = true,
    maxDepth: number = 10
  ): Promise<string[]> {
    const invalidated: string[] = [];

    await this.invalidateRecursive(key, invalidated, cascade, maxDepth, 0);

    return invalidated;
  }

  private async invalidateRecursive(
    key: string,
    invalidated: string[],
    cascade: boolean,
    maxDepth: number,
    currentDepth: number
  ): Promise<void> {
    if (invalidated.includes(key)) return;
    if (currentDepth > maxDepth) return;

    // Delete from storage
    await this.storage.delete(key);
    invalidated.push(key);

    // Cascade to dependents
    if (cascade) {
      const dependents = this.dependents.get(key);
      if (dependents) {
        for (const dependent of dependents) {
          await this.invalidateRecursive(
            dependent,
            invalidated,
            cascade,
            maxDepth,
            currentDepth + 1
          );
        }
      }
    }

    // Clean up tracking
    this.dependencies.delete(key);
    this.dependents.delete(key);
    this.versions.delete(key);
  }

  /**
   * Invalidate keys matching pattern
   */
  async invalidatePattern(pattern: string | RegExp): Promise<string[]> {
    const invalidated: string[] = [];
    const regex = typeof pattern === 'string' ? new RegExp(pattern) : pattern;

    // Get all keys that match pattern
    // Note: In production, this would query the storage layer
    for (const key of this.dependencies.keys()) {
      if (regex.test(key)) {
        const result = await this.invalidate(key);
        invalidated.push(...result);
      }
    }

    return invalidated;
  }

  /**
   * Check version and invalidate if mismatch
   */
  async checkVersion(key: string, expectedVersion: number): Promise<boolean> {
    const currentVersion = this.versions.get(key) ?? 0;

    if (currentVersion !== expectedVersion) {
      await this.invalidate(key);
      return false;
    }

    return true;
  }

  /**
   * Update version for a key
   */
  updateVersion(key: string, version: number): void {
    this.versions.set(key, version);
  }

  /**
   * Get dependency graph stats
   */
  getStats() {
    let totalDependencies = 0;
    for (const deps of this.dependencies.values()) {
      totalDependencies += deps.size;
    }

    return {
      keys: this.dependencies.size,
      totalDependencies,
      avgDependenciesPerKey: totalDependencies / (this.dependencies.size || 1),
      rules: this.rules.size,
    };
  }
}
```

---

## 2. Benchmark Implementation Guide

### 2.1 Benchmark Framework

```typescript
/**
 * Production-ready benchmark framework
 *
 * Usage:
 * ```typescript
 * const benchmark = new PerformanceBenchmark({
 *   name: 'cache-lookup',
 *   iterations: 1000,
 *   warmup: 100,
 * });
 *
 * benchmark.run(async () => {
 *   await cache.get('test-key');
 * });
 *
 * console.log(benchmark.getResults());
 * ```
 */

export class PerformanceBenchmark {
  private measurements: number[] = [];
  private startTime: number = 0;
  private warmupComplete: boolean = false;

  constructor(
    private config: {
      name: string;
      iterations: number;
      warmup: number;
      timeout?: number;
    }
  ) {}

  /**
   * Run benchmark with automatic warmup
   */
  async run(operation: () => Promise<void>): Promise<BenchmarkResult> {
    const { iterations, warmup, name, timeout } = this.config;

    // Warmup phase
    for (let i = 0; i < warmup; i++) {
      await operation();
    }

    this.warmupComplete = true;
    this.measurements = [];

    // Measurement phase
    const benchmarkStart = performance.now();

    for (let i = 0; i < iterations; i++) {
      const iterStart = performance.now();

      if (timeout) {
        await Promise.race([
          operation(),
          this.timeoutPromise(timeout),
        ]);
      } else {
        await operation();
      }

      const iterEnd = performance.now();
      this.measurements.push(iterEnd - iterStart);
    }

    const benchmarkEnd = performance.now();

    return {
      name,
      iterations,
      totalDuration: benchmarkEnd - benchmarkStart,
      metrics: this.calculateMetrics(),
    };
  }

  /**
   * Run benchmark with concurrent operations
   */
  async runConcurrent(
    operation: () => Promise<void>,
    concurrency: number
  ): Promise<BenchmarkResult> {
    const { iterations, warmup, name } = this.config;

    // Warmup
    const warmupPromises = Array(Math.min(warmup, concurrency))
      .fill(null)
      .map(() => operation());
    await Promise.all(warmupPromises);

    this.warmupComplete = true;
    this.measurements = [];

    // Run concurrent batches
    const benchmarkStart = performance.now();
    let completed = 0;

    while (completed < iterations) {
      const batchSize = Math.min(concurrency, iterations - completed);
      const batchStart = performance.now();

      const batch = Array(batchSize)
        .fill(null)
        .map(async () => {
          const opStart = performance.now();
          await operation();
          return performance.now() - opStart;
        });

      const batchResults = await Promise.all(batch);
      this.measurements.push(...batchResults);
      completed += batchSize;
    }

    const benchmarkEnd = performance.now();

    return {
      name,
      iterations,
      totalDuration: benchmarkEnd - benchmarkStart,
      metrics: this.calculateMetrics(),
      concurrency,
    };
  }

  /**
   * Calculate statistical metrics
   */
  private calculateMetrics(): BenchmarkMetrics {
    const sorted = [...this.measurements].sort((a, b) => a - b);
    const n = sorted.length;

    const sum = sorted.reduce((a, b) => a + b, 0);
    const mean = sum / n;

    const variance =
      sorted.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / n;
    const stdDev = Math.sqrt(variance);

    return {
      min: sorted[0],
      max: sorted[n - 1],
      mean,
      median: sorted[Math.floor(n / 2)],
      p50: sorted[Math.floor(n * 0.5)],
      p90: sorted[Math.floor(n * 0.9)],
      p95: sorted[Math.floor(n * 0.95)],
      p99: sorted[Math.floor(n * 0.99)],
      stdDev,
      samples: n,
      opsPerSecond: 1000 / mean,
    };
  }

  private timeoutPromise(ms: number): Promise<never> {
    return new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Benchmark timeout')), ms);
    });
  }
}

interface BenchmarkResult {
  name: string;
  iterations: number;
  totalDuration: number;
  metrics: BenchmarkMetrics;
  concurrency?: number;
}

interface BenchmarkMetrics {
  min: number;
  max: number;
  mean: number;
  median: number;
  p50: number;
  p90: number;
  p95: number;
  p99: number;
  stdDev: number;
  samples: number;
  opsPerSecond: number;
}
```

### 2.2 Regression Detection

```typescript
/**
 * Performance regression detector
 *
 * Compares current metrics against baseline and detects regressions.
 */

export class RegressionDetector {
  constructor(
    private baselines: Map<string, BenchmarkMetrics>,
    private thresholds: {
      maxLatencyRegression: number; // e.g., 0.05 = 5% slower is a regression
      maxThroughputRegression: number;
      minOpsPerSecond: number;
    }
  ) {}

  /**
   * Check for regressions
   */
  detect(name: string, current: BenchmarkMetrics): RegressionResult {
    const baseline = this.baselines.get(name);

    const result: RegressionResult = {
      name,
      hasRegression: false,
      regressions: [],
      improvements: [],
    };

    if (!baseline) {
      result.status = 'no-baseline';
      return result;
    }

    // Check latency regression (higher is worse)
    const latencyDelta = (current.p99 - baseline.p99) / baseline.p99;
    if (latencyDelta > this.thresholds.maxLatencyRegression) {
      result.hasRegression = true;
      result.regressions.push({
        metric: 'p99_latency',
        baseline: baseline.p99,
        current: current.p99,
        delta: latencyDelta,
        threshold: this.thresholds.maxLatencyRegression,
      });
    } else if (latencyDelta < -this.thresholds.maxLatencyRegression) {
      result.improvements.push({
        metric: 'p99_latency',
        baseline: baseline.p99,
        current: current.p99,
        delta: Math.abs(latencyDelta),
      });
    }

    // Check throughput regression (lower is worse)
    const throughputDelta =
      (baseline.opsPerSecond - current.opsPerSecond) / baseline.opsPerSecond;
    if (throughputDelta > this.thresholds.maxThroughputRegression) {
      result.hasRegression = true;
      result.regressions.push({
        metric: 'ops_per_second',
        baseline: baseline.opsPerSecond,
        current: current.opsPerSecond,
        delta: throughputDelta,
        threshold: this.thresholds.maxThroughputRegression,
      });
    } else if (throughputDelta < -this.thresholds.maxThroughputRegression) {
      result.improvements.push({
        metric: 'ops_per_second',
        baseline: baseline.opsPerSecond,
        current: current.opsPerSecond,
        delta: Math.abs(throughputDelta),
      });
    }

    // Check minimum throughput
    if (current.opsPerSecond < this.thresholds.minOpsPerSecond) {
      result.hasRegression = true;
      result.regressions.push({
        metric: 'min_throughput',
        baseline: this.thresholds.minOpsPerSecond,
        current: current.opsPerSecond,
        delta: 1 - current.opsPerSecond / this.thresholds.minOpsPerSecond,
        threshold: 0,
      });
    }

    result.status = result.hasRegression ? 'failed' : 'passed';

    return result;
  }

  /**
   * Update baseline
   */
  updateBaseline(name: string, metrics: BenchmarkMetrics): void {
    this.baselines.set(name, metrics);
  }

  /**
   * Save baselines to JSON
   */
  serializeBaselines(): string {
    return JSON.stringify(Object.fromEntries(this.baselines));
  }

  /**
   * Load baselines from JSON
   */
  static deserializeBaselines(json: string): Map<string, BenchmarkMetrics> {
    const obj = JSON.parse(json);
    return new Map(Object.entries(obj));
  }
}

interface RegressionResult {
  name: string;
  hasRegression: boolean;
  status: 'passed' | 'failed' | 'no-baseline';
  regressions: RegressionInfo[];
  improvements: ImprovementInfo[];
}

interface RegressionInfo {
  metric: string;
  baseline: number;
  current: number;
  delta: number;
  threshold: number;
}

interface ImprovementInfo {
  metric: string;
  baseline: number;
  current: number;
  delta: number;
}
```

---

## 3. Edge Cases and Solutions

### 3.1 Cache Invalidation Races

**Problem**: Multiple concurrent requests try to invalidate and repopulate the same cache entry, causing thundering herd.

```typescript
/**
 * Solution: Single-flight pattern for cache repopulation
 *
 * Ensures only one request repopulates the cache while others wait.
 */

export class SingleFlightCache<V> {
  private inflight: Map<string, Promise<V>> = new Map();
  private cache: Map<string, { value: V; expiresAt: number }> = new Map();

  constructor(
    private loader: (key: string) => Promise<V>,
    private ttl: number
  ) {}

  async get(key: string): Promise<V> {
    // Check cache
    const cached = this.cache.get(key);
    if (cached && Date.now() < cached.expiresAt) {
      return cached.value;
    }

    // Check if already loading
    const inflight = this.inflight.get(key);
    if (inflight) {
      return inflight;
    }

    // Start loading
    const loadPromise = this.load(key);
    this.inflight.set(key, loadPromise);

    try {
      const value = await loadPromise;
      return value;
    } finally {
      this.inflight.delete(key);
    }
  }

  private async load(key: string): Promise<V> {
    const value = await this.loader(key);

    this.cache.set(key, {
      value,
      expiresAt: Date.now() + this.ttl,
    });

    return value;
  }

  /**
   * Invalidate with debounce to prevent rapid re-invalidations
   */
  async invalidateDebounced(key: string, delay: number): Promise<void> {
    // Wait for any inflight requests to complete
    const inflight = this.inflight.get(key);
    if (inflight) {
      await inflight.catch(() => {}); // Ignore errors
    }

    // Wait delay before invalidating
    await new Promise(resolve => setTimeout(resolve, delay));

    this.cache.delete(key);
  }
}
```

### 3.2 Memory Pressure Handling

**Problem**: System runs low on memory, need to gracefully degrade cache.

```typescript
/**
 * Solution: Memory pressure aware cache
 *
 * Monitors memory usage and proactively evicts when pressure is high.
 */

export class MemoryPressureCache<V> {
  private cache: Map<string, CacheEntry<V>> = new Map();
  private memoryUsage: number = 0;
  private pressureLevel: 'low' | 'medium' | 'high' = 'low';

  constructor(
    private config: {
      maxMemory: number;
      lowPressureThreshold: number; // e.g., 0.6 = 60%
      highPressureThreshold: number; // e.g., 0.85 = 85%
      criticalThreshold: number; // e.g., 0.95 = 95%
    },
    private getSystemMemory: () => { used: number; total: number }
  ) {
    this.startMonitoring();
  }

  private startMonitoring(): void {
    // Monitor every second
    setInterval(() => {
      this.checkMemoryPressure();
    }, 1000);
  }

  private checkMemoryPressure(): void {
    const { used, total } = this.getSystemMemory();
    const ratio = used / total;

    const previousLevel = this.pressureLevel;

    if (ratio >= this.config.criticalThreshold) {
      this.pressureLevel = 'high';
      this.emergencyEviction(0.5); // Evict 50% of cache
    } else if (ratio >= this.config.highPressureThreshold) {
      this.pressureLevel = 'high';
      this.proactiveEviction(0.2); // Evict 20% of cache
    } else if (ratio >= this.config.lowPressureThreshold) {
      this.pressureLevel = 'medium';
    } else {
      this.pressureLevel = 'low';
    }

    if (previousLevel !== this.pressureLevel) {
      console.log(`Memory pressure changed: ${previousLevel} -> ${this.pressureLevel}`);
    }
  }

  /**
   * Proactive eviction based on LRU
   */
  private proactiveEviction(ratio: number): void {
    const toEvict = Math.floor(this.cache.size * ratio);
    const entries = [...this.cache.entries()]
      .sort((a, b) => a[1].lastAccessed - b[1].lastAccessed);

    for (let i = 0; i < toEvict && i < entries.length; i++) {
      const [key, entry] = entries[i];
      this.cache.delete(key);
      this.memoryUsage -= entry.size;
    }
  }

  /**
   * Emergency eviction during critical memory pressure
   */
  private emergencyEviction(ratio: number): void {
    // More aggressive: also evict recently accessed
    const toEvict = Math.floor(this.cache.size * ratio);
    const entries = [...this.cache.entries()]
      .filter(([_, e]) => e.qualityScore < 0.8) // Keep high-quality entries
      .sort((a, b) => a[1].qualityScore - b[1].qualityScore);

    for (let i = 0; i < toEvict && i < entries.length; i++) {
      const [key, entry] = entries[i];
      this.cache.delete(key);
      this.memoryUsage -= entry.size;
    }

    // Force GC if available
    if (global.gc) {
      global.gc();
    }
  }

  /**
   * Adaptive TTL based on memory pressure
   */
  getAdaptiveTTL(baseTTL: number): number {
    switch (this.pressureLevel) {
      case 'high':
        return baseTTL * 0.25; // Shorter TTL when memory is tight
      case 'medium':
        return baseTTL * 0.5;
      case 'low':
      default:
        return baseTTL;
    }
  }
}

interface CacheEntry<V> {
  value: V;
  size: number;
  lastAccessed: number;
  qualityScore: number;
}
```

### 3.3 Concurrent Write Conflicts

**Problem**: Multiple writers trying to update the same cache entry simultaneously.

```typescript
/**
 * Solution: Optimistic locking with version tracking
 */

export class OptimisticLockingCache<V> {
  private cache: Map<string, { value: V; version: number }> = new Map();

  /**
   * Read with version
   */
  read(key: string): { value: V; version: number } | null {
    const entry = this.cache.get(key);
    return entry ? { ...entry } : null;
  }

  /**
   * Conditional write - only succeeds if version matches
   */
  write(key: string, value: V, expectedVersion: number): boolean {
    const current = this.cache.get(key);

    // Entry doesn't exist and we expect version 0
    if (!current && expectedVersion === 0) {
      this.cache.set(key, { value, version: 1 });
      return true;
    }

    // Version mismatch
    if (!current || current.version !== expectedVersion) {
      return false;
    }

    // Update with new version
    this.cache.set(key, { value, version: expectedVersion + 1 });
    return true;
  }

  /**
   * Retry write with exponential backoff
   */
  async writeWithRetry(
    key: string,
    updater: (current: V | null) => Promise<V>,
    maxRetries: number = 3
  ): Promise<boolean> {
    let retries = 0;

    while (retries < maxRetries) {
      const current = this.read(key);
      const newValue = await updater(current?.value ?? null);

      if (this.write(key, newValue, current?.version ?? 0)) {
        return true;
      }

      // Exponential backoff
      const delay = Math.pow(2, retries) * 10;
      await new Promise(resolve => setTimeout(resolve, delay));
      retries++;
    }

    return false;
  }
}
```

### 3.4 TTL Drift

**Problem**: Clock skew or long-running operations cause TTL to drift.

```typescript
/**
 * Solution: Monotonic time and TTL refresh boundaries
 */

export class MonotonicTTLCache<V> {
  private cache: Map<string, {
    value: V;
    expiresAt: number;
    refreshBoundary: number; // Only refresh if within this boundary
  }> = new Map();

  // Monotonic clock (not affected by system clock changes)
  private getMonotonicTime(): number {
    // Use performance.now() for monotonic time
    // Add a base for absolute time reference
    return performance.now();
  }

  set(key: string, value: V, ttlMs: number): void {
    const now = this.getMonotonicTime();
    this.cache.set(key, {
      value,
      expiresAt: now + ttlMs,
      refreshBoundary: now + ttlMs * 0.8, // Refresh in last 20% of TTL
    });
  }

  get(key: string): { value: V; shouldRefresh: boolean } | null {
    const entry = this.cache.get(key);
    if (!entry) return null;

    const now = this.getMonotonicTime();

    // Expired
    if (now >= entry.expiresAt) {
      this.cache.delete(key);
      return null;
    }

    // Check if should refresh
    const shouldRefresh = now >= entry.refreshBoundary;

    return {
      value: entry.value,
      shouldRefresh,
    };
  }

  /**
   * Background refresh without blocking reads
   */
  async refreshIfNeeded(
    key: string,
    loader: () => Promise<V>,
    ttlMs: number
  ): Promise<void> {
    const entry = this.cache.get(key);
    if (!entry) {
      // Load fresh
      const value = await loader();
      this.set(key, value, ttlMs);
      return;
    }

    const now = this.getMonotonicTime();
    if (now >= entry.refreshBoundary && now < entry.expiresAt) {
      // Refresh in background
      loader().then(value => {
        this.set(key, value, ttlMs);
      }).catch(err => {
        console.error(`Background refresh failed for ${key}:`, err);
      });
    }
  }
}
```

---

## 4. Test Scenarios

### 4.1 Cache Performance Tests

```typescript
/**
 * Cache performance test suite
 */

describe('Cache Performance', () => {
  let cache: LRUCacheWithTTL<string>;

  beforeEach(() => {
    cache = new LRUCacheWithTTL(10000, 100 * 1024 * 1024, 3600000);
  });

  describe('Basic Operations', () => {
    it('should achieve O(1) get performance', async () => {
      // Populate cache
      for (let i = 0; i < 10000; i++) {
        cache.set(`key-${i}`, `value-${i}`);
      }

      const benchmark = new PerformanceBenchmark({
        name: 'cache-get',
        iterations: 10000,
        warmup: 100,
      });

      const result = await benchmark.run(async () => {
        cache.get(`key-${Math.floor(Math.random() * 10000)}`);
      });

      // Assert O(1) - mean should be < 0.1ms
      expect(result.metrics.mean).toBeLessThan(0.1);

      // Assert low variance - indicates consistent performance
      expect(result.metrics.stdDev / result.metrics.mean).toBeLessThan(0.5);
    });

    it('should handle concurrent reads without degradation', async () => {
      // Populate cache
      for (let i = 0; i < 1000; i++) {
        cache.set(`key-${i}`, `value-${i}`);
      }

      const benchmark = new PerformanceBenchmark({
        name: 'concurrent-reads',
        iterations: 10000,
        warmup: 100,
      });

      const result = await benchmark.runConcurrent(async () => {
        cache.get(`key-${Math.floor(Math.random() * 1000)}`);
      }, 100); // 100 concurrent readers

      // Throughput should scale with concurrency
      expect(result.metrics.opsPerSecond).toBeGreaterThan(100000);
    });
  });

  describe('Eviction', () => {
    it('should maintain performance during eviction', async () => {
      const smallCache = new LRUCacheWithTTL<string>(
        100, // Small cache to trigger frequent evictions
        10 * 1024, // 10KB
        3600000
      );

      const times: number[] = [];

      // Write more than capacity
      for (let i = 0; i < 1000; i++) {
        const start = performance.now();
        smallCache.set(`key-${i}`, `x`.repeat(100));
        times.push(performance.now() - start);
      }

      // Eviction should not cause significant latency spikes
      const maxTime = Math.max(...times);
      expect(maxTime).toBeLessThan(10); // Max 10ms per operation
    });

    it('should correctly evict LRU entries', () => {
      const cache = new LRUCacheWithTTL<string>(3, Infinity, 3600000);

      cache.set('a', '1');
      cache.set('b', '2');
      cache.set('c', '3');

      // Access 'a' to make it recently used
      cache.get('a');

      // Add new entry - should evict 'b' (LRU)
      cache.set('d', '4');

      expect(cache.get('a')).toBe('1');
      expect(cache.get('b')).toBeUndefined(); // Evicted
      expect(cache.get('c')).toBe('3');
      expect(cache.get('d')).toBe('4');
    });
  });

  describe('TTL', () => {
    it('should expire entries correctly', async () => {
      const cache = new LRUCacheWithTTL<string>(100, Infinity, 100); // 100ms TTL

      cache.set('key', 'value');
      expect(cache.get('key')).toBe('value');

      // Wait for expiry
      await new Promise(resolve => setTimeout(resolve, 150));

      expect(cache.get('key')).toBeUndefined();
    });

    it('should not have significant TTL drift', async () => {
      const cache = new LRUCacheWithTTL<string>(100, Infinity, 1000);
      const iterations = 100;
      const drifts: number[] = [];

      for (let i = 0; i < iterations; i++) {
        const start = Date.now();
        cache.set(`key-${i}`, `value-${i}`, 100);

        // Wait for expiry
        await new Promise(resolve => setTimeout(resolve, 100));

        // Check actual expiry time
        const checkStart = Date.now();
        while (cache.get(`key-${i}`) !== undefined) {
          await new Promise(resolve => setTimeout(resolve, 1));
        }
        const actualExpiry = Date.now();

        drifts.push(actualExpiry - start - 100);
      }

      // Average drift should be < 10ms
      const avgDrift = drifts.reduce((a, b) => a + b, 0) / drifts.length;
      expect(Math.abs(avgDrift)).toBeLessThan(10);
    });
  });
});
```

### 4.2 KV-Cache Benchmark Tests

```typescript
/**
 * KV-Cache benchmark tests (KVCOMM targets)
 */

describe('KV-Cache Benchmarks', () => {
  describe('Cache Hit Rate', () => {
    it('should achieve 70%+ hit rate in shared-prefix scenario', async () => {
      const framework = new KVBenchmarkFramework({
        iterations: 1000,
        warmupIterations: 100,
        numAgents: 10,
        sequenceLength: 2048,
        embeddingDim: 768,
        targetCacheHitRate: 0.70,
        verbose: true,
      });

      const result = await framework.runBenchmark('shared-prefix');

      expect(result.comparison.hitRateStatus).toBe('passed');
      expect(result.metrics.cacheHitRate).toBeGreaterThanOrEqual(0.70);
    });
  });

  describe('TTFT Speedup', () => {
    it('should achieve 7.8x TTFT speedup', async () => {
      const framework = new KVBenchmarkFramework({
        iterations: 500,
        warmupIterations: 50,
        targetTTFTSpeedup: 7.8,
        verbose: true,
      });

      const result = await framework.runBenchmark('shared-prefix');

      expect(result.metrics.ttftSpeedup).toBeGreaterThanOrEqual(7.8);
    });
  });

  describe('Memory Efficiency', () => {
    it('should achieve 50%+ memory reduction', async () => {
      const framework = new KVBenchmarkFramework({
        iterations: 1000,
        warmupIterations: 100,
        targetMemoryReduction: 0.50,
        enableCompression: true,
        verbose: true,
      });

      const result = await framework.runBenchmark('shared-prefix');

      expect(result.metrics.memoryReduction).toBeGreaterThanOrEqual(0.50);
    });
  });

  describe('Regression Tests', () => {
    it('should detect performance regressions', async () => {
      const baselines = new Map<string, BenchmarkMetrics>([
        ['cache-lookup', {
          min: 0.01,
          max: 5,
          mean: 0.05,
          median: 0.04,
          p50: 0.04,
          p90: 0.08,
          p95: 0.12,
          p99: 0.25,
          stdDev: 0.02,
          samples: 1000,
          opsPerSecond: 20000,
        }],
      ]);

      const detector = new RegressionDetector(baselines, {
        maxLatencyRegression: 0.05,
        maxThroughputRegression: 0.05,
        minOpsPerSecond: 15000,
      });

      // Simulate current metrics (with regression)
      const currentMetrics: BenchmarkMetrics = {
        min: 0.01,
        max: 10,
        mean: 0.08, // 60% slower
        median: 0.06,
        p50: 0.06,
        p90: 0.15,
        p95: 0.25,
        p99: 0.50, // 100% slower
        stdDev: 0.05,
        samples: 1000,
        opsPerSecond: 12500, // 37.5% slower
      };

      const result = detector.detect('cache-lookup', currentMetrics);

      expect(result.hasRegression).toBe(true);
      expect(result.regressions.length).toBeGreaterThan(0);
    });
  });
});
```

### 4.3 Stress Tests

```typescript
/**
 * Stress tests for cache system
 */

describe('Cache Stress Tests', () => {
  describe('High Load', () => {
    it('should handle 1M operations without memory leak', async () => {
      const cache = new LRUCacheWithTTL<string>(10000, 100 * 1024 * 1024, 3600000);
      const initialMemory = process.memoryUsage().heapUsed;

      for (let i = 0; i < 1000000; i++) {
        cache.set(`key-${i % 15000}`, `value-${i}`);

        if (i % 100000 === 0) {
          // Check memory isn't growing unboundedly
          const currentMemory = process.memoryUsage().heapUsed;
          const growth = currentMemory - initialMemory;

          // Should not grow more than 50MB
          expect(growth).toBeLessThan(50 * 1024 * 1024);
        }
      }

      // Force GC and check final memory
      if (global.gc) global.gc();

      const finalMemory = process.memoryUsage().heapUsed;
      const totalGrowth = finalMemory - initialMemory;

      expect(totalGrowth).toBeLessThan(100 * 1024 * 1024);
    });

    it('should maintain stability under burst traffic', async () => {
      const cache = new LRUCacheWithTTL<string>(1000, 10 * 1024 * 1024, 3600000);

      // Warmup
      for (let i = 0; i < 1000; i++) {
        cache.set(`key-${i}`, `value-${i}`);
      }

      // Burst: 10000 concurrent operations
      const burstStart = performance.now();

      const operations = Array(10000)
        .fill(null)
        .map((_, i) => {
          if (i % 3 === 0) {
            return Promise.resolve(cache.get(`key-${i % 1000}`));
          } else {
            cache.set(`key-${i}`, `value-${i}`);
            return Promise.resolve();
          }
        });

      await Promise.all(operations);

      const burstDuration = performance.now() - burstStart;

      // Should complete burst in under 1 second
      expect(burstDuration).toBeLessThan(1000);
    });
  });

  describe('Edge Cases', () => {
    it('should handle very large values', () => {
      const cache = new LRUCacheWithTTL<string>(100, 10 * 1024 * 1024, 3600000);

      // 1MB value
      const largeValue = 'x'.repeat(1024 * 1024);

      expect(() => cache.set('large', largeValue)).not.toThrow();
      expect(cache.get('large')).toBe(largeValue);
    });

    it('should handle empty and null values', () => {
      const cache = new LRUCacheWithTTL<string | null>(100, Infinity, 3600000);

      cache.set('empty', '');
      cache.set('null', null);

      expect(cache.get('empty')).toBe('');
      expect(cache.get('null')).toBe(null);
    });

    it('should handle key collisions correctly', () => {
      const cache = new LRUCacheWithTTL<string>(100, Infinity, 3600000);

      cache.set('key', 'value1');
      cache.set('key', 'value2');
      cache.set('key', 'value3');

      expect(cache.get('key')).toBe('value3');
      expect(cache.getStats().entries).toBe(1);
    });
  });
});
```

---

## 5. Performance Patterns

### 5.1 Prefetching Pattern

```typescript
/**
 * Prefetching pattern for predictable access patterns
 */

export class PrefetchingCache<V> {
  private cache: Map<string, V> = new Map();
  private accessPattern: Map<string, string[]> = new Map();
  private prefetchQueue: string[] = [];
  private prefetching: boolean = false;

  /**
   * Record access pattern for learning
   */
  recordAccess(key: string): void {
    // Track what keys are typically accessed together
    // This is a simplified version - real implementation would use
    // more sophisticated pattern detection
  }

  /**
   * Get value and trigger prefetch
   */
  async get(key: string, loader: (key: string) => Promise<V>): Promise<V> {
    // Trigger background prefetch for related keys
    this.prefetchRelated(key, loader);

    // Return current value
    if (this.cache.has(key)) {
      return this.cache.get(key)!;
    }

    const value = await loader(key);
    this.cache.set(key, value);
    return value;
  }

  /**
   * Prefetch related keys in background
   */
  private prefetchRelated(key: string, loader: (key: string) => Promise<V>): void {
    const related = this.accessPattern.get(key) || [];

    for (const relatedKey of related) {
      if (!this.cache.has(relatedKey) && !this.prefetchQueue.includes(relatedKey)) {
        this.prefetchQueue.push(relatedKey);
      }
    }

    this.processPrefetchQueue(loader);
  }

  /**
   * Process prefetch queue in background
   */
  private async processPrefetchQueue(loader: (key: string) => Promise<V>): Promise<void> {
    if (this.prefetching || this.prefetchQueue.length === 0) return;

    this.prefetching = true;

    while (this.prefetchQueue.length > 0) {
      const key = this.prefetchQueue.shift()!;

      if (!this.cache.has(key)) {
        try {
          const value = await loader(key);
          this.cache.set(key, value);
        } catch (error) {
          console.error(`Prefetch failed for ${key}:`, error);
        }
      }
    }

    this.prefetching = false;
  }
}
```

### 5.2 Circuit Breaker Pattern

```typescript
/**
 * Circuit breaker for cache operations
 *
 * Prevents cascading failures when cache backend is slow/unavailable
 */

export class CircuitBreakerCache<V> {
  private state: 'closed' | 'open' | 'half-open' = 'closed';
  private failures: number = 0;
  private lastFailureTime: number = 0;

  constructor(
    private cache: {
      get: (key: string) => Promise<V | undefined>;
      set: (key: string, value: V) => Promise<void>;
    },
    private config: {
      failureThreshold: number;
      resetTimeout: number;
      halfOpenMaxCalls: number;
    },
    private fallback: {
      get: (key: string) => Promise<V | undefined>;
      set?: (key: string, value: V) => Promise<void>;
    }
  ) {}

  async get(key: string): Promise<V | undefined> {
    if (this.state === 'open') {
      if (Date.now() - this.lastFailureTime > this.config.resetTimeout) {
        this.state = 'half-open';
      } else {
        return this.fallback.get(key);
      }
    }

    try {
      const value = await this.cache.get(key);
      this.onSuccess();
      return value;
    } catch (error) {
      this.onFailure();
      return this.fallback.get(key);
    }
  }

  async set(key: string, value: V): Promise<void> {
    if (this.state === 'open') {
      // Don't attempt write to failing backend
      if (this.fallback.set) {
        return this.fallback.set(key, value);
      }
      return;
    }

    try {
      await this.cache.set(key, value);
      this.onSuccess();
    } catch (error) {
      this.onFailure();
      if (this.fallback.set) {
        return this.fallback.set(key, value);
      }
    }
  }

  private onSuccess(): void {
    this.failures = 0;
    this.state = 'closed';
  }

  private onFailure(): void {
    this.failures++;
    this.lastFailureTime = Date.now();

    if (this.failures >= this.config.failureThreshold) {
      this.state = 'open';
    }
  }

  getState(): { state: string; failures: number } {
    return {
      state: this.state,
      failures: this.failures,
    };
  }
}
```

### 5.3 Read-Through/Write-Through Pattern

```typescript
/**
 * Read-through and write-through cache pattern
 */

export class ReadWriteThroughCache<V> {
  constructor(
    private cache: {
      get: (key: string) => Promise<V | undefined>;
      set: (key: string, value: V, ttl?: number) => Promise<void>;
      delete: (key: string) => Promise<boolean>;
    },
    private backend: {
      read: (key: string) => Promise<V>;
      write: (key: string, value: V) => Promise<void>;
      delete: (key: string) => Promise<void>;
    },
    private config: {
      ttl: number;
      writeDelay: number; // Batch writes
    }
  ) {}

  /**
   * Read-through: get from cache, load from backend on miss
   */
  async get(key: string): Promise<V> {
    // Try cache first
    const cached = await this.cache.get(key);
    if (cached !== undefined) {
      return cached;
    }

    // Load from backend
    const value = await this.backend.read(key);

    // Populate cache
    await this.cache.set(key, value, this.config.ttl);

    return value;
  }

  /**
   * Write-through: write to cache and backend
   */
  async set(key: string, value: V): Promise<void> {
    // Write to cache immediately
    await this.cache.set(key, value, this.config.ttl);

    // Write to backend
    await this.backend.write(key, value);
  }

  /**
   * Write-behind: write to cache immediately, backend async
   */
  async setAsync(key: string, value: V): Promise<void> {
    // Write to cache immediately
    await this.cache.set(key, value, this.config.ttl);

    // Write to backend asynchronously
    this.backend.write(key, value).catch(error => {
      console.error(`Async write failed for ${key}:`, error);
    });
  }

  /**
   * Invalidate both cache and backend
   */
  async delete(key: string): Promise<void> {
    await this.cache.delete(key);
    await this.backend.delete(key);
  }
}
```

---

## Appendix A: Quick Reference

### A.1 Performance Targets (KVCOMM)

| Metric | Target | Description |
|--------|--------|-------------|
| Cache Hit Rate | 70%+ | Percentage of requests served from cache |
| TTFT Speedup | 7.8x | Time-to-first-token improvement |
| Memory Reduction | 50% | Reduction in memory usage vs baseline |
| Lookup Latency P99 | <100ms | 99th percentile lookup time |
| Throughput | >1000 ops/s | Operations per second |

### A.2 Cache Configuration Quick Reference

```typescript
// Recommended defaults
const DEFAULT_CACHE_CONFIG = {
  maxEntries: 10000,
  maxMemoryBytes: 1024 * 1024 * 1024, // 1GB
  defaultTTL: 3600000, // 1 hour
  evictionPolicy: 'hybrid',
  lruWeight: 0.4,
  lfuWeight: 0.3,
  qualityWeight: 0.3,
  evictionThreshold: 0.9,
};
```

### A.3 Benchmark Configuration Quick Reference

```typescript
const DEFAULT_BENCHMARK_CONFIG = {
  iterations: 1000,
  warmupIterations: 100,
  timeout: 300000, // 5 minutes
  seed: Date.now(),
  numAgents: 10,
  sequenceLength: 2048,
  embeddingDim: 768,
};
```

---

*Document generated for glm-4.7 implementation agents*
*POLLN Performance Architecture Team*
