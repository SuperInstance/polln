"use client";

import { useState } from "react";
import Link from "next/link";
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
} from "lucide-react";

export default function Navigation() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState<string | null>(null);

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

  const getColorClasses = (color: string) => {
    switch (color) {
      case "user":
        return "text-user hover:text-user-light";
      case "developer":
        return "text-developer hover:text-developer-light";
      case "engineer":
        return "text-engineer hover:text-engineer-light";
      default:
        return "text-primary-400 hover:text-primary-300";
    }
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-dark-900/95 backdrop-blur-sm border-b border-dark-600">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
              <span className="text-white font-bold text-sm">T</span>
            </div>
            <span className="font-bold text-lg">
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
                  className={`flex items-center gap-1 px-4 py-2 rounded-lg transition-colors ${getColorClasses(
                    item.color
                  )}`}
                >
                  <item.icon className="w-4 h-4" />
                  {item.label}
                  <ChevronDown className="w-3 h-3" />
                </Link>

                {/* Dropdown */}
                {activeDropdown === item.label && (
                  <div className="absolute top-full left-0 mt-1 w-56 bg-dark-700 rounded-lg shadow-xl border border-dark-500 overflow-hidden animate-slide-down">
                    <div className="p-3 border-b border-dark-500">
                      <p className="text-xs text-gray-400">
                        {item.description}
                      </p>
                    </div>
                    <div className="py-1">
                      {item.subItems.map((subItem) => (
                        <Link
                          key={subItem.label}
                          href={subItem.href}
                          className="block px-4 py-2 text-sm text-gray-300 hover:bg-dark-600 hover:text-white transition-colors"
                        >
                          {subItem.label}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}

            <div className="w-px h-6 bg-dark-500 mx-2" />

            <Link
              href="/security"
              className="flex items-center gap-1 px-3 py-2 text-sm text-gray-300 hover:text-white transition-colors"
            >
              <Shield className="w-4 h-4" />
              Security
            </Link>

            <Link
              href="/architecture"
              className="flex items-center gap-1 px-3 py-2 text-sm text-gray-300 hover:text-white transition-colors"
            >
              <BookOpen className="w-4 h-4" />
              Architecture
            </Link>

            <Link
              href="/learning"
              className="flex items-center gap-1 px-3 py-2 text-sm text-gray-300 hover:text-white transition-colors"
            >
              <BookOpen className="w-4 h-4" />
              Learning
            </Link>
          </div>

          {/* CTA Button */}
          <div className="hidden md:flex items-center gap-3">
            <Link
              href="/download"
              className="flex items-center gap-2 bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              <Download className="w-4 h-4" />
              Download
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 text-gray-400 hover:text-white"
            onClick={() => setIsOpen(!isOpen)}
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isOpen && (
        <div className="md:hidden bg-dark-800 border-t border-dark-600">
          <div className="px-4 py-4 space-y-2">
            {navItems.map((item) => (
              <div key={item.label}>
                <Link
                  href={item.href}
                  className={`flex items-center gap-2 px-4 py-3 rounded-lg ${getColorClasses(
                    item.color
                  )} bg-dark-700`}
                  onClick={() => setIsOpen(false)}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
                <div className="ml-8 mt-1 space-y-1">
                  {item.subItems.map((subItem) => (
                    <Link
                      key={subItem.label}
                      href={subItem.href}
                      className="block px-4 py-2 text-sm text-gray-400 hover:text-white"
                      onClick={() => setIsOpen(false)}
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
                className="flex items-center gap-2 px-4 py-3 text-gray-300 hover:text-white"
                onClick={() => setIsOpen(false)}
              >
                <Shield className="w-5 h-5" />
                Security Model
              </Link>

              <Link
                href="/architecture"
                className="flex items-center gap-2 px-4 py-3 text-gray-300 hover:text-white"
                onClick={() => setIsOpen(false)}
              >
                <BookOpen className="w-5 h-5" />
                Architecture
              </Link>

              <Link
                href="/origin-story"
                className="flex items-center gap-2 px-4 py-3 text-gray-300 hover:text-white"
                onClick={() => setIsOpen(false)}
              >
                <BookOpen className="w-5 h-5" />
                Origin Story
              </Link>

              <Link
                href="/learning"
                className="flex items-center gap-2 px-4 py-3 text-gray-300 hover:text-white"
                onClick={() => setIsOpen(false)}
              >
                <BookOpen className="w-5 h-5" />
                Learning Center
              </Link>
            </div>

            <Link
              href="/download"
              className="flex items-center justify-center gap-2 bg-primary-600 text-white px-4 py-3 rounded-lg font-medium mt-4"
              onClick={() => setIsOpen(false)}
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
