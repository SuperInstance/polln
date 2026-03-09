/**
 * POLLN Protocol Adapter
 *
 * Bidirectional protocol translation between SPORE (Microbiome) and Core POLLN messaging.
 * Enables seamless cross-system communication with proper message routing and handling.
 *
 * @module microbiome/protocol-adapter
 */

import { v4 as uuidv4 } from 'uuid';
import { EventEmitter } from 'events';
import type { A2APackage } from '../core/types.js';
import type { Colony } from '../core/colony.js';
import type { ColonyStructure } from './types.js';
import { MicrobiomeBridge } from './bridge.js';

// ============================================================================
// MESSAGE TYPE DEFINITIONS
// ============================================================================

/**
 * SPORE message types (Microbiome)
 */
export enum SporeType {
  RESOURCE_REQUEST = 'resource_request',
  RESOURCE_OFFER = 'resource_offer',
  METABOLISM_COMPLETE = 'metabolism_complete',
  REPRODUCTION_EVENT = 'reproduction_event',
  DEATH_EVENT = 'death_event',
  SYMBIOSIS_REQUEST = 'symbiosis_request',
  SYMBIOSIS_RESPONSE = 'symbiosis_response',
  COLONY_FORM = 'colony_form',
  COLONY_DISSOLVE = 'colony_dissolve',
  MURMURATION = 'murmuration',
  IMMUNE_RESPONSE = 'immune_response',
  EXPLORATION = 'exploration',
}

/**
 * Core message types (POLLN)
 */
export enum CoreMessageType {
  AGENT_PROPOSAL = 'agent_proposal',
  AGENT_SELECTION = 'agent_selection',
  AGENT_EXECUTION = 'agent_execution',
  AGENT_RESULT = 'agent_result',
  GOAL_UPDATE = 'goal_update',
  VALUE_UPDATE = 'value_update',
  SAFETY_CHECK = 'safety_check',
  WORLD_MODEL_UPDATE = 'world_model_update',
  DREAM_CYCLE = 'dream_cycle',
  FEDERATED_SYNC = 'federated_sync',
  COLONY_SYNC = 'colony_sync',
  STIGMERGY_SIGNAL = 'stigmergy_signal',
}

/**
 * SPORE message (Microbiome format)
 */
export interface SporeMessage {
  type: SporeType | string;
  payload: unknown;
  sourceId: string;
  targetId?: string;
  timestamp: number;
  metadata?: Record<string, unknown>;
}

/**
 * Core message (POLLN format)
 */
export interface CoreMessage {
  type: CoreMessageType | string;
  payload: unknown;
  sourceId: string;
  targetId?: string;
  timestamp: number;
  parentIds: string[];
  causalChainId: string;
  layer: 'SAFETY' | 'REFLEX' | 'HABITUAL' | 'DELIBERATE';
  privacyLevel: 'PUBLIC' | 'COLONY' | 'PRIVATE';
}

/**
 * Unified message type for routing
 */
export type UnifiedMessage = SporeMessage | CoreMessage;

/**
 * Message routing direction
 */
export type MessageDirection = 'microbiome-to-core' | 'core-to-microbiome' | 'bidirectional';

/**
 * Channel mapping between systems
 */
export interface ChannelMapping {
  microbiomeChannel: string;
  coreChannel: string;
  direction: MessageDirection;
  active: boolean;
}

// ============================================================================
// PROTOCOL ADAPTER CONFIGURATION
// ============================================================================

/**
 * Configuration for ProtocolAdapter
 */
export interface ProtocolAdapterConfig {
  /** Enable verbose logging */
  verbose?: boolean;

  /** Bridge instance for agent conversion */
  bridge?: MicrobiomeBridge;

  /** Auto-sync channels between systems */
  autoSyncChannels?: boolean;

  /** Default privacy level for translated messages */
  defaultPrivacyLevel?: 'PUBLIC' | 'COLONY' | 'PRIVATE';

  /** Default subsumption layer for translated messages */
  defaultLayer?: 'SAFETY' | 'REFLEX' | 'HABITUAL' | 'DELIBERATE';

  /** Message type mapping overrides */
  customTypeMappings?: Partial<Record<SporeType | string, CoreMessageType | string>>;

  /** Reverse message type mapping overrides */
  customReverseTypeMappings?: Partial<Record<CoreMessageType | string, SporeType | string>>;
}

// ============================================================================
// MESSAGE TYPE MAPPINGS
// ============================================================================

/**
 * Default SPORE to Core message type mappings
 */
const DEFAULT_SPORE_TO_CORE: Record<string, string> = {
  [SporeType.RESOURCE_REQUEST]: CoreMessageType.AGENT_PROPOSAL,
  [SporeType.RESOURCE_OFFER]: CoreMessageType.AGENT_RESULT,
  [SporeType.METABOLISM_COMPLETE]: CoreMessageType.AGENT_EXECUTION,
  [SporeType.REPRODUCTION_EVENT]: CoreMessageType.COLONY_SYNC,
  [SporeType.DEATH_EVENT]: CoreMessageType.VALUE_UPDATE,
  [SporeType.SYMBIOSIS_REQUEST]: CoreMessageType.AGENT_PROPOSAL,
  [SporeType.SYMBIOSIS_RESPONSE]: CoreMessageType.AGENT_RESULT,
  [SporeType.COLONY_FORM]: CoreMessageType.COLONY_SYNC,
  [SporeType.COLONY_DISSOLVE]: CoreMessageType.COLONY_SYNC,
  [SporeType.MURMURATION]: CoreMessageType.STIGMERGY_SIGNAL,
  [SporeType.IMMUNE_RESPONSE]: CoreMessageType.SAFETY_CHECK,
  [SporeType.EXPLORATION]: CoreMessageType.AGENT_PROPOSAL,
};

/**
 * Default Core to SPORE message type mappings
 */
const DEFAULT_CORE_TO_SPORE: Record<string, string> = {
  [CoreMessageType.AGENT_PROPOSAL]: SporeType.RESOURCE_REQUEST,
  [CoreMessageType.AGENT_SELECTION]: SporeType.SYMBIOSIS_REQUEST,
  [CoreMessageType.AGENT_EXECUTION]: SporeType.METABOLISM_COMPLETE,
  [CoreMessageType.AGENT_RESULT]: SporeType.RESOURCE_OFFER,
  [CoreMessageType.GOAL_UPDATE]: SporeType.SYMBIOSIS_RESPONSE,
  [CoreMessageType.VALUE_UPDATE]: SporeType.METABOLISM_COMPLETE,
  [CoreMessageType.SAFETY_CHECK]: SporeType.IMMUNE_RESPONSE,
  [CoreMessageType.WORLD_MODEL_UPDATE]: SporeType.EXPLORATION,
  [CoreMessageType.DREAM_CYCLE]: SporeType.MURMURATION,
  [CoreMessageType.FEDERATED_SYNC]: SporeType.COLONY_FORM,
  [CoreMessageType.COLONY_SYNC]: SporeType.COLONY_FORM,
  [CoreMessageType.STIGMERGY_SIGNAL]: SporeType.MURMURATION,
};

// ============================================================================
// PROTOCOL ADAPTER
// ============================================================================

/**
 * ProtocolAdapter - Bidirectional protocol translation
 *
 * Handles:
 * 1. SPORE ↔ Core message translation
 * 2. Message routing between systems
 * 3. Message type mismatch handling
 * 4. Communication channel synchronization
 * 5. Colony communication bridging
 * 6. Cross-system event handling
 */
export class ProtocolAdapter extends EventEmitter {
  private config: Required<ProtocolAdapterConfig>;
  private adapterId: string;
  private bridge: MicrobiomeBridge;
  private channelMappings: Map<string, ChannelMapping>;
  private messageHistory: Map<string, UnifiedMessage[]>;
  private typeMappings: Map<string, string>;
  private reverseTypeMappings: Map<string, string>;
  private routingTable: Map<string, string>; // sourceChannel -> targetChannel

  constructor(config: ProtocolAdapterConfig = {}) {
    super();

    this.adapterId = uuidv4();
    this.bridge = config.bridge || new MicrobiomeBridge();
    this.channelMappings = new Map();
    this.messageHistory = new Map();
    this.typeMappings = new Map();
    this.reverseTypeMappings = new Map();
    this.routingTable = new Map();

    this.config = {
      verbose: config.verbose ?? false,
      bridge: this.bridge,
      autoSyncChannels: config.autoSyncChannels ?? true,
      defaultPrivacyLevel: config.defaultPrivacyLevel ?? 'COLONY',
      defaultLayer: config.defaultLayer ?? 'HABITUAL',
      customTypeMappings: config.customTypeMappings ?? {},
      customReverseTypeMappings: config.customReverseTypeMappings ?? {},
    };

    // Initialize type mappings
    this.initializeTypeMappings();

    if (this.config.verbose) {
      console.log(`[ProtocolAdapter] Initialized adapter ${this.adapterId}`);
    }
  }

  // ==========================================================================
  // MESSAGE TRANSLATION
  // ==========================================================================

  /**
   * Translate SPORE message to Core format
   *
   * @param spore - SPORE message from microbiome
   * @returns Core message format
   */
  sporeToCore(spore: SporeMessage): CoreMessage {
    const coreType = this.mapSporeTypeToCore(spore.type);
    const causalChainId = uuidv4();

    // If payload is an object, preserve metadata within it
    // Otherwise, wrap it to include metadata
    let payload: any;
    if (spore.payload && typeof spore.payload === 'object' && !Array.isArray(spore.payload)) {
      payload = {
        ...spore.payload,
        _sporeMetadata: spore.metadata || {},
      };
    } else {
      payload = {
        data: spore.payload,
        _sporeMetadata: spore.metadata || {},
      };
    }

    const core: CoreMessage = {
      type: coreType,
      payload,
      sourceId: spore.sourceId,
      targetId: spore.targetId,
      timestamp: spore.timestamp,
      parentIds: [], // SPORE doesn't track parent IDs
      causalChainId,
      layer: this.inferSubsumptionLayer(spore.type, spore.payload),
      privacyLevel: this.config.defaultPrivacyLevel,
    };

    // Store in history
    this.addToHistory('spore-to-core', spore);
    this.addToHistory('core', core);

    this.emit('translated', {
      direction: 'spore-to-core',
      original: spore,
      translated: core,
    });

    if (this.config.verbose) {
      console.log(`[ProtocolAdapter] Translated SPORE ${spore.type} -> Core ${coreType}`);
    }

    return core;
  }

  /**
   * Translate Core message to SPORE format
   *
   * @param core - Core message from POLLN
   * @returns SPORE message format
   */
  coreToSpore(core: CoreMessage): SporeMessage {
    const sporeType = this.mapCoreTypeToSpore(core.type);

    const spore: SporeMessage = {
      type: sporeType,
      payload: core.payload,
      sourceId: core.sourceId,
      targetId: core.targetId,
      timestamp: core.timestamp,
      metadata: {
        causalChainId: core.causalChainId,
        parentIds: core.parentIds,
        layer: core.layer,
        privacyLevel: core.privacyLevel,
      },
    };

    // Store in history
    this.addToHistory('core-to-spore', core);
    this.addToHistory('spore', spore);

    this.emit('translated', {
      direction: 'core-to-spore',
      original: core,
      translated: spore,
    });

    if (this.config.verbose) {
      console.log(`[ProtocolAdapter] Translated Core ${core.type} -> SPORE ${sporeType}`);
    }

    return spore;
  }

  // ==========================================================================
  // MESSAGE ROUTING
  // ==========================================================================

  /**
   * Route message between systems
   *
   * @param message - Message to route
   * @param from - Source system
   * @param to - Target system
   * @returns Routed message or null if routing failed
   */
  routeMessage(
    message: UnifiedMessage,
    from: 'microbiome' | 'core',
    to: 'microbiome' | 'core'
  ): UnifiedMessage | null {
    // Validate routing direction
    if (from === to) {
      if (this.config.verbose) {
        console.log(`[ProtocolAdapter] No routing needed (same system)`);
      }
      return message;
    }

    let translated: UnifiedMessage;

    if (from === 'microbiome' && to === 'core') {
      // Translate SPORE to Core
      translated = this.sporeToCore(message as SporeMessage);
    } else if (from === 'core' && to === 'microbiome') {
      // Translate Core to SPORE
      translated = this.coreToSpore(message as CoreMessage);
    } else {
      this.emit('error', {
        message: 'Invalid routing direction',
        from,
        to,
      });
      return null;
    }

    // Apply routing table transformations
    const routedMessage = this.applyRoutingTable(translated, from, to);

    // Ensure metadata is preserved for Core messages
    if (to === 'core' && (routedMessage as CoreMessage).payload) {
      // For Core messages, metadata may be in the payload
      const coreMsg = routedMessage as CoreMessage;
      if (!(coreMsg.payload as any).metadata) {
        (coreMsg.payload as any).metadata = {};
      }
    }

    this.emit('routed', {
      original: message,
      routed: routedMessage,
      from,
      to,
    });

    return routedMessage;
  }

  /**
   * Route A2A package between systems
   *
   * @param package - A2A package to route
   * @param from - Source system
   * @param to - Target system
   * @returns Routed A2A package or null if routing failed
   */
  routeA2A(
    pkg: A2APackage,
    from: 'microbiome' | 'core',
    to: 'microbiome' | 'core'
  ): A2APackage | null {
    if (from === to) {
      return pkg;
    }

    // Use bridge to convert A2A package
    if (from === 'microbiome' && to === 'core') {
      const bridged = this.bridge.bridgeA2AToCore(pkg);
      // Ensure receiverId is preserved
      if (bridged && pkg.receiverId) {
        bridged.receiverId = pkg.receiverId;
      }
      return bridged;
    } else if (from === 'core' && to === 'microbiome') {
      const bridged = this.bridge.bridgeA2AToMicrobiome(pkg);
      // Ensure targetId is preserved
      if (bridged && pkg.receiverId) {
        (bridged as any).targetId = pkg.receiverId;
      }
      return bridged;
    }

    return null;
  }

  // ==========================================================================
  // MESSAGE TYPE HANDLING
  // ==========================================================================

  /**
   * Handle message type mismatch
   *
   * @param type - Unknown message type
   * @param fallbackType - Fallback type to use
   * @returns Handled message or null
   */
  handleTypeMismatch(type: string, fallbackType?: string): UnifiedMessage | null {
    const mappedType = this.findClosestTypeMatch(type);

    if (this.config.verbose) {
      console.log(`[ProtocolAdapter] Handling type mismatch: ${type} -> ${mappedType || fallbackType || 'unknown'}`);
    }

    this.emit('type_mismatch', {
      originalType: type,
      mappedType,
      fallbackType,
    });

    if (!mappedType && !fallbackType) {
      return null;
    }

    // Return a placeholder message with the mapped type
    return {
      type: mappedType || fallbackType || 'unknown',
      payload: { originalType: type, handled: true },
      sourceId: 'protocol-adapter',
      timestamp: Date.now(),
    } as UnifiedMessage;
  }

  /**
   * Find closest matching type for unknown message types
   *
   * @param type - Unknown type
   * @returns Closest matching type or null
   */
  private findClosestTypeMatch(type: string): string | null {
    // Check custom mappings first
    if (this.config.customTypeMappings[type]) {
      return this.config.customTypeMappings[type] as string;
    }

    if (this.config.customReverseTypeMappings[type]) {
      return this.config.customReverseTypeMappings[type] as string;
    }

    // Try fuzzy matching
    const allTypes = [
      ...Object.values(SporeType),
      ...Object.values(CoreMessageType),
    ];

    for (const knownType of allTypes) {
      if (type.toLowerCase().includes(knownType.toLowerCase()) ||
          knownType.toLowerCase().includes(type.toLowerCase())) {
        return knownType;
      }
    }

    return null;
  }

  // ==========================================================================
  // CHANNEL SYNCHRONIZATION
  // ==========================================================================

  /**
   * Synchronize communication channels between systems
   *
   * @param microChannels - Microbiome channels (topic -> subscribers)
   * @param coreChannels - Core channels (topic -> subscribers)
   */
  syncChannels(
    microChannels: Map<string, string[]>,
    coreChannels: Map<string, Set<string>>
  ): void {
    if (this.config.verbose) {
      console.log(`[ProtocolAdapter] Syncing channels between systems`);
    }

    // Map microbiome channels to core channels
    for (const [microTopic, subscribers] of microChannels.entries()) {
      const coreTopic = this.mapChannelName(microTopic, 'microbiome-to-core');

      // Create mapping
      const mapping: ChannelMapping = {
        microbiomeChannel: microTopic,
        coreChannel: coreTopic,
        direction: 'bidirectional',
        active: true,
      };

      this.channelMappings.set(microTopic, mapping);
      this.routingTable.set(microTopic, coreTopic);

      // Reverse mapping
      this.routingTable.set(coreTopic, microTopic);

      this.emit('channel_mapped', mapping);
    }

    // Map core channels to microbiome channels
    for (const [coreTopic, subscribers] of coreChannels.entries()) {
      if (!this.routingTable.has(coreTopic)) {
        const microTopic = this.mapChannelName(coreTopic, 'core-to-microbiome');

        const mapping: ChannelMapping = {
          microbiomeChannel: microTopic,
          coreChannel: coreTopic,
          direction: 'bidirectional',
          active: true,
        };

        this.channelMappings.set(microTopic, mapping);
        this.routingTable.set(coreTopic, microTopic);
        this.routingTable.set(microTopic, coreTopic);

        this.emit('channel_mapped', mapping);
      }
    }

    if (this.config.verbose) {
      console.log(`[ProtocolAdapter] Synced ${this.channelMappings.size} channel mappings`);
    }
  }

  /**
   * Map channel name between systems
   *
   * @param channel - Original channel name
   * @param direction - Mapping direction
   * @returns Mapped channel name
   */
  private mapChannelName(
    channel: string,
    direction: 'microbiome-to-core' | 'core-to-microbiome'
  ): string {
    // Apply naming convention transformation
    if (direction === 'microbiome-to-core') {
      // Microbiome uses snake_case, Core uses camelCase
      return channel
        .split('_')
        .map((word, index) => index === 0 ? word : word.charAt(0).toUpperCase() + word.slice(1))
        .join('');
    } else {
      // Core uses camelCase, Microbiome uses snake_case
      return channel
        .replace(/([A-Z])/g, '_$1')
        .toLowerCase()
        .replace(/^_/, '');
    }
  }

  /**
   * Get mapped channel name
   *
   * @param channel - Channel name
   * @param system - Which system the channel is from
   * @returns Mapped channel name or undefined
   */
  getMappedChannel(
    channel: string,
    system: 'microbiome' | 'core'
  ): string | undefined {
    return this.routingTable.get(channel);
  }

  // ==========================================================================
  // COLONY COMMUNICATION
  // ==========================================================================

  /**
   * Translate colony communication between systems
   *
   * @param colony - Colony structure
   * @param message - Message to translate
   * @returns Array of translated messages (one per member)
   */
  translateColonyCommunication(
    colony: ColonyStructure,
    message: UnifiedMessage
  ): UnifiedMessage[] {
    const translatedMessages: UnifiedMessage[] = [];

    // Get all colony members
    const members = colony.members;

    // Translate message for each member
    for (const memberId of members) {
      const memberMessage: UnifiedMessage = {
        ...message,
        targetId: memberId,
        metadata: {
          ...((message as SporeMessage).metadata || {}),
          colonyId: colony.id,
          colonySize: members.length,
          memberIndex: members.indexOf(memberId),
        },
      };

      translatedMessages.push(memberMessage);
    }

    if (this.config.verbose) {
      console.log(`[ProtocolAdapter] Translated colony message to ${translatedMessages.length} members`);
    }

    this.emit('colony_communication_translated', {
      colonyId: colony.id,
      memberCount: members.length,
      originalMessage: message,
      translatedMessages,
    });

    return translatedMessages;
  }

  /**
   * Bridge colony communication between microbiome and core colonies
   *
   * @param microColony - Microbiome colony
   * @param coreColony - Core colony
   * @param message - Message to bridge
   * @returns Bridged messages for both colonies
   */
  bridgeColonyCommunication(
    microColony: ColonyStructure,
    coreColony: Colony,
    message: UnifiedMessage
  ): {
    microbiome: UnifiedMessage[];
    core: UnifiedMessage[];
  } {
    // Sync colonies first
    this.bridge.syncColonies(microColony, coreColony);

    // Translate for microbiome members
    const microbiomeMessages = this.translateColonyCommunication(
      microColony,
      message
    );

    // Translate for core members
    const coreMembers = coreColony.getAllAgents().map(a => a.id);
    const coreMessages: UnifiedMessage[] = coreMembers.map(memberId => ({
      ...message,
      targetId: memberId,
      metadata: {
        ...((message as SporeMessage).metadata || {}),
        colonyId: coreColony.id,
        colonySize: coreMembers.length,
      },
    }));

    if (this.config.verbose) {
      console.log(`[ProtocolAdapter] Bridged colony communication: ${microbiomeMessages.length} microbiome, ${coreMessages.length} core`);
    }

    this.emit('colony_communication_bridged', {
      microColonyId: microColony.id,
      coreColonyId: coreColony.id,
      microbiomeMessageCount: microbiomeMessages.length,
      coreMessageCount: coreMessages.length,
    });

    return {
      microbiome: microbiomeMessages,
      core: coreMessages,
    };
  }

  // ==========================================================================
  // EVENT HANDLING
  // ==========================================================================

  /**
   * Handle cross-system event
   *
   * @param event - Event from one system
   * @param sourceSystem - Source system
   * @returns Translated event for target system
   */
  handleCrossSystemEvent(
    event: Record<string, unknown>,
    sourceSystem: 'microbiome' | 'core'
  ): Record<string, unknown> {
    const translatedEvent: Record<string, unknown> = {
      ...event,
      sourceSystem,
      adapterId: this.adapterId,
      translatedAt: Date.now(),
    };

    // Add system-specific metadata
    if (sourceSystem === 'microbiome') {
      translatedEvent.targetSystem = 'core';
      translatedEvent.metadata = {
        ...event,
        originalFormat: 'spore',
      };
    } else {
      translatedEvent.targetSystem = 'microbiome';
      translatedEvent.metadata = {
        ...event,
        originalFormat: 'core',
      };
    }

    this.emit('cross_system_event', translatedEvent);

    return translatedEvent;
  }

  // ==========================================================================
  // UTILITY METHODS
  // ==========================================================================

  /**
   * Get adapter statistics
   */
  getStats() {
    return {
      adapterId: this.adapterId,
      channelMappings: this.channelMappings.size,
      routingTableEntries: this.routingTable.size,
      messageHistorySize: Array.from(this.messageHistory.values())
        .reduce((sum, history) => sum + history.length, 0),
      typeMappings: this.typeMappings.size,
      config: this.config,
    };
  }

  /**
   * Clear message history
   */
  clearHistory(): void {
    this.messageHistory.clear();
    if (this.config.verbose) {
      console.log(`[ProtocolAdapter] Cleared message history`);
    }
  }

  /**
   * Reset channel mappings
   */
  resetChannelMappings(): void {
    this.channelMappings.clear();
    this.routingTable.clear();
    if (this.config.verbose) {
      console.log(`[ProtocolAdapter] Reset channel mappings`);
    }
  }

  // ==========================================================================
  // PRIVATE HELPERS
  // ==========================================================================

  /**
   * Initialize type mappings
   */
  private initializeTypeMappings(): void {
    // SPORE to Core mappings
    for (const [sporeType, coreType] of Object.entries(DEFAULT_SPORE_TO_CORE)) {
      this.typeMappings.set(sporeType, coreType);
    }

    // Add custom mappings
    for (const [sporeType, coreType] of Object.entries(this.config.customTypeMappings)) {
      this.typeMappings.set(sporeType, coreType);
    }

    // Core to SPORE mappings
    for (const [coreType, sporeType] of Object.entries(DEFAULT_CORE_TO_SPORE)) {
      this.reverseTypeMappings.set(coreType, sporeType);
    }

    // Add custom reverse mappings
    for (const [coreType, sporeType] of Object.entries(this.config.customReverseTypeMappings)) {
      this.reverseTypeMappings.set(coreType, sporeType);
    }
  }

  /**
   * Map SPORE type to Core type
   */
  private mapSporeTypeToCore(type: string): string {
    return this.typeMappings.get(type) || CoreMessageType.AGENT_PROPOSAL;
  }

  /**
   * Map Core type to SPORE type
   */
  private mapCoreTypeToSpore(type: string): string {
    return this.reverseTypeMappings.get(type) || SporeType.RESOURCE_REQUEST;
  }

  /**
   * Infer subsumption layer from message type and payload
   */
  private inferSubsumptionLayer(
    type: string,
    payload: unknown
  ): 'SAFETY' | 'REFLEX' | 'HABITUAL' | 'DELIBERATE' {
    // Safety-related messages
    if (type === SporeType.IMMUNE_RESPONSE || type === CoreMessageType.SAFETY_CHECK) {
      return 'SAFETY';
    }

    // Reflex responses
    if (type === SporeType.MURMURATION || type === CoreMessageType.STIGMERGY_SIGNAL) {
      return 'REFLEX';
    }

    // Deliberate actions
    if (type === SporeType.EXPLORATION || type === CoreMessageType.WORLD_MODEL_UPDATE) {
      return 'DELIBERATE';
    }

    // Default to habitual
    return this.config.defaultLayer;
  }

  /**
   * Apply routing table transformations to message
   */
  private applyRoutingTable(
    message: UnifiedMessage,
    from: 'microbiome' | 'core',
    to: 'microbiome' | 'core'
  ): UnifiedMessage {
    // Apply channel mappings if present
    if (this.routingTable.size > 0) {
      // Check for channel in different locations based on message type
      let sourceChannel: string | undefined;

      // Try SporeMessage metadata first
      const sporeMetadata = (message as SporeMessage).metadata;
      if (sporeMetadata?.channel) {
        sourceChannel = sporeMetadata.channel as string;
      }

      // Try CoreMessage payload _sporeMetadata
      if (!sourceChannel) {
        const corePayload = (message as CoreMessage).payload as any;
        if (corePayload?._sporeMetadata?.channel) {
          sourceChannel = corePayload._sporeMetadata.channel;
        }
      }

      if (sourceChannel && this.routingTable.has(sourceChannel)) {
        const targetChannel = this.routingTable.get(sourceChannel)!;

        if (this.config.verbose) {
          console.log(`[ProtocolAdapter] Applying channel mapping: ${sourceChannel} -> ${targetChannel}`);
        }

        // Handle SporeMessage format
        if ((message as SporeMessage).metadata !== undefined) {
          const updatedMetadata = {
            ...(message as SporeMessage).metadata,
            channel: targetChannel,
            originalChannel: sourceChannel,
          };

          return {
            ...message,
            metadata: updatedMetadata,
          } as UnifiedMessage;
        }

        // Handle CoreMessage format (metadata in payload._sporeMetadata)
        const coreMsg = message as CoreMessage;
        const updatedPayload = {
          ...(coreMsg.payload as any),
          _sporeMetadata: {
            ...(coreMsg.payload as any)._sporeMetadata || {},
            channel: targetChannel,
            originalChannel: sourceChannel,
          },
        };

        return {
          ...coreMsg,
          payload: updatedPayload,
        } as UnifiedMessage;
      }
    }

    return message;
  }

  /**
   * Add message to history
   */
  private addToHistory(key: string, message: UnifiedMessage): void {
    if (!this.messageHistory.has(key)) {
      this.messageHistory.set(key, []);
    }

    const history = this.messageHistory.get(key)!;
    history.push(message);

    // Keep only last 100 messages
    if (history.length > 100) {
      history.shift();
    }
  }
}

// ============================================================================
// FACTORY FUNCTIONS
// ============================================================================

/**
 * Create a default protocol adapter
 */
export function createProtocolAdapter(config?: ProtocolAdapterConfig): ProtocolAdapter {
  return new ProtocolAdapter(config);
}

/**
 * Create a protocol adapter with verbose logging
 */
export function createVerboseAdapter(config?: Omit<ProtocolAdapterConfig, 'verbose'>): ProtocolAdapter {
  return new ProtocolAdapter({ ...config, verbose: true });
}

/**
 * Create a protocol adapter with custom bridge
 */
export function createAdapterWithBridge(
  bridge: MicrobiomeBridge,
  config?: Omit<ProtocolAdapterConfig, 'bridge'>
): ProtocolAdapter {
  return new ProtocolAdapter({ ...config, bridge });
}
