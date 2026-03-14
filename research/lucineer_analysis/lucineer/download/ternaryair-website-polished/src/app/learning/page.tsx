import Link from "next/link";
import { BookOpen, Users, Code, Cpu, ArrowRight, GraduationCap, Lightbulb, Rocket, Fish } from "lucide-react";

const learningLevels = [
  {
    level: 1,
    title: "Beginner",
    audience: "Everyone",
    time: "30 min",
    icon: Users,
    color: "blue",
    topics: ["What is AI inference?", "Why privacy matters", "How TernaryAir protects you", "Use cases and benefits"],
  },
  {
    level: 2,
    title: "Intermediate",
    audience: "Tech Users",
    time: "45 min",
    icon: Lightbulb,
    color: "green",
    topics: ["How AI inference works", "Security vs convenience", "Comparison with alternatives", "Integration options"],
  },
  {
    level: 3,
    title: "Advanced",
    audience: "Developers",
    time: "60 min",
    icon: Code,
    color: "purple",
    topics: ["Python SDK deep dive", "API reference", "Code examples", "Integration patterns"],
  },
  {
    level: 4,
    title: "Expert",
    audience: "Hardware Eng.",
    time: "90 min",
    icon: Cpu,
    color: "amber",
    topics: ["RTL architecture", "RAU innovation", "FPGA prototyping", "Silicon design"],
  },
  {
    level: 5,
    title: "Researcher",
    audience: "Academics",
    time: "120 min",
    icon: GraduationCap,
    color: "violet",
    topics: ["Mathematical foundations", "Ternary quantization theory", "Related work", "Research directions"],
  },
];

export default function LearningPage() {
  return (
    <div className="animated-bg min-h-screen pt-20">
      {/* Hero */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-full px-5 py-2 mb-6">
              <BookOpen className="w-4 h-4 text-green-400" />
              <span className="text-green-400 text-sm font-medium">Learning Center</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
              <span className="gradient-text">Make AI Understandable</span>
            </h1>

            <p className="text-xl text-gray-300 mb-4 max-w-3xl mx-auto">
              Comprehensive education for all technical levels
            </p>

            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Whether you&apos;re a complete beginner or a hardware engineer, we have
              a learning path designed for you.
            </p>
          </div>

          {/* Quick Start */}
          <div className="max-w-4xl mx-auto mb-16">
            <div className="bg-dark-800/80 backdrop-blur-sm rounded-2xl p-8 border border-dark-600">
              <h3 className="font-semibold mb-6 flex items-center gap-3 text-lg">
                <Rocket className="w-5 h-5 text-green-400" />
                New to AI Hardware? Start Here
              </h3>
              <div className="grid md:grid-cols-3 gap-4">
                <Link href="/users" className="p-5 rounded-xl bg-dark-700/50 hover:bg-dark-600 transition-colors group">
                  <div className="text-sm text-blue-400 font-medium mb-1">Start with</div>
                  <div className="font-semibold text-white group-hover:text-blue-400 transition-colors">For Users</div>
                  <p className="text-xs text-gray-500 mt-2">Non-technical introduction</p>
                </Link>
                <div className="p-5 rounded-xl bg-dark-700/50 border border-dark-600">
                  <h4 className="font-medium mb-2 text-white">Quick Overview</h4>
                  <p className="text-xs text-gray-500">5-minute summary of TernaryAir</p>
                </div>
                <div className="p-5 rounded-xl bg-dark-700/50 border border-dark-600">
                  <h4 className="font-medium mb-2 text-white">Watch Demo</h4>
                  <p className="text-xs text-gray-500">See TernaryAir in action</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Learning Levels */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-dark-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Choose Your Path</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Each level builds on the previous. Start where you&apos;re comfortable.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-5">
            {learningLevels.map((item) => {
              const colorMap: Record<string, { text: string; border: string }> = {
                blue: { text: "text-blue-400", border: "border-blue-500/30 hover:border-blue-500/50" },
                green: { text: "text-green-400", border: "border-green-500/30 hover:border-green-500/50" },
                purple: { text: "text-purple-400", border: "border-purple-500/30 hover:border-purple-500/50" },
                amber: { text: "text-amber-400", border: "border-amber-500/30 hover:border-amber-500/50" },
                violet: { text: "text-violet-400", border: "border-violet-500/30 hover:border-violet-500/50" },
              };
              const colors = colorMap[item.color] || colorMap.green;

              return (
                <div
                  key={item.level}
                  className={`bg-dark-800/80 backdrop-blur-sm rounded-2xl p-6 border transition-all ${colors.border}`}
                >
                  <div className="text-xs text-gray-500 mb-2">Level {item.level}</div>
                  <div className="flex items-center gap-2 mb-3">
                    <item.icon className={`w-5 h-5 ${colors.text}`} />
                    <h3 className="font-semibold">{item.title}</h3>
                  </div>
                  <div className="text-xs text-gray-400 mb-4">
                    {item.audience} • {item.time}
                  </div>
                  <ul className="space-y-2 text-xs text-gray-400">
                    {item.topics.map((topic, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-gray-600 mt-0.5">•</span>
                        <span>{topic}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Visual Learning */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Visual Learning</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              We use diagrams that work across cultures and languages
            </p>
          </div>

          <div className="code-block max-w-4xl mx-auto">
            <div className="code-header">
              <div className="code-dot bg-red-500" />
              <div className="code-dot bg-yellow-500" />
              <div className="code-dot bg-green-500" />
              <span className="ml-2 text-gray-400 text-sm">Example: How It Works</span>
            </div>
            <div className="code-content">
              <pre className="ascii-diagram">{`    YOUR COMPUTER                 TERNARYAIR
   ┌─────────────┐              ┌─────────────┐
   │             │              │             │
   │  Your Data  │   ──USB──▶   │  AI Brain   │
   │  Your Files │              │  (Frozen)   │
   │  Your Life  │   ◀──USB──   │             │
   │             │              │             │
   └─────────────┘              └─────────────┘
         │                             │
         ▼                             ▼
   ✗ Never sent to cloud        ✗ No network
   ✗ Never stored               ✗ No memory
   ✗ Never logged               ✗ No hacking`}</pre>
            </div>
          </div>

          <div className="mt-10 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {[
              { emoji: "📐", title: "Spatial = Meaning", desc: "Position conveys relationships" },
              { emoji: "🔣", title: "Universal Symbols", desc: "No translation needed" },
              { emoji: "📊", title: "Progressive Detail", desc: "Simple → complex" },
            ].map((item) => (
              <div key={item.title} className="bg-dark-800/80 rounded-xl p-6 border border-dark-600 text-center">
                <div className="text-3xl mb-3">{item.emoji}</div>
                <h4 className="font-medium mb-2">{item.title}</h4>
                <p className="text-xs text-gray-400">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Origin Story */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-dark-800/30">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 text-green-400 mb-6">
            <Fish className="w-6 h-6" />
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold mb-8">The Origin Story</h2>
          <blockquote className="text-lg text-gray-300 italic mb-6 space-y-4 leading-relaxed">
            <p>I&apos;m a fisherman and a developer.</p>
            <p>
              I needed AI that works on a boat, in the middle of nowhere, with no
              internet and limited power. Cloud AI doesn&apos;t work there. GPUs were
              too expensive.
            </p>
            <p>
              So I designed my own architecture — efficient enough for USB power,
              cheap enough for anyone, and secure enough that it can&apos;t be compromised.
            </p>
            <p className="text-green-400 font-semibold not-italic">
              AI should work for you, not the other way around.
            </p>
          </blockquote>
          <p className="text-gray-400">
            — <span className="font-semibold text-white">Casey DiGennaro</span>, SuperInstance.AI
          </p>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-6">Ready to Learn?</h2>
          <p className="text-gray-400 text-lg mb-10 max-w-2xl mx-auto">
            Choose your path and start your journey with TernaryAir.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/users"
              className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-500 hover:to-blue-600 text-white px-8 py-4 rounded-xl font-medium transition-all glow-blue shadow-lg"
            >
              <Users className="w-5 h-5" />
              Start as User
            </Link>
            <Link
              href="/developers"
              className="inline-flex items-center gap-2 bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-500 hover:to-violet-500 text-white px-8 py-4 rounded-xl font-medium transition-all glow-purple shadow-lg"
            >
              <Code className="w-5 h-5" />
              Start as Developer
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
