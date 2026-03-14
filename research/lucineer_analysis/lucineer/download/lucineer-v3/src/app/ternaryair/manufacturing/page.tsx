"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Cpu, Layers, Box, Zap, ArrowRight, ChevronRight,
  Play, Pause, RotateCcw, Download, Share2, Settings,
  Check, AlertTriangle, Info, Clock, DollarSign,
  Rocket, Factory, FileCode, Ship, Package, TestTube,
  Calendar, Users, Globe, Shield
} from "lucide-react";

// Manufacturing pathways
const pathways = [
  {
    id: "tinytapeout",
    name: "TinyTapeout",
    description: "Affordable chip prototyping for hobbyists and students",
    price: "$100 - $500",
    timeline: "3-4 months",
    minOrder: 1,
    technology: "SKY130 (130nm)",
    area: "1mm² - 10mm²",
    features: ["Open-source PDK", "Educational focus", "Community support", "Shared shuttle"],
    ideal: "First-time designers, students, hobbyists",
    icon: "🎓",
    color: "#3b82f6",
  },
  {
    id: "mpw",
    name: "MPW Shuttle",
    description: "Multi-Project Wafer service for small production runs",
    price: "$5,000 - $50,000",
    timeline: "6-12 months",
    minOrder: 10,
    technology: "28nm - 180nm",
    area: "10mm² - 100mm²",
    features: ["Dedicated engineering", "GDSII submission", "Packaging options", "Testing support"],
    ideal: "Startups, research labs, small products",
    icon: "🔬",
    color: "#8b5cf6",
  },
  {
    id: "full",
    name: "Full Tapeout",
    description: "Production-ready manufacturing for volume orders",
    price: "$100,000+",
    timeline: "12-18 months",
    minOrder: 10000,
    technology: "7nm - 28nm",
    area: "50mm² - 500mm²",
    features: ["Dedicated masks", "Production quality", "Full QA/Testing", "Custom packaging"],
    ideal: "Companies, products going to market",
    icon: "🏭",
    color: "#22c55e",
  },
];

// Manufacturing timeline phases
const phases = [
  {
    id: 1,
    name: "Design Review",
    duration: "2-4 weeks",
    description: "Submit your design for feasibility review",
    steps: ["Upload GDSII", "DRC/LVS check", "Timing analysis", "Power analysis"],
    deliverable: "Approved design package",
  },
  {
    id: 2,
    name: "Mask Generation",
    duration: "4-6 weeks",
    description: "Photomasks created from your design",
    steps: ["Data preparation", "Mask writing", "Inspection", "Repair"],
    deliverable: "Mask set ready",
  },
  {
    id: 3,
    name: "Fabrication",
    duration: "8-12 weeks",
    description: "Wafers processed in cleanroom",
    steps: ["Wafer start", "Layer deposition", "Patterning", "Metallization"],
    deliverable: "Processed wafers",
  },
  {
    id: 4,
    name: "Packaging",
    duration: "2-4 weeks",
    description: "Dice and package your chips",
    steps: ["Wafer probe", "Dicing", "Die attach", "Wire bonding"],
    deliverable: "Packaged chips",
  },
  {
    id: 5,
    name: "Testing",
    duration: "1-2 weeks",
    description: "Functional and quality testing",
    steps: ["Electrical test", "Functional test", "Burn-in", "Quality inspection"],
    deliverable: "Qualified chips",
  },
  {
    id: 6,
    name: "Delivery",
    duration: "1 week",
    description: "Shipping to your location",
    steps: ["Packaging", "Documentation", "Shipping", "Tracking"],
    deliverable: "Your chips arrive!",
  },
];

// Cost calculator
function CostCalculator() {
  const [pathway, setPathway] = useState("tinytapeout");
  const [quantity, setQuantity] = useState(1);
  const [packaging, setPackaging] = useState("qfn");
  const [testing, setTesting] = useState("basic");

  const baseCosts = {
    tinytapeout: 250,
    mpw: 15000,
    full: 150000,
  };

  const packagingCosts = {
    none: 0,
    qfn: 50,
    bga: 150,
    custom: 500,
  };

  const testingCosts = {
    none: 0,
    basic: 25,
    extended: 100,
    full: 500,
  };

  const totalCost = baseCosts[pathway as keyof typeof baseCosts] +
    packagingCosts[packaging as keyof typeof packagingCosts] * quantity +
    testingCosts[testing as keyof typeof testingCosts] * quantity;

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50">
        <div className="flex items-center gap-3">
          <DollarSign className="w-5 h-5 text-green-400" />
          <span className="font-semibold">Cost Estimator</span>
        </div>
      </div>

      <div className="p-6">
        {/* Pathway Selection */}
        <div className="mb-6">
          <label className="text-sm text-gray-400 mb-2 block">Manufacturing Pathway</label>
          <div className="grid grid-cols-3 gap-2">
            {pathways.map((p) => (
              <button
                key={p.id}
                onClick={() => setPathway(p.id)}
                className={`p-3 rounded-xl text-sm transition-all ${
                  pathway === p.id
                    ? "bg-green-500/20 text-green-400 border border-green-500/30"
                    : "bg-dark-700/50 text-gray-400 border border-dark-600"
                }`}
              >
                <div className="text-lg mb-1">{p.icon}</div>
                <div className="font-medium">{p.name}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Quantity */}
        <div className="mb-6">
          <div className="flex justify-between mb-2">
            <span className="text-sm text-gray-400">Quantity</span>
            <span className="text-sm font-mono text-blue-400">{quantity}</span>
          </div>
          <input
            type="range"
            min="1"
            max="pathway === 'tinytapeout' ? 10 : pathway === 'mpw' ? 1000 : 100000"
            value={quantity}
            onChange={(e) => setQuantity(parseInt(e.target.value))}
            className="w-full accent-blue-500"
          />
        </div>

        {/* Packaging */}
        <div className="mb-6">
          <label className="text-sm text-gray-400 mb-2 block">Packaging Type</label>
          <div className="grid grid-cols-4 gap-2">
            {[
              { id: "none", label: "Bare Die" },
              { id: "qfn", label: "QFN" },
              { id: "bga", label: "BGA" },
              { id: "custom", label: "Custom" },
            ].map((pkg) => (
              <button
                key={pkg.id}
                onClick={() => setPackaging(pkg.id)}
                className={`py-2 rounded-lg text-xs transition-all ${
                  packaging === pkg.id
                    ? "bg-purple-500/20 text-purple-400 border border-purple-500/30"
                    : "bg-dark-700/50 text-gray-400 border border-dark-600"
                }`}
              >
                {pkg.label}
              </button>
            ))}
          </div>
        </div>

        {/* Testing */}
        <div className="mb-6">
          <label className="text-sm text-gray-400 mb-2 block">Testing Level</label>
          <div className="grid grid-cols-4 gap-2">
            {[
              { id: "none", label: "None" },
              { id: "basic", label: "Basic" },
              { id: "extended", label: "Extended" },
              { id: "full", label: "Full QA" },
            ].map((test) => (
              <button
                key={test.id}
                onClick={() => setTesting(test.id)}
                className={`py-2 rounded-lg text-xs transition-all ${
                  testing === test.id
                    ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                    : "bg-dark-700/50 text-gray-400 border border-dark-600"
                }`}
              >
                {test.label}
              </button>
            ))}
          </div>
        </div>

        {/* Total Cost */}
        <div className="bg-gradient-to-r from-green-900/30 to-emerald-900/30 rounded-xl p-4 text-center border border-green-500/30">
          <span className="text-sm text-gray-400">Estimated Total Cost</span>
          <div className="text-4xl font-bold font-mono text-green-400 mt-1">
            ${totalCost.toLocaleString()}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Actual costs may vary based on design complexity
          </p>
        </div>
      </div>
    </div>
  );
}

// Timeline Visualizer
function TimelineVisualizer() {
  const [activePhase, setActivePhase] = useState(0);

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50">
        <div className="flex items-center gap-3">
          <Calendar className="w-5 h-5 text-blue-400" />
          <span className="font-semibold">Manufacturing Timeline</span>
        </div>
      </div>

      <div className="p-6">
        {/* Phase Indicators */}
        <div className="flex items-center justify-between mb-6">
          {phases.map((phase, index) => (
            <button
              key={phase.id}
              onClick={() => setActivePhase(index)}
              className={`flex flex-col items-center ${
                index <= activePhase ? "text-green-400" : "text-gray-500"
              }`}
            >
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center mb-2 transition-all ${
                  index < activePhase
                    ? "bg-green-500"
                    : index === activePhase
                    ? "bg-green-500/20 border-2 border-green-500"
                    : "bg-dark-700"
                }`}
              >
                {index < activePhase ? (
                  <Check className="w-4 h-4 text-white" />
                ) : (
                  <span className="text-sm">{index + 1}</span>
                )}
              </div>
              <span className="text-xs hidden md:block">{phase.name}</span>
            </button>
          ))}
        </div>

        {/* Progress Bar */}
        <div className="h-2 bg-dark-700 rounded-full mb-6 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full transition-all"
            style={{ width: `${((activePhase + 1) / phases.length) * 100}%` }}
          />
        </div>

        {/* Active Phase Details */}
        <div className="bg-dark-700/50 rounded-xl p-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold">{phases[activePhase].name}</h4>
            <span className="text-sm text-blue-400">{phases[activePhase].duration}</span>
          </div>
          <p className="text-sm text-gray-400 mb-4">{phases[activePhase].description}</p>

          <div className="grid grid-cols-2 gap-2">
            {phases[activePhase].steps.map((step) => (
              <div
                key={step}
                className="flex items-center gap-2 text-sm text-gray-400"
              >
                <ChevronRight className="w-4 h-4 text-green-400" />
                {step}
              </div>
            ))}
          </div>

          <div className="mt-4 pt-4 border-t border-dark-600">
            <span className="text-xs text-gray-500">Deliverable:</span>
            <span className="text-sm text-green-400 ml-2">
              {phases[activePhase].deliverable}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

// Partner Foundries
function PartnerFoundries() {
  const foundries = [
    { name: "SkyWater", technology: "SKY130", location: "USA", ideal: "Open-source" },
    { name: "GlobalFoundries", technology: "22FDX", location: "USA/EU", ideal: "Low power" },
    { name: "TSMC", technology: "28nm+", location: "Taiwan", ideal: "High volume" },
    { name: "Samsung", technology: "28nm+", location: "Korea", ideal: "Advanced nodes" },
  ];

  return (
    <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
      <div className="p-4 border-b border-dark-600 bg-dark-700/50">
        <div className="flex items-center gap-3">
          <Factory className="w-5 h-5 text-amber-400" />
          <span className="font-semibold">Partner Foundries</span>
        </div>
      </div>

      <div className="p-4">
        <div className="grid grid-cols-2 gap-3">
          {foundries.map((foundry) => (
            <div
              key={foundry.name}
              className="p-3 rounded-xl bg-dark-700/50 border border-dark-600"
            >
              <div className="font-medium">{foundry.name}</div>
              <div className="text-xs text-gray-500 mt-1">{foundry.technology}</div>
              <div className="flex items-center gap-2 mt-2 text-xs text-gray-400">
                <Globe className="w-3 h-3" />
                {foundry.location}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function ManufacturingPage() {
  return (
    <div className="animated-bg min-h-screen pt-24 pb-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/ternaryair"
            className="flex items-center gap-2 text-gray-400 hover:text-white text-sm mb-4"
          >
            <ChevronRight className="w-4 h-4 rotate-180" />
            Back to TernaryAir
          </Link>

          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 flex items-center justify-center">
              <Factory className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold">Manufacturing Pathway</h1>
              <p className="text-sm text-gray-500">From design to silicon</p>
            </div>
          </div>

          <p className="text-lg text-gray-300 max-w-3xl">
            Turn your TernaryAir design into real silicon. We connect hobbyists with affordable 
            prototyping services and help scale to production when ready.
          </p>
        </div>

        {/* Pathway Selection */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Choose Your Path</h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {pathways.map((pathway) => (
              <div
                key={pathway.id}
                className="bg-dark-800/80 backdrop-blur-lg rounded-2xl border border-dark-600 overflow-hidden hover:border-green-500/30 transition-all"
              >
                <div
                  className="h-2"
                  style={{ background: pathway.color }}
                />
                <div className="p-6">
                  <div className="text-4xl mb-4">{pathway.icon}</div>
                  <h3 className="text-xl font-bold mb-2">{pathway.name}</h3>
                  <p className="text-sm text-gray-400 mb-4">{pathway.description}</p>

                  <div className="space-y-2 text-sm mb-4">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Price Range</span>
                      <span className="text-green-400 font-mono">{pathway.price}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Timeline</span>
                      <span className="text-blue-400">{pathway.timeline}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Min Order</span>
                      <span className="text-purple-400">{pathway.minOrder}+</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Technology</span>
                      <span className="text-amber-400">{pathway.technology}</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1 mb-4">
                    {pathway.features.map((feature) => (
                      <span
                        key={feature}
                        className="px-2 py-0.5 rounded-full bg-dark-700/50 text-xs text-gray-400"
                      >
                        {feature}
                      </span>
                    ))}
                  </div>

                  <div className="pt-4 border-t border-dark-600">
                    <div className="text-xs text-gray-500 mb-2">Ideal for:</div>
                    <div className="text-sm text-gray-300">{pathway.ideal}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Cost Calculator & Timeline */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
          <CostCalculator />
          <TimelineVisualizer />
        </div>

        {/* Partner Foundries */}
        <section className="mb-12">
          <PartnerFoundries />
        </section>

        {/* Getting Started Checklist */}
        <section className="mb-12">
          <div className="bg-dark-800/80 rounded-2xl border border-dark-600 overflow-hidden">
            <div className="p-4 border-b border-dark-600 bg-dark-700/50">
              <div className="flex items-center gap-3">
                <Check className="w-5 h-5 text-green-400" />
                <span className="font-semibold">Manufacturing Readiness Checklist</span>
              </div>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { item: "Design reviewed and validated", status: "required" },
                  { item: "GDSII file exported", status: "required" },
                  { item: "DRC/LVS checks passed", status: "required" },
                  { item: "Timing analysis complete", status: "recommended" },
                  { item: "Power analysis done", status: "recommended" },
                  { item: "Test plan documented", status: "recommended" },
                  { item: "Packaging requirements defined", status: "optional" },
                  { item: "IP licensing verified", status: "optional" },
                ].map((check, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-3 p-3 rounded-xl bg-dark-700/50"
                  >
                    <div
                      className={`w-5 h-5 rounded-full flex items-center justify-center ${
                        check.status === "required"
                          ? "bg-red-500/20 text-red-400 border border-red-500/30"
                          : check.status === "recommended"
                          ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                          : "bg-green-500/20 text-green-400 border border-green-500/30"
                      }`}
                    >
                      <span className="text-xs">
                        {check.status === "required" ? "!" : check.status === "recommended" ? "○" : "✓"}
                      </span>
                    </div>
                    <span className="text-sm text-gray-300">{check.item}</span>
                  </div>
                ))}
              </div>

              <div className="mt-6 flex gap-4">
                <Link
                  href="/ternaryair/voxel-lab"
                  className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white font-medium transition-all"
                >
                  <Box className="w-5 h-5" />
                  Start Designing
                </Link>
                <Link
                  href="/ternaryair/tutorials"
                  className="flex items-center gap-2 px-6 py-3 rounded-xl bg-dark-700 hover:bg-dark-600 text-gray-300 font-medium border border-dark-500 transition-all"
                >
                  <Play className="w-5 h-5" />
                  Watch Tutorial
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="bg-gradient-to-r from-green-900/30 via-dark-800 to-emerald-900/30 rounded-2xl p-8 border border-green-500/20 text-center">
          <h2 className="text-2xl font-bold mb-4">Ready to Make Your Chip?</h2>
          <p className="text-gray-400 mb-6 max-w-xl mx-auto">
            Complete your design in TernaryAir, and we&apos;ll help you navigate the manufacturing 
            process from first prototype to production.
          </p>
          <Link
            href="/ternaryair/voxel-lab"
            className="inline-flex items-center gap-3 bg-green-600 hover:bg-green-500 text-white px-8 py-4 rounded-xl font-semibold transition-all"
          >
            <Rocket className="w-5 h-5" />
            Start Your Design
          </Link>
        </section>
      </div>
    </div>
  );
}
