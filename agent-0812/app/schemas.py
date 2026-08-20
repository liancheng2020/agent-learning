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


class PatchStep(BaseModel):
    category: str
    action: str
    reason: str


class PatchPlan(BaseModel):
    file: str
    risk: Literal["low", "requires-review"]
    steps: list[PatchStep]


class ToolCallRecord(BaseModel):
    name: str
    arguments: dict[str, Any]
    ok: bool = True


class ReviewResponse(BaseModel):
    summary: str
    findings: list[Finding]
    sources: list[Source]
    patch_plan: PatchPlan
    tool_calls: list[ToolCallRecord]

