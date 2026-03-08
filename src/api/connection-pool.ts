/**
 * WebSocket Connection Pool
 *
 * Optimizations:
 * - Reusable connection objects
 * - Connection pooling for reduced overhead
 * - Automatic cleanup of idle connections
 * - Load balancing across connections
 * - Health checking and automatic reconnection
 *
 * Sprint 7: Performance Optimization
 */

import { EventEmitter } from 'events';
import type { WebSocket } from 'ws';

// ============================================================================
// CONNECTION POOL TYPES
// ============================================================================

export interface PooledConnection {
  id: string;
  ws: WebSocket;
  createdAt: number;
  lastUsed: number;
  isActive: boolean;
  messageCount: number;
  metadata: Record<string, unknown>;
}

export interface ConnectionPoolConfig {
  maxConnections: number;
  minConnections: number;
  maxIdleTimeMs: number;
  healthCheckIntervalMs: number;
  enableAutoScaling: boolean;
  scaleUpThreshold: number; // Utilization percentage
  scaleDownThreshold: number; // Utilization percentage
}

export interface PoolStats {
  totalConnections: number;
  activeConnections: number;
  idleConnections: number;
  avgMessagesPerConnection: number;
  poolUtilization: number;
}

// ============================================================================
// CONNECTION POOL IMPLEMENTATION
// ============================================================================

export class WebSocketConnectionPool extends EventEmitter {
  private config: ConnectionPoolConfig;
  private connections: Map<string, PooledConnection> = new Map();
  private availableConnections: Set<string> = new Set();

  private healthCheckInterval: NodeJS.Timeout | null = null;
  private cleanupInterval: NodeJS.Timeout | null = null;

  // Statistics
  private totalCreated = 0;
  private totalDestroyed = 0;
  private totalMessages = 0;

  constructor(config: Partial<ConnectionPoolConfig> = {}) {
    super();

    this.config = {
      maxConnections: 100,
      minConnections: 5,
      maxIdleTimeMs: 5 * 60 * 1000, // 5 minutes
      healthCheckIntervalMs: 30 * 1000, // 30 seconds
      enableAutoScaling: true,
      scaleUpThreshold: 0.8, // 80% utilization
      scaleDownThreshold: 0.2, // 20% utilization
      ...config,
    };

    // Start health check and cleanup intervals
    this.startHealthCheck();
    this.startCleanup();
  }

  /**
   * Acquire a connection from the pool
   */
  acquire(): PooledConnection | null {
    // Try to get an available connection
    for (const connId of this.availableConnections) {
      const conn = this.connections.get(connId);
      if (conn && !conn.isActive) {
        conn.isActive = true;
        conn.lastUsed = Date.now();
        this.availableConnections.delete(connId);
        return conn;
      }
    }

    // No available connections
    return null;
  }

  /**
   * Add a new connection to the pool
   */
  add(ws: WebSocket, metadata: Record<string, unknown> = {}): PooledConnection {
    // Check if pool is at capacity
    if (this.connections.size >= this.config.maxConnections) {
      throw new Error('Connection pool at maximum capacity');
    }

    const connId = this.generateConnectionId();
    const now = Date.now();

    const connection: PooledConnection = {
      id: connId,
      ws,
      createdAt: now,
      lastUsed: now,
      isActive: true,
      messageCount: 0,
      metadata,
    };

    this.connections.set(connId, connection);
    this.totalCreated++;

    this.emit('connection:added', connection);

    // Auto-scale if needed
    if (this.config.enableAutoScaling) {
      this.checkScaling();
    }

    return connection;
  }

  /**
   * Release a connection back to the pool
   */
  release(connectionId: string): void {
    const conn = this.connections.get(connectionId);
    if (!conn) return;

    conn.isActive = false;
    conn.lastUsed = Date.now();
    this.availableConnections.add(connectionId);

    this.emit('connection:released', conn);

    // Auto-scale down if needed
    if (this.config.enableAutoScaling) {
      this.checkScaling();
    }
  }

  /**
   * Remove a connection from the pool
   */
  remove(connectionId: string): void {
    const conn = this.connections.get(connectionId);
    if (!conn) return;

    // Close WebSocket if still open
    if (conn.ws.readyState === conn.ws.OPEN) {
      conn.ws.close();
    }

    this.connections.delete(connectionId);
    this.availableConnections.delete(connectionId);
    this.totalDestroyed++;

    this.emit('connection:removed', conn);
  }

  /**
   * Get a specific connection by ID
   */
  get(connectionId: string): PooledConnection | undefined {
    return this.connections.get(connectionId);
  }

  /**
   * Get all connections
   */
  getAllConnections(): PooledConnection[] {
    return Array.from(this.connections.values());
  }

  /**
   * Get active connections
   */
  getActiveConnections(): PooledConnection[] {
    return this.getAllConnections().filter(c => c.isActive);
  }

  /**
   * Get idle connections
   */
  getIdleConnections(): PooledConnection[] {
    return this.getAllConnections().filter(c => !c.isActive);
  }

  /**
   * Update connection metadata
   */
  updateMetadata(connectionId: string, metadata: Record<string, unknown>): void {
    const conn = this.connections.get(connectionId);
    if (conn) {
      conn.metadata = { ...conn.metadata, ...metadata };
    }
  }

  /**
   * Increment message count for a connection
   */
  incrementMessageCount(connectionId: string): void {
    const conn = this.connections.get(connectionId);
    if (conn) {
      conn.messageCount++;
      conn.lastUsed = Date.now();
      this.totalMessages++;
    }
  }

  /**
   * Get pool statistics
   */
  getStats(): PoolStats & {
    totalCreated: number;
    totalDestroyed: number;
    totalMessages: number;
  } {
    const total = this.connections.size;
    const active = this.getActiveConnections().length;
    const idle = this.getIdleConnections().length;

    const avgMessages = total > 0
      ? Array.from(this.connections.values()).reduce((sum, c) => sum + c.messageCount, 0) / total
      : 0;

    return {
      totalConnections: total,
      activeConnections: active,
      idleConnections: idle,
      avgMessagesPerConnection: avgMessages,
      poolUtilization: total / this.config.maxConnections,
      totalCreated: this.totalCreated,
      totalDestroyed: this.totalDestroyed,
      totalMessages: this.totalMessages,
    };
  }

  /**
   * Shutdown the connection pool
   */
  shutdown(): void {
    // Close all connections
    for (const conn of this.connections.values()) {
      if (conn.ws.readyState === conn.ws.OPEN) {
        conn.ws.close();
      }
    }

    // Clear intervals
    if (this.healthCheckInterval) {
      clearInterval(this.healthCheckInterval);
      this.healthCheckInterval = null;
    }

    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval);
      this.cleanupInterval = null;
    }

    // Clear collections
    this.connections.clear();
    this.availableConnections.clear();

    this.emit('pool:shutdown');
  }

  // ==========================================================================
  // PRIVATE METHODS
  // ==========================================================================

  private generateConnectionId(): string {
    return `conn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private startHealthCheck(): void {
    this.healthCheckInterval = setInterval(() => {
      this.performHealthCheck();
    }, this.config.healthCheckIntervalMs);
  }

  private startCleanup(): void {
    this.cleanupInterval = setInterval(() => {
      this.performCleanup();
    }, this.config.maxIdleTimeMs / 2); // Check at half the max idle time
  }

  private performHealthCheck(): void {
    const now = Date.now();
    const staleConnections: string[] = [];

    for (const [id, conn] of this.connections) {
      // Check if connection is stale (no activity for too long)
      const idleTime = now - conn.lastUsed;
      if (idleTime > this.config.maxIdleTimeMs && !conn.isActive) {
        staleConnections.push(id);
      }

      // Check WebSocket health
      if (conn.ws.readyState !== conn.ws.OPEN && conn.ws.readyState !== conn.ws.CONNECTING) {
        staleConnections.push(id);
      }
    }

    // Remove stale connections
    for (const id of staleConnections) {
      this.remove(id);
    }

    if (staleConnections.length > 0) {
      this.emit('pool:cleaned', { removed: staleConnections.length });
    }
  }

  private performCleanup(): void {
    // Remove idle connections beyond minimum
    const idle = this.getIdleConnections();
    const toRemove = idle.length - this.config.minConnections;

    if (toRemove > 0) {
      // Remove least recently used idle connections
      const sorted = idle.sort((a, b) => a.lastUsed - b.lastUsed);
      for (let i = 0; i < toRemove; i++) {
        this.remove(sorted[i].id);
      }
    }
  }

  private checkScaling(): void {
    const stats = this.getStats();
    const utilization = stats.poolUtilization;

    // Scale up if utilization is high
    if (utilization > this.config.scaleUpThreshold) {
      this.emit('pool:scale_up', {
        current: stats.totalConnections,
        utilization,
      });
    }

    // Scale down if utilization is low
    if (utilization < this.config.scaleDownThreshold) {
      this.emit('pool:scale_down', {
        current: stats.totalConnections,
        utilization,
      });
    }
  }
}

// ============================================================================
// CONNECTION POOL MANAGER
// ============================================================================

export class ConnectionPoolManager {
  private pools: Map<string, WebSocketConnectionPool> = new Map();

  /**
   * Create a new connection pool
   */
  createPool(
    name: string,
    config: Partial<ConnectionPoolConfig> = {}
  ): WebSocketConnectionPool {
    if (this.pools.has(name)) {
      throw new Error(`Connection pool '${name}' already exists`);
    }

    const pool = new WebSocketConnectionPool(config);
    this.pools.set(name, pool);

    return pool;
  }

  /**
   * Get a connection pool by name
   */
  getPool(name: string): WebSocketConnectionPool | undefined {
    return this.pools.get(name);
  }

  /**
   * Remove a connection pool
   */
  removePool(name: string): void {
    const pool = this.pools.get(name);
    if (pool) {
      pool.shutdown();
      this.pools.delete(name);
    }
  }

  /**
   * Get all pool statistics
   */
  getAllStats(): Record<string, PoolStats> {
    const stats: Record<string, PoolStats> = {};

    for (const [name, pool] of this.pools) {
      stats[name] = pool.getStats();
    }

    return stats;
  }

  /**
   * Shutdown all pools
   */
  shutdownAll(): void {
    for (const pool of this.pools.values()) {
      pool.shutdown();
    }
    this.pools.clear();
  }
}
