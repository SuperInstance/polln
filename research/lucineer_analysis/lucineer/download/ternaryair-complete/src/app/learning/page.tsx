import Link from "next/link";
import {
  BookOpen,
  GraduationCap,
  Code,
  Cpu,
  ArrowRight,
  CheckCircle,
  Zap,
} from "lucide-react";

export default function LearningPage() {
  return (
    <div className="min-h-screen pt-24 pb-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="w-16 h-16 rounded-2xl bg-green-500/10 flex items-center justify-center mx-auto mb-6">
            <BookOpen className="w-8 h-8 text-green-400" />
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="gradient-text">Learning Center</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Comprehensive educational resources for all skill levels. From AI basics to advanced hardware design.
          </p>
        </div>

        {/* Learning Levels */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <GraduationCap className="w-6 h-6 text-green-400" />
            Learning Paths
          </h2>

          <div className="space-y-6">
            {/* Beginner */}
            <div className="feature-card">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center flex-shrink-0">
                  <span className="text-xl font-bold text-blue-400">1</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-xl mb-2 text-blue-400">Beginner: What is AI Hardware?</h3>
                  <p className="text-gray-400 mb-4">
                    Start here if you&apos;re new to AI or hardware. Learn the basics of how AI models work, 
                    why hardware matters, and what makes TernaryAir different.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                    <div className="flex items-center gap-2 text-gray-400">
                      <CheckCircle className="w-4 h-4 text-blue-400" />
                      What is a neural network?
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <CheckCircle className="w-4 h-4 text-blue-400" />
                      How does AI inference work?
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <CheckCircle className="w-4 h-4 text-blue-400" />
                      Why do we need specialized chips?
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <CheckCircle className="w-4 h-4 text-blue-400" />
                      What is ternary computing?
                    </div>
                  </div>
                  <Link href="/users" className="inline-flex items-center gap-2 text-blue-400 text-sm mt-4 hover:underline">
                    Start Learning <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            </div>

            {/* Intermediate */}
            <div className="feature-card">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center flex-shrink-0">
                  <span className="text-xl font-bold text-purple-400">2</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-xl mb-2 text-purple-400">Intermediate: Building with TernaryAir</h3>
                  <p className="text-gray-400 mb-4">
                    Learn to use the Python SDK, integrate with your applications, and build AI-powered 
                    projects with complete privacy.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                    <div className="flex items-center gap-2 text-gray-400">
                      <CheckCircle className="w-4 h-4 text-purple-400" />
                      Python SDK fundamentals
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <CheckCircle className="w-4 h-4 text-purple-400" />
                      REST API integration
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <CheckCircle className="w-4 h-4 text-purple-400" />
                      OpenAI compatibility layer
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <CheckCircle className="w-4 h-4 text-purple-400" />
                      Building chat applications
                    </div>
                  </div>
                  <Link href="/developers" className="inline-flex items-center gap-2 text-purple-400 text-sm mt-4 hover:underline">
                    Start Building <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            </div>

            {/* Advanced */}
            <div className="feature-card">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center flex-shrink-0">
                  <span className="text-xl font-bold text-amber-400">3</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-xl mb-2 text-amber-400">Advanced: FPGA Prototyping</h3>
                  <p className="text-gray-400 mb-4">
                    Dive into the RTL source, simulate the design, and prototype on real FPGA hardware. 
                    Understand how the RAU works at the register level.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                    <div className="flex items-center gap-2 text-gray-400">
                      <CheckCircle className="w-4 h-4 text-amber-400" />
                      SystemVerilog basics
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <CheckCircle className="w-4 h-4 text-amber-400" />
                      RTL simulation with Verilator
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <CheckCircle className="w-4 h-4 text-amber-400" />
                      FPGA synthesis flow
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <CheckCircle className="w-4 h-4 text-amber-400" />
                      Performance optimization
                    </div>
                  </div>
                  <Link href="/engineers" className="inline-flex items-center gap-2 text-amber-400 text-sm mt-4 hover:underline">
                    Start Prototyping <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            </div>

            {/* Expert */}
            <div className="feature-card">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 rounded-xl bg-red-500/10 flex items-center justify-center flex-shrink-0">
                  <span className="text-xl font-bold text-red-400">4</span>
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-xl mb-2 text-red-400">Expert: Silicon Design</h3>
                  <p className="text-gray-400 mb-4">
                    Master the complete ASIC flow: from RTL to GDSII. Learn about mask-locked weight encoding, 
                    physical design, and tapeout preparation.
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                    <div className="flex items-center gap-2 text-gray-400">
                      <CheckCircle className="w-4 h-4 text-red-400" />
                      ASIC design flow
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <CheckCircle className="w-4 h-4 text-red-400" />
                      Physical synthesis
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <CheckCircle className="w-4 h-4 text-red-400" />
                      Via-based weight encoding
                    </div>
                    <div className="flex items-center gap-2 text-gray-400">
                      <CheckCircle className="w-4 h-4 text-red-400" />
                      Design for manufacturing
                    </div>
                  </div>
                  <Link href="/architecture" className="inline-flex items-center gap-2 text-red-400 text-sm mt-4 hover:underline">
                    Dive Deep <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Key Concepts */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Zap className="w-6 h-6 text-green-400" />
            Key Concepts
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="download-card text-center">
              <Code className="w-8 h-8 text-green-400 mx-auto mb-3" />
              <h4 className="font-semibold mb-2">Ternary Weights</h4>
              <p className="text-sm text-gray-400">
                Neural network weights restricted to {-1, 0, +1}. 90% reduction in compute complexity.
              </p>
            </div>

            <div className="download-card text-center">
              <Cpu className="w-8 h-8 text-green-400 mx-auto mb-3" />
              <h4 className="font-semibold mb-2">Mask-Locking</h4>
              <p className="text-sm text-gray-400">
                Encoding weights in silicon metal layers. Zero memory access, infinite bandwidth.
              </p>
            </div>

            <div className="download-card text-center">
              <Zap className="w-8 h-8 text-green-400 mx-auto mb-3" />
              <h4 className="font-semibold mb-2">RAU</h4>
              <p className="text-sm text-gray-400">
                Rotation-Accumulate Unit. Replaces multiplication with sign manipulation.
              </p>
            </div>
          </div>
        </section>

        {/* Resources */}
        <section className="mb-16">
          <h2 className="text-2xl font-bold mb-6">Additional Resources</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="feature-card">
              <h4 className="font-semibold mb-2">Research Papers</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>• BitNet: 1-bit LLMs (Microsoft Research)</li>
                <li>• iFairy: Complex-valued Ternary LLMs (Peking University)</li>
                <li>• TeLLMe: FPGA Ternary Inference (arXiv:2510.15926)</li>
              </ul>
            </div>

            <div className="feature-card">
              <h4 className="font-semibold mb-2">Video Tutorials</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>• Getting Started with TernaryAir (YouTube)</li>
                <li>• FPGA Prototyping Walkthrough (YouTube)</li>
                <li>• Architecture Deep Dive (YouTube)</li>
              </ul>
            </div>
          </div>
        </section>

        {/* CTA */}
        <div className="bg-gradient-to-br from-green-500/10 to-green-900/10 border border-green-500/30 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold mb-4">Start Your Journey</h3>
          <p className="text-gray-400 mb-6">
            Download TernaryAir and explore the complete learning resources.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/download" className="btn-primary">
              Download Package
            </Link>
            <Link href="/users" className="btn-secondary">
              Begin with Basics
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
