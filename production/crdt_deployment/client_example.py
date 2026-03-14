#!/usr/bin/env python3
"""
CRDT Coordination Service - Client Library

Python client library for interacting with the CRDT Coordination Service.
Provides high-level abstractions for common operations.
"""

import asyncio
import aiohttp
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import time


# =============================================================================
# Client Exceptions
# =============================================================================

class CRDTClientError(Exception):
    """Base exception for CRDT client errors."""
    pass


class OperationFailedError(CRDTClientError):
    """Raised when an operation fails."""
    pass


class ServiceUnavailableError(CRDTClientError):
    """Raised when the service is unavailable."""
    pass


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class ClientConfig:
    """Client configuration."""
    base_url: str = "http://localhost:8001"
    timeout: float = 5.0
    retry_attempts: int = 3
    retry_delay: float = 0.1


@dataclass
class OperationResult:
    """Result of an operation."""
    op_id: str
    success: bool
    value: Optional[Any] = None
    error: Optional[str] = None
    version: int = 0
    latency_ms: float = 0.0
    path_used: str = "unknown"


# =============================================================================
# CRDT Client
# =============================================================================

class CRDTClient:
    """
    Python client for CRDT Coordination Service.

    Example usage:
        ```python
        client = CRDTClient("http://localhost:8001")

        # Write operation
        result = await client.write("my_key", "my_value")

        # Read operation
        result = await client.read("my_key")
        print(result.value)  # "my_value"

        # Increment operation
        result = await client.increment("counter")
        print(result.value)  # 1

        # Close client
        await client.close()
        ```
    """

    def __init__(self, config: Optional[ClientConfig] = None):
        """
        Initialize CRDT client.

        Args:
            config: Client configuration (optional)
        """
        self.config = config or ClientConfig()
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def connect(self):
        """Establish connection to service."""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def close(self):
        """Close connection to service."""
        if self.session:
            await self.session.close()
            self.session = None

    async def health(self) -> Dict[str, Any]:
        """
        Check service health.

        Returns:
            Health status dictionary
        """
        await self._ensure_connected()

        url = f"{self.config.base_url}/health"
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise ServiceUnavailableError(f"Service returned status {response.status}")

    async def write(self,
                    key: str,
                    value: Any,
                    criticality: float = 0.5,
                    op_id: Optional[str] = None) -> OperationResult:
        """
        Write a value to a key.

        Args:
            key: The key to write
            value: The value to write
            criticality: Operation criticality (0.0 - 1.0)
            op_id: Optional operation ID (auto-generated if not provided)

        Returns:
            OperationResult with write outcome
        """
        return await self._execute_operation(
            op_type="write",
            key=key,
            value=str(value),
            criticality=criticality,
            op_id=op_id
        )

    async def read(self,
                   key: str,
                   criticality: float = 0.5,
                   op_id: Optional[str] = None) -> OperationResult:
        """
        Read a value from a key.

        Args:
            key: The key to read
            criticality: Operation criticality (0.0 - 1.0)
            op_id: Optional operation ID (auto-generated if not provided)

        Returns:
            OperationResult with read value
        """
        return await self._execute_operation(
            op_type="read",
            key=key,
            criticality=criticality,
            op_id=op_id
        )

    async def increment(self,
                       key: str,
                       criticality: float = 0.5,
                       op_id: Optional[str] = None) -> OperationResult:
        """
        Increment a counter value.

        Args:
            key: The counter key to increment
            criticality: Operation criticality (0.0 - 1.0)
            op_id: Optional operation ID (auto-generated if not provided)

        Returns:
            OperationResult with incremented value
        """
        return await self._execute_operation(
            op_type="compute",
            key=key,
            criticality=criticality,
            op_id=op_id
        )

    async def batch_write(self,
                         items: Dict[str, Any],
                         criticality: float = 0.5) -> List[OperationResult]:
        """
        Write multiple key-value pairs in parallel.

        Args:
            items: Dictionary of key-value pairs to write
            criticality: Operation criticality for all writes

        Returns:
            List of OperationResult objects
        """
        tasks = [
            self.write(key, value, criticality)
            for key, value in items.items()
        ]

        return await asyncio.gather(*tasks)

    async def get_metrics(self) -> Dict[str, Any]:
        """
        Get service metrics.

        Returns:
            Metrics dictionary
        """
        await self._ensure_connected()

        url = f"{self.config.base_url}/metrics"
        async with self.session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise ServiceUnavailableError(f"Failed to get metrics: {response.status}")

    async def _execute_operation(self,
                                op_type: str,
                                key: str,
                                value: Optional[str] = None,
                                criticality: float = 0.5,
                                op_id: Optional[str] = None) -> OperationResult:
        """
        Execute an operation with retry logic.

        Args:
            op_type: Type of operation (read, write, compute)
            key: Operation key
            value: Optional value for write operations
            criticality: Operation criticality
            op_id: Optional operation ID

        Returns:
            OperationResult
        """
        await self._ensure_connected()

        # Generate op_id if not provided
        if op_id is None:
            op_id = f"client-op-{int(time.time() * 1000000)}"

        # Prepare request payload
        payload = {
            "op_id": op_id,
            "op_type": op_type,
            "key": key,
            "value": value,
            "criticality": criticality,
            "conflict_probability": 0.1  # Default
        }

        # Retry logic
        last_error = None
        for attempt in range(self.config.retry_attempts):
            try:
                url = f"{self.config.base_url}/operation"
                async with self.session.post(url, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return OperationResult(
                            op_id=data["op_id"],
                            success=data["status"] == "success",
                            value=data.get("result", {}).get("value") if data.get("result") else None,
                            error=data.get("error"),
                            version=data.get("result", {}).get("version", 0) if data.get("result") else 0,
                            latency_ms=data.get("latency_ms", 0.0),
                            path_used=data.get("path_used", "unknown")
                        )
                    else:
                        error_text = await response.text()
                        last_error = OperationFailedError(f"Operation failed: {error_text}")

                        # Don't retry client errors (4xx)
                        if 400 <= response.status < 500:
                            raise last_error

            except asyncio.TimeoutError:
                last_error = ServiceUnavailableError("Operation timed out")
            except aiohttp.ClientError as e:
                last_error = ServiceUnavailableError(f"Connection error: {e}")

            # Wait before retry
            if attempt < self.config.retry_attempts - 1:
                await asyncio.sleep(self.config.retry_delay * (2 ** attempt))

        # All retries failed
        raise last_error or OperationFailedError("Operation failed after retries")

    async def _ensure_connected(self):
        """Ensure client session is active."""
        if self.session is None:
            await self.connect()


# =============================================================================
# High-Level Abstractions
# =============================================================================

class CRDTCounter:
    """
    Distributed counter using CRDT.

    Example:
        ```python
        counter = CRDTCounter(client, "my_counter")

        # Increment
        await counter.increment()
        value = await counter.get_value()
        print(value)  # 1

        # Increment by amount
        await counter.increment(5)
        value = await counter.get_value()
        print(value)  # 6
        ```
    """

    def __init__(self, client: CRDTClient, key: str):
        """
        Initialize counter.

        Args:
            client: CRDT client instance
            key: Counter key name
        """
        self.client = client
        self.key = key

    async def increment(self, amount: int = 1) -> int:
        """
        Increment counter.

        Args:
            amount: Amount to increment by

        Returns:
            New counter value
        """
        for _ in range(amount):
            result = await self.client.increment(self.key)
            if not result.success:
                raise OperationFailedError(f"Failed to increment counter: {result.error}")

        # Get final value
        result = await self.client.read(self.key)
        return int(result.value) if result.value else 0

    async def get_value(self) -> int:
        """
        Get current counter value.

        Returns:
            Current counter value
        """
        result = await self.client.read(self.key)
        return int(result.value) if result.value else 0

    async def reset(self) -> int:
        """
        Reset counter to 0.

        Returns:
            New counter value (0)
        """
        await self.client.write(self.key, 0)
        return 0


class CRDTMap:
    """
    Distributed map using CRDT.

    Example:
        ```python
        map = CRDTMap(client, "my_map")

        # Set key-value pairs
        await map.set("field1", "value1")
        await map.set("field2", "value2")

        # Get value
        value = await map.get("field1")
        print(value)  # "value1"

        # Get all fields
        all_data = await map.get_all()
        print(all_data)  # {"field1": "value1", "field2": "value2"}
        ```
    """

    def __init__(self, client: CRDTClient, prefix: str):
        """
        Initialize map.

        Args:
            client: CRDT client instance
            prefix: Key prefix for map entries
        """
        self.client = client
        self.prefix = prefix

    def _make_key(self, field: str) -> str:
        """Create prefixed key for field."""
        return f"{self.prefix}:{field}"

    async def set(self, field: str, value: Any) -> None:
        """
        Set field value.

        Args:
            field: Field name
            value: Field value
        """
        await self.client.write(self._make_key(field), value)

    async def get(self, field: str) -> Optional[Any]:
        """
        Get field value.

        Args:
            field: Field name

        Returns:
            Field value or None if not exists
        """
        result = await self.client.read(self._make_key(field))
        return result.value if result.success else None

    async def delete(self, field: str) -> None:
        """
        Delete field (set to None).

        Args:
            field: Field name
        """
        await self.client.write(self._make_key(field), None)

    async def get_all(self, fields: List[str]) -> Dict[str, Any]:
        """
        Get multiple field values.

        Args:
            fields: List of field names

        Returns:
            Dictionary of field names to values
        """
        tasks = [self.get(field) for field in fields]
        values = await asyncio.gather(*tasks)

        return dict(zip(fields, values))


# =============================================================================
# Usage Examples
# =============================================================================

async def example_basic_operations():
    """Example: Basic operations."""
    async with CRDTClient() as client:
        # Check health
        health = await client.health()
        print(f"Service health: {health}")

        # Write value
        result = await client.write("example_key", "example_value")
        print(f"Write result: {result}")

        # Read value
        result = await client.read("example_key")
        print(f"Read value: {result.value}")

        # Increment counter
        result = await client.increment("counter")
        print(f"Counter value: {result.value}")


async def example_counter():
    """Example: Distributed counter."""
    async with CRDTClient() as client:
        counter = CRDTCounter(client, "page_views")

        # Increment counter
        value = await counter.increment()
        print(f"Page views: {value}")

        # Increment by 10
        value = await counter.increment(10)
        print(f"Page views: {value}")

        # Get current value
        value = await counter.get_value()
        print(f"Total page views: {value}")


async def example_map():
    """Example: Distributed map."""
    async with CRDTClient() as client:
        user_profile = CRDTMap(client, "user:123")

        # Set fields
        await user_profile.set("name", "Alice")
        await user_profile.set("email", "alice@example.com")
        await user_profile.set("age", "30")

        # Get fields
        name = await user_profile.get("name")
        email = await user_profile.get("email")
        print(f"User: {name} <{email}>")

        # Get all fields
        profile = await user_profile.get_all(["name", "email", "age"])
        print(f"Profile: {profile}")


async def example_batch_operations():
    """Example: Batch operations."""
    async with CRDTClient() as client:
        # Batch write
        items = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
        results = await client.batch_write(items)

        print(f"Batch write results: {len(results)} operations")
        for result in results:
            print(f"  {result.op_id}: {result.success}")


async def example_metrics():
    """Example: Get service metrics."""
    async with CRDTClient() as client:
        metrics = await client.get_metrics()

        print("Service Metrics:")
        print(f"  Node ID: {metrics['node_id']}")
        print(f"  Total Operations: {metrics['total_ops']}")
        print(f"  Fast Path Ratio: {metrics['fast_path_ratio']:.2%}")
        print(f"  Average Latency: {metrics['avg_latency_ms']:.2f}ms")
        print(f"  Merge Queue Size: {metrics['merge_queue_size']}")


async def example_error_handling():
    """Example: Error handling."""
    async with CRDTClient() as client:
        try:
            # Try to read non-existent key
            result = await client.read("non_existent_key")
            print(f"Value: {result.value}")  # None

            # Write with high criticality (slow path)
            result = await client.write(
                "critical_config",
                "production_value",
                criticality=0.9
            )
            print(f"Critical write: {result.path_used}")

        except OperationFailedError as e:
            print(f"Operation failed: {e}")
        except ServiceUnavailableError as e:
            print(f"Service unavailable: {e}")


# =============================================================================
# Main Entry Point
# =============================================================================

async def main():
    """Run all examples."""
    print("=" * 60)
    print("CRDT Coordination Service - Client Examples")
    print("=" * 60)

    examples = [
        ("Basic Operations", example_basic_operations),
        ("Distributed Counter", example_counter),
        ("Distributed Map", example_map),
        ("Batch Operations", example_batch_operations),
        ("Service Metrics", example_metrics),
        ("Error Handling", example_error_handling)
    ]

    for name, example_func in examples:
        print(f"\n{name}:")
        print("-" * 60)
        try:
            await example_func()
        except Exception as e:
            print(f"Error: {e}")

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
