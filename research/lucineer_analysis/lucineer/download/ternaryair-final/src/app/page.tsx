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
  Terminal,
  Gamepad2,
  Clock,
  GraduationCap,
  Briefcase,
  Rocket,
  Sparkles,
} from "lucide-react";

export default function Home() {
  return (
    <div className="animated-bg min-h-screen">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 sm:px-6 lg:px-8 overflow-hidden">
        {/* Background effects */}
        <div className="absolute inset-0 grid-pattern opacity-30" />
        <div className="absolute top-1/4 left-10 w-96 h-96 bg-green-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 right-10 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl" />
        
        <div className="max-w-7xl mx-auto relative">
          <div className="text-center mb-12">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-full px-5 py-2 mb-8 pulse-glow">
              <Sparkles className="w-4 h-4 text-green-400" />
              <span className="text-green-400 text-sm font-medium">
                Learn AI Through Play • All Ages Welcome
              </span>
            </div>

            {/* Title */}
            <h1 className="text-5xl sm:text-6xl lg:text-8xl font-bold mb-6 text-shadow">
              <span className="gradient-text">TernaryAir</span>
            </h1>

            {/* Tagline */}
            <p className="text-2xl sm:text-3xl text-gray-200 mb-4 font-medium">
              Where Learning Meets Fun
            </p>

            <p className="text-lg text-gray-400 mb-10 max-w-2xl mx-auto leading-relaxed">
              Master AI concepts through timing games, sequencing puzzles, and interactive simulations. 
              From playground games to professional chip design — one platform, infinite depth.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-wrap justify-center gap-4 mb-12">
              <Link
                href="/learning"
                className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-7 py-3.5 rounded-xl font-medium transition-all glow-green shadow-lg"
              >
                <Gamepad2 className="w-5 h-5" />
                Start Your Journey
              </Link>

              <Link
                href="/timing-playground"
                className="flex items-center gap-2 bg-dark-700/80 hover:bg-dark-600 text-white px-7 py-3.5 rounded-xl font-medium transition-all border border-dark-500 hover:border-dark-400"
              >
                <Clock className="w-5 h-5 text-green-400" />
                Try the Playground
              </Link>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-3xl mx-auto">
              {[
                { value: "4", label: "Age Groups", icon: Users },
                { value: "∞", label: "Learning Paths", icon: Rocket },
                { value: "100+", label: "Interactive Lessons", icon: Zap },
                { value: "Free", label: "MIT Licensed", icon: Shield },
              ].map((stat) => (
                <div
                  key={stat.label}
                  className="bg-dark-800/60 backdrop-blur-sm rounded-xl p-5 border border-dark-600 hover:border-green-500/30 transition-colors"
                >
                  <stat.icon className="w-5 h-5 text-green-400 mb-2" />
                  <div className="text-2xl font-bold text-green-400">{stat.value}</div>
                  <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Age Groups Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Choose Your Learning Path</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Whether you&apos;re just starting out or diving deep into chip design, 
              we have content tailored for your journey.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Young Learners */}
            <Link
              href="/learning?age=young"
              className="group age-card bg-dark-800/80 backdrop-blur-sm rounded-2xl p-6 border border-dark-600 card-hover hover:border-blue-500/30"
            >
              <div className="w-14 h-14 rounded-xl bg-blue-500/10 flex items-center justify-center mb-5 group-hover:bg-blue-500/20 transition-colors">
                <Gamepad2 className="w-7 h-7 text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-blue-400">
                Young Learners
              </h3>
              <p className="text-gray-500 text-sm mb-3">Ages 4-10</p>
              <p className="text-gray-400 text-sm mb-5 leading-relaxed">
                Fun games teaching timing through traffic lights, musical chairs, 
                and domino chains. Learn without knowing you&apos;re learning!
              </p>
              <ul className="space-y-2 text-sm text-gray-500">
                {["Traffic Light Games", "Musical Chairs Timing", "Domino Chains"].map((item) => (
                  <li key={item} className="flex items-center gap-2">
                    <ArrowRight className="w-4 h-4 text-blue-400" />
                    {item}
                  </li>
                ))}
              </ul>
            </Link>

            {/* Middle School */}
            <Link
              href="/learning?age=middle"
              className="group age-card bg-dark-800/80 backdrop-blur-sm rounded-2xl p-6 border border-dark-600 card-hover hover:border-purple-500/30"
            >
              <div className="w-14 h-14 rounded-xl bg-purple-500/10 flex items-center justify-center mb-5 group-hover:bg-purple-500/20 transition-colors">
                <Clock className="w-7 h-7 text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-purple-400">
                Middle School
              </h3>
              <p className="text-gray-500 text-sm mb-3">Ages 11-14</p>
              <p className="text-gray-400 text-sm mb-5 leading-relaxed">
                Animation timing, music beat programming, and traffic flow 
                coordination. Bridge the gap between games and technology.
              </p>
              <ul className="space-y-2 text-sm text-gray-500">
                {["Animation Frames", "Beat Programming", "Traffic Systems"].map((item) => (
                  <li key={item} className="flex items-center gap-2">
                    <ArrowRight className="w-4 h-4 text-purple-400" />
                    {item}
                  </li>
                ))}
              </ul>
            </Link>

            {/* High School */}
            <Link
              href="/learning?age=high"
              className="group age-card bg-dark-800/80 backdrop-blur-sm rounded-2xl p-6 border border-dark-600 card-hover hover:border-amber-500/30"
            >
              <div className="w-14 h-14 rounded-xl bg-amber-500/10 flex items-center justify-center mb-5 group-hover:bg-amber-500/20 transition-colors">
                <GraduationCap className="w-7 h-7 text-amber-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-amber-400">
                High School
              </h3>
              <p className="text-gray-500 text-sm mb-3">Ages 15-18</p>
              <p className="text-gray-400 text-sm mb-5 leading-relaxed">
                Sports replay analysis, assembly line optimization, and 
                introduction to digital logic timing concepts.
              </p>
              <ul className="space-y-2 text-sm text-gray-500">
                {["Digital Logic Intro", "Timing Analysis", "System Design"].map((item) => (
                  <li key={item} className="flex items-center gap-2">
                    <ArrowRight className="w-4 h-4 text-amber-400" />
                    {item}
                  </li>
                ))}
              </ul>
            </Link>

            {/* Professional */}
            <Link
              href="/professional"
              className="group age-card bg-dark-800/80 backdrop-blur-sm rounded-2xl p-6 border border-dark-600 card-hover hover:border-green-500/30"
            >
              <div className="w-14 h-14 rounded-xl bg-green-500/10 flex items-center justify-center mb-5 group-hover:bg-green-500/20 transition-colors">
                <Briefcase className="w-7 h-7 text-green-400" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-green-400">
                Professional
              </h3>
              <p className="text-gray-500 text-sm mb-3">18+ & Engineers</p>
              <p className="text-gray-400 text-sm mb-5 leading-relaxed">
                FPGA timing closure, clock domain crossing, pipeline 
                optimization, and real chip design tools.
              </p>
              <ul className="space-y-2 text-sm text-gray-500">
                {["FPGA Timing", "CDC Analysis", "Pipeline Design"].map((item) => (
                  <li key={item} className="flex items-center gap-2">
                    <ArrowRight className="w-4 h-4 text-green-400" />
                    {item}
                  </li>
                ))}
              </ul>
            </Link>
          </div>
        </div>
      </section>

      {/* Synergy Concept */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-dark-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">One Concept, Infinite Depth</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              The same timing principles appear at every level, creating synergistic 
              learning that deepens understanding through multiple perspectives.
            </p>
          </div>

          <div className="code-block max-w-4xl mx-auto">
            <div className="code-header">
              <div className="code-dot bg-red-500" />
              <div className="code-dot bg-yellow-500" />
              <div className="code-dot bg-green-500" />
              <span className="ml-2 text-gray-400 text-sm">
                Timing Concept Synergy Map
              </span>
            </div>
            <div className="code-content">
              <pre className="text-sm text-gray-300">{`PROFESSIONAL: Clock Domain Crossing (CDC)
    │
    │  Same concept, different complexity
    │
INTERMEDIATE: Animation Frame Sequencing
    │
    │  Same timing principles, new context
    │
YOUNG LEARNER: Traffic Light Sequence

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every level teaches the same fundamentals:
• Events happen in sequence
• Timing determines success  
• Coordination creates harmony
• Violations cause failures

Learn once, apply everywhere!`}</pre>
            </div>
          </div>
        </div>
      </section>

      {/* Key Innovations */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">What Makes Us Different</h2>
          </div>

          <div className="feature-grid">
            {[
              {
                icon: Gamepad2,
                title: "Game-Like Learning",
                description: "Master complex concepts through engaging games and simulations. Learning happens naturally as you play."
              },
              {
                icon: Users,
                title: "Cross-Generational",
                description: "Parents and children can learn together, each at their own level. The same concepts scale from playground to profession."
              },
              {
                icon: Cpu,
                title: "Real-World Connection",
                description: "Every game connects to real professional applications. Traffic lights teach state machines. Dominoes teach propagation delay."
              },
              {
                icon: Globe,
                title: "Cultural Synergy",
                description: "Time concepts explained through diverse cultural lenses - cyclical time, rhythmic time, event-based time."
              },
              {
                icon: Zap,
                title: "Interactive Simulations",
                description: "Hands-on tools let you experiment with timing, see violations in real-time, and learn by doing."
              },
              {
                icon: Shield,
                title: "Open Source",
                description: "MIT licensed, fully open source. Use our tools, contribute to development, build your own applications."
              },
            ].map((feature) => (
              <div key={feature.title} className="feature-item">
                <feature.icon className="w-8 h-8 text-green-400 mb-4" />
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-green-900/20 via-dark-900 to-dark-900">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-6">
            Ready to Start Your Journey?
          </h2>
          <p className="text-gray-400 text-lg mb-10 max-w-2xl mx-auto leading-relaxed">
            Join thousands of learners discovering AI concepts through play. 
            Free forever, open source, and built for everyone.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/learning"
              className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-8 py-4 rounded-xl font-medium transition-all glow-green shadow-lg"
            >
              <Rocket className="w-5 h-5" />
              Begin Learning
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

function Globe({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10" />
      <line x1="2" y1="12" x2="22" y2="12" />
      <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
    </svg>
  );
}
