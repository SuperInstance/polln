"""
TernaryAir REST API Server

This module provides a FastAPI-based REST API server that implements
an OpenAI-compatible interface for TernaryAir inference.

Usage:
    uvicorn server:app --host 0.0.0.0 --port 8000

Then you can use it like OpenAI API:
    curl http://localhost:8000/v1/completions \
        -H "Content-Type: application/json" \
        -d '{"prompt": "Hello, world!", "max_tokens": 50}'
"""

from __future__ import annotations

import time
import uuid
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ternaryair import TernaryAir, Simulator

# Initialize FastAPI app
app = FastAPI(
    title="TernaryAir API",
    description="OpenAI-compatible API for TernaryAir inference",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global device instance
_device: Optional[TernaryAir] = None


def get_device() -> TernaryAir:
    """Get or create device instance."""
    global _device
    if _device is None:
        _device = TernaryAir(backend=Simulator())
    return _device


# ============================================================================
# Request/Response Models
# ============================================================================

class CompletionRequest(BaseModel):
    """Request model for text completion."""
    prompt: str
    max_tokens: int = Field(default=256, ge=1, le=4096)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    top_k: int = Field(default=40, ge=0)
    repeat_penalty: float = Field(default=1.1, ge=1.0, le=2.0)
    stream: bool = Field(default=False)
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": "What is machine learning?",
                    "max_tokens": 100,
                    "temperature": 0.7,
                }
            ]
        }
    }


class CompletionChoice(BaseModel):
    """Completion choice model."""
    text: str
    index: int = 0
    finish_reason: str = "length"


class Usage(BaseModel):
    """Token usage model."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class CompletionResponse(BaseModel):
    """Response model for text completion."""
    id: str
    object: str = "text_completion"
    created: int
    model: str = "ternaryair-350m"
    choices: List[CompletionChoice]
    usage: Usage


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Request model for chat completion."""
    messages: List[ChatMessage]
    max_tokens: int = Field(default=256, ge=1, le=4096)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    model: str = "ternaryair-350m"


class ChatChoice(BaseModel):
    """Chat choice model."""
    index: int = 0
    message: ChatMessage
    finish_reason: str = "stop"


class ChatResponse(BaseModel):
    """Response model for chat completion."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str = "ternaryair-350m"
    choices: List[ChatChoice]
    usage: Usage


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "TernaryAir API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/v1/models")
async def list_models():
    """List available models."""
    return {
        "object": "list",
        "data": [
            {
                "id": "ternaryair-350m",
                "object": "model",
                "created": 1700000000,
                "owned_by": "superinstance",
            }
        ]
    }


@app.post("/v1/completions", response_model=CompletionResponse)
async def create_completion(request: CompletionRequest):
    """Create text completion."""
    device = get_device()
    
    try:
        # Generate completion
        response_text = device.generate(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            repeat_penalty=request.repeat_penalty,
        )
        
        # Estimate token counts (simplified)
        prompt_tokens = len(request.prompt.split())
        completion_tokens = len(response_text.split())
        
        return CompletionResponse(
            id=f"cmpl-{uuid.uuid4().hex[:24]}",
            created=int(time.time()),
            choices=[
                CompletionChoice(
                    text=response_text,
                    finish_reason="length",
                )
            ],
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/chat/completions", response_model=ChatResponse)
async def create_chat_completion(request: ChatRequest):
    """Create chat completion."""
    device = get_device()
    
    try:
        # Convert messages to prompt
        prompt_parts = []
        for msg in request.messages:
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"Assistant: {msg.content}")
        
        prompt = "\n".join(prompt_parts) + "\nAssistant:"
        
        # Generate response
        response_text = device.generate(
            prompt=prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        
        # Estimate token counts
        prompt_tokens = sum(len(m.content.split()) for m in request.messages)
        completion_tokens = len(response_text.split())
        
        return ChatResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:24]}",
            created=int(time.time()),
            choices=[
                ChatChoice(
                    message=ChatMessage(
                        role="assistant",
                        content=response_text,
                    ),
                    finish_reason="stop",
                )
            ],
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/device/info")
async def get_device_info():
    """Get device information."""
    device = get_device()
    info = device.info
    return {
        "model": info.model,
        "firmware": info.firmware_version,
        "serial": info.serial_number,
        "memory_mb": info.memory_mb,
        "max_tokens": info.max_tokens,
    }


@app.get("/v1/device/status")
async def get_device_status():
    """Get device status."""
    device = get_device()
    status = device.status
    return {
        "ready": status.is_ready,
        "temperature_c": status.temperature_c,
        "power_w": status.power_w,
        "tokens_generated": status.tokens_generated,
        "inference_count": status.inference_count,
        "uptime_s": status.uptime_s,
    }


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
