import { NextRequest, NextResponse } from "next/server";

// ============================================================================
// LLN TRAINING DATA COLLECTION API
// Collects user interactions for ML training
// ============================================================================

interface TrainingDataPoint {
  id: string;
  timestamp: number;
  userId: string;
  sessionId: string;
  actionType: string;
  domain: string;
  target: string;
  context: Record<string, unknown>;
  outcome: "success" | "failure" | "neutral";
  value: number;
  culturalContext: string;
  ageGroup: string;
  metadata: Record<string, unknown>;
}

// In-memory store (in production, use a database)
let trainingDataStore: TrainingDataPoint[] = [];
let sessionStats: Record<string, {
  startTime: number;
  actionCount: number;
  successRate: number;
  dominantPattern: string;
}> = {};

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    const dataPoint: TrainingDataPoint = {
      id: `td_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      userId: body.userId || "anonymous",
      sessionId: body.sessionId || `session_${Date.now()}`,
      actionType: body.actionType || "unknown",
      domain: body.domain || "general",
      target: body.target || "",
      context: body.context || {},
      outcome: body.outcome || "neutral",
      value: body.value || 0,
      culturalContext: body.culturalContext || "US",
      ageGroup: body.ageGroup || "adult",
      metadata: body.metadata || {}
    };

    // Store the data point
    trainingDataStore.push(dataPoint);

    // Update session stats
    if (!sessionStats[dataPoint.sessionId]) {
      sessionStats[dataPoint.sessionId] = {
        startTime: Date.now(),
        actionCount: 0,
        successRate: 0,
        dominantPattern: "unknown"
      };
    }
    
    const session = sessionStats[dataPoint.sessionId];
    session.actionCount++;
    if (dataPoint.outcome === "success") {
      session.successRate = (session.successRate * (session.actionCount - 1) + 1) / session.actionCount;
    } else {
      session.successRate = (session.successRate * (session.actionCount - 1)) / session.actionCount;
    }

    // Analyze for patterns (simplified ML)
    const recentActions = trainingDataStore
      .filter(d => d.sessionId === dataPoint.sessionId)
      .slice(-20);
    
    const actionCounts: Record<string, number> = {};
    recentActions.forEach(a => {
      actionCounts[a.actionType] = (actionCounts[a.actionType] || 0) + 1;
    });
    
    const dominantAction = Object.entries(actionCounts)
      .sort((a, b) => b[1] - a[1])[0];
    
    if (dominantAction) {
      session.dominantPattern = dominantAction[0];
    }

    return NextResponse.json({
      success: true,
      id: dataPoint.id,
      sessionStats: sessionStats[dataPoint.sessionId],
      totalDataPoints: trainingDataStore.length
    });

  } catch (error) {
    console.error("Error processing training data:", error);
    return NextResponse.json(
      { success: false, error: "Failed to process training data" },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const sessionId = searchParams.get("sessionId");
  const userId = searchParams.get("userId");
  const limit = parseInt(searchParams.get("limit") || "100");
  const format = searchParams.get("format") || "json";

  let data = [...trainingDataStore];

  // Filter by session
  if (sessionId) {
    data = data.filter(d => d.sessionId === sessionId);
  }

  // Filter by user
  if (userId) {
    data = data.filter(d => d.userId === userId);
  }

  // Limit results
  data = data.slice(-limit);

  // Calculate statistics
  const stats = {
    totalDataPoints: trainingDataStore.length,
    filteredCount: data.length,
    sessions: Object.keys(sessionStats).length,
    avgSessionLength: Object.values(sessionStats).reduce((sum, s) => sum + s.actionCount, 0) / 
      Math.max(1, Object.keys(sessionStats).length),
    successRate: data.filter(d => d.outcome === "success").length / Math.max(1, data.length),
    actionDistribution: data.reduce((acc, d) => {
      acc[d.actionType] = (acc[d.actionType] || 0) + 1;
      return acc;
    }, {} as Record<string, number>),
    domainDistribution: data.reduce((acc, d) => {
      acc[d.domain] = (acc[d.domain] || 0) + 1;
      return acc;
    }, {} as Record<string, number>)
  };

  if (format === "ml") {
    // Format for ML training
    const mlData = data.map(d => ({
      input: JSON.stringify({
        action: d.actionType,
        domain: d.domain,
        target: d.target,
        context: d.context
      }),
      output: JSON.stringify({
        outcome: d.outcome,
        value: d.value
      }),
      metadata: {
        culturalContext: d.culturalContext,
        ageGroup: d.ageGroup,
        timestamp: d.timestamp
      }
    }));

    return NextResponse.json({
      trainingData: mlData,
      stats
    });
  }

  return NextResponse.json({
    data,
    stats,
    sessionStats: sessionId ? sessionStats[sessionId] : sessionStats
  });
}

export async function DELETE(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const sessionId = searchParams.get("sessionId");
  const confirm = searchParams.get("confirm");

  if (confirm !== "true") {
    return NextResponse.json({
      success: false,
      message: "Confirmation required. Add ?confirm=true to delete."
    });
  }

  if (sessionId) {
    trainingDataStore = trainingDataStore.filter(d => d.sessionId !== sessionId);
    delete sessionStats[sessionId];
    return NextResponse.json({
      success: true,
      message: `Deleted session ${sessionId}`
    });
  }

  // Clear all
  trainingDataStore = [];
  sessionStats = {};
  return NextResponse.json({
    success: true,
    message: "All training data cleared"
  });
}
