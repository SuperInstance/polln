import Link from "next/link";
import {
  Code,
  Terminal,
  BookOpen,
  Zap,
  Package,
  Play,
  ArrowRight,
  Download,
  Copy,
  FileCode,
  Cpu,
} from "lucide-react";

const codeExamples = [
  {
    title: "Basic Generation",
    code: `from ternaryair import TernaryAir

# Connect to device (or use simulator)
device = TernaryAir()

# Generate text
response = device.generate("Hello, how are you?")
print(response)
# Output: "I'm doing well, thank you for asking!"`,
  },
  {
    title: "Streaming",
    code: `from ternaryair import TernaryAir

device = TernaryAir()

# Stream tokens as they're generated
for token in device.stream("Tell me a story about"):
    print(token, end='', flush=True)`,
  },
  {
    title: "With Simulator",
    code: `from ternaryair import TernaryAir, Simulator

# Use software simulator (no hardware needed)
device = TernaryAir(backend=Simulator())

response = device.generate("What is machine learning?")
print(response)`,
  },
  {
    title: "Conversation Mode",
    code: `from ternaryair import TernaryAir

device = TernaryAir()

with device.conversation() as chat:
    chat.send("My name is Alice")
    response = chat.send("What's my name?")
    # Device remembers "Alice" from previous message`,
  },
];

export default function DevelopersPage() {
  return (
    <div className="animated-bg min-h-screen pt-20">
      {/* Hero */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/30 rounded-full px-5 py-2 mb-6">
              <Code className="w-4 h-4 text-purple-400" />
              <span className="text-purple-400 text-sm font-medium">
                For Developers
              </span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-6">
              <span className="gradient-text-developer">Build with TernaryAir</span>
            </h1>

            <p className="text-xl text-gray-300 mb-4 max-w-3xl mx-auto">
              Python SDK with clean API, streaming support, and zero-config setup
            </p>

            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Get started in seconds with pip install. Works with our hardware
              device or software simulator.
            </p>
          </div>

          {/* Quick Install */}
          <div className="max-w-2xl mx-auto mb-12">
            <div className="code-block">
              <div className="code-header">
                <div className="code-dot bg-red-500" />
                <div className="code-dot bg-yellow-500" />
                <div className="code-dot bg-green-500" />
                <span className="ml-2 text-gray-400 text-sm">Terminal</span>
              </div>
              <div className="code-content flex items-center justify-between">
                <code className="font-mono text-purple-400 text-lg">
                  $ pip install ternaryair
                </code>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText("pip install ternaryair");
                  }}
                  className="p-2 hover:bg-dark-600 rounded-lg transition-colors group"
                  title="Copy to clipboard"
                >
                  <Copy className="w-5 h-5 text-gray-400 group-hover:text-white" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Start */}
      <section id="quick-start" className="py-20 px-4 sm:px-6 lg:px-8 bg-dark-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Quick Start</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              From zero to running inference in under a minute
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            {[
              {
                step: 1,
                title: "Install",
                code: "pip install ternaryair",
              },
              {
                step: 2,
                title: "Import",
                code: "from ternaryair import TernaryAir",
              },
              {
                step: 3,
                title: "Generate",
                code: 'device.generate("Hello!")',
              },
            ].map((item) => (
              <div
                key={item.step}
                className="bg-dark-800/80 rounded-2xl p-6 border border-dark-600"
              >
                <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center mb-5 text-purple-400 font-bold text-lg">
                  {item.step}
                </div>
                <h3 className="font-semibold mb-3 text-lg">{item.title}</h3>
                <code className="text-sm text-gray-400 font-mono bg-dark-700 px-3 py-2 rounded-lg block">
                  {item.code}
                </code>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Code Examples */}
      <section id="examples" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Code Examples</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Common patterns for using TernaryAir
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {codeExamples.map((example, index) => (
              <div key={index} className="code-block">
                <div className="code-header">
                  <FileCode className="w-4 h-4 text-purple-400" />
                  <span className="ml-2 text-gray-400 text-sm">
                    {example.title}
                  </span>
                </div>
                <div className="code-content font-mono text-sm">
                  <pre className="whitespace-pre-wrap text-gray-300">{example.code}</pre>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* API Reference */}
      <section id="api" className="py-20 px-4 sm:px-6 lg:px-8 bg-dark-800/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">API Reference</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Complete SDK documentation
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* TernaryAir Class */}
            <div className="bg-dark-800/80 rounded-2xl p-8 border border-dark-600">
              <h3 className="text-xl font-semibold mb-4 text-purple-400">
                TernaryAir Class
              </h3>
              <p className="text-sm text-gray-400 mb-6">
                Main interface for inference operations.
              </p>

              <div className="space-y-5">
                {[
                  {
                    sig: "__init__(config=None, backend=None, device_path=None)",
                    desc: "Initialize TernaryAir interface. Use Simulator backend for software simulation.",
                  },
                  {
                    sig: "generate(prompt, max_tokens=None, temperature=None, ...)",
                    desc: "Generate text completion for the given prompt. Returns string.",
                  },
                  {
                    sig: "stream(prompt, max_tokens=None, ...)",
                    desc: "Stream text generation token by token. Yields strings.",
                  },
                  {
                    sig: "batch_generate(prompts, ...)",
                    desc: "Generate completions for multiple prompts. Returns list of strings.",
                  },
                  {
                    sig: "conversation()",
                    desc: "Start a conversation session with context retention.",
                  },
                ].map((method) => (
                  <div key={method.sig} className="border-b border-dark-600 pb-4 last:border-0 last:pb-0">
                    <h4 className="font-mono text-sm text-blue-400 mb-2">
                      {method.sig}
                    </h4>
                    <p className="text-xs text-gray-500">
                      {method.desc}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Config Class */}
            <div className="bg-dark-800/80 rounded-2xl p-8 border border-dark-600">
              <h3 className="text-xl font-semibold mb-4 text-purple-400">
                Config Class
              </h3>
              <p className="text-sm text-gray-400 mb-6">
                Configuration options for inference parameters.
              </p>

              <div className="space-y-3 text-sm mb-6">
                {[
                  { name: "max_tokens", type: "int", default: "100" },
                  { name: "temperature", type: "float", default: "0.7" },
                  { name: "top_p", type: "float", default: "0.9" },
                  { name: "top_k", type: "int", default: "40" },
                  { name: "repeat_penalty", type: "float", default: "1.1" },
                  { name: "device_path", type: "str", default: "auto-detect" },
                ].map((param) => (
                  <div key={param.name} className="flex justify-between border-b border-dark-600 pb-2">
                    <span className="text-gray-300">{param.name}</span>
                    <span className="text-gray-500">{param.type} ({param.default})</span>
                  </div>
                ))}
              </div>

              <div>
                <h4 className="font-semibold mb-3">Presets</h4>
                <div className="space-y-2">
                  {[
                    "Config.default()     # Balanced settings",
                    "Config.deterministic() # temperature=0",
                    "Config.creative()    # temperature=1.0",
                  ].map((preset) => (
                    <div key={preset} className="bg-dark-700 rounded-lg p-2 font-mono text-xs text-gray-400">
                      {preset}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Exceptions */}
          <div className="mt-8 bg-dark-800/80 rounded-2xl p-8 border border-dark-600">
            <h3 className="text-xl font-semibold mb-6 text-purple-400">
              Exceptions
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {[
                { name: "TernaryAirError", desc: "Base exception class" },
                { name: "DeviceNotFoundError", desc: "Device not connected" },
                { name: "ConnectionError", desc: "Connection failed" },
                { name: "InferenceError", desc: "Inference failed" },
              ].map((exc) => (
                <div key={exc.name}>
                  <h4 className="font-mono text-sm text-red-400">
                    {exc.name}
                  </h4>
                  <p className="text-xs text-gray-500 mt-1">{exc.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* SDK Details */}
      <section id="sdk" className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">Python SDK Features</h2>
            <p className="text-gray-400 max-w-2xl mx-auto text-lg">
              Everything you need to integrate TernaryAir into your applications
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: Zap,
                title: "Streaming Support",
                desc: "Real-time token streaming for responsive UIs and long-form generation.",
              },
              {
                icon: Package,
                title: "Software Simulator",
                desc: "Develop and test without hardware using the built-in simulator.",
              },
              {
                icon: Play,
                title: "Batch Processing",
                desc: "Process multiple prompts efficiently with batch_generate().",
              },
              {
                icon: Cpu,
                title: "Device Info",
                desc: "Query device status, temperature, power consumption, and more.",
              },
              {
                icon: BookOpen,
                title: "Context Manager",
                desc: "Automatic resource management with Python context managers.",
              },
              {
                icon: Terminal,
                title: "CLI Tool",
                desc: "Command-line interface for quick testing and scripting.",
              },
            ].map((feature) => (
              <div key={feature.title} className="bg-dark-800/80 rounded-2xl p-6 border border-dark-600">
                <feature.icon className="w-8 h-8 text-purple-400 mb-4" />
                <h3 className="font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-gray-400">
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* OpenAI Compatible */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-dark-800/30">
        <div className="max-w-4xl mx-auto">
          <div className="bg-purple-500/5 border border-purple-500/30 rounded-2xl p-8 text-center">
            <h2 className="text-2xl font-bold mb-4">OpenAI-Compatible API</h2>
            <p className="text-gray-400 mb-6">
              TernaryAir provides an OpenAI-compatible interface for easy
              integration with existing applications.
            </p>

            <div className="code-block text-left">
              <div className="code-header">
                <span className="text-gray-400 text-sm">
                  Coming Soon: Direct Compatibility
                </span>
              </div>
              <div className="code-content font-mono text-sm">
                <pre className="text-gray-300">{`# Drop-in replacement for OpenAI
from ternaryair import OpenAI

client = OpenAI()  # Uses TernaryAir device

response = client.chat.completions.create(
    model="ternaryair-350m",
    messages=[{"role": "user", "content": "Hello!"}]
)`}</pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-purple-900/20 to-dark-900">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl sm:text-4xl font-bold mb-6">Start Building Today</h2>
          <p className="text-gray-400 text-lg mb-10 max-w-2xl mx-auto">
            Download the SDK and integrate private AI into your applications.
            MIT licensed, open source, forever free.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/download"
              className="flex items-center gap-2 bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-500 hover:to-violet-500 text-white px-8 py-4 rounded-xl font-medium transition-all glow-purple shadow-lg"
            >
              <Download className="w-5 h-5" />
              Download SDK
            </Link>

            <Link
              href="/architecture"
              className="flex items-center gap-2 bg-dark-700/80 hover:bg-dark-600 text-white px-8 py-4 rounded-xl font-medium transition-all border border-dark-500"
            >
              View Architecture
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
