import Link from "next/link";
import { Download, ArrowRight, Fish, Anchor, Cpu, Shield, Heart, Github } from "lucide-react";

export default function OriginStoryPage() {
  return (
    <div className="animated-bg min-h-screen pt-20">
      {/* Hero */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-full px-5 py-2 mb-6">
              <Fish className="w-4 h-4 text-green-400" />
              <span className="text-green-400 text-sm font-medium">Origin Story</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
              <span className="gradient-text">How TernaryAir Was Born</span>
            </h1>
            
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              A fisherman, a developer, and a need for AI that works anywhere
            </p>
          </div>
        </div>
      </section>

      {/* The Story */}
      <section className="py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto">
          <div className="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 md:p-12 border border-dark-600 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-green-500/5 rounded-full blur-3xl" />
            <div className="relative">
              <div className="flex items-center gap-3 mb-8">
                <Anchor className="w-8 h-8 text-green-400" />
                <span className="text-green-400 font-medium">The Problem</span>
              </div>
              
              <blockquote className="text-xl text-gray-300 leading-relaxed space-y-6">
                <p>
                  I&apos;m a fisherman and a developer.
                </p>
                
                <p>
                  I needed AI that works on a boat, in the middle of nowhere, with no 
                  internet and limited power. Cloud AI doesn&apos;t work there. GPUs were 
                  too expensive.
                </p>
                
                <p>
                  So I designed my own architecture — efficient enough for USB power, 
                  cheap enough for anyone to afford, and secure enough that it 
                  can&apos;t be compromised.
                </p>
              </blockquote>
            </div>
          </div>

          <div className="bg-green-500/5 backdrop-blur-sm rounded-2xl p-8 md:p-12 border border-green-500/20 mt-8">
            <div className="flex items-center gap-3 mb-8">
              <Cpu className="w-8 h-8 text-green-400" />
              <span className="text-green-400 font-medium">The Innovation</span>
            </div>
            
            <blockquote className="text-xl text-gray-300 leading-relaxed space-y-6">
              <p>
                The mask-locked design started as a cost optimization (no external 
                memory for weights). But I realized it&apos;s also the most secure AI 
                architecture possible — the model is literally frozen in silicon. 
                It can&apos;t be modified, can&apos;t be extracted, can&apos;t phone home.
              </p>
              
              <p>
                That&apos;s the hardware boundary between you and AI agents.
              </p>
            </blockquote>
          </div>

          <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/5 backdrop-blur-sm rounded-2xl p-8 md:p-12 border border-green-500/30 mt-8">
            <div className="flex items-center gap-3 mb-8">
              <Heart className="w-8 h-8 text-green-400" />
              <span className="text-green-400 font-medium">The Mission</span>
            </div>
            
            <blockquote className="text-xl text-gray-300 leading-relaxed space-y-6">
              <p className="text-green-400 font-semibold not-italic">
                I&apos;m releasing everything under MIT license. Build your own. 
                Improve it. Use it for whatever you want.
              </p>
              
              <p className="text-green-400 font-semibold not-italic">
                AI should work for you, not the other way around.
              </p>
            </blockquote>
          </div>
          
          <div className="mt-12 text-center">
            <p className="text-gray-400 mb-2">
              — <span className="font-semibold text-white">Casey DiGennaro</span>
            </p>
            <p className="text-sm text-gray-500">
              Founder, SuperInstance.AI
            </p>
          </div>
        </div>
      </section>

      {/* Timeline */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-dark-800/30">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl sm:text-3xl font-bold mb-12 text-center">The Journey</h2>
          
          <div className="space-y-8">
            {[
              {
                phase: "The Problem",
                icon: Anchor,
                description: "Needed AI on a boat with no internet and limited power. Cloud AI doesn't work. GPUs too expensive.",
              },
              {
                phase: "The Insight",
                icon: Cpu,
                description: "Realized ternary weights (only +1, 0, -1) could eliminate expensive multipliers. 90% fewer gates.",
              },
              {
                phase: "The Innovation",
                icon: Shield,
                description: "Mask-locked ROM: weights as physical metal patterns, not data. Immutable, unreadable, unstealable.",
              },
              {
                phase: "The Mission",
                icon: Heart,
                description: "Open-source everything. $99 price target. MIT license. Build your own.",
              },
            ].map((item, index) => (
              <div key={index} className="flex gap-6">
                <div className="flex flex-col items-center">
                  <div className="w-14 h-14 rounded-xl bg-green-500/20 border border-green-500/50 flex items-center justify-center text-green-400">
                    <item.icon className="w-6 h-6" />
                  </div>
                  {index < 3 && <div className="w-0.5 h-full bg-dark-600 mt-4" />}
                </div>
                <div className="pb-8">
                  <h3 className="font-semibold text-xl mb-3">{item.phase}</h3>
                  <p className="text-gray-400 leading-relaxed">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl sm:text-3xl font-bold mb-12 text-center">Core Values</h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            {[
              {
                title: "Privacy First",
                desc: "Your data should never leave your control. This isn't a feature — it's the foundation.",
                icon: Shield,
              },
              {
                title: "Open Source Forever",
                desc: "MIT license. No royalties. No restrictions. Build anything you want.",
                icon: Github,
              },
              {
                title: "Accessible to All",
                desc: "$99 target price. USB powered. No technical expertise required.",
                icon: Cpu,
              },
              {
                title: "Verifiable Trust",
                desc: "Don't trust — verify. All designs are open for inspection.",
                icon: Heart,
              },
            ].map((item) => (
              <div key={item.title} className="bg-dark-800/80 rounded-2xl p-8 border border-dark-600">
                <item.icon className="w-8 h-8 text-green-400 mb-4" />
                <h3 className="font-semibold text-xl mb-3 text-green-400">{item.title}</h3>
                <p className="text-gray-400 leading-relaxed">
                  {item.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Quote */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-dark-800/30">
        <div className="max-w-3xl mx-auto text-center">
          <blockquote className="text-2xl sm:text-3xl text-gray-300 italic leading-relaxed">
            &ldquo;I built this because I needed it. I&apos;m sharing it because I think you might need it too.&rdquo;
          </blockquote>
          <p className="mt-6 text-gray-400">— Casey DiGennaro</p>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-green-900/20 to-dark-900">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-6">Join the Mission</h2>
          <p className="text-gray-400 text-lg mb-10">
            Download everything. Build something amazing.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/download"
              className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-8 py-4 rounded-xl font-medium transition-all glow-green shadow-lg"
            >
              <Download className="w-5 h-5" />
              Download Everything
            </Link>
            <a
              href="https://github.com/superinstance/ternaryair"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 bg-dark-700/80 hover:bg-dark-600 text-white px-8 py-4 rounded-xl font-medium transition-all border border-dark-500"
            >
              <Github className="w-5 h-5" />
              View on GitHub
              <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
