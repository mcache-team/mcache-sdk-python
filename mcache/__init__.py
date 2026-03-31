"""
mcache-sdk: Python client for the mcache cache service.

Two implementations are available:
  - HTTP:  mcache.http_client.HttpClient
  - gRPC:  mcache.grpc_client.GrpcClient

Both implement the abstract base class :class:`CacheClient`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class Item:
    """A cache entry returned by the server."""
    prefix: str
    data: Any
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expire_time: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class McacheError(Exception):
    """Base exception for all mcache SDK errors."""


class NotFoundError(McacheError):
    """Raised when the requested prefix does not exist or has expired."""


class AlreadyExistsError(McacheError):
    """Raised when inserting a prefix that already exists."""


# ---------------------------------------------------------------------------
# Abstract client interface
# ---------------------------------------------------------------------------

class CacheClient(ABC):
    """Unified interface for interacting with mcache."""

    @abstractmethod
    def insert(
        self,
        prefix: str,
        data: Any,
        *,
        ttl_seconds: float = 0,
    ) -> None:
        """Create a new cache entry.

        Args:
            prefix: Hierarchical key path (e.g. ``"user/profile/name"``).
            data: Any JSON-serialisable value.
            ttl_seconds: Time-to-live in seconds. ``0`` means no expiry.

        Raises:
            AlreadyExistsError: If the prefix already exists.
        """

    @abstractmethod
    def get(self, prefix: str) -> Item:
        """Retrieve a cache entry by exact prefix.

        Raises:
            NotFoundError: If the prefix does not exist or has expired.
        """

    @abstractmethod
    def update(
        self,
        prefix: str,
        data: Any,
        *,
        ttl_seconds: float = 0,
    ) -> None:
        """Update an existing cache entry.

        Raises:
            NotFoundError: If the prefix does not exist.
        """

    @abstractmethod
    def delete(self, prefix: str) -> None:
        """Delete a cache entry.

        Raises:
            NotFoundError: If the prefix does not exist.
        """

    @abstractmethod
    def list_by_prefix(self, prefix: str) -> list[Item]:
        """Return all direct child items under the given prefix path."""

    def close(self) -> None:
        """Release any underlying connections. Override if needed."""

    def __enter__(self) -> "CacheClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()


__all__ = [
    "Item",
    "McacheError",
    "NotFoundError",
    "AlreadyExistsError",
    "CacheClient",
]
