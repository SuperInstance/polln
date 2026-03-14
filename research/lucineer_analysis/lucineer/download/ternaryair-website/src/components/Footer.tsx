import Link from "next/link";
import { Github, Twitter, Mail, Heart } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-dark-800 border-t border-dark-600">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
                <span className="text-white font-bold text-sm">T</span>
              </div>
              <span className="font-bold text-lg gradient-text">TernaryAir</span>
            </Link>
            <p className="text-gray-400 text-sm max-w-md mb-4">
              The hardware boundary between you and AI. Open-source ternary
              inference engine for secure, private, and affordable AI inference.
            </p>
            <div className="flex items-center gap-4">
              <a
                href="https://github.com/superinstance/ternaryair"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="https://twitter.com/superinstance"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a
                href="mailto:hello@superinstance.ai"
                className="text-gray-400 hover:text-white transition-colors"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-semibold text-white mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/download"
                  className="text-gray-400 hover:text-primary-400 text-sm transition-colors"
                >
                  Download
                </Link>
              </li>
              <li>
                <Link
                  href="/users"
                  className="text-gray-400 hover:text-primary-400 text-sm transition-colors"
                >
                  For Users
                </Link>
              </li>
              <li>
                <Link
                  href="/developers"
                  className="text-gray-400 hover:text-primary-400 text-sm transition-colors"
                >
                  For Developers
                </Link>
              </li>
              <li>
                <Link
                  href="/engineers"
                  className="text-gray-400 hover:text-primary-400 text-sm transition-colors"
                >
                  For Engineers
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
                  href="/security"
                  className="text-gray-400 hover:text-primary-400 text-sm transition-colors"
                >
                  Security Model
                </Link>
              </li>
              <li>
                <Link
                  href="/architecture"
                  className="text-gray-400 hover:text-primary-400 text-sm transition-colors"
                >
                  Architecture
                </Link>
              </li>
              <li>
                <Link
                  href="/learning"
                  className="text-gray-400 hover:text-primary-400 text-sm transition-colors"
                >
                  Learning Center
                </Link>
              </li>
              <li>
                <Link
                  href="/origin-story"
                  className="text-gray-400 hover:text-primary-400 text-sm transition-colors"
                >
                  Origin Story
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-dark-600 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-gray-500 text-sm">
            © {new Date().getFullYear()} SuperInstance.AI. MIT License.
          </p>
          <p className="text-gray-500 text-sm flex items-center gap-1">
            Made with <Heart className="w-4 h-4 text-red-500" /> by Casey
            DiGennaro
          </p>
        </div>
      </div>
    </footer>
  );
}
