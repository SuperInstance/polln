import Link from "next/link";
import {
  ArrowRight,
  Clock,
  Gamepad2,
  Lightbulb,
  Target,
  CheckCircle,
  Play,
  Pause,
  RotateCcw,
} from "lucide-react";

export default function LearningPage() {
  return (
    <div className="animated-bg min-h-screen pt-24 pb-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-full px-5 py-2 mb-6">
            <Lightbulb className="w-4 h-4 text-green-400" />
            <span className="text-green-400 text-sm font-medium">Interactive Learning Hub</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="gradient-text">Learn AI Through Timing</span>
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto text-lg">
            Master fundamental AI and chip design concepts through interactive games, 
            visualizations, and hands-on exercises.
          </p>
        </div>

        {/* Learning Paths */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold mb-8">Learning Paths</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Path 1: Timing Fundamentals */}
            <div className="bg-dark-800/60 backdrop-blur-sm rounded-2xl p-8 border border-dark-600">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center">
                  <Clock className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold">Timing Fundamentals</h3>
                  <p className="text-gray-500 text-sm">8 lessons • 2 hours</p>
                </div>
              </div>
              <p className="text-gray-400 text-sm mb-6">
                Learn the basics of timing through traffic lights, musical chairs, 
                and domino chains. Perfect for beginners of all ages.
              </p>
              <div className="space-y-3 mb-6">
                {[
                  { title: "What is Timing?", status: "completed" },
                  { title: "Sequence & Order", status: "completed" },
                  { title: "Events and Triggers", status: "in-progress" },
                  { title: "Waiting & Patience", status: "locked" },
                  { title: "Coordination Games", status: "locked" },
                ].map((lesson, i) => (
                  <div key={i} className="flex items-center gap-3 text-sm">
                    {lesson.status === "completed" ? (
                      <CheckCircle className="w-5 h-5 text-green-400" />
                    ) : lesson.status === "in-progress" ? (
                      <Play className="w-5 h-5 text-amber-400" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border border-dark-500" />
                    )}
                    <span className={lesson.status === "locked" ? "text-gray-500" : "text-gray-300"}>
                      {lesson.title}
                    </span>
                  </div>
                ))}
              </div>
              <Link
                href="/timing-playground"
                className="flex items-center gap-2 text-blue-400 hover:text-blue-300 font-medium"
              >
                Continue Learning <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            {/* Path 2: Digital Logic */}
            <div className="bg-dark-800/60 backdrop-blur-sm rounded-2xl p-8 border border-dark-600">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                  <Target className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold">Digital Logic Timing</h3>
                  <p className="text-gray-500 text-sm">12 lessons • 4 hours</p>
                </div>
              </div>
              <p className="text-gray-400 text-sm mb-6">
                Bridge from games to real digital logic. Learn setup/hold times, 
                propagation delay, and state machines.
              </p>
              <div className="space-y-3 mb-6">
                {[
                  { title: "Logic Gates", status: "completed" },
                  { title: "Flip-Flops", status: "completed" },
                  { title: "Clock Signals", status: "completed" },
                  { title: "Setup & Hold Time", status: "in-progress" },
                  { title: "Timing Violations", status: "locked" },
                ].map((lesson, i) => (
                  <div key={i} className="flex items-center gap-3 text-sm">
                    {lesson.status === "completed" ? (
                      <CheckCircle className="w-5 h-5 text-green-400" />
                    ) : lesson.status === "in-progress" ? (
                      <Play className="w-5 h-5 text-amber-400" />
                    ) : (
                      <div className="w-5 h-5 rounded-full border border-dark-500" />
                    )}
                    <span className={lesson.status === "locked" ? "text-gray-500" : "text-gray-300"}>
                      {lesson.title}
                    </span>
                  </div>
                ))}
              </div>
              <Link
                href="/timing-playground"
                className="flex items-center gap-2 text-purple-400 hover:text-purple-300 font-medium"
              >
                Continue Learning <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>

        {/* Concept Cards */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold mb-8">Core Concepts</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                title: "Sequencing",
                emoji: "🎯",
                description: "Events happen in a specific order. Learn to identify, predict, and control sequences.",
                game: "Domino Chains",
                bridge: "Pipeline stages in processors"
              },
              {
                title: "Synchronization",
                emoji: "🔄",
                description: "Multiple events need to happen together. Master the art of coordination.",
                game: "Musical Chairs",
                bridge: "Clock domain crossing"
              },
              {
                title: "Timing Violations",
                emoji: "⚠️",
                description: "When events happen too early or too late, systems fail. Learn to prevent this.",
                game: "Jump Rope",
                bridge: "Setup/hold violations"
              },
            ].map((concept) => (
              <div key={concept.title} className="bg-dark-800/60 backdrop-blur-sm rounded-xl p-6 border border-dark-600">
                <div className="text-3xl mb-3">{concept.emoji}</div>
                <h3 className="text-lg font-semibold mb-2">{concept.title}</h3>
                <p className="text-gray-400 text-sm mb-4">{concept.description}</p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center gap-2">
                    <Gamepad2 className="w-4 h-4 text-blue-400" />
                    <span className="text-gray-500">Game: </span>
                    <span className="text-blue-400">{concept.game}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <ArrowRight className="w-4 h-4 text-green-400" />
                    <span className="text-gray-500">Bridge: </span>
                    <span className="text-green-400">{concept.bridge}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Interactive Demo */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold mb-8">Try It Now: Traffic Light Simulator</h2>
          <div className="bg-dark-800/60 backdrop-blur-sm rounded-2xl p-8 border border-dark-600">
            <div className="flex flex-col md:flex-row gap-8">
              {/* Traffic Light */}
              <div className="flex-shrink-0 flex flex-col items-center">
                <div className="bg-dark-700 rounded-2xl p-4 space-y-3">
                  <div className="w-16 h-16 rounded-full bg-red-500 flex items-center justify-center animate-pulse" />
                  <div className="w-16 h-16 rounded-full bg-dark-600" />
                  <div className="w-16 h-16 rounded-full bg-dark-600" />
                </div>
                <div className="mt-4 bg-dark-700 rounded-lg px-4 py-2">
                  <span className="text-gray-400 text-sm">RED - 30 seconds</span>
                </div>
              </div>

              {/* Explanation */}
              <div className="flex-1">
                <h3 className="text-lg font-semibold mb-4">State Machine Learning</h3>
                <p className="text-gray-400 text-sm mb-4">
                  A traffic light is a perfect example of a <strong className="text-white">finite state machine</strong>. 
                  It cycles through states (Red → Green → Yellow) with fixed timing.
                </p>
                <div className="code-block mb-4">
                  <div className="code-content font-mono text-xs">
                    <div className="text-purple-400">states:</div>
                    <div className="ml-4">RED (30s) → GREEN (25s) → YELLOW (5s)</div>
                    <div className="mt-2 text-purple-400">transitions:</div>
                    <div className="ml-4">timer_expired → next_state</div>
                    <div className="mt-2 text-purple-400">lesson:</div>
                    <div className="ml-4 text-green-400">// Same pattern in CPUs!</div>
                    <div className="ml-4 text-green-400">// FETCH → DECODE → EXECUTE</div>
                  </div>
                </div>
                <Link
                  href="/timing-playground"
                  className="inline-flex items-center gap-2 bg-green-500/10 text-green-400 px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-500/20 transition-colors"
                >
                  Open Full Simulator <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>
          </div>
        </div>

        {/* Age-Specific Content */}
        <div>
          <h2 className="text-2xl font-bold mb-8">Explore by Age Group</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { age: "4-10", name: "Young Learners", color: "blue", icon: "🎮" },
              { age: "11-14", name: "Middle School", color: "purple", icon: "🎯" },
              { age: "15-18", name: "High School", color: "amber", icon: "📐" },
              { age: "18+", name: "Professional", color: "green", icon: "💼" },
            ].map((group) => (
              <Link
                key={group.age}
                href={`/learning?age=${group.age}`}
                className={`bg-dark-800/60 backdrop-blur-sm rounded-xl p-5 border border-dark-600 hover:border-${group.color}-500/30 transition-colors group`}
              >
                <div className="text-2xl mb-2">{group.icon}</div>
                <h3 className="font-semibold mb-1">{group.name}</h3>
                <p className="text-gray-500 text-sm">Ages {group.age}</p>
                <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-white transition-colors mt-3" />
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
