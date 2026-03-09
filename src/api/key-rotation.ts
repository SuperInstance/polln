/**
 * Key Rotation Manager for JWT Signing Keys
 *
 * Provides production-ready key rotation with:
 * - Multiple active keys with versioning
 * - Automatic rotation on schedule
 * - Graceful transition period (old keys still valid)
 * - Integration with JWT signing/verification
 * - Audit logging for all key operations
 */

import { createHash, randomBytes, generateKeyPairSync } from 'crypto';
import { sign, verify, Algorithm } from 'jsonwebtoken';
import { v4 as uuidv4 } from 'uuid';

// ============================================================================
// Types
// ============================================================================

export interface KeyMetadata {
  /** Unique key identifier */
  keyId: string;
  /** Key version (monotonically increasing) */
  version: number;
  /** When the key was created */
  createdAt: number;
  /** When the key becomes active for signing */
  activeAt: number;
  /** When the key expires (no longer valid for verification) */
  expiresAt: number;
  /** Key status */
  status: KeyStatus;
  /** Algorithm used for this key */
  algorithm: Algorithm;
  /** Key size in bits (for asymmetric keys) */
  keySize?: number;
}

export type KeyStatus = 'pending' | 'active' | 'deprecated' | 'expired' | 'compromised';

export interface KeyRotationConfig {
  /** Number of keys to keep in rotation history */
  keyHistorySize: number;
  /** Grace period before old keys are fully deprecated (milliseconds) */
  gracePeriodMs: number;
  /** Key lifetime before expiration (milliseconds) */
  keyLifetimeMs: number;
  /** Rotation interval (0 = manual only) */
  rotationIntervalMs: number;
  /** Default algorithm for new keys */
  defaultAlgorithm: Algorithm;
  /** Whether to use asymmetric keys (RSA) */
  useAsymmetric: boolean;
  /** RSA key size (if using asymmetric) */
  rsaKeySize: number;
}

export interface KeyRotationStats {
  /** Total keys in history */
  totalKeys: number;
  /** Currently active key ID */
  activeKeyId: string;
  /** Keys by status */
  keysByStatus: Partial<Record<KeyStatus, number>>;
  /** Last rotation time */
  lastRotationAt?: number;
  /** Next scheduled rotation */
  nextRotationAt?: number;
}

export interface KeyWithSecret extends KeyMetadata {
  /** The secret key (for signing) */
  secret: string;
  /** Public key (for asymmetric verification) */
  publicKey?: string;
}

// ============================================================================
// Key Rotation Manager
// ============================================================================

export class KeyRotationManager {
  private keys: Map<string, KeyWithSecret> = new Map();
  private currentKeyId: string | null = null;
  private rotationTimer: NodeJS.Timeout | null = null;
  private config: KeyRotationConfig;
  private auditLog: ((event: AuditEvent) => void) | null = null;

  constructor(config?: Partial<KeyRotationConfig>) {
    this.config = {
      keyHistorySize: 5,
      gracePeriodMs: 24 * 60 * 60 * 1000, // 1 day
      keyLifetimeMs: 90 * 24 * 60 * 60 * 1000, // 90 days
      rotationIntervalMs: 30 * 24 * 60 * 60 * 1000, // 30 days
      defaultAlgorithm: 'HS256',
      useAsymmetric: false,
      rsaKeySize: 2048,
      ...config,
    };

    // Initialize with first key
    this.initialize();
  }

  /**
   * Initialize the key manager with the first key
   */
  private async initialize(): Promise<void> {
    const initialKey = this.generateKey();
    this.keys.set(initialKey.keyId, initialKey);
    this.currentKeyId = initialKey.keyId;

    // Start rotation timer if interval is set
    if (this.config.rotationIntervalMs > 0) {
      this.scheduleRotation(this.config.rotationIntervalMs);
    }

    this.logAudit({
      category: 'key_management',
      type: 'key_manager_initialized',
      severity: 'INFO',
      details: {
        keyId: initialKey.keyId,
        algorithm: initialKey.algorithm,
        useAsymmetric: this.config.useAsymmetric,
      },
    });
  }

  /**
   * Generate a new signing key
   */
  private generateKey(): KeyWithSecret {
    const keyId = this.generateKeyId();
    const now = Date.now();

    let secret: string;
    let publicKey: string | undefined;
    let algorithm: Algorithm;

    if (this.config.useAsymmetric) {
      // Generate RSA key pair
      algorithm = 'RS256';
      const { privateKey, publicKey: pubKey } = generateKeyPairSync('rsa', {
        modulusLength: this.config.rsaKeySize,
      });
      secret = privateKey.export({ type: 'pkcs8', format: 'pem' }).toString();
      publicKey = pubKey.export({ type: 'spki', format: 'pem' }).toString();
    } else {
      // Generate symmetric secret
      algorithm = this.config.defaultAlgorithm;
      secret = randomBytes(64).toString('base64');
    }

    const key: KeyWithSecret = {
      keyId,
      version: this.keys.size + 1,
      createdAt: now,
      activeAt: now + this.config.gracePeriodMs, // Active after grace period
      expiresAt: now + this.config.keyLifetimeMs,
      status: 'pending',
      algorithm,
      keySize: this.config.rsaKeySize,
      secret,
      publicKey,
    };

    return key;
  }

  /**
   * Generate a unique key ID
   */
  private generateKeyId(): string {
    return createHash('sha256')
      .update(`key-${Date.now()}-${randomBytes(16).toString('hex')}`)
      .digest('hex')
      .substring(0, 16);
  }

  /**
   * Schedule automatic key rotation
   */
  private scheduleRotation(intervalMs: number): void {
    if (this.rotationTimer) {
      clearTimeout(this.rotationTimer);
    }

    this.rotationTimer = setTimeout(async () => {
      try {
        await this.rotate();
      } catch (error) {
        console.error('[KeyRotationManager] Rotation failed:', error);
        // Reschedule even on failure
        this.scheduleRotation(this.config.rotationIntervalMs);
      }
    }, intervalMs);
  }

  /**
   * Perform manual key rotation
   */
  async rotate(options?: {
    force?: boolean;
    reason?: string;
    compromisedKeyId?: string;
  }): Promise<string> {
    const newKey = this.generateKey();

    // Mark old current key as deprecated
    if (this.currentKeyId) {
      const oldKey = this.keys.get(this.currentKeyId);
      if (oldKey) {
        oldKey.status = 'deprecated';

        // Handle compromised key
        if (options?.compromisedKeyId === this.currentKeyId) {
          oldKey.status = 'compromised';
          oldKey.expiresAt = Date.now(); // Immediately expire
        }
      }
    }

    // Add new key
    this.keys.set(newKey.keyId, newKey);
    this.currentKeyId = newKey.keyId;

    // Clean up old keys beyond history size (after adding new key)
    await this.cleanupOldKeys();

    // Schedule next rotation
    if (this.config.rotationIntervalMs > 0) {
      this.scheduleRotation(this.config.rotationIntervalMs);
    }

    this.logAudit({
      category: 'key_management',
      type: 'key_rotated',
      severity: 'INFO',
      details: {
        newKeyId: newKey.keyId,
        previousKeyId: this.keys.get(this.currentKeyId)?.keyId,
        reason: options?.reason || 'scheduled_rotation',
        forced: options?.force || false,
      },
    });

    return newKey.keyId;
  }

  /**
   * Get the current active key for signing
   */
  getCurrentKey(): { keyId: string; secret: string; algorithm: Algorithm } | null {
    if (!this.currentKeyId) {
      return null;
    }

    const key = this.keys.get(this.currentKeyId);
    if (!key) {
      return null;
    }

    return {
      keyId: key.keyId,
      secret: key.secret,
      algorithm: key.algorithm,
    };
  }

  /**
   * Get a key by ID (for verification)
   */
  getKey(keyId: string): { secret: string; publicKey?: string; algorithm: Algorithm } | null {
    const key = this.keys.get(keyId);
    if (!key) {
      return null;
    }

    // Check if key is expired
    if (key.status === 'expired' || Date.now() > key.expiresAt) {
      return null;
    }

    return {
      secret: key.secret,
      publicKey: key.publicKey,
      algorithm: key.algorithm,
    };
  }

  /**
   * Sign a JWT with the current key
   */
  sign(
    payload: Record<string, unknown>,
    options?: {
      expiresIn?: string | number;
      issuer?: string;
      audience?: string;
    }
  ): string {
    const current = this.getCurrentKey();
    if (!current) {
      throw new Error('No active key available for signing');
    }

    const now = Math.floor(Date.now() / 1000);

    const signOptions: {
      algorithm: Algorithm;
      expiresIn: string | number;
      issuer?: string;
      audience?: string;
      header: Record<string, string>;
    } = {
      algorithm: current.algorithm,
      expiresIn: options?.expiresIn || 3600, // 1 hour default
      header: { kid: current.keyId }, // Key ID in header
    };

    if (options?.issuer) {
      signOptions.issuer = options.issuer;
    }
    if (options?.audience) {
      signOptions.audience = options.audience;
    }

    return sign(
      {
        ...payload,
        iat: now,
      },
      current.secret,
      signOptions
    );
  }

  /**
   * Verify a JWT token, checking all valid keys
   */
  verify(
    token: string,
    options?: {
      issuer?: string;
      audience?: string;
    }
  ): { valid: boolean; payload?: Record<string, unknown>; keyId?: string; error?: string } {
    // Get key ID from token header (without verifying)
    const decodedHeader = this.decodeHeader(token);
    const keyId = decodedHeader?.kid;

    if (keyId) {
      // Try specific key first
      const key = this.getKey(keyId);
      if (key) {
        try {
          const payload = verify(token, key.secret, {
            algorithms: [key.algorithm],
            issuer: options?.issuer,
            audience: options?.audience,
          }) as Record<string, unknown>;

          return { valid: true, payload, keyId };
        } catch (error) {
          // Try other keys
        }
      }
    }

    // Try all active and deprecated keys (grace period)
    for (const [id, key] of this.keys.entries()) {
      if (key.status === 'expired' || key.status === 'compromised') {
        continue;
      }

      try {
        const payload = verify(token, key.secret, {
          algorithms: [key.algorithm],
          issuer: options?.issuer,
          audience: options?.audience,
        }) as Record<string, unknown>;

        return { valid: true, payload, keyId: id };
      } catch {
        // Continue to next key
      }
    }

    return { valid: false, error: 'No valid key found for token' };
  }

  /**
   * Decode JWT header without verification
   */
  private decodeHeader(token: string): { kid?: string } | null {
    try {
      const header = token.split('.')[0];
      const decoded = Buffer.from(header, 'base64url').toString('utf-8');
      return JSON.parse(decoded) as { kid?: string };
    } catch {
      return null;
    }
  }

  /**
   * Mark a key as compromised
   */
  async compromiseKey(keyId: string, reason: string): Promise<void> {
    const key = this.keys.get(keyId);
    if (!key) {
      throw new Error(`Key ${keyId} not found`);
    }

    key.status = 'compromised';
    key.expiresAt = Date.now(); // Immediately expire

    // If this is the current key, force rotation
    if (this.currentKeyId === keyId) {
      await this.rotate({ reason: `Compromised key: ${reason}`, compromisedKeyId: keyId });
    }

    this.logAudit({
      category: 'key_management',
      type: 'key_compromised',
      severity: 'WARNING',
      details: {
        keyId,
        reason,
        wasCurrentKey: this.currentKeyId === keyId,
      },
    });
  }

  /**
   * Get key metadata without secret
   */
  getKeyInfo(keyId: string): KeyMetadata | null {
    const key = this.keys.get(keyId);
    if (!key) {
      return null;
    }

    const { secret, publicKey, ...info } = key;
    return info;
  }

  /**
   * Get all keys metadata (without secrets)
   */
  getAllKeys(): KeyMetadata[] {
    return Array.from(this.keys.values()).map(key => {
      const { secret, publicKey, ...info } = key;
      return info;
    }).sort((a, b) => b.createdAt - a.createdAt);
  }

  /**
   * Get rotation statistics
   */
  getStats(): KeyRotationStats {
    const keysByStatus: Partial<Record<KeyStatus, number>> = {};

    for (const key of this.keys.values()) {
      keysByStatus[key.status] = (keysByStatus[key.status] || 0) + 1;
    }

    const activeKeys = Array.from(this.keys.values()).filter(
      k => k.status === 'active' || k.status === 'deprecated'
    );

    // Find newest deprecated key for last rotation time
    const lastRotation = activeKeys
      .filter(k => k.status === 'deprecated')
      .sort((a, b) => b.createdAt - a.createdAt)[0];

    return {
      totalKeys: this.keys.size,
      activeKeyId: this.currentKeyId || '',
      keysByStatus,
      lastRotationAt: lastRotation?.createdAt,
      nextRotationAt: this.rotationTimer ? Date.now() + this.config.rotationIntervalMs : undefined,
    };
  }

  /**
   * Clean up old keys beyond history size
   */
  private async cleanupOldKeys(): Promise<void> {
    const now = Date.now();
    const keysArray = Array.from(this.keys.entries())
      .sort((a, b) => b[1].createdAt - a[1].createdAt);

    // Find keys that can be safely deleted
    const keysToRemove: string[] = [];
    const eligibleKeys = keysArray.slice(this.config.keyHistorySize);

    for (const [keyId, key] of eligibleKeys) {
      // Don't delete if it's the current key
      if (keyId === this.currentKeyId) {
        continue;
      }

      // Only delete if grace period has passed
      if (now >= key.activeAt) {
        keysToRemove.push(keyId);
      }
    }

    // Delete the keys
    for (const keyId of keysToRemove) {
      this.keys.delete(keyId);
      this.logAudit({
        category: 'key_management',
        type: 'key_deleted',
        severity: 'INFO',
        details: { keyId },
      });
    }
  }

  /**
   * Manually expire a key
   */
  expireKey(keyId: string): boolean {
    const key = this.keys.get(keyId);
    if (!key) {
      return false;
    }

    key.status = 'expired';
    key.expiresAt = Date.now();

    this.logAudit({
      category: 'key_management',
      type: 'key_expired',
      severity: 'INFO',
      details: { keyId },
    });

    return true;
  }

  /**
   * Set audit log callback
   */
  setAuditLogger(logger: (event: AuditEvent) => void): void {
    this.auditLog = logger;
  }

  /**
   * Log audit event
   */
  private logAudit(event: AuditEvent): void {
    if (this.auditLog) {
      this.auditLog({
        ...event,
        timestamp: Date.now(),
      });
    }
  }

  /**
   * Shutdown and cleanup
   */
  async shutdown(): Promise<void> {
    if (this.rotationTimer) {
      clearTimeout(this.rotationTimer);
      this.rotationTimer = null;
    }

    this.logAudit({
      category: 'key_management',
      type: 'key_manager_shutdown',
      severity: 'INFO',
      details: {
        totalKeys: this.keys.size,
        activeKeyId: this.currentKeyId,
      },
    });
  }
}

// ============================================================================
// Types for Audit Events
// ============================================================================

export interface AuditEvent {
  category: string;
  type: string;
  severity: 'INFO' | 'WARNING' | 'ERROR';
  timestamp: number;
  details?: Record<string, unknown>;
}

// ============================================================================
// Factory Function
// ============================================================================

export function createKeyRotationManager(
  config?: Partial<KeyRotationConfig>
): KeyRotationManager {
  return new KeyRotationManager(config);
}

// ============================================================================
// Integration with AuthenticationMiddleware
// ============================================================================

import { AuthenticationMiddleware } from './middleware.js';
import type { JWTConfig } from './middleware.js';

/**
 * Extended authentication middleware with key rotation support
 */
export class AuthenticationMiddlewareWithKeyRotation extends AuthenticationMiddleware {
  private keyManager: KeyRotationManager;

  constructor(
    keyRotationConfig?: Partial<KeyRotationConfig>,
    jwtConfig?: Partial<JWTConfig>
  ) {
    // Create with empty config (keys will be managed by rotation)
    super({ ...jwtConfig, secret: 'placeholder' }); // Placeholder, will use keyManager

    this.keyManager = new KeyRotationManager(keyRotationConfig);

    // Override token generation to use key rotation
    this.generateTokenPair = this.generateTokenPairWithRotation.bind(this);
  }

  /**
   * Generate token pair using current key from rotation manager
   */
  private generateTokenPairWithRotation(
    gardenerId: string,
    permissions: import('./types.js').Permission[],
    additionalClaims?: Record<string, unknown>
  ): import('./middleware.js').TokenPair {
    const now = Math.floor(Date.now() / 1000);

    // Sign with current key
    const accessToken = this.keyManager.sign(
      {
        sub: gardenerId,
        permissions,
        type: 'access',
        ...additionalClaims,
      },
      {
        expiresIn: this.getJwtConfig().accessTokenExpiry,
        issuer: this.getJwtConfig().issuer,
        audience: this.getJwtConfig().audience,
      }
    );

    // For refresh tokens, also use key rotation
    const refreshTokenId = uuidv4();
    const refreshToken = this.keyManager.sign(
      {
        sub: gardenerId,
        type: 'refresh',
        jti: refreshTokenId,
      },
      {
        expiresIn: this.getJwtConfig().refreshTokenExpiry,
        issuer: this.getJwtConfig().issuer,
        audience: this.getJwtConfig().audience,
      }
    );

    // Store refresh token
    (this as any).refreshTokens.set(refreshTokenId, {
      gardenerId,
      expiresAt: now + this.getJwtConfig().refreshTokenExpiry,
    });

    return {
      accessToken,
      refreshToken,
      expiresAt: now + this.getJwtConfig().accessTokenExpiry,
    };
  }

  /**
   * Validate access token using key rotation manager
   */
  override validateAccessToken(token: string): {
    gardenerId: string;
    permissions: import('./types.js').Permission[];
  } | null {
    const result = this.keyManager.verify(token, {
      issuer: this.getJwtConfig().issuer,
      audience: this.getJwtConfig().audience,
    });

    if (!result.valid || !result.payload) {
      return null;
    }

    const { sub, permissions, type } = result.payload as {
      sub?: string;
      permissions?: import('./types.js').Permission[];
      type?: string;
    };

    if (type !== 'access' || !sub) {
      return null;
    }

    return {
      gardenerId: sub,
      permissions: permissions || [],
    };
  }

  /**
   * Force key rotation
   */
  async rotateKeys(reason?: string): Promise<string> {
    return this.keyManager.rotate({ reason });
  }

  /**
   * Get key rotation statistics
   */
  getKeyStats(): KeyRotationStats {
    return this.keyManager.getStats();
  }

  /**
   * Get key manager for advanced operations
   */
  getKeyManager(): KeyRotationManager {
    return this.keyManager;
  }

  /**
   * Shutdown and cleanup
   */
  async shutdown(): Promise<void> {
    await this.keyManager.shutdown();
  }

  private getJwtConfig(): JWTConfig {
    return (this as any).jwtConfig as JWTConfig;
  }
}
