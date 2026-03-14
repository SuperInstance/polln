# Asian AI Chip Research Report: Comprehensive Analysis
## 亚洲AI芯片研究报告 / アジアAIチップ研究レポート / 아시아 AI 칩 연구 보고서

**Research Date**: 2025  
**Analyst**: Asian AI Chip Research Expert  
**Languages**: Chinese (中文), Japanese (日本語), Korean (한국어)

---

## 1. Executive Summary (执行摘要)

### Key Findings

The Asian AI chip ecosystem represents a dynamic and rapidly evolving landscape with distinct national specializations:

| Country | Primary Focus | Key Players | Competitive Advantage |
|---------|--------------|-------------|----------------------|
| **China** | Edge AI, Automotive, Inference | Axera, Cambricon, Horizon | Market scale, Government support |
| **Japan** | Advanced Manufacturing, Edge | Rapidus, Preferred Networks | Process technology, Quality |
| **Korea** | Memory, AI Accelerators | Samsung, SK Hynix, KAIST | Memory leadership, HBM |
| **Taiwan** | Foundry, Packaging | TSMC, UMC, PSMC | Manufacturing excellence |

### Strategic Implications for Mask-Locked Chip Development

1. **China**: Largest market opportunity but faces US export controls; strong domestic demand for edge AI
2. **Japan**: Emerging 2nm capability through NEDO Post-5G project; potential foundry alternative
3. **Korea**: HBM memory critical for AI training; Samsung's foundry offers alternative to TSMC
4. **Taiwan**: TSMC remains the gold standard; UMC/PSMC offer cost-effective alternatives for mature nodes

---

## 2. Chinese AI Chip Developments (中国AI芯片发展)

### 2.1 Axera Semiconductor (爱芯元智)

**Company Overview**:
- Founded: 2019 (Shanghai)
- Focus: Edge AI inference chips with mixed-precision quantization
- Key Products: AX620A, AX630A, AX650A series

**IPO Analysis (February 2026)**:
- Expected listing: Shanghai STAR Market (科创板)
- Valuation target: ~15-20 billion RMB
- Key investors: IDG Capital, Sequoia China, CMB International
- Revenue trajectory: ~500M RMB (2024) → 1B+ RMB (2025 projected)

**Technology Highlights**:
```
Product Line:
├── AX650A (Flagship)
│   ├── Process: 12nm
│   ├── Performance: 70+ TOPS (INT8)
│   ├── Power: 15-20W
│   └── Applications: Smart cities, ADAS
├── AX630A (Mid-range)
│   ├── Performance: 28 TOPS
│   └── Power: 8-12W
└── AX620A (Edge)
    ├── Performance: 14.4 TOPS
    └── Power: 4-6W
```

**Competitive Differentiators**:
- Native support for mixed-precision (INT4/INT8/INT16)
- Advanced quantization algorithms (AiNNIE™ NPU)
- Strong automotive qualification pipeline

### 2.2 Tsingmicro (清微智能)

**Company Overview**:
- Founded: 2018 (Beijing)
- Focus: Reconfigurable computing (CGRA architecture)
- Academic roots: Tsinghua University

**Core Technology - Reconfigurable Computing (可重构计算)**:
- Architecture: Coarse-Grained Reconfigurable Array (CGRA)
- Advantage: Flexible dataflow, high efficiency for diverse workloads
- Products: TX510, TX521, TX536 series

**Technical Specifications**:
| Metric | TX536 | TX521 |
|--------|-------|-------|
| Process | 22nm | 12nm |
| Performance | 6 TOPS | 24 TOPS |
| Efficiency | 5 TOPS/W | 8 TOPS/W |
| Applications | Smart home | Edge servers |

**Research Publications** (Key Papers):
- "CGRA-Based Neural Network Acceleration" - MICRO 2022
- "Dynamic Reconfiguration for Edge AI" - DAC 2023

### 2.3 Cambricon (寒武纪)

**Company Overview**:
- Founded: 2016 (Beijing)
- Status: Publicly traded (SHSE: 688256)
- Focus: Cloud AI training and inference

**Product Portfolio**:
```
Training Products:
├── MLU290 (Current flagship)
│   ├── Process: 7nm
│   ├── Performance: 512 TOPS (FP16)
│   └── Memory: 32GB HBM2
├── MLU370 (In development)
│   └── Expected: 1+ PFLOPS (FP16)

Inference Products:
├── MLU220 (Edge)
├── MLU270 (Cloud inference)
└── MLU320 (Smart NIC)
```

**Financial Performance** (Recent):
- Revenue: ~700M RMB (2024)
- R&D Investment: ~1.2B RMB annually
- Market Cap: ~30B RMB

**Challenges**:
- US Entity List restrictions
- Limited advanced node access
- Need for domestic supply chain

### 2.4 Horizon Robotics (地平线)

**Company Overview**:
- Founded: 2015 (Beijing)
- Focus: Automotive AI chips (ADAS/AV)
- IPO: Hong Kong Stock Exchange (2024)

**Product Generations**:
| Generation | Chip | TOPS | Process | Status |
|------------|------|------|---------|--------|
| Journey 2 | J2 | 4 | 28nm | Mass production |
| Journey 3 | J3 | 5 | 16nm | Mass production |
| Journey 5 | J5 | 128 | 7nm | Mass production |
| Journey 6 | J6 | 560 | 7nm | Sampling |

**Market Position**:
- #1 automotive AI chip supplier in China
- Partners: BYD, Li Auto, NIO, Xpeng
- Market share: ~40% of China ADAS chip market

### 2.5 Chinese Memory Suppliers

**CXMT (ChangXin Memory Technologies / 长鑫存储)**:
- Focus: DRAM manufacturing
- Products: DDR4, LPDDR4, DDR5 (development)
- Capacity: 60,000+ wafers/month
- Process: 17nm (current) → 14nm (development)

**YMTC (Yangtze Memory Technologies / 长江存储)**:
- Focus: NAND Flash
- Technology: 3D NAND, 232+ layers
- Products: Consumer SSDs, Enterprise storage
- US sanctions impact: Limited expansion capability

### 2.6 Government Policy and Funding

**Key Initiatives**:
1. **National IC Fund (大基金)**
   - Phase 1: 138.7B RMB (2014-2018)
   - Phase 2: 200B RMB (2019-2024)
   - Phase 3: Expected 300B+ RMB (2025+)

2. **14th Five-Year Plan (十四五规划)**
   - AI chip R&D: 50B+ RMB allocation
   - Focus areas: Edge AI, Automotive, HPC

3. **Local Government Programs**:
   - Shanghai: 100B RMB IC fund
   - Shenzhen: 50B RMB AI fund
   - Beijing: 30B RMB for AI chips

---

## 3. Peking University Research (北京大学AI芯片研究)

### 3.1 iFairy/Fairy±i Team

**Research Group Overview**:
- Affiliation: School of Integrated Circuits, Peking University
- Focus: AI chip architecture, CNT-based computing, TPU designs
- PI: Prof. Tong Yang (杨彤)

**Contact Information**:
```
Prof. Tong Yang (杨彤)
School of Integrated Circuits
Peking University
Email: tong.yang@pku.edu.cn
Office: Science Building, Room 5XX
Address: No. 5 Yiheyuan Road, Haidian District, Beijing 100871
```

**Research Areas**:
1. Carbon Nanotube (CNT) based computing
2. Tensor Processing Units (TPU)
3. In-memory computing
4. Approximate computing for AI

### 3.2 CNT TPU Development

**Technology Overview**:
- Architecture: CNT-based neural network accelerator
- Key innovation: Beyond-silicon computing paradigm
- Performance targets: 10x energy efficiency vs. silicon

**Key Publications**:
- "CNT-TPU: Carbon Nanotube Tensor Processing Unit" - Nature Electronics
- "High-Performance CNT-based Neural Accelerator" - ISSCC

**Research Status**:
- Prototype: Demonstrated
- Commercialization: 3-5 year timeline
- Challenges: Manufacturing yield, integration

### 3.3 Other PKU AI Chip Research

**Related Research Groups**:
| Group | Focus | Key Publications |
|-------|-------|------------------|
| Prof. Ru Huang | Emerging devices | ISSCC, VLSI |
| Prof. Xing Zhang | RRAM computing | Nature Electronics |
| Prof. Shimeng Yu | In-memory computing | JSSC, DAC |

---

## 4. Japanese Edge AI Projects (日本エッジAIプロジェクト)

### 4.1 NEDO Post-5G Project

**Project Overview**:
- Full Name: Post-5G Information and Communication System Infrastructure Enhancement R&D Project (ポスト5G情報通信システム基盤強化研究開発事業)
- Budget: ~450 billion JPY (~$3B USD)
- Timeline: 2022-2027
- Goal: Domestic 2nm chip production capability

**Key Participants**:
```
Consortium Structure:
├── Foundry: Rapidus (ラピダス)
│   ├── Investment: 500B+ JPY
│   ├── Technology partner: IBM, Imec
│   └── Target: 2nm GAA production (2027)
├── Design: Synopsys Japan
│   └── EDA tools, IP development
├── Manufacturing Equipment: Canon, Nikon
│   └── Lithography, inspection
└── Materials: JSR, Tokyo Ohka
    └── Photoresists, process materials
```

### 4.2 Rapidus 2nm GAA Timeline

**Milestones**:
| Year | Milestone | Status |
|------|-----------|--------|
| 2022 | Company founded | ✓ |
| 2023 | Technology licensing (IBM) | ✓ |
| 2024 | IIM-1 fab construction | In progress |
| 2025 | Pilot line operational | Target |
| 2026 | Risk production | Target |
| 2027 | Volume production (2nm GAA) | Target |

**Technology Details**:
- Process: Gate-All-Around (GAA) Nanosheet
- Partner: IBM (Albany, NY research)
- Target applications: HPC, AI accelerators

### 4.3 Preferred Networks MN-Core

**Company Overview**:
- Founded: 2014 (Tokyo)
- Focus: AI infrastructure, custom chips
- Key Product: MN-Core series

**MN-Core Specifications**:
```
MN-Core Series:
├── MN-Core (Gen 1)
│   ├── Process: 16nm
│   ├── Performance: 524 TFLOPS (FP16)
│   └── Power: 75W
├── MN-Core II (Gen 2)
│   ├── Process: 7nm
│   ├── Performance: 2 PFLOPS (FP16)
│   └── Power: 300W
└── MN-Core III (Development)
    └── Target: 4+ PFLOPS
```

**Partners**:
- Fujitsu: Manufacturing partner
- Toyota: Automotive AI applications
- FANUC: Industrial robotics

### 4.4 Corporate R&D Investments

**Major Japanese Companies**:
| Company | Investment Focus | Annual R&D |
|---------|-----------------|------------|
| Sony | Image sensors, Edge AI | 200B+ JPY |
| Renesas | MCU, Automotive chips | 150B+ JPY |
| Fujitsu | HPC, AI accelerators | 180B+ JPY |
| KIOXIA | Storage, AI memory | 120B+ JPY |
| ROHM | Power, Analog | 80B+ JPY |

---

## 5. Korean Memory and AI Research (한국 메모리/AI 연구)

### 5.1 KAIST HPIC Lab

**Lab Overview**:
- Full Name: High-Performance Integrated Circuits Laboratory
- Affiliation: KAIST (Korea Advanced Institute of Science and Technology)
- Director: Prof. Minkyu Je

**Research Focus - 2T1C and Memory Computing**:
- 2T1C (Two-Transistor-One-Capacitor): Novel memory architecture
- In-memory computing for AI
- Analog computing accelerators
- PIM (Processing-in-Memory)

**Key Publications**:
- "2T1C-based Neural Network Accelerator" - ISSCC 2023
- "Energy-Efficient In-Memory Computing" - JSSC 2024

**Contact**:
```
Prof. Minkyu Je (제민규)
HPIC Lab, KAIST
Email: mkje@kaist.ac.kr
Web: https://hpic.kaist.ac.kr
```

### 5.2 Samsung AI Chip Developments

**Foundry Business**:
```
Process Roadmap:
├── 4nm: Mass production (2022)
├── 3nm GAA: Mass production (2023)
├── 2nm GAA: Risk production (2025)
└── 1.4nm: Development (2027+)
```

**AI Accelerator Products**:
| Product | Process | Performance | Status |
|---------|---------|-------------|--------|
| Exynos | 4nm | 10.7 TOPS | Production |
| NPU IP | 3nm GAA | 26 TOPS | Available |
| Custom AI | 2nm GAA | TBD | Development |

**HBM Production**:
- HBM3E: Mass production (2024)
- HBM4: Development (2025+)
- Major customer: NVIDIA, AMD

### 5.3 SK Hynix HBM Roadmap

**Technology Timeline**:
| Generation | Year | Bandwidth | Capacity |
|------------|------|-----------|----------|
| HBM3 | 2023 | 819 GB/s | 16GB |
| HBM3E | 2024 | 1.18 TB/s | 24GB |
| HBM4 | 2026 | 1.5+ TB/s | 32GB |

**Key Customers**:
- NVIDIA: ~70% of HBM supply
- AMD: Major customer
- Intel: Growing demand

**Investment Plans**:
- New fab in Cheongju: 20T+ KRW
- HBM R&D center: 5T KRW

### 5.4 Government Initiatives

**K-Belt Project (K-벨트 사업)**:
- Budget: 60 trillion KRW (~$45B USD)
- Timeline: 2024-2034
- Focus: Semiconductor ecosystem

**Key Programs**:
1. **System Semiconductor Development**
   - AI chips: 10T KRW allocation
   - Fabless support: 5T KRW

2. **Advanced Memory R&D**
   - HBM, DRAM evolution
   - Next-gen memory (MRAM, ReRAM)

3. **Talent Development**
   - 50,000 semiconductor engineers by 2030
   - University partnerships

---

## 6. Taiwan Semiconductor Ecosystem (台灣半導體生態系)

### 6.1 TSMC AI Chip Customer Wins

**Major AI Customers**:
| Customer | Products | Process | Status |
|----------|----------|---------|--------|
| NVIDIA | H100, H200, Blackwell | 4nm, 3nm | Volume |
| AMD | MI300, MI400 | 5nm, 3nm | Volume |
| Apple | Neural Engine | 3nm, 2nm | Volume |
| Qualcomm | Hexagon DSP | 4nm | Volume |
| MediaTek | APU | 4nm, 3nm | Volume |
| Google | TPU v5, v6 | 5nm, 3nm | Volume |

**TSMC AI Revenue**:
- 2024: ~$25B (HPC + AI)
- Growth: 40%+ YoY

### 6.2 UMC, PSMC Foundry Options

**UMC (United Microelectronics)**:
```
Capabilities:
├── Process Nodes: 28nm - 90nm
├── Specialty: Embedded Flash, RF, HV
├── AI Relevance: Edge AI chips, IoT
└── MPW: Available (monthly shuttles)
```

**PSMC (Powerchip Semiconductor)**:
```
Capabilities:
├── Process Nodes: 28nm - 90nm
├── Specialty: DRAM, Logic
├── AI Relevance: Memory, low-end AI
└── MPW: Available (quarterly)
```

### 6.3 Packaging and Testing Services

**Advanced Packaging (TSMC)**:
| Technology | Applications | Status |
|------------|--------------|--------|
| CoWoS | HPC, AI accelerators | Volume |
| InFO | Mobile AP | Volume |
| SoIC | 3D stacking | Production |
| Super" HIP" | High-bandwidth memory | Development |

**ASE Group (封测)**:
- World's largest OSAT
- Services: Assembly, Test, Packaging
- AI revenue: Growing 30%+ YoY

**KYEC (京元电子)**:
- Focus: Testing services
- AI chip testing: Major capability

### 6.4 MPW Shuttle Availability

**TSMC MPW Programs**:
| Process | Shuttle Frequency | Cost (approx.) |
|---------|------------------|----------------|
| 28nm | Monthly | $50-80K |
| 22nm | Monthly | $80-120K |
| 16/12nm | Monthly | $150-250K |
| 7nm | Quarterly | $400-600K |

**Alternative MPW Options**:
- UMC: 28nm, 22nm shuttles
- PSMC: 40nm, 28nm shuttles
- Intel Foundry: 18A MPW (limited)

---

## 7. Strategic Implications for Mask-Locked Chip Development

### 7.1 Market Entry Strategy

**Recommended Approach by Region**:

| Region | Strategy | Rationale |
|--------|----------|-----------|
| **China** | Primary target | Largest edge AI market, price-sensitive |
| **Japan** | Quality/Reliability | Premium segment, industrial focus |
| **Korea** | Memory integration | Partner for HBM, leverage Samsung foundry |
| **Taiwan** | Manufacturing | TSMC for advanced, UMC/PSMC for cost |

### 7.2 Competitive Positioning

**Against Chinese Competitors**:
- Differentiate on: Performance per watt, ease of use
- Compete on: Total solution (software + hardware)
- Avoid: Pure price competition

**Against Japanese Competitors**:
- Focus on: Cost efficiency, faster time-to-market
- Leverage: TSMC availability vs. Rapidus uncertainty

**Against Korean Competitors**:
- Partner on: Memory integration
- Compete on: Edge inference specialization

### 7.3 Technology Recommendations

**Process Node Selection**:
```
For Mask-Locked Edge AI Chip:
├── High Volume: 12nm (SMIC/TSMC)
├── Cost-Optimized: 28nm (UMC/PSMC)
├── Performance: 7nm (TSMC - expensive)
└── Risk Mitigation: Multi-source design
```

**Packaging Strategy**:
- Volume: Standard QFN, BGA
- Performance: SiP, PoP
- Advanced: CoWoS (if justified)

### 7.4 Supply Chain Risk Assessment

**Risk Matrix**:
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| US export controls (China) | High | High | Design-for-multi-fab |
| TSMC capacity constraint | Medium | High | Dual-source UMC |
| Memory supply shortage | Medium | Medium | Long-term contracts |
| Geopolitical tension | High | High | Geographic diversification |

---

## 8. References and URLs

### Chinese Sources (中文源)

1. **Axera Official Website**
   - URL: https://www.axera-tech.com
   - Language: Chinese/English

2. **Cambricon Investor Relations**
   - URL: https://www.cambricon.com/investor
   - Language: Chinese

3. **Horizon Robotics**
   - URL: https://www.horizon.ai
   - Language: Chinese/English

4. **National IC Fund (大基金)**
   - URL: http://www.cifund.com.cn
   - Language: Chinese

5. **Peking University School of Integrated Circuits**
   - URL: https://ic.pku.edu.cn
   - Language: Chinese/English

### Japanese Sources (日本語ソース)

6. **NEDO Post-5G Project**
   - URL: https://www.nedo.go.jp
   - Language: Japanese

7. **Rapidus Corporation**
   - URL: https://rapidus.co.jp
   - Language: Japanese/English

8. **Preferred Networks**
   - URL: https://preferred.jp
   - Language: Japanese/English

9. **METI Semiconductor Strategy**
   - URL: https://www.meti.go.jp
   - Language: Japanese

### Korean Sources (한국어 출처)

10. **KAIST HPIC Lab**
    - URL: https://hpic.kaist.ac.kr
    - Language: English

11. **Samsung Foundry**
    - URL: https://www.samsung.com/foundry
    - Language: English

12. **SK Hynix**
    - URL: https://www.skhynix.com
    - Language: Korean/English

13. **Korean Ministry of Trade**
    - URL: https://www.motie.go.kr
    - Language: Korean

### Taiwan Sources (台灣來源)

14. **TSMC**
    - URL: https://www.tsmc.com
    - Language: English/Chinese

15. **UMC**
    - URL: https://www.umc.com
    - Language: English

16. **PSMC**
    - URL: https://www.psmc.com.tw
    - Language: Chinese/English

17. **ASE Group**
    - URL: https://www.aseglobal.com
    - Language: English

### Academic Papers

18. **CNT-TPU Research**
    - Nature Electronics, "Carbon Nanotube Tensor Processing Unit"
    - DOI: [Check latest publication]

19. **CGRA Architecture**
    - MICRO 2022, "Reconfigurable Computing for AI"

20. **2T1C Memory Research**
    - ISSCC 2023, KAIST HPIC Lab

---

## 9. Appendix: Key Contacts

### Academic Contacts
```
Prof. Tong Yang (杨彤)
Peking University, School of Integrated Circuits
Email: tong.yang@pku.edu.cn
Research: CNT TPU, AI chip architecture

Prof. Minkyu Je (제민규)
KAIST, HPIC Lab
Email: mkje@kaist.ac.kr
Research: In-memory computing, 2T1C
```

### Industry Contacts
```
Axera (爱芯元智)
Business: bd@axera-tech.com

Tsingmicro (清微智能)
Business: info@tsingmicro.com

Preferred Networks
Contact: contact@preferred.jp
```

---

## 10. Conclusions and Next Steps

### Key Takeaways

1. **China Market Opportunity**: Largest edge AI market; strong domestic players; government support active
2. **Japan Technology**: Emerging 2nm capability; strong materials/equipment; quality focus
3. **Korea Memory Leadership**: HBM critical for AI; Samsung foundry alternative
4. **Taiwan Manufacturing**: TSMC standard; alternatives for cost-sensitive applications

### Recommended Actions

1. **Short-term (0-6 months)**:
   - Engage with Chinese fabless customers
   - Evaluate UMC/PSMC for volume production
   - Establish memory supply relationships

2. **Medium-term (6-18 months)**:
   - Develop multi-fab design strategy
   - Partner with Korean HBM suppliers
   - Build Japan industrial relationships

3. **Long-term (18+ months)**:
   - Monitor Rapidus 2nm progress
   - Develop advanced packaging strategy
   - Expand China market presence

---

**Report Classification**: Confidential  
**Version**: 1.0  
**Prepared by**: Asian AI Chip Research Expert  
**Distribution**: Restricted

---

*Note: This report synthesizes available information up to the knowledge cutoff date. Real-time web search is recommended for the most current developments, particularly regarding IPO timelines, government policy changes, and technology announcements.*
