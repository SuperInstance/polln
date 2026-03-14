import Link from "next/link";
import { Cpu, Github, Twitter, Linkedin, Mail } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-dark-900 border-t border-dark-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <Link href="/" className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                <Cpu className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold gradient-text">TernaryAir</span>
            </Link>
            <p className="text-gray-400 text-sm mb-4 max-w-md">
              Educational AI platform teaching concepts through timing, sequencing, and game-like experiences. 
              From young learners to professionals, everyone can understand AI at their own pace.
            </p>
            <div className="flex items-center gap-4">
              <a href="https://github.com/superinstance/ternaryair" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors">
                <Github className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <Linkedin className="w-5 h-5" />
              </a>
              <a href="mailto:hello@ternaryair.ai" className="text-gray-400 hover:text-white transition-colors">
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Learning */}
          <div>
            <h3 className="text-white font-semibold mb-4">Learning</h3>
            <ul className="space-y-2">
              <li><Link href="/learning" className="text-gray-400 hover:text-green-400 text-sm transition-colors">Learning Hub</Link></li>
              <li><Link href="/timing-playground" className="text-gray-400 hover:text-green-400 text-sm transition-colors">Timing Playground</Link></li>
              <li><Link href="/professional" className="text-gray-400 hover:text-green-400 text-sm transition-colors">Professional Tools</Link></li>
              <li><Link href="/about" className="text-gray-400 hover:text-green-400 text-sm transition-colors">About Us</Link></li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-white font-semibold mb-4">Resources</h3>
            <ul className="space-y-2">
              <li><a href="#" className="text-gray-400 hover:text-green-400 text-sm transition-colors">Documentation</a></li>
              <li><a href="#" className="text-gray-400 hover:text-green-400 text-sm transition-colors">API Reference</a></li>
              <li><a href="#" className="text-gray-400 hover:text-green-400 text-sm transition-colors">Research Papers</a></li>
              <li><a href="#" className="text-gray-400 hover:text-green-400 text-sm transition-colors">Community</a></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-dark-700 mt-12 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-gray-500 text-sm">
            © 2026 TernaryAir / SuperInstance.AI. All rights reserved.
          </p>
          <div className="flex items-center gap-6 text-sm">
            <a href="#" className="text-gray-400 hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" className="text-gray-400 hover:text-white transition-colors">Terms of Service</a>
            <a href="#" className="text-gray-400 hover:text-white transition-colors">MIT License</a>
          </div>
        </div>
      </div>
    </footer>
  );
}
