/**
 * Tests for Token Revocation List
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals';
import {
  TokenRevocationList,
  createTokenRevocationList,
  AuthenticationMiddlewareWithRevocation,
  type RevocationReason,
} from '../revocation.js';

describe('TokenRevocationList', () => {
  let revocationList: TokenRevocationList;

  beforeEach(() => {
    revocationList = createTokenRevocationList({
      backend: 'memory',
      entryTTL: 60000, // 1 minute for tests
      cleanupInterval: 1000,
    });
  });

  afterEach(async () => {
    await revocationList.shutdown();
  });

  describe('User Revocation', () => {
    it('should revoke all tokens for a user', async () => {
      const gardenerId = 'user-123';
      const revocationId = await revocationList.revokeUser(
        gardenerId,
        'logout'
      );

      expect(revocationId).toBeTruthy();
      expect(revocationId).toHaveLength(16);

      const check = await revocationList.checkUser(gardenerId);
      expect(check.revoked).toBe(true);
      expect(check.reason).toBe('logout');
      expect(check.revokedAt).toBeGreaterThan(0);
      expect(check.revocationId).toBe(revocationId);
    });

    it('should return not revoked for non-revoked user', async () => {
      const check = await revocationList.checkUser('nonexistent-user');
      expect(check.revoked).toBe(false);
      expect(check.reason).toBeUndefined();
    });

    it('should handle multiple revocations for same user', async () => {
      const gardenerId = 'user-456';

      await revocationList.revokeUser(gardenerId, 'logout');
      await revocationList.revokeUser(gardenerId, 'security_breach');

      const revocations = await revocationList.getUserRevocations(gardenerId);
      expect(revocations).toHaveLength(2);

      const check = await revocationList.checkUser(gardenerId);
      expect(check.revoked).toBe(true);
      expect(check.reason).toBe('security_breach'); // Most recent
    });

    it('should include metadata in revocation', async () => {
      const gardenerId = 'user-789';
      const metadata = {
        ipAddress: '192.168.1.1',
        userAgent: 'test-agent',
      };

      const revocationId = await revocationList.revokeUser(
        gardenerId,
        'suspicious_activity',
        metadata
      );

      const revocations = await revocationList.getUserRevocations(gardenerId);
      expect(revocations).toHaveLength(1);
      expect(revocations[0].metadata).toMatchObject(metadata);
    });
  });

  describe('Token Revocation', () => {
    it('should revoke a specific token by JTI', async () => {
      const jti = 'token-jti-123';
      const revocationId = await revocationList.revokeToken(
        jti,
        'logout'
      );

      expect(revocationId).toBeTruthy();

      const check = await revocationList.checkToken(jti);
      expect(check.revoked).toBe(true);
      expect(check.reason).toBe('logout');
    });

    it('should return not revoked for non-revoked token', async () => {
      const check = await revocationList.checkToken('nonexistent-jti');
      expect(check.revoked).toBe(false);
    });

    it('should handle multiple token revocations', async () => {
      const jti1 = 'token-jti-1';
      const jti2 = 'token-jti-2';

      await revocationList.revokeToken(jti1, 'logout');
      await revocationList.revokeToken(jti2, 'password_change');

      const check1 = await revocationList.checkToken(jti1);
      const check2 = await revocationList.checkToken(jti2);

      expect(check1.revoked).toBe(true);
      expect(check1.reason).toBe('logout');
      expect(check2.revoked).toBe(true);
      expect(check2.reason).toBe('password_change');
    });
  });

  describe('Token Validation', () => {
    it('should validate non-revoked tokens', async () => {
      const decoded = {
        sub: 'user-123',
        jti: 'token-jti-456',
      };

      const isValid = await revocationList.validateToken(decoded);
      expect(isValid).toBe(true);
    });

    it('should reject tokens with revoked user', async () => {
      const gardenerId = 'user-789';
      await revocationList.revokeUser(gardenerId, 'security_breach');

      const decoded = {
        sub: gardenerId,
        jti: 'token-jti-789',
      };

      const isValid = await revocationList.validateToken(decoded);
      expect(isValid).toBe(false);
    });

    it('should reject tokens with revoked JTI', async () => {
      const jti = 'token-jti-999';
      await revocationList.revokeToken(jti, 'token_theft');

      const decoded = {
        sub: 'user-999',
        jti,
      };

      const isValid = await revocationList.validateToken(decoded);
      expect(isValid).toBe(false);
    });

    it('should handle tokens without JTI', async () => {
      const gardenerId = 'user-no-jti';

      const decoded = {
        sub: gardenerId,
      };

      const isValid = await revocationList.validateToken(decoded);
      expect(isValid).toBe(true);
    });

    it('should handle tokens without user ID', async () => {
      const jti = 'token-no-user';

      const decoded = {
        jti,
      };

      const isValid = await revocationList.validateToken(decoded);
      expect(isValid).toBe(true);
    });
  });

  describe('Revocation Reasons', () => {
    const reasons: RevocationReason[] = [
      'logout',
      'security_breach',
      'password_change',
      'permission_change',
      'suspicious_activity',
      'admin_action',
      'token_theft',
    ];

    it.each(reasons)('should handle %s reason', async (reason) => {
      await revocationList.revokeUser('user-1', reason);

      const check = await revocationList.checkUser('user-1');
      expect(check.reason).toBe(reason);
    });
  });

  describe('Remove Revocation', () => {
    it('should remove a user revocation', async () => {
      const gardenerId = 'user-removable';
      const revocationId = await revocationList.revokeUser(gardenerId, 'logout');

      await revocationList.removeRevocation(revocationId);

      const check = await revocationList.checkUser(gardenerId);
      expect(check.revoked).toBe(false);
    });

    it('should remove a token revocation', async () => {
      const jti = 'token-removable';
      const revocationId = await revocationList.revokeToken(jti, 'logout');

      await revocationList.removeRevocation(revocationId);

      const check = await revocationList.checkToken(jti);
      expect(check.revoked).toBe(false);
    });

    it('should handle removing non-existent revocation', async () => {
      await expect(
        revocationList.removeRevocation('nonexistent-id')
      ).resolves.not.toThrow();
    });
  });

  describe('Cleanup', () => {
    it('should clean up expired entries', async () => {
      // Create revocation with very short TTL
      const revocationListShort = createTokenRevocationList({
        backend: 'memory',
        entryTTL: 100, // 100ms
        cleanupInterval: 50,
      });

      await revocationListShort.revokeUser('user-expire', 'logout');

      // Wait for expiry
      await new Promise(resolve => setTimeout(resolve, 200));

      const count = await revocationListShort.cleanup();
      expect(count).toBeGreaterThan(0);

      await revocationListShort.shutdown();
    });

    it('should not clean up active entries', async () => {
      await revocationList.revokeUser('user-active', 'logout');

      const count = await revocationList.cleanup();
      expect(count).toBe(0);

      const check = await revocationList.checkUser('user-active');
      expect(check.revoked).toBe(true);
    });
  });

  describe('Get User Revocations', () => {
    it('should return empty array for user with no revocations', async () => {
      const revocations = await revocationList.getUserRevocations('nonexistent');
      expect(revocations).toEqual([]);
    });

    it('should return all revocations for user', async () => {
      const gardenerId = 'user-multiple';

      await revocationList.revokeUser(gardenerId, 'logout');
      await revocationList.revokeUser(gardenerId, 'security_breach');

      const revocations = await revocationList.getUserRevocations(gardenerId);
      expect(revocations).toHaveLength(2);
      expect(revocations[0].reason).toBe('logout');
      expect(revocations[1].reason).toBe('security_breach');
    });

    it('should return revocations in reverse chronological order', async () => {
      const gardenerId = 'user-ordered';

      await revocationList.revokeUser(gardenerId, 'logout');
      await revocationList.revokeUser(gardenerId, 'admin_action');

      const revocations = await revocationList.getUserRevocations(gardenerId);
      expect(revocations).toHaveLength(2);
      expect(revocations[0].revokedAt).toBeGreaterThanOrEqual(
        revocations[1].revokedAt
      );
    });
  });

  describe('Shutdown', () => {
    it('should cleanup resources on shutdown', async () => {
      await revocationList.revokeUser('user-shutdown', 'logout');
      await revocationList.shutdown();

      // Should not throw
      await expect(revocationList.checkUser('user-shutdown')).resolves.not.toThrow();
    });
  });
});

describe('AuthenticationMiddlewareWithRevocation', () => {
  let auth: AuthenticationMiddlewareWithRevocation;

  beforeEach(() => {
    auth = new AuthenticationMiddlewareWithRevocation(
      {
        backend: 'memory',
        entryTTL: 60000,
        cleanupInterval: 1000,
      },
      {
        secret: 'test-secret',
        algorithm: 'HS256',
        accessTokenExpiry: 3600,
        refreshTokenExpiry: 604800,
        issuer: 'test-issuer',
        audience: 'test-audience',
      }
    );
  });

  afterEach(async () => {
    await auth.shutdown();
  });

  describe('User Token Revocation', () => {
    it('should revoke all user tokens', async () => {
      const gardenerId = 'user-revoke-test';

      // Generate a token
      const tokenPair = auth.generateTokenPair(gardenerId, [
        { resource: 'colony', actions: ['read'] },
      ]);

      // Validate before revocation
      const beforeValid = auth.validateAccessToken(tokenPair.accessToken);
      expect(beforeValid).toBeTruthy();

      // Revoke user
      await auth.revokeUserTokens(gardenerId, 'security_breach');

      // Validate after revocation
      const afterValid = auth.validateAccessToken(tokenPair.accessToken);
      expect(afterValid).toBeNull();
    });

    it('should check if user is revoked', async () => {
      const gardenerId = 'user-check-revoke';

      expect(await auth.isUserRevoked(gardenerId)).toBe(false);

      await auth.revokeUserTokens(gardenerId, 'logout');

      expect(await auth.isUserRevoked(gardenerId)).toBe(true);
    });

    it('should return revocation list', () => {
      const list = auth.getRevocationList();
      expect(list).toBeInstanceOf(TokenRevocationList);
    });
  });

  describe('Refresh Token Revocation', () => {
    it('should revoke refresh token and add to revocation list', async () => {
      const gardenerId = 'user-refresh-revoke';

      const tokenPair = auth.generateTokenPair(gardenerId, [
        { resource: 'colony', actions: ['read'] },
      ]);

      // Revoke the refresh token
      const revoked = await auth.revokeRefreshToken(
        tokenPair.refreshToken,
        'logout'
      );
      expect(revoked).toBe(true);

      // Check that the JTI is in revocation list
      const { decode } = require('jsonwebtoken');
      const decoded = decode(tokenPair.refreshToken) as { jti: string };

      const list = auth.getRevocationList();
      const check = await list.checkToken(decoded.jti);
      expect(check.revoked).toBe(true);
      expect(check.reason).toBe('logout');
    });

    it('should handle invalid refresh token', async () => {
      const revoked = await auth.revokeRefreshToken(
        'invalid-token',
        'logout'
      );
      expect(revoked).toBe(false);
    });
  });

  describe('Access Token Validation with Revocation', () => {
    it('should validate non-revoked access token', () => {
      const gardenerId = 'user-valid-token';

      const tokenPair = auth.generateTokenPair(gardenerId, [
        { resource: 'colony', actions: ['read'] },
      ]);

      const validated = auth.validateAccessToken(tokenPair.accessToken);
      expect(validated).toBeTruthy();
      expect(validated?.gardenerId).toBe(gardenerId);
    });

    it('should reject access token for revoked user', async () => {
      const gardenerId = 'user-revoked-access';

      const tokenPair = auth.generateTokenPair(gardenerId, [
        { resource: 'colony', actions: ['read'] },
      ]);

      // Revoke user
      await auth.revokeUserTokens(gardenerId, 'admin_action');

      // Token should now be invalid
      const validated = auth.validateAccessToken(tokenPair.accessToken);
      expect(validated).toBeNull();
    });
  });

  describe('Shutdown', () => {
    it('should shutdown revocation list', async () => {
      await auth.shutdown();
      // Should not throw
      await expect(auth.shutdown()).resolves.not.toThrow();
    });
  });
});

describe('Factory Function', () => {
  it('should create TokenRevocationList with default config', () => {
    const list = createTokenRevocationList();
    expect(list).toBeInstanceOf(TokenRevocationList);
  });

  it('should create TokenRevocationList with custom config', () => {
    const list = createTokenRevocationList({
      backend: 'memory',
      entryTTL: 30000,
      cleanupInterval: 5000,
    });
    expect(list).toBeInstanceOf(TokenRevocationList);
  });

  it('should throw error for redis backend without URL', () => {
    expect(() =>
      createTokenRevocationList({
        backend: 'redis',
      })
    ).toThrow('redisUrl is required');
  });

  it('should throw error for file backend without path', () => {
    expect(() =>
      createTokenRevocationList({
        backend: 'file',
      })
    ).toThrow('revocationFilePath is required');
  });
});
