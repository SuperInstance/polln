# A2A Protocol Integration
## Device-Native Agents as First-Class Participants in the Agent-to-Agent Internet

**Document Version**: 1.0  
**Date**: January 2026  
**Classification**: Technical Specification  
**Status**: Architecture Definition

---

# Executive Summary

The Agent-to-Agent (A2A) protocol, announced by Google in April 2025, represents a paradigm shift in AI interoperability—enabling autonomous agents to communicate, coordinate, and collaborate across organizational and platform boundaries. The Mask-Locked Inference Chip positions itself as the **hardware foundation** that makes A2A practical for every device.

This document specifies how Device-Native Agents (DNA)—AI agents whose reasoning models are permanently encoded in silicon—become first-class participants in the emerging A2A ecosystem. Unlike software agents running on general-purpose hardware, device-native agents offer:

- **Guaranteed Availability**: Always-on, always-ready agent presence
- **Hardware-Enforced Privacy**: Selective data sharing via silicon-level access controls
- **Zero Latency Discovery**: Instant capability negotiation without model loading
- **Trustworthy Identity**: Cryptographic identity rooted in immutable hardware

The convergence of A2A protocol standardization and mask-locked silicon creates a unique strategic opportunity: becoming the **first hardware to natively speak A2A**.

---

# Part I: A2A Protocol Overview

## 1.1 Core Concepts and Architecture

### Protocol Definition

The Agent-to-Agent (A2A) protocol is an open standard that enables AI agents to:
1. **Discover** each other's presence and capabilities
2. **Negotiate** task assignments and data access
3. **Communic** intents, requests, and results
4. **Coordinate** multi-step, multi-agent workflows

### Architectural Model

```
┌─────────────────────────────────────────────────────────────────────┐
│                    A2A ARCHITECTURAL MODEL                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│    ┌──────────────┐                    ┌──────────────┐            │
│    │   USER A     │                    │   USER B     │            │
│    │  (Human)     │                    │  (Human)     │            │
│    └──────┬───────┘                    └──────┬───────┘            │
│           │                                   │                     │
│           │ Task Request                      │ Task Request        │
│           ▼                                   ▼                     │
│    ┌──────────────┐                    ┌──────────────┐            │
│    │  CLIENT      │◄───── A2A ────────►│  CLIENT      │            │
│    │  AGENT A     │     Protocol       │  AGENT B     │            │
│    │              │                    │              │            │
│    │ (Cloud LLM)  │                    │ (Device DNA) │            │
│    └──────┬───────┘                    └──────┬───────┘            │
│           │                                   │                     │
│           │ MCP                               │ MCP                 │
│           │ (Tools)                           │ (Tools)             │
│           ▼                                   ▼                     │
│    ┌──────────────┐                    ┌──────────────┐            │
│    │  External    │                    │  Device      │            │
│    │  Services    │                    │  Hardware    │            │
│    │  (APIs)      │                    │  (Sensors)   │            │
│    └──────────────┘                    └──────────────┘            │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Three-Agent Communication Framework

A2A operates within a three-agent framework:

| Role | Description | Example |
|------|-------------|---------|
| **User** | Entity that triggers tasks, receives results | Human end-user, automated system |
| **Client Agent** | Solicits and delivers tasks on behalf of user | Cloud LLM, personal assistant |
| **Remote Agent** | Executes tasks, provides specialized capabilities | Device-native agent, service agent |

### Core Message Types

```
A2A Message Taxonomy:
│
├── Discovery Messages
│   ├── BEACON: Announce agent presence
│   ├── QUERY_CAPABILITIES: Request agent card
│   └── ADVERTISE_CAPABILITIES: Respond with capabilities
│
├── Session Messages
│   ├── INITIATE_SESSION: Request connection
│   ├── ACCEPT_SESSION: Confirm connection
│   ├── AUTHENTICATE: Prove identity
│   └── TERMINATE_SESSION: Close connection
│
├── Task Messages
│   ├── REQUEST_TASK: Delegate work to agent
│   ├── TASK_STATUS: Progress update
│   ├── TASK_RESULT: Final output
│   └── TASK_ERROR: Failure notification
│
└── Data Messages
    ├── REQUEST_DATA: Ask for information
    ├── DATA_RESPONSE: Provide information
    ├── DATA_DENIED: Refuse access
    └── DATA_STREAM: Continuous data feed
```

## 1.2 Protocol Comparison: A2A vs MCP vs ACP

### Complementary Protocols, Different Purposes

```
┌─────────────────────────────────────────────────────────────────────┐
│                 AGENT PROTOCOL ECOSYSTEM                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐                                                │
│  │      MCP        │  Agent ↔ Tool Connections                      │
│  │  (Anthropic)    │  "How do I use this hammer?"                   │
│  │  Nov 2024       │                                                │
│  │                 │  Scope: Single agent accessing tools           │
│  │  Model Context  │  Discovery: Tool catalogs                      │
│  │  Protocol       │  Transport: Stdio, HTTP, SSE                   │
│  └────────┬────────┘                                                │
│           │                                                          │
│           │ Complements                                              │
│           ▼                                                          │
│  ┌─────────────────┐                                                │
│  │      A2A        │  Agent ↔ Agent Communication                   │
│  │  (Google)       │  "Can you help me with this?"                  │
│  │  Apr 2025       │                                                │
│  │                 │  Scope: Multi-agent coordination               │
│  │  Agent-to-Agent │  Discovery: Agent cards, directories           │
│  │  Protocol       │  Transport: HTTP/2, WebSocket, gRPC            │
│  └────────┬────────┘                                                │
│           │                                                          │
│           │ Alternative (IBM)                                        │
│           ▼                                                          │
│  ┌─────────────────┐                                                │
│  │      ACP        │  Agent ↔ Agent Communication                   │
│  │  (IBM)          │  Alternative specification                     │
│  │  Mar 2025       │                                                │
│  │                 │  Scope: Similar to A2A                         │
│  │  Agent          │  Discovery: Centralized registry               │
│  │  Communication  │  Transport: HTTP, WebSocket                    │
│  │  Protocol       │                                                │
│  └─────────────────┘                                                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Detailed Comparison

| Feature | MCP (Anthropic) | A2A (Google) | ACP (IBM) |
|---------|-----------------|--------------|-----------|
| **Launch Date** | November 2024 | April 2025 | March 2025 |
| **Primary Purpose** | Agent-to-Tool | Agent-to-Agent | Agent-to-Agent |
| **Discovery** | Tool catalogs | Agent Cards | Central registry |
| **Message Format** | JSON-RPC 2.0 | JSON-LD | JSON |
| **Transport** | Stdio, HTTP, SSE | HTTP/2, WebSocket | HTTP, WebSocket |
| **Authentication** | API keys | OAuth 2.0, mTLS | OAuth 2.0 |
| **Semantic Layer** | Tool schemas | Capability ontology | Service descriptions |
| **State Management** | Stateless | Session-based | Session-based |
| **Enterprise Focus** | High | Very High | High |

### The Complete Agent Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMPLETE AGENT STACK                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Layer 4: Multi-Agent Orchestration                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  "Which agents should work together on this problem?"         │  │
│  │  • Task decomposition                                         │  │
│  │  • Agent selection                                            │  │
│  │  • Result aggregation                                         │  │
│  │  • Framework: LangGraph, AutoGen, CrewAI                      │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                           │ A2A Protocol                            │
│  Layer 3: Agent-to-Agent Communication                              │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  "How do agents talk to each other?"                          │  │
│  │  • Capability discovery                                       │  │
│  │  • Task delegation                                            │  │
│  │  • Result passing                                             │  │
│  │  • Protocol: A2A (Google), ACP (IBM)                          │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                           │ MCP Protocol                            │
│  Layer 2: Agent-to-Tool Connection                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  "How do agents use external capabilities?"                   │  │
│  │  • Tool discovery                                             │  │
│  │  • Parameter passing                                          │  │
│  │  • Result retrieval                                           │  │
│  │  • Protocol: MCP (Anthropic)                                  │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                           │ APIs, SDKs                              │
│  Layer 1: Foundation Infrastructure                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  "What runs the agents?"                                      │  │
│  │  • Compute: Cloud GPUs, Edge chips, Device silicon            │  │
│  │  • Network: HTTP, WebSocket, gRPC                             │  │
│  │  • Security: TLS, OAuth, certificates                         │  │
│  │  • Hardware: Mask-Locked Inference Chip (THIS PROJECT)        │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 1.3 Current State of the Specification

### Specification Maturity (as of January 2026)

| Component | Status | Version | Notes |
|-----------|--------|---------|-------|
| Core Protocol | Stable | 1.0 | Published specification |
| Agent Card Schema | Stable | 1.0 | JSON-LD format defined |
| Discovery Protocol | Draft | 0.9 | BLE/mDNS under review |
| Security Model | Stable | 1.0 | OAuth 2.0 + mTLS |
| Transport Bindings | Stable | 1.0 | HTTP/2, WebSocket, gRPC |
| Task Execution | Draft | 0.8 | Async patterns evolving |
| Device Agent Profile | Proposed | 0.1 | **OPPORTUNITY FOR CONTRIBUTION** |

### Key Specification Documents

1. **A2A Core Specification** - Primary protocol definition
2. **Agent Card Schema** - Capability description format
3. **Transport Binding Specifications** - HTTP/2, WebSocket, gRPC
4. **Security Considerations** - Authentication and authorization
5. **Implementation Guide** - Developer resources

### Open Areas for Contribution

The A2A specification has gaps that Device-Native Agents can help fill:

| Gap | Opportunity | DNA Contribution |
|-----|-------------|------------------|
| Device agent profile | Define hardware-specific constraints | Power, latency, bandwidth profiles |
| Offline operation | Intermittent connectivity handling | Local-first agent behavior |
| Privacy controls | Fine-grained data access | Hardware-enforced privacy gates |
| Trust roots | Hardware identity | Mask-locked cryptographic identity |
| Safety constraints | Device safety rules | Hardware interlock integration |

## 1.4 Key Players and Adoption Status

### Protocol Sponsors

| Organization | Role | Contribution |
|--------------|------|--------------|
| **Google** | Primary sponsor | Protocol design, reference implementation |
| **Anthropic** | Ecosystem partner | MCP integration, Claude support |
| **Atlassian** | Enterprise adopter | Jira/Confluence agent integration |
| **Box** | Enterprise adopter | Content management agents |
| **Salesforce** | Enterprise adopter | CRM agent integration |
| **SAP** | Enterprise adopter | Enterprise software agents |
| **ServiceNow** | Enterprise adopter | ITSM agent integration |
| **Workday** | Enterprise adopter | HCM agent integration |

### Implementation Status

```
A2A Adoption Timeline:
│
│  2024 Q4 ─────────────────────────────────────────────────────────
│           │ MCP Launch (Anthropic)
│           │
│  2025 Q1 ─────────────────────────────────────────────────────────
│           │ ACP Launch (IBM, March)
│           │
│  2025 Q2 ─────────────────────────────────────────────────────────
│           │ A2A Launch (Google, April)
│           │ Enterprise partners announced
│           │
│  2025 Q3 ─────────────────────────────────────────────────────────
│           │ Reference implementations released
│           │ MCP-A2A integration patterns published
│           │
│  2025 Q4 ─────────────────────────────────────────────────────────
│           │ First production deployments
│           │ Standards body formation discussions
│           │
│  2026 Q1 ───────────────────────────────────────────────────────── ◄ NOW
│           │ Specification stabilization
│           │ Device agent profile proposals needed
│           │ [Mask-Locked Chip opportunity window]
│           │
│  2026 Q2+ ────────────────────────────────────────────────────────
│           │ Expected: Formal standards body
│           │ Expected: Device agent specifications
│           │ Expected: Hardware certification programs
│
```

### Strategic Positioning

The Mask-Locked Inference Chip can influence the A2A ecosystem by:

1. **Contributing Device Agent Profile** - Define how constrained devices participate
2. **Providing Reference Implementation** - First hardware-native A2A stack
3. **Demonstrating New Capabilities** - Show what's possible with hardware agents
4. **Establishing Safety Patterns** - Hardware-enforced constraints as model

---

# Part II: Device-Native Agent as A2A Participant

## 2.1 How a Mask-Locked Agent Speaks A2A

### The DNA A2A Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│                DEVICE-NATIVE AGENT A2A STACK                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Layer 7: Agent Semantics (MASK-LOCKED)                             │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Neural network weights encoding:                             │  │
│  │  • Intent classification                                      │  │
│  │  • Capability understanding                                   │  │
│  │  • Natural language generation                                │  │
│  │  • Protocol message interpretation                            │  │
│  │                                                               │  │
│  │  Size: ~50M parameters dedicated to protocol handling         │  │
│  │  Latency: <10ms for intent classification                     │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                           │                                          │
│  Layer 6: A2A Protocol Handler (FIRMWARE)                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Software implementation of:                                  │  │
│  │  • Message serialization/deserialization                      │  │
│  │  • Session state management                                   │  │
│  │  • Capability negotiation                                     │  │
│  │  • Error handling                                             │  │
│  │                                                               │  │
│  │  Memory: 1 MB message buffers                                 │  │
│  │  CPU: Embedded RISC-V core (320 MHz)                          │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                           │                                          │
│  Layer 5: Transport Layer (HARDWARE ACCELERATED)                    │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Hardware acceleration for:                                   │  │
│  │  • TLS encryption/decryption                                  │  │
│  │  • JSON parsing (partial)                                     │  │
│  │  • Message checksum verification                              │  │
│  │                                                               │  │
│  │  Crypto engine: AES-256, SHA-256, ECDSA                       │  │
│  │  Latency: <1ms per message                                    │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                           │                                          │
│  Layer 4: Network Interface (HARDWARE)                              │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Physical interfaces:                                         │  │
│  │  • WiFi 6 (802.11ax) via external module                      │  │
│  │  • Thread (802.15.4) for mesh networking                      │  │
│  │  • BLE 5.3 for discovery                                      │  │
│  │  • Ethernet (optional, via SPI bridge)                        │  │
│  │                                                               │  │
│  │  SPI interface to WiFi/BLE module: 50 Mbps                    │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Message Processing Pipeline

```
A2A Message Processing Flow:
│
│  1. RECEIVE (Network Interface)
│     ┌─────────────────────────────────────────────────────────┐
│     │ WiFi/BLE/Thread → SPI → DMA → Message Buffer (1 MB)    │
│     │                                                         │
│     │ Interrupt: "Message received"                           │
│     │ Power: Wake from light sleep if needed                  │
│     │ Latency: <5ms from physical layer to buffer             │
│     └─────────────────────────────────────────────────────────┘
│                           │
│  2. VERIFY (Transport Layer)
│     ┌─────────────────────────────────────────────────────────┐
│     │ Check TLS integrity, decrypt payload                    │
│     │                                                         │
│     │ Hardware crypto: <1ms                                   │
│     │ Verify message structure (partial hardware parsing)     │
│     └─────────────────────────────────────────────────────────┘
│                           │
│  3. PARSE (Protocol Handler)
│     ┌─────────────────────────────────────────────────────────┐
│     │ JSON deserialization → Internal representation          │
│     │                                                         │
│     │ Software on RISC-V: 1-5ms depending on complexity       │
│     │ Validate against A2A schema                             │
│     └─────────────────────────────────────────────────────────┘
│                           │
│  4. UNDERSTAND (Neural Engine)
│     ┌─────────────────────────────────────────────────────────┐
│     │ Intent classification via forward pass                  │
│     │                                                         │
│     │ Compute array: <10ms                                    │
│     │ Classify: QUERY, ACTION, CONFIGURE, NEGOTIATE, etc.     │
│     │ Extract parameters from message content                  │
│     └─────────────────────────────────────────────────────────┘
│                           │
│  5. VALIDATE (Safety Layer)
│     ┌─────────────────────────────────────────────────────────┐
│     │ Check against hardware constraints                       │
│     │                                                         │
│     │ Hardware interlocks: Nanoseconds                        │
│     │ Neural safety check: <1ms                               │
│     │ Policy check: <1ms                                      │
│     └─────────────────────────────────────────────────────────┘
│                           │
│  6. EXECUTE (Action Engine)
│     ┌─────────────────────────────────────────────────────────┐
│     │ Perform requested action or generate response            │
│     │                                                         │
│     │ Variable by action type:                                │
│     │   - Sensor read: <10ms                                  │
│     │   - Actuator control: <100ms                            │
│     │   - Complex reasoning: 100ms-2s                         │
│     └─────────────────────────────────────────────────────────┘
│                           │
│  7. RESPOND (Protocol Handler)
│     ┌─────────────────────────────────────────────────────────┐
│     │ Generate A2A response message                            │
│     │                                                         │
│     │ Neural generation: Variable (streaming possible)        │
│     │ JSON serialization: <1ms                                 │
│     │ TLS encryption: <1ms                                     │
│     │ Network transmit: <5ms                                   │
│     └─────────────────────────────────────────────────────────┘
│
│  Total Round-Trip Latency (simple query): <50ms
│  Total Round-Trip Latency (complex action): <500ms
```

### A2A Agent Card for Device-Native Agent

```json
{
  "@context": "https://a2a-protocol.org/context/v1",
  "@type": "AgentCard",
  "agent_identity": {
    "agent_id": "did:masklock:device:uuid-v4-generated-at-first-boot",
    "name": "Smart Thermostat Agent",
    "version": "1.0.0",
    "description": "Device-native agent for HVAC control with hardware-enforced safety",
    "manufacturer": {
      "name": "OEM Partner",
      "uri": "https://partner.example.com"
    },
    "model": "MT-2026-PRO",
    "hardware_revision": "rev1.0",
    "firmware_version": "2.3.1"
  },
  "capabilities": {
    "a2a_version": "1.0",
    "profiles": [
      "https://a2a-protocol.org/profiles/device-agent/v1",
      "https://a2a-protocol.org/profiles/sensor-agent/v1",
      "https://a2a-protocol.org/profiles/safety-critical/v1"
    ],
    "sensors": [
      {
        "sensor_id": "temp_ambient",
        "type": "temperature",
        "unit": "celsius",
        "range": [-20, 60],
        "resolution": 0.1,
        "update_rate": "1Hz",
        "access_mode": "read",
        "privacy_level": "local_only"
      },
      {
        "sensor_id": "humidity",
        "type": "humidity",
        "unit": "percent",
        "range": [0, 100],
        "resolution": 1,
        "update_rate": "0.1Hz",
        "access_mode": "read",
        "privacy_level": "shareable"
      }
    ],
    "actuators": [
      {
        "actuator_id": "hvac_control",
        "type": "hvac_relay",
        "modes": ["off", "heat", "cool", "auto"],
        "safety_constraints": [
          {
            "constraint_id": "max_temp",
            "type": "hardware_enforced",
            "description": "Maximum temperature limit",
            "value": 30,
            "unit": "celsius"
          },
          {
            "constraint_id": "min_cycle_time",
            "type": "policy_enforced",
            "description": "Minimum time between mode changes",
            "value": 300,
            "unit": "seconds"
          }
        ]
      }
    ],
    "apis": [
      {
        "api_id": "set_temperature",
        "description": "Set target temperature",
        "parameters": {
          "target": {
            "type": "number",
            "range": [15, 30],
            "unit": "celsius"
          }
        },
        "returns": {
          "type": "object",
          "properties": {
            "status": {"enum": ["accepted", "rejected", "pending_consent"]},
            "reason": {"type": "string"},
            "effective_value": {"type": "number"}
          }
        },
        "requires_consent": false,
        "safety_level": "medium"
      },
      {
        "api_id": "set_mode",
        "description": "Change operating mode",
        "parameters": {
          "mode": {"enum": ["home", "away", "sleep", "vacation"]}
        },
        "requires_consent": true,
        "safety_level": "low"
      }
    ],
    "communication": {
      "transports": ["https", "websocket"],
      "message_formats": ["json-ld"],
      "streaming": true,
      "max_message_size": 65536,
      "response_timeout_ms": 5000
    },
    "constraints": {
      "power_profile": "low_power",
      "max_concurrent_sessions": 3,
      "offline_capable": true,
      "local_first": true
    }
  },
  "authentication": {
    "methods": ["mtls", "oauth2", "did"],
    "supported_algorithms": ["ES256", "ES384", "ES512"],
    "key_rotation_supported": true
  },
  "trust": {
    "attestation": "hardware_root",
    "safety_certification": "IEC-62443",
    "audit_logging": true
  }
}
```

## 2.2 Agent Discovery Protocol

### Discovery Overview

Device-Native Agents must be discoverable by cloud agents seeking their capabilities. The discovery process operates at multiple levels:

```
Discovery Hierarchy:
│
├── Level 0: Physical Presence (BLE Beacons)
│   ├── Short-range discovery (<10m)
│   ├── No network infrastructure required
│   └── For initial pairing and local coordination
│
├── Level 1: Local Network (mDNS/DNS-SD)
│   ├── LAN discovery
│   ├── Home/office environments
│   └── For same-network coordination
│
├── Level 2: Cloud Directory (A2A Registry)
│   ├── Internet-wide discovery
│   ├── Capability-based search
│   └── For remote agent coordination
│
└── Level 3: Mesh Network (Thread)
    ├── IoT mesh networks
    ├── Beyond WiFi range
    └── For industrial/smart city deployment
```

### BLE Beacon Discovery

```
BLE Advertisement Format for A2A Discovery:
┌────────────────────────────────────────────────────────────────────┐
│                        BLE Advertisement Packet                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Byte 0-1:   Length = 0x1A (26 bytes)                              │
│  Byte 2:     Type = 0xFF (Manufacturer Specific)                   │
│  Byte 3-4:   Company ID = 0xXXXX (Assigned by Bluetooth SIG)       │
│  Byte 5:     Protocol ID = 0xA2 (A2A Protocol)                     │
│  Byte 6:     Version = 0x01                                        │
│  Byte 7:     Flags:                                                │
│              ├── Bit 0: Accepts connections                        │
│              ├── Bit 1: Requires authentication                    │
│              ├── Bit 2: Has safety constraints                     │
│              └── Bit 3-7: Reserved                                 │
│  Byte 8-23:  Device Class Hash (SHA-256 truncated)                 │
│              └── Quick capability matching                         │
│  Byte 24-25: Service Port (big-endian)                             │
│  Byte 26:    RSSI Calibration Offset                               │
│                                                                     │
│  Total: 27 bytes (fits in BLE advertisement)                       │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘

Beacon Transmission Schedule:
┌────────────────────────────────────────────────────────────────────┐
│ Mode              │ Interval     │ Power    │ Battery Impact      │
├───────────────────┼──────────────┼──────────┼─────────────────────┤
│ Active Discovery  │ 100 ms       │ 0 dBm    │ ~1 mW average       │
│ Normal Operation  │ 1 second     │ -4 dBm   │ ~0.1 mW average     │
│ Power Saving      │ 10 seconds   │ -8 dBm   │ ~0.01 mW average    │
│ Deep Sleep        │ Disabled     │ N/A      │ 0 mW                │
└────────────────────────────────────────────────────────────────────┘
```

### mDNS/DNS-SD Service Discovery

```
DNS-SD Service Registration:
│
│  Service Name: _a2a._tcp.local
│
│  Instance: Smart Thermostat [UUID]._a2a._tcp.local
│
│  TXT Records:
│  ├── v=1                    (A2A protocol version)
│  ├── cap=sensor,actuator    (capability classes)
│  ├── cls=thermostat         (device class)
│  ├── mfr=OEM_Partner        (manufacturer code)
│  ├── mdl=MT-2026-PRO        (model)
│  ├── sec=high               (security level)
│  ├── off=true               (offline capable)
│  └── card=https://[device-ip]/a2a/card.json
│
│  Port: 8443 (HTTPS)
│  Priority: 0
│  Weight: 0
```

### Cloud Directory Registration

```json
{
  "registration": {
    "agent_did": "did:masklock:device:uuid-v4",
    "endpoint": "https://gateway.example.com/agent/uuid-v4",
    "card_uri": "https://gateway.example.com/agent/uuid-v4/card.json",
    "visibility": "private",
    "owner_did": "did:web:user.example.com",
    "registered_at": "2026-01-15T10:30:00Z",
    "expires_at": "2027-01-15T10:30:00Z",
    "proof": {
      "type": "EcdsaSecp256r1Signature2019",
      "created": "2026-01-15T10:30:00Z",
      "proofPurpose": "authentication",
      "verificationMethod": "did:masklock:device:uuid-v4#key-1",
      "jws": "eyJhbGciOiJFUzI1NiIs..."
    }
  }
}
```

### Discovery Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENT DISCOVERY FLOW                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Cloud Agent                        Device-Native Agent             │
│  ┌──────────────┐                   ┌──────────────┐               │
│  │              │                   │              │               │
│  │   Search     │                   │   Beaconing  │               │
│  │   Request    │                   │   (BLE/mDNS) │               │
│  │              │                   │              │               │
│  └──────┬───────┘                   └──────┬───────┘               │
│         │                                  │                        │
│         │ 1. Query Directory               │                        │
│         ▼                                  │                        │
│  ┌──────────────┐                          │                        │
│  │   A2A        │                          │                        │
│  │   Registry   │                          │                        │
│  │              │                          │                        │
│  └──────┬───────┘                          │                        │
│         │                                  │                        │
│         │ 2. Return Matching Agents        │                        │
│         ▼                                  │                        │
│  ┌──────────────┐                          │                        │
│  │   Select     │                          │                        │
│  │   Candidate  │                          │                        │
│  │              │                          │                        │
│  └──────┬───────┘                          │                        │
│         │                                  │                        │
│         │ 3. Request Agent Card            │                        │
│         │─────────────────────────────────►│                        │
│         │                                  │                        │
│         │ 4. Return Agent Card             │                        │
│         │◄─────────────────────────────────│                        │
│         │                                  │                        │
│         │ 5. Evaluate Capabilities         │                        │
│         ▼                                  │                        │
│  ┌──────────────┐                          │                        │
│  │   Match      │                          │                        │
│  │   Found?     │                          │                        │
│  │              │                          │                        │
│  └──────┬───────┘                          │                        │
│         │                                  │                        │
│         │ 6. Initiate Session              │                        │
│         │─────────────────────────────────►│                        │
│         │                                  │                        │
│         │ 7. Mutual Authentication         │                        │
│         │◄────────────────────────────────►│                        │
│         │                                  │                        │
│         │ 8. Session Established           │                        │
│         │◄────────────────────────────────►│                        │
│         │                                  │                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 2.3 Capability Advertisement

### Capability Declaration Schema

The Device-Native Agent declares capabilities through a structured schema that integrates with the A2A Agent Card:

```json
{
  "capability_declaration": {
    "version": "1.0",
    "timestamp": "2026-01-15T10:30:00Z",
    "valid_until": "2026-01-22T10:30:00Z",
    
    "device_class": {
      "category": "environmental_control",
      "subcategory": "hvac_thermostat",
      "certifications": ["ENERGY_STAR", "IEC_62443"]
    },
    
    "functional_capabilities": {
      "sensing": [
        {
          "capability_id": "temperature_measurement",
          "ontology": "https://schema.org/temperature",
          "properties": {
            "accuracy": {"value": 0.5, "unit": "celsius"},
            "range": {"min": -20, "max": 60, "unit": "celsius"},
            "resolution": {"value": 0.1, "unit": "celsius"},
            "latency_ms": 10,
            "update_frequency_hz": 1
          },
          "access_control": {
            "local": "always_allowed",
            "remote": "requires_authentication",
            "streaming": true
          }
        }
      ],
      "actuation": [
        {
          "capability_id": "temperature_control",
          "ontology": "https://schema.org/SetTemperatureAction",
          "properties": {
            "control_range": {"min": 15, "max": 30, "unit": "celsius"},
            "modes": ["heat", "cool", "auto", "off"],
            "response_time_ms": 5000
          },
          "access_control": {
            "local": "requires_user_presence",
            "remote": "requires_explicit_consent"
          },
          "safety_constraints": [
            {
              "type": "hardware_enforced",
              "constraint": "max_temperature",
              "value": 30,
              "unit": "celsius",
              "description": "Physical relay cutoff at 30°C"
            }
          ]
        }
      ],
      "reasoning": [
        {
          "capability_id": "schedule_optimization",
          "ontology": "https://a2a-protocol.org/capabilities/optimization",
          "properties": {
            "model_type": "mask_locked_llm",
            "model_size_params": 2000000000,
            "context_window": 512,
            "inference_rate_tok_per_s": 80
          },
          "access_control": {
            "local": "always_allowed",
            "remote": "requires_authentication"
          }
        }
      ]
    },
    
    "communication_capabilities": {
      "transports": [
        {
          "protocol": "https",
          "port": 8443,
          "tls_version": "1.3",
          "authentication": ["mtls", "oauth2"]
        },
        {
          "protocol": "websocket",
          "port": 8443,
          "subprotocol": "a2a.v1"
        },
        {
          "protocol": "thread",
          "port": 61616,
          "network_name": "mesh_network"
        }
      ],
      "message_formats": ["json-ld", "cbor"],
      "max_concurrent_sessions": 3,
      "session_timeout_ms": 300000
    },
    
    "constraint_profile": {
      "power": {
        "operating_mode": "low_power",
        "average_power_mw": 55,
        "peak_power_mw": 2100,
        "deep_sleep_power_mw": 0.5
      },
      "connectivity": {
        "offline_capable": true,
        "offline_cache_hours": 168,
        "sync_on_reconnect": true
      },
      "compute": {
        "max_inference_concurrent": 1,
        "inference_priority": "interactive"
      }
    }
  }
}
```

### Capability Negotiation Protocol

```
Capability Negotiation Flow:
│
│  Cloud Agent                                          Device Agent
│       │                                                     │
│       │  1. TASK_REQUEST                                   │
│       │  {                                                 │
│       │    "task_type": "temperature_adjustment",         │
│       │    "parameters": {                                 │
│       │      "target": 22,                                 │
│       │      "unit": "celsius"                             │
│       │    },                                              │
│       │    "constraints": {                                │
│       │      "timeout_ms": 10000,                          │
│       │      "requires_confirmation": true                 │
│       │    }                                               │
│       │  }                                                 │
│       │────────────────────────────────────────────────────►│
│       │                                                     │
│       │  2. CAPABILITY_CHECK                               │
│       │     (Device internally validates against           │
│       │      hardware constraints and safety rules)        │
│       │                                                     │
│       │  3. CAPABILITY_RESPONSE                            │
│       │  {                                                 │
│       │    "status": "accepted_with_modifications",        │
│       │    "modifications": {                              │
│       │      "original_target": 22,                        │
│       │      "effective_target": 22,                       │
│       │      "reason": "within_safe_range"                 │
│       │    },                                              │
│       │    "safety_confirmation": {                        │
│       │      "hardware_constraints_checked": true,         │
│       │      "user_consent_required": false                │
│       │    }                                               │
│       │  }                                                 │
│       │◄────────────────────────────────────────────────────│
│       │                                                     │
│       │  4. EXECUTE_CONFIRMATION                           │
│       │  {                                                 │
│       │    "confirmed": true                               │
│       │  }                                                 │
│       │────────────────────────────────────────────────────►│
│       │                                                     │
│       │  5. TASK_RESULT                                    │
│       │  {                                                 │
│       │    "status": "success",                            │
│       │    "result": {                                     │
│       │      "temperature_set": 22,                        │
│       │      "mode": "cool",                               │
│       │      "estimated_time_to_target": "15 minutes"      │
│       │    }                                               │
│       │  }                                                 │
│       │◄────────────────────────────────────────────────────│
│       │                                                     │
```

## 2.4 Authentication and Authorization Model

### Authentication Framework

```
┌─────────────────────────────────────────────────────────────────────┐
│               AUTHENTICATION ARCHITECTURE                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Level 0: Hardware Identity (IMMUTABLE)                             │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Root of Trust: Mask-Locked Identity Key                      │  │
│  │                                                               │  │
│  │  • Private key derived from silicon-unique PUF               │  │
│  │  • Public key embedded in device certificate                 │  │
│  │  • Certificate signed by manufacturer CA                     │  │
│  │  • Key never leaves device                                   │  │
│  │                                                               │  │
│  │  Device Identity: did:masklock:device:[hardware-uuid]        │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                           │                                          │
│  Level 1: Session Authentication (MUTUAL)                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Mutual TLS (mTLS) or OAuth 2.0                              │  │
│  │                                                               │  │
│  │  mTLS Flow:                                                   │  │
│  │  1. Cloud agent presents certificate                         │  │
│  │  2. Device verifies against trusted CA                       │  │
│  │  3. Device presents its certificate                          │  │
│  │  4. Cloud agent verifies manufacturer signature              │  │
│  │  5. Session established with mutual trust                    │  │
│  │                                                               │  │
│  │  OAuth 2.0 Flow:                                              │  │
│  │  1. User authorizes cloud agent to access device             │  │
│  │  2. Cloud agent obtains access token                         │  │
│  │  3. Device validates token signature                         │  │
│  │  4. Session established with delegated authority             │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                           │                                          │
│  Level 2: Action Authorization (CONTEXTUAL)                         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Fine-grained permission checks                               │  │
│  │                                                               │  │
│  │  Per-Action Checks:                                           │  │
│  │  • Is this action type permitted for this session?           │  │
│  │  • Does the action require user consent?                     │  │
│  │  • Does the action violate safety constraints?               │  │
│  │  • Is the rate limit exceeded?                               │  │
│  │  • Is local user presence required?                          │  │
│  │                                                               │  │
│  │  Decision made by neural + hardware combination              │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Authorization Matrix

| Action Type | Local User | Authenticated Cloud Agent | Anonymous |
|-------------|------------|---------------------------|-----------|
| Read temperature | ✓ | ✓ | ✗ |
| Read humidity | ✓ | ✓ (anonymized) | ✗ |
| Set temperature | ✓ | ✓ (with consent) | ✗ |
| Change mode | ✓ | ✓ (with consent) | ✗ |
| Read schedule | ✓ | ✓ | ✗ |
| Modify schedule | ✓ | ✓ (with consent) | ✗ |
| Read energy usage | ✓ | ✓ (anonymized) | ✗ |
| Factory reset | ✓ (local only) | ✗ | ✗ |
| Firmware update | ✓ (verified) | ✗ | ✗ |
| Read all sensor history | ✓ | ✗ | ✗ |

### Consent Management

```
Consent Request Flow:
│
│  Cloud Agent                          Device Agent              User
│       │                                   │                       │
│       │ REQUEST_ACTION                   │                       │
│       │ {                                │                       │
│       │   "action": "set_temperature",   │                       │
│       │   "parameters": {"target": 28}   │                       │
│       │ }                                │                       │
│       │──────────────────────────────────►│                       │
│       │                                   │                       │
│       │                                   │ CHECK: Consent needed│
│       │                                   │ ✓ (high temperature) │
│       │                                   │                       │
│       │                                   │ CONSENT_REQUIRED     │
│       │                                   │ {                     │
│       │                                   │   "reason": "Target  │
│       │                                   │    temperature above │
│       │                                   │    comfort range",   │
│       │                                   │   "timeout_ms": 60000│
│       │                                   │ }                     │
│       │                                   │──────────────────────►│
│       │                                   │                       │
│       │                                   │              User reviews
│       │                                   │              and approves
│       │                                   │                       │
│       │                                   │ CONSENT_GRANTED      │
│       │                                   │◄──────────────────────│
│       │                                   │                       │
│       │ ACTION_RESULT                    │                       │
│       │ {                                │                       │
│       │   "status": "success",           │                       │
│       │   "consent_id": "abc123"         │                       │
│       │ }                                │                       │
│       │◄──────────────────────────────────│                       │
│       │                                   │                       │
```

## 2.5 Privacy Considerations

### Privacy Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PRIVACY ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Principle 1: Local-First Processing                                │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  All data processing occurs on-device by default              │  │
│  │  Data only leaves device when explicitly authorized           │  │
│  │  Hardware gates prevent unauthorized data exfiltration        │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Principle 2: Granular Data Sharing                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Data categories with different sharing policies:             │  │
│  │                                                               │  │
│  │  LOCAL_ONLY: Never shared                                    │  │
│  │  ├── Raw sensor timestamps                                   │  │
│  │  ├── User presence indicators                                │  │
│  │  └── Device health diagnostics                               │  │
│  │                                                               │  │
│  │  ANONYMIZED: Shareable with aggregation                      │  │
│  │  ├── Temperature averages (no timestamps)                    │  │
│  │  ├── Energy usage (daily totals)                             │  │
│  │  └── Operating mode statistics                               │  │
│  │                                                               │  │
│  │  SHAREABLE: Shareable with consent                           │  │
│  │  ├── Current temperature reading                             │  │
│  │  ├── Current operating mode                                  │  │
│  │  └── Schedule configuration                                  │  │
│  │                                                               │  │
│  │  SENSITIVE: Requires explicit consent per request            │  │
│  │  ├── Temperature history                                     │  │
│  │  ├── User presence history                                   │  │
│  │  └── Detailed energy consumption                             │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Principle 3: Differential Privacy                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  For anonymized data sharing, apply differential privacy:     │  │
│  │                                                               │  │
│  │  • Add calibrated noise to aggregated data                   │  │
│  │  • Noise level calibrated to privacy budget (ε)              │  │
│  │  • Privacy budget tracked across all disclosures             │  │
│  │  • Hardware enforces budget limits                           │  │
│  │                                                               │  │
│  │  Implementation: Neural network generates noise               │  │
│  │  as part of response synthesis (mask-locked, auditable)      │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Principle 4: Audit Trail                                           │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  All data access logged to immutable storage:                 │  │
│  │                                                               │  │
│  │  Log Entry:                                                   │  │
│  │  ├── Timestamp (hardware clock)                              │  │
│  │  ├── Requesting agent identity                               │  │
│  │  ├── Data category accessed                                  │  │
│  │  ├── Amount of data disclosed                                │  │
│  │  ├── Privacy budget consumed                                 │  │
│  │  └── User consent record (if applicable)                     │  │
│  │                                                               │  │
│  │  Storage: External flash, append-only                         │  │
│  │  Retention: 1 year minimum                                   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Privacy-Preserving Response Generation

```python
# Conceptual privacy filter implemented in neural network

class PrivacyFilter:
    """
    Hardware-enforced privacy filtering for A2A responses.
    Implemented as mask-locked neural network weights.
    """
    
    def filter_response(self, request, data, privacy_level):
        """
        Apply privacy filtering based on data category and request context.
        
        Args:
            request: A2A request message
            data: Raw data from device sensors/state
            privacy_level: LOCAL_ONLY, ANONYMIZED, SHAREABLE, SENSITIVE
        
        Returns:
            Filtered response safe for transmission
        """
        
        # Check 1: Data category access permission
        if privacy_level == "LOCAL_ONLY":
            return PrivacyRejection("Data category not shareable")
        
        # Check 2: User consent (for SENSITIVE)
        if privacy_level == "SENSITIVE":
            if not self.has_consent(request.requester):
                return ConsentRequest(request, data)
        
        # Check 3: Apply differential privacy (for ANONYMIZED)
        if privacy_level == "ANONYMIZED":
            data = self.apply_differential_privacy(
                data,
                epsilon=self.privacy_budget_remaining
            )
            self.privacy_budget_remaining -= epsilon_used
        
        # Check 4: Remove identifying information
        data = self.remove_identifiers(data)
        data = self.remove_timestamps(data)
        data = self.aggregate_temporal_data(data)
        
        # Check 5: Hardware gate verification
        if not self.hardware_gate.verify_safe_to_transmit(data):
            return PrivacyRejection("Hardware safety check failed")
        
        return FilteredResponse(data)
```

---

# Part III: Technical Implementation

## 3.1 Message Format Specification

### A2A Message Structure

```
A2A Message Envelope:
┌─────────────────────────────────────────────────────────────────────┐
│ Byte Offset │ Field                 │ Size    │ Description        │
├─────────────┼───────────────────────┼─────────┼────────────────────┤
│ 0-3         │ Magic Number          │ 4 bytes │ 0xA2A00001         │
│ 4-5         │ Version               │ 2 bytes │ Protocol version   │
│ 6-9         │ Message ID            │ 4 bytes │ Unique identifier  │
│ 10-13       │ Timestamp             │ 4 bytes │ Unix timestamp     │
│ 14-15       │ Message Type          │ 2 bytes │ See type table     │
│ 16-19       │ Payload Length        │ 4 bytes │ JSON payload size  │
│ 20-23       │ Flags                 │ 4 bytes │ See flags table    │
│ 24-55       │ Sender DID            │ 32 bytes│ DID (truncated)    │
│ 56-87       │ Recipient DID         │ 32 bytes│ DID (truncated)    │
│ 88+         │ Payload               │ N bytes │ JSON-LD content    │
│ N+88-...    │ Signature             │ 64 bytes│ ECDSA signature    │
└─────────────────────────────────────────────────────────────────────┘

Message Types:
┌─────────────┬────────────────────────────────────────────────────────┐
│ Type Code   │ Message Type                                           │
├─────────────┼────────────────────────────────────────────────────────┤
│ 0x0001      │ BEACON                                                 │
│ 0x0002      │ QUERY_CAPABILITIES                                     │
│ 0x0003      │ ADVERTISE_CAPABILITIES                                 │
│ 0x0010      │ INITIATE_SESSION                                       │
│ 0x0011      │ ACCEPT_SESSION                                         │
│ 0x0012      │ AUTHENTICATE                                           │
│ 0x0013      │ TERMINATE_SESSION                                      │
│ 0x0020      │ REQUEST_TASK                                           │
│ 0x0021      │ TASK_STATUS                                            │
│ 0x0022      │ TASK_RESULT                                            │
│ 0x0023      │ TASK_ERROR                                             │
│ 0x0030      │ REQUEST_DATA                                           │
│ 0x0031      │ DATA_RESPONSE                                          │
│ 0x0032      │ DATA_DENIED                                            │
│ 0x0033      │ DATA_STREAM                                            │
│ 0x0040      │ CONSENT_REQUEST                                        │
│ 0x0041      │ CONSENT_GRANTED                                        │
│ 0x0042      │ CONSENT_DENIED                                         │
└─────────────┴────────────────────────────────────────────────────────┘
```

### JSON-LD Payload Examples

```json
// Example: REQUEST_DATA message
{
  "@context": "https://a2a-protocol.org/context/v1",
  "@type": "RequestDataMessage",
  "message_id": "msg-uuid-v4",
  "timestamp": "2026-01-15T10:30:00.000Z",
  "request": {
    "data_type": "sensor_reading",
    "sensor_id": "temp_ambient",
    "parameters": {
      "include_history": false,
      "resolution": "full"
    }
  },
  "constraints": {
    "timeout_ms": 5000,
    "privacy_level": "anonymized_acceptable"
  }
}

// Example: DATA_RESPONSE message
{
  "@context": "https://a2a-protocol.org/context/v1",
  "@type": "DataResponseMessage",
  "message_id": "msg-uuid-v4-response",
  "in_response_to": "msg-uuid-v4",
  "timestamp": "2026-01-15T10:30:00.050Z",
  "status": "success",
  "data": {
    "sensor_id": "temp_ambient",
    "value": 22.5,
    "unit": "celsius",
    "timestamp_approximate": "2026-01-15T10:30:00Z",
    "quality": "high",
    "privacy_applied": {
      "method": "rounding",
      "precision_reduced_to": 0.5
    }
  }
}

// Example: REQUEST_TASK message (device action)
{
  "@context": "https://a2a-protocol.org/context/v1",
  "@type": "RequestTaskMessage",
  "message_id": "msg-uuid-v4",
  "timestamp": "2026-01-15T10:30:00.000Z",
  "task": {
    "task_type": "device_action",
    "action_id": "set_temperature",
    "parameters": {
      "target": 23.0,
      "unit": "celsius",
      "mode": "cool"
    },
    "reason": "User requested cooler temperature via voice assistant",
    "priority": "normal",
    "timeout_ms": 30000
  },
  "delegation": {
    "delegator_did": "did:web:user.example.com",
    "delegation_token": "eyJhbGciOiJFUzI1NiIs..."
  }
}
```

### Binary Encoding for Low-Bandwidth

For constrained networks (Thread, BLE), a binary encoding is defined:

```
CBOR-Encoding for A2A Messages:

; Request Data (minimal)
{
  0: 0x0030,              ; message_type: REQUEST_DATA
  1: "msg-id",            ; message_id
  2: 1234567890,          ; timestamp
  3: "temp_amb",          ; sensor_id (abbreviated)
  4: false,               ; include_history
}

; Binary size comparison:
; JSON: ~350 bytes
; CBOR: ~85 bytes
; Compression ratio: 4:1
```

## 3.2 Transport Layer Considerations

### Transport Comparison

| Transport | Range | Bandwidth | Latency | Power | Use Case |
|-----------|-------|-----------|---------|-------|----------|
| **BLE 5.3** | 10-100m | 2 Mbps | 10-50ms | Low | Discovery, pairing |
| **WiFi 6** | 50-100m | 1+ Gbps | 1-10ms | High | Primary communication |
| **Thread** | 10-30m (mesh) | 250 Kbps | 20-100ms | Low | IoT mesh, industrial |
| **Ethernet** | 100m (cable) | 100 Mbps-1Gbps | <1ms | Medium | Fixed installations |

### WiFi Implementation (Primary Transport)

```
WiFi Network Stack for A2A:
│
├── Physical Layer: WiFi 6 (802.11ax)
│   ├── Frequency: 2.4 GHz (range) or 5 GHz (speed)
│   ├── Target Wake Time (TWT) for power saving
│   └── External module (ESP32-C6, RTL8720DN)
│
├── Data Link Layer
│   ├── Security: WPA3-Personal/Enterprise
│   └── QoS: WMM for prioritizing A2A traffic
│
├── Network Layer
│   ├── IPv6 preferred (for Thread interop)
│   ├── IPv4 fallback
│   └── DNS-SD for local discovery
│
├── Transport Layer
│   ├── TCP for reliable delivery
│   │   └── HTTPS (TLS 1.3)
│   └── WebSocket for streaming
│       └── WSS (TLS 1.3)
│
└── Application Layer
    ├── HTTP/2 for request-response
    ├── WebSocket for bidirectional streaming
    └── gRPC for structured communication (optional)
```

### Thread Implementation (Mesh/IoT)

```
Thread Network Stack for A2A:
│
├── Physical Layer: IEEE 802.15.4
│   ├── Frequency: 2.4 GHz
│   ├── Range: 10-30m per hop
│   ├── Mesh networking (self-healing)
│   └── Integrated or external radio
│
├── Thread Layer
│   ├── Mesh routing
│   ├── Border router for internet connectivity
│   └── Device authentication
│
├── IP Layer
│   ├── IPv6 only
│   ├── 6LoWPAN compression
│   └── Mesh-local and global addressing
│
├── Transport Layer
│   ├── UDP (primary for Thread)
│   │   └── DTLS 1.3
│   └── CoAP (Constrained Application Protocol)
│       └── A2A binding over CoAP
│
└── A2A Adaptation
    ├── Message aggregation
    ├── Binary encoding (CBOR)
    └── Delay-tolerant messaging
```

### BLE Implementation (Discovery Only)

```
BLE Usage for A2A:
│
├── Discovery (Primary Use)
│   ├── Advertisement of agent presence
│   ├── Quick capability preview
│   └── Initial pairing trigger
│
├── Connection (Secondary Use)
│   ├── Low-bandwidth communication
│   ├── Fallback when WiFi unavailable
│   └── Direct mobile phone interaction
│
└── GATT Service Definition
    ├── Service UUID: 0xA2A0
    │
    ├── Characteristic: Agent Card
    │   ├── UUID: 0xA2A1
    │   ├── Properties: Read
    │   └── Value: Compressed Agent Card JSON
    │
    ├── Characteristic: Task Request
    │   ├── UUID: 0xA2A2
    │   ├── Properties: Write
    │   └── Value: Task request JSON
    │
    └── Characteristic: Task Response
        ├── UUID: 0xA2A3
        ├── Properties: Read, Notify
        └── Value: Task response JSON
```

## 3.3 Payload Optimization for Low-Bandwidth

### Optimization Strategies

```
┌─────────────────────────────────────────────────────────────────────┐
│               PAYLOAD OPTIMIZATION STRATEGIES                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Strategy 1: Message Compression                                    │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Apply compression to JSON payloads:                          │  │
│  │                                                               │  │
│  │  • GZIP: 70-80% size reduction                               │  │
│  │  • Brotli: 75-85% size reduction                             │  │
│  │  • zstd: 70-80% with faster decompression                    │  │
│  │                                                               │  │
│  │  Hardware acceleration: Decompress on chip                   │  │
│  │  Compression offload: External module (WiFi chip)            │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Strategy 2: Binary Encoding (CBOR)                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Replace JSON with CBOR for constrained networks:            │  │
│  │                                                               │  │
│  │  • Size reduction: 60-70%                                    │  │
│  │  • Parsing: 5-10× faster                                     │  │
│  │  • Implementation: ~10 KB code footprint                     │  │
│  │                                                               │  │
│  │  Use when: Bandwidth < 500 Kbps                              │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Strategy 3: Schema-Based Encoding                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Pre-shared schema eliminates field names:                   │  │
│  │                                                               │  │
│  │  JSON: {"temperature": 22.5, "unit": "celsius"}              │  │
│  │  Schema encoding: [22.5, 0] (enum for unit)                  │  │
│  │                                                               │  │
│  │  Size reduction: 80-90%                                      │  │
│  │  Requires: Schema negotiation at session start               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Strategy 4: Differential Encoding                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  For streaming data, send changes only:                      │  │
│  │                                                               │  │
│  │  Full message: {"temp": 22.5, "humidity": 45, "mode": "cool"}│  │
│  │  Delta: {"temp": 22.7}  // only temperature changed          │  │
│  │                                                               │  │
│  │  Reduction: 90%+ for frequent updates                        │  │
│  │  Requires: Sequence numbers for ordering                     │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Strategy 5: Semantic Compression                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Neural network generates concise responses:                 │  │
│  │                                                               │  │
│  │  Full: "The current temperature reading from the ambient    │  │
│  │         sensor is 22.5 degrees Celsius."                     │  │
│  │                                                               │  │
│  │  Compressed by NN: "temp: 22.5°C"                            │  │
│  │                                                               │  │
│  │  Reduction: 80%                                              │  │
│  │  Implemented in: Mask-locked inference weights               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Bandwidth Budget by Network Type

| Network | Effective BW | Message Budget | Recommended Encoding |
|---------|--------------|----------------|----------------------|
| WiFi (primary) | 10+ Mbps | Unlimited | JSON + TLS |
| WiFi (congested) | 1-10 Mbps | <100 KB | JSON + GZIP |
| Thread (mesh) | 100-200 Kbps | <10 KB | CBOR + schema |
| BLE | 100-200 Kbps | <5 KB | CBOR + schema + diff |

## 3.4 Latency Requirements and Optimization

### Latency Targets

```
Latency Requirements by Operation Type:
│
├── Discovery Operations
│   ├── BLE beacon detection: < 1 second
│   ├── mDNS resolution: < 500 ms
│   └── Agent card retrieval: < 1 second
│
├── Session Operations
│   ├── TLS handshake: < 200 ms
│   ├── Authentication: < 100 ms
│   └── Capability negotiation: < 500 ms
│
├── Query Operations
│   ├── Simple sensor read: < 50 ms
│   ├── State query: < 100 ms
│   └── Historical data query: < 500 ms
│
├── Action Operations
│   ├── Simple actuation: < 100 ms (ack), < 5s (complete)
│   ├── Complex action: < 500 ms (ack), < 30s (complete)
│   └── Action with consent: < 60 seconds (user timeout)
│
└── Streaming Operations
    ├── Sensor stream start: < 100 ms
    ├── Stream latency: < 50 ms per sample
    └── Stream stop: < 50 ms
```

### Latency Optimization Techniques

```
┌─────────────────────────────────────────────────────────────────────┐
│                 LATENCY OPTIMIZATION TECHNIQUES                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Technique 1: Connection Pooling                                    │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Maintain persistent connections to known agents              │  │
│  │                                                               │  │
│  │  • Skip TLS handshake for known peers                        │  │
│  │  • Session resumption (TLS 1.3 PSK)                          │  │
│  │  • Reduce connection overhead to <10ms                       │  │
│  │                                                               │  │
│  │  Tradeoff: Memory for session state (~10 KB per session)     │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Technique 2: Predictive Wake                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Wake from low-power state predictively:                     │  │
│  │                                                               │  │
│  │  • Schedule-based: Wake before expected interactions         │  │
│  │  • Event-based: Wake on sensor threshold                     │  │
│  │  • Network-triggered: Wake on network activity               │  │
│  │                                                               │  │
│  │  Wake time optimization: Light sleep → Active in <10ms       │  │
│  │  Deep sleep → Active in <100ms (for periodic checks)         │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Technique 3: Message Prioritization                                │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Process high-priority messages first:                       │  │
│  │                                                               │  │
│  │  Priority Queue:                                              │  │
│  │  ├── P0: Safety-critical (immediate)                         │  │
│  │  ├── P1: User-interactive (<100ms)                           │  │
│  │  ├── P2: Normal operations (<1s)                             │  │
│  │  └── P3: Background tasks (best effort)                      │  │
│  │                                                               │  │
│  │  Implementation: Hardware priority queue in message buffer   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Technique 4: Pre-computed Responses                                │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  For predictable queries, pre-compute responses:             │  │
│  │                                                               │  │
│  │  • Current sensor values: Updated on change, ready to send   │  │
│  │  • Capability card: Cached in memory                         │  │
│  │  • Status reports: Generated periodically                    │  │
│  │                                                               │  │
│  │  Response latency: <5ms for cached responses                 │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Technique 5: Neural Inference Optimization                         │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Optimize inference for latency:                             │  │
│  │                                                               │  │
│  │  • Speculative decoding: Generate multiple tokens in parallel│  │
│  │  • Early exit: Skip layers for simple queries                │  │
│  │  • Cache KV: Reuse context across queries                    │  │
│  │                                                               │  │
│  │  Latency reduction: 30-50% for simple queries                │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 3.5 Error Handling and Recovery

### Error Classification

```
Error Taxonomy:
│
├── Network Errors
│   ├── Connection lost
│   ├── Timeout
│   ├── Unreachable
│   └── Bandwidth exceeded
│
├── Protocol Errors
│   ├── Invalid message format
│   ├── Unsupported version
│   ├── Authentication failure
│   └── Authorization denied
│
├── Device Errors
│   ├── Sensor failure
│   ├── Actuator failure
│   ├── Resource exhausted
│   └── Internal error
│
├── Safety Errors
│   ├── Constraint violation
│   ├── User consent required
│   ├── Unsafe operation
│   └── Hardware interlock triggered
│
└── Application Errors
    ├── Invalid parameters
    ├── Precondition not met
    ├── Operation not supported
    └── Business rule violation
```

### Error Response Format

```json
{
  "@context": "https://a2a-protocol.org/context/v1",
  "@type": "ErrorMessage",
  "message_id": "error-uuid-v4",
  "in_response_to": "original-message-id",
  "timestamp": "2026-01-15T10:30:00.000Z",
  "error": {
    "code": "SAFETY_CONSTRAINT_VIOLATION",
    "category": "safety",
    "severity": "high",
    "message": "Requested temperature exceeds hardware safety limit",
    "details": {
      "constraint": "max_temperature",
      "requested_value": 35,
      "maximum_allowed": 30,
      "unit": "celsius",
      "enforcement_level": "hardware"
    },
    "recovery_suggestions": [
      "Request a value within the allowed range [15, 30]",
      "Contact local user for manual override"
    ],
    "retry_allowed": true,
    "retry_after_ms": null
  }
}
```

### Recovery Strategies

```
┌─────────────────────────────────────────────────────────────────────┐
│                    RECOVERY STRATEGIES                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Network Recovery                                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Strategy: Automatic reconnection with exponential backoff    │  │
│  │                                                               │  │
│  │  Reconnection attempts:                                       │  │
│  │  ├── Attempt 1: Immediate                                    │  │
│  │  ├── Attempt 2: Wait 1 second                                │  │
│  │  ├── Attempt 3: Wait 2 seconds                               │  │
│  │  ├── Attempt 4: Wait 4 seconds                               │  │
│  │  └── Max: Wait 60 seconds, then alert user                   │  │
│  │                                                               │  │
│  │  Message queue: Buffer up to 100 messages during disconnect  │  │
│  │  Priority: Safety messages transmitted first on reconnect    │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Session Recovery                                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Strategy: Session resumption for transient failures          │  │
│  │                                                               │  │
│  │  TLS Session Resumption:                                      │  │
│  │  • Pre-Shared Key (PSK) for known clients                    │  │
│  │  • Session tickets for quick resumption                      │  │
│  │  • Resume in <50ms vs <200ms for full handshake              │  │
│  │                                                               │  │
│  │  A2A Session State:                                           │  │
│  │  • Preserve session state for 5 minutes after disconnect     │  │
│  │  • Resume in-progress tasks if possible                      │  │
│  │  • Notify cloud agent of recovered session                   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Task Recovery                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Strategy: Idempotent operations with status tracking        │  │
│  │                                                               │  │
│  │  Idempotency:                                                 │  │
│  │  • Each task has unique ID                                   │  │
│  │  • Duplicate requests return same result                     │  │
│  │  • No double-execution of side effects                       │  │
│  │                                                               │  │
│  │  Checkpointing:                                               │  │
│  │  • Long tasks checkpoint progress                            │  │
│  │  • Resume from checkpoint after failure                      │  │
│  │  • Maximum recovery time: 30 seconds                         │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Safety Recovery                                                    │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Strategy: Fail-safe defaults with escalation                │  │
│  │                                                               │  │
│  │  Fail-safe behaviors:                                         │  │
│  │  ├── Communication lost: Maintain current safe state         │  │
│  │  ├── Sensor failure: Use last known good value + alert       │  │
│  │  ├── Actuator failure: Disable and alert                     │  │
│  │  └── Safety constraint triggered: Physical interlock         │  │
│  │                                                               │  │
│  │  Escalation:                                                  │  │
│  │  ├── Level 1: Log and continue (minor issues)                │  │
│  │  ├── Level 2: Alert cloud agent (significant issues)         │  │
│  │  └── Level 3: Alert local user (critical issues)             │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

# Part IV: Use Case Scenarios

## 4.1 Cloud Agent Requests Sensor Data

### Scenario Description

A cloud-based personal assistant (e.g., Google Assistant, Alexa) needs to check the temperature at home before suggesting what to wear.

### Message Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  USE CASE 1: CLOUD AGENT REQUESTS SENSOR DATA                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Cloud Assistant                              Device-Native Agent   │
│  ┌──────────────────┐                         ┌──────────────────┐  │
│  │                  │                         │                  │  │
│  │ User asks:       │                         │ (Light sleep)    │  │
│  │ "What should I   │                         │                  │  │
│  │  wear today?"    │                         │                  │  │
│  │                  │                         │                  │  │
│  └────────┬─────────┘                         └────────┬─────────┘  │
│           │                                            │            │
│           │ 1. Decide to check home temperature        │            │
│           │                                            │            │
│           │ 2. REQUEST_DATA                            │            │
│           │ {                                          │            │
│           │   "data_type": "sensor_reading",          │            │
│           │   "sensor_id": "temp_ambient",            │            │
│           │   "include_history": false                │            │
│           │ }                                          │            │
│           │───────────────────────────────────────────►│            │
│           │                                            │            │
│           │                                            │ WAKE       │
│           │                                            │ (~5ms)     │
│           │                                            │            │
│           │                                            │ VERIFY     │
│           │                                            │ (~1ms)     │
│           │                                            │            │
│           │                                            │ READ       │
│           │                                            │ (~5ms)     │
│           │                                            │            │
│           │ 3. DATA_RESPONSE                           │            │
│           │ {                                          │            │
│           │   "status": "success",                     │            │
│           │   "data": {                                │            │
│           │     "value": 18.5,                         │            │
│           │     "unit": "celsius"                      │            │
│           │   }                                        │            │
│           │ }                                          │            │
│           │◄───────────────────────────────────────────│            │
│           │                                            │            │
│           │ 4. Return to sleep                          │            │
│           │                                            │ SLEEP      │
│           │                                            │            │
│           │ Response to user:                           │            │
│           │ "It's 18.5°C at home,                      │            │
│           │  consider a light jacket."                  │            │
│           │                                            │            │
│                                                                      │
│  Total latency: <50ms                                               │
│  Power impact: ~10 mJ (wake + process + sleep)                      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Privacy Considerations

| Data Element | Privacy Level | Handling |
|--------------|---------------|----------|
| Temperature value | SHAREABLE | Transmitted with user consent |
| Timestamp | SENSITIVE | Rounded to nearest minute |
| Sensor ID | LOCAL_ONLY | Translated to generic identifier |
| Location | LOCAL_ONLY | Not transmitted (cloud knows device context) |

## 4.2 Cloud Agent Instructs Device to Perform Action

### Scenario Description

A user at work realizes they left the heating on. They ask their cloud assistant to turn it off.

### Message Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  USE CASE 2: CLOUD AGENT INSTRUCTS DEVICE ACTION                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Cloud Assistant                              Device-Native Agent   │
│  ┌──────────────────┐                         ┌──────────────────┐  │
│  │                  │                         │                  │  │
│  │ User asks:       │                         │ (Active,         │
│  │ "Turn off the    │                         │  monitoring)     │
│  │  heating"        │                         │                  │  │
│  │                  │                         │                  │  │
│  └────────┬─────────┘                         └────────┬─────────┘  │
│           │                                            │            │
│           │ 1. REQUEST_TASK                            │            │
│           │ {                                          │            │
│           │   "task_type": "device_action",            │            │
│           │   "action_id": "set_mode",                 │            │
│           │   "parameters": {                          │            │
│           │     "mode": "off"                          │            │
│           │   },                                       │            │
│           │   "reason": "User request",                │            │
│           │   "delegation_token": "..."                │            │
│           │ }                                          │            │
│           │───────────────────────────────────────────►│            │
│           │                                            │            │
│           │                                            │ VALIDATE   │
│           │                                            │ (~1ms)     │
│           │                                            │            │
│           │                                            │ CHECK      │
│           │                                            │ User       │
│           │                                            │ consent    │
│           │                                            │ (cached)   │
│           │                                            │            │
│           │                                            │ EXECUTE    │
│           │                                            │ (~100ms)   │
│           │                                            │            │
│           │ 2. TASK_RESULT                             │            │
│           │ {                                          │            │
│           │   "status": "success",                     │            │
│           │   "result": {                              │            │
│           │     "previous_mode": "heat",               │            │
│           │     "new_mode": "off",                     │            │
│           │     "effective_at": "..."                  │            │
│           │   }                                        │            │
│           │ }                                          │            │
│           │◄───────────────────────────────────────────│            │
│           │                                            │            │
│           │                                            │ LOG        │
│           │                                            │ audit      │
│           │                                            │ trail      │
│           │                                            │            │
│                                                                      │
│  Total latency: <200ms                                              │
│  Audit: User ID, timestamp, action, result logged                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Safety Validation

```
Safety Checks Performed:
│
├── Hardware Constraints
│   ├── Is "off" a valid mode? ✓
│   ├── Does "off" violate any hard constraints? ✓ No
│   └── Hardware interlock check? ✓ Pass
│
├── Policy Constraints
│   ├── Is user authorized? ✓ (delegation token valid)
│   ├── Is rate limit exceeded? ✓ No
│   └── Is time-based restriction active? ✓ No
│
├── State Validation
│   ├── Is current mode different from requested? ✓ Yes
│   └── Are preconditions met? ✓ Yes
│
└── Result: Action approved, execute immediately
```

## 4.3 Device Agent Initiates Communication

### Scenario Description

The device detects an anomaly (temperature rising unexpectedly when HVAC is off) and proactively alerts the user through their cloud assistant.

### Message Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  USE CASE 3: DEVICE AGENT INITIATES COMMUNICATION                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Device-Native Agent                           Cloud Assistant      │
│  ┌──────────────────┐                          ┌──────────────────┐  │
│  │                  │                          │                  │  │
│  │ (Monitoring)     │                          │                  │  │
│  │                  │                          │                  │  │
│  │ Anomaly detected:│                          │                  │  │
│  │ Temperature      │                          │                  │  │
│  │ rising with      │                          │                  │  │
│  │ HVAC off         │                          │                  │  │
│  │                  │                          │                  │  │
│  └────────┬─────────┘                          └────────┬─────────┘  │
│           │                                             │            │
│           │ NEURAL ANALYSIS                             │            │
│           │ - Temperature: 25°C and rising              │            │
│           │ - HVAC: Off                                 │            │
│           │ - Anomaly confidence: 85%                   │            │
│           │                                             │            │
│           │ DECISION: Alert user                        │            │
│           │                                             │            │
│           │ 1. INITIATE_SESSION                         │            │
│           │ {                                           │            │
│           │   "purpose": "alert",                       │            │
│           │   "priority": "high"                        │            │
│           │ }                                           │            │
│           │────────────────────────────────────────────►│            │
│           │                                             │            │
│           │ 2. ACCEPT_SESSION                           │            │
│           │◄────────────────────────────────────────────│            │
│           │                                             │            │
│           │ 3. NOTIFY_EVENT                             │            │
│           │ {                                           │            │
│           │   "event_type": "anomaly_detected",         │            │
│           │   "severity": "warning",                    │            │
│           │   "data": {                                 │            │
│           │     "anomaly_type": "unexpected_warming",   │            │
│           │     "current_temp": 25.0,                   │            │
│           │     "rate": 0.5,                            │            │
│           │     "unit": "celsius_per_hour",             │            │
│           │     "hvac_status": "off"                    │            │
│           │   },                                        │            │
│           │   "recommendation": "Check for external     │            │
│           │    heat source or turn on cooling",         │            │
│           │   "suggested_actions": [                    │            │
│           │     {"action": "set_mode", "params":        │            │
│           │      {"mode": "cool"}},                     │            │
│           │     {"action": "ignore", "params": {}}      │            │
│           │   ]                                         │            │
│           │ }                                           │            │
│           │────────────────────────────────────────────►│            │
│           │                                             │            │
│           │                                             │ NOTIFY     │
│           │                                             │ user       │
│           │                                             │            │
│           │ 4. EVENT_ACKNOWLEDGED                       │            │
│           │ {                                           │            │
│           │   "user_notified": true,                    │            │
│           │   "notification_method": "push"             │            │
│           │ }                                           │            │
│           │◄────────────────────────────────────────────│            │
│           │                                             │            │
│                                                                      │
│  User receives: "Your thermostat detected unusual warming           │
│                  at home. Temperature is 25°C and rising.           │
│                  Would you like to turn on cooling?"                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Anomaly Detection (Neural)

```python
# Conceptual anomaly detection in mask-locked weights

class AnomalyDetector:
    """
    Anomaly detection implemented in neural network.
    Runs continuously in monitoring mode (55 mW).
    """
    
    def detect(self, sensor_history, device_state):
        """
        Detect anomalies in sensor readings.
        
        Args:
            sensor_history: Recent temperature readings
            device_state: Current HVAC state, mode, etc.
        
        Returns:
            Anomaly assessment with confidence
        """
        
        # Feature extraction (neural forward pass)
        features = self.extract_features(sensor_history, device_state)
        
        # Anomaly scoring
        # - Expected temperature trend based on HVAC state
        # - Comparison with historical patterns
        # - External factors (time of day, season)
        
        anomaly_score = self.score_anomaly(features)
        
        if anomaly_score > THRESHOLD_HIGH:
            return AnomalyDetected(
                type="unexpected_warming",
                confidence=anomaly_score,
                severity="warning",
                recommendation=self.generate_recommendation(features)
            )
        elif anomaly_score > THRESHOLD_LOW:
            return PotentialAnomaly(
                type="unusual_pattern",
                confidence=anomaly_score,
                continue_monitoring=True
            )
        else:
            return NormalOperation()
```

## 4.4 Multi-Device Coordination Through Cloud Agent

### Scenario Description

A user asks their cloud assistant to optimize comfort across multiple devices: thermostat, smart blinds, and ceiling fan. The cloud agent coordinates these device-native agents.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  USE CASE 4: MULTI-DEVICE COORDINATION                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│                        Cloud Orchestrator                            │
│                      ┌───────────────────┐                           │
│                      │                   │                           │
│                      │  Coordination     │                           │
│                      │  Logic            │                           │
│                      │                   │                           │
│                      └─────────┬─────────┘                           │
│                                │                                     │
│           ┌────────────────────┼────────────────────┐               │
│           │                    │                    │               │
│           ▼                    ▼                    ▼               │
│   ┌───────────────┐   ┌───────────────┐   ┌───────────────┐        │
│   │ Thermostat    │   │ Smart Blinds  │   │ Ceiling Fan   │        │
│   │ Agent         │   │ Agent         │   │ Agent         │        │
│   │               │   │               │   │               │        │
│   │ Mask-Locked   │   │ Mask-Locked   │   │ Mask-Locked   │        │
│   │ Chip          │   │ Chip          │   │ Chip          │        │
│   └───────────────┘   └───────────────┘   └───────────────┘        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Coordination Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  MULTI-DEVICE COORDINATION FLOW                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  User │ Cloud Orchestrator │ Thermostat │ Blinds │ Fan              │
│   │         │                    │          │        │               │
│   │ "Optimize│                    │          │        │               │
│   │  comfort"│                    │          │        │               │
│   │─────────►│                    │          │        │               │
│   │         │                    │          │        │               │
│   │         │ 1. REQUEST_DATA    │          │        │               │
│   │         │ (from all devices) │          │        │               │
│   │         │───────────────────►│          │        │               │
│   │         │─────────────────────────────►│        │               │
│   │         │────────────────────────────────────────►│               │
│   │         │                    │          │        │               │
│   │         │ 2. DATA_RESPONSE   │          │        │               │
│   │         │◄───────────────────│          │        │               │
│   │         │◄─────────────────────────────│        │               │
│   │         │◄────────────────────────────────────────│               │
│   │         │                    │          │        │               │
│   │         │ Current state:     │          │        │               │
│   │         │ - Temp: 26°C       │          │        │               │
│   │         │ - Blinds: open     │          │        │               │
│   │         │ - Fan: off         │          │        │               │
│   │         │ - Outside: sunny   │          │        │               │
│   │         │                    │          │        │               │
│   │         │ 3. Plan:           │          │        │               │
│   │         │ - Close blinds 50% │          │        │               │
│   │         │ - Turn on fan low  │          │        │               │
│   │         │ - AC to 24°C       │          │        │               │
│   │         │                    │          │        │               │
│   │         │ 4. REQUEST_TASK    │          │        │               │
│   │         │ (parallel)         │          │        │               │
│   │         │─────────────────────────────►│        │               │
│   │         │────────────────────────────────────────►│               │
│   │         │───────────────────►│          │        │               │
│   │         │                    │          │        │               │
│   │         │ 5. TASK_RESULT     │          │        │               │
│   │         │◄─────────────────────────────│        │               │
│   │         │◄────────────────────────────────────────│               │
│   │         │◄───────────────────│          │        │               │
│   │         │                    │          │        │               │
│   │         │ 6. All actions     │          │        │               │
│   │         │    completed       │          │        │               │
│   │         │                    │          │        │               │
│   │ "Done!   │                    │          │        │               │
│   │  Blinds  │                    │          │        │               │
│   │  half    │                    │          │        │               │
│   │  closed, │                    │          │        │               │
│   │  fan on  │                    │          │        │               │
│   │  low, AC │                    │          │        │               │
│   │  to 24°C"│                    │          │        │               │
│   │◄─────────│                    │          │        │               │
│                                                                      │
│  Coordination time: <2 seconds                                      │
│  Total energy per device: <100 mJ                                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 4.5 Emergency Escalation Protocols

### Scenario Description

The device detects a critical safety condition (e.g., temperature exceeding 40°C, potential fire) and must escalate through multiple channels immediately.

### Escalation Levels

```
┌─────────────────────────────────────────────────────────────────────┐
│  EMERGENCY ESCALATION LEVELS                                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Level 1: Device Autonomous Action (milliseconds)                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Hardware interlocks activate automatically:                  │  │
│  │                                                               │  │
│  │  • Temperature > 40°C: Cut power to heating                  │  │
│  │  • Current surge: Circuit breaker trip                       │  │
│  │  • Gas detection (if equipped): Shut gas valve               │  │
│  │                                                               │  │
│  │  Response time: <1ms (hardware only)                         │  │
│  │  Notification: Log and queue for transmission                │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                           │                                          │
│                           ▼                                          │
│  Level 2: Immediate Alert (seconds)                                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Notify all available channels simultaneously:                │  │
│  │                                                               │  │
│  │  • Cloud agent: EMERGENCY_EVENT message                      │  │
│  │  • Local user: Audio alarm (if speaker)                      │  │
│  │  • Mobile app: Push notification                             │  │
│  │  • Thread mesh: Broadcast to other devices                   │  │
│  │                                                               │  │
│  │  Response time: <5 seconds                                   │  │
│  │  Priority: P0 (highest)                                      │  │
│  │  Retry: Aggressive (no backoff)                              │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                           │                                          │
│                           ▼                                          │
│  Level 3: Cloud Escalation (minutes)                                │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  If no user response in N minutes, escalate externally:       │  │
│  │                                                               │  │
│  │  • Emergency contacts: SMS/call from cloud                   │  │
│  │  • Emergency services: If configured, contact authorities    │  │
│  │  • Neighbors: If opt-in, alert nearby trusted devices        │  │
│  │                                                               │  │
│  │  Timeout: User configurable (default 5 minutes)              │  │
│  │  Requires: Pre-configuration by user                         │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Emergency Message Format

```json
{
  "@context": "https://a2a-protocol.org/context/v1",
  "@type": "EmergencyEventMessage",
  "message_id": "emergency-uuid-v4",
  "timestamp": "2026-01-15T10:30:00.000Z",
  "priority": "P0",
  "emergency": {
    "type": "temperature_critical",
    "severity": "critical",
    "device_action_taken": [
      {
        "action": "power_cutoff",
        "target": "heating_element",
        "timestamp": "2026-01-15T10:30:00.000Z"
      }
    ],
    "current_state": {
      "temperature": 42.5,
      "unit": "celsius",
      "hvac_mode": "off",
      "heating_power": "disabled"
    },
    "historical_data": [
      {"timestamp": "2026-01-15T10:28:00Z", "temp": 38.2},
      {"timestamp": "2026-01-15T10:29:00Z", "temp": 40.1},
      {"timestamp": "2026-01-15T10:30:00Z", "temp": 42.5}
    ],
    "potential_causes": [
      "External heat source",
      "Sensor malfunction",
      "Fire in vicinity"
    ],
    "recommended_user_actions": [
      "Check for fire or smoke",
      "If safe, open windows for ventilation",
      "Call emergency services if fire suspected"
    ]
  },
  "requires_acknowledgment": true,
  "acknowledgment_timeout_ms": 300000
}
```

---

# Part V: Competitive Positioning

## 5.1 Positioning in the A2A Ecosystem

### Unique Value Proposition

```
┌─────────────────────────────────────────────────────────────────────┐
│               MASK-LOCKED CHIP A2A POSITIONING                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Positioning Statement:                                             │
│  "The first hardware to natively speak A2A"                         │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Competitors                 │ Us                             │  │
│  ├───────────────────────────────┼───────────────────────────────┤  │
│  │  Software agents on           │ Hardware agents with           │  │
│  │  general hardware             │ mask-locked intelligence       │  │
│  ├───────────────────────────────┼───────────────────────────────┤  │
│  │  A2A as software layer        │ A2A baked into silicon         │  │
│  ├───────────────────────────────┼───────────────────────────────┤  │
│  │  Model loading latency        │ Zero cold start                │  │
│  ├───────────────────────────────┼───────────────────────────────┤  │
│  │  10-100W power consumption    │ 2-3W power consumption         │  │
│  ├───────────────────────────────┼───────────────────────────────┤  │
│  │  Cloud or powerful edge       │ Any device, anywhere           │  │
│  ├───────────────────────────────┼───────────────────────────────┤  │
│  │  Software-defined safety      │ Hardware-enforced safety       │  │
│  └───────────────────────────────┴───────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Ecosystem Position

```
A2A Ecosystem Map:
│
├── Cloud Platforms
│   ├── Google Cloud (Gemini agents)
│   ├── AWS (Bedrock agents)
│   ├── Azure (Copilot agents)
│   └── Anthropic (Claude agents)
│       └── These need device endpoints → OUR OPPORTUNITY
│
├── Agent Frameworks
│   ├── LangGraph, AutoGen, CrewAI
│   └── Need device integration → OUR OPPORTUNITY
│
├── Enterprise Software
│   ├── Salesforce, SAP, ServiceNow
│   └── Need device data → OUR OPPORTUNITY
│
├── Device Manufacturers
│   ├── Consumer IoT (thermostats, lights, etc.)
│   ├── Industrial IoT (sensors, actuators)
│   ├── Medical devices
│   └── These need A2A capability → OUR SOLUTION
│
└── Semiconductor Companies
    ├── NVIDIA (high-end)
    ├── Intel (datacenter)
    ├── Qualcomm (mobile)
    └── US (device-native A2A) → UNIQUE POSITION
```

## 5.2 Potential Partnership with Google/Anthropic

### Google Partnership Opportunity

| Partnership Type | Description | Value to Google | Value to Us |
|------------------|-------------|-----------------|-------------|
| **Technical Collaboration** | Co-develop device agent profile | Extends A2A to billions of devices | Credibility, early access |
| **Reference Implementation** | Our chip as A2A device reference | Demonstrates protocol completeness | Marketing leverage |
| **Integration Partnership** | Pre-integrated with Google Assistant | Better smart home experience | Distribution channel |
| **Investment** | Strategic investment | Hardware ecosystem play | Capital + validation |

### Anthropic Partnership Opportunity

| Partnership Type | Description | Value to Anthropic | Value to Us |
|------------------|-------------|-------------------|-------------|
| **MCP Integration** | Our chip as MCP tool endpoint | Physical world access for Claude | Claude ecosystem access |
| **Safety Collaboration** | Hardware safety patterns | Embodied AI safety insights | Safety expertise |
| **Model Optimization** | Optimize Claude models for our chip | Edge deployment of Claude | Access to frontier models |

### Partnership Strategy

```
Partnership Approach:
│
├── Phase 1: Technical Contribution (Months 1-6)
│   ├── Contribute device agent profile to A2A spec
│   ├── Publish open-source reference implementation
│   └── Demonstrate interoperability with Google/Anthropic agents
│
├── Phase 2: Partnership Discussions (Months 6-12)
│   ├── Engage Google A2A team
│   ├── Engage Anthropic MCP team
│   └── Explore investment opportunities
│
├── Phase 3: Formal Partnership (Months 12-18)
│   ├── Announce strategic partnership
│   ├── Co-marketing at I/O, developer events
│   └── Integration with flagship products
│
└── Phase 4: Deep Integration (Months 18+)
    ├── Optimized models for our architecture
    ├── Joint go-to-market
    └── Potential acquisition discussion
```

## 5.3 Standards Body Participation Strategy

### Standards Organizations

| Organization | Relevance | Participation Goal |
|--------------|-----------|-------------------|
| **A2A Working Group** | Core protocol development | Drive device agent profile |
| **W3C Web of Things** | IoT standards | Align A2A with WoT |
| **IETF** | Transport protocols | Influence A2A transport bindings |
| **IEEE** | Hardware standards | Define hardware certification |
| **IIC (Industrial Internet Consortium)** | Industrial IoT | Position for industrial adoption |

### Contribution Strategy

```
Standards Contribution Roadmap:
│
├── Immediate (Q1 2026)
│   ├── Submit "Device Agent Profile" proposal to A2A WG
│   ├── Define hardware capability declaration format
│   └── Propose safety constraint integration
│
├── Near-term (Q2-Q3 2026)
│   ├── Lead "Low-Power Agent" working group
│   ├── Contribute reference implementation
│   └── Propose certification criteria
│
├── Medium-term (Q4 2026 - Q2 2027)
│   ├── Co-edit A2A Device Agent specification
│   ├── Establish hardware testing framework
│   └── Publish interoperability test suite
│
└── Long-term (2027+)
    ├── Drive A2A 2.0 device requirements
    ├── Establish certification program
    └── Influence regulatory frameworks
```

## 5.4 "First Hardware to Natively Speak A2A" Positioning

### Marketing Narrative

```
┌─────────────────────────────────────────────────────────────────────┐
│                   MARKETING NARRATIVE                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  The Agentic Internet Needs Hardware Foundation                     │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  "Every device will soon have an AI agent.                    │  │
│  │   But today, those agents run as software on servers,         │  │
│  │  consuming gigawatts and introducing latency.                 │  │
│  │                                                               │  │
│  │  The Mask-Locked Inference Chip is the first hardware        │  │
│  │  purpose-built for the agentic internet—where AI agents       │  │
│  │  are first-class citizens, not software afterthoughts.        │  │
│  │                                                               │  │
│  │  Our chips don't run AI. They ARE AI."                        │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Key Messages:                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  1. First-to-market: No other hardware speaks A2A natively   │  │
│  │  2. Standards leadership: We're defining how devices talk    │  │
│  │  3. Performance advantage: 100x more efficient than software │  │
│  │  4. Safety advantage: Hardware-enforced constraints          │  │
│  │  5. Privacy advantage: Data never leaves device unnecessarily│  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Competitive Comparison

| Capability | Software Agent (Cloud) | Software Agent (Edge GPU) | Mask-Locked DNA |
|------------|------------------------|---------------------------|-----------------|
| A2A Native | No (adapter needed) | No (adapter needed) | **Yes (hardware)** |
| Cold Start Latency | 100-500ms | 500-2000ms | **0ms** |
| Power (active) | 100-500W | 10-50W | **2-3W** |
| Power (idle) | 50-200W | 5-10W | **55mW** |
| Always-on | Expensive | Possible | **Native** |
| Hardware Safety | None | None | **Hardware interlocks** |
| Privacy | Cloud processing | Edge processing | **On-device only** |
| Cost per unit | Cloud pricing | $200-500 | **$35-60** |
| Billions of devices | No | No | **Yes** |

---

# Part VI: Future Evolution

## 6.1 How A2A Might Evolve

### Near-Term Evolution (2026-2027)

```
A2A Protocol Evolution Predictions:
│
├── Specification Evolution
│   ├── Device agent profile (our contribution)
│   ├── Offline/intermittent connectivity handling
│   ├── Privacy-preserving computation
│   ├── Safety constraint integration
│   └── Multi-modal agent communication
│
├── Ecosystem Evolution
│   ├── Agent marketplaces
│   ├── Capability discovery directories
│   ├── Trust/reputation systems
│   ├── Agent insurance/liability frameworks
│   └── Regulatory compliance tools
│
├── Technical Evolution
│   ├── More efficient binary protocols
│   ├── Hardware acceleration standards
│   ├── Edge-to-edge communication (bypassing cloud)
│   └── Quantum-resistant cryptography
│
└── Application Evolution
    ├── Autonomous negotiation
    ├── Multi-agent planning
    ├── Federated learning among agents
    └── Agent swarm coordination
```

### Long-Term Vision (2027-2030)

```
┌─────────────────────────────────────────────────────────────────────┐
│                 A2A LONG-TERM VISION                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  2027: The Device Agent Explosion                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Every new appliance, vehicle, and industrial device          │  │
│  │  ships with an A2A-capable agent.                             │  │
│  │                                                               │  │
│  │  Device-native agents become the norm.                        │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  2028: The Agent Economy                                            │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Agents negotiate on behalf of users:                         │  │
│  │  - Energy trading between devices                             │  │
│  │  - Service contracts with other agents                        │  │
│  │  - Autonomous purchasing decisions                            │  │
│  │                                                               │  │
│  │  Hardware agents are trusted more than cloud agents           │  │
│  │  for sensitive operations.                                    │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  2029: The Embodied Agent Standard                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Physical robots, vehicles, and industrial equipment          │  │
│  │  coordinate via A2A.                                          │  │
│  │                                                               │  │
│  │  Mask-locked chips become standard in safety-critical         │  │
│  │  systems where software agents cannot be trusted.             │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  2030: The Global Agent Mesh                                        │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Billions of agents form a global mesh, coordinating          │  │
│  │  energy, transportation, healthcare, and daily life.          │  │
│  │                                                               │  │
│  │  Hardware agents handle the majority of device                │  │
│  │  interactions, with cloud agents providing                    │  │
│  │  orchestration and complex reasoning.                         │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 6.2 Ensuring Forward Compatibility

### Compatibility Strategy

```
┌─────────────────────────────────────────────────────────────────────┐
│               FORWARD COMPATIBILITY STRATEGY                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Strategy 1: Protocol Versioning                                    │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Implement robust version negotiation:                        │  │
│  │                                                               │  │
│  │  • Firmware supports multiple A2A versions                   │  │
│  │  • Graceful degradation to older versions                    │  │
│  │  • Capability flags for optional features                    │  │
│  │  • Version-agnostic message parsing where possible           │  │
│  │                                                               │  │
│  │  Firmware updates enable new protocol features               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Strategy 2: Extensibility Points                                   │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Design for extension:                                        │  │
│  │                                                               │  │
│  │  • Reserved message type ranges for future use               │  │
│  │  • Extensible capability schema                              │  │
│  │  • Unknown field handling (ignore vs error)                  │  │
│  │  • Plugin architecture for custom message types              │  │
│  │                                                               │  │
│  │  Firmware updates add new capability handlers                │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Strategy 3: Model Adaptability                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Mask-locked model designed for adaptability:                │  │
│  │                                                               │  │
│  │  • Protocol handling uses general patterns                   │  │
│  │  • New message types learned from few-shot examples          │  │
│  │  • Intent classification extensible via prompt engineering   │  │
│  │  • Safety rules parameterized in mutable memory              │  │
│  │                                                               │  │
│  │  New behaviors via prompt updates (if supported)             │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Strategy 4: Hardware Headroom                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Design hardware with margin:                                 │  │
│  │                                                               │  │
│  │  • Extra SRAM for larger contexts                            │  │
│  │  • Reserved compute cycles for new operations                │  │
│  │  • GPIO/I2C/SPI pins for future sensors                      │  │
│  │  • Flash space for firmware updates                          │  │
│  │                                                               │  │
│  │  Hardware lasts multiple protocol generations                │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Update Mechanisms

```
Firmware Update Architecture:
│
├── Signed Updates Only
│   ├── Firmware signed by manufacturer
│   ├── Signature verified by hardware root of trust
│   └── Prevents malicious updates
│
├── A/B Partitioning
│   ├── Two firmware partitions
│   ├── Update writes to inactive partition
│   ├── Bootloader verifies before switching
│   └── Automatic rollback on failure
│
├── Delta Updates
│   ├── Send only changed portions
│   ├── Reduces bandwidth requirement
│   └── Faster update cycle
│
├── Update Triggers
│   ├── User-initiated (via app)
│   ├── Scheduled maintenance window
│   ├── Critical security update (forced)
│   └── A2A protocol update notification
│
└── Update Constraints
    ├── Battery level requirement (>20%)
    ├── Network requirement (stable connection)
    ├── User consent (for non-critical)
    └── Maintenance window (configurable)
```

## 6.3 Hardware Upgrade Path Considerations

### Multi-Generation Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│               HARDWARE GENERATION ROADMAP                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Generation 1 (2026): Foundation                                    │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Model: 2B parameters, ternary/iFairy                         │  │
│  │  Context: 512 tokens                                          │  │
│  │  Transport: WiFi, BLE discovery                               │  │
│  │  A2A: v1.0 compliant                                          │  │
│  │  Process: 28nm                                                │  │
│  │  Price: $35-60                                                │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                           │                                          │
│                           ▼                                          │
│  Generation 2 (2027): Enhanced                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Model: 3B parameters, improved quantization                  │  │
│  │  Context: 1024 tokens                                         │  │
│  │  Transport: WiFi 6, Thread mesh, BLE 5.3                      │  │
│  │  A2A: v1.0 + device profile extensions                        │  │
│  │  Process: 22nm (optional) or 28nm optimized                   │  │
│  │  Price: $45-70                                                │  │
│  │                                                               │  │
│  │  New capabilities:                                            │  │
│  │  • Multi-modal input (audio, simple vision)                  │  │
│  │  • Federated learning participation                          │  │
│  │  • Enhanced privacy (on-device differential privacy)         │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                           │                                          │
│                           ▼                                          │
│  Generation 3 (2028): Advanced                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Model: 5B parameters, next-gen quantization                  │  │
│  │  Context: 2048 tokens                                         │  │
│  │  Transport: WiFi 7, Thread 1.4, BLE 6.0                       │  │
│  │  A2A: v2.0 (agent-to-agent negotiation)                       │  │
│  │  Process: 22nm or 14nm (if cost-effective)                    │  │
│  │  Price: $55-80                                                │  │
│  │                                                               │  │
│  │  New capabilities:                                            │  │
│  │  • Autonomous task planning                                  │  │
│  │  • Multi-agent coordination leadership                       │  │
│  │  • Advanced reasoning (chain-of-thought)                     │  │
│  │  • Edge-to-edge agent communication                          │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                           │                                          │
│                           ▼                                          │
│  Generation 4 (2029+): Intelligent                                  │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Model: 7-10B parameters, breakthrough architectures          │  │
│  │  Context: 4096+ tokens                                        │  │
│  │  Transport: WiFi 7/8, Thread 2.0, next-gen mesh               │  │
│  │  A2A: v3.0 (autonomous negotiation, economy)                  │  │
│  │  Process: Advanced node (TBD based on market)                 │  │
│  │  Price: Target <$100                                           │  │
│  │                                                               │  │
│  │  New capabilities:                                            │  │
│  │  • Full autonomy within constraints                          │  │
│  │  • Economic participation (agent transactions)               │  │
│  │  • Collaborative learning                                    │  │
│  │  • Universal agent interoperability                          │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Migration Path for Customers

```
Customer Migration Strategy:
│
├── Software Compatibility
│   ├── Same A2A interface across generations
│   ├── New features discoverable via capability negotiation
│   ├── Legacy devices continue to function
│   └── Gradual adoption of new capabilities
│
├── Hardware Compatibility
│   ├── Same physical form factor (where possible)
│   ├── Same pinout for drop-in replacement
│   ├── Backward-compatible I/O interfaces
│   └── Migration guide for new features
│
├── Ecosystem Compatibility
│   ├── Existing integrations continue working
│   ├── New devices join existing networks
│   ├── Multi-generation coordination supported
│   └── Cloud agent handles capability differences
│
└── Upgrade Incentives
    ├── Trade-in program for Gen 1 → Gen 2
    ├── Subscription model for always-current hardware
    ├── Enterprise upgrade paths
    └── Developer program for early access
```

---

# Appendix A: Quick Reference

## A2A Message Types Summary

| Type Code | Message Type | Direction | Purpose |
|-----------|--------------|-----------|---------|
| 0x0001 | BEACON | Device→Any | Discovery broadcast |
| 0x0002 | QUERY_CAPABILITIES | Any→Device | Request agent card |
| 0x0003 | ADVERTISE_CAPABILITIES | Device→Any | Provide agent card |
| 0x0010 | INITIATE_SESSION | Client→Device | Start connection |
| 0x0011 | ACCEPT_SESSION | Device→Client | Confirm connection |
| 0x0012 | AUTHENTICATE | Bidirectional | Verify identity |
| 0x0013 | TERMINATE_SESSION | Bidirectional | End connection |
| 0x0020 | REQUEST_TASK | Client→Device | Delegate work |
| 0x0021 | TASK_STATUS | Device→Client | Progress update |
| 0x0022 | TASK_RESULT | Device→Client | Final output |
| 0x0023 | TASK_ERROR | Device→Client | Failure notice |
| 0x0030 | REQUEST_DATA | Client→Device | Ask for information |
| 0x0031 | DATA_RESPONSE | Device→Client | Provide information |
| 0x0032 | DATA_DENIED | Device→Client | Refuse access |
| 0x0033 | DATA_STREAM | Device→Client | Continuous feed |
| 0x0040 | CONSENT_REQUEST | Device→Client | Ask user consent |
| 0x0041 | CONSENT_GRANTED | Client→Device | User approved |
| 0x0042 | CONSENT_DENIED | Client→Device | User rejected |

## Transport Quick Reference

| Transport | Use Case | Bandwidth | Latency | Power |
|-----------|----------|-----------|---------|-------|
| WiFi 6 | Primary communication | 1+ Gbps | 1-10ms | High |
| BLE 5.3 | Discovery, pairing | 2 Mbps | 10-50ms | Low |
| Thread | IoT mesh, industrial | 250 Kbps | 20-100ms | Low |
| Ethernet | Fixed installations | 100+ Mbps | <1ms | Medium |

## Privacy Level Summary

| Level | Description | Sharing Policy |
|-------|-------------|----------------|
| LOCAL_ONLY | Never leaves device | Never shared |
| ANONYMIZED | Aggregate only | With differential privacy |
| SHAREABLE | Current values | With authentication |
| SENSITIVE | Historical/detail | With explicit consent |

## Safety Constraint Levels

| Level | Enforcement | Response Time | Override |
|-------|-------------|---------------|----------|
| Hardware Interlock | Physical circuit | Nanoseconds | Impossible |
| Neural Constraint | Mask-locked weights | Microseconds | Impossible |
| Policy Runtime | Software check | Milliseconds | User authorized |

---

# Appendix B: Glossary

| Term | Definition |
|------|------------|
| **A2A** | Agent-to-Agent Protocol - Open standard for AI agent communication |
| **ACP** | Agent Communication Protocol - IBM's alternative to A2A |
| **Agent Card** | JSON-LD document describing an agent's capabilities |
| **BLE** | Bluetooth Low Energy - Used for discovery |
| **CBOR** | Concise Binary Object Representation - Binary JSON alternative |
| **DID** | Decentralized Identifier - Self-sovereign identity |
| **DNA** | Device-Native Agent - Agent with mask-locked intelligence |
| **MCP** | Model Context Protocol - Anthropic's agent-to-tool protocol |
| **mTLS** | Mutual TLS - Bidirectional certificate authentication |
| **RAU** | Rotation-Accumulate Unit - Compute element for iFairy |
| **Thread** | IPv6 mesh networking protocol for IoT |

---

*Document prepared for: Mask-Locked Inference Chip Development*  
*Version: 1.0*  
*Date: January 2026*
