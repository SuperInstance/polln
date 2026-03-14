import Link from "next/link";
import { Github, Twitter, Mail, Heart, Fish, Shield, Cpu, Code, Users, BookOpen, Download } from "lucide-react";

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-dark-800 border-t border-dark-600">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10">
          {/* Brand */}
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center gap-2 mb-5 group">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-green-500/20 group-hover:shadow-green-500/40 transition-shadow">
                <span className="text-white font-bold">T</span>
              </div>
              <span className="font-bold text-xl gradient-text">TernaryAir</span>
            </Link>
            <p className="text-gray-400 text-sm max-w-md mb-5 leading-relaxed">
              The hardware boundary between you and AI. Open-source ternary inference 
              engine for secure, private, and affordable AI inference. MIT licensed.
            </p>
            <div className="flex items-center gap-4">
              <a
                href="https://github.com/superinstance/ternaryair"
                target="_blank"
                rel="noopener noreferrer"
                className="w-9 h-9 rounded-lg bg-dark-700 hover:bg-dark-600 flex items-center justify-center text-gray-400 hover:text-white transition-all"
                aria-label="GitHub"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="https://twitter.com/superinstance"
                target="_blank"
                rel="noopener noreferrer"
                className="w-9 h-9 rounded-lg bg-dark-700 hover:bg-dark-600 flex items-center justify-center text-gray-400 hover:text-white transition-all"
                aria-label="Twitter"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a
                href="mailto:hello@superinstance.ai"
                className="w-9 h-9 rounded-lg bg-dark-700 hover:bg-dark-600 flex items-center justify-center text-gray-400 hover:text-white transition-all"
                aria-label="Email"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* For You */}
          <div>
            <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
              <Users className="w-4 h-4 text-blue-400" />
              For You
            </h3>
            <ul className="space-y-3">
              <li>
                <Link
                  href="/users"
                  className="text-gray-400 hover:text-blue-400 text-sm transition-colors"
                >
                  User Guide
                </Link>
              </li>
              <li>
                <Link
                  href="/users#use-cases"
                  className="text-gray-400 hover:text-blue-400 text-sm transition-colors"
                >
                  Use Cases
                </Link>
              </li>
              <li>
                <Link
                  href="/security"
                  className="text-gray-400 hover:text-blue-400 text-sm transition-colors"
                >
                  Security Model
                </Link>
              </li>
              <li>
                <Link
                  href="/learning"
                  className="text-gray-400 hover:text-blue-400 text-sm transition-colors"
                >
                  Learning Center
                </Link>
              </li>
            </ul>
          </div>

          {/* For Developers */}
          <div>
            <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
              <Code className="w-4 h-4 text-purple-400" />
              Developers
            </h3>
            <ul className="space-y-3">
              <li>
                <Link
                  href="/developers"
                  className="text-gray-400 hover:text-purple-400 text-sm transition-colors"
                >
                  SDK Docs
                </Link>
              </li>
              <li>
                <Link
                  href="/developers#api"
                  className="text-gray-400 hover:text-purple-400 text-sm transition-colors"
                >
                  API Reference
                </Link>
              </li>
              <li>
                <Link
                  href="/developers#examples"
                  className="text-gray-400 hover:text-purple-400 text-sm transition-colors"
                >
                  Code Examples
                </Link>
              </li>
              <li>
                <a
                  href="https://github.com/superinstance/ternaryair"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-purple-400 text-sm transition-colors"
                >
                  GitHub Repository
                </a>
              </li>
            </ul>
          </div>

          {/* For Engineers */}
          <div>
            <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-amber-400" />
              Engineers
            </h3>
            <ul className="space-y-3">
              <li>
                <Link
                  href="/engineers"
                  className="text-gray-400 hover:text-amber-400 text-sm transition-colors"
                >
                  RTL Source
                </Link>
              </li>
              <li>
                <Link
                  href="/architecture"
                  className="text-gray-400 hover:text-amber-400 text-sm transition-colors"
                >
                  Architecture
                </Link>
              </li>
              <li>
                <Link
                  href="/engineers#fpga"
                  className="text-gray-400 hover:text-amber-400 text-sm transition-colors"
                >
                  FPGA Prototyping
                </Link>
              </li>
              <li>
                <Link
                  href="/download"
                  className="text-gray-400 hover:text-amber-400 text-sm transition-colors"
                >
                  Bitstreams
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Stats */}
        <div className="mt-12 pt-8 border-t border-dark-600">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">$99</div>
              <div className="text-xs text-gray-500 mt-1">Target Price</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">100+</div>
              <div className="text-xs text-gray-500 mt-1">Tokens/sec</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">3-5W</div>
              <div className="text-xs text-gray-500 mt-1">USB Power</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">MIT</div>
              <div className="text-xs text-gray-500 mt-1">Open Source</div>
            </div>
          </div>
        </div>

        {/* Bottom */}
        <div className="border-t border-dark-600 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex flex-col md:flex-row items-center gap-4 text-sm text-gray-500">
            <p>© {currentYear} SuperInstance.AI. MIT License.</p>
            <span className="hidden md:inline text-dark-500">•</span>
            <p className="flex items-center gap-1.5">
              Made with <Heart className="w-4 h-4 text-red-500" /> by 
              <a 
                href="https://superinstance.ai" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-green-400 hover:text-green-300 transition-colors"
              >
                Casey DiGennaro
              </a>
            </p>
          </div>
          
          <div className="flex items-center gap-4 text-sm text-gray-500">
            <Link 
              href="/origin-story"
              className="hover:text-green-400 transition-colors flex items-center gap-1"
            >
              <Fish className="w-4 h-4" />
              The Story
            </Link>
            <span className="text-dark-500">•</span>
            <Link 
              href="/download"
              className="hover:text-green-400 transition-colors flex items-center gap-1"
            >
              <Download className="w-4 h-4" />
              Download
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
