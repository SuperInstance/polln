"use client";

import Link from "next/link";
import { 
  Github, Twitter, Mail, Heart, Cpu, BookOpen, Download, 
  Zap, Users, Code, Sparkles, ExternalLink
} from "lucide-react";

const footerLinks = {
  learning: [
    { name: "Young Learners (4-10)", href: "/learning?age=young" },
    { name: "Middle School (11-14)", href: "/learning?age=middle" },
    { name: "High School (15-18)", href: "/learning?age=high" },
    { name: "Professional (18+)", href: "/learning?age=pro" },
  ],
  resources: [
    { name: "TernaryAir Studio", href: "/ternaryair" },
    { name: "Timing Playground", href: "/timing-playground" },
    { name: "Download Center", href: "/downloads" },
    { name: "Research Hub", href: "/research" },
  ],
  community: [
    { name: "API Connections", href: "/api-connect" },
    { name: "Contributing", href: "/contributing" },
    { name: "GitHub", href: "https://github.com/lucineer", external: true },
  ],
};

// Partner ecosystem links
const partnerLinks = [
  { name: "SuperInstance.AI", href: "https://superinstance.ai", description: "AI within spreadsheets" },
  { name: "LucidDreamer.com", href: "https://luciddreamer.com", description: "Community building" },
];

// Voxel game concept credit
const voxelGameCredit = {
  creators: "Magnus & Casey DiGennaro",
  description: "Voxel Game Concept",
};

export default function Footer() {
  return (
    <footer className="bg-dark-950 border-t border-dark-700">
      {/* Main Footer */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Brand Column */}
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                <Cpu className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="text-xl font-bold gradient-text">Lucineer</span>
                <p className="text-xs text-gray-500">Become a Lucineer</p>
              </div>
            </Link>
            <p className="text-gray-400 text-sm leading-relaxed mb-4 max-w-sm">
              Learn AI through timing games and interactive simulations. Design real chips with TernaryAir. 
              Free forever, works offline, open source.
            </p>
            <div className="flex items-center gap-4">
              <a 
                href="https://github.com/lucineer" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-gray-500 hover:text-white transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
              <a 
                href="https://twitter.com/lucineer" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-gray-500 hover:text-white transition-colors"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a 
                href="mailto:hello@lucineer.com" 
                className="text-gray-500 hover:text-white transition-colors"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Learning Column */}
          <div>
            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-green-400" />
              Learning
            </h3>
            <ul className="space-y-2">
              {footerLinks.learning.map((link) => (
                <li key={link.name}>
                  <Link 
                    href={link.href}
                    className="text-gray-400 hover:text-white text-sm transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources Column */}
          <div>
            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
              <Download className="w-4 h-4 text-green-400" />
              Resources
            </h3>
            <ul className="space-y-2">
              {footerLinks.resources.map((link) => (
                <li key={link.name}>
                  <Link 
                    href={link.href}
                    className="text-gray-400 hover:text-white text-sm transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Community Column */}
          <div>
            <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
              <Users className="w-4 h-4 text-green-400" />
              Community
            </h3>
            <ul className="space-y-2">
              {footerLinks.community.map((link) => (
                <li key={link.name}>
                  {link.external ? (
                    <a 
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-gray-400 hover:text-white text-sm transition-colors flex items-center gap-1"
                    >
                      {link.name}
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  ) : (
                    <Link 
                      href={link.href}
                      className="text-gray-400 hover:text-white text-sm transition-colors"
                    >
                      {link.name}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Partner Ecosystem - Subtle Section */}
      <div className="border-t border-dark-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2 text-gray-600 text-xs">
              <Sparkles className="w-3 h-3" />
              <span>Part of the Lucineer ecosystem:</span>
            </div>
            <div className="flex items-center gap-6">
              {partnerLinks.map((partner) => (
                <a
                  key={partner.name}
                  href={partner.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-600 hover:text-gray-400 transition-colors text-xs flex items-center gap-1.5"
                  title={partner.description}
                >
                  {partner.name}
                  <ExternalLink className="w-2.5 h-2.5" />
                </a>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Voxel Game Concept Credit */}
      <div className="border-t border-dark-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col sm:flex-row items-center justify-center gap-2 text-center">
            <div className="flex items-center gap-2 text-gray-600 text-sm">
              <Cpu className="w-4 h-4 text-purple-400" />
              <span className="text-gray-500">
                {voxelGameCredit.description} by{" "}
                <span className="text-gray-400 font-medium">{voxelGameCredit.creators}</span>
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-dark-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-sm text-gray-500">
            <div className="flex items-center gap-1">
              <span>© {new Date().getFullYear()} Lucineer. Built with curiosity by </span>
              <span className="text-gray-400">Magnus & Casey DiGennaro</span>
              <span> and </span>
              <Heart className="w-4 h-4 text-red-500 inline" />
              <span>for learners everywhere.</span>
            </div>
            <div className="flex items-center gap-6">
              <Link href="/privacy" className="hover:text-white transition-colors">
                Privacy
              </Link>
              <Link href="/terms" className="hover:text-white transition-colors">
                Terms
              </Link>
              <Link href="/license" className="hover:text-white transition-colors">
                MIT License
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
