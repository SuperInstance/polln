# Security Model

TernaryAir provides hardware-enforced security through physical isolation and immutable weights.

## Core Security Properties

| Property | Mechanism | Bypass Possibility |
|----------|-----------|-------------------|
| No data exfiltration | No network hardware | **Impossible** |
| No persistent memory | Volatile SRAM only | **Impossible** |
| Immutable model | Mask-locked ROM | **Impossible** |
| Agent isolation | Hardware boundary | **Impossible** |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHYSICAL SECURITY ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   YOUR COMPUTER ──── USB ────▶ TERNARYAIR DEVICE                       │
│                                                                         │
│   TernaryAir Device Contains:                                          │
│   ✗ NO network interface (physically not present)                      │
│   ✗ NO file system access (no storage controller)                      │
│   ✗ NO persistent memory (volatile SRAM only)                          │
│   ✗ NO programmable cores (fixed-function only)                        │
│   ✗ NO firmware updates (ROM-based control)                            │
│                                                                         │
│   The device is a PURE FUNCTION: Input → Inference → Output            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Mask-Locked Weights

Weights are stored as physical via patterns in metal layers:

- **Cannot be read** - It's geometry, not data
- **Cannot be modified** - It's solid metal patterns
- **Cannot be extracted** - Requires destructive analysis

Extraction would require:
1. Physical decapsulation (destroys chip)
2. Electron microscopy imaging
3. Manual pattern tracing

Cost: $100,000+ | Time: Weeks | Result: One extracted model, destroyed chip

## Agent Isolation

TernaryAir creates a hardware boundary between AI agents and your system:

```
WITHOUT TernaryAir:
  AI Agent ──▶ [Full System Access: Files, Network, Commands]

WITH TernaryAir:
  AI Agent ──▶ [TernaryAir Hardware Boundary] ──▶ TEXT OUTPUT ONLY
                    │
                    ├── ✗ NO FILES
                    ├── ✗ NO NETWORK
                    └── ✗ NO MEMORY
```

## Compliance

### Healthcare (HIPAA)
- No PHI transmission over network
- No persistent storage of PHI
- Air-gapped processing

### Legal (Attorney-Client Privilege)
- No records or logs
- Cannot be subpoenaed
- Privileged communications protected

### Financial (Regulatory)
- Data never leaves controlled environment
- No audit trail to compromise
- Hardware-enforced isolation

## Verification

You can verify security by:

1. **Physical inspection**: No network hardware present
2. **Functional testing**: Operates in Faraday cage unchanged
3. **Traffic monitoring**: Only USB communication
4. **Power cycle test**: No retained state after power-off

## Summary

TernaryAir provides **security by physics, not by policy**. The hardware architecture makes certain attacks physically impossible rather than just difficult.
