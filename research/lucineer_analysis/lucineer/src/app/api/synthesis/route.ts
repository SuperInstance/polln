import { NextRequest, NextResponse } from "next/server";

// ============================================================================
// SYNTHESIS API
// Generates method combinations and training data
// ============================================================================

interface MethodIngredient {
  id: string;
  name: string;
  strength: "discovery" | "creation" | "analysis" | "social" | "expression";
  energyLevel: "calm" | "moderate" | "high" | "intense";
  synergies: string[];
  conflicts: string[];
  culturalAffinity: Record<string, number>;
}

interface SynthesisResult {
  id: string;
  methods: string[];
  combinationName: string;
  synergyScore: number;
  description: string;
  outputs: string[];
  mlFeatures: Record<string, number>;
  culturalVariants: Record<string, string>;
  ageAdaptations: Record<string, string>;
}

// Method ingredients database
const METHOD_INGREDIENTS: MethodIngredient[] = [
  {
    id: "socratic",
    name: "Socratic Questioning",
    strength: "discovery",
    energyLevel: "moderate",
    synergies: ["debate", "inquiry-based", "case-study"],
    conflicts: ["gamification"],
    culturalAffinity: { JP: 0.7, US: 0.9, GH: 0.8, DE: 0.85, IN: 0.75 }
  },
  {
    id: "project-based",
    name: "Project-Based Learning",
    strength: "creation",
    energyLevel: "high",
    synergies: ["design-thinking", "collaborative", "problem-based"],
    conflicts: [],
    culturalAffinity: { JP: 0.85, US: 0.9, GH: 0.75, DE: 0.95, BR: 0.9 }
  },
  {
    id: "inquiry-based",
    name: "Inquiry-Based Learning",
    strength: "discovery",
    energyLevel: "moderate",
    synergies: ["socratic", "problem-based", "case-study"],
    conflicts: ["apprenticeship"],
    culturalAffinity: { JP: 0.75, US: 0.85, GH: 0.7, DE: 0.9, IN: 0.8 }
  },
  {
    id: "collaborative",
    name: "Collaborative Learning",
    strength: "social",
    energyLevel: "high",
    synergies: ["project-based", "peer-teaching", "design-thinking"],
    conflicts: ["apprenticeship"],
    culturalAffinity: { JP: 0.9, US: 0.75, GH: 0.95, ZA: 0.95, CN: 0.85 }
  },
  {
    id: "storytelling",
    name: "Narrative Learning",
    strength: "expression",
    energyLevel: "calm",
    synergies: ["case-study", "simulation", "montessori"],
    conflicts: ["debate"],
    culturalAffinity: { JP: 0.85, GH: 0.95, SN: 0.95, EG: 0.9, MX: 0.9 }
  },
  {
    id: "debate",
    name: "Debate & Discourse",
    strength: "analysis",
    energyLevel: "intense",
    synergies: ["socratic", "case-study", "peer-teaching"],
    conflicts: ["storytelling", "montessori"],
    culturalAffinity: { US: 0.95, UK: 0.9, DE: 0.85, KR: 0.8, JP: 0.6 }
  },
  {
    id: "gamification",
    name: "Gamified Learning",
    strength: "creation",
    energyLevel: "high",
    synergies: ["simulation", "project-based", "collaborative"],
    conflicts: ["socratic", "storytelling"],
    culturalAffinity: { KR: 0.95, US: 0.9, BR: 0.85, JP: 0.8, DE: 0.7 }
  },
  {
    id: "simulation",
    name: "Immersive Simulation",
    strength: "creation",
    energyLevel: "high",
    synergies: ["gamification", "case-study", "problem-based"],
    conflicts: [],
    culturalAffinity: { US: 0.85, JP: 0.8, DE: 0.85, KR: 0.85, BR: 0.8 }
  },
  {
    id: "design-thinking",
    name: "Design Thinking",
    strength: "creation",
    energyLevel: "high",
    synergies: ["project-based", "collaborative", "problem-based"],
    conflicts: ["apprenticeship"],
    culturalAffinity: { US: 0.9, DE: 0.85, BR: 0.9, JP: 0.8, KR: 0.75 }
  },
  {
    id: "apprenticeship",
    name: "Apprenticeship Model",
    strength: "social",
    energyLevel: "calm",
    synergies: ["storytelling", "montessori", "case-study"],
    conflicts: ["collaborative", "inquiry-based", "design-thinking"],
    culturalAffinity: { JP: 0.95, IN: 0.9, GH: 0.9, EG: 0.85, DE: 0.8 }
  },
  {
    id: "montessori",
    name: "Montessori Approach",
    strength: "discovery",
    energyLevel: "calm",
    synergies: ["storytelling", "inquiry-based", "project-based"],
    conflicts: ["debate", "gamification"],
    culturalAffinity: { US: 0.8, DE: 0.85, IT: 0.9, NL: 0.85, BR: 0.75 }
  },
  {
    id: "peer-teaching",
    name: "Peer Teaching",
    strength: "social",
    energyLevel: "moderate",
    synergies: ["collaborative", "flipped-classroom", "debate"],
    conflicts: ["apprenticeship"],
    culturalAffinity: { US: 0.85, JP: 0.7, DE: 0.8, BR: 0.85, IN: 0.75 }
  },
  {
    id: "case-study",
    name: "Case Study Method",
    strength: "analysis",
    energyLevel: "moderate",
    synergies: ["socratic", "storytelling", "simulation", "debate"],
    conflicts: [],
    culturalAffinity: { US: 0.95, UK: 0.9, DE: 0.85, JP: 0.8, IN: 0.8 }
  },
  {
    id: "problem-based",
    name: "Problem-Based Learning",
    strength: "analysis",
    energyLevel: "high",
    synergies: ["project-based", "inquiry-based", "design-thinking", "collaborative"],
    conflicts: [],
    culturalAffinity: { US: 0.85, DE: 0.9, NL: 0.9, AU: 0.85, SG: 0.85 }
  },
  {
    id: "flipped-classroom",
    name: "Flipped Classroom",
    strength: "discovery",
    energyLevel: "moderate",
    synergies: ["peer-teaching", "socratic", "collaborative"],
    conflicts: [],
    culturalAffinity: { US: 0.85, UK: 0.8, AU: 0.85, DE: 0.75, KR: 0.7 }
  }
];

// Synthesis store
let synthesisHistory: SynthesisResult[] = [];

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { methods, generateTrainingData = true, culturalContext = "US" } = body;

    if (!methods || !Array.isArray(methods) || methods.length < 2) {
      return NextResponse.json(
        { success: false, error: "At least 2 methods required for synthesis" },
        { status: 400 }
      );
    }

    // Find the method ingredients
    const methodIngredients = methods
      .map((m: string) => METHOD_INGREDIENTS.find(mi => mi.id === m))
      .filter(Boolean) as MethodIngredient[];

    if (methodIngredients.length < 2) {
      return NextResponse.json(
        { success: false, error: "Invalid method IDs provided" },
        { status: 400 }
      );
    }

    // Calculate synergy score
    const synergyScore = calculateSynergy(methodIngredients);

    // Generate combination name
    const combinationName = generateCombinationName(methodIngredients);

    // Generate outputs
    const outputs = generateOutputs(methodIngredients);

    // Generate ML features
    const mlFeatures = generateMLFeatures(methodIngredients, synergyScore);

    // Generate cultural variants
    const culturalVariants = generateCulturalVariants(methodIngredients);

    // Generate age adaptations
    const ageAdaptations = generateAgeAdaptations(methodIngredients);

    // Create synthesis result
    const result: SynthesisResult = {
      id: `synthesis_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      methods,
      combinationName,
      synergyScore,
      description: `Combines ${methodIngredients.map(m => m.name).join(" + ")} for enhanced learning outcomes`,
      outputs,
      mlFeatures,
      culturalVariants,
      ageAdaptations
    };

    // Store the result
    synthesisHistory.push(result);

    // Generate training data if requested
    let trainingData = null;
    if (generateTrainingData) {
      trainingData = generateMLTrainingData(result, culturalContext);
    }

    return NextResponse.json({
      success: true,
      result,
      trainingData,
      totalSyntheses: synthesisHistory.length
    });

  } catch (error) {
    console.error("Error in synthesis:", error);
    return NextResponse.json(
      { success: false, error: "Failed to perform synthesis" },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const action = searchParams.get("action");
  const limit = parseInt(searchParams.get("limit") || "50");

  if (action === "discover") {
    // Discover all valid combinations
    const combinations = discoverAllCombinations();
    return NextResponse.json({
      combinations,
      total: combinations.length,
      methods: METHOD_INGREDIENTS
    });
  }

  if (action === "methods") {
    return NextResponse.json({
      methods: METHOD_INGREDIENTS,
      total: METHOD_INGREDIENTS.length
    });
  }

  // Return synthesis history
  return NextResponse.json({
    history: synthesisHistory.slice(-limit),
    total: synthesisHistory.length
  });
}

function calculateSynergy(methods: MethodIngredient[]): number {
  let score = 0.5; // base

  for (let i = 0; i < methods.length; i++) {
    for (let j = i + 1; j < methods.length; j++) {
      const m1 = methods[i];
      const m2 = methods[j];

      // Synergy bonus
      if (m1.synergies.includes(m2.id)) score += 0.15;
      if (m2.synergies.includes(m1.id)) score += 0.1;

      // Conflict penalty
      if (m1.conflicts.includes(m2.id)) score -= 0.2;
      if (m2.conflicts.includes(m1.id)) score -= 0.2;

      // Strength complementarity
      if (m1.strength !== m2.strength) score += 0.08;

      // Energy balance
      const energyLevels = ["calm", "moderate", "high", "intense"];
      const energyDiff = Math.abs(
        energyLevels.indexOf(m1.energyLevel) - energyLevels.indexOf(m2.energyLevel)
      );
      if (energyDiff === 1) score += 0.05;
      if (energyDiff >= 3) score -= 0.05;
    }
  }

  return Math.max(0, Math.min(1, score));
}

function generateCombinationName(methods: MethodIngredient[]): string {
  const prefixes: Record<string, string> = {
    socratic: "Inquiry-Driven",
    "project-based": "Experiential",
    "inquiry-based": "Discovery-Based",
    collaborative: "Collective",
    storytelling: "Narrative-Enhanced",
    debate: "Dialectical",
    gamification: "Game-Infused",
    simulation: "Immersive",
    "design-thinking": "Human-Centered",
    apprenticeship: "Mentored",
    montessori: "Self-Directed",
    "peer-teaching": "Reciprocal",
    "case-study": "Case-Anchored",
    "problem-based": "Challenge-Centered",
    "flipped-classroom": "Flipped"
  };

  // Primary method is the one with most synergies
  const primary = methods.reduce((best, m) => {
    const synergyCount = methods.filter(other => 
      m.synergies.includes(other.id)
    ).length;
    const bestSynergyCount = methods.filter(other => 
      best.synergies.includes(other.id)
    ).length;
    return synergyCount > bestSynergyCount ? m : best;
  });

  return `${prefixes[primary.id] || "Hybrid"} ${methods.find(m => m !== primary)?.name || "Learning"}`;
}

function generateOutputs(methods: MethodIngredient[]): string[] {
  const outputs: string[] = [];
  
  methods.forEach(m => {
    switch (m.strength) {
      case "discovery":
        outputs.push("Enhanced inquiry capabilities");
        break;
      case "creation":
        outputs.push("Tangible project outputs");
        break;
      case "analysis":
        outputs.push("Critical thinking development");
        break;
      case "social":
        outputs.push("Collaborative skill building");
        break;
      case "expression":
        outputs.push("Creative expression channels");
        break;
    }
  });

  return [...new Set(outputs)];
}

function generateMLFeatures(methods: MethodIngredient[], synergy: number): Record<string, number> {
  return {
    method_count: methods.length,
    synergy_score: synergy,
    discovery_strength: methods.filter(m => m.strength === "discovery").length / methods.length,
    creation_strength: methods.filter(m => m.strength === "creation").length / methods.length,
    analysis_strength: methods.filter(m => m.strength === "analysis").length / methods.length,
    social_strength: methods.filter(m => m.strength === "social").length / methods.length,
    expression_strength: methods.filter(m => m.strength === "expression").length / methods.length,
    avg_energy_level: methods.reduce((sum, m) => {
      const levels = { calm: 1, moderate: 2, high: 3, intense: 4 };
      return sum + levels[m.energyLevel];
    }, 0) / methods.length / 4,
    conflict_count: methods.reduce((count, m) => 
      count + methods.filter(other => m.conflicts.includes(other.id)).length, 0
    ) / 2
  };
}

function generateCulturalVariants(methods: MethodIngredient[]): Record<string, string> {
  const variants: Record<string, string> = {};
  const cultures = ["JP", "US", "GH", "DE", "IN", "BR", "CN", "KR"];

  cultures.forEach(culture => {
    const avgAffinity = methods.reduce((sum, m) => 
      sum + (m.culturalAffinity[culture] || 0.7), 0
    ) / methods.length;

    if (avgAffinity >= 0.85) {
      variants[culture] = `Highly compatible - ${methods[0].name} naturally aligns with ${culture} educational traditions`;
    } else if (avgAffinity >= 0.75) {
      variants[culture] = `Good fit - Adapt with minor cultural adjustments`;
    } else {
      variants[culture] = `Requires adaptation - Consider local educational context`;
    }
  });

  return variants;
}

function generateAgeAdaptations(methods: MethodIngredient[]): Record<string, string> {
  return {
    child: "Simplify concepts, add visual elements, reduce complexity",
    teen: "Add challenge elements, social features, identity formation support",
    university: "Deepen rigor, add research components, career preparation",
    adult: "Focus on practical application, ROI, professional integration",
    senior: "Emphasize wisdom sharing, legacy building, intergenerational exchange"
  };
}

function generateMLTrainingData(result: SynthesisResult, culturalContext: string): Record<string, unknown>[] {
  const examples: Record<string, unknown>[] = [];
  
  // Generate multiple training examples from the synthesis
  for (let i = 0; i < 5; i++) {
    examples.push({
      input: {
        methods: result.methods,
        context: `Learning scenario ${i + 1}`,
        cultural_context: culturalContext
      },
      output: {
        synergy_score: result.synergyScore,
        recommended_name: result.combinationName,
        outputs: result.outputs
      },
      metadata: {
        synthesis_id: result.id,
        quality_score: result.mlFeatures.synergy_score,
        timestamp: Date.now()
      }
    });
  }

  return examples;
}

function discoverAllCombinations(): { methods: string[]; synergy: number; name: string }[] {
  const combinations: { methods: string[]; synergy: number; name: string }[] = [];

  // Generate all 2-way combinations
  for (let i = 0; i < METHOD_INGREDIENTS.length; i++) {
    for (let j = i + 1; j < METHOD_INGREDIENTS.length; j++) {
      const m1 = METHOD_INGREDIENTS[i];
      const m2 = METHOD_INGREDIENTS[j];
      const synergy = calculateSynergy([m1, m2]);

      if (synergy >= 0.7) {
        combinations.push({
          methods: [m1.id, m2.id],
          synergy,
          name: generateCombinationName([m1, m2])
        });
      }
    }
  }

  return combinations.sort((a, b) => b.synergy - a.synergy);
}
