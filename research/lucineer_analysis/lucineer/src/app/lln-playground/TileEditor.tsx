"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Puzzle,
  Play,
  Pause,
  RefreshCw,
  Copy,
  Download,
  Upload,
  Settings,
  ChevronRight,
  ChevronLeft,
  Plus,
  Trash2,
  GripVertical,
  Zap,
  MessageSquare,
  Users,
  Target,
  Clock,
  Sparkles,
  Brain,
  Music,
  Camera,
  Mic,
  Smartphone,
  Globe,
  Palette,
  BookOpen,
  Trophy,
  Star,
  Heart,
  Award,
} from "lucide-react";

// ============================================================================
// TILE TYPES - Synthesized from 15+ platforms
// ============================================================================

type TileCategory = 
  | "agent"      // LLN-specific: Agent commands
  | "constraint" // LLN-specific: Apply constraint
  | "idiom"      // LLN-specific: Use idiom
  | "sensing"    // Input sensing (OctoStudio)
  | "action"     // Do something
  | "control"    // If/then, loops
  | "event"      // When [condition] happens
  | "output";    // Hardware/output

interface TileBlock {
  id: string;
  type: TileCategory;
  subType: string;
  label: string;
  icon: string;
  color: string;
  parameters: TileParameter[];
  connected: {
    next: string | null;
    branches: { condition: string; target: string }[];
  };
  position: { x: number; y: number };
}

interface TileParameter {
  id: string;
  name: string;
  type: "string" | "number" | "dropdown" | "agent" | "idiom" | "constraint" | "sensor";
  value: any;
  options?: string[];
}

// ============================================================================
// TILE LIBRARY - Pre-defined tiles from platform synthesis
// ============================================================================

const TILE_LIBRARY: Record<TileCategory, Omit<TileBlock, "id" | "connected" | "position">[]> = {
  agent: [
    { type: "agent", subType: "create", label: "Create Agent", icon: "🤖", color: "#10B981", parameters: [
      { id: "name", name: "Name", type: "string", value: "NewAgent" },
      { id: "role", name: "Role", type: "dropdown", value: "actor", options: ["actor", "guesser", "judge", "helper"] },
    ]},
    { type: "agent", subType: "speak", label: "Agent Speaks", icon: "💬", color: "#8B5CF6", parameters: [
      { id: "message", name: "Message", type: "string", value: "" },
      { id: "constraint", name: "Constraint", type: "constraint", value: "" },
    ]},
    { type: "agent", subType: "think", label: "Agent Thinks", icon: "🧠", color: "#EC4899", parameters: [
      { id: "prompt", name: "Prompt", type: "string", value: "" },
      { id: "tokens", name: "Max Tokens", type: "number", value: 100 },
    ]},
    { type: "agent", subType: "guess", label: "Agent Guesses", icon: "🎯", color: "#F59E0B", parameters: [
      { id: "target", name: "Target Word", type: "string", value: "" },
    ]},
  ],
  
  constraint: [
    { type: "constraint", subType: "apply", label: "Apply Constraint", icon: "🎭", color: "#EF4444", parameters: [
      { id: "constraintType", name: "Type", type: "dropdown", value: "rhyme", 
        options: ["rhyme", "haiku", "emoji-only", "no-letter", "negative", "roast", "pirate", "shakespeare"] },
    ]},
    { type: "constraint", subType: "remove", label: "Remove Constraint", icon: "❌", color: "#6B7280", parameters: [
      { id: "constraintType", name: "Type", type: "dropdown", value: "rhyme", 
        options: ["rhyme", "haiku", "emoji-only", "no-letter", "negative", "roast"] },
    ]},
    { type: "constraint", subType: "random", label: "Random Constraint", icon: "🎲", color: "#8B5CF6", parameters: [
      { id: "difficulty", name: "Difficulty", type: "dropdown", value: "beginner", 
        options: ["beginner", "intermediate", "advanced"] },
    ]},
  ],
  
  idiom: [
    { type: "idiom", subType: "use", label: "Use Idiom", icon: "💎", color: "#F59E0B", parameters: [
      { id: "idiom", name: "Idiom", type: "idiom", value: "" },
    ]},
    { type: "idiom", subType: "create", label: "Create Idiom", icon: "✨", color: "#EC4899", parameters: [
      { id: "shorthand", name: "Shorthand", type: "string", value: "" },
      { id: "meaning", name: "Meaning", type: "string", value: "" },
    ]},
    { type: "idiom", subType: "share", label: "Share Idiom", icon: "📤", color: "#10B981", parameters: [
      { id: "idiom", name: "Idiom", type: "idiom", value: "" },
    ]},
  ],
  
  sensing: [
    { type: "sensing", subType: "tilt", label: "On Tilt", icon: "📱", color: "#3B82F6", parameters: [
      { id: "direction", name: "Direction", type: "dropdown", value: "any", 
        options: ["any", "left", "right", "up", "down"] },
    ]},
    { type: "sensing", subType: "shake", label: "On Shake", icon: "📳", color: "#3B82F6", parameters: [] },
    { type: "sensing", subType: "camera", label: "On Photo", icon: "📷", color: "#3B82F6", parameters: [
      { id: "saveAs", name: "Save As", type: "string", value: "photo" },
    ]},
    { type: "sensing", subType: "mic", label: "On Sound", icon: "🎤", color: "#3B82F6", parameters: [
      { id: "threshold", name: "Threshold", type: "number", value: 50 },
    ]},
    { type: "sensing", subType: "location", label: "On Location", icon: "📍", color: "#3B82F6", parameters: [
      { id: "radius", name: "Radius (m)", type: "number", value: 100 },
    ]},
  ],
  
  event: [
    { type: "event", subType: "start", label: "When Started", icon: "🚩", color: "#22C55E", parameters: [] },
    { type: "event", subType: "tap", label: "When Tapped", icon: "👆", color: "#22C55E", parameters: [] },
    { type: "event", subType: "message", label: "When Message Received", icon: "📨", color: "#22C55E", parameters: [
      { id: "messageType", name: "Type", type: "string", value: "" },
    ]},
    { type: "event", subType: "timer", label: "Every", icon: "⏱️", color: "#22C55E", parameters: [
      { id: "seconds", name: "Seconds", type: "number", value: 1 },
    ]},
  ],
  
  action: [
    { type: "action", subType: "say", label: "Say", icon: "💬", color: "#F59E0B", parameters: [
      { id: "text", name: "Text", type: "string", value: "" },
    ]},
    { type: "action", subType: "wait", label: "Wait", icon: "⏳", color: "#6B7280", parameters: [
      { id: "seconds", name: "Seconds", type: "number", value: 1 },
    ]},
    { type: "action", subType: "playSound", label: "Play Sound", icon: "🔊", color: "#EC4899", parameters: [
      { id: "sound", name: "Sound", type: "dropdown", value: "pop", 
        options: ["pop", "click", "chime", "celebration", "error"] },
    ]},
    { type: "action", subType: "vibrate", label: "Vibrate", icon: "📳", color: "#6366F1", parameters: [] },
  ],
  
  control: [
    { type: "control", subType: "if", label: "If", icon: "❓", color: "#F97316", parameters: [
      { id: "condition", name: "Condition", type: "string", value: "" },
    ]},
    { type: "control", subType: "ifElse", label: "If/Else", icon: "🔀", color: "#F97316", parameters: [
      { id: "condition", name: "Condition", type: "string", value: "" },
    ]},
    { type: "control", subType: "loop", label: "Repeat", icon: "🔄", color: "#F97316", parameters: [
      { id: "times", name: "Times", type: "number", value: 10 },
    ]},
    { type: "control", subType: "forever", label: "Forever", icon: "♾️", color: "#F97316", parameters: [] },
    { type: "control", subType: "stop", label: "Stop", icon: "🛑", color: "#EF4444", parameters: [] },
  ],
  
  output: [
    { type: "output", subType: "display", label: "Display", icon: "📺", color: "#6366F1", parameters: [
      { id: "content", name: "Content", type: "string", value: "" },
    ]},
    { type: "output", subType: "led", label: "LED Pattern", icon: "💡", color: "#6366F1", parameters: [
      { id: "pattern", name: "Pattern", type: "dropdown", value: "smile", 
        options: ["smile", "heart", "star", "x", "check"] },
    ]},
    { type: "output", subType: "notification", label: "Notify", icon: "🔔", color: "#6366F1", parameters: [
      { id: "title", name: "Title", type: "string", value: "" },
      { id: "body", name: "Body", type: "string", value: "" },
    ]},
  ],
};

// ============================================================================
// CULTURAL THEMES
// ============================================================================

const CULTURAL_THEMES = {
  default: {
    name: "Default",
    colors: { primary: "#8B5CF6", secondary: "#EC4899", accent: "#10B981" },
    fonts: { display: "Inter", body: "Inter" },
    icons: { agent: "🤖", constraint: "🎭", idiom: "💎" },
  },
  japanese: {
    name: "日本語",
    colors: { primary: "#DC2626", secondary: "#F59E0B", accent: "#10B981" },
    fonts: { display: "Noto Sans JP", body: "Noto Sans JP" },
    icons: { agent: "🤖", constraint: "🎭", idiom: "🗾" },
  },
  swahili: {
    name: "Kiswahili",
    colors: { primary: "#059669", secondary: "#DC2626", accent: "#000000" },
    fonts: { display: "Inter", body: "Inter" },
    icons: { agent: "🤖", constraint: "🎭", idiom: "🌍" },
  },
  chinese: {
    name: "中文",
    colors: { primary: "#DC2626", secondary: "#FCD34D", accent: "#000000" },
    fonts: { display: "Noto Sans SC", body: "Noto Sans SC" },
    icons: { agent: "🤖", constraint: "🎭", idiom: "🧧" },
  },
};

// ============================================================================
// MAIN TILE EDITOR COMPONENT
// ============================================================================

export function TileEditor() {
  const [tiles, setTiles] = useState<TileBlock[]>([]);
  const [selectedTile, setSelectedTile] = useState<string | null>(null);
  const [activeCategory, setActiveCategory] = useState<TileCategory>("agent");
  const [isRunning, setIsRunning] = useState(false);
  const [culturalTheme, setCulturalTheme] = useState<keyof typeof CULTURAL_THEMES>("default");
  
  // Add a tile to the workspace
  const addTile = useCallback((category: TileCategory, index: number) => {
    const template = TILE_LIBRARY[category][index];
    const newTile: TileBlock = {
      id: `tile_${Date.now()}`,
      ...template,
      parameters: template.parameters.map(p => ({ ...p })),
      connected: { next: null, branches: [] },
      position: { 
        x: tiles.length > 0 ? tiles[tiles.length - 1].position.x + 180 : 50, 
        y: 200 
      },
    };
    setTiles(prev => [...prev, newTile]);
  }, [tiles]);
  
  // Remove a tile
  const removeTile = useCallback((id: string) => {
    setTiles(prev => prev.filter(t => t.id !== id));
    if (selectedTile === id) setSelectedTile(null);
  }, [selectedTile]);
  
  // Update tile parameter
  const updateParameter = useCallback((tileId: string, paramId: string, value: any) => {
    setTiles(prev => prev.map(tile => {
      if (tile.id !== tileId) return tile;
      return {
        ...tile,
        parameters: tile.parameters.map(p => 
          p.id === paramId ? { ...p, value } : p
        ),
      };
    }));
  }, []);
  
  // Connect tiles
  const connectTiles = useCallback((fromId: string, toId: string) => {
    setTiles(prev => prev.map(tile => {
      if (tile.id === fromId) {
        return { ...tile, connected: { ...tile.connected, next: toId } };
      }
      return tile;
    }));
  }, []);
  
  // Run the program
  const runProgram = useCallback(async () => {
    setIsRunning(true);
    
    // Find starting tile (event type)
    let currentTile = tiles.find(t => t.type === "event");
    
    while (currentTile && isRunning) {
      // Highlight current tile
      setSelectedTile(currentTile.id);
      
      // Simulate execution
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Move to next tile
      if (currentTile.connected.next) {
        currentTile = tiles.find(t => t.id === currentTile!.connected.next);
      } else {
        break;
      }
    }
    
    setIsRunning(false);
    setSelectedTile(null);
  }, [tiles, isRunning]);
  
  // Export tiles as JSON
  const exportTiles = useCallback(() => {
    const json = JSON.stringify(tiles, null, 2);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `lln-program-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }, [tiles]);
  
  const theme = CULTURAL_THEMES[culturalTheme];
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-950 to-slate-900 flex">
      {/* Tile Palette */}
      <div className="w-64 bg-slate-800/50 border-r border-slate-700/50 p-4 overflow-y-auto">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Puzzle className="w-5 h-5 text-purple-400" />
          Tile Library
        </h2>
        
        {/* Category Tabs */}
        <div className="flex flex-wrap gap-1 mb-4">
          {(Object.keys(TILE_LIBRARY) as TileCategory[]).map(cat => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-2 py-1 rounded text-xs transition-colors ${
                activeCategory === cat 
                  ? 'bg-purple-500/30 text-purple-300' 
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
        
        {/* Tiles in Category */}
        <div className="space-y-2">
          {TILE_LIBRARY[activeCategory].map((tile, idx) => (
            <motion.button
              key={`${activeCategory}-${idx}`}
              onClick={() => addTile(activeCategory, idx)}
              className="w-full p-3 rounded-xl border border-slate-700/50 bg-slate-900/50 hover:border-purple-500/50 transition-all text-left"
              style={{ borderLeftColor: tile.color, borderLeftWidth: 4 }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <div className="flex items-center gap-2">
                <span className="text-xl">{tile.icon}</span>
                <span className="text-white text-sm">{tile.label}</span>
              </div>
            </motion.button>
          ))}
        </div>
      </div>
      
      {/* Main Workspace */}
      <div className="flex-1 flex flex-col">
        {/* Toolbar */}
        <div className="bg-slate-800/50 border-b border-slate-700/50 p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <motion.button
              onClick={runProgram}
              disabled={tiles.length === 0}
              className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 ${
                isRunning 
                  ? 'bg-red-500/20 text-red-400' 
                  : 'bg-green-500/20 text-green-400'
              }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isRunning ? (
                <>
                  <Pause className="w-4 h-4" />
                  Stop
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  Run
                </>
              )}
            </motion.button>
            
            <button
              onClick={() => setTiles([])}
              className="px-3 py-2 rounded-lg bg-slate-700/50 text-slate-400 hover:text-white"
            >
              <Trash2 className="w-4 h-4" />
            </button>
            
            <button
              onClick={exportTiles}
              className="px-3 py-2 rounded-lg bg-slate-700/50 text-slate-400 hover:text-white"
            >
              <Download className="w-4 h-4" />
            </button>
          </div>
          
          {/* Cultural Theme Selector */}
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-purple-400" />
            <select
              value={culturalTheme}
              onChange={(e) => setCulturalTheme(e.target.value as keyof typeof CULTURAL_THEMES)}
              className="bg-slate-700/50 text-white rounded-lg px-3 py-1.5 text-sm"
            >
              {Object.entries(CULTURAL_THEMES).map(([key, value]) => (
                <option key={key} value={key}>{value.name}</option>
              ))}
            </select>
          </div>
        </div>
        
        {/* Workspace Canvas */}
        <div className="flex-1 p-8 overflow-auto">
          {tiles.length === 0 ? (
            <div className="h-full flex items-center justify-center text-slate-500">
              <div className="text-center">
                <Puzzle className="w-16 h-16 mx-auto mb-4 opacity-30" />
                <p className="text-lg">Drag tiles from the library to build your LLN program</p>
                <p className="text-sm mt-2">Start with an Event tile, then add Agents, Constraints, and Actions</p>
              </div>
            </div>
          ) : (
            <div className="relative min-h-[600px]">
              {/* Connection Lines */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none">
                {tiles.map(tile => 
                  tile.connected.next && (
                    <line
                      key={`line-${tile.id}`}
                      x1={tile.position.x + 160}
                      y1={tile.position.y + 40}
                      x2={tiles.find(t => t.id === tile.connected.next)?.position.x || 0}
                      y2={tiles.find(t => t.id === tile.connected.next)?.position.y + 40 || 0}
                      stroke="#8B5CF6"
                      strokeWidth="2"
                      strokeDasharray="4"
                    />
                  )
                )}
              </svg>
              
              {/* Tiles */}
              <AnimatePresence>
                {tiles.map((tile, idx) => (
                  <motion.div
                    key={tile.id}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    className={`absolute p-4 rounded-xl border-2 cursor-pointer ${
                      selectedTile === tile.id 
                        ? 'border-purple-500 ring-2 ring-purple-500/30' 
                        : 'border-slate-700'
                    } ${isRunning && selectedTile === tile.id ? 'ring-4 ring-green-500/50' : ''}`}
                    style={{ 
                      left: tile.position.x, 
                      top: tile.position.y,
                      backgroundColor: tile.color + '20',
                      borderColor: tile.color,
                    }}
                    onClick={() => setSelectedTile(tile.id)}
                    drag
                    dragMomentum={false}
                    onDragEnd={(_, info) => {
                      setTiles(prev => prev.map(t => 
                        t.id === tile.id 
                          ? { ...t, position: { x: tile.position.x + info.offset.x, y: tile.position.y + info.offset.y } }
                          : t
                      ));
                    }}
                  >
                    <div className="flex items-center gap-3">
                      <GripVertical className="w-4 h-4 text-slate-500" />
                      <span className="text-2xl">{tile.icon}</span>
                      <span className="text-white font-medium">{tile.label}</span>
                      <button
                        onClick={(e) => { e.stopPropagation(); removeTile(tile.id); }}
                        className="ml-2 p-1 rounded hover:bg-red-500/20 text-slate-400 hover:text-red-400"
                      >
                        <Trash2 className="w-3 h-3" />
                      </button>
                    </div>
                    
                    {/* Parameters */}
                    {tile.parameters.length > 0 && (
                      <div className="mt-3 space-y-2">
                        {tile.parameters.map(param => (
                          <div key={param.id} className="flex items-center gap-2">
                            <span className="text-xs text-slate-400">{param.name}:</span>
                            {param.type === "dropdown" ? (
                              <select
                                value={param.value}
                                onChange={(e) => updateParameter(tile.id, param.id, e.target.value)}
                                className="bg-slate-800 text-white text-xs rounded px-2 py-1"
                              >
                                {param.options?.map(opt => (
                                  <option key={opt} value={opt}>{opt}</option>
                                ))}
                              </select>
                            ) : param.type === "number" ? (
                              <input
                                type="number"
                                value={param.value}
                                onChange={(e) => updateParameter(tile.id, param.id, Number(e.target.value))}
                                className="bg-slate-800 text-white text-xs rounded px-2 py-1 w-16"
                              />
                            ) : (
                              <input
                                type="text"
                                value={param.value}
                                onChange={(e) => updateParameter(tile.id, param.id, e.target.value)}
                                className="bg-slate-800 text-white text-xs rounded px-2 py-1 w-24"
                                placeholder={param.name}
                              />
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {/* Connection Point */}
                    <div 
                      className="absolute right-0 top-1/2 -translate-y-1/2 translate-x-1/2 w-4 h-4 rounded-full bg-purple-500 border-2 border-white cursor-pointer"
                      onClick={(e) => {
                        e.stopPropagation();
                        // Find next tile to connect
                        const nextTile = tiles.find(t => 
                          t.id !== tile.id && 
                          !tiles.some(other => other.connected.next === t.id)
                        );
                        if (nextTile) {
                          connectTiles(tile.id, nextTile.id);
                        }
                      }}
                    />
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>
        
        {/* Token Counter */}
        <div className="bg-slate-800/50 border-t border-slate-700/50 p-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              <span className="text-white">Tiles: {tiles.length}</span>
            </div>
            <div className="flex items-center gap-2">
              <Target className="w-4 h-4 text-green-400" />
              <span className="text-white">Connections: {tiles.filter(t => t.connected.next).length}</span>
            </div>
          </div>
          <div className="text-sm text-slate-400">
            Built with 💜 from ScratchJr, Scratch, Kodable, Tynker, OctoStudio + 10 more platforms
          </div>
        </div>
      </div>
    </div>
  );
}

export default TileEditor;
