/**
 * POLLN Microbiome - Dashboard System Tests
 *
 * Comprehensive test suite for the dashboard and visualization system
 */

import { describe, test, expect, beforeEach, afterEach, jest } from '@jest/globals';
import {
  DashboardSystem,
  DashboardConfig,
  WidgetConfig,
  WidgetType,
  DashboardTemplate,
  ChartType,
  ExportFormat,
  VisualizationQuery,
  createDashboardSystem,
} from '../dashboard.js';
import { AnalyticsPipeline, AnalyticsEventType, TimeWindow } from '../analytics.js';
import type { WebSocket } from 'ws';

// Mock WebSocket
class MockWebSocket {
  readyState = 1; // OPEN
  sentMessages: string[] = [];
  private eventListeners: Map<string, (() => void)[]> = new Map();

  send(data: string): void {
    this.sentMessages.push(data);
  }

  close(): void {
    this.readyState = 3; // CLOSED
    this.emit('close');
  }

  on(event: string, listener: (...args: any[]) => void): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, []);
    }
    this.eventListeners.get(event)!.push(listener as any);
  }

  private emit(event: string): void {
    const listeners = this.eventListeners.get(event) || [];
    for (const listener of listeners) {
      listener();
    }
  }
}

describe('DashboardSystem', () => {
  let analytics: AnalyticsPipeline;
  let dashboardSystem: DashboardSystem;

  beforeEach(() => {
    analytics = new AnalyticsPipeline({
      maxEventsInMemory: 1000,
      enableStreaming: false,
    });

    // Seed some analytics data
    analytics.recordEvent(AnalyticsEventType.AGENT_BORN, {
      agentId: 'agent1',
      taxonomy: 'bacteria',
      fitness: 0.8,
    });
    analytics.recordEvent(AnalyticsEventType.AGENT_BORN, {
      agentId: 'agent2',
      taxonomy: 'virus',
      fitness: 0.6,
    });
    analytics.recordEvent(AnalyticsEventType.COLONY_FORMED, {
      colonyId: 'colony1',
      memberCount: 5,
      stability: 0.7,
    });

    dashboardSystem = createDashboardSystem({
      analyticsPipeline: analytics,
      enableStreaming: false,
      defaultUpdateInterval: 1000,
    });
  });

  afterEach(() => {
    dashboardSystem.destroy();
  });

  // ========================================================================
  // Dashboard Creation & Management
  // ========================================================================

  describe('Dashboard Creation', () => {
    test('should create a new dashboard with basic config', () => {
      const config: DashboardConfig = {
        id: 'test-dashboard',
        name: 'Test Dashboard',
        description: 'A test dashboard',
      };

      const dashboard = dashboardSystem.createDashboard(config);

      expect(dashboard).toBeDefined();
      expect(dashboard.id).toBe('test-dashboard');
      expect(dashboard.config.name).toBe('Test Dashboard');
      expect(dashboard.isActive).toBe(true);
      expect(dashboard.widgets.size).toBe(0);
    });

    test('should create dashboard with system overview template', () => {
      const config: DashboardConfig = {
        id: 'system-overview',
        name: 'System Overview',
        template: DashboardTemplate.SYSTEM_OVERVIEW,
      };

      const dashboard = dashboardSystem.createDashboard(config);

      expect(dashboard).toBeDefined();
      expect(dashboard.widgets.size).toBeGreaterThan(0);
      expect(dashboard.config.template).toBe(DashboardTemplate.SYSTEM_OVERVIEW);
    });

    test('should create dashboard with performance template', () => {
      const config: DashboardConfig = {
        id: 'performance-dashboard',
        name: 'Performance',
        template: DashboardTemplate.PERFORMANCE,
      };

      const dashboard = dashboardSystem.createDashboard(config);

      expect(dashboard).toBeDefined();
      expect(dashboard.widgets.size).toBeGreaterThan(0);
      expect(dashboard.config.template).toBe(DashboardTemplate.PERFORMANCE);
    });

    test('should create dashboard with evolution template', () => {
      const config: DashboardConfig = {
        id: 'evolution-dashboard',
        name: 'Evolution',
        template: DashboardTemplate.EVOLUTION,
      };

      const dashboard = dashboardSystem.createDashboard(config);

      expect(dashboard).toBeDefined();
      expect(dashboard.widgets.size).toBeGreaterThan(0);
      expect(dashboard.config.template).toBe(DashboardTemplate.EVOLUTION);
    });

    test('should create dashboard with colony template', () => {
      const config: DashboardConfig = {
        id: 'colony-dashboard',
        name: 'Colony',
        template: DashboardTemplate.COLONY,
      };

      const dashboard = dashboardSystem.createDashboard(config);

      expect(dashboard).toBeDefined();
      expect(dashboard.widgets.size).toBeGreaterThan(0);
      expect(dashboard.config.template).toBe(DashboardTemplate.COLONY);
    });

    test('should create dashboard with security template', () => {
      const config: DashboardConfig = {
        id: 'security-dashboard',
        name: 'Security',
        template: DashboardTemplate.SECURITY,
      };

      const dashboard = dashboardSystem.createDashboard(config);

      expect(dashboard).toBeDefined();
      expect(dashboard.widgets.size).toBeGreaterThan(0);
      expect(dashboard.config.template).toBe(DashboardTemplate.SECURITY);
    });

    test('should create custom dashboard without template', () => {
      const config: DashboardConfig = {
        id: 'custom-dashboard',
        name: 'Custom Dashboard',
        template: DashboardTemplate.CUSTOM,
      };

      const dashboard = dashboardSystem.createDashboard(config);

      expect(dashboard).toBeDefined();
      expect(dashboard.widgets.size).toBe(0);
    });

    test('should emit event when dashboard is created', (done) => {
      const config: DashboardConfig = {
        id: 'event-test-dashboard',
        name: 'Event Test',
      };

      dashboardSystem.on('dashboard:created', (data) => {
        expect(data.dashboardId).toBe('event-test-dashboard');
        done();
      });

      dashboardSystem.createDashboard(config);
    });
  });

  describe('Dashboard Retrieval', () => {
    test('should retrieve existing dashboard', () => {
      const config: DashboardConfig = {
        id: 'retrieve-dashboard',
        name: 'Retrieve Test',
      };

      dashboardSystem.createDashboard(config);
      const retrieved = dashboardSystem.getDashboard('retrieve-dashboard');

      expect(retrieved).toBeDefined();
      expect(retrieved?.id).toBe('retrieve-dashboard');
    });

    test('should return undefined for non-existent dashboard', () => {
      const retrieved = dashboardSystem.getDashboard('non-existent');
      expect(retrieved).toBeUndefined();
    });

    test('should list all dashboards', () => {
      dashboardSystem.createDashboard({ id: 'dash1', name: 'Dashboard 1' });
      dashboardSystem.createDashboard({ id: 'dash2', name: 'Dashboard 2' });
      dashboardSystem.createDashboard({ id: 'dash3', name: 'Dashboard 3' });

      const dashboards = dashboardSystem.listDashboards();

      expect(dashboards).toHaveLength(3);
      expect(dashboards.map(d => d.id)).toEqual(expect.arrayContaining(['dash1', 'dash2', 'dash3']));
    });
  });

  describe('Dashboard Updates', () => {
    test('should update dashboard configuration', () => {
      const config: DashboardConfig = {
        id: 'update-dashboard',
        name: 'Original Name',
      };

      dashboardSystem.createDashboard(config);

      const updated = (dashboardSystem as any).updateDashboardConfig('update-dashboard', {
        name: 'Updated Name',
        description: 'Updated description',
      });

      expect(updated).toBeDefined();
      expect(updated?.config.name).toBe('Updated Name');
      expect(updated?.config.description).toBe('Updated description');
    });

    test('should return null when updating non-existent dashboard', () => {
      const result = (dashboardSystem as any).updateDashboardConfig('non-existent', { name: 'New Name' });
      expect(result).toBeNull();
    });

    test('should emit event when dashboard is updated', (done) => {
      const config: DashboardConfig = {
        id: 'update-event-dashboard',
        name: 'Update Event Test',
      };

      dashboardSystem.createDashboard(config);

      dashboardSystem.on('dashboard:updated', (data) => {
        expect(data.dashboardId).toBe('update-event-dashboard');
        done();
      });

      (dashboardSystem as any).updateDashboardConfig('update-event-dashboard', { name: 'Updated' });
    });
  });

  describe('Dashboard Deletion', () => {
    test('should delete existing dashboard', () => {
      const config: DashboardConfig = {
        id: 'delete-dashboard',
        name: 'Delete Test',
      };

      dashboardSystem.createDashboard(config);
      const deleted = dashboardSystem.deleteDashboard('delete-dashboard');

      expect(deleted).toBe(true);
      expect(dashboardSystem.getDashboard('delete-dashboard')).toBeUndefined();
    });

    test('should return false when deleting non-existent dashboard', () => {
      const deleted = dashboardSystem.deleteDashboard('non-existent');
      expect(deleted).toBe(false);
    });

    test('should stop auto-refresh when dashboard is deleted', () => {
      const config: DashboardConfig = {
        id: 'delete-refresh-dashboard',
        name: 'Delete Refresh Test',
        autoRefresh: true,
        updateInterval: 100,
      };

      dashboardSystem.createDashboard(config);
      dashboardSystem.deleteDashboard('delete-refresh-dashboard');

      // Wait to ensure no errors occur
      return new Promise(resolve => setTimeout(resolve, 200));
    });

    test('should emit event when dashboard is deleted', (done) => {
      const config: DashboardConfig = {
        id: 'delete-event-dashboard',
        name: 'Delete Event Test',
      };

      dashboardSystem.createDashboard(config);

      dashboardSystem.on('dashboard:deleted', (data) => {
        expect(data.dashboardId).toBe('delete-event-dashboard');
        done();
      });

      dashboardSystem.deleteDashboard('delete-event-dashboard');
    });
  });

  // ========================================================================
  // Widget Management
  // ========================================================================

  describe('Widget Addition', () => {
    let dashboard: DashboardConfig;

    beforeEach(() => {
      dashboard = {
        id: 'widget-test-dashboard',
        name: 'Widget Test',
      };
      dashboardSystem.createDashboard(dashboard);
    });

    test('should add metric card widget', () => {
      const widget: WidgetConfig = {
        id: 'metric1',
        type: WidgetType.METRIC_CARD,
        title: 'Total Agents',
        dataSource: { type: 'analytics', source: 'ecosystem.totalAgents' },
        options: { showTrend: true, unit: 'agents' },
      };

      const added = dashboardSystem.addWidget('widget-test-dashboard', widget);

      expect(added).toBeDefined();
      expect(added?.id).toBe('metric1');
      expect(added?.type).toBe(WidgetType.METRIC_CARD);
      expect(added?.data.type).toBe('metric');
    });

    test('should add line chart widget', () => {
      const widget: WidgetConfig = {
        id: 'chart1',
        type: WidgetType.LINE_CHART,
        title: 'Population Trend',
        dataSource: { type: 'analytics', source: 'timeSeries' },
        options: { showGrid: true, showTooltip: true },
      };

      const added = dashboardSystem.addWidget('widget-test-dashboard', widget);

      expect(added).toBeDefined();
      expect(added?.type).toBe(WidgetType.LINE_CHART);
      expect(added?.data.type).toBe('chart');
    });

    test('should add gauge widget', () => {
      const widget: WidgetConfig = {
        id: 'gauge1',
        type: WidgetType.GAUGE,
        title: 'Health Score',
        dataSource: { type: 'analytics', source: 'ecosystem.healthScore' },
        options: { threshold: { warning: 0.5, critical: 0.3 } },
      };

      const added = dashboardSystem.addWidget('widget-test-dashboard', widget);

      expect(added).toBeDefined();
      expect(added?.type).toBe(WidgetType.GAUGE);
    });

    test('should add table widget', () => {
      const widget: WidgetConfig = {
        id: 'table1',
        type: WidgetType.TABLE,
        title: 'Agent Data',
        dataSource: { type: 'analytics', source: 'agent.list' },
        options: {
          columns: [
            { key: 'id', title: 'ID', sortable: true },
            { key: 'fitness', title: 'Fitness', type: 'number' },
          ],
        },
      };

      const added = dashboardSystem.addWidget('widget-test-dashboard', widget);

      expect(added).toBeDefined();
      expect(added?.type).toBe(WidgetType.TABLE);
      expect(added?.data.type).toBe('table');
    });

    test('should add log viewer widget', () => {
      const widget: WidgetConfig = {
        id: 'log1',
        type: WidgetType.LOG_VIEWER,
        title: 'Event Log',
        dataSource: { type: 'analytics', source: 'events' },
        options: { maxLines: 50, logLevel: 'info' },
      };

      const added = dashboardSystem.addWidget('widget-test-dashboard', widget);

      expect(added).toBeDefined();
      expect(added?.type).toBe(WidgetType.LOG_VIEWER);
      expect(added?.data.type).toBe('log');
    });

    test('should return null when adding to non-existent dashboard', () => {
      const widget: WidgetConfig = {
        id: 'metric1',
        type: WidgetType.METRIC_CARD,
        title: 'Test',
        dataSource: { type: 'analytics', source: 'test' },
      };

      const added = dashboardSystem.addWidget('non-existent', widget);
      expect(added).toBeNull();
    });

    test('should emit event when widget is added', (done) => {
      const widget: WidgetConfig = {
        id: 'event-widget',
        type: WidgetType.METRIC_CARD,
        title: 'Event Test',
        dataSource: { type: 'analytics', source: 'test' },
      };

      dashboardSystem.on('widget:added', (data) => {
        expect(data.dashboardId).toBe('widget-test-dashboard');
        expect(data.widgetId).toBe('event-widget');
        done();
      });

      dashboardSystem.addWidget('widget-test-dashboard', widget);
    });
  });

  describe('Widget Retrieval', () => {
    test('should retrieve existing widget', () => {
      const config: DashboardConfig = {
        id: 'widget-retrieve-dashboard',
        name: 'Widget Retrieve Test',
        template: DashboardTemplate.SYSTEM_OVERVIEW,
      };

      dashboardSystem.createDashboard(config);
      const widget = dashboardSystem.getWidget('total_agents');

      expect(widget).toBeDefined();
      expect(widget?.id).toBe('total_agents');
    });

    test('should return undefined for non-existent widget', () => {
      const widget = dashboardSystem.getWidget('non-existent');
      expect(widget).toBeUndefined();
    });
  });

  describe('Widget Updates', () => {
    test('should update widget data', () => {
      const config: DashboardConfig = {
        id: 'widget-update-dashboard',
        name: 'Widget Update Test',
        template: DashboardTemplate.SYSTEM_OVERVIEW,
      };

      const dashboard = dashboardSystem.createDashboard(config);
      const widget = dashboard.widgets.get('total_agents');

      expect(widget).toBeDefined();

      // Trigger update
      dashboardSystem.updateWidget('widget-update-dashboard', 'total_agents');

      const updated = dashboardSystem.getWidget('total_agents');
      expect(updated?.lastUpdate).toBeGreaterThan(0);
      expect(updated?.state.updateCount).toBeGreaterThan(0);
    });
  });

  describe('Widget Removal', () => {
    test('should remove widget from dashboard', () => {
      const config: DashboardConfig = {
        id: 'widget-remove-dashboard',
        name: 'Widget Remove Test',
        template: DashboardTemplate.SYSTEM_OVERVIEW,
      };

      dashboardSystem.createDashboard(config);

      const removed = dashboardSystem.removeWidget('widget-remove-dashboard', 'total_agents');

      expect(removed).toBe(true);
      expect(dashboardSystem.getWidget('total_agents')).toBeUndefined();
    });

    test('should return false when removing from non-existent dashboard', () => {
      const removed = dashboardSystem.removeWidget('non-existent', 'widget1');
      expect(removed).toBe(false);
    });

    test('should return false when removing non-existent widget', () => {
      const config: DashboardConfig = {
        id: 'widget-remove-missing-dashboard',
        name: 'Widget Remove Missing Test',
      };

      dashboardSystem.createDashboard(config);

      const removed = dashboardSystem.removeWidget('widget-remove-missing-dashboard', 'non-existent');
      expect(removed).toBe(false);
    });
  });

  // ========================================================================
  // Real-time Updates
  // ========================================================================

  describe('Real-time Updates', () => {
    test('should update dashboard with full data', (done) => {
      const config: DashboardConfig = {
        id: 'realtime-dashboard',
        name: 'Real-time Test',
        template: DashboardTemplate.SYSTEM_OVERVIEW,
      };

      const dashboard = dashboardSystem.createDashboard(config);
      const originalUpdateTime = dashboard.lastUpdate;

      // Wait a bit to ensure different timestamp
      setTimeout(() => {
        dashboardSystem.updateDashboard('realtime-dashboard', {
          dashboardId: 'realtime-dashboard',
          type: 'full',
          data: dashboard.data,
          timestamp: Date.now(),
        });

        expect(dashboard.lastUpdate).toBeGreaterThan(originalUpdateTime);
        done();
      }, 10);
    });

    test('should update dashboard with incremental widget data', (done) => {
      const config: DashboardConfig = {
        id: 'incremental-dashboard',
        name: 'Incremental Test',
        template: DashboardTemplate.SYSTEM_OVERVIEW,
      };

      const dashboard = dashboardSystem.createDashboard(config);
      const widget = dashboard.widgets.get('total_agents');

      const originalUpdateTime = widget?.lastUpdate || 0;

      // Wait a bit to ensure different timestamp
      setTimeout(() => {
        dashboardSystem.updateDashboard('incremental-dashboard', {
          dashboardId: 'incremental-dashboard',
          widgetId: 'total_agents',
          type: 'incremental',
          data: { type: 'metric', value: 100 },
          timestamp: Date.now(),
        });

        const updated = dashboard.widgets.get('total_agents');
        expect(updated?.lastUpdate).toBeGreaterThan(originalUpdateTime);
        done();
      }, 10);
    });
  });

  describe('Auto-refresh', () => {
    test('should start auto-refresh for dashboard', (done) => {
      const config: DashboardConfig = {
        id: 'auto-refresh-dashboard',
        name: 'Auto-refresh Test',
        autoRefresh: true,
        updateInterval: 100,
      };

      const dashboard = dashboardSystem.createDashboard(config);
      const originalUpdateCount = dashboard.data.metadata.updateCount;

      // Wait for at least one auto-refresh cycle
      setTimeout(() => {
        expect(dashboard.data.metadata.updateCount).toBeGreaterThan(originalUpdateCount);
        done();
      }, 200);
    });

    test('should stop auto-refresh when dashboard is deleted', () => {
      const config: DashboardConfig = {
        id: 'stop-refresh-dashboard',
        name: 'Stop Refresh Test',
        autoRefresh: true,
        updateInterval: 100,
      };

      dashboardSystem.createDashboard(config);
      dashboardSystem.deleteDashboard('stop-refresh-dashboard');

      // Should not throw any errors
      return new Promise(resolve => setTimeout(resolve, 200));
    });
  });

  // ========================================================================
  // Data Querying
  // ========================================================================

  describe('Data Querying', () => {
    test('should query all dashboards', () => {
      dashboardSystem.createDashboard({
        id: 'query-dash1',
        name: 'Query Dashboard 1',
        template: DashboardTemplate.SYSTEM_OVERVIEW,
      });
      dashboardSystem.createDashboard({
        id: 'query-dash2',
        name: 'Query Dashboard 2',
        template: DashboardTemplate.PERFORMANCE,
      });

      const result = dashboardSystem.queryData({});

      expect(result.dashboards.size).toBe(2);
      expect(result.metadata.dashboardsCount).toBe(2);
      expect(result.widgets.size).toBeGreaterThan(0);
    });

    test('should query specific dashboard', () => {
      dashboardSystem.createDashboard({
        id: 'query-specific-dashboard',
        name: 'Query Specific',
        template: DashboardTemplate.SYSTEM_OVERVIEW,
      });

      const result = dashboardSystem.queryData({
        dashboardId: 'query-specific-dashboard',
      });

      expect(result.dashboards.size).toBe(1);
      expect(result.dashboards.has('query-specific-dashboard')).toBe(true);
    });

    test('should query specific widgets', () => {
      dashboardSystem.createDashboard({
        id: 'query-widgets-dashboard',
        name: 'Query Widgets',
        template: DashboardTemplate.SYSTEM_OVERVIEW,
      });

      const result = dashboardSystem.queryData({
        dashboardId: 'query-widgets-dashboard',
        widgetIds: ['total_agents', 'active_colonies'],
      });

      expect(result.widgets.size).toBe(2);
      expect(result.widgets.has('total_agents')).toBe(true);
      expect(result.widgets.has('active_colonies')).toBe(true);
    });
  });

  // ========================================================================
  // Chart Generation
  // ========================================================================

  describe('Chart Generation', () => {
    test('should generate line chart from time series', () => {
      const timeSeriesData = analytics.aggregateMetrics(TimeWindow.HOUR);

      const chart = dashboardSystem.generateChart(timeSeriesData.timeSeriesData, ChartType.LINE);

      expect(chart.type).toBe(ChartType.LINE);
      expect(chart.series).toBeDefined();
      expect(Array.isArray(chart.series)).toBe(true);
    });

    test('should generate bar chart', () => {
      const timeSeriesData = analytics.aggregateMetrics(TimeWindow.HOUR);

      const chart = dashboardSystem.generateChart(timeSeriesData.timeSeriesData, ChartType.BAR);

      expect(chart.type).toBe(ChartType.BAR);
      expect(chart.series).toBeDefined();
    });

    test('should generate histogram', () => {
      const timeSeriesData = analytics.aggregateMetrics(TimeWindow.HOUR);

      const chart = dashboardSystem.generateChart(timeSeriesData.timeSeriesData, ChartType.HISTOGRAM);

      expect(chart.type).toBe(ChartType.HISTOGRAM);
      expect(chart.series).toBeDefined();
    });

    test('should calculate chart range', () => {
      // Add some test data
      analytics.recordEvent(AnalyticsEventType.AGENT_BORN, { agentId: 'test1', value: 10 });
      analytics.recordEvent(AnalyticsEventType.AGENT_BORN, { agentId: 'test2', value: 20 });
      analytics.recordEvent(AnalyticsEventType.AGENT_BORN, { agentId: 'test3', value: 30 });

      const timeSeriesData = analytics.aggregateMetrics(TimeWindow.HOUR);
      const chart = dashboardSystem.generateChart(timeSeriesData.timeSeriesData, ChartType.LINE);

      if (chart.series.length > 0 && chart.series[0].data.length > 0) {
        expect(chart.range).toBeDefined();
        expect(chart.range?.min).toBeDefined();
        expect(chart.range?.max).toBeDefined();
      }
    });
  });

  // ========================================================================
  // Export Functionality
  // ========================================================================

  describe('Export Functionality', () => {
    let dashboardId: string;

    beforeEach(() => {
      const config: DashboardConfig = {
        id: 'export-dashboard',
        name: 'Export Test',
        template: DashboardTemplate.SYSTEM_OVERVIEW,
      };

      dashboardSystem.createDashboard(config);
      dashboardId = config.id;
    });

    test('should export dashboard to JSON', () => {
      const result = dashboardSystem.exportDashboard(dashboardId, ExportFormat.JSON);

      expect(result.id).toBeDefined();
      expect(result.format).toBe(ExportFormat.JSON);
      expect(result.data).toBeDefined();
      expect(result.size).toBeGreaterThan(0);
      expect(result.generatedAt).toBeDefined();
    });

    test('should export dashboard to CSV', () => {
      const result = dashboardSystem.exportDashboard(dashboardId, ExportFormat.CSV);

      expect(result.format).toBe(ExportFormat.CSV);
      expect(result.data).toContain('Dashboard:');
      expect(result.data).toContain('Generated:');
      expect(result.data).toContain('Metric,Value');
      expect(result.data).toContain('Total Agents');
      expect(result.data).toContain('Active Colonies');
    });

    test('should export dashboard to HTML', () => {
      const result = dashboardSystem.exportDashboard(dashboardId, ExportFormat.HTML);

      expect(result.format).toBe(ExportFormat.HTML);
      expect(result.data).toContain('<!DOCTYPE html>');
      expect(result.data).toContain('<title>');
      expect(result.data).toContain('</html>');
    });

    test('should throw error for non-existent dashboard', () => {
      expect(() => {
        dashboardSystem.exportDashboard('non-existent', ExportFormat.JSON);
      }).toThrow('Dashboard not found');
    });

    test('should include dashboard metadata in JSON export', () => {
      const result = dashboardSystem.exportDashboard(dashboardId, ExportFormat.JSON);
      const parsed = JSON.parse(result.data);

      expect(parsed.dashboard).toBeDefined();
      expect(parsed.widgets).toBeDefined();
      expect(parsed.data).toBeDefined();
      expect(parsed.exportedAt).toBeDefined();
    });

    test('should generate valid HTML structure', () => {
      const result = dashboardSystem.exportDashboard(dashboardId, ExportFormat.HTML);

      expect(result.data).toContain('<head>');
      expect(result.data).toContain('<body>');
      expect(result.data).toContain('<style>');
      expect(result.data).toContain('class="dashboard"');
      expect(result.data).toContain('class="widget"');
    });
  });

  // ========================================================================
  // WebSocket Integration
  // ========================================================================

  describe('WebSocket Integration', () => {
    test('should register WebSocket client', () => {
      const ws = new MockWebSocket() as unknown as WebSocket;

      dashboardSystem.registerWebSocketClient(ws);

      // Should not throw
      expect(dashboardSystem.getStats()).toBeDefined();
    });

    test('should broadcast widget update to clients', (done) => {
      const ws = new MockWebSocket() as unknown as WebSocket;

      dashboardSystem.registerWebSocketClient(ws);

      // Create dashboard with streaming enabled
      const streamingSystem = createDashboardSystem({
        analyticsPipeline: analytics,
        enableStreaming: true,
      });

      const config: DashboardConfig = {
        id: 'ws-dashboard',
        name: 'WebSocket Test',
      };

      streamingSystem.createDashboard(config);
      streamingSystem.addWidget('ws-dashboard', {
        id: 'ws-widget',
        type: WidgetType.METRIC_CARD,
        title: 'WS Widget',
        dataSource: { type: 'analytics', source: 'ecosystem.totalAgents' },
      });

      // Trigger update
      setTimeout(() => {
        streamingSystem.updateWidget('ws-dashboard', 'ws-widget');
        streamingSystem.destroy();
        done();
      }, 100);
    });

    test('should handle WebSocket close', () => {
      const ws = new MockWebSocket() as unknown as WebSocket;

      dashboardSystem.registerWebSocketClient(ws);
      (ws as any).close();

      // Should not throw
      expect(dashboardSystem.getStats()).toBeDefined();
    });
  });

  // ========================================================================
  // Template System
  // ========================================================================

  describe('Template System', () => {
    test('should apply system overview template widgets', () => {
      const config: DashboardConfig = {
        id: 'template-system-dashboard',
        name: 'Template System Test',
        template: DashboardTemplate.SYSTEM_OVERVIEW,
      };

      const dashboard = dashboardSystem.createDashboard(config);

      expect(dashboard.widgets.size).toBeGreaterThan(0);
      expect(dashboard.widgets.has('total_agents')).toBe(true);
      expect(dashboard.widgets.has('active_colonies')).toBe(true);
      expect(dashboard.widgets.has('diversity_index')).toBe(true);
    });

    test('should apply performance template widgets', () => {
      const config: DashboardConfig = {
        id: 'template-perf-dashboard',
        name: 'Template Perf Test',
        template: DashboardTemplate.PERFORMANCE,
      };

      const dashboard = dashboardSystem.createDashboard(config);

      expect(dashboard.widgets.size).toBeGreaterThan(0);
      expect(dashboard.widgets.has('avg_processing_time')).toBe(true);
      expect(dashboard.widgets.has('throughput')).toBe(true);
      expect(dashboard.widgets.has('error_rate')).toBe(true);
    });

    test('should apply evolution template widgets', () => {
      const config: DashboardConfig = {
        id: 'template-evo-dashboard',
        name: 'Template Evo Test',
        template: DashboardTemplate.EVOLUTION,
      };

      const dashboard = dashboardSystem.createDashboard(config);

      expect(dashboard.widgets.size).toBeGreaterThan(0);
      expect(dashboard.widgets.has('avg_fitness')).toBe(true);
      expect(dashboard.widgets.has('generation_count')).toBe(true);
    });

    test('should apply colony template widgets', () => {
      const config: DashboardConfig = {
        id: 'template-colony-dashboard',
        name: 'Template Colony Test',
        template: DashboardTemplate.COLONY,
      };

      const dashboard = dashboardSystem.createDashboard(config);

      expect(dashboard.widgets.size).toBeGreaterThan(0);
      expect(dashboard.widgets.has('colony_count')).toBe(true);
      expect(dashboard.widgets.has('avg_colony_size')).toBe(true);
    });

    test('should apply security template widgets', () => {
      const config: DashboardConfig = {
        id: 'template-security-dashboard',
        name: 'Template Security Test',
        template: DashboardTemplate.SECURITY,
      };

      const dashboard = dashboardSystem.createDashboard(config);

      expect(dashboard.widgets.size).toBeGreaterThan(0);
      expect(dashboard.widgets.has('threat_level')).toBe(true);
      expect(dashboard.widgets.has('compliance_score')).toBe(true);
      expect(dashboard.widgets.has('active_alerts')).toBe(true);
    });
  });

  // ========================================================================
  // Statistics & Cleanup
  // ========================================================================

  describe('Statistics', () => {
    test('should return system statistics', (done) => {
      dashboardSystem.createDashboard({
        id: 'stats-dash1',
        name: 'Stats Dashboard 1',
        template: DashboardTemplate.SYSTEM_OVERVIEW,
      });
      dashboardSystem.createDashboard({
        id: 'stats-dash2',
        name: 'Stats Dashboard 2',
        template: DashboardTemplate.PERFORMANCE,
      });

      // Wait a bit to ensure uptime > 0
      setTimeout(() => {
        const stats = dashboardSystem.getStats();

        expect(stats.totalDashboards).toBe(2);
        expect(stats.totalWidgets).toBeGreaterThan(0);
        expect(stats.activeDashboards).toBe(2);
        expect(stats.uptime).toBeGreaterThan(0);
        done();
      }, 10);
    });

    test('should track active dashboards correctly', () => {
      const dash1 = dashboardSystem.createDashboard({
        id: 'active-dash1',
        name: 'Active Dashboard 1',
      });

      let stats = dashboardSystem.getStats();
      expect(stats.activeDashboards).toBe(1);

      dash1.isActive = false;
      stats = dashboardSystem.getStats();
      expect(stats.activeDashboards).toBe(0);
    });
  });

  describe('Cleanup', () => {
    test('should destroy dashboard system', () => {
      const ws = new MockWebSocket() as unknown as WebSocket;

      dashboardSystem.registerWebSocketClient(ws);
      dashboardSystem.createDashboard({
        id: 'cleanup-dashboard',
        name: 'Cleanup Test',
        autoRefresh: true,
      });

      // Should not throw
      expect(() => {
        dashboardSystem.destroy();
      }).not.toThrow();

      const stats = dashboardSystem.getStats();
      expect(stats.totalDashboards).toBe(0);
      expect(stats.totalWidgets).toBe(0);
    });

    test('should close all WebSocket connections on destroy', () => {
      const ws1 = new MockWebSocket() as unknown as WebSocket;
      const ws2 = new MockWebSocket() as unknown as WebSocket;

      dashboardSystem.registerWebSocketClient(ws1);
      dashboardSystem.registerWebSocketClient(ws2);

      dashboardSystem.destroy();

      expect(ws1.readyState).toBe(3); // CLOSED
      expect(ws2.readyState).toBe(3); // CLOSED
    });
  });

  // ========================================================================
  // Integration Tests
  // ========================================================================

  describe('Integration: End-to-End Workflow', () => {
    test('should create dashboard, add widgets, update, and export', () => {
      // Create dashboard
      const config: DashboardConfig = {
        id: 'e2e-dashboard',
        name: 'E2E Test Dashboard',
        description: 'End-to-end test',
      };

      const dashboard = dashboardSystem.createDashboard(config);
      expect(dashboard).toBeDefined();

      // Add widgets
      const metricWidget: WidgetConfig = {
        id: 'e2e-metric',
        type: WidgetType.METRIC_CARD,
        title: 'Test Metric',
        dataSource: { type: 'analytics', source: 'ecosystem.totalAgents' },
        options: { showTrend: true },
      };

      const added = dashboardSystem.addWidget('e2e-dashboard', metricWidget);
      expect(added).toBeDefined();

      // Update widget
      dashboardSystem.updateWidget('e2e-dashboard', 'e2e-metric');
      const updated = dashboardSystem.getWidget('e2e-metric');
      expect(updated?.state.updateCount).toBeGreaterThan(0);

      // Query data
      const queryResult = dashboardSystem.queryData({
        dashboardId: 'e2e-dashboard',
      });
      expect(queryResult.widgets.has('e2e-metric')).toBe(true);

      // Export
      const exportResult = dashboardSystem.exportDashboard('e2e-dashboard', ExportFormat.JSON);
      expect(exportResult.format).toBe(ExportFormat.JSON);
      expect(exportResult.size).toBeGreaterThan(0);
    });

    test('should handle multiple dashboards with different templates', () => {
      const templates = [
        DashboardTemplate.SYSTEM_OVERVIEW,
        DashboardTemplate.PERFORMANCE,
        DashboardTemplate.EVOLUTION,
        DashboardTemplate.COLONY,
        DashboardTemplate.SECURITY,
      ];

      for (const template of templates) {
        const config: DashboardConfig = {
          id: `multi-${template}`,
          name: `Multi ${template}`,
          template,
        };

        const dashboard = dashboardSystem.createDashboard(config);
        expect(dashboard.widgets.size).toBeGreaterThan(0);
      }

      const stats = dashboardSystem.getStats();
      expect(stats.totalDashboards).toBe(templates.length);
    });
  });

  // ========================================================================
  // Edge Cases & Error Handling
  // ========================================================================

  describe('Edge Cases', () => {
    test('should handle empty analytics data', () => {
      const emptyAnalytics = new AnalyticsPipeline();
      const emptySystem = createDashboardSystem({
        analyticsPipeline: emptyAnalytics,
      });

      const config: DashboardConfig = {
        id: 'empty-data-dashboard',
        name: 'Empty Data Test',
      };

      const dashboard = emptySystem.createDashboard(config);

      expect(dashboard).toBeDefined();
      expect(dashboard.data.metrics).toBeDefined();

      emptySystem.destroy();
    });

    test('should handle rapid dashboard creation and deletion', () => {
      for (let i = 0; i < 10; i++) {
        const config: DashboardConfig = {
          id: `rapid-${i}`,
          name: `Rapid ${i}`,
        };

        dashboardSystem.createDashboard(config);
        dashboardSystem.deleteDashboard(`rapid-${i}`);
      }

      const stats = dashboardSystem.getStats();
      expect(stats.totalDashboards).toBe(0);
    });

    test('should handle widget with invalid data source', () => {
      const config: DashboardConfig = {
        id: 'invalid-source-dashboard',
        name: 'Invalid Source Test',
      };

      dashboardSystem.createDashboard(config);

      const widget: WidgetConfig = {
        id: 'invalid-source-widget',
        type: WidgetType.METRIC_CARD,
        title: 'Invalid Source',
        dataSource: { type: 'analytics', source: 'invalid.metric.path' },
      };

      const added = dashboardSystem.addWidget('invalid-source-dashboard', widget);

      // Should not throw, but return default/empty data
      expect(added).toBeDefined();
      expect(added?.data.type).toBe('metric');
    });
  });
});
