"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import { 
  Menu, X, Cpu, Zap, ChevronDown, Download, Settings, BookOpen, 
  Users, Clock, Code, ArrowRight, ExternalLink, Wand2, Lock
} from "lucide-react";

const navItems = [
  { 
    name: "Learn", 
    href: "/learning",
    icon: BookOpen,
    children: [
      { name: "Young Learners (4-10)", href: "/learning?age=young", color: "blue" },
      { name: "Middle School (11-14)", href: "/learning?age=middle", color: "purple" },
      { name: "High School (15-18)", href: "/learning?age=high", color: "amber" },
      { name: "Professional (18+)", href: "/learning?age=pro", color: "green" },
    ]
  },
  { name: "TernaryAir", href: "/ternaryair", icon: Lock },
  { name: "Playground", href: "/timing-playground", icon: Clock },
  { name: "Connect AI", href: "/api-connect", icon: Zap },
  { name: "Downloads", href: "/downloads", icon: Download },
  { name: "Research", href: "/research", icon: BookOpen },
];

export default function Navigation() {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const pathname = usePathname();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav 
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled 
          ? "bg-dark-900/95 backdrop-blur-lg border-b border-dark-700 shadow-lg" 
          : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 md:h-20">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative w-10 h-10 md:w-12 md:h-12">
              <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 animate-pulse-slow" />
              <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center group-hover:shadow-lg group-hover:shadow-green-500/25 transition-shadow">
                <Wand2 className="w-5 h-5 md:w-6 md:h-6 text-white" />
              </div>
            </div>
            <div className="hidden sm:block">
              <span className="text-xl md:text-2xl font-bold gradient-text">Lucineer</span>
              <p className="text-[10px] text-gray-500 -mt-1">Become a Lucineer</p>
            </div>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center gap-1">
            {navItems.map((item) => (
              <div 
                key={item.name}
                className="relative"
                onMouseEnter={() => item.children && setActiveDropdown(item.name)}
                onMouseLeave={() => setActiveDropdown(null)}
              >
                <Link
                  href={item.href}
                  className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                    pathname === item.href || pathname.startsWith(item.href + "/")
                      ? item.name === "TernaryAir" 
                        ? "bg-green-500/10 text-green-400"
                        : "bg-green-500/10 text-green-400"
                      : item.name === "TernaryAir"
                        ? "text-green-400 hover:text-green-300 hover:bg-dark-700/50"
                        : "text-gray-400 hover:text-white hover:bg-dark-700/50"
                  }`}
                >
                  {item.icon && <item.icon className="w-4 h-4" />}
                  {item.name}
                  {item.children && <ChevronDown className="w-3 h-3" />}
                </Link>
                
                {/* Dropdown */}
                {item.children && activeDropdown === item.name && (
                  <div className="absolute top-full left-0 mt-1 w-56 py-2 bg-dark-800/95 backdrop-blur-lg rounded-xl border border-dark-600 shadow-xl animate-fade-in">
                    {item.children.map((child) => (
                      <Link
                        key={child.name}
                        href={child.href}
                        className={`flex items-center gap-2 px-4 py-2.5 text-sm hover:bg-dark-700/50 transition-colors ${
                          child.color === "blue" ? "text-blue-400 hover:text-blue-300" :
                          child.color === "purple" ? "text-purple-400 hover:text-purple-300" :
                          child.color === "amber" ? "text-amber-400 hover:text-amber-300" :
                          "text-green-400 hover:text-green-300"
                        }`}
                      >
                        <ArrowRight className="w-3 h-3" />
                        {child.name}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Right Side Actions */}
          <div className="hidden lg:flex items-center gap-3">
            <Link
              href="/settings"
              className="p-2.5 rounded-lg text-gray-400 hover:text-white hover:bg-dark-700/50 transition-all"
            >
              <Settings className="w-5 h-5" />
            </Link>
            <Link
              href="/ternaryair"
              className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-5 py-2.5 rounded-xl font-medium transition-all text-sm shadow-lg hover:shadow-green-500/25"
            >
              <Cpu className="w-4 h-4" />
              Open TernaryAir
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="lg:hidden p-2 rounded-lg text-gray-400 hover:text-white hover:bg-dark-700/50 transition-colors"
            aria-label="Toggle menu"
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="lg:hidden bg-dark-900/98 backdrop-blur-lg border-t border-dark-700 animate-slide-down">
          <div className="px-4 py-6 space-y-2">
            {navItems.map((item) => (
              <div key={item.name}>
                <Link
                  href={item.href}
                  onClick={() => !item.children && setIsOpen(false)}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl text-base font-medium transition-all ${
                    pathname === item.href
                      ? item.name === "TernaryAir"
                        ? "bg-green-500/10 text-green-400"
                        : "bg-green-500/10 text-green-400"
                      : item.name === "TernaryAir"
                        ? "text-green-400"
                        : "text-gray-300 hover:text-white hover:bg-dark-700/50"
                  }`}
                >
                  {item.icon && <item.icon className="w-5 h-5" />}
                  {item.name}
                </Link>
                {item.children && (
                  <div className="ml-4 mt-1 space-y-1">
                    {item.children.map((child) => (
                      <Link
                        key={child.name}
                        href={child.href}
                        onClick={() => setIsOpen(false)}
                        className="flex items-center gap-2 px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors"
                      >
                        <ArrowRight className="w-3 h-3" />
                        {child.name}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
            <div className="pt-4 border-t border-dark-700">
              <Link
                href="/ternaryair"
                onClick={() => setIsOpen(false)}
                className="flex items-center justify-center gap-2 w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white px-5 py-3 rounded-xl font-medium transition-all"
              >
                <Cpu className="w-5 h-5" />
                Open TernaryAir Studio
              </Link>
            </div>
          </div>
        </div>
      )}
    </nav>
  );
}
