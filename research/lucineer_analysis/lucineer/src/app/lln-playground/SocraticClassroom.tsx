// ============================================================================
// LLN PLAYGROUND - SOCRATIC CLASSROOM SIMULATION FRAMEWORK
// 25 Rounds of Socratic Teaching with Diverse Students Worldwide
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
  XCircle,
  AlertCircle,
  ArrowRight,
  Star,
  Trophy,
  Target,
  Clock,
  Languages
} from "lucide-react";

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

interface Student {
  id: string;
  name: string;
  avatar: string;
  age: number;
  country: string;
  language: string;
  proficiency: "beginner" | "intermediate" | "advanced" | "expert";
  culturalContext: string;
  learningStyle: "visual" | "auditory" | "kinesthetic" | "reading";
  personality: "curious" | "analytical" | "creative" | "practical" | "social";
  questions: string[];
  misconceptions: string[];
}

interface Teacher {
  id: string;
  name: string;
  avatar: string;
  teachingStyle: "socratic" | "facilitator" | "mentor" | "challenger";
  expertise: string[];
  languages: string[];
  patience: number;
  adaptability: number;
}

interface DialogueTurn {
  speaker: "teacher" | "student";
  speakerId: string;
  content: string;
  type: "question" | "answer" | "insight" | "challenge" | "encouragement" | "correction";
  timestamp: number;
  targetStudent?: string;
  understanding: number; // 0-1
  languageUsed: string;
}

interface Topic {
  id: string;
  title: string;
  description: string;
  difficulty: "beginner" | "intermediate" | "advanced" | "expert";
  prerequisites: string[];
  keyConcepts: string[];
  commonMisconceptions: string[];
  analogies: Record<string, string>; // cultural context -> analogy
  tileRepresentation: TileDefinition;
}

interface TileDefinition {
  id: string;
  type: string;
  visual: string;
  behavior: string;
  connections: string[];
}

interface ClassroomSession {
  round: number;
  sessionType: "student-diverse" | "agent-to-agent" | "professional-group";
  teacher: Teacher;
  students: Student[];
  topic: Topic;
  dialogue: DialogueTurn[];
  insights: string[];
  tilesCreated: TileDefinition[];
  culturalAdaptations: string[];
  mlData: {
    understandingTrajectory: number[];
    engagementLevels: Record<string, number>;
    conceptMastery: Record<string, number>;
    culturalFactors: Record<string, number>;
  };
}

// ============================================================================
// STUDENT PERSONAS - DIVERSE GLOBAL CLASSROOM
// ============================================================================

export const DIVERSE_STUDENTS: Student[] = [
  // Young Learners (Ages 7-12)
  {
    id: "s1",
    name: "Yuki",
    avatar: "👧",
    age: 10,
    country: "JP",
    language: "ja",
    proficiency: "beginner",
    culturalContext: "Japanese - Values harmony and precision",
    learningStyle: "visual",
    personality: "curious",
    questions: ["どうしてエージェントは言葉を理解できるの？", "Are agents like robot friends?"],
    misconceptions: ["Agents are like humans inside computers"]
  },
  {
    id: "s2",
    name: "Kwame",
    avatar: "👦",
    age: 11,
    country: "GH",
    language: "en",
    proficiency: "beginner",
    culturalContext: "Ghanaian - Values storytelling and community",
    learningStyle: "auditory",
    personality: "social",
    questions: ["Can agents tell stories like my grandmother?", "Do agents have tribes?"],
    misconceptions: ["Agents know everything about Africa"]
  },
  {
    id: "s3",
    name: "Sofia",
    avatar: "👧",
    age: 9,
    country: "BR",
    language: "pt",
    proficiency: "beginner",
    culturalContext: "Brazilian - Values creativity and expression",
    learningStyle: "kinesthetic",
    personality: "creative",
    questions: ["Posso ensinar o agente a dançar?", "Can agents learn my games?"],
    misconceptions: ["Agents can only speak English"]
  },

  // Teens (Ages 13-18)
  {
    id: "s4",
    name: "Min-jun",
    avatar: "🧑",
    age: 16,
    country: "KR",
    language: "ko",
    proficiency: "intermediate",
    culturalContext: "Korean - Values competition and excellence",
    learningStyle: "reading",
    personality: "analytical",
    questions: ["토큰 효율성을 어떻게 최적화하나요?", "What's the optimal constraint strategy?"],
    misconceptions: ["More tokens always mean better results"]
  },
  {
    id: "s5",
    name: "Aisha",
    avatar: "👩",
    age: 17,
    country: "NG",
    language: "en",
    proficiency: "intermediate",
    culturalContext: "Nigerian - Values innovation and community impact",
    learningStyle: "practical",
    personality: "practical",
    questions: ["How can agents help my community?", "Can agents work offline?"],
    misconceptions: ["AI is only for rich countries"]
  },
  {
    id: "s6",
    name: "Lucas",
    avatar: "🧑",
    age: 15,
    country: "DE",
    language: "de",
    proficiency: "intermediate",
    culturalContext: "German - Values precision and systematic thinking",
    learningStyle: "analytical",
    personality: "analytical",
    questions: ["Wie funktioniert die Token-Berechnung?", "What's the mathematical model?"],
    misconceptions: ["Agents are purely statistical"]
  },

  // University Students
  {
    id: "s7",
    name: "Priya",
    avatar: "👩",
    age: 21,
    country: "IN",
    language: "en",
    proficiency: "advanced",
    culturalContext: "Indian - Values tradition and innovation balance",
    learningStyle: "reading",
    personality: "analytical",
    questions: ["How do idioms preserve cultural knowledge?", "Can agents learn Sanskrit patterns?"],
    misconceptions: ["Modern AI has no connection to ancient wisdom"]
  },
  {
    id: "s8",
    name: "Chen Wei",
    avatar: "👨",
    age: 22,
    country: "CN",
    language: "zh",
    proficiency: "advanced",
    culturalContext: "Chinese - Values scholarship and practical application",
    learningStyle: "visual",
    personality: "analytical",
    questions: ["成语如何在AI系统中应用？", "How do constraint systems compare to calligraphy rules?"],
    misconceptions: ["AI creativity is limited to Western concepts"]
  },
  {
    id: "s9",
    name: "Fatou",
    avatar: "👩",
    age: 20,
    country: "SN",
    language: "fr",
    proficiency: "intermediate",
    culturalContext: "Senegalese - Values oral tradition and creative expression",
    learningStyle: "auditory",
    personality: "creative",
    questions: ["Comment les agents peuvent-ils préserver les traditions orales?", "Can rhythm patterns become idioms?"],
    misconceptions: ["AI cannot understand non-written traditions"]
  },

  // Working Professionals
  {
    id: "s10",
    name: "Marcus",
    avatar: "👨",
    age: 35,
    country: "US",
    language: "en",
    proficiency: "expert",
    culturalContext: "American - Values innovation and speed",
    learningStyle: "practical",
    personality: "practical",
    questions: ["How can I integrate LLN into my production system?", "What's the ROI timeline?"],
    misconceptions: ["LLN is just another API wrapper"]
  },
  {
    id: "s11",
    name: "Dr. Okello",
    avatar: "👨",
    age: 45,
    country: "KE",
    language: "en",
    proficiency: "advanced",
    culturalContext: "Kenyan - Values community and practical impact",
    learningStyle: "kinesthetic",
    personality: "practical",
    questions: ["Can this help with agricultural decisions?", "How do we train agents in local languages?"],
    misconceptions: ["Complex AI requires massive resources"]
  },
  {
    id: "s12",
    name: "Yuki-san",
    avatar: "👵",
    age: 72,
    country: "JP",
    language: "ja",
    proficiency: "beginner",
    culturalContext: "Japanese Elder - Values patience and mastery",
    learningStyle: "visual",
    personality: "curious",
    questions: ["将棋のようなパターン認識はできますか？", "Is this like learning calligraphy?"],
    misconceptions: ["I'm too old to learn new technology"]
  },

  // Additional Diverse Students
  {
    id: "s13",
    name: "Ahmed",
    avatar: "👨",
    age: 28,
    country: "EG",
    language: "ar",
    proficiency: "intermediate",
    culturalContext: "Egyptian - Values history and innovation",
    learningStyle: "reading",
    personality: "analytical",
    questions: ["كيف يمكن للذكاء الاصطناعي الحفاظ على التراث؟", "Can agents understand hieroglyphics logic?"],
    misconceptions: ["AI is purely a Western invention"]
  },
  {
    id: "s14",
    name: "Maria",
    avatar: "👩",
    age: 55,
    country: "MX",
    language: "es",
    proficiency: "beginner",
    culturalContext: "Mexican - Values family and celebration",
    learningStyle: "social",
    personality: "social",
    questions: ["¿Pueden los agentes aprender recetas de familia?", "Can agents help preserve our traditions?"],
    misconceptions: ["AI will replace human creativity"]
  },
  {
    id: "s15",
    name: "Ibrahim",
    avatar: "👨",
    age: 30,
    country: "SA",
    language: "ar",
    proficiency: "intermediate",
    culturalContext: "Saudi - Values precision and hospitality",
    learningStyle: "analytical",
    personality: "analytical",
    questions: ["كيف تتعامل الوكلاء مع اللغة العربية؟", "How does tokenization work for Arabic?"],
    misconceptions: ["Arabic is too complex for AI"]
  }
];

// ============================================================================
// TEACHER PERSONAS
// ============================================================================

export const TEACHER_PERSONAS: Teacher[] = [
  {
    id: "t1",
    name: "Professor Sage",
    avatar: "🧙",
    teachingStyle: "socratic",
    expertise: ["AI fundamentals", "Cross-cultural communication", "Game theory"],
    languages: ["en", "es", "fr", "zh", "ja", "ar", "sw", "pt"],
    patience: 0.95,
    adaptability: 0.9
  },
  {
    id: "t2",
    name: "Dr. Ubuntu",
    avatar: "🌍",
    teachingStyle: "facilitator",
    expertise: ["Community learning", "African traditions", "Collaborative AI"],
    languages: ["en", "sw", "zu", "ha", "yo", "pt"],
    patience: 0.98,
    adaptability: 0.95
  },
  {
    id: "t3",
    name: "Sensei Harmony",
    avatar: "🎋",
    teachingStyle: "mentor",
    expertise: ["Japanese aesthetics", "Precision learning", "Mastery paths"],
    languages: ["ja", "en", "zh", "ko"],
    patience: 0.99,
    adaptability: 0.85
  },
  {
    id: "t4",
    name: "Coach Champion",
    avatar: "🏆",
    teachingStyle: "challenger",
    expertise: ["Competition dynamics", "Speed learning", "Gamification"],
    languages: ["en", "ko", "zh", "es"],
    patience: 0.7,
    adaptability: 0.95
  }
];

// ============================================================================
// TOPICS FOR SOCRATIC TEACHING
// ============================================================================

export const SOCRATIC_TOPICS: Topic[] = [
  {
    id: "topic-1",
    title: "What is an LLN Agent?",
    description: "Understanding AI agents as participants in communication networks",
    difficulty: "beginner",
    prerequisites: [],
    keyConcepts: ["Agent", "Role", "Communication", "Constraint"],
    commonMisconceptions: [
      "Agents are human-like",
      "Agents have feelings",
      "Agents know everything"
    ],
    analogies: {
      "JP": "Agents are like students in a calligraphy class - each has a role and follows rules",
      "NG": "Agents are like members of a village council - each voice matters",
      "CN": "Agents are like pieces on a Go board - strategic positions",
      "US": "Agents are like players on a sports team - different positions, same goal"
    },
    tileRepresentation: {
      id: "tile-agent-basic",
      type: "agent",
      visual: "🤖",
      behavior: "Participates in communication with assigned role",
      connections: ["role", "constraint", "message"]
    }
  },
  {
    id: "topic-2",
    title: "How Do Constraints Shape Communication?",
    description: "Exploring how limitations create creativity",
    difficulty: "intermediate",
    prerequisites: ["topic-1"],
    keyConcepts: ["Constraint", "Creativity", "Token efficiency", "Compression"],
    commonMisconceptions: [
      "Constraints only limit",
      "More freedom = better communication",
      "Constraints are punishments"
    ],
    analogies: {
      "JP": "Like haiku - 5-7-5 syllables create beauty through limitation",
      "SN": "Like drum patterns - rhythm constraints create music",
      "BR": "Like capoeira - rules within the game create art",
      "DE": "Like chess rules - constraints enable strategy"
    },
    tileRepresentation: {
      id: "tile-constraint",
      type: "constraint",
      visual: "🎭",
      behavior: "Applies rules to communication that shape output",
      connections: ["agent", "message", "idiom"]
    }
  },
  {
    id: "topic-3",
    title: "What Are Idioms and SMPbots?",
    description: "Understanding compressed communication patterns",
    difficulty: "intermediate",
    prerequisites: ["topic-1", "topic-2"],
    keyConcepts: ["Idiom", "Compression", "Seed", "SMPbot", "Token savings"],
    commonMisconceptions: [
      "Idioms are just emojis",
      "SMPbots are fixed forever",
      "Compression loses information"
    ],
    analogies: {
      "CN": "Like 成语 (chengyu) - four characters capture whole stories",
      "NG": "Like proverbs - one phrase carries generations of wisdom",
      "JP": "Like seasonal words in haiku - single word evokes whole season",
      "IN": "Like Sanskrit sutras - compressed knowledge"
    },
    tileRepresentation: {
      id: "tile-idiom",
      type: "idiom",
      visual: "💎",
      behavior: "Compressed communication pattern that saves tokens",
      connections: ["agent", "message", "seed"]
    }
  },
  {
    id: "topic-4",
    title: "How Does Token Economics Work?",
    description: "Understanding the currency of AI communication",
    difficulty: "advanced",
    prerequisites: ["topic-1", "topic-2", "topic-3"],
    keyConcepts: ["Token", "Efficiency", "Cost", "ROI", "Optimization"],
    commonMisconceptions: [
      "More tokens always better",
      "Token counting is simple",
      "Efficiency equals quality"
    ],
    analogies: {
      "KE": "Like M-Pesa credits - digital currency with real value",
      "JP": "Like ink in calligraphy - precious resource to use wisely",
      "US": "Like fuel efficiency - getting more from less",
      "DE": "Like energy conservation - efficient systems"
    },
    tileRepresentation: {
      id: "tile-token",
      type: "economics",
      visual: "🪙",
      behavior: "Tracks and optimizes communication cost",
      connections: ["message", "idiom", "constraint"]
    }
  },
  {
    id: "topic-5",
    title: "What Makes Cross-Cultural AI?",
    description: "Building AI that respects and learns from all cultures",
    difficulty: "advanced",
    prerequisites: ["topic-1", "topic-2", "topic-3", "topic-4"],
    keyConcepts: ["Culture", "Translation", "Adaptation", "Respect", "Diversity"],
    commonMisconceptions: [
      "AI is culturally neutral",
      "One approach fits all",
      "Translation equals understanding"
    ],
    analogies: {
      "ALL": "Like a good translator - understands meaning, not just words",
      "SN": "Like a griot - carries stories across generations and cultures",
      "IN": "Like a festival - universal celebration with local flavors"
    },
    tileRepresentation: {
      id: "tile-culture",
      type: "cultural",
      visual: "🌍",
      behavior: "Adapts communication to cultural context",
      connections: ["agent", "idiom", "constraint", "language"]
    }
  }
];

// ============================================================================
// SOCRATIC CLASSROOM COMPONENT
// ============================================================================

interface SocraticClassroomProps {
  round: number;
  sessionType: "student-diverse" | "agent-to-agent" | "professional-group";
  onSessionComplete: (session: ClassroomSession) => void;
}

export function SocraticClassroom({ round, sessionType, onSessionComplete }: SocraticClassroomProps) {
  return (
    <div className="space-y-6">
      {/* Classroom Header */}
      <div className="bg-gradient-to-br from-indigo-900/30 to-purple-900/30 rounded-2xl p-6 border border-indigo-500/30">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center">
              <GraduationCap className="w-6 h-6 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">Socratic Classroom</h3>
              <p className="text-sm text-indigo-300">Round {round} • {sessionType.replace("-", " ")}</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Globe className="w-4 h-4 text-green-400" />
              <span className="text-sm text-slate-400">15 Countries</span>
            </div>
            <div className="flex items-center gap-2">
              <Languages className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-slate-400">12 Languages</span>
            </div>
          </div>
        </div>
      </div>

      {/* Teacher Panel */}
      <TeacherPanel />

      {/* Students Grid */}
      <StudentsGrid students={DIVERSE_STUDENTS.slice(0, 8)} />

      {/* Dialogue Simulation */}
      <DialogueSimulation 
        round={round} 
        sessionType={sessionType}
        onComplete={onSessionComplete}
      />
    </div>
  );
}

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

function TeacherPanel() {
  const teacher = TEACHER_PERSONAS[0]; // Professor Sage

  return (
    <motion.div 
      className="bg-slate-800/50 rounded-2xl p-6 border border-amber-500/30"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <div className="flex items-start gap-4">
        <div className="text-5xl">{teacher.avatar}</div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="text-lg font-semibold text-amber-400">{teacher.name}</h4>
            <span className="px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-xs">
              {teacher.teachingStyle}
            </span>
          </div>
          <div className="flex flex-wrap gap-2 mb-3">
            {teacher.expertise.map(exp => (
              <span key={exp} className="px-2 py-1 rounded-lg bg-slate-700 text-slate-300 text-xs">
                {exp}
              </span>
            ))}
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <span className="text-xs text-slate-500">Languages:</span>
              {teacher.languages.slice(0, 6).map(lang => (
                <span key={lang} className="text-xs text-blue-400">{lang.toUpperCase()}</span>
              ))}
              {teacher.languages.length > 6 && (
                <span className="text-xs text-slate-500">+{teacher.languages.length - 6}</span>
              )}
            </div>
            <div className="flex items-center gap-1">
              <span className="text-xs text-slate-500">Patience:</span>
              <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                <div className="h-full bg-green-500" style={{ width: `${teacher.patience * 100}%` }} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}

function StudentsGrid({ students }: { students: Student[] }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      {students.map((student, idx) => (
        <motion.div
          key={student.id}
          className="bg-slate-800/50 rounded-xl p-4 border border-slate-700 hover:border-purple-500/50 transition-colors"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: idx * 0.05 }}
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="text-2xl">{student.avatar}</div>
            <div>
              <div className="text-white font-medium text-sm">{student.name}</div>
              <div className="text-xs text-slate-500">{student.country} • Age {student.age}</div>
            </div>
          </div>
          <div className="flex items-center gap-2 mb-2">
            <span className={`px-2 py-0.5 rounded text-xs ${
              student.proficiency === 'beginner' ? 'bg-green-500/20 text-green-400' :
              student.proficiency === 'intermediate' ? 'bg-yellow-500/20 text-yellow-400' :
              student.proficiency === 'advanced' ? 'bg-orange-500/20 text-orange-400' :
              'bg-red-500/20 text-red-400'
            }`}>
              {student.proficiency}
            </span>
            <span className="text-xs text-blue-400">{student.language.toUpperCase()}</span>
          </div>
          <div className="text-xs text-slate-400 line-clamp-2">
            {student.questions[0]}
          </div>
        </motion.div>
      ))}
    </div>
  );
}

interface DialogueSimulationProps {
  round: number;
  sessionType: "student-diverse" | "agent-to-agent" | "professional-group";
  onComplete: (session: ClassroomSession) => void;
}

function DialogueSimulation({ round, sessionType, onComplete }: DialogueSimulationProps) {
  return (
    <div className="bg-slate-800/50 rounded-2xl p-6 border border-purple-500/30">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-lg font-semibold text-white flex items-center gap-2">
          <MessageCircle className="w-5 h-5 text-purple-400" />
          Socratic Dialogue
        </h4>
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-slate-500" />
          <span className="text-sm text-slate-500">Round {round}/25</span>
        </div>
      </div>

      {/* Simulated Dialogue */}
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {/* Teacher Question */}
        <DialogueBubble
          speaker="teacher"
          name="Professor Sage"
          avatar="🧙"
          content="Yuki-san, you asked a wonderful question about how agents understand words. Let me ask everyone: when you learn calligraphy, what rules do you follow?"
          type="question"
          targetStudent="Yuki"
          language="mixed"
        />

        {/* Student Response */}
        <DialogueBubble
          speaker="student"
          name="Yuki"
          avatar="👧"
          content="書道では、筆の動きと形のルールがあります。(In calligraphy, we have rules for brush movement and form.)"
          type="answer"
          language="ja"
        />

        {/* Teacher Follow-up */}
        <DialogueBubble
          speaker="teacher"
          name="Professor Sage"
          avatar="🧙"
          content="Exactly! Now Kwame, in your grandmother's stories, are there rules for how stories are told?"
          type="question"
          targetStudent="Kwame"
          language="en"
        />

        {/* Student Response */}
        <DialogueBubble
          speaker="student"
          name="Kwame"
          avatar="👦"
          content="Yes! There is a rhythm, and the story must teach something. The griot knows which words to use for each occasion."
          type="answer"
          language="en"
        />

        {/* Teacher Synthesis */}
        <DialogueBubble
          speaker="teacher"
          name="Professor Sage"
          avatar="🧙"
          content="Beautiful! So Yuki's calligraphy rules and Kwame's storytelling rules are both... constraints! Agents work the same way. They have roles (like brush positions or storyteller roles) and constraints (like brush strokes or story rhythms). What happens when you break these rules?"
          type="insight"
          language="en"
        />

        {/* Multiple Student Responses */}
        <DialogueBubble
          speaker="student"
          name="Min-jun"
          avatar: "🧑"
          content="규칙을 어기면... 새로운 창의성이 생길 수도 있어요. (Breaking rules... can create new creativity.)"
          type="insight"
          language="ko"
        />

        <DialogueBubble
          speaker="student"
          name="Fatou"
          avatar="👩"
          content="Comme dans le jazz - on doit connaître les règles pour pouvoir les briser avec intention! (Like in jazz - you must know rules to break them with intention!)"
          type="insight"
          language="fr"
        />

        {/* Teacher Challenge */}
        <DialogueBubble
          speaker="teacher"
          name="Professor Sage"
          avatar="🧙"
          content="Fatou brings us to a key insight! Constraints don't limit creativity - they enable it. Marcus, you work in technology. How does this relate to your API design work?"
          type="challenge"
          targetStudent="Marcus"
          language="en"
        />

        {/* Professional Student Response */}
        <DialogueBubble
          speaker="student"
          name="Marcus"
          avatar="👨"
          content="APIs need constraints - rate limits, schemas, protocols. Without them, chaos. But good constraints enable developers to build amazing things. I see it now - LLN agents have 'API contracts' with each other!"
          type="insight"
          language="en"
        />

        {/* Celebration */}
        <DialogueBubble
          speaker="teacher"
          name="Professor Sage"
          avatar="🧙"
          content="🌟 That's the connection! Yuki's calligraphy, Kwame's stories, Min-jun's competition, Fatou's jazz, Marcus's APIs - all use constraints to create meaning. This is the essence of LLN: structured creativity across cultures and domains."
          type="encouragement"
          language="en"
        />
      </div>

      {/* Tile Creation */}
      <div className="mt-6 p-4 bg-purple-900/30 rounded-xl border border-purple-500/30">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-4 h-4 text-purple-400" />
          <span className="text-sm font-medium text-purple-300">Tile Created This Round</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 rounded-xl bg-purple-500/20 flex items-center justify-center text-3xl">
            🎯
          </div>
          <div>
            <h5 className="text-white font-medium">Constraint Creativity Tile</h5>
            <p className="text-sm text-slate-400">Transforms limitations into creative possibilities</p>
            <div className="flex gap-2 mt-2">
              <span className="text-xs px-2 py-1 rounded bg-purple-500/20 text-purple-300">constraint</span>
              <span className="text-xs px-2 py-1 rounded bg-blue-500/20 text-blue-300">creativity</span>
              <span className="text-xs px-2 py-1 rounded bg-green-500/20 text-green-300">cultural</span>
            </div>
          </div>
        </div>
      </div>

      {/* Action Button */}
      <motion.button
        className="w-full mt-4 py-3 rounded-xl bg-gradient-to-r from-purple-500 to-indigo-500 text-white font-medium flex items-center justify-center gap-2"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => {
          // Simulate session completion
          onComplete({
            round,
            sessionType,
            teacher: TEACHER_PERSONAS[0],
            students: DIVERSE_STUDENTS.slice(0, 8),
            topic: SOCRATIC_TOPICS[0],
            dialogue: [],
            insights: ["Constraints enable creativity", "Cultural patterns are universal", "API design mirrors constraint games"],
            tilesCreated: [{ id: "tile-1", type: "constraint", visual: "🎯", behavior: "Transform limitations to possibilities", connections: ["creativity", "culture"] }],
            culturalAdaptations: ["Japanese calligraphy analogy", "African storytelling connection", "Korean competition insight"],
            mlData: {
              understandingTrajectory: [0.3, 0.5, 0.7, 0.85, 0.9],
              engagementLevels: { "Yuki": 0.95, "Kwame": 0.88, "Min-jun": 0.92, "Fatou": 0.91, "Marcus": 0.85 },
              conceptMastery: { "constraints": 0.9, "creativity": 0.85, "cultural": 0.88 },
              culturalFactors: { "JP": 0.92, "GH": 0.88, "KR": 0.91, "SN": 0.89, "US": 0.87 }
            }
          });
        }}
      >
        Complete Round & Generate Tiles
        <ArrowRight className="w-4 h-4" />
      </motion.button>
    </div>
  );
}

interface DialogueBubbleProps {
  speaker: "teacher" | "student";
  name: string;
  avatar: string;
  content: string;
  type: "question" | "answer" | "insight" | "challenge" | "encouragement" | "correction";
  targetStudent?: string;
  language: string;
}

function DialogueBubble({ speaker, name, avatar, content, type, targetStudent, language }: DialogueBubbleProps) {
  const isTeacher = speaker === "teacher";
  
  const typeColors = {
    question: "border-blue-500/30 bg-blue-500/10",
    answer: "border-green-500/30 bg-green-500/10",
    insight: "border-purple-500/30 bg-purple-500/10",
    challenge: "border-orange-500/30 bg-orange-500/10",
    encouragement: "border-yellow-500/30 bg-yellow-500/10",
    correction: "border-red-500/30 bg-red-500/10"
  };

  return (
    <motion.div
      className={`flex gap-3 ${isTeacher ? "" : "flex-row-reverse"}`}
      initial={{ opacity: 0, x: isTeacher ? -20 : 20 }}
      animate={{ opacity: 1, x: 0 }}
    >
      <div className="text-2xl">{avatar}</div>
      <div className={`flex-1 p-4 rounded-xl border ${typeColors[type]}`}>
        <div className="flex items-center gap-2 mb-2">
          <span className={`font-medium text-sm ${isTeacher ? "text-amber-400" : "text-slate-300"}`}>
            {name}
          </span>
          <span className="text-xs px-2 py-0.5 rounded-full bg-slate-700 text-slate-400">
            {type}
          </span>
          {targetStudent && (
            <span className="text-xs text-blue-400">→ {targetStudent}</span>
          )}
          <span className="text-xs text-slate-500 ml-auto">{language}</span>
        </div>
        <p className="text-slate-200 text-sm leading-relaxed">{content}</p>
      </div>
    </motion.div>
  );
}

// ============================================================================
// AGENT-TO-AGENT CLASSROOM
// ============================================================================

export function AgentToAgentClassroom({ round }: { round: number }) {
  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-cyan-900/30 to-blue-900/30 rounded-2xl p-6 border border-cyan-500/30">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-cyan-500/20 flex items-center justify-center">
            <Brain className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Agent-to-Agent Teaching</h3>
            <p className="text-sm text-cyan-300">AI teachers learning from AI students</p>
          </div>
        </div>

        {/* Agent Participants */}
        <div className="grid grid-cols-4 gap-4">
          {[
            { name: "Teacher Bot", emoji: "🧠", role: "Socratic Instructor" },
            { name: "Student Alpha", emoji: "🤖", role: "Curious Learner" },
            { name: "Student Beta", emoji: "🤖", role: "Analytical Mind" },
            { name: "Student Gamma", emoji: "🤖", role: "Creative Explorer" }
          ].map((agent, idx) => (
            <motion.div
              key={agent.name}
              className="bg-slate-800/50 rounded-xl p-4 text-center border border-slate-700"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
            >
              <div className="text-3xl mb-2">{agent.emoji}</div>
              <div className="text-white font-medium text-sm">{agent.name}</div>
              <div className="text-xs text-slate-500">{agent.role}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// PROFESSIONAL GROUPS CLASSROOM
// ============================================================================

export function ProfessionalGroupsClassroom({ round }: { round: number }) {
  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-emerald-900/30 to-teal-900/30 rounded-2xl p-6 border border-emerald-500/30">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center">
            <Users className="w-6 h-6 text-emerald-400" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Professional Learning Groups</h3>
            <p className="text-sm text-emerald-300">Industry-specific AI education</p>
          </div>
        </div>

        {/* Professional Groups */}
        <div className="grid grid-cols-3 gap-4">
          {[
            { field: "Healthcare", emoji: "🏥", professionals: ["Dr. Aisha", "Nurse Chen", "Researcher Omar"] },
            { field: "Finance", emoji: "💰", professionals: ["Analyst Kim", "Trader Jane", "CFO Marcus"] },
            { field: "Education", emoji: "📚", professionals: ["Prof. Elena", "Teacher Yuki", "Principal Ade"] }
          ].map((group) => (
            <motion.div
              key={group.field}
              className="bg-slate-800/50 rounded-xl p-4 border border-slate-700"
              whileHover={{ scale: 1.02 }}
            >
              <div className="text-2xl mb-2">{group.emoji}</div>
              <h4 className="text-white font-medium mb-2">{group.field}</h4>
              <div className="space-y-1">
                {group.professionals.map(pro => (
                  <div key={pro} className="text-xs text-slate-400">{pro}</div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// EXPORTS
// ============================================================================

export default {
  SocraticClassroom,
  AgentToAgentClassroom,
  ProfessionalGroupsClassroom,
  DIVERSE_STUDENTS,
  TEACHER_PERSONAS,
  SOCRATIC_TOPICS
};
