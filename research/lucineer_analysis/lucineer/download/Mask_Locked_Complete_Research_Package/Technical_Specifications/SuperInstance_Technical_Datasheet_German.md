# SuperInstance.AI
## Technisches Datenblatt

**Dokumentversion**: 1.0  
**Datum**: März 2026  
**Klassifikation**: Technische Referenzdokumentation  
**Zielgruppe**: Entwicklungsingenieure, Systemintegratoren, Industriekunden

---

# 1. Technische Übersicht

## 1.1 Produktbeschreibung

SuperInstance.AI ist ein KI-Inferenz-Beschleuniger für Edge-Anwendungen, der für den Einsatz in Consumer-Geräten, eingebetteten Systemen und industriellen Anwendungen konzipiert ist. Die Architektur basiert auf einer hybriden Mask-Locked-Technologie mit modularem Cartridge-Design.

## 1.2 Technische Alleinstellungsmerkmale

| Merkmal | Ausprägung | Technische Grundlage |
|---------|------------|---------------------|
| **Gewichtsspeicherung** | Mask-Locked Metal-Interconnect | Null Zugriffsenergie für Gewichte |
| **Arithmetik** | Multiplikationsfrei (C₄-Quantisierung) | Rotation-Accumulate Units |
| **Modularität** | Austauschbare Model-Cartridges | Hardware-Separation von Gewichten und KV-Cache |
| **Leistungsaufnahme** | 2-3W | USB-betrieben, passiv gekühlt |
| **Formfaktor** | USB4-Stick / PCIe-Karte | Consumer- und Industrieanwendungen |

## 1.3 Anwendungsgebiete

- Lokale LLM-Inferenz auf Laptops und Tablets
- Industrielle Edge-Computing-Anwendungen
- Datenschutzkonforme On-Premise-KI-Systeme
- Eingebettete Systeme mit geringer Leistungsaufnahme
- Maker- und Bildungsprojekte

---

# 2. Architektur

## 2.1 Systemarchitektur

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     SUPERINSTANCE.AI ARCHITEKTUR                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│    ┌────────────────────────────────────────────────────────────────┐   │
│    │                    HOST-SCHNITTSTELLE                           │   │
│    │              USB4 (40 Gbps) / PCIe 4.0 x4                       │   │
│    └────────────────────────────┬───────────────────────────────────┘   │
│                                 │                                        │
│    ┌────────────────────────────▼───────────────────────────────────┐   │
│    │                   TRÄGERPLATINE (Fix)                           │   │
│    │  ┌──────────────────────────────────────────────────────────┐  │   │
│    │  │              COMPUTE-ENGINE-ARRAY                        │  │   │
│    │  │         32×32 Systolisches Array (1024 RAUs)             │  │   │
│    │  │         Mask-Locked Gewichte (modell-spezifisch)         │  │   │
│    │  └──────────────────────────────────────────────────────────┘  │   │
│    │  ┌──────────────────────────────────────────────────────────┐  │   │
│    │  │                   STEUERLOGIK                            │  │   │
│    │  │  Token-Streaming FSM │ Attention-Scheduler │ Swarm-Koord. │  │   │
│    │  └──────────────────────────────────────────────────────────┘  │   │
│    └────────────────────────────┬───────────────────────────────────┘   │
│                                 │                                        │
│    ┌────────────────────────────▼───────────────────────────────────┐   │
│    │                 CARTRIDGE-SLOT (Austauschbar)                   │   │
│    │  ┌──────────────────────────────────────────────────────────┐  │   │
│    │  │               LPDDR5-SPEICHER                            │  │   │
│    │  │    KV-Cache (512 MB - 2 GB) │ Token-Puffer │ Konfig.     │  │   │
│    │  └──────────────────────────────────────────────────────────┘  │   │
│    │  ┌──────────────────────────────────────────────────────────┐  │   │
│    │  │              MODEL-IDENTITY-ROM                          │  │   │
│    │  │    Modell-Metadaten │ Gewichts-Checksummen │ Version     │  │   │
│    │  └──────────────────────────────────────────────────────────┘  │   │
│    └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## 2.2 Rotation-Accumulate Unit (RAU)

Die iFairy-RAU-Architektur implementiert komplexe Multiplikation durch reine Datenpermutation.

```
┌──────────────────────────────────────────────────────────────────────┐
│                    ROTATION-ACCUMULATE UNIT                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Eingänge:          a_in (Real) ───┬──────────────────────────────   │
│                     b_in (Imag) ───┼───► 4:1 MUX ──────► real_out   │
│                     w[1:0] (2-bit)─┘    {a,-a,b,-b}                 │
│                                                                       │
│                                   ┌───► 4:1 MUX ──────► imag_out   │
│                                   │    {b,-b,a,-a}                 │
│                                                                       │
│  Akkumulation:     acc_r ──────► Adder (Real) ──────► acc_r_next   │
│                    acc_i ──────► Adder (Imag) ──────► acc_i_next   │
│                                                                       │
│  Gatteranzahl:     ~150 Gatter pro RAU                               │
│  Latenz:           1 Taktzyklus (kombinatorischer Pfad)             │
│  Energie/Op:       ~0,15 pJ (28nm)                                  │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### C₄-Gewichtsoperationen

| Gewicht w | Drehwinkel | Operation | Hardware-Implementierung |
|-----------|-----------|-----------|-------------------------|
| +1 | 0° | Identität | 0 Gatter |
| -1 | 180° | Negation | 2 NOT-Gatter |
| +i | +90° | Swap + Neg(Real) | Wire-Cross + 1 NOT |
| -i | -90° | Swap + Neg(Imag) | Wire-Cross + 1 NOT |

## 2.3 Speicherhierarchie

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      DREI-STUFEN-SPEICHERHIERARCHIE                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  STUFE 0: Mask-ROM-Gewichte (Nur-Lese)                                  │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Kapazität:    2B Parameter × 2 Bit = 500 MB                       │ │
│  │  Kodierung:    Metal-Layer-Routing (Null Zugriffszeit)            │ │
│  │  Bandbreite:   Unbegrenzt (fest verdrahtet)                        │ │
│  │  Leistung:     Null (keine Leseoperation)                          │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                              │                                           │
│                              ▼                                           │
│  STUFE 1: On-Chip SRAM (KV-Cache + Aktivierungen)                       │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Kapazität:    21-42 MB                                            │ │
│  │  Technologie:  6T SRAM, 28nm                                       │ │
│  │  Zugriffszeit: 1-2 Taktzyklen                                      │ │
│  │  Energie:      1-2 pJ/Bit                                          │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                              │                                           │
│                              ▼                                           │
│  STUFE 2: LPDDR5 (Erweiterter Kontext)                                  │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  Kapazität:    512 MB - 2 GB (konfigurierbar)                      │ │
│  │  Technologie:  LPDDR5-6400                                         │ │
│  │  Bandbreite:   51,2 GB/s (2 Kanäle)                                │ │
│  │  Zugriffszeit: 20-40 ns                                            │ │
│  │  Energie:      10-20 pJ/Bit                                        │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

# 3. Technische Spezifikationen

## 3.1 Produktvarianten

| Variante | Formfaktor | Schnittstelle | Leistung | Zielanwendung | UVP |
|----------|-----------|---------------|----------|---------------|-----|
| **Consumer** | USB4-Stick | USB4 (40 Gbps) | 3W | Laptops, Tablets | 35-49 € |
| **Prosumer** | PCIe-Karte | PCIe 4.0 x4 | 15W | Workstations, Edge-Server | 79-149 € |
| **Industrial** | UCIe-Chiplet | UCIe (64 GB/s) | 5W | Eingebettete Systeme, Robotik | Individuell |

## 3.2 Modellunterstützung

| Parameter | Spezifikation |
|-----------|---------------|
| **Unterstützte Modelle** | BitNet 2B-4T, iFairy 700M/1.3B |
| **Parameteranzahl** | 700M - 2.4B |
| **Gewichtsquantisierung** | Ternär {-1, 0, +1} oder C₄ {±1, ±i} |
| **Kontextlänge** | 512 - 4096 Tokens (konfigurierbar) |
| **Modellaustausch** | Cartridge-Wechsel (hardwareseitig) |

## 3.3 Compute-Engine

| Parameter | Wert |
|-----------|------|
| **Array-Konfiguration** | 32 × 32 Systolisches Array |
| **Verarbeitungselemente** | 1024 RAUs |
| **Taktfrequenz** | 250 MHz |
| **Gatter pro RAU** | ~150 |
| **Gesamtgatterzahl (Compute)** | ~153.000 Gatter |

## 3.4 Physikalische Eigenschaften

| Eigenschaft | USB4-Stick | PCIe-Karte |
|-------------|-----------|------------|
| **Abmessungen** | 95 × 25 × 12 mm | 167 × 69 × 20 mm |
| **Gewicht** | 35 g | 180 g |
| **Betriebstemperatur** | 0°C bis 50°C | 0°C bis 60°C |
| **Lagertemperatur** | -20°C bis 70°C | -20°C bis 70°C |
| **Luftfeuchtigkeit** | 10% - 90% (nicht kondensierend) | 10% - 90% (nicht kondensierend) |
| **Kühlung** | Passiv | Passiv |

## 3.5 Herstellungsprozess

| Parameter | Spezifikation |
|-----------|---------------|
| **Prozessknoten** | 28nm (TSMC oder gleichwertig) |
| **Die-Fläche** | ~40 mm² |
| **Transistoranzahl** | ~500M |
| **Verpackung** | BGA / QFN (variabel nach Variante) |

---

# 4. Leistungskennzahlen

## 4.1 Inferenz-Leistung

### Consumer-Tier (USB4-Stick)

| Kennzahl | Zielwert | Toleranz | Testbedingungen |
|----------|----------|----------|-----------------|
| **Durchsatz** | 80-150 tok/s | ±10% | BitNet 2B-4T |
| **First-Token-Latenz** | <50 ms | ±20% | Kaltstart |
| **Inter-Token-Latenz** | 10-15 ms | ±15% | Stationärer Zustand |
| **MMLU-Score** | >50% | - | BitNet 2B-Baseline |
| **Kontextlänge** | 512-2048 Tokens | - | Konfigurierbar |

### Prosumer-Tier (PCIe-Karte)

| Kennzahl | Zielwert | Toleranz | Testbedingungen |
|----------|----------|----------|-----------------|
| **Durchsatz** | 200-400 tok/s | ±10% | BitNet 2B-4T |
| **First-Token-Latenz** | <30 ms | ±20% | Kaltstart |
| **Inter-Token-Latenz** | 5-10 ms | ±15% | Stationärer Zustand |
| **Swarm-Modus** | Bis zu 3 Cartridges | - | Ensemble-Inferenz |

## 4.2 Energieeffizienz-Vergleich

| Produkt | Durchsatz | Leistung | tok/s/W | Relativ |
|---------|-----------|----------|---------|---------|
| **SuperInstance.AI Consumer** | 100 tok/s | 2W | **50** | 29× |
| **SuperInstance.AI Prosumer** | 300 tok/s | 8W | **37,5** | 22× |
| NVIDIA Jetson Orin Nano | 25 tok/s | 15W | 1,7 | 1× (Referenz) |
| Hailo-10H | 9 tok/s | 5W | 1,8 | 1,1× |
| Taalas HC1* | 15.000 tok/s | 200W | 75 | 44× |

*Datacenter-Produkt, anderer Zielmarkt

## 4.3 Qualitätserhaltung bei Quantisierung

| Quantisierungsverfahren | Gewichtssatz | Bits/Gewicht | Relative Qualität |
|------------------------|--------------|--------------|-------------------|
| FP16 (Baseline) | IEEE 754 | 16,0 | 100% |
| INT8 | {-128...+127} | 8,0 | 95-98% |
| INT4 | {-8...+7} | 4,0 | 88-92% |
| BitNet Ternär | {-1, 0, +1} | 1,58 | 90-95% |
| **iFairy C₄** | {±1, ±i} | **2,0** | **100-110%*** |

*Peer-reviewed Ergebnisse (arXiv:2508.05571)

---

# 5. Schnittstellen

## 5.1 USB4-Schnittstelle (Consumer-Tier)

| Parameter | Spezifikation |
|-----------|---------------|
| **Standard** | USB4 Gen 3×2 |
| **Datenrate** | 40 Gbps (bidirektional) |
| **Protokoll** | USB4 Tunneling (PCIe, USB 3.2, DisplayPort) |
| **Stromversorgung** | USB-Bus-Power (5V, max. 3W) |
| **Stecker** | USB-C (Reversible) |
| **Treiber** | Plug-and-Play (Windows 11, macOS 14+, Linux Kernel 6.0+) |

### USB4-Pinbelegung

| Pin | Funktion | Signal |
|-----|----------|--------|
| A1-A4, B1-B4 | Masse & Stromversorgung | GND, VBUS (5V) |
| A5, B5 | Konfigurationskanal | CC1, CC2 |
| A6-A7, B6-B7 | USB 2.0 | D+, D- |
| A8-A9, B8-B9 | Hochgeschwindigkeits-Differential | TX1±, RX1± |
| A10-A11, B10-B11 | Hochgeschwindigkeits-Differential | TX2±, RX2± |

## 5.2 PCIe-Schnittstelle (Prosumer-Tier)

| Parameter | Spezifikation |
|-----------|---------------|
| **Standard** | PCIe 4.0 x4 |
| **Datenrate** | 64 Gbps (16 GT/s × 4 Lanes) |
| **Formfaktor** | Low-Profile PCIe-Add-in-Card |
| **Stromversorgung** | PCIe-Steckplatz (75W verfügbar, max. 15W genutzt) |
| **Abmessungen** | 167,65 mm × 68,90 mm (Low-Profile) |
| **Kühlung** | Passiver Kühlkörper |

### PCIe-Konfigurationsraum

| Offset | Register | Wert |
|--------|----------|------|
| 0x00 | Vendor ID | 0xXXXX (TBD) |
| 0x02 | Device ID | 0xXXXX (TBD) |
| 0x04 | Command | 0x0007 (Memory, I/O, Bus Master) |
| 0x08 | Revision ID | 0x01 |
| 0x0A | Class Code | 0x1180 (AI Accelerator) |
| 0x10 | BAR0 | Memory-Mapped Registers |
| 0x14 | BAR1 | Cartridge-Memory-Window |

## 5.3 GPIO und Erweiterung (Industrial-Tier)

| Parameter | Spezifikation |
|-----------|---------------|
| **Schnittstelle** | UCIe (Universal Chiplet Interconnect Express) |
| **Datenrate** | 64 GB/s (konfigurierbar) |
| **GPIO-Anzahl** | 16 (multiplexiert) |
| **Spannungspegel** | 1,8V / 3,3V (konfigurierbar) |
| **Funktionen** | Status-LEDs, Interrupts, Cartridge-Detection |

### GPIO-Pindefinitionen

| GPIO | Funktion | Richtung | Beschreibung |
|------|----------|----------|--------------|
| 0-2 | Status-LED | Ausgang | Aktivität / Fehler / Bereitschaft |
| 3 | Cartridge-Detect | Eingang | Cartridge vorhanden |
| 4 | Cartridge-Lock | Ausgang | Cartridge verriegelt |
| 5-7 | Reserved | - | Reserviert für zukünftige Erweiterungen |
| 8-15 | Debug-Interface | Bidirektional | JTAG / UART-Debug |

## 5.4 Cartridge-Schnittstelle

| Parameter | Spezifikation |
|-----------|---------------|
| **Verbinder-Typ** | Proprietärer High-Density-Verbinder |
| **Kontaktanzahl** | 120 Pins |
| **Speicherinterface** | LPDDR5-6400 (2 Kanäle) |
| **Identifikations-ROM** | I²C (32 KB EEPROM) |
| **Wechselzyklen** | Min. 500 Einsteckzyklen |
| **Hot-Swap** | Unterstützt (Hardware-Locking erforderlich) |

---

# 6. Stromverbrauch

## 6.1 Leistungsaufnahme nach Betriebszustand

| Betriebszustand | Consumer (USB4) | Prosumer (PCIe) | Bemerkung |
|-----------------|-----------------|-----------------|-----------|
| **Inferenz (Peak)** | 2,0-2,5W | 8-12W | Bei 100 tok/s |
| **Inferenz (Nominal)** | 1,5-2,0W | 6-8W | Durchschnitt |
| **Idle (Bereit)** | 300-500mW | 1-2W | Sleep-Mode aktiv |
| **Standby (Tiefschlaf)** | <50mW | <100mW | USB-Suspend / PCIe-D3 |
| **Ausgeschaltet** | <1mW | <5mW | Power-Down |

## 6.2 Energieverbrauch pro Token

```
Energieverbrauch pro Token (Consumer-Tier):
─────────────────────────────────────────────

Komponente           Energie/Token    Anteil
─────────────────────────────────────────────
Compute (RAU)        50-100 μJ        15-25%
KV-Cache (SRAM)      150-200 μJ       40-50%
Steuerlogik          30-50 μJ         8-12%
I/O (USB)            20-30 μJ         5-8%
Leckstrom            30-50 μJ         10-15%
─────────────────────────────────────────────
GESAMT               280-430 μJ       100%

Leistung bei 100 tok/s = ~35-43 mW (theoretisch)
Tatsächliche Leistung = 1,5-2,5W (Overhead eingerechnet)
```

## 6.3 Detaillierte Leistungsaufschlüsselung

### Consumer-Tier (2W Budget)

| Komponente | Leistung | Anmerkung |
|------------|----------|-----------|
| Compute-Array | ~0,5W | Bei 250 MHz, 1024 RAUs |
| SRAM-Zugriff | ~0,8W | 21 MB, 80 tok/s |
| USB-I/O | ~0,3W | 5V/500mA Budget |
| Leckstrom (28nm) | ~0,2W | Raumtemperatur |
| Steuerlogik | ~0,2W | FSM, Routing |
| **Gesamt** | **~2W** | **Innerhalb 3W Budget** |

## 6.4 Energieeffizienz-Vergleich

| Computing-Paradigma | Energie/MAC | Relative Effizienz |
|--------------------|-------------|-------------------|
| Digital FP16 | 50-100 pJ | 1× |
| Digital INT8 | 10-30 pJ | 3-10× |
| Digital Ternär | 0,5-2 pJ | 50-200× |
| **iFairy RAU** | **0,1-0,5 pJ** | **100-500×** |
| **2T1C PIM*** | **1-5 fJ** | **10.000-100.000×** |

*Prozess-In-Memory (analoge Crossbar), geplant für zukünftige Generationen

---

# 7. Datenschutz und Compliance

## 7.1 DSGVO-Konformität

### Datensparsamkeit

SuperInstance.AI verarbeitet alle KI-Inferenz lokal auf dem Gerät. Es werden keine Benutzerdaten an externe Server übertragen.

| DSGVO-Prinzip | Implementierung |
|---------------|-----------------|
| **Datenminimierung** | Keine Cloud-Kommunikation, lokale Verarbeitung |
| **Zweckbindung** | Daten verbleiben auf dem Endgerät des Nutzers |
| **Speicherbegrenzung** | Keine dauerhafte Speicherung von Benutzerdaten |
| **Integrität** | Offline-Betrieb verhindert externe Manipulation |
| **Transparenz** | Open-Source-Treiber, dokumentierte Datenflüsse |

### Technische Maßnahmen

| Maßnahme | Beschreibung |
|----------|--------------|
| **Air-Gap-Betrieb** | Vollständige Offline-Funktionalität |
| **Keine Telemetrie** | Keine Nutzungsdatenübertragung |
| **Lokale Speicherung** | KV-Cache verbleibt im RAM (flüchtig) |
| **Open-Source** | Treiber und SDK vollständig einsehbar |

## 7.2 Zertifizierungen

| Zertifizierung | Status | Beschreibung |
|---------------|--------|--------------|
| **CE-Kennzeichnung** | Geplant | Konformität EU-Richtlinien |
| **FCC Part 15 (Class B)** | Geplant | US-EMV-Konformität |
| **RoHS** | Geplant | Beschränkung gefährlicher Stoffe |
| **REACH** | Geplant | EU-Chemikalienverordnung |
| **USB-IF** | Geplant | USB4-Logo-Nutzung |

## 7.3 Sicherheit

### Hardware-Sicherheit

| Funktion | Implementierung |
|----------|-----------------|
| **Secure Boot** | Verifizierte Firmware-Signatur |
| **Cartridge-Authentifizierung** | Kryptographische Verifizierung |
| **JTAG-Lock** | Debug-Interface deaktivierbar |
| **Temper-Schutz** | Erkennung physischer Manipulation (optional) |

### Software-Sicherheit

| Funktion | Implementierung |
|----------|-----------------|
| **Treiber-Signatur** | Signierte Windows/macOS/Linux-Treiber |
| **API-Authentifizierung** | Zugriffskontrolle für Inferenz-API |
| **Memory-Isolation** | Separater Adressraum für Cartridge-Speicher |

---

# 8. Qualitätssicherung

## 8.1 Design-Verifikation

| Verifikationsmethode | Abdeckung | Werkzeuge |
|---------------------|-----------|-----------|
| **Funktionale Simulation** | 100% Code Coverage | Verilator, VCS |
| **Formale Verifikation** | Kritische Pfade | JasperGold |
| **Timing-Analyse** | Static Timing Analysis | PrimeTime |
| **Leistungsanalyse** | Gate-Level Power | PrimeTime-PX |
| **Linting** | 100% RTL | SpyGlass, Verilator |

## 8.2 Test- und Validierungsprozess

### FPGA-Prototypisierung (Gate 0)

| Test | Ziel | Kriterium |
|------|------|-----------|
| Funktionale Korrektheit | BitNet-Inferenz | Identische Ausgabe zu Referenz |
| Durchsatz | Min. 25 tok/s | KV260-FPGA |
| Leistungsaufnahme | <5W | Messung |

### Silizium-Validierung (Gate 2)

| Test | Ziel | Kriterium |
|------|------|-----------|
| Funktionale Validierung | Alle Betriebsmodi | Automatisierte Testsuite |
| Performanz | 80-150 tok/s | Silizium-Messung |
| Leistungsaufnahme | <2,5W | Silizium-Messung |
| EMV | CE/FCC-Limits | Zertifizierungslabor |
| Temperatur | 0-50°C Betrieb | Klimakammer |

## 8.3 Lebensdauer und Zuverlässigkeit

| Parameter | Spezifikation |
|-----------|---------------|
| **MTBF** | >100.000 Stunden (industrielle Anwendung) |
| **Lebensdauer** | 10 Jahre bei normaler Nutzung |
| **Flash-Schreibzyklen** | N/A (kein Flash für Benutzerdaten) |
| **Cartridge-Steckzyklen** | Min. 500 Zyklen |

### Umgebungsbedingungen

| Bedingung | Spezifikation |
|-----------|---------------|
| **Betriebstemperatur** | 0°C bis 50°C (Consumer), 0°C bis 60°C (Industrial) |
| **Lagertemperatur** | -20°C bis 70°C |
| **Relative Luftfeuchtigkeit** | 10% bis 90% (nicht kondensierend) |
| **Vibration** | IEC 60068-2-6 |
| **Schock** | IEC 60068-2-27 |

---

# 9. Bestellinformationen

## 9.1 Produktkennzeichnung

### Consumer-Tier (USB4-Stick)

| Bestellnummer | Beschreibung | UVP |
|---------------|--------------|-----|
| SI-USB4-B2-35 | BitNet 2B-4T, 512 Tokens On-Chip | 35 € |
| SI-USB4-B2-49 | BitNet 2B-4T, 2K Tokens, 512MB LPDDR5 | 49 € |
| SI-USB4-B2-69 | BitNet 2B-4T, 4K Tokens, 1GB LPDDR5 | 69 € |

### Prosumer-Tier (PCIe-Karte)

| Bestellnummer | Beschreibung | UVP |
|---------------|--------------|-----|
| SI-PCIE-B2-79 | BitNet 2B-4T, Single-Cartridge | 79 € |
| SI-PCIE-B2-149 | BitNet 2B-4T, Triple-Cartridge (Swarm) | 149 € |

### Cartridges (Ersatz/Upgrade)

| Bestellnummer | Beschreibung | UVP |
|---------------|--------------|-----|
| CARTRIDGE-B2-512 | BitNet 2B-4T, 512 Tokens | 15 € |
| CARTRIDGE-B2-2K | BitNet 2B-4T, 2K Tokens | 25 € |
| CARTRIDGE-B2-4K | BitNet 2B-4T, 4K Tokens | 35 € |
| CARTRIDGE-IF1-2K | iFairy 1.3B, 2K Tokens | 30 € |

## 9.2 Mindestbestellmengen

| Kundentyp | Mindestbestellmenge | Lieferzeit |
|-----------|---------------------|------------|
| Einzelnutzer | 1 Stück | 2-4 Wochen |
| Wiederverkäufer | 50 Stück | 4-6 Wochen |
| Industriekunde | 100 Stück | 6-8 Wochen |
| OEM-Kunde | 1.000 Stück | 8-12 Wochen |

## 9.3 Garantiebedingungen

| Produkt | Garantiezeit | Umfang |
|---------|--------------|--------|
| Hardware (Consumer) | 2 Jahre | Material- und Herstellungsfehler |
| Hardware (Industrial) | 3 Jahre | Material- und Herstellungsfehler |
| Cartridges | 1 Jahr | Material- und Herstellungsfehler |
| Software/Treiber | Keine gesonderte Garantie | Open-Source, AS-IS |

---

# 10. Kontakt und Support

## 10.1 Technischer Support

| Kanal | Verfügbarkeit | Reaktionszeit |
|-------|---------------|---------------|
| **E-Mail: support@superinstance.ai** | Mo-Fr 09:00-18:00 CET | 24 Stunden |
| **GitHub Issues** | 24/7 | Community-Support |
| **Dokumentation** | docs.superinstance.ai | Self-Service |

## 10.2 Vertrieb

| Region | Kontakt | Telefon |
|--------|---------|---------|
| **Deutschland, Österreich, Schweiz** | sales-de@superinstance.ai | +49 (0)XXX XXX XXXX |
| **EU (übrige)** | sales-eu@superinstance.ai | +31 (0)XXX XXX XXXX |
| **USA / Kanada** | sales-na@superinstance.ai | +1 (XXX) XXX-XXXX |
| **Asien-Pazifik** | sales-apac@superinstance.ai | +81 (0)XXX XXX XXXX |

## 10.3 Unternehmensinformationen

| Information | Details |
|-------------|---------|
| **Firmensitz** | [Adresse einfügen] |
| **Rechtsform** | [Rechtsform einfügen] |
| **Handelsregister** | [Nummer einfügen] |
| **USt-IdNr.** | [Nummer einfügen] |
| **Geschäftsführung** | [Name einfügen] |

## 10.4 Dokumentationsressourcen

| Ressource | URL |
|-----------|-----|
| Technische Dokumentation | docs.superinstance.ai |
| API-Referenz | api.superinstance.ai/docs |
| GitHub-Repository | github.com/superinstance |
| GitHub-Diskussionen | github.com/superinstance/community/discussions |

---

# Anhang A: Abkürzungsverzeichnis

| Abkürzung | Bedeutung |
|-----------|-----------|
| ASIC | Application-Specific Integrated Circuit |
| BGA | Ball Grid Array |
| CE | Communauté Européenne (EU-Konformität) |
| DSGVO | Datenschutz-Grundverordnung |
| EMV | Elektromagnetische Verträglichkeit |
| FCC | Federal Communications Commission |
| FSM | Finite State Machine |
| GPIO | General Purpose Input/Output |
| KV | Key-Value |
| LLM | Large Language Model |
| LPDDR | Low-Power Double Data Rate |
| MAC | Multiply-Accumulate |
| MMLU | Massive Multitask Language Understanding |
| MPW | Multi-Project Wafer |
| MTBF | Mean Time Between Failures |
| PCIe | Peripheral Component Interconnect Express |
| QFN | Quad Flat No-leads |
| RAU | Rotation-Accumulate Unit |
| RoHS | Restriction of Hazardous Substances |
| SRAM | Static Random-Access Memory |
| UCIe | Universal Chiplet Interconnect Express |
| UVP | Unverbindliche Preisempfehlung |
| USB | Universal Serial Bus |

---

# Anhang B: Änderungshistorie

| Version | Datum | Änderungen |
|---------|-------|------------|
| 1.0 | März 2026 | Erste Veröffentlichung |

---

# Rechtlicher Hinweis

Dieses Dokument dient ausschließlich Informationszwecken und stellt keine rechtsverbindliche Zusicherung dar. Technische Spezifikationen können ohne vorherige Ankündigung geändert werden. Alle Markenzeichen und eingetragenen Marken sind Eigentum ihrer jeweiligen Inhaber.

Die in diesem Dokument enthaltenen Leistungsangaben basieren auf Labormessungen und Simulationen unter definierten Bedingungen. Die tatsächliche Leistung kann je nach Anwendung, Umgebung und Konfiguration variieren.

Für die aktuellsten Spezifikationen und Verfügbarkeiten wenden Sie sich bitte an unseren Vertrieb.

---

*© 2026 SuperInstance.AI. Alle Rechte vorbehalten.*
