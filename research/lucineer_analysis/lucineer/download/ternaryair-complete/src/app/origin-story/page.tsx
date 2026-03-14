import Link from "next/link";
import {
  Anchor,
  Waves,
  Zap,
  Lightbulb,
  Heart,
  ArrowRight,
  Compass,
} from "lucide-react";

export default function OriginStoryPage() {
  return (
    <div className="min-h-screen pt-24 pb-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="w-16 h-16 rounded-2xl bg-blue-500/10 flex items-center justify-center mx-auto mb-6">
            <Anchor className="w-8 h-8 text-blue-400" />
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="gradient-text">The Origin Story</span>
          </h1>
          <p className="text-xl text-gray-400">
            How a fisherman&apos;s need for AI on a boat led to a revolutionary new architecture.
          </p>
        </div>

        {/* Story */}
        <article className="prose prose-invert prose-lg max-w-none">
          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <Waves className="w-6 h-6 text-blue-400" />
              <h2 className="text-2xl font-bold m-0">The Problem</h2>
            </div>
            <p className="text-gray-300 leading-relaxed">
              I&apos;m Casey DiGennaro. By trade, I&apos;m a software developer. By passion, I&apos;m a fisherman. 
              I spend my weekends on a boat off the coast of Maine, where cell service is a distant memory 
              and the only cloud is the one that might bring rain.
            </p>
            <p className="text-gray-300 leading-relaxed">
              A few years ago, I started experimenting with AI. Like everyone else, I was amazed by what 
              these systems could do. But I kept running into the same problem: <span className="text-blue-400 font-semibold">I could only use them 
              when I had internet.</span>
            </p>
            <p className="text-gray-300 leading-relaxed">
              On my boat, in the middle of nowhere, I was cut off from the AI revolution. Sure, I could 
              download a model and run it locally—but that required a powerful laptop with a GPU that 
              would drain my batteries in an hour. Not exactly practical when you&apos;re 20 miles offshore.
            </p>
          </section>

          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <Lightbulb className="w-6 h-6 text-amber-400" />
              <h2 className="text-2xl font-bold m-0">The Insight</h2>
            </div>
            <p className="text-gray-300 leading-relaxed">
              I started thinking about what I actually needed from AI. I didn&apos;t need to train models. 
              I didn&apos;t need to run different models every day. I just wanted one capable model that 
              worked—offline, with limited power, forever.
            </p>
            <p className="text-gray-300 leading-relaxed">
              And then it hit me: <span className="text-amber-400 font-semibold">why do we store AI weights in memory at all?</span>
            </p>
            <p className="text-gray-300 leading-relaxed">
              Traditional chips treat model weights like data—they&apos;re loaded from memory every time 
              you run inference. That&apos;s fine if you want flexibility. But what if you&apos;re willing to 
              trade flexibility for efficiency? What if you could bake the weights directly into silicon, 
              making them part of the chip&apos;s physical structure?
            </p>
            <p className="text-gray-300 leading-relaxed">
              That&apos;s when I discovered ternary neural networks—models that work with just three 
              weight values: -1, 0, and +1. With ternary weights, you don&apos;t need multiplication. 
              You just need to add, subtract, or ignore. A simple sign flip replaces a complex 
              multiply operation.
            </p>
          </section>

          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <Zap className="w-6 h-6 text-green-400" />
              <h2 className="text-2xl font-bold m-0">The Solution</h2>
            </div>
            <p className="text-gray-300 leading-relaxed">
              I designed the RAU—Rotation-Accumulate Unit. Instead of multiplying weights by activations, 
              the RAU simply rotates (negates) or passes through activations based on the weight value. 
              <span className="text-green-400 font-semibold"> No multiplication needed. 90% fewer gates. 85% less power.</span>
            </p>
            <p className="text-gray-300 leading-relaxed">
              Combined with mask-locking—encoding weights in the chip&apos;s metal interconnect layers—the 
              result is a device that can run capable AI models at 100+ tokens per second, drawing only 
              3-5 watts from a USB port. No internet required. No cloud subscription. No data leaving 
              your device.
            </p>
            <p className="text-gray-300 leading-relaxed">
              The model is literally frozen in silicon. It can&apos;t be updated, hacked, or modified 
              remotely. It&apos;s a function, not a program. Input goes in, output comes out, and 
              nothing else happens.
            </p>
          </section>

          <section className="mb-12">
            <div className="flex items-center gap-3 mb-6">
              <Compass className="w-6 h-6 text-purple-400" />
              <h2 className="text-2xl font-bold m-0">The Mission</h2>
            </div>
            <p className="text-gray-300 leading-relaxed">
              I realized this wasn&apos;t just about fishing boats. This was about bringing AI to 
              <span className="text-purple-400 font-semibold"> everyone, everywhere</span>—not just people with fast internet and expensive hardware.
            </p>
            <p className="text-gray-300 leading-relaxed">
              Students in rural areas. Researchers in the field. Journalists working on sensitive stories. 
              Healthcare providers handling private data. Anyone who needs AI that works offline, 
              protects their privacy, and doesn&apos;t require a subscription.
            </p>
            <p className="text-gray-300 leading-relaxed">
              That&apos;s why TernaryAir is open source. MIT licensed. The complete RTL, SDK, and 
              documentation are available for anyone to use, modify, and build upon. Because the 
              future of AI shouldn&apos;t be locked behind APIs and paywalls.
            </p>
          </section>
        </article>

        {/* Quote */}
        <div className="feature-card my-12">
          <blockquote className="text-xl sm:text-2xl text-gray-200 italic text-center mb-4">
            &ldquo;I designed TernaryAir because I needed AI that works on a boat. 
            But the problems I solved—offline operation, low power, privacy by design—turn 
            out to be problems everyone has.&rdquo;
          </blockquote>
          <p className="text-center text-gray-400">
            — Casey DiGennaro, Founder of SuperInstance.AI
          </p>
        </div>

        {/* CTA */}
        <div className="bg-gradient-to-br from-green-500/10 to-green-900/10 border border-green-500/30 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold mb-4">Join the Journey</h3>
          <p className="text-gray-400 mb-6">
            Download TernaryAir and experience AI that works anywhere.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/download" className="btn-primary">
              Download Now
            </Link>
            <Link href="/architecture" className="btn-secondary">
              Explore the Architecture
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
