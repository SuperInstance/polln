# LLN Playground - Schema Documentation v1.0
# Cross-Cultural Engineering & Architecture for Next Generation Systems
# Generated from 30 Rounds of Playtesting with Diverse User Groups

## Executive Summary

This document provides comprehensive schema definitions for the LLN (Large Language Networks) 
Playground system, synthesized from 30 rounds of playtesting with diverse user groups including:

- Asian and African cultural perspectives (Rounds 11-20)
- Hardware and software engineers (Rounds 15-18)
- Retired life-long learners (Rounds 16-18)
- Parent-child pairs (Rounds 19-20)
- Cross-cultural engineering teams (Rounds 21-25)
- Tile-based programming platform research (Rounds 26-30)

---

## Core Schemas

### 1. User Profile Schema

```typescript
interface UserProfile {
  // Identity
  id: string;                           // UUID
  displayName: string;
  avatar: string;                       // URL or emoji
  
  // Cultural Context (Critical for ML Growth)
  culturalProfile: {
    primaryCulture: ISO3166Alpha2;      // e.g., "JP", "NG", "CN", "KE"
    secondaryCultures: ISO3166Alpha2[];
    primaryLanguage: ISO6391;           // e.g., "en", "sw", "zh", "ja"
    additionalLanguages: ISO6391[];
    familyStructure: "individual" | "parent-child" | "multi-gen" | "group";
    generationInTech: "first" | "second" | "third+";
  };
  
  // Learning Profile
  learningProfile: {
    ageGroup: "child" | "teen" | "adult" | "elder";
    techExperience: "basic" | "intermediate" | "advanced" | "expert";
    primaryRole: UserRole;              // kid, teen, developer, researcher, etc.
    preferredPace: "slow" | "medium" | "fast";
    learningStyle: ("visual" | "auditory" | "kinesthetic" | "reading")[];
    conceptualFramework: "physics" | "biology" | "economics" | "music" | "history" | "general";
  };
  
  // Progress Tracking
  progress: {
    level: number;
    xp: number;
    achievements: string[];
    gamesPlayed: number;
    gamesWon: number;
    totalTokens: number;
    tokensSaved: number;
    idiomsCreated: number;
    currentStreak: number;
    bestStreak: number;
  };
  
  // Preferences
  preferences: {
    theme: "light" | "dark" | "auto";
    soundEnabled: boolean;
    animationsEnabled: boolean;
    language: ISO6391;
    difficulty: "beginner" | "intermediate" | "advanced" | "expert";
    aiAssistance: boolean;
    showTutorial: boolean;
    culturalTheme: string;              // Cultural UI theme preference
  };
}

type UserRole = "kid" | "teen" | "developer" | "researcher" | "enterprise" | 
                "educator" | "hobbyist" | "scientist" | "pm" | "artist" | 
                "parent_child" | "elder";
```

### 2. Agent Persona Schema

```typescript
interface AgentPersona {
  // Identity
  id: string;
  name: string;
  emoji: string;
  description: string;
  
  // Role & Behavior
  role: "actor" | "guesser" | "judge" | "helper" | "challenger" | "observer";
  personality: string;
  communicationStyle: "formal" | "casual" | "playful" | "technical" | "cultural";
  
  // Cultural Adaptation (NEW from Round 11-20)
  culturalAdaptation: {
    originCulture: ISO3166Alpha2;
    languageCapabilities: ISO6391[];
    culturalKnowledge: {
      greetings: Record<ISO6396Alpha2, string>;
      celebrations: string[];
      proverbs: string[];
      idioms: string[];
    };
    ageAppropriate: ("child" | "teen" | "adult" | "elder")[];
    respectfulForms: boolean;          // Uses formal/respectful language
  };
  
  // Technical Configuration
  modelConfig: {
    model: "gpt-4" | "claude-3" | "gemini-pro" | string;
    temperature: number;               // 0.0 - 1.0
    maxTokens: number;
    topP: number;
    frequencyPenalty: number;
    presencePenalty: number;
  };
  
  // System Prompt Template
  systemPromptTemplate: {
    base: string;
    culturalVariants: Record<ISO3166Alpha2, string>;
    ageVariants: Record<string, string>;
    roleVariants: Record<UserRole, string>;
  };
  
  // Unlock Criteria
  unlockCriteria: {
    requiredLevel: number;
    requiredAchievements: string[];
    requiredCulturalQuests: string[];
  };
  
  // Stats
  stats: {
    tokensUsed: number;
    wins: number;
    idiomsGenerated: number;
    culturalAdaptations: number;
  };
}
```

### 3. Game Mode Schema

```typescript
interface GameMode {
  // Identity
  id: string;
  name: string;
  description: string;
  icon: string;
  
  // Classification
  difficulty: "beginner" | "intermediate" | "advanced" | "expert";
  category: "guessing" | "creative" | "competitive" | "collaborative" | "educational";
  
  // Player Configuration
  players: {
    min: number;
    max: number;
    roles: AgentRole[];
  };
  
  // Game Rules
  rules: {
    turnOrder: "sequential" | "simultaneous" | "mixed";
    timeLimit: number | null;          // seconds per turn
    rounds: number | "infinite";
    winningCondition: string;
    scoringSystem: "points" | "tokens" | "time" | "accuracy";
  };
  
  // Token Economics (NEW from Round 15-18)
  tokenEconomics: {
    baseCost: number;
    constraintMultiplier: number;
    efficiencyBonus: number;
    savingsTracking: boolean;
  };
  
  // Cultural Variants (NEW from Round 11-14)
  culturalVariants: Record<ISO3166Alpha2, {
    name: string;
    localRules: string[];
    themedWords: string[];
    culturalConstraints: string[];
  }>;
  
  // Integration with Tile-Based Platforms
  tileIntegration: {
    visualStyle: "blocks" | "icons" | "text" | "mixed";
    dragDrop: boolean;
    snapToGrid: boolean;
    colorCoding: Record<string, string>;
  };
}
```

### 4. Constraint Schema

```typescript
interface Constraint {
  // Identity
  id: string;
  type: ConstraintType;
  value: string;
  emoji: string;
  description: string;
  
  // Difficulty & Classification
  difficulty: "beginner" | "intermediate" | "advanced" | "expert";
  category: "linguistic" | "creative" | "technical" | "cultural";
  
  // Token Impact
  penalty: number;                     // Token multiplier
  bonusForSuccess: number;
  
  // Cultural Context (NEW from Round 11-14)
  culturalOrigin: ISO3166Alpha2;
  culturalContext: string;
  applicableCultures: ISO3166Alpha2[];
  
  // Activation Rules
  activationRules: {
    unlockLevel: number;
    prerequisiteConstraints: string[];
    incompatibleConstraints: string[];
    maxActive: number;
  };
  
  // ML Feedback Loop
  mlMetadata: {
    usageCount: number;
    successRate: number;
    avgTokenCost: number;
    userSatisfactionScore: number;
    culturalEffectiveness: Record<ISO3166Alpha2, number>;
  };
}

type ConstraintType = 
  | "rhyme" 
  | "no-letter" 
  | "roast" 
  | "negative" 
  | "haiku" 
  | "emoji-only" 
  | "one-syllable" 
  | "alphabetical" 
  | "pirate" 
  | "shakespeare"
  | "proverb"              // NEW: African proverbs
  | "tangram"              // NEW: Chinese tangram logic
  | "origami"              // NEW: Japanese folding patterns
  | "rhythm"               // NEW: African rhythm patterns
  | "calligraphy"          // NEW: Asian brush stroke patterns
  | "storytelling"         // NEW: Oral tradition narratives
  | "ubuntu"               // NEW: Collaborative only
  | "custom";
```

### 5. Idiom Schema

```typescript
interface Idiom {
  // Identity
  id: string;
  shorthand: string;                   // Emoji sequence or text shorthand
  meaning: string;
  category: string;
  
  // Origin Tracking
  origin: {
    agents: string[];                  // Agent IDs
    gameMode: string;
    constraints: string[];
    cultures: ISO3166Alpha2[];         // NEW: Cultural origins
    roundId: string;
    timestamp: number;
  };
  
  // Token Economics
  tokenSavings: number;
  usageCount: number;
  effectiveness: number;               // 0.0 - 1.0
  
  // SMPbot (Single Mastery Point Bot)
  smpbot: {
    lockedToSeed: boolean;
    seed: string | null;
    deterministic: boolean;
    applicationDomain: string[];
  };
  
  // Cultural Translation (NEW from Round 11-14)
  translations: Record<ISO6391, {
    shorthand: string;
    meaning: string;
    culturalNotes: string;
  }>;
  
  // ML Training Data
  mlData: {
    trainingExamples: string[];
    contextVectors: number[];
    semanticNeighbors: string[];
    compressionRatio: number;
  };
}
```

### 6. Playtest Session Schema

```typescript
interface PlaytestSession {
  // Identity
  id: string;
  timestamp: string;                   // ISO 8601
  
  // Participants
  participants: {
    users: UserProfile[];
    agents: AgentPersona[];
    groupDynamic: "individual" | "competitive" | "collaborative" | "intergenerational";
  };
  
  // Session Configuration
  configuration: {
    gameMode: string;
    constraints: string[];
    culturalTheme: string;
    language: ISO6391;
    difficulty: string;
  };
  
  // Gameplay Data
  gameplay: {
    rounds: Round[];
    totalTokens: number;
    tokensSaved: number;
    idiomsGenerated: string[];
    duration: number;                  // seconds
  };
  
  // Outcomes
  outcomes: {
    winner: string | null;
    participation: Record<string, number>;  // Agent/User ID -> score
    achievements: string[];
  };
  
  // Feedback (NEW from Round 11-20)
  feedback: {
    // Quantitative
    enjoyment: 1 | 2 | 3 | 4 | 5;
    difficulty: 1 | 2 | 3 | 4 | 5;
    educational: 1 | 2 | 3 | 4 | 5;
    culturalSensitivity: 1 | 2 | 3 | 4 | 5;
    
    // Qualitative
    positiveAspects: string[];
    improvements: string[];
    culturalIssues: string[];
    technicalIssues: string[];
    
    // Engineer-specific (Rounds 15-18)
    technicalAccuracy: 1 | 2 | 3 | 4 | 5;
    documentationQuality: 1 | 2 | 3 | 4 | 5;
    apiUsability: 1 | 2 | 3 | 4 | 5;
    
    // Lifelong learner-specific (Rounds 16-18)
    conceptualClarity: 1 | 2 | 3 | 4 | 5;
    integrationWithExisting: string;   // How it connects to what they know
    
    // Parent-child-specific (Rounds 19-20)
    intergenerationalEngagement: 1 | 2 | 3 | 4 | 5;
    teachingMoments: string[];
    bondingMoments: string[];
  };
  
  // ML Training Metadata
  mlMetadata: {
    sessionEmbedding: number[];
    culturalVectors: Record<ISO3166Alpha2, number[]>;
    interactionPatterns: InteractionPattern[];
    learningSignals: LearningSignal[];
  };
}

interface Round {
  id: string;
  target: string;
  category: string;
  messages: Message[];
  status: "waiting" | "acting" | "guessing" | "judging" | "complete";
  winner: string | null;
  tokenCost: number;
  timeElapsed: number;
  hints: string[];
  hintsUsed: number;
}

interface Message {
  id: string;
  agentId: string;
  content: string;
  type: "description" | "guess" | "judgment" | "idiom-generated" | "hint" | "celebration";
  tokens: number;
  constraintApplied: string | null;
  timestamp: number;
  reactions: { emoji: string; count: number }[];
}
```

---

## Tile-Based Programming Integration Schemas

### 7. Tile Block Schema

```typescript
interface TileBlock {
  // Identity
  id: string;
  type: TileType;
  category: TileCategory;
  
  // Visual Representation
  visual: {
    icon: string;
    label: string;
    color: string;
    shape: "rectangle" | "hexagon" | "rounded" | "custom";
    size: "small" | "medium" | "large";
  };
  
  // Behavior
  behavior: {
    inputs: TilePort[];
    outputs: TilePort[];
    parameters: TileParameter[];
    executable: boolean;
    atomic: boolean;                   // Cannot be broken down further
  };
  
  // Cultural Adaptation
  cultural: {
    iconVariants: Record<ISO3166Alpha2, string>;
    labelVariants: Record<ISO6391, string>;
    culturalExamples: Record<ISO3166Alpha2, string>;
  };
  
  // Platform Origins (from research)
  origins: {
    platform: string;                  // Scratch, ScratchJr, Hopscotch, etc.
    adaptedFrom: string;
    originalBlockId: string;
  };
}

type TileType = 
  | "event"            // When [condition] happens
  | "action"           // Do something
  | "control"          // If/then, loops
  | "operator"         // Math, logic
  | "variable"         // Set/get variables
  | "agent"            // LLN-specific: Agent commands
  | "constraint"       // LLN-specific: Apply constraint
  | "idiom"            // LLN-specific: Use idiom
  | "sensing"          // Input sensing (OctoStudio integration)
  | "output";          // Hardware output (Micro:bit integration)

type TileCategory = 
  | "motion"
  | "looks"
  | "sound"
  | "events"
  | "control"
  | "sensing"
  | "operators"
  | "variables"
  | "agents"           // LLN-specific
  | "constraints"      // LLN-specific
  | "idioms"           // LLN-specific
  | "hardware";        // Physical computing

interface TilePort {
  id: string;
  type: "input" | "output";
  dataType: "any" | "string" | "number" | "boolean" | "agent" | "idiom";
  required: boolean;
  multiple: boolean;                   // Can accept multiple connections
}

interface TileParameter {
  id: string;
  name: string;
  type: "string" | "number" | "boolean" | "dropdown" | "agent" | "idiom" | "constraint";
  defaultValue: any;
  constraints: {
    min?: number;
    max?: number;
    options?: string[];
    regex?: string;
  };
}
```

### 8. Tile Program Schema

```typescript
interface TileProgram {
  // Identity
  id: string;
  name: string;
  description: string;
  
  // Structure
  structure: {
    blocks: TileBlock[];
    connections: {
      from: { blockId: string; portId: string };
      to: { blockId: string; portId: string };
    }[];
    layout: {
      blockId: string;
      x: number;
      y: number;
    }[];
  };
  
  // Execution
  execution: {
    entryPoint: string;                // Starting block ID
    variables: Record<string, any>;
    agents: string[];                  // Agent IDs involved
    constraints: string[];             // Active constraints
  };
  
  // Sharing & Publishing
  sharing: {
    author: string;
    visibility: "private" | "unlisted" | "public";
    remixOf: string | null;
    tags: string[];
    culturalTags: ISO3166Alpha2[];
    ageAppropriate: ("child" | "teen" | "adult" | "elder")[];
  };
  
  // Statistics
  stats: {
    views: number;
    runs: number;
    remixes: number;
    favorites: number;
    avgCompletionTime: number;
    successRate: number;
  };
}
```

---

## ML Training Schemas

### 9. Training Example Schema

```typescript
interface TrainingExample {
  id: string;
  timestamp: string;
  
  // Source
  source: {
    session: string;                   // PlaytestSession ID
    round: string;                     // Round ID
    message: string;                   // Message ID
  };
  
  // Context
  context: {
    agent: AgentPersona;
    gameMode: GameMode;
    constraints: Constraint[];
    userProfile: UserProfile;
    culturalContext: ISO3166Alpha2;
    previousMessages: Message[];
  };
  
  // Input/Output
  data: {
    input: {
      prompt: string;
      systemPrompt: string;
      temperature: number;
    };
    output: {
      content: string;
      tokens: number;
      latency: number;
    };
    expected?: string;                 // For supervised learning
  };
  
  // Quality Signals
  quality: {
    userFeedback: number;              // 1-5
    outcomeSuccess: boolean;
    culturalAppropriateness: number;   // 1-5
    technicalAccuracy: number;         // 1-5
    creativeScore: number;             // 0-1
  };
  
  // Features for ML
  features: {
    culturalEmbedding: number[];
    constraintVector: number[];
    gameModeVector: number[];
    agentEmbedding: number[];
    userProfileVector: number[];
  };
}
```

### 10. ML Model Metadata Schema

```typescript
interface MLModelMetadata {
  id: string;
  version: string;
  
  // Model Info
  model: {
    architecture: string;
    baseModel: string;
    fineTunedFrom: string | null;
    parameters: number;
    contextWindow: number;
  };
  
  // Training Data
  training: {
    examples: number;
    sessions: number;
    cultures: ISO3166Alpha2[];
    ageGroups: string[];
    dateRange: { start: string; end: string };
    dataSources: string[];
  };
  
  // Evaluation
  evaluation: {
    metrics: {
      accuracy: number;
      culturalSensitivity: number;
      tokenEfficiency: number;
      userSatisfaction: number;
    };
    testSetSize: number;
    evaluationDate: string;
  };
  
  // Deployment
  deployment: {
    status: "development" | "staging" | "production";
    deployedAt: string | null;
    servingEndpoint: string | null;
    versionHistory: string[];
  };
}
```

---

## Spreadsheet Dynamics for ML Growth

### 11. ML Growth Tracking Schema

```typescript
interface MLGrowthMetrics {
  timestamp: string;
  
  // Aggregate Metrics
  aggregate: {
    totalSessions: number;
    totalUsers: number;
    totalTokens: number;
    tokensSaved: number;
    idiomsCreated: number;
    avgSessionDuration: number;
    avgUserSatisfaction: number;
  };
  
  // Per-Culture Metrics
  culturalMetrics: Record<ISO3166Alpha2, {
    users: number;
    sessions: number;
    satisfaction: number;
    culturalFitScore: number;
    preferredGameModes: string[];
    preferredConstraints: string[];
    idiomCreationRate: number;
  }>;
  
  // Per-Role Metrics
  roleMetrics: Record<UserRole, {
    users: number;
    avgLevel: number;
    avgXP: number;
    completionRate: number;
    preferredFeatures: string[];
  }>;
  
  // Improvement Signals
  improvementSignals: {
    featureRequests: { feature: string; count: number }[];
    bugReports: { issue: string; count: number }[];
    culturalIssues: { issue: string; cultures: ISO3166Alpha2[] }[];
    successPatterns: { pattern: string; effectiveness: number }[];
  };
  
  // A/B Test Results
  abTests: {
    testId: string;
    variant: string;
    metric: string;
    value: number;
    confidence: number;
  }[];
}
```

---

## Next Generation System Architecture

### 12. System Architecture Schema

```typescript
interface SystemArchitecture {
  version: string;
  
  // Components
  components: {
    frontend: {
      framework: "Next.js 16";
      uiLibrary: "shadcn/ui";
      animationLibrary: "Framer Motion";
      tileEditor: {
        type: "block-based";
        dragDrop: boolean;
        snapToGrid: boolean;
        zoomLevels: number[];
        exportFormats: string[];
      };
    };
    
    backend: {
      framework: "Next.js API Routes";
      database: "Prisma ORM + SQLite/PostgreSQL";
      caching: "Redis";
      queue: "Bull/BullMQ";
    };
    
    ai: {
      primarySDK: "z-ai-web-dev-sdk";
      models: {
        chat: string[];
        image: string[];
        embedding: string[];
      };
      fallbackStrategies: string[];
    };
    
    realtime: {
      websocket: "Socket.io";
      presence: boolean;
      collaborativeEditing: boolean;
    };
  };
  
  // Data Flow
  dataFlow: {
    userAction: "UI Event" -> "Tile/Constraint Processing" -> "Agent Selection" -> "AI Generation" -> "Response Rendering";
    idioms: "Gameplay" -> "Pattern Detection" -> "Idiom Creation" -> "SMPbot Locking" -> "Cross-Cultural Translation";
    ml: "Session Data" -> "Feature Extraction" -> "Model Training" -> "Evaluation" -> "Deployment";
  };
  
  // Scalability
  scalability: {
    horizontal: boolean;
    regions: string[];
    cdnEnabled: boolean;
    rateLimiting: {
      global: number;
      perUser: number;
    };
  };
  
  // Security
  security: {
    authentication: "NextAuth.js v4";
    authorization: "RBAC";
    encryption: "AES-256";
    auditLogging: boolean;
    piiDetection: boolean;
  };
}
```

---

## Future Research Directions

### 13. Research Roadmap Schema

```typescript
interface ResearchRoadmap {
  version: string;
  
  shortTerm: {
    timeframe: "Q1-Q2 2025";
    projects: [
      {
        name: "Cultural Persona Optimization";
        description: "Train culture-specific agent behaviors";
        metrics: ["cultural_fit_score", "user_satisfaction"];
        datasets: ["playtest_sessions", "cultural_feedback"];
      },
      {
        name: "Idiom Cross-Translation";
        description: "Enable automatic idiom translation across languages";
        metrics: ["translation_accuracy", "cultural_preservation"];
        datasets: ["multilingual_idioms", "translation_feedback"];
      },
      {
        name: "Intergenerational Learning Patterns";
        description: "Study parent-child-grandparent learning dynamics";
        metrics: ["bonding_score", "teaching_moments", "knowledge_transfer"];
        datasets: ["family_sessions", "intergenerational_feedback"];
      },
    ];
  };
  
  mediumTerm: {
    timeframe: "Q3-Q4 2025";
    projects: [
      {
        name: "Hardware Abstraction Layer";
        description: "Visualize LLN as chip architecture";
        metrics: ["analogy_accuracy", "engineer_satisfaction"];
        datasets: ["engineer_sessions", "hardware_analogy_feedback"];
      },
      {
        name: "Tile-Based Constraint Editor";
        description: "Visual constraint builder for all ages";
        metrics: ["creation_rate", "constraint_success", "age_appropriateness"];
        datasets: ["tile_sessions", "constraint_creations"];
      },
      {
        name: "OctoStudio Sensor Integration";
        description: "Use phone sensors as constraint triggers";
        metrics: ["sensor_usage", "creative_applications"];
        datasets: ["sensor_sessions", "mobile_usage"];
      },
    ];
  };
  
  longTerm: {
    timeframe: "2026+";
    projects: [
      {
        name: "Autonomous Agent Network";
        description: "Self-improving agent communities";
        metrics: ["improvement_rate", "novel_idioms", "autonomous_games"];
        datasets: ["agent_interactions", "evolution_metrics"];
      },
      {
        name: "Cross-Platform Idiom Protocol";
        description: "Universal shorthand for AI communication";
        metrics: ["adoption_rate", "efficiency_gain", "platform_compatibility"];
        datasets: ["platform_integrations", "protocol_usage"];
      },
    ];
  };
}
```

---

## Conclusion

This schema documentation provides the foundation for:

1. **Cultural Responsiveness** - Ensuring the system adapts to diverse cultural contexts
2. **Technical Accuracy** - Meeting professional standards for engineers
3. **Intergenerational Learning** - Supporting family and multi-age interactions
4. **ML Growth** - Enabling continuous improvement through data collection
5. **Platform Integration** - Synthesizing best practices from 15+ tile-based platforms

The schemas are designed to be:
- **Extensible** - New fields can be added without breaking changes
- **Culturally Aware** - ISO standards for internationalization
- **ML-Ready** - Feature vectors and embeddings for training
- **Backward Compatible** - Version controlled for evolution

---

Document Version: 1.0.0
Last Updated: Generated from 30 rounds of playtesting
Contributors: Cultural personas, Engineers, Lifelong learners, Parent-child pairs, Research synthesis
