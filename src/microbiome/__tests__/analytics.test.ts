/**
 * POLLN Microbiome - Analytics Pipeline Tests
 *
 * Comprehensive test suite for the analytics pipeline system.
 *
 * @module microbiome/__tests__/analytics.test
 */

import {
  AnalyticsPipeline,
  AnalyticsEventType,
  TimeWindow,
  ReportScope,
  AnomalyType,
  PatternType,
  createAnalyticsPipeline,
  type AnalyticsEvent,
  type AggregatedMetrics,
  type AnalyticsReport,
  type Statistics,
} from '../analytics.js';
import { AgentTaxonomy, ResourceType } from '../types.js';

describe('AnalyticsPipeline', () => {
  let pipeline: AnalyticsPipeline;

  beforeEach(() => {
    pipeline = new AnalyticsPipeline({
      maxEventsInMemory: 1000,
      eventRetentionPeriod: 60000, // 1 minute for testing
      anomalySensitivity: 0.7,
      patternDetectionThreshold: 0.6,
    });
  });

  describe('Event Collection', () => {
    test('should record events successfully', () => {
      const eventId = pipeline.recordEvent(
        AnalyticsEventType.AGENT_BORN,
        { agentId: 'agent1', taxonomy: AgentTaxonomy.BACTERIA }
      );

      expect(eventId).toBeDefined();
      expect(eventId).toMatch(/^evt_\d+_[a-z0-9]+$/);
    });

    test('should store events with correct structure', () => {
      pipeline.recordEvent(
        AnalyticsEventType.AGENT_BORN,
        { agentId: 'agent1', taxonomy: AgentTaxonomy.BACTERIA },
        { source: 'test', tags: ['test-tag'] }
      );

      const events = pipeline['events']; // Access private property for testing
      expect(events).toHaveLength(1);
      expect(events[0].type).toBe(AnalyticsEventType.AGENT_BORN);
      expect(events[0].data.agentId).toBe('agent1');
      expect(events[0].metadata?.source).toBe('test');
      expect(events[0].metadata?.tags).toEqual(['test-tag']);
    });

    test('should enforce max events limit', () => {
      const smallPipeline = new AnalyticsPipeline({ maxEventsInMemory: 5 });

      for (let i = 0; i < 10; i++) {
        smallPipeline.recordEvent(AnalyticsEventType.AGENT_BORN, { agentId: `agent${i}` });
      }

      const stats = smallPipeline.getStats();
      expect(stats.totalEvents).toBe(5);
    });

    test('should clean up old events', async () => {
      jest.useFakeTimers();

      pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, { agentId: 'agent1' });

      // Advance time past retention period
      jest.advanceTimersByTime(120000);

      pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, { agentId: 'agent2' });

      const stats = pipeline.getStats();
      expect(stats.totalEvents).toBe(1); // Only the recent event

      jest.useRealTimers();
    });

    test('should get events by type', () => {
      pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, { agentId: 'agent1' });
      pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, { agentId: 'agent2' });
      pipeline.recordEvent(AnalyticsEventType.AGENT_DIED, { agentId: 'agent1' });

      const bornEvents = pipeline.getEventsByType(AnalyticsEventType.AGENT_BORN);
      const diedEvents = pipeline.getEventsByType(AnalyticsEventType.AGENT_DIED);

      expect(bornEvents).toHaveLength(2);
      expect(diedEvents).toHaveLength(1);
    });

    test('should get events in time range', () => {
      const now = Date.now();
      pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, { timestamp: now - 2000 });
      pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, { timestamp: now - 1000 });
      pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, { timestamp: now });

      const events = pipeline.getEventsInRange(now - 1500, now);
      expect(events.length).toBeGreaterThanOrEqual(1);
    });

    test('should clear all events', () => {
      pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, { agentId: 'agent1' });
      pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, { agentId: 'agent2' });

      pipeline.clearEvents();

      const stats = pipeline.getStats();
      expect(stats.totalEvents).toBe(0);
    });
  });

  describe('Metric Aggregation', () => {
    beforeEach(() => {
      // Seed with test data
      for (let i = 0; i < 20; i++) {
        pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, {
          agentId: `agent${i}`,
          taxonomy: AgentTaxonomy.BACTERIA,
          fitness: { overall: 0.5 + Math.random() * 0.3 },
        });
      }

      for (let i = 0; i < 5; i++) {
        pipeline.recordEvent(AnalyticsEventType.AGENT_DIED, {
          agentId: `agent${i}`,
        });
      }

      for (let i = 0; i < 10; i++) {
        pipeline.recordEvent(AnalyticsEventType.OPERATION_PERFORMED, {
          agentId: `agent${i % 20}`,
          duration: 100 + Math.random() * 200,
          success: Math.random() > 0.1,
        });
      }
    });

    test('should aggregate metrics over time window', () => {
      const metrics = pipeline.aggregateMetrics(TimeWindow.MINUTE);

      expect(metrics).toBeDefined();
      expect(metrics.timestamp).toBeGreaterThan(0);
      expect(metrics.window).toBe(TimeWindow.MINUTE);
      expect(metrics.agentMetrics).toBeInstanceOf(Map);
      expect(metrics.colonyMetrics).toBeInstanceOf(Map);
      expect(metrics.ecosystemMetrics).toBeDefined();
      expect(metrics.timeSeriesData).toBeInstanceOf(Array);
    });

    test('should calculate ecosystem-level metrics', () => {
      const metrics = pipeline.aggregateMetrics(TimeWindow.MINUTE);
      const ecoMetrics = metrics.ecosystemMetrics;

      expect(ecoMetrics.totalAgents).toBe(20);
      expect(ecoMetrics.populationByTaxonomy.get(AgentTaxonomy.BACTERIA)).toBe(20);
      expect(ecoMetrics.diversity).toBeGreaterThanOrEqual(0);
      expect(ecoMetrics.healthScore).toBeGreaterThanOrEqual(0);
      expect(ecoMetrics.healthScore).toBeLessThanOrEqual(1);
    });

    test('should calculate birth and death rates', () => {
      const metrics = pipeline.aggregateMetrics(TimeWindow.MINUTE);
      const ecoMetrics = metrics.ecosystemMetrics;

      expect(ecoMetrics.birthRate).toBeGreaterThan(0);
      expect(ecoMetrics.deathRate).toBeGreaterThan(0);
      expect(ecoMetrics.growthRate).toBeDefined();
    });

    test('should calculate time-series data with statistics', () => {
      const metrics = pipeline.aggregateMetrics(TimeWindow.MINUTE);

      expect(metrics.timeSeriesData.length).toBeGreaterThan(0);

      for (const ts of metrics.timeSeriesData) {
        expect(ts.metric).toBeDefined();
        expect(ts.points).toBeInstanceOf(Array);
        expect(ts.stats.count).toBeGreaterThan(0);
        expect(ts.stats.avg).toBeDefined();
        expect(ts.stats.min).toBeLessThanOrEqual(ts.stats.max);
        expect(ts.stats.p50).toBeDefined();
        expect(ts.stats.p95).toBeDefined();
        expect(ts.stats.p99).toBeDefined();
        expect(ts.stats.variance).toBeGreaterThanOrEqual(0);
        expect(ts.stats.stdDev).toBeGreaterThanOrEqual(0);
      }
    });

    test('should cache aggregated metrics', () => {
      const metrics1 = pipeline.aggregateMetrics(TimeWindow.MINUTE);
      const metrics2 = pipeline.getCachedMetrics(TimeWindow.MINUTE);

      expect(metrics2).toBeDefined();
      expect(metrics2.timestamp).toBe(metrics1.timestamp);
    });

    test('should calculate agent-level metrics', () => {
      const metrics = pipeline.aggregateMetrics(TimeWindow.MINUTE);

      expect(metrics.agentMetrics.size).toBeGreaterThan(0);

      for (const [agentId, agentMetrics] of metrics.agentMetrics.entries()) {
        expect(agentMetrics.agentId).toBe(agentId);
        expect(agentMetrics.taxonomy).toBeDefined();
        expect(agentMetrics.fitness.overall).toBeGreaterThanOrEqual(0);
        expect(agentMetrics.fitness.overall).toBeLessThanOrEqual(1);
        expect(agentMetrics.processing.totalOperations).toBeGreaterThanOrEqual(0);
        expect(agentMetrics.lifecycle.isAlive).toBeDefined();
      }
    });
  });

  describe('Statistical Analysis', () => {
    test('should compute descriptive statistics', () => {
      const values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
      const stats = pipeline.computeStatistics(values);

      expect(stats.descriptive.mean).toBeCloseTo(5.5);
      expect(stats.descriptive.median).toBeCloseTo(5.5);
      expect(stats.descriptive.variance).toBeGreaterThan(0);
      expect(stats.descriptive.standardDeviation).toBeGreaterThan(0);
      expect(stats.descriptive.skewness).toBeDefined();
      expect(stats.descriptive.kurtosis).toBeDefined();
    });

    test('should calculate percentiles correctly', () => {
      const values = Array.from({ length: 100 }, (_, i) => i + 1);
      const stats = pipeline.computeStatistics(values);

      // Using linear interpolation method for percentiles
      expect(stats.percentiles.p25).toBeGreaterThan(25);
      expect(stats.percentiles.p25).toBeLessThan(26);
      expect(stats.percentiles.p50).toBeGreaterThan(50);
      expect(stats.percentiles.p50).toBeLessThan(52);
      expect(stats.percentiles.p75).toBeGreaterThan(75);
      expect(stats.percentiles.p75).toBeLessThan(76);
      expect(stats.percentiles.p90).toBeGreaterThan(90);
      expect(stats.percentiles.p90).toBeLessThan(91);
      expect(stats.percentiles.p95).toBeGreaterThan(95);
      expect(stats.percentiles.p95).toBeLessThan(96);
      expect(stats.percentiles.p99).toBeGreaterThan(99);
      expect(stats.percentiles.p99).toBeLessThan(100);
    });

    test('should detect outliers', () => {
      const values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]; // 100 is an outlier
      const stats = pipeline.computeStatistics(values);

      expect(stats.distribution.outliers.length).toBeGreaterThan(0);
      expect(stats.distribution.outliers).toContain(100);
    });

    test('should handle empty values', () => {
      const stats = pipeline.computeStatistics([]);

      expect(stats.descriptive.mean).toBe(0);
      expect(stats.descriptive.variance).toBe(0);
      expect(stats.distribution.outliers).toEqual([]);
    });

    test('should handle single value', () => {
      const stats = pipeline.computeStatistics([42]);

      expect(stats.descriptive.mean).toBe(42);
      expect(stats.descriptive.median).toBe(42);
      expect(stats.descriptive.mode).toBe(42);
      expect(stats.descriptive.variance).toBe(0);
    });
  });

  describe('Trend Analysis', () => {
    test('should detect increasing trend', () => {
      const data: TimeSeriesData = {
        metric: 'test_metric',
        points: Array.from({ length: 20 }, (_, i) => ({
          timestamp: Date.now() + i * 1000,
          metric: 'test_metric',
          value: i * 10,
        })),
        stats: {
          count: 20,
          sum: 1900,
          avg: 95,
          min: 0,
          max: 190,
          p50: 95,
          p95: 180.5,
          p99: 188.1,
          variance: 0,
          stdDev: 0,
        },
      };

      const trend = pipeline.analyzeTimeSeries(data);

      expect(trend.direction).toBe('increasing');
      expect(trend.strength).toBeCloseTo(1);
      expect(trend.rateOfChange).toBeGreaterThan(0);
    });

    test('should detect decreasing trend', () => {
      const data: TimeSeriesData = {
        metric: 'test_metric',
        points: Array.from({ length: 20 }, (_, i) => ({
          timestamp: Date.now() + i * 1000,
          metric: 'test_metric',
          value: 200 - i * 10,
        })),
        stats: {
          count: 20,
          sum: 2100,
          avg: 105,
          min: 10,
          max: 200,
          p50: 105,
          p95: 195,
          p99: 198,
          variance: 0,
          stdDev: 0,
        },
      };

      const trend = pipeline.analyzeTimeSeries(data);

      expect(trend.direction).toBe('decreasing');
      expect(trend.strength).toBeCloseTo(1);
      expect(trend.rateOfChange).toBeLessThan(0);
    });

    test('should detect stable trend', () => {
      const constantValue = 50;
      const data: TimeSeriesData = {
        metric: 'test_metric',
        points: Array.from({ length: 20 }, (_, i) => ({
          timestamp: Date.now() + i * 1000,
          metric: 'test_metric',
          value: constantValue,
        })),
        stats: {
          count: 20,
          sum: 1000,
          avg: constantValue,
          min: constantValue,
          max: constantValue,
          p50: constantValue,
          p95: constantValue,
          p99: constantValue,
          variance: 0,
          stdDev: 0,
        },
      };

      const trend = pipeline.analyzeTimeSeries(data);

      expect(trend.direction).toBe('stable');
    });

    test('should generate predictions', () => {
      const data: TimeSeriesData = {
        metric: 'test_metric',
        points: Array.from({ length: 20 }, (_, i) => ({
          timestamp: Date.now() + i * 1000,
          metric: 'test_metric',
          value: i * 10,
        })),
        stats: {
          count: 20,
          sum: 1900,
          avg: 95,
          min: 0,
          max: 190,
          p50: 95,
          p95: 180.5,
          p99: 188.1,
          variance: 0,
          stdDev: 0,
        },
      };

      const trend = pipeline.analyzeTimeSeries(data);

      expect(trend.prediction).toBeDefined();
      expect(trend.prediction).toHaveLength(5);
      expect(trend.confidenceInterval).toBeDefined();
    });
  });

  describe('Anomaly Detection', () => {
    beforeEach(() => {
      // Create normal population
      for (let i = 0; i < 50; i++) {
        pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, {
          agentId: `agent${i}`,
          taxonomy: AgentTaxonomy.BACTERIA,
        });
      }

      // Create normal death rate
      for (let i = 0; i < 5; i++) {
        pipeline.recordEvent(AnalyticsEventType.AGENT_DIED, {
          agentId: `agent${i}`,
        });
      }
    });

    test('should detect population crash', () => {
      // Simulate massive die-off - MORE deaths than births
      for (let i = 0; i < 60; i++) { // 60 deaths vs 50 births = actual crash
        pipeline.recordEvent(AnalyticsEventType.AGENT_DIED, {
          agentId: `agent${i}`,
        });
      }

      // Use HOUR window instead of MINUTE to capture all events
      const metrics = pipeline.aggregateMetrics(TimeWindow.HOUR);
      const anomalies = pipeline.detectAnomalies(metrics);

      const crashAnomaly = anomalies.find(a => a.type === AnomalyType.POPULATION_CRASH);
      expect(crashAnomaly).toBeDefined();
      expect(crashAnomaly?.severity).toBeGreaterThan(0.5);
    });

    test('should detect population explosion', () => {
      // Simulate rapid reproduction
      for (let i = 0; i < 100; i++) {
        pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, {
          agentId: `new_agent${i}`,
          taxonomy: AgentTaxonomy.BACTERIA,
        });
      }

      const metrics = pipeline.aggregateMetrics(TimeWindow.MINUTE);
      const anomalies = pipeline.detectAnomalies(metrics);

      const explosionAnomaly = anomalies.find(a => a.type === AnomalyType.POPULATION_EXPLOSION);
      expect(explosionAnomaly).toBeDefined();
    });

    test('should detect performance degradation', () => {
      // Record slow operations
      for (let i = 0; i < 10; i++) {
        pipeline.recordEvent(AnalyticsEventType.OPERATION_PERFORMED, {
          agentId: `agent${i}`,
          operation: 'test_operation',
          duration: 10000, // 10 seconds - very slow
          success: true,
        });
      }

      const metrics = pipeline.aggregateMetrics(TimeWindow.MINUTE);
      const anomalies = pipeline.detectAnomalies(metrics);

      const perfAnomaly = anomalies.find(a => a.type === AnomalyType.PERFORMANCE_DEGRADATION);
      expect(perfAnomaly).toBeDefined();
    });

    test('should provide suggested actions for anomalies', () => {
      for (let i = 0; i < 40; i++) {
        pipeline.recordEvent(AnalyticsEventType.AGENT_DIED, {
          agentId: `agent${i}`,
        });
      }

      const metrics = pipeline.aggregateMetrics(TimeWindow.MINUTE);
      const anomalies = pipeline.detectAnomalies(metrics);

      for (const anomaly of anomalies) {
        if (anomaly.severity > 0.5) {
          expect(anomaly.suggestedActions).toBeDefined();
          expect(anomaly.suggestedActions?.length).toBeGreaterThan(0);
        }
      }
    });
  });

  describe('Correlation Analysis', () => {
    test('should detect positive correlation', () => {
      // Record correlated events
      for (let i = 0; i < 20; i++) {
        pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, {
          agentId: `agent${i}`,
          fitness: i,
          throughput: i * 2,
        });
      }

      const metrics = pipeline.aggregateMetrics(TimeWindow.MINUTE);
      const correlations = pipeline.analyzeCorrelations(metrics);

      expect(correlations.length).toBeGreaterThan(0);
    });

    test('should detect negative correlation', () => {
      // Record negatively correlated events
      for (let i = 0; i < 20; i++) {
        pipeline.recordEvent(AnalyticsEventType.OPERATION_PERFORMED, {
          agentId: `agent${i}`,
          duration: 1000 - i * 10,
          efficiency: i * 5,
        });
      }

      const metrics = pipeline.aggregateMetrics(TimeWindow.MINUTE);
      const correlations = pipeline.analyzeCorrelations(metrics);

      const negativeCorr = correlations.find(c => c.direction === 'negative');
      expect(negativeCorr).toBeDefined();
    });
  });

  describe('Report Generation', () => {
    beforeEach(() => {
      // Seed with diverse test data
      for (let i = 0; i < 30; i++) {
        pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, {
          agentId: `agent${i}`,
          taxonomy: Object.values(AgentTaxonomy)[i % 5],
          fitness: {
            overall: 0.3 + Math.random() * 0.6,
            throughput: Math.random(),
            accuracy: Math.random(),
            efficiency: Math.random(),
            cooperation: Math.random(),
          },
        });
      }

      for (let i = 0; i < 5; i++) {
        pipeline.recordEvent(AnalyticsEventType.AGENT_DIED, {
          agentId: `agent${i}`,
        });
      }

      for (let i = 0; i < 3; i++) {
        pipeline.recordEvent(AnalyticsEventType.COLONY_FORMED, {
          colonyId: `colony${i}`,
          memberCount: 10 + i * 5,
          stability: 0.5 + Math.random() * 0.5,
          coEvolutionBonus: 0.1 + Math.random() * 0.2,
        });
      }
    });

    test('should generate full analytics report', () => {
      const report = pipeline.generateReport(ReportScope.FULL);

      expect(report.id).toBeDefined();
      expect(report.timestamp).toBeDefined();
      expect(report.scope).toBe(ReportScope.FULL);
      expect(report.timeRange).toBeDefined();
      expect(report.metrics).toBeDefined();
      expect(report.statistics).toBeInstanceOf(Map);
      expect(report.patterns).toBeInstanceOf(Array);
      expect(report.anomalies).toBeInstanceOf(Array);
      expect(report.correlations).toBeInstanceOf(Array);
      expect(report.trends).toBeInstanceOf(Map);
      expect(report.insights).toBeInstanceOf(Array);
    });

    test('should generate actionable insights', () => {
      const report = pipeline.generateReport(ReportScope.FULL);

      expect(report.insights.length).toBeGreaterThan(0);

      for (const insight of report.insights) {
        expect(insight).toBeDefined();
        expect(typeof insight).toBe('string');
        expect(insight.length).toBeGreaterThan(0);
      }
    });

    test('should respect time range in report', () => {
      const now = Date.now();
      const timeRange = {
        start: now - 30000, // 30 seconds ago
        end: now,
      };

      const report = pipeline.generateReport(ReportScope.FULL, timeRange);

      expect(report.timeRange.start).toBe(timeRange.start);
      expect(report.timeRange.end).toBe(timeRange.end);
    });

    test('should include diversity metrics in insights', () => {
      const report = pipeline.generateReport(ReportScope.FULL);

      const diversityInsight = report.insights.find(i =>
        i.toLowerCase().includes('diversity')
      );
      expect(diversityInsight).toBeDefined();
    });

    test('should include health score in insights', () => {
      const report = pipeline.generateReport(ReportScope.FULL);

      const healthInsight = report.insights.find(i =>
        i.toLowerCase().includes('health')
      );
      expect(healthInsight).toBeDefined();
    });
  });

  describe('Event Sources', () => {
    test('should register event source', () => {
      const source = {
        id: 'test_source',
        type: 'ecosystem' as const,
        config: {},
        active: true,
      };

      pipeline.registerSource(source);

      const stats = pipeline.getStats();
      expect(stats.registeredSources).toBe(1);
    });

    test('should unregister event source', () => {
      const source = {
        id: 'test_source',
        type: 'ecosystem' as const,
        config: {},
        active: true,
      };

      pipeline.registerSource(source);
      expect(pipeline.getStats().registeredSources).toBe(1);

      pipeline.unregisterSource('test_source');
      expect(pipeline.getStats().registeredSources).toBe(0);
    });

    test('should collect events from active source', () => {
      const source = {
        id: 'test_source',
        type: 'ecosystem' as const,
        config: {},
        active: true,
      };

      pipeline.registerSource(source);
      const events = pipeline.collectEvents(source);

      expect(events).toBeInstanceOf(Array);
    });
  });

  describe('Pipeline Statistics', () => {
    beforeEach(() => {
      for (let i = 0; i < 10; i++) {
        pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, { agentId: `agent${i}` });
      }
      for (let i = 0; i < 3; i++) {
        pipeline.recordEvent(AnalyticsEventType.AGENT_DIED, { agentId: `agent${i}` });
      }
    });

    test('should return pipeline statistics', () => {
      const stats = pipeline.getStats();

      expect(stats.totalEvents).toBe(13);
      expect(stats.eventsByType.get(AnalyticsEventType.AGENT_BORN)).toBe(10);
      expect(stats.eventsByType.get(AnalyticsEventType.AGENT_DIED)).toBe(3);
      expect(stats.registeredSources).toBe(0);
      expect(stats.uptime).toBeGreaterThanOrEqual(0); // Can be 0 in fast tests
    });

    test('should track last aggregation time', () => {
      pipeline.aggregateMetrics(TimeWindow.MINUTE);

      const stats = pipeline.getStats();
      expect(stats.lastAggregation).toBeGreaterThan(0);
    });
  });

  describe('Pattern Detection', () => {
    test('should detect patterns in behavior data', () => {
      // Create oscillating pattern
      for (let i = 0; i < 20; i++) {
        pipeline.recordEvent(AnalyticsEventType.OPERATION_PERFORMED, {
          agentId: 'agent1',
          duration: 100 + Math.sin(i) * 50,
          success: true,
        });
      }

      const events = pipeline.getEventsByType(AnalyticsEventType.OPERATION_PERFORMED);
      const patterns = pipeline.detectPatterns(events);

      expect(patterns).toBeInstanceOf(Array);
    });
  });

  describe('Integration with Ecosystem', () => {
    test('should integrate with DigitalTerrarium events', () => {
      // Simulate ecosystem events
      const ecosystemEvents = [
        { type: AnalyticsEventType.AGENT_BORN, data: { agentId: 'agent1', taxonomy: AgentTaxonomy.BACTERIA } },
        { type: AnalyticsEventType.COLONY_FORMED, data: { colonyId: 'colony1', memberCount: 10 } },
        { type: AnalyticsEventType.SYMBIOSIS_FORMED, data: { sourceId: 'agent1', targetId: 'agent2' } },
      ];

      for (const event of ecosystemEvents) {
        pipeline.recordEvent(event.type, event.data);
      }

      const report = pipeline.generateReport(ReportScope.FULL);

      expect(report.metrics.ecosystemMetrics.totalAgents).toBe(1);
      expect(report.insights.length).toBeGreaterThan(0);
    });
  });

  describe('Edge Cases', () => {
    test('should handle no events gracefully', () => {
      const emptyPipeline = new AnalyticsPipeline();
      const report = emptyPipeline.generateReport(ReportScope.FULL);

      expect(report).toBeDefined();
      expect(report.metrics.ecosystemMetrics.totalAgents).toBe(0);
    });

    test('should handle single event', () => {
      pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, {
        agentId: 'agent1',
        taxonomy: AgentTaxonomy.BACTERIA,
      });

      const metrics = pipeline.aggregateMetrics(TimeWindow.MINUTE);

      expect(metrics.ecosystemMetrics.totalAgents).toBe(1);
    });

    test('should handle very large values', () => {
      pipeline.recordEvent(AnalyticsEventType.OPERATION_PERFORMED, {
        duration: Number.MAX_SAFE_INTEGER,
        success: true,
      });

      const metrics = pipeline.aggregateMetrics(TimeWindow.MINUTE);
      const tsData = metrics.timeSeriesData.find(ts => ts.metric.includes('duration'));

      expect(tsData).toBeDefined();
      expect(tsData?.stats.max).toBe(Number.MAX_SAFE_INTEGER);
    });

    test('should handle negative values', () => {
      pipeline.recordEvent(AnalyticsEventType.OPERATION_PERFORMED, {
        delta: -100,
        success: true,
      });

      const stats = pipeline.getStats();
      expect(stats.totalEvents).toBe(1);
    });
  });

  describe('Performance', () => {
    test('should handle large number of events efficiently', () => {
      const startTime = Date.now();

      for (let i = 0; i < 1000; i++) {
        pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, {
          agentId: `agent${i}`,
          taxonomy: AgentTaxonomy.BACTERIA,
        });
      }

      const recordTime = Date.now() - startTime;
      expect(recordTime).toBeLessThan(1000); // Should complete in less than 1 second

      const aggStart = Date.now();
      pipeline.aggregateMetrics(TimeWindow.HOUR);
      const aggTime = Date.now() - aggStart;

      expect(aggTime).toBeLessThan(2000); // Should complete in less than 2 seconds
    });

    test('should maintain memory efficiency', () => {
      const limitedPipeline = new AnalyticsPipeline({ maxEventsInMemory: 100 });

      for (let i = 0; i < 200; i++) {
        limitedPipeline.recordEvent(AnalyticsEventType.AGENT_BORN, { agentId: `agent${i}` });
      }

      const stats = limitedPipeline.getStats();
      expect(stats.totalEvents).toBe(100); // Should not exceed limit
    });
  });
});

describe('createAnalyticsPipeline', () => {
  test('should create pipeline with default config', () => {
    const pipeline = createAnalyticsPipeline();

    expect(pipeline).toBeInstanceOf(AnalyticsPipeline);
    expect(pipeline.getStats().totalEvents).toBe(0);
  });

  test('should create pipeline with custom config', () => {
    const pipeline = createAnalyticsPipeline({
      maxEventsInMemory: 500,
      anomalySensitivity: 0.8,
    });

    expect(pipeline).toBeInstanceOf(AnalyticsPipeline);

    // Verify config by testing behavior
    for (let i = 0; i < 600; i++) {
      pipeline.recordEvent(AnalyticsEventType.AGENT_BORN, { agentId: `agent${i}` });
    }

    const stats = pipeline.getStats();
    expect(stats.totalEvents).toBe(500); // Should respect custom limit
  });
});

describe('Analytics Integration', () => {
  test('should work with colony metrics', () => {
    const pipeline = new AnalyticsPipeline();

    pipeline.recordEvent(AnalyticsEventType.COLONY_FORMED, {
      colonyId: 'colony1',
      memberCount: 50,
      stability: 0.8,
      coEvolutionBonus: 0.15,
    });

    const metrics = pipeline.aggregateMetrics(TimeWindow.MINUTE);
    const colonyMetrics = metrics.colonyMetrics.get('colony1');

    expect(colonyMetrics).toBeDefined();
    expect(colonyMetrics?.memberCount).toBe(50);
    expect(colonyMetrics?.stability).toBe(0.8);
  });

  test('should track resource events', () => {
    const pipeline = new AnalyticsPipeline();

    pipeline.recordEvent(AnalyticsEventType.RESOURCE_CONSUMED, {
      resource: ResourceType.COMPUTE,
      amount: 100,
    });

    pipeline.recordEvent(AnalyticsEventType.RESOURCE_PRODUCED, {
      resource: ResourceType.COMPUTE,
      amount: 50,
    });

    const stats = pipeline.getStats();
    expect(stats.totalEvents).toBe(2);
  });
});
