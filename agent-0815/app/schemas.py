from typing import Any, Literal

from pydantic import BaseModel, Field


class ReviewRequest(BaseModel):
    diff_text: str = Field(min_length=1, max_length=200_000)
    code: str = Field(default="", max_length=200_000)


class Finding(BaseModel):
    severity: Literal["high", "medium", "low"]
    category: str = Field(min_length=1)
    file: str = Field(min_length=1)
    line: int = Field(ge=1)
    message: str = Field(min_length=1)
    suggestion: str = Field(min_length=1)


class Source(BaseModel):
    id: str
    title: str
    text: str
    score: int = Field(ge=0)


class PatchStep(BaseModel):
    category: str
    action: str
    reason: str


class PatchPlan(BaseModel):
    file: str
    risk: Literal["low", "requires-review"]
    steps: list[PatchStep]


class ReviewSynthesis(BaseModel):
    summary: str = Field(min_length=1)
    findings: list[Finding]
    sources: list[Source]
    patch_plan: PatchPlan


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict[str, Any]


class ToolCallSummary(BaseModel):
    name: str
    status: Literal["completed", "degraded"]
    attempts: int = Field(ge=1)
    latency_ms: int = Field(ge=0)


class ReviewResult(ReviewSynthesis):
    trace_id: str
    provider: str
    tool_calls: list[ToolCallSummary]


class ErrorResponse(BaseModel):
    code: str
    message: str
    trace_id: str
    details: dict[str, Any] = Field(default_factory=dict)

