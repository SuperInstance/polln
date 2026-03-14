"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  ChevronDown,
  Download,
  Shield,
  Cpu,
  Code,
  Users,
  BookOpen,
  Menu,
  X,
  Fish,
} from "lucide-react";

export default function Navigation() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);
  const [scrolled, setScrolled] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    setIsOpen(false);
  }, [pathname]);

  const navItems = [
    {
      label: "Users",
      href: "/users",
      color: "user",
      icon: Users,
      description: "Non-technical guide to TernaryAir",
      subItems: [
        { label: "What is TernaryAir?", href: "/users#what-is" },
        { label: "Why It Matters", href: "/users#why-matters" },
        { label: "Use Cases", href: "/users#use-cases" },
        { label: "Privacy & Security", href: "/users#privacy" },
      ],
    },
    {
      label: "Developers",
      href: "/developers",
      color: "developer",
      icon: Code,
      description: "SDK documentation and API",
      subItems: [
        { label: "Quick Start", href: "/developers#quick-start" },
        { label: "API Reference", href: "/developers#api" },
        { label: "Examples", href: "/developers#examples" },
        { label: "Python SDK", href: "/developers#sdk" },
      ],
    },
    {
      label: "Engineers",
      href: "/engineers",
      color: "engineer",
      icon: Cpu,
      description: "RTL and hardware design",
      subItems: [
        { label: "Architecture", href: "/engineers#architecture" },
        { label: "RTL Source", href: "/engineers#rtl" },
        { label: "FPGA Prototyping", href: "/engineers#fpga" },
        { label: "Silicon Design", href: "/engineers#silicon" },
      ],
    },
  ];

  const getColorClasses = (color: string, isHover = false) => {
    const colors: Record<string, string> = {
      user: isHover ? "text-blue-400" : "text-blue-400",
      developer: isHover ? "text-purple-400" : "text-purple-400",
      engineer: isHover ? "text-amber-400" : "text-amber-400",
      primary: isHover ? "text-green-300" : "text-green-400",
    };
    return colors[color] || colors.primary;
  };

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-dark-900/98 backdrop-blur-md border-b border-dark-600 shadow-lg"
          : "bg-dark-900/95 backdrop-blur-sm border-b border-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-green-500/20 group-hover:shadow-green-500/40 transition-shadow">
              <span className="text-white font-bold text-sm">T</span>
            </div>
            <span className="font-bold text-xl">
              <span className="gradient-text">TernaryAir</span>
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => (
              <div
                key={item.label}
                className="relative"
                onMouseEnter={() => setActiveDropdown(item.label)}
                onMouseLeave={() => setActiveDropdown(null)}
              >
                <Link
                  href={item.href}
                  className={`flex items-center gap-1.5 px-4 py-2 rounded-lg transition-all hover:bg-dark-700/50 ${getColorClasses(
                    item.color
                  )}`}
                >
                  <item.icon className="w-4 h-4" />
                  {item.label}
                  <ChevronDown className="w-3 h-3 opacity-50" />
                </Link>

                {/* Dropdown */}
                {activeDropdown === item.label && (
                  <div className="absolute top-full left-0 mt-1 w-60 bg-dark-800 rounded-xl shadow-2xl border border-dark-500 overflow-hidden animate-slide-down">
                    <div className="p-3 border-b border-dark-600 bg-dark-800/50">
                      <p className="text-xs text-gray-400">
                        {item.description}
                      </p>
                    </div>
                    <div className="py-1">
                      {item.subItems.map((subItem) => (
                        <Link
                          key={subItem.label}
                          href={subItem.href}
                          className="block px-4 py-2.5 text-sm text-gray-300 hover:bg-dark-700 hover:text-white transition-colors"
                        >
                          {subItem.label}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}

            <div className="w-px h-6 bg-dark-600 mx-2" />

            <Link
              href="/security"
              className={`flex items-center gap-1.5 px-3 py-2 text-sm rounded-lg transition-all hover:bg-dark-700/50 ${
                pathname === "/security" ? "text-green-400" : "text-gray-300 hover:text-white"
              }`}
            >
              <Shield className="w-4 h-4" />
              Security
            </Link>

            <Link
              href="/architecture"
              className={`flex items-center gap-1.5 px-3 py-2 text-sm rounded-lg transition-all hover:bg-dark-700/50 ${
                pathname === "/architecture" ? "text-green-400" : "text-gray-300 hover:text-white"
              }`}
            >
              <BookOpen className="w-4 h-4" />
              Architecture
            </Link>

            <Link
              href="/learning"
              className={`flex items-center gap-1.5 px-3 py-2 text-sm rounded-lg transition-all hover:bg-dark-700/50 ${
                pathname === "/learning" ? "text-green-400" : "text-gray-300 hover:text-white"
              }`}
            >
              <BookOpen className="w-4 h-4" />
              Learning
            </Link>

            <Link
              href="/origin-story"
              className={`flex items-center gap-1.5 px-3 py-2 text-sm rounded-lg transition-all hover:bg-dark-700/50 ${
                pathname === "/origin-story" ? "text-green-400" : "text-gray-300 hover:text-white"
              }`}
            >
              <Fish className="w-4 h-4" />
              Origin
            </Link>
          </div>

          {/* CTA Button */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              href="/download"
              className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-5 py-2.5 rounded-lg font-medium transition-all shadow-lg shadow-green-500/20 hover:shadow-green-500/40"
            >
              <Download className="w-4 h-4" />
              Download
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 text-gray-400 hover:text-white rounded-lg hover:bg-dark-700 transition-colors"
            onClick={() => setIsOpen(!isOpen)}
            aria-label={isOpen ? "Close menu" : "Open menu"}
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden bg-dark-800 border-t border-dark-600 animate-slide-down">
          <div className="px-4 py-4 space-y-2">
            {navItems.map((item) => (
              <div key={item.label}>
                <Link
                  href={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg bg-dark-700/50 ${getColorClasses(
                    item.color
                  )}`}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
                <div className="ml-8 mt-1 space-y-1">
                  {item.subItems.map((subItem) => (
                    <Link
                      key={subItem.label}
                      href={subItem.href}
                      className="block px-4 py-2 text-sm text-gray-400 hover:text-white rounded-lg hover:bg-dark-700/30"
                    >
                      {subItem.label}
                    </Link>
                  ))}
                </div>
              </div>
            ))}

            <div className="border-t border-dark-600 pt-4 mt-4 space-y-2">
              <Link
                href="/security"
                className="flex items-center gap-3 px-4 py-3 text-gray-300 hover:text-white rounded-lg hover:bg-dark-700/50"
              >
                <Shield className="w-5 h-5" />
                Security Model
              </Link>

              <Link
                href="/architecture"
                className="flex items-center gap-3 px-4 py-3 text-gray-300 hover:text-white rounded-lg hover:bg-dark-700/50"
              >
                <BookOpen className="w-5 h-5" />
                Architecture
              </Link>

              <Link
                href="/learning"
                className="flex items-center gap-3 px-4 py-3 text-gray-300 hover:text-white rounded-lg hover:bg-dark-700/50"
              >
                <BookOpen className="w-5 h-5" />
                Learning Center
              </Link>

              <Link
                href="/origin-story"
                className="flex items-center gap-3 px-4 py-3 text-gray-300 hover:text-white rounded-lg hover:bg-dark-700/50"
              >
                <Fish className="w-5 h-5" />
                Origin Story
              </Link>
            </div>

            <Link
              href="/download"
              className="flex items-center justify-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white px-4 py-3.5 rounded-xl font-medium shadow-lg shadow-green-500/20 mt-4"
            >
              <Download className="w-5 h-5" />
              Download Now
            </Link>
          </div>
        </div>
      )}
    </nav>
  );
}
