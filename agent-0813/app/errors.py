from typing import Any


class AgentError(Exception):
    def __init__(self, code: str, message: str, trace_id: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.trace_id = trace_id
        self.details = details or {}


class ToolError(AgentError):
    pass

