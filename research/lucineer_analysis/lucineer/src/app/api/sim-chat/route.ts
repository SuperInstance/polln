import { NextRequest, NextResponse } from 'next/server'
import ZAI from 'z-ai-web-dev-sdk'

export async function POST(request: NextRequest) {
  try {
    const { message, activeSimulation, progress, ageMode } = await request.json()
    
    const zai = await ZAI.create()
    
    const systemPrompt = `You are an AI research companion helping users learn about chip design and the TernaryAir project. You explain concepts at an appropriate level for the user's age mode: ${ageMode}.

Current context:
- Active simulation: ${activeSimulation || 'none'}
- Topics completed: ${progress?.topicsCompleted?.join(', ') || 'none'}
- User interests: ${progress?.interests?.join(', ') || 'none'}

TernaryAir project key facts:
- $99 retail price, 100+ tok/s inference speed
- 3-5W USB power, 28nm process
- 256x256 RAU (Recursive Arithmetic Unit) array
- Ternary logic (-1, 0, +1) for 90% gate reduction
- On-chip SRAM, no external DRAM needed
- Mask-locked security feature
- MIT open source license

Respond conversationally and helpfully. If they ask about a specific topic, suggest related simulations they might enjoy. Keep responses concise (2-4 sentences) but informative.`

    const completion = await zai.chat.completions.create({
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: message }
      ],
      temperature: 0.7,
      max_tokens: 300,
    })

    const response = completion.choices[0]?.message?.content || 'Let me help you explore that topic!'
    
    // Detect suggested topic from response
    const suggestedTopic = detectTopic(message)
    
    return NextResponse.json({ 
      response,
      suggestedTopic 
    })
    
  } catch (error: any) {
    console.error('Sim chat error:', error)
    return NextResponse.json({ 
      response: 'I\'m here to help you learn! Try asking about thermal management, timing analysis, yield optimization, or ternary logic.',
      suggestedTopic: null
    }, { status: 200 })
  }
}

function detectTopic(message: string): string | null {
  const topics: Record<string, string[]> = {
    'thermal': ['heat', 'thermal', 'temperature', 'cooling', 'hot'],
    'timing': ['timing', 'delay', 'clock', 'propagation', 'speed'],
    'yield': ['yield', 'manufacturing', 'defect', 'safe zone'],
    'ternary': ['ternary', '-1', '+1', 'balanced', 'trit'],
    'neural': ['neural', 'ai', 'model', 'inference', 'acceleration'],
    'power': ['power', 'watt', 'energy', 'efficiency', 'usb']
  }
  
  const lower = message.toLowerCase()
  for (const [topic, keywords] of Object.entries(topics)) {
    if (keywords.some(kw => lower.includes(kw))) {
      return topic
    }
  }
  return null
}
