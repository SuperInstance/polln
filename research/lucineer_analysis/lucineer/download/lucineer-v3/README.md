# Lucineer v3.0

**Become a Lucineer** — Learn AI Through Timing & Play

## Overview

Lucineer is an open-source educational platform teaching AI concepts through timing games, interactive simulations, and chip design tools. From playground games to professional hardware design, one platform serves all ages.

## Features

### 🎮 Learning Platform
- **Age-Adaptive Content**: Same concepts taught at 4 different depth levels
- **Timing Simulators**: Traffic lights, domino chains, state machines
- **Offline-First**: Works without internet, progress saved locally

### 🔧 TernaryAir Chip Design Studio
- **Voxel Playground**: 3D hardware prototyping
- **Progressive Iteration**: From concept to Cadence-ready schemas
- **Lucineer AI Co-Inventor**: AI-assisted chip design

### 🔌 API Connections
- Multi-provider support (Groq, OpenAI, x.ai, DeepSeek, Kimi, Anthropic, Ollama)
- Local-first key storage with encryption
- Works offline with local models

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **Storage**: IndexedDB (local-first)
- **License**: MIT

## Project Structure

```
lucineer-v3/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Homepage
│   │   ├── layout.tsx            # Root layout
│   │   ├── globals.css           # Global styles
│   │   ├── learning/             # Learning modules
│   │   ├── ternaryair/           # Chip design studio
│   │   ├── timing-playground/    # Simulators
│   │   ├── api-connect/          # API management
│   │   ├── downloads/            # Download center
│   │   └── research/             # Research hub
│   └── components/
│       ├── Navigation.tsx        # Main navigation
│       └── Footer.tsx            # Site footer
├── DESIGN_SYSTEM.md              # Complete style guide
├── COMPONENT_EXTRACTION_ANALYSIS.md  # Standalone repo analysis
├── INTER_PROJECT_SYNERGY.md      # Ecosystem documentation
├── package.json
├── tailwind.config.ts
└── tsconfig.json
```

## Getting Started

```bash
# Install dependencies
bun install

# Run development server
bun run dev

# Build for production
bun run build
```

## Age Groups

| Group | Ages | Focus |
|-------|------|-------|
| Young Learners | 4-10 | Games, traffic lights, musical chairs |
| Middle School | 11-14 | Animation timing, beat programming |
| High School | 15-18 | Digital logic, timing analysis |
| Professional | 18+ | FPGA, CDC, pipeline optimization |

## Partner Ecosystem

Lucineer is part of a larger ecosystem:

- **[SuperInstance.AI](https://superinstance.ai)** — AI within spreadsheets
- **[LucidDreamer.com](https://luciddreamer.com)** — Community building platform

## License

MIT License — Free forever, open source.

---

*Version 3.0.0 | March 2026*
