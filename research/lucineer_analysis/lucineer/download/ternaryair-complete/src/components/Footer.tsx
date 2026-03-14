import Link from "next/link";
import { Github, Twitter, Mail, Heart, ExternalLink } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-[#050505] border-t border-green-500/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <Link href="/" className="flex items-center gap-3 mb-4">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-green-500 to-green-700 flex items-center justify-center shadow-lg shadow-green-500/20">
                <span className="text-white font-bold text-sm">T</span>
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-lg gradient-text">TernaryAir</span>
                <span className="text-[10px] text-green-500/60 -mt-1">by SuperInstance.AI</span>
              </div>
            </Link>
            <p className="text-gray-400 text-sm max-w-md mb-6">
              The hardware boundary between you and AI. Open-source mask-locked ternary inference chip for secure, private, and affordable AI inference. MIT License.
            </p>
            <div className="flex items-center gap-4">
              <a
                href="https://github.com/superinstance/ternaryair"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-green-400 transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="https://twitter.com/superinstance"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-green-400 transition-colors"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a
                href="mailto:hello@superinstance.ai"
                className="text-gray-400 hover:text-green-400 transition-colors"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Documentation */}
          <div>
            <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
              Documentation
              <ExternalLink className="w-3 h-3 text-gray-500" />
            </h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/users"
                  className="text-gray-400 hover:text-green-400 text-sm transition-colors"
                >
                  For Users
                </Link>
              </li>
              <li>
                <Link
                  href="/developers"
                  className="text-gray-400 hover:text-green-400 text-sm transition-colors"
                >
                  For Developers
                </Link>
              </li>
              <li>
                <Link
                  href="/engineers"
                  className="text-gray-400 hover:text-green-400 text-sm transition-colors"
                >
                  For Engineers
                </Link>
              </li>
              <li>
                <Link
                  href="/architecture"
                  className="text-gray-400 hover:text-green-400 text-sm transition-colors"
                >
                  Architecture
                </Link>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="font-semibold text-white mb-4">Resources</h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/download"
                  className="text-gray-400 hover:text-green-400 text-sm transition-colors"
                >
                  Download
                </Link>
              </li>
              <li>
                <Link
                  href="/security"
                  className="text-gray-400 hover:text-green-400 text-sm transition-colors"
                >
                  Security Model
                </Link>
              </li>
              <li>
                <Link
                  href="/learning"
                  className="text-gray-400 hover:text-green-400 text-sm transition-colors"
                >
                  Learning Center
                </Link>
              </li>
              <li>
                <Link
                  href="/origin-story"
                  className="text-gray-400 hover:text-green-400 text-sm transition-colors"
                >
                  Origin Story
                </Link>
              </li>
            </ul>
          </div>

          {/* Community */}
          <div>
            <h3 className="font-semibold text-white mb-4">Community</h3>
            <ul className="space-y-2">
              <li>
                <a
                  href="https://github.com/superinstance/ternaryair"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-green-400 text-sm transition-colors"
                >
                  GitHub Repository
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/superinstance/ternaryair/discussions"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-green-400 text-sm transition-colors"
                >
                  Discussions
                </a>
              </li>
              <li>
                <a
                  href="https://github.com/superinstance/ternaryair/issues"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-green-400 text-sm transition-colors"
                >
                  Issue Tracker
                </a>
              </li>
              <li>
                <a
                  href="https://discord.gg/ternaryair"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-green-400 text-sm transition-colors"
                >
                  Discord Community
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-green-500/10 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-gray-500 text-sm">
            © {new Date().getFullYear()} SuperInstance.AI. MIT License. Open Source Forever.
          </p>
          <p className="text-gray-500 text-sm flex items-center gap-1">
            Made with <Heart className="w-4 h-4 text-green-500" /> by Casey DiGennaro
          </p>
        </div>
      </div>
    </footer>
  );
}
