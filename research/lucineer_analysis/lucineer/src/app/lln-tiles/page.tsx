"use client";

import dynamic from 'next/dynamic';

// Dynamically import the TileEditor to avoid SSR issues
const TileEditor = dynamic(() => import('../lln-playground/TileEditor').then(mod => mod.default), {
  ssr: false,
  loading: () => (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-purple-400">Loading Tile Editor...</p>
      </div>
    </div>
  ),
});

export default function LLNTilesPage() {
  return <TileEditor />;
}
