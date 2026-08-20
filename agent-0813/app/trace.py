from datetime import UTC, datetime
from typing import Any


class TraceStore:
    def __init__(self) -> None:
        self._events: dict[str, list[dict[str, Any]]] = {}

    def emit(self, trace_id: str, event: str, **payload: Any) -> dict[str, Any]:
        record = {"ts": datetime.now(UTC).isoformat(), "traceId": trace_id, "event": event, **payload}
        self._events.setdefault(trace_id, []).append(record)
        return record

    def get(self, trace_id: str) -> list[dict[str, Any]]:
        return list(self._events.get(trace_id, []))


trace_store = TraceStore()

