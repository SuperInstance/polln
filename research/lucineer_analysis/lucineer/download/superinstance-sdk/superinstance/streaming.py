"""
SuperInstance SDK - Streaming Generation

This module provides enhanced streaming utilities for real-time token
generation with callbacks, async support, and advanced features.
"""

from typing import Iterator, Callable, Optional, List, Any, Union
from dataclasses import dataclass
import time


@dataclass
class StreamEvent:
    """Event emitted during streaming generation."""
    token: str
    position: int
    timestamp: float
    latency_ms: float
    cumulative_text: str


class StreamingGenerator:
    """
    Enhanced streaming generator with callbacks and events.

    This class wraps the Model's streaming functionality with additional
    features like event emission, progress tracking, and early stopping.

    Example:
        >>> from superinstance import Device, StreamingGenerator
        >>> device = Device()
        >>> model = device.load_cartridge()
        >>> stream = StreamingGenerator(model)
        >>> for event in stream.generate("Hello"):
        ...     print(f"[{event.position}] {event.token}")
    """

    def __init__(self, model: 'Model'):
        """
        Initialize streaming generator.

        Args:
            model: A loaded Model instance
        """
        self._model = model
        self._stop_requested = False

    def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7,
        on_token: Optional[Callable[[StreamEvent], None]] = None,
        on_complete: Optional[Callable[[str], None]] = None,
        stop_on: Optional[List[str]] = None,
    ) -> Iterator[StreamEvent]:
        """
        Generate streaming response with events.

        Args:
            prompt: Input text prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            on_token: Callback for each token event
            on_complete: Callback when generation completes
            stop_on: List of strings to stop generation on

        Yields:
            StreamEvent for each token generated

        Example:
            >>> def handle_token(event):
            ...     print(event.token, end="", flush=True)
            >>> for event in stream.generate("Hello", on_token=handle_token):
            ...     pass  # Events already handled by callback
        """
        self._stop_requested = False
        cumulative_text = ""
        position = 0
        start_time = time.time()
        last_time = start_time

        try:
            for token, delay_ms in self._model._generator.generate_stream(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature
            ):
                if self._stop_requested:
                    break

                current_time = time.time()
                latency_ms = (current_time - last_time) * 1000
                last_time = current_time
                cumulative_text += token

                event = StreamEvent(
                    token=token,
                    position=position,
                    timestamp=current_time,
                    latency_ms=latency_ms,
                    cumulative_text=cumulative_text
                )

                if on_token:
                    on_token(event)

                yield event
                position += 1

                # Check stop conditions
                if stop_on:
                    for stop_str in stop_on:
                        if stop_str in cumulative_text:
                            self._stop_requested = True
                            break

        except Exception as e:
            raise

        if on_complete:
            on_complete(cumulative_text)

    def stop(self) -> None:
        """Request to stop generation."""
        self._stop_requested = True


class AsyncStreamingGenerator:
    """
    Async-compatible streaming generator.

    Provides async/await interface for streaming generation,
    useful for web servers and async applications.

    Example:
        >>> import asyncio
        >>> from superinstance import Device
        >>> from superinstance.streaming import AsyncStreamingGenerator
        >>>
        >>> async def main():
        ...     device = Device()
        ...     model = device.load_cartridge()
        ...     async_stream = AsyncStreamingGenerator(model)
        ...     async for token in async_stream.generate("Hello"):
        ...         print(token, end="")
        >>>
        >>> asyncio.run(main())
    """

    def __init__(self, model: 'Model'):
        """
        Initialize async streaming generator.

        Args:
            model: A loaded Model instance
        """
        self._model = model
        self._stop_requested = False

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.7,
    ) -> 'AsyncIterator[str]':
        """
        Async streaming generation.

        Args:
            prompt: Input text prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Yields:
            Individual tokens as strings
        """
        import asyncio

        self._stop_requested = False

        for token, delay_ms in self._model._generator.generate_stream(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature
        ):
            if self._stop_requested:
                break

            # Yield control back to event loop
            await asyncio.sleep(0)
            yield token

    def stop(self) -> None:
        """Request to stop generation."""
        self._stop_requested = True


class StreamingCollector:
    """
    Collects streaming output into a complete response.

    Useful when you want both streaming display and the final result.

    Example:
        >>> from superinstance import Device
        >>> from superinstance.streaming import StreamingCollector
        >>>
        >>> device = Device()
        >>> model = device.load_cartridge()
        >>> collector = StreamingCollector()
        >>>
        >>> for token in model.generate_stream("Hello"):
        ...     print(token, end="", flush=True)
        ...     collector.add(token)
        >>>
        >>> result = collector.result()
        >>> print(f"\\nGenerated {result['token_count']} tokens")
    """

    def __init__(self):
        """Initialize collector."""
        self._tokens: List[str] = []
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None

    def start(self) -> None:
        """Start timing collection."""
        self._start_time = time.time()

    def add(self, token: str) -> None:
        """Add a token to the collection."""
        if self._start_time is None:
            self.start()
        self._tokens.append(token)

    def finish(self) -> None:
        """Finish timing collection."""
        self._end_time = time.time()

    def text(self) -> str:
        """Get the collected text."""
        return ''.join(self._tokens)

    def token_count(self) -> int:
        """Get the number of tokens collected."""
        return len(self._tokens)

    def duration_ms(self) -> float:
        """Get the duration in milliseconds."""
        if self._start_time is None:
            return 0
        end = self._end_time or time.time()
        return (end - self._start_time) * 1000

    def tokens_per_second(self) -> float:
        """Get the generation rate in tokens per second."""
        duration_ms = self.duration_ms()
        if duration_ms == 0:
            return 0
        return len(self._tokens) / (duration_ms / 1000)

    def result(self) -> dict:
        """Get complete result as dictionary."""
        self.finish()
        return {
            'text': self.text(),
            'token_count': self.token_count(),
            'duration_ms': self.duration_ms(),
            'tokens_per_second': self.tokens_per_second(),
        }


class StreamingBuffer:
    """
    Buffer for accumulating streaming output with line-based callbacks.

    Useful for processing output line-by-line while still streaming.

    Example:
        >>> from superinstance import Device
        >>> from superinstance.streaming import StreamingBuffer
        >>>
        >>> device = Device()
        >>> model = device.load_cartridge()
        >>> buffer = StreamingBuffer(on_line=lambda line: print(f"LINE: {line}"))
        >>>
        >>> for token in model.generate_stream("Write a poem:"):
        ...     buffer.add(token)
        >>> buffer.flush()  # Flush remaining content
    """

    def __init__(
        self,
        on_line: Optional[Callable[[str], None]] = None,
        line_separator: str = '\n'
    ):
        """
        Initialize buffer.

        Args:
            on_line: Callback for each complete line
            line_separator: Line separator character(s)
        """
        self._buffer = ""
        self._on_line = on_line
        self._separator = line_separator

    def add(self, token: str) -> None:
        """Add a token to the buffer."""
        self._buffer += token
        self._process_lines()

    def _process_lines(self) -> None:
        """Process complete lines in buffer."""
        while self._separator in self._buffer:
            line, self._buffer = self._buffer.split(self._separator, 1)
            if self._on_line and line:
                self._on_line(line)

    def flush(self) -> str:
        """
        Flush remaining content.

        Returns:
            Any remaining content in the buffer
        """
        remaining = self._buffer
        if self._on_line and remaining:
            self._on_line(remaining)
        self._buffer = ""
        return remaining

    def content(self) -> str:
        """Get current buffer content without flushing."""
        return self._buffer
