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
  CheckCircle,
  XCircle,
} from "lucide-react";

export default function Home() {
  return (
    <div className="animated-bg min-h-screen">
      {/* Hero Section */}
      <section className="relative hero-gradient pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        {/* Background effects */}
        <div className="absolute inset-0 grid-pattern opacity-30" />
        <div className="absolute top-1/4 left-10 w-96 h-96 bg-green-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-10 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl" />
        <div className="absolute top-1/3 right-1/4 w-64 h-64 bg-purple-500/5 rounded-full blur-3xl" />
        
        <div className="max-w-7xl mx-auto relative">
          <div className="text-center mb-12">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-full px-5 py-2 mb-8 pulse-glow">
              <Shield className="w-4 h-4 text-green-400" />
              <span className="text-green-400 text-sm font-medium">
                Open Source • Air-Gapped • Secure
              </span>
            </div>

            {/* Title */}
            <h1 className="text-5xl sm:text-6xl lg:text-8xl font-bold mb-6 text-shadow">
              <span className="gradient-text">TernaryAir</span>
            </h1>

            {/* Tagline */}
            <p className="text-2xl sm:text-3xl text-gray-200 mb-4 font-medium">
              The hardware boundary between you and AI
            </p>

            <p className="text-lg text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
              Open-source ternary inference hardware. Secure, private, and
              affordable AI inference that runs locally without network access.
              MIT licensed for everyone.
            </p>

            {/* Download Buttons */}
            <div className="flex flex-wrap justify-center gap-4 mb-12">
              <Link
                href="/download"
                className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-7 py-3.5 rounded-xl font-medium transition-all glow-green shadow-lg"
              >
                <Download className="w-5 h-5" />
                Full Repository (ZIP)
              </Link>

              <button
                onClick={() => {
                  navigator.clipboard.writeText("pip install ternaryair");
                }}
                className="flex items-center gap-2 bg-dark-700/80 hover:bg-dark-600 text-white px-7 py-3.5 rounded-xl font-medium transition-all border border-dark-500 hover:border-dark-400"
              >
                <Terminal className="w-5 h-5 text-green-400" />
                <code className="text-sm">pip install ternaryair</code>
              </button>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-3xl mx-auto">
              {[
                { value: "$99", label: "Target Price" },
                { value: "100+", label: "Tokens/sec" },
                { value: "3-5W", label: "USB Powered" },
                { value: "MIT", label: "Open Source" },
              ].map((stat) => (
                <div
                  key={stat.label}
                  className="bg-dark-800/60 backdrop-blur-sm rounded-xl p-5 border border-dark-600 hover:border-green-500/30 transition-colors"
                >
                  <div className="text-2xl font-bold text-green-400">{stat.value}</div>
                  <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Security Model ASCII */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-dark-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 text-green-400 mb-4">
              <Lock className="w-6 h-6" />
            </div>
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Hardware-Enforced Security
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              TernaryAir creates a physical boundary between AI agents and your
              system. The model is frozen in silicon—immutable, air-gapped, and
              secure by design.
            </p>
          </div>

          <div className="code-block max-w-4xl mx-auto">
            <div className="code-header">
              <div className="code-dot bg-red-500" />
              <div className="code-dot bg-yellow-500" />
              <div className="code-dot bg-green-500" />
              <span className="ml-2 text-gray-400 text-sm">
                Security Architecture
              </span>
            </div>
            <div className="code-content">
              <pre className="ascii-diagram">{`┌──────────────────────────────────────────────────────────────┐
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
              Whether you&apos;re a user, developer, or hardware engineer, we
              have documentation tailored for you.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Users */}
            <Link
              href="/users"
              className="group bg-dark-800/80 backdrop-blur-sm rounded-2xl p-8 border border-dark-600 card-hover hover:border-blue-500/30"
            >
              <div className="w-14 h-14 rounded-xl bg-blue-500/10 flex items-center justify-center mb-5 group-hover:bg-blue-500/20 transition-colors">
                <Users className="w-7 h-7 text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-blue-400">
                For Users
              </h3>
              <p className="text-gray-400 text-sm mb-5 leading-relaxed">
                Non-technical guide to understanding TernaryAir, why it matters,
                and how to use it for private AI.
              </p>
              <ul className="space-y-2.5 text-sm text-gray-500">
                {["What is TernaryAir?", "Privacy & Security Benefits", "Use Cases & Applications"].map((item) => (
                  <li key={item} className="flex items-center gap-2">
                    <ArrowRight className="w-4 h-4 text-blue-400" />
                    {item}
                  </li>
                ))}
              </ul>
            </Link>

            {/* Developers */}
            <Link
              href="/developers"
              className="group bg-dark-800/80 backdrop-blur-sm rounded-2xl p-8 border border-dark-600 card-hover hover:border-purple-500/30"
            >
              <div className="w-14 h-14 rounded-xl bg-purple-500/10 flex items-center justify-center mb-5 group-hover:bg-purple-500/20 transition-colors">
                <Code className="w-7 h-7 text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-purple-400">
                For Developers
              </h3>
              <p className="text-gray-400 text-sm mb-5 leading-relaxed">
                SDK documentation, API reference, code examples, and integration
                guides for building with TernaryAir.
              </p>
              <ul className="space-y-2.5 text-sm text-gray-500">
                {["Python SDK Quick Start", "API Reference", "Code Examples"].map((item) => (
                  <li key={item} className="flex items-center gap-2">
                    <ArrowRight className="w-4 h-4 text-purple-400" />
                    {item}
                  </li>
                ))}
              </ul>
            </Link>

            {/* Engineers */}
            <Link
              href="/engineers"
              className="group bg-dark-800/80 backdrop-blur-sm rounded-2xl p-8 border border-dark-600 card-hover hover:border-amber-500/30"
            >
              <div className="w-14 h-14 rounded-xl bg-amber-500/10 flex items-center justify-center mb-5 group-hover:bg-amber-500/20 transition-colors">
                <Cpu className="w-7 h-7 text-amber-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3 text-amber-400">
                For Engineers
              </h3>
              <p className="text-gray-400 text-sm mb-5 leading-relaxed">
                RTL source code, FPGA prototyping guides, architecture deep
                dives, and silicon design documentation.
              </p>
              <ul className="space-y-2.5 text-sm text-gray-500">
                {["RTL Architecture", "FPGA Prototyping", "Silicon Design"].map((item) => (
                  <li key={item} className="flex items-center gap-2">
                    <ArrowRight className="w-4 h-4 text-amber-400" />
                    {item}
                  </li>
                ))}
              </ul>
            </Link>
          </div>
        </div>
      </section>

      {/* Quick Start Code */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-dark-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-6">
                Get Started in Minutes
              </h2>
              <p className="text-gray-400 text-lg mb-6 leading-relaxed">
                Install the Python SDK and start running inference. Works with
                the simulator if you don&apos;t have hardware yet.
              </p>

              <div className="flex items-center gap-6 text-sm text-gray-400 mb-8">
                <div className="flex items-center gap-2">
                  <Zap className="w-4 h-4 text-green-400" />
                  Zero config
                </div>
                <div className="flex items-center gap-2">
                  <Package className="w-4 h-4 text-green-400" />
                  pip install
                </div>
                <div className="flex items-center gap-2">
                  <Shield className="w-4 h-4 text-green-400" />
                  Works offline
                </div>
              </div>

              <Link
                href="/developers"
                className="inline-flex items-center gap-2 text-green-400 hover:text-green-300 font-medium text-lg group"
              >
                View full documentation
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>

            <div className="code-block">
              <div className="code-header">
                <div className="code-dot bg-red-500" />
                <div className="code-dot bg-yellow-500" />
                <div className="code-dot bg-green-500" />
                <span className="ml-2 text-gray-400 text-sm">Python</span>
              </div>
              <div className="code-content font-mono text-sm">
                <div className="text-gray-500"># Install: pip install ternaryair</div>
                <br />
                <div>
                  <span className="text-purple-400">from</span>{" "}
                  <span className="text-blue-400">ternaryair</span>{" "}
                  <span className="text-purple-400">import</span>{" "}
                  <span className="text-amber-400">TernaryAir</span>, Simulator
                </div>
                <br />
                <div className="text-gray-500">
                  # Connect to device (or use simulator)
                </div>
                <div>
                  device = <span className="text-amber-400">TernaryAir</span>
                  (backend=<span className="text-amber-400">Simulator</span>())
                </div>
                <br />
                <div className="text-gray-500"># Generate text</div>
                <div>
                  response = device.<span className="text-blue-400">generate</span>
                  (<span className="text-green-400">
                    "Hello, how are you?"
                  </span>
                  )
                </div>
                <div>
                  <span className="text-purple-400">print</span>(response)
                </div>
                <br />
                <div className="text-gray-500"># Streaming</div>
                <div>
                  <span className="text-purple-400">for</span> token{" "}
                  <span className="text-purple-400">in</span> device.
                  <span className="text-blue-400">stream</span>
                  (<span className="text-green-400">
                    "Tell me a story"
                  </span>
                  ):
                </div>
                <div>
                  {"    "}
                  <span className="text-purple-400">print</span>(token,
                  end=<span className="text-green-400">""</span>,
                  flush=<span className="text-amber-400">True</span>)
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
              Compare TernaryAir&apos;s security and privacy guarantees against
              other AI solutions.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="comparison-table w-full max-w-4xl mx-auto">
              <thead>
                <tr>
                  <th className="text-left text-gray-300">Risk</th>
                  <th className="text-center text-gray-300">Cloud AI</th>
                  <th className="text-center text-gray-300">Local GPU</th>
                  <th className="text-center text-green-400">TernaryAir</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { risk: "Data leaves device", cloud: true, gpu: false, ternary: false },
                  { risk: "Model can be modified", cloud: true, gpu: true, ternary: false },
                  { risk: "Agent can access files", cloud: true, gpu: true, ternary: false },
                  { risk: "Agent can access network", cloud: true, gpu: "maybe", ternary: false },
                  { risk: "Remembers your inputs", cloud: true, gpu: true, ternary: false },
                  { risk: "Costs $500+", cloud: true, gpu: true, ternary: false },
                  { risk: "Open source", cloud: false, gpu: false, ternary: true },
                ].map((row) => (
                  <tr key={row.risk}>
                    <td className="text-gray-300">{row.risk}</td>
                    <td className="text-center">
                      {row.cloud ? (
                        <span className="text-red-400">✓ Yes</span>
                      ) : (
                        <span className="text-gray-500">✗ No</span>
                      )}
                    </td>
                    <td className="text-center">
                      {row.gpu === "maybe" ? (
                        <span className="text-yellow-400">⚠ Maybe</span>
                      ) : row.gpu ? (
                        <span className="text-red-400">✓ Yes</span>
                      ) : (
                        <span className="text-green-400">✗ No</span>
                      )}
                    </td>
                    <td className="text-center">
                      {row.ternary ? (
                        <span className="text-green-400 font-bold">✓ MIT</span>
                      ) : (
                        <span className="text-green-400 font-bold">✗ No</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Key Innovation */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-dark-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 text-amber-400 mb-4">
                <Cpu className="w-6 h-6" />
              </div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-6">
                The RAU: Our Key Innovation
              </h2>
              <p className="text-gray-400 text-lg mb-6 leading-relaxed">
                The Rotation-Accumulate Unit replaces multiplication with sign
                manipulation, achieving 90% gate reduction and 85% power
                reduction compared to traditional multipliers.
              </p>

              <div className="space-y-4 mb-8">
                <div className="bg-dark-700/50 rounded-xl p-5 border border-dark-600">
                  <div className="text-sm text-gray-500 mb-2">
                    Traditional MAC
                  </div>
                  <div className="font-mono text-lg">result = activation × weight</div>
                  <div className="text-xs text-gray-500 mt-2">
                    Gates: ~500 per bit | Power: High
                  </div>
                </div>

                <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-5">
                  <div className="text-sm text-green-400 mb-2">
                    TernaryAir RAU
                  </div>
                  <div className="font-mono text-lg">result = activation ⊕ weight</div>
                  <div className="text-xs text-green-400/70 mt-2">
                    Gates: ~50 total | Power: Low
                  </div>
                </div>
              </div>

              <Link
                href="/architecture"
                className="inline-flex items-center gap-2 text-green-400 hover:text-green-300 font-medium text-lg group"
              >
                Explore the architecture
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>

            <div className="code-block">
              <div className="code-header">
                <div className="code-dot bg-red-500" />
                <div className="code-dot bg-yellow-500" />
                <div className="code-dot bg-green-500" />
                <span className="ml-2 text-gray-400 text-sm">
                  Ternary Weight Encoding
                </span>
              </div>
              <div className="code-content font-mono text-sm">
                <div className="text-gray-500">
                  // Ternary weights {"{-1, 0, +1}"} mean:
                </div>
                <br />
                <div>
                  <span className="text-green-400">+1</span>: Pass activation through
                </div>
                <div>
                  <span className="text-gray-400"> 0</span>: Zero output
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
                <div>
                  {"    "}W_PLUS_ONE: rotated = activation;
                </div>
                <div>
                  {"    "}W_ZERO: rotated = <span className="text-amber-400">0</span>;
                </div>
                <div>
                  {"    "}W_MINUS_ONE: rotated = -activation;
                </div>
                <div>
                  <span className="text-purple-400">endcase</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Origin Story Teaser */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <div className="bg-dark-800/50 rounded-2xl p-10 border border-dark-600 relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 to-transparent" />
            <div className="relative">
              <blockquote className="text-xl sm:text-2xl text-gray-300 italic mb-6 leading-relaxed">
                &ldquo;I&apos;m a fisherman and a developer. I needed AI that works
                on a boat, in the middle of nowhere, with no internet and limited
                power. So I designed my own architecture.&rdquo;
              </blockquote>

              <p className="text-gray-400 mb-6">
                — <span className="font-semibold text-white">Casey DiGennaro</span>, Founder of SuperInstance.AI
              </p>

              <Link
                href="/origin-story"
                className="inline-flex items-center gap-2 text-green-400 hover:text-green-300 font-medium group"
              >
                Read the full origin story
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-green-900/20 via-dark-900 to-dark-900">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-6">
            Ready to Get Started?
          </h2>
          <p className="text-gray-400 text-lg mb-10 max-w-2xl mx-auto leading-relaxed">
            Download TernaryAir and start running secure, private AI inference
            today. MIT licensed, open source, and built for everyone.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/download"
              className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-8 py-4 rounded-xl font-medium transition-all glow-green shadow-lg"
            >
              <Download className="w-5 h-5" />
              Download Now
            </Link>

            <a
              href="https://github.com/superinstance/ternaryair"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 bg-dark-700/80 hover:bg-dark-600 text-white px-8 py-4 rounded-xl font-medium transition-all border border-dark-500"
            >
              <Github className="w-5 h-5" />
              View on GitHub
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
