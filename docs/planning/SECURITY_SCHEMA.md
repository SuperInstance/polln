# POLLN Security Schema

**Document Version**: 1.0.0
**Last Updated**: 2026-03-08
**Classification**: Internal Architecture Document

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication Schemas](#authentication-schemas)
3. [Authorization Models](#authorization-models)
4. [Threat Model (STRIDE)](#threat-model-stride)
5. [Security Invariants](#security-invariants)
6. [Audit Event Schemas](#audit-event-schemas)
7. [Encryption Patterns](#encryption-patterns)
8. [Security Constraint Categories](#security-constraint-categories)

---

## Overview

This document defines the security schemas, threat models, and invariants for the POLLN distributed intelligence system. These schemas are designed to guide secure implementation by glm-4.7 agents.

### Security Architecture Principles

1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Agents receive minimum necessary permissions
3. **Fail Safe**: Security failures default to deny
4. **Auditability**: All actions are traceable and replayable
5. **Zero Trust**: No implicit trust based on network location

### Current Security Infrastructure

The existing codebase includes:

| Component | Location | Purpose |
|-----------|----------|---------|
| `SafetyLayer` | `src/core/safety.ts` | Constitutional constraints, kill switch, rollbacks |
| `GuardianAngelAgent` | `src/core/guardian/` | Real-time execution monitoring with veto power |
| `AuthenticationMiddleware` | `src/api/middleware.ts` | JWT-based authentication |
| `RateLimitMiddleware` | `src/api/middleware.ts` | Request rate limiting |
| `ValidationMiddleware` | `src/api/middleware.ts` | Input validation and sanitization |

---

## Authentication Schemas

### 2.1 JWT Token Schema

```typescript
interface JWTConfig {
  secret: string;              // HMAC secret (min 256 bits)
  algorithm: 'HS256' | 'HS384' | 'HS512' | 'RS256';
  accessTokenExpiry: number;   // Seconds (default: 3600)
  refreshTokenExpiry: number;  // Seconds (default: 604800)
  issuer: string;              // Token issuer identifier
  audience: string;            // Expected audience
}

interface TokenPair {
  accessToken: string;
  refreshToken: string;
  expiresAt: number;           // Unix timestamp
}

interface AccessTokenPayload {
  sub: string;                 // Gardener ID (subject)
  permissions: Permission[];   // Granted permissions
  type: 'access';              // Token type
  iat: number;                 // Issued at
  jti: string;                 // JWT ID (unique)
  exp: number;                 // Expiration
  iss: string;                 // Issuer
  aud: string;                 // Audience
}

interface RefreshTokenPayload {
  sub: string;                 // Gardener ID
  type: 'refresh';             // Token type
  jti: string;                 // JWT ID
  iat: number;                 // Issued at
  exp: number;                 // Expiration
}
```

### 2.2 API Token Schema (Legacy)

```typescript
interface APIToken {
  token: string;               // UUID v4 token
  gardenerId: string;          // Owner identifier
  permissions: Permission[];   // Granted permissions
  createdAt: number;           // Creation timestamp
  expiresAt: number;           // Expiration timestamp
  rateLimit: RateLimitConfig;  // Rate limiting config
}
```

### 2.3 Authentication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────>│  Auth API   │────>│  Token Store│
└─────────────┘     └─────────────┘     └─────────────┘
      │                   │                    │
      │ 1. Credentials    │                    │
      │                   │ 2. Validate        │
      │                   │                    │
      │                   │ 3. Generate Tokens │
      │<──────────────────│                    │
      │ 4. TokenPair      │                    │
      │                   │                    │
      │ 5. API Request    │                    │
      │──────────────────>│                    │
      │   + Access Token  │ 6. Validate Token  │
      │                   │───────────────────>│
      │                   │<───────────────────│
      │                   │ 7. Token Valid     │
      │<──────────────────│                    │
      │ 8. Response       │                    │
```

### 2.4 Token Refresh Flow

```typescript
// Token refresh invariant
interface TokenRefreshInvariant {
  // Old refresh token MUST be invalidated
  invalidateOldToken: boolean;  // ALWAYS true

  // New token pair MUST have new jti
  newJwtId: string;             // MUST be unique

  // Refresh MUST fail if token is revoked
  checkRevocation: boolean;     // ALWAYS true
}
```

---

## Authorization Models

### 3.1 Role-Based Access Control (RBAC)

```typescript
interface Role {
  id: string;
  name: string;
  description: string;
  permissions: Permission[];
  inherits?: string[];          // Role inheritance
}

interface Permission {
  resource: string;             // 'colony' | 'agent' | 'dream' | 'stats' | 'config'
  actions: string[];            // 'read' | 'write' | 'admin' | 'execute'
  constraints?: PermissionConstraint[];
}

interface PermissionConstraint {
  type: 'time' | 'rate' | 'resource' | 'colony';
  value: unknown;
}

// Predefined Roles
const ROLES = {
  ADMIN: {
    id: 'role:admin',
    name: 'Administrator',
    permissions: [
      { resource: '*', actions: ['*'] }
    ]
  },
  KEEPER: {
    id: 'role:keeper',
    name: 'Keeper',
    permissions: [
      { resource: 'colony', actions: ['read', 'write'] },
      { resource: 'agent', actions: ['read', 'write', 'execute'] },
      { resource: 'dream', actions: ['read', 'write'] },
      { resource: 'stats', actions: ['read'] }
    ]
  },
  OBSERVER: {
    id: 'role:observer',
    name: 'Observer',
    permissions: [
      { resource: 'colony', actions: ['read'] },
      { resource: 'agent', actions: ['read'] },
      { resource: 'stats', actions: ['read'] }
    ]
  }
};
```

### 3.2 Capability-Based Security (Agent Level)

```typescript
interface AgentCapability {
  id: string;
  agentId: string;
  capability: string;
  parameters: Record<string, unknown>;
  expiresAt?: number;
  delegatedFrom?: string;       // Capability delegation chain
  constraints: CapabilityConstraint[];
}

interface CapabilityConstraint {
  type: 'max_uses' | 'time_window' | 'resource_limit' | 'privacy_level';
  value: number | string;
}

// Capability Types
enum CapabilityType {
  SPAWN_AGENT = 'spawn_agent',
  KILL_AGENT = 'kill_agent',
  MODIFY_SYNAPSE = 'modify_synapse',
  ACCESS_PRIVATE_DATA = 'access_private_data',
  DREAM_CYCLE = 'dream_cycle',
  FEDERATED_SYNC = 'federated_sync',
  SHARE_POLLEN = 'share_pollen',
  MODIFY_CONSTRAINT = 'modify_constraint'
}
```

### 3.3 Resource Access Matrix

```typescript
// Resource: colony
interface ColonyAccess {
  read: ['admin', 'keeper', 'observer'];
  write: ['admin', 'keeper'];
  admin: ['admin'];
}

// Resource: agent
interface AgentAccess {
  read: ['admin', 'keeper', 'observer'];
  write: ['admin', 'keeper'];
  execute: ['admin', 'keeper'];
  kill: ['admin'];
}

// Resource: dream
interface DreamAccess {
  read: ['admin', 'keeper'];
  write: ['admin', 'keeper'];
  trigger: ['admin', 'keeper'];
}

// Resource: stats
interface StatsAccess {
  read: ['admin', 'keeper', 'observer'];
}

// Resource: config
interface ConfigAccess {
  read: ['admin', 'keeper'];
  write: ['admin'];
}
```

---

## Threat Model (STRIDE)

### 4.1 Spoofing

**Description**: Attacker impersonates legitimate user or agent.

| Threat Vector | Likelihood | Impact | Mitigation |
|--------------|------------|--------|------------|
| Stolen JWT token | Medium | High | Short expiry, token revocation, secure storage |
| Agent ID spoofing | Medium | High | Agent authentication, cryptographic signatures |
| WebSocket connection spoofing | Low | High | TLS, origin validation, authentication |

**Mitigation Schemas**:

```typescript
interface AntiSpoofingConfig {
  // Token security
  tokenBinding: boolean;        // Bind token to client certificate
  tokenRotation: number;        // Rotate tokens every N minutes
  tokenRevocationList: Set<string>;

  // Agent authentication
  agentSignatureRequired: boolean;
  agentKeyRotation: number;     // Key rotation interval

  // Connection security
  tlsRequired: boolean;
  originValidation: boolean;
  clientCertOptional: boolean;
}
```

### 4.2 Tampering

**Description**: Attacker modifies data in transit or at rest.

| Threat Vector | Likelihood | Impact | Mitigation |
|--------------|------------|--------|------------|
| A2A package tampering | Medium | High | Cryptographic signatures, hash chains |
| Payload injection | High | High | Input validation, sanitization |
| State corruption | Low | Critical | Checksums, state integrity checks |

**Mitigation Schemas**:

```typescript
interface TamperProtectionConfig {
  // A2A Package integrity
  packageSigning: boolean;
  signatureAlgorithm: 'RS256' | 'EdDSA';
  hashChainEnabled: boolean;

  // Input validation
  maxPayloadSize: number;       // 10MB default
  sanitizeStrings: boolean;
  validateJsonSchema: boolean;

  // State integrity
  stateChecksums: boolean;
  checkpointIntegrity: boolean;
}
```

### 4.3 Repudiation

**Description**: Attacker denies performing an action.

| Threat Vector | Likelihood | Impact | Mitigation |
|--------------|------------|--------|------------|
| Unlogged actions | Medium | Medium | Comprehensive audit logging |
| Deleted audit logs | Low | High | Immutable log storage, log forwarding |
| Causal chain breaks | Medium | High | Mandatory parent IDs, chain validation |

**Mitigation Schemas**:

```typescript
interface AuditConfig {
  // Logging requirements
  logAllActions: boolean;       // ALWAYS true
  logRetentionDays: number;     // 90 days minimum

  // Audit trail
  causalChainRequired: boolean; // ALWAYS true
  parentIdsRequired: boolean;   // ALWAYS true

  // Log integrity
  logSigning: boolean;
  logImmutability: boolean;
  logForwarding: string[];      // External log destinations
}
```

### 4.4 Information Disclosure

**Description**: Attacker gains access to sensitive data.

| Threat Vector | Likelihood | Impact | Mitigation |
|--------------|------------|--------|------------|
| PII in payloads | High | High | PII detection, encryption |
| Sensitive data exposure | Medium | Critical | Privacy levels, access controls |
| KV cache data leakage | Medium | High | Encryption at rest, access logging |

**Mitigation Schemas**:

```typescript
interface DataProtectionConfig {
  // PII protection
  piiDetectionEnabled: boolean;
  piiPatterns: RegExp[];
  piiAction: 'block' | 'redact' | 'encrypt';

  // Privacy levels
  privacyLevels: {
    PUBLIC: { encryptAtRest: false; encryptInTransit: true; };
    COLONY: { encryptAtRest: true; encryptInTransit: true; };
    PRIVATE: { encryptAtRest: true; encryptInTransit: true; accessLogging: true; };
  };

  // Data retention
  maxRetentionDays: number;
  autoDelete: boolean;
}
```

### 4.5 Denial of Service

**Description**: Attacker disrupts service availability.

| Threat Vector | Likelihood | Impact | Mitigation |
|--------------|------------|--------|------------|
| Rate limit bypass | Medium | High | Multi-level rate limiting |
| Resource exhaustion | Medium | High | Resource quotas, memory limits |
| Agent spawn flood | Medium | Medium | Spawn rate limits, agent quotas |

**Mitigation Schemas**:

```typescript
interface DoSProtectionConfig {
  // Rate limiting
  globalRateLimit: number;      // 1000 req/min
  perUserRateLimit: number;     // 100 req/min
  perAgentRateLimit: number;    // 60 req/min
  burstLimit: number;           // 10 burst

  // Resource limits
  maxAgentsPerColony: number;   // 1000
  maxMemoryPerAgent: number;    // 4096 MB
  maxCpuPerAgent: number;       // 10000 ms

  // Spawn protection
  spawnRateLimit: number;       // 10 spawns/min
  agentQuota: number;           // Per gardener quota
}
```

### 4.6 Elevation of Privilege

**Description**: Attacker gains unauthorized access or capabilities.

| Threat Vector | Likelihood | Impact | Mitigation |
|--------------|------------|--------|------------|
| Permission bypass | Low | Critical | Strict permission checks |
| Role escalation | Low | Critical | Role validation, no self-promotion |
| Constraint override | Medium | Critical | Non-overridable constraints |

**Mitigation Schemas**:

```typescript
interface PrivilegeProtectionConfig {
  // Permission enforcement
  strictPermissionCheck: boolean;  // ALWAYS true
  permissionCache: boolean;
  permissionCacheTTL: number;      // 5 minutes

  // Role protection
  noSelfPromotion: boolean;        // ALWAYS true
  roleChangeRequiresAdmin: boolean;

  // Constraint protection
  nonOverridableConstraints: Set<string>;
  overrideRequiresAudit: boolean;
  overrideRateLimit: number;       // 5 per day
}
```

---

## Security Invariants

### 5.1 Authentication Invariants

```typescript
// INVARIANT: No anonymous access to protected resources
const INV_NO_ANONYMOUS_ACCESS = {
  id: 'AUTH-001',
  description: 'All protected resources require valid authentication',
  enforcement: 'mandatory',
  check: (request: Request) => !!request.auth
};

// INVARIANT: Tokens expire
const INV_TOKEN_EXPIRY = {
  id: 'AUTH-002',
  description: 'All tokens have finite lifetime',
  enforcement: 'mandatory',
  check: (token: Token) => token.expiresAt > Date.now() && token.expiresAt < Infinity
};

// INVARIANT: Refresh tokens are single-use
const INV_REFRESH_SINGLE_USE = {
  id: 'AUTH-003',
  description: 'Refresh tokens can only be used once',
  enforcement: 'mandatory',
  check: (refreshToken: string) => !usedRefreshTokens.has(refreshToken)
};
```

### 5.2 Authorization Invariants

```typescript
// INVARIANT: Default deny
const INV_DEFAULT_DENY = {
  id: 'AUTHZ-001',
  description: 'Access is denied unless explicitly granted',
  enforcement: 'mandatory',
  check: (permission: Permission, resource: string) =>
    permission.resource === resource || permission.resource === '*'
};

// INVARIANT: Least privilege
const INV_LEAST_PRIVILEGE = {
  id: 'AUTHZ-002',
  description: 'Agents receive minimum necessary permissions',
  enforcement: 'recommended',
  check: (agent: Agent, permissions: Permission[]) =>
    permissions.every(p => agent.requiredPermissions.includes(p))
};

// INVARIANT: No privilege escalation
const INV_NO_ESCALATION = {
  id: 'AUTHZ-003',
  description: 'Agents cannot grant themselves more privileges',
  enforcement: 'mandatory',
  check: (modifier: Agent, target: Agent, newPermissions: Permission[]) =>
    !newPermissions.some(p => !modifier.permissions.includes(p))
};
```

### 5.3 Data Integrity Invariants

```typescript
// INVARIANT: Causal chain continuity
const INV_CAUSAL_CHAIN = {
  id: 'DATA-001',
  description: 'All A2A packages have valid parent references',
  enforcement: 'mandatory',
  check: (pkg: A2APackage) =>
    pkg.parentIds.every(id => packageStore.has(id)) || pkg.parentIds.length === 0
};

// INVARIANT: Payload integrity
const INV_PAYLOAD_INTEGRITY = {
  id: 'DATA-002',
  description: 'Payloads must pass validation before processing',
  enforcement: 'mandatory',
  check: (payload: unknown) => validatePayload(payload)
};

// INVARIANT: State consistency
const INV_STATE_CONSISTENCY = {
  id: 'DATA-003',
  description: 'State transitions must be atomic and consistent',
  enforcement: 'mandatory',
  check: (beforeState: State, afterState: State) =>
    validateStateTransition(beforeState, afterState)
};
```

### 5.4 Safety Invariants

```typescript
// INVARIANT: Kill switch works
const INV_KILL_SWITCH = {
  id: 'SAFE-001',
  description: 'Kill switch immediately halts all operations',
  enforcement: 'mandatory',
  check: () => killSwitchResponseTime < 5000 // 5 seconds
};

// INVARIANT: Critical constraints cannot be overridden
const INV_NO_OVERRIDE_CRITICAL = {
  id: 'SAFE-002',
  description: 'Critical severity constraints are never overridable',
  enforcement: 'mandatory',
  check: (constraint: Constraint) =>
    constraint.severity !== 'CRITICAL' || constraint.cannotOverride === true
};

// INVARIANT: Rollback capability
const INV_ROLLBACK = {
  id: 'SAFE-003',
  description: 'System can rollback to last known good state',
  enforcement: 'mandatory',
  check: () => checkpoints.length > 0
};
```

### 5.5 Privacy Invariants

```typescript
// INVARIANT: Privacy level enforcement
const INV_PRIVACY_LEVEL = {
  id: 'PRIV-001',
  description: 'Data access respects privacy level classification',
  enforcement: 'mandatory',
  check: (data: Data, accessor: Agent) =>
    data.privacyLevel === 'PUBLIC' ||
    (data.privacyLevel === 'COLONY' && accessor.colonyId === data.colonyId) ||
    (data.privacyLevel === 'PRIVATE' && accessor.id === data.ownerId)
};

// INVARIANT: PII protection
const INV_PII_PROTECTION = {
  id: 'PRIV-002',
  description: 'PII is detected and blocked or encrypted',
  enforcement: 'mandatory',
  check: (payload: unknown) =>
    !containsPII(payload) || isEncrypted(payload)
};

// INVARIANT: Differential privacy
const INV_DIFFERENTIAL_PRIVACY = {
  id: 'PRIV-003',
  description: 'Shared patterns include differential privacy metadata',
  enforcement: 'recommended',
  check: (pollenGrain: PollenGrain) =>
    !pollenGrain.metadata.isPrivate ||
    pollenGrain.metadata.differentialPrivacyEpsilon !== undefined
};
```

---

## Audit Event Schemas

### 6.1 Core Audit Event

```typescript
interface AuditEvent {
  // Identification
  id: string;                   // UUID v4
  timestamp: number;            // Unix timestamp (ms)
  version: string;              // Schema version

  // Classification
  category: AuditCategory;
  severity: SafetySeverity;
  type: AuditEventType;

  // Context
  gardenerId?: string;
  colonyId?: string;
  agentId?: string;
  sessionId?: string;

  // Action
  action: string;
  resource: string;
  resourceId?: string;

  // Result
  outcome: 'success' | 'failure' | 'denied' | 'error';
  message: string;
  details?: Record<string, unknown>;

  // Traceability
  causalChainId?: string;
  parentEventIds?: string[];

  // Security
  sourceIp?: string;
  userAgent?: string;

  // Compliance
  piiInvolved: boolean;
  retentionUntil?: number;
}

enum AuditCategory {
  AUTHENTICATION = 'authentication',
  AUTHORIZATION = 'authorization',
  DATA_ACCESS = 'data_access',
  DATA_MODIFICATION = 'data_modification',
  AGENT_LIFECYCLE = 'agent_lifecycle',
  COLONY_LIFECYCLE = 'colony_lifecycle',
  SAFETY = 'safety',
  COMPLIANCE = 'compliance',
  SYSTEM = 'system'
}

enum AuditEventType {
  // Authentication
  LOGIN_SUCCESS = 'login_success',
  LOGIN_FAILURE = 'login_failure',
  LOGOUT = 'logout',
  TOKEN_REFRESH = 'token_refresh',
  TOKEN_REVOKED = 'token_revoked',

  // Authorization
  ACCESS_GRANTED = 'access_granted',
  ACCESS_DENIED = 'access_denied',
  PERMISSION_CHANGE = 'permission_change',
  ROLE_CHANGE = 'role_change',

  // Agent
  AGENT_SPAWNED = 'agent_spawned',
  AGENT_KILLED = 'agent_killed',
  AGENT_ACTIVATED = 'agent_activated',
  AGENT_DEACTIVATED = 'agent_deactivated',
  AGENT_EXECUTED = 'agent_executed',

  // Safety
  CONSTRAINT_VIOLATION = 'constraint_violation',
  KILL_SWITCH_TRIGGERED = 'kill_switch_triggered',
  ROLLBACK_PERFORMED = 'rollback_performed',
  SAFE_MODE_ENABLED = 'safe_mode_enabled',

  // Guardian
  GUARDIAN_REVIEW = 'guardian_review',
  GUARDIAN_VETO = 'guardian_veto',
  GUARDIAN_OVERRIDE = 'guardian_override'
}
```

### 6.2 Specialized Audit Events

```typescript
// Guardian Review Event
interface GuardianAuditEvent extends AuditEvent {
  category: AuditCategory.SAFETY;
  type: AuditEventType.GUARDIAN_REVIEW;

  details: {
    proposalId: string;
    decision: 'ALLOW' | 'MODIFY' | 'VETO';
    confidence: number;
    constraintResults: Array<{
      constraintId: string;
      passed: boolean;
      reason: string;
    }>;
    reviewTimeMs: number;
    overridden: boolean;
  };
}

// Data Access Event
interface DataAccessAuditEvent extends AuditEvent {
  category: AuditCategory.DATA_ACCESS;

  details: {
    resourceType: string;
    resourceId: string;
    accessType: 'read' | 'write' | 'delete';
    privacyLevel: PrivacyLevel;
    containsPII: boolean;
    encryptionUsed: boolean;
  };
}

// A2A Package Event
interface A2AAuditEvent extends AuditEvent {
  category: AuditCategory.SYSTEM;

  details: {
    packageId: string;
    senderId: string;
    receiverId: string;
    packageType: string;
    parentIds: string[];
    causalChainId: string;
    privacyLevel: PrivacyLevel;
    signed: boolean;
  };
}
```

### 6.3 Audit Log Storage Schema

```typescript
interface AuditLogConfig {
  // Storage
  backend: 'file' | 'database' | 'syslog' | 'elasticsearch';
  connectionString: string;

  // Retention
  retentionDays: number;        // 90 days minimum
  archiveAfterDays: number;     // 30 days
  compressArchives: boolean;

  // Integrity
  signLogs: boolean;
  signAlgorithm: 'RS256' | 'HS256';
  immutableStorage: boolean;

  // Performance
  batchSize: number;            // 100 events
  flushIntervalMs: number;      // 5000ms

  // Forwarding
  forwardTo: Array<{
    destination: string;
    format: 'json' | 'cef' | 'syslog';
    filters?: AuditFilter[];
  }>;
}
```

---

## Encryption Patterns

### 7.1 Data Classification and Encryption

```typescript
interface EncryptionPolicy {
  classification: DataClassification;
  atRest: EncryptionConfig;
  inTransit: EncryptionConfig;
  inMemory: EncryptionConfig;
}

interface EncryptionConfig {
  enabled: boolean;
  algorithm: string;
  keyLength: number;
  keyRotationDays: number;
}

enum DataClassification {
  PUBLIC = 'public',
  INTERNAL = 'internal',
  CONFIDENTIAL = 'confidential',
  RESTRICTED = 'restricted'
}

// Default policies
const ENCRYPTION_POLICIES: Record<DataClassification, EncryptionPolicy> = {
  PUBLIC: {
    classification: DataClassification.PUBLIC,
    atRest: { enabled: false, algorithm: 'none', keyLength: 0, keyRotationDays: 0 },
    inTransit: { enabled: true, algorithm: 'TLS1.3', keyLength: 256, keyRotationDays: 0 },
    inMemory: { enabled: false, algorithm: 'none', keyLength: 0, keyRotationDays: 0 }
  },
  INTERNAL: {
    classification: DataClassification.INTERNAL,
    atRest: { enabled: true, algorithm: 'AES-256-GCM', keyLength: 256, keyRotationDays: 90 },
    inTransit: { enabled: true, algorithm: 'TLS1.3', keyLength: 256, keyRotationDays: 0 },
    inMemory: { enabled: false, algorithm: 'none', keyLength: 0, keyRotationDays: 0 }
  },
  CONFIDENTIAL: {
    classification: DataClassification.CONFIDENTIAL,
    atRest: { enabled: true, algorithm: 'AES-256-GCM', keyLength: 256, keyRotationDays: 30 },
    inTransit: { enabled: true, algorithm: 'TLS1.3', keyLength: 256, keyRotationDays: 0 },
    inMemory: { enabled: true, algorithm: 'AES-256-GCM', keyLength: 256, keyRotationDays: 30 }
  },
  RESTRICTED: {
    classification: DataClassification.RESTRICTED,
    atRest: { enabled: true, algorithm: 'AES-256-GCM', keyLength: 256, keyRotationDays: 7 },
    inTransit: { enabled: true, algorithm: 'TLS1.3', keyLength: 256, keyRotationDays: 0 },
    inMemory: { enabled: true, algorithm: 'AES-256-GCM', keyLength: 256, keyRotationDays: 7 }
  }
};
```

### 7.2 Key Management Schema

```typescript
interface KeyManagementConfig {
  // Key derivation
  kdf: 'PBKDF2' | 'Argon2' | 'scrypt';
  kdfIterations: number;
  saltLength: number;

  // Key storage
  keyStorage: 'hsm' | 'vault' | 'kms' | 'file';
  keyEncryptionKey: boolean;    // Encrypt keys at rest

  // Key lifecycle
  maxKeyAge: number;            // Days
  maxKeyUses: number;
  autoRotate: boolean;

  // Key access
  keyAccessLogging: boolean;
  keyAccessRateLimit: number;
}

interface EncryptedData {
  ciphertext: string;           // Base64 encoded
  iv: string;                   // Initialization vector
  authTag?: string;             // Authentication tag (GCM)
  keyId: string;                // Key identifier
  algorithm: string;
  version: number;
  encryptedAt: number;
}
```

### 7.3 Secure Communication Schema

```typescript
interface SecureCommConfig {
  // TLS configuration
  tlsMinVersion: 'TLS1.2' | 'TLS1.3';
  cipherSuites: string[];
  certificateValidation: boolean;

  // WebSocket security
  wsMaxFrameSize: number;       // 1MB
  wsMaxMessageSize: number;     // 10MB
  wsCompression: boolean;

  // Message security
  messageSigning: boolean;
  signatureAlgorithm: 'RS256' | 'EdDSA';
  messageEncryption: boolean;

  // Connection security
  connectionTimeout: number;    // 30000ms
  heartbeatInterval: number;    // 30000ms
  maxConnectionsPerIp: number;  // 10
}
```

---

## Security Constraint Categories

### 8.1 Constraint Hierarchy

```
CRITICAL (cannot override)
  |
  +-- Harm Prevention
  +-- Action Blacklist
  +-- Injection Prevention
  |
HIGH (requires admin override)
  |
  +-- Resource Limits
  +-- Privacy Protection
  +-- Network Access
  |
MEDIUM (requires audit)
  |
  +-- Rate Limiting
  +-- Audit Trail
  +-- Data Retention
  |
LOW (log only)
  |
  +-- Output Format
  +-- Transparency
```

### 8.2 Built-in Constraints

| Constraint ID | Category | Severity | Override |
|--------------|----------|----------|----------|
| `memory_limit` | resource_limits | HIGH | Admin |
| `cpu_limit` | resource_limits | HIGH | Admin |
| `execution_duration` | resource_limits | HIGH | Admin |
| `action_whitelist` | action_control | CRITICAL | No |
| `action_blacklist` | action_control | CRITICAL | No |
| `file_operation` | action_control | HIGH | Admin |
| `agent_rate_limit` | rate_limiting | MEDIUM | Audit |
| `global_rate_limit` | rate_limiting | HIGH | Admin |
| `pii_detection` | privacy_protection | HIGH | Admin |
| `sensitive_data` | privacy_protection | HIGH | Admin |
| `privacy_level` | privacy_protection | MEDIUM | Audit |
| `harm_prevention` | ethical_guidelines | CRITICAL | No |
| `bias_detection` | ethical_guidelines | MEDIUM | Audit |
| `transparency` | ethical_guidelines | LOW | Log |
| `output_size` | output_validation | MEDIUM | Audit |
| `output_format` | output_validation | LOW | Log |
| `malicious_content` | output_validation | CRITICAL | No |
| `injection_attack` | security | CRITICAL | No |
| `network_access` | security | HIGH | Admin |
| `audit_trail` | compliance | MEDIUM | Audit |
| `data_retention` | compliance | LOW | Log |

---

## Appendix A: Security Checklist

### A.1 Implementation Checklist

- [ ] All API endpoints require authentication
- [ ] JWT tokens have appropriate expiry times
- [ ] Refresh tokens are single-use and revocable
- [ ] Rate limiting is enabled at all levels
- [ ] Input validation on all user-provided data
- [ ] Output encoding to prevent injection
- [ ] All A2A packages have causal chain references
- [ ] Guardian constraints are properly configured
- [ ] Kill switch is tested and functional
- [ ] Audit logging is comprehensive
- [ ] Encryption at rest for sensitive data
- [ ] TLS for all network communication
- [ ] Key management is properly implemented

### A.2 Deployment Checklist

- [ ] JWT_SECRET is strong (256+ bits)
- [ ] TLS certificates are valid and not expired
- [ ] Rate limits are appropriate for production load
- [ ] Audit logs are forwarded to secure storage
- [ ] HSM or Vault is configured for key storage
- [ ] Firewall rules restrict access appropriately
- [ ] Monitoring and alerting for security events
- [ ] Incident response plan is documented

---

*Document maintained by: POLLN Security Architecture Team*
*Next review: 2026-Q2*
