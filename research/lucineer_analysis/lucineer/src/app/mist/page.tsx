"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import Image from "next/image";
import { motion, AnimatePresence } from "framer-motion";
import {
  Dog,
  Sheep,
  Home,
  TreePine,
  Sun,
  Moon,
  CloudRain,
  Snowflake,
  MessageCircle,
  Heart,
  Star,
  Award,
  ArrowRight,
  Play,
  Volume2,
  VolumeX,
  HelpCircle,
  Sparkles,
  Target,
  Users,
  BookOpen,
  Brain,
  Zap,
} from "lucide-react";

// ============================================================================
// MIST: THE TALE OF A SHEEPDOG PUPPY
// A Voxel Farm World for Young Learners
// ============================================================================

// Game constants
const LEVELS = {
  APPRENTICE: 0,    // Learning the trade
  JOURNEYMAN: 1,    // Training puppies
  MASTER: 2,        // Managing trainers
  ELDER: 3,         // Wisdom council
};

const SEASONS = {
  SPRING: { name: "Spring", icon: Sparkles, color: "text-green-400" },
  SUMMER: { name: "Summer", icon: Sun, color: "text-yellow-400" },
  AUTUMN: { name: "Autumn", icon: TreePine, color: "text-orange-400" },
  WINTER: { name: "Winter", icon: Snowflake, color: "text-blue-300" },
};

// Alpha Dog teachings - progressive revelation
const TEACHINGS = {
  // Level 0 - First discoveries
  IDENTITY: [
    { reveal: "You are a dog. A special kind of dog.", insight: "self-awareness" },
    { reveal: "You live in a kennel with many other dogs.", insight: "community" },
    { reveal: "This is a farm. Farms have animals.", insight: "environment" },
    { reveal: "The animals are called sheep. We help the farmer with them.", insight: "purpose" },
  ],
  SHEEP: [
    { reveal: "Sheep are gentle. They follow each other.", insight: "flocking" },
    { reveal: "Sheep eat grass. We guide them to good grass.", insight: "guidance" },
    { reveal: "When sheep are scared, they run together.", insight: "herd-behavior" },
  ],
  RAMS: [
    { reveal: "Not all sheep are the same. Some are different.", insight: "diversity" },
    { reveal: "Rams are sheep, but bigger. They have curved horns.", insight: "variation" },
    { reveal: "Rams can be stubborn. They need patience, not force.", insight: "patience" },
  ],
  WORK: [
    { reveal: "Every dog on this farm has a job.", insight: "trade" },
    { reveal: "My job is to teach you. Your job is to learn.", insight: "mentorship" },
    { reveal: "Work is how we help the farm family.", insight: "contribution" },
    { reveal: "Good work takes time. You are just beginning.", insight: "patience" },
  ],
  FAMILY: [
    { reveal: "Your mother was a great working dog.", insight: "lineage" },
    { reveal: "Her mother before her. Many generations.", insight: "heritage" },
    { reveal: "Each generation learns from the one before.", insight: "knowledge-transfer" },
    { reveal: "Someday, you will teach your own puppies.", insight: "legacy" },
  ],
};

// Voxel Grid Component
function VoxelGrid({ world, playerPos, onMove }: { 
  world: string[][]; 
  playerPos: { x: number; y: number };
  onMove: (dx: number, dy: number) => void;
}) {
  const CELL_SIZE = 40;
  
  const getCellContent = (cell: string) => {
    switch (cell) {
      case "G": return { bg: "bg-green-600", label: "🌿" };
      case "F": return { bg: "bg-amber-700", label: "🌾" };
      case "W": return { bg: "bg-blue-400", label: "💧" };
      case "T": return { bg: "bg-green-800", label: "🌳" };
      case "B": return { bg: "bg-red-800", label: "🏠" };
      case "S": return { bg: "bg-gray-100", label: "🐑" };
      case "K": return { bg: "bg-amber-600", label: "🐕" };
      default: return { bg: "bg-green-500", label: "" };
    }
  };

  return (
    <div className="relative inline-block">
      <div 
        className="grid gap-0.5 bg-green-900/50 p-2 rounded-xl border-2 border-green-800"
        style={{ 
          gridTemplateColumns: `repeat(${world[0]?.length || 8}, ${CELL_SIZE}px)` 
        }}
      >
        {world.map((row, y) =>
          row.map((cell, x) => {
            const content = getCellContent(cell);
            const isPlayer = playerPos.x === x && playerPos.y === y;
            
            return (
              <motion.div
                key={`${x}-${y}`}
                className={`${content.bg} rounded-sm flex items-center justify-center text-lg relative`}
                style={{ width: CELL_SIZE, height: CELL_SIZE }}
                whileHover={{ scale: 1.05 }}
                onClick={() => onMove(x - playerPos.x, y - playerPos.y)}
              >
                {isPlayer ? (
                  <motion.div
                    className="text-2xl"
                    animate={{ y: [0, -3, 0] }}
                    transition={{ duration: 0.5, repeat: Infinity }}
                  >
                    🐕
                  </motion.div>
                ) : (
                  content.label
                )}
              </motion.div>
            );
          })
        )}
      </div>
    </div>
  );
}

// Alpha Dog Dialogue Component
function AlphaDogDialogue({ 
  teaching, 
  onAcknowledge, 
  isVisible 
}: { 
  teaching: { reveal: string; insight: string } | null;
  onAcknowledge: () => void;
  isVisible: boolean;
}) {
  if (!teaching || !isVisible) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 50 }}
        className="fixed bottom-24 left-1/2 -translate-x-1/2 w-full max-w-2xl px-4 z-50"
      >
        <div className="bg-amber-900/95 backdrop-blur-sm rounded-2xl border-2 border-amber-600 p-6 shadow-2xl">
          {/* Alpha Dog Portrait */}
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 rounded-full bg-amber-600 flex items-center justify-center text-3xl border-2 border-amber-400">
              🐕
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <span className="font-bold text-amber-200">Elder Bark</span>
                <span className="text-xs bg-amber-700 px-2 py-0.5 rounded-full text-amber-200">Alpha Dog</span>
              </div>
              <p className="text-amber-50 text-lg leading-relaxed mb-4">
                "{teaching.reveal}"
              </p>
              <div className="flex items-center justify-between">
                <span className="text-xs text-amber-400 italic">
                  💡 Insight: {teaching.insight}
                </span>
                <button
                  onClick={onAcknowledge}
                  className="px-4 py-2 bg-amber-600 hover:bg-amber-500 rounded-lg text-amber-100 font-medium transition-colors flex items-center gap-2"
                >
                  I understand
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}

// Progress Tracker
function ProgressTracker({ 
  discoveries, 
  totalDiscoveries,
  level 
}: { 
  discoveries: string[];
  totalDiscoveries: number;
  level: number;
}) {
  const levelNames = ["Apprentice", "Journeyman", "Master", "Elder"];
  
  return (
    <div className="bg-card/80 backdrop-blur-sm rounded-xl border border-border p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold flex items-center gap-2">
          <Award className="w-4 h-4 text-amber-400" />
          Progress
        </h3>
        <span className="text-xs bg-amber-600/20 text-amber-400 px-2 py-1 rounded-full">
          Level {level}: {levelNames[level]}
        </span>
      </div>
      
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">Discoveries</span>
          <span className="font-mono text-primary">{discoveries.length}/{totalDiscoveries}</span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-primary to-amber-400"
            initial={{ width: 0 }}
            animate={{ width: `${(discoveries.length / totalDiscoveries) * 100}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
        
        {discoveries.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {discoveries.slice(-5).map((d, i) => (
              <span key={i} className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded">
                {d}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// Parent Layer Info (shown on hover/click for adults)
function ParentLayer({ visible }: { visible: boolean }) {
  if (!visible) return null;
  
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed top-20 right-4 w-80 bg-purple-900/90 backdrop-blur-sm rounded-xl border border-purple-500 p-4 z-40"
    >
      <div className="flex items-center gap-2 mb-3">
        <Brain className="w-4 h-4 text-purple-300" />
        <span className="text-sm font-medium text-purple-200">Parent Layer: AI Concepts</span>
      </div>
      
      <div className="space-y-3 text-sm text-purple-100">
        <div className="p-2 bg-purple-800/50 rounded-lg">
          <strong className="text-purple-300">Tabula Rosa:</strong>
          <p className="text-xs mt-1">Your child is experiencing what it's like to be a blank slate AI model, learning only from its "teacher" (the Alpha Dog).</p>
        </div>
        
        <div className="p-2 bg-purple-800/50 rounded-lg">
          <strong className="text-purple-300">Knowledge Distillation:</strong>
          <p className="text-xs mt-1">Each generation of working dogs represents how AI knowledge transfers - parent models teaching child models.</p>
        </div>
        
        <div className="p-2 bg-purple-800/50 rounded-lg">
          <strong className="text-purple-300">Progressive Revelation:</strong>
          <p className="text-xs mt-1">The game reveals complexity gradually - just like training specialized AI models (rams vs sheep = edge cases).</p>
        </div>
      </div>
    </motion.div>
  );
}

// Main Game Component
export default function MistGame() {
  // Game state
  const [level, setLevel] = useState(LEVELS.APPRENTICE);
  const [season, setSeason] = useState("SPRING");
  const [discoveries, setDiscoveries] = useState<string[]>([]);
  const [currentTeaching, setCurrentTeaching] = useState<{ reveal: string; insight: string } | null>(null);
  const [showDialogue, setShowDialogue] = useState(false);
  const [teachingIndex, setTeachingIndex] = useState(0);
  const [currentTopic, setCurrentTopic] = useState<keyof typeof TEACHINGS>("IDENTITY");
  const [showParentLayer, setShowParentLayer] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [playerPos, setPlayerPos] = useState({ x: 4, y: 4 });
  
  // Simple world map
  const [world] = useState([
    ["T", "T", "G", "G", "G", "G", "G", "T"],
    ["T", "G", "G", "S", "S", "G", "G", "T"],
    ["G", "G", "G", "S", "S", "G", "F", "F"],
    ["G", "S", "S", "G", "G", "G", "F", "F"],
    ["G", "S", "S", "G", "K", "G", "G", "G"],
    ["G", "G", "G", "G", "G", "G", "B", "B"],
    ["T", "G", "W", "W", "G", "G", "B", "B"],
    ["T", "T", "G", "G", "G", "T", "T", "T"],
  ]);

  // Calculate total discoveries
  const totalDiscoveries = Object.values(TEACHINGS).reduce((sum, t) => sum + t.length, 0);

  // Handle movement
  const handleMove = useCallback((dx: number, dy: number) => {
    const newX = Math.max(0, Math.min(world[0].length - 1, playerPos.x + dx));
    const newY = Math.max(0, Math.min(world.length - 1, playerPos.y + dy));
    
    const cell = world[newY]?.[newX];
    
    // Check for discoveries
    if (cell === "S" && !discoveries.includes("sheep")) {
      setCurrentTopic("SHEEP");
      setTeachingIndex(0);
      setCurrentTeaching(TEACHINGS.SHEEP[0]);
      setShowDialogue(true);
      setDiscoveries(prev => [...prev, "sheep"]);
    }
    
    setPlayerPos({ x: newX, y: newY });
  }, [playerPos, world, discoveries]);

  // Keyboard controls
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case "ArrowUp":
        case "w":
          handleMove(0, -1);
          break;
        case "ArrowDown":
        case "s":
          handleMove(0, 1);
          break;
        case "ArrowLeft":
        case "a":
          handleMove(-1, 0);
          break;
        case "ArrowRight":
        case "d":
          handleMove(1, 0);
          break;
      }
    };
    
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleMove]);

  // Handle teaching acknowledgment
  const handleAcknowledge = () => {
    setShowDialogue(false);
    
    // Get next teaching
    const topicTeachings = TEACHINGS[currentTopic];
    const nextIndex = teachingIndex + 1;
    
    if (nextIndex < topicTeachings.length) {
      setTimeout(() => {
        setTeachingIndex(nextIndex);
        setCurrentTeaching(topicTeachings[nextIndex]);
        setShowDialogue(true);
      }, 1000);
    }
  };

  // Start first teaching
  useEffect(() => {
    if (discoveries.length === 0) {
      setTimeout(() => {
        setCurrentTeaching(TEACHINGS.IDENTITY[0]);
        setShowDialogue(true);
        setDiscoveries(["identity"]);
      }, 1500);
    }
  }, []);

  return (
    <div className="animated-gradient-bg min-h-screen">
      {/* Header */}
      <section className="pt-20 pb-4 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-between"
          >
            <div className="flex items-center gap-4">
              <Link href="/" className="text-muted-foreground hover:text-foreground transition-colors">
                ← Back to Platform
              </Link>
            </div>
            
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowParentLayer(!showParentLayer)}
                className={`p-2 rounded-lg transition-colors ${
                  showParentLayer ? "bg-purple-600 text-white" : "bg-card hover:bg-muted"
                }`}
                title="Toggle Parent Layer (AI Learning Concepts)"
              >
                <Brain className="w-5 h-5" />
              </button>
              <button
                onClick={() => setSoundEnabled(!soundEnabled)}
                className="p-2 rounded-lg bg-card hover:bg-muted transition-colors"
              >
                {soundEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
              </button>
              <button
                className="p-2 rounded-lg bg-card hover:bg-muted transition-colors"
                title="Help"
              >
                <HelpCircle className="w-5 h-5" />
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Game Title */}
      <section className="px-4 pb-6">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <h1 className="text-3xl sm:text-4xl font-bold mb-2">
              <span className="text-amber-400">Mist</span>
              <span className="text-muted-foreground text-xl ml-2">
                Tale of a Sheepdog Puppy
              </span>
            </h1>
            <p className="text-muted-foreground">
              A voxel farm world where you learn to be a working dog
            </p>
          </motion.div>
        </div>
      </section>

      {/* Main Game Area */}
      <section className="px-4 pb-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            
            {/* Left Panel - Story/Context */}
            <div className="space-y-4">
              <div className="bg-card/80 backdrop-blur-sm rounded-xl border border-border p-4">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-amber-400" />
                  Your Story
                </h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  You are a young puppy in a kennel of working dogs. 
                  The farm is vast and full of things to discover. 
                  Elder Bark, the Alpha Dog, will teach you everything.
                </p>
                
                <div className="mt-4 p-3 bg-amber-900/20 rounded-lg border border-amber-700/30">
                  <p className="text-xs text-amber-200 italic">
                    "Every master was once an apprentice. Every teacher was once a student."
                  </p>
                  <p className="text-xs text-amber-400 mt-1">— Elder Bark</p>
                </div>
              </div>
              
              {/* Season Indicator */}
              <div className="bg-card/80 backdrop-blur-sm rounded-xl border border-border p-4">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <Sun className="w-4 h-4 text-yellow-400" />
                  Season
                </h3>
                <div className="flex gap-2">
                  {Object.entries(SEASONS).map(([key, s]) => (
                    <button
                      key={key}
                      onClick={() => setSeason(key)}
                      className={`flex-1 p-2 rounded-lg text-center transition-all ${
                        season === key
                          ? `${s.color} bg-current/10 border border-current`
                          : "bg-muted/30 border border-border"
                      }`}
                    >
                      <s.icon className="w-4 h-4 mx-auto" />
                      <span className="text-xs mt-1 block">{s.name}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Center - Game World */}
            <div className="lg:col-span-2">
              <div className="bg-gradient-to-b from-green-900/30 to-amber-900/20 rounded-2xl border border-green-700/30 p-6">
                {/* World Title */}
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold flex items-center gap-2">
                    <TreePine className="w-4 h-4 text-green-400" />
                    Farm World
                  </h3>
                  <span className="text-xs text-muted-foreground">
                    Use Arrow Keys or WASD to move
                  </span>
                </div>
                
                {/* Voxel Grid */}
                <div className="flex justify-center">
                  <VoxelGrid 
                    world={world} 
                    playerPos={playerPos}
                    onMove={handleMove}
                  />
                </div>
                
                {/* Legend */}
                <div className="mt-4 flex flex-wrap justify-center gap-4 text-xs text-muted-foreground">
                  <span>🌿 Grass</span>
                  <span>🌾 Field</span>
                  <span>💧 Water</span>
                  <span>🌳 Tree</span>
                  <span>🏠 Barn</span>
                  <span>🐑 Sheep</span>
                  <span>🐕 Kennel</span>
                </div>
                
                {/* Mobile Controls */}
                <div className="mt-4 grid grid-cols-3 gap-2 max-w-[150px] mx-auto lg:hidden">
                  <div />
                  <button
                    onClick={() => handleMove(0, -1)}
                    className="p-3 bg-card rounded-lg active:bg-primary/20"
                  >
                    ↑
                  </button>
                  <div />
                  <button
                    onClick={() => handleMove(-1, 0)}
                    className="p-3 bg-card rounded-lg active:bg-primary/20"
                  >
                    ←
                  </button>
                  <button
                    onClick={() => handleMove(0, 1)}
                    className="p-3 bg-card rounded-lg active:bg-primary/20"
                  >
                    ↓
                  </button>
                  <button
                    onClick={() => handleMove(1, 0)}
                    className="p-3 bg-card rounded-lg active:bg-primary/20"
                  >
                    →
                  </button>
                </div>
              </div>
            </div>

            {/* Right Panel - Progress */}
            <div className="space-y-4">
              <ProgressTracker
                discoveries={discoveries}
                totalDiscoveries={totalDiscoveries}
                level={level}
              />
              
              {/* Current Objectives */}
              <div className="bg-card/80 backdrop-blur-sm rounded-xl border border-border p-4">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <Target className="w-4 h-4 text-blue-400" />
                  Current Task
                </h3>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
                    <span>Explore the farm</span>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <div className="w-2 h-2 rounded-full bg-muted" />
                    <span>Find the sheep</span>
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <div className="w-2 h-2 rounded-full bg-muted" />
                    <span>Learn from Elder Bark</span>
                  </div>
                </div>
              </div>
              
              {/* Quick Stats */}
              <div className="bg-card/80 backdrop-blur-sm rounded-xl border border-border p-4">
                <h3 className="font-semibold mb-3 flex items-center gap-2">
                  <Zap className="w-4 h-4 text-yellow-400" />
                  Stats
                </h3>
                <div className="grid grid-cols-2 gap-3 text-center">
                  <div className="p-2 bg-muted/30 rounded-lg">
                    <div className="text-xl font-bold text-amber-400">0</div>
                    <div className="text-xs text-muted-foreground">Sheep Herded</div>
                  </div>
                  <div className="p-2 bg-muted/30 rounded-lg">
                    <div className="text-xl font-bold text-blue-400">0</div>
                    <div className="text-xs text-muted-foreground">Rams Met</div>
                  </div>
                  <div className="p-2 bg-muted/30 rounded-lg">
                    <div className="text-xl font-bold text-green-400">0</div>
                    <div className="text-xs text-muted-foreground">Puppies Trained</div>
                  </div>
                  <div className="p-2 bg-muted/30 rounded-lg">
                    <div className="text-xl font-bold text-purple-400">0</div>
                    <div className="text-xs text-muted-foreground">Wisdom Points</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Alpha Dog Dialogue */}
      <AlphaDogDialogue
        teaching={currentTeaching}
        onAcknowledge={handleAcknowledge}
        isVisible={showDialogue}
      />

      {/* Parent Layer Overlay */}
      <ParentLayer visible={showParentLayer} />

      {/* Bottom Info */}
      <section className="py-8 px-4 bg-card/50 border-t border-border">
        <div className="max-w-4xl mx-auto text-center">
          <h3 className="font-semibold mb-4 flex items-center justify-center gap-2">
            <Users className="w-4 h-4 text-purple-400" />
            For Parents & Young Learners
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-muted-foreground">
            <div className="p-4 bg-muted/30 rounded-lg text-left">
              <h4 className="font-medium text-foreground mb-2">🐕 For Kids</h4>
              <p>
                You're a puppy learning to be a farm dog! Explore, discover sheep, 
                and listen to Elder Bark's wisdom. Every master was once an apprentice.
              </p>
            </div>
            <div className="p-4 bg-purple-900/20 rounded-lg text-left border border-purple-700/30">
              <h4 className="font-medium text-purple-300 mb-2">🧠 For Parents</h4>
              <p>
                This game teaches AI concepts through metaphor: knowledge distillation, 
                progressive learning, and specialization - all wrapped in a charming farm story.
              </p>
            </div>
          </div>
          
          <div className="mt-6 flex flex-wrap justify-center gap-4">
            <Link
              href="/tabula-rosa"
              className="text-sm text-purple-400 hover:text-purple-300 transition-colors"
            >
              Learn about Tabula Rosa →
            </Link>
            <Link
              href="/learning"
              className="text-sm text-primary hover:text-primary/80 transition-colors"
            >
              More Learning Games →
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
