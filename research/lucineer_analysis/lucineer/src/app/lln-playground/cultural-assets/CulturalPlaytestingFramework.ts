# ============================================================================
// LLN PLAYGROUND - CULTURAL PLAYTESTING FRAMEWORK
// Rounds 11-30: Diverse Cultural Perspectives & Engineering Architecture
// ============================================================================

import { motion } from "framer-motion";

// ============================================================================
// CULTURAL PERSONAS - Asian & African Traditions
// ============================================================================

export const CULTURAL_PERSONAS = {
  // East Asian Perspectives
  japanese_elder: {
    id: "jp_elder",
    name: "Kenji-san",
    emoji: "🎌",
    age: 72,
    background: "Retired mathematics teacher, lifelong shogi player",
    culturalContext: "Values precision, patience, and mastery through repetition",
    learningStyle: "Structured, methodical, appreciates clear progressions",
    techExperience: "Basic - uses smartphone for calls and photos",
    interests: ["Origami logic", "Haiku constraints", "Calligraphy patterns"],
    suggestions: ["Add zen garden visual theme", "Include calligraphic animations"],
  },
  
  chinese_parent_child: {
    id: "cn_parent_child",
    name: "Mei & Little Wei",
    emoji: "👨‍👧",
    age: "38 & 7",
    background: "Software engineer mother teaching son about AI",
    culturalContext: "Values education, family bonding, future preparation",
    learningStyle: "Collaborative, goal-oriented, celebrates achievements",
    techExperience: "Mother: Expert | Child: Growing up with tech",
    interests: ["Tangram puzzles", "Dragon stories", "Abacus math"],
    suggestions: ["Add Chinese language option", "Include tangram-based constraint games"],
  },
  
  korean_student: {
    id: "kr_student",
    name: "Min-jun",
    emoji: "🇰🇷",
    age: 16,
    background: "High school student, competitive gamer, esports aspirant",
    culturalContext: "Values competition, speed, optimization, ranking systems",
    learningStyle: "Fast-paced, competitive, seeks efficiency",
    techExperience: "Advanced - multiple platforms daily",
    interests: ["Starcraft strategy", "K-pop rhythm games", "Speed running"],
    suggestions: ["Add competitive leaderboards", "Include speed-based challenges"],
  },
  
  indian_family: {
    id: "in_family",
    name: "Sharma Family",
    emoji: "🇮🇳",
    age: "Multiple generations",
    background: "Multi-generational household, grandparents curious about AI",
    culturalContext: "Values family unity, oral traditions, storytelling",
    learningStyle: "Narrative-based, collaborative, celebration of festivals",
    techExperience: "Mixed - children teach grandparents",
    interests: ["Bollywood stories", "Cricket statistics", "Festival patterns"],
    suggestions: ["Add story-building from festivals", "Include multilingual support"],
  },
  
  // African Perspectives
  nigerian_educator: {
    id: "ng_educator",
    name: "Adeola",
    emoji: "🇳🇬",
    age: 45,
    background: "University computer science lecturer, Afrobeat enthusiast",
    culturalContext: "Values community, oral tradition, call-and-response learning",
    learningStyle: "Discussion-based, practical applications, mentorship",
    techExperience: "Expert - teaches programming",
    interests: ["Afrobeat rhythms", "Nollywood storytelling", "Adinkra symbols"],
    suggestions: ["Add rhythm-based constraints", "Include African storytelling modes"],
  },
  
  kenyan_innovator: {
    id: "ke_innovator",
    name: "Wanjiku",
    emoji: "🇰🇪",
    age: 28,
    background: "Tech startup founder, mobile payments expert (M-Pesa generation)",
    culturalContext: "Values innovation, mobile-first solutions, community impact",
    learningStyle: "Problem-solving, entrepreneurial, practical outcomes",
    techExperience: "Expert - mobile-first mindset",
    interests: ["Safari patterns", "Mobile-first UX", "Swahili proverbs"],
    suggestions: ["Optimize for mobile", "Add Swahili language", "Include impact metrics"],
  },
  
  ethiopian_historian: {
    id: "et_historian",
    name: "Tadesse",
    emoji: "🇪🇹",
    age: 65,
    background: "Retired archaeologist, fascinated by how AI preserves culture",
    culturalContext: "Values history, ancient scripts (Ge'ez), preservation",
    learningStyle: "Historical connections, pattern recognition, storytelling",
    techExperience: "Basic - curious about digital preservation",
    interests: ["Ancient scripts", "Coffee ceremony patterns", "Historical connections"],
    suggestions: ["Add historical AI timeline", "Include script visualization tools"],
  },
  
  south_african_youth: {
    id: "za_youth",
    name: "Thabo",
    emoji: "🇿🇦",
    age: 19,
    background: "University student, Ubuntu philosophy practitioner",
    culturalContext: "Values community (Ubuntu), multilingual (11 official languages)",
    learningStyle: "Collaborative, community-focused, multilingual",
    techExperience: "Intermediate - uses for studies",
    interests: ["Ubuntu philosophy", "Safari wildlife", "Rainbow nation diversity"],
    suggestions: ["Add Ubuntu mode (collaborative learning)", "Multilingual support"],
  },
  
  ghanaian_diaspora: {
    id: "gh_diaspora",
    name: "Kwame Jr.",
    emoji: "🇬🇭",
    age: 32,
    background: "US-based engineer visiting family, bridging two worlds",
    culturalContext: "Values both heritage and innovation, Kente cloth patterns",
    learningStyle: "Bridge-builder, comparative, practical",
    techExperience: "Expert - Silicon Valley trained",
    interests: ["Kente pattern logic", "Diaspora connections", "Ananse stories"],
    suggestions: ["Add pattern recognition from textiles", "Include Ananse storytelling mode"],
  },
  
  senegalese_artist: {
    id: "sn_artist",
    name: "Fatou",
    emoji: "🇸🇳",
    age: 35,
    background: "Digital artist blending traditional patterns with AI",
    culturalContext: "Values creative expression, Teranga (hospitality)",
    learningStyle: "Visual, creative, experimental",
    techExperience: "Advanced - digital artist",
    interests: ["Wolof patterns", "Glass painting logic", "Sabar rhythms"],
    suggestions: ["Add visual pattern creation mode", "Include rhythm-based constraints"],
  },
};

// ============================================================================
// ENGINEER PERSONAS - Hardware & Software Professionals
// ============================================================================

export const ENGINEER_PERSONAS = {
  silicon_architect: {
    id: "hw_architect",
    name: "Dr. Chen Wei",
    emoji: "🔬",
    role: "Silicon Architecture Lead",
    company: "Major Chip Manufacturer",
    expertise: ["RTL design", "Physical design", "Timing closure", "Power analysis"],
    testingFocus: ["Accuracy of hardware analogies", "Technical correctness", "Flow efficiency"],
    feedback: {
      strengths: ["Token economics model is innovative", "Cell-based approach mirrors HDL concepts"],
      improvements: [
        "Add timing diagram visualizations",
        "Include gate-level abstraction modes",
        "Show actual token flow like signal propagation",
        "Add constraint modes that mirror synthesis constraints",
      ],
    },
  },
  
  rtl_designer: {
    id: "rtl_designer",
    name: "Priya Sharma",
    emoji: "⚡",
    role: "RTL Design Engineer",
    company: "Semiconductor Startup",
    expertise: ["Verilog/SystemVerilog", "State machines", "Protocol design"],
    testingFocus: ["Logic flow", "State transitions", "Debug capabilities"],
    feedback: {
      strengths: ["Agent state management is elegant", "Constraint system mirrors design rules"],
      improvements: [
        "Add waveform-style message visualization",
        "Include assertion-based testing modes",
        "Show agent interactions as state diagrams",
        "Add coverage metrics like in verification",
      ],
    },
  },
  
  software_architect: {
    id: "sw_architect",
    name: "Marcus Johnson",
    emoji: "🏗️",
    role: "Principal Software Architect",
    company: "Cloud Infrastructure Company",
    expertise: ["Distributed systems", "API design", "Performance optimization"],
    testingFocus: ["API ergonomics", "Error handling", "Documentation clarity"],
    feedback: {
      strengths: ["API design is RESTful and intuitive", "Error messages are helpful"],
      improvements: [
        "Add request/response logging with timestamps",
        "Include rate limiting visualization",
        "Show token usage as resource graphs",
        "Add circuit breaker patterns for agent failures",
      ],
    },
  },
  
  ml_engineer: {
    id: "ml_engineer",
    name: "Aisha Okonkwo",
    emoji: "🧠",
    role: "ML Infrastructure Engineer",
    company: "AI Research Lab",
    expertise: ["Model deployment", "Prompt engineering", "Token optimization"],
    testingFocus: ["Token efficiency", "Prompt quality", "Model behavior"],
    feedback: {
      strengths: ["Idiom generation is innovative", "Token tracking is accurate"],
      improvements: [
        "Add prompt template editor",
        "Include A/B testing framework for prompts",
        "Show attention visualization when possible",
        "Add temperature/top_p sliders for agent responses",
      ],
    },
  },
  
  devops_engineer: {
    id: "devops",
    name: "Yuki Tanaka",
    emoji: "🔧",
    role: "DevOps/SRE Lead",
    company: "Financial Services",
    expertise: ["CI/CD", "Monitoring", "Incident response"],
    testingFocus: ["Reliability", "Observability", "Deployment ease"],
    feedback: {
      strengths: ["Real-time metrics are clear", "Error handling is robust"],
      improvements: [
        "Add Prometheus metrics export",
        "Include health check endpoints",
        "Show circuit breaker status",
        "Add deployment runbook documentation",
      ],
    },
  },
  
  security_engineer: {
    id: "security",
    name: "Omar Hassan",
    emoji: "🔐",
    role: "Security Engineer",
    company: "Cybersecurity Firm",
    expertise: ["Penetration testing", "Secure coding", "Compliance"],
    testingFocus: ["Input validation", "Access control", "Data privacy"],
    feedback: {
      strengths: ["Input sanitization is good", "No obvious injection vectors"],
      improvements: [
        "Add rate limiting per user",
        "Include audit logging for all actions",
        "Show security score per session",
        "Add PII detection in generated content",
      ],
    },
  },
};

// ============================================================================
// LIFELONG LEARNER PERSONAS - Retired Professionals
// ============================================================================

export const LIFELONG_LEARNER_PERSONAS = {
  retired_physicist: {
    id: "ret_physicist",
    name: "Dr. Eleanor Wright",
    emoji: "⚛️",
    age: 78,
    background: "Retired quantum physicist, wants to understand AI through physics lens",
    conceptualMapping: {
      tokens: "Like quanta of information - discrete packets",
      agents: "Like particles with specific properties and behaviors",
      constraints: "Like physical laws governing interactions",
      idioms: "Like emergent phenomena from complex systems",
    },
    questions: [
      "How does token efficiency relate to entropy?",
      "Can agents form quantum-like superposition states?",
      "Is there a conservation law for information in the system?",
    ],
    suggestions: [
      "Add physics analogy mode",
      "Include entropy calculations for token usage",
      "Show wave/particle duality in message visualization",
    ],
  },
  
  retired_biologist: {
    id: "ret_biologist",
    name: "Dr. James Okello",
    emoji: "🧬",
    age: 74,
    background: "Retired evolutionary biologist, sees AI as new form of life",
    conceptualMapping: {
      agents: "Like species in an ecosystem",
      games: "Like evolutionary selection pressures",
      idioms: "Like genetic mutations that become adaptations",
      constraints: "Like environmental pressures shaping evolution",
    },
    questions: [
      "Can idioms 'reproduce' and evolve?",
      "Do agents compete for 'resources' (tokens)?",
      "Is there a fitness function for successful communication?",
    ],
    suggestions: [
      "Add evolutionary visualization",
      "Include 'mutation' modes for idioms",
      "Show agent 'fitness' scores",
    ],
  },
  
  retired_economist: {
    id: "ret_economist",
    name: "Prof. Wang Xiu",
    emoji: "📈",
    age: 81,
    background: "Retired development economist, interested in token economics",
    conceptualMapping: {
      tokens: "Like currency with scarcity and value",
      idiomSavings: "Like compound interest and capital accumulation",
      games: "Like market transactions and negotiations",
      agents: "Like economic actors with preferences",
    },
    questions: [
      "What determines the 'exchange rate' between different token types?",
      "Can agents form 'cartels' or 'cooperatives'?",
      "Is there inflation in the idiom 'economy'?",
    ],
    suggestions: [
      "Add economic dashboard",
      "Include token inflation/deflation metrics",
      "Show agent 'wealth' distribution",
    ],
  },
  
  retired_musician: {
    id: "ret_musician",
    name: "Maria Santos",
    emoji: "🎵",
    age: 76,
    background: "Retired orchestra conductor, sees AI as new instrument",
    conceptualMapping: {
      agents: "Like musicians in an orchestra",
      constraints: "Like tempo, key, and time signatures",
      games: "Like musical improvisations",
      idioms: "Like musical motifs and themes",
    },
    questions: [
      "Can agents 'harmonize' like musical chords?",
      "Is there rhythm in the token flow?",
      "Can we 'compose' agent interactions?",
    ],
    suggestions: [
      "Add musical visualization mode",
      "Include rhythm-based constraint games",
      "Show agent 'harmony' scores",
    ],
  },
  
  retired_historian: {
    id: "ret_historian",
    name: "Dr. Ahmed Hassan",
    emoji: "📜",
    age: 79,
    background: "Retired historian of technology, sees AI as latest chapter",
    conceptualMapping: {
      idioms: "Like how writing compressed oral traditions",
      games: "Like how sports teach social skills",
      agents: "Like how tools extended human capabilities",
      constraints: "Like how rules shape civilizations",
    },
    questions: [
      "How will future historians view this technology?",
      "What patterns from history repeat here?",
      "How do we preserve 'digital heritage' (idioms)?",
    ],
    suggestions: [
      "Add historical timeline mode",
      "Include pattern recognition from history",
      "Show idiom 'archaeological' layers",
    ],
  },
};

// ============================================================================
// PARENT-CHILD PAIR PERSONAS
// ============================================================================

export const PARENT_CHILD_PAIRS = {
  tech_parent_tech_child: {
    id: "tech_tech",
    parentName: "David",
    childName: "Emma",
    parentAge: 38,
    childAge: 10,
    parentBackground: "Software Engineer at Google",
    childBackground: "Growing up with code, loves Scratch",
    interactionStyle: "Parent guides, child explores",
    challenges: [
      "Parent sometimes over-explains",
      "Child wants more freedom",
      "Balancing education with fun",
    ],
    discoveries: [
      "Constraint games become shared language",
      "Idioms created together become inside jokes",
      "Competition motivates both",
    ],
    feedback: {
      improvements: [
        "Add 'guide mode' for parents",
        "Include difficulty auto-adjustment",
        "Show progress separately for parent vs child",
        "Add collaborative vs competitive mode toggle",
      ],
    },
  },
  
  non_tech_parent_curious_child: {
    id: "non_tech_curious",
    parentName: "Jennifer",
    childName: "Marcus",
    parentAge: 42,
    childAge: 12,
    parentBackground: "Elementary school teacher",
    childBackground: "Curious about technology, asks many questions",
    interactionStyle: "Child teaches parent, both learn",
    challenges: [
      "Parent feels behind",
      "Child's questions exceed parent's knowledge",
      "Need for accessible explanations",
    ],
    discoveries: [
      "Learning together builds bond",
      "Child takes pride in teaching",
      "System explanations help parent",
    ],
    feedback: {
      improvements: [
        "Add 'learn together' mode",
        "Include simple explanations for each concept",
        "Add hints that don't give away answers",
        "Include parent-specific tutorials",
      ],
    },
  },
  
  grandparent_grandchild: {
    id: "grandparent_grandchild",
    parentName: "Grandma Rosa",
    childName: "Sofia",
    parentAge: 68,
    childAge: 8,
    parentBackground: "Retired nurse, basic tech skills",
    childBackground: "Digital native, shows grandma tech",
    interactionStyle: "Grandchild guides, grandparent asks questions",
    challenges: [
      "Large tech knowledge gap",
      "Different speeds of learning",
      "Need patience on both sides",
    ],
    discoveries: [
      "Games bridge generation gap",
      "Grandparent's life wisdom adds context",
      "Child develops teaching skills",
    ],
    feedback: {
      improvements: [
        "Add larger text/UI option",
        "Include voice instructions",
        "Add slower pace option",
        "Include intergenerational achievement badges",
      ],
    },
  },
  
  immigrant_parent_american_child: {
    id: "immigrant_american",
    parentName: "Chen Wei",
    childName: "Alex",
    parentAge: 40,
    childAge: 11,
    parentBackground: "Engineer from China, strong math background",
    childBackground: "American-born, creative and artistic",
    interactionStyle: "Parent brings structure, child brings creativity",
    challenges: [
      "Different educational philosophies",
      "Language preferences differ",
      "Balancing structure and creativity",
    ],
    discoveries: [
      "Bilingual idiom generation",
      "Cultural exchange through games",
      "Parent's discipline + child's creativity = success",
    ],
    feedback: {
      improvements: [
        "Add bilingual mode",
        "Include cultural context options",
        "Add structure/creativity balance tools",
        "Include cultural celebration achievements",
      ],
    },
  },
};

// ============================================================================
// AGENT DISCUSSION FRAMEWORK
// ============================================================================

export interface AgentDiscussion {
  round: number;
  participants: string[];
  topic: string;
  observations: string[];
  suggestedImprovements: string[];
  crossCulturalInsights: string[];
  engineeringFeedback: string[];
  mlGrowthOpportunities: string[];
}

export const SAMPLE_DISCUSSIONS: AgentDiscussion[] = [
  {
    round: 11,
    participants: ["Kenji-san", "Dr. Chen Wei", "Adeola", "Marcus & Emma"],
    topic: "Cultural Accessibility & Technical Accuracy",
    observations: [
      "Japanese users prefer structured progression over open exploration",
      "Hardware engineers found analogies accurate but wanted more depth",
      "African educators emphasized community aspects missing in current design",
      "Parent-child pairs need better role-switching capabilities",
    ],
    suggestedImprovements: [
      "Add 'Sensei Mode' for structured learning paths",
      "Include hardware diagram visualizations",
      "Add Ubuntu Mode for collaborative learning",
      "Create parent/child role toggle in UI",
    ],
    crossCulturalInsights: [
      "Patience is valued in both Japanese and African traditions",
      "Storytelling bridges technical concepts across cultures",
      "Family learning differs significantly across regions",
    ],
    engineeringFeedback: [
      "Add state machine visualization for agent interactions",
      "Include timing diagrams for message flow",
      "Show token propagation like signal delay",
    ],
    mlGrowthOpportunities: [
      "Train culture-specific agent personas",
      "Learn optimal constraint combinations per culture",
      "Predict user frustration points from interaction patterns",
    ],
  },
  {
    round: 15,
    participants: ["Dr. Eleanor Wright", "Priya Sharma", "Fatou", "Chen Wei & Alex"],
    topic: "Conceptual Bridges & Professional Integration",
    observations: [
      "Retired physicists appreciate entropy-based explanations",
      "RTL designers found state diagrams helpful",
      "Artists want more visual feedback mechanisms",
      "Immigrant families benefit from bilingual idioms",
    ],
    suggestedImprovements: [
      "Add physics analogy toggle (entropy view, quantum view)",
      "Include Verilog-like syntax for advanced users",
      "Add visual pattern creation mode",
      "Create bilingual idiom library",
    ],
    crossCulturalInsights: [
      "Math and physics are universal languages",
      "Art and code both express patterns",
      "Bilingual users bridge cultural gaps automatically",
    ],
    engineeringFeedback: [
      "Add assertion mode for constraint validation",
      "Include coverage metrics for idiom usage",
      "Show synthesis-like optimization passes",
    ],
    mlGrowthOpportunities: [
      "Detect user's conceptual framework preference",
      "Auto-translate idioms across languages",
      "Learn optimal explanation styles per background",
    ],
  },
  {
    round: 20,
    participants: ["All cultural personas", "All engineer personas", "Parent-child pairs"],
    topic: "System Synthesis & Next Generation Planning",
    observations: [
      "Cultural diversity improves system robustness",
      "Professional accuracy and accessibility can coexist",
      "Intergenerational learning reveals UX gaps",
      "Constraint games have universal appeal with cultural variations",
    ],
    suggestedImprovements: [
      "Create culture-specific theme packs",
      "Add professional mode with technical accuracy",
      "Include family learning progress tracking",
      "Build adaptive constraint recommendation engine",
    ],
    crossCulturalInsights: [
      "Universal patterns emerge from cultural diversity",
      "Technology adoption patterns vary by generation",
      "Play is a universal learning mechanism",
    ],
    engineeringFeedback: [
      "Build plugin architecture for extensions",
      "Create API versioning strategy",
      "Include comprehensive test coverage metrics",
    ],
    mlGrowthOpportunities: [
      "Multi-armed bandit for constraint selection",
      "Cultural preference modeling",
      "Cross-cultural idiom translation",
      "Generational learning path optimization",
    ],
  },
];

// ============================================================================
// TILE-BASED PROGRAMMING RESEARCH SYNTHESIS
// ============================================================================

export const TILE_PROGRAMMING_PLATFORMS = {
  scratchjr: {
    name: "ScratchJr",
    targetAge: "5-7",
    keyFeatures: ["No text required", "Icon-based blocks", "Story-focused", "Tablet-first"],
    lessons: [
      "Eliminate text barriers for youngest users",
      "Use recognizable icons for actions",
      "Make every block have immediate visual feedback",
      "Support storytelling as primary motivation",
    ],
    integrationIdeas: [
      "Add icon-based constraint selection for kids",
      "Create emoji-based game mode",
      "Build story-building with visual tiles",
    ],
  },
  
  scratch: {
    name: "Scratch 3.0",
    targetAge: "8-16",
    keyFeatures: ["Largest community", "Infinite complexity", "Project sharing", "Extensions"],
    lessons: [
      "Community drives engagement",
      "Sharing motivates learning",
      "Extensions enable growth",
      "Project-based learning works",
    ],
    integrationIdeas: [
      "Add idiom sharing marketplace",
      "Create agent extension system",
      "Build project templates library",
    ],
  },
  
  swift_playgrounds: {
    name: "Swift Playgrounds",
    targetAge: "12+",
    keyFeatures: ["Apple ecosystem", "Block to text transition", "Real Swift code", "iPad optimized"],
    lessons: [
      "Gradual transition from blocks to text",
      "Real code motivates advanced learners",
      "Platform ecosystem matters",
    ],
    integrationIdeas: [
      "Add "show code" mode for agent definitions",
      "Create text-based constraint editor",
      "Build Swift/Python export for idioms",
    ],
  },
  
  kodable: {
    name: "Kodable",
    targetAge: "5-10",
    keyFeatures: ["Maze navigation", "If/then logic", "Fuzzy characters", "K-5 curriculum"],
    lessons: [
      "Characters create emotional connection",
      "Mazes provide clear goals",
      "Progressive difficulty keeps engagement",
    ],
    integrationIdeas: [
      "Add maze-style game mode",
      "Create lovable agent characters",
      "Build progressive constraint unlocking",
    ],
  },
  
  osmo_coding: {
    name: "Osmo Coding Awbie",
    targetAge: "5-12",
    keyFeatures: ["Physical blocks", "Camera recognition", "Tactile learning", "Tablet companion"],
    lessons: [
      "Physical manipulatives aid understanding",
      "Multi-sensory learning is powerful",
      "Blended digital/physical works",
    ],
    integrationIdeas: [
      "Add printable constraint cards",
      "Create physical idiom tokens concept",
      "Build camera-based constraint input",
    ],
  },
  
  tynker: {
    name: "Tynker",
    targetAge: "7-14",
    keyFeatures: ["Minecraft mods", "Roblox integration", "Structured lessons", "Game-based"],
    lessons: [
      "Connect to existing passions",
      "Modding drives engagement",
      "Structured lessons provide path",
    ],
    integrationIdeas: [
      "Add game modding concepts",
      "Create Minecraft-themed word categories",
      "Build achievement unlock system",
    ],
  },
  
  lightbot: {
    name: "LightBot",
    targetAge: "8+",
    keyFeatures: ["Minimal UI", "Pure logic", "Function concepts", "Loop concepts"],
    lessons: [
      "Minimalism focuses attention",
      "Functions and loops are key concepts",
      "Pure logic puzzles engage thinkers",
    ],
    integrationIdeas: [
      "Add "minimal mode" for advanced users",
      "Create function-based idioms",
      "Build loop optimization challenges",
    ],
  },
  
  hopscotch: {
    name: "Hopscotch",
    targetAge: "8-13",
    keyFeatures: ["Real games", "Publishing", "iPad native", "Creative freedom"],
    lessons: [
      "Publishing motivates quality",
      "Real games feel meaningful",
      "Creative freedom enables expression",
    ],
    integrationIdeas: [
      "Add idiom publishing",
      "Create game mode builder",
      "Build creative constraint studio",
    ],
  },
  
  code_org: {
    name: "Code.org",
    targetAge: "6-18",
    keyFeatures: ["Themed puzzles", "Disney/Minecraft", "Structured courses", "Hour of Code"],
    lessons: [
      "Themes drive initial engagement",
      "Short activities work (Hour of Code)",
      "Structured courses provide progression",
    ],
    integrationIdeas: [
      "Add themed word packs (Disney, Minecraft)",
      "Create "Hour of LLN" activities",
      "Build structured learning paths",
    ],
  },
  
  microbit: {
    name: "Micro:bit MakeCode",
    targetAge: "10+",
    keyFeatures: ["Hardware output", "LED matrix", "Sensors", "Physical computing"],
    lessons: [
      "Hardware output makes abstract concrete",
      "Sensors enable real-world interaction",
      "Physical computing is engaging",
    ],
    integrationIdeas: [
      "Add hardware visualization mode",
      "Create sensor-based constraint triggers",
      "Build LED matrix idiom display",
    ],
  },
  
  vexcode_vr: {
    name: "VEXcode VR",
    targetAge: "10+",
    keyFeatures: ["Virtual robot", "3D environment", "Competition ready", "No hardware needed"],
    lessons: [
      "Virtual robots eliminate hardware costs",
      "3D environments increase immersion",
      "Competition drives engagement",
    ],
    integrationIdeas: [
      "Add 3D agent visualization",
      "Create virtual competition modes",
      "Build robot-themed constraints",
    ],
  },
  
  turtle_academy: {
    name: "Turtle Academy",
    targetAge: "8+",
    keyFeatures: ["Logo language", "Geometry focus", "Drawing output", "Mathematical patterns"],
    lessons: [
      "Drawing output provides visual feedback",
      "Geometry teaches logical thinking",
      "Simple commands create complex patterns",
    ],
    integrationIdeas: [
      "Add turtle-style drawing mode",
      "Create geometric constraint games",
      "Build pattern-based idiom visualization",
    ],
  },
};

// ============================================================================
// SYNTHESIS: BEST OF ALL WORLDS
// ============================================================================

export const SYNTHESIZED_FEATURES = {
  // From ScratchJr: Icon-based for youngest
  iconMode: {
    source: "ScratchJr",
    feature: "Icon-based constraint selection",
    implementation: "Replace text constraints with emoji/icon tiles for kids mode",
  },
  
  // From Scratch: Community sharing
  sharing: {
    source: "Scratch",
    feature: "Idiom marketplace and sharing",
    implementation: "Let users publish, remix, and share successful idiom patterns",
  },
  
  // From Swift Playgrounds: Code view
  codeView: {
    source: "Swift Playgrounds",
    feature: "Show underlying code/structure",
    implementation: "Toggle to see agent definitions as code-like structure",
  },
  
  // From Kodable: Character-driven
  characters: {
    source: "Kodable",
    feature: "Lovable agent characters",
    implementation: "Design agent personas with distinct personalities and visual styles",
  },
  
  // From Osmo: Physical-digital bridge
  physical: {
    source: "Osmo Coding",
    feature: "Printable constraint cards",
    implementation: "Create PDF cards that can be scanned or entered physically",
  },
  
  // From Tynker: Passion connection
  passions: {
    source: "Tynker",
    feature: "Theme packs",
    implementation: "Minecraft, Roblox, Disney-themed word categories and constraints",
  },
  
  // From LightBot: Minimalist mode
  minimal: {
    source: "LightBot",
    feature: "Pure logic mode",
    implementation: "Strip UI to essentials for focused problem-solving",
  },
  
  // From Hopscotch: Publishing
  publishing: {
    source: "Hopscotch",
    feature: "Game mode publishing",
    implementation: "Let advanced users create and share custom game modes",
  },
  
  // From Code.org: Themed activities
  themed: {
    source: "Code.org",
    feature: "Themed puzzle sets",
    implementation: "Curated activity packs: "AI for Animals", "Holiday LLN", etc.",
  },
  
  // From Micro:bit: Hardware visualization
  hardware: {
    source: "Micro:bit",
    feature: "Hardware abstraction",
    implementation: "Show agents as hardware components, tokens as signals",
  },
  
  // From VEXcode VR: Virtual competition
  competition: {
    source: "VEXcode VR",
    feature: "Virtual agent competition",
    implementation: "3D arena where agent teams compete in real-time",
  },
  
  // From Turtle Academy: Geometric patterns
  geometry: {
    source: "Turtle Academy",
    feature: "Pattern visualization",
    implementation: "Draw idiom patterns as geometric art",
  },
};

// ============================================================================
// CROSS-CULTURAL ENGINEERING SCHEMAS
// ============================================================================

export const ENGINEERING_SCHEMAS = {
  // Schema for cultural adaptation
  culturalAdaptation: {
    id: "cultural_adaptation_v1",
    version: "1.0.0",
    description: "Schema for culturally-responsive UX adaptations",
    fields: {
      culture: "string (ISO 3166-1 alpha-2)",
      language: "string (ISO 639-1)",
      ageGroup: "enum (child, teen, adult, elder)",
      techLevel: "enum (basic, intermediate, advanced)",
      learningStyle: "enum (visual, auditory, kinesthetic, reading)",
      preferredPace: "enum (slow, medium, fast)",
      familyStructure: "enum (individual, parent-child, multi-gen, group)",
      valuesPriorities: "array of strings",
    },
  },
  
  // Schema for agent persona
  agentPersona: {
    id: "agent_persona_v1",
    version: "1.0.0",
    description: "Schema for defining agent behaviors and characteristics",
    fields: {
      id: "uuid",
      name: "string",
      emoji: "unicode",
      role: "enum (actor, guesser, judge, helper, challenger, observer)",
      personality: "string",
      communicationStyle: "enum (formal, casual, playful, technical)",
      culturalBackground: "string (ISO 3166-1)",
      ageAppropriate: "array of age groups",
      constraints: "array of constraint IDs",
      modelConfig: {
        model: "string",
        temperature: "number (0-1)",
        maxTokens: "number",
        systemPrompt: "string",
      },
    },
  },
  
  // Schema for game mode
  gameMode: {
    id: "game_mode_v1",
    version: "1.0.0",
    description: "Schema for defining game modes",
    fields: {
      id: "uuid",
      name: "string",
      description: "string",
      icon: "unicode or image URL",
      difficulty: "enum (beginner, intermediate, advanced, expert)",
      minPlayers: "number",
      maxPlayers: "number",
      avgTokens: "number",
      rules: "array of rule objects",
      winningCondition: "string",
      timeLimit: "number (seconds, optional)",
      culturalVariants: "array of culture-specific modifications",
    },
  },
  
  // Schema for idiom
  idiom: {
    id: "idiom_v1",
    version: "1.0.0",
    description: "Schema for learned communication shorthand",
    fields: {
      id: "uuid",
      shorthand: "string (emoji sequence or text)",
      meaning: "string",
      category: "string",
      originAgents: "array of agent IDs",
      originCultures: "array of culture codes",
      usageCount: "number",
      tokenSavings: "number",
      seed: "string (optional, for SMPbot locking)",
      lockedToSeed: "boolean",
      createdAt: "timestamp",
      lastUsed: "timestamp",
      effectiveness: "number (0-1)",
    },
  },
  
  // Schema for playtest session
  playtestSession: {
    id: "playtest_session_v1",
    version: "1.0.0",
    description: "Schema for recording playtest sessions",
    fields: {
      id: "uuid",
      timestamp: "ISO 8601",
      participantProfiles: "array of user profile IDs",
      gameMode: "game mode ID",
      constraints: "array of constraint IDs",
      rounds: "array of round objects",
      idiomsGenerated: "array of idiom IDs",
      totalTokens: "number",
      tokensSaved: "number",
      feedback: {
        enjoyment: "number (1-5)",
        difficulty: "number (1-5)",
        educational: "number (1-5)",
        improvements: "array of strings",
        culturalIssues: "array of strings",
      },
      culturalContext: {
        primaryCulture: "string",
        mixedCultural: "boolean",
        languageUsed: "string",
        familyParticipation: "boolean",
      },
    },
  },
};

export default {
  CULTURAL_PERSONAS,
  ENGINEER_PERSONAS,
  LIFELONG_LEARNER_PERSONAS,
  PARENT_CHILD_PAIRS,
  SAMPLE_DISCUSSIONS,
  TILE_PROGRAMMING_PLATFORMS,
  SYNTHESIZED_FEATURES,
  ENGINEERING_SCHEMAS,
};
