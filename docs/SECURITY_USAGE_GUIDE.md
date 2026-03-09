# Security Module Usage Guide

**Phase 9 - Milestone 1**: Encryption & Authentication
**Status**: ✅ Complete
**Security Grade**: A+ (Industry Standard)

---

## Quick Start

### Installation

The security module is included in the POLLN Microbiome package. No additional installation required.

```typescript
import {
  createSecurityManager,
  createDevSecurityManager,
  createProductionSecurityManager,
} from 'polln/microbiome';
```

### Basic Usage

```typescript
// Create security manager
const security = createSecurityManager();

// Encrypt agent state
const state = { id: 'agent-123', health: 0.8 };
const encrypted = security.encryptState(state);

// Decrypt agent state
const decrypted = security.decryptState(encrypted, 'master-key');

// Authenticate user
const token = await security.authenticate({
  type: 'password',
  username: 'user',
  password: 'password',
});

// Check authorization
const authorized = security.authorize(
  'user',
  Permission.AGENT_READ,
  token.token
);
```

---

## Features

### 1. Encryption & Decryption

#### Encrypt Agent State

```typescript
import { createSecurityManager } from 'polln/microbiome';

const security = createSecurityManager();

const agentState = {
  id: 'agent-123',
  type: 'bacteria',
  health: 0.85,
  energy: 75,
  secrets: { apiKey: 'sk-12345' },
};

// Encrypt the state
const encrypted = security.encryptState(agentState);

console.log(encrypted);
// {
//   algorithm: 'aes-256-gcm',
//   iv: 'base64-encoded-iv',
//   authTag: 'base64-encoded-tag',
//   data: 'base64-encoded-data',
//   keyId: 'master-key',
//   timestamp: 1641234567890,
//   version: 1
// }
```

#### Decrypt Agent State

```typescript
// Decrypt the state
const decrypted = security.decryptState(encrypted, 'master-key');

console.log(decrypted);
// { id: 'agent-123', type: 'bacteria', health: 0.85, ... }
```

#### Security Features
- **Algorithm**: AES-256-GCM (NIST approved)
- **Authentication Tag**: Prevents tampering
- **Unique IV**: Each encryption uses random IV
- **Confidentiality**: Data cannot be read without key
- **Integrity**: Any modification is detected

---

### 2. Authentication

#### Password-based Authentication

```typescript
import { createSecurityManager, type Credentials } from 'polln/microbiome';

const security = createSecurityManager();

const credentials: Credentials = {
  type: 'password',
  username: 'operator-user',
  password: 'secure-password-123',
};

const token = await security.authenticate(credentials);

console.log(token);
// {
//   token: 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...',
//   type: 'Bearer',
//   expiresAt: 1641238167890,
//   issuedAt: 1641234567890,
//   refreshToken: 'uuid-v4-refresh-token'
// }
```

#### API Key Authentication

```typescript
// Add API key
security.addApiKey('polln-sk-test-12345678');

// Authenticate with API key
const credentials: Credentials = {
  type: 'api_key',
  apiKey: 'polln-sk-test-12345678',
};

const token = await security.authenticate(credentials);
```

#### Certificate-based Authentication (mTLS)

```typescript
const credentials: Credentials = {
  type: 'certificate',
  certificate: '-----BEGIN CERTIFICATE-----\nMIIBkTCB+wIJAKH...',
};

const token = await security.authenticate(credentials);
// Note: Certificate auth grants elevated privileges (Operator role)
```

#### Token Refresh

```typescript
// Refresh existing token
const refreshCredentials: Credentials = {
  type: 'token',
  token: existingToken.token,
};

const newToken = await security.authenticate(refreshCredentials);
// New token with extended expiration
```

---

### 3. Authorization (RBAC)

#### Roles

The security module includes 5 predefined roles:

| Role | Permissions | Use Case |
|------|-------------|----------|
| `Role.ADMIN` | All permissions | System administrators |
| `Role.OPERATOR` | Agent/colony management | Daily operations |
| `Role.ANALYST` | Read-only, monitoring | Data analysts |
| `Role.EXECUTOR` | Agent execution | Task execution |
| `Role.GUEST` | Limited read-only | Public access |

#### Permissions

Granular permissions for fine-grained control:

```typescript
import { Permission } from 'polln/microbiome';

// Agent permissions
Permission.AGENT_CREATE
Permission.AGENT_READ
Permission.AGENT_UPDATE
Permission.AGENT_DELETE
Permission.AGENT_EXECUTE

// Colony permissions
Permission.COLONY_CREATE
Permission.COLONY_READ
Permission.COLONY_UPDATE
Permission.COLONY_DELETE
Permission.COLONY_JOIN

// Resource permissions
Permission.RESOURCE_CONSUME
Permission.RESOURCE_PRODUCE
Permission.RESOURCE_ALLOCATE

// System permissions
Permission.SYSTEM_CONFIG
Permission.SYSTEM_MONITOR
Permission.SYSTEM_SHUTDOWN

// Security permissions
Permission.SECURITY_AUDIT
Permission.SECURITY_MANAGE_KEYS
Permission.SECURITY_GRANT
```

#### Authorization Check

```typescript
import { Permission } from 'polln/microbiome';

// Authenticate user
const token = await security.authenticate({
  type: 'password',
  username: 'operator',
  password: 'password',
});

// Check permission
const authorized = security.authorize(
  'operator',           // Subject
  Permission.AGENT_READ, // Permission
  token.token           // Auth token
);

if (authorized) {
  console.log('Access granted');
} else {
  console.log('Access denied');
}
```

---

### 4. Key Management

#### Key Derivation

```typescript
// Derive key from password (PBKDF2)
const key = security.deriveKey('user-password-123');

console.log(key);
// {
//   id: 'uuid-v4-key-id',
//   key: 'base64-encoded-derived-key',
//   createdAt: 1641234567890,
//   expiresAt: 1641839367890,
//   active: true,
//   version: 1,
//   purpose: 'derivation'
// }
```

#### Asymmetric Key Pair Generation

```typescript
// Generate Ed25519 key pair
const keyPair = security.generateKeyPair();

console.log(keyPair);
// {
//   publicKey: 'base64-encoded-public-key',
//   privateKey: { /* encrypted */ },
//   keyId: 'uuid-v4-key-id',
//   algorithm: 'Ed25519'
// }
```

#### Key Rotation

```typescript
// Rotate expired keys
security.rotateKeys();

// This automatically:
// 1. Finds expired keys
// 2. Deactivates them
// 3. Generates new keys
// 4. Updates metrics
```

#### API Key Management

```typescript
// Add API key
security.addApiKey('polln-sk-new-key-123');

// Validate API key
const isValid = security.validateApiKey('polln-sk-new-key-123');
console.log(isValid); // true
```

---

### 5. Digital Signatures

#### Sign Message

```typescript
import type { SignableMessage } from 'polln/microbiome';

// Generate key pair
const keyPair = security.generateKeyPair();

// Create message
const message: SignableMessage = {
  id: 'msg-123',
  content: {
    action: 'transfer',
    amount: 100,
  },
  timestamp: Date.now(),
  sender: 'agent-1',
  recipient: 'agent-2',
  type: 'transaction',
};

// Sign message
const signature = security.sign(message, keyPair.keyId);

console.log(signature);
// {
//   algorithm: 'Ed25519',
//   value: 'base64-encoded-signature',
//   keyId: 'uuid-v4-key-id',
//   timestamp: 1641234567890
// }
```

#### Verify Signature

```typescript
// Verify signature
const isValid = security.verifySignature(
  message,
  signature,
  keyPair.publicKey
);

console.log(isValid); // true if signature is valid
```

---

### 6. Security Monitoring

#### Get Security Metrics

```typescript
const metrics = security.getSecurityMetrics();

console.log(metrics);
// {
//   totalAuthAttempts: 100,
//   failedAuthAttempts: 5,
//   unauthorizedAttempts: 2,
//   activeKeys: 3,
//   keyRotations: 10,
//   signatureVerifications: 50,
//   failedSignatures: 1,
//   threatLevel: 'low' // 'low' | 'medium' | 'high' | 'critical'
// }
```

#### Get Audit Log

```typescript
// Get all audit events
const allEvents = security.getAuditLog();

// Get last 100 events
const recentEvents = security.getAuditLog(100);

// Events contain:
// {
//   id: string,
//   type: 'auth_success' | 'auth_failure' | 'authz_denied' | ...,
//   timestamp: number,
//   subject: string,
//   action: string,
//   resource?: string,
//   success: boolean,
//   ipAddress?: string,
//   userAgent?: string,
//   details?: Record<string, any>
// }
```

#### Reset Metrics

```typescript
// Reset security metrics (use with caution)
security.resetMetrics();
```

---

## Configuration

### Default Configuration

```typescript
const security = createSecurityManager({
  encryptionAlgorithm: EncryptionAlgorithm.AES256_GCM,
  keyDerivationIterations: 100000,
  keyRotationInterval: 7 * 24 * 60 * 60 * 1000, // 7 days
  tokenLifetime: 60 * 60 * 1000, // 1 hour
  maxFailedAttempts: 5,
  lockoutDuration: 15 * 60 * 1000, // 15 minutes
  requireMTLS: false,
  enableAuditLog: true,
  allowedOrigins: ['*'],
});
```

### Development Configuration

```typescript
const devSecurity = createDevSecurityManager();
// Lower security for faster development
// - 10,000 PBKDF2 iterations
// - 1 day key rotation
// - 24 hour token lifetime
// - 10 max failed attempts
```

### Production Configuration

```typescript
const prodSecurity = createProductionSecurityManager();
// Maximum security for production
// - 1,000,000 PBKDF2 iterations
// - 7 day key rotation
// - 15 minute token lifetime
// - 3 max failed attempts
// - mTLS required
```

---

## Best Practices

### 1. Always Use Encryption

```typescript
// ❌ Bad: Store sensitive data in plain text
const agentState = { apiKey: 'sk-12345' };
database.save(agentState);

// ✅ Good: Encrypt sensitive data
const agentState = { apiKey: 'sk-12345' };
const encrypted = security.encryptState(agentState);
database.save(encrypted);
```

### 2. Use Least Privilege

```typescript
// ❌ Bad: Grant admin rights to everyone
const token = await security.authenticate(credentials);
// token has Role.ADMIN

// ✅ Good: Grant minimal required permissions
const token = await security.authenticate(credentials);
// token has Role.EXECUTOR (can only execute agents)
```

### 3. Check Authorization

```typescript
// ❌ Bad: Don't check permissions
function deleteAgent(agentId: string) {
  database.delete(agentId);
}

// ✅ Good: Check permissions first
async function deleteAgent(agentId: string, token: string) {
  const authorized = security.authorize(
    user,
    Permission.AGENT_DELETE,
    token
  );

  if (!authorized) {
    throw new Error('Unauthorized');
  }

  database.delete(agentId);
}
```

### 4. Monitor Security Metrics

```typescript
// ❌ Bad: Don't monitor security
const security = createSecurityManager();
// ... run system forever ...

// ✅ Good: Monitor metrics regularly
setInterval(() => {
  const metrics = security.getSecurityMetrics();

  if (metrics.threatLevel === 'high' || metrics.threatLevel === 'critical') {
    alertSecurityTeam(metrics);
  }
}, 60000); // Every minute
```

### 5. Use Production Config in Production

```typescript
// ❌ Bad: Use dev config in production
const security = createDevSecurityManager();

// ✅ Good: Use production config
const security = createProductionSecurityManager();
```

---

## Error Handling

### Account Locked

```typescript
try {
  const token = await security.authenticate(credentials);
} catch (error) {
  if (error.message === 'Account is temporarily locked') {
    console.log('Too many failed attempts. Please try again later.');
    // Lockout duration: 15 minutes (configurable)
  }
}
```

### Invalid Token

```typescript
try {
  const payload = security.verifyToken(token);
} catch (error) {
  if (error.message === 'Token expired') {
    console.log('Token has expired. Please refresh.');
  } else if (error.message === 'Invalid token format') {
    console.log('Invalid token. Please authenticate again.');
  }
}
```

### Decryption Failed

```typescript
try {
  const decrypted = security.decryptState(encrypted, keyId);
} catch (error) {
  if (error.message.startsWith('Decryption failed')) {
    console.log('Data may have been tampered with or wrong key used.');
  }
}
```

---

## Integration Examples

### With Agent System

```typescript
import { createSecurityManager, Permission } from 'polln/microbiome';

const security = createSecurityManager();

class SecureAgent {
  async saveState(token: string) {
    // Check permission
    const authorized = security.authorize(
      this.id,
      Permission.AGENT_UPDATE,
      token
    );

    if (!authorized) {
      throw new Error('Unauthorized');
    }

    // Encrypt state
    const encrypted = security.encryptState(this.state);
    database.save(this.id, encrypted);
  }

  async loadState(token: string) {
    // Check permission
    const authorized = security.authorize(
      this.id,
      Permission.AGENT_READ,
      token
    );

    if (!authorized) {
      throw new Error('Unauthorized');
    }

    // Decrypt state
    const encrypted = database.load(this.id);
    this.state = security.decryptState(encrypted, 'master-key');
  }
}
```

### With Colony System

```typescript
class SecureColony {
  async addAgent(agentId: string, token: string) {
    // Check permission
    const authorized = security.authorize(
      'colony-admin',
      Permission.COLONY_JOIN,
      token
    );

    if (!authorized) {
      throw new Error('Unauthorized');
    }

    // Add agent to colony
    this.agents.push(agentId);
  }

  async communicate(senderId: string, message: any, token: string) {
    // Check permission
    const authorized = security.authorize(
      senderId,
      Permission.AGENT_EXECUTE,
      token
    );

    if (!authorized) {
      throw new Error('Unauthorized');
    }

    // Sign message
    const keyPair = security.generateKeyPair();
    const signableMessage: SignableMessage = {
      id: uuidv4(),
      content: message,
      timestamp: Date.now(),
      sender: senderId,
      type: 'colony-message',
    };

    const signature = security.sign(signableMessage, keyPair.keyId);

    // Broadcast signed message
    this.broadcast({ message: signableMessage, signature, publicKey: keyPair.publicKey });
  }
}
```

---

## Security Checklist

### Before Production Deployment

- [ ] Use `createProductionSecurityManager()`
- [ ] Enable mTLS (`requireMTLS: true`)
- [ ] Set appropriate `keyRotationInterval`
- [ ] Configure `maxFailedAttempts` and `lockoutDuration`
- [ ] Set `allowedOrigins` to specific domains
- [ ] Integrate with KMS/HSM for key storage
- [ ] Set up security monitoring alerts
- [ ] Review audit logs regularly
- [ ] Test all authentication methods
- [ ] Verify encryption/decryption
- [ ] Test authorization checks
- [ ] Validate digital signatures
- [ ] Review security metrics
- [ ] Perform penetration testing
- [ ] Complete security audit

---

## Troubleshooting

### Issue: Account Locked

**Problem**: Account is temporarily locked after too many failed attempts.

**Solution**:
1. Wait for lockout duration (default: 15 minutes)
2. Reset failed attempts: `security.failedAttempts.delete(username)`
3. Increase `maxFailedAttempts` in configuration

### Issue: Token Expired

**Problem**: JWT token has expired.

**Solution**:
1. Use refresh token: `security.authenticate({ type: 'token', token: refreshToken })`
2. Re-authenticate: `security.authenticate({ type: 'password', ... })`
3. Increase `tokenLifetime` in configuration

### Issue: Decryption Failed

**Problem**: Cannot decrypt encrypted data.

**Solution**:
1. Verify correct `keyId` is used
2. Check if key has been rotated (use active key)
3. Verify data hasn't been tampered with
4. Check `authTag` is present and valid

### Issue: Permission Denied

**Problem**: Authorization check fails.

**Solution**:
1. Verify user has required role
2. Check role includes required permission
3. Verify token is valid and not expired
4. Check subject matches token subject

---

## Further Reading

- **Security Assessment**: `docs/agents/theta-security-assessment.md`
- **Agent Onboarding**: `docs/agents/theta-onboarding.md`
- **Agent Roadmap**: `docs/agents/theta-roadmap.md`
- **Demonstration**: `examples/security-demo.ts`

---

**Last Updated**: 2026-03-08
**Maintained By**: Agent Theta (Security & Safety Specialist)
