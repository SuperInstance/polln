/**
 * Distributed Tracer
 *
 * Provides distributed tracing capabilities for tracking requests
 * across multiple agents, colonies, and causal chains.
 */

import type {
  DistributedTrace,
  TraceSpan,
  TraceTimeline,
  TraceStats,
  TraceError,
  TraceMetadata,
  TraceLog,
  TraceEvent,
} from './types.js';
import { DebugError } from './types.js';

// ============================================================================
// DistributedTracer Class
// ============================================================================

/**
 * Tracer for distributed execution across agents and colonies
 */
export class DistributedTracer {
  private traces: Map<string, DistributedTrace> = new Map();
  private activeSpans: Map<string, TraceSpan> = new Map();
  private traceHistory: Map<string, DistributedTrace[]> = new Map();
  private maxHistorySize: number = 10000;

  /**
   * Start a new trace
   *
   * @param causalChainId - Causal chain ID
   * @param metadata - Trace metadata
   * @returns Trace ID
   */
  startTrace(causalChainId: string, metadata: Partial<TraceMetadata> = {}): string {
    const traceId = `trace_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    const trace: DistributedTrace = {
      traceId,
      causalChainId,
      root: {
        spanId: `${traceId}_root`,
        operationName: 'root',
        agentId: 'system',
        colonyId: 'system',
        startTime: Date.now(),
        endTime: 0,
        duration: 0,
        status: 'ok',
        tags: {},
        logs: [],
        events: [],
        packageIds: [],
      },
      spans: [],
      timeline: {
        startTime: Date.now(),
        endTime: 0,
        duration: 0,
        criticalPath: [],
      },
      stats: {
        totalSpans: 0,
        errorCount: 0,
        totalDuration: 0,
        avgDuration: 0,
        minDuration: 0,
        maxDuration: 0,
        agentsInvolved: [],
        coloniesInvolved: [],
      },
      errors: [],
      metadata: {
        timestamp: Date.now(),
        type: 'task',
        tags: metadata.tags || [],
        userId: metadata.userId,
        sessionId: metadata.sessionId,
      },
    };

    this.traces.set(traceId, trace);
    this.activeSpans.set(traceId, trace.root);

    return traceId;
  }

  /**
   * Start a new span
   *
   * @param traceId - Trace ID
   * @param operationName - Operation name
   * @param agentId - Agent ID
   * @param colonyId - Colony ID
   * @param parentSpanId - Parent span ID (optional)
   * @param tags - Span tags
   * @returns Span ID
   */
  startSpan(
    traceId: string,
    operationName: string,
    agentId: string,
    colonyId: string,
    parentSpanId?: string,
    tags: Record<string, string | number | boolean> = {}
  ): string {
    const trace = this.traces.get(traceId);
    if (!trace) {
      throw new DebugError('TRACE_NOT_FOUND', `Trace ${traceId} not found`);
    }

    const spanId = `${traceId}_${agentId}_${Date.now()}`;
    const startTime = Date.now();

    const span: TraceSpan = {
      spanId,
      parentSpanId: parentSpanId || trace.root.spanId,
      operationName,
      agentId,
      colonyId,
      startTime,
      endTime: 0,
      duration: 0,
      status: 'ok',
      tags,
      logs: [],
      events: [],
      packageIds: [],
    };

    this.activeSpans.set(spanId, span);
    trace.spans.push(span);

    // Update stats
    this.updateTraceStats(trace);

    return spanId;
  }

  /**
   * Finish a span
   *
   * @param spanId - Span ID
   * @param status - Span status
   * @param error - Error (if failed)
   */
  finishSpan(
    spanId: string,
    status: TraceSpan['status'] = 'ok',
    error?: Error
  ): void {
    const span = this.activeSpans.get(spanId);
    if (!span) {
      throw new DebugError('TRACE_NOT_FOUND', `Span ${spanId} not found`);
    }

    const endTime = Date.now();
    span.endTime = endTime;
    span.duration = endTime - span.startTime;
    span.status = status;

    // Add error if provided
    if (error) {
      this.addErrorToSpan(span, error);
    }

    this.activeSpans.delete(spanId);

    // Update trace stats
    for (const trace of this.traces.values()) {
      if (trace.spans.some(s => s.spanId === spanId)) {
        this.updateTraceStats(trace);
        break;
      }
    }
  }

  /**
   * Add a log to a span
   *
   * @param spanId - Span ID
   * @param level - Log level
   * @param message - Log message
   * @param fields - Log fields
   */
  addLog(
    spanId: string,
    level: TraceLog['level'],
    message: string,
    fields?: Record<string, unknown>
  ): void {
    const span = this.activeSpans.get(spanId);
    if (!span) {
      // Check in completed spans
      for (const trace of this.traces.values()) {
        const found = trace.spans.find(s => s.spanId === spanId);
        if (found) {
          const log: TraceLog = {
            timestamp: Date.now(),
            level,
            message,
            fields,
          };
          found.logs.push(log);
          return;
        }
      }
      return;
    }

    const log: TraceLog = {
      timestamp: Date.now(),
      level,
      message,
      fields,
    };

    span.logs.push(log);
  }

  /**
   * Add an event to a span
   *
   * @param spanId - Span ID
   * @param name - Event name
   * @param attributes - Event attributes
   */
  addEvent(
    spanId: string,
    name: string,
    attributes: Record<string, unknown> = {}
  ): void {
    const span = this.activeSpans.get(spanId);
    if (!span) {
      // Check in completed spans
      for (const trace of this.traces.values()) {
        const found = trace.spans.find(s => s.spanId === spanId);
        if (found) {
          const event: TraceEvent = {
            timestamp: Date.now(),
            name,
            attributes,
          };
          found.events.push(event);
          return;
        }
      }
      return;
    }

    const event: TraceEvent = {
      timestamp: Date.now(),
      name,
      attributes,
    };

    span.events.push(event);
  }

  /**
   * Link an A2A package to a span
   *
   * @param spanId - Span ID
   * @param packageId - A2A package ID
   */
  linkPackage(spanId: string, packageId: string): void {
    const span = this.activeSpans.get(spanId);
    if (!span) return;

    span.packageIds.push(packageId);
  }

  /**
   * Finish a trace
   *
   * @param traceId - Trace ID
   * @returns Completed trace
   */
  finishTrace(traceId: string): DistributedTrace {
    const trace = this.traces.get(traceId);
    if (!trace) {
      throw new DebugError('TRACE_NOT_FOUND', `Trace ${traceId} not found`);
    }

    // Finish root span if still active
    if (this.activeSpans.has(trace.root.spanId)) {
      this.finishSpan(trace.root.spanId);
    }

    // Update timeline
    trace.timeline.endTime = Date.now();
    trace.timeline.duration = trace.timeline.endTime - trace.timeline.startTime;

    // Compute critical path
    trace.timeline.criticalPath = this.computeCriticalPath(trace);

    // Finalize stats
    this.updateTraceStats(trace);

    // Store in history
    this.storeTraceHistory(traceId, trace);

    return trace;
  }

  /**
   * Get a trace
   *
   * @param traceId - Trace ID
   * @returns Trace or null
   */
  getTrace(traceId: string): DistributedTrace | null {
    return this.traces.get(traceId) || null;
  }

  /**
   * Get trace by causal chain ID
   *
   * @param causalChainId - Causal chain ID
   * @returns Trace or null
   */
  getTraceByCausalChain(causalChainId: string): DistributedTrace | null {
    for (const trace of this.traces.values()) {
      if (trace.causalChainId === causalChainId) {
        return trace;
      }
    }
    return null;
  }

  /**
   * List all traces
   *
   * @param filters - Optional filters
   * @returns Array of traces
   */
  listTraces(filters?: TraceFilters): DistributedTrace[] {
    let traces = Array.from(this.traces.values());

    if (filters) {
      if (filters.agentId) {
        traces = traces.filter(t =>
          t.spans.some(s => s.agentId === filters.agentId)
        );
      }

      if (filters.colonyId) {
        traces = traces.filter(t =>
          t.spans.some(s => s.colonyId === filters.colonyId)
        );
      }

      if (filters.type) {
        traces = traces.filter(t => t.metadata.type === filters.type);
      }

      if (filters.minStartTime) {
        traces = traces.filter(t => t.timeline.startTime >= filters.minStartTime!);
      }

      if (filters.maxStartTime) {
        traces = traces.filter(t => t.timeline.startTime <= filters.maxStartTime!);
      }

      if (filters.limit) {
        traces = traces.slice(0, filters.limit);
      }
    }

    return traces;
  }

  /**
   * Get trace history for a causal chain
   *
   * @param causalChainId - Causal chain ID
   * @param limit - Maximum number of traces
   * @returns Array of traces
   */
  getTraceHistory(causalChainId: string, limit?: number): DistributedTrace[] {
    const history = this.traceHistory.get(causalChainId) || [];
    return limit ? history.slice(-limit) : history;
  }

  /**
   * Analyze trace performance
   *
   * @param traceId - Trace ID
   * @returns Performance analysis
   */
  analyzePerformance(traceId: string): TracePerformanceAnalysis {
    const trace = this.traces.get(traceId);
    if (!trace) {
      throw new DebugError('TRACE_NOT_FOUND', `Trace ${traceId} not found`);
    }

    const analysis: TracePerformanceAnalysis = {
      traceId,
      totalDuration: trace.timeline.duration,
      spanCount: trace.stats.totalSpans,
      errorCount: trace.stats.errorCount,
      avgSpanDuration: trace.stats.avgDuration,
      minSpanDuration: trace.stats.minDuration,
      maxSpanDuration: trace.stats.maxDuration,

      // Slowest spans
      slowestSpans: [...trace.spans]
        .sort((a, b) => b.duration - a.duration)
        .slice(0, 10)
        .map(s => ({
          spanId: s.spanId,
          operationName: s.operationName,
          agentId: s.agentId,
          duration: s.duration,
        })),

      // Spans with errors
      errorSpans: trace.spans
        .filter(s => s.status === 'error')
        .map(s => ({
          spanId: s.spanId,
          operationName: s.operationName,
          agentId: s.agentId,
          error: s.logs.find(l => l.level === 'error')?.message || 'Unknown error',
        })),

      // Agent breakdown
      agentBreakdown: this.computeAgentBreakdown(trace),

      // Timeline visualization data
      timelineData: this.computeTimelineData(trace),
    };

    return analysis;
  }

  /**
   * Export trace to various formats
   *
   * @param traceId - Trace ID
   * @param format - Export format
   * @returns Exported data
   */
  exportTrace(traceId: string, format: TraceExportFormat): string {
    const trace = this.traces.get(traceId);
    if (!trace) {
      throw new DebugError('TRACE_NOT_FOUND', `Trace ${traceId} not found`);
    }

    switch (format) {
      case 'json':
        return JSON.stringify(trace, null, 2);

      case 'jaeger':
        return this.exportToJaeger(trace);

      case 'zipkin':
        return this.exportToZipkin(trace);

      default:
        throw new DebugError(
          'TRACE_NOT_FOUND',
          `Unknown export format: ${format}`
        );
    }
  }

  // ==========================================================================
  // Private Methods
  // ==========================================================================

  private updateTraceStats(trace: DistributedTrace): void {
    const spans = trace.spans.concat(trace.root);

    trace.stats.totalSpans = spans.length;
    trace.stats.errorCount = spans.filter(s => s.status === 'error').length;

    const durations = spans.map(s => s.duration).filter(d => d > 0);
    if (durations.length > 0) {
      trace.stats.totalDuration = durations.reduce((sum, d) => sum + d, 0);
      trace.stats.avgDuration = trace.stats.totalDuration / durations.length;
      trace.stats.minDuration = Math.min(...durations);
      trace.stats.maxDuration = Math.max(...durations);
    }

    // Track unique agents and colonies
    const agents = new Set<string>();
    const colonies = new Set<string>();

    for (const span of spans) {
      agents.add(span.agentId);
      colonies.add(span.colonyId);
    }

    trace.stats.agentsInvolved = Array.from(agents);
    trace.stats.coloniesInvolved = Array.from(colonies);
  }

  private computeCriticalPath(trace: DistributedTrace): string[] {
    // Compute critical path using longest path algorithm
    const spans = trace.spans.concat(trace.root);

    // Build span tree
    const children = new Map<string, string[]>();
    for (const span of spans) {
      if (span.parentSpanId) {
        if (!children.has(span.parentSpanId)) {
          children.set(span.parentSpanId, []);
        }
        children.get(span.parentSpanId)!.push(span.spanId);
      }
    }

    // Find longest path from root
    const longestPath: string[] = [];
    const stack: Array<{ spanId: string; path: string[] }> = [
      { spanId: trace.root.spanId, path: [] },
    ];

    while (stack.length > 0) {
      const { spanId, path } = stack.pop()!;
      const currentPath = [...path, spanId];

      const spanChildren = children.get(spanId) || [];
      if (spanChildren.length === 0) {
        // Leaf node - check if this is the longest path
        if (currentPath.length > longestPath.length) {
          longestPath.length = 0;
          longestPath.push(...currentPath);
        }
      } else {
        for (const child of spanChildren) {
          stack.push({ spanId: child, path: currentPath });
        }
      }
    }

    return longestPath;
  }

  private addErrorToSpan(span: TraceSpan, error: Error): void {
    const traceError: TraceError = {
      errorId: `err_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      spanId: span.spanId,
      message: error.message,
      stackTrace: error.stack,
      timestamp: Date.now(),
    };

    // Add error log
    span.logs.push({
      timestamp: traceError.timestamp,
      level: 'error',
      message: error.message,
      fields: {
        stackTrace: error.stack,
      },
    });

    // Find or create trace to add error
    for (const trace of this.traces.values()) {
      if (trace.spans.some(s => s.spanId === span.spanId)) {
        trace.errors.push(traceError);
        break;
      }
    }
  }

  private storeTraceHistory(traceId: string, trace: DistributedTrace): void {
    let history = this.traceHistory.get(trace.causalChainId);

    if (!history) {
      history = [];
      this.traceHistory.set(trace.causalChainId, history);
    }

    history.push(trace);

    // Enforce max size
    if (history.length > this.maxHistorySize) {
      history.shift();
    }
  }

  private computeAgentBreakdown(trace: DistributedTrace): AgentBreakdown[] {
    const agentStats = new Map<string, {
      totalDuration: number;
      spanCount: number;
      errorCount: number;
    }>();

    for (const span of trace.spans) {
      let stats = agentStats.get(span.agentId);
      if (!stats) {
        stats = { totalDuration: 0, spanCount: 0, errorCount: 0 };
        agentStats.set(span.agentId, stats);
      }

      stats.totalDuration += span.duration;
      stats.spanCount++;
      if (span.status === 'error') {
        stats.errorCount++;
      }
    }

    return Array.from(agentStats.entries()).map(([agentId, stats]) => ({
      agentId,
      totalDuration: stats.totalDuration,
      spanCount: stats.spanCount,
      errorCount: stats.errorCount,
      avgDuration: stats.totalDuration / stats.spanCount,
    }));
  }

  private computeTimelineData(trace: DistributedTrace): TimelineDataPoint[] {
    const points: TimelineDataPoint[] = [];
    const startTime = trace.timeline.startTime;

    for (const span of trace.spans) {
      points.push({
        spanId: span.spanId,
        operationName: span.operationName,
        agentId: span.agentId,
        startTime: span.startTime - startTime,
        endTime: span.endTime - startTime,
        duration: span.duration,
      });
    }

    return points.sort((a, b) => a.startTime - b.startTime);
  }

  private exportToJaeger(trace: DistributedTrace): string {
    // Export to Jaeger JSON format
    const jaegerTrace = {
      traceID: trace.traceId.replace(/_/g, '').substring(0, 32),
      spans: trace.spans.map(span => ({
        traceID: trace.traceId.replace(/_/g, '').substring(0, 32),
        spanID: span.spanId.replace(/_/g, '').substring(0, 16),
        parentSpanID: span.parentSpanId?.replace(/_/g, '').substring(0, 16) || '',
        operationName: span.operationName,
        startTime: span.startTime * 1000, // Microseconds
        duration: span.duration * 1000, // Microseconds
        tags: Object.entries(span.tags).map(([key, value]) => ({
          key,
          value: String(value),
          type: typeof value,
        })),
        logs: span.logs.map(log => ({
          timestamp: log.timestamp * 1000,
          fields: [
            { key: 'level', value: log.level },
            { key: 'message', value: log.message },
            ...(log.fields ? Object.entries(log.fields).map(([k, v]) => ({
              key: k,
              value: String(v),
            })) : []),
          ],
        })),
      })),
    };

    return JSON.stringify(jaegerTrace, null, 2);
  }

  private exportToZipkin(trace: DistributedTrace): string {
    // Export to Zipkin JSON format
    const zipkinSpans = trace.spans.map(span => ({
      traceId: trace.traceId,
      id: span.spanId,
      parentId: span.parentSpanId,
      name: span.operationName,
      timestamp: span.startTime * 1000, // Microseconds
      duration: span.duration * 1000, // Microseconds
      localEndpoint: {
        serviceName: span.agentId,
      },
      tags: span.tags,
    }));

    return JSON.stringify(zipkinSpans, null, 2);
  }
}

// ============================================================================
// Types
// ============================================================================

/**
 * Trace filters
 */
export interface TraceFilters {
  /**
   * Filter by agent ID
   */
  agentId?: string;

  /**
   * Filter by colony ID
   */
  colonyId?: string;

  /**
   * Filter by trace type
   */
  type?: string;

  /**
   * Filter by minimum start time
   */
  minStartTime?: number;

  /**
   * Filter by maximum start time
   */
  maxStartTime?: number;

  /**
   * Limit results
   */
  limit?: number;
}

/**
 * Trace performance analysis
 */
export interface TracePerformanceAnalysis {
  /**
   * Trace ID
   */
  traceId: string;

  /**
   * Total duration
   */
  totalDuration: number;

  /**
   * Span count
   */
  spanCount: number;

  /**
   * Error count
   */
  errorCount: number;

  /**
   * Average span duration
   */
  avgSpanDuration: number;

  /**
   * Minimum span duration
   */
  minSpanDuration: number;

  /**
   * Maximum span duration
   */
  maxSpanDuration: number;

  /**
   * Slowest spans
   */
  slowestSpans: Array<{
    spanId: string;
    operationName: string;
    agentId: string;
    duration: number;
  }>;

  /**
   * Spans with errors
   */
  errorSpans: Array<{
    spanId: string;
    operationName: string;
    agentId: string;
    error: string;
  }>;

  /**
   * Agent breakdown
   */
  agentBreakdown: AgentBreakdown[];

  /**
   * Timeline data
   */
  timelineData: TimelineDataPoint[];
}

/**
 * Agent breakdown
 */
export interface AgentBreakdown {
  /**
   * Agent ID
   */
  agentId: string;

  /**
   * Total duration
   */
  totalDuration: number;

  /**
   * Span count
   */
  spanCount: number;

  /**
   * Error count
   */
  errorCount: number;

  /**
   * Average duration
   */
  avgDuration: number;
}

/**
 * Timeline data point
 */
export interface TimelineDataPoint {
  /**
   * Span ID
   */
  spanId: string;

  /**
   * Operation name
   */
  operationName: string;

  /**
   * Agent ID
   */
  agentId: string;

  /**
   * Start time (relative to trace start)
   */
  startTime: number;

  /**
   * End time (relative to trace start)
   */
  endTime: number;

  /**
   * Duration
   */
  duration: number;
}

/**
 * Trace export format
 */
export type TraceExportFormat = 'json' | 'jaeger' | 'zipkin';
