import Link from "next/link";
import { Download, ArrowRight, Fish } from "lucide-react";

export default function OriginStoryPage() {
  return (
    <div className="animated-bg min-h-screen pt-20">
      {/* Hero */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 bg-primary-500/10 border border-primary-500/30 rounded-full px-4 py-2 mb-6">
              <Fish className="w-4 h-4 text-primary-400" />
              <span className="text-primary-400 text-sm font-medium">Origin Story</span>
            </div>

            <h1 className="text-4xl sm:text-5xl font-bold mb-6">
              <span className="gradient-text">How TernaryAir Was Born</span>
            </h1>
          </div>
        </div>
      </section>

      {/* The Story */}
      <section className="py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto">
          <div className="prose prose-invert prose-lg max-w-none">
            <blockquote className="text-xl text-gray-300 italic leading-relaxed space-y-6 border-l-4 border-primary-500 pl-6">
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
              
              <p>
                The mask-locked design started as a cost optimization (no external 
                memory for weights). But I realized it&apos;s also the most secure AI 
                architecture possible — the model is literally frozen in silicon. 
                It can&apos;t be modified, can&apos;t be extracted, can&apos;t phone home.
              </p>
              
              <p>
                That&apos;s the hardware boundary between you and AI agents.
              </p>
              
              <p className="text-primary-400 font-semibold not-italic">
                I&apos;m releasing everything under MIT license. Build your own. 
                Improve it. Use it for whatever you want.
              </p>
              
              <p className="text-primary-400 font-semibold not-italic">
                AI should work for you, not the other way around.
              </p>
            </blockquote>
          </div>
          
          <div className="mt-12 text-center text-gray-400">
            — <span className="font-semibold text-white">Casey DiGennaro</span>
            <br />
            <span className="text-sm">Founder, SuperInstance.AI</span>
          </div>
        </div>
      </section>

      {/* Timeline */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold mb-8 text-center">The Journey</h2>
          
          <div className="space-y-6">
            {[
              {
                phase: "The Problem",
                description: "Needed AI on a boat with no internet and limited power. Cloud AI doesn't work. GPUs too expensive.",
              },
              {
                phase: "The Insight",
                description: "Realized ternary weights (only +1, 0, -1) could eliminate expensive multipliers. 90% fewer gates.",
              },
              {
                phase: "The Innovation",
                description: "Mask-locked ROM: weights as physical metal patterns, not data. Immutable, unreadable, unstealable.",
              },
              {
                phase: "The Mission",
                description: "Open-source everything. $99 price target. MIT license. Build your own.",
              },
            ].map((item, index) => (
              <div key={index} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="w-10 h-10 rounded-full bg-primary-500/20 border border-primary-500/50 flex items-center justify-center text-primary-400 font-bold">
                    {index + 1}
                  </div>
                  {index < 3 && <div className="w-px h-full bg-dark-500 mt-2" />}
                </div>
                <div className="pb-8">
                  <h3 className="font-semibold text-lg mb-2">{item.phase}</h3>
                  <p className="text-gray-400">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Values */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold mb-8 text-center">Core Values</h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-dark-800 rounded-xl p-6 border border-dark-600">
              <h3 className="font-semibold mb-2 text-primary-400">Privacy First</h3>
              <p className="text-sm text-gray-400">
                Your data should never leave your control. This isn&apos;t a feature — 
                it&apos;s the foundation.
              </p>
            </div>
            
            <div className="bg-dark-800 rounded-xl p-6 border border-dark-600">
              <h3 className="font-semibold mb-2 text-primary-400">Open Source Forever</h3>
              <p className="text-sm text-gray-400">
                MIT license. No royalties. No restrictions. Build anything you want.
              </p>
            </div>
            
            <div className="bg-dark-800 rounded-xl p-6 border border-dark-600">
              <h3 className="font-semibold mb-2 text-primary-400">Accessible to All</h3>
              <p className="text-sm text-gray-400">
                $99 target price. USB powered. No technical expertise required.
              </p>
            </div>
            
            <div className="bg-dark-800 rounded-xl p-6 border border-dark-600">
              <h3 className="font-semibold mb-2 text-primary-400">Verifiable Trust</h3>
              <p className="text-sm text-gray-400">
                Don&apos;t trust — verify. All designs are open for inspection.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-primary-900/20 to-dark-900">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Join the Mission</h2>
          <p className="text-gray-400 mb-8">
            Download everything. Build something amazing.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/download"
              className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-8 py-4 rounded-lg font-medium transition-all glow-green"
            >
              <Download className="w-5 h-5" />
              Download Everything
            </Link>
            <a
              href="https://github.com/superinstance/ternaryair"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-8 py-4 rounded-lg font-medium transition-all border border-dark-500"
            >
              View on GitHub
              <ArrowRight className="w-4 h-4" />
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
