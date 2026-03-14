import Link from "next/link";
import {
  Code,
  Terminal,
  Package,
  Zap,
  CheckCircle,
  ArrowRight,
  BookOpen,
  Copy,
  Server,
  Webhook,
} from "lucide-react";

export default function DevelopersPage() {
  return (
    <div className="min-h-screen pt-24 pb-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="w-16 h-16 rounded-2xl bg-purple-500/10 flex items-center justify-center mx-auto mb-6">
            <Code className="w-8 h-8 text-purple-400" />
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="gradient-text-developer">For Developers</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            SDK documentation, API reference, code examples, and integration guides for building with TernaryAir.
          </p>
        </div>

        {/* Quick Start */}
        <section id="quick-start" className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Zap className="w-6 h-6 text-purple-400" />
            Quick Start
          </h2>

          <div className="code-block mb-6">
            <div className="code-header">
              <div className="code-dot bg-red-500" />
              <div className="code-dot bg-yellow-500" />
              <div className="code-dot bg-green-500" />
              <span className="ml-2 text-gray-400 text-sm">Installation</span>
            </div>
            <div className="code-content font-mono text-sm">
              <div className="text-gray-500"># Install via pip</div>
              <div><span className="text-green-400">$</span> pip install ternaryair</div>
              <br />
              <div className="text-gray-500"># Or with optional dependencies</div>
              <div><span className="text-green-400">$</span> pip install ternaryair[server,simulator]</div>
            </div>
          </div>

          <div className="code-block">
            <div className="code-header">
              <div className="code-dot bg-red-500" />
              <div className="code-dot bg-yellow-500" />
              <div className="code-dot bg-green-500" />
              <span className="ml-2 text-gray-400 text-sm">Hello World</span>
            </div>
            <div className="code-content font-mono text-sm">
              <div><span className="text-purple-400">from</span> ternaryair <span className="text-purple-400">import</span> TernaryAir, Simulator</div>
              <br />
              <div className="text-gray-500"># Create device with simulator backend</div>
              <div>device = TernaryAir(backend=Simulator())</div>
              <br />
              <div className="text-gray-500"># Generate text</div>
              <div>response = device.generate(<span className="text-green-400">&quot;Hello, TernaryAir!&quot;</span>)</div>
              <div><span className="text-purple-400">print</span>(response)</div>
            </div>
          </div>
        </section>

        {/* Python SDK */}
        <section id="sdk" className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Package className="w-6 h-6 text-purple-400" />
            Python SDK
          </h2>

          <div className="feature-card mb-6">
            <h3 className="font-semibold text-lg mb-4">Basic Usage</h3>
            <div className="code-block">
              <div className="code-content font-mono text-sm">
                <div><span className="text-purple-400">from</span> ternaryair <span className="text-purple-400">import</span> TernaryAir</div>
                <br />
                <div className="text-gray-500"># Connect to physical device</div>
                <div>device = TernaryAir() <span className="text-gray-500"># Auto-detects USB device</span></div>
                <br />
                <div className="text-gray-500"># Or use simulator for testing</div>
                <div><span className="text-purple-400">from</span> ternaryair <span className="text-purple-400">import</span> Simulator</div>
                <div>device = TernaryAir(backend=Simulator())</div>
                <br />
                <div className="text-gray-500"># Generate with parameters</div>
                <div>response = device.generate(</div>
                <div>    <span className="text-green-400">&quot;Write a haiku about AI&quot;</span>,</div>
                <div>    max_tokens=<span className="text-amber-300">100</span>,</div>
                <div>    temperature=<span className="text-amber-300">0.7</span></div>
                <div>)</div>
              </div>
            </div>
          </div>

          <div className="feature-card mb-6">
            <h3 className="font-semibold text-lg mb-4">Streaming</h3>
            <div className="code-block">
              <div className="code-content font-mono text-sm">
                <div className="text-gray-500"># Stream tokens as they&apos;re generated</div>
                <div><span className="text-purple-400">for</span> token <span className="text-purple-400">in</span> device.stream(<span className="text-green-400">&quot;Tell me a story&quot;</span>):</div>
                <div>    <span className="text-purple-400">print</span>(token, end=<span className="text-green-400">&quot;&quot;</span>, flush=<span className="text-amber-300">True</span>)</div>
              </div>
            </div>
          </div>

          <div className="feature-card">
            <h3 className="font-semibold text-lg mb-4">Chat Mode</h3>
            <div className="code-block">
              <div className="code-content font-mono text-sm">
                <div className="text-gray-500"># Multi-turn conversation</div>
                <div>messages = [</div>
                <div>    {<span className="text-green-400">&quot;role&quot;</span>: <span className="text-green-400">&quot;system&quot;</span>, <span className="text-green-400">&quot;content&quot;</span>: <span className="text-green-400">&quot;You are helpful.&quot;</span>},</div>
                <div>    {<span className="text-green-400">&quot;role&quot;</span>: <span className="text-green-400">&quot;user&quot;</span>, <span className="text-green-400">&quot;content&quot;</span>: <span className="text-green-400">&quot;What is 2+2?&quot;</span>}</div>
                <div>]</div>
                <br />
                <div>response = device.chat(messages)</div>
              </div>
            </div>
          </div>
        </section>

        {/* REST API */}
        <section id="api" className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <Server className="w-6 h-6 text-purple-400" />
            REST API Server
          </h2>

          <div className="feature-card mb-6">
            <p className="text-gray-300 mb-6">
              TernaryAir includes an OpenAI-compatible REST API server. Drop-in replacement for OpenAI API.
            </p>

            <div className="code-block mb-6">
              <div className="code-header">
                <span className="text-gray-400 text-sm">Start the server</span>
              </div>
              <div className="code-content font-mono text-sm">
                <div className="text-gray-500"># Start API server on port 8000</div>
                <div><span className="text-green-400">$</span> ternaryair-server --port 8000</div>
                <br />
                <div className="text-gray-500"># Or with custom config</div>
                <div><span className="text-green-400">$</span> ternaryair-server --config config.yaml</div>
              </div>
            </div>

            <h3 className="font-semibold text-lg mb-4">OpenAI Compatibility</h3>
            <div className="code-block">
              <div className="code-content font-mono text-sm">
                <div><span className="text-purple-400">from</span> openai <span className="text-purple-400">import</span> OpenAI</div>
                <br />
                <div className="text-gray-500"># Point OpenAI SDK to TernaryAir</div>
                <div>client = OpenAI(</div>
                <div>    base_url=<span className="text-green-400">&quot;http://localhost:8000/v1&quot;</span>,</div>
                <div>    api_key=<span className="text-green-400">&quot;not-needed&quot;</span>  <span className="text-gray-500"># No API key required</span></div>
                <div>)</div>
                <br />
                <div className="text-gray-500"># Use exactly like OpenAI</div>
                <div>response = client.chat.completions.create(</div>
                <div>    model=<span className="text-green-400">&quot;ternaryair&quot;</span>,</div>
                <div>    messages=[{<span className="text-green-400">&quot;role&quot;</span>: <span className="text-green-400">&quot;user&quot;</span>, <span className="text-green-400">&quot;content&quot;</span>: <span className="text-green-400">&quot;Hello!&quot;</span>}]</div>
                <div>)</div>
                <br />
                <div><span className="text-purple-400">print</span>(response.choices[0].message.content)</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="download-card">
              <Webhook className="w-6 h-6 text-purple-400 mb-3" />
              <h4 className="font-semibold mb-2">Endpoints</h4>
              <ul className="text-sm text-gray-400 space-y-1">
                <li><code className="text-green-400">POST /v1/completions</code></li>
                <li><code className="text-green-400">POST /v1/chat/completions</code></li>
                <li><code className="text-green-400">GET /v1/models</code></li>
                <li><code className="text-green-400">GET /health</code></li>
              </ul>
            </div>
            <div className="download-card">
              <CheckCircle className="w-6 h-6 text-purple-400 mb-3" />
              <h4 className="font-semibold mb-2">Compatible With</h4>
              <ul className="text-sm text-gray-400 space-y-1">
                <li>OpenAI Python SDK</li>
                <li>LangChain</li>
                <li>LlamaIndex</li>
                <li>Any OpenAI-compatible tool</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Examples */}
        <section id="examples" className="mb-16">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
            <BookOpen className="w-6 h-6 text-purple-400" />
            Code Examples
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="feature-card">
              <h4 className="font-semibold mb-2">CLI Tool</h4>
              <div className="code-block">
                <div className="code-content font-mono text-sm">
                  <div><span className="text-green-400">$</span> ternaryair chat</div>
                  <div><span className="text-green-400">$</span> ternaryair generate <span className="text-green-400">&quot;prompt&quot;</span></div>
                  <div><span className="text-green-400">$</span> ternaryair bench</div>
                </div>
              </div>
            </div>
            <div className="feature-card">
              <h4 className="font-semibold mb-2">Environment Variables</h4>
              <div className="code-block">
                <div className="code-content font-mono text-sm">
                  <div>TERNARYAIR_DEVICE=<span className="text-green-400">&quot;/dev/ttyUSB0&quot;</span></div>
                  <div>TERNARYAIR_BAUD=<span className="text-amber-300">115200</span></div>
                  <div>TERNARYAIR_TIMEOUT=<span className="text-amber-300">30</span></div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <div className="bg-gradient-to-br from-purple-500/10 to-purple-900/10 border border-purple-500/30 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold mb-4">Build Something Amazing</h3>
          <p className="text-gray-400 mb-6">
            Download TernaryAir and start building private, secure AI applications today.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/download" className="btn-primary">
              Download SDK
            </Link>
            <Link href="/engineers" className="btn-secondary">
              For Engineers
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
