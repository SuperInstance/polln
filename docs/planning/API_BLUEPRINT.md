# POLLN API Implementation Blueprint

**Target Agent**: glm-4.7 Implementation Agents
**Version**: 1.0.0
**Last Updated**: 2026-03-08

---

## Table of Contents

1. [Quick Start Guide](#1-quick-start-guide)
2. [Connection Implementation](#2-connection-implementation)
3. [Message Handling Patterns](#3-message-handling-patterns)
4. [Subscription Management](#4-subscription-management)
5. [Command Execution](#5-command-execution)
6. [Query Processing](#6-query-processing)
7. [Error Handling](#7-error-handling)
8. [Edge Cases](#8-edge-cases)
9. [Test Scenarios](#9-test-scenarios)
10. [Code Examples](#10-code-examples)

---

## 1. Quick Start Guide

### 1.1 Server Setup

```typescript
import { createPOLLNServer, POLLNServer } from './api/index.js';

const server = createPOLLNServer({
  port: 3000,
  host: '0.0.0.0',
  auth: {
    enableAuth: true,
    defaultToken: process.env.DEFAULT_API_TOKEN,
    tokenExpiresIn: 24 * 60 * 60 * 1000, // 24 hours
  },
  rateLimit: {
    requestsPerMinute: 100,
    burstLimit: 10,
  },
  heartbeat: {
    interval: 30000,
    timeout: 10000,
  },
});

await server.start();
console.log('POLLN API server started on port 3000');
```

### 1.2 Client Setup

```typescript
import { createPOLLNClient } from './api/client/index.js';

const client = createPOLLNClient({
  url: 'ws://localhost:3000/api/ws',
  token: process.env.API_TOKEN,
  reconnect: true,
  maxReconnectAttempts: 5,
  requestTimeout: 30000,
});

await client.connect();

// Subscribe to events
await client.subscribeToColony('colony_abc', ['agent_registered', 'stats_updated']);

// Query stats
const stats = await client.queryStats('colony_abc', { includeKVCache: true });
console.log(stats);
```

---

## 2. Connection Implementation

### 2.1 WebSocket Connection Flow

```typescript
// Server-side connection handling
class ConnectionHandler {
  private connections: Map<string, ConnectionInfo> = new Map();

  handleConnection(ws: WebSocket, req: IncomingMessage): void {
    const clientId = this.generateClientId();
    const connection: ConnectionInfo = {
      id: clientId,
      clientId,
      connectedAt: Date.now(),
      subscriptions: [],
      isAuthenticated: false,
      ip: req.socket.remoteAddress,
      isAlive: true,
    };

    this.connections.set(clientId, connection);

    // Set up handlers
    ws.on('message', (data) => this.handleMessage(clientId, ws, data));
    ws.on('close', () => this.handleClose(clientId));
    ws.on('error', (err) => this.handleError(clientId, err));
    ws.on('pong', () => this.handlePong(clientId));

    // Send welcome
    this.sendWelcome(ws, clientId);
  }

  private sendWelcome(ws: WebSocket, clientId: string): void {
    this.sendMessage(ws, {
      id: this.generateMessageId(),
      timestamp: Date.now(),
      type: 'welcome',
      payload: {
        message: 'Connected to POLLN WebSocket API',
        serverTime: Date.now(),
        clientId,
      },
      success: true,
    });
  }
}
```

### 2.2 Authentication Flow

```typescript
// Authentication handling
async function handleAuthentication(
  clientId: string,
  message: ClientMessage,
  auth: AuthenticationMiddleware
): Promise<AuthenticatedClient | null> {
  const { token } = message.payload as { token: string };

  // Try JWT validation first
  const jwtResult = auth.validateAccessToken(token);
  if (jwtResult) {
    return {
      id: clientId,
      gardenerId: jwtResult.gardenerId,
      permissions: jwtResult.permissions,
      token,
      connectedAt: Date.now(),
      lastActivity: Date.now(),
    };
  }

  // Fall back to legacy token
  const apiToken = auth.validateToken(token);
  if (apiToken) {
    return {
      id: clientId,
      gardenerId: apiToken.gardenerId,
      permissions: apiToken.permissions,
      token,
      connectedAt: Date.now(),
      lastActivity: Date.now(),
    };
  }

  return null;
}
```

### 2.3 Connection State Machine

```
                 +----------------+
                 |   CONNECTING   |
                 +-------+--------+
                         |
                         v
                 +-------+--------+
           +---->|    CONNECTED   |<----+
           |     +-------+--------+     |
           |             |              |
     Reconnect    +------+------+   Disconnect
           |      |    AUTH    |      |
           |      +------+-----+      |
           |             |            |
           |     +-------v--------+   |
           +-----|  AUTHENTICATED |---+
                 +-------+--------+
                         |
                         v
                 +-------+--------+
                 |     ACTIVE     |
                 +-------+--------+
                         |
                         v
                 +-------+--------+
                 | DISCONNECTING  |
                 +-------+--------+
                         |
                         v
                 +-------+--------+
                 |  DISCONNECTED  |
                 +----------------+
```

---

## 3. Message Handling Patterns

### 3.1 Message Router Pattern

```typescript
class MessageRouter {
  private handlers: Map<string, MessageHandler> = new Map();

  register(type: string, handler: MessageHandler): void {
    this.handlers.set(type, handler);
  }

  async route(message: ClientMessage, context: HandlerContext): Promise<ServerMessage | null> {
    const handler = this.handlers.get(message.type);

    if (!handler) {
      return this.createErrorResponse(
        message.id,
        APIErrorFactory.create('INVALID_PAYLOAD', `Unknown message type: ${message.type}`)
      );
    }

    try {
      return await handler(message, context);
    } catch (error) {
      return this.createErrorResponse(
        message.id,
        APIErrorFactory.internalError(error instanceof Error ? error.message : 'Unknown error')
      );
    }
  }
}
```

### 3.2 Request-Response Correlation

```typescript
// Client-side request tracking
class RequestTracker {
  private pending: Map<string, PendingRequest> = new Map();
  private timeout: number;

  constructor(timeout: number = 30000) {
    this.timeout = timeout;
  }

  track(messageId: string): Promise<ServerMessage> {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(messageId);
        reject(new Error(`Request ${messageId} timed out`));
      }, this.timeout);

      this.pending.set(messageId, { resolve, reject, timer });
    });
  }

  resolve(message: ServerMessage): boolean {
    const pending = this.pending.get(message.correlationId || message.id);
    if (!pending) return false;

    clearTimeout(pending.timer);
    this.pending.delete(message.correlationId || message.id);

    if (message.error) {
      pending.reject(new APIError(message.error));
    } else {
      pending.resolve(message);
    }
    return true;
  }
}
```

### 3.3 Middleware Chain

```typescript
type Middleware = (
  message: ClientMessage,
  context: HandlerContext,
  next: () => Promise<ServerMessage | null>
) => Promise<ServerMessage | null>;

class MiddlewareChain {
  private middlewares: Middleware[] = [];

  use(middleware: Middleware): this {
    this.middlewares.push(middleware);
    return this;
  }

  async execute(message: ClientMessage, context: HandlerContext): Promise<ServerMessage | null> {
    let index = 0;

    const next = async (): Promise<ServerMessage | null> => {
      if (index >= this.middlewares.length) {
        return null;
      }
      const middleware = this.middlewares[index++];
      return middleware(message, context, next);
    };

    return next();
  }
}

// Usage
const chain = new MiddlewareChain();
chain
  .use(rateLimitMiddleware)
  .use(authenticationMiddleware)
  .use(validationMiddleware)
  .use(loggingMiddleware);
```

---

## 4. Subscription Management

### 4.1 Subscription Store

```typescript
interface SubscriptionStore {
  // Map: clientId -> subscriptions
  private store: Map<string, Subscription[]>;

  add(clientId: string, subscription: Subscription): void;
  remove(clientId: string, type: string, id: string): void;
  getSubscribers(type: string, id: string): string[];
  getClientSubscriptions(clientId: string): Subscription[];
}

class InMemorySubscriptionStore implements SubscriptionStore {
  private store: Map<string, Subscription[]> = new Map();

  add(clientId: string, subscription: Subscription): void {
    const subs = this.store.get(clientId) || [];

    // Check for duplicate
    const exists = subs.some(s =>
      s.type === subscription.type && s.id === subscription.id
    );
    if (exists) return;

    subs.push(subscription);
    this.store.set(clientId, subs);
  }

  remove(clientId: string, type: string, id: string): void {
    const subs = this.store.get(clientId);
    if (!subs) return;

    const filtered = subs.filter(s => !(s.type === type && s.id === id));
    this.store.set(clientId, filtered);
  }

  getSubscribers(type: string, id: string): string[] {
    const subscribers: string[] = [];

    for (const [clientId, subs] of this.store) {
      if (subs.some(s => s.type === type && s.id === id)) {
        subscribers.push(clientId);
      }
    }

    return subscribers;
  }
}
```

### 4.2 Event Broadcasting

```typescript
class EventBroadcaster {
  constructor(
    private subscriptions: SubscriptionStore,
    private connections: Map<string, WebSocket>
  ) {}

  broadcastColonyEvent(colonyId: string, eventType: ColonyEventType, data: unknown): void {
    const subscribers = this.subscriptions.getSubscribers('colony', colonyId);
    const message: ServerMessage = {
      id: this.generateMessageId(),
      timestamp: Date.now(),
      type: 'event:colony',
      payload: { colonyId, eventType, data },
      success: true,
    };

    for (const clientId of subscribers) {
      const ws = this.connections.get(clientId);
      if (ws && ws.readyState === WebSocket.OPEN) {
        this.sendMessage(ws, message);
      }
    }
  }

  broadcastAgentEvent(
    agentId: string,
    colonyId: string,
    eventType: AgentEventType,
    data: unknown
  ): void {
    // Broadcast to agent subscribers
    const agentSubscribers = this.subscriptions.getSubscribers('agent', agentId);

    const message: ServerMessage = {
      id: this.generateMessageId(),
      timestamp: Date.now(),
      type: 'event:agent',
      payload: { agentId, colonyId, eventType, data },
      success: true,
    };

    for (const clientId of agentSubscribers) {
      const ws = this.connections.get(clientId);
      if (ws && ws.readyState === WebSocket.OPEN) {
        this.sendMessage(ws, message);
      }
    }
  }
}
```

### 4.3 Subscription Validation

```typescript
function validateSubscription(
  type: string,
  payload: unknown,
  client: AuthenticatedClient
): { valid: boolean; error?: APIError } {
  if (!payload || typeof payload !== 'object') {
    return { valid: false, error: APIErrorFactory.invalidPayload() };
  }

  const p = payload as Record<string, unknown>;

  switch (type) {
    case 'subscribe:colony': {
      if (typeof p.colonyId !== 'string' || !p.colonyId) {
        return { valid: false, error: APIErrorFactory.invalidPayload({ field: 'colonyId' }) };
      }
      if (!Array.isArray(p.events) || p.events.length === 0) {
        return { valid: false, error: APIErrorFactory.invalidPayload({ field: 'events' }) };
      }
      // Check permission
      if (!hasPermission(client, 'colony', 'read')) {
        return { valid: false, error: APIErrorFactory.forbidden() };
      }
      return { valid: true };
    }

    case 'subscribe:agent': {
      if (typeof p.agentId !== 'string' || !p.agentId) {
        return { valid: false, error: APIErrorFactory.invalidPayload({ field: 'agentId' }) };
      }
      if (!Array.isArray(p.events) || p.events.length === 0) {
        return { valid: false, error: APIErrorFactory.invalidPayload({ field: 'events' }) };
      }
      if (!hasPermission(client, 'agent', 'read')) {
        return { valid: false, error: APIErrorFactory.forbidden() };
      }
      return { valid: true };
    }

    default:
      return { valid: false, error: APIErrorFactory.invalidPayload({ unknownType: type }) };
  }
}
```

---

## 5. Command Execution

### 5.1 Command Handler Pattern

```typescript
interface CommandContext {
  client: AuthenticatedClient;
  colonies: Map<string, Colony>;
  broadcast: EventBroadcaster;
}

type CommandHandler<T, R> = (
  payload: T,
  context: CommandContext
) => Promise<CommandResult<R>>;

// Command registry
class CommandRegistry {
  private handlers: Map<string, CommandHandler<any, any>> = new Map();

  register<T, R>(type: string, handler: CommandHandler<T, R>): void {
    this.handlers.set(type, handler);
  }

  async execute<T, R>(
    type: string,
    payload: T,
    context: CommandContext
  ): Promise<CommandResult<R>> {
    const handler = this.handlers.get(type);
    if (!handler) {
      return { success: false, message: `Unknown command: ${type}` };
    }
    return handler(payload, context);
  }
}
```

### 5.2 Spawn Agent Command

```typescript
const spawnAgentHandler: CommandHandler<CommandSpawnPayload, { agentId: string }> = async (
  payload,
  context
) => {
  const { typeId, config } = payload;

  // Validate agent type
  const agentType = getAgentType(typeId);
  if (!agentType) {
    return {
      success: false,
      message: `Unknown agent type: ${typeId}`,
    };
  }

  // Check permissions
  if (!hasPermission(context.client, 'agent', 'write')) {
    return {
      success: false,
      message: 'Insufficient permissions to spawn agents',
    };
  }

  try {
    // Create agent
    const agentId = await createAgent(typeId, config);

    // Broadcast event
    context.broadcast.broadcastColonyEvent(
      config?.colonyId || 'default',
      'agent_registered',
      { agentId, typeId, config }
    );

    return {
      success: true,
      message: 'Agent spawned successfully',
      data: { agentId },
    };
  } catch (error) {
    return {
      success: false,
      message: `Failed to spawn agent: ${error instanceof Error ? error.message : 'Unknown error'}`,
    };
  }
};
```

### 5.3 Activate/Deactivate Commands

```typescript
const activateAgentHandler: CommandHandler<CommandActivatePayload, { agentId: string }> = async (
  payload,
  context
) => {
  const { agentId } = payload;

  // Find colony containing this agent
  let colony: Colony | undefined;
  let colonyId: string | undefined;

  for (const [cid, c] of context.colonies) {
    if (c.getAgent(agentId)) {
      colony = c;
      colonyId = cid;
      break;
    }
  }

  if (!colony) {
    return {
      success: false,
      message: `Agent not found: ${agentId}`,
    };
  }

  // Check permissions
  if (!hasPermission(context.client, 'agent', 'write')) {
    return {
      success: false,
      message: 'Insufficient permissions',
    };
  }

  const success = colony.activateAgent(agentId);

  if (success) {
    context.broadcast.broadcastColonyEvent(colonyId!, 'agent_activated', { agentId });
    context.broadcast.broadcastAgentEvent(agentId, colonyId!, 'state_updated', {
      status: 'active',
    });
  }

  return {
    success,
    message: success ? 'Agent activated' : 'Failed to activate agent',
    data: { agentId, colonyId },
  };
};
```

### 5.4 Dream Command

```typescript
const dreamHandler: CommandHandler<CommandDreamPayload, { dreamId: string }> = async (
  payload,
  context
) => {
  const { colonyId, agentId, episodeCount = 10 } = payload;

  // Validate
  if (!colonyId && !agentId) {
    return {
      success: false,
      message: 'Either colonyId or agentId must be specified',
    };
  }

  // Check permissions
  if (!hasPermission(context.client, 'dream', 'write')) {
    return {
      success: false,
      message: 'Insufficient permissions',
    };
  }

  try {
    // Start dream cycle (async)
    const dreamId = startDreamCycle({
      colonyId,
      agentId,
      episodeCount,
      onComplete: (result) => {
        context.broadcast.broadcastColonyEvent(
          colonyId || 'default',
          'dream_completed',
          { dreamId, result }
        );
      },
    });

    return {
      success: true,
      message: 'Dream cycle initiated',
      data: { dreamId, colonyId, agentId, episodeCount },
    };
  } catch (error) {
    return {
      success: false,
      message: `Failed to start dream cycle: ${error instanceof Error ? error.message : 'Unknown'}`,
    };
  }
};
```

---

## 6. Query Processing

### 6.1 Query Handler Pattern

```typescript
interface QueryContext {
  client: AuthenticatedClient;
  colonies: Map<string, Colony>;
}

type QueryHandler<T, R> = (
  payload: T,
  context: QueryContext
) => Promise<R>;

class QueryProcessor {
  private handlers: Map<string, QueryHandler<any, any>> = new Map();

  register<T, R>(type: string, handler: QueryHandler<T, R>): void {
    this.handlers.set(type, handler);
  }

  async process<T, R>(type: string, payload: T, context: QueryContext): Promise<R> {
    const handler = this.handlers.get(type);
    if (!handler) {
      throw new APIError(APIErrorFactory.notFound('Query type'));
    }
    return handler(payload, context);
  }
}
```

### 6.2 Stats Query

```typescript
const statsQueryHandler: QueryHandler<QueryStatsPayload, ResponseStatsPayload> = async (
  payload,
  context
) => {
  const { colonyId, includeKVCache, includeAgents } = payload;

  if (!colonyId) {
    throw new APIError(APIErrorFactory.invalidPayload({ missing: 'colonyId' }));
  }

  const colony = context.colonies.get(colonyId);
  if (!colony) {
    throw new APIError(APIErrorFactory.notFound('Colony'));
  }

  if (!hasPermission(context.client, 'stats', 'read')) {
    throw new APIError(APIErrorFactory.forbidden());
  }

  const stats = await colony.getStats();

  const response: ResponseStatsPayload = {
    colonyId,
    stats,
  };

  if (includeKVCache) {
    response.kvCacheStats = await colony.getKVCacheStats();
  }

  if (includeAgents) {
    response.agents = colony.getAllAgents();
  }

  return response;
};
```

### 6.3 Agents Query with Pagination

```typescript
const agentsQueryHandler: QueryHandler<QueryAgentsPayload, ResponseAgentsPayload> = async (
  payload,
  context
) => {
  const { colonyId, filter } = payload;

  const colony = context.colonies.get(colonyId);
  if (!colony) {
    throw new APIError(APIErrorFactory.notFound('Colony'));
  }

  if (!hasPermission(context.client, 'agent', 'read')) {
    throw new APIError(APIErrorFactory.forbidden());
  }

  let agents = colony.getAllAgents();
  const total = agents.length;

  // Apply filters
  if (filter?.status) {
    agents = agents.filter(a => a.status === filter.status);
  }
  if (filter?.typeId) {
    agents = agents.filter(a => a.typeId === filter.typeId);
  }
  if (filter?.minSuccessRate !== undefined) {
    agents = agents.filter(a => a.successRate >= filter.minSuccessRate!);
  }
  if (filter?.maxLatency !== undefined) {
    agents = agents.filter(a => a.avgLatencyMs <= filter.maxLatency!);
  }

  const filtered = agents.length;

  // Apply pagination
  if (filter?.limit) {
    const offset = filter.offset || 0;
    agents = agents.slice(offset, offset + filter.limit);
  }

  return {
    colonyId,
    agents,
    total,
    filtered,
    pagination: filter?.limit ? {
      limit: filter.limit,
      offset: filter.offset || 0,
      hasMore: (filter.offset || 0) + agents.length < filtered,
    } : undefined,
  };
};
```

---

## 7. Error Handling

### 7.1 Error Factory Usage

```typescript
import { APIErrorFactory } from './middleware.js';

// Common error patterns
const errors = {
  unauthorized: () => APIErrorFactory.unauthorized(),
  forbidden: () => APIErrorFactory.forbidden(),
  notFound: (resource: string) => APIErrorFactory.notFound(resource),
  invalidPayload: (details?: Record<string, unknown>) =>
    APIErrorFactory.invalidPayload(details),
  rateLimited: () => APIErrorFactory.rateLimited(),
  internal: (message?: string) => APIErrorFactory.internalError(message),
};

// Usage in handler
async function handleRequest(message: ClientMessage): Promise<ServerMessage> {
  try {
    // ... processing

    if (!authorized) {
      return createErrorResponse(message.id, errors.forbidden());
    }

    if (!resource) {
      return createErrorResponse(message.id, errors.notFound('Agent'));
    }

    // ... success response
  } catch (error) {
    return createErrorResponse(
      message.id,
      errors.internal(error instanceof Error ? error.message : 'Unknown error')
    );
  }
}
```

### 7.2 Error Response Builder

```typescript
function createErrorResponse(
  correlationId: string,
  error: APIError
): ServerMessage {
  return {
    id: `error_${Date.now()}_${randomBytes(4).toString('hex')}`,
    timestamp: Date.now(),
    type: 'error',
    payload: null,
    success: false,
    correlationId,
    error,
  };
}
```

### 7.3 Typed Error Handling

```typescript
class APIError extends Error {
  constructor(public readonly apiError: APIErrorInterface) {
    super(apiError.message);
    this.name = 'APIError';
  }

  get code(): ErrorCode {
    return this.apiError.code;
  }

  get details(): Record<string, unknown> | undefined {
    return this.apiError.details;
  }

  isClientError(): boolean {
    return [
      'UNAUTHORIZED', 'FORBIDDEN', 'NOT_FOUND',
      'INVALID_PAYLOAD', 'RATE_LIMITED',
      'COLONY_NOT_FOUND', 'AGENT_NOT_FOUND',
    ].includes(this.code);
  }

  isServerError(): boolean {
    return ['INTERNAL_ERROR', 'SERVICE_UNAVAILABLE', 'TIMEOUT'].includes(this.code);
  }
}

// Usage
try {
  await processMessage(message);
} catch (error) {
  if (error instanceof APIError) {
    if (error.isClientError()) {
      // Log at warn level
      logger.warn('Client error', { code: error.code, message: error.message });
    } else {
      // Log at error level
      logger.error('Server error', { error });
    }
  }
}
```

---

## 8. Edge Cases

### 8.1 Malformed Input

```typescript
// Handle various malformed inputs
function safeParseMessage(data: Buffer): ClientMessage | null {
  let parsed: unknown;

  // 1. Check if data is valid UTF-8
  let text: string;
  try {
    text = data.toString('utf-8');
  } catch {
    return null; // Invalid UTF-8
  }

  // 2. Parse JSON
  try {
    parsed = JSON.parse(text);
  } catch {
    return null; // Invalid JSON
  }

  // 3. Validate structure
  if (!parsed || typeof parsed !== 'object') {
    return null;
  }

  const msg = parsed as Record<string, unknown>;

  // 4. Check required fields
  if (typeof msg.id !== 'string') return null;
  if (typeof msg.timestamp !== 'number') return null;
  if (typeof msg.type !== 'string') return null;
  if (msg.payload === undefined) return null;

  return msg as ClientMessage;
}

// Usage
ws.on('message', (data: Buffer) => {
  const message = safeParseMessage(data);
  if (!message) {
    sendError(ws, APIErrorFactory.invalidPayload({ reason: 'Malformed message' }));
    return;
  }
  // ... process message
});
```

### 8.2 Timeout Handling

```typescript
// Request timeout handling
class TimeoutHandler {
  private pending: Map<string, NodeJS.Timeout> = new Map();
  private defaultTimeout: number;

  constructor(defaultTimeout: number = 30000) {
    this.defaultTimeout = defaultTimeout;
  }

  startTracking(messageId: string, timeout?: number): void {
    const ms = timeout || this.defaultTimeout;
    const timer = setTimeout(() => {
      this.pending.delete(messageId);
      this.emit('timeout', { messageId });
    }, ms);
    this.pending.set(messageId, timer);
  }

  stopTracking(messageId: string): void {
    const timer = this.pending.get(messageId);
    if (timer) {
      clearTimeout(timer);
      this.pending.delete(messageId);
    }
  }
}

// Server-side timeout handling
async function handleWithTimeout<T>(
  message: ClientMessage,
  handler: () => Promise<T>,
  timeoutMs: number = message.timeout || 30000
): Promise<T | ServerMessage> {
  let timeoutId: NodeJS.Timeout;

  const timeoutPromise = new Promise<never>((_, reject) => {
    timeoutId = setTimeout(() => {
      reject(new TimeoutError(`Request ${message.id} timed out`));
    }, timeoutMs);
  });

  try {
    const result = await Promise.race([handler(), timeoutPromise]);
    clearTimeout(timeoutId!);
    return result;
  } catch (error) {
    clearTimeout(timeoutId!);
    if (error instanceof TimeoutError) {
      return createErrorResponse(
        message.id,
        APIErrorFactory.create('TIMEOUT', 'Request timed out')
      );
    }
    throw error;
  }
}
```

### 8.3 Large Payload Handling

```typescript
// Validate payload size
const MAX_PAYLOAD_SIZE = 10 * 1024 * 1024; // 10MB

function validatePayloadSize(data: Buffer): boolean {
  return data.length <= MAX_PAYLOAD_SIZE;
}

// Stream large responses
async function streamLargeResponse(
  ws: WebSocket,
  messageId: string,
  data: unknown[],
  chunkSize: number = 100
): Promise<void> {
  const totalChunks = Math.ceil(data.length / chunkSize);

  for (let i = 0; i < totalChunks; i++) {
    const chunk = data.slice(i * chunkSize, (i + 1) * chunkSize);
    const isLast = i === totalChunks - 1;

    const message: ServerMessage = {
      id: `${messageId}_chunk_${i}`,
      correlationId: messageId,
      timestamp: Date.now(),
      type: 'response:agents', // Example
      payload: {
        chunk,
        chunkIndex: i,
        totalChunks,
        isLast,
      },
      success: true,
    };

    ws.send(JSON.stringify(message));

    // Allow backpressure handling
    if (ws.bufferedAmount > 1024 * 1024) {
      await waitForDrain(ws);
    }
  }
}

function waitForDrain(ws: WebSocket): Promise<void> {
  return new Promise(resolve => {
    ws.once('drain', resolve);
  });
}
```

### 8.4 Connection Interruption

```typescript
// Handle connection interruption during operation
class ResilientOperation {
  private connections: Map<string, WebSocket>;

  async executeWithRecovery<T>(
    clientId: string,
    operation: () => Promise<T>,
    onConnectionLost?: () => void
  ): Promise<T | null> {
    const ws = this.connections.get(clientId);

    if (!ws || ws.readyState !== WebSocket.OPEN) {
      onConnectionLost?.();
      return null;
    }

    try {
      return await operation();
    } catch (error) {
      // Check if connection was lost
      if (ws.readyState !== WebSocket.OPEN) {
        onConnectionLost?.();
        return null;
      }
      throw error;
    }
  }
}

// Reconnection handling (client-side)
class ReconnectionManager {
  private attempts = 0;
  private maxAttempts: number;
  private baseInterval: number;

  constructor(maxAttempts = 5, baseInterval = 1000) {
    this.maxAttempts = maxAttempts;
    this.baseInterval = baseInterval;
  }

  async reconnect(connect: () => Promise<void>): Promise<boolean> {
    while (this.attempts < this.maxAttempts) {
      const delay = this.baseInterval * Math.pow(2, this.attempts);
      await sleep(delay);

      try {
        await connect();
        this.attempts = 0;
        return true;
      } catch {
        this.attempts++;
      }
    }
    return false;
  }

  reset(): void {
    this.attempts = 0;
  }
}
```

### 8.5 Duplicate Message Handling

```typescript
// Idempotency handling
class IdempotencyCache {
  private cache: Map<string, { response: ServerMessage; timestamp: number }> = new Map();
  private ttl: number;

  constructor(ttlMs: number = 60000) {
    this.ttl = ttlMs;
  }

  get(messageId: string): ServerMessage | null {
    const entry = this.cache.get(messageId);
    if (!entry) return null;

    if (Date.now() - entry.timestamp > this.ttl) {
      this.cache.delete(messageId);
      return null;
    }

    return entry.response;
  }

  set(messageId: string, response: ServerMessage): void {
    this.cache.set(messageId, { response, timestamp: Date.now() });
  }

  cleanup(): void {
    const now = Date.now();
    for (const [id, entry] of this.cache) {
      if (now - entry.timestamp > this.ttl) {
        this.cache.delete(id);
      }
    }
  }
}

// Usage in message handler
async function handleMessage(
  message: ClientMessage,
  idempotency: IdempotencyCache
): Promise<ServerMessage> {
  // Check for duplicate
  const cached = idempotency.get(message.id);
  if (cached) {
    return { ...cached, correlationId: message.id };
  }

  // Process message
  const response = await processMessage(message);

  // Cache response for idempotent operations
  if (message.type.startsWith('command:')) {
    idempotency.set(message.id, response);
  }

  return response;
}
```

---

## 9. Test Scenarios

### 9.1 Connection Tests

```typescript
describe('WebSocket Connection', () => {
  it('should establish connection and receive welcome', async () => {
    const client = createPOLLNClient({ url: WS_URL });
    const welcomePromise = once(client, 'welcome');

    await client.connect();
    const welcome = await welcomePromise;

    expect(welcome).toBeDefined();
    expect(welcome.serverTime).toBeLessThanOrEqual(Date.now());
  });

  it('should authenticate with valid token', async () => {
    const client = createPOLLNClient({
      url: WS_URL,
      token: validToken,
    });

    await client.connect();
    expect(client.isAuthenticated()).toBe(true);
  });

  it('should reject invalid token', async () => {
    const client = createPOLLNClient({
      url: WS_URL,
      token: 'invalid-token',
    });

    await expect(client.connect()).rejects.toThrow('Authentication failed');
  });

  it('should handle reconnection', async () => {
    const client = createPOLLNClient({
      url: WS_URL,
      reconnect: true,
      maxReconnectAttempts: 3,
    });

    await client.connect();
    const ws = (client as any).ws;

    // Simulate disconnect
    ws.close();

    await once(client, 'reconnected');
    expect(client.isConnected()).toBe(true);
  });
});
```

### 9.2 Subscription Tests

```typescript
describe('Subscriptions', () => {
  it('should subscribe to colony events', async () => {
    const client = await connectedClient();

    await client.subscribeToColony('colony_abc', ['agent_registered']);

    // Trigger event
    await spawnAgent('task-agent');

    const event = await once(client, 'colony:event');
    expect(event.eventType).toBe('agent_registered');
  });

  it('should unsubscribe correctly', async () => {
    const client = await connectedClient();

    await client.subscribeToColony('colony_abc', ['agent_registered']);
    await client.unsubscribeFromColony('colony_abc');

    // Trigger event
    await spawnAgent('task-agent');

    // Should not receive event
    await expect(
      Promise.race([
        once(client, 'colony:event'),
        sleep(1000).then(() => 'timeout'),
      ])
    ).resolves.toBe('timeout');
  });

  it('should filter events by type', async () => {
    const client = await connectedClient();

    await client.subscribeToColony('colony_abc', ['stats_updated']);

    // Trigger different event
    await spawnAgent('task-agent');

    // Should not receive agent_registered
    await expect(
      Promise.race([
        once(client, 'colony:event'),
        sleep(500).then(() => 'timeout'),
      ])
    ).resolves.toBe('timeout');
  });
});
```

### 9.3 Command Tests

```typescript
describe('Commands', () => {
  it('should spawn agent', async () => {
    const client = await connectedClient();

    const result = await client.spawnAgent('task-agent', {
      modelFamily: 'gpt-4',
    });

    expect(result.success).toBe(true);
    expect(result.data.agentId).toBeDefined();
  });

  it('should activate agent', async () => {
    const client = await connectedClient();
    const { agentId } = await spawnTestAgent();

    const result = await client.activateAgent(agentId);

    expect(result.success).toBe(true);
  });

  it('should fail for non-existent agent', async () => {
    const client = await connectedClient();

    await expect(
      client.activateAgent('non-existent-agent')
    ).rejects.toThrow('Agent not found');
  });

  it('should trigger dream cycle', async () => {
    const client = await connectedClient();

    const result = await client.triggerDream('colony_abc', {
      episodeCount: 5,
    });

    expect(result.success).toBe(true);
    expect(result.data.dreamId).toBeDefined();
  });
});
```

### 9.4 Query Tests

```typescript
describe('Queries', () => {
  it('should query colony stats', async () => {
    const client = await connectedClient();

    const stats = await client.queryStats('colony_abc', {
      includeKVCache: true,
      includeAgents: true,
    });

    expect(stats.colonyId).toBe('colony_abc');
    expect(stats.stats).toBeDefined();
    expect(stats.kvCacheStats).toBeDefined();
    expect(stats.agents).toBeInstanceOf(Array);
  });

  it('should query agents with pagination', async () => {
    const client = await connectedClient();

    const result = await client.queryAgents('colony_abc', {
      status: 'active',
      limit: 10,
      offset: 0,
    });

    expect(result.agents.length).toBeLessThanOrEqual(10);
    expect(result.total).toBeGreaterThanOrEqual(result.filtered);
  });

  it('should query specific agent', async () => {
    const client = await connectedClient();
    const { agentId } = await spawnTestAgent();

    const result = await client.queryAgent(agentId, {
      includeHistory: true,
    });

    expect(result.agent.id).toBe(agentId);
    expect(result.history).toBeInstanceOf(Array);
  });
});
```

### 9.5 Error Handling Tests

```typescript
describe('Error Handling', () => {
  it('should return error for invalid payload', async () => {
    const client = await connectedClient();

    const ws = (client as any).ws;
    ws.send(JSON.stringify({
      id: 'test_001',
      timestamp: Date.now(),
      type: 'subscribe:colony',
      payload: {}, // Missing required fields
    }));

    const error = await once(client, 'error');
    expect(error.code).toBe('INVALID_PAYLOAD');
  });

  it('should handle rate limiting', async () => {
    const client = await connectedClient();

    // Send many requests rapidly
    const promises = Array(150).fill(null).map(() =>
      client.ping().catch(e => e)
    );

    const results = await Promise.all(promises);
    const rateLimited = results.filter(r => r instanceof Error);

    expect(rateLimited.length).toBeGreaterThan(0);
  });

  it('should handle timeout', async () => {
    const client = await connectedClient({
      requestTimeout: 100,
    });

    // Server takes longer than timeout
    await expect(
      client.triggerDream('colony_abc', { episodeCount: 1000 })
    ).rejects.toThrow('timeout');
  });
});
```

### 9.6 Edge Case Tests

```typescript
describe('Edge Cases', () => {
  it('should handle malformed JSON', async () => {
    const client = await connectedClient();
    const ws = (client as any).ws;

    ws.send('not valid json');

    const error = await once(client, 'error');
    expect(error.code).toBe('INVALID_PAYLOAD');
  });

  it('should handle extremely large payload', async () => {
    const client = await connectedClient();

    const largeConfig = {
      data: 'x'.repeat(20 * 1024 * 1024), // 20MB
    };

    await expect(
      client.spawnAgent('task-agent', largeConfig)
    ).rejects.toThrow();
  });

  it('should handle concurrent subscriptions', async () => {
    const client = await connectedClient();

    const subscriptions = Array(10).fill(null).map((_, i) =>
      client.subscribeToColony(`colony_${i}`, ['agent_registered'])
    );

    const results = await Promise.allSettled(subscriptions);
    const successful = results.filter(r => r.status === 'fulfilled');

    expect(successful.length).toBe(10);
  });

  it('should handle duplicate message IDs', async () => {
    const client = await connectedClient();

    // Send same message ID twice
    const result1 = await client.ping();
    const result2 = await client.ping();

    // Both should succeed (idempotency)
    expect(result1).toBeDefined();
    expect(result2).toBeDefined();
  });

  it('should handle stale timestamps', async () => {
    const client = await connectedClient();
    const ws = (client as any).ws;

    // Send message with old timestamp
    ws.send(JSON.stringify({
      id: 'stale_001',
      timestamp: Date.now() - 10 * 60 * 1000, // 10 minutes ago
      type: 'ping',
      payload: null,
    }));

    const error = await once(client, 'error');
    expect(error.code).toBe('INVALID_PAYLOAD');
  });
});
```

---

## 10. Code Examples

### 10.1 Complete Server Implementation

```typescript
// server.ts
import { createServer } from 'http';
import { WebSocketServer, WebSocket } from 'ws';
import { v4 as uuidv4 } from 'uuid';

interface ServerConfig {
  port: number;
  host?: string;
}

export class POLLNServer {
  private httpServer: any;
  private wsServer: WebSocketServer | null = null;
  private connections: Map<string, WebSocket> = new Map();
  private subscriptions: Map<string, Set<string>> = new Map();

  constructor(private config: ServerConfig) {}

  async start(): Promise<void> {
    this.httpServer = createServer();
    this.wsServer = new WebSocketServer({ server: this.httpServer });

    this.wsServer.on('connection', (ws, req) => {
      const clientId = uuidv4();
      this.connections.set(clientId, ws);
      this.subscriptions.set(clientId, new Set());

      ws.on('message', (data) => this.handleMessage(clientId, ws, data));
      ws.on('close', () => this.handleClose(clientId));
      ws.on('error', (err) => this.handleError(clientId, err));

      this.send(ws, {
        id: uuidv4(),
        timestamp: Date.now(),
        type: 'welcome',
        payload: { clientId, serverTime: Date.now() },
        success: true,
      });
    });

    return new Promise((resolve) => {
      this.httpServer.listen(this.config.port, this.config.host, resolve);
    });
  }

  private handleMessage(clientId: string, ws: WebSocket, data: Buffer): void {
    try {
      const message = JSON.parse(data.toString());
      // ... handle message
    } catch (error) {
      this.sendError(ws, 'INVALID_PAYLOAD', 'Failed to parse message');
    }
  }

  private handleClose(clientId: string): void {
    this.connections.delete(clientId);
    this.subscriptions.delete(clientId);
  }

  private handleError(clientId: string, error: Error): void {
    console.error(`Client ${clientId} error:`, error);
  }

  private send(ws: WebSocket, message: any): void {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    }
  }

  private sendError(ws: WebSocket, code: string, message: string): void {
    this.send(ws, {
      id: uuidv4(),
      timestamp: Date.now(),
      type: 'error',
      payload: null,
      success: false,
      error: { code, message },
    });
  }

  async stop(): Promise<void> {
    return new Promise((resolve) => {
      this.wsServer?.close(() => {
        this.httpServer?.close(resolve);
      });
    });
  }
}
```

### 10.2 Complete Client Implementation

```typescript
// client.ts
import WebSocket from 'ws';
import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';

export class POLLNClient extends EventEmitter {
  private ws: WebSocket | null = null;
  private connected = false;
  private pendingRequests: Map<string, {
    resolve: Function;
    reject: Function;
    timeout: NodeJS.Timeout;
  }> = new Map();

  constructor(private config: { url: string; timeout?: number }) {
    super();
  }

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.config.url);

      this.ws.on('open', () => {
        this.connected = true;
        this.emit('connected');
        resolve();
      });

      this.ws.on('message', (data) => this.handleMessage(data));
      this.ws.on('error', (err) => this.emit('error', err));
      this.ws.on('close', () => {
        this.connected = false;
        this.emit('disconnected');
        this.rejectAllPending('Connection closed');
      });
    });
  }

  async request(type: string, payload: any): Promise<any> {
    return new Promise((resolve, reject) => {
      if (!this.connected || !this.ws) {
        reject(new Error('Not connected'));
        return;
      }

      const id = uuidv4();
      const message = { id, timestamp: Date.now(), type, payload };

      const timeout = setTimeout(() => {
        this.pendingRequests.delete(id);
        reject(new Error('Request timeout'));
      }, this.config.timeout || 30000);

      this.pendingRequests.set(id, { resolve, reject, timeout });
      this.ws.send(JSON.stringify(message));
    });
  }

  private handleMessage(data: Buffer): void {
    try {
      const message = JSON.parse(data.toString());

      const pending = this.pendingRequests.get(message.correlationId || message.id);
      if (pending) {
        clearTimeout(pending.timeout);
        this.pendingRequests.delete(message.correlationId || message.id);

        if (message.error) {
          pending.reject(new Error(message.error.message));
        } else {
          pending.resolve(message.payload);
        }
        return;
      }

      // Emit events for unsolicited messages
      if (message.type.startsWith('event:')) {
        this.emit(message.type, message.payload);
      }
    } catch (error) {
      this.emit('error', error);
    }
  }

  private rejectAllPending(reason: string): void {
    for (const [id, pending] of this.pendingRequests) {
      clearTimeout(pending.timeout);
      pending.reject(new Error(reason));
    }
    this.pendingRequests.clear();
  }

  async disconnect(): Promise<void> {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.connected = false;
  }

  isConnected(): boolean {
    return this.connected;
  }
}
```

### 10.3 Integration Example

```typescript
// example.ts
import { POLLNServer } from './server.js';
import { POLLNClient } from './client.js';
import { Colony } from '../core/colony.js';

async function main() {
  // Start server
  const server = new POLLNServer({ port: 3000 });
  await server.start();
  console.log('Server started on port 3000');

  // Create and register colony
  const colony = new Colony({ id: 'colony_abc' });
  server.registerColony(colony);

  // Connect client
  const client = new POLLNClient({ url: 'ws://localhost:3000/api/ws' });
  await client.connect();
  console.log('Client connected');

  // Subscribe to events
  client.on('event:colony', (payload) => {
    console.log('Colony event:', payload);
  });

  await client.request('subscribe:colony', {
    colonyId: 'colony_abc',
    events: ['agent_registered', 'stats_updated'],
  });

  // Spawn agent
  const spawnResult = await client.request('command:spawn', {
    typeId: 'task-agent',
    config: { modelFamily: 'gpt-4' },
  });
  console.log('Spawned agent:', spawnResult);

  // Query stats
  const stats = await client.request('query:stats', {
    colonyId: 'colony_abc',
    includeKVCache: true,
  });
  console.log('Stats:', stats);

  // Cleanup
  await client.disconnect();
  await server.stop();
}

main().catch(console.error);
```

---

## Appendix: Checklist for Implementation Agents

### Before Implementation
- [ ] Review `src/api/types.ts` for all type definitions
- [ ] Review `src/api/middleware.ts` for authentication patterns
- [ ] Review `src/api/handlers.ts` for message handling patterns
- [ ] Check `src/api/openapi.yaml` for complete API specification

### During Implementation
- [ ] Use TypeScript strict mode
- [ ] Validate all incoming messages with JSON schema
- [ ] Implement proper error handling with APIErrorFactory
- [ ] Add request correlation IDs for tracing
- [ ] Handle connection state transitions correctly
- [ ] Implement idempotency for commands

### After Implementation
- [ ] Run all test scenarios from Section 9
- [ ] Test edge cases from Section 8
- [ ] Verify rate limiting works correctly
- [ ] Test reconnection behavior
- [ ] Validate error response format

---

*Blueprint generated for glm-4.7 implementation agents*
*Version: 1.0.0*
