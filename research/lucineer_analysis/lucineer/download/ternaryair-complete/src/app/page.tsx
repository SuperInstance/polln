import Link from "next/link";
import {
  Download,
  Shield,
  Zap,
  Lock,
  Cpu,
  Code,
  Users,
  ArrowRight,
  Github,
  Package,
  FileText,
  HardDrive,
  Terminal,
  CheckCircle2,
  XCircle,
  AlertCircle,
} from "lucide-react";

export default function Home() {
  return (
    <div className="animated-bg min-h-screen">
      {/* Hero Section */}
      <section className="relative hero-gradient pt-32 pb-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-full px-5 py-2 mb-8">
              <Shield className="w-4 h-4 text-green-400" />
              <span className="text-green-400 text-sm font-medium">
                Open Source MIT License • Air-Gapped by Design • $99 Retail
              </span>
            </div>

            {/* Main Headline */}
            <h1 className="text-5xl sm:text-6xl lg:text-8xl font-bold mb-6 text-shadow">
              <span className="gradient-text">TernaryAir</span>
            </h1>

            <p className="text-2xl sm:text-3xl text-gray-200 mb-4 max-w-3xl mx-auto font-medium">
              The Hardware Boundary Between You and AI
            </p>

            <p className="text-lg text-gray-400 mb-10 max-w-2xl mx-auto">
              Open-source mask-locked ternary inference chip. Secure, private, and affordable AI inference that runs locally without network access. Forever.
            </p>

            {/* Download Buttons */}
            <div className="flex flex-wrap justify-center gap-4 mb-16">
              <Link
                href="/download"
                className="btn-primary pulse-cta"
              >
                <Download className="w-5 h-5" />
                Download Everything (ZIP)
              </Link>

              <button
                onClick={() => {
                  navigator.clipboard.writeText("pip install ternaryair");
                }}
                className="btn-secondary"
              >
                <Terminal className="w-5 h-5" />
                pip install ternaryair
              </button>

              <a
                href="https://github.com/superinstance/ternaryair"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-secondary"
              >
                <Github className="w-5 h-5" />
                View on GitHub
              </a>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-4xl mx-auto">
              <div className="stat-card">
                <div className="value">$99</div>
                <div className="text-sm text-gray-400 mt-1">Target Price</div>
              </div>
              <div className="stat-card">
                <div className="value">100+</div>
                <div className="text-sm text-gray-400 mt-1">Tokens/sec</div>
              </div>
              <div className="stat-card">
                <div className="value">3-5W</div>
                <div className="text-sm text-gray-400 mt-1">USB Powered</div>
              </div>
              <div className="stat-card">
                <div className="value">MIT</div>
                <div className="text-sm text-gray-400 mt-1">Open Source</div>
              </div>
            </div>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-1/4 left-10 w-64 h-64 bg-green-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-10 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl" />
      </section>

      {/* Security Model ASCII */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-[#050505]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              <Lock className="inline w-8 h-8 text-green-400 mr-3" />
              Hardware-Enforced Security
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              TernaryAir creates a physical boundary between AI agents and your system. 
              The model is frozen in silicon—immutable, air-gapped, and secure by design.
            </p>
          </div>

          <div className="code-block max-w-4xl mx-auto">
            <div className="code-header">
              <div className="code-dot bg-red-500" />
              <div className="code-dot bg-yellow-500" />
              <div className="code-dot bg-green-500" />
              <span className="ml-2 text-gray-400 text-sm font-mono">Security Architecture</span>
            </div>
            <div className="code-content">
              <pre className="ascii-diagram">{`┌──────────────────────────────────────────────────────────────┐
│                      YOUR COMPUTER                           │
│  [Files] [Network] [Apps] [AI Agents] [Camera] [Mic]         │
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
│   ✗ No code execution     (fixed-function hardware)         │
│                                                              │
│   It's a FUNCTION, not a PROGRAM.                           │
│   Input → Inference → Output. Nothing else.                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘`}</pre>
            </div>
          </div>
        </div>
      </section>

      {/* Audience Paths */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Choose Your Path</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Whether you&apos;re a user, developer, or hardware engineer, we have comprehensive documentation tailored for you.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Users */}
            <Link
              href="/users"
              className="feature-card card-hover group"
            >
              <div className="w-14 h-14 rounded-xl bg-blue-500/10 flex items-center justify-center mb-5">
                <Users className="w-7 h-7 text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-blue-400">
                For Users
              </h3>
              <p className="text-gray-400 text-sm mb-5">
                Non-technical guide to understanding TernaryAir, why it matters for privacy, and how to use it for secure AI.
              </p>
              <ul className="space-y-2 text-sm text-gray-500">
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-blue-400" />
                  What is TernaryAir?
                </li>
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-blue-400" />
                  Privacy & Security Benefits
                </li>
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-blue-400" />
                  Use Cases & Applications
                </li>
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-blue-400" />
                  Getting Started Guide
                </li>
              </ul>
            </Link>

            {/* Developers */}
            <Link
              href="/developers"
              className="feature-card card-hover group"
            >
              <div className="w-14 h-14 rounded-xl bg-purple-500/10 flex items-center justify-center mb-5">
                <Code className="w-7 h-7 text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-purple-400">
                For Developers
              </h3>
              <p className="text-gray-400 text-sm mb-5">
                SDK documentation, API reference, code examples, and integration guides for building with TernaryAir.
              </p>
              <ul className="space-y-2 text-sm text-gray-500">
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-purple-400" />
                  Python SDK Quick Start
                </li>
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-purple-400" />
                  OpenAI-Compatible API
                </li>
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-purple-400" />
                  Code Examples & Tutorials
                </li>
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-purple-400" />
                  Integration Guides
                </li>
              </ul>
            </Link>

            {/* Engineers */}
            <Link
              href="/engineers"
              className="feature-card card-hover group"
            >
              <div className="w-14 h-14 rounded-xl bg-amber-500/10 flex items-center justify-center mb-5">
                <Cpu className="w-7 h-7 text-amber-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-amber-400">
                For Engineers
              </h3>
              <p className="text-gray-400 text-sm mb-5">
                RTL source code, FPGA prototyping guides, architecture deep dives, and silicon design documentation.
              </p>
              <ul className="space-y-2 text-sm text-gray-500">
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-amber-400" />
                  RTL Architecture
                </li>
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-amber-400" />
                  FPGA Prototyping
                </li>
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-amber-400" />
                  RAU Design Deep Dive
                </li>
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-amber-400" />
                  Silicon Implementation
                </li>
              </ul>
            </Link>
          </div>
        </div>
      </section>

      {/* Quick Start Code */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-[#050505]">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                Get Started in Minutes
              </h2>
              <p className="text-gray-400 mb-6 text-lg">
                Install the Python SDK and start running inference immediately. 
                Works with the simulator if you don&apos;t have hardware yet.
              </p>

              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-400 mb-8">
                <div className="flex items-center gap-2 bg-green-500/10 px-3 py-1.5 rounded-full">
                  <Zap className="w-4 h-4 text-green-400" />
                  Zero config
                </div>
                <div className="flex items-center gap-2 bg-green-500/10 px-3 py-1.5 rounded-full">
                  <Package className="w-4 h-4 text-green-400" />
                  pip install
                </div>
                <div className="flex items-center gap-2 bg-green-500/10 px-3 py-1.5 rounded-full">
                  <Shield className="w-4 h-4 text-green-400" />
                  Works offline
                </div>
              </div>

              <Link
                href="/developers"
                className="inline-flex items-center gap-2 text-green-400 hover:text-green-300 font-medium text-lg"
              >
                View full documentation
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>

            <div className="code-block">
              <div className="code-header">
                <div className="code-dot bg-red-500" />
                <div className="code-dot bg-yellow-500" />
                <div className="code-dot bg-green-500" />
                <span className="ml-2 text-gray-400 text-sm">Python SDK</span>
              </div>
              <div className="code-content font-mono text-sm">
                <div className="text-gray-500"># Install: pip install ternaryair</div>
                <br />
                <div>
                  <span className="text-purple-400">from</span>{" "}
                  <span className="text-blue-300">ternaryair</span>{" "}
                  <span className="text-purple-400">import</span>{" "}
                  <span className="text-amber-300">TernaryAir</span>, Simulator
                </div>
                <br />
                <div className="text-gray-500"># Connect to device (or use simulator)</div>
                <div>
                  device = <span className="text-amber-300">TernaryAir</span>
                  (backend=<span className="text-amber-300">Simulator</span>())
                </div>
                <br />
                <div className="text-gray-500"># Generate text</div>
                <div>
                  response = device.<span className="text-blue-300">generate</span>
                  (<span className="text-green-400">
                    &quot;Hello, how are you?&quot;
                  </span>)
                </div>
                <div>
                  <span className="text-purple-400">print</span>(response)
                </div>
                <br />
                <div className="text-gray-500"># Streaming output</div>
                <div>
                  <span className="text-purple-400">for</span> token{" "}
                  <span className="text-purple-400">in</span> device.
                  <span className="text-blue-300">stream</span>
                  (<span className="text-green-400">&quot;Tell me a story&quot;</span>):
                </div>
                <div>
                  {"    "}
                  <span className="text-purple-400">print</span>(token,
                  end=<span className="text-green-400">&quot;&quot;</span>,
                  flush=<span className="text-amber-300">True</span>)
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Comparison Table */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Why TernaryAir?</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Compare TernaryAir&apos;s security and privacy guarantees against other AI solutions.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="comparison-table w-full max-w-4xl mx-auto">
              <thead>
                <tr>
                  <th className="text-left text-gray-300">Security Risk</th>
                  <th className="text-center text-gray-300">Cloud AI</th>
                  <th className="text-center text-gray-300">Local GPU</th>
                  <th className="text-center text-green-400">TernaryAir</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="text-gray-300">Data leaves device</td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><CheckCircle2 className="w-5 h-5 text-green-400 mx-auto" /></td>
                  <td className="text-center"><CheckCircle2 className="w-5 h-5 text-green-400 mx-auto" /></td>
                </tr>
                <tr>
                  <td className="text-gray-300">Model can be modified remotely</td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><CheckCircle2 className="w-5 h-5 text-green-400 mx-auto" /></td>
                </tr>
                <tr>
                  <td className="text-gray-300">Agent can access your files</td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><CheckCircle2 className="w-5 h-5 text-green-400 mx-auto" /></td>
                </tr>
                <tr>
                  <td className="text-gray-300">Agent can access network</td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><AlertCircle className="w-5 h-5 text-yellow-400 mx-auto" /></td>
                  <td className="text-center"><CheckCircle2 className="w-5 h-5 text-green-400 mx-auto" /></td>
                </tr>
                <tr>
                  <td className="text-gray-300">Remembers your inputs</td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><CheckCircle2 className="w-5 h-5 text-green-400 mx-auto" /></td>
                </tr>
                <tr>
                  <td className="text-gray-300">Costs $500+</td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><CheckCircle2 className="w-5 h-5 text-green-400 mx-auto" /></td>
                </tr>
                <tr>
                  <td className="text-gray-300">Open source & auditable</td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><CheckCircle2 className="w-5 h-5 text-green-400 mx-auto" /></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Key Innovation */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-[#050505]">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-4">
                The RAU: Our Key Innovation
              </h2>
              <p className="text-gray-400 mb-6 text-lg">
                The Rotation-Accumulate Unit replaces multiplication with sign manipulation, 
                achieving <span className="text-green-400 font-semibold">90% gate reduction</span> and 
                <span className="text-green-400 font-semibold"> 85% power reduction</span> compared to traditional multipliers.
              </p>

              <div className="space-y-4 mb-8">
                <div className="bg-[#0a0a0a] border border-gray-700 rounded-xl p-5">
                  <div className="text-sm text-gray-400 mb-2">
                    Traditional MAC (Multiply-Accumulate)
                  </div>
                  <div className="font-mono text-sm text-gray-300">
                    result = activation × weight
                  </div>
                  <div className="text-xs text-gray-500 mt-2">
                    Gates: ~500 per bit | Power: High | Latency: 2+ cycles
                  </div>
                </div>

                <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-5">
                  <div className="text-sm text-green-400 mb-2 font-medium">
                    TernaryAir RAU (Rotation-Accumulate)
                  </div>
                  <div className="font-mono text-sm text-white">
                    result = ROTATE(activation, weight)
                  </div>
                  <div className="text-xs text-green-400/70 mt-2">
                    Gates: ~50 total | Power: Low | Latency: 1 cycle
                  </div>
                </div>
              </div>

              <Link
                href="/architecture"
                className="inline-flex items-center gap-2 text-green-400 hover:text-green-300 font-medium text-lg"
              >
                Explore the architecture
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>

            <div className="code-block">
              <div className="code-header">
                <div className="code-dot bg-red-500" />
                <div className="code-dot bg-yellow-500" />
                <div className="code-dot bg-green-500" />
                <span className="ml-2 text-gray-400 text-sm">Ternary Weight Encoding (SystemVerilog)</span>
              </div>
              <div className="code-content font-mono text-sm">
                <div className="text-gray-500">
                  // Ternary weights {"{-1, 0, +1}"} enable:
                </div>
                <br />
                <div>
                  <span className="text-green-400">+1</span>: Pass activation through unchanged
                </div>
                <div>
                  <span className="text-gray-400"> 0</span>: Zero output (no connection)
                </div>
                <div>
                  <span className="text-purple-400">-1</span>: Negate activation
                </div>
                <br />
                <div className="text-gray-500">
                  // No multiplier needed. 90% gate reduction.
                </div>
                <br />
                <div className="text-purple-400">always_comb</div>
                <div>
                  <span className="text-purple-400">case</span> (weight)
                </div>
                <div className="text-gray-300">
                  {"    "}W_PLUS_ONE: rotated = activation;
                </div>
                <div className="text-gray-300">
                  {"    "}W_ZERO: rotated = <span className="text-amber-300">32&apos;b0</span>;
                </div>
                <div className="text-gray-300">
                  {"    "}W_MINUS_ONE: rotated = -activation;
                </div>
                <div>
                  <span className="text-purple-400">endcase</span>
                </div>
                <br />
                <div className="text-gray-500">// Accumulate results</div>
                <div className="text-gray-300">
                  accumulator &lt;= accumulator + rotated;
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Origin Story Teaser */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <div className="feature-card">
            <blockquote className="text-xl sm:text-2xl text-gray-200 italic mb-6 leading-relaxed">
              &ldquo;I&apos;m a fisherman and a developer. I needed AI that works on a boat, 
              in the middle of nowhere, with no internet and limited power. 
              So I designed my own architecture—efficient enough for USB power, 
              secure enough that it can&apos;t be compromised, cheap enough for anyone.&rdquo;
            </blockquote>

            <p className="text-gray-400 mb-6">
              — <span className="text-green-400 font-medium">Casey DiGennaro</span>, Founder of SuperInstance.AI
            </p>

            <Link
              href="/origin-story"
              className="inline-flex items-center gap-2 text-green-400 hover:text-green-300 font-medium"
            >
              Read the full origin story
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Download Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-[#050505]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Download Everything</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Get the complete TernaryAir package: RTL source, Python SDK, documentation, and more.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="download-card">
              <div className="flex items-center gap-3 mb-3">
                <HardDrive className="w-6 h-6 text-green-400" />
                <h3 className="font-semibold">RTL Source</h3>
              </div>
              <p className="text-sm text-gray-400 mb-4">
                SystemVerilog RTL for RAU, synaptic array, KV cache, and top-level design.
              </p>
              <Link href="/download#rtl" className="text-green-400 text-sm hover:underline">
                View RTL →
              </Link>
            </div>

            <div className="download-card">
              <div className="flex items-center gap-3 mb-3">
                <Package className="w-6 h-6 text-green-400" />
                <h3 className="font-semibold">Python SDK</h3>
              </div>
              <p className="text-sm text-gray-400 mb-4">
                Full Python SDK with simulator, device driver, and OpenAI-compatible API.
              </p>
              <Link href="/download#sdk" className="text-green-400 text-sm hover:underline">
                pip install ternaryair →
              </Link>
            </div>

            <div className="download-card">
              <div className="flex items-center gap-3 mb-3">
                <FileText className="w-6 h-6 text-green-400" />
                <h3 className="font-semibold">Documentation</h3>
              </div>
              <p className="text-sm text-gray-400 mb-4">
                Complete docs for users, developers, and hardware engineers.
              </p>
              <Link href="/download#docs" className="text-green-400 text-sm hover:underline">
                View Documentation →
              </Link>
            </div>
          </div>

          <div className="text-center mt-10">
            <Link
              href="/download"
              className="btn-primary text-lg"
            >
              <Download className="w-5 h-5" />
              Download Complete Package (ZIP)
            </Link>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-green-900/20 to-[#050505]">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto text-lg">
            Download TernaryAir and start running secure, private AI inference today. 
            MIT licensed, open source, and built for everyone.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/download"
              className="btn-primary text-lg"
            >
              <Download className="w-5 h-5" />
              Download Now
            </Link>

            <a
              href="https://github.com/superinstance/ternaryair"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary text-lg"
            >
              <Github className="w-5 h-5" />
              Star on GitHub
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
