import Link from "next/link";
import {
  Download,
  FileCode,
  Package,
  FileText,
  HardDrive,
  Terminal,
  FolderArchive,
  Github,
  CheckCircle,
  ExternalLink,
} from "lucide-react";

export default function DownloadPage() {
  return (
    <div className="min-h-screen pt-24 pb-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="gradient-text">Download TernaryAir</span>
          </h1>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto">
            Get everything you need: RTL source code, Python SDK, REST API server, and comprehensive documentation.
          </p>
        </div>

        {/* Quick Download */}
        <div className="bg-gradient-to-br from-green-500/10 to-green-900/10 border border-green-500/30 rounded-2xl p-8 mb-16">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div>
              <h2 className="text-2xl font-bold mb-2 flex items-center gap-3">
                <FolderArchive className="w-7 h-7 text-green-400" />
                Complete Package
              </h2>
              <p className="text-gray-400">
                Download everything in one ZIP file: RTL, SDK, API, docs, and examples.
              </p>
              <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                <span className="flex items-center gap-1"><CheckCircle className="w-4 h-4 text-green-400" /> v1.0.0</span>
                <span className="flex items-center gap-1"><CheckCircle className="w-4 h-4 text-green-400" /> MIT License</span>
                <span className="flex items-center gap-1"><CheckCircle className="w-4 h-4 text-green-400" /> ~2.5 MB</span>
              </div>
            </div>
            <a
              href="/ternaryair-complete.zip"
              className="btn-primary text-lg whitespace-nowrap"
            >
              <Download className="w-5 h-5" />
              Download ZIP
            </a>
          </div>
        </div>

        {/* Package Contents */}
        <h2 id="contents" className="text-3xl font-bold mb-8">Package Contents</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-16">
          {/* RTL Source */}
          <div id="rtl" className="feature-card">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center">
                <HardDrive className="w-6 h-6 text-amber-400" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">RTL Source Code</h3>
                <span className="text-sm text-gray-500">SystemVerilog</span>
              </div>
            </div>
            <p className="text-gray-400 text-sm mb-4">
              Complete RTL implementation including the RAU (Rotation-Accumulate Unit), synaptic array, 
              weight ROM, KV cache, and top-level inference engine.
            </p>
            <div className="code-block mb-4">
              <div className="code-content text-sm font-mono">
                <div className="text-gray-500">rtl/</div>
                <div className="ml-4">├── <span className="text-amber-300">rau.sv</span> <span className="text-gray-500"># Rotation-Accumulate Unit</span></div>
                <div className="ml-4">├── <span className="text-amber-300">synaptic_array.sv</span> <span className="text-gray-500"># Parallel RAU array</span></div>
                <div className="ml-4">├── <span className="text-amber-300">weight_rom.sv</span> <span className="text-gray-500"># Mask-locked weights</span></div>
                <div className="ml-4">├── <span className="text-amber-300">kv_cache.sv</span> <span className="text-gray-500"># KV cache controller</span></div>
                <div className="ml-4">└── <span className="text-amber-300">top_level.sv</span> <span className="text-gray-500"># Inference engine</span></div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <a href="#" className="text-green-400 text-sm hover:underline flex items-center gap-1">
                View on GitHub <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>

          {/* Python SDK */}
          <div id="sdk" className="feature-card">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                <Package className="w-6 h-6 text-purple-400" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">Python SDK</h3>
                <span className="text-sm text-gray-500">pip install ternaryair</span>
              </div>
            </div>
            <p className="text-gray-400 text-sm mb-4">
              Full-featured Python SDK with device driver, simulator, streaming support, 
              and OpenAI-compatible interface.
            </p>
            <div className="code-block mb-4">
              <div className="code-content text-sm font-mono">
                <div className="text-gray-500"># Install via pip</div>
                <div><span className="text-green-400">$</span> pip install ternaryair</div>
                <br />
                <div className="text-gray-500"># Or from source</div>
                <div><span className="text-green-400">$</span> git clone https://github.com/superinstance/ternaryair</div>
                <div><span className="text-green-400">$</span> cd ternaryair && pip install -e .</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Link href="/developers" className="text-green-400 text-sm hover:underline">
                SDK Documentation →
              </Link>
            </div>
          </div>

          {/* REST API */}
          <div id="api" className="feature-card">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center">
                <Terminal className="w-6 h-6 text-blue-400" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">REST API Server</h3>
                <span className="text-sm text-gray-500">OpenAI-Compatible</span>
              </div>
            </div>
            <p className="text-gray-400 text-sm mb-4">
              Drop-in replacement for OpenAI API. Works with existing tools and libraries 
              that use the OpenAI SDK.
            </p>
            <div className="code-block mb-4">
              <div className="code-content text-sm font-mono">
                <div className="text-gray-500"># Start the server</div>
                <div><span className="text-green-400">$</span> ternaryair-server --port 8000</div>
                <br />
                <div className="text-gray-500"># Use with OpenAI SDK</div>
                <div><span className="text-purple-400">from</span> openai <span className="text-purple-400">import</span> OpenAI</div>
                <div>client = OpenAI(base_url=<span className="text-green-400">&quot;http://localhost:8000/v1&quot;</span>)</div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Link href="/developers#api" className="text-green-400 text-sm hover:underline">
                API Documentation →
              </Link>
            </div>
          </div>

          {/* Documentation */}
          <div id="docs" className="feature-card">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 rounded-xl bg-green-500/10 flex items-center justify-center">
                <FileText className="w-6 h-6 text-green-400" />
              </div>
              <div>
                <h3 className="text-xl font-semibold">Documentation</h3>
                <span className="text-sm text-gray-500">Complete Guides</span>
              </div>
            </div>
            <p className="text-gray-400 text-sm mb-4">
              Comprehensive documentation for users, developers, and hardware engineers. 
              Includes tutorials, API reference, and architecture guides.
            </p>
            <div className="code-block mb-4">
              <div className="code-content text-sm font-mono">
                <div className="text-gray-500">docs/</div>
                <div className="ml-4">├── <span className="text-blue-300">users/</span> <span className="text-gray-500"># User guides</span></div>
                <div className="ml-4">├── <span className="text-purple-300">developers/</span> <span className="text-gray-500"># API & SDK docs</span></div>
                <div className="ml-4">├── <span className="text-amber-300">engineers/</span> <span className="text-gray-500"># RTL & FPGA guides</span></div>
                <div className="ml-4">├── <span className="text-green-300">ARCHITECTURE.md</span></div>
                <div className="ml-4">└── <span className="text-green-300">SECURITY_MODEL.md</span></div>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <Link href="/learning" className="text-green-400 text-sm hover:underline">
                Learning Center →
              </Link>
            </div>
          </div>
        </div>

        {/* GitHub */}
        <div className="bg-[#0a0a0a] border border-gray-700 rounded-xl p-8 text-center">
          <Github className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">Prefer GitHub?</h3>
          <p className="text-gray-400 mb-4">
            Clone the repository directly from GitHub for the latest updates.
          </p>
          <div className="code-block max-w-md mx-auto mb-4">
            <div className="code-content text-sm font-mono text-center">
              git clone https://github.com/superinstance/ternaryair.git
            </div>
          </div>
          <a
            href="https://github.com/superinstance/ternaryair"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 text-green-400 hover:underline"
          >
            View on GitHub <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
}
