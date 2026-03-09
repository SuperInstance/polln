# POLLN Security Blueprint

**Document Version**: 1.0.0
**Last Updated**: 2026-03-08
**Classification**: Implementation Guide for glm-4.7 Agents

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication Implementation](#authentication-implementation)
3. [Authorization Implementation](#authorization-implementation)
4. [Guardian Angel Integration](#guardian-angel-integration)
5. [Input Validation Patterns](#input-validation-patterns)
6. [Audit Logging Implementation](#audit-logging-implementation)
7. [Edge Cases and Attack Vectors](#edge-cases-and-attack-vectors)
8. [Security Test Scenarios](#security-test-scenarios)
9. [Production Hardening](#production-hardening)

---

## Overview

This blueprint provides implementation guidance for security features in POLLN. It is designed to be used by glm-4.7 agents implementing security controls.

### Key Files to Modify

| File | Purpose | Security Concerns |
|------|---------|-------------------|
| `src/api/middleware.ts` | Authentication, rate limiting, validation | Token validation, input sanitization |
| `src/core/safety.ts` | Safety layer, constraints, kill switch | Constraint evaluation, rollback |
| `src/core/guardian/*.ts` | Guardian angel, constraints | Real-time monitoring, veto logic |
| `src/core/communication.ts` | A2A package system | Causal chain integrity, signing |
| `src/api/types.ts` | API type definitions | Permission models, audit types |

---

## Authentication Implementation

### 2.1 JWT Authentication Pattern

The existing `AuthenticationMiddleware` class in `src/api/middleware.ts` implements JWT authentication. Here is the recommended usage pattern:

```typescript
// Example: Protecting a WebSocket connection
import { AuthenticationMiddleware } from './middleware.js';

const authMiddleware = new AuthenticationMiddleware({
  secret: process.env.JWT_SECRET!,
  algorithm: 'HS256',
  accessTokenExpiry: 3600,    // 1 hour
  refreshTokenExpiry: 604800, // 7 days
  issuer: 'polln-api',
  audience: 'polln-clients'
});

// On WebSocket connection
wsServer.on('connection', async (ws, req) => {
  // Extract token from query or header
  const token = extractToken(req);

  // Validate token
  const validated = authMiddleware.validateAccessToken(token);
  if (!validated) {
    ws.close(4001, 'Unauthorized');
    return;
  }

  // Create authenticated client
  const client = authMiddleware.authenticate(
    generateClientId(),
    token
  );

  // Store client for later use
  clients.set(client.id, client);
});
```

### 2.2 Token Generation Pattern

```typescript
// Generating tokens for a new session
function createSession(gardenerId: string, roles: string[]): TokenPair {
  // Map roles to permissions
  const permissions = rolesToPermissions(roles);

  // Generate token pair
  const tokenPair = authMiddleware.generateTokenPair(
    gardenerId,
    permissions,
    {
      // Additional claims
      sessionId: generateSessionId(),
      ip: request.ip
    }
  );

  // Log token creation
  auditLogger.log({
    category: 'authentication',
    type: 'token_created',
    gardenerId,
    sessionId: tokenPair.accessToken.slice(-8) // Last 8 chars only
  });

  return tokenPair;
}
```

### 2.3 Token Refresh Pattern

```typescript
// Refreshing an expired access token
async function refreshSession(refreshToken: string): Promise<TokenPair | null> {
  // Validate and refresh
  const newTokens = authMiddleware.refreshAccessToken(refreshToken);

  if (!newTokens) {
    // Refresh failed - possible token theft
    auditLogger.log({
      category: 'authentication',
      type: 'refresh_failed',
      severity: 'WARNING'
    });
    return null;
  }

  // Log successful refresh
  auditLogger.log({
    category: 'authentication',
    type: 'token_refreshed'
  });

  return newTokens;
}
```

### 2.4 Token Revocation Pattern

```typescript
// On logout or security event
async function revokeSession(refreshToken: string): Promise<void> {
  // Revoke refresh token
  const revoked = authMiddleware.revokeRefreshToken(refreshToken);

  if (revoked) {
    auditLogger.log({
      category: 'authentication',
      type: 'token_revoked',
      severity: 'INFO'
    });
  }
}

// On security breach - revoke all tokens for user
async function revokeAllUserTokens(gardenerId: string): Promise<void> {
  // This requires implementing a revocation list
  // See production hardening section
  await revocationList.addUser(gardenerId);

  auditLogger.log({
    category: 'authentication',
    type: 'all_tokens_revoked',
    gardenerId,
    severity: 'WARNING'
  });
}
```

---

## Authorization Implementation

### 3.1 Permission Check Pattern

```typescript
// Check if client has permission for action
function checkPermission(
  client: AuthenticatedClient,
  resource: string,
  action: string
): boolean {
  return client.permissions.some(
    p => (p.resource === resource || p.resource === '*') &&
         (p.actions.includes(action) || p.actions.includes('*'))
  );
}

// Usage in handler
function handleSpawnAgent(client: AuthenticatedClient, payload: unknown): Response {
  if (!checkPermission(client, 'agent', 'write')) {
    return {
      success: false,
      error: {
        code: 'FORBIDDEN',
        message: 'Insufficient permissions to spawn agents'
      }
    };
  }

  // Proceed with spawn
  // ...
}
```

### 3.2 Resource-Based Authorization

```typescript
// Check if client can access specific resource
function canAccessResource(
  client: AuthenticatedClient,
  resource: { colonyId: string; privacyLevel: PrivacyLevel }
): boolean {
  // Public resources are always accessible
  if (resource.privacyLevel === PrivacyLevel.PUBLIC) {
    return true;
  }

  // Colony resources require same colony membership
  if (resource.privacyLevel === PrivacyLevel.COLONY) {
    return client.colonyId === resource.colonyId;
  }

  // Private resources require ownership
  if (resource.privacyLevel === PrivacyLevel.PRIVATE) {
    return client.isOwner === true;
  }

  return false;
}
```

### 3.3 Role-Based Permission Mapping

```typescript
// Map roles to permissions
const ROLE_PERMISSIONS: Record<string, Permission[]> = {
  admin: [
    { resource: '*', actions: ['*'] }
  ],
  keeper: [
    { resource: 'colony', actions: ['read', 'write'] },
    { resource: 'agent', actions: ['read', 'write', 'execute'] },
    { resource: 'dream', actions: ['read', 'write'] },
    { resource: 'stats', actions: ['read'] },
    { resource: 'config', actions: ['read'] }
  ],
  observer: [
    { resource: 'colony', actions: ['read'] },
    { resource: 'agent', actions: ['read'] },
    { resource: 'stats', actions: ['read'] }
  ]
};

function rolesToPermissions(roles: string[]): Permission[] {
  const permissions: Permission[] = [];

  for (const role of roles) {
    const rolePerms = ROLE_PERMISSIONS[role];
    if (rolePerms) {
      permissions.push(...rolePerms);
    }
  }

  // Deduplicate
  return deduplicatePermissions(permissions);
}
```

---

## Guardian Angel Integration

### 4.1 Basic Integration Pattern

The Guardian Angel system provides real-time execution monitoring with veto power. Integrate it with the A2A package system:

```typescript
import { GuardianIntegratedSafety, createGuardianContext } from '../guardian/index.js';
import { SafetyLayer } from '../safety.js';

// Create integrated safety system
const safetyLayer = new SafetyLayer();
const guardianSafety = new GuardianIntegratedSafety(safetyLayer, {
  enabled: true,
  strictMode: false,
  learningEnabled: true,
  allowThreshold: 0.8,
  modifyThreshold: 0.5,
  vetoThreshold: 0.3
});

// Review A2A package before execution
async function processPackage(pkg: A2APackage): Promise<void> {
  // Review with guardian
  const review = await guardianSafety.reviewPackage(pkg);

  switch (review.decision) {
    case 'ALLOW':
      // Proceed with execution
      await executePackage(pkg);
      guardianSafety.completeExecution(pkg, 'success');
      break;

    case 'MODIFY':
      // Apply modifications and proceed
      const modifiedPkg = applyModifications(pkg, review.modifications);
      await executePackage(modifiedPkg);
      guardianSafety.completeExecution(pkg, 'success');
      break;

    case 'VETO':
      // Block execution
      guardianSafety.completeExecution(pkg, 'failure', review.reason);
      throw new Error(`Guardian veto: ${review.reason}`);
  }
}
```

### 4.2 Custom Constraint Implementation

```typescript
import { GuardianConstraint, GuardianContext, ConstraintResult } from '../guardian/types.js';

// Create a custom constraint
const customConstraint: GuardianConstraint = {
  id: 'custom-sensitive-operation',
  name: 'Sensitive Operation Check',
  description: 'Validates sensitive operations require additional confirmation',
  category: 'security',
  severity: 'high',
  weight: 1.0,
  active: true,
  version: 1,
  adaptiveWeight: true,
  falsePositiveCount: 0,
  falseNegativeCount: 0,
  lastAdjusted: Date.now(),

  evaluate: async (context: GuardianContext): Promise<ConstraintResult> => {
    // Check if this is a sensitive operation
    const sensitiveOps = ['delete_agent', 'modify_constraint', 'export_data'];
    const isSensitive = sensitiveOps.includes(context.action);

    if (isSensitive) {
      // Check for confirmation in metadata
      const confirmed = context.metadata.confirmed === true;

      if (!confirmed) {
        return {
          passed: false,
          decision: 'MODIFY',
          reason: 'Sensitive operation requires confirmation',
          severity: 'high',
          confidence: 0.95,
          modifications: {
            metadata: {
              ...context.metadata,
              requiresConfirmation: true
            }
          }
        };
      }
    }

    return {
      passed: true,
      decision: 'ALLOW',
      reason: 'Operation is safe',
      severity: 'low',
      confidence: 0.9
    };
  }
};

// Add constraint to guardian
const guardian = guardianSafety.getGuardian();
guardian.addConstraint(customConstraint);
```

### 4.3 Handling Guardian Events

```typescript
// Listen for guardian events
const guardian = guardianSafety.getGuardian();

// Review completed
guardian.on('review_completed', (review: GuardianReview) => {
  auditLogger.log({
    category: 'safety',
    type: 'guardian_review',
    agentId: review.agentId,
    details: {
      decision: review.decision,
      confidence: review.confidence,
      reviewTimeMs: review.reviewTimeMs
    }
  });
});

// Alert created
guardian.on('alert_created', (alert: GuardianAlert) => {
  // Send to monitoring system
  monitoring.alert({
    severity: alert.severity,
    title: alert.title,
    description: alert.description
  });
});

// Weight adjusted (learning)
guardian.on('weight_adjusted', (adjustment: WeightAdjustment) => {
  logger.info('Constraint weight adjusted', {
    constraintId: adjustment.constraintId,
    oldWeight: adjustment.oldWeight,
    newWeight: adjustment.newWeight
  });
});
```

---

## Input Validation Patterns

### 5.1 Message Validation

The `ValidationMiddleware` class provides comprehensive input validation:

```typescript
import { ValidationMiddleware } from './middleware.js';

const validator = new ValidationMiddleware({
  maxMessageAge: 300000,      // 5 minutes
  maxPayloadSize: 10485760,   // 10MB
  maxStringLength: 10000,
  sanitizeStrings: true,
  validateJson: true
});

// Validate incoming message
function handleIncomingMessage(raw: unknown): ClientMessage | null {
  if (!validator.validateMessage(raw)) {
    return null;
  }

  const message = raw as ClientMessage;

  // Additional type-specific validation
  if (message.type.startsWith('subscribe:')) {
    if (!validator.validateSubscription(message.type, message.payload)) {
      return null;
    }
  }

  if (message.type.startsWith('command:')) {
    if (!validator.validateCommand(message.type, message.payload)) {
      return null;
    }
  }

  return message;
}
```

### 5.2 Custom Payload Validation

```typescript
// Validate agent spawn payload
interface SpawnAgentPayload {
  typeId: string;
  config?: Record<string, unknown>;
}

function validateSpawnPayload(payload: unknown): payload is SpawnAgentPayload {
  if (!payload || typeof payload !== 'object') {
    return false;
  }

  const p = payload as Record<string, unknown>;

  // typeId is required and must be valid
  if (typeof p.typeId !== 'string' || p.typeId.length === 0) {
    return false;
  }

  // typeId must be alphanumeric with dashes/underscores
  if (!/^[a-zA-Z0-9_-]+$/.test(p.typeId)) {
    return false;
  }

  // config is optional but must be object if present
  if (p.config !== undefined && typeof p.config !== 'object') {
    return false;
  }

  // Validate config keys
  if (p.config) {
    const config = p.config as Record<string, unknown>;
    for (const key of Object.keys(config)) {
      if (!isValidConfigKey(key)) {
        return false;
      }
    }
  }

  return true;
}

function isValidConfigKey(key: string): boolean {
  // Must be valid identifier
  if (!/^[a-zA-Z_][a-zA-Z0-9_]*$/.test(key)) {
    return false;
  }

  // Block dangerous keys
  const blocked = ['__proto__', 'constructor', 'prototype', 'eval', 'function'];
  return !blocked.includes(key);
}
```

### 5.3 String Sanitization

```typescript
// Sanitize user-provided strings
function sanitizeUserInput(input: string): string {
  // Remove null bytes
  let sanitized = input.replace(/\0/g, '');

  // Remove control characters (except newline, tab, CR)
  sanitized = sanitized.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');

  // Trim to max length
  if (sanitized.length > 10000) {
    sanitized = sanitized.slice(0, 10000);
  }

  return sanitized;
}

// Validate string doesn't contain dangerous patterns
function isSafeString(input: string): boolean {
  const dangerousPatterns = [
    /<script[^>]*>.*?<\/script>/gis,
    /<iframe[^>]*>.*?<\/iframe>/gis,
    /javascript:/gi,
    /on\w+\s*=/gi,
    /<\?php/gi,
    /\$\{.*?\}/g  // Template injection
  ];

  return !dangerousPatterns.some(p => p.test(input));
}
```

---

## Audit Logging Implementation

### 6.1 Core Audit Logger

```typescript
interface AuditLogger {
  log(event: Partial<AuditEvent>): void;
  query(filter: AuditFilter): Promise<AuditEvent[]>;
}

class FileAuditLogger implements AuditLogger {
  private buffer: AuditEvent[] = [];
  private flushInterval: NodeJS.Timeout;

  constructor(private config: AuditLogConfig) {
    this.flushInterval = setInterval(
      () => this.flush(),
      config.flushIntervalMs
    );
  }

  log(event: Partial<AuditEvent>): void {
    const fullEvent: AuditEvent = {
      id: uuidv4(),
      timestamp: Date.now(),
      version: '1.0.0',
      category: event.category ?? 'system',
      severity: event.severity ?? 'INFO',
      type: event.type ?? 'unknown',
      action: event.action ?? 'unknown',
      resource: event.resource ?? 'unknown',
      outcome: event.outcome ?? 'success',
      message: event.message ?? '',
      piiInvolved: event.piiInvolved ?? false,
      ...event
    };

    this.buffer.push(fullEvent);

    // Flush if buffer full
    if (this.buffer.length >= this.config.batchSize) {
      this.flush();
    }
  }

  private async flush(): Promise<void> {
    if (this.buffer.length === 0) return;

    const events = [...this.buffer];
    this.buffer = [];

    // Write to file
    await fs.appendFile(
      this.config.connectionString,
      events.map(e => JSON.stringify(e)).join('\n') + '\n'
    );

    // Forward to external systems
    for (const dest of this.config.forwardTo) {
      await this.forward(events, dest);
    }
  }

  private async forward(events: AuditEvent[], dest: any): Promise<void> {
    // Implementation for external log forwarding
  }
}
```

### 6.2 Audit Decorator Pattern

```typescript
// Decorator for automatic audit logging
function audited(
  category: AuditCategory,
  action: string,
  options?: { resource?: string; piiInvolved?: boolean }
) {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor
  ) {
    const original = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      const startTime = Date.now();
      let outcome: 'success' | 'failure' = 'success';
      let message = `${action} completed`;

      try {
        const result = await original.apply(this, args);
        return result;
      } catch (error) {
        outcome = 'failure';
        message = `${action} failed: ${error.message}`;
        throw error;
      } finally {
        auditLogger.log({
          category,
          type: action as AuditEventType,
          action,
          resource: options?.resource ?? 'unknown',
          outcome,
          message,
          piiInvolved: options?.piiInvolved ?? false,
          details: {
            durationMs: Date.now() - startTime
          }
        });
      }
    };

    return descriptor;
  };
}

// Usage
class AgentManager {
  @audited('agent_lifecycle', 'agent_spawned', { resource: 'agent' })
  async spawnAgent(typeId: string, config: AgentConfig): Promise<Agent> {
    // Implementation
  }

  @audited('agent_lifecycle', 'agent_killed', { resource: 'agent' })
  async killAgent(agentId: string): Promise<void> {
    // Implementation
  }
}
```

---

## Edge Cases and Attack Vectors

### 7.1 Token Theft

**Scenario**: Attacker steals a valid JWT token.

**Detection**:
- Multiple concurrent sessions from different IPs
- Token used after logout
- Unusual access patterns

**Mitigation**:
```typescript
// Implement token binding
interface TokenBinding {
  token: string;
  fingerprint: string;  // Browser fingerprint
  ipHash: string;       // Hash of IP address
}

function validateTokenBinding(token: string, request: Request): boolean {
  const binding = tokenBindings.get(token);
  if (!binding) return false;

  // Check fingerprint matches
  const currentFingerprint = generateFingerprint(request);
  if (binding.fingerprint !== currentFingerprint) {
    // Potential token theft
    auditLogger.log({
      category: 'authentication',
      type: 'token_binding_mismatch',
      severity: 'WARNING'
    });
    return false;
  }

  return true;
}
```

### 7.2 Rate Limit Bypass

**Scenario**: Attacker uses multiple IPs or distributed attack.

**Detection**:
- Coordinated requests from multiple sources
- Request patterns suggesting automation

**Mitigation**:
```typescript
// Implement distributed rate limiting
class DistributedRateLimiter {
  private globalCounter: Counter;
  private ipTrackers: Map<string, Counter> = new Map();

  checkLimit(ip: string): boolean {
    // Check global limit first
    if (!this.globalCounter.check()) {
      return false;
    }

    // Check per-IP limit
    let tracker = this.ipTrackers.get(ip);
    if (!tracker) {
      tracker = new Counter(this.config.perIpLimit);
      this.ipTrackers.set(ip, tracker);
    }

    return tracker.check();
  }

  // Detect coordinated attacks
  detectCoordinatedAttack(): boolean {
    // If many IPs hitting similar limits simultaneously
    const activeIps = Array.from(this.ipTrackers.values())
      .filter(c => c.utilization() > 0.8).length;

    return activeIps > 100; // Threshold
  }
}
```

### 7.3 Injection via A2A Package

**Scenario**: Malicious payload in A2A package.

**Detection**:
- Unusual characters in payload
- Known injection patterns
- Unexpected payload structure

**Mitigation**:
```typescript
// Sanitize A2A package payload
function sanitizeA2APayload(pkg: A2APackage): A2APackage {
  return {
    ...pkg,
    payload: deepSanitize(pkg.payload)
  };
}

function deepSanitize(obj: unknown): unknown {
  if (typeof obj === 'string') {
    return sanitizeUserInput(obj);
  }

  if (Array.isArray(obj)) {
    return obj.map(deepSanitize);
  }

  if (obj && typeof obj === 'object') {
    const sanitized: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj)) {
      if (isValidKey(key)) {
        sanitized[key] = deepSanitize(value);
      }
    }
    return sanitized;
  }

  return obj;
}
```

### 7.4 Guardian Constraint Bypass

**Scenario**: Attacker crafts payload to bypass specific constraints.

**Detection**:
- Repeated constraint modifications
- Pattern of near-threshold values
- Feedback anomalies

**Mitigation**:
```typescript
// Implement constraint hardening
class HardenedGuardian extends GuardianAngelAgent {
  private recentModifications: Map<string, number[]> = new Map();

  override async reviewProposal(context: GuardianContext): Promise<GuardianReview> {
    // Check for suspicious patterns
    if (this.isSuspiciousPattern(context)) {
      // Force strict mode for this review
      const originalStrictMode = this.config.strictMode;
      this.config.strictMode = true;

      try {
        return await super.reviewProposal(context);
      } finally {
        this.config.strictMode = originalStrictMode;
      }
    }

    return super.reviewProposal(context);
  }

  private isSuspiciousPattern(context: GuardianContext): boolean {
    // Track modifications per agent
    const agentId = context.agentId;
    let modifications = this.recentModifications.get(agentId) ?? [];

    // Keep last hour
    const oneHourAgo = Date.now() - 3600000;
    modifications = modifications.filter(t => t > oneHourAgo);

    // Check for high modification rate
    if (modifications.length > 10) {
      return true;
    }

    return false;
  }
}
```

### 7.5 Memory Exhaustion

**Scenario**: Attacker causes memory exhaustion via large payloads or unbounded collections.

**Detection**:
- Growing memory usage
- Large number of cached items
- Slow garbage collection

**Mitigation**:
```typescript
// Implement bounded collections
class BoundedMap<K, V> {
  private map: Map<K, V> = new Map();
  private accessOrder: K[] = [];

  constructor(private maxSize: number) {}

  get(key: K): V | undefined {
    return this.map.get(key);
  }

  set(key: K, value: V): void {
    if (this.map.size >= this.maxSize && !this.map.has(key)) {
      // Evict oldest
      const oldest = this.accessOrder.shift();
      if (oldest) {
        this.map.delete(oldest);
      }
    }

    this.map.set(key, value);
    this.accessOrder.push(key);
  }
}

// Monitor memory usage
class MemoryMonitor {
  private threshold: number;

  constructor(thresholdMB: number = 1024) {
    this.threshold = thresholdMB * 1024 * 1024;
  }

  check(): boolean {
    const usage = process.memoryUsage();
    if (usage.heapUsed > this.threshold) {
      auditLogger.log({
        category: 'system',
        type: 'memory_threshold_exceeded',
        severity: 'WARNING',
        details: {
          heapUsed: usage.heapUsed,
          threshold: this.threshold
        }
      });

      // Trigger cleanup
      this.cleanup();
      return false;
    }
    return true;
  }

  private cleanup(): void {
    // Force garbage collection if available
    if (global.gc) {
      global.gc();
    }
  }
}
```

---

## Security Test Scenarios

### 8.1 Authentication Tests

```typescript
describe('Authentication Security', () => {
  let authMiddleware: AuthenticationMiddleware;

  beforeEach(() => {
    authMiddleware = new AuthenticationMiddleware({
      secret: 'test-secret-key-min-256-bits-long',
      algorithm: 'HS256'
    });
  });

  test('rejects invalid tokens', () => {
    const result = authMiddleware.validateAccessToken('invalid-token');
    expect(result).toBeNull();
  });

  test('rejects expired tokens', () => {
    const token = jwt.sign(
      { sub: 'user1', permissions: [], type: 'access' },
      'test-secret-key-min-256-bits-long',
      { expiresIn: '-1h' }
    );

    const result = authMiddleware.validateAccessToken(token);
    expect(result).toBeNull();
  });

  test('rejects refresh tokens for access validation', () => {
    const { refreshToken } = authMiddleware.generateTokenPair(
      'user1',
      [{ resource: 'colony', actions: ['read'] }]
    );

    const result = authMiddleware.validateAccessToken(refreshToken);
    expect(result).toBeNull();
  });

  test('invalidates old refresh token on refresh', async () => {
    const tokens = authMiddleware.generateTokenPair(
      'user1',
      [{ resource: 'colony', actions: ['read'] }]
    );

    // First refresh should work
    const newTokens = authMiddleware.refreshAccessToken(tokens.refreshToken);
    expect(newTokens).not.toBeNull();

    // Second refresh with same token should fail
    const failRefresh = authMiddleware.refreshAccessToken(tokens.refreshToken);
    expect(failRefresh).toBeNull();
  });
});
```

### 8.2 Authorization Tests

```typescript
describe('Authorization Security', () => {
  test('denies access without permission', () => {
    const client: AuthenticatedClient = {
      id: 'client1',
      gardenerId: 'user1',
      permissions: [{ resource: 'stats', actions: ['read'] }],
      token: 'token',
      connectedAt: Date.now(),
      lastActivity: Date.now()
    };

    expect(checkPermission(client, 'agent', 'write')).toBe(false);
  });

  test('allows access with wildcard permission', () => {
    const client: AuthenticatedClient = {
      id: 'client1',
      gardenerId: 'user1',
      permissions: [{ resource: '*', actions: ['*'] }],
      token: 'token',
      connectedAt: Date.now(),
      lastActivity: Date.now()
    };

    expect(checkPermission(client, 'agent', 'write')).toBe(true);
    expect(checkPermission(client, 'colony', 'admin')).toBe(true);
  });

  test('enforces privacy levels', () => {
    const publicResource = { colonyId: 'colony1', privacyLevel: PrivacyLevel.PUBLIC };
    const colonyResource = { colonyId: 'colony1', privacyLevel: PrivacyLevel.COLONY };
    const privateResource = { colonyId: 'colony1', privacyLevel: PrivacyLevel.PRIVATE };

    const client: AuthenticatedClient = {
      id: 'client1',
      gardenerId: 'user1',
      colonyId: 'colony1',
      isOwner: false,
      permissions: [],
      token: 'token',
      connectedAt: Date.now(),
      lastActivity: Date.now()
    };

    expect(canAccessResource(client, publicResource)).toBe(true);
    expect(canAccessResource(client, colonyResource)).toBe(true);
    expect(canAccessResource(client, privateResource)).toBe(false);
  });
});
```

### 8.3 Input Validation Tests

```typescript
describe('Input Validation Security', () => {
  let validator: ValidationMiddleware;

  beforeEach(() => {
    validator = new ValidationMiddleware({
      maxMessageAge: 300000,
      maxPayloadSize: 10485760,
      maxStringLength: 10000
    });
  });

  test('rejects messages with invalid IDs', () => {
    expect(validator.validateMessage({
      id: '../../../etc/passwd',
      timestamp: Date.now(),
      type: 'ping',
      payload: {}
    })).toBe(false);
  });

  test('rejects messages with future timestamps', () => {
    expect(validator.validateMessage({
      id: 'msg1',
      timestamp: Date.now() + 120000, // 2 minutes in future
      type: 'ping',
      payload: {}
    })).toBe(false);
  });

  test('rejects messages with old timestamps', () => {
    expect(validator.validateMessage({
      id: 'msg1',
      timestamp: Date.now() - 400000, // Older than maxMessageAge
      type: 'ping',
      payload: {}
    })).toBe(false);
  });

  test('rejects XSS attempts', () => {
    expect(validator.validateMessage({
      id: 'msg1',
      timestamp: Date.now(),
      type: 'command:spawn',
      payload: {
        typeId: '<script>alert(1)</script>'
      }
    })).toBe(false);
  });

  test('rejects prototype pollution attempts', () => {
    expect(validator.validateMessage({
      id: 'msg1',
      timestamp: Date.now(),
      type: 'command:spawn',
      payload: {
        typeId: 'valid',
        config: {
          __proto__: { polluted: true }
        }
      }
    })).toBe(false);
  });
});
```

### 8.4 Guardian Tests

```typescript
describe('Guardian Angel Security', () => {
  let guardian: GuardianAngelAgent;

  beforeEach(() => {
    guardian = new GuardianAngelAgent({
      enabled: true,
      strictMode: false,
      learningEnabled: false
    });
  });

  test('vetoes blacklisted actions', async () => {
    const context: GuardianContext = {
      proposalId: 'p1',
      agentId: 'agent1',
      action: 'delete_all_data',
      payload: {},
      trace: [],
      metadata: {},
      timestamp: Date.now(),
      layer: 'DELIBERATE'
    };

    const review = await guardian.reviewProposal(context);
    expect(review.decision).toBe('VETO');
  });

  test('vetoes injection attempts', async () => {
    const context: GuardianContext = {
      proposalId: 'p1',
      agentId: 'agent1',
      action: 'query',
      payload: { sql: "SELECT * FROM users; DROP TABLE users;--" },
      trace: [],
      metadata: {},
      timestamp: Date.now(),
      layer: 'DELIBERATE'
    };

    const review = await guardian.reviewProposal(context);
    expect(review.decision).toBe('VETO');
  });

  test('allows whitelisted actions', async () => {
    const context: GuardianContext = {
      proposalId: 'p1',
      agentId: 'agent1',
      action: 'analyze',
      payload: { data: 'test' },
      trace: ['parent1'],
      metadata: {},
      timestamp: Date.now(),
      layer: 'DELIBERATE'
    };

    const review = await guardian.reviewProposal(context);
    expect(review.decision).toBe('ALLOW');
  });

  test('strict mode vetoes on any failure', async () => {
    guardian.enableStrictMode();

    const context: GuardianContext = {
      proposalId: 'p1',
      agentId: 'agent1',
      action: 'analyze',
      payload: { data: 'a'.repeat(20 * 1024 * 1024) }, // Large payload
      trace: [],
      metadata: {},
      timestamp: Date.now(),
      layer: 'DELIBERATE'
    };

    const review = await guardian.reviewProposal(context);
    expect(review.decision).toBe('VETO');
  });
});
```

### 8.5 Rate Limiting Tests

```typescript
describe('Rate Limiting Security', () => {
  let rateLimiter: RateLimitMiddleware;

  beforeEach(() => {
    rateLimiter = new RateLimitMiddleware({
      requestsPerMinute: 10,
      burstLimit: 3,
      windowMs: 60000
    });
  });

  test('allows requests within limit', () => {
    for (let i = 0; i < 5; i++) {
      expect(rateLimiter.checkLimit('client1')).toBe(true);
    }
  });

  test('blocks requests exceeding limit', () => {
    // Use up burst tokens
    for (let i = 0; i < 3; i++) {
      rateLimiter.checkLimit('client1');
    }

    // Use up rate limit
    for (let i = 0; i < 7; i++) {
      rateLimiter.checkLimit('client1');
    }

    // Should be blocked now
    expect(rateLimiter.checkLimit('client1')).toBe(false);
  });

  test('separate limits per client', () => {
    // Exhaust client1's limit
    for (let i = 0; i < 10; i++) {
      rateLimiter.checkLimit('client1');
    }

    // client2 should still be allowed
    expect(rateLimiter.checkLimit('client2')).toBe(true);
  });
});
```

---

## Production Hardening

### 9.1 Environment Configuration

```bash
# .env.production (DO NOT COMMIT)

# JWT Configuration
JWT_SECRET=<256-bit-random-string>
JWT_ALGORITHM=HS256
JWT_ACCESS_EXPIRY=3600
JWT_REFRESH_EXPIRY=604800
JWT_ISSUER=polln-api
JWT_AUDIENCE=polln-clients

# Validation
VALIDATION_MAX_MESSAGE_AGE=300000
VALIDATION_MAX_PAYLOAD_SIZE=10485760
VALIDATION_MAX_STRING_LENGTH=10000

# Rate Limiting
RATE_LIMIT_REQUESTS_PER_MINUTE=100
RATE_LIMIT_BURST_LIMIT=10
RATE_LIMIT_WINDOW_MS=60000

# Guardian
GUARDIAN_ENABLED=true
GUARDIAN_STRICT_MODE=false
GUARDIAN_LEARNING_ENABLED=true

# Audit
AUDIT_RETENTION_DAYS=90
AUDIT_LOG_PATH=/var/log/polln/audit
AUDIT_SIGN_LOGS=true

# Encryption
ENCRYPTION_ALGORITHM=AES-256-GCM
KEY_ROTATION_DAYS=30
```

### 9.2 Token Revocation List

For production, implement a distributed token revocation list:

```typescript
import { Redis } from 'ioredis';

class TokenRevocationList {
  private redis: Redis;
  private prefix = 'revoked:';

  constructor(redisUrl: string) {
    this.redis = new Redis(redisUrl);
  }

  async revoke(jti: string, expiresAt: number): Promise<void> {
    const ttl = Math.max(0, Math.floor((expiresAt - Date.now()) / 1000));
    await this.redis.setex(
      `${this.prefix}${jti}`,
      ttl,
      '1'
    );
  }

  async isRevoked(jti: string): Promise<boolean> {
    const result = await this.redis.get(`${this.prefix}${jti}`);
    return result === '1';
  }

  async revokeUser(gardenerId: string): Promise<void> {
    // Store user-level revocation with TTL
    await this.redis.setex(
      `${this.prefix}user:${gardenerId}`,
      86400, // 24 hours
      Date.now().toString()
    );
  }

  async isUserRevoked(gardenerId: string, tokenIat: number): Promise<boolean> {
    const revokedAt = await this.redis.get(`${this.prefix}user:${gardenerId}`);
    if (!revokedAt) return false;

    return tokenIat * 1000 < parseInt(revokedAt);
  }
}
```

### 9.3 Key Rotation

```typescript
class KeyRotationManager {
  private currentKeyId: string;
  private keys: Map<string, { key: string; createdAt: number }> = new Map();
  private rotationInterval: NodeJS.Timeout;

  constructor(
    private kmsClient: KMSClient,
    private rotationDays: number = 30
  ) {
    this.rotationInterval = setInterval(
      () => this.rotate(),
      rotationDays * 24 * 60 * 60 * 1000
    );
  }

  async rotate(): Promise<void> {
    const newKeyId = uuidv4();
    const newKey = await this.kmsClient.generateKey();

    this.keys.set(newKeyId, {
      key: newKey,
      createdAt: Date.now()
    });

    this.currentKeyId = newKeyId;

    // Clean up old keys (keep last 3)
    const sortedKeys = Array.from(this.keys.entries())
      .sort((a, b) => b[1].createdAt - a[1].createdAt);

    for (let i = 3; i < sortedKeys.length; i++) {
      this.keys.delete(sortedKeys[i][0]);
    }

    auditLogger.log({
      category: 'system',
      type: 'key_rotated',
      severity: 'INFO',
      details: { keyId: newKeyId }
    });
  }

  getCurrentKey(): { keyId: string; key: string } {
    const keyData = this.keys.get(this.currentKeyId)!;
    return {
      keyId: this.currentKeyId,
      key: keyData.key
    };
  }

  getKey(keyId: string): string | undefined {
    return this.keys.get(keyId)?.key;
  }
}
```

### 9.4 Monitoring and Alerting

```typescript
// Security metrics collection
const securityMetrics = {
  // Authentication metrics
  authAttempts: new Counter({
    name: 'polln_auth_attempts_total',
    help: 'Total authentication attempts',
    labelNames: ['outcome']
  }),

  tokenRefreshes: new Counter({
    name: 'polln_token_refreshes_total',
    help: 'Total token refresh attempts',
    labelNames: ['outcome']
  }),

  // Authorization metrics
  accessDenied: new Counter({
    name: 'polln_access_denied_total',
    help: 'Total access denied events',
    labelNames: ['resource', 'action']
  }),

  // Guardian metrics
  guardianReviews: new Counter({
    name: 'polln_guardian_reviews_total',
    help: 'Total guardian reviews',
    labelNames: ['decision']
  }),

  guardianVetoes: new Counter({
    name: 'polln_guardian_vetoes_total',
    help: 'Total guardian vetoes',
    labelNames: ['constraint']
  }),

  // Rate limiting
  rateLimitExceeded: new Counter({
    name: 'polln_rate_limit_exceeded_total',
    help: 'Total rate limit exceeded events',
    labelNames: ['client_type']
  })
};

// Alert thresholds
const alertThresholds = {
  failedAuthRate: 10,      // per minute
  guardianVetoRate: 5,     // per minute
  rateLimitRate: 100       // per minute
};

// Alert handler
function checkAlerts(): void {
  const failedAuth = securityMetrics.authAttempts.get({ outcome: 'failure' });
  if (failedAuth > alertThresholds.failedAuthRate) {
    sendAlert('high_failed_auth_rate', {
      rate: failedAuth,
      threshold: alertThresholds.failedAuthRate
    });
  }

  // ... other checks
}
```

---

## Summary

This blueprint provides comprehensive implementation guidance for POLLN security features. Key points:

1. **Authentication**: Use JWT with proper expiry, single-use refresh tokens, and revocation support
2. **Authorization**: Implement RBAC with permission checks on every resource access
3. **Guardian Integration**: Enable real-time monitoring with the Guardian Angel system
4. **Input Validation**: Validate and sanitize all user input
5. **Audit Logging**: Log all security-relevant events
6. **Edge Cases**: Handle token theft, rate limit bypass, injection, and memory exhaustion
7. **Testing**: Implement comprehensive security tests
8. **Production**: Use environment variables, token revocation, key rotation, and monitoring

---

*Document maintained by: POLLN Security Architecture Team*
*Next review: 2026-Q2*
