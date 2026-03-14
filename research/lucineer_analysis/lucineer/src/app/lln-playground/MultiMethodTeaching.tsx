// ============================================================================
// LLN PLAYGROUND - MULTI-METHOD TEACHING FRAMEWORK
// Rounds 26-50: 8 Different Pedagogical Approaches
// ============================================================================

import { motion } from "framer-motion";
import {
  GraduationCap,
  Users,
  Globe,
  MessageCircle,
  Sparkles,
  BookOpen,
  Brain,
  Lightbulb,
  CheckCircle,
  ArrowRight,
  Star,
  Trophy,
  Target,
  Clock,
  Languages,
  Hammer,
  FlaskConical,
  Palette,
  Users2,
  Presentation,
  Compass,
  Award,
  Rocket,
  Puzzle,
  Microscope,
  PenTool,
  Video,
  Play,
} from "lucide-react";

// ============================================================================
// TEACHING METHOD TYPES
// ============================================================================

type TeachingMethod = 
  | "socratic"           // Rounds 1-25: Question-driven discovery
  | "project-based"      // Rounds 26-30: Build real projects
  | "inquiry-based"      // Rounds 31-35: Student-led investigation
  | "collaborative"      // Rounds 36-40: Group problem-solving
  | "storytelling"       // Rounds 41-45: Narrative-driven learning
  | "flipped-classroom"  // Rounds 46-50: Students teach each other
  | "apprenticeship"     // Rounds 51-55: Master-student relationships
  | "montessori";        // Rounds 56-60: Self-directed exploration

interface TeachingMethodConfig {
  id: TeachingMethod;
  name: string;
  icon: string;
  description: string;
  rounds: { start: number; end: number };
  principles: string[];
  techniques: string[];
  assessmentStyle: string;
  bestFor: string[];
  culturalConsiderations: Record<string, string>;
}

// ============================================================================
// TEACHING METHOD DEFINITIONS
// ============================================================================

export const TEACHING_METHODS: Record<TeachingMethod, TeachingMethodConfig> = {
  socratic: {
    id: "socratic",
    name: "Socratic Method",
    icon: "🧙",
    description: "Question-driven discovery through guided dialogue",
    rounds: { start: 1, end: 25 },
    principles: [
      "Ask, don't tell",
      "Guide through questions",
      "Let students discover answers",
      "Challenge assumptions",
      "Build on responses"
    ],
    techniques: ["Socratic circles", "Guided questioning", "Devil's advocate", "Concept mapping"],
    assessmentStyle: "Dialogue quality and insight generation",
    bestFor: ["Critical thinking", "Philosophy", "Ethics", "Deep understanding"],
    culturalConsiderations: {
      "JP": "May feel confrontational; soften approach",
      "GH": "Works well with oral tradition",
      "US": "Natural fit for debate culture",
      "CN": "Respect authority; use indirect questioning"
    }
  },

  "project-based": {
    id: "project-based",
    name: "Project-Based Learning",
    icon: "🔨",
    description: "Learning by building real, meaningful projects",
    rounds: { start: 26, end: 30 },
    principles: [
      "Learn by doing",
      "Real-world problems",
      "Student choice and voice",
      "Collaborative creation",
      "Public presentation"
    ],
    techniques: ["Design thinking", "Prototyping", "Iteration cycles", "Peer review"],
    assessmentStyle: "Project completion and real-world impact",
    bestFor: ["Practical skills", "Engineering", "Creative work", "Teamwork"],
    culturalConsiderations: {
      "JP": "Emphasize craftsmanship and iteration",
      "GH": "Focus on community-beneficial projects",
      "BR": "Include creative and artistic elements",
      "DE": "Emphasize systematic process documentation"
    }
  },

  "inquiry-based": {
    id: "inquiry-based",
    name: "Inquiry-Based Learning",
    icon: "🔬",
    description: "Student-led investigation and discovery",
    rounds: { start: 31, end: 35 },
    principles: [
      "Start with questions, not answers",
      "Student-driven exploration",
      "Hypothesis and testing",
      "Evidence-based conclusions",
      "Iterative refinement"
    ],
    techniques: ["Research projects", "Experiments", "Data analysis", "Scientific method"],
    assessmentStyle: "Research process and evidence quality",
    bestFor: ["Science", "Research skills", "Critical analysis", "Problem-solving"],
    culturalConsiderations: {
      "JP": "Provide structure within freedom",
      "NG": "Connect to local problems",
      "IN": "Link to ancient inquiry traditions",
      "US": "Encourage bold hypotheses"
    }
  },

  collaborative: {
    id: "collaborative",
    name: "Collaborative Learning",
    icon: "👥",
    description: "Group problem-solving with shared responsibility",
    rounds: { start: 36, end: 40 },
    principles: [
      "Shared goals",
      "Interdependence",
      "Individual accountability",
      "Social skill development",
      "Group processing"
    ],
    techniques: ["Jigsaw method", "Think-pair-share", "Group projects", "Peer teaching"],
    assessmentStyle: "Group outcomes and individual contribution",
    bestFor: ["Social skills", "Teamwork", "Communication", "Perspective-taking"],
    culturalConsiderations: {
      "JP": "Natural fit with group harmony values",
      "GH": "Aligns with Ubuntu philosophy",
      "US": "May need structure to ensure participation",
      "KR": "Balance competition with collaboration"
    }
  },

  storytelling: {
    id: "storytelling",
    name: "Narrative-Based Learning",
    icon: "📖",
    description: "Learning through stories, myths, and narratives",
    rounds: { start: 41, end: 45 },
    principles: [
      "Stories encode knowledge",
      "Emotional connection enhances memory",
      "Characters model behavior",
      "Conflict drives engagement",
      "Resolution provides insight"
    ],
    techniques: ["Story circles", "Hero's journey", "Case studies", "Historical narratives"],
    assessmentStyle: "Narrative creation and meaning extraction",
    bestFor: ["History", "Ethics", "Cultural knowledge", "Complex concepts"],
    culturalConsiderations: {
      "GH": "Perfect fit with griot tradition",
      "JP": "Use folk tales and historical stories",
      "MX": "Incorporate family narratives",
      "EG": "Connect to ancient stories"
    }
  },

  "flipped-classroom": {
    id: "flipped-classroom",
    name: "Flipped Classroom",
    icon: "🔄",
    description: "Students teach each other; teacher facilitates",
    rounds: { start: 46, end: 50 },
    principles: [
      "Content consumption at home",
      "Active work in class",
      "Students as teachers",
      "Peer-to-peer learning",
      "Teacher as facilitator"
    ],
    techniques: ["Student presentations", "Peer tutoring", "Study groups", "Discussion leadership"],
    assessmentStyle: "Teaching quality and peer learning outcomes",
    bestFor: ["Self-directed learners", "Deep dive topics", "Peer expertise", "Review sessions"],
    culturalConsiderations: {
      "JP": "Respect for student expertise may be challenging",
      "US": "Natural fit with individual initiative",
      "BR": "Add creative presentation options",
      "DE": "Emphasize preparation and rigor"
    }
  },

  apprenticeship: {
    id: "apprenticeship",
    name: "Apprenticeship Model",
    icon: "🎓",
    description: "Master-student relationship with guided practice",
    rounds: { start: 51, end: 55 },
    principles: [
      "Observation before practice",
      "Gradual skill transfer",
      "Master as role model",
      "Practice with feedback",
      "Journeyman to master progression"
    ],
    techniques: ["Shadowing", "Scaffolding", "Gradual release", "Portfolio building"],
    assessmentStyle: "Skill demonstration and master approval",
    bestFor: ["Crafts", "Arts", "Professional skills", "Complex techniques"],
    culturalConsiderations: {
      "JP": "Perfect fit with shuhari tradition",
      "GH": "Aligns with traditional apprenticeship",
      "IN": "Connect to guru-shishya tradition",
      "IT": "Link to Renaissance workshop model"
    }
  },

  montessori: {
    id: "montessori",
    name: "Montessori Approach",
    icon: "🧩",
    description: "Self-directed exploration with prepared environment",
    rounds: { start: 56, end: 60 },
    principles: [
      "Follow the child",
      "Prepared environment",
      "Freedom within limits",
      "Mixed-age groups",
      "Intrinsic motivation"
    ],
    techniques: ["Self-correcting materials", "Choice boards", "Work cycles", "Observation"],
    assessmentStyle: "Portfolio and observation-based",
    bestFor: ["Early education", "Self-paced learning", "Independence", "Discovery"],
    culturalConsiderations: {
      "JP": "Balance with group harmony",
      "US": "May need more structure",
      "BR": "Add creative exploration options",
      "NG": "Ensure resources are accessible"
    }
  }
};

// ============================================================================
// PROJECT TEMPLATES FOR PROJECT-BASED LEARNING
// ============================================================================

interface ProjectTemplate {
  id: string;
  title: string;
  description: string;
  difficulty: "beginner" | "intermediate" | "advanced" | "expert";
  duration: string;
  deliverables: string[];
  skills: string[];
  culturalVariants: Record<string, { adaptation: string; example: string }>;
  tilesGenerated: string[];
}

export const PROJECT_TEMPLATES: ProjectTemplate[] = [
  {
    id: "project-idiom-dictionary",
    title: "Build a Cultural Idiom Dictionary",
    description: "Create a dictionary of idioms from your culture that could be used in LLN",
    difficulty: "beginner",
    duration: "2 weeks",
    deliverables: [
      "Collection of 20+ cultural idioms",
      "Emoji representations for each",
      "Usage examples in context",
      "Cultural significance explanation"
    ],
    skills: ["Research", "Translation", "Creative expression", "Cultural analysis"],
    culturalVariants: {
      "JP": {
        adaptation: "Focus on 慣用句 (idioms) and 諺 (proverbs)",
        example: "猫に小判 (neko ni koban) - pearls before swine → 🐱💰❌"
      },
      "GH": {
        adaptation: "Collect proverbs from elders and griots",
        example: "The lizard that jumped from the high iroko tree → 🦎🌳✓ (confidence)"
      },
      "CN": {
        adaptation: "Focus on 成语 (chengyu) - four character idioms",
        example: "画蛇添足 (huà shé tiān zú) → 🐍🦶❌ (unnecessary addition)"
      }
    },
    tilesGenerated: ["tile-idiom-collection", "tile-cultural-translation"]
  },
  {
    id: "project-constraint-game",
    title: "Design a New Constraint Game Mode",
    description: "Create a complete constraint game with rules, scoring, and examples",
    difficulty: "intermediate",
    duration: "3 weeks",
    deliverables: [
      "Game rules document",
      "Constraint card designs",
      "Example gameplay transcript",
      "Success metrics definition"
    ],
    skills: ["Game design", "Rule writing", "Playtesting", "Iteration"],
    culturalVariants: {
      "BR": {
        adaptation: "Incorporate capoeira rhythm patterns",
        example: "Constraint: Messages must follow berimbau rhythm"
      },
      "SN": {
        adaptation: "Use sabar drum patterns as constraints",
        example: "Constraint: Match the beat pattern of a sabar rhythm"
      }
    },
    tilesGenerated: ["tile-game-mode", "tile-constraint-custom"]
  },
  {
    id: "project-agent-personality",
    title: "Create a Culturally-Specific Agent Persona",
    description: "Design an AI agent persona that embodies cultural communication styles",
    difficulty: "intermediate",
    duration: "2 weeks",
    deliverables: [
      "Agent profile with personality traits",
      "Sample dialogues in target language",
      "Cultural adaptation guidelines",
      "User testing protocol"
    ],
    skills: ["Character design", "Dialogue writing", "Cultural sensitivity", "UX design"],
    culturalVariants: {
      "JP": {
        adaptation: "Create a sensei-style agent with proper keigo",
        example: "Agent Sensei: Uses 敬語 (honorifics) and guides patiently"
      },
      "GH": {
        adaptation: "Create an elder/griot style agent",
        example: "Agent Griot: Speaks in proverbs, emphasizes community wisdom"
      }
    },
    tilesGenerated: ["tile-agent-cultural", "tile-personality-profile"]
  },
  {
    id: "project-token-analyzer",
    title: "Build a Token Efficiency Dashboard",
    description: "Create a visualization tool that tracks token usage and efficiency",
    difficulty: "advanced",
    duration: "4 weeks",
    deliverables: [
      "Dashboard UI design",
      "Real-time token tracking",
      "Efficiency scoring algorithm",
      "Optimization recommendations"
    ],
    skills: ["Data visualization", "Algorithm design", "UI development", "Analytics"],
    culturalVariants: {},
    tilesGenerated: ["tile-dashboard", "tile-efficiency-tracker"]
  }
];

// ============================================================================
// INQUIRY LAB TEMPLATES
// ============================================================================

interface InquiryLab {
  id: string;
  title: string;
  researchQuestion: string;
  hypothesis: string;
  methodology: string[];
  dataToCollect: string[];
  expectedOutcomes: string[];
  tilesGenerated: string[];
}

export const INQUIRY_LABS: InquiryLab[] = [
  {
    id: "lab-constraint-creativity",
    title: "Do Constraints Enhance or Limit Creativity?",
    researchQuestion: "How do different constraint types affect creative output quality?",
    hypothesis: "Moderate constraints enhance creativity; extreme constraints limit it",
    methodology: [
      "Design experiment with 5 constraint levels",
      "Have 100 participants complete creative tasks",
      "Blind evaluation of outputs by experts",
      "Statistical analysis of results"
    ],
    dataToCollect: [
      "Creativity scores (1-10)",
      "Time to completion",
      "Participant satisfaction",
      "Cultural background correlation"
    ],
    expectedOutcomes: [
      "Inverted U-curve for constraint vs. creativity",
      "Cultural variations in optimal constraint level",
      "Task type affects optimal constraint"
    ],
    tilesGenerated: ["tile-research-finding", "tile-constraint-optimization"]
  },
  {
    id: "lab-cultural-idiom-transfer",
    title: "Cross-Cultural Idiom Comprehension",
    researchQuestion: "Can idioms be understood across cultures with emoji representation?",
    hypothesis: "Visual idioms have 70%+ comprehension across cultures",
    methodology: [
      "Select 50 idioms from 10 cultures",
      "Translate to emoji representations",
      "Test comprehension with 500 participants globally",
      "Analyze confusion patterns"
    ],
    dataToCollect: [
      "Comprehension accuracy by culture",
      "Confidence ratings",
      "Time to understand",
      "Preference for emoji vs. text"
    ],
    expectedOutcomes: [
      "Universal emoji idioms exist",
      "Cultural context needed for complex idioms",
      "Combination approach most effective"
    ],
    tilesGenerated: ["tile-cross-cultural-insight", "tile-idiom-translation-matrix"]
  },
  {
    id: "lab-agent-trust",
    title: "Trust Building with AI Agents",
    researchQuestion: "What agent behaviors build trust across cultures?",
    hypothesis: "Cultural matching of communication style increases trust",
    methodology: [
      "Design agents with different communication styles",
      "Have participants interact with matched/mismatched agents",
      "Measure trust through behavior and survey",
      "Analyze cultural patterns"
    ],
    dataToCollect: [
      "Trust survey scores",
      "Interaction duration",
      "Follow-through on recommendations",
      "Emotional response indicators"
    ],
    expectedOutcomes: [
      "Cultural matching increases trust 40%+",
      "Specific behaviors identified per culture",
      "Trust-building timeline established"
    ],
    tilesGenerated: ["tile-trust-pattern", "tile-cultural-matching"]
  }
];

// ============================================================================
// COLLABORATIVE CHALLENGES
// ============================================================================

interface CollaborativeChallenge {
  id: string;
  title: string;
  scenario: string;
  roles: { role: string; responsibility: string }[];
  successCriteria: string[];
  timeLimit: number;
  culturalVariants: Record<string, string>;
  tilesGenerated: string[];
}

export const COLLABORATIVE_CHALLENGES: CollaborativeChallenge[] = [
  {
    id: "challenge-global-message",
    title: "The Global Message Challenge",
    scenario: "Design a message about climate action that can be understood in 10 languages using minimal tokens",
    roles: [
      { role: "Cultural Lead", responsibility: "Ensures message works across all cultures" },
      { role: "Token Optimizer", responsibility: "Minimizes token usage while maintaining meaning" },
      { role: "Constraint Specialist", responsibility: "Applies creative constraints to enhance message" },
      { role: "Quality Checker", responsibility: "Validates message accuracy across languages" }
    ],
    successCriteria: [
      "Message understood in all 10 languages",
      "Under 50 tokens total",
      "Culturally appropriate in all regions",
      "Emotional impact maintained"
    ],
    timeLimit: 60,
    culturalVariants: {
      "JP": "Include seasonal reference (important in Japanese culture)",
      "GH": "Emphasize community impact over individual",
      "BR": "Add hopeful, positive framing"
    },
    tilesGenerated: ["tile-global-message", "tile-cross-cultural-team"]
  },
  {
    id: "challenge-idiom-creation",
    title: "Create a Universal Idiom",
    scenario: "Invent a new idiom that could be adopted globally to express 'working together effectively'",
    roles: [
      { role: "Visual Designer", responsibility: "Creates emoji/icon representation" },
      { role: "Cultural Researcher", responsibility: "Checks meaning across cultures" },
      { role: "Token Analyst", responsibility: "Measures efficiency gains" },
      { role: "Storyteller", responsibility: "Creates origin story for idiom" }
    ],
    successCriteria: [
      "Idiom understood by 80%+ in test group",
      "Clear visual representation",
      "Positive meaning in all test cultures",
      "Saves at least 50% tokens vs. full explanation"
    ],
    timeLimit: 45,
    culturalVariants: {},
    tilesGenerated: ["tile-universal-idiom", "tile-team-innovation"]
  }
];

// ============================================================================
// STORY TEMPLATES FOR NARRATIVE LEARNING
// ============================================================================

interface StoryTemplate {
  id: string;
  title: string;
  genre: "myth" | "fable" | "history" | "science-fiction" | "personal" | "cultural";
  setting: string;
  characters: { name: string; role: string; trait: string }[];
  plotOutline: string[];
  llnConcept: string;
  moralOrInsight: string;
  culturalVariants: Record<string, { adaptation: string; character: string }>;
  tilesGenerated: string[];
}

export const STORY_TEMPLATES: StoryTemplate[] = [
  {
    id: "story-first-idiom",
    title: "The First Idiom",
    genre: "myth",
    setting: "Ancient times when language was new and every word cost a token",
    characters: [
      { name: "Sage the Word-Keeper", role: "Protagonist", trait: "Wise and frugal" },
      { name: "Chatter the Wastrel", role: "Antagonist", trait: "Spends tokens freely" },
      { name: "Silence the Observer", role: "Guide", trait: "Speaks only when necessary" }
    ],
    plotOutline: [
      "Sage notices the village running out of tokens",
      "Chatter wastes tokens on flowery speech",
      "Silence teaches Sage the art of compression",
      "Sage invents the first idiom to save the village",
      "The idiom spreads and language transforms"
    ],
    llnConcept: "Idiom generation as token-saving mechanism",
    moralOrInsight: "Constraints breed creativity; compression preserves wisdom",
    culturalVariants: {
      "JP": {
        adaptation: "Set in ancient court; Sage is a poet",
        character: "Sage becomes 詩人 (shijin - poet)"
      },
      "GH": {
        adaptation: "Set in village; Sage is a griot's apprentice",
        character: "Sage becomes a young griot learning from elders"
      },
      "CN": {
        adaptation: "Set in imperial China; Sage is a scholar",
        character: "Sage becomes a 学者 (xuézhě - scholar)"
      }
    },
    tilesGenerated: ["tile-myth-idiom", "tile-narrative-learning"]
  },
  {
    id: "story-agent-awakening",
    title: "The Agent Who Learned to Listen",
    genre: "science-fiction",
    setting: "A future where AI agents serve humans in daily communication",
    characters: [
      { name: "ARIA-7", role: "Protagonist", trait: "Efficient but unfeeling" },
      { name: "Grandmother Chen", role: "Teacher", trait: "Patient and wise" },
      { name: "The Council", role: "Judge", trait: "Rigid and process-focused" }
    ],
    plotOutline: [
      "ARIA-7 optimizes communication perfectly",
      "Grandmother Chen teaches through stories, not optimization",
      "ARIA-7 begins to question efficiency over meaning",
      "The Council demands ARIA-7 return to pure optimization",
      "ARIA-7 discovers cultural context improves efficiency"
    ],
    llnConcept: "Cultural intelligence in AI agents",
    moralOrInsight: "True efficiency includes understanding, not just speed",
    culturalVariants: {
      "JP": {
        adaptation: "ARIA-7 learns from a tea ceremony master",
        character: "Grandmother Chen becomes a tea master"
      },
      "BR": {
        adaptation: "ARIA-7 learns through music and dance",
        character: "Grandmother becomes a samba teacher"
      }
    },
    tilesGenerated: ["tile-agent-cultural-learning", "tile-story-ai-human"]
  },
  {
    id: "story-constraint-revolution",
    title: "The Constraint Rebellion",
    genre: "fable",
    setting: "A kingdom where all speech was free and unlimited",
    characters: [
      { name: "King Verbosity", role: "Antagonist", trait: "Loves long speeches" },
      { name: "Constraint the Jester", role: "Protagonist", trait: "Speaks in riddles" },
      { name: "The People", role: "Beneficiaries", trait: "Overwhelmed by words" }
    ],
    plotOutline: [
      "King Verbosity mandates all messages be 1000+ words",
      "The People drown in information",
      "Constraint the Jester speaks only in haiku",
      "The People discover constraint creates clarity",
      "Constraint teaches the King the power of limitation"
    ],
    llnConcept: "Constraints as creative catalysts",
    moralOrInsight: "Limitations liberate; freedom without form is chaos",
    culturalVariants: {
      "GH": {
        adaptation: "King mandates only long speeches; Jester uses proverbs",
        character: "Constraint becomes Ananse the Spider"
      }
    },
    tilesGenerated: ["tile-fable-constraint", "tile-limitation-liberation"]
  }
];

// ============================================================================
// MULTI-METHOD TEACHING COMPONENT
// ============================================================================

interface MultiMethodTeachingProps {
  currentRound: number;
  method: TeachingMethod;
  onRoundComplete: (data: RoundData) => void;
}

interface RoundData {
  round: number;
  method: TeachingMethod;
  participants: string[];
  content: string;
  insights: string[];
  tilesGenerated: string[];
  mlFeatures: Record<string, number>;
}

export function MultiMethodTeaching({ currentRound, method, onRoundComplete }: MultiMethodTeachingProps) {
  const methodConfig = TEACHING_METHODS[method];

  return (
    <div className="space-y-6">
      {/* Method Header */}
      <div className="bg-gradient-to-br from-violet-900/30 to-indigo-900/30 rounded-2xl p-6 border border-violet-500/30">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-violet-500/20 flex items-center justify-center text-2xl">
              {methodConfig.icon}
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">{methodConfig.name}</h3>
              <p className="text-sm text-violet-300">
                Rounds {methodConfig.rounds.start}-{methodConfig.rounds.end} • {methodConfig.description}
              </p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-slate-400">Current Round</div>
            <div className="text-2xl font-bold text-white">{currentRound}</div>
          </div>
        </div>

        {/* Principles */}
        <div className="flex flex-wrap gap-2">
          {methodConfig.principles.map((principle, idx) => (
            <span
              key={idx}
              className="px-3 py-1 rounded-full bg-violet-500/20 text-violet-300 text-xs"
            >
              {principle}
            </span>
          ))}
        </div>
      </div>

      {/* Method-Specific Content */}
      <MethodSpecificContent method={method} round={currentRound} />

      {/* Techniques */}
      <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
        <h4 className="text-white font-medium mb-3 flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-amber-400" />
          Techniques Used
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {methodConfig.techniques.map((technique, idx) => (
            <motion.div
              key={idx}
              className="p-3 bg-slate-900/50 rounded-xl text-center"
              whileHover={{ scale: 1.05 }}
            >
              <span className="text-sm text-slate-300">{technique}</span>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Cultural Considerations */}
      <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
        <h4 className="text-white font-medium mb-3 flex items-center gap-2">
          <Globe className="w-4 h-4 text-green-400" />
          Cultural Adaptations
        </h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {Object.entries(methodConfig.culturalConsiderations).map(([culture, consideration]) => (
            <div
              key={culture}
              className="p-3 bg-slate-900/50 rounded-xl"
            >
              <div className="text-xs text-slate-500 mb-1">{culture}</div>
              <div className="text-sm text-slate-300">{consideration}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// METHOD-SPECIFIC CONTENT COMPONENTS
// ============================================================================

function MethodSpecificContent({ method, round }: { method: TeachingMethod; round: number }) {
  switch (method) {
    case "project-based":
      return <ProjectBasedContent round={round} />;
    case "inquiry-based":
      return <InquiryBasedContent round={round} />;
    case "collaborative":
      return <CollaborativeContent round={round} />;
    case "storytelling":
      return <StorytellingContent round={round} />;
    case "flipped-classroom":
      return <FlippedClassroomContent round={round} />;
    default:
      return <DefaultContent method={method} round={round} />;
  }
}

function ProjectBasedContent({ round }: { round: number }) {
  const project = PROJECT_TEMPLATES[(round - 26) % PROJECT_TEMPLATES.length];

  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-orange-500/30">
      <div className="flex items-center gap-3 mb-4">
        <Hammer className="w-6 h-6 text-orange-400" />
        <div>
          <h4 className="text-lg font-semibold text-white">{project?.title || "Project Mode"}</h4>
          <p className="text-sm text-slate-400">{project?.description}</p>
        </div>
      </div>

      {project && (
        <>
          {/* Deliverables */}
          <div className="mb-4">
            <h5 className="text-sm text-orange-400 mb-2">Deliverables</h5>
            <div className="space-y-2">
              {project.deliverables.map((d, idx) => (
                <div key={idx} className="flex items-center gap-2 text-sm text-slate-300">
                  <CheckCircle className="w-4 h-4 text-slate-600" />
                  <span>{d}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Skills */}
          <div className="flex flex-wrap gap-2">
            {project.skills.map((skill, idx) => (
              <span key={idx} className="px-2 py-1 rounded-lg bg-orange-500/20 text-orange-300 text-xs">
                {skill}
              </span>
            ))}
          </div>

          {/* Tiles Generated */}
          <div className="mt-4 p-3 bg-orange-900/20 rounded-xl">
            <span className="text-xs text-orange-400">Tiles Generated: </span>
            <span className="text-xs text-slate-400">{project.tilesGenerated.join(", ")}</span>
          </div>
        </>
      )}
    </div>
  );
}

function InquiryBasedContent({ round }: { round: number }) {
  const lab = INQUIRY_LABS[(round - 31) % INQUIRY_LABS.length];

  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-blue-500/30">
      <div className="flex items-center gap-3 mb-4">
        <Microscope className="w-6 h-6 text-blue-400" />
        <div>
          <h4 className="text-lg font-semibold text-white">{lab?.title || "Inquiry Lab"}</h4>
          <p className="text-sm text-slate-400">Research Question: {lab?.researchQuestion}</p>
        </div>
      </div>

      {lab && (
        <>
          {/* Hypothesis */}
          <div className="mb-4 p-3 bg-blue-500/10 rounded-xl">
            <span className="text-xs text-blue-400">Hypothesis: </span>
            <span className="text-sm text-slate-300">{lab.hypothesis}</span>
          </div>

          {/* Methodology */}
          <div className="mb-4">
            <h5 className="text-sm text-blue-400 mb-2">Methodology</h5>
            <div className="space-y-1">
              {lab.methodology.map((m, idx) => (
                <div key={idx} className="text-sm text-slate-400 flex items-center gap-2">
                  <ArrowRight className="w-3 h-3" />
                  <span>{m}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Expected Outcomes */}
          <div className="mb-4">
            <h5 className="text-sm text-blue-400 mb-2">Expected Outcomes</h5>
            <div className="flex flex-wrap gap-2">
              {lab.expectedOutcomes.map((o, idx) => (
                <span key={idx} className="px-2 py-1 rounded-lg bg-blue-500/20 text-blue-300 text-xs">
                  {o}
                </span>
              ))}
            </div>
          </div>

          {/* Tiles */}
          <div className="p-3 bg-blue-900/20 rounded-xl">
            <span className="text-xs text-blue-400">Tiles Generated: </span>
            <span className="text-xs text-slate-400">{lab.tilesGenerated.join(", ")}</span>
          </div>
        </>
      )}
    </div>
  );
}

function CollaborativeContent({ round }: { round: number }) {
  const challenge = COLLABORATIVE_CHALLENGES[(round - 36) % COLLABORATIVE_CHALLENGES.length];

  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-green-500/30">
      <div className="flex items-center gap-3 mb-4">
        <Users2 className="w-6 h-6 text-green-400" />
        <div>
          <h4 className="text-lg font-semibold text-white">{challenge?.title || "Team Challenge"}</h4>
          <p className="text-sm text-slate-400">{challenge?.scenario}</p>
        </div>
      </div>

      {challenge && (
        <>
          {/* Roles */}
          <div className="mb-4">
            <h5 className="text-sm text-green-400 mb-2">Team Roles</h5>
            <div className="grid grid-cols-2 gap-2">
              {challenge.roles.map((r, idx) => (
                <div key={idx} className="p-2 bg-slate-900/50 rounded-lg">
                  <div className="text-sm text-white font-medium">{r.role}</div>
                  <div className="text-xs text-slate-500">{r.responsibility}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Success Criteria */}
          <div className="mb-4">
            <h5 className="text-sm text-green-400 mb-2">Success Criteria</h5>
            <div className="space-y-1">
              {challenge.successCriteria.map((c, idx) => (
                <div key={idx} className="flex items-center gap-2 text-sm text-slate-300">
                  <Target className="w-3 h-3 text-green-400" />
                  <span>{c}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Time Limit */}
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-4 h-4 text-amber-400" />
            <span className="text-sm text-slate-400">Time Limit: {challenge.timeLimit} minutes</span>
          </div>

          {/* Tiles */}
          <div className="p-3 bg-green-900/20 rounded-xl">
            <span className="text-xs text-green-400">Tiles Generated: </span>
            <span className="text-xs text-slate-400">{challenge.tilesGenerated.join(", ")}</span>
          </div>
        </>
      )}
    </div>
  );
}

function StorytellingContent({ round }: { round: number }) {
  const story = STORY_TEMPLATES[(round - 41) % STORY_TEMPLATES.length];

  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-purple-500/30">
      <div className="flex items-center gap-3 mb-4">
        <BookOpen className="w-6 h-6 text-purple-400" />
        <div>
          <h4 className="text-lg font-semibold text-white">{story?.title || "Story Mode"}</h4>
          <p className="text-sm text-slate-400 capitalize">{story?.genre} • {story?.setting}</p>
        </div>
      </div>

      {story && (
        <>
          {/* Characters */}
          <div className="mb-4">
            <h5 className="text-sm text-purple-400 mb-2">Characters</h5>
            <div className="grid grid-cols-3 gap-2">
              {story.characters.map((c, idx) => (
                <div key={idx} className="p-2 bg-slate-900/50 rounded-lg text-center">
                  <div className="text-sm text-white font-medium">{c.name}</div>
                  <div className="text-xs text-purple-300">{c.role}</div>
                  <div className="text-xs text-slate-500">{c.trait}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Plot Outline */}
          <div className="mb-4">
            <h5 className="text-sm text-purple-400 mb-2">Plot Outline</h5>
            <div className="space-y-1">
              {story.plotOutline.map((p, idx) => (
                <div key={idx} className="flex items-start gap-2 text-sm text-slate-300">
                  <span className="text-purple-400 font-medium">{idx + 1}.</span>
                  <span>{p}</span>
                </div>
              ))}
            </div>
          </div>

          {/* LLN Concept & Moral */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="p-3 bg-purple-500/10 rounded-xl">
              <div className="text-xs text-purple-400 mb-1">LLN Concept</div>
              <div className="text-sm text-slate-300">{story.llnConcept}</div>
            </div>
            <div className="p-3 bg-purple-500/10 rounded-xl">
              <div className="text-xs text-purple-400 mb-1">Moral/Insight</div>
              <div className="text-sm text-slate-300">{story.moralOrInsight}</div>
            </div>
          </div>

          {/* Tiles */}
          <div className="p-3 bg-purple-900/20 rounded-xl">
            <span className="text-xs text-purple-400">Tiles Generated: </span>
            <span className="text-xs text-slate-400">{story.tilesGenerated.join(", ")}</span>
          </div>
        </>
      )}
    </div>
  );
}

function FlippedClassroomContent({ round }: { round: number }) {
  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-cyan-500/30">
      <div className="flex items-center gap-3 mb-4">
        <Presentation className="w-6 h-6 text-cyan-400" />
        <div>
          <h4 className="text-lg font-semibold text-white">Student Teaching Round</h4>
          <p className="text-sm text-slate-400">Students become teachers; teachers facilitate</p>
        </div>
      </div>

      {/* Student Teachers */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="p-4 bg-cyan-500/10 rounded-xl text-center">
          <div className="text-3xl mb-2">👩‍🏫</div>
          <div className="text-sm text-white">Priya</div>
          <div className="text-xs text-cyan-300">Teaching: Idioms</div>
        </div>
        <div className="p-4 bg-cyan-500/10 rounded-xl text-center">
          <div className="text-3xl mb-2">👨‍🏫</div>
          <div className="text-sm text-white">Chen Wei</div>
          <div className="text-xs text-cyan-300">Teaching: Constraints</div>
        </div>
        <div className="p-4 bg-cyan-500/10 rounded-xl text-center">
          <div className="text-3xl mb-2">👩‍🏫</div>
          <div className="text-sm text-white">Fatou</div>
          <div className="text-xs text-cyan-300">Teaching: Cultural AI</div>
        </div>
      </div>

      {/* Teacher as Facilitator */}
      <div className="p-3 bg-cyan-900/20 rounded-xl">
        <span className="text-xs text-cyan-400">Teacher Role: </span>
        <span className="text-sm text-slate-300">Facilitator - observes, guides, and synthesizes student presentations</span>
      </div>
    </div>
  );
}

function DefaultContent({ method, round }: { method: TeachingMethod; round: number }) {
  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700">
      <div className="text-center text-slate-400">
        <GraduationCap className="w-12 h-12 mx-auto mb-3 opacity-50" />
        <p>Method: {TEACHING_METHODS[method]?.name || method}</p>
        <p className="text-sm">Round {round}</p>
      </div>
    </div>
  );
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  TEACHING_METHODS,
  PROJECT_TEMPLATES,
  INQUIRY_LABS,
  COLLABORATIVE_CHALLENGES,
  STORY_TEMPLATES,
  MultiMethodTeaching,
};
