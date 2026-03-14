import Link from "next/link";
import { 
  Cpu, Github, Twitter, Linkedin, Mail, Heart, 
  BookOpen, Download, Users, Zap, ExternalLink
} from "lucide-react";

const footerLinks = {
  learn: [
    { name: "Young Learners", href: "/learning?age=young" },
    { name: "Middle School", href: "/learning?age=middle" },
    { name: "High School", href: "/learning?age=high" },
    { name: "Professional", href: "/learning?age=pro" },
    { name: "Timing Playground", href: "/timing-playground" },
  ],
  tools: [
    { name: "Pro Tools", href: "/professional" },
    { name: "API Connect", href: "/api-connect" },
    { name: "Downloads", href: "/downloads" },
    { name: "Research Hub", href: "/research" },
  ],
  community: [
    { name: "Community", href: "/community" },
    { name: "Contributing", href: "/community#contribute" },
    { name: "Discord", href: "#", external: true },
    { name: "GitHub Discussions", href: "https://github.com/superinstance/ternaryair", external: true },
  ],
  resources: [
    { name: "Documentation", href: "/docs" },
    { name: "Design System", href: "/design-system" },
    { name: "API Reference", href: "/api-reference" },
    { name: "Status", href: "/status" },
  ],
};

export default function Footer() {
  return (
    <footer className="bg-dark-900 border-t border-dark-700">
      {/* Main Footer */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 lg:gap-12">
          {/* Brand Column */}
          <div className="col-span-2 md:col-span-3 lg:col-span-2">
            <Link href="/" className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center">
                <Cpu className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold gradient-text">TernaryAir</span>
            </Link>
            <p className="text-gray-400 text-sm mb-6 max-w-sm leading-relaxed">
              Learn AI through play. Master timing concepts from traffic lights to FPGA design. 
              Offline-first, open source, built for everyone.
            </p>
            <div className="flex items-center gap-4">
              <a 
                href="https://github.com/superinstance/ternaryair" 
                target="_blank" 
                rel="noopener noreferrer"
                className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-dark-700 transition-all"
                aria-label="GitHub"
              >
                <Github className="w-5 h-5" />
              </a>
              <a 
                href="#" 
                className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-dark-700 transition-all"
                aria-label="Twitter"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a 
                href="#" 
                className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-dark-700 transition-all"
                aria-label="LinkedIn"
              >
                <Linkedin className="w-5 h-5" />
              </a>
              <a 
                href="mailto:hello@ternaryair.ai" 
                className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-dark-700 transition-all"
                aria-label="Email"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Learn */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-green-400" />
              Learn
            </h3>
            <ul className="space-y-2.5">
              {footerLinks.learn.map((link) => (
                <li key={link.name}>
                  <Link 
                    href={link.href}
                    className="text-sm text-gray-400 hover:text-green-400 transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Tools */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
              <Zap className="w-4 h-4 text-blue-400" />
              Tools
            </h3>
            <ul className="space-y-2.5">
              {footerLinks.tools.map((link) => (
                <li key={link.name}>
                  <Link 
                    href={link.href}
                    className="text-sm text-gray-400 hover:text-blue-400 transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Community */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
              <Users className="w-4 h-4 text-purple-400" />
              Community
            </h3>
            <ul className="space-y-2.5">
              {footerLinks.community.map((link) => (
                <li key={link.name}>
                  {link.external ? (
                    <a 
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-gray-400 hover:text-purple-400 transition-colors flex items-center gap-1"
                    >
                      {link.name}
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  ) : (
                    <Link 
                      href={link.href}
                      className="text-sm text-gray-400 hover:text-purple-400 transition-colors"
                    >
                      {link.name}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-sm font-semibold text-white mb-4 flex items-center gap-2">
              <Download className="w-4 h-4 text-amber-400" />
              Resources
            </h3>
            <ul className="space-y-2.5">
              {footerLinks.resources.map((link) => (
                <li key={link.name}>
                  <Link 
                    href={link.href}
                    className="text-sm text-gray-400 hover:text-amber-400 transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Download Banner */}
        <div className="mt-12 p-6 rounded-2xl bg-gradient-to-r from-green-500/10 via-dark-800 to-blue-500/10 border border-dark-600">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="text-center md:text-left">
              <h3 className="text-lg font-semibold text-white mb-1">
                Take It Offline
              </h3>
              <p className="text-sm text-gray-400">
                Download everything. Learn anywhere, anytime. No internet needed.
              </p>
            </div>
            <Link
              href="/downloads"
              className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-6 py-3 rounded-xl font-medium transition-all shadow-lg"
            >
              <Download className="w-5 h-5" />
              Download Free
            </Link>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-dark-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm">
            <div className="flex items-center gap-2 text-gray-500">
              <span>© 2026 TernaryAir / SuperInstance.AI</span>
              <span>•</span>
              <span className="flex items-center gap-1">
                Made with <Heart className="w-3 h-3 text-red-500" /> for learners everywhere
              </span>
            </div>
            <div className="flex items-center gap-6">
              <Link href="/privacy" className="text-gray-500 hover:text-white transition-colors">
                Privacy
              </Link>
              <Link href="/terms" className="text-gray-500 hover:text-white transition-colors">
                Terms
              </Link>
              <Link href="/license" className="text-gray-500 hover:text-white transition-colors">
                MIT License
              </Link>
              <a 
                href="#" 
                className="flex items-center gap-1 text-gray-500 hover:text-green-400 transition-colors"
              >
                <span className="w-2 h-2 rounded-full bg-green-500" />
                All systems operational
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
