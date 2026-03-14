import Link from "next/link";
import {
  Cpu,
  Clock,
  Zap,
  AlertTriangle,
  CheckCircle,
  ArrowRight,
  Download,
  Play,
  Settings,
  BarChart3,
  Code,
  FileText,
} from "lucide-react";

export default function ProfessionalPage() {
  return (
    <div className="animated-bg min-h-screen pt-24 pb-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-green-500/10 border border-green-500/30 rounded-full px-5 py-2 mb-6">
            <Cpu className="w-4 h-4 text-green-400" />
            <span className="text-green-400 text-sm font-medium">Professional Grade Tools</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="gradient-text">Professional Timing Tools</span>
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto text-lg">
            Real-world FPGA and chip design tools for engineers. Timing closure, 
            CDC analysis, and pipeline optimization.
          </p>
        </div>

        {/* Tools Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-16">
          {/* FPGA Timing Closure Tool */}
          <div className="bg-dark-800/60 backdrop-blur-sm rounded-2xl border border-dark-600 overflow-hidden">
            <div className="p-6 border-b border-dark-600">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-green-500/10 flex items-center justify-center">
                  <Clock className="w-6 h-6 text-green-400" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold">Timing Closure Analyzer</h2>
                  <p className="text-gray-500 text-sm">Static timing analysis</p>
                </div>
              </div>
            </div>

            <div className="p-6">
              {/* Sample Timing Report */}
              <div className="code-block mb-6">
                <div className="code-header">
                  <div className="code-dot bg-red-500" />
                  <div className="code-dot bg-yellow-500" />
                  <div className="code-dot bg-green-500" />
                  <span className="ml-2 text-gray-400 text-sm">timing_report.txt</span>
                </div>
                <div className="code-content font-mono text-xs overflow-x-auto">
                  <pre className="text-gray-300">{`Timing Summary:
┌─────────────────────────────────────────────┐
│ Clock Domain    Target    Slack    Status   │
├─────────────────────────────────────────────┤
│ clk_sys         250 MHz   +2.032ns  ✅ MET  │
│ clk_memory      200 MHz   +1.456ns  ✅ MET  │
│ clk_display     150 MHz   -0.234ns  ❌ VIOL │
└─────────────────────────────────────────────┘

Worst Path (clk_display):
  Source:      pixel_counter[15]/CLK
  Destination: video_out[7]/D
  Data Delay:  6.89ns (target: 6.67ns)
  Suggestion:  Add pipeline stage or reduce logic`}</pre>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex flex-wrap gap-2">
                <button className="flex items-center gap-2 px-4 py-2 bg-green-500/10 text-green-400 rounded-lg text-sm hover:bg-green-500/20 transition-colors">
                  <Play className="w-4 h-4" />
                  Run Analysis
                </button>
                <button className="flex items-center gap-2 px-4 py-2 bg-dark-700 text-gray-300 rounded-lg text-sm hover:bg-dark-600 transition-colors">
                  <Settings className="w-4 h-4" />
                  Configure
                </button>
                <button className="flex items-center gap-2 px-4 py-2 bg-dark-700 text-gray-300 rounded-lg text-sm hover:bg-dark-600 transition-colors">
                  <Download className="w-4 h-4" />
                  Export
                </button>
              </div>
            </div>
          </div>

          {/* CDC Analysis Tool */}
          <div className="bg-dark-800/60 backdrop-blur-sm rounded-2xl border border-dark-600 overflow-hidden">
            <div className="p-6 border-b border-dark-600">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center">
                  <Zap className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold">CDC Analyzer</h2>
                  <p className="text-gray-500 text-sm">Clock domain crossing checker</p>
                </div>
              </div>
            </div>

            <div className="p-6">
              {/* CDC Visualization */}
              <div className="code-block mb-6">
                <div className="code-content font-mono text-xs overflow-x-auto">
                  <pre className="text-gray-300">{`Clock Domain Crossing Report:

Domain A (100MHz) ──▶ Domain B (200MHz)
┌───────────────┐     ┌───────────────┐
│   data_bus[7] │────▶│ 2-FF Sync     │ ✅ Safe
│   valid_flag  │────▶│ 2-FF Sync     │ ✅ Safe  
│   counter[3]  │────▶│ ⚠️ NO SYNC    │ ❌ Risk!
└───────────────┘     └───────────────┘

Recommendations:
  • counter[3]: Add synchronizer chain
  • Consider using async FIFO for buses`}</pre>
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-dark-700 rounded-lg p-3 text-center">
                  <div className="text-xl font-bold text-green-400">12</div>
                  <div className="text-gray-500 text-xs">Safe Crossings</div>
                </div>
                <div className="bg-dark-700 rounded-lg p-3 text-center">
                  <div className="text-xl font-bold text-amber-400">3</div>
                  <div className="text-gray-500 text-xs">Warnings</div>
                </div>
                <div className="bg-dark-700 rounded-lg p-3 text-center">
                  <div className="text-xl font-bold text-red-400">1</div>
                  <div className="text-gray-500 text-xs">Critical</div>
                </div>
              </div>

              <button className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-purple-500/10 text-purple-400 rounded-lg text-sm hover:bg-purple-500/20 transition-colors">
                View Full Report <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Pipeline Optimizer */}
          <div className="bg-dark-800/60 backdrop-blur-sm rounded-2xl border border-dark-600 overflow-hidden">
            <div className="p-6 border-b border-dark-600">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center">
                  <BarChart3 className="w-6 h-6 text-blue-400" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold">Pipeline Optimizer</h2>
                  <p className="text-gray-500 text-sm">Stage balancing tool</p>
                </div>
              </div>
            </div>

            <div className="p-6">
              {/* Pipeline Visualization */}
              <div className="mb-6">
                <div className="text-sm text-gray-400 mb-3">Pipeline Stage Distribution:</div>
                <div className="space-y-3">
                  {[
                    { stage: "Stage 1 (Fetch)", delay: 2.3, target: 4, status: "good" },
                    { stage: "Stage 2 (Decode)", delay: 5.8, target: 4, status: "bad" },
                    { stage: "Stage 3 (Execute)", delay: 3.9, target: 4, status: "good" },
                    { stage: "Stage 4 (Writeback)", delay: 1.2, target: 4, status: "good" },
                  ].map((item) => (
                    <div key={item.stage} className="flex items-center gap-3">
                      <div className="w-32 text-xs text-gray-400">{item.stage}</div>
                      <div className="flex-1 h-4 bg-dark-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            item.status === "good" ? "bg-green-500" : "bg-red-500"
                          }`}
                          style={{ width: `${(item.delay / 8) * 100}%` }}
                        />
                      </div>
                      <div className={`text-xs ${item.status === "good" ? "text-green-400" : "text-red-400"}`}>
                        {item.delay}ns
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3 mb-4">
                <div className="flex items-center gap-2 text-amber-400 text-sm">
                  <AlertTriangle className="w-4 h-4" />
                  <span className="font-medium">Optimization Suggestion</span>
                </div>
                <p className="text-gray-400 text-xs mt-1">
                  Stage 2 is the bottleneck. Consider splitting decode into 2 stages 
                  for 40% frequency improvement.
                </p>
              </div>

              <button className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-500/10 text-blue-400 rounded-lg text-sm hover:bg-blue-500/20 transition-colors">
                Auto-Optimize Pipeline <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Code Generator */}
          <div className="bg-dark-800/60 backdrop-blur-sm rounded-2xl border border-dark-600 overflow-hidden">
            <div className="p-6 border-b border-dark-600">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-amber-500/10 flex items-center justify-center">
                  <Code className="w-6 h-6 text-amber-400" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold">RTL Code Generator</h2>
                  <p className="text-gray-500 text-sm">Timing-optimized HDL</p>
                </div>
              </div>
            </div>

            <div className="p-6">
              <div className="code-block mb-6">
                <div className="code-header">
                  <div className="code-dot bg-red-500" />
                  <div className="code-dot bg-yellow-500" />
                  <div className="code-dot bg-green-500" />
                  <span className="ml-2 text-gray-400 text-sm">synchronizer.v</span>
                </div>
                <div className="code-content font-mono text-xs overflow-x-auto">
                  <pre className="text-gray-300">{`// Generated: 2-FF Synchronizer
// Optimized for: Xilinx 7-series

module synchronizer #(
  parameter WIDTH = 8
)(
  input  wire clk_dst,
  input  wire [WIDTH-1:0] data_in,
  output reg  [WIDTH-1:0] data_out
);

  (* ASYNC_REG = "TRUE" *)
  reg [WIDTH-1:0] sync_stage;

  always @(posedge clk_dst) begin
    sync_stage <= data_in;
    data_out   <= sync_stage;
  end

endmodule`}</pre>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                <button className="flex items-center gap-2 px-4 py-2 bg-amber-500/10 text-amber-400 rounded-lg text-sm hover:bg-amber-500/20 transition-colors">
                  <FileText className="w-4 h-4" />
                  Verilog
                </button>
                <button className="flex items-center gap-2 px-4 py-2 bg-dark-700 text-gray-300 rounded-lg text-sm hover:bg-dark-600 transition-colors">
                  <FileText className="w-4 h-4" />
                  VHDL
                </button>
                <button className="flex items-center gap-2 px-4 py-2 bg-dark-700 text-gray-300 rounded-lg text-sm hover:bg-dark-600 transition-colors">
                  <FileText className="w-4 h-4" />
                  SystemVerilog
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Feature List */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold mb-8">Professional Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { icon: Clock, title: "Timing Analysis", desc: "Complete STA reports" },
              { icon: Zap, title: "CDC Detection", desc: "Cross-domain safety" },
              { icon: BarChart3, title: "Pipeline Tuning", desc: "Stage optimization" },
              { icon: Code, title: "Code Generation", desc: "Optimized RTL output" },
              { icon: CheckCircle, title: "Constraint Help", desc: "SDC/XDC assist" },
              { icon: Settings, title: "Multi-Platform", desc: "Xilinx, Intel, Lattice" },
              { icon: Download, title: "Export Options", desc: "Reports & scripts" },
              { icon: Play, title: "Real-time", desc: "Live analysis view" },
            ].map((feature) => (
              <div key={feature.title} className="bg-dark-800/60 backdrop-blur-sm rounded-xl p-5 border border-dark-600">
                <feature.icon className="w-6 h-6 text-green-400 mb-3" />
                <h3 className="font-medium mb-1">{feature.title}</h3>
                <p className="text-gray-500 text-sm">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Navigation */}
        <div className="flex justify-center gap-4">
          <Link
            href="/timing-playground"
            className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-6 py-3 rounded-xl font-medium transition-colors"
          >
            ← Timing Playground
          </Link>
          <Link
            href="/about"
            className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-6 py-3 rounded-xl font-medium transition-all"
          >
            About the Project <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}
