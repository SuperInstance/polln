import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { Button } from '../ui/Button';
import AnalyticsChart from './AnalyticsChart';

interface AnalyticsData {
  pageViews: number;
  uniqueVisitors: number;
  bounceRate: number;
  averageTimeOnSite: number;
  topPages: { page: string; views: number; }[];
  topReferrers: { referrer: string; visits: number; }[];
  geoData: { country: string; visitors: number; }[];
  events: { event: string; count: number; }[];
}

interface RealTimeData {
  activeVisitors: number;
  pageViews: number;
  topPages: { page: string; views: number; }[];
  events: { event: string; count: number; }[];
}

const AnalyticsDashboard: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState<'day' | 'week' | 'month'>('week');
  const [realTimeData, setRealTimeData] = useState<RealTimeData>({
    activeVisitors: 0,
    pageViews: 0,
    topPages: [],
    events: []
  });
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData>({
    pageViews: 0,
    uniqueVisitors: 0,
    bounceRate: 0,
    averageTimeOnSite: 0,
    topPages: [],
    topReferrers: [],
    geoData: [],
    events: []
  });

  // Mock data - in real implementation, fetch from Plausible API
  useEffect(() => {
    // Simulate real-time data updates
    const interval = setInterval(() => {
      setRealTimeData(prev => ({
        ...prev,
        activeVisitors: Math.floor(Math.random() * 50) + 10,
        pageViews: prev.pageViews + Math.floor(Math.random() * 5)
      }));
    }, 5000);

    // Load initial data
    setAnalyticsData({
      pageViews: 12543,
      uniqueVisitors: 8932,
      bounceRate: 42.3,
      averageTimeOnSite: 267,
      topPages: [
        { page: '/', views: 3245 },
        { page: '/demos/spreadsheet', views: 2156 },
        { page: '/tutorials', views: 1823 },
        { page: '/white-papers', views: 1234 },
        { page: '/about', views: 876 }
      ],
      topReferrers: [
        { referrer: 'Direct', visits: 4321 },
        { referrer: 'Google', visits: 3211 },
        { referrer: 'Twitter', visits: 876 },
        { referrer: 'GitHub', visits: 543 },
        { referrer: 'Reddit', visits: 321 }
      ],
      geoData: [
        { country: 'United States', visitors: 5432 },
        { country: 'United Kingdom', visitors: 2134 },
        { country: 'Canada', visitors: 1432 },
        { country: 'Germany', visitors: 987 },
        { country: 'Australia', visitors: 654 }
      ],
      events: [
        { event: 'tutorial_start', count: 1567 },
        { event: 'demo_interaction', count: 1234 },
        { event: 'white_paper_download', count: 987 },
        { event: 'age_group_selected', count: 876 },
        { event: 'learning_path_started', count: 654 }
      ]
    });

    return () => clearInterval(interval);
  }, []);

  const downloadReport = (format: 'csv' | 'json') => {
    const data = format === 'csv'
      ? convertToCSV(analyticsData)
      : JSON.stringify(analyticsData, null, 2);

    const blob = new Blob([data], { type: format === 'csv' ? 'text/csv' : 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics-report-${new Date().toISOString()}.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const convertToCSV = (data: AnalyticsData) => {
    const headers = ['Metric', 'Value'];
    const rows = [
      ['Page Views', data.pageViews.toString()],
      ['Unique Visitors', data.uniqueVisitors.toString()],
      ['Bounce Rate', `${data.bounceRate}%`],
      ['Avg Time (seconds)', data.averageTimeOnSite.toString()]
    ];

    return [headers, ...rows].map(row => row.join(',')).join('\n');
  };

  return (
    <div className="space-y-6">
      {/* Real-time Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Active Visitors</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-primary-600">{realTimeData.activeVisitors}</div>
            <p className="text-sm text-gray-600 mt-1">Currently online</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Total Page Views</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-accent-600">{analyticsData.pageViews.toLocaleString()}</div>
            <p className="text-sm text-gray-600 mt-1">Last {selectedPeriod}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Unique Visitors</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-secondary-600">{analyticsData.uniqueVisitors.toLocaleString()}</div>
            <p className="text-sm text-gray-600 mt-1">Last {selectedPeriod}</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Bounce Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-warning-600">{analyticsData.bounceRate}%</div>
            <p className="text-sm text-gray-600 mt-1">Last {selectedPeriod}</p>
          </CardContent>
        </Card>
      </div>

      {/* Time Period Selector */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex gap-2">
          {(['day', 'week', 'month'] as const).map(period => (
            <Button
              key={period}
              variant={selectedPeriod === period ? 'primary' : 'outline'}
              onClick={() => setSelectedPeriod(period)}
            >
              {period.charAt(0).toUpperCase() + period.slice(1)}
            </Button>
          ))}
        </div>

        <div className="flex gap-2">
          <Button variant="outline" onClick={() => downloadReport('csv')}>
            Download CSV
          </Button>
          <Button variant="outline" onClick={() => downloadReport('json')}>
            Download JSON
          </Button>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle>Page Views Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <AnalyticsChart type="line" data={generateTrendData()} height={300} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Visitor Sources</CardTitle>
          </CardHeader>
          <CardContent>
            <AnalyticsChart type="doughnut" data={analyticsData.topReferrers} height={300} />
          </CardContent>
        </Card>
      </div>

      {/* Top Pages and Events */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Top Pages</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {analyticsData.topPages.map((page, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-sm font-medium">{page.page}</span>
                  <span className="text-sm text-gray-600">{page.views.toLocaleString()} views</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Custom Events</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {analyticsData.events.map((event, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-sm font-medium">{event.event.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                  <span className="text-sm text-gray-600">{event.count.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// Helper function to generate mock trend data
const generateTrendData = () => {
  const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  return days.map(day => ({
    label: day,
    value: Math.floor(Math.random() * 2000) + 1000
  }));
};

export default AnalyticsDashboard;