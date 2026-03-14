'use client'

import { useState } from 'react'

// Download data
const downloads = [
  {
    name: 'Full Repository',
    description: 'Complete source code, RTL, SDK, and documentation',
    size: '~10 MB',
    format: 'ZIP',
    url: 'https://github.com/superinstance/ternaryair/archive/refs/heads/main.zip',
    icon: '📦',
    primary: true,
  },
  {
    name: 'Python SDK',
    description: 'Install via pip for immediate use',
    size: '~500 KB',
    format: 'PyPI',
    url: 'https://pypi.org/project/ternaryair/',
    icon: '🐍',
    command: 'pip install ternaryair',
  },
  {
    name: 'RTL Source',
    description: 'SystemVerilog hardware design files',
    size: '~100 KB',
    format: 'SV',
    url: 'https://github.com/superinstance/ternaryair/tree/main/hardware/rtl',
    icon: '⚡',
  },
  {
    name: 'FPGA Bitstreams',
    description: 'Pre-built for PYNQ-Z2, Arty A7',
    size: '~5 MB',
    format: 'BIT',
    url: 'https://github.com/superinstance/ternaryair/tree/main/hardware/fpga/bitstreams',
    icon: '🔧',
  },
  {
    name: 'Documentation PDF',
    description: 'Complete technical documentation',
    size: '~2 MB',
    format: 'PDF',
    url: '/docs/ternaryair-docs.pdf',
    icon: '📄',
  },
  {
    name: 'Security Whitepaper',
    description: 'Threat model and security analysis',
    size: '~500 KB',
    format: 'PDF',
    url: '/docs/ternaryair-security.pdf',
    icon: '🔐',
  },
]

// Comparison data
const comparisonData = [
  { feature: 'Internet Required', cloud: 'Yes', gpu: 'No', ternaryair: 'No' },
  { feature: 'Data Leaves Device', cloud: 'Yes', gpu: 'No', ternaryair: 'No' },
  { feature: 'Model Can Be Stolen', cloud: 'Yes', gpu: 'Yes', ternaryair: 'No' },
  { feature: 'Monthly Subscription', cloud: 'Yes', gpu: 'No', ternaryair: 'No' },
  { feature: 'Power Consumption', cloud: '300W+', gpu: '200W+', ternaryair: '4W' },
  { feature: 'Cost', cloud: '$20-200/mo', gpu: '$500+', ternaryair: '$99' },
  { feature: 'Open Source', cloud: 'No', gpu: 'No', ternaryair: 'Yes (MIT)' },
]

// Specs data
const specs = [
  { label: 'Retail Price', value: '$99', note: 'One-time purchase' },
  { label: 'Performance', value: '100+ tok/s', note: 'Sustained throughput' },
  { label: 'Power', value: '3-5W', note: 'USB powered' },
  { label: 'Model Size', value: '350M params', note: 'BitNet b1.58' },
  { label: 'Context', value: '4096 tokens', note: 'KV cache' },
  { label: 'Interface', value: 'USB 3.0', note: 'Universal' },
  { label: 'Process', value: '28nm', note: 'Mature, reliable' },
  { label: 'Security', value: 'Air-gapped', note: 'By design' },
]

export default function Home() {
  const [activeTab, setActiveTab] = useState<'users' | 'developers' | 'engineers'>('users')
  const [copied, setCopied] = useState(false)

  const copyCommand = (cmd: string) => {
    navigator.clipboard.writeText(cmd)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 md:py-32">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 via-transparent to-violet-500/10" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-cyan-900/20 via-transparent to-transparent" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm mb-8">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <span className="text-gray-300">v1.0.0 Released — MIT Licensed</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="gradient-text">TernaryAir</span>
          </h1>
          
          <p className="text-xl md:text-2xl text-gray-300 mb-4 max-w-3xl mx-auto">
            Open Source Air-Gapped AI Inference Hardware
          </p>
          
          <p className="text-lg text-gray-400 mb-12 max-w-2xl mx-auto">
            The hardware boundary between you and AI. Private, secure, affordable.
            Works anywhere, powered by USB, costs $99.
          </p>

          {/* Key Benefits */}
          <div className="flex flex-wrap justify-center gap-4 mb-12">
            {['🔒 Air-Gapped', '⚡ 100+ tok/s', '🔌 USB Powered', '💰 $99 One-Time'].map((item) => (
              <div key={item} className="px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-sm">
                {item}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Download Section */}
      <section id="download" className="py-20 border-t border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Download Everything
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              All source code, documentation, and pre-built files. Free forever under MIT license.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            {downloads.map((item) => (
              <a
                key={item.name}
                href={item.url}
                target={item.url.startsWith('http') ? '_blank' : undefined}
                rel={item.url.startsWith('http') ? 'noopener' : undefined}
                className={`group p-6 rounded-xl border transition-all ${
                  item.primary
                    ? 'bg-gradient-to-br from-cyan-500/20 to-violet-500/20 border-cyan-500/30 hover:border-cyan-500/50'
                    : 'bg-white/5 border-white/10 hover:border-white/20'
                }`}
              >
                <div className="flex items-start gap-4">
                  <span className="text-3xl">{item.icon}</span>
                  <div className="flex-1">
                    <h3 className="font-semibold mb-1 group-hover:text-cyan-400 transition-colors">
                      {item.name}
                    </h3>
                    <p className="text-sm text-gray-400 mb-2">{item.description}</p>
                    <div className="flex items-center gap-3 text-xs text-gray-500">
                      <span>{item.format}</span>
                      <span>•</span>
                      <span>{item.size}</span>
                    </div>
                    {item.command && (
                      <div 
                        className="mt-3 flex items-center gap-2 text-xs font-mono bg-black/30 px-3 py-2 rounded border border-white/10 cursor-pointer"
                        onClick={(e) => { e.preventDefault(); copyCommand(item.command!); }}
                      >
                        <span className="text-green-400">$</span>
                        <span>{item.command}</span>
                        <span className="ml-auto text-gray-500">{copied ? '✓' : '📋'}</span>
                      </div>
                    )}
                  </div>
                </div>
              </a>
            ))}
          </div>

          {/* Quick Start */}
          <div className="max-w-3xl mx-auto">
            <div className="p-6 rounded-xl bg-black/40 border border-white/10">
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <span className="text-cyan-400">▶</span> Quick Start
              </h3>
              <pre className="text-sm overflow-x-auto">
{`# Clone the repository
git clone https://github.com/superinstance/ternaryair.git
cd ternaryair

# Install Python SDK
pip install ternaryair

# Try it immediately (no hardware needed)
python -c "from ternaryair import TernaryAir, Simulator; \\
  print(TernaryAir(backend=Simulator()).generate('Hello!'))"`}
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Why It Matters */}
      <section className="py-20 border-t border-white/10 bg-gradient-to-b from-transparent to-black/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Why TernaryAir Matters
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Cloud AI sends your data to other people's computers. TernaryAir keeps it yours.
            </p>
          </div>

          {/* Comparison Table */}
          <div className="overflow-x-auto mb-16">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-4 px-4 text-gray-400 font-medium">Feature</th>
                  <th className="text-center py-4 px-4 text-gray-400 font-medium">Cloud AI</th>
                  <th className="text-center py-4 px-4 text-gray-400 font-medium">Local GPU</th>
                  <th className="text-center py-4 px-4 text-cyan-400 font-medium">TernaryAir</th>
                </tr>
              </thead>
              <tbody>
                {comparisonData.map((row, i) => (
                  <tr key={i} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-4 px-4">{row.feature}</td>
                    <td className="py-4 px-4 text-center">
                      {row.cloud === 'Yes' ? '✅' : row.cloud === 'No' ? '❌' : row.cloud}
                    </td>
                    <td className="py-4 px-4 text-center">
                      {row.gpu === 'Yes' ? '✅' : row.gpu === 'No' ? '❌' : row.gpu}
                    </td>
                    <td className="py-4 px-4 text-center text-cyan-400 font-medium">
                      {row.ternaryair === 'No' ? '❌' : row.ternaryair === 'Yes (MIT)' ? '✅ MIT' : row.ternaryair}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Security Diagram */}
          <div className="grid lg:grid-cols-2 gap-8 items-center">
            <div>
              <h3 className="text-2xl font-bold mb-4">
                Hardware-Enforced Security
              </h3>
              <p className="text-gray-400 mb-6">
                TernaryAir is not software. It's hardware. The security model is enforced by physics,
                not by code that can be hacked.
              </p>
              <ul className="space-y-3">
                {[
                  { icon: '🚫', text: 'No network interface — data exfiltration is physically impossible' },
                  { icon: '🔒', text: 'Mask-locked ROM — weights cannot be read, modified, or stolen' },
                  { icon: '⚡', text: 'Volatile memory only — no data persists after power-off' },
                  { icon: '🛡️', text: 'Agent isolation — AI cannot access your files or network' },
                ].map((item) => (
                  <li key={item.text} className="flex items-start gap-3">
                    <span className="text-xl">{item.icon}</span>
                    <span className="text-gray-300">{item.text}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            <div className="p-6 rounded-xl bg-black/40 border border-white/10">
              <pre className="text-xs text-cyan-300 overflow-x-auto ascii-art">
{`┌──────────────────────────────────────────────────────────────┐
│                      YOUR COMPUTER                           │
│  [Files] [Network] [Apps] [AI Agents]                        │
└──────────────────────────────────────────────────────────────┘
                         │ USB
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    TERNARYAIR DEVICE                         │
│                                                              │
│   ✗ No file access        (no filesystem)                   │
│   ✗ No network access     (no network hardware)             │
│   ✗ No memory persistence (volatile SRAM only)              │
│   ✗ No self-modification  (weights in ROM)                  │
│                                                              │
│   It's a FUNCTION, not a PROGRAM.                           │
│   Input → Inference → Output. Nothing else.                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘`}
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Specifications */}
      <section className="py-20 border-t border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Specifications
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Designed for efficiency, security, and accessibility.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {specs.map((spec) => (
              <div key={spec.label} className="p-6 rounded-xl bg-white/5 border border-white/10 text-center">
                <div className="text-2xl font-bold text-cyan-400 mb-1">{spec.value}</div>
                <div className="text-sm text-gray-300 mb-1">{spec.label}</div>
                <div className="text-xs text-gray-500">{spec.note}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Audience Tabs */}
      <section id="users" className="py-20 border-t border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Choose Your Path
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Explore TernaryAir from your perspective.
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="flex justify-center gap-4 mb-12">
            {[
              { id: 'users', label: 'For Users', icon: '👤', desc: 'Non-technical' },
              { id: 'developers', label: 'For Developers', icon: '👨‍💻', desc: 'Software' },
              { id: 'engineers', label: 'For Engineers', icon: '🔧', desc: 'Hardware' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as typeof activeTab)}
                className={`px-6 py-4 rounded-xl border transition-all ${
                  activeTab === tab.id
                    ? 'bg-cyan-500/20 border-cyan-500/50 text-white'
                    : 'bg-white/5 border-white/10 text-gray-400 hover:text-white hover:border-white/20'
                }`}
              >
                <span className="text-2xl mb-1 block">{tab.icon}</span>
                <span className="font-medium">{tab.label}</span>
                <span className="text-xs block opacity-60">{tab.desc}</span>
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="min-h-[400px]">
            {activeTab === 'users' && (
              <div className="space-y-12">
                <div className="grid lg:grid-cols-2 gap-8">
                  <div>
                    <h3 className="text-2xl font-bold mb-4">What Is TernaryAir?</h3>
                    <p className="text-gray-400 mb-4">
                      TernaryAir is an AI device that works like a calculator — plug it in, use it,
                      unplug it when done. No internet needed, no monthly fees, your data never leaves.
                    </p>
                    <p className="text-gray-400">
                      It's designed for anyone who wants AI assistance without sending their
                      personal information to cloud servers. Doctors, lawyers, business owners,
                      or anyone who values privacy.
                    </p>
                  </div>
                  <div className="p-6 rounded-xl bg-black/40 border border-white/10">
                    <h4 className="font-semibold mb-4 text-cyan-400">Use Cases</h4>
                    <ul className="space-y-3 text-sm text-gray-300">
                      <li className="flex items-start gap-2">
                        <span className="text-green-400">✓</span>
                        <span><strong>Private AI Assistant</strong> — Ask health, finance, or personal questions without data leaving your control</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-green-400">✓</span>
                        <span><strong>Off-Grid AI</strong> — Works on boats, cabins, anywhere without internet (USB powered)</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-green-400">✓</span>
                        <span><strong>Safe AI Agents</strong> — AI can help but cannot access your files or network</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-green-400">✓</span>
                        <span><strong>Professional Work</strong> — Analyze confidential documents, draft communications</span>
                      </li>
                    </ul>
                  </div>
                </div>

                <div>
                  <h3 className="text-2xl font-bold mb-6 text-center">How It Works</h3>
                  <div className="grid md:grid-cols-3 gap-6">
                    {[
                      { step: 1, title: 'Plug In', desc: 'Connect TernaryAir to your computer via USB. It draws less power than a phone charger.' },
                      { step: 2, title: 'Ask', desc: 'Type your question. The device processes it locally, without internet.' },
                      { step: 3, title: 'Done', desc: 'Unplug when finished. No data is stored. No history remains.' },
                    ].map((item) => (
                      <div key={item.step} className="relative p-6 rounded-xl bg-white/5 border border-white/10">
                        <div className="absolute -top-4 left-6 w-8 h-8 rounded-full bg-cyan-500 flex items-center justify-center font-bold text-black">
                          {item.step}
                        </div>
                        <h4 className="font-semibold mt-2 mb-2">{item.title}</h4>
                        <p className="text-sm text-gray-400">{item.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'developers' && (
              <div className="space-y-12">
                <div className="p-6 rounded-xl bg-black/40 border border-white/10">
                  <h3 className="text-xl font-bold mb-4">Python SDK</h3>
                  <pre className="text-sm overflow-x-auto">
{`from ternaryair import TernaryAir, Simulator

# Connect to device (or use simulator for development)
device = TernaryAir()  # Hardware
# OR
device = TernaryAir(backend=Simulator())  # No hardware needed

# Simple generation
response = device.generate("Hello, world!")
print(response)

# Streaming output
for token in device.stream("Tell me a story"):
    print(token, end='', flush=True)

# Conversation with context
with device.conversation() as chat:
    chat.send("My name is Alice")
    response = chat.send("What's my name?")  # Device remembers

# Batch processing
responses = device.batch_generate(["prompt 1", "prompt 2", "prompt 3"])`}
                  </pre>
                </div>

                <div className="grid lg:grid-cols-2 gap-8">
                  <div className="p-6 rounded-xl bg-white/5 border border-white/10">
                    <h4 className="font-semibold mb-4 text-violet-400">REST API Server</h4>
                    <p className="text-sm text-gray-400 mb-4">
                      OpenAI-compatible API for easy integration with existing tools.
                    </p>
                    <pre className="text-xs">
{`# Start the server
uvicorn ternaryair.server:app --port 8000

# Use like OpenAI API
curl http://localhost:8000/v1/completions \\
  -H "Content-Type: application/json" \\
  -d '{"prompt": "Hello", "max_tokens": 50}'`}
                    </pre>
                  </div>

                  <div className="p-6 rounded-xl bg-white/5 border border-white/10">
                    <h4 className="font-semibold mb-4 text-emerald-400">Model Conversion</h4>
                    <p className="text-sm text-gray-400 mb-4">
                      Convert PyTorch models to ternary format.
                    </p>
                    <pre className="text-xs">
{`from ternaryair.models import convert_pytorch_model

# Convert any model
result = convert_pytorch_model(my_model)
print(f"Sparsity: {result.sparsity:.1%}")
print(f"Compression: {result.compression_ratio}x")`}
                    </pre>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-4 text-center">SDK Features</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    {[
                      { name: 'Streaming', desc: 'Real-time output' },
                      { name: 'Batch Mode', desc: 'Multiple prompts' },
                      { name: 'Conversation', desc: 'Context retention' },
                      { name: 'Simulator', desc: 'No hardware needed' },
                      { name: 'CLI Tool', desc: 'Command line' },
                      { name: 'REST API', desc: 'OpenAI compatible' },
                      { name: 'Type Hints', desc: 'Full typing' },
                      { name: 'Async', desc: 'Non-blocking' },
                    ].map((feature) => (
                      <div key={feature.name} className="p-3 rounded-lg bg-white/5 text-center">
                        <div className="font-medium">{feature.name}</div>
                        <div className="text-xs text-gray-500">{feature.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'engineers' && (
              <div className="space-y-12">
                <div className="grid lg:grid-cols-2 gap-8">
                  <div>
                    <h3 className="text-2xl font-bold mb-4">The RAU: Key Innovation</h3>
                    <p className="text-gray-400 mb-4">
                      The Rotation-Accumulate Unit replaces multiplication with sign manipulation.
                      Ternary weights {-1, 0, +1} mean multiplication is just switching.
                    </p>
                    <div className="p-4 rounded-lg bg-black/40 border border-white/10 text-sm">
                      <div className="text-gray-500 mb-2">// Traditional MAC</div>
                      <div className="text-gray-300 mb-4">result = activation × weight  // ~500 gates</div>
                      <div className="text-gray-500 mb-2">// TernaryAir RAU</div>
                      <div className="text-emerald-400">result = activation ⊕ weight  // ~50 gates</div>
                      <div className="mt-4 text-cyan-400">→ 90% gate reduction, 90% power reduction</div>
                    </div>
                  </div>

                  <div>
                    <h3 className="text-2xl font-bold mb-4">Architecture</h3>
                    <pre className="text-xs ascii-art overflow-x-auto">
{`┌─────────────────────────────────────────────────┐
│              TERNARYAIR CHIP                     │
│                                                  │
│   USB ──▶ [Protocol] ──▶ [Input Buffer]        │
│                              │                   │
│                              ▼                   │
│                       ┌──────────────┐          │
│                       │  PE Array    │◀── Weight│
│                       │  12×8 RAU    │    ROM   │
│                       └──────────────┘          │
│                              │                   │
│                              ▼                   │
│                       [KV Cache] ──▶ USB        │
│                                                  │
│   Process: 28nm │ Power: 4W │ Speed: 100MHz    │
└─────────────────────────────────────────────────┘`}
                    </pre>
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-bold mb-4">RTL Modules</h3>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[
                      { name: 'top_level.sv', lines: 286, desc: 'Main inference engine, state machine, I/O' },
                      { name: 'rau.sv', lines: 169, desc: 'Rotation-Accumulate Unit — the key innovation' },
                      { name: 'synaptic_array.sv', lines: 150, desc: '12×8 PE array with tree adders' },
                      { name: 'weight_rom.sv', lines: 109, desc: 'Mask-locked ternary weight storage' },
                      { name: 'kv_cache.sv', lines: 100, desc: 'Key-value cache for attention' },
                    ].map((file) => (
                      <div key={file.name} className="p-4 rounded-lg bg-white/5 border border-white/10">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-mono text-sm text-cyan-400">{file.name}</span>
                          <span className="text-xs text-gray-500">{file.lines} lines</span>
                        </div>
                        <p className="text-xs text-gray-400">{file.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="grid lg:grid-cols-2 gap-8">
                  <div className="p-6 rounded-xl bg-white/5 border border-white/10">
                    <h4 className="font-semibold mb-4">FPGA Prototyping</h4>
                    <pre className="text-xs">
{`# Build bitstream for PYNQ-Z2
cd hardware/fpga
make bitstream BOARD=pynq-z2

# Program FPGA
make program BOARD=pynq-z2

# Or use pre-built
make flash-prebuilt BOARD=pynq-z2`}
                    </pre>
                  </div>

                  <div className="p-6 rounded-xl bg-white/5 border border-white/10">
                    <h4 className="font-semibold mb-4">RTL Simulation</h4>
                    <pre className="text-xs">
{`# Install Icarus Verilog
sudo apt install iverilog

# Compile and run
cd hardware/rtl
iverilog -g2012 -o sim *.sv
vvp sim

# View waveforms
gtkwave dump.vcd`}
                    </pre>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold mb-4 text-center">Physical Design</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    {[
                      { label: 'Process', value: '28nm LP' },
                      { label: 'Die Size', value: '100mm²' },
                      { label: 'Yield', value: '73.8%' },
                      { label: 'Die Cost', value: '$7.02' },
                      { label: 'Package', value: 'QFN-64' },
                      { label: 'Power', value: '4.0W' },
                      { label: 'Frequency', value: '100 MHz' },
                      { label: 'Efficiency', value: '25 tok/J' },
                    ].map((spec) => (
                      <div key={spec.label} className="p-3 rounded-lg bg-white/5 text-center">
                        <div className="text-lg font-bold text-cyan-400">{spec.value}</div>
                        <div className="text-xs text-gray-500">{spec.label}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Origin Story */}
      <section className="py-20 border-t border-white/10 bg-gradient-to-b from-transparent to-black/20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              The Origin Story
            </h2>
          </div>
          
          <blockquote className="text-lg md:text-xl text-gray-300 leading-relaxed space-y-4 italic">
            <p>
              I'm a fisherman and a developer.
            </p>
            <p>
              I needed AI that works on a boat, in the middle of nowhere, with no internet and
              limited power. Cloud AI doesn't work there. Local LLMs needed expensive GPUs I
              couldn't justify.
            </p>
            <p>
              So I designed my own architecture — efficient enough for USB power, cheap enough
              for anyone to afford, and secure enough that it can't be compromised.
            </p>
            <p>
              The mask-locked design started as a cost optimization. But I realized it's also
              the most secure AI architecture possible — the model is literally frozen in silicon.
            </p>
            <p>
              Now I'm open-sourcing everything. Build your own. Improve it. Use it for whatever
              you want.
            </p>
            <p className="text-cyan-400 font-semibold not-italic">
              AI should work for you, not the other way around.
            </p>
          </blockquote>
          
          <div className="text-center mt-8">
            <p className="text-gray-400">
              — <span className="font-semibold">Casey DiGennaro</span>, SuperInstance.AI
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 border-t border-white/10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
            Download everything for free. MIT licensed. No restrictions.
            Build something amazing.
          </p>
          
          <div className="flex flex-wrap justify-center gap-4">
            <a
              href="https://github.com/superinstance/ternaryair/archive/refs/heads/main.zip"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-cyan-500 to-violet-500 text-white font-semibold hover:opacity-90 transition-opacity"
            >
              <span>⬇️</span> Download Everything
            </a>
            <a
              href="https://github.com/superinstance/ternaryair"
              target="_blank"
              rel="noopener"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-white/10 border border-white/20 text-white font-semibold hover:bg-white/20 transition-colors"
            >
              <span>📦</span> View on GitHub
            </a>
          </div>
        </div>
      </section>
    </main>
  )
}
