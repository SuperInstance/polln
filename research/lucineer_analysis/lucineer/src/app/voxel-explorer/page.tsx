"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence, useAnimation } from "framer-motion";
import {
  Zap,
  Box,
  Cpu,
  HardDrive,
  Lightbulb,
  CircuitBoard,
  ChevronRight,
  ChevronDown,
  Play,
  Pause,
  RotateCcw,
  X,
  Info,
  Volume2,
  VolumeX,
  Sparkles,
  ArrowRight,
  ArrowDown,
  ArrowUp,
  Eye,
  Layers,
  Grid3X3,
  Home,
  BookOpen,
  GraduationCap,
  Heart,
  Star,
  Trophy,
  Target,
  Compass,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

// ============================================================================
// LUCINEER - STEPHEN BIESTY INSPIRED VOXEL EXPLORER
// Educational Technology Cross-Section Explorer
// ============================================================================

// Age levels
type AgeLevel = "elementary" | "middle" | "high";

// Character definitions
interface Character {
  id: string;
  name: string;
  role: string;
  emoji: string;
  color: string;
  bgColor: string;
  description: Record<AgeLevel, string>;
  dialogue: Record<AgeLevel, string[]>;
}

// Component definitions
interface ComponentInfo {
  id: string;
  name: string;
  description: Record<AgeLevel, string>;
  details: Record<AgeLevel, string[]>;
}

// Module definitions
interface ContentModule {
  id: string;
  title: string;
  subtitle: string;
  icon: typeof Cpu;
  color: string;
  gradient: string;
  characters: Character[];
  components: ComponentInfo[];
  funFacts: Record<AgeLevel, string[]>;
  journey: string[];
}

// ============================================================================
// CHARACTER DEFINITIONS
// ============================================================================

const CHARACTERS: Record<string, Character> = {
  volt: {
    id: "volt",
    name: "Volt",
    role: "Voltage Guide",
    emoji: "⚡",
    color: "text-yellow-400",
    bgColor: "bg-yellow-500/20",
    description: {
      elementary: "I'm Volt! I carry electricity like a lightning bolt! ZAP!",
      middle: "I measure electrical potential difference - the push that moves electrons through circuits.",
      high: "I represent voltage (V), the electromotive force measured in volts. I drive current through resistance according to Ohm's Law: V = IR.",
    },
    dialogue: {
      elementary: [
        "Ready to ZOOM through the circuit! ⚡",
        "I give electrons the energy to move!",
        "More voltage = FASTER electrons! Vroom!",
      ],
      middle: [
        "I create the potential difference that drives electron flow.",
        "Higher voltage means more energy per electron.",
        "I work with Current and Resistance - we're the Ohm's Law team!",
      ],
      high: [
        "I establish the electric field that accelerates charge carriers.",
        "My potential difference determines current flow: I = V/R.",
        "Power dissipation: P = VI. I'm essential to energy transfer!",
      ],
    },
  },
  bit: {
    id: "bit",
    name: "Bit",
    role: "Data Carrier",
    emoji: "📦",
    color: "text-blue-400",
    bgColor: "bg-blue-500/20",
    description: {
      elementary: "I'm Bit! I carry a tiny piece of information - either a 0 or a 1!",
      middle: "I'm the smallest unit of digital data. Eight of me make a byte!",
      high: "I'm a binary digit - the fundamental unit of information in computing and digital communications.",
    },
    dialogue: {
      elementary: [
        "I can be a ZERO or a ONE! 🎭",
        "Put 8 of us together = 1 Byte!",
        "I travel through wires super fast!",
      ],
      middle: [
        "I represent a binary state - on or off, true or false.",
        "With my friends, we can represent any number or letter!",
        "I travel through circuits as high or low voltage signals.",
      ],
      high: [
        "I encode information entropy - one bit = one binary decision.",
        "Shannon's information theory defines my capacity.",
        "I propagate as voltage transitions through logic gates.",
      ],
    },
  },
  fetch: {
    id: "fetch",
    name: "Fetch",
    role: "Memory Retriever",
    emoji: "🐕",
    color: "text-amber-400",
    bgColor: "bg-amber-500/20",
    description: {
      elementary: "I'm Fetch the dog robot! I run to memory and bring back data! Woof!",
      middle: "I'm the fetch unit - I retrieve instructions and data from memory for the CPU to process.",
      high: "I execute the fetch cycle: MAR ← PC, MDR ← M[MAR], IR ← MDR, PC ← PC+1. I'm the first stage of the instruction pipeline.",
    },
    dialogue: {
      elementary: [
        "Going to get your data! *woof* 🐕",
        "I run REALLY fast to memory!",
        "Got it! Here's your information!",
      ],
      middle: [
        "Initiating memory fetch operation...",
        "Transferring address to Memory Address Register.",
        "Data retrieved! Loading into instruction register.",
      ],
      high: [
        "Executing fetch-decode-execute cycle...",
        "PC to MAR, initiating memory read.",
        "MDR loaded, incrementing PC. Ready for decode stage.",
      ],
    },
  },
  carry: {
    id: "carry",
    name: "Carry",
    role: "Arithmetic Helper",
    emoji: "🐜",
    color: "text-orange-400",
    bgColor: "bg-orange-500/20",
    description: {
      elementary: "I'm Carry the ant! When numbers get too big, I help carry the extra!",
      middle: "I handle carry operations in addition and overflow in arithmetic calculations.",
      high: "I manage the carry flag in the ALU status register, handling arithmetic overflow and multi-precision operations.",
    },
    dialogue: {
      elementary: [
        "One plus one equals... TWO! I carry the extra! 🐜",
        "When the bucket is full, I carry to the next!",
        "Math is easier with friends helping!",
      ],
      middle: [
        "Monitoring ALU overflow conditions...",
        "Setting carry flag for multi-byte operations.",
        "Propagating carry through adder chain.",
      ],
      high: [
        "Detecting arithmetic overflow in signed operations.",
        "Updating PSR carry flag for conditional branches.",
        "Implementing carry-lookahead for faster addition.",
      ],
    },
  },
  switch: {
    id: "switch",
    name: "Switch",
    role: "Transistor Gatekeeper",
    emoji: "🚪",
    color: "text-cyan-400",
    bgColor: "bg-cyan-500/20",
    description: {
      elementary: "I'm Switch! I open and close to let electricity through or block it!",
      middle: "I'm a transistor - a tiny switch that controls electron flow with a gate signal.",
      high: "I'm a MOSFET transistor - a field-effect device that modulates current flow through a semiconductor channel using gate voltage.",
    },
    dialogue: {
      elementary: [
        "Gate OPEN! Come on through! 🚪",
        "Gate CLOSED! No electrons today!",
        "I switch MILLIONS of times per second!",
      ],
      middle: [
        "Gate voltage applied - channel conducting.",
        "Threshold voltage exceeded - switching ON.",
        "I amplify signals and perform logic operations.",
      ],
      high: [
        "Vgs > Vth - inversion layer formed.",
        "Channel modulation controlling Id.",
        "Operating in saturation region for amplification.",
      ],
    },
  },
  merge: {
    id: "merge",
    name: "Merge",
    role: "CRDT Combiner",
    emoji: "🐙",
    color: "text-purple-400",
    bgColor: "bg-purple-500/20",
    description: {
      elementary: "I'm Merge the octopus! I combine things from different places into one!",
      middle: "I handle Conflict-free Replicated Data Types - merging data from multiple sources safely.",
      high: "I implement CRDT merge operations - monotonically increasing data structures that guarantee eventual consistency without coordination.",
    },
    dialogue: {
      elementary: [
        "I have many arms to gather data! 🐙",
        "Everyone's work comes together!",
        "No fighting - we merge peacefully!",
      ],
      middle: [
        "Merging concurrent updates from replicas...",
        "Using commutative operations to resolve conflicts.",
        "Eventual consistency guaranteed!",
      ],
      high: [
        "Applying state-based CRDT merge function.",
        "Monotonic merge preserving all updates.",
        "Vector clock comparison for causality tracking.",
      ],
    },
  },
  cache: {
    id: "cache",
    name: "Cache",
    role: "Fast Storage Keeper",
    emoji: "🐿️",
    color: "text-green-400",
    bgColor: "bg-green-500/20",
    description: {
      elementary: "I'm Cache the squirrel! I keep important stuff close by for quick access!",
      middle: "I'm the CPU cache - a super-fast memory that keeps frequently used data close to the processor.",
      high: "I implement a multi-level cache hierarchy (L1/L2/L3) with SRAM technology, using set-associative mapping and replacement policies.",
    },
    dialogue: {
      elementary: [
        "I store the BEST stuff right here! 🐿️",
        "Need something? I probably have it ready!",
        "My stash is SUPER fast to check!",
      ],
      middle: [
        "Checking L1 cache for requested address...",
        "Cache HIT! Data ready in nanoseconds.",
        "LRU replacement policy engaged.",
      ],
      high: [
        "Translation Lookaside Buffer lookup complete.",
        "Set-associative mapping: way prediction hit.",
        "Coherency protocol: MESI state update.",
      ],
    },
  },
  router: {
    id: "router",
    name: "Router",
    role: "Traffic Director",
    emoji: "🚦",
    color: "text-red-400",
    bgColor: "bg-red-500/20",
    description: {
      elementary: "I'm Router! I tell data packets which way to go! Left? Right? Straight?",
      middle: "I route data packets through networks, finding the best path to their destination.",
      high: "I implement packet routing using routing tables, NAT translation, and various protocols like OSPF and BGP.",
    },
    dialogue: {
      elementary: [
        "Turn left for the internet! 🚦",
        "I know ALL the best shortcuts!",
        "Traffic jam? I'll find another way!",
      ],
      middle: [
        "Analyzing packet destination IP...",
        "Routing table lookup complete.",
        "Forwarding to next hop.",
      ],
      high: [
        "BGP route selection in progress.",
        "NAT translation applied.",
        "QoS policy enforcement engaged.",
      ],
    },
  },
  pixel: {
    id: "pixel",
    name: "Pixel",
    role: "Display Specialist",
    emoji: "📺",
    color: "text-pink-400",
    bgColor: "bg-pink-500/20",
    description: {
      elementary: "I'm Pixel! I'm a tiny dot of color on your screen! Millions of us make pictures!",
      middle: "I represent a picture element - I combine red, green, and blue light to create any color.",
      high: "I'm a pixel with RGB subpixels, each controlled by 8-bit (or higher) color channels, refreshing at 60-240Hz.",
    },
    dialogue: {
      elementary: [
        "Red + Blue + Green = ALL the colors! 📺",
        "I light up to show you pictures!",
        "My friends and I make videos move!",
      ],
      middle: [
        "Adjusting RGB subpixel intensities...",
        "24-bit color depth activated.",
        "Refresh rate synchronized.",
      ],
      high: [
        "PWM duty cycle controlling luminance.",
        "sRGB color space mapping applied.",
        "Frame buffer DMA transfer complete.",
      ],
    },
  },
  photon: {
    id: "photon",
    name: "Photon",
    role: "Light Messenger",
    emoji: "🕊️",
    color: "text-white",
    bgColor: "bg-white/20",
    description: {
      elementary: "I'm Photon! I'm a tiny packet of light that zips around super fast!",
      middle: "I'm a photon - a quantum of light that carries electromagnetic energy at the speed of light.",
      high: "I'm a photon - an elementary particle with zero rest mass, representing a quantum of the electromagnetic field with energy E = hf.",
    },
    dialogue: {
      elementary: [
        "I fly at the SPEED OF LIGHT! 🕊️",
        "I carry energy and make things glow!",
        "Electrons make me when they get excited!",
      ],
      middle: [
        "Released by electron energy transition.",
        "Traveling at 299,792,458 m/s!",
        "Carrying electromagnetic energy.",
      ],
      high: [
        "Spontaneous emission from excited state.",
        "Energy quantized: E = hν = hc/λ.",
        "Wave-particle duality: probability amplitude.",
      ],
    },
  },
};

// ============================================================================
// CONTENT MODULES
// ============================================================================

const CONTENT_MODULES: ContentModule[] = [
  {
    id: "transistor",
    title: "Inside a Transistor",
    subtitle: "The Switch That Changed the World",
    icon: Zap,
    color: "text-yellow-400",
    gradient: "from-yellow-500/20 to-orange-500/20",
    characters: [CHARACTERS.volt, CHARACTERS.switch, CHARACTERS.bit],
    components: [
      {
        id: "source",
        name: "Source",
        description: {
          elementary: "Where the electrons start their journey!",
          middle: "The terminal where current enters the transistor channel.",
          high: "The source terminal - heavily doped semiconductor region providing charge carriers.",
        },
        details: {
          elementary: ["Connected to ground", "Electrons flow from here"],
          middle: ["Connected to circuit ground", "Provides charge carriers", "Forms one end of the channel"],
          high: ["Heavily doped n+ or p+ region", "Source-body junction bias affects threshold", "Carrier injection point"],
        },
      },
      {
        id: "drain",
        name: "Drain",
        description: {
          elementary: "Where electrons come out after their journey!",
          middle: "The terminal where current exits the transistor channel.",
          high: "The drain terminal - collects charge carriers, voltage determines current flow.",
        },
        details: {
          elementary: ["Connected to output", "Electrons exit here"],
          middle: ["Connected to Vdd through load", "Current collected here", "Forms other end of channel"],
          high: ["Heavily doped region", "Drain-source voltage creates electric field", "Pinch-off region at saturation"],
        },
      },
      {
        id: "gate",
        name: "Gate",
        description: {
          elementary: "The magic switch that controls everything!",
          middle: "The control terminal that opens or closes the channel.",
          high: "The gate terminal - capacitive control electrode that modulates channel conductivity.",
        },
        details: {
          elementary: ["Opens and closes the path", "Like a water faucet!"],
          middle: ["Controls electron flow", "Voltage applied here switches the transistor", "Separated by thin insulator"],
          high: ["MOS capacitor structure", "Threshold voltage ~0.5-1V", "Gate oxide ~1-2nm thick"],
        },
      },
      {
        id: "channel",
        name: "Channel",
        description: {
          elementary: "The road electrons travel on!",
          middle: "The conductive path between source and drain.",
          high: "The inversion channel - formed when gate voltage exceeds threshold, enabling current flow.",
        },
        details: {
          elementary: ["Path for electrons", "Can be open or closed"],
          middle: ["Forms when gate is ON", "Resistance determines current", "Length affects speed"],
          high: ["Inversion layer formation", "Channel length ~5-20nm modern", "Mobility affects transconductance"],
        },
      },
    ],
    funFacts: {
      elementary: [
        "The first transistor was as big as a fingernail!",
        "Your phone has BILLIONS of transistors!",
        "Transistors are smaller than a virus!",
      ],
      middle: [
        "Modern transistors are only 5 nanometers wide!",
        "Moore's Law predicts transistors double every 2 years.",
        "Transistors replaced vacuum tubes in computers.",
      ],
      high: [
        "FinFETs use 3D fin structures for better control.",
        "Gate-all-around transistors are the next generation.",
        "Quantum tunneling limits transistor scaling below 1nm.",
      ],
    },
    journey: ["voltage", "gate", "channel", "output"],
  },
  {
    id: "cpu",
    title: "Chip City",
    subtitle: "Exploring a Modern Processor",
    icon: Cpu,
    color: "text-blue-400",
    gradient: "from-blue-500/20 to-cyan-500/20",
    characters: [CHARACTERS.fetch, CHARACTERS.carry, CHARACTERS.cache, CHARACTERS.bit],
    components: [
      {
        id: "cores",
        name: "CPU Cores",
        description: {
          elementary: "The brains that do all the thinking!",
          middle: "Independent processing units that execute instructions in parallel.",
          high: "Multi-core execution units with private L1 caches, sharing L3 cache and memory bus.",
        },
        details: {
          elementary: ["Each core is like a tiny computer", "More cores = more things at once!"],
          middle: ["Execute instructions independently", "Share memory and cache", "Typical CPUs have 4-16 cores"],
          high: ["Superscalar architecture", "Out-of-order execution", "Branch prediction units"],
        },
      },
      {
        id: "cache-mem",
        name: "Cache Memory",
        description: {
          elementary: "Super-fast storage right next to the brain!",
          middle: "Multi-level memory hierarchy for frequently accessed data.",
          high: "L1/L2 private caches per core, shared L3 cache, SRAM technology.",
        },
        details: {
          elementary: ["Like a desk vs a library", "Keeps important stuff close"],
          middle: ["L1: fastest, smallest", "L2: medium speed and size", "L3: shared between cores"],
          high: ["L1: 32-64KB, ~4 cycle latency", "L2: 256KB-1MB, ~12 cycles", "L3: 8-64MB, ~40 cycles"],
        },
      },
      {
        id: "alu",
        name: "ALU",
        description: {
          elementary: "The math station! Where numbers get crunched!",
          middle: "Arithmetic Logic Unit - performs math and logical operations.",
          high: "Combinational logic performing integer arithmetic, bitwise ops, and comparisons.",
        },
        details: {
          elementary: ["Does addition and subtraction", "Compares numbers too!"],
          middle: ["Performs arithmetic operations", "Handles logic (AND, OR, NOT)", "Results stored in registers"],
          high: ["Adder with carry lookahead", "Barrel shifter for rotations", "Flags: Zero, Sign, Carry, Overflow"],
        },
      },
      {
        id: "interconnect",
        name: "Interconnects",
        description: {
          elementary: "Tiny roads connecting everything together!",
          middle: "Communication pathways between components on the chip.",
          high: "Mesh/ring network-on-chip topology with cache coherency protocols.",
        },
        details: {
          elementary: ["Data travels on these roads", "Super tiny wires!"],
          middle: ["Connect all chip components", "Carry signals between parts", "Organized in layers"],
          high: ["Mesh topology in modern CPUs", "Cache coherency traffic", "Multiple metal layers (10-15)"],
        },
      },
    ],
    funFacts: {
      elementary: [
        "CPU stands for Central Processing Unit!",
        "Modern CPUs have billions of parts!",
        "They can do billions of math problems per second!",
      ],
      middle: [
        "CPU clock speeds are measured in GHz (billions per second!)",
        "The first CPU had only 2,300 transistors.",
        "CPUs generate heat and need cooling fans.",
      ],
      high: [
        "Modern CPUs have 10+ billion transistors.",
        "TDP (Thermal Design Power) ranges from 15W to 250W+.",
        "Instruction-level parallelism can execute 4-8 ops per cycle.",
      ],
    },
    journey: ["fetch", "decode", "execute", "writeback"],
  },
  {
    id: "memory",
    title: "Memory Lane",
    subtitle: "How RAM Remembers",
    icon: HardDrive,
    color: "text-green-400",
    gradient: "from-green-500/20 to-emerald-500/20",
    characters: [CHARACTERS.fetch, CHARACTERS.cache, CHARACTERS.bit],
    components: [
      {
        id: "dram-cell",
        name: "DRAM Cell",
        description: {
          elementary: "A tiny bucket that holds one bit of information!",
          middle: "One transistor and one capacitor storing a single bit.",
          high: "1T1C DRAM cell - capacitor stores charge, transistor provides access.",
        },
        details: {
          elementary: ["Full bucket = 1", "Empty bucket = 0"],
          middle: ["Capacitor holds charge", "Transistor controls access", "Needs constant refresh"],
          high: ["~30fF capacitor", "Charge leaks in ~64ms", "Row activation: ~30ns"],
        },
      },
      {
        id: "refresh",
        name: "Refresh Circuit",
        description: {
          elementary: "Keeps refilling the buckets so they don't leak!",
          middle: "Periodically recharges capacitors to maintain data integrity.",
          high: "Auto-refresh and self-refresh modes, 64ms refresh window for all rows.",
        },
        details: {
          elementary: ["Like watering plants!", "Done automatically"],
          middle: ["Reads and rewrites each cell", "Happens every few milliseconds", "Causes brief delays"],
          high: ["8192 rows to refresh per 64ms", "Refresh commands: tRFC ~350ns", "Refresh scheduling optimization"],
        },
      },
      {
        id: "row-column",
        name: "Row/Column Decoder",
        description: {
          elementary: "The address system that finds the right bucket!",
          middle: "Selects specific memory cells using row and column addresses.",
          high: "Hierarchical address decoding with sense amplifiers and column mux.",
        },
        details: {
          elementary: ["Like finding a seat in a stadium", "Row number + Column number = Location!"],
          middle: ["Row address activates a 'page'", "Column address selects specific cell", "Multiplexed addressing saves pins"],
          high: ["RAS/CAS strobe timing", "tRCD: Row to Column delay ~15ns", "Burst mode for sequential access"],
        },
      },
      {
        id: "sense-amp",
        name: "Sense Amplifier",
        description: {
          elementary: "Detects if a bucket is full or empty!",
          middle: "Amplifies tiny signals from memory cells into readable data.",
          high: "Differential amplifier detecting ~100mV signals, outputting full logic levels.",
        },
        details: {
          elementary: ["Makes weak signals strong!", "Helps read the data"],
          middle: ["Detects small voltage differences", "Amplifies to logic levels", "Shared across a row"],
          high: ["Precharge to Vdd/2", "Sensing time ~5ns", "Equalization for next read"],
        },
      },
    ],
    funFacts: {
      elementary: [
        "RAM stands for Random Access Memory!",
        "RAM forgets everything when power goes off!",
        "Your computer might have 8-32 GB of RAM!",
      ],
      middle: [
        "DDR means Double Data Rate - transfers on both clock edges!",
        "Modern RAM can transfer 25+ GB per second!",
        "RAM is much faster than your hard drive.",
      ],
      high: [
        "DDR5 offers 51.2 GB/s per module.",
        "CAS latency has increased but bandwidth improved.",
        "ECC RAM detects and corrects single-bit errors.",
      ],
    },
    journey: ["address", "activate", "read", "output"],
  },
  {
    id: "led",
    title: "The LED Light Show",
    subtitle: "How Electrons Become Light",
    icon: Lightbulb,
    color: "text-amber-400",
    gradient: "from-amber-500/20 to-yellow-500/20",
    characters: [CHARACTERS.volt, CHARACTERS.photon, CHARACTERS.pixel],
    components: [
      {
        id: "anode",
        name: "Anode (+)",
        description: {
          elementary: "Where positive charges enter!",
          middle: "The positive terminal connected to the p-type semiconductor.",
          high: "P-type anode region with hole majority carriers, forward biased junction.",
        },
        details: {
          elementary: ["Connect to positive side", "Electrons enter here"],
          middle: ["P-type semiconductor region", "Holes are majority carriers", "Forward bias required"],
          high: ["P-type doping: acceptor atoms", "Work function affects injection", "Contact resistance optimization"],
        },
      },
      {
        id: "cathode",
        name: "Cathode (-)",
        description: {
          elementary: "Where electrons come in!",
          middle: "The negative terminal connected to the n-type semiconductor.",
          high: "N-type cathode region with electron majority carriers, ohmic contact.",
        },
        details: {
          elementary: ["Connect to negative side", "Longer leg on LED!"],
          middle: ["N-type semiconductor region", "Electrons are majority carriers", "Current flows from cathode to anode"],
          high: ["N-type doping: donor atoms", "Electron injection efficiency", "Thermal management via substrate"],
        },
      },
      {
        id: "junction",
        name: "P-N Junction",
        description: {
          elementary: "The magical meeting place where light is born!",
          middle: "Where p-type and n-type semiconductors meet and create light.",
          high: "Forward-biased junction where electrons and holes recombine, emitting photons.",
        },
        details: {
          elementary: ["Like a dance floor for electrons!", "They meet and make light!"],
          middle: ["Electrons meet holes here", "Energy released as light", "Different materials = different colors!"],
          high: ["Bandgap determines wavelength", "GaAs: red, GaN: blue/green", "Internal quantum efficiency ~50-90%"],
        },
      },
      {
        id: "lens",
        name: "LED Lens",
        description: {
          elementary: "Focuses the light like a tiny flashlight!",
          middle: "Transparent encapsulation that directs and protects the light.",
          high: "Epoxy or silicone lens with specific viewing angle and TIR optics.",
        },
        details: {
          elementary: ["Makes light shine forward", "Protects the tiny chip inside"],
          middle: ["Shapes the light beam", "Different angles available", "Clear or diffused options"],
          high: ["Viewing angle: 15-120°", "TIR (Total Internal Reflection)", "Domed vs. flat lens design"],
        },
      },
    ],
    funFacts: {
      elementary: [
        "LED stands for Light Emitting Diode!",
        "LEDs can last 50,000 hours - that's 5+ years nonstop!",
        "LEDs come in ALL the colors of the rainbow!",
      ],
      middle: [
        "Blue LEDs were invented in 1994 - earning a Nobel Prize!",
        "White LEDs use a blue LED with yellow phosphor.",
        "LEDs are super efficient - little heat, lots of light!",
      ],
      high: [
        "External quantum efficiency ~60% for best devices.",
        "Droop effect reduces efficiency at high currents.",
        "Micro-LEDs are the future of displays.",
      ],
    },
    journey: ["voltage", "injection", "recombination", "emission"],
  },
  {
    id: "circuit",
    title: "Circuit Board City",
    subtitle: "Traces, Layers, and Components",
    icon: CircuitBoard,
    color: "text-emerald-400",
    gradient: "from-emerald-500/20 to-teal-500/20",
    characters: [CHARACTERS.volt, CHARACTERS.bit, CHARACTERS.router],
    components: [
      {
        id: "traces",
        name: "Copper Traces",
        description: {
          elementary: "Tiny copper roads for electricity to travel on!",
          middle: "Conductive pathways etched into the board connecting components.",
          high: "Controlled impedance transmission lines with specific width/thickness for signal integrity.",
        },
        details: {
          elementary: ["Like roads for electrons!", "Connect all the parts together"],
          middle: ["Made of copper foil", "Etched to create patterns", "Different widths for different currents"],
          high: ["Impedance: 50Ω single-ended", "Trace width vs. dielectric thickness", "Skin effect at high frequencies"],
        },
      },
      {
        id: "layers",
        name: "Board Layers",
        description: {
          elementary: "Like a sandwich with many floors!",
          middle: "Multiple layers of traces stacked with insulating material between.",
          high: "4-16 layer stackup with ground/power planes and signal layers.",
        },
        details: {
          elementary: ["More layers = more connections!", "Some layers are for power"],
          middle: ["Signal layers carry data", "Power/ground planes reduce noise", "Vias connect between layers"],
          high: ["Prepreg and core materials", "Layer stackup optimization", "EMI/EMC considerations"],
        },
      },
      {
        id: "vias",
        name: "Vias",
        description: {
          elementary: "Tiny tunnels between floors!",
          middle: "Small holes plated with copper that connect different layers.",
          high: "Through-hole, blind, and buried vias with specific aspect ratios.",
        },
        details: {
          elementary: ["Electrons take the elevator!", "Connect top to bottom"],
          middle: ["Drilled and plated holes", "Connect traces on different layers", "Different types for different uses"],
          high: ["Aspect ratio: depth/diameter", "Via-in-pad for BGAs", "Filled vs. tented vias"],
        },
      },
      {
        id: "components",
        name: "Components",
        description: {
          elementary: "All the little parts that make electronics work!",
          middle: "Resistors, capacitors, chips, and connectors soldered to the board.",
          high: "SMD and through-hole components with specific packages and footprints.",
        },
        details: {
          elementary: ["Each part has a job!", "Work together like a team"],
          middle: ["Resistors limit current", "Capacitors store charge", "ICs do the thinking"],
          high: ["IPC footprint standards", "Thermal relief patterns", "Tombstoning prevention"],
        },
      },
    ],
    funFacts: {
      elementary: [
        "PCB stands for Printed Circuit Board!",
        "The green color is a protective coating!",
        "Your computer has MANY circuit boards inside!",
      ],
      middle: [
        "PCBs can have 20+ layers in advanced devices!",
        "Gold is used on connector contacts - it doesn't corrode!",
        "Modern PCBs are designed on computers before being made.",
      ],
      high: [
        "HDI (High Density Interconnect) enables 0.1mm trace/space.",
        "Blind/buried vias reduce layer count.",
        "Flex and rigid-flex PCBs for wearables.",
      ],
    },
    journey: ["input", "trace", "component", "output"],
  },
  {
    id: "network",
    title: "The Network Highway",
    subtitle: "Data Packets Traveling",
    icon: CircuitBoard,
    color: "text-violet-400",
    gradient: "from-violet-500/20 to-purple-500/20",
    characters: [CHARACTERS.router, CHARACTERS.bit, CHARACTERS.merge],
    components: [
      {
        id: "packet",
        name: "Data Packet",
        description: {
          elementary: "A tiny package of information traveling through the internet!",
          middle: "A formatted unit of data with header, payload, and trailer.",
          high: "Layered protocol data unit with encapsulation through OSI model.",
        },
        details: {
          elementary: ["Like a letter in an envelope!", "Has an address on it!"],
          middle: ["Contains destination address", "Has a sequence number", "Includes error checking"],
          high: ["MTU: 1500 bytes typical", "Header overhead: 20-60 bytes", "Fragmentation and reassembly"],
        },
      },
      {
        id: "routing-table",
        name: "Routing Table",
        description: {
          elementary: "A map that shows where to send each package!",
          middle: "Database that tells the router which way to send each packet.",
          high: "Forwarding Information Base with prefix matching and next-hop selection.",
        },
        details: {
          elementary: ["Like a GPS for data!", "Knows all the roads!"],
          middle: ["Lists all destinations", "Shows best path to each", "Updates automatically"],
          high: ["Longest prefix match", "Administrative distance", "Route redistribution"],
        },
      },
      {
        id: "protocol",
        name: "Network Protocol",
        description: {
          elementary: "Rules that everyone follows to communicate!",
          middle: "Standard rules for formatting and transmitting data.",
          high: "TCP/IP stack with encapsulation, flow control, and error recovery.",
        },
        details: {
          elementary: ["Like speaking the same language!", "Everyone understands!"],
          middle: ["TCP for reliable delivery", "UDP for speed", "IP for addressing"],
          high: ["3-way handshake", "Sliding window flow control", "Congestion avoidance"],
        },
      },
      {
        id: "latency",
        name: "Latency",
        description: {
          elementary: "How long it takes for data to travel!",
          middle: "The delay between sending and receiving data.",
          high: "Propagation delay, transmission delay, queuing delay, processing delay.",
        },
        details: {
          elementary: ["Lower is better!", "Measured in milliseconds"],
          middle: ["Speed of light limits", "Distance matters", "Each hop adds delay"],
          high: ["RTT = 2 × propagation", "Jitter = variation in latency", "Bufferbloat causes latency spikes"],
        },
      },
    ],
    funFacts: {
      elementary: [
        "The internet sends data in tiny packets!",
        "A webpage might arrive in hundreds of packets!",
        "Packets can take different routes to the same place!",
      ],
      middle: [
        "Internet traffic travels at 2/3 speed of light in fiber!",
        "Packets can arrive out of order and be reassembled!",
        "TCP makes sure nothing gets lost along the way.",
      ],
      high: [
        "Intercontinental latency: ~50-200ms.",
        "Anycast routing enables global load balancing.",
        "QUIC protocol reduces connection setup latency.",
      ],
    },
    journey: ["send", "route", "transmit", "receive"],
  },
];

// ============================================================================
// AGE LEVEL CONFIGURATIONS
// ============================================================================

const AGE_CONFIGS = {
  elementary: {
    label: "Elementary",
    ages: "Ages 5-10",
    icon: Heart,
    color: "text-pink-400",
    bgColor: "bg-pink-500/20",
    borderColor: "border-pink-500/30",
    description: "Fun characters and simple explanations!",
  },
  middle: {
    label: "Middle School",
    ages: "Ages 11-14",
    icon: Star,
    color: "text-blue-400",
    bgColor: "bg-blue-500/20",
    borderColor: "border-blue-500/30",
    description: "More technical detail with engaging visuals!",
  },
  high: {
    label: "High School",
    ages: "Ages 15-18",
    icon: GraduationCap,
    color: "text-amber-400",
    bgColor: "bg-amber-500/20",
    borderColor: "border-amber-500/30",
    description: "Full technical explanations for curious minds!",
  },
};

// ============================================================================
// VOXEL CROSS-SECTION COMPONENTS
// ============================================================================

interface VoxelCellProps {
  x: number;
  y: number;
  color: string;
  delay?: number;
  onClick?: () => void;
  active?: boolean;
  label?: string;
}

function VoxelCell({ x, y, color, delay = 0, onClick, active = false, label }: VoxelCellProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, duration: 0.3, type: "spring" }}
      whileHover={{ scale: 1.1, zIndex: 10 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`
        w-8 h-8 sm:w-10 sm:h-10 cursor-pointer relative
        transition-all duration-200
        ${active ? "ring-2 ring-white/50 ring-offset-1 ring-offset-background" : ""}
      `}
      style={{
        backgroundColor: color,
        boxShadow: active ? `0 0 20px ${color}` : `2px 2px 0 rgba(0,0,0,0.3)`,
      }}
    >
      {label && (
        <span className="absolute inset-0 flex items-center justify-center text-[8px] sm:text-[10px] font-bold text-white/90">
          {label}
        </span>
      )}
    </motion.div>
  );
}

interface FlowArrowProps {
  startDelay?: number;
  direction?: "right" | "down" | "up" | "left";
  color?: string;
}

function FlowArrow({ startDelay = 0, direction = "right", color = "#22c55e" }: FlowArrowProps) {
  const getPath = () => {
    switch (direction) {
      case "down": return "M10 0 L10 20";
      case "up": return "M10 20 L10 0";
      case "left": return "M20 10 L0 10";
      default: return "M0 10 L20 10";
    }
  };

  const getArrow = () => {
    switch (direction) {
      case "down": return "M10 15 L6 10 M10 15 L14 10";
      case "up": return "M10 5 L6 10 M10 5 L14 10";
      case "left": return "M5 10 L10 6 M5 10 L10 14";
      default: return "M15 10 L10 6 M15 10 L10 14";
    }
  };

  return (
    <motion.svg
      width="20"
      height="20"
      viewBox="0 0 20 20"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: startDelay }}
      className="absolute"
    >
      <motion.path
        d={getPath()}
        stroke={color}
        strokeWidth="2"
        fill="none"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ delay: startDelay + 0.5, duration: 1, repeat: Infinity, repeatDelay: 0.5 }}
      />
      <motion.path
        d={getArrow()}
        stroke={color}
        strokeWidth="2"
        fill="none"
        initial={{ opacity: 0 }}
        animate={{ opacity: [0, 1, 1, 0] }}
        transition={{ delay: startDelay + 1, duration: 1, repeat: Infinity, repeatDelay: 0.5 }}
      />
    </motion.svg>
  );
}

// ============================================================================
// CHARACTER COMPONENT
// ============================================================================

interface CharacterBubbleProps {
  character: Character;
  ageLevel: AgeLevel;
  position?: "left" | "right";
  isWalking?: boolean;
  onDismiss?: () => void;
}

function CharacterBubble({ character, ageLevel, position = "left", isWalking = true, onDismiss }: CharacterBubbleProps) {
  const [currentDialogue, setCurrentDialogue] = useState(0);
  const dialogue = character.dialogue[ageLevel];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentDialogue((prev) => (prev + 1) % dialogue.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [dialogue.length]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, x: position === "left" ? -20 : 20 }}
      animate={{ opacity: 1, y: 0, x: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`flex ${position === "right" ? "flex-row-reverse" : ""} items-start gap-2 sm:gap-3 max-w-md`}
    >
      {/* Character */}
      <motion.div
        animate={isWalking ? { y: [0, -5, 0] } : {}}
        transition={{ duration: 1, repeat: Infinity, ease: "easeInOut" }}
        className={`flex-shrink-0 w-12 h-12 sm:w-16 sm:h-16 rounded-xl ${character.bgColor} border border-current/20 flex items-center justify-center text-2xl sm:text-3xl ${character.color}`}
      >
        {character.emoji}
      </motion.div>

      {/* Speech Bubble */}
      <motion.div
        layout
        className={`relative flex-1 ${character.bgColor} border border-current/20 rounded-xl p-2 sm:p-3`}
      >
        <div className={`text-sm sm:text-base font-medium ${character.color}`}>
          {character.name}
        </div>
        <AnimatePresence mode="wait">
          <motion.p
            key={currentDialogue}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.3 }}
            className="text-xs sm:text-sm text-foreground mt-1"
          >
            {dialogue[currentDialogue]}
          </motion.p>
        </AnimatePresence>
        
        {/* Bubble pointer */}
        <div
          className={`absolute top-3 w-2 h-2 ${character.bgColor} border-${position === "left" ? "r" : "l"} border-${position === "left" ? "t" : "t"} border-current/20 transform ${position === "left" ? "-left-1 rotate-45" : "-right-1 rotate-45"}`}
          style={{ borderTopColor: "transparent", borderRightColor: position === "left" ? "transparent" : undefined, borderLeftColor: position === "right" ? "transparent" : undefined }}
        />
      </motion.div>
    </motion.div>
  );
}

// ============================================================================
// CROSS-SECTION VISUALIZATION COMPONENTS
// ============================================================================

interface TransistorViewProps {
  ageLevel: AgeLevel;
  onSelectComponent: (id: string) => void;
  activeComponent: string | null;
  isExploded: boolean;
  isPlaying: boolean;
}

function TransistorView({ ageLevel, onSelectComponent, activeComponent, isExploded, isPlaying }: TransistorViewProps) {
  const [electronPos, setElectronPos] = useState(0);
  
  useEffect(() => {
    if (isPlaying) {
      const interval = setInterval(() => {
        setElectronPos((prev) => (prev + 1) % 100);
      }, 100);
      return () => clearInterval(interval);
    }
  }, [isPlaying]);

  const components = [
    { id: "source", color: "#3b82f6", label: "S", x: 0, y: 2 },
    { id: "gate", color: "#eab308", label: "G", x: 2, y: 1 },
    { id: "channel", color: "#22c55e", label: "CH", x: 2, y: 2 },
    { id: "drain", color: "#ef4444", label: "D", x: 4, y: 2 },
  ];

  return (
    <div className="relative w-full max-w-2xl mx-auto">
      {/* Transistor cross-section visualization */}
      <motion.div
        animate={isExploded ? { scale: 1.2 } : { scale: 1 }}
        className="relative bg-gradient-to-b from-slate-800/50 to-slate-900/50 rounded-2xl p-4 sm:p-8 border border-slate-700"
      >
        {/* Silicon substrate */}
        <div className="absolute inset-4 sm:inset-8 bg-gradient-to-b from-gray-600/30 to-gray-700/30 rounded-lg border border-gray-500/30">
          <div className="absolute top-0 left-0 right-0 text-center text-xs text-gray-400 py-1">
            Silicon Substrate
          </div>
        </div>

        {/* Component grid */}
        <div className="relative grid grid-cols-5 gap-1 sm:gap-2 py-6 sm:py-8">
          {components.map((comp, idx) => (
            <motion.div
              key={comp.id}
              style={{ gridColumnStart: comp.x + 1, gridRowStart: comp.y }}
              animate={isExploded ? { 
                x: (comp.x - 2) * 20, 
                y: (comp.y - 2) * 20,
                scale: 1.1 
              } : { x: 0, y: 0, scale: 1 }}
              transition={{ type: "spring", stiffness: 100 }}
            >
              <VoxelCell
                x={comp.x}
                y={comp.y}
                color={comp.color}
                delay={idx * 0.1}
                onClick={() => onSelectComponent(comp.id)}
                active={activeComponent === comp.id}
                label={comp.label}
              />
            </motion.div>
          ))}
        </div>

        {/* Electron flow animation */}
        {isPlaying && (
          <motion.div
            className="absolute w-2 h-2 sm:w-3 sm:h-3 bg-yellow-400 rounded-full"
            animate={{
              x: [0, 80, 160],
              opacity: [0, 1, 1, 0],
            }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            style={{ top: "60%", left: "15%" }}
          />
        )}

        {/* Gate oxide layer */}
        <div className="absolute top-1/3 left-1/3 right-1/3 h-2 sm:h-3 bg-amber-500/30 border border-amber-500/50 rounded text-center">
          <span className="text-[8px] sm:text-[10px] text-amber-400">Gate Oxide</span>
        </div>

        {/* Metal contacts */}
        <div className="absolute bottom-2 sm:bottom-4 left-4 sm:left-8 w-6 sm:w-8 h-2 bg-gray-400 rounded-sm" />
        <div className="absolute bottom-2 sm:bottom-4 right-4 sm:right-8 w-6 sm:w-8 h-2 bg-gray-400 rounded-sm" />
        <div className="absolute top-2 sm:top-4 left-1/2 transform -translate-x-1/2 w-6 sm:w-8 h-2 bg-gray-400 rounded-sm" />
      </motion.div>

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-2 sm:gap-4 mt-4">
        {components.map((comp) => (
          <button
            key={comp.id}
            onClick={() => onSelectComponent(comp.id)}
            className={`flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1 rounded-lg text-xs sm:text-sm transition-all ${
              activeComponent === comp.id ? "bg-white/10 ring-1 ring-white/30" : "bg-black/20"
            }`}
          >
            <div className="w-2 h-2 sm:w-3 sm:h-3 rounded-sm" style={{ backgroundColor: comp.color }} />
            <span className="capitalize">{comp.id}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

interface CPUViewProps {
  ageLevel: AgeLevel;
  onSelectComponent: (id: string) => void;
  activeComponent: string | null;
  isExploded: boolean;
  isPlaying: boolean;
}

function CPUView({ ageLevel, onSelectComponent, activeComponent, isExploded, isPlaying }: CPUViewProps) {
  const components = [
    { id: "cores", color: "#3b82f6", label: "Core", x: 1, y: 0, w: 2, h: 2 },
    { id: "cache-mem", color: "#22c55e", label: "L3 Cache", x: 0, y: 0, w: 1, h: 3 },
    { id: "alu", color: "#f59e0b", label: "ALU", x: 3, y: 0, w: 1, h: 1 },
    { id: "interconnect", color: "#8b5cf6", label: "Interconnect", x: 0, y: 3, w: 4, h: 1 },
  ];

  return (
    <div className="relative w-full max-w-2xl mx-auto">
      <motion.div
        animate={isExploded ? { scale: 1.1 } : { scale: 1 }}
        className="relative bg-gradient-to-b from-slate-800/50 to-slate-900/50 rounded-2xl p-4 sm:p-6 border border-slate-700"
      >
        {/* CPU Die */}
        <div className="absolute inset-2 sm:inset-4 bg-gradient-to-br from-gray-700/20 to-gray-800/20 rounded-lg border border-gray-600/30">
          <div className="absolute top-0 left-0 right-0 text-center text-[10px] sm:text-xs text-gray-400 py-1">
            CPU Die (Silicon)
          </div>
        </div>

        {/* Component grid */}
        <div className="relative grid grid-cols-4 gap-1 sm:gap-2 p-4 sm:p-6 min-h-[200px] sm:min-h-[280px]">
          {components.map((comp, idx) => (
            <motion.div
              key={comp.id}
              style={{ 
                gridColumnStart: comp.x + 1, 
                gridColumnEnd: comp.x + comp.w + 1,
                gridRowStart: comp.y + 1,
                gridRowEnd: comp.y + comp.h + 1,
                backgroundColor: comp.color,
              }}
              animate={isExploded ? { 
                scale: 1.05,
                x: (comp.x - 1.5) * 10,
                y: (comp.y - 1.5) * 10,
              } : { scale: 1, x: 0, y: 0 }}
              transition={{ type: "spring", stiffness: 100 }}
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onSelectComponent(comp.id)}
              className={`
                rounded-lg cursor-pointer flex items-center justify-center
                text-xs sm:text-sm font-medium text-white/90
                transition-all duration-200 p-2 sm:p-4
                ${activeComponent === comp.id ? "ring-2 ring-white/50" : ""}
              `}
            >
              <div className="text-center">
                <div className="text-[10px] sm:text-xs opacity-70">{comp.label}</div>
                {isPlaying && comp.id === "cores" && (
                  <motion.div
                    className="mt-1 w-2 h-2 sm:w-3 sm:h-3 mx-auto bg-white/50 rounded-full"
                    animate={{ scale: [1, 1.3, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  />
                )}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Pin grid */}
        <div className="absolute bottom-0 left-0 right-0 flex justify-center gap-0.5 p-1">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="w-1 h-2 sm:w-1.5 sm:h-3 bg-gray-400 rounded-sm" />
          ))}
        </div>
      </motion.div>

      {/* Data flow animation */}
      {isPlaying && (
        <motion.div className="absolute inset-0 pointer-events-none">
          <motion.div
            className="absolute w-2 h-2 bg-blue-400 rounded-full"
            animate={{
              x: ["10%", "50%", "90%"],
              y: ["50%", "30%", "50%"],
            }}
            transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
          />
        </motion.div>
      )}

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-2 sm:gap-4 mt-4">
        {components.map((comp) => (
          <button
            key={comp.id}
            onClick={() => onSelectComponent(comp.id)}
            className={`flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1 rounded-lg text-xs sm:text-sm transition-all ${
              activeComponent === comp.id ? "bg-white/10 ring-1 ring-white/30" : "bg-black/20"
            }`}
          >
            <div className="w-2 h-2 sm:w-3 sm:h-3 rounded-sm" style={{ backgroundColor: comp.color }} />
            <span className="capitalize">{comp.id.replace("-", " ")}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

interface MemoryViewProps {
  ageLevel: AgeLevel;
  onSelectComponent: (id: string) => void;
  activeComponent: string | null;
  isExploded: boolean;
  isPlaying: boolean;
}

function MemoryView({ ageLevel, onSelectComponent, activeComponent, isExploded, isPlaying }: MemoryViewProps) {
  const components = [
    { id: "dram-cell", color: "#3b82f6", label: "Cell", x: 0, y: 0 },
    { id: "dram-cell", color: "#3b82f6", label: "", x: 1, y: 0 },
    { id: "dram-cell", color: "#3b82f6", label: "", x: 2, y: 0 },
    { id: "dram-cell", color: "#3b82f6", label: "", x: 0, y: 1 },
    { id: "dram-cell", color: "#3b82f6", label: "", x: 1, y: 1 },
    { id: "dram-cell", color: "#3b82f6", label: "", x: 2, y: 1 },
    { id: "row-column", color: "#f59e0b", label: "Decoder", x: 3, y: 0, h: 2 },
    { id: "sense-amp", color: "#22c55e", label: "Sense Amp", x: 0, y: 2, w: 3 },
    { id: "refresh", color: "#ef4444", label: "Refresh", x: 3, y: 2 },
  ];

  const [activeCell, setActiveCell] = useState<{ row: number; col: number } | null>(null);

  useEffect(() => {
    if (!isPlaying) return;
    
    const interval = setInterval(() => {
      setActiveCell({
        row: Math.floor(Math.random() * 2),
        col: Math.floor(Math.random() * 3),
      });
    }, 500);
    return () => clearInterval(interval);
  }, [isPlaying]);

  return (
    <div className="relative w-full max-w-2xl mx-auto">
      <motion.div
        animate={isExploded ? { scale: 1.1 } : { scale: 1 }}
        className="relative bg-gradient-to-b from-slate-800/50 to-slate-900/50 rounded-2xl p-4 sm:p-6 border border-slate-700"
      >
        {/* Memory array */}
        <div className="grid grid-cols-4 gap-1 sm:gap-2">
          {/* DRAM cells grid */}
          {[0, 1].map((row) =>
            [0, 1, 2].map((col) => (
              <motion.div
                key={`${row}-${col}`}
                animate={{
                  scale: activeCell?.row === row && activeCell?.col === col ? 1.2 : 1,
                  boxShadow:
                    activeCell?.row === row && activeCell?.col === col
                      ? "0 0 20px rgba(59, 130, 246, 0.5)"
                      : "none",
                }}
                className="aspect-square bg-blue-600/50 border border-blue-400/30 rounded flex items-center justify-center"
              >
                <div className="w-1/2 h-1/2 bg-blue-400/30 rounded-full" />
                <div className="absolute bottom-0 right-0 w-0.5 h-1/2 bg-blue-400/50" />
              </motion.div>
            ))
          )}

          {/* Row/Column decoder */}
          <div
            className="row-span-2 bg-amber-500/50 border border-amber-400/30 rounded flex items-center justify-center"
            onClick={() => onSelectComponent("row-column")}
          >
            <span className="text-[8px] sm:text-[10px] text-amber-200 text-center p-1">
              Row/Col Decoder
            </span>
          </div>

          {/* Sense amplifier */}
          <div
            className="col-span-3 bg-green-500/50 border border-green-400/30 rounded flex items-center justify-center"
            onClick={() => onSelectComponent("sense-amp")}
          >
            <span className="text-xs sm:text-sm text-green-200">Sense Amplifiers</span>
          </div>

          {/* Refresh circuit */}
          <div
            className="bg-red-500/50 border border-red-400/30 rounded flex items-center justify-center"
            onClick={() => onSelectComponent("refresh")}
          >
            <span className="text-[8px] sm:text-[10px] text-red-200 text-center p-1">
              Refresh
            </span>
          </div>
        </div>

        {/* Address bus */}
        <div className="absolute -left-2 top-1/2 transform -translate-y-1/2 -translate-x-full">
          <div className="flex flex-col gap-0.5">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="w-4 h-1 bg-gray-400 rounded-sm" />
            ))}
          </div>
          <span className="text-[8px] text-gray-400 mt-1 block">Addr</span>
        </div>

        {/* Data bus */}
        <div className="absolute -right-2 top-1/2 transform -translate-y-1/2 translate-x-full">
          <div className="flex flex-col gap-0.5">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="w-4 h-1 bg-gray-400 rounded-sm" />
            ))}
          </div>
          <span className="text-[8px] text-gray-400 mt-1 block">Data</span>
        </div>
      </motion.div>

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-2 sm:gap-4 mt-4">
        {[
          { id: "dram-cell", color: "#3b82f6", label: "DRAM Cell" },
          { id: "row-column", color: "#f59e0b", label: "Decoder" },
          { id: "sense-amp", color: "#22c55e", label: "Sense Amp" },
          { id: "refresh", color: "#ef4444", label: "Refresh" },
        ].map((comp) => (
          <button
            key={comp.id}
            onClick={() => onSelectComponent(comp.id)}
            className={`flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1 rounded-lg text-xs sm:text-sm transition-all ${
              activeComponent === comp.id ? "bg-white/10 ring-1 ring-white/30" : "bg-black/20"
            }`}
          >
            <div className="w-2 h-2 sm:w-3 sm:h-3 rounded-sm" style={{ backgroundColor: comp.color }} />
            <span>{comp.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

interface LEDViewProps {
  ageLevel: AgeLevel;
  onSelectComponent: (id: string) => void;
  activeComponent: string | null;
  isExploded: boolean;
  isPlaying: boolean;
}

function LEDView({ ageLevel, onSelectComponent, activeComponent, isExploded, isPlaying }: LEDViewProps) {
  return (
    <div className="relative w-full max-w-2xl mx-auto">
      <motion.div
        animate={isExploded ? { scale: 1.1 } : { scale: 1 }}
        className="relative bg-gradient-to-b from-slate-800/50 to-slate-900/50 rounded-2xl p-6 sm:p-8 border border-slate-700"
      >
        <div className="flex flex-col items-center gap-4">
          {/* LED lens (dome) */}
          <motion.div
            animate={isExploded ? { y: -30 } : { y: 0 }}
            className="w-24 h-24 sm:w-32 sm:h-32 bg-gradient-to-b from-white/20 to-white/5 rounded-full border-2 border-white/30 relative overflow-hidden"
            onClick={() => onSelectComponent("lens")}
          >
            <div className="absolute inset-2 bg-gradient-to-br from-amber-300/30 to-amber-500/20 rounded-full" />
            <div className="absolute inset-4 bg-gradient-to-br from-white/40 to-transparent rounded-full" />
            
            {/* Light rays */}
            {isPlaying && (
              <>
                {Array.from({ length: 8 }).map((_, i) => (
                  <motion.div
                    key={i}
                    className="absolute w-1 h-8 sm:h-12 bg-gradient-to-t from-yellow-400 to-transparent"
                    style={{
                      top: "50%",
                      left: "50%",
                      transformOrigin: "center bottom",
                      transform: `rotate(${i * 45}deg) translateY(-100%)`,
                    }}
                    animate={{ opacity: [0.3, 0.8, 0.3], scaleY: [1, 1.2, 1] }}
                    transition={{ duration: 1, repeat: Infinity, delay: i * 0.1 }}
                  />
                ))}
              </>
            )}
          </motion.div>

          {/* LED chip */}
          <motion.div
            animate={isExploded ? { scale: 1.1 } : { scale: 1 }}
            className="w-12 h-8 sm:w-16 sm:h-10 bg-gradient-to-r from-blue-500/50 via-yellow-500/50 to-red-500/50 rounded border border-white/30 relative"
            onClick={() => onSelectComponent("junction")}
          >
            <div className="absolute inset-1 bg-gradient-to-r from-blue-400/30 to-red-400/30 rounded" />
            
            {/* Photon emission */}
            {isPlaying && (
              <motion.div
                className="absolute -top-2 left-1/2 w-2 h-2 bg-yellow-300 rounded-full"
                animate={{ y: [-5, -20], opacity: [1, 0] }}
                transition={{ duration: 0.5, repeat: Infinity }}
              />
            )}
          </motion.div>

          {/* Terminals */}
          <div className="flex gap-8 sm:gap-12">
            <motion.div
              animate={isExploded ? { x: -20, y: 20 } : { x: 0, y: 0 }}
              className="flex flex-col items-center"
              onClick={() => onSelectComponent("anode")}
            >
              <div className="w-3 h-16 sm:w-4 sm:h-20 bg-gradient-to-b from-gray-400 to-gray-500 rounded-b" />
              <span className="text-[10px] sm:text-xs text-gray-400 mt-1">+ Anode</span>
            </motion.div>
            <motion.div
              animate={isExploded ? { x: 20, y: 20 } : { x: 0, y: 0 }}
              className="flex flex-col items-center"
              onClick={() => onSelectComponent("cathode")}
            >
              <div className="w-3 h-20 sm:w-4 sm:h-24 bg-gradient-to-b from-gray-400 to-gray-500 rounded-b" />
              <span className="text-[10px] sm:text-xs text-gray-400 mt-1">- Cathode</span>
            </motion.div>
          </div>
        </div>

        {/* Electron flow animation */}
        {isPlaying && (
          <motion.div className="absolute inset-0 pointer-events-none">
            <motion.div
              className="absolute w-2 h-2 bg-blue-400 rounded-full"
              style={{ bottom: "30%", left: "35%" }}
              animate={{ x: [0, 60], opacity: [0, 1, 1, 0] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            />
            <motion.div
              className="absolute w-2 h-2 bg-red-400 rounded-full"
              style={{ bottom: "30%", right: "35%" }}
              animate={{ x: [0, -60], opacity: [0, 1, 1, 0] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: 0.5 }}
            />
          </motion.div>
        )}
      </motion.div>

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-2 sm:gap-4 mt-4">
        {[
          { id: "anode", color: "#3b82f6", label: "Anode (+)" },
          { id: "cathode", color: "#ef4444", label: "Cathode (-)" },
          { id: "junction", color: "#f59e0b", label: "P-N Junction" },
          { id: "lens", color: "#ffffff", label: "Lens" },
        ].map((comp) => (
          <button
            key={comp.id}
            onClick={() => onSelectComponent(comp.id)}
            className={`flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1 rounded-lg text-xs sm:text-sm transition-all ${
              activeComponent === comp.id ? "bg-white/10 ring-1 ring-white/30" : "bg-black/20"
            }`}
          >
            <div className="w-2 h-2 sm:w-3 sm:h-3 rounded-full border" style={{ backgroundColor: comp.color === "#ffffff" ? "transparent" : comp.color, borderColor: comp.color }} />
            <span>{comp.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

interface CircuitBoardViewProps {
  ageLevel: AgeLevel;
  onSelectComponent: (id: string) => void;
  activeComponent: string | null;
  isExploded: boolean;
  isPlaying: boolean;
}

function CircuitBoardView({ ageLevel, onSelectComponent, activeComponent, isExploded, isPlaying }: CircuitBoardViewProps) {
  return (
    <div className="relative w-full max-w-2xl mx-auto">
      <motion.div
        animate={isExploded ? { scale: 1.05 } : { scale: 1 }}
        className="relative bg-gradient-to-b from-emerald-900/30 to-emerald-950/50 rounded-2xl p-4 sm:p-6 border border-emerald-700/50"
      >
        {/* Board substrate */}
        <div className="absolute inset-2 bg-emerald-800/20 rounded-lg" />

        {/* Multiple layers */}
        {isExploded && (
          <>
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 0.3, y: -20 }}
              className="absolute inset-4 bg-amber-500/20 rounded border border-amber-500/30"
            >
              <span className="text-[8px] text-amber-400 absolute top-1 left-2">Layer 3 - Power</span>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 0.3, y: -10 }}
              className="absolute inset-4 bg-blue-500/20 rounded border border-blue-500/30"
              style={{ top: 0 }}
            >
              <span className="text-[8px] text-blue-400 absolute top-1 left-2">Layer 2 - Ground</span>
            </motion.div>
          </>
        )}

        {/* Traces */}
        <div className="relative grid grid-cols-8 gap-0.5 sm:gap-1 p-2 sm:p-4">
          {/* Horizontal traces */}
          {[0, 1, 2, 3, 4].map((row) => (
            <div key={`h-${row}`} className="col-span-8 h-1 sm:h-1.5 bg-gradient-to-r from-amber-500/50 via-amber-500 to-amber-500/50 rounded-full my-2 sm:my-3" />
          ))}
        </div>

        {/* Vertical traces */}
        <div className="absolute inset-4 grid grid-cols-6 gap-2 sm:gap-4 pointer-events-none">
          {[0, 1, 2, 3, 4, 5].map((col) => (
            <div key={`v-${col}`} className="w-0.5 sm:w-1 h-full bg-gradient-to-b from-amber-500/50 via-amber-500 to-amber-500/50 rounded-full" />
          ))}
        </div>

        {/* Components */}
        <div className="absolute top-8 sm:top-12 left-8 sm:left-12">
          <motion.div
            whileHover={{ scale: 1.1 }}
            onClick={() => onSelectComponent("components")}
            className={`w-8 h-4 sm:w-12 sm:h-6 bg-gray-700 border border-gray-500 rounded-sm flex items-center justify-center ${activeComponent === "components" ? "ring-2 ring-white/50" : ""}`}
          >
            <span className="text-[6px] sm:text-[8px] text-gray-300">IC</span>
          </motion.div>
        </div>

        <div className="absolute top-8 sm:top-12 right-8 sm:right-12">
          <motion.div
            whileHover={{ scale: 1.1 }}
            onClick={() => onSelectComponent("components")}
            className={`w-3 h-5 sm:w-4 sm:h-8 bg-gradient-to-b from-blue-400 to-blue-600 rounded-sm ${activeComponent === "components" ? "ring-2 ring-white/50" : ""}`}
          />
        </div>

        <div className="absolute bottom-8 sm:bottom-12 left-1/3">
          <motion.div
            whileHover={{ scale: 1.1 }}
            onClick={() => onSelectComponent("components")}
            className={`w-2 h-3 sm:w-3 sm:h-4 bg-gradient-to-b from-red-400 to-red-600 rounded-sm ${activeComponent === "components" ? "ring-2 ring-white/50" : ""}`}
          />
        </div>

        {/* Vias */}
        <div className="absolute top-1/4 left-1/4 w-2 h-2 sm:w-3 sm:h-3 bg-gray-400 rounded-full border border-gray-500" />
        <div className="absolute top-3/4 right-1/4 w-2 h-2 sm:w-3 sm:h-3 bg-gray-400 rounded-full border border-gray-500" />
        <div className="absolute bottom-1/4 left-1/3 w-2 h-2 sm:w-3 sm:h-3 bg-gray-400 rounded-full border border-gray-500" />

        {/* Signal animation */}
        {isPlaying && (
          <motion.div
            className="absolute w-2 h-2 bg-green-400 rounded-full"
            animate={{
              x: ["0%", "80%", "80%", "0%"],
              y: ["20%", "20%", "80%", "80%"],
            }}
            transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
          />
        )}
      </motion.div>

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-2 sm:gap-4 mt-4">
        {[
          { id: "traces", color: "#f59e0b", label: "Traces" },
          { id: "layers", color: "#3b82f6", label: "Layers" },
          { id: "vias", color: "#9ca3af", label: "Vias" },
          { id: "components", color: "#6b7280", label: "Components" },
        ].map((comp) => (
          <button
            key={comp.id}
            onClick={() => onSelectComponent(comp.id)}
            className={`flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1 rounded-lg text-xs sm:text-sm transition-all ${
              activeComponent === comp.id ? "bg-white/10 ring-1 ring-white/30" : "bg-black/20"
            }`}
          >
            <div className="w-2 h-2 sm:w-3 sm:h-3 rounded-sm" style={{ backgroundColor: comp.color }} />
            <span className="capitalize">{comp.id}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

interface NetworkViewProps {
  ageLevel: AgeLevel;
  onSelectComponent: (id: string) => void;
  activeComponent: string | null;
  isExploded: boolean;
  isPlaying: boolean;
}

function NetworkView({ ageLevel, onSelectComponent, activeComponent, isExploded, isPlaying }: NetworkViewProps) {
  const routers = [
    { id: "r1", x: 20, y: 30 },
    { id: "r2", x: 50, y: 20 },
    { id: "r3", x: 80, y: 30 },
    { id: "r4", x: 35, y: 60 },
    { id: "r5", x: 65, y: 60 },
  ];

  const connections = [
    ["r1", "r2"],
    ["r2", "r3"],
    ["r1", "r4"],
    ["r3", "r5"],
    ["r4", "r5"],
    ["r2", "r4"],
    ["r2", "r5"],
  ];

  const [packetPos, setPacketPos] = useState(0);

  useEffect(() => {
    if (isPlaying) {
      const interval = setInterval(() => {
        setPacketPos((prev) => (prev + 1) % connections.length);
      }, 800);
      return () => clearInterval(interval);
    }
  }, [isPlaying, connections.length]);

  return (
    <div className="relative w-full max-w-2xl mx-auto">
      <motion.div
        animate={isExploded ? { scale: 1.05 } : { scale: 1 }}
        className="relative bg-gradient-to-b from-violet-900/30 to-purple-950/50 rounded-2xl p-4 sm:p-6 border border-violet-700/50 min-h-[300px] sm:min-h-[400px]"
      >
        {/* Network cloud */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute inset-0 bg-gradient-to-br from-violet-500/20 to-purple-500/20 rounded-full blur-3xl" />
        </div>

        {/* Connection lines */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
          {connections.map(([from, to], idx) => {
            const fromRouter = routers.find((r) => r.id === from);
            const toRouter = routers.find((r) => r.id === to);
            if (!fromRouter || !toRouter) return null;

            const isActive = idx === packetPos;

            return (
              <motion.line
                key={`${from}-${to}`}
                x1={fromRouter.x}
                y1={fromRouter.y}
                x2={toRouter.x}
                y2={toRouter.y}
                stroke={isActive ? "#22c55e" : "#8b5cf6"}
                strokeWidth={isActive ? "0.8" : "0.3"}
                strokeDasharray="2,2"
                animate={isActive ? { opacity: [0.5, 1, 0.5] } : { opacity: 0.5 }}
                transition={{ duration: 0.5, repeat: isActive ? Infinity : 0 }}
              />
            );
          })}
        </svg>

        {/* Routers */}
        {routers.map((router) => (
          <motion.div
            key={router.id}
            className="absolute w-10 h-10 sm:w-14 sm:h-14 bg-violet-600/50 border border-violet-400/50 rounded-lg flex items-center justify-center cursor-pointer"
            style={{ left: `${router.x}%`, top: `${router.y}%`, transform: "translate(-50%, -50%)" }}
            whileHover={{ scale: 1.2 }}
            onClick={() => onSelectComponent("routing-table")}
          >
            <span className="text-lg sm:text-xl">🚦</span>
          </motion.div>
        ))}

        {/* Packet animation */}
        {isPlaying && (
          <motion.div
            className="absolute w-4 h-4 sm:w-6 sm:h-6 bg-blue-500 rounded border border-blue-300 flex items-center justify-center"
            style={{
              left: `${(routers.find((r) => r.id === connections[packetPos]?.[0])?.x || 0)}%`,
              top: `${(routers.find((r) => r.id === connections[packetPos]?.[0])?.y || 0)}%`,
            }}
            animate={{
              left: [
                `${routers.find((r) => r.id === connections[packetPos]?.[0])?.x || 0}%`,
                `${routers.find((r) => r.id === connections[packetPos]?.[1])?.x || 0}%`,
              ],
              top: [
                `${routers.find((r) => r.id === connections[packetPos]?.[0])?.y || 0}%`,
                `${routers.find((r) => r.id === connections[packetPos]?.[1])?.y || 0}%`,
              ],
            }}
            transition={{ duration: 0.7, ease: "linear" }}
          >
            <span className="text-[8px] sm:text-xs">📦</span>
          </motion.div>
        )}

        {/* Client/Server icons */}
        <div className="absolute bottom-4 left-4 w-8 h-8 sm:w-10 sm:h-10 bg-blue-600/50 border border-blue-400/50 rounded flex items-center justify-center">
          <span className="text-sm sm:text-base">💻</span>
        </div>
        <div className="absolute bottom-4 right-4 w-8 h-8 sm:w-10 sm:h-10 bg-green-600/50 border border-green-400/50 rounded flex items-center justify-center">
          <span className="text-sm sm:text-base">🖥️</span>
        </div>
      </motion.div>

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-2 sm:gap-4 mt-4">
        {[
          { id: "packet", color: "#3b82f6", label: "Packet" },
          { id: "routing-table", color: "#8b5cf6", label: "Router" },
          { id: "protocol", color: "#22c55e", label: "Protocol" },
          { id: "latency", color: "#f59e0b", label: "Latency" },
        ].map((comp) => (
          <button
            key={comp.id}
            onClick={() => onSelectComponent(comp.id)}
            className={`flex items-center gap-1 sm:gap-2 px-2 sm:px-3 py-1 rounded-lg text-xs sm:text-sm transition-all ${
              activeComponent === comp.id ? "bg-white/10 ring-1 ring-white/30" : "bg-black/20"
            }`}
          >
            <div className="w-2 h-2 sm:w-3 sm:h-3 rounded-sm" style={{ backgroundColor: comp.color }} />
            <span className="capitalize">{comp.id}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function VoxelExplorerPage() {
  const [ageLevel, setAgeLevel] = useState<AgeLevel>("elementary");
  const [selectedModule, setSelectedModule] = useState<ContentModule | null>(null);
  const [activeComponent, setActiveComponent] = useState<string | null>(null);
  const [isExploded, setIsExploded] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showCharacterPanel, setShowCharacterPanel] = useState(true);
  const [progress, setProgress] = useState(0);

  // Get current module characters
  const currentCharacters = selectedModule?.characters || [];

  // Handle component selection
  const handleSelectComponent = useCallback((id: string) => {
    setActiveComponent(id);
  }, []);

  // Get component info for current selection
  const getComponentInfo = useCallback((): ComponentInfo | null => {
    if (!selectedModule || !activeComponent) return null;
    return selectedModule.components.find((c) => c.id === activeComponent) || null;
  }, [selectedModule, activeComponent]);

  // Render the appropriate visualization
  const renderVisualization = useCallback(() => {
    if (!selectedModule) return null;

    const props = {
      ageLevel,
      onSelectComponent: handleSelectComponent,
      activeComponent,
      isExploded,
      isPlaying,
    };

    switch (selectedModule.id) {
      case "transistor":
        return <TransistorView {...props} />;
      case "cpu":
        return <CPUView {...props} />;
      case "memory":
        return <MemoryView {...props} />;
      case "led":
        return <LEDView {...props} />;
      case "circuit":
        return <CircuitBoardView {...props} />;
      case "network":
        return <NetworkView {...props} />;
      default:
        return <TransistorView {...props} />;
    }
  }, [selectedModule, ageLevel, handleSelectComponent, activeComponent, isExploded, isPlaying]);

  // Update progress when module changes
  useEffect(() => {
    if (!selectedModule) return;
    
    // Reset progress when module changes
    let currentProgress = 0;
    const interval = setInterval(() => {
      currentProgress = Math.min(currentProgress + 5, 100);
      setProgress(currentProgress);
    }, 500);
    return () => clearInterval(interval);
  }, [selectedModule]);

  return (
    <div className="min-h-screen bg-background text-foreground overflow-x-hidden">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-md border-b border-border">
        <div className="max-w-7xl mx-auto px-4 py-3 sm:py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                <Box className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg sm:text-xl font-bold gradient-text">Lucineer</h1>
                <p className="text-[10px] sm:text-xs text-muted-foreground">Voxel Explorer</p>
              </div>
            </div>

            {/* Age Level Selector */}
            <div className="flex items-center gap-1 sm:gap-2">
              {(Object.keys(AGE_CONFIGS) as AgeLevel[]).map((level) => {
                const config = AGE_CONFIGS[level];
                const Icon = config.icon;
                return (
                  <button
                    key={level}
                    onClick={() => setAgeLevel(level)}
                    className={`
                      px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg text-xs sm:text-sm font-medium
                      transition-all duration-200 flex items-center gap-1 sm:gap-2
                      ${ageLevel === level 
                        ? `${config.bgColor} border ${config.borderColor} ${config.color}` 
                        : "bg-muted/50 text-muted-foreground hover:bg-muted"
                      }
                    `}
                  >
                    <Icon className="w-3 h-3 sm:w-4 sm:h-4" />
                    <span className="hidden sm:inline">{config.label}</span>
                    <span className="sm:hidden">{config.ages.split("-")[0].replace("Ages ", "")}+</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-4 sm:py-6">
        <AnimatePresence mode="wait">
          {!selectedModule ? (
            // Module Selection View
            <motion.div
              key="module-select"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6 sm:space-y-8"
            >
              {/* Welcome Section */}
              <div className="text-center space-y-2 sm:space-y-4">
                <motion.h2
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-2xl sm:text-3xl md:text-4xl font-bold"
                >
                  <span className="gradient-text">Explore Technology</span>
                  <span className="text-foreground"> from the Inside!</span>
                </motion.h2>
                <motion.p
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.1 }}
                  className="text-sm sm:text-base text-muted-foreground max-w-2xl mx-auto"
                >
                  {AGE_CONFIGS[ageLevel].description} Click on a module to start your journey through
                  the amazing world of technology!
                </motion.p>
              </div>

              {/* Character Preview */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="flex flex-wrap justify-center gap-2 sm:gap-4"
              >
                {Object.values(CHARACTERS).slice(0, 5).map((char, idx) => (
                  <motion.div
                    key={char.id}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 + idx * 0.1 }}
                    className="flex flex-col items-center gap-1"
                  >
                    <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-xl ${char.bgColor} border border-current/20 flex items-center justify-center text-xl sm:text-2xl ${char.color}`}>
                      {char.emoji}
                    </div>
                    <span className="text-[10px] sm:text-xs text-muted-foreground">{char.name}</span>
                  </motion.div>
                ))}
              </motion.div>

              {/* Module Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
                {CONTENT_MODULES.map((module, idx) => {
                  const Icon = module.icon;
                  return (
                    <motion.div
                      key={module.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 + idx * 0.1 }}
                      whileHover={{ scale: 1.02, y: -5 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setSelectedModule(module)}
                      className={`relative overflow-hidden rounded-xl border border-border bg-gradient-to-br ${module.gradient} p-4 sm:p-6 cursor-pointer group`}
                    >
                      {/* Background decoration */}
                      <div className="absolute inset-0 opacity-5">
                        <Grid3X3 className="absolute right-0 bottom-0 w-32 h-32 sm:w-48 sm:h-48 transform rotate-12" />
                      </div>

                      <div className="relative space-y-3 sm:space-y-4">
                        {/* Icon */}
                        <div className={`w-12 h-12 sm:w-14 sm:h-14 rounded-xl ${module.color} bg-current/10 flex items-center justify-center`}>
                          <Icon className="w-6 h-6 sm:w-7 sm:h-7" />
                        </div>

                        {/* Title */}
                        <div>
                          <h3 className="text-lg sm:text-xl font-bold">{module.title}</h3>
                          <p className="text-xs sm:text-sm text-muted-foreground">{module.subtitle}</p>
                        </div>

                        {/* Characters */}
                        <div className="flex -space-x-2">
                          {module.characters.slice(0, 3).map((char) => (
                            <div
                              key={char.id}
                              className={`w-7 h-7 sm:w-8 sm:h-8 rounded-full ${char.bgColor} border-2 border-background flex items-center justify-center text-sm sm:text-base`}
                            >
                              {char.emoji}
                            </div>
                          ))}
                          {module.characters.length > 3 && (
                            <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-muted border-2 border-background flex items-center justify-center text-[10px] sm:text-xs">
                              +{module.characters.length - 3}
                            </div>
                          )}
                        </div>

                        {/* Fun fact preview */}
                        <p className="text-xs sm:text-sm text-muted-foreground italic">
                          &ldquo;{module.funFacts[ageLevel][0]}&rdquo;
                        </p>

                        {/* Click hint */}
                        <div className="flex items-center gap-1 text-xs text-muted-foreground group-hover:text-foreground transition-colors">
                          <Play className="w-3 h-3 sm:w-4 sm:h-4" />
                          <span>Click to explore</span>
                          <ChevronRight className="w-3 h-3 sm:w-4 sm:h-4 ml-auto" />
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          ) : (
            // Module Exploration View
            <motion.div
              key="module-explore"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-4 sm:space-y-6"
            >
              {/* Module Header */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <button
                  onClick={() => {
                    setSelectedModule(null);
                    setActiveComponent(null);
                    setIsExploded(false);
                    setIsPlaying(false);
                  }}
                  className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
                >
                  <ChevronRight className="w-4 h-4 transform rotate-180" />
                  Back to Modules
                </button>

                <div className="flex items-center gap-2 sm:gap-3">
                  {/* Progress */}
                  <div className="w-20 sm:w-32">
                    <Progress value={progress} className="h-1 sm:h-2" />
                  </div>
                  <Badge variant="outline" className="text-[10px] sm:text-xs">
                    {AGE_CONFIGS[ageLevel].ages}
                  </Badge>
                </div>
              </div>

              {/* Title Section */}
              <div className="flex items-center gap-3 sm:gap-4">
                <div className={`w-12 h-12 sm:w-16 sm:h-16 rounded-xl ${selectedModule.color} bg-current/10 flex items-center justify-center`}>
                  <selectedModule.icon className="w-6 h-6 sm:w-8 sm:h-8" />
                </div>
                <div>
                  <h2 className="text-xl sm:text-2xl md:text-3xl font-bold">{selectedModule.title}</h2>
                  <p className="text-sm sm:text-base text-muted-foreground">{selectedModule.subtitle}</p>
                </div>
              </div>

              {/* Main Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 sm:gap-6">
                {/* Visualization Panel */}
                <div className="lg:col-span-2 space-y-4">
                  {/* Controls */}
                  <div className="flex flex-wrap items-center gap-2 sm:gap-3">
                    <Button
                      variant={isPlaying ? "default" : "outline"}
                      size="sm"
                      onClick={() => setIsPlaying(!isPlaying)}
                      className="gap-2"
                    >
                      {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                      {isPlaying ? "Pause" : "Play"}
                    </Button>
                    <Button
                      variant={isExploded ? "default" : "outline"}
                      size="sm"
                      onClick={() => setIsExploded(!isExploded)}
                      className="gap-2"
                    >
                      <Layers className="w-4 h-4" />
                      {isExploded ? "Collapse" : "Explode"}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setActiveComponent(null)}
                      className="gap-2"
                    >
                      <RotateCcw className="w-4 h-4" />
                      Reset
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setShowCharacterPanel(!showCharacterPanel)}
                      className="gap-2 ml-auto"
                    >
                      {showCharacterPanel ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
                      {showCharacterPanel ? "Characters On" : "Characters Off"}
                    </Button>
                  </div>

                  {/* Cross-section View */}
                  <Card className="p-2 sm:p-4 border-border">
                    {renderVisualization()}
                  </Card>

                  {/* Component Info */}
                  <AnimatePresence mode="wait">
                    {activeComponent && getComponentInfo() && (
                      <motion.div
                        key={activeComponent}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="bg-card border border-border rounded-xl p-4"
                      >
                        <h4 className="text-base sm:text-lg font-semibold mb-2 capitalize">
                          {activeComponent.replace("-", " ")}
                        </h4>
                        <p className="text-sm text-muted-foreground mb-3">
                          {getComponentInfo()?.description[ageLevel]}
                        </p>
                        <ul className="space-y-1">
                          {getComponentInfo()?.details[ageLevel].map((detail, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-xs sm:text-sm">
                              <ChevronRight className="w-3 h-3 sm:w-4 sm:h-4 mt-0.5 text-primary flex-shrink-0" />
                              <span>{detail}</span>
                            </li>
                          ))}
                        </ul>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                {/* Character Panel */}
                <div className="space-y-4">
                  {/* Characters */}
                  {showCharacterPanel && (
                    <div className="space-y-3 sm:space-y-4">
                      <h3 className="text-base sm:text-lg font-semibold flex items-center gap-2">
                        <Sparkles className="w-4 h-4 sm:w-5 sm:h-5 text-primary" />
                        Your Guides
                      </h3>
                      <div className="space-y-3 sm:space-y-4 max-h-[400px] sm:max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
                        {currentCharacters.map((char, idx) => (
                          <CharacterBubble
                            key={char.id}
                            character={char}
                            ageLevel={ageLevel}
                            position={idx % 2 === 0 ? "left" : "right"}
                            isWalking={isPlaying}
                          />
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Fun Facts */}
                  <div className="bg-card border border-border rounded-xl p-4">
                    <h3 className="text-sm sm:text-base font-semibold mb-3 flex items-center gap-2">
                      <Info className="w-4 h-4 text-primary" />
                      Fun Facts
                    </h3>
                    <ul className="space-y-2">
                      {selectedModule.funFacts[ageLevel].map((fact, idx) => (
                        <motion.li
                          key={idx}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.1 }}
                          className="flex items-start gap-2 text-xs sm:text-sm"
                        >
                          <Star className="w-3 h-3 sm:w-4 sm:h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                          <span>{fact}</span>
                        </motion.li>
                      ))}
                    </ul>
                  </div>

                  {/* Journey Steps */}
                  <div className="bg-card border border-border rounded-xl p-4">
                    <h3 className="text-sm sm:text-base font-semibold mb-3 flex items-center gap-2">
                      <Compass className="w-4 h-4 text-primary" />
                      Journey Steps
                    </h3>
                    <div className="space-y-2">
                      {selectedModule.journey.map((step, idx) => (
                        <motion.div
                          key={step}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.1 }}
                          className="flex items-center gap-2 text-xs sm:text-sm"
                        >
                          <div className="w-5 h-5 sm:w-6 sm:h-6 rounded-full bg-primary/20 text-primary text-[10px] sm:text-xs flex items-center justify-center font-medium">
                            {idx + 1}
                          </div>
                          <span className="capitalize">{step}</span>
                          {idx < selectedModule.journey.length - 1 && (
                            <ArrowRight className="w-3 h-3 text-muted-foreground ml-auto" />
                          )}
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* All Characters Overview */}
              <div className="bg-card border border-border rounded-xl p-4 sm:p-6">
                <h3 className="text-base sm:text-lg font-semibold mb-4">Meet All Characters</h3>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 sm:gap-4">
                  {Object.values(CHARACTERS).map((char) => (
                    <motion.div
                      key={char.id}
                      whileHover={{ scale: 1.05 }}
                      className={`flex flex-col items-center gap-2 p-3 rounded-xl ${char.bgColor} border border-current/10`}
                    >
                      <span className="text-2xl sm:text-3xl">{char.emoji}</span>
                      <div className="text-center">
                        <div className={`font-medium ${char.color}`}>{char.name}</div>
                        <div className="text-[10px] sm:text-xs text-muted-foreground">{char.role}</div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="border-t border-border py-4 sm:py-6 mt-8 sm:mt-12">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-xs sm:text-sm text-muted-foreground">
            Lucineer Voxel Explorer • Inspired by Stephen Biesty&apos;s &ldquo;Incredible Everything&rdquo; and David Macaulay&apos;s &ldquo;The Way Things Work&rdquo;
          </p>
          <p className="text-[10px] sm:text-xs text-muted-foreground mt-1">
            Educational technology exploration for {AGE_CONFIGS[ageLevel].ages}
          </p>
        </div>
      </footer>

      {/* Custom Styles */}
      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(255, 255, 255, 0.3);
        }
      `}</style>
    </div>
  );
}
