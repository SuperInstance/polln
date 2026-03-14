import Link from "next/link";
import { Github, Twitter, Mail, Heart, BookOpen, Clock, Cpu, Users, Sparkles, Gamepad2, Music, Brain } from "lucide-react";

const footerLinks = {
  platform: [
    { label: "Home", href: "/" },
    { label: "MIST Game", href: "/mist" },
    { label: "Music Playground", href: "/music" },
    { label: "Professional Tools", href: "/professional" },
  ],
  learning: [
    { label: "MIST: Young Learners", href: "/mist" },
    { label: "Tabula Rosa Research", href: "/tabula-rosa" },
    { label: "Learning Hub", href: "/learning" },
    { label: "Timing Playground", href: "/timing-playground" },
  ],
  resources: [
    { label: "About Us", href: "/about" },
    { label: "Research", href: "/about#research" },
    { label: "Team", href: "/about#team" },
    { label: "Contact", href: "mailto:hello@lucineer.ai" },
  ],
};

const ageGroups = [
  { label: "Kids (5-10)", href: "/mist", icon: Gamepad2, color: "text-primary" },
  { label: "Students", href: "/learning", icon: BookOpen, color: "text-cyan-400" },
  { label: "Researchers", href: "/tabula-rosa", icon: Brain, color: "text-purple-400" },
  { label: "Engineers", href: "/professional", icon: Cpu, color: "text-amber-400" },
];

export default function Footer() {
  return (
    <footer className="bg-card border-t border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12">
          {/* Brand Column */}
          <div className="lg:col-span-2">
            <Link href="/" className="flex items-center gap-3 mb-6 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-lg">L</span>
              </div>
              <div className="flex flex-col">
                <span className="font-bold text-lg gradient-text">Lucineer</span>
                <span className="text-xs text-muted-foreground">AI Education & Chip Design</span>
              </div>
            </Link>
            <p className="text-muted-foreground mb-6 max-w-md leading-relaxed">
              From games that teach kids how AI works, to professional tools for building inference chips. 
              One platform for explorers and engineers alike.
            </p>
            
            {/* Age Group Pills */}
            <div className="flex flex-wrap gap-2 mb-6">
              {ageGroups.map((group) => (
                <Link
                  key={group.label}
                  href={group.href}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-all duration-200 hover:scale-105 ${group.color} border-current/30 hover:border-current bg-current/5`}
                >
                  <group.icon className="w-3 h-3" />
                  <span>{group.label}</span>
                </Link>
              ))}
            </div>

            {/* Social Links */}
            <div className="flex items-center gap-4">
              <a
                href="https://github.com/superinstance/lucineer"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
                aria-label="GitHub"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="https://twitter.com/superinstance"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
                aria-label="Twitter"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a
                href="mailto:hello@lucineer.ai"
                className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
                aria-label="Email"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Platform Links */}
          <div>
            <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
              <Clock className="w-4 h-4 text-primary" />
              Platform
            </h3>
            <ul className="space-y-3">
              {footerLinks.platform.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-muted-foreground hover:text-primary transition-colors text-sm"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Learning Links */}
          <div>
            <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-blue-400" />
              Learning
            </h3>
            <ul className="space-y-3">
              {footerLinks.learning.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-muted-foreground hover:text-blue-400 transition-colors text-sm"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Resources Links */}
          <div>
            <h3 className="font-semibold text-foreground mb-4 flex items-center gap-2">
              <Users className="w-4 h-4 text-amber-400" />
              Resources
            </h3>
            <ul className="space-y-3">
              {footerLinks.resources.map((link) => (
                <li key={link.label}>
                  <Link
                    href={link.href}
                    className="text-muted-foreground hover:text-amber-400 transition-colors text-sm"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-border mt-12 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-muted-foreground text-sm">
              © {new Date().getFullYear()} Lucineer. Open source under MIT License.
            </p>
            <div className="flex items-center gap-6 text-sm text-muted-foreground">
              <Link href="/about" className="hover:text-foreground transition-colors">
                Privacy Policy
              </Link>
              <Link href="/about" className="hover:text-foreground transition-colors">
                Terms of Use
              </Link>
              <span className="flex items-center gap-1">
                Made with <Heart className="w-4 h-4 text-red-500" /> for curious minds
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
