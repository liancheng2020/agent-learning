from __future__ import annotations

import json
import os
import time

from app.agent import ReviewAgent
from app.cache import CacheBackend, review_cache_key
from app.schemas import ReviewResult
from app.trace import MODEL, TraceStore, estimate_cost, estimate_tokens


class ReviewService:
    def __init__(self, agent: ReviewAgent, traces: TraceStore, cache: CacheBackend) -> None:
        self.agent = agent
        self.traces = traces
        self.cache = cache
        self.ttl_seconds = int(os.getenv("REVIEW_CACHE_TTL_SECONDS", "300"))

    def review(self, diff_text: str) -> ReviewResult:
        prompt_version = f"review-{self.agent.version}-v3"
        trace_id = self.traces.start(prompt_version, {"diff_chars": len(diff_text)})
        started = time.perf_counter()
        key = review_cache_key(diff_text, prompt_version)
        lookup = self.cache.get(key)
        self.traces.emit(
            trace_id,
            "cache.lookup",
            cache={"key": key, "hit": lookup.value is not None, "backend": lookup.backend, "degraded": lookup.degraded},
        )
        if lookup.value is None:
            result = self.agent.review(diff_text, trace_id=trace_id)
            payload = result.model_dump(exclude={"trace_id", "cache_hit"})
            self.cache.set(key, json.dumps(payload, ensure_ascii=False), self.ttl_seconds)
            return result

        cached = json.loads(lookup.value)
        cached["tool_runs"] = [
            {**tool_run, "status": "cached", "latency_ms": 0}
            for tool_run in cached["tool_runs"]
        ]
        result = ReviewResult(trace_id=trace_id, cache_hit=True, **cached)
        input_tokens = estimate_tokens(diff_text)
        output_tokens = estimate_tokens(result.model_dump_json())
        self.traces.emit(
            trace_id,
            "run.completed",
            model=MODEL,
            prompt_version=prompt_version,
            metrics={
                "duration_ms": round((time.perf_counter() - started) * 1000, 3),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "cost_usd": estimate_cost(input_tokens, output_tokens),
            },
            status="completed",
        )
        return result
