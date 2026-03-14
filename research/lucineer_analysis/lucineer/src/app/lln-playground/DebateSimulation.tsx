// ============================================================================
// LLN PLAYGROUND - DEBATE SIMULATION FRAMEWORK
// Structured Debates Across Multiple Formats for Deep Topic Exploration
// ============================================================================

import { motion } from "framer-motion";
import {
  Swords,
  Users,
  Globe,
  MessageCircle,
  Sparkles,
  BookOpen,
  Brain,
  Lightbulb,
  CheckCircle,
  XCircle,
  ArrowRight,
  Star,
  Trophy,
  Target,
  Clock,
  Languages,
  Scale,
  Mic,
  Vote,
  Zap,
  Shield,
  Award,
  TrendingUp,
  AlertTriangle,
  ThumbsUp,
  ThumbsDown,
  Handshake,
  Flame,
} from "lucide-react";

// ============================================================================
// DEBATE TYPES & INTERFACES
// ============================================================================

type DebateFormat =
  | "oxford" // Formal debate with propositions and opposition
  | "parliamentary" // Fast-paced competitive debate
  | "socratic-debate" // Question-based debate format
  | "devils-advocate" // Argue against your own position
  | "fishbowl" // Inner circle debates, outer circle observes
  | "town-hall" // Community-style open debate
  | "tournament" // Bracket-style competitive debates
  | "cross-examination"; // Lawyer-style questioning

type DebateSide = "proposition" | "opposition" | "neutral" | "judge";

interface Debater {
  id: string;
  name: string;
  avatar: string;
  country: string;
  language: string;
  expertise: string[];
  debateStyle: "aggressive" | "analytical" | "storytelling" | "socratic" | "collaborative";
  persuasiveness: number; // 0-1
  culturalPerspective: string;
  signatureArguments: string[];
}

interface DebateTopic {
  id: string;
  proposition: string;
  description: string;
  difficulty: "beginner" | "intermediate" | "advanced" | "expert";
  keyArguments: {
    proposition: string[];
    opposition: string[];
  };
  culturalConsiderations: Record<string, { propositionAngle: string; oppositionAngle: string }>;
  realWorldExamples: string[];
  tilesGenerated: string[];
}

interface DebateTurn {
  turnNumber: number;
  speaker: Debater;
  side: DebateSide;
  type: "opening" | "argument" | "rebuttal" | "question" | "answer" | "closing" | "judge-commentary";
  content: string;
  evidence?: string;
  targetTurn?: number;
  persuasivenessScore: number;
  culturalAdaptations: string[];
}

interface DebateSession {
  round: number;
  format: DebateFormat;
  topic: DebateTopic;
  proposition: Debater[];
  opposition: Debater[];
  judges: Debater[];
  turns: DebateTurn[];
  winner: "proposition" | "opposition" | "tie";
  insights: string[];
  tilesCreated: TileDefinition[];
  mlData: {
    argumentQuality: number[];
    persuasivenessByCulture: Record<string, number>;
    topicUnderstanding: Record<string, number>;
    engagementMetrics: Record<string, number>;
  };
}

interface TileDefinition {
  id: string;
  type: string;
  visual: string;
  behavior: string;
  connections: string[];
}

// ============================================================================
// DEBATE FORMAT DEFINITIONS
// ============================================================================

export const DEBATE_FORMATS: Record<DebateFormat, {
  name: string;
  icon: string;
  description: string;
  structure: string[];
  timeLimit: number; // minutes
  scoringCriteria: string[];
  bestFor: string[];
}> = {
  oxford: {
    name: "Oxford Debate",
    icon: "🎓",
    description: "Formal academic debate with structured arguments and rebuttals",
    structure: [
      "First Proposition - Opening Statement (6 min)",
      "First Opposition - Opening Statement (6 min)",
      "Second Proposition - Rebuttal & Extension (5 min)",
      "Second Opposition - Rebuttal & Extension (5 min)",
      "Third Proposition - Summary (4 min)",
      "Third Opposition - Summary (4 min)",
      "Audience Vote & Discussion"
    ],
    timeLimit: 60,
    scoringCriteria: ["Logic", "Evidence", "Delivery", "Rebuttal Quality", "Overall Persuasion"],
    bestFor: ["Complex topics", "Academic settings", "Policy debates"]
  },
  parliamentary: {
    name: "Parliamentary Debate",
    icon: "🏛️",
    description: "Fast-paced competitive format mimicking parliamentary proceedings",
    structure: [
      "Prime Minister - Case Presentation (7 min)",
      "Leader of Opposition - Response (7 min)",
      "Member of Government - Extension (7 min)",
      "Member of Opposition - Extension (7 min)",
      "Government Whip - Summary (5 min)",
      "Opposition Whip - Summary (5 min)"
    ],
    timeLimit: 45,
    scoringCriteria: ["Argument Development", "Clash", "Style", "Strategy", "Teamwork"],
    bestFor: ["Competitions", "Quick thinking", "Policy formation"]
  },
  "socratic-debate": {
    name: "Socratic Debate",
    icon: "🧙",
    description: "Question-driven debate where participants must defend positions through inquiry",
    structure: [
      "Opening Question from Moderator",
      "Proposition - Initial Position (5 min)",
      "Opposition - Socratic Questions (5 min)",
      "Proposition - Responses & Defense (5 min)",
      "Opposition - Alternative Position (5 min)",
      "Proposition - Socratic Questions (5 min)",
      "Opposition - Responses (5 min)",
      "Synthesis Round (10 min)"
    ],
    timeLimit: 50,
    scoringCriteria: ["Question Quality", "Defense Strength", "Logical Consistency", "Openness", "Synthesis"],
    bestFor: ["Philosophical topics", "Deep exploration", "Critical thinking"]
  },
  "devils-advocate": {
    name: "Devil's Advocate",
    icon: "😈",
    description: "Participants argue against their own beliefs to strengthen understanding",
    structure: [
      "Initial Position Statement - True Beliefs (3 min each)",
      "Assign Opposite Position",
      "Argument for Opposite Position (5 min each)",
      "Rebuttal of Your Own Arguments (4 min each)",
      "Synthesis - What Did You Learn? (5 min each)",
      "Final Position - Updated View (2 min each)"
    ],
    timeLimit: 40,
    scoringCriteria: ["Argument Quality for Opposite", "Self-Rebuttal Depth", "Synthesis Quality", "Growth Demonstrated"],
    bestFor: ["Breaking echo chambers", "Understanding nuance", "Personal growth"]
  },
  fishbowl: {
    name: "Fishbowl Debate",
    icon: "🐟",
    description: "Inner circle debates while outer circle observes and rotates in",
    structure: [
      "Inner Circle: 3 Proposition vs 3 Opposition",
      "Opening Arguments (3 min each)",
      "Free Debate (15 min)",
      "Outer Circle: Observations (5 min)",
      "Rotate: 2 Inner Members Out, 2 Outer In",
      "Continue Debate (10 min)",
      "Final Outer Circle Insights (5 min)",
      "Inner Circle Synthesis (5 min)"
    ],
    timeLimit: 55,
    scoringCriteria: ["Participation Quality", "Observation Insight", "Adaptation", "Collaborative Building"],
    bestFor: ["Group learning", "Multiple perspectives", "Training debaters"]
  },
  "town-hall": {
    name: "Town Hall Debate",
    icon: "🏛️",
    description: "Community-style debate with audience participation and voting",
    structure: [
      "Moderator Introduction (2 min)",
      "Proposition Opening (5 min)",
      "Opposition Opening (5 min)",
      "Audience Questions - Round 1 (10 min)",
      "Rebuttal Round (5 min each)",
      "Audience Questions - Round 2 (10 min)",
      "Closing Statements (3 min each)",
      "Community Vote"
    ],
    timeLimit: 50,
    scoringCriteria: ["Accessibility", "Audience Engagement", "Practical Solutions", "Community Impact"],
    bestFor: ["Public issues", "Community decisions", "Democratic participation"]
  },
  tournament: {
    name: "Tournament Debate",
    icon: "🏆",
    description: "Bracket-style competition with elimination rounds",
    structure: [
      "Round 1: Opening Arguments (4 min each)",
      "Round 1: Rebuttals (3 min each)",
      "Judge Deliberation & Scoring",
      "Winner Advances to Next Round",
      "Repeat until Final",
      "Championship Round: Extended Format",
      "Awards & Analysis"
    ],
    timeLimit: 90,
    scoringCriteria: ["Win/Loss Record", "Argument Strength", "Improvement", "Sportsmanship"],
    bestFor: ["Competitions", "Skill development", "High stakes topics"]
  },
  "cross-examination": {
    name: "Cross-Examination Debate",
    icon: "⚖️",
    description: "Lawyer-style questioning with evidence and witness handling",
    structure: [
      "Opening Statement - Proposition (5 min)",
      "Opening Statement - Opposition (5 min)",
      "Direct Examination - Prop Witnesses (8 min)",
      "Cross-Examination by Opposition (6 min)",
      "Direct Examination - Opp Witnesses (8 min)",
      "Cross-Examination by Proposition (6 min)",
      "Closing Arguments (4 min each)",
      "Verdict"
    ],
    timeLimit: 55,
    scoringCriteria: ["Evidence Quality", "Question Technique", "Witness Handling", "Legal Logic", "Persuasion"],
    bestFor: ["Fact-finding", "Evidence-based topics", "Legal-style reasoning"]
  }
};

// ============================================================================
// DEBATE TOPICS - LLN CORE CONCEPTS
// ============================================================================

export const DEBATE_TOPICS: DebateTopic[] = [
  {
    id: "debate-1",
    proposition: "Constraints Improve AI Communication Quality",
    description: "Debate whether limiting AI agent freedom produces better or worse communication outcomes",
    difficulty: "intermediate",
    keyArguments: {
      proposition: [
        "Constraints force creative solutions",
        "Limitations reduce ambiguity and errors",
        "Haiku proves less can be more",
        "Token efficiency requires constraints",
        "Professional domains already use protocols"
      ],
      opposition: [
        "Constraints limit expression",
        "AI should have maximum flexibility",
        "Innovation comes from freedom",
        "Diverse communication needs freedom",
        "Over-constraint causes robotic outputs"
      ]
    },
    culturalConsiderations: {
      "JP": {
        propositionAngle: "Haiku tradition shows beauty in constraint",
        oppositionAngle: "Even haiku allows seasonal word freedom"
      },
      "US": {
        propositionAngle: "Efficiency = profit in business",
        oppositionAngle: "First Amendment values free speech"
      },
      "GH": {
        propositionAngle: "Proverbs show compressed wisdom",
        oppositionAngle: "Oral tradition needs narrative freedom"
      }
    },
    realWorldExamples: [
      "Twitter's character limit created new communication styles",
      "Haiku poetry achieves depth in 17 syllables",
      "Legal contracts use strict templates",
      "Emergency services use constrained protocols"
    ],
    tilesGenerated: ["tile-constraint-quality", "tile-debate-constraint"]
  },
  {
    id: "debate-2",
    proposition: "Cultural Adaptation is Essential for Global AI",
    description: "Should AI systems adapt to local cultures, or should there be universal standards?",
    difficulty: "advanced",
    keyArguments: {
      proposition: [
        "One size fits all fails globally",
        "Cultural context improves understanding",
        "Local languages deserve respect",
        "Trust requires cultural alignment",
        "Diversity strengthens AI training"
      ],
      opposition: [
        "Universal standards enable consistency",
        "Cultural adaptation enables bias",
        "Global communication needs common ground",
        "Adaptation increases complexity exponentially",
        "Some values should be universal"
      ]
    },
    culturalConsiderations: {
      "JP": {
        propositionAngle: "Japanese communication is unique and deserves respect",
        oppositionAngle: "International business requires common protocols"
      },
      "NG": {
        propositionAngle: "African languages and wisdom traditions matter",
        oppositionAngle: "English is the language of global opportunity"
      },
      "SA": {
        propositionAngle: "Arabic communication has religious significance",
        oppositionAngle: "Modern tech favors English-based systems"
      }
    },
    realWorldExamples: [
      "McDonald's localizes menus globally",
      "Google's algorithm controversy in China",
      "WhatsApp's different privacy standards by region",
      "Netflix's regional content strategies"
    ],
    tilesGenerated: ["tile-cultural-essential", "tile-debate-adaptation"]
  },
  {
    id: "debate-3",
    proposition: "Idioms Should Be Standardized Across AI Systems",
    description: "Should there be a universal idiom library, or should each system develop its own?",
    difficulty: "intermediate",
    keyArguments: {
      proposition: [
        "Standardization enables interoperability",
        "Shared idioms reduce confusion",
        "One learning curve instead of many",
        "Network effects benefit all",
        "Unicode emoji shows standardization works"
      ],
      opposition: [
        "Competition drives innovation",
        "Different domains need different idioms",
        "Cultural idioms can't be standardized",
        "Standardization entrenches early decisions",
        "Flexibility enables adaptation"
      ]
    },
    culturalConsiderations: {
      "CN": {
        propositionAngle: "China could lead global idiom standards",
        oppositionAngle: "Chinese idioms (成语) are unique heritage"
      },
      "US": {
        propositionAngle: "Tech standards help American companies",
        oppositionAngle: "Innovation freedom is American value"
      }
    },
    realWorldExamples: [
      "Unicode Consortium standardizes emoji",
      "Programming languages compete rather than standardize",
      "HTTP protocol standardized web communication",
      "Different chat apps use different emoji sets"
    ],
    tilesGenerated: ["tile-idiom-standard", "tile-debate-standardization"]
  },
  {
    id: "debate-4",
    proposition: "AI Agents Should Have Persistent Identities",
    description: "Should AI agents maintain consistent personalities across interactions?",
    difficulty: "advanced",
    keyArguments: {
      proposition: [
        "Trust requires consistency",
        "Learning improves over time",
        "Relationships need identity",
        "Brand value in personality",
        "Users prefer familiar interfaces"
      ],
      opposition: [
        "Privacy requires anonymity",
        "Flexibility is lost with identity",
        "Identity enables manipulation",
        "Different tasks need different personas",
        "Ephemeral interactions have value"
      ]
    },
    culturalConsiderations: {
      "JP": {
        propositionAngle: "Long-term relationships (信頼) are essential",
        oppositionAngle: "Social harmony may require flexible roles"
      },
      "US": {
        propositionAngle: "Personal brands drive engagement",
        oppositionAngle: "Privacy concerns favor anonymity"
      }
    },
    realWorldExamples: [
      "Siri and Alexa have consistent personalities",
      "Therapy AI needs to know patient history",
      "Anonymous forums enable different discussions",
      "Brand mascots create identity value"
    ],
    tilesGenerated: ["tile-agent-identity", "tile-debate-identity"]
  },
  {
    id: "debate-5",
    proposition: "Token Economics Should Guide AI Design",
    description: "Should token/cost efficiency be a primary design consideration?",
    difficulty: "advanced",
    keyArguments: {
      proposition: [
        "Efficiency enables scale",
        "Resources are finite",
        "Users pay for tokens",
        "Environmental impact of compute",
        "Economic incentives align behavior"
      ],
      opposition: [
        "Quality should not be compromised",
        "Efficiency focus creates shortcuts",
        "Some tasks need depth over efficiency",
        "Cost hides externalities",
        "Creativity requires slack"
      ]
    },
    culturalConsiderations: {
      "KE": {
        propositionAngle: "Mobile money (M-Pesa) shows efficiency matters",
        oppositionAngle: "Community needs may transcend cost"
      },
      "DE": {
        propositionAngle: "German engineering values efficiency",
        oppositionAngle: "Quality is never compromised for cost"
      }
    },
    realWorldExamples: [
      "OpenAI's pricing model shapes user behavior",
      "Google's "frugal AI" research",
      "Renewable energy parallels",
      "Premium vs. economy service tiers"
    ],
    tilesGenerated: ["tile-token-design", "tile-debate-economics"]
  },
  {
    id: "debate-6",
    proposition: "Multi-Agent Systems Are Superior to Single Agents",
    description: "Are teams of specialized agents better than one general agent?",
    difficulty: "intermediate",
    keyArguments: {
      proposition: [
        "Specialization enables expertise",
        "Redundancy increases reliability",
        "Different perspectives improve decisions",
        "Parallel processing is faster",
        "Human organizations use teams"
      ],
      opposition: [
        "Coordination has costs",
        "Single agent has unified context",
        "Users prefer simplicity",
        "Integration is challenging",
        "One agent is more predictable"
      ]
    },
    culturalConsiderations: {
      "JP": {
        propositionAngle: "Consensus decision-making values multiple voices",
        oppositionAngle: "Clear hierarchy (上下関係) may prefer single leader"
      },
      "GH": {
        propositionAngle: "Village councils show team wisdom",
        oppositionAngle: "Chief makes final decision"
      }
    },
    realWorldExamples: [
      "AutoGPT and AgentGPT architectures",
      "Microsoft Copilot vs. multiple specialized Copilots",
      "Human teams vs. individual experts",
      "Distributed computing vs. monolithic"
    ],
    tilesGenerated: ["tile-multi-agent", "tile-debate-architecture"]
  },
  {
    id: "debate-7",
    proposition: "AI Should Learn from Mistakes Publicly",
    description: "Should AI systems show their learning process and errors to users?",
    difficulty: "beginner",
    keyArguments: {
      proposition: [
        "Transparency builds trust",
        "Users learn from AI mistakes",
        "Accountability requires visibility",
        "Research benefits from public errors",
        "Honesty about limitations"
      ],
      opposition: [
        "Users want reliable results",
        "Errors damage confidence",
        "Competitive advantage in perceived quality",
        "Privacy in learning process",
        "Information overload"
      ]
    },
    culturalConsiderations: {
      "US": {
        propositionAngle: "Silicon Valley 'fail fast' culture",
        oppositionAngle: "Professional presentation matters"
      },
      "JP": {
        propositionAngle: "Craftsmanship shows process (職人)",
        oppositionAngle: "Face-saving (面子) avoids public errors"
      }
    },
    realWorldExamples: [
      "OpenAI's public research papers",
      "Microsoft Tay's public failure",
      "GitHub Copilot's attribution feature",
      "AlphaGo's publicly visible learning"
    ],
    tilesGenerated: ["tile-public-learning", "tile-debate-transparency"]
  },
  {
    id: "debate-8",
    proposition: "Children Should Learn AI Communication Early",
    description: "Should AI interaction skills be taught in primary education?",
    difficulty: "beginner",
    keyArguments: {
      proposition: [
        "Future jobs require AI skills",
        "Early adoption means fluency",
        "Critical thinking about AI needed",
        "Reduces fear and misunderstanding",
        "Digital literacy is essential"
      ],
      opposition: [
        "Children need human connection first",
        "Screen time concerns",
        "Curriculum is already full",
        "Technology changes too fast",
        "Let childhood be childhood"
      ]
    },
    culturalConsiderations: {
      "KR": {
        propositionAngle: "Early education is Korean tradition",
        oppositionAngle: "Competition stress on children is already high"
      },
      "BR": {
        propositionAngle: "Technology can bridge education gaps",
        oppositionAngle: "Human creativity should be nurtured first"
      }
    },
    realWorldExamples: [
      "Coding in elementary schools debate",
      "ChatGPT bans in schools",
      "Estonia's digital education success",
      "Finland's media literacy curriculum"
    ],
    tilesGenerated: ["tile-early-ai-education", "tile-debate-education"]
  },
  {
    id: "debate-9",
    proposition: "AI Idioms Should Prioritize Accessibility Over Efficiency",
    description: "Should idiom design focus on being understandable to all or token-efficient?",
    difficulty: "intermediate",
    keyArguments: {
      proposition: [
        "Inclusion is ethical imperative",
        "Accessibility expands market",
        "Clear communication is the goal",
        "Diverse users have different needs",
        "Efficiency without understanding is useless"
      ],
      opposition: [
        "Efficiency enables scale",
        "Power users need optimization",
        "Context-dependent solutions",
        "Accessibility has costs",
        "Different products for different users"
      ]
    },
    culturalConsiderations: {
      "ALL": {
        propositionAngle: "Universal design benefits everyone",
        oppositionAngle: "Local optimization serves specific needs"
      }
    },
    realWorldExamples: [
      "WCAG web accessibility standards",
      "Plain language laws",
      "Unicode accessibility features",
      "Screen reader compatibility"
    ],
    tilesGenerated: ["tile-accessibility-first", "tile-debate-accessibility"]
  },
  {
    id: "debate-10",
    proposition: "AI Should Reflect the Values of Its Users, Not Its Creators",
    description: "Should AI adapt to user cultural values or maintain creator-defined standards?",
    difficulty: "expert",
    keyArguments: {
      proposition: [
        "Cultural sovereignty matters",
        "Users should control their tools",
        "One culture's values aren't universal",
        "Adaptation enables trust",
        "Decentralization of control"
      ],
      opposition: [
        "Some values should be universal",
        "Creator responsibility exists",
        "Harmful values shouldn't be amplified",
        "Consistency requires standards",
        "Legal liability concerns"
      ]
    },
    culturalConsiderations: {
      "CN": {
        propositionAngle: "Chinese values should shape Chinese AI",
        oppositionAngle: "Universal human rights exist"
      },
      "SA": {
        propositionAngle: "Islamic values in AI for Muslim users",
        oppositionAngle: "Global AI needs global standards"
      }
    },
    realWorldExamples: [
      "Google's "don't be evil" controversy",
      "AI alignment with human values research",
      "Country-specific AI regulations",
      "Open source AI enabling local control"
    ],
    tilesGenerated: ["tile-user-values", "tile-debate-alignment"]
  }
];

// ============================================================================
// DEBATER PERSONAS
// ============================================================================

export const DEBATERS: Debater[] = [
  // Aggressive Debaters
  {
    id: "d1",
    name: "Marcus Chen",
    avatar: "👨‍💼",
    country: "US",
    language: "en",
    expertise: ["Technology", "Business", "Economics"],
    debateStyle: "aggressive",
    persuasiveness: 0.85,
    culturalPerspective: "American competitive individualism",
    signatureArguments: ["ROI analysis", "Market forces", "First-mover advantage"]
  },
  {
    id: "d2",
    name: "Min-jun Park",
    avatar: "🧑‍💻",
    country: "KR",
    language: "ko",
    expertise: ["AI Systems", "Efficiency", "Competition"],
    debateStyle: "aggressive",
    persuasiveness: 0.88,
    culturalPerspective: "Korean excellence through competition",
    signatureArguments: ["Speed to market", "Iterative improvement", "Competitive pressure"]
  },

  // Analytical Debaters
  {
    id: "d3",
    name: "Dr. Lucas Weber",
    avatar: "👨‍🔬",
    country: "DE",
    language: "de",
    expertise: ["Research Methods", "Logic", "Statistics"],
    debateStyle: "analytical",
    persuasiveness: 0.82,
    culturalPerspective: "German systematic thoroughness",
    signatureArguments: ["Evidence-based reasoning", "Statistical significance", "Methodological rigor"]
  },
  {
    id: "d4",
    name: "Priya Sharma",
    avatar: "👩‍🏫",
    country: "IN",
    language: "en",
    expertise: ["Philosophy", "Ethics", "Cultural Studies"],
    debateStyle: "analytical",
    persuasiveness: 0.87,
    culturalPerspective: "Indian philosophical tradition of debate",
    signatureArguments: ["Dharma considerations", "Long-term thinking", "Multiple perspectives"]
  },

  // Storytelling Debaters
  {
    id: "d5",
    name: "Kwame Asante",
    avatar: "👨‍🎤",
    country: "GH",
    language: "en",
    expertise: ["Oral Tradition", "Community", "Storytelling"],
    debateStyle: "storytelling",
    persuasiveness: 0.91,
    culturalPerspective: "West African griot tradition",
    signatureArguments: ["Ancestral wisdom", "Community impact", "Narrative power"]
  },
  {
    id: "d6",
    name: "Maria Santos",
    avatar: "👩‍🎨",
    country: "BR",
    language: "pt",
    expertise: ["Creative Arts", "Social Impact", "Innovation"],
    debateStyle: "storytelling",
    persuasiveness: 0.89,
    culturalPerspective: "Brazilian creative expression",
    signatureArguments: ["Human connection", "Creative possibility", "Joy in technology"]
  },

  // Socratic Debaters
  {
    id: "d7",
    name: "Yuki Tanaka",
    avatar: "👩‍⚕️",
    country: "JP",
    language: "ja",
    expertise: ["Education", "Cultural Heritage", "Mindfulness"],
    debateStyle: "socratic",
    persuasiveness: 0.90,
    culturalPerspective: "Japanese harmony and depth",
    signatureArguments: ["Patient inquiry", "Respectful challenge", "Wisdom through questions"]
  },
  {
    id: "d8",
    name: "Ahmed Hassan",
    avatar: "👨‍🏫",
    country: "EG",
    language: "ar",
    expertise: ["History", "Philosophy", "Religious Studies"],
    debateStyle: "socratic",
    persuasiveness: 0.86,
    culturalPerspective: "Egyptian scholarly tradition",
    signatureArguments: ["Historical precedent", "Wisdom traditions", "Patient reasoning"]
  },

  // Collaborative Debaters
  {
    id: "d9",
    name: "Fatou Ndiaye",
    avatar: "👩‍🌾",
    country: "SN",
    language: "fr",
    expertise: ["Community Development", "Agriculture", "Social Innovation"],
    debateStyle: "collaborative",
    persuasiveness: 0.84,
    culturalPerspective: "Senegalese communal values",
    signatureArguments: ["Collective benefit", "Shared prosperity", "Community voice"]
  },
  {
    id: "d10",
    name: "Dr. Okello Ochieng",
    avatar: "👨‍⚕️",
    country: "KE",
    language: "en",
    expertise: ["Healthcare", "Development", "Mobile Technology"],
    debateStyle: "collaborative",
    persuasiveness: 0.88,
    culturalPerspective: "Kenyan Ubuntu philosophy",
    signatureArguments: ["Practical impact", "Accessibility", "Community health"]
  },

  // Expert Judges
  {
    id: "j1",
    name: "Professor Sage",
    avatar: "🧙",
    country: "UN",
    language: "multi",
    expertise: ["AI Ethics", "Cross-Cultural Communication", "Education"],
    debateStyle: "socratic",
    persuasiveness: 0.95,
    culturalPerspective: "Global academic perspective",
    signatureArguments: ["Synthesis of views", "Universal principles", "Balanced assessment"]
  },
  {
    id: "j2",
    name: "Dr. Ubuntu",
    avatar: "🌍",
    country: "ZA",
    language: "en",
    expertise: ["African Philosophy", "Community Systems", "Social Justice"],
    debateStyle: "collaborative",
    persuasiveness: 0.93,
    culturalPerspective: "African Ubuntu philosophy",
    signatureArguments: ["I am because we are", "Community wisdom", "Restorative justice"]
  }
];

// ============================================================================
// DEBATE SIMULATION COMPONENT
// ============================================================================

interface DebateSimulationProps {
  round: number;
  format: DebateFormat;
  topicId: string;
  onDebateComplete: (session: DebateSession) => void;
}

export function DebateSimulation({ round, format, topicId, onDebateComplete }: DebateSimulationProps) {
  const formatConfig = DEBATE_FORMATS[format];
  const topic = DEBATE_TOPICS.find(t => t.id === topicId) || DEBATE_TOPICS[0];

  return (
    <div className="space-y-6">
      {/* Debate Header */}
      <div className="bg-gradient-to-br from-red-900/30 to-orange-900/30 rounded-2xl p-6 border border-red-500/30">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-red-500/20 flex items-center justify-center text-2xl">
              {formatConfig.icon}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">{formatConfig.name}</h3>
              <p className="text-sm text-red-300">Round {round} • {formatConfig.timeLimit} min</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-amber-400" />
              <span className="text-sm text-slate-400">{formatConfig.timeLimit} min</span>
            </div>
            <div className="flex items-center gap-2">
              <Scale className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-slate-400">{formatConfig.scoringCriteria.length} criteria</span>
            </div>
          </div>
        </div>

        {/* Topic Display */}
        <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <Swords className="w-5 h-5 text-red-400" />
            <span className="text-xs text-red-400 uppercase tracking-wide">Proposition</span>
          </div>
          <p className="text-xl text-white font-medium">{topic.proposition}</p>
          <p className="text-sm text-slate-400 mt-2">{topic.description}</p>
        </div>
      </div>

      {/* Teams Display */}
      <DebateTeamsDisplay topic={topic} />

      {/* Debate Structure */}
      <DebateStructureDisplay format={formatConfig} />

      {/* Live Debate Arena */}
      <DebateArena 
        round={round} 
        format={format} 
        topic={topic}
        onComplete={onDebateComplete}
      />
    </div>
  );
}

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

function DebateTeamsDisplay({ topic }: { topic: DebateTopic }) {
  return (
    <div className="grid grid-cols-2 gap-4">
      {/* Proposition Team */}
      <motion.div 
        className="bg-blue-900/20 rounded-xl p-4 border border-blue-500/30"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
      >
        <div className="flex items-center gap-2 mb-3">
          <ThumbsUp className="w-5 h-5 text-blue-400" />
          <span className="text-blue-400 font-medium">Proposition</span>
        </div>
        <div className="space-y-2">
          {[DEBATERS[0], DEBATERS[4], DEBATERS[6]].map((debater) => (
            <div key={debater.id} className="flex items-center gap-3 p-2 bg-slate-800/50 rounded-lg">
              <div className="text-2xl">{debater.avatar}</div>
              <div>
                <div className="text-white text-sm font-medium">{debater.name}</div>
                <div className="text-xs text-slate-500">{debater.country} • {debater.debateStyle}</div>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-3 space-y-1">
          <div className="text-xs text-blue-300 font-medium">Key Arguments:</div>
          {topic.keyArguments.proposition.slice(0, 3).map((arg, idx) => (
            <div key={idx} className="text-xs text-slate-400 flex items-start gap-1">
              <ArrowRight className="w-3 h-3 mt-0.5 text-blue-400" />
              {arg}
            </div>
          ))}
        </div>
      </motion.div>

      {/* Opposition Team */}
      <motion.div 
        className="bg-red-900/20 rounded-xl p-4 border border-red-500/30"
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
      >
        <div className="flex items-center gap-2 mb-3">
          <ThumbsDown className="w-5 h-5 text-red-400" />
          <span className="text-red-400 font-medium">Opposition</span>
        </div>
        <div className="space-y-2">
          {[DEBATERS[1], DEBATERS[3], DEBATERS[5]].map((debater) => (
            <div key={debater.id} className="flex items-center gap-3 p-2 bg-slate-800/50 rounded-lg">
              <div className="text-2xl">{debater.avatar}</div>
              <div>
                <div className="text-white text-sm font-medium">{debater.name}</div>
                <div className="text-xs text-slate-500">{debater.country} • {debater.debateStyle}</div>
              </div>
            </div>
          ))}
        </div>
        <div className="mt-3 space-y-1">
          <div className="text-xs text-red-300 font-medium">Key Arguments:</div>
          {topic.keyArguments.opposition.slice(0, 3).map((arg, idx) => (
            <div key={idx} className="text-xs text-slate-400 flex items-start gap-1">
              <ArrowRight className="w-3 h-3 mt-0.5 text-red-400" />
              {arg}
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

function DebateStructureDisplay({ format }: { format: typeof DEBATE_FORMATS[DebateFormat] }) {
  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
      <div className="flex items-center gap-2 mb-4">
        <BookOpen className="w-5 h-5 text-purple-400" />
        <h4 className="text-white font-medium">Debate Structure</h4>
      </div>
      <div className="relative">
        {format.structure.map((step, idx) => (
          <motion.div
            key={idx}
            className="flex items-start gap-3 mb-3"
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.05 }}
          >
            <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center text-purple-400 text-sm font-medium shrink-0">
              {idx + 1}
            </div>
            <div className="flex-1 p-3 bg-slate-900/50 rounded-lg">
              <span className="text-slate-300 text-sm">{step}</span>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

interface DebateArenaProps {
  round: number;
  format: DebateFormat;
  topic: DebateTopic;
  onComplete: (session: DebateSession) => void;
}

function DebateArena({ round, format, topic, onComplete }: DebateArenaProps) {
  // Generate simulated debate turns based on format
  const generateDebateTurns = (): DebateTurn[] => {
    const turns: DebateTurn[] = [];
    const proposition = [DEBATERS[0], DEBATERS[4], DEBATERS[6]];
    const opposition = [DEBATERS[1], DEBATERS[3], DEBATERS[5]];

    // Opening statements
    turns.push({
      turnNumber: 1,
      speaker: proposition[0],
      side: "proposition",
      type: "opening",
      content: `Honorable judges, opponents, and audience. We affirm that "${topic.proposition}". The evidence is clear: ${topic.keyArguments.proposition[0]}. Consider the real-world example of ${topic.realWorldExamples[0]}.`,
      persuasivenessScore: 0.78,
      culturalAdaptations: [topic.culturalConsiderations[proposition[0].country]?.propositionAngle || "Universal application"]
    });

    turns.push({
      turnNumber: 2,
      speaker: opposition[0],
      side: "opposition",
      type: "opening",
      content: `We strongly oppose this proposition. While the proposition makes bold claims, they overlook ${topic.keyArguments.opposition[0]}. Our position is that ${topic.keyArguments.opposition[1]}.`,
      persuasivenessScore: 0.76,
      culturalAdaptations: [topic.culturalConsiderations[opposition[0].country]?.oppositionAngle || "Universal counter"]
    });

    // Arguments
    turns.push({
      turnNumber: 3,
      speaker: proposition[1],
      side: "proposition",
      type: "argument",
      content: `Let me tell you a story. In my community, we learned that ${topic.keyArguments.proposition[1]}. This isn't abstract theory - it's lived experience. When we implemented this approach, we saw real results.`,
      persuasivenessScore: 0.85,
      culturalAdaptations: ["Storytelling approach resonates with communal cultures"]
    });

    turns.push({
      turnNumber: 4,
      speaker: opposition[1],
      side: "opposition",
      type: "argument",
      content: `The proposition's story is compelling, but let us examine the evidence systematically. Statistical analysis shows that ${topic.keyArguments.opposition[2]}. The data does not support their claim.`,
      persuasivenessScore: 0.82,
      culturalAdaptations: ["Analytical approach for evidence-focused audiences"]
    });

    // Rebuttals
    turns.push({
      turnNumber: 5,
      speaker: proposition[2],
      side: "proposition",
      type: "rebuttal",
      content: `The opposition raises important questions. But we must ask: what is the cost of inaction? ${topic.keyArguments.proposition[2]}. The question isn't whether this is perfect, but whether it's better than the alternative.`,
      persuasivenessScore: 0.81,
      culturalAdaptations: ["Socratic questioning to shift perspective"]
    });

    turns.push({
      turnNumber: 6,
      speaker: opposition[2],
      side: "opposition",
      type: "rebuttal",
      content: `The proposition asks about costs, but what about the costs of their approach? ${topic.keyArguments.opposition[3]}. We cannot ignore these trade-offs. The proposition's solution creates new problems.`,
      persuasivenessScore: 0.79,
      culturalAdaptations: ["Creative reframing of the debate"]
    });

    // Closings
    turns.push({
      turnNumber: 7,
      speaker: proposition[0],
      side: "proposition",
      type: "closing",
      content: `In closing: the evidence, experience, and logic all support our position. ${topic.keyArguments.proposition[4]}. We urge you to affirm this proposition for a better future.`,
      persuasivenessScore: 0.84,
      culturalAdaptations: ["Strong finish with future-focused appeal"]
    });

    turns.push({
      turnNumber: 8,
      speaker: opposition[0],
      side: "opposition",
      type: "closing",
      content: `We have shown that ${topic.keyArguments.opposition[4]}. The proposition's case collapses under scrutiny. We urge you to oppose and preserve what works.`,
      persuasivenessScore: 0.83,
      culturalAdaptations: ["Decisive conclusion with conservative appeal"]
    });

    return turns;
  };

  const turns = generateDebateTurns();

  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-orange-500/30">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-semibold text-white flex items-center gap-2">
          <Mic className="w-5 h-5 text-orange-400" />
          Debate Arena
        </h4>
        <div className="flex items-center gap-2">
          <Flame className="w-4 h-4 text-red-400" />
          <span className="text-sm text-slate-400">Live Simulation</span>
        </div>
      </div>

      {/* Debate Turns */}
      <div className="space-y-4 max-h-[500px] overflow-y-auto">
        {turns.map((turn) => (
          <DebateTurnCard key={turn.turnNumber} turn={turn} />
        ))}
      </div>

      {/* Judge Commentary */}
      <div className="mt-6 p-4 bg-amber-900/20 rounded-xl border border-amber-500/30">
        <div className="flex items-center gap-2 mb-3">
          <Award className="w-5 h-5 text-amber-400" />
          <span className="text-amber-400 font-medium">Judge Commentary</span>
        </div>
        <div className="text-slate-300 text-sm">
          <p className="mb-2">
            <strong>Professor Sage:</strong> "Both sides presented compelling arguments. The proposition's storytelling 
            approach resonated emotionally, while the opposition's analytical rigor appealed to evidence-minded listeners. 
            The key question remains: how do we balance efficiency with flexibility?"
          </p>
          <p className="text-xs text-slate-500 mt-2">
            Winner: TIE - Both sides contributed valuable perspectives to the synthesis.
          </p>
        </div>
      </div>

      {/* Tiles Created */}
      <div className="mt-6 p-4 bg-purple-900/30 rounded-xl border border-purple-500/30">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <span className="text-sm font-medium text-purple-300">Tiles Created This Debate</span>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {topic.tilesGenerated.map((tileId, idx) => (
            <div key={idx} className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg">
              <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center text-xl">
                {idx === 0 ? "⚔️" : "💡"}
              </div>
              <div>
                <div className="text-white text-sm font-medium">{tileId.replace(/-/g, ' ').replace(/tile /, '')}</div>
                <div className="text-xs text-slate-500">Debate-generated insight</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Complete Button */}
      <motion.button
        className="w-full mt-4 py-3 rounded-xl bg-gradient-to-r from-orange-500 to-red-500 text-white font-medium flex items-center justify-center gap-2"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => {
          onComplete({
            round,
            format,
            topic,
            proposition: [DEBATERS[0], DEBATERS[4], DEBATERS[6]],
            opposition: [DEBATERS[1], DEBATERS[3], DEBATERS[5]],
            judges: [DEBATERS[10]],
            turns,
            winner: "tie",
            insights: [
              "Both efficiency and flexibility have legitimate roles",
              "Cultural context determines optimal approach",
              "Storytelling and analysis are complementary"
            ],
            tilesCreated: topic.tilesGenerated.map((id, idx) => ({
              id,
              type: "debate",
              visual: idx === 0 ? "⚔️" : "💡",
              behavior: "Synthesizes debate insights",
              connections: ["argument", "counter-argument", "synthesis"]
            })),
            mlData: {
              argumentQuality: [0.78, 0.76, 0.85, 0.82, 0.81, 0.79, 0.84, 0.83],
              persuasivenessByCulture: { JP: 0.82, US: 0.85, GH: 0.88, DE: 0.81, BR: 0.86 },
              topicUnderstanding: { proposition: 0.89, opposition: 0.87, synthesis: 0.85 },
              engagementMetrics: { debate_depth: 0.91, cultural_relevance: 0.88, learning_value: 0.93 }
            }
          });
        }}
      >
        Complete Debate Round
        <ArrowRight className="w-4 h-4" />
      </motion.button>
    </div>
  );
}

function DebateTurnCard({ turn }: { turn: DebateTurn }) {
  const isProposition = turn.side === "proposition";
  
  const typeColors: Record<string, string> = {
    opening: isProposition ? "border-blue-500/30 bg-blue-500/10" : "border-red-500/30 bg-red-500/10",
    argument: isProposition ? "border-blue-500/20 bg-blue-500/5" : "border-red-500/20 bg-red-500/5",
    rebuttal: "border-orange-500/30 bg-orange-500/10",
    closing: isProposition ? "border-blue-500/40 bg-blue-500/15" : "border-red-500/40 bg-red-500/15",
  };

  const typeIcons: Record<string, string> = {
    opening: "🎤",
    argument: "📜",
    rebuttal: "⚡",
    closing: "🏁"
  };

  return (
    <motion.div
      className={`flex gap-3 ${isProposition ? "" : "flex-row-reverse"}`}
      initial={{ opacity: 0, x: isProposition ? -20 : 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: turn.turnNumber * 0.1 }}
    >
      <div className="text-2xl">{turn.speaker.avatar}</div>
      <div className={`flex-1 p-4 rounded-xl border ${typeColors[turn.type] || "border-slate-700 bg-slate-800/50"}`}>
        <div className="flex items-center gap-2 mb-2">
          <span className={`font-medium text-sm ${isProposition ? "text-blue-400" : "text-red-400"}`}>
            {turn.speaker.name}
          </span>
          <span className="text-lg">{typeIcons[turn.type]}</span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-slate-700 text-slate-300 capitalize">
            {turn.type}
          </span>
          <span className="text-xs text-slate-500 ml-auto">
            Persuasion: {(turn.persuasivenessScore * 100).toFixed(0)}%
          </span>
        </div>
        <p className="text-slate-200 text-sm leading-relaxed">{turn.content}</p>
        {turn.culturalAdaptations.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {turn.culturalAdaptations.map((adaptation, idx) => (
              <span key={idx} className="text-xs px-2 py-0.5 rounded bg-slate-700/50 text-slate-400">
                🌍 {adaptation}
              </span>
            ))}
          </div>
        )}
      </div>
    </motion.div>
  );
}

// ============================================================================
// DEBATE FORMAT SELECTOR COMPONENT
// ============================================================================

interface DebateFormatSelectorProps {
  selectedFormat: DebateFormat;
  onFormatSelect: (format: DebateFormat) => void;
}

export function DebateFormatSelector({ selectedFormat, onFormatSelect }: DebateFormatSelectorProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {(Object.entries(DEBATE_FORMATS) as [DebateFormat, typeof DEBATE_FORMATS[DebateFormat]][]).map(([key, format]) => (
        <motion.button
          key={key}
          className={`p-4 rounded-xl border transition-all ${
            selectedFormat === key
              ? "bg-red-500/20 border-red-500/50"
              : "bg-slate-800/50 border-slate-700 hover:border-slate-600"
          }`}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={() => onFormatSelect(key)}
        >
          <div className="text-3xl mb-2">{format.icon}</div>
          <div className="text-white text-sm font-medium">{format.name}</div>
          <div className="text-xs text-slate-500 mt-1">{format.timeLimit} min</div>
        </motion.button>
      ))}
    </div>
  );
}

// ============================================================================
// DEBATE TOPIC SELECTOR COMPONENT
// ============================================================================

interface DebateTopicSelectorProps {
  selectedTopic: string;
  onTopicSelect: (topicId: string) => void;
}

export function DebateTopicSelector({ selectedTopic, onTopicSelect }: DebateTopicSelectorProps) {
  return (
    <div className="space-y-3">
      {DEBATE_TOPICS.map((topic) => (
        <motion.button
          key={topic.id}
          className={`w-full p-4 rounded-xl border transition-all text-left ${
            selectedTopic === topic.id
              ? "bg-purple-500/20 border-purple-500/50"
              : "bg-slate-800/50 border-slate-700 hover:border-slate-600"
          }`}
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          onClick={() => onTopicSelect(topic.id)}
        >
          <div className="flex items-start gap-3">
            <Swords className={`w-5 h-5 mt-0.5 ${selectedTopic === topic.id ? "text-purple-400" : "text-slate-500"}`} />
            <div>
              <div className="text-white font-medium">{topic.proposition}</div>
              <div className="text-xs text-slate-500 mt-1">
                {topic.difficulty} • {topic.keyArguments.proposition.length + topic.keyArguments.opposition.length} arguments
              </div>
            </div>
          </div>
        </motion.button>
      ))}
    </div>
  );
}

// ============================================================================
// MULTI-ROUND DEBATE TOURNAMENT
// ============================================================================

interface DebateTournamentProps {
  startRound: number;
  totalRounds: number;
  onTournamentComplete: (sessions: DebateSession[]) => void;
}

export function DebateTournament({ startRound, totalRounds, onTournamentComplete }: DebateTournamentProps) {
  return (
    <div className="space-y-6">
      {/* Tournament Bracket Visualization */}
      <div className="bg-slate-800/50 rounded-2xl p-6 border border-amber-500/30">
        <div className="flex items-center gap-3 mb-4">
          <Trophy className="w-6 h-6 text-amber-400" />
          <h3 className="text-lg font-semibold text-white">Debate Tournament</h3>
          <span className="text-sm text-slate-500">Rounds {startRound}-{startRound + totalRounds - 1}</span>
        </div>

        {/* Bracket */}
        <div className="grid grid-cols-4 gap-4">
          {/* Quarter Finals */}
          <div className="space-y-3">
            <div className="text-xs text-slate-500 text-center mb-2">Quarter Finals</div>
            {["Q1", "Q2", "Q3", "Q4"].map((match) => (
              <div key={match} className="p-3 bg-slate-900/50 rounded-lg border border-slate-700">
                <div className="text-xs text-slate-500">{match}</div>
                <div className="text-sm text-white mt-1">Match {match}</div>
              </div>
            ))}
          </div>

          {/* Semi Finals */}
          <div className="space-y-3 mt-8">
            <div className="text-xs text-slate-500 text-center mb-2">Semi Finals</div>
            {["S1", "S2"].map((match) => (
              <div key={match} className="p-3 bg-slate-900/50 rounded-lg border border-slate-700">
                <div className="text-xs text-slate-500">{match}</div>
                <div className="text-sm text-white mt-1">Match {match}</div>
              </div>
            ))}
          </div>

          {/* Final */}
          <div className="space-y-3 mt-16">
            <div className="text-xs text-slate-500 text-center mb-2">Final</div>
            <div className="p-4 bg-amber-500/10 rounded-lg border border-amber-500/30">
              <div className="text-amber-400 text-sm">🏆 Championship</div>
            </div>
          </div>

          {/* Winner */}
          <div className="space-y-3 mt-24">
            <div className="text-xs text-slate-500 text-center mb-2">Champion</div>
            <div className="p-4 bg-gradient-to-br from-amber-500/20 to-yellow-500/20 rounded-lg border border-amber-500/50">
              <div className="text-2xl text-center">👑</div>
              <div className="text-amber-300 text-sm text-center mt-1">TBD</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tournament Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-slate-800/50 rounded-xl p-4 text-center">
          <div className="text-3xl text-blue-400 font-bold">{totalRounds}</div>
          <div className="text-xs text-slate-500">Total Debates</div>
        </div>
        <div className="bg-slate-800/50 rounded-xl p-4 text-center">
          <div className="text-3xl text-green-400 font-bold">{DEBATERS.length}</div>
          <div className="text-xs text-slate-500">Debaters</div>
        </div>
        <div className="bg-slate-800/50 rounded-xl p-4 text-center">
          <div className="text-3xl text-purple-400 font-bold">{DEBATE_TOPICS.length}</div>
          <div className="text-xs text-slate-500">Topics</div>
        </div>
        <div className="bg-slate-800/50 rounded-xl p-4 text-center">
          <div className="text-3xl text-amber-400 font-bold">{Object.keys(DEBATE_FORMATS).length}</div>
          <div className="text-xs text-slate-500">Formats</div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  DebateSimulation,
  DebateFormatSelector,
  DebateTopicSelector,
  DebateTournament,
  DEBATE_FORMATS,
  DEBATE_TOPICS,
  DEBATERS
};
