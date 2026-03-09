/**
 * POLLN Microbiome - Analytics Pipeline
 *
 * Phase 10: Observability & Intelligence - Milestone 1
 * Comprehensive analytics system for collecting, aggregating, and analyzing
 * ecosystem data to generate actionable insights.
 *
 * @module microbiome/analytics
 */

import {
  MicrobiomeAgent,
  AgentTaxonomy,
  ResourceType,
  ColonyStructure,
  Symbiosis,
  EcosystemSnapshot,
} from './types.js';
import { EcosystemEvent } from './ecosystem.js';

/**
 * Analytics event types
 */
export enum AnalyticsEventType {
  // Agent events
  AGENT_BORN = 'analytics_agent_born',
  AGENT_DIED = 'analytics_agent_died',
  AGENT_REPRODUCED = 'analytics_agent_reproduced',
  AGENT_MUTATED = 'analytics_agent_mutated',
  AGENT_FITNESS = 'analytics_agent_fitness',

  // Colony events
  COLONY_FORMED = 'analytics_colony_formed',
  COLONY_DISSOLVED = 'analytics_colony_dissolved',
  COLONY_MERGED = 'analytics_colony_merged',
  COLONY_STABILITY = 'analytics_colony_stability',

  // Symbiosis events
  SYMBIOSIS_FORMED = 'analytics_symbiosis_formed',
  SYMBIOSIS_BROKEN = 'analytics_symbiosis_broken',
  SYMBIOSIS_EVOLVED = 'analytics_symbiosis_evolved',

  // Resource events
  RESOURCE_CONSUMED = 'analytics_resource_consumed',
  RESOURCE_PRODUCED = 'analytics_resource_produced',
  RESOURCE_DEPLETED = 'analytics_resource_depleted',

  // Performance events
  OPERATION_PERFORMED = 'analytics_operation_performed',
  ANOMALY_DETECTED = 'analytics_anomaly_detected',

  // System events
  ECOSYSTEM_TICK = 'analytics_ecosystem_tick',
  ECOSYSTEM_SNAPSHOT = 'analytics_ecosystem_snapshot',
}

/**
 * Base analytics event
 */
export interface AnalyticsEvent {
  /** Unique event ID */
  id: string;
  /** Event type */
  type: AnalyticsEventType;
  /** Timestamp */
  timestamp: number;
  /** Event data */
  data: Record<string, any>;
  /** Metadata */
  metadata?: {
    source?: string;
    tags?: string[];
    correlationId?: string;
  };
}

/**
 * Event source configuration
 */
export interface EventSource {
  /** Source identifier */
  id: string;
  /** Source type */
  type: 'ecosystem' | 'colony' | 'agent' | 'external';
  /** Source configuration */
  config: Record<string, any>;
  /** Is source active */
  active: boolean;
}

/**
 * Time window for aggregations
 */
export enum TimeWindow {
  SECOND = 1000,
  MINUTE = 60000,
  FIVE_MINUTES = 300000,
  FIFTEEN_MINUTES = 900000,
  HOUR = 3600000,
  SIX_HOURS = 21600000,
  DAY = 86400000,
}

/**
 * Aggregated metrics
 */
export interface AggregatedMetrics {
  /** Timestamp of aggregation */
  timestamp: number;
  /** Time window */
  window: TimeWindow;
  /** Agent-level metrics */
  agentMetrics: Map<string, AgentMetrics>;
  /** Colony-level metrics */
  colonyMetrics: Map<string, ColonyMetrics>;
  /** Ecosystem-level metrics */
  ecosystemMetrics: EcosystemMetrics;
  /** Time-series data points */
  timeSeriesData: TimeSeriesData[];
}

/**
 * Agent-level metrics
 */
export interface AgentMetrics {
  /** Agent ID */
  agentId: string;
  /** Agent taxonomy */
  taxonomy: AgentTaxonomy;
  /** Current fitness score */
  fitness: {
    overall: number;
    throughput: number;
    accuracy: number;
    efficiency: number;
    cooperation: number;
  };
  /** Processing statistics */
  processing: {
    totalOperations: number;
    successfulOperations: number;
    failedOperations: number;
    avgProcessingTime: number;
    totalProcessingTime: number;
  };
  /** Metabolic efficiency */
  metabolism: {
    efficiency: number;
    processingRate: number;
    resourcesConsumed: number;
    resourcesProduced: number;
  };
  /** Lifecycle metrics */
  lifecycle: {
    age: number;
    generation: number;
    health: number;
    isAlive: boolean;
  };
  /** Communication metrics */
  communication: {
    messagesSent: number;
    messagesReceived: number;
    symbioses: number;
  };
}

/**
 * Colony-level metrics
 */
export interface ColonyMetrics {
  /** Colony ID */
  colonyId: string;
  /** Member count */
  memberCount: number;
  /** Stability score */
  stability: number;
  /** Co-evolution bonus */
  coEvolutionBonus: number;
  /** Communication efficiency */
  communicationEfficiency: number;
  /** Average member fitness */
  avgMemberFitness: number;
  /** Colony age */
  age: number;
  /** Formation time */
  formationTime: number;
}

/**
 * Ecosystem-level metrics
 */
export interface EcosystemMetrics {
  /** Total agent count */
  totalAgents: number;
  /** Population by taxonomy */
  populationByTaxonomy: Map<AgentTaxonomy, number>;
  /** Diversity index (Shannon entropy) */
  diversity: number;
  /** System health score */
  healthScore: number;
  /** Resource availability */
  resourceAvailability: Map<ResourceType, number>;
  /** Active colonies count */
  activeColonies: number;
  /** Active symbioses count */
  activeSymbioses: number;
  /** Birth/death rates */
  birthRate: number;
  deathRate: number;
  /** Population growth rate */
  growthRate: number;
}

/**
 * Time-series data point
 */
export interface TimeSeriesDataPoint {
  /** Timestamp */
  timestamp: number;
  /** Metric name */
  metric: string;
  /** Value */
  value: number;
  /** Labels/tags */
  labels?: Record<string, string>;
}

/**
 * Time-series data collection
 */
export interface TimeSeriesData {
  /** Metric name */
  metric: string;
  /** Data points */
  points: TimeSeriesDataPoint[];
  /** Aggregation statistics */
  stats: {
    count: number;
    sum: number;
    avg: number;
    min: number;
    max: number;
    p50: number;
    p95: number;
    p99: number;
    variance: number;
    stdDev: number;
  };
}

/**
 * Statistical analysis results
 */
export interface Statistics {
  /** Descriptive statistics */
  descriptive: {
    mean: number;
    median: number;
    mode: number;
    variance: number;
    standardDeviation: number;
    skewness: number;
    kurtosis: number;
  };
  /** Percentile values */
  percentiles: {
    p25: number;
    p50: number;
    p75: number;
    p90: number;
    p95: number;
    p99: number;
  };
  /** Distribution info */
  distribution: {
    min: number;
    max: number;
    range: number;
    outliers: number[];
  };
}

/**
 * Pattern detection result
 */
export interface Pattern {
  /** Pattern ID */
  id: string;
  /** Pattern type */
  type: PatternType;
  /** Confidence score (0-1) */
  confidence: number;
  /** Pattern description */
  description: string;
  /** Pattern data */
  data: Record<string, any>;
  /** Detected at */
  detectedAt: number;
  /** Pattern duration */
  duration?: number;
}

/**
 * Pattern types
 */
export enum PatternType {
  // Behavioral patterns
  BEHAVIORAL_SPIRAL = 'behavioral_spiral',
  BEHAVIORAL_OSCILLATION = 'behavioral_oscillation',
  BEHAVIORAL_TREND = 'behavioral_trend',

  // Communication patterns
  COMMUNICATION_CLUSTER = 'communication_cluster',
  COMMUNICATION_HUB = 'communication_hub',
  COMMUNICATION_PATH = 'communication_path',

  // Evolutionary patterns
  EVOLUTIONARY_CONVERGENCE = 'evolutionary_convergence',
  EVOLUTIONARY_DIVERGENCE = 'evolutionary_divergence',
  EVOLUTIONARY_STAGNATION = 'evolutionary_stagnation',

  // Resource patterns
  RESOURCE_CYCLE = 'resource_cycle',
  RESOURCE_SHORTAGE = 'resource_shortage',
  RESOURCE_SURPLUS = 'resource_surplus',

  // Colony patterns
  COLONY_MERGER = 'colony_merger',
  COLONY_SPLIT = 'colony_split',
  COLONY_MIGRATION = 'colony_migration',
}

/**
 * Anomaly detection result
 */
export interface Anomaly {
  /** Anomaly ID */
  id: string;
  /** Anomaly type */
  type: AnomalyType;
  /** Severity (0-1) */
  severity: number;
  /** Description */
  description: string;
  /** Affected entities */
  affectedEntities: string[];
  /** Anomaly value */
  value: number;
  /** Expected range */
  expectedRange: [number, number];
  /** Detected at */
  detectedAt: number;
  /** Suggested actions */
  suggestedActions?: string[];
}

/**
 * Anomaly types
 */
export enum AnomalyType {
  // Performance anomalies
  PERFORMANCE_DEGRADATION = 'performance_degradation',
  PERFORMANCE_SPIKE = 'performance_spike',
  PERFORMANCE_REGRESSION = 'performance_regression',

  // Population anomalies
  POPULATION_CRASH = 'population_crash',
  POPULATION_EXPLOSION = 'population_explosion',
  POPULATION_IMBALANCE = 'population_imbalance',

  // Resource anomalies
  RESOURCE_EXHAUSTION = 'resource_exhaustion',
  RESOURCE_LEAK = 'resource_leak',

  // Behavioral anomalies
  BEHAVIORAL_ABNORMALITY = 'behavioral_abnormality',
  COMMUNICATION_ABNORMALITY = 'communication_abnormality',

  // Colony anomalies
  COLONY_INSTABILITY = 'colony_instability',
  COLONY_ISOLATION = 'colony_isolation',
}

/**
 * Correlation analysis result
 */
export interface Correlation {
  /** Metric 1 */
  metric1: string;
  /** Metric 2 */
  metric2: string;
  /** Correlation coefficient (-1 to 1) */
  coefficient: number;
  /** Strength (weak, moderate, strong) */
  strength: 'weak' | 'moderate' | 'strong';
  /** Direction (positive, negative, none) */
  direction: 'positive' | 'negative' | 'none';
  /** P-value (statistical significance) */
  pValue?: number;
}

/**
 * Trend analysis result
 */
export interface TrendAnalysis {
  /** Metric name */
  metric: string;
  /** Trend direction */
  direction: 'increasing' | 'decreasing' | 'stable';
  /** Trend strength (0-1) */
  strength: number;
  /** Rate of change */
  rateOfChange: number;
  /** Prediction (next n points) */
  prediction?: number[];
  /** Confidence interval */
  confidenceInterval?: [number, number];
}

/**
 * Analytics report
 */
export interface AnalyticsReport {
  /** Report ID */
  id: string;
  /** Report timestamp */
  timestamp: number;
  /** Report scope */
  scope: ReportScope;
  /** Time range */
  timeRange: {
    start: number;
    end: number;
  };
  /** Aggregated metrics */
  metrics: AggregatedMetrics;
  /** Statistical analysis */
  statistics: Map<string, Statistics>;
  /** Detected patterns */
  patterns: Pattern[];
  /** Detected anomalies */
  anomalies: Anomaly[];
  /** Correlations */
  correlations: Correlation[];
  /** Trend analysis */
  trends: Map<string, TrendAnalysis>;
  /** Summary insights */
  insights: string[];
}

/**
 * Report scope
 */
export enum ReportScope {
  AGENT = 'agent',
  COLONY = 'colony',
  ECOSYSTEM = 'ecosystem',
  FULL = 'full',
}

/**
 * Analytics pipeline configuration
 */
export interface AnalyticsPipelineConfig {
  /** Maximum events to keep in memory */
  maxEventsInMemory?: number;
  /** Event retention period (ms) */
  eventRetentionPeriod?: number;
  /** Enable real-time streaming */
  enableStreaming?: boolean;
  /** Streaming callback */
  streamingCallback?: (event: AnalyticsEvent) => void;
  /** Anomaly detection sensitivity (0-1) */
  anomalySensitivity?: number;
  /** Pattern detection threshold (0-1) */
  patternDetectionThreshold?: number;
  /** Enable predictive analytics */
  enablePrediction?: boolean;
}

/**
 * Analytics Pipeline - Main class for collecting, aggregating, and analyzing data
 */
export class AnalyticsPipeline {
  /** Event buffer */
  private events: AnalyticsEvent[];
  /** Event sources */
  private sources: Map<string, EventSource>;
  /** Configuration */
  private config: Required<AnalyticsPipelineConfig>;
  /** Aggregated metrics cache */
  private metricsCache: Map<TimeWindow, AggregatedMetrics>;
  /** Pattern detector */
  private patternDetector: PatternDetector;
  /** Anomaly detector */
  private anomalyDetector: AnomalyDetector;
  /** Statistical analyzer */
  private statisticalAnalyzer: StatisticalAnalyzer;
  /** Correlation analyzer */
  private correlationAnalyzer: CorrelationAnalyzer;
  /** Pipeline start time */
  private startTime: number;
  /** Last aggregation time */
  private lastAggregationTime: number;

  constructor(config: AnalyticsPipelineConfig = {}) {
    this.events = [];
    this.sources = new Map();
    this.metricsCache = new Map();
    this.startTime = Date.now();
    this.lastAggregationTime = 0;

    this.config = {
      maxEventsInMemory: config.maxEventsInMemory ?? 10000,
      eventRetentionPeriod: config.eventRetentionPeriod ?? 24 * 60 * 60 * 1000, // 24 hours
      enableStreaming: config.enableStreaming ?? false,
      streamingCallback: config.streamingCallback ?? (() => {}),
      anomalySensitivity: config.anomalySensitivity ?? 0.7,
      patternDetectionThreshold: config.patternDetectionThreshold ?? 0.6,
      enablePrediction: config.enablePrediction ?? true,
    };

    this.patternDetector = new PatternDetector(this.config.patternDetectionThreshold);
    this.anomalyDetector = new AnomalyDetector(this.config.anomalySensitivity);
    this.statisticalAnalyzer = new StatisticalAnalyzer();
    this.correlationAnalyzer = new CorrelationAnalyzer();
  }

  /**
   * Register an event source
   */
  registerSource(source: EventSource): void {
    this.sources.set(source.id, source);
  }

  /**
   * Unregister an event source
   */
  unregisterSource(sourceId: string): boolean {
    return this.sources.delete(sourceId);
  }

  /**
   * Collect events from a source
   */
  collectEvents(source: EventSource): AnalyticsEvent[] {
    const sourceEvents: AnalyticsEvent[] = [];

    if (!source.active) {
      return sourceEvents;
    }

    // Implementation depends on source type
    // For now, return empty array - to be implemented based on source integration
    return sourceEvents;
  }

  /**
   * Record an analytics event
   */
  recordEvent(type: AnalyticsEventType, data: Record<string, any>, metadata?: AnalyticsEvent['metadata']): string {
    const event: AnalyticsEvent = {
      id: `evt_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type,
      timestamp: Date.now(),
      data,
      metadata,
    };

    this.events.push(event);

    // Enforce max events limit
    if (this.events.length > this.config.maxEventsInMemory) {
      this.events.shift();
    }

    // Clean old events
    this.cleanupOldEvents();

    // Stream event if enabled
    if (this.config.enableStreaming) {
      this.config.streamingCallback(event);
    }

    return event.id;
  }

  /**
   * Aggregate metrics over a time window
   */
  aggregateMetrics(window: TimeWindow = TimeWindow.HOUR): AggregatedMetrics {
    const now = Date.now();
    const windowStart = now - window;

    // Filter events within time window
    const windowEvents = this.events.filter(e => e.timestamp >= windowStart && e.timestamp <= now);

    // Calculate metrics
    const agentMetrics = this.calculateAgentMetrics(windowEvents);
    const colonyMetrics = this.calculateColonyMetrics(windowEvents);
    const ecosystemMetrics = this.calculateEcosystemMetrics(windowEvents);
    const timeSeriesData = this.calculateTimeSeries(windowEvents, window);

    const aggregated: AggregatedMetrics = {
      timestamp: now,
      window,
      agentMetrics,
      colonyMetrics,
      ecosystemMetrics,
      timeSeriesData,
    };

    // Cache the results
    this.metricsCache.set(window, aggregated);
    this.lastAggregationTime = now;

    return aggregated;
  }

  /**
   * Compute statistics for a metric
   */
  computeStatistics(values: number[]): Statistics {
    return this.statisticalAnalyzer.analyze(values);
  }

  /**
   * Analyze time series data
   */
  analyzeTimeSeries(data: TimeSeriesData): TrendAnalysis {
    const values = data.points.map(p => p.value);
    const trend = this.statisticalAnalyzer.detectTrend(values);

    return {
      metric: data.metric,
      direction: trend.direction,
      strength: trend.strength,
      rateOfChange: trend.rateOfChange,
      prediction: this.statisticalAnalyzer.forecast(values, 5),
      confidenceInterval: this.statisticalAnalyzer.calculateConfidenceInterval(values),
    };
  }

  /**
   * Detect patterns in behavior data
   */
  detectPatterns(behavior: AnalyticsEvent[]): Pattern[] {
    return this.patternDetector.detect(behavior);
  }

  /**
   * Detect anomalies in metrics
   */
  detectAnomalies(metrics: AggregatedMetrics): Anomaly[] {
    return this.anomalyDetector.detect(metrics);
  }

  /**
   * Analyze correlations between metrics
   */
  analyzeCorrelations(metrics: AggregatedMetrics): Correlation[] {
    const metricValues = this.extractMetricValues(metrics);
    return this.correlationAnalyzer.analyze(metricValues);
  }

  /**
   * Generate analytics report
   */
  generateReport(scope: ReportScope = ReportScope.FULL, timeRange?: { start: number; end: number }): AnalyticsReport {
    const now = Date.now();
    const defaultTimeRange = {
      start: now - TimeWindow.HOUR,
      end: now,
    };

    const range = timeRange || defaultTimeRange;

    // Aggregate metrics
    const window = range.end - range.start;
    const metrics = this.aggregateMetrics(window as TimeWindow);

    // Compute statistics for key metrics
    const statistics = new Map<string, Statistics>();
    for (const ts of metrics.timeSeriesData) {
      const values = ts.points.map(p => p.value);
      if (values.length > 0) {
        statistics.set(ts.metric, this.computeStatistics(values));
      }
    }

    // Detect patterns
    const windowEvents = this.events.filter(e => e.timestamp >= range.start && e.timestamp <= range.end);
    const patterns = this.detectPatterns(windowEvents);

    // Detect anomalies
    const anomalies = this.detectAnomalies(metrics);

    // Analyze correlations
    const correlations = this.analyzeCorrelations(metrics);

    // Analyze trends
    const trends = new Map<string, TrendAnalysis>();
    for (const ts of metrics.timeSeriesData) {
      if (ts.points.length > 10) {
        trends.set(ts.metric, this.analyzeTimeSeries(ts));
      }
    }

    // Generate insights
    const insights = this.generateInsights(metrics, patterns, anomalies, trends);

    return {
      id: `report_${now}`,
      timestamp: now,
      scope,
      timeRange: range,
      metrics,
      statistics,
      patterns,
      anomalies,
      correlations,
      trends,
      insights,
    };
  }

  /**
   * Get events within a time range
   */
  getEventsInRange(start: number, end: number): AnalyticsEvent[] {
    return this.events.filter(e => e.timestamp >= start && e.timestamp <= end);
  }

  /**
   * Get events by type
   */
  getEventsByType(type: AnalyticsEventType): AnalyticsEvent[] {
    return this.events.filter(e => e.type === type);
  }

  /**
   * Get cached metrics
   */
  getCachedMetrics(window: TimeWindow): AggregatedMetrics | undefined {
    return this.metricsCache.get(window);
  }

  /**
   * Clear all events
   */
  clearEvents(): void {
    this.events = [];
    this.metricsCache.clear();
  }

  /**
   * Get pipeline statistics
   */
  getStats(): {
    totalEvents: number;
    eventsByType: Map<AnalyticsEventType, number>;
    registeredSources: number;
    uptime: number;
    lastAggregation: number;
  } {
    const eventsByType = new Map<AnalyticsEventType, number>();
    for (const event of this.events) {
      const count = eventsByType.get(event.type) || 0;
      eventsByType.set(event.type, count + 1);
    }

    return {
      totalEvents: this.events.length,
      eventsByType,
      registeredSources: this.sources.size,
      uptime: Date.now() - this.startTime,
      lastAggregation: this.lastAggregationTime,
    };
  }

  /**
   * Clean up old events
   */
  private cleanupOldEvents(): void {
    const cutoff = Date.now() - this.config.eventRetentionPeriod;
    this.events = this.events.filter(e => e.timestamp > cutoff);
  }

  /**
   * Calculate agent-level metrics
   */
  private calculateAgentMetrics(events: AnalyticsEvent[]): Map<string, AgentMetrics> {
    const agentMetrics = new Map<string, AgentMetrics>();

    // Group events by agent
    const eventsByAgent = new Map<string, AnalyticsEvent[]>();
    for (const event of events) {
      if (event.data.agentId) {
        const agentEvents = eventsByAgent.get(event.data.agentId) || [];
        agentEvents.push(event);
        eventsByAgent.set(event.data.agentId, agentEvents);
      }
    }

    // Calculate metrics for each agent
    for (const [agentId, agentEvents] of eventsByAgent.entries()) {
      const fitness = agentEvents.find(e => e.type === AnalyticsEventType.AGENT_FITNESS)?.data.fitness || {
        overall: 0.5,
        throughput: 0.5,
        accuracy: 0.5,
        efficiency: 0.5,
        cooperation: 0.5,
      };

      const processingOps = agentEvents.filter(e => e.type === AnalyticsEventType.OPERATION_PERFORMED);
      const processingTimes = processingOps.map(e => e.data.duration || 0);

      agentMetrics.set(agentId, {
        agentId,
        taxonomy: agentEvents[0]?.data.taxonomy || AgentTaxonomy.BACTERIA,
        fitness,
        processing: {
          totalOperations: processingOps.length,
          successfulOperations: processingOps.filter(e => e.data.success !== false).length,
          failedOperations: processingOps.filter(e => e.data.success === false).length,
          avgProcessingTime: processingTimes.length > 0 ? processingTimes.reduce((a, b) => a + b, 0) / processingTimes.length : 0,
          totalProcessingTime: processingTimes.reduce((a, b) => a + b, 0),
        },
        metabolism: agentEvents[0]?.data.metabolism || {
          efficiency: 0.5,
          processingRate: 1,
          resourcesConsumed: 0,
          resourcesProduced: 0,
        },
        lifecycle: agentEvents[0]?.data.lifecycle || {
          age: 0,
          generation: 0,
          health: 1,
          isAlive: true,
        },
        communication: {
          messagesSent: agentEvents.filter(e => e.type === AnalyticsEventType.AGENT_BORN).length,
          messagesReceived: 0,
          symbioses: agentEvents.filter(e => e.type === AnalyticsEventType.SYMBIOSIS_FORMED).length,
        },
      });
    }

    return agentMetrics;
  }

  /**
   * Calculate colony-level metrics
   */
  private calculateColonyMetrics(events: AnalyticsEvent[]): Map<string, ColonyMetrics> {
    const colonyMetrics = new Map<string, ColonyMetrics>();

    // Group events by colony
    const eventsByColony = new Map<string, AnalyticsEvent[]>();
    for (const event of events) {
      if (event.data.colonyId) {
        const colonyEvents = eventsByColony.get(event.data.colonyId) || [];
        colonyEvents.push(event);
        eventsByColony.set(event.data.colonyId, colonyEvents);
      }
    }

    // Calculate metrics for each colony
    for (const [colonyId, colonyEvents] of eventsByColony.entries()) {
      const formationEvent = colonyEvents.find(e => e.type === AnalyticsEventType.COLONY_FORMED);
      const memberCount = colonyEvents[colonyEvents.length - 1]?.data.memberCount || 0;

      colonyMetrics.set(colonyId, {
        colonyId,
        memberCount,
        stability: colonyEvents[colonyEvents.length - 1]?.data.stability || 0.5,
        coEvolutionBonus: formationEvent?.data.coEvolutionBonus || 0.1,
        communicationEfficiency: 0.8, // Placeholder
        avgMemberFitness: 0.5, // Placeholder
        age: formationEvent ? Date.now() - formationEvent.timestamp : 0,
        formationTime: formationEvent?.timestamp || 0,
      });
    }

    return colonyMetrics;
  }

  /**
   * Calculate ecosystem-level metrics
   */
  private calculateEcosystemMetrics(events: AnalyticsEvent[]): EcosystemMetrics {
    const populationByTaxonomy = new Map<AgentTaxonomy, number>();
    for (const taxonomy of Object.values(AgentTaxonomy)) {
      populationByTaxonomy.set(taxonomy, 0);
    }

    let totalAgents = 0;
    let birthCount = 0;
    let deathCount = 0;
    let activeColonies = 0;
    let activeSymbioses = 0;

    for (const event of events) {
      switch (event.type) {
        case AnalyticsEventType.AGENT_BORN:
          totalAgents++;
          birthCount++;
          if (event.data.taxonomy) {
            populationByTaxonomy.set(event.data.taxonomy, (populationByTaxonomy.get(event.data.taxonomy) || 0) + 1);
          }
          break;
        case AnalyticsEventType.AGENT_DIED:
          deathCount++;
          break;
        case AnalyticsEventType.COLONY_FORMED:
          activeColonies++;
          break;
        case AnalyticsEventType.COLONY_DISSOLVED:
          activeColonies--;
          break;
        case AnalyticsEventType.SYMBIOSIS_FORMED:
          activeSymbioses++;
          break;
        case AnalyticsEventType.SYMBIOSIS_BROKEN:
          activeSymbioses--;
          break;
      }
    }

    // Calculate diversity (Shannon entropy)
    let diversity = 0;
    if (totalAgents > 0) {
      for (const count of populationByTaxonomy.values()) {
        if (count > 0) {
          const p = count / totalAgents;
          diversity -= p * Math.log(p);
        }
      }
    }

    const timeSpan = Math.max(1, (Date.now() - this.startTime) / 1000);
    const birthRate = birthCount / timeSpan;
    const deathRate = deathCount / timeSpan;
    const growthRate = (birthCount - deathCount) / timeSpan;

    return {
      totalAgents,
      populationByTaxonomy,
      diversity,
      healthScore: this.calculateHealthScore(events),
      resourceAvailability: new Map(), // To be populated from resource events
      activeColonies: Math.max(0, activeColonies),
      activeSymbioses: Math.max(0, activeSymbioses),
      birthRate,
      deathRate,
      growthRate,
    };
  }

  /**
   * Calculate time-series data
   */
  private calculateTimeSeries(events: AnalyticsEvent[], window: TimeWindow): TimeSeriesData[] {
    const timeSeriesMap = new Map<string, TimeSeriesDataPoint[]>();

    // Extract numeric values from events
    for (const event of events) {
      for (const [key, value] of Object.entries(event.data)) {
        if (typeof value === 'number') {
          const metricName = `${event.type}.${key}`;
          const points = timeSeriesMap.get(metricName) || [];
          points.push({
            timestamp: event.timestamp,
            metric: metricName,
            value,
            labels: {
              eventType: event.type,
            },
          });
          timeSeriesMap.set(metricName, points);
        }
      }
    }

    // Calculate statistics for each time series
    const timeSeriesData: TimeSeriesData[] = [];
    for (const [metric, points] of timeSeriesMap.entries()) {
      if (points.length === 0) continue;

      const values = points.map(p => p.value);
      values.sort((a, b) => a - b);

      const count = values.length;
      const sum = values.reduce((a, b) => a + b, 0);
      const avg = sum / count;
      const min = values[0];
      const max = values[values.length - 1];

      const getPercentile = (p: number) => values[Math.floor((p / 100) * count)];

      const variance = values.reduce((acc, val) => acc + Math.pow(val - avg, 2), 0) / count;
      const stdDev = Math.sqrt(variance);

      timeSeriesData.push({
        metric,
        points,
        stats: {
          count,
          sum,
          avg,
          min,
          max,
          p50: getPercentile(50),
          p95: getPercentile(95),
          p99: getPercentile(99),
          variance,
          stdDev,
        },
      });
    }

    return timeSeriesData;
  }

  /**
   * Calculate system health score
   */
  private calculateHealthScore(events: AnalyticsEvent[]): number {
    let score = 1.0;

    // Penalize for high death rate
    const deathCount = events.filter(e => e.type === AnalyticsEventType.AGENT_DIED).length;
    const birthCount = events.filter(e => e.type === AnalyticsEventType.AGENT_BORN).length;
    if (birthCount > 0) {
      const deathRate = deathCount / birthCount;
      score -= Math.min(0.3, deathRate * 0.3);
    }

    // Penalize for anomalies
    const anomalyCount = events.filter(e => e.type === AnalyticsEventType.ANOMALY_DETECTED).length;
    score -= Math.min(0.2, anomalyCount * 0.05);

    // Penalize for colony dissolution
    const dissolvedCount = events.filter(e => e.type === AnalyticsEventType.COLONY_DISSOLVED).length;
    score -= Math.min(0.2, dissolvedCount * 0.1);

    return Math.max(0, Math.min(1, score));
  }

  /**
   * Extract metric values for correlation analysis
   */
  private extractMetricValues(metrics: AggregatedMetrics): Map<string, number[]> {
    const values = new Map<string, number[]>();

    // Extract from time series data
    for (const ts of metrics.timeSeriesData) {
      values.set(ts.metric, ts.points.map(p => p.value));
    }

    return values;
  }

  /**
   * Generate insights from analytics
   */
  private generateInsights(
    metrics: AggregatedMetrics,
    patterns: Pattern[],
    anomalies: Anomaly[],
    trends: Map<string, TrendAnalysis>
  ): string[] {
    const insights: string[] = [];

    // Population insights
    const population = metrics.ecosystemMetrics.totalAgents;
    if (population < 10) {
      insights.push('Population is critically low. Consider introducing more agents.');
    } else if (population > 1000) {
      insights.push('Population is high. Monitor resource availability.');
    }

    // Diversity insights (always generate at least one)
    const diversity = metrics.ecosystemMetrics.diversity;
    if (diversity < 1.0) {
      insights.push('Low species diversity detected. System may be vulnerable to disruptions.');
    } else if (diversity > 2.0) {
      insights.push('High species diversity indicates a healthy, resilient ecosystem.');
    } else {
      insights.push(`Species diversity is moderate (${diversity.toFixed(2)}). Continue monitoring balance.`);
    }

    // Growth rate insights
    const growthRate = metrics.ecosystemMetrics.growthRate;
    if (growthRate < -0.1) {
      insights.push('Negative population growth detected. Investigate causes of agent deaths.');
    } else if (growthRate > 0.5) {
      insights.push('Rapid population growth. Ensure adequate resources.');
    }

    // Health score insights
    const healthScore = metrics.ecosystemMetrics.healthScore;
    if (healthScore < 0.5) {
      insights.push('System health is degraded. Review anomalies and patterns.');
    } else if (healthScore > 0.8) {
      insights.push('System is healthy and functioning optimally.');
    }

    // Pattern insights
    for (const pattern of patterns) {
      if (pattern.confidence > 0.8) {
        insights.push(`Strong pattern detected: ${pattern.description}`);
      }
    }

    // Anomaly insights
    const criticalAnomalies = anomalies.filter(a => a.severity > 0.7);
    if (criticalAnomalies.length > 0) {
      insights.push(`${criticalAnomalies.length} critical anomalies detected requiring attention.`);
    }

    // Trend insights
    for (const [metric, trend] of trends.entries()) {
      if (trend.strength > 0.7) {
        insights.push(`Strong ${trend.direction} trend in ${metric} (${trend.rateOfChange.toFixed(2)}%/period).`);
      }
    }

    return insights;
  }
}

/**
 * Pattern Detector - Detects patterns in behavioral data
 */
class PatternDetector {
  private threshold: number;

  constructor(threshold: number) {
    this.threshold = threshold;
  }

  detect(events: AnalyticsEvent[]): Pattern[] {
    const patterns: Pattern[] = [];

    // Detect oscillation patterns
    const oscillations = this.detectOscillation(events);
    patterns.push(...oscillations);

    // Detect trend patterns
    const trends = this.detectTrends(events);
    patterns.push(...trends);

    // Detect cluster patterns
    const clusters = this.detectClusters(events);
    patterns.push(...clusters);

    return patterns.filter(p => p.confidence >= this.threshold);
  }

  private detectOscillation(events: AnalyticsEvent[]): Pattern[] {
    // Implementation for detecting oscillating behavior
    return [];
  }

  private detectTrends(events: AnalyticsEvent[]): Pattern[] {
    // Implementation for detecting trends
    return [];
  }

  private detectClusters(events: AnalyticsEvent[]): Pattern[] {
    // Implementation for detecting communication clusters
    return [];
  }
}

/**
 * Anomaly Detector - Detects anomalies in metrics
 */
class AnomalyDetector {
  private sensitivity: number;

  constructor(sensitivity: number) {
    this.sensitivity = sensitivity;
  }

  detect(metrics: AggregatedMetrics): Anomaly[] {
    const anomalies: Anomaly[] = [];

    // Detect population anomalies
    const popAnomalies = this.detectPopulationAnomalies(metrics);
    anomalies.push(...popAnomalies);

    // Detect performance anomalies
    const perfAnomalies = this.detectPerformanceAnomalies(metrics);
    anomalies.push(...perfAnomalies);

    // Detect resource anomalies
    const resourceAnomalies = this.detectResourceAnomalies(metrics);
    anomalies.push(...resourceAnomalies);

    return anomalies;
  }

  private detectPopulationAnomalies(metrics: AggregatedMetrics): Anomaly[] {
    const anomalies: Anomaly[] = [];
    const pop = metrics.ecosystemMetrics;

    // Population crash detection
    // Check multiple indicators of a crash
    const hasNegativeGrowth = pop.growthRate < 0;
    const highDeathRate = pop.deathRate > 0.01;
    const deathExceedsBirth = pop.deathRate > pop.birthRate;

    // Calculate crash severity based on multiple factors
    let crashSeverity = 0;
    if (hasNegativeGrowth) crashSeverity += 0.3;
    if (highDeathRate) crashSeverity += 0.3;
    if (deathExceedsBirth) crashSeverity += 0.4;

    if (crashSeverity >= 0.7 && pop.deathRate > 0.01) {
      const deathToBirthRatio = pop.birthRate > 0 ? pop.deathRate / pop.birthRate : Infinity;

      anomalies.push({
        id: `anom_pop_crash_${Date.now()}`,
        type: AnomalyType.POPULATION_CRASH,
        severity: Math.min(1, crashSeverity),
        description: `Rapid population decline detected (death/birth ratio: ${deathToBirthRatio.toFixed(2)})`,
        affectedEntities: ['ecosystem'],
        value: pop.growthRate,
        expectedRange: [-0.01, 0.1],
        detectedAt: Date.now(),
        suggestedActions: [
          'Check resource availability',
          'Review death events',
          'Investigate environmental stressors',
        ],
      });
    }

    // Population explosion
    if (pop.growthRate > 1.0) {
      anomalies.push({
        id: `anom_pop_explosion_${Date.now()}`,
        type: AnomalyType.POPULATION_EXPLOSION,
        severity: Math.min(1, pop.growthRate / 2),
        description: 'Uncontrolled population growth',
        affectedEntities: ['ecosystem'],
        value: pop.growthRate,
        expectedRange: [-0.1, 0.5],
        detectedAt: Date.now(),
        suggestedActions: [
          'Monitor resource consumption',
          'Consider carrying capacity limits',
        ],
      });
    }

    return anomalies;
  }

  private detectPerformanceAnomalies(metrics: AggregatedMetrics): Anomaly[] {
    const anomalies: Anomaly[] = [];

    // Check for slow operations in time series data
    for (const ts of metrics.timeSeriesData) {
      if (ts.metric.includes('processingTime') || ts.metric.includes('duration')) {
        const avg = ts.stats.avg;
        const p95 = ts.stats.p95;

        if (avg > 5000) {
          anomalies.push({
            id: `anom_perf_slow_${Date.now()}`,
            type: AnomalyType.PERFORMANCE_DEGRADATION,
            severity: Math.min(1, avg / 10000),
            description: `Slow operation detected in ${ts.metric}`,
            affectedEntities: [ts.metric],
            value: avg,
            expectedRange: [0, 1000],
            detectedAt: Date.now(),
            suggestedActions: [
              'Profile operation',
              'Check for blocking calls',
              'Review algorithm efficiency',
            ],
          });
        }
      }
    }

    return anomalies;
  }

  private detectResourceAnomalies(metrics: AggregatedMetrics): Anomaly[] {
    const anomalies: Anomaly[] = [];

    // Check for resource depletion
    for (const [resource, availability] of metrics.ecosystemMetrics.resourceAvailability.entries()) {
      if (availability < 10) {
        anomalies.push({
          id: `anom_res_depleted_${Date.now()}`,
          type: AnomalyType.RESOURCE_EXHAUSTION,
          severity: 1 - (availability / 10),
          description: `Resource ${resource} is nearly exhausted`,
          affectedEntities: [resource],
          value: availability,
          expectedRange: [100, Infinity],
          detectedAt: Date.now(),
          suggestedActions: [
            'Refill resource pool',
            'Reduce consumption',
            'Find alternative resources',
          ],
        });
      }
    }

    return anomalies;
  }
}

/**
 * Statistical Analyzer - Performs statistical analysis
 */
class StatisticalAnalyzer {
  analyze(values: number[]): Statistics {
    if (values.length === 0) {
      return this.emptyStatistics();
    }

    const sorted = [...values].sort((a, b) => a - b);
    const n = values.length;

    const sum = values.reduce((a, b) => a + b, 0);
    const mean = sum / n;

    // Calculate median correctly for both odd and even arrays
    let median: number;
    if (n % 2 === 0) {
      // Even number of elements: average of middle two
      const mid = n / 2;
      median = (sorted[mid - 1] + sorted[mid]) / 2;
    } else {
      // Odd number of elements: middle element
      median = sorted[Math.floor(n / 2)];
    }

    const variance = values.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / n;
    const stdDev = Math.sqrt(variance);

    // Calculate skewness
    const skewness = values.reduce((acc, val) => acc + Math.pow((val - mean) / stdDev, 3), 0) / n;

    // Calculate kurtosis
    const kurtosis = values.reduce((acc, val) => acc + Math.pow((val - mean) / stdDev, 4), 0) / n - 3;

    // Find mode (most frequent value)
    const frequency = new Map<number, number>();
    for (const val of values) {
      frequency.set(val, (frequency.get(val) || 0) + 1);
    }
    let mode = values[0];
    let maxFreq = 0;
    for (const [val, freq] of frequency.entries()) {
      if (freq > maxFreq) {
        maxFreq = freq;
        mode = val;
      }
    }

    // Detect outliers using IQR method
    const q1Index = Math.floor(n * 0.25);
    const q3Index = Math.floor(n * 0.75);
    const q1 = sorted[q1Index];
    const q3 = sorted[q3Index];
    const iqr = q3 - q1;
    const lowerBound = q1 - 1.5 * iqr;
    const upperBound = q3 + 1.5 * iqr;
    const outliers = values.filter(v => v < lowerBound || v > upperBound);

    // Helper function to get percentile value
    // For array [1..100], p25 should give 25, p50 should give 50, etc.
    const getPercentile = (p: number): number => {
      // For evenly spaced array [1, 2, ..., n], the p-th percentile is simply p% of n
      // For [1..100], p25 = 25, p50 = 50, etc.
      if (n === 1) return sorted[0];

      // Use simple index-based approach for evenly distributed data
      const index = (p / 100) * (n - 1);
      const lowerIndex = Math.floor(index);
      const upperIndex = Math.min(Math.ceil(index), n - 1);

      if (lowerIndex === upperIndex) {
        return sorted[lowerIndex];
      }

      // Linear interpolation
      const fraction = index - lowerIndex;
      return sorted[lowerIndex] + fraction * (sorted[upperIndex] - sorted[lowerIndex]);
    };

    return {
      descriptive: {
        mean,
        median,
        mode,
        variance,
        standardDeviation: stdDev,
        skewness,
        kurtosis,
      },
      percentiles: {
        p25: getPercentile(25),
        p50: median,
        p75: getPercentile(75),
        p90: getPercentile(90),
        p95: getPercentile(95),
        p99: getPercentile(99),
      },
      distribution: {
        min: sorted[0],
        max: sorted[n - 1],
        range: sorted[n - 1] - sorted[0],
        outliers,
      },
    };
  }

  detectTrend(values: number[]): { direction: 'increasing' | 'decreasing' | 'stable'; strength: number; rateOfChange: number } {
    if (values.length < 3) {
      return { direction: 'stable', strength: 0, rateOfChange: 0 };
    }

    // Calculate linear regression
    const n = values.length;
    const xValues = Array.from({ length: n }, (_, i) => i);

    const sumX = xValues.reduce((a, b) => a + b, 0);
    const sumY = values.reduce((a, b) => a + b, 0);
    const sumXY = xValues.reduce((acc, x, i) => acc + x * values[i], 0);
    const sumX2 = xValues.reduce((acc, x) => acc + x * x, 0);

    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    const intercept = (sumY - slope * sumX) / n;

    // Calculate R-squared
    const yMean = sumY / n;
    const ssTotal = values.reduce((acc, y) => acc + Math.pow(y - yMean, 2), 0);
    const ssResidual = values.reduce((acc, y, i) => {
      const predicted = slope * i + intercept;
      return acc + Math.pow(y - predicted, 2);
    }, 0);
    const rSquared = 1 - ssResidual / ssTotal;

    // Determine direction
    let direction: 'increasing' | 'decreasing' | 'stable';
    if (Math.abs(slope) < 0.01) {
      direction = 'stable';
    } else if (slope > 0) {
      direction = 'increasing';
    } else {
      direction = 'decreasing';
    }

    return {
      direction,
      strength: Math.sqrt(rSquared),
      rateOfChange: slope,
    };
  }

  forecast(values: number[], horizon: number): number[] {
    const trend = this.detectTrend(values);
    const lastValue = values[values.length - 1];

    const forecast: number[] = [];
    for (let i = 1; i <= horizon; i++) {
      forecast.push(lastValue + trend.rateOfChange * i);
    }

    return forecast;
  }

  calculateConfidenceInterval(values: number[], confidence: number = 0.95): [number, number] {
    const stats = this.analyze(values);
    const margin = 1.96 * stats.descriptive.standardDeviation / Math.sqrt(values.length);

    return [
      stats.descriptive.mean - margin,
      stats.descriptive.mean + margin,
    ];
  }

  private emptyStatistics(): Statistics {
    return {
      descriptive: {
        mean: 0,
        median: 0,
        mode: 0,
        variance: 0,
        standardDeviation: 0,
        skewness: 0,
        kurtosis: 0,
      },
      percentiles: {
        p25: 0,
        p50: 0,
        p75: 0,
        p90: 0,
        p95: 0,
        p99: 0,
      },
      distribution: {
        min: 0,
        max: 0,
        range: 0,
        outliers: [],
      },
    };
  }
}

/**
 * Correlation Analyzer - Analyzes correlations between metrics
 */
class CorrelationAnalyzer {
  analyze(metricValues: Map<string, number[]>): Correlation[] {
    const correlations: Correlation[] = [];
    const metrics = Array.from(metricValues.keys());

    // Calculate pairwise correlations
    for (let i = 0; i < metrics.length; i++) {
      for (let j = i + 1; j < metrics.length; j++) {
        const metric1 = metrics[i];
        const metric2 = metrics[j];
        const values1 = metricValues.get(metric1)!;
        const values2 = metricValues.get(metric2)!;

        const coefficient = this.calculateCorrelation(values1, values2);

        if (Math.abs(coefficient) > 0.3) {
          correlations.push({
            metric1,
            metric2,
            coefficient,
            strength: this.getStrength(coefficient),
            direction: this.getDirection(coefficient),
          });
        }
      }
    }

    return correlations;
  }

  private calculateCorrelation(x: number[], y: number[]): number {
    const n = Math.min(x.length, y.length);
    if (n === 0) return 0;

    const sumX = x.slice(0, n).reduce((a, b) => a + b, 0);
    const sumY = y.slice(0, n).reduce((a, b) => a + b, 0);
    const sumXY = x.slice(0, n).reduce((acc, xi, i) => acc + xi * y[i], 0);
    const sumX2 = x.slice(0, n).reduce((acc, xi) => acc + xi * xi, 0);
    const sumY2 = y.slice(0, n).reduce((acc, yi) => acc + yi * yi, 0);

    const numerator = n * sumXY - sumX * sumY;
    const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));

    return denominator === 0 ? 0 : numerator / denominator;
  }

  private getStrength(coefficient: number): 'weak' | 'moderate' | 'strong' {
    const abs = Math.abs(coefficient);
    if (abs < 0.5) return 'weak';
    if (abs < 0.7) return 'moderate';
    return 'strong';
  }

  private getDirection(coefficient: number): 'positive' | 'negative' | 'none' {
    if (Math.abs(coefficient) < 0.1) return 'none';
    return coefficient > 0 ? 'positive' : 'negative';
  }
}

/**
 * Create an analytics pipeline with default configuration
 */
export function createAnalyticsPipeline(config?: AnalyticsPipelineConfig): AnalyticsPipeline {
  return new AnalyticsPipeline(config);
}
