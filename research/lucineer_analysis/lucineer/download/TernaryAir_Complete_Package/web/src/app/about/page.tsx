import Link from "next/link";
import {
  Users,
  Target,
  Lightbulb,
  Rocket,
  Github,
  Mail,
  BookOpen,
  Cpu,
  Heart,
  ArrowRight,
} from "lucide-react";

export default function AboutPage() {
  return (
    <div className="animated-bg min-h-screen pt-24 pb-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-full px-5 py-2 mb-6">
            <Heart className="w-4 h-4 text-green-400" />
            <span className="text-green-400 text-sm font-medium">Our Mission</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="gradient-text">About TernaryAir</span>
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto text-lg">
            Making AI and chip design education accessible to everyone through 
            game-like learning and visual understanding.
          </p>
        </div>

        {/* Story Section */}
        <div className="mb-20">
          <div className="max-w-4xl mx-auto">
            <div className="bg-dark-800/60 backdrop-blur-sm rounded-2xl p-8 md:p-12 border border-dark-600">
              <h2 className="text-2xl font-bold mb-6">Our Story</h2>
              <div className="prose prose-invert max-w-none">
                <p className="text-gray-300 leading-relaxed mb-4">
                  TernaryAir was born from a simple observation: the fundamental concepts 
                  of timing and synchronization in chip design are the same concepts 
                  children learn through playground games.
                </p>
                <p className="text-gray-300 leading-relaxed mb-4">
                  When a child plays musical chairs, they&apos;re learning about event-driven 
                  timing and resource contention. When dominoes fall in sequence, they&apos;re 
                  witnessing propagation delay. When traffic lights cycle through states, 
                  they&apos;re observing a finite state machine in action.
                </p>
                <p className="text-gray-300 leading-relaxed">
                  We asked: <span className="text-green-400 font-medium">What if we could bridge 
                  these experiences intentionally?</span> What if learning advanced chip design 
                  felt as natural as playing games?
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Mission Cards */}
        <div className="mb-20">
          <h2 className="text-2xl font-bold mb-8 text-center">Our Mission</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: Lightbulb,
                title: "Democratize Knowledge",
                description: "Make complex chip design concepts accessible to everyone, regardless of background or prior experience.",
              },
              {
                icon: Target,
                title: "Bridge All Ages",
                description: "Create learning pathways that scale from childhood curiosity to professional expertise, all using the same fundamental concepts.",
              },
              {
                icon: Rocket,
                title: "Inspire Innovation",
                description: "Show that advanced technology can be fun, approachable, and creative—not just for experts in labs.",
              },
            ].map((mission) => (
              <div key={mission.title} className="bg-dark-800/60 backdrop-blur-sm rounded-xl p-6 border border-dark-600">
                <mission.icon className="w-8 h-8 text-green-400 mb-4" />
                <h3 className="text-lg font-semibold mb-2">{mission.title}</h3>
                <p className="text-gray-400 text-sm">{mission.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Synergy Concept */}
        <div className="mb-20">
          <h2 className="text-2xl font-bold mb-8 text-center">The Synergy Principle</h2>
          <div className="bg-dark-800/60 backdrop-blur-sm rounded-2xl p-8 border border-dark-600">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
              <div>
                <h3 className="text-xl font-semibold mb-4">One Concept, Infinite Depth</h3>
                <p className="text-gray-400 mb-4">
                  Our core innovation is showing how the same timing concepts appear 
                  at every level of complexity, from games to professional engineering.
                </p>
                <ul className="space-y-3">
                  {[
                    { game: "Musical Chairs", concept: "Event-driven timing", pro: "Interrupt handling" },
                    { game: "Traffic Lights", concept: "State machines", pro: "CPU control logic" },
                    { game: "Domino Chains", concept: "Propagation delay", pro: "Signal timing" },
                    { game: "Jump Rope", concept: "Synchronization", pro: "Clock domain crossing" },
                  ].map((item) => (
                    <li key={item.game} className="flex items-center gap-3 text-sm">
                      <span className="w-32 text-blue-400">{item.game}</span>
                      <ArrowRight className="w-4 h-4 text-gray-500" />
                      <span className="text-purple-400">{item.concept}</span>
                      <ArrowRight className="w-4 h-4 text-gray-500" />
                      <span className="text-green-400">{item.pro}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="code-block">
                <div className="code-content font-mono text-xs">
                  <pre className="text-gray-300">{`LEARNING SYNERGY:

┌─────────────────────────────────────┐
│     PROFESSIONAL UNDERSTANDING      │
│   (FPGA, ASIC, CDC, Pipelines)     │
└─────────────────────────────────────┘
                  ▲
                  │ Bridge through
                  │ same concepts
                  ▼
┌─────────────────────────────────────┐
│       FOUNDATIONAL GAMES            │
│   (Traffic lights, dominoes)       │
└─────────────────────────────────────┘

Result: Deeper understanding through
        multiple perspectives!`}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Team Section */}
        <div className="mb-20">
          <h2 className="text-2xl font-bold mb-8 text-center">The Team</h2>
          <div className="max-w-2xl mx-auto">
            <div className="bg-dark-800/60 backdrop-blur-sm rounded-xl p-6 border border-dark-600 text-center">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center mx-auto mb-4">
                <Cpu className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-xl font-semibold mb-2">SuperInstance.AI</h3>
              <p className="text-gray-400 text-sm mb-4">
                Building open-source AI infrastructure for everyone. TernaryAir is 
                our educational initiative to make chip design accessible.
              </p>
              <div className="flex justify-center gap-4">
                <a
                  href="https://github.com/superinstance"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
                >
                  <Github className="w-5 h-5" />
                  GitHub
                </a>
                <a
                  href="mailto:hello@ternaryair.ai"
                  className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
                >
                  <Mail className="w-5 h-5" />
                  Contact
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Resources */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold mb-8 text-center">Resources</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                icon: BookOpen,
                title: "Documentation",
                description: "Comprehensive guides and tutorials for all levels",
                link: "/learning",
              },
              {
                icon: Github,
                title: "Open Source",
                description: "MIT licensed code available on GitHub",
                link: "https://github.com/superinstance/ternaryair",
              },
              {
                icon: Users,
                title: "Community",
                description: "Join our growing community of learners",
                link: "#",
              },
            ].map((resource) => (
              <Link
                key={resource.title}
                href={resource.link}
                className="bg-dark-800/60 backdrop-blur-sm rounded-xl p-6 border border-dark-600 hover:border-green-500/30 transition-colors group"
              >
                <resource.icon className="w-8 h-8 text-green-400 mb-4" />
                <h3 className="text-lg font-semibold mb-2">{resource.title}</h3>
                <p className="text-gray-400 text-sm mb-4">{resource.description}</p>
                <span className="flex items-center gap-2 text-green-400 text-sm">
                  Learn more <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </span>
              </Link>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="text-center">
          <div className="bg-gradient-to-br from-green-900/20 via-dark-900 to-dark-900 rounded-2xl p-8 md:p-12 border border-dark-600">
            <h2 className="text-2xl font-bold mb-4">Ready to Start Learning?</h2>
            <p className="text-gray-400 mb-8 max-w-xl mx-auto">
              Join us in making AI and chip design education accessible to everyone. 
              Free, open source, and built with love.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Link
                href="/learning"
                className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-8 py-3 rounded-xl font-medium transition-all"
              >
                <Rocket className="w-5 h-5" />
                Start Your Journey
              </Link>
              <a
                href="https://github.com/superinstance/ternaryair"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-8 py-3 rounded-xl font-medium transition-colors"
              >
                <Github className="w-5 h-5" />
                View on GitHub
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
