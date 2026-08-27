from __future__ import annotations

import json
import math
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import uuid4


MODEL = {
    "provider": "local",
    "name": "rule-rag-reviewer-v1",
    "input_usd_per_million": 0.0,
    "output_usd_per_million": 0.0,
}


def estimate_tokens(value: str) -> int:
    return max(1, math.ceil(len(value) / 4))


def estimate_cost(input_tokens: int, output_tokens: int, model: dict[str, Any] = MODEL) -> float:
    return round(
        input_tokens * float(model["input_usd_per_million"]) / 1_000_000
        + output_tokens * float(model["output_usd_per_million"]) / 1_000_000,
        8,
    )


class TraceStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)
        self._lock = Lock()

    def start(self, prompt_version: str, attributes: dict[str, Any]) -> str:
        trace_id = f"trc_{uuid4().hex}"
        self.emit(
            trace_id,
            "run.started",
            model=MODEL,
            prompt_version=prompt_version,
            attributes=attributes,
        )
        return trace_id

    def emit(self, trace_id: str, event: str, **payload: Any) -> dict[str, Any]:
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "trace_id": trace_id,
            "event": event,
            **payload,
        }
        with self._lock, self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    def get(self, trace_id: str) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        with self._lock, self.path.open(encoding="utf-8") as stream:
            for line in stream:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("trace_id") == trace_id:
                    records.append(record)
        return records
