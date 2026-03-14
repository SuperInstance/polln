"use client";

import Link from "next/link";
import {
  Users, Star, Heart, Award, MessageCircle, Github,
  Trophy, Target, Upload, Shield, ExternalLink, ArrowRight,
  CheckCircle, Sparkles, Crown
} from "lucide-react";

const achievements = [
  { id: "learner", icon: "🎓", name: "Learner", description: "Completed first module", earned: true },
  { id: "explorer", icon: "🚀", name: "Explorer", description: "Downloaded offline pack", earned: true },
  { id: "builder", icon: "🔧", name: "Builder", description: "Contributed code", earned: false },
  { id: "teacher", icon: "📚", name: "Teacher", description: "Created educational content", earned: false },
  { id: "star", icon: "🌟", name: "Star", description: "Received community recognition", earned: false },
  { id: "champion", icon: "👑", name: "Champion", description: "Helped 10+ community members", earned: false },
];

const recentContributions = [
  {
    user: "Alex K.",
    avatar: "A",
    action: "created",
    item: "Traffic Light FSM Lesson",
    time: "2 hours ago",
    likes: 12,
  },
  {
    user: "Sarah M.",
    avatar: "S",
    action: "improved",
    item: "Setup/Hold Visualizer",
    time: "5 hours ago",
    likes: 8,
  },
  {
    user: "Dev Team",
    avatar: "D",
    action: "released",
    item: "v2.0 Design System",
    time: "1 day ago",
    likes: 24,
  },
];

const topContributors = [
  { name: "Casey D.", contributions: 47, badges: ["🎓", "🚀", "🔧", "🌟"] },
  { name: "Alex K.", contributions: 23, badges: ["🎓", "📚", "🔧"] },
  { name: "Sarah M.", contributions: 19, badges: ["🎓", "🚀", "📚"] },
];

export default function CommunityPage() {
  return (
    <div className="animated-bg min-h-screen pt-24 pb-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 bg-purple-500/10 border border-purple-500/30 rounded-full px-5 py-2 mb-6">
            <Users className="w-4 h-4 text-purple-400" />
            <span className="text-purple-400 text-sm font-medium">Open Community</span>
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            <span className="gradient-text">Community Hub</span>
          </h1>
          <p className="text-gray-400 max-w-2xl mx-auto text-lg">
            Learn together, build together, get recognized. Share your creations 
            and help others learn.
          </p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          <div className="bg-dark-800/60 rounded-xl p-5 border border-dark-600 text-center">
            <div className="text-3xl font-bold text-green-400">2,847</div>
            <div className="text-sm text-gray-500">Community Members</div>
          </div>
          <div className="bg-dark-800/60 rounded-xl p-5 border border-dark-600 text-center">
            <div className="text-3xl font-bold text-blue-400">156</div>
            <div className="text-sm text-gray-500">Contributions</div>
          </div>
          <div className="bg-dark-800/60 rounded-xl p-5 border border-dark-600 text-center">
            <div className="text-3xl font-bold text-purple-400">89</div>
            <div className="text-sm text-gray-500">Custom Lessons</div>
          </div>
          <div className="bg-dark-800/60 rounded-xl p-5 border border-dark-600 text-center">
            <div className="text-3xl font-bold text-amber-400">12K</div>
            <div className="text-sm text-gray-500">Downloads This Month</div>
          </div>
        </div>

        {/* How to Contribute */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6">How to Contribute</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-dark-800/60 rounded-xl border border-dark-600 p-6">
              <div className="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center mb-4">
                <Upload className="w-6 h-6 text-blue-400" />
              </div>
              <h3 className="font-semibold mb-2">Share Content</h3>
              <p className="text-sm text-gray-400 mb-4">
                Create lessons, simulators, or improvements. Submit via GitHub PR or our community form.
              </p>
              <Link href="#contribute" className="text-sm text-blue-400 hover:text-blue-300">
                Learn how to submit →
              </Link>
            </div>
            
            <div className="bg-dark-800/60 rounded-xl border border-dark-600 p-6">
              <div className="w-12 h-12 rounded-xl bg-green-500/10 flex items-center justify-center mb-4">
                <MessageCircle className="w-6 h-6 text-green-400" />
              </div>
              <h3 className="font-semibold mb-2">Help Others</h3>
              <p className="text-sm text-gray-400 mb-4">
                Answer questions, review contributions, and share your knowledge with new learners.
              </p>
              <a href="#" className="text-sm text-green-400 hover:text-green-300">
                Join discussions →
              </a>
            </div>
            
            <div className="bg-dark-800/60 rounded-xl border border-dark-600 p-6">
              <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center mb-4">
                <Star className="w-6 h-6 text-purple-400" />
              </div>
              <h3 className="font-semibold mb-2">Get Recognized</h3>
              <p className="text-sm text-gray-400 mb-4">
                Earn badges, appear on leaderboards, and build your reputation as an educator.
              </p>
              <Link href="#recognition" className="text-sm text-purple-400 hover:text-purple-300">
                View recognition system →
              </Link>
            </div>
          </div>
        </section>

        {/* Achievements */}
        <section id="recognition" className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Recognition System</h2>
          
          <div className="bg-dark-800/60 rounded-xl border border-dark-600 p-6 mb-6">
            <div className="flex items-center gap-3 mb-4">
              <Trophy className="w-6 h-6 text-amber-400" />
              <h3 className="font-semibold">Your Achievements</h3>
            </div>
            
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
              {achievements.map((achievement) => (
                <div
                  key={achievement.id}
                  className={`relative text-center p-4 rounded-xl border ${
                    achievement.earned
                      ? "bg-dark-700/50 border-green-500/30"
                      : "bg-dark-800/50 border-dark-600 opacity-50"
                  }`}
                >
                  <div className="text-3xl mb-2">{achievement.icon}</div>
                  <div className="text-xs font-medium text-white">{achievement.name}</div>
                  {achievement.earned && (
                    <CheckCircle className="absolute top-2 right-2 w-4 h-4 text-green-400" />
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Top Contributors */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Top Contributors</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {topContributors.map((contributor, index) => (
              <div
                key={contributor.name}
                className={`bg-dark-800/60 rounded-xl border border-dark-600 p-5 flex items-center gap-4 ${
                  index === 0 ? "md:border-amber-500/30" : ""
                }`}
              >
                <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold ${
                  index === 0 ? "bg-gradient-to-br from-amber-500 to-yellow-600 text-white" :
                  index === 1 ? "bg-gradient-to-br from-gray-400 to-gray-500 text-white" :
                  "bg-gradient-to-br from-orange-600 to-orange-700 text-white"
                }`}>
                  {contributor.name.charAt(0)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{contributor.name}</span>
                    {index === 0 && <Crown className="w-4 h-4 text-amber-400" />}
                  </div>
                  <div className="text-sm text-gray-500">{contributor.contributions} contributions</div>
                  <div className="flex gap-1 mt-1">
                    {contributor.badges.map((badge, i) => (
                      <span key={i} className="text-sm">{badge}</span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Recent Activity */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Recent Contributions</h2>
          
          <div className="bg-dark-800/60 rounded-xl border border-dark-600 divide-y divide-dark-600">
            {recentContributions.map((item, index) => (
              <div key={index} className="p-4 flex items-center gap-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center text-white font-medium">
                  {item.avatar}
                </div>
                <div className="flex-1">
                  <p className="text-sm">
                    <span className="font-medium text-white">{item.user}</span>
                    <span className="text-gray-400"> {item.action} </span>
                    <span className="text-green-400">{item.item}</span>
                  </p>
                  <p className="text-xs text-gray-500">{item.time}</p>
                </div>
                <div className="flex items-center gap-1 text-gray-500">
                  <Heart className="w-4 h-4" />
                  <span className="text-sm">{item.likes}</span>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Age Verification Notice */}
        <section id="cloudflare" className="mb-12">
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-6">
            <div className="flex items-start gap-4">
              <Shield className="w-6 h-6 text-amber-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-amber-400 mb-2">Cloud Sync & Full Community Features</h3>
                <p className="text-gray-400 text-sm mb-4">
                  To sync your progress across devices and access full community features, 
                  connect to Cloudflare with age verification. This requires confirming you are 18 or older.
                </p>
                <button className="flex items-center gap-2 px-6 py-2.5 bg-amber-500/10 text-amber-400 rounded-lg text-sm hover:bg-amber-500/20 transition-colors">
                  <Sparkles className="w-4 h-4" />
                  Set Up Cloud Sync
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Links */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6">Community Links</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <a
              href="https://github.com/superinstance/ternaryair"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-4 bg-dark-800/60 rounded-xl border border-dark-600 p-5 hover:border-green-500/30 transition-all"
            >
              <Github className="w-8 h-8 text-gray-400" />
              <div>
                <h3 className="font-semibold">GitHub Repository</h3>
                <p className="text-sm text-gray-500">Star us, fork, contribute</p>
              </div>
              <ExternalLink className="w-4 h-4 text-gray-500 ml-auto" />
            </a>
            
            <Link
              href="/research"
              className="flex items-center gap-4 bg-dark-800/60 rounded-xl border border-dark-600 p-5 hover:border-green-500/30 transition-all"
            >
              <Award className="w-8 h-8 text-gray-400" />
              <div>
                <h3 className="font-semibold">Research & Documentation</h3>
                <p className="text-sm text-gray-500">Technical deep dives</p>
              </div>
              <ArrowRight className="w-4 h-4 text-gray-500 ml-auto" />
            </Link>
          </div>
        </section>

        {/* Navigation */}
        <div className="flex justify-center gap-4 mt-12">
          <Link
            href="/research"
            className="flex items-center gap-2 bg-dark-700 hover:bg-dark-600 text-white px-6 py-3 rounded-xl font-medium transition-colors"
          >
            ← Research Hub
          </Link>
          <Link
            href="/learning"
            className="flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white px-6 py-3 rounded-xl font-medium transition-all"
          >
            Start Learning <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    </div>
  );
}
