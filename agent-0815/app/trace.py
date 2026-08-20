import json
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any


class TraceStore:
    def __init__(self, path: str | Path = "data/trace.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)
        self._lock = Lock()

    def emit(self, trace_id: str, event: str, **payload: Any) -> dict[str, Any]:
        record = {"ts": datetime.now(UTC).isoformat(), "traceId": trace_id, "event": event, **payload}
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
                if record.get("traceId") == trace_id:
                    records.append(record)
        return records


trace_store = TraceStore()

