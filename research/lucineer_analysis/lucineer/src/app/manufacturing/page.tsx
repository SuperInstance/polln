"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Head from "next/head";
import Link from "next/link";
import {
  Atom,
  Beaker,
  Box,
  Cpu,
  Database,
  Eye,
  Factory,
  Gauge,
  Layers,
  Lightbulb,
  Microscope,
  Shield,
  Sparkles,
  Sun,
  Target,
  Waves,
  Zap,
  AlertTriangle,
} from "lucide-react";

// Manufacturing Process Steps
const manufacturingSteps = [
  {
    id: "silicon-extraction",
    name: "Silicon Extraction",
    subtitle: "From Sand to Crystal",
    icon: Sun,
    color: "from-amber-500 to-orange-600",
    description: "Silicon is extracted from silica sand through carbothermic reduction at 1900°C",
    physics: [
      { name: "Reaction Temperature", value: "T = 1900°C", meaning: "Carbothermic reduction" },
      { name: "Chemical Equation", value: "SiO₂ + 2C → Si + 2CO", meaning: "Silicon dioxide to silicon" },
      { name: "Purity Target", value: "99.9999999%", meaning: "9N purity required" },
    ],
    voxelConcept: "Watch sand grains transform into glowing crystals as heat rises",
    whatYouLearn: "Phase transitions, chemical reduction, purity metrics",
  },
  {
    id: "czochralski-growth",
    name: "Czochralski Growth",
    subtitle: "Crystal Pulling",
    icon: Atom,
    color: "from-blue-500 to-cyan-600",
    description: "A seed crystal is dipped into molten silicon and slowly pulled upward, rotating to form a cylindrical ingot",
    physics: [
      { name: "Pull Rate", value: "v = 1-2 mm/min", meaning: "Crystal growth speed" },
      { name: "Rotation Speed", value: "ω = 10-40 rpm", meaning: "Ingot rotation for uniformity" },
      { name: "Temperature Gradient", value: "ΔT = 20-50°C/cm", meaning: "Solidification control" },
    ],
    voxelConcept: "Control the pull! A voxel cylinder grows from the molten pool",
    whatYouLearn: "Crystal growth mechanics, thermal gradients, defect formation",
  },
  {
    id: "wafer-slicing",
    name: "Wafer Slicing",
    subtitle: "Diamond Wire Saw",
    icon: Target,
    color: "from-slate-500 to-gray-600",
    description: "Silicon ingot is sliced into thin wafers using a diamond-embedded wire saw",
    physics: [
      { name: "Wafer Thickness", value: "t = 775 μm (300mm)", meaning: "Standard thickness" },
      { name: "Kerf Loss", value: "k ≈ 100-150 μm", meaning: "Material lost per cut" },
      { name: "Surface Roughness", value: "Ra < 0.5 μm", meaning: "Initial finish quality" },
    ],
    voxelConcept: "Guide the wire through the crystal, minimizing waste",
    whatYouLearn: "Diamond cutting, kerf loss economics, precision mechanics",
  },
  {
    id: "photolithography",
    name: "Photolithography",
    subtitle: "Pattern Transfer",
    icon: Eye,
    color: "from-violet-500 to-purple-600",
    description: "UV light projects a pattern through a mask onto photoresist-coated wafer",
    physics: [
      { name: "Resolution", value: "R = k₁λ/NA", meaning: "Rayleigh criterion" },
      { name: "Wavelength", value: "λ = 193 nm (ArF)", meaning: "Deep UV lithography" },
      { name: "Numerical Aperture", value: "NA = 1.35", meaning: "Immersion optics" },
    ],
    voxelConcept: "Be the photon! Navigate through the mask to expose the pattern",
    whatYouLearn: "Optical physics, resolution limits, exposure chemistry",
  },
  {
    id: "etching",
    name: "Etching",
    subtitle: "Selective Removal",
    icon: Beaker,
    color: "from-green-500 to-emerald-600",
    description: "Chemical or plasma etching removes material in exposed areas",
    physics: [
      { name: "Etch Rate", value: "ER = k·[reactant]", meaning: "Reaction kinetics" },
      { name: "Selectivity", value: "S = ER₁/ER₂", meaning: "Material preference" },
      { name: "Anisotropy", value: "A = 1 - (lateral/vertical)", meaning: "Directional control" },
    ],
    voxelConcept: "Control the etch - carve channels into the voxel landscape",
    whatYouLearn: "Plasma chemistry, selectivity, anisotropic etching",
  },
  {
    id: "ion-implantation",
    name: "Ion Implantation",
    subtitle: "Doping the Silicon",
    icon: AlertTriangle,
    color: "from-yellow-500 to-orange-600",
    description: "Accelerated ions are shot into the silicon to modify its electrical properties",
    physics: [
      { name: "Ion Energy", value: "E = 1 keV - 1 MeV", meaning: "Acceleration voltage" },
      { name: "Dose", value: "Φ = 10¹¹ - 10¹⁶ cm⁻²", meaning: "Ion concentration" },
      { name: "Range", value: "Rp = f(E, M)", meaning: "Penetration depth" },
    ],
    voxelConcept: "Launch ions into the crystal! Aim for the right depth",
    whatYouLearn: "Dopant profiles, ion stopping, activation annealing",
  },
  {
    id: "metallization",
    name: "Metallization",
    subtitle: "Metal Interconnects",
    icon: Zap,
    color: "from-amber-400 to-yellow-600",
    description: "Copper or aluminum wires are patterned to connect transistors",
    physics: [
      { name: "Wire Width", value: "w = 10-100 nm", meaning: "Minimum feature" },
      { name: "Resistance", value: "R = ρL/A", meaning: "Resistivity equation" },
      { name: "Current Density", value: "J < 10⁶ A/cm²", meaning: "Electromigration limit" },
    ],
    voxelConcept: "Draw the metal highways where electrons will flow!",
    whatYouLearn: "Interconnect design, RC delay, electromigration",
  },
  {
    id: "mask-locked-weights",
    name: "Mask-Locked Weights",
    subtitle: "Neural Encoding",
    icon: Cpu,
    color: "from-emerald-500 to-green-600",
    description: "Neural network weights are physically encoded as metal patterns - immutable forever",
    physics: [
      { name: "Ternary Encoding", value: "w ∈ {-1, 0, +1}", meaning: "BitNet weights" },
      { name: "Bit Density", value: "ρ = 10¹² bits/cm²", meaning: "Information density" },
      { name: "Zero Access Energy", value: "E_access = 0", meaning: "No memory fetch" },
    ],
    voxelConcept: "Freeze the weights! See neural patterns become silicon reality",
    whatYouLearn: "Weight encoding, ternary logic, hardware instantiation",
  },
  {
    id: "packaging",
    name: "Packaging",
    subtitle: "Chip Protection",
    icon: Shield,
    color: "from-blue-500 to-indigo-600",
    description: "The die is mounted, wire-bonded or flip-chipped, and encapsulated",
    physics: [
      { name: "Thermal Resistance", value: "θ_ja = 20-100 °C/W", meaning: "Heat dissipation" },
      { name: "Bond Wire", value: "d = 25-50 μm", meaning: "Wire diameter" },
      { name: "I/O Count", value: "N = 8-1000+", meaning: "Package pins" },
    ],
    voxelConcept: "Build a protective shell around the precious silicon",
    whatYouLearn: "Package types, thermal design, wire bonding",
  },
  {
    id: "testing-binning",
    name: "Testing & Binning",
    subtitle: "Quality Sorting",
    icon: Gauge,
    color: "from-indigo-500 to-violet-600",
    description: "Chips are tested for functionality and sorted by performance grade",
    physics: [
      { name: "Test Coverage", value: "C > 99%", meaning: "Fault detection" },
      { name: "Yield", value: "Y = e^(-D₀A)", meaning: "Poisson model" },
      { name: "Bins", value: "B = speed grades", meaning: "Performance tiers" },
    ],
    voxelConcept: "Run the tests! Sort chips into speed bins",
    whatYouLearn: "ATPG, yield modeling, binning economics",
  },
];

// Yield Calculator
function YieldCalculator() {
  const [dieArea, setDieArea] = useState(120);
  const [defectDensity, setDefectDensity] = useState(0.5);

  const yieldRate = Math.exp(-defectDensity * dieArea / 100);
  const grossDies = Math.floor(Math.PI * 150 * 150 / dieArea);
  const goodDies = Math.floor(grossDies * yieldRate);

  return (
    <div className="bg-card rounded-2xl border border-border p-6">
      <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <Database className="w-5 h-5 text-emerald-400" />
        Yield Calculator
      </h3>
      
      <div className="space-y-4">
        <div>
          <label className="text-sm text-muted-foreground">Die Area (mm²): {dieArea}</label>
          <input
            type="range"
            min="10"
            max="500"
            value={dieArea}
            onChange={(e) => setDieArea(Number(e.target.value))}
            className="w-full h-2 bg-muted rounded-lg"
          />
        </div>

        <div>
          <label className="text-sm text-muted-foreground">Defect Density: {defectDensity.toFixed(1)}</label>
          <input
            type="range"
            min="0.1"
            max="2"
            step="0.1"
            value={defectDensity}
            onChange={(e) => setDefectDensity(Number(e.target.value))}
            className="w-full h-2 bg-muted rounded-lg"
          />
        </div>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-4">
        <div className="bg-muted rounded-xl p-4 text-center">
          <div className="text-3xl font-bold text-emerald-400">{grossDies}</div>
          <div className="text-xs text-muted-foreground">Gross Dies</div>
        </div>
        <div className="bg-muted rounded-xl p-4 text-center">
          <div className="text-3xl font-bold text-cyan-400">{(yieldRate * 100).toFixed(1)}%</div>
          <div className="text-xs text-muted-foreground">Yield</div>
        </div>
        <div className="col-span-2 bg-emerald-500/10 rounded-xl p-4 text-center border border-emerald-500/30">
          <div className="text-4xl font-bold text-emerald-400">{goodDies}</div>
          <div className="text-sm text-muted-foreground">Good Dies per Wafer</div>
        </div>
      </div>
    </div>
  );
}

// Process Step Card
function ProcessStepCard({ step, index, onClick }: { step: typeof manufacturingSteps[0]; index: number; onClick: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.03 }}
      onClick={onClick}
      className="cursor-pointer group"
    >
      <div className="bg-card rounded-2xl border border-border overflow-hidden hover:border-emerald-500/50 transition-colors">
        <div className={`h-2 bg-gradient-to-r ${step.color}`} />
        <div className="p-4">
          <div className="flex items-center gap-3 mb-2">
            <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${step.color} flex items-center justify-center`}>
              <step.icon className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-xs font-mono text-muted-foreground">Step {index + 1}</span>
              <h3 className="font-semibold">{step.name}</h3>
            </div>
          </div>
          <p className="text-xs text-muted-foreground line-clamp-2">{step.description}</p>
        </div>
      </div>
    </motion.div>
  );
}

// Detail Modal
function StepDetailModal({ step, onClose }: { step: typeof manufacturingSteps[0]; onClose: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, y: 20 }}
        animate={{ scale: 1, y: 0 }}
        exit={{ scale: 0.9, y: 20 }}
        className="bg-card rounded-3xl border border-border max-w-3xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className={`h-24 bg-gradient-to-r ${step.color} relative flex items-center px-6`}>
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-white/20 flex items-center justify-center">
              <step.icon className="w-7 h-7 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">{step.name}</h2>
              <p className="text-white/80">{step.subtitle}</p>
            </div>
          </div>
        </div>

        <div className="p-6 space-y-6">
          <p className="text-lg text-muted-foreground">{step.description}</p>

          <div>
            <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Atom className="w-5 h-5 text-cyan-400" />
              Physics & Mathematics
            </h3>
            <div className="grid gap-3">
              {step.physics.map((formula, i) => (
                <div key={i} className="bg-black/30 rounded-lg p-4 border border-white/10">
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-sm font-medium text-emerald-400">{formula.name}</span>
                    <span className="text-xs text-muted-foreground">{formula.meaning}</span>
                  </div>
                  <code className="text-xl font-mono text-white">{formula.value}</code>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-gradient-to-r from-emerald-500/10 to-cyan-400/10 rounded-xl p-4 border border-emerald-500/20">
            <h4 className="font-medium mb-2 flex items-center gap-2">
              <Box className="w-4 h-4 text-cyan-400" />
              Voxel Experience
            </h4>
            <p className="text-muted-foreground">{step.voxelConcept}</p>
          </div>

          <button
            onClick={onClose}
            className="w-full py-3 rounded-xl bg-emerald-500/10 text-emerald-400 font-medium"
          >
            Close
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default function ManufacturingPage() {
  const [selectedStep, setSelectedStep] = useState<typeof manufacturingSteps[0] | null>(null);

  return (
    <>
      <Head>
        <title>Manufacturing | Lucineer - From Sand to Silicon</title>
        <meta name="description" content="Interactive visualization of semiconductor manufacturing for mask-locked inference chips" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-background via-background to-emerald-500/5 pt-20">
        <section className="py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center mb-12"
            >
              <div className="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/30 rounded-full px-4 py-2 mb-6">
                <Factory className="w-4 h-4 text-emerald-400" />
                <span className="text-emerald-400 text-sm font-medium">Virtual Fab Floor</span>
              </div>

              <h1 className="text-4xl sm:text-5xl font-bold mb-4">
                <span className="bg-gradient-to-r from-emerald-400 via-cyan-400 to-purple-400 bg-clip-text text-transparent">
                  From Sand to Silicon
                </span>
              </h1>
              
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Walk through 10 manufacturing steps that transform raw materials into mask-locked inference chips
              </p>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
                {manufacturingSteps.map((step, index) => (
                  <ProcessStepCard
                    key={step.id}
                    step={step}
                    index={index}
                    onClick={() => setSelectedStep(step)}
                  />
                ))}
              </div>

              <div className="space-y-6">
                <YieldCalculator />

                <div className="bg-card rounded-2xl border border-border p-6">
                  <h3 className="text-lg font-semibold mb-4">Key Metrics</h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Process Node</span>
                      <span className="font-mono text-emerald-400">28nm</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Metal Layers</span>
                      <span className="font-mono text-cyan-400">6-8</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Cycle Time</span>
                      <span className="font-mono text-amber-400">6-8 weeks</span>
                    </div>
                  </div>
                </div>

                <Link
                  href="/math-universe"
                  className="block bg-card rounded-2xl border border-border p-4 hover:border-emerald-500/50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <Box className="w-5 h-5 text-emerald-400" />
                    <span>Explore Math Universe →</span>
                  </div>
                </Link>
              </div>
            </div>
          </div>
        </section>

        <AnimatePresence>
          {selectedStep && (
            <StepDetailModal step={selectedStep} onClose={() => setSelectedStep(null)} />
          )}
        </AnimatePresence>
      </div>
    </>
  );
}
