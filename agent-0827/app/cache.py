from __future__ import annotations

import hashlib
import os
import time
from dataclasses import dataclass
from typing import Protocol

from redis import Redis
from redis.exceptions import RedisError


@dataclass(frozen=True)
class CacheLookup:
    value: str | None
    backend: str
    degraded: bool = False


class CacheBackend(Protocol):
    name: str

    def get(self, key: str) -> CacheLookup: ...

    def set(self, key: str, value: str, ttl_seconds: int) -> str: ...

    def status(self) -> dict[str, object]: ...


class MemoryCache:
    name = "memory"

    def __init__(self) -> None:
        self._values: dict[str, tuple[float, str]] = {}

    def get(self, key: str) -> CacheLookup:
        item = self._values.get(key)
        if item is None:
            return CacheLookup(None, self.name)
        expires_at, value = item
        if expires_at <= time.monotonic():
            self._values.pop(key, None)
            return CacheLookup(None, self.name)
        return CacheLookup(value, self.name)

    def set(self, key: str, value: str, ttl_seconds: int) -> str:
        self._values[key] = (time.monotonic() + ttl_seconds, value)
        return self.name

    def status(self) -> dict[str, object]:
        return {"backend": self.name, "available": True, "degraded": False}


class RedisCache:
    name = "redis"

    def __init__(self, url: str, client: Redis | None = None) -> None:
        self.client = client or Redis.from_url(
            url,
            decode_responses=True,
            socket_connect_timeout=0.2,
            socket_timeout=0.2,
        )

    def get(self, key: str) -> CacheLookup:
        value = self.client.get(key)
        return CacheLookup(value, self.name)

    def set(self, key: str, value: str, ttl_seconds: int) -> str:
        self.client.setex(key, ttl_seconds, value)
        return self.name

    def status(self) -> dict[str, object]:
        return {"backend": self.name, "available": bool(self.client.ping()), "degraded": False}


class ResilientCache:
    name = "redis-with-memory-fallback"

    def __init__(self, primary: RedisCache, fallback: MemoryCache | None = None) -> None:
        self.primary = primary
        self.fallback = fallback or MemoryCache()

    def get(self, key: str) -> CacheLookup:
        try:
            return self.primary.get(key)
        except (RedisError, OSError):
            fallback = self.fallback.get(key)
            return CacheLookup(fallback.value, fallback.backend, degraded=True)

    def set(self, key: str, value: str, ttl_seconds: int) -> str:
        try:
            return self.primary.set(key, value, ttl_seconds)
        except (RedisError, OSError):
            return self.fallback.set(key, value, ttl_seconds)

    def status(self) -> dict[str, object]:
        try:
            return self.primary.status()
        except (RedisError, OSError) as error:
            return {
                "backend": self.name,
                "available": True,
                "degraded": True,
                "primary_error": type(error).__name__,
            }


def create_cache() -> CacheBackend:
    if os.getenv("CACHE_BACKEND", "redis").lower() == "memory":
        return MemoryCache()
    redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    return ResilientCache(RedisCache(redis_url))


def review_cache_key(diff_text: str, prompt_version: str) -> str:
    digest = hashlib.sha256(f"{prompt_version}\0{diff_text}".encode()).hexdigest()
    return f"frontend-review:{digest}"
