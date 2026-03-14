"""
TernaryAir SDK type definitions.
"""

from typing import Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class GenerationResult:
    """Result of a generation request.
    
    Attributes:
        text: Generated text.
        tokens_generated: Number of tokens generated.
        prompt_tokens: Number of tokens in prompt.
        finish_reason: Reason for finishing (length, stop, etc).
        timing_ms: Time taken in milliseconds.
    """
    text: str
    tokens_generated: int
    prompt_tokens: int
    finish_reason: str
    timing_ms: float


@dataclass
class TokenUsage:
    """Token usage statistics.
    
    Attributes:
        prompt_tokens: Tokens in the prompt.
        completion_tokens: Tokens in the completion.
        total_tokens: Total tokens used.
    """
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class ChatMessage:
    """A message in a chat conversation.
    
    Attributes:
        role: Message role (system, user, assistant).
        content: Message content.
    """
    role: str
    content: str


@dataclass  
class ChatCompletionChoice:
    """A choice in a chat completion response.
    
    Attributes:
        index: Choice index.
        message: The message.
        finish_reason: Reason for finishing.
    """
    index: int
    message: ChatMessage
    finish_reason: str


@dataclass
class ChatCompletionResponse:
    """Response from chat completion.
    
    Attributes:
        id: Response ID.
        object: Object type.
        created: Creation timestamp.
        model: Model name.
        choices: List of choices.
        usage: Token usage.
    """
    id: str
    object: str
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: TokenUsage


@dataclass
class CompletionChoice:
    """A choice in a completion response.
    
    Attributes:
        text: Generated text.
        index: Choice index.
        finish_reason: Reason for finishing.
    """
    text: str
    index: int
    finish_reason: str


@dataclass
class CompletionResponse:
    """Response from text completion.
    
    Attributes:
        id: Response ID.
        object: Object type.
        created: Creation timestamp.
        model: Model name.
        choices: List of choices.
        usage: Token usage.
    """
    id: str
    object: str
    created: int
    model: str
    choices: List[CompletionChoice]
    usage: TokenUsage
