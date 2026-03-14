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
  Plane,
  Ship,
} from "lucide-react";

export default function UsersPage() {
  return (
    <div className="animated-bg min-h-screen pt-20">
      {/* Hero */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/30 rounded-full px-5 py-2 mb-6">
              <Shield className="w-4 h-4 text-blue-400" />
              <span className="text-blue-400 text-sm font-medium">For Users</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
              <span className="gradient-text-user">Your AI, Your Privacy</span>
            </h1>

            <p className="text-xl text-gray-300 mb-4 max-w-3xl mx-auto">
              TernaryAir gives you powerful AI without compromising your privacy
            </p>

            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              No cloud. No data collection. No remembering what you said. Just
              smart AI that works for you, not against you.
            </p>
          </div>
        </div>
      </section>

      {/* What is TernaryAir */}
      <section id="what-is" className="py-20 px-4 sm:px-6 lg:px-8 bg-dark-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl sm:text-4xl font-bold mb-6">
                What is TernaryAir?
              </h2>

              <p className="text-gray-300 text-lg mb-4 leading-relaxed">
                TernaryAir is a small device that runs AI locally on your
                computer—like having a tiny, secure brain in a USB stick.
              </p>

              <p className="text-gray-300 text-lg mb-4 leading-relaxed">
                Unlike cloud AI services (like ChatGPT or Claude) that send your
                data to remote servers, TernaryAir runs entirely on your desk.
                Nothing leaves your computer. Ever.
              </p>

              <p className="text-gray-400 mb-8 leading-relaxed">
                The &quot;ternary&quot; part means it uses a simplified way of
                computing that&apos;s extremely efficient—making it affordable
                ($99 target) and able to run on USB power alone.
              </p>

              <div className="space-y-4">
                {[
                  "Runs AI without internet",
                  "Your data never leaves your device",
                  "Cannot be hacked or modified remotely",
                  "Forgets everything when powered off",
                ].map((item) => (
                  <div key={item} className="flex items-center gap-3">
                    <CheckCircle className="w-5 h-5 text-blue-400 flex-shrink-0" />
                    <span className="text-gray-300">{item}</span>
                  </div>
                ))}
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
      <section id="why-matters" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Why It Matters</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Understanding the risks of cloud AI and how TernaryAir protects you
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* The Problem */}
            <div className="bg-dark-800/80 rounded-2xl p-8 border border-dark-600">
              <h3 className="text-xl font-semibold mb-6 text-red-400 flex items-center gap-2">
                <XCircle className="w-5 h-5" />
                The Problem with Cloud AI
              </h3>

              <div className="space-y-5">
                {[
                  {
                    title: "Your data leaves your device",
                    desc: "Every prompt you send travels to someone else's computer",
                  },
                  {
                    title: "Your conversations are stored",
                    desc: "AI companies keep logs that can be hacked or subpoenaed",
                  },
                  {
                    title: "You can't verify what happens",
                    desc: '"Trust us" isn\'t a security model',
                  },
                  {
                    title: "AI agents can access your system",
                    desc: "Software agents with file and network access can be exploited",
                  },
                ].map((item) => (
                  <div key={item.title} className="flex items-start gap-3">
                    <XCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-medium text-gray-200">
                        {item.title}
                      </div>
                      <div className="text-sm text-gray-400">
                        {item.desc}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* The Solution */}
            <div className="bg-blue-500/5 rounded-2xl p-8 border border-blue-500/30">
              <h3 className="text-xl font-semibold mb-6 text-blue-400 flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                How TernaryAir Solves This
              </h3>

              <div className="space-y-5">
                {[
                  {
                    title: "Hardware-enforced isolation",
                    desc: "Physically impossible to access your files or network",
                  },
                  {
                    title: "No memory persistence",
                    desc: "Forgets everything when you power it off",
                  },
                  {
                    title: "Immutable model",
                    desc: "The AI is frozen in hardware—can't be modified or corrupted",
                  },
                  {
                    title: "Verifiable security",
                    desc: "Open source—you can verify every claim",
                  },
                ].map((item) => (
                  <div key={item.title} className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-medium text-gray-200">
                        {item.title}
                      </div>
                      <div className="text-sm text-gray-400">
                        {item.desc}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section id="use-cases" className="py-20 px-4 sm:px-6 lg:px-8 bg-dark-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Use Cases</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Who benefits from air-gapped AI?
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Healthcare */}
            <div className="bg-dark-800/80 rounded-2xl p-6 border border-dark-600 card-hover">
              <div className="w-14 h-14 rounded-xl bg-red-500/10 flex items-center justify-center mb-5">
                <Stethoscope className="w-7 h-7 text-red-400" />
              </div>
              <h3 className="text-lg font-semibold mb-3">Healthcare</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                Process patient data without PHI ever leaving your facility.
                HIPAA-compliant by design—no cloud transmission means no audit
                risk.
              </p>
            </div>

            {/* Legal */}
            <div className="bg-dark-800/80 rounded-2xl p-6 border border-dark-600 card-hover">
              <div className="w-14 h-14 rounded-xl bg-blue-500/10 flex items-center justify-center mb-5">
                <Scale className="w-7 h-7 text-blue-400" />
              </div>
              <h3 className="text-lg font-semibold mb-3">Legal</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                Protect attorney-client privilege. No records, no logs, no
                subpoenas. Your client communications stay private.
              </p>
            </div>

            {/* Finance */}
            <div className="bg-dark-800/80 rounded-2xl p-6 border border-dark-600 card-hover">
              <div className="w-14 h-14 rounded-xl bg-green-500/10 flex items-center justify-center mb-5">
                <Building className="w-7 h-7 text-green-400" />
              </div>
              <h3 className="text-lg font-semibold mb-3">Finance</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                Analyze sensitive financial data without exposure. Regulatory
                compliance built into the hardware.
              </p>
            </div>

            {/* Education */}
            <div className="bg-dark-800/80 rounded-2xl p-6 border border-dark-600 card-hover">
              <div className="w-14 h-14 rounded-xl bg-purple-500/10 flex items-center justify-center mb-5">
                <GraduationCap className="w-7 h-7 text-purple-400" />
              </div>
              <h3 className="text-lg font-semibold mb-3">Education</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                Give students AI tools without exposing their data. Perfect for
                schools with strict privacy requirements.
              </p>
            </div>

            {/* Personal */}
            <div className="bg-dark-800/80 rounded-2xl p-6 border border-dark-600 card-hover">
              <div className="w-14 h-14 rounded-xl bg-green-500/10 flex items-center justify-center mb-5">
                <Home className="w-7 h-7 text-green-400" />
              </div>
              <h3 className="text-lg font-semibold mb-3">Personal Use</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                Write personal documents, journal, or brainstorm without your
                thoughts being logged and analyzed.
              </p>
            </div>

            {/* Remote/Offline */}
            <div className="bg-dark-800/80 rounded-2xl p-6 border border-dark-600 card-hover">
              <div className="w-14 h-14 rounded-xl bg-amber-500/10 flex items-center justify-center mb-5">
                <Ship className="w-7 h-7 text-amber-400" />
              </div>
              <h3 className="text-lg font-semibold mb-3">Remote Work</h3>
              <p className="text-sm text-gray-400 leading-relaxed">
                Works anywhere—on a boat, in a cabin, during travel. No internet
                required. USB powered.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Privacy & Security */}
      <section id="privacy" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Privacy & Security</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Security you can verify, not just trust
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-dark-800/80 rounded-2xl p-8 border border-dark-600">
              <div className="flex items-center gap-3 mb-6">
                <Lock className="w-6 h-6 text-blue-400" />
                <h3 className="text-lg font-semibold">Physical Security</h3>
              </div>
              <ul className="space-y-3 text-sm text-gray-400">
                <li className="flex items-start gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  No network hardware present on the device
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  Operates unchanged in a Faraday cage
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  Only USB communication possible
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  No retained state after power-off
                </li>
              </ul>
            </div>

            <div className="bg-dark-800/80 rounded-2xl p-8 border border-dark-600">
              <div className="flex items-center gap-3 mb-6">
                <Eye className="w-6 h-6 text-blue-400" />
                <h3 className="text-lg font-semibold">Verifiable Trust</h3>
              </div>
              <ul className="space-y-3 text-sm text-gray-400">
                <li className="flex items-start gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  All designs are open source (MIT license)
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  You can build it yourself from scratch
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  No closed-source firmware or secrets
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  Independent audits welcome
                </li>
              </ul>
            </div>
          </div>

          <div className="mt-10 text-center">
            <Link
              href="/security"
              className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 font-medium group"
            >
              Read the full security model
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-900/20 to-dark-900">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-6">Ready for Private AI?</h2>
          <p className="text-gray-400 text-lg mb-10 max-w-2xl mx-auto">
            Download TernaryAir and experience AI that respects your privacy.
            MIT licensed, open source, forever free.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/download"
              className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white px-8 py-4 rounded-xl font-medium transition-all glow-blue shadow-lg"
            >
              <Download className="w-5 h-5" />
              Download Now
            </Link>

            <Link
              href="/learning"
              className="flex items-center gap-2 bg-dark-700/80 hover:bg-dark-600 text-white px-8 py-4 rounded-xl font-medium transition-all border border-dark-500"
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
