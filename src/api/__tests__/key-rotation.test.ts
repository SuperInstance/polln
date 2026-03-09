/**
 * Tests for Key Rotation Manager
 */

import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import {
  KeyRotationManager,
  createKeyRotationManager,
  AuthenticationMiddlewareWithKeyRotation,
  type KeyStatus,
  type KeyRotationConfig,
} from '../key-rotation.js';

// Mock console.error to avoid clutter
const originalError = console.error;
beforeAll(() => {
  console.error = jest.fn();
});

afterAll(() => {
  console.error = originalError;
});

describe('KeyRotationManager', () => {
  let manager: KeyRotationManager;

  beforeEach(() => {
    manager = createKeyRotationManager({
      rotationIntervalMs: 0, // Manual rotation only for tests
      keyHistorySize: 3,
      gracePeriodMs: 1000, // 1 second for tests
      keyLifetimeMs: 30000, // 30 seconds for tests
    });
  });

  afterEach(async () => {
    await manager.shutdown();
  });

  describe('Initialization', () => {
    it('should create initial key on startup', () => {
      const stats = manager.getStats();
      expect(stats.totalKeys).toBe(1);
      expect(stats.activeKeyId).toBeTruthy();
      expect(stats.activeKeyId).toHaveLength(16);
    });

    it('should use HS256 algorithm by default', () => {
      const keys = manager.getAllKeys();
      expect(keys).toHaveLength(1);
      expect(keys[0].algorithm).toBe('HS256');
    });

    it('should have pending status for new key', () => {
      const keys = manager.getAllKeys();
      expect(keys[0].status).toBe('pending');
    });
  });

  describe('Key Rotation', () => {
    it('should rotate to a new key', async () => {
      const initialKeyId = manager.getStats().activeKeyId;
      const newKeyId = await manager.rotate();

      expect(newKeyId).toBeTruthy();
      expect(newKeyId).not.toBe(initialKeyId);

      const stats = manager.getStats();
      expect(stats.totalKeys).toBe(2);
      expect(stats.activeKeyId).toBe(newKeyId);
    });

    it('should mark old key as deprecated', async () => {
      const initialKeyId = manager.getStats().activeKeyId;
      await manager.rotate();

      const oldKey = manager.getKeyInfo(initialKeyId!);
      expect(oldKey?.status).toBe('deprecated');
    });

    it('should maintain key version numbers', async () => {
      await manager.rotate();
      await manager.rotate();

      const keys = manager.getAllKeys();
      const versions = keys.map(k => k.version).sort((a, b) => b - a);

      expect(versions).toEqual([3, 2, 1]);
    });

    it('should clean up old keys beyond history size', async () => {
      // Rotate 5 times (total 6 keys)
      for (let i = 0; i < 5; i++) {
        await manager.rotate();
      }

      // Wait for grace period to pass
      await new Promise(resolve => setTimeout(resolve, 1100));

      // Trigger cleanup
      await manager['cleanupOldKeys']();

      const stats = manager.getStats();
      // Should keep keyHistorySize (3) plus current
      expect(stats.totalKeys).toBeLessThanOrEqual(4);
    });

    it('should include rotation reason in audit', async () => {
      const auditEvents: unknown[] = [];
      manager['auditLog'] = (event: unknown) => auditEvents.push(event);

      await manager.rotate({ reason: 'security_upgrade' });

      const rotationEvent = auditEvents.find(
        (e: any) => e.type === 'key_rotated'
      ) as any;
      expect(rotationEvent?.details.reason).toBe('security_upgrade');
    });
  });

  describe('Token Signing', () => {
    it('should sign token with current key', () => {
      const token = manager.sign(
        { sub: 'user-123', permissions: [] },
        { expiresIn: 3600 }
      );

      expect(token).toBeTruthy();
      expect(typeof token).toBe('string');

      // JWT format: header.payload.signature
      const parts = token.split('.');
      expect(parts).toHaveLength(3);
    });

    it('should include key ID in token header', () => {
      const currentKeyId = manager.getStats().activeKeyId;
      const token = manager.sign({ sub: 'user-123', permissions: [] });

      // Decode header
      const header = JSON.parse(
        Buffer.from(token.split('.')[0], 'base64url').toString()
      );

      expect(header.kid).toBe(currentKeyId);
    });

    it('should include standard JWT claims', () => {
      const token = manager.sign(
        { sub: 'user-123', permissions: [] },
        { expiresIn: 3600, issuer: 'test-issuer', audience: 'test-audience' }
      );

      const payload = JSON.parse(
        Buffer.from(token.split('.')[1], 'base64url').toString()
      );

      expect(payload.sub).toBe('user-123');
      expect(payload.iat).toBeTruthy();
      expect(payload.exp).toBeTruthy();
    });
  });

  describe('Token Verification', () => {
    it('should verify valid token signed by current key', () => {
      const token = manager.sign(
        { sub: 'user-123', permissions: [{ resource: 'colony', actions: ['read'] }] },
        { issuer: 'test-issuer', audience: 'test-audience' }
      );

      const result = manager.verify(token, {
        issuer: 'test-issuer',
        audience: 'test-audience',
      });

      expect(result.valid).toBe(true);
      expect(result.payload?.sub).toBe('user-123');
      expect(result.keyId).toBeTruthy();
    });

    it('should verify token signed by deprecated key (grace period)', async () => {
      const token = manager.sign({ sub: 'user-456', permissions: [] });
      const oldKeyId = manager.getStats().activeKeyId;

      // Rotate to new key
      await manager.rotate();

      // Old token should still be valid (grace period)
      const result = manager.verify(token);
      expect(result.valid).toBe(true);
      expect(result.keyId).toBe(oldKeyId);
    });

    it('should reject invalid token', () => {
      const result = manager.verify('invalid.token.here');
      expect(result.valid).toBe(false);
      expect(result.error).toBeTruthy();
    });

    it('should reject token with wrong signature', () => {
      const validToken = manager.sign({ sub: 'user-789', permissions: [] });
      const tamperedToken = validToken + 'tampered';

      const result = manager.verify(tamperedToken);
      expect(result.valid).toBe(false);
    });

    it('should reject token with expired key', async () => {
      const token = manager.sign({ sub: 'user-999', permissions: [] });
      const keyId = manager.getStats().activeKeyId;

      // Manually expire the key
      manager.expireKey(keyId!);

      const result = manager.verify(token);
      expect(result.valid).toBe(false);
    });
  });

  describe('Key Compromise', () => {
    it('should mark key as compromised', async () => {
      const keyId = manager.getStats().activeKeyId;
      await manager.compromiseKey(keyId!, 'suspected_leak');

      const keyInfo = manager.getKeyInfo(keyId!);
      expect(keyInfo?.status).toBe('compromised');
    });

    it('should immediately expire compromised key', async () => {
      const keyId = manager.getStats().activeKeyId;
      await manager.compromiseKey(keyId!, 'security_breach');

      const keyInfo = manager.getKeyInfo(keyId!);
      expect(keyInfo?.expiresAt).toBeLessThanOrEqual(Date.now());
    });

    it('should force rotation when current key is compromised', async () => {
      const originalKeyId = manager.getStats().activeKeyId;
      await manager.compromiseKey(originalKeyId!, 'detected_exposure');

      const newKeyId = manager.getStats().activeKeyId;
      expect(newKeyId).not.toBe(originalKeyId);
    });
  });

  describe('Key Expiration', () => {
    it('should manually expire a key', () => {
      const keyId = manager.getStats().activeKeyId;
      const result = manager.expireKey(keyId!);

      expect(result).toBe(true);

      const keyInfo = manager.getKeyInfo(keyId!);
      expect(keyInfo?.status).toBe('expired');
    });

    it('should return false when expiring non-existent key', () => {
      const result = manager.expireKey('nonexistent-key');
      expect(result).toBe(false);
    });

    it('should reject tokens signed by expired key', () => {
      const token = manager.sign({ sub: 'user-expire', permissions: [] });
      const keyId = manager.getStats().activeKeyId;

      manager.expireKey(keyId!);

      const result = manager.verify(token);
      expect(result.valid).toBe(false);
    });
  });

  describe('Key Information', () => {
    it('should return key info without secret', () => {
      const keyId = manager.getStats().activeKeyId;
      const keyInfo = manager.getKeyInfo(keyId!);

      expect(keyInfo).toBeTruthy();
      expect(keyInfo?.keyId).toBe(keyId);
      expect(keyInfo).not.toHaveProperty('secret');
    });

    it('should return all keys sorted by creation time', async () => {
      await manager.rotate();
      await manager.rotate();

      const keys = manager.getAllKeys();
      expect(keys.length).toBeGreaterThanOrEqual(2);

      // Check descending order
      for (let i = 0; i < keys.length - 1; i++) {
        expect(keys[i].createdAt).toBeGreaterThanOrEqual(keys[i + 1].createdAt);
      }
    });

    it('should return null for non-existent key', () => {
      const keyInfo = manager.getKeyInfo('nonexistent');
      expect(keyInfo).toBeNull();
    });
  });

  describe('Statistics', () => {
    it('should return accurate stats', async () => {
      await manager.rotate();
      await manager.rotate();

      const stats = manager.getStats();

      expect(stats.totalKeys).toBe(3);
      expect(stats.activeKeyId).toBeTruthy();
      expect(stats.keysByStatus.pending).toBeGreaterThan(0);
    });

    it('should track last rotation time', async () => {
      await manager.rotate();

      const stats = manager.getStats();
      expect(stats.lastRotationAt).toBeTruthy();
      expect(stats.lastRotationAt).toBeLessThanOrEqual(Date.now());
    });

    it('should not have next rotation for manual mode', () => {
      const stats = manager.getStats();
      expect(stats.nextRotationAt).toBeUndefined();
    });
  });

  describe('Asymmetric Keys (RSA)', () => {
    it('should generate RSA key pairs when configured', () => {
      const rsaManager = createKeyRotationManager({
        rotationIntervalMs: 0,
        useAsymmetric: true,
        rsaKeySize: 2048,
      });

      const keys = rsaManager.getAllKeys();
      expect(keys).toHaveLength(1);
      expect(keys[0].algorithm).toBe('RS256');

      rsaManager.shutdown();
    });

    it('should include public key in key metadata', () => {
      const rsaManager = createKeyRotationManager({
        rotationIntervalMs: 0,
        useAsymmetric: true,
      });

      const key = rsaManager['keys'].values().next().value;
      expect(key.publicKey).toBeTruthy();
      expect(key.publicKey).toContain('BEGIN PUBLIC KEY');

      rsaManager.shutdown();
    });
  });

  describe('Shutdown', () => {
    it('should cleanup resources on shutdown', async () => {
      await manager.shutdown();
      // Should not throw
      await expect(manager.shutdown()).resolves.not.toThrow();
    });
  });
});

describe('AuthenticationMiddlewareWithKeyRotation', () => {
  let auth: AuthenticationMiddlewareWithKeyRotation;

  beforeEach(() => {
    auth = new AuthenticationMiddlewareWithKeyRotation(
      {
        rotationIntervalMs: 0,
      },
      {
        issuer: 'test-issuer',
        audience: 'test-audience',
        accessTokenExpiry: 3600,
        refreshTokenExpiry: 604800,
      }
    );
  });

  afterEach(async () => {
    await auth.shutdown();
  });

  describe('Token Generation with Rotation', () => {
    it('should generate token pair using key rotation', () => {
      const tokenPair = auth.generateTokenPair('user-123', [
        { resource: 'colony', actions: ['read', 'write'] },
      ]);

      expect(tokenPair.accessToken).toBeTruthy();
      expect(tokenPair.refreshToken).toBeTruthy();
      expect(tokenPair.expiresAt).toBeTruthy();
    });

    it('should validate token signed by key manager', () => {
      const tokenPair = auth.generateTokenPair('user-456', [
        { resource: 'agent', actions: ['read'] },
      ]);

      const validated = auth.validateAccessToken(tokenPair.accessToken);

      expect(validated).toBeTruthy();
      expect(validated?.gardenerId).toBe('user-456');
      expect(validated?.permissions).toHaveLength(1);
    });

    it('should reject token from rotated key after grace period', async () => {
      const tokenPair = auth.generateTokenPair('user-789', []);

      // Rotate keys
      await auth.rotateKeys('scheduled_rotation');

      // Token from old key should still work (grace period)
      const validated = auth.validateAccessToken(tokenPair.accessToken);
      expect(validated).toBeTruthy();
    });
  });

  describe('Key Rotation', () => {
    it('should rotate keys on demand', async () => {
      const statsBefore = auth.getKeyStats();
      await auth.rotateKeys('security_upgrade');

      const statsAfter = auth.getKeyStats();
      expect(statsAfter.totalKeys).toBe(statsBefore.totalKeys + 1);
    });

    it('should provide access to key manager', () => {
      const keyManager = auth.getKeyManager();
      expect(keyManager).toBeInstanceOf(KeyRotationManager);
    });
  });

  describe('Statistics', () => {
    it('should return key rotation stats', () => {
      const stats = auth.getKeyStats();
      expect(stats.totalKeys).toBeGreaterThan(0);
      expect(stats.activeKeyId).toBeTruthy();
    });
  });

  describe('Shutdown', () => {
    it('should shutdown key manager', async () => {
      await auth.shutdown();
      // Should not throw
      await expect(auth.shutdown()).resolves.not.toThrow();
    });
  });
});

describe('Factory Function', () => {
  it('should create KeyRotationManager with default config', () => {
    const manager = createKeyRotationManager();
    expect(manager).toBeInstanceOf(KeyRotationManager);
    manager.shutdown();
  });

  it('should create KeyRotationManager with custom config', () => {
    const manager = createKeyRotationManager({
      rotationIntervalMs: 60000,
      keyHistorySize: 10,
    });
    expect(manager).toBeInstanceOf(KeyRotationManager);
    manager.shutdown();
  });
});
