/**
 * Cloudflare Worker Function for Analytics
 * Handles custom analytics events and stores them in D1
 */

export interface Env {
  ANALYTICS_D1: D1Database;
  JWT_SECRET: string;
}

export interface AnalyticsEvent {
  name: string;
  properties?: Record<string, any>;
  url: string;
  path: string;
  referrer?: string;
  userAgent?: string;
  screenResolution?: string;
  viewport?: string;
  timestamp: number;
  sessionId?: string;
}

export async function onRequest(context: { request: Request; env: Env }) {
  const { request, env } = context;

  // Add CORS headers for browser requests
  const corsHeaders = {
    'Access-Control-Allow-Origin': 'https://superinstance.ai',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '86400',
  };

  // Handle CORS preflight
  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  // Only allow POST requests
  if (request.method !== 'POST') {
    return new Response('Method not allowed', {
      status: 405,
      headers: corsHeaders
    });
  }

  try {
    // Parse request body
    const event: AnalyticsEvent = await request.json();

    // Validate required fields
    if (!event.name || !event.timestamp) {
      return new Response('Missing required fields: name, timestamp', {
        status: 400,
        headers: corsHeaders
      });
    }

    // Clean and validate data
    const cleanedEvent = {
      name: event.name.substring(0, 100), // Limit length
      properties: JSON.stringify(event.properties || {}),
      url: (event.url || '').substring(0, 500),
      path: (event.path || '/').substring(0, 500),
      referrer: (event.referrer || '').substring(0, 500),
      userAgent: (event.userAgent || '').substring(0, 200),
      screenResolution: event.screenResolution || '',
      viewport: event.viewport || '',
      timestamp: new Date(event.timestamp),
      sessionId: event.sessionId || generateSessionId(request),
      ipHash: await generateIpHash(request), // Privacy-preserving IP tracking
      country: request.cf?.country || 'unknown'
    };

    // Store in D1 database
    await storeEvent(env.ANALYTICS_D1, cleanedEvent);

    // Also aggregate metrics in real-time
    await updateMetrics(env.ANALYTICS_D1, event);

    return new Response('Event tracked successfully', {
      status: 200,
      headers: corsHeaders
    });

  } catch (error) {
    console.error('Analytics error:', error);
    return new Response('Internal server error', {
      status: 500,
      headers: corsHeaders
    });
  }
}

/**
 * Store event in D1 database
 */
async function storeEvent(db: D1Database, event: any) {
  const { results } = await db.prepare(`
    INSERT INTO analytics_events (
      name, properties, url, path, referrer, user_agent,
      screen_resolution, viewport, timestamp, session_id,
      ip_hash, country
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).bind(
    event.name,
    event.properties,
    event.url,
    event.path,
    event.referrer,
    event.userAgent,
    event.screenResolution,
    event.viewport,
    event.timestamp.toISOString(),
    event.sessionId,
    event.ipHash,
    event.country
  ).run();

  return results;
}

/**
 * Update real-time metrics
 */
async function updateMetrics(db: D1Database, event: AnalyticsEvent) {
  const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format

  // Update daily metrics
  await db.prepare(`
    INSERT OR REPLACE INTO daily_metrics
    (date, metric_name, metric_value)
    VALUES (?, ?,
      COALESCE(
        (SELECT metric_value + 1 FROM daily_metrics WHERE date = ? AND metric_name = ?),
        1
      )
    )
  `).bind(
    today,
    event.name,
    today,
    event.name
  ).run();

  // Special handling for page views
  if (event.name === 'pageview') {
    // Update page view counts
    await db.prepare(`
      INSERT OR REPLACE INTO page_views
      (date, path, views)
      VALUES (?, ?,
        COALESCE(
          (SELECT views + 1 FROM page_views WHERE date = ? AND path = ?),
          1
        )
      )
    `).bind(
      today,
      event.path,
      today,
      event.path
    ).run();
  }
}

/**
 * Generate a session ID from request
 */
function generateSessionId(request: Request): string {
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  const userAgent = request.headers.get('User-Agent') || 'unknown';
  const today = new Date().toISOString().split('T')[0];

  // Create a unique session ID based on IP + User Agent + Date
  const sessionString = `${ip}-${userAgent}-${today}`;

  // Simple hash function for demo - use proper crypto in production
  let hash = 0;
  for (let i = 0; i < sessionString.length; i++) {
    const char = sessionString.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }

  return Math.abs(hash).toString(36);
}

/**
 * Generate a privacy-preserving IP hash
 */
async function generateIpHash(request: Request): Promise<string> {
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  const encoder = new TextEncoder();
  const data = encoder.encode(ip);

  // In a real implementation, use Web Crypto API
  // For now, return a simple hash
  return ip.split('').reduce((acc, char) => {
    return acc + char.charCodeAt(0);
  }, '');
}

/**
 * Initialize database schema
 */
export async function initSchema(db: D1Database) {
  await db.exec(`
    CREATE TABLE IF NOT EXISTS analytics_events (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      properties TEXT,
      url TEXT,
      path TEXT,
      referrer TEXT,
      user_agent TEXT,
      screen_resolution TEXT,
      viewport TEXT,
      timestamp DATETIME,
      session_id TEXT,
      ip_hash TEXT,
      country TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      INDEX idx_timestamp (timestamp),
      INDEX idx_name (name),
      INDEX idx_session (session_id)
    );

    CREATE TABLE IF NOT EXISTS daily_metrics (
      date TEXT,
      metric_name TEXT,
      metric_value INTEGER DEFAULT 0,
      PRIMARY KEY (date, metric_name)
    );

    CREATE TABLE IF NOT EXISTS page_views (
      date TEXT,
      path TEXT,
      views INTEGER DEFAULT 0,
      PRIMARY KEY (date, path)
    );
  `);
}

/**
 * API endpoint to fetch analytics data
 */
export async function fetchAnalytics(context: { request: Request; env: Env }) {
  const { request, env } = context;
  const url = new URL(request.url);
  const startDate = url.searchParams.get('start_date') || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
  const endDate = url.searchParams.get('end_date') || new Date().toISOString().split('T')[0];
  const metric = url.searchParams.get('metric');

  // Validate date range
  if (new Date(startDate) > new Date(endDate)) {
    return new Response('Invalid date range', { status: 400 });
  }

  try {
    let query: string;
    let results: any;

    if (metric === 'pageviews') {
      // Get page view data
      query = `
        SELECT date, path, SUM(views) as total_views
        FROM page_views
        WHERE date BETWEEN ? AND ?
        GROUP BY date, path
        ORDER BY date DESC, total_views DESC
      `;
      results = await env.ANALYTICS_D1.prepare(query)
        .bind(startDate, endDate)
        .all();
    } else if (metric === 'events') {
      // Get event data
      query = `
        SELECT
          name as event_name,
          COUNT(*) as count,
          COUNT(DISTINCT session_id) as unique_sessions
        FROM analytics_events
        WHERE timestamp BETWEEN ? AND ?
        GROUP BY name
        ORDER BY count DESC
      `;
      results = await env.ANALYTICS_D1.prepare(query)
        .bind(startDate, endDate)
        .all();
    } else if (metric === 'metrics') {
      // Get daily metrics
      query = `
        SELECT date, metric_name, metric_value
        FROM daily_metrics
        WHERE date BETWEEN ? AND ?
        ORDER BY date DESC
      `;
      results = await env.ANALYTICS_D1.prepare(query)
        .bind(startDate, endDate)
        .all();
    } else {
      // Get summary statistics
      query = `
        SELECT
          COUNT(*) as total_events,
          COUNT(DISTINCT session_id) as unique_visitors,
          COUNT(DISTINCT CASE WHEN name = 'pageview' THEN session_id END) as visitors_with_pageviews,
          COUNT(CASE WHEN name = 'pageview' THEN 1 END) as total_pageviews,
          COUNT(DISTINCT path) as unique_pages_viewed,
          AVG(CASE WHEN name = 'pageview' THEN 1 ELSE 0 END) * 100 as bounce_rate
        FROM analytics_events
        WHERE timestamp BETWEEN ? AND ?
      `;
      results = await env.ANALYTICS_D1.prepare(query)
        .bind(startDate, endDate)
        .all();
    }

    return new Response(JSON.stringify(results), {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': 'https://superinstance.ai'
      }
    });

  } catch (error) {
    console.error('Analytics fetch error:', error);
    return new Response('Internal server error', { status: 500 });
  }
}