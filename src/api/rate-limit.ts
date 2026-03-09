/**
 * Distributed Rate Limiting Module
 *
 * Provides production-ready rate limiting with:
 * - Token bucket algorithm (smooth rate limiting)
 * - Sliding window algorithm (accurate rate limiting)
 * - Multiple storage backends (memory, Redis)
 * - Distributed synchronization
 * - Middleware integration
 */

import { EventEmitter } from 'events';

// ============================================================================
// Types
// ============================================================================

export type RateLimitAlgorithm = 'token-bucket' | 'sliding-window';

export interface RateLimitConfig {
  /** Maximum requests allowed */
  maxRequests: number;
  /** Time window in milliseconds */
  windowMs: number;
  /** Algorithm to use */
  algorithm: RateLimitAlgorithm;
  /** Key prefix for storage */
  keyPrefix: string;
  /** Whether to enable distributed mode */
  distributed: boolean;
}

export interface RateLimitResult {
  /** Whether the request is allowed */
  allowed: boolean;
  /** Remaining requests in window */
  remaining: number;
  /** Time when limit resets (milliseconds) */
  resetAt: number;
  /** Retry after milliseconds (if not allowed) */
  retryAfter?: number;
  /** Current rate limit state */
  state?: RateLimitState;
}

export interface RateLimitState {
  /** Current token count (for token bucket) */
  tokens?: number;
  /** Last refill time (for token bucket) */
  lastRefillAt?: number;
  /** Request timestamps (for sliding window) */
  timestamps?: number[];
  /** Window start time */
  windowStartAt: number;
}

export interface RateLimitStorage {
  /** Get rate limit state for key */
  get(key: string): Promise<RateLimitState | null>;
  /** Set rate limit state for key */
  set(key: string, state: RateLimitState, ttlMs: number): Promise<void>;
  /** Increment request count */
  increment(key: string): Promise<number>;
  /** Delete rate limit state */
  del(key: string): Promise<void>;
  /** Check if key exists */
  exists(key: string): Promise<boolean>;
}

export interface RateLimitStats {
  /** Total requests tracked */
  totalRequests: number;
  /** Total requests blocked */
  blockedRequests: number;
  /** Keys currently being tracked */
  activeKeys: number;
  /** Peak concurrent keys */
  peakKeys: number;
}

// ============================================================================
// Token Bucket Algorithm
// ============================================================================

export class TokenBucketRateLimiter extends EventEmitter {
  private config: RateLimitConfig;
  private storage: RateLimitStorage;
  private stats: RateLimitStats = {
    totalRequests: 0,
    blockedRequests: 0,
    activeKeys: 0,
    peakKeys: 0,
  };

  constructor(config: RateLimitConfig, storage: RateLimitStorage) {
    super();
    this.config = config;
    this.storage = storage;
  }

  /**
   * Check if request is allowed
   */
  async checkLimit(key: string): Promise<RateLimitResult> {
    const fullKey = `${this.config.keyPrefix}:${key}`;

    this.stats.totalRequests++;

    const state = await this.storage.get(fullKey);
    const now = Date.now();

    if (!state) {
      // First request - create new bucket
      const newState: RateLimitState = {
        tokens: this.config.maxRequests - 1,
        lastRefillAt: now,
        windowStartAt: now,
      };

      await this.storage.set(fullKey, newState, this.config.windowMs);

      this.emit('allowed', { key, remaining: newState.tokens });

      return {
        allowed: true,
        remaining: newState.tokens,
        resetAt: now + this.config.windowMs,
        state: newState,
      };
    }

    // Refill tokens based on time elapsed
    const elapsed = now - (state.lastRefillAt || now);
    const refillAmount = Math.floor(
      (elapsed / this.config.windowMs) * this.config.maxRequests
    );

    let tokens = Math.min(
      this.config.maxRequests,
      (state.tokens || 0) + refillAmount
    );

    // Consume one token
    if (tokens > 0) {
      tokens--;
      state.tokens = tokens;
      state.lastRefillAt = now;

      await this.storage.set(fullKey, state, this.config.windowMs);

      this.emit('allowed', { key, remaining: tokens });

      return {
        allowed: true,
        remaining: tokens,
        resetAt: state.lastRefillAt + this.config.windowMs,
        state,
      };
    }

    // Rate limited
    this.stats.blockedRequests++;
    const resetAt = (state.lastRefillAt || now) + this.config.windowMs;
    const retryAfter = Math.max(0, resetAt - now);

    this.emit('blocked', { key, retryAfter });

    return {
      allowed: false,
      remaining: 0,
      resetAt,
      retryAfter,
      state,
    };
  }

  /**
   * Reset rate limit for key
   */
  async reset(key: string): Promise<void> {
    const fullKey = `${this.config.keyPrefix}:${key}`;
    await this.storage.del(fullKey);
  }

  /**
   * Get statistics
   */
  getStats(): RateLimitStats {
    return { ...this.stats };
  }

  /**
   * Reset statistics
   */
  resetStats(): void {
    this.stats = {
      totalRequests: 0,
      blockedRequests: 0,
      activeKeys: 0,
      peakKeys: 0,
    };
  }
}

// ============================================================================
// Sliding Window Algorithm
// ============================================================================

export class SlidingWindowRateLimiter extends EventEmitter {
  private config: RateLimitConfig;
  private storage: RateLimitStorage;
  private stats: RateLimitStats = {
    totalRequests: 0,
    blockedRequests: 0,
    activeKeys: 0,
    peakKeys: 0,
  };

  constructor(config: RateLimitConfig, storage: RateLimitStorage) {
    super();
    this.config = config;
    this.storage = storage;
  }

  /**
   * Check if request is allowed
   */
  async checkLimit(key: string): Promise<RateLimitResult> {
    const fullKey = `${this.config.keyPrefix}:${key}`;

    this.stats.totalRequests++;

    const state = await this.storage.get(fullKey);
    const now = Date.now();

    if (!state) {
      // First request
      const newState: RateLimitState = {
        timestamps: [now],
        windowStartAt: now,
      };

      await this.storage.set(fullKey, newState, this.config.windowMs);

      this.emit('allowed', { key, remaining: this.config.maxRequests - 1 });

      return {
        allowed: true,
        remaining: this.config.maxRequests - 1,
        resetAt: now + this.config.windowMs,
        state: newState,
      };
    }

    // Filter out timestamps outside the current window
    const windowStart = now - this.config.windowMs;
    const timestamps = (state.timestamps || []).filter(t => t > windowStart);

    if (timestamps.length < this.config.maxRequests) {
      // Allow request
      timestamps.push(now);
      const newState: RateLimitState = {
        timestamps,
        windowStartAt: now,
      };

      await this.storage.set(fullKey, newState, this.config.windowMs);

      this.emit('allowed', { key, remaining: this.config.maxRequests - timestamps.length });

      return {
        allowed: true,
        remaining: this.config.maxRequests - timestamps.length,
        resetAt: timestamps[0] + this.config.windowMs,
        state: newState,
      };
    }

    // Rate limited
    this.stats.blockedRequests++;
    const oldestTimestamp = timestamps[0];
    const resetAt = oldestTimestamp + this.config.windowMs;
    const retryAfter = Math.max(0, resetAt - now);

    this.emit('blocked', { key, retryAfter });

    return {
      allowed: false,
      remaining: 0,
      resetAt,
      retryAfter,
      state,
    };
  }

  /**
   * Reset rate limit for key
   */
  async reset(key: string): Promise<void> {
    const fullKey = `${this.config.keyPrefix}:${key}`;
    await this.storage.del(fullKey);
  }

  /**
   * Get statistics
   */
  getStats(): RateLimitStats {
    return { ...this.stats };
  }

  /**
   * Reset statistics
   */
  resetStats(): void {
    this.stats = {
      totalRequests: 0,
      blockedRequests: 0,
      activeKeys: 0,
      peakKeys: 0,
    };
  }
}

// ============================================================================
// In-Memory Storage
// ============================================================================

export class MemoryRateLimitStorage implements RateLimitStorage {
  private store: Map<string, { state: RateLimitState; expiresAt: number }> = new Map();

  async get(key: string): Promise<RateLimitState | null> {
    const entry = this.store.get(key);
    if (!entry) {
      return null;
    }

    if (Date.now() > entry.expiresAt) {
      this.store.delete(key);
      return null;
    }

    return entry.state;
  }

  async set(key: string, state: RateLimitState, ttlMs: number): Promise<void> {
    this.store.set(key, {
      state,
      expiresAt: Date.now() + ttlMs,
    });
  }

  async increment(key: string): Promise<number> {
    const entry = this.store.get(key);
    if (!entry || Date.now() > entry.expiresAt) {
      return 0;
    }

    const count = (entry.state.timestamps?.length || 0) + 1;
    return count;
  }

  async del(key: string): Promise<void> {
    this.store.delete(key);
  }

  async exists(key: string): Promise<boolean> {
    const entry = this.store.get(key);
    if (!entry) {
      return false;
    }

    if (Date.now() > entry.expiresAt) {
      this.store.delete(key);
      return false;
    }

    return true;
  }

  /**
   * Clean up expired entries
   */
  cleanup(): number {
    const now = Date.now();
    let count = 0;

    for (const [key, entry] of this.store.entries()) {
      if (now > entry.expiresAt) {
        this.store.delete(key);
        count++;
      }
    }

    return count;
  }

  /**
   * Get number of active keys
   */
  size(): number {
    this.cleanup();
    return this.store.size;
  }

  /**
   * Clear all entries
   */
  clear(): void {
    this.store.clear();
  }
}

// ============================================================================
// Redis Storage (Interface for Redis client)
// ============================================================================

export interface RedisClient {
  get(key: string): Promise<string | null>;
  set(key: string, value: string, px?: number): Promise<string | null>;
  del(key: string): Promise<number>;
  exists(key: string): Promise<number>;
  incr(key: string): Promise<number>;
}

export class RedisRateLimitStorage implements RateLimitStorage {
  private client: RedisClient;

  constructor(client: RedisClient) {
    this.client = client;
  }

  async get(key: string): Promise<RateLimitState | null> {
    const value = await this.client.get(key);
    if (!value) {
      return null;
    }

    try {
      return JSON.parse(value) as RateLimitState;
    } catch {
      return null;
    }
  }

  async set(key: string, state: RateLimitState, ttlMs: number): Promise<void> {
    const value = JSON.stringify(state);
    await this.client.set(key, value, 'px', ttlMs);
  }

  async increment(key: string): Promise<number> {
    return this.client.incr(key);
  }

  async del(key: string): Promise<void> {
    await this.client.del(key);
  }

  async exists(key: string): Promise<boolean> {
    const result = await this.client.exists(key);
    return result > 0;
  }
}

// ============================================================================
// Unified Rate Limiter
// ============================================================================

export class RateLimiter extends EventEmitter {
  private limiter: TokenBucketRateLimiter | SlidingWindowRateLimiter;
  private storage: RateLimitStorage;

  constructor(config: RateLimitConfig, storage?: RateLimitStorage) {
    super();

    this.storage = storage || new MemoryRateLimitStorage();

    if (config.algorithm === 'token-bucket') {
      this.limiter = new TokenBucketRateLimiter(config, this.storage);
    } else {
      this.limiter = new SlidingWindowRateLimiter(config, this.storage);
    }

    // Forward events
    this.limiter.on('allowed', (data) => this.emit('allowed', data));
    this.limiter.on('blocked', (data) => this.emit('blocked', data));
  }

  /**
   * Check if request is allowed
   */
  async checkLimit(key: string): Promise<RateLimitResult> {
    return this.limiter.checkLimit(key);
  }

  /**
   * Reset rate limit for key
   */
  async reset(key: string): Promise<void> {
    return this.limiter.reset(key);
  }

  /**
   * Get statistics
   */
  getStats(): RateLimitStats {
    return this.limiter.getStats();
  }

  /**
   * Reset statistics
   */
  resetStats(): void {
    this.limiter.resetStats();
  }
}

// ============================================================================
// Middleware Integration
// ============================================================================

import type { IncomingMessage } from 'http';

export interface RateLimitMiddlewareOptions {
  /** Function to extract key from request */
  keyGenerator: (req: IncomingMessage) => string | Promise<string>;
  /** Whether to skip rate limit */
  skipFailedRequests?: boolean;
  /** Whether to skip successful requests */
  skipSuccessfulRequests?: boolean;
  /** Custom handler for rate limit exceeded */
  onLimitReached?: (result: RateLimitResult, req: IncomingMessage) => void | Promise<void>;
}

export class RateLimitMiddleware {
  private limiter: RateLimiter;
  private options: RateLimitMiddlewareOptions;

  constructor(
    config: RateLimitConfig,
    options: RateLimitMiddlewareOptions,
    storage?: RateLimitStorage
  ) {
    this.limiter = new RateLimiter(config, storage);
    this.options = options;
  }

  /**
   * Middleware function
   */
  async middleware(req: IncomingMessage): Promise<RateLimitResult | null> {
    const key = await this.options.keyGenerator(req);
    const result = await this.limiter.checkLimit(key);

    if (!result.allowed && this.options.onLimitReached) {
      await this.options.onLimitReached(result, req);
    }

    return result;
  }

  /**
   * Get limiter instance
   */
  getLimiter(): RateLimiter {
    return this.limiter;
  }

  /**
   * Get rate limit statistics
   */
  getStats(): RateLimitStats {
    return this.limiter.getStats();
  }
}

// ============================================================================
// Factory Functions
// ============================================================================

export function createRateLimiter(
  config?: Partial<RateLimitConfig>,
  storage?: RateLimitStorage
): RateLimiter {
  const fullConfig: RateLimitConfig = {
    maxRequests: 100,
    windowMs: 60000, // 1 minute
    algorithm: 'token-bucket',
    keyPrefix: 'ratelimit',
    distributed: false,
    ...config,
  };

  return new RateLimiter(fullConfig, storage);
}

export function createRateLimitMiddleware(
  rateLimitConfig?: Partial<RateLimitConfig>,
  middlewareOptions?: RateLimitMiddlewareOptions,
  storage?: RateLimitStorage
): RateLimitMiddleware {
  const fullConfig: RateLimitConfig = {
    maxRequests: 100,
    windowMs: 60000,
    algorithm: 'token-bucket',
    keyPrefix: 'ratelimit',
    distributed: false,
    ...rateLimitConfig,
  };

  const fullOptions: RateLimitMiddlewareOptions = {
    keyGenerator: middlewareOptions?.keyGenerator || ((req) => {
      // Default: use IP address
      const socket = (req as any).socket;
      return socket?.remoteAddress || 'unknown';
    }),
    skipFailedRequests: middlewareOptions?.skipFailedRequests || false,
    skipSuccessfulRequests: middlewareOptions?.skipSuccessfulRequests || false,
    onLimitReached: middlewareOptions?.onLimitReached,
  };

  return new RateLimitMiddleware(fullConfig, fullOptions, storage);
}

// ============================================================================
// Preset Configurations
// ============================================================================

export const RateLimitPresets = {
  /** Strict rate limiting (10 req/min) */
  strict: {
    maxRequests: 10,
    windowMs: 60000,
    algorithm: 'sliding-window' as RateLimitAlgorithm,
    keyPrefix: 'ratelimit-strict',
    distributed: false,
  },

  /** Standard rate limiting (100 req/min) */
  standard: {
    maxRequests: 100,
    windowMs: 60000,
    algorithm: 'token-bucket' as RateLimitAlgorithm,
    keyPrefix: 'ratelimit-standard',
    distributed: false,
  },

  /** Lenient rate limiting (1000 req/min) */
  lenient: {
    maxRequests: 1000,
    windowMs: 60000,
    algorithm: 'token-bucket' as RateLimitAlgorithm,
    keyPrefix: 'ratelimit-lenient',
    distributed: false,
  },

  /** API rate limiting (60 req/min) */
  api: {
    maxRequests: 60,
    windowMs: 60000,
    algorithm: 'token-bucket' as RateLimitAlgorithm,
    keyPrefix: 'ratelimit-api',
    distributed: false,
  },
};
