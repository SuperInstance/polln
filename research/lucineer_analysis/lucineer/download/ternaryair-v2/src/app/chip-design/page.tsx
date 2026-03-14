"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import {
  Cpu, Box, Layers, Globe, Code, Download, ArrowRight, Play, Pause,
  RotateCcw, ZoomIn, ZoomOut, Move, Settings, MessageCircle, Send,
  ChevronRight, Lightbulb, Target, Zap, HardDrive, Terminal, FileText,
  Check, AlertTriangle, Info, Sparkles, Microscope
} from "lucide-react";

// Voxel types
const VOXEL_TYPES = {
  EMPTY: { color: 'transparent', name: 'Empty' },
  GATE_AND: { color: '#3b82f6', name: 'AND Gate' },
  GATE_OR: { color: '#8b5cf6', name: 'OR Gate' },
  GATE_NOT: { color: '#ef4444', name: 'NOT Gate' },
  GATE_XOR: { color: '#f59e0b', name: 'XOR Gate' },
  WIRE: { color: '#22c55e', name: 'Wire' },
  INPUT: { color: '#06b6d4', name: 'Input' },
  OUTPUT: { color: '#ec4899', name: 'Output' },
  MEMORY: { color: '#6366f1', name: 'Memory' },
  POWER: { color: '#fbbf24', name: 'Power' },
};

// Lucineer conversation states
type AbstractionLayer = 'vision' | 'architecture' | 'hardware' | 'layout' | 'model' | 'chip' | 'eda';

const LAYER_NAMES: Record<AbstractionLayer, string> = {
  vision: "Use Case Vision",
  architecture: "System Architecture",
  hardware: "Hardware Selection",
  layout: "Board Layout",
  model: "Model Selection",
  chip: "Intra-Chip Design",
  eda: "EDA Export",
};

// Sample conversation flow
const sampleConversation = [
  { role: 'user', content: 'I want to design a smart downrigger for fishing in Sitka, Alaska' },
  { role: 'lucineer', content: "Exciting project! Sitka has unique underwater terrain. I'll load the Navionics charts for the area. What fish species are you targeting?" },
  { role: 'user', content: 'King salmon, mainly. I need depth control and maybe sonar integration.' },
  { role: 'lucineer', content: "King salmon typically run 50-200ft deep. For depth control, you'll need:\n• Depth sensor (MS5837 - $8)\n• MCU (ESP32-C3 - $2)\n• Motor driver (A4988 - $2)\n\nWith sonar, we'd add a transducer interface. What's your target price point?" },
  { role: 'user', content: 'Around $75 for the electronics, not counting the downrigger itself.' },
  { role: 'lucineer', content: "Perfect! That gives us room for a nice setup. Let me generate a rough architecture:\n\n```\nSensors → MCU → Motor\n   ↓         ↓\nBLE ←→ Phone App\n```\n\nI'm pulling up the underwater terrain for Sitka Sound to help visualize deployment scenarios. Would you like me to generate a 3D bottom simulation?" },
];

export default function ChipDesignPage() {
  // Voxel grid state
  const [gridSize] = useState({ x: 8, y: 8, z: 4 });
  const [voxels, setVoxels] = useState<Map<string, keyof typeof VOXEL_TYPES>>(new Map());
  const [selectedType, setSelectedType] = useState<keyof typeof VOXEL_TYPES>('GATE_AND');
  const [rotation, setRotation] = useState({ x: 30, y: -45 });
  const [zoom, setZoom] = useState(1);
  const [isPlaying, setIsPlaying] = useState(false);
  
  // Lucineer chat state
  const [messages, setMessages] = useState(sampleConversation);
  const [inputValue, setInputValue] = useState('');
  const [currentLayer, setCurrentLayer] = useState<AbstractionLayer>('architecture');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Project state
  const [projectName, setProjectName] = useState("Sitka Smart Downrigger");
  const [isDragging, setIsDragging] = useState(false);
  const [lastMousePos, setLastMousePos] = useState({ x: 0, y: 0 });

  // Auto-scroll chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Handle mouse rotation
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setLastMousePos({ x: e.clientX, y: e.clientY });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    const deltaX = e.clientX - lastMousePos.x;
    const deltaY = e.clientY - lastMousePos.y;
    setRotation(prev => ({
      x: Math.max(-90, Math.min(90, prev.x + deltaY * 0.5)),
      y: prev.y + deltaX * 0.5,
    }));
    setLastMousePos({ x: e.clientX, y: e.clientY });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Place voxel
  const placeVoxel = (x: number, y: number, z: number) => {
    const key = `${x},${y},${z}`;
    setVoxels(prev => {
      const newVoxels = new Map(prev);
      if (newVoxels.get(key) === selectedType) {
        newVoxels.delete(key);
      } else {
        newVoxels.set(key, selectedType);
      }
      return newVoxels;
    });
  };

  // Send message to Lucineer
  const handleSend = () => {
    if (!inputValue.trim()) return;
    
    setMessages(prev => [...prev, { role: 'user', content: inputValue }]);
    
    // Simulate Lucineer response
    setTimeout(() => {
      const responses = [
        "Good question! Let me think through the tradeoffs...",
        "Based on your requirements, I'd suggest adding a low-power mode for battery life.",
        "I've updated the architecture diagram. Check the voxel view to see component placement.",
        "For that use case, we could use a BitNet model at Int4 quantization - only 200KB!",
      ];
      setMessages(prev => [...prev, { 
        role: 'lucineer', 
        content: responses[Math.floor(Math.random() * responses.length)] 
      }]);
    }, 1000);
    
    setInputValue('');
  };

  // Render simple voxel (CSS-based)
  const renderVoxel = (x: number, y: number, z: number) => {
    const key = `${x},${y},${z}`;
    const type = voxels.get(key) || 'EMPTY';
    if (type === 'EMPTY') return null;
    
    const { color } = VOXEL_TYPES[type];
    const size = 30 * zoom;
    const offsetX = (x - z) * size * 0.7;
    const offsetY = (y * size * 0.8) - (x + z) * size * 0.3;
    
    return (
      <div
        key={key}
        className="absolute cursor-pointer transition-all duration-150 hover:brightness-125"
        style={{
          left: `calc(50% + ${offsetX}px)`,
          top: `calc(50% + ${offsetY}px)`,
          width: size,
          height: size,
          backgroundColor: color,
          transform: `rotateX(60deg) rotateZ(45deg)`,
          boxShadow: `
            inset -${size/4}px -${size/4}px 0 rgba(0,0,0,0.3),
            inset ${size/4}px ${size/4}px 0 rgba(255,255,255,0.2),
            ${size/8}px ${size/8}px 0 rgba(0,0,0,0.5)
          `,
        }}
        onClick={() => placeVoxel(x, y, z)}
      />
    );
  };

  return (
    <div className="animated-bg min-h-screen pt-20 pb-8">
      <div className="max-w-[1800px] mx-auto px-4 sm:px-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                <Microscope className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold">Chip Design Studio</h1>
                <p className="text-sm text-gray-500">with Lucineer AI Co-Inventor</p>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="px-4 py-2 bg-dark-700/50 rounded-lg border border-dark-600">
              <span className="text-xs text-gray-500">Current Layer:</span>
              <span className="ml-2 text-green-400 font-medium">{LAYER_NAMES[currentLayer]}</span>
            </div>
            <Link
              href="/downloads"
              className="flex items-center gap-2 px-4 py-2 bg-green-500/10 text-green-400 rounded-lg hover:bg-green-500/20 transition-colors"
            >
              <Download className="w-4 h-4" />
              Export
            </Link>
          </div>
        </div>

        {/* Main Layout: Editor + Chat */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
          {/* Left: Voxel Editor + Tools */}
          <div className="xl:col-span-2 space-y-4">
            {/* Toolbar */}
            <div className="bg-dark-800/80 backdrop-blur-sm rounded-xl border border-dark-600 p-4">
              <div className="flex flex-wrap items-center gap-4">
                {/* Component Selector */}
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">Components:</span>
                  <div className="flex gap-1">
                    {Object.entries(VOXEL_TYPES).slice(1).map(([key, value]) => (
                      <button
                        key={key}
                        onClick={() => setSelectedType(key as keyof typeof VOXEL_TYPES)}
                        className={`w-8 h-8 rounded-lg transition-all ${
                          selectedType === key 
                            ? 'ring-2 ring-white ring-offset-2 ring-offset-dark-800' 
                            : 'hover:scale-110'
                        }`}
                        style={{ backgroundColor: value.color }}
                        title={value.name}
                      />
                    ))}
                  </div>
                </div>
                
                <div className="h-6 w-px bg-dark-600" />
                
                {/* View Controls */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setZoom(z => Math.min(2, z + 0.1))}
                    className="p-2 bg-dark-700 hover:bg-dark-600 rounded-lg"
                  >
                    <ZoomIn className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setZoom(z => Math.max(0.5, z - 0.1))}
                    className="p-2 bg-dark-700 hover:bg-dark-600 rounded-lg"
                  >
                    <ZoomOut className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => { setRotation({ x: 30, y: -45 }); setZoom(1); }}
                    className="p-2 bg-dark-700 hover:bg-dark-600 rounded-lg"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>
                </div>
                
                <div className="h-6 w-px bg-dark-600" />
                
                {/* Simulation Controls */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setIsPlaying(!isPlaying)}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-lg ${
                      isPlaying 
                        ? 'bg-green-500/20 text-green-400' 
                        : 'bg-dark-700 hover:bg-dark-600'
                    }`}
                  >
                    {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    {isPlaying ? 'Running' : 'Simulate'}
                  </button>
                </div>
              </div>
            </div>

            {/* Voxel Canvas */}
            <div 
              className="bg-dark-800/80 backdrop-blur-sm rounded-xl border border-dark-600 overflow-hidden"
              style={{ height: '500px' }}
            >
              <div className="h-full flex">
                {/* 3D View */}
                <div 
                  className="flex-1 relative overflow-hidden cursor-grab active:cursor-grabbing"
                  onMouseDown={handleMouseDown}
                  onMouseMove={handleMouseMove}
                  onMouseUp={handleMouseUp}
                  onMouseLeave={handleMouseUp}
                  style={{
                    perspective: '1000px',
                  }}
                >
                  <div 
                    className="absolute inset-0 flex items-center justify-center"
                    style={{
                      transform: `rotateX(${rotation.x}deg) rotateY(${rotation.y}deg)`,
                      transformStyle: 'preserve-3d',
                    }}
                  >
                    {/* Render grid */}
                    {Array.from({ length: gridSize.z }).map((_, z) =>
                      Array.from({ length: gridSize.y }).map((_, y) =>
                        Array.from({ length: gridSize.x }).map((_, x) =>
                          renderVoxel(x, y, z)
                        )
                      )
                    )}
                    
                    {/* Grid floor */}
                    <div 
                      className="absolute border border-dark-500/30"
                      style={{
                        width: gridSize.x * 30 * zoom,
                        height: gridSize.z * 30 * zoom,
                        transform: 'rotateX(90deg) translateZ(-10px)',
                        background: 'linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px)',
                        backgroundSize: `${30 * zoom}px ${30 * zoom}px`,
                      }}
                    />
                  </div>
                  
                  {/* Instructions overlay */}
                  <div className="absolute bottom-4 left-4 text-xs text-gray-500">
                    Drag to rotate • Click to place • Right-click to remove
                  </div>
                </div>
                
                {/* Side panel: Component info */}
                <div className="w-64 border-l border-dark-600 p-4 overflow-y-auto">
                  <h3 className="font-semibold text-sm mb-3 flex items-center gap-2">
                    <Layers className="w-4 h-4 text-green-400" />
                    Component Library
                  </h3>
                  
                  <div className="space-y-2">
                    {Object.entries(VOXEL_TYPES).slice(1).map(([key, value]) => (
                      <button
                        key={key}
                        onClick={() => setSelectedType(key as keyof typeof VOXEL_TYPES)}
                        className={`w-full flex items-center gap-3 p-2 rounded-lg text-left text-sm transition-all ${
                          selectedType === key 
                            ? 'bg-green-500/10 border border-green-500/30' 
                            : 'bg-dark-700/50 border border-transparent hover:border-dark-500'
                        }`}
                      >
                        <div 
                          className="w-6 h-6 rounded"
                          style={{ backgroundColor: value.color }}
                        />
                        <span>{value.name}</span>
                      </button>
                    ))}
                  </div>
                  
                  <div className="mt-6 pt-4 border-t border-dark-600">
                    <h3 className="font-semibold text-sm mb-3 flex items-center gap-2">
                      <Globe className="w-4 h-4 text-blue-400" />
                      Real-World Data
                    </h3>
                    <button className="w-full flex items-center gap-2 p-2 bg-blue-500/10 border border-blue-500/30 rounded-lg text-sm text-blue-400 hover:bg-blue-500/20 transition-colors">
                      <Globe className="w-4 h-4" />
                      Load Sitka Terrain
                    </button>
                    <p className="text-xs text-gray-500 mt-2">
                      Import Navionics charts, underwater bathymetry
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Progression Layers */}
            <div className="bg-dark-800/80 backdrop-blur-sm rounded-xl border border-dark-600 p-4">
              <h3 className="font-semibold text-sm mb-3 flex items-center gap-2">
                <Target className="w-4 h-4 text-amber-400" />
                Progressive Iteration
              </h3>
              
              <div className="flex items-center gap-2 overflow-x-auto pb-2">
                {(Object.keys(LAYER_NAMES) as AbstractionLayer[]).map((layer, index) => (
                  <button
                    key={layer}
                    onClick={() => setCurrentLayer(layer)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-all ${
                      currentLayer === layer
                        ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                        : index < Object.keys(LAYER_NAMES).indexOf(currentLayer)
                        ? 'bg-dark-700/50 text-gray-400 border border-dark-600'
                        : 'bg-dark-800/50 text-gray-500 border border-dark-700'
                    }`}
                  >
                    <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs ${
                      index < Object.keys(LAYER_NAMES).indexOf(currentLayer)
                        ? 'bg-green-500 text-white'
                        : currentLayer === layer
                        ? 'bg-green-500/30 text-green-400'
                        : 'bg-dark-600 text-gray-500'
                    }`}>
                      {index < Object.keys(LAYER_NAMES).indexOf(currentLayer) ? '✓' : index + 1}
                    </span>
                    {LAYER_NAMES[layer]}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Right: Lucineer Chat */}
          <div className="bg-dark-800/80 backdrop-blur-sm rounded-xl border border-dark-600 flex flex-col h-[700px]">
            {/* Chat Header */}
            <div className="p-4 border-b border-dark-600">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="font-semibold">Lucineer</h2>
                  <p className="text-xs text-gray-500">AI Co-Inventor • Online</p>
                </div>
              </div>
            </div>
            
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[90%] rounded-xl p-3 ${
                      msg.role === 'user'
                        ? 'bg-green-500/10 border border-green-500/30 text-white'
                        : 'bg-dark-700/50 border border-dark-600 text-gray-200'
                    }`}
                  >
                    {msg.role === 'lucineer' && (
                      <div className="flex items-center gap-2 mb-2 text-purple-400 text-xs font-medium">
                        <Sparkles className="w-3 h-3" />
                        Lucineer
                      </div>
                    )}
                    <div className="text-sm whitespace-pre-wrap">{msg.content}</div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            
            {/* Quick Actions */}
            <div className="px-4 py-2 border-t border-dark-600">
              <div className="flex gap-2 overflow-x-auto">
                {[
                  "Generate architecture",
                  "Add sonar integration",
                  "Show terrain data",
                  "Export to Cadence",
                ].map((action) => (
                  <button
                    key={action}
                    onClick={() => setInputValue(action)}
                    className="flex-shrink-0 px-3 py-1.5 bg-dark-700/50 rounded-lg text-xs text-gray-400 hover:text-white hover:bg-dark-600 transition-colors"
                  >
                    {action}
                  </button>
                ))}
              </div>
            </div>
            
            {/* Input */}
            <div className="p-4 border-t border-dark-600">
              <div className="flex gap-2">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Describe your project or ask questions..."
                  className="flex-1 bg-dark-700/50 border border-dark-600 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-green-500/50"
                />
                <button
                  onClick={handleSend}
                  className="p-2 bg-green-500/10 text-green-400 rounded-lg hover:bg-green-500/20 transition-colors"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom: Export Options */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { icon: FileText, title: 'RTL Export', desc: 'Verilog/VHDL for Cadence' },
            { icon: Code, title: 'Constraints', desc: 'SDC timing constraints' },
            { icon: Layers, title: 'Layout Hints', desc: 'Floorplan suggestions' },
            { icon: Terminal, title: 'Test Vectors', desc: 'Verification patterns' },
          ].map((item) => (
            <button
              key={item.title}
              className="flex items-center gap-3 p-4 bg-dark-800/60 rounded-xl border border-dark-600 hover:border-green-500/30 transition-all text-left"
            >
              <item.icon className="w-5 h-5 text-green-400" />
              <div>
                <div className="font-medium text-sm">{item.title}</div>
                <div className="text-xs text-gray-500">{item.desc}</div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
