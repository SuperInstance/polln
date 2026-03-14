"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Menu,
  X,
  Home,
  BookOpen,
  Clock,
  Cpu,
  Users,
  ChevronDown,
  Sparkles,
  GraduationCap,
  Briefcase,
  Music,
  Brain,
  Layers,
  Factory,
  DollarSign,
  Code2,
  Bot,
  Box,
  Table,
  Hexagon,
  Atom,
  Network,
  Puzzle,
} from "lucide-react";

const navItems = [
  {
    label: "Home",
    href: "/",
    icon: Home,
  },
  {
    label: "Voxel Explorer",
    href: "/voxel-explorer",
    icon: Box,
    description: "Stephen Biesty inspired cross-sections and exploded views",
    highlight: true,
  },
  {
    label: "CRDT Lab",
    href: "/crdt-lab",
    icon: Atom,
    description: "Conflict-free replicated data types simulation",
    highlight: true,
  },
  {
    label: "LLN Playground",
    href: "/lln-playground",
    icon: Network,
    description: "Large Language Networks - agents learning through play",
    highlight: true,
  },
  {
    label: "LLN Tiles",
    href: "/lln-tiles",
    icon: Puzzle,
    description: "Tile-based programming for LLN - visual agent builder",
    highlight: true,
  },
  {
    label: "Agent Cells",
    href: "/agent-cells",
    icon: Layers,
    description: "Hierarchical real-time AI with confidence-based autonomy",
    highlight: true,
  },
  {
    label: "Cell Builder",
    href: "/cell-builder",
    icon: Table,
    description: "Spreadsheet AI - build neural networks in cells",
    highlight: true,
  },
  {
    label: "Tile Intelligence",
    href: "/tile-intelligence",
    icon: Box,
    description: "POLLN Tile concepts - inspectable AI",
    highlight: true,
  },
  {
    label: "Mist Game",
    href: "/mist",
    icon: Sparkles,
    description: "Sheepdog puppy adventure for ages 5-10",
    highlight: true,
  },
  {
    label: "Math Universe",
    href: "/math-universe",
    icon: Hexagon,
    description: "Interactive math visualizations for AI & humans",
    highlight: true,
  },
  {
    label: "RTL Studio",
    href: "/rtl-studio",
    icon: Code2,
    description: "RTL to GDSII design flow",
    highlight: true,
  },
  {
    label: "Manufacturing",
    href: "/manufacturing",
    icon: Factory,
    description: "From sand to silicon - fab floor walkthrough",
    highlight: true,
  },
  {
    label: "Chip Studio",
    href: "/professional",
    icon: Cpu,
    description: "Design inference chips",
    subItems: [
      { label: "Design Studio", href: "/professional#design" },
      { label: "CDC Visualization", href: "/professional#cdc" },
      { label: "Pipeline Designer", href: "/professional#pipeline" },
      { label: "Resource Calculator", href: "/professional#calculator" },
    ],
  },
  {
    label: "Economics",
    href: "/economics",
    icon: DollarSign,
    description: "Market simulation and pricing",
  },
  {
    label: "Specs",
    href: "/specs",
    icon: GraduationCap,
    description: "Technical specifications and math",
  },
  {
    label: "Music",
    href: "/music",
    icon: Music,
    description: "Generative MIDI playground",
  },
  {
    label: "Tabula Rosa",
    href: "/tabula-rosa",
    icon: Brain,
    description: "Specialist model research",
  },
  {
    label: "Learning",
    href: "/learning",
    icon: BookOpen,
    description: "Interactive educational content",
  },
  {
    label: "About",
    href: "/about",
    icon: Users,
  },
];

const ageGroups = [
  {
    label: "Young Learners",
    href: "/learning?age=young",
    icon: Sparkles,
    color: "text-green-400",
    age: "Ages 5-10",
  },
  {
    label: "Middle School",
    href: "/learning?age=middle",
    icon: GraduationCap,
    color: "text-blue-400",
    age: "Ages 11-14",
  },
  {
    label: "High School",
    href: "/learning?age=high",
    icon: BookOpen,
    color: "text-amber-400",
    age: "Ages 15-18",
  },
  {
    label: "Professional",
    href: "/professional",
    icon: Briefcase,
    color: "text-purple-400",
    age: "18+",
  },
];

export default function Navigation() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const pathname = usePathname();

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/95 backdrop-blur-md border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <motion.div
              className="relative w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Cpu className="text-primary-foreground w-5 h-5" />
              <div className="absolute inset-0 rounded-xl bg-primary/20 animate-ping" style={{ animationDuration: '3s' }} />
            </motion.div>
            <div className="flex flex-col">
              <span className="font-bold text-lg gradient-text">Lucineer</span>
              <span className="text-xs text-muted-foreground hidden sm:block">Inference Chip Platform</span>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center gap-1">
            {navItems.map((item) => (
              <div
                key={item.label}
                className="relative"
                onMouseEnter={() => item.subItems && setActiveDropdown(item.label)}
                onMouseLeave={() => setActiveDropdown(null)}
              >
                <Link
                  href={item.href}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                    pathname === item.href
                      ? "text-primary bg-primary/10"
                      : "text-muted-foreground hover:text-foreground hover:bg-muted"
                  }`}
                >
                  <item.icon className="w-4 h-4" />
                  <span className="font-medium">{item.label}</span>
                  {item.subItems && <ChevronDown className="w-3 h-3" />}
                </Link>

                {/* Dropdown */}
                <AnimatePresence>
                  {activeDropdown === item.label && item.subItems && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: 10 }}
                      transition={{ duration: 0.15 }}
                      className="absolute top-full left-0 mt-2 w-56 bg-card rounded-xl shadow-xl border border-border overflow-hidden"
                    >
                      <div className="p-3 border-b border-border bg-muted/50">
                        <p className="text-xs text-muted-foreground">
                          {item.description}
                        </p>
                      </div>
                      <div className="py-1">
                        {item.subItems.map((subItem) => (
                          <Link
                            key={subItem.label}
                            href={subItem.href}
                            className="block px-4 py-2.5 text-sm text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
                          >
                            {subItem.label}
                          </Link>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>

          {/* Age Group Pills - Desktop */}
          <div className="hidden lg:flex items-center gap-2">
            {ageGroups.map((group) => (
              <Link
                key={group.label}
                href={group.href}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all duration-200 hover:scale-105 ${
                  group.color
                } border-current/30 hover:border-current bg-current/5`}
              >
                <group.icon className="w-3 h-3" />
                <span className="hidden xl:inline">{group.age}</span>
              </Link>
            ))}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="lg:hidden p-2 text-muted-foreground hover:text-foreground transition-colors"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="lg:hidden bg-card border-t border-border overflow-hidden"
          >
            <div className="px-4 py-4 space-y-2">
              {navItems.map((item) => (
                <div key={item.label}>
                  <Link
                    href={item.href}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      pathname === item.href
                        ? "text-primary bg-primary/10"
                        : "text-muted-foreground hover:text-foreground hover:bg-muted"
                    }`}
                    onClick={() => setIsOpen(false)}
                  >
                    <item.icon className="w-5 h-5" />
                    <span className="font-medium">{item.label}</span>
                  </Link>
                  {item.subItems && (
                    <div className="ml-8 mt-1 space-y-1">
                      {item.subItems.map((subItem) => (
                        <Link
                          key={subItem.label}
                          href={subItem.href}
                          className="block px-4 py-2 text-sm text-muted-foreground hover:text-foreground"
                          onClick={() => setIsOpen(false)}
                        >
                          {subItem.label}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}

              {/* Mobile Age Groups */}
              <div className="border-t border-border pt-4 mt-4">
                <p className="px-4 text-xs text-muted-foreground mb-2 uppercase tracking-wider">
                  Age Groups
                </p>
                <div className="grid grid-cols-2 gap-2 px-2">
                  {ageGroups.map((group) => (
                    <Link
                      key={group.label}
                      href={group.href}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm ${group.color} bg-current/5 border border-current/20`}
                      onClick={() => setIsOpen(false)}
                    >
                      <group.icon className="w-4 h-4" />
                      <span>{group.label}</span>
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
