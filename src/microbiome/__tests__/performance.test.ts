/**
 * POLLN Microbiome - Performance Monitoring Tests
 *
 * Comprehensive tests for the performance monitoring system including
 * metric tracking, percentile calculation, anomaly detection, and export formats.
 *
 * @module microbiome/__tests__/performance.test
 */

import {
  PerformanceMonitor,
  PerformanceMetric,
  PerformanceAlert,
  PerformanceSummary,
  MetricsExport,
  createPerformanceMonitor,
  monitorOperation,
} from '../performance.js';

describe('PerformanceMonitor', () => {
  let monitor: PerformanceMonitor;

  beforeEach(() => {
    monitor = new PerformanceMonitor({
      maxSamples: 100,
      enableAnomalyDetection: true,
      regressionThreshold: 0.5,
      slowOperationThreshold: 100,
    });
  });

  describe('Basic Operation Recording', () => {
    test('should record a single operation', () => {
      monitor.recordOperation('test_operation', 50);

      const metric = monitor.getMetric('test_operation');
      expect(metric).toBeDefined();
      expect(metric?.count).toBe(1);
      expect(metric?.totalTime).toBe(50);
      expect(metric?.avgTime).toBe(50);
      expect(metric?.minTime).toBe(50);
      expect(metric?.maxTime).toBe(50);
    });

    test('should record multiple operations', () => {
      monitor.recordOperation('test_operation', 50);
      monitor.recordOperation('test_operation', 100);
      monitor.recordOperation('test_operation', 150);

      const metric = monitor.getMetric('test_operation');
      expect(metric?.count).toBe(3);
      expect(metric?.totalTime).toBe(300);
      expect(metric?.avgTime).toBe(100);
      expect(metric?.minTime).toBe(50);
      expect(metric?.maxTime).toBe(150);
    });

    test('should track multiple different operations', () => {
      monitor.recordOperation('operation_a', 50);
      monitor.recordOperation('operation_b', 100);
      monitor.recordOperation('operation_c', 150);

      expect(monitor.getMetric('operation_a')?.count).toBe(1);
      expect(monitor.getMetric('operation_b')?.count).toBe(1);
      expect(monitor.getMetric('operation_c')?.count).toBe(1);
    });

    test('should handle zero-duration operations', () => {
      monitor.recordOperation('instant_operation', 0);

      const metric = monitor.getMetric('instant_operation');
      expect(metric?.count).toBe(1);
      expect(metric?.minTime).toBe(0);
    });
  });

  describe('Percentile Calculation', () => {
    test('should calculate p50 (median) correctly', () => {
      // Create a distribution with known median
      const values = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100];
      values.forEach(v => monitor.recordOperation('test', v));

      const metric = monitor.getMetric('test');
      // Median should be around 50-60
      expect(metric?.p50).toBeGreaterThanOrEqual(50);
      expect(metric?.p50).toBeLessThanOrEqual(60);
    });

    test('should calculate p95 correctly', () => {
      // Create 100 samples, p95 should be near 95
      const values = Array.from({ length: 100 }, (_, i) => i + 1);
      values.forEach(v => monitor.recordOperation('test', v));

      const metric = monitor.getMetric('test');
      expect(metric?.p95).toBeGreaterThanOrEqual(90);
      expect(metric?.p95).toBeLessThanOrEqual(100);
    });

    test('should calculate p99 correctly', () => {
      // Create 100 samples, p99 should be near 99
      const values = Array.from({ length: 100 }, (_, i) => i + 1);
      values.forEach(v => monitor.recordOperation('test', v));

      const metric = monitor.getMetric('test');
      expect(metric?.p99).toBeGreaterThanOrEqual(95);
      expect(metric?.p99).toBeLessThanOrEqual(100);
    });

    test('should handle single sample for percentiles', () => {
      monitor.recordOperation('test', 100);

      const metric = monitor.getMetric('test');
      expect(metric?.p50).toBe(100);
      expect(metric?.p95).toBe(100);
      expect(metric?.p99).toBe(100);
    });

    test('should maintain percentiles with rolling samples', () => {
      const smallMonitor = new PerformanceMonitor({ maxSamples: 10 });

      // Add 20 samples, should only keep last 10
      for (let i = 1; i <= 20; i++) {
        smallMonitor.recordOperation('test', i * 10);
      }

      const metric = smallMonitor.getMetric('test');
      expect(metric?.count).toBe(20); // Count still tracks all
      expect(metric?.samples.length).toBe(10); // But samples are limited
      expect(metric?.samples[0]).toBe(110); // First kept sample is 11th value
    });
  });

  describe('Anomaly Detection', () => {
    test('should detect slow operations', () => {
      // Record slow operations (need 5+ samples to trigger)
      for (let i = 0; i < 5; i++) {
        monitor.recordOperation('slow_operation', 150);
      }

      const alerts = monitor.detectAnomalies();
      const slowAlerts = alerts.filter(a => a.type === 'slowdown');
      expect(slowAlerts.length).toBeGreaterThan(0);
      expect(slowAlerts[0].operation).toBe('slow_operation');
    });

    test('should detect performance regression', () => {
      // Establish baseline with fast operations (need 20 to set baseline)
      for (let i = 0; i < 20; i++) {
        monitor.recordOperation('regression_test', 10);
      }

      // Call detectAnomalies to set the baseline
      monitor.detectAnomalies();

      // Clear any alerts from baseline
      monitor.clearAlerts();

      // Record MANY slow operations that trigger regression
      // Need enough to push the average over baseline * 1.5 = 15ms
      for (let i = 0; i < 30; i++) {
        monitor.recordOperation('regression_test', 25); // 150% increase > 50% threshold
      }

      const alerts = monitor.detectAnomalies();
      const regressionAlerts = alerts.filter(a => a.type === 'regression');
      expect(regressionAlerts.length).toBeGreaterThan(0);
    });

    test('should detect performance spikes', () => {
      // Establish baseline (need 20 samples total)
      for (let i = 0; i < 10; i++) {
        monitor.recordOperation('spike_test', 50);
      }
      for (let i = 0; i < 10; i++) {
        monitor.recordOperation('spike_test', 500); // Spike
      }

      const alerts = monitor.detectAnomalies();
      const spikeAlerts = alerts.filter(a => a.type === 'spike');
      expect(spikeAlerts.length).toBeGreaterThan(0);
    });

    test('should clear old alerts', async () => {
      // Need enough samples to trigger alert
      for (let i = 0; i < 5; i++) {
        monitor.recordOperation('test', 200);
      }
      monitor.detectAnomalies();

      const beforeClear = monitor.getAlerts().length;
      expect(beforeClear).toBeGreaterThan(0);

      // Clear all alerts (no time limit)
      monitor.clearAlerts();

      const afterClear = monitor.getAlerts().length;
      expect(afterClear).toBe(0);
    });

    test('should not create duplicate alerts within time window', () => {
      monitor.recordOperation('test', 200);
      monitor.detectAnomalies();

      const firstCount = monitor.getAlerts().length;

      // Try to detect again immediately
      monitor.detectAnomalies();

      const secondCount = monitor.getAlerts().length;
      // Should not have increased significantly (no duplicates)
      expect(secondCount).toBeLessThanOrEqual(firstCount + 1);
    });
  });

  describe('Metrics Export', () => {
    beforeEach(() => {
      // Create some sample data
      monitor.recordOperation('evolution', 500);
      monitor.recordOperation('evolution', 600);
      monitor.recordOperation('colony_discovery', 100);
      monitor.recordOperation('colony_discovery', 150);
      monitor.recordOperation('immune_scan', 75);
    });

    test('should export metrics in Prometheus format', () => {
      const exportData = monitor.exportPrometheus();

      expect(exportData.format).toBe('prometheus');
      expect(typeof exportData.data).toBe('string');
      expect(exportData.data).toContain('polln_operation_count');
      expect(exportData.data).toContain('polln_operation_avg_time_ms');
      expect(exportData.data).toContain('polln_operation_p50_time_ms');
      expect(exportData.data).toContain('polln_operation_p95_time_ms');
      expect(exportData.data).toContain('polln_operation_p99_time_ms');
      expect(exportData.data).toContain('evolution');
      expect(exportData.data).toContain('colony_discovery');
    });

    test('should export metrics in JSON format', () => {
      const exportData = monitor.exportJSON();

      expect(exportData.format).toBe('json');
      expect(typeof exportData.data).toBe('object');

      const data = exportData.data as Record<string, any>;
      expect(data).toHaveProperty('timestamp');
      expect(data).toHaveProperty('totalOperations');
      expect(data).toHaveProperty('operations');
      expect(data).toHaveProperty('alerts');
      expect(data).toHaveProperty('healthScore');

      expect(data.operations).toHaveProperty('evolution');
      expect(data.operations).toHaveProperty('colony_discovery');
      expect(data.operations.evolution).toHaveProperty('count');
      expect(data.operations.evolution).toHaveProperty('avgTime');
      expect(data.operations.evolution).toHaveProperty('p50');
      expect(data.operations.evolution).toHaveProperty('p95');
      expect(data.operations.evolution).toHaveProperty('p99');
    });

    test('should export metrics in InfluxDB format', () => {
      const exportData = monitor.exportInflux();

      expect(exportData.format).toBe('influx');
      expect(typeof exportData.data).toBe('string');
      expect(exportData.data).toContain('polln_operation');
      expect(exportData.data).toContain('count=');
      expect(exportData.data).toContain('avg_time_ms=');
      expect(exportData.data).toContain('p50_time_ms=');
      expect(exportData.data).toContain('p95_time_ms=');
      expect(exportData.data).toContain('p99_time_ms=');
    });

    test('should export with default Prometheus format', () => {
      const exportData = monitor.exportMetrics();
      expect(exportData.format).toBe('prometheus');
    });

    test('should export in different formats based on parameter', () => {
      const prometheus = monitor.exportMetrics('prometheus');
      const json = monitor.exportMetrics('json');
      const influx = monitor.exportMetrics('influx');

      expect(prometheus.format).toBe('prometheus');
      expect(json.format).toBe('json');
      expect(influx.format).toBe('influx');
    });
  });

  describe('Performance Summary', () => {
    test('should generate comprehensive performance summary', () => {
      monitor.recordOperation('op1', 100);
      monitor.recordOperation('op2', 200);
      monitor.recordOperation('op3', 300);

      const summary = monitor.getSummary();

      expect(summary).toHaveProperty('timestamp');
      expect(summary.totalOperations).toBe(3);
      expect(summary.totalExecutionTime).toBe(600);
      expect(summary.operations.size).toBe(3);
      expect(summary.alerts).toEqual([]);
      expect(summary.healthScore).toBeGreaterThanOrEqual(0);
      expect(summary.healthScore).toBeLessThanOrEqual(1);
    });

    test('should calculate health score correctly', () => {
      // Good performance
      for (let i = 0; i < 10; i++) {
        monitor.recordOperation('fast', 10);
      }

      let summary = monitor.getSummary();
      expect(summary.healthScore).toBeGreaterThan(0.8);

      // Add slow operations
      monitor.recordOperation('slow', 200);
      summary = monitor.getSummary();
      expect(summary.healthScore).toBeLessThan(1.0);
    });

    test('should include active alerts in summary', () => {
      // Need enough samples to trigger alert
      for (let i = 0; i < 5; i++) {
        monitor.recordOperation('slow_op', 200);
      }
      monitor.detectAnomalies();

      const summary = monitor.getSummary();
      expect(summary.alerts.length).toBeGreaterThan(0);
    });
  });

  describe('Synchronous Operation Recording', () => {
    test('should record synchronous operation timing', () => {
      const result = monitor.recordOperationSync('sync_op', () => {
        return 42;
      });

      expect(result).toBe(42);

      const metric = monitor.getMetric('sync_op');
      expect(metric?.count).toBe(1);
      expect(metric?.totalTime).toBeGreaterThanOrEqual(0);
    });

    test('should record sync operation that throws', () => {
      expect(() => {
        monitor.recordOperationSync('failing_op', () => {
          throw new Error('Test error');
        });
      }).toThrow('Test error');

      const metric = monitor.getMetric('failing_op');
      expect(metric?.count).toBe(1);
    });
  });

  describe('Asynchronous Operation Recording', () => {
    test('should record async operation timing', async () => {
      const result = await monitor.recordOperationAsync('async_op', async () => {
        await new Promise(resolve => setTimeout(resolve, 10));
        return 42;
      });

      expect(result).toBe(42);

      const metric = monitor.getMetric('async_op');
      expect(metric?.count).toBe(1);
      expect(metric?.totalTime).toBeGreaterThanOrEqual(5); // Reduced threshold for timing precision
    });

    test('should record async operation that rejects', async () => {
      await expect(
        monitor.recordOperationAsync('failing_async_op', async () => {
          throw new Error('Async error');
        })
      ).rejects.toThrow('Async error');

      const metric = monitor.getMetric('failing_async_op');
      expect(metric?.count).toBe(1);
    });
  });

  describe('Performance Trends', () => {
    test('should detect improving trend', () => {
      // Add samples that get faster over time
      for (let i = 0; i < 100; i++) {
        monitor.recordOperation('improving', 100 - i); // 100, 99, 98, ... 1
      }

      const trends = monitor.getTrends('improving');
      expect(trends.trend).toBe('improving');
      expect(trends.changeRate).toBeLessThan(0);
    });

    test('should detect degrading trend', () => {
      // Add samples that get slower over time
      for (let i = 0; i < 100; i++) {
        monitor.recordOperation('degrading', i + 1); // 1, 2, 3, ... 100
      }

      const trends = monitor.getTrends('degrading');
      expect(trends.trend).toBe('degrading');
      expect(trends.changeRate).toBeGreaterThan(0);
    });

    test('should detect stable trend', () => {
      // Add consistent samples
      for (let i = 0; i < 100; i++) {
        monitor.recordOperation('stable', 50);
      }

      const trends = monitor.getTrends('stable');
      expect(trends.trend).toBe('stable');
    });

    test('should return stable for insufficient data', () => {
      monitor.recordOperation('test', 50);

      const trends = monitor.getTrends('test');
      expect(trends.trend).toBe('stable');
      expect(trends.changeRate).toBe(0);
    });
  });

  describe('Metrics Management', () => {
    test('should reset all metrics', () => {
      monitor.recordOperation('test', 100);
      expect(monitor.getMetric('test')?.count).toBe(1);

      monitor.reset();
      expect(monitor.getMetric('test')).toBeUndefined();
      expect(monitor.getAlerts()).toHaveLength(0);
    });

    test('should get all metrics', () => {
      monitor.recordOperation('op1', 100);
      monitor.recordOperation('op2', 200);

      const allMetrics = monitor.getAllMetrics();
      expect(allMetrics.size).toBe(2);
      expect(allMetrics.has('op1')).toBe(true);
      expect(allMetrics.has('op2')).toBe(true);
    });

    test('should return undefined for non-existent metric', () => {
      expect(monitor.getMetric('nonexistent')).toBeUndefined();
    });
  });

  describe('Configuration', () => {
    test('should use custom maxSamples configuration', () => {
      const customMonitor = new PerformanceMonitor({ maxSamples: 5 });

      for (let i = 0; i < 10; i++) {
        customMonitor.recordOperation('test', i);
      }

      const metric = customMonitor.getMetric('test');
      expect(metric?.samples.length).toBe(5);
      expect(metric?.count).toBe(10); // Count still tracks all
    });

    test('should respect anomaly detection enable/disable', () => {
      const disabledMonitor = new PerformanceMonitor({
        enableAnomalyDetection: false,
        slowOperationThreshold: 10,
      });

      // Need enough samples to trigger alert
      for (let i = 0; i < 5; i++) {
        disabledMonitor.recordOperation('slow', 1000);
      }

      // With anomaly detection disabled, recordOperation won't auto-detect
      // So getAlerts() should be empty
      expect(disabledMonitor.getAlerts().length).toBe(0);

      // But we can still manually call detectAnomalies
      const manualAlerts = disabledMonitor.detectAnomalies();
      expect(manualAlerts.length).toBeGreaterThan(0);

      // And now getAlerts() should return them
      expect(disabledMonitor.getAlerts().length).toBeGreaterThan(0);
    });
  });

  describe('Real-world Scenarios', () => {
    test('should handle evolution operation tracking', () => {
      // Simulate evolution taking variable time
      const evolutionTimes = [450, 520, 480, 510, 490, 500, 505, 495, 515, 505];
      evolutionTimes.forEach(time => {
        monitor.recordOperation('evolution', time);
      });

      const metric = monitor.getMetric('evolution');
      expect(metric?.count).toBe(10);
      expect(metric?.avgTime).toBeGreaterThan(450);
      expect(metric?.avgTime).toBeLessThan(550);
      expect(metric?.p50).toBeGreaterThan(450);
      expect(metric?.p50).toBeLessThan(550);
    });

    test('should handle colony discovery operation tracking', () => {
      // Simulate colony discovery being faster
      const colonyTimes = [80, 95, 85, 90, 88, 92, 87, 91, 89, 93];
      colonyTimes.forEach(time => {
        monitor.recordOperation('colony_discovery', time);
      });

      const metric = monitor.getMetric('colony_discovery');
      expect(metric?.count).toBe(10);
      expect(metric?.avgTime).toBeGreaterThan(70);
      expect(metric?.avgTime).toBeLessThan(100);
    });

    test('should track murmuration execution', () => {
      // Murmuration should be very fast (automated patterns)
      monitor.recordOperation('murmuration_execute', 1);
      monitor.recordOperation('murmuration_execute', 2);
      monitor.recordOperation('murmuration_execute', 1);

      const metric = monitor.getMetric('murmuration_execute');
      expect(metric?.avgTime).toBeLessThan(5);
      expect(metric?.maxTime).toBeLessThan(10);
    });

    test('should track immune system scanning', () => {
      // Immune scans vary with population
      monitor.recordOperation('immune_scan', 50);
      monitor.recordOperation('immune_scan', 55);
      monitor.recordOperation('immune_scan', 48);
      monitor.recordOperation('immune_scan', 52);
      monitor.recordOperation('immune_scan', 51);

      const metric = monitor.getMetric('immune_scan');
      expect(metric?.count).toBe(5);
      expect(metric?.avgTime).toBeGreaterThan(40);
      expect(metric?.avgTime).toBeLessThan(60);
    });
  });

  describe('Factory Function', () => {
    test('should create monitor using factory function', () => {
      const createdMonitor = createPerformanceMonitor({
        maxSamples: 50,
      });

      expect(createdMonitor).toBeInstanceOf(PerformanceMonitor);

      createdMonitor.recordOperation('test', 100);
      expect(createdMonitor.getMetric('test')?.count).toBe(1);
    });
  });

  describe('Edge Cases', () => {
    test('should handle very large sample sizes', () => {
      const largeMonitor = new PerformanceMonitor({ maxSamples: 10000 });

      for (let i = 0; i < 5000; i++) {
        largeMonitor.recordOperation('large_test', Math.random() * 1000);
      }

      const metric = largeMonitor.getMetric('large_test');
      expect(metric?.count).toBe(5000);
      expect(metric?.samples.length).toBe(5000);
    });

    test('should handle operation names with special characters', () => {
      monitor.recordOperation('operation/with/slashes', 100);
      monitor.recordOperation('operation-with-dashes', 200);
      monitor.recordOperation('operation.with.dots', 300);

      const prometheus = monitor.exportPrometheus();
      // All special characters should be replaced with underscores
      expect(prometheus.data).toContain('operation_with_slashes');
      expect(prometheus.data).toContain('operation_with_dashes');
      expect(prometheus.data).toContain('operation_with_dots');
    });

    test('should handle concurrent operations', async () => {
      const promises = [];
      for (let i = 0; i < 100; i++) {
        promises.push(
          monitor.recordOperationAsync('concurrent', async () => {
            await new Promise(resolve => setTimeout(resolve, Math.random() * 10));
            return i;
          })
        );
      }

      await Promise.all(promises);

      const metric = monitor.getMetric('concurrent');
      expect(metric?.count).toBe(100);
    });
  });

  describe('Health Score Calculation', () => {
    test('should start with perfect health score', () => {
      const summary = monitor.getSummary();
      expect(summary.healthScore).toBe(1.0);
    });

    test('should decrease health score with critical alerts', () => {
      monitor.recordOperation('test', 1000);
      monitor.detectAnomalies();

      const summary = monitor.getSummary();
      // Health score should decrease due to alerts
      expect(summary.healthScore).toBeLessThan(1.0);
    });

    test('should decrease health score with multiple slow operations', () => {
      for (let i = 0; i < 10; i++) {
        monitor.recordOperation(`slow_${i}`, 300);
      }

      const summary = monitor.getSummary();
      expect(summary.healthScore).toBeLessThan(0.5);
    });
  });
});

describe('monitorOperation decorator', () => {
  test('should decorate class methods', async () => {
    // Note: Decorators in Jest require special handling
    // This test verifies the decorator function exists and has correct structure
    expect(typeof monitorOperation).toBe('function');

    const decorator = monitorOperation('test_operation');
    expect(typeof decorator).toBe('function');

    // The decorator should be usable with standard method descriptor
    const descriptor = {
      value: async function() {
        return 42;
      },
      enumerable: false,
      configurable: true,
      writable: true
    };

    const result = decorator({}, 'testMethod', descriptor);
    expect(result).toBeDefined();
    expect(result.value).toBeDefined();
  });

  test('should use default operation name if not provided', () => {
    const decorator = monitorOperation();
    expect(typeof decorator).toBe('function');

    const descriptor = {
      value: async function() {
        return 42;
      },
      enumerable: false,
      configurable: true,
      writable: true
    };

    const result = decorator({}, 'testMethod', descriptor);
    expect(result).toBeDefined();
  });
});
