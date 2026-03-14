import Link from "next/link";
import {
  Download,
  Package,
  FileCode,
  HardDrive,
  Terminal,
  FileText,
  Cpu,
  CpuIcon,
  Zap,
  ExternalLink,
  Copy,
  CheckCircle,
} from "lucide-react";

const downloadCategories = [
  {
    title: "Source Code",
    icon: Package,
    items: [
      {
        name: "Full Repository",
        description: "Complete source including RTL, SDK, documentation, and examples",
        size: "~10 MB",
        format: "ZIP",
        url: "https://github.com/superinstance/ternaryair/archive/refs/heads/main.zip",
        primary: true,
      },
      {
        name: "Python SDK Source",
        description: "Python SDK source code for custom builds",
        size: "~200 KB",
        format: "GitHub",
        url: "https://github.com/superinstance/ternaryair/tree/main/software/sdk",
      },
      {
        name: "RTL Source",
        description: "SystemVerilog hardware design files",
        size: "~100 KB",
        format: "GitHub",
        url: "https://github.com/superinstance/ternaryair/tree/main/hardware/rtl",
      },
    ],
  },
  {
    title: "Python Packages",
    icon: Terminal,
    items: [
      {
        name: "TernaryAir SDK",
        description: "Main Python package with simulator",
        size: "~500 KB",
        format: "PyPI",
        command: "pip install ternaryair",
        url: "https://pypi.org/project/ternaryair/",
      },
      {
        name: "Development Build",
        description: "All development dependencies included",
        size: "~5 MB",
        format: "PyPI",
        command: 'pip install "ternaryair[dev]"',
      },
      {
        name: "Server Extension",
        description: "REST API server (FastAPI)",
        size: "~1 MB",
        format: "PyPI",
        command: 'pip install "ternaryair[server]"',
      },
    ],
  },
  {
    title: "FPGA Bitstreams",
    icon: Cpu,
    items: [
      {
        name: "PYNQ-Z2 Bitstream",
        description: "Pre-built bitstream for Xilinx PYNQ-Z2 board",
        size: "~3 MB",
        format: "BIT",
        url: "https://github.com/superinstance/ternaryair/releases/download/v1.0.0/ternaryair-pynqz2.bit",
      },
      {
        name: "Arty A7 Bitstream",
        description: "Pre-built bitstream for Digilent Arty A7",
        size: "~3 MB",
        format: "BIT",
        url: "https://github.com/superinstance/ternaryair/releases/download/v1.0.0/ternaryair-artya7.bit",
      },
    ],
  },
  {
    title: "Documentation",
    icon: FileText,
    items: [
      {
        name: "Complete Documentation PDF",
        description: "All documentation in a single PDF file",
        size: "~2 MB",
        format: "PDF",
        url: "/docs/ternaryair-docs.pdf",
      },
      {
        name: "Security Whitepaper",
        description: "Threat model and security analysis",
        size: "~500 KB",
        format: "PDF",
        url: "/docs/ternaryair-security.pdf",
      },
      {
        name: "Architecture Guide",
        description: "Hardware and software architecture overview",
        size: "~1 MB",
        format: "PDF",
        url: "/docs/ternaryair-architecture.pdf",
      },
    ],
  },
  {
    title: "Pre-trained Models",
    icon: Zap,
    items: [
      {
        name: "BitNet-125M-Ternary",
        description: "125M parameter model, optimized for speed",
        size: "~40 MB",
        format: "BIN",
        url: "https://github.com/superinstance/ternaryair/releases/download/v1.0.0/bitnet-125m-ternary.bin",
      },
      {
        name: "BitNet-350M-Ternary",
        description: "350M parameter model, balanced performance",
        size: "~120 MB",
        format: "BIN",
        url: "https://github.com/superinstance/ternaryair/releases/download/v1.0.0/bitnet-350m-ternary.bin",
      },
    ],
  },
];

export default function DownloadPage() {
  return (
    <div className="animated-bg min-h-screen pt-20">
      {/* Hero */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl sm:text-5xl font-bold mb-6">
              <span className="gradient-text">Download Center</span>
            </h1>
            <p className="text-xl text-gray-300 mb-4 max-w-3xl mx-auto">
              Everything you need to use, develop, and build with TernaryAir
            </p>
            <p className="text-gray-400 max-w-2xl mx-auto">
              All free and open source under MIT license. No restrictions.
            </p>
          </div>

          {/* Quick Download */}
          <div className="max-w-4xl mx-auto mb-16">
            <div className="bg-gradient-to-br from-primary-500/20 to-primary-700/10 border border-primary-500/30 rounded-2xl p-8">
              <div className="flex flex-col md:flex-row items-center justify-between gap-6">
                <div className="text-center md:text-left">
                  <h2 className="text-2xl font-bold mb-2">Get Everything at Once</h2>
                  <p className="text-gray-400">
                    Complete repository with all source code, documentation, and examples.
                  </p>
                </div>
                <a
                  href="https://github.com/superinstance/ternaryair/archive/refs/heads/main.zip"
                  className="inline-flex items-center gap-3 px-8 py-4 rounded-xl bg-primary-600 hover:bg-primary-500 text-white font-semibold text-lg transition-all glow-green"
                >
                  <Download className="w-5 h-5" />
                  Download Full Repository
                  <span className="text-sm opacity-75">(~10 MB)</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Download Categories */}
      <section className="py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {downloadCategories.map((category) => (
            <div key={category.title} className="mb-12">
              <div className="flex items-center gap-3 mb-6">
                <category.icon className="w-6 h-6 text-primary-400" />
                <h2 className="text-2xl font-bold">{category.title}</h2>
              </div>

              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {category.items.map((item) => (
                  <a
                    key={item.name}
                    href={item.url}
                    target={item.url.startsWith("http") ? "_blank" : undefined}
                    rel={item.url.startsWith("http") ? "noopener noreferrer" : undefined}
                    className={`group p-6 rounded-xl border transition-all ${
                      item.primary
                        ? "bg-white/10 border-white/20 hover:border-white/40"
                        : "bg-dark-800 border-dark-600 hover:border-dark-400"
                    }`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <h3 className="font-semibold group-hover:text-primary-400 transition-colors">
                        {item.name}
                      </h3>
                      <span className="text-xs px-2 py-1 rounded bg-dark-600 text-gray-400">
                        {item.format}
                      </span>
                    </div>
                    <p className="text-sm text-gray-400 mb-4">{item.description}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">{item.size}</span>
                      <span className="text-sm text-primary-400 group-hover:translate-x-1 transition-transform">
                        {item.url.startsWith("http") ? (
                          <span className="flex items-center gap-1">
                            Download <ExternalLink className="w-3 h-3" />
                          </span>
                        ) : (
                          "Download →"
                        )}
                      </span>
                    </div>
                    {item.command && (
                      <div className="mt-4 p-3 rounded bg-dark-700 border border-dark-500">
                        <code className="text-xs text-green-400 font-mono">
                          $ {item.command}
                        </code>
                      </div>
                    )}
                  </a>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Version Info */}
      <section className="py-8 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-dark-800 rounded-xl p-6 border border-dark-600">
            <h3 className="font-semibold mb-4">Version Information</h3>
            <div className="grid md:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Latest Release:</span>
                <span className="ml-2 text-primary-400 font-mono">v1.0.0</span>
              </div>
              <div>
                <span className="text-gray-500">Release Date:</span>
                <span className="ml-2">March 8, 2026</span>
              </div>
              <div>
                <span className="text-gray-500">License:</span>
                <span className="ml-2">MIT</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* GitHub CTA */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-gray-400 mb-6">
            Prefer to browse before downloading?
          </p>
          <a
            href="https://github.com/superinstance/ternaryair"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-3 text-primary-400 hover:text-primary-300 transition-colors text-lg"
          >
            <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z" />
            </svg>
            View on GitHub →
          </a>
        </div>
      </section>
    </div>
  );
}
