import Link from "next/link";
import { BookOpen, Users, Code, Cpu, ArrowRight, GraduationCap, Lightbulb, Rocket } from "lucide-react";

const learningLevels = [
  {
    level: 1,
    title: "Beginner",
    audience: "Everyone",
    time: "30 min",
    icon: Users,
    color: "user",
    topics: ["What is AI inference?", "Why privacy matters", "How TernaryAir protects you", "Use cases and benefits"],
  },
  {
    level: 2,
    title: "Intermediate",
    audience: "Tech Users",
    time: "45 min",
    icon: Lightbulb,
    color: "primary",
    topics: ["How AI inference works", "Security vs convenience", "Comparison with alternatives", "Integration options"],
  },
  {
    level: 3,
    title: "Advanced",
    audience: "Developers",
    time: "60 min",
    icon: Code,
    color: "developer",
    topics: ["Python SDK deep dive", "API reference", "Code examples", "Integration patterns"],
  },
  {
    level: 4,
    title: "Expert",
    audience: "Hardware Eng.",
    time: "90 min",
    icon: Cpu,
    color: "engineer",
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
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 bg-primary-500/10 border border-primary-500/30 rounded-full px-4 py-2 mb-6">
              <BookOpen className="w-4 h-4 text-primary-400" />
              <span className="text-primary-400 text-sm font-medium">Learning Center</span>
            </div>

            <h1 className="text-4xl sm:text-5xl font-bold mb-6">
              <span className="gradient-text">Make AI Understandable</span>
            </h1>

            <p className="text-xl text-gray-300 mb-4 max-w-3xl mx-auto">
              Comprehensive education for all technical levels
            </p>

            <p className="text-gray-400 max-w-2xl mx-auto">
              Whether you&apos;re a complete beginner or a hardware engineer, we have
              a learning path designed for you.
            </p>
          </div>

          {/* Quick Start */}
          <div className="max-w-4xl mx-auto mb-16">
            <div className="bg-dark-800 rounded-xl p-6 border border-dark-600">
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <Rocket className="w-5 h-5 text-primary-400" />
                New to AI Hardware? Start Here
              </h3>
              <div className="grid md:grid-cols-3 gap-4">
                <Link href="/users" className="p-4 rounded-lg bg-dark-700 hover:bg-dark-600 transition-colors">
                  <div className="text-sm text-user font-medium mb-1">Start with</div>
                  <div className="font-semibold">For Users</div>
                  <h3 className="font-medium mb-2">For Users</Link>
                  <p className="text-xs text-gray-400">Non-technical introduction</p>
                </Link>
                <div className="p-4 rounded-lg bg-dark-700">
                  <h4 className="font-medium mb-2">Quick Overview</h4>
                  <p className="text-xs text-gray-400">5-minute summary</p>
                </div>
                <div className="p-4 rounded-lg bg-dark-700">
                  <h4 className="font-medium mb-2">Watch Demo</h4>
                  <p className="text-xs text-gray-400">See it in action</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Learning Levels */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Choose Your Path</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Each level builds on the previous. Start where you&apos;re comfortable.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {learningLevels.map((item) => {
              const colorClasses: Record<string, string> = {
                user: "text-user border-user/30 hover:border-user/50",
                primary: "text-primary-400 border-primary-400/30 hover:border-primary-400/50",
                developer: "text-developer border-developer/30 hover:border-developer/50",
                engineer: "text-engineer border-engineer/30 hover:border-engineer/50",
                violet: "text-violet-400 border-violet-400/30 hover:border-violet-400/50",
              };

              return (
                <div
                  key={item.level}
                  className={`bg-dark-700 rounded-xl p-5 border transition-all ${
                    colorClasses[item.color]
                  }`}
                >
                  <div className="text-xs opacity-60 mb-2">Level {item.level}</div>
                  <div className="flex items-center gap-2 mb-3">
                    <item.icon className="w-5 h-5" />
                    <h3 className="font-semibold">{item.title}</h3>
                  </div>
                  <div className="text-xs text-gray-400 mb-3">
                    {item.audience} • {item.time}
                  </div>
                  <ul className="space-y-1 text-xs text-gray-400">
                    {item.topics.map((topic, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-gray-600">•</span>
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
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Visual Learning</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
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

          <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="bg-dark-800 rounded-lg p-4 border border-dark-600 text-center">
              <div className="text-2xl mb-2">📐</div>
              <h4 className="font-medium mb-1">Spatial = Meaning</h4>
              <p className="text-xs text-gray-400">Position conveys relationships</p>
            </div>
            <div className="bg-dark-800 rounded-lg p-4 border border-dark-600 text-center">
              <div className="text-2xl mb-2">🔣</div>
              <h4 className="font-medium mb-1">Universal Symbols</h4>
              <p className="text-xs text-gray-400">No translation needed</p>
            </div>
            <div className="bg-dark-800 rounded-lg p-4 border border-dark-600 text-center">
              <div className="text-2xl mb-2">📊</div>
              <h4 className="font-medium mb-1">Progressive Detail</h4>
              <p className="text-xs text-gray-400">Simple → complex</p>
            </div>
          </div>
        </div>
      </section>

      {/* Origin Story */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6">The Origin Story</h2>
          <blockquote className="text-lg text-gray-300 italic mb-6 space-y-4">
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
            <p className="text-primary-400 font-semibold not-italic">
              AI should work for you, not the other way around.
            </p>
          </blockquote>
          <p className="text-gray-400">
            — <span className="font-semibold">Casey DiGennaro</span>, SuperInstance.AI
          </p>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Learn?</h2>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
            Choose your path and start your journey.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/users"
              className="inline-flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-8 py-4 rounded-lg font-medium transition-all glow-green"
            >
              <Users className="w-5 h-5" />
              Start as User
            </Link>
            <Link
              href="/developers"
              className="inline-flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-8 py-4 rounded-lg font-medium transition-all border border-dark-500"
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
