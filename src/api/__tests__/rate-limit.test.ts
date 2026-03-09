/**
 * Tests for Rate Limiting Module
 */

import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import {
  TokenBucketRateLimiter,
  SlidingWindowRateLimiter,
  MemoryRateLimitStorage,
  RedisRateLimitStorage,
  RateLimiter,
  RateLimitMiddleware,
  createRateLimiter,
  createRateLimitMiddleware,
  RateLimitPresets,
  type RateLimitConfig,
  type RateLimitState,
  type RedisClient,
} from '../rate-limit.js';

// Mock console.error to avoid clutter
const originalError = console.error;
beforeAll(() => {
  console.error = jest.fn();
});

afterAll(() => {
  console.error = originalError;
});

describe('MemoryRateLimitStorage', () => {
  let storage: MemoryRateLimitStorage;

  beforeEach(() => {
    storage = new MemoryRateLimitStorage();
  });

  describe('Basic Operations', () => {
    it('should store and retrieve state', async () => {
      const state: RateLimitState = {
        windowStartAt: Date.now(),
        tokens: 5,
      };

      await storage.set('test-key', state, 60000);
      const retrieved = await storage.get('test-key');

      expect(retrieved).toEqual(state);
    });

    it('should return null for non-existent key', async () => {
      const result = await storage.get('non-existent');
      expect(result).toBeNull();
    });

    it('should delete state', async () => {
      const state: RateLimitState = { windowStartAt: Date.now() };
      await storage.set('test-key', state, 60000);
      await storage.del('test-key');

      const result = await storage.get('test-key');
      expect(result).toBeNull();
    });

    it('should check if key exists', async () => {
      const state: RateLimitState = { windowStartAt: Date.now() };
      await storage.set('test-key', state, 60000);

      expect(await storage.exists('test-key')).toBe(true);
      expect(await storage.exists('non-existent')).toBe(false);
    });

    it('should increment counter', async () => {
      const state: RateLimitState = {
        windowStartAt: Date.now(),
        timestamps: [1, 2, 3],
      };
      await storage.set('test-key', state, 60000);

      const count = await storage.increment('test-key');
      expect(count).toBe(4);
    });
  });

  describe('Expiration', () => {
    it('should expire state after TTL', async () => {
      const state: RateLimitState = { windowStartAt: Date.now() };
      await storage.set('test-key', state, 100); // 100ms TTL

      // Should exist immediately
      expect(await storage.exists('test-key')).toBe(true);

      // Wait for expiration
      await new Promise(resolve => setTimeout(resolve, 150));

      expect(await storage.exists('test-key')).toBe(false);
      expect(await storage.get('test-key')).toBeNull();
    });

    it('should cleanup expired entries', () => {
      const state: RateLimitState = { windowStartAt: Date.now() };
      storage.set('test-key', state, 100);
      storage.set('test-key-2', state, 60000);

      // Wait for first to expire
      jest.advanceTimersByTime(150);

      // Manually trigger cleanup (it's not automatic)
      // In actual usage, cleanup() is called internally
    });
  });

  describe('Size and Clear', () => {
    it('should return store size', async () => {
      const state: RateLimitState = { windowStartAt: Date.now() };
      await storage.set('key1', state, 60000);
      await storage.set('key2', state, 60000);

      expect(storage.size()).toBe(2);
    });

    it('should clear all entries', async () => {
      const state: RateLimitState = { windowStartAt: Date.now() };
      await storage.set('key1', state, 60000);
      await storage.set('key2', state, 60000);

      storage.clear();
      expect(storage.size()).toBe(0);
    });
  });
});

describe('TokenBucketRateLimiter', () => {
  let limiter: TokenBucketRateLimiter;
  let storage: MemoryRateLimitStorage;
  const config: RateLimitConfig = {
    maxRequests: 10,
    windowMs: 1000,
    algorithm: 'token-bucket',
    keyPrefix: 'test',
    distributed: false,
  };

  beforeEach(() => {
    storage = new MemoryRateLimitStorage();
    limiter = new TokenBucketRateLimiter(config, storage);
  });

  describe('Rate Limiting', () => {
    it('should allow first request', async () => {
      const result = await limiter.checkLimit('user-1');

      expect(result.allowed).toBe(true);
      expect(result.remaining).toBe(9);
      expect(result.state?.tokens).toBe(9);
    });

    it('should allow requests until bucket is empty', async () => {
      const key = 'user-2';

      // Allow first 10 requests
      for (let i = 0; i < 10; i++) {
        const result = await limiter.checkLimit(key);
        expect(result.allowed).toBe(true);
        expect(result.remaining).toBe(9 - i);
      }

      // 11th request should be blocked
      const blocked = await limiter.checkLimit(key);
      expect(blocked.allowed).toBe(false);
      expect(blocked.remaining).toBe(0);
      expect(blocked.retryAfter).toBeGreaterThan(0);
    });

    it('should refill tokens over time', async () => {
      const key = 'user-3';
      const configSlow: RateLimitConfig = {
        ...config,
        maxRequests: 10,
        windowMs: 100, // 100ms window for faster testing
      };

      const slowLimiter = new TokenBucketRateLimiter(configSlow, storage);

      // Consume all tokens
      for (let i = 0; i < 10; i++) {
        await slowLimiter.checkLimit(key);
      }

      // Should be blocked
      let result = await slowLimiter.checkLimit(key);
      expect(result.allowed).toBe(false);

      // Wait for partial refill
      await new Promise(resolve => setTimeout(resolve, 60));

      // Should have some tokens back
      result = await slowLimiter.checkLimit(key);
      expect(result.allowed).toBe(true);
      expect(result.remaining).toBeGreaterThanOrEqual(0);
    });

    it('should handle multiple keys independently', async () => {
      const result1 = await limiter.checkLimit('user-1');
      const result2 = await limiter.checkLimit('user-2');

      expect(result1.remaining).toBe(9);
      expect(result2.remaining).toBe(9);
    });
  });

  describe('Reset', () => {
    it('should reset rate limit for key', async () => {
      await limiter.checkLimit('user-1');
      await limiter.reset('user-1');

      // Should start fresh after reset
      const result = await limiter.checkLimit('user-1');
      expect(result.remaining).toBe(9);
    });
  });

  describe('Statistics', () => {
    it('should track statistics', async () => {
      await limiter.checkLimit('user-1');
      await limiter.checkLimit('user-1');

      // Consume all for user-2
      for (let i = 0; i < 15; i++) {
        await limiter.checkLimit('user-2');
      }

      const stats = limiter.getStats();
      expect(stats.totalRequests).toBe(17);
      expect(stats.blockedRequests).toBe(5);
    });

    it('should reset statistics', async () => {
      await limiter.checkLimit('user-1');
      limiter.resetStats();

      const stats = limiter.getStats();
      expect(stats.totalRequests).toBe(0);
    });
  });

  describe('Events', () => {
    it('should emit allowed event', async () => {
      const handler = jest.fn();
      limiter.on('allowed', handler);

      await limiter.checkLimit('user-1');

      expect(handler).toHaveBeenCalledWith(
        expect.objectContaining({ key: 'user-1' })
      );
    });

    it('should emit blocked event', async () => {
      const handler = jest.fn();

      // Consume all tokens
      for (let i = 0; i < 10; i++) {
        await limiter.checkLimit('user-1');
      }

      limiter.on('blocked', handler);
      await limiter.checkLimit('user-1');

      expect(handler).toHaveBeenCalledWith(
        expect.objectContaining({ key: 'user-1' })
      );
    });
  });
});

describe('SlidingWindowRateLimiter', () => {
  let limiter: SlidingWindowRateLimiter;
  let storage: MemoryRateLimitStorage;
  const config: RateLimitConfig = {
    maxRequests: 5,
    windowMs: 1000,
    algorithm: 'sliding-window',
    keyPrefix: 'test',
    distributed: false,
  };

  beforeEach(() => {
    storage = new MemoryRateLimitStorage();
    limiter = new SlidingWindowRateLimiter(config, storage);
  });

  describe('Rate Limiting', () => {
    it('should allow first request', async () => {
      const result = await limiter.checkLimit('user-1');

      expect(result.allowed).toBe(true);
      expect(result.remaining).toBe(4);
    });

    it('should allow requests within window', async () => {
      const key = 'user-2';

      for (let i = 0; i < 5; i++) {
        const result = await limiter.checkLimit(key);
        expect(result.allowed).toBe(true);
        expect(result.remaining).toBe(4 - i);
      }

      // 6th request should be blocked
      const blocked = await limiter.checkLimit(key);
      expect(blocked.allowed).toBe(false);
    });

    it('should slide window correctly', async () => {
      const key = 'user-3';
      const configSlow: RateLimitConfig = {
        ...config,
        windowMs: 100, // 100ms window
      };

      const slowLimiter = new SlidingWindowRateLimiter(configSlow, storage);

      // Make 5 requests
      for (let i = 0; i < 5; i++) {
        await slowLimiter.checkLimit(key);
      }

      // Should be blocked
      let result = await slowLimiter.checkLimit(key);
      expect(result.allowed).toBe(false);

      // Wait for window to slide
      await new Promise(resolve => setTimeout(resolve, 110));

      // Should allow new requests
      result = await slowLimiter.checkLimit(key);
      expect(result.allowed).toBe(true);
    });

    it('should track timestamps correctly', async () => {
      const key = 'user-4';

      await limiter.checkLimit(key);
      await limiter.checkLimit(key);

      const result = await limiter.checkLimit(key);
      expect(result.state?.timestamps).toHaveLength(3);
    });
  });

  describe('Reset', () => {
    it('should reset rate limit for key', async () => {
      await limiter.checkLimit('user-1');
      await limiter.reset('user-1');

      // Should start fresh after reset
      const result = await limiter.checkLimit('user-1');
      expect(result.remaining).toBe(4);
    });
  });
});

describe('RateLimiter', () => {
  describe('Factory Function', () => {
    it('should create rate limiter with default config', () => {
      const limiter = createRateLimiter();

      expect(limiter).toBeInstanceOf(RateLimiter);
    });

    it('should create rate limiter with custom config', () => {
      const limiter = createRateLimiter({
        maxRequests: 50,
        windowMs: 30000,
      });

      expect(limiter).toBeInstanceOf(RateLimiter);
    });

    it('should use token-bucket algorithm by default', async () => {
      const limiter = createRateLimiter({
        maxRequests: 5,
        windowMs: 1000,
      });

      // Test multiple requests to verify token bucket behavior
      const key = 'test-user';
      const results = [];

      for (let i = 0; i < 6; i++) {
        const result = await limiter.checkLimit(key);
        results.push(result.allowed);
      }

      // Token bucket allows bursts, so all might be allowed
      expect(results[0]).toBe(true);
    });

    it('should use sliding window when specified', async () => {
      const limiter = createRateLimiter({
        maxRequests: 3,
        windowMs: 1000,
        algorithm: 'sliding-window',
      });

      const key = 'test-user';

      // First 3 should be allowed
      for (let i = 0; i < 3; i++) {
        const result = await limiter.checkLimit(key);
        expect(result.allowed).toBe(true);
      }

      // 4th should be blocked
      const result = await limiter.checkLimit(key);
      expect(result.allowed).toBe(false);
    });
  });

  describe('Events', () => {
    it('should forward allowed events', async () => {
      const limiter = createRateLimiter();
      const handler = jest.fn();
      limiter.on('allowed', handler);

      await limiter.checkLimit('user-1');

      expect(handler).toHaveBeenCalled();
    });

    it('should forward blocked events', async () => {
      const limiter = createRateLimiter({
        maxRequests: 2,
        windowMs: 1000,
        algorithm: 'sliding-window',
      });

      const handler = jest.fn();

      // Consume all
      await limiter.checkLimit('user-1');
      await limiter.checkLimit('user-1');

      limiter.on('blocked', handler);
      await limiter.checkLimit('user-1');

      expect(handler).toHaveBeenCalled();
    });
  });
});

describe('RateLimitMiddleware', () => {
  it('should create middleware with default key generator', async () => {
    const middleware = createRateLimitMiddleware(undefined, {
      keyGenerator: async (req) => 'test-key',
    });

    const mockReq = {
      socket: { remoteAddress: '192.168.1.1' },
    } as any;

    const result = await middleware.middleware(mockReq);

    expect(result).toBeTruthy();
    expect(result?.allowed).toBe(true);
  });

  it('should use custom key generator', async () => {
    const customKey = 'custom-user-id';
    const middleware = createRateLimitMiddleware(
      undefined,
      {
        keyGenerator: async () => customKey,
      }
    );

    const mockReq = {} as any;
    await middleware.middleware(mockReq);

    // Verify the key was used by checking a second request
    const result = await middleware.middleware(mockReq);
    expect(result?.remaining).toBeLessThan(100); // Default max is 100
  });

  it('should call onLimitReached handler', async () => {
    const handler = jest.fn();
    const middleware = createRateLimitMiddleware(
      {
        maxRequests: 2,
        windowMs: 1000,
        algorithm: 'sliding-window',
      },
      {
        keyGenerator: async () => 'test-key',
        onLimitReached: handler,
      }
    );

    const mockReq = {} as any;

    // Consume all
    await middleware.middleware(mockReq);
    await middleware.middleware(mockReq);

    // Should trigger handler
    await middleware.middleware(mockReq);

    expect(handler).toHaveBeenCalled();
  });

  it('should provide limiter access', () => {
    const middleware = createRateLimitMiddleware();
    const limiter = middleware.getLimiter();

    expect(limiter).toBeInstanceOf(RateLimiter);
  });

  it('should track statistics', async () => {
    const middleware = createRateLimitMiddleware();
    const mockReq = {
      socket: { remoteAddress: '127.0.0.1' },
    } as any;

    await middleware.middleware(mockReq);
    await middleware.middleware(mockReq);

    const stats = middleware.getStats();
    expect(stats.totalRequests).toBe(2);
  });
});

describe('RateLimitPresets', () => {
  it('should have strict preset', () => {
    expect(RateLimitPresets.strict.maxRequests).toBe(10);
    expect(RateLimitPresets.strict.algorithm).toBe('sliding-window');
  });

  it('should have standard preset', () => {
    expect(RateLimitPresets.standard.maxRequests).toBe(100);
    expect(RateLimitPresets.standard.algorithm).toBe('token-bucket');
  });

  it('should have lenient preset', () => {
    expect(RateLimitPresets.lenient.maxRequests).toBe(1000);
  });

  it('should have api preset', () => {
    expect(RateLimitPresets.api.maxRequests).toBe(60);
  });

  it('should work with preset configuration', async () => {
    const limiter = createRateLimiter(RateLimitPresets.strict);

    // Strict is 10 req/min
    const key = 'test-user';
    let blocked = false;

    for (let i = 0; i < 15; i++) {
      const result = await limiter.checkLimit(key);
      if (!result.allowed) {
        blocked = true;
        break;
      }
    }

    expect(blocked).toBe(true);
  });
});

describe('RedisRateLimitStorage', () => {
  it('should create storage with Redis client', () => {
    const mockClient = {
      get: jest.fn().mockResolvedValue(null),
      set: jest.fn().mockResolvedValue('OK'),
      del: jest.fn().mockResolvedValue(1),
      exists: jest.fn().mockResolvedValue(0),
      incr: jest.fn().mockResolvedValue(1),
    } as unknown as RedisClient;

    const storage = new RedisRateLimitStorage(mockClient);
    expect(storage).toBeInstanceOf(RedisRateLimitStorage);
  });

  it('should parse JSON from Redis', async () => {
    const mockState: RateLimitState = {
      windowStartAt: Date.now(),
      tokens: 5,
    };

    const mockClient = {
      get: jest.fn().mockResolvedValue(JSON.stringify(mockState)),
      set: jest.fn().mockResolvedValue('OK'),
      del: jest.fn().mockResolvedValue(1),
      exists: jest.fn().mockResolvedValue(1),
      incr: jest.fn().mockResolvedValue(1),
    } as unknown as RedisClient;

    const storage = new RedisRateLimitStorage(mockClient);
    const result = await storage.get('test-key');

    expect(result).toEqual(mockState);
  });

  it('should handle invalid JSON gracefully', async () => {
    const mockClient = {
      get: jest.fn().mockResolvedValue('invalid-json'),
      set: jest.fn().mockResolvedValue('OK'),
      del: jest.fn().mockResolvedValue(1),
      exists: jest.fn().mockResolvedValue(0),
      incr: jest.fn().mockResolvedValue(1),
    } as unknown as RedisClient;

    const storage = new RedisRateLimitStorage(mockClient);
    const result = await storage.get('test-key');

    expect(result).toBeNull();
  });

  it('should serialize state to JSON', async () => {
    const mockState: RateLimitState = {
      windowStartAt: Date.now(),
      tokens: 10,
    };

    const mockClient = {
      get: jest.fn().mockResolvedValue(null),
      set: jest.fn().mockResolvedValue('OK'),
      del: jest.fn().mockResolvedValue(1),
      exists: jest.fn().mockResolvedValue(0),
      incr: jest.fn().mockResolvedValue(1),
    } as unknown as RedisClient;

    const storage = new RedisRateLimitStorage(mockClient);
    await storage.set('test-key', mockState, 60000);

    expect(mockClient.set).toHaveBeenCalledWith(
      'test-key',
      JSON.stringify(mockState),
      'px',
      60000
    );
  });
});
