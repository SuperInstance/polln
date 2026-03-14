import { NextRequest, NextResponse } from 'next/server'
import ZAI from 'z-ai-web-dev-sdk'

export async function POST(request: NextRequest) {
  try {
    const { command, worldState, selectedBot, puzzle } = await request.json()
    
    const zai = await ZAI.create()
    
    // Build context for AI
    const bot = worldState.find((e: any) => e.id === selectedBot)
    const resources = worldState.filter((e: any) => e.type === 'resource')
    const enemies = worldState.filter((e: any) => e.type === 'enemy')
    const storage = worldState.find((e: any) => e.type === 'storage')
    
    const systemPrompt = `You are an AI agent controller for a game. You control a bot in a 10x10 grid world.
    
Current state:
- Bot position: (${bot?.x}, ${bot?.y})
- Bot energy: ${bot?.energy || 100}
- Bot inventory: ${bot?.inventory?.length || 0} items
- Nearby resources: ${resources.map((r: any) => `(${r.x},${r.y})`).join(', ') || 'none visible'}
- Nearby enemies: ${enemies.map((e: any) => `(${e.x},${e.y})`).join(', ') || 'none visible'}
- Storage location: ${storage ? `(${storage.x},${storage.y})` : 'unknown'}
- Current objective: ${puzzle?.objective || 'unknown'}

Available actions:
- move: {action: "move", params: {targetId: "id"} or {direction: "up/down/left/right"}}
- collect: {action: "collect", params: {}}
- drop: {action: "drop", params: {}}
- attack: {action: "attack", params: {}}
- scan: {action: "scan", params: {}}
- wait: {action: "wait", params: {}}

Respond with JSON containing:
1. "reasoning": brief explanation of your decision
2. "actions": array of action objects to execute

Example response:
{"reasoning": "I see a resource nearby, so I'll collect it", "actions": [{"action": "collect", "params": {}}]}

Keep responses short and focused on the immediate next action.`

    const completion = await zai.chat.completions.create({
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: command }
      ],
      temperature: 0.7,
      max_tokens: 300,
    })

    const responseText = completion.choices[0]?.message?.content || '{"reasoning": "No response", "actions": []}'
    
    // Parse the JSON response
    try {
      const parsed = JSON.parse(responseText)
      return NextResponse.json(parsed)
    } catch {
      // If parsing fails, return a default action
      return NextResponse.json({
        reasoning: "I'm thinking about the best move...",
        actions: [{ action: 'scan', params: {} }]
      })
    }
    
  } catch (error: any) {
    console.error('Agent think error:', error)
    return NextResponse.json({
      reasoning: "I need to analyze the situation more carefully",
      actions: [{ action: 'scan', params: {} }]
    }, { status: 200 }) // Return 200 even on error to keep game running
  }
}
