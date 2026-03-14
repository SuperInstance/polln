"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Zap, Key, Check, X, AlertTriangle, ExternalLink, Copy, 
  Eye, EyeOff, RefreshCw, Shield, Server, HardDrive, Cloud,
  Info, ChevronDown, ArrowRight, Download
} from "lucide-react";

// API Provider configurations
const apiProviders = {
  free: [
    {
      id: "groq",
      name: "Groq",
      description: "Ultra-fast inference with Llama models",
      models: ["Llama 3.1 8B", "Llama 3.1 70B", "Mixtral 8x7B"],
      pricing: "Free tier available",
      url: "https://console.groq.com/keys",
      icon: "⚡",
      color: "orange",
    },
    {
      id: "xai",
      name: "x.ai (Grok)",
      description: "Access to Grok models from xAI",
      models: ["Grok-1", "Grok-2"],
      pricing: "Free tier with X Premium",
      url: "https://x.ai",
      icon: "𝕏",
      color: "blue",
    },
    {
      id: "huggingface",
      name: "HuggingFace",
      description: "Open models and free inference API",
      models: ["Various open models"],
      pricing: "Free tier available",
      url: "https://huggingface.co/settings/tokens",
      icon: "🤗",
      color: "yellow",
    },
  ],
  lowCost: [
    {
      id: "deepseek",
      name: "DeepSeek",
      description: "High quality at lowest cost",
      models: ["DeepSeek-V3", "DeepSeek-Coder"],
      pricing: "$0.14 per 1M tokens",
      url: "https://platform.deepseek.com/api_keys",
      icon: "🔍",
      color: "purple",
    },
    {
      id: "zai",
      name: "z.ai",
      description: "Cost-effective AI inference",
      models: ["Various models"],
      pricing: "Pay per use",
      url: "https://z.ai",
      icon: "🎯",
      color: "green",
    },
    {
      id: "kimi",
      name: "Kimi (Moonshot)",
      description: "Long context models from China",
      models: ["Kimi Chat", "Moonshot"],
      pricing: "Competitive pricing",
      url: "https://kimi.ai",
      icon: "🌙",
      color: "indigo",
    },
    {
      id: "minimax",
      name: "MiniMax",
      description: "Chinese AI with strong capabilities",
      models: ["abab5.5", "abab5.5-chat"],
      pricing: "Competitive pricing",
      url: "https://api.minimax.chat",
      icon: "🔷",
      color: "cyan",
    },
  ],
  major: [
    {
      id: "openai",
      name: "OpenAI",
      description: "GPT-4, DALL-E, Embeddings",
      models: ["GPT-4 Turbo", "GPT-4o", "DALL-E 3"],
      pricing: "Pay per use",
      url: "https://platform.openai.com/api-keys",
      icon: "🧠",
      color: "emerald",
    },
    {
      id: "anthropic",
      name: "Anthropic",
      description: "Claude models for safe AI",
      models: ["Claude 3.5 Sonnet", "Claude 3 Opus"],
      pricing: "Pay per use",
      url: "https://console.anthropic.com/",
      icon: "🤖",
      color: "amber",
    },
    {
      id: "google",
      name: "Google AI",
      description: "Gemini models from Google",
      models: ["Gemini Pro", "Gemini Ultra"],
      pricing: "Free tier + pay per use",
      url: "https://aistudio.google.com/app/apikey",
      icon: "💎",
      color: "blue",
    },
    {
      id: "mistral",
      name: "Mistral",
      description: "Open weights and API models",
      models: ["Mistral Large", "Codestral"],
      pricing: "Pay per use",
      url: "https://console.mistral.ai/",
      icon: "🌀",
      color: "orange",
    },
  ],
  local: [
    {
      id: "ollama",
      name: "Ollama",
      description: "Run models fully local",
      models: ["Llama 3.1", "Mistral", "Phi-3", "...and more"],
      pricing: "Free (uses your hardware)",
      url: "https://ollama.ai",
      icon: "🦙",
      color: "green",
      isLocal: true,
    },
    {
      id: "lmstudio",
      name: "LM Studio",
      description: "Desktop app for local models",
      models: ["Any GGUF model"],
      pricing: "Free",
      url: "https://lmstudio.ai",
      icon: "💻",
      color: "purple",
      isLocal: true,
    },
  ],
};

// Custom API configuration
const customApiConfig = {
  id: "custom",
  name: "Custom Endpoint",
  description: "Connect to any OpenAI-compatible API",
  fields: ["URL", "API Key", "Model Name"],
};

// Status indicator component
function StatusIndicator({ status }: { status: "connected" | "disconnected" | "pending" }) {
  const colors = {
    connected: "bg-green-500",
    disconnected: "bg-gray-500",
    pending: "bg-amber-500 animate-pulse",
  };
  const labels = {
    connected: "Connected",
    disconnected: "Not connected",
    pending: "Testing...",
  };
  
  return (
    <div className="flex items-center gap-2 text-xs">
      <span className={`w-2 h-2 rounded-full ${colors[status]}`} />
      <span className="text-gray-400">{labels[status]}</span>
    </div>
  );
}

export default function APIConnectPage() {
  const [expandedProvider, setExpandedProvider] = useState<string | null>(null);
  const [showKey, setShowKey] = useState<Record<string, boolean>>({});
  const [apiKeys, setApiKeys] = useState<Record<string, string>>({});
  const [connectionStatus, setConnectionStatus] = useState<Record<string, "connected" | "disconnected" | "pending">>({});
  const [customUrl, setCustomUrl] = useState("");
  const [customKey, setCustomKey] = useState("");
  const [customModel, setCustomModel] = useState("");

  const toggleKeyVisibility = (id: string) => {
    setShowKey(prev => ({ ...prev, [id]: !prev[id] }));
  };

  const handleKeyChange = (id: string, value: string) => {
    setApiKeys(prev => ({ ...prev, [id]: value }));
  };

  const testConnection = (id: string) => {
    setConnectionStatus(prev => ({ ...prev, [id]: "pending" }));
    // Simulate connection test
    setTimeout(() => {
      setConnectionStatus(prev => ({ ...prev, [id]: "connected" }));
    }, 1500);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="animated-bg min-h-screen pt-24 pb-20">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-full px-5 py-2 mb-6">
            <Zap className="w-4 h-4 text-green-400" />
            <span className="text-green-400 text-sm font-medium">Optional Enhancement</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="gradient-text">Connect AI APIs</span>
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto text-lg">
            Enhance your learning with AI-powered explanations. Everything works offline — 
            APIs are optional enhancements.
          </p>
        </div>

        {/* Important Notice */}
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6 mb-10">
          <div className="flex items-start gap-4">
            <Info className="w-6 h-6 text-blue-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-semibold text-blue-400 mb-2">Works Without APIs</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                All simulators, lessons, and tools work offline immediately. 
                API connections add AI-powered explanations and personalized help — 
                they&apos;re completely optional. Your data stays on your device.
              </p>
            </div>
          </div>
        </div>

        {/* Free Tier Providers */}
        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <h2 className="text-2xl font-bold">Free Tiers</h2>
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/30">
              Start Free
            </span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {apiProviders.free.map((provider) => (
              <div
                key={provider.id}
                className="bg-dark-800/60 rounded-xl border border-dark-600 overflow-hidden hover:border-green-500/30 transition-all"
              >
                <div className="p-5">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{provider.icon}</span>
                      <div>
                        <h3 className="font-semibold">{provider.name}</h3>
                        <StatusIndicator status={connectionStatus[provider.id] || "disconnected"} />
                      </div>
                    </div>
                    <a
                      href={provider.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-400 hover:text-white transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                  
                  <p className="text-sm text-gray-400 mb-3">{provider.description}</p>
                  <p className="text-xs text-green-400 mb-4">{provider.pricing}</p>
                  
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {provider.models.slice(0, 2).map((model) => (
                      <span key={model} className="px-2 py-1 rounded text-xs bg-dark-700 text-gray-400">
                        {model}
                      </span>
                    ))}
                  </div>
                  
                  <div className="relative">
                    <input
                      type={showKey[provider.id] ? "text" : "password"}
                      placeholder="Enter API key..."
                      value={apiKeys[provider.id] || ""}
                      onChange={(e) => handleKeyChange(provider.id, e.target.value)}
                      className="w-full bg-dark-700/50 border border-dark-600 rounded-lg px-3 py-2 text-sm pr-16 focus:outline-none focus:border-green-500/50"
                    />
                    <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                      <button
                        onClick={() => toggleKeyVisibility(provider.id)}
                        className="p-1 text-gray-400 hover:text-white"
                      >
                        {showKey[provider.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                      <button
                        onClick={() => testConnection(provider.id)}
                        disabled={!apiKeys[provider.id]}
                        className="p-1 text-gray-400 hover:text-green-400 disabled:opacity-50"
                      >
                        <RefreshCw className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Low Cost Providers */}
        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <h2 className="text-2xl font-bold">Low Cost</h2>
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-purple-500/10 text-purple-400 border border-purple-500/30">
              Best Value
            </span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {apiProviders.lowCost.map((provider) => (
              <div
                key={provider.id}
                className="bg-dark-800/60 rounded-xl border border-dark-600 overflow-hidden hover:border-purple-500/30 transition-all"
              >
                <div className="p-5">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{provider.icon}</span>
                      <div>
                        <h3 className="font-semibold">{provider.name}</h3>
                        <StatusIndicator status={connectionStatus[provider.id] || "disconnected"} />
                      </div>
                    </div>
                    <a
                      href={provider.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-400 hover:text-white transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                  
                  <div className="flex justify-between items-center mb-3">
                    <p className="text-sm text-gray-400">{provider.description}</p>
                    <span className="text-sm font-medium text-purple-400">{provider.pricing}</span>
                  </div>
                  
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {provider.models.map((model) => (
                      <span key={model} className="px-2 py-1 rounded text-xs bg-dark-700 text-gray-400">
                        {model}
                      </span>
                    ))}
                  </div>
                  
                  <div className="relative">
                    <input
                      type={showKey[provider.id] ? "text" : "password"}
                      placeholder="Enter API key..."
                      value={apiKeys[provider.id] || ""}
                      onChange={(e) => handleKeyChange(provider.id, e.target.value)}
                      className="w-full bg-dark-700/50 border border-dark-600 rounded-lg px-3 py-2 text-sm pr-16 focus:outline-none focus:border-purple-500/50"
                    />
                    <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                      <button
                        onClick={() => toggleKeyVisibility(provider.id)}
                        className="p-1 text-gray-400 hover:text-white"
                      >
                        {showKey[provider.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                      <button
                        onClick={() => testConnection(provider.id)}
                        disabled={!apiKeys[provider.id]}
                        className="p-1 text-gray-400 hover:text-purple-400 disabled:opacity-50"
                      >
                        <RefreshCw className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Major Providers */}
        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <h2 className="text-2xl font-bold">Major Providers</h2>
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/30">
              Enterprise
            </span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {apiProviders.major.map((provider) => (
              <div
                key={provider.id}
                className="bg-dark-800/60 rounded-xl border border-dark-600 overflow-hidden hover:border-amber-500/30 transition-all"
              >
                <div className="p-5">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{provider.icon}</span>
                      <div>
                        <h3 className="font-semibold">{provider.name}</h3>
                        <StatusIndicator status={connectionStatus[provider.id] || "disconnected"} />
                      </div>
                    </div>
                    <a
                      href={provider.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-400 hover:text-white transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                  
                  <p className="text-sm text-gray-400 mb-3">{provider.description}</p>
                  <p className="text-xs text-amber-400 mb-4">{provider.pricing}</p>
                  
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {provider.models.map((model) => (
                      <span key={model} className="px-2 py-1 rounded text-xs bg-dark-700 text-gray-400">
                        {model}
                      </span>
                    ))}
                  </div>
                  
                  <div className="relative">
                    <input
                      type={showKey[provider.id] ? "text" : "password"}
                      placeholder="Enter API key..."
                      value={apiKeys[provider.id] || ""}
                      onChange={(e) => handleKeyChange(provider.id, e.target.value)}
                      className="w-full bg-dark-700/50 border border-dark-600 rounded-lg px-3 py-2 text-sm pr-16 focus:outline-none focus:border-amber-500/50"
                    />
                    <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                      <button
                        onClick={() => toggleKeyVisibility(provider.id)}
                        className="p-1 text-gray-400 hover:text-white"
                      >
                        {showKey[provider.id] ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                      <button
                        onClick={() => testConnection(provider.id)}
                        disabled={!apiKeys[provider.id]}
                        className="p-1 text-gray-400 hover:text-amber-400 disabled:opacity-50"
                      >
                        <RefreshCw className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Local Options */}
        <section className="mb-12">
          <div className="flex items-center gap-3 mb-6">
            <h2 className="text-2xl font-bold">Fully Local</h2>
            <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-500/10 text-green-400 border border-green-500/30">
              100% Private
            </span>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {apiProviders.local.map((provider) => (
              <div
                key={provider.id}
                className="bg-dark-800/60 rounded-xl border border-dark-600 overflow-hidden hover:border-green-500/30 transition-all"
              >
                <div className="p-5">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{provider.icon}</span>
                      <div>
                        <h3 className="font-semibold">{provider.name}</h3>
                        <div className="flex items-center gap-2 text-xs">
                          <span className="w-2 h-2 rounded-full bg-green-500" />
                          <span className="text-gray-400">Local option</span>
                        </div>
                      </div>
                    </div>
                    <a
                      href={provider.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-400 hover:text-white transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  </div>
                  
                  <p className="text-sm text-gray-400 mb-3">{provider.description}</p>
                  <p className="text-xs text-green-400 mb-4">{provider.pricing}</p>
                  
                  <div className="flex flex-wrap gap-1.5 mb-4">
                    {provider.models.map((model) => (
                      <span key={model} className="px-2 py-1 rounded text-xs bg-dark-700 text-gray-400">
                        {model}
                      </span>
                    ))}
                  </div>
                  
                  <div className="flex gap-2">
                    <Link
                      href="/downloads#ollama"
                      className="flex items-center gap-2 px-4 py-2 bg-green-500/10 text-green-400 rounded-lg text-sm hover:bg-green-500/20 transition-colors"
                    >
                      <Download className="w-4 h-4" />
                      Install Guide
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Custom Endpoint */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Custom Endpoint</h2>
          
          <div className="bg-dark-800/60 rounded-xl border border-dark-600 p-6">
            <p className="text-gray-400 text-sm mb-6">
              Connect to any OpenAI-compatible API endpoint (vLLM, LocalAI, custom servers)
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div>
                <label className="block text-sm text-gray-400 mb-2">API URL</label>
                <input
                  type="text"
                  placeholder="http://localhost:11434/v1"
                  value={customUrl}
                  onChange={(e) => setCustomUrl(e.target.value)}
                  className="w-full bg-dark-700/50 border border-dark-600 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-green-500/50"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">API Key (optional)</label>
                <input
                  type="password"
                  placeholder="Leave empty for local"
                  value={customKey}
                  onChange={(e) => setCustomKey(e.target.value)}
                  className="w-full bg-dark-700/50 border border-dark-600 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-green-500/50"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-2">Model Name</label>
                <input
                  type="text"
                  placeholder="llama3.1"
                  value={customModel}
                  onChange={(e) => setCustomModel(e.target.value)}
                  className="w-full bg-dark-700/50 border border-dark-600 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-green-500/50"
                />
              </div>
            </div>
            
            <button className="flex items-center gap-2 px-6 py-2.5 bg-green-500/10 text-green-400 rounded-lg text-sm hover:bg-green-500/20 transition-colors">
              <RefreshCw className="w-4 h-4" />
              Test Connection
            </button>
          </div>
        </section>

        {/* Cloudflare Sync */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Cloud Sync (Optional)</h2>
          
          <div className="bg-dark-800/60 rounded-xl border border-dark-600 p-6">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center flex-shrink-0">
                <Cloud className="w-6 h-6 text-amber-400" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold mb-2">Sync to Cloudflare</h3>
                <p className="text-gray-400 text-sm mb-4">
                  Optionally sync your progress, settings, and API keys to Cloudflare for 
                  cross-device access. Requires age verification (18+).
                </p>
                <div className="flex items-center gap-2 text-xs text-gray-500 mb-4">
                  <Shield className="w-4 h-4" />
                  <span>Your data is encrypted end-to-end</span>
                </div>
                <button className="flex items-center gap-2 px-6 py-2.5 bg-dark-700 text-gray-300 rounded-lg text-sm hover:bg-dark-600 transition-colors">
                  Connect Cloudflare
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Navigation */}
        <div className="flex justify-center gap-4 mt-12">
          <Link
            href="/learning"
            className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-6 py-3 rounded-xl font-medium transition-colors"
          >
            ← Back to Learning
          </Link>
          <Link
            href="/downloads"
            className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-6 py-3 rounded-xl font-medium transition-all"
          >
            Download Center <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}
