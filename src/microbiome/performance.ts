/**
 * POLLN Microbiome - Performance Monitoring System
 *
 * Phase 5: Production Optimization - Milestone 1
 * Comprehensive performance monitoring with percentile calculation,
 * anomaly detection, and metrics export for external monitoring systems.
 *
 * @module microbiome/performance
 */

/**
 * Performance metric for a single operation
 */
export interface PerformanceMetric {
  /** Operation name (e.g., 'evolution', 'colony_discovery') */
  operation: string;
  /** Number of times operation was recorded */
  count: number;
  /** Total time spent on this operation (ms) */
  totalTime: number;
  /** Average time per operation (ms) */
  avgTime: number;
  /** Minimum time for a single operation (ms) */
  minTime: number;
  /** Maximum time for a single operation (ms) */
  maxTime: number;
  /** 50th percentile (median) time (ms) */
  p50: number;
  /** 95th percentile time (ms) */
  p95: number;
  /** 99th percentile time (ms) */
  p99: number;
  /** Timestamp of last update */
  lastUpdated: number;
  /** Individual timing samples (kept for percentile calculation) */
  samples: number[];
  /** Maximum samples to keep (prevents memory bloat) */
  maxSamples: number;
}

/**
 * Performance alert for anomalies
 */
export interface PerformanceAlert {
  /** Alert ID */
  id: string;
  /** Severity level */
  severity: 'info' | 'warning' | 'critical';
  /** Operation that triggered the alert */
  operation: string;
  /** Alert message */
  message: string;
  /** Current value that triggered alert */
  currentValue: number;
  /** Expected/threshold value */
  thresholdValue: number;
  /** Timestamp when alert was generated */
  timestamp: number;
  /** Type of anomaly */
  type: 'regression' | 'spike' | 'slowdown' | 'memory_growth';
}

/**
 * Performance summary across all operations
 */
export interface PerformanceSummary {
  /** Summary timestamp */
  timestamp: number;
  /** Total operations tracked */
  totalOperations: number;
  /** Total execution time across all operations */
  totalExecutionTime: number;
  /** Operations by name */
  operations: Map<string, PerformanceMetric>;
  /** Active alerts */
  alerts: PerformanceAlert[];
  /** System health score (0-1) */
  healthScore: number;
}

/**
 * Metrics export format
 */
export interface MetricsExport {
  /** Export format type */
  format: 'prometheus' | 'json' | 'influx';
  /** Exported data */
  data: string | Record<string, any>;
  /** Export timestamp */
  timestamp: number;
}

/**
 * Performance monitor configuration
 */
export interface PerformanceMonitorConfig {
  /** Maximum samples to keep per operation */
  maxSamples?: number;
  /** Enable automatic anomaly detection */
  enableAnomalyDetection?: boolean;
  /** Regression threshold (percentage increase to alert) */
  regressionThreshold?: number;
  /** Slow operation threshold (ms) */
  slowOperationThreshold?: number;
  /** Enable metrics streaming */
  enableStreaming?: boolean;
  /** Streaming callback for real-time metrics */
  streamingCallback?: (metrics: PerformanceSummary) => void;
}

/**
 * Performance monitor - tracks and analyzes system performance
 */
export class PerformanceMonitor {
  /** Metrics by operation name */
  private metrics: Map<string, PerformanceMetric>;
  /** Active alerts */
  private alerts: PerformanceAlert[];
  /** Configuration */
  private config: Required<PerformanceMonitorConfig>;
  /** Historical baselines for anomaly detection */
  private baselines: Map<string, number>;
  /** Monitor start time */
  private startTime: number;

  constructor(config: PerformanceMonitorConfig = {}) {
    this.metrics = new Map();
    this.alerts = [];
    this.baselines = new Map();
    this.startTime = Date.now();

    this.config = {
      maxSamples: config.maxSamples ?? 1000,
      enableAnomalyDetection: config.enableAnomalyDetection ?? true,
      regressionThreshold: config.regressionThreshold ?? 0.5, // 50% increase
      slowOperationThreshold: config.slowOperationThreshold ?? 1000, // 1 second
      enableStreaming: config.enableStreaming ?? false,
      streamingCallback: config.streamingCallback ?? (() => {}),
    };
  }

  /**
   * Record an operation timing
   */
  recordOperation(operation: string, duration: number, metadata?: Record<string, any>): void {
    const now = Date.now();

    // Get or create metric
    let metric = this.metrics.get(operation);
    if (!metric) {
      metric = this.createMetric(operation);
      this.metrics.set(operation, metric);
    }

    // Update basic stats
    metric.count++;
    metric.totalTime += duration;
    metric.minTime = Math.min(metric.minTime, duration);
    metric.maxTime = Math.max(metric.maxTime, duration);
    metric.avgTime = metric.totalTime / metric.count;

    // Add sample for percentile calculation
    metric.samples.push(duration);
    if (metric.samples.length > metric.maxSamples) {
      metric.samples.shift(); // Remove oldest sample
    }

    // Recalculate percentiles
    this.calculatePercentiles(metric);

    metric.lastUpdated = now;

    // Detect anomalies if enabled
    if (this.config.enableAnomalyDetection) {
      this.detectAnomalies();
    }

    // Stream metrics if enabled
    if (this.config.enableStreaming) {
      const summary = this.getSummary();
      this.config.streamingCallback(summary);
    }
  }

  /**
   * Record operation with automatic timing
   */
  async recordOperationAsync<T>(
    operation: string,
    fn: () => Promise<T>,
    metadata?: Record<string, any>
  ): Promise<T> {
    const start = Date.now();
    try {
      const result = await fn();
      const duration = Date.now() - start;
      this.recordOperation(operation, duration, metadata);
      return result;
    } catch (error) {
      const duration = Date.now() - start;
      this.recordOperation(operation, duration, { ...metadata, error: true });
      throw error;
    }
  }

  /**
   * Record synchronous operation with automatic timing
   */
  recordOperationSync<T>(
    operation: string,
    fn: () => T,
    metadata?: Record<string, any>
  ): T {
    const start = Date.now();
    try {
      const result = fn();
      const duration = Date.now() - start;
      this.recordOperation(operation, duration, metadata);
      return result;
    } catch (error) {
      const duration = Date.now() - start;
      this.recordOperation(operation, duration, { ...metadata, error: true });
      throw error;
    }
  }

  /**
   * Get performance summary
   */
  getSummary(): PerformanceSummary {
    const totalOperations = Array.from(this.metrics.values()).reduce(
      (sum, m) => sum + m.count,
      0
    );
    const totalExecutionTime = Array.from(this.metrics.values()).reduce(
      (sum, m) => sum + m.totalTime,
      0
    );

    // Calculate health score based on alerts and performance
    const healthScore = this.calculateHealthScore();

    return {
      timestamp: Date.now(),
      totalOperations,
      totalExecutionTime,
      operations: new Map(this.metrics),
      alerts: [...this.alerts],
      healthScore,
    };
  }

  /**
   * Get metric for a specific operation
   */
  getMetric(operation: string): PerformanceMetric | undefined {
    return this.metrics.get(operation);
  }

  /**
   * Get all metrics
   */
  getAllMetrics(): Map<string, PerformanceMetric> {
    return new Map(this.metrics);
  }

  /**
   * Get active alerts
   */
  getAlerts(): PerformanceAlert[] {
    return [...this.alerts];
  }

  /**
   * Clear old alerts
   */
  clearAlerts(olderThan?: number): void {
    if (olderThan) {
      const cutoff = Date.now() - olderThan;
      this.alerts = this.alerts.filter(alert => alert.timestamp > cutoff);
    } else {
      this.alerts = [];
    }
  }

  /**
   * Reset all metrics
   */
  reset(): void {
    this.metrics.clear();
    this.alerts = [];
    this.baselines.clear();
    this.startTime = Date.now();
  }

  /**
   * Export metrics in Prometheus format
   */
  exportPrometheus(): MetricsExport {
    const lines: string[] = [];

    // Add metadata
    lines.push('# POLLN Microbiome Performance Metrics');
    lines.push(`# Exported at: ${new Date().toISOString()}`);
    lines.push('');

    // Export each operation's metrics
    const metricsArray = Array.from(this.metrics.entries());
    for (const [operation, metric] of metricsArray) {
      // Sanitize operation name for Prometheus (replace special chars with underscores)
      const safeOpName = operation.replace(/[^a-zA-Z0-9_]/g, '_');

      // Count metric
      lines.push(
        `polln_operation_count{operation="${safeOpName}"} ${metric.count}`
      );

      // Time metrics
      lines.push(
        `polln_operation_total_time_ms{operation="${safeOpName}"} ${metric.totalTime}`
      );
      lines.push(
        `polln_operation_avg_time_ms{operation="${safeOpName}"} ${metric.avgTime.toFixed(2)}`
      );
      lines.push(
        `polln_operation_min_time_ms{operation="${safeOpName}"} ${metric.minTime === Infinity ? 0 : metric.minTime}`
      );
      lines.push(
        `polln_operation_max_time_ms{operation="${safeOpName}"} ${metric.maxTime === -Infinity ? 0 : metric.maxTime}`
      );

      // Percentile metrics
      lines.push(
        `polln_operation_p50_time_ms{operation="${safeOpName}"} ${metric.p50.toFixed(2)}`
      );
      lines.push(
        `polln_operation_p95_time_ms{operation="${safeOpName}"} ${metric.p95.toFixed(2)}`
      );
      lines.push(
        `polln_operation_p99_time_ms{operation="${safeOpName}"} ${metric.p99.toFixed(2)}`
      );

      lines.push('');
    }

    // Export system health
    const summary = this.getSummary();
    lines.push(`polln_health_score ${summary.healthScore.toFixed(2)}`);
    lines.push(`polln_total_operations ${summary.totalOperations}`);
    lines.push(`polln_total_execution_time_ms ${summary.totalExecutionTime}`);
    lines.push(`polln_active_alerts ${summary.alerts.length}`);
    lines.push('');
    lines.push(`polln_monitor_uptime_ms ${Date.now() - this.startTime}`);

    return {
      format: 'prometheus',
      data: lines.join('\n'),
      timestamp: Date.now(),
    };
  }

  /**
   * Export metrics in JSON format
   */
  exportJSON(): MetricsExport {
    const summary = this.getSummary();

    const data = {
      timestamp: summary.timestamp,
      uptime: Date.now() - this.startTime,
      totalOperations: summary.totalOperations,
      totalExecutionTime: summary.totalExecutionTime,
      healthScore: summary.healthScore,
      operations: {} as Record<string, any>,
      alerts: summary.alerts,
    };

    // Convert operations map to object
    const metricsArray = Array.from(this.metrics.entries());
    for (const [operation, metric] of metricsArray) {
      data.operations[operation] = {
        count: metric.count,
        totalTime: metric.totalTime,
        avgTime: metric.avgTime,
        minTime: metric.minTime,
        maxTime: metric.maxTime,
        p50: metric.p50,
        p95: metric.p95,
        p99: metric.p99,
        lastUpdated: metric.lastUpdated,
      };
    }

    return {
      format: 'json',
      data,
      timestamp: Date.now(),
    };
  }

  /**
   * Export metrics in InfluxDB line protocol format
   */
  exportInflux(): MetricsExport {
    const lines: string[] = [];

    const metricsArray = Array.from(this.metrics.entries());
    for (const [operation, metric] of metricsArray) {
      const safeOpName = operation.replace(/[^a-z0-9_]/gi, '_');
      const timestamp = metric.lastUpdated * 1e6; // Convert to nanoseconds

      // Create measurement with tags and fields
      const line = `polln_operation,operation=${safeOpName} ` +
        `count=${metric.count}i,` +
        `total_time_ms=${metric.totalTime},` +
        `avg_time_ms=${metric.avgTime.toFixed(2)},` +
        `min_time_ms=${metric.minTime},` +
        `max_time_ms=${metric.maxTime},` +
        `p50_time_ms=${metric.p50.toFixed(2)},` +
        `p95_time_ms=${metric.p95.toFixed(2)},` +
        `p99_time_ms=${metric.p99.toFixed(2)} ` +
        `${timestamp}`;

      lines.push(line);
    }

    return {
      format: 'influx',
      data: lines.join('\n'),
      timestamp: Date.now(),
    };
  }

  /**
   * Export metrics (defaults to Prometheus format)
   */
  exportMetrics(format: 'prometheus' | 'json' | 'influx' = 'prometheus'): MetricsExport {
    switch (format) {
      case 'prometheus':
        return this.exportPrometheus();
      case 'json':
        return this.exportJSON();
      case 'influx':
        return this.exportInflux();
      default:
        return this.exportPrometheus();
    }
  }

  /**
   * Detect performance anomalies
   */
  detectAnomalies(): PerformanceAlert[] {
    const newAlerts: PerformanceAlert[] = [];
    const now = Date.now();

    const metricsArray = Array.from(this.metrics.entries());
    for (const [operation, metric] of metricsArray) {
      // Update baseline if we have enough samples and no baseline exists
      const baseline = this.baselines.get(operation);
      if (metric.count >= 20 && !baseline) {
        this.baselines.set(operation, metric.avgTime);
      }

      // Check for slow operations (only if we have enough samples)
      if (metric.count >= 5 && metric.avgTime > this.config.slowOperationThreshold) {
        const alert: PerformanceAlert = {
          id: `${operation}-slow-${now}`,
          severity: 'warning',
          operation,
          message: `Operation ${operation} is slow (avg: ${metric.avgTime.toFixed(2)}ms)`,
          currentValue: metric.avgTime,
          thresholdValue: this.config.slowOperationThreshold,
          timestamp: now,
          type: 'slowdown',
        };
        newAlerts.push(alert);
      }

      // Check for performance regression (now baseline is set above)
      const currentBaseline = this.baselines.get(operation);
      if (currentBaseline && metric.count > 10) {
        // Only check after we have enough samples
        const regressionThreshold = currentBaseline * (1 + this.config.regressionThreshold);
        if (metric.avgTime > regressionThreshold) {
          const alert: PerformanceAlert = {
            id: `${operation}-regression-${now}`,
            severity: 'critical',
            operation,
            message: `Performance regression in ${operation} (${metric.avgTime.toFixed(2)}ms vs baseline ${currentBaseline.toFixed(2)}ms)`,
            currentValue: metric.avgTime,
            thresholdValue: regressionThreshold,
            timestamp: now,
            type: 'regression',
          };
          newAlerts.push(alert);
        }
      }

      // Check for spikes (sudden increases in max time)
      if (metric.samples.length >= 20) {
        const recentSamples = metric.samples.slice(-10);
        const avgRecent = recentSamples.reduce((a, b) => a + b, 0) / recentSamples.length;
        const olderSamples = metric.samples.slice(0, -10);
        if (olderSamples.length > 0) {
          const avgOlder = olderSamples.reduce((a, b) => a + b, 0) / olderSamples.length;
          if (avgRecent > avgOlder * 2 && metric.maxTime > avgOlder * 3) {
            const alert: PerformanceAlert = {
              id: `${operation}-spike-${now}`,
              severity: 'warning',
              operation,
              message: `Performance spike in ${operation} (max: ${metric.maxTime}ms)`,
              currentValue: metric.maxTime,
              thresholdValue: avgOlder * 3,
              timestamp: now,
              type: 'spike',
            };
            newAlerts.push(alert);
          }
        }
      }
    }

    // Add new alerts (avoid duplicates)
    for (const alert of newAlerts) {
      const exists = this.alerts.some(
        existing =>
          existing.operation === alert.operation &&
          existing.type === alert.type &&
          existing.timestamp > now - 60000 // Avoid duplicates within 1 minute
      );
      if (!exists) {
        this.alerts.push(alert);
      }
    }

    // Keep only recent alerts (last hour)
    const alertRetention = 60 * 60 * 1000; // 1 hour
    this.alerts = this.alerts.filter(alert => alert.timestamp > now - alertRetention);

    return newAlerts;
  }

  /**
   * Get performance trends over time
   */
  getTrends(operation: string, windowSize: number = 100): {
    trend: 'improving' | 'degrading' | 'stable';
    changeRate: number;
  } {
    const metric = this.metrics.get(operation);
    if (!metric || metric.samples.length < windowSize) {
      return { trend: 'stable', changeRate: 0 };
    }

    const samples = metric.samples.slice(-windowSize);
    const firstHalf = samples.slice(0, Math.floor(windowSize / 2));
    const secondHalf = samples.slice(Math.floor(windowSize / 2));

    const avgFirst = firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
    const avgSecond = secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;

    const changeRate = ((avgSecond - avgFirst) / avgFirst) * 100;

    let trend: 'improving' | 'degrading' | 'stable';
    if (changeRate > 10) {
      trend = 'degrading';
    } else if (changeRate < -10) {
      trend = 'improving';
    } else {
      trend = 'stable';
    }

    return { trend, changeRate };
  }

  /**
   * Calculate system health score
   */
  private calculateHealthScore(): number {
    if (this.metrics.size === 0) {
      return 1.0;
    }

    let score = 1.0;

    // Penalize for alerts
    const criticalAlerts = this.alerts.filter(a => a.severity === 'critical').length;
    const warningAlerts = this.alerts.filter(a => a.severity === 'warning').length;

    score -= criticalAlerts * 0.2;
    score -= warningAlerts * 0.1;

    // Penalize for slow operations
    const metricsArray = Array.from(this.metrics.values());
    for (const metric of metricsArray) {
      if (metric.avgTime > this.config.slowOperationThreshold * 2) {
        score -= 0.1;
      } else if (metric.avgTime > this.config.slowOperationThreshold) {
        score -= 0.05;
      }
    }

    // Ensure score is between 0 and 1
    return Math.max(0, Math.min(1, score));
  }

  /**
   * Create a new metric
   */
  private createMetric(operation: string): PerformanceMetric {
    return {
      operation,
      count: 0,
      totalTime: 0,
      avgTime: 0,
      minTime: Infinity,
      maxTime: -Infinity,
      p50: 0,
      p95: 0,
      p99: 0,
      lastUpdated: Date.now(),
      samples: [],
      maxSamples: this.config.maxSamples,
    };
  }

  /**
   * Calculate percentiles from samples
   */
  private calculatePercentiles(metric: PerformanceMetric): void {
    if (metric.samples.length === 0) {
      return;
    }

    // Sort samples for percentile calculation
    const sorted = [...metric.samples].sort((a, b) => a - b);

    // Helper to get value at percentile
    const getPercentile = (p: number): number => {
      const index = Math.floor((p / 100) * sorted.length);
      return sorted[Math.min(index, sorted.length - 1)];
    };

    metric.p50 = getPercentile(50);
    metric.p95 = getPercentile(95);
    metric.p99 = getPercentile(99);
  }
}

/**
 * Create a performance monitor with default configuration
 */
export function createPerformanceMonitor(
  config?: PerformanceMonitorConfig
): PerformanceMonitor {
  return new PerformanceMonitor(config);
}

/**
 * Decorator for automatic performance monitoring
 */
export function monitorOperation(operationName?: string) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const originalMethod = descriptor.value;
    const operation = operationName || `${target.constructor.name}.${propertyKey}`;

    if (!originalMethod) {
      throw new Error(`Cannot decorate ${propertyKey}: method not found`);
    }

    descriptor.value = async function (...args: any[]) {
      // Check if instance has performance monitor
      const monitor = (this as any)._performanceMonitor as PerformanceMonitor;
      if (!monitor) {
        return originalMethod.apply(this, args);
      }

      return monitor.recordOperationAsync(operation, () =>
        originalMethod.apply(this, args)
      );
    };

    return descriptor;
  };
}
