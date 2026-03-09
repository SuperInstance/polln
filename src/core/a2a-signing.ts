/**
 * A2A Package Cryptographic Signing Module
 *
 * Provides integrity and non-repudiation for A2A packages through:
 * - HMAC-based signatures (symmetric)
 * - RSA/EdDSA signatures (asymmetric)
 * - Hash chains for incremental verification
 * - Signature verification
 * - Key management integration
 */

import { createHash, createHmac, randomBytes } from 'crypto';
import { sign as signJwt, verify as verifyJwt, Algorithm } from 'jsonwebtoken';
import { v4 as uuidv4 } from 'uuid';

// ============================================================================
// Types
// ============================================================================

export interface PackageSignature {
  /** Unique signature ID */
  signatureId: string;
  /** Key ID used for signing */
  keyId: string;
  /** Signature algorithm */
  algorithm: SignatureAlgorithm;
  /** The signature value (base64url encoded) */
  signature: string;
  /** Timestamp when signature was created */
  signedAt: number;
  /** Signature expiration (optional) */
  expiresAt?: number;
  /** Signer's agent ID */
  signerId: string;
  /** Hash of the payload (for verification) */
  payloadHash: string;
}

export type SignatureAlgorithm = 'HS256' | 'HS384' | 'HS512' | 'RS256' | 'RS384' | 'RS512' | 'EdDSA';

export interface A2ASigningConfig {
  /** Enable package signing */
  enableSigning: boolean;
  /** Default signature algorithm */
  defaultAlgorithm: SignatureAlgorithm;
  /** Signature expiration (milliseconds, 0 = no expiration) */
  signatureExpirationMs: number;
  /** Enable hash chain for incremental verification */
  enableHashChain: boolean;
  /** Key identifier prefix */
  keyIdPrefix: string;
}

export interface SignatureVerificationResult {
  /** Whether signature is valid */
  valid: boolean;
  /** Signature details (if valid) */
  signature?: PackageSignature;
  /** Verification error (if invalid) */
  error?: string;
}

export interface HashChainLink {
  /** Link hash (hash of previous link + package data) */
  linkHash: string;
  /** Package ID this link represents */
  packageId: string;
  /** Previous link hash */
  previousHash: string;
  /** Timestamp */
  timestamp: number;
  /** Signer's agent ID */
  signerId: string;
  /** Signature value used to create the link hash */
  signature: string;
}

// ============================================================================
// A2A Package Signing Service
// ============================================================================

export class A2APackageSigningService {
  private config: A2ASigningConfig;
  private signingKeys: Map<string, string> = new Map(); // keyId -> secret
  private signatures: Map<string, PackageSignature> = new Map(); // packageId -> signature
  private hashChains: Map<string, HashChainLink[]> = new Map(); // agentId -> chain
  private keyRotationCounter = 0;

  constructor(config?: Partial<A2ASigningConfig>) {
    this.config = {
      enableSigning: true,
      defaultAlgorithm: 'HS256',
      signatureExpirationMs: 7 * 24 * 60 * 60 * 1000, // 7 days
      enableHashChain: true,
      keyIdPrefix: 'a2a-key',
      ...config,
    };

    // Initialize with default signing key
    this.initializeSigningKey();
  }

  /**
   * Initialize default signing key
   */
  private initializeSigningKey(): void {
    const keyId = `${this.config.keyIdPrefix}-0`;
    const secret = this.generateSecret();
    this.signingKeys.set(keyId, secret);
  }

  /**
   * Generate a new signing secret
   */
  private generateSecret(): string {
    return randomBytes(64).toString('base64');
  }

  /**
   * Generate key ID
   */
  private generateKeyId(): string {
    return `${this.config.keyIdPrefix}-${++this.keyRotationCounter}`;
  }

  /**
   * Sign an A2A package
   */
  async signPackage<T>(
    pkg: import('./types.js').A2APackage<T>,
    options?: {
      keyId?: string;
      algorithm?: SignatureAlgorithm;
      signerId?: string;
    }
  ): Promise<PackageSignature> {
    if (!this.config.enableSigning) {
      throw new Error('Package signing is disabled');
    }

    const keyId = options?.keyId || Array.from(this.signingKeys.keys())[0];
    if (!keyId) {
      throw new Error('No signing key available');
    }

    const secret = this.signingKeys.get(keyId);
    if (!secret) {
      throw new Error(`Signing key ${keyId} not found`);
    }

    const algorithm = options?.algorithm || this.config.defaultAlgorithm;
    const signerId = options?.signerId || pkg.senderId;
    const payloadHash = this.hashPackage(pkg);

    let signature: string;

    if (algorithm.startsWith('HS')) {
      // HMAC signing
      signature = this.signHMAC(payloadHash, secret, algorithm);
    } else if (algorithm.startsWith('RS')) {
      // RSA signing (requires key rotation manager with RSA)
      signature = this.signAsymmetric(payloadHash, secret, algorithm);
    } else if (algorithm === 'EdDSA') {
      // EdDSA signing
      signature = this.signAsymmetric(payloadHash, secret, algorithm);
    } else {
      throw new Error(`Unsupported algorithm: ${algorithm}`);
    }

    const packageSignature: PackageSignature = {
      signatureId: uuidv4(),
      keyId,
      algorithm,
      signature,
      signedAt: Date.now(),
      expiresAt: this.config.signatureExpirationMs > 0
        ? Date.now() + this.config.signatureExpirationMs
        : undefined,
      signerId,
      payloadHash,
    };

    // Store signature
    this.signatures.set(pkg.id, packageSignature);

    // Update hash chain if enabled
    if (this.config.enableHashChain) {
      this.updateHashChain(pkg, packageSignature);
    }

    return packageSignature;
  }

  /**
   * Sign package payload with HMAC
   */
  private signHMAC(payloadHash: string, secret: string, algorithm: SignatureAlgorithm): string {
    const hmac = createHmac(algorithm.replace('HS', 'sha') as 'sha256' | 'sha384' | 'sha512', secret);
    hmac.update(payloadHash);
    return hmac.digest('base64url');
  }

  /**
   * Sign package payload with asymmetric key
   */
  private signAsymmetric(payloadHash: string, privateKey: string, algorithm: SignatureAlgorithm): string {
    const jwtPayload = {
      payload: payloadHash,
      alg: algorithm,
    };

    return signJwt(jwtPayload, privateKey, { algorithm });
  }

  /**
   * Verify package signature
   */
  async verifySignature<T>(
    pkg: import('./types.js').A2APackage<T>
  ): Promise<SignatureVerificationResult> {
    const signature = this.signatures.get(pkg.id);
    if (!signature) {
      return {
        valid: false,
        error: 'No signature found for package',
      };
    }

    // Check expiration
    if (signature.expiresAt && Date.now() > signature.expiresAt) {
      return {
        valid: false,
        error: 'Signature has expired',
      };
    }

    // Verify hash hasn't changed
    const currentHash = this.hashPackage(pkg);
    if (currentHash !== signature.payloadHash) {
      return {
        valid: false,
        error: 'Package payload has been modified',
      };
    }

    // Verify signature
    const secret = this.signingKeys.get(signature.keyId);
    if (!secret) {
      return {
        valid: false,
        error: 'Signing key not found',
      };
    }

    let isValid = false;

    if (signature.algorithm.startsWith('HS')) {
      isValid = this.verifyHMAC(signature, secret);
    } else if (signature.algorithm.startsWith('RS') || signature.algorithm === 'EdDSA') {
      isValid = this.verifyAsymmetric(signature, secret);
    }

    if (isValid) {
      return {
        valid: true,
        signature,
      };
    }

    return {
      valid: false,
      error: 'Signature verification failed',
    };
  }

  /**
   * Verify HMAC signature
   */
  private verifyHMAC(signature: PackageSignature, secret: string): boolean {
    const hmac = createHmac(
      signature.algorithm.replace('HS', 'sha') as 'sha256' | 'sha384' | 'sha512',
      secret
    );
    hmac.update(signature.payloadHash);
    const expected = hmac.digest('base64url');
    return expected === signature.signature;
  }

  /**
   * Verify asymmetric signature
   */
  private verifyAsymmetric(signature: PackageSignature, publicKey: string): boolean {
    try {
      const decoded = verifyJwt(
        signature.signature,
        publicKey,
        { algorithms: [signature.algorithm] }
      ) as { payload?: string };

      return decoded.payload === signature.payloadHash;
    } catch {
      return false;
    }
  }

  /**
   * Hash package for signing
   */
  private hashPackage<T>(pkg: import('./types.js').A2APackage<T>): string {
    // Create canonical representation for hashing
    const canonical = JSON.stringify({
      id: pkg.id,
      timestamp: pkg.timestamp,
      senderId: pkg.senderId,
      receiverId: pkg.receiverId,
      type: pkg.type,
      payload: pkg.payload,
      parentIds: pkg.parentIds.sort(), // Sort for determinism
      causalChainId: pkg.causalChainId,
      privacyLevel: pkg.privacyLevel,
      layer: pkg.layer,
    });

    return createHash('sha256').update(canonical).digest('base64url');
  }

  /**
   * Update hash chain
   */
  private updateHashChain<T>(
    pkg: import('./types.js').A2APackage<T>,
    signature: PackageSignature
  ): void {
    const chain = this.hashChains.get(pkg.senderId) || [];

    // Get previous hash
    const previousHash = chain.length > 0
      ? chain[chain.length - 1].linkHash
      : 'genesis';

    // Create link hash
    const linkData = `${previousHash}:${pkg.id}:${signature.signature}`;
    const linkHash = createHash('sha256').update(linkData).digest('hex');

    const link: HashChainLink = {
      linkHash,
      packageId: pkg.id,
      previousHash,
      timestamp: Date.now(),
      signerId: signature.signerId,
      signature: signature.signature,
    };

    chain.push(link);
    this.hashChains.set(pkg.senderId, chain);
  }

  /**
   * Get hash chain for an agent
   */
  getHashChain(agentId: string): HashChainLink[] {
    return this.hashChains.get(agentId) || [];
  }

  /**
   * Verify hash chain integrity
   */
  verifyHashChain(agentId: string): boolean {
    const chain = this.hashChains.get(agentId);
    if (!chain || chain.length === 0) {
      return true; // Empty chain is valid
    }

    for (let i = 0; i < chain.length; i++) {
      const link = chain[i];

      // Verify previous hash matches
      if (i > 0) {
        if (link.previousHash !== chain[i - 1].linkHash) {
          return false;
        }
      } else {
        // First link should have genesis hash
        if (link.previousHash !== 'genesis') {
          return false;
        }
      }

      // Recompute link hash
      const linkData = `${link.previousHash}:${link.packageId}:${link.signature}`;
      const expectedHash = createHash('sha256').update(linkData).digest('hex');

      if (link.linkHash !== expectedHash) {
        return false;
      }
    }

    return true;
  }

  /**
   * Rotate signing key
   */
  rotateSigningKey(): string {
    const newKeyId = this.generateKeyId();
    const newSecret = this.generateSecret();
    this.signingKeys.set(newKeyId, newSecret);

    // Mark old keys for potential cleanup
    // (In production, you'd want to keep old keys for verification)

    return newKeyId;
  }

  /**
   * Get signature for package
   */
  getSignature(packageId: string): PackageSignature | undefined {
    return this.signatures.get(packageId);
  }

  /**
   * Add signing key (for asymmetric keys)
   */
  addSigningKey(keyId: string, secret: string): void {
    this.signingKeys.set(keyId, secret);
  }

  /**
   * Remove expired signatures
   */
  cleanupExpiredSignatures(): number {
    let count = 0;
    const now = Date.now();

    for (const [packageId, signature] of this.signatures.entries()) {
      if (signature.expiresAt && signature.expiresAt < now) {
        this.signatures.delete(packageId);
        count++;
      }
    }

    return count;
  }

  /**
   * Get signing statistics
   */
  getStats(): {
    totalSignatures: number;
    activeKeys: number;
    hashChains: number;
  } {
    let activeKeys = 0;
    for (const [keyId, secret] of this.signingKeys.entries()) {
      if (secret) activeKeys++;
    }

    return {
      totalSignatures: this.signatures.size,
      activeKeys,
      hashChains: this.hashChains.size,
    };
  }

  /**
   * Clear all signatures and hash chains
   */
  clear(): void {
    this.signatures.clear();
    this.hashChains.clear();
  }
}

// ============================================================================
// A2A Package System Extension with Signing
// ============================================================================

import { A2APackageSystem, type A2APackageSystemConfig } from './communication.js';

/**
 * Extended A2A Package System with cryptographic signing
 */
export class A2APackageSystemWithSigning extends A2APackageSystem {
  private signingService: A2APackageSigningService;

  constructor(
    config?: Partial<A2APackageSystemConfig>,
    signingConfig?: Partial<A2ASigningConfig>
  ) {
    super(config);
    this.signingService = new A2APackageSigningService(signingConfig);
  }

  /**
   * Create package with automatic signing
   */
  override async createPackage<T>(
    senderId: string,
    receiverId: string,
    type: string,
    payload: T,
    options?: {
      privacyLevel?: import('./types.js').PrivacyLevel;
      layer?: import('./types.js').SubsumptionLayer;
      parentIds?: string[];
      dpMetadata?: import('./communication.js').PackageMetadata;
      sign?: boolean;
      signerId?: string;
    }
  ): Promise<import('./types.js').A2APackage<T>> {
    // Create base package
    const pkg = await super.createPackage(
      senderId,
      receiverId,
      type,
      payload,
      options
    );

    // Sign if enabled (default true)
    if (options?.sign !== false) {
      await this.signingService.signPackage(pkg, {
        signerId: options?.signerId || senderId,
      });
    }

    return pkg;
  }

  /**
   * Verify package signature
   */
  async verifySignature<T>(
    pkg: import('./types.js').A2APackage<T>
  ): Promise<SignatureVerificationResult> {
    return this.signingService.verifySignature(pkg);
  }

  /**
   * Get signing service for advanced operations
   */
  getSigningService(): A2APackageSigningService {
    return this.signingService;
  }

  /**
   * Rotate signing keys
   */
  rotateSigningKey(): string {
    return this.signingService.rotateSigningKey();
  }

  /**
   * Get hash chain for an agent
   */
  getHashChain(agentId: string): HashChainLink[] {
    return this.signingService.getHashChain(agentId);
  }

  /**
   * Verify hash chain integrity
   */
  verifyHashChain(agentId: string): boolean {
    return this.signingService.verifyHashChain(agentId);
  }

  /**
   * Cleanup expired signatures
   */
  cleanupExpiredSignatures(): number {
    return this.signingService.cleanupExpiredSignatures();
  }
}

// ============================================================================
// Factory Functions
// ============================================================================

export function createA2ASigningService(
  config?: Partial<A2ASigningConfig>
): A2APackageSigningService {
  return new A2APackageSigningService(config);
}

export function createA2APackageSystemWithSigning(
  systemConfig?: Partial<A2APackageSystemConfig>,
  signingConfig?: Partial<A2ASigningConfig>
): A2APackageSystemWithSigning {
  return new A2APackageSystemWithSigning(systemConfig, signingConfig);
}
