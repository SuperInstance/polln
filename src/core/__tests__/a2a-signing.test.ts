/**
 * Tests for A2A Package Cryptographic Signing Module
 */

import { describe, it, expect, beforeEach, afterEach, jest } from '@jest/globals';
import {
  A2APackageSigningService,
  A2APackageSystemWithSigning,
  createA2ASigningService,
  createA2APackageSystemWithSigning,
  type PackageSignature,
  type SignatureAlgorithm,
  type A2ASigningConfig,
  type HashChainLink,
} from '../a2a-signing.js';
import { type A2APackage } from '../types.js';

// Mock console.error to avoid clutter
const originalError = console.error;
beforeAll(() => {
  console.error = jest.fn();
});

afterAll(() => {
  console.error = originalError;
});

describe('A2APackageSigningService', () => {
  let signingService: A2APackageSigningService;
  let mockPackage: A2APackage<{ message: string }>;

  beforeEach(() => {
    signingService = createA2ASigningService({
      enableSigning: true,
      defaultAlgorithm: 'HS256',
      signatureExpirationMs: 7 * 24 * 60 * 60 * 1000, // 7 days
      enableHashChain: true,
    });

    // Create a mock package
    mockPackage = {
      id: 'pkg-001',
      timestamp: Date.now(),
      senderId: 'agent-001',
      receiverId: 'agent-002',
      type: 'test-message',
      payload: { message: 'Hello, World!' },
      parentIds: [],
      causalChainId: 'chain-001',
      privacyLevel: 'public',
      layer: 'deliberate',
    };
  });

  describe('Initialization', () => {
    it('should create with default config', () => {
      const service = createA2ASigningService();
      const stats = service.getStats();

      expect(stats.totalSignatures).toBe(0);
      expect(stats.activeKeys).toBe(1);
      expect(stats.hashChains).toBe(0);
    });

    it('should create with custom config', () => {
      const config: Partial<A2ASigningConfig> = {
        defaultAlgorithm: 'HS512',
        signatureExpirationMs: 0,
        enableHashChain: false,
      };
      const service = createA2ASigningService(config);
      const stats = service.getStats();

      expect(stats.activeKeys).toBe(1);
    });

    it('should initialize with default signing key', () => {
      const keys = signingService['signingKeys'];
      expect(keys.size).toBe(1);
      expect(keys.has('a2a-key-0')).toBe(true);
    });
  });

  describe('Package Signing', () => {
    it('should sign a package with default settings', async () => {
      const signature = await signingService.signPackage(mockPackage);

      expect(signature).toBeTruthy();
      expect(signature.signatureId).toBeTruthy();
      expect(signature.keyId).toBe('a2a-key-0');
      expect(signature.algorithm).toBe('HS256');
      expect(signature.signature).toBeTruthy();
      expect(signature.signedAt).toBeLessThanOrEqual(Date.now());
      expect(signature.signerId).toBe(mockPackage.senderId);
      expect(signature.payloadHash).toBeTruthy();
    });

    it('should sign with custom algorithm', async () => {
      const signature = await signingService.signPackage(mockPackage, {
        algorithm: 'HS512',
      });

      expect(signature.algorithm).toBe('HS512');
    });

    it('should sign with custom signer ID', async () => {
      const signature = await signingService.signPackage(mockPackage, {
        signerId: 'custom-signer',
      });

      expect(signature.signerId).toBe('custom-signer');
    });

    it('should store signature after signing', async () => {
      await signingService.signPackage(mockPackage);
      const retrieved = signingService.getSignature(mockPackage.id);

      expect(retrieved).toBeTruthy();
      expect(retrieved?.signatureId).toBeTruthy();
    });

    it('should throw when signing is disabled', async () => {
      const disabledService = createA2ASigningService({
        enableSigning: false,
      });

      await expect(disabledService.signPackage(mockPackage)).rejects.toThrow(
        'Package signing is disabled'
      );
    });

    it('should include signature expiration when configured', async () => {
      const service = createA2ASigningService({
        signatureExpirationMs: 3600000, // 1 hour
      });
      const signature = await service.signPackage(mockPackage);

      expect(signature.expiresAt).toBeTruthy();
      expect(signature.expiresAt).toBeGreaterThan(Date.now());
    });

    it('should not include expiration when set to 0', async () => {
      const service = createA2ASigningService({
        signatureExpirationMs: 0,
      });
      const signature = await service.signPackage(mockPackage);

      expect(signature.expiresAt).toBeUndefined();
    });

    it('should use custom key ID when provided', async () => {
      signingService.addSigningKey('custom-key', 'secret-value');

      const signature = await signingService.signPackage(mockPackage, {
        keyId: 'custom-key',
      });

      expect(signature.keyId).toBe('custom-key');
    });

    it('should throw when key ID not found', async () => {
      await expect(
        signingService.signPackage(mockPackage, { keyId: 'non-existent-key' })
      ).rejects.toThrow('Signing key non-existent-key not found');
    });
  });

  describe('Signature Verification', () => {
    it('should verify valid signature', async () => {
      await signingService.signPackage(mockPackage);
      const result = await signingService.verifySignature(mockPackage);

      expect(result.valid).toBe(true);
      expect(result.signature).toBeTruthy();
      expect(result.error).toBeUndefined();
    });

    it('should reject when no signature found', async () => {
      const result = await signingService.verifySignature(mockPackage);

      expect(result.valid).toBe(false);
      expect(result.error).toBe('No signature found for package');
    });

    it('should reject expired signature', async () => {
      const service = createA2ASigningService({
        signatureExpirationMs: 100, // 100ms
      });

      await service.signPackage(mockPackage);

      // Wait for expiration
      await new Promise(resolve => setTimeout(resolve, 150));

      const result = await service.verifySignature(mockPackage);
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Signature has expired');
    });

    it('should reject when package is modified', async () => {
      await signingService.signPackage(mockPackage);

      // Modify the package
      mockPackage.payload.message = 'Modified message';

      const result = await signingService.verifySignature(mockPackage);
      expect(result.valid).toBe(false);
      expect(result.error).toBe('Package payload has been modified');
    });

    it('should reject when signing key is removed', async () => {
      const service = createA2ASigningService();

      // Add a temporary key and sign with it
      service.addSigningKey('temp-key', 'temp-secret');
      const signature = await service.signPackage(mockPackage, {
        keyId: 'temp-key',
      });

      // Remove the key
      service['signingKeys'].delete('temp-key');

      // Manually update the key ID in signature to test missing key
      const storedSignature = service['signatures'].get(mockPackage.id);
      if (storedSignature) {
        // Signature is already stored, let's verify
      }

      const result = await service.verifySignature(mockPackage);
      expect(result.valid).toBe(false);
    });
  });

  describe('Hash Chains', () => {
    it('should create hash chain link when signing', async () => {
      await signingService.signPackage(mockPackage);
      const chain = signingService.getHashChain(mockPackage.senderId);

      expect(chain.length).toBe(1);
      expect(chain[0].packageId).toBe(mockPackage.id);
      expect(chain[0].previousHash).toBe('genesis');
      expect(chain[0].linkHash).toBeTruthy();
    });

    it('should chain multiple packages from same sender', async () => {
      await signingService.signPackage(mockPackage);

      const pkg2: A2APackage<{ data: number }> = {
        ...mockPackage,
        id: 'pkg-002',
        payload: { data: 42 },
      };

      await signingService.signPackage(pkg2);

      const chain = signingService.getHashChain(mockPackage.senderId);
      expect(chain.length).toBe(2);
      expect(chain[1].previousHash).toBe(chain[0].linkHash);
    });

    it('should verify hash chain integrity', () => {
      const chain = signingService.getHashChain(mockPackage.senderId);
      expect(signingService.verifyHashChain(mockPackage.senderId)).toBe(true);
    });

    it('should detect broken hash chain', async () => {
      await signingService.signPackage(mockPackage);

      const chain = signingService.getHashChain(mockPackage.senderId);
      chain[0].linkHash = 'tampered-hash';

      expect(signingService.verifyHashChain(mockPackage.senderId)).toBe(false);
    });

    it('should not create hash chain when disabled', async () => {
      const service = createA2ASigningService({
        enableHashChain: false,
      });

      await service.signPackage(mockPackage);
      const chain = service.getHashChain(mockPackage.senderId);

      expect(chain.length).toBe(0);
    });

    it('should maintain separate chains per sender', async () => {
      await signingService.signPackage(mockPackage);

      const pkg2: A2APackage<{ data: string }> = {
        ...mockPackage,
        id: 'pkg-002',
        senderId: 'agent-002',
      };

      await signingService.signPackage(pkg2);

      const chain1 = signingService.getHashChain('agent-001');
      const chain2 = signingService.getHashChain('agent-002');

      expect(chain1.length).toBe(1);
      expect(chain2.length).toBe(1);
    });
  });

  describe('Key Management', () => {
    it('should rotate signing key', () => {
      const oldKeyId = Array.from(signingService['signingKeys'].keys())[0];
      const newKeyId = signingService.rotateSigningKey();

      expect(newKeyId).not.toBe(oldKeyId);
      expect(newKeyId).toContain('a2a-key-');
    });

    it('should add custom signing key', () => {
      signingService.addSigningKey('custom-key', 'custom-secret');

      const key = signingService['signingKeys'].get('custom-key');
      expect(key).toBe('custom-secret');
    });

    it('should maintain multiple keys', () => {
      signingService.addSigningKey('key-1', 'secret-1');
      signingService.addSigningKey('key-2', 'secret-2');

      expect(signingService['signingKeys'].size).toBe(3); // default + 2 new
    });
  });

  describe('Signature Cleanup', () => {
    it('should remove expired signatures', async () => {
      const service = createA2ASigningService({
        signatureExpirationMs: 100,
      });

      await service.signPackage(mockPackage);

      // Wait for expiration
      await new Promise(resolve => setTimeout(resolve, 150));

      const count = service.cleanupExpiredSignatures();
      expect(count).toBe(1);

      const signature = service.getSignature(mockPackage.id);
      expect(signature).toBeUndefined();
    });

    it('should not remove non-expired signatures', async () => {
      const service = createA2ASigningService({
        signatureExpirationMs: 3600000,
      });

      await service.signPackage(mockPackage);

      const count = service.cleanupExpiredSignatures();
      expect(count).toBe(0);

      const signature = service.getSignature(mockPackage.id);
      expect(signature).toBeTruthy();
    });
  });

  describe('Statistics', () => {
    it('should return accurate statistics', async () => {
      await signingService.signPackage(mockPackage);
      await signingService.signPackage({
        ...mockPackage,
        id: 'pkg-002',
      });

      const stats = signingService.getStats();

      expect(stats.totalSignatures).toBe(2);
      expect(stats.activeKeys).toBe(1);
      expect(stats.hashChains).toBe(1);
    });
  });

  describe('Clear Operation', () => {
    it('should clear all signatures and hash chains', async () => {
      await signingService.signPackage(mockPackage);

      signingService.clear();

      const stats = signingService.getStats();
      expect(stats.totalSignatures).toBe(0);
      expect(stats.hashChains).toBe(0);
    });
  });

  describe('HMAC Signing', () => {
    const algorithms: SignatureAlgorithm[] = ['HS256', 'HS384', 'HS512'];

    it.each(algorithms)('should sign and verify with %s', async (algorithm) => {
      const signature = await signingService.signPackage(mockPackage, {
        algorithm,
      });

      expect(signature.algorithm).toBe(algorithm);

      const result = await signingService.verifySignature(mockPackage);
      expect(result.valid).toBe(true);
    });
  });
});

describe('A2APackageSystemWithSigning', () => {
  let packageSystem: A2APackageSystemWithSigning;

  beforeEach(() => {
    packageSystem = createA2APackageSystemWithSigning(
      undefined, // Default A2A system config
      {
        enableSigning: true,
        defaultAlgorithm: 'HS256',
        signatureExpirationMs: 7 * 24 * 60 * 60 * 1000,
      }
    );
  });

  afterEach(() => {
    // Cleanup
  });

  describe('Package Creation with Signing', () => {
    it('should create and sign package by default', async () => {
      const pkg = await packageSystem.createPackage(
        'sender-001',
        'receiver-001',
        'test-type',
        { data: 'test' }
      );

      expect(pkg).toBeTruthy();
      expect(pkg.id).toBeTruthy();

      // Verify signature exists
      const signingService = packageSystem.getSigningService();
      const signature = signingService.getSignature(pkg.id);
      expect(signature).toBeTruthy();
    });

    it('should skip signing when sign option is false', async () => {
      const pkg = await packageSystem.createPackage(
        'sender-001',
        'receiver-001',
        'test-type',
        { data: 'test' },
        { sign: false }
      );

      expect(pkg).toBeTruthy();

      const signingService = packageSystem.getSigningService();
      const signature = signingService.getSignature(pkg.id);
      expect(signature).toBeUndefined();
    });

    it('should use custom signer ID when provided', async () => {
      const customSigner = 'custom-signer-agent';
      const pkg = await packageSystem.createPackage(
        'sender-001',
        'receiver-001',
        'test-type',
        { data: 'test' },
        { signerId: customSigner }
      );

      const signingService = packageSystem.getSigningService();
      const signature = signingService.getSignature(pkg.id!);
      expect(signature?.signerId).toBe(customSigner);
    });
  });

  describe('Signature Verification', () => {
    it('should verify valid package signature', async () => {
      const pkg = await packageSystem.createPackage(
        'sender-001',
        'receiver-001',
        'test-type',
        { data: 'test' }
      );

      const result = await packageSystem.verifySignature(pkg);
      expect(result.valid).toBe(true);
    });

    it('should reject unsigned package', async () => {
      const pkg = await packageSystem.createPackage(
        'sender-001',
        'receiver-001',
        'test-type',
        { data: 'test' },
        { sign: false }
      );

      const result = await packageSystem.verifySignature(pkg);
      expect(result.valid).toBe(false);
    });
  });

  describe('Hash Chain Operations', () => {
    it('should get hash chain for agent', async () => {
      await packageSystem.createPackage(
        'agent-001',
        'agent-002',
        'test',
        { data: 'test-1' }
      );

      await packageSystem.createPackage(
        'agent-001',
        'agent-003',
        'test',
        { data: 'test-2' }
      );

      const chain = packageSystem.getHashChain('agent-001');
      expect(chain.length).toBe(2);
    });

    it('should verify hash chain integrity', async () => {
      await packageSystem.createPackage(
        'agent-001',
        'agent-002',
        'test',
        { data: 'test' }
      );

      const isValid = packageSystem.verifyHashChain('agent-001');
      expect(isValid).toBe(true);
    });
  });

  describe('Key Rotation', () => {
    it('should rotate signing keys', () => {
      const statsBefore = packageSystem.getSigningService().getStats();
      const newKeyId = packageSystem.rotateSigningKey();

      expect(newKeyId).toBeTruthy();

      const statsAfter = packageSystem.getSigningService().getStats();
      expect(statsAfter.activeKeys).toBeGreaterThan(statsBefore.activeKeys);
    });
  });

  describe('Signature Cleanup', () => {
    it('should cleanup expired signatures', () => {
      const count = packageSystem.cleanupExpiredSignatures();
      expect(typeof count).toBe('number');
    });
  });

  describe('Signing Service Access', () => {
    it('should provide access to underlying signing service', () => {
      const service = packageSystem.getSigningService();
      expect(service).toBeInstanceOf(A2APackageSigningService);
    });
  });
});

describe('Factory Functions', () => {
  it('should create signing service with factory', () => {
    const service = createA2ASigningService({
      defaultAlgorithm: 'HS512',
    });

    expect(service).toBeInstanceOf(A2APackageSigningService);
  });

  it('should create package system with factory', () => {
    const system = createA2APackageSystemWithSigning(
      { enablePersistence: false },
      { enableSigning: true }
    );

    expect(system).toBeInstanceOf(A2APackageSystemWithSigning);
  });
});

describe('Hash Chain Integrity Edge Cases', () => {
  let signingService: A2APackageSigningService;

  beforeEach(() => {
    signingService = createA2ASigningService();
  });

  it('should handle empty chain as valid', () => {
    const isValid = signingService.verifyHashChain('non-existent-agent');
    expect(isValid).toBe(true);
  });

  it('should detect tampered previous hash', async () => {
    const pkg: A2APackage<{ data: string }> = {
      id: 'pkg-001',
      timestamp: Date.now(),
      senderId: 'agent-001',
      receiverId: 'agent-002',
      type: 'test',
      payload: { data: 'test' },
      parentIds: [],
      causalChainId: 'chain-001',
      privacyLevel: 'public',
      layer: 'deliberate',
    };

    await signingService.signPackage(pkg);

    const chain = signingService.getHashChain('agent-001');
    if (chain.length > 0) {
      // Tamper with the first link's previous hash
      chain[0].previousHash = 'not-genesis';

      expect(signingService.verifyHashChain('agent-001')).toBe(false);
    }
  });
});
