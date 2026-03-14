import { NextRequest, NextResponse } from 'next/server';
import ZAI from 'z-ai-web-dev-sdk';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { messages, max_tokens = 4096, temperature = 0.8 } = body;

    const zai = await ZAI.create();

    const completion = await zai.chat.completions.create({
      messages: messages,
      max_tokens: max_tokens,
      temperature: temperature,
    });

    const content = completion.choices[0]?.message?.content || '';

    return NextResponse.json({
      content: content,
      usage: {
        prompt_tokens: completion.usage?.prompt_tokens || 0,
        completion_tokens: completion.usage?.completion_tokens || 0,
        total_tokens: completion.usage?.total_tokens || 0
      }
    });
  } catch (error: any) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    );
  }
}
