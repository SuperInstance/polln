# Process Engineering Specification: 28nm Synapse-Inspired Chip Architecture

**Document Version:** 1.0  
**Process Node:** 28nm Poly/SiON (LP/HP)  
**Application:** Neuromorphic Compute - Synaptic Weight Encoding  
**Date:** January 2025  

---

## Executive Summary

This document defines the process design rules for implementing synapse-inspired chip structures at the 28nm technology node. The key innovation is the **"Synaptic Gap"** structure, where the biological synaptic cleft (20-30nm) maps directly to the 28nm gate length, enabling mask-locked ternary weight encoding through contact/via pattern configurations.

---

## 1. 28nm Design Rules for "Synaptic Gap" Structures

### 1.1 Critical Dimension Matching: Biological → Silicon

| Biological Parameter | Dimension | Silicon Equivalent | 28nm Node Rule |
|---------------------|-----------|-------------------|----------------|
| Synaptic Cleft Width | 20-30 nm | Minimum Gate Length | L_gate = 28nm |
| Vesicle Release Site | ~50 nm | Contact Landing Pad | 50nm × 50nm |
| Postsynaptic Density | ~200 nm | Active Region | 200nm × 200nm |
| Dendritic Spacing | 0.5-2 μm | Metal Pitch | 1x-4x pitch |

### 1.2 Synaptic Gap Design Rules Table

| Rule ID | Description | Min Value | Max Value | Recommended | DRC Check |
|---------|-------------|-----------|-----------|-------------|-----------|
| **SG-001** | Synaptic Gap Width (Active-to-Active) | 24 nm | 32 nm | 28 nm | ▢ |
| **SG-002** | Pre-Synaptic Active Area | 0.04 μm² | - | 0.06 μm² | ▢ |
| **SG-003** | Post-Synaptic Active Area | 0.04 μm² | - | 0.08 μm² | ▢ |
| **SG-004** | Gap Fill Dielectric Thickness | 25 nm | 35 nm | 30 nm | ▢ |
| **SG-005** | Gate Oxide Thickness (HP) | 1.2 nm | - | 1.2 nm | ▢ |
| **SG-006** | Gate Oxide Thickness (LP) | 2.8 nm | - | 2.8 nm | ▢ |
| **SG-007** | STI Depth | 120 nm | 150 nm | 140 nm | ▢ |
| **SG-008** | N-Well to P-Well Spacing | 400 nm | - | 500 nm | ▢ |
| **SG-009** | Poly-Silicon Width | 28 nm | - | 30 nm | ▢ |
| **SG-010** | Poly-Silicon Spacing | 28 nm | - | 30 nm | ▢ |

### 1.3 Synaptic Gap Cross-Section Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    M6 - Global Power/Signal                  │
├─────────────────────────────────────────────────────────────┤
│                    M5 - Weight Bus (High)                    │
├─────────────────────────────────────────────────────────────┤
│                    M4 - Inter-Synapse Routing                │
├─────────────────────────────────────────────────────────────┤
│                    M3 - Weight Value [±1, 0]                 │
├─────────────────────────────────────────────────────────────┤
│                    M2 - Column Select Lines                  │
├─────────────────────────────────────────────────────────────┤
│                    M1 - Row Select Lines                     │
├──────────┬─────────────────┬────────────┬───────────────────┤
│  PRE     │    SYNAPTIC     │   POST     │   Isolation       │
│  ACTIVE  │     GAP         │   ACTIVE   │   Channel         │
│  Region  │    28nm         │   Region   │   (SiO2)          │
│  [A]     │                 │   [B]      │                   │
├──────────┴─────────────────┴────────────┴───────────────────┤
│                    Silicon Substrate                         │
└─────────────────────────────────────────────────────────────┘
```

### 1.4 Electrical Isolation Requirements

| Parameter | Specification | Notes |
|-----------|---------------|-------|
| Leakage Current (Gap) | < 1 pA @ 1.0V | STI + Trench isolation |
| Breakdown Voltage | > 5.0V | Design margin for ESD |
| Parasitic Capacitance | < 0.5 fF/μm² | Minimize crosstalk |
| Junction Isolation | Deep N-Well | Triple-well option |

---

## 2. Metal Stack Configuration for Mask-Locked Weights (M1-M6)

### 2.1 28nm Metal Stack Architecture

| Layer | Material | Thickness | Min Width | Min Spacing | Min Pitch | Function |
|-------|----------|-----------|-----------|-------------|-----------|----------|
| **M1** | Cu | 80 nm | 45 nm | 45 nm | 90 nm | Row Select / Local Interconnect |
| **M2** | Cu | 80 nm | 45 nm | 45 nm | 90 nm | Column Select / Weight Bit 0 |
| **M3** | Cu | 120 nm | 70 nm | 70 nm | 140 nm | Weight Value Encoding |
| **M4** | Cu | 140 nm | 80 nm | 80 nm | 160 nm | Inter-Synapse Routing |
| **M5** | Cu | 280 nm | 140 nm | 140 nm | 280 nm | Weight Bus / Global Signal |
| **M6** | Cu | 400 nm | 200 nm | 200 nm | 400 nm | Power Distribution |
| **M7** | Cu | 800 nm | 400 nm | 400 nm | 800 nm | Pad / Redistribuion |

### 2.2 Via Stack Configuration

| Via | Connects | Size | Thickness | Resistance | Function |
|-----|----------|------|-----------|------------|----------|
| **V1** | M1-M2 | 45 nm × 45 nm | 40 nm | 15 Ω | Contact via |
| **V2** | M2-M3 | 70 nm × 70 nm | 40 nm | 12 Ω | Weight encode via |
| **V3** | M3-M4 | 80 nm × 80 nm | 50 nm | 10 Ω | Routing via |
| **V4** | M4-M5 | 140 nm × 140 nm | 50 nm | 8 Ω | Bus via |
| **V5** | M5-M6 | 200 nm × 200 nm | 60 nm | 6 Ω | Power via |
| **V6** | M6-M7 | 400 nm × 400 nm | 80 nm | 4 Ω | Pad via |

### 2.3 Metal Layer Assignment for Ternary Weight Encoding

```
┌────────────────────────────────────────────────────────────────────────┐
│                        WEIGHT ENCODING ARCHITECTURE                      │
├────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│    M6 ──── [VDD_GLOBAL] ──── [VSS_GLOBAL] ──── [IO_PADS]               │
│              │                │               │                         │
│    M5 ──── [WEIGHT_BUS] ──── [BIAS_Lines] ──── [REF_VOLTAGE]           │
│              │                │               │                         │
│    M4 ──── [SYNAPSE_SELECT] ──── [CROSSBAR] ──── [OUTPUT_ROUTE]        │
│              │                │               │                         │
│    M3 ──── [WEIGHT_SIGN] ──── [WEIGHT_MAG] ──── [WEIGHT_ZERO]          │
│              │      │             │              │                      │
│    M2 ──── [COL_0] ─── [COL_1] ─── [COL_2] ─── [COL_3]                 │
│              │        │         │          │                            │
│    M1 ──── [ROW_0] ─── [ROW_1] ─── [ROW_2] ─── [ROW_3]                 │
│              │        │         │          │                            │
│    ─────────────────────────────────────────────────────────           │
│    ACTIVE ── [PRE_SYNAPTIC] ─── [GAP] ─── [POST_SYNAPTIC]              │
│                                                                          │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.4 Weight Value Metal Pattern Definitions

| Weight | M3 Pattern | M2 Connection | V2 Pattern | Description |
|--------|------------|---------------|------------|-------------|
| **+1** | Solid Fill | Both active | Dual Via | Positive full weight |
| **-1** | Solid Fill | Inverted | Dual Via | Negative full weight |
| **0** | No metal | N/A | No Via | Zero weight (mask gap) |
| **+0.5** | Half-fill | Single active | Single Via | Fractional positive |
| **-0.5** | Half-fill | Inverted single | Single Via | Fractional negative |

---

## 3. Contact/Via Patterns for Ternary Weight Encoding

### 3.1 Ternary Weight Encoding Scheme

```
TERNARY WEIGHT = { -1, 0, +1 }

┌─────────────────────────────────────────────────────────────────────┐
│                    CONTACT PATTERN ENCODING                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  WEIGHT = +1                    WEIGHT = 0                    WEIGHT = -1
│  ┌───────────┐                  ┌───────────┐                  ┌───────────┐
│  │ ●       ● │                  │           │                  │ ●       ● │
│  │    M3     │                  │    M3     │                  │    M3     │
│  │ ●       ● │                  │  [GAP]    │                  │ ●       ● │
│  └─────┬─────┘                  └───────────┘                  └─────┬─────┘
│        │                                                             │
│  ┌─────┴─────┐                  ┌───────────┐                  ┌─────┴─────┐
│  │    M2     │                  │    M2     │                  │    M2     │
│  │  ACTIVE   │                  │  ACTIVE   │                  │  INVERTED │
│  └───────────┘                  └───────────┘                  └───────────┘
│  V2: 4 vias                    V2: 0 vias                     V2: 4 vias
│  Sign: +1                      Sign: 0                        Sign: -1
│  Route: VDD                    Route: FLOAT                   Route: VSS
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Contact Pattern Design Rules

| Rule ID | Parameter | +1 Weight | 0 Weight | -1 Weight |
|---------|-----------|-----------|----------|-----------|
| **CT-001** | V2 Via Count | 4 | 0 | 4 |
| **CT-002** | M3 Coverage | 100% | 0% | 100% |
| **CT-003** | M2 Routing | VDD connected | Floating | VSS connected |
| **CT-004** | Contact Size | 70nm × 70nm | N/A | 70nm × 70nm |
| **CT-005** | Contact Spacing | 70nm (min) | N/A | 70nm (min) |
| **CT-006** | Enclosure | 35nm (min) | N/A | 35nm (min) |
| **CT-007** | Resistance | 10 Ω/via | ∞ | 10 Ω/via |

### 3.3 Via Pattern Matrix

| Pattern ID | Via Arrangement | Weight Value | Effective R | Notes |
|------------|-----------------|--------------|-------------|-------|
| **VP-001** | 2×2 Grid (4 vias) | +1 or -1 | 2.5 Ω | Maximum conductance |
| **VP-002** | 1×2 Grid (2 vias) | ±0.5 | 5 Ω | Half conductance |
| **VP-003** | Single Via | ±0.25 | 10 Ω | Quarter conductance |
| **VP-004** | No Via (open) | 0 | ∞ | Zero weight |
| **VP-005** | Anti-fuse blown | 0 | ∞ | Programmable zero |
| **VP-006** | Fuse intact | +1 | 2.5 Ω | Programmable weight |

### 3.4 Weight Matrix Layout Example (4×4 Synapse Array)

```
                    C0      C1      C2      C3
                 ┌───────┬───────┬───────┬───────┐
              R0 │  +1   │   0   │  -1   │  +1   │
                 │ ●●●●  │       │ ●●●●  │ ●●●●  │
                 ├───────┼───────┼───────┼───────┤
              R1 │   0   │  +1   │   0   │  -1   │
                 │       │ ●●●●  │       │ ●●●●  │
                 ├───────┼───────┼───────┼───────┤
              R2 │  -1   │   0   │  +1   │   0   │
                 │ ●●●●  │       │ ●●●●  │       │
                 ├───────┼───────┼───────┼───────┤
              R3 │  +1   │  -1   │   0   │  +1   │
                 │ ●●●●  │ ●●●●  │       │ ●●●●  │
                 └───────┴───────┴───────┴───────┘

    VIA PATTERN LEGEND:
    ●●●● = 4 vias (full weight, ±1)
    [blank] = 0 vias (zero weight)
```

### 3.5 Mask-Locked Security Features

| Feature | Implementation | Security Level |
|---------|---------------|----------------|
| Weight Invisibility | M3 pattern hidden under M4-M6 | High |
| Reverse Engineering Barrier | No visible metal cuts | Very High |
| Process Variability Tolerance | Via redundancy (4 vias) | Medium |
| Tamper Evidence | Break-before-make fuses | High |
| Clone Prevention | Unique via pattern per chip | Very High |

---

## 4. Thermal Isolation Channel Design Rules

### 4.1 Thermal Isolation Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     THERMAL ISOLATION CHANNEL                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│    ┌───────────────┐    THERMAL    ┌───────────────┐                    │
│    │   COMPUTE     │    CHANNEL    │   COMPUTE     │                    │
│    │    UNIT A     │               │    UNIT B     │                    │
│    │               │   ┌─────┐     │               │                    │
│    │   ┌─────┐     │   │SiO₂ │     │   ┌─────┐     │                    │
│    │   │MAC  │     │   │     │     │   │MAC  │     │                    │
│    │   │ARRAY│     │   │AIR  │     │   │ARRAY│     │                    │
│    │   └─────┘     │   │GAP  │     │   └─────┘     │                    │
│    │               │   │     │     │               │                    │
│    │   HOT SPOT    │   └─────┘     │   HOT SPOT    │                    │
│    │   Ta = 85°C   │   Rth=5°C/W   │   Tb = 75°C   │                    │
│    └───────────────┘               └───────────────┘                    │
│                                                                          │
│    Thermal Channel Width: 2-5 μm                                         │
│    Thermal Resistance: >5°C/W per channel                               │
│    Temperature Delta: 10-15°C between adjacent units                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Thermal Isolation Channel Design Rules Table

| Rule ID | Parameter | Min | Typical | Max | Units | Notes |
|---------|-----------|-----|---------|-----|-------|-------|
| **TI-001** | Channel Width | 2.0 | 3.0 | 5.0 | μm | Wider = better isolation |
| **TI-002** | Channel Depth | 150 | 200 | 250 | nm | Etch into STI |
| **TI-003** | SiO₂ Fill Thickness | 25 | 30 | 35 | nm | Liner oxide |
| **TI-004** | Air Gap Width | 1.0 | 1.5 | 2.0 | μm | Effective isolation |
| **TI-005** | Channel Length | 50 | 100 | 200 | μm | Match compute unit |
| **TI-006** | Thermal Resistance | 5 | 10 | 20 | °C/W | Design target |
| **TI-007** | Sidewall Angle | 85 | 88 | 90 | deg | Anisotropic etch |
| **TI-008** | Metal Bridge Width | 0 | 50 | 100 | nm | Optional thermal path |
| **TI-009** | Channel Spacing (regular) | 10 | 20 | 50 | μm | Between channels |
| **TI-010** | Crosstalk Temperature | - | <5 | 10 | °C | Max allowable |

### 4.3 Thermal Isolation Material Stack

| Layer | Material | Thermal Conductivity (W/m·K) | Thickness | Function |
|-------|----------|------------------------------|-----------|----------|
| **Liner** | SiO₂ | 1.4 | 30 nm | Passivation |
| **Core** | Air/Void | 0.026 | 1.5 μm | Primary isolation |
| **Seal** | SiNₓ | 30 | 50 nm | Mechanical support |
| **Cap** | SiO₂ | 1.4 | 100 nm | CMP stop |

### 4.4 Thermal Channel Pattern Options

```
Option A: Air Gap Channel (Best Isolation)
┌─────────────┐     ┌─────────────┐
│  COMPUTE A  │▓▓▓▓▓│  COMPUTE B  │
│             │AIR  │             │
└─────────────┘     └─────────────┘
Rth = 15-20 °C/W

Option B: Oxide-Filled Channel (Moderate Isolation)
┌─────────────┐     ┌─────────────┐
│  COMPUTE A  │▓▓▓▓▓│  COMPUTE B  │
│             │SiO₂ │             │
└─────────────┘     └─────────────┘
Rth = 5-8 °C/W

Option C: Metal Bridge Channel (Controlled Coupling)
┌─────────────┐     ┌─────────────┐
│  COMPUTE A  │▓▓M▓▓│  COMPUTE B  │
│             │Cu   │             │
└─────────────┘     └─────────────┘
Rth = 1-3 °C/W (tunable)

▓ = Isolation material, M = Metal bridge (optional)
```

### 4.5 Thermal Simulation Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Silicon Thermal Conductivity | 150 W/m·K | Process spec |
| SiO₂ Thermal Conductivity | 1.4 W/m·K | Process spec |
| Cu Thermal Conductivity | 400 W/m·K | Process spec |
| Air Thermal Conductivity | 0.026 W/m·K | Reference |
| Chip Max Temperature | 125°C | Design limit |
| Junction Temperature (operating) | 85°C | Target |
| Ambient Temperature | 25-55°C | Application |

---

## 5. SPICE Parameters for Cleft-Interconnect

### 5.1 Device Models (28nm Poly/SiON)

```spice
* 28nm Synapse-Inspired Chip SPICE Models
* Process: 28nm Poly/SiON LP/HP
* Foundry: Generic (Synopsys 28nm PTM compatible)

*===========================================
* MOSFET MODELS
*===========================================

.MODEL nmos_28lp nmos (
+ lmin = 28e-9          lmax = 100e-9
+ wmin = 80e-9          
+ tox = 2.8e-9          * Gate oxide (LP)
+ toxqm = 2.8e-9        * Electrical oxide
+ nch = 4.5e17          * Channel doping
+ vth0 = 0.35           * Threshold voltage
+ u0 = 350              * Mobility (cm²/V·s)
+ rdsw = 150            * Rds*w
+ pclm = 0.5            * Channel length modulation
+ drout = 50            * DIBL coefficient
+ kt1 = -0.12           * Temperature coefficient
+ kt2 = 0.022           * Temperature coefficient 2
+ ua = 1e-9             * Mobility reduction
+ ub = 1e-18            * Mobility reduction 2
+ uc = 0                * Mobility reduction 3
)

.MODEL pmos_28lp pmos (
+ lmin = 28e-9          lmax = 100e-9
+ wmin = 80e-9          
+ tox = 2.8e-9          * Gate oxide (LP)
+ toxqm = 2.8e-9        * Electrical oxide
+ nch = 3.5e17          * Channel doping
+ vth0 = -0.38          * Threshold voltage
+ u0 = 120              * Mobility (cm²/V·s)
+ rdsw = 200            * Rds*w
+ pclm = 0.6            * Channel length modulation
+ drout = 40            * DIBL coefficient
+ kt1 = -0.12           * Temperature coefficient
+ kt2 = 0.022           * Temperature coefficient 2
+ ua = 2e-9             * Mobility reduction
+ ub = 0.5e-18          * Mobility reduction 2
+ uc = -1e-10           * Mobility reduction 3
)
```

### 5.2 Synaptic Gap Interconnect Model

```spice
*===========================================
* SYNAPTIC GAP INTERCONNECT MODEL
*===========================================

* Subcircuit for Synaptic Gap Structure
* Represents the parasitic coupling between
* pre-synaptic and post-synaptic regions

.SUBCKT synaptic_gap pre_post post_pre
+ PARAMS: gap_w=28e-9 gap_l=100e-9

* Parasitic capacitance across gap
C_gap pre_post post_pre {0.5e-15 * gap_l / 100e-9}

* Leakage resistance (tunneling + surface)
R_leak pre_post post_pre 1e12

* Junction isolation (reverse biased diode behavior)
D_iso pre_post post_pre gap_diode

.ENDS synaptic_gap

* Gap isolation diode model
.MODEL gap_diode d (
+ is = 1e-18            * Reverse saturation
+ n = 1.5               * Ideality factor
+ bv = 5.0              * Breakdown voltage
+ ibv = 1e-6            * Breakdown current
+ cj0 = 0.5e-15         * Zero-bias capacitance
+ vj = 0.7              * Built-in potential
+ m = 0.5               * Grading coefficient
+ tt = 1e-12            * Transit time
)
```

### 5.3 Ternary Weight Interconnect Model

```spice
*===========================================
* TERNARY WEIGHT ENCODING MODEL
*===========================================

* Weight +1: Full conductance
.SUBCKT weight_pos vdd vss weight_out
+ PARAMS: r_via=2.5
R_pos vdd weight_out {r_via/4}
.ENDS weight_pos

* Weight -1: Full negative conductance
.SUBCKT weight_neg vdd vss weight_out
+ PARAMS: r_via=2.5
R_neg vss weight_out {r_via/4}
.ENDS weight_neg

* Weight 0: Zero conductance (open)
.SUBCKT weight_zero vdd vss weight_out
R_zero vdd weight_out 1e15
.ENDS weight_zero

* Complete weight cell subcircuit
.SUBCKT weight_cell vdd vss row_sel col_sel weight_out
+ PARAMS: w_val=1 r_via=2.5

* Weight value select mux
S_weight_p vdd weight_out row_sel col_sel weight_sw_pos
S_weight_n vss weight_out row_sel col_sel weight_sw_neg

.MODEL weight_sw_pos sw ron=10 roff=1e12 vt=0.5
.MODEL weight_sw_neg sw ron=10 roff=1e12 vt=-0.5

* Include via resistance based on weight
R_via vdd weight_out {r_via/abs(w_val)/4} 

.ENDS weight_cell
```

### 5.4 Thermal Isolation Channel SPICE Model

```spice
*===========================================
* THERMAL ISOLATION CHANNEL MODEL
*===========================================

* Thermal-electrical analogy:
* Temperature T (K) ↔ Voltage V (V)
* Heat Flow P (W) ↔ Current I (A)
* Thermal Resistance Rth (K/W) ↔ Resistance R (Ω)
* Thermal Capacitance Cth (J/K) ↔ Capacitance C (F)

.SUBCKT thermal_channel temp_hot temp_cold
+ PARAMS: 
+ channel_w=3e-6        * Channel width (m)
+ channel_l=100e-6      * Channel length (m)
+ channel_d=200e-9      * Channel depth (m)
+ k_sio2=1.4            * SiO2 thermal conductivity (W/m·K)
+ k_air=0.026           * Air thermal conductivity (W/m·K)

* Effective thermal resistance
* Rth = L / (k * A) where A = W * D
R_th_sio2 temp_hot temp_mid {channel_l / (k_sio2 * channel_w * channel_d)}
R_th_air temp_mid temp_cold {channel_l / (k_air * channel_w * channel_d * 0.5)}

* Thermal capacitance (heat capacity of channel material)
* Cth = ρ * V * c_p where ρ = density, c_p = specific heat
C_th temp_hot 0 {2.2e6 * channel_w * channel_l * channel_d * 730}

.ENDS thermal_channel

* Complete thermal network for compute unit pair
.SUBCKT compute_pair_thermal temp_a temp_b temp_amb
+ PARAMS: r_th_channel=10

X_th_channel temp_a temp_b thermal_channel 
+ PARAMS: channel_w=3e-6 channel_l=100e-6

* Heat sink path
R_th_sink_a temp_a temp_amb 5
R_th_sink_b temp_b temp_amb 5

.ENDS compute_pair_thermal
```

### 5.5 Complete Synapse Array SPICE Subcircuit

```spice
*===========================================
* SYNAPSE ARRAY COMPLETE MODEL
*===========================================

.SUBCKT synapse_array_4x4 
+ vdd vss 
+ row_sel<3:0> col_sel<3:0>
+ weight_out<3:0>
+ PARAMS: r_via=2.5

* Instance 4x4 weight cells
* Row 0
Xw00 vdd vss row_sel<0> col_sel<0> weight_out<0> weight_cell PARAMS: w_val=+1 r_via=2.5
Xw01 vdd vss row_sel<0> col_sel<1> weight_out<0> weight_cell PARAMS: w_val=0 r_via=2.5
Xw02 vdd vss row_sel<0> col_sel<2> weight_out<0> weight_cell PARAMS: w_val=-1 r_via=2.5
Xw03 vdd vss row_sel<0> col_sel<3> weight_out<0> weight_cell PARAMS: w_val=+1 r_via=2.5

* Row 1
Xw10 vdd vss row_sel<1> col_sel<0> weight_out<1> weight_cell PARAMS: w_val=0 r_via=2.5
Xw11 vdd vss row_sel<1> col_sel<1> weight_out<1> weight_cell PARAMS: w_val=+1 r_via=2.5
Xw12 vdd vss row_sel<1> col_sel<2> weight_out<1> weight_cell PARAMS: w_val=0 r_via=2.5
Xw13 vdd vss row_sel<1> col_sel<3> weight_out<1> weight_cell PARAMS: w_val=-1 r_via=2.5

* Row 2
Xw20 vdd vss row_sel<2> col_sel<0> weight_out<2> weight_cell PARAMS: w_val=-1 r_via=2.5
Xw21 vdd vss row_sel<2> col_sel<1> weight_out<2> weight_cell PARAMS: w_val=0 r_via=2.5
Xw22 vdd vss row_sel<2> col_sel<2> weight_out<2> weight_cell PARAMS: w_val=+1 r_via=2.5
Xw23 vdd vss row_sel<2> col_sel<3> weight_out<2> weight_cell PARAMS: w_val=0 r_via=2.5

* Row 3
Xw30 vdd vss row_sel<3> col_sel<0> weight_out<3> weight_cell PARAMS: w_val=+1 r_via=2.5
Xw31 vdd vss row_sel<3> col_sel<1> weight_out<3> weight_cell PARAMS: w_val=-1 r_via=2.5
Xw32 vdd vss row_sel<3> col_sel<2> weight_out<3> weight_cell PARAMS: w_val=0 r_via=2.5
Xw33 vdd vss row_sel<3> col_sel<3> weight_out<3> weight_cell PARAMS: w_val=+1 r_via=2.5

.ENDS synapse_array_4x4
```

### 5.6 Key SPICE Simulation Parameters

| Parameter | Symbol | Value | Units | Notes |
|-----------|--------|-------|-------|-------|
| Gate Length | L_g | 28 | nm | Minimum feature |
| Gate Oxide | t_ox | 2.8 | nm | LP process |
| Threshold Voltage (N) | V_thn | 0.35 | V | Typical |
| Threshold Voltage (P) | V_thp | -0.38 | V | Typical |
| Supply Voltage | V_DD | 1.0 | V | Core |
| I/O Voltage | V_IO | 1.8/2.5 | V | I/O ring |
| NMOS Mobility | μ_n | 350 | cm²/V·s | Typical |
| PMOS Mobility | μ_p | 120 | cm²/V·s | Typical |
| Via Resistance | R_via | 10 | Ω | V2 typical |
| Metal Sheet Resistance | R_sh | 0.15 | Ω/sq | M3 |
| Capacitance per μm | C_metal | 0.2 | fF/μm | M3-M4 |

---

## 6. Process Flow for Mask Generation

### 6.1 Mask Layer Summary

| Mask # | Layer Name | Mask Type | Tone | CD (nm) | Overlay (nm) | Function |
|--------|------------|-----------|------|---------|--------------|----------|
| **M1** | N-Well | Binary | Clear | 400 | ±20 | N-well definition |
| **M2** | Active | Binary | Dark | 50 | ±5 | Active area |
| **M3** | STI | Binary | Clear | 100 | ±10 | Isolation trench |
| **M4** | Poly | Binary | Dark | 28 | ±3 | Gate electrode |
| **M5** | N+ Implant | Binary | Clear | 50 | ±10 | S/D implant |
| **M6** | P+ Implant | Binary | Clear | 50 | ±10 | S/D implant |
| **M7** | Contact | Binary | Dark | 45 | ±4 | CA to active/poly |
| **M8** | Metal 1 | Binary | Dark | 45 | ±4 | Local interconnect |
| **M9** | Via 1 | Binary | Dark | 45 | ±4 | V1 via |
| **M10** | Metal 2 | Binary | Dark | 45 | ±4 | Row select |
| **M11** | Via 2 | Binary | Dark | 70 | ±5 | **Weight encode** |
| **M12** | Metal 3 | Binary | Dark | 70 | ±5 | **Weight value** |
| **M13** | Via 3 | Binary | Dark | 80 | ±6 | Routing via |
| **M14** | Metal 4 | Binary | Dark | 80 | ±6 | Inter-synapse |
| **M15** | Via 4 | Binary | Dark | 140 | ±10 | Bus via |
| **M16** | Metal 5 | Binary | Dark | 140 | ±10 | Weight bus |
| **M17** | Via 5 | Binary | Dark | 200 | ±12 | Power via |
| **M18** | Metal 6 | Binary | Dark | 200 | ±12 | Global power |
| **M19** | Pad | Binary | Dark | 5000 | ±50 | Bond pad |

### 6.2 Critical Process Flow Steps

```
╔════════════════════════════════════════════════════════════════════════╗
║                    28NM SYNAPSE CHIP PROCESS FLOW                      ║
╠════════════════════════════════════════════════════════════════════════╣
║                                                                         ║
║  PHASE 1: FRONT-END (FEOL)                                              ║
║  ─────────────────────────────────────────────────────────────────     ║
║  [01] Substrate Prep: 300mm p-type <100>, 10-20 Ω·cm                   ║
║  [02] N-Well Implant & Drive: 400 keV P, 1800°C anneal                 ║
║  [03] STI Formation: 140nm deep, 150nm wide trenches                   ║
║  [04] Gate Oxide: 2.8nm SiON (LP) @ 1050°C, N₂O ambient               ║
║  [05] Poly Gate: 100nm poly-Si, 28nm CD, Phos doped                    ║
║  [06] Offset Spacer: 15nm SiN                                          ║
║  [07] LDD Implant: N-LDD 30keV As, P-LDD 30keV BF₂                     ║
║  [08] Main Spacer: 40nm SiN                                            ║
║  [09] S/D Implant: N+ 50keV As, P+ 50keV BF₂                           ║
║  [10] RTA Anneal: 1050°C, 10s spike                                    ║
║  [11] Salicide: CoSi₂ on active & poly                                 ║
║                                                                         ║
║  PHASE 2: BACK-END (BEOL)                                               ║
║  ─────────────────────────────────────────────────────────────────     ║
║  [12] PMD Deposition: 300nm SiO₂ + PSG                                 ║
║  [13] Contact Etch: 45nm CD, W fill, CMP                               ║
║  [14] Metal 1 Damascene: 80nm Cu, 45nm CD                              ║
║  [15] Via 1 Etch: 45nm CD, W fill                                      ║
║  [16] Metal 2 Damascene: 80nm Cu, 45nm CD                              ║
║  [17] ★ Via 2 WEIGHT ENCODE: 70nm CD, PATTERN LOCK ★                   ║
║  [18] ★ Metal 3 WEIGHT VALUE: 70nm Cu, MASK-LOCKED ★                   ║
║  [19] Via 3 Etch: 80nm CD, Cu fill                                     ║
║  [20] Metal 4 Damascene: 140nm Cu, 80nm CD                             ║
║  [21] Thermal Channel Etch: 3μm wide, 200nm deep                       ║
║  [22] Air Gap Formation: Selective etch, seal cap                      ║
║  [23] Via 4-5 & Metal 5-6: Standard Cu damascene                       ║
║  [24] Passivation: 1μm SiN                                             ║
║  [25] Pad Etch: Al pad, 5μm × 5μm                                      ║
║                                                                         ║
║  PHASE 3: POST-PROCESS                                                  ║
║  ─────────────────────────────────────────────────────────────────     ║
║  [26] WAT: Electrical test, parametric                                  ║
║  [27] Sort: Functional test, binning                                    ║
║  [28] Assembly: WLCSP or QFN package                                    ║
║  [29] Final Test: Burn-in, speed bin                                    ║
║                                                                         ║
╚════════════════════════════════════════════════════════════════════════╝

★ = Critical mask-locked weight encoding steps
```

### 6.3 Mask Generation Specifications

| Specification | Value | Notes |
|---------------|-------|-------|
| Mask Type | Binary Chrome on Quartz | Standard |
| Write Tool | E-beam 50 keV | High precision |
| Write Grid | 1 nm | Critical layers |
| CD Control | ±3 nm (1σ) | M3/V2 weight layers |
| CD Uniformity | ±2 nm across field | Weight uniformity |
| Overlay | ±5 nm (1σ) | Layer-to-layer |
| Defect Density | <0.01/cm² @ 50nm | Zero critical defects |
| Mask Size | 6" × 6" × 0.25" | Standard reticle |
| Data Format | GDSII / OASIS | Industry standard |

### 6.4 OPC/RET Requirements

| Layer | RET Method | Model Complexity | Critical Features |
|-------|------------|------------------|-------------------|
| Active | SRAF + OPC | High | CD uniformity |
| Poly | SRAF + OPC + PSM | Very High | Gate length control |
| Contact | SRAF + OPC | High | Via coverage |
| M1-M2 | SRAF + OPC | Medium | Standard |
| **V2 (Weight)** | **Custom OPC** | **Very High** | **Via count control** |
| **M3 (Weight)** | **Custom OPC** | **Very High** | **Pattern fidelity** |
| M4-M6 | SRAF + OPC | Medium | Standard |

---

## 7. Design Rule Summary Tables

### 7.1 Complete DRC Rule Summary

| Category | Rule Count | Critical Rules | Yield Impact |
|----------|------------|----------------|--------------|
| Active | 15 | 5 | High |
| Poly | 18 | 8 | Very High |
| STI | 12 | 4 | Medium |
| Well | 8 | 3 | Low |
| Implant | 10 | 2 | Low |
| Contact | 20 | 6 | High |
| Metal 1-2 | 25 | 5 | Medium |
| **Via 2 (Weight)** | **15** | **10** | **Critical** |
| **Metal 3 (Weight)** | **18** | **12** | **Critical** |
| Metal 4-6 | 30 | 4 | Low |
| Thermal Channel | 10 | 5 | Medium |
| **TOTAL** | **181** | **64** | - |

### 7.2 Critical Design Rules Quick Reference

| Rule | Description | Value | Violation Consequence |
|------|-------------|-------|----------------------|
| **SG-001** | Synaptic Gap Width | 28±4 nm | Electrical coupling |
| **CT-004** | V2 Via Size | 70×70 nm | Weight error |
| **CT-005** | V2 Via Spacing | 70 nm | Lithography fail |
| **TI-006** | Thermal Rth | >5 °C/W | Thermal crosstalk |
| **M3-001** | M3 Width | 70 nm min | Weight conductance |

### 7.3 Process Corner Parameters

| Corner | Vth (mV) | L (nm) | t_ox (nm) | Weight R (Ω) | Notes |
|--------|----------|--------|-----------|--------------|-------|
| **TT** | 350 | 28.0 | 2.80 | 2.5 | Typical |
| **FF** | 300 | 26.5 | 2.65 | 2.0 | Fast-Fast |
| **SS** | 400 | 29.5 | 2.95 | 3.2 | Slow-Slow |
| **FS** | 330/420 | 27.5 | 2.75 | 2.3 | Fast N/Slow P |
| **SF** | 420/330 | 28.5 | 2.85 | 2.8 | Slow N/Fast P |

---

## 8. Appendix: Reference Data

### A.1 Biological Synapse Parameters (Reference)

| Parameter | Biological Value | Silicon Scaling |
|-----------|------------------|-----------------|
| Synaptic Cleft Width | 20-30 nm | → Gate Length 28nm |
| Vesicle Diameter | 40-50 nm | → Contact Size 45nm |
| Active Zone Size | 200-500 nm | → Active Area 200nm |
| Synapse Density | 10⁹-10¹¹ /cm³ | → 10⁸ /cm² (2D) |
| Transmission Time | 0.5-2 ms | → ~1 ns (electrical) |
| Energy/Event | 10⁴-10⁵ ATP | → ~1 fJ/operation |

### A.2 Material Properties Reference

| Material | ρ (Ω·cm) | k (W/m·K) | ε_r | Application |
|----------|----------|-----------|-----|-------------|
| Si | 10⁴ | 150 | 11.7 | Substrate |
| SiO₂ | >10¹⁴ | 1.4 | 3.9 | Gate oxide, isolation |
| SiNₓ | >10¹⁴ | 30 | 7.5 | Spacer, passivation |
| Cu | 1.7e-6 | 400 | - | Interconnect |
| W | 5.6e-6 | 174 | - | Contact, via |
| CoSi₂ | 10e-6 | - | - | Salicide |

### A.3 Defect Density Budget (28nm Node)

| Defect Type | Target | Specification |
|-------------|--------|---------------|
| Critical Defects | <0.1/cm² | D0 |
| Via Opens | <0.01% | Yield impact |
| Metal Shorts | <0.01% | Yield impact |
| Gate Shorts | <0.001% | Kill defect |
| Gate Opens | <0.001% | Kill defect |

---

## 9. Summary

This process engineering specification defines the complete design rules for implementing synapse-inspired chip structures at the 28nm technology node. Key innovations include:

1. **Synaptic Gap Structure**: 28nm minimum spacing matching biological synaptic cleft dimensions
2. **Mask-Locked Weights**: Ternary encoding {-1, 0, +1} via V2 via patterns in M3 metal
3. **Thermal Isolation**: Air-gap channels providing >5°C/W thermal resistance between compute units
4. **SPICE Models**: Complete device and interconnect models for simulation
5. **Process Flow**: 29-step flow with critical weight encoding at steps 17-18

The design enables secure, mask-programmable neuromorphic computing with direct biological analogy at the nanoscale.

---

**Document Control:**
- Created: January 2025
- Status: Final Draft
- Classification: Technical Specification
- Review Cycle: Annual

**End of Document**
