import Link from "next/link";
import {
  Shield,
  Lock,
  Eye,
  Zap,
  CheckCircle,
  XCircle,
  AlertTriangle,
  ArrowRight,
} from "lucide-react";

export default function SecurityPage() {
  return (
    <div className="min-h-screen pt-24 pb-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="w-16 h-16 rounded-2xl bg-green-500/10 flex items-center justify-center mx-auto mb-6">
            <Shield className="w-8 h-8 text-green-400" />
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="gradient-text">Security Model</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Understanding why TernaryAir is the most secure way to use AI. Hardware-enforced isolation, immutable models, and zero data exposure.
          </p>
        </div>

        {/* Core Principle */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Lock className="w-6 h-6 text-green-400" />
            Core Principle: Physical Isolation
          </h2>

          <div className="feature-card mb-8">
            <p className="text-gray-300 text-lg mb-6">
              TernaryAir creates a <span className="text-green-400 font-semibold">physical boundary</span> between AI inference and your computer. 
              Unlike software AI that runs on your CPU/GPU, TernaryAir is a separate device with no shared resources.
            </p>

            <div className="code-block mb-6">
              <div className="code-header">
                <span className="text-gray-400 text-sm">The Isolation Model</span>
              </div>
              <div className="code-content">
                <pre className="ascii-diagram">{`┌──────────────────────────────────────────────────────────────┐
│                      YOUR COMPUTER                           │
│                                                              │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│   │   Files     │  │   Network   │  │   Camera    │        │
│   │   (Full)    │  │   (Full)    │  │   (Full)    │        │
│   └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                              │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│   │   Memory    │  │   Keyboard  │  │   Browser   │        │
│   │   (Full)    │  │   (Full)    │  │   (Full)    │        │
│   └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                              │
│   ══════════════════════════════════════════════════════   │
│                      USB INTERFACE                          │
│   (Only data: text in → text out. Nothing else.)          │
│   ══════════════════════════════════════════════════════   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                         │ USB
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                    TERNARYAIR DEVICE                         │
│                                                              │
│   ✗ No filesystem access                                    │
│   ✗ No network interface                                    │
│   ✗ No camera/microphone                                    │
│   ✗ No keyboard/mouse                                       │
│   ✗ No persistent memory                                    │
│   ✗ No code execution                                       │
│                                                              │
│   ✓ Text input → Inference → Text output                   │
│   ✓ That's IT.                                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘`}</pre>
              </div>
            </div>
          </div>
        </section>

        {/* Threat Model */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Eye className="w-6 h-6 text-green-400" />
            Threat Model Comparison
          </h2>

          <div className="overflow-x-auto mb-6">
            <table className="comparison-table w-full">
              <thead>
                <tr>
                  <th className="text-left text-gray-300">Threat</th>
                  <th className="text-center text-gray-300">Cloud AI</th>
                  <th className="text-center text-gray-300">Local Software</th>
                  <th className="text-center text-green-400">TernaryAir</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="text-gray-300">Data leaves your device</td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><CheckCircle className="w-5 h-5 text-green-400 mx-auto" /></td>
                  <td className="text-center"><CheckCircle className="w-5 h-5 text-green-400 mx-auto" /></td>
                </tr>
                <tr>
                  <td className="text-gray-300">Model can be changed remotely</td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><CheckCircle className="w-5 h-5 text-green-400 mx-auto" /></td>
                </tr>
                <tr>
                  <td className="text-gray-300">AI can access your files</td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><CheckCircle className="w-5 h-5 text-green-400 mx-auto" /></td>
                </tr>
                <tr>
                  <td className="text-gray-300">AI can access network</td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><AlertTriangle className="w-5 h-5 text-yellow-400 mx-auto" /></td>
                  <td className="text-center"><CheckCircle className="w-5 h-5 text-green-400 mx-auto" /></td>
                </tr>
                <tr>
                  <td className="text-gray-300">Conversation history stored</td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><AlertTriangle className="w-5 h-5 text-yellow-400 mx-auto" /></td>
                  <td className="text-center"><CheckCircle className="w-5 h-5 text-green-400 mx-auto" /></td>
                </tr>
                <tr>
                  <td className="text-gray-300">Supply chain attacks possible</td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><CheckCircle className="w-5 h-5 text-green-400 mx-auto" /></td>
                </tr>
                <tr>
                  <td className="text-gray-300">Prompt injection attacks</td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><XCircle className="w-5 h-5 text-red-400 mx-auto" /></td>
                  <td className="text-center"><CheckCircle className="w-5 h-5 text-green-400 mx-auto" /></td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        {/* Key Security Properties */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Zap className="w-6 h-6 text-green-400" />
            Key Security Properties
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="feature-card">
              <Lock className="w-8 h-8 text-green-400 mb-4" />
              <h3 className="font-semibold text-lg mb-2">Immutable Model</h3>
              <p className="text-gray-400 text-sm">
                The AI model is physically encoded in silicon. It cannot be modified, updated, or corrupted by software. 
                To change the model, you need a new chip.
              </p>
            </div>

            <div className="feature-card">
              <Shield className="w-8 h-8 text-green-400 mb-4" />
              <h3 className="font-semibold text-lg mb-2">No Persistent Storage</h3>
              <p className="text-gray-400 text-sm">
                TernaryAir uses only volatile SRAM. Power off the device, and all conversation data is instantly gone. 
                No logs, no history, no traces.
              </p>
            </div>

            <div className="feature-card">
              <Eye className="w-8 h-8 text-green-400 mb-4" />
              <h3 className="font-semibold text-lg mb-2">Air-Gapped by Design</h3>
              <p className="text-gray-400 text-sm">
                No network hardware. No WiFi, no Ethernet, no Bluetooth. The only way data enters or leaves is through 
                the USB text interface.
              </p>
            </div>

            <div className="feature-card">
              <CheckCircle className="w-8 h-8 text-green-400 mb-4" />
              <h3 className="font-semibold text-lg mb-2">Open Source & Auditable</h3>
              <p className="text-gray-400 text-sm">
                Complete RTL source is MIT licensed. Anyone can audit the hardware design. No hidden backdoors, 
                no secret telemetry.
              </p>
            </div>
          </div>
        </section>

        {/* Use Cases */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6">Security-Focused Use Cases</h2>

          <div className="space-y-4">
            <div className="feature-card">
              <h3 className="font-semibold mb-2">Journalists & Whistleblowers</h3>
              <p className="text-gray-400 text-sm">
                Research sensitive topics without leaving traces. No server logs, no API records, no cloud storage.
              </p>
            </div>

            <div className="feature-card">
              <h3 className="font-semibold mb-2">Healthcare & Legal</h3>
              <p className="text-gray-400 text-sm">
                Process sensitive documents without data exposure. HIPAA and attorney-client privilege protected by physics.
              </p>
            </div>

            <div className="feature-card">
              <h3 className="font-semibold mb-2">Defense & Government</h3>
              <p className="text-gray-400 text-sm">
                Air-gapped environments need AI too. TernaryAir works in SCIFs and classified networks.
              </p>
            </div>

            <div className="feature-card">
              <h3 className="font-semibold mb-2">Personal Privacy</h3>
              <p className="text-gray-400 text-sm">
                Keep your thoughts private. Your AI conversations are nobody&apos;s business but yours.
              </p>
            </div>
          </div>
        </section>

        {/* CTA */}
        <div className="bg-gradient-to-br from-green-500/10 to-green-900/10 border border-green-500/30 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold mb-4">Experience Private AI</h3>
          <p className="text-gray-400 mb-6">
            Download TernaryAir and start using AI without compromising your privacy.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/download" className="btn-primary">
              Download Now
            </Link>
            <Link href="/users" className="btn-secondary">
              Learn More
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
