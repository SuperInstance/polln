# Ternäre Inferenz-Chip: Technische Spezifikation
## Ternary Inference Chip: Technical Specification (German Edition)

**Autor**: SuperInstance.AI Forschungsteam  
**Datum**: März 2026  
**Version**: v2.0

---

## Zusammenfassung

Dieses Dokument spezifiziert die technische Implementierung eines ternären Inferenz-Chips für Kanten-Berechnung (Edge Computing). Der Chip nutzt dreiwertige Gewichte {-1, 0, +1} und masken-lockierte ROM-Speicher, um eine Effizienz von 46,6 tok/s/W zu erreichen.

**Technische Klassifikation**: ASIC für Edge-Inferenz  
**Fertigungsprozess**: TSMC 28nm HPM  
**Leistungsziel**: 5W @ 1GHz

---

## 1. Architektur-Übersicht

### 1.1 Blockdiagramm

```
┌─────────────────────────────────────────────────────────────┐
│                    SuperInstance Edge-500                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   PCIe      │    │   DMA       │    │   Host      │     │
│  │   Gen2 x4   │◄──►│   Engine    │◄──►│   Interface │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                                │
│         ▼                  ▼                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              System Controller (RISC-V)              │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│         ┌──────────────────┼──────────────────┐            │
│         ▼                  ▼                  ▼            │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Weight    │    │    PE       │    │   KV        │     │
│  │   ROM       │    │   Array     │    │   Cache     │     │
│  │   (Mask)    │    │  (32×32)    │    │  (SRAM)     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                  │            │
│         └──────────────────┼──────────────────┘            │
│                            ▼                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    LPDDR4 Controller                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                            │                                │
│                      LPDDR4-3200                            │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Technische Daten

| Parameter | Spezifikation | Bemerkung |
|-----------|---------------|-----------|
| Fertigung | TSMC 28nm HPM | Reifer Prozess |
| Chipfläche | 25 mm² | 5mm × 5mm Die |
| Transistoren | ~50M | Enthalten SRAM/ROM |
| Taktfrequenz | 1 GHz | Maximal |
| Versorgungsspannung | 0.9V Core / 1.8V I/O | Standard |
| Leistungsaufnahme | 5W typisch | Bei Volllast |
| Gehäuse | BGA-256 | 17mm × 17mm |

---

## 2. Verarbeitungselement (PE) Design

### 2.1 PE-Architektur

Jedes PE führt eine ternäre MAC-Operation durch:

```verilog
// PE Ternäres MAC-Modul
module pe_ternary (
    input  clk,
    input  rst_n,
    input  [15:0] activation_in,
    input  [1:0]  weight,        // 00=0, 01=+1, 10=-1
    input  [31:0] partial_sum_in,
    output [15:0] activation_out,
    output [31:0] partial_sum_out
);
    reg [31:0] product;
    reg [31:0] accumulator;
    
    // Ternäre Multiplikation (vereinfacht)
    always @(*) begin
        case (weight)
            2'b00: product = 32'b0;
            2'b01: product = {16'b0, activation_in};
            2'b10: product = -{16'b0, activation_in};
            default: product = 32'b0;
        endcase
    end
    
    // Akkumulation
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            accumulator <= 32'b0;
        else
            accumulator <= partial_sum_in + product;
    end
    
    // Pipeline-Register
    always @(posedge clk) begin
        activation_out <= activation_in;
        partial_sum_out <= accumulator;
    end
endmodule
```

### 2.2 PE-Array Konfiguration

```
32×32 Systolische Anordnung:

    A0  A1  A2  ... A31  (Aktivierungen)
    ↓   ↓   ↓       ↓
┌───┬───┬───┬───┬───┐
│PE │PE │PE │...│PE │ ← Zeile 0: W0,0 W0,1 ... W0,31
├───┼───┼───┼───┼───┤
│PE │PE │PE │...│PE │ ← Zeile 1: W1,0 W1,1 ... W1,31
├───┼───┼───┼───┼───┤
│...│...│...│...│...│
├───┼───┼───┼───┼───┤
│PE │PE │PE │...│PE │ ← Zeile 31
└───┴───┴───┴───┴───┘
    ↓   ↓   ↓       ↓
   S0  S1  S2  ... S31  (Summen)
```

**Datenfluss**:
- Aktivierungen: Horizontal (West → Ost)
- Partielle Summen: Vertikal (Nord → Süd)
- Gewichte: Stationär (in ROM gespeichert)

### 2.3 Ressourcen pro PE

| Komponente | Fläche | Leistung | Latenz |
|------------|--------|----------|--------|
| Ternäres MAC | 45 µm² | 0.3 mW | 1 Takt |
| Register | 80 µm² | 0.1 mW | - |
| Kontrolle | 30 µm² | 0.05 mW | - |
| **Gesamt** | **155 µm²** | **0.45 mW** | **1 Takt** |

**Array-Gesamt**: 32×32 = 1024 PEs
- Fläche: 0.16 mm²
- Leistung: 460 mW (dynamisch)

---

## 3. Speicher-Subsystem

### 3.1 Gewichts-ROM (Mask-Locked)

**Design-Spezifikation**:

```
ROM-Organisation:
────────────────────────────────
Gesamtkapazität:    700 Mbit
Anordnung:          1024 Blöcke × 683 Kbit
Zugriffszeit:       1 Takt (1 ns)
Bandbreite:         1024 bits/Takt
                    = 1 Tbit/s @ 1GHz
────────────────────────────────
```

**Masken-Layer**:

| Layer | Funktion | Minimale Feature |
|-------|----------|------------------|
| Metal 1-4 | Bit-Zellen | 90nm Pitch |
| Via 1-3 | Verbindungen | 100nm |
| Diffusion | Auswahltransistoren | 120nm |

**Bit-Zelle Design**:
```
Ternäre ROM-Zelle (2 Bits pro Zelle):

┌─────┐     ┌─────┐
│ M1  │─────│ M2  │  → 00 = -1
└─────┘     └─────┘
    │           │
    X           │         → 01 = 0 (kein Kontakt)
                │
            ┌─────┐
            │ M3  │      → 10 = +1
            └─────┘
```

### 3.2 SRAM-Konfiguration

**KV-Cache SRAM**:

| Parameter | Wert |
|-----------|------|
| Kapazität | 512 KB |
| Organisation | 8 Bänke × 64 KB |
| Zugriff | 2-Port (1R/1W) |
| Latenz | 2 Takte |
| Bandbreite | 128 GB/s |

**Timing-Anforderungen**:
```
CLK → ADDR:     0.2 ns (Setup)
ADDR → DATA:    1.5 ns (Zugriff)
DATA → CLK:     0.1 ns (Hold)
```

### 3.3 LPDDR4-Interface

**Spezifikation**:

| Parameter | Wert |
|-----------|------|
| Typ | LPDDR4-3200 |
| Kapazität | 512 MB (extern) |
| Busbreite | 16-bit |
| Bandbreite | 12.8 GB/s |
| Latenz | CL22 |

**Controller-Features**:
- Automatische Refresh-Verwaltung
- Power-Down-Modi
- ECC-Unterstützung (optional)

---

## 4. Takterzeugung und Verteilung

### 4.1 PLL-Konfiguration

```
Eingang:     50 MHz (Referenz)
Ausgang:     1 GHz (Core)
             500 MHz (SRAM)
             200 MHz (Peripherie)

PLL-Parameter:
────────────────────────────────
VCO-Frequenz:     2 GHz
Teiler Core:      /2 → 1 GHz
Teiler SRAM:      /4 → 500 MHz
Teiler Periph:    /10 → 200 MHz
Jitter (RMS):     < 2 ps
────────────────────────────────
```

### 4.2 Taktverteilung

**Clock-Tree Design**:

```
                    ┌─────┐
        50MHz ─────►│ PLL │
                    └──┬──┘
                       │ 1GHz
        ┌──────────────┼──────────────┐
        │              │              │
    ┌───▼───┐      ┌───▼───┐      ┌───▼───┐
    │Buffer │      │Buffer │      │Buffer │
    └───┬───┘      └───┬───┘      └───┬───┘
        │              │              │
    PE-Bank 0      PE-Bank 1      PE-Bank 2
    (Rows 0-10)    (Rows 11-21)   (Rows 22-31)
```

**Clock Skew Budget**:
- Global Skew: < 50 ps
- Local Skew: < 20 ps
- Insertion Delay: < 200 ps

---

## 5. Stromversorgung

### 5.1 Power-Domains

```
┌─────────────────────────────────────────────┐
│               Power Distribution            │
├─────────────────────────────────────────────┤
│  VDD_Core (0.9V)                            │
│  ├── PE-Array        : 2.5W                 │
│  ├── SRAM            : 0.8W                 │
│  ├── ROM             : 0.3W                 │
│  ├── Controller      : 0.4W                 │
│  └── Clock Tree      : 0.5W                 │
│                      ──────                  │
│                      4.5W                    │
├─────────────────────────────────────────────┤
│  VDD_IO (1.8V)                              │
│  ├── PCIe             : 0.3W                │
│  └── LPDDR4           : 0.2W                │
│                       ──────                 │
│                       0.5W                   │
├─────────────────────────────────────────────┤
│  Total: 5.0W                                │
└─────────────────────────────────────────────┘
```

### 5.2 Power-Gating

**Implementierung**:
```verilog
// Power-Gating Steuerung
module power_gate_ctrl (
    input  clk,
    input  sleep_mode,
    output pg_enable,
    output iso_enable
);
    reg [3:0] sleep_counter;
    
    always @(posedge clk) begin
        if (sleep_mode)
            sleep_counter <= sleep_counter + 1;
        else
            sleep_counter <= 4'b0;
    end
    
    // Power-Gate nach 16 Takten Sleep
    assign pg_enable = (sleep_counter == 4'hF);
    assign iso_enable = pg_enable;
endmodule
```

---

## 6. ESD und Latchup-Schutz

### 6.1 ESD-Spezifikation

| Test | Anforderungen | Ergebnis |
|------|---------------|----------|
| HBM | ±2 kV | Pass |
| CDM | ±500 V | Pass |
| MM | ±200 V | Pass |

### 6.2 I/O-Zellen

**ESD-Clamp Design**:
```
            VDD
             │
         ┌───┴───┐
         │  R    │
         └───┬───┘
             │
PAD ─────┬───┼───┬──── Internal
         │   │   │
        ┌┴┐ ┌┴┐ ┌┴┐
        │ │ │ │ │ │    ESD Clamp
        └┬┘ └┬┘ └┬┘
         │   │   │
            VSS
```

---

## 7. Test- und Debug-Schnittstellen

### 7.1 JTAG-Interface

**Unterstützte Funktionen**:
- Boundary Scan (IEEE 1149.1)
- Debug-Zugriff zu allen Registern
- Memory BIST-Auslösung
- PLL-Konfiguration

### 7.2 Test-Modi

| Modus | Beschreibung | Abdeckung |
|-------|--------------|-----------|
| Scan | ATPG-Muster | 95% |
| MBIST | Memory-Test | 100% |
| LBIST | Logik-BIST | 90% |
| Functional | Funktionstest | Vollständig |

---

## 8. Zuverlässigkeitsanforderungen

### 8.1 Lebensdauer

| Parameter | Spezifikation |
|-----------|---------------|
| Betriebstemperatur | -40°C bis +85°C |
| Lagerungstemperatur | -55°C bis +150°C |
| MTBF | > 100.000 Stunden |
| Design-Lebensdauer | 10 Jahre |

### 8.2 Alterungseffekte

**BTI (Bias Temperature Instability) Degradation**:
```
ΔVth(t) = A × (t/t0)^n × exp(-Ea/kT)

Wobei:
- A = Prozessabhängige Konstante
- n = 0.25 (typisch für 28nm)
- Ea = 0.5 eV
- T = Betriebstemperatur

Ergebnis nach 10 Jahren @ 85°C:
- ΔVth ≈ 30 mV
- Frequenzdegradation < 5%
```

---

## 9. Packaging

### 9.1 Gehäuse-Spezifikation

| Parameter | Wert |
|-----------|------|
| Typ | PBGA |
| Größe | 17mm × 17mm |
| Bälle | 256 |
| Pitch | 1.0mm |
| Material | Halogen-freies EMC |

### 9.2 Thermal-Charakteristik

```
Thermal-Widerstände:
────────────────────────────
θJA (Luft)    : 35°C/W
θJC (Gehäuse) : 8°C/W
θJB (Board)   : 15°C/W
────────────────────────────

Maximale Leistung bei:
- TA = 70°C
- TJmax = 125°C

Pmax = (125 - 70) / 35 = 1.57W

⚠️ Kühlkörper erforderlich für 5W!
```

---

## 10. Qualifikationsplan

### 10.1 Zuverlässigkeitstests

| Test | Bedingungen | Dauer | Proben |
|------|-------------|-------|--------|
| HTOL | 125°C, 1.1×VDD | 1000h | 77 |
| LTOL | -55°C, 1.1×VDD | 1000h | 77 |
| HTS | 150°C | 1000h | 77 |
| THB | 85°C/85%RH | 1000h | 77 |
| TC | -55°C ↔ +125°C | 500 cycles | 77 |

### 10.2 Produktions-Test

```
Wafer-Test (WS):
────────────────────────────
Scan-Pattern:      95% Abdeckung
MBIST:             Alle Speicher
Frequenz-Test:     Binär-Search
Leistungs-Test:    Statische Messung
────────────────────────────

Endtest (FT):
────────────────────────────
Funktionstest:     Vollständig
Geschwindigkeit:   1 GHz Binning
Leistung:          ≤ 5W @ 1GHz
────────────────────────────
```

---

## Anhang A: Pin-Konfiguration

| Pin-Gruppe | Anzahl | Funktion |
|------------|--------|----------|
| Core Power | 32 | VDD/VSS |
| I/O Power | 16 | VDDIO/VSSIO |
| PCIe | 18 | TX/RX/CLK |
| LPDDR4 | 24 | DQ/CA/CLK |
| SPI/I2C | 8 | Konfiguration |
| JTAG | 5 | Debug |
| GPIO | 16 | Status/Steuerung |
| NC | 137 | Reserviert |
| **Gesamt** | **256** | |

---

## Anhang B: Design-for-Test (DFT) Zusammenfassung

```
┌─────────────────────────────────────────────┐
│              DFT-Architektur                │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐  │
│  │ Scan    │   │ MBIST   │   │ LBIST   │  │
│  │ Chain   │   │ Ctrl    │   │ Ctrl    │  │
│  │ 1024    │   │         │   │         │  │
│  └────┬────┘   └────┬────┘   └────┬────┘  │
│       │             │             │        │
│       └─────────────┼─────────────┘        │
│                     │                      │
│              ┌──────▼──────┐               │
│              │   JTAG      │               │
│              │   TAP       │               │
│              └─────────────┘               │
│                                             │
└─────────────────────────────────────────────┘

Test-Abdeckung:
- Scan: 95%
- Memory: 100%
- Logik: 90%
```

---

*Dokumentversion: 2.0*  
*Kontakt: engineering@superinstance.ai*
