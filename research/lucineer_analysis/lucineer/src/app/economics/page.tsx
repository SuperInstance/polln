"use client";

import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import Head from "next/head";
import Link from "next/link";
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  Users,
  Target,
  PieChart,
  BarChart3,
  Zap,
  Globe,
  AlertTriangle,
  Building2,
  Calculator,
  LineChart,
  Layers,
  Shield,
} from "lucide-react";

// Competitor Data
const competitors = [
  { name: "Taalas", funding: 169, focus: "Data Center", power: "200W+", tokens: "14,000/s", threat: "low" },
  { name: "Quadric", funding: 72, focus: "Edge LLM IP", power: "5-10W", tokens: "Variable", threat: "high" },
  { name: "Hailo", funding: 340, focus: "Vision AI", power: "2.5W", tokens: "Limited LLM", threat: "medium" },
  { name: "Axelera", funding: 250, focus: "Edge GenAI", power: "10W", tokens: "214 TOPS", threat: "high" },
  { name: "Lucineer (Us)", funding: 0.5, focus: "Mask-Locked Edge", power: "2-5W", tokens: "25-35/s", threat: "none" },
];

// Customer Segments
const customerSegments = [
  { name: "DIY/Makers", size: 500000, price: 35, growth: 0.15, color: "from-green-500 to-emerald-600" },
  { name: "Education", size: 150000, price: 50, growth: 0.20, color: "from-blue-500 to-cyan-600" },
  { name: "Industrial IoT", size: 50000, price: 89, growth: 0.25, color: "from-purple-500 to-violet-600" },
  { name: "Consumer Devices", size: 2000000, price: 25, growth: 0.30, color: "from-amber-500 to-orange-600" },
  { name: "Enterprise", size: 10000, price: 150, growth: 0.10, color: "from-red-500 to-rose-600" },
];

// Supply Chain Risks
const supplyChainRisks = [
  { component: "LPDDR4 Memory", risk: "High", price: 12, trend: "up", alternative: "Wait for LPDDR5" },
  { component: "TSMC 28nm Capacity", risk: "Medium", price: 3000, trend: "stable", alternative: "GSMC backup" },
  { component: "Packaging (QFN)", risk: "Low", price: 3, trend: "down", alternative: "Multiple sources" },
  { component: "Test Equipment", risk: "Low", price: 5, trend: "stable", alternative: "In-house ATE" },
];

// TCO Calculator Component
function TCOCalculator() {
  const [years, setYears] = useState(3);
  const [queries, setQueries] = useState(1000000);
  const [cloudPrice, setCloudPrice] = useState(0.0001);

  const cloudCost = queries * cloudPrice * 365 * years;
  const luciCost = 55 + (years * 5); // Hardware + power
  const savings = cloudCost - luciCost;
  const roi = (savings / luciCost) * 100;

  return (
    <div className="bg-card rounded-2xl border border-border p-6">
      <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <Calculator className="w-5 h-5 text-emerald-400" />
        Total Cost of Ownership
      </h3>
      
      <div className="space-y-4">
        <div>
          <label className="text-sm text-muted-foreground">Years of Operation: {years}</label>
          <input
            type="range"
            min="1"
            max="10"
            value={years}
            onChange={(e) => setYears(Number(e.target.value))}
            className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer"
          />
        </div>

        <div>
          <label className="text-sm text-muted-foreground">Queries/Day: {queries.toLocaleString()}</label>
          <input
            type="range"
            min="10000"
            max="10000000"
            step="10000"
            value={queries}
            onChange={(e) => setQueries(Number(e.target.value))}
            className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer"
          />
        </div>

        <div>
          <label className="text-sm text-muted-foreground">Cloud API Price/Query: ${cloudPrice.toFixed(4)}</label>
          <input
            type="range"
            min="0.00001"
            max="0.001"
            step="0.00001"
            value={cloudPrice}
            onChange={(e) => setCloudPrice(Number(e.target.value))}
            className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer"
          />
        </div>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="bg-red-500/10 rounded-xl p-4 text-center border border-red-500/30">
          <div className="text-2xl font-bold text-red-400">${cloudCost.toLocaleString()}</div>
          <div className="text-xs text-muted-foreground">Cloud API ({years} years)</div>
        </div>
        <div className="bg-emerald-500/10 rounded-xl p-4 text-center border border-emerald-500/30">
          <div className="text-2xl font-bold text-emerald-400">${luciCost.toLocaleString()}</div>
          <div className="text-xs text-muted-foreground">LUCI-3 Hardware</div>
        </div>
        <div className="col-span-2 bg-gradient-to-r from-emerald-500/20 to-cyan-400/20 rounded-xl p-4 text-center border border-emerald-500/40">
          <div className="text-3xl font-bold text-emerald-400">{roi > 0 ? roi.toFixed(0) + "%" : "0%"}</div>
          <div className="text-sm text-muted-foreground">ROI vs Cloud</div>
          <div className="text-xs text-muted-foreground mt-1">Saves ${savings.toLocaleString()} over {years} years</div>
        </div>
      </div>
    </div>
  );
}

// Competitive Matrix Component
function CompetitiveMatrix() {
  return (
    <div className="bg-card rounded-2xl border border-border p-6">
      <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <Target className="w-5 h-5 text-purple-400" />
        Competitive Positioning
      </h3>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left py-2">Company</th>
              <th className="text-left py-2">Focus</th>
              <th className="text-right py-2">Funding ($M)</th>
              <th className="text-right py-2">Power</th>
              <th className="text-center py-2">Threat</th>
            </tr>
          </thead>
          <tbody>
            {competitors.map((c, i) => (
              <tr key={i} className={`border-b border-border/50 ${c.name === "Lucineer (Us)" ? "bg-emerald-500/10" : ""}`}>
                <td className="py-3 font-medium">{c.name}</td>
                <td className="py-3 text-muted-foreground">{c.focus}</td>
                <td className="py-3 text-right font-mono">${c.funding}</td>
                <td className="py-3 text-right font-mono">{c.power}</td>
                <td className="py-3 text-center">
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    c.threat === "high" ? "bg-red-500/20 text-red-400" :
                    c.threat === "medium" ? "bg-amber-500/20 text-amber-400" :
                    c.threat === "low" ? "bg-green-500/20 text-green-400" :
                    "bg-cyan-500/20 text-cyan-400"
                  }`}>
                    {c.threat === "none" ? "Us" : c.threat}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// Market Segment Visualization
function MarketSegments() {
  const totalMarket = customerSegments.reduce((sum, s) => sum + s.size * s.price * s.growth, 0);

  return (
    <div className="bg-card rounded-2xl border border-border p-6">
      <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <PieChart className="w-5 h-5 text-cyan-400" />
        Target Market Segments
      </h3>

      <div className="space-y-4">
        {customerSegments.map((segment, i) => {
          const segmentValue = segment.size * segment.price * segment.growth;
          const percentage = (segmentValue / totalMarket) * 100;

          return (
            <div key={i} className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="font-medium">{segment.name}</span>
                <div className="text-right">
                  <span className="text-sm text-muted-foreground">${segment.price}/unit</span>
                  <span className="ml-2 text-xs text-emerald-400">+{(segment.growth * 100).toFixed(0)}%</span>
                </div>
              </div>
              <div className="h-3 bg-muted rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${percentage}%` }}
                  transition={{ delay: i * 0.1, duration: 0.5 }}
                  className={`h-full bg-gradient-to-r ${segment.color} rounded-full`}
                />
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>{segment.size.toLocaleString()} customers</span>
                <span>{percentage.toFixed(1)}% of weighted market</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6 p-4 bg-emerald-500/10 rounded-xl border border-emerald-500/20">
        <div className="text-center">
          <div className="text-3xl font-bold text-emerald-400">
            ${(totalMarket / 1000000).toFixed(1)}M
          </div>
          <div className="text-sm text-muted-foreground">Weighted Market Opportunity</div>
        </div>
      </div>
    </div>
  );
}

// Supply Chain Risk Matrix
function SupplyChainRisk() {
  return (
    <div className="bg-card rounded-2xl border border-border p-6">
      <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <AlertTriangle className="w-5 h-5 text-amber-400" />
        Supply Chain Risk Matrix
      </h3>

      <div className="space-y-4">
        {supplyChainRisks.map((item, i) => (
          <div key={i} className="p-4 bg-muted rounded-xl">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">{item.component}</span>
              <span className={`px-2 py-1 rounded-full text-xs ${
                item.risk === "High" ? "bg-red-500/20 text-red-400" :
                item.risk === "Medium" ? "bg-amber-500/20 text-amber-400" :
                "bg-green-500/20 text-green-400"
              }`}>
                {item.risk} Risk
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Est. Cost: ${item.price}</span>
              <span className={`flex items-center gap-1 ${
                item.trend === "up" ? "text-red-400" :
                item.trend === "down" ? "text-green-400" :
                "text-muted-foreground"
              }`}>
                {item.trend === "up" && <TrendingUp className="w-4 h-4" />}
                {item.trend === "down" && <TrendingDown className="w-4 h-4" />}
                {item.trend === "stable" && "→"}
                {item.trend}
              </span>
            </div>
            <div className="mt-2 text-xs text-muted-foreground">
              Alternative: {item.alternative}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// Break-Even Calculator
function BreakEvenCalculator() {
  const [fixedCosts, setFixedCosts] = useState(3000000);
  const [variableCost, setVariableCost] = useState(28);
  const [price, setPrice] = useState(55);

  const breakEven = Math.ceil(fixedCosts / (price - variableCost));
  const contributionMargin = ((price - variableCost) / price * 100).toFixed(1);

  return (
    <div className="bg-card rounded-2xl border border-border p-6">
      <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <LineChart className="w-5 h-5 text-blue-400" />
        Break-Even Analysis
      </h3>

      <div className="space-y-4">
        <div>
          <label className="text-sm text-muted-foreground">Fixed Costs (NRE): ${(fixedCosts / 1000000).toFixed(1)}M</label>
          <input
            type="range"
            min="500000"
            max="10000000"
            step="100000"
            value={fixedCosts}
            onChange={(e) => setFixedCosts(Number(e.target.value))}
            className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer"
          />
        </div>

        <div>
          <label className="text-sm text-muted-foreground">Variable Cost: ${variableCost}</label>
          <input
            type="range"
            min="15"
            max="50"
            value={variableCost}
            onChange={(e) => setVariableCost(Number(e.target.value))}
            className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer"
          />
        </div>

        <div>
          <label className="text-sm text-muted-foreground">Price: ${price}</label>
          <input
            type="range"
            min="35"
            max="150"
            value={price}
            onChange={(e) => setPrice(Number(e.target.value))}
            className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer"
          />
        </div>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="bg-blue-500/10 rounded-xl p-4 text-center border border-blue-500/30">
          <div className="text-3xl font-bold text-blue-400">{breakEven.toLocaleString()}</div>
          <div className="text-xs text-muted-foreground">Units to Break Even</div>
        </div>
        <div className="bg-purple-500/10 rounded-xl p-4 text-center border border-purple-500/30">
          <div className="text-3xl font-bold text-purple-400">{contributionMargin}%</div>
          <div className="text-xs text-muted-foreground">Contribution Margin</div>
        </div>
      </div>

      <div className="mt-4 p-3 bg-black/20 rounded-lg">
        <code className="text-xs text-muted-foreground">
          BE = FC / (P - VC) = ${fixedCosts.toLocaleString()} / (${price} - ${variableCost}) = {breakEven.toLocaleString()} units
        </code>
      </div>
    </div>
  );
}

export default function EconomicsPage() {
  return (
    <>
      <Head>
        <title>Economics | Lucineer - Market Intelligence</title>
        <meta name="description" content="Market simulation, competitive positioning, and economic analysis for mask-locked inference chips" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-background via-background to-purple-500/5 pt-20">
        <section className="py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center mb-12"
            >
              <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/30 rounded-full px-4 py-2 mb-6">
                <DollarSign className="w-4 h-4 text-purple-400" />
                <span className="text-purple-400 text-sm font-medium">Market Intelligence</span>
              </div>

              <h1 className="text-4xl sm:text-5xl font-bold mb-4">
                <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-emerald-400 bg-clip-text text-transparent">
                  Economic Simulation Engine
                </span>
              </h1>

              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Model pricing, competition, and market dynamics for mask-locked inference chips
              </p>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <TCOCalculator />
              <CompetitiveMatrix />
              <MarketSegments />
              <SupplyChainRisk />
              <BreakEvenCalculator />

              {/* Strategy Summary */}
              <div className="bg-gradient-to-br from-emerald-500/10 via-cyan-400/10 to-purple-500/10 rounded-2xl border border-emerald-500/20 p-6">
                <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-emerald-400" />
                  Strategic Position
                </h3>

                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-emerald-500/20 flex items-center justify-center flex-shrink-0">
                      <Shield className="w-4 h-4 text-emerald-400" />
                    </div>
                    <div>
                      <h4 className="font-medium">First-Mover in Sub-$50 Edge LLM</h4>
                      <p className="text-sm text-muted-foreground">No competitor targets the $25-60 price point for 3B+ parameter inference</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                      <Layers className="w-4 h-4 text-cyan-400" />
                    </div>
                    <div>
                      <h4 className="font-medium">Mask-Locked Moat</h4>
                      <p className="text-sm text-muted-foreground">Hardware instantiation creates unique differentiation vs programmable chips</p>
                    </div>
                  </div>

                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center flex-shrink-0">
                      <Globe className="w-4 h-4 text-purple-400" />
                    </div>
                    <div>
                      <h4 className="font-medium">18-Month Window</h4>
                      <p className="text-sm text-muted-foreground">Taalas focused on data center, Quadric still building. Time to establish edge presence.</p>
                    </div>
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-border">
                  <Link
                    href="/manufacturing"
                    className="flex items-center justify-center gap-2 w-full py-3 rounded-xl bg-emerald-500/10 text-emerald-400 font-medium hover:bg-emerald-500/20 transition-colors"
                  >
                    <Building2 className="w-4 h-4" />
                    View Manufacturing Process
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </>
  );
}
