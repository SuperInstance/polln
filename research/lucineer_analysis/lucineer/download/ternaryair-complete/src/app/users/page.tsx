import Link from "next/link";
import {
  Users,
  Shield,
  Lock,
  Zap,
  CheckCircle,
  ArrowRight,
  BookOpen,
  Home,
  Briefcase,
  Plane,
  Heart,
} from "lucide-react";

export default function UsersPage() {
  return (
    <div className="min-h-screen pt-24 pb-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="w-16 h-16 rounded-2xl bg-blue-500/10 flex items-center justify-center mx-auto mb-6">
            <Users className="w-8 h-8 text-blue-400" />
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="gradient-text-user">For Users</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            A non-technical guide to understanding TernaryAir, why it matters for your privacy, 
            and how to use it for secure AI.
          </p>
        </div>

        {/* What is TernaryAir */}
        <section id="what-is" className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <BookOpen className="w-6 h-6 text-blue-400" />
            What is TernaryAir?
          </h2>
          
          <div className="feature-card mb-6">
            <p className="text-gray-300 text-lg leading-relaxed mb-6">
              TernaryAir is a <span className="text-blue-400 font-semibold">USB device that runs AI locally</span> on your computer. 
              Unlike cloud AI services like ChatGPT or Claude, TernaryAir works entirely offline—you don&apos;t need an internet 
              connection, and your conversations never leave your device.
            </p>
            
            <p className="text-gray-300 text-lg leading-relaxed mb-6">
              Think of it like a calculator: you plug it in, type your question, and get an answer. 
              The AI model is permanently &quot;baked into&quot; the hardware—it cannot be changed, hacked, or updated remotely. 
              This makes it the most secure way to use AI.
            </p>

            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-6">
              <h3 className="font-semibold text-blue-400 mb-3">Key Points</h3>
              <ul className="space-y-3 text-gray-300">
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
                  <span>Works <strong>completely offline</strong>—no internet required</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
                  <span><strong>No subscription fees</strong>—pay once, use forever</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
                  <span><strong>Your data stays private</strong>—nothing is sent to the cloud</span>
                </li>
                <li className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
                  <span><strong>AI model cannot be modified</strong>—it&apos;s frozen in hardware</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* Why It Matters */}
        <section id="why-matters" className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Shield className="w-6 h-6 text-blue-400" />
            Why It Matters
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="feature-card">
              <Lock className="w-8 h-8 text-blue-400 mb-4" />
              <h3 className="font-semibold text-lg mb-2">Privacy Protection</h3>
              <p className="text-gray-400 text-sm">
                When you use cloud AI, your conversations are stored on someone else&apos;s servers. 
                With TernaryAir, your data never leaves your desk. Period.
              </p>
            </div>

            <div className="feature-card">
              <Shield className="w-8 h-8 text-blue-400 mb-4" />
              <h3 className="font-semibold text-lg mb-2">Security Guarantee</h3>
              <p className="text-gray-400 text-sm">
                Cloud AI can be updated remotely. TernaryAir&apos;s model is physically embedded in silicon—it 
                cannot be changed without replacing the hardware.
              </p>
            </div>

            <div className="feature-card">
              <Zap className="w-8 h-8 text-blue-400 mb-4" />
              <h3 className="font-semibold text-lg mb-2">Always Available</h3>
              <p className="text-gray-400 text-sm">
                Works anywhere, anytime. No internet? No problem. Server down? Not your problem. 
                TernaryAir is always ready.
              </p>
            </div>

            <div className="feature-card">
              <Heart className="w-8 h-8 text-blue-400 mb-4" />
              <h3 className="font-semibold text-lg mb-2">No Surprises</h3>
              <p className="text-gray-400 text-sm">
                No subscription price hikes. No feature changes you didn&apos;t ask for. 
                What you buy is what you get—forever.
              </p>
            </div>
          </div>
        </section>

        {/* Use Cases */}
        <section id="use-cases" className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Briefcase className="w-6 h-6 text-blue-400" />
            Use Cases
          </h2>

          <div className="space-y-4">
            <div className="feature-card">
              <div className="flex items-start gap-4">
                <Home className="w-8 h-8 text-blue-400 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-lg mb-1">Home & Personal Use</h3>
                  <p className="text-gray-400 text-sm">
                    Write emails, draft documents, brainstorm ideas, get help with homework, 
                    plan trips, learn new topics—all without sending your personal thoughts to a corporation.
                  </p>
                </div>
              </div>
            </div>

            <div className="feature-card">
              <div className="flex items-start gap-4">
                <Briefcase className="w-8 h-8 text-blue-400 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-lg mb-1">Work & Professional</h3>
                  <p className="text-gray-400 text-sm">
                    Draft reports, summarize documents, generate ideas, proofread content. 
                    Perfect for professionals who handle sensitive information.
                  </p>
                </div>
              </div>
            </div>

            <div className="feature-card">
              <div className="flex items-start gap-4">
                <Plane className="w-8 h-8 text-blue-400 flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-lg mb-1">Travel & Remote Work</h3>
                  <p className="text-gray-400 text-sm">
                    On a plane, in a cabin, on a boat—TernaryAir works anywhere. 
                    Perfect for digital nomads and remote workers who need AI assistance offline.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Getting Started */}
        <section id="getting-started" className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Zap className="w-6 h-6 text-blue-400" />
            Getting Started
          </h2>

          <div className="feature-card">
            <p className="text-gray-300 text-lg mb-6">
              Using TernaryAir is as simple as using a USB drive. Here&apos;s how it works:
            </p>

            <ol className="space-y-4">
              <li className="flex items-start gap-4">
                <span className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 font-bold flex-shrink-0">1</span>
                <div>
                  <h4 className="font-semibold mb-1">Plug it in</h4>
                  <p className="text-gray-400 text-sm">Connect TernaryAir to any USB port on your computer. It draws minimal power (3-5W).</p>
                </div>
              </li>
              <li className="flex items-start gap-4">
                <span className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 font-bold flex-shrink-0">2</span>
                <div>
                  <h4 className="font-semibold mb-1">Open the app</h4>
                  <p className="text-gray-400 text-sm">Use our simple desktop app or any terminal. No complex setup required.</p>
                </div>
              </li>
              <li className="flex items-start gap-4">
                <span className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 font-bold flex-shrink-0">3</span>
                <div>
                  <h4 className="font-semibold mb-1">Start chatting</h4>
                  <p className="text-gray-400 text-sm">Type your question, get an answer. Just like any other AI assistant—but completely private.</p>
                </div>
              </li>
            </ol>
          </div>
        </section>

        {/* CTA */}
        <div className="bg-gradient-to-br from-blue-500/10 to-blue-900/10 border border-blue-500/30 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold mb-4">Ready to Get Started?</h3>
          <p className="text-gray-400 mb-6">
            Download TernaryAir and experience private, secure AI today.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/download" className="btn-primary">
              Download Now
            </Link>
            <Link href="/developers" className="btn-secondary">
              For Developers
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
