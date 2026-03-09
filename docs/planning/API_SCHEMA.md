# POLLN API Schema Specification

**Version**: 1.0.0
**Protocol**: WebSocket (Primary) / HTTP (Health Checks)
**Last Updated**: 2026-03-08

---

## Table of Contents

1. [Protocol Overview](#1-protocol-overview)
2. [Versioning Strategy](#2-versioning-strategy)
3. [Base Message Schema](#3-base-message-schema)
4. [Client Message Types](#4-client-message-types)
5. [Server Message Types](#5-server-message-types)
6. [Payload Schemas](#6-payload-schemas)
7. [Error Schemas](#7-error-schemas)
8. [A2A Package Protocol Extensions](#8-a2a-package-protocol-extensions)
9. [Authentication Schemas](#9-authentication-schemas)
10. [Rate Limiting Schemas](#10-rate-limiting-schemas)

---

## 1. Protocol Overview

### 1.1 Transport Layer

| Transport | Endpoint | Purpose |
|-----------|----------|---------|
| WebSocket | `/api/ws` | Real-time bidirectional communication |
| HTTP | `/health` | Liveness probe (Kubernetes) |
| HTTP | `/ready` | Readiness probe (Kubernetes) |
| HTTP | `/metrics` | Prometheus metrics |

### 1.2 Message Flow

```
Client                                      Server
  |                                            |
  |------------ WebSocket Connect ------------>|
  |<----------- Connection Ack ----------------|
  |                                            |
  |-------- Auth Message (if enabled) -------->|
  |<----------- Auth Response -----------------|
  |                                            |
  |-------- Subscribe Message ---------------->|
  |<----------- Subscribe Ack -----------------|
  |                                            |
  |-------- Query/Command Message ------------>|
  |<----------- Response ----------------------|
  |                                            |
  |                  [Event occurs]            |
  |<----------- Event Broadcast ---------------|
  |                                            |
  |-------- Ping ----------------------------->|
  |<----------- Pong --------------------------|
```

### 1.3 Connection Lifecycle States

```typescript
type ConnectionState =
  | 'connecting'      // WebSocket opening
  | 'connected'       // WebSocket open, not authenticated
  | 'authenticated'   // Authentication successful
  | 'active'          // Subscriptions active
  | 'disconnecting'   // Graceful shutdown
  | 'disconnected'    // Connection closed
  | 'reconnecting';   // Attempting reconnection
```

---

## 2. Versioning Strategy

### 2.1 Protocol Version Header

All messages include an implicit protocol version determined at connection time.

```typescript
interface ProtocolVersion {
  major: number;      // Breaking changes
  minor: number;      // New features, backward compatible
  patch: number;      // Bug fixes
}

// Current version: 1.0.0
const CURRENT_PROTOCOL: ProtocolVersion = { major: 1, minor: 0, patch: 0 };
```

### 2.2 Version Negotiation

```typescript
interface VersionNegotiation {
  clientVersion: ProtocolVersion;
  supportedVersions: ProtocolVersion[];
}

// Server responds with highest compatible version
interface VersionResponse {
  agreedVersion: ProtocolVersion;
  deprecatedFeatures?: string[];
  minimumVersion: ProtocolVersion;
}
```

### 2.3 Backward Compatibility Rules

| Change Type | Major | Minor | Patch |
|-------------|-------|-------|-------|
| Remove message type | X | | |
| Remove required field | X | | |
| Add required field | X | | |
| Add optional field | | X | |
| Add message type | | X | |
| Change field semantics | X | | |
| Bug fix | | | X |

### 2.4 Deprecation Policy

```typescript
interface DeprecationNotice {
  feature: string;           // Message type or field
  deprecatedIn: ProtocolVersion;
  removedIn: ProtocolVersion;
  migrationGuide: string;    // URL to documentation
}

// Included in server welcome message
interface WelcomeMessage {
  protocolVersion: ProtocolVersion;
  deprecations: DeprecationNotice[];
  serverTime: number;
}
```

---

## 3. Base Message Schema

### 3.1 ClientMessage

```typescript
interface ClientMessage<T = unknown> {
  // Required fields
  id: string;                  // Unique message identifier
                               // Format: /^[a-zA-Z0-9_-]{1,100}$/
  timestamp: number;           // Unix timestamp in milliseconds
                               // Must be within 5 minutes of server time
  type: ClientMessageType;     // Message type enum
  payload: T;                  // Type-specific payload

  // Optional fields
  correlationId?: string;      // For request correlation
  timeout?: number;            // Request timeout in ms (default: 30000)
}
```

**Validation Rules**:
- `id`: 1-100 alphanumeric characters, hyphens, underscores
- `timestamp`: Positive integer, not in future (1 min tolerance)
- `type`: Must be valid ClientMessageType
- `payload`: Max size 10MB (configurable)

### 3.2 ServerMessage

```typescript
interface ServerMessage<T = unknown> {
  // Required fields
  id: string;                  // Unique message identifier
  timestamp: number;           // Unix timestamp in milliseconds
  type: ServerMessageType;     // Message type enum
  payload: T | null;           // Type-specific payload or null for errors

  // Status fields
  success: boolean;            // Operation success status

  // Error fields (only when success is false)
  error?: APIError;

  // Correlation (for request/response)
  correlationId?: string;      // Matches client message id
}
```

### 3.3 Message ID Generation

```typescript
// Recommended format
function generateMessageId(): string {
  return `msg_${Date.now()}_${randomBytes(4).toString('hex')}`;
}

// Examples
// msg_1709123456789_a1b2c3d4
// msg_1709123456790_e5f6a7b8
```

---

## 4. Client Message Types

### 4.1 Type Enumeration

```typescript
type ClientMessageType =
  // Subscriptions
  | 'subscribe:colony'
  | 'unsubscribe:colony'
  | 'subscribe:agent'
  | 'unsubscribe:agent'
  | 'subscribe:dreams'
  | 'unsubscribe:dreams'
  | 'subscribe:stats'
  | 'unsubscribe:stats'
  | 'subscribe:kv-cache'        // NEW: KV-Cache monitoring
  | 'unsubscribe:kv-cache'      // NEW: KV-Cache monitoring

  // Commands
  | 'command:spawn'
  | 'command:despawn'
  | 'command:activate'
  | 'command:deactivate'
  | 'command:dream'
  | 'command:sync-federation'   // NEW: Federation sync
  | 'command:clear-cache'       // NEW: Cache management

  // Queries
  | 'query:stats'
  | 'query:agents'
  | 'query:agent'
  | 'query:config'
  | 'query:kv-anchors'          // NEW: KV anchor query
  | 'query:meadow'              // NEW: Meadow marketplace
  | 'query:federation'          // NEW: Federation status

  // System
  | 'ping'
  | 'auth';                     // Authentication
```

### 4.2 Message Type Categories

| Category | Prefix | Purpose |
|----------|--------|---------|
| Subscription | `subscribe:` / `unsubscribe:` | Real-time event streams |
| Command | `command:` | State-changing operations |
| Query | `query:` | Read-only data retrieval |
| System | (none) | Connection management |

---

## 5. Server Message Types

### 5.1 Type Enumeration

```typescript
type ServerMessageType =
  // Events (push notifications)
  | 'event:colony'
  | 'event:agent'
  | 'event:dream'
  | 'event:stats'
  | 'event:kv-cache'            // NEW: KV-Cache events
  | 'event:federation'          // NEW: Federation events
  | 'event:meadow'              // NEW: Meadow events

  // Responses
  | 'response:stats'
  | 'response:agents'
  | 'response:agent'
  | 'response:config'
  | 'response:command'
  | 'response:kv-anchors'       // NEW
  | 'response:meadow'           // NEW
  | 'response:federation'       // NEW

  // System
  | 'pong'
  | 'error'
  | 'welcome';                  // Connection acknowledgment
```

### 5.2 Response Correlation

Responses to client requests include the original message ID:

```typescript
// Client sends
{
  "id": "msg_001",
  "type": "query:stats",
  "payload": { "colonyId": "colony_abc" }
}

// Server responds
{
  "id": "msg_002",
  "correlationId": "msg_001",  // References client message
  "type": "response:stats",
  "payload": { ... },
  "success": true
}
```

---

## 6. Payload Schemas

### 6.1 Subscription Payloads

#### SubscribeColonyPayload

```typescript
interface SubscribeColonyPayload {
  colonyId: string;             // Required: Colony identifier
  events: ColonyEventType[];    // Required: Event filter
}

type ColonyEventType =
  | 'agent_registered'
  | 'agent_unregistered'
  | 'agent_activated'
  | 'agent_deactivated'
  | 'stats_updated'
  | 'dream_completed'
  | 'kv_cache_updated'          // NEW
  | 'federation_sync'           // NEW
  | 'error';
```

**Example**:
```json
{
  "id": "msg_001",
  "timestamp": 1709123456789,
  "type": "subscribe:colony",
  "payload": {
    "colonyId": "colony_abc123",
    "events": ["agent_registered", "stats_updated", "dream_completed"]
  }
}
```

#### SubscribeAgentPayload

```typescript
interface SubscribeAgentPayload {
  agentId: string;              // Required: Agent identifier
  events: AgentEventType[];     // Required: Event filter
}

type AgentEventType =
  | 'state_updated'
  | 'executed'
  | 'succeeded'
  | 'failed'
  | 'value_changed'
  | 'anchor_matched'            // NEW: KV anchor matched
  | 'learning_updated'          // NEW: Hebbian learning update
  | 'error';
```

#### SubscribeKVCachePayload (NEW)

```typescript
interface SubscribeKVCachePayload {
  colonyId: string;
  events: KVCacheEventType[];
}

type KVCacheEventType =
  | 'anchor_created'
  | 'anchor_matched'
  | 'anchor_evicted'
  | 'cache_hit'
  | 'cache_miss'
  | 'compression_update';
```

### 6.2 Command Payloads

#### CommandSpawnPayload

```typescript
interface CommandSpawnPayload {
  typeId: string;               // Required: Agent type identifier
  config?: AgentSpawnConfig;    // Optional: Spawn configuration
}

interface AgentSpawnConfig {
  // Core configuration
  modelFamily?: string;         // LLM model family
  defaultParams?: Record<string, unknown>;

  // SPORE Protocol
  inputTopics?: string[];
  outputTopic?: string;

  // Performance
  targetLatencyMs?: number;
  maxMemoryMB?: number;

  // KV-Cache (NEW)
  enableKVCache?: boolean;
  anchorPoolSize?: number;

  // Custom configuration
  [key: string]: unknown;
}
```

#### CommandDreamPayload

```typescript
interface CommandDreamPayload {
  colonyId?: string;            // Colony to dream
  agentId?: string;             // Specific agent (optional)
  episodeCount?: number;        // Number of episodes (default: 10)
  options?: DreamOptions;
}

interface DreamOptions {
  includeKVAnchors?: boolean;   // Include KV-cache dreaming
  learningRate?: number;        // Override learning rate
  temperature?: number;         // Dream exploration temperature
}
```

#### CommandSyncFederationPayload (NEW)

```typescript
interface CommandSyncFederationPayload {
  colonyId: string;
  syncType: 'anchors' | 'models' | 'pollen' | 'all';
  options?: {
    privacyBudget?: number;     // Differential privacy epsilon
    minParticipants?: number;   // Minimum participants for round
    timeout?: number;           // Sync timeout in ms
  };
}
```

### 6.3 Query Payloads

#### QueryStatsPayload

```typescript
interface QueryStatsPayload {
  colonyId?: string;            // Optional: specific colony
  includeKVCache?: boolean;     // Include KV-cache statistics
  includeAgents?: boolean;      // Include agent list
  includeFederation?: boolean;  // Include federation status (NEW)
}
```

#### QueryAgentsPayload

```typescript
interface QueryAgentsPayload {
  colonyId: string;             // Required
  filter?: AgentFilter;
}

interface AgentFilter {
  status?: 'active' | 'dormant' | 'hibernating' | 'error';
  typeId?: string;
  minSuccessRate?: number;      // 0.0 - 1.0
  maxLatency?: number;          // Max latency in ms
  tags?: string[];              // Agent tags (NEW)
  limit?: number;               // Pagination limit
  offset?: number;              // Pagination offset
}
```

#### QueryKVAnchorsPayload (NEW)

```typescript
interface QueryKVAnchorsPayload {
  colonyId: string;
  filter?: AnchorFilter;
}

interface AnchorFilter {
  minUsageCount?: number;
  maxAge?: number;              // Max age in ms
  minHitRate?: number;
  sourceAgentId?: string;
  limit?: number;
  offset?: number;
}
```

### 6.4 Event Payloads

#### ColonyEventPayload

```typescript
interface ColonyEventPayload {
  colonyId: string;
  eventType: ColonyEventType;
  data: ColonyEventData;
  timestamp: number;
}

type ColonyEventData =
  | AgentRegisteredData
  | StatsUpdatedData
  | DreamCompletedData
  | KVCacheUpdatedData          // NEW
  | FederationSyncData          // NEW
  | ErrorData;

interface AgentRegisteredData {
  agentId: string;
  typeId: string;
  config: Partial<AgentSpawnConfig>;
}

interface DreamCompletedData {
  dreamId: string;
  episodeCount: number;
  metrics: {
    totalLoss: number;
    avgReconstructionError: number;
    avgKLDivergence: number;
    policyImprovement: number;
  };
  anchorOptimizations?: number; // NEW: KV anchors optimized
}
```

#### AgentEventPayload

```typescript
interface AgentEventPayload {
  agentId: string;
  colonyId: string;
  eventType: AgentEventType;
  data: AgentEventData;
  timestamp: number;
}

interface AgentExecutedData {
  taskId: string;
  input: unknown;
  output: unknown;
  latencyMs: number;
  confidence: number;
  kvCacheHit?: boolean;         // NEW
  anchorUsed?: string;          // NEW: Anchor ID if matched
}

interface LearningUpdatedData {
  synapseUpdates: Array<{
    sourceId: string;
    targetId: string;
    oldWeight: number;
    newWeight: number;
    reward: number;
  }>;
  valueFunctionChange: number;
}
```

### 6.5 Response Payloads

#### ResponseStatsPayload

```typescript
interface ResponseStatsPayload {
  colonyId: string;
  stats: ColonyStats;
  kvCacheStats?: KVCacheStats;
  federationStats?: FederationStats;
  agents?: AgentState[];
}

interface ColonyStats {
  // Agent counts
  totalAgents: number;
  activeAgents: number;
  dormantAgents: number;
  hibernatingAgents: number;

  // Resources
  totalCompute: number;
  totalMemory: number;
  totalNetwork: number;
  usedCompute: number;
  usedMemory: number;

  // Diversity
  shannonDiversity: number;
  typeDistribution: Record<string, number>;

  // Performance
  avgLatencyMs: number;
  successRate: number;
  throughputPerMinute: number;

  // Learning
  totalSynapticUpdates: number;
  avgValueFunction: number;

  // Timestamps
  createdAt: number;
  lastActivity: number;
}

interface KVCacheStats {
  // Segment stats
  totalSegments: number;
  totalSizeBytes: number;

  // Hit rates
  hitRate: number;
  missRate: number;
  evictions: number;

  // Anchors
  anchors: {
    total: number;
    active: number;
    matched: number;
    avgMatchConfidence: number;
  };

  // Compression
  compression: {
    originalSize: number;
    compressedSize: number;
    ratio: number;
  };

  // Performance
  avgLookupTimeMs: number;
  avgCompressTimeMs: number;
}

interface FederationStats {
  connectedColonies: number;
  activeRounds: number;
  completedRounds: number;
  totalSharedAnchors: number;
  avgRoundLatency: number;
  privacyBudgetRemaining: number;
}
```

#### ResponseAgentsPayload

```typescript
interface ResponseAgentsPayload {
  colonyId: string;
  agents: AgentState[];
  total: number;
  filtered: number;
  pagination?: {
    limit: number;
    offset: number;
    hasMore: boolean;
  };
}

interface AgentState {
  id: string;
  typeId: string;
  categoryId: 'task' | 'role' | 'core';

  // Status
  status: 'active' | 'dormant' | 'hibernating' | 'error';
  lastActive: number;

  // Model
  modelVersion: number;
  modelHash?: string;

  // Performance
  valueFunction: number;
  successCount: number;
  failureCount: number;
  successRate: number;
  avgLatencyMs: number;
  executionCount: number;

  // KV-Cache (NEW)
  kvCacheStats?: {
    anchorsCreated: number;
    anchorsMatched: number;
    cacheHitRate: number;
  };

  // State snapshot (optional)
  stateSnapshot?: Record<string, unknown>;
}
```

---

## 7. Error Schemas

### 7.1 APIError Structure

```typescript
interface APIError {
  code: ErrorCode;              // Machine-readable error code
  message: string;              // Human-readable message
  details?: Record<string, unknown>;  // Additional context
  stack?: string;               // Stack trace (dev mode only)
  requestId?: string;           // Request ID for debugging
  timestamp: number;            // Error timestamp
}
```

### 7.2 Error Codes

```typescript
type ErrorCode =
  // Authentication (401)
  | 'UNAUTHORIZED'              // Not authenticated
  | 'TOKEN_EXPIRED'             // Token has expired
  | 'TOKEN_INVALID'             // Token is malformed
  | 'SESSION_REVOKED'           // Session was revoked

  // Authorization (403)
  | 'FORBIDDEN'                 // Insufficient permissions
  | 'RESOURCE_LOCKED'           // Resource is locked
  | 'RATE_LIMITED'              // Rate limit exceeded

  // Not Found (404)
  | 'NOT_FOUND'                 // Generic not found
  | 'COLONY_NOT_FOUND'          // Colony doesn't exist
  | 'AGENT_NOT_FOUND'           // Agent doesn't exist
  | 'ANCHOR_NOT_FOUND'          // KV anchor doesn't exist

  // Validation (400)
  | 'INVALID_PAYLOAD'           // Malformed payload
  | 'INVALID_MESSAGE_TYPE'      // Unknown message type
  | 'INVALID_ID_FORMAT'         // Invalid ID format
  | 'INVALID_TIMESTAMP'         // Timestamp out of range
  | 'MISSING_REQUIRED_FIELD'    // Required field missing
  | 'FIELD_TYPE_MISMATCH'       // Field has wrong type

  // Conflict (409)
  | 'ALREADY_EXISTS'            // Resource already exists
  | 'VERSION_CONFLICT'          // Optimistic locking failure
  | 'STATE_CONFLICT'            // Invalid state transition

  // Server Errors (500)
  | 'INTERNAL_ERROR'            // Generic server error
  | 'SERVICE_UNAVAILABLE'       // Service temporarily unavailable
  | 'TIMEOUT'                   // Operation timed out
  | 'COMMAND_FAILED'            // Command execution failed

  // Protocol Errors
  | 'PROTOCOL_VIOLATION'        // Protocol not followed
  | 'MESSAGE_TOO_LARGE'         // Message exceeds size limit
  | 'UNSUPPORTED_VERSION'       // Protocol version not supported;
```

### 7.3 Error Response Examples

#### Validation Error

```json
{
  "id": "msg_error_001",
  "timestamp": 1709123456789,
  "type": "error",
  "payload": null,
  "success": false,
  "error": {
    "code": "INVALID_PAYLOAD",
    "message": "Payload validation failed",
    "details": {
      "field": "colonyId",
      "reason": "must be a non-empty string",
      "received": ""
    },
    "requestId": "msg_001",
    "timestamp": 1709123456789
  }
}
```

#### Rate Limit Error

```json
{
  "id": "msg_error_002",
  "timestamp": 1709123456789,
  "type": "error",
  "payload": null,
  "success": false,
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 100,
      "windowMs": 60000,
      "retryAfter": 45000,
      "resetAt": 1709123516789
    },
    "requestId": "msg_050",
    "timestamp": 1709123456789
  }
}
```

#### Not Found Error

```json
{
  "id": "msg_error_003",
  "timestamp": 1709123456789,
  "type": "error",
  "payload": null,
  "success": false,
  "error": {
    "code": "AGENT_NOT_FOUND",
    "message": "Agent not found",
    "details": {
      "agentId": "agent_nonexistent",
      "searchedColonies": ["colony_abc", "colony_def"]
    },
    "requestId": "msg_025",
    "timestamp": 1709123456789
  }
}
```

---

## 8. A2A Package Protocol Extensions

### 8.1 A2A Package over WebSocket

A2A packages can be transmitted via the WebSocket API for agent-to-agent communication:

```typescript
interface A2ATransmitPayload {
  type: 'a2a:transmit';
  payload: {
    senderId: string;
    receiverId: string;
    packageType: string;
    content: unknown;
    options?: {
      privacyLevel?: PrivacyLevel;
      layer?: SubsumptionLayer;
      parentIds?: string[];
    };
  };
}

type PrivacyLevel = 'PUBLIC' | 'COLONY' | 'PRIVATE';
type SubsumptionLayer = 'SAFETY' | 'REFLEX' | 'HABITUAL' | 'DELIBERATE';
```

### 8.2 A2A Event Notification

```typescript
interface A2AEventPayload {
  type: 'event:a2a';
  payload: {
    package: A2APackage;
    delivered: boolean;
    latencyMs: number;
  };
}

interface A2APackage {
  id: string;
  timestamp: number;
  senderId: string;
  receiverId: string;
  type: string;
  payload: unknown;
  parentIds: string[];
  causalChainId: string;
  privacyLevel: PrivacyLevel;
  layer: SubsumptionLayer;
  dpMetadata?: {
    epsilon: number;
    delta: number;
    noiseScale: number;
  };
}
```

### 8.3 Causal Chain Query

```typescript
interface QueryCausalChainPayload {
  type: 'query:causal-chain';
  payload: {
    packageId: string;
    depth?: number;             // Max chain depth (default: 100)
  };
}

interface ResponseCausalChainPayload {
  chain: A2APackage[];
  depth: number;
  totalPackages: number;
}
```

---

## 9. Authentication Schemas

### 9.1 Authentication Request

```typescript
interface AuthPayload {
  type: 'auth';
  payload: {
    token: string;              // JWT or legacy token
    refreshToken?: string;      // For token refresh
  };
}
```

### 9.2 Authentication Response

```typescript
interface AuthSuccessPayload {
  gardenerId: string;
  permissions: Permission[];
  tokenType: 'jwt' | 'legacy';
  expiresAt: number;
  refreshExpiresAt?: number;
}

interface Permission {
  resource: 'colony' | 'agent' | 'dream' | 'stats' | 'kv-cache' | 'federation';
  actions: ('read' | 'write' | 'admin')[];
}
```

### 9.3 JWT Token Structure

```typescript
interface JWTPayload {
  // Standard claims
  sub: string;                  // Gardener ID
  iat: number;                  // Issued at
  exp: number;                  // Expiration
  iss: string;                  // Issuer (polln-api)
  aud: string;                  // Audience (polln-clients)
  jti: string;                  // JWT ID

  // Custom claims
  type: 'access' | 'refresh';
  permissions: Permission[];
}
```

---

## 10. Rate Limiting Schemas

### 10.1 Rate Limit Headers

Rate limit information is included in error responses:

```typescript
interface RateLimitInfo {
  limit: number;                // Max requests per window
  remaining: number;            // Remaining requests
  resetAt: number;              // Window reset timestamp
  retryAfter?: number;          // Seconds until retry (when limited)
}
```

### 10.2 Colony-Aware Rate Limiting

```typescript
interface ColonyRateLimitInfo extends RateLimitInfo {
  colonyLimit: number;
  colonyRemaining: number;

  // Per-resource limits
  resourceLimits: Record<string, {
    read: RateLimitInfo;
    write: RateLimitInfo;
  }>;
}
```

### 10.3 Rate Limit Configuration

```typescript
interface RateLimitConfig {
  // Connection-level
  requestsPerMinute: number;    // Default: 100
  burstLimit: number;           // Default: 10
  windowMs: number;             // Default: 60000

  // Colony-level (NEW)
  colonyRequestsPerMinute: number;  // Default: 1000
  colonyBurstLimit: number;         // Default: 100

  // Resource-level (NEW)
  resourceLimits: Map<string, {
    readPerMinute: number;
    writePerMinute: number;
  }>;
}
```

---

## Appendix A: JSON Schema Definitions

### ClientMessage JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://polln.io/schemas/client-message.json",
  "type": "object",
  "required": ["id", "timestamp", "type", "payload"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^[a-zA-Z0-9_-]{1,100}$"
    },
    "timestamp": {
      "type": "integer",
      "minimum": 1
    },
    "type": {
      "type": "string",
      "enum": [
        "subscribe:colony", "unsubscribe:colony",
        "subscribe:agent", "unsubscribe:agent",
        "subscribe:dreams", "unsubscribe:dreams",
        "subscribe:stats", "unsubscribe:stats",
        "subscribe:kv-cache", "unsubscribe:kv-cache",
        "command:spawn", "command:despawn",
        "command:activate", "command:deactivate",
        "command:dream", "command:sync-federation",
        "command:clear-cache",
        "query:stats", "query:agents", "query:agent",
        "query:config", "query:kv-anchors",
        "query:meadow", "query:federation",
        "ping", "auth"
      ]
    },
    "payload": {
      "oneOf": [
        { "$ref": "#/definitions/SubscribeColonyPayload" },
        { "$ref": "#/definitions/CommandSpawnPayload" },
        { "$ref": "#/definitions/QueryStatsPayload" },
        { "type": "null" }
      ]
    },
    "correlationId": {
      "type": "string",
      "pattern": "^[a-zA-Z0-9_-]{1,100}$"
    },
    "timeout": {
      "type": "integer",
      "minimum": 1000,
      "maximum": 300000
    }
  },
  "definitions": {
    "SubscribeColonyPayload": {
      "type": "object",
      "required": ["colonyId", "events"],
      "properties": {
        "colonyId": { "type": "string", "minLength": 1, "maxLength": 100 },
        "events": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": [
              "agent_registered", "agent_unregistered",
              "agent_activated", "agent_deactivated",
              "stats_updated", "dream_completed",
              "kv_cache_updated", "federation_sync", "error"
            ]
          },
          "minItems": 1
        }
      }
    }
  }
}
```

---

## Appendix B: Type Definition Reference

Full TypeScript type definitions are available in:
- `src/api/types.ts` - API-specific types
- `src/core/types.ts` - Core domain types
- `src/core/communication.ts` - A2A package types

---

*Document generated for glm-4.7 implementation agents*
*Schema version: 1.0.0*
