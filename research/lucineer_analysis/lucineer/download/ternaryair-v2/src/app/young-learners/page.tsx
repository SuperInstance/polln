"use client";

import { useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import {
  Gamepad2, Star, ArrowRight, RotateCcw, Sparkles, Trophy, Target
} from "lucide-react";

const characters = [
  { id: 'terny', name: 'Terny the Robot', emoji: '🤖', color: 'green' },
  { id: 'data', name: 'Data the Dog', emoji: '🐕', color: 'blue' },
  { id: 'logic', name: 'Logic the Owl', emoji: '🦉', color: 'purple' },
  { id: 'pixel', name: 'Pixel the Cat', emoji: '🐱', color: 'pink' },
];

const puzzleCategories = [
  { id: 'patterns', title: 'Pattern Playground', emoji: '🎨', difficulty: 1, puzzles: 8, completed: 3 },
  { id: 'chains', title: 'Chain Reactions', emoji: '⚡', difficulty: 2, puzzles: 10, completed: 1 },
  { id: 'pipes', title: 'Pipe Dreams', emoji: '🔧', difficulty: 2, puzzles: 8, completed: 0 },
  { id: 'training', title: 'Teach the Robot', emoji: '🧠', difficulty: 3, puzzles: 6, completed: 0 },
];

export default function YoungLearnersPage() {
  const searchParams = useSearchParams();
  const ageParam = searchParams.get('age') || '4-6';
  
  const [grid, setGrid] = useState<string[][]>(() => 
    Array(6).fill(null).map(() => Array(6).fill('empty'))
  );
  const [moves, setMoves] = useState(0);
  const [celebration, setCelebration] = useState(false);
  
  const colors = ['empty', 'red', 'blue', 'green', 'yellow'];
  
  const handleBlockClick = (row: number, col: number) => {
    const current = grid[row][col];
    const nextIndex = (colors.indexOf(current) + 1) % colors.length;
    const newGrid = grid.map(r => [...r]);
    newGrid[row][col] = colors[nextIndex];
    setGrid(newGrid);
    setMoves(m => m + 1);
    
    if (Math.random() > 0.8) {
      setCelebration(true);
      setTimeout(() => setCelebration(false), 2000);
    }
  };
  
  return (
    <div className="animated-bg min-h-screen pt-20 pb-8">
      {celebration && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="text-center">
            <div className="text-8xl animate-bounce">🎉</div>
            <h2 className="text-4xl font-bold text-white mt-4">Amazing!</h2>
            <div className="flex justify-center gap-2 mt-4">
              {[...Array(5)].map((_, i) => <Star key={i} className="w-8 h-8 text-yellow-400 fill-yellow-400" />)}
            </div>
          </div>
        </div>
      )}
      
      <div className="max-w-7xl mx-auto px-4">
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/30 rounded-full px-5 py-2 mb-4">
            <Gamepad2 className="w-4 h-4 text-blue-400" />
            <span className="text-blue-400 text-sm font-medium">Ages {ageParam} • Voxel Puzzles</span>
          </div>
          <h1 className="text-4xl font-bold mb-2">
            <span className="gradient-text">Incredible Machine World</span>
          </h1>
          <p className="text-gray-400">Build amazing machines, solve silly puzzles!</p>
        </div>
        
        <div className="flex justify-center gap-3 mb-6">
          {characters.map((char) => (
            <div key={char.id} className="flex flex-col items-center p-3 bg-dark-700/30 rounded-xl">
              <span className="text-3xl">{char.emoji}</span>
              <span className="text-xs text-gray-400">{char.name.split(' ')[0]}</span>
            </div>
          ))}
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {puzzleCategories.map((cat) => (
            <button key={cat.id} className="bg-dark-800/60 rounded-xl border border-dark-600 p-4 hover:border-green-500/30 transition-all text-left">
              <span className="text-3xl">{cat.emoji}</span>
              <h3 className="font-semibold mt-2">{cat.title}</h3>
              <p className="text-xs text-gray-500">{cat.completed}/{cat.puzzles} done</p>
            </button>
          ))}
        </div>
        
        <div className="bg-dark-800/60 rounded-xl border border-dark-600 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold flex items-center gap-2">
              <Target className="w-4 h-4 text-amber-400" />
              Pattern Puzzle
            </h3>
            <span className="text-sm text-gray-400">Moves: {moves}</span>
          </div>
          
          <div className="grid grid-cols-6 gap-2 max-w-md mx-auto">
            {grid.map((row, ri) => row.map((cell, ci) => (
              <button
                key={`${ri}-${ci}`}
                onClick={() => handleBlockClick(ri, ci)}
                className="w-12 h-12 rounded-lg transition-all hover:scale-105"
                style={{ backgroundColor: cell === 'empty' ? '#1f2937' : cell === 'red' ? '#ef4444' : cell === 'blue' ? '#3b82f6' : cell === 'green' ? '#22c55e' : '#eab308' }}
              />
            )))}
          </div>
          
          <button onClick={() => { setGrid(Array(6).fill(null).map(() => Array(6).fill('empty'))); setMoves(0); }} 
            className="mt-4 flex items-center gap-2 mx-auto text-sm text-gray-400 hover:text-white">
            <RotateCcw className="w-4 h-4" /> Reset
          </button>
        </div>
        
        <div className="flex justify-center gap-4 mt-8">
          <Link href="/learning" className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 px-6 py-3 rounded-xl font-medium transition-colors">
            ← Learning Hub
          </Link>
          <Link href="/timing-playground" className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 px-6 py-3 rounded-xl font-medium transition-all">
            More Games <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}
