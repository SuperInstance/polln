/**
 * StorageInstance - Implementation for persistent storage management instances
 *
 * Represents storage systems that can store, retrieve, and manage data
 * with various storage backends and access patterns.
 */

import {
  BaseSuperInstance, InstanceType, InstanceState, InstanceCapability,
  CellPosition, InstanceConfiguration, InstancePermissions,
  InstanceMessage, InstanceMessageResponse, InstanceStatus, InstanceMetrics,
  Connection, ConnectionType, InstanceSnapshot, ValidationResult
} from '../types/base';

/**
 * StorageType - Types of storage backends
 */
export enum StorageType {
  MEMORY = 'memory',
  FILE_SYSTEM = 'file_system',
  DATABASE = 'database',
  OBJECT_STORAGE = 'object_storage',
  KEY_VALUE = 'key_value',
  CACHE = 'cache',
  ARCHIVE = 'archive'
}

/**
 * StorageFormat - Data storage formats
 */
export enum StorageFormat {
  JSON = 'json',
  BINARY = 'binary',
  TEXT = 'text',
  CSV = 'csv',
  PARQUET = 'parquet',
  AVRO = 'avro',
  PROTOBUF = 'protobuf'
}

/**
 * CompressionAlgorithm - Compression algorithms
 */
export enum CompressionAlgorithm {
  NONE = 'none',
  GZIP = 'gzip',
  DEFLATE = 'deflate',
  BROTLI = 'brotli',
  LZ4 = 'lz4',
  SNAPPY = 'snappy'
}

/**
 * EncryptionAlgorithm - Encryption algorithms
 */
export enum EncryptionAlgorithm {
  NONE = 'none',
  AES256 = 'aes256',
  CHACHA20 = 'chacha20',
  RSA = 'rsa'
}

/**
 * StoragePolicy - Storage policy configuration
 */
export interface StoragePolicy {
  retentionPeriod: number; // Days to retain data
  backupFrequency: number; // Hours between backups
  replicationFactor: number; // Number of replicas
  compression: CompressionAlgorithm;
  encryption: EncryptionAlgorithm;
  versioning: boolean; // Enable versioning
  deduplication: boolean; // Enable deduplication
}

/**
 * StorageStats - Storage statistics
 */
export interface StorageStats {
  totalSize: number; // Total storage used in bytes
  objectCount: number; // Number of stored objects
  availableSpace: number; // Available space in bytes
  readOperations: number; // Number of read operations
  writeOperations: number; // Number of write operations
  deleteOperations: number; // Number of delete operations
  errorRate: number; // Error rate (0-1)
  averageLatency: number; // Average operation latency in ms
}

/**
 * StorageObject - Object stored in storage
 */
export interface StorageObject {
  key: string;
  data: any;
  metadata: StorageMetadata;
  size: number; // Size in bytes
  createdAt: number;
  updatedAt: number;
  expiresAt?: number; // Expiration timestamp
  version?: string; // Version identifier
}

/**
 * StorageMetadata - Metadata for stored objects
 */
export interface StorageMetadata {
  contentType: string;
  encoding: string;
  compression: CompressionAlgorithm;
  encryption: EncryptionAlgorithm;
  checksum: string;
  tags: Record<string, string>;
  customMetadata: Record<string, any>;
}

/**
 * QueryCondition - Condition for querying storage
 */
export interface QueryCondition {
  field: string;
  operator: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'contains' | 'startsWith' | 'endsWith' | 'in' | 'notIn';
  value: any;
}

/**
 * StorageQuery - Query for searching storage
 */
export interface StorageQuery {
  conditions: QueryCondition[];
  limit?: number;
  offset?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

/**
 * QueryResult - Result of a storage query
 */
export interface QueryResult {
  objects: StorageObject[];
  totalCount: number;
  queryTime: number; // Query execution time in ms
  hasMore: boolean;
}

/**
 * BackupConfig - Backup configuration
 */
export interface BackupConfig {
  enabled: boolean;
  frequency: number; // Hours between backups
  retention: number; // Days to keep backups
  location: string; // Backup location
  compression: CompressionAlgorithm;
  encryption: EncryptionAlgorithm;
}

/**
 * StorageInstance - Interface for storage instances
 */
export interface StorageInstance {
  type: InstanceType.OBJECT_STORAGE | InstanceType.FILE_SYSTEM | InstanceType.KEY_VALUE_STORE | InstanceType.CACHE;

  // Storage-specific properties
  storageType: StorageType;
  storageFormat: StorageFormat;
  storagePolicy: StoragePolicy;
  backupConfig: BackupConfig;
  basePath: string; // Base path for storage

  // Core storage operations
  put(key: string, data: any, metadata?: Partial<StorageMetadata>): Promise<StorageObject>;
  get(key: string): Promise<StorageObject | null>;
  delete(key: string): Promise<boolean>;
  exists(key: string): Promise<boolean>;

  // Batch operations
  putMany(objects: Array<{ key: string; data: any; metadata?: Partial<StorageMetadata> }>): Promise<StorageObject[]>;
  getMany(keys: string[]): Promise<(StorageObject | null)[]>;
  deleteMany(keys: string[]): Promise<boolean[]>;

  // Query operations
  query(query: StorageQuery): Promise<QueryResult>;
  search(text: string, fields?: string[]): Promise<QueryResult>;

  // Management operations
  list(prefix?: string, limit?: number): Promise<string[]>;
  clear(): Promise<void>;
  compact(): Promise<void>; // Optimize storage

  // Backup and recovery
  backup(): Promise<string>; // Returns backup ID
  restore(backupId: string): Promise<void>;
  listBackups(): Promise<string[]>;

  // Monitoring
  getStats(): StorageStats;
  getHealth(): { healthy: boolean; issues: string[] };
}

/**
 * ConcreteStorageInstance - Implementation of StorageInstance
 */
export class ConcreteStorageInstance extends BaseSuperInstance implements StorageInstance {
  type: InstanceType.OBJECT_STORAGE | InstanceType.FILE_SYSTEM | InstanceType.KEY_VALUE_STORE | InstanceType.CACHE;
  storageType: StorageType;
  storageFormat: StorageFormat;
  storagePolicy: StoragePolicy;
  backupConfig: BackupConfig;
  basePath: string;

  private connections: Map<string, Connection> = new Map();
  private children: SuperInstance[] = [];
  private parents: SuperInstance[] = [];
  private storage: Map<string, StorageObject> = new Map();
  private backups: Map<string, Map<string, StorageObject>> = new Map();
  private stats: StorageStats = {
    totalSize: 0,
    objectCount: 0,
    availableSpace: 1024 * 1024 * 1024, // 1GB default
    readOperations: 0,
    writeOperations: 0,
    deleteOperations: 0,
    errorRate: 0,
    averageLatency: 0
  };
  private totalLatency: number = 0;
  private totalOperations: number = 0;

  constructor(config: {
    id: string;
    name: string;
    description: string;
    cellPosition: CellPosition;
    spreadsheetId: string;
    storageType: StorageType;
    storageFormat?: StorageFormat;
    storagePolicy?: Partial<StoragePolicy>;
    backupConfig?: Partial<BackupConfig>;
    basePath?: string;
    configuration?: Partial<InstanceConfiguration>;
  }) {
    const instanceType = this.mapStorageTypeToInstanceType(config.storageType);

    super({
      id: config.id,
      type: instanceType,
      name: config.name,
      description: config.description,
      cellPosition: config.cellPosition,
      spreadsheetId: config.spreadsheetId,
      configuration: config.configuration,
      capabilities: ['storage', 'read', 'write', 'persistence']
    });

    this.type = instanceType;
    this.storageType = config.storageType;
    this.storageFormat = config.storageFormat || StorageFormat.JSON;
    this.storagePolicy = {
      retentionPeriod: 30, // 30 days
      backupFrequency: 24, // 24 hours
      replicationFactor: 1,
      compression: CompressionAlgorithm.NONE,
      encryption: EncryptionAlgorithm.NONE,
      versioning: false,
      deduplication: false,
      ...config.storagePolicy
    };
    this.backupConfig = {
      enabled: true,
      frequency: 24, // 24 hours
      retention: 7, // 7 days
      location: './backups',
      compression: CompressionAlgorithm.GZIP,
      encryption: EncryptionAlgorithm.NONE,
      ...config.backupConfig
    };
    this.basePath = config.basePath || './storage';
  }

  async initialize(config?: Partial<InstanceConfiguration>): Promise<void> {
    if (config) {
      this.configuration = { ...this.configuration, ...config };
    }

    const validation = this.validateConfiguration(this.configuration);
    if (!validation.valid) {
      throw new Error(`Configuration validation failed: ${validation.errors.map(e => e.message).join(', ')}`);
    }

    // Initialize storage based on type
    await this.initializeStorage();

    // Start backup scheduler if enabled
    if (this.backupConfig.enabled) {
      this.startBackupScheduler();
    }

    this.updateState(InstanceState.INITIALIZED);
  }

  async activate(): Promise<void> {
    if (this.state !== InstanceState.INITIALIZED && this.state !== InstanceState.IDLE) {
      throw new Error(`Cannot activate from state: ${this.state}`);
    }
    this.updateState(InstanceState.RUNNING);
  }

  async deactivate(): Promise<void> {
    if (this.state !== InstanceState.RUNNING && this.state !== InstanceState.PROCESSING) {
      throw new Error(`Cannot deactivate from state: ${this.state}`);
    }
    this.updateState(InstanceState.IDLE);
  }

  async terminate(): Promise<void> {
    // Clean up connections
    this.connections.clear();
    this.children = [];
    this.parents = [];

    // Clear storage
    this.storage.clear();
    this.backups.clear();

    // Reset stats
    this.stats = {
      totalSize: 0,
      objectCount: 0,
      availableSpace: 1024 * 1024 * 1024,
      readOperations: 0,
      writeOperations: 0,
      deleteOperations: 0,
      errorRate: 0,
      averageLatency: 0
    };
    this.totalLatency = 0;
    this.totalOperations = 0;

    this.updateState(InstanceState.TERMINATED);
  }

  async serialize(): Promise<InstanceSnapshot> {
    // Serialize storage data
    const storageData: Record<string, StorageObject> = {};
    for (const [key, obj] of this.storage) {
      storageData[key] = obj;
    }

    return {
      id: this.id,
      type: this.type,
      state: this.state,
      data: {
        storageType: this.storageType,
        storageFormat: this.storageFormat,
        storagePolicy: this.storagePolicy,
        backupConfig: this.backupConfig,
        basePath: this.basePath,
        stats: this.stats,
        storageData
      },
      configuration: this.configuration,
      timestamp: Date.now(),
      version: '1.0.0'
    };
  }

  async deserialize(snapshot: InstanceSnapshot): Promise<void> {
    if (![
      InstanceType.OBJECT_STORAGE,
      InstanceType.FILE_SYSTEM,
      InstanceType.KEY_VALUE_STORE,
      InstanceType.CACHE
    ].includes(snapshot.type as any)) {
      throw new Error(`Cannot deserialize snapshot of type ${snapshot.type} into StorageInstance`);
    }

    const data = snapshot.data;
    this.type = snapshot.type as any;
    this.storageType = data.storageType;
    this.storageFormat = data.storageFormat;
    this.storagePolicy = data.storagePolicy;
    this.backupConfig = data.backupConfig;
    this.basePath = data.basePath;
    this.stats = data.stats;

    // Restore storage data
    if (data.storageData) {
      this.storage.clear();
      for (const [key, obj] of Object.entries(data.storageData)) {
        this.storage.set(key, obj as StorageObject);
      }
    }

    this.configuration = snapshot.configuration;
    this.updateState(snapshot.state as InstanceState);
  }

  async sendMessage(message: InstanceMessage): Promise<InstanceMessageResponse> {
    try {
      await this.receiveMessage(message);
      return {
        messageId: message.id,
        status: 'success',
        payload: { received: true, timestamp: Date.now() }
      };
    } catch (error) {
      return {
        messageId: message.id,
        status: 'error',
        error: {
          code: 'MESSAGE_PROCESSING_ERROR',
          message: error instanceof Error ? error.message : 'Unknown error',
          recoverable: true,
          context: { messageType: message.type }
        }
      };
    }
  }

  async receiveMessage(message: InstanceMessage): Promise<void> {
    switch (message.type) {
      case 'data':
        await this.handleDataMessage(message);
        break;
      case 'command':
        await this.handleCommandMessage(message);
        break;
      case 'query':
        await this.handleQueryMessage(message);
        break;
      default:
        console.warn(`Unhandled message type: ${message.type}`);
    }
  }

  async getStatus(): Promise<InstanceStatus> {
    const health = this.getHealth();
    return {
      state: this.state,
      health: health.healthy ? 'healthy' : 'unhealthy',
      uptime: Date.now() - this.createdAt,
      warnings: health.issues,
      lastError: undefined
    };
  }

  async getMetrics(): Promise<InstanceMetrics> {
    return {
      cpuUsage: 0, // Storage instances typically don't use much CPU
      memoryUsage: this.stats.totalSize / 1024 / 1024, // Convert to MB
      diskUsage: this.stats.totalSize / 1024 / 1024, // Convert to MB
      networkIn: 0,
      networkOut: 0,
      requestCount: this.totalOperations,
      errorRate: this.stats.errorRate,
      latency: {
        p50: this.stats.averageLatency,
        p90: this.stats.averageLatency * 1.5,
        p95: this.stats.averageLatency * 2,
        p99: this.stats.averageLatency * 3,
        max: this.stats.averageLatency * 5
      }
    };
  }

  async getChildren(): Promise<SuperInstance[]> {
    return [...this.children];
  }

  async getParents(): Promise<SuperInstance[]> {
    return [...this.parents];
  }

  async getNeighbors(): Promise<SuperInstance[]> {
    // In a real implementation, this would query the spreadsheet for neighboring cells
    return [];
  }

  async connectTo(target: SuperInstance, connectionType: ConnectionType): Promise<Connection> {
    const connection: Connection = {
      id: `${this.id}-${target.id}-${Date.now()}`,
      source: this.id,
      target: target.id,
      type: connectionType,
      bandwidth: 1000, // 1 Gbps
      latency: 10, // 10ms
      reliability: 0.99,
      establishedAt: Date.now()
    };

    this.connections.set(connection.id, connection);
    return connection;
  }

  async disconnectFrom(target: SuperInstance): Promise<void> {
    for (const [id, connection] of this.connections) {
      if (connection.target === target.id) {
        this.connections.delete(id);
        break;
      }
    }
  }

  // StorageInstance specific methods

  async put(key: string, data: any, metadata?: Partial<StorageMetadata>): Promise<StorageObject> {
    const startTime = Date.now();

    try {
      // Check if object exists and handle versioning
      const existing = this.storage.get(key);
      if (existing && this.storagePolicy.versioning) {
        // Create versioned copy
        const versionKey = `${key}.v${Date.now()}`;
        await this.putInternal(versionKey, existing.data, existing.metadata);
      }

      // Create storage object
      const storageObject = await this.putInternal(key, data, metadata);

      // Update stats
      this.updateStats('write', Date.now() - startTime, true);

      return storageObject;
    } catch (error) {
      this.updateStats('write', Date.now() - startTime, false);
      throw error;
    }
  }

  async get(key: string): Promise<StorageObject | null> {
    const startTime = Date.now();

    try {
      const object = this.storage.get(key);

      if (!object) {
        this.updateStats('read', Date.now() - startTime, true);
        return null;
      }

      // Check expiration
      if (object.expiresAt && object.expiresAt < Date.now()) {
        await this.delete(key);
        this.updateStats('read', Date.now() - startTime, true);
        return null;
      }

      this.updateStats('read', Date.now() - startTime, true);
      return object;
    } catch (error) {
      this.updateStats('read', Date.now() - startTime, false);
      throw error;
    }
  }

  async delete(key: string): Promise<boolean> {
    const startTime = Date.now();

    try {
      const existed = this.storage.delete(key);

      if (existed) {
        // Update total size
        const object = this.storage.get(key); // Get before delete for size
        if (object) {
          this.stats.totalSize -= object.size;
          this.stats.objectCount--;
        }
      }

      this.updateStats('delete', Date.now() - startTime, true);
      return existed;
    } catch (error) {
      this.updateStats('delete', Date.now() - startTime, false);
      throw error;
    }
  }

  async exists(key: string): Promise<boolean> {
    const startTime = Date.now();
    const exists = this.storage.has(key);
    this.updateStats('read', Date.now() - startTime, true);
    return exists;
  }

  async putMany(objects: Array<{ key: string; data: any; metadata?: Partial<StorageMetadata> }>): Promise<StorageObject[]> {
    const results: StorageObject[] = [];

    for (const obj of objects) {
      try {
        const result = await this.put(obj.key, obj.data, obj.metadata);
        results.push(result);
      } catch (error) {
        // Continue with other objects even if one fails
        console.error(`Failed to put object ${obj.key}:`, error);
      }
    }

    return results;
  }

  async getMany(keys: string[]): Promise<(StorageObject | null)[]> {
    const results: (StorageObject | null)[] = [];

    for (const key of keys) {
      try {
        const result = await this.get(key);
        results.push(result);
      } catch (error) {
        // Continue with other keys even if one fails
        console.error(`Failed to get object ${key}:`, error);
        results.push(null);
      }
    }

    return results;
  }

  async deleteMany(keys: string[]): Promise<boolean[]> {
    const results: boolean[] = [];

    for (const key of keys) {
      try {
        const result = await this.delete(key);
        results.push(result);
      } catch (error) {
        // Continue with other keys even if one fails
        console.error(`Failed to delete object ${key}:`, error);
        results.push(false);
      }
    }

    return results;
  }

  async query(query: StorageQuery): Promise<QueryResult> {
    const startTime = Date.now();

    try {
      let objects = Array.from(this.storage.values());

      // Apply conditions
      for (const condition of query.conditions) {
        objects = objects.filter(obj => {
          const value = this.getFieldValue(obj, condition.field);
          return this.evaluateCondition(value, condition.operator, condition.value);
        });
      }

      // Apply sorting
      if (query.sortBy) {
        objects.sort((a, b) => {
          const aValue = this.getFieldValue(a, query.sortBy!);
          const bValue = this.getFieldValue(b, query.sortBy!);

          if (query.sortOrder === 'desc') {
            return this.compareValues(bValue, aValue);
          }
          return this.compareValues(aValue, bValue);
        });
      }

      // Apply pagination
      const totalCount = objects.length;
      const offset = query.offset || 0;
      const limit = query.limit || totalCount;
      const paginatedObjects = objects.slice(offset, offset + limit);

      const queryTime = Date.now() - startTime;

      return {
        objects: paginatedObjects,
        totalCount,
        queryTime,
        hasMore: offset + limit < totalCount
      };
    } catch (error) {
      this.updateStats('read', Date.now() - startTime, false);
      throw error;
    }
  }

  async search(text: string, fields?: string[]): Promise<QueryResult> {
    const startTime = Date.now();

    try {
      const searchText = text.toLowerCase();
      const objects = Array.from(this.storage.values());
      const results: StorageObject[] = [];

      for (const obj of objects) {
        let found = false;

        // Search in specified fields or all fields
        const searchFields = fields || ['key', 'data', 'metadata.tags'];

        for (const field of searchFields) {
          const value = this.getFieldValue(obj, field);
          if (typeof value === 'string' && value.toLowerCase().includes(searchText)) {
            found = true;
            break;
          }
        }

        if (found) {
          results.push(obj);
        }
      }

      const queryTime = Date.now() - startTime;

      return {
        objects: results,
        totalCount: results.length,
        queryTime,
        hasMore: false
      };
    } catch (error) {
      this.updateStats('read', Date.now() - startTime, false);
      throw error;
    }
  }

  async list(prefix?: string, limit?: number): Promise<string[]> {
    const startTime = Date.now();

    try {
      let keys = Array.from(this.storage.keys());

      if (prefix) {
        keys = keys.filter(key => key.startsWith(prefix));
      }

      if (limit && limit > 0) {
        keys = keys.slice(0, limit);
      }

      this.updateStats('read', Date.now() - startTime, true);
      return keys;
    } catch (error) {
      this.updateStats('read', Date.now() - startTime, false);
      throw error;
    }
  }

  async clear(): Promise<void> {
    const startTime = Date.now();

    try {
      this.storage.clear();
      this.stats.totalSize = 0;
      this.stats.objectCount = 0;

      this.updateStats('delete', Date.now() - startTime, true);
    } catch (error) {
      this.updateStats('delete', Date.now() - startTime, false);
      throw error;
    }
  }

  async compact(): Promise<void> {
    const startTime = Date.now();

    try {
      // Remove expired objects
      const now = Date.now();
      const expiredKeys: string[] = [];

      for (const [key, obj] of this.storage) {
        if (obj.expiresAt && obj.expiresAt < now) {
          expiredKeys.push(key);
        }
      }

      for (const key of expiredKeys) {
        this.storage.delete(key);
      }

      // Update stats
      this.stats.objectCount = this.storage.size;
      this.stats.totalSize = Array.from(this.storage.values()).reduce((sum, obj) => sum + obj.size, 0);

      this.updateStats('write', Date.now() - startTime, true);
    } catch (error) {
      this.updateStats('write', Date.now() - startTime, false);
      throw error;
    }
  }

  async backup(): Promise<string> {
    const startTime = Date.now();

    try {
      const backupId = `backup-${Date.now()}`;
      const backupData = new Map(this.storage);

      this.backups.set(backupId, backupData);

      // Clean up old backups
      await this.cleanupOldBackups();

      this.updateStats('write', Date.now() - startTime, true);
      return backupId;
    } catch (error) {
      this.updateStats('write', Date.now() - startTime, false);
      throw error;
    }
  }

  async restore(backupId: string): Promise<void> {
    const startTime = Date.now();

    try {
      const backupData = this.backups.get(backupId);
      if (!backupData) {
        throw new Error(`Backup ${backupId} not found`);
      }

      // Restore from backup
      this.storage = new Map(backupData);

      // Update stats
      this.stats.objectCount = this.storage.size;
      this.stats.totalSize = Array.from(this.storage.values()).reduce((sum, obj) => sum + obj.size, 0);

      this.updateStats('write', Date.now() - startTime, true);
    } catch (error) {
      this.updateStats('write', Date.now() - startTime, false);
      throw error;
    }
  }

  async listBackups(): Promise<string[]> {
    return Array.from(this.backups.keys());
  }

  getStats(): StorageStats {
    return { ...this.stats };
  }

  getHealth(): { healthy: boolean; issues: string[] } {
    const issues: string[] = [];

    // Check available space
    if (this.stats.availableSpace < 1024 * 1024 * 100) { // Less than 100MB
      issues.push('Low available storage space');
    }

    // Check error rate
    if (this.stats.errorRate > 0.05) { // 5% error rate
      issues.push('High error rate detected');
    }

    // Check if storage is接近容量
    const usagePercentage = this.stats.totalSize / (this.stats.totalSize + this.stats.availableSpace);
    if (usagePercentage > 0.9) { // 90% usage
      issues.push('Storage接近容量限制');
    }

    return {
      healthy: issues.length === 0,
      issues
    };
  }

  // Private helper methods

  private mapStorageTypeToInstanceType(storageType: StorageType): InstanceType {
    switch (storageType) {
      case StorageType.FILE_SYSTEM:
        return InstanceType.FILE_SYSTEM;
      case StorageType.OBJECT_STORAGE:
        return InstanceType.OBJECT_STORAGE;
      case StorageType.KEY_VALUE:
        return InstanceType.KEY_VALUE_STORE;
      case StorageType.CACHE:
        return InstanceType.CACHE;
      default:
        return InstanceType.OBJECT_STORAGE;
    }
  }

  private async initializeStorage(): Promise<void> {
    // Initialize storage based on type
    switch (this.storageType) {
      case StorageType.MEMORY:
        // Memory storage is already initialized
        break;
      case StorageType.FILE_SYSTEM:
        // In production, this would create directories, check permissions, etc.
        console.log(`Initializing file system storage at ${this.basePath}`);
        break;
      case StorageType.DATABASE:
        // In production, this would connect to database
        console.log('Initializing database storage');
        break;
      // Other storage types would have their own initialization
    }
  }

  private startBackupScheduler(): void {
    if (!this.backupConfig.enabled) return;

    // Schedule regular backups
    const backupInterval = this.backupConfig.frequency * 60 * 60 * 1000; // Convert hours to ms

    setInterval(async () => {
      try {
        await this.backup();
        console.log(`Backup completed for storage instance ${this.id}`);
      } catch (error) {
        console.error(`Backup failed for storage instance ${this.id}:`, error);
      }
    }, backupInterval);
  }

  private async putInternal(key: string, data: any, metadata?: Partial<StorageMetadata>): Promise<StorageObject> {
    // Calculate size
    const size = this.calculateObjectSize(data);

    // Check available space
    if (size > this.stats.availableSpace) {
      throw new Error('Insufficient storage space');
    }

    // Create metadata
    const fullMetadata: StorageMetadata = {
      contentType: 'application/json',
      encoding: 'utf-8',
      compression: this.storagePolicy.compression,
      encryption: this.storagePolicy.encryption,
      checksum: this.calculateChecksum(data),
      tags: {},
      customMetadata: {},
      ...metadata
    };

    // Create storage object
    const now = Date.now();
    const storageObject: StorageObject = {
      key,
      data,
      metadata: fullMetadata,
      size,
      createdAt: now,
      updatedAt: now,
      expiresAt: this.storagePolicy.retentionPeriod > 0
        ? now + (this.storagePolicy.retentionPeriod * 24 * 60 * 60 * 1000)
        : undefined,
      version: this.storagePolicy.versioning ? `v${now}` : undefined
    };

    // Update existing object stats
    const existing = this.storage.get(key);
    if (existing) {
      this.stats.totalSize -= existing.size;
    } else {
      this.stats.objectCount++;
    }

    // Store object
    this.storage.set(key, storageObject);
    this.stats.totalSize += size;

    return storageObject;
  }

  private calculateObjectSize(data: any): number {
    if (data === null || data === undefined) {
      return 0;
    }

    if (typeof data === 'string') {
      return new TextEncoder().encode(data).length;
    }

    if (data instanceof ArrayBuffer) {
      return data.byteLength;
    }

    if (ArrayBuffer.isView(data)) {
      return data.byteLength;
    }

    try {
      const jsonString = JSON.stringify(data);
      return new TextEncoder().encode(jsonString).length;
    } catch {
      // Fallback for circular references or other issues
      return 1024; // Default size
    }
  }

  private calculateChecksum(data: any): string {
    // Simple checksum calculation
    // In production, use a proper hash function like SHA-256
    const str = JSON.stringify(data);
    let hash = 0;

    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32-bit integer
    }

    return hash.toString(16);
  }

  private getFieldValue(obj: StorageObject, field: string): any {
    const parts = field.split('.');
    let value: any = obj;

    for (const part of parts) {
      if (value && typeof value === 'object' && part in value) {
        value = value[part];
      } else {
        return undefined;
      }
    }

    return value;
  }

  private evaluateCondition(value: any, operator: string, conditionValue: any): boolean {
    switch (operator) {
      case 'eq':
        return value === conditionValue;
      case 'neq':
        return value !== conditionValue;
      case 'gt':
        return value > conditionValue;
      case 'gte':
        return value >= conditionValue;
      case 'lt':
        return value < conditionValue;
      case 'lte':
        return value <= conditionValue;
      case 'contains':
        return typeof value === 'string' && value.includes(conditionValue);
      case 'startsWith':
        return typeof value === 'string' && value.startsWith(conditionValue);
      case 'endsWith':
        return typeof value === 'string' && value.endsWith(conditionValue);
      case 'in':
        return Array.isArray(conditionValue) && conditionValue.includes(value);
      case 'notIn':
        return Array.isArray(conditionValue) && !conditionValue.includes(value);
      default:
        return false;
    }
  }

  private compareValues(a: any, b: any): number {
    if (a === b) return 0;
    if (a === undefined || a === null) return 1;
    if (b === undefined || b === null) return -1;

    if (typeof a === 'string' && typeof b === 'string') {
      return a.localeCompare(b);
    }

    return a < b ? -1 : 1;
  }

  private updateStats(operation: 'read' | 'write' | 'delete', latency: number, success: boolean): void {
    this.totalOperations++;
    this.totalLatency += latency;

    // Update operation-specific stats
    switch (operation) {
      case 'read':
        this.stats.readOperations++;
        break;
      case 'write':
        this.stats.writeOperations++;
        break;
      case 'delete':
        this.stats.deleteOperations++;
        break;
    }

    // Update error rate
    if (!success) {
      const totalErrors = this.stats.errorRate * (this.totalOperations - 1);
      this.stats.errorRate = (totalErrors + 1) / this.totalOperations;
    } else {
      const totalErrors = this.stats.errorRate * (this.totalOperations - 1);
      this.stats.errorRate = totalErrors / this.totalOperations;
    }

    // Update average latency
    this.stats.averageLatency = this.totalLatency / this.totalOperations;
  }

  private async cleanupOldBackups(): Promise<void> {
    if (!this.backupConfig.enabled || this.backupConfig.retention <= 0) return;

    const now = Date.now();
    const retentionMs = this.backupConfig.retention * 24 * 60 * 60 * 1000;

    for (const [backupId] of this.backups) {
      const timestamp = parseInt(backupId.split('-')[1]);
      if (now - timestamp > retentionMs) {
        this.backups.delete(backupId);
      }
    }
  }

  private handleDataMessage(message: InstanceMessage): void {
    const { payload } = message;

    if (payload && payload.operation) {
      switch (payload.operation) {
        case 'put':
          if (payload.key && payload.data !== undefined) {
            this.put(payload.key, payload.data, payload.metadata);
          }
          break;
        case 'get':
          if (payload.key) {
            this.get(payload.key);
          }
          break;
        case 'delete':
          if (payload.key) {
            this.delete(payload.key);
          }
          break;
      }
    }
  }

  private handleCommandMessage(message: InstanceMessage): void {
    const { payload } = message;

    if (payload && payload.command) {
      switch (payload.command) {
        case 'clear':
          this.clear();
          break;
        case 'compact':
          this.compact();
          break;
        case 'backup':
          this.backup();
          break;
        case 'restore':
          if (payload.backupId) {
            this.restore(payload.backupId);
          }
          break;
      }
    }
  }

  private handleQueryMessage(message: InstanceMessage): void {
    const { payload } = message;

    if (payload && payload.query) {
      // Handle storage queries
      console.log(`Processing storage query: ${JSON.stringify(payload.query)}`);
    }
  }
}