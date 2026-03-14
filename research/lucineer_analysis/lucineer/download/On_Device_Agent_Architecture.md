# On-Device Agent Architecture
## Hardware Foundation for the Agentic Internet

**Document Version**: 1.0  
**Date**: January 2026  
**Classification**: Technical Specification Document  
**Status**: Architecture Definition

---

# Executive Summary

This document defines the **Device-Native Agent Architecture**—a paradigm where AI agents are not software abstractions running on general-purpose hardware, but **first-class hardware citizens** embedded directly into device silicon via mask-locked neural network weights.

The Mask-Locked Inference Chip enables a fundamentally new agent model:
- **Permanent Intelligence**: Agent knowledge encoded in silicon, immutable and always available
- **Zero-Energy Weight Access**: No memory bandwidth bottleneck for agent reasoning
- **Milliwatt Operation**: Always-on agents monitoring device state
- **Hardware-Enforced Privacy**: No data leaves the device without explicit user consent

This architecture transforms every enabled device into an autonomous agent node in the emerging **Agentic Internet**—a global network of AI agents communicating via the A2A protocol.

---

# Part I: Core Architecture

## 1.1 The Device-Native Agent Concept

### Definition

A **Device-Native Agent (DNA)** is an AI agent whose core reasoning model is permanently encoded in the hardware's metal interconnect layers. Unlike software agents that load models into memory, the DNA's intelligence is:

1. **Physically Present**: Weights hardwired in silicon routing
2. **Instantly Available**: No model loading, no cold start
3. **Immutable**: Core agent behavior cannot be modified by software attacks
4. **Zero Marginal Access Cost**: Reading weights costs no energy

### Architectural Principles

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEVICE-NATIVE AGENT                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         MASK-LOCKED WEIGHT LAYER (Permanent)              │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐         │  │
│  │  │ Layer 1 │ │ Layer 2 │ │  ...    │ │ Layer N │         │  │
│  │  │ Weights │ │ Weights │ │ Weights │ │ Weights │         │  │
│  │  │ (Metal) │ │ (Metal) │ │ (Metal) │ │ (Metal) │         │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘         │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         RUNTIME STATE (Mutable, SRAM)                     │  │
│  │  ┌────────────┐ ┌────────────┐ ┌─────────────────────┐   │  │
│  │  │ KV Cache   │ │ Activation │ │ Device State        │   │  │
│  │  │ 42 MB      │ │ Buffers    │ │ Registry            │   │  │
│  │  │ (Sliding)  │ │ 8 MB       │ │ 256 KB              │   │  │
│  │  └────────────┘ └────────────┘ └─────────────────────┘   │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         SYSTOLIC COMPUTE ARRAY                             │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │ 32×32 Processing Elements (1024 RAUs)               │ │  │
│  │  │ Weight-stationary, iFairy complex-valued ops        │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │         I/O INTERFACE LAYER                               │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │  │
│  │  │ A2A      │ │ Device   │ │ User     │ │ Safety   │     │  │
│  │  │ Protocol │ │ Sensors  │ │ Interface│ │ Monitor  │     │  │
│  │  │ Stack    │ │ & GPIO   │ │ (USB/UART)│ │ (HW)     │     │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 1.2 Agent Knowledge Encoding

### Four Knowledge Domains

The mask-locked model encodes four distinct knowledge domains:

| Domain | Description | Encoding Method | Size (est.) |
|--------|-------------|-----------------|-------------|
| **World Knowledge** | General language understanding, reasoning | Pre-trained LLM weights | 1.8B params |
| **Device Schema** | This device's capabilities, APIs, constraints | Special token embeddings + fine-tuning | 100M params |
| **Safety Rules** | What the agent must never do | Constitutional AI fine-tuning | 50M params |
| **Protocol Handlers** | A2A message parsing, capability negotiation | Specialized attention heads | 50M params |

### Device Schema Token Vocabulary

```
Special Token Range: [0xF000 - 0xFFFF]

Device Capability Tokens:
  0xF000: <SENSOR_START>
  0xF001 - 0xF01F: Sensor type identifiers (temp, pressure, etc.)
  0xF020: <ACTUATOR_START>
  0xF021 - 0xF03F: Actuator type identifiers
  0xF040: <API_START>
  0xF041 - 0xF0FF: Device-specific API tokens

Safety Constraint Tokens:
  0xF100: <SAFETY_HARD>
  0xF101 - 0xF110: Hard constraint types
  0xF120: <SAFETY_SOFT>
  0xF121 - 0xF130: Soft constraint types

State Tokens:
  0xF200: <STATE_READ>
  0xF201: <STATE_WRITE>
  0xF202 - 0xF2FF: State variable tokens
```

## 1.3 Memory Architecture

### Three-Tier Memory Hierarchy

```
Tier 0: Mask-Locked Weights (Permanent)
├── Size: 2B parameters × 2 bits = 500 MB equivalent
├── Access Energy: 0 pJ (hardwired routing)
├── Bandwidth: Infinite (weights always present at PE)
└── Persistence: Lifetime of device

Tier 1: On-Chip SRAM (Fast Mutable State)
├── KV Cache: 42 MB (512-token sliding window + 4 attention sinks)
├── Activation Buffers: 8 MB (per-layer activations)
├── Device State Registry: 256 KB
├── Message Buffers: 1 MB (A2A queue)
├── Total: ~51 MB
├── Access Energy: 1-5 pJ/bit
├── Bandwidth: On-demand (no external bus)
└── Technology: 28nm SRAM compiler

Tier 2: External Flash (Configuration, Logs)
├── Size: 16 MB (typical)
├── Access: Via SPI interface
├── Purpose: User preferences, audit logs, firmware updates
└── NOT for model weights (those are hardwired)
```

### KV Cache Architecture Details

```
Per-Layer KV Storage:
┌──────────────────────────────────────────────────────────┐
│ Key Cache (K):  [SINK_4][SLIDING_WINDOW_508]             │
│ Value Cache (V): [SINK_4][SLIDING_WINDOW_508]            │
│                                                          │
│ Total per layer: 2 × d × 512 × b                        │
│   For d=2560, b=0.5 bytes (INT4):                       │
│   = 2 × 2560 × 512 × 0.5 = 1.31 MB                      │
│                                                          │
│ All 32 layers: 1.31 MB × 32 = 42 MB                     │
└──────────────────────────────────────────────────────────┘

Cache Management Policy:
- Permanent: First 4 tokens (attention sinks)
- Sliding: Most recent 508 tokens
- Eviction: FIFO for sliding portion
- No compression (maintains quality)
```

## 1.4 I/O Interface Architecture

### Interface Block Diagram

```
                    ┌──────────────────────────────┐
                    │     DEVICE-NATIVE AGENT      │
                    └──────────────────────────────┘
                           │         │
           ┌───────────────┼─────────┼───────────────┐
           │               │         │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──▼─────────────▼───┐
    │   A2A I/F   │ │   Device    │ │    User I/F        │
    │   (WiFi/    │ │   Sensor    │ │    (USB/UART)      │
    │   Thread/   │ │   Bridge    │ │                    │
    │   BLE)      │ │             │ │                    │
    └──────┬──────┘ └──────┬──────┘ └────────┬───────────┘
           │               │                  │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌────────▼───────────┐
    │ Network     │ │ GPIO/ADC/   │ │ Serial Interface   │
    │ Stack       │ │ I2C/SPI     │ │ CDC-ACM            │
    │ (TCP/UDP)   │ │ Interfaces  │ │ Protocol           │
    └─────────────┘ └─────────────┘ └────────────────────┘
```

### Pin Configuration (48-pin QFN Package)

| Pin Group | Pins | Function | Bandwidth |
|-----------|------|----------|-----------|
| Power | 8 | VDD, GND, VDDIO | 3W max |
| USB | 4 | USB 2.0 D+/D-/VBUS | 480 Mbps |
| Network | 4 | SPI for WiFi/BLE module | 50 Mbps |
| Sensors | 16 | GPIO/ADC/I2C/SPI | Configurable |
| Debug | 8 | JTAG, UART | Debug only |
| Reserved | 8 | Future expansion | — |

### Bandwidth Requirements

```
Agent Reasoning:
- Input: User query ~500 tokens = 1 KB
- Output: Response ~200 tokens = 400 bytes
- Latency: <100ms first token
- Throughput: 80+ tokens/second

Device I/O:
- Sensor polling: 1-10 KB/s typical
- Actuator commands: <1 KB/s
- State updates: Event-driven

A2A Protocol:
- Discovery beacons: 100 bytes/broadcast
- Capability exchange: 1-5 KB/negotiation
- Task messages: 1-10 KB typical
- Privacy-filtered data: Variable
```

## 1.5 Power Domains

### Power Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    POWER MANAGEMENT                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Domain 0   │  │  Domain 1   │  │  Domain 2   │         │
│  │  (Always-On)│  │  (Active)   │  │  (Standby)  │         │
│  │             │  │             │  │             │         │
│  │ • Safety    │  │ • Compute   │  │ • External  │         │
│  │   Monitor   │  │   Array     │  │   Memory    │         │
│  │ • Wake      │  │ • KV Cache  │  │ • Network   │         │
│  │   Logic     │  │ • Activations│  │   I/F       │         │
│  │ • GPIO      │  │             │  │ • USB       │         │
│  │   Monitor   │  │             │  │             │         │
│  │             │  │             │  │             │         │
│  │  ~5 mW      │  │  ~2W active │  │  ~100 mW    │         │
│  │  continuous │  │  ~50 mW idle│  │  when active│         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  Domain Transitions:                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Deep     │  │ Light    │  │ Active   │  │ Turbo    │   │
│  │ Sleep    │→ │ Sleep    │→ │ Reasoning│→ │ Burst    │   │
│  │ 0.5 mW   │  │ 5 mW     │  │ 2W       │  │ 3W       │   │
│  │ <100 mW  │  │ <10 ms   │  │ Normal   │  │ Max perf │   │
│  │ wake     │  │ wake     │  │          │  │          │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Power Budget by Operating Mode

| Mode | Domain 0 | Domain 1 | Domain 2 | Total | Duration |
|------|----------|----------|----------|-------|----------|
| Deep Sleep | 0.5 mW | Off | Off | 0.5 mW | Days |
| Light Sleep | 5 mW | 5 mW | Off | 10 mW | Hours |
| Monitoring | 5 mW | 50 mW | Off | 55 mW | Continuous |
| Active Reasoning | 5 mW | 2W | 100 mW | 2.1W | Minutes |
| Turbo Mode | 5 mW | 2.5W | 500 mW | 3W | Seconds |

---

# Part II: Agent Capability Model

## 2.1 Self-Description System

### Capability Declaration Schema

Every Device-Native Agent exposes a structured capability declaration:

```json
{
  "agent_identity": {
    "agent_id": "uuid-v4-generated-at-first-boot",
    "device_class": "thermostat|medical_monitor|sensor|hub",
    "manufacturer": "string",
    "model": "string",
    "firmware_version": "semver",
    "hardware_revision": "string"
  },
  "capabilities": {
    "sensors": [
      {
        "sensor_id": "temp_ambient",
        "type": "temperature",
        "unit": "celsius",
        "range": [-20, 60],
        "resolution": 0.1,
        "update_rate": "1Hz",
        "access": "read"
      }
    ],
    "actuators": [
      {
        "actuator_id": "hvac_control",
        "type": "relay",
        "states": ["off", "heat", "cool"],
        "safety_constraints": ["max_cycle_rate_4_per_hour"],
        "access": "write"
      }
    ],
    "apis": [
      {
        "api_id": "set_temperature",
        "parameters": [
          {"name": "target", "type": "float", "range": [15, 30]}
        ],
        "returns": "success|error",
        "safety": "requires_user_consent"
      }
    ]
  },
  "constraints": {
    "hard_constraints": [
      {
        "constraint_id": "max_temp",
        "description": "Never set temperature above 30°C",
        "enforcement": "hardware"
      },
      {
        "constraint_id": "no_remote_override",
        "description": "Local user presence required for safety changes",
        "enforcement": "hardware"
      }
    ],
    "soft_constraints": [
      {
        "constraint_id": "energy_saving",
        "description": "Prefer energy-efficient schedules",
        "priority": "medium"
      }
    ]
  },
  "state": {
    "exposed_state": [
      {
        "state_id": "current_temperature",
        "type": "float",
        "access": "read",
        "privacy": "local_only"
      },
      {
        "state_id": "operating_mode",
        "type": "enum",
        "values": ["home", "away", "sleep"],
        "access": "read_write",
        "privacy": "shareable_anonymized"
      }
    ]
  }
}
```

### Self-Description Token Encoding

The capability schema is encoded in the agent's embedded knowledge:

```
Token Sequence for Capability Declaration:
┌────────┬─────────────┬────────────────────────────────────┐
│ Token  │ Meaning     │ Description                        │
├────────┼─────────────┼────────────────────────────────────┤
│ 0xF000 │ <CAP_START> │ Beginning of capability block      │
│ 0xF001 │ <SENSOR>    │ Following tokens describe sensor   │
│ 0x0042 │ "temp"      │ Sensor type (from vocab)           │
│ 0xF010 │ <RANGE>     │ Range follows                      │
│ -20    │ INT16       │ Range minimum                      │
│ 60     │ INT16       │ Range maximum                      │
│ ...    │ ...         │ ...                                │
│ 0xF0FF │ <CAP_END>   │ End of capability block            │
└────────┴─────────────┴────────────────────────────────────┘
```

## 2.2 Intent Understanding Pipeline

### Processing Stages

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTENT UNDERSTANDING PIPELINE                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Stage 1: Input Parsing                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ User Input → Tokenizer → [tokens]                         │   │
│  │                                                            │   │
│  │ Sources:                                                   │   │
│  │ • Direct user text (USB/UART)                             │   │
│  │ • A2A protocol message (network)                          │   │
│  │ • Sensor event trigger (device)                           │   │
│  │ • Scheduled task (internal)                               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  Stage 2: Context Integration                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ [tokens] + Device_State → Contextualized_Input            │   │
│  │                                                            │   │
│  │ Device State Injected:                                     │   │
│  │ • Current sensor readings                                  │   │
│  │ • Operating mode                                           │   │
│  │ • Recent action history                                    │   │
│  │ • Active constraints                                       │   │
│  │ • User preferences                                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  Stage 3: Intent Classification                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Contextualized_Input → Intent_Vector                      │   │
│  │                                                            │   │
│  │ Intent Categories (special tokens):                        │   │
│  │ • 0xFA00: <QUERY> (information request)                   │   │
│  │ • 0xFA01: <ACTION> (device control)                       │   │
│  │ • 0xFA02: <CONFIGURE> (settings change)                   │   │
│  │ • 0xFA03: <REPORT> (status/telemetry)                     │   │
│  │ • 0xFA04: <NEGOTIATE> (A2A capability exchange)           │   │
│  │ • 0xFA05: <CLARIFY> (need more information)               │   │
│  │ • 0xFA06: <REJECT> (safety violation)                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  Stage 4: Parameter Extraction                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Intent_Vector + Input → Structured_Command                │   │
│  │                                                            │   │
│  │ Example:                                                   │   │
│  │ Input: "Set temperature to 22 degrees"                    │   │
│  │ → Intent: ACTION                                           │   │
│  │ → Target: set_temperature API                             │   │
│  │ → Parameters: {target: 22}                                 │   │
│  │ → Confidence: 0.95                                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  Stage 5: Safety Validation                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Structured_Command → Safety_Check → Validated_Command     │   │
│  │                                                            │   │
│  │ Check Against:                                             │   │
│  │ • Hard constraints (hardware-enforced)                    │   │
│  │ • Soft constraints (policy-based)                         │   │
│  │ • User consent requirements                               │   │
│  │ • Rate limiting                                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Intent Classification Confusion Matrix (Target)

| True Intent | QUERY | ACTION | CONFIGURE | REJECT |
|-------------|-------|--------|-----------|--------|
| QUERY | 98% | 1% | 0.5% | 0.5% |
| ACTION | 0.5% | 97% | 1.5% | 1% |
| CONFIGURE | 0.5% | 1% | 97% | 1.5% |
| REJECT | 0% | 0% | 0% | 100% |

Note: REJECT intent has 100% precision requirement—any potential safety violation must be flagged.

## 2.3 Action Planning System

### Planning Algorithm

```
FUNCTION PlanAction(intent, parameters, device_state):
  
  1. VALIDATE INPUT
     IF parameters.out_of_range:
       RETURN ClarificationRequest("Parameter out of valid range")
     
  2. CHECK PRECONDITIONS
     FOR each precondition IN action.preconditions:
       IF NOT precondition.satisfied(device_state):
         RETURN ActionImpossible(precondition.reason)
     
  3. GENERATE ACTION SEQUENCE
     IF intent.is_simple:
       action_sequence = [SingleAction(intent, parameters)]
     ELSE:
       action_sequence = DecomposeComplexAction(intent, parameters)
     
  4. VERIFY SAFETY
     FOR each action IN action_sequence:
       IF action.violates_hard_constraint:
         RETURN SafetyRejection(action, constraint)
       IF action.violates_soft_constraint:
         action.add_warning(soft_constraint.warning)
     
  5. CHECK USER CONSENT
     IF intent.requires_consent AND NOT user_consent_present:
       RETURN ConsentRequest(intent, parameters, risk_explanation)
     
  6. RETURN ActionPlan(action_sequence, estimated_duration, 
                       resource_usage, safety_warnings)
```

### Action Decomposition Example

```
Intent: "Optimize for energy saving while keeping comfortable"

Decomposition:
1. CHECK current_temperature, current_mode
2. READ user_preferences.comfort_range
3. READ energy_price_schedule (if available)
4. COMPUTE optimal_setpoint_curve
5. GENERATE schedule:
   - 06:00-08:00: 20°C (wake up)
   - 08:00-18:00: 16°C (away)
   - 18:00-22:00: 21°C (evening)
   - 22:00-06:00: 18°C (sleep)
6. PREVIEW schedule to user
7. AWAIT confirmation
8. IF confirmed: APPLY schedule
```

## 2.4 Safety Enforcement Architecture

### Three-Level Safety Model

```
┌─────────────────────────────────────────────────────────────────┐
│                    SAFETY ENFORCEMENT LEVELS                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Level 0: Hardware Interlock (NANOMETER-LEVEL)                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Physical circuits that CANNOT be overridden by software  │   │
│  │                                                            │   │
│  │ Examples:                                                  │   │
│  │ • Thermal cutoff relay (max 30°C enforcement)            │   │
│  │ • Current limiter for actuators                           │   │
│  │ • Watchdog timer for response liveness                   │   │
│  │ • Secure boot verification                                │   │
│  │                                                            │   │
│  │ Response time: Nanoseconds                                │   │
│  │ Override: IMPOSSIBLE                                      │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Level 1: Mask-Locked Constraints (MICROSECOND-LEVEL)           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Neural network weights encoding safety rules             │   │
│  │                                                            │   │
│  │ The agent CANNOT generate unsafe outputs because:        │   │
│  │ • Safety tokens have fixed embeddings                     │   │
│  │ • Attention patterns trained to reject unsafe actions    │   │
│  │ • Output vocabulary restricted for safety-critical APIs  │   │
│  │                                                            │   │
│  │ Response time: Microseconds (one forward pass)           │   │
│  │ Override: IMPOSSIBLE (weights in silicon)                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Level 2: Policy Runtime (MILLISECOND-LEVEL)                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Software checks on mutable state                          │   │
│  │                                                            │   │
│  │ Examples:                                                  │   │
│  │ • Rate limiting (no more than X actions per minute)      │   │
│  │ • Time-based restrictions (no changes during night)      │   │
│  │ • User consent verification                               │   │
│  │ • Anomaly detection on sensor readings                   │   │
│  │                                                            │   │
│  │ Response time: Milliseconds                               │   │
│  │ Override: User with proper authentication                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Safety Constraint Encoding

```python
# Example safety constraint for thermostat
HARD_CONSTRAINTS = {
    "max_temperature": {
        "value": 30,  # degrees celsius
        "enforcement": "hardware",  # relay cutoff
        "neural_embedding": 0xF101,  # token ID
        "reason": "Fire safety regulation"
    },
    "min_temperature": {
        "value": 10,
        "enforcement": "neural",  # mask-locked
        "neural_embedding": 0xF102,
        "reason": "Pipe freeze prevention"
    }
}

SOFT_CONSTRAINTS = {
    "energy_saving_mode": {
        "priority": "medium",
        "conditions": ["user_away", "scheduled_night"],
        "adjustment": -2,  # lower by 2 degrees
        "user_override": True
    }
}
```

## 2.5 State Management

### State Registry Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    STATE REGISTRY (256 KB)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Partition 0: Agent State (64 KB)                               │
│  ├── Current operating mode: 4 bytes                           │
│  ├── Last action timestamp: 8 bytes                            │
│  ├── Pending actions queue: 4 KB                               │
│  ├── Conversation context: 16 KB                               │
│  └── A2A session state: 8 KB                                   │
│                                                                  │
│  Partition 1: Device State (64 KB)                              │
│  ├── Sensor readings array: 8 KB                               │
│  ├── Actuator states: 4 KB                                     │
│  ├── Configuration snapshot: 16 KB                             │
│  └── Diagnostic data: 36 KB                                    │
│                                                                  │
│  Partition 2: User State (64 KB)                               │
│  ├── User preferences: 16 KB                                   │
│  ├── Consent flags: 4 KB                                       │
│  ├── Interaction history: 32 KB                                │
│  └── Personalization data: 12 KB                               │
│                                                                  │
│  Partition 3: Safety State (64 KB)                             │
│  ├── Constraint violation log: 16 KB                           │
│  ├── Anomaly detection state: 16 KB                            │
│  ├── Audit trail: 32 KB                                        │
│  └── Checkpoint data for recovery                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### State Update Protocol

```
STATE UPDATE FLOW:

1. SENSOR UPDATE (Interrupt-driven)
   ├── Sensor interrupt → Read value
   ├── Update State Registry (Partition 1)
   ├── Check against thresholds
   └── IF threshold crossed → Wake agent

2. ACTUATOR UPDATE (Command-driven)
   ├── Receive command → Validate
   ├── Update actuator hardware
   ├── Update State Registry (Partition 1)
   ├── Log to Audit Trail (Partition 3)
   └── Acknowledge to caller

3. USER STATE UPDATE (Explicit)
   ├── Receive user preference change
   ├── Validate against constraints
   ├── Update State Registry (Partition 2)
   ├── Log to Audit Trail
   └── Confirm to user

4. AGENT STATE UPDATE (Autonomous)
   ├── Agent decision made
   ├── Update internal state (Partition 0)
   ├── IF action taken → Update Partition 1 & 3
   └── Continue or sleep
```

---

# Part III: A2A Protocol Integration

## 3.1 A2A Protocol Overview

The Agent-to-Agent (A2A) protocol is an open standard for AI agent interoperability. Device-Native Agents are **first-class citizens** in the A2A ecosystem.

### Protocol Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                    A2A PROTOCOL STACK                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Layer 7: Application (Agent Semantics)                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • Intent exchange                                         │   │
│  │ • Capability negotiation                                  │   │
│  │ • Task delegation                                         │   │
│  │ • Result reporting                                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Layer 6: Agent Description Language                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • Agent Card (JSON-LD)                                    │   │
│  │ • Capability Schema                                       │   │
│  │ • Semantic Annotations                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Layer 5: Session Management                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • Connection establishment                                │   │
│  │ • Authentication (mutual)                                 │   │
│  │ • Session state                                           │   │
│  │ • Graceful termination                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Layer 4: Message Transport                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • Message framing                                         │   │
│  │ • Sequence numbers                                        │   │
│  │ • Acknowledgment                                          │   │
│  │ • Retransmission                                          │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Layer 3: Network Layer                                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • WiFi (802.11)                                          │   │
│  │ • Thread (802.15.4)                                      │   │
│  │ • BLE (for discovery)                                    │   │
│  │ • Ethernet (optional)                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 3.2 Discovery Mechanism

### Local Discovery (BLE Beacons)

```
BLE Advertisement Packet Format:
┌────────────────────────────────────────────────────────────────┐
│ Preamble │ Access Addr │ PDU │ CRC │                           │
└────────────────────────────────────────────────────────────────┘
                           │
                     ┌─────▼─────┐
                     │ A2A-ADV   │
                     │ Service   │
                     │ UUID      │
                     └─────┬─────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌─────▼─────┐     ┌─────▼─────┐
    │ Agent   │      │ Device    │     │ Capability│
    │ ID      │      │ Class     │     │ Hash      │
    │ 16 B    │      │ 2 B       │     │ 4 B       │
    └─────────┘      └───────────┘     └───────────┘

Total: 31 bytes (fits in single BLE advertisement)
```

### Network Discovery (mDNS/DNS-SD)

```
mDNS Service Registration:
_service._a2a._tcp.local. → Agent Instance

TXT Records:
├── agent_id=<uuid>
├── device_class=<class>
├── capabilities_hash=<sha256_truncated>
├── api_version=1.0
├── auth_methods=["certificate", "token"]
└── privacy_level=<local|anonymized|full>

Discovery Query:
cloud_agent → mDNS query → _a2a._tcp.local.
device_agent → mDNS response → Agent Instance + TXT

Follow-up: HTTP GET to agent/.well-known/agent.json for full Agent Card
```

### Discovery Sequence Diagram

```
Cloud Agent          Network            Device-Native Agent
    │                  │                      │
    │  mDNS Query      │                      │
    │  (_a2a._tcp)     │                      │
    │─────────────────>│                      │
    │                  │   mDNS Response      │
    │                  │<─────────────────────│
    │                  │   (Agent Card URL)   │
    │<─────────────────│                      │
    │                  │                      │
    │  HTTP GET agent.json                   │
    │─────────────────────────────────────────>│
    │                  │                      │
    │  HTTP 200 (Agent Card)                 │
    │<─────────────────────────────────────────│
    │                  │                      │
    │  [Parse capabilities]                   │
    │  [Decide to interact]                   │
    │                  │                      │
    │  A2A Session Init                      │
    │─────────────────────────────────────────>│
    │                  │                      │
```

## 3.3 Capability Negotiation

### Agent Card Structure

```json
{
  "@context": "https://a2a-protocol.org/context/v1",
  "agent_id": "urn:uuid:550e8400-e29b-41d4-a716-446655440000",
  "agent_type": "Device-Native",
  "name": "Smart Thermostat Agent",
  "description": "Manages HVAC control with safety constraints",
  "version": "1.0.0",
  "capabilities": {
    "inputs": [
      {
        "name": "temperature_query",
        "type": "query",
        "description": "Query current temperature",
        "parameters": {},
        "returns": {"type": "float", "unit": "celsius"}
      },
      {
        "name": "set_temperature",
        "type": "action",
        "description": "Set target temperature",
        "parameters": {
          "target": {"type": "float", "range": [15, 30], "unit": "celsius"}
        },
        "requires_consent": true,
        "safety_rating": "medium"
      }
    ],
    "outputs": [
      {
        "name": "temperature_reading",
        "type": "telemetry",
        "frequency": "1Hz",
        "privacy": "local_only"
      },
      {
        "name": "mode_change_event",
        "type": "event",
        "privacy": "shareable_anonymized"
      }
    ]
  },
  "constraints": {
    "hard": [
      {
        "type": "range",
        "parameter": "target",
        "min": 15,
        "max": 30,
        "reason": "Safety limits"
      }
    ],
    "rate_limits": {
      "set_temperature": {"max": 4, "window": "1h"}
    }
  },
  "authentication": {
    "methods": ["certificate", "pre-shared-key"],
    "certificate_url": "https://device.local/cert.pem"
  },
  "privacy": {
    "data_classification": "personal",
    "sharing_policy": "user_consent_required",
    "retention": "7d"
  }
}
```

### Negotiation Protocol

```
NEGOTIATION FLOW:

1. CAPABILITY EXCHANGE
   Cloud Agent                     Device-Native Agent
       │                                │
       │  Agent Card Request            │
       │───────────────────────────────>│
       │                                │
       │  Agent Card                    │
       │<───────────────────────────────│
       │                                │
       │  [Analyze capabilities]        │
       │                                │
       │  Task Request                  │
       │  (with required capabilities)  │
       │───────────────────────────────>│
       │                                │
       │  Capability Match Response     │
       │  (accept/reject/partial)       │
       │<───────────────────────────────│
       │                                │

2. TASK NEGOTIATION (if partial match)
       │                                │
       │  Alternative Task Proposal     │
       │<───────────────────────────────│
       │                                │
       │  Accept/Modify/Reject          │
       │───────────────────────────────>│
       │                                │

3. PRIVACY NEGOTIATION
       │                                │
       │  Data Request                  │
       │  (specifies fields needed)     │
       │───────────────────────────────>│
       │                                │
       │  Privacy Filter Response       │
       │  (what can be shared)          │
       │<───────────────────────────────│
       │                                │
       │  Consent Request (if needed)   │
       │───────────────────────────────>│
       │                                │
       │  User Consent Result           │
       │<───────────────────────────────│
       │                                │

4. SESSION ESTABLISHMENT
       │                                │
       │  Session Start                 │
       │  (session_id, parameters)      │
       │───────────────────────────────>│
       │                                │
       │  Session Accept                │
       │  (session_id, auth_token)      │
       │<───────────────────────────────│
       │                                │
```

## 3.4 Message Format

### A2A Message Structure

```
Message Header (16 bytes):
┌────────────────────────────────────────────────────────────────┐
│ 0x00-0x03 │ Magic Number (0xA2A2A2A2)                         │
│ 0x04-0x07 │ Protocol Version (0x00010000 = v1.0)              │
│ 0x08-0x0B │ Message Type                                     │
│ 0x0C-0x0F │ Message Length (excluding header)                 │
└────────────────────────────────────────────────────────────────┘

Message Types:
├── 0x0001: CAPABILITY_QUERY
├── 0x0002: CAPABILITY_RESPONSE
├── 0x0003: TASK_REQUEST
├── 0x0004: TASK_RESPONSE
├── 0x0005: TASK_STATUS
├── 0x0006: DATA_REQUEST
├── 0x0007: DATA_RESPONSE
├── 0x0008: CONSENT_REQUEST
├── 0x0009: CONSENT_RESPONSE
├── 0x000A: ERROR
└── 0x000B: HEARTBEAT

Message Body (variable):
┌────────────────────────────────────────────────────────────────┐
│ Session ID (16 bytes)                                          │
│ Sequence Number (4 bytes)                                      │
│ Timestamp (8 bytes)                                            │
│ Payload Length (4 bytes)                                       │
│ Payload (JSON or binary)                                       │
│ Signature (32 bytes, Ed25519)                                  │
└────────────────────────────────────────────────────────────────┘
```

### Example Message: Task Request

```json
{
  "message_type": "TASK_REQUEST",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "sequence": 1,
  "timestamp": "2026-01-15T10:30:00Z",
  "task": {
    "task_id": "task_001",
    "action": "set_temperature",
    "parameters": {
      "target": 22.0
    },
    "priority": "normal",
    "deadline": "2026-01-15T10:35:00Z",
    "requester": "cloud_agent_12345"
  },
  "metadata": {
    "reason": "User requested via mobile app",
    "user_id_hash": "sha256:user_email"
  }
}
```

### Example Message: Task Response

```json
{
  "message_type": "TASK_RESPONSE",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "sequence": 2,
  "timestamp": "2026-01-15T10:30:01Z",
  "response_to": 1,
  "status": "accepted",
  "task_id": "task_001",
  "execution_plan": {
    "steps": [
      {
        "step_id": 1,
        "action": "verify_range",
        "status": "completed",
        "result": "valid"
      },
      {
        "step_id": 2,
        "action": "check_user_consent",
        "status": "required",
        "consent_token": "consent_abc123"
      }
    ],
    "estimated_completion": "2026-01-15T10:30:10Z"
  }
}
```

## 3.5 Privacy-Preserving Data Exchange

### Privacy Filter Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                  PRIVACY FILTER PIPELINE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Stage 1: Data Classification                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Input Data → Classify by sensitivity                      │   │
│  │                                                            │   │
│  │ Levels:                                                    │   │
│  │ • PUBLIC: Can be freely shared                            │   │
│  │ • ANONYMIZED: Aggregated/timestamps removed               │   │
│  │ • LOCAL_ONLY: Never leaves device                         │   │
│  │ • SENSITIVE: Requires explicit consent                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  Stage 2: Filter Application                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ FOR each data_field IN request:                          │   │
│  │   IF field.level == LOCAL_ONLY:                          │   │
│  │     REMOVE field from response                            │   │
│  │   ELIF field.level == ANONYMIZED:                        │   │
│  │     APPLY anonymization(field)                            │   │
│  │   ELIF field.level == SENSITIVE:                         │   │
│  │     IF NOT consent_present(field):                       │   │
│  │       REQUEST consent or REMOVE field                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  Stage 3: Differential Privacy (Optional)                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ IF requested_data is aggregate:                           │   │
│  │   ADD calibrated noise (Laplace mechanism)               │   │
│  │   ε = privacy_budget_per_request                          │   │
│  │   Total ε tracked per day, resets at midnight            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  Stage 4: Output Validation                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Verify no PII leaked                                      │   │
│  │ Log data exchange for audit                               │   │
│  │ Return filtered response                                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Anonymization Techniques

| Data Type | Technique | Example |
|-----------|-----------|---------|
| Temperature | Rounding, jitter | 22.347°C → 22.0°C |
| Timestamp | Bucketing | 10:34:27 → 10:30-10:45 window |
| Location | Geo-hashing | Precise → 100m grid |
| User ID | Pseudonymization | user@email.com → hash123 |
| Usage patterns | Aggregation | Individual → cohort stats |

---

# Part IV: Implementation Specifications

## 4.1 Model Architecture

### Recommended: Hybrid Ternary-Complex Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  MODEL ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Embedding Layer (INT8, Learned)                                │
│  ├── Vocabulary: 65,536 tokens                                  │
│  ├── Dimension: 2560                                            │
│  ├── Size: 65,536 × 2560 × 1 byte = 160 MB (in metal)          │
│  └── Includes special device capability tokens                  │
│                                                                  │
│  Transformer Layers × 32                                        │
│  ├── Attention (iFairy Complex-Valued)                         │
│  │   ├── Q, K, V projections: {±1, ±i} weights                │
│  │   ├── Output projection: {±1, ±i} weights                  │
│  │   └── Per-layer params: ~20M (2 bits each)                 │
│  │                                                              │
│  ├── Feed-Forward (BitNet Ternary)                             │
│  │   ├── Up projection: {-1, 0, +1} weights                   │
│  │   ├── Down projection: {-1, 0, +1} weights                 │
│  │   └── Per-layer params: ~40M (1.58 bits each)              │
│  │                                                              │
│  └── Layer Norm (FP16, per-device tunable)                     │
│      └── Per-layer params: ~10K × 2 bytes = 20 KB              │
│                                                                  │
│  Output Head (Ternary)                                          │
│  ├── Project to vocabulary: 2560 → 65,536                      │
│  ├── Tied with embeddings (optional)                           │
│  └── Size: Saved if tied                                       │
│                                                                  │
│  Total Parameters: ~2B                                          │
│  Average bits per param: ~1.8                                   │
│  Total storage: ~450 MB equivalent                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Layer-Type Assignment Rationale

| Layer Type | Weight Type | Reasoning |
|------------|-------------|-----------|
| Attention projections | iFairy {±1, ±i} | Better rotational invariance for attention patterns |
| FFN layers | BitNet ternary | Sparsity benefits, zero-weight skipping |
| Layer norms | FP16 | Small size, critical for stability |
| Embeddings | INT8 | Vocabulary size, standard practice |

## 4.2 Quantization Strategy

### Weight Quantization

```
QUANTIZATION SCHEME:

1. Pre-training: Full precision (FP32)
   
2. Fine-tuning Phase 1: Ternary quantization-aware training
   ├── Straight-through estimator for gradients
   ├── Learnable scaling factors per layer
   └── Sparsity-inducing regularization

3. Fine-tuning Phase 2: Complex-valued conversion
   ├── Map ternary → complex with learned rotations
   ├── Joint optimization of real/imaginary components
   └── Fine-tune on device-specific tasks

4. Calibration: Layer norm scales
   ├── Run calibration dataset through model
   ├── Collect activation statistics
   ├── Set layer norm parameters
   └── These are the ONLY per-device adjustable parameters

5. Freezing: Convert to mask-locked weights
   ├── Generate GDSII layout
   ├── Route weights as metal interconnect patterns
   └── Permanent, immutable storage
```

### Activation Quantization

```
Activation Precision:

Input Activations: INT8
├── Dynamic range: [-128, 127]
├── Scale factor per layer: learned during training
└── Quantization: Symmetric, per-tensor

KV Cache: INT4
├── 4 bits per key/value element
├── Per-head scaling factors
├── Calibration on held-out data
└── Quality impact: <2% perplexity increase

Accumulators: INT32
├── Full precision accumulation
├── Prevents overflow in long sequences
└── Saturating arithmetic for safety
```

## 4.3 Memory Requirements by Device Class

### Memory Tiers

| Device Class | SRAM | Flash | External DRAM | Use Case |
|--------------|------|-------|---------------|----------|
| **Minimal** | 16 MB | 4 MB | None | Simple sensors, single function |
| **Standard** | 42 MB | 16 MB | None | Smart home devices, appliances |
| **Extended** | 64 MB | 32 MB | Optional 256 MB | Complex devices, medical |
| **Hub** | 128 MB | 64 MB | 512 MB | Gateway devices, coordinators |

### Memory Allocation (Standard Device)

```
ON-CHIP SRAM (42 MB):
├── KV Cache: 32 MB (512 token context, INT4)
├── Activation buffers: 6 MB (layer outputs)
├── State registry: 256 KB
├── Message queues: 2 MB
├── Working memory: 1.744 MB
└── ECC overhead: ~2 MB (5% overhead)

FLASH (16 MB):
├── Agent configuration: 1 MB
├── User preferences: 1 MB
├── Audit logs: 4 MB (rolling)
├── Calibration data: 1 MB
├── Firmware backup: 4 MB
└── Reserved: 5 MB

MASK-LOCKED WEIGHTS (not in memory budget):
└── Equivalent to 450 MB, stored in metal layers
```

### Area Impact

```
28nm SRAM: 6 Mbit/mm² (SRAM compiler)

SRAM Area by Device Class:
├── Minimal (16 MB): 16 × 8 / 6 ≈ 21 mm²
├── Standard (42 MB): 42 × 8 / 6 ≈ 56 mm²
├── Extended (64 MB): 64 × 8 / 6 ≈ 85 mm²
└── Hub (128 MB): 128 × 8 / 6 ≈ 171 mm²

Note: Standard device may require die size optimization or
external LPDDR4 for extended KV cache.
```

## 4.4 Power Profiles

### Power Budget Analysis

```
COMPONENT POWER BREAKDOWN (Standard Device):

Active Reasoning Mode:
├── Compute Array (1024 RAUs @ 250MHz): 0.5W
├── SRAM Access (42 MB, 80 tok/s): 0.8W
├── Control Logic: 0.2W
├── I/O (USB/Network): 0.3W
├── Leakage (28nm): 0.2W
└── TOTAL: 2.0W

Monitoring Mode (always-on):
├── Safety Monitor (hardware): 0.005W
├── Sensor Polling: 0.01W
├── Wake Logic: 0.005W
├── Leakage: 0.1W (power-gated arrays)
└── TOTAL: 0.12W

Deep Sleep:
├── RTC + Wake Logic: 0.0005W
└── TOTAL: 0.5 mW
```

### Power Management States

```
┌─────────────────────────────────────────────────────────────────┐
│                    POWER STATE MACHINE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    Sensor Event    ┌──────────┐                  │
│  │  DEEP    │ ─────────────────> │ MONITOR  │                  │
│  │  SLEEP   │                    │          │                  │
│  │ 0.5 mW   │ <───────────────── │ 120 mW   │                  │
│  └──────────┘    Timeout         └────┬─────┘                  │
│       ▲                              │                          │
│       │                              │ User/A2A Request         │
│       │                              ▼                          │
│       │     Timeout           ┌──────────┐                      │
│       └────────────────────── │ ACTIVE   │                      │
│                                │ 2.0W     │                      │
│                                └────┬─────┘                      │
│                                     │                            │
│                                     │ Burst Task                 │
│                                     ▼                            │
│                                ┌──────────┐                      │
│                                │ TURBO    │                      │
│                                │ 3.0W     │                      │
│                                └──────────┘                      │
│                                                                  │
│  Transition Times:                                               │
│  ├── Deep Sleep → Monitor: 100 ms                               │
│  ├── Monitor → Active: 10 ms                                    │
│  ├── Active → Turbo: 1 ms                                       │
│  └── Any → Deep Sleep: 50 ms                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Battery Life Calculations

| Power Source | Capacity | Typical Use | Battery Life |
|--------------|----------|-------------|--------------|
| Coin cell (CR2032) | 220 mAh | Monitoring only | 6 months |
| AA battery | 2500 mAh | 10 queries/day | 1 year |
| USB (5V/500mA) | Unlimited | Continuous | N/A |
| Solar (indoor) | 10-50 mW | Low-power mode | Self-sustaining |

## 4.5 Security Model

### Hardware-Enforced Security

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Trust Root (Hardware)                                          │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • Secure boot ROM (mask-locked, immutable)               │   │
│  │ • Device unique key (PUF-derived)                        │   │
│  │ • Hardware true random number generator                  │   │
│  │ • Debug access control (permanently disabled in prod)    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Authentication Layer                                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • Mutual TLS for A2A connections                         │   │
│  │ • Per-session ephemeral keys                             │   │
│  │ • Certificate pinning to manufacturer CA                 │   │
│  │ • User presence detection for sensitive operations       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Data Protection                                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • All external communications encrypted (TLS 1.3)        │   │
│  │ • User data encrypted at rest (AES-256-GCM)             │   │
│  │ • Keys derived from device PUF + user password           │   │
│  │ • Secure key storage in hardware (no software access)    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Integrity Protection                                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • Mask-locked weights: Tamper-evident by design          │   │
│  │ • Firmware: Signed + verified on each boot               │   │
│  │ • Configuration: HMAC-protected                          │   │
│  │ • Audit log: Append-only, hash-chained                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  Isolation Boundaries                                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ • Agent logic: Mask-locked (cannot be modified)          │   │
│  │ • Mutable state: Memory-protected regions                │   │
│  │ • Network stack: Sandboxed from agent core               │   │
│  │ • User data: Separate encrypted partition                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Attack Surface Analysis

| Attack Vector | Mitigation | Residual Risk |
|---------------|------------|---------------|
| Model extraction | Weights in metal, cannot be read | None |
| Firmware tampering | Secure boot, signed updates | Very Low |
| Side-channel (power) | Constant-time operations | Low |
| Network MITM | TLS 1.3, certificate pinning | Very Low |
| Physical tampering | PUF keys, tamper detection | Medium |
| Memory extraction | Encrypted, keys in hardware | Low |

---

# Part V: Example Device Implementations

## 5.1 Smart Thermostat Agent

### Device Profile

```
┌─────────────────────────────────────────────────────────────────┐
│              SMART THERMOSTAT AGENT SPECIFICATION               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Device Class: Standard                                         │
│  Power Source: 24V AC (HVAC system) or USB                      │
│  Form Factor: Wall-mounted touchscreen                          │
│                                                                  │
│  Sensors:                                                        │
│  ├── Temperature (ambient): 0.1°C resolution, 1 Hz             │
│  ├── Temperature (remote, optional): via BLE sensor            │
│  ├── Humidity: 1% resolution, 0.1 Hz                           │
│  ├── Occupancy: PIR sensor, event-driven                       │
│  └── Light: Ambient light for display brightness               │
│                                                                  │
│  Actuators:                                                      │
│  ├── HVAC relay: Heat/Cool/Fan control                         │
│  ├── Display: 3.5" color touchscreen                           │
│  └── Status LED: Operating mode indicator                      │
│                                                                  │
│  APIs:                                                           │
│  ├── set_temperature(target) → success/error                   │
│  ├── set_mode(home|away|sleep|schedule) → success/error        │
│  ├── get_status() → {temp, humidity, mode, setpoint}           │
│  └── schedule_set(timeslot, setpoint) → success/error          │
│                                                                  │
│  Hard Constraints:                                               │
│  ├── Temperature range: 10-30°C (hardware enforced)            │
│  ├── Cycle rate: Max 4 cycles/hour (protect compressor)        │
│  └── Remote override: Requires local confirmation              │
│                                                                  │
│  Soft Constraints:                                               │
│  ├── Energy saving: Prefer 0.5°C below user setpoint           │
│  └── Comfort learning: Adapt to user patterns                  │
│                                                                  │
│  Memory Configuration:                                           │
│  ├── SRAM: 42 MB (standard)                                    │
│  ├── Flash: 16 MB                                              │
│  └── No external DRAM required                                 │
│                                                                  │
│  Power Budget:                                                   │
│  ├── Idle: 50 mW (display off, monitoring)                     │
│  ├── Active display: 500 mW                                    │
│  ├── Active reasoning: 2W                                      │
│  └── Peak (turbo): 3W                                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Sample Interactions

```
USER: "What's the temperature?"

AGENT RESPONSE:
┌─────────────────────────────────────────────────┐
│ The current temperature is 21.3°C.              │
│ Humidity is at 45%.                             │
│ The system is in 'home' mode,                   │
│ setpoint is 22°C.                               │
│                                                 │
│ Would you like me to adjust anything?           │
└─────────────────────────────────────────────────┘

---

USER: "Set it to 23 degrees"

AGENT RESPONSE:
┌─────────────────────────────────────────────────┐
│ I'll set the temperature to 23°C.               │
│                                                 │
│ [CONFIRM] [CANCEL]                              │
└─────────────────────────────────────────────────┘

[User confirms]

AGENT RESPONSE:
┌─────────────────────────────────────────────────┐
│ Done! Temperature set to 23°C.                  │
│ The HVAC will start heating shortly.            │
│                                                 │
│ Current: 21.3°C → Target: 23.0°C               │
└─────────────────────────────────────────────────┘

---

CLOUD AGENT (via A2A):
"Request energy report for the past week"

AGENT RESPONSE:
┌─────────────────────────────────────────────────┐
│ A2A_DATA_RESPONSE                               │
│                                                 │
│ privacy_level: anonymized                       │
│ data: {                                         │
│   "period": "2026-01-08 to 2026-01-14",        │
│   "avg_temperature": 21.2,                      │
│   "hvac_runtime_hours": 42.3,                   │
│   "estimated_energy_kwh": 125,                  │
│   "efficiency_score": "good"                    │
│ }                                               │
│                                                 │
│ Note: Exact temperatures and times             │
│ withheld per privacy policy.                    │
└─────────────────────────────────────────────────┘
```

## 5.2 Medical Device Monitoring Agent

### Device Profile

```
┌─────────────────────────────────────────────────────────────────┐
│           MEDICAL DEVICE MONITORING AGENT SPECIFICATION         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Device Class: Extended (with external DRAM option)             │
│  Power Source: Medical-grade power supply + battery backup      │
│  Form Factor: Bedside monitor or integrated device              │
│  Certification: FDA Class II (software component)               │
│                                                                  │
│  Sensors:                                                        │
│  ├── Vital signs: Heart rate, SpO2, blood pressure             │
│  ├── Temperature: Core and skin temperature                     │
│  ├── Respiration: Rate and pattern                              │
│  ├── Patient movement: Accelerometer                            │
│  └── Device status: Battery, connectivity, calibration         │
│                                                                  │
│  Actuators:                                                      │
│  ├── Display: Medical-grade touchscreen                         │
│  ├── Alarms: Visual and audible alerts                          │
│  └── Data transmission: Secure channel to hospital system      │
│                                                                  │
│  APIs:                                                           │
│  ├── get_vitals() → {hr, spo2, bp, temp, resp}                 │
│  ├── get_trend(vital, period) → time series                     │
│  ├── set_alarm_thresholds(vital, min, max) → success/error     │
│  └── acknowledge_alarm(alarm_id) → success/error               │
│                                                                  │
│  Hard Constraints:                                               │
│  ├── Alarm cannot be disabled remotely                          │
│  ├── Patient data never leaves device unencrypted              │
│  ├── All actions logged with timestamp                         │
│  ├── Fail-safe: Default to alert on sensor failure             │
│  └── Calibration required after power cycle                    │
│                                                                  │
│  Privacy:                                                        │
│  ├── HIPAA compliant data handling                             │
│  ├── All external data transmission encrypted                   │
│  ├── Local-only processing for raw sensor data                 │
│  └── Audit trail for all data access                           │
│                                                                  │
│  Memory Configuration:                                           │
│  ├── SRAM: 64 MB (extended for trend storage)                  │
│  ├── Flash: 32 MB (audit logs, calibration)                    │
│  └── LPDDR4: 256 MB (extended trend analysis)                  │
│                                                                  │
│  Power Budget:                                                   │
│  ├── Normal monitoring: 1W                                      │
│  ├── Active reasoning: 2W                                       │
│  ├── Alarm active: 3W                                           │
│  └── Battery backup: 8 hours operation                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Safety-Critical Response Example

```
SENSOR EVENT: SpO2 drops to 88% (threshold: 90%)

AGENT AUTONOMOUS RESPONSE:
┌─────────────────────────────────────────────────────────────────┐
│ ALARM TRIGGERED                                                  │
│                                                                  │
│ Event: SpO2 below threshold                                     │
│ Current: 88%                                                    │
│ Threshold: 90%                                                  │
│ Timestamp: 2026-01-15T14:32:15Z                                │
│                                                                  │
│ Actions Taken:                                                   │
│ ├── Visual alarm: RED flashing display                         │
│ ├── Audio alarm: Medium priority tone                          │
│ ├── Trend analysis: SpO2 declining over past 5 minutes         │
│ ├── Hospital system notification: Sent via secure channel      │
│ └── Log entry: Created with full context                       │
│                                                                  │
│ Awaiting nurse acknowledgment...                                │
└─────────────────────────────────────────────────────────────────┘

---

NURSE ACKNOWLEDGES ALARM

AGENT RESPONSE:
┌─────────────────────────────────────────────────────────────────┐
│ ALARM ACKNOWLEDGED                                               │
│                                                                  │
│ Acknowledged by: Nurse Smith (badge: 12345)                     │
│ Timestamp: 2026-01-15T14:32:45Z                                │
│ Response time: 30 seconds                                       │
│                                                                  │
│ Continuing enhanced monitoring...                               │
│ Alarm will re-trigger if SpO2 < 85%                            │
└─────────────────────────────────────────────────────────────────┘
```

## 5.3 Industrial Sensor Agent

### Device Profile

```
┌─────────────────────────────────────────────────────────────────┐
│              INDUSTRIAL SENSOR AGENT SPECIFICATION              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Device Class: Standard (ruggedized)                            │
│  Power Source: 24V DC industrial supply                         │
│  Form Factor: DIN rail mounted                                  │
│  Environment: -20°C to 60°C, IP65 rated                         │
│                                                                  │
│  Sensors:                                                        │
│  ├── Vibration: Tri-axial accelerometer, 10 kHz               │
│  ├── Temperature: RTD sensor, -40 to 200°C                     │
│  ├── Pressure: 0-100 bar range                                 │
│  ├── Flow: Ultrasonic flow meter                               │
│  └── Current: Motor current draw                               │
│                                                                  │
│  Actuators:                                                      │
│  ├── Relay outputs: Alarm triggers                             │
│  ├── 4-20mA output: Process control signal                     │
│  └── Status indicators: LED array                              │
│                                                                  │
│  APIs:                                                           │
│  ├── get_measurement(sensor_id) → value + quality              │
│  ├── get_health_score() → equipment health index               │
│  ├── set_threshold(sensor, alert_level) → success/error        │
│  └── calibrate(sensor_id, reference) → success/error          │
│                                                                  │
│  Hard Constraints:                                               │
│  ├── Never issue control commands directly                     │
│  ├── Alert on anomaly detection (cannot be disabled)           │
│  ├── Calibration schedule enforced                             │
│  └── All data tagged with quality indicator                    │
│                                                                  │
│  Predictive Maintenance:                                         │
│  ├── Vibration pattern analysis (bearing wear)                 │
│  ├── Temperature trend analysis (thermal stress)               │
│  ├── Current signature analysis (motor health)                 │
│  └── Remaining useful life estimation                          │
│                                                                  │
│  Memory Configuration:                                           │
│  ├── SRAM: 42 MB (standard)                                    │
│  ├── Flash: 32 MB (extended logging)                           │
│  └── No external DRAM                                           │
│                                                                  │
│  Power Budget:                                                   │
│  ├── Normal: 100 mW (continuous monitoring)                    │
│  ├── Active analysis: 500 mW                                   │
│  └── Peak: 1W (during anomaly detection)                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Predictive Maintenance Interaction

```
CLOUD AGENT (via A2A):
"Request health assessment for pump P-101"

AGENT RESPONSE:
┌─────────────────────────────────────────────────────────────────┐
│ A2A_DATA_RESPONSE                                                │
│                                                                  │
│ equipment_id: pump_P-101                                         │
│ assessment:                                                      │
│   overall_health: 78%                                           │
│   confidence: 0.92                                               │
│                                                                  │
│ indicators:                                                      │
│   bearing_wear:                                                  │
│     status: warning                                              │
│     trend: +15% vibration over 30 days                          │
│     predicted_failure: 45-60 days                               │
│                                                                  │
│   motor_health:                                                  │
│     status: normal                                               │
│     current_draw: 12.3A (nominal: 12.0A)                        │
│                                                                  │
│   thermal:                                                       │
│     status: normal                                               │
│     temperature: 65°C (max: 80°C)                               │
│                                                                  │
│ recommendation: Schedule bearing inspection within 30 days      │
│                                                                  │
│ data_freshness: 2026-01-15T10:00:00Z                           │
└─────────────────────────────────────────────────────────────────┘

---

ANOMALY DETECTION EVENT:

AGENT AUTONOMOUS RESPONSE:
┌─────────────────────────────────────────────────────────────────┐
│ ALERT: Vibration anomaly detected                               │
│                                                                  │
│ equipment_id: pump_P-101                                         │
│ sensor: vibration_z_axis                                         │
│ value: 4.2 mm/s (threshold: 3.5 mm/s)                          │
│                                                                  │
│ Pattern:                                                        │
│ ├── Harmonic at 1x RPM: Increasing amplitude                   │
│ ├── Harmonic at 4x RPM: New emergence                          │
│ └── Pattern match: 87% similarity to bearing failure #2341     │
│                                                                  │
│ Actions:                                                         │
│ ├── Local relay: Triggered (alert to control system)           │
│ ├── Trend logging: Accelerated sampling initiated              │
│ ├── A2A notification: Sent to maintenance cloud agent          │
│ └── Audit log: Created with full signal snapshot               │
│                                                                  │
│ Recommendation: Inspect bearing immediately                     │
└─────────────────────────────────────────────────────────────────┘
```

## 5.4 Smart Home Hub Agent

### Device Profile

```
┌─────────────────────────────────────────────────────────────────┐
│              SMART HOME HUB AGENT SPECIFICATION                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Device Class: Hub                                              │
│  Power Source: AC mains + battery backup                        │
│  Form Factor: Desktop or wall-mounted                           │
│  Connectivity: WiFi, Thread, BLE, Zigbee                        │
│                                                                  │
│  Sensors (aggregated from child devices):                       │
│  ├── Presence: Occupancy per room                               │
│  ├── Environmental: Temperature, humidity per zone             │
│  ├── Security: Door/window sensors, motion detectors           │
│  ├── Energy: Power consumption per circuit                     │
│  └── Environmental: Air quality, noise level                   │
│                                                                  │
│  Actuators (via child devices):                                 │
│  ├── Lighting: All controllable lights                         │
│  ├── Climate: HVAC, ceiling fans                               │
│  ├── Security: Door locks, alarm system                        │
│  ├── Window coverings: Blinds, shades                          │
│  └── Entertainment: Media systems                              │
│                                                                  │
│  APIs:                                                           │
│  ├── scene_activate(scene_name) → success/error                │
│  ├── device_control(device_id, command) → success/error        │
│  ├── get_home_status() → {occupancy, security, climate}        │
│  ├── create_automation(trigger, action) → success/error        │
│  └── get_energy_report(period) → consumption breakdown         │
│                                                                  │
│  Hard Constraints:                                               │
│  ├── Security system: Remote disarm requires user auth         │
│  ├── Door locks: Never auto-unlock on unknown presence         │
│  ├── Emergency: Always route alerts to user                    │
│  └── Privacy: No audio/video storage without consent           │
│                                                                  │
│  Coordination Capabilities:                                      │
│  ├── Multi-device scene orchestration                           │
│  ├── Conflict resolution (multiple user requests)              │
│  ├── Energy optimization across devices                        │
│  └── A2A delegation to child device agents                     │
│                                                                  │
│  Memory Configuration:                                           │
│  ├── SRAM: 128 MB (extended for multi-device state)            │
│  ├── Flash: 64 MB (automation rules, preferences)              │
│  └── LPDDR4: 512 MB (extended context)                         │
│                                                                  │
│  Power Budget:                                                   │
│  ├── Idle: 500 mW (monitoring all devices)                     │
│  ├── Active: 2W (processing requests)                          │
│  ├── Coordination: 3W (orchestrating complex actions)          │
│  └── Battery backup: 4 hours                                    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Multi-Device Coordination Example

```
USER: "I'm going to bed"

AGENT RESPONSE:
┌─────────────────────────────────────────────────────────────────┐
│ Activating "Good Night" scene:                                  │
│                                                                  │
│ Lighting:                                                        │
│ ├── Living room: OFF                                            │
│ ├── Kitchen: OFF                                                │
│ ├── Bedroom: 10% (fade over 2 minutes)                         │
│ └── Bathroom nightlight: ON                                     │
│                                                                  │
│ Climate:                                                         │
│ ├── Living zones: Set to 18°C (energy saving)                  │
│ └── Bedroom: Set to 19°C (comfort)                             │
│                                                                  │
│ Security:                                                        │
│ ├── All doors: LOCKED                                           │
│ ├── Security system: ARMED (stay mode)                         │
│ └── Motion sensors: Bedroom disabled for night                 │
│                                                                  │
│ Entertainment:                                                   │
│ └── All media: OFF                                              │
│                                                                  │
│ Window coverings:                                                │
│ └── All blinds: CLOSED                                          │
│                                                                  │
│ [Scene active. Sleep well!]                                     │
│                                                                  │
│ Tip: Say "Good morning" when you wake up.                      │
└─────────────────────────────────────────────────────────────────┘

---

CLOUD AGENT (via A2A):
"Request home status for emergency services"

AGENT RESPONSE:
┌─────────────────────────────────────────────────────────────────┐
│ A2A_DATA_RESPONSE                                                │
│                                                                  │
│ emergency_context:                                               │
│   occupancy:                                                     │
│     confirmed: true                                              │
│     location: "Bedroom"                                          │
│     persons: 2 (privacy level: count only)                      │
│                                                                  │
│   access_points:                                                 │
│     front_door: "unlocked for emergency services"              │
│     garage: "unlocked for emergency services"                  │
│     [User pre-consented for emergency override]                 │
│                                                                  │
│   hazards:                                                       │
│     smoke_detected: false                                        │
│     co_detected: false                                           │
│     water_leak: false                                            │
│                                                                  │
│   environmental:                                                 │
│     indoor_temp: 19°C                                            │
│     air_quality: "good"                                          │
│                                                                  │
│   devices_with_issues: none                                      │
│                                                                  │
│ auth_context:                                                    │
│   requester: "emergency_services_authenticated"                 │
│   consent: "pre-authorized emergency access"                    │
│   timestamp: 2026-01-15T02:34:00Z                              │
└─────────────────────────────────────────────────────────────────┘
```

---

# Part VI: Implementation Roadmap

## 6.1 Development Phases

```
Phase 1: Architecture Validation (Month 1-3)
├── Simulate agent model on FPGA (KV260)
├── Validate intent classification accuracy
├── Test safety constraint enforcement
├── Measure power vs. simulation
└── Deliverable: Working FPGA prototype

Phase 2: Model Finalization (Month 4-6)
├── Fine-tune on device-specific datasets
├── Optimize quantization for target precision
├── Validate A2A protocol implementation
├── Complete safety certification documentation
└── Deliverable: Frozen model weights

Phase 3: Silicon Implementation (Month 7-12)
├── GDSII layout generation
├── MPW tapeout (20-40 units)
├── Silicon validation
├── Firmware development
└── Deliverable: Prototype chips

Phase 4: Productization (Month 13-18)
├── Full mask set for production
├── Certification testing (FCC, CE, etc.)
├── Volume manufacturing ramp
├── SDK and documentation
└── Deliverable: Production units
```

## 6.2 Key Metrics

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| Intent classification accuracy | >95% | Test dataset |
| Safety rejection precision | 100% | Formal verification |
| A2A protocol compliance | 100% | Conformance testing |
| Power (active) | <2.5W | Silicon measurement |
| Power (monitoring) | <100mW | Silicon measurement |
| First token latency | <100ms | Silicon measurement |
| Throughput | >80 tok/s | Silicon measurement |

---

# Appendix A: Glossary

| Term | Definition |
|------|------------|
| **A2A** | Agent-to-Agent protocol for AI agent interoperability |
| **DNA** | Device-Native Agent - AI agent embedded in device hardware |
| **Mask-Locked** | Neural network weights permanently encoded in silicon metal layers |
| **iFairy** | Complex-valued weight representation using {±1, ±i} |
| **BitNet** | Ternary weight representation using {-1, 0, +1} |
| **KV Cache** | Key-Value cache for transformer attention mechanism |
| **RAU** | Rotation-Accumulate Unit for iFairy computation |
| **PE** | Processing Element in systolic array |

---

# Appendix B: Reference Specifications

## B.1 iFairy Weight Encoding

```
2-bit encoding for {±1, ±i}:
├── 00: +1
├── 01: -1
├── 10: +i
└── 11: -i

RAU Operation for w × (a + bi):
├── w = +1: out = (a, b)
├── w = -1: out = (-a, -b)
├── w = +i: out = (-b, a)
└── w = -i: out = (b, -a)
```

## B.2 Ternary Weight Encoding

```
1.58-bit encoding (2 bits with zero state):
├── 00: 0 (skip operation)
├── 01: +1
└── 10: -1
    11: reserved/unused

PE Operation for w × a:
├── w = +1: out = a
├── w = -1: out = -a
└── w = 0: skip (no operation)
```

## B.3 KV Cache Layout

```
Per-layer structure (for L=32, d=2560, W=512, INT4):

┌────────────────────────────────────────────────────────────┐
│ Layer i Key Cache                                          │
│ ┌────────────┬───────────────────────────────────────────┐│
│ │ Sink (4×d) │ Sliding Window (508×d)                   ││
│ │ 5 KB       │ 635 KB                                     ││
│ └────────────┴───────────────────────────────────────────┘│
│                                                            │
│ Layer i Value Cache                                        │
│ ┌────────────┬───────────────────────────────────────────┐│
│ │ Sink (4×d) │ Sliding Window (508×d)                   ││
│ │ 5 KB       │ 635 KB                                     ││
│ └────────────┴───────────────────────────────────────────┘│
│                                                            │
│ Total per layer: ~1.28 MB                                  │
│ Total for 32 layers: ~42 MB                                │
└────────────────────────────────────────────────────────────┘
```

---

*Document Version 1.0 | Prepared for Mask-Locked Inference Chip Development*
