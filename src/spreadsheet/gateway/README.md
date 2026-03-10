# POLLN API Gateway

**Enterprise API gateway with authentication, rate limiting, circuit breaking, and caching**

---

## Overview

The POLLN API Gateway provides a unified entry point for all API requests with comprehensive middleware for authentication, rate limiting, fault tolerance, and performance optimization.

---

## Features

| Feature | Description |
|---------|-------------|
| **Gateway Server** | HTTP/HTTPS server with request routing and forwarding |
| **Dynamic Routing** | Pattern-based routing with parameter extraction |
| **Rate Limiting** | Token bucket and sliding window algorithms |
| **Circuit Breaker** | Fault tolerance with automatic recovery |
| **Authentication** | JWT, API Key, Session, OAuth providers |
| **Caching** | In-memory LRU/LFU/FIFO cache |
| **Metrics** | Request/response tracking and statistics |

---

## Installation

```bash
# The API gateway is included in POLLN
npm install @polln/gateway
```

---

## Quick Start

### Basic Gateway Server

```typescript
import { GatewayServer } from '@polln/gateway';

const server = new GatewayServer({
  port: 3000,
  host: '0.0.0.0',
  routes: [
    {
      id: 'api-route',
      path: '/api/*',
      methods: ['GET', 'POST', 'PUT', 'DELETE'],
      upstream: {
        host: 'localhost',
        port: 8080,
        protocol: 'http'
      }
    }
  ]
});

await server.start();
console.log('Gateway listening on port 3000');
```

### Configuration

```typescript
import { DEFAULT_GATEWAY_CONFIG } from '@polln/gateway';

const config = {
  ...DEFAULT_GATEWAY_CONFIG,
  port: 3000,
  rateLimit: {
    enabled: true,
    windowMs: 60000,
    maxRequests: 100
  },
  circuitBreaker: {
    enabled: true,
    failureThreshold: 5,
    resetTimeoutMs: 60000
  },
  cache: {
    enabled: true,
    ttl: 300000,
    maxSize: 10000
  }
};
```

---

## Routing

### Dynamic Routes

```typescript
import { GatewayRouter, RouteBuilder } from '@polln/gateway';

const router = new GatewayRouter();

// Using RouteBuilder
const apiRoute = RouteBuilder
  .create('/api/users/:userId')
  .id('user-api')
  .methods('GET', 'PUT', 'DELETE')
  .to('backend', 8080)
  .timeout(30000)
  .build();

router.addRoute(apiRoute);

// Match incoming request
const match = await router.match(request);
if (match) {
  console.log(`Matched route: ${match.route.id}`);
  console.log(`Params: ${JSON.stringify(match.params)}`);
}
```

### Predefined Routes

```typescript
import { CommonRoutes } from '@polln/gateway';

// Health check endpoint
router.addRoute(CommonRoutes.healthCheck('/health'));

// API proxy
router.addRoute(CommonRoutes.apiProxy('/api', 'backend', 8080));

// Static assets
router.addRoute(CommonRoutes.staticAssets('/assets', 'cdn', 9000));

// WebSocket
router.addRoute(CommonRoutes.websocket('/ws', 'websocket', 3001));
```

---

## Rate Limiting

### Token Bucket Rate Limiter

```typescript
import { RateLimiter } from '@polln/gateway';

const limiter = new RateLimiter({
  keyPrefix: 'api-rate-limit',
  maxRequests: 100,
  windowMs: 60000  // 1 minute
});

// Check rate limit
const result = limiter.check('user-123');
if (!result.allowed) {
  console.log('Rate limit exceeded');
  console.log(`Retry after: ${result.resetTime}ms`);
}
```

### Sliding Window Rate Limiter

```typescript
import { SlidingWindowRateLimiter } from '@polln/gateway';

const limiter = new SlidingWindowRateLimiter({
  maxRequests: 100,
  windowMs: 60000,
  precision: 10  // seconds
});

const result = limiter.check('user-123');
console.log(`${result.remaining} requests remaining`);
```

---

## Circuit Breaker

### Fault Tolerance

```typescript
import { CircuitBreaker } from '@polln/gateway';

const breaker = new CircuitBreaker({
  failureThreshold: 5,
  resetTimeoutMs: 60000,
  monitoringPeriodMs: 10000
});

// Execute with circuit breaker protection
try {
  const result = await breaker.execute(async () => {
    return await fetch('https://api.backend.com/data');
  });
  console.log('Request succeeded');
} catch (error) {
  console.error('Circuit breaker opened or request failed:', error);
}

// Check circuit state
const state = breaker.getState();
console.log(`Circuit state: ${state}`); // CLOSED, OPEN, HALF_OPEN

// Get statistics
const stats = breaker.getStatistics();
console.log(`Failure rate: ${stats.failureRate}%`);
```

---

## Authentication

### JWT Authentication

```typescript
import { JWTProvider } from '@polln/gateway';

const jwt = new JWTProvider({
  secret: process.env.JWT_SECRET || 'change-me',
  algorithm: 'HS256',
  expiresIn: '1h'
});

// Generate token
const token = await jwt.generateToken({
  userId: 'user-123',
  email: 'user@example.com',
  roles: ['user', 'admin']
});

console.log(`Token: ${token.accessToken}`);

// Verify token
const user = await jwt.verifyToken(token.accessToken);
if (user) {
  console.log(`Authenticated: ${user.userId}`);
}
```

### API Key Authentication

```typescript
import { APIKeyProvider } from '@polln/gateway';

const provider = new APIKeyProvider({
  keys: {
    'key-123': { userId: 'user-123', scopes: ['read', 'write'] },
    'key-456': { userId: 'user-456', scopes: ['read'] }
  }
});

const user = await provider.verifyKey('key-123');
if (user) {
  console.log(`Authenticated: ${user.userId}`);
  console.log(`Scopes: ${user.scopes.join(', ')}`);
}
```

---

## Caching

### In-Memory Cache

```typescript
import { MemoryCacheProvider } from '@polln/gateway';

const cache = new MemoryCacheProvider({
  ttl: 300000,      // 5 minutes
  maxSize: 10000,   // max entries
  evictionPolicy: 'lru'  // least recently used
});

// Set cache entry
await cache.set('user-123', userData);

// Get from cache
const cached = await cache.get('user-123');
if (cached) {
  console.log('Cache hit');
} else {
  console.log('Cache miss');
}

// Delete entry
await cache.delete('user-123');

// Get statistics
const stats = cache.getStats();
console.log(`Hit rate: ${(stats.hitRate * 100).toFixed(1)}%`);
```

### Cache Key Builder

```typescript
import { CacheKeyBuilder } from '@polln/gateway';

const key = CacheKeyBuilder.forRequest('GET', '/api/users', { page: '1' });
console.log(key); // req:GET:/api/users:page=1
```

### Cache Decorator

```typescript
import { Cacheable } from '@polln/gateway';

class MyService {
  @Cacheable(cache, 'user-cache', { ttl: 60000 })
  async getUser(userId: string) {
    return await database.findUser(userId);
  }
}

// First call fetches from database
const user1 = await service.getUser('user-123');

// Second call returns from cache
const user2 = await service.getUser('user-123');
```

---

## Middleware

### Custom Middleware

```typescript
import type { Middleware } from '@polln/gateway';

const loggingMiddleware: Middleware = async (request) => {
  console.log(`${request.method} ${request.url}`);
  return request; // Return modified request or undefined
};

const authMiddleware: Middleware = async (request) => {
  const token = request.headers['authorization'];
  if (!token) {
    throw new Error('Unauthorized');
  }
  // Add user info to request
  return { ...request, user: { id: 'user-123' } };
};
```

### Route-Specific Middleware

```typescript
const route = RouteBuilder
  .create('/api/admin/*')
  .id('admin-route')
  .methods('GET', 'POST')
  .addMiddleware(authMiddleware)
  .addMiddleware(loggingMiddleware)
  .to('admin', 8080)
  .build();
```

---

## Monitoring

### Gateway Statistics

```typescript
const server = new GatewayServer(config);

// Get runtime statistics
const stats = await server.getStatistics();
console.log(`
  Total Requests: ${stats.totalRequests}
  Success Rate: ${(stats.successRate * 100).toFixed(1)}%
  Avg Latency: ${stats.avgLatency}ms
  P95 Latency: ${stats.p95Latency}ms
  P99 Latency: ${stats.p99Latency}ms
`);
```

### Circuit Breaker Stats

```typescript
const breaker = new CircuitBreaker(config);
const stats = breaker.getStatistics();
console.log(`
  State: ${stats.state}
  Success Count: ${stats.successCount}
  Failure Count: ${stats.failureCount}
  Failure Rate: ${(stats.failureRate * 100).toFixed(1)}%
  Last Failure: ${stats.lastFailureTime}
`);
```

---

## CLI Usage

```bash
# Start gateway server
polln-gateway start --config gateway.config.js

# Validate configuration
polln-gateway validate --config gateway.config.js

# Export routes
polln-gateway export-routes --format json

# Show statistics
polln-gateway stats

# Health check
polln-gateway health
```

---

## Configuration File

```javascript
// gateway.config.js
export default {
  port: 3000,
  host: '0.0.0.0',
  trustProxy: true,
  routes: [
    {
      id: 'api-users',
      path: '/api/users/*',
      methods: ['GET', 'POST', 'PUT', 'DELETE'],
      upstream: {
        host: 'api-server',
        port: 8080,
        protocol: 'http',
        path: '/'
      },
      stripPrefix: true,
      timeout: 30000,
      middleware: []
    }
  ],
  rateLimit: {
    enabled: true,
    windowMs: 60000,
    maxRequests: 100
  },
  circuitBreaker: {
    enabled: true,
    failureThreshold: 5,
    resetTimeoutMs: 60000
  },
  cache: {
    enabled: true,
    ttl: 300000,
    maxSize: 10000,
    evictionPolicy: 'lru'
  },
  auth: {
    jwt: {
      secret: process.env.JWT_SECRET,
      algorithm: 'HS256',
      expiresIn: '1h'
    },
    apiKey: {
      enabled: true,
      header: 'x-api-key',
      keys: {}
    }
  }
};
```

---

## Best Practices

1. **Use HTTPS in production**
2. **Enable rate limiting** to prevent abuse
3. **Configure circuit breakers** for external services
4. **Cache GET requests** with appropriate TTL
5. **Monitor metrics** and set up alerts
6. **Use environment variables** for secrets
7. **Implement graceful shutdown**

---

## License

MIT License - part of POLLN

---

**Repository:** https://github.com/SuperInstance/polln
**Package:** @polln/gateway
**Last Updated:** 2026-03-09
