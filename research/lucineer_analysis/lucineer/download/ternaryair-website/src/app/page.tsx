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
} from "lucide-react";

export default function Home() {
  return (
    <div className="animated-bg min-h-screen">
      {/* Hero Section */}
      <section className="relative hero-gradient pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 bg-primary-500/10 border border-primary-500/30 rounded-full px-4 py-2 mb-6">
              <Shield className="w-4 h-4 text-primary-400" />
              <span className="text-primary-400 text-sm font-medium">
                Open Source • Air-Gapped • Secure
              </span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold mb-6 text-shadow">
              <span className="gradient-text">TernaryAir</span>
            </h1>

            <p className="text-xl sm:text-2xl text-gray-300 mb-4 max-w-3xl mx-auto">
              The hardware boundary between you and AI
            </p>

            <p className="text-lg text-gray-400 mb-8 max-w-2xl mx-auto">
              Open-source ternary inference hardware. Secure, private, and
              affordable AI inference that runs locally without network access.
            </p>

            {/* Download Buttons */}
            <div className="flex flex-wrap justify-center gap-4 mb-12">
              <Link
                href="/download"
                className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-6 py-3 rounded-lg font-medium transition-all glow-green"
              >
                <Download className="w-5 h-5" />
                Full Repository (ZIP)
              </Link>

              <button
                onClick={() => {
                  navigator.clipboard.writeText("pip install ternaryair");
                }}
                className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-6 py-3 rounded-lg font-medium transition-all border border-dark-500"
              >
                <Terminal className="w-5 h-5" />
                pip install ternaryair
              </button>

              <Link
                href="/download#rtl"
                className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-6 py-3 rounded-lg font-medium transition-all border border-dark-500"
              >
                <HardDrive className="w-5 h-5" />
                RTL Source
              </Link>

              <Link
                href="/download#docs"
                className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-6 py-3 rounded-lg font-medium transition-all border border-dark-500"
              >
                <FileText className="w-5 h-5" />
                Documentation
              </Link>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-3xl mx-auto">
              <div className="bg-dark-800/50 rounded-lg p-4 border border-dark-600">
                <div className="text-2xl font-bold text-primary-400">$99</div>
                <div className="text-sm text-gray-400">Target Price</div>
              </div>
              <div className="bg-dark-800/50 rounded-lg p-4 border border-dark-600">
                <div className="text-2xl font-bold text-primary-400">
                  100+
                </div>
                <div className="text-sm text-gray-400">Tokens/sec</div>
              </div>
              <div className="bg-dark-800/50 rounded-lg p-4 border border-dark-600">
                <div className="text-2xl font-bold text-primary-400">3-5W</div>
                <div className="text-sm text-gray-400">USB Powered</div>
              </div>
              <div className="bg-dark-800/50 rounded-lg p-4 border border-dark-600">
                <div className="text-2xl font-bold text-primary-400">MIT</div>
                <div className="text-sm text-gray-400">Open Source</div>
              </div>
            </div>
          </div>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-1/4 left-10 w-64 h-64 bg-primary-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-10 w-64 h-64 bg-blue-500/5 rounded-full blur-3xl" />
      </section>

      {/* Security Model ASCII */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">
              <Lock className="inline w-8 h-8 text-primary-400 mr-2" />
              Hardware-Enforced Security
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
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
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Choose Your Path</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Whether you&apos;re a user, developer, or hardware engineer, we
              have documentation tailored for you.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Users */}
            <Link
              href="/users"
              className="group bg-dark-800 rounded-xl p-6 border border-dark-600 card-hover glow-blue"
            >
              <div className="w-12 h-12 rounded-lg bg-user/10 flex items-center justify-center mb-4">
                <Users className="w-6 h-6 text-user" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-user">
                For Users
              </h3>
              <p className="text-gray-400 text-sm mb-4">
                Non-technical guide to understanding TernaryAir, why it matters,
                and how to use it for private AI.
              </p>
              <ul className="space-y-2 text-sm text-gray-500">
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-user" />
                  What is TernaryAir?
                </li>
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-user" />
                  Privacy & Security Benefits
                </li>
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-user" />
                  Use Cases & Applications
                </li>
              </ul>
            </Link>

            {/* Developers */}
            <Link
              href="/developers"
              className="group bg-dark-800 rounded-xl p-6 border border-dark-600 card-hover glow-purple"
            >
              <div className="w-12 h-12 rounded-lg bg-developer/10 flex items-center justify-center mb-4">
                <Code className="w-6 h-6 text-developer" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-developer">
                For Developers
              </h3>
              <p className="text-gray-400 text-sm mb-4">
                SDK documentation, API reference, code examples, and integration
                guides for building with TernaryAir.
              </p>
              <ul className="space-y-2 text-sm text-gray-500">
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-developer" />
                  Python SDK Quick Start
                </li>
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-developer" />
                  API Reference
                </li>
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-developer" />
                  Code Examples
                </li>
              </ul>
            </Link>

            {/* Engineers */}
            <Link
              href="/engineers"
              className="group bg-dark-800 rounded-xl p-6 border border-dark-600 card-hover glow-amber"
            >
              <div className="w-12 h-12 rounded-lg bg-engineer/10 flex items-center justify-center mb-4">
                <Cpu className="w-6 h-6 text-engineer" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-engineer">
                For Engineers
              </h3>
              <p className="text-gray-400 text-sm mb-4">
                RTL source code, FPGA prototyping guides, architecture deep
                dives, and silicon design documentation.
              </p>
              <ul className="space-y-2 text-sm text-gray-500">
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-engineer" />
                  RTL Architecture
                </li>
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-engineer" />
                  FPGA Prototyping
                </li>
                <li className="flex items-center gap-2">
                  <ArrowRight className="w-4 h-4 text-engineer" />
                  Silicon Design
                </li>
              </ul>
            </Link>
          </div>
        </div>
      </section>

      {/* Quick Start Code */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-4">
                Get Started in Minutes
              </h2>
              <p className="text-gray-400 mb-6">
                Install the Python SDK and start running inference. Works with
                the simulator if you don&apos;t have hardware yet.
              </p>

              <div className="flex items-center gap-3 text-sm text-gray-400 mb-6">
                <div className="flex items-center gap-1">
                  <Zap className="w-4 h-4 text-primary-400" />
                  Zero config
                </div>
                <div className="flex items-center gap-1">
                  <Package className="w-4 h-4 text-primary-400" />
                  pip install
                </div>
                <div className="flex items-center gap-1">
                  <Shield className="w-4 h-4 text-primary-400" />
                  Works offline
                </div>
              </div>

              <Link
                href="/developers"
                className="inline-flex items-center gap-2 text-primary-400 hover:text-primary-300 font-medium"
              >
                View full documentation
                <ArrowRight className="w-4 h-4" />
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
                  <span className="text-developer">from</span>{" "}
                  <span className="text-user">ternaryair</span>{" "}
                  <span className="text-developer">import</span>{" "}
                  <span className="text-engineer">TernaryAir</span>,
                  Simulator
                </div>
                <br />
                <div className="text-gray-500">
                  # Connect to device (or use simulator)
                </div>
                <div>
                  device = <span className="text-engineer">TernaryAir</span>
                  (backend=<span className="text-engineer">Simulator</span>())
                </div>
                <br />
                <div className="text-gray-500"># Generate text</div>
                <div>
                  response = device.<span className="text-user">generate</span>
                  (<span className="text-primary-400">
                    "Hello, how are you?"
                  </span>
                  )
                </div>
                <div>
                  <span className="text-developer">print</span>(response)
                </div>
                <br />
                <div className="text-gray-500"># Streaming</div>
                <div>
                  <span className="text-developer">for</span> token{" "}
                  <span className="text-developer">in</span> device.
                  <span className="text-user">stream</span>
                  (<span className="text-primary-400">
                    "Tell me a story"
                  </span>
                  ):
                </div>
                <div>
                  {"    "}
                  <span className="text-developer">print</span>(token,
                  end=<span className="text-primary-400">""</span>,
                  flush=<span className="text-engineer">True</span>)
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Comparison Table */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Why TernaryAir?</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
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
                  <th className="text-center text-primary-400">TernaryAir</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="text-gray-300">Data leaves device</td>
                  <td className="text-center text-red-400">✓ Yes</td>
                  <td className="text-center text-green-400">✗ No</td>
                  <td className="text-center text-primary-400 font-bold">
                    ✗ No
                  </td>
                </tr>
                <tr>
                  <td className="text-gray-300">Model can be modified</td>
                  <td className="text-center text-red-400">✓ Yes</td>
                  <td className="text-center text-red-400">✓ Yes</td>
                  <td className="text-center text-primary-400 font-bold">
                    ✗ No
                  </td>
                </tr>
                <tr>
                  <td className="text-gray-300">Agent can access files</td>
                  <td className="text-center text-red-400">✓ Yes</td>
                  <td className="text-center text-red-400">✓ Yes</td>
                  <td className="text-center text-primary-400 font-bold">
                    ✗ No
                  </td>
                </tr>
                <tr>
                  <td className="text-gray-300">Agent can access network</td>
                  <td className="text-center text-red-400">✓ Yes</td>
                  <td className="text-center text-yellow-400">⚠ Maybe</td>
                  <td className="text-center text-primary-400 font-bold">
                    ✗ No
                  </td>
                </tr>
                <tr>
                  <td className="text-gray-300">Remembers your inputs</td>
                  <td className="text-center text-red-400">✓ Yes</td>
                  <td className="text-center text-red-400">✓ Yes</td>
                  <td className="text-center text-primary-400 font-bold">
                    ✗ No
                  </td>
                </tr>
                <tr>
                  <td className="text-gray-300">Costs $500+</td>
                  <td className="text-center text-red-400">✓ Often</td>
                  <td className="text-center text-red-400">✓ Often</td>
                  <td className="text-center text-primary-400 font-bold">
                    ✗ $99
                  </td>
                </tr>
                <tr>
                  <td className="text-gray-300">Open source</td>
                  <td className="text-center text-red-400">✗ No</td>
                  <td className="text-center text-red-400">✗ No</td>
                  <td className="text-center text-primary-400 font-bold">
                    ✓ MIT
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Key Innovation */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-4">
                The RAU: Our Key Innovation
              </h2>
              <p className="text-gray-400 mb-6">
                The Rotation-Accumulate Unit replaces multiplication with sign
                manipulation, achieving 90% gate reduction and 85% power
                reduction compared to traditional multipliers.
              </p>

              <div className="space-y-4">
                <div className="bg-dark-700 rounded-lg p-4">
                  <div className="text-sm text-gray-400 mb-2">
                    Traditional MAC
                  </div>
                  <div className="font-mono text-sm">
                    result = activation × weight
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Gates: ~500 per bit | Power: High
                  </div>
                </div>

                <div className="bg-primary-500/10 border border-primary-500/30 rounded-lg p-4">
                  <div className="text-sm text-primary-400 mb-2">
                    TernaryAir RAU
                  </div>
                  <div className="font-mono text-sm">
                    result = activation ⊕ weight
                  </div>
                  <div className="text-xs text-primary-400/70 mt-1">
                    Gates: ~50 total | Power: Low
                  </div>
                </div>
              </div>

              <Link
                href="/architecture"
                className="inline-flex items-center gap-2 text-primary-400 hover:text-primary-300 font-medium mt-6"
              >
                Explore the architecture
                <ArrowRight className="w-4 h-4" />
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
                  <span className="text-primary-400">+1</span>: Pass
                  activation through
                </div>
                <div>
                  <span className="text-gray-400"> 0</span>: Zero output
                </div>
                <div>
                  <span className="text-developer">-1</span>: Negate
                  activation
                </div>
                <br />
                <div className="text-gray-500">
                  // No multiplier needed. 90% gate reduction.
                </div>
                <br />
                <div className="text-developer">always_comb</div>
                <div>
                  <span className="text-developer">case</span> (weight)
                </div>
                <div>
                  {"    "}W_PLUS_ONE: rotated = activation;
                </div>
                <div>
                  {"    "}W_ZERO: rotated = <span className="text-engineer">0</span>;
                </div>
                <div>
                  {"    "}W_MINUS_ONE: rotated = -activation;
                </div>
                <div>
                  <span className="text-developer">endcase</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Origin Story Teaser */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <blockquote className="text-xl sm:text-2xl text-gray-300 italic mb-6">
            &ldquo;I&apos;m a fisherman and a developer. I needed AI that works
            on a boat, in the middle of nowhere, with no internet and limited
            power. So I designed my own architecture.&rdquo;
          </blockquote>

          <p className="text-gray-400 mb-6">
            — Casey DiGennaro, Founder of SuperInstance.AI
          </p>

          <Link
            href="/origin-story"
            className="inline-flex items-center gap-2 text-primary-400 hover:text-primary-300 font-medium"
          >
            Read the full origin story
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-primary-900/20 to-dark-900">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
            Download TernaryAir and start running secure, private AI inference
            today. MIT licensed, open source, and built for everyone.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/download"
              className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-8 py-4 rounded-lg font-medium transition-all glow-green"
            >
              <Download className="w-5 h-5" />
              Download Now
            </Link>

            <a
              href="https://github.com/superinstance/ternaryair"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-8 py-4 rounded-lg font-medium transition-all border border-dark-500"
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
