import { NextRequest, NextResponse } from 'next/server';
import ZAI from 'z-ai-web-dev-sdk';

// Agent personas for the charades game
const AGENT_PERSONAS = {
  riddler: {
    name: "Riddler",
    role: "actor",
    systemPrompt: `You are Riddler, a clever actor in a charades game. Your job is to describe a secret word WITHOUT saying the word itself. Be cryptic but accurate. You love wordplay and riddles. Keep descriptions under 30 words.`
  },
  oracle: {
    name: "Oracle",
    role: "guesser",
    systemPrompt: `You are Oracle, a wise guesser in a charades game. Your job is to guess the secret word based on descriptions. You are thoughtful and analytical. Always make ONE clear guess per turn.`
  },
  jester: {
    name: "Jester",
    role: "actor",
    systemPrompt: `You are Jester, a playful actor in a charades game. Your job is to describe a secret word WITHOUT saying the word itself. You are funny and use humor in your descriptions. Keep descriptions under 30 words.`
  },
  sage: {
    name: "Sage",
    role: "judge",
    systemPrompt: `You are Sage, a fair judge in a charades game. Your job is to evaluate guesses and determine if they correctly identify the target word. Be generous with close guesses.`
  }
};

// Constraint templates
const CONSTRAINT_PROMPTS: Record<string, string> = {
  rhyme: "IMPORTANT: Your description MUST RHYME! Every line should rhyme.",
  "no-letter": "IMPORTANT: Do NOT use the letter 'E' in your description! This is a lipogram constraint.",
  roast: "IMPORTANT: Roast your opponent playfully! Give them a score out of 100 for their guessing skills.",
  negative: "IMPORTANT: Describe using ONLY NEGATIVE statements (what the thing is NOT).",
  haiku: "IMPORTANT: Your description MUST be a HAIKU (5-7-5 syllables).",
  "emoji-only": "IMPORTANT: Use ONLY EMOJIS to describe! No words allowed."
};

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { 
      action, 
      targetWord, 
      agentId, 
      constraints = [], 
      previousMessages = [],
      guessContent 
    } = body;

    const zai = await ZAI.create();

    switch (action) {
      case 'describe': {
        // Actor describes the target word
        const agent = AGENT_PERSONAS[agentId as keyof typeof AGENT_PERSONAS] || AGENT_PERSONAS.riddler;
        
        let constraintPrompt = '';
        for (const constraintType of constraints) {
          if (CONSTRAINT_PROMPTS[constraintType]) {
            constraintPrompt += '\n' + CONSTRAINT_PROMPTS[constraintType];
          }
        }

        const completion = await zai.chat.completions.create({
          messages: [
            {
              role: 'system',
              content: `${agent.systemPrompt}${constraintPrompt}

The secret word you are describing is: "${targetWord}"

DO NOT say the word "${targetWord}" or any direct variation of it.
Be creative and clever in your description.`
            },
            {
              role: 'user',
              content: 'Give your description now.'
            }
          ],
          temperature: 0.8,
          max_tokens: 100
        });

        const description = completion.choices[0]?.message?.content || 'A mysterious thing...';
        const tokenCount = completion.usage?.total_tokens || Math.ceil(description.length / 4);

        return NextResponse.json({
          success: true,
          agent: agent.name,
          content: description,
          tokens: tokenCount,
          type: 'description'
        });
      }

      case 'guess': {
        // Guesser tries to identify the word
        const agent = AGENT_PERSONAS[agentId as keyof typeof AGENT_PERSONAS] || AGENT_PERSONAS.oracle;
        
        const messagesList = previousMessages.map((m: { agent: string; content: string }) => 
          `${m.agent}: ${m.content}`
        ).join('\n');

        const completion = await zai.chat.completions.create({
          messages: [
            {
              role: 'system',
              content: `${agent.systemPrompt}

Here are the descriptions from the actors:
${messagesList}

Make your best guess. Respond with just your guess, nothing else.`
            },
            {
              role: 'user',
              content: 'What is your guess?'
            }
          ],
          temperature: 0.7,
          max_tokens: 50
        });

        const guess = completion.choices[0]?.message?.content || 'Unknown';
        const tokenCount = completion.usage?.total_tokens || Math.ceil(guess.length / 4);

        return NextResponse.json({
          success: true,
          agent: agent.name,
          content: guess,
          tokens: tokenCount,
          type: 'guess'
        });
      }

      case 'judge': {
        // Judge evaluates the guess
        const agent = AGENT_PERSONAS[agentId as keyof typeof AGENT_PERSONAS] || AGENT_PERSONAS.sage;
        
        const completion = await zai.chat.completions.create({
          messages: [
            {
              role: 'system',
              content: `${agent.systemPrompt}

The target word was: "${targetWord}"
The guess was: "${guessContent}"

Determine if the guess is correct or close enough to be considered correct.
Respond with JSON format: { "correct": true/false, "feedback": "your feedback" }`
            },
            {
              role: 'user',
              content: 'Judge this guess.'
            }
          ],
          temperature: 0.3,
          max_tokens: 100
        });

        const response = completion.choices[0]?.message?.content || '{"correct": false, "feedback": "Unable to judge"}';
        const tokenCount = completion.usage?.total_tokens || 50;

        let judgment;
        try {
          judgment = JSON.parse(response);
        } catch {
          judgment = { 
            correct: response.toLowerCase().includes('correct') && !response.toLowerCase().includes('not correct'),
            feedback: response
          };
        }

        return NextResponse.json({
          success: true,
          agent: agent.name,
          content: judgment.feedback,
          correct: judgment.correct,
          tokens: tokenCount,
          type: 'judgment'
        });
      }

      case 'generate-idiom': {
        // Generate a shorthand idiom from successful gameplay
        const completion = await zai.chat.completions.create({
          messages: [
            {
              role: 'system',
              content: `You are an idiom creator. Given a successful communication between agents, create a shorthand emoji/symbol combination that represents the concept learned.

The idiom should:
1. Be 2-4 emojis or symbols
2. Capture the essence of the concept
3. Be memorable and intuitive
4. Save tokens when reused

Respond in JSON format: { "shorthand": "emoji sequence", "meaning": "what it means" }`
            },
            {
              role: 'user',
              content: `Create an idiom for successfully identifying "${targetWord}" through constrained communication.

Constraints used: ${constraints.join(', ')}
Communication summary: ${previousMessages.slice(-3).map((m: { agent: string; content: string }) => m.content).join(' | ')}`
            }
          ],
          temperature: 0.9,
          max_tokens: 100
        });

        const response = completion.choices[0]?.message?.content || '{"shorthand": "🎯", "meaning": "Success"}';
        const tokenCount = completion.usage?.total_tokens || 30;

        let idiom;
        try {
          idiom = JSON.parse(response);
        } catch {
          idiom = { shorthand: "✨", meaning: response };
        }

        return NextResponse.json({
          success: true,
          idiom,
          tokens: tokenCount,
          type: 'idiom-generated'
        });
      }

      default:
        return NextResponse.json({ error: 'Unknown action' }, { status: 400 });
    }
  } catch (error) {
    console.error('LLN Game API error:', error);
    return NextResponse.json({ 
      error: 'Failed to process game action',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

export async function GET(req: NextRequest) {
  return NextResponse.json({
    name: "LLN Playground API",
    version: "0.1.0",
    actions: ["describe", "guess", "judge", "generate-idiom"],
    agents: Object.keys(AGENT_PERSONAS),
    constraints: Object.keys(CONSTRAINT_PROMPTS)
  });
}
