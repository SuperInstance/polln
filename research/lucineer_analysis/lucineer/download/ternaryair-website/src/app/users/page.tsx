import Link from "next/link";
import {
  Shield,
  Lock,
  Eye,
  Wallet,
  Building,
  Stethoscope,
  Scale,
  GraduationCap,
  Home,
  CheckCircle,
  XCircle,
  ArrowRight,
  Download,
} from "lucide-react";

export default function UsersPage() {
  return (
    <div className="animated-bg min-h-screen pt-20">
      {/* Hero */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 bg-user/10 border border-user/30 rounded-full px-4 py-2 mb-6">
              <Shield className="w-4 h-4 text-user" />
              <span className="text-user text-sm font-medium">For Users</span>
            </div>

            <h1 className="text-4xl sm:text-5xl font-bold mb-6">
              <span className="gradient-text-user">Your AI, Your Privacy</span>
            </h1>

            <p className="text-xl text-gray-300 mb-4 max-w-3xl mx-auto">
              TernaryAir gives you powerful AI without compromising your privacy
            </p>

            <p className="text-gray-400 max-w-2xl mx-auto">
              No cloud. No data collection. No remembering what you said. Just
              smart AI that works for you, not against you.
            </p>
          </div>
        </div>
      </section>

      {/* What is TernaryAir */}
      <section id="what-is" className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-6">
                What is TernaryAir?
              </h2>

              <p className="text-gray-300 mb-4">
                TernaryAir is a small device that runs AI locally on your
                computer—like having a tiny, secure brain in a USB stick.
              </p>

              <p className="text-gray-300 mb-4">
                Unlike cloud AI services (like ChatGPT or Claude) that send your
                data to remote servers, TernaryAir runs entirely on your desk.
                Nothing leaves your computer. Ever.
              </p>

              <p className="text-gray-400 mb-6">
                The &quot;ternary&quot; part means it uses a simplified way of
                computing that&apos;s extremely efficient—making it affordable
                ($99) and able to run on USB power alone.
              </p>

              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-user flex-shrink-0" />
                  <span className="text-gray-300">
                    Runs AI without internet
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-user flex-shrink-0" />
                  <span className="text-gray-300">
                    Your data never leaves your device
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-user flex-shrink-0" />
                  <span className="text-gray-300">
                    Cannot be hacked or modified remotely
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <CheckCircle className="w-5 h-5 text-user flex-shrink-0" />
                  <span className="text-gray-300">
                    Forgets everything when powered off
                  </span>
                </div>
              </div>
            </div>

            <div className="code-block">
              <div className="code-header">
                <div className="code-dot bg-red-500" />
                <div className="code-dot bg-yellow-500" />
                <div className="code-dot bg-green-500" />
                <span className="ml-2 text-gray-400 text-sm">
                  How It Works
                </span>
              </div>
              <div className="code-content">
                <pre className="ascii-diagram">{`     YOUR COMPUTER                 TERNARYAIR
    ┌─────────────┐              ┌─────────────┐
    │             │              │             │
    │  Your Data  │   ──USB──▶   │  AI Brain   │
    │  Your Files │              │  (Frozen)   │
    │  Your Life  │   ◀──USB──   │             │
    │             │              │             │
    └─────────────┘              └─────────────┘
          │                             │
          │                             │
          ▼                             ▼
    ✗ Never sent to cloud        ✗ No network
    ✗ Never stored               ✗ No memory
    ✗ Never logged               ✗ No hacking`}</pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Why It Matters */}
      <section id="why-matters" className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Why It Matters</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Understanding the risks of cloud AI and how TernaryAir protects
              you
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* The Problem */}
            <div className="bg-dark-800 rounded-xl p-6 border border-dark-600">
              <h3 className="text-xl font-semibold mb-4 text-red-400">
                The Problem with Cloud AI
              </h3>

              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-1" />
                  <div>
                    <div className="font-medium text-gray-200">
                      Your data leaves your device
                    </div>
                    <div className="text-sm text-gray-400">
                      Every prompt you send travels to someone else&apos;s
                      computer
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-1" />
                  <div>
                    <div className="font-medium text-gray-200">
                      Your conversations are stored
                    </div>
                    <div className="text-sm text-gray-400">
                      AI companies keep logs that can be hacked or subpoenaed
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-1" />
                  <div>
                    <div className="font-medium text-gray-200">
                      You can&apos;t verify what happens
                    </div>
                    <div className="text-sm text-gray-400">
                      Trust us&quot; isn&apos;t a security model
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-1" />
                  <div>
                    <div className="font-medium text-gray-200">
                      AI agents can access your system
                    </div>
                    <div className="text-sm text-gray-400">
                      Software agents with file and network access can be
                      exploited
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* The Solution */}
            <div className="bg-user/5 rounded-xl p-6 border border-user/30">
              <h3 className="text-xl font-semibold mb-4 text-user">
                How TernaryAir Solves This
              </h3>

              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-user flex-shrink-0 mt-1" />
                  <div>
                    <div className="font-medium text-gray-200">
                      Hardware-enforced isolation
                    </div>
                    <div className="text-sm text-gray-400">
                      Physically impossible to access your files or network
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-user flex-shrink-0 mt-1" />
                  <div>
                    <div className="font-medium text-gray-200">
                      No memory persistence
                    </div>
                    <div className="text-sm text-gray-400">
                      Forgets everything when you power it off
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-user flex-shrink-0 mt-1" />
                  <div>
                    <div className="font-medium text-gray-200">
                      Immutable model
                    </div>
                    <div className="text-sm text-gray-400">
                      The AI is frozen in hardware—can&apos;t be modified or
                      corrupted
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-user flex-shrink-0 mt-1" />
                  <div>
                    <div className="font-medium text-gray-200">
                      Verifiable security
                    </div>
                    <div className="text-sm text-gray-400">
                      Open source—you can verify every claim
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section id="use-cases" className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Use Cases</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Who benefits from air-gapped AI?
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Healthcare */}
            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500 card-hover">
              <div className="w-12 h-12 rounded-lg bg-red-500/10 flex items-center justify-center mb-4">
                <Stethoscope className="w-6 h-6 text-red-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Healthcare</h3>
              <p className="text-sm text-gray-400">
                Process patient data without PHI ever leaving your facility.
                HIPAA-compliant by design—no cloud transmission means no audit
                risk.
              </p>
            </div>

            {/* Legal */}
            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500 card-hover">
              <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center mb-4">
                <Scale className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Legal</h3>
              <p className="text-sm text-gray-400">
                Protect attorney-client privilege. No records, no logs, no
                subpoenas. Your client communications stay private.
              </p>
            </div>

            {/* Finance */}
            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500 card-hover">
              <div className="w-12 h-12 rounded-lg bg-green-500/10 flex items-center justify-center mb-4">
                <Building className="w-6 h-6 text-green-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Finance</h3>
              <p className="text-sm text-gray-400">
                Analyze sensitive financial data without exposure. Regulatory
                compliance built into the hardware.
              </p>
            </div>

            {/* Education */}
            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500 card-hover">
              <div className="w-12 h-12 rounded-lg bg-purple-500/10 flex items-center justify-center mb-4">
                <GraduationCap className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Education</h3>
              <p className="text-sm text-gray-400">
                Give students AI tools without exposing their data. Perfect for
                schools with strict privacy requirements.
              </p>
            </div>

            {/* Personal */}
            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500 card-hover">
              <div className="w-12 h-12 rounded-lg bg-primary-500/10 flex items-center justify-center mb-4">
                <Home className="w-6 h-6 text-primary-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Personal Use</h3>
              <p className="text-sm text-gray-400">
                Write personal documents, journal, or brainstorm without your
                thoughts being logged and analyzed.
              </p>
            </div>

            {/* Remote/Offline */}
            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500 card-hover">
              <div className="w-12 h-12 rounded-lg bg-amber-500/10 flex items-center justify-center mb-4">
                <Wallet className="w-6 h-6 text-amber-400" />
              </div>
              <h3 className="text-lg font-semibold mb-2">Remote Work</h3>
              <p className="text-sm text-gray-400">
                Works anywhere—on a boat, in a cabin, during travel. No internet
                required. USB powered.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Privacy & Security */}
      <section id="privacy" className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Privacy & Security</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Security you can verify, not just trust
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-dark-800 rounded-xl p-6 border border-dark-600">
              <div className="flex items-center gap-3 mb-4">
                <Lock className="w-6 h-6 text-user" />
                <h3 className="text-lg font-semibold">Physical Security</h3>
              </div>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>• No network hardware present on the device</li>
                <li>• Operates unchanged in a Faraday cage</li>
                <li>• Only USB communication possible</li>
                <li>• No retained state after power-off</li>
              </ul>
            </div>

            <div className="bg-dark-800 rounded-xl p-6 border border-dark-600">
              <div className="flex items-center gap-3 mb-4">
                <Eye className="w-6 h-6 text-user" />
                <h3 className="text-lg font-semibold">Verifiable Trust</h3>
              </div>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>• All designs are open source (MIT license)</li>
                <li>• You can build it yourself from scratch</li>
                <li>• No closed-source firmware or secrets</li>
                <li>• Independent audits welcome</li>
              </ul>
            </div>
          </div>

          <div className="mt-8 text-center">
            <Link
              href="/security"
              className="inline-flex items-center gap-2 text-user hover:text-user-light font-medium"
            >
              Read the full security model
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-user/10 to-dark-900">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Ready for Private AI?</h2>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
            Download TernaryAir and experience AI that respects your privacy.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/download"
              className="flex items-center gap-2 bg-user hover:bg-user-dark text-white px-8 py-4 rounded-lg font-medium transition-all glow-blue"
            >
              <Download className="w-5 h-5" />
              Download Now
            </Link>

            <Link
              href="/learning"
              className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-8 py-4 rounded-lg font-medium transition-all border border-dark-500"
            >
              Visit Learning Center
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
