from pathlib import Path

from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError

from app.cache import MemoryCache, RedisCache, ResilientCache, review_cache_key
from app.main import create_app

ROOT = Path(__file__).resolve().parents[1]


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.ttls: dict[str, int] = {}

    def get(self, key: str) -> str | None:
        return self.values.get(key)

    def setex(self, key: str, ttl: int, value: str) -> None:
        self.values[key] = value
        self.ttls[key] = ttl

    def ping(self) -> bool:
        return True


class BrokenRedis(FakeRedis):
    def get(self, key: str) -> str | None:
        raise ConnectionError("redis unavailable")

    def setex(self, key: str, ttl: int, value: str) -> None:
        raise ConnectionError("redis unavailable")

    def ping(self) -> bool:
        raise ConnectionError("redis unavailable")


def test_redis_backend_uses_ttl_and_returns_cached_value() -> None:
    client = FakeRedis()
    cache = RedisCache("redis://unused", client=client)
    cache.set("key", "value", 60)
    assert cache.get("key").value == "value"
    assert client.ttls["key"] == 60


def test_redis_failure_falls_back_to_memory() -> None:
    cache = ResilientCache(RedisCache("redis://unused", client=BrokenRedis()), MemoryCache())
    assert cache.set("key", "value", 30) == "memory"
    lookup = cache.get("key")
    assert lookup.value == "value"
    assert lookup.degraded is True
    assert cache.status()["degraded"] is True


def test_repeated_review_hits_cache_and_keeps_new_trace_id(tmp_path: Path) -> None:
    cache = MemoryCache()
    application = create_app(ROOT, tmp_path / "approvals.db", tmp_path / "trace.jsonl", cache)
    client = TestClient(application)
    payload = {"diff_text": "+localStorage.setItem('accessToken', token);"}

    first = client.post("/review", json=payload).json()
    second = client.post("/review", json=payload).json()

    assert first["cache_hit"] is False
    assert second["cache_hit"] is True
    assert all(run["status"] == "cached" for run in second["tool_runs"])
    assert first["trace_id"] != second["trace_id"]
    events = client.get(f"/traces/{second['trace_id']}").json()["events"]
    lookup = next(event for event in events if event["event"] == "cache.lookup")
    assert lookup["cache"]["hit"] is True
    assert not any(event["event"] == "tool.completed" for event in events)


def test_cache_key_changes_with_prompt_version() -> None:
    diff = "+const value = userInput;"
    assert review_cache_key(diff, "v1") != review_cache_key(diff, "v2")
