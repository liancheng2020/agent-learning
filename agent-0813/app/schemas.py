from typing import Any, Literal

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    diff_text: str = Field(min_length=1, max_length=200_000)
    code: str = Field(default="", max_length=200_000)


class Finding(BaseModel):
    severity: Literal["high", "medium", "low"]
    category: str
    file: str
    line: int = Field(ge=1)
    message: str
    suggestion: str


class Source(BaseModel):
    id: str
    title: str
    text: str
    score: int


class PatchPlan(BaseModel):
    file: str
    risk: Literal["low", "requires-review"]
    steps: list[dict[str, str]]


class ToolCallRecord(BaseModel):
    name: str
    status: Literal["completed", "degraded"]
    attempts: int
    latency_ms: int


class ReviewResponse(BaseModel):
    trace_id: str
    summary: str
    findings: list[Finding]
    sources: list[Source]
    patch_plan: PatchPlan
    tool_calls: list[ToolCallRecord]


class ErrorResponse(BaseModel):
    code: str
    message: str
    trace_id: str
    details: dict[str, Any] = {}

