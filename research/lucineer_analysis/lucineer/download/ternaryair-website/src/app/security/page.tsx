import Link from "next/link";
import { Shield, Lock, Eye, CheckCircle, XCircle, ArrowRight, Download } from "lucide-react";

export default function SecurityPage() {
  return (
    <div className="animated-bg min-h-screen pt-20">
      {/* Hero */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 bg-primary-500/10 border border-primary-500/30 rounded-full px-4 py-2 mb-6">
              <Shield className="w-4 h-4 text-primary-400" />
              <span className="text-primary-400 text-sm font-medium">Security Model</span>
            </div>

            <h1 className="text-4xl sm:text-5xl font-bold mb-6">
              <span className="gradient-text">Hardware-Enforced Security</span>
            </h1>

            <p className="text-xl text-gray-300 mb-4 max-w-3xl mx-auto">
              Security by physics, not by policy
            </p>

            <p className="text-gray-400 max-w-2xl mx-auto">
              The security model is enforced by the hardware architecture itself,
              making certain attacks physically impossible rather than just difficult.
            </p>
          </div>
        </div>
      </section>

      {/* Core Security Properties */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Core Security Properties</h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full max-w-4xl mx-auto">
              <thead>
                <tr className="border-b border-dark-500">
                  <th className="text-left py-4 px-4 text-gray-300">Property</th>
                  <th className="text-left py-4 px-4 text-gray-300">Mechanism</th>
                  <th className="text-center py-4 px-4 text-primary-400">Bypass Possibility</th>
                </tr>
              </thead>
              <tbody className="text-sm">
                <tr className="border-b border-dark-600">
                  <td className="py-4 px-4">No data exfiltration</td>
                  <td className="py-4 px-4 text-gray-400">No network hardware</td>
                  <td className="py-4 px-4 text-center text-green-400 font-bold">Impossible</td>
                </tr>
                <tr className="border-b border-dark-600">
                  <td className="py-4 px-4">No persistent memory</td>
                  <td className="py-4 px-4 text-gray-400">Volatile SRAM only</td>
                  <td className="py-4 px-4 text-center text-green-400 font-bold">Impossible</td>
                </tr>
                <tr className="border-b border-dark-600">
                  <td className="py-4 px-4">Immutable model</td>
                  <td className="py-4 px-4 text-gray-400">Mask-locked ROM</td>
                  <td className="py-4 px-4 text-center text-green-400 font-bold">Impossible</td>
                </tr>
                <tr className="border-b border-dark-600">
                  <td className="py-4 px-4">Agent isolation</td>
                  <td className="py-4 px-4 text-gray-400">Hardware boundary</td>
                  <td className="py-4 px-4 text-center text-green-400 font-bold">Impossible</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Air-Gapped Architecture */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-6">Air-Gapped Architecture</h2>
              <p className="text-gray-300 mb-4">
                TernaryAir has <strong>no network capability</strong> — this is enforced
                at the hardware level. The device physically cannot connect to any network.
              </p>
              <p className="text-gray-400 mb-6">
                This is fundamentally different from software firewalls or air-gapped
                computers, which could be compromised. TernaryAir&apos;s lack of network
                hardware means data exfiltration is not just prevented — it&apos;s
                physically impossible.
              </p>

              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <XCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                  <span className="text-gray-300">NO network interface (physically not present)</span>
                </div>
                <div className="flex items-center gap-3">
                  <XCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                  <span className="text-gray-300">NO file system access (no storage controller)</span>
                </div>
                <div className="flex items-center gap-3">
                  <XCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                  <span className="text-gray-300">NO persistent memory (volatile SRAM only)</span>
                </div>
                <div className="flex items-center gap-3">
                  <XCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                  <span className="text-gray-300">NO programmable cores (fixed-function only)</span>
                </div>
              </div>
            </div>

            <div className="code-block">
              <div className="code-header">
                <div className="code-dot bg-red-500" />
                <div className="code-dot bg-yellow-500" />
                <div className="code-dot bg-green-500" />
                <span className="ml-2 text-gray-400 text-sm">Security Architecture</span>
              </div>
              <div className="code-content">
                <pre className="ascii-diagram">{`┌──────────────────────────────────────────────────────┐
│                  YOUR COMPUTER                        │
│  [Files] [Network] [Apps] [AI Agents]                │
└──────────────────────────────────────────────────────┘
                       │ USB Only
                       ▼
┌──────────────────────────────────────────────────────┐
│                TERNARYAIR DEVICE                      │
│                                                       │
│   ✗ NO network interface (physically not present)    │
│   ✗ NO file system access (no storage controller)    │
│   ✗ NO persistent memory (volatile SRAM only)        │
│   ✗ NO programmable cores (fixed-function only)      │
│                                                       │
│   It's a FUNCTION, not a PROGRAM.                    │
│   Input → Inference → Output. Nothing else.          │
│                                                       │
└──────────────────────────────────────────────────────┘`}</pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mask-Locked Weights */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Mask-Locked Weights</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              The AI model is literally frozen in silicon. It cannot be read, modified, or stolen.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto">
            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500">
              <h3 className="text-xl font-semibold mb-4 text-primary-400">What It Means</h3>
              <ul className="space-y-3 text-sm text-gray-300">
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-primary-400 mt-0.5" />
                  <span><strong>Cannot be read</strong> — It&apos;s geometry, not data</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-primary-400 mt-0.5" />
                  <span><strong>Cannot be modified</strong> — It&apos;s solid metal patterns</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-primary-400 mt-0.5" />
                  <span><strong>Cannot be extracted</strong> — Requires destructive analysis</span>
                </li>
              </ul>
            </div>

            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500">
              <h3 className="text-xl font-semibold mb-4 text-amber-400">Extraction Requirements</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>1. Physical decapsulation (destroys the chip)</li>
                <li>2. Electron microscopy imaging</li>
                <li>3. Manual via pattern tracing</li>
                <li>4. Weeks of work</li>
              </ul>
              <div className="mt-4 pt-4 border-t border-dark-500 text-xs text-gray-500">
                Cost: $100,000+ | Result: Destroyed chip, one extracted model
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Agent Isolation */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Agent Isolation</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              AI agents run as software. Software can be compromised. TernaryAir creates a
              hardware boundary that software cannot cross.
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl mx-auto">
            <div className="bg-red-500/5 border border-red-500/30 rounded-xl p-6">
              <h3 className="text-xl font-semibold mb-4 text-red-400">Without TernaryAir</h3>
              <div className="code-block">
                <div className="code-content font-mono text-xs">
                  <pre className="ascii-diagram text-red-300">{`    AI Agent
        │
        ├──▶ [Read Files]
        ├──▶ [Access Network]
        ├──▶ [Execute Commands]
        └──▶ [Remember Everything]

    Risk: Agent can do anything you can do`}</pre>
                </div>
              </div>
            </div>

            <div className="bg-primary-500/5 border border-primary-500/30 rounded-xl p-6">
              <h3 className="text-xl font-semibold mb-4 text-primary-400">With TernaryAir</h3>
              <div className="code-block">
                <div className="code-content font-mono text-xs">
                  <pre className="ascii-diagram">{`    AI Agent
        │
        └──▶ [Hardware Boundary]
                  │
                  ├──✗ NO FILES
                  ├──✗ NO NETWORK  
                  └──✗ NO MEMORY
                      │
                      ▼
               TEXT OUTPUT ONLY`}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Verification */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Verifiable Security</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              You don&apos;t have to trust us. You can verify every claim.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {[
              { title: "Physical Inspection", desc: "No network hardware present" },
              { title: "Functional Testing", desc: "Operates in Faraday cage unchanged" },
              { title: "Traffic Monitoring", desc: "Only USB communication detected" },
              { title: "Power Cycle Test", desc: "No retained state after power-off" },
            ].map((item) => (
              <div key={item.title} className="bg-dark-700 rounded-xl p-6 border border-dark-500 text-center">
                <Eye className="w-8 h-8 text-primary-400 mx-auto mb-4" />
                <h3 className="font-semibold mb-2">{item.title}</h3>
                <p className="text-sm text-gray-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-primary-900/20 to-dark-900">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Audit the Code</h2>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
            All designs are open source. Download and verify for yourself.
          </p>
          <a
            href="https://github.com/superinstance/ternaryair"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-8 py-4 rounded-lg font-medium transition-all glow-green"
          >
            <Download className="w-5 h-5" />
            View Source Code
          </a>
        </div>
      </section>
    </div>
  );
}
