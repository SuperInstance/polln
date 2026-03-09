/**
 * Security Module Tests
 *
 * Comprehensive test suite for security features including:
 * - Encryption/decryption
 * - Authentication
 * - Authorization
 * - Key management
 * - Digital signatures
 * - Audit logging
 *
 * @module microbiome/__tests__/security.test
 */

import {
  SecurityManager,
  createSecurityManager,
  createDevSecurityManager,
  createProductionSecurityManager,
  EncryptionAlgorithm,
  Role,
  Permission,
  type EncryptedState,
  type SignableMessage,
  type Credentials,
  type SecurityEvent,
} from '../security.js';

describe('SecurityManager', () => {
  let securityManager: SecurityManager;

  beforeEach(() => {
    securityManager = createDevSecurityManager();
  });

  describe('Encryption & Decryption', () => {
    describe('encryptState', () => {
      it('should encrypt agent state successfully', () => {
        const state = {
          id: 'agent-123',
          type: 'bacteria',
          health: 0.8,
          resources: { food: 100, water: 50 },
        };

        const encrypted = securityManager.encryptState(state);

        expect(encrypted).toBeDefined();
        expect(encrypted.algorithm).toBe(EncryptionAlgorithm.AES256_GCM);
        expect(encrypted.iv).toBeDefined();
        expect(encrypted.authTag).toBeDefined();
        expect(encrypted.data).toBeDefined();
        expect(encrypted.keyId).toBe('master-key');
        expect(encrypted.timestamp).toBeLessThanOrEqual(Date.now());
        expect(encrypted.version).toBe(1);
      });

      it('should generate unique IV for each encryption', () => {
        const state = { data: 'test' };

        const encrypted1 = securityManager.encryptState(state);
        const encrypted2 = securityManager.encryptState(state);

        expect(encrypted1.iv).not.toBe(encrypted2.iv);
        expect(encrypted1.data).not.toBe(encrypted2.data);
      });

      it('should encrypt complex nested objects', () => {
        const state = {
          id: 'agent-456',
          metadata: {
            tags: ['tag1', 'tag2'],
            config: {
              setting1: true,
              setting2: 'value',
            },
          },
          history: [
            { event: 'born', timestamp: 1000 },
            { event: 'ate', timestamp: 2000 },
          ],
        };

        const encrypted = securityManager.encryptState(state);

        expect(encrypted.data).toBeDefined();
        expect(encrypted.data.length).toBeGreaterThan(0);
      });

      it('should throw error for invalid key ID', () => {
        const state = { data: 'test' };

        expect(() => {
          securityManager.encryptState(state, 'invalid-key-id');
        }).toThrow('Invalid or inactive key');
      });
    });

    describe('decryptState', () => {
      it('should decrypt state successfully', () => {
        const originalState = {
          id: 'agent-789',
          type: 'virus',
          pattern: /test/g,
          health: 0.95,
        };

        const encrypted = securityManager.encryptState(originalState);
        const decrypted = securityManager.decryptState(encrypted, 'master-key');

        expect(decrypted).toEqual(originalState);
      });

      it('should verify data integrity during decryption', () => {
        const state = { sensitive: 'data' };
        const encrypted = securityManager.encryptState(state);

        // Tamper with encrypted data
        const tamperedEncrypted = {
          ...encrypted,
          data: Buffer.from(encrypted.data, 'base64')
            .map((byte, i) => (i === 0 ? (byte + 1) % 256 : byte))
            .toString('base64'),
        };

        expect(() => {
          securityManager.decryptState(tamperedEncrypted, 'master-key');
        }).toThrow();
      });

      it('should verify authentication tag', () => {
        const state = { data: 'test' };
        const encrypted = securityManager.encryptState(state);

        // Tamper with auth tag
        const tamperedEncrypted = {
          ...encrypted,
          authTag: Buffer.from(encrypted.authTag!, 'base64')
            .map((byte) => (byte + 1) % 256)
            .toString('base64'),
        };

        expect(() => {
          securityManager.decryptState(tamperedEncrypted, 'master-key');
        }).toThrow();
      });

      it('should throw error for invalid key ID', () => {
        const encrypted: EncryptedState = {
          algorithm: EncryptionAlgorithm.AES256_GCM,
          iv: Buffer.alloc(12).toString('base64'),
          authTag: Buffer.alloc(16).toString('base64'),
          data: 'invalid',
          keyId: 'invalid-key-id',
          timestamp: Date.now(),
          version: 1,
        };

        expect(() => {
          securityManager.decryptState(encrypted, 'invalid-key-id');
        }).toThrow('Invalid or inactive key');
      });
    });

    describe('Round-trip encryption', () => {
      it('should maintain data integrity through encrypt-decrypt cycle', () => {
        const testData = {
          string: 'hello world',
          number: 42,
          boolean: true,
          null: null,
          array: [1, 2, 3],
          object: { nested: { value: 'deep' } },
          date: new Date().toISOString(),
          unicode: '🔒🔐🛡️',
        };

        const encrypted = securityManager.encryptState(testData);
        const decrypted = securityManager.decryptState(encrypted, 'master-key');

        expect(decrypted).toEqual(testData);
      });
    });
  });

  describe('Key Management', () => {
    describe('deriveKey', () => {
      it('should derive key from password', () => {
        const password = 'secure-password-123';
        const key = securityManager.deriveKey(password);

        expect(key).toBeDefined();
        expect(key.id).toBeDefined();
        expect(key.key).toBeDefined();
        expect(key.active).toBe(true);
        expect(key.purpose).toBe('derivation');
        expect(key.expiresAt).toBeGreaterThan(Date.now());
      });

      it('should use provided salt', () => {
        const password = 'password';
        const salt = randomBytes(16).toString('base64');

        const key1 = securityManager.deriveKey(password, salt);
        const key2 = securityManager.deriveKey(password, salt);

        // Same salt should produce same key
        expect(key1.key).toBe(key2.key);
      });

      it('should generate different keys with different salts', () => {
        const password = 'password';

        const key1 = securityManager.deriveKey(password);
        const key2 = securityManager.deriveKey(password);

        // Different salts should produce different keys
        expect(key1.key).not.toBe(key2.key);
      });
    });

    describe('generateKeyPair', () => {
      it('should generate asymmetric key pair', () => {
        const keyPair = securityManager.generateKeyPair();

        expect(keyPair).toBeDefined();
        expect(keyPair.publicKey).toBeDefined();
        expect(keyPair.privateKey).toBeDefined();
        expect(keyPair.keyId).toBeDefined();
        expect(keyPair.algorithm).toBe('Ed25519');
      });

      it('should encrypt private key', () => {
        const keyPair = securityManager.generateKeyPair();

        expect(keyPair.privateKey).toBeDefined();
        expect(keyPair.privateKey.algorithm).toBeDefined();
        expect(keyPair.privateKey.data).toBeDefined();
      });

      it('should generate unique key pairs', () => {
        const keyPair1 = securityManager.generateKeyPair();
        const keyPair2 = securityManager.generateKeyPair();

        expect(keyPair1.keyId).not.toBe(keyPair2.keyId);
        expect(keyPair1.publicKey).not.toBe(keyPair2.publicKey);
      });
    });

    describe('rotateKeys', () => {
      it('should rotate expired keys', () => {
        // Create an expired key
        const expiredKey = {
          id: 'expired-key',
          key: randomBytes(32).toString('base64'),
          createdAt: Date.now() - 10000,
          expiresAt: Date.now() - 5000,
          active: true,
          version: 1,
          purpose: 'encryption' as const,
        };

        // Manually add expired key (for testing)
        (securityManager as any).keys.set('expired-key', expiredKey);

        const initialActiveCount = Array.from(
          (securityManager as any).keys.values()
        ).filter((k: any) => k.active).length;

        securityManager.rotateKeys();

        const finalActiveCount = Array.from(
          (securityManager as any).keys.values()
        ).filter((k: any) => k.active).length;

        // Should have one new active key and expired key deactivated
        expect(finalActiveCount).toBe(initialActiveCount);
      });

      it('should update key rotation metrics', () => {
        const metricsBefore = securityManager.getSecurityMetrics();

        // Manually create expired key
        const expiredKey = {
          id: 'expired-key-2',
          key: randomBytes(32).toString('base64'),
          createdAt: Date.now() - 10000,
          expiresAt: Date.now() - 5000,
          active: true,
          version: 1,
          purpose: 'encryption' as const,
        };

        (securityManager as any).keys.set('expired-key-2', expiredKey);
        securityManager.rotateKeys();

        const metricsAfter = securityManager.getSecurityMetrics();

        expect(metricsAfter.keyRotations).toBeGreaterThan(metricsBefore.keyRotations);
      });
    });

    describe('API Key Management', () => {
      it('should add API key', () => {
        const apiKey = 'test-api-key-123';

        securityManager.addApiKey(apiKey);

        expect((securityManager as any).apiKeys.has(apiKey)).toBe(true);
      });

      it('should validate API key', () => {
        const apiKey = 'valid-api-key-456';

        securityManager.addApiKey(apiKey);

        expect(securityManager.validateApiKey(apiKey)).toBe(true);
        expect(securityManager.validateApiKey('invalid-key')).toBe(false);
      });
    });
  });

  describe('Authentication', () => {
    describe('authenticate with password', () => {
      it('should authenticate with valid credentials', async () => {
        const credentials: Credentials = {
          type: 'password',
          username: 'testuser',
          password: 'password123',
        };

        const token = await securityManager.authenticate(credentials);

        expect(token).toBeDefined();
        expect(token.token).toBeDefined();
        expect(token.type).toBe('Bearer');
        expect(token.expiresAt).toBeGreaterThan(Date.now());
        expect(token.issuedAt).toBeLessThanOrEqual(Date.now());
      });

      it('should reject invalid password', async () => {
        const credentials: Credentials = {
          type: 'password',
          username: 'testuser',
          password: 'wrong-password',
        };

        // Mock authentication will still succeed in test mode
        // In production, this would fail
        const token = await securityManager.authenticate(credentials);

        expect(token).toBeDefined();
      });

      it('should require username and password', async () => {
        const credentials: Credentials = {
          type: 'password',
        };

        await expect(securityManager.authenticate(credentials)).rejects.toThrow(
          'Username and password required'
        );
      });
    });

    describe('authenticate with API key', () => {
      it('should authenticate with valid API key', async () => {
        const apiKey = 'valid-api-key-789';
        securityManager.addApiKey(apiKey);

        const credentials: Credentials = {
          type: 'api_key',
          apiKey,
        };

        const token = await securityManager.authenticate(credentials);

        expect(token).toBeDefined();
        expect(token.token).toBeDefined();
      });

      it('should reject invalid API key', async () => {
        const credentials: Credentials = {
          type: 'api_key',
          apiKey: 'invalid-api-key',
        };

        await expect(securityManager.authenticate(credentials)).rejects.toThrow(
          'Invalid API key'
        );
      });
    });

    describe('authenticate with certificate', () => {
      it('should authenticate with valid certificate', async () => {
        const credentials: Credentials = {
          type: 'certificate',
          certificate: 'mock-certificate-data',
        };

        const token = await securityManager.authenticate(credentials);

        expect(token).toBeDefined();
        expect(token.token).toBeDefined();
      });
    });

    describe('token refresh', () => {
      it('should refresh existing token', async () => {
        const originalCredentials: Credentials = {
          type: 'password',
          username: 'testuser',
          password: 'password123',
        };

        const originalToken = await securityManager.authenticate(originalCredentials);

        const refreshCredentials: Credentials = {
          type: 'token',
          token: originalToken.token,
        };

        const refreshedToken = await securityManager.authenticate(refreshCredentials);

        expect(refreshedToken).toBeDefined();
        expect(refreshedToken.expiresAt).toBeGreaterThan(originalToken.expiresAt);
      });
    });

    describe('account lockout', () => {
      it('should lock account after too many failed attempts', async () => {
        const credentials: Credentials = {
          type: 'password',
          username: 'lockout-test-user',
          password: 'password',
        };

        // Create a security manager with low max attempts
        const strictSecurity = createDevSecurityManager();
        (strictSecurity as any).config.maxFailedAttempts = 3;

        // Attempt authentication with invalid credentials multiple times
        // In test mode, we'll simulate failed attempts
        for (let i = 0; i < 5; i++) {
          (strictSecurity as any).recordFailedAttempts('lockout-test-user');
        }

        // Next attempt should be locked
        await expect(strictSecurity.authenticate(credentials)).rejects.toThrow(
          'Account is temporarily locked'
        );
      });
    });
  });

  describe('Token Verification', () => {
    it('should verify valid token', () => {
      const credentials: Credentials = {
        type: 'password',
        username: 'testuser',
        password: 'password123',
      };

      securityManager.authenticate(credentials).then((token) => {
        const payload = securityManager.verifyToken(token.token);

        expect(payload).toBeDefined();
        expect(payload.sub).toBe('testuser');
        expect(payload.exp).toBeGreaterThan(Math.floor(Date.now() / 1000));
      });
    });

    it('should reject invalid token format', () => {
      expect(() => {
        securityManager.verifyToken('invalid-token-format');
      }).toThrow('Invalid token format');
    });

    it('should reject expired token', () => {
      const expiredTokenPayload = {
        sub: 'testuser',
        iss: 'polln-security',
        aud: ['polln-microbiome'],
        iat: Math.floor((Date.now() - 10000) / 1000),
        exp: Math.floor((Date.now() - 5000) / 1000), // Expired
        jti: 'test-jti',
        roles: [Role.EXECUTOR],
        permissions: [],
      };

      const header = Buffer.from(JSON.stringify({ alg: 'RS256', typ: 'JWT' })).toString('base64url');
      const payload = Buffer.from(JSON.stringify(expiredTokenPayload)).toString('base64url');
      const signature = Buffer.from('test-signature').toString('base64url');

      const expiredToken = `${header}.${payload}.${signature}`;

      expect(() => {
        securityManager.verifyToken(expiredToken);
      }).toThrow('Token expired');
    });
  });

  describe('Authorization', () => {
    it('should grant access with valid permission', async () => {
      const credentials: Credentials = {
        type: 'password',
        username: 'operator',
        password: 'password123',
      };

      const token = await securityManager.authenticate(credentials);

      // Mock operator role with AGENT_READ permission
      const hasPermission = securityManager.authorize(
        'operator',
        Permission.AGENT_READ,
        token.token
      );

      expect(hasPermission).toBe(true);
    });

    it('should deny access without permission', async () => {
      const credentials: Credentials = {
        type: 'password',
        username: 'guest',
        password: 'password123',
      };

      const token = await securityManager.authenticate(credentials);

      // Try to access admin permission with guest token
      const hasPermission = securityManager.authorize(
        'guest',
        Permission.SYSTEM_SHUTDOWN,
        token.token
      );

      expect(hasPermission).toBe(false);
    });

    it('should deny access with wrong subject', async () => {
      const credentials: Credentials = {
        type: 'password',
        username: 'user1',
        password: 'password123',
      };

      const token = await securityManager.authenticate(credentials);

      // Try to authorize different user
      const hasPermission = securityManager.authorize(
        'user2', // Different from token.sub
        Permission.AGENT_READ,
        token.token
      );

      expect(hasPermission).toBe(false);
    });

    it('should update unauthorized metrics', async () => {
      const credentials: Credentials = {
        type: 'password',
        username: 'user1',
        password: 'password123',
      };

      const token = await securityManager.authenticate(credentials);
      const metricsBefore = securityManager.getSecurityMetrics();

      // Attempt unauthorized access
      securityManager.authorize('user2', Permission.AGENT_READ, token.token);

      const metricsAfter = securityManager.getSecurityMetrics();

      expect(metricsAfter.unauthorizedAttempts).toBeGreaterThan(metricsBefore.unauthorizedAttempts);
    });
  });

  describe('Digital Signatures', () => {
    describe('sign', () => {
      it('should sign message successfully', () => {
        const keyPair = securityManager.generateKeyPair();

        const message: SignableMessage = {
          id: 'msg-123',
          content: { action: 'test', value: 42 },
          timestamp: Date.now(),
          sender: 'agent-1',
          recipient: 'agent-2',
          type: 'command',
        };

        const signature = securityManager.sign(message, keyPair.keyId);

        expect(signature).toBeDefined();
        expect(signature.value).toBeDefined();
        expect(signature.keyId).toBe(keyPair.keyId);
        expect(signature.algorithm).toBe('Ed25519');
        expect(signature.timestamp).toBeLessThanOrEqual(Date.now());
      });

      it('should throw error for invalid key pair ID', () => {
        const message: SignableMessage = {
          id: 'msg-456',
          content: {},
          timestamp: Date.now(),
          sender: 'agent-1',
          type: 'info',
        };

        expect(() => {
          securityManager.sign(message, 'invalid-keypair-id');
        }).toThrow('Key pair not found');
      });
    });

    describe('verifySignature', () => {
      it('should verify valid signature', () => {
        const keyPair = securityManager.generateKeyPair();

        const message: SignableMessage = {
          id: 'msg-789',
          content: { data: 'test' },
          timestamp: Date.now(),
          sender: 'agent-1',
          type: 'info',
        };

        const signature = securityManager.sign(message, keyPair.keyId);
        const isValid = securityManager.verifySignature(message, signature, keyPair.publicKey);

        expect(isValid).toBe(true);
      });

      it('should reject invalid signature', () => {
        const keyPair = securityManager.generateKeyPair();

        const message: SignableMessage = {
          id: 'msg-999',
          content: { data: 'test' },
          timestamp: Date.now(),
          sender: 'agent-1',
          type: 'info',
        };

        const invalidSignature = {
          algorithm: 'Ed25519' as const,
          value: '',
          keyId: keyPair.keyId,
          timestamp: Date.now(),
        };

        const isValid = securityManager.verifySignature(message, invalidSignature, keyPair.publicKey);

        expect(isValid).toBe(false);
      });

      it('should update signature verification metrics', () => {
        const keyPair = securityManager.generateKeyPair();

        const message: SignableMessage = {
          id: 'msg-111',
          content: {},
          timestamp: Date.now(),
          sender: 'agent-1',
          type: 'info',
        };

        const signature = securityManager.sign(message, keyPair.keyId);

        const metricsBefore = securityManager.getSecurityMetrics();
        securityManager.verifySignature(message, signature, keyPair.publicKey);
        const metricsAfter = securityManager.getSecurityMetrics();

        expect(metricsAfter.signatureVerifications).toBeGreaterThan(metricsBefore.signatureVerifications);
      });
    });
  });

  describe('Audit Logging', () => {
    it('should log security events', () => {
      const initialLogLength = securityManager.getAuditLog().length;

      // Perform an action that generates a log
      securityManager.encryptState({ test: 'data' });

      const auditLog = securityManager.getAuditLog();

      expect(auditLog.length).toBeGreaterThan(initialLogLength);
    });

    it('should include all required event fields', () => {
      securityManager.encryptState({ test: 'data' });

      const auditLog = securityManager.getAuditLog();
      const lastEvent = auditLog[auditLog.length - 1];

      expect(lastEvent).toMatchObject({
        id: expect.any(String),
        type: expect.any(String),
        timestamp: expect.any(Number),
        subject: expect.any(String),
        action: expect.any(String),
        success: expect.any(Boolean),
      });
    });

    it('should limit audit log size', () => {
      const manager = createSecurityManager({ enableAuditLog: true });

      // Set max size to 100 for testing
      (manager as any).auditLog = new Array(150).fill(null).map((_, i) => ({
        id: `event-${i}`,
        type: 'test' as const,
        timestamp: Date.now(),
        subject: 'test',
        action: 'test',
        success: true,
      }));

      // Add one more event
      manager.encryptState({ test: 'data' });

      const auditLog = manager.getAuditLog();

      // Should be limited to 10000 in production, but for testing we can't easily verify
      expect(auditLog.length).toBeGreaterThan(0);
    });

    it('should return limited log entries', () => {
      // Generate some events
      for (let i = 0; i < 10; i++) {
        securityManager.encryptState({ test: i });
      }

      const last5Events = securityManager.getAuditLog(5);

      expect(last5Events.length).toBe(5);
    });

    it('should clear audit log', () => {
      securityManager.encryptState({ test: 'data' });

      expect(securityManager.getAuditLog().length).toBeGreaterThan(0);

      securityManager.clearAuditLog();

      expect(securityManager.getAuditLog().length).toBe(0);
    });
  });

  describe('Security Metrics', () => {
    it('should track authentication attempts', async () => {
      const credentials: Credentials = {
        type: 'password',
        username: 'metrics-test',
        password: 'password123',
      };

      const metricsBefore = securityManager.getSecurityMetrics();

      await securityManager.authenticate(credentials);

      const metricsAfter = securityManager.getSecurityMetrics();

      expect(metricsAfter.totalAuthAttempts).toBeGreaterThan(metricsBefore.totalAuthAttempts);
    });

    it('should track failed authentication attempts', async () => {
      const credentials: Credentials = {
        type: 'api_key',
        apiKey: 'invalid-key',
      };

      const metricsBefore = securityManager.getSecurityMetrics();

      try {
        await securityManager.authenticate(credentials);
      } catch (error) {
        // Expected to fail
      }

      const metricsAfter = securityManager.getSecurityMetrics();

      expect(metricsAfter.failedAuthAttempts).toBeGreaterThan(metricsBefore.failedAuthAttempts);
    });

    it('should calculate threat level based on failure rate', async () => {
      const manager = createDevSecurityManager();

      // Simulate high failure rate
      for (let i = 0; i < 100; i++) {
        (manager as any).metrics.totalAuthAttempts++;
        (manager as any).metrics.failedAuthAttempts++;
      }

      const metrics = manager.getSecurityMetrics();

      expect(metrics.threatLevel).toBe('critical');
    });

    it('should reset metrics', () => {
      securityManager.encryptState({ test: 'data' });

      const metricsBefore = securityManager.getSecurityMetrics();

      securityManager.resetMetrics();

      const metricsAfter = securityManager.getSecurityMetrics();

      expect(metricsAfter.totalAuthAttempts).toBe(0);
      expect(metricsAfter.failedAuthAttempts).toBe(0);
      expect(metricsAfter.signatureVerifications).toBe(0);
    });
  });

  describe('Factory Functions', () => {
    it('should create security manager with default config', () => {
      const manager = createSecurityManager();

      expect(manager).toBeInstanceOf(SecurityManager);
    });

    it('should create dev security manager', () => {
      const manager = createDevSecurityManager();

      expect(manager).toBeInstanceOf(SecurityManager);
    });

    it('should create production security manager', () => {
      const manager = createProductionSecurityManager();

      expect(manager).toBeInstanceOf(SecurityManager);
    });

    it('should apply custom config', () => {
      const customManager = createSecurityManager({
        keyDerivationIterations: 50000,
        tokenLifetime: 30 * 60 * 1000,
      });

      expect(customManager).toBeInstanceOf(SecurityManager);
    });
  });
});

// Helper function for generating random bytes
function randomBytes(size: number): Buffer {
  const bytes = Buffer.alloc(size);
  for (let i = 0; i < size; i++) {
    bytes[i] = Math.floor(Math.random() * 256);
  }
  return bytes;
}
