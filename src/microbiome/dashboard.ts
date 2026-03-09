/**
 * POLLN Microbiome - Dashboard & Visualization System
 *
 * Phase 10: Observability & Intelligence - Milestone 2
 * Comprehensive dashboard system for real-time visualization,
 * interactive widgets, and multi-format export capabilities.
 *
 * @module microbiome/dashboard
 */

import { EventEmitter } from 'events';
import { AnalyticsPipeline, AggregatedMetrics, TimeSeriesData, ReportScope, TimeWindow } from './analytics.js';
import type { WebSocket } from 'ws';

/**
 * Dashboard configuration
 */
export interface DashboardConfig {
  /** Dashboard ID */
  id: string;
  /** Dashboard name */
  name: string;
  /** Dashboard description */
  description?: string;
  /** Dashboard template */
  template?: DashboardTemplate;
  /** Layout configuration */
  layout?: DashboardLayout;
  /** Update interval (ms) */
  updateInterval?: number;
  /** Auto-refresh enabled */
  autoRefresh?: boolean;
}

/**
 * Dashboard templates
 */
export enum DashboardTemplate {
  SYSTEM_OVERVIEW = 'system_overview',
  PERFORMANCE = 'performance',
  EVOLUTION = 'evolution',
  COLONY = 'colony',
  SECURITY = 'security',
  CUSTOM = 'custom',
}

/**
 * Dashboard layout configuration
 */
export interface DashboardLayout {
  /** Layout type */
  type: 'grid' | 'flex' | 'absolute';
  /** Number of columns */
  columns?: number;
  /** Widget positions */
  positions?: Map<string, WidgetPosition>;
}

/**
 * Widget position
 */
export interface WidgetPosition {
  /** Row index */
  row: number;
  /** Column index */
  column: number;
  /** Row span */
  rowSpan?: number;
  /** Column span */
  columnSpan?: number;
}

/**
 * Widget types
 */
export enum WidgetType {
  // Metric widgets
  METRIC_CARD = 'metric_card',
  GAUGE = 'gauge',
  PROGRESS = 'progress',

  // Chart widgets
  LINE_CHART = 'line_chart',
  BAR_CHART = 'bar_chart',
  PIE_CHART = 'pie_chart',
  HEATMAP = 'heatmap',
  SCATTER_PLOT = 'scatter_plot',
  HISTOGRAM = 'histogram',
  SANKEY = 'sankey',
  NETWORK_GRAPH = 'network_graph',
  TREEMAP = 'treemap',

  // Data widgets
  TABLE = 'table',
  LOG_VIEWER = 'log_viewer',
  EVENT_LIST = 'event_list',

  // Special widgets
  COLONY_VISUALIZATION = 'colony_visualization',
  COMMUNICATION_GRAPH = 'communication_graph',
  RESOURCE_MONITOR = 'resource_monitor',
}

/**
 * Widget configuration
 */
export interface WidgetConfig {
  /** Widget ID */
  id: string;
  /** Widget type */
  type: WidgetType;
  /** Widget title */
  title: string;
  /** Widget position */
  position?: WidgetPosition;
  /** Widget size */
  size?: WidgetSize;
  /** Data source */
  dataSource: DataSource;
  /** Widget options */
  options?: WidgetOptions;
  /** Refresh interval (ms) */
  refreshInterval?: number;
}

/**
 * Widget size
 */
export interface WidgetSize {
  /** Width in grid units */
  width: number;
  /** Height in grid units */
  height: number;
  /** Minimum width */
  minWidth?: number;
  /** Minimum height */
  minHeight?: number;
}

/**
 * Data source configuration
 */
export interface DataSource {
  /** Source type */
  type: 'analytics' | 'custom' | 'external';
  /** Source identifier */
  source: string;
  /** Query configuration */
  query?: DataQuery;
  /** Aggregation configuration */
  aggregation?: DataAggregation;
}

/**
 * Data query
 */
export interface DataQuery {
  /** Time range */
  timeRange?: { start: number; end: number };
  /** Filters */
  filters?: Record<string, any>;
  /** Group by */
  groupBy?: string[];
  /** Order by */
  orderBy?: { field: string; direction: 'asc' | 'desc' };
  /** Limit */
  limit?: number;
}

/**
 * Data aggregation
 */
export interface DataAggregation {
  /** Aggregation function */
  function: 'sum' | 'avg' | 'min' | 'max' | 'count' | 'percentile';
  /** Time window */
  window?: TimeWindow;
  /** Percentile value (for percentile aggregation) */
  percentile?: number;
}

/**
 * Widget options (type-specific)
 */
export type WidgetOptions = {
  // Chart options
  xAxis?: AxisOptions;
  yAxis?: AxisOptions;
  legend?: LegendOptions;
  colors?: string[];
  showGrid?: boolean;
  showTooltip?: boolean;
  enableZoom?: boolean;
  enablePan?: boolean;

  // Metric card options
  showTrend?: boolean;
  showDelta?: boolean;
  trendPeriod?: TimeWindow;
  threshold?: { warning: number; critical: number };
  unit?: string;

  // Table options
  columns?: TableColumn[];
  sortable?: boolean;
  filterable?: boolean;
  pagination?: { pageSize: number };

  // Log viewer options
  logLevel?: 'debug' | 'info' | 'warn' | 'error';
  maxLines?: number;
  autoScroll?: boolean;

  // Custom options
  [key: string]: any;
};

/**
 * Axis options
 */
export interface AxisOptions {
  /** Axis label */
  label?: string;
  /** Axis type */
  type?: 'linear' | 'log' | 'time' | 'category';
  /** Minimum value */
  min?: number;
  /** Maximum value */
  max?: number;
  /** Show axis */
  show?: boolean;
}

/**
 * Legend options
 */
export interface LegendOptions {
  /** Show legend */
  show?: boolean;
  /** Legend position */
  position?: 'top' | 'bottom' | 'left' | 'right';
}

/**
 * Table column definition
 */
export interface TableColumn {
  /** Column key */
  key: string;
  /** Column title */
  title: string;
  /** Column type */
  type?: 'text' | 'number' | 'date' | 'boolean';
  /** Sortable */
  sortable?: boolean;
  /** Filterable */
  filterable?: boolean;
  /** Cell renderer */
  renderer?: (value: any) => string;
}

/**
 * Chart types
 */
export enum ChartType {
  LINE = 'line',
  BAR = 'bar',
  PIE = 'pie',
  HEATMAP = 'heatmap',
  SCATTER = 'scatter',
  HISTOGRAM = 'histogram',
  SANKEY = 'sankey',
  NETWORK = 'network',
  TREEMAP = 'treemap',
  GAUGE = 'gauge',
}

/**
 * Export formats
 */
export enum ExportFormat {
  PNG = 'png',
  PDF = 'pdf',
  SVG = 'svg',
  CSV = 'csv',
  JSON = 'json',
  HTML = 'html',
}

/**
 * Dashboard state
 */
export interface Dashboard {
  /** Dashboard ID */
  id: string;
  /** Dashboard configuration */
  config: DashboardConfig;
  /** Dashboard widgets */
  widgets: Map<string, ActiveWidget>;
  /** Dashboard data */
  data: DashboardData;
  /** Last update timestamp */
  lastUpdate: number;
  /** Is active */
  isActive: boolean;
}

/**
 * Active widget (with runtime data)
 */
export interface ActiveWidget extends WidgetConfig {
  /** Last data update */
  lastUpdate: number;
  /** Current data */
  data: WidgetData;
  /** Widget state */
  state: WidgetState;
}

/**
 * Widget data
 */
export type WidgetData = {
  type: 'metric';
  value: number;
  trend?: number;
  delta?: number;
} | {
  type: 'chart';
  chartData: ChartData;
} | {
  type: 'table';
  rows: Record<string, any>[];
  columns: string[];
} | {
  type: 'log';
  entries: LogEntry[];
} | {
  type: 'custom';
  data: any;
};

/**
 * Chart data
 */
export interface ChartData {
  /** Chart type */
  type: ChartType;
  /** Data series */
  series: ChartSeries[];
  /** Categories (for categorical charts) */
  categories?: string[];
  /** Min/max values */
  range?: { min: number; max: number };
}

/**
 * Chart series
 */
export interface ChartSeries {
  /** Series name */
  name: string;
  /** Data points */
  data: ChartPoint[];
  /** Color */
  color?: string;
}

/**
 * Chart point
 */
export interface ChartPoint {
  /** X value (timestamp or category) */
  x: number | string;
  /** Y value */
  y: number;
  /** Additional metadata */
  metadata?: Record<string, any>;
}

/**
 * Log entry
 */
export interface LogEntry {
  /** Timestamp */
  timestamp: number;
  /** Log level */
  level: 'debug' | 'info' | 'warn' | 'error';
  /** Message */
  message: string;
  /** Metadata */
  metadata?: Record<string, any>;
}

/**
 * Widget state
 */
export interface WidgetState {
  /** Is loading */
  isLoading: boolean;
  /** Has error */
  hasError: boolean;
  /** Error message */
  error?: string;
  /** Update count */
  updateCount: number;
}

/**
 * Dashboard data
 */
export interface DashboardData {
  /** Time-series data */
  timeSeries: Map<string, TimeSeriesData>;
  /** Current metrics */
  metrics: AggregatedMetrics;
  /** Dashboard metadata */
  metadata: {
    generatedAt: number;
    dataRange: { start: number; end: number };
    updateCount: number;
  };
}

/**
 * Visualization query
 */
export interface VisualizationQuery {
  /** Dashboard ID */
  dashboardId?: string;
  /** Widget IDs */
  widgetIds?: string[];
  /** Time range */
  timeRange?: { start: number; end: number };
  /** Data sources */
  dataSources?: string[];
  /** Include metadata */
  includeMetadata?: boolean;
}

/**
 * Visualization data
 */
export interface VisualizationData {
  /** Dashboard data */
  dashboards: Map<string, DashboardData>;
  /** Widget data */
  widgets: Map<string, WidgetData>;
  /** Global metadata */
  metadata: {
    generatedAt: number;
    dashboardsCount: number;
    widgetsCount: number;
  };
}

/**
 * Real-time update data
 */
export interface RealTimeData {
  /** Dashboard ID */
  dashboardId: string;
  /** Widget ID */
  widgetId?: string;
  /** Update type */
  type: 'full' | 'incremental' | 'alert';
  /** Data */
  data: WidgetData | DashboardData;
  /** Timestamp */
  timestamp: number;
}

/**
 * Export result
 */
export interface ExportResult {
  /** Export ID */
  id: string;
  /** Export format */
  format: ExportFormat;
  /** Data URL or path */
  data: string;
  /** File size (bytes) */
  size: number;
  /** Generated at */
  generatedAt: number;
}

/**
 * Dashboard system configuration
 */
export interface DashboardSystemConfig {
  /** Analytics pipeline */
  analyticsPipeline: AnalyticsPipeline;
  /** Enable WebSocket streaming */
  enableStreaming?: boolean;
  /** WebSocket server path (for integration) */
  wsPath?: string;
  /** Default update interval (ms) */
  defaultUpdateInterval?: number;
  /** Maximum cached dashboards */
  maxCachedDashboards?: number;
  /** Export directory */
  exportDirectory?: string;
}

/**
 * Dashboard System - Main class for dashboard management
 */
export class DashboardSystem extends EventEmitter {
  /** Analytics pipeline */
  private analytics: AnalyticsPipeline;
  /** Configuration */
  private config: Required<DashboardSystemConfig>;
  /** Dashboard registry */
  private dashboards: Map<string, Dashboard>;
  /** Widget registry */
  private widgets: Map<string, ActiveWidget>;
  /** Update intervals */
  private updateIntervals: Map<string, NodeJS.Timeout>;
  /** WebSocket clients */
  private wsClients: Set<WebSocket>;
  /** System start time */
  private startTime: number;

  constructor(config: DashboardSystemConfig) {
    super();
    this.analytics = config.analyticsPipeline;
    this.dashboards = new Map();
    this.widgets = new Map();
    this.updateIntervals = new Map();
    this.wsClients = new Set();
    this.startTime = Date.now();

    this.config = {
      analyticsPipeline: config.analyticsPipeline,
      enableStreaming: config.enableStreaming ?? false,
      wsPath: config.wsPath ?? '/api/dashboards',
      defaultUpdateInterval: config.defaultUpdateInterval ?? 5000,
      maxCachedDashboards: config.maxCachedDashboards ?? 10,
      exportDirectory: config.exportDirectory ?? './exports',
    };
  }

  // ========================================================================
  // Dashboard Management
  // ========================================================================

  /**
   * Create a new dashboard
   */
  createDashboard(config: DashboardConfig): Dashboard {
    const dashboard: Dashboard = {
      id: config.id,
      config,
      widgets: new Map(),
      data: this.initializeDashboardData(config),
      lastUpdate: Date.now(),
      isActive: true,
    };

    this.dashboards.set(config.id, dashboard);

    // Apply template if specified
    if (config.template && config.template !== DashboardTemplate.CUSTOM) {
      this.applyTemplate(dashboard, config.template);
    }

    // Start auto-refresh if enabled
    if (config.autoRefresh !== false) {
      this.startAutoRefresh(config.id);
    }

    this.emit('dashboard:created', { dashboardId: config.id });
    return dashboard;
  }

  /**
   * Get a dashboard by ID
   */
  getDashboard(dashboardId: string): Dashboard | undefined {
    return this.dashboards.get(dashboardId);
  }

  /**
   * List all dashboards
   */
  listDashboards(): Dashboard[] {
    return Array.from(this.dashboards.values());
  }

  /**
   * Update dashboard configuration
   */
  updateDashboardConfig(dashboardId: string, config: Partial<DashboardConfig>): Dashboard | null {
    const dashboard = this.dashboards.get(dashboardId);
    if (!dashboard) {
      return null;
    }

    // Merge config but preserve id
    const { id, ...configWithoutId } = config as any;
    dashboard.config = { ...dashboard.config, ...configWithoutId };
    dashboard.lastUpdate = Date.now();

    this.emit('dashboard:updated', { dashboardId });
    return dashboard;
  }

  /**
   * Delete a dashboard
   */
  deleteDashboard(dashboardId: string): boolean {
    const dashboard = this.dashboards.get(dashboardId);
    if (!dashboard) {
      return false;
    }

    // Stop auto-refresh
    this.stopAutoRefresh(dashboardId);

    // Remove widgets
    for (const widgetId of dashboard.widgets.keys()) {
      this.widgets.delete(widgetId);
    }

    this.dashboards.delete(dashboardId);
    this.emit('dashboard:deleted', { dashboardId });
    return true;
  }

  // ========================================================================
  // Widget Management
  // ========================================================================

  /**
   * Add a widget to a dashboard
   */
  addWidget(dashboardId: string, widgetConfig: WidgetConfig): ActiveWidget | null {
    const dashboard = this.dashboards.get(dashboardId);
    if (!dashboard) {
      return null;
    }

    const widget: ActiveWidget = {
      ...widgetConfig,
      lastUpdate: 0,
      data: this.initializeWidgetData(widgetConfig),
      state: {
        isLoading: false,
        hasError: false,
        updateCount: 0,
      },
    };

    dashboard.widgets.set(widgetConfig.id, widget);
    this.widgets.set(widgetConfig.id, widget);

    // Initial data load
    this.updateWidget(dashboardId, widgetConfig.id);

    this.emit('widget:added', { dashboardId, widgetId: widgetConfig.id });
    return widget;
  }

  /**
   * Get a widget by ID
   */
  getWidget(widgetId: string): ActiveWidget | undefined {
    return this.widgets.get(widgetId);
  }

  /**
   * Update a widget
   */
  updateWidget(dashboardId: string, widgetId: string): void {
    const dashboard = this.dashboards.get(dashboardId);
    const widget = dashboard?.widgets.get(widgetId);

    if (!widget) {
      return;
    }

    widget.state.isLoading = true;

    try {
      const data = this.fetchWidgetData(widget);
      widget.data = data;
      widget.lastUpdate = Date.now();
      widget.state.updateCount++;
      widget.state.hasError = false;
      widget.state.error = undefined;

      // Emit update event
      if (this.config.enableStreaming) {
        this.broadcastWidgetUpdate(dashboardId, widgetId, data);
      }
    } catch (error) {
      widget.state.hasError = true;
      widget.state.error = error instanceof Error ? error.message : String(error);
    } finally {
      widget.state.isLoading = false;
    }

    this.emit('widget:updated', { dashboardId, widgetId });
  }

  /**
   * Remove a widget from a dashboard
   */
  removeWidget(dashboardId: string, widgetId: string): boolean {
    const dashboard = this.dashboards.get(dashboardId);
    if (!dashboard) {
      return false;
    }

    const removed = dashboard.widgets.delete(widgetId);
    this.widgets.delete(widgetId);

    if (removed) {
      this.emit('widget:removed', { dashboardId, widgetId });
    }

    return removed;
  }

  // ========================================================================
  // Real-time Updates
  // ========================================================================

  /**
   * Update a dashboard with real-time data
   */
  updateDashboard(dashboardId: string, data: RealTimeData): void {
    const dashboard = this.dashboards.get(dashboardId);
    if (!dashboard) {
      return;
    }

    if (data.type === 'full') {
      // Full dashboard update
      dashboard.data = data.data as DashboardData;
    } else if (data.widgetId) {
      // Incremental widget update
      const widget = dashboard.widgets.get(data.widgetId);
      if (widget) {
        widget.data = data.data as WidgetData;
        widget.lastUpdate = data.timestamp;
      }
    }

    dashboard.lastUpdate = data.timestamp;
    this.emit('dashboard:updated', { dashboardId });
  }

  /**
   * Start auto-refresh for a dashboard
   */
  private startAutoRefresh(dashboardId: string): void {
    const dashboard = this.dashboards.get(dashboardId);
    if (!dashboard) {
      return;
    }

    const interval = dashboard.config.updateInterval || this.config.defaultUpdateInterval;

    const timeout = setInterval(() => {
      if (!dashboard.isActive) {
        return;
      }

      // Update all widgets
      for (const widgetId of dashboard.widgets.keys()) {
        this.updateWidget(dashboardId, widgetId);
      }

      // Update dashboard data
      dashboard.data.metrics = this.analytics.aggregateMetrics();
      dashboard.data.metadata.generatedAt = Date.now();
      dashboard.data.metadata.updateCount++;
    }, interval);

    this.updateIntervals.set(dashboardId, timeout);
  }

  /**
   * Stop auto-refresh for a dashboard
   */
  private stopAutoRefresh(dashboardId: string): void {
    const interval = this.updateIntervals.get(dashboardId);
    if (interval) {
      clearInterval(interval);
      this.updateIntervals.delete(dashboardId);
    }
  }

  // ========================================================================
  // Data Querying
  // ========================================================================

  /**
   * Query data for visualization
   */
  queryData(query: VisualizationQuery): VisualizationData {
    const dashboards = new Map<string, DashboardData>();
    const widgets = new Map<string, WidgetData>();

    if (query.dashboardId) {
      // Query specific dashboard
      const dashboard = this.dashboards.get(query.dashboardId);
      if (dashboard) {
        dashboards.set(query.dashboardId, dashboard.data);

        if (query.widgetIds && query.widgetIds.length > 0) {
          // Query specific widgets
          for (const widgetId of query.widgetIds) {
            const widget = dashboard.widgets.get(widgetId);
            if (widget) {
              widgets.set(widgetId, widget.data);
            }
          }
        } else {
          // Query all widgets
          for (const [widgetId, widget] of dashboard.widgets.entries()) {
            widgets.set(widgetId, widget.data);
          }
        }
      }
    } else {
      // Query all dashboards
      for (const [id, dashboard] of this.dashboards.entries()) {
        dashboards.set(id, dashboard.data);
        for (const [widgetId, widget] of dashboard.widgets.entries()) {
          widgets.set(widgetId, widget.data);
        }
      }
    }

    return {
      dashboards,
      widgets,
      metadata: {
        generatedAt: Date.now(),
        dashboardsCount: dashboards.size,
        widgetsCount: widgets.size,
      },
    };
  }

  // ========================================================================
  // Chart Generation
  // ========================================================================

  /**
   * Generate a chart from data
   */
  generateChart(data: TimeSeriesData | any[], chartType: ChartType, options?: WidgetOptions): ChartData {
    const series: ChartSeries[] = [];

    if (Array.isArray(data) && data.length > 0) {
      // Time-series data
      const tsData = data as TimeSeriesData[];
      for (const ts of tsData) {
        series.push({
          name: ts.metric,
          data: ts.points.map(p => ({ x: p.timestamp, y: p.value })),
        });
      }
    } else if ('points' in data) {
      // Single time series
      const ts = data as TimeSeriesData;
      series.push({
        name: ts.metric,
        data: ts.points.map(p => ({ x: p.timestamp, y: p.value })),
      });
    }

    // Calculate range
    let range: { min: number; max: number } | undefined;
    if (series.length > 0 && series[0].data.length > 0) {
      const allValues = series.flatMap(s => s.data.map(d => d.y));
      range = {
        min: Math.min(...allValues),
        max: Math.max(...allValues),
      };
    }

    return {
      type: chartType,
      series,
      range,
    };
  }

  // ========================================================================
  // Export Functionality
  // ========================================================================

  /**
   * Export a dashboard
   */
  exportDashboard(dashboardId: string, format: ExportFormat): ExportResult {
    const dashboard = this.dashboards.get(dashboardId);
    if (!dashboard) {
      throw new Error(`Dashboard not found: ${dashboardId}`);
    }

    const exportId = `export_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    let data: string;
    let size: number;

    switch (format) {
      case ExportFormat.JSON:
        data = this.exportToJSON(dashboard);
        size = data.length;
        break;

      case ExportFormat.CSV:
        data = this.exportToCSV(dashboard);
        size = data.length;
        break;

      case ExportFormat.HTML:
        data = this.exportToHTML(dashboard);
        size = data.length;
        break;

      case ExportFormat.PNG:
      case ExportFormat.PDF:
      case ExportFormat.SVG:
        // For binary formats, we'd need actual rendering libraries
        // Return placeholder for now
        data = `export_${dashboardId}.${format}`;
        size = 0;
        break;

      default:
        throw new Error(`Unsupported export format: ${format}`);
    }

    return {
      id: exportId,
      format,
      data,
      size,
      generatedAt: Date.now(),
    };
  }

  /**
   * Export dashboard to JSON
   */
  private exportToJSON(dashboard: Dashboard): string {
    const exportData = {
      dashboard: {
        id: dashboard.id,
        config: dashboard.config,
        lastUpdate: dashboard.lastUpdate,
      },
      widgets: Array.from(dashboard.widgets.entries()).map(([id, widget]) => ({
        id,
        config: widget,
        data: widget.data,
      })),
      data: {
        metrics: this.serializeMetrics(dashboard.data.metrics),
        timeSeries: Array.from(dashboard.data.timeSeries.entries()).map(([id, ts]) => ({
          metric: id,
          points: ts.points,
        })),
      },
      exportedAt: Date.now(),
    };

    return JSON.stringify(exportData, null, 2);
  }

  /**
   * Export dashboard to CSV
   */
  private exportToCSV(dashboard: Dashboard): string {
    const lines: string[] = [];

    // Add header
    lines.push(`Dashboard: ${dashboard.config.name}`);
    lines.push(`Generated: ${new Date(dashboard.lastUpdate).toISOString()}`);
    lines.push('');

    // Export metrics summary
    lines.push('Metric,Value');
    const metrics = dashboard.data.metrics.ecosystemMetrics;
    lines.push(`Total Agents,${metrics.totalAgents}`);
    lines.push(`Active Colonies,${metrics.activeColonies}`);
    lines.push(`Diversity,${metrics.diversity.toFixed(4)}`);
    lines.push(`Health Score,${metrics.healthScore.toFixed(4)}`);
    lines.push(`Birth Rate,${metrics.birthRate.toFixed(6)}`);
    lines.push(`Death Rate,${metrics.deathRate.toFixed(6)}`);
    lines.push(`Growth Rate,${metrics.growthRate.toFixed(6)}`);
    lines.push('');

    // Export time-series data
    for (const [metric, ts] of dashboard.data.timeSeries.entries()) {
      lines.push(`Metric: ${metric}`);
      lines.push('Timestamp,Value');

      for (const point of ts.points) {
        lines.push(`${point.timestamp},${point.value}`);
      }

      lines.push(''); // Empty line between metrics
    }

    return lines.join('\n');
  }

  /**
   * Export dashboard to HTML
   */
  private exportToHTML(dashboard: Dashboard): string {
    const widgets = Array.from(dashboard.widgets.entries());
    const widgetHTML = widgets.map(([id, widget]) => {
      return `
        <div class="widget" id="widget-${id}">
          <h3>${widget.title}</h3>
          <div class="widget-content">
            ${this.renderWidgetToHTML(widget)}
          </div>
        </div>
      `;
    }).join('\n');

    return `
<!DOCTYPE html>
<html>
<head>
  <title>${dashboard.config.name}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    .dashboard { max-width: 1200px; margin: 0 auto; }
    .widget { border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px; }
    .widget h3 { margin-top: 0; color: #333; }
    .widget-content { min-height: 100px; }
    .metric { font-size: 32px; font-weight: bold; }
    .trend { font-size: 14px; }
    .trend.up { color: green; }
    .trend.down { color: red; }
  </style>
</head>
<body>
  <div class="dashboard">
    <h1>${dashboard.config.name}</h1>
    ${dashboard.config.description ? `<p>${dashboard.config.description}</p>` : ''}
    <p class="metadata">Generated: ${new Date(dashboard.lastUpdate).toISOString()}</p>
    ${widgetHTML}
  </div>
</body>
</html>
    `.trim();
  }

  /**
   * Render widget to HTML
   */
  private renderWidgetToHTML(widget: ActiveWidget): string {
    if (widget.data.type === 'metric') {
      const trend = widget.data.trend !== undefined
        ? `<span class="trend ${widget.data.trend >= 0 ? 'up' : 'down'}">
             ${widget.data.trend >= 0 ? '↑' : '↓'} ${Math.abs(widget.data.trend).toFixed(2)}%
           </span>`
        : '';

      return `
        <div class="metric">
          ${widget.data.value.toFixed(2)}
          ${widget.options?.unit || ''}
        </div>
        ${trend}
      `;
    }

    if (widget.data.type === 'chart') {
      return `<div class="chart-placeholder">Chart: ${widget.data.chartData.type}</div>`;
    }

    if (widget.data.type === 'table') {
      const headers = widget.data.columns.map(col => `<th>${col}</th>`).join('');
      const rows = widget.data.rows.map(row => {
        const cells = widget.data.columns.map(col => `<td>${row[col]}</td>`).join('');
        return `<tr>${cells}</tr>`;
      }).join('');

      return `
        <table>
          <thead><tr>${headers}</tr></thead>
          <tbody>${rows}</tbody>
        </table>
      `;
    }

    return `<div class="widget-placeholder">Widget type: ${widget.type}</div>`;
  }

  // ========================================================================
  // WebSocket Integration
  // ========================================================================

  /**
   * Register a WebSocket client for real-time updates
   */
  registerWebSocketClient(ws: WebSocket): void {
    this.wsClients.add(ws);

    ws.on('close', () => {
      this.wsClients.delete(ws);
    });

    ws.on('error', () => {
      this.wsClients.delete(ws);
    });
  }

  /**
   * Broadcast widget update to all connected clients
   */
  private broadcastWidgetUpdate(dashboardId: string, widgetId: string, data: WidgetData): void {
    if (this.wsClients.size === 0) {
      return;
    }

    const message = {
      type: 'widget:update',
      dashboardId,
      widgetId,
      data,
      timestamp: Date.now(),
    };

    const payload = JSON.stringify(message);

    for (const ws of this.wsClients) {
      if (ws.readyState === 1) { // OPEN
        ws.send(payload);
      }
    }
  }

  // ========================================================================
  // Template System
  // ========================================================================

  /**
   * Apply a dashboard template
   */
  private applyTemplate(dashboard: Dashboard, template: DashboardTemplate): void {
    switch (template) {
      case DashboardTemplate.SYSTEM_OVERVIEW:
        this.applySystemOverviewTemplate(dashboard);
        break;
      case DashboardTemplate.PERFORMANCE:
        this.applyPerformanceTemplate(dashboard);
        break;
      case DashboardTemplate.EVOLUTION:
        this.applyEvolutionTemplate(dashboard);
        break;
      case DashboardTemplate.COLONY:
        this.applyColonyTemplate(dashboard);
        break;
      case DashboardTemplate.SECURITY:
        this.applySecurityTemplate(dashboard);
        break;
    }
  }

  /**
   * Apply system overview template
   */
  private applySystemOverviewTemplate(dashboard: Dashboard): void {
    const widgets: WidgetConfig[] = [
      {
        id: 'total_agents',
        type: WidgetType.METRIC_CARD,
        title: 'Total Agents',
        position: { row: 0, column: 0 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'ecosystem.totalAgents' },
        options: { showTrend: true, unit: 'agents' },
      },
      {
        id: 'active_colonies',
        type: WidgetType.METRIC_CARD,
        title: 'Active Colonies',
        position: { row: 0, column: 1 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'ecosystem.activeColonies' },
        options: { showTrend: true, unit: 'colonies' },
      },
      {
        id: 'diversity_index',
        type: WidgetType.METRIC_CARD,
        title: 'Diversity Index',
        position: { row: 0, column: 2 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'ecosystem.diversity' },
        options: { showTrend: true },
      },
      {
        id: 'health_score',
        type: WidgetType.GAUGE,
        title: 'System Health',
        position: { row: 1, column: 0 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'ecosystem.healthScore' },
        options: { threshold: { warning: 0.5, critical: 0.3 } },
      },
      {
        id: 'population_trend',
        type: WidgetType.LINE_CHART,
        title: 'Population Trend',
        position: { row: 1, column: 1, columnSpan: 2 },
        size: { width: 2, height: 2 },
        dataSource: { type: 'analytics', source: 'timeSeries' },
        options: { showGrid: true, showTooltip: true },
      },
      {
        id: 'birth_death_rate',
        type: WidgetType.BAR_CHART,
        title: 'Birth/Death Rate',
        position: { row: 2, column: 0 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'ecosystem.birthRate' },
        options: { showGrid: true },
      },
    ];

    for (const widget of widgets) {
      this.addWidget(dashboard.id, widget);
    }
  }

  /**
   * Apply performance template
   */
  private applyPerformanceTemplate(dashboard: Dashboard): void {
    const widgets: WidgetConfig[] = [
      {
        id: 'avg_processing_time',
        type: WidgetType.METRIC_CARD,
        title: 'Avg Processing Time',
        position: { row: 0, column: 0 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'processing.avgProcessingTime' },
        options: { showTrend: true, unit: 'ms', threshold: { warning: 1000, critical: 5000 } },
      },
      {
        id: 'throughput',
        type: WidgetType.METRIC_CARD,
        title: 'Throughput',
        position: { row: 0, column: 1 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'processing.totalOperations' },
        options: { showTrend: true, unit: 'ops/s' },
      },
      {
        id: 'error_rate',
        type: WidgetType.METRIC_CARD,
        title: 'Error Rate',
        position: { row: 0, column: 2 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'processing.failedOperations' },
        options: { showTrend: true, unit: '%', threshold: { warning: 5, critical: 10 } },
      },
      {
        id: 'latency_distribution',
        type: WidgetType.HISTOGRAM,
        title: 'Latency Distribution',
        position: { row: 1, column: 0, columnSpan: 2 },
        size: { width: 2, height: 2 },
        dataSource: { type: 'analytics', source: 'processing.processingTime' },
        options: { showGrid: true },
      },
      {
        id: 'operations_over_time',
        type: WidgetType.LINE_CHART,
        title: 'Operations Over Time',
        position: { row: 1, column: 2 },
        size: { width: 1, height: 2 },
        dataSource: { type: 'analytics', source: 'timeSeries' },
        options: { showGrid: true, showTooltip: true },
      },
    ];

    for (const widget of widgets) {
      this.addWidget(dashboard.id, widget);
    }
  }

  /**
   * Apply evolution template
   */
  private applyEvolutionTemplate(dashboard: Dashboard): void {
    const widgets: WidgetConfig[] = [
      {
        id: 'avg_fitness',
        type: WidgetType.METRIC_CARD,
        title: 'Avg Fitness',
        position: { row: 0, column: 0 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'evolution.avgFitness' },
        options: { showTrend: true },
      },
      {
        id: 'generation_count',
        type: WidgetType.METRIC_CARD,
        title: 'Generation Count',
        position: { row: 0, column: 1 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'evolution.generation' },
        options: { unit: 'gen' },
      },
      {
        id: 'mutation_rate',
        type: WidgetType.METRIC_CARD,
        title: 'Mutation Rate',
        position: { row: 0, column: 2 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'evolution.mutationRate' },
        options: { showTrend: true, unit: '%' },
      },
      {
        id: 'fitness_trend',
        type: WidgetType.LINE_CHART,
        title: 'Fitness Trend',
        position: { row: 1, column: 0, columnSpan: 2 },
        size: { width: 2, height: 2 },
        dataSource: { type: 'analytics', source: 'timeSeries' },
        options: { showGrid: true, showTooltip: true },
      },
      {
        id: 'species_distribution',
        type: WidgetType.PIE_CHART,
        title: 'Species Distribution',
        position: { row: 1, column: 2 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'ecosystem.populationByTaxonomy' },
        options: { showLegend: true },
      },
    ];

    for (const widget of widgets) {
      this.addWidget(dashboard.id, widget);
    }
  }

  /**
   * Apply colony template
   */
  private applyColonyTemplate(dashboard: Dashboard): void {
    const widgets: WidgetConfig[] = [
      {
        id: 'colony_count',
        type: WidgetType.METRIC_CARD,
        title: 'Colony Count',
        position: { row: 0, column: 0 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'ecosystem.activeColonies' },
        options: { showTrend: true, unit: 'colonies' },
      },
      {
        id: 'avg_colony_size',
        type: WidgetType.METRIC_CARD,
        title: 'Avg Colony Size',
        position: { row: 0, column: 1 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'colony.avgMemberCount' },
        options: { showTrend: true, unit: 'agents' },
      },
      {
        id: 'communication_efficiency',
        type: WidgetType.METRIC_CARD,
        title: 'Communication Efficiency',
        position: { row: 0, column: 2 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'colony.communicationEfficiency' },
        options: { showTrend: true, unit: '%' },
      },
      {
        id: 'colony_visualization',
        type: WidgetType.COLONY_VISUALIZATION,
        title: 'Colony Structure',
        position: { row: 1, column: 0, columnSpan: 2 },
        size: { width: 2, height: 2 },
        dataSource: { type: 'analytics', source: 'colony.structure' },
      },
      {
        id: 'communication_graph',
        type: WidgetType.COMMUNICATION_GRAPH,
        title: 'Communication Network',
        position: { row: 1, column: 2 },
        size: { width: 1, height: 2 },
        dataSource: { type: 'analytics', source: 'colony.communication' },
      },
    ];

    for (const widget of widgets) {
      this.addWidget(dashboard.id, widget);
    }
  }

  /**
   * Apply security template
   */
  private applySecurityTemplate(dashboard: Dashboard): void {
    const widgets: WidgetConfig[] = [
      {
        id: 'threat_level',
        type: WidgetType.GAUGE,
        title: 'Threat Level',
        position: { row: 0, column: 0 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'security.threatLevel' },
        options: { threshold: { warning: 0.5, critical: 0.7 } },
      },
      {
        id: 'compliance_score',
        type: WidgetType.METRIC_CARD,
        title: 'Compliance Score',
        position: { row: 0, column: 1 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'security.complianceScore' },
        options: { showTrend: true, unit: '%' },
      },
      {
        id: 'active_alerts',
        type: WidgetType.METRIC_CARD,
        title: 'Active Alerts',
        position: { row: 0, column: 2 },
        size: { width: 1, height: 1 },
        dataSource: { type: 'analytics', source: 'security.activeAlerts' },
        options: { showTrend: true, threshold: { warning: 5, critical: 10 } },
      },
      {
        id: 'security_events',
        type: WidgetType.EVENT_LIST,
        title: 'Security Events',
        position: { row: 1, column: 0, columnSpan: 3 },
        size: { width: 3, height: 2 },
        dataSource: { type: 'analytics', source: 'security.events' },
        options: { maxLines: 20 },
      },
    ];

    for (const widget of widgets) {
      this.addWidget(dashboard.id, widget);
    }
  }

  // ========================================================================
  // Helper Methods
  // ========================================================================

  /**
   * Initialize dashboard data
   */
  private initializeDashboardData(config: DashboardConfig): DashboardData {
    return {
      timeSeries: new Map(),
      metrics: this.analytics.aggregateMetrics(),
      metadata: {
        generatedAt: Date.now(),
        dataRange: { start: Date.now() - TimeWindow.HOUR, end: Date.now() },
        updateCount: 0,
      },
    };
  }

  /**
   * Initialize widget data
   */
  private initializeWidgetData(config: WidgetConfig): WidgetData {
    switch (config.type) {
      case WidgetType.METRIC_CARD:
      case WidgetType.GAUGE:
      case WidgetType.PROGRESS:
        return { type: 'metric', value: 0 };

      case WidgetType.LINE_CHART:
      case WidgetType.BAR_CHART:
      case WidgetType.PIE_CHART:
      case WidgetType.HEATMAP:
      case WidgetType.SCATTER_PLOT:
      case WidgetType.HISTOGRAM:
      case WidgetType.SANKEY:
      case WidgetType.NETWORK_GRAPH:
      case WidgetType.TREEMAP:
        return {
          type: 'chart',
          chartData: { type: ChartType.LINE, series: [] },
        };

      case WidgetType.TABLE:
        return { type: 'table', rows: [], columns: [] };

      case WidgetType.LOG_VIEWER:
      case WidgetType.EVENT_LIST:
        return { type: 'log', entries: [] };

      default:
        return { type: 'custom', data: null };
    }
  }

  /**
   * Fetch widget data from analytics
   */
  private fetchWidgetData(widget: ActiveWidget): WidgetData {
    const source = widget.dataSource.source;

    // Extract metric path (e.g., 'ecosystem.totalAgents')
    const parts = source.split('.');
    const category = parts[0];
    const metric = parts.slice(1).join('.');

    const metrics = this.analytics.aggregateMetrics();

    switch (category) {
      case 'ecosystem':
        return this.fetchEcosystemMetric(metrics, metric);

      case 'colony':
        return this.fetchColonyMetric(metrics, metric);

      case 'processing':
        return this.fetchProcessingMetric(metrics, metric);

      case 'evolution':
        return this.fetchEvolutionMetric(metrics, metric);

      case 'security':
        return this.fetchSecurityMetric(metrics, metric);

      case 'timeSeries':
        return this.fetchTimeSeriesData(widget);

      default:
        return widget.data;
    }
  }

  /**
   * Fetch ecosystem metric
   */
  private fetchEcosystemMetric(metrics: AggregatedMetrics, metric: string): WidgetData {
    const ecoMetrics = metrics.ecosystemMetrics;

    const valueMap: Record<string, number> = {
      totalAgents: ecoMetrics.totalAgents,
      activeColonies: ecoMetrics.activeColonies,
      activeSymbioses: ecoMetrics.activeSymbioses,
      diversity: ecoMetrics.diversity,
      healthScore: ecoMetrics.healthScore,
      birthRate: ecoMetrics.birthRate,
      deathRate: ecoMetrics.deathRate,
      growthRate: ecoMetrics.growthRate,
    };

    const value = valueMap[metric] ?? 0;

    return {
      type: 'metric',
      value,
      trend: Math.random() * 10 - 5, // Simulated trend
      delta: Math.random() * 20 - 10, // Simulated delta
    };
  }

  /**
   * Fetch colony metric
   */
  private fetchColonyMetric(metrics: AggregatedMetrics, metric: string): WidgetData {
    // Calculate from colony metrics
    const colonies = Array.from(metrics.colonyMetrics.values());

    let value = 0;
    switch (metric) {
      case 'avgMemberCount':
        value = colonies.length > 0
          ? colonies.reduce((sum, c) => sum + c.memberCount, 0) / colonies.length
          : 0;
        break;
      case 'avgStability':
        value = colonies.length > 0
          ? colonies.reduce((sum, c) => sum + c.stability, 0) / colonies.length
          : 0;
        break;
      case 'communicationEfficiency':
        value = colonies.length > 0
          ? colonies.reduce((sum, c) => sum + c.communicationEfficiency, 0) / colonies.length
          : 0;
        break;
    }

    return {
      type: 'metric',
      value,
      trend: Math.random() * 10 - 5,
    };
  }

  /**
   * Fetch processing metric
   */
  private fetchProcessingMetric(metrics: AggregatedMetrics, metric: string): WidgetData {
    // Calculate from agent metrics
    const agents = Array.from(metrics.agentMetrics.values());

    let value = 0;
    switch (metric) {
      case 'totalOperations':
        value = agents.reduce((sum, a) => sum + a.processing.totalOperations, 0);
        break;
      case 'successfulOperations':
        value = agents.reduce((sum, a) => sum + a.processing.successfulOperations, 0);
        break;
      case 'failedOperations':
        value = agents.reduce((sum, a) => sum + a.processing.failedOperations, 0);
        break;
      case 'avgProcessingTime':
        value = agents.length > 0
          ? agents.reduce((sum, a) => sum + a.processing.avgProcessingTime, 0) / agents.length
          : 0;
        break;
    }

    return {
      type: 'metric',
      value,
      trend: Math.random() * 10 - 5,
    };
  }

  /**
   * Fetch evolution metric
   */
  private fetchEvolutionMetric(metrics: AggregatedMetrics, metric: string): WidgetData {
    const agents = Array.from(metrics.agentMetrics.values());

    let value = 0;
    switch (metric) {
      case 'avgFitness':
        value = agents.length > 0
          ? agents.reduce((sum, a) => sum + a.fitness.overall, 0) / agents.length
          : 0;
        break;
      case 'generation':
        value = agents.length > 0
          ? Math.max(...agents.map(a => a.lifecycle.generation))
          : 0;
        break;
    }

    return {
      type: 'metric',
      value,
      trend: Math.random() * 10 - 5,
    };
  }

  /**
   * Fetch security metric
   */
  private fetchSecurityMetric(metrics: AggregatedMetrics, metric: string): WidgetData {
    // Placeholder for security metrics
    const valueMap: Record<string, number> = {
      threatLevel: 0.2,
      complianceScore: 95,
      activeAlerts: 2,
    };

    return {
      type: 'metric',
      value: valueMap[metric] ?? 0,
      trend: Math.random() * 10 - 5,
    };
  }

  /**
   * Fetch time-series data
   */
  private fetchTimeSeriesData(widget: ActiveWidget): WidgetData {
    const metrics = this.analytics.aggregateMetrics();
    const chartData = this.generateChart(metrics.timeSeriesData, ChartType.LINE, widget.options);

    return {
      type: 'chart',
      chartData,
    };
  }

  /**
   * Serialize metrics for export
   */
  private serializeMetrics(metrics: AggregatedMetrics): any {
    return {
      timestamp: metrics.timestamp,
      window: metrics.window,
      ecosystem: {
        totalAgents: metrics.ecosystemMetrics.totalAgents,
        activeColonies: metrics.ecosystemMetrics.activeColonies,
        diversity: metrics.ecosystemMetrics.diversity,
        healthScore: metrics.ecosystemMetrics.healthScore,
        birthRate: metrics.ecosystemMetrics.birthRate,
        deathRate: metrics.ecosystemMetrics.deathRate,
        growthRate: metrics.ecosystemMetrics.growthRate,
      },
    };
  }

  // ========================================================================
  // Statistics & Cleanup
  // ========================================================================

  /**
   * Get system statistics
   */
  getStats(): {
    totalDashboards: number;
    totalWidgets: number;
    activeDashboards: number;
    uptime: number;
  } {
    const activeDashboards = Array.from(this.dashboards.values())
      .filter(d => d.isActive).length;

    return {
      totalDashboards: this.dashboards.size,
      totalWidgets: this.widgets.size,
      activeDashboards,
      uptime: Date.now() - this.startTime,
    };
  }

  /**
   * Clean up resources
   */
  destroy(): void {
    // Stop all auto-refresh intervals
    for (const dashboardId of this.updateIntervals.keys()) {
      this.stopAutoRefresh(dashboardId);
    }

    // Close all WebSocket connections
    for (const ws of this.wsClients) {
      ws.close();
    }
    this.wsClients.clear();

    // Clear all registries
    this.dashboards.clear();
    this.widgets.clear();
  }
}

/**
 * Create a dashboard system with default configuration
 */
export function createDashboardSystem(config: DashboardSystemConfig): DashboardSystem {
  return new DashboardSystem(config);
}
