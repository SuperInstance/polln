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
  CheckCircle,
  FileCode,
  Cpu,
} from "lucide-react";

export default function DevelopersPage() {
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

  return (
    <div className="animated-bg min-h-screen pt-20">
      {/* Hero */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 bg-developer/10 border border-developer/30 rounded-full px-4 py-2 mb-6">
              <Code className="w-4 h-4 text-developer" />
              <span className="text-developer text-sm font-medium">
                For Developers
              </span>
            </div>

            <h1 className="text-4xl sm:text-5xl font-bold mb-6">
              <span className="gradient-text-developer">Build with TernaryAir</span>
            </h1>

            <p className="text-xl text-gray-300 mb-4 max-w-3xl mx-auto">
              Python SDK with clean API, streaming support, and zero-config setup
            </p>

            <p className="text-gray-400 max-w-2xl mx-auto">
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
                <code className="font-mono text-developer">
                  pip install ternaryair
                </code>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText("pip install ternaryair");
                  }}
                  className="p-2 hover:bg-dark-600 rounded transition-colors"
                >
                  <Copy className="w-4 h-4 text-gray-400" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Start */}
      <section id="quick-start" className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Quick Start</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              From zero to running inference in under a minute
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500">
              <div className="w-10 h-10 rounded-full bg-developer/20 flex items-center justify-center mb-4 text-developer font-bold">
                1
              </div>
              <h3 className="font-semibold mb-2">Install</h3>
              <code className="text-sm text-gray-400 font-mono">
                pip install ternaryair
              </code>
            </div>

            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500">
              <div className="w-10 h-10 rounded-full bg-developer/20 flex items-center justify-center mb-4 text-developer font-bold">
                2
              </div>
              <h3 className="font-semibold mb-2">Import</h3>
              <code className="text-sm text-gray-400 font-mono">
                from ternaryair import TernaryAir
              </code>
            </div>

            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500">
              <div className="w-10 h-10 rounded-full bg-developer/20 flex items-center justify-center mb-4 text-developer font-bold">
                3
              </div>
              <h3 className="font-semibold mb-2">Generate</h3>
              <code className="text-sm text-gray-400 font-mono">
                device.generate("Hello!")
              </code>
            </div>
          </div>
        </div>
      </section>

      {/* Code Examples */}
      <section id="examples" className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Code Examples</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Common patterns for using TernaryAir
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {codeExamples.map((example, index) => (
              <div key={index} className="code-block">
                <div className="code-header">
                  <FileCode className="w-4 h-4 text-developer" />
                  <span className="ml-2 text-gray-400 text-sm">
                    {example.title}
                  </span>
                </div>
                <div className="code-content font-mono text-sm">
                  <pre className="whitespace-pre-wrap">{example.code}</pre>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* API Reference */}
      <section id="api" className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">API Reference</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Complete SDK documentation
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* TernaryAir Class */}
            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500">
              <h3 className="text-xl font-semibold mb-4 text-developer">
                TernaryAir Class
              </h3>
              <p className="text-sm text-gray-400 mb-4">
                Main interface for inference operations.
              </p>

              <div className="space-y-4">
                <div className="border-b border-dark-500 pb-4">
                  <h4 className="font-mono text-sm text-user mb-2">
                    __init__(config=None, backend=None, device_path=None)
                  </h4>
                  <p className="text-xs text-gray-500">
                    Initialize TernaryAir interface. Use Simulator backend for
                    software simulation.
                  </p>
                </div>

                <div className="border-b border-dark-500 pb-4">
                  <h4 className="font-mono text-sm text-user mb-2">
                    generate(prompt, max_tokens=None, temperature=None, ...)
                  </h4>
                  <p className="text-xs text-gray-500">
                    Generate text completion for the given prompt. Returns
                    string.
                  </p>
                </div>

                <div className="border-b border-dark-500 pb-4">
                  <h4 className="font-mono text-sm text-user mb-2">
                    stream(prompt, max_tokens=None, ...)
                  </h4>
                  <p className="text-xs text-gray-500">
                    Stream text generation token by token. Yields strings.
                  </p>
                </div>

                <div className="border-b border-dark-500 pb-4">
                  <h4 className="font-mono text-sm text-user mb-2">
                    batch_generate(prompts, ...)
                  </h4>
                  <p className="text-xs text-gray-500">
                    Generate completions for multiple prompts. Returns list of
                    strings.
                  </p>
                </div>

                <div>
                  <h4 className="font-mono text-sm text-user mb-2">
                    conversation()
                  </h4>
                  <p className="text-xs text-gray-500">
                    Start a conversation session with context retention.
                  </p>
                </div>
              </div>
            </div>

            {/* Config Class */}
            <div className="bg-dark-700 rounded-xl p-6 border border-dark-500">
              <h3 className="text-xl font-semibold mb-4 text-developer">
                Config Class
              </h3>
              <p className="text-sm text-gray-400 mb-4">
                Configuration options for inference parameters.
              </p>

              <div className="space-y-3 text-sm">
                <div className="flex justify-between border-b border-dark-500 pb-2">
                  <span className="text-gray-300">max_tokens</span>
                  <span className="text-gray-500">int (default: 100)</span>
                </div>
                <div className="flex justify-between border-b border-dark-500 pb-2">
                  <span className="text-gray-300">temperature</span>
                  <span className="text-gray-500">float (default: 0.7)</span>
                </div>
                <div className="flex justify-between border-b border-dark-500 pb-2">
                  <span className="text-gray-300">top_p</span>
                  <span className="text-gray-500">float (default: 0.9)</span>
                </div>
                <div className="flex justify-between border-b border-dark-500 pb-2">
                  <span className="text-gray-300">top_k</span>
                  <span className="text-gray-500">int (default: 40)</span>
                </div>
                <div className="flex justify-between border-b border-dark-500 pb-2">
                  <span className="text-gray-300">repeat_penalty</span>
                  <span className="text-gray-500">float (default: 1.1)</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">device_path</span>
                  <span className="text-gray-500">str (auto-detect)</span>
                </div>
              </div>

              <div className="mt-6">
                <h4 className="font-semibold mb-2">Presets</h4>
                <div className="space-y-2">
                  <div className="bg-dark-600 rounded p-2 font-mono text-xs">
                    Config.default() # Balanced settings
                  </div>
                  <div className="bg-dark-600 rounded p-2 font-mono text-xs">
                    Config.deterministic() # temperature=0
                  </div>
                  <div className="bg-dark-600 rounded p-2 font-mono text-xs">
                    Config.creative() # temperature=1.0
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Exceptions */}
          <div className="mt-8 bg-dark-700 rounded-xl p-6 border border-dark-500">
            <h3 className="text-xl font-semibold mb-4 text-developer">
              Exceptions
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <h4 className="font-mono text-sm text-red-400">
                  TernaryAirError
                </h4>
                <p className="text-xs text-gray-500">Base exception class</p>
              </div>
              <div>
                <h4 className="font-mono text-sm text-red-400">
                  DeviceNotFoundError
                </h4>
                <p className="text-xs text-gray-500">Device not connected</p>
              </div>
              <div>
                <h4 className="font-mono text-sm text-red-400">
                  ConnectionError
                </h4>
                <p className="text-xs text-gray-500">Connection failed</p>
              </div>
              <div>
                <h4 className="font-mono text-sm text-red-400">
                  InferenceError
                </h4>
                <p className="text-xs text-gray-500">Inference failed</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* SDK Details */}
      <section id="sdk" className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Python SDK Features</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              Everything you need to integrate TernaryAir into your applications
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-dark-800 rounded-xl p-6 border border-dark-600">
              <Zap className="w-8 h-8 text-developer mb-4" />
              <h3 className="font-semibold mb-2">Streaming Support</h3>
              <p className="text-sm text-gray-400">
                Real-time token streaming for responsive UIs and long-form
                generation.
              </p>
            </div>

            <div className="bg-dark-800 rounded-xl p-6 border border-dark-600">
              <Package className="w-8 h-8 text-developer mb-4" />
              <h3 className="font-semibold mb-2">Software Simulator</h3>
              <p className="text-sm text-gray-400">
                Develop and test without hardware using the built-in simulator.
              </p>
            </div>

            <div className="bg-dark-800 rounded-xl p-6 border border-dark-600">
              <Play className="w-8 h-8 text-developer mb-4" />
              <h3 className="font-semibold mb-2">Batch Processing</h3>
              <p className="text-sm text-gray-400">
                Process multiple prompts efficiently with batch_generate().
              </p>
            </div>

            <div className="bg-dark-800 rounded-xl p-6 border border-dark-600">
              <Cpu className="w-8 h-8 text-developer mb-4" />
              <h3 className="font-semibold mb-2">Device Info</h3>
              <p className="text-sm text-gray-400">
                Query device status, temperature, power consumption, and more.
              </p>
            </div>

            <div className="bg-dark-800 rounded-xl p-6 border border-dark-600">
              <BookOpen className="w-8 h-8 text-developer mb-4" />
              <h3 className="font-semibold mb-2">Context Manager</h3>
              <p className="text-sm text-gray-400">
                Automatic resource management with Python context managers.
              </p>
            </div>

            <div className="bg-dark-800 rounded-xl p-6 border border-dark-600">
              <Terminal className="w-8 h-8 text-developer mb-4" />
              <h3 className="font-semibold mb-2">CLI Tool</h3>
              <p className="text-sm text-gray-400">
                Command-line interface for quick testing and scripting.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* OpenAI Compatible */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800/50">
        <div className="max-w-4xl mx-auto">
          <div className="bg-developer/5 border border-developer/30 rounded-xl p-8 text-center">
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
                <pre>{`# Drop-in replacement for OpenAI
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
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-developer/10 to-dark-900">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">Start Building Today</h2>
          <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
            Download the SDK and integrate private AI into your applications.
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/download"
              className="flex items-center gap-2 bg-developer hover:bg-developer-dark text-white px-8 py-4 rounded-lg font-medium transition-all glow-purple"
            >
              <Download className="w-5 h-5" />
              Download SDK
            </Link>

            <Link
              href="/architecture"
              className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-8 py-4 rounded-lg font-medium transition-all border border-dark-500"
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
