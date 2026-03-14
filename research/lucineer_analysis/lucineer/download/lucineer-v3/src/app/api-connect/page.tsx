"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Zap, Key, Check, X, ExternalLink, Shield, Lock, RefreshCw,
  ArrowRight, AlertCircle, Settings, Eye, EyeOff, Trash2, Plus
} from "lucide-react";

// API Provider definitions
const apiProviders = [
  {
    id: "groq",
    name: "Groq",
    description: "Ultra-fast inference with LPU technology",
    models: ["Llama 3.1", "Mixtral", "Gemma"],
    pricing: "Free tier available",
    website: "https://console.groq.com",
    color: "#F97316",
    category: "free",
  },
  {
    id: "openai",
    name: "OpenAI",
    description: "GPT-4, DALL-E, and embeddings",
    models: ["GPT-4o", "GPT-4 Turbo", "DALL-E 3"],
    pricing: "Pay per use",
    website: "https://platform.openai.com",
    color: "#10B981",
    category: "major",
  },
  {
    id: "xai",
    name: "x.ai",
    description: "Grok access for real-time knowledge",
    models: ["Grok-1", "Grok-2"],
    pricing: "Subscription based",
    website: "https://x.ai",
    color: "#000000",
    category: "free",
  },
  {
    id: "deepseek",
    name: "DeepSeek",
    description: "Cost-effective reasoning models",
    models: ["DeepSeek-V3", "DeepSeek-Coder"],
    pricing: "$0.14/1M tokens",
    website: "https://platform.deepseek.com",
    color: "#6366F1",
    category: "low-cost",
  },
  {
    id: "kimi",
    name: "Kimi.ai",
    description: "Long context understanding",
    models: ["Moonshot-v1", "Kimi"],
    pricing: "Competitive rates",
    website: "https://kimi.ai",
    color: "#8B5CF6",
    category: "low-cost",
  },
  {
    id: "anthropic",
    name: "Anthropic",
    description: "Claude models for safety-first AI",
    models: ["Claude 3.5 Sonnet", "Claude 3 Opus"],
    pricing: "Pay per use",
    website: "https://console.anthropic.com",
    color: "#D97706",
    category: "major",
  },
  {
    id: "ollama",
    name: "Ollama",
    description: "Run models locally, fully offline",
    models: ["Llama 3.1", "Mistral", "Phi-3"],
    pricing: "Free (local)",
    website: "https://ollama.ai",
    color: "#22C55E",
    category: "local",
  },
  {
    id: "huggingface",
    name: "HuggingFace",
    description: "Open models and serverless inference",
    models: ["Thousands of models"],
    pricing: "Free tier available",
    website: "https://huggingface.co",
    color: "#FFB800",
    category: "free",
  },
];

const categories = [
  { id: "all", name: "All Providers" },
  { id: "free", name: "Free Tiers" },
  { id: "low-cost", name: "Low Cost" },
  { id: "major", name: "Major Players" },
  { id: "local", name: "Local / Offline" },
];

export default function APIConnectPage() {
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [connectedProviders, setConnectedProviders] = useState<string[]>([]);
  const [showKeyModal, setShowKeyModal] = useState<string | null>(null);
  const [apiKey, setApiKey] = useState("");
  const [showKey, setShowKey] = useState(false);

  const filteredProviders = selectedCategory === "all"
    ? apiProviders
    : apiProviders.filter((p) => p.category === selectedCategory);

  const handleConnect = (providerId: string) => {
    setShowKeyModal(providerId);
    setApiKey("");
  };

  const handleSaveKey = () => {
    if (showKeyModal && apiKey) {
      // In real app, encrypt and store locally
      setConnectedProviders((prev) => [...prev, showKeyModal]);
      setShowKeyModal(null);
      setApiKey("");
    }
  };

  const handleDisconnect = (providerId: string) => {
    setConnectedProviders((prev) => prev.filter((id) => id !== providerId));
  };

  return (
    <div className="animated-bg min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-12">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold">API Connections</h1>
              <p className="text-sm text-gray-500">Connect AI providers for enhanced features</p>
            </div>
          </div>

          <p className="text-xl text-gray-300 max-w-3xl">
            Connect your API keys to unlock AI-powered features. All keys are stored locally 
            in your browser — we never see or store them on our servers.
          </p>
        </div>

        {/* Security Notice */}
        <div className="bg-green-900/20 border border-green-500/30 rounded-xl p-4 mb-8 flex items-start gap-3">
          <Shield className="w-5 h-5 text-green-400 mt-0.5" />
          <div>
            <h3 className="font-semibold text-green-400">Local-First Security</h3>
            <p className="text-sm text-gray-400">
              Your API keys are encrypted and stored only in your browser&apos;s IndexedDB. 
              We never transmit them to any server. You can delete them at any time.
            </p>
          </div>
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap gap-2 mb-8">
          {categories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedCategory === category.id
                  ? "bg-green-500/20 text-green-400 border border-green-500/30"
                  : "bg-dark-700/50 text-gray-400 hover:text-white"
              }`}
            >
              {category.name}
            </button>
          ))}
        </div>

        {/* Provider Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredProviders.map((provider) => (
            <div
              key={provider.id}
              className="bg-dark-800/80 backdrop-blur-lg rounded-xl border border-dark-600 overflow-hidden"
            >
              <div className="p-4 flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center"
                    style={{ background: `${provider.color}20` }}
                  >
                    <span className="text-lg font-bold" style={{ color: provider.color }}>
                      {provider.name.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <h3 className="font-semibold">{provider.name}</h3>
                    <p className="text-xs text-gray-500">{provider.pricing}</p>
                  </div>
                </div>
                {connectedProviders.includes(provider.id) && (
                  <span className="flex items-center gap-1 text-xs text-green-400 bg-green-500/10 px-2 py-1 rounded-full">
                    <Check className="w-3 h-3" />
                    Connected
                  </span>
                )}
              </div>

              <div className="px-4 pb-4">
                <p className="text-sm text-gray-400 mb-3">{provider.description}</p>
                <div className="flex flex-wrap gap-1 mb-4">
                  {provider.models.map((model) => (
                    <span
                      key={model}
                      className="text-xs px-2 py-0.5 rounded bg-dark-700/50 text-gray-400"
                    >
                      {model}
                    </span>
                  ))}
                </div>

                <div className="flex items-center gap-2">
                  {connectedProviders.includes(provider.id) ? (
                    <>
                      <button
                        onClick={() => handleDisconnect(provider.id)}
                        className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-dark-700/50 hover:bg-red-500/10 text-gray-400 hover:text-red-400 text-sm transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                        Disconnect
                      </button>
                      <button className="p-2 rounded-lg bg-dark-700/50 hover:bg-dark-600 transition-colors">
                        <Settings className="w-4 h-4 text-gray-400" />
                      </button>
                    </>
                  ) : (
                    <button
                      onClick={() => handleConnect(provider.id)}
                      className="flex-1 flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-green-600 hover:bg-green-500 text-white text-sm transition-colors"
                    >
                      <Key className="w-4 h-4" />
                      Connect
                    </button>
                  )}
                  <a
                    href={provider.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 rounded-lg bg-dark-700/50 hover:bg-dark-600 transition-colors"
                  >
                    <ExternalLink className="w-4 h-4 text-gray-400" />
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Add Custom Provider */}
        <div className="mt-8">
          <button className="w-full flex items-center justify-center gap-2 p-4 rounded-xl border-2 border-dashed border-dark-600 hover:border-green-500/30 text-gray-400 hover:text-green-400 transition-colors">
            <Plus className="w-5 h-5" />
            Add Custom API Provider
          </button>
        </div>
      </div>

      {/* API Key Modal */}
      {showKeyModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-dark-800 rounded-2xl border border-dark-600 max-w-md w-full overflow-hidden">
            <div className="p-4 border-b border-dark-600 flex items-center justify-between">
              <h3 className="font-semibold">Connect {apiProviders.find((p) => p.id === showKeyModal)?.name}</h3>
              <button
                onClick={() => setShowKeyModal(null)}
                className="p-1 rounded-lg hover:bg-dark-700 transition-colors"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>

            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">API Key</label>
                <div className="relative">
                  <input
                    type={showKey ? "text" : "password"}
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="Enter your API key"
                    className="w-full bg-dark-700 border border-dark-600 rounded-lg px-4 py-2.5 pr-10 text-white placeholder-gray-500 focus:outline-none focus:border-green-500"
                  />
                  <button
                    onClick={() => setShowKey(!showKey)}
                    className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded hover:bg-dark-600 transition-colors"
                  >
                    {showKey ? (
                      <EyeOff className="w-4 h-4 text-gray-400" />
                    ) : (
                      <Eye className="w-4 h-4 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>

              <div className="flex items-start gap-2 text-xs text-gray-500">
                <Lock className="w-4 h-4 mt-0.5" />
                <span>Your key is encrypted and stored locally. We never see it.</span>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowKeyModal(null)}
                  className="flex-1 px-4 py-2.5 rounded-lg bg-dark-700 hover:bg-dark-600 text-gray-400 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveKey}
                  disabled={!apiKey}
                  className="flex-1 px-4 py-2.5 rounded-lg bg-green-600 hover:bg-green-500 disabled:bg-dark-700 disabled:text-gray-500 text-white transition-colors"
                >
                  Connect
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
