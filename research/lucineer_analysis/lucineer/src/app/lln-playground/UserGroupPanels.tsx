// ============================================================================
// LLN PLAYGROUND - SPECIALIZED USER GROUP COMPONENTS
// These components provide tailored UX for each user persona
// ============================================================================

import { motion } from "framer-motion";
import {
  Code2,
  Copy,
  Download,
  Play,
  Save,
  Settings,
  Terminal,
  FileJson,
  Database,
  BarChart3,
  Users,
  Clock,
  Zap,
  Target,
  TrendingUp,
  Award,
  BookOpen,
  CheckCircle,
  XCircle,
  AlertCircle,
  Info,
  Lightbulb,
  Sparkles,
  Layers,
  Network,
  Puzzle,
} from "lucide-react";

// ============================================================================
// DEVELOPER TOOLS - For Builders who want to create agents and APIs
// ============================================================================

interface AgentConfig {
  id: string;
  name: string;
  systemPrompt: string;
  model: string;
  temperature: number;
  maxTokens: number;
  constraints: string[];
}

interface DeveloperToolsProps {
  agents: AgentConfig[];
  onAgentUpdate: (agent: AgentConfig) => void;
  onRunTest: (agentId: string) => void;
  tokenUsage: { used: number; budget: number };
  apiLogs: ApiLog[];
}

interface ApiLog {
  id: string;
  timestamp: number;
  endpoint: string;
  method: string;
  request: string;
  response: string;
  tokens: number;
  duration: number;
  status: "success" | "error";
}

export function DeveloperPanel({
  agents,
  onAgentUpdate,
  onRunTest,
  tokenUsage,
  apiLogs,
}: DeveloperToolsProps) {
  return (
    <div className="space-y-6">
      {/* API Console Header */}
      <div className="bg-slate-800/50 rounded-2xl p-6 border border-indigo-500/30">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Terminal className="w-5 h-5 text-indigo-400" />
            Developer Console
          </h3>
          <div className="flex items-center gap-3">
            <div className="text-xs text-slate-400">
              Token Budget: <span className="text-indigo-400">{tokenUsage.used.toLocaleString()}</span> / {tokenUsage.budget.toLocaleString()}
            </div>
            <div className="h-2 w-24 bg-slate-700 rounded-full overflow-hidden">
              <div 
                className="h-full bg-indigo-500 rounded-full"
                style={{ width: `${(tokenUsage.used / tokenUsage.budget) * 100}%` }}
              />
            </div>
          </div>
        </div>

        {/* Quick Code Snippets */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <CodeSnippet 
            title="Create Agent" 
            code={`const agent = await lln.createAgent({
  name: "CustomBot",
  role: "actor",
  model: "gpt-4",
  constraints: ["rhyme", "haiku"]
});`}
          />
          <CodeSnippet 
            title="Play Round" 
            code={`const round = await lln.playRound({
  mode: "charades",
  targetWord: "ELEPHANT",
  agents: [agent1, agent2],
  constraints: activeConstraints
});`}
          />
          <CodeSnippet 
            title="Export Idioms" 
            code={`const idioms = await lln.exportIdioms({
  format: "json",
  includeStats: true,
  filterBy: { usageCount: { $gt: 10 } }
});`}
          />
        </div>

        {/* API Logs */}
        <div className="bg-slate-900 rounded-xl p-4 font-mono text-xs">
          <div className="flex items-center justify-between mb-2">
            <span className="text-slate-500">API Logs</span>
            <button className="text-indigo-400 hover:text-indigo-300">Clear</button>
          </div>
          <div className="space-y-1 max-h-40 overflow-y-auto">
            {apiLogs.map(log => (
              <div key={log.id} className="flex items-center gap-2 text-slate-400">
                <span className="text-slate-600">{new Date(log.timestamp).toLocaleTimeString()}</span>
                <span className={log.method === 'POST' ? 'text-green-400' : 'text-blue-400'}>{log.method}</span>
                <span>{log.endpoint}</span>
                <span className="text-slate-500">{log.duration}ms</span>
                <span className="text-amber-400">{log.tokens}t</span>
                {log.status === 'success' ? (
                  <CheckCircle className="w-3 h-3 text-green-400" />
                ) : (
                  <XCircle className="w-3 h-3 text-red-400" />
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function CodeSnippet({ title, code }: { title: string; code: string }) {
  return (
    <motion.div 
      className="bg-slate-900 rounded-xl p-3 border border-slate-700"
      whileHover={{ borderColor: 'rgba(99, 102, 241, 0.5)' }}
    >
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-indigo-400">{title}</span>
        <button className="text-slate-500 hover:text-white">
          <Copy className="w-3 h-3" />
        </button>
      </div>
      <pre className="text-xs text-slate-400 whitespace-pre-wrap line-clamp-4">{code}</pre>
    </motion.div>
  );
}

// ============================================================================
// RESEARCHER TOOLS - For Academic Study and Data Collection
// ============================================================================

interface ExperimentConfig {
  id: string;
  name: string;
  hypothesis: string;
  variables: {
    independent: string[];
    dependent: string[];
    controls: string[];
  };
  sampleSize: number;
  duration: number;
  status: "draft" | "running" | "completed" | "paused";
}

interface ResearchData {
  roundsCompleted: number;
  idiomsGenerated: number;
  avgTokensPerRound: number;
  successRate: number;
  constraintEfficiency: Record<string, number>;
  agentPerformance: Record<string, { wins: number; avgTokens: number }>;
}

interface ResearcherToolsProps {
  experiments: ExperimentConfig[];
  data: ResearchData;
  onExportData: (format: "json" | "csv" | "bib") => void;
  onStartExperiment: (config: ExperimentConfig) => void;
}

export function ResearcherPanel({
  experiments,
  data,
  onExportData,
  onStartExperiment,
}: ResearcherToolsProps) {
  return (
    <div className="space-y-6">
      {/* Experiment Builder */}
      <div className="bg-slate-800/50 rounded-2xl p-6 border border-purple-500/30">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-purple-400" />
            Research Dashboard
          </h3>
          <div className="flex gap-2">
            <button 
              onClick={() => onExportData("json")}
              className="px-3 py-1.5 rounded-lg bg-purple-500/20 text-purple-400 text-xs flex items-center gap-1"
            >
              <FileJson className="w-3 h-3" />
              JSON
            </button>
            <button 
              onClick={() => onExportData("csv")}
              className="px-3 py-1.5 rounded-lg bg-purple-500/20 text-purple-400 text-xs flex items-center gap-1"
            >
              <Database className="w-3 h-3" />
              CSV
            </button>
          </div>
        </div>

        {/* Statistics Grid */}
        <div className="grid grid-cols-4 gap-4 mb-4">
          <StatCard label="Rounds Completed" value={data.roundsCompleted} color="purple" />
          <StatCard label="Idioms Generated" value={data.idiomsGenerated} color="pink" />
          <StatCard label="Avg Tokens/Round" value={data.avgTokensPerRound} color="amber" />
          <StatCard label="Success Rate" value={`${(data.successRate * 100).toFixed(1)}%`} color="green" />
        </div>

        {/* Constraint Efficiency Chart */}
        <div className="bg-slate-900 rounded-xl p-4">
          <h4 className="text-sm text-purple-400 mb-3">Constraint Efficiency Analysis</h4>
          <div className="space-y-2">
            {Object.entries(data.constraintEfficiency).map(([constraint, efficiency]) => (
              <div key={constraint} className="flex items-center gap-3">
                <span className="text-xs text-slate-400 w-24">{constraint}</span>
                <div className="flex-1 h-2 bg-slate-700 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${efficiency * 100}%` }}
                  />
                </div>
                <span className="text-xs text-slate-400">{(efficiency * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Active Experiments */}
        <div className="mt-4">
          <h4 className="text-sm text-purple-400 mb-3">Active Experiments</h4>
          <div className="space-y-2">
            {experiments.map(exp => (
              <div key={exp.id} className="flex items-center justify-between p-3 bg-slate-900 rounded-xl">
                <div>
                  <div className="text-white text-sm">{exp.name}</div>
                  <div className="text-xs text-slate-500">{exp.hypothesis}</div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    exp.status === 'running' ? 'bg-green-500/20 text-green-400' :
                    exp.status === 'completed' ? 'bg-blue-500/20 text-blue-400' :
                    'bg-slate-500/20 text-slate-400'
                  }`}>
                    {exp.status}
                  </span>
                  <button 
                    onClick={() => onStartExperiment(exp)}
                    className="p-1.5 rounded bg-purple-500/20 text-purple-400"
                  >
                    <Play className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: string | number; color: string }) {
  const colorClasses = {
    purple: "border-purple-500/30 text-purple-400",
    pink: "border-pink-500/30 text-pink-400",
    amber: "border-amber-500/30 text-amber-400",
    green: "border-green-500/30 text-green-400",
  };

  return (
    <div className={`bg-slate-900 rounded-xl p-3 border ${colorClasses[color as keyof typeof colorClasses]}`}>
      <div className="text-xs text-slate-500">{label}</div>
      <div className={`text-xl font-bold ${colorClasses[color as keyof typeof colorClasses].split(' ')[1]}`}>
        {value}
      </div>
    </div>
  );
}

// ============================================================================
// ENTERPRISE TOOLS - For Business Process Optimization
// ============================================================================

interface TeamMetrics {
  members: number;
  activeProjects: number;
  totalTokensUsed: number;
  tokensSaved: number;
  costSavings: number;
}

interface EnterpriseToolsProps {
  teamMetrics: TeamMetrics;
  recentActivity: Activity[];
  roiData: { period: string; savings: number; investment: number }[];
}

interface Activity {
  id: string;
  user: string;
  action: string;
  timestamp: number;
  tokens: number;
}

export function EnterprisePanel({ teamMetrics, recentActivity, roiData }: EnterpriseToolsProps) {
  return (
    <div className="space-y-6">
      {/* Team Dashboard */}
      <div className="bg-slate-800/50 rounded-2xl p-6 border border-cyan-500/30">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Users className="w-5 h-5 text-cyan-400" />
            Enterprise Dashboard
          </h3>
          <button className="px-3 py-1.5 rounded-lg bg-cyan-500/20 text-cyan-400 text-xs">
            Manage Team
          </button>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-5 gap-4 mb-6">
          <MetricCard 
            icon={Users} 
            label="Team Members" 
            value={teamMetrics.members} 
            color="cyan" 
          />
          <MetricCard 
            icon={Layers} 
            label="Active Projects" 
            value={teamMetrics.activeProjects} 
            color="blue" 
          />
          <MetricCard 
            icon={Zap} 
            label="Tokens Used" 
            value={teamMetrics.totalTokensUsed.toLocaleString()} 
            color="amber" 
          />
          <MetricCard 
            icon={TrendingUp} 
            label="Tokens Saved" 
            value={teamMetrics.tokensSaved.toLocaleString()} 
            color="green" 
          />
          <MetricCard 
            icon={Target} 
            label="Cost Savings" 
            value={`$${teamMetrics.costSavings.toLocaleString()}`} 
            color="emerald" 
          />
        </div>

        {/* ROI Chart */}
        <div className="bg-slate-900 rounded-xl p-4 mb-4">
          <h4 className="text-sm text-cyan-400 mb-3">Return on Investment</h4>
          <div className="flex items-end gap-2 h-32">
            {roiData.map((data, idx) => (
              <div key={idx} className="flex-1 flex flex-col items-center gap-1">
                <div className="w-full flex gap-1 items-end justify-center h-24">
                  <div 
                    className="w-1/2 bg-cyan-500 rounded-t"
                    style={{ height: `${(data.savings / Math.max(...roiData.map(d => d.savings))) * 100}%` }}
                  />
                  <div 
                    className="w-1/2 bg-slate-600 rounded-t"
                    style={{ height: `${(data.investment / Math.max(...roiData.map(d => d.investment))) * 100}%` }}
                  />
                </div>
                <span className="text-xs text-slate-500">{data.period}</span>
              </div>
            ))}
          </div>
          <div className="flex justify-center gap-4 mt-2">
            <span className="text-xs text-cyan-400 flex items-center gap-1">
              <div className="w-2 h-2 bg-cyan-500 rounded" /> Savings
            </span>
            <span className="text-xs text-slate-400 flex items-center gap-1">
              <div className="w-2 h-2 bg-slate-600 rounded" /> Investment
            </span>
          </div>
        </div>

        {/* Recent Activity */}
        <div>
          <h4 className="text-sm text-cyan-400 mb-3">Recent Activity</h4>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {recentActivity.map(activity => (
              <div key={activity.id} className="flex items-center justify-between p-2 bg-slate-900 rounded-lg">
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 rounded-full bg-cyan-500/20 flex items-center justify-center text-xs text-cyan-400">
                    {activity.user[0]}
                  </div>
                  <span className="text-sm text-slate-300">{activity.action}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-xs text-amber-400">{activity.tokens}t</span>
                  <span className="text-xs text-slate-500">
                    {new Date(activity.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ icon: Icon, label, value, color }: { 
  icon: React.ElementType; 
  label: string; 
  value: string | number; 
  color: string;
}) {
  const colorClasses = {
    cyan: "text-cyan-400 bg-cyan-500/10",
    blue: "text-blue-400 bg-blue-500/10",
    amber: "text-amber-400 bg-amber-500/10",
    green: "text-green-400 bg-green-500/10",
    emerald: "text-emerald-400 bg-emerald-500/10",
  };

  return (
    <div className="bg-slate-900 rounded-xl p-3">
      <div className={`w-8 h-8 rounded-lg ${colorClasses[color as keyof typeof colorClasses].split(' ')[1]} flex items-center justify-center mb-2`}>
        <Icon className={`w-4 h-4 ${colorClasses[color as keyof typeof colorClasses].split(' ')[0]}`} />
      </div>
      <div className="text-xl font-bold text-white">{value}</div>
      <div className="text-xs text-slate-500">{label}</div>
    </div>
  );
}

// ============================================================================
// EDUCATOR TOOLS - For Teaching AI Concepts
// ============================================================================

interface Lesson {
  id: string;
  title: string;
  description: string;
  difficulty: "beginner" | "intermediate" | "advanced";
  duration: number;
  objectives: string[];
  prerequisites: string[];
}

interface StudentProgress {
  studentId: string;
  name: string;
  completedLessons: number;
  totalLessons: number;
  averageScore: number;
  lastActive: number;
}

interface EducatorToolsProps {
  lessons: Lesson[];
  students: StudentProgress[];
  onCreateLesson: () => void;
  onAssignLesson: (lessonId: string, studentIds: string[]) => void;
}

export function EducatorPanel({ lessons, students, onCreateLesson, onAssignLesson }: EducatorToolsProps) {
  return (
    <div className="space-y-6">
      {/* Lesson Builder */}
      <div className="bg-slate-800/50 rounded-2xl p-6 border border-pink-500/30">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-pink-400" />
            Educator Dashboard
          </h3>
          <button 
            onClick={onCreateLesson}
            className="px-3 py-1.5 rounded-lg bg-pink-500/20 text-pink-400 text-xs flex items-center gap-1"
          >
            <Sparkles className="w-3 h-3" />
            Create Lesson
          </button>
        </div>

        {/* Class Stats */}
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="bg-slate-900 rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-white">{students.length}</div>
            <div className="text-xs text-slate-500">Students</div>
          </div>
          <div className="bg-slate-900 rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-white">{lessons.length}</div>
            <div className="text-xs text-slate-500">Lessons</div>
          </div>
          <div className="bg-slate-900 rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-pink-400">
              {students.length > 0 
                ? (students.reduce((acc, s) => acc + s.averageScore, 0) / students.length).toFixed(0)
                : 0}%
            </div>
            <div className="text-xs text-slate-500">Avg Score</div>
          </div>
        </div>

        {/* Lessons List */}
        <div className="mb-4">
          <h4 className="text-sm text-pink-400 mb-3">Available Lessons</h4>
          <div className="grid grid-cols-2 gap-3">
            {lessons.map(lesson => (
              <motion.div
                key={lesson.id}
                className="p-4 bg-slate-900 rounded-xl border border-slate-700 hover:border-pink-500/50 transition-colors"
                whileHover={{ scale: 1.02 }}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="text-white font-medium">{lesson.title}</div>
                  <span className={`text-xs px-2 py-0.5 rounded ${
                    lesson.difficulty === 'beginner' ? 'bg-green-500/20 text-green-400' :
                    lesson.difficulty === 'intermediate' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {lesson.difficulty}
                  </span>
                </div>
                <p className="text-xs text-slate-500 mb-2">{lesson.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-slate-600">{lesson.duration} min</span>
                  <button 
                    onClick={() => onAssignLesson(lesson.id, students.map(s => s.studentId))}
                    className="text-xs text-pink-400 hover:text-pink-300"
                  >
                    Assign →
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Student Progress */}
        <div>
          <h4 className="text-sm text-pink-400 mb-3">Student Progress</h4>
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {students.map(student => (
              <div key={student.studentId} className="flex items-center gap-3 p-3 bg-slate-900 rounded-xl">
                <div className="w-10 h-10 rounded-full bg-pink-500/20 flex items-center justify-center text-pink-400">
                  {student.name[0]}
                </div>
                <div className="flex-1">
                  <div className="text-white text-sm">{student.name}</div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-pink-500 rounded-full"
                        style={{ width: `${(student.completedLessons / student.totalLessons) * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-slate-500">
                      {student.completedLessons}/{student.totalLessons}
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-pink-400 text-sm">{student.averageScore}%</div>
                  <div className="text-xs text-slate-500">avg score</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// ARTIST TOOLS - For Creative Generative Content
// ============================================================================

interface CreativeProject {
  id: string;
  title: string;
  type: "story" | "poem" | "dialogue" | "scene" | "character";
  status: "draft" | "in-progress" | "completed";
  collaborators: string[];
  wordCount: number;
  lastEdited: number;
}

interface ArtistToolsProps {
  projects: CreativeProject[];
  prompts: string[];
  onCreateProject: (type: CreativeProject["type"]) => void;
  onGeneratePrompt: () => void;
}

export function ArtistPanel({ projects, prompts, onCreateProject, onGeneratePrompt }: ArtistToolsProps) {
  return (
    <div className="space-y-6">
      {/* Creative Studio */}
      <div className="bg-slate-800/50 rounded-2xl p-6 border border-fuchsia-500/30">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-fuchsia-400" />
            Creative Studio
          </h3>
          <button 
            onClick={onGeneratePrompt}
            className="px-3 py-1.5 rounded-lg bg-fuchsia-500/20 text-fuchsia-400 text-xs flex items-center gap-1"
          >
            <Lightbulb className="w-3 h-3" />
            New Prompt
          </button>
        </div>

        {/* Project Types */}
        <div className="grid grid-cols-5 gap-3 mb-6">
          {[
            { type: "story", emoji: "📖", label: "Story" },
            { type: "poem", emoji: "🎭", label: "Poem" },
            { type: "dialogue", emoji: "💬", label: "Dialogue" },
            { type: "scene", emoji: "🎬", label: "Scene" },
            { type: "character", emoji: "👤", label: "Character" },
          ].map(({ type, emoji, label }) => (
            <motion.button
              key={type}
              onClick={() => onCreateProject(type as CreativeProject["type"])}
              className="p-4 bg-slate-900 rounded-xl border border-slate-700 hover:border-fuchsia-500/50 transition-colors text-center"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className="text-2xl mb-1">{emoji}</div>
              <div className="text-xs text-slate-400">{label}</div>
            </motion.button>
          ))}
        </div>

        {/* Inspiration Prompts */}
        <div className="bg-slate-900 rounded-xl p-4 mb-4">
          <h4 className="text-sm text-fuchsia-400 mb-3">Inspiration Prompts</h4>
          <div className="flex flex-wrap gap-2">
            {prompts.map((prompt, idx) => (
              <span 
                key={idx}
                className="px-3 py-1.5 rounded-full bg-fuchsia-500/10 text-fuchsia-300 text-xs"
              >
                {prompt}
              </span>
            ))}
          </div>
        </div>

        {/* Projects */}
        <div>
          <h4 className="text-sm text-fuchsia-400 mb-3">Your Projects</h4>
          <div className="space-y-2">
            {projects.map(project => (
              <motion.div
                key={project.id}
                className="flex items-center gap-4 p-4 bg-slate-900 rounded-xl border border-slate-700 hover:border-fuchsia-500/30"
                whileHover={{ x: 4 }}
              >
                <div className="w-12 h-12 rounded-xl bg-fuchsia-500/20 flex items-center justify-center text-2xl">
                  {project.type === "story" ? "📖" :
                   project.type === "poem" ? "🎭" :
                   project.type === "dialogue" ? "💬" :
                   project.type === "scene" ? "🎬" : "👤"}
                </div>
                <div className="flex-1">
                  <div className="text-white font-medium">{project.title}</div>
                  <div className="text-xs text-slate-500 flex items-center gap-2">
                    <span>{project.wordCount} words</span>
                    <span>•</span>
                    <span>{project.collaborators.length} collaborators</span>
                  </div>
                </div>
                <div className={`px-2 py-0.5 rounded text-xs ${
                  project.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                  project.status === 'in-progress' ? 'bg-fuchsia-500/20 text-fuchsia-400' :
                  'bg-slate-500/20 text-slate-400'
                }`}>
                  {project.status}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// EXPORT ALL COMPONENTS
// ============================================================================

export const UserGroupComponents = {
  DeveloperPanel,
  ResearcherPanel,
  EnterprisePanel,
  EducatorPanel,
  ArtistPanel,
};
