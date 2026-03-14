# TernaryAir Voxel Platform Schemas
## Complete System Architecture

**Version:** 2.0  
**Date:** March 2026

---

## Part 1: Lucineer - Chip Design Co-Inventor

### 1.1 System Overview

**Lucineer** is an AI co-inventor that progressively iterates from high-level abstractions to detailed chip schemas ready for Cadence/Synopsis.

```
ABSTRACTION LAYERS (Top to Bottom):
┌─────────────────────────────────────────────┐
│ Layer 0: Use Case Vision                    │
│   "Smart downrigger for Sitka fishing"      │
└─────────────────────────────────────────────┘
           ↓ Lucineer asks clarifying questions
┌─────────────────────────────────────────────┐
│ Layer 1: System Architecture                │
│   Sensors → Processing → Actuators          │
└─────────────────────────────────────────────┘
           ↓ Component selection begins
┌─────────────────────────────────────────────┐
│ Layer 2: Hardware Selection                 │
│   MCU, sensors, power, connectivity         │
└─────────────────────────────────────────────┘
           ↓ Tradeoff discussions
┌─────────────────────────────────────────────┐
│ Layer 3: Board Layout Considerations        │
│   Form factor, casing, thermal, cost        │
└─────────────────────────────────────────────┘
           ↓ Chip specification
┌─────────────────────────────────────────────┐
│ Layer 4: Model Selection for Edge           │
│   BitNet vs iFairy vs custom, quantization  │
└─────────────────────────────────────────────┘
           ↓ Detailed design
┌─────────────────────────────────────────────┐
│ Layer 5: Intra-Chip Design                  │
│   RAU arrays, memory, I/O, timing           │
└─────────────────────────────────────────────┘
           ↓ Export schemas
┌─────────────────────────────────────────────┐
│ Layer 6: EDA Export (Cadence/Synopsis)      │
│   RTL, constraints, layout hints            │
└─────────────────────────────────────────────┘
```

### 1.2 Voxel Environment Schema

```typescript
interface VoxelWorld {
  // World configuration
  id: string;
  name: string;
  type: 'sandbox' | 'simulation' | 'puzzle';
  
  // Geographic data integration
  geography: {
    terrainSource: 'generated' | 'real_world';
    location?: {
      name: string;  // "Sitka, Alaska"
      coordinates: [number, number];  // [lat, lng]
      underwater: boolean;
    };
    imageryProvider?: 'google_earth' | 'navionics' | 'noaa';
  };
  
  // Voxel grid
  grid: {
    size: [number, number, number];  // [x, y, z] in voxels
    resolution: number;  // meters per voxel
    origin: [number, number, number];  // real-world coordinates
  };
  
  // Entities in world
  entities: VoxelEntity[];
  
  // Physics simulation
  physics: {
    enabled: boolean;
    gravity: number;
    waterLevel?: number;
    current?: Vector3D;
  };
  
  // API connections
  integrations: {
    imageGenerator?: APIConnection;
    webSearch?: APIConnection;
    chartProvider?: APIConnection;
  };
}

interface VoxelEntity {
  id: string;
  type: 'boat' | 'device' | 'sensor' | 'terrain' | 'water' | 'fish' | 'custom';
  
  // Voxel composition
  voxels: Voxel[];
  
  // Behavior
  behavior?: EntityBehavior;
  
  // Chip design link (for devices)
  chipDesign?: ChipSchema;
  
  // Interactive elements
  interactive: boolean;
  clickable: boolean;
  draggable: boolean;
}

interface Voxel {
  position: [number, number, number];
  color: string;
  material: 'solid' | 'transparent' | 'emissive' | 'water';
  
  // Component reference (for chip design)
  component?: LogicComponent;
}

interface EntityBehavior {
  type: 'static' | 'animated' | 'simulated' | 'ai_controlled';
  
  // For AI/ML components
  model?: {
    type: 'bitnet' | 'ifairy' | 'custom';
    weights?: string;  // Reference to model weights
    inference: 'local' | 'edge_device' | 'cloud';
  };
  
  // State machine for logic
  states?: StateDefinition[];
}
```

### 1.3 Progressive Iteration Engine

```typescript
interface ProgressiveIteration {
  currentLayer: AbstractionLayer;
  
  // Conversation context
  conversation: Message[];
  
  // Extracted requirements
  requirements: {
    functional: Requirement[];
    constraints: Constraint[];
    preferences: Preference[];
  };
  
  // Generated artifacts
  artifacts: {
    blockDiagrams: BlockDiagram[];
    schematics: Schematic[];
    codeSnippets: CodeSnippet[];
    simulations: SimulationResult[];
  };
  
  // Next steps
  suggestedQuestions: string[];
  requiredDecisions: Decision[];
}

type AbstractionLayer = 
  | 'use_case'      // Layer 0
  | 'architecture'  // Layer 1
  | 'hardware'      // Layer 2
  | 'layout'        // Layer 3
  | 'model'         // Layer 4
  | 'chip_design'   // Layer 5
  | 'eda_export';   // Layer 6

// Lucineer conversation patterns
const lucineerPatterns = {
  // Layer 0 → Layer 1
  useCaseToArchitecture: [
    "What sensors will your {device} need?",
    "How will {device} communicate with the user?",
    "What's the power source for {device}?",
    "What are the environmental conditions where {device} operates?",
  ],
  
  // Layer 1 → Layer 2
  architectureToHardware: [
    "Given your {constraints}, I recommend {mcu}. Does {price_point} work?",
    "For {sensor_type}, we could use {option_a} or {option_b}. {tradeoff}.",
    "The {component} you selected needs {power}. Is battery life a concern?",
  ],
  
  // Layer 2 → Layer 3
  hardwareToLayout: [
    "Your components need about {area} board space. What's the casing size?",
    "Thermal analysis shows {temp} at peak load. Do you need a heatsink?",
    "For {price_point}, I suggest {board_type}. Here's a rough layout...",
  ],
  
  // Layer 3 → Layer 4
  layoutToModel: [
    "You need to detect {pattern}. BitNet {size} model would fit in {memory}.",
    "For latency under {ms}ms, consider {quantization} quantization.",
    "The iFairy addition-only architecture could reduce power by {percent}%.",
  ],
  
  // Layer 4 → Layer 5
  modelToChipDesign: [
    "Your model needs {macs} operations per inference. Here's the RAU array...",
    "Memory bandwidth requires {mbps}. Let's plan the bus architecture.",
    "For {target_fps} FPS, we need {pipeline_stages} pipeline stages.",
  ],
  
  // Layer 5 → Layer 6
  chipDesignToEDA: [
    "Generating RTL for Cadence...",
    "Here are the timing constraints for Synopsis...",
    "Layout hints generated based on your form factor...",
  ],
};
```

### 1.4 Sitka Downrigger Example Flow

```typescript
const sitkaDownriggerExample = {
  // User starts at Layer 0
  initialPrompt: "I want to design a smart downrigger for fishing in Sitka, Alaska",
  
  // Lucineer Layer 0 Response
  layer0Response: {
    message: "Exciting project! Sitka has unique underwater terrain and currents. Let me pull up some data...",
    actions: [
      "Load Navionics chart for Sitka Sound",
      "Generate 3D underwater terrain from bathymetry",
      "Create voxel simulation environment",
    ],
    questions: [
      "What species are you targeting? (affects depth and speed)",
      "Do you want real-time sonar integration?",
      "What's your target price point for the device?",
    ],
  },
  
  // Geographic Integration
  geographicData: {
    location: "Sitka, Alaska",
    coordinates: [57.0531, -135.3300],
    chartSources: ["Navionics", "NOAA Bathymetry"],
    imagerySources: ["Google Earth", "Satellite"],
    environmentalData: {
      waterDepth: "20-300m",
      commonCurrent: "0.5-2 knots",
      visibility: "10-50 feet",
    },
  },
  
  // Progressive Abstraction
  progression: [
    {
      layer: "use_case",
      summary: "Smart downrigger for Sitka salmon fishing",
      decisions: ["Target: King Salmon", "Depth: 50-200ft", "Sonar: Yes"],
    },
    {
      layer: "architecture",
      summary: "Depth sensor → MCU → Motor controller → App",
      decisions: ["Wireless: BLE", "Power: Rechargeable Li-ion"],
    },
    {
      layer: "hardware",
      summary: "ESP32-C3 + depth sensor + stepper driver",
      decisions: ["MCU: ESP32-C3 ($2)", "Sensor: MS5837 ($8)"],
    },
    {
      layer: "layout",
      summary: "Circular PCB, 50mm diameter, IP68 housing",
      decisions: ["Form: Fits standard downrigger", "Price: <$75 target"],
    },
    {
      layer: "model",
      summary: "TinyML depth optimization model",
      decisions: ["BitNet 0.73B", "Int4 quantization", "200KB weights"],
    },
    {
      layer: "chip_design",
      summary: "Custom ternary inference accelerator",
      decisions: ["4 RAU arrays", "SRAM 256KB", "USB-C power"],
    },
    {
      layer: "eda_export",
      summary: "RTL + constraints ready for fabrication",
      deliverables: ["chip.v", "constraints.sdc", "layout_hints.json"],
    },
  ],
};
```

---

## Part 2: Young Learners Voxel Puzzles

### 2.1 System Overview

**Voxel Playground for Ages 4-10** featuring character-driven puzzles that teach AI and technology concepts through play.

```
DESIGN PHILOSOPHY:
┌─────────────────────────────────────────────┐
│ "Incredible Machine meets Minecraft         │
│  meets AI Education"                        │
│                                              │
│  • Silly characters with serious lessons    │
│  • Fail-forward gameplay                    │
│  • Voxel building with purpose              │
│  • AI concepts as game mechanics            │
└─────────────────────────────────────────────┘
```

### 2.2 Character System Schema

```typescript
interface GameCharacter {
  id: string;
  name: string;
  emoji: string;
  
  // Visual representation
  voxelModel: VoxelModel;
  animations: {
    idle: Animation;
    happy: Animation;
    confused: Animation;
    working: Animation;
    success: Animation;
  };
  
  // Personality
  personality: {
    speechPattern: 'simple' | 'rhyming' | 'technical' | 'silly';
    catchphrase: string;
    encouragementStyle: 'cheerleader' | 'coach' | 'friend' | 'detective';
  };
  
  // Educational role
  teaches: ConceptCategory[];
  
  // Interaction
  voiceEnabled: boolean;
  subtitlesEnabled: boolean;
}

// Main Characters
const characters: GameCharacter[] = [
  {
    id: 'terny',
    name: 'Terny the Robot',
    emoji: '🤖',
    personality: {
      speechPattern: 'simple',
      catchphrase: "Let's figure this out together!",
      encouragementStyle: 'friend',
    },
    teaches: ['logic', 'patterns', 'sequences'],
  },
  {
    id: 'data',
    name: 'Data the Dog',
    emoji: '🐕',
    personality: {
      speechPattern: 'silly',
      catchphrase: "I'll fetch the answer! *woof*",
      encouragementStyle: 'cheerleader',
    },
    teaches: ['data', 'classification', 'sorting'],
  },
  {
    id: 'logic',
    name: 'Logic the Owl',
    emoji: '🦉',
    personality: {
      speechPattern: 'rhyming',
      catchphrase: "Think it through, the answer's with you!",
      encouragementStyle: 'coach',
    },
    teaches: ['reasoning', 'if-then', 'deduction'],
  },
  {
    id: 'pixel',
    name: 'Pixel the Cat',
    emoji: '🐱',
    personality: {
      speechPattern: 'silly',
      catchphrase: "Patterns are like yarn - fun to play with!",
      encouragementStyle: 'friend',
    },
    teaches: ['patterns', 'images', 'recognition'],
  },
  {
    id: 'neural',
    name: 'Neural the Octopus',
    emoji: '🐙',
    personality: {
      speechPattern: 'technical',
      catchphrase: "I have many connections, and so does your brain!",
      encouragementStyle: 'detective',
    },
    teaches: ['neural_networks', 'connections', 'learning'],
  },
];
```

### 2.3 Puzzle Schema

```typescript
interface VoxelPuzzle {
  id: string;
  name: string;
  description: string;
  
  // Age targeting
  ageRange: [number, number];  // [min, max]
  difficulty: 1 | 2 | 3 | 4 | 5;
  
  // Puzzle type
  category: PuzzleCategory;
  
  // Learning objectives
  objectives: LearningObjective[];
  
  // Voxel world setup
  world: {
    size: [number, number, number];
    initialEntities: VoxelEntity[];
    goalState: GoalCondition;
    availableComponents: Component[];
  };
  
  // Tutorial/hints
  tutorial: TutorialSequence;
  hintSystem: Hint[];
  
  // Rewards
  rewards: {
    stars: number;  // 1-3 based on efficiency
    badges: string[];
    unlockNext: string[];
  };
}

type PuzzleCategory = 
  | 'pattern_recognition'
  | 'logic_chains'
  | 'data_flow'
  | 'training_simulation'
  | 'sensor_processing'
  | 'agent_coordination';

interface LearningObjective {
  concept: string;
  bloomsLevel: 'remember' | 'understand' | 'apply' | 'analyze' | 'create';
  assessment: AssessmentCriteria;
}

// Example Puzzle: Pattern Pipeline
const patternPipelinePuzzle: VoxelPuzzle = {
  id: 'pattern-pipe-01',
  name: "Pixel's Pattern Pipeline",
  description: "Help Pixel sort the colorful blocks!",
  ageRange: [4, 6],
  difficulty: 1,
  category: 'pattern_recognition',
  
  objectives: [
    {
      concept: 'pattern_matching',
      bloomsLevel: 'apply',
      assessment: 'Correctly sorts 80% of blocks',
    },
  ],
  
  world: {
    size: [20, 10, 20],
    initialEntities: [
      { type: 'conveyor', position: [0, 0, 0] },
      { type: 'block_spawner', position: [0, 5, 0] },
      { type: 'bin_red', position: [10, 0, 5] },
      { type: 'bin_blue', position: [10, 0, 10] },
    ],
    goalState: {
      type: 'sort_accuracy',
      threshold: 0.8,
    },
    availableComponents: [
      { type: 'color_sensor', cost: 1 },
      { type: 'diverter', cost: 1 },
      { type: 'conveyor', cost: 1 },
    ],
  },
  
  tutorial: {
    steps: [
      {
        highlight: 'block_spawner',
        message: "Blocks will come out here! Watch their colors.",
        character: 'pixel',
      },
      {
        highlight: 'color_sensor',
        message: "Place a sensor to detect the color!",
        character: 'terny',
      },
      {
        highlight: 'diverter',
        message: "Connect the sensor to a diverter to sort!",
        character: 'logic',
      },
    ],
  },
  
  rewards: {
    stars: 3,
    badges: ['first_sorter'],
    unlockNext: ['pattern-pipe-02'],
  },
};
```

### 2.4 Age-Appropriate Scaffolding

```typescript
const ageScaffolding = {
  // Ages 4-5: Maximum guidance, minimal text
  age4to5: {
    instructionMethod: 'animation_only',
    maxSteps: 3,
    componentLimit: 3,
    hintFrequency: 'always',
    celebrationIntensity: 'maximum',
    failureFeedback: 'giggle_and_reset',
  },
  
  // Ages 6-7: Icons + simple text, moderate guidance
  age6to7: {
    instructionMethod: 'animation_plus_icons',
    maxSteps: 5,
    componentLimit: 5,
    hintFrequency: 'on_request',
    celebrationIntensity: 'high',
    failureFeedback: 'gentle_suggestion',
  },
  
  // Ages 8-10: Full interaction, challenge mode
  age8to10: {
    instructionMethod: 'animation_icons_text',
    maxSteps: 10,
    componentLimit: 10,
    hintFrequency: 'earned',
    celebrationIntensity: 'moderate',
    failureFeedback: 'analytical_hint',
  },
};
```

### 2.5 Component Interaction System

```typescript
// Based on Incredible Machine patterns
interface VoxelComponent {
  id: string;
  type: ComponentType;
  
  // Voxel representation
  voxels: VoxelDefinition[];
  animations: ComponentAnimations;
  
  // Socket system (connection points)
  inputs: InputSocket[];
  outputs: OutputSocket[];
  
  // Behavior
  behavior: ComponentBehavior;
  
  // Feedback
  sounds: SoundEffects;
  particles: ParticleEffects;
}

interface InputSocket {
  id: string;
  position: [number, number, number];  // Local offset
  type: 'signal' | 'data' | 'power' | 'mechanical';
  acceptsFrom: string[];  // Compatible output types
  visual: {
    inactive: Color;
    active: Color;
    pulseAnimation: boolean;
  };
}

interface OutputSocket {
  id: string;
  position: [number, number, number];
  type: 'signal' | 'data' | 'power' | 'mechanical';
  outputValue: (inputs: any[]) => any;
  visual: {
    glow: boolean;
    trailEffect: boolean;
    colorByValue: boolean;
  };
}

// Example Components
const componentLibrary = {
  // Sensors (Input Components)
  colorSensor: {
    type: 'sensor',
    inputs: [],
    outputs: [{ type: 'data', value: 'detected_color' }],
    behavior: { type: 'detect', property: 'color' },
  },
  
  // Logic (Processing Components)
  comparator: {
    type: 'logic',
    inputs: [{ type: 'data' }, { type: 'data' }],
    outputs: [{ type: 'signal', value: 'match_result' }],
    behavior: { type: 'compare', operation: 'equals' },
  },
  
  // Actuators (Output Components)
  diverter: {
    type: 'actuator',
    inputs: [{ type: 'signal' }],
    outputs: [],
    behavior: { type: 'redirect', direction: 'left_or_right' },
  },
  
  // Connectors (Flow Components)
  conveyor: {
    type: 'connector',
    inputs: [{ type: 'mechanical' }],
    outputs: [{ type: 'mechanical' }],
    behavior: { type: 'transport', speed: 1 },
  },
};
```

### 2.6 AI Concept Mappings to Game Mechanics

```typescript
const conceptToMechanicMap = {
  // Pattern Recognition → Sorting Puzzles
  pattern_recognition: {
    gameMechanic: 'sort_colored_blocks',
    aiConcept: 'classification',
    ageVariants: {
      '4-5': 'Two colors only, visual feedback',
      '6-7': 'Three colors, timing element',
      '8-10': 'Patterns within patterns, custom rules',
    },
  },
  
  // Logic Chains → Domino/Rube Goldberg
  logic_chains: {
    gameMechanic: 'chain_reaction',
    aiConcept: 'rule_execution',
    ageVariants: {
      '4-5': 'Three-piece chain, obvious connections',
      '6-7': 'Five-piece chain, some branching',
      '8-10': 'Multi-path chains, optimization',
    },
  },
  
  // Data Flow → Pipe Routing
  data_flow: {
    gameMechanic: 'pipe_connection',
    aiConcept: 'information_routing',
    ageVariants: {
      '4-5': 'Single path, color-coded',
      '6-7': 'Multiple inputs to single output',
      '8-10': 'Transforms and filters along path',
    },
  },
  
  // Training → Teaching by Example
  training_simulation: {
    gameMechanic: 'show_and_tell',
    aiConcept: 'supervised_learning',
    ageVariants: {
      '4-5': 'Show happy/sad examples, character learns',
      '6-7': 'Multiple categories, character gets confused',
      '8-10': 'Feature selection, what matters for learning',
    },
  },
  
  // Neural Networks → Connection Building
  neural_networks: {
    gameMechanic: 'connection_puzzle',
    aiConcept: 'weighted_connections',
    ageVariants: {
      '4-5': 'Connect dots, strength = line thickness',
      '6-7': 'Multiple layers, visual weight feedback',
      '8-10': 'Adjust weights, see prediction change',
    },
  },
  
  // Agent Coordination → Multi-character Tasks
  agent_coordination: {
    gameMechanic: 'team_puzzle',
    aiConcept: 'distributed_systems',
    ageVariants: {
      '4-5': 'Two characters, simple task split',
      '6-7': 'Three characters, communication needed',
      '8-10': 'Multiple agents, optimization challenge',
    },
  },
};
```

---

## Part 3: Integration Architecture

### 3.1 Shared Voxel Engine

```typescript
interface VoxelEngine {
  // Core rendering
  renderer: {
    library: 'three.js';
    antialias: boolean;
    shadows: boolean;
    postProcessing: PostProcessingStack;
  };
  
  // Physics
  physics: {
    engine: 'cannon-es' | 'ammo.js';
    gravity: Vector3D;
    collisions: CollisionSystem;
  };
  
  // Interaction
  interaction: {
    raycasting: boolean;
    selection: SelectionSystem;
    dragDrop: DragDropSystem;
  };
  
  // Serialization
  saveLoad: {
    format: 'json' | 'binary';
    compression: boolean;
    cloudSync: boolean;
  };
}
```

### 3.2 API Integration Layer

```typescript
interface APIIntegrationManager {
  // Image generation for terrain/objects
  imageGeneration: {
    providers: ['openai', 'stability', 'midjourney', 'local'];
    useCases: ['terrain_texture', 'object_appearance', 'concept_art'];
  };
  
  // Web search for real-world data
  webSearch: {
    providers: ['google', 'bing', 'duckduckgo'];
    useCases: ['charts', 'specs', 'examples'];
  };
  
  // Chart/map data
  chartData: {
    providers: ['navionics', 'noaa', 'google_maps'];
    useCases: ['bathymetry', 'navigation', 'terrain'];
  };
  
  // LLM for Lucineer
  llm: {
    providers: ['groq', 'openai', 'anthropic', 'local_ollama'];
    useCases: ['invention_coaching', 'code_generation', 'explanation'];
  };
}
```

---

## Part 4: Development Roadmap

### Phase 1: Core Infrastructure (Rounds 1-3)
- Voxel engine integration
- Basic component system
- Homepage third button + Chip Design landing

### Phase 2: Professional Tools (Rounds 4-6)
- Lucineer conversation system
- Real-world data integration
- Progressive iteration engine

### Phase 3: Young Learners (Rounds 7-8)
- Character system
- Age-appropriate puzzles
- Scaffolding system

### Phase 4: Polish & Integration (Rounds 9-10)
- Cross-platform testing
- Performance optimization
- Final documentation

---

*Schema Version: 2.0.0*
