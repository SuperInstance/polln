import { NextRequest, NextResponse } from "next/server";

// ============================================================================
// USER ACTIONS API
// Tracks user behavior for ML learning
// ============================================================================

interface UserAction {
  id: string;
  timestamp: number;
  userId: string;
  sessionId: string;
  type: "click" | "hover" | "scroll" | "input" | "select" | "play" | "complete" | "share" | "create" | "learn" | "explore" | "synthesize";
  domain: string;
  target: string;
  context: Record<string, unknown>;
  outcome?: "success" | "failure" | "neutral";
  value?: number;
  duration?: number;
}

interface UserPattern {
  patternId: string;
  name: string;
  confidence: number;
  frequency: number;
  lastSeen: number;
  relatedActions: string[];
}

interface UserPreference {
  key: string;
  value: unknown;
  confidence: number;
  learned: boolean;
  lastUpdated: number;
}

// In-memory stores
let actionsStore: UserAction[] = [];
let patternsStore: Map<string, UserPattern> = new Map();
let preferencesStore: Map<string, UserPreference> = new Map();

// Initialize default patterns
const defaultPatterns: UserPattern[] = [
  { patternId: "explorer", name: "Explorer Pattern", confidence: 0.5, frequency: 0, lastSeen: 0, relatedActions: ["hover", "scroll", "click"] },
  { patternId: "completer", name: "Completer Pattern", confidence: 0.5, frequency: 0, lastSeen: 0, relatedActions: ["play", "complete"] },
  { patternId: "socializer", name: "Socializer Pattern", confidence: 0.5, frequency: 0, lastSeen: 0, relatedActions: ["share", "learn"] },
  { patternId: "creator", name: "Creator Pattern", confidence: 0.5, frequency: 0, lastSeen: 0, relatedActions: ["create", "synthesize"] }
];

defaultPatterns.forEach(p => patternsStore.set(p.patternId, p));

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const action: UserAction = {
      id: `action_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      userId: body.userId || "anonymous",
      sessionId: body.sessionId || `session_${Date.now()}`,
      type: body.type || "click",
      domain: body.domain || "general",
      target: body.target || "",
      context: body.context || {},
      outcome: body.outcome,
      value: body.value,
      duration: body.duration
    };

    // Store the action
    actionsStore.push(action);

    // Analyze and update patterns
    analyzePatterns(action);

    // Update preferences based on action
    updatePreferences(action);

    return NextResponse.json({
      success: true,
      actionId: action.id,
      patterns: Array.from(patternsStore.values()),
      preferences: Array.from(preferencesStore.values()),
      detectedPattern: getDominantPattern()
    });

  } catch (error) {
    console.error("Error processing user action:", error);
    return NextResponse.json(
      { success: false, error: "Failed to process action" },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const userId = searchParams.get("userId");
  const sessionId = searchParams.get("sessionId");
  const limit = parseInt(searchParams.get("limit") || "50");
  const includePatterns = searchParams.get("patterns") === "true";
  const includePreferences = searchParams.get("preferences") === "true";

  let actions = [...actionsStore];

  if (userId) {
    actions = actions.filter(a => a.userId === userId);
  }

  if (sessionId) {
    actions = actions.filter(a => a.sessionId === sessionId);
  }

  actions = actions.slice(-limit);

  const response: Record<string, unknown> = {
    actions,
    totalActions: actionsStore.length
  };

  if (includePatterns) {
    response.patterns = Array.from(patternsStore.values());
    response.dominantPattern = getDominantPattern();
  }

  if (includePreferences) {
    response.preferences = Array.from(preferencesStore.values());
  }

  return NextResponse.json(response);
}

function analyzePatterns(action: UserAction) {
  patternsStore.forEach((pattern, id) => {
    if (pattern.relatedActions.includes(action.type)) {
      pattern.frequency++;
      pattern.lastSeen = action.timestamp;
      pattern.confidence = Math.min(1, pattern.confidence + 0.05);
      patternsStore.set(id, pattern);
    }
  });
}

function updatePreferences(action: UserAction) {
  // Learn from user behavior
  if (action.type === "create" || action.type === "synthesize") {
    updatePreference("creative_mode", true, 0.8);
  }

  if (action.type === "share") {
    updatePreference("social_enabled", true, 0.75);
  }

  if (action.domain === "game" && action.outcome === "success") {
    updatePreference("game_difficulty", "adaptive", 0.7);
  }

  if (action.domain === "learning" && action.duration && action.duration > 60000) {
    updatePreference("deep_learning", true, 0.65);
  }
}

function updatePreference(key: string, value: unknown, confidence: number) {
  const existing = preferencesStore.get(key);
  
  preferencesStore.set(key, {
    key,
    value,
    confidence: existing ? Math.min(1, existing.confidence + 0.1) : confidence,
    learned: true,
    lastUpdated: Date.now()
  });
}

function getDominantPattern(): UserPattern | null {
  let dominant: UserPattern | null = null;
  let maxConfidence = 0;

  patternsStore.forEach(pattern => {
    if (pattern.frequency > 0 && pattern.confidence > maxConfidence) {
      maxConfidence = pattern.confidence;
      dominant = pattern;
    }
  });

  return dominant;
}
